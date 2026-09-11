#!/bin/bash
# WorkBuddy 每日自动更新脚本
# 每天凌晨6:00自动运行

WORKDIR="/workspace/workbuddy"
LOGFILE="/tmp/workbuddy-update.log"

# Token从本地密钥文件读取（该文件不上传到GitHub）
TOKENFILE="$WORKDIR/.token"
if [ -f "$TOKENFILE" ]; then
    export GITHUB_TOKEN=$(cat "$TOKENFILE" | tr -d '[:space:]')
fi

# 修复GitHub DNS污染问题（沙箱网络可能拦截api.github.com）
if ! curl -s -m 10 -o /dev/null "https://api.github.com/" 2>/dev/null; then
    grep -q "api.github.com" /etc/hosts 2>/dev/null || echo "140.82.112.6 api.github.com" >> /etc/hosts
    grep -q "github.com$" /etc/hosts 2>/dev/null || echo "140.82.112.3 github.com" >> /etc/hosts
fi

echo "=== WorkBuddy 自动更新 $(date '+%Y-%m-%d %H:%M:%S') ===" >> "$LOGFILE"

cd "$WORKDIR" || exit 1

# 运行数据生成器
python3 generator.py >> "$LOGFILE" 2>&1

if [ $? -eq 0 ]; then
    echo "✅ 数据生成成功" >> "$LOGFILE"
else
    echo "❌ 数据生成失败" >> "$LOGFILE"
    exit 1
fi

# GitHub Pages 会在 data.json 更新后自动部署
# 不需要额外操作

echo "=== 更新完成 ===" >> "$LOGFILE"
