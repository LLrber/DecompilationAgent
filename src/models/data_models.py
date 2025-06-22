"""
数据模型定义

定义代码分析过程中使用的数据结构。
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional


@dataclass
class FunctionInfo:
    """函数信息数据模型"""
    name: str
    signature: str
    start_line: int
    end_line: int
    code: str
    calls: List[str]
    complexity: int


@dataclass
class ChunkInfo:
    """代码块信息"""
    id: str
    functions: List[Dict[str, Any]]
    size: int


@dataclass
class AnalysisResult:
    """分析结果数据模型"""
    total_chunks: int
    chunks: List[ChunkInfo]
    file_info: Dict[str, Any]


@dataclass
class DependencyInfo:
    """依赖关系信息"""
    caller: str
    callee: str
    call_count: int


@dataclass
class SecurityRisk:
    """安全风险信息"""
    level: str  # 'high', 'medium', 'low'
    description: str
    line_number: int
    suggestion: str 