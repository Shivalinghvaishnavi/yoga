#!/bin/sh
# Usage: probe.sh VIDEO_ID...   Prints creator, title, length, embeddable flag and licence text for each.
for id in "$@"; do
  html=$(curl -sL -A "Mozilla/5.0" "https://www.youtube.com/watch?v=$id")
  oe=$(curl -s -o /dev/null -w "%{http_code}" "https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v=$id&format=json")
  title=$(printf '%s' "$html" | grep -o '<title>[^<]*' | head -1 | sed 's/<title>//')
  author=$(printf '%s' "$html" | grep -o '"author":"[^"]*"' | head -1)
  len=$(printf '%s' "$html" | grep -o '"lengthSeconds":"[0-9]*"' | head -1)
  emb=$(printf '%s' "$html" | grep -o '"playableInEmbed":[a-z]*' | head -1)
  cc=$(printf '%s' "$html" | grep -o 'Creative Commons[^"<]\{0,40\}' | head -1)
  echo "$id | oembed=$oe | $emb | $len | $author | cc=[${cc}] | $title"
done
