"""应用配置管理模块。"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# 项目路径
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
SESSIONS_DIR = DATA_DIR / "sessions"

# 确保目录存在
SESSIONS_DIR.mkdir(parents=True, exist_ok=True)

# SiliconFlow API 配置
SILICONFLOW_API_KEY = os.getenv("SILICONFLOW_API_KEY", "")
SILICONFLOW_BASE_URL = os.getenv("SILICONFLOW_BASE_URL", "https://api.siliconflow.cn/v1")
CHAT_COMPLETIONS_ENDPOINT = f"{SILICONFLOW_BASE_URL}/chat/completions"

# 模型配置
VISION_MODEL = os.getenv("VISION_MODEL", "Qwen/Qwen2-VL-72B-Instruct")
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "2048"))
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))

# 图片配置
MAX_IMAGE_SIZE = (1024, 1024)
SUPPORTED_IMAGE_TYPES = ["jpg", "jpeg", "png", "webp"]
