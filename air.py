from aiogram import Bot, Dispatcher
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.dispatcher.middlewares.base import BaseMiddleware
from typing import Any, Awaitable, Callable, Dict
from aiogram import F
import asyncio
import random
import sqlite3
import time
from datetime import datetime, timedelta, timezone
from aiogram.types import (
    Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton,
    LabeledPrice, PreCheckoutQuery,
)
from database import (
	log_payment, has_charge_id, get_payment_stats, get_user_payments,
	ttt_create, ttt_get, ttt_update, ttt_delete, get_user_ttt,
	get_stale_ttt, get_pending_ttt_older_than,
	get_stale_duels, get_pending_duels_older_than,
    ensure_user_stats, get_user_stats,
    increment_stat,
    ACHIEVEMENTS, get_achievement_info,
    unlock_achievement,
    get_user_achievements,
    get_achievement_count,
    get_next_achievement,
    check_all_achievements,
    duel_create, duel_get, duel_update, duel_delete, get_user_duel,
    give_vip_days,
    get_spouse, is_married, marry_users, divorce_users, get_marriage_date,
    get_marriage, get_marriage_balance, change_marriage_balance,
    get_balance, add_balance, add_msg_auto,
    get_bot_soon, set_bot_soon,
    clear_bot_soon,
    get_all_user_ids,
    get_case_cooldown, set_case_cooldown, clear_case_cooldown,
    init_db, ensure_user, get_user, change_balance, add_msg, set_balance,
    transfer_msg, buy_vip, log_transaction, is_vip_active,
    get_last_daily, claim_daily,
    get_daily_streak, set_daily_streak,
    get_top, get_top_bank, get_user_rank, get_history,
    calc_level, get_user_level,
    add_ban, get_active_ban, remove_ban, list_bans,
    bank_get, bank_put, bank_take, bank_ensure,
    get_nick, set_nick,
    get_title, set_title, clear_title,
    get_last_rob, set_last_rob,
    give_vip, remove_vip,
    log_anon, get_anon_logs,
    add_anon_mute, get_active_anon_mute, remove_anon_mute,
    get_bot_info, set_bot_info, get_bot_stats,
    add_shop_item, remove_shop_item, get_shop_item, get_shop_items,
    get_user_purchases_count, log_purchase,
    get_shield_until, set_shield_until, is_shield_active,
    get_hide_balance_until, set_hide_balance_until, is_hide_balance_active,
    get_anon_shield_until, set_anon_shield_until, is_anon_shield_active,
    get_lucky_until, set_lucky_until, is_lucky_active,
    add_access, remove_access, get_user_levels, has_access, get_all_admins,
    add_warn, get_user_warns, get_warn_count, remove_warn, clear_warns, get_all_warned,
    WARN_LIMIT, WARN_BAN_DAYS,
)

TOKEN = "8572154161:AAEcHzZnnI_CPAnxFSc2YbTkMgA3Aq79fNg"
OWNER_IDS = {7564741700}

# =========================================================
#  ПРЕМИУМ-ЭМОДЗИ (custom_emoji_id)
# =========================================================

# Статусы
PREM_CHECK = "5215492745900077682"  # ✅ галочка (открыто)
PREM_LOCK  = "5291873529464122510"  # 🔒 замок (не открыто)
PREM_TOP1  = "5332299818943400671"  # 🏆 топ1 (заголовок)

# Эмодзи достижений (по ach_id)
ACH_PREMIUM = {
    "first_step":       "5420548207031627277",  # 🎯 прицел
    "talker":           "5235814241927181048",  # 💬 сообщения
    "super_talker":     "5235814241927181048",  # 💬 сообщения
    "mega_talker":      "5235814241927181048",  # 💬 сообщения
    "saver":            "5987880246865565644",  # 💰 деньги
    "millionaire":      "5429153655045507054",  # 💎 алмаз
    "multimillionaire": "5413566144986503832",  # 🏆 кубок
    "gangster":         "5454292102923961799",  # 🥷 ниндзя
    "generous":         "5987880246865565644",  # 💸 деньги
    "rockefeller":      "5366223171454278937",  # 🏦 банк
    "worker":           "5190458330719461749",  # 🔥 труд
    "top1":             "5807868868886009920",  # 👑 корона
    "gambler":          "5226449843127340604",  # 🎰 слоты
    "ludoman":          "5429477976615961027",  # 🎲 кубик
    "family_man":       "5267214996936340701",  # 💍 кольцо
    "gladiator":        "5393607290228067750",  # ⚔️ мечи
}


def _p(emoji_id: str, fallback: str = "•") -> str:
    """Обёртка премиум-эмодзи в HTML-тег."""
    return f'<tg-emoji emoji-id="{emoji_id}">{fallback}</tg-emoji>'

FALLBACK_PHOTO = "AgACAgIAAxkBAAIHw2rBO_JkJf85SvqHSKn1-SUcX-HBAAKpHmsbvrQISv3mE3rfYsMOAQADAgADeAADPQQ"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Приглашения
_duel_invites: dict = {}
_marry_invites: dict = {}
_ttt_invites: dict = {}

DUEL_MIN_BET = 1000
DUEL_TIMEOUT = 300
DUEL_TURN_TIMEOUT = 60


# =========================================================
#  МИДЛВАРЬ: БАН
# =========================================================

class BanMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        if not event.from_user or event.from_user.is_bot:
            return await handler(event, data)

        user = event.from_user
        ensure_user(user)

        try:
            ban = get_active_ban(user.id)
        except Exception as e:
            print(f"[BAN-MW] Ошибка get_active_ban: {e}")
            ban = None

        if ban:
            reason, banned_until, _ = ban

            if banned_until is None:
                until_text = "навсегда"
            else:
                try:
                    until_dt = datetime.fromisoformat(banned_until)
                    remaining = until_dt - datetime.now()
                    days_left = max(1, remaining.days)
                    until_text = f"{days_left} дн. (до {until_dt.strftime('%d.%m.%Y %H:%M')})"
                except ValueError:
                    until_text = "—"

            try:
                await event.answer(
                    f"🚫 <b>Вы заблокированы</b>\n\n"
                    f"└─ Причина: <b>{reason}</b>\n"
                    f"└─ Срок: <b>{until_text}</b>",
                    parse_mode="HTML"
                )
            except Exception:
                pass
            return

        return await handler(event, data)


dp.message.middleware(BanMiddleware())
print("[STARTUP] BanMiddleware подключена")


# =========================================================
#  АНТИФЛУД
# =========================================================

_last_reward: dict[int, float] = {}
NORMAL_COOLDOWN = 2.0
VIP_COOLDOWN = 1.0

_last_casino: dict[int, float] = {}
CASINO_COOLDOWN = 20.0
CASINO_VIP_COOLDOWN = 10.0

# Локи для предотвращения race conditions на юзера
_user_locks: dict[int, asyncio.Lock] = {}


def get_user_lock(user_id: int) -> asyncio.Lock:
    """Возвращает (создаёт) Lock для юзера — защита от двойных нажатий."""
    if user_id not in _user_locks:
        _user_locks[user_id] = asyncio.Lock()
    return _user_locks[user_id]

async def _duel_watchdog():
    """Раз в 30 секунд проверяет брошенные дуэли."""
    while True:
        await asyncio.sleep(30)
        try:
            # 1) Активные дуэли старше DUEL_TIMEOUT — возврат ставок обоим
            stale = get_stale_duels(DUEL_TIMEOUT)
            for did in stale:
                duel = duel_get(did)
                if not duel:
                    continue

                (did_, ch_id, op_id, bet, status, hp1, hp2, am1, am2,
                 turn, msg_id, chat_id, *_rest) = duel

                # Возвращаем ставки
                add_balance(ch_id, bet)
                add_balance(op_id, bet)
                log_transaction(ch_id, op_id, bet, "duel_timeout")

                text = (
                    f"⏰ <b>Дуэль прервана по таймауту</b>\n\n"
                    f"└─ Ставки возвращены: по {bet} msg\n"
                    f"└─ Играйте внимательнее!"
                )

                if msg_id and chat_id:
                    try:
                        await bot.edit_message_text(
                            chat_id=chat_id, message_id=msg_id,
                            text=text, parse_mode="HTML", reply_markup=None
                        )
                    except Exception:
                        pass

                duel_delete(did)

            # 2) Pending-дуэли старше DUEL_TIMEOUT — просто удалить
            old_pending = get_pending_duels_older_than(DUEL_TIMEOUT)
            for did in old_pending:
                duel = duel_get(did)
                if duel:
                    duel_delete(did)

        except Exception as e:
            print(f"[DUEL-WATCHDOG] Ошибка: {e}")



# =========================================================
#  ПРОВЕРКА ДОСТУПА
# =========================================================

def is_main_owner(user_id: int) -> bool:
    return user_id in OWNER_IDS


def is_owner(user_id: int) -> bool:
    return is_main_owner(user_id) or has_access(user_id, "owner")


def is_econom(user_id: int) -> bool:
    return is_owner(user_id) or has_access(user_id, "econom")


def is_moder(user_id: int) -> bool:
    return is_owner(user_id) or has_access(user_id, "moder")


def is_senior(user_id: int) -> bool:
    return is_owner(user_id) or has_access(user_id, "senior")


def get_level_priority(user_id: int) -> int:
    if is_main_owner(user_id):
        return 5
    levels = get_user_levels(user_id)
    if "owner" in levels:
        return 4
    if "senior" in levels:
        return 3
    if "moder" in levels:
        return 2
    if "econom" in levels:
        return 1
    return 0


def can_touch(actor_id: int, target_id: int) -> tuple:
    if actor_id == target_id:
        return False, "❌ Нельзя применить к самому себе"

    actor_priority = get_level_priority(actor_id)
    target_priority = get_level_priority(target_id)

    if is_main_owner(target_id) and not is_main_owner(actor_id):
        return False, "❌ Нельзя трогать главного владельца"

    if is_main_owner(actor_id):
        return True, ""

    if actor_priority == 0:
        return False, "❌ У тебя нет прав"

    if target_priority >= actor_priority:
        return False, "❌ Нельзя трогать пользователя с равным или более высоким уровнем"

    return True, ""


def can_warn(actor_id: int, target_id: int) -> tuple:
    if actor_id == target_id:
        return False, "❌ Нельзя предупредить себя"

    actor_priority = get_level_priority(actor_id)
    target_priority = get_level_priority(target_id)

    if is_main_owner(target_id) and not is_main_owner(actor_id):
        return False, "❌ Нельзя предупредить главного владельца"

    if is_main_owner(actor_id):
        return True, ""

    if actor_priority == 0:
        return False, "❌ У тебя нет прав"

    if target_priority >= actor_priority:
        return False, "❌ Нельзя предупредить пользователя с равным или более высоким уровнем"

    if actor_priority == 2 and is_vip_active(target_id):
        return False, "❌ VIP защищён от предупреждений"

    return True, ""


# =========================================================
#  ВСПОМОГАТЕЛЬНОЕ
# =========================================================

def log_cmd(name: str, message: Message):
    user = message.from_user
    user_info = f"@{user.username}" if user.username else f"ID: {user.id}"
    time_str = datetime.now().strftime("%H:%M")
    print(f"\n[{time_str}] {name} | {user_info} | {user.full_name}")


def find_user_id(message: Message, arg: str):
    if message.reply_to_message and not message.reply_to_message.from_user.is_bot:
        u = message.reply_to_message.from_user
        return u.id, u.full_name

    if arg and arg.startswith("@"):
        uname = arg.lstrip("@")
        conn = sqlite3.connect("users.db")
        cur = conn.cursor()
        cur.execute(
            "SELECT user_id, full_name FROM users WHERE LOWER(username) = LOWER(?)",
            (uname,)
        )
        row = cur.fetchone()
        conn.close()
        if row:
            return row[0], row[1]
    return None, None


def _to_int(s):
    """Безопасный парсер целых положительных чисел."""
    if s is None:
        return None
    try:
        v = int(s)
    except (ValueError, TypeError):
        return None
    if v < 0:
        return None
    return v


def _parse_user_amount(message: Message, args: list):
    """Парсит target и amount. Возвращает (target_id, target_name, amount)."""
    target_arg = None
    amount_str = None

    if message.reply_to_message:
        if args:
            amount_str = args[0]
        target = message.reply_to_message.from_user
        if target.is_bot:
            return None, None, None
        ensure_user(target)
        return target.id, target.full_name, _to_int(amount_str)
    else:
        if len(args) < 2:
            return None, None, None
        target_arg = args[0]
        amount_str = args[1]

    target_id, target_name = find_user_id(message, target_arg)
    return target_id, target_name, _to_int(amount_str)


def ensure_user_by_id(user_id: int):
    conn = sqlite3.connect("users.db")
    cur = conn.cursor()
    cur.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
    if cur.fetchone() is None:
        cur.execute(
            "INSERT INTO users (user_id, username, full_name, msg_count, vip_until, last_daily, last_activity) "
            "VALUES (?, NULL, NULL, 0, NULL, NULL, ?)",
            (user_id, datetime.now().isoformat())
        )
        conn.commit()
    conn.close()


def _shortage_hint(needed: int, have: int) -> str:
    missing = needed - have
    return (
        f"\n\n💡 <b>Как заработать:</b>\n"
        f"└─ 🎁 /daily — бонус раз в день\n"
        f"└─ 🎰 /casino — попытать удачу\n"
        f"└─ 🎯 Не хватает: <b>{missing}</b> msg"
    )

# =========================================================
#  КЕЙСЫ
# =========================================================

CASES = {
    "case": {
        "name": "🎁 Обычный кейс",
        "price": 1000,
        "cooldown_normal": 10 * 60,
        "cooldown_vip": 5 * 60,
        "items": [
            ("🥉", "Бронза",  0,  40, 500,    0),
            ("🥈", "Серебро", 40, 70, 1000,   0),
            ("🥇", "Золото",  70, 85, 2500,   0),
            ("💰", "Куш",     85, 95, 5000,   0),
            ("💎", "Алмаз",   95, 99, 10000,  0),
            ("👑", "VIP",     99, 100, 0,     3),
        ],
    },
    "rarecase": {
        "name": "💎 Редкий кейс",
        "price": 5000,
        "cooldown_normal": 30 * 60,
        "cooldown_vip": 15 * 60,
        "items": [
            ("🥈", "Серебро",  0,  35, 3000,  0),
            ("🥇", "Золото",   35, 65, 7000,  0),
            ("💰", "Куш",      65, 85, 15000, 0),
            ("💎", "Алмаз",    85, 95, 30000, 0),
            ("🛡️", "Щит",      95, 98.5, 30000, 0),
            ("👑", "VIP",      98.5, 100, 0,   7),
        ],
    },
    "lcase": {
        "name": "👑 Легендарный кейс",
        "price": 25000,
        "cooldown_normal": 60 * 60,
        "cooldown_vip": 30 * 60,
        "items": [
            ("💰", "Куш",        0,  40, 20000, 0),
            ("💎", "Алмаз",      40, 70, 40000, 0),
            ("👑", "VIP",        70, 85, 20000, 3),
            ("🏆", "VIP+",       85, 95, 40000, 7),
            ("🌟", "ДЖЕКПОТ",    95, 99, 100000, 0),
            ("💎👑", "МЕГА",     99, 99.9, 250000, 30),
            ("🎰", "ЛЕГЕНДА",    99.9, 100, 500000, 90),
        ],
    },
}


def _roll_case_item(items: list):
    roll = random.random() * 100
    for emoji, name, min_p, max_p, msg_r, vip_d in items:
        if min_p <= roll < max_p:
            return emoji, name, msg_r, vip_d
    emoji, name, _, _, msg_r, vip_d = items[-1]
    return emoji, name, msg_r, vip_d


def _render_case_grid(items_pool: list, size: int = 3):
    lines = []
    for _ in range(size):
        row = [random.choice(items_pool) for _ in range(size)]
        lines.append(" | ".join(row))
    return "\n".join(lines)


async def _open_case_animation(message, case_key, result_emoji, result_name,
                                reward_msg, reward_vip, new_balance, chance):
    case_data = CASES[case_key]
    pool = [item[0] for item in case_data["items"]]

    msg = await message.answer(
        f"🎁 <b>Открываем {case_data['name']}…</b>\n\n"
        f"{_render_case_grid(pool, 3)}",
        parse_mode="HTML"
    )

    for _ in range(6):
        await asyncio.sleep(0.4)
        try:
            await msg.edit_text(
                f"🎁 <b>Открываем {case_data['name']}…</b>\n\n"
                f"{_render_case_grid(pool, 3)}",
                parse_mode="HTML"
            )
        except Exception:
            pass

    await asyncio.sleep(0.4)

    reward_text = ""
    if reward_msg > 0:
        reward_text = f"└─ Награда: <b>+{reward_msg}</b> msg\n"
    if reward_vip > 0:
        if reward_msg > 0:
            reward_text += f"└─ 👑 VIP на <b>{reward_vip}</b> дней\n"
        else:
            reward_text = f"└─ 👑 VIP на <b>{reward_vip}</b> дней\n"

    result_text = (
        f"{result_emoji} <b>{result_name.upper()}!</b>\n"
        f"└─ Шанс: {chance:.1f}%\n"
        f"{reward_text}"
        f"└─ Баланс: {new_balance} msg"
    )

    try:
        await msg.edit_text(
            f"🎁 <b>{case_data['name']} открыт!</b>\n\n"
            f"┌─────────────┐\n"
            f"│ {result_emoji} {result_name.upper()}\n"
            f"└─────────────┘\n\n"
            f"{result_text}",
            parse_mode="HTML"
        )
    except Exception:
        await message.answer(result_text, parse_mode="HTML")


async def _handle_case_open(message: Message, case_key: str):
    log_cmd(f"🎁 /{case_key}", message)
    user = message.from_user
    ensure_user(user)

    lock = get_user_lock(user.id)
    async with lock:
        case_data = CASES[case_key]
        price = case_data["price"]

        vip = is_vip_active(user.id)
        cooldown_seconds = case_data["cooldown_vip"] if vip else case_data["cooldown_normal"]
        cooldown = timedelta(seconds=cooldown_seconds)

        last_open = get_case_cooldown(user.id, case_key)
        if last_open:
            try:
                last_dt = datetime.fromisoformat(last_open)
                elapsed = datetime.now() - last_dt
                if elapsed < cooldown:
                    remaining = cooldown - elapsed
                    m = remaining.seconds // 60
                    s = remaining.seconds % 60
                    time_text = f"{m} мин {s} сек" if m > 0 else f"{s} сек"
                    vip_hint = "" if vip else "\n\n💡 С VIP кулдаун короче в 2 раза"
                    await message.answer(
                        f"⏳ <b>Кейс на перезарядке</b>\n"
                        f"└─ Ждать: <b>{time_text}</b>{vip_hint}",
                        parse_mode="HTML"
                    )
                    return
            except ValueError:
                pass

        balance = get_balance(user.id)
        if balance < price:
            missing = price - balance
            await message.answer(
                f"😢 <b>Недостаточно msg!</b>\n\n"
                f"└─ Нужно: {price}\n"
                f"└─ У тебя: {balance}\n"
                f"└─ 💡 Не хватает: {missing}",
                parse_mode="HTML"
            )
            return

        # ✅ Списываем и запускаем кулдаун ПОСЛЕ успешного списания
        new_balance_before = add_balance(user.id, -price)
        log_transaction(user.id, user.id, -price, "case")
        set_case_cooldown(user.id, case_key)

    emoji, name, reward_msg, reward_vip = _roll_case_item(case_data["items"])

    chance = 0
    for e, n, min_p, max_p, m_r, v_d in case_data["items"]:
        if n == name:
            chance = max_p - min_p
            break

    if reward_msg > 0:
        new_balance = add_balance(user.id, reward_msg)
    else:
        new_balance = get_balance(user.id)

    if reward_vip > 0:
        give_vip_days(user.id, reward_vip)

    await _open_case_animation(
        message, case_key, emoji, name,
        reward_msg, reward_vip, new_balance, chance
    )


# =========================================================
#  БРАК
# =========================================================

MARRY_PRICE = 5000
MARRY_MIN_LEVEL = 25
MARRY_TIMEOUT = 3600


# ====================================
#  ПРОФИЛЬ
# ====================================

def _build_profile_page(target_id: int, viewer_id: int, page: int) -> tuple:
    """Собирает текст страницы профиля с пагинацией."""
    ensure_user_by_id(target_id)
    data = get_user(target_id)

    if not data:
        return None, None

    uid, uname, fname, _balance_local, vip_until, last_daily = data
    balance = get_balance(uid)

    PROFILE_PAGES = 3
    if page < 0:
        page = 0
    if page >= PROFILE_PAGES:
        page = PROFILE_PAGES - 1

    # ─── Навигация: [ 1 ] [ •2• ] [ 3 ] ───
    nav_row = []
    for p in range(PROFILE_PAGES):
        if p == page:
            nav_row.append(InlineKeyboardButton(
                text=f"• {p + 1} •",
                callback_data="prof_noop"
            ))
        else:
            nav_row.append(InlineKeyboardButton(
                text=f"{p + 1}",
                callback_data=f"prof_page_{viewer_id}_{target_id}_{p}"
            ))

    kb_rows = [nav_row]

    # Кнопка бонуса — только для себя и только на стр. 0
    if viewer_id == uid and page == 0:
        daily_available = True
        if last_daily:
            try:
                last_dt = datetime.fromisoformat(last_daily)
                if datetime.now() - last_dt < DAILY_COOLDOWN:
                    daily_available = False
            except ValueError:
                pass
        if daily_available:
            kb_rows.insert(0, [InlineKeyboardButton(
                text="🎁 Бонус", callback_data="prof_daily"
            )])

    kb = InlineKeyboardMarkup(inline_keyboard=kb_rows)

    # ═══════════════════════════════════════════
    #  СТРАНИЦА 0 — ОСНОВНОЕ + БАНК
    # ═══════════════════════════════════════════
    if page == 0:
        nick, _ = get_nick(uid)
        display_name = nick or fname
        lvl = get_user_level(uid)

        bank_info = bank_get(uid)
        bank_line = f"🏦 Банк: <b>{bank_info['balance']:,}</b> msg"

        text = (
            f"👤 <b>{fname}</b> | <code>{uid}</code>\n"
            f"💰 Баланс: <b>{balance:,}</b> msg\n"
            f"{bank_line}\n"
            f"👻 Имя: <b>{display_name}</b>\n"
            f"\n"
            f"📤 Уровень: <b>{lvl['level']}</b> — {lvl['title']}\n"
            f"✨ msg: <b>{lvl['current_progress']:,}/{lvl['next_required']:,}</b>"
        )

    # ═══════════════════════════════════════════
    #  СТРАНИЦА 1 — СТАТУС
    # ═══════════════════════════════════════════
    elif page == 1:
        vip_line = "нет"
        if vip_until:
            try:
                until = datetime.fromisoformat(vip_until)
                if until > datetime.now():
                    vip_line = f"до {until.strftime('%d.%m.%Y %H:%M')}"
            except ValueError:
                pass

        streak = get_daily_streak(uid)
        daily_line = "✅ доступен"
        if last_daily:
            try:
                last_dt = datetime.fromisoformat(last_daily)
                elapsed = datetime.now() - last_dt
                if elapsed < DAILY_COOLDOWN:
                    remaining = DAILY_COOLDOWN - elapsed
                    h = remaining.seconds // 3600
                    m = (remaining.seconds % 3600) // 60
                    daily_line = f"⏱️ {h}ч {m}м"
            except ValueError:
                pass

        warn_count = get_warn_count(uid)
        if warn_count >= WARN_LIMIT:
            warn_line = f"\n⚠️ Варны: <b>{warn_count}/{WARN_LIMIT}</b> (лимит!)"
        elif warn_count > 0:
            warn_line = f"\n⚠️ Варны: <b>{warn_count}/{WARN_LIMIT}</b>"
        else:
            warn_line = ""

        text = (
            f"▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰\n"
            f"👑 <b>СТАТУС</b>\n"
            f"▱▱▱▱▱▱▱▱▱▱▱▱▱▱▱▱▱\n\n"
            f"👑 VIP: <b>{vip_line}</b>\n"
            f"🎁 /daily: <b>{daily_line}</b>\n"
            f"🔥 Streak: <b>{streak}/7</b>"
            f"{warn_line}"
        )

    # ═══════════════════════════════════════════
    #  СТРАНИЦА 2 — ТОП + ДОСТИЖЕНИЯ
    # ═══════════════════════════════════════════
    else:
        rank = get_user_rank(uid)

        ach_count = get_achievement_count(uid)
        ach_list = get_user_achievements(uid)
        ach_emojis = []
        for ach_id in ach_list[:10]:
            info = get_achievement_info(ach_id)
            if info:
                ach_emojis.append(info[0])
        ach_emojis_line = " ".join(ach_emojis) if ach_emojis else "нет"

        next_ach = get_next_achievement(uid)
        if next_ach:
            (n_id, n_emoji, n_name, n_current, n_threshold, n_percent) = next_ach
            filled_ach = int(n_percent / 10)
            ach_bar = "▰" * filled_ach + "▱" * (10 - filled_ach)
            next_block = (
                f"\n\n🎯 <b>Следующее:</b>\n"
                f"└─ {n_emoji} «{n_name}»: {n_current:,}/{n_threshold:,}\n"
                f"└─ {ach_bar} {n_percent}%"
            )
        else:
            next_block = "\n\n🏆 <b>Все достижения открыты!</b>"

        text = (
            f"▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰\n"
            f"🏆 <b>ПРОГРЕСС</b>\n"
            f"▱▱▱▱▱▱▱▱▱▱▱▱▱▱▱▱▱\n\n"
            f"🏆 Место в топе: <b>#{rank}</b>\n"
            f"🏅 Достижения: <b>{ach_count}/{len(ACHIEVEMENTS)}</b>\n"
            f"└─ {ach_emojis_line}"
            f"{next_block}"
        )

    return text, kb


async def _get_avatar_photo(user_id: int, viewer_id: int, target_vip: bool):
    if user_id == viewer_id or target_vip:
        try:
            photos = await bot.get_user_profile_photos(user_id, limit=1)
            if photos.total_count > 0:
                return photos.photos[0][-1].file_id
        except Exception as e:
            print(f"[AVATAR] Ошибка для {user_id}: {e}")
        return FALLBACK_PHOTO
    return FALLBACK_PHOTO


def build_bank_text_and_kb(user_id):
    info = bank_get(user_id)
    vip = is_vip_active(user_id)
    rate = "2%" if vip else "1%"

    earned_line = ""
    if info["earned_now"] > 0:
        earned_line = f"\n└─ 💵 Начислено сейчас: <b>+{info['earned_now']}</b> msg"

    now_kr = datetime.now(timezone(timedelta(hours=7))).replace(tzinfo=None)
    minutes_left = 60 - now_kr.minute
    if minutes_left == 60:
        minutes_left = 0
    next_line = f"\n└─ ⏳ Следующее начисление через: {minutes_left} мин"

    vip_note = " 👑" if vip else ""

    text = (
        f"🏦 <b>Твой банк</b>{vip_note}\n\n"
        f"└─ 💰 На счету: <b>{info['balance']}</b> msg\n"
        f"└─ 📈 Ставка: <b>{rate} в час</b> (в :00 по Красноярску)"
        f"{earned_line}"
        f"{next_line}\n"
        f"└─ 💎 Всего заработано: {info['total_earned']} msg"
    )

    kb_rows = []
    if info["balance"] > 0:
        kb_rows.append([InlineKeyboardButton(
            text=f"💸 Снять всё ({info['balance']})",
            callback_data=f"bank_take_all_{user_id}"
        )])

    kb = InlineKeyboardMarkup(inline_keyboard=kb_rows)
    return text, kb

# =========================================================
#  КОНСТАНТЫ
# =========================================================

DAILY_AMOUNT = 500
DAILY_VIP_AMOUNT = 1000
DAILY_COOLDOWN = timedelta(hours=24)
DAILY_STREAK_RESET = timedelta(hours=25)

ROB_COOLDOWN = timedelta(hours=1)
PRICE_ANON = 600

_last_daily_reminder: dict = {}
DAILY_REMINDER_COOLDOWN = 12 * 3600


async def _daily_reminder(user_id: int, chat_id: int):
    now = time.monotonic()
    last = _last_daily_reminder.get(user_id, 0)
    if now - last < DAILY_REMINDER_COOLDOWN:
        return

    last_daily = get_last_daily(user_id)
    if last_daily:
        try:
            last_dt = datetime.fromisoformat(last_daily)
            if datetime.now() - last_dt < DAILY_COOLDOWN:
                return
        except ValueError:
            pass

    streak = get_daily_streak(user_id)
    if streak <= 0:
        return

    _last_daily_reminder[user_id] = now
    try:
        await bot.send_message(
            chat_id,
            f"🎁 <b>Ты ещё не забирал ежедневный бонус!</b>\n\n"
            f"└─ 🔥 Streak: {streak}/7 (не потеряй!)\n"
            f"└─ 💰 Награда ждёт\n\n"
            f"Забрать: /daily",
            parse_mode="HTML"
        )
    except Exception:
        pass


# =====================================
#  /start
# =====================================

@dp.message(Command("start"))
async def cmd_start(message: Message):
    log_cmd("🚀 /start", message)
    user = message.from_user
    ensure_user(user)
    balance = get_balance(user.id)

    GREET = '<tg-emoji emoji-id="5343984088493599366">👋</tg-emoji>'
    MONEY = '<tg-emoji emoji-id="5987880246865565644">💰</tg-emoji>'

    if balance > 0:
        text = (
            f"{GREET} С возвращением, <b>{user.full_name}</b>!\n\n"
            f"└─ {MONEY} Твой баланс: <b>{balance:,}</b> msg\n\n"
            f"Список команд — /help"
        )
    else:
        text = (
            f"{GREET} Привет, <b>{user.full_name}</b>!\n\n"
            f"Добро пожаловать в бота-экономику с валютой <b>msg</b> {MONEY}\n\n"
            f"<b>С чего начать:</b>\n"
            f"└─ /daily — забери первый бонус (500 msg)\n"
            f"└─ {MONEY} /balance — проверь баланс\n"
            f"└─ /top — посмотри на богачей\n"
            f"└─ /help — все команды\n\n"
            f"<b>Как заработать:</b>\n"
            f"└─ +1 msg за каждое сообщение (раз в 2 сек)\n"
            f"└─ /daily — раз в день\n"
            f"└─ /casino — попытать удачу\n\n"
            f"Удачи! 🍀"
        )

    await message.answer(text, parse_mode="HTML")
    await _daily_reminder(user.id, message.chat.id)


# =========================================================
#  /version
# =========================================================

@dp.message(Command("version"))
async def cmd_version(message: Message):
    log_cmd("📌 /version", message)
    version = get_bot_info("version") or "1.07"
    changelog = get_bot_info("changelog") or "нет изменений"
    soon = get_bot_soon()

    text = (
        f"📌 <b>Версия — {version}</b>\n\n"
        f"<b>Что нового:</b>\n"
        f"{changelog}"
    )
    if soon:
        text += f"\n\n━━━━━━━━━━━━━━━\n\n{soon}"

    await message.answer(text, parse_mode="HTML")


# =========================================================
#  /help
# =========================================================

HELP_PER_PAGE = 10

HELP_COMMANDS = [
    ("🚀", "/start", "начать"),
    ("👤", "/profile", "твой профиль"),
    ("🎭", "/nick", "сменить ник"),
    ("🏷️", "/title", "установить титул"),
    ("🏆", "/top", "топ-10 богачей"),
    ("📜", "/history", "последние транзакции"),
    ("❌", "/ttt", "крестики-нолики на ставку"),
    ("🎁", "/gift", "подарить msg"),
    ("🥷", "/rob", "ограбить (1 час)"),
    ("🏦", "/bank", "твой банк"),
    ("📥", "/bankput", "положить в банк"),
    ("📤", "/banktake", "снять из банка"),
    ("💌", "/anon", "анонимка (600 msg)"),
    ("👑", "/buyvip", "VIP (1 нед = 1000 msg)"),
    ("🎁", "/daily", "ежедневный бонус (500 msg)"),
    ("🎰", "/casino", "казино (x1.5–x25)"),
    ("🎁", "/case", "обычный кейс (1000 msg)"),
    ("💎", "/rarecase", "редкий кейс (5000 msg)"),
    ("👑", "/lcase", "легендарный кейс (25000 msg)"),
    ("💍", "/marry", "предложить брак"),
    ("💔", "/divorce", "развод"),
    ("⚔️", "/duel", "дуэль 1 на 1"),
    ("🏅", "/achievements", "все достижения"),
    ("👑", "/vipinfo", "что даёт VIP"),
    ("📌", "/version", "версия бота"),
    ("📖", "/help", "этот список"),
]


def _build_help_page(page: int, is_admin: bool) -> tuple:
    total = len(HELP_COMMANDS)
    total_pages = max(1, (total + HELP_PER_PAGE - 1) // HELP_PER_PAGE)

    if page < 0:
        page = 0
    if page >= total_pages:
        page = total_pages - 1

    start = page * HELP_PER_PAGE
    end = start + HELP_PER_PAGE
    page_items = HELP_COMMANDS[start:end]

    lines = [f"📖 <b>Помощь — {page + 1}/{total_pages}</b>\n"]
    for emoji, cmd, desc in page_items:
        lines.append(f"{emoji} <code>{cmd}</code> — {desc}")

    if page == total_pages - 1:
        lines.append(
            "\n<b>Как заработать msg:</b>\n"
            "└─ +1 msg за сообщение (раз в 2 сек)\n"
            "└─ Для VIP: +1 msg раз в 1 сек 👑\n"
            "└─ 🎁 /daily — раз в день\n"
            "└─ 🏦 Банк: 1%/час (VIP 2%/час)"
        )
        if is_admin:
            lines.append("\n👑 <code>/own</code> — твои команды")

    text = "\n".join(lines)

    nav_row = []
    if page > 0:
        nav_row.append(InlineKeyboardButton(
            text="⬅️ Назад", callback_data=f"help_page_{page - 1}"
        ))
    nav_row.append(InlineKeyboardButton(
        text=f"{page + 1}/{total_pages}", callback_data="help_noop"
    ))
    if page < total_pages - 1:
        nav_row.append(InlineKeyboardButton(
            text="Вперёд ➡️", callback_data=f"help_page_{page + 1}"
        ))

    kb = InlineKeyboardMarkup(inline_keyboard=[nav_row])
    return text, kb


@dp.message(Command("help"))
async def cmd_help(message: Message):
    log_cmd("📖 /help", message)
    user_id = message.from_user.id
    is_admin = is_owner(user_id) or bool(get_user_levels(user_id))
    text, kb = _build_help_page(0, is_admin)

    await message.answer(
        text, parse_mode="HTML", reply_markup=kb,
        reply_to_message_id=message.message_id
    )


@dp.callback_query(lambda c: c.data.startswith("help_page_"))
async def cb_help_page(callback: CallbackQuery):
    parts = callback.data.split("_")
    if len(parts) != 3:
        await callback.answer("⚠️ Ошибка данных", show_alert=True)
        return
    try:
        page = int(parts[2])
    except ValueError:
        await callback.answer("⚠️ Ошибка данных", show_alert=True)
        return

    user_id = callback.from_user.id
    is_admin = is_owner(user_id) or bool(get_user_levels(user_id))
    text, kb = _build_help_page(page, is_admin)

    try:
        if callback.message.photo:
            await callback.message.edit_caption(caption=text, parse_mode="HTML", reply_markup=kb)
        else:
            await callback.message.edit_text(text, parse_mode="HTML", reply_markup=kb)
    except Exception as e:
        print(f"[HELP] Ошибка редактирования: {e}")
    await callback.answer()


@dp.callback_query(lambda c: c.data == "help_noop")
async def cb_help_noop(callback: CallbackQuery):
    await callback.answer()

# =========================================================
#  ПЛАТЕЖИ ЗА STARS
# =========================================================

STARS_TO_MSG = 1000   # 1 звезда = 1000 msg

# Пакеты msg
BUY_PACKAGES = [
    (1_000,    1),
    (5_000,    5),
    (10_000,   10),
    (50_000,   50),
    (100_000,  100),
]

# =========================================================
#  /buymsg — покупка msg за звёзды
# =========================================================

@dp.message(Command("buymsg"))
async def cmd_buymsg(message: Message):
    log_cmd("⭐ /buymsg", message)
    user = message.from_user
    ensure_user(user)

    # Формируем кнопки 2 в ряд
    rows = []
    row = []
    for msg_amount, stars in BUY_PACKAGES:
        row.append(InlineKeyboardButton(
            text=f"{msg_amount:,} msg — {stars}⭐",
            callback_data=f"buy_pkg_{msg_amount}"
        ))
        if len(row) == 2:
            rows.append(row)
            row = []

    if row:
        rows.append(row)

    kb = InlineKeyboardMarkup(inline_keyboard=rows)

    await message.answer(
        f"⭐ <b>Покупка msg за Telegram Stars</b>\n\n"
        f"└─ Курс: <b>1 ⭐ = {STARS_TO_MSG:,} msg</b>\n"
        f"└─ Минимальный пакет: {BUY_PACKAGES[0][0]:,} msg\n\n"
        f"<b>Выбери пакет:</b>",
        parse_mode="HTML",
        reply_markup=kb
    )

@dp.callback_query(lambda c: c.data.startswith("buy_pkg_"))
async def cb_buy_pkg(callback: CallbackQuery):
    data = callback.data

    try:
        msg_amount = int(data.replace("buy_pkg_", ""))
    except ValueError:
        await callback.answer("⚠️ Ошибка данных", show_alert=True)
        return

    # Находим пакет
    stars = None
    for m, s in BUY_PACKAGES:
        if m == msg_amount:
            stars = s
            break

    if stars is None:
        await callback.answer("⚠️ Пакет не найден", show_alert=True)
        return

    user_id = callback.from_user.id
    ensure_user(callback.from_user)

    # Отправляем счёт
    try:
        await bot.send_invoice(
            chat_id=callback.message.chat.id,
            title=f"{msg_amount:,} msg",
            description=f"Покупка {msg_amount:,} msg за {stars} ⭐",
            payload=f"buymsg_{user_id}_{msg_amount}",
            provider_token="",
            currency="XTR",
            prices=[LabeledPrice(label="msg", amount=stars)],
        )
    except Exception as e:
        print(f"[PAYMENT] Ошибка отправки счёта: {e}")
        await callback.answer(
            "❌ Не удалось создать счёт, попробуй позже",
            show_alert=True
        )
        return

    await callback.answer()

    # Опционально — удаляем клавиатуру выбора пакета
    try:
        await callback.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass

@dp.pre_checkout_query()
async def pre_checkout_handler(pre_checkout_query: PreCheckoutQuery):
    """Подтверждаем платёж (10 секунд на ответ)."""
    try:
        await pre_checkout_query.answer(ok=True)
        print(f"[PAYMENT] Pre-checkout OK: user={pre_checkout_query.from_user.id}")
    except Exception as e:
        print(f"[PAYMENT] Ошибка pre-checkout: {e}")
        try:
            await pre_checkout_query.answer(
                ok=False,
                error_message="Ошибка обработки, попробуйте позже"
            )
        except Exception:
            pass

@dp.message(F.successful_payment)
async def successful_payment_handler(message: Message):
    """Обрабатываем успешный платёж."""
    user = message.from_user
    payment = message.successful_payment

    print(f"[PAYMENT] ✅ Успех: user={user.id}, "
          f"total={payment.total_amount}, "
          f"charge={payment.telegram_payment_charge_id}")

    # 🔒 Идемпотентность: не начисляем второй раз
    if has_charge_id(payment.telegram_payment_charge_id):
        await message.answer(
            "⚠️ Этот платёж уже был обработан",
            parse_mode="HTML"
        )
        return

    # 🔍 Валидация payload
    try:
        parts = payment.invoice_payload.split("_")
        # Формат: buymsg_{user_id}_{msg_amount}
        if len(parts) != 3 or parts[0] != "buymsg":
            raise ValueError("Неверный формат payload")

        payload_user_id = int(parts[1])
        msg_amount = int(parts[2])

        if payload_user_id != user.id:
            raise ValueError("Payload не совпадает с пользователем")

        # Проверяем, что msg_amount соответствует оплаченным звёздам
        expected_stars = msg_amount // STARS_TO_MSG
        if payment.total_amount != expected_stars:
            raise ValueError("Сумма не совпадает")

    except (ValueError, IndexError) as e:
        print(f"[PAYMENT] ❌ Ошибка payload: {e}")
        await message.answer(
            "❌ <b>Ошибка валидации платежа</b>\n"
            "Обратитесь в поддержку: /paysupport",
            parse_mode="HTML"
        )
        return

    # 💰 Начисляем msg
    ensure_user(user)
    new_balance = add_balance(user.id, msg_amount)

    # 📝 Логируем
    log_payment(
        user.id,
        payment.total_amount,
        msg_amount,
        payment.telegram_payment_charge_id,
        payment.provider_payment_charge_id or ""
    )
    log_transaction(user.id, user.id, msg_amount, "stars_buy")

    # 🎉 Уведомляем
    await message.answer(
        f"✅ <b>Платёж получен!</b>\n\n"
        f"└─ ⭐ Оплачено: <b>{payment.total_amount}</b> Stars\n"
        f"└─ 💰 Начислено: <b>+{msg_amount:,}</b> msg\n"
        f"└─ Баланс: {new_balance:,} msg\n\n"
        f"💡 Спасибо за поддержку!",
        parse_mode="HTML"
    )

    # 🏆 Проверка достижений
    await _check_and_notify_achievements(user.id, message.chat.id)

@dp.message(Command("paysupport"))
async def cmd_paysupport(message: Message):
    log_cmd("💬 /paysupport", message)
    await message.answer(
        "💬 <b>Поддержка по платежам</b>\n\n"
        "Если платёж прошёл, но msg не начислились — напишите:\n"
        "└─ @твой_юзернейм\n\n"
        "При обращении укажите:\n"
        "└─ ID платежа (из чека Telegram)\n"
        "└─ Дату и сумму",
        parse_mode="HTML"
    )

# ======================================
#  /profile
# ======================================

@dp.message(Command("profile"))
async def cmd_profile(message: Message):
    log_cmd("👤 /profile", message)
    target = message.from_user

    if message.reply_to_message and not message.reply_to_message.from_user.is_bot:
        target = message.reply_to_message.from_user
    else:
        args = message.text.split()[1:]
        if args and args[0].startswith("@"):
            found_id, found_name = find_user_id(message, args[0])
            if found_id is None:
                await message.answer("❌ Пользователь не найден")
                return

            class TargetObj:
                pass

            target = TargetObj()
            target.id = found_id
            target.username = None
            target.full_name = found_name
            target.is_bot = False
            ensure_user_by_id(found_id)

    ensure_user_by_id(target.id)
    text, kb = _build_profile_page(target.id, message.from_user.id, 0)
    if text is None:
        await message.answer("❌ Профиль не найден")
        return

    target_vip = is_vip_active(target.id)
    photo_id = await _get_avatar_photo(target.id, message.from_user.id, target_vip)

    if photo_id:
        try:
            await message.answer_photo(
                photo=photo_id, caption=text, parse_mode="HTML",
                reply_markup=kb, reply_to_message_id=message.message_id
            )
            return
        except Exception as e:
            print(f"[PROFILE] Ошибка отправки фото: {e}")

    await message.answer(
        text, parse_mode="HTML", reply_markup=kb,
        reply_to_message_id=message.message_id
    )


@dp.callback_query(lambda c: c.data.startswith("prof_page_"))
async def cb_prof_page(callback: CallbackQuery):
    parts = callback.data.split("_")
    if len(parts) != 5:
        await callback.answer("⚠️ Ошибка данных", show_alert=True)
        return

    try:
        viewer_id = int(parts[2])
        target_id = int(parts[3])
        page = int(parts[4])
    except ValueError:
        await callback.answer("⚠️ Ошибка данных", show_alert=True)
        return

    text, kb = _build_profile_page(target_id, viewer_id, page)
    if text is None:
        await callback.answer("⚠️ Профиль не найден", show_alert=True)
        return

    try:
        if callback.message.photo:
            await callback.message.edit_caption(caption=text, parse_mode="HTML", reply_markup=kb)
        else:
            await callback.message.edit_text(text, parse_mode="HTML", reply_markup=kb)
    except Exception as e:
        print(f"[PROF] Ошибка редактирования: {e}")
    await callback.answer()


@dp.callback_query(lambda c: c.data == "prof_noop")
async def cb_prof_noop(callback: CallbackQuery):
    await callback.answer()


# =====================================
#  /achievements
# =====================================

ACH_PER_PAGE = 5


def _get_achievement_value_safe(user_id: int, field: str) -> int:
    try:
        if field == "msg_count":
            return get_balance(user_id)
        if field == "bank_balance":
            return bank_get(user_id)["balance"]
        if field == "daily_streak":
            return get_daily_streak(user_id)
        if field == "top_rank":
            return 1 if get_user_rank(user_id) == 1 else 0
        if field == "marriage_days":
            if not is_married(user_id):
                return 0
            married_at = get_marriage_date(user_id)
            if not married_at:
                return 0
            try:
                return (datetime.now() - datetime.fromisoformat(married_at)).days
            except ValueError:
                return 0
        stats = get_user_stats(user_id)
        return stats.get(field, 0)
    except Exception as e:
        print(f"[ACH] Ошибка получения значения {field}: {e}")
        return 0


def _build_achievements_page(target_id: int, page: int) -> tuple:
    unlocked = set(get_user_achievements(target_id))
    total = len(ACHIEVEMENTS)
    total_pages = max(1, (total + ACH_PER_PAGE - 1) // ACH_PER_PAGE)

    if page < 0:
        page = 0
    if page >= total_pages:
        page = total_pages - 1

    start = page * ACH_PER_PAGE
    end = start + ACH_PER_PAGE
    page_items = ACHIEVEMENTS[start:end]

    # ─── Заголовок ───
    lines = [
        f"{_p(PREM_TOP1, '🏆')} <b>Достижения: {len(unlocked)}/{total}</b>",
        f"Страница {page + 1}/{total_pages}",
        "",
    ]

    # ─── Достижения ───
    for ach_id, emoji, name, field, threshold in page_items:
        prem_id = ACH_PREMIUM.get(ach_id)
        if prem_id:
            ach_icon = _p(prem_id, emoji)
        else:
            ach_icon = emoji

        if ach_id in unlocked:
            status = _p(PREM_CHECK, "✅")
            lines.append(f"{status} {ach_icon} <b>{name}</b>")
        else:
            status = _p(PREM_LOCK, "🔒")
            current = _get_achievement_value_safe(target_id, field)
            percent = min(100, int((current / threshold) * 100)) if threshold > 0 else 0
            filled = int(percent / 10)
            bar = "▰" * filled + "▱" * (10 - filled)
            lines.append(
                f"{status} {ach_icon} <b>{name}</b>\n"
                f"└─ {current:,}/{threshold:,} ({percent}%)\n"
                f"└─ {bar}"
            )

    text = "\n".join(lines)

    # ─── Пагинация в стиле профиля ───
    nav_row = []
    for p in range(total_pages):
        if p == page:
            nav_row.append(InlineKeyboardButton(
                text=f"• {p + 1} •",
                callback_data="ach_noop"
            ))
        else:
            nav_row.append(InlineKeyboardButton(
                text=f"{p + 1}",
                callback_data=f"ach_page_{target_id}_{p}"
            ))

    kb = InlineKeyboardMarkup(inline_keyboard=[nav_row])
    return text, kb, total_pages


@dp.message(Command("achievements"))
async def cmd_achievements(message: Message):
    log_cmd("🏅 /achievements", message)
    target = message.from_user

    if message.reply_to_message and not message.reply_to_message.from_user.is_bot:
        target = message.reply_to_message.from_user
    else:
        args = message.text.split()[1:]
        if args and args[0].startswith("@"):
            found_id, found_name = find_user_id(message, args[0])
            if found_id is None:
                await message.answer("❌ Пользователь не найден")
                return

            class TargetObj:
                pass

            target = TargetObj()
            target.id = found_id
            target.username = None
            target.full_name = found_name
            target.is_bot = False
            ensure_user_by_id(found_id)

    ensure_user_by_id(target.id)
    text, kb, total_pages = _build_achievements_page(target.id, 0)
    if text is None:
        await message.answer("❌ Не удалось загрузить достижения")
        return

    await message.answer(
        text, parse_mode="HTML", reply_markup=kb,
        reply_to_message_id=message.message_id
    )


@dp.callback_query(lambda c: c.data.startswith("ach_page_"))
async def cb_ach_page(callback: CallbackQuery):
    parts = callback.data.split("_")
    if len(parts) != 4:
        await callback.answer("⚠️ Ошибка данных", show_alert=True)
        return
    try:
        target_id = int(parts[2])
        page = int(parts[3])
    except ValueError:
        await callback.answer("⚠️ Ошибка данных", show_alert=True)
        return

    text, kb, total_pages = _build_achievements_page(target_id, page)
    if text is None:
        await callback.answer("⚠️ Не удалось загрузить", show_alert=True)
        return

    try:
        if callback.message.photo:
            await callback.message.edit_caption(caption=text, parse_mode="HTML", reply_markup=kb)
        else:
            await callback.message.edit_text(text, parse_mode="HTML", reply_markup=kb)
    except Exception as e:
        print(f"[ACH] Ошибка редактирования: {e}")
    await callback.answer()


@dp.callback_query(lambda c: c.data == "ach_noop")
async def cb_ach_noop(callback: CallbackQuery):
    await callback.answer()


async def _check_and_notify_achievements(user_id: int, chat_id: int):
    try:
        new_ach = check_all_achievements(user_id)
    except Exception as e:
        print(f"[ACH] Ошибка проверки: {e}")
        return

    if not new_ach:
        return

    for ach_id, emoji, name in new_ach:
        try:
            await bot.send_message(
                chat_id,
                f"🎉 <b>Новое достижение!</b>\n\n"
                f"└─ {emoji} «{name}»\n\n"
                f"Проверить все: /achievements",
                parse_mode="HTML"
            )
        except Exception as e:
            print(f"[ACH] Ошибка уведомления: {e}")
        await asyncio.sleep(0.5)


# =========================================================
#  /top
# =========================================================

def _format_top_name(uid):
    data = get_user(uid)
    if not data:
        return f"ID:{uid}"

    nick, _ = get_nick(uid)
    title, _ = get_title(uid)
    uname = data[1]
    fname = data[2]

    if nick:
        name = nick
    elif uname:
        name = f"@{uname}"
    else:
        name = fname or f"ID:{uid}"

    if title:
        name = f"{name} [{title}]"
    return name


def _build_top_with_marriages(current_user_id: int, limit: int = 10):
    conn = sqlite3.connect("users.db")
    cur = conn.cursor()

    cur.execute("SELECT user1_id, user2_id, balance FROM marriages")
    marriages = cur.fetchall()

    married_users = set()
    marriage_by_user = {}
    for u1, u2, balance in marriages:
        married_users.add(u1)
        married_users.add(u2)
        marriage_by_user[u1] = (u2, balance, u1, u2)
        marriage_by_user[u2] = (u1, balance, u1, u2)

    cur.execute("""
        SELECT user_id, msg_count FROM users
        WHERE user_id NOT IN (
            SELECT user1_id FROM marriages
            UNION
            SELECT user2_id FROM marriages
        )
    """)
    singles = cur.fetchall()
    conn.close()

    items = []
    seen_pairs = set()
    for uid in married_users:
        spouse_id, balance, u1, u2 = marriage_by_user[uid]
        pair_key = tuple(sorted([u1, u2]))
        if pair_key in seen_pairs:
            continue
        seen_pairs.add(pair_key)

        name1 = _format_top_name(u1)
        name2 = _format_top_name(u2)
        display = f"{name1} 💍 {name2}"

        hide1 = is_hide_balance_active(u1)
        hide2 = is_hide_balance_active(u2)
        viewer_is_owner = is_owner(current_user_id)

        if (hide1 or hide2) and u1 != current_user_id and u2 != current_user_id and not viewer_is_owner:
            balance_text = "▒▒▒▒▒"
        else:
            balance_text = str(balance)

        is_me = current_user_id in (u1, u2)
        items.append({
            "balance": balance,
            "display": display,
            "display_balance": balance_text,
            "is_me": is_me,
        })

    for uid, balance in singles:
        name = _format_top_name(uid)
        hide = is_hide_balance_active(uid)

        if hide and uid != current_user_id and not is_owner(current_user_id):
            balance_text = "▒▒▒▒▒"
        else:
            balance_text = str(balance)

        items.append({
            "balance": balance,
            "display": name,
            "display_balance": balance_text,
            "is_me": uid == current_user_id,
        })

    items.sort(key=lambda x: x["balance"], reverse=True)
    return items[:limit]


@dp.message(Command("top"))
async def cmd_top(message: Message):
    log_cmd("🏆 /top", message)
    user = message.from_user
    ensure_user(user)

    args = message.text.split()[1:]
    mode = args[0].lower() if args else "msg"

    if mode not in ("msg", "bank"):
        await message.answer(
            "❌ Использование:\n"
            "└─ /top — топ по кошельку\n"
            "└─ /top bank — топ по банку",
            parse_mode="HTML"
        )
        return

    if mode == "bank":
        top_bank = get_top_bank(10)
        if not top_bank:
            await message.answer(
                "🏆 <b>Топ пока пуст</b>\n\n└─ Стань первым в рейтинге!",
                parse_mode="HTML"
            )
            return

        medals = {1: "🥇", 2: "🥈", 3: "🥉"}
        lines = ["🏆 <b>Топ-10 по банку</b>\n"]
        for i, row in enumerate(top_bank, start=1):
            uid = row[0]
            balance = row[-1]
            medal = medals.get(i, f"{i}.")
            name = _format_top_name(uid)
            if is_married(uid):
                name = f"{name} 💍"
            marker = " ← ты" if uid == user.id else ""
            lines.append(f"{medal} {name} — <b>{balance}</b> msg{marker}")
        text = "\n".join(lines)
    else:
        top = _build_top_with_marriages(user.id, 10)
        if not top:
            await message.answer(
                "🏆 <b>Топ пока пуст</b>\n\n"
                "└─ Стань первым в рейтинге!\n\n"
                "💡 <b>Как заработать:</b>\n"
                "└─ 🎁 /daily — бонус\n"
                "└─ 🎰 /casino — удача",
                parse_mode="HTML"
            )
            return

        medals = {1: "🥇", 2: "🥈", 3: "🥉"}
        lines = ["🏆 <b>Топ-10 по кошельку</b>\n"]
        for i, item in enumerate(top, start=1):
            medal = medals.get(i, f"{i}.")
            marker = " ← ты" if item["is_me"] else ""
            lines.append(
                f"{medal} {item['display']} — <b>{item['display_balance']}</b> msg{marker}"
            )
        text = "\n".join(lines)

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👤 Профиль", callback_data="top_profile")]
    ])

    await message.answer(
        text, parse_mode="HTML", reply_markup=kb,
        reply_to_message_id=message.message_id
    )


@dp.callback_query(lambda c: c.data == "top_profile")
async def cb_top_profile(callback: CallbackQuery):
    user = callback.from_user
    text, kb = _build_profile_page(user.id, user.id, 0)
    if text is None:
        await callback.answer("❌ Профиль не найден", show_alert=True)
        return

    try:
        await callback.message.edit_text(text, parse_mode="HTML", reply_markup=kb)
    except Exception as e:
        print(f"[TOP] Ошибка перехода к профилю: {e}")
    await callback.answer()


# =========================================================
#  /history
# =========================================================

@dp.message(Command("history"))
async def cmd_history(message: Message):
    log_cmd("📜 /history", message)
    user = message.from_user
    ensure_user(user)

    rows = get_history(user.id, limit=10)
    if not rows:
        await message.answer(
            "📭 <b>Тут пока пусто</b>\n\n"
            "└─ Как только появятся транзакции — увидишь их здесь\n\n"
            "💡 <b>Попробуй:</b>\n"
            "└─ 🎁 /daily — получи первый бонус\n"
            "└─ 🎰 /casino 100 — сыграй в казино",
            parse_mode="HTML"
        )
        return

    kind_emoji = {
        "transfer":         "🎁",
        "buy_vip":          "👑",
        "casino_win":       "🎰",
        "casino_lose":      "🎰",
        "casino_jackpot":   "🎰",
        "daily":            "🎁",
        "rob_success":      "🥷",
        "rob_fail":         "🚔",
        "admin_add":        "⚙️",
        "admin_rem":        "⚙️",
        "admin_set":        "⚙️",
        "admin_givevip":    "👑",
        "admin_remvip":     "🚫",
        "admin_unban":      "✅",
        "anon":             "💌",
        "buy_shield":       "🛡️",
        "buy_hide_balance": "🕵️",
        "buy_anon_shield":  "🕶️",
        "buy_lucky":        "🍀",
        "auto_ban":         "🚫",
        "marry":            "💍",
        "case":             "🎁",
    }

    lines = ["📜 <b>Последние транзакции</b>\n"]
    for from_id, to_id, amount, kind, created_at in rows:
        try:
            dt = datetime.fromisoformat(created_at)
            date_str = dt.strftime("%d.%m %H:%M")
        except ValueError:
            date_str = "—"

        emoji = kind_emoji.get(kind, "•")

        if kind == "transfer":
            if from_id == user.id:
                lines.append(f"{emoji} → подарок <b>-{abs(amount)}</b> msg | {date_str}")
            else:
                lines.append(f"{emoji} ← подарок <b>+{abs(amount)}</b> msg | {date_str}")
        elif kind == "daily":
            lines.append(f"{emoji} бонус <b>+{abs(amount)}</b> msg | {date_str}")
        elif kind == "buy_vip":
            lines.append(f"{emoji} покупка VIP <b>{amount}</b> msg | {date_str}")
        elif kind == "casino_win":
            lines.append(f"{emoji} казино победа <b>+{abs(amount)}</b> msg | {date_str}")
        elif kind == "casino_lose":
            lines.append(f"{emoji} казино проигрыш <b>{amount}</b> msg | {date_str}")
        elif kind == "casino_jackpot":
            lines.append(f"{emoji} ДЖЕКПОТ <b>+{abs(amount)}</b> msg | {date_str}")
        elif kind == "rob_success":
            if from_id == user.id:
                lines.append(f"{emoji} ограбление удалось <b>+{abs(amount)}</b> msg | {date_str}")
            else:
                lines.append(f"{emoji} тебя ограбили <b>-{abs(amount)}</b> msg | {date_str}")
        elif kind == "rob_fail":
            lines.append(f"{emoji} ограбление провалилось <b>{amount}</b> msg | {date_str}")
        elif kind == "marry":
            lines.append(f"{emoji} брак <b>{amount}</b> msg | {date_str}")
        elif kind == "case":
            lines.append(f"{emoji} кейс <b>{amount}</b> msg | {date_str}")
        else:
            lines.append(f"{emoji} {kind} <b>{amount}</b> msg | {date_str}")

    await message.answer("\n".join(lines), parse_mode="HTML")


# =========================================================
#  /gift
# =========================================================

@dp.message(Command("gift"))
async def cmd_gift(message: Message):
    log_cmd("🎁 /gift", message)
    user = message.from_user
    ensure_user(user)

    args = message.text.split()[1:]
    target_id = None
    target_name = None
    amount = None

    if message.reply_to_message:
        if len(args) != 1:
            await message.answer(
                "❌ Формат: ответь на сообщение и напиши /gift [сумма]",
                parse_mode="HTML"
            )
            return
        try:
            amount = int(args[0])
        except ValueError:
            await message.answer(
                f"😅 «{args[0]}» — это не число\n└─ Пример: /gift 100",
                parse_mode="HTML"
            )
            return
        target = message.reply_to_message.from_user
        if target.is_bot:
            await message.answer("❌ Нельзя дарить боту")
            return
        target_id = target.id
        target_name = target.full_name
        ensure_user(target)
    else:
        if len(args) != 2:
            await message.answer(
                "❌ Использование:\n"
                "└─ ответь на сообщение и напиши /gift [сумма]\n"
                "└─ или /gift @username [сумма]",
                parse_mode="HTML"
            )
            return

        a, b = args
        if a.startswith("@"):
            target_name, amount_str = a, b
        elif b.startswith("@"):
            target_name, amount_str = b, a
        else:
            await message.answer("❌ Укажи @username получателя")
            return

        try:
            amount = int(amount_str)
        except ValueError:
            await message.answer(
                f"😅 «{amount_str}» — это не число\n"
                f"└─ Пример: /gift @username 100",
                parse_mode="HTML"
            )
            return

        conn = sqlite3.connect("users.db")
        cur = conn.cursor()
        uname = target_name.lstrip("@")
        cur.execute(
            "SELECT user_id, full_name FROM users WHERE LOWER(username) = LOWER(?)",
            (uname,)
        )
        row = cur.fetchone()
        conn.close()
        if row is None:
            await message.answer(
                "❌ Пользователь не найден (он должен написать боту хотя бы раз)"
            )
            return
        target_id, target_name = row

    if target_id == user.id:
        await message.answer("❌ Нельзя дарить самому себе")
        return
    if amount <= 0:
        await message.answer("❌ Сумма должна быть положительной")
        return

    # ✅ Атомарный перевод (в database.py — с BEGIN/COMMIT)
    ok, info = transfer_msg(user.id, target_id, amount)
    if not ok:
        if "Недостаточно" in info:
            balance = get_balance(user.id)
            await message.answer(
                f"😢 <b>Недостаточно msg!</b>\n\n"
                f"└─ Нужно: {amount}\n"
                f"└─ У тебя: {balance}"
                f"{_shortage_hint(amount, balance)}",
                parse_mode="HTML"
            )
        else:
            await message.answer(f"❌ {info}")
        return

    msg = await message.answer("🎁 <b>Отправляем подарок…</b>", parse_mode="HTML")
    for frame in ["🎁", "🎁✨", "🎉", "🎉✨", "✅"]:
        await asyncio.sleep(0.5)
        try:
            await msg.edit_text(
                f"🎁 <b>Отправляем подарок…</b>\n\n{frame}",
                parse_mode="HTML"
            )
        except Exception:
            pass

    new_balance = get_balance(user.id)

    await msg.edit_text(
        f"✅ <b>Подарок отправлен!</b>\n\n"
        f"└─ Кому: {target_name}\n"
        f"└─ Сумма: <b>{amount}</b> msg\n"
        f"└─ Твой баланс: {new_balance} msg",
        parse_mode="HTML"
    )

    try:
        await bot.send_message(
            target_id,
            f"🎁 <b>Тебе подарили {amount} msg!</b>\n└─ От: {user.full_name}"
        )
    except Exception:
        pass

# =========================================================
#  /buyvip
# =========================================================

@dp.message(Command("buyvip"))
async def cmd_buyvip(message: Message):
    log_cmd("👑 /buyvip", message)
    user = message.from_user

    args = message.text.split()[1:]
    if len(args) != 1:
        await message.answer(
            "❌ Использование: /buyvip [недели]\n└─ 1 неделя = 1000 msg",
            parse_mode="HTML"
        )
        return

    try:
        weeks = int(args[0])
    except ValueError:
        await message.answer(
            f"😅 «{args[0]}» — это не число\n└─ Пример: /buyvip 1",
            parse_mode="HTML"
        )
        return

    # ✅ buy_vip — атомарная (см. database.py фикс)
    ok, info = buy_vip(user.id, weeks)
    if not ok:
        await message.answer(f"❌ {info}")
        return

    until = datetime.fromisoformat(info)
    await message.answer(
        f"👑 <b>VIP активирован!</b>\n"
        f"└─ Куплено: {weeks} нед.\n"
        f"└─ Стоимость: {weeks * 1000} msg\n"
        f"└─ Действует до: {until.strftime('%d.%m.%Y %H:%M')}\n\n"
        f"⚡ Теперь ты получаешь +1 msg раз в 1 сек!\n"
        f"💡 Все VIP-возможности: /vipinfo",
        parse_mode="HTML"
    )


# =========================================================
#  /vipinfo
# =========================================================

@dp.message(Command("vipinfo"))
async def cmd_vipinfo(message: Message):
    log_cmd("👑 /vipinfo", message)
    user = message.from_user
    ensure_user(user)

    vip = is_vip_active(user.id)

    if vip:
        vip_until = None
        data = get_user(user.id)
        if data and data[4]:
            try:
                until = datetime.fromisoformat(data[4])
                if until > datetime.now():
                    vip_until = until
            except ValueError:
                pass

        until_line = ""
        if vip_until:
            diff = vip_until - datetime.now()
            d = diff.days
            h = diff.seconds // 3600
            until_line = f"\n└─ ⏳ До окончания: <b>{d} дн. {h} ч</b>"

        await message.answer(
            f"👑 <b>Твои VIP-возможности</b>{until_line}\n\n"
            f"⚡ <b>Ускоренный доход:</b>\n└─ +1 msg раз в 1 сек\n\n"
            f"🎰 <b>Быстрое казино:</b>\n└─ Кулдаун 10 сек\n\n"
            f"🏦 <b>Улучшенный банк:</b>\n└─ 2%/час\n\n"
            f"🎁 <b>Двойной daily:</b>\n└─ 1000 msg\n└─ 7-й день: 5000 msg\n\n"
            f"🎭 <b>Безлимитный ник</b>\n\n"
            f"🛡️ <b>Защита от warn</b>\n\n"
            f"👑 <b>Продлить:</b> /buyvip [недели]",
            parse_mode="HTML"
        )
    else:
        await message.answer(
            "👑 <b>VIP-подписка</b>\n\n"
            "Что даёт VIP:\n\n"
            "⚡ +1 msg раз в 1 сек (вместо 2)\n"
            "🎰 Кулдаун казино 10 сек\n"
            "🏦 Банк 2%/час\n"
            "🎁 Двойной daily\n"
            "🎭 Безлимитный /nick\n"
            "🛡️ Защита от warn\n\n"
            "💰 <b>Цена:</b> 1000 msg / неделя\n"
            "└─ Купить: /buyvip [недели]",
            parse_mode="HTML"
        )


# =========================================================
#  CASINO — общая логика
# =========================================================

CASINO_SLOTS = ["🍒", "🍋", "🍊", "⭐", "💎", "7️⃣"]


def _casino_replay_kb(bet: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔂 Еще раз", callback_data=f"casino_replay_{bet}")]
    ])


def _casino_spin() -> tuple:
    """Возвращает (result, mult, win_amount_factor, kind, header, line_symbol)."""
    lucky = False  # вычислим снаружи
    return None


def _casino_generate_result(lucky: bool) -> tuple:
    win_chance = 0.59 if lucky else 0.44
    roll = random.random()

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

    if a == b == c:
        multipliers = {"🍒": 4, "🍋": 5, "🍊": 6, "⭐": 8, "💎": 12, "7️⃣": 25}
        mult = multipliers[a]
        kind = "casino_jackpot" if a == "7️⃣" else "casino_win"
        header = "🎉 <b>ДЖЕКПОТ!</b>" if a == "7️⃣" else "🎉 <b>Победа!</b>"
        line_symbol = "═════════════"
    elif a == b or b == c or a == c:
        mult = 1.5
        kind = "casino_win"
        header = "✨ <b>Почти джекпот!</b>"
        line_symbol = "─────────────"
    else:
        mult = 0
        kind = "casino_lose"
        header = "😢 <b>Проигрыш…</b>"
        line_symbol = "─────────────"

    return result, mult, kind, header, line_symbol


async def _casino_play(user, bet: int, edit_target):
    """
    Универсальная логика казино.
    edit_target — Message (для команды) или CallbackQuery.message (для callback).
    """
    vip = is_vip_active(user.id)
    lucky = is_lucky_active(user.id)

    add_balance(user.id, -bet)
    result, mult, kind, header, line_symbol = _casino_generate_result(lucky)

    a, b, c = result
    win_amount = int(bet * mult) if mult > 0 else 0

    if win_amount > 0:
        new_balance = add_balance(user.id, win_amount)
    else:
        new_balance = get_balance(user.id)

    log_transaction(user.id, user.id, win_amount - bet, kind)
    increment_stat(user.id, "total_casino_games", 1)
    if win_amount == 0:
        increment_stat(user.id, "total_casino_losses", bet)

    result_line = f"  {a} | {b} | {c}\n  {line_symbol}"

    next_wait = int(CASINO_VIP_COOLDOWN if vip else CASINO_COOLDOWN)
    cooldown_hint = f"\n└─ {'👑' if vip else '⏳'} Следующая игра через {next_wait} сек"
    lucky_hint = "\n└─ 🍀 Лаки-казино активно!" if lucky else ""

    if win_amount > 0:
        result_text = (
            f"🎰 <b>Крутим барабаны…</b>\n\n"
            f"{result_line}\n\n"
            f"{header}\n"
            f"└─ Ставка: {bet} msg\n"
            f"└─ Множитель: x{mult}\n"
            f"└─ Выигрыш: <b>+{win_amount}</b> msg\n"
            f"└─ Баланс: {new_balance} msg"
            f"{lucky_hint}{cooldown_hint}"
        )
    else:
        result_text = (
            f"🎰 <b>Крутим барабаны…</b>\n\n"
            f"{result_line}\n\n"
            f"{header}\n"
            f"└─ Ставка: {bet} msg\n"
            f"└─ Потеряно: <b>-{bet}</b> msg\n"
            f"└─ Баланс: {new_balance} msg"
            f"{lucky_hint}{cooldown_hint}"
        )

    kb = _casino_replay_kb(bet)

    try:
        await edit_target.edit_text(result_text, parse_mode="HTML", reply_markup=kb)
    except Exception as e:
        print(f"[CASINO] Ошибка редактирования: {e}")


@dp.message(Command("casino"))
async def cmd_casino(message: Message):
    log_cmd("🎰 /casino", message)
    user = message.from_user
    ensure_user(user)

    args = message.text.split()[1:]
    if len(args) != 1:
        await message.answer(
            "❌ Использование: /casino [ставка]\n\n"
            "<b>Таблица выплат:</b>\n"
            "└─ 7️⃣7️⃣7️⃣ — x25 🎉 ДЖЕКПОТ\n"
            "└─ 💎💎💎 — x12\n"
            "└─ ⭐⭐⭐ — x8\n"
            "└─ 🍊🍊🍊 — x6\n"
            "└─ 🍋🍋🍋 — x5\n"
            "└─ 🍒🍒🍒 — x4\n"
            "└─ 2 одинаковых — x1.5\n"
            "└─ всё разное — проигрыш",
            parse_mode="HTML"
        )
        return

    try:
        bet = int(args[0])
    except ValueError:
        await message.answer(
            f"😅 «{args[0]}» — это не число\n└─ Пример: /casino 100",
            parse_mode="HTML"
        )
        return

    if bet <= 0:
        await message.answer("❌ Ставка должна быть положительной")
        return

    # Защита от race condition на юзера
    lock = get_user_lock(user.id)
    async with lock:
        vip = is_vip_active(user.id)
        cooldown = CASINO_VIP_COOLDOWN if vip else CASINO_COOLDOWN
        now = time.monotonic()
        diff = now - _last_casino.get(user.id, 0)

        if diff < cooldown:
            remaining = cooldown - diff
            minutes = int(remaining // 60)
            seconds = int(remaining % 60)
            time_text = f"{minutes} мин {seconds} сек" if minutes > 0 else f"{seconds} сек"
            vip_hint = "" if vip else "\n\n💡 С VIP кулдаун короче (10 сек вместо 20)"
            await message.answer(
                f"⏳ <b>Казино на перезарядке</b>\n"
                f"└─ Ждать: <b>{time_text}</b>{vip_hint}",
                parse_mode="HTML"
            )
            return

        balance = get_balance(user.id)
        if balance < bet:
            await message.answer(
                f"😢 <b>Недостаточно msg!</b>\n\n"
                f"└─ Нужно: {bet}\n"
                f"└─ У тебя: {balance}"
                f"{_shortage_hint(bet, balance)}",
                parse_mode="HTML"
            )
            return

        _last_casino[user.id] = now

    msg = await message.answer("🎰 <b>Крутим барабаны…</b>", parse_mode="HTML")

    for _ in range(6):
        line = " | ".join(random.choices(CASINO_SLOTS, k=3))
        await asyncio.sleep(0.5)
        try:
            await msg.edit_text(
                f"🎰 <b>Крутим барабаны…</b>\n\n{line}",
                parse_mode="HTML"
            )
        except Exception:
            pass

    await _casino_play(user, bet, msg)
    await _check_and_notify_achievements(user.id, message.chat.id)


@dp.callback_query(F.data.startswith("casino_replay_"))
async def cb_casino_replay(callback: CallbackQuery):
    try:
        bet = int(callback.data.replace("casino_replay_", ""))
    except ValueError:
        await callback.answer("⚠️ Ошибка данных", show_alert=True)
        return

    user = callback.from_user
    ensure_user(user)

    if bet <= 0:
        await callback.answer("❌ Некорректная ставка", show_alert=True)
        return

    lock = get_user_lock(user.id)
    async with lock:
        vip = is_vip_active(user.id)
        cooldown = CASINO_VIP_COOLDOWN if vip else CASINO_COOLDOWN
        now = time.monotonic()
        diff = now - _last_casino.get(user.id, 0)

        if diff < cooldown:
            remaining = cooldown - diff
            minutes = int(remaining // 60)
            seconds = int(remaining % 60)
            time_text = f"{minutes} мин {seconds} сек" if minutes > 0 else f"{seconds} сек"
            await callback.answer(f"⏳ Подожди ещё {time_text}", show_alert=True)
            return

        balance = get_balance(user.id)
        if balance < bet:
            await callback.answer(
                f"😢 Недостаточно msg! Нужно: {bet}, у тебя: {balance}",
                show_alert=True
            )
            return

        _last_casino[user.id] = now

    await callback.answer()

    try:
        await callback.message.edit_text("🎰 <b>Крутим барабаны…</b>", parse_mode="HTML")
    except Exception:
        pass

    for _ in range(6):
        line = " | ".join(random.choices(CASINO_SLOTS, k=3))
        await asyncio.sleep(0.5)
        try:
            await callback.message.edit_text(
                f"🎰 <b>Крутим барабаны…</b>\n\n{line}",
                parse_mode="HTML"
            )
        except Exception:
            pass

    await _casino_play(user, bet, callback.message)
    await _check_and_notify_achievements(user.id, callback.message.chat.id)


# =========================================================
#  /daily
# =========================================================

@dp.message(Command("daily"))
async def cmd_daily(message: Message):
    log_cmd("🎁 /daily", message)
    user = message.from_user
    ensure_user(user)

    lock = get_user_lock(user.id)
    async with lock:
        last = get_last_daily(user.id)
        now = datetime.now()
        current_streak = get_daily_streak(user.id)

        if last:
            try:
                last_dt = datetime.fromisoformat(last)
                elapsed = now - last_dt

                if elapsed < DAILY_COOLDOWN:
                    remaining = DAILY_COOLDOWN - elapsed
                    hours = remaining.seconds // 3600
                    minutes = (remaining.seconds % 3600) // 60
                    await message.answer(
                        f"⏳ Бонус уже получен!\n"
                        f"└─ Следующий через: <b>{hours} ч {minutes} мин</b>",
                        parse_mode="HTML"
                    )
                    return

                if elapsed > DAILY_STREAK_RESET:
                    current_streak = 0
            except ValueError:
                pass

        new_streak = current_streak + 1
        vip = is_vip_active(user.id)

        if new_streak >= 7:
            amount = 2500 if not vip else 5000
            is_bonus_day = True
            new_streak = 0
        else:
            amount = DAILY_AMOUNT if not vip else DAILY_VIP_AMOUNT
            is_bonus_day = False

    msg = await message.answer("🎁 <b>Открываем подарок…</b>", parse_mode="HTML")
    for frame in ["📦", "📦✨", "🎁", "🎁✨", "🎉🎁", "🎉🎁✨"]:
        await asyncio.sleep(0.5)
        try:
            await msg.edit_text(
                f"🎁 <b>Открываем подарок…</b>\n\n{frame}",
                parse_mode="HTML"
            )
        except Exception:
            pass

    new_balance = claim_daily(user.id, amount)
    set_daily_streak(user.id, new_streak)

    vip_note = "\n└─ 👑 VIP-бонус x2!" if vip else ""

    if is_bonus_day:
        streak_line = f"\n🔥 <b>Streak 7/7! Бонус ×5!</b>"
    else:
        display_streak = new_streak if new_streak > 0 else 7
        streak_line = f"\n🔥 Streak: {display_streak}/7"

    await msg.edit_text(
        f"🎁 <b>Ежедневный бонус получен!</b>\n\n"
        f"🎉 +{amount} msg{vip_note}"
        f"{streak_line}\n"
        f"└─ Баланс: {new_balance} msg\n\n"
        f"Следующий бонус — через 24 часа.",
        parse_mode="HTML"
    )


# =========================================================
#  /nick
# =========================================================

@dp.message(Command("nick"))
async def cmd_nick(message: Message):
    log_cmd("🎭 /nick", message)
    user = message.from_user
    ensure_user(user)

    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        nick, _ = get_nick(user.id)
        current = nick or user.full_name
        await message.answer(
            f"🎭 <b>Твой ник</b>\n\n"
            f"└─ Текущий: <b>{current}</b>\n\n"
            f"Сменить: /nick [новое имя]",
            parse_mode="HTML"
        )
        return

    new_nick = args[1].strip()
    if len(new_nick) < 1 or len(new_nick) > 20:
        await message.answer("❌ Ник должен быть от 1 до 20 символов")
        return

    forbidden = ["\n", "\r", "\t"]
    if any(ch in new_nick for ch in forbidden):
        await message.answer("❌ Ник не должен содержать переносов строк")
        return

    vip = is_vip_active(user.id)

    if not vip:
        _, changed_at = get_nick(user.id)
        if changed_at:
            try:
                last_dt = datetime.fromisoformat(changed_at)
                elapsed = datetime.now() - last_dt
                cooldown = timedelta(hours=24)
                if elapsed < cooldown:
                    remaining = cooldown - elapsed
                    h = remaining.seconds // 3600
                    m = (remaining.seconds % 3600) // 60
                    await message.answer(
                        f"⏳ <b>Ник можно менять раз в 24 часа</b>\n"
                        f"└─ Следующий раз через: <b>{h} ч {m} мин</b>\n\n"
                        f"💡 VIP может менять ник без ограничений 👑",
                        parse_mode="HTML"
                    )
                    return
            except ValueError:
                pass

    set_nick(user.id, new_nick)

    msg = await message.answer("🎭 <b>Меняем ник…</b>", parse_mode="HTML")
    for frame in ["🎭", "✏️", "📝", "✅"]:
        await asyncio.sleep(0.2)
        try:
            await msg.edit_text(f"🎭 <b>Меняем ник…</b>\n\n{frame}", parse_mode="HTML")
        except Exception:
            pass

    vip_note = " 👑" if vip else ""
    await msg.edit_text(
        f"✅ <b>Ник изменён!</b>{vip_note}\n└─ Новый: <b>{new_nick}</b>",
        parse_mode="HTML"
    )


# =========================================================
#  /title
# =========================================================

@dp.message(Command("title"))
async def cmd_title(message: Message):
    log_cmd("🏷️ /title", message)
    user = message.from_user
    ensure_user(user)

    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        current_title, _ = get_title(user.id)
        if current_title:
            clear_title(user.id)
            await message.answer(
                f"✅ <b>Титул убран</b>\n└─ Было: <b>{current_title}</b>",
                parse_mode="HTML"
            )
        else:
            await message.answer(
                "🏷️ <b>Титул</b>\n\n"
                "└─ У тебя нет титула\n\n"
                "<b>Установить:</b>\n"
                "└─ <code>/title [до 4 символов]</code>\n"
                "└─ <code>/title</code> без текста — убрать\n\n"
                "💡 Титул виден в /top и /profile",
                parse_mode="HTML"
            )
        return

    new_title = args[1].strip()

    if not new_title:
        current_title, _ = get_title(user.id)
        if current_title:
            clear_title(user.id)
            await message.answer(
                f"✅ <b>Титул убран</b>\n└─ Было: <b>{current_title}</b>",
                parse_mode="HTML"
            )
        else:
            await message.answer("ℹ️ У тебя нет титула")
        return

    if len(new_title) > 4:
        await message.answer(
            f"❌ <b>Титул слишком длинный</b>\n"
            f"└─ Максимум: 4 символа\n"
            f"└─ У тебя: {len(new_title)}",
            parse_mode="HTML"
        )
        return

    _, changed_at = get_title(user.id)
    if changed_at:
        try:
            last_dt = datetime.fromisoformat(changed_at)
            elapsed = datetime.now() - last_dt
            cooldown = timedelta(hours=12)
            if elapsed < cooldown:
                remaining = cooldown - elapsed
                h = remaining.seconds // 3600
                m = (remaining.seconds % 3600) // 60
                await message.answer(
                    f"⏳ <b>Титул можно менять раз в 12 часов</b>\n"
                    f"└─ Следующий раз через: <b>{h} ч {m} мин</b>",
                    parse_mode="HTML"
                )
                return
        except ValueError:
            pass

    set_title(user.id, new_title)

    await message.answer(
        f"✅ <b>Титул установлен!</b>\n"
        f"└─ Новый: <b>{new_title}</b>\n"
        f"└─ В топе: <b>{user.full_name} [{new_title}]</b>\n\n"
        f"💡 Менять можно раз в 12 часов",
        parse_mode="HTML"
    )


# =========================================================
#  /rob
# =========================================================

@dp.message(Command("rob"))
async def cmd_rob(message: Message):
    log_cmd("🥷 /rob", message)
    user = message.from_user
    ensure_user(user)

    target_id = None
    target_name = None
    target_obj = None

    if message.reply_to_message:
        target = message.reply_to_message.from_user
        target_id = target.id
        target_name = target.full_name
        target_obj = target
    else:
        args = message.text.split()[1:]
        if not args or not args[0].startswith("@"):
            await message.answer(
                "❌ Использование:\n"
                "└─ ответь на сообщение: /rob\n"
                "└─ или /rob @username",
                parse_mode="HTML"
            )
            return
        found_id, found_name = find_user_id(message, args[0])
        if found_id is None:
            await message.answer("❌ Пользователь не найден")
            return
        target_id = found_id
        target_name = found_name

    if target_obj and target_obj.is_bot:
        await message.answer("❌ Нельзя грабить бота")
        return

    if target_id == user.id:
        await message.answer("😄 Нельзя грабить самого себя")
        return

    if is_main_owner(target_id):
        await message.answer("❌ Нельзя грабить главного владельца")
        return

    last_rob = get_last_rob(user.id)
    if last_rob:
        try:
            last_dt = datetime.fromisoformat(last_rob)
            elapsed = datetime.now() - last_dt
            if elapsed < ROB_COOLDOWN:
                remaining = ROB_COOLDOWN - elapsed
                m = remaining.seconds // 60
                s = remaining.seconds % 60
                await message.answer(
                    f"⏳ <b>Ограбление на перезарядке</b>\n"
                    f"└─ Ждать: <b>{m} мин {s} сек</b>",
                    parse_mode="HTML"
                )
                return
        except ValueError:
            pass

    ensure_user_by_id(target_id)
    target_data = get_user(target_id)
    if not target_data:
        await message.answer("❌ Цель не найдена")
        return

    if is_shield_active(target_id):
        await message.answer(
            f"🛡️ <b>У {target_name} активен щит!</b>\n└─ Ограбление невозможно",
            parse_mode="HTML"
        )
        return

    target_balance = get_balance(target_id)
    if target_balance <= 0:
        await message.answer(f"❌ У {target_name} нет msg для грабежа")
        return

    lock = get_user_lock(user.id)
    async with lock:
        robber_balance = get_balance(user.id)
        target_vip = is_vip_active(target_id)

        if target_vip:
            success_chance = 0.10
            penalty_rate = 0.10
            vip_note = "\n👑 У жертвы VIP — грабить сложнее!"
        else:
            success_chance = 0.30
            penalty_rate = 0.05
            vip_note = ""

        set_last_rob(user.id)
        success = random.random() < success_chance

        if success:
            steal_amount = int(target_balance * 0.10)
            if steal_amount < 1:
                steal_amount = 1
            if steal_amount > target_balance:
                steal_amount = target_balance

            add_balance(target_id, -steal_amount)
            new_balance = add_balance(user.id, steal_amount)
            log_transaction(user.id, target_id, steal_amount, "rob_success")

            await message.answer(
                f"🥷 <b>Ограбление удалось!</b>{vip_note}\n\n"
                f"└─ Жертва: {target_name}\n"
                f"└─ Украдено: <b>+{steal_amount}</b> msg\n"
                f"└─ Твой баланс: {new_balance} msg",
                parse_mode="HTML"
            )

            try:
                await bot.send_message(
                    target_id,
                    f"🥷 <b>Тебя ограбили!</b>\n"
                    f"└─ Вор: {user.full_name}\n"
                    f"└─ Украдено: -{steal_amount} msg"
                )
            except Exception:
                pass
        else:
            penalty = int(robber_balance * penalty_rate)
            if penalty < 1:
                penalty = 1
            if penalty > robber_balance:
                penalty = robber_balance

            new_balance = add_balance(user.id, -penalty)
            log_transaction(user.id, user.id, -penalty, "rob_fail")

            await message.answer(
                f"🚔 <b>Ограбление провалилось!</b>{vip_note}\n\n"
                f"└─ Жертва: {target_name}\n"
                f"└─ Штраф: <b>-{penalty}</b> msg\n"
                f"└─ Твой баланс: {new_balance} msg",
                parse_mode="HTML"
            )

            try:
                await bot.send_message(
                    target_id,
                    f"🛡️ <b>Тебя пытались ограбить!</b>\n"
                    f"└─ Вор: {user.full_name}\n"
                    f"└─ Результат: провалился\n"
                    f"└─ Твои msg в безопасности 💰"
                )
            except Exception:
                pass


# ─── ПРЕМИУМ-ЭМОДЗИ ───
PREM_IN    = "5875008416132370818"  # 📥
PREM_OUT   = "5875078273775439450"  # 📤
PREM_MONEY = "5987880246865565644"  # 💰
PREM_BANK  = "5366223171454278937"  # 🏦
PREM_CHECK = "5215492745900077682"  # ✅
PREM_ERR   = "5368686743220415997"  # ❌
PREM_RATE  = "5364105043907716258"  # 📈
PREM_TIME  = "6096070825239122661"  # ⏳

# =================================
#  /bank, /bankput, /banktake
# =================================

BANK_PHOTO = "AgACAgIAAxkBAAIKSWrJ_0HZTAIyoaOcm1kH_8f6tty9AAIvH2sbJWsQSq4FP9M8Qc37AQADAgADeAADPQQ"

# -----------------------------------
def build_bank_text_and_kb(user_id):
    bank_ensure(user_id)
    info = bank_get(user_id)
    vip = is_vip_active(user_id)
    rate = "2%" if vip else "1%"

    vip_mark = f' {_p(PREM_TOP1, "👑")}' if vip else ""

    earned_line = ""
    if info["earned_now"] > 0:
        earned_line = (
            f"\n{_p(PREM_MONEY, '💰')} Начислено сейчас: <b>+{info['earned_now']:,}</b> msg"
        )

    now_kr = datetime.now(timezone(timedelta(hours=7))).replace(tzinfo=None)
    minutes_left = 60 - now_kr.minute
    if minutes_left == 60:
        minutes_left = 0
    next_line = (
        f"\n{_p(PREM_TIME, '⏳')} Следующее начисление через: <b>{minutes_left} мин</b>"
    )

    text = (
        f"{_p(PREM_BANK, '🏦')} <b>Твой банк</b>{vip_mark}\n\n"
        f"{_p(PREM_MONEY, '💰')} На счету: <b>{info['balance']:,}</b> msg\n"
        f"{_p(PREM_RATE, '📈')} Ставка: <b>{rate} в час</b> (в :00 по Красноярску)"
        f"{earned_line}"
        f"{next_line}\n"
        f"{_p(PREM_CHECK, '✅')} Всего заработано: <b>{info['total_earned']:,}</b> msg"
    )

    kb_rows = []
    if info["balance"] > 0:
        kb_rows.append([InlineKeyboardButton(
            text=f"Снять всё ({info['balance']:,})",
            callback_data=f"bank_take_all_{user_id}",
            icon_custom_emoji_id=PREM_OUT
        )])

    kb = InlineKeyboardMarkup(inline_keyboard=kb_rows)
    return text, kb
# -----------------------------------

# -----------------------------------
@dp.message(Command("bank"))
async def cmd_bank(message: Message):
    log_cmd("🏦 /bank", message)
    user = message.from_user
    ensure_user(user)

    text, kb = build_bank_text_and_kb(user.id)

    try:
        await message.answer_photo(
            photo=BANK_PHOTO,
            caption=text,
            parse_mode="HTML",
            reply_markup=kb,
            reply_to_message_id=message.message_id
        )
    except Exception as e:
        print(f"[BANK] Ошибка отправки фото: {e}")
        await message.answer(
            text, parse_mode="HTML", reply_markup=kb,
            reply_to_message_id=message.message_id
        )
# -----------------------------------

# -----------------------------------
def _bank_put_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="500", callback_data="bank_put_500",
                icon_custom_emoji_id=PREM_IN
            ),
            InlineKeyboardButton(
                text="1 000", callback_data="bank_put_1000",
                icon_custom_emoji_id=PREM_IN
            ),
        ],
        [
            InlineKeyboardButton(
                text="5 000", callback_data="bank_put_5000",
                icon_custom_emoji_id=PREM_IN
            ),
            InlineKeyboardButton(
                text="10 000", callback_data="bank_put_10000",
                icon_custom_emoji_id=PREM_IN
            ),
        ]
    ])
# -----------------------------------

# -----------------------------------
def _bank_take_kb(user_id: int):
    info = bank_get(user_id)
    balance = info["balance"]
    rows = []

    row1 = []
    if balance >= 500:
        row1.append(InlineKeyboardButton(
            text="500", callback_data="bank_take_500",
            icon_custom_emoji_id=PREM_OUT
        ))
    if balance >= 1000:
        row1.append(InlineKeyboardButton(
            text="1 000", callback_data="bank_take_1000",
            icon_custom_emoji_id=PREM_OUT
        ))
    if row1:
        rows.append(row1)

    row2 = []
    if balance >= 5000:
        row2.append(InlineKeyboardButton(
            text="5 000", callback_data="bank_take_5000",
            icon_custom_emoji_id=PREM_OUT
        ))
    if balance >= 10000:
        row2.append(InlineKeyboardButton(
            text="10 000", callback_data="bank_take_10000",
            icon_custom_emoji_id=PREM_OUT
        ))
    if row2:
        rows.append(row2)

    rows.append([InlineKeyboardButton(
        text=f"Снять всё ({balance:,})",
        callback_data=f"bank_take_all_{user_id}",
        icon_custom_emoji_id=PREM_OUT
    )])
    return InlineKeyboardMarkup(inline_keyboard=rows)
# -----------------------------------

# -----------------------------------
@dp.message(Command("bankput"))
async def cmd_bankput(message: Message):
    log_cmd("📥 /bankput", message)
    user = message.from_user
    ensure_user(user)

    args = message.text.split()[1:]
    if not args:
        await message.answer(
            f"{_p(PREM_IN, '📥')} <b>Положить в банк</b>\n\n"
            f"Выбери сумму или напиши <code>/bankput [сумма]</code>",
            parse_mode="HTML",
            reply_markup=_bank_put_kb()
        )
        return

    try:
        amount = int(args[0])
    except ValueError:
        await message.answer(
            f"😅 «{args[0]}» — это не число\n└─ Пример: /bankput 500",
            parse_mode="HTML"
        )
        return

    if amount <= 0:
        await message.answer(
            f"{_p(PREM_ERR, '❌')} Сумма должна быть положительной",
            parse_mode="HTML"
        )
        return

    ok, info, new_bank, new_wallet = bank_put(user.id, amount)
    if not ok:
        await message.answer(f"{_p(PREM_ERR, '❌')} {info}", parse_mode="HTML")
        return

    await message.answer(
        f"{_p(PREM_CHECK, '✅')} <b>Положено в банк</b>\n"
        f"└─ Внесено: <b>{amount:,}</b> msg\n"
        f"└─ В банке: {new_bank:,} msg\n"
        f"└─ В кошельке: {new_wallet:,} msg",
        parse_mode="HTML"
    )
# -----------------------------------

# -----------------------------------
@dp.message(Command("banktake"))
async def cmd_banktake(message: Message):
    log_cmd("📤 /banktake", message)
    user = message.from_user
    ensure_user(user)

    args = message.text.split()[1:]
    if not args:
        info = bank_get(user.id)
        if info["balance"] <= 0:
            await message.answer(
                f"{_p(PREM_OUT, '📤')} <b>Снять из банка</b>\n\n"
                f"└─ {_p(PREM_MONEY, '💰')} В банке пусто",
                parse_mode="HTML"
            )
            return

        await message.answer(
            f"{_p(PREM_OUT, '📤')} <b>Снять из банка</b>\n\n"
            f"└─ {_p(PREM_MONEY, '💰')} Доступно: <b>{info['balance']:,}</b> msg\n\n"
            f"Выбери сумму или напиши <code>/banktake [сумма]</code>",
            parse_mode="HTML",
            reply_markup=_bank_take_kb(user.id)
        )
        return

    try:
        amount = int(args[0])
    except ValueError:
        await message.answer(
            f"😅 «{args[0]}» — это не число\n└─ Пример: /banktake 500",
            parse_mode="HTML"
        )
        return

    if amount <= 0:
        await message.answer(
            f"{_p(PREM_ERR, '❌')} Сумма должна быть положительной",
            parse_mode="HTML"
        )
        return

    ok, info, new_bank, new_wallet = bank_take(user.id, amount)
    if not ok:
        await message.answer(f"{_p(PREM_ERR, '❌')} {info}", parse_mode="HTML")
        return

    await message.answer(
        f"{_p(PREM_CHECK, '✅')} <b>Снято из банка</b>\n"
        f"└─ Снято: <b>{amount:,}</b> msg\n"
        f"└─ В банке: {new_bank:,} msg\n"
        f"└─ В кошельке: {new_wallet:,} msg",
        parse_mode="HTML"
    )
# -----------------------------------

# =====================================
#  CALLBACK: банк
# =====================================
@dp.callback_query(F.data.startswith("bank_put_"))
async def cb_bank_put(callback: CallbackQuery):
    try:
        amount = int(callback.data.replace("bank_put_", ""))
    except ValueError:
        await callback.answer("⚠️ Ошибка данных", show_alert=True)
        return

    user_id = callback.from_user.id
    ensure_user(callback.from_user)

    ok, info, new_bank, new_wallet = bank_put(user_id, amount)
    if not ok:
        await callback.answer(f"❌ {info}", show_alert=True)
        return

    text, kb = build_bank_text_and_kb(user_id)

    try:
        if callback.message.photo:
            await callback.message.edit_caption(
                caption=text, parse_mode="HTML", reply_markup=kb
            )
        else:
            await callback.message.edit_text(
                text, parse_mode="HTML", reply_markup=kb
            )
    except Exception as e:
        print(f"[BANK] Ошибка редактирования: {e}")

    await callback.answer(f"📥 +{amount:,} msg")
# -----------------------------------

# -----------------------------------
@dp.callback_query(F.data.startswith("bank_take_all_"))
async def cb_bank_take_all(callback: CallbackQuery):
    try:
        user_id = int(callback.data.replace("bank_take_all_", ""))
    except ValueError:
        await callback.answer("⚠️ Ошибка данных", show_alert=True)
        return

    if callback.from_user.id != user_id:
        await callback.answer("❌ Это не твой банк", show_alert=True)
        return

    info = bank_get(user_id)
    amount = info["balance"]
    if amount <= 0:
        await callback.answer("❌ В банке пусто", show_alert=True)
        return

    ok, msg, new_bank, new_wallet = bank_take(user_id, amount)
    if not ok:
        await callback.answer(f"❌ {msg}", show_alert=True)
        return

    text, kb = build_bank_text_and_kb(user_id)

    try:
        if callback.message.photo:
            await callback.message.edit_caption(
                caption=text, parse_mode="HTML", reply_markup=kb
            )
        else:
            await callback.message.edit_text(
                text, parse_mode="HTML", reply_markup=kb
            )
    except Exception as e:
        print(f"[BANK] Ошибка редактирования: {e}")

    await callback.answer(f"📤 -{amount:,} msg")
# -----------------------------------

# -----------------------------------
@dp.callback_query(F.data.startswith("bank_take_") & ~F.data.startswith("bank_take_all_"))
async def cb_bank_take(callback: CallbackQuery):
    try:
        amount = int(callback.data.replace("bank_take_", ""))
    except ValueError:
        await callback.answer("⚠️ Ошибка данных", show_alert=True)
        return

    user_id = callback.from_user.id
    ensure_user(callback.from_user)

    ok, info, new_bank, new_wallet = bank_take(user_id, amount)
    if not ok:
        await callback.answer(f"❌ {info}", show_alert=True)
        return

    text, kb = build_bank_text_and_kb(user_id)

    try:
        if callback.message.photo:
            await callback.message.edit_caption(
                caption=text, parse_mode="HTML", reply_markup=kb
            )
        else:
            await callback.message.edit_text(
                text, parse_mode="HTML", reply_markup=kb
            )
    except Exception as e:
        print(f"[BANK] Ошибка редактирования: {e}")

    await callback.answer(f"📤 -{amount:,} msg")
# -----------------------------------


# ====================================
#  /case, /rarecase, /lcase
# ====================================

@dp.message(Command("case"))
async def cmd_case(message: Message):
    await _handle_case_open(message, "case")


@dp.message(Command("rarecase"))
async def cmd_rarecase(message: Message):
    await _handle_case_open(message, "rarecase")


@dp.message(Command("lcase"))
async def cmd_lcase(message: Message):
    await _handle_case_open(message, "lcase")


# =========================================================
#  /anon
# =========================================================

@dp.message(Command("anon"))
async def cmd_anon(message: Message):
    log_cmd("💌 /anon", message)
    user = message.from_user
    ensure_user(user)

    mute = get_active_anon_mute(user.id)
    if mute:
        reason, muted_until, _ = mute
        if muted_until is None:
            until_text = "навсегда"
        else:
            try:
                until_dt = datetime.fromisoformat(muted_until)
                diff = until_dt - datetime.now()
                d = diff.days
                h = diff.seconds // 3600
                until_text = f"{d} дн. {h} ч"
            except ValueError:
                until_text = "—"

        await message.answer(
            f"🚫 <b>Тебе запрещено отправлять анонимки</b>\n\n"
            f"└─ Причина: {reason}\n"
            f"└─ Осталось: {until_text}",
            parse_mode="HTML"
        )
        return

    target_id = None
    target_name = None

    if message.reply_to_message:
        target = message.reply_to_message.from_user
        if target.is_bot:
            await message.answer("❌ Нельзя писать анонимки боту")
            return
        target_id = target.id
        target_name = target.full_name

        args = message.text.split(maxsplit=1)
        if len(args) < 2:
            await message.answer("❌ Напиши текст: /anon [текст]", parse_mode="HTML")
            return
        text = args[1].strip()
    else:
        args = message.text.split(maxsplit=2)
        if len(args) < 3 or not args[1].startswith("@"):
            await message.answer(
                "❌ Использование:\n"
                "└─ ответь на сообщение: /anon [текст]\n"
                "└─ или /anon @username [текст]",
                parse_mode="HTML"
            )
            return
        target_arg = args[1]
        text = args[2].strip()

        target_id, target_name = find_user_id(message, target_arg)
        if target_id is None:
            await message.answer("❌ Пользователь не найден")
            return

    if target_id == user.id:
        await message.answer("❌ Нельзя писать анонимку самому себе")
        return

    if is_main_owner(target_id):
        await message.answer("❌ Нельзя писать анонимку главному владельцу")
        return

    if not text:
        await message.answer("❌ Текст пустой")
        return

    if len(text) > 500:
        await message.answer("❌ Текст слишком длинный (макс. 500 символов)")
        return

    if is_anon_shield_active(target_id):
        await message.answer(
            f"🕶️ <b>У {target_name} активен анон-щит</b>\n"
            f"└─ Анонимка не доставлена\n"
            f"└─ msg не списаны"
        )
        return

    balance = get_balance(user.id)
    if balance < PRICE_ANON:
        await message.answer(
            f"😢 <b>Недостаточно msg!</b>\n\n"
            f"└─ Нужно: {PRICE_ANON}\n"
            f"└─ У тебя: {balance}"
            f"{_shortage_hint(PRICE_ANON, balance)}",
            parse_mode="HTML"
        )
        return

    # ✅ Списываем заранее
    add_balance(user.id, -PRICE_ANON)

    # Пытаемся отправить
    try:
        await bot.send_message(
            target_id,
            f"💌 <b>Анонимное сообщение</b>\n\n{text}",
            parse_mode="HTML"
        )
    except Exception as e:
        # ❗ Возвращаем msg при ошибке
        add_balance(user.id, PRICE_ANON)
        await message.answer(f"❌ Не удалось отправить: {e}")
        return

    log_transaction(user.id, target_id, -PRICE_ANON, "anon")
    log_anon(user.id, target_id, text)

    new_balance = get_balance(user.id)

    await message.answer(
        f"✅ <b>Анонимка отправлена</b>\n"
        f"└─ Кому: {target_name}\n"
        f"└─ Стоимость: {PRICE_ANON} msg\n"
        f"└─ Новый баланс: {new_balance} msg",
        parse_mode="HTML"
    )


# =========================================================
#  /marry, /divorce
# =========================================================

@dp.message(Command("marry"))
async def cmd_marry(message: Message):
    log_cmd("💍 /marry", message)
    user = message.from_user
    ensure_user(user)

    if is_married(user.id):
        spouse_id = get_spouse(user.id)
        spouse_data = get_user(spouse_id) if spouse_id else None
        spouse_name = "?"
        if spouse_data:
            uname = spouse_data[1]
            fname = spouse_data[2]
            spouse_name = f"@{uname}" if uname else (fname or f"ID:{spouse_id}")

        await message.answer(
            f"💍 Ты уже в браке с <b>{spouse_name}</b>\n\n💔 Развод: /divorce",
            parse_mode="HTML"
        )
        return

    lvl = get_user_level(user.id)
    if lvl["level"] < MARRY_MIN_LEVEL:
        await message.answer(
            f"🔒 <b>Брак доступен с {MARRY_MIN_LEVEL} уровня</b>\n\n"
            f"└─ Твой уровень: {lvl['level']}\n"
            f"└─ Прогресс: {lvl['current_progress']}/{lvl['next_required']} msg",
            parse_mode="HTML"
        )
        return

    balance = get_balance(user.id)
    if balance < MARRY_PRICE:
        missing = MARRY_PRICE - balance
        await message.answer(
            f"😢 <b>Недостаточно msg!</b>\n\n"
            f"└─ Нужно: {MARRY_PRICE}\n"
            f"└─ У тебя: {balance}\n"
            f"└─ 💡 Не хватает: {missing}",
            parse_mode="HTML"
        )
        return

    target_id = None
    target_name = None

    if message.reply_to_message:
        target = message.reply_to_message.from_user
        if target.is_bot:
            await message.answer("❌ Нельзя жениться на боте")
            return
        target_id = target.id
        target_name = target.full_name
        ensure_user(target)
    else:
        args = message.text.split()[1:]
        if not args or not args[0].startswith("@"):
            await message.answer(
                "❌ Использование:\n"
                "└─ ответь на сообщение: /marry\n"
                "└─ или /marry @username",
                parse_mode="HTML"
            )
            return
        target_id, target_name = find_user_id(message, args[0])
        if target_id is None:
            await message.answer("❌ Пользователь не найден")
            return
        ensure_user_by_id(target_id)

    if target_id == user.id:
        await message.answer("😄 Нельзя жениться на себе")
        return

    if is_married(target_id):
        await message.answer(f"💔 {target_name} уже в браке")
        return

    if get_active_ban(target_id):
        await message.answer(f"❌ {target_name} забанен")
        return

    import uuid
    invite_id = uuid.uuid4().hex[:12]

    _marry_invites[invite_id] = {
        "from_id": user.id,
        "from_name": user.full_name,
        "to_id": target_id,
        "to_name": target_name,
        "created_at": time.monotonic(),
    }

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="💍 Принять", callback_data=f"marry_yes_{invite_id}"),
            InlineKeyboardButton(text="❌ Отклонить", callback_data=f"marry_no_{invite_id}"),
        ]
    ])

    await message.answer(
        f"💍 <b>Предложение руки и сердца</b>\n\n"
        f"└─ От: <b>{user.full_name}</b>\n"
        f"└─ Кому: <b>{target_name}</b>\n\n"
        f"💰 Стоимость: {MARRY_PRICE} msg\n"
        f"⏳ Действует 1 час\n\n"
        f"<i>Ждём ответа...</i>",
        parse_mode="HTML",
        reply_markup=kb
    )


@dp.message(Command("divorce"))
async def cmd_divorce(message: Message):
    log_cmd("💔 /divorce", message)
    user = message.from_user
    ensure_user(user)

    marriage = get_marriage(user.id)
    if not marriage:
        await message.answer(
            "💔 Ты не в браке\n\n💍 Жениться: /marry @user",
            parse_mode="HTML"
        )
        return

    _, u1, u2, total = marriage
    spouse_id = u2 if u1 == user.id else u1

    spouse_data = get_user(spouse_id)
    spouse_name = "?"
    if spouse_data:
        s_uname = spouse_data[1]
        s_fname = spouse_data[2]
        spouse_name = f"@{s_uname}" if s_uname else (s_fname or f"ID:{spouse_id}")

    ok, half1, half2 = divorce_users(user.id)
    if not ok:
        await message.answer("❌ Не удалось развестись")
        return

    await message.answer(
        f"💔 <b>Развод</b>\n\n"
        f"└─ Бывший супруг: {spouse_name}\n"
        f"└─ Общий счёт: {total} msg\n"
        f"└─ Твоя доля: <b>{half1}</b> msg\n"
        f"└─ Твой баланс: {half1} msg",
        parse_mode="HTML"
    )

    try:
        await bot.send_message(
            spouse_id,
            f"💔 <b>Развод</b>\n\n"
            f"└─ Бывший супруг: {user.full_name}\n"
            f"└─ Общий счёт: {total} msg\n"
            f"└─ Твоя доля: <b>{half2}</b> msg\n"
            f"└─ Твой баланс: {half2} msg",
            parse_mode="HTML"
        )
    except Exception:
        pass


# =========================================================
#  CALLBACK: marry (с возвратом msg при ошибке)
# =========================================================

@dp.callback_query(lambda c: c.data.startswith("marry_yes_") or c.data.startswith("marry_no_"))
async def cb_marry(callback: CallbackQuery):
    data = callback.data
    user_id = callback.from_user.id
    user_name = callback.from_user.full_name

    if data.startswith("marry_yes_"):
        invite_id = data.replace("marry_yes_", "")
        invite = _marry_invites.get(invite_id)

        if not invite:
            await callback.answer("⚠️ Предложение устарело", show_alert=True)
            return
        if user_id != invite["to_id"]:
            await callback.answer("❌ Это не для тебя", show_alert=True)
            return
        if time.monotonic() - invite["created_at"] > MARRY_TIMEOUT:
            _marry_invites.pop(invite_id, None)
            await callback.answer("⏰ Предложение истекло", show_alert=True)
            return

        from_id = invite["from_id"]
        to_id = invite["to_id"]

        if is_married(from_id) or is_married(to_id):
            _marry_invites.pop(invite_id, None)
            await callback.message.edit_text("❌ Один из вас уже в браке")
            await callback.answer()
            return

        from_balance = get_balance(from_id)
        if from_balance < MARRY_PRICE:
            _marry_invites.pop(invite_id, None)
            await callback.message.edit_text(
                f"❌ У {invite['from_name']} недостаточно msg для оплаты"
            )
            await callback.answer()
            return

        # ✅ Списываем ДО создания
        add_balance(from_id, -MARRY_PRICE)

        if not marry_users(from_id, to_id):
            # ❗ Возврат msg при ошибке
            add_balance(from_id, MARRY_PRICE)
            _marry_invites.pop(invite_id, None)
            await callback.message.edit_text("❌ Не удалось создать брак")
            await callback.answer()
            return

        _marry_invites.pop(invite_id, None)

        try:
            await callback.message.edit_text(
                f"💍 <b>Брак заключён!</b>\n\n"
                f"└─ {invite['from_name']} 💕 {invite['to_name']}\n\n"
                f"💰 Стоимость: {MARRY_PRICE} msg (оплатил инициатор)\n"
                f"👥 Теперь у вас общий счёт\n"
                f"💔 Развод: /divorce",
                parse_mode="HTML"
            )
        except Exception:
            pass

        try:
            await bot.send_message(
                from_id,
                f"💍 <b>Тебе ответили «Да»!</b>\n\n"
                f"└─ Супруг: <b>{invite['to_name']}</b>\n"
                f"└─ Теперь у вас общий счёт",
                parse_mode="HTML"
            )
        except Exception:
            pass

        log_transaction(from_id, to_id, -MARRY_PRICE, "marry")
        await callback.answer("💍 Брак заключён!")

    elif data.startswith("marry_no_"):
        invite_id = data.replace("marry_no_", "")
        invite = _marry_invites.get(invite_id)
        if not invite:
            await callback.answer("⚠️ Предложение устарело", show_alert=True)
            return
        if user_id != invite["to_id"]:
            await callback.answer("❌ Это не для тебя", show_alert=True)
            return

        _marry_invites.pop(invite_id, None)
        try:
            await callback.message.edit_text(f"❌ <b>{user_name}</b> отклонил предложение")
        except Exception:
            pass
        await callback.answer("❌ Отклонено")

# =====================================
#  КРЕСТИКИ-НОЛИКИ
# =====================================

def ttt_create(player_x_id: int, player_o_id: int, bet: int) -> int:
    """Создаёт партию. X ходит первым."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO tictactoe "
        "(player_x_id, player_o_id, bet, board, turn_id, status, created_at, last_move_at) "
        "VALUES (?, ?, ?, ?, ?, 'pending', ?, ?)",
        (player_x_id, player_o_id, bet,
         "---------", player_x_id,
         datetime.now().isoformat(), datetime.now().isoformat())
    )
    conn.commit()
    game_id = cur.lastrowid
    conn.close()
    return game_id


def ttt_get(game_id: int):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "SELECT id, player_x_id, player_o_id, bet, board, turn_id, status, "
        "message_id, chat_id, created_at, last_move_at "
        "FROM tictactoe WHERE id = ?",
        (game_id,)
    )
    row = cur.fetchone()
    conn.close()
    return row


def ttt_update(game_id: int, **fields):
    if not fields:
        return
    keys = ", ".join(f"{k} = ?" for k in fields.keys())
    values = list(fields.values()) + [game_id]

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(f"UPDATE tictactoe SET {keys} WHERE id = ?", values)
    conn.commit()
    conn.close()


def ttt_delete(game_id: int):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("DELETE FROM tictactoe WHERE id = ?", (game_id,))
    conn.commit()
    conn.close()


def get_user_ttt(user_id: int):
    """Активная игра юзера (pending или active)."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "SELECT id, player_x_id, player_o_id, bet, board, turn_id, status, "
        "message_id, chat_id, created_at, last_move_at "
        "FROM tictactoe "
        "WHERE (player_x_id = ? OR player_o_id = ?) "
        "AND status IN ('pending', 'active') "
        "ORDER BY id DESC LIMIT 1",
        (user_id, user_id)
    )
    row = cur.fetchone()
    conn.close()
    return row


def get_stale_ttt(timeout_seconds: int) -> list:
    """Игры, брошенные по таймауту."""
    threshold = (datetime.now() - timedelta(seconds=timeout_seconds)).isoformat()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "SELECT id FROM tictactoe "
        "WHERE status = 'active' AND last_move_at < ?",
        (threshold,)
    )
    rows = cur.fetchall()
    conn.close()
    return [row[0] for row in rows]


def get_pending_ttt_older_than(timeout_seconds: int) -> list:
    threshold = (datetime.now() - timedelta(seconds=timeout_seconds)).isoformat()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "SELECT id FROM tictactoe "
        "WHERE status = 'pending' AND created_at < ?",
        (threshold,)
    )
    rows = cur.fetchall()
    conn.close()
    return [row[0] for row in rows]
TTT_MIN_BET = 500       # минимальная ставка
TTT_TIMEOUT = 300       # 5 минут на приглашение
TTT_TURN_TIMEOUT = 60   # 1 минута на ход

# Выигрышные линии
TTT_LINES = [
    (0, 1, 2), (3, 4, 5), (6, 7, 8),   # горизонтали
    (0, 3, 6), (1, 4, 7), (2, 5, 8),   # вертикали
    (0, 4, 8), (2, 4, 6),               # диагонали
]


def _ttt_check_winner(board: str):
    """
    Возвращает:
      'X' — победил X
      'O' — победил O
      'D' — ничья
      None — игра продолжается
    """
    for a, b, c in TTT_LINES:
        if board[a] != "-" and board[a] == board[b] == board[c]:
            return board[a]

    if "-" not in board:
        return "D"

    return None

def _ttt_render(game_id: int, viewer_id: int):
    """Возвращает (text, kb) для игры."""
    game = ttt_get(game_id)
    if not game:
        return None, None

    (gid, x_id, o_id, bet, board, turn_id, status,
     msg_id, chat_id, created_at, last_move_at) = game

    # Имена
    def _name(uid):
        data = get_user(uid)
        if not data:
            return f"ID:{uid}"
        uname, fname = data[1], data[2]
        return f"@{uname}" if uname else (fname or f"ID:{uid}")

    x_name = _name(x_id)
    o_name = _name(o_id)

    # Эмодзи на клетке
    EMOJI = {"X": "❌", "O": "⭕", "-": "⬜"}

    # Текст шапки
    if status == "pending":
        text = (
            f"❌ <b>Крестики-нолики</b> ⭕\n\n"
            f"└─ ❌ {x_name}\n"
            f"└─ ⭕ {o_name}\n"
            f"└─ 💰 Ставка: <b>{bet}</b> msg\n\n"
            f"<i>Ждём принятия...</i>"
        )
        return text, None

    if status == "done":
        winner = _ttt_check_winner(board)
        if winner == "X":
            result = f"🏆 Победил ❌ <b>{x_name}</b>!"
        elif winner == "O":
            result = f"🏆 Победил ⭕ <b>{o_name}</b>!"
        else:
            result = "🤝 Ничья!"

        # Сетка
        grid = "\n".join(
            " ".join(EMOJI[board[r * 3 + c]] for c in range(3))
            for r in range(3)
        )

        text = (
            f"❌ <b>Крестики-нолики</b> ⭕\n\n"
            f"{grid}\n\n"
            f"{result}"
        )
        return text, None

    # Активная игра
    turn_mark = "❌" if turn_id == x_id else "⭕"
    turn_name = x_name if turn_id == x_id else o_name

    grid = "\n".join(
        " ".join(EMOJI[board[r * 3 + c]] for c in range(3))
        for r in range(3)
    )

    text = (
        f"❌ <b>Крестики-нолики</b> ⭕\n\n"
        f"└─ ❌ {x_name}\n"
        f"└─ ⭕ {o_name}\n"
        f"└─ 💰 Ставка: <b>{bet}</b> msg\n\n"
        f"{grid}\n\n"
        f"⏳ Ход: {turn_mark} <b>{turn_name}</b>"
    )

    # Кнопки для активной игры
    # Показываем ВСЕМ (как в /duel), проверка хода — в callback
    kb_rows = []
    for r in range(3):
        row = []
        for c in range(3):
            idx = r * 3 + c
            cell = board[idx]

            if cell == "-":
                # Пустая клетка — кликабельная
                row.append(InlineKeyboardButton(
                    text="⬜",
                    callback_data=f"ttt_move_{game_id}_{idx}"
                ))
            else:
                # Занятая — показываем символ, но не кликабельно
                # (Telegram не даёт «некликабельные» кнопки,
                #  поэтому используем любой callback — он отклонит)
                row.append(InlineKeyboardButton(
                    text=EMOJI[cell],
                    callback_data=f"ttt_noop"
                ))
        kb_rows.append(row)

    # Кнопка "Сдаться"
    kb_rows.append([
        InlineKeyboardButton(
            text="🏳️ Сдаться",
            callback_data=f"ttt_flee_{game_id}"
        )
    ])

    kb = InlineKeyboardMarkup(inline_keyboard=kb_rows)
    return text, kb

@dp.message(Command("ttt"))
async def cmd_ttt(message: Message):
    log_cmd("❌ /ttt", message)
    user = message.from_user
    ensure_user(user)

    # Уже в игре?
    active = get_user_ttt(user.id)
    if active:
        game_id = active[0]
        text, kb = _ttt_render(game_id, user.id)
        await message.answer(
            f"⏳ <b>Ты уже в игре</b>\n\n{text}",
            parse_mode="HTML",
            reply_markup=kb
        )
        return

    args = message.text.split()[1:]

    target_id = None
    target_name = None
    bet = None

    # Ищем цель
    if message.reply_to_message:
        target = message.reply_to_message.from_user
        if target.is_bot:
            await message.answer("❌ Нельзя вызвать бота")
            return
        target_id = target.id
        target_name = target.full_name
        ensure_user(target)

        if len(args) != 1:
            await message.answer(
                "❌ Формат: ответь на сообщение и напиши <code>/ttt [ставка]</code>",
                parse_mode="HTML"
            )
            return
        try:
            bet = int(args[0])
        except ValueError:
            await message.answer("❌ Ставка должна быть числом")
            return
    else:
        if len(args) != 2 or not args[0].startswith("@"):
            await message.answer(
                "❌ Использование:\n"
                "└─ ответь на сообщение: <code>/ttt [ставка]</code>\n"
                "└─ или <code>/ttt @username [ставка]</code>",
                parse_mode="HTML"
            )
            return

        target_id, target_name = find_user_id(message, args[0])
        if target_id is None:
            await message.answer("❌ Пользователь не найден")
            return
        ensure_user_by_id(target_id)

        try:
            bet = int(args[1])
        except ValueError:
            await message.answer("❌ Ставка должна быть числом")
            return

    if target_id == user.id:
        await message.answer("😄 Нельзя играть с самим собой")
        return

    if bet < TTT_MIN_BET:
        await message.answer(
            f"❌ Минимальная ставка: <b>{TTT_MIN_BET}</b> msg",
            parse_mode="HTML"
        )
        return

    # Проверки
    if get_user_ttt(target_id):
        await message.answer(f"❌ {target_name} уже в игре")
        return

    if get_active_ban(target_id):
        await message.answer(f"❌ {target_name} забанен")
        return

    balance = get_balance(user.id)
    if balance < bet:
        await message.answer(
            f"😢 <b>Недостаточно msg!</b>\n\n"
            f"└─ Нужно: {bet}\n"
            f"└─ У тебя: {balance}"
            f"{_shortage_hint(bet, balance)}",
            parse_mode="HTML"
        )
        return

    target_balance = get_balance(target_id)
    if target_balance < bet:
        await message.answer(
            f"❌ У {target_name} недостаточно msg\n"
            f"└─ Нужно: {bet}\n"
            f"└─ У него: {target_balance}"
        )
        return

    # Создаём приглашение
    import uuid
    invite_id = uuid.uuid4().hex[:12]

    _ttt_invites[invite_id] = {
        "challenger_id": user.id,
        "challenger_name": user.full_name,
        "opponent_id": target_id,
        "opponent_name": target_name,
        "bet": bet,
        "created_at": time.monotonic(),
    }

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="❌ Принять", callback_data=f"ttt_yes_{invite_id}"),
            InlineKeyboardButton(text="❌ Отклонить", callback_data=f"ttt_no_{invite_id}"),
        ]
    ])

    await message.answer(
        f"❌ <b>Крестики-нолики</b> ⭕\n\n"
        f"└─ Вызывающий: <b>{user.full_name}</b> (❌)\n"
        f"└─ Противник: <b>{target_name}</b> (⭕)\n\n"
        f"💰 Ставка: <b>{bet}</b> msg\n"
        f"🎲 Кто первый — <b>случайно</b>\n"
        f"⏳ Действует 5 минут\n\n"
        f"<i>Ждём ответа...</i>",
        parse_mode="HTML",
        reply_markup=kb
    )

@dp.callback_query(lambda c: c.data.startswith("ttt_yes_") or c.data.startswith("ttt_no_"))
async def cb_ttt_invite(callback: CallbackQuery):
    data = callback.data
    user_id = callback.from_user.id
    user_name = callback.from_user.full_name

    if data.startswith("ttt_yes_"):
        invite_id = data.replace("ttt_yes_", "")
        invite = _ttt_invites.get(invite_id)

        if not invite:
            await callback.answer("⚠️ Приглашение устарело", show_alert=True)
            return
        if user_id != invite["opponent_id"]:
            await callback.answer("❌ Это не для тебя", show_alert=True)
            return
        if time.monotonic() - invite["created_at"] > TTT_TIMEOUT:
            _ttt_invites.pop(invite_id, None)
            await callback.answer("⏰ Приглашение истекло", show_alert=True)
            return

        challenger_id = invite["challenger_id"]
        opponent_id = invite["opponent_id"]
        bet = invite["bet"]

        # Проверка баланса
        ch_balance = get_balance(challenger_id)
        op_balance = get_balance(opponent_id)

        if ch_balance < bet or op_balance < bet:
            _ttt_invites.pop(invite_id, None)
            await callback.message.edit_text("❌ У одного из игроков недостаточно msg")
            await callback.answer()
            return

        # Списываем ставки
        add_balance(challenger_id, -bet)
        add_balance(opponent_id, -bet)

        # Кто X, кто O — случайно
        if random.random() < 0.5:
            x_id, o_id = challenger_id, opponent_id
        else:
            x_id, o_id = opponent_id, challenger_id

        try:
            game_id = ttt_create(x_id, o_id, bet)
        except Exception as e:
            # Возврат при ошибке
            add_balance(challenger_id, bet)
            add_balance(opponent_id, bet)
            _ttt_invites.pop(invite_id, None)
            await callback.message.edit_text(f"❌ Ошибка создания игры: {e}")
            await callback.answer()
            return

        # Активируем
        ttt_update(
            game_id,
            status="active",
            message_id=callback.message.message_id,
            chat_id=callback.message.chat.id
        )

        _ttt_invites.pop(invite_id, None)

        log_transaction(challenger_id, opponent_id, bet, "ttt_start")

        # Рендерим
        text, kb = _ttt_render(game_id, user_id)
        try:
            await callback.message.edit_text(
                text, parse_mode="HTML", reply_markup=kb
            )
        except Exception as e:
            print(f"[TTT] Ошибка рендера: {e}")

        await callback.answer("🎮 Игра началась!")

    elif data.startswith("ttt_no_"):
        invite_id = data.replace("ttt_no_", "")
        invite = _ttt_invites.get(invite_id)

        if not invite:
            await callback.answer("⚠️ Приглашение устарело", show_alert=True)
            return
        if user_id != invite["opponent_id"]:
            await callback.answer("❌ Это не для тебя", show_alert=True)
            return

        _ttt_invites.pop(invite_id, None)
        try:
            await callback.message.edit_text(
                f"❌ <b>{user_name}</b> отклонил вызов"
            )
        except Exception:
            pass
        await callback.answer("❌ Отклонено")

@dp.callback_query(lambda c: c.data.startswith("ttt_move_"))
async def cb_ttt_move(callback: CallbackQuery):
    data = callback.data
    user_id = callback.from_user.id

    # Формат: ttt_move_{game_id}_{cell_idx}
    parts = data.split("_")
    if len(parts) != 4:
        await callback.answer("⚠️ Ошибка данных", show_alert=True)
        return

    try:
        game_id = int(parts[2])
        cell_idx = int(parts[3])
    except ValueError:
        await callback.answer("⚠️ Ошибка данных", show_alert=True)
        return

    game = ttt_get(game_id)
    if not game:
        await callback.answer("⚠️ Игра не найдена", show_alert=True)
        return

    (gid, x_id, o_id, bet, board, turn_id, status,
     msg_id, chat_id, created_at, last_move_at) = game

    if status != "active":
        await callback.answer("⚠️ Игра не активна", show_alert=True)
        return

    # Проверка: ты игрок?
    if user_id not in (x_id, o_id):
        await callback.answer("❌ Ты не участник", show_alert=True)
        return

    # Проверка: твой ход?
    if user_id != turn_id:
        await callback.answer("⏳ Сейчас не твой ход", show_alert=True)
        return

    # Проверка: клетка свободна?
    if cell_idx < 0 or cell_idx > 8:
        await callback.answer("⚠️ Ошибка клетки", show_alert=True)
        return

    if board[cell_idx] != "-":
        await callback.answer("❌ Клетка занята", show_alert=True)
        return

    # Твой символ
    my_mark = "X" if user_id == x_id else "O"

    # Обновляем поле
    new_board = board[:cell_idx] + my_mark + board[cell_idx + 1:]

    # Проверка победы
    winner = _ttt_check_winner(new_board)

    if winner is None:
        # Игра продолжается — передаём ход
        next_turn = o_id if turn_id == x_id else x_id

        ttt_update(
            game_id,
            board=new_board,
            turn_id=next_turn,
            last_move_at=datetime.now().isoformat()
        )

        # Рендер
        text, kb = _ttt_render(game_id, user_id)
        try:
            await callback.message.edit_text(
                text, parse_mode="HTML", reply_markup=kb
            )
        except Exception as e:
            print(f"[TTT] Ошибка редактирования: {e}")

        await callback.answer(f"✅ Ход сделан: {my_mark}")

    else:
        # Игра закончена
        ttt_update(
            game_id,
            board=new_board,
            status="done",
            last_move_at=datetime.now().isoformat()
        )

        # Обработка результата
        if winner == "D":
            # Ничья — возврат ставок
            add_balance(x_id, bet)
            add_balance(o_id, bet)
            log_transaction(x_id, o_id, bet, "ttt_draw")

            # Рендер
            text, kb = _ttt_render(game_id, user_id)
            try:
                await callback.message.edit_text(
                    text, parse_mode="HTML"
                )
            except Exception:
                pass

            # Уведомления
            for uid, name in ((x_id, "❌"), (o_id, "⭕")):
                try:
                    await bot.send_message(
                        uid,
                        f"🤝 <b>Ничья в крестиках-ноликах</b>\n\n"
                        f"└─ Ставка возвращена: {bet} msg"
                    )
                except Exception:
                    pass

            await callback.answer("🤝 Ничья!")

        else:
            # Победа одного
            winner_id = x_id if winner == "X" else o_id
            loser_id = o_id if winner == "X" else x_id

            add_balance(winner_id, bet * 2)
            log_transaction(loser_id, winner_id, bet, "ttt_win")

            # Рендер
            text, kb = _ttt_render(game_id, user_id)
            try:
                await callback.message.edit_text(
                    text, parse_mode="HTML"
                )
            except Exception:
                pass

            winner_name = "?"
            wdata = get_user(winner_id)
            if wdata:
                uname, fname = wdata[1], wdata[2]
                winner_name = f"@{uname}" if uname else (fname or f"ID:{winner_id}")

            # Уведомление
            try:
                await bot.send_message(
                    loser_id,
                    f"❌ <b>Ты проиграл в крестики-нолики</b>\n\n"
                    f"└─ Победитель: {winner_name}\n"
                    f"└─ Потеряно: {bet} msg"
                )
            except Exception:
                pass

            await callback.answer(f"🏆 Победа! +{bet * 2} msg")

        # Удаляем игру
        ttt_delete(game_id)

@dp.callback_query(lambda c: c.data == "ttt_noop")
async def cb_ttt_noop(callback: CallbackQuery):
    await callback.answer("Занято")

@dp.callback_query(lambda c: c.data.startswith("ttt_flee_"))
async def cb_ttt_flee(callback: CallbackQuery):
    data = callback.data
    user_id = callback.from_user.id

    try:
        game_id = int(data.replace("ttt_flee_", ""))
    except ValueError:
        await callback.answer("⚠️ Ошибка данных", show_alert=True)
        return

    game = ttt_get(game_id)
    if not game:
        await callback.answer("⚠️ Игра не найдена", show_alert=True)
        return

    (gid, x_id, o_id, bet, board, turn_id, status,
     msg_id, chat_id, created_at, last_move_at) = game

    if status != "active":
        await callback.answer("⚠️ Игра не активна", show_alert=True)
        return

    if user_id not in (x_id, o_id):
        await callback.answer("❌ Ты не участник", show_alert=True)
        return

    # Победитель — соперник
    winner_id = o_id if user_id == x_id else x_id
    loser_id = user_id

    add_balance(winner_id, bet * 2)
    log_transaction(loser_id, winner_id, bet, "ttt_flee")

    # Обновляем — ставим статус done и «показываем» победу
    ttt_update(game_id, status="done")

    text = f"🏳️ <b>{callback.from_user.full_name} сдался</b>\n\n🏆 Соперник забирает банк"

    try:
        await callback.message.edit_text(
            text, parse_mode="HTML"
        )
    except Exception:
        pass

    try:
        await bot.send_message(
            winner_id,
            f"🏆 <b>Соперник сдался!</b>\n\n"
            f"└─ Ты получаешь: +{bet * 2} msg"
        )
    except Exception:
        pass

    ttt_delete(game_id)
    await callback.answer("🏳️ Сдался")

async def _ttt_watchdog():
    """Раз в 30 сек проверяет брошенные игры."""
    while True:
        await asyncio.sleep(30)
        try:
            # 1) Активные игры — таймаут на ход
            stale = get_stale_ttt(TTT_TURN_TIMEOUT)
            for gid in stale:
                game = ttt_get(gid)
                if not game:
                    continue

                (g, x_id, o_id, bet, board, turn_id, status,
                 msg_id, chat_id, *_rest) = game

                if status != "active":
                    continue

                # Проиграл тот, чей ход (не сходил)
                loser_id = turn_id
                winner_id = o_id if loser_id == x_id else x_id

                add_balance(winner_id, bet * 2)
                log_transaction(loser_id, winner_id, bet, "ttt_timeout")

                text = (
                    f"⏰ <b>Таймаут хода</b>\n\n"
                    f"└─ Ход не сделан за {TTT_TURN_TIMEOUT} сек\n"
                    f"└─ Победитель забирает банк: +{bet * 2} msg"
                )

                if msg_id and chat_id:
                    try:
                        await bot.edit_message_text(
                            chat_id=chat_id, message_id=msg_id,
                            text=text, parse_mode="HTML",
                            reply_markup=None
                        )
                    except Exception:
                        pass

                ttt_delete(gid)

            # 2) Pending старше TTT_TIMEOUT — просто удалить
            old_pending = get_pending_ttt_older_than(TTT_TIMEOUT)
            for gid in old_pending:
                ttt_delete(gid)

        except Exception as e:
            print(f"[TTT-WATCHDOG] Ошибка: {e}")



# =====================================
#  ДУЭЛЬ
# =====================================

def _duel_kb(duel_id: int, turn: int,
             am1: int, am2: int, used_heal1: int, used_heal2: int):
    """
    Клавиатура показывается ВСЕМ участникам, но кнопки — от лица того,
    чей сейчас ход. Проверка «чей ход» — в cb_duel_move.
    Если нажал не тот — получит алерт «сейчас не твой ход».
    """
    if turn == 0:
        my_am = am1
        my_heal = used_heal1
    else:
        my_am = am2
        my_heal = used_heal2

    row1 = [InlineKeyboardButton(
        text="🗡️ Атака",
        callback_data=f"duel_move_{duel_id}_attack"
    )]

    row2 = []
    if my_am >= 1:
        row2.append(InlineKeyboardButton(
            text="🛡️ Защита (1🎯)",
            callback_data=f"duel_move_{duel_id}_shield"
        ))
    if my_am >= 2:
        row2.append(InlineKeyboardButton(
            text="🔫 Пистолет (2🎯)",
            callback_data=f"duel_move_{duel_id}_pistol"
        ))

    row3 = []
    if my_am >= 1 and not my_heal:
        row3.append(InlineKeyboardButton(
            text="💚 Лечение (1🎯)",
            callback_data=f"duel_move_{duel_id}_heal"
        ))

    rows = [row1]
    if row2:
        rows.append(row2)
    if row3:
        rows.append(row3)

    return InlineKeyboardMarkup(inline_keyboard=rows)


async def _render_duel(chat_id: int, duel_id: int, edit: bool = True):
    duel = duel_get(duel_id)
    if not duel:
        return

    (did, ch_id, op_id, bet, status, hp1, hp2, am1, am2, turn, msg_id, cid,
     move1, move2, used_heal1, used_heal2, created_at) = duel

    ch_data = get_user(ch_id)
    op_data = get_user(op_id)
    ch_name = (ch_data[1] and f"@{ch_data[1]}") or ch_data[2] or f"ID:{ch_id}" if ch_data else "?"
    op_name = (op_data[1] and f"@{op_data[1]}") or op_data[2] or f"ID:{op_id}" if op_data else "?"

    if status == "active":
        if move1 and not move2:
            # Первый сделал ход, второй ещё не сделал
            text = (
                f"⚔️ <b>ДУЭЛЬ</b>\n\n"
                f"<b>{ch_name}</b> ❤️ {hp1}/3 · 🎯 {am1}\n"
                f"<b>{op_name}</b> ❤️ {hp2}/3 · 🎯 {am2}\n\n"
                f"⏳ <b>{ch_name}</b> сделал ход\n"
                f"🎯 Ждём ход: <b>{op_name}</b>"
            )
        elif move2 and not move1:
            # Второй сделал ход, первый ещё не сделал
            text = (
                f"⚔️ <b>ДУЭЛЬ</b>\n\n"
                f"<b>{ch_name}</b> ❤️ {hp1}/3 · 🎯 {am1}\n"
                f"<b>{op_name}</b> ❤️ {hp2}/3 · 🎯 {am2}\n\n"
                f"⏳ <b>{op_name}</b> сделал ход\n"
                f"🎯 Ждём ход: <b>{ch_name}</b>"
            )
        else:
            # Оба могут ходить (начало раунда)
            current_name = ch_name if turn == 0 else op_name
            text = (
                f"⚔️ <b>ДУЭЛЬ</b>\n\n"
                f"<b>{ch_name}</b> ❤️ {hp1}/3 · 🎯 {am1}\n"
                f"<b>{op_name}</b> ❤️ {hp2}/3 · 🎯 {am2}\n\n"
                f"⏳ Ход: <b>{current_name}</b>"
            )
    else:
        text = "⚔️ Дуэль завершена"

    # ✅ Клавиатура показывается ВСЕГДА, пока раунд не завершён.
    # Кнопки — от лица того, чей сейчас ход.
    # Проверка «чей ход» — внутри cb_duel_move.
    kb = None
    if status == "active":
        kb = _duel_kb(duel_id, turn, am1, am2, used_heal1, used_heal2)

    try:
        if edit:
            await bot.edit_message_text(
                chat_id=chat_id, message_id=msg_id, text=text,
                parse_mode="HTML", reply_markup=kb
            )
        else:
            msg = await bot.send_message(chat_id, text, parse_mode="HTML", reply_markup=kb)
            duel_update(duel_id, message_id=msg.message_id, chat_id=chat_id)
    except Exception as e:
        print(f"[DUEL] Ошибка рендера: {e}")

@dp.message(Command("duel"))
async def cmd_duel(message: Message):
    log_cmd("⚔️ /duel", message)
    user = message.from_user
    ensure_user(user)

    active = get_user_duel(user.id)
    if active:
        await message.answer("⚔️ Ты уже в дуэли! Заверши её.", parse_mode="HTML")
        return

    args = message.text.split()[1:]
    target_id = None
    target_name = None
    bet = None

    if message.reply_to_message:
        target = message.reply_to_message.from_user
        if target.is_bot:
            await message.answer("❌ Нельзя вызвать бота")
            return
        target_id = target.id
        target_name = target.full_name
        ensure_user(target)

        if len(args) != 1:
            await message.answer(
                "❌ Формат: ответь на сообщение и напиши <code>/duel [ставка]</code>",
                parse_mode="HTML"
            )
            return
        try:
            bet = int(args[0])
        except ValueError:
            await message.answer("❌ Ставка должна быть числом")
            return
    else:
        if len(args) != 2 or not args[0].startswith("@"):
            await message.answer(
                "❌ Использование:\n"
                "└─ ответь на сообщение: <code>/duel [ставка]</code>\n"
                "└─ или <code>/duel @username [ставка]</code>",
                parse_mode="HTML"
            )
            return

        target_id, target_name = find_user_id(message, args[0])
        if target_id is None:
            await message.answer("❌ Пользователь не найден")
            return
        ensure_user_by_id(target_id)

        try:
            bet = int(args[1])
        except ValueError:
            await message.answer("❌ Ставка должна быть числом")
            return

    if target_id == user.id:
        await message.answer("😄 Нельзя вызвать себя")
        return

    if bet < DUEL_MIN_BET:
        await message.answer(f"❌ Минимальная ставка: <b>{DUEL_MIN_BET}</b> msg", parse_mode="HTML")
        return

    if get_user_duel(target_id):
        await message.answer(f"⚔️ {target_name} уже в дуэли")
        return

    if get_active_ban(target_id):
        await message.answer(f"❌ {target_name} забанен")
        return

    balance = get_balance(user.id)
    if balance < bet:
        await message.answer(
            f"😢 <b>Недостаточно msg!</b>\n\n"
            f"└─ Нужно: {bet}\n"
            f"└─ У тебя: {balance}"
            f"{_shortage_hint(bet, balance)}",
            parse_mode="HTML"
        )
        return

    target_balance = get_balance(target_id)
    if target_balance < bet:
        await message.answer(
            f"❌ У {target_name} недостаточно msg\n"
            f"└─ Нужно: {bet}\n"
            f"└─ У него: {target_balance}"
        )
        return

    import uuid
    invite_id = uuid.uuid4().hex[:12]

    _duel_invites[invite_id] = {
        "challenger_id": user.id,
        "challenger_name": user.full_name,
        "opponent_id": target_id,
        "opponent_name": target_name,
        "bet": bet,
        "created_at": time.monotonic(),
    }

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="⚔️ Принять", callback_data=f"duel_yes_{invite_id}"),
            InlineKeyboardButton(text="❌ Отклонить", callback_data=f"duel_no_{invite_id}"),
        ]
    ])

    await message.answer(
        f"⚔️ <b>Вызов на дуэль!</b>\n\n"
        f"└─ Вызывающий: <b>{user.full_name}</b>\n"
        f"└─ Противник: <b>{target_name}</b>\n\n"
        f"💰 Ставка: <b>{bet}</b> msg\n"
        f"❤️ Жизни: 3 у каждого\n"
        f"🎯 Аминки: 3 у каждого\n"
        f"⏳ Действует 5 минут\n\n"
        f"<i>Ждём ответа...</i>",
        parse_mode="HTML",
        reply_markup=kb
    )


@dp.callback_query(lambda c: c.data.startswith("duel_yes_") or c.data.startswith("duel_no_"))
async def cb_duel_invite(callback: CallbackQuery):
    data = callback.data
    user_id = callback.from_user.id
    user_name = callback.from_user.full_name

    if data.startswith("duel_yes_"):
        invite_id = data.replace("duel_yes_", "")
        invite = _duel_invites.get(invite_id)

        if not invite:
            await callback.answer("⚠️ Приглашение устарело", show_alert=True)
            return
        if user_id != invite["opponent_id"]:
            await callback.answer("❌ Это не для тебя", show_alert=True)
            return
        if time.monotonic() - invite["created_at"] > DUEL_TIMEOUT:
            _duel_invites.pop(invite_id, None)
            await callback.answer("⏰ Приглашение истекло", show_alert=True)
            return

        challenger_id = invite["challenger_id"]
        opponent_id = invite["opponent_id"]
        bet = invite["bet"]

        ch_balance = get_balance(challenger_id)
        op_balance = get_balance(opponent_id)

        if ch_balance < bet or op_balance < bet:
            _duel_invites.pop(invite_id, None)
            await callback.message.edit_text("❌ У одного из игроков недостаточно msg")
            await callback.answer()
            return

        # ✅ Списываем ставки
        add_balance(challenger_id, -bet)
        add_balance(opponent_id, -bet)

        # Создаём дуэль
        try:
            duel_id = duel_create(challenger_id, opponent_id, bet)
        except Exception as e:
            # ❗ Возврат при ошибке БД
            add_balance(challenger_id, bet)
            add_balance(opponent_id, bet)
            _duel_invites.pop(invite_id, None)
            await callback.message.edit_text(f"❌ Ошибка создания дуэли: {e}")
            await callback.answer()
            return

        first_turn = random.randint(0, 1)
        duel_update(duel_id, turn=first_turn, status="active")
        duel_update(
            duel_id,
            message_id=callback.message.message_id,
            chat_id=callback.message.chat.id
        )

        _duel_invites.pop(invite_id, None)
        await _render_duel(callback.message.chat.id, duel_id, edit=True)

        log_transaction(challenger_id, opponent_id, bet, "duel_start")
        await callback.answer("⚔️ Дуэль началась!")

    elif data.startswith("duel_no_"):
        invite_id = data.replace("duel_no_", "")
        invite = _duel_invites.get(invite_id)
        if not invite:
            await callback.answer("⚠️ Приглашение устарело", show_alert=True)
            return
        if user_id != invite["opponent_id"]:
            await callback.answer("❌ Это не для тебя", show_alert=True)
            return

        _duel_invites.pop(invite_id, None)
        try:
            await callback.message.edit_text(f"❌ <b>{user_name}</b> отклонил вызов на дуэль")
        except Exception:
            pass
        await callback.answer("❌ Отклонено")


@dp.callback_query(lambda c: c.data.startswith("duel_move_"))
async def cb_duel_move(callback: CallbackQuery):
    data = callback.data
    user_id = callback.from_user.id

    parts = data.split("_", 3)
    if len(parts) != 4:
        await callback.answer("⚠️ Ошибка данных", show_alert=True)
        return

    try:
        duel_id = int(parts[2])
    except ValueError:
        await callback.answer("⚠️ Ошибка данных", show_alert=True)
        return

    move = parts[3]
    if move not in ("attack", "shield", "pistol", "heal"):
        await callback.answer("⚠️ Неизвестное действие", show_alert=True)
        return

    duel = duel_get(duel_id)
    if not duel:
        await callback.answer("⚠️ Дуэль не найдена", show_alert=True)
        return

    (did, ch_id, op_id, bet, status, hp1, hp2, am1, am2, turn, msg_id, chat_id,
     move1, move2, used_heal1, used_heal2, created_at) = duel

    if status != "active":
        await callback.answer("⚠️ Дуэль не активна", show_alert=True)
        return

    if user_id not in (ch_id, op_id):
        await callback.answer("❌ Ты не участник", show_alert=True)
        return

    # ✅ Чей сейчас ход
    expected_player = ch_id if turn == 0 else op_id
    if user_id != expected_player:
        await callback.answer("⏳ Сейчас не твой ход", show_alert=True)
        return

    # ✅ Не сделал ли уже ход в этом раунде
    is_challenger = (user_id == ch_id)
    if is_challenger and move1:
        await callback.answer("⏳ Ты уже сделал ход в этом раунде", show_alert=True)
        return
    if (not is_challenger) and move2:
        await callback.answer("⏳ Ты уже сделал ход в этом раунде", show_alert=True)
        return

    # Аминки / лечение текущего игрока
    if is_challenger:
        my_am = am1
        my_heal = used_heal1
    else:
        my_am = am2
        my_heal = used_heal2

    cost = 0
    if move == "attack":
        cost = 0
    elif move == "shield":
        cost = 1
    elif move == "pistol":
        cost = 2
    elif move == "heal":
        cost = 1
        if my_heal:
            await callback.answer("❌ Лечение уже использовано", show_alert=True)
            return

    if my_am < cost:
        await callback.answer(f"❌ Не хватает аминок (нужно {cost})", show_alert=True)
        return

    # Записываем ход
    if is_challenger:
        duel_update(duel_id, move1=move, am1=am1 - cost)
        if move == "heal":
            duel_update(duel_id, used_heal1=1)
    else:
        duel_update(duel_id, move2=move, am2=am2 - cost)
        if move == "heal":
            duel_update(duel_id, used_heal2=1)

    move_names = {
        "attack": "🗡️ Атака",
        "shield": "🛡️ Защита",
        "pistol": "🔫 Пистолет",
        "heal": "💚 Лечение",
    }
    await callback.answer(f"✅ Ты выбрал: {move_names[move]}")

    # Перечитываем дуэль
    duel = duel_get(duel_id)
    (did, ch_id, op_id, bet, status, hp1, hp2, am1, am2, turn, msg_id, chat_id,
     move1, move2, used_heal1, used_heal2, created_at) = duel

    # ✅ Проверяем: оба сделали ход?
    if move1 and move2:
        # Оба сделали — резолвим раунд
        await _resolve_duel_round(duel_id)
    else:
        # ✅ Передаём ход ДРУГОМУ и показываем ЕГО клавиатуру
        # Но НЕ резолвим — ждём второго
        new_turn = 1 if turn == 0 else 0
        duel_update(duel_id, turn=new_turn)
        await _render_duel(chat_id, duel_id, edit=True)


async def _resolve_duel_round(duel_id: int):
    duel = duel_get(duel_id)
    if not duel:
        return

    (did, ch_id, op_id, bet, status, hp1, hp2, am1, am2, turn, msg_id, chat_id,
     move1, move2, used_heal1, used_heal2, created_at) = duel

    move_names = {
        "attack": "🗡️ Атака",
        "shield": "🛡️ Защита",
        "pistol": "🔫 Пистолет",
        "heal": "💚 Лечение",
    }
    move1_text = move_names.get(move1, "?")
    move2_text = move_names.get(move2, "?")

    ch_data = get_user(ch_id)
    op_data = get_user(op_id)
    ch_name = (ch_data[1] and f"@{ch_data[1]}") or ch_data[2] or f"ID:{ch_id}" if ch_data else "?"
    op_name = (op_data[1] and f"@{op_data[1]}") or op_data[2] or f"ID:{op_id}" if op_data else "?"

    damage_to_1 = 0
    damage_to_2 = 0
    heal_1 = 0
    heal_2 = 0
    log_lines = []

    if move1 == "attack":
        if move2 == "attack":
            damage_to_1 += 1
            damage_to_2 += 1
            log_lines.append("⚔️ Оба атаковали — оба получают урон!")
        elif move2 == "shield":
            log_lines.append(f"🛡️ {op_name} заблокировал атаку")
        elif move2 == "pistol":
            damage_to_1 += 1
            log_lines.append(f"🔫 {op_name} выстрелил — атака {ch_name} не дошла")
        elif move2 == "heal":
            damage_to_2 += 1
            heal_2 += 1
            log_lines.append(f"⚔️ {ch_name} атаковал, 💚 {op_name} лечился")

    elif move1 == "shield":
        if move2 == "attack":
            log_lines.append(f"🛡️ {ch_name} заблокировал атаку")
        elif move2 == "pistol":
            damage_to_1 += 1
            log_lines.append(f"🔫 {op_name} пробил защиту!")
        elif move2 == "shield":
            log_lines.append("🛡️ Оба защищаются — ничего не происходит")
        elif move2 == "heal":
            heal_2 += 1
            log_lines.append(f"🛡️ {ch_name} защищается, 💚 {op_name} лечился")

    elif move1 == "pistol":
        if move2 == "attack":
            damage_to_2 += 1
            log_lines.append(f"🔫 {ch_name} выстрелил — урон!")
        elif move2 == "shield":
            damage_to_2 += 1
            log_lines.append(f"🔫 {ch_name} пробил защиту!")
        elif move2 == "pistol":
            damage_to_1 += 1
            damage_to_2 += 1
            log_lines.append("🔫 Оба выстрелили — оба ранены!")
        elif move2 == "heal":
            damage_to_2 += 1
            heal_2 += 1
            log_lines.append(f"🔫 {ch_name} выстрелил, 💚 {op_name} лечился")

    elif move1 == "heal":
        heal_1 += 1
        if move2 == "attack":
            damage_to_1 += 1
            log_lines.append(f"💚 {ch_name} лечился, но ⚔️ {op_name} атаковал")
        elif move2 == "shield":
            log_lines.append(f"💚 {ch_name} лечился, 🛡️ {op_name} защищался")
        elif move2 == "pistol":
            damage_to_1 += 1
            log_lines.append(f"💚 {ch_name} лечился, но 🔫 {op_name} выстрелил")
        elif move2 == "heal":
            log_lines.append("💚 Оба лечились")

    new_hp1 = max(0, min(3, hp1 - damage_to_1 + heal_1))
    new_hp2 = max(0, min(3, hp2 - damage_to_2 + heal_2))

    duel_update(duel_id, hp1=new_hp1, hp2=new_hp2, move1=None, move2=None)

    someone_died = new_hp1 <= 0 or new_hp2 <= 0

    result_text = (
        f"⚔️ <b>РАУНД</b>\n\n"
        f"<b>{ch_name}</b>: {move1_text}\n"
        f"<b>{op_name}</b>: {move2_text}\n\n"
        f"└─ " + "\n└─ ".join(log_lines) + "\n\n"
        f"❤️ {ch_name}: {new_hp1}/3\n"
        f"❤️ {op_name}: {new_hp2}/3"
    )

    try:
        await bot.edit_message_text(
            chat_id=chat_id, message_id=msg_id, text=result_text, parse_mode="HTML"
        )
    except Exception:
        pass

    await asyncio.sleep(2)

    if not someone_died:
        duel_update(duel_id, turn=0)
        await _render_duel(chat_id, duel_id, edit=True)
        return

    if new_hp1 <= 0 and new_hp2 <= 0:
        await _finish_duel_draw(chat_id, duel_id, ch_id, op_id, ch_name, op_name, new_hp1, new_hp2)
    elif new_hp1 <= 0:
        await _finish_duel_win(chat_id, duel_id, ch_id, op_id, ch_name, op_name, op_id, new_hp1, new_hp2)
    else:
        await _finish_duel_win(chat_id, duel_id, ch_id, op_id, ch_name, op_name, ch_id, new_hp1, new_hp2)


async def _finish_duel_win(chat_id, duel_id, ch_id, op_id, ch_name, op_name, winner, hp1, hp2):
    duel = duel_get(duel_id)
    if not duel:
        return

    bet = duel[3]
    msg_id = duel[10]

    add_balance(winner, bet * 2)

    loser = op_id if winner == ch_id else ch_id
    winner_name = ch_name if winner == ch_id else op_name
    loser_name = op_name if winner == ch_id else ch_name
    winner_hp = hp1 if winner == ch_id else hp2

    log_transaction(loser, winner, bet, "duel_win")

    text = (
        f"🏆 <b>ПОБЕДА!</b>\n\n"
        f"<b>{winner_name}</b> — победитель! 🎉\n"
        f"❤️ Осталось жизней: {winner_hp}/3\n\n"
        f"<b>{loser_name}</b> — повержен ☠️\n"
        f"❤️ Жизней: 0/3\n\n"
        f"💰 Ставка: {bet} msg\n"
        f"💰 Выигрыш: <b>+{bet * 2}</b> msg\n\n"
        f"<i>Дуэль завершена</i>"
    )

    try:
        await bot.edit_message_text(chat_id=chat_id, message_id=msg_id, text=text, parse_mode="HTML")
    except Exception:
        await bot.send_message(chat_id, text, parse_mode="HTML")

    try:
        await bot.send_message(
            loser,
            f"⚔️ <b>Ты проиграл дуэль!</b>\n\n"
            f"└─ Победитель: {winner_name}\n"
            f"└─ Потеряно: {bet} msg"
        )
    except Exception:
        pass

    duel_delete(duel_id)


async def _finish_duel_draw(chat_id, duel_id, ch_id, op_id, ch_name, op_name, hp1, hp2):
    duel = duel_get(duel_id)
    if not duel:
        return

    bet = duel[3]
    msg_id = duel[10]

    add_balance(ch_id, bet)
    add_balance(op_id, bet)

    text = (
        f"🤝 <b>НИЧЬЯ!</b>\n\n"
        f"<b>{ch_name}</b> ❤️ 0/3\n"
        f"<b>{op_name}</b> ❤️ 0/3\n\n"
        f"💰 Ставки возвращены: по {bet} msg\n\n"
        f"<i>Дуэль завершена</i>"
    )

    try:
        await bot.edit_message_text(chat_id=chat_id, message_id=msg_id, text=text, parse_mode="HTML")
    except Exception:
        await bot.send_message(chat_id, text, parse_mode="HTML")

    for uid, name in ((ch_id, ch_name), (op_id, op_name)):
        try:
            await bot.send_message(
                uid,
                f"🤝 <b>Дуэль завершена ничьей</b>\n\n"
                f"└─ Соперник: {name}\n"
                f"└─ Ставка возвращена: {bet} msg"
            )
        except Exception:
            pass

    duel_delete(duel_id)


# =========================================================
#  МОДЕРАЦИЯ: /warn, /unwarn, /warnlist
# =========================================================

@dp.message(Command("warn"))
async def cmd_warn(message: Message):
    log_cmd("⚠️ /warn", message)
    actor_id = message.from_user.id

    if not is_moder(actor_id) and not is_senior(actor_id):
        await message.answer("⛔ Только для модераторов")
        return

    lines = message.text.split("\n", 1)
    first_line = lines[0].strip()
    reason = lines[1].strip() if len(lines) > 1 else "не указана"

    target_id = None
    target_name = None

    if message.reply_to_message:
        target = message.reply_to_message.from_user
        if target.is_bot:
            await message.answer("❌ Нельзя предупредить бота")
            return
        target_id = target.id
        target_name = target.full_name
        ensure_user(target)
    else:
        args = first_line.split()[1:]
        if not args or not args[0].startswith("@"):
            await message.answer(
                "❌ Использование:\n"
                "└─ ответь на сообщение: /warn\n"
                "└─ или /warn @username\n"
                "На новой строке — причина",
                parse_mode="HTML"
            )
            return
        target_id, target_name = find_user_id(message, args[0])
        if target_id is None:
            await message.answer("❌ Пользователь не найден")
            return
        ensure_user_by_id(target_id)

    if target_id == actor_id:
        await message.answer("❌ Нельзя предупредить себя")
        return
    if target_id in OWNER_IDS:
        await message.answer("❌ Нельзя предупредить владельца")
        return

    can, reason_err = can_warn(actor_id, target_id)
    if not can:
        await message.answer(reason_err)
        return

    if get_active_ban(target_id):
        await message.answer(
            f"⚠️ <b>{target_name} уже забанен</b>\n└─ Сначала /unban",
            parse_mode="HTML"
        )
        return

    current_count = get_warn_count(target_id)
    if current_count >= WARN_LIMIT:
        await message.answer(
            f"⚠️ <b>{target_name} уже имеет {WARN_LIMIT} warn</b>\n"
            f"└─ Проверь /warnlist",
            parse_mode="HTML"
        )
        return

    add_warn(target_id, reason, actor_id)
    new_count = current_count + 1

    await message.answer(
        f"⚠️ <b>Предупреждение выдано</b>\n"
        f"└─ Кому: {target_name} ({target_id})\n"
        f"└─ Причина: {reason}\n"
        f"└─ Всего warn: {new_count}/{WARN_LIMIT}",
        parse_mode="HTML"
    )

    try:
        await bot.send_message(
            target_id,
            f"⚠️ <b>Тебе выдано предупреждение ({new_count}/{WARN_LIMIT})</b>\n\n"
            f"└─ Причина: {reason}\n\n"
            f"💡 {WARN_LIMIT} предупреждения = бан на {WARN_BAN_DAYS} дней"
        )
    except Exception:
        pass

    if new_count >= WARN_LIMIT:
        banned_until = add_ban(target_id, f"Авто-бан: {WARN_LIMIT} предупреждения", WARN_BAN_DAYS, actor_id)
        clear_warns(target_id)
        log_transaction(actor_id, target_id, 0, "auto_ban")

        try:
            until_dt = datetime.fromisoformat(banned_until)
            await bot.send_message(
                target_id,
                f"🚫 <b>Ты забанен!</b>\n\n"
                f"└─ Причина: набрано {WARN_LIMIT} предупреждения\n"
                f"└─ Срок: {WARN_BAN_DAYS} дней\n"
                f"└─ До: {until_dt.strftime('%d.%m.%Y %H:%M')}"
            )
        except Exception:
            pass

        await message.answer(
            f"🚫 <b>Авто-бан сработал!</b>\n"
            f"└─ {target_name} забанен на {WARN_BAN_DAYS} дней\n"
            f"└─ Warn сброшены",
            parse_mode="HTML"
        )


@dp.message(Command("unwarn"))
async def cmd_unwarn(message: Message):
    log_cmd("✅ /unwarn", message)
    actor_id = message.from_user.id

    if not is_moder(actor_id) and not is_senior(actor_id):
        await message.answer("⛔ Только для модераторов")
        return

    args = message.text.split()[1:]
    target_id = None
    target_name = None
    warn_num = None

    if message.reply_to_message:
        target = message.reply_to_message.from_user
        target_id = target.id
        target_name = target.full_name
        ensure_user(target)
        if args:
            try:
                warn_num = int(args[0])
            except ValueError:
                await message.answer(f"😅 «{args[0]}» — это не число\n└─ Пример: /unwarn 1", parse_mode="HTML")
                return
    else:
        if len(args) < 2 or not args[0].startswith("@"):
            await message.answer(
                "❌ Использование:\n"
                "└─ ответь на сообщение: /unwarn [номер]\n"
                "└─ или /unwarn @username [номер]\n\n"
                "Номер warn можно узнать в /warnlist",
                parse_mode="HTML"
            )
            return

        target_id, target_name = find_user_id(message, args[0])
        if target_id is None:
            await message.answer("❌ Пользователь не найден")
            return

        try:
            warn_num = int(args[1])
        except ValueError:
            await message.answer(f"😅 «{args[1]}» — это не число\n└─ Пример: /unwarn @user 1", parse_mode="HTML")
            return

    if warn_num is None:
        await message.answer("❌ Укажи номер warn")
        return

    if not is_owner(actor_id):
        can, reason_err = can_warn(actor_id, target_id)
        if not can:
            await message.answer(reason_err)
            return

    warns = get_user_warns(target_id)
    if not warns:
        await message.answer(f"ℹ️ У {target_name} нет предупреждений")
        return

    if warn_num < 1 or warn_num > len(warns):
        await message.answer(
            f"❌ У {target_name} только {len(warns)} warn\n"
            f"└─ Номер должен быть от 1 до {len(warns)}"
        )
        return

    warn = warns[warn_num - 1]
    warn_id = warn[0]
    warn_reason = warn[1]

    remove_warn(warn_id)

    await message.answer(
        f"✅ <b>Предупреждение снято</b>\n"
        f"└─ Кому: {target_name}\n"
        f"└─ Warn #{warn_num}: {warn_reason}\n"
        f"└─ Осталось: {len(warns) - 1}/{WARN_LIMIT}",
        parse_mode="HTML"
    )

    try:
        await bot.send_message(
            target_id,
            f"✅ <b>С тебя снято предупреждение</b>\n└─ Было: {warn_reason}"
        )
    except Exception:
        pass


@dp.message(Command("warnlist"))
async def cmd_warnlist(message: Message):
    log_cmd("📜 /warnlist", message)
    actor_id = message.from_user.id

    if not is_moder(actor_id) and not is_senior(actor_id):
        await message.answer("⛔ Только для модераторов")
        return

    all_warned = get_all_warned()
    if not all_warned:
        await message.answer("📭 <b>Нет юзеров с предупреждениями</b>", parse_mode="HTML")
        return

    lines = ["⚠️ <b>Юзеры с предупреждениями:</b>\n"]

    for user_id, count, warns in all_warned[:15]:
        data = get_user(user_id)
        name = "?"
        if data:
            uname = data[1]
            fname = data[2]
            name = f"@{uname}" if uname else (fname or f"ID:{user_id}")

        lines.append(f"\n<b>{name}</b> — {count} warn")

        for i, warn in enumerate(warns, start=1):
            warn_id, reason, warned_by, warned_at = warn
            try:
                dt = datetime.fromisoformat(warned_at)
                date_str = dt.strftime("%d.%m %H:%M")
            except ValueError:
                date_str = "—"

            wb_data = get_user(warned_by)
            wb_name = "?"
            if wb_data:
                wb_uname = wb_data[1]
                wb_name = f"@{wb_uname}" if wb_uname else wb_data[2]

            lines.append(f"└─ <b>#{i}</b> {reason}")
            lines.append(f"   {wb_name} | {date_str}")

    if len(all_warned) > 15:
        lines.append(f"\n...и ещё {len(all_warned) - 15}")

    text = "\n".join(lines)
    if len(text) > 4000:
        text = text[:3900] + "\n...обрезано"

    await message.answer(text, parse_mode="HTML")


# =========================================================
#  АДМИН-КОМАНДЫ (короткие)
# =========================================================

@dp.message(Command("anonlog"))
async def cmd_anonlog(message: Message):
    log_cmd("📜 /anonlog", message)
    actor_id = message.from_user.id
    if not is_moder(actor_id) and not is_senior(actor_id):
        await message.answer("⛔ Только для модераторов")
        return

    args = message.text.split()[1:]
    to_id = None
    to_name = None
    if message.reply_to_message:
        to_id = message.reply_to_message.from_user.id
        to_name = message.reply_to_message.from_user.full_name
    elif args and args[0].startswith("@"):
        to_id, to_name = find_user_id(message, args[0])
        if to_id is None:
            await message.answer("❌ Пользователь не найден")
            return

    rows = get_anon_logs(limit=20, to_id=to_id)
    if not rows:
        await message.answer(f"📭 Анонимок для {to_name} нет" if to_name else "📭 Анонимок нет")
        return

    header = "📜 <b>Последние анонимки</b>"
    if to_name:
        header += f" → {to_name}"
    header += "\n"

    lines = [header]
    for from_id, t_id, text, created_at in rows:
        try:
            dt = datetime.fromisoformat(created_at)
            date_str = dt.strftime("%d.%m %H:%M")
        except ValueError:
            date_str = "—"
        from_data = get_user(from_id)
        to_data = get_user(t_id)
        from_name = from_data[2] if from_data else f"ID:{from_id}"
        to_name_str = to_data[2] if to_data else f"ID:{t_id}"
        short_text = text if len(text) <= 40 else text[:40] + "..."
        lines.append(f"\n<b>{from_name}</b> → <b>{to_name_str}</b> | {date_str}\n└─ {short_text}")

    await message.answer("\n".join(lines), parse_mode="HTML")


@dp.message(Command("anonmute"))
async def cmd_anonmute(message: Message):
    log_cmd("🚫 /anonmute", message)
    actor_id = message.from_user.id
    if not is_moder(actor_id) and not is_senior(actor_id):
        await message.answer("⛔ Только для модераторов")
        return

    lines = message.text.split("\n", 1)
    first_line = lines[0].strip()
    reason = lines[1].strip() if len(lines) > 1 else "не указана"
    parts = first_line.split()[1:]

    if not parts:
        await message.answer("❌ Формат:\n/anonmute @username 7\nпричина\n\n0 = навсегда", parse_mode="HTML")
        return

    target_arg = None
    days_str = None
    if parts[0].startswith("@"):
        target_arg = parts[0]
        if len(parts) < 2:
            await message.answer("❌ Укажи срок (дней), 0 = навсегда")
            return
        days_str = parts[1]
    else:
        days_str = parts[0]

    try:
        days = int(days_str)
        if days < 0:
            raise ValueError
    except ValueError:
        await message.answer("❌ Срок должен быть числом ≥ 0")
        return

    target_id, target_name = find_user_id(message, target_arg)
    if target_id is None:
        await message.answer("❌ Пользователь не найден")
        return
    if target_id in OWNER_IDS:
        await message.answer("❌ Нельзя мутить владельца")
        return

    if not is_owner(actor_id):
        can, reason_err = can_touch(actor_id, target_id)
        if not can:
            await message.answer(reason_err)
            return

    if get_active_anon_mute(target_id):
        await message.answer(f"⚠️ {target_name} уже в муте анонимок")
        return

    ensure_user_by_id(target_id)
    muted_until = add_anon_mute(target_id, reason, days, actor_id)

    if days == 0:
        until_text = "навсегда"
        notify_text = f"🚫 Тебе запрещено отправлять анонимки\n└─ Причина: {reason}\n└─ Срок: навсегда"
    else:
        until_dt = datetime.fromisoformat(muted_until)
        until_text = f"{days} дн. (до {until_dt.strftime('%d.%m.%Y %H:%M')})"
        notify_text = f"🚫 Тебе запрещено отправлять анонимки\n└─ Причина: {reason}\n└─ Срок: {days} дн."

    await message.answer(
        f"🚫 <b>Мут анонимок выдан</b>\n"
        f"└─ Кому: {target_name} ({target_id})\n"
        f"└─ Причина: {reason}\n"
        f"└─ Срок: {until_text}",
        parse_mode="HTML"
    )

    try:
        await bot.send_message(target_id, notify_text)
    except Exception:
        pass


@dp.message(Command("anonunmute"))
async def cmd_anonunmute(message: Message):
    log_cmd("✅ /anonunmute", message)
    actor_id = message.from_user.id
    if not is_moder(actor_id) and not is_senior(actor_id):
        await message.answer("⛔ Только для модераторов")
        return

    args = message.text.split()[1:]
    target_arg = args[0] if args else None
    target_id, target_name = find_user_id(message, target_arg)
    if target_id is None:
        await message.answer("❌ Укажи @username или ответь на сообщение")
        return

    if not get_active_anon_mute(target_id):
        await message.answer(f"ℹ️ {target_name} не в муте анонимок")
        return

    remove_anon_mute(target_id)
    await message.answer(
        f"✅ <b>Мут анонимок снят</b>\n└─ Кому: {target_name} ({target_id})",
        parse_mode="HTML"
    )

    try:
        await bot.send_message(target_id, "✅ Тебе снова разрешено отправлять анонимки")
    except Exception:
        pass


@dp.message(Command("setver"))
async def cmd_setver(message: Message):
    log_cmd("⚙️ /setver", message)
    if not is_owner(message.from_user.id):
        await message.answer("⛔ Команда только для владельца")
        return

    lines = message.text.split("\n", 1)
    first_line = lines[0].strip()
    body = lines[1].strip() if len(lines) > 1 else ""

    parts = first_line.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer(
            "❌ Формат:\n"
            "<code>/setver [версия]\n"
            "[changelog]</code>\n\n"
            "Разделить «что нового» и «скоро» можно через <code>=======</code>",
            parse_mode="HTML"
        )
        return

    version = parts[1].strip()
    if len(version) > 20:
        await message.answer("❌ Версия слишком длинная (макс. 20 символов)")
        return

    SEPARATOR = "======="
    if SEPARATOR in body:
        changelog, soon = body.split(SEPARATOR, 1)
        changelog = changelog.strip()
        soon = soon.strip()
    else:
        changelog = body.strip()
        soon = None

    if len(changelog) > 500:
        await message.answer("❌ Changelog слишком длинный (макс. 500)")
        return
    if soon and len(soon) > 800:
        await message.answer("❌ Блок «Скоро» слишком длинный (макс. 800)")
        return

    set_bot_info("version", version)
    set_bot_info("changelog", changelog if changelog else "нет изменений")
    if soon:
        set_bot_soon(soon)
    else:
        clear_bot_soon()

    preview = (
        f"📌 <b>Версия — {version}</b>\n\n"
        f"<b>Что нового:</b>\n"
        f"{changelog if changelog else 'нет изменений'}"
    )
    if soon:
        preview += f"\n\n━━━━━━━━━━━━━━━\n\n{soon}"

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📢 Отправить всем", callback_data="broadcast_yes"),
            InlineKeyboardButton(text="❌ Не отправлять", callback_data="broadcast_no"),
        ]
    ])

    await message.answer(
        f"✅ <b>Версия обновлена!</b>\n\n"
        f"<b>Превью:</b>\n\n"
        f"{preview}\n\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"📢 <b>Разослать уведомление всем юзерам?</b>",
        parse_mode="HTML",
        reply_markup=kb
    )


@dp.callback_query(lambda c: c.data in ("broadcast_yes", "broadcast_no"))
async def cb_broadcast(callback: CallbackQuery):
    if not is_main_owner(callback.from_user.id):
        await callback.answer("⛔ Только для главного владельца", show_alert=True)
        return

    action = callback.data

    if action == "broadcast_no":
        try:
            await callback.message.edit_reply_markup(reply_markup=None)
        except Exception:
            pass
        await callback.answer("❌ Рассылка отменена")
        return

    await callback.answer("📢 Начинаю рассылку...")
    try:
        await callback.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass

    version = get_bot_info("version") or "?"
    changelog = get_bot_info("changelog") or "нет изменений"
    soon = get_bot_soon()

    text = f"📌 <b>Бот обновлён до версии {version}!</b>\n\n<b>Что нового:</b>\n{changelog}"
    if soon:
        text += f"\n\n━━━━━━━━━━━━━━━\n\n{soon}"

    user_ids = get_all_user_ids()
    if not user_ids:
        await callback.message.answer("⚠️ В БД нет юзеров")
        return

    status_msg = await callback.message.answer(
        f"📢 <b>Рассылка начата</b>\n"
        f"└─ Всего юзеров: {len(user_ids)}\n"
        f"└─ Скорость: 20 msg/сек\n"
        f"└─ Ожидаемое время: ~{len(user_ids) // 20 + 1} сек",
        parse_mode="HTML"
    )

    sent = 0
    failed = 0

    for uid in user_ids:
        try:
            await bot.send_message(uid, text, parse_mode="HTML")
            sent += 1
        except Exception as e:
            failed += 1
            print(f"[BROADCAST] Ошибка для {uid}: {e}")
        # ✅ Ускорил с 1 сек до 0.05 сек (20/сек)
        await asyncio.sleep(0.05)

    await status_msg.edit_text(
        f"✅ <b>Рассылка завершена!</b>\n\n"
        f"└─ 📤 Отправлено: <b>{sent}</b>\n"
        f"└─ ❌ Ошибок: <b>{failed}</b>\n"
        f"└─ 👥 Всего: {len(user_ids)}",
        parse_mode="HTML"
    )


# =========================================================
#  БАНЫ
# =========================================================

@dp.message(Command("ban"))
async def cmd_ban(message: Message):
    log_cmd("🚫 /ban", message)
    actor_id = message.from_user.id
    if not is_senior(actor_id):
        await message.answer("⛔ Только для старших модераторов")
        return

    lines = message.text.split("\n", 1)
    first_line = lines[0].strip()
    reason = lines[1].strip() if len(lines) > 1 else "не указана"
    parts = first_line.split()[1:]

    if not parts:
        await message.answer(
            "❌ Формат:\n/ban @username 7\nпричина\n\n"
            "Или ответь на сообщение:\n/ban 7\nпричина\n\n0 = навсегда",
            parse_mode="HTML"
        )
        return

    target_arg = None
    days_str = None
    if parts[0].startswith("@"):
        target_arg = parts[0]
        if len(parts) < 2:
            await message.answer("❌ Укажи срок (дней), 0 = навсегда")
            return
        days_str = parts[1]
    else:
        days_str = parts[0]

    try:
        days = int(days_str)
        if days < 0:
            raise ValueError
    except ValueError:
        await message.answer("❌ Срок должен быть числом ≥ 0")
        return

    target_id, target_name = find_user_id(message, target_arg)
    if target_id is None:
        await message.answer(
            "❌ Пользователь не найден.\n"
            "Он должен хотя бы раз написать боту, или ответь на его сообщение."
        )
        return

    if not is_owner(actor_id):
        can, reason2 = can_touch(actor_id, target_id)
        if not can:
            await message.answer(reason2)
            return

    if get_active_ban(target_id):
        await message.answer(f"⚠️ {target_name} уже забанен. Сначала /unban.")
        return

    ensure_user_by_id(target_id)
    banned_until = add_ban(target_id, reason, days, actor_id)

    if days == 0:
        until_text = "навсегда"
        notify_text = f"🚫 Ты забанен\n└─ Причина: {reason}\n└─ Срок: навсегда"
    else:
        until_dt = datetime.fromisoformat(banned_until)
        until_text = f"{days} дн. (до {until_dt.strftime('%d.%m.%Y %H:%M')})"
        notify_text = f"🚫 Ты забанен\n└─ Причина: {reason}\n└─ Срок: {days} дн."

    await message.answer(
        f"🚫 <b>Забанен</b>\n"
        f"└─ Кому: {target_name} ({target_id})\n"
        f"└─ Причина: {reason}\n"
        f"└─ Срок: {until_text}",
        parse_mode="HTML"
    )

    try:
        await bot.send_message(target_id, notify_text)
    except Exception:
        pass


@dp.message(Command("unban"))
async def cmd_unban(message: Message):
    log_cmd("✅ /unban", message)
    actor_id = message.from_user.id
    if not is_senior(actor_id):
        await message.answer("⛔ Только для старших модераторов")
        return

    args = message.text.split()[1:]
    target_arg = args[0] if args else None
    target_id, target_name = find_user_id(message, target_arg)
    if target_id is None:
        await message.answer("❌ Укажи @username или ответь на сообщение")
        return

    if not is_owner(actor_id):
        can, reason = can_touch(actor_id, target_id)
        if not can:
            await message.answer(reason)
            return

    if not get_active_ban(target_id):
        await message.answer(f"ℹ️ {target_name} не забанен")
        return

    remove_ban(target_id)
    log_transaction(actor_id, target_id, 0, "admin_unban")

    await message.answer(
        f"✅ <b>Разбанен</b>\n└─ Кому: {target_name} ({target_id})",
        parse_mode="HTML"
    )

    try:
        await bot.send_message(target_id, "✅ Ты разбанен. Доступ восстановлен.")
    except Exception:
        pass


@dp.message(Command("banlist"))
async def cmd_banlist(message: Message):
    log_cmd("📜 /banlist", message)
    actor_id = message.from_user.id
    if not is_senior(actor_id):
        await message.answer("⛔ Только для старших модераторов")
        return

    rows = list_bans()
    if not rows:
        await message.answer("📭 Список банов пуст")
        return

    lines = ["🚫 <b>Забаненные:</b>\n"]
    active_count = 0

    for user_id, reason, banned_until, banned_at, uname, fname in rows:
        if banned_until is None:
            status = "навсегда"
            active = True
        else:
            try:
                until_dt = datetime.fromisoformat(banned_until)
                if until_dt > datetime.now():
                    status = f"до {until_dt.strftime('%d.%m.%Y %H:%M')}"
                    active = True
                else:
                    status = "истёк"
                    active = False
            except ValueError:
                status = "—"
                active = False

        if not active:
            continue

        active_count += 1
        name = f"@{uname}" if uname else (fname or f"ID: {user_id}")
        lines.append(f"• {name} — {reason} | {status}")

    if active_count == 0:
        await message.answer("📭 Активных банов нет")
        return

    await message.answer("\n".join(lines), parse_mode="HTML")


# =========================================================
#  ЭКОНОМИКА: /addmsg, /remmsg, /setmsg, /givevip, /remvip, /stats
# =========================================================

@dp.message(Command("addmsg"))
async def cmd_addmsg(message: Message):
    log_cmd("💰 /addmsg", message)
    if not is_econom(message.from_user.id):
        await message.answer("⛔ Команда только для экономистов")
        return

    args = message.text.split()[1:]
    target_id, target_name, amount = _parse_user_amount(message, args)

    if target_id is None or amount is None:
        await message.answer("❌ Укажи @username или ответь на сообщение, и сумму")
        return

    if not is_owner(message.from_user.id):
        can, reason = can_touch(message.from_user.id, target_id)
        if not can:
            await message.answer(reason)
            return

    ensure_user_by_id(target_id)
    new_balance = add_balance(target_id, amount)
    log_transaction(message.from_user.id, target_id, amount, "admin_add")

    await message.answer(
        f"✅ <b>Начислено</b>\n"
        f"└─ Кому: {target_name}\n"
        f"└─ Сумма: +{amount} msg\n"
        f"└─ Новый баланс: {new_balance} msg",
        parse_mode="HTML"
    )


@dp.message(Command("remmsg"))
async def cmd_remmsg(message: Message):
    log_cmd("💸 /remmsg", message)
    if not is_econom(message.from_user.id):
        await message.answer("⛔ Команда только для экономистов")
        return

    args = message.text.split()[1:]
    target_id, target_name, amount = _parse_user_amount(message, args)

    if target_id is None or amount is None:
        await message.answer("❌ Укажи @username или ответь на сообщение, и сумму")
        return

    if not is_owner(message.from_user.id):
        can, reason = can_touch(message.from_user.id, target_id)
        if not can:
            await message.answer(reason)
            return

    ensure_user_by_id(target_id)
    new_balance = add_balance(target_id, -amount)
    log_transaction(message.from_user.id, target_id, -amount, "admin_rem")

    await message.answer(
        f"✅ <b>Списано</b>\n"
        f"└─ Кому: {target_name}\n"
        f"└─ Сумма: -{amount} msg\n"
        f"└─ Новый баланс: {new_balance} msg",
        parse_mode="HTML"
    )


@dp.message(Command("setmsg"))
async def cmd_setmsg(message: Message):
    log_cmd("⚙️ /setmsg", message)
    if not is_econom(message.from_user.id):
        await message.answer("⛔ Команда только для экономистов")
        return

    args = message.text.split()[1:]
    target_id, target_name, amount = _parse_user_amount(message, args)

    if target_id is None or amount is None:
        await message.answer("❌ Укажи @username или ответь на сообщение, и сумму")
        return

    if not is_owner(message.from_user.id):
        can, reason = can_touch(message.from_user.id, target_id)
        if not can:
            await message.answer(reason)
            return

    ensure_user_by_id(target_id)
    set_balance(target_id, amount)
    log_transaction(message.from_user.id, target_id, amount, "admin_set")

    await message.answer(
        f"✅ <b>Баланс установлен</b>\n"
        f"└─ Кому: {target_name}\n"
        f"└─ Новый баланс: {amount} msg",
        parse_mode="HTML"
    )


@dp.message(Command("givevip"))
async def cmd_givevip(message: Message):
    log_cmd("👑 /givevip", message)
    if not is_econom(message.from_user.id):
        await message.answer("⛔ Команда только для экономистов")
        return

    args = message.text.split()[1:]

    if message.reply_to_message:
        if not args:
            await message.answer("❌ Формат (reply): /givevip [недели]")
            return
        weeks_str = args[0]
        target = message.reply_to_message.from_user
        if target.is_bot:
            await message.answer("❌ Нельзя выдать VIP боту")
            return
        target_id = target.id
        target_name = target.full_name
        ensure_user(target)
    else:
        if len(args) < 2:
            await message.answer(
                "❌ Использование:\n"
                "└─ ответь на сообщение: /givevip [недели]\n"
                "└─ или /givevip @username [недели]"
            )
            return
        target_id, target_name = find_user_id(message, args[0])
        if target_id is None:
            await message.answer("❌ Пользователь не найден")
            return
        ensure_user_by_id(target_id)
        weeks_str = args[1]

    if not is_owner(message.from_user.id):
        can, reason = can_touch(message.from_user.id, target_id)
        if not can:
            await message.answer(reason)
            return

    try:
        weeks = int(weeks_str)
        if weeks <= 0:
            raise ValueError
    except ValueError:
        await message.answer("❌ Количество недель должно быть положительным числом")
        return

    result = give_vip(target_id, weeks)
    if result is None:
        await message.answer("❌ Пользователь не найден в БД")
        return

    until_dt = datetime.fromisoformat(result)
    log_transaction(message.from_user.id, target_id, weeks, "admin_givevip")

    await message.answer(
        f"👑 <b>VIP выдан</b>\n"
        f"└─ Кому: {target_name} ({target_id})\n"
        f"└─ Срок: {weeks} нед.\n"
        f"└─ Действует до: {until_dt.strftime('%d.%m.%Y %H:%M')}",
        parse_mode="HTML"
    )

    try:
        await bot.send_message(
            target_id,
            f"👑 <b>Тебе выдан VIP!</b>\n"
            f"└─ На {weeks} нед.\n"
            f"└─ Действует до: {until_dt.strftime('%d.%m.%Y %H:%M')}"
        )
    except Exception:
        pass


@dp.message(Command("remvip"))
async def cmd_remvip(message: Message):
    log_cmd("🚫 /remvip", message)
    if not is_econom(message.from_user.id):
        await message.answer("⛔ Команда только для экономистов")
        return

    args = message.text.split()[1:]

    if message.reply_to_message:
        target = message.reply_to_message.from_user
        if target.is_bot:
            await message.answer("❌ Нельзя снять VIP у бота")
            return
        target_id = target.id
        target_name = target.full_name
        ensure_user(target)
    else:
        if not args or not args[0].startswith("@"):
            await message.answer(
                "❌ Использование:\n"
                "└─ ответь на сообщение: /remvip\n"
                "└─ или /remvip @username"
            )
            return
        target_id, target_name = find_user_id(message, args[0])
        if target_id is None:
            await message.answer("❌ Пользователь не найден")
            return

    if not is_owner(message.from_user.id):
        can, reason = can_touch(message.from_user.id, target_id)
        if not can:
            await message.answer(reason)
            return

    if not is_vip_active(target_id):
        await message.answer(f"ℹ️ У {target_name} нет активного VIP")
        return

    remove_vip(target_id)
    log_transaction(message.from_user.id, target_id, 0, "admin_remvip")

    await message.answer(
        f"🚫 <b>VIP снят</b>\n└─ Кому: {target_name} ({target_id})",
        parse_mode="HTML"
    )

    try:
        await bot.send_message(target_id, "🚫 <b>Твой VIP снят</b>")
    except Exception:
        pass


@dp.message(Command("stats"))
async def cmd_stats(message: Message):
    log_cmd("📊 /stats", message)
    if not is_econom(message.from_user.id):
        await message.answer("⛔ Команда только для экономистов")
        return

    stats = get_bot_stats()

    await message.answer(
        f"📊 <b>Статистика бота</b>\n\n"
        f"👥 <b>Юзеры:</b>\n"
        f"└─ Всего: {stats['total_users']}\n"
        f"└─ С VIP: {stats['vip_users']}\n"
        f"└─ Забанено: {stats['banned_users']}\n\n"
        f"💰 <b>Экономика:</b>\n"
        f"└─ Всего msg: {stats['total_msg']:,}\n"
        f"└─ В банках: {stats['bank_msg']:,}\n"
        f"└─ В кошельках: {stats['wallet_msg']:,}\n"
        f"└─ Средний баланс: {stats['avg_balance']:,}\n\n"
        f"🏆 <b>Топ-1:</b> {stats['top1_name']} — {stats['top1_balance']:,} msg",
        parse_mode="HTML"
    )


# =========================================================
#  ДОСТУПЫ
# =========================================================

CATEGORIES = {
    "econom": {
        "title": "💰 <b>Экономика</b>",
        "text": (
            "└─ /addmsg [@user] [сумма]\n"
            "└─ /remmsg [@user] [сумма]\n"
            "└─ /setmsg [@user] [сумма]\n"
            "└─ /givevip [@user] [недели]\n"
            "└─ /remvip [@user]\n"
            "└─ /stats"
        ),
    },
    "moder": {
        "title": "⚠️ <b>Модерация</b>",
        "text": (
            "<b>Варны:</b>\n"
            "└─ /warn [@user] + причина\n"
            "└─ /unwarn [@user] [номер]\n"
            "└─ /warnlist\n\n"
            "<b>Баны:</b>\n"
            "└─ /ban [@user] [дней] + причина\n"
            "└─ /unban [@user]\n"
            "└─ /banlist"
        ),
    },
    "anon": {
        "title": "💌 <b>Анонимки</b>",
        "text": (
            "└─ /anonlog [@user]\n"
            "└─ /anonmute [@user] [дней] + причина\n"
            "└─ /anonunmute [@user]"
        ),
    },
    "access": {
        "title": "🔑 <b>Доступ</b>",
        "text": (
            "└─ /setaccess [@user] [уровни]\n"
            "└─ /accesslist\n\n"
            "<i>Уровни: econom, moder, senior</i>"
        ),
    },
    "bot": {
        "title": "⚙️ <b>Бот</b>",
        "text": (
            "└─ /setver [версия] + changelog\n"
            "└─ /stats"
        ),
    },
}


def kb_main(role: str) -> InlineKeyboardMarkup:
    allow = {
        "owner":  ["econom", "moder", "anon", "access", "bot"],
        "senior": ["moder", "anon", "access"],
        "moder":  ["moder", "anon"],
        "econom": ["econom"],
    }[role]

    labels = {
        "econom": "💰 Экономика",
        "moder":  "⚠️ Модерация",
        "anon":   "💌 Анонимки",
        "access": "🔑 Доступ",
        "bot":    "⚙️ Бот",
    }

    rows, row = [], []
    for key in allow:
        row.append(InlineKeyboardButton(text=labels[key], callback_data=f"own:cat:{key}"))
        if len(row) == 2:
            rows.append(row)
            row = []
    if row:
        rows.append(row)

    return InlineKeyboardMarkup(inline_keyboard=rows)


def kb_back() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data="own:back")]
    ])


def get_role(user_id: int):
    if is_owner(user_id):
        return "owner"
    if is_senior(user_id):
        return "senior"
    if is_moder(user_id):
        return "moder"
    if is_econom(user_id):
        return "econom"
    return None


ROLE_TITLES = {
    "owner":  "👑 <b>Команды владельца</b>",
    "senior": "🚫 <b>Команды старшего модератора</b>",
    "moder":  "⚠️ <b>Команды модератора</b>",
    "econom": "💰 <b>Команды экономиста</b>",
}

# =========================================================
#  ДЕВ-ИНСТРУМЕНТ: получение custom_emoji_id
# =========================================================

@dp.message(Command("getemoji"))
async def cmd_getemoji(message: Message):
    log_cmd("🎨 /getemoji", message)
    user_id = message.from_user.id

    # Только владелец
    if not is_main_owner(user_id) and not is_owner(user_id):
        await message.answer("⛔ Только для владельца")
        return

    # Источник: reply → forward → само сообщение
    target_msg = None
    if message.reply_to_message:
        target_msg = message.reply_to_message
    else:
        target_msg = message

    text = target_msg.text or target_msg.caption or ""
    entities = target_msg.entities or target_msg.caption_entities or []

    # Собираем custom_emoji из entities
    found = []
    for ent in entities:
        if ent.type == "custom_emoji":
            emoji_id = getattr(ent, "custom_emoji_id", None)
            if emoji_id:
                # Вырезаем сам символ из текста (для наглядности)
                symbol = text[ent.offset:ent.offset + ent.length]
                found.append((symbol, emoji_id))

    if not found:
        await message.answer(
            "❌ <b>Премиум-эмодзи не найдены</b>\n\n"
            "Как пользоваться:\n"
            "└─ Отправь премиум-эмодзи и ответь на него <code>/getemoji</code>\n"
            "└─ Или перешли сообщение с эмодзи и ответь <code>/getemoji</code>\n"
            "└─ Или напиши эмодзи и сразу <code>/getemoji</code> в том же сообщении:\n"
            "    <code>/getemoji 🎁</code> (нужен премиум-эмодзи)",
            parse_mode="HTML"
        )
        return

    lines = [f"🎨 <b>Найдено премиум-эмодзи: {len(found)}</b>\n"]
    for i, (symbol, emoji_id) in enumerate(found, start=1):
        lines.append(
            f"<b>#{i}</b> {symbol}\n"
            f"└─ <code>{emoji_id}</code>\n"
        )

    lines.append("\n💡 <b>HTML-код для вставки:</b>")
    for i, (symbol, emoji_id) in enumerate(found, start=1):
        lines.append(
            f"<code>&lt;tg-emoji emoji-id=\"{emoji_id}\"&gt;{symbol}&lt;/tg-emoji&gt;</code>"
        )

    await message.answer("\n".join(lines), parse_mode="HTML")

@dp.message(Command("own"))
async def cmd_own(message: Message):
    log_cmd("👑 /own", message)
    role = get_role(message.from_user.id)
    if not role:
        await message.answer("⛔ У тебя нет прав")
        return

    await message.answer(
        f"{ROLE_TITLES[role]}\n\nВыбери категорию:",
        parse_mode="HTML",
        reply_markup=kb_main(role),
    )


@dp.callback_query(F.data == "own:back")
async def cb_own_back(call: CallbackQuery):
    role = get_role(call.from_user.id)
    if not role:
        await call.answer("⛔ Нет прав", show_alert=True)
        return
    await call.message.edit_text(
        f"{ROLE_TITLES[role]}\n\nВыбери категорию:",
        parse_mode="HTML",
        reply_markup=kb_main(role),
    )
    await call.answer()


@dp.callback_query(F.data.startswith("own:cat:"))
async def cb_own_cat(call: CallbackQuery):
    role = get_role(call.from_user.id)
    if not role:
        await call.answer("⛔ Нет прав", show_alert=True)
        return

    key = call.data.split(":", 2)[2]
    allow = {
        "owner":  {"econom", "moder", "anon", "access", "bot"},
        "senior": {"moder", "anon", "access"},
        "moder":  {"moder", "anon"},
        "econom": {"econom"},
    }[role]

    if key not in allow or key not in CATEGORIES:
        await call.answer("⛔ Недоступно", show_alert=True)
        return

    cat = CATEGORIES[key]
    await call.message.edit_text(
        f"{cat['title']}\n\n{cat['text']}",
        parse_mode="HTML",
        reply_markup=kb_back(),
    )
    await call.answer()


@dp.message(Command("setaccess"))
async def cmd_setaccess(message: Message):
    log_cmd("🔑 /setaccess", message)
    actor_id = message.from_user.id

    if not is_owner(actor_id) and not is_senior(actor_id):
        await message.answer("⛔ Только для владельца или старшего модератора")
        return

    args = message.text.split()[1:]
    if message.reply_to_message:
        target = message.reply_to_message.from_user
        if target.is_bot:
            await message.answer("❌ Нельзя выдать доступ боту")
            return
        target_id = target.id
        target_name = target.full_name
        ensure_user(target)
        level_args = args
    else:
        if len(args) < 2 or not args[0].startswith("@"):
            await message.answer(
                "❌ Использование:\n"
                "└─ ответь на сообщение: /setaccess [уровни]\n"
                "└─ или /setaccess @username [уровни]\n\n"
                "Уровни: econom, moder, senior, none",
                parse_mode="HTML"
            )
            return

        target_id, target_name = find_user_id(message, args[0])
        if target_id is None:
            await message.answer("❌ Пользователь не найден")
            return
        ensure_user_by_id(target_id)
        level_args = args[1:]

    if not level_args:
        await message.answer("❌ Укажи уровни: econom, moder, senior или none")
        return

    if target_id in OWNER_IDS:
        await message.answer("❌ Владелец не нуждается в уровнях")
        return

    if target_id == actor_id:
        await message.answer("❌ Нельзя выдать уровень себе")
        return

    if not is_owner(actor_id):
        if has_access(target_id, "senior"):
            await message.answer("❌ Нельзя трогать другого старшего модератора")
            return
        for level in level_args:
            if level.lower() == "senior":
                await message.answer("❌ Только владелец может выдавать уровень senior")
                return

    if level_args[0].lower() == "none":
        current = get_user_levels(target_id)
        for level in current:
            remove_access(target_id, level)

        if current:
            await message.answer(
                f"✅ <b>Уровни сняты</b>\n"
                f"└─ Кому: {target_name}\n"
                f"└─ Было: {', '.join(current)}",
                parse_mode="HTML"
            )
            try:
                await bot.send_message(target_id, "🚫 Твои права администратора сняты")
            except Exception:
                pass
        else:
            await message.answer(f"ℹ️ У {target_name} нет уровней")
        return

    added = []
    already = []
    invalid = []

    for level in level_args:
        level = level.lower()
        if level not in ("econom", "moder", "senior"):
            invalid.append(level)
            continue

        if add_access(target_id, level, actor_id):
            added.append(level)
        else:
            already.append(level)

    lines = []
    if added:
        lines.append(f"✅ <b>Уровни выданы</b>")
        lines.append(f"└─ Кому: {target_name}")
        lines.append(f"└─ Новые: {', '.join(added)}")
    if already:
        lines.append(f"ℹ️ Уже были: {', '.join(already)}")
    if invalid:
        lines.append(f"❌ Неверные: {', '.join(invalid)}")

    await message.answer("\n".join(lines), parse_mode="HTML")

    if added:
        level_names = {
            "econom": "💰 Экономист",
            "moder": "⚠️ Модератор",
            "senior": "🚫 Старший модератор",
        }
        names = [level_names.get(l, l) for l in added]
        try:
            await bot.send_message(
                target_id,
                f"⚡ <b>Тебе выданы права!</b>\n"
                f"└─ {', '.join(names)}\n\n"
                f"Список команд: /own"
            )
        except Exception:
            pass


@dp.message(Command("accesslist"))
async def cmd_accesslist(message: Message):
    log_cmd("📜 /accesslist", message)
    if not is_owner(message.from_user.id):
        await message.answer("⛔ Только для владельца")
        return

    admins = get_all_admins()

    def name_of(uid):
        data = get_user(uid)
        if not data:
            return f"ID:{uid}"
        uname = data[1]
        fname = data[2]
        return f"@{uname}" if uname else (fname or f"ID:{uid}")

    lines = ["👑 <b>Уровни доступа</b>\n"]

    lines.append("⭐ <b>Главный владелец:</b>")
    for oid in OWNER_IDS:
        lines.append(f"└─ {name_of(oid)}")

    if admins.get("owner"):
        lines.append("\n👑 <b>Владельцы:</b>")
        for uid in admins["owner"]:
            lines.append(f"└─ {name_of(uid)}")

    if admins.get("senior"):
        lines.append("\n🚫 <b>Старшие модераторы:</b>")
        for uid in admins["senior"]:
            lines.append(f"└─ {name_of(uid)}")
    else:
        lines.append("\n🚫 <b>Старшие модераторы:</b> нет")

    if admins.get("moder"):
        lines.append("\n⚠️ <b>Модераторы:</b>")
        for uid in admins["moder"]:
            lines.append(f"└─ {name_of(uid)}")
    else:
        lines.append("\n⚠️ <b>Модераторы:</b> нет")

    if admins.get("econom"):
        lines.append("\n💰 <b>Экономисты:</b>")
        for uid in admins["econom"]:
            lines.append(f"└─ {name_of(uid)}")
    else:
        lines.append("\n💰 <b>Экономисты:</b> нет")

    await message.answer("\n".join(lines), parse_mode="HTML")


# =========================================================
#  СКРЫТЫЕ КОМАНДЫ-ПОМОЩНИКИ
# =========================================================

@dp.message(Command("balance"))
async def cmd_balance(message: Message):
    log_cmd("💰 /balance", message)
    user = message.from_user
    ensure_user(user)
    balance = get_balance(user.id)
    await message.answer(
        f"💰 <b>Твой баланс:</b> <b>{balance}</b> msg",
        parse_mode="HTML"
    )


# =========================================================
#  CATCH-ALL
# =========================================================

@dp.message()
async def catch_all_messages(message: Message):
    if message.text and message.text.startswith("/"):
        print(f"[CATCH-ALL] Пропущена команда без хендлера: {message.text!r}")
        if message.from_user and not message.from_user.is_bot:
            await _daily_reminder(message.from_user.id, message.chat.id)
        return

    if not message.from_user or message.from_user.is_bot:
        return

    user = message.from_user

    try:
        ensure_user(user)
    except Exception as e:
        print(f"[CATCH-ALL] ❌ ensure_user: {e}")
        return

    try:
        vip = is_vip_active(user.id)
    except Exception as e:
        print(f"[CATCH-ALL] ❌ is_vip_active: {e}")
        vip = False

    cooldown = VIP_COOLDOWN if vip else NORMAL_COOLDOWN
    now = time.monotonic()
    last = _last_reward.get(user.id, 0)
    if now - last < cooldown:
        return

    try:
        add_msg_auto(user.id, 1)
        increment_stat(user.id, "total_messages", 1)
        _last_reward[user.id] = now
    except Exception as e:
        print(f"[CATCH-ALL] ❌ add_msg_auto: {e}")
        return

    await _daily_reminder(user.id, message.chat.id)
    await _check_and_notify_achievements(user.id, message.chat.id)


# =========================================================
#  ЗАПУСК
# =========================================================

async def main():
    init_db()
    print("Бот запущен...")
    print("Ждём сообщения...\n")
    asyncio.create_task(_ttt_watchdog())
    asyncio.create_task(_duel_watchdog())
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())