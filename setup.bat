@echo off
REM Shopify Automation - GitHub Setup Script (Windows)
REM 运行此脚本初始化 Git 仓库

echo ============================================
echo Shopify Automation - GitHub Setup
echo ============================================
echo.

REM 检查 Git 是否安装
where git >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Git 未安装，请先安装 Git
    echo 下载地址: https://git-scm.com/download/win
    pause
    exit /b 1
)

REM 检查是否已有远程仓库
git remote -v | findstr /C:"origin" >nul
if %errorlevel% equ 0 (
    echo [INFO] 远程仓库已存在
) else (
    echo [INPUT] 请输入 GitHub 仓库 URL
    echo (例如: https://github.com/username/shopify-automation.git)
    set /p repo_url="> "
    
    if "%repo_url%"=="" (
        echo [ERROR] 未提供仓库 URL
        pause
        exit /b 1
    )
    
    git remote add origin %repo_url%
    echo [OK] 已添加远程仓库
)

REM 初始化 Git（如果需要）
if not exist ".git" (
    echo [INFO] 初始化 Git 仓库...
    git init
    git branch -M main
    
    echo [INFO] 添加文件...
    git add .
    
    echo [INFO] 创建初始提交...
    git commit -m "Initial commit - Shopify Automation Framework"
    
    echo.
    echo ============================================
    echo Git 仓库初始化完成！
    echo ============================================
    echo.
    echo 下一步：
    echo 1. 在 GitHub 上创建仓库（如果还没有）
    echo 2. 添加 Secrets 到 GitHub
    echo 3. 推送代码: git push -u origin main
    echo.
)

echo ============================================
echo GitHub Secrets 配置指南
echo ============================================
echo.
echo 1. 进入 GitHub 仓库 -^> Settings -^> Secrets and variables -^> Actions
echo 2. 添加以下 Secrets:
echo.
echo    Name: SHOPIFY_STORE
echo    Value: hyl-test.myshopify.com
echo.
echo    Name: SHOPIFY_TOKEN
echo    Value: shpat_xxxxxxxxxxxxxxxxxxxx
echo.
echo    Name: SHOPIFY_THEME_ID
echo    Value: 151845732535
echo.
echo ============================================
echo 设置完成！
echo ============================================
pause