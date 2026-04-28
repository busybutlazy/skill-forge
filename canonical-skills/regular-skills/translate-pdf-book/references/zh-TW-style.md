# Traditional Chinese Style Guide (zh-TW)

Style reference for translating technical books into Traditional Chinese suitable for Taiwan engineering readers.

## General Principles

- Write for a reader who can read English but prefers Chinese.
- Prefer natural phrasing over word-for-word translation.
- Match the register of the source: casual prose stays casual, technical prose stays precise.
- Aim for readability first; accuracy second only when they truly conflict.

## Terminology Decisions

**Keep in English when:**
- The English term is universally used in Taiwan engineering contexts (e.g., API, cache, pipeline, PR, merge)
- No natural Chinese equivalent exists or the Chinese term sounds awkward
- The term is a proper noun (product names, company names, tool names)

**Translate when:**
- A well-established Traditional Chinese equivalent exists and is widely used
- The source text is explaining a concept where the Chinese makes the meaning clearer

**Mixed form (preferred for technical jargon):**
- Introduce the Chinese translation on first use, then use whichever reads more naturally afterward
- Example: 職責範圍（scope）

## Sentence Structure

- Prefer shorter sentences over compound sentences with multiple clauses.
- Omit subject when it is clear from context — Chinese naturally does this.
- Avoid over-using 的 chains longer than three levels.
- Do not add 所 + verb constructions unless they appear in the source.

## Punctuation

- Use full-width punctuation: 。，：；！？「」『』（）
- Use 、for items in a list within a sentence.
- Use full-width space between Chinese and inline English/numbers: `設計 API 時` not `設計API時`.
- Do not put a space before 。or ，.

## Headings

- Chapter heading: `# 第 N 章：<title>`
- Section heading: `## <title>`
- Subsection: `### <title>`
- Capitalize the first letter of English words in headings.

## Numbers

- Use Arabic numerals for counts, measurements, and code values.
- Spell out ordinals in Chinese: 第一、第二 (not 第1、第2) in body prose.
- In headings use: `第 1 章` with a space before the numeral.

## Lists and Tables

- Use `- ` for unordered lists (same as English Markdown).
- Keep table headers in the same language as the surrounding prose or use bilingual headers when the column contains mixed-language data.

## Code and Technical Strings

- Never translate code blocks, command names, file paths, or environment variables.
- Inline code stays in backticks even when surrounded by Chinese text.
- Example: 執行 `pdftotext -layout book.pdf` 來提取文字。

## Figures and Images

- Write `（圖略）` where a figure appears in the source.
- If the caption is relevant, write: `（圖略：<brief Chinese description of what the figure shows>）`

## Common Mistranslation Traps

| Avoid | Prefer |
|-------|--------|
| 他/她 for generic third person | 他們 or restructure to avoid |
| 的確 (indeed) as filler | drop it or rephrase |
| 注意 as a heading | 注意事項 or 提醒 |
| 點擊 for UI actions | 按一下 or 點選 |
| 執行（execute）for running code | 執行 is fine; 跑 is too informal |
| 請注意… to open every paragraph | use sparingly |
