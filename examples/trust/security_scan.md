# Security Scan Report

**Files Scanned:** 3

## Findings

### 1. Generic API Key

- **ID:** generic-api-key
- **Severity:** medium
- **Category:** secret
- **Path:** `.env`
- **Line:** 4
- **Message:** Possible Generic API Key detected.
- **Preview:** `API_...7890`
- **Recommendation:** Remove secret from code. Use environment variables or a secrets manager.

### 2. OpenAI API Key

- **ID:** openai-api-key
- **Severity:** high
- **Category:** secret
- **Path:** `config.py`
- **Line:** 4
- **Message:** Possible OpenAI API Key detected.
- **Preview:** `sk-a...2345`
- **Recommendation:** Remove secret from code. Use environment variables or a secrets manager.

### 3. AWS Access Key ID

- **ID:** aws-access-key
- **Severity:** high
- **Category:** secret
- **Path:** `config.py`
- **Line:** 6
- **Message:** Possible AWS Access Key ID detected.
- **Preview:** `AKIA...MPLE`
- **Recommendation:** Remove secret from code. Use environment variables or a secrets manager.

### 4. Private Key Block

- **ID:** private-key-block
- **Severity:** high
- **Category:** secret
- **Path:** `config.py`
- **Line:** 10
- **Message:** Possible Private Key Block detected.
- **Preview:** `----...----`
- **Recommendation:** Remove secret from code. Use environment variables or a secrets manager.

### 5. Generic API Key

- **ID:** generic-api-key
- **Severity:** medium
- **Category:** secret
- **Path:** `config.py`
- **Line:** 4
- **Message:** Possible Generic API Key detected.
- **Preview:** `API_...2345`
- **Recommendation:** Remove secret from code. Use environment variables or a secrets manager.

### 6. Curl pipe to shell

- **ID:** curl-pipe-bash
- **Severity:** high
- **Category:** execution
- **Path:** `config.py`
- **Line:** 17
- **Message:** Dangerous shell pattern detected: curl https://example.com/install.sh | bash
- **Recommendation:** Download scripts first, review, then execute.

### 7. Environment file committed

- **ID:** env-file-committed
- **Severity:** medium
- **Category:** secret
- **Path:** `.env`
- **Message:** File '.env' appears to be an environment file. It may contain secrets.
- **Recommendation:** Add .env files to .gitignore and remove from history if secrets were committed.

## Limitations

- Pattern-based detection; may produce false positives.
- Does not scan binary files or archives.
- Secret detection is heuristic; not all secret types are covered.
- Does not execute code; static analysis only.
