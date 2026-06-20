# Trust & Supply-Chain Security Report

**Repository:** `E:\Projects\OSS-Paper-CI`
**Schema Version:** 0.1

## Summary

| Severity | Count |
|----------|-------|
| High     | 71 |
| Medium   | 44 |
| Low      | 2 |

**Overall Status:** FAIL

## Findings

### 1. Curl pipe to shell

- **ID:** curl-pipe-bash
- **Severity:** high
- **Category:** execution
- **Path:** `.local_trust_security_taskboard_v2_9.md`
- **Line:** 17
- **Message:** Dangerous shell pattern detected: curl | bash
- **Recommendation:** Download scripts first, review, then execute.

### 2. Recursive force delete from root

- **ID:** rm-rf-root
- **Severity:** high
- **Category:** execution
- **Path:** `.local_trust_security_taskboard_v2_9.md`
- **Line:** 18
- **Message:** Dangerous shell pattern detected: rm -rf /
- **Recommendation:** Never delete from root. Use explicit paths.

### 3. Sudo usage

- **ID:** sudo-in-ci
- **Severity:** medium
- **Category:** execution
- **Path:** `.local_trust_security_taskboard_v2_9.md`
- **Line:** 18
- **Message:** Dangerous shell pattern detected: sudo
- **Recommendation:** Avoid sudo in CI; use containers or explicit permissions.

### 4. World-writable permissions

- **ID:** chmod-777
- **Severity:** medium
- **Category:** execution
- **Path:** `.local_trust_security_taskboard_v2_9.md`
- **Line:** 18
- **Message:** Dangerous shell pattern detected: chmod 777
- **Recommendation:** Use more restrictive permissions (e.g., 755 or 644).

### 5. Unsafe pickle load

- **ID:** unsafe-pickle
- **Severity:** high
- **Category:** execution
- **Path:** `.local_trust_security_taskboard_v2_9.md`
- **Line:** 20
- **Message:** Dangerous shell pattern detected: pickle.load
- **Recommendation:** Pickle can execute arbitrary code. Use safer formats like JSON.

### 6. Sudo usage

- **ID:** sudo-in-ci
- **Severity:** medium
- **Category:** execution
- **Path:** `CHANGELOG.md`
- **Line:** 13
- **Message:** Dangerous shell pattern detected: sudo
- **Recommendation:** Avoid sudo in CI; use containers or explicit permissions.

### 7. World-writable permissions

- **ID:** chmod-777
- **Severity:** medium
- **Category:** execution
- **Path:** `CHANGELOG.md`
- **Line:** 13
- **Message:** Dangerous shell pattern detected: chmod 777
- **Recommendation:** Use more restrictive permissions (e.g., 755 or 644).

### 8. Recursive force delete from root

- **ID:** rm-rf-root
- **Severity:** high
- **Category:** execution
- **Path:** `Dockerfile`
- **Line:** 14
- **Message:** Dangerous shell pattern detected: rm -rf /
- **Recommendation:** Never delete from root. Use explicit paths.

### 9. Sudo usage

- **ID:** sudo-in-ci
- **Severity:** medium
- **Category:** execution
- **Path:** `README.ja.md`
- **Line:** 104
- **Message:** Dangerous shell pattern detected: sudo
- **Recommendation:** Avoid sudo in CI; use containers or explicit permissions.

### 10. Sudo usage

- **ID:** sudo-in-ci
- **Severity:** medium
- **Category:** execution
- **Path:** `README.md`
- **Line:** 104
- **Message:** Dangerous shell pattern detected: sudo
- **Recommendation:** Avoid sudo in CI; use containers or explicit permissions.

### 11. Sudo usage

- **ID:** sudo-in-ci
- **Severity:** medium
- **Category:** execution
- **Path:** `README.zh-CN.md`
- **Line:** 104
- **Message:** Dangerous shell pattern detected: sudo
- **Recommendation:** Avoid sudo in CI; use containers or explicit permissions.

### 12. Sudo usage

- **ID:** sudo-in-ci
- **Severity:** medium
- **Category:** execution
- **Path:** `dev-history/FINAL_DELIVERABLES_ROUND4.md`
- **Line:** 73
- **Message:** Dangerous shell pattern detected: sudo
- **Recommendation:** Avoid sudo in CI; use containers or explicit permissions.

### 13. Sudo usage

- **ID:** sudo-in-ci
- **Severity:** medium
- **Category:** execution
- **Path:** `dev-history/FINAL_DELIVERABLES_ROUND5.md`
- **Line:** 75
- **Message:** Dangerous shell pattern detected: sudo
- **Recommendation:** Avoid sudo in CI; use containers or explicit permissions.

### 14. Sudo usage

- **ID:** sudo-in-ci
- **Severity:** medium
- **Category:** execution
- **Path:** `docs/checks.md`
- **Line:** 195
- **Message:** Dangerous shell pattern detected: sudo
- **Recommendation:** Avoid sudo in CI; use containers or explicit permissions.

### 15. Recursive force delete from root

- **ID:** rm-rf-root
- **Severity:** high
- **Category:** execution
- **Path:** `docs/reproduce-security.md`
- **Line:** 54
- **Message:** Dangerous shell pattern detected: rm -rf /
- **Recommendation:** Never delete from root. Use explicit paths.

### 16. Sudo usage

- **ID:** sudo-in-ci
- **Severity:** medium
- **Category:** execution
- **Path:** `docs/reproduce-security.md`
- **Line:** 55
- **Message:** Dangerous shell pattern detected: sudo
- **Recommendation:** Avoid sudo in CI; use containers or explicit permissions.

### 17. Sudo usage

- **ID:** sudo-in-ci
- **Severity:** medium
- **Category:** execution
- **Path:** `docs/reproduce.md`
- **Line:** 27
- **Message:** Dangerous shell pattern detected: sudo
- **Recommendation:** Avoid sudo in CI; use containers or explicit permissions.

### 18. Curl pipe to shell

- **ID:** curl-pipe-bash
- **Severity:** high
- **Category:** execution
- **Path:** `docs/security-model.md`
- **Line:** 37
- **Message:** Dangerous shell pattern detected: curl | sh`, `wget | bash
- **Recommendation:** Download scripts first, review, then execute.

### 19. Wget pipe to shell

- **ID:** wget-pipe-sh
- **Severity:** high
- **Category:** execution
- **Path:** `docs/security-model.md`
- **Line:** 37
- **Message:** Dangerous shell pattern detected: wget | bash
- **Recommendation:** Download scripts first, review, then execute.

### 20. Recursive force delete from root

- **ID:** rm-rf-root
- **Severity:** high
- **Category:** execution
- **Path:** `docs/security-model.md`
- **Line:** 35
- **Message:** Dangerous shell pattern detected: rm -rf /
- **Recommendation:** Never delete from root. Use explicit paths.

### 21. Recursive force delete from root

- **ID:** rm-rf-root
- **Severity:** high
- **Category:** execution
- **Path:** `docs/security-model.md`
- **Line:** 35
- **Message:** Dangerous shell pattern detected: rm -rf /
- **Recommendation:** Never delete from root. Use explicit paths.

### 22. Sudo usage

- **ID:** sudo-in-ci
- **Severity:** medium
- **Category:** execution
- **Path:** `docs/security-model.md`
- **Line:** 36
- **Message:** Dangerous shell pattern detected: sudo
- **Recommendation:** Avoid sudo in CI; use containers or explicit permissions.

### 23. Generic Bearer Token

- **ID:** generic-bearer
- **Severity:** medium
- **Category:** secret
- **Path:** `docs/security-scan.md`
- **Line:** 24
- **Message:** Possible Generic Bearer Token detected.
- **Recommendation:** Remove secret from code. Use environment variables or a secrets manager.

### 24. Generic Bearer Token

- **ID:** generic-bearer
- **Severity:** medium
- **Category:** secret
- **Path:** `docs/security-scan.md`
- **Line:** 24
- **Message:** Possible Generic Bearer Token detected.
- **Recommendation:** Remove secret from code. Use environment variables or a secrets manager.

### 25. Curl pipe to shell

- **ID:** curl-pipe-bash
- **Severity:** high
- **Category:** execution
- **Path:** `docs/security-scan.md`
- **Line:** 31
- **Message:** Dangerous shell pattern detected: curl pipe to bash | High | `curl ... \| bash
- **Recommendation:** Download scripts first, review, then execute.

### 26. Wget pipe to shell

- **ID:** wget-pipe-sh
- **Severity:** high
- **Category:** execution
- **Path:** `docs/security-scan.md`
- **Line:** 32
- **Message:** Dangerous shell pattern detected: wget pipe to shell | High | `wget ... \| sh
- **Recommendation:** Download scripts first, review, then execute.

### 27. Recursive force delete from root

- **ID:** rm-rf-root
- **Severity:** high
- **Category:** execution
- **Path:** `docs/security-scan.md`
- **Line:** 33
- **Message:** Dangerous shell pattern detected: rm -rf /
- **Recommendation:** Never delete from root. Use explicit paths.

### 28. Sudo usage

- **ID:** sudo-in-ci
- **Severity:** medium
- **Category:** execution
- **Path:** `docs/security-scan.md`
- **Line:** 34
- **Message:** Dangerous shell pattern detected: Sudo
- **Recommendation:** Avoid sudo in CI; use containers or explicit permissions.

### 29. Sudo usage

- **ID:** sudo-in-ci
- **Severity:** medium
- **Category:** execution
- **Path:** `docs/security-scan.md`
- **Line:** 34
- **Message:** Dangerous shell pattern detected: sudo
- **Recommendation:** Avoid sudo in CI; use containers or explicit permissions.

### 30. World-writable permissions

- **ID:** chmod-777
- **Severity:** medium
- **Category:** execution
- **Path:** `docs/security-scan.md`
- **Line:** 35
- **Message:** Dangerous shell pattern detected: chmod 777
- **Recommendation:** Use more restrictive permissions (e.g., 755 or 644).

### 31. Eval with variable

- **ID:** eval-variable
- **Severity:** high
- **Category:** execution
- **Path:** `docs/security-scan.md`
- **Line:** 36
- **Message:** Dangerous shell pattern detected: eval $
- **Recommendation:** Avoid eval with variables; use arrays or functions.

### 32. Unsafe pickle load

- **ID:** unsafe-pickle
- **Severity:** high
- **Category:** execution
- **Path:** `docs/security-scan.md`
- **Line:** 37
- **Message:** Dangerous shell pattern detected: pickle.load
- **Recommendation:** Pickle can execute arbitrary code. Use safer formats like JSON.

### 33. Curl pipe to shell

- **ID:** curl-pipe-bash
- **Severity:** high
- **Category:** execution
- **Path:** `docs/smoke-runs.md`
- **Line:** 62
- **Message:** Dangerous shell pattern detected: curl | sh
- **Recommendation:** Download scripts first, review, then execute.

### 34. Recursive force delete from root

- **ID:** rm-rf-root
- **Severity:** high
- **Category:** execution
- **Path:** `docs/smoke-runs.md`
- **Line:** 62
- **Message:** Dangerous shell pattern detected: rm -rf /
- **Recommendation:** Never delete from root. Use explicit paths.

### 35. Sudo usage

- **ID:** sudo-in-ci
- **Severity:** medium
- **Category:** execution
- **Path:** `docs/smoke-runs.md`
- **Line:** 62
- **Message:** Dangerous shell pattern detected: sudo
- **Recommendation:** Avoid sudo in CI; use containers or explicit permissions.

### 36. Sudo usage

- **ID:** sudo-in-ci
- **Severity:** medium
- **Category:** execution
- **Path:** `docs/supply-chain.md`
- **Line:** 28
- **Message:** Dangerous shell pattern detected: sudo
- **Recommendation:** Avoid sudo in CI; use containers or explicit permissions.

### 37. Curl pipe to shell

- **ID:** curl-pipe-bash
- **Severity:** high
- **Category:** execution
- **Path:** `docs/troubleshooting.md`
- **Line:** 37
- **Message:** Dangerous shell pattern detected: curl | sh`, `wget | sh
- **Recommendation:** Download scripts first, review, then execute.

### 38. Wget pipe to shell

- **ID:** wget-pipe-sh
- **Severity:** high
- **Category:** execution
- **Path:** `docs/troubleshooting.md`
- **Line:** 37
- **Message:** Dangerous shell pattern detected: wget | sh
- **Recommendation:** Download scripts first, review, then execute.

### 39. Sudo usage

- **ID:** sudo-in-ci
- **Severity:** medium
- **Category:** execution
- **Path:** `docs/troubleshooting.md`
- **Line:** 37
- **Message:** Dangerous shell pattern detected: sudo
- **Recommendation:** Avoid sudo in CI; use containers or explicit permissions.

### 40. Sudo usage

- **ID:** sudo-in-ci
- **Severity:** medium
- **Category:** execution
- **Path:** `docs/trust.md`
- **Line:** 30
- **Message:** Dangerous shell pattern detected: sudo
- **Recommendation:** Avoid sudo in CI; use containers or explicit permissions.

### 41. World-writable permissions

- **ID:** chmod-777
- **Severity:** medium
- **Category:** execution
- **Path:** `docs/trust.md`
- **Line:** 30
- **Message:** Dangerous shell pattern detected: chmod 777
- **Recommendation:** Use more restrictive permissions (e.g., 755 or 644).

### 42. Curl pipe to shell

- **ID:** curl-pipe-bash
- **Severity:** high
- **Category:** execution
- **Path:** `examples/evaluation-corpus/expected_outcomes.yml`
- **Line:** 157
- **Message:** Dangerous shell pattern detected: curl | bash
- **Recommendation:** Download scripts first, review, then execute.

### 43. Curl pipe to shell

- **ID:** curl-pipe-bash
- **Severity:** high
- **Category:** execution
- **Path:** `examples/evaluation-corpus/expected_outcomes.yml`
- **Line:** 161
- **Message:** Dangerous shell pattern detected: curl | bash
- **Recommendation:** Download scripts first, review, then execute.

### 44. Curl pipe to shell

- **ID:** curl-pipe-bash
- **Severity:** high
- **Category:** execution
- **Path:** `examples/evaluation-corpus/expected_outcomes.yml`
- **Line:** 165
- **Message:** Dangerous shell pattern detected: curl | bash
- **Recommendation:** Download scripts first, review, then execute.

### 45. Curl pipe to shell

- **ID:** curl-pipe-bash
- **Severity:** high
- **Category:** execution
- **Path:** `examples/evaluation-corpus/README.md`
- **Line:** 37
- **Message:** Dangerous shell pattern detected: curl | bash
- **Recommendation:** Download scripts first, review, then execute.

### 46. Curl pipe to shell

- **ID:** curl-pipe-bash
- **Severity:** high
- **Category:** execution
- **Path:** `examples/evaluation-corpus/unsafe_script_project/README.md`
- **Line:** 13
- **Message:** Dangerous shell pattern detected: curl | bash
- **Recommendation:** Download scripts first, review, then execute.

### 47. Curl pipe to shell

- **ID:** curl-pipe-bash
- **Severity:** high
- **Category:** execution
- **Path:** `examples/evaluation-corpus/unsafe_script_project/README.md`
- **Line:** 22
- **Message:** Dangerous shell pattern detected: curl | bash
- **Recommendation:** Download scripts first, review, then execute.

### 48. Curl pipe to shell

- **ID:** curl-pipe-bash
- **Severity:** high
- **Category:** execution
- **Path:** `examples/evaluation-corpus/unsafe_script_project/scripts/download_and_run.sh`
- **Line:** 6
- **Message:** Dangerous shell pattern detected: curl | bash
- **Recommendation:** Download scripts first, review, then execute.

### 49. Curl pipe to shell

- **ID:** curl-pipe-bash
- **Severity:** high
- **Category:** execution
- **Path:** `examples/evaluation-corpus/unsafe_script_project/scripts/download_and_run.sh`
- **Line:** 8
- **Message:** Dangerous shell pattern detected: curl -s https://example.com/install.sh | bash
- **Recommendation:** Download scripts first, review, then execute.

### 50. Wget pipe to shell

- **ID:** wget-pipe-sh
- **Severity:** high
- **Category:** execution
- **Path:** `examples/evaluation-corpus/unsafe_script_project/scripts/download_and_run.sh`
- **Line:** 11
- **Message:** Dangerous shell pattern detected: wget -qO- https://example.com/setup.sh | bash
- **Recommendation:** Download scripts first, review, then execute.

### 51. Curl pipe to shell

- **ID:** curl-pipe-bash
- **Severity:** high
- **Category:** execution
- **Path:** `examples/reports/evaluation_summary.json`
- **Line:** 8513
- **Message:** Dangerous shell pattern detected: curl | bash
- **Recommendation:** Download scripts first, review, then execute.

### 52. Curl pipe to shell

- **ID:** curl-pipe-bash
- **Severity:** high
- **Category:** execution
- **Path:** `examples/reports/evaluation_summary.json`
- **Line:** 8521
- **Message:** Dangerous shell pattern detected: curl | bash
- **Recommendation:** Download scripts first, review, then execute.

### 53. Curl pipe to shell

- **ID:** curl-pipe-bash
- **Severity:** high
- **Category:** execution
- **Path:** `examples/reports/evaluation_summary.json`
- **Line:** 8526
- **Message:** Dangerous shell pattern detected: curl | bash
- **Recommendation:** Download scripts first, review, then execute.

### 54. Recursive force delete from root

- **ID:** rm-rf-root
- **Severity:** high
- **Category:** execution
- **Path:** `examples/terminal/README.md`
- **Line:** 23
- **Message:** Dangerous shell pattern detected: rm -rf /
- **Recommendation:** Never delete from root. Use explicit paths.

### 55. Curl pipe to shell

- **ID:** curl-pipe-bash
- **Severity:** high
- **Category:** execution
- **Path:** `src/oss_paper_ci/runner.py`
- **Line:** 28
- **Message:** Dangerous shell pattern detected: curl | sh
- **Recommendation:** Download scripts first, review, then execute.

### 56. Curl pipe to shell

- **ID:** curl-pipe-bash
- **Severity:** high
- **Category:** execution
- **Path:** `src/oss_paper_ci/runner.py`
- **Line:** 29
- **Message:** Dangerous shell pattern detected: curl |bash
- **Recommendation:** Download scripts first, review, then execute.

### 57. Wget pipe to shell

- **ID:** wget-pipe-sh
- **Severity:** high
- **Category:** execution
- **Path:** `src/oss_paper_ci/runner.py`
- **Line:** 30
- **Message:** Dangerous shell pattern detected: wget | sh
- **Recommendation:** Download scripts first, review, then execute.

### 58. Wget pipe to shell

- **ID:** wget-pipe-sh
- **Severity:** high
- **Category:** execution
- **Path:** `src/oss_paper_ci/runner.py`
- **Line:** 31
- **Message:** Dangerous shell pattern detected: wget | bash
- **Recommendation:** Download scripts first, review, then execute.

### 59. Recursive force delete from root

- **ID:** rm-rf-root
- **Severity:** high
- **Category:** execution
- **Path:** `src/oss_paper_ci/runner.py`
- **Line:** 22
- **Message:** Dangerous shell pattern detected: rm -rf /
- **Recommendation:** Never delete from root. Use explicit paths.

### 60. Recursive force delete from root

- **ID:** rm-rf-root
- **Severity:** high
- **Category:** execution
- **Path:** `src/oss_paper_ci/runner.py`
- **Line:** 23
- **Message:** Dangerous shell pattern detected: rm -rf /
- **Recommendation:** Never delete from root. Use explicit paths.

### 61. Sudo usage

- **ID:** sudo-in-ci
- **Severity:** medium
- **Category:** execution
- **Path:** `src/oss_paper_ci/runner.py`
- **Line:** 26
- **Message:** Dangerous shell pattern detected: sudo
- **Recommendation:** Avoid sudo in CI; use containers or explicit permissions.

### 62. Generic Bearer Token

- **ID:** generic-bearer
- **Severity:** medium
- **Category:** secret
- **Path:** `src/oss_paper_ci/security.py`
- **Line:** 39
- **Message:** Possible Generic Bearer Token detected.
- **Recommendation:** Remove secret from code. Use environment variables or a secrets manager.

### 63. Sudo usage

- **ID:** sudo-in-ci
- **Severity:** medium
- **Category:** execution
- **Path:** `src/oss_paper_ci/security.py`
- **Line:** 74
- **Message:** Dangerous shell pattern detected: sudo
- **Recommendation:** Avoid sudo in CI; use containers or explicit permissions.

### 64. Sudo usage

- **ID:** sudo-in-ci
- **Severity:** medium
- **Category:** execution
- **Path:** `src/oss_paper_ci/security.py`
- **Line:** 76
- **Message:** Dangerous shell pattern detected: Sudo
- **Recommendation:** Avoid sudo in CI; use containers or explicit permissions.

### 65. Sudo usage

- **ID:** sudo-in-ci
- **Severity:** medium
- **Category:** execution
- **Path:** `src/oss_paper_ci/security.py`
- **Line:** 78
- **Message:** Dangerous shell pattern detected: sudo
- **Recommendation:** Avoid sudo in CI; use containers or explicit permissions.

### 66. Recursive force delete from root

- **ID:** rm-rf-root
- **Severity:** high
- **Category:** execution
- **Path:** `tests/test_reproduce_runner.py`
- **Line:** 162
- **Message:** Dangerous shell pattern detected: rm -rf /
- **Recommendation:** Never delete from root. Use explicit paths.

### 67. Sudo usage

- **ID:** sudo-in-ci
- **Severity:** medium
- **Category:** execution
- **Path:** `tests/test_reproduce_runner.py`
- **Line:** 162
- **Message:** Dangerous shell pattern detected: sudo
- **Recommendation:** Avoid sudo in CI; use containers or explicit permissions.

### 68. Curl pipe to shell

- **ID:** curl-pipe-bash
- **Severity:** high
- **Category:** execution
- **Path:** `tests/test_reproduce_security.py`
- **Line:** 28
- **Message:** Dangerous shell pattern detected: curl | sh
- **Recommendation:** Download scripts first, review, then execute.

### 69. Curl pipe to shell

- **ID:** curl-pipe-bash
- **Severity:** high
- **Category:** execution
- **Path:** `tests/test_reproduce_security.py`
- **Line:** 29
- **Message:** Dangerous shell pattern detected: curl | sh
- **Recommendation:** Download scripts first, review, then execute.

### 70. Recursive force delete from root

- **ID:** rm-rf-root
- **Severity:** high
- **Category:** execution
- **Path:** `tests/test_reproduce_security.py`
- **Line:** 22
- **Message:** Dangerous shell pattern detected: rm -rf /
- **Recommendation:** Never delete from root. Use explicit paths.

### 71. Recursive force delete from root

- **ID:** rm-rf-root
- **Severity:** high
- **Category:** execution
- **Path:** `tests/test_reproduce_security.py`
- **Line:** 69
- **Message:** Dangerous shell pattern detected: rm -rf /
- **Recommendation:** Never delete from root. Use explicit paths.

### 72. Recursive force delete from root

- **ID:** rm-rf-root
- **Severity:** high
- **Category:** execution
- **Path:** `tests/test_reproduce_security.py`
- **Line:** 81
- **Message:** Dangerous shell pattern detected: rm -rf /
- **Recommendation:** Never delete from root. Use explicit paths.

### 73. Recursive force delete from root

- **ID:** rm-rf-root
- **Severity:** high
- **Category:** execution
- **Path:** `tests/test_reproduce_security.py`
- **Line:** 89
- **Message:** Dangerous shell pattern detected: rm -rf /
- **Recommendation:** Never delete from root. Use explicit paths.

### 74. Sudo usage

- **ID:** sudo-in-ci
- **Severity:** medium
- **Category:** execution
- **Path:** `tests/test_reproduce_security.py`
- **Line:** 25
- **Message:** Dangerous shell pattern detected: sudo
- **Recommendation:** Avoid sudo in CI; use containers or explicit permissions.

### 75. Sudo usage

- **ID:** sudo-in-ci
- **Severity:** medium
- **Category:** execution
- **Path:** `tests/test_reproduce_security.py`
- **Line:** 69
- **Message:** Dangerous shell pattern detected: sudo
- **Recommendation:** Avoid sudo in CI; use containers or explicit permissions.

### 76. Sudo usage

- **ID:** sudo-in-ci
- **Severity:** medium
- **Category:** execution
- **Path:** `tests/test_reproduce_security.py`
- **Line:** 81
- **Message:** Dangerous shell pattern detected: sudo
- **Recommendation:** Avoid sudo in CI; use containers or explicit permissions.

### 77. Recursive force delete from root

- **ID:** rm-rf-root
- **Severity:** high
- **Category:** execution
- **Path:** `tests/test_round4_features.py`
- **Line:** 192
- **Message:** Dangerous shell pattern detected: rm -rf /
- **Recommendation:** Never delete from root. Use explicit paths.

### 78. OpenAI API Key

- **ID:** openai-api-key
- **Severity:** high
- **Category:** secret
- **Path:** `tests/test_secret_scan.py`
- **Line:** 13
- **Message:** Possible OpenAI API Key detected.
- **Recommendation:** Remove secret from code. Use environment variables or a secrets manager.

### 79. AWS Access Key ID

- **ID:** aws-access-key
- **Severity:** high
- **Category:** secret
- **Path:** `tests/test_secret_scan.py`
- **Line:** 29
- **Message:** Possible AWS Access Key ID detected.
- **Recommendation:** Remove secret from code. Use environment variables or a secrets manager.

### 80. Private Key Block

- **ID:** private-key-block
- **Severity:** high
- **Category:** secret
- **Path:** `tests/test_secret_scan.py`
- **Line:** 37
- **Message:** Possible Private Key Block detected.
- **Recommendation:** Remove secret from code. Use environment variables or a secrets manager.

### 81. Curl pipe to shell

- **ID:** curl-pipe-bash
- **Severity:** high
- **Category:** execution
- **Path:** `tests/test_secret_scan.py`
- **Line:** 45
- **Message:** Dangerous shell pattern detected: curl https://example.com/setup.sh | bash
- **Recommendation:** Download scripts first, review, then execute.

### 82. Sudo usage

- **ID:** sudo-in-ci
- **Severity:** medium
- **Category:** execution
- **Path:** `tests/test_secret_scan.py`
- **Line:** 51
- **Message:** Dangerous shell pattern detected: sudo
- **Recommendation:** Avoid sudo in CI; use containers or explicit permissions.

### 83. Sudo usage

- **ID:** sudo-in-ci
- **Severity:** medium
- **Category:** execution
- **Path:** `tests/test_secret_scan.py`
- **Line:** 55
- **Message:** Dangerous shell pattern detected: sudo
- **Recommendation:** Avoid sudo in CI; use containers or explicit permissions.

### 84. World-writable permissions

- **ID:** chmod-777
- **Severity:** medium
- **Category:** execution
- **Path:** `tests/test_secret_scan.py`
- **Line:** 59
- **Message:** Dangerous shell pattern detected: chmod 777
- **Recommendation:** Use more restrictive permissions (e.g., 755 or 644).

### 85. World-writable permissions

- **ID:** chmod-777
- **Severity:** medium
- **Category:** execution
- **Path:** `tests/test_secret_scan.py`
- **Line:** 61
- **Message:** Dangerous shell pattern detected: chmod 777
- **Recommendation:** Use more restrictive permissions (e.g., 755 or 644).

### 86. Eval with variable

- **ID:** eval-variable
- **Severity:** high
- **Category:** execution
- **Path:** `tests/test_secret_scan.py`
- **Line:** 69
- **Message:** Dangerous shell pattern detected: eval $
- **Recommendation:** Avoid eval with variables; use arrays or functions.

### 87. Unsafe pickle load

- **ID:** unsafe-pickle
- **Severity:** high
- **Category:** execution
- **Path:** `tests/test_secret_scan.py`
- **Line:** 75
- **Message:** Dangerous shell pattern detected: pickle.load
- **Recommendation:** Pickle can execute arbitrary code. Use safer formats like JSON.

### 88. Unsafe pickle load

- **ID:** unsafe-pickle
- **Severity:** high
- **Category:** execution
- **Path:** `tests/test_secret_scan.py`
- **Line:** 77
- **Message:** Dangerous shell pattern detected: pickle.load
- **Recommendation:** Pickle can execute arbitrary code. Use safer formats like JSON.

### 89. OpenAI API Key

- **ID:** openai-api-key
- **Severity:** high
- **Category:** secret
- **Path:** `tests/test_security_scan_cli.py`
- **Line:** 28
- **Message:** Possible OpenAI API Key detected.
- **Recommendation:** Remove secret from code. Use environment variables or a secrets manager.

### 90. Private Key Block

- **ID:** private-key-block
- **Severity:** high
- **Category:** secret
- **Path:** `tests/test_security_scan_cli.py`
- **Line:** 49
- **Message:** Possible Private Key Block detected.
- **Recommendation:** Remove secret from code. Use environment variables or a secrets manager.

### 91. Curl pipe to shell

- **ID:** curl-pipe-bash
- **Severity:** high
- **Category:** execution
- **Path:** `tests/test_security_scan_cli.py`
- **Line:** 83
- **Message:** Dangerous shell pattern detected: curl https://example.com/install.sh | bash
- **Recommendation:** Download scripts first, review, then execute.

### 92. Curl pipe to shell

- **ID:** curl-pipe-bash
- **Severity:** high
- **Category:** execution
- **Path:** `tests/test_smoke_security.py`
- **Line:** 23
- **Message:** Dangerous shell pattern detected: curl | sh
- **Recommendation:** Download scripts first, review, then execute.

### 93. Curl pipe to shell

- **ID:** curl-pipe-bash
- **Severity:** high
- **Category:** execution
- **Path:** `tests/test_smoke_security.py`
- **Line:** 27
- **Message:** Dangerous shell pattern detected: curl |bash
- **Recommendation:** Download scripts first, review, then execute.

### 94. Curl pipe to shell

- **ID:** curl-pipe-bash
- **Severity:** high
- **Category:** execution
- **Path:** `tests/test_smoke_security.py`
- **Line:** 64
- **Message:** Dangerous shell pattern detected: Curl | sh
- **Recommendation:** Download scripts first, review, then execute.

### 95. Wget pipe to shell

- **ID:** wget-pipe-sh
- **Severity:** high
- **Category:** execution
- **Path:** `tests/test_smoke_security.py`
- **Line:** 31
- **Message:** Dangerous shell pattern detected: wget | sh
- **Recommendation:** Download scripts first, review, then execute.

### 96. Wget pipe to shell

- **ID:** wget-pipe-sh
- **Severity:** high
- **Category:** execution
- **Path:** `tests/test_smoke_security.py`
- **Line:** 35
- **Message:** Dangerous shell pattern detected: wget | bash
- **Recommendation:** Download scripts first, review, then execute.

### 97. Recursive force delete from root

- **ID:** rm-rf-root
- **Severity:** high
- **Category:** execution
- **Path:** `tests/test_smoke_security.py`
- **Line:** 11
- **Message:** Dangerous shell pattern detected: rm -rf /
- **Recommendation:** Never delete from root. Use explicit paths.

### 98. Recursive force delete from root

- **ID:** rm-rf-root
- **Severity:** high
- **Category:** execution
- **Path:** `tests/test_smoke_security.py`
- **Line:** 15
- **Message:** Dangerous shell pattern detected: rm -rf /
- **Recommendation:** Never delete from root. Use explicit paths.

### 99. Recursive force delete from root

- **ID:** rm-rf-root
- **Severity:** high
- **Category:** execution
- **Path:** `tests/test_smoke_security.py`
- **Line:** 63
- **Message:** Dangerous shell pattern detected: rm -rf /
- **Recommendation:** Never delete from root. Use explicit paths.

### 100. Recursive force delete from root

- **ID:** rm-rf-root
- **Severity:** high
- **Category:** execution
- **Path:** `tests/test_smoke_security.py`
- **Line:** 151
- **Message:** Dangerous shell pattern detected: rm -rf /
- **Recommendation:** Never delete from root. Use explicit paths.

### 101. Sudo usage

- **ID:** sudo-in-ci
- **Severity:** medium
- **Category:** execution
- **Path:** `tests/test_smoke_security.py`
- **Line:** 19
- **Message:** Dangerous shell pattern detected: sudo
- **Recommendation:** Avoid sudo in CI; use containers or explicit permissions.

### 102. Sudo usage

- **ID:** sudo-in-ci
- **Severity:** medium
- **Category:** execution
- **Path:** `tests/test_smoke_security.py`
- **Line:** 63
- **Message:** Dangerous shell pattern detected: SUDO
- **Recommendation:** Avoid sudo in CI; use containers or explicit permissions.

### 103. Generic API Key

- **ID:** generic-api-key
- **Severity:** medium
- **Category:** secret
- **Path:** `tests/fixtures/security_secret_repo/.env`
- **Line:** 4
- **Message:** Possible Generic API Key detected.
- **Recommendation:** Remove secret from code. Use environment variables or a secrets manager.

### 104. OpenAI API Key

- **ID:** openai-api-key
- **Severity:** high
- **Category:** secret
- **Path:** `tests/fixtures/security_secret_repo/config.py`
- **Line:** 4
- **Message:** Possible OpenAI API Key detected.
- **Recommendation:** Remove secret from code. Use environment variables or a secrets manager.

### 105. AWS Access Key ID

- **ID:** aws-access-key
- **Severity:** high
- **Category:** secret
- **Path:** `tests/fixtures/security_secret_repo/config.py`
- **Line:** 6
- **Message:** Possible AWS Access Key ID detected.
- **Recommendation:** Remove secret from code. Use environment variables or a secrets manager.

### 106. Private Key Block

- **ID:** private-key-block
- **Severity:** high
- **Category:** secret
- **Path:** `tests/fixtures/security_secret_repo/config.py`
- **Line:** 10
- **Message:** Possible Private Key Block detected.
- **Recommendation:** Remove secret from code. Use environment variables or a secrets manager.

### 107. Generic API Key

- **ID:** generic-api-key
- **Severity:** medium
- **Category:** secret
- **Path:** `tests/fixtures/security_secret_repo/config.py`
- **Line:** 4
- **Message:** Possible Generic API Key detected.
- **Recommendation:** Remove secret from code. Use environment variables or a secrets manager.

### 108. Curl pipe to shell

- **ID:** curl-pipe-bash
- **Severity:** high
- **Category:** execution
- **Path:** `tests/fixtures/security_secret_repo/config.py`
- **Line:** 17
- **Message:** Dangerous shell pattern detected: curl https://example.com/install.sh | bash
- **Recommendation:** Download scripts first, review, then execute.

### 109. Curl pipe to shell

- **ID:** curl-pipe-bash
- **Severity:** high
- **Category:** execution
- **Path:** `tests/golden/evaluation_summary.json`
- **Line:** 8513
- **Message:** Dangerous shell pattern detected: curl | bash
- **Recommendation:** Download scripts first, review, then execute.

### 110. Curl pipe to shell

- **ID:** curl-pipe-bash
- **Severity:** high
- **Category:** execution
- **Path:** `tests/golden/evaluation_summary.json`
- **Line:** 8521
- **Message:** Dangerous shell pattern detected: curl | bash
- **Recommendation:** Download scripts first, review, then execute.

### 111. Curl pipe to shell

- **ID:** curl-pipe-bash
- **Severity:** high
- **Category:** execution
- **Path:** `tests/golden/evaluation_summary.json`
- **Line:** 8526
- **Message:** Dangerous shell pattern detected: curl | bash
- **Recommendation:** Download scripts first, review, then execute.

### 112. Environment file committed

- **ID:** env-file-committed
- **Severity:** medium
- **Category:** secret
- **Path:** `tests/fixtures/security_secret_repo/.env`
- **Message:** File '.env' appears to be an environment file. It may contain secrets.
- **Recommendation:** Add .env files to .gitignore and remove from history if secrets were committed.

### 113. Missing explicit permissions

- **ID:** workflow-missing-permissions
- **Severity:** medium
- **Category:** workflow
- **Path:** `.github/workflows/ci.yml`
- **Message:** Workflow does not declare explicit permissions. Default token permissions may be overly broad.
- **Recommendation:** Add 'permissions: contents: read' or more specific permissions.

### 114. High-risk trigger: workflow_dispatch

- **ID:** workflow-trigger-workflow_dispatch
- **Severity:** medium
- **Category:** workflow
- **Path:** `.github/workflows/docs.yml`
- **Message:** Workflow uses 'workflow_dispatch' which can be exploited if it checks out PR code.
- **Recommendation:** Avoid pull_request_target with PR code checkout. Use pull_request instead.

### 115. Third-party action: actions/upload-pages-artifact

- **ID:** workflow-third-party-action
- **Severity:** low
- **Category:** workflow
- **Path:** `.github/workflows/docs.yml`
- **Line:** 32
- **Message:** Action 'actions/upload-pages-artifact@v5' is not from a known official source and is not SHA-pinned.
- **Recommendation:** Pin third-party actions to SHA for supply-chain security.

### 116. Third-party action: actions/deploy-pages

- **ID:** workflow-third-party-action
- **Severity:** low
- **Category:** workflow
- **Path:** `.github/workflows/docs.yml`
- **Line:** 45
- **Message:** Action 'actions/deploy-pages@v5' is not from a known official source and is not SHA-pinned.
- **Recommendation:** Pin third-party actions to SHA for supply-chain security.

### 117. Missing explicit permissions

- **ID:** workflow-missing-permissions
- **Severity:** medium
- **Category:** workflow
- **Path:** `.github/workflows/install-smoke.yml`
- **Message:** Workflow does not declare explicit permissions. Default token permissions may be overly broad.
- **Recommendation:** Add 'permissions: contents: read' or more specific permissions.

## Limitations

- Local static analysis only; no runtime verification.
- No cryptographic signing or attestation.
- Secret detection uses pattern matching; may produce false positives/negatives.
- Workflow audit is static; does not verify runtime behavior.
- Dependency inventory is based on declared metadata, not resolved lockfiles.
- Provenance manifest is locally generated; not a signed SLSA attestation.
- Does not verify the integrity of third-party dependencies.
