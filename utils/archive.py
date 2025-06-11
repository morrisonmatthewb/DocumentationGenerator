"""
Archive file extraction utilities.
"""

import os
import zipfile
import tempfile
import shutil
from typing import Dict, List, Tuple, Any, Optional
from config.constants import (
    SUPPORTED_EXTENSIONS,
    SUPPORTED_ARCHIVE_FORMATS,
    MAX_EXTRACT_SIZE,
    MAX_FILES,
    MAX_UPLOAD_SIZE,
)


def extract_archive_to_temp_dir(uploaded_file, file_extension: str) -> Tuple[str, str]:
    """
    Extract the contents of an archive file to a temporary directory.
    Supports multiple archive formats.

    Args:
        uploaded_file: The uploaded archive file
        file_extension: The file extension to determine the archive type

    Returns:
        Tuple of (temp_dir, extraction_dir) paths
    """
    # Create a temporary directory
    temp_dir = tempfile.mkdtemp()
    temp_archive_path = os.path.join(temp_dir, f"archive{file_extension}")

    # Save uploaded file to disk temporarily
    with open(temp_archive_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    extraction_dir = os.path.join(temp_dir, "extracted")
    os.makedirs(extraction_dir, exist_ok=True)

    uploaded_file.seek(0, os.SEEK_END)
    file_size = uploaded_file.tell()
    uploaded_file.seek(0)
    
    if file_size > MAX_UPLOAD_SIZE:  
        raise Exception(f"Archive too large: {file_size / (1024*1024):.1f}MB")
    
    try:
        # Handle different archive formats with some zip bomb protection
        if file_extension.lower() == '.zip':
            total_size = 0
            file_count = 0
            
            with zipfile.ZipFile(temp_archive_path, 'r') as zip_ref:
                for info in zip_ref.infolist():
                    file_count += 1
                    if file_count > MAX_FILES:
                        raise Exception("Archive contains too many files")
                    
                    if '..' in info.filename or info.filename.startswith('/'):
                        raise Exception(f"Unsafe path: {info.filename}")
                    
                    total_size += info.file_size
                    if total_size > MAX_EXTRACT_SIZE:
                        raise Exception("Archive too large when extracted")
                
                zip_ref.extractall(extraction_dir)
                
        elif file_extension.lower() == '.7z':
            import py7zr
            total_size = 0
            file_count = 0
            
            with py7zr.SevenZipFile(temp_archive_path, mode='r') as z:
                for info in z.list():
                    file_count += 1
                    if file_count > MAX_FILES:
                        raise Exception("Archive contains too many files")
                    
                    if '..' in info.filename or info.filename.startswith('/'):
                        raise Exception(f"Unsafe path: {info.filename}")
                    
                    if hasattr(info, 'uncompressed'):
                        total_size += info.uncompressed
                        if total_size > MAX_EXTRACT_SIZE:
                            raise Exception("Archive too large when extracted")
                
                z.extractall(path=extraction_dir)
                
        elif file_extension.lower() == '.rar':
            import rarfile
            total_size = 0
            file_count = 0
            
            with rarfile.RarFile(temp_archive_path) as rf:
                for info in rf.infolist():
                    file_count += 1
                    if file_count > MAX_FILES:
                        raise Exception("Archive contains too many files")
                    
                    if '..' in info.filename or info.filename.startswith('/'):
                        raise Exception(f"Unsafe path: {info.filename}")
                    
                    total_size += info.file_size
                    if total_size > MAX_EXTRACT_SIZE:
                        raise Exception("Archive too large when extracted")
                
                rf.extractall(path=extraction_dir)

    except Exception as e:
        # Clean up and re-raise
        shutil.rmtree(temp_dir)
        raise Exception(f"Failed to extract archive: {str(e)}")

    return temp_dir, extraction_dir


def extract_files_from_archive(
    uploaded_file,
    selected_extensions: Optional[List[str]] = None,
    max_file_size_mb: int = 5,
) -> Dict[str, Dict[str, Any]]:
    """
    Extract files from various archive formats based on selected extensions.

    Args:
        uploaded_file: The uploaded archive file
        selected_extensions: List of file extensions to extract (None for all supported)
        max_file_size_mb: Maximum size of individual files to process in MB

    Returns:
        Dictionary mapping file paths to their content
    """
    if selected_extensions is None:
        selected_extensions = list(SUPPORTED_EXTENSIONS.keys())

    # Determine archive type from filename
    file_name = uploaded_file.name
    file_extension = os.path.splitext(file_name)[1].lower()

    if file_extension not in SUPPORTED_ARCHIVE_FORMATS:
        raise ValueError(f"Unsupported archive format: {file_extension}.")

    # Extract archive to temp directory
    temp_dir, extraction_dir = extract_archive_to_temp_dir(
        uploaded_file, file_extension
    )

    try:
        # Process extracted files
        extracted_files = {}
        max_bytes = max_file_size_mb * 1024 * 1024

        # Walk through directory structure
        for root, _, files in os.walk(extraction_dir):
            for file in files:
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, extraction_dir)

                # Skip files that are too large
                if os.path.getsize(file_path) > max_bytes:
                    continue

                file_ext = os.path.splitext(file)[1].lower()
                if file_ext in selected_extensions:
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            content = f.read()

                            # Get directory structure for organization
                            dir_path = os.path.dirname(rel_path)

                            extracted_files[rel_path] = {
                                "content": content,
                                "language": SUPPORTED_EXTENSIONS.get(
                                    file_ext, "Unknown"
                                ),
                                "directory": dir_path,
                            }
                    except UnicodeDecodeError:
                        # Skip binary files or files with encoding issues
                        continue

        return extracted_files

    finally:
        # Clean up temporary directory
        shutil.rmtree(temp_dir)
