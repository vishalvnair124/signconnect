import os
import shutil

# Base dataset directory
base_dir = r"D:\sign_dataset"
# Destination directory to copy files
destination_dir = r"D:\data_set"

os.makedirs(destination_dir, exist_ok=True)

# Walk through every folder
for root, dirs, files in os.walk(base_dir):
    # Filter only .mov files in the current folder
    mov_files = [f for f in files if f.lower().endswith(".mov")]

    if mov_files:  # If this folder has any .mov file
        # Get folder name
        folder_name = os.path.basename(root)

        # Clean folder name: "1. Hello" -> "Hello", "Ex. Monsoon" -> "Monsoon"
        if folder_name.lower().startswith("ex."):
            new_name = folder_name.split(maxsplit=1)[-1]
        elif ". " in folder_name or (folder_name and folder_name[0].isdigit()):
            new_name = folder_name.split(maxsplit=1)[-1]
        else:
            new_name = folder_name

        # Pick ONLY the first .mov file
        file_to_copy = mov_files[0]

        # Build source and destination paths
        source_file = os.path.join(root, file_to_copy)
        destination_file = os.path.join(destination_dir, f"{new_name}.mov")

        # Handle duplicate names by adding _1, _2, etc.
        counter = 1
        while os.path.exists(destination_file):
            name, ext = os.path.splitext(f"{new_name}.mov")
            destination_file = os.path.join(destination_dir, f"{name}_{counter}{ext}")
            counter += 1

        # Copy the file
        shutil.copy2(source_file, destination_file)
        print(f"Copied: {source_file} -> {destination_file}")
