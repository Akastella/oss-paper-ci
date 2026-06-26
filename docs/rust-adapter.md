# Rust Adapter

The Rust adapter detects Rust projects and generates reproduction plans.

## Detection

Files detected:
- `Cargo.toml`, `Cargo.lock`
- `src/main.rs`, `src/bin/*.rs`, `src/lib.rs`

## Planning

Install steps:
- `Cargo.toml` → `cargo build --release`

Run steps:
- `cargo run --release`
- `cargo test`

## Runtime

Requires: `cargo`

Support level: **execute-if-runtime-present**

## Limitations

- Rust toolchain must be installed separately
- Compilation may take significant time
