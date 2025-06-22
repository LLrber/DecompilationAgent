"""
辅助工具函数

包含各种通用的辅助函数。
"""

import os
import logging
from pathlib import Path
from typing import List

from ..config.settings import Settings


def setup_logging(settings: Settings) -> None:
    """设置日志配置"""
    
    # 确保日志目录存在
    log_dir = Path(settings.log_file).parent
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # 配置日志格式
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # 配置日志级别
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)
    
    # 基本配置
    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=[
            logging.FileHandler(settings.log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    # 设置第三方库日志级别
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("fastapi").setLevel(logging.WARNING)


def ensure_directories(directories: List[str]) -> None:
    """确保目录存在"""
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)


def clean_function_name(name: str) -> str:
    """清理函数名用于图表显示"""
    import re
    return re.sub(r'[^a-zA-Z0-9_]', '_', name)


def get_file_info(file_path: str) -> dict:
    """获取文件信息"""
    if not os.path.exists(file_path):
        return {"error": "文件不存在"}
    
    stat = os.stat(file_path)
    return {
        "path": file_path,
        "size": stat.st_size,
        "modified": stat.st_mtime,
        "exists": True
    }