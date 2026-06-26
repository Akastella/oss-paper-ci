# R Adapter

The R adapter detects R projects and generates reproduction plans.

## Detection

Files detected:
- `DESCRIPTION`, `renv.lock`, `install.R`, `.Rprofile`, `NAMESPACE`
- `*.R`, `*.r`, `*.Rmd`, `*.rmd`, `*.qmd` scripts and notebooks

## Planning

Install steps:
- `renv.lock` → `Rscript -e 'renv::restore()'`
- `install.R` → `Rscript install.R`
- `DESCRIPTION` → `Rscript -e 'devtools::install_deps()'`

Run steps:
- `Rscript <script>` for R scripts
- `Rscript -e 'rmarkdown::render("<file>")'` for Rmd files

## Runtime

Requires: `Rscript`

Support level: **execute-if-runtime-present**

## Limitations

- R runtime must be installed separately
- renv restoration requires renv package
- Some R packages may require system libraries

## Safety

- `install.packages()` calls are flagged as warnings
