# Quick Rename Fix

## Usage

`/quick-rename <OLD_NAME> <NEW_NAME>`

## Parameters

- `<OLD_NAME>`: The old name to be renamed
- `<NEW_NAME>`: The new name

## Overview

This is a simplified version of `/rename-fixer` for straightforward renames. It automatically runs four phases: recon, analysis, fix, and validation.

## Agent Chain

```
First use rename-detective sub agent to scan codebase for [<OLD_NAME>] and generate reference map, 
then use impact-analyzer sub agent to evaluate impact and create fix strategy, 
then use batch-fixer sub agent to execute fixes following the strategy, 
then use rename-validator sub agent to validate completeness with scoring. 
If validation score ≥95% complete workflow with final report, 
otherwise use batch-fixer sub agent again with validation feedback for missed references and repeat validation.
```

## Workflow

1. **Recon** - Scan all references of `<OLD_NAME>`
2. **Analysis** - Evaluate impact scope and risk
3. **Fix** - Execute the rename in batch
4. **Validation** - Validate completeness (target ≥95%)
5. **Iterate** - If needed, fix missed items and validate again

## Quality Assurance

- ✅ Automatically scans all file types
- ✅ Smart categorization and prioritization
- ✅ Batch fixes for consistency
- ✅ Multi-dimensional validation for completeness
- ✅ Auto-pass when score ≥95%

## Outputs

Generated under `.claude/rename-fixes/{timestamp}-{old_name}-to-{new_name}/`:
- `reference-map.json` - Reference inventory
- `impact-analysis.md` - Impact analysis
- `changes-summary.md` - Change summary
- `validation-report.md` - Validation report
- `manual-review-items.md` - Items requiring manual review

## Examples

```bash
/quick-rename calculatePrice computeTotalCost
/quick-rename UserManager UserService
/quick-rename old_function new_function
```

## Suitable For

✅ Function/variable renames
✅ Class/interface renames
✅ Module renames
✅ Config key renames

## Not Suitable For

❌ Cross-repo renames
❌ Renames involving external APIs (requires extra backward-compat consideration)
❌ Complex refactors (prefer IDE refactor tools)

## Differences vs Full Version

| Feature | quick-rename | rename-fixer |
|-----|-------------|--------------|
| Parameters | Simple (old/new) | Flexible (supports error messages, etc.) |
| Control | Fully automatic | Can be run step-by-step |
| Report | Standard format | Detailed and customizable |
| Best for | Simple scenarios | Complex scenarios |

Use the full `/rename-fixer` command when you need finer-grained control.
