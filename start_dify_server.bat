@echo off
echo ========================================
echo     启动Dify优化的逆向代码分析服务器
echo ========================================
echo.
echo 服务器信息:
echo - 主机: 0.0.0.0
echo - 端口: 382
echo - 传输: SSE
echo - 优化: Dify兼容
echo.
echo 启动中...
echo.

python mcp_server_dify.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo 错误: 服务器启动失败！
    echo 请检查:
    echo 1. Python环境是否正确安装
    echo 2. 依赖包是否已安装 (pip install -r requirements.txt)
    echo 3. 端口382是否被占用
    echo.
    pause
) else (
    echo.
    echo 服务器已关闭
    pause
) 