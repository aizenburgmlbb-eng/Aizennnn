import os
import json
import hashlib
import hmac
import urllib.parse
import asyncio
from aiohttp import web
import aiohttp_cors
from datetime import datetime, timedelta

# Импорт БД
from database import (
    get_user, get_balance, get_user_level, claim_daily, get_last_daily, 
    add_balance, is_vip_active, init_db, treasury_ensure
)

# Импорт бота и фоновых задач из air.py
from air import (
    bot, dp, CASES, _roll_case_item, _roll_wedding_prize, 
    BUY_PACKAGES, _db_backup_loop,
)

BOT_TOKEN = "8572154161:AAFLLxcagDzZYyvWrFBMhbkYdROxktSy8wo"

# ─── ВАЛИДАЦИЯ MINI APP ───
def validate_init_data(init_data: str) -> dict:
    try:
        parsed_data = dict(urllib.parse.parse_qsl(init_data))
        hash_str = parsed_data.pop('hash', None)
        if not hash_str:
            return None
        data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(parsed_data.items()))
        secret_key = hmac.new(b"WebAppData", BOT_TOKEN.encode(), hashlib.sha256).digest()
        calculated_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
        if calculated_hash == hash_str:
            return json.loads(parsed_data.get('user', '{}'))
        return None
    except Exception as e:
        print(f"[API] Ошибка валидации: {e}")
        return None

# ─── API ХЕНДЛЕРЫ ───
async def handle_get_profile(request):
    init_data = request.headers.get('X-Telegram-Init-Data')
    if not init_data:
        return web.json_response({"error": "No init data"}, status=401)
    user_data = validate_init_data(init_data)
    if not user_data:
        return web.json_response({"error": "Invalid signature"}, status=403)

    user_id = user_data['id']
    user_row = get_user(user_id)
    if not user_row:
        return web.json_response({"error": "User not found"}, status=404)

    balance = get_balance(user_id)
    lvl = get_user_level(user_id)
    vip = is_vip_active(user_id)
    
    last_daily = get_last_daily(user_id)
    daily_available = True
    hours_left = 0
    if last_daily:
        try:
            last_dt = datetime.fromisoformat(last_daily)
            elapsed = datetime.now() - last_dt
            if elapsed < timedelta(hours=24):
                daily_available = False
                hours_left = 24 - int(elapsed.total_seconds() // 3600)
        except ValueError:
            pass

    return web.json_response({
        "user_id": user_id,
        "custom_id": user_row[6] or 0,
        "registered_at": user_row[7] or "",
        "name": user_data.get('first_name', 'Игрок'),
        "balance": balance,
        "level": lvl['level'],
        "level_title": lvl['title'],
        "vip": vip,
        "daily_available": daily_available,
        "daily_hours_left": hours_left
    })

async def index_handler(request):
    return web.FileResponse('./index.html')

# ─── ЗАПУСК БОТА ───
async def start_bot():
    print("[API] Попытка запустить бота (polling)...")
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        print("[API] Вебхук удален, запускаем polling...")
        await dp.start_polling(bot)
    except Exception as e:
        print(f"[API] ❌ КРИТИЧЕСКАЯ ОШИБКА БОТА: {e}")

async def on_startup(app):
    print("[API] Инициализация БД...")
    init_db()
    treasury_ensure()
    
    # Запускаем фоновые задачи
    asyncio.create_task(_db_backup_loop())
    print("[API] ✅ Фоновые задачи (бэкап) запущены")
    
    # Запускаем бота
    asyncio.create_task(start_bot())

# ─── ИНИЦИАЛИЗАЦИЯ ВЕБ-СЕРВЕРА ───
app = web.Application()
app.on_startup.append(on_startup)

app.router.add_get('/', index_handler)
app.router.add_get('/api/profile', handle_get_profile)
# Добавь сюда свои остальные роуты из старого api.py (top, casino, case и т.д.)

# CORS для Mini App
cors = aiohttp_cors.setup(app, defaults={
    "*": aiohttp_cors.ResourceOptions(
        allow_credentials=True,
        expose_headers="*",
        allow_headers="*"
    )
})
for route in list(app.router.routes()):
    cors.add(route)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    web.run_app(app, host='0.0.0.0', port=port)