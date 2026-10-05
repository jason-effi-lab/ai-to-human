# 规则来源与依据

本文件说明规则的来源代号与适用边界。来源提供检查问题的线索，不直接证明中文规则有效，也不能据此判断文本由 AI 生成。触发条件、例外、允许动作与示例均由本项目编写；未复制第三方规则原文、代码、图表或样例，也未复用第三方数据。

## 来源与适用边界

| 代号 | 来源与核心价值 | 对规则的支持边界 |
| --- | --- | --- |
| S-PNAS | [Reinhart 等，PNAS 2025：语法和修辞风格的跨文体比较](https://pmc.ncbi.nlm.nih.gov/articles/PMC11874169/)。英文多文体实证；提醒模式须看文体。 | 不能推出某个中文词、连接词或句长应被禁用。文章页面标注 CC BY-NC-ND 4.0；本项目仅引用研究结论与链接。 |
| S-DIVERSITY | [Wang 与 Spitz，EMNLP Findings 2025：改写对语言多样性的影响](https://aclanthology.org/2025.findings-emnlp.1228/)。英文改写实证；提醒编辑器可能压缩内容或推向默认用词。 | 不提供简体中文去模板化阈值；只支持保护作者原有表达的必要性。 |
| S-DRIFT | [Abdulhai 等，arXiv 2026：辅助写作中的语义与立场漂移](https://arxiv.org/html/2603.18161v1)。英文材料与编辑实验；提示最小改动指令仍可能改义。 | 预印本，样本及任务范围有限；只支持语义保真边界的风险判断，不提供本项目失败率。 |
| S-STYLE-METRIC | [Pauli 等，EMNLP Findings 2025：风格转换保真指标的元评测](https://aclanthology.org/2025.findings-emnlp.1175/)。提示表面相似可能遮蔽改义。 | 用于理解保真评价的局限，不作为逐条中文改写指令或现成阈值。 |
| S-DISCOURSE | [Zhang 等，ACL 2024：篇章模式与机器文本检测](https://aclanthology.org/2024.acl-long.298/)。提醒篇章层面也可出现重复模式。 | 检测研究不是中文篇章删改清单；D 系列具体规则由本项目制定。 |
| S-TEXT | [中文技术文档写作规范，ruanyf/document-style-guide](https://github.com/ruanyf/document-style-guide/blob/master/docs/text.md)。中文技术编辑实践，关注清楚指代、易懂措辞和句子主干。 | 不是通用中文实验结论；未复制其规则或例句，也不采纳固定句长、主动语态等绝对要求。 |
| S-GOOGLE | [Google developer documentation style guide：Voice and tone](https://developers.google.com/style/tone)。英文技术文档编辑实践，提供具体、清楚、适合语域的写作思路。 | 英文技术文档场景，不能直接推出中文口播、随笔或评论的规范；未复制其例句。 |
| S-NEWS | [Li 等，NewsBench，ACL 2024](https://aclanthology.org/2024.acl-long.538/)。中文新闻编辑评价参考，区分文体匹配、连贯与指令遵从。 | 新闻文体的标准不能外推至其他文体；只提供文体、连贯与指令遵从的评价维度，不证明本文规则有效。 |
| P-EDIT | 本项目依据[编辑契约](editing-guide.md)提出的编辑判断：只改可指出的阅读问题，保留事实、关系、立场和作者声音。 | 这些判断由本项目制定，不能归为论文或官方规范已经验证的中文去 AI 味规则。 |

## 规则到依据

| 规则 | 依据 |
| --- | --- |
| W-01、W-02、W-03 | S-TEXT、S-GOOGLE、P-EDIT |
| W-04、W-05 | S-TEXT、P-EDIT |
| W-06 | S-GOOGLE、S-PNAS、P-EDIT |
| W-07 | S-TEXT、S-GOOGLE、S-PNAS、P-EDIT |
| D-01、D-02、D-04 | S-DISCOURSE、P-EDIT；D-02 另参照 S-TEXT，D-04 另参照 S-PNAS |
| D-03 | S-GOOGLE、P-EDIT |
| D-05 | S-GOOGLE、P-EDIT |

S-DIVERSITY、S-DRIFT、S-STYLE-METRIC 和 S-NEWS 主要支撑保真边界、文体保护和评价方法，不作为具体词句规则的实证依据。规则受[编辑契约](editing-guide.md)与[文体边界](genre-boundaries.md)共同约束。引用用于来源追溯，日常编辑无需打开外部网页。
