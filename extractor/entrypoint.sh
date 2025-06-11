#!/bin/sh
set -e

# Inputs from GitHub Actions
MANIFEST_FILE="$INPUT_MANIFEST"
MANIFEST_TYPE="$INPUT_MANIFEST_TYPE"

if [ -z "$MANIFEST_FILE" ]; then
  echo "::error::Input 'manifest' is required"
  exit 1
fi

CMD="python -m extractor.cli $MANIFEST_FILE"
if [ ! -z "$MANIFEST_TYPE" ]; then
  CMD="$CMD --manifest-type $MANIFEST_TYPE"
fi

# Run the command and capture output
OUTPUT=$(eval $CMD)
echo "$OUTPUT"

# Set output for GitHub Actions
# Remove newlines for output variable
OUTPUT_CLEAN=$(echo "$OUTPUT" | tr '\n' ' ')
if [ -n "$GITHUB_OUTPUT" ]; then
  echo "output=$OUTPUT_CLEAN" >> $GITHUB_OUTPUT
fi