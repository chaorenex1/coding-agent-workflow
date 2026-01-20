# Pre-Tool-Use Hook: Enforce Codex/Gemini Workflow Contract
# PowerShell version for Windows

$ErrorActionPreference = "Stop"

# Read JSON input from stdin
$INPUT = $input | Out-String

# Parse JSON
try {
    $json = $INPUT | ConvertFrom-Json
    $toolName = $json.tool_name
    $filePath = if ($json.parameters.file_path) { $json.parameters.file_path }
                elseif ($json.parameters.notebook_path) { $json.parameters.notebook_path }
                else { "" }
    $content = if ($json.parameters.content) { $json.parameters.content }
               elseif ($json.parameters.new_string) { $json.parameters.new_string }
               elseif ($json.parameters.new_source) { $json.parameters.new_source }
               else { "" }
} catch {
    # If parsing fails, allow the operation
    Write-Output $INPUT
    exit 0
}

# Define patterns
$codeExtensions = @(".js", ".ts", ".jsx", ".tsx", ".py", ".java", ".go", ".rs", ".cpp", ".c", ".h", ".rb", ".php", ".swift", ".kt", ".scala", ".sh", ".bash")
$uxExtensions = @(".css", ".scss", ".sass", ".less", ".html", ".vue", ".svelte")
$uxContentPatterns = @("class=", "style=", "<div", "<button", "@media", ".css", "background:", "color:")

# Check if tool is Edit/Write/NotebookEdit
if ($toolName -in @("Edit", "Write", "NotebookEdit")) {
    # Check for code file
    $isCodeFile = $false
    foreach ($ext in $codeExtensions) {
        if ($filePath -like "*$ext") {
            $isCodeFile = $true
            break
        }
    }

    if ($isCodeFile) {
        Write-Error "❌ BLOCKED: Direct edit to code file detected!"
        Write-Error "📋 File: $filePath"
        Write-Error "⚠️  Violation: Rule #2 Workflow Contract"
        Write-Error "✅ Required: Use /code-with-codex skill instead"
        Write-Error ""
        Write-Error "Suggested command:"
        Write-Error "  /code-with-codex [describe your code change]"
        exit 1
    }

    # Check for UX file or content
    $isUxFile = $false
    foreach ($ext in $uxExtensions) {
        if ($filePath -like "*$ext") {
            $isUxFile = $true
            break
        }
    }

    $hasUxContent = $false
    foreach ($pattern in $uxContentPatterns) {
        if ($content -like "*$pattern*") {
            $hasUxContent = $true
            break
        }
    }

    if ($isUxFile -or $hasUxContent) {
        Write-Error "❌ BLOCKED: Direct edit to UX/styling file detected!"
        Write-Error "📋 File: $filePath"
        Write-Error "⚠️  Violation: Rule #2 Workflow Contract"
        Write-Error "✅ Required: Use /ux-design-gemini skill instead"
        Write-Error ""
        Write-Error "Suggested command:"
        Write-Error "  /ux-design-gemini [describe your design change]"
        exit 1
    }
}

# Allow non-code/non-UX edits
Write-Output $INPUT
exit 0
