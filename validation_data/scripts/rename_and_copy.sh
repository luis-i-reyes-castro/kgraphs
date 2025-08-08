#!/bin/bash

# Source and destination directories
SOURCE_DIR="/home/luis/DAL/JPG"
DEST_DIR="/home/luis/DJI_AGRAS_LATINO/raw"

# Ensure the destination directory exists
mkdir -p "$DEST_DIR"

# Associative array to keep track of counts for each timestamp
declare -A timestamp_counts

# Loop through all JPG files in the source directory
for file in "$SOURCE_DIR"/*.jpg; do
    # Extract the base filename (without path)
    filename=$(basename "$file")

    # Use regex to extract the date and time components
    if [[ $filename =~ ([0-9]{4}-[0-9]{2}-[0-9]{2})\ ([0-9]{2})\ ([0-9]{2})\ ([0-9]{2}) ]]; then
        # Extract the matched groups
        date_part="${BASH_REMATCH[1]}"
        hour="${BASH_REMATCH[2]}"
        minute="${BASH_REMATCH[3]}"
        second="${BASH_REMATCH[4]}"

        # Construct the base new filename (without index)
        base_new_filename="${date_part}_${hour}-${minute}-${second}"

        # Initialize or increment the count for this timestamp
        if [[ -z "${timestamp_counts[$base_new_filename]}" ]]; then
            timestamp_counts[$base_new_filename]=0
        else
            timestamp_counts[$base_new_filename]=$((timestamp_counts[$base_new_filename] + 1))
        fi

        # Construct the full new filename with index
        new_filename="${base_new_filename}_i${timestamp_counts[$base_new_filename]}.jpg"

        # Copy the file to the destination directory with the new name
        cp "$file" "$DEST_DIR/$new_filename"

        echo "Copied and renamed: $filename -> $new_filename"
    else
        echo "Skipping file (does not match expected format): $filename"
    fi
done

echo "All files processed."
