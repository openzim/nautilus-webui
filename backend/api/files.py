import hashlib
from collections.abc import Iterator
from pathlib import Path
from typing import BinaryIO
from uuid import UUID

from api.constants import constants
from api.database import get_local_fpath_for


def calculate_file_size(file: BinaryIO) -> int:
    """Calculate the size of a file chunk by chunk"""
    size = 0
    for chunk in read_file_in_chunks(file):
        size += len(chunk)
    return size


def read_file_in_chunks(
    reader: BinaryIO, chunk_size=constants.chunk_size
) -> Iterator[bytes]:
    """Read Big file chunk by chunk. Default chunk size is 2k"""
    while True:
        chunk = reader.read(chunk_size)
        if not chunk:
            break
        yield chunk
    reader.seek(0)


def save_file(file: BinaryIO, file_name: str, project_id: UUID) -> Path:
    """Saves a binary file to a specific location and returns its path."""
    fpath = get_local_fpath_for(file_name, project_id)
    if not fpath.is_file():
        with open(fpath, "wb") as file_object:
            for chunk in read_file_in_chunks(file):
                file_object.write(chunk)
    return fpath


def generate_file_hash(file: BinaryIO) -> str:
    """Generate sha256 hash of a file, optimized for large files"""
    hasher = hashlib.sha256()
    for chunk in read_file_in_chunks(file):
        hasher.update(chunk)
    return hasher.hexdigest()


def normalize_filename(filename: str) -> str:
    """filesystem (ext4,apfs,hfs+,ntfs,exfat) and S3 compliant filename"""

    normalized = str(filename)

    # we replace / with __ as it would have a meaning
    replacements = (("/", "__"),)
    for pattern, repl in replacements:
        normalized = filename.replace(pattern, repl)

    # other prohibited chars are removed (mostly for Windows context)
    removals = ["\\", ":", "*", "?", '"', "<", ">", "|"] + [
        chr(idx) for idx in range(1, 32)
    ]
    for char in removals:
        normalized.replace(char, "")

    # ext4/exfat has a 255B filename limit (s3 is 1KiB)
    return normalized.encode("utf-8")[:255].decode("utf-8")
