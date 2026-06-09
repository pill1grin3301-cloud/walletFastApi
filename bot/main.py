# bot/main.py
import asyncio
import httpx
from bot.config import bot_settings

TOKEN = bot_settings.TELEGRAM_TOKEN
URL = f"https://api.telegram.org/bot{TOKEN}/"
# Telegram long-poll timeout=10s; httpx default read=5s → ReadTimeout
POLL_TIMEOUT = 10
HTTP_TIMEOUT = httpx.Timeout(connect=10.0, read=POLL_TIMEOUT + 15.0, write=10.0, pool=10.0)


async def get_updates(offset=None):
    async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
        r = await client.get(URL + "getUpdates", params={"offset": offset, "timeout": POLL_TIMEOUT})
        return r.json().get("result", [])


async def send_message(chat_id, text):
    async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
        await client.post(URL + "sendMessage", json={"chat_id": chat_id, "text": text})


async def main():
    print("✅ Бот запущен, жду сообщений...", flush=True)
    last_id = 0
    while True:
        try:
            updates = await get_updates(last_id + 1)
            for u in updates:
                msg = u.get("message")
                if msg:
                    chat_id = msg["chat"]["id"]
                    text = msg.get("text", "")
                    print(f"📩 {chat_id}: {text}", flush=True)
                    await send_message(chat_id, f"Эхо: {text}")
                last_id = u["update_id"]
        except httpx.TimeoutException as e:
            print(f"⚠️ Таймаут сети ({type(e).__name__}), повтор...", flush=True)
        except httpx.HTTPError as e:
            print(f"⚠️ Ошибка сети ({type(e).__name__}), повтор через 5с...", flush=True)
            await asyncio.sleep(5)


if __name__ == "__main__":
    asyncio.run(main())
