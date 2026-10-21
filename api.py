import hashlib
import hmac
import json
import urllib.parse
from aiohttp import web
import sqlite3
from datetime import datetime, timedelta

# Импортируем функции из вашей базы данных
from database import get_user, get_balance, get_user_level, claim_daily, get_last_daily, add_balance, is_vip_active

# ВАШ ТОКЕН (тот же, что в air.py)
BOT_TOKEN = "8572154161:AAFLLxcagDzZYyvWrFBMhbkYdROxktSy8wo"

# --- ФУНКЦИЯ ПРОВЕРКИ ПОДПИСИ TELEGRAM ---
def validate_init_data(init_data: str) -> dict:
    """Проверяет, что данные пришли именно из Telegram."""
    try:
        parsed_data = dict(urllib.parse.parse_qsl(init_data))
        hash_str = parsed_data.pop('hash', None)
        if not hash_str:
            return None

        # Собираем строку для проверки
        data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(parsed_data.items()))
        
        # Секретный ключ
        secret_key = hmac.new(b"WebAppData", BOT_TOKEN.encode(), hashlib.sha256).digest()
        
        # Вычисляем хеш
        calculated_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

        if calculated_hash == hash_str:
            # Подпись верна! Возвращаем данные пользователя
            user_data = json.loads(parsed_data.get('user', '{}'))
            return user_data
        return None
    except Exception as e:
        print(f"[API] Ошибка валидации: {e}")
        return None

# --- ОБРАБОТЧИКИ ЗАПРОСОВ ---

async def handle_get_profile(request):
    """Отдает профиль пользователя."""
    init_data = request.headers.get('X-Telegram-Init-Data')
    if not init_data:
        return web.json_response({"error": "No init data"}, status=401)

    user_data = validate_init_data(init_data)
    if not user_data:
        return web.json_response({"error": "Invalid signature"}, status=403)

    user_id = user_data['id']
    
    # Получаем данные из вашей БД
    balance = get_balance(user_id)
    lvl = get_user_level(user_id)
    vip = is_vip_active(user_id)
    
    # Проверяем, доступен ли daily
    last_daily = get_last_daily(user_id)
    daily_available = True
    if last_daily:
        try:
            last_dt = datetime.fromisoformat(last_daily)
            if datetime.now() - last_dt < timedelta(hours=24):
                daily_available = False
        except ValueError:
            pass

    return web.json_response({
        "user_id": user_id,
        "name": user_data.get('first_name', 'Игрок'),
        "balance": balance,
        "level": lvl['level'],
        "level_title": lvl['title'],
        "vip": vip,
        "daily_available": daily_available
    })

async def handle_claim_daily(request):
    """Выдает ежедневный бонус."""
    init_data = request.headers.get('X-Telegram-Init-Data')
    if not init_data:
        return web.json_response({"error": "No init data"}, status=401)

    user_data = validate_init_data(init_data)
    if not user_data:
        return web.json_response({"error": "Invalid signature"}, status=403)

    user_id = user_data['id']
    
    # Проверяем кулдаун
    last_daily = get_last_daily(user_id)
    if last_daily:
        try:
            last_dt = datetime.fromisoformat(last_daily)
            if datetime.now() - last_dt < timedelta(hours=24):
                return web.json_response({"error": "Daily уже получен"}, status=400)
        except ValueError:
            pass

    # Начисляем (имитация логики из air.py, 500 msg)
    amount = 500
    new_balance = claim_daily(user_id, amount)
    
    return web.json_response({
        "success": True,
        "amount": amount,
        "new_balance": new_balance
    })

# --- ЗАПУСК СЕРВЕРА ---
app = web.Application()
app.router.add_get('/api/profile', handle_get_profile)
app.router.add_post('/api/daily', handle_claim_daily)

# Раздаем статические файлы (ваш index.html)
app.router.add_static('/', path='.', name='static')

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=8080)