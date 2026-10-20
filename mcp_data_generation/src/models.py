# models.py

from dataclasses import dataclass, field


@dataclass
class Document:
    identifier: str = ""

    project: str = ""
    organizational_unit: list[str] = field(default_factory=list)

    source_system: str = ""
    source_identifier: str = ""
    source_url: str = ""

    date: str = ""

    asset_type: str = ""
    content_type: str = ""
    title: str = ""

    content: str = ""