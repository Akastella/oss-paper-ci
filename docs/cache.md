# Incremental Cache

The cache avoids re-scanning projects that have not changed since the last scan.

## Usage

```bash
# Enable cache
oss-paper-ci batch scan --workspace oss-paper-ci-workspace.yml --cache

# View cache info
oss-paper-ci cache info --workspace oss-paper-ci-workspace.yml

# Clean cache
oss-paper-ci cache clean --workspace oss-paper-ci-workspace.yml
```

## Cache Key

A cache entry is keyed by the hash of:
- All files in the project directory
- Active policy profile
- Config file content
- Rule pack file contents
- oss-paper-ci version
- Cache schema version

## Invalidation

Cache is invalidated when:
- Any file in the project changes
- The profile changes
- The config file changes
- Any rule pack file changes
- oss-paper-ci version changes

## Storage

Cache files are stored in `.oss-paper-ci-cache/` in the workspace directory.
Each project gets its own JSON cache file.

## Corrupt Cache

If a cache file is corrupted or unreadable, it is treated as a cache miss.
The scan proceeds normally and the cache is rebuilt.

## Behavior

- Cache does not change scan results
- Cache is an optimization only
- Cache hit results are marked with `cache_hit: true` in the batch report
- Cache is disabled by default
- `.oss-paper-ci-cache/` is gitignored

## Notes

- Cache stores no absolute paths as keys
- Cache is local to the workspace directory
- Cache can be safely deleted at any time
