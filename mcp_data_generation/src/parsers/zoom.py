# parsers/zoom.py

import json
import re
from pathlib import Path
from datetime import datetime
from src.models import Document

def process(file_path: Path) -> Document:
    content_type = _get_content_type(file_path)

    if content_type is None:
        print(f"Skipping unsupported Zoom file: {file_path.name}")
        return

    date_object = _extract_date(file_path)

    raw_content = _read_file(file_path)

    if file_path.suffix.lower() == ".vtt":
        content = _extract_vtt_text(raw_content)
    else:
        content = raw_content

    metadata = _load_metadata(file_path)

    document = _build_document(
        file_path=file_path,
        content=content,
        content_type=content_type,
        date_object=date_object,
        metadata=metadata,
    )

    return document

def _is_zoom_export_file(file_path: Path) -> bool:
    return bool(
        re.match(
            r"^GMT\d{8}-\d{6}_Recording.*\.(txt|vtt)$",
            file_path.name,
            re.IGNORECASE,
        )
    )

def _get_content_type(file_path: Path) -> str | None:
    if not _is_zoom_export_file(file_path):
        return None

    file_name = file_path.name.lower()
    if file_name.endswith(".txt"):
        return "Chat"

    if ".cc." in file_name:
        return "ClosedCaptioning"

    if ".transcript." in file_name:
        return "Transcript"

    return None


def _extract_date(file_path: Path) -> datetime:
    file_name = file_path.name

    date_string = file_name[3:11]

    return datetime.strptime(date_string, "%Y%m%d")


def _read_file(file_path: Path) -> str:
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def _extract_vtt_text(content: str) -> str:
    timestamp_pattern = re.compile(
        r"\d{2}:\d{2}:\d{2}\.\d{3}\s*-->\s*\d{2}:\d{2}:\d{2}\.\d{3}"
    )

    lines = []

    for line in content.splitlines():
        line = line.strip()

        if not line:
            continue

        if line == "WEBVTT":
            continue

        if timestamp_pattern.match(line):
            continue

        lines.append(line)

    return " ".join(lines)

def _extract_source_identifier(file_path: Path) -> str:
    return file_path.name.split("_")[0]


def _build_document(
    file_path: Path,
    content: str,
    content_type: str,
    date_object: datetime,
    metadata: dict,
) -> Document:

    return Document(
        project=metadata["project"],
        organizational_unit=metadata["organizational_unit"],
        source_system="Zoom",
        source_identifier=_extract_source_identifier(file_path),
        source_url=metadata.get("source_url", ""),
        date=date_object.strftime("%Y-%m-%d"),
        asset_type="Meeting",
        content_type=content_type,
        title=metadata["title"],
        content=content,
    )


def _load_metadata(file_path: Path) -> dict:
    current_path = file_path.parent

    while current_path != current_path.parent:

        metadata_file = current_path / "metadata.json"

        if metadata_file.exists():
            with open(metadata_file, "r", encoding="utf-8") as f:
                return json.load(f)

        current_path = current_path.parent

    raise FileNotFoundError(
        f"No metadata.json found for {file_path}"
    )