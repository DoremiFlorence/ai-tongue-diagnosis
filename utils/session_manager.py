"""会话管理模块。"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

from config.settings import SESSIONS_DIR
from models.schemas import SessionSchema


def generate_session_id() -> str:
    """生成唯一会话 ID。"""
    return f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"


def save_session(session: SessionSchema) -> None:
    """保存会话到本地。

    Args:
        session: 会话数据
    """
    session.updated_at = datetime.now()
    file_path = SESSIONS_DIR / f"{session.session_id}.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(session.model_dump(mode="json"), f, ensure_ascii=False, indent=2, default=str)


def load_session(session_id: str) -> Optional[SessionSchema]:
    """加载会话。

    Args:
        session_id: 会话 ID

    Returns:
        会话数据，不存在则返回 None
    """
    file_path = SESSIONS_DIR / f"{session_id}.json"
    if not file_path.exists():
        return None

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return SessionSchema(**data)


def list_sessions() -> list[dict]:
    """列出所有会话。

    Returns:
        会话列表，包含基本信息
    """
    sessions = []
    for file_path in sorted(SESSIONS_DIR.glob("*.json"), reverse=True):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            sessions.append({
                "session_id": data["session_id"],
                "created_at": data["created_at"],
                "has_diagnosis": bool(data.get("final_diagnosis")),
            })
        except (json.JSONDecodeError, KeyError):
            continue
    return sessions


def delete_session(session_id: str) -> bool:
    """删除会话。

    Args:
        session_id: 会话 ID

    Returns:
        是否删除成功
    """
    file_path = SESSIONS_DIR / f"{session_id}.json"
    if file_path.exists():
        file_path.unlink()
        return True
    return False
