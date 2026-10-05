#!/usr/bin/env python3
"""Compare two UTF-8 texts for explicit protected content and semantic risk.

Usage: python3 check_protected.py --original before.md --candidate after.md
       [--mode markdown|text] [--frozen-list frozen.json]

The JSON output has status pass/violation/review/unparsed and arrays named
violations, review, parse_errors. Exit codes are 0/1/2/3 respectively.
This is a diagnostic aid, not an editor or a semantic-fidelity proof.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path


FENCE_OPEN = re.compile(r"^ {0,3}(`{3,}|~{3,})[^\r\n]*$")
ATX_HEADING = re.compile(r"^ {0,3}#{1,6}(?:[ \t]+|$)[^\r\n]*$")
SETEXT = re.compile(r"^ {0,3}(?:={2,}|-{2,})[ \t]*$")
ORDERED = re.compile(r"^( {0,3})(\d+[.)])([ \t]+)(.*)$")
REFERENCE_DEF = re.compile(r"^ {0,3}\[[^\]\r\n]+\]:[ \t]*(<[^>]+>|\S+)")
REFERENCE_USE = re.compile(r"!?\[[^\]\r\n]*\]\[([^\]\r\n]+)\]")
LINK_START = re.compile(r"!?(?:\[[^\]\r\n]*\])\(")
TABLE_SEP_CELL = re.compile(r"^:?-{3,}:?$")
URL = re.compile(r"https?://[^\s<>]+")
ABS_PATH = re.compile(r"(?<![\w/])(?:/[A-Za-z0-9._-]+){2,}(?![\w/])")
REL_PATH = re.compile(r"(?<![\w/])(?:\.\.?/)?(?:[A-Za-z0-9._-]+/)+[A-Za-z0-9._-]+\.[A-Za-z0-9]{1,8}(?![\w/])")
OPTION = re.compile(r"(?<!\w)--[a-zA-Z][\w-]*")
EXPLICIT_ID = re.compile(r"(?<![\w-])[A-Z][A-Z0-9]{1,}(?:-[A-Z0-9]+)+(?![\w-])")
MARKDOWN_ID = re.compile(r"\{#[A-Za-z][\w-]*\}")
HTML_ANCHOR = re.compile(r"<a\b[^>]*>", re.I)
HTML_ATTRIBUTE = re.compile(r"\b(id|href)\s*=\s*(['\"])(.*?)\2", re.I)
QUOTE = re.compile(r"“[^”\r\n]*”|「[^」\r\n]*」")
NUMBER = re.compile(r"(?<![\w.])\d+(?:[.,]\d+)*(?:%|％)?")
QUALIFIER = re.compile(
    r"没有|不能|不会|不是|并非|至少|至多|可能|预计|必须|仅在|只有|除非|如果|之前|之后|"
    r"已经|正在|尚未|未必|并不|不少于|不超过|仅|只|不|未|无|已|将"
)


@dataclass(frozen=True)
class Token:
    value: str
    line: int


@dataclass
class Parsed:
    tokens: dict[str, list[Token]] = field(default_factory=dict)
    ordered_text: list[Token] = field(default_factory=list)
    quotes: list[Token] = field(default_factory=list)
    semantic_text: str = ""
    errors: list[dict] = field(default_factory=list)

    def add(self, kind: str, value: str, line: int) -> None:
        self.tokens.setdefault(kind, []).append(Token(value, line))

    def error(self, code: str, line: int) -> None:
        self.errors.append({"code": code, "line": line, "message": "输入结构无法可靠解析"})


def bare(line: str) -> str:
    return line.rstrip("\r\n")


def line_at(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def is_escaped(text: str, index: int) -> bool:
    count = 0
    index -= 1
    while index >= 0 and text[index] == "\\":
        count += 1
        index -= 1
    return count % 2 == 1


def table_separator(line: str) -> bool:
    value = bare(line).strip().strip("|")
    cells = [cell.strip() for cell in value.split("|")]
    return bool(cells) and all(TABLE_SEP_CELL.fullmatch(cell) for cell in cells)


def matching_link_close(text: str, opening: int) -> int | None:
    depth = 1
    in_angle = False
    for i in range(opening + 1, len(text)):
        char = text[i]
        if is_escaped(text, i):
            continue
        if char == "<":
            in_angle = True
        elif char == ">":
            in_angle = False
        elif not in_angle and char == "(":
            depth += 1
        elif not in_angle and char == ")":
            depth -= 1
            if depth == 0:
                return i
    return None


def link_destination(body: str) -> str | None:
    value = body.strip()
    if value.startswith("<"):
        close = value.find(">")
        return value[1:close] if close >= 0 else None
    return value.split(maxsplit=1)[0] if value else ""


def plain_url(value: str) -> str:
    value = value.rstrip(".,;!?。，；！？\"'")
    while value.endswith(")") and value.count(")") > value.count("("):
        value = value[:-1]
    return value


def scan_inline(line: str, number: int, parsed: Parsed, markdown: bool) -> str:
    """Collect supported inline literals; return text with code/links masked."""
    mask = list(bare(line))
    raw = bare(line)
    i = 0
    while markdown and i < len(raw):
        if raw[i] != "`" or is_escaped(raw, i):
            i += 1
            continue
        end_run = i
        while end_run < len(raw) and raw[end_run] == "`":
            end_run += 1
        run = raw[i:end_run]
        close = None
        cursor = end_run
        while cursor < len(raw):
            if raw[cursor] == "`" and not is_escaped(raw, cursor):
                stop = cursor
                while stop < len(raw) and raw[stop] == "`":
                    stop += 1
                if raw[cursor:stop] == run:
                    close = stop
                    break
                cursor = stop
            else:
                cursor += 1
        if close is None:
            parsed.error("unclosed_inline_code", number)
            return ""
        parsed.add("inline_code", raw[i:close], number)
        mask[i:close] = " " * (close - i)
        i = close

    masked = "".join(mask)
    reference = REFERENCE_DEF.match(masked) if markdown else None
    if reference:
        label = masked[masked.find("[") + 1:masked.find("]")]
        parsed.add("link_reference_label", label, number)
        target = reference.group(1).strip("<>")
        parsed.add("link_target", target, number)
        mask[reference.start(1):reference.end(1)] = " " * len(reference.group(1))
        masked = "".join(mask)

    cursor = 0
    while markdown and (match := LINK_START.search(masked, cursor)):
        opening = match.end() - 1
        close = matching_link_close(masked, opening)
        if close is None:
            parsed.error("unclosed_markdown_link", number)
            return ""
        target = link_destination(masked[opening + 1:close])
        if target is None:
            parsed.error("invalid_markdown_link_target", number)
            return ""
        parsed.add("link_target", target, number)
        mask[match.start():close + 1] = " " * (close + 1 - match.start())
        masked = "".join(mask)
        cursor = close + 1
    if markdown and "](" in masked:
        parsed.error("unsupported_markdown_link", number)
        return ""
    if markdown:
        for use in REFERENCE_USE.finditer(masked):
            parsed.add("link_reference_use", use.group(1), number)

    for anchor in HTML_ANCHOR.finditer(masked):
        for attr in HTML_ATTRIBUTE.finditer(anchor.group()):
            parsed.add("html_anchor", attr.group(1).lower() + "=" + attr.group(3), number)
        if not HTML_ATTRIBUTE.search(anchor.group()):
            parsed.error("unsupported_html_anchor", number)
    for value in MARKDOWN_ID.finditer(masked):
        parsed.add("markdown_anchor", value.group(), number)
    if re.search(r"<(?:table|pre|code)\b", masked, re.I):
        parsed.error("unsupported_html_structure", number)
    for name, expression in (("url", URL), ("path", ABS_PATH), ("relative_path", REL_PATH),
                             ("option", OPTION), ("explicit_id", EXPLICIT_ID)):
        for value in expression.finditer(masked):
            literal = plain_url(value.group()) if name == "url" else value.group()
            if literal:
                parsed.add(name, literal, number)
    parsed.quotes.extend(Token(m.group(), number) for m in QUOTE.finditer(masked))
    return masked


def parse(text: str, mode: str) -> Parsed:
    parsed = Parsed()
    lines = text.splitlines(keepends=True)
    i = 0
    semantic: list[str] = []
    if mode == "markdown" and lines and bare(lines[0]) == "---":
        close = next((j for j in range(1, len(lines)) if bare(lines[j]) == "---"), None)
        if close is None:
            parsed.error("unclosed_frontmatter", 1)
            return parsed
        parsed.add("frontmatter", "".join(lines[:close + 1]), 1)
        semantic.extend("" for _ in range(close + 1))
        i = close + 1
    while i < len(lines):
        line = bare(lines[i])
        number = i + 1
        if mode == "markdown":
            fence = FENCE_OPEN.match(line)
            if fence:
                marker = fence.group(1)
                closing = re.compile(r"^ {0,3}" + re.escape(marker[0]) + "{" + str(len(marker)) + r",}[ \t]*$")
                close = next((j for j in range(i + 1, len(lines)) if closing.match(bare(lines[j]))), None)
                if close is None:
                    parsed.error("unclosed_fenced_code", number)
                    return parsed
                parsed.add("fenced_code", "".join(lines[i:close + 1]), number)
                semantic.extend("" for _ in range(close + 1 - i))
                i = close + 1
                continue
            if re.match(r"^(?: {4}|\t)\S", line):
                close = i + 1
                while close < len(lines) and (re.match(r"^(?: {4}|\t)", bare(lines[close]))
                                              or not bare(lines[close]).strip()):
                    close += 1
                parsed.add("indented_code", "".join(lines[i:close]), number)
                semantic.extend("" for _ in range(close - i))
                i = close
                continue
            if i + 1 < len(lines) and "|" in line and table_separator(lines[i + 1]):
                close = i + 2
                while close < len(lines) and "|" in bare(lines[close]) and bare(lines[close]).strip():
                    close += 1
                parsed.add("table", "".join(lines[i:close]), number)
                semantic.extend("" for _ in range(close - i))
                i = close
                continue
            if line.lstrip().startswith("|") and line.count("|") >= 2:
                parsed.error("unsupported_table_like_line", number)
                semantic.append("")
                i += 1
                continue
            if i + 1 < len(lines) and line.strip() and SETEXT.match(bare(lines[i + 1])):
                parsed.add("heading", "".join(lines[i:i + 2]), number)
                semantic.extend(("", ""))
                i += 2
                continue
            if ATX_HEADING.match(line):
                parsed.add("heading", line, number)
            if re.match(r"^ {0,3}>", line):
                parsed.add("blockquote", lines[i], number)
                semantic.append("")
                i += 1
                continue
            ordered = ORDERED.match(line)
            if ordered:
                parsed.add("ordered_marker", ordered.group(1) + ordered.group(2), number)
                parsed.ordered_text.append(Token(ordered.group(4), number))
        semantic.append(scan_inline(line, number, parsed, mode == "markdown"))
        i += 1
    parsed.semantic_text = "\n".join(semantic)
    return parsed


def first_difference(before: list[Token], after: list[Token]) -> tuple[int | None, int | None]:
    for original, candidate in zip(before, after):
        if original.value != candidate.value:
            return original.line, candidate.line
    return (before[len(after)].line if len(before) > len(after) else None,
            after[len(before)].line if len(after) > len(before) else None)


def compare_tokens(before: list[Token], after: list[Token], kind: str, message: str) -> dict | None:
    if [item.value for item in before] == [item.value for item in after]:
        return None
    original_line, candidate_line = first_difference(before, after)
    return {"code": kind + "_changed", "original_line": original_line,
            "candidate_line": candidate_line, "message": message}


def frozen_tokens(text: str, snippets: list[str]) -> list[Token]:
    hits = []
    for snippet in snippets:
        start = 0
        while (position := text.find(snippet, start)) >= 0:
            hits.append((position, Token(snippet, line_at(text, position))))
            start = position + len(snippet)
    return [item for _, item in sorted(hits, key=lambda pair: pair[0])]


def check(original: str, candidate: str, mode: str, frozen: list[str] | None = None) -> dict:
    frozen = frozen or []
    before, after = parse(original, mode), parse(candidate, mode)
    parse_errors = [{"side": side, **error} for side, parsed in (("original", before), ("candidate", after))
                    for error in parsed.errors]
    violations: list[dict] = []
    review: list[dict] = []
    for kind in sorted(before.tokens.keys() | after.tokens.keys()):
        issue = compare_tokens(before.tokens.get(kind, []), after.tokens.get(kind, []), kind,
                               "明确受保护的字面内容或 Markdown 结构发生变化")
        if issue:
            violations.append(issue)
    if frozen:
        for snippet in frozen:
            if snippet not in original:
                parse_errors.append({"side": "configuration", "code": "frozen_not_in_original",
                                     "line": None, "message": "指定冻结片段未出现在原文"})
        issue = compare_tokens(frozen_tokens(original, frozen), frozen_tokens(candidate, frozen),
                               "frozen", "用户指定的冻结片段发生变化")
        if issue:
            violations.append(issue)
    if mode == "markdown":
        issue = compare_tokens(before.ordered_text, after.ordered_text, "ordered_item_text",
                               "有序列表正文变化；可能涉及操作步骤，请对照原文复核")
        if issue:
            review.append(issue)
    issue = compare_tokens(before.quotes, after.quotes, "quoted_text",
                           "引号内文字变化；若为直接引文则必须保留原样")
    if issue:
        review.append(issue)
    for kind, expression in (("number", NUMBER), ("qualifier", QUALIFIER)):
        left = [Token(m.group(), line_at(before.semantic_text, m.start())) for m in expression.finditer(before.semantic_text)]
        right = [Token(m.group(), line_at(after.semantic_text, m.start())) for m in expression.finditer(after.semantic_text)]
        issue = compare_tokens(left, right, kind, "数字或限定词变化；需人工检查对象绑定和原意")
        if issue:
            review.append(issue)
    status = "unparsed" if parse_errors else "violation" if violations else "review" if review else "pass"
    return {"status": status, "semantic_fidelity_verified": False,
            "violations": violations, "review": review, "parse_errors": parse_errors}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--original", type=Path, required=True, help="UTF-8 原文文件")
    parser.add_argument("--candidate", type=Path, required=True, help="UTF-8 候选稿文件")
    parser.add_argument("--mode", choices=("markdown", "text"), default="markdown",
                        help="默认按受支持的 Markdown 子集解析；纯文本使用 text")
    parser.add_argument("--frozen-list", type=Path, help="JSON 字符串数组：用户明确指定的冻结片段")
    args = parser.parse_args()
    try:
        original = args.original.read_bytes().decode("utf-8")
        candidate = args.candidate.read_bytes().decode("utf-8")
        frozen = json.loads(args.frozen_list.read_text(encoding="utf-8")) if args.frozen_list else []
        if not isinstance(frozen, list) or any(not isinstance(item, str) or not item for item in frozen):
            raise ValueError("frozen-list 必须是非空字符串组成的 JSON 数组")
        result = check(original, candidate, args.mode, frozen)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        result = {"status": "unparsed", "semantic_fidelity_verified": False,
                  "violations": [], "review": [],
                  "parse_errors": [{"side": "input", "code": "input_error", "line": None,
                                    "message": str(exc)}]}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return {"pass": 0, "violation": 1, "review": 2, "unparsed": 3}[result["status"]]


if __name__ == "__main__":
    raise SystemExit(main())
