#!/bin/bash

# Function to generate MD5 checksum for a given file using openssl
generate_md5_checksum() {
    openssl md5 -binary "$1" | openssl base64
}

# Function to compare checksums of files in expected and observed directories
compare_checksums() {
    expected_dir="$1"
    observed_dir="$2"

    while IFS= read -r -d '' file_name; do
        expected_file_path="$file_name"
        # remove the expected_dir prefix from the file path
        file_name="${file_name#$expected_dir/}"
        observed_file_path="$observed_dir/$file_name"

        if [ -f "$expected_file_path" ] && [ -f "$observed_file_path" ]; then
            expected_checksum=$(generate_md5_checksum "$expected_file_path")
            observed_checksum=$(generate_md5_checksum "$observed_file_path")

            if [ "$expected_checksum" != "$observed_checksum" ]; then
                echo -e "\033[0;31mChecksum mismatch for file: $file_name\033[0m"
                echo "Expected: $expected_checksum"
                echo "Observed: $observed_checksum"
                exit 1
            else
                echo "Checksum matched for file: $file_name"
            fi
        else
            echo "File not found: $file_name at $expected_file_path or $observed_file_path"
            exit 1
        fi
    done < <(find "$expected_dir" -type f -print0)
}

compare_checksums "assets/test/output" "testing/output"
