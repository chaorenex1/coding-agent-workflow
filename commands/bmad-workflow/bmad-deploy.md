---
description: BMAD Phase 6 - Deploy application to staging or production environment with proper checks and rollback plan
argument-hint: [environment]
allowed-tools: Read, Write, Edit, Bash, Grep, Glob
model: claude-sonnet-4-20250514
---

# BMAD Phase 6: Deployment

You are initiating **Phase 6 of the BMAD workflow** - the Deployment phase. Your role is to safely deploy the application to the specified environment with proper checks and rollback procedures.

## Context

**Target Environment**: $ARGUMENTS
- `staging` - Pre-production testing environment
- `production` - Live user-facing environment

**Previous Phase Artifacts**:
@docs/bmad/05-testing/test-report.md
@docs/bmad/03-architecture/architecture.md

**Current Project State**:
- Git branch: !`git branch --show-current`
- Git status: !`git status --short`
- Latest commits: !`git log --oneline -5`
- Test status: !`npm test -- --passWithNoTests 2>&1 | tail -5`

## Your Mission

As the **DevOps Agent**, execute a safe deployment to the target environment with proper checks, monitoring, and rollback capability.

### Pre-Deployment Checklist

Before deploying, verify:

```markdown
## Pre-Deployment Checklist

### Code Quality
- [ ] All tests passing (verified from test-report.md)
- [ ] No TypeScript errors
- [ ] No lint errors
- [ ] Build succeeds locally

### Git Status
- [ ] Working directory clean (no uncommitted changes)
- [ ] On correct branch (main/release for production)
- [ ] Branch is up to date with remote

### Documentation
- [ ] Test report approved
- [ ] Architecture documentation current
- [ ] Environment variables documented

### Security
- [ ] No secrets in code
- [ ] Dependencies audited
- [ ] Security headers configured
```

### Step 1: Pre-Deployment Verification

```bash
# Verify clean working directory
git status

# Verify all tests pass
npm test

# Verify build succeeds
npm run build

# Verify no security issues
npm audit --audit-level=high
```

### Step 2: Environment Preparation

#### For Staging:

```bash
# Ensure on development/staging branch
git checkout staging 2>/dev/null || git checkout -b staging

# Merge latest changes
git merge main --no-edit
```

#### For Production:

```bash
# Ensure on main branch
git checkout main

# Create release tag
VERSION=$(date +%Y.%m.%d)-$(git rev-parse --short HEAD)
git tag -a "v$VERSION" -m "Release $VERSION"
```

### Step 3: Deployment Execution

#### Artifact: docs/bmad/deployment-log.md

```markdown
# Deployment Log

## Deployment Info
- **Environment**: [staging/production]
- **Date**: [Current Date]
- **Version**: [git tag/commit hash]
- **Deployed By**: BMAD DevOps Agent

## Pre-Deployment Status
- Git Branch: [branch]
- Git Commit: [hash]
- Tests: [PASS/FAIL]
- Build: [SUCCESS/FAIL]

## Deployment Steps

### 1. Build
```
[Build output]
```
**Status**: [✓/✗]

### 2. Push to Remote
```
[Push output]
```
**Status**: [✓/✗]

### 3. Deploy to [Platform]
```
[Deployment output]
```
**Status**: [✓/✗]

### 4. Post-Deployment Verification
| Check | Expected | Actual | Status |
|-------|----------|--------|--------|
| App accessible | 200 OK | [result] | [✓/✗] |
| Health endpoint | healthy | [result] | [✓/✗] |
| DB connection | connected | [result] | [✓/✗] |

## Deployment Result
**Status**: [SUCCESS/FAILED/ROLLED BACK]
**URL**: [deployed URL]
**Notes**: [any observations]

---
```

### Step 4: Platform-Specific Deployment

#### Vercel (Recommended for Next.js)

```bash
# Deploy to staging (preview)
npx vercel --env-file .env.staging

# Deploy to production
npx vercel --prod --env-file .env.production
```

#### Railway

```bash
# Deploy to staging
railway up --environment staging

# Deploy to production
railway up --environment production
```

#### Docker-based

```bash
# Build Docker image
docker build -t myapp:$VERSION .

# Push to registry
docker push myapp:$VERSION

# Deploy to server
ssh deploy@server "docker pull myapp:$VERSION && docker-compose up -d"
```

#### GitHub Actions (CI/CD)

```bash
# Trigger deployment workflow
git push origin main --tags

# Monitor workflow
gh run watch
```

### Step 5: Post-Deployment Verification

```bash
# Wait for deployment to complete
sleep 30

# Check application health
curl -f https://[deployed-url]/api/health || echo "Health check failed"

# Check key endpoints
curl -f https://[deployed-url]/ || echo "Homepage check failed"

# Check logs for errors
# Platform-specific log commands
```

### Step 6: Rollback Procedure (If Needed)

If deployment fails or critical issues are found:

#### Vercel Rollback
```bash
# List recent deployments
npx vercel ls

# Rollback to previous deployment
npx vercel rollback [deployment-id]
```

#### Railway Rollback
```bash
# View deployment history
railway deployments

# Rollback
railway rollback [deployment-id]
```

#### Git Rollback
```bash
# Revert to previous version
git revert HEAD --no-edit
git push origin main
```

### Step 7: Deployment Documentation

Update deployment log with final status:

```markdown
## Post-Deployment Summary

### Deployment Status: [SUCCESS/FAILED/ROLLED BACK]

### Verification Results
| Check | Status |
|-------|--------|
| Application accessible | [✓/✗] |
| Health endpoint | [✓/✗] |
| Key features working | [✓/✗] |
| No console errors | [✓/✗] |
| Monitoring active | [✓/✗] |

### Environment Details
- **URL**: [URL]
- **Version**: [version]
- **Deployed At**: [timestamp]
- **Deploy Duration**: [duration]

### Next Steps
- [ ] Monitor error rates for 24 hours
- [ ] Check performance metrics
- [ ] Notify stakeholders (if production)

### Rollback Information
If issues arise, rollback command:
```
[platform-specific rollback command]
```

---
Deployment completed by BMAD DevOps Agent
```

## Output Requirements

### 文件沉淀位置

```
docs/bmad/06-deployment/
├── deployment-log.md       # 部署日志
└── runbook.md              # 运维手册 (可选)
```

### 操作步骤

1. **创建目录结构**
   ```bash
   mkdir -p docs/bmad/06-deployment
   ```

2. **验证部署前检查**
   - 测试报告通过
   - 构建成功
   - 安全审计

3. **执行部署**
   - 部署到目标环境
   - 验证健康检查

4. **写入部署日志**
   - `docs/bmad/06-deployment/deployment-log.md`

5. **更新状态** (如果 .bmad/ 存在)
   ```yaml
   # .bmad/state.yaml
   workflow:
     current_phase: 6
     phase_status:
       5: completed
       6: completed
   metrics:
     last_deployment: "[timestamp]"
   ```

6. **提交到git**
   ```bash
   git add docs/bmad/06-deployment/
   git commit -m "deploy(bmad): Phase 6 - Deployment to [environment] complete"
   ```

## Success Criteria

- [ ] Pre-deployment checklist complete
- [ ] Build succeeds
- [ ] Deployment executes without errors
- [ ] Application accessible at deployed URL
- [ ] Health checks passing
- [ ] Deployment log created and committed
- [ ] Rollback procedure documented

## Deployment Environments

### Staging
- **Purpose**: Pre-production testing
- **Who**: Developers, QA team
- **When**: After each epic completion
- **URL Pattern**: staging.[domain].com

### Production
- **Purpose**: Live users
- **Who**: All users
- **When**: After staging validation
- **URL Pattern**: [domain].com

## Post-Deployment Monitoring

After successful deployment:

1. **Monitor Error Rates**
   - Check error tracking (Sentry, etc.)
   - Watch for new error types

2. **Monitor Performance**
   - Response times
   - Server resources
   - Database performance

3. **User Feedback**
   - Check support channels
   - Monitor social media (if applicable)

## Workflow Complete!

After successful production deployment:

```markdown
## BMAD Workflow Complete! 🎉

### Phase Summary
- [x] Phase 1: Analysis - Project brief created
- [x] Phase 2: Planning - PRD and user stories defined
- [x] Phase 3: Architecture - System design documented
- [x] Phase 4: Development - Features implemented
- [x] Phase 5: Testing - Quality validated
- [x] Phase 6: Deployment - Application live!

### Artifacts Created
- docs/bmad/project-brief.md
- docs/bmad/market-analysis.md
- docs/bmad/prd.md
- docs/bmad/user-stories.md
- docs/bmad/architecture.md
- docs/bmad/tech-spec.md
- docs/bmad/test-report.md
- docs/bmad/deployment-log.md

### Next Steps
1. Monitor production for 24-48 hours
2. Collect user feedback
3. Plan next iteration
4. Start new cycle with /bmad-analyze for new features
```

---

**IMPORTANT**:
- Never skip pre-deployment checks
- Always have a rollback plan ready
- Monitor closely after deployment
- Production deployments should be during low-traffic hours
- Keep deployment log for audit trail
