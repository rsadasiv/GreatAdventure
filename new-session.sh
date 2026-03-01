#!/usr/bin/env bash
# Create a new session file with today's date and a slug.

if [ -z "$1" ]; then
  echo "Usage: ./new-session.sh <slug>"
  exit 1
fi

DATE=$(date +%Y-%m-%d)
SLUG=$1
DIR="projects/sample-project/sessions"
mkdir -p "$DIR"
FILE="$DIR/${DATE}-${SLUG}.md"

if [ -f "$FILE" ]; then
  echo "File already exists: $FILE"
  exit 1
fi

cat > "$FILE" <<EOF
# Session: ${DATE} – ${SLUG}

## Aim

## Prompt used

\`\`\`prompt
\`\`\`

## Notes

## To Integrate

- [ ]
EOF

echo "Created $FILE"
