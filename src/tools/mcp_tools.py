"""
MCP工具函数实现

包含所有用于代码分析的MCP工具函数。
"""

import re
import os
from typing import Dict, List, Any, Tuple
from dataclasses import asdict
from collections import defaultdict

from ..core.analyzer import CodeAnalyzer
from ..models.data_models import FunctionInfo

# 创建全局分析器实例
analyzer = CodeAnalyzer()

# 全局分析历史记录（用于智能推荐）
analysis_history = []

def add_to_history(tool_name: str, result: Dict[str, Any]):
    """添加分析历史记录"""
    analysis_history.append({
        "tool": tool_name,
        "timestamp": __import__('time').time(),
        "result": result
    })
    # 保持最近50条记录
    if len(analysis_history) > 50:
        analysis_history.pop(0)

def get_smart_recommendations(current_tool: str, current_result: Dict[str, Any]) -> Dict[str, Any]:
    """生成智能推荐"""
    recommendations = []
    suggested_inputs = []
    
    if current_tool == "chunk_code_tool":
        if current_result.get("total_functions", 0) > 0:
            recommendations.extend([
                ("analyze_dependencies_tool", "分析函数间的调用关系和依赖"),
                ("search_code_tool", "搜索特定的函数或关键词"),
                ("security_audit_tool", "检测潜在的安全问题")
            ])
            suggested_inputs.extend([
                "分析依赖关系",
                "搜索 modbus",
                "安全审计",
                f"分析函数 {current_result.get('chunks', [{}])[0].get('functions', [{}])[0].get('name', '函数名')}"
            ])
    
    elif current_tool == "analyze_function_tool":
        func_name = current_result.get("function_name", "")
        if current_result.get("security_concerns"):
            recommendations.append(("security_audit_tool", "深入分析安全问题"))
        if current_result.get("complexity_indicators", {}).get("line_count", 0) > 50:
            recommendations.append(("refactor_function_tool", "获取重构建议"))
        recommendations.extend([
            ("search_code_tool", f"搜索调用 {func_name} 的其他位置"),
            ("analyze_data_structures_tool", "分析相关的数据结构")
        ])
        suggested_inputs.extend([
            f"搜索 {func_name}",
            "分析数据结构",
            "重构建议"
        ])
    
    elif current_tool == "analyze_dependencies_tool":
        critical_funcs = [node["name"] for node in current_result.get("dependency_nodes", []) 
                         if node.get("importance_score", 0) > 7]
        if critical_funcs:
            recommendations.append(("analyze_function_tool", f"深入分析关键函数: {', '.join(critical_funcs[:3])}"))
            for func in critical_funcs[:3]:
                suggested_inputs.append(f"分析函数 {func}")
        recommendations.extend([
            ("generate_mermaid_chart_tool", "生成可视化依赖图"),
            ("security_audit_tool", "检测整体安全问题")
        ])
        suggested_inputs.extend([
            "生成依赖图",
            "安全审计"
        ])
    
    elif current_tool == "search_code_tool":
        results = current_result.get("results", [])
        if results:
            func_names = [r.get("function_name") for r in results if r.get("function_name")]
            if func_names:
                recommendations.append(("analyze_function_tool", f"分析搜索到的函数"))
                for func in func_names[:3]:
                    suggested_inputs.append(f"分析函数 {func}")
        recommendations.extend([
            ("analyze_data_structures_tool", "分析相关数据结构"),
            ("security_audit_tool", "安全审计")
        ])
    
    elif current_tool == "security_audit_tool":
        issues = current_result.get("security_issues", [])
        if issues:
            recommendations.extend([
                ("refactor_function_tool", "获取修复建议"),
                ("search_code_tool", "搜索相似的安全问题")
            ])
            suggested_inputs.extend([
                "重构建议",
                "搜索 strcpy",
                "搜索 malloc"
            ])
    
    elif current_tool == "analyze_data_structures_tool":
        structs = current_result.get("structures", [])
        if structs:
            recommendations.extend([
                ("search_code_tool", "搜索结构体的使用位置"),
                ("security_audit_tool", "检查结构体相关的安全问题")
            ])
            for struct in structs[:3]:
                suggested_inputs.append(f"搜索 {struct.get('name', '')}")
    
    # 通用推荐
    recommendations.append(("smart_assistant_tool", "获取个性化分析建议"))
    suggested_inputs.append("智能助手")
    
    return {
        "recommendations": recommendations,
        "suggested_inputs": suggested_inputs,
        "analysis_tips": [
            "💡 使用'搜索'命令快速定位关键代码",
            "🔍 使用'分析函数'深入理解具体实现",
            "🛡️ 使用'安全审计'发现潜在问题",
            "📊 使用'生成依赖图'可视化代码结构"
        ]
    }


def chunk_code(file_path: str, max_chunk_size: int = 2000) -> Dict[str, Any]:
    """
    将长代码文件分块处理，解决大模型上下文限制
    
    Args:
        file_path: 代码文件路径
        max_chunk_size: 最大块大小（行数）
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return {"error": f"无法读取文件: {str(e)}"}
    
    functions = analyzer.extract_functions(content)
    
    chunks = []
    current_chunk = []
    current_size = 0
    
    for func in functions:
        func_size = func.end_line - func.start_line
        
        if current_size + func_size > max_chunk_size and current_chunk:
            chunks.append({
                "id": f"chunk_{len(chunks)}",
                "functions": [asdict(f) for f in current_chunk],
                "size": current_size
            })
            current_chunk = [func]
            current_size = func_size
        else:
            current_chunk.append(func)
            current_size += func_size
    
    if current_chunk:
        chunks.append({
            "id": f"chunk_{len(chunks)}",
            "functions": [asdict(f) for f in current_chunk],
            "size": current_size
        })
    
    result = {
        "total_chunks": len(chunks),
        "chunks": chunks,
        "file_info": {
            "path": file_path,
            "total_lines": len(content.split('\n')),
            "total_functions": len(functions)
        }
    }
    
    # 添加到历史记录并生成推荐
    add_to_history("chunk_code_tool", result)
    result["smart_recommendations"] = get_smart_recommendations("chunk_code_tool", result)
    
    return result


def analyze_function(function_code: str, function_name: str) -> Dict[str, Any]:
    """
    深度分析单个函数
    
    Args:
        function_code: 函数代码
        function_name: 函数名
    """
    
    lines = function_code.split('\n')
    complexity_indicators = {
        'loops': len(re.findall(r'\b(for|while|do)\b', function_code)),
        'conditions': len(re.findall(r'\b(if|else|switch)\b', function_code)),
        'function_calls': len(re.findall(r'\w+\s*\(', function_code)),
        'line_count': len([l for l in lines if l.strip()]),
        'nested_blocks': function_code.count('{')
    }
    
    # 用途推断
    purpose_hints = []
    name_lower = function_name.lower()
    
    if any(word in name_lower for word in ['init', 'initialize', 'setup', 'create']):
        purpose_hints.append("初始化函数")
    if any(word in name_lower for word in ['free', 'destroy', 'cleanup', 'close']):
        purpose_hints.append("资源释放函数")
    if any(word in name_lower for word in ['get', 'read', 'fetch']):
        purpose_hints.append("数据获取函数")
    if any(word in name_lower for word in ['set', 'write', 'store']):
        purpose_hints.append("数据设置函数")
    if any(word in name_lower for word in ['send', 'recv', 'transmit']):
        purpose_hints.append("网络通信函数")
    if 'modbus' in name_lower:
        purpose_hints.append("Modbus协议函数")
    if 'tcp' in name_lower:
        purpose_hints.append("TCP网络函数")
    if 'rtu' in name_lower:
        purpose_hints.append("RTU串口函数")
    
    # 错误处理分析
    error_handling = []
    if 'return -1' in function_code or 'return NULL' in function_code:
        error_handling.append("包含错误返回值")
    if 'errno' in function_code:
        error_handling.append("使用errno错误处理")
    if re.search(r'\bif\s*\([^)]*==\s*NULL\)', function_code):
        error_handling.append("包含NULL检查")
    
    # 安全风险分析
    security_concerns = []
    if re.search(r'\b(strcpy|strcat|sprintf|gets)\b', function_code):
        security_concerns.append("使用不安全的字符串函数")
    if re.search(r'\bmalloc\b', function_code) and 'free' not in function_code:
        security_concerns.append("潜在内存泄漏")
    
    result = {
        "function_name": function_name,
        "complexity_indicators": complexity_indicators,
        "purpose_hints": purpose_hints,
        "error_handling": error_handling,
        "security_concerns": security_concerns,
        "analysis": {
            "estimated_purpose": " | ".join(purpose_hints) if purpose_hints else "通用处理函数",
            "complexity_level": (
                "极高" if complexity_indicators['line_count'] > 100 else
                "高" if complexity_indicators['line_count'] > 50 else
                "中" if complexity_indicators['line_count'] > 20 else
                "低"
            ),
            "reliability": (
                "优秀" if len(error_handling) >= 3 else
                "良好" if len(error_handling) >= 2 else
                "一般" if len(error_handling) >= 1 else
                "需要改进"
            ),
            "security_risk": (
                "高" if len(security_concerns) >= 2 else
                "中" if len(security_concerns) == 1 else
                "低"
            )
        }
    }
    
    # 添加到历史记录并生成推荐
    add_to_history("analyze_function_tool", result)
    result["smart_recommendations"] = get_smart_recommendations("analyze_function_tool", result)
    
    return result


def analyze_dependencies(chunks_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    分析函数间依赖关系
    
    Args:
        chunks_data: 从chunk_code返回的数据
    """
    
    if "error" in chunks_data:
        return {"error": "无效的分块数据"}
    
    # 收集所有函数和调用关系
    all_functions = {}
    call_graph = []
    
    for chunk in chunks_data.get("chunks", []):
        for func_data in chunk.get("functions", []):
            func_name = func_data["name"]
            calls = func_data.get("calls", [])
            
            all_functions[func_name] = {
                "calls": calls,
                "called_by": [],
                "complexity": func_data.get("complexity", 1),
                "line_count": func_data.get("end_line", 0) - func_data.get("start_line", 0)
            }
            
            for called_func in calls:
                call_graph.append((func_name, called_func))
    
    # 构建反向调用关系
    for caller, callee in call_graph:
        if callee in all_functions:
            all_functions[callee]["called_by"].append(caller)
    
    # 计算重要性评分
    dependency_nodes = []
    for func_name, func_info in all_functions.items():
        calls_in = len(func_info["called_by"])
        calls_out = len(func_info["calls"])
        complexity = func_info["complexity"]
        
        importance_score = (calls_in * 2) + (calls_out * 0.5) + (complexity * 0.1)
        
        # 模块分组
        module_group = "core"
        if "modbus" in func_name.lower():
            module_group = "modbus"
        elif "tcp" in func_name.lower():
            module_group = "network"
        elif "rtu" in func_name.lower():
            module_group = "serial"
        elif any(word in func_name.lower() for word in ["init", "free"]):
            module_group = "lifecycle"
        elif any(word in func_name.lower() for word in ["get", "set"]):
            module_group = "data_access"
        
        dependency_nodes.append({
            "name": func_name,
            "calls": func_info["calls"],
            "called_by": func_info["called_by"],
            "importance_score": importance_score,
            "module_group": module_group,
            "complexity": complexity
        })
    
    # 按重要性排序
    dependency_nodes.sort(key=lambda x: x["importance_score"], reverse=True)
    
    # 识别关键函数
    critical_count = max(1, len(dependency_nodes) // 10)
    critical_functions = dependency_nodes[:critical_count]
    
    # 模块分组
    modules = {}
    for node in dependency_nodes:
        module = node["module_group"]
        if module not in modules:
            modules[module] = []
        modules[module].append(node["name"])
    
    result = {
        "total_functions": len(all_functions),
        "total_relationships": len(call_graph),
        "dependency_nodes": dependency_nodes,
        "critical_functions": [f["name"] for f in critical_functions],
        "modules": modules,
        "call_graph": call_graph,
        "statistics": {
            "max_calls_in": max([len(f["called_by"]) for f in all_functions.values()], default=0),
            "max_calls_out": max([len(f["calls"]) for f in all_functions.values()], default=0),
            "avg_complexity": sum([f["complexity"] for f in all_functions.values()]) / len(all_functions) if all_functions else 0
        }
    }
    
    # 添加到历史记录并生成推荐
    add_to_history("analyze_dependencies_tool", result)
    result["smart_recommendations"] = get_smart_recommendations("analyze_dependencies_tool", result)
    
    return result


def generate_mermaid_chart(dependency_data: Dict[str, Any], chart_type: str = "flowchart", max_nodes: int = 20) -> str:
    """
    生成Mermaid图表
    
    Args:
        dependency_data: 依赖分析数据
        chart_type: 图表类型 ("flowchart" | "graph" | "mindmap")
        max_nodes: 最大节点数
    """
    
    if "error" in dependency_data:
        return "错误: 无效的依赖数据"
    
    call_graph = dependency_data.get("call_graph", [])
    modules = dependency_data.get("modules", {})
    
    # 限制节点数
    call_graph = call_graph[:max_nodes]
    
    if chart_type == "flowchart":
        mermaid_code = ["flowchart TD"]
        
        added_nodes = set()
        for caller, callee in call_graph:
            clean_caller = re.sub(r'[^a-zA-Z0-9_]', '_', caller)
            clean_callee = re.sub(r'[^a-zA-Z0-9_]', '_', callee)
            
            if caller not in added_nodes:
                mermaid_code.append(f'    {clean_caller}["{caller}"]')
                added_nodes.add(caller)
            
            if callee not in added_nodes:
                mermaid_code.append(f'    {clean_callee}["{callee}"]')
                added_nodes.add(callee)
            
            mermaid_code.append(f'    {clean_caller} --> {clean_callee}')
    
    elif chart_type == "mindmap":
        mermaid_code = ["mindmap"]
        mermaid_code.append("  root((代码结构))")
        
        for module, functions in modules.items():
            if functions:
                mermaid_code.append(f"    {module}")
                for func in functions[:5]:  # 每个模块最多5个函数
                    clean_func = re.sub(r'[^a-zA-Z0-9_]', '_', func)
                    mermaid_code.append(f"      {clean_func}")
    
    else:  # graph
        mermaid_code = ["graph LR"]
        for caller, callee in call_graph:
            clean_caller = re.sub(r'[^a-zA-Z0-9_]', '_', caller)
            clean_callee = re.sub(r'[^a-zA-Z0-9_]', '_', callee)
            mermaid_code.append(f'    {clean_caller}[{caller}] --> {clean_callee}[{callee}]')
    
    return '\n'.join(mermaid_code)


def refactor_function(function_code: str, function_name: str) -> Dict[str, Any]:
    """
    提供函数重构建议
    
    Args:
        function_code: 函数代码
        function_name: 函数名
    """
    
    suggestions = []
    
    # 检查函数长度
    lines = function_code.split('\n')
    if len(lines) > 50:
        suggestions.append("函数过长，建议拆分为更小的函数")
    
    # 检查复杂度
    complexity = analyzer._calculate_complexity(function_code)
    if complexity > 15:
        suggestions.append("函数复杂度过高，建议简化逻辑")
    
    # 检查变量命名
    single_vars = re.findall(r'\b[a-z]\b', function_code)
    if single_vars:
        suggestions.append(f"建议使用更具描述性的变量名替换: {', '.join(set(single_vars))}")
    
    # 检查错误处理
    if 'return -1' not in function_code and 'return NULL' not in function_code:
        suggestions.append("建议添加错误处理和返回值检查")
    
    # 检查魔数
    magic_numbers = re.findall(r'\b\d{2,}\b', function_code)
    if magic_numbers:
        suggestions.append(f"建议为魔数定义常量: {', '.join(set(magic_numbers))}")
    
    # 生成改进评分
    improvement_score = max(0, 100 - len(suggestions) * 15)
    
    result = {
        "function_name": function_name,
        "suggestions": suggestions,
        "improvement_score": improvement_score,
        "priority": "高" if len(suggestions) > 3 else "中" if len(suggestions) > 1 else "低"
    }
    
    # 添加到历史记录并生成推荐
    add_to_history("refactor_function_tool", result)
    result["smart_recommendations"] = get_smart_recommendations("refactor_function_tool", result)
    
    return result


def generate_report(file_path: str, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    生成综合分析报告
    
    Args:
        file_path: 文件路径
        analysis_data: 分析数据
    """
    
    if "error" in analysis_data:
        result = {"error": "无效的分析数据"}
    else:
        total_functions = analysis_data.get("total_functions", 0)
        critical_functions = [
            node["name"] for node in analysis_data.get("dependency_nodes", [])
            if node.get("importance_score", 0) > 7
        ]
        
        modules = analysis_data.get("modules", {})
        
        result = {
            "file_path": file_path,
            "summary": {
                "total_functions": total_functions,
                "critical_functions": len(critical_functions),
                "modules": len(modules),
                "relationships": analysis_data.get("total_relationships", 0)
            },
            "key_findings": {
                "most_important_functions": critical_functions[:5],
                "module_distribution": {k: len(v) for k, v in modules.items()},
                "complexity_analysis": "基于依赖关系分析的复杂度评估"
            },
            "recommendations": [
                "关注高重要性评分的函数",
                "检查模块间的耦合度",
                "考虑重构复杂度过高的函数"
            ]
        }
    
    # 添加到历史记录并生成推荐
    add_to_history("generate_report_tool", result)
    result["smart_recommendations"] = get_smart_recommendations("generate_report_tool", result)
    
    return result


def search_code_tool(file_path: str, search_pattern: str, search_type: str = "function") -> Dict[str, Any]:
    """
    在代码中搜索特定模式
    
    Args:
        file_path: 代码文件路径
        search_pattern: 搜索模式（函数名、变量名、字符串等）
        search_type: 搜索类型 ("function", "variable", "string", "regex")
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return {"error": f"无法读取文件: {str(e)}"}
    
    lines = content.split('\n')
    results = []
    
    if search_type == "function":
        # 搜索函数定义和调用
        func_def_pattern = rf'\b{re.escape(search_pattern)}\s*\('
        func_call_pattern = rf'\b{re.escape(search_pattern)}\s*\('
        
        for i, line in enumerate(lines):
            if re.search(func_def_pattern, line):
                # 判断是定义还是调用
                is_definition = any(keyword in line for keyword in ['int ', 'void ', 'static ', 'char ', 'uint'])
                results.append({
                    "line_number": i + 1,
                    "line_content": line.strip(),
                    "match_type": "definition" if is_definition else "call",
                    "function_name": search_pattern
                })
    
    elif search_type == "variable":
        # 搜索变量使用
        var_pattern = rf'\b{re.escape(search_pattern)}\b'
        for i, line in enumerate(lines):
            if re.search(var_pattern, line):
                results.append({
                    "line_number": i + 1,
                    "line_content": line.strip(),
                    "match_type": "variable_usage"
                })
    
    elif search_type == "string":
        # 搜索字符串字面量
        for i, line in enumerate(lines):
            if search_pattern in line:
                results.append({
                    "line_number": i + 1,
                    "line_content": line.strip(),
                    "match_type": "string_literal"
                })
    
    elif search_type == "regex":
        # 正则表达式搜索
        try:
            pattern = re.compile(search_pattern)
            for i, line in enumerate(lines):
                if pattern.search(line):
                    results.append({
                        "line_number": i + 1,
                        "line_content": line.strip(),
                        "match_type": "regex_match"
                    })
        except re.error as e:
            return {"error": f"无效的正则表达式: {str(e)}"}
    
    result = {
        "search_pattern": search_pattern,
        "search_type": search_type,
        "total_matches": len(results),
        "results": results[:50],  # 限制结果数量
        "file_info": {
            "path": file_path,
            "total_lines": len(lines)
        }
    }
    
    # 添加到历史记录并生成推荐
    add_to_history("search_code_tool", result)
    result["smart_recommendations"] = get_smart_recommendations("search_code_tool", result)
    
    return result


def analyze_data_structures_tool(file_path: str) -> Dict[str, Any]:
    """
    分析代码中的数据结构
    
    Args:
        file_path: 代码文件路径
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return {"error": f"无法读取文件: {str(e)}"}
    
    structures = []
    enums = []
    typedefs = []
    
    # 查找结构体定义
    struct_pattern = r'typedef\s+struct\s*\{([^}]+)\}\s*(\w+);?|struct\s+(\w+)\s*\{([^}]+)\}'
    for match in re.finditer(struct_pattern, content, re.MULTILINE | re.DOTALL):
        if match.group(2):  # typedef struct
            struct_name = match.group(2)
            struct_body = match.group(1)
        else:  # regular struct
            struct_name = match.group(3)
            struct_body = match.group(4)
        
        # 分析字段
        fields = []
        for line in struct_body.split('\n'):
            line = line.strip()
            if line and not line.startswith('//') and not line.startswith('/*'):
                # 简单的字段解析
                field_match = re.search(r'(\w+(?:\s*\*)?)\s+(\w+)(?:\[.*?\])?\s*;', line)
                if field_match:
                    fields.append({
                        "type": field_match.group(1).strip(),
                        "name": field_match.group(2),
                        "line": line
                    })
        
        structures.append({
            "name": struct_name,
            "fields": fields,
            "field_count": len(fields),
            "estimated_size": len(fields) * 4  # 粗略估计
        })
    
    # 查找枚举定义
    enum_pattern = r'typedef\s+enum\s*\{([^}]+)\}\s*(\w+);?|enum\s+(\w+)\s*\{([^}]+)\}'
    for match in re.finditer(enum_pattern, content, re.MULTILINE | re.DOTALL):
        if match.group(2):  # typedef enum
            enum_name = match.group(2)
            enum_body = match.group(1)
        else:  # regular enum
            enum_name = match.group(3)
            enum_body = match.group(4)
        
        # 分析枚举值
        values = []
        for line in enum_body.split('\n'):
            line = line.strip().rstrip(',')
            if line and not line.startswith('//'):
                values.append(line)
        
        enums.append({
            "name": enum_name,
            "values": values,
            "value_count": len(values)
        })
    
    # 查找typedef定义
    typedef_pattern = r'typedef\s+([^;]+)\s+(\w+)\s*;'
    for match in re.finditer(typedef_pattern, content):
        base_type = match.group(1).strip()
        typedef_name = match.group(2)
        
        if not any(keyword in base_type for keyword in ['struct', 'enum']):
            typedefs.append({
                "name": typedef_name,
                "base_type": base_type
            })
    
    result = {
        "structures": structures,
        "enums": enums,
        "typedefs": typedefs,
        "summary": {
            "total_structures": len(structures),
            "total_enums": len(enums),
            "total_typedefs": len(typedefs),
            "complex_structures": [s for s in structures if s["field_count"] > 5]
        },
        "analysis": {
            "most_complex_struct": max(structures, key=lambda x: x["field_count"]) if structures else None,
            "data_model_complexity": "高" if len(structures) > 10 else "中" if len(structures) > 3 else "低"
        }
    }
    
    # 添加到历史记录并生成推荐
    add_to_history("analyze_data_structures_tool", result)
    result["smart_recommendations"] = get_smart_recommendations("analyze_data_structures_tool", result)
    
    return result


def security_audit_tool(file_path: str) -> Dict[str, Any]:
    """
    安全审计工具，检测潜在的安全问题
    
    Args:
        file_path: 代码文件路径
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return {"error": f"无法读取文件: {str(e)}"}
    
    lines = content.split('\n')
    security_issues = []
    
    # 定义安全检查规则
    security_rules = [
        {
            "pattern": r'\b(strcpy|strcat|sprintf|gets)\s*\(',
            "severity": "高",
            "category": "缓冲区溢出",
            "description": "使用不安全的字符串函数，可能导致缓冲区溢出",
            "suggestion": "使用安全版本：strncpy, strncat, snprintf, fgets"
        },
        {
            "pattern": r'\bmalloc\s*\([^)]+\)(?![^;]*free)',
            "severity": "中",
            "category": "内存泄漏",
            "description": "malloc分配的内存可能没有对应的free",
            "suggestion": "确保每个malloc都有对应的free调用"
        },
        {
            "pattern": r'\bsystem\s*\(',
            "severity": "高",
            "category": "命令注入",
            "description": "使用system()函数可能导致命令注入攻击",
            "suggestion": "使用更安全的API如execv()系列函数"
        },
        {
            "pattern": r'password|passwd|pwd',
            "severity": "中",
            "category": "敏感信息",
            "description": "可能包含硬编码的密码或敏感信息",
            "suggestion": "避免在代码中硬编码敏感信息"
        },
        {
            "pattern": r'\[\s*\w+\s*\]\s*=(?![^;]*sizeof)',
            "severity": "中",
            "category": "数组越界",
            "description": "数组访问可能存在越界风险",
            "suggestion": "添加边界检查或使用安全的数组操作"
        },
        {
            "pattern": r'rand\s*\(\)',
            "severity": "低",
            "category": "弱随机数",
            "description": "使用rand()生成的随机数不够安全",
            "suggestion": "使用加密安全的随机数生成器"
        }
    ]
    
    # 检查每一行
    for i, line in enumerate(lines):
        for rule in security_rules:
            if re.search(rule["pattern"], line, re.IGNORECASE):
                security_issues.append({
                    "line_number": i + 1,
                    "line_content": line.strip(),
                    "severity": rule["severity"],
                    "category": rule["category"],
                    "description": rule["description"],
                    "suggestion": rule["suggestion"]
                })
    
    # 统计分析
    severity_count = defaultdict(int)
    category_count = defaultdict(int)
    
    for issue in security_issues:
        severity_count[issue["severity"]] += 1
        category_count[issue["category"]] += 1
    
    # 计算安全评分
    high_weight = severity_count["高"] * 3
    medium_weight = severity_count["中"] * 2
    low_weight = severity_count["低"] * 1
    total_weight = high_weight + medium_weight + low_weight
    
    security_score = max(0, 100 - total_weight * 2)
    
    result = {
        "security_issues": security_issues[:50],  # 限制结果数量
        "summary": {
            "total_issues": len(security_issues),
            "severity_distribution": dict(severity_count),
            "category_distribution": dict(category_count),
            "security_score": security_score
        },
        "risk_assessment": {
            "overall_risk": (
                "高风险" if security_score < 60 else
                "中风险" if security_score < 80 else
                "低风险"
            ),
            "critical_issues": [issue for issue in security_issues if issue["severity"] == "高"],
            "recommendations": [
                "优先修复高严重性问题",
                "建立代码安全审查流程",
                "使用静态分析工具定期检查",
                "培训开发人员安全编程实践"
            ]
        }
    }
    
    # 添加到历史记录并生成推荐
    add_to_history("security_audit_tool", result)
    result["smart_recommendations"] = get_smart_recommendations("security_audit_tool", result)
    
    return result


def smart_assistant_tool(context: str = "") -> Dict[str, Any]:
    """
    智能分析助手，基于历史记录提供个性化建议
    
    Args:
        context: 用户提供的上下文信息
    """
    
    # 分析历史记录
    recent_tools = [h["tool"] for h in analysis_history[-10:]]
    tool_frequency = defaultdict(int)
    for tool in recent_tools:
        tool_frequency[tool] += 1
    
    # 生成建议
    suggestions = []
    workflow_recommendations = []
    
    if not analysis_history:
        suggestions.extend([
            "🚀 开始分析：使用 'chunk_code_tool' 将大文件分块处理",
            "🔍 快速搜索：使用 'search_code_tool' 查找特定函数或关键词",
            "🛡️ 安全检查：使用 'security_audit_tool' 发现潜在安全问题"
        ])
        workflow_recommendations.extend([
            "1. 首先使用代码分块工具了解整体结构",
            "2. 然后分析函数依赖关系",
            "3. 深入分析关键函数",
            "4. 进行安全审计",
            "5. 生成综合报告"
        ])
    else:
        # 基于历史记录的智能建议
        last_tool = analysis_history[-1]["tool"]
        last_result = analysis_history[-1]["result"]
        
        if "chunk_code_tool" in recent_tools and "analyze_dependencies_tool" not in recent_tools:
            suggestions.append("📊 建议分析函数依赖关系，了解代码结构")
        
        if "security_audit_tool" not in recent_tools:
            suggestions.append("🛡️ 建议进行安全审计，发现潜在问题")
        
        if "analyze_data_structures_tool" not in recent_tools:
            suggestions.append("🏗️ 建议分析数据结构，理解数据模型")
        
        # 检查是否有高复杂度函数需要重构
        for history in analysis_history[-5:]:
            if history["tool"] == "analyze_function_tool":
                complexity = history["result"].get("complexity_indicators", {}).get("line_count", 0)
                if complexity > 50:
                    suggestions.append(f"🔧 发现高复杂度函数，建议使用重构工具优化")
                    break
    
    # 生成个性化的下一步建议
    next_steps = []
    if context:
        context_lower = context.lower()
        if "安全" in context_lower or "security" in context_lower:
            next_steps.append("进行全面的安全审计")
        if "函数" in context_lower or "function" in context_lower:
            next_steps.append("分析特定函数的实现细节")
        if "结构" in context_lower or "struct" in context_lower:
            next_steps.append("分析数据结构和类型定义")
        if "搜索" in context_lower or "search" in context_lower:
            next_steps.append("使用代码搜索功能定位关键代码")
    
    if not next_steps:
        next_steps = [
            "分析代码整体结构",
            "识别关键函数和依赖关系",
            "检查潜在的安全问题",
            "生成可视化图表"
        ]
    
    result = {
        "analysis_summary": {
            "total_analyses": len(analysis_history),
            "recent_tools_used": list(set(recent_tools)),
            "most_used_tool": max(tool_frequency.items(), key=lambda x: x[1])[0] if tool_frequency else None
        },
        "personalized_suggestions": suggestions,
        "workflow_recommendations": workflow_recommendations,
        "next_steps": next_steps,
        "tips": [
            "💡 使用具体的函数名或关键词进行搜索更有效",
            "🎯 关注高重要性评分的函数，它们通常是系统核心",
            "🔄 定期进行安全审计，保持代码质量",
            "📈 使用依赖图可视化复杂的调用关系",
            "🛠️ 对复杂函数进行重构，提高代码可维护性"
        ],
        "context_analysis": f"基于上下文 '{context}'，为您定制了专门的分析建议" if context else "通用分析建议",
        "suggested_commands": [
            "搜索 modbus",
            "分析函数 main",
            "安全审计",
            "分析数据结构",
            "生成依赖图"
        ]
    }
    
    # 添加到历史记录
    add_to_history("smart_assistant_tool", result)
    
    return result 