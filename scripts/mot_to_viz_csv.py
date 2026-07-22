"""Convert a BoT-SORT MOTChallenge results .txt into a CSV that
scripts/visualize_boxes.py can render, colored by the tracker's assigned ID.

demo.py writes each tracked box as:
    frame_id,track_id,x,y,w,h,score,-1,-1,-1
This emits: frame,x1,y1,x2,y2,tracker_id  (tlwh -> xyxy).

Then:
    python scripts/visualize_boxes.py --csv <out.csv> \
        --video ~/blindspot_data/S01/c001/vdo_trim.mp4 \
        --color-by tracker_id --out S01_c01_<variant>_trackerid.mp4

Coloring by tracker_id (NOT the ground-truth track_id) is what makes the
clean vs poisoned clips differ: the tracker associates on the poisoned
embeddings, so its assigned IDs fragment/switch under the attack.
"""

from __future__ import annotations

import argparse
import csv


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mot", required=True, help="BoT-SORT results .txt (frame,tid,x,y,w,h,...)")
    ap.add_argument("--out", required=True, help="Output CSV for visualize_boxes.py")
    args = ap.parse_args()

    rows_in = 0
    rows_out = 0
    with open(args.mot) as f, open(args.out, "w", newline="") as o:
        w = csv.writer(o)
        w.writerow(["frame", "x1", "y1", "x2", "y2", "tracker_id"])
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows_in += 1
            parts = line.split(",")
            if len(parts) < 6:
                continue
            frame, tid = parts[0], parts[1]
            x, y, ww, hh = (float(parts[2]), float(parts[3]), float(parts[4]), float(parts[5]))
            w.writerow([frame, int(round(x)), int(round(y)),
                        int(round(x + ww)), int(round(y + hh)), tid])
            rows_out += 1

    print(f"Read {rows_in} MOT rows, wrote {rows_out} boxes -> {args.out}")


if __name__ == "__main__":
    main()
