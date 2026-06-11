# Themes

OSS-Paper-CI supports terminal themes to customize the visual output.

## Available Themes

| Name | Description |
|------|-------------|
| `classic` | Default theme with balanced colors and symbols |
| `minimal` | Reduced decoration, suitable for CI logs |
| `contrast` | High contrast for accessibility |

## Usage

```bash
# List available themes
oss-paper-ci theme list

# Preview a theme
oss-paper-ci theme preview --theme minimal

# Use a theme with any command
oss-paper-ci workbench . --theme contrast
oss-paper-ci scan . --theme minimal --plain
```

## Theme Components

Each theme defines:

- **Status colors** — pass (green), fail (red), warn (yellow)
- **Status icons** — `[PASS]`, `[FAIL]`, `[WARN]`, `[SKIP]`
- **Structural styling** — titles, headings, borders
- **Score colors** — color thresholds for score display

## Customization

Themes are defined in `src/oss_paper_ci/themes.py`. To add a custom theme,
subclass `Theme` and register it in the `THEMES` dictionary.

## CI and Plain Mode

In CI environments, `--theme minimal` is recommended for clean log output.
Use `--plain` to disable all decoration for fully machine-readable output.
