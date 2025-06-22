"""
应用程序设置

集中管理所有配置参数。
"""

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class Settings:
    """应用程序设置"""
    
    # 服务器设置
    server_name: str = "reverse-code-analyzer"
    description: str = "逆向代码分析工具 - 专门用于分析反编译得到的C代码"
    
    # 文件路径设置
    input_dir: str = "input"
    output_dir: str = "output"
    logs_dir: str = "logs"
    
    # 分析设置
    max_chunk_size: int = 600
    max_nodes: int = 20
    
    # 传输设置
    transport: str = "stdio"  # stdio, http, sse
    
    # HTTP设置
    http_host: str = "0.0.0.0"
    http_port: int = 382
    
    # SSE设置
    sse_host: str = "0.0.0.0"
    sse_port: int = 8001
    
    # 日志设置
    log_level: str = "INFO"
    log_file: str = "logs/app.log"
    
    # 调试设置
    debug: bool = False
    
    @classmethod
    def from_env(cls) -> 'Settings':
        """从环境变量创建设置"""
        return cls(
            server_name=os.getenv("SERVER_NAME", "reverse-code-analyzer"),
            description=os.getenv("DESCRIPTION", "逆向代码分析工具"),
            input_dir=os.getenv("INPUT_DIR", "input"),
            output_dir=os.getenv("OUTPUT_DIR", "output"),
            logs_dir=os.getenv("LOGS_DIR", "logs"),
            max_chunk_size=int(os.getenv("MAX_CHUNK_SIZE", "600")),
            max_nodes=int(os.getenv("MAX_NODES", "20")),
            transport=os.getenv("TRANSPORT", "stdio"),
            http_host=os.getenv("HTTP_HOST", "0.0.0.0"),
            http_port=int(os.getenv("HTTP_PORT", "382")),
            sse_host=os.getenv("SSE_HOST", "0.0.0.0"),
            sse_port=int(os.getenv("SSE_PORT", "8001")),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            log_file=os.getenv("LOG_FILE", "logs/app.log"),
            debug=os.getenv("DEBUG", "false").lower() == "true"
        )


# 全局设置实例
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """获取全局设置实例"""
    global _settings
    if _settings is None:
        _settings = Settings.from_env()
    return _settings 