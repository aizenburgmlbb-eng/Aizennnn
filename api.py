import os
import json
import hashlib
import hmac
import urllib.parse
import asyncio
import random
import sqlite3
from aiohttp import web
import aiohttp_cors
from datetime import datetime, timedelta

# Импорт БД
from database import (
    get_user, get_balance, get_user_level, claim_daily, get_last_daily, 
    add_balance, is_vip_active, init_db, treasury_ensure, get_user_rank,
    get_spouse, get_reputation, get_daily_streak, get_top, give_vip_days,
    buy_vip, log_transaction, is_lucky_active, increment_stat, BOT_TREASURY_ID,
    get_case_cooldown, set_case_cooldown, get_couple_info, wedding_case_get_cooldown,
    wedding_case_set_cooldown
)

# Импорт бота и фоновых задач из air.py
from air import (
    bot, dp, CASES, _roll_case_item, _roll_wedding_prize, 
    BUY_PACKAGES, _db_backup_loop,
)

BOT_TOKEN = "8572154161:AAFFCotXoo6S9wOBhmSgZzvPh_PTX3V7YmU"

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
    bank_balance = bank_get(user_id)['balance'] if 'bank_get' in globals() else 0
    lvl = get_user_level(user_id)
    vip = is_vip_active(user_id)
    rank = get_user_rank(user_id)
    rep = get_reputation(user_id)
    streak = get_daily_streak(user_id)
    
    vip_days = None
    if user_row[4]:
        try:
            until = datetime.fromisoformat(user_row[4])
            if until > datetime.now(): vip_days = (until - datetime.now()).days
        except ValueError: pass

    spouse_id = get_spouse(user_id)
    spouse_name = None
    if spouse_id:
        spouse_data = get_user(spouse_id)
        if spouse_data: spouse_name = spouse_data[2] or f"@{spouse_data[1]}"
    
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
        except ValueError: pass

    return web.json_response({
        "user_id": user_id,
        "custom_id": user_row[6] or 0,
        "registered_at": user_row[7] or "",
        "name": user_data.get('first_name', 'Игрок'),
        "avatar_url": None,
        "balance": balance,
        "bank_balance": bank_balance,
        "level": lvl['level'],
        "level_title": lvl['title'],
        "vip": vip,
        "vip_days": vip_days,
        "rank": rank,
        "rep": rep,
        "streak": streak,
        "spouse": spouse_name,
        "daily_available": daily_available,
        "daily_hours_left": hours_left
    })

async def handle_spin_wheel(request):
    init_data = request.headers.get('X-Telegram-Init-Data')
    user_data = validate_init_data(init_data) if init_data else None
    if not user_data: return web.json_response({"error": "Auth error"}, status=403)
    user_id = user_data['id']
    
    last_daily = get_last_daily(user_id)
    if last_daily:
        try:
            last_dt = datetime.fromisoformat(last_daily)
            if datetime.now() - last_dt < timedelta(hours=24):
                return web.json_response({"error": "Колесо уже крутили сегодня"}, status=400)
        except ValueError: pass

    prizes = [
        {"type": "msg", "value": 500, "chance": 30, "label": "500 msg", "emoji": "💰"},
        {"type": "msg", "value": 1000, "chance": 25, "label": "1000 msg", "emoji": "💰"},
        {"type": "msg", "value": 2500, "chance": 15, "label": "2500 msg", "emoji": "💰"},
        {"type": "msg", "value": 5000, "chance": 5, "label": "5000 msg", "emoji": "💰"},
        {"type": "vip", "value": 1, "chance": 15, "label": "VIP 1 день", "emoji": "👑"},
        {"type": "vip", "value": 3, "chance": 5, "label": "VIP 3 дня", "emoji": "👑"},
        {"type": "empty", "value": 0, "chance": 5, "label": "Пусто", "emoji": "💨"}
    ]
    
    roll = random.uniform(0, 100)
    acc = 0
    chosen = prizes[-1]
    for p in prizes:
        acc += p["chance"]
        if roll <= acc:
            chosen = p
            break

    if chosen["type"] == "msg":
        add_balance(user_id, chosen["value"])
        log_transaction(user_id, user_id, chosen["value"], "daily_wheel")
        msg = f"💰 Выигрыш: +{chosen['value']:,} msg"
    elif chosen["type"] == "vip":
        give_vip_days(user_id, chosen["value"])
        msg = f"👑 Выигрыш: VIP на {chosen['value']} дн."
    else:
        msg = "💨 Увы, сегодня пусто."

    claim_daily(user_id, 0)
    return web.json_response({"success": True, "prize": chosen, "msg": msg, "new_balance": get_balance(user_id)})

async def handle_get_top(request):
    init_data = request.headers.get('X-Telegram-Init-Data')
    if not validate_init_data(init_data): return web.json_response({"error": "Auth error"}, status=403)
    
    top = get_top(10)
    result = []
    for i, (uid, uname, fname, bal) in enumerate(top, 1):
        u_row = get_user(uid)
        c_id = u_row[6] if (u_row and len(u_row) > 6) else 0
        result.append({"place": i, "name": fname or uname or str(uid), "balance": int(bal or 0), "avatar": "", "custom_id": c_id or 0})
    return web.json_response(result)

async def handle_open_case(request):
    init_data = request.headers.get('X-Telegram-Init-Data')
    user_data = validate_init_data(init_data) if init_data else None
    if not user_data: return web.json_response({"error": "Auth error"}, status=403)
    user_id = user_data['id']
    try:
        data = await request.json()
        case_key = data.get('case_key')
    except: return web.json_response({"error": "Invalid data"}, status=400)

    if case_key not in CASES: return web.json_response({"error": "Кейс не найден"}, status=404)
    case_data = CASES[case_key]
    price = case_data["price"]
    is_wedding_case = case_data.get("is_wedding_case", False)
    is_vip = is_vip_active(user_id)

    if case_data.get("vip_only") and not is_vip: return web.json_response({"error": "👑 Только для VIP!"}, status=403)
    if case_data.get("is_pet_case"): return web.json_response({"error": "Кейсы питомцев доступны только в боте (/cases)"}, status=400)

    if is_wedding_case:
        couple_info = get_couple_info(user_id)
        if not couple_info.get("ok"): return web.json_response({"error": "❌ Только для пар!"}, status=403)
        last_case = wedding_case_get_cooldown(user_id)
        if last_case:
            try:
                last_dt = datetime.fromisoformat(last_case)
                if datetime.now() - last_dt < timedelta(hours=24): return web.json_response({"error": "⏳ Свадебный кейс на перезарядке"}, status=400)
            except ValueError: pass
        prize = _roll_wedding_prize()
        if prize["kind"] == "msg":
            add_balance(couple_info["user1_id"], prize["amount"])
            log_transaction(BOT_TREASURY_ID, couple_info["user1_id"], prize["amount"], "wedding_case_msg")
            res_text = f"💰 Пара получила: +{prize['amount']:,} msg"
        else:
            give_vip_days(couple_info["user1_id"], prize["vip_days"])
            give_vip_days(couple_info["user2_id"], prize["vip_days"])
            res_text = f"👑 VIP на {prize['vip_days']} дней каждому!"
        wedding_case_set_cooldown(user_id)
        return web.json_response({"success": True, "result_text": f"{prize['phrase']}\n{res_text}", "new_balance": get_balance(user_id)})

    last_open = get_case_cooldown(user_id, case_key)
    if last_open:
        try:
            last_dt = datetime.fromisoformat(last_open)
            cd_sec = case_data["cooldown_vip"] if is_vip else case_data["cooldown_normal"]
            if datetime.now() - last_dt < timedelta(seconds=cd_sec): return web.json_response({"error": "⏳ Кейс на перезарядке"}, status=400)
        except ValueError: pass

    balance = get_balance(user_id)
    if balance < price: return web.json_response({"error": f"😢 Недостаточно msg! Нужно: {price}"}, status=400)

    add_balance(user_id, -price)
    log_transaction(user_id, user_id, -price, "case")
    set_case_cooldown(user_id, case_key)

    kind, msg_amount, vip_days = _roll_case_item(case_data)
    if kind == "vip":
        give_vip_days(user_id, vip_days)
        result_text = f"👑 Выигрыш: VIP на {vip_days} дней"
    else:
        add_balance(user_id, msg_amount)
        profit = msg_amount - price
        result_text = f"💰 Выигрыш: +{msg_amount:,} msg\n└─ Профит: {profit:+,} msg"
    return web.json_response({"success": True, "result_text": result_text, "new_balance": get_balance(user_id)})

async def handle_casino(request):
    init_data = request.headers.get('X-Telegram-Init-Data')
    user_data = validate_init_data(init_data) if init_data else None
    if not user_data: return web.json_response({"error": "Auth error"}, status=403)
    user_id = user_data['id']
    try:
        data = await request.json()
        bet = int(data.get('bet', 1000))
    except: return web.json_response({"error": "Invalid data"}, status=400)

    if bet < 1000: return web.json_response({"error": "Минимальная ставка 1000 msg"}, status=400)
    balance = get_balance(user_id)
    if balance < bet: return web.json_response({"error": "😢 Недостаточно msg!"}, status=400)

    lucky = is_lucky_active(user_id)
    add_balance(user_id, -bet)
    
    win_chance = 0.59 if lucky else 0.44
    roll = random.random()
    CASINO_SLOTS = ["🍒", "🍋", "🍊", "⭐", "💎", "7️⃣"]

    if roll < 0.03:
        symbol = random.choice(CASINO_SLOTS)
        result = [symbol, symbol, symbol]
    elif roll < win_chance:
        symbol = random.choice(CASINO_SLOTS)
        other = random.choice([s for s in CASINO_SLOTS if s != symbol])
        positions = random.sample([0, 1, 2], 2)
        result = [other, other, other]
        result[positions[0]] = symbol
        result[positions[1]] = symbol
    else:
        result = random.sample(CASINO_SLOTS, 3)

    a, b, c = result
    mult = 0
    kind = "casino_lose"

    if a == b == c:
        multipliers = {"🍒": 4, "🍋": 5, "🍊": 6, "⭐": 8, "💎": 12, "7️⃣": 25}
        mult = multipliers[a]
        kind = "casino_jackpot" if a == "7️⃣" else "casino_win"
    elif a == b or b == c or a == c:
        mult = 1.5
        kind = "casino_win"

    win_amount = int(bet * mult) if mult > 0 else 0
    if win_amount > 0: add_balance(user_id, win_amount)

    log_transaction(user_id, user_id, win_amount - bet, kind)
    increment_stat(user_id, "total_casino_games", 1)
    if win_amount == 0: increment_stat(user_id, "total_casino_losses", bet)

    return web.json_response({"success": True, "result": result, "win_amount": win_amount, "mult": mult, "new_balance": get_balance(user_id), "is_jackpot": a == b == c and a == "7️⃣"})

async def handle_buy_vip(request):
    init_data = request.headers.get('X-Telegram-Init-Data')
    user_data = validate_init_data(init_data) if init_data else None
    if not user_data: return web.json_response({"error": "Auth error"}, status=403)
    user_id = user_data['id']
    try:
        data = await request.json()
        weeks = int(data.get('weeks', 0))
    except: return web.json_response({"error": "Invalid data"}, status=400)
    
    if weeks <= 0: return web.json_response({"error": "Неверное количество недель"}, status=400)
    ok, info = buy_vip(user_id, weeks)
    if not ok: return web.json_response({"error": info}, status=400)
    return web.json_response({"success": True, "new_balance": get_balance(user_id)})

async def handle_buy_vip_stars(request):
    init_data = request.headers.get('X-Telegram-Init-Data')
    user_data = validate_init_data(init_data) if init_data else None
    if not user_data: return web.json_response({"error": "Auth error"}, status=403)
    user_id = user_data['id']
    try:
        from aiogram.types import LabeledPrice
        invoice_link = await bot.create_invoice_link(
            title="VIP на 7 дней",
            description="Покупка VIP-статуса на 7 дней",
            payload=f"buyvip_{user_id}_7",
            provider_token="",
            currency="XTR",
            prices=[LabeledPrice(label="VIP", amount=10)]
        )
        return web.json_response({"success": True, "link": invoice_link})
    except Exception as e:
        print(f"[API] Ошибка инвойса VIP: {e}")
        return web.json_response({"error": "Ошибка создания счета"}, status=500)

async def handle_buy_stars_link(request):
    init_data = request.headers.get('X-Telegram-Init-Data')
    user_data = validate_init_data(init_data) if init_data else None
    if not user_data: return web.json_response({"error": "Auth error"}, status=403)
    user_id = user_data['id']
    try:
        data = await request.json()
        stars = int(data.get('stars'))
    except: return web.json_response({"error": "Invalid data"}, status=400)

    package = next((p for p in BUY_PACKAGES if p[1] == stars), None)
    if not package: return web.json_response({"error": "Пакет не найден"}, status=404)
    msg_amount = package[0]

    try:
        from aiogram.types import LabeledPrice
        invoice_link = await bot.create_invoice_link(
            title=f"{msg_amount:,} msg",
            description=f"Покупка {msg_amount:,} msg за {stars} ⭐",
            payload=f"buymsg_{user_id}_{stars}",
            provider_token="",
            currency="XTR",
            prices=[LabeledPrice(label="msg", amount=stars)]
        )
        return web.json_response({"success": True, "link": invoice_link})
    except Exception as e:
        return web.json_response({"error": "Ошибка создания счета"}, status=500)

async def index_handler(request):
    # АБСОЛЮТНЫЙ ПУТЬ к index.html
    file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'index.html')
    return web.FileResponse(file_path)

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
    asyncio.create_task(_db_backup_loop())
    print("[API] ✅ Фоновые задачи (бэкап) запущены")
    asyncio.create_task(start_bot())

# ─── ИНИЦИАЛИЗАЦИЯ ВЕБ-СЕРВЕРА ───
app = web.Application()
app.on_startup.append(on_startup)

app.router.add_get('/', index_handler)
app.router.add_get('/api/profile', handle_get_profile)
app.router.add_post('/api/spin_wheel', handle_spin_wheel)
app.router.add_get('/api/top', handle_get_top)
app.router.add_post('/api/open_case', handle_open_case)
app.router.add_post('/api/casino', handle_casino)
app.router.add_post('/api/buy_vip', handle_buy_vip)
app.router.add_post('/api/buy_vip_stars', handle_buy_vip_stars)
app.router.add_post('/api/buy_stars', handle_buy_stars_link)

cors = aiohttp_cors.setup(app, defaults={
    "*": aiohttp_cors.ResourceOptions(allow_credentials=True, expose_headers="*", allow_headers="*")
})
for route in list(app.router.routes()):
    cors.add(route)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    web.run_app(app, host='0.0.0.0', port=port)
