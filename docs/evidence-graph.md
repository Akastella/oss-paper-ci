# Evidence Graph

The evidence graph is a directed graph that captures the relationships between
artifacts in a scientific paper repository. It answers questions like "which
script generated this figure?" and "which paper references this dataset?"

## Usage

```bash
# Markdown report (default)
oss-paper-ci graph /path/to/repo

# JSON output
oss-paper-ci graph /path/to/repo --format json

# Write to file
oss-paper-ci graph /path/to/repo --output graph-report.md
```

## Concepts

### Nodes

Every significant file in the repository becomes a **node** in the graph. Each
node has a **type** that describes its role:

| Type | Description | Example |
|------|-------------|---------|
| `tex` | LaTeX source file | `paper/main.tex` |
| `bib` | BibTeX bibliography | `paper/refs.bib` |
| `script` | Executable code | `scripts/train.py` |
| `config` | Configuration file | `config.yaml` |
| `environment` | Dependency declaration | `requirements.txt` |
| `data` | Dataset file | `data/train.csv` |
| `result` | Experiment output | `results/scores.json` |
| `figure` | Image or plot | `figures/loss_curve.png` |
| `table` | Table source | `tables/results.tex` |
| `notebook` | Jupyter notebook | `analysis.ipynb` |
| `readme` | Documentation | `README.md` |
| `ci` | CI configuration | `.github/workflows/ci.yml` |
| `contract` | Reproducibility contract | `reproducibility.yml` |

### Edges

Edges represent **directed relationships** between nodes:

| Relation | Meaning | Example |
|----------|---------|---------|
| `references` | One artifact mentions another | Paper includes a figure |
| `generates` | One artifact creates another | Script produces a plot |
| `requires` | One artifact depends on another | Script reads a dataset |
| `declares` | Contract declares an artifact | Contract lists a script |
| `documents` | Documentation describes an artifact | README explains a script |
| `validates` | One artifact validates another | CI runs a test |
| `runs` | Documentation or config invokes a script | README shows a command |
| `outputs` | An artifact is an output | Script outputs a result |

### Confidence

Each edge carries a **confidence** level:

- **explicit** -- the relationship is directly stated (e.g., `\includegraphics{...}` in LaTeX)
- **inferred** -- the relationship is guessed from naming conventions or heuristics

## How the Graph Is Built

The `build_evidence_graph` function performs the following analysis steps:

1. **File scanning** -- Walk the repository tree (respecting ignore patterns) and
   classify every file into a node type based on its extension and name.

2. **LaTeX parsing** -- Parse `.tex` files for `\includegraphics`, `\input`, and
   `\bibliography` commands. Create explicit `references` edges to the target
   figures, tables, and bibliography files.

3. **README command extraction** -- Find shell commands in README files that
   invoke scripts (e.g., `python scripts/train.py`). Create `runs` edges.

4. **Script I/O analysis** -- Scan Python scripts for `open()`, `read_csv()`,
   `savefig()`, and similar calls. Create `requires` or `generates` edges
   depending on whether the script reads or writes.

5. **Config reference scanning** -- Parse YAML/TOML config files for references
   to scripts and data paths. Create `runs` or `references` edges.

6. **Contract edge injection** -- If a reproducibility contract exists, add
   `declares` edges from the contract to all scripts, configs, and environment
   files it references.

7. **Heuristic generation edges** -- If a script name contains words like
   `plot`, `figure`, or `visual`, infer that it may generate figures. These
   edges are marked as `inferred`.

## Report Sections

The Markdown report answers six key questions:

### 1. Paper artifacts with code links

Which `.tex` files have connections to executable scripts? A paper with no code
links is a reproducibility risk.

### 2. Results with generation scripts

Which figures, tables, and result files have a known script that produces them?
Orphan results (no generation script) are flagged.

### 3. Scripts with undeclared environment dependencies

Which scripts lack an explicit link to an environment file (`requirements.txt`,
`environment.yml`, etc.)? These may have hidden dependencies.

### 4. Referenced data without availability

Which data files are referenced by scripts but do not exist on disk? These may
need to be downloaded or generated.

### 5. Orphan figures and tables

Which figures and tables are not referenced by any paper file? These may be
unused or the paper may be incomplete.

### 6. Expected outputs that are missing

When a script is expected to generate an output (via a `generates` edge) but
the output file does not exist, the experiment may not have been run.

## JSON Format

With `--format json`, the output is a JSON object:

```json
{
  "nodes": [
    {
      "id": "tex:paper/main.tex",
      "type": "tex",
      "path": "paper/main.tex",
      "label": "main.tex",
      "exists": true,
      "metadata": {}
    }
  ],
  "edges": [
    {
      "source": "tex:paper/main.tex",
      "target": "figure:figures/results.png",
      "relation": "references",
      "evidence": "\\includegraphics{../figures/results.png}",
      "confidence": "explicit"
    }
  ],
  "summary": {
    "total_nodes": 12,
    "total_edges": 8,
    "orphan_nodes": 2,
    "broken_edges": 0,
    "node_types": {"tex": 1, "script": 3, "figure": 1},
    "edge_relations": {"references": 3, "generates": 2, "requires": 3}
  }
}
```

## Programmatic Usage

```python
from oss_paper_ci.graph import build_evidence_graph
from oss_paper_ci.reporting.graph_report import generate_graph_markdown

graph = build_evidence_graph("/path/to/repo")

# Query the graph
orphans = graph.find_orphan_nodes()
broken = graph.find_broken_edges()

# Generate report
report = generate_graph_markdown(graph)
print(report)
```

## Limitations

- LaTeX parsing uses regex, not a full parser. Complex macro usage may be missed.
- Script I/O analysis is heuristic. Dynamic file paths (e.g., constructed at
  runtime) will not be detected.
- The graph only reflects files that exist on disk at scan time. Generated
  outputs from past runs are not tracked unless they are still present.
