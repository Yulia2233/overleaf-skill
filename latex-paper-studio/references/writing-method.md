# 集成写作方法

来源：Master-cai/Research-Paper-Writing-Skills，commit `77e7c2c1ba06f7d71844873147665437a03aac1b`。原仓库说明其方法整理自 Peng Sida 的公开笔记，面向 ML/CV/NLP。本技能保留原文和许可，适配多文件 LaTeX、证据记录与会议约束；原指南的经验建议不是官方投稿政策。

## 工作单元

1. 明确本次解释/证明什么、读者和材料。读 `paper-context.md` 的已定选择。
2. 给 3–7 点的小纲；只改一句时不强行扩展成一节。
3. 一段一个 message，主题句在前，后续给机制、解释、证据或边界。首次出现的术语、缩写、变量可理解。
4. 反向大纲：每段主旨 → 本节主张 → 全文贡献。删除或重排无法映射的段落，不用连接词掩盖推理跳跃。
5. 建立 `Claim | Evidence | Status`，证据指向用户实验文件、图表、核验文献或理论推导。计划中的实验标 pending，不能写成结果。
6. 检查图表、公式、引用、量纲、条件、误差及比较基线与正文一致。
7. 用怀疑的审稿人视角检查，凭证据修订，不以更强修辞掩盖问题。

## 按节加载原指南

| 当前工作 | 原指南 | 落实内容 |
|---|---|---|
| 摘要 | [abstract.md](upstream/research-paper-writing/references/abstract.md) | 问题、核心方案、证据、结论的完整叙事，遵循字数和格式 |
| 引言 | [introduction.md](upstream/research-paper-writing/references/introduction.md) | 任务、重要性、挑战、缺口、洞见和贡献 |
| 相关工作 | [related-work.md](upstream/research-paper-writing/references/related-work.md) | 分类比较、定位贡献、公允陈述适用范围 |
| 方法 | [method.md](upstream/research-paper-writing/references/method.md) | 总览、动机、设计、优势来源、符号与接口 |
| 实验 | [experiments.md](upstream/research-paper-writing/references/experiments.md) | 问题、设置、比较、观察、解释与不足 |
| 结论 | [conclusion.md](upstream/research-paper-writing/references/conclusion.md) | 回答研究问题，不增加未经验证的主张 |
| 衔接 | [flow source](upstream/research-paper-writing/references/does-my-writing-flow-source.md) | 主旨句、术语自足、句间关系、反向大纲 |
| 自审 | [paper-review.md](upstream/research-paper-writing/references/paper-review.md) | 贡献、表达、实验强度、评估完整性、方法合理性 |

示例按需查 [index](upstream/research-paper-writing/references/examples/index.md)，不能把例文结果当作用户结果。

`paper-context.md` 保存标题、方向、语言、故事、贡献、术语、证据、锁定决定和待补信息；`outline.md` 保存章节、篇幅、主张、证据和图表计划；`claims.md` 保存较长证据表。每轮说明改了什么、支持来自哪里、还缺什么。段落标签和自审问题留在笔记里。保护 label/cite/ref、数学语义、实测值及会议类文件；官方规则优先。
