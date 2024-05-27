from bs4 import BeautifulSoup
import shutil
import re
import os
import zipfile


# This is the 3rd version of the renaming function. This file needs to be in the same folder
# as the relevant zip files. The zip files are extracted, and moved to a folder named after the course
# (this usually is not the most accurate). All videos are placed in the folder and named after the order in which
# they appear in the ToC. Beside the video, a rename_to_folder.py file is present, which renames each file to the foldername
# + original filename


def write_func(directory):
    func = """
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
"""

    with open(os.path.join(directory, "rename_to_folder.py"), "x") as file:
        file.write(func)


def extract_zip_files(directory):
    paths = []
    for filename in os.listdir(directory):
        if filename.endswith(".zip") and "on-demand video library" in filename.lower():
            file_path = os.path.join(directory, filename)
            try:
                with zipfile.ZipFile(file_path, 'r') as zip_ref:
                    extract_path = os.path.splitext(file_path)[0]
                    zip_ref.extractall(extract_path)
                    paths.append(extract_path)
                    print(f"Extracted: {filename} into {extract_path}")
            except zipfile.BadZipFile:
                print(f"Error: The file {filename} is not a zip file or it is corrupted.")
    return paths


def fix_html(text):
    fixed = text.replace('.mp4" /', '.mp4"')
    return fixed


def format_filename(original_name):
    # find the match for number at the end of the original_name
    number = re.search(r"\d+/", original_name).group(0)

    # Assemble the new filename
    new_filename = f"{number[:-1]}.mp4"

    return new_filename

def move_files(file_dict, curr_dir):
    """
    Takes a dictionary with file paths as keys and original file names as values,
    reformats the file names, and renames the files.
    """

    for original_path, original_name in file_dict.items():
        # Reformat the file name
        new_name = format_filename(original_name)
        print(new_name)

        # Construct new path by joining new dir and new name
        new_path = os.path.join(curr_dir, new_name)

        # Copy the file to the new location
        try:
            shutil.move(os.path.join(curr_dir, original_path), new_path)
            print(f"Moved '{original_path}' to '{new_path}'")

        except Exception as e:
            print(f" '{original_path}' to '{new_path}': {e}")


# Delete second subfolder from list of paths (in this case should be the subfolder,
# after everything has been moved from it
def deleteFolder(path):
    shutil.rmtree(path)
    print(f"Removed {path}")


def extract_links_from_html(file_path):
    # Open and read the HTML file
    with open(file_path, 'r') as file:
        html_content = file.read()
        html_content = fix_html(html_content)

    # Parse the HTML
    soup = BeautifulSoup(html_content, 'html', )

    a_tags = soup.find_all('a')
    # for anchor in a_tags:
    # print(anchor['href'], anchor.get_text())

    # Build the dictionary: {href: content}
    links_dict = {}
    for tag in a_tags:
        href = tag.get('href')
        content = tag.string
        if href:  # Ensure href is not None
            links_dict[href] = content
    return links_dict


def remove_leading_numbers(s):
    # This regex matches any sequence of digits at the beginning of the string,
    # possibly followed by punctuation like a dot, space, or dash.
    return re.sub(r'^\d+[\.\s\-]*', '', s)


def get_course_name(name):
    course_name = []
    # Splitting the original name into components
    parts = name.split(" - ")
    year_part = parts[-2].replace("'", " ").strip()  # Convert "Company'Year" to "Company Year"
    # Join the first two
    track_title = " ".join(parts[:(-2)]).replace(" - ", " ")
    track_title = remove_leading_numbers(track_title)
    topic_part = parts[-1]  # The last part is the course name
    # remove the numbers at the end
    topic_name = re.sub(r"\s\d+\/\d+$", '', topic_part)
    course_name = f"{year_part}_{track_title}_{topic_name}"

    return course_name


def deleteEmptyTrees(dir):
    import os
    import shutil

    # Get the current directory

    # Walk through each directory in the current directory
    for root, dirs, files in os.walk(dir, topdown=False):
        for name in dirs:
            dir_path = os.path.join(root, name)
            # Check if the directory is empty
            if not os.listdir(dir_path):
                # Delete the directory
                shutil.rmtree(dir_path)
                print(f"Deleted empty folder: {dir_path}")


def rename_folder(dir, new_name):
    # Construct the new directory path based on the new name
    # This assumes you want the new directory to be in the same parent directory as the current one
    parent_dir = os.path.dirname(dir)
    new_directory_path = os.path.join(parent_dir, new_name)

    # Check if a directory with the new name already exists
    if not os.path.exists(new_directory_path):
        # Rename the current directory
        os.rename(dir, new_directory_path)
        print(f"Directory renamed to: {new_directory_path}")
    else:
        print(f"A directory with the name '{new_name}' already exists.")


if __name__ == "__main__":
    # get current directory
    currentDir = os.getcwd()
    print(f"Current directory is {currentDir}")

    # Extract all On-Demand Video Library .zip files
    zipped_paths = extract_zip_files(currentDir)

    # Look through each folder of videos
    for root in zipped_paths:
        tocLink = os.path.join(root, "Table of Contents.html")
        toc = extract_links_from_html(tocLink)

        original_file_name = list(toc.values())[0]
        course_name = get_course_name(original_file_name)
        # Move all video files to new folder named after course
        move_files(toc, root)
        write_func(root)
        deleteEmptyTrees(root)
        os.remove(tocLink)
        rename_folder(root, course_name)
        print(f"Finished unpacking {course_name}")

