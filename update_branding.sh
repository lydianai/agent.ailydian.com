#!/bin/bash

# Script to update branding from "Lydian" to "MEDIAN AGENT" with "Lydian" subtitle
# across all HTML files

echo "🔄 Updating branding to MEDIAN AGENT..."
echo "=========================================="

cd /Users/lydian/Desktop/HealthCare-AI-Quantum-System/frontend

# Count files to update
total_files=$(find pages templates -name "*.html" -type f | wc -l | tr -d ' ')
echo "📁 Found $total_files HTML files to update"
echo

# Update patterns:
# 1. "LYDIAN MEDI" -> "MEDIAN AGENT"
# 2. "Lydian Agent" -> "MEDIAN AGENT"
# 3. "Lydian Healthcare AI" -> "MEDIAN AGENT"
# 4. Title tags
# 5. Meta descriptions

updated=0

for file in $(find pages templates -name "*.html" -type f); do
    if grep -q "LYDIAN MEDI\|Lydian Agent\|Lydian Healthcare" "$file" 2>/dev/null; then
        echo "  ✏️  Updating: $(basename $file)"

        # Create backup
        cp "$file" "$file.bak"

        # Replace logo text
        sed -i.tmp 's/LYDIAN MEDI/MEDIAN AGENT/g' "$file"
        sed -i.tmp 's/Lydian Agent/MEDIAN AGENT/g' "$file"
        sed -i.tmp 's/Lydian Healthcare AI/MEDIAN AGENT/g' "$file"
        sed -i.tmp 's/Lydian Healthcare/MEDIAN AGENT/g' "$file"

        # Clean up temp files
        rm -f "$file.tmp"

        ((updated++))
    fi
done

echo
echo "=========================================="
echo "✅ Updated $updated files"
echo "🎯 Branding changed to: MEDIAN AGENT"
echo
echo "Next steps:"
echo "1. Check a few files manually"
echo "2. Commit changes: git add . && git commit -m 'Rebrand to MEDIAN AGENT'"
echo "3. Deploy: vercel --prod"
