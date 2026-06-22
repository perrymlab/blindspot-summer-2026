# Ground-truth cross-camera annotations

Human-annotated cross-camera vehicle identities from the multicam-reid toolkit
(https://github.com/figaone/multicam-reid). Each scenario folder contains:

```
<scenario>/
  matches.json          # global id -> {camera: local track id}
  tracks/
    c01.tracks.json     # per-camera boxes from annotation tracker
    c02.tracks.json
    c03.tracks.json
  sync.json             # frame offsets (only if sync step was run)
```

These files are created by: `bash scripts/save_annotations.sh <scenario>`
(use `all` to save every completed annotation at once)
after annotating with: `python -m multicam_reid match ~/annotation/<scenario>`

See docs/data/ANNOTATION_GUIDE.md for the full workflow.

## Status

| Scenario | Annotated | Matches | Committed |
|----------|-----------|---------|-----------|
| S07 | In progress | — | No |
| S14 | Pending | — | No |
| S15 | Pending | — | No |
