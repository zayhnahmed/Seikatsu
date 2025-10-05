"""
Cleanup Script
Removes old log files and temporary data to free up disk space.
Run this periodically to maintain a clean development/production environment.
"""

import sys
import os
import glob
from pathlib import Path
from datetime import datetime, timedelta
import logging

# Add parent directory to path to allow imports
sys.path.append(str(Path(__file__).parent.parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


def cleanup_log_files(directory: str = ".", older_than_days: int = 7):
    """
    Delete log files older than specified number of days.
    
    Args:
        directory: Directory to search for log files (default: current directory)
        older_than_days: Delete files older than this many days (default: 7)
    """
    try:
        logger.info(f"Searching for .log files in: {directory}")
        
        # Find all .log files
        log_pattern = os.path.join(directory, "*.log")
        log_files = glob.glob(log_pattern)
        
        if not log_files:
            logger.info("No .log files found")
            return
        
        logger.info(f"Found {len(log_files)} log file(s)")
        
        deleted_count = 0
        skipped_count = 0
        cutoff_date = datetime.now() - timedelta(days=older_than_days)
        
        for log_file in log_files:
            try:
                # Get file modification time
                file_mtime = datetime.fromtimestamp(os.path.getmtime(log_file))
                
                if file_mtime < cutoff_date:
                    # File is older than cutoff, delete it
                    file_size = os.path.getsize(log_file)
                    os.remove(log_file)
                    logger.info(
                        f"Deleted: {log_file} "
                        f"(Size: {file_size / 1024:.2f} KB, "
                        f"Modified: {file_mtime.strftime('%Y-%m-%d')})"
                    )
                    deleted_count += 1
                else:
                    logger.info(f"Skipped (recent): {log_file}")
                    skipped_count += 1
                    
            except FileNotFoundError:
                logger.warning(f"File not found (already deleted?): {log_file}")
            except PermissionError:
                logger.error(f"Permission denied: {log_file}")
            except Exception as e:
                logger.error(f"Error processing {log_file}: {str(e)}")
        
        logger.info(f"Cleanup complete: {deleted_count} deleted, {skipped_count} skipped")
        
    except Exception as e:
        logger.error(f"Error during log cleanup: {str(e)}")


def cleanup_pycache(root_directory: str = "."):
    """
    Remove __pycache__ directories recursively.
    
    Args:
        root_directory: Root directory to start search (default: current directory)
    """
    try:
        logger.info(f"Searching for __pycache__ directories in: {root_directory}")
        
        deleted_count = 0
        
        for dirpath, dirnames, filenames in os.walk(root_directory):
            if "__pycache__" in dirnames:
                pycache_path = os.path.join(dirpath, "__pycache__")
                try:
                    # Remove directory and all contents
                    import shutil
                    shutil.rmtree(pycache_path)
                    logger.info(f"Deleted: {pycache_path}")
                    deleted_count += 1
                except Exception as e:
                    logger.error(f"Error deleting {pycache_path}: {str(e)}")
        
        if deleted_count > 0:
            logger.info(f"Removed {deleted_count} __pycache__ director(ies)")
        else:
            logger.info("No __pycache__ directories found")
            
    except Exception as e:
        logger.error(f"Error during __pycache__ cleanup: {str(e)}")


def cleanup_temp_files(directory: str = ".", patterns: list = None):
    """
    Remove temporary files matching specific patterns.
    
    Args:
        directory: Directory to search (default: current directory)
        patterns: List of file patterns to delete (default: ['.tmp', '.cache'])
    """
    if patterns is None:
        patterns = ["*.tmp", "*.cache", "*.bak", "*~"]
    
    try:
        logger.info(f"Searching for temporary files in: {directory}")
        
        deleted_count = 0
        
        for pattern in patterns:
            file_pattern = os.path.join(directory, pattern)
            temp_files = glob.glob(file_pattern)
            
            for temp_file in temp_files:
                try:
                    os.remove(temp_file)
                    logger.info(f"Deleted: {temp_file}")
                    deleted_count += 1
                except Exception as e:
                    logger.error(f"Error deleting {temp_file}: {str(e)}")
        
        if deleted_count > 0:
            logger.info(f"Removed {deleted_count} temporary file(s)")
        else:
            logger.info("No temporary files found")
            
    except Exception as e:
        logger.error(f"Error during temp file cleanup: {str(e)}")


def get_directory_size(directory: str = "."):
    """
    Calculate total size of a directory.
    
    Args:
        directory: Directory path
        
    Returns:
        Size in bytes
    """
    total_size = 0
    
    try:
        for dirpath, dirnames, filenames in os.walk(directory):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                try:
                    total_size += os.path.getsize(filepath)
                except (OSError, FileNotFoundError):
                    pass
    except Exception as e:
        logger.error(f"Error calculating directory size: {str(e)}")
    
    return total_size


def format_size(size_bytes: int) -> str:
    """Format bytes into human-readable string."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"


def cleanup_all(log_days: int = 7):
    """
    Run all cleanup operations.
    
    Args:
        log_days: Delete log files older than this many days
    """
    try:
        logger.info("=" * 60)
        logger.info("SEIKATSU CLEANUP SCRIPT")
        logger.info("=" * 60)
        
        # Get initial directory size
        initial_size = get_directory_size(".")
        logger.info(f"Initial directory size: {format_size(initial_size)}")
        logger.info("-" * 60)
        
        # Cleanup operations
        logger.info("1. Cleaning up log files...")
        cleanup_log_files(older_than_days=log_days)
        logger.info("-" * 60)
        
        logger.info("2. Cleaning up __pycache__ directories...")
        cleanup_pycache()
        logger.info("-" * 60)
        
        logger.info("3. Cleaning up temporary files...")
        cleanup_temp_files()
        logger.info("-" * 60)
        
        # Get final directory size
        final_size = get_directory_size(".")
        freed_space = initial_size - final_size
        
        logger.info("=" * 60)
        logger.info("CLEANUP SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Initial size: {format_size(initial_size)}")
        logger.info(f"Final size: {format_size(final_size)}")
        logger.info(f"Freed space: {format_size(freed_space)}")
        logger.info("=" * 60)
        logger.info("✅ Cleanup operations completed")
        logger.info("=" * 60)
        logger.info("For detailed logs, check the console output")
        logger.info("=" * 60)
        logger.info("Consider scheduling this script to run periodically")
        logger.info("=" * 60)
        logger.info("Visit https://seikatsu.app for more information")
        logger.info("=" * 60)
        logger.info("Thank you for using Seikatsu!")
        logger.info("=" * 60)
    except Exception as e:
        logger.error("=" * 60)
        logger.error(f"❌ Error during cleanup: {str(e)}")
        logger.error("=" * 60)
        sys.exit(1)


if __name__ == "__main__":
    # Parse command line arguments
    import argparse
    
    parser = argparse.ArgumentParser(description="Cleanup script for Seikatsu project")
    parser.add_argument(
        "--log-days",
        type=int,
        default=7,
        help="Delete log files older than this many days (default: 7)"
    )
    
    args = parser.parse_args()
    
    # Run cleanup
    cleanup_all(log_days=args.log_days)