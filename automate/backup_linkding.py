#!/usr/bin/env python3
import os
import sys
import shutil
import json
from datetime import datetime
import subprocess

def load_config():
    """Load configuration from JSON file"""
    config_path = os.path.join(os.path.dirname(__file__), "backup_config.json")
    try:
        with open(config_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: Configuration file not found at {config_path}")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in configuration file {config_path}")
        sys.exit(1)

def run_command(cmd, cwd=None):
    """Run a shell command and return output"""
    print(f"\nExecuting command: {cmd}")
    process = subprocess.run(cmd, cwd=cwd, shell=True, capture_output=True, text=True)

    if process.stdout:
        print("Output:")
        print(process.stdout)

    if process.stderr:
        print("Error output:")
        print(process.stderr)

    if process.returncode != 0:
        print(f"Command failed with exit code: {process.returncode}")
        sys.exit(1)

    return process.stdout.strip()

def main():
    # Load configuration
    config = load_config()
    dest_dir = config["backup_dest_dir"]

    # Define paths
    linkding_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    backup_dir = os.path.join(linkding_dir, "backups")
    dest_file = os.path.join(dest_dir, "linkding_bookmarks.json")

    # Create backup using Django management command
    print("Creating backup...")
    run_command("python3 manage.py backup_bookmarks_as_json", cwd=linkding_dir)

    # Find the most recent backup file
    backup_files = [f for f in os.listdir(backup_dir) if f.startswith("linkding_bookmarks_")]
    if not backup_files:
        print("No backup file found!")
        sys.exit(1)

    latest_backup = max(backup_files)
    backup_path = os.path.join(backup_dir, latest_backup)

    # Move the file to destination
    print(f"Moving {latest_backup} to {dest_file}")
    shutil.copy2(backup_path, dest_file)

    # Git operations
    print("Committing and pushing changes...")
    os.chdir(dest_dir)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    run_command("git add linkding_bookmarks.json")
    run_command(f'git commit -m "Update linkding bookmarks backup - {timestamp}"')
    run_command("git push")

    # Clean up backup files after successful commit
    print("Cleaning up backup files...")
    for backup_file in backup_files:
        file_path = os.path.join(backup_dir, backup_file)
        os.remove(file_path)
        print(f"Deleted: {backup_file}")

    print("Backup completed successfully!")

if __name__ == "__main__":
    main()
