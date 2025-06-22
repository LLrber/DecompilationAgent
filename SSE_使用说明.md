# SSE模式使用说明

## 什么是SSE模式？

SSE (Server-Sent Events) 是一种允许服务器向客户端推送实时数据的技术。在逆向代码分析器中，SSE模式可以用于：

- 实时监控分析进度
- 推送分析结果
- 提供心跳检测
- 实时状态更新

## 🚀 启动SSE服务器

### 方法1：使用批处理文件（推荐）
```bash
# Windows
start_sse_server.bat

# Linux/Mac
chmod +x start_sse_server.bat
./start_sse_server.bat
```

### 方法2：直接运行Python命令
```bash
python mcp_server.py --transport sse --host 0.0.0.0 --debug
```

### 方法3：使用环境变量
```bash
# 设置环境变量
set TRANSPORT=sse
set SSE_HOST=0.0.0.0
set SSE_PORT=8001

# 运行服务器
python mcp_server.py
```

## 🌐 访问SSE服务

### 服务器信息
- **主机地址**: 0.0.0.0 (允许外部访问)
- **端口**: 8001
- **服务器信息**: http://0.0.0.0:8001/
- **标准SSE端点**: http://0.0.0.0:8001/sse
- **MCP SSE端点**: http://0.0.0.0:8001/mcp (推荐用于MCP客户端)

### 访问方式

#### 1. 使用测试页面（推荐）
打开浏览器访问：`test_sse.html`

这个测试页面提供了：
- 实时连接状态显示
- SSE数据接收日志
- 连接/断开控制
- 清空日志功能

#### 2. 使用curl命令
```bash
# 测试服务器状态
curl http://0.0.0.0:8001/

# 连接SSE流
curl -N -H "Accept: text/event-stream" http://0.0.0.0:8001/sse
```

#### 3. 使用JavaScript
```javascript
const eventSource = new EventSource('http://0.0.0.0:8001/sse');

eventSource.onopen = function(event) {
    console.log('SSE连接已建立');
};

eventSource.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('收到数据:', data);
};

eventSource.onerror = function(event) {
    console.log('SSE连接错误');
};
```

#### 4. 使用Python客户端
```python
import requests
import json

# 连接SSE流
response = requests.get('http://0.0.0.0:8001/sse', stream=True)

for line in response.iter_lines():
    if line:
        line = line.decode('utf-8')
        if line.startswith('data: '):
            data = json.loads(line[6:])  # 去掉 'data: ' 前缀
            print('收到数据:', data)
```

## 📊 SSE数据格式

服务器推送的数据格式为JSON：

```json
{
    "type": "heartbeat",
    "timestamp": "2024-01-01T12:00:00Z",
    "status": "running"
}
```

可能的数据类型：
- `heartbeat`: 心跳检测（每30秒）
- `analysis_progress`: 分析进度更新
- `analysis_result`: 分析结果
- `error`: 错误信息
- `status`: 状态更新

## 🔧 配置选项

### 环境变量
- `SSE_HOST`: SSE服务器主机地址（默认：0.0.0.0）
- `SSE_PORT`: SSE服务器端口（默认：8001）
- `DEBUG`: 启用调试模式（默认：false）

### 配置文件
编辑 `src/config/settings.py`：

```python
# SSE设置
sse_host: str = "0.0.0.0"
sse_port: int = 8001
```

## 🛠️ MCP集成

如果要在MCP（Model Context Protocol）中使用SSE模式，使用以下配置：

```json
{
  "mcpServers": {
    "reverse-code-analyzer": {
      "url": "http://0.0.0.0:8001/mcp",
      "transport": "sse",
      "description": "Reverse Code Analysis Tool (SSE Mode)"
    }
  }
}
```

## 🔍 故障排除

### 常见问题

1. **Content-Type错误**
   ```
   Expected response header Content-Type to contain 'text/event-stream', got 'application/json'
   ```
   **解决方案**：
   - 确保使用正确的SSE端点：`/mcp` 而不是 `/sse`
   - 检查MCP配置文件中的URL是否正确
   - 重启服务器确保修改生效

2. **连接被拒绝**
   - 检查服务器是否已启动
   - 确认端口8001未被占用
   - 检查防火墙设置

3. **CORS错误**
   - 确保从正确的域名访问
   - 检查浏览器安全设置

4. **数据接收不到**
   - 检查网络连接
   - 查看服务器日志
   - 确认SSE端点URL正确

### 调试模式
启动时添加 `--debug` 参数可以看到详细日志：

```bash
python mcp_server.py --transport sse --debug
```

### 日志查看
检查 `logs/app.log` 文件获取详细错误信息。

## 📝 示例用法

### 完整启动流程
1. 打开命令行终端
2. 切换到项目目录
3. 运行：`start_sse_server.bat`
4. 打开浏览器访问：`test_sse.html`
5. 点击"连接SSE"按钮
6. 观察实时数据推送

### 集成到应用程序
```javascript
class SSEClient {
    constructor(url) {
        this.url = url;
        this.eventSource = null;
    }
    
    connect() {
        this.eventSource = new EventSource(this.url);
        
        this.eventSource.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleData(data);
        };
    }
    
    handleData(data) {
        switch(data.type) {
            case 'heartbeat':
                console.log('服务器运行正常');
                break;
            case 'analysis_result':
                this.processAnalysisResult(data);
                break;
        }
    }
    
    disconnect() {
        if (this.eventSource) {
            this.eventSource.close();
        }
    }
}

// 使用示例
const client = new SSEClient('http://0.0.0.0:8001/sse');
client.connect();
```

## 🔗 相关文档

- [HTTP模式使用说明](README.md)
- [MCP协议文档](https://spec.modelcontextprotocol.io/)
- [Server-Sent Events规范](https://html.spec.whatwg.org/multipage/server-sent-events.html) 