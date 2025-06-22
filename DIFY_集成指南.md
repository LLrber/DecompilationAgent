# Dify集成指南

## 🎯 概述

本项目现在提供了专门为Dify优化的MCP服务器，基于FastMCP库构建，完全兼容Dify的MCP SSE插件。

## 🚀 快速开始

### 1. 启动Dify优化服务器

```bash
# 方法1：使用批处理文件（推荐）
start_dify_server.bat

# 方法2：直接运行Python
python mcp_server_dify.py
```

### 2. 验证服务器运行

服务器启动后，您应该看到：
```
INFO:__main__:启动Dify优化的逆向代码分析MCP服务器...
INFO:     Uvicorn running on http://0.0.0.0:382 (Press CTRL+C to quit)
```

### 3. 在Dify中配置

1. 在Dify的插件市场安装 [MCP SSE插件](https://marketplace.dify.ai/plugins/junjiem/mcp_sse)
2. 使用以下配置：
   - **服务器URL**: `http://0.0.0.0:382`
   - **传输方式**: SSE
   - **超时时间**: 30秒

## 🛠️ 可用工具

### 代码分析工具

| 工具名称 | 描述 | 输入参数 |
|---------|------|----------|
| `chunk_code_tool` | 将长代码文件分块处理 | `file_path`, `max_chunk_size` |
| `analyze_function_tool` | 深度分析单个函数 | `function_code`, `function_name` |
| `analyze_dependencies_tool` | 分析函数间依赖关系 | `chunks_data` |
| `search_code` | 搜索代码中的特定模式 | `file_path`, `search_pattern`, `search_type` |

### 可视化工具

| 工具名称 | 描述 | 输入参数 |
|---------|------|----------|
| `generate_mermaid_chart_tool` | 生成Mermaid依赖图表 | `dependency_data`, `chart_type`, `max_nodes` |
| `generate_report_tool` | 生成综合分析报告 | `file_path`, `analysis_data` |

### 优化工具

| 工具名称 | 描述 | 输入参数 |
|---------|------|----------|
| `refactor_function_tool` | 提供重构建议 | `function_code`, `function_name` |
| `analyze_data_structures` | 分析数据结构 | `file_path` |
| `security_audit` | 安全审计 | `file_path` |

### 智能助手

| 工具名称 | 描述 | 输入参数 |
|---------|------|----------|
| `smart_assistant` | 智能分析建议 | `context` |

## 📝 使用示例

### 示例1：分析C代码文件

```
1. 使用工具：chunk_code_tool
   参数：
   - file_path: "input/libCmpTemplateEvent.so.c"
   - max_chunk_size: 600

2. 使用工具：analyze_dependencies_tool
   参数：
   - chunks_data: [上一步的结果]

3. 使用工具：generate_mermaid_chart_tool
   参数：
   - dependency_data: [上一步的结果]
   - chart_type: "flowchart"
```

### 示例2：安全审计

```
1. 使用工具：security_audit
   参数：
   - file_path: "input/libCmpTemplateEvent.so.c"

2. 使用工具：search_code
   参数：
   - file_path: "input/libCmpTemplateEvent.so.c"
   - search_pattern: "strcpy"
   - search_type: "function"
```

### 示例3：函数重构

```
1. 使用工具：search_code
   参数：
   - file_path: "input/libCmpTemplateEvent.so.c"
   - search_pattern: "main"
   - search_type: "function"

2. 使用工具：analyze_function_tool
   参数：
   - function_code: [从搜索结果中获取的函数代码]
   - function_name: "main"

3. 使用工具：refactor_function_tool
   参数：
   - function_code: [同上]
   - function_name: "main"
```

## 🔧 技术架构

### 服务器架构

```
FastMCP Server (mcp_server_dify.py)
├── SSE Transport (端口 382)
├── 10个分析工具
├── 智能推荐系统
└── 历史记录跟踪
```

### 与标准版本的区别

| 特性 | 标准版本 | Dify优化版本 |
|------|----------|-------------|
| 基础库 | 原生MCP | FastMCP |
| 兼容性 | Cursor等 | Dify专用 |
| 协议处理 | 手动实现 | 自动处理 |
| 错误处理 | 基础 | 增强 |
| 响应格式 | JSON-RPC | Dify格式 |

## 🐛 故障排除

### 常见问题

1. **连接失败**
   ```
   错误：PluginInvokeError: ConnectionError: 'id'
   解决：使用Dify优化版本 (mcp_server_dify.py)
   ```

2. **端口占用**
   ```bash
   # 检查端口状态
   netstat -ano | findstr :382
   
   # 强制停止进程
   taskkill /F /PID [进程ID]
   ```

3. **工具调用失败**
   ```
   检查：
   - 文件路径是否正确
   - 参数格式是否正确
   - 服务器是否正常运行
   ```

### 调试模式

启动服务器时会自动开启调试模式，查看详细日志：
```bash
python mcp_server_dify.py
```

### 日志文件

检查 `logs/app.log` 获取详细错误信息。

## 📊 性能优化

### 配置调优

在 `mcp_server_dify.py` 中调整：
```python
config = ConfigSchema(
    debug=True,
    max_chunk_size=600  # 根据需要调整
)
```

### 内存优化

- 代码块大小：600行（默认）
- 历史记录：最多50条
- 超时设置：30秒

## 🔗 相关链接

- [Dify官网](https://dify.ai/)
- [MCP SSE插件](https://marketplace.dify.ai/plugins/junjiem/mcp_sse)
- [FastMCP文档](https://github.com/jlowin/fastmcp)
- [项目GitHub](https://github.com/your-repo/DecompilationAgent)

## 📞 支持

如果遇到问题，请：

1. 检查服务器日志
2. 验证配置参数
3. 查看故障排除部分
4. 提交Issue到GitHub

---

**🎉 现在您可以在Dify中使用强大的逆向代码分析功能了！** 