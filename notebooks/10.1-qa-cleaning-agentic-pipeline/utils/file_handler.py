import json
import os


def load_input(path: str) -> list:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_output(data: list, path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
