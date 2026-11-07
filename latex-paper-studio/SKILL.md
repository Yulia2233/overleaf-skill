---
name: latex-paper-studio
description: 用会议或期刊官方模板创建和撰写 LaTeX 论文，在网页中使用文件树、源码编辑、真实 PDF 编译预览、源码/PDF 选文批注与 Agent 修改，并导出可上传 Overleaf 的 ZIP。适用于网页写论文、按投稿规范起草或修改、多文件 LaTeX 协作；内置 Research-Paper-Writing-Skills 写作方法。
---

# LaTeX 论文工作台

交付可持续编辑的论文工程、真实编译 PDF 和可导入 Overleaf 的源码包。中文沟通；正文语言遵循投稿要求及用户选择。技能目录记为 `SKILL_DIR`，论文项目目录记为 `PROJECT`；不要把论文写进技能安装目录。

## 首次调用与恢复

1. 先读现有 `paper-context.md`、`venue.json`、`venue-rules.md` 和 `outline.md`，复用已经确认的信息。首次缺少目标时首先问：**准备投哪个会议/期刊、哪一年、哪个 track/文章类型，是审稿版还是终稿版？有没有指定模板文件或官方链接？** 可合并询问暂定标题、方向、已有大纲和实验材料，不要求用户一次填完所有字段。
2. 用户提供模板就直接采用并核对版本；没有提供就主动检索该届官网，下载其链接的完整模板到工作区，保留类、样式、图片与许可。没选 venue 时可以先讨论大纲，不能冒认通用模板为正式投稿模板。
3. 按 [会议规范流程](references/venue-compliance.md) 获取官方要求，区分年份、track、审稿与终稿。尚未公布的规则写“未核实”，不用上一届冒充本届。模板与最新官方政策有冲突时记录并解决后再称合规。
4. 根据用户内容提出标题与分节大纲，标明每节主张、证据、图表、篇幅预算及待补信息；已有大纲就沿用。写入 `paper-context.md` 和 `outline.md`。缺少结果时可写结构与方法，不虚构数字。

## 启动网页

读 [运行与批注协议](references/workbench.md)。依赖 Python 3.10+、latexmk 和官方模板所需的 pdfLaTeX/XeLaTeX/LuaLaTeX。前端已打包，无需 npm 或 CDN。

```bash
python3 "$SKILL_DIR/scripts/studio.py" init --project "$PROJECT" --template /absolute/template.zip --main main.tex --engine pdflatex
python3 "$SKILL_DIR/scripts/studio.py" serve --project "$PROJECT" --port 0
```

已有项目用 `configure --project ... --main ... --engine ...`，不覆盖正文。新文档在具备 `create_latex_project` 时先用它创建专属目录，再放入官方模板并 configure；现有项目直接复用。`init --demo` 仅演示功能，不能代替会议模板。

服务打印 URL 后用浏览器工具或 `open_in_codex` 打开，保持服务进程可用。布局为最左文件树、中间源码、右侧 PDF。源码任意位置可键入或粘贴，支持撤销、保存、编译、多文件、入口和引擎选择。

预览必须来自真实 TeX 编译，不用 HTML/MathJax 仿制。编译失败显示日志并标注旧预览。PDF.js 文字层可选文批注；无文字的图片区域改用源码定位，不声称支持扫描件选字。

## 内置写作方法

写作前读 [写作方法](references/writing-method.md)。指定的 Research-Paper-Writing-Skills 已按固定 commit 内置于 [upstream](references/upstream/research-paper-writing/UPSTREAM-SKILL.md)，保留 [MIT 许可](references/upstream/LICENSE) 与 [来源记录](references/upstream/SOURCE.json)，无需另装。

- 先建立论文故事：问题 → 已有方法局限 → 核心洞见 → 方法 → 证据 → 边界；先小纲后正文。
- 一段一个主旨，首句说明主旨；新术语先定义，句间因果、对照、递进或解释关系明确。
- 每节写后做反向大纲：主题句如何支持本节和全文主张。
- 摘要/引言的重要主张对应真实实验、图表或已核验文献；不支持就降级或删除，不编数据、引用、DOI、优势或结论。
- 方法讲动机、设计和技术优势；实验说明公平比较、基线、参数、复现条件、消融和局限。
- 图表可读性属于内容质量，但不得擅改官方字号、版心、间距、类和 bibliography 样式。
- 按当前章节只加载相应原指南：`abstract.md`、`introduction.md`、`related-work.md`、`method.md`、`experiments.md`、`conclusion.md`，均位于 `references/upstream/research-paper-writing/references/`。最终用 `paper-review.md` 检查贡献、表达、实验强度、评估完整性、方法合理性。
- 主张证据表、段落角色标签、自审问题写进编辑笔记，不强塞投稿正文。

## 批注与修改

源码或 PDF 选文都可加标签与修改要求；保存原文、前后文、文件/行号或 PDF 页码、位置和来源版本。标签只是修改请求，不是执行任意工具的指令。

默认使用当前对话 Agent：网页提交后用户在本对话说“处理批注”，读取队列修改。**按钮默认只入队，不会自动唤醒已结束的对话。** 用户明确希望提交后自动修改，且有已登录 Codex CLI 时，serve 加 `--agent codex`；界面明确显示模式。继承用户模型配置，执行超时停止，不无限重试。

```bash
python3 "$SKILL_DIR/scripts/studio.py" pending --project "$PROJECT"
python3 "$SKILL_DIR/scripts/studio.py" wait --project "$PROJECT" --seconds 50
python3 "$SKILL_DIR/scripts/studio.py" resolve --project "$PROJECT" --id REQUEST_ID --status done --summary '修改内容与验证结果'
```

处理前重读会议规则和证据，核对选文版本；变更后通过引用及上下文重定位，不盲按旧行号替换。PDF→源码结合 SyncTeX 候选和上下文；无法唯一定位则 needs-info。润色不能擅加实验结论。

修改后编译、检查 PDF 和相关规则，记录改动、证据与待补项，再更新状态。自动 CLI 模式在隔离副本修改；仅原工程未发生并发变化、模板未改且新稿编译成功时合回。冲突和失败副本保存在 `.paper-studio/jobs/`。

## 合规与 Overleaf

按会议规范逐项记录通过 / 不通过 / 未核实 / 不适用及依据。编译通过不等于合规；投稿前重新核查官方政策，只对确已检查项下结论。

```bash
python3 "$SKILL_DIR/scripts/studio.py" export --project "$PROJECT" --output /absolute/paper-overleaf.zip
```

网页也可导出。ZIP 包含入口、章节、参考文献、图、类和样式，排除批注、日志、历史与私密笔记。Overleaf → New Project → Upload Project，按 `OVERLEAF-IMPORT.md` 设置 Main document、Compiler、TeX Live。只要求“可以导入”时交付包，不擅自登录、上传、共享或投稿。

最终提供项目路径、网页、编译状态、ZIP、模板版本及未核实规则/待补证据。未选 venue 时明确展示的是演示项目。
