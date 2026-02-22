#!/bin/bash

# Update logo tagline from "AGENT" to "Lydian" subtitle
# across all HTML files

echo "🔄 Adding Lydian subtitle to logo..."
echo "=========================================="

cd /Users/lydian/Desktop/HealthCare-AI-Quantum-System/frontend

updated=0

for file in $(find pages templates -name "*.html" -type f); do
    if grep -q '<div class="logo-tagline">AGENT</div>' "$file" 2>/dev/null; then
        echo "  ✏️  Updating: $(basename $file)"

        # Replace AGENT with Lydian in logo-tagline
        sed -i.tmp 's/<div class="logo-tagline">AGENT<\/div>/<div class="logo-tagline">Lydian<\/div>/g' "$file"

        # Clean up temp files
        rm -f "$file.tmp"

        ((updated++))
    fi
done

echo
echo "=========================================="
echo "✅ Updated $updated files"
echo "🎯 Logo now shows: MEDIAN AGENT"
echo "              with: Lydian (subtitle)"
echo

