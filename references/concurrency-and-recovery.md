# Adaptive generation and recovery

Only remote image-generation calls may overlap. Read sheet rows, choose titles, inspect images, normalize, validate, write the manifest, create Feishu folders, upload and verify in serial order.

## Choosing concurrency

Run `python3 scripts/preflight.py` immediately before dispatch. `auto` is the default. Use the script's recommendation, capped at four. If total/free memory or a clearly healthy OS pressure state cannot be reliably detected, if pressure is not green, if available memory is insufficient, or on systems with 8 GB total, use 1. At 12–23 GB use at most 2; 24–47 GB at most 3; 48 GB+ at most 4. A user may explicitly choose a lower cap. Begin with two independent generation jobs; increase only after they finish without pressure increase, timeouts or service errors, and only up to the detected recommendation. Recheck pressure after each batch. When pressure rises, stop dispatch, let active jobs finish, then continue at 1. If the image tool does not support reliable concurrent calls, use 1.

Each `title × ratio` is one independent image call and has a unique task ID, source filename, and temporary directory. Never share mutable paths between workers. Workers return only task ID, title, ratio, raw image path, and error; only the main task inspects outputs and changes `交付清单.json`. Do not load all full-size outputs at once.

Do not regenerate an accepted output when its recorded file hash still matches. Retry only the failed image. After HTTP 429 or `usage_limit_reached`, stop dispatch immediately and checkpoint without repeated retries. For an occasional timeout, wait, then retry that single image at most once. Preserve completed outputs and pending task records on interruption; resume only pending/failed work.

## Serial review and delivery

After generation results are collected, handle each image in order: full-size source visual inspection, `prepare_delivery.py`, final PNG visual inspection, `validate_cover.py`, then one manifest acceptance write. Acceptance must not overwrite an already accepted item; if its image changes, review it again. Feishu folder creation, each upload, receipt checkpoint, and post-upload listing are also serial. Keep final dimensions at exactly 1080×1920, 1440×1080 or 1920×1080 PNG; never trade resolution for speed.
