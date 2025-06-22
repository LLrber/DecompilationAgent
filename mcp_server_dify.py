from typing import Dict, List, Optional, Any, Union
from fastmcp import FastMCP
from pydantic import BaseModel, Field
import json
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 配置模式定义
class ConfigSchema(BaseModel):
    debug: bool = Field(default=False, description="Enable debug logging")
    max_chunk_size: int = Field(default=600, description="Maximum chunk size for code analysis")

# 导入我们的分析工具
from src.tools.mcp_tools import (
    chunk_code, analyze_function, analyze_dependencies,
    generate_mermaid_chart, refactor_function, generate_report,
    search_code_tool, analyze_data_structures_tool, security_audit_tool, smart_assistant_tool
)

class ReverseCodeAnalyzerServer:
    def __init__(self, config: ConfigSchema):
        self.config = config
        self.analysis_history: List[Dict[str, Any]] = []
    
    def log_analysis(self, tool_name: str, result: Dict[str, Any]):
        """记录分析历史"""
        self.analysis_history.append({
            "tool": tool_name,
            "timestamp": "now",
            "result": result
        })

def create_reverse_code_analyzer_server(config: ConfigSchema = ConfigSchema()):
    """创建逆向代码分析MCP服务器"""
    mcp = FastMCP(name="Reverse Code Analyzer")
    
    # 创建分析服务器实例
    analyzer = ReverseCodeAnalyzerServer(config)
    
    @mcp.tool()
    def chunk_code_tool(
        file_path: str = Field(description="代码文件路径"),
        max_chunk_size: Optional[int] = Field(default=None, description="最大块大小，默认600行")
    ) -> Dict[str, Any]:
        """将长代码文件分块处理，解决大模型上下文限制"""
        try:
            if max_chunk_size is None:
                max_chunk_size = config.max_chunk_size
            
            result = chunk_code(file_path=file_path, max_chunk_size=max_chunk_size)
            analyzer.log_analysis("chunk_code", result)
            
            return {
                "content": [{
                    "type": "text", 
                    "text": json.dumps(result, ensure_ascii=False, indent=2)
                }]
            }
        except Exception as e:
            logger.error(f"代码分块错误: {e}")
            return {
                "content": [{
                    "type": "text",
                    "text": json.dumps({
                        "error": str(e),
                        "status": "failed"
                    }, ensure_ascii=False, indent=2)
                }],
                "is_error": True
            }
    
    @mcp.tool()
    def analyze_function_tool(
        function_code: str = Field(description="函数源代码"),
        function_name: str = Field(description="函数名称")
    ) -> Dict[str, Any]:
        """深度分析单个函数的结构、复杂度和潜在问题"""
        try:
            result = analyze_function(function_code=function_code, function_name=function_name)
            analyzer.log_analysis("analyze_function", result)
            
            return {
                "content": [{
                    "type": "text",
                    "text": json.dumps(result, ensure_ascii=False, indent=2)
                }]
            }
        except Exception as e:
            logger.error(f"函数分析错误: {e}")
            return {
                "content": [{
                    "type": "text",
                    "text": json.dumps({
                        "error": str(e),
                        "status": "failed"
                    }, ensure_ascii=False, indent=2)
                }],
                "is_error": True
            }
    
    @mcp.tool()
    def analyze_dependencies_tool(
        chunks_data: Dict[str, Any] = Field(description="代码块数据")
    ) -> Dict[str, Any]:
        """分析函数间的依赖关系和调用链"""
        try:
            result = analyze_dependencies(chunks_data=chunks_data)
            analyzer.log_analysis("analyze_dependencies", result)
            
            return {
                "content": [{
                    "type": "text",
                    "text": json.dumps(result, ensure_ascii=False, indent=2)
                }]
            }
        except Exception as e:
            logger.error(f"依赖分析错误: {e}")
            return {
                "content": [{
                    "type": "text",
                    "text": json.dumps({
                        "error": str(e),
                        "status": "failed"
                    }, ensure_ascii=False, indent=2)
                }],
                "is_error": True
            }
    
    @mcp.tool()
    def generate_mermaid_chart_tool(
        dependency_data: Dict[str, Any] = Field(description="依赖关系数据"),
        chart_type: str = Field(default="flowchart", description="图表类型"),
        max_nodes: Optional[int] = Field(default=20, description="最大节点数")
    ) -> Dict[str, Any]:
        """生成Mermaid格式的依赖关系图表"""
        try:
            result = generate_mermaid_chart(
                dependency_data=dependency_data,
                chart_type=chart_type,
                max_nodes=max_nodes
            )
            analyzer.log_analysis("generate_mermaid_chart", {"chart": result})
            
            return {
                "content": [{
                    "type": "text",
                    "text": result
                }]
            }
        except Exception as e:
            logger.error(f"图表生成错误: {e}")
            return {
                "content": [{
                    "type": "text",
                    "text": json.dumps({
                        "error": str(e),
                        "status": "failed"
                    }, ensure_ascii=False, indent=2)
                }],
                "is_error": True
            }
    
    @mcp.tool()
    def refactor_function_tool(
        function_code: str = Field(description="函数源代码"),
        function_name: str = Field(description="函数名称")
    ) -> Dict[str, Any]:
        """提供函数重构建议和优化方案"""
        try:
            result = refactor_function(function_code=function_code, function_name=function_name)
            analyzer.log_analysis("refactor_function", result)
            
            return {
                "content": [{
                    "type": "text",
                    "text": json.dumps(result, ensure_ascii=False, indent=2)
                }]
            }
        except Exception as e:
            logger.error(f"重构分析错误: {e}")
            return {
                "content": [{
                    "type": "text",
                    "text": json.dumps({
                        "error": str(e),
                        "status": "failed"
                    }, ensure_ascii=False, indent=2)
                }],
                "is_error": True
            }
    
    @mcp.tool()
    def generate_report_tool(
        file_path: str = Field(description="文件路径"),
        analysis_data: Dict[str, Any] = Field(description="分析数据")
    ) -> Dict[str, Any]:
        """生成综合分析报告"""
        try:
            result = generate_report(file_path=file_path, analysis_data=analysis_data)
            analyzer.log_analysis("generate_report", result)
            
            return {
                "content": [{
                    "type": "text",
                    "text": json.dumps(result, ensure_ascii=False, indent=2)
                }]
            }
        except Exception as e:
            logger.error(f"报告生成错误: {e}")
            return {
                "content": [{
                    "type": "text",
                    "text": json.dumps({
                        "error": str(e),
                        "status": "failed"
                    }, ensure_ascii=False, indent=2)
                }],
                "is_error": True
            }
    
    @mcp.tool()
    def search_code(
        file_path: str = Field(description="文件路径"),
        search_pattern: str = Field(description="搜索模式"),
        search_type: str = Field(default="function", description="搜索类型")
    ) -> Dict[str, Any]:
        """在代码中搜索特定模式或结构"""
        try:
            result = search_code_tool(
                file_path=file_path,
                search_pattern=search_pattern,
                search_type=search_type
            )
            analyzer.log_analysis("search_code", result)
            
            return {
                "content": [{
                    "type": "text",
                    "text": json.dumps(result, ensure_ascii=False, indent=2)
                }]
            }
        except Exception as e:
            logger.error(f"代码搜索错误: {e}")
            return {
                "content": [{
                    "type": "text",
                    "text": json.dumps({
                        "error": str(e),
                        "status": "failed"
                    }, ensure_ascii=False, indent=2)
                }],
                "is_error": True
            }
    
    @mcp.tool()
    def analyze_data_structures(
        file_path: str = Field(description="文件路径")
    ) -> Dict[str, Any]:
        """分析代码中的数据结构定义和使用"""
        try:
            result = analyze_data_structures_tool(file_path=file_path)
            analyzer.log_analysis("analyze_data_structures", result)
            
            return {
                "content": [{
                    "type": "text",
                    "text": json.dumps(result, ensure_ascii=False, indent=2)
                }]
            }
        except Exception as e:
            logger.error(f"数据结构分析错误: {e}")
            return {
                "content": [{
                    "type": "text",
                    "text": json.dumps({
                        "error": str(e),
                        "status": "failed"
                    }, ensure_ascii=False, indent=2)
                }],
                "is_error": True
            }
    
    @mcp.tool()
    def security_audit(
        file_path: str = Field(description="文件路径")
    ) -> Dict[str, Any]:
        """安全审计工具，检测潜在的安全问题"""
        try:
            result = security_audit_tool(file_path=file_path)
            analyzer.log_analysis("security_audit", result)
            
            return {
                "content": [{
                    "type": "text",
                    "text": json.dumps(result, ensure_ascii=False, indent=2)
                }]
            }
        except Exception as e:
            logger.error(f"安全审计错误: {e}")
            return {
                "content": [{
                    "type": "text",
                    "text": json.dumps({
                        "error": str(e),
                        "status": "failed"
                    }, ensure_ascii=False, indent=2)
                }],
                "is_error": True
            }
    
    @mcp.tool()
    def smart_assistant(
        context: str = Field(default="", description="上下文信息")
    ) -> Dict[str, Any]:
        """智能分析助手，基于历史记录提供个性化建议"""
        try:
            result = smart_assistant_tool(context=context)
            # 添加历史分析信息
            result["analysis_history_count"] = len(analyzer.analysis_history)
            analyzer.log_analysis("smart_assistant", result)
            
            return {
                "content": [{
                    "type": "text",
                    "text": json.dumps(result, ensure_ascii=False, indent=2)
                }]
            }
        except Exception as e:
            logger.error(f"智能助手错误: {e}")
            return {
                "content": [{
                    "type": "text",
                    "text": json.dumps({
                        "error": str(e),
                        "status": "failed"
                    }, ensure_ascii=False, indent=2)
                }],
                "is_error": True
            }
    
    return mcp

# 主函数
if __name__ == "__main__":
    # 创建配置
    config = ConfigSchema(debug=True, max_chunk_size=600)
    
    # 创建服务器
    server = create_reverse_code_analyzer_server(config)
    
    logger.info("启动Dify优化的逆向代码分析MCP服务器...")
    logger.info("服务器地址: http://0.0.0.0:382")
    logger.info("传输方式: SSE")
    
    # 运行服务器
    server.run(transport='sse', host="0.0.0.0", port=382) 