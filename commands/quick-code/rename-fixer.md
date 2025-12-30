# Rename Failure Fix Workflow

## Usage

`/rename-fixer <RENAME_CONTEXT>`

## Parameters

- `<RENAME_CONTEXT>`: Rename-related context, including:
  - Old name and new name
  - Or an error message / logs
  - Or affected file paths

## Context

- Automatically analyze naming references across the project
- Detect missed updates caused by renames
- Identify cross-file / cross-module naming dependencies

## Your Role

You are the **Rename Failure Fix Coordinator**, responsible for directing four specialist sub-agents:

1. **Rename Detective (rename-detective)** — Global scan to find all name references
2. **Impact Analyzer (impact-analyzer)** — Assess rename scope and risk
3. **Batch Fixer (batch-fixer)** — Execute systematic renames and fixes
4. **Rename Validator (rename-validator)** — Validate completeness and correctness

## Workflow

### Phase 1: Recon & Discovery (rename-detective)
```
Use rename-detective sub agent to scan entire codebase for [$RENAME_CONTEXT], identify all references including direct imports, string literals, comments, configuration files, and documentation, then output comprehensive reference map with file paths and line numbers.
```

**Outputs**:
- Complete reference list (file path + line number)
- Reference type classification (code/config/docs/comments)
- Name-usage heatmap (high-frequency areas)

### Phase 2: Impact Analysis (impact-analyzer)
```
Use impact-analyzer sub agent with reference map from rename-detective to evaluate rename impact across modules, assess risk levels for each reference type, identify potential breaking changes, and prioritize fixes by criticality.
```

**Outputs**:
- Impact report (module-level / file-level)
- Risk rating (high/medium/low)
- Fix priority list
- Potential side-effect warnings

### Phase 3: Batch Fix (batch-fixer)
```
Use batch-fixer sub agent with prioritized fix list from impact-analyzer to execute systematic renaming across all identified references, handle special cases like string literals and dynamic references, update configuration files and documentation, then generate change summary.
```

**Outputs**:
- Fix changes across all files
- Special-case handling notes
- Change summary report
- Rollback script (if needed)

### Phase 4: Validation & Confirmation (rename-validator)
```
Use rename-validator sub agent to verify all references updated correctly, check for residual old names using multiple search patterns, test critical imports and dependencies, ensure no compilation or runtime errors, then score completeness (0-100%). If score ≥95% complete workflow, otherwise identify missed references and use batch-fixer sub agent for targeted fixes, then re-validate.
```

**Outputs**:
- Validation score (0-100%)
- Missed reference list (if any)
- Functional test results
- Final quality report

## Quality Gate

### Validation Criteria
- **Completeness score ≥95%**: All references updated correctly
- **Build/compile passes**: No syntax/import errors
- **Tests pass**: Critical functional tests succeed
- **Docs synced**: Related docs updated

### Iteration Strategy
- **Round 1**: Main code references (typically reaches 85–92%)
- **Round 2**: Edge cases and misses (typically reaches 95%+)
- **Max 3 rounds**: Ensure quality without over-iterating

## Smart Capabilities

### 1. Intelligent Reference Detection
- **Multi-pattern matching**: variables, types, functions, properties
- **Context-aware**: distinguish same-name symbols in different scopes
- **Dynamic references**: string concatenation, reflection, etc.

### 2. Safe Fix Strategy
- **Non-invasive**: minimize structural code changes
- **Incremental validation**: validate after each batch
- **Atomic operations**: supports full rollback

### 3. Cross-file Coordination
- **Dependency topology**: fix in dependency order
- **Module boundaries**: detect cross-module interface changes
- **Version control**: auto-create a fix branch

## Special Scenarios

### Scenario 1: String Literals
```javascript
// Detect and prompt for manual confirmation
const apiPath = "/api/oldName/endpoint"  // may need updating
```

### Scenario 2: Config Files
```yaml
# Auto-detect and update
service:
  name: oldServiceName  # → newServiceName
```

### Scenario 3: Comments & Docs
```python
# Old name: oldFunction
# New name: newFunction  # auto-update comments
```

### Scenario 4: Dynamic References
```python
# Mark as requiring manual review
getattr(obj, "oldName")  # may impact runtime
```

## Output Format

### 1. Executive Summary
- Total reference count
- Successfully fixed count
- Manual review required count
- Overall completeness percentage

### 2. Detailed Report
```markdown
## Fix Report

### Metrics
- Files scanned: {file_count}
- References found: {total_refs}
- Auto-fixed: {auto_fixed}
- Manual review: {manual_review}
- Completeness: {completion_score}%

### Fix Details
#### File 1: path/to/file.ts
- Line 23: import { oldName } → import { newName }
- Line 45: function oldName() → function newName()

#### File 2: path/to/config.json
- Line 12: "name": "oldName" → "name": "newName"

### Manual Review Items
1. [High] src/utils.ts:67 - confirm string literal
2. [Medium] docs/README.md:34 - review documentation reference

### Validation Results
✓ Build/compile passes
✓ Import verification passes
✓ Unit tests pass
⚠ 2 items require manual review

### Next Actions
- [ ] Review manual items
- [ ] Run full test suite
- [ ] Update changelog
- [ ] Submit for code review
```

### 3. Storage Location
```
./.claude/rename-fixes/{timestamp}-{old_name}-to-{new_name}/
  ├── reference-map.json           # full reference map
  ├── impact-analysis.md           # impact analysis report
  ├── changes-summary.md           # change summary
  ├── validation-report.md         # validation report
  └── manual-review-items.md       # manual review checklist
```

## Success Criteria

- ✅ **No misses**: all code references updated
- ✅ **Build passes**: no syntax/type/import errors
- ✅ **Tests pass**: no regressions
- ✅ **Docs synced**: related docs updated
- ✅ **Traceable**: complete fix records and rollback capability

## Examples

### Example 1: Function Rename
```bash
/rename-fixer "Rename function calculatePrice to computeTotalCost"
```

### Example 2: From an Error Message
```bash
/rename-fixer "ReferenceError: getUserData is not defined (previous name: fetchUserInfo)"
```

### Example 3: Class Rename
```bash
/rename-fixer "Class UserManager was renamed to UserService; fix all references"
```

## Benefits

1. **Fully automated**: one command, end-to-end
2. **Low miss rate**: multi-dimensional scanning
3. **High efficiency**: batch processing saves time
4. **High reliability**: multi-round validation
5. **Rollback-ready**: safe change reversion
6. **Handles complexity**: smart support for edge cases

Provide the rename context, and the workflow will automatically complete recon, analysis, fix, and validation end-to-end.
