# Quality checklist

Accept an output only when every required gate passes.

## Exact-copy gate

- The visible title matches the requested title character for character.
- The visible title belongs to the title in this file's name and manifest entry; compare all three directly. Do not infer image content from filenames, task IDs, source paths, generation order, or neighboring covers.
- In a batch, compare each cover against other selected titles and verify no artwork/title pair has been swapped, especially when titles share words or cover the same topic.
- Punctuation is present unless omission was explicitly allowed.
- `REITs` and other permitted Latin text retain exact capitalization and spacing.
- Across all requested ratios for one title, exactly the recorded `highlight_text` characters use the accent color; no neighboring characters are included or omitted.
- No extra words, digits, labels, fake text or watermark appear anywhere.

## Identity gate

- The presenter is the same person as `assets/presenter-identity-original.png`.
- Face shape, eyes, glasses, haircut and professional appearance remain recognizable.
- No second person, extra limbs or broken hands are visible.
- The face is unobstructed and not crowded by title or props.

## Composition gate

- The title is the first visual focus and is readable at thumbnail size.
- The presenter is the second visual focus.
- Props remain secondary and do not cover the headline or face.
- Brown, mustard and cream dominate; torn paper and halftone texture are evident.
- The cover is one complete image, not a grid or multi-cover collection.
- Safe margins remain around critical text and face.

## Technical gate

- 9:16 output is PNG at exactly 1080×1920.
- 4:3 output is PNG at exactly 1440×1080.
- 16:9 output is PNG at exactly 1920×1080.
- Filename is the original title plus one space and `9-16`, `4-3` or `16-9`.
- Chinese comma `，` remains a comma in the filename; never convert it to `-`.
- The file opens successfully and is not empty.
- Check the final normalized file visually again. Wrong-orientation source mappings must be rejected, not aggressively center-cropped. Structural/CRC/hash checks do not replace visual word/identity review.
- Do not mark a file accepted until the final normalized PNG itself has been opened and its visible title, intended title, ratio, and filename have all been matched. Recheck this after replacing any previously accepted file; the old acceptance/hash is no longer valid.

## Retry policy

Retry only the failed image. Keep accepted images unchanged.

- Wrong character: repeat the exact title twice in the prompt, specify the failing character, simplify the background behind the title and keep the same composition references.
- Extra text: remove any prop that resembles paper, signage, screen content, chart labels or newspaper print; restate the absolute text exclusion.
- Identity drift: place the presenter source second and explicitly say to preserve face, glasses, haircut, suit, tie and pose.
- Crowded layout: reduce prop count to three and reserve the ratio-specific title zone before placing the presenter.
- After two failed one-pass attempts, report the remaining copy defect instead of silently compositing text in a second pass.
