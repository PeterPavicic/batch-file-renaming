import os
import re
# Get the current working directory
current_directory = os.getcwd()

# Get the parent directory name
directory_basename = os.path.basename(current_directory)

# List all files in the current directory
for filename in os.listdir(current_directory):
    # Check if the file is an .mp4 file
    if filename.endswith(".mp4"):
        # Construct the new filename
        filenum = re.search(r"[0-9]+\.mp4$", filename).group(0)
        new_filename = directory_basename + " " + filenum
        # Construct the full path for the old and new filenames
        old_file_path = os.path.join(current_directory, filename)
        new_file_path = os.path.join(current_directory, new_filename)
        # Rename the file
        os.rename(old_file_path, new_file_path)
        print(f"Renamed '{filename}' to '{new_filename}'")
