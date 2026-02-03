"""图片处理工具模块。"""

import base64
import io
from typing import Tuple

from PIL import Image

from config.settings import MAX_IMAGE_SIZE


def compress_image(image_bytes: bytes, max_size: Tuple[int, int] = MAX_IMAGE_SIZE) -> bytes:
    """压缩图片到指定尺寸。

    Args:
        image_bytes: 原始图片字节
        max_size: 最大尺寸 (宽, 高)

    Returns:
        压缩后的图片字节 (JPEG 格式)
    """
    image = Image.open(io.BytesIO(image_bytes))

    if image.mode in ("RGBA", "P"):
        image = image.convert("RGB")

    image.thumbnail(max_size, Image.Resampling.LANCZOS)

    output = io.BytesIO()
    image.save(output, format="JPEG", quality=85, optimize=True)
    return output.getvalue()


def image_to_base64(image_bytes: bytes, compress: bool = True) -> str:
    """将图片转换为 base64 编码。

    Args:
        image_bytes: 图片字节
        compress: 是否压缩图片

    Returns:
        base64 编码的图片字符串
    """
    if compress:
        image_bytes = compress_image(image_bytes)

    return base64.b64encode(image_bytes).decode("utf-8")


def validate_image(image_bytes: bytes) -> bool:
    """验证图片是否有效。

    Args:
        image_bytes: 图片字节

    Returns:
        图片是否有效
    """
    try:
        image = Image.open(io.BytesIO(image_bytes))
        image.verify()
        return True
    except Exception:
        return False
