# 逆向代码分析MCP工具

专门为逆向工程场景设计的MCP（Model Context Protocol）工具，能够分析反编译得到的C语言代码，提供结构化的分析结果。

## 核心功能

- **代码分块** - 解决大文件上下文限制问题
- **函数分析** - 深度分析函数用途、复杂度、安全风险
- **依赖关系** - 构建函数调用图和模块依赖
- **Mermaid图表** - 生成可视化流程图
- **重构建议** - 提供代码改进建议
- **综合报告** - 生成完整分析报告

## 支持的通信方式

- **stdio** - 标准输入输出（MCP标准协议，适用于Cursor等IDE）

## 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 运行方式

```bash
# 启动MCP服务器（stdio模式）
python mcp_server.py

# 或者显式指定transport
python mcp_server.py --transport stdio
```

## Cursor集成

复制 `config/cursor/mcp_config.json` 内容到Cursor的MCP配置文件中即可使用。

## 工具列表

1. **chunk_code** - 代码分块处理
2. **analyze_function** - 单函数深度分析
3. **analyze_dependencies** - 依赖关系分析
4. **generate_mermaid_chart** - Mermaid图表生成
5. **refactor_function** - 重构建议
6. **generate_report** - 综合报告生成

## 使用示例

在Cursor中使用MCP工具分析反编译的C代码文件，支持代码分块、函数分析、依赖关系分析、图表生成等功能。

## 项目结构

```
DecompilationAgent/
├── src/                     # 源代码模块
│   ├── models/             # 数据模型
│   ├── core/               # 核心分析引擎
│   ├── tools/              # MCP工具函数
│   ├── config/             # 配置管理
│   └── utils/              # 工具函数
├── config/cursor/          # Cursor集成配置
├── tests/                  # 测试目录
├── input/                  # 输入文件目录
├── output/                 # 输出文件目录
├── logs/                   # 日志目录
├── mcp_server.py          # 主服务器入口
├── requirements.txt       # Python依赖
└── README.md             # 项目说明
```

## 特性

- 🔍 **专业逆向分析** - 识别Modbus、TCP、RTU等协议函数
- 📊 **可视化图表** - 支持Mermaid流程图和思维导图
- 🚀 **高性能处理** - 智能分块解决大文件问题
- 🛡️ **安全检测** - 识别潜在的安全风险
- 🔧 **重构建议** - 提供具体的代码改进方案

## 许可证

MIT License 