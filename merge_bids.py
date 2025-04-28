#!/usr/bin/env python3
import os
import shutil
import argparse
import json
import logging
import pandas as pd
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Merge two BIDS directories")
    parser.add_argument("--source", required=True, help="Source BIDS directory")
    parser.add_argument("--destination", required=True, help="Destination BIDS directory")
    parser.add_argument("--conflict", choices=["skip", "overwrite", "rename"], default="skip",
                        help="How to handle conflicts: skip, overwrite, or rename files")
    parser.add_argument("--dry-run", action="store_true", help="Perform a dry run without copying files")
    return parser.parse_args()

def validate_bids_directory(bids_dir):
    """Check if the directory is a valid BIDS directory."""
    dataset_desc_path = os.path.join(bids_dir, "dataset_description.json")

    if not os.path.exists(dataset_desc_path):
        logger.error(f"Not a BIDS directory: {bids_dir} (missing dataset_description.json)")
        return False

    try:
        with open(dataset_desc_path, 'r') as f:
            dataset_desc = json.load(f)

        if "Name" not in dataset_desc or "BIDSVersion" not in dataset_desc:
            logger.error(f"Invalid dataset_description.json in {bids_dir}")
            return False

    except json.JSONDecodeError:
        logger.error(f"Invalid JSON in dataset_description.json in {bids_dir}")
        return False

    return True

def merge_dataset_description(source_dir, dest_dir):
    """Merge dataset_description.json files."""
    source_desc_path = os.path.join(source_dir, "dataset_description.json")
    dest_desc_path = os.path.join(dest_dir, "dataset_description.json")

    with open(source_desc_path, 'r') as f:
        source_desc = json.load(f)

    with open(dest_desc_path, 'r') as f:
        dest_desc = json.load(f)

    # Merge authors, acknowledgements, etc.
    if "Authors" in source_desc and "Authors" in dest_desc:
        combined_authors = list(set(source_desc["Authors"] + dest_desc["Authors"]))
        dest_desc["Authors"] = combined_authors

    if "Acknowledgements" in source_desc:
        dest_desc["Acknowledgements"] = dest_desc.get("Acknowledgements", "") + " " + source_desc.get("Acknowledgements", "")

    # Write merged description
    with open(dest_desc_path, 'w') as f:
        json.dump(dest_desc, f, indent=4)

    logger.info("Merged dataset descriptions")

def copy_file(src, dest, conflict_strategy):
    """Copy a file with conflict handling."""
    if os.path.exists(dest):
        if conflict_strategy == "skip":
            logger.info(f"Skipping existing file: {dest}")
            return
        elif conflict_strategy == "overwrite":
            logger.info(f"Overwriting file: {dest}")
        elif conflict_strategy == "rename":
            base, ext = os.path.splitext(dest)
            counter = 1
            new_dest = f"{base}_v{counter}{ext}"
            while os.path.exists(new_dest):
                counter += 1
                new_dest = f"{base}_v{counter}{ext}"
            dest = new_dest
            logger.info(f"File exists, renaming to: {os.path.basename(dest)}")

    shutil.copy2(src, dest)
    logger.info(f"Copied: {src} -> {dest}")

def merge_bids_directories(source_dir, dest_dir, conflict_strategy="skip", dry_run=False):
    """Merge source BIDS directory into destination directory."""
    # Verify both directories are valid BIDS directories
    if not validate_bids_directory(source_dir) or not validate_bids_directory(dest_dir):
        return False

    # First handle the dataset description
    if not dry_run:
        merge_dataset_description(source_dir, dest_dir)
    if not dry_run:
        sucess = merge_particitipants_tsv(source_dir, dest_dir)
        # pause for user to check the merged participants.tsv
        input("Press Enter to continue...")
        if not sucess:
            logger.error("Failed to merge participants.tsv")
            return False

    # Handle subject directories and other BIDS folders
    for item in os.listdir(source_dir):
        source_path = os.path.join(source_dir, item)
        dest_path = os.path.join(dest_dir, item)

        # Skip dataset_description.json as it's handled separately
        if item == "dataset_description.json":
            continue
        if item == "participants.tsv":
            continue

        # skip if not sub-ADNI....
        if not item.startswith("sub-ADNI"):
            logger.info(f"Skipping non-subject directory: {item}")
            continue

        # Handle directories (subjects, derivatives, code, etc.)
        if os.path.isdir(source_path):
            if not os.path.exists(dest_path):
                logger.info(f"Creating directory: {item}")
                if not dry_run:
                    os.makedirs(dest_path, exist_ok=True)

            # Copy all content recursively
            for root, dirs, files in os.walk(source_path):
                rel_path = os.path.relpath(root, source_path)
                target_dir = dest_path if rel_path == "." else os.path.join(dest_path, rel_path)

                if not os.path.exists(target_dir) and not dry_run:
                    os.makedirs(target_dir, exist_ok=True)

                # Copy files
                for file in files:
                    source_file = os.path.join(root, file)
                    dest_file = os.path.join(target_dir, file)

                    if dry_run:
                        logger.info(f"Would copy: {source_file} -> {dest_file}")
                    else:
                        copy_file(source_file, dest_file, conflict_strategy)

        # Handle files at root level
        elif os.path.isfile(source_path):
            if dry_run:
                logger.info(f"Would copy: {source_path} -> {dest_path}")
            else:
                copy_file(source_path, dest_path, conflict_strategy)

    return True

def merge_particitipants_tsv(source_dir, dest_dir):
    """Merge participants.tsv files."""
    source_participants_path = os.path.join(source_dir, "participants.tsv")
    dest_participants_path = os.path.join(dest_dir, "participants.tsv")

    if not os.path.exists(source_participants_path):
        logger.warning(f"Source participants.tsv does not exist: {source_participants_path}")
        return False

    if not os.path.exists(dest_participants_path):
        logger.info(f"Copying participants.tsv from {source_participants_path} to {dest_participants_path}")
        shutil.copy2(source_participants_path, dest_participants_path)
    else:
        # make a backup of the destination participants.tsv
        backup_path = dest_participants_path + ".bak"
        shutil.copy2(dest_participants_path, backup_path)
        logger.info(f"Created backup Copy: {dest_participants_path} -> {backup_path}")
        logger.warning(f"Destination participants.tsv already exists: {dest_participants_path}")
        df1 = pd.read_csv(source_participants_path, sep="\t")
        df2 = pd.read_csv(dest_participants_path, sep="\t")
        a = pd.merge(df1, df2, on="participant_id", how='outer', suffixes=("","_drop"))
        for col_name in a.columns:
            if not col_name.endswith("_drop") and col_name != "participant_id":
                a[col_name] = a[col_name].fillna(a[col_name + "_drop"])
        a = a.drop(columns=[col for col in a.columns if col.endswith("_drop")])
        a.to_csv(dest_participants_path, sep="\t", index=False)
        # report overlaping participants
        logger.info(f"Merged participants.tsv files: {source_participants_path} -> {dest_participants_path}")
        # compute overlapping participants
        count = len(set(df1.participant_id).intersection(set(df2.participant_id)))
        logger.info(f"Overlapping participants: {count} form source = {len(df1)} and dest={len(df2)}")
    return True

def main():
    args = parse_args()

    source_dir = os.path.abspath(args.source)
    dest_dir = os.path.abspath(args.destination)

    logger.info(f"Source BIDS directory: {source_dir}")
    logger.info(f"Destination BIDS directory: {dest_dir}")

    if args.dry_run:
        logger.info("Performing dry run (no files will be copied)")

    if not os.path.exists(source_dir):
        logger.error(f"Source directory does not exist: {source_dir}")
        return 1

    if not os.path.exists(dest_dir):
        logger.error(f"Destination directory does not exist: {dest_dir}")
        return 1

    success = merge_bids_directories(source_dir, dest_dir, args.conflict, args.dry_run)

    if success:
        logger.info("BIDS merge completed successfully")
        return 0
    else:
        logger.error("BIDS merge failed")
        return 1

if __name__ == "__main__":
    exit(main())