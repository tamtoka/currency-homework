import json
from pathlib import Path
from tempfile import NamedTemporaryFile
from time import time


CACHE_PATH = "currency_rate.json"
CACHE_LIFETIME = 24 * 60 * 60


def save_to_file(data: dict, path=CACHE_PATH) -> None:
    target = Path(path)
    temp_path = None
    try:
        with NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=target.parent, delete=False
        ) as file:
            temp_path = Path(file.name)
            json.dump(data, file, ensure_ascii=False, indent=4)
            file.write("\n")
        temp_path.replace(target)
    finally:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)


def read_from_file(path) -> dict:
    with Path(path).open(encoding="utf-8") as file:
        data = json.load(file)
    if not isinstance(data, dict):
        raise ValueError("Ожидался JSON-объект.")
    return data


def read_fresh_rates(base: str, path=CACHE_PATH) -> dict | None:
    try:
        age = time() - Path(path).stat().st_mtime
        if not 0 <= age < CACHE_LIFETIME:
            return None
        data = read_from_file(path)
    except (OSError, ValueError):
        return None

    if data.get("base_code") == base and isinstance(data.get("rates"), dict):
        return data
    return None
