# 快速重命名修复

## 用法

`/quick-rename <OLD_NAME> <NEW_NAME>`

## 参数

- `<OLD_NAME>`：需要重命名的旧名称
- `<NEW_NAME>`：新的名称

## 简介

这是 `/rename-fixer` 的简化版本，适用于简单的重命名场景。自动完成侦察、分析、修复、验证四个阶段。

## 智能体链

```
First use rename-detective sub agent to scan codebase for [<OLD_NAME>] and generate reference map, 
then use impact-analyzer sub agent to evaluate impact and create fix strategy, 
then use batch-fixer sub agent to execute fixes following the strategy, 
then use rename-validator sub agent to validate completeness with scoring. 
If validation score ≥95% complete workflow with final report, 
otherwise use batch-fixer sub agent again with validation feedback for missed references and repeat validation.
```

## 工作流程

1. **侦察阶段** - 扫描所有 `<OLD_NAME>` 引用
2. **分析阶段** - 评估影响范围和风险
3. **修复阶段** - 批量执行重命名
4. **验证阶段** - 验证完整性（目标≥95%）
5. **迭代优化** - 如需要，针对遗漏项再次修复

## 质量保证

- ✅ 自动扫描所有文件类型
- ✅ 智能分类和优先级排序
- ✅ 批量修复保证一致性
- ✅ 多维度验证确保完整性
- ✅ 得分≥95%自动通过

## 输出

生成在 `.claude/rename-fixes/{timestamp}-{old_name}-to-{new_name}/` 目录：
- `reference-map.json` - 引用清单
- `impact-analysis.md` - 影响分析
- `changes-summary.md` - 变更摘要
- `validation-report.md` - 验证报告
- `manual-review-items.md` - 人工确认项

## 示例

```bash
/quick-rename calculatePrice computeTotalCost
/quick-rename UserManager UserService
/quick-rename old_function new_function
```

## 适用场景

✅ 函数/变量重命名
✅ 类/接口重命名
✅ 模块重命名
✅ 配置键重命名

## 不适用场景

❌ 跨仓库重命名
❌ 涉及外部API的重命名（需要额外考虑向后兼容）
❌ 复杂的代码重构（建议使用IDE重构工具）

## 与完整版的区别

| 特性 | quick-rename | rename-fixer |
|-----|-------------|--------------|
| 参数 | 简单（新旧名称） | 灵活（支持错误信息等） |
| 控制 | 全自动 | 可分步执行 |
| 报告 | 标准格式 | 详细可定制 |
| 适用 | 简单场景 | 复杂场景 |

需要更细粒度控制时，请使用完整版 `/rename-fixer` 命令。
