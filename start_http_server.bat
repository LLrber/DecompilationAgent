@echo off
echo 启动逆向代码分析MCP HTTP服务器...
echo 服务器将在 http://0.0.0.0:382 启动
echo 按 Ctrl+C 停止服务器
echo.
python mcp_server.py --transport http --port 382 --debug
pause 