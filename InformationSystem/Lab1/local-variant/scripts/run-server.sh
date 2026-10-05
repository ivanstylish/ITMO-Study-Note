#!/bin/sh
# 在当前终端设置数据库账号和密码；脚本只读取环境变量，不保存密码。
set -eu
: "${DB_USER:?Set DB_USER to the PostgreSQL role}"
: "${DB_PASSWORD:?Set DB_PASSWORD before starting the server}"
export DB_URL="${DB_URL:-jdbc:postgresql://pg:5432/studs}"
export DB_SCHEMA="${DB_SCHEMA:-lab1_info}"
export SERVER_ADDRESS="${SERVER_ADDRESS:-127.0.0.1}"
export PORT="${PORT:-18080}"
SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
exec java -Duser.timezone=UTC -jar "$SCRIPT_DIR/../build/libs/city-lab1.jar"

