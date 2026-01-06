# Installation Guide - Development Workflow Suite

**Complete installation instructions for all 10 slash commands.**

---

## 🚀 Quick Install (Recommended)

### Install All Commands at Once

#### User-Level (All Projects)

**macOS / Linux:**
```bash
cp generated-commands/dev-workflow-suite/{debug,fix,explain,requirements-understanding,requirements-analysis,ask-user,implementation-analysis,optimization,refactoring,test}.md ~/.claude/commands/
```

**Windows PowerShell:**
```powershell
Copy-Item generated-commands\dev-workflow-suite\*.md $HOME\.claude\commands\
```

**Windows Command Prompt:**
```cmd
copy generated-commands\dev-workflow-suite\*.md %USERPROFILE%\.claude\commands\
```

#### Project-Level (Current Project)

**macOS / Linux:**
```bash
mkdir -p .claude/commands
cp generated-commands/dev-workflow-suite/{debug,fix,explain,requirements-understanding,requirements-analysis,ask-user,implementation-analysis,optimization,refactoring,test}.md .claude/commands/
```

**Windows PowerShell:**
```powershell
New-Item -ItemType Directory -Force -Path .claude\commands
Copy-Item generated-commands\dev-workflow-suite\*.md .claude\commands\
```

---

## 📦 Selective Installation

### Install Only What You Need

#### Essential Commands (Recommended Start)

```bash
# Install core development commands
cp generated-commands/dev-workflow-suite/debug.md ~/.claude/commands/
cp generated-commands/dev-workflow-suite/fix.md ~/.claude/commands/
cp generated-commands/dev-workflow-suite/test.md ~/.claude/commands/
```

#### By Development Phase

**Requirements Phase:**
```bash
cp generated-commands/dev-workflow-suite/requirements-understanding.md ~/.claude/commands/
cp generated-commands/dev-workflow-suite/requirements-analysis.md ~/.claude/commands/
cp generated-commands/dev-workflow-suite/ask-user.md ~/.claude/commands/
```

**Implementation Phase:**
```bash
cp generated-commands/dev-workflow-suite/implementation-analysis.md ~/.claude/commands/
cp generated-commands/dev-workflow-suite/explain.md ~/.claude/commands/
```

**Quality Phase:**
```bash
cp generated-commands/dev-workflow-suite/test.md ~/.claude/commands/
cp generated-commands/dev-workflow-suite/refactoring.md ~/.claude/commands/
cp generated-commands/dev-workflow-suite/optimization.md ~/.claude/commands/
```

**Maintenance Phase:**
```bash
cp generated-commands/dev-workflow-suite/debug.md ~/.claude/commands/
cp generated-commands/dev-workflow-suite/fix.md ~/.claude/commands/
```

---

## ✅ Verification

### Check Installation

```bash
# List installed commands
ls ~/.claude/commands/

# Or for project-level
ls .claude/commands/

# Expected output:
# debug.md
# fix.md
# explain.md
# requirements-understanding.md
# requirements-analysis.md
# ask-user.md
# implementation-analysis.md
# optimization.md
# refactoring.md
# test.md
```

### Test a Command

```bash
# Start Claude Code
claude code

# Try a command
/debug

# You should see the debugging assistant activate
```

---

## 📍 Installation Locations

### User-Level Installation
**Path:** `~/.claude/commands/`

**Pros:**
- ✅ Available in all projects
- ✅ Install once, use everywhere
- ✅ Personal workflow customization

**Cons:**
- ❌ Updates affect all projects
- ❌ Not shared with team

**Best for:**
- Personal development
- Freelancers
- Solo projects

---

### Project-Level Installation
**Path:** `.claude/commands/`

**Pros:**
- ✅ Version controlled
- ✅ Team collaboration
- ✅ Project-specific customization

**Cons:**
- ❌ Must install per project
- ❌ Manual sync across projects

**Best for:**
- Team projects
- Open source
- Client projects

---

## 👥 Team Installation

### 1. Install at Project Level

```bash
# Create commands directory
mkdir -p .claude/commands

# Copy all commands
cp generated-commands/dev-workflow-suite/*.md .claude/commands/

# Verify
ls .claude/commands/
```

### 2. Commit to Version Control

```bash
# Add to git
git add .claude/commands/

# Commit
git commit -m "feat: add development workflow slash commands suite

Includes 10 slash commands:
- /debug - Interactive debugging
- /fix - Automated bug fixes
- /explain - Code explanation
- /requirements-understanding - Requirements clarification
- /requirements-analysis - Technical requirements
- /ask-user - Question generation
- /implementation-analysis - Implementation planning
- /optimization - Performance optimization
- /refactoring - Code quality improvement
- /test - Test generation
"

# Push
git push origin main
```

### 3. Team Members Pull

```bash
# Team members pull
git pull

# Commands automatically available
/debug
/test
# etc.
```

### 4. Document Team Workflows

Add to `CONTRIBUTING.md`:

```markdown
## Development Slash Commands

We use the following slash commands for standardized workflows:

### Bug Fix Process
1. `/debug [issue]` - Investigate the bug
2. `/fix [issue]` - Implement fix with tests
3. `/test [component]` - Verify fix
4. Commit and create PR

### Feature Development
1. `/requirements-understanding [feature]` - Clarify requirements
2. `/requirements-analysis [feature]` - Technical planning
3. `/implementation-analysis [feature]` - Design implementation
4. Implement feature
5. `/test [feature]` - Add tests
6. `/refactoring [code]` - Improve quality

See `.claude/commands/` for all available commands.
```

---

## 🔄 Updating Commands

### Update User-Level Installation

```bash
# Re-copy commands
cp generated-commands/dev-workflow-suite/*.md ~/.claude/commands/

# Restart Claude Code session
```

### Update Project-Level Installation

```bash
# Re-copy commands
cp generated-commands/dev-workflow-suite/*.md .claude/commands/

# Commit update
git add .claude/commands/
git commit -m "chore: update development workflow commands"
git push
```

---

## 🗑️ Uninstalling

### Remove User-Level Installation

**macOS / Linux:**
```bash
rm ~/.claude/commands/{debug,fix,explain,requirements-understanding,requirements-analysis,ask-user,implementation-analysis,optimization,refactoring,test}.md
```

**Windows PowerShell:**
```powershell
Remove-Item $HOME\.claude\commands\{debug,fix,explain,requirements-understanding,requirements-analysis,ask-user,implementation-analysis,optimization,refactoring,test}.md
```

### Remove Project-Level Installation

```bash
# Remove directory
rm -rf .claude/commands/

# Or keep directory but remove specific commands
rm .claude/commands/{debug,fix,explain,requirements-understanding,requirements-analysis,ask-user,implementation-analysis,optimization,refactoring,test}.md
```

---

## 🛠️ Prerequisites

### Required Tools (All Commands)

```bash
# Verify git
git --version
# Required: ≥ 2.x

# Verify grep
grep --version
# Required: Any version

# Verify find
find --version
# Required: Any version
```

### Optional Tools (Enhanced Features)

**For Node.js Projects:**
```bash
node --version  # ≥ 14.x
npm --version   # ≥ 6.x
```

**For Python Projects:**
```bash
python --version  # ≥ 3.7
pip --version     # ≥ 20.x
```

**For Testing:**
```bash
jest --version   # For JavaScript testing
pytest --version # For Python testing
```

---

## 🔧 Configuration

### Custom Bash Permissions

If you need to add additional bash commands, edit the command's YAML frontmatter:

```yaml
---
description: ...
allowed-tools: Read, Write, Bash(git status:*), Bash(your-custom-command:*)
---
```

**Note:** Never use wildcard `Bash` - always specify exact commands.

### Custom Log Paths

For `/debug` command, edit to include custom log locations:

```bash
# Edit debug.md
nano ~/.claude/commands/debug.md

# Find the log discovery section and add your paths
!`find . /your/custom/logs -type f -name "*.log" ...`
```

---

## 🐛 Troubleshooting

### Commands Not Found

**Symptom:** `/debug` shows "command not found"

**Solutions:**
1. Verify installation location:
   ```bash
   ls ~/.claude/commands/debug.md
   ```

2. Check filename (must be lowercase with .md extension):
   ```bash
   # Correct
   debug.md

   # Incorrect
   Debug.md
   DEBUG.md
   debug.MD
   ```

3. Restart Claude Code session

---

### Permission Errors

**Symptom:** "Permission denied" when running bash commands

**Solutions:**
1. Check YAML frontmatter has correct bash permissions
2. Verify bash tools are installed (`git`, `grep`, `find`)
3. Check file system permissions:
   ```bash
   ls -la ~/.claude/commands/
   chmod 644 ~/.claude/commands/*.md
   ```

---

### YAML Parse Errors

**Symptom:** Command loads but doesn't work

**Solutions:**
1. Verify YAML frontmatter syntax:
   - Starts with `---`
   - Ends with `---`
   - Proper indentation
   - No special characters

2. Validate with online YAML validator

3. Compare with working command file

---

### Git Not Found

**Symptom:** Git commands fail

**Solutions:**
1. Install Git:
   ```bash
   # macOS
   brew install git

   # Ubuntu/Debian
   sudo apt-get install git

   # Windows
   # Download from git-scm.com
   ```

2. Verify PATH:
   ```bash
   which git
   echo $PATH
   ```

---

## 🎯 Platform-Specific Notes

### macOS

- Use Homebrew for tools: `brew install git`
- Commands location: `/Users/username/.claude/commands/`
- Use `bash` or `zsh` shell

### Linux

- Use package manager: `apt-get`, `yum`, `dnf`
- Commands location: `/home/username/.claude/commands/`
- Most tools pre-installed

### Windows

- Use Git Bash or WSL for best compatibility
- Commands location: `C:\Users\username\.claude\commands\`
- Install Git for Windows from git-scm.com
- PowerShell recommended for installation

---

## 📚 Next Steps

After installation:

1. **Read README.md**
   ```bash
   cat generated-commands/dev-workflow-suite/README.md
   ```

2. **Review Workflow Guide**
   ```bash
   cat generated-commands/dev-workflow-suite/WORKFLOW_GUIDE.md
   ```

3. **Test Each Command**
   ```bash
   /debug
   /test
   /explain
   # etc.
   ```

4. **Customize for Your Needs**
   - Edit bash permissions
   - Adjust output formats
   - Add project-specific patterns

5. **Create Team Workflows**
   - Document standard processes
   - Share with team
   - Measure impact

---

## 💡 Tips

**For Best Results:**
- Install user-level for personal use
- Install project-level for team collaboration
- Start with 3-4 essential commands
- Add more as you get comfortable
- Customize to fit your workflow

**Performance:**
- Commands are lightweight (text files)
- No performance impact
- Instant loading
- Parallel execution supported

**Maintenance:**
- Update when new versions available
- Keep customizations documented
- Share improvements with team
- Version control project-level installations

---

**You're ready to transform your development workflow!** 🚀

For questions or issues, refer to the troubleshooting section or check individual command documentation.
