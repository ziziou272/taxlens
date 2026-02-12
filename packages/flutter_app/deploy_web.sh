#!/bin/bash
set -e
cd "$(dirname "$0")"

echo "Building Flutter web..."
flutter build web --release --base-href "/taxlens/"

echo "Build complete. Output in build/web/"
echo "Deploy contents of build/web/ to ziziou.com/taxlens/"
