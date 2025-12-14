# Coding Agent Workflow

一个面向「多 Agent 编排」「代码工作流执行」「技能化复用」的轻量仓库。通过规范化的 `agents/`、`commands/` 与 `skills/` 目录，将提示工程与可运行脚本/技能结合，帮助你在真实项目中快速完成：项目脚手架、代码阅读与设计、影响面分析、重构与重命名、代码评审、以及技术生态评估等任务。

---

## 目录结构

- **env/**: 环境或运行依赖占位（如后续需要统一环境脚本）。
- **agents/**: 面向角色/流程的编排文档（如 PRD 开发、重构验证、评审流程等）。
- **commands/**: 以「命令」视角的工作流指令与操作手册（项目架构、代码阅读、快改/快更等）。
- **skills/**: 可执行的能力单元（Python 脚本等），例如代码重构分析器、Codex CLI 桥、Git 代码评审器、技术栈评估器等。

---

## 快速开始

1) 安装基础依赖（如需运行 Python 技能）：

```powershell
# 建议使用虚拟环境（任选其一）
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt  # 若 skills 下模块提供了依赖文件，请进入对应子目录安装
```

2) 浏览工作流文档，选择要执行的命令或技能：
- 工作流与角色说明：查看 agents/ 与 commands/ 下的各类 `*.md`
- 可运行技能：进入 skills/ 对应子目录的 `HOW_TO_USE.md` 或 `README.md`

---

## 使用示例

以下示例选取两个常用技能，演示最小可运行路径（具体以各技能目录的使用说明为准）。

- **技能：Codex CLI Bridge**（位置：`skills/codex-cli-bridge/`）
	- 功能：在命令行中桥接/执行基于文档的工作流，解析 `agents/`、`commands/` 指令并组织执行。
	- 尝试运行：
		```powershell
		Push-Location skills/codex-cli-bridge
		# 查看使用说明与示例输入
		Get-ChildItem
		# 安装依赖（若目录内提供 requirements/INSTALL）
		# 参考该技能的 INSTALL.md / README.md
		# 运行示例（以实际脚本为准）
		python bridge.py --help
		Pop-Location
		```

- **技能：代码重构分析器**（位置：`skills/code-refactor-analyzer/`）
	- 功能：根据输入（如 `sample_input.json`）生成重构分析报告，输出影响范围与建议。
	- 尝试运行：
		```powershell
		Push-Location skills/code-refactor-analyzer
		python main.py --input sample_input.json --out expected_output.json
		Pop-Location
		```

---

## 开发约定

- **文档即工作流**：`agents/` 与 `commands/` 下的 `*.md` 是可操作的流程指南或命令说明，保持清晰、原子化与可组合。
- **技能最小化**：`skills/` 下每个技能应有最小运行示例、输入/输出样例与依赖说明（`HOW_TO_USE.md`、`README.md`、`expected_output.json` 等）。
- **安全与合规**：避免引入含版权风险的数据或脚本；尊重第三方仓库的许可证。

---

## 贡献

欢迎通过以下方式贡献：
- 补充/优化工作流与命令文档（agents/、commands/）。
- 新增技能或完善现有技能的使用说明与示例。
- 修复问题与改进工程化脚本（如依赖安装、报告生成、可视化）。

提交 PR 前请确保：
- 文档清晰、示例可运行、依赖可安装。
- 不引入与本仓库范围无关的大改动。

---

## 致谢

感谢所有在多 Agent 编排、提示工程与工程化实践方面的开源探索者和文档作者；本仓库汇集并沉淀了在实际协作中行之有效的提示与流程范式，期待与你共同完善。

---

## License

MIT License - 详见 LICENSE 文件
