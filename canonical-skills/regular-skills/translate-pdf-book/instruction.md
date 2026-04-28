# Translate PDF Book

Use this skill to translate long PDF books or articles into Traditional Chinese Markdown while preserving quality across chapters.

## When to Use

Use this skill when you need to:
- Translate a PDF book or long article into Traditional Chinese (zh-TW)
- Extract text, split into chapters, maintain a consistent glossary, and produce per-chapter Markdown files
- Create a single merged Markdown output alongside per-chapter files
- Optionally parallelize chapter translation with subagents

Do not use this skill when:
- The PDF is scanned (image-only) without OCR capability — report the gap and stop
- The translation target is not Traditional Chinese
- The document is short enough to translate in one pass without chapter splitting

## Workflow

### 1. Inspect the PDF

- Confirm the file path exists.
- Determine whether it has extractable text or is image-scanned.
- Prefer local extraction tools: `pdftotext`, Python PDF libraries, or macOS Quartz.
- If the PDF is scanned and text extraction fails, report that OCR is required and stop.

### 2. Extract Source Text

- Write extracted text to a source file (e.g., `Book_Title.raw.txt`).
- Preserve `--- Page N ---` markers in the source file only.
- Do not carry PDF page headers, page numbers, or repeated book titles into the translated output.

### 3. Identify Structure

- Locate front matter, introduction, chapters, appendices, and index.
- Create `source_chapters/`.
- Write one English source slice per chapter:
  - `source_chapters/01_chapter_slug.en.txt`
  - `source_chapters/02_chapter_slug.en.txt`

### 4. Create Translation Workspace

- Create `translated/`.
- Create `translated/TERMS.md` before starting any translation.
  - Scan the source text for recurring domain-specific terms, names, and phrases.
  - Decide on a consistent zh-TW rendering for each one and record it.
  - `TERMS.md` is per-book: its entries depend on the subject matter of the book being translated, not on any fixed default list.
- Use Traditional Chinese (zh-TW) suitable for Taiwan engineering readers.

### 5. Translate Chapter by Chapter

- Create one Markdown file per chapter: `translated/01_chapter_slug.zh-TW.md`
- Start each chapter with `# 第 N 章：<title>`.
- Use `##` and `###` for internal headings.
- Skip images. If a figure or table position matters, write `（圖略）` at that location.
- Keep meaningful footnotes.
- Remove page headers, page numbers, repeated book titles, and extraction artifacts.

### 6. Parallelize with Subagents (Long Books)

- Assign each worker agent exactly one chapter with a disjoint write path.
- Tell workers they share the workspace and must not modify other files.
- Require each worker to read `translated/TERMS.md` before translating.
- After each worker returns, inspect its output before updating the index.

### 7. Create Index

- Write a root index file (e.g., `Book_Title_zh-TW.md`) linking all chapters in reading order.
- Mark unfinished chapters with `（待翻譯）` only while work is in progress.
- Remove all `待翻譯` markers before declaring the task complete.

### 8. Merge Final Output

- Keep the individual chapter files.
- Create one merged Markdown: `Book_Title_zh-TW_full.md`
- Concatenate files in reading order; add `\n\n---\n\n` separators between chapters.

### 9. Validate

- Check all expected files exist.
- Confirm heading order is consistent across chapters.
- Search for extraction leftovers: `--- Page`, repeated page headers, `待翻譯`.
- Confirm merged file line count is plausible relative to the source.
- Report final paths.

## Translation Rules

- Use Traditional Chinese (zh-TW).
- Prefer natural Taiwan technical-writing style over literal translation.
- Preserve common engineering terms when they are more readable in English.
- Keep names, book titles, company names, and product names in their original form unless a standard Chinese translation exists.
- Keep terminology consistent with `translated/TERMS.md`.
- Do not translate indexes unless explicitly requested.
- Do not translate image contents unless explicitly requested.

## Glossary Format

`translated/TERMS.md` is a per-book file. Its entries must reflect the domain and vocabulary of the specific book being translated — there is no fixed default list.

Use this format:

```markdown
# Terms

| English | zh-TW | Notes |
|---------|-------|-------|
| <term>  | <translation> | <optional context> |
```

**Example entries** (from a software career book — for illustration only):

| English | zh-TW | Notes |
|---------|-------|-------|
| staff engineer | Staff Engineer | proper noun; keep in English |
| individual contributor | 個人貢獻者 | |
| career ladder | 職涯階梯 | |
| scope | 職責範圍 | 視語境可譯為影響範圍 |
| trade-off | 取捨 | |
| incident | incident | 必要時譯為事故 |

Populate the actual glossary by reading the source text first, not by copying these examples.

## Output Layout

```text
.
├── Book_Title.pdf
├── Book_Title_zh-TW.md           ← root index
├── Book_Title_zh-TW_full.md      ← merged full output
├── source_chapters/
│   ├── 01_chapter_slug.en.txt
│   └── ...
└── translated/
    ├── TERMS.md
    ├── 00_front_matter.zh-TW.md
    ├── 00_introduction.zh-TW.md
    ├── 01_chapter_slug.zh-TW.md
    └── ...
```

## Completion Report

At the end of the task, report:
- Root index file path
- Merged full Markdown path
- Chapter directory path
- Source chapter directory path
- Validation checks performed
- Anything not translated (images, index, appendices)
