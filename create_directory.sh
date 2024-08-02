#!/bin/bash

# Ensure script is run with root privileges
if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root" 
   exit 1
fi

# Ensure 'usnewsdevs' group exists
if ! getent group usnewsdevs > /dev/null; then
    echo "Group 'usnewsdevs' does not exist. Please create it first."
    exit 1
fi

# Ensure at least one path is provided
if [ $# -eq 0 ]; then
    echo "No paths provided. Please provide one or more paths."
    exit 1
fi

# Function to create shared directory
create_shared_directory() {
    local path=$1

    # Create the directory if it doesn't exist
    mkdir -p "$path"
    
    # Change group ownership to 'usnewsdevs'
    chown :usnewsdevs "$path"
    
    # Set permissions: read, write, and execute for the group
    chmod 2775 "$path"
    
    # Set default ACLs to ensure new files/directories inherit group permissions
    setfacl -d -m g::rwx "$path"
    setfacl -d -m o::rx "$path"

    echo "Shared directory created at: $path"
}

# Iterate through all provided paths and create shared directories
for path in "$@"; do
    create_shared_directory "$path"
done

echo "All specified directories have been configured."