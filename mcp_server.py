#!/usr/bin/env python3
"""
Reverse Code Analysis MCP Server
逆向代码分析MCP服务器 - 重构版本
"""

import argparse
import logging
from typing import Dict, Any

try:
    from fastmcp import FastMCP
except ImportError:
    print("需要安装fastmcp: pip install fastmcp")
    exit(1)

from src.config.settings import get_settings
from src.utils.helpers import setup_logging, ensure_directories
from src.tools.mcp_tools import (
    chunk_code,
    analyze_function,
    analyze_dependencies,
    generate_mermaid_chart,
    refactor_function,
    generate_report,
    search_code_tool,
    analyze_data_structures_tool,
    security_audit_tool,
    smart_assistant_tool
)

# 获取设置
settings = get_settings()

# 设置日志
setup_logging(settings)
logger = logging.getLogger(__name__)

# 确保必要目录存在
ensure_directories([
    settings.input_dir,
    settings.output_dir,
    settings.logs_dir
])

# 初始化MCP服务器
mcp = FastMCP(settings.server_name)

# 注册工具函数
@mcp.tool()
def chunk_code_tool(file_path: str, max_chunk_size: int = None) -> Dict[str, Any]:
    """
    将长代码文件分块处理，解决大模型上下文限制
    
    Args:
        file_path: 代码文件路径
        max_chunk_size: 最大块大小（行数）
    """
    if max_chunk_size is None:
        max_chunk_size = settings.max_chunk_size
    return chunk_code(file_path, max_chunk_size)


@mcp.tool()
def analyze_function_tool(function_code: str, function_name: str) -> Dict[str, Any]:
    """
    深度分析单个函数
    
    Args:
        function_code: 函数代码
        function_name: 函数名
    """
    return analyze_function(function_code, function_name)


@mcp.tool()
def analyze_dependencies_tool(chunks_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    分析函数间依赖关系
    
    Args:
        chunks_data: 从chunk_code返回的数据
    """
    return analyze_dependencies(chunks_data)


@mcp.tool()
def generate_mermaid_chart_tool(dependency_data: Dict[str, Any], chart_type: str = "flowchart", max_nodes: int = None) -> str:
    """
    生成Mermaid图表
    
    Args:
        dependency_data: 依赖分析数据
        chart_type: 图表类型 ("flowchart" | "graph" | "mindmap")
        max_nodes: 最大节点数
    """
    if max_nodes is None:
        max_nodes = settings.max_nodes
    return generate_mermaid_chart(dependency_data, chart_type, max_nodes)


@mcp.tool()
def refactor_function_tool(function_code: str, function_name: str) -> Dict[str, Any]:
    """
    提供函数重构建议
    
    Args:
        function_code: 函数代码
        function_name: 函数名
    """
    return refactor_function(function_code, function_name)


@mcp.tool()
def generate_report_tool(file_path: str, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    生成综合分析报告
    
    Args:
        file_path: 文件路径
        analysis_data: 分析数据
    """
    return generate_report(file_path, analysis_data)


@mcp.tool()
def search_code(file_path: str, search_pattern: str, search_type: str = "function") -> Dict[str, Any]:
    """
    在代码中搜索特定模式
    
    Args:
        file_path: 代码文件路径
        search_pattern: 搜索模式（函数名、变量名、字符串等）
        search_type: 搜索类型 ("function", "variable", "string", "regex")
    """
    return search_code_tool(file_path, search_pattern, search_type)


@mcp.tool()
def analyze_data_structures(file_path: str) -> Dict[str, Any]:
    """
    分析代码中的数据结构
    
    Args:
        file_path: 代码文件路径
    """
    return analyze_data_structures_tool(file_path)


@mcp.tool()
def security_audit(file_path: str) -> Dict[str, Any]:
    """
    安全审计工具，检测潜在的安全问题
    
    Args:
        file_path: 代码文件路径
    """
    return security_audit_tool(file_path)


@mcp.tool()
def smart_assistant(context: str = "") -> Dict[str, Any]:
    """
    智能分析助手，基于历史记录提供个性化建议
    
    Args:
        context: 用户提供的上下文信息
    """
    return smart_assistant_tool(context)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="逆向代码分析MCP服务器")
    parser.add_argument(
        "--transport", 
        choices=["stdio", "http", "sse"], 
        default=settings.transport,
        help="通信方式"
    )
    parser.add_argument("--host", default=settings.http_host, help="主机地址")
    parser.add_argument("--port", type=int, help="端口号（如果不指定，HTTP使用382，SSE使用8001）")
    parser.add_argument("--debug", action="store_true", help="启用调试模式")
    
    args = parser.parse_args()
    
    # 更新设置
    settings.transport = args.transport
    settings.debug = args.debug
    
    # 根据传输方式确定端口
    if args.port is not None:
        # 用户指定了端口
        if settings.transport == "sse":
            settings.sse_port = args.port
        else:
            settings.http_port = args.port
    # 如果用户没有指定端口，使用默认值（HTTP: 382, SSE: 8001）
    
    logger.info(f"启动 {settings.server_name} - 传输方式: {settings.transport}")
    
    if settings.transport == "stdio":
        # stdio模式 - 用于MCP标准协议
        logger.info("使用stdio模式启动MCP服务器")
        mcp.run()
        
    elif settings.transport == "http":
        # HTTP模式 - 符合MCP协议的HTTP服务器
        from fastapi import FastAPI, Request, HTTPException
        from fastapi.middleware.cors import CORSMiddleware
        import uvicorn
        import json
        
        app = FastAPI(
            title=settings.server_name,
            description=settings.description,
            version="1.0.0"
        )
        
        # 添加CORS支持
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # MCP协议处理器
        async def handle_mcp_request(request_data: dict) -> dict:
            """处理MCP协议请求"""
            method = request_data.get("method")
            params = request_data.get("params", {})
            request_id = request_data.get("id", None)  # 确保id有默认值
            
            try:
                if method == "initialize":
                    return {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": {
                            "protocolVersion": "2024-11-05",
                            "capabilities": {
                                "tools": {}
                            },
                            "serverInfo": {
                                "name": settings.server_name,
                                "version": "1.0.0"
                            }
                        }
                    }
                
                elif method == "tools/list":
                    tools = [
                        {
                            "name": "chunk_code_tool",
                            "description": "将长代码文件分块处理，解决大模型上下文限制",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "file_path": {"type": "string"},
                                    "max_chunk_size": {"type": "integer", "default": 2000}
                                },
                                "required": ["file_path"]
                            }
                        },
                        {
                            "name": "analyze_function_tool",
                            "description": "深度分析单个函数",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "function_code": {"type": "string"},
                                    "function_name": {"type": "string"}
                                },
                                "required": ["function_code", "function_name"]
                            }
                        },
                        {
                            "name": "analyze_dependencies_tool",
                            "description": "分析函数间依赖关系",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "chunks_data": {"type": "object"}
                                },
                                "required": ["chunks_data"]
                            }
                        },
                        {
                            "name": "generate_mermaid_chart_tool",
                            "description": "生成Mermaid图表",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "dependency_data": {"type": "object"},
                                    "chart_type": {"type": "string", "default": "flowchart"},
                                    "max_nodes": {"type": "integer", "default": 20}
                                },
                                "required": ["dependency_data"]
                            }
                        },
                        {
                            "name": "refactor_function_tool",
                            "description": "提供函数重构建议",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "function_code": {"type": "string"},
                                    "function_name": {"type": "string"}
                                },
                                "required": ["function_code", "function_name"]
                            }
                        },
                        {
                            "name": "generate_report_tool",
                            "description": "生成综合分析报告",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "file_path": {"type": "string"},
                                    "analysis_data": {"type": "object"}
                                },
                                "required": ["file_path", "analysis_data"]
                            }
                        },
                        {
                            "name": "search_code",
                            "description": "在代码中搜索特定模式",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "file_path": {"type": "string"},
                                    "search_pattern": {"type": "string"},
                                    "search_type": {"type": "string", "default": "function"}
                                },
                                "required": ["file_path", "search_pattern"]
                            }
                        },
                        {
                            "name": "analyze_data_structures",
                            "description": "分析代码中的数据结构",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "file_path": {"type": "string"}
                                },
                                "required": ["file_path"]
                            }
                        },
                        {
                            "name": "security_audit",
                            "description": "安全审计工具，检测潜在的安全问题",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "file_path": {"type": "string"}
                                },
                                "required": ["file_path"]
                            }
                        },
                        {
                            "name": "smart_assistant",
                            "description": "智能分析助手，基于历史记录提供个性化建议",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "context": {"type": "string", "default": ""}
                                },
                                "required": []
                            }
                        }
                    ]
                    
                    return {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": {
                            "tools": tools
                        }
                    }
                
                elif method == "notifications/initialized":
                    # 处理初始化通知 - 这是一个通知，不需要响应
                    logger.info("收到初始化通知")
                    return None  # 通知不需要响应
                
                elif method == "tools/call":
                    tool_name = params.get("name")
                    arguments = params.get("arguments", {})
                    
                    # 工具路由 - 调用原始函数而不是装饰器函数
                    if tool_name == "chunk_code_tool":
                        result = chunk_code(**arguments)
                    elif tool_name == "analyze_function_tool":
                        result = analyze_function(**arguments)
                    elif tool_name == "analyze_dependencies_tool":
                        result = analyze_dependencies(**arguments)
                    elif tool_name == "generate_mermaid_chart_tool":
                        result = generate_mermaid_chart(**arguments)
                    elif tool_name == "refactor_function_tool":
                        result = refactor_function(**arguments)
                    elif tool_name == "generate_report_tool":
                        result = generate_report(**arguments)
                    elif tool_name == "search_code":
                        result = search_code_tool(**arguments)
                    elif tool_name == "analyze_data_structures":
                        result = analyze_data_structures_tool(**arguments)
                    elif tool_name == "security_audit":
                        result = security_audit_tool(**arguments)
                    elif tool_name == "smart_assistant":
                        result = smart_assistant_tool(**arguments)
                    else:
                        raise ValueError(f"未知工具: {tool_name}")
                    
                    return {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": {
                            "content": [
                                {
                                    "type": "text",
                                    "text": json.dumps(result, ensure_ascii=False, indent=2)
                                }
                            ]
                        }
                    }
                
                else:
                    raise ValueError(f"未知方法: {method}")
                    
            except Exception as e:
                logger.error(f"MCP请求处理错误: {e}")
                # 确保request_id在异常情况下也有值
                error_id = request_id if 'request_id' in locals() else None
                return {
                    "jsonrpc": "2.0",
                    "id": error_id,
                    "error": {
                        "code": -32603,
                        "message": str(e)
                    }
                }
        
        @app.post("/")
        async def mcp_endpoint(request: Request):
            """MCP协议主端点"""
            request_id = None
            try:
                request_data = await request.json()
                request_id = request_data.get("id", None)  # 提取请求ID
                logger.info(f"收到MCP请求: {request_data.get('method', 'unknown')}")
                response = await handle_mcp_request(request_data)
                
                # 如果是通知类型的消息，返回空响应
                if response is None:
                    return {"status": "ok"}
                
                return response
            except Exception as e:
                logger.error(f"MCP端点错误: {e}")
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,  # 包含请求ID，解析错误时为None
                    "error": {
                        "code": -32700,
                        "message": "Parse error"
                    }
                }
        
        @app.get("/")
        async def root():
            return {
                "name": settings.server_name,
                "description": settings.description,
                "version": "1.0.0",
                "transport": "http",
                "protocol": "MCP"
            }
        
        logger.info(f"MCP HTTP服务器启动在 http://{args.host}:{args.port}")
        uvicorn.run(app, host=args.host, port=args.port)
        
    elif settings.transport == "sse":
        # SSE模式 - Server-Sent Events
        from fastapi import FastAPI, Request
        from fastapi.responses import StreamingResponse
        import uvicorn
        import json
        import asyncio
        
        app = FastAPI(
            title=f"{settings.server_name} SSE",
            description=f"{settings.description} - SSE模式",
            version="1.0.0"
        )
        
        @app.get("/")
        async def root():
            return {
                "name": settings.server_name,
                "description": settings.description,
                "version": "1.0.0",
                "transport": "sse"
            }
        
        @app.get("/sse")
        async def sse_endpoint():
            """标准SSE端点 - 用于浏览器和通用SSE客户端"""
            async def event_stream():
                while True:
                    # 这里可以实现实时数据推送
                    data = {
                        "type": "heartbeat",
                        "timestamp": "now",
                        "status": "running"
                    }
                    yield f"data: {json.dumps(data)}\n\n"
                    await asyncio.sleep(30)
            
            return StreamingResponse(
                event_stream(),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET",
                    "Access-Control-Allow-Headers": "Cache-Control"
                }
            )
        
        # 创建MCP请求处理函数（重用HTTP模式的逻辑）
        async def handle_mcp_request_sse(request_data: dict) -> dict:
            """处理MCP请求 - SSE模式"""
            try:
                method = request_data.get("method")
                params = request_data.get("params", {})
                request_id = request_data.get("id", None)  # 确保id有默认值
                
                if method == "initialize":
                    return {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": {
                            "protocolVersion": "2024-11-05",
                            "capabilities": {
                                "tools": {}
                            },
                            "serverInfo": {
                                "name": settings.server_name,
                                "version": "1.0.0"
                            }
                        }
                    }
                
                elif method == "tools/list":
                    # 返回工具列表（与HTTP模式相同）
                    tools = [
                        {
                            "name": "chunk_code_tool",
                            "description": "将长代码文件分块处理，解决大模型上下文限制",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "file_path": {"type": "string"},
                                    "max_chunk_size": {"type": "integer", "default": settings.max_chunk_size}
                                },
                                "required": ["file_path"]
                            }
                        },
                        {
                            "name": "analyze_function_tool",
                            "description": "深度分析单个函数",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "function_code": {"type": "string"},
                                    "function_name": {"type": "string"}
                                },
                                "required": ["function_code", "function_name"]
                            }
                        }
                        # 可以添加更多工具...
                    ]
                    
                    return {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": {
                            "tools": tools
                        }
                    }
                
                elif method == "notifications/initialized":
                    # 处理初始化通知 - 这是一个通知，不需要响应
                    logger.info("收到SSE初始化通知")
                    return None  # 通知不需要响应
                
                elif method == "tools/call":
                    tool_name = params.get("name")
                    arguments = params.get("arguments", {})
                    
                    # 工具路由
                    if tool_name == "chunk_code_tool":
                        result = chunk_code(**arguments)
                    elif tool_name == "analyze_function_tool":
                        result = analyze_function(**arguments)
                    else:
                        raise ValueError(f"未知工具: {tool_name}")
                    
                    return {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": {
                            "content": [
                                {
                                    "type": "text",
                                    "text": json.dumps(result, ensure_ascii=False, indent=2)
                                }
                            ]
                        }
                    }
                
                else:
                    raise ValueError(f"未知方法: {method}")
                    
            except Exception as e:
                logger.error(f"MCP SSE请求处理错误: {e}")
                # 确保request_id在异常情况下也有值
                error_id = request_id if 'request_id' in locals() else None
                return {
                    "jsonrpc": "2.0",
                    "id": error_id,
                    "error": {
                        "code": -32603,
                        "message": str(e)
                    }
                }
        
        @app.post("/mcp")
        async def mcp_sse_post_endpoint(request: Request):
            """MCP SSE模式的POST端点 - 处理工具调用"""
            request_id = None
            try:
                request_data = await request.json()
                request_id = request_data.get("id", None)  # 提取请求ID
                logger.info(f"收到MCP SSE请求: {request_data.get('method', 'unknown')}")
                response = await handle_mcp_request_sse(request_data)
                
                # 如果是通知类型的消息，返回空响应
                if response is None:
                    return {"status": "ok"}
                
                return response
            except Exception as e:
                logger.error(f"MCP SSE端点错误: {e}")
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,  # 包含请求ID，解析错误时为None
                    "error": {
                        "code": -32700,
                        "message": "Parse error"
                    }
                }
        
        @app.get("/mcp")
        async def mcp_sse_endpoint():
            """MCP专用SSE端点 - 符合MCP协议的SSE实现"""
            async def mcp_event_stream():
                # 发送初始化消息
                init_message = {
                    "jsonrpc": "2.0",
                    "method": "notifications/initialized",
                    "params": {
                        "protocolVersion": "2024-11-05",
                        "serverInfo": {
                            "name": settings.server_name,
                            "version": "1.0.0"
                        }
                    }
                }
                yield f"data: {json.dumps(init_message)}\n\n"
                
                # 持续发送心跳
                while True:
                    heartbeat = {
                        "jsonrpc": "2.0",
                        "method": "notifications/progress",
                        "params": {
                            "progressToken": "heartbeat",
                            "value": {
                                "kind": "report",
                                "message": "Server running",
                                "percentage": 100
                            }
                        }
                    }
                    yield f"data: {json.dumps(heartbeat)}\n\n"
                    await asyncio.sleep(30)
            
            return StreamingResponse(
                mcp_event_stream(),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET, POST",
                    "Access-Control-Allow-Headers": "Content-Type, Cache-Control"
                }
            )
        
        logger.info(f"SSE服务器启动在 http://{args.host}:{settings.sse_port}")
        uvicorn.run(app, host=args.host, port=settings.sse_port)


if __name__ == "__main__":
    main() 