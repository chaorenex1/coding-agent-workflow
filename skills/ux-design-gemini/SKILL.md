---
name: ux-design-gemini
description: "Create UX designs using memex-cli with Gemini backend. Use when (1) Generating user flows and wireframes, (2) Creating UI component specifications, (3) Designing interaction patterns, (4) Building design system documentation, (5) Producing responsive layout guides."
---

# UX Design with Gemini

Use memex-cli to leverage Gemini for UX design tasks with multimodal analysis and structured output generation.

---

## When to Use This Skill

**Choose ux-design-gemini when:**
- Creating design documentation (personas, journey maps, wireframes)
- Building design systems and component libraries
- Analyzing design screenshots for critique
- Generating structured design specifications

**Choose other skills when:**
- **Code implementation** → Use [code-with-codex](../code-with-codex/SKILL.md)
- **Complex architecture decisions** → Use Claude via memex-cli
- **Multi-backend workflows** → Combine Gemini (design) + Codex (code)

---

## Design Stages Overview

| Stage | Design Tasks | Output Examples | Gemini Strengths |
|-------|--------------|-----------------|------------------|
| **Research** | User personas, journey maps | [User Research](examples/user-research.md) | Text analysis, structured output |
| **Define** | Information architecture, site maps | [IA Examples](examples/information-architecture.md) | Hierarchical structure generation |
| **Ideate** | User flows, concept descriptions | See Quick Start below | Rapid iteration on concepts |
| **Prototype** | Wireframe specs, mockups, design systems | [Wireframes](examples/wireframes-mockups.md), [Components](examples/component-systems.md) | Detailed specifications |
| **Test** | Design reviews, accessibility audits | [Design Review](examples/design-review.md) | **Image analysis** for visual critique |

➜ **Complete workflow guide:** [references/design-workflow.md](references/design-workflow.md)

---

## Quick Start

### Generate User Flow

```bash
memex-cli run --stdin <<'EOF'
---TASK---
id: user-flow
backend: gemini
workdir: /path/to/project
---CONTENT---
设计一个电商App的用户购物流程，包含浏览、加购、结算、支付的完整流程图
---END---
EOF
```

### Create Wireframe Spec

```bash
memex-cli run --stdin <<'EOF'
---TASK---
id: wireframe
backend: gemini
workdir: /path/to/project
---CONTENT---
为登录注册页面创建线框图规格说明，包含布局、组件位置、交互状态
---END---
EOF
```

### Design Component System

```bash
memex-cli run --stdin <<'EOF'
---TASK---
id: component-system
backend: gemini
workdir: /path/to/project
---CONTENT---
设计一套移动端UI组件规范，包含按钮、输入框、卡片、导航栏的样式定义
---END---
EOF
```

---

## Common UX Tasks

### User Research

```bash
memex-cli run --stdin <<'EOF'
---TASK---
id: personas
backend: gemini
---CONTENT---
为健身App创建3个用户画像，包含目标、痛点、使用场景
---END---
EOF
```

➜ **More examples:** [examples/user-research.md](examples/user-research.md)

---

### Information Architecture

```bash
memex-cli run --stdin <<'EOF'
---TASK---
id: sitemap
backend: gemini
---CONTENT---
为SaaS项目管理工具设计站点地图和导航结构
---END---
EOF
```

➜ **More examples:** [examples/information-architecture.md](examples/information-architecture.md)

---

### Wireframes & Mockups

```bash
memex-cli run --stdin <<'EOF'
---TASK---
id: wireframe-specs
backend: gemini
---CONTENT---
创建移动端外卖App关键页面的低保真线框图规格（首页、商家详情、购物车）
---END---
EOF
```

➜ **More examples:** [examples/wireframes-mockups.md](examples/wireframes-mockups.md)

---

### Component Systems

```bash
memex-cli run --stdin <<'EOF'
---TASK---
id: design-system
backend: gemini
---CONTENT---
创建设计系统文档：色彩系统、字体规范、间距体系、组件库
---END---
EOF
```

➜ **More examples:** [examples/component-systems.md](examples/component-systems.md)

---

### Design Review

```bash
memex-cli run --stdin <<'EOF'
---TASK---
id: heuristic-eval
backend: gemini
files: ./dashboard.png
files-mode: embed
---CONTENT---
使用Nielsen's 10 Heuristics评估这个仪表板设计
---END---
EOF
```

➜ **More examples:** [examples/design-review.md](examples/design-review.md)

---

## Multimodal Capabilities

**Gemini's unique strength:** Analyze design screenshots for visual critique.

### Upload Design for Review

```bash
memex-cli run --stdin <<'EOF'
---TASK---
id: design-critique
backend: gemini
files: ./mockup.png
files-mode: embed        # Required for image analysis
---CONTENT---
审查这个设计稿：
1. 视觉层次是否清晰
2. 色彩对比度是否符合WCAG AA标准
3. 组件布局是否合理
4. 留白和间距是否恰当
---END---
EOF
```

**Supported formats:** PNG, JPG, WEBP (< 5MB recommended)

### Compare Design Versions

```bash
memex-cli run --stdin <<'EOF'
---TASK---
id: version-compare
backend: gemini
files: ./v1-home.png, ./v2-home.png
files-mode: embed
---CONTENT---
对比这两个版本的首页设计，分析改进之处和潜在问题
---END---
EOF
```

### Competitive Analysis

```bash
memex-cli run --stdin <<'EOF'
---TASK---
id: competitive-analysis
backend: gemini
files: ./our-app.png, ./competitor-a.png, ./competitor-b.png
files-mode: embed
---CONTENT---
对比分析我们的App与竞品的设计：布局、视觉风格、交互模式
---END---
EOF
```

**Use cases:**
- Design critique and feedback
- Accessibility audit (color contrast check)
- Competitive screenshot analysis
- Design system compliance verification

➜ **Advanced image analysis techniques:** [references/multimodal-tips.md](references/multimodal-tips.md)

---

## Advanced Workflows

For multi-task workflows, parallel execution, and resume functionality, refer to memex-cli skill:

- **Multi-task DAG workflows:** [memex-cli/references/advanced-usage.md](../memex-cli/references/advanced-usage.md)
- **Parallel execution patterns:** [memex-cli/examples/parallel-tasks.md](../memex-cli/examples/parallel-tasks.md)
- **Resume interrupted runs:** [memex-cli/examples/resume-workflow.md](../memex-cli/examples/resume-workflow.md)

**Example multi-stage workflow:**

```bash
memex-cli run --stdin <<'EOF'
---TASK---
id: research
backend: gemini
---CONTENT---
用户研究
---END---

---TASK---
id: architecture
backend: gemini
dependencies: research
---CONTENT---
信息架构设计
---END---

---TASK---
id: wireframe
backend: gemini
dependencies: architecture
---CONTENT---
线框图规格
---END---
EOF
```

See [references/design-workflow.md](references/design-workflow.md) for complete design process with DAG examples.

---

## Quick Reference

### Required Fields

| Field | Description |
|-------|-------------|
| `id` | Unique task identifier |
| `backend` | `gemini` |
| `workdir` | Working directory path |

### Optional Fields

| Field | Default | Description |
|-------|---------|-------------|
| `dependencies` | - | Task IDs for sequential execution |
| `timeout` | 300 | Seconds |
| `files` | - | Design files to analyze (PNG, JPG) |
| `files-mode` | auto | `embed` (required for image analysis) |

---

## Additional Resources

### Progressive Disclosure Documentation

- **[HOW_TO_USE.md](HOW_TO_USE.md)** - Complete usage guide
  - When to use this skill
  - Gemini vs other backends
  - Integration with design tools
  - Workflow recommendations

- **[references/design-principles.md](references/design-principles.md)** - UX design fundamentals
  - UX methodologies (Design Thinking, UCD)
  - Nielsen's 10 heuristics
  - Mobile design guidelines (iOS HIG, Material Design)
  - Accessibility standards (WCAG 2.1)
  - Visual hierarchy and color theory

- **[references/design-workflow.md](references/design-workflow.md)** - Complete design process
  - 5-stage workflow (Research → Define → Ideate → Prototype → Test)
  - Deliverables by stage
  - DAG workflow examples
  - Iteration and feedback loops
  - Handoff to development

- **[references/multimodal-tips.md](references/multimodal-tips.md)** - Image analysis techniques
  - File format and size recommendations
  - Design critique prompt templates
  - Multi-image comparison analysis
  - Screenshot preparation tips

### Detailed Examples

- **[examples/user-research.md](examples/user-research.md)** - Personas, journey maps, competitive analysis
- **[examples/information-architecture.md](examples/information-architecture.md)** - Site maps, navigation, content hierarchy
- **[examples/wireframes-mockups.md](examples/wireframes-mockups.md)** - Lo-fi wireframes, hi-fi mockups, responsive layouts
- **[examples/component-systems.md](examples/component-systems.md)** - Design systems, component libraries, style guides
- **[examples/design-review.md](examples/design-review.md)** - Heuristic evaluations, accessibility audits, visual critiques

---

## Tips

1. **Use structured prompts**
   - Specify output format (Markdown tables, ASCII diagrams)
   - Provide context (target users, design constraints)
   - Include specific requirements (WCAG compliance, iOS HIG)

2. **Leverage multimodal analysis**
   - Upload design screenshots for visual feedback
   - Compare multiple design versions
   - Analyze competitor interfaces
   - Use `files-mode: embed` for image analysis

3. **Break down large projects**
   - Use dependencies for sequential stages
   - Parallelize independent pages/components
   - See [design workflow guide](references/design-workflow.md)

4. **Integrate with design tools**
   - Export from Figma/Sketch as PNG
   - Use Gemini to generate component specs
   - Create handoff documentation for developers

5. **Follow design principles**
   - Reference [design principles guide](references/design-principles.md)
   - Apply Nielsen's heuristics for evaluation
   - Ensure WCAG 2.1 Level AA compliance

---

## SKILL Reference

- [skills/memex-cli/SKILL.md](../memex-cli/SKILL.md) - Memex CLI full documentation
- [HOW_TO_USE.md](HOW_TO_USE.md) - Detailed usage guide for this skill
