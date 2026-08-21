# AGENTS.md

## Scope
This repository hosts approved companion material for the book *Business Analytics and Artificial Intelligence: An Advanced Guide to Data-Driven Decision Making*.

## Governing rules

- Preserve companion-material IP restrictions and repository documentation.
- Keep notebook paths stable for external Colab links.
- Use synthetic or lawfully licensed data only.
- Never add credentials, tokens, or private datasets.
- Do not commit executed notebook outputs or execution counts.
- Preserve substantive educational content and sequencing in notebooks.

## Validation

Run the repository validation and follow repository branch/pull-request workflow.

```bash
python scripts/validate_notebooks.py

# Execute only notebooks that are explicitly safe for this environment (do not overwrite source notebooks)
# Example:
python -m nbconvert --to notebook --execute notebooks/Ch04_Gradient_Descent.ipynb --output-dir /tmp/baai-exec --output Ch04_Gradient_Descent.executed.ipynb --ExecutePreprocessor.timeout=300
```

## Operational guidance

- Preserve stable notebook paths under `notebooks/` and `appendices/`.
- Update README and Colab links when adding or renaming notebooks.
- Execute only lightweight, self-contained notebooks in this environment; document any skipped notebooks and reasons.
- Stop and report missing source notebooks rather than fabricating files.
- Keep manuscript, publisher, and model-weight materials out of this repository.
- Work through a branch and pull request.
