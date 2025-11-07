#!/bin/bash

# Helper script to ensure a local MongoDB daemon is running.
# Designed to fix Linux startup issues where the bot fails with "Connection refused".

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DB_PATH="$ROOT_DIR/data/mongodb"
LOG_DIR="$ROOT_DIR/logs"
LOG_FILE="$LOG_DIR/mongodb.log"
PORT="27017"
BIND_IP="127.0.0.1"

mkdir -p "$DB_PATH" "$LOG_DIR"

python3 - "$BIND_IP" "$PORT" <<'PY'
import socket
import sys

host = sys.argv[1]
port = int(sys.argv[2])
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.settimeout(0.5)
    try:
        sock.connect((host, port))
    except (ConnectionRefusedError, OSError):
        sys.exit(1)
    else:
        sys.exit(0)
PY

STATUS=$?
if [ "$STATUS" -eq 0 ]; then
    echo "✅ MongoDB уже запущен на $BIND_IP:$PORT"
    exit 0
fi

if ! command -v mongod >/dev/null 2>&1; then
    echo "❌ Команда 'mongod' не найдена. Установите MongoDB или настройте переменную MONGODB_URI."
    exit 1
fi

MONGOD_ARGS=(
    "--dbpath" "$DB_PATH"
    "--logpath" "$LOG_FILE"
    "--bind_ip" "$BIND_IP"
    "--port" "$PORT"
    "--fork"
)

# If journaling directory does not exist, mongod might refuse to start.
# Create a placeholder to keep logs tidy.
touch "$LOG_FILE"

set +e
mongod "${MONGOD_ARGS[@]}"
MONGOD_STATUS=$?
set -e

if [ "$MONGOD_STATUS" -ne 0 ]; then
    echo "❌ Не удалось запустить MongoDB. Проверьте логи: $LOG_FILE"
    exit $MONGOD_STATUS
fi

echo "🚀 MongoDB успешно запущен (данные: $DB_PATH, лог: $LOG_FILE)"
