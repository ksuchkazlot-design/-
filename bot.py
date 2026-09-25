#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
APIALWAYS — Telegram Stars бот (валюта XTR).

Как получить токен:
  1. Откройте @BotFather в Telegram -> /newbot -> имя и username.
  2. BotFather выдаст токен вида 123456789:AA...  Вставьте его ниже (или в env STARS_BOT_TOKEN).

Как подключить к сайту:
  Вставьте username бота (без @) в index.html:  const STARS_BOT = 'ваш_бот';

Логика:
  Сайт открывает https://t.me/<бот>?start=pay_<план>_<цена>
  Бот отвечает инвойсом XTR (Telegram Stars), после успешной оплаты
  выдаёт следующий свободный ключ из keys.txt.

Запуск:  python bot.py
Зависимости: только стандартная библиотека Python 3.8+.
"""

import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

# Токен от @BotFather (переменная окружения STARS_BOT_TOKEN имеет приоритет).
# Не выкладывайте этот файл публично: токен даёт полный контроль над ботом.
TOKEN = os.environ.get("STARS_BOT_TOKEN", "8860588231:AAGJCwseLcd1aBfONLy9_DihD8VhtxpaqQM")
API = "https://api.telegram.org/bot" + TOKEN

# Курс: сколько Stars списывать (ваш курс, меняйте при желании)
STARS = {
    "1399": 819,    # Claude / GPT / Gemini Unlimited
    "3399": 1990,   # Trio (все три API)
}
PLAN_TITLES = {
    "claude": "Claude Unlimited на 30 дней",
    "gpt": "GPT Unlimited на 30 дней",
    "gemini": "Gemini Unlimited на 30 дней",
    "trio": "Все три API (Claude + GPT + Gemini) на 30 дней",
    "custom": "APIALWAYS — доступ на 30 дней",
}

KEYS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "keys.txt")
PAYMENTS_LOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "payments.log")
SUPPORT_URL = "https://t.me/products_supbot"


def api(method, **payload):
    """POST-вызов Bot API. Возвращает result или бросает исключение."""
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(API + "/" + method, data=data,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        body = json.loads(resp.read().decode("utf-8"))
    if not body.get("ok"):
        raise RuntimeError("%s: %s" % (method, body.get("description")))
    return body["result"]


def take_key():
    """Забирает первый ключ из keys.txt и перезаписывает файл."""
    if not os.path.exists(KEYS_FILE):
        return None
    with open(KEYS_FILE, "r", encoding="utf-8") as f:
        keys = [line.strip() for line in f if line.strip()]
    if not keys:
        return None
    key = keys[0]
    with open(KEYS_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(keys[1:]) + ("\n" if len(keys) > 1 else ""))
    return key


def log_payment(text):
    with open(PAYMENTS_LOG, "a", encoding="utf-8") as f:
        f.write(time.strftime("%Y-%m-%d %H:%M:%S") + "  " + text + "\n")


def send_text(chat_id, text):
    api("sendMessage", chat_id=chat_id, text=text, parse_mode="HTML")


def handle_start(message):
    chat_id = message["chat"]["id"]
    text = message.get("text") or ""
    payload = text.split(" ", 1)[1].strip() if " " in text else ""
    if not payload.startswith("pay_"):
        send_text(chat_id,
                  "Привет! Это бот оплаты APIALWAYS. 🤖\n\n"
                  "Нажмите кнопку «Оплатить Stars» на сайте — бот выставит счёт."
                  "\n\nПоддержка: " + SUPPORT_URL)
        return
    # pay_<план>_<цена>
    parts = payload.split("_")
    plan = parts[1] if len(parts) > 1 else "custom"
    amount = parts[2] if len(parts) > 2 else "0"
    price = STARS.get(amount)
    if price is None:
        send_text(chat_id, "Неизвестный тариф. Напишите в поддержку: " + SUPPORT_URL)
        return
    title = PLAN_TITLES.get(plan, PLAN_TITLES["custom"])
    api("sendInvoice",
        chat_id=chat_id,
        title=title,
        description="APIALWAYS. Оплата Telegram Stars, ключ придёт сразу после оплаты.",
        payload=payload,              # вернётся в successful_payment
        provider_token="",            # для XTR токен провайдера не нужен
        currency="XTR",
        prices=[{"label": title, "amount": price}],
        start_parameter="apialways-" + plan)


def handle_pre_checkout(query):
    try:
        api("answerPreCheckoutQuery",
            pre_checkout_query_id=query["id"], ok=True)
    except Exception as exc:          # noqa: BLE001 — не роняем поллинг
        print("pre_checkout error:", exc, file=sys.stderr)


def handle_successful_payment(message):
    chat_id = message["chat"]["id"]
    payment = message["successful_payment"]
    payload = payment.get("invoice_payload", "")
    total = payment.get("total_amount", "?")
    payer = message.get("from", {}).get("username") or str(chat_id)
    log_payment("%s paid %s XTR payload=%s" % (payer, total, payload))
    key = take_key()
    if key:
        send_text(chat_id,
                  "✅ Оплата получена!\n\n"
                  "Ваш API-ключ:\n<code>%s</code>\n\n"
                  "Endpoint: <code>https://api.apialways.top/v1</code>\n"
                  "Инструкция: https://apialways.top\n"
                  "Вопросы: %s" % (key, SUPPORT_URL))
    else:
        send_text(chat_id,
                  "✅ Оплата получена, но ключи закончились.\n"
                  "Напишите в поддержку — выдадим вручную: " + SUPPORT_URL)
        log_payment("!!! keys.txt пуст, платёж без ключа: " + payload)


def handle_update(update):
    message = update.get("message")
    if message:
        text = message.get("text") or ""
        if text.startswith("/start"):
            handle_start(message)
        elif message.get("successful_payment"):
            handle_successful_payment(message)
        elif text:
            send_text(message["chat"]["id"],
                      "Команда не распознана. Оплата — через кнопку на сайте. "
                      "Поддержка: " + SUPPORT_URL)
        return
    query = update.get("pre_checkout_query")
    if query:
        handle_pre_checkout(query)


def main():
    if TOKEN.startswith("ВСТАВЬТЕ"):
        sys.exit("Вставьте токен от @BotFather в переменную TOKEN (или env STARS_BOT_TOKEN).")
    print("Бот запущен.")
    offset = None
    while True:
        try:
            updates = api("getUpdates", offset=offset, timeout=40,
                          allowed_updates=["message", "pre_checkout_query"])
        except (urllib.error.URLError, urllib.error.HTTPError, RuntimeError, OSError) as exc:
            print("poll error:", exc, file=sys.stderr)
            time.sleep(5)
            continue
        for update in updates:
            offset = update["update_id"] + 1
            try:
                handle_update(update)
            except Exception as exc:  # noqa: BLE001 — один сбой не должен убивать поллинг
                print("update error:", exc, file=sys.stderr)


if __name__ == "__main__":
    main()
