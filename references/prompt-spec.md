# Prompt specification

Use the templates below as strict production prompts. Replace bracketed fields; do not shorten the exclusions.

## Shared content contract

- Generate one complete standalone cover in one pass.
- For 9:16 and 16:9, use the matching ratio example as Image 1. For 4:3, use the 16:9 example as a style anchor and explicitly request a new 4:3 composition. Use the presenter source as Image 2, the original style reference as Image 3, and the detailed layout reference as Image 4.
- Preserve exact headline text. A visually omitted comma is permitted only when the user explicitly allows it; the filename must still retain the comma.
- Before generating any ratio, record one exact `highlight_text` substring per title. Insert the same substring in every ratio prompt as `[HIGHLIGHT_TEXT]`; color exactly those characters in the accent color and keep all other title characters in the normal title color. If no substring is selected, use no accent color on title text in any ratio.
- Keep all text complete, correctly shaped and legible. Show no other text.
- Do not automatically add a terminal question mark, punctuation or quotation marks absent from the exact title. Quote delimiters in the prompt are not printed characters.
- Select 3–6 topic-relevant props. Props must be unlabeled, secondary and outlined in white.
- Preserve the presenter identity exactly.

## 9:16 template

```text
Create ONE complete standalone 9:16 vertical Chinese finance-education video cover in a single image-generation pass. Do not make a grid, contact sheet, split screen, multi-poster composition, or blank background for later typography.

Use Image 1 as the exact series and vertical composition anchor. Use Image 2 as the identity anchor: preserve the same real Chinese male presenter, face, glasses, haircut, black suit, white shirt, striped tie, crossed-arm pose and professional identity. Use Images 3–4 only for the brown/yellow retro collage mood, torn-paper layering and bold headline treatment.

Exact headline text only:
“[EXACT_TITLE]”
Recommended line breaks: [LINE_BREAKS].
Highlight exactly “[HIGHLIGHT_TEXT]” in the accent color; no other title characters are accented. Keep this choice identical in all ratios.

Put the headline as the first visual focus in the upper 35–42%, using oversized bold Chinese display lettering on layered irregular mustard and cream torn-paper sticker cards. Put the presenter large in the lower-middle or lower-right with a thick clean white cutout outline. Keep the face clear and recognizable.

Visual style: low-saturation retro editorial collage; dominant dark brown, mustard yellow and warm cream; vintage halftone dots; tactile paper texture; clean bright hierarchy. Add only restrained topic props with white outlines: [TOPIC_PROPS]. Keep them secondary and away from the title and face.

All Chinese characters must be complete, clear, correctly shaped and easy to read. Do not rewrite, add, delete, substitute, duplicate or misspell any character. Absolute exclusions: no other Chinese or English words, subtitles, labels, tags, digits, clocks with numerals, prices, chart axes, tick marks, newspaper writing, fake microtext, logos, watermarks, UI icons, QR codes, decorative gibberish, second person, grid or border frame. Allow English only when it occurs in the exact title.
```

## 4:3 template

```text
Create ONE complete standalone 4:3 landscape Chinese finance-education video cover in a single image-generation pass. Do not crop a finished 16:9 cover, make a grid, contact sheet, split screen, multi-poster composition, or blank background for later typography.

Use Image 1 for the series style, but adapt the layout to a fresh 4:3 canvas. Use Image 2 as the identity anchor: preserve the same real Chinese male presenter, face, glasses, haircut, black suit, white shirt, striped tie, crossed-arm pose and professional identity. Use Images 3–4 only for the brown/yellow retro collage mood, torn-paper layering and bold headline treatment.

Exact headline text only:
“[EXACT_TITLE]”
Recommended line breaks: [LINE_BREAKS].
Highlight exactly “[HIGHLIGHT_TEXT]” in the accent color; no other title characters are accented. Keep this choice identical in all ratios.

Put the headline as the first visual focus on the LEFT 55–60%, using oversized bold Chinese display lettering on layered irregular mustard and cream torn-paper sticker cards. Put the presenter large on the RIGHT with a thick clean white cutout outline. Keep the full title and face inside safe margins.

Visual style: low-saturation retro editorial collage; dominant dark brown, mustard yellow and warm cream; vintage halftone dots; tactile paper texture; clean bright hierarchy. Add only restrained topic props with white outlines: [TOPIC_PROPS]. Keep them secondary and away from the title and face.

All Chinese characters must be complete, clear, correctly shaped and easy to read. Do not rewrite, add, delete, substitute, duplicate or misspell any character. Absolute exclusions: no other Chinese or English words, subtitles, labels, tags, digits, clocks with numerals, prices, chart axes, tick marks, newspaper writing, fake microtext, logos, watermarks, UI icons, QR codes, decorative gibberish, second person, grid or border frame. Allow English only when it occurs in the exact title.
```

## 16:9 template

```text
Create ONE complete standalone 16:9 horizontal Chinese finance-education video cover in a single image-generation pass. Do not make a grid, contact sheet, split screen, multi-poster composition, or blank background for later typography.

Use Image 1 as the exact series and horizontal composition anchor. Use Image 2 as the identity anchor: preserve the same real Chinese male presenter, face, glasses, haircut, black suit, white shirt, striped tie, crossed-arm pose and professional identity. Use Images 3–4 only for the brown/yellow retro collage mood, torn-paper layering and bold headline treatment.

Exact headline text only:
“[EXACT_TITLE]”
Recommended line breaks: [LINE_BREAKS].
Highlight exactly “[HIGHLIGHT_TEXT]” in the accent color; no other title characters are accented. Keep this choice identical in all ratios.

Put the headline as the first visual focus on the LEFT 58–62%, using oversized bold Chinese display lettering on layered irregular mustard and cream torn-paper sticker cards. Put the presenter large on the RIGHT 38–42% with a thick clean white cutout outline. Keep the face clear and recognizable.

Visual style: low-saturation retro editorial collage; dominant dark brown, mustard yellow and warm cream; vintage halftone dots; tactile paper texture; clean bright hierarchy. Add only restrained topic props with white outlines: [TOPIC_PROPS]. Keep them secondary and away from the title and face.

All Chinese characters must be complete, clear, correctly shaped and easy to read. Do not rewrite, add, delete, substitute, duplicate or misspell any character. Absolute exclusions: no other Chinese or English words, subtitles, labels, tags, digits, clocks with numerals, prices, chart axes, tick marks, newspaper writing, fake microtext, logos, watermarks, UI icons, QR codes, decorative gibberish, second person, grid or border frame. Allow English only when it occurs in the exact title.
```

## Line-breaking heuristics

- Break by semantic phrase, not by equal character count.
- Keep particles with their phrase; avoid leaving `的`, `了`, `吗`, `呢` alone.
- Use 2 lines for short titles, 3 for medium/long horizontal titles, and up to 4 for long vertical titles.
- Choose one exact phrase as the color accent for the title and use that same phrase across every ratio.

## Topic-prop mapping

- Real estate: houses, apartment towers, skyline, magnifying glass, key silhouette, unlabeled price curve.
- Asset allocation: coins, house, computer, unlabeled pie shape, magnifying glass, abstract allocation blocks.
- Insurance: shield silhouette, document shape without writing, umbrella, buildings, magnifying glass.
- Overseas investing: globe without labels, airplane, skyline, coins, magnifying glass, unlabeled curve.
- Retirement: modest house, suitcase, plant, coins, calm city skyline, abstract savings arrow.

Never use a prop if it introduces visible digits or text.
