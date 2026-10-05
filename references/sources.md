# 规则依据与验证状态

本文件说明运行规则卡的来源代号。来源用来解释**为什么值得检查某类问题**，不证明对应中文规则有效，更不证明文本由 AI 生成。所有具体触发条件、例外、允许动作与示例由本项目编写，没有复制论文、指南或开源项目的规则原文、代码、图表或样例。项目未复用第三方代码和数据；未来若要复用，需单独核验许可与署名要求。

## 代号与证据等级

| 代号 | 来源与核心价值 | 对规则的支持边界 |
| --- | --- | --- |
| S-PNAS | [Reinhart 等，PNAS 2025：语法和修辞风格的跨文体比较](https://pmc.ncbi.nlm.nih.gov/articles/PMC11874169/)。英文多文体实证；提醒模式须看文体。 | 不能推出某个中文词、连接词或句长应被禁用。文章页面标注 CC BY-NC-ND 4.0；本项目仅引用研究结论与链接。 |
| S-DIVERSITY | [Wang 与 Spitz，EMNLP Findings 2025：改写对语言多样性的影响](https://aclanthology.org/2025.findings-emnlp.1228/)。英文改写实证；提醒编辑器可能压缩内容或推向默认用词。 | 不提供简体中文去模板化阈值；只支持保护作者原有表达的评测动机。 |
| S-DRIFT | [Abdulhai 等，arXiv 2026：辅助写作中的语义与立场漂移](https://arxiv.org/html/2603.18161v1)。英文材料与编辑实验；提示最小改动指令仍可能改义。 | 预印本，样本及任务范围有限；只支持语义保真边界的风险判断，不提供本项目失败率。 |
| S-STYLE-METRIC | [Pauli 等，EMNLP Findings 2025：风格转换保真指标的元评测](https://aclanthology.org/2025.findings-emnlp.1175/)。提示表面相似可能遮蔽改义。 | 用于后续评测设计，不作为逐条中文改写指令或现成阈值。 |
| S-DISCOURSE | [Zhang 等，ACL 2024：篇章模式与机器文本检测](https://aclanthology.org/2024.acl-long.298/)。提醒篇章层面也可出现重复模式。 | 检测研究不是中文篇章删改清单；D 系列具体判断仍是本项目编辑假设。 |
| S-TEXT | [中文技术文档写作规范，ruanyf/document-style-guide](https://github.com/ruanyf/document-style-guide/blob/master/docs/text.md)。中文技术编辑实践，关注清楚指代、易懂措辞和句子主干。 | 不是通用中文实验结论；未复制其规则或例句，也不采纳固定句长、主动语态等绝对要求。 |
| S-GOOGLE | [Google developer documentation style guide：Voice and tone](https://developers.google.com/style/tone)。英文技术文档编辑实践，提供具体、清楚、适合语域的写作思路。 | 英文技术文档场景，不能直接推出中文口播、随笔或评论的规范；未复制其例句。 |
| S-NEWS | [Li 等，NewsBench，ACL 2024](https://aclanthology.org/2024.acl-long.538/)。中文新闻编辑评价参考，区分文体匹配、连贯与指令遵从。 | 新闻文体的标准不能外推至其他文体；用于后续评测维度，而非本文规则的通过证明。 |
| P-EDIT | 本项目依据[编辑契约](editing-guide.md)提出的编辑判断：只改可指出的阅读问题，保留事实、关系、立场和作者声音。 | 已完成项目开发回归和单人人工盲评，有效样本未证明稳定表达优势；不能表述为论文或官方规范已经验证的中文去 AI 味规则。 |

## 规则到依据

| 规则 | 依据 | 当前状态 |
| --- | --- | --- |
| W-01、W-02、W-03 | S-TEXT、S-GOOGLE、P-EDIT | 条件与例子已写定；效果待评测 |
| W-04、W-05 | S-TEXT、P-EDIT | 条件与例子已写定；效果待评测 |
| W-06 | S-GOOGLE、S-PNAS、P-EDIT | 条件与例子已写定；效果待评测 |
| W-07 | S-TEXT、S-GOOGLE、S-PNAS、P-EDIT | 条件与例子已写定；效果待评测 |
| D-01、D-02、D-04 | S-DISCOURSE、P-EDIT；D-02 另参照 S-TEXT，D-04 另参照 S-PNAS | 条件与例子已写定；效果待评测 |
| D-03 | S-GOOGLE、P-EDIT | 条件与例子已写定；效果待评测 |
| D-05 | S-GOOGLE、P-EDIT | 条件与例子已写定；效果待评测 |

S-DIVERSITY、S-DRIFT、S-STYLE-METRIC 和 S-NEWS 主要支撑全局保真边界、文体保护或后续评测方法，不被强行挂靠为某个词句的实证依据。规则受[编辑契约](editing-guide.md)与[文体边界](genre-boundaries.md)共同约束。运行时无需遍历外部网页；引用只用于维护可追溯性。来源页面可变，发布前应再核对链接及复用材料的许可。
