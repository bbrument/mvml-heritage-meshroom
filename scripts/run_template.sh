#!/usr/bin/env bash
# Create a Meshroom project from a template and an object folder of the dataset, then compute it, from the command
# line (no UI).
#
#   run_template.sh <template.mgt> <object folder> <project folder> [toNode]
#
# Example: run_template.sh templates/biface/biface_visart-eccv26.mgt /data/visart/biface /data/runs/biface
#
# Requires the Meshroom environment of docs/INSTALL.md (Meshroom on PYTHONPATH, AliceVision, plugins). MESHROOM_SRC
# is the Meshroom clone (default: found from the `meshroom` Python package).
# Options (environment variables):
#   GROUP_CAMERA_FALLBACK=global   one camera intrinsic for all the images, for images without a body serial number
#                                  (e.g. JPEG converted from the NEF; not needed on the NEF of the dataset), see B12
# Works around R3: meshroom_batch keeps only the last of several `-i` values, so all the image folders are passed as
# one comma-separated value.
set -eu
TPL=$(realpath "$1"); OBJ=$(realpath "$2"); OUT=$3; TO=${4:-}
MESHROOM_SRC=${MESHROOM_SRC:-$(python -c 'import meshroom, os; print(os.path.dirname(os.path.dirname(meshroom.__file__)))')}
mkdir -p "$OUT"; OUT=$(realpath "$OUT")
PROJECT=$OUT/project.mg

if [ ! -f "$PROJECT" ]; then
    T=$OUT/$(basename "$TPL")
    python - "$TPL" "$T" "${GROUP_CAMERA_FALLBACK:-}" <<'EOF'
import json, sys
src, dst, fallback = sys.argv[1:]
data = json.load(open(src))
if fallback:
    data["graph"]["CameraInit_1"]["inputs"]["groupCameraFallback"] = fallback
json.dump(data, open(dst, "w"), indent=4)
EOF
    # every folder holding images (MV/, PS/PS_xx/), as ONE comma-separated value (R3)
    FOLDERS=$(find "$OBJ" -type f \( -iname '*.nef' -o -iname '*.jpg' -o -iname '*.png' -o -iname '*.exr' \) \
              -printf '%h\n' | sort -u | paste -sd,)
    [ -n "$FOLDERS" ] || { echo "no image found in $OBJ"; exit 1; }
    python "$MESHROOM_SRC/bin/meshroom_batch" -i "$FOLDERS" -p "$T" --save "$PROJECT" --compute no > "$OUT/batch.log" 2>&1 \
        || { echo "meshroom_batch failed, see $OUT/batch.log"; tail -5 "$OUT/batch.log"; exit 1; }
fi
python - "$PROJECT" <<'EOF'
import json, sys
inputs = json.load(open(sys.argv[1]))["graph"]["CameraInit_1"]["inputs"]
print(f"{sys.argv[1]}: {len(inputs['viewpoints'])} images, {len(inputs['intrinsics'])} camera intrinsics")
EOF

# meshroom_compute needs an absolute path (B7)
python "$MESHROOM_SRC/bin/meshroom_compute" "$PROJECT" ${TO:+--toNode "$TO"} > "$OUT/run.log" 2>&1 && RC=0 || RC=$?
echo "meshroom_compute exit $RC, log $OUT/run.log"
grep -aE 'ERROR|Traceback' "$OUT/run.log" | head -5 || true
exit $RC
