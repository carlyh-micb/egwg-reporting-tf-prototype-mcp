import base64
import copy
import json
from hmac import compare_digest

from blake3 import blake3


def py_saidify(data: dict, label: str = "d") -> tuple[str, dict]:
    """Return the Blake3-256 SAID and a copied dictionary containing it."""
    if label not in data:
        raise ValueError(f'Missing id field labeled "{label}"')

    # Work on a copy and reserve the final 44-character qualified SAID width.
    sad = copy.deepcopy(data)
    sad[label] = "#" * 44

    # Match JavaScript's compact JSON serialization and hash its UTF-8 bytes.
    serialized = json.dumps(
        sad, ensure_ascii=False, separators=(",", ":")
    ).encode("utf-8")
    digest = blake3(serialized).digest(length=32)

    # Qualify the unpadded base64url digest with the Blake3-256 code "E".

    # CESR qb64 encoding for Blake3-256
    raw = b"\x00" + digest
    encoded = base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")
    said = "E" + encoded[1:]

    sad[label] = said
    return said, sad


def py_verify(sad: dict, said: str, label: str = "d") -> bool:
    if label not in sad:
        raise ValueError(
            f"Cannot verify self addressing data without digest field {label}"
        )

    derived, _ = py_saidify(sad, label)

    return (
        compare_digest(derived, said)
        and compare_digest(sad[label], said)
    )


def py_saidify_urn(data: dict, label: str = "d") -> tuple[str, dict]:
    """
    Return a URN SAID and a SAD containing the URN.
    """
    urn_placeholder = "urn:said:" + ("#" * 44)

    sad = copy.deepcopy(data)
    sad[label] = urn_placeholder

    serialized = json.dumps(
        sad,
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode("utf-8")

    digest = blake3(serialized).digest(length=32)

    raw = b"\x00" + digest
    encoded = base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")

    urn = "urn:said:E" + encoded[1:]

    sad[label] = urn

    return urn, sad

def py_verify_urn(sad: dict, urn: str, label: str = "d") -> bool:
    derived, _ = py_saidify_urn(sad, label)
    return compare_digest(derived, urn)