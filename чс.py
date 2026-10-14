from telethon import TelegramClient, events
from datetime import datetime, timezone, timedelta
import json
import os

api_id = 22679797
api_hash = "6dbdcaa13cc090e733f7a8f7f7557206"

SESSION_NAME = "my_userbot"
BLACKLIST_FILE = "blacklist.json"

# Красноярск = UTC+7
KRASNOYARSK = timezone(timedelta(hours=7))

client = TelegramClient(SESSION_NAME, api_id, api_hash)


# ---------- Работа с JSON ----------

def load_blacklist() -> dict:
    if not os.path.exists(BLACKLIST_FILE):
        return {}
    try:
        with open(BLACKLIST_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def save_blacklist(data: dict) -> None:
    with open(BLACKLIST_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def now_str() -> str:
    return datetime.now(KRASNOYARSK).strftime("%d.%m.%Y %H:%M")


def display_name(user) -> str:
    name = " ".join(filter(None, [user.first_name, user.last_name]))
    return name or (f"@{user.username}" if user.username else f"ID {user.id}")


# ---------- Обработчик команд ----------

@client.on(events.NewMessage(outgoing=True, func=lambda e: e.is_private))
async def commands_handler(event):
    text = (event.raw_text or "").strip()
    me = await client.get_me()

    # Команды работают только от твоего аккаунта
    if event.sender_id != me.id:
        return

    # Чтобы команда сработала, нужен собеседник
    peer = await event.get_chat()
    if peer is None or peer.id == me.id:
        return

    target_id = str(peer.id)
    bl = load_blacklist()

    # ---- +чс ----
    if text == "+чс":
        if target_id in bl:
            await event.reply("⚠️ Уже в ЧС")
            return
        bl[target_id] = {
            "name": display_name(peer),
            "added": now_str(),
        }
        save_blacklist(bl)
        await event.reply(f"✅ Добавлен в ЧС: {display_name(peer)}")
        return

    # ---- -чс ----
    if text == "-чс":
        if target_id not in bl:
            await event.reply("⚠️ Его нет в ЧС")
            return
        removed = bl.pop(target_id)
        save_blacklist(bl)
        await event.reply(f"🗑 Удалён из ЧС: {removed.get('name', target_id)}")
        return

    # ---- чс (список) ----
    if text == "чс":
        if not bl:
            await event.reply("Список пуст...")
            return
        lines = ["Пользователи в ЧС:"]
        for i, (uid, info) in enumerate(bl.items(), start=1):
            name = info.get("name", f"ID {uid}")
            added = info.get("added", "—")
            link = f'<a href="tg://user?id={uid}">{name}</a>'
            lines.append(f"{i}. {link} | {added}")
        await event.reply("\n".join(lines), parse_mode="html")
        return


# ---------- Автоудаление сообщений от юзеров в ЧС ----------

@client.on(events.NewMessage(incoming=True, func=lambda e: e.is_private))
async def autodelete_handler(event):
    sender_id = str(event.sender_id)
    bl = load_blacklist()
    if sender_id in bl:
        try:
            await event.delete()
        except Exception:
            pass


print("Userbot запущен. Ожидаю команды...")
client.start()
client.run_until_disconnected()