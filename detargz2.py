"""Extract a tar archive while rejecting unsafe or unexpectedly large entries.

This extractor intentionally supports only ordinary files and directories.  It
does not preserve archive ownership, permissions, timestamps, links, devices,
or other special metadata.
"""

from __future__ import annotations

import argparse
import ntpath
import os
from pathlib import Path
import stat
import sys
import tarfile
from dataclasses import dataclass
from typing import BinaryIO, Iterable, Optional


DEFAULT_MAX_MEMBERS = 10_000
DEFAULT_MAX_FILE_SIZE = 2 * 1024**3
DEFAULT_MAX_TOTAL_SIZE = 10 * 1024**3
COPY_CHUNK_SIZE = 1024 * 1024
MAX_NAME_LENGTH = 4096
MAX_PATH_COMPONENTS = 256


class ExtractionError(Exception):
    """An archive or destination failed a safety check."""


@dataclass(frozen=True)
class CheckedMember:
    info: tarfile.TarInfo
    relative_path: Path
    is_directory: bool


def non_negative_integer(value: str) -> int:
    try:
        result = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("must be an integer") from exc
    if result < 0:
        raise argparse.ArgumentTypeError("must not be negative")
    return result


def parse_arguments(argv: Optional[Iterable[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Safely extract regular files and directories from a tar archive."
    )
    parser.add_argument("archive", type=Path, help="tar archive to extract")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="destination directory (default: ARCHIVE.extracted)",
    )
    parser.add_argument(
        "--max-members",
        type=non_negative_integer,
        default=DEFAULT_MAX_MEMBERS,
        help=f"maximum archive entries (default: {DEFAULT_MAX_MEMBERS})",
    )
    parser.add_argument(
        "--max-file-size",
        type=non_negative_integer,
        default=DEFAULT_MAX_FILE_SIZE,
        metavar="BYTES",
        help=f"maximum expanded size of one file (default: {DEFAULT_MAX_FILE_SIZE})",
    )
    parser.add_argument(
        "--max-total-size",
        type=non_negative_integer,
        default=DEFAULT_MAX_TOTAL_SIZE,
        metavar="BYTES",
        help=f"maximum total expanded file size (default: {DEFAULT_MAX_TOTAL_SIZE})",
    )
    return parser.parse_args(argv)


def path_is_within(root: Path, candidate: Path) -> bool:
    try:
        return os.path.commonpath((os.fspath(root), os.fspath(candidate))) == os.fspath(root)
    except ValueError:
        # Different drives on Windows, for example, can have no common path.
        return False


def validate_windows_component(component: str, member_name: str) -> None:
    """Reject names that can be aliases, devices, or streams on Windows."""
    if any(ord(character) < 32 for character in component):
        raise ExtractionError(f"control character in member name {member_name!r}")
    if any(character in '<>:"|?*' for character in component):
        raise ExtractionError(f"Windows-special character in member name {member_name!r}")
    if component.endswith((" ", ".")):
        raise ExtractionError(f"Windows-ambiguous member name {member_name!r}")

    device_name = component.split(".", 1)[0].rstrip(" .").upper()
    reserved = {"CON", "PRN", "AUX", "NUL", "CLOCK$"}
    reserved.update(f"COM{number}" for number in range(1, 10))
    reserved.update(f"LPT{number}" for number in range(1, 10))
    if device_name in reserved:
        raise ExtractionError(f"Windows device name in archive member {member_name!r}")


def safe_relative_path(member_name: str, output_root: Path) -> Path:
    if not member_name or "\x00" in member_name:
        raise ExtractionError("archive contains an empty or NUL-containing member name")
    if len(member_name) > MAX_NAME_LENGTH:
        raise ExtractionError(f"archive member name is too long: {member_name!r}")

    # Tar names conventionally use '/', but treating '\\' as a separator as
    # well prevents a name from becoming traversal only on Windows.
    portable_name = member_name.replace("\\", "/")
    windows_name = portable_name.replace("/", "\\")
    drive, _ = ntpath.splitdrive(windows_name)
    if portable_name.startswith("/") or drive or ntpath.isabs(windows_name):
        raise ExtractionError(f"absolute or drive-qualified member path {member_name!r}")

    components = []
    for component in portable_name.split("/"):
        if component in ("", "."):
            continue
        if component == "..":
            raise ExtractionError(f"parent traversal in archive member {member_name!r}")
        validate_windows_component(component, member_name)
        components.append(component)

    if not components:
        # A root-directory entry named "." or "./" is common in tar files.
        # The caller permits it only for directories and treats it as a no-op.
        return Path(".")
    if len(components) > MAX_PATH_COMPONENTS:
        raise ExtractionError(f"archive member path is too deep: {member_name!r}")

    relative_path = Path(*components)
    candidate = (output_root / relative_path).resolve(strict=False)
    if not path_is_within(output_root, candidate):
        raise ExtractionError(f"archive member escapes the destination: {member_name!r}")
    return relative_path


def path_key(path: Path) -> str:
    """Return the platform's normalized key for collision detection."""
    return os.path.normcase(os.path.normpath(os.fspath(path)))


def inspect_archive(
    archive: tarfile.TarFile,
    output_root: Path,
    max_members: int,
    max_file_size: int,
    max_total_size: int,
) -> list[CheckedMember]:
    checked: list[CheckedMember] = []
    kinds_by_path: dict[str, str] = {}
    total_size = 0

    for number, member in enumerate(archive, start=1):
        if number > max_members:
            raise ExtractionError(f"archive contains more than {max_members} entries")

        relative_path = safe_relative_path(member.name, output_root)
        if relative_path == Path("."):
            if member.isdir():
                continue
            raise ExtractionError(f"archive member has no usable path: {member.name!r}")

        key = path_key(relative_path)
        if key in kinds_by_path:
            raise ExtractionError(f"duplicate archive path {member.name!r}")

        if member.isdir():
            kind = "directory"
            is_directory = True
        elif member.isfile():
            kind = "file"
            is_directory = False
            if member.size < 0:
                raise ExtractionError(f"negative size for archive member {member.name!r}")
            if member.size > max_file_size:
                raise ExtractionError(
                    f"archive member {member.name!r} exceeds the per-file size limit"
                )
            total_size += member.size
            if total_size > max_total_size:
                raise ExtractionError("archive exceeds the total expanded-size limit")
        else:
            raise ExtractionError(
                f"unsupported entry type for {member.name!r}; only files and directories are allowed"
            )

        kinds_by_path[key] = kind
        checked.append(CheckedMember(member, relative_path, is_directory))

    for member in checked:
        parent = member.relative_path.parent
        while parent != Path("."):
            if kinds_by_path.get(path_key(parent)) == "file":
                raise ExtractionError(
                    f"archive path {os.fspath(parent)!r} is both a file and a parent directory"
                )
            parent = parent.parent

    return checked


def is_reparse_point(file_stat: os.stat_result) -> bool:
    attributes = getattr(file_stat, "st_file_attributes", 0)
    reparse_flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
    return bool(attributes & reparse_flag)


def verify_real_directory(path: Path) -> None:
    try:
        file_stat = path.lstat()
    except OSError as exc:
        raise ExtractionError(f"cannot inspect destination directory {path}: {exc}") from exc
    if stat.S_ISLNK(file_stat.st_mode) or is_reparse_point(file_stat):
        raise ExtractionError(f"destination path is a link or reparse point: {path}")
    if not stat.S_ISDIR(file_stat.st_mode):
        raise ExtractionError(f"destination path is not a directory: {path}")


def ensure_directory(output_root: Path, relative_directory: Path) -> Path:
    current = output_root
    for component in relative_directory.parts:
        current = current / component
        try:
            current.mkdir(mode=0o700)
        except FileExistsError:
            pass
        except OSError as exc:
            raise ExtractionError(f"cannot create directory {current}: {exc}") from exc
        verify_real_directory(current)
        try:
            resolved = current.resolve(strict=True)
        except OSError as exc:
            raise ExtractionError(f"cannot resolve destination directory {current}: {exc}") from exc
        if not path_is_within(output_root, resolved):
            raise ExtractionError(f"destination directory escapes extraction root: {current}")
    return current


def copy_member(source: BinaryIO, destination: BinaryIO, expected_size: int) -> None:
    remaining = expected_size
    while remaining:
        block = source.read(min(COPY_CHUNK_SIZE, remaining))
        if not block:
            raise ExtractionError("archive member ended before its declared size")
        destination.write(block)
        remaining -= len(block)


def extract_checked_members(
    archive: tarfile.TarFile,
    members: list[CheckedMember],
    output_root: Path,
) -> None:
    for member in members:
        if member.is_directory:
            ensure_directory(output_root, member.relative_path)
            continue

        parent = ensure_directory(output_root, member.relative_path.parent)
        destination_path = parent / member.relative_path.name
        try:
            source = archive.extractfile(member.info)
        except (KeyError, OSError, tarfile.TarError) as exc:
            raise ExtractionError(f"cannot read archive member {member.info.name!r}: {exc}") from exc
        if source is None:
            raise ExtractionError(f"archive member has no file data: {member.info.name!r}")

        try:
            with source, destination_path.open("xb") as destination:
                copy_member(source, destination, member.info.size)
        except FileExistsError as exc:
            raise ExtractionError(f"refusing to overwrite destination path {destination_path}") from exc
        except ExtractionError:
            raise
        except OSError as exc:
            raise ExtractionError(f"cannot write destination file {destination_path}: {exc}") from exc


def run(args: argparse.Namespace) -> Path:
    try:
        archive_path = args.archive.expanduser().resolve(strict=True)
    except OSError as exc:
        raise ExtractionError(f"cannot resolve archive path {args.archive}: {exc}") from exc

    if args.output is None:
        output_path = archive_path.with_name(archive_path.name + ".extracted")
    else:
        output_path = args.output.expanduser().resolve(strict=False)

    try:
        output_parent = output_path.parent.resolve(strict=True)
    except OSError as exc:
        raise ExtractionError(f"cannot resolve output parent {output_path.parent}: {exc}") from exc
    verify_real_directory(output_parent)
    output_path = output_parent / output_path.name

    if output_path == archive_path:
        raise ExtractionError("the output directory cannot be the archive itself")

    try:
        raw_archive = archive_path.open("rb")
    except OSError as exc:
        raise ExtractionError(f"cannot open archive {archive_path}: {exc}") from exc

    with raw_archive:
        try:
            if not stat.S_ISREG(os.fstat(raw_archive.fileno()).st_mode):
                raise ExtractionError(f"archive is not a regular file: {archive_path}")
            archive = tarfile.open(fileobj=raw_archive, mode="r:*")
        except (OSError, tarfile.TarError) as exc:
            raise ExtractionError(f"not a readable tar archive: {archive_path}: {exc}") from exc

        with archive:
            checked_members = inspect_archive(
                archive,
                output_path,
                args.max_members,
                args.max_file_size,
                args.max_total_size,
            )

            try:
                output_path.mkdir(mode=0o700)
            except FileExistsError as exc:
                raise ExtractionError(f"destination already exists: {output_path}") from exc
            except OSError as exc:
                raise ExtractionError(f"cannot create destination {output_path}: {exc}") from exc
            verify_real_directory(output_path)

            try:
                extract_checked_members(archive, checked_members, output_path)
            except Exception as exc:
                if isinstance(exc, ExtractionError):
                    detail = str(exc)
                else:
                    detail = f"unexpected extraction error: {exc}"
                raise ExtractionError(
                    f"{detail}. The newly created destination may be incomplete: {output_path}"
                ) from exc

    return output_path


def main(argv: Optional[Iterable[str]] = None) -> int:
    args = parse_arguments(argv)
    try:
        output_path = run(args)
    except ExtractionError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("Interrupted.", file=sys.stderr)
        return 130

    print(f"Extracted safely to: {output_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
