#!/bin/sh
# Usage: studio/preview.sh <motion> <camera> <t1,t2,t3,t4>   -> /tmp/gfprev/<motion>.png (frames side by side)
set -e
M=$1; C=$2; T=$3
D=/tmp/gfprev; mkdir -p $D
blender -b studio/character/instructor_mpfb.blend -P studio/render/preview.py -- $M $C $D/$M "$T" >/dev/null 2>&1
N=$(echo "$T" | tr ',' '\n' | wc -l | tr -d ' ')
IN=""; for i in $(seq 0 $((N-1))); do IN="$IN -i $D/${M}_$i.png"; done
ffmpeg -v error -y $IN -filter_complex "hstack=inputs=$N" $D/$M.png
echo $D/$M.png
