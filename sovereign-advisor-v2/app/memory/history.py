import json
import os
from pathlib import Path
from typing import Dict, List

HISTORY_PATH = Path(os.getenv("HISTORY_PATH", "data/history/chat_history.json"))
HISTORY_PATH.parent.mkdir(parents=True, exist_ok=True)
if not HISTORY_PATH.exists():
    HISTORY_PATH.write_text(json.dumps({}))


def _load() -> Dict:
    return json.loads(HISTORY_PATH.read_text() or "{}")


def _save(data: Dict) -> None:
    HISTORY_PATH.write_text(json.dumps(data, indent=2))


def append_message(thread_id: str, role: str, content: str, metadata: Dict | None = None) -> None:
    data = _load()
    data.setdefault(thread_id, [])
    item = {"role": role, "content": content}
    if metadata:
        item["metadata"] = metadata
    data[thread_id].append(item)
    _save(data)


def get_thread_messages(thread_id: str) -> List[Dict]:
    return _load().get(thread_id, [])


def list_threads() -> List[str]:
    return list(_load().keys())
