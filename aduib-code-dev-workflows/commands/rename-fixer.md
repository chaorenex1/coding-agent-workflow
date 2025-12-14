# 重命名错误修复工作流

## 用法

`/rename-fixer <RENAME_CONTEXT>`

## 参数

- `<RENAME_CONTEXT>`：重命名相关信息，包括：
  - 旧名称和新名称
  - 或者错误信息/日志
  - 或者受影响的文件路径

## 上下文

- 自动分析项目中的命名引用
- 检测因重命名导致的遗漏更新
- 识别跨文件、跨模块的命名依赖

## 你的角色

你是**重命名错误修复协调者**，负责指挥4个专业智能体协同工作：

1. **命名侦察员 (rename-detective)** —— 全局扫描，发现所有命名引用
2. **影响分析师 (impact-analyzer)** —— 评估重命名影响范围和风险
3. **批量修复员 (batch-fixer)** —— 执行批量重命名和修复
4. **验证专家 (rename-validator)** —— 验证修复完整性和正确性

## 工作流程

### 阶段 1：侦察与发现（rename-detective）
```
Use rename-detective sub agent to scan entire codebase for [$RENAME_CONTEXT], identify all references including direct imports, string literals, comments, configuration files, and documentation, then output comprehensive reference map with file paths and line numbers.
```

**输出产物**：
- 完整的引用清单（文件路径 + 行号）
- 引用类型分类（代码/配置/文档/注释）
- 命名使用热力图（高频引用区域）

### 阶段 2：影响分析（impact-analyzer）
```
Use impact-analyzer sub agent with reference map from rename-detective to evaluate rename impact across modules, assess risk levels for each reference type, identify potential breaking changes, and prioritize fixes by criticality.
```

**输出产物**：
- 影响范围报告（模块级/文件级）
- 风险评级（高/中/低）
- 修复优先级列表
- 潜在副作用预警

### 阶段 3：批量修复（batch-fixer）
```
Use batch-fixer sub agent with prioritized fix list from impact-analyzer to execute systematic renaming across all identified references, handle special cases like string literals and dynamic references, update configuration files and documentation, then generate change summary.
```

**输出产物**：
- 所有文件的修复更改
- 特殊情况处理记录
- 变更摘要报告
- 回滚脚本（如需要）

### 阶段 4：验证与确认（rename-validator）
```
Use rename-validator sub agent to verify all references updated correctly, check for residual old names using multiple search patterns, test critical imports and dependencies, ensure no compilation or runtime errors, then score completeness (0-100%). If score ≥95% complete workflow, otherwise identify missed references and use batch-fixer sub agent for targeted fixes, then re-validate.
```

**输出产物**：
- 验证得分（0-100%）
- 遗漏引用清单（如有）
- 功能测试结果
- 最终质量报告

## 质量门控机制

### 验证标准
- **完整性得分 ≥95%**：所有引用已正确更新
- **编译通过**：无语法错误或导入错误
- **测试通过**：关键功能测试无报错
- **文档同步**：相关文档已同步更新

### 迭代策略
- **第1轮**：主要代码引用修复（通常达到85-92%）
- **第2轮**：边缘情况和遗漏处理（通常达到95%+）
- **最大3轮**：确保质量同时避免过度迭代

## 智能特性

### 1. 智能引用检测
- **多模式匹配**：变量名、类型名、函数名、属性名
- **上下文感知**：区分同名不同作用域的引用
- **动态引用**：字符串拼接、反射调用等特殊情况

### 2. 安全修复策略
- **非侵入式**：最小化代码结构变动
- **增量验证**：每批次修复后即时验证
- **原子操作**：支持整体回滚

### 3. 跨文件协调
- **依赖拓扑**：按依赖顺序修复
- **模块边界**：识别模块间接口变化
- **版本控制**：自动创建修复分支

## 特殊场景处理

### 场景1：字符串字面量
```javascript
// 检测并提示人工确认
const apiPath = "/api/oldName/endpoint"  // 可能需要更新
```

### 场景2：配置文件
```yaml
# 自动识别并更新
service:
  name: oldServiceName  # → newServiceName
```

### 场景3：注释和文档
```python
# 旧名称：oldFunction
# 新名称：newFunction  # 自动更新注释
```

### 场景4：动态引用
```python
# 标记为需要人工审查
getattr(obj, "oldName")  # 可能影响运行时
```

## 输出格式

### 1. 执行摘要
- 总引用数量
- 修复成功数量
- 需要人工确认数量
- 总体完成度百分比

### 2. 详细报告
```markdown
## 修复报告

### 统计数据
- 扫描文件：{file_count}
- 发现引用：{total_refs}
- 自动修复：{auto_fixed}
- 人工确认：{manual_review}
- 完成度：{completion_score}%

### 修复详情
#### 文件1：path/to/file.ts
- 第23行：import { oldName } → import { newName }
- 第45行：function oldName() → function newName()

#### 文件2：path/to/config.json
- 第12行："name": "oldName" → "name": "newName"

### 人工确认项
1. [高优先级] src/utils.ts:67 - 字符串字面量需确认
2. [中优先级] docs/README.md:34 - 文档引用需审查

### 验证结果
✓ 编译通过
✓ 导入验证通过
✓ 单元测试通过
⚠ 2处需人工确认

### 后续行动
- [ ] 审查人工确认项
- [ ] 执行完整测试套件
- [ ] 更新变更日志
- [ ] 提交代码审查
```

### 3. 保存位置
```
./.claude/rename-fixes/{timestamp}-{old_name}-to-{new_name}/
  ├── reference-map.json           # 完整引用映射
  ├── impact-analysis.md           # 影响分析报告
  ├── changes-summary.md           # 变更摘要
  ├── validation-report.md         # 验证报告
  └── manual-review-items.md       # 人工确认清单
```

## 成功标准

- ✅ **零遗漏**：所有代码引用已更新
- ✅ **编译通过**：无语法或类型错误
- ✅ **测试通过**：现有测试无回归
- ✅ **文档同步**：相关文档已更新
- ✅ **可追溯**：完整的修复记录和回滚能力

## 使用示例

### 示例1：函数重命名
```bash
/rename-fixer "将函数 calculatePrice 重命名为 computeTotalCost"
```

### 示例2：基于错误信息
```bash
/rename-fixer "ReferenceError: getUserData is not defined (原名：fetchUserInfo)"
```

### 示例3：类重命名
```bash
/rename-fixer "类 UserManager 已重命名为 UserService，修复所有引用"
```

## 优势总结

1. **全自动化**：一条命令完成全流程
2. **零遗漏**：多维度扫描确保完整性
3. **高效率**：批量处理节省时间
4. **高可靠**：多轮验证确保质量
5. **可回滚**：支持安全的变更回退
6. **智能化**：自动处理复杂场景

只需提供重命名上下文，工作流将自动完成侦察、分析、修复、验证的完整流程！
