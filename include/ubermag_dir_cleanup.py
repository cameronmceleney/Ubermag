# -*- coding: utf-8 -*-

# -------------------------- Preprocessing Directives -------------------------

# Standard Libraries
import os as os
import re
from sys import exit

# 3rd Party packages
from datetime import datetime

# import matplotlib.pyplot as plt
# import numpy as np

# My packages/Header files
# Here

# ----------------------------- Program Information ----------------------------

"""
Description of what foo.py does
"""
PROGRAM_NAME = "foo.py"
"""
Created on (date) by (author)
"""

__all__ = [
    "get_valid_input",
    "process_drive_dir",
    "natural_sort_key",
    "main"
]


def get_valid_input(prompt, valid_options):
    """
    Repeatedly prompt the user until a valid option is entered.
    valid_options should be a list of acceptable lowercase responses.
    """
    while True:
        response = input(prompt).strip().lower()
        if response in valid_options:
            return response
        print(f"Invalid input. Please enter one of: {', '.join(valid_options)}.")


def process_drive_dir(directory, save_spacing, batch_mode=False):
    """
    Process a single drive directory by scanning for files matching the pattern:
    dmi_with_anisotropy-Oxs_TimeDriver-Magnetization-#########-@@@@@@@.omf

    - Files with sequence number 0 or where (seq + 1) is a multiple of save_spacing are kept.
    - Others are marked for deletion.

    In normal mode, the user is prompted to print the deletion list and confirm deletion.
    In batch_mode, deletion confirmation is skipped.
    """
    pattern = re.compile(
        r"^dmi_paper-Oxs_TimeDriver-Magnetization-(\d{9})-(\d{7})\.omf$"
    )
    delete_list = []
    keep_list = []

    for filename in os.listdir(directory):
        match = pattern.match(filename)
        if match:
            seq = int(match.group(1))
            if seq == 0 or (seq + 1) % save_spacing == 0:
                keep_list.append(filename)
            else:
                delete_list.append(filename)

    total_files = len(keep_list) + len(delete_list)
    print("\n----------------------------------------")
    print(f"Directory: {directory}")
    print(f"Total matching files found: {total_files}")
    print(f"Files marked for deletion: {len(delete_list)}")
    print("----------------------------------------\n")

    # If no files are marked for deletion, skip deletion prompts.
    if not delete_list:
        print("No files marked for deletion in this directory. Skipping deletion.\n")
        return

    if not batch_mode:
        show = get_valid_input("Print all file names marked for deletion? (yes/no): ", ["yes", "no"])
        if show == "yes":
            print("\n".join(delete_list))
        confirm = get_valid_input("Delete these files? (yes/no): ", ["yes", "no"])
        if confirm != "yes":
            print("Deletion cancelled for this directory.\n")
            return

    # Batch mode or confirmed deletion: proceed to delete files.
    for f in delete_list:
        full_path = os.path.join(directory, f)
        try:
            os.remove(full_path)
        except Exception as e:
            print(f"Error deleting {full_path}: {e}")
    print("Deletion complete for this directory.\n")


def natural_sort_key(path):
    """
    Provides a natural sorting key based on the integer following 'drive-' in the directory name.
    """
    base = os.path.basename(path)
    m = re.match(r'^drive-(\d+)', base)
    if m:
        return int(m.group(1))
    return 0


def main():
    target_dir = input("Enter target directory: ").strip()
    if not os.path.isdir(target_dir):
        print("Provided target directory is not valid.")
        return

    # Determine if the final directory is of the 'drive-...' format.
    base_name = os.path.basename(target_dir.rstrip(os.sep))
    drive_pattern = re.compile(r'^drive-')
    batch_mode = False

    if drive_pattern.match(base_name):
        # Workflow Example 2: Final directory already in drive format.
        try:
            save_spacing = int(input("Enter save spacing (e.g., 500): ").strip())
        except ValueError:
            print("Invalid spacing value. Exiting.")
            return
        # No batch_mode confirmation needed here since yes-to-all is not an option.
        process_drive_dir(target_dir, save_spacing, batch_mode)
    else:
        # Workflow Example 1: Look for candidate 'drive-...' subdirectories.
        candidate_dirs = []
        for name in os.listdir(target_dir):
            full_path = os.path.join(target_dir, name)
            if os.path.isdir(full_path) and drive_pattern.match(name):
                candidate_dirs.append(full_path)

        if not candidate_dirs:
            print("No candidate drive- directories found in the specified directory.")
            return

        # Sort candidate directories naturally (e.g., drive-0, drive-1, ...)
        candidate_dirs.sort(key=natural_sort_key)

        print("\nCandidate drive- directories found:")
        for cand in candidate_dirs:
            print(f"  - {os.path.basename(cand)}")
        print("")

        # Accept hidden input "yes-to-all" along with "yes" or "no"
        cand_input = get_valid_input(
            "Do you want to check all files in these candidate directories? (yes/no/yes-to-all): ",
            ["yes", "no", "yes-to-all"]
        )
        if cand_input == "no":
            print("Operation cancelled.")
            return
        elif cand_input == "yes-to-all":
            # Extra confirmation for batch deletion
            confirm_all = get_valid_input(
                "Are you really sure you want to delete all files without further confirmation? (yes/no): ",
                ["yes", "no"]
            )
            if confirm_all != "yes":
                print("Batch deletion cancelled. Reverting to manual confirmation mode.")
            else:
                batch_mode = True

        try:
            save_spacing = int(input("Enter save spacing (e.g., 500): ").strip())
        except ValueError:
            print("Invalid spacing value. Exiting.")
            return

        # If batch_mode is active, confirm the save_spacing value.
        if batch_mode:
            print(f"\n[Confirmation] You have entered a save spacing value of: {save_spacing}")
            confirm_spacing = get_valid_input("Is this correct? (yes/no): ", ["yes", "no"])
            if confirm_spacing != "yes":
                print("Save spacing not confirmed. Exiting to avoid mass deletion.")
                return

        # Process each candidate directory.
        for cand in candidate_dirs:
            process_drive_dir(cand, save_spacing, batch_mode)


if __name__ == '__main__':
    main()
