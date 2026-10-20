from pathlib import Path
import hashlib
import json
from datetime import datetime, timezone
from dataclasses import asdict

from src.models import Document
from src.py_saidify import py_saidify

RAW_DIR = Path("data/raw")
REGISTRY_FILE = Path("data/ingestion_registry.json")
PROCESSED_DIR = Path("data/processed")

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

def _sha256_file(file_path: Path) -> str:
    sha = hashlib.sha256()

    with open(file_path, "rb") as f:
        while chunk := f.read(8192):
            sha.update(chunk)

    return sha.hexdigest()


def _load_registry() -> dict:
    if not REGISTRY_FILE.exists():
        return {}

    with open(REGISTRY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_registry(registry: dict) -> None:
    with open(REGISTRY_FILE, "w", encoding="utf-8") as f:
        json.dump(registry, f, indent=2)


def _get_source_system(file_path: Path) -> str:
    relative_path = file_path.relative_to(RAW_DIR)

    return relative_path.parts[0].lower()


def _process_file(file_path: Path) -> None:
    source_system = _get_source_system(file_path)

    print(f"Processing {file_path}")
    print(f"Source: {source_system}")

    if source_system == "zoom":
        from src.parsers import zoom

        document = zoom.process(file_path)

        return document

    else:
        print(f"No parser registered for '{source_system}'")
        return None

def _save_document(document: dict) -> None:

    output_file = (
        PROCESSED_DIR /
        f"{document['identifier']}.json"
    )

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(document, f, indent=2)

def main() -> None:
    registry = _load_registry()

    for file_path in RAW_DIR.rglob("*"):

        if not file_path.is_file():
            continue

        if file_path.name == "metadata.json":
            continue

        file_hash = _sha256_file(file_path)

        registry_entry = registry.get(file_path.as_posix())

        if (
            registry_entry
            and registry_entry["file_hash"] == file_hash
        ):
            print(f"Skipping {file_path}")
            continue

        document = _process_file(file_path)

        if document is None:
            continue

        document_dict = asdict(document)

        said, document_dict = py_saidify(
            document_dict,
            label="identifier"
        )

        _save_document(document_dict)

        registry[file_path.as_posix()] = {
            "file_hash": file_hash,
            "document_said": said,
            "processed_at": datetime.now(
                timezone.utc
            ).isoformat()
        }

    _save_registry(registry)


if __name__ == "__main__":
    main()