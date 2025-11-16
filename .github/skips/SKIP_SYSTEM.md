# Claude CI/CD Skip System

This repository uses a secure skip system for Claude CI/CD workflows.

## How It Works

The system prevents accidental or unauthorized skipping of Claude CI/CD workflows through hash validation.

### Two Security Levels:

#### 1. Standard Mode (Content-based)
The `.skip` file must contain exactly the following text:
```
SKIP_CLAUDE_CI_APPROVED
```

**SHA256 Hash:** `80960e69edf8e0868c81b3fa9eb415a5421d1e6ac6dc8e3abd640f3dd85c2f3c`

#### 2. Enhanced Mode (Secret-based)
Set a GitHub Secret named `SKIP_FILE_HASH` with any SHA256 hash. Only `.skip` files with this exact hash will be accepted.

## Usage

### Disable Claude CI/CD:

**Standard Mode:**
```bash
# Copy the example file
cp .skip.example .skip

# Or create the file manually
echo -n "SKIP_CLAUDE_CI_APPROVED" > .skip

# Commit and push
git add .skip
git commit -m "Disable Claude CI/CD temporarily"
git push
```

**Enhanced Mode (recommended for production):**
```bash
# 1. Create a .skip file with your own content
echo -n "MySecretSkipToken2024!" > .skip

# 2. Calculate the hash
sha256sum .skip | awk '{print $1}'
# Example output: abc123def456...

# 3. Add the secret to GitHub:
#    Settings > Secrets and variables > Actions > New repository secret
#    Name: SKIP_FILE_HASH
#    Value: abc123def456...

# 4. Commit and push
git add .skip
git commit -m "Disable Claude CI/CD with your own token"
git push
```

### Re-enable Claude CI/CD:

```bash
rm .skip
git add .skip
git commit -m "Re-enable Claude CI/CD"
git push
```

## Security Features

1. **Hash Validation**: Not every `.skip` file is accepted
2. **Fallback Logic**: If `.skip` file is invalid, CI/CD continues normally
3. **Audit Trail**: All skip attempts are documented in the workflow logs
4. **Flexibility**: Supports both simple and secret-based mode

## Affected Workflows

- `.github/workflows/claude.yml` (Issue/PR comments with @claude)
- `.github/workflows/claude-code-review.yml` (Automatic PR reviews)

## Workflow Outputs

- ✅ No .skip file found - proceeding with Claude CI/CD
- ⏭️ Valid .skip file found (content verified) - Claude CI/CD will be skipped
- ⏭️ Valid .skip file found (hash verified) - Claude CI/CD will be skipped
- ⚠️ .skip file found but invalid content - proceeding with Claude CI/CD for security
- ⚠️ .skip file found but hash mismatch - proceeding with Claude CI/CD for security

## Create Your Own Hash

```bash
# Create any text and calculate hash
echo -n "YourOwnText" | sha256sum | awk '{print $1}'

# Or use a random token
openssl rand -base64 32 | tee .skip | sha256sum | awk '{print $1}'
```
