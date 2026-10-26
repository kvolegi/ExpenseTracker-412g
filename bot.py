"""
Telegram Bot Runner for Expense Tracker (@expense412trackerbot)
==============================================================
Автономний бот для обробки команди /start, налаштування Menu Button 
та відкриття Telegram Mini App.
Працює на чистому httpx (без додаткових залежностей).

Використання:
    python3 bot.py
    або з параметрами:
    python3 bot.py --url https://your-webapp-url.com
"""

import os
import sys
import time
import argparse
import logging
import httpx
from pathlib import Path

# Load .env if python-dotenv is installed
try:
    from dotenv import load_dotenv
    for path in [Path(__file__).resolve().parent / ".env", Path(__file__).resolve().parent / "backend" / ".env"]:
        if path.exists():
            load_dotenv(path)
            break
except ImportError:
    pass

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("ExpenseTrackerBot")

DEFAULT_TOKEN = "8915867180:AAG9PzD-ed2pKbKHZZsqs2T-xnbAqa8r68g"
DEFAULT_WEBAPP_URL = "https://expensetrackerbot-10-production.up.railway.app"

def get_args():
    parser = argparse.ArgumentParser(description="Expense Tracker Telegram Bot Runner")
    parser.add_argument("--token", default=os.getenv("TELEGRAM_BOT_TOKEN", DEFAULT_TOKEN), help="Telegram Bot Token")
    parser.add_argument("--url", default=os.getenv("WEBAPP_URL", DEFAULT_WEBAPP_URL), help="Telegram Mini App Web URL")
    return parser.parse_args()

class ExpenseTrackerBot:
    def __init__(self, token: str, webapp_url: str):
        self.token = token.strip()
        self.webapp_url = webapp_url.strip()
        self.api_url = f"https://api.telegram.org/bot{self.token}"
        self.client = httpx.Client(timeout=35.0)

    def api_call(self, method: str, json_data: dict = None) -> dict:
        url = f"{self.api_url}/{method}"
        resp = self.client.post(url, json=json_data or {})
        resp.raise_for_status()
        return resp.json()

    def setup_bot_profile(self):
        """Configure bot commands, descriptions, and menu button."""
        try:
            me = self.api_call("getMe")
            bot_user = me.get("result", {})
            logger.info(f"Бот успішно авторизований: @{bot_user.get('username')} ({bot_user.get('first_name')})")

            # 1. Set Menu Button to open Web App
            self.api_call("setChatMenuButton", {
                "menu_button": {
                    "type": "web_app",
                    "text": "💰 Expense Tracker",
                    "web_app": {"url": self.webapp_url}
                }
            })
            logger.info(f"Кнопку меню налаштовано на WebApp URL: {self.webapp_url}")

            # 2. Set Bot Commands
            self.api_call("setMyCommands", {
                "commands": [
                    {"command": "start", "description": "Запустити Expense Tracker"},
                    {"command": "app", "description": "Відкрити Telegram Mini App"},
                    {"command": "help", "description": "Інформація про проєкт та авторів"}
                ]
            })

            # 3. Set Description
            self.api_call("setMyDescription", {
                "description": (
                    "💰 Expense Tracker — Telegram Mini App для обліку особистих фінансів.\n"
                    "Розроблено студентами ОНЮА (ІПЗ-42).\n"
                    "Натисніть Start для запуску додатку."
                )
            })
            logger.info("Профіль, опис та команди бота успішно оновлено.")
        except Exception as e:
            logger.warning(f"Попередження при налаштуванні профілю бота: {e}")

    def handle_message(self, message: dict):
        chat_id = message.get("chat", {}).get("id")
        text = message.get("text", "").strip()
        from_user = message.get("from", {})
        first_name = from_user.get("first_name", "Користувачу")

        if not chat_id:
            return

        if text.startswith("/help"):
            help_text = (
                "📚 *Expense Tracker — Довідка проєкту*\n\n"
                "🔹 *Про проєкт:* Telegram Mini App для обліку витрат та доходів із 4-рівневою архітектурою, "
                "GoF-патернами, захистом STRIDE та Supabase PostgreSQL.\n\n"
                "👥 *Автори (НУ «ОЮА», група ІПЗ-42):*\n"
                "• *Мілена Петрушенко* — Team Lead & Solution Architect\n"
                "• *Вікторія Чугуннікова* — DBA & DevOps Engineer\n"
                "• *Єгор Бевзюк* — QA Lead & Frontend Engineer\n\n"
                "👨‍🏫 *Викладач:* Ніколаєнко С.В.\n\n"
                "Натисніть кнопку нижче, щоб відкрити додаток! 👇"
            )
            keyboard = {
                "inline_keyboard": [
                    [
                        {"text": "🚀 Відкрити Expense Tracker", "web_app": {"url": self.webapp_url}}
                    ],
                    [
                        {"text": "🐙 Репозиторій на GitHub", "url": "https://github.com/kvolegi/ExpenseTracker-412g"}
                    ]
                ]
            }
            self.api_call("sendMessage", {
                "chat_id": chat_id,
                "text": help_text,
                "parse_mode": "Markdown",
                "reply_markup": keyboard
            })
            return

        # Default for /start, /app or any message:
        welcome_text = (
            f"👋 *Вітаємо, {first_name}!*\n\n"
            "💰 *Expense Tracker* готовий до роботи!\n\n"
            "Тут ви можете:\n"
            "• Додавати витрати та доходи за категоріями\n"
            "• Переглядати аналітику та графіки за тиждень\n"
            "• Отримувати автоматичні сповіщення про транзакції\n\n"
            "Натисніть кнопку нижче, щоб розпочати роботу 👇"
        )
        keyboard = {
            "inline_keyboard": [
                [
                    {"text": "🚀 Відкрити Expense Tracker", "web_app": {"url": self.webapp_url}}
                ],
                [
                    {"text": "ℹ️ Про проєкт / Довідка", "callback_data": "help"}
                ]
            ]
        }
        self.api_call("sendMessage", {
            "chat_id": chat_id,
            "text": welcome_text,
            "parse_mode": "Markdown",
            "reply_markup": keyboard
        })

    def handle_callback_query(self, query: dict):
        query_id = query.get("id")
        data = query.get("data")
        chat_id = query.get("message", {}).get("chat", {}).get("id")

        try:
            self.api_call("answerCallbackQuery", {"callback_query_id": query_id})
        except Exception:
            pass

        if data == "help" and chat_id:
            self.handle_message({"chat": {"id": chat_id}, "text": "/help", "from": query.get("from", {})})

    def run(self):
        self.setup_bot_profile()
        logger.info(f"Бот успішно запущений і очікує повідомлень...")
        offset = 0

        while True:
            try:
                updates = self.api_call("getUpdates", {"offset": offset, "timeout": 25})
                for update in updates.get("result", []):
                    offset = update["update_id"] + 1

                    if "message" in update:
                        self.handle_message(update["message"])
                    elif "callback_query" in update:
                        self.handle_callback_query(update["callback_query"])

            except httpx.TimeoutException:
                continue
            except KeyboardInterrupt:
                logger.info("Зупинка бота користувачем.")
                break
            except Exception as e:
                logger.error(f"Помилка в циклі опитування: {e}")
                time.sleep(3)

if __name__ == "__main__":
    args = get_args()
    bot = ExpenseTrackerBot(token=args.token, webapp_url=args.url)
    bot.run()
