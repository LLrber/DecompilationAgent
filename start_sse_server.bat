@echo off
echo 启动逆向代码分析MCP SSE服务器...
echo 服务器将在 http://0.0.0.0:382 启动
echo.
echo 可用端点:
echo   - 服务器信息: http://0.0.0.0:382/
echo   - 标准SSE: http://0.0.0.0:382/sse
echo   - MCP SSE: http://0.0.0.0:382/mcp
echo.
echo 按 Ctrl+C 停止服务器
echo.
python mcp_server.py --transport sse --host 0.0.0.0 --debug
pause 