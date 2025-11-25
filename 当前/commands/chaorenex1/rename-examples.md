# 重命名修复工作流 - 使用示例

## 场景1：函数重命名

### 背景
将函数 `getUserData` 重命名为 `fetchUserInfo`，但遗漏了一些引用，导致编译错误。

### 错误信息
```
ReferenceError: getUserData is not defined
  at processUser (src/services/user.ts:45)
  at handleRequest (src/controllers/api.ts:23)
```

### 使用命令
```bash
/rename-fixer "ReferenceError: getUserData is not defined (原名：getUserData，新名：fetchUserInfo)"
```

或使用快速版本：
```bash
/quick-rename getUserData fetchUserInfo
```

### 执行过程

#### 阶段1：侦察（5秒）
```
🔍 命名侦察员正在扫描代码库...
✓ 扫描完成：发现 34 处引用分布在 12 个文件中
✓ 生成引用清单和热力图
```

#### 阶段2：分析（10秒）
```
📊 影响分析师正在评估影响...
✓ 影响范围：3个模块直接受影响
✓ 风险评级：中等（无公共API变更）
✓ 修复策略：4个批次，预计15分钟
```

#### 阶段3：修复（12分钟）
```
🔧 批量修复员正在执行修复...
✓ 批次1（P0 - 编译）：23处 ✓
✓ 批次2（P1 - 运行时）：6处 ✓
✓ 批次3（P2 - 内部）：5处 ✓
✓ 批次4（P3 - 文档）：0处
✓ 修复完成：34/34处
```

#### 阶段4：验证（3分钟）
```
✅ 验证专家正在检查完整性...
✓ 残留扫描：无遗漏
✓ 编译检查：通过
✓ 测试执行：45/45通过
✓ 完成度得分：98.5%
✅ 质量门控通过！
```

### 最终报告
```markdown
## 修复摘要
- 总引用数：34
- 自动修复：34
- 需人工确认：0
- 完成度：98.5%
- 状态：✅ 完成

## 后续行动
- [x] 编译通过
- [x] 测试通过
- [ ] 运行集成测试
- [ ] 更新变更日志
```

---

## 场景2：类重命名（包含配置文件）

### 背景
将类 `UserManager` 重命名为 `UserService`，影响代码和配置文件。

### 使用命令
```bash
/rename-fixer "将类 UserManager 重命名为 UserService，修复所有引用"
```

### 执行过程

#### 阶段1：侦察
```
🔍 发现 89 处引用：
- 代码文件：67处
- 配置文件：12处
- 文档文件：10处
```

#### 阶段2：分析
```
📊 影响分析：
- 直接依赖模块：8个
- 间接依赖模块：3个
- 高风险项：4处（配置文件）
- 预计时间：25分钟
```

#### 阶段3：修复
```
🔧 批量修复：
✓ P0（导入/类型）：36处
✓ P1（配置）：12处
  ⚠️ 2处需人工确认（API配置）
✓ P2（函数调用）：41处
✓ P3（文档）：10处
```

#### 阶段4：验证（第1轮）
```
⚠️ 验证得分：92.5%（<95%阈值）
问题：
- 配置文件中2处动态引用未处理
- 建议二次修复
```

#### 阶段3（二次修复）
```
🔧 针对遗漏项修复...
✓ 修复动态配置引用：2处
```

#### 阶段4：验证（第2轮）
```
✅ 验证得分：96.8%
✓ 无遗漏引用
✓ 编译和测试通过
✅ 质量门控通过！
```

### 人工确认项
```markdown
## 需要人工确认（2处）

### MANUAL-001：API配置路径
**文件**：config/api.yaml:23
**内容**：`endpoint: /api/UserManager/list`
**建议**：确认API是否需要向后兼容

### MANUAL-002：数据库表名
**文件**：database/schema.sql:45
**内容**：`CREATE TABLE user_manager (...)`
**建议**：数据库变更需要单独的迁移脚本
```

---

## 场景3：基于错误日志的快速修复

### 错误日志
```
Error: Cannot find module '../utils/oldHelper'
  at require (internal/modules/cjs/loader.js:883)
  at Object.<anonymous> (src/services/processor.ts:12)

Error: Property 'oldHelper' does not exist on type 'Utils'
  at src/controllers/api.ts:34
```

### 使用命令
```bash
/rename-fixer "oldHelper 已重命名为 newHelper，出现模块找不到和属性不存在错误"
```

### 执行结果
```
🔍 侦察：发现 12 处 oldHelper 引用
📊 分析：全部为内部引用，低风险
🔧 修复：12处自动修复完成
✅ 验证：100%通过，无遗漏

✅ 修复完成！
```

---

## 场景4：跨文件类型的全局重命名

### 背景
配置键 `service_name` 需要统一重命名为 `serviceName`（驼峰命名）

### 影响范围
- TypeScript代码
- JSON配置
- YAML配置
- 文档

### 使用命令
```bash
/quick-rename service_name serviceName
```

### 特殊处理

#### TypeScript
```typescript
// 自动处理
const config = {
  service_name: "api"  // → serviceName: "api"
}
```

#### JSON
```json
// 自动处理
{
  "service_name": "api"  // → "serviceName": "api"
}
```

#### YAML
```yaml
# 自动处理
service_name: api  # → serviceName: api
```

#### 文档
```markdown
<!-- 自动处理 -->
配置项 `service_name` 用于...  
<!-- → 配置项 `serviceName` 用于... -->
```

### 验证结果
```
✅ 跨文件类型修复完成
- TypeScript：23处
- JSON：8处
- YAML：12处
- Markdown：5处
总计：48处，100%成功
```

---

## 场景5：处理特殊字符和命名约定

### 场景A：驼峰到蛇形
```bash
/rename-fixer "将 calculateTotalPrice 改为 calculate_total_price"
```

智能体会自动识别命名约定变化，并处理：
- `calculateTotalPrice` → `calculate_total_price`
- `CalculateTotalPrice` → `Calculate_total_price`（如果存在）

### 场景B：带命名空间
```bash
/rename-fixer "将 Utils.oldHelper 改为 Utils.newHelper"
```

智能体会识别命名空间：
- `Utils.oldHelper()` → `Utils.newHelper()`
- 但不会误改 `oldHelper()`（无命名空间前缀）

---

## 最佳实践

### ✅ 推荐做法

1. **提供清晰的上下文**
```bash
# 好
/rename-fixer "函数 getUserData 已改为 fetchUserInfo，修复所有引用"

# 更好
/rename-fixer "ReferenceError: getUserData is not defined。原名：getUserData，新名：fetchUserInfo"
```

2. **先在测试分支执行**
```bash
git checkout -b fix/rename-getUserData
/quick-rename getUserData fetchUserInfo
```

3. **查看生成的报告**
```bash
# 查看修复摘要
cat .claude/rename-fixes/*/changes-summary.md

# 查看验证报告
cat .claude/rename-fixes/*/validation-report.md
```

4. **处理人工确认项**
```bash
# 查看需要人工确认的项
cat .claude/rename-fixes/*/manual-review-items.md
```

### ❌ 避免的做法

1. **不要在生产分支直接执行**
```bash
# 危险！
git checkout main
/quick-rename criticalFunction newName
```

2. **不要忽略人工确认项**
```markdown
⚠️ 高优先级确认项必须处理：
- API端点变更
- 数据库schema变更
- 外部配置引用
```

3. **不要跳过测试**
```bash
# 修复后务必运行测试
npm test
npm run test:integration
```

---

## 故障排除

### 问题1：验证得分低于95%

**原因**：存在遗漏的引用或编译错误

**解决**：
1. 查看验证报告中的"遗漏项分析"
2. 工作流会自动触发二次修复
3. 或手动处理标记的问题

### 问题2：动态引用无法自动修复

**表现**：
```javascript
const methodName = config.method  // 可能是 "oldName"
obj[methodName]()
```

**解决**：
1. 查看 `manual-review-items.md`
2. 手动审查运行时值
3. 添加映射逻辑：
```javascript
const nameMap = { "oldName": "newName" }
const methodName = nameMap[config.method] || config.method
```

### 问题3：测试失败

**原因**：测试代码中的硬编码值或mock未更新

**解决**：
1. 检查测试文件中的字符串字面量
2. 更新mock数据
3. 检查测试快照

---

## 工作流集成

### 与Git集成
```bash
# 1. 创建修复分支
git checkout -b fix/rename-operation

# 2. 执行修复
/quick-rename oldName newName

# 3. 查看变更
git diff

# 4. 提交变更
git add .
git commit -m "fix: rename oldName to newName

- Fixed 89 references across 45 files
- Updated configuration and documentation
- All tests passing (validation score: 96.5%)"

# 5. 推送并创建PR
git push origin fix/rename-operation
```

### 与CI/CD集成
```yaml
# .github/workflows/rename-check.yml
name: Rename Validation

on: [pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Check for naming inconsistencies
        run: |
          # 搜索常见的命名不一致
          npm run lint
          npm run type-check
          npm test
```

---

## 总结

重命名修复工作流提供：

1. **全自动化** - 一条命令完成全流程
2. **智能化** - 多智能体协同，处理复杂场景
3. **高质量** - 多轮验证，确保≥95%完成度
4. **可追溯** - 完整的报告和变更记录
5. **可回滚** - 支持安全的变更回退

无论是简单的变量重命名还是复杂的类重命名，都能高效、安全地完成！
