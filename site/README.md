# APIALWAYS — сайт (клон apialways.top)

Статический лендинг продажи безлимитных API (Claude / GPT / Gemini). Полная копия рабочего сайта apialways.top, без зависимостей и сборки — просто отдавайте папку как статику.

## Файлы

| Файл | Назначение |
|---|---|
| `index.html` | Главная страница (всё в одном файле: стили + скрипты) |
| `tos.html` | Terms of Service / Privacy / Fair Use |
| `status.html` | Статус сервисов |
| `favicon.svg` | Фавикон |
| `llms.txt` | Файл для AI-ассистентов (SEO) |
| `bot/bot.py` | Telegram Stars бот (выдаёт ключи после оплаты XTR) |
| `bot/keys.txt` | Очередь ключей для выдачи (по одному в строке) |

## Локальный запуск

```powershell
python -m http.server 8000 --directory D:\Cline\apialways-site
# открыть http://127.0.0.1:8000/
```

## Оплата

Все кнопки «Купить ключ» ведут на платёжную страницу `pay-links.pro`:

| Тариф | Ссылка |
|---|---|
| Claude Unlimited (1399) | `https://pay-links.pro/fast/?sum=1399&name=CLAUDE-UNLIM` |
| GPT Unlimited (1399) | `https://pay-links.pro/fast/?sum=1399&name=GPT-UNLIM` |
| Gemini Unlimited (1399) | `https://pay-links.pro/fast/?sum=1399&name=GEMINI-UNLIM` |
| Все три API / trio (3399) | `https://pay-links.pro/fast/?sum=3399&name=TRIOAPI-UNLIM` |

Открываются в новой вкладке (`target="_blank"`).

### Кнопки Telegram Stars

Под каждой кнопкой «Купить ключ» есть голубая кнопка **«⭐ Оплатить Stars · 819»**
(в блоке Trio — 1990). Пока `STARS_BOT` пустой, она ведёт на тот же pay-links.pro
(там способ «Telegram Stars» уже есть). После ввода `STARS_BOT` кнопки с классом
`stars-pay` открывают вашего бота с deep-link `pay_<план>_<цена>`.

### Как убрать криптовалюту из платёжной страницы

На самом сайте крипты нет — блок «Криптовалюта / USDT / TON / Bitcoin / TRX»
рендерит сервер pay-links.pro, и параметрами URL это не управляется
(проверены `method=`, `hide=`, `only=`, `disabled=` — список способов не меняется).

Способа убрать крипту:

1. **Личный кабинет pay-links.pro** — в настройках способов оплаты отключите
   «Криптовалюта» (так же, как там уже отключены QIWI и Юmoney — они в HTML
   идут с `display:none`). После этого перезагрузите платёжную ссылку.
2. Если в кабинете такой опции нет — напишите в поддержку pay-links.pro
   и попросите отключить метод для ваших ссылок.

## Оплата через Telegram Stars (свой бот)

Кнопки имеют класс `stars-pay` и атрибуты `data-plan` / `data-amount`
(`claude`/`gpt`/`gemini` — 1399, `trio` — 3399).

### Пошаговое подключение

1. **Создайте бота**: откройте в Telegram **@BotFather** → `/newbot` →
   придумайте имя и username (должен заканчиваться на `bot`) → BotFather
   выдаст токен вида `123456789:AA...`.
2. **Приём Stars не требует отдельной настройки** — валюта `XTR` включена
   в Bot API из коробки, платежный провайдер не нужен.
3. **Запустите бота** из папки `bot/`:
   ```powershell
   $env:STARS_BOT_TOKEN="123456789:AA..."
   python D:\Cline\apialways-site\bot\bot.py
   ```
   Токен также можно вписать прямо в `bot/bot.py` (переменная `TOKEN`).
4. **Ключи** кладите по одному в строку в `bot/keys.txt` — бот выдаёт
   первый свободный после оплаты, всё пишет в `bot/payments.log`.
5. **Впишите username бота** в `index.html` (без `@`):
   ```js
   const STARS_BOT = 'ваш_бот';
   ```
   Голубые кнопки начнут открывать бота вместо pay-links.pro.
6. **Курс Stars** задаётся в `bot/bot.py`, словарь `STARS`
   (по умолчанию 1399 ₽ → 819⭐, 3399 ₽ → 1990⭐ — как на pay-links.pro).
   Если поменяете курс там — обновите и цифры на кнопках в `index.html`.

После успешной оплаты бот отправляет ключ и endpoint; логика выдачи ключей —
на стороне бота (можно заменить `take_key()` на свой API).
