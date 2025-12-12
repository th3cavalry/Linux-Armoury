#!/bin/bash
set -e

# Script to prepare files for Flathub submission
# This script copies all necessary files to a submission directory

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
APP_ID="com.github.th3cavalry.linux-armoury"
SUBMISSION_DIR="${SCRIPT_DIR}/flathub-submission"

echo "=== Preparing Flathub Submission for Linux Armoury ==="
echo ""

# Clean and create submission directory
if [ -d "$SUBMISSION_DIR" ]; then
    echo "Removing existing submission directory..."
    rm -rf "$SUBMISSION_DIR"
fi

echo "Creating submission directory: $SUBMISSION_DIR"
mkdir -p "$SUBMISSION_DIR"

# Copy manifest
echo "Copying Flatpak manifest..."
cp "$SCRIPT_DIR/${APP_ID}.yml" "$SUBMISSION_DIR/"

# Copy desktop file
echo "Copying desktop file..."
cp "$SCRIPT_DIR/${APP_ID}.desktop" "$SUBMISSION_DIR/"

# Copy metainfo
echo "Copying metainfo file..."
cp "$SCRIPT_DIR/data/metainfo/${APP_ID}.metainfo.xml" "$SUBMISSION_DIR/"

# Copy icon
echo "Copying icon..."
cp "$SCRIPT_DIR/data/icons/${APP_ID}.svg" "$SUBMISSION_DIR/"

# Copy requirements
echo "Copying requirements.txt..."
cp "$SCRIPT_DIR/requirements.txt" "$SUBMISSION_DIR/"

# Copy vendored wheels if they exist
if [ -d "$SCRIPT_DIR/flatpak-wheels" ]; then
    echo "Copying vendored wheels..."
    cp -r "$SCRIPT_DIR/flatpak-wheels" "$SUBMISSION_DIR/"
fi

# Copy README for context
echo "Copying README..."
cp "$SCRIPT_DIR/README.md" "$SUBMISSION_DIR/"

# Copy LICENSE
echo "Copying LICENSE..."
cp "$SCRIPT_DIR/LICENSE" "$SUBMISSION_DIR/"

echo ""
echo "=== Validation ==="
echo ""

# Check if files exist
required_files=(
    "${APP_ID}.yml"
    "${APP_ID}.desktop"
    "${APP_ID}.metainfo.xml"
    "${APP_ID}.svg"
    "requirements.txt"
)

all_present=true
for file in "${required_files[@]}"; do
    if [ -f "$SUBMISSION_DIR/$file" ]; then
        echo "✓ $file"
    else
        echo "✗ $file - MISSING!"
        all_present=false
    fi
done

echo ""

if [ "$all_present" = true ]; then
    echo "✓ All required files are present"
else
    echo "✗ Some required files are missing!"
    exit 1
fi

# Create a tarball
echo ""
echo "Creating tarball..."
cd "$SCRIPT_DIR"
tar czf "flathub-submission.tar.gz" -C "$SUBMISSION_DIR" .
echo "✓ Created: flathub-submission.tar.gz"

echo ""
echo "=== Summary ==="
echo ""
echo "Submission files prepared in: $SUBMISSION_DIR"
echo "Tarball created: flathub-submission.tar.gz"
echo ""
echo "Next steps:"
echo "1. Review the submission guide: docs/FLATHUB_SUBMISSION.md"
echo "2. Test build locally: make flatpak-build"
echo "3. Fork https://github.com/flathub/flathub"
echo "4. Create submission branch from 'new-pr'"
echo "5. Copy files from $SUBMISSION_DIR to your fork"
echo "6. Submit pull request to Flathub"
echo ""
echo "For detailed instructions, see: docs/FLATHUB_SUBMISSION.md"
