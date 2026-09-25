#!/usr/bin/env bash
# ============================================================
#  APIALWAYS — Telegram Stars бот: установка одной командой
#  Запуск на свежем Ubuntu/Debian (под root):
#     bash setup.sh
#  Что делает: ставит python3, скачивает бота, настраивает
#  systemd (автозапуск при перезагрузке) и запускает его.
# ============================================================
set -e

BOT_DIR="/opt/apialways-bot"
REPO_RAW="https://raw.githubusercontent.com/ksuchkazlot-design/-/master"

echo "==[1/5]== Останавливаю возможный прежний бот..."
systemctl stop apialways-bot 2>/dev/null || true

echo "==[2/5]== Ставлю Python3..."
export DEBIAN_FRONTEND=noninteractive
apt-get update -y -qq
apt-get install -y -qq python3 curl

echo "==[3/5]== Кладу файлы бота в $BOT_DIR..."
mkdir -p "$BOT_DIR"
curl -fsSL "$REPO_RAW/bot.py" -o "$BOT_DIR/bot.py"
# keys.txt: свой файл, если уже создавали — не затираем
if [ ! -f "$BOT_DIR/keys.txt" ]; then
  printf 'sk-always-PLACEHOLDER-1\nsk-always-PLACEHOLDER-2\nsk-always-PLACEHOLDER-3\n' > "$BOT_DIR/keys.txt"
fi

echo "==[4/5]== Создаю systemd-сервис (автозапуск)..."
cat > /etc/systemd/system/apialways-bot.service <<'UNIT'
[Unit]
Description=APIALWAYS Telegram Stars bot
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
WorkingDirectory=/opt/apialways-bot
ExecStart=/usr/bin/python3 -u bot.py
Restart=always
RestartSec=5
User=root

[Install]
WantedBy=multi-user.target
UNIT
systemctl daemon-reload
systemctl enable apialways-bot >/dev/null 2>&1

echo "==[5/5]== Запускаю бота..."
systemctl restart apialways-bot
sleep 3

echo "----------------------------------------"
systemctl --no-pager -l status apialways-bot | head -n 12 || true
echo "----------------------------------------"
if systemctl is-active --quiet apialways-bot; then
  echo "ГОТОВО. Бот работает и переживёт перезагрузку сервера."
  echo "Логи:      journalctl -u apialways-bot -f"
  echo "Ключи:     nano $BOT_DIR/keys.txt"
  echo "Перезапуск: systemctl restart apialways-bot"
else
  echo "Бот упал. Смотрите лог: journalctl -u apialways-bot -n 50"
  exit 1
fi
