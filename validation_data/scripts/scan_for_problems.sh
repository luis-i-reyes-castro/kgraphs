#!/bin/bash

JPG_DIR="/home/luis/DAL/JPG"

# First check if directory exists
if [ ! -d "$JPG_DIR" ]; then
    echo "Error: Directory $JPG_DIR does not exist!"
    exit 1
fi

# Check if directory is readable
if [ ! -r "$JPG_DIR" ]; then
    echo "Error: Cannot read directory $JPG_DIR!"
    exit 1
fi

echo "Scanning filenames in $JPG_DIR for potential issues..."
echo "=================================================="
echo

# Debug: Print number of files found
file_count=$(find "$JPG_DIR" -type f | wc -l)
echo "Found $file_count files in directory"
echo

# Initialize counters
total_files=0
problem_files=0

# Create a temporary file for results
temp_file=$(mktemp)

echo "Potential problematic files:" > "$temp_file"
echo "-------------------------" >> "$temp_file"

# Modified find command with error handling
while IFS= read -r file; do
    filename=$(basename "$file")
    ((total_files++))
    
    # Check for various potential issues
    if [[ "$filename" =~ [[:cntrl:]] ]]; then
        echo "Control characters found in: $filename" >> "$temp_file"
        ((problem_files++))
    fi
    
    if [[ "$filename" =~ [^[:ascii:]] ]]; then
        echo "Non-ASCII characters found in: $filename" >> "$temp_file"
        hex_name=$(echo "$filename" | xxd -p)
        echo "  Hex representation: $hex_name" >> "$temp_file"
        ((problem_files++))
    fi
    
    if [[ "$filename" =~ [\'\"\(\)\[\]\{\}\<\>\&\$\;\`] ]]; then
        echo "Special shell characters found in: $filename" >> "$temp_file"
        ((problem_files++))
    fi
    
    # Get file size
    size=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file")
    if (( size > 10485760 )); then  # larger than 10MB
        echo "Large file ($(( size / 1048576 ))MB): $filename" >> "$temp_file"
        ((problem_files++))
    fi
done < <(find "$JPG_DIR" -type f)

# Print results
echo "Summary:"
echo "--------"
echo "Total files scanned: $total_files"
echo "Potential problems found: $problem_files"
echo
cat "$temp_file"

# Clean up
rm "$temp_file"

# List the last 10 files alphabetically
echo
echo "Last 10 files alphabetically:"
echo "---------------------------"
ls -1 "$JPG_DIR" | sort | tail -n 10

# Additional check for the specific files that might be causing the hang
echo
echo "Details of the last few files:"
echo "----------------------------"
ls -la "$JPG_DIR" | sort | tail -n 5
