#!/bin/bash
# 医疗AI前沿网站自动更新脚本（cron 调用）
source ~/.hermes/scripts/website-env.sh  # token 从这里读，不进 git
export PATH="$HOME/.local/bin:$PATH"

cd ~/obsidian-zhaochenggang
GIT_SSH_COMMAND="ssh -i ~/.ssh/obsidian_key" git pull origin main --no-edit >/dev/null 2>&1

cd ~/website-demo
python3 build_site.py 2>&1
