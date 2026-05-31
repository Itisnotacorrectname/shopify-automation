@echo off
REM 本地部署脚本 - Windows 版本
REM 使用方法: deploy-local.bat [zip文件路径]

setlocal enabledelayedexpansion

set "ZIP_FILE=%1"
if "%ZIP_FILE%"=="" set "ZIP_FILE=theme.zip"

echo ============================================================
echo Shopify Theme - 本地部署
echo ============================================================

REM 检查 gh CLI
where gh >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [错误] 未安装 gh CLI
    echo 请从 https://cli.github.com 安装
    exit /b 1
)

REM 下载最新的主题包
echo.
echo [1/3] 下载主题包...
gh run download latest --repo Itisnotacorrectname/shopify-automation --name shopify-theme-zip --dir . || (
    echo [错误] 下载失败
    echo 请确保：
    echo   1. 已登录: gh auth login
    echo   2. 已运行 GitHub Actions workflow
    exit /b 1
)

REM 解压
echo.
echo [2/3] 解压文件...
powershell -Command "Expand-Archive -Force '%ZIP_FILE%' 'deploy-temp'"

REM 部署
echo.
echo [3/3] 部署到 Shopify...
cd deploy-temp
python ..\cli.py deploy --full --theme-dir .
cd ..

REM 清理
echo.
echo 清理临时文件...
rmdir /s /q deploy-temp 2>nul

echo.
echo ============================================================
echo 部署完成！
echo ============================================================
endlocal