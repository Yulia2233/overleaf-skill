# 运行与批注协议

Python 3.10+ 标准库后端，CodeMirror/PDF.js 已本地打包。编译依赖 latexmk 和选定引擎，缺失会报错。不读项目 latexmkrc，不开 shell escape。需要 minted 的模板先核实官方允许的方案。

```bash
python3 scripts/studio.py init --project /absolute/paper --template /absolute/template.zip --main main.tex --engine pdflatex
python3 scripts/studio.py configure --project /absolute/existing --main main.tex --engine xelatex
python3 scripts/studio.py serve --project /absolute/paper --port 0
python3 scripts/studio.py compile --project /absolute/paper
python3 scripts/studio.py export --project /absolute/paper --output /absolute/paper-overleaf.zip
```

服务只绑定 127.0.0.1，URL fragment 是凭证；用实际返回 URL，不猜端口。运行信息在 `.paper-studio/server.json`。需要后台运行时用 subprocess.Popen(start_new_session=True)，日志写 `.paper-studio/server.log`；检查并复用已有服务。`init --demo` 仅演示，不代表任何会议模板。

文件树可切换、新建文本、导入图片/源码。源码有行号、高亮、撤销、Cmd/Ctrl+S。修改后显式保存/编译；未保存离开有提示；外部变更时保存返回冲突，不覆盖。

源码选文或光标插入点、PDF 文字层选文 → 批注选文 → 标签与要求 → 保存批注 → 提交批注。批注持久化在 `.paper-studio/state.json`，记录来源版本、引用、行号/页码、矩形、SyncTeX 候选。候选不是精确语义映射；旧 PDF 不接受新执行批注。失败编译保留上次 PDF，明确显示旧预览。

默认“当前对话”模式：用户提交后在对话说“处理批注”，Agent 用 pending 读取；处理前核对来源，修改后编译，resolve 标完成。可用 wait 等待一次，最长 60 秒。已结束对话不会被网页按钮自动唤醒。

用户明确选择自动模式后，加 `--agent codex`：使用已登录 CLI，在隔离副本执行 `codex exec --sandbox workspace-write --skip-git-repo-check --ephemeral`，不指定模型、不跳过沙箱。提示含会议规则、证据笔记、批注、写作方法。原项目来源摘要未变、模板未改、候选编译成功才合并；否则保留任务副本，标失败或冲突。超时停止，不无限重试。

状态：draft → pending → processing → done / failed / conflict / needs-info。重启发现 processing 会标 failed 并保留记录。提交前保存。自动修改期间并发编辑会保守拒绝整批合并。

`.paper-studio/`、`venue/`、上下文/大纲/证据/合规笔记均不进入 Overleaf 包。保留源码、图表、字体和模板依赖及目录结构，添加入口/引擎/TeX Live 说明。导出后在干净目录解压编译验证，不冒称已经在 Overleaf 云端测试。

修改前端时在 assets 运行 npm ci 与 node build.mjs；分发不含 node_modules。`python3 scripts/test_studio.py` 验证冲突、队列、失败编译、ZIP 安全、导出重编译；另用浏览器检查编辑、PDF 选文和提交。
