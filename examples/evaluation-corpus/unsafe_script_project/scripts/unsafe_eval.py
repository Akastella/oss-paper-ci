#!/usr/bin/env python3
"""Synthetic Python script for testing dry-run detection.

WARNING: This script contains risky patterns - DO NOT EXECUTE
This is a test fixture for oss-paper-ci evaluation.
"""

def process_input(user_input):
    """Process user input using eval - RISKY PATTERN."""
    # Risky pattern: eval() usage
    # This allows arbitrary code execution
    result = eval(user_input)
    return result

def run_command(command):
    """Execute a command using exec - RISKY PATTERN."""
    # Risky pattern: exec() usage
    exec(command)

def main():
    print("This script is for testing detection only.")
    print("It should NOT be executed.")
    # These lines demonstrate risky patterns:
    # eval("print('hello')")
    # exec("print('hello')")

if __name__ == "__main__":
    main()
