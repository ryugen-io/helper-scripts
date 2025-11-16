# Claude CI/CD Skip System

This repository uses a secure skip system for Claude CI/CD workflows with support for **global** and **individual workflow** skipping.

---

## How It Works

The system prevents accidental or unauthorized skipping of Claude CI/CD workflows through content or hash validation. You can skip **all workflows** or **specific workflows individually**.

### Centralized Skip Validation

All skip logic is centralized in `.github/workflows/check-skip.yml`, which is called by each workflow with its specific name. This eliminates code duplication and provides consistent behavior across all workflows.

---

## Skip File Types

### 1. Global Skip File: `.skip.all`

Skips **all** Claude CI/CD workflows.

**Affected workflows:**
- `claude.yml` - Issue/PR comments with @claude
- `claude-code-review.yml` - Automatic PR reviews
- `update-readme.yml` - README auto-updates

### 2. Workflow-Specific Skip Files

Skip **individual** workflows:

- `.skip.claude` - Only skip @claude issue/PR comments
- `.skip.claude-review` - Only skip automatic PR reviews
- `.skip.update-readme` - Only skip README auto-updates

**Priority:** Global skip is checked first, then workflow-specific skip.

---

## Two Security Modes

### Default Mode (Content-based)

Each skip file has its own unique default content. Simply create the file with the exact content:

| Skip File | Default Content | SHA256 Hash |
|-----------|----------------|-------------|
| `.skip.all` | `SKIP_ALL` | `88c37a9d66d9beb6754b78394d172d69277bbd3a09042a034030e254ca86a1dc` |
| `.skip.claude` | `SKIP_CLAUDE` | `077fecdbe0dd4dae5056aaf9d153f7b3190976bb29b0e6556f5b043f21457e74` |
| `.skip.claude-review` | `SKIP_REVIEW` | `a195ef1a0888cf99be6bf404deac8707a113ea7b4d0ca2861a3da02e87ebfe35` |
| `.skip.update-readme` | `SKIP_README` | `c88189c2b9754d9e3853ed6933bf5523a345119dbc463ec1a14a09a8d1f03b3c` |

**No GitHub Secrets required** - just copy the example file!

### Custom Mode (Hash-based)

Set workflow-specific GitHub Secrets with custom SHA256 hashes. Each workflow can have its own unique hash for additional security:

- `SKIP_FILE_HASH_ALL` - Custom hash for `.skip.all`
- `SKIP_FILE_HASH_CLAUDE` - Custom hash for `.skip.claude`
- `SKIP_FILE_HASH_CLAUDE_REVIEW` - Custom hash for `.skip.claude-review`
- `SKIP_FILE_HASH_UPDATE_README` - Custom hash for `.skip.update-readme`

**Benefits:**
- Different teams can control different workflows
- Revoke access to specific workflows by changing their hash
- Use your own secret content instead of defaults

---

## Usage Examples

### Skip ALL Workflows (Default Mode)

```bash
# Use the example file
cp .github/skips/.skip.all.example .github/skips/.skip.all

# Or create manually
echo -n "SKIP_ALL" > .github/skips/.skip.all

# Commit and push
git add .github/skips/.skip.all
git commit -m "Skip all Claude CI/CD workflows"
git push
```

### Skip ALL Workflows (Custom Mode)

```bash
# 1. Create your own secret content
echo -n "MySecretSkipToken2024!" > .github/skips/.skip.all

# 2. Calculate the hash
sha256sum .github/skips/.skip.all | awk '{print $1}'
# Example output: abc123def456...

# 3. Add the secret to GitHub:
#    Settings > Secrets and variables > Actions > New repository secret
#    Name: SKIP_FILE_HASH_ALL
#    Value: abc123def456...

# 4. Commit and push
git add .github/skips/.skip.all
git commit -m "Skip all Claude CI/CD with custom token"
git push
```

### Skip ONLY the Claude Comment Workflow (Default Mode)

```bash
# Use the example file
cp .github/skips/.skip.claude.example .github/skips/.skip.claude

# Or create manually
echo -n "SKIP_CLAUDE" > .github/skips/.skip.claude

# Commit and push
git add .github/skips/.skip.claude
git commit -m "Skip only @claude comment workflow"
git push
```

### Skip ONLY the Claude Comment Workflow (Custom Mode)

```bash
# Create custom content and set SKIP_FILE_HASH_CLAUDE secret
echo -n "ClaudeWorkflowToken123" > .github/skips/.skip.claude
sha256sum .github/skips/.skip.claude | awk '{print $1}'
# Add hash to GitHub Secret: SKIP_FILE_HASH_CLAUDE

git add .github/skips/.skip.claude
git commit -m "Skip only @claude comment workflow with custom token"
git push
```

### Skip ONLY the Code Review Workflow (Default Mode)

```bash
# Use the example file
cp .github/skips/.skip.claude-review.example .github/skips/.skip.claude-review

# Or create manually
echo -n "SKIP_REVIEW" > .github/skips/.skip.claude-review

# Commit and push
git add .github/skips/.skip.claude-review
git commit -m "Skip only automatic code reviews"
git push
```

### Skip ONLY the Code Review Workflow (Custom Mode)

```bash
# Create custom content and set SKIP_FILE_HASH_CLAUDE_REVIEW secret
echo -n "ReviewWorkflowToken456" > .github/skips/.skip.claude-review
sha256sum .github/skips/.skip.claude-review | awk '{print $1}'
# Add hash to GitHub Secret: SKIP_FILE_HASH_CLAUDE_REVIEW

git add .github/skips/.skip.claude-review
git commit -m "Skip only automatic code reviews with custom token"
git push
```

### Skip ONLY the README Update Workflow (Default Mode)

```bash
# Use the example file
cp .github/skips/.skip.update-readme.example .github/skips/.skip.update-readme

# Or create manually
echo -n "SKIP_README" > .github/skips/.skip.update-readme

# Commit and push
git add .github/skips/.skip.update-readme
git commit -m "Skip only README auto-updates"
git push
```

### Skip ONLY the README Update Workflow (Custom Mode)

```bash
# Create custom content and set SKIP_FILE_HASH_UPDATE_README secret
echo -n "ReadmeWorkflowToken789" > .github/skips/.skip.update-readme
sha256sum .github/skips/.skip.update-readme | awk '{print $1}'
# Add hash to GitHub Secret: SKIP_FILE_HASH_UPDATE_README

git add .github/skips/.skip.update-readme
git commit -m "Skip only README auto-updates with custom token"
git push
```

---

## Re-enabling Workflows

### Re-enable ALL Workflows

```bash
rm .github/skips/.skip.all
git add .github/skips/.skip.all
git commit -m "Re-enable all Claude CI/CD workflows"
git push
```

### Re-enable Specific Workflow

```bash
# Re-enable @claude comments only
rm .github/skips/.skip.claude

# Re-enable code reviews only
rm .github/skips/.skip.claude-review

# Re-enable README updates only
rm .github/skips/.skip.update-readme

git add .github/skips/
git commit -m "Re-enable specific Claude workflows"
git push
```

---

## Security Features

1. **Content Validation**: Each skip file has a unique default content
2. **Hash Validation**: Custom mode requires exact hash match
3. **Centralized Logic**: All validation happens in one place (no code duplication)
4. **Fallback Logic**: Invalid skip files are ignored, CI/CD continues normally
5. **Audit Trail**: All skip attempts are documented in workflow logs
6. **Flexibility**: Supports both simple default and custom secret-based modes
7. **Granular Control**: Skip all workflows or individual ones

---

## Architecture

### Centralized Validation

```
check-skip.yml (reusable workflow)
    ├── Accepts: workflow_name parameter
    ├── Checks: .skip.all (global)  default content: "SKIP_ALL"
    ├── Checks: .skip.<workflow_name> (individual)  unique default content
    └── Returns: should_skip output

claude.yml
    └── Calls: check-skip.yml with workflow_name="claude"
         Checks for .skip.claude (default: "SKIP_CLAUDE")

claude-code-review.yml
    └── Calls: check-skip.yml with workflow_name="claude-review"
         Checks for .skip.claude-review (default: "SKIP_REVIEW")

update-readme.yml
    └── Calls: check-skip.yml with workflow_name="update-readme"
         Checks for .skip.update-readme (default: "SKIP_README")
```

### Validation Priority

1. **Check global skip** (`.skip.all`)  Content: `SKIP_ALL` or custom hash
2. **Check workflow-specific skip** (`.skip.<workflow_name>`)  Unique content or custom hash
3. **No valid skip found**  Proceed with workflow

### Validation Logic

For each skip file:
1. **If custom hash secret is set**  Validate against that hash (custom mode)
2. **Otherwise**  Validate against default content (default mode)

---

## Best Practices

1. **Use default mode** for quick, temporary skips (no secrets required)
2. **Use custom mode** for production environments and permanent skips
3. **Use individual skips** when you only want to disable specific workflows
4. **Use global skip** during maintenance windows or when testing
5. **Document skip reasons** in commit messages
6. **Remove skip files** when no longer needed
7. **Check workflow logs** to verify skip behavior

---

## Troubleshooting

### Skip File Not Working (Default Mode)

1. Verify exact content: `cat -A .github/skips/.skip.all`
2. Should show the exact default content with no trailing newline:
   - `.skip.all`  `SKIP_ALL$`
   - `.skip.claude`  `SKIP_CLAUDE$`
   - `.skip.claude-review`  `SKIP_REVIEW$`
   - `.skip.update-readme`  `SKIP_README$`
3. If content is wrong, recreate: `echo -n "SKIP_ALL" > .github/skips/.skip.all`
4. Review workflow logs in `.github/workflows/logs/`

### Skip File Not Working (Custom Mode)

1. Check hash: `sha256sum .github/skips/.skip.all`
2. Verify it matches the hash in your GitHub Secret (e.g., `SKIP_FILE_HASH_ALL`)
3. Ensure the secret name is correct for the skip file type
4. Review workflow logs in `.github/workflows/logs/`

### Workflow Still Running Despite Skip File

1. Check if skip file is committed and pushed
2. Verify workflow_name matches skip file name (e.g., `.skip.claude` for `workflow_name: "claude"`)
3. Check for hash mismatch or content errors in workflow logs
4. Ensure file contains no extra whitespace or newlines
5. Verify you're using the correct default content for the workflow type

### Want to Skip Multiple but Not All Workflows

Create individual skip files:
```bash
cp .github/skips/.skip.claude.example .github/skips/.skip.claude
cp .github/skips/.skip.claude-review.example .github/skips/.skip.claude-review
# Don't create .skip.update-readme - it will still run

git add .github/skips/
git commit -m "Skip Claude and code review, keep README updates"
git push
```

---

## Quick Reference

### Default Contents

```bash
# Global skip
echo -n "SKIP_ALL" > .github/skips/.skip.all

# Individual skips
echo -n "SKIP_CLAUDE" > .github/skips/.skip.claude
echo -n "SKIP_REVIEW" > .github/skips/.skip.claude-review
echo -n "SKIP_README" > .github/skips/.skip.update-readme
```

### Default Hashes

```bash
# SKIP_ALL
88c37a9d66d9beb6754b78394d172d69277bbd3a09042a034030e254ca86a1dc

# SKIP_CLAUDE
077fecdbe0dd4dae5056aaf9d153f7b3190976bb29b0e6556f5b043f21457e74

# SKIP_REVIEW
a195ef1a0888cf99be6bf404deac8707a113ea7b4d0ca2861a3da02e87ebfe35

# SKIP_README
c88189c2b9754d9e3853ed6933bf5523a345119dbc463ec1a14a09a8d1f03b3c
```

### Custom Hash Generation

```bash
# Generate custom content and hash for any workflow
echo -n "YourCustomSecret" | sha256sum | awk '{print $1}'

# Or use random token
openssl rand -base64 32 | tee .github/skips/.skip.all | sha256sum | awk '{print $1}'
```

### GitHub Secret Names

- `.skip.all`  `SKIP_FILE_HASH_ALL`
- `.skip.claude`  `SKIP_FILE_HASH_CLAUDE`
- `.skip.claude-review`  `SKIP_FILE_HASH_CLAUDE_REVIEW`
- `.skip.update-readme`  `SKIP_FILE_HASH_UPDATE_README`

---

**Version:** 2.0 (Individual Skip System)
**Last Updated:** 2025-11-16
