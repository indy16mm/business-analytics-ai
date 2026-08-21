#!/usr/bin/env python3
"""Static validation for chapter and appendix notebooks.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Dict, List, Tuple

ROOT = Path(__file__).resolve().parents[1]

CHAPTER_RE = re.compile(r"^Ch\d{2}_[A-Za-z0-9_]+\.ipynb$", re.IGNORECASE)
APPENDIX_RE = re.compile(r"^Appendix_[A-Z]_[A-Za-z0-9_]+\.ipynb$")

FORBIDDEN_NAME = re.compile(r"(final|copy|\(\d+\)|\(\d+\))", re.IGNORECASE)
SECRET_PATTERNS = [
    re.compile(r"(?i)sk-[a-z0-9]{20,}"),
    re.compile(r"(?i)AKIA[0-9A-Z]{16}"),
    re.compile(r'(?i)(api[_-]?key|api[_-]?token|secret|password)\s*[:=]\s*["\'][^"\']{12,}["\']'),
]


def notebook_files() -> List[Path]:
    paths = []
    for folder in [ROOT / 'notebooks', ROOT / 'appendices']:
        if folder.is_dir():
            paths.extend(sorted(folder.glob('*.ipynb')))
    return paths


def check_filename(path: Path) -> List[str]:
    issues: List[str] = []
    name = path.name
    if '(' in name or ')' in name or ' ' in name:
        issues.append('unsafe filename characters')
    if 'final' in name.lower() or 'copy' in name.lower():
        issues.append('forbidden suffix text in filename')
    if 'duplicate-download' in name.lower() or '(1)' in name:
        issues.append('duplicate-download suffix detected')
    if not (CHAPTER_RE.match(name) or APPENDIX_RE.match(name)):
        issues.append('filename does not match chapter/appendix naming pattern')
    return issues


def check_notebook(path: Path) -> Tuple[bool, List[str], Dict[str, object]]:
    issues: List[str] = []
    metadata = {
        'path': str(path),
        'markdown_cells': 0,
        'code_cells': 0,
        'outputs_clean': True,
        'execution_counts_clean': True,
        'first_cell_is_markdown': False,
        'first_cell_identifies_notebook': False,
        'has_book_identification': False,
        'has_secret': False,
    }

    try:
        nb = json.loads(path.read_text(encoding='utf-8'))
    except json.JSONDecodeError as exc:
        issues.append(f'invalid JSON: {exc}')
        return False, issues, metadata

    cells = nb.get('cells')
    if not isinstance(cells, list):
        issues.append('missing or invalid notebook "cells" field')
        return False, issues, metadata

    if 'nbformat' not in nb or 'nbformat_minor' not in nb:
        issues.append('missing nbformat metadata fields')

    first_cell = cells[0] if cells else None
    if not first_cell or first_cell.get('cell_type') != 'markdown':
        issues.append('first cell is not markdown')
    else:
        metadata['first_cell_is_markdown'] = True
        txt = ''.join(first_cell.get('source', []))
        metadata['has_book_identification'] = 'Business Analytics and Artificial Intelligence' in txt
        if not metadata['has_book_identification']:
            issues.append('first markdown cell does not include book title')

        title_ok = False
        if path.parent.name == 'notebooks':
            title_ok = bool(re.search(r'#\s*Chapter\s+\d+\s+Companion Notebook', txt))
        elif path.parent.name == 'appendices':
            title_ok = bool(re.search(r'#\s*Appendix\s+[A-Z]\s+Companion Notebook', txt))
        metadata['first_cell_identifies_notebook'] = title_ok
        if not title_ok:
            issues.append('first markdown cell does not identify chapter/appendix pattern')

    text_for_scanning = ''

    for idx, cell in enumerate(cells):
        ctype = cell.get('cell_type')
        if ctype == 'markdown':
            if idx == 0:
                metadata['markdown_cells'] += 1
            else:
                metadata['markdown_cells'] += 1
            continue

        if ctype != 'code':
            continue

        metadata['code_cells'] += 1
        if cell.get('execution_count') is not None:
            metadata['execution_counts_clean'] = False
            issues.append(f'code cell #{idx} has non-null execution_count')

        outputs = cell.get('outputs')
        if outputs:
            metadata['outputs_clean'] = False
            issues.append(f'code cell #{idx} has stored outputs')
        text_for_scanning += '\n'.join(cell.get('source', []))

    if not text_for_scanning:
        # still scan markdown too for secret false positives
        for cell in cells:
            if cell.get('cell_type') == 'markdown':
                text_for_scanning += '\n'.join(cell.get('source', []))

    for pat in SECRET_PATTERNS:
        if pat.search(text_for_scanning):
            metadata['has_secret'] = True
            issues.append('likely embedded secret pattern detected')
            break

    metadata['filename_issues'] = check_filename(path)
    if metadata['filename_issues']:
        issues.extend(metadata['filename_issues'])

    return len(issues) == 0, issues, metadata


def main() -> int:
    files = notebook_files()
    total = len(files)
    failed = 0

    for path in files:
        ok, issues, meta = check_notebook(path)
        if ok:
            status = 'PASS'
        else:
            status = 'FAIL'
            failed += 1
        print(f'[{status}] {path}')
        print(f"  markdown_cells={meta['markdown_cells']} code_cells={meta['code_cells']} outputs_clean={meta['outputs_clean']} execution_counts_clean={meta['execution_counts_clean']} first_cell_markdown={meta['first_cell_is_markdown']} book_id={meta['has_book_identification']}")
        if issues:
            for issue in issues:
                print(f'  - {issue}')

    print(f'Validation summary: checked {total}, passed {total - failed}, failed {failed}')
    return 0 if failed == 0 else 1


if __name__ == '__main__':
    raise SystemExit(main())
