from aiogram import Bot, Dispatcher
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.dispatcher.middlewares.base import BaseMiddleware
from typing import Any, Awaitable, Callable, Dict
import html
import os
import asyncio
from datetime import datetime, timedelta, timezone

from aiogram.types import (
    Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton,
    LabeledPrice, PreCheckoutQuery, WebAppInfo,
)
from aiogram.types import FSInputFile
from aiogram import F
import asyncio
import random
import sqlite3
import time
from datetime import datetime, timedelta, timezone
from database import (
    get_next_custom_id,
    admin_set_custom_id,
    BANK_MAX_BALANCE_NORMAL,
    BANK_MAX_BALANCE_VIP, 
    BOT_TREASURY_ID, treasury_get_balance, treasury_ensure,
wedding_case_get_cooldown, wedding_case_set_cooldown,
gift_to_couple, get_top_couples, get_couple_rank, get_couple_info,
    title_is_taken,
    reset_get_targets, reset_apply_target, reset_get_user_balance,
    bank_get, bank_put, bank_take, bank_ensure,
bank_admin_add, bank_admin_remove,
	pet_add, pet_get_by_user, pet_get_by_id, pet_get_active, pet_set_active,
pet_count, pet_rename, pet_feed, pet_delete, pet_update_mood,
pet_is_name_taken, pet_set_death_notified,
pet_action_get_cooldown, pet_action_set_cooldown, pet_get_status,
PET_TYPES, PET_ACTION_COOLDOWN, PET_FEED_COOLDOWN, PET_DEATH_TIME,
PET_FEED_PRICE, PET_MOOD_DECAY_PER_HOUR, PET_MOOD_MAX,
PET_NAME_MAX_LEN, PET_RENAME_PRICE,
	get_ball_cooldown, set_ball_cooldown,
	get_history_by_kinds,
get_history_count_by_kinds,
get_history_summary_24h,
    get_top_streak,
	promo_create, promo_get, promo_activate, promo_delete, promo_list,
get_reputation, get_last_rep, set_last_rep, change_reputation,
	get_next_payment_number,
save_payment_code,
find_payment_by_code,
	delete_account,
	get_referrer, set_referrer, increment_referral_msg, get_referral,
count_rewards_24h, mark_referral_rewarded, get_referral_stats,
	log_payment, has_charge_id, get_payment_stats, get_user_payments,
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

TOKEN = "8572154161:AAFLLxcagDzZYyvWrFBMhbkYdROxktSy8wo"

AI_LIMIT_NORMAL = 10
AI_LIMIT_VIP = 20
AI_WINDOW = timedelta(minutes=1)
user_text_requests: dict[int, list[datetime]] = {}

BOT_USERNAME = "Aminka_Ai_bot"
OWNER_IDS = {7564741700}
# =====================================
#  АВТО-БЭКАП БАЗЫ ДАННЫХ
# =====================================

BACKUP_OWNER_ID = 7564741700       # кому отправлять бэкапы
BACKUP_DB_PATH = "users.db"        # путь к БД

BACKUP_CHECK_INTERVAL = 60         # раз в 60 секунд проверяем
# Игровые таймауты (нужны до watchdog'ов)
DUEL_TIMEOUT = 300
DUEL_TURN_TIMEOUT = 60
DUEL_MIN_BET = 1000

# =====================================
#  МАГИЧЕСКИЙ ШАР (/ball)
# =====================================

BALL_COOLDOWN_NORMAL = timedelta(minutes=5)
BALL_COOLDOWN_VIP    = timedelta(minutes=2)

# Премиум-эмодзи шаров
BALL_EMOJIS = [
    ("5418138833457793454", "🎱"),  # шар
    ("5361837567463399422", "🔮"),  # хрусталь
    ("5348097378672975991", "✨"),  # искры
    ("5429477976615961027", "🎲"),  # кубик
    ("5431585469823467283", "💫"),  # звёздный вихрь
    ("5429099589997184246", "🌙"),  # луна
]

BALL_ANSWERS = [
    "✅ Да",
    "🔥 Определённо да",
    "😅 Скорее да",
    "❌ Нет",
    "⛔ Определённо нет",
    "🚫 Даже не думай",
    "🤨 Есть сомнения",
    "😏 Сам подумай",
    "🔮 Пока не ясно",
    "💭 Спроси позже",
    "🎲 50/50",
    "⏳ Время покажет",
]

# =====================================
#  ПИТОМЦЫ
# =====================================

# Шансы выпадения
PET_COMMON_CASE = {
    "cat":     40,
    "dog":     30,
    "snake":   20,
    "hamster": 10,
}

PET_RARE_CASE = {
    "mouse":   30,
    "rabbit":  25,
    "turtle":  20,
    "fish":    15,
    "bear":    7,
    "fox":     3,
}

PET_CASE_PRICE_COMMON = 2500
PET_CASE_PRICE_RARE = 5000

PET_LIMIT_NORMAL = 1
PET_LIMIT_VIP = 3

# Эмодзи для анимации кейса (сетка 3×3)
PET_CASE_EMOJIS = ["🐱", "🐶", "🐍", "🐹", "🐭", "🐰", "🐢", "🐟", "🐻", "🦊"]

# Фразы для действий
PET_ACTION_PHRASES = {
    "pet": [
        "{name} мурлычет от удовольствия 😻",
        "{name} трётся о твою руку 🐾",
        "{name} довольно жмурится 😌",
        "Ты погладил {name}, и он(а) засиял(а) ✨",
        "{name} виляет хвостом от счастья 🐕",
        "{name} прижался(ась) к тебе 💕",
    ],
    "wash": [
        "Ты помыл {name}! Теперь он(а) чистый(ая) 🛁",
        "{name} блестит после купания ✨",
        "{name} недоволен(льна), но зато чистый(ая) 💦",
        "Пена летит во все стороны! {name} сияет 🫧",
        "{name} пахнет свежестью и мятой 🌿",
        "Купание прошло успешно, {name} доволен(льна) 🚿",
    ],
    "play": [
        "Ты поиграл с {name}! Он(а) в восторге 🎾",
        "{name} прыгает и радуется 🎉",
        "{name} принёс(ла) тебе игрушку 🧸",
        "Игра была весёлой! {name} устал(а), но счастлив(а) 😄",
        "{name} гоняется за мячиком 🏀",
        "{name} рад(а) провести с тобой время 💫",
    ],
}

PET_ACTION_NAMES = {
    "pet":  "Погладить",
    "wash": "Помыть",
    "play": "Поиграть",
}

PET_ACTION_EMOJIS = {
    "pet":  "🤚",
    "wash": "🛁",
    "play": "🎮",
}

# Фразы для результата кейса
PET_CASE_SUCCESS = [
    "🎉 Невероятно! Ты выбил питомца!",
    "✨ Удача на твоей стороне!",
    "🎊 Поздравляем, новый друг!",
    "🌟 Вот это дроп!",
    "💫 Отличный улов!",
]

# Фразы для дубликата
PET_CASE_DUPLICATE = [
    "😔 Такой питомец у тебя уже есть",
    "🤷 Дубликат! Возвращаем msg",
    "😐 Опять этот... Возврат",
    "🔄 Повтор, возвращаем msg",
]

PREM_DELETE = "5429137527443310063"  # 🗑️ удаление
REFERRER_REWARD = 2000    # сколько получает приглашающий
REFERRAL_REWARD = 1000    # сколько получает приглашённый
REFERRAL_THRESHOLD = 20   # сколько сообщений должен написать реферал
REFERRAL_VIP_DAYS = 2     # VIP приглашённому
REFERRAL_MAX_PER_DAY = 4  # максимум наград в 24ч

BOT_USERNAME = "Aminka_Ai_bot"
# Модерация через профиль
BAN_MIN_DAYS = 0
BAN_MAX_DAYS = 30
BAN_COOLDOWN = 2.0  # сек между кликами по счётчику

# Временные состояния экранов модерации
# { message_id: {"target_id": int, "actor_id": int, "days": int, "mode": str, "last_click": float} }
_mod_panels: dict = {}
# =====================================
#  ПРЕМИУМ-ЭМОДЗИ (custom_emoji_id)
# =====================================

# Статусы
PREM_CHECK = "5215492745900077682"  # ✅ галочка (открыто)
PREM_LOCK  = "5291873529464122510"  # 🔒 замок (не открыто)
PREM_TOP1  = "5332299818943400671"  # 🏆 топ1 (заголовок)

PREM_LINK  = "5765071340847501478"  # 🔗
PREM_USERS = "5902335789798265487"  # 👥
PREM_GIFT  = "5199749070830197566"  # 🎁
PREM_BONUS = "5870928411949539680"  # ✨

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

FALLBACK_PHOTO = "AgACAgIAAxkBAAILu2rNjFR6CE9NdRrgp27N9BwmlO-9AALkHWsbjhRxSq6BR2Q4O82xAQADAgADeAADPQQ"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Приглашения
_duel_invites: dict = {}
_marry_invites: dict = {}
_ttt_invites: dict = {}
# Тень — юзер не получает ответы от бота 1 час
_shadow_users: dict[int, float] = {}
SHADOW_DURATION = 3600  # 1 час
# { user_id: pet_id } — питомцы, ждущие имени
_pending_pet_names: dict = {}

DUEL_MIN_BET = 1000
DUEL_TIMEOUT = 300
DUEL_TURN_TIMEOUT = 60

# =====================================
# МИЛДВАРЬ: троллинг
# =====================================
class ShadowMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        if not event.from_user or event.from_user.is_bot:
            return await handler(event, data)

        user_id = event.from_user.id
        until = _shadow_users.get(user_id)

        print(f"[SHADOW-DEBUG] user={user_id} until={until} now={time.monotonic()} all={_shadow_users}")

        if until:
            if time.monotonic() < until:
                try:
                    ensure_user(event.from_user)
                    add_msg_auto(user_id, 1)
                    increment_stat(user_id, "total_messages", 1)
                except Exception as e:
                    print(f"[SHADOW] Ошибка: {e}")
                return
            else:
                _shadow_users.pop(user_id, None)

        return await handler(event, data)

class ShadowCallbackMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[CallbackQuery, Dict[str, Any]], Awaitable[Any]],
        event: CallbackQuery,
        data: Dict[str, Any],
    ) -> Any:
        if not event.from_user or event.from_user.is_bot:
            return await handler(event, data)

        user_id = event.from_user.id

        until = _shadow_users.get(user_id)
        if until:
            if time.monotonic() < until:
                await event.answer()
                return
            else:
                _shadow_users.pop(user_id, None)

        return await handler(event, data)

# =====================================
#  ФЛАГ БЛОКИРОВКИ ВО ВРЕМЯ /resetmsg
# =====================================

_reset_in_progress: bool = False


class ResetLockMiddleware(BaseMiddleware):
    """
    Пока идёт /resetmsg — все команды (кроме самой /resetmsg)
    получают заглушку. Владелец тоже.
    """
    async def __call__(self, handler, event, data):
        global _reset_in_progress

        if not _reset_in_progress:
            return await handler(event, data)

        # ─── Проверяем: это /resetmsg? ───
        text = None
        if isinstance(event, Message):
            text = event.text or ""
        elif isinstance(event, CallbackQuery):
            # Пропускаем только callback'и самой /resetmsg (подтверждение)
            data_str = event.data or ""
            if data_str.startswith(("resetmsg_yes_", "resetmsg_no_")):
                return await handler(event, data)
            # Остальные callback'и — блокируем
            try:
                await event.answer(
                    "🔧 Сейчас идёт сброс msg. Командами нельзя пользоваться временно.",
                    show_alert=True
                )
            except Exception:
                pass
            return

        # Пропускаем саму /resetmsg — пусть хендлер сам ответит «уже идёт»
        if text and text.startswith("/resetmsg"):
            return await handler(event, data)

        # Всё остальное — блокируем
        try:
            await event.answer(
                "🔧 Сейчас идёт сброс msg.\n"
                "Командами нельзя пользоваться временно.",
                parse_mode="HTML"
            )
        except Exception:
            pass
        return

# =====================================
#  МИДЛВАРЬ: БАН
# =====================================

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

# =====================================
#  МИЛДВАРЬ: фильтр команд от каналов и групп
# =====================================

class ChannelFilterMiddleware(BaseMiddleware):
    """
    Игнорирует команды, пришедшие от имени канала или группы.
    Обычные сообщения пропускает.
    """
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        sender_chat = getattr(event, "sender_chat", None)

        if sender_chat:
            # Команда?
            text = event.text or ""
            is_command = text.startswith("/")

            # Канал или группа — блокируем только команды
            if sender_chat.type in ("channel", "supergroup", "group"):
                if is_command:
                    return  # молча игнорируем
                # обычные сообщения — пропускаем (не наша задача)
                if not event.from_user:
                    return

            # Прочие sender_chat без from_user — тоже игнор
            if not event.from_user:
                return

        return await handler(event, data)

class ChannelFilterCallbackMiddleware(BaseMiddleware):
    """
    Игнорирует callback'и от имени канала или группы.
    """
    async def __call__(
        self,
        handler: Callable[[CallbackQuery, Dict[str, Any]], Awaitable[Any]],
        event: CallbackQuery,
        data: Dict[str, Any],
    ) -> Any:
        sender_chat = getattr(event, "sender_chat", None)

        if sender_chat:
            if sender_chat.type in ("channel", "supergroup", "group"):
                try:
                    await event.answer()
                except Exception:
                    pass
                return

            if not event.from_user:
                return

        return await handler(event, data)


dp.message.middleware(ChannelFilterMiddleware())
dp.message.middleware(BanMiddleware())
dp.message.middleware(ShadowMiddleware())
dp.callback_query.middleware(ChannelFilterCallbackMiddleware())
dp.callback_query.middleware(ShadowCallbackMiddleware())
dp.message.middleware(ResetLockMiddleware())
dp.callback_query.middleware(ResetLockMiddleware())
print("[STARTUP] ChannelFilter + Ban + Shadow middleware подключены")


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

# =====================================
#  ПРОВЕРКА ДОСТУПА
# =====================================

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

# =====================================
#  /addbank, /rembank — управление банком юзера
# =====================================

@dp.message(Command("addbank"))
async def cmd_addbank(message: Message):
    log_cmd("🏦 /addbank", message)

    if not is_main_owner(message.from_user.id) and not is_owner(message.from_user.id):
        await message.answer("⛔ Только для владельца")
        return

    args = message.text.split()[1:]
    target_id, target_name, amount = _parse_user_amount(message, args)

    if target_id is None or amount is None:
        await message.answer(
            "❌ Использование:\n"
            "└─ ответь на сообщение: <code>/addbank [сумма]</code>\n"
            "└─ или <code>/addbank @username [сумма]</code>",
            parse_mode="HTML"
        )
        return

    ensure_user_by_id(target_id)
    new_balance = bank_admin_add(target_id, amount)
    log_transaction(message.from_user.id, target_id, amount, "admin_bank_add")

    await message.answer(
        f"🏦 <b>Начислено в банк</b>\n"
        f"└─ Кому: {target_name}\n"
        f"└─ Сумма: <b>+{amount:,}</b> msg\n"
        f"└─ В банке: <b>{new_balance:,}</b> msg",
        parse_mode="HTML"
    )


@dp.message(Command("rembank"))
async def cmd_rembank(message: Message):
    log_cmd("🏦 /rembank", message)

    if not is_main_owner(message.from_user.id) and not is_owner(message.from_user.id):
        await message.answer("⛔ Только для владельца")
        return

    args = message.text.split()[1:]
    target_id, target_name, amount = _parse_user_amount(message, args)

    if target_id is None or amount is None:
        await message.answer(
            "❌ Использование:\n"
            "└─ ответь на сообщение: <code>/rembank [сумма]</code>\n"
            "└─ или <code>/rembank @username [сумма]</code>",
            parse_mode="HTML"
        )
        return

    ensure_user_by_id(target_id)
    new_balance = bank_admin_remove(target_id, amount)
    log_transaction(message.from_user.id, target_id, -amount, "admin_bank_rem")

    await message.answer(
        f"🏦 <b>Списано из банка</b>\n"
        f"└─ Кому: {target_name}\n"
        f"└─ Сумма: <b>-{amount:,}</b> msg\n"
        f"└─ В банке: <b>{new_balance:,}</b> msg",
        parse_mode="HTML"
    )

# =====================================
#  ПИТОМЦЫ — хелперы форматирования
# =====================================

def _format_pet_time(hours_left: float) -> str:
    """Форматирует 'через 5 часов 12 минут' / 'меньше минуты' / 'сейчас'."""
    if hours_left <= 0:
        return "сейчас"

    total_minutes = int(hours_left * 60)
    if total_minutes < 1:
        return "меньше минуты"

    h = total_minutes // 60
    m = total_minutes % 60

    if h == 0:
        return f"{m} мин"
    if m == 0:
        return f"{h} ч"
    return f"{h} ч {m} мин"


def _pet_mood_emoji(mood: int) -> str:
    """Эмодзи настроения по шкале."""
    if mood >= 80:
        return "😻"
    if mood >= 60:
        return "😊"
    if mood >= 40:
        return "😐"
    if mood >= 20:
        return "😔"
    return "😿"


def _pet_status_line(pet_row) -> str:
    """
    Возвращает строку статуса питомца:
    - 'Время до еды: через 5ч 12м'
    - '🐾 Питомец хочет кушать'
    - '⚠️ Питомец умирает, осталось 45 мин'
    """
    pet_id = pet_row[0]
    status = pet_get_status(pet_id)
    if not status:
        return "❓ Статус неизвестен"

    hours_until_death = status["hours_left_until_death"]
    hours_until_hungry = status["hours_left_until_hungry"]
    is_hungry = status["is_hungry"]
    is_dying = status["is_dying"]

    if is_dying:
        time_str = _format_pet_time(hours_until_death)
        return f"⚠️ Питомец умирает, осталось: <b>{time_str}</b>"

    if is_hungry:
        time_str = _format_pet_time(hours_until_death)
        return f"🍽️ Питомец хочет кушать\n└─ 🕐 Умрёт через: <b>{time_str}</b>"

    time_str = _format_pet_time(hours_until_hungry)
    return f"🍽️ Время до еды: <b>через {time_str}</b>"


def _pet_build_switch_row(pets: list, active_id: int) -> list:
    """
    Строит ряд кнопок-переключателей активного питомца.
    pets — список строк из user_pets.
    Возвращает список InlineKeyboardButton или [].
    """
    if len(pets) <= 1:
        return []

    row = []
    for p in pets:
        pid = p[0]
        ptype = p[2]
        pname = p[3]

        emoji, _, _ = PET_TYPES.get(ptype, ("❓", "?", "common"))

        if pid == active_id:
            text = f"• {emoji} {pname} •"
            cb = "pet_noop"
        else:
            text = f"{emoji} {pname}"
            cb = f"pet_switch_{pid}"

        row.append(InlineKeyboardButton(text=text, callback_data=cb))

    return row


# =====================================
#  ПИТОМЦЫ — сборка меню
# =====================================

def _build_pet_menu(user_id: int) -> tuple:
    """
    Главное меню /pet.
    Возвращает (text, kb) или (None, None) если питомцев нет.
    """
    pets = pet_get_by_user(user_id)
    if not pets:
        return None, None

    active = pet_get_active(user_id)
    if not active:
        # Fallback — берём первого
        active = pets[0]
        pet_set_active(user_id, active[0])

    (pid, _uid, ptype, pname, mood, fed_at, created_at, is_active, _dn) = active
    emoji, type_name, _rarity = PET_TYPES.get(ptype, ("❓", "?", "common"))

    status_line = _pet_status_line(active)
    mood_emoji = _pet_mood_emoji(mood)

    lines = []

    # ─── Список питомцев (если > 1) ───
    if len(pets) > 1:
        pet_list = " · ".join(
            f"{PET_TYPES.get(p[2], ('❓',))[0]} {p[3]}"
            for p in pets
        )
        lines.append(f"🐾 <b>Твои питомцы:</b> {pet_list}")
        lines.append("")

    # ─── Карточка активного ───
    lines.append(f"{emoji} <b>Питомец:</b> {type_name}")
    lines.append(f"📛 <b>Имя:</b> {pname}")
    lines.append(f"{mood_emoji} <b>Настроение:</b> {mood}/{PET_MOOD_MAX}")
    lines.append(status_line)

    text = "\n".join(lines)

    # ─── Кнопки ───
    kb_rows = []

    # Переключатели активного
    switch_row = _pet_build_switch_row(pets, pid)
    if switch_row:
        kb_rows.append(switch_row)

    # Основные действия
    kb_rows.append([
        InlineKeyboardButton(text="🍽️ Покормить", callback_data=f"pet_feed_{pid}"),
        InlineKeyboardButton(text="🎮 Действия", callback_data=f"pet_actions_{pid}"),
    ])
    kb_rows.append([
        InlineKeyboardButton(text="🐾 Питомцы", callback_data="pet_list_main"),
    ])

    kb = InlineKeyboardMarkup(inline_keyboard=kb_rows)
    return text, kb


def _build_pets_all() -> tuple:
    """Справочник всех питомцев."""
    lines = ["🐾 <b>Все питомцы</b>", ""]

    # ─── Обычные ───
    lines.append("🎁 <b>Обычный кейс</b> (2500 msg):")
    for ptype, chance in PET_COMMON_CASE.items():
        emoji, name, _ = PET_TYPES[ptype]
        lines.append(f"└─ {emoji} <b>{name}</b> — {chance}%")

    lines.append("")
    lines.append("💎 <b>Редкий кейс</b> (5000 msg, VIP):")
    for ptype, chance in PET_RARE_CASE.items():
        emoji, name, _ = PET_TYPES[ptype]
        lines.append(f"└─ {emoji} <b>{name}</b> — {chance}%")

    text = "\n".join(lines)

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data="pet_back_main")]
    ])
    return text, kb


def _build_pets_mine(user_id: int) -> tuple:
    """Список питомцев юзера с кнопками действий."""
    pets = pet_get_by_user(user_id)
    if not pets:
        return None, None

    lines = [f"🐾 <b>Твои питомцы</b> ({len(pets)})", ""]

    kb_rows = []

    for p in pets:
        pid, _uid, ptype, pname, mood, fed_at, created_at, is_active, _dn = p
        emoji, type_name, _rarity = PET_TYPES.get(ptype, ("❓", "?", "common"))
        mood_emoji = _pet_mood_emoji(mood)

        marker = " ⭐ <b>активный</b>" if is_active else ""
        lines.append(f"{emoji} <b>{pname}</b> ({type_name}){marker}")
        lines.append(f"└─ {mood_emoji} Настроение: {mood}/{PET_MOOD_MAX}")

        # Кнопки действий для этого питомца
        kb_rows.append([
            InlineKeyboardButton(text=f"🤚 {pname}", callback_data=f"pet_pet_{pid}"),
            InlineKeyboardButton(text=f"🛁 {pname}", callback_data=f"pet_wash_{pid}"),
            InlineKeyboardButton(text=f"🎮 {pname}", callback_data=f"pet_play_{pid}"),
        ])

    text = "\n".join(lines)

    kb_rows.append([
        InlineKeyboardButton(text="◀️ Назад", callback_data="pet_back_main")
    ])

    kb = InlineKeyboardMarkup(inline_keyboard=kb_rows)
    return text, kb


def _build_pet_actions(pet_id: int) -> tuple:
    """Меню действий для питомца."""
    pet = pet_get_by_id(pet_id)
    if not pet:
        return None, None

    (pid, user_id, ptype, pname, mood, fed_at, created_at, is_active, _dn) = pet
    emoji, type_name, _rarity = PET_TYPES.get(ptype, ("❓", "?", "common"))
    mood_emoji = _pet_mood_emoji(mood)

    # Кулдауны каждого действия
    now = datetime.now()
    action_lines = []

    for action in ("pet", "wash", "play"):
        last = pet_action_get_cooldown(pid, action)
        act_name = PET_ACTION_NAMES[action]
        act_emoji = PET_ACTION_EMOJIS[action]

        if last:
            try:
                last_dt = datetime.fromisoformat(last)
                elapsed = now - last_dt
                if elapsed < PET_ACTION_COOLDOWN:
                    remaining = PET_ACTION_COOLDOWN - elapsed
                    total_min = int(remaining.total_seconds() / 60)
                    if total_min < 1:
                        time_str = "меньше минуты"
                    else:
                        time_str = f"{total_min} мин"
                    action_lines.append(f"└─ {act_emoji} <b>{act_name}</b> — ⏳ {time_str}")
                    continue
            except ValueError:
                pass

        action_lines.append(f"└─ {act_emoji} <b>{act_name}</b> — ✅ доступно")

    text = (
        f"🎮 <b>Действия</b>\n\n"
        f"{emoji} <b>{pname}</b> ({type_name})\n"
        f"{mood_emoji} Настроение: <b>{mood}/{PET_MOOD_MAX}</b>\n"
        f"\n"
        + "\n".join(action_lines)
    )

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🤚 Погладить", callback_data=f"pet_do_pet_{pid}"),
            InlineKeyboardButton(text="🛁 Помыть", callback_data=f"pet_do_wash_{pid}"),
        ],
        [
            InlineKeyboardButton(text="🎮 Поиграть", callback_data=f"pet_do_play_{pid}"),
        ],
        [
            InlineKeyboardButton(text="◀️ Назад", callback_data="pet_back_main"),
        ],
    ])
    return text, kb

# =====================================
#  /pet — главное меню питомцев
# =====================================

@dp.message(Command("pet"))
async def cmd_pet(message: Message):
    log_cmd("🐾 /pet", message)
    user = message.from_user
    ensure_user(user)

    # Проверка питомцев на смерть (при активности)
    await _pet_check_deaths(user.id)

    text, kb = _build_pet_menu(user.id)
    if text is None:
        # Нет питомцев
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🐾 Все питомцы", callback_data="pet_list_all")],
            [InlineKeyboardButton(text="🎁 Кейсы в /cases", callback_data="pet_noop")],
        ])
        await message.answer(
            "🐾 <b>У тебя пока нет питомцев</b>\n\n"
            "└─ Купи кейс питомца в /cases\n"
            "└─ Обычный — 2500 msg\n"
            "└─ Редкий — 5000 msg (только VIP)",
            parse_mode="HTML",
            reply_markup=kb,
            reply_to_message_id=message.message_id
        )
        return

    await message.answer(
        text, parse_mode="HTML", reply_markup=kb,
        reply_to_message_id=message.message_id
    )






@dp.message(Command("petname"))
async def cmd_petname(message: Message):
    log_cmd("📛 /petname", message)
    user = message.from_user
    ensure_user(user)

    await _pet_check_deaths(user.id)

    args = message.text.split(maxsplit=1)

    if len(args) < 2 or not args[1].strip():
        await message.answer(
            "📛 <b>Смена имени питомца</b>\n\n"
            "└─ Использование: <code>/petname [имя]</code>\n"
            f"└─ До {PET_NAME_MAX_LEN} символов\n"
            "└─ Имя должно быть уникальным\n"
            f"└─ Смена: {PET_RENAME_PRICE} msg (первое имя — бесплатно)",
            parse_mode="HTML"
        )
        return

    new_name = args[1].strip()

    # ─── Валидация ───
    if len(new_name) < 1 or len(new_name) > PET_NAME_MAX_LEN:
        await message.answer(
            f"❌ Имя должно быть от 1 до {PET_NAME_MAX_LEN} символов",
            parse_mode="HTML"
        )
        return

    forbidden = ["<", ">", "&", "@", "\n", "\r", "\t"]
    if any(ch in new_name for ch in forbidden):
        await message.answer(
            "❌ Имя не может содержать символы <code>&lt; &gt; &amp; @</code> и переносы",
            parse_mode="HTML"
        )
        return

    if pet_is_name_taken(new_name):
        await message.answer(
            f"❌ Имя <b>{new_name}</b> уже занято",
            parse_mode="HTML"
        )
        return

    # ─── Есть ли pending (первое имя) ───
    pending_pet_id = _pending_pet_names.get(user.id)

    if pending_pet_id:
        pet = pet_get_by_id(pending_pet_id)
        if pet and pet[1] == user.id:
            if pet_rename(pending_pet_id, new_name):
                _pending_pet_names.pop(user.id, None)

                pet_emoji, pet_type_name, _ = PET_TYPES.get(pet[2], ("❓", "?", "common"))

                await message.answer(
                    f"✅ <b>Питомец назван!</b>\n"
                    f"└─ {pet_emoji} {pet_type_name}: <b>{new_name}</b>\n"
                    f"└─ Имя установлено бесплатно\n\n"
                    f"💡 Смотреть: /pet",
                    parse_mode="HTML"
                )
                return
            else:
                await message.answer("❌ Не удалось установить имя (занято?)")
                return
        else:
            # Записи нет — забыли
            _pending_pet_names.pop(user.id, None)

    # ─── Обычная смена имени ───
    pets = pet_get_by_user(user.id)
    if not pets:
        await message.answer("🐾 У тебя нет питомцев")
        return

    if len(pets) == 1:
        await _pet_do_rename(message, user, pets[0][0], new_name)
        return

    # Несколько — выбор
    kb_rows = []
    for p in pets:
        pid, _uid, ptype, pname, *_ = p
        emoji, _, _ = PET_TYPES.get(ptype, ("❓", "?", "common"))
        kb_rows.append([InlineKeyboardButton(
            text=f"{emoji} {pname}",
            callback_data=f"pet_rename_{pid}_{new_name}"
        )])

    kb = InlineKeyboardMarkup(inline_keyboard=kb_rows)

    await message.answer(
        f"📛 <b>Кого переименовать в «{new_name}»?</b>",
        parse_mode="HTML",
        reply_markup=kb
    )


async def _pet_do_rename(message: Message, user, pet_id: int, new_name: str):
    """Общая логика переименования (вызывается и из команды, и из callback)."""
    # Проверка баланса
    balance = get_balance(user.id)
    if balance < PET_RENAME_PRICE:
        await message.answer(
            f"😢 <b>Недостаточно msg!</b>\n\n"
            f"└─ Нужно: {PET_RENAME_PRICE}\n"
            f"└─ У тебя: {balance}",
            parse_mode="HTML"
        )
        return

    # Меняем
    if not pet_rename(pet_id, new_name):
        await message.answer(
            f"❌ Не удалось переименовать — имя уже занято",
            parse_mode="HTML"
        )
        return

    # Списываем
    add_balance(user.id, -PET_RENAME_PRICE)
    log_transaction(user.id, user.id, -PET_RENAME_PRICE, "pet_rename")

    await message.answer(
        f"✅ <b>Имя питомца изменено!</b>\n"
        f"└─ Новое: <b>{new_name}</b>\n"
        f"└─ Списано: {PET_RENAME_PRICE} msg",
        parse_mode="HTML"
    )

@dp.callback_query(F.data.startswith("pet_switch_"))
async def cb_pet_switch(callback: CallbackQuery):
    try:
        pet_id = int(callback.data.replace("pet_switch_", ""))
    except ValueError:
        await callback.answer("⚠️ Ошибка", show_alert=True)
        return

    pet = pet_get_by_id(pet_id)
    if not pet:
        await callback.answer("⚠️ Питомец не найден", show_alert=True)
        return

    user_id = pet[1]
    if callback.from_user.id != user_id:
        await callback.answer("❌ Это не твой питомец", show_alert=True)
        return

    pet_set_active(user_id, pet_id)

    text, kb = _build_pet_menu(user_id)
    if text is None:
        await callback.answer("⚠️ Ошибка", show_alert=True)
        return

    try:
        await callback.message.edit_text(text, parse_mode="HTML", reply_markup=kb)
    except Exception as e:
        print(f"[PET] Ошибка: {e}")
    await callback.answer()

@dp.callback_query(F.data == "pet_back_main")
async def cb_pet_back_main(callback: CallbackQuery):
    user_id = callback.from_user.id
    ensure_user(callback.from_user)

    text, kb = _build_pet_menu(user_id)

    if text is None:
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🐾 Все питомцы", callback_data="pet_list_all")],
        ])
        try:
            await callback.message.edit_text(
                "🐾 <b>У тебя пока нет питомцев</b>\n\n"
                "└─ Купи кейс питомца в /cases",
                parse_mode="HTML",
                reply_markup=kb
            )
        except Exception:
            pass
        await callback.answer()
        return

    try:
        await callback.message.edit_text(text, parse_mode="HTML", reply_markup=kb)
    except Exception as e:
        print(f"[PET] Ошибка: {e}")
    await callback.answer()

@dp.callback_query(F.data == "pet_list_all")
async def cb_pet_list_all(callback: CallbackQuery):
    text, kb = _build_pets_all()

    try:
        await callback.message.edit_text(text, parse_mode="HTML", reply_markup=kb)
    except Exception as e:
        print(f"[PET] Ошибка: {e}")
    await callback.answer()

@dp.callback_query(F.data == "pet_list_main")
async def cb_pet_list_main(callback: CallbackQuery):
    user_id = callback.from_user.id

    text, kb = _build_pets_mine(user_id)
    if text is None:
        await callback.answer("🐾 У тебя нет питомцев", show_alert=True)
        return

    try:
        await callback.message.edit_text(text, parse_mode="HTML", reply_markup=kb)
    except Exception as e:
        print(f"[PET] Ошибка: {e}")
    await callback.answer()

@dp.callback_query(F.data.startswith("pet_actions_"))
async def cb_pet_actions(callback: CallbackQuery):
    try:
        pet_id = int(callback.data.replace("pet_actions_", ""))
    except ValueError:
        await callback.answer("⚠️ Ошибка", show_alert=True)
        return

    pet = pet_get_by_id(pet_id)
    if not pet:
        await callback.answer("⚠️ Питомец не найден", show_alert=True)
        return

    if callback.from_user.id != pet[1]:
        await callback.answer("❌ Это не твой питомец", show_alert=True)
        return

    text, kb = _build_pet_actions(pet_id)
    if text is None:
        await callback.answer("⚠️ Ошибка", show_alert=True)
        return

    try:
        await callback.message.edit_text(text, parse_mode="HTML", reply_markup=kb)
    except Exception as e:
        print(f"[PET] Ошибка: {e}")
    await callback.answer()

@dp.callback_query(F.data == "pet_noop")
async def cb_pet_noop(callback: CallbackQuery):
    await callback.answer()

@dp.callback_query(F.data.startswith("pet_rename_"))
async def cb_pet_rename(callback: CallbackQuery):
    # Формат: pet_rename_{pet_id}_{new_name}
    # new_name может содержать подчёркивания, поэтому парсим аккуратно
    data = callback.data[len("pet_rename_"):]

    # Отделяем pet_id (число до первого "_")
    parts = data.split("_", 1)
    if len(parts) != 2:
        await callback.answer("⚠️ Ошибка", show_alert=True)
        return

    try:
        pet_id = int(parts[0])
    except ValueError:
        await callback.answer("⚠️ Ошибка", show_alert=True)
        return

    new_name = parts[1]

    pet = pet_get_by_id(pet_id)
    if not pet:
        await callback.answer("⚠️ Питомец не найден", show_alert=True)
        return

    user_id = pet[1]
    if callback.from_user.id != user_id:
        await callback.answer("❌ Это не твой питомец", show_alert=True)
        return

    # Проверка баланса
    balance = get_balance(user_id)
    if balance < PET_RENAME_PRICE:
        await callback.answer(
            f"😢 Нужно {PET_RENAME_PRICE} msg, у тебя {balance}",
            show_alert=True
        )
        return

    # Проверка уникальности (могли занять, пока юзер думал)
    if pet_is_name_taken(new_name):
        await callback.answer(
            f"❌ Имя «{new_name}» уже занято",
            show_alert=True
        )
        return

    if not pet_rename(pet_id, new_name):
        await callback.answer("❌ Ошибка переименования", show_alert=True)
        return

    add_balance(user_id, -PET_RENAME_PRICE)
    log_transaction(user_id, user_id, -PET_RENAME_PRICE, "pet_rename")

    try:
        await callback.message.edit_text(
            f"✅ <b>Имя питомца изменено!</b>\n"
            f"└─ Новое: <b>{new_name}</b>\n"
            f"└─ Списано: {PET_RENAME_PRICE} msg",
            parse_mode="HTML"
        )
    except Exception:
        pass

    await callback.answer("✅ Готово!")

async def _pet_check_deaths(user_id: int):
    """
    Проверяет питомцев юзера при активности:
    - Если питомец прожил > 36ч без кормления — удаляет, шлёт уведомление.
    - Если до смерти < 1ч и уведомление не слали — шлёт предупреждение.
    """
    try:
        pets = pet_get_by_user(user_id)
        if not pets:
            return

        now = datetime.now()

        for p in pets:
            pid = p[0]
            pname = p[3]
            fed_at = p[5]
            death_notified = p[8]

            if not fed_at:
                # Нет данных о кормлении — считаем, что только что создан, скипаем
                continue

            try:
                fed_dt = datetime.fromisoformat(fed_at)
            except ValueError:
                continue

            elapsed = now - fed_dt
            elapsed_hours = elapsed.total_seconds() / 3600

            # ─── Смерть ───
            if elapsed_hours >= 36:
                pet_delete(pid)
                try:
                    await bot.send_message(
                        user_id,
                        f"💀 <b>Твой питомец умер...</b>\n\n"
                        f"└─ Имя: <b>{pname}</b>\n"
                        f"└─ Причина: голод\n\n"
                        f"💡 Имя освобождено. Купи нового питомца в /cases",
                        parse_mode="HTML"
                    )
                except Exception:
                    pass
                continue

            # ─── Уведомление за 1 час ───
            hours_until_death = 36 - elapsed_hours

            if 0 < hours_until_death <= 1 and not death_notified:
                pet_set_death_notified(pid)
                try:
                    minutes = int(hours_until_death * 60)
                    await bot.send_message(
                        user_id,
                        f"⚠️ <b>Твой питомец умирает!</b>\n\n"
                        f"└─ Имя: <b>{pname}</b>\n"
                        f"└─ Осталось: <b>{minutes} мин</b>\n\n"
                        f"💡 Срочно покорми: /pet",
                        parse_mode="HTML"
                    )
                except Exception:
                    pass

    except Exception as e:
        print(f"[PET] Ошибка проверки смертей: {e}")


async def _pet_apply_mood_decay(pet_row):
    """
    Начисляет падение настроения со временем (-20/час).
    Возвращает актуальное настроение.
    """
    pid = pet_row[0]
    mood = pet_row[4]
    fed_at = pet_row[5]

    if not fed_at:
        return mood

    try:
        fed_dt = datetime.fromisoformat(fed_at)
    except ValueError:
        return mood

    # Настроение падает от момента создания/последнего кормления
    # Но проще — использовать fed_at как точку отсчёта
    # Однако настроение падает независимо, поэтому храним время последнего обновления.

    # Упрощённый вариант: считаем от последнего действия (или кормления).
    # Возьмём время последнего действия, или fed_at если действий не было.
    last_action_at = fed_at

    for action in ("pet", "wash", "play"):
        last = pet_action_get_cooldown(pid, action)
        if last and last > last_action_at:
            last_action_at = last

    try:
        last_dt = datetime.fromisoformat(last_action_at)
    except ValueError:
        return mood

    elapsed = datetime.now() - last_dt
    hours = int(elapsed.total_seconds() / 3600)

    if hours <= 0:
        return mood

    new_mood = max(0, mood - hours * PET_MOOD_DECAY_PER_HOUR)
    return new_mood

@dp.callback_query(F.data.startswith("pet_feed_"))
async def cb_pet_feed(callback: CallbackQuery):
    try:
        pet_id = int(callback.data.replace("pet_feed_", ""))
    except ValueError:
        await callback.answer("⚠️ Ошибка", show_alert=True)
        return

    user = callback.from_user
    ensure_user(user)

    pet = pet_get_by_id(pet_id)
    if not pet:
        await callback.answer("⚠️ Питомец не найден", show_alert=True)
        return

    (pid, owner_id, ptype, pname, mood, fed_at, created_at, is_active, _dn) = pet

    if user.id != owner_id:
        await callback.answer("❌ Это не твой питомец", show_alert=True)
        return

    # ─── Проверка: сыт ли? ───
    status = pet_get_status(pid)
    if status and not status["is_hungry"]:
        # Сыт — показываем сколько ждать
        hours_left = status["hours_left_until_hungry"]
        time_str = _format_pet_time(hours_left)
        await callback.answer(
            f"🍽️ {pname} ещё сыт!\nСледующее кормление через: {time_str}",
            show_alert=True
        )
        return

    # ─── Проверка: питомец умирает? ───
    if status and status["hours_left_until_death"] <= 0:
        await callback.answer(
            "💀 Питомец уже умер...",
            show_alert=True
        )
        return

    # ─── Проверка баланса ───
    balance = get_balance(user.id)
    if balance < PET_FEED_PRICE:
        await callback.answer(
            f"😢 Недостаточно msg!\nНужно: {PET_FEED_PRICE}, у тебя: {balance}",
            show_alert=True
        )
        return

    # ─── Кормим ───
    add_balance(user.id, -PET_FEED_PRICE)
    log_transaction(user.id, user.id, -PET_FEED_PRICE, "pet_feed")
    pet_feed(pid)

    # Обновляем меню
    text, kb = _build_pet_menu(user.id)
    if text:
        try:
            await callback.message.edit_text(text, parse_mode="HTML", reply_markup=kb)
        except Exception as e:
            print(f"[PET] Ошибка: {e}")

    await callback.answer(f"🍽️ {pname} покормлен!")

    # Уведомление
    try:
        await bot.send_message(
            user.id,
            f"🍽️ <b>Ты покормил {pname}!</b>\n"
            f"└─ Списано: {PET_FEED_PRICE} msg\n"
            f"└─ Теперь сыт на 12 часов",
            parse_mode="HTML"
        )
    except Exception:
        pass

# =====================================
#  ПИТОМЦЫ — действия
# =====================================

async def _pet_do_action(user_id: int, pet_id: int, action: str, edit_target):
    """
    Выполняет действие над питомцем.
    edit_target — Message или CallbackQuery.message для редактирования.
    Возвращает (успех: bool, сообщение_ответа: str).
    """
    pet = pet_get_by_id(pet_id)
    if not pet:
        return False, "⚠️ Питомец не найден"

    (pid, owner_id, ptype, pname, mood, fed_at, created_at, is_active, _dn) = pet

    if user_id != owner_id:
        return False, "❌ Это не твой питомец"

    # ─── Проверка смерти ───
    status = pet_get_status(pid)
    if not status or status["hours_left_until_death"] <= 0:
        return False, "💀 Питомец умер..."

    # ─── Проверка кулдауна ───
    last = pet_action_get_cooldown(pid, action)
    if last:
        try:
            last_dt = datetime.fromisoformat(last)
            elapsed = datetime.now() - last_dt
            if elapsed < PET_ACTION_COOLDOWN:
                remaining = PET_ACTION_COOLDOWN - elapsed
                total_min = int(remaining.total_seconds() / 60)
                if total_min < 1:
                    time_str = "меньше минуты"
                else:
                    time_str = f"{total_min} мин"
                act_name = PET_ACTION_NAMES[action]
                return False, f"⏳ <b>{act_name}</b> — ещё {time_str}"
        except ValueError:
            pass

    # ─── Применяем decay настроения ───
    new_mood = await _pet_apply_mood_decay(pet)
    if new_mood != mood:
        pet_update_mood(pid, new_mood)
        mood = new_mood

    # ─── Начисляем +10 ───
    new_mood = min(PET_MOOD_MAX, mood + 10)
    pet_update_mood(pid, new_mood)

    # ─── Ставим кулдаун ───
    pet_action_set_cooldown(pid, action)

    # ─── Фраза ───
    phrases = PET_ACTION_PHRASES.get(action, ["Ты сделал что-то с {name}"])
    phrase = random.choice(phrases).format(name=pname)

    # ─── Обновляем меню ───
    text, kb = _build_pet_actions(pid)
    if text:
        try:
            await edit_target.edit_text(text, parse_mode="HTML", reply_markup=kb)
        except Exception as e:
            print(f"[PET] Ошибка редактирования: {e}")

    # ─── Отправляем фразу в отдельном сообщении ───
    try:
        await bot.send_message(
            user_id,
            f"{phrase}\n\n"
            f"└─ Настроение: <b>{new_mood}/{PET_MOOD_MAX}</b> (+10)",
            parse_mode="HTML"
        )
    except Exception:
        pass

    return True, phrase

@dp.callback_query(F.data.startswith("pet_do_"))
async def cb_pet_do_action(callback: CallbackQuery):
    # Формат: pet_do_{action}_{pet_id}
    data = callback.data[len("pet_do_"):]

    parts = data.split("_", 1)
    if len(parts) != 2:
        await callback.answer("⚠️ Ошибка", show_alert=True)
        return

    action = parts[0]
    try:
        pet_id = int(parts[1])
    except ValueError:
        await callback.answer("⚠️ Ошибка", show_alert=True)
        return

    if action not in ("pet", "wash", "play"):
        await callback.answer("⚠️ Неизвестное действие", show_alert=True)
        return

    user = callback.from_user
    ensure_user(user)

    ok, msg = await _pet_do_action(user.id, pet_id, action, callback.message)

    if not ok:
        await callback.answer(msg.replace("<b>", "").replace("</b>", ""), show_alert=True)
        return

    await callback.answer("✅")

@dp.callback_query(F.data.startswith("pet_pet_"))
async def cb_pet_quick_pet(callback: CallbackQuery):
    await _pet_quick_action(callback, "pet")


@dp.callback_query(F.data.startswith("pet_wash_"))
async def cb_pet_quick_wash(callback: CallbackQuery):
    await _pet_quick_action(callback, "wash")


@dp.callback_query(F.data.startswith("pet_play_"))
async def cb_pet_quick_play(callback: CallbackQuery):
    await _pet_quick_action(callback, "play")


async def _pet_quick_action(callback: CallbackQuery, action: str):
    """Общая логика для быстрых действий из списка питомцев."""
    prefix = f"pet_{action}_"
    try:
        pet_id = int(callback.data.replace(prefix, ""))
    except ValueError:
        await callback.answer("⚠️ Ошибка", show_alert=True)
        return

    user = callback.from_user
    ensure_user(user)

    ok, msg = await _pet_do_action(user.id, pet_id, action, callback.message)

    if not ok:
        await callback.answer(msg.replace("<b>", "").replace("</b>", ""), show_alert=True)
        return

    await callback.answer("✅")

    # После действия обновляем список «Твои питомцы»
    text, kb = _build_pets_mine(user.id)
    if text:
        try:
            await callback.message.edit_text(text, parse_mode="HTML", reply_markup=kb)
        except Exception:
            pass

def _roll_pet_from_case(pool: str) -> str:
    """
    Возвращает pet_type по шансам.
    pool — 'common' или 'rare'.
    """
    if pool == "common":
        chances = PET_COMMON_CASE
    else:
        chances = PET_RARE_CASE

    # Взвешенный рандом
    total = sum(chances.values())
    roll = random.uniform(0, total)

    acc = 0.0
    for ptype, weight in chances.items():
        acc += weight
        if roll < acc:
            return ptype

    # Fallback — первый
    return next(iter(chances.keys()))

def _render_pet_case_grid() -> str:
    """Возвращает сетку 3×3 из случайных эмодзи питомцев."""
    picked = [random.choice(PET_CASE_EMOJIS) for _ in range(9)]
    lines = []
    for r in range(3):
        row = picked[r * 3:r * 3 + 3]
        lines.append(" | ".join(row))
    return "\n".join(lines)


async def _pet_case_animation(edit_target, case_data: dict, user_id: int):
    """
    Анимация кейса питомца: 3 шага сетки + результат.
    edit_target — Message или CallbackQuery.message.
    """
    delay = case_data["frame_delay"]

    # ─── 3 шага сетки ───
    for _ in range(3):
        try:
            await edit_target.edit_text(
                f"🐾 <b>Крутим…</b>\n\n{_render_pet_case_grid()}",
                parse_mode="HTML"
            )
        except Exception:
            pass
        await asyncio.sleep(delay)

    # ─── Результат ───
    pool = case_data["pet_pool"]
    pet_type = _roll_pet_from_case(pool)

    pet_emoji, pet_type_name, _ = PET_TYPES.get(pet_type, ("❓", "?", "common"))

    # ─── Проверка: питомец уже есть? ───
    user_pets = pet_get_by_user(user_id)
    already_have = any(p[2] == pet_type for p in user_pets)

    price = case_data["price"]

    if already_have:
        # Возврат
        add_balance(user_id, price)
        log_transaction(user_id, user_id, price, "pet_case_refund")

        phrase = random.choice(PET_CASE_DUPLICATE)

        new_balance = get_balance(user_id)

        result_text = (
            f"🐾 <b>Кейс открыт!</b>\n\n"
            f"└─ Выпал: {pet_emoji} <b>{pet_type_name}</b>\n"
            f"└─ {phrase}\n\n"
            f"💰 Возврат: <b>+{price:,}</b> msg\n"
            f"└─ Баланс: <b>{new_balance:,}</b> msg"
        )

        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text="🎁 К кейсам",
                callback_data=f"cases_page_{user_id}_0"
            )]
        ])

        try:
            await edit_target.edit_text(result_text, parse_mode="HTML", reply_markup=kb)
        except Exception:
            pass

        return

    # ─── Проверка слота ───
    is_vip = is_vip_active(user_id)
    pet_slots = PET_LIMIT_VIP if is_vip else PET_LIMIT_NORMAL
    current_count = pet_count(user_id)

    if current_count >= pet_slots:
        # Нет места — возврат
        add_balance(user_id, price)
        log_transaction(user_id, user_id, price, "pet_case_no_slot")

        new_balance = get_balance(user_id)

        result_text = (
            f"🐾 <b>Кейс открыт!</b>\n\n"
            f"└─ Выпал: {pet_emoji} <b>{pet_type_name}</b>\n"
            f"└─ ❌ У тебя нет свободного слота ({current_count}/{pet_slots})\n\n"
            f"💰 Возврат: <b>+{price:,}</b> msg\n"
            f"└─ Баланс: <b>{new_balance:,}</b> msg\n\n"
            f"💡 VIP даёт 3 слота вместо 1"
        )

        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text="🎁 К кейсам",
                callback_data=f"cases_page_{user_id}_0"
            )]
        ])

        try:
            await edit_target.edit_text(result_text, parse_mode="HTML", reply_markup=kb)
        except Exception:
            pass

        return

    # ─── Всё ок — создаём питомца ───
    # Имя пока не задано — временное
    temp_name = f"__pending_{user_id}_{int(time.time())}"

    pet_id = pet_add(user_id, pet_type, temp_name)

    if pet_id == 0:
        # Ошибка — возврат
        add_balance(user_id, price)
        log_transaction(user_id, user_id, price, "pet_case_error")

        try:
            await edit_target.edit_text(
                f"❌ <b>Ошибка создания питомца</b>\n"
                f"└─ Возврат: +{price:,} msg",
                parse_mode="HTML"
            )
        except Exception:
            pass
        return

    # ─── Сохраняем pet_id для следующего шага ───
    # Юзер введёт имя через /petname
    _pending_pet_names[user_id] = pet_id

    phrase = random.choice(PET_CASE_SUCCESS)

    result_text = (
        f"🐾 <b>Кейс открыт!</b>\n\n"
        f"{phrase}\n\n"
        f"└─ Выпал: {pet_emoji} <b>{pet_type_name}</b>\n"
        f"└─ Списано: {price:,} msg\n\n"
        f"📛 <b>Задай имя питомцу:</b>\n"
        f"└─ <code>/petname [имя]</code>\n"
        f"└─ До 15 символов\n"
        f"└─ Стоимость первого имени: <b>бесплатно</b>"
    )

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="🎁 К кейсам",
            callback_data=f"cases_page_{user_id}_0"
        )]
    ])

    try:
        await edit_target.edit_text(result_text, parse_mode="HTML", reply_markup=kb)
    except Exception:
        pass



# =====================================
#  /promo — активация промокода
# =====================================
@dp.message(Command("promo"))
async def cmd_promo(message: Message):
    log_cmd("🎟️ /promo", message)
    user = message.from_user
    ensure_user(user)

    args = message.text.split()[1:]
    if not args:
        await message.answer(
            "🎟️ <b>Активация промокода</b>\n\n"
            "Использование:\n"
            "└─ <code>/promo КОД</code>\n\n"
            "💡 Промокоды публикуются в канале:\n"
            "└─ @Amina_updates",
            parse_mode="HTML"
        )
        return

    code = args[0].strip()

    ok, msg, reward_type, reward_value = promo_activate(user.id, code)
    if not ok:
        await message.answer(f"❌ {msg}")
        return

    if reward_type == "msg":
        add_balance(user.id, reward_value)
        log_transaction(user.id, user.id, reward_value, "promo")
        reward_text = f"💰 <b>+{reward_value:,}</b> msg"
    elif reward_type == "vip":
        give_vip_days(user.id, reward_value)
        reward_text = f"👑 <b>VIP на {reward_value} дней</b>"
    else:
        reward_text = "?"

    new_balance = get_balance(user.id)

    await message.answer(
        f"🎟️ <b>Промокод активирован!</b>\n\n"
        f"└─ Код: <code>{code.upper()}</code>\n"
        f"└─ Награда: {reward_text}\n"
        f"└─ Баланс: {new_balance:,} msg",
        parse_mode="HTML"
    )

    await log_to_channel(
        f"🎟️ <b>Промокод активирован</b>\n"
        f"└─ Юзер: {user.full_name} (<code>{user.id}</code>)\n"
        f"└─ Код: <code>{code.upper()}</code>\n"
        f"└─ Награда: {reward_type} {reward_value}"
    )



# =====================================
#  /addpromo — создание промокода (владелец)
# =====================================

@dp.message(Command("addpromo"))
async def cmd_addpromo(message: Message):
    log_cmd("🎟️ /addpromo", message)

    if not is_main_owner(message.from_user.id) and not is_owner(message.from_user.id):
        await message.answer("⛔ Только для владельца")
        return

    args = message.text.split()[1:]
    if len(args) < 3:
        await message.answer(
            "❌ Использование:\n"
            "<code>/addpromo КОД ТИП ЗНАЧЕНИЕ [ЛИМИТ]</code>\n\n"
            "Тип:\n"
            "└─ <code>msg</code> — награда в msg\n"
            "└─ <code>vip</code> — награда VIP (дней)\n\n"
            "Примеры:\n"
            "└─ <code>/addpromo NEW2026 msg 5000</code>\n"
            "└─ <code>/addpromo VIPDAY vip 7</code>\n"
            "└─ <code>/addpromo BONUS100 msg 1000 100</code>",
            parse_mode="HTML"
        )
        return

    code = args[0].strip().upper()
    reward_type = args[1].lower().strip()

    if reward_type not in ("msg", "vip"):
        await message.answer("❌ Тип награды: только <code>msg</code> или <code>vip</code>", parse_mode="HTML")
        return

    try:
        reward_value = int(args[2])
        if reward_value <= 0:
            raise ValueError
    except ValueError:
        await message.answer("❌ Значение должно быть положительным числом")
        return

    max_uses = 0
    if len(args) >= 4:
        try:
            max_uses = int(args[3])
            if max_uses < 0:
                max_uses = 0
        except ValueError:
            await message.answer("❌ Лимит должен быть числом")
            return

    ok = promo_create(code, reward_type, reward_value, max_uses)
    if not ok:
        await message.answer(f"❌ Промокод <code>{code}</code> уже существует", parse_mode="HTML")
        return

    limit_text = "∞" if max_uses == 0 else str(max_uses)
    type_text = f"💰 {reward_value:,} msg" if reward_type == "msg" else f"👑 VIP на {reward_value} дн."

    await message.answer(
        f"✅ <b>Промокод создан</b>\n\n"
        f"└─ Код: <code>{code}</code>\n"
        f"└─ Награда: {type_text}\n"
        f"└─ Лимит: {limit_text}",
        parse_mode="HTML"
    )


# =========================================================
#  /delpromo — удалить промокод
# =========================================================

@dp.message(Command("delpromo"))
async def cmd_delpromo(message: Message):
    log_cmd("🗑️ /delpromo", message)

    if not is_main_owner(message.from_user.id) and not is_owner(message.from_user.id):
        await message.answer("⛔ Только для владельца")
        return

    args = message.text.split()[1:]
    if not args:
        await message.answer("❌ Укажи код: <code>/delpromo NEW2026</code>", parse_mode="HTML")
        return

    code = args[0].strip().upper()

    if not promo_delete(code):
        await message.answer(f"❌ Промокод <code>{code}</code> не найден", parse_mode="HTML")
        return

    await message.answer(f"✅ Промокод <code>{code}</code> удалён", parse_mode="HTML")


# =========================================================
#  /promolist — список промокодов
# =========================================================

@dp.message(Command("promolist"))
async def cmd_promolist(message: Message):
    log_cmd("📋 /promolist", message)

    if not is_main_owner(message.from_user.id) and not is_owner(message.from_user.id):
        await message.answer("⛔ Только для владельца")
        return

    rows = promo_list()
    if not rows:
        await message.answer("📭 Промокодов нет")
        return

    lines = ["🎟️ <b>Промокоды:</b>\n"]

    for code, r_type, r_value, max_uses, used, created in rows:
        limit_text = "∞" if max_uses == 0 else str(max_uses)
        type_text = f"💰 {r_value:,} msg" if r_type == "msg" else f"👑 VIP {r_value} дн."

        lines.append(
            f"<code>{code}</code> — {type_text}\n"
            f"└─ Использовано: {used}/{limit_text}"
        )

    await message.answer("\n".join(lines), parse_mode="HTML")

REP_COOLDOWN = timedelta(hours=24)


@dp.message(Command("rep"))
async def cmd_rep(message: Message):
    log_cmd("⭐ /rep", message)
    user = message.from_user
    ensure_user(user)

    args = message.text.split()[1:]
    arg = args[0] if args else None

    # Универсальный поиск: реплай, @username или ID
    target_id, target_name = _find_target_by_arg(message, arg)

    if target_id is None:
        await message.answer(
            "⭐ <b>Репутация</b>\n\n"
            "Использование:\n"
            "└─ Ответь на сообщение: <code>/rep</code>\n"
            "└─ Или: <code>/rep @username</code>\n"
            "└─ Или: <code>/rep [ID]</code>\n\n"
            f"💡 Раз в 2 часа можно дать +1 или -1 к репутации",
            parse_mode="HTML"
        )
        return

    if target_id == user.id:
        await message.answer("❌ Нельзя дать репутацию себе")
        return

    last = get_last_rep(user.id)
    if last:
        try:
            last_dt = datetime.fromisoformat(last)
            elapsed = datetime.now() - last_dt
            if elapsed < REP_COOLDOWN:
                remaining = REP_COOLDOWN - elapsed
                h = remaining.seconds // 3600
                m = (remaining.seconds % 3600) // 60
                await message.answer(
                    f"⏳ <b>Репутацию можно давать раз в 2 часа</b>\n"
                    f"└─ Следующий раз через: <b>{h} ч {m} мин</b>",
                    parse_mode="HTML"
                )
                return
        except ValueError:
            pass

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="👍 +1",
                callback_data=f"rep_plus_{user.id}_{target_id}"
            ),
            InlineKeyboardButton(
                text="👎 -1",
                callback_data=f"rep_minus_{user.id}_{target_id}"
            ),
        ]
    ])

    current_rep = get_reputation(target_id)

    await message.answer(
        f"⭐ <b>Репутация</b>\n\n"
        f"└─ Кому: <b>{target_name}</b>\n"
        f"└─ Текущая: <b>{current_rep}</b>\n\n"
        f"Выбери действие:",
        parse_mode="HTML",
        reply_markup=kb
    )


# =====================================
#  ВСПОМОГАТЕЛЬНОЕ
# =====================================

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


from database import get_next_custom_id   # добавь в импорт air.py, если нет

def ensure_user_by_id(user_id: int):
    from database import get_next_custom_id
    conn = sqlite3.connect("users.db")
    cur = conn.cursor()
    cur.execute("SELECT user_id, custom_id FROM users WHERE user_id = ?", (user_id,))
    row = cur.fetchone()
    if row is None:
        new_id = get_next_custom_id()
        now_iso = datetime.now().isoformat()
        cur.execute(
            "INSERT INTO users (user_id, username, full_name, msg_count, vip_until, last_daily, last_activity, custom_id, registered_at) "
            "VALUES (?, NULL, NULL, 0, NULL, NULL, ?, ?, ?)",
            (user_id, now_iso, new_id, now_iso)
        )
    elif row[1] is None:
        new_id = get_next_custom_id()
        cur.execute(
            "UPDATE users SET custom_id = ?, registered_at = COALESCE(registered_at, ?) WHERE user_id = ?",
            (new_id, datetime.now().isoformat(), user_id)
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

# ====================================
# КЕЙСЫ
# ====================================

CASES = {
    "case": {
        "name": "🎁 Обычный кейс",
        "price": 950,
        "cooldown_normal": 10 * 60,
        "cooldown_vip": 5 * 60,
        "frame_delay": 0.55,
        "msg_range": (800, 1600),
        "tiers": [
            (700, 900, 57.0),
            (900, 1150, 28.0),
            (1150, 1600, 10.0),
        ],
        "vip_chance": 5.0,
        "vip_days": 3,
    },
    "rarecase": {
        "name": "💎 Редкий кейс",
        "price": 4500,
        "cooldown_normal": 30 * 60,
        "cooldown_vip": 15 * 60,
        "frame_delay": 0.55,
        "msg_range": (4300, 8000),
        "tiers": [
            (4300, 5000, 54.0),
            (5000, 6000, 27.0),
            (6000, 8000, 9.0),
        ],
        "vip_chance": 10.0,
        "vip_days": 7,
    },
    "lcase": {
        "name": "👑 Легендарный кейс",
        "price": 24500,
        "cooldown_normal": 60 * 60,
        "cooldown_vip": 30 * 60,
        "frame_delay": 0.6,
        "msg_range": (24000, 31000),
        "tiers": [
            (24000, 25000, 51.0),
            (25000, 27500, 25.5),
            (27500, 31000, 8.5),
        ],
        "vip_chance": 15.0,
        "vip_days": 30,
    },
    "petcase": {
        "name": "🐾 Обычный кейс питомца",
        "price": 4000,
        "cooldown_normal": 0, # без кулдауна
        "cooldown_vip": 0,
        "frame_delay": 0.6,
        "msg_range": (0, 0), #msg не выпадает
        "tiers": [],   # категорий msg нет
        "vip_chance": 0,
        "vip_days": 0,
        "is_pet_case": True,
        "pet_pool": "common",
},
    "petrarecase": {
        "name": "🐾 Редкий кейс питомца",
        "price": 7000,
        "cooldown_normal": 0,
        "cooldown_vip": 0,
        "frame_delay": 0.6,
        "msg_range": (0, 0),
        "tiers": [],
        "vip_chance": 0,
        "vip_days": 0,
        "is_pet_case": True,
        "pet_pool": "rare",
        "vip_only": True,
},
    "weddingcase": {
        "name": "💍 Свадебный кейс",
        "price": 0,                 # бесплатно
        "cooldown_normal": 0,       # кулдаун отдельно (24ч на пару)
        "cooldown_vip": 0,
        "frame_delay": 0.6,
        "msg_range": (0, 0),
        "tiers": [],
        "vip_chance": 0,
        "vip_days": 0,
        "is_wedding_case": True,
},
}


CASE_EMOJIS = [
    "🎁", "🔥", "👋", "🎀", "👜",
    "👛", "🤑", "🤩", "🥳", "💎",
    "💰", "🏆", "⭐", "🎰", "👑",
]

def _render_case_grid() -> str:
    """Возвращает сетку 3×3 из случайных эмодзи (без повторов)."""
    picked = random.sample(CASE_EMOJIS, 9)
    lines = []
    for r in range(3):
        row = picked[r * 3:r * 3 + 3]
        lines.append(" | ".join(row))
    return "\n".join(lines)


def _roll_case_item(case_data: dict) -> tuple:
    """Возвращает (kind, msg_amount, vip_days)."""
    roll = random.random() * 100

    if roll < case_data["vip_chance"]:
        return ("vip", 0, case_data["vip_days"])

    tier_roll = random.random() * 100
    acc = 0.0
    chosen = case_data["tiers"][0]

    for tier in case_data["tiers"]:
        acc += tier[2]
        if tier_roll < acc:
            chosen = tier
            break

    min_msg, max_msg, _chance = chosen
    msg_amount = random.randint(min_msg, max_msg)

    return ("msg", msg_amount, 0)


def _get_case_cooldown_info(user_id: int, case_key: str) -> tuple:
    """
    Возвращает (ready: bool, text: str).
    text — '✅ Готов' или '⏱️ 5 мин 30 сек'
    """
    case_data = CASES[case_key]
    vip = is_vip_active(user_id)
    cooldown_seconds = (
        case_data["cooldown_vip"] if vip else case_data["cooldown_normal"]
    )

    last_open = get_case_cooldown(user_id, case_key)
    if not last_open:
        return True, "✅ Готов к открытию"

    try:
        last_dt = datetime.fromisoformat(last_open)
        elapsed = datetime.now() - last_dt
        cooldown = timedelta(seconds=cooldown_seconds)

        if elapsed >= cooldown:
            return True, "✅ Готов к открытию"

        remaining = cooldown - elapsed
        m = remaining.seconds // 60
        s = remaining.seconds % 60
        time_text = f"{m} мин {s} сек" if m > 0 else f"{s} сек"
        return False, f"⏱️ {time_text}"
    except ValueError:
        return True, "✅ Готов к открытию"

async def _open_case_animation(message, case_key, kind, msg_amount, vip_days, viewer_id):
    case_data = CASES[case_key]
    delay = case_data["frame_delay"]

    msg = await message.answer(
        f"🎁 <b>Крутим…</b>\n\n{_render_case_grid()}",
        parse_mode="HTML"
    )

    for _ in range(2):
        await asyncio.sleep(delay)
        try:
            await msg.edit_text(
                f"🎁 <b>Крутим…</b>\n\n{_render_case_grid()}",
                parse_mode="HTML"
            )
        except Exception:
            pass

    await asyncio.sleep(delay)

    if kind == "vip":
        result_text = (
            f"🎁 <b>КЕЙС ОТКРЫТ!</b>\n\n"
            f"└─ 👑 Выигрыш: <b>VIP на {vip_days} дней</b>"
        )
    else:
        profit = msg_amount - case_data["price"]
        if profit >= 0:
            profit_line = f"└─ Профит: <b>+{profit:,}</b> msg"
        else:
            profit_line = f"└─ Профит: 📉 <b>{profit:,}</b> msg"

        result_text = (
            f"🎁 <b>КЕЙС ОТКРЫТ!</b>\n\n"
            f"└─ Выигрыш: <b>+{msg_amount:,}</b> msg\n"
            f"{profit_line}"
        )

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="🎁 К кейсам",
            callback_data=f"cases_page_{viewer_id}_0"
        )]
    ])

    try:
        await msg.edit_text(result_text, parse_mode="HTML", reply_markup=kb)
    except Exception:
        await message.answer(result_text, parse_mode="HTML", reply_markup=kb)

async def _handle_case_open(message: Message, case_key: str):
    log_cmd(f"🎁 /{case_key}", message)
    user = message.from_user
    ensure_user(user)

    lock = get_user_lock(user.id)
    async with lock:
        case_data = CASES[case_key]
        price = case_data["price"]

        vip = is_vip_active(user.id)
        cooldown_seconds = (
            case_data["cooldown_vip"] if vip else case_data["cooldown_normal"]
        )
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
                f"└─ Нужно: {price:,}\n"
                f"└─ У тебя: {balance:,}\n"
                f"└─ 💡 Не хватает: {missing:,}",
                parse_mode="HTML"
            )
            return

        add_balance(user.id, -price)
        log_transaction(user.id, user.id, -price, "case")
        set_case_cooldown(user.id, case_key)

    kind, msg_amount, vip_days = _roll_case_item(case_data)

    if kind == "vip":
        give_vip_days(user.id, vip_days)
    else:
        add_balance(user.id, msg_amount)

    await _open_case_animation(
        message, case_key, kind, msg_amount, vip_days, user.id
    )

# =====================================
#  /cases — магазин кейсов с пагинацией
# ======================================

CASES_PER_PAGE = 5
CASES_ORDER = ["case", "rarecase", "lcase", "petcase", "petrarecase", "weddingcase"]


def _build_cases_page(user_id: int, page: int) -> tuple:
    """Собирает текст и клавиатуру для страницы /cases."""
    ensure_user_by_id(user_id)

    if page < 0:
        page = 0
    if page >= len(CASES_ORDER):
        page = len(CASES_ORDER) - 1

    case_key = CASES_ORDER[page]
    case_data = CASES[case_key]

    balance = get_balance(user_id)

    is_pet_case = case_data.get("is_pet_case", False)
    is_vip_only = case_data.get("vip_only", False)
    is_wedding_case = case_data.get("is_wedding_case", False)
    is_vip = is_vip_active(user_id)

    # ─── Кулдаун только для игровых кейсов ───
    if not is_pet_case and not is_wedding_case:
        ready, cooldown_text = _get_case_cooldown_info(user_id, case_key)
    else:
        ready, cooldown_text = True, "✅ Готов к открытию"

    emoji = case_data["name"].split()[0]
    name = " ".join(case_data["name"].split()[1:])

    # ═══════════════════════════════════════════
    #  СВАДЕБНЫЙ КЕЙС
    # ═══════════════════════════════════════════
    if is_wedding_case:
        # Пара?
        couple_info = get_couple_info(user_id)

        # Кулдаун пары
        last_case = wedding_case_get_cooldown(user_id) if couple_info.get("ok") else None
        ready_w = True
        cooldown_text_w = "✅ Готов к открытию"
        if last_case:
            try:
                last_dt = datetime.fromisoformat(last_case)
                elapsed = datetime.now() - last_dt
                if elapsed < timedelta(hours=24):
                    ready_w = False
                    remaining = timedelta(hours=24) - elapsed
                    h = remaining.seconds // 3600
                    m = (remaining.seconds % 3600) // 60
                    cooldown_text_w = f"⏱️ {h}ч {m}м"
            except ValueError:
                pass

        # Призы
        prizes_lines = [
            "└─ 💰 1 000–5 000 msg — 40%",
            "└─ 💰 10 000–20 000 msg — 20%",
            "└─ 💎 20 000–50 000 msg — 10%",
            "└─ 👑 VIP 14 дней — 20%",
            "└─ 👑 VIP 28 дней — 10%",
        ]
        prizes_block = "\n".join(prizes_lines)

        if not couple_info.get("ok"):
            # Не в браке
            text = (
                f"{emoji} <b>{name}</b>\n"
                f"\n"
                f"❌ <b>Только для пар</b>\n"
                f"└─ Жениться: <code>/marry @user</code>\n"
                f"\n"
                f"📊 <b>Что может выпасть:</b>\n"
                f"{prizes_block}"
            )
            kb_rows = [[InlineKeyboardButton(
                text="◀️ К кейсам",
                callback_data=f"cases_page_{user_id}_0"
            )]]
        else:
            # Пара есть
            u1 = couple_info["user1_id"]
            u2 = couple_info["user2_id"]
            name1 = _couple_name(u1)
            name2 = _couple_name(u2)

            text = (
                f"{emoji} <b>{name}</b>\n"
                f"\n"
                f"💍 Пара: {name1} 💕 {name2}\n"
                f"└─ Общий счёт: <b>{couple_info['balance']:,}</b> msg\n"
                f"└─ Цена: <b>бесплатно</b>\n"
                f"└─ Кулдаун: <b>24 часа</b> на пару\n"
                f"\n"
                f"📊 <b>Что может выпасть:</b>\n"
                f"{prizes_block}\n"
                f"\n"
                f"⏳ Статус: {cooldown_text_w}"
            )

            btn_text = f"{emoji} Открыть (бесплатно)"
            kb_rows = [[InlineKeyboardButton(
                text=btn_text,
                callback_data=f"case_buy_{user_id}_weddingcase"
            )]]

    # ═══════════════════════════════════════════
    #  ПИТОМЦЫ
    # ═══════════════════════════════════════════
    elif is_pet_case:
        pool_name = "common" if case_data["pet_pool"] == "common" else "rare"
        pool = PET_COMMON_CASE if pool_name == "common" else PET_RARE_CASE

        pet_lines = []
        for ptype, chance in pool.items():
            pet_emoji, pet_name, _ = PET_TYPES.get(ptype, ("❓", "?", "common"))
            pet_lines.append(f"└─ {pet_emoji} {pet_name} — {chance}%")

        pool_block = "\n".join(pet_lines)

        pet_slots = PET_LIMIT_VIP if is_vip else PET_LIMIT_NORMAL
        current_pets = pet_count(user_id)

        text = (
            f"{emoji} <b>{name}</b>\n"
            f"\n"
            f"💰 Баланс: <b>{balance:,}</b> msg\n"
            f"\n"
            f"└─ Цена: <b>{case_data['price']:,}</b> msg\n"
            f"└─ Питомцы: <b>{current_pets}/{pet_slots}</b>\n"
        )

        if is_vip_only:
            vip_mark = " ✅" if is_vip else " ❌"
            text += f"└─ Только VIP:{vip_mark}\n"

        text += (
            f"\n"
            f"📊 <b>Что может выпасть:</b>\n"
            f"{pool_block}\n"
            f"\n"
            f"💡 Если питомец уже есть — вернём msg"
        )

        btn_emoji = emoji
        btn_text = f"{btn_emoji} Открыть ({case_data['price']:,})"
        kb_rows = [[InlineKeyboardButton(
            text=btn_text,
            callback_data=f"case_buy_{user_id}_{case_key}"
        )]]

    # ═══════════════════════════════════════════
    #  ИГРОВЫЕ КЕЙСЫ
    # ═══════════════════════════════════════════
    else:
        tier_emojis = ["🥉", "🥈", "🥇"]
        tiers_lines = []
        for i, (t_min, t_max, chance) in enumerate(case_data["tiers"]):
            emoji_tier = tier_emojis[i] if i < len(tier_emojis) else "🎖️"
            chance_text = f"{chance:g}%"
            tiers_lines.append(
                f"└─ {emoji_tier} {t_min:,}–{t_max:,} ({chance_text})"
            )

        vip_chance = case_data["vip_chance"]
        vip_days = case_data["vip_days"]
        tiers_lines.append(
            f"└─ 👑 VIP {vip_days} дн. ({vip_chance:g}%)"
        )
        tiers_block = "\n".join(tiers_lines)

        text = (
            f"{emoji} <b>{name}</b>\n"
            f"\n"
            f"💰 Баланс: <b>{balance:,}</b> msg\n"
            f"\n"
            f"└─ Цена: <b>{case_data['price']:,}</b> msg\n"
            f"└─ Кулдаун: <b>{case_data['cooldown_normal'] // 60} мин</b>\n"
            f"\n"
            f"📊 <b>Категории выигрыша:</b>\n"
            f"{tiers_block}\n"
            f"\n"
            f"⏳ Статус: {cooldown_text}"
        )

        kb_rows = [[InlineKeyboardButton(
            text=f"{emoji} Крутить ({case_data['price']:,})",
            callback_data=f"case_buy_{user_id}_{case_key}"
        )]]

    # ═══════════════════════════════════════════
    #  НАВИГАЦИЯ (по 3 кнопки в ряд)
    # ═══════════════════════════════════════════
    nav_buttons = []
    for p in range(len(CASES_ORDER)):
        if p == page:
            nav_buttons.append(InlineKeyboardButton(
                text=f"• {p + 1} •",
                callback_data="cases_noop"
            ))
        else:
            nav_buttons.append(InlineKeyboardButton(
                text=f"{p + 1}",
                callback_data=f"cases_page_{user_id}_{p}"
            ))

    for i in range(0, len(nav_buttons), 3):
        kb_rows.append(nav_buttons[i:i + 3])

    kb = InlineKeyboardMarkup(inline_keyboard=kb_rows)
    return text, kb
# =======================================
#  /photo — получить file_id
# =====================================

@dp.message(Command("photo"))
async def cmd_photo(message: Message):
    log_cmd("📷 /photo", message)
    user_id = message.from_user.id

    # Только владелец
    if not is_main_owner(user_id) and not is_owner(user_id):
        return

    # Ищем медиа: reply → forward → само сообщение
    target_msg = message.reply_to_message if message.reply_to_message else message

    # ─── Фото ───
    if target_msg.photo:
        photo = target_msg.photo[-1]
        await message.answer(
            f"📷 <b>Фото</b>\n\n"
            f"<code>{photo.file_id}</code>",
            parse_mode="HTML"
        )
        return

    # ─── Видео ───
    if target_msg.video:
        video = target_msg.video
        await message.answer(
            f"🎬 <b>Видео</b>\n\n"
            f"<code>{video.file_id}</code>",
            parse_mode="HTML"
        )
        return

    # ─── Документ ───
    if target_msg.document:
        doc = target_msg.document
        await message.answer(
            f"📎 <b>Документ</b>\n\n"
            f"<code>{doc.file_id}</code>",
            parse_mode="HTML"
        )
        return

    # ─── GIF / Анимация ───
    if target_msg.animation:
        anim = target_msg.animation
        await message.answer(
            f"🎞️ <b>GIF</b>\n\n"
            f"<code>{anim.file_id}</code>",
            parse_mode="HTML"
        )
        return

    # ─── Стикер ───
    if target_msg.sticker:
        sticker = target_msg.sticker
        await message.answer(
            f"🎨 <b>Стикер</b>\n\n"
            f"<code>{sticker.file_id}</code>",
            parse_mode="HTML"
        )
        return

    # ─── Аудио ───
    if target_msg.audio:
        audio = target_msg.audio
        await message.answer(
            f"🎵 <b>Аудио</b>\n\n"
            f"<code>{audio.file_id}</code>",
            parse_mode="HTML"
        )
        return

    # ─── Ничего не найдено ───
    await message.answer(
        "❌ <b>Медиа не найдено</b>\n\n"
        "Как пользоваться:\n"
        "└─ Отправь фото/видео и напиши <code>/photo</code>\n"
        "└─ Или ответь на сообщение с медиа и напиши <code>/photo</code>",
        parse_mode="HTML"
    )



@dp.message(Command("cases"))
async def cmd_cases(message: Message):
    log_cmd("🎁 /cases", message)
    user = message.from_user
    ensure_user(user)

    text, kb = _build_cases_page(user.id, 0)

    await message.answer(
        text, parse_mode="HTML", reply_markup=kb,
        reply_to_message_id=message.message_id
    )


@dp.callback_query(F.data.startswith("cases_page_"))
async def cb_cases_page(callback: CallbackQuery):
    parts = callback.data.split("_")
    if len(parts) != 4:
        await callback.answer("⚠️ Ошибка данных", show_alert=True)
        return

    try:
        owner_id = int(parts[2])
        page = int(parts[3])
    except ValueError:
        await callback.answer("⚠️ Ошибка данных", show_alert=True)
        return

    if callback.from_user.id != owner_id:
        await callback.answer("❌ Это не для тебя", show_alert=True)
        return

    text, kb = _build_cases_page(owner_id, page)

    try:
        await callback.message.edit_text(
            text, parse_mode="HTML", reply_markup=kb
        )
    except Exception as e:
        print(f"[CASES] Ошибка: {e}")
    await callback.answer()


@dp.callback_query(F.data == "cases_noop")
async def cb_cases_noop(callback: CallbackQuery):
    await callback.answer()


@dp.callback_query(F.data.startswith("case_buy_"))
async def cb_case_buy(callback: CallbackQuery):
    parts = callback.data.split("_")
    # case_buy_{user_id}_{case_key}
    if len(parts) != 4:
        await callback.answer("⚠️ Ошибка данных", show_alert=True)
        return

    try:
        owner_id = int(parts[2])
    except ValueError:
        await callback.answer("⚠️ Ошибка данных", show_alert=True)
        return

    case_key = parts[3]

    if case_key not in CASES:
        await callback.answer("⚠️ Кейс не найден", show_alert=True)
        return

    if callback.from_user.id != owner_id:
        await callback.answer("❌ Это не для тебя", show_alert=True)
        return

    user = callback.from_user
    ensure_user(user)

    case_data = CASES[case_key]
    price = case_data["price"]

    is_pet_case = case_data.get("is_pet_case", False)
    is_vip_only = case_data.get("vip_only", False)
    is_wedding_case = case_data.get("is_wedding_case", False)
    is_vip = is_vip_active(owner_id)

    # ─── Проверка VIP ───
    if is_vip_only and not is_vip:
        await callback.answer(
            "👑 Только для VIP! Купи VIP: /buyvip",
            show_alert=True
        )
        return

    # ─── Свадебный кейс ───
    if is_wedding_case:
        couple_info = get_couple_info(owner_id)
        if not couple_info.get("ok"):
            await callback.answer(
                "❌ Кейс только для пар! /marry",
                show_alert=True
            )
            return

        # Кулдаун
        last_case = wedding_case_get_cooldown(owner_id)
        if last_case:
            try:
                last_dt = datetime.fromisoformat(last_case)
                elapsed = datetime.now() - last_dt
                if elapsed < timedelta(hours=24):
                    remaining = timedelta(hours=24) - elapsed
                    h = remaining.seconds // 3600
                    m = (remaining.seconds % 3600) // 60
                    await callback.answer(
                        f"⏳ Свадебный кейс на перезарядке: {h}ч {m}м",
                        show_alert=True
                    )
                    return
            except ValueError:
                pass

        await callback.answer("💍 Крутим…")
        await _wedding_case_animation(callback.message, owner_id, couple_info)
        return

    # ─── Кулдаун (только для игровых кейсов) ───
    if not is_pet_case:
        ready, cooldown_text = _get_case_cooldown_info(owner_id, case_key)
        if not ready:
            await callback.answer(
                f"⏳ Кейс на перезарядке: {cooldown_text.replace('⏱️ ', '')}",
                show_alert=True
            )
            return

    # ─── Баланс ───
    balance = get_balance(owner_id)
    if balance < price:
        await callback.answer(
            f"😢 Недостаточно msg! Нужно: {price:,}, у тебя: {balance:,}",
            show_alert=True
        )
        return

    # ─── Списываем ───
    add_balance(owner_id, -price)
    log_transaction(owner_id, owner_id, -price, "case")

    if not is_pet_case:
        set_case_cooldown(owner_id, case_key)

    await callback.answer()

    # ─── Открываем ───
    if is_pet_case:
        await _pet_case_animation(callback.message, case_data, owner_id)
    else:
        # ─── Игровой кейс (старая логика) ───
        kind, msg_amount, vip_days = _roll_case_item(case_data)

        if kind == "vip":
            give_vip_days(owner_id, vip_days)
        else:
            add_balance(owner_id, msg_amount)

        delay = case_data["frame_delay"]

        try:
            await callback.message.edit_text(
                f"🎁 <b>Крутим…</b>\n\n{_render_case_grid()}",
                parse_mode="HTML"
            )
        except Exception:
            pass

        for _ in range(2):
            await asyncio.sleep(delay)
            try:
                await callback.message.edit_text(
                    f"🎁 <b>Крутим…</b>\n\n{_render_case_grid()}",
                    parse_mode="HTML"
                )
            except Exception:
                pass

        await asyncio.sleep(delay)

        if kind == "vip":
            result_text = (
                f"🎁 <b>КЕЙС ОТКРЫТ!</b>\n\n"
                f"└─ 👑 Выигрыш: <b>VIP на {vip_days} дней</b>"
            )
        else:
            profit = msg_amount - case_data["price"]
            if profit >= 0:
                profit_line = f"└─ Профит: <b>+{profit:,}</b> msg"
            else:
                profit_line = f"└─ Профит: 📉 <b>{profit:,}</b> msg"

            result_text = (
                f"🎁 <b>КЕЙС ОТКРЫТ!</b>\n\n"
                f"└─ Выигрыш: <b>+{msg_amount:,}</b> msg\n"
                f"{profit_line}"
            )

        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text="🎁 К кейсам",
                callback_data=f"cases_page_{owner_id}_0"
            )]
        ])

        try:
            await callback.message.edit_text(
                result_text, parse_mode="HTML", reply_markup=kb
            )
        except Exception:
            pass

    await _check_and_notify_achievements(owner_id, callback.message.chat.id)

# =====================================
#  СВАДЕБНЫЙ КЕЙС — анимация и призы
# =====================================

WEDDING_CASE_EMOJIS = ["💍", "💕", "🎁", "🎉", "💐", "🥂", "💖", "✨", "🌹", "💎"]


def _render_wedding_grid() -> str:
    """Сетка 3×3 из свадебных эмодзи (без повторов)."""
    picked = random.sample(WEDDING_CASE_EMOJIS, 9)
    lines = []
    for r in range(3):
        row = picked[r * 3:r * 3 + 3]
        lines.append(" | ".join(row))
    return "\n".join(lines)


def _roll_wedding_prize() -> dict:
    """
    Возвращает приз:
    {
        "kind": "msg" | "vip",
        "amount": int,      # для msg
        "vip_days": int,    # для vip
        "phrase": str,
    }
    Шансы:
      40% — 1000–5000 msg
      20% — 10 000–20 000 msg
      10% — 20 000–50 000 msg
      20% — VIP 14 дней
      10% — VIP 28 дней
    """
    roll = random.random() * 100

    if roll < 40:
        amount = random.randint(1000, 5000)
        return {
            "kind": "msg",
            "amount": amount,
            "vip_days": 0,
            "phrase": random.choice([
                "💕 Нежный подарок для пары!",
                "💐 Немного романтики!",
                "🌹 Приятный сюрприз!",
            ]),
        }
    elif roll < 60:
        amount = random.randint(10_000, 20_000)
        return {
            "kind": "msg",
            "amount": amount,
            "vip_days": 0,
            "phrase": random.choice([
                "💰 Щедрый подарок!",
                "✨ Отличный улов!",
                "💎 Блестяще!",
            ]),
        }
    elif roll < 70:
        amount = random.randint(20_000, 50_000)
        return {
            "kind": "msg",
            "amount": amount,
            "vip_days": 0,
            "phrase": random.choice([
                "🎉 ДЖЕКПОТ! Огромный подарок!",
                "🔥 Вот это удача!",
                "💎 Бриллиантовая свадьба!",
            ]),
        }
    elif roll < 90:
        return {
            "kind": "vip",
            "amount": 0,
            "vip_days": 14,
            "phrase": "👑 VIP на 14 дней каждому!",
        }
    else:
        return {
            "kind": "vip",
            "amount": 0,
            "vip_days": 28,
            "phrase": "👑 VIP на 28 дней каждому!",
        }


async def _wedding_case_animation(edit_target, user_id: int, couple_info: dict):
    """
    Анимация свадебного кейса.
    edit_target — Message (для callback).
    """
    delay = 0.6

    # ─── 3 кадра анимации ───
    for _ in range(3):
        try:
            await edit_target.edit_text(
                f"💍 <b>Открываем свадебный кейс…</b>\n\n{_render_wedding_grid()}",
                parse_mode="HTML"
            )
        except Exception:
            pass
        await asyncio.sleep(delay)

    # ─── Результат ───
    prize = _roll_wedding_prize()

    u1 = couple_info["user1_id"]
    u2 = couple_info["user2_id"]
    name1 = _couple_name(u1)
    name2 = _couple_name(u2)

    # Выдаём награду
    if prize["kind"] == "msg":
        amount = prize["amount"]
        add_balance(u1, amount)  # зачисляется в общий счёт пары (т.к. married)
        log_transaction(BOT_TREASURY_ID, u1, amount, "wedding_case_msg")

        result_text = (
            f"🎉 <b>Свадебный кейс открыт!</b>\n\n"
            f"💍 {name1} 💕 {name2}\n\n"
            f"{prize['phrase']}\n\n"
            f"💰 Пара получила: <b>+{amount:,}</b> msg\n"
            f"└─ В общий счёт\n"
        )
    else:
        days = prize["vip_days"]
        give_vip_days(u1, days)
        give_vip_days(u2, days)

        result_text = (
            f"🎉 <b>Свадебный кейс открыт!</b>\n\n"
            f"💍 {name1} 💕 {name2}\n\n"
            f"{prize['phrase']}\n\n"
            f"👑 VIP на <b>{days} дней</b> каждому\n"
        )

    # Ставим кулдаун
    wedding_case_set_cooldown(user_id)

    # Кнопка возврата в /cases
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="🎁 К кейсам",
            callback_data=f"cases_page_{user_id}_0"
        )]
    ])

    try:
        await edit_target.edit_text(result_text, parse_mode="HTML", reply_markup=kb)
    except Exception:
        pass

    # Уведомление супругу (если открыл не он)
    spouse_id = u2 if user_id == u1 else u1
    if spouse_id != user_id:
        try:
            await bot.send_message(
                spouse_id,
                f"💍 <b>Твоя пара открыла свадебный кейс!</b>\n\n"
                f"└─ {prize['phrase']}\n"
                f"└─ Проверь: /couple",
                parse_mode="HTML"
            )
        except Exception:
            pass

# ====================================
#  /case, /rarecase, /lcase
# =====================================
@dp.message(Command("case"))
async def cmd_case(message: Message):
    await _handle_case_open(message, "case")

@dp.message(Command("rarecase"))
async def cmd_rarecase(message: Message):
    await _handle_case_open(message, "rarecase")

@dp.message(Command("lcase"))
async def cmd_lcase(message: Message):
    await _handle_case_open(message, "lcase")





# =====================================
#  БРАК
# =====================================

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

    # Премиум-эмодзи: только если И смотрящий, И цель — VIP
    use_premium = is_vip_active(target_id) and is_vip_active(viewer_id)

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

    kb_rows = []

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
            kb_rows.append([InlineKeyboardButton(
                text="🎁 Бонус", callback_data="prof_daily"
            )])

    # ─── Навигация (снизу) ───
    kb_rows.append(nav_row)

    kb = InlineKeyboardMarkup(inline_keyboard=kb_rows)

    # ═══════════════════════════════════════════
    #  СТРАНИЦА 0 — ОСНОВНОЕ + БАНК
    # ═══════════════════════════════════════════
    if page == 0:
        nick, _ = get_nick(uid)
        display_name = nick or fname
        lvl = get_user_level(uid)
        rep = get_reputation(uid)

        bank_info = bank_get(uid)

        E_USER  = _pr(use_premium, "user")
        E_MONEY = _pr(use_premium, "money")
        E_BANK  = _pr(use_premium, "bank")
        E_STAR  = _pr(use_premium, "star")
        E_LEVEL = _pr(use_premium, "level")

        text = (
            f"{E_USER} <b>{fname}</b> | <code>{uid}</code>\n"
            f"{E_MONEY} Баланс: <b>{balance:,}</b> msg\n"
            f"{E_BANK} Банк: <b>{bank_info['balance']:,}</b> msg\n"
            f"👻 Имя: <b>{display_name}</b>\n"
            f"{E_STAR} Репутация: <b>{rep}</b>\n"
            f"\n"
            f"{E_LEVEL} Уровень: <b>{lvl['level']}</b> — {lvl['title']}\n"
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

        E_VIP  = _pr(use_premium, "vip")
        E_GIFT = _pr(use_premium, "gift")
        E_FIRE = _pr(use_premium, "fire")
        E_WARN = _pr(use_premium, "warn")

        if warn_count >= WARN_LIMIT:
            warn_line = f"\n{E_WARN} Варны: <b>{warn_count}/{WARN_LIMIT}</b> (лимит!)"
        elif warn_count > 0:
            warn_line = f"\n{E_WARN} Варны: <b>{warn_count}/{WARN_LIMIT}</b>"
        else:
            warn_line = ""

        text = (
            f"▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰\n"
            f"{E_VIP} <b>СТАТУС</b>\n"
            f"▱▱▱▱▱▱▱▱▱▱▱▱▱▱▱▱▱\n\n"
            f"{E_VIP} VIP: <b>{vip_line}</b>\n"
            f"{E_GIFT} /daily: <b>{daily_line}</b>\n"
            f"{E_FIRE} Streak: <b>{streak}/7</b>"
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

        E_TROPHY = _pr(use_premium, "trophy")
        E_MEDAL  = _pr(use_premium, "medal")

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
            next_block = f"\n\n{E_TROPHY} <b>Все достижения открыты!</b>"

        text = (
            f"▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰\n"
            f"{E_TROPHY} <b>ПРОГРЕСС</b>\n"
            f"▱▱▱▱▱▱▱▱▱▱▱▱▱▱▱▱▱\n\n"
            f"{E_TROPHY} Место в топе: <b>#{rank}</b>\n"
            f"{E_MEDAL} Достижения: <b>{ach_count}/{len(ACHIEVEMENTS)}</b>\n"
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
    """Собирает главный экран /bank."""
    bank_ensure(user_id)
    info = bank_get(user_id)
    vip = is_vip_active(user_id)
    rate = 0.02 if vip else 0.01
    rate_text = "2%" if vip else "1%"

    # ─── Премиум только для VIP ───
    def e(emoji_id, fallback):
        return _p(emoji_id, fallback) if vip else fallback

    E_BANK  = e(PREM_BANK, "🏦")
    E_MONEY = e(PREM_MONEY, "💰")
    E_RATE  = e(PREM_RATE, "📈")

    vip_mark = f' {_p(PREM_TOP1, "👑")}' if vip else ""

    balance = info["balance"]
    total_earned = info["total_earned"]
    earned_now = info["earned_now"]

    # ─── Прогноз на 10ч и 24ч (сложный процент) ───
    if balance > 0:
        forecast_10h = int(balance * ((1 + rate) ** 10 - 1))
        forecast_24h = int(balance * ((1 + rate) ** 24 - 1))
    else:
        forecast_10h = 0
        forecast_24h = 0

    # ─── Время до начисления ───
    now_kr = datetime.now(timezone(timedelta(hours=7))).replace(tzinfo=None)
    minutes_passed = now_kr.minute
    minutes_left = 60 - minutes_passed
    if minutes_left == 60:
        minutes_left = 0

    # Прогресс-бар (10 сегментов)
    filled = int((minutes_passed / 60) * 10)
    if filled > 10:
        filled = 10
    bar = "▰" * filled + "▱" * (10 - filled)

    # ─── Место в топе банков ───
    try:
        conn = sqlite3.connect("users.db")
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM banks WHERE balance > ?", (balance,))
        rank = cur.fetchone()[0] + 1
        conn.close()

        if rank == 1:
            rank_line = f"└─ 🥇 <b>Ты в топе банков!</b>"
        else:
            rank_line = f"└─ 🏆 Место в топе: <b>#{rank}</b>"
    except Exception:
        rank_line = ""

    # ─── Сборка текста ───
    lines = [
        f"{E_BANK} <b>Твой банк</b>{vip_mark}",
        "",
        f"└─ {E_MONEY} На счету: <b>{balance:,}</b> msg",
        f"└─ {E_RATE} Ставка: <b>{rate_text} в час</b>",
        "",
    ]

    if balance > 0:
        lines.append(f"📊 <b>Прогноз:</b>")
        lines.append(f"└─ За 10ч: <b>+{forecast_10h:,}</b> msg")
        lines.append(f"└─ За 24ч: <b>+{forecast_24h:,}</b> msg")
        lines.append("")

    lines.append(f"⏳ <b>До начисления:</b> {minutes_left} мин")
    lines.append(f"{bar}")

    if earned_now > 0:
        lines.append("")
        lines.append(f"💵 Начислено сейчас: <b>+{earned_now:,}</b> msg")

    if total_earned > 0:
        lines.append("")
        lines.append(f"✅ Всего заработано: <b>{total_earned:,}</b> msg")

    if rank_line:
        lines.append("")
        lines.append(rank_line)

    text = "\n".join(lines)

    # ─── Кнопки ───
    kb_rows = []

    wallet = get_balance(user_id)
    if wallet > 0:
        kb_rows.append([
            InlineKeyboardButton(
                text="📥 Положить",
                callback_data=f"bank_add_{user_id}"
            ),
            InlineKeyboardButton(
                text=f"📤 Снять всё",
                callback_data=f"bank_take_all_{user_id}"
            ),
        ])
    elif balance > 0:
        kb_rows.append([
            InlineKeyboardButton(
                text=f"📤 Снять всё ({balance:,})",
                callback_data=f"bank_take_all_{user_id}"
            ),
        ])

    kb = InlineKeyboardMarkup(inline_keyboard=kb_rows)
    return text, kb

# ======================================
#  КОНСТАНТЫ
# =====================================
# Для напоминаний о daily
_last_chat_ids: dict[int, int] = {}
_daily_notified: set[int] = set() 
DAILY_AMOUNT = 500
DAILY_VIP_AMOUNT = 2000
DAILY_COOLDOWN = timedelta(hours=24)
DAILY_STREAK_RESET = timedelta(hours=27)

ROB_COOLDOWN = timedelta(hours=1)
ROB_COOLDOWN_VIP = timedelta(minutes=30)
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
#  ПОДАРОК ПАРЕ (по ссылке ?start=gift_<u1>_<u2>)
# =====================================

COUPLE_GIFT_AMOUNTS = [1000, 5000, 10000, 50000, 100000, 500000]


def _short_gift_amount(n: int) -> str:
    """1000 → 1к, 500000 → 500к, 1000000 → 1млн."""
    if n >= 1_000_000:
        return f"{n // 1_000_000}млн"
    if n >= 1_000:
        return f"{n // 1_000}к"
    return str(n)


def _couple_gift_kb(g_u1: int, g_u2: int, viewer_id: int) -> InlineKeyboardMarkup:
    """Клавиатура выбора суммы подарка: 3 в ряд."""
    rows = []
    row = []
    for amount in COUPLE_GIFT_AMOUNTS:
        row.append(InlineKeyboardButton(
            text=f"{_short_gift_amount(amount)}",
            callback_data=f"cgift_{g_u1}_{g_u2}_{amount}_{viewer_id}"
        ))
        if len(row) == 3:
            rows.append(row)
            row = []
    if row:
        rows.append(row)

    return InlineKeyboardMarkup(inline_keyboard=rows)


async def _show_couple_gift_menu(message: Message, viewer_id: int, g_u1: int, g_u2: int):
    """Показывает меню подарка паре."""
    name1 = _couple_name(g_u1)
    name2 = _couple_name(g_u2)

    balance = get_balance(viewer_id)

    await message.answer(
        f"💐 <b>Поздравить пару</b>\n\n"
        f"└─ {name1} 💕 {name2}\n"
        f"└─ Твой баланс: <b>{balance:,}</b> msg\n\n"
        f"<b>Сколько хотите подарить?</b>\n"
        f"💡 Подарок идёт в общий счёт пары",
        parse_mode="HTML",
        reply_markup=_couple_gift_kb(g_u1, g_u2, viewer_id)
    )


@dp.callback_query(F.data.startswith("cgift_"))
async def cb_couple_gift(callback: CallbackQuery):
    # Формат: cgift_{u1}_{u2}_{amount}_{viewer}
    parts = callback.data.split("_")
    if len(parts) != 5:
        await callback.answer("⚠️ Ошибка данных", show_alert=True)
        return

    try:
        g_u1 = int(parts[1])
        g_u2 = int(parts[2])
        amount = int(parts[3])
        viewer_id = int(parts[4])
    except ValueError:
        await callback.answer("⚠️ Ошибка данных", show_alert=True)
        return

    if callback.from_user.id != viewer_id:
        await callback.answer("❌ Это не для тебя", show_alert=True)
        return

    # Проверка: пара всё ещё в браке?
    marriage = get_marriage(g_u1)
    if not marriage:
        await callback.answer(
            "❌ Эта пара больше не вместе",
            show_alert=True
        )
        return

    _, u1, u2, _ = marriage
    if set([u1, u2]) != set([g_u1, g_u2]):
        await callback.answer(
            "❌ Эта пара больше не вместе",
            show_alert=True
        )
        return

    # Нельзя дарить своей же паре
    if viewer_id in (g_u1, g_u2):
        await callback.answer(
            "😄 Нельзя дарить своей же паре",
            show_alert=True
        )
        return

    # Проверка баланса
    balance = get_balance(viewer_id)
    if balance < amount:
        await callback.answer(
            f"😢 Недостаточно msg!\nНужно: {amount:,}, у тебя: {balance:,}",
            show_alert=True
        )
        return

    # Списываем и зачисляем паре
    ok, info, new_balance = gift_to_couple(viewer_id, g_u1, amount)
    if not ok:
        await callback.answer(f"❌ {info}", show_alert=True)
        return

    name1 = _couple_name(g_u1)
    name2 = _couple_name(g_u2)
    giver_name = _couple_name(viewer_id)

    try:
        await callback.message.edit_text(
            f"🎁 <b>Подарок отправлен!</b>\n\n"
            f"└─ Паре: {name1} 💕 {name2}\n"
            f"└─ Сумма: <b>+{amount:,}</b> msg\n"
            f"└─ В общий счёт пары\n\n"
            f"💡 {name1} и {name2} получили уведомление",
            parse_mode="HTML"
        )
    except Exception:
        pass

    # Уведомления обоим супругам
    for spouse_id in (g_u1, g_u2):
        if spouse_id == viewer_id:
            continue
        try:
            await bot.send_message(
                spouse_id,
                f"💐 <b>Подарок вашей паре!</b>\n\n"
                f"└─ От: {giver_name}\n"
                f"└─ Сумма: <b>+{amount:,}</b> msg\n"
                f"└─ Общий счёт: <b>{new_balance:,}</b> msg",
                parse_mode="HTML"
            )
        except Exception:
            pass

    await log_to_channel(
        f"💐 <b>Подарок паре</b>\n"
        f"└─ От: {giver_name} (<code>{viewer_id}</code>)\n"
        f"└─ Паре: {name1} 💕 {name2}\n"
        f"└─ Сумма: <b>{amount:,}</b> msg"
    )

    await callback.answer(f"🎁 +{amount:,} msg паре")


# =====================================
#  /start
# =====================================
START_PHOTO = "AgACAgIAAxkBAAIMWWrOF8WYyyI6YFFdt1voAAGprg0H-AACNB9rG471cUotKqhmO_sDxAEAAwIAA3gAAz0E"
MINI_APP_URL = "https://bot-1793373292-4868-ayzen.bothost.tech/"
CHANNEL_URL = "https://t.me/Amina_updates"

@dp.message(Command("start"))
async def cmd_start(message: Message):
    log_cmd("🚀 /start", message)
    user = message.from_user
    ensure_user(user)
    balance = get_balance(user.id)

    GREET = _p(PREM_BONUS, "👋")
    MONEY = _p(PREM_MONEY, "💰")
    GIFT  = _p(PREM_GIFT, "🎁")
    USERS = _p(PREM_USERS, "👥")

    args = message.text.split()

    # ─── Подарок паре (gift_<u1>_<u2>) ───
    if len(args) > 1 and args[1].startswith("gift_"):
        payload = args[1].replace("gift_", "")
        parts_payload = payload.split("_")

        if len(parts_payload) == 2:
            try:
                g_u1 = int(parts_payload[0])
                g_u2 = int(parts_payload[1])
            except ValueError:
                g_u1 = g_u2 = None

            if g_u1 and g_u2:
                marriage = get_marriage(g_u1)
                pair_ok = False
                if marriage:
                    _, u1, u2, _ = marriage
                    if set([u1, u2]) == set([g_u1, g_u2]):
                        pair_ok = True

                if not pair_ok:
                    await message.answer("❌ <b>Эта пара больше не вместе</b>", parse_mode="HTML")
                    return

                if user.id in (g_u1, g_u2):
                    await message.answer("😄 <b>Нельзя дарить своей же паре</b>", parse_mode="HTML")
                    return

                await _show_couple_gift_menu(message, user.id, g_u1, g_u2)
                return

    # ─── Реферальная ссылка (ref<id>) ───
    referrer_id = None
    is_new_referral = False

    if len(args) > 1 and args[1].startswith("ref"):
        try:
            referrer_id = int(args[1].replace("ref", ""))
        except ValueError:
            referrer_id = None

    if referrer_id and referrer_id != user.id:
        existing_referrer = get_referrer(user.id)
        is_new = (balance == 0 and existing_referrer is None)

        if is_new and not get_active_ban(referrer_id):
            ref_data = get_user(referrer_id)
            if ref_data:
                ok = set_referrer(user.id, referrer_id)
                if ok:
                    is_new_referral = True
                    add_balance(user.id, REFERRAL_REWARD)
                    give_vip_days(user.id, REFERRAL_VIP_DAYS)
                    log_transaction(referrer_id, user.id, REFERRAL_REWARD, "referral_bonus")

                    try:
                        ref_name = user.full_name
                        await bot.send_message(
                            referrer_id,
                            f"{USERS} <b>По твоей ссылке зарегистрировался</b>\n"
                            f"└─ <b>{ref_name}</b>\n\n"
                            f"{GIFT} Награда: <b>+{REFERRER_REWARD}</b> msg придёт после "
                            f"<b>{REFERRAL_THRESHOLD}</b> сообщений реферала",
                            parse_mode="HTML"
                        )
                    except Exception:
                        pass

    # ─── Кнопки (только Канал и Mini App) ───
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="🚀 Открыть приложение",
                web_app=WebAppInfo(url=MINI_APP_URL)
            )
        ],
        [
            InlineKeyboardButton(
                text="📢 Наш канал",
                url=CHANNEL_URL
            )
        ],
    ])

    # ─── Формируем текст ───
    if is_new_referral:
        text = (
            f"{GREET} Привет, <b>{user.full_name}</b>!\n\n"
            f"{GIFT} Ты пришёл по реферальной ссылке!\n"
            f"└─ Бонус: <b>+{REFERRAL_REWARD}</b> msg\n"
            f"└─ VIP на <b>{REFERRAL_VIP_DAYS}</b> день\n\n"
            f"{MONEY} Твой баланс: <b>{get_balance(user.id):,}</b> msg\n\n"
            f"🚀 Открой Mini App, чтобы крутить колесо и играть!"
        )
    elif balance > 0:
        rank = get_user_rank(user.id)
        lvl = get_user_level(user.id)

        text = (
            f"{GREET} С возвращением, <b>{user.full_name}</b>!\n\n"
            f"{MONEY} Баланс: <b>{balance:,}</b> msg\n"
            f"🏆 Место: <b>#{rank}</b>\n"
            f"📊 Уровень: <b>{lvl['level']}</b>\n\n"
            f"━━━━━━━━━━━━━━━\n"
            f"🚀 Открой Mini App, чтобы забрать бонус, крутить кейсы и смотреть топ!"
        )
    else:
        text = (
            f"{GREET} Добро пожаловать в Амину, <b>{user.full_name}</b>!\n\n"
            f"Это экономический бот с валютой <b>msg</b>.\n\n"
            f"━━━━━━━━━━━━━━━\n"
            f"🎯 <b>Что тебя ждёт:</b>\n"
            f"└─ 🎰 Колесо Фортуны (каждый день)\n"
            f"└─ 🎁 Кейсы и питомцы\n"
            f"└─ 🎰 Казино и дуэли\n"
            f"└─ 💍 Браки и рейтинг пар\n\n"
            f"👇 Нажми на кнопку ниже, чтобы начать!"
        )

    # ─── Отправляем ───
    try:
        await message.answer_photo(
            photo=START_PHOTO,
            caption=text,
            parse_mode="HTML",
            reply_markup=kb,
            reply_to_message_id=message.message_id
        )
    except Exception as e:
        print(f"[START] Ошибка фото: {e}")
        await message.answer(
            text, parse_mode="HTML", reply_markup=kb,
            reply_to_message_id=message.message_id
        )

    await _daily_reminder(user.id, message.chat.id)
# =====================================
#  /ref — реферальная программа
# =====================================

@dp.message(Command("ref"))
async def cmd_ref(message: Message):
    log_cmd("🔗 /ref", message)
    user = message.from_user
    ensure_user(user)

    LINK  = _p(PREM_LINK, "🔗")
    USERS = _p(PREM_USERS, "👥")
    GIFT  = _p(PREM_GIFT, "🎁")
    CHECK = _p(PREM_CHECK, "✅")
    MONEY = _p(PREM_MONEY, "💰")

    ref_link = f"https://t.me/{BOT_USERNAME}?start=ref{user.id}"
    stats = get_referral_stats(user.id)
    rewards_today = count_rewards_24h(user.id)
    left_today = max(0, REFERRAL_MAX_PER_DAY - rewards_today)

    text = (
        f"{LINK} <b>Твоя реферальная ссылка:</b> <code>{ref_link}</code>\n"
        f"{USERS} Приглашено: <b>{stats['total']}</b> | {CHECK} Активных: <b>{stats['active']}</b>\n"
        f"⏳ В ожидании: <b>{stats['pending']}</b> | 💤 Сгорело: <b>{stats['burned']}</b>\n"
        f"{MONEY} Заработано: <b>{stats['earned']:,}</b> msg\n"
        f"{GIFT} Наград сегодня: <b>{rewards_today}/{REFERRAL_MAX_PER_DAY}</b>"
        f" (осталось {left_today})\n\n"
        f"<b>Как это работает:</b>\n"
        f"└─ Ты получаешь <b>{REFERRER_REWARD}</b> msg за реферала\n"
        f"└─ Реферал должен написать <b>{REFERRAL_THRESHOLD}</b> сообщений\n"
        f"└─ Реферал получает <b>{REFERRAL_REWARD}</b> msg + VIP на {REFERRAL_VIP_DAYS} день\n"

    )

    await message.answer(
        text, parse_mode="HTML",
        reply_to_message_id=message.message_id
    )

@dp.message(Command("setid"))
async def cmd_setid(message: Message):
    log_cmd("🆔 /setid", message)
    actor_id = message.from_user.id

    # Только владелец
    if not is_owner(actor_id):
        await message.answer("⛔ Только для владельца")
        return

    args = message.text.split()[1:]
    
    # Парсим аргументы
    if len(args) < 2:
        await message.answer(
            "❌ Использование:\n"
            "└─ <code>/setid @username 777</code>\n"
            "└─ <code>/setid [Telegram ID] 777</code>\n"
            "└─ или ответь на сообщение: <code>/setid 777</code>",
            parse_mode="HTML"
        )
        return

    target_arg = args[0]
    try:
        new_id = int(args[1])
        if new_id <= 0:
            raise ValueError
    except ValueError:
        await message.answer("❌ Новый custom_id должен быть положительным числом")
        return

    # ─── ПОИСК ЦЕЛИ (по реплаю, @username или Telegram ID) ───
    target_id = None
    target_name = None

    if message.reply_to_message:
        target = message.reply_to_message.from_user
        if target.is_bot:
            await message.answer("❌ Нельзя менять ID боту")
            return
        target_id = target.id
        target_name = target.full_name
        ensure_user(target)
    else:
        conn = sqlite3.connect("users.db")
        cur = conn.cursor()
        
        if target_arg.isdigit():
            # Ищем по РЕАЛЬНОМУ Telegram ID (user_id)
            cur.execute("SELECT user_id, full_name FROM users WHERE user_id = ?", (int(target_arg),))
        else:
            # Ищем по @username
            uname = target_arg.lstrip("@")
            cur.execute("SELECT user_id, full_name FROM users WHERE LOWER(username) = LOWER(?)", (uname,))
            
        row = cur.fetchone()
        conn.close()
        
        if row:
            target_id, target_name = row
        else:
            await message.answer("❌ Пользователь с таким Telegram ID или @username не найден в базе.")
            return

    if target_id == actor_id:
        await message.answer("❌ Нельзя менять ID самому себе (ты OWNER_ID = 1)")
        return

    # ─── МЕНЯЕМ ID В БАЗЕ ───
    ok, err = admin_set_custom_id(target_id, new_id)
    
    if not ok:
        await message.answer(f"❌ <b>Ошибка:</b> {err}", parse_mode="HTML")
        return

    await message.answer(
        f"✅ <b>Внутренний ID изменён</b>\n\n"
        f"└─ Кому: {target_name} (TG: <code>{target_id}</code>)\n"
        f"└─ Новый custom_id: <b>{new_id}</b>\n\n"
        f"💡 Теперь в профиле и топе он будет отображаться как <code>ID: {new_id}</code>",
        parse_mode="HTML"
    )

    # Уведомляем пользователя
    try:
        await bot.send_message(
            target_id,
            f"🆔 <b>Твой внутренний ID изменён!</b>\n\n"
            f"└─ Новый ID: <b>{new_id}</b>\n\n"
            f"💡 Теперь в топе и профиле ты будешь под этим номером",
            parse_mode="HTML"
        )
    except Exception:
        pass

    await log_to_channel(
        f"🆔 <b>Смена custom_id</b>\n"
        f"└─ Кому: {target_name} (<code>{target_id}</code>)\n"
        f"└─ Кем: {message.from_user.full_name}\n"
        f"└─ Новый ID: <b>{new_id}</b>"
    )

# =====================================
#  /version
# =====================================

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


# =====================================
#  /help — справка по категориям
# =====================================

HELP_CATEGORIES = {
    "econom": {
        "title": "💰 ЭКОНОМИКА",
        "emoji": "💰",
        "button": "💰 Экономика",
        "text": (
            "💵 <code>/balance</code> — твой баланс\n"
            "🎁 <code>/daily</code> — бонус раз в день (500 msg)\n"
            "🏦 <code>/bank</code> — банк с 1%/час\n"
            "📥 <code>/bankput</code> — положить в банк\n"
            "📤 <code>/banktake</code> — снять из банка\n"
            "🏆 <code>/top</code> — топ-10 богачей\n"
            "📜 <code>/history</code> — последние транзакции\n"
            "💸 <code>/gift</code> — подарить msg другу"
        ),
    },
    "games": {
        "title": "🎮 ИГРЫ",
        "emoji": "🎮",
        "button": "🎮 Игры",
        "text": (
            "🎁 <code>/case</code> — обычный кейс (1000 msg)\n"
            "💎 <code>/rarecase</code> — редкий кейс (5000 msg)\n"
            "👑 <code>/lcase</code> — легендарный (25 000 msg)\n"
            "🧭 <code>/cases</code> — магазин кейсов\n"
            "🎰 <code>/casino [ставка]</code> — казино (x1.5–x25)\n"
            "⚔️ <code>/duel @user [ставка]</code> — дуэль"
        ),
    },
    "social": {
        "title": "👥 СОЦИАЛЬНОЕ",
        "emoji": "👥",
        "button": "👥 Социальное",
        "text": (
            "🥷 <code>/rob @user</code> — ограбить (1ч кулдаун)\n"
            "💌 <code>/anon @user [текст]</code> — анонимка (600 msg)\n"
            "💍 <code>/marry @user</code> — предложить брак\n"
            "💔 <code>/divorce</code> — развод\n"
            "⭐ <code>/rep @user</code> — репутация (+1/-1)"
        ),
    },
    "profile": {
        "title": "👤 ПРОФИЛЬ",
        "emoji": "👤",
        "button": "👤 Профиль",
        "text": (
            "👤 <code>/profile</code> — 3 страницы профиля\n"
            "🎭 <code>/nick [имя]</code> — сменить ник\n"
            "🏷️ <code>/title [до 4 симв.]</code> — титул\n"
            "🏅 <code>/achievements</code> — достижения"
        ),
    },
    "vip": {
        "title": "👑 VIP",
        "emoji": "👑",
        "button": "👑 VIP",
        "text": (
            "👑 <code>/buyvip [недели]</code> — купить VIP\n"
            "💡 <code>/vipinfo</code> — что даёт VIP\n"
            "⭐ <code>/buymsg</code> — купить msg за звёзды"
        ),
    },
    "info": {
        "title": "🔗 ИНФО И РЕФЕРАЛКА",
        "emoji": "🔗",
        "button": "🔗 Инфо",
        "text": (
            "🚀 <code>/start</code> — начало\n"
            "🔗 <code>/ref</code> — реферальная программа\n"
            "🎟️ <code>/promo КОД</code> — активировать промокод\n"
            "📢 <code>/channel</code> — канал с новостями\n"
            "📌 <code>/version</code> — версия бота\n"
            "📖 <code>/help</code> — эта справка"
        ),
    },
}


def _build_help_main(is_admin: bool) -> tuple:
    """Главный экран /help с категориями."""
    text = (
        "📖 <b>Помощь — Амина</b>\n"
        "\n"
        "Выбери раздел:\n"
    )

    rows = []
    row = []
    for key, cat in HELP_CATEGORIES.items():
        row.append(InlineKeyboardButton(
            text=cat["button"],
            callback_data=f"help_cat_{key}"
        ))
        if len(row) == 2:
            rows.append(row)
            row = []

    if row:
        rows.append(row)

    # Админ-панель — если админ
    if is_admin:
        rows.append([InlineKeyboardButton(
            text="👑 Админ-панель",
            callback_data="help_admin"
        )])

    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return text, kb


def _build_help_category(key: str) -> tuple:
    """Экран категории /help."""
    cat = HELP_CATEGORIES.get(key)
    if not cat:
        return None, None

    text = (
        f"▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰\n"
        f"{cat['emoji']} <b>{cat['title']}</b>\n"
        f"▱▱▱▱▱▱▱▱▱▱▱▱▱▱▱▱▱\n\n"
        f"{cat['text']}"
    )

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="◀️ Назад",
            callback_data="help_back"
        )]
    ])
    return text, kb


@dp.message(Command("help"))
async def cmd_help(message: Message):
    log_cmd("📖 /help", message)
    user_id = message.from_user.id
    is_admin = is_owner(user_id) or bool(get_user_levels(user_id))
    text, kb = _build_help_main(is_admin)

    await message.answer(
        text, parse_mode="HTML", reply_markup=kb,
        reply_to_message_id=message.message_id
    )


@dp.callback_query(F.data.startswith("help_cat_"))
async def cb_help_category(callback: CallbackQuery):
    key = callback.data.replace("help_cat_", "")

    text, kb = _build_help_category(key)
    if text is None:
        await callback.answer("⚠️ Категория не найдена", show_alert=True)
        return

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
        print(f"[HELP] Ошибка: {e}")
    await callback.answer()


@dp.callback_query(F.data == "help_back")
async def cb_help_back(callback: CallbackQuery):
    user_id = callback.from_user.id
    is_admin = is_owner(user_id) or bool(get_user_levels(user_id))
    text, kb = _build_help_main(is_admin)

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
        print(f"[HELP] Ошибка: {e}")
    await callback.answer()


@dp.callback_query(F.data == "help_admin")
async def cb_help_admin(callback: CallbackQuery):
    user_id = callback.from_user.id
    role = get_role(user_id)
    if not role:
        await callback.answer("⛔ Нет прав", show_alert=True)
        return

    await callback.message.edit_text(
        f"{ROLE_TITLES[role]}\n\nВыбери категорию:",
        parse_mode="HTML",
        reply_markup=kb_main(role)
    )
    await callback.answer()


# =====================================
#  /broadcast — рассылка всем юзерам
# =====================================

BROADCAST_CHANNEL_ID = -1003354891084
BROADCAST_OWNER_LINK = "https://t.me/Kaoruko_off"
BROADCAST_CHANNEL_LINK = "https://t.me/Amina_updates"

# Временное хранилище: { owner_id: { text, photo_id, entities } }
_broadcast_drafts: dict = {}


def _broadcast_user_kb() -> InlineKeyboardMarkup:
    """Кнопки, которые получат юзеры в рассылке."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="💬 Написать владельцу",
                url=BROADCAST_OWNER_LINK
            ),
            InlineKeyboardButton(
                text="📢 Канал с новостями",
                url=BROADCAST_CHANNEL_LINK
            ),
        ]
    ])


def _broadcast_confirm_kb(owner_id: int) -> InlineKeyboardMarkup:
    """Кнопки подтверждения/отмены для владельца."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="✅ Подтвердить",
                callback_data=f"bc_confirm_{owner_id}"
            ),
            InlineKeyboardButton(
                text="❌ Отмена",
                callback_data=f"bc_cancel_{owner_id}"
            ),
        ]
    ])


@dp.message(Command("broadcast"))
async def cmd_broadcast(message: Message):
    log_cmd("📢 /broadcast", message)
    owner_id = message.from_user.id

    if not is_main_owner(owner_id) and not is_owner(owner_id):
        await message.answer("⛔ Только для владельца")
        return

    # ─── Источник: reply → forward → само сообщение ───
    target_msg = message.reply_to_message if message.reply_to_message else message

    text = target_msg.text or target_msg.caption or ""
    entities = target_msg.entities or target_msg.caption_entities or []
    photo_id = target_msg.photo[-1].file_id if target_msg.photo else None

    # ─── Если команда с текстом в самом сообщении (не reply) ───
    # /broadcast Привет всем
    if target_msg is message and text.startswith("/broadcast"):
        # Убираем саму команду
        first_line = text.split("\n", 1)
        text = first_line[1].strip() if len(first_line) > 1 else ""

    if not text and not photo_id:
        await message.answer(
            "❌ <b>Как использовать /broadcast</b>\n\n"
            "└─ Ответь на сообщение с текстом/фото:\n"
            "    <code>/broadcast</code>\n\n"
            "└─ Или напиши сразу:\n"
            "    <code>/broadcast Текст сообщения</code>\n\n"
            "└─ Или отправь фото с подписью и ответь:\n"
            "    <code>/broadcast</code>",
            parse_mode="HTML"
        )
        return

    # ─── Складываем черновик ───
    _broadcast_drafts[owner_id] = {
        "text": text,
        "photo_id": photo_id,
        "created_at": time.monotonic(),
    }

    # ─── Превью ───
    user_count = len(get_all_user_ids())

    preview_caption = (
        f"📢 <b>Предпросмотр рассылки</b>\n\n"
        f"└─ Получателей: <b>{user_count}</b>\n"
        f"└─ Тип: <b>{'фото + текст' if photo_id else 'текст'}</b>\n\n"
        f"━━━━━━━━━━━━━━━\n"
        f"{text if text else '<i>(без текста)</i>'}\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"Подтвердить отправку?"
    )

    kb = _broadcast_confirm_kb(owner_id)

    if photo_id:
        try:
            await message.answer_photo(
                photo=photo_id,
                caption=preview_caption,
                parse_mode="HTML",
                reply_markup=kb
            )
            return
        except Exception as e:
            print(f"[BROADCAST] Ошибка превью с фото: {e}")

    await message.answer(
        preview_caption,
        parse_mode="HTML",
        reply_markup=kb
    )


@dp.callback_query(F.data.startswith("bc_cancel_"))
async def cb_broadcast_cancel(callback: CallbackQuery):
    try:
        owner_id = int(callback.data.replace("bc_cancel_", ""))
    except ValueError:
        await callback.answer("⚠️ Ошибка данных", show_alert=True)
        return

    if callback.from_user.id != owner_id:
        await callback.answer("❌ Это не для тебя", show_alert=True)
        return

    _broadcast_drafts.pop(owner_id, None)

    try:
        await callback.message.edit_caption(
            caption="❌ <b>Рассылка отменена</b>",
            parse_mode="HTML"
        )
    except Exception:
        try:
            await callback.message.edit_text(
                "❌ <b>Рассылка отменена</b>",
                parse_mode="HTML"
            )
        except Exception:
            pass

    await callback.answer("❌ Отменено")


@dp.callback_query(F.data.startswith("bc_confirm_"))
async def cb_broadcast_confirm(callback: CallbackQuery):
    try:
        owner_id = int(callback.data.replace("bc_confirm_", ""))
    except ValueError:
        await callback.answer("⚠️ Ошибка данных", show_alert=True)
        return

    if callback.from_user.id != owner_id:
        await callback.answer("❌ Это не для тебя", show_alert=True)
        return

    draft = _broadcast_drafts.pop(owner_id, None)
    if not draft:
        await callback.answer("⚠️ Черновик устарел", show_alert=True)
        return

    text = draft["text"]
    photo_id = draft["photo_id"]

    # ─── Проверка: черновик не старше 10 минут ───
    if time.monotonic() - draft["created_at"] > 600:
        await callback.answer("⏰ Черновик устарел", show_alert=True)
        return

    await callback.answer("📢 Начинаю рассылку...")

    try:
        if photo_id:
            await callback.message.edit_caption(
                caption="📢 <b>Рассылка запущена…</b>",
                parse_mode="HTML"
            )
        else:
            await callback.message.edit_text(
                "📢 <b>Рассылка запущена…</b>",
                parse_mode="HTML"
            )
    except Exception:
        pass

    # ─── 1. Отправляем в канал ───
    try:
        if photo_id:
            await bot.send_photo(
                chat_id=BROADCAST_CHANNEL_ID,
                photo=photo_id,
                caption=text if text else None,
                parse_mode="HTML",
                reply_markup=_broadcast_user_kb()
            )
        else:
            await bot.send_message(
                chat_id=BROADCAST_CHANNEL_ID,
                text=text,
                parse_mode="HTML",
                reply_markup=_broadcast_user_kb()
            )
        print("[BROADCAST] ✅ Отправлено в канал")
    except Exception as e:
        print(f"[BROADCAST] ❌ Ошибка отправки в канал: {e}")

    # ─── 2. Рассылка юзерам ───
    user_ids = get_all_user_ids()
    total = len(user_ids)

    sent = 0
    failed = 0

    status_msg = await callback.message.answer(
        f"📢 <b>Рассылка…</b>\n"
        f"└─ Прогресс: 0/{total}",
        parse_mode="HTML"
    )

    # Обновляем прогресс каждые N юзеров
    UPDATE_EVERY = 50

    for i, uid in enumerate(user_ids, start=1):
        try:
            if photo_id:
                await bot.send_photo(
                    chat_id=uid,
                    photo=photo_id,
                    caption=text if text else None,
                    parse_mode="HTML",
                    reply_markup=_broadcast_user_kb()
                )
            else:
                await bot.send_message(
                    chat_id=uid,
                    text=text,
                    parse_mode="HTML",
                    reply_markup=_broadcast_user_kb()
                )
            sent += 1
        except Exception as e:
            failed += 1
            print(f"[BROADCAST] Ошибка для {uid}: {e}")

        # Небольшая задержка, чтобы не словить флуд-лимит
        await asyncio.sleep(0.05)

        # Обновляем прогресс
        if i % UPDATE_EVERY == 0:
            try:
                await status_msg.edit_text(
                    f"📢 <b>Рассылка…</b>\n"
                    f"└─ Прогресс: {i}/{total}\n"
                    f"└─ Отправлено: {sent}\n"
                    f"└─ Ошибок: {failed}",
                    parse_mode="HTML"
                )
            except Exception:
                pass

    # ─── 3. Итог ───
    try:
        await status_msg.edit_text(
            f"✅ <b>Рассылка завершена!</b>\n\n"
            f"└─ 📤 Отправлено: <b>{sent}</b>\n"
            f"└─ ❌ Ошибок: <b>{failed}</b>\n"
            f"└─ 👥 Всего: <b>{total}</b>\n"
            f"└─ 📢 В канал: <b>отправлено</b>",
            parse_mode="HTML"
        )
    except Exception:
        pass

    await log_to_channel(
        f"📢 <b>Рассылка</b>\n"
        f"└─ Инициатор: {callback.from_user.full_name} (<code>{owner_id}</code>)\n"
        f"└─ Тип: {'фото + текст' if photo_id else 'текст'}\n"
        f"└─ Отправлено: {sent}/{total}\n"
        f"└─ Ошибок: {failed}"
    )

# ====================================
#  ПЛАТЕЖИ ЗА STARS
# ====================================

# Формат: (msg_amount, stars, bonus_percent)
# bonus_percent — только для отображения в UI (0 = нет бонуса)
BUY_PACKAGES = [
    (1_000,      1,    0),
    (5_000,      5,    0),
    (10_000,     10,   0),
    (52_500,     50,   5),
    (110_000,    100,  10),
    (230_000,    200,  15),
    (600_000,    500,  20),
    (1_000_000,  1000, 0),
]

def _short_num(n: int) -> str:
    """Форматирует число: 1000 → 1к, 1000000 → 1 млн."""
    if n >= 1_000_000:
        val = n / 1_000_000
        if val == int(val):
            return f"{int(val)} млн"
        return f"{val:.1f} млн".replace(".0", "")

    if n >= 1_000:
        val = n / 1_000
        if val == int(val):
            return f"{int(val)}к"
        return f"{val:.1f}к".replace(".0", "")

    return str(n)

def get_package_by_stars(stars: int):
    """Возвращает (msg_amount, bonus) для пакета или None."""
    for msg, s, bonus in BUY_PACKAGES:
        if s == stars:
            return msg, bonus
    return None

# ====================================
#  /buymsg — покупка msg за звёзды
# ====================================

@dp.message(Command("buymsg"))
async def cmd_buymsg(message: Message):
    log_cmd("⭐ /buymsg", message)
    user = message.from_user
    ensure_user(user)

    rows = []
    row = []

    for msg_amount, stars, bonus in BUY_PACKAGES:
        text = f"{_short_num(msg_amount)} msg — {stars} ⭐"

        row.append(InlineKeyboardButton(
            text=text,
            callback_data=f"buy_pkg_{stars}"
        ))

        if len(row) == 2:
            rows.append(row)
            row = []

    if row:
        rows.append(row)

    kb = InlineKeyboardMarkup(inline_keyboard=rows)

    await message.answer(
        f"⭐ <b>Покупка msg за Telegram Stars</b>\n\n"
        f"└─ Курс: <b>1 ⭐ = 1 000 msg</b>\n"
        f"└─ Бонус до <b>+25%</b> на крупные пакеты\n\n"
        f"<b>Выбери пакет:</b>",
        parse_mode="HTML",
        reply_markup=kb
    )

@dp.callback_query(lambda c: c.data.startswith("buy_pkg_"))
async def cb_buy_pkg(callback: CallbackQuery):
    data = callback.data

    try:
        stars = int(data.replace("buy_pkg_", ""))
    except ValueError:
        await callback.answer("⚠️ Ошибка данных", show_alert=True)
        return

    # Проверяем, что такой пакет существует
    package = get_package_by_stars(stars)
    if package is None:
        await callback.answer("⚠️ Пакет не найден", show_alert=True)
        return

    msg_amount, bonus = package

    user_id = callback.from_user.id
    ensure_user(callback.from_user)

    # Отправляем счёт
    try:
        await bot.send_invoice(
            chat_id=callback.message.chat.id,
            title=f"{msg_amount:,} msg",
            description=f"Покупка {msg_amount:,} msg за {stars} ⭐",
            payload=f"buymsg_{user_id}_{stars}",
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
          f"charge={payment.telegram_payment_charge_id}, "
          f"payload={payment.invoice_payload}")

    # 🔒 Идемпотентность — не начисляем второй раз
    if has_charge_id(payment.telegram_payment_charge_id):
        await message.answer(
            "⚠️ Этот платёж уже был обработан",
            parse_mode="HTML"
        )
        return

    # 🔍 Парсим payload
    try:
        parts = payment.invoice_payload.split("_")
        if len(parts) != 3:
            raise ValueError("Неверный формат payload")

        action = parts[0]
        payload_user_id = int(parts[1])
        value = int(parts[2])

        if payload_user_id != user.id:
            raise ValueError("Payload не совпадает с пользователем")

    except (ValueError, IndexError) as e:
        print(f"[PAYMENT] ❌ Ошибка payload: {e}")
        await message.answer(
            "❌ <b>Ошибка валидации платежа</b>\n"
            "Обратитесь в поддержку: /paysupport",
            parse_mode="HTML"
        )
        return

    ensure_user(user)

    # ═══════════════════════════════════════════
    #  ВЕТКА 1: покупка msg
    # ═══════════════════════════════════════════
    if action == "buymsg":
        if value != payment.total_amount:
            print(f"[PAYMENT] ❌ Сумма не совпадает: {value} != {payment.total_amount}")
            await message.answer("❌ Ошибка: сумма не совпадает")
            return

        package = get_package_by_stars(value)
        if package is None:
            await message.answer(f"❌ Пакет {value}⭐ не найден")
            return

        msg_amount, bonus = package

        new_balance = add_balance(user.id, msg_amount)
        log_payment(
            user.id,
            payment.total_amount,
            msg_amount,
            payment.telegram_payment_charge_id,
            payment.provider_payment_charge_id or ""
        )
        log_transaction(user.id, user.id, msg_amount, "stars_buy")

        payment_number = get_next_payment_number()
        payment_code = f"#paymsg{payment_number}"
        save_payment_code(payment.telegram_payment_charge_id, payment_code)

        bonus_line = f"\n└─ 🎁 Бонус: <b>+{bonus}%</b>" if bonus > 0 else ""

        await message.answer(
            f"✅ <b>Платёж получен!</b>\n\n"
            f"└─ ⭐ Оплачено: <b>{payment.total_amount}</b> Stars\n"
            f"└─ 🧾 Код платежа: <code>{payment_code}</code>"
            f"{bonus_line}\n"
            f"└─ 💰 Начислено: <b>+{msg_amount:,}</b> msg\n"
            f"└─ Баланс: {new_balance:,} msg\n\n"
            f"💡 Спасибо за поддержку!",
            parse_mode="HTML"
        )

        await _check_and_notify_achievements(user.id, message.chat.id)

        await log_to_channel(
            f"💳 <b>Платёж Stars (msg)</b>\n"
            f"└─ Юзер: {user.full_name} (<code>{user.id}</code>)\n"
            f"└─ Оплачено: <b>{payment.total_amount} ⭐</b>\n"
            f"└─ Начислено: <b>{msg_amount:,} msg</b>\n"
            f"└─ Код: <code>{payment_code}</code>"
        )
        return

    # ═══════════════════════════════════════════
    #  ВЕТКА 2: покупка VIP
    # ═══════════════════════════════════════════
    if action == "buyvip":
        days = value

        if days <= 0 or days > 365:
            await message.answer("❌ Неверное количество дней VIP")
            return

        result = give_vip_days(user.id, days)
        if result is None:
            await message.answer("❌ Ошибка выдачи VIP, обратитесь в поддержку")
            return

        until_dt = datetime.fromisoformat(result)

        log_payment(
            user.id,
            payment.total_amount,
            0,   # msg не начисляем
            payment.telegram_payment_charge_id,
            payment.provider_payment_charge_id or ""
        )
        log_transaction(user.id, user.id, 0, "stars_buy_vip")

        await message.answer(
            f"✅ <b>VIP активирован!</b>\n\n"
            f"└─ ⭐ Оплачено: <b>{payment.total_amount}</b> Stars\n"
            f"└─ 👑 VIP на <b>{days} дней</b>\n"
            f"└─ 📅 До: <b>{until_dt.strftime('%d.%m.%Y %H:%M')}</b>\n\n"
            f"💡 Спасибо за поддержку!",
            parse_mode="HTML"
        )

        await log_to_channel(
            f"💳 <b>Платёж Stars (VIP)</b>\n"
            f"└─ Юзер: {user.full_name} (<code>{user.id}</code>)\n"
            f"└─ Оплачено: <b>{payment.total_amount} ⭐</b>\n"
            f"└─ VIP на <b>{days} дней</b>"
        )
        return

    # ═══════════════════════════════════════════
    #  НЕИЗВЕСТНЫЙ action
    # ═══════════════════════════════════════════
    print(f"[PAYMENT] ⚠️ Неизвестный action: {action}")
    await message.answer(
        f"⚠️ <b>Платёж получен, но тип не распознан</b>\n"
        f"└─ Action: <code>{action}</code>\n"
        f"└─ Обратитесь в поддержку: /paysupport",
        parse_mode="HTML"
    )

@dp.message(Command("paysupport"))
async def cmd_paysupport(message: Message):
    log_cmd("💬 /paysupport", message)
    await message.answer(
        "💬 <b>Поддержка по платежам</b>\n\n"
        "Если платёж прошёл, но msg не начислились — напишите:\n"
        "└─ t.me/Kaoruko_off\n\n"
        "При обращении укажите:\n"
        "└─ ID платежа (из чека Telegram)\n"
        "└─ Дату и сумму",
        parse_mode="HTML"
    )

# =====================================
#  /post — публикация поста в канал с кнопками
# =====================================

CHANNEL_ID = -1003354891084
CHANNEL_LINK = "https://t.me/Amina_updates"
BOT_LINK = "https://t.me/Aminka_Ai_bot"
OWNER_LINK = "https://t.me/Kaoruko_off"


@dp.message(Command("post"))
async def cmd_post(message: Message):
    log_cmd("📢 /post", message)

    if not is_main_owner(message.from_user.id) and not is_owner(message.from_user.id):
        await message.answer("⛔ Только для владельца")
        return

    # ─── Текст поста ───
    lines = message.text.split("\n", 1)
    if len(lines) < 2:
        await message.answer(
            "❌ Формат:\n"
            "<code>/post\n"
            "Текст поста\n"
            "(HTML-разметка поддерживается)</code>\n\n"
            "💡 Бот сам добавит кнопки внизу",
            parse_mode="HTML"
        )
        return

    post_text = lines[1].strip()

    if not post_text:
        await message.answer("❌ Текст пустой")
        return

    if len(post_text) > 4000:
        await message.answer("❌ Текст слишком длинный (макс. 4000)")
        return

    # ─── Кнопки ───
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="🚀 Перейти в бота",
                url=BOT_LINK
            ),
            InlineKeyboardButton(
                text="👑 Владелец",
                url=OWNER_LINK
            ),
        ]
    ])

    # ─── Публикация ───
    try:
        sent = await bot.send_message(
            chat_id=CHANNEL_ID,
            text=post_text,
            parse_mode="HTML",
            reply_markup=kb,
            disable_web_page_preview=True
        )

        await message.answer(
            f"✅ <b>Пост опубликован</b>\n\n"
            f"└─ Канал: @Amina_updates\n"
            f"└─ ID сообщения: <code>{sent.message_id}</code>\n\n"
            f"💡 Если нужно исправить — отредактируй вручную",
            parse_mode="HTML"
        )

    except Exception as e:
        await message.answer(f"❌ Ошибка публикации: {e}")

import html
import unicodedata

# ===================================
#  ХЕЛПЕР: очистка + экранирование имени
# ===================================

def _clean_name(text: str, fallback: str = "") -> str:
    """
    Убирает невидимые/управляющие Unicode-символы, обрезает пробелы
    и экранирует HTML-спецсимволы.
    Возвращает безопасную строку для вставки в parse_mode="HTML".
    """
    if not text:
        return fallback

    # Убираем control / format / surrogate / private / unassigned
    cleaned = "".join(
        ch for ch in text
        if unicodedata.category(ch) not in ("Cf", "Cc", "Cs", "Co", "Cn")
    )

    # Убираем zero-width и прочие невидимки
    for ch in ("\u200b", "\u200c", "\u200d", "\u2060", "\ufeff"):
        cleaned = cleaned.replace(ch, "")

    cleaned = cleaned.strip()

    if not cleaned:
        return fallback

    return html.escape(cleaned)


# ===================================
#  ПРОФИЛЬ
# ===================================

PROFILE_PREMIUM = {
    "user":    ("4974647275046306350", "👤"),
    "money":   ("6098001486053119347", "💰"),
    "bank":    ("5366223171454278937", "🏦"),
    "star":    ("5427379047573244592", "⭐"),
    "level":   ("5298520596945070277", "📊"),
    "vip":     ("5219827798125846744", "👑"),
    "gift":    ("5199749070830197566", "🎁"),
    "fire":    ("5429166655911511454", "🔥"),
    "warn":    ("5215677343594457295", "⚠️"),
    "trophy":  ("5413566144986503832", "🏆"),
    "medal":   ("5789828777882162072", "🏅"),
}


def _pr(use_premium: bool, key: str) -> str:
    """Возвращает премиум-эмодзи если use_premium=True, иначе обычный."""
    emoji_id, fallback = PROFILE_PREMIUM.get(key, ("", "•"))
    if use_premium and emoji_id:
        return _p(emoji_id, fallback)
    return fallback


def _build_profile_page(target_id: int, viewer_id: int, page: int) -> tuple:
    """Собирает текст страницы профиля с пагинацией."""
    ensure_user_by_id(target_id)
    data = get_user(target_id)

    if not data:
        return None, None

    # Теперь data возвращает 8 элементов
    uid, uname, fname, _balance_local, vip_until, last_daily, custom_id, registered_at = data
    
    balance = get_balance(uid)

    # ─── ЧИСТКА + ЭКРАНИРОВАНИЕ ───
    safe_fname = _clean_name(fname, fallback=f"ID:{uid}")
    safe_uname = _clean_name(uname) if uname else ""

    use_premium = is_vip_active(target_id) and is_vip_active(viewer_id)

    PROFILE_PAGES = 3
    if page < 0:
        page = 0
    if page >= PROFILE_PAGES:
        page = PROFILE_PAGES - 1

    # ─── Навигация ───
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

    kb_rows = []

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
            kb_rows.append([InlineKeyboardButton(
                text="🎁 Бонус", callback_data="prof_daily"
            )])

    kb_rows.append(nav_row)
    kb = InlineKeyboardMarkup(inline_keyboard=kb_rows)

    # ═══════════════════════════════════════════
    #  СТРАНИЦА 0 — ОСНОВНОЕ
    # ═══════════════════════════════════════════
    if page == 0:
        nick, _ = get_nick(uid)

        safe_nick = _clean_name(nick) if nick else ""
        display_name = safe_nick or safe_fname

        lvl = get_user_level(uid)
        rep = get_reputation(uid)

        bank_info = bank_get(uid)

        spouse_id = get_spouse(uid)
        marriage_line = ""
        if spouse_id:
            spouse_name = _couple_name(spouse_id)
            married_at = get_marriage_date(uid)
            days = 0
            if married_at:
                try:
                    m_dt = datetime.fromisoformat(married_at)
                    days = (datetime.now() - m_dt).days
                except ValueError:
                    pass
            marriage_line = f"\n💍 В браке с <b>{spouse_name}</b> ({days} дн.)"

        # Форматируем дату регистрации
        reg_date_str = "—"
        if registered_at:
            try:
                reg_dt = datetime.fromisoformat(registered_at)
                reg_date_str = reg_dt.strftime("%d.%m.%Y")
            except ValueError:
                pass

        E_USER  = _pr(use_premium, "user")
        E_MONEY = _pr(use_premium, "money")
        E_BANK  = _pr(use_premium, "bank")
        E_STAR  = _pr(use_premium, "star")
        E_LEVEL = _pr(use_premium, "level")

        # ВЫВОДИМ CUSTOM_ID ВМЕСТО UID
        text = (
            f"{E_USER} <b>{safe_fname}</b> | ID: <code>{custom_id}</code>\n"
            f"{E_MONEY} Баланс: <b>{balance:,}</b> msg\n"
            f"{E_BANK} Банк: <b>{bank_info['balance']:,}</b> msg\n"
            f"👻 Имя: <b>{display_name}</b>\n"
            f"{E_STAR} Репутация: <b>{rep}</b>"
            f"{marriage_line}\n"
            f"📅 Регистрация: <b>{reg_date_str}</b>\n"
            f"\n"
            f"{E_LEVEL} Уровень: <b>{lvl['level']}</b> — {lvl['title']}\n"
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

        E_VIP  = _pr(use_premium, "vip")
        E_GIFT = _pr(use_premium, "gift")
        E_FIRE = _pr(use_premium, "fire")
        E_WARN = _pr(use_premium, "warn")

        if warn_count >= WARN_LIMIT:
            warn_line = f"\n{E_WARN} Варны: <b>{warn_count}/{WARN_LIMIT}</b> (лимит!)"
        elif warn_count > 0:
            warn_line = f"\n{E_WARN} Варны: <b>{warn_count}/{WARN_LIMIT}</b>"
        else:
            warn_line = ""

        text = (
            f"▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰\n"
            f"{E_VIP} <b>СТАТУС</b>\n"
            f"▱▱▱▱▱▱▱▱▱▱▱▱▱▱▱▱▱\n\n"
            f"{E_VIP} VIP: <b>{vip_line}</b>\n"
            f"{E_GIFT} /daily: <b>{daily_line}</b>\n"
            f"{E_FIRE} Streak: <b>{streak}/7</b>"
            f"{warn_line}"
        )

    # ═══════════════════════════════════════════
    #  СТРАНИЦА 2 — ПРОГРЕСС
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

        E_TROPHY = _pr(use_premium, "trophy")
        E_MEDAL  = _pr(use_premium, "medal")

        next_ach = get_next_achievement(uid)
        if next_ach:
            (n_id, n_emoji, n_name, n_current, n_threshold, n_percent) = next_ach
            filled_ach = int(n_percent / 10)
            ach_bar = "▰" * filled_ach + "▱" * (10 - filled_ach)
            safe_ach_name = html.escape(n_name)
            next_block = (
                f"\n\n🎯 <b>Следующее:</b>\n"
                f"└─ {n_emoji} «{safe_ach_name}»: {n_current:,}/{n_threshold:,}\n"
                f"└─ {ach_bar} {n_percent}%"
            )
        else:
            next_block = f"\n\n{E_TROPHY} <b>Все достижения открыты!</b>"

        text = (
            f"▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰\n"
            f"{E_TROPHY} <b>ПРОГРЕСС</b>\n"
            f"▱▱▱▱▱▱▱▱▱▱▱▱▱▱▱▱▱\n\n"
            f"{E_TROPHY} Место в топе: <b>#{rank}</b>\n"
            f"{E_MEDAL} Достижения: <b>{ach_count}/{len(ACHIEVEMENTS)}</b>\n"
            f"└─ {ach_emojis_line}"
            f"{next_block}"
        )

    return text, kb



# ===================================
#  /profile — команда
# ===================================
@dp.message(Command("profile"))
async def cmd_profile(message: Message):
    log_cmd("👤 /profile", message)
    target = message.from_user

    # 1. Если это реплай на сообщение
    if message.reply_to_message and not message.reply_to_message.from_user.is_bot:
        target = message.reply_to_message.from_user
        ensure_user(target)
    
    # 2. Если передан аргумент (текст после команды)
    else:
        args = message.text.split()[1:]
        if args:
            arg = args[0]
            
            # Если это @username
            if arg.startswith("@"):
                found_id, found_name = find_user_id(message, arg)
                if found_id is None:
                    await message.answer("❌ Пользователь не найден")
                    return

                class TargetObj: pass
                target = TargetObj()
                target.id = found_id
                target.username = None
                target.full_name = found_name
                target.is_bot = False
                ensure_user_by_id(found_id)
            
            # Если это числовой ID (custom_id)
            elif arg.isdigit():
                conn = sqlite3.connect("users.db")
                cur = conn.cursor()
                cur.execute("SELECT user_id, full_name, username FROM users WHERE custom_id = ?", (int(arg),))
                row = cur.fetchone()
                conn.close()

                if not row:
                    await message.answer(f"❌ Пользователь с ID {arg} не найден в базе.")
                    return

                class TargetObj: pass
                target = TargetObj()
                target.id = row[0]
                target.full_name = row[1] or f"ID:{arg}"
                target.username = row[2]
                target.is_bot = False
                ensure_user_by_id(target.id)
            
            else:
                await message.answer("❌ Укажи @username или ID пользователя")
                return

    # Профиль казны скрыт
    if target.id == BOT_TREASURY_ID:
        await message.answer("🤖 Профиль казны скрыт")
        return

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

    # Fallback: текст без фото
    try:
        await message.answer(
            text, parse_mode="HTML", reply_markup=kb,
            reply_to_message_id=message.message_id
        )
    except Exception as e:
        print(f"[PROFILE] Ошибка отправки текста: {e}")
        plain = text
        for tag in ("<b>", "</b>", "<i>", "</i>", "<code>", "</code>",
                    "<blockquote>", "</blockquote>", "<tg-emoji", "</tg-emoji>"):
            plain = plain.replace(tag, "")
        await message.answer(
            plain[:4000], reply_markup=kb,
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
            await callback.message.edit_caption(
                caption=text, parse_mode="HTML", reply_markup=kb
            )
        else:
            await callback.message.edit_text(
                text, parse_mode="HTML", reply_markup=kb
            )
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

# ====================================
# /top
# ====================================
TOP_PHOTO = "AgACAgIAAxkBAAIPZ2rVfTo-y8hQtNxROrEp7Q1u5AHyAAKPH2sbjvVxSns2-0mR2kvdAQADAgADeAADPQQ"

def _format_top_name(user_id: int) -> str:
    nick, _ = get_nick(user_id)
    if nick:
        name = html.escape(nick)
    else:
        data = get_user(user_id)
        if not data:
            name = f"ID:{user_id}"
        else:
            uname = data[1]
            fname = data[2]
            if uname:
                name = f"@{html.escape(uname)}"
            elif fname:
                name = html.escape(fname)
            else:
                name = f"ID:{user_id}"

    title, _ = get_title(user_id)
    if title:
        name = f"{name} [{html.escape(title)}]"

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

    # ─── Пары ───
    for uid in married_users:
        spouse_id, balance, u1, u2 = marriage_by_user[uid]
        pair_key = tuple(sorted([u1, u2]))
        if pair_key in seen_pairs:
            continue
        seen_pairs.add(pair_key)

        # Пропускаем пары с казной
        if BOT_TREASURY_ID in (u1, u2):
            continue

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

    # ─── Одиночки ───
    for uid, balance in singles:
        if uid == BOT_TREASURY_ID:
            continue

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


TOP_CATEGORIES = {
    "wallet": {
        "title": "КОШЕЛЁК",
        "emoji": "💰",
        "button": "💰 Кошелёк",
    },
    "bank": {
        "title": "БАНК",
        "emoji": "🏦",
        "button": "🏦 Банк",
    },
    "streak": {
        "title": "STREAK",
        "emoji": "🔥",
        "button": "🔥 Streak",
    },
}


def _top_medal(i: int) -> str:
    """Возвращает медаль или номер для позиции."""
    medals = {
        1: "🥇", 2: "🥈", 3: "🥉",
        4: "4️⃣", 5: "5️⃣", 6: "6️⃣", 7: "7️⃣", 8: "8️⃣",
        9: "9️⃣", 10: "🔟",
        11: "1️⃣1️⃣", 12: "1️⃣2️⃣", 13: "1️⃣3️⃣",
        14: "1️⃣4️⃣", 15: "1️⃣5️⃣",
    }
    return medals.get(i, f"{i}.")


def _top_kb(active: str, viewer_id: int) -> InlineKeyboardMarkup:
    """Клавиатура с переключением категорий."""
    row = []
    for key, cat in TOP_CATEGORIES.items():
        if key == active:
            text = f"• {cat['button']} •"
            cb = "top_noop"
        else:
            text = cat["button"]
            cb = f"top_cat_{key}_{viewer_id}"
        row.append(InlineKeyboardButton(text=text, callback_data=cb))

    kb = InlineKeyboardMarkup(inline_keyboard=[row])
    return kb


def _build_top_page(category: str, viewer_id: int) -> tuple:
    """Собирает экран /top для категории."""
    ensure_user_by_id(viewer_id)

    if category not in TOP_CATEGORIES:
        category = "wallet"

    cat = TOP_CATEGORIES[category]
    limit = 10

    # ─── Данные в зависимости от категории ───
    if category == "wallet":
        # Топ по кошельку (с учётом браков)
        top = _build_top_with_marriages(viewer_id, limit)

        lines = []
        for i, item in enumerate(top, start=1):
            medal = _top_medal(i)
            marker = " ← ты" if item["is_me"] else ""
            lines.append(
                f"{medal} {item['display']} — <b>{item['display_balance']}</b> msg{marker}"
            )

        # Твоё место, если не в топе
        viewer_rank = get_user_rank(viewer_id)
        if viewer_rank > limit:
            viewer_balance = get_balance(viewer_id)
            hide = is_hide_balance_active(viewer_id)
            balance_text = "▒▒▒▒▒" if hide else f"{viewer_balance:,}"
            lines.append("")
            lines.append("━━━━━━━━━━━━━━━")
            lines.append(f"👤 Ты: <b>#{viewer_rank}</b> — {balance_text} msg")
            lines.append("━━━━━━━━━━━━━━━")

    elif category == "bank":
        # Топ по банку
        top_bank = get_top_bank(limit)

        lines = []
        for i, row in enumerate(top_bank, start=1):
            uid = row[0]
            if uid == BOT_TREASURY_ID:
                continue
            balance = row[-1]
            medal = _top_medal(i)
            name = _format_top_name(uid)
            if is_married(uid):
                name = f"{name} 💍"

            hide = is_hide_balance_active(uid)
            if hide and uid != viewer_id and not is_owner(viewer_id):
                balance_text = "▒▒▒▒▒"
            else:
                balance_text = f"{balance:,}"

            marker = " ← ты" if uid == viewer_id else ""
            lines.append(f"{medal} {name} — <b>{balance_text}</b> msg{marker}")

        # Твоё место
        try:
            conn = sqlite3.connect("users.db")
            cur = conn.cursor()
            cur.execute("SELECT balance FROM banks WHERE user_id = ?", (viewer_id,))
            row = cur.fetchone()
            my_bank = row[0] if row else 0

            cur.execute(
                "SELECT COUNT(*) FROM banks WHERE balance > ? AND user_id != ?",
                (my_bank, BOT_TREASURY_ID)
            )
            rank = cur.fetchone()[0] + 1
            conn.close()

            if rank > limit:
                hide = is_hide_balance_active(viewer_id)
                my_text = "▒▒▒▒▒" if hide else f"{my_bank:,}"
                lines.append("")
                lines.append("━━━━━━━━━━━━━━━")
                lines.append(f"👤 Ты: <b>#{rank}</b> — {my_text} msg")
                lines.append("━━━━━━━━━━━━━━━")
        except Exception as e:
            print(f"[TOP] Ошибка ранга банка: {e}")

    else:  # streak
        top_streak = get_top_streak(limit)

        if not top_streak:
            text = (
                f"🏆 <b>ТОП — {cat['emoji']} {cat['title']}</b>\n"
                f"\n"
                f"📭 Пока ни у кого нет streak.\n"
                f"└─ Забирай /daily каждый день и попадёшь сюда!"
            )
            kb = _top_kb(category, viewer_id)
            return text, kb

        lines = []
        for i, (uid, streak) in enumerate(top_streak, start=1):
            if uid == BOT_TREASURY_ID:
                continue
            medal = _top_medal(i)
            name = _format_top_name(uid)
            marker = " ← ты" if uid == viewer_id else ""
            lines.append(
                f"{medal} {name} — 🔥 <b>{streak}/7</b>{marker}"
            )

        # Твоё место
        viewer_streak = get_daily_streak(viewer_id)
        if viewer_streak > 0:
            try:
                conn = sqlite3.connect("users.db")
                cur = conn.cursor()
                cur.execute(
                    "SELECT COUNT(*) FROM users WHERE daily_streak > ? AND user_id != ?",
                    (viewer_streak, BOT_TREASURY_ID)
                )
                rank = cur.fetchone()[0] + 1
                conn.close()

                if rank > limit:
                    lines.append("")
                    lines.append("━━━━━━━━━━━━━━━")
                    lines.append(f"👤 Ты: <b>#{rank}</b> — 🔥 {viewer_streak}/7")
                    lines.append("━━━━━━━━━━━━━━━")
            except Exception as e:
                print(f"[TOP] Ошибка ранга streak: {e}")
        else:
            lines.append("")
            lines.append("━━━━━━━━━━━━━━━")
            lines.append("👤 У тебя нет streak")
            lines.append("└─ /daily — начни копить!")
            lines.append("━━━━━━━━━━━━━━━")

    text = (
        f"🏆 <b>ТОП-10 — {cat['emoji']} {cat['title']}</b>\n"
        f"\n"
        + "\n".join(lines)
    )

    kb = _top_kb(category, viewer_id)
    return text, kb


@dp.message(Command("top"))
async def cmd_top(message: Message):
    log_cmd("🏆 /top", message)
    user = message.from_user
    ensure_user(user)

    args = message.text.split()[1:]
    mode = args[0].lower() if args else "wallet"

    # Определяем категорию
    if mode == "bank":
        category = "bank"
    elif mode == "streak":
        category = "streak"
    else:
        category = "wallet"

    text, kb = _build_top_page(category, user.id)

    try:
        await message.answer_photo(
            photo=TOP_PHOTO,
            caption=text,
            parse_mode="HTML",
            reply_markup=kb,
            reply_to_message_id=message.message_id
        )
    except Exception as e:
        print(f"[TOP] Ошибка фото: {e}")
        await message.answer(
            text, parse_mode="HTML", reply_markup=kb,
            reply_to_message_id=message.message_id
        )


@dp.callback_query(F.data.startswith("top_cat_"))
async def cb_top_cat(callback: CallbackQuery):
    parts = callback.data.split("_")
    # top_cat_{category}_{viewer_id}
    if len(parts) != 4:
        await callback.answer("⚠️ Ошибка данных", show_alert=True)
        return

    category = parts[2]
    try:
        viewer_id = int(parts[3])
    except ValueError:
        await callback.answer("⚠️ Ошибка данных", show_alert=True)
        return

    if callback.from_user.id != viewer_id:
        await callback.answer("❌ Это не твой топ", show_alert=True)
        return

    text, kb = _build_top_page(category, viewer_id)

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
        print(f"[TOP] Ошибка: {e}")
    await callback.answer()


@dp.callback_query(F.data == "top_noop")
async def cb_top_noop(callback: CallbackQuery):
    await callback.answer()

# =====================================
#  /couple — данные пары ↔ рейтинг пар
# =====================================

COUPLE_PHOTO = "AgACAgIAAxkBAAIPZ2rVfTo-y8hQtNxROrEp7Q1u5AHyAAKPH2sbjvVxSns2-0mR2kvdAQADAgADeAADPQQ"  # можно заменить на своё


def _couple_name(user_id: int) -> str:
    """Имя для отображения: ник → @username → full_name → ID."""
    nick, _ = get_nick(user_id)
    if nick:
        return html.escape(nick)

    data = get_user(user_id)
    if not data:
        return f"ID:{user_id}"

    uname = data[1]
    fname = data[2]

    if uname:
        return f"@{html.escape(uname)}"
    if fname:
        return html.escape(fname)
    return f"ID:{user_id}"


def _couple_main_kb(couple: dict, viewer_id: int) -> InlineKeyboardMarkup:
    """Клавиатура экрана данных пары."""
    rows = [
        [InlineKeyboardButton(
            text="🏆 Рейтинг пар",
            callback_data=f"couple_top_{viewer_id}"
        )],
    ]

    # Кнопка развода — только для себя (если viewer один из пары)
    if viewer_id in (couple["user1_id"], couple["user2_id"]):
        rows.append([InlineKeyboardButton(
            text="💔 Развод",
            callback_data=f"couple_divorce_{viewer_id}"
        )])

    return InlineKeyboardMarkup(inline_keyboard=rows)


def _build_couple_main(viewer_id: int) -> tuple:
    """Экран данных пары."""
    info = get_couple_info(viewer_id)

    if not info.get("ok"):
        text = (
            "💔 <b>Ты не в браке</b>\n\n"
            "└─ Жениться: <code>/marry @user</code>\n"
            "└─ Или посмотри рейтинг пар 👇"
        )
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text="🏆 Рейтинг пар",
                callback_data=f"couple_top_{viewer_id}"
            )]
        ])
        return text, kb

    u1 = info["user1_id"]
    u2 = info["user2_id"]
    name1 = _couple_name(u1)
    name2 = _couple_name(u2)

    rank = get_couple_rank(viewer_id)
    rank_medal = {1: "🥇", 2: "🥈", 3: "🥉"}.get(rank, f"#{rank}")

    days = info["days_together"]
    days_line = f"{days} дн." if days > 0 else "меньше дня"

    # Кулдаун кейса
    last_case = info.get("last_case_at")
    case_line = "✅ доступен"
    if last_case:
        try:
            last_dt = datetime.fromisoformat(last_case)
            elapsed = datetime.now() - last_dt
            if elapsed < timedelta(hours=24):
                remaining = timedelta(hours=24) - elapsed
                h = remaining.seconds // 3600
                m = (remaining.seconds % 3600) // 60
                case_line = f"⏱️ {h}ч {m}м"
        except ValueError:
            pass

    text = (
        f"💍 <b>Твоя пара</b>\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"👥 {name1} 💕 {name2}\n\n"
        f"📅 Вместе: <b>{days_line}</b>\n"
        f"💰 Общий счёт: <b>{info['balance']:,}</b> msg\n"
        f"🏆 Место: <b>{rank_medal}</b>\n\n"
        f"🏦 <b>Личные банки:</b>\n"
        f"└─ {name1}: <b>{info['bank1']:,}</b> msg\n"
        f"└─ {name2}: <b>{info['bank2']:,}</b> msg\n\n"
        f"💍 Свадебный кейс: <b>{case_line}</b>\n"
        f"└─ Открыть: /cases → стр. 6"
    )

    kb = _couple_main_kb(info, viewer_id)
    return text, kb


def _build_couple_top(viewer_id: int) -> tuple:
    """Экран рейтинга пар."""
    top = get_top_couples(10)

    lines = ["🏆 <b>ТОП-10 пар</b>\n"]

    my_rank = get_couple_rank(viewer_id)

    medals = {
        1: "🥇", 2: "🥈", 3: "🥉",
        4: "4️⃣", 5: "5️⃣", 6: "6️⃣", 7: "7️⃣", 8: "8️⃣", 9: "9️⃣", 10: "🔟",
    }

    for i, row in enumerate(top, start=1):
        u1, u2, balance = row
        name1 = _couple_name(u1)
        name2 = _couple_name(u2)

        # Скрытые балансы
        hide = is_hide_balance_active(u1) or is_hide_balance_active(u2)
        if hide and viewer_id not in (u1, u2) and not is_owner(viewer_id):
            bal_text = "▒▒▒▒▒"
        else:
            bal_text = f"{balance:,}"

        marker = " ← ты" if viewer_id in (u1, u2) else ""
        medal = medals.get(i, f"{i}.")
        lines.append(f"{medal} {name1} 💍 {name2} — <b>{bal_text}</b> msg{marker}")

    # Позиция пары, если не в топе
    if my_rank > len(top) and my_rank > 0:
        my_info = get_couple_info(viewer_id)
        if my_info.get("ok"):
            hide = is_hide_balance_active(viewer_id)
            my_bal = "▒▒▒▒▒" if hide else f"{my_info['balance']:,}"
            lines.append("")
            lines.append("━━━━━━━━━━━━━━━")
            lines.append(f"👤 Ты: <b>#{my_rank}</b> — {my_bal} msg")
            lines.append("━━━━━━━━━━━━━━━")

    text = "\n".join(lines)

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="◀️ Назад к паре",
            callback_data=f"couple_main_{viewer_id}"
        )]
    ])
    return text, kb


@dp.message(Command("couple"))
async def cmd_couple(message: Message):
    log_cmd("💍 /couple", message)
    user = message.from_user
    ensure_user(user)

    text, kb = _build_couple_main(user.id)

    try:
        await message.answer_photo(
            photo=COUPLE_PHOTO,
            caption=text,
            parse_mode="HTML",
            reply_markup=kb,
            reply_to_message_id=message.message_id
        )
    except Exception as e:
        print(f"[COUPLE] Ошибка фото: {e}")
        await message.answer(
            text, parse_mode="HTML", reply_markup=kb,
            reply_to_message_id=message.message_id
        )


@dp.callback_query(F.data.startswith("couple_top_"))
async def cb_couple_top(callback: CallbackQuery):
    try:
        viewer_id = int(callback.data.replace("couple_top_", ""))
    except ValueError:
        await callback.answer("⚠️ Ошибка данных", show_alert=True)
        return

    if callback.from_user.id != viewer_id:
        await callback.answer("❌ Это не твоя пара", show_alert=True)
        return

    text, kb = _build_couple_top(viewer_id)

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
        print(f"[COUPLE] Ошибка: {e}")
    await callback.answer()


@dp.callback_query(F.data.startswith("couple_main_"))
async def cb_couple_main(callback: CallbackQuery):
    try:
        viewer_id = int(callback.data.replace("couple_main_", ""))
    except ValueError:
        await callback.answer("⚠️ Ошибка данных", show_alert=True)
        return

    if callback.from_user.id != viewer_id:
        await callback.answer("❌ Это не твоя пара", show_alert=True)
        return

    text, kb = _build_couple_main(viewer_id)

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
        print(f"[COUPLE] Ошибка: {e}")
    await callback.answer()


@dp.callback_query(F.data.startswith("couple_divorce_"))
async def cb_couple_divorce(callback: CallbackQuery):
    try:
        viewer_id = int(callback.data.replace("couple_divorce_", ""))
    except ValueError:
        await callback.answer("Пиши /divorce", show_alert=True)
        return

    if callback.from_user.id != viewer_id:
        await callback.answer("❌ Это не твоя пара", show_alert=True)
        return

    info = get_couple_info(viewer_id)
    if not info.get("ok"):
        await callback.answer("❌ Ты не в браке", show_alert=True)
        return

    # Предупреждение со штрафом
    balance = info["balance"]
    penalty = balance * 10 // 100
    remainder = balance - penalty
    half1 = remainder // 2
    half2 = remainder - half1

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="💔 Точно развестись",
                callback_data=f"couple_divorce_yes_{viewer_id}"
            ),
            InlineKeyboardButton(
                text="❌ Отмена",
                callback_data=f"couple_divorce_no_{viewer_id}"
            ),
        ]
    ])

    try:
        await callback.message.edit_caption(
            caption=(
                f"💔 <b>Развод</b>\n\n"
                f"└─ Общий счёт: <b>{balance:,}</b> msg\n"
                f"└─ Штраф 10%: <b>-{penalty:,}</b> msg (в казну)\n"
                f"└─ Остаток: <b>{remainder:,}</b> msg\n\n"
                f"<b>Ты получишь:</b> <b>{half1:,}</b> msg\n"
                f"<b>Супруг получит:</b> <b>{half2:,}</b> msg\n\n"
                f"⏳ После развода — кулдаун 7 дней\n\n"
                f"Точно развестись?"
            ),
            parse_mode="HTML",
            reply_markup=kb
        )
    except Exception:
        try:
            await callback.message.edit_text(
                text=(
                    f"💔 <b>Развод</b>\n\n"
                    f"└─ Общий счёт: <b>{balance:,}</b> msg\n"
                    f"└─ Штраф 10%: <b>-{penalty:,}</b> msg (в казну)\n"
                    f"└─ Остаток: <b>{remainder:,}</b> msg\n\n"
                    f"<b>Ты получишь:</b> <b>{half1:,}</b> msg\n"
                    f"<b>Супруг получит:</b> <b>{half2:,}</b> msg\n\n"
                    f"⏳ После развода — кулдаун 7 дней\n\n"
                    f"Точно развестись?"
                ),
                parse_mode="HTML",
                reply_markup=kb
            )
        except Exception:
            pass
    await callback.answer()


@dp.callback_query(F.data.startswith("couple_divorce_no_"))
async def cb_couple_divorce_no(callback: CallbackQuery):
    try:
        viewer_id = int(callback.data.replace("couple_divorce_no_", ""))
    except ValueError:
        await callback.answer("⚠️ Ошибка данных", show_alert=True)
        return

    if callback.from_user.id != viewer_id:
        await callback.answer("❌ Это не твоя пара", show_alert=True)
        return

    text, kb = _build_couple_main(viewer_id)

    try:
        if callback.message.photo:
            await callback.message.edit_caption(
                caption=text, parse_mode="HTML", reply_markup=kb
            )
        else:
            await callback.message.edit_text(
                text, parse_mode="HTML", reply_markup=kb
            )
    except Exception:
        pass
    await callback.answer("❌ Отменено")


@dp.callback_query(F.data.startswith("couple_divorce_yes_"))
async def cb_couple_divorce_yes(callback: CallbackQuery):
    try:
        viewer_id = int(callback.data.replace("couple_divorce_yes_", ""))
    except ValueError:
        await callback.answer("⚠️ Ошибка данных", show_alert=True)
        return

    if callback.from_user.id != viewer_id:
        await callback.answer("❌ Это не твоя пара", show_alert=True)
        return

    info = get_couple_info(viewer_id)
    if not info.get("ok"):
        await callback.answer("❌ Ты не в браке", show_alert=True)
        return

    u1 = info["user1_id"]
    u2 = info["user2_id"]

    # Развод
    ok, half1, half2, penalty = divorce_users(viewer_id)

    if not ok:
        await callback.answer("❌ Ошибка развода", show_alert=True)
        return

    # Кто чья доля
    my_half = half1 if viewer_id == u1 else half2
    spouse_id = u2 if viewer_id == u1 else u1
    spouse_half = half2 if viewer_id == u1 else half1

    name1 = _couple_name(u1)
    name2 = _couple_name(u2)

    try:
        await callback.message.edit_caption(
            caption=(
                f"💔 <b>Развод</b>\n\n"
                f"└─ Пара: {name1} 💍 {name2}\n"
                f"└─ Штраф: <b>-{penalty:,}</b> msg\n"
                f"└─ Ты получил: <b>{my_half:,}</b> msg\n\n"
                f"⏳ Кулдаун на брак: 7 дней"
            ),
            parse_mode="HTML"
        )
    except Exception:
        try:
            await callback.message.edit_text(
                text=(
                    f"💔 <b>Развод</b>\n\n"
                    f"└─ Пара: {name1} 💍 {name2}\n"
                    f"└─ Штраф: <b>-{penalty:,}</b> msg\n"
                    f"└─ Ты получил: <b>{my_half:,}</b> msg\n\n"
                    f"⏳ Кулдаун на брак: 7 дней"
                ),
                parse_mode="HTML"
            )
        except Exception:
            pass

    # Уведомление супругу
    try:
        await bot.send_message(
            spouse_id,
            f"💔 <b>Развод</b>\n\n"
            f"└─ Бывший супруг: {_couple_name(viewer_id)}\n"
            f"└─ Твоя доля: <b>{spouse_half:,}</b> msg\n"
            f"└─ Штраф пары: -{penalty:,} msg\n\n"
            f"⏳ Кулдаун на брак: 7 дней",
            parse_mode="HTML"
        )
    except Exception:
        pass

    await log_to_channel(
        f"💔 <b>Развод</b>\n"
        f"└─ Пара: {name1} 💍 {name2}\n"
        f"└─ Штраф: <b>{penalty:,}</b> msg → в казну\n"
        f"└─ Инициатор: {_couple_name(viewer_id)}"
    )

    await callback.answer("💔 Развод оформлен")



# =====================================
#  /history — история транзакций по категориям
# =====================================
HISTORY_MAP = {
    "transfer":           ("🎁", "Подарок"),
    "daily":              ("🎁", "Ежедневный бонус"),
    "casino_win":         ("🎰", "Победа в казино"),
    "casino_lose":        ("🎰", "Проигрыш в казино"),
    "casino_jackpot":     ("🎰", "ДЖЕКПОТ в казино"),
    "case":               ("🎁", "Открытие кейса"),
    "duel_win":           ("⚔️", "Победа в дуэли"),
    "duel_timeout":       ("⚔️", "Таймаут дуэли"),
    "rob_success":        ("🥷", "Успешное ограбление"),
    "rob_fail":           ("🚔", "Провал ограбления"),
    "anon":               ("💌", "Анонимка"),
    "marry":              ("💍", "Брак"),
    "stars_buy":          ("⭐", "Покупка Stars"),
    "buy_vip":            ("👑", "Покупка VIP"),
    "promo":              ("🎟️", "Промокод"),
    "referral_bonus":     ("👥", "Реферальный бонус"),
    "referral_reward":    ("👥", "Награда за реферала"),
    "admin_add":          ("⚙️", "Начислено админом"),
    "admin_rem":          ("⚙️", "Списано админом"),
    "admin_set":          ("⚙️", "Баланс установлен"),
    "admin_givevip":      ("👑", "Выдан VIP"),
    "admin_remvip":       ("🚫", "Снят VIP"),
    "admin_unban":        ("✅", "Разбан"),
    "auto_ban":           ("🚫", "Авто-бан"),
}


HISTORY_CATEGORIES = {
    "msg": {
        "title": "💰 Msg",
        "button": "💰 Msg",
        "kinds": [
            "transfer", "stars_buy", "buy_vip", "promo",
            "referral_bonus", "referral_reward",
        ],
    },
    "daily": {
        "title": "🎁 Ежедневное",
        "button": "🎁 Ежедневное",
        "kinds": ["daily"],
    },
    "games": {
        "title": "🎰 Игры",
        "button": "🎰 Игры",
        "kinds": [
            "casino_win", "casino_lose", "casino_jackpot",
            "case", "duel_win", "duel_timeout",
        ],
    },
    "social": {
        "title": "👥 Социальное",
        "button": "👥 Социальное",
        "kinds": ["rob_success", "rob_fail", "anon", "marry"],
    },
    "admin": {
        "title": "🛠 Админ",
        "button": "🛠 Админ",
        "kinds": [
            "admin_add", "admin_rem", "admin_set",
            "admin_givevip", "admin_remvip",
            "admin_unban", "auto_ban",
        ],
    },
    "summary": {
        "title": "📊 Итоги",
        "button": "📊 Итоги",
        "kinds": [],
    },
}


def _format_history_date_kr(iso_str: str) -> str:
    """Форматирует дату по Красноярску: 'сегодня 14:30', 'вчера 22:15'."""
    try:
        dt = datetime.fromisoformat(iso_str)
    except ValueError:
        return "—"

    # UTC+7
    dt_kr = dt + timedelta(hours=7)
    now_kr = datetime.now() + timedelta(hours=7)

    if dt_kr.date() == now_kr.date():
        return f"сегодня {dt_kr.strftime('%H:%M')}"
    if dt_kr.date() == (now_kr.date() - timedelta(days=1)):
        return f"вчера {dt_kr.strftime('%H:%M')}"

    return dt_kr.strftime("%d.%m %H:%M")


def _format_history_row(user_id: int, row: tuple) -> str:
    """Форматирует одну строку истории."""
    from_id, to_id, amount, kind, created_at = row

    emoji, name = HISTORY_MAP.get(kind, ("•", kind))
    date_str = _format_history_date_kr(created_at)

    # ─── Особые случаи ───
    if kind == "transfer":
        if from_id == user_id:
            return f"{emoji} {name} <b>-{abs(amount):,}</b> msg | {date_str}"
        return f"{emoji} {name} <b>+{abs(amount):,}</b> msg | {date_str}"

    if kind == "rob_success":
        if from_id == user_id:
            return f"{emoji} {name} <b>+{abs(amount):,}</b> msg | {date_str}"
        return f"{emoji} Тебя ограбили <b>-{abs(amount):,}</b> msg | {date_str}"

    if kind == "rob_fail":
        return f"{emoji} {name} <b>-{abs(amount):,}</b> msg | {date_str}"

    if kind == "admin_set":
        return f"{emoji} {name}: <b>{amount:,}</b> msg | {date_str}"

    if kind == "stars_buy":
        return f"{emoji} {name}: <b>+{abs(amount):,}</b> msg | {date_str}"

    # ─── Общий случай ───
    if amount > 0:
        return f"{emoji} {name} <b>+{amount:,}</b> msg | {date_str}"
    elif amount < 0:
        return f"{emoji} {name} <b>{amount:,}</b> msg | {date_str}"
    else:
        return f"{emoji} {name} | {date_str}"


def _build_history_menu(user_id: int) -> tuple:
    """Главное меню истории."""
    is_admin = is_owner(user_id) or is_moder(user_id) or is_senior(user_id)

    text = (
        f"📜 <b>История — Меню</b>\n"
        f"\n"
        f"Выбери категорию:"
    )

    rows = []
    row = []
    for key, cat in HISTORY_CATEGORIES.items():
        # Категория «Админ» — только для модераторов
        if key == "admin" and not is_admin:
            continue

        row.append(InlineKeyboardButton(
            text=cat["button"],
            callback_data=f"hist_cat_{key}_{user_id}"
        ))
        if len(row) == 2:
            rows.append(row)
            row = []

    if row:
        rows.append(row)

    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    return text, kb


def _build_history_category(user_id: int, category: str, page: int = 0) -> tuple:
    """Экран категории истории."""
    if category not in HISTORY_CATEGORIES:
        return None, None

    cat = HISTORY_CATEGORIES[category]

    # ─── Итоги ───
    if category == "summary":
        summary = get_history_summary_24h(user_id)

        text = (
            f"📊 <b>История — Итоги</b>\n"
            f"\n"
            f"━━━━━━━━━━━━━━━\n"
            f"📅 За 24 часа\n"
            f"━━━━━━━━━━━━━━━\n"
            f"\n"
            f"🟢 Приход: <b>+{summary['income']:,}</b> msg\n"
            f"🔴 Расход: <b>-{summary['expense']:,}</b> msg\n"
            f"📈 Чистый: <b>{summary['net']:+,}</b> msg"
        )

        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text="◀️ Назад",
                callback_data=f"hist_back_{user_id}"
            )]
        ])
        return text, kb

    # ─── Категория с транзакциями ───
    kinds = cat["kinds"]
    limit = 10

    total = get_history_count_by_kinds(user_id, kinds)

    if total == 0:
        text = (
            f"📜 <b>История — {cat['title']}</b>\n"
            f"\n"
            f"📭 Нет операций в этой категории"
        )
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text="◀️ Назад",
                callback_data=f"hist_back_{user_id}"
            )]
        ])
        return text, kb

    total_pages = max(1, (total + limit - 1) // limit)
    if page < 0:
        page = 0
    if page >= total_pages:
        page = total_pages - 1

    offset = page * limit
    rows = get_history_by_kinds(user_id, kinds, limit, offset)

    lines = [f"📜 <b>История — {cat['title']}</b>\n"]
    for row in rows:
        lines.append(_format_history_row(user_id, row))

    text = "\n".join(lines)

    # ─── Пагинация как в профиле ───
    nav_row = []
    for p in range(total_pages):
        if p == page:
            nav_row.append(InlineKeyboardButton(
                text=f"• {p + 1} •",
                callback_data="hist_noop"
            ))
        else:
            nav_row.append(InlineKeyboardButton(
                text=f"{p + 1}",
                callback_data=f"hist_cat_{category}_{user_id}_{p}"
            ))

    # Ограничение: максимум 10 кнопок в строке
    kb_rows = []
    for i in range(0, len(nav_row), 5):
        kb_rows.append(nav_row[i:i + 5])

    kb_rows.append([InlineKeyboardButton(
        text="◀️ Назад",
        callback_data=f"hist_back_{user_id}"
    )])

    kb = InlineKeyboardMarkup(inline_keyboard=kb_rows)
    return text, kb


# =====================================
#  /history — команда и callback'и
# =====================================
@dp.message(Command("history"))
async def cmd_history(message: Message):
    log_cmd("📜 /history", message)
    user = message.from_user
    ensure_user(user)

    text, kb = _build_history_menu(user.id)

    await message.answer(
        text, parse_mode="HTML", reply_markup=kb,
        reply_to_message_id=message.message_id
    )


@dp.callback_query(F.data.startswith("hist_cat_"))
async def cb_hist_cat(callback: CallbackQuery):
    parts = callback.data.split("_")
    # hist_cat_{category}_{user_id} или hist_cat_{category}_{user_id}_{page}
    if len(parts) < 4:
        await callback.answer("⚠️ Ошибка данных", show_alert=True)
        return

    category = parts[2]
    try:
        owner_id = int(parts[3])
        page = int(parts[4]) if len(parts) > 4 else 0
    except ValueError:
        await callback.answer("⚠️ Ошибка данных", show_alert=True)
        return

    if callback.from_user.id != owner_id:
        await callback.answer("❌ Это не твоя история", show_alert=True)
        return

    text, kb = _build_history_category(owner_id, category, page)
    if text is None:
        await callback.answer("⚠️ Категория не найдена", show_alert=True)
        return

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
        print(f"[HIST] Ошибка: {e}")
    await callback.answer()


@dp.callback_query(F.data.startswith("hist_back_"))
async def cb_hist_back(callback: CallbackQuery):
    parts = callback.data.split("_")
    # hist_back_{user_id}
    if len(parts) != 3:
        await callback.answer("⚠️ Ошибка данных", show_alert=True)
        return

    try:
        owner_id = int(parts[2])
    except ValueError:
        await callback.answer("⚠️ Ошибка данных", show_alert=True)
        return

    if callback.from_user.id != owner_id:
        await callback.answer("❌ Это не твоя история", show_alert=True)
        return

    text, kb = _build_history_menu(owner_id)

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
        print(f"[HIST] Ошибка: {e}")
    await callback.answer()


@dp.callback_query(F.data == "hist_noop")
async def cb_hist_noop(callback: CallbackQuery):
    await callback.answer()


# ======================================
#  /gift
# ======================================
@dp.message(Command("gift"))
async def cmd_gift(message: Message):
    log_cmd("🎁 /gift", message)
    user = message.from_user
    ensure_user(user)

    args = message.text.split()[1:]
    target_id = None
    target_name = None
    target_is_bot = False
    amount = None

    # ─── Определяем получателя ───
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
        target_id = target.id
        target_name = target.full_name
        target_is_bot = target.is_bot

        if not target_is_bot:
            ensure_user(target)

    else:
        if len(args) != 2:
            await message.answer(
                "❌ Использование:\n"
                "└─ ответь на сообщение и напиши /gift [сумма]\n"
                "└─ или /gift @username [сумма]\n"
                "└─ или /gift [ID] [сумма]",
                parse_mode="HTML"
            )
            return

        a, b = args
        
        # Логика: ищем, что из введенного есть в базе (ID), а что сумма
        conn = sqlite3.connect("users.db")
        cur = conn.cursor()
        
        found_target_arg = None
        found_amount_str = None

        if a.startswith("@"):
            found_target_arg, found_amount_str = a, b
        elif b.startswith("@"):
            found_target_arg, found_amount_str = b, a
        elif a.isdigit() and b.isdigit():
            # Оба числа. Проверяем, существует ли первое как custom_id
            cur.execute("SELECT user_id FROM users WHERE custom_id = ?", (int(a),))
            if cur.fetchone():
                found_target_arg, found_amount_str = a, b
            else:
                # Если первого нет, проверяем второе
                cur.execute("SELECT user_id FROM users WHERE custom_id = ?", (int(b),))
                if cur.fetchone():
                    found_target_arg, found_amount_str = b, a
                else:
                    # Ни один не найден как ID, считаем первое ID, второе сумму
                    found_target_arg, found_amount_str = a, b
        elif a.isdigit():
            found_target_arg, found_amount_str = a, b
        elif b.isdigit():
            found_target_arg, found_amount_str = b, a
        else:
            conn.close()
            await message.answer("❌ Укажи @user или числовой ID получателя")
            return

        try:
            amount = int(found_amount_str)
        except ValueError:
            conn.close()
            await message.answer(
                f"😅 «{found_amount_str}» — это не число\n"
                f"└─ Пример: /gift @username 100",
                parse_mode="HTML"
            )
            return

        if not found_target_arg.startswith("@"):
            # Ищем по custom_id
            cur.execute(
                "SELECT user_id, full_name FROM users WHERE custom_id = ?",
                (int(found_target_arg),)
            )
        else:
            # Ищем по @username
            uname = found_target_arg.lstrip("@")
            cur.execute(
                "SELECT user_id, full_name FROM users WHERE LOWER(username) = LOWER(?)",
                (uname,)
            )
            
        row = cur.fetchone()
        conn.close()

        if row is not None:
            target_id, target_name = row
        else:
            # Если не нашли в БД и это @username, пробуем через Telegram API
            if found_target_arg.startswith("@"):
                try:
                    chat = await bot.get_chat(found_target_arg)
                    if chat.type == "private":
                        target_id = chat.id
                        target_name = chat.full_name or chat.username or f"ID:{target_id}"
                        target_is_bot = getattr(chat, 'is_bot', False)
                    else:
                        await message.answer("❌ Не могу отправить msg в канал/группу")
                        return
                except Exception:
                    await message.answer(
                        "❌ Пользователь не найден.\n"
                        "└─ Юзер должен написать боту хотя бы раз,\n"
                        "    или укажи @username / ID правильно"
                    )
                    return
            else:
                await message.answer(f"❌ Пользователь с ID {found_target_arg} не найден в базе.")
                return

    # ─── Проверки ───
    if target_id == user.id:
        await message.answer("❌ Нельзя дарить самому себе")
        return

    if amount == 0:
        await message.answer("😏 Хитро, но 0 — это 0. Укажи сумму больше.")
        return

    # ═══════════════════════════════════════════
    #  ЛОГИКА ДЛЯ БОТОВ
    # ═══════════════════════════════════════════
    if target_is_bot:
        bot_name = target_name

        if amount > 0:
            ok, info = transfer_msg(user.id, target_id, amount)
            if not ok:
                if "Недостаточно" in info:
                    balance = get_balance(user.id)
                    await message.answer(
                        f"😢 <b>Недостаточно msg!</b>\n\n"
                        f"└─ Нужно: {amount:,}\n"
                        f"└─ У тебя: {balance:,}"
                        f"{_shortage_hint(amount, balance)}",
                        parse_mode="HTML"
                    )
                else:
                    await message.answer(f"❌ {info}")
                return

            new_balance = get_balance(user.id)
            try:
                conn = sqlite3.connect("users.db")
                cur = conn.cursor()
                cur.execute(
                    "INSERT OR IGNORE INTO users "
                    "(user_id, username, full_name, msg_count, last_activity) "
                    "VALUES (?, NULL, ?, 0, ?)",
                    (target_id, bot_name, datetime.now().isoformat())
                )
                conn.commit()
                conn.close()
            except Exception as e:
                print(f"[GIFT-BOT] Ошибка создания записи бота: {e}")

            await message.answer(
                f"🎁 {bot_name} благодарит тебя за {amount:,}msg!\n\n"
                f"└─ Твой баланс: {new_balance:,}msg\n\n"
                f"💡 Спасибо за поддержку!",
                parse_mode="HTML"
            )

            await log_to_channel(
                f"🎁 <b>Подарок боту</b>\n"
                f"└─ От: {user.full_name} (<code>{user.id}</code>)\n"
                f"└─ Боту: {bot_name} (<code>{target_id}</code>)\n"
                f"└─ Сумма: <b>{amount:,}</b> msg"
            )
        else:
            await message.answer(
                f"😏 Бот {bot_name} принял твой «подарок» "
                f"на {amount:,}msg...\n\n"
                f"└─ Но твои msg остались с тобой 😉\n"
                f"└─ Баланс: {get_balance(user.id):,}msg"
            )
        return

    # ═══════════════════════════════════════════
    #  ЛОГИКА ДЛЯ ОБЫЧНЫХ ЮЗЕРОВ
    # ═══════════════════════════════════════════
    if amount <= 0:
        await message.answer("❌ Сумма должна быть положительной")
        return

    # ✅ Атомарный перевод
    ok, info = transfer_msg(user.id, target_id, amount)
    if not ok:
        if "Недостаточно" in info:
            balance = get_balance(user.id)
            await message.answer(
                f"😢 <b>Недостаточно msg!</b>\n\n"
                f"└─ Нужно: {amount:,}\n"
                f"└─ У тебя: {balance:,}"
                f"{_shortage_hint(amount, balance)}",
                parse_mode="HTML"
            )
        else:
            await message.answer(f"❌ {info}")
        return

    # ─── Анимация ───
    msg = await message.answer("🎁 <b>Отправляем подарок…</b>", parse_mode="HTML")
    for frame in ["🎁", "🎁✨", "🎉", "🎉✨", "✅"]:
        await asyncio.sleep(0.6)
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
        f"└─ Сумма: <b>{amount:,}</b> msg\n"
        f"└─ Твой баланс: {new_balance:,} msg",
        parse_mode="HTML"
    )

    try:
        await bot.send_message(
            target_id,
            f"🎁 <b>Тебе подарили {amount:,} msg!</b>\n"
            f"└─ От: {user.full_name}"
        )
    except Exception:
        pass

    await log_to_channel(
        f"🎁 <b>Подарок</b>\n"
        f"└─ От: {user.full_name} (<code>{user.id}</code>)\n"
        f"└─ Кому: {target_name} (<code>{target_id}</code>)\n"
        f"└─ Сумма: <b>{amount:,}</b> msg"
    )

# ======================================
#  /buyvip
# ======================================
@dp.message(Command("buyvip"))
async def cmd_buyvip(message: Message):
    log_cmd("👑 /buyvip", message)
    user = message.from_user

    args = message.text.split()[1:]
    if len(args) != 1:
        await message.answer(
            "❌ Использование: /buyvip [недели]\n└─ 1 неделя = 2000 msg",
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
        f"└─ Стоимость: {weeks * 2000} msg\n"
        f"└─ Действует до: {until.strftime('%d.%m.%Y %H:%M')}\n\n"
        f"⚡ Теперь ты получаешь +1 msg раз в 1 сек!\n"
        f"💡 Все VIP-возможности: /vipinfo",
        parse_mode="HTML"
    )


# ====================================
#  /vipinfo
# ====================================

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
            f"👑 <b>Твои VIP-возможности</b>{until_line}\n"
            f"⚡ <b>Ускоренный доход:</b>\n└─ +1 msg раз в 1 сек\n"
            f"🎰 <b>Быстрое казино:</b>\n└─ Кулдаун 10 сек\n"
            f"🎱 <b>Быстрый магический шар:</b>\n└─ Кулдаун 2 мин (вместо 5)\n"
            f"🏦 <b>Улучшенный банк:</b>\n└─ 1%/час (вместо 0.5%)\n└─ Лимит: 1 000 000 msg\n"
            f"🎁 <b>Двойной daily:</b>\n└─ 1000 msg\n└─ 7-й день: 5000 msg\n"
            f"🎭 <b>Безлимитный ник</b>\n"
            f"🛡️ <b>Защита от warn</b>\n"
            f"👑 <b>Продлить:</b> /buyvip [дни]",
            parse_mode="HTML"
        )
    else:
        await message.answer(
            "👑 <b>VIP-подписка</b>\n"
            "Что даёт VIP:\n"
            "⚡ +1 msg раз в 1 сек (вместо 2)\n"
            "🎰 Кулдаун казино 10 сек\n"
            "🎱 Кулдаун /ball 2 мин (вместо 5)\n"
            "🏦 Банк 2%/час\n"
            "🎁 Двойной daily\n"
            "🎭 Безлимитный /nick\n"
            "🛡️ Защита от warn\n"
            "💰 <b>Цена:</b> 2000 msg / 7 дней\n"
            "└─ Купить: /buyvip [дни]",
            parse_mode="HTML"
        )


# =====================================
#  CASINO — общая логика
# =====================================

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

# =====================================
#  /ball — магический шар
# =====================================

@dp.message(Command("ball"))
async def cmd_ball(message: Message):
    log_cmd("🎱 /ball", message)
    user = message.from_user
    ensure_user(user)

    # ─── Аргументы ───
    args = message.text.split(maxsplit=1)

    if len(args) < 2 or not args[1].strip():
        await message.answer(
            "🎱 <b>Магический шар ждёт вопроса!</b>\n\n"
            "└─ Задай вопрос вместе с командой:\n"
            "└─ <code>/ball Я лягу сегодня спать в 22:00?</code>",
            parse_mode="HTML"
        )
        return

    question = args[1].strip()
    if len(question) > 300:
        await message.answer(
            "❌ <b>Вопрос слишком длинный</b>\n"
            "└─ Максимум: 300 символов",
            parse_mode="HTML"
        )
        return

    # ─── Кулдаун ───
    vip = is_vip_active(user.id)
    cooldown = BALL_COOLDOWN_VIP if vip else BALL_COOLDOWN_NORMAL

    last_asked = get_ball_cooldown(user.id)
    if last_asked:
        try:
            last_dt = datetime.fromisoformat(last_asked)
            elapsed = datetime.now() - last_dt
            if elapsed < cooldown:
                remaining = cooldown - elapsed
                m = remaining.seconds // 60
                s = remaining.seconds % 60
                time_text = f"{m} мин {s} сек" if m > 0 else f"{s} сек"
                vip_hint = (
                    "" if vip
                    else "\n\n💡 С VIP кулдаун короче: 2 мин вместо 5"
                )
                await message.answer(
                    f"⏳ <b>Шар отдыхает</b>\n"
                    f"└─ Осталось: <b>{time_text}</b>{vip_hint}",
                    parse_mode="HTML"
                )
                return
        except ValueError:
            pass

    # ─── Выбираем шар и ответ заранее ───
    emoji_id, fallback = random.choice(BALL_EMOJIS)
    ball = _p(emoji_id, fallback)
    answer = random.choice(BALL_ANSWERS)

    # ─── Ставим кулдаун СРАЗУ (до анимации, чтобы не спамили) ───
    set_ball_cooldown(user.id)

    # ─── Анимация: 3 шага ───
    safe_question = question.replace("<", "&lt;").replace(">", "&gt;")

    msg = await message.answer(
        f"{ball} <b>Читаю вопрос...</b> 👀",
        parse_mode="HTML"
    )

    await asyncio.sleep(0.6)
    try:
        await msg.edit_text(
            f"{ball} <b>Думаю над вопросом...</b> 🤔",
            parse_mode="HTML"
        )
    except Exception:
        pass

    await asyncio.sleep(0.6)
    try:
        await msg.edit_text(
            f"{ball} <b>«{safe_question}»</b>\n\n"
            f"{answer}",
            parse_mode="HTML"
        )
    except Exception as e:
        print(f"[BALL] Ошибка редактирования: {e}")



# =====================================
#  /daily — ежедневный бонус
# =====================================
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
                        f"⏳ <b>Бонус уже получен!</b>\n"
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

    # ─── Анимация: Амина заряжает подарок ───

    # Рандомная фраза-приветствие от Амины
    charger = random.choice([
        "Амина наполняет подарок светом… 🌸",
        "Амина вкладывает тепло в подарок… 💫",
        "Амина заряжает сюрприз… 🌷",
        "Амина шепчет что-то подарку… ✨",
    ])

    phases = [
        (10,  "▰▱▱▱▱▱▱▱▱▱", "📦",      "Только начинаем…"),
        (25,  "▰▰▰▱▱▱▱▱▱▱", "📦✨",    "Свет разгорается…"),
        (45,  "▰▰▰▰▰▱▱▱▱▱", "🎁",      "Уже чувствуется тепло…"),
        (65,  "▰▰▰▰▰▰▰▱▱▱", "🎁✨",    "Почти готово…"),
        (85,  "▰▰▰▰▰▰▰▰▰▱", "🎉🎁",    "Ещё чуть-чуть…"),
        (100, "▰▰▰▰▰▰▰▰▰▰", "🎉🎁✨",  "Готово!"),
    ]

    # Первый кадр
    msg = await message.answer(
        f"🌸 <b>{charger}</b>\n\n"
        f"▱▱▱▱▱▱▱▱▱▱ 0%\n\n"
        f"        📦",
        parse_mode="HTML"
    )

    # Проходим по фазам
    for percent, bar, emoji, status in phases:
        await asyncio.sleep(0.55)
        try:
            await msg.edit_text(
                f"🌸 <b>{charger}</b>\n\n"
                f"{bar} {percent}%\n\n"
                f"        {emoji}\n\n"
                f"└─ {status}",
                parse_mode="HTML"
            )
        except Exception:
            pass

    # ─── Финальная сцена ───
    await asyncio.sleep(0.6)

    # Особый финал для 7-го дня
    if is_bonus_day:
        for flash in [
            "⭐⭐ <b>Звёзды летят во все стороны!</b> ⭐⭐\n\n"
            "        ⭐⭐⭐\n"
            "       ⭐⭐⭐⭐⭐\n"
            "        ⭐⭐⭐",
            "🌟🌟 <b>Амина в восторге!</b> 🌟🌟\n\n"
            "          ⭐🏆⭐",
        ]:
            await asyncio.sleep(0.6)
            try:
                await msg.edit_text(flash, parse_mode="HTML")
            except Exception:
                pass
        await asyncio.sleep(0.6)

    # ─── Начисление бонуса ───
    new_balance = claim_daily(user.id, amount)
    set_daily_streak(user.id, new_streak)

    # ─── Streak для отображения ───
    if is_bonus_day:
        display_streak = 7
    else:
        display_streak = new_streak

    vip_mark = " 👑" if vip else ""
    streak_note = (
        "🔥🔥🔥 <b>STREAK 7/7 — ЛЕГЕНДА!</b> 🔥🔥🔥\n"
        "└─ Завтра начинаем заново!"
        if is_bonus_day
        else f"🔥 <b>Streak: {display_streak}/7</b>"
    )

    final_phrase = random.choice([
        "Амина улыбается — это тебе 💕",
        "«Держи, это для тебя!» — говорит Амина",
        "Амина подмигнула и протянула подарок 😊",
        "«Ты заслужил!» — улыбнулась Амина",
    ])

    if is_bonus_day:
        final_phrase = "🔥 Амина в восторге — 7 дней подряд! Ты лучший!"

    # ─── Следующая сумма ───
    next_amount = DAILY_AMOUNT if not vip else DAILY_VIP_AMOUNT
    bonus_amount = 2500 if not vip else 5000

    # ─── До 7-го дня ───
    days_left = 7 - display_streak

    # ─── Прогресс-бар streak ───
    filled = min(display_streak, 7)
    streak_bar = "▰" * filled + "▱" * (7 - filled)

    # ─── Сборка финального текста ───
    final_text = (
        f"🎉 <b>Подарок открыт!</b>{vip_mark}\n\n"
        f"💰 <b>+{amount:,}</b> msg\n\n"
        f"💕 <i>{final_phrase}</i>\n\n"
        f"{streak_note}\n"
        f"{streak_bar} {display_streak}/7\n\n"
        f"└─ Завтра: +{next_amount:,} msg"
    )

    if not is_bonus_day:
        if days_left <= 2:
            final_text += (
                f"\n└─ 🔥 Через <b>{days_left}</b> дн. — <b>+{bonus_amount:,} msg</b> 🎉"
            )
        else:
            final_text += (
                f"\n└─ На 7-й день: <b>+{bonus_amount:,} msg</b> 🎉"
            )

    _daily_notified.discard(user.id)
    final_text += (
        f"\n\n"
        f"💰 Баланс: <b>{new_balance:,}</b> msg\n"
        f"⏳ Следующий: <b>через 24ч</b>"
    )

    # ─── Кнопки ───
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="🎰 Казино",
                callback_data="daily_casino"
            ),
            InlineKeyboardButton(
                text="🎁 Кейс",
                callback_data="daily_case"
            ),
        ],
        [
            InlineKeyboardButton(
                text="👤 Профиль",
                callback_data="daily_profile"
            ),
        ]
    ])

    try:
        await msg.edit_text(final_text, parse_mode="HTML", reply_markup=kb)
    except Exception as e:
        print(f"[DAILY] Ошибка редактирования: {e}")
        await message.answer(final_text, parse_mode="HTML", reply_markup=kb)

    # ─── Логируем 7-й день ───
    if is_bonus_day:
        await log_to_channel(
            f"🎁 <b>Streak 7/7!</b>\n"
            f"└─ Юзер: {user.full_name} (<code>{user.id}</code>)\n"
            f"└─ Получено: <b>+{amount:,}</b> msg"
        )

# =====================================
#  КОНСТАНТЫ /nick
# =====================================

NICK_COOLDOWN_VIP = timedelta(hours=6)
NICK_COOLDOWN_NORMAL = timedelta(hours=12)

NICK_MAX_LEN_VIP = 20
NICK_MAX_LEN_NORMAL = 10

NICK_FORBIDDEN_CHARS = ["<", ">", "\\", "/", "@", "\n", "\r", "\t"]


def _nick_max_len(vip: bool) -> int:
    return NICK_MAX_LEN_VIP if vip else NICK_MAX_LEN_NORMAL


def _nick_cooldown(vip: bool) -> timedelta:
    return NICK_COOLDOWN_VIP if vip else NICK_COOLDOWN_NORMAL


def _nick_validate(nick: str, vip: bool) -> tuple:
    """
    Проверяет ник.
    Возвращает (ok: bool, error_text: str).
    """
    max_len = _nick_max_len(vip)

    if not nick:
        return False, "❌ Ник не может быть пустым"

    if len(nick) > max_len:
        limit_text = "20 (VIP)" if vip else "10"
        return False, (
            f"❌ <b>Ник слишком длинный</b>\n"
            f"└─ Максимум: {limit_text} символов\n"
            f"└─ У тебя: {len(nick)}"
        )

    found = [ch for ch in NICK_FORBIDDEN_CHARS if ch in nick]
    if found:
        display = []
        for ch in found:
            if ch == "\n":
                display.append("перенос строки")
            elif ch == "\r":
                display.append("возврат каретки")
            elif ch == "\t":
                display.append("табуляция")
            elif ch == "\\":
                display.append("`\\`")
            else:
                display.append(f"`{ch}`")

        return False, (
            f"❌ <b>Запрещённые символы в нике</b>\n"
            f"└─ Найдено: {', '.join(set(display))}\n"
            f"└─ Нельзя: <code>&lt; &gt; \\ / @</code> и переносы"
        )

    return True, ""


# =====================================
#  ХЕЛПЕРЫ ДЛЯ /nick
# =====================================

def _format_time_ago(iso_str: str) -> str:
    """Возвращает '2 дня назад', '5 мин назад' и т.д."""
    if not iso_str:
        return "—"
    try:
        dt = datetime.fromisoformat(iso_str)
    except ValueError:
        return "—"

    now = datetime.now()
    diff = now - dt

    seconds = int(diff.total_seconds())
    if seconds < 60:
        return "только что"

    minutes = seconds // 60
    if minutes < 60:
        return f"{minutes} мин назад"

    hours = minutes // 60
    if hours < 24:
        return f"{hours} ч назад"

    days = hours // 24
    if days < 30:
        return f"{days} дн. назад"

    months = days // 30
    return f"{months} мес. назад"


def _format_time_left(iso_str: str, cooldown: timedelta) -> str:
    """Сколько осталось до след. смены."""
    if not iso_str:
        return "—"
    try:
        dt = datetime.fromisoformat(iso_str)
    except ValueError:
        return "—"

    elapsed = datetime.now() - dt
    remaining = cooldown - elapsed

    if remaining.total_seconds() <= 0:
        return "сейчас можно"

    seconds = int(remaining.total_seconds())
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60

    if hours > 0:
        return f"через {hours}ч {minutes}м"
    return f"через {minutes}м"


def _build_nick_screen(user_id: int) -> tuple:
    """Собирает компактный экран /nick."""
    nick, changed_at = get_nick(user_id)
    vip = is_vip_active(user_id)

    data = get_user(user_id)
    if not data:
        return None, None

    fname = data[2] or f"ID:{user_id}"
    balance = get_balance(user_id)

    # ─── ЭКРАНИРОВАНИЕ ───
    safe_nick = html.escape(nick) if nick else ""
    safe_fname = html.escape(fname) if fname else f"ID:{user_id}"

    display = safe_nick or safe_fname

    if safe_nick:
        head = f"🎭 Твой ник: <b>{safe_nick}</b>"
    else:
        head = "🎭 Твой ник: не установлен"

    lines = [head]

    if changed_at:
        lines.append(f"└─ Изменён: {_format_time_ago(changed_at)}")

    lines.append(f"└─ В топе: <b>{display}</b> — {balance:,} msg")

    lines.append("")

    max_len = _nick_max_len(vip)
    cooldown = _nick_cooldown(vip)

    if vip:
        lines.append(f"📋 1–{max_len} символов · 👑 VIP: кулдаун 6ч")
    else:
        lines.append(f"📋 1–{max_len} символов · кулдаун 12ч (VIP — 6ч)")
    lines.append("└─ Без <code>&lt; &gt; \\ / @</code> и переносов")

    can_change = True

    if changed_at:
        try:
            last_dt = datetime.fromisoformat(changed_at)
            elapsed = datetime.now() - last_dt
            if elapsed < cooldown:
                can_change = False
                left_text = _format_time_left(changed_at, cooldown)
                lines.append("")
                lines.append(f"⏳ Смена: <b>{left_text}</b>")
        except ValueError:
            pass

    text = "\n".join(lines)

    kb_rows = []

    if can_change:
        if nick:
            kb_rows.append([
                InlineKeyboardButton(
                    text="🎭 Сменить",
                    callback_data="nick_change"
                ),
                InlineKeyboardButton(
                    text="🗑️ Убрать",
                    callback_data="nick_remove"
                ),
            ])
        else:
            kb_rows.append([
                InlineKeyboardButton(
                    text="🎭 Установить",
                    callback_data="nick_change"
                ),
            ])

    kb = InlineKeyboardMarkup(inline_keyboard=kb_rows) if kb_rows else None
    return text, kb


# =====================================
#  /nick — сменить ник
# =====================================
@dp.message(Command("nick"))
async def cmd_nick(message: Message):
    log_cmd("🎭 /nick", message)
    user = message.from_user
    ensure_user(user)

    args = message.text.split(maxsplit=1)

    # ─── Без аргумента — показать экран ───
    if len(args) < 2:
        text, kb = _build_nick_screen(user.id)
        if text is None:
            await message.answer("❌ Профиль не найден")
            return

        try:
            await message.answer(
                text, parse_mode="HTML", reply_markup=kb,
                reply_to_message_id=message.message_id
            )
        except Exception as e:
            print(f"[NICK] Ошибка экрана: {e}")
            # Fallback без разметки
            plain = text.replace("<b>", "").replace("</b>", "")
            plain = plain.replace("<code>", "").replace("</code>", "")
            await message.answer(
                plain, reply_markup=kb,
                reply_to_message_id=message.message_id
            )
        return

    # ─── С аргументом — установить ник ───
    new_nick = args[1].strip()

    vip = is_vip_active(user.id)

    # ─── Валидация ───
    ok, err = _nick_validate(new_nick, vip)
    if not ok:
        await message.answer(
            err,
            parse_mode="HTML",
            reply_to_message_id=message.message_id
        )
        return

    # ─── Кулдаун ───
    cooldown = _nick_cooldown(vip)

    _, changed_at = get_nick(user.id)
    if changed_at:
        try:
            last_dt = datetime.fromisoformat(changed_at)
            elapsed = datetime.now() - last_dt
            if elapsed < cooldown:
                remaining = cooldown - elapsed
                h = remaining.seconds // 3600
                m = (remaining.seconds % 3600) // 60

                if vip:
                    cooldown_text = "6 часов"
                    vip_hint = ""
                else:
                    cooldown_text = "12 часов"
                    vip_hint = "\n\n💡 VIP меняет ник раз в 6 часов 👑"

                await message.answer(
                    f"⏳ <b>Ник можно менять раз в {cooldown_text}</b>\n"
                    f"└─ Следующий раз через: <b>{h} ч {m} мин</b>{vip_hint}",
                    parse_mode="HTML",
                    reply_to_message_id=message.message_id
                )
                return
        except ValueError:
            pass

    # ─── Устанавливаем ───
    set_nick(user.id, new_nick)

    msg = await message.answer(
        "🎭 <b>Меняем ник…</b>",
        parse_mode="HTML",
        reply_to_message_id=message.message_id
    )

    for frame in ["🎭", "✏️", "📝", "✅"]:
        await asyncio.sleep(0.2)
        try:
            await msg.edit_text(
                f"🎭 <b>Меняем ник…</b>\n\n{frame}",
                parse_mode="HTML"
            )
        except Exception:
            pass

    vip_note = " 👑" if vip else ""

    # ─── ЭКРАНИРОВАНИЕ ───
    safe_nick = html.escape(new_nick)

    try:
        await msg.edit_text(
            f"✅ <b>Ник изменён!</b>{vip_note}\n\n"
            f"└─ Новый: <b>{safe_nick}</b>\n"
            f"└─ В топе: <b>{safe_nick}</b> — {get_balance(user.id):,} msg",
            parse_mode="HTML"
        )
    except Exception as e:
        print(f"[NICK] Ошибка финала: {e}")
        await msg.edit_text(
            f"✅ Ник изменён!\n"
            f"└─ Новый: {safe_nick}"
        )

    # ─── Лог в канал ───
    safe_fullname = html.escape(user.full_name or "")
    await log_to_channel(
        f"🎭 <b>Смена ника</b>\n"
        f"└─ Юзер: {safe_fullname} (<code>{user.id}</code>)\n"
        f"└─ Новый ник: <b>{safe_nick}</b>\n"
        f"└─ VIP: {'да' if vip else 'нет'}"
    )


# =====================================
#  CALLBACK'И ДЛЯ /nick
# =====================================

@dp.callback_query(F.data == "nick_change")
async def cb_nick_change(callback: CallbackQuery):
    user_id = callback.from_user.id
    vip = is_vip_active(user_id)
    max_len = _nick_max_len(vip)

    await callback.answer(
        f"🎭 Введи: /nick [новое имя]\n"
        f"└─ Пример: /nick Антон\n\n"
        f"💡 1–{max_len} символов, без < > \\ / @ и переносов",
        show_alert=True
    )


@dp.callback_query(F.data == "nick_remove")
async def cb_nick_remove(callback: CallbackQuery):
    user_id = callback.from_user.id

    nick, _ = get_nick(user_id)
    if not nick:
        await callback.answer("ℹ️ У тебя нет ника", show_alert=True)
        return

    vip = is_vip_active(user_id)
    cooldown = _nick_cooldown(vip)

    _, changed_at = get_nick(user_id)
    if changed_at:
        try:
            last_dt = datetime.fromisoformat(changed_at)
            elapsed = datetime.now() - last_dt
            if elapsed < cooldown:
                remaining = cooldown - elapsed
                h = remaining.seconds // 3600
                m = (remaining.seconds % 3600) // 60
                await callback.answer(
                    f"⏳ Убрать можно через {h}ч {m}м",
                    show_alert=True
                )
                return
        except ValueError:
            pass

    cooldown_text = "6ч" if vip else "12ч"

    # ─── ЭКРАНИРОВАНИЕ ───
    safe_nick = html.escape(nick)

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="✅ Убрать",
                callback_data="nick_remove_confirm"
            ),
            InlineKeyboardButton(
                text="❌ Отмена",
                callback_data="nick_remove_cancel"
            ),
        ]
    ])

    try:
        await callback.message.edit_text(
            f"🗑️ <b>Убрать ник?</b>\n\n"
            f"└─ Текущий: <b>{safe_nick}</b>\n"
            f"└─ В топе будет имя из Telegram\n\n"
            f"💡 Запустит кулдаун {cooldown_text}",
            parse_mode="HTML",
            reply_markup=kb
        )
    except Exception as e:
        print(f"[NICK] Ошибка превью удаления: {e}")
    await callback.answer()


@dp.callback_query(F.data == "nick_remove_confirm")
async def cb_nick_remove_confirm(callback: CallbackQuery):
    user_id = callback.from_user.id

    set_nick(user_id, "")

    try:
        await callback.message.edit_text(
            "✅ <b>Ник убран</b>\n\n"
            "└─ В топе будет имя из Telegram",
            parse_mode="HTML"
        )
    except Exception:
        pass

    await callback.answer("✅ Убран")


@dp.callback_query(F.data == "nick_remove_cancel")
async def cb_nick_remove_cancel(callback: CallbackQuery):
    user_id = callback.from_user.id
    text, kb = _build_nick_screen(user_id)

    try:
        if text:
            await callback.message.edit_text(
                text, parse_mode="HTML", reply_markup=kb
            )
        else:
            await callback.message.edit_text(
                "❌ Отменено",
                reply_markup=None
            )
    except Exception as e:
        print(f"[NICK] Ошибка отмены: {e}")
    await callback.answer("❌ Отменено")





# ======================================
#  /rob — ограбление
# ======================================
ROB_SUCCESS_PHRASES = [
    "Ты вломился в дом {target}!\n└─ Схватил: <b>+{amount}</b> msg\n└─ И сбежал в закат 🌅",
    "Пока {target} спал, ты вынес <b>{amount}</b> msg!\n└─ Тише едешь — дальше будешь 🤫",
    "Чисто сработано! <b>+{amount}</b> msg в кармане\n└─ Никто ничего не видел 👀",
    "{target} даже не заметил пропажи!\n└─ <b>+{amount}</b> msg уже у тебя 🏃",
    "План сработал идеально!\n└─ Ты унёс <b>+{amount}</b> msg\n└─ {target} в шоке 😱",
    "Ночная вылазка удалась!\n└─ <b>+{amount}</b> msg у тебя\n└─ Спасибо {target} за щедрость 💰",
    "Ты проскользнул как тень!\n└─ <b>+{amount}</b> msg исчезли из казны {target} 🥷",
    "Грабитель из тебя сегодня отличный!\n└─ <b>+{amount}</b> msg\n└─ {target} проклинает свою беспечность 😈",
    "Взлом прошёл как по маслу!\n└─ <b>+{amount}</b> msg\n└─ {target} ничего не заметил 🔓",
    "Ограбление века!\n└─ Ты вынес <b>+{amount}</b> msg\n└─ {target} до сих пор в шоке 💎",
]

ROB_FAIL_PHRASES = [
    "Тебя поймали за руку!\n└─ Штраф: <b>-{penalty}</b> msg\n└─ Сирена 🚨 и позор",
    "{target} вызвал полицию!\n└─ Штраф: <b>-{penalty}</b> msg\n└─ Беги, пока можешь 🚓",
    "Побег не удался.\n└─ <b>-{penalty}</b> msg\n└─ Урок на будущее 😅",
    "Тебя опознали по камерам!\n└─ Штраф: <b>-{penalty}</b> msg\n└─ В следующий раз — маску 🎭",
    "{target} оказался начеку!\n└─ <b>-{penalty}</b> msg\n└─ Сигнализация сработала 🚨",
    "Ты поскользнулся на банановой кожуре!\n└─ Штраф: <b>-{penalty}</b> msg\n└─ Даже смешно 🍌",
    "Собака {target} укусила тебя за ногу!\n└─ <b>-{penalty}</b> msg на лечение 🐕",
    "Соседи вызвали охрану!\n└─ <b>-{penalty}</b> msg\n└─ Больше не суйся сюда 🚔",
    "Ты перепутал окно и упал в кусты!\n└─ Штраф: <b>-{penalty}</b> msg\n└─ Позор на весь район 🌳",
    "{target} не спал и ждал тебя!\n└─ <b>-{penalty}</b> msg\n└─ Ловушка сработала 🪤",
]

# =====================================
#  КОНСТАНТЫ /title
# =====================================

TITLE_MAX_LEN_VIP = 6
TITLE_MAX_LEN_NORMAL = 3

TITLE_COOLDOWN = timedelta(hours=12)

TITLE_FORBIDDEN_CHARS = ["<", ">", "\\", "/", "@", "\n", "\r", "\t"]


def _title_max_len(vip: bool) -> int:
    return TITLE_MAX_LEN_VIP if vip else TITLE_MAX_LEN_NORMAL


def _title_validate(title: str, vip: bool) -> tuple:
    """
    Проверяет титул (формат).
    Возвращает (ok: bool, error_text: str).
    """
    max_len = _title_max_len(vip)

    if not title:
        return False, "❌ Титул не может быть пустым"

    if len(title) > max_len:
        limit_text = "6 (VIP)" if vip else "3"
        return False, (
            f"❌ <b>Титул слишком длинный</b>\n"
            f"└─ Максимум: {limit_text} символа\n"
            f"└─ У тебя: {len(title)}"
        )

    found = [ch for ch in TITLE_FORBIDDEN_CHARS if ch in title]
    if found:
        display = []
        for ch in found:
            if ch == "\n":
                display.append("перенос строки")
            elif ch == "\r":
                display.append("возврат каретки")
            elif ch == "\t":
                display.append("табуляция")
            elif ch == "\\":
                display.append("`\\`")
            else:
                display.append(f"`{ch}`")

        return False, (
            f"❌ <b>Запрещённые символы в титуле</b>\n"
            f"└─ Найдено: {', '.join(set(display))}\n"
            f"└─ Нельзя: <code>&lt; &gt; \\ / @</code> и переносы"
        )

    return True, ""


def _title_check_cooldown(user_id: int) -> tuple:
    """
    Возвращает (can_change: bool, left_text: str).
    """
    _, changed_at = get_title(user_id)
    if not changed_at:
        return True, ""

    try:
        last_dt = datetime.fromisoformat(changed_at)
    except ValueError:
        return True, ""

    elapsed = datetime.now() - last_dt
    if elapsed >= TITLE_COOLDOWN:
        return True, ""

    remaining = TITLE_COOLDOWN - elapsed
    h = remaining.seconds // 3600
    m = (remaining.seconds % 3600) // 60
    return False, f"{h} ч {m} мин"


def _build_title_screen(user_id: int) -> tuple:
    """Экран /title без аргументов."""
    current_title, changed_at = get_title(user_id)
    vip = is_vip_active(user_id)
    max_len = _title_max_len(vip)

    if current_title:
        head = f"🏷️ Твой титул: <b>{current_title}</b>"
    else:
        head = "🏷️ Титул не установлен"

    lines = [head]

    if changed_at:
        lines.append(f"└─ Изменён: {_format_time_ago(changed_at)}")

    lines.append("")
    if vip:
        lines.append(f"📋 1–{max_len} символов · 👑 VIP")
    else:
        lines.append(f"📋 1–{max_len} символа · VIP — до {TITLE_MAX_LEN_VIP}")
    lines.append("└─ Без <code>&lt; &gt; \\ / @</code> и переносов")
    lines.append("└─ Титул должен быть уникальным")
    lines.append("")

    can_change, left_text = _title_check_cooldown(user_id)

    if not can_change:
        lines.append(f"⏳ Смена: <b>через {left_text}</b>")
        lines.append("")

    if current_title:
        lines.append("<b>Убрать:</b> <code>/title</code> без текста")
    lines.append("<b>Установить:</b> <code>/title [текст]</code>")

    text = "\n".join(lines)

    kb_rows = []
    if can_change and current_title:
        kb_rows.append([
            InlineKeyboardButton(
                text="🗑️ Убрать титул",
                callback_data="title_remove"
            ),
        ])

    kb = InlineKeyboardMarkup(inline_keyboard=kb_rows) if kb_rows else None
    return text, kb


@dp.message(Command("title"))
async def cmd_title(message: Message):
    log_cmd("🏷️ /title", message)
    user = message.from_user
    ensure_user(user)

    args = message.text.split(maxsplit=1)

    # ─── Без аргумента — показать экран ───
    if len(args) < 2 or not args[1].strip():
        # Если титул есть — убираем (по исходному поведению: /title без текста = убрать)
        current_title, _ = get_title(user.id)

        if current_title:
            can_change, left_text = _title_check_cooldown(user.id)
            if not can_change:
                await message.answer(
                    f"⏳ <b>Титул можно менять раз в 12 часов</b>\n"
                    f"└─ Следующий раз через: <b>{left_text}</b>",
                    parse_mode="HTML",
                    reply_to_message_id=message.message_id
                )
                return

            clear_title(user.id)
            await message.answer(
                f"✅ <b>Титул убран</b>\n└─ Было: <b>{current_title}</b>",
                parse_mode="HTML",
                reply_to_message_id=message.message_id
            )
            return

        # Титула нет — показываем экран
        text, kb = _build_title_screen(user.id)
        await message.answer(
            text, parse_mode="HTML", reply_markup=kb,
            reply_to_message_id=message.message_id
        )
        return

    # ─── С аргументом — установить титул ───
    new_title = args[1].strip()
    vip = is_vip_active(user.id)

    # ─── Валидация формата ───
    ok, err = _title_validate(new_title, vip)
    if not ok:
        await message.answer(
            err,
            parse_mode="HTML",
            reply_to_message_id=message.message_id
        )
        return

    # ─── Проверка уникальности ───
    if title_is_taken(new_title, exclude_user_id=user.id):
        await message.answer(
            f"❌ <b>Титул «{new_title}» уже занят</b>\n"
            f"└─ Выбери другой",
            parse_mode="HTML",
            reply_to_message_id=message.message_id
        )
        return

    # ─── Кулдаун ───
    can_change, left_text = _title_check_cooldown(user.id)
    if not can_change:
        vip_hint = "" if vip else "\n\n💡 VIP меняет титул раз в 12 часов тоже"
        await message.answer(
            f"⏳ <b>Титул можно менять раз в 12 часов</b>\n"
            f"└─ Следующий раз через: <b>{left_text}</b>{vip_hint}",
            parse_mode="HTML",
            reply_to_message_id=message.message_id
        )
        return

    # ─── Устанавливаем ───
    set_title(user.id, new_title)

    vip_note = " 👑" if vip else ""

    await message.answer(
        f"✅ <b>Титул установлен!</b>{vip_note}\n"
        f"└─ Новый: <b>{new_title}</b>\n"
        f"└─ В топе: <b>{user.full_name} [{new_title}]</b>\n\n"
        f"💡 Менять можно раз в 12 часов",
        parse_mode="HTML",
        reply_to_message_id=message.message_id
    )

    await log_to_channel(
        f"🏷️ <b>Смена титула</b>\n"
        f"└─ Юзер: {user.full_name} (<code>{user.id}</code>)\n"
        f"└─ Новый титул: <b>{new_title}</b>\n"
        f"└─ VIP: {'да' if vip else 'нет'}"
    )


# =====================================
#  CALLBACK'И ДЛЯ /title
# =====================================

@dp.callback_query(F.data == "title_remove")
async def cb_title_remove(callback: CallbackQuery):
    user_id = callback.from_user.id

    current_title, _ = get_title(user_id)
    if not current_title:
        await callback.answer("ℹ️ У тебя нет титула", show_alert=True)
        return

    can_change, left_text = _title_check_cooldown(user_id)
    if not can_change:
        await callback.answer(
            f"⏳ Убрать можно через {left_text}",
            show_alert=True
        )
        return

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="✅ Убрать",
                callback_data="title_remove_confirm"
            ),
            InlineKeyboardButton(
                text="❌ Отмена",
                callback_data="title_remove_cancel"
            ),
        ]
    ])

    try:
        await callback.message.edit_text(
            f"🗑️ <b>Убрать титул?</b>\n\n"
            f"└─ Текущий: <b>{current_title}</b>\n"
            f"└─ В топе будет без титула\n\n"
            f"💡 Запустит кулдаун 12ч",
            parse_mode="HTML",
            reply_markup=kb
        )
    except Exception:
        pass
    await callback.answer()


@dp.callback_query(F.data == "title_remove_confirm")
async def cb_title_remove_confirm(callback: CallbackQuery):
    user_id = callback.from_user.id

    clear_title(user_id)

    try:
        await callback.message.edit_text(
            "✅ <b>Титул убран</b>\n\n"
            "└─ В топе будешь без титула",
            parse_mode="HTML"
        )
    except Exception:
        pass

    await callback.answer("✅ Убран")


@dp.callback_query(F.data == "title_remove_cancel")
async def cb_title_remove_cancel(callback: CallbackQuery):
    user_id = callback.from_user.id
    text, kb = _build_title_screen(user_id)

    try:
        await callback.message.edit_text(
            text, parse_mode="HTML", reply_markup=kb
        )
    except Exception:
        pass
    await callback.answer("❌ Отменено")

@dp.message(Command("rob"))
async def cmd_rob(message: Message):
    log_cmd("🥷 /rob", message)
    user = message.from_user
    ensure_user(user)

    target_id = None
    target_name = None
    target_obj = None

    args = message.text.split()[1:]
    target_arg = args[0] if args else None

    # ─── Поиск цели ───
    if message.reply_to_message:
        target = message.reply_to_message.from_user
        target_id = target.id
        target_name = target.full_name
        target_obj = target
    elif target_arg:
        # Ищем по @username или custom_id
        conn = sqlite3.connect("users.db")
        cur = conn.cursor()
        
        if target_arg.isdigit():
            cur.execute("SELECT user_id, full_name FROM users WHERE custom_id = ?", (int(target_arg),))
        else:
            uname = target_arg.lstrip("@")
            cur.execute("SELECT user_id, full_name FROM users WHERE LOWER(username) = LOWER(?)", (uname,))
            
        row = cur.fetchone()
        conn.close()
        
        if row:
            target_id = row[0]
            target_name = row[1]
        else:
            await message.answer("❌ Пользователь не найден")
            return
    else:
        await message.answer(
            "❌ Использование:\n"
            "└─ ответь на сообщение: /rob\n"
            "└─ или /rob @username\n"
            "└─ или /rob [ID]",
            parse_mode="HTML"
        )
        return

    # ─── Проверка: цель — бот ───
    if target_obj and target_obj.is_bot:
        await message.answer(
            "🤖 <b>Бота конечно хорошо грабить, но выбери другую цель, "
            "вдруг повезёт выбить сумму больше чем -100 msg...</b>",
            parse_mode="HTML"
        )
        return

    if target_id == user.id:
        await message.answer("😄 Нельзя грабить самого себя")
        return

    # ─── Кулдаун ───
    robber_vip = is_vip_active(user.id)
    cooldown = ROB_COOLDOWN_VIP if robber_vip else ROB_COOLDOWN

    last_rob = get_last_rob(user.id)
    if last_rob:
        try:
            last_dt = datetime.fromisoformat(last_rob)
            elapsed = datetime.now() - last_dt
            if elapsed < cooldown:
                remaining = cooldown - elapsed
                total_seconds = int(remaining.total_seconds())

                if total_seconds < 60:
                    time_text = "меньше минуты"
                else:
                    minutes = total_seconds // 60
                    text = f"{minutes} минут"
                    if minutes % 10 == 1 and minutes % 100 != 11:
                        time_text = f"{minutes} минуту"
                    elif 2 <= minutes % 10 <= 4 and not (12 <= minutes % 100 <= 14):
                        time_text = f"{minutes} минуты"
                    else:
                        time_text = f"{minutes} минут"

                await message.answer(
                    f"⏳ <b>Вы уже ограбили человека, ждите {time_text}</b>",
                    parse_mode="HTML"
                )
                return
        except ValueError:
            pass

    # ─── Проверки цели ───
    ensure_user_by_id(target_id)
    target_data = get_user(target_id)
    if not target_data:
        await message.answer("❌ Цель не найдена")
        return

    target_balance = get_balance(target_id)
    if target_balance <= 0:
        await message.answer(f"❌ У {target_name} нет msg для грабежа")
        return

    # ─── Логика ограбления ───
    lock = get_user_lock(user.id)
    async with lock:
        robber_balance = get_balance(user.id)
        target_vip = is_vip_active(target_id)

        # Шансы успеха
        if target_vip:
            success_chance = 0.15
            steal_rate = 0.25
            penalty_rate = 0.05
        else:
            success_chance = 0.10
            steal_rate = 0.15
            penalty_rate = 0.10

        set_last_rob(user.id)
        success = random.random() < success_chance

        vip_suffix = " | цель с VIP" if target_vip else ""

        if success:
            steal_amount = int(target_balance * steal_rate)
            if steal_amount < 1:
                steal_amount = 1
            if steal_amount > target_balance:
                steal_amount = target_balance

            add_balance(target_id, -steal_amount)
            new_balance = add_balance(user.id, steal_amount)
            log_transaction(user.id, target_id, steal_amount, "rob_success")

            phrase = random.choice(ROB_SUCCESS_PHRASES)
            body = phrase.format(target=target_name, amount=f"{steal_amount:,}")

            await message.answer(
                f"🥷 <b>УСПЕХ{vip_suffix}</b>\n\n"
                f"{body}\n\n"
                f"└─ Твой баланс: <b>{new_balance:,}</b> msg",
                parse_mode="HTML"
            )

            try:
                await bot.send_message(
                    target_id,
                    f"🥷 <b>Тебя ограбили!</b>\n"
                    f"└─ Вор: {user.full_name}\n"
                    f"└─ Украдено: <b>-{steal_amount:,}</b> msg"
                )
            except Exception:
                pass

            if steal_amount >= 5000:
                await log_to_channel(
                    f"🥷 <b>Крупное ограбление</b>\n"
                    f"└─ Вор: {user.full_name} (<code>{user.id}</code>)\n"
                    f"└─ Жертва: {target_name} (<code>{target_id}</code>)\n"
                    f"└─ Украдено: <b>{steal_amount:,}</b> msg"
                )

        else:
            penalty = int(robber_balance * penalty_rate)
            if penalty < 1:
                penalty = 1
            if penalty > robber_balance:
                penalty = robber_balance

            new_balance = add_balance(user.id, -penalty)
            log_transaction(user.id, user.id, -penalty, "rob_fail")

            phrase = random.choice(ROB_FAIL_PHRASES)
            body = phrase.format(target=target_name, penalty=f"{penalty:,}")

            await message.answer(
                f"🚔 <b>ПРОВАЛ{vip_suffix}</b>\n\n"
                f"{body}\n\n"
                f"└─ Твой баланс: <b>{new_balance:,}</b> msg",
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

            if penalty >= 5000:
                await log_to_channel(
                    f"🚔 <b>Крупный провал ограбления</b>\n"
                    f"└─ Вор: {user.full_name} (<code>{user.id}</code>)\n"
                    f"└─ Жертва: {target_name} (<code>{target_id}</code>)\n"
                    f"└─ Штраф: <b>{penalty:,}</b> msg"
                )
# ==================================

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

BANK_PHOTO = "AgACAgIAAxkBAAIKimrKE3d0E9-9E7T83gHn_DRKCx_WAAIvH2sbJWsQSq4FP9M8Qc37AQADAgADeAADPQQ"

# -----------------------------------
def build_bank_text_and_kb(user_id):
    """Собирает главный экран /bank."""
    bank_ensure(user_id)
    info = bank_get(user_id)
    vip = is_vip_active(user_id)
    
    # Новые ставки
    rate = 0.01 if vip else 0.005
    rate_text = "1%" if vip else "0.5%"
    
    # Новые лимиты
    max_limit = BANK_MAX_BALANCE_VIP if vip else BANK_MAX_BALANCE_NORMAL

    def e(emoji_id, fallback):
        return _p(emoji_id, fallback) if vip else fallback

    E_BANK  = e(PREM_BANK, "🏦")
    E_MONEY = e(PREM_MONEY, "💰")
    E_RATE  = e(PREM_RATE, "📈")

    vip_mark = f' {_p(PREM_TOP1, "👑")}' if vip else ""

    balance = info["balance"]
    total_earned = info["total_earned"]
    earned_now = info["earned_now"]

    # Прогноз (считаем по новой ставке, но с учетом лимита)
    effective_balance = min(balance, max_limit)
    if effective_balance > 0:
        forecast_10h = int(effective_balance * ((1 + rate) ** 10 - 1))
        forecast_24h = int(effective_balance * ((1 + rate) ** 24 - 1))
    else:
        forecast_10h = 0
        forecast_24h = 0

    # Время до начисления
    now_kr = datetime.now(timezone(timedelta(hours=7))).replace(tzinfo=None)
    minutes_passed = now_kr.minute
    minutes_left = 60 - minutes_passed
    if minutes_left == 60:
        minutes_left = 0

    filled = int((minutes_passed / 60) * 10)
    if filled > 10:
        filled = 10
    bar = "▰" * filled + "▱" * (10 - filled)

    # Место в топе банков
    try:
        conn = sqlite3.connect("users.db")
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM banks WHERE balance > ?", (balance,))
        rank = cur.fetchone()[0] + 1
        conn.close()

        if rank == 1:
            rank_line = f"└─ 🥇 <b>Ты в топе банков!</b>"
        else:
            rank_line = f"└─ 🏆 Место в топе: <b>#{rank}</b>"
    except Exception:
        rank_line = ""

    lines = [
        f"{E_BANK} <b>Твой банк</b>{vip_mark}",
        "",
        f"└─ {E_MONEY} На счету: <b>{balance:,}</b> / {max_limit:,} msg", # <-- Показываем лимит
        f"└─ {E_RATE} Ставка: <b>{rate_text} в час</b>",
        "",
    ]

    if balance > 0:
        lines.append(f"📊 <b>Прогноз:</b>")
        lines.append(f"└─ За 10ч: <b>+{forecast_10h:,}</b> msg")
        lines.append(f"└─ За 24ч: <b>+{forecast_24h:,}</b> msg")
        
        if balance > max_limit:
            lines.append(f"└─ ⚠️ Сумма выше лимита не приносит дохода!")
        lines.append("")

    lines.append(f"⏳ <b>До начисления:</b> {minutes_left} мин")
    lines.append(f"{bar}")

    if earned_now > 0:
        lines.append("")
        lines.append(f"💵 Начислено сейчас: <b>+{earned_now:,}</b> msg")

    if total_earned > 0:
        lines.append("")
        lines.append(f"✅ Всего заработано: <b>{total_earned:,}</b> msg")

    if rank_line:
        lines.append("")
        lines.append(rank_line)

    text = "\n".join(lines)

    kb_rows = []

    wallet = get_balance(user_id)
    if wallet > 0:
        kb_rows.append([
            InlineKeyboardButton(
                text="📥 Положить",
                callback_data=f"bank_add_{user_id}"
            ),
            InlineKeyboardButton(
                text=f"📤 Снять всё",
                callback_data=f"bank_take_all_{user_id}"
            ),
        ])
    elif balance > 0:
        kb_rows.append([
            InlineKeyboardButton(
                text=f"📤 Снять всё ({balance:,})",
                callback_data=f"bank_take_all_{user_id}"
            ),
        ])

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
# ===================================
#  CALLBACK: положить в банк
# ===================================

def _bank_add_kb(user_id: int, current_bank: int) -> InlineKeyboardMarkup:
    """Клавиатура быстрых сумм для пополнения."""
    vip = is_vip_active(user_id)
    max_limit = BANK_MAX_BALANCE_VIP if vip else BANK_MAX_BALANCE_NORMAL
    space_left = max_limit - current_bank

    rows = [
        [
            InlineKeyboardButton(text="1к",    callback_data=f"bank_add_do_1000_{user_id}"),
            InlineKeyboardButton(text="5к",    callback_data=f"bank_add_do_5000_{user_id}"),
            InlineKeyboardButton(text="10к",   callback_data=f"bank_add_do_10000_{user_id}"),
        ],
        [
            InlineKeyboardButton(text="50к",   callback_data=f"bank_add_do_50000_{user_id}"),
            InlineKeyboardButton(text="100к",  callback_data=f"bank_add_do_100000_{user_id}"),
        ]
    ]
    
    # Добавляем кнопку "Максимум", если есть свободное место
    if space_left > 0:
        rows.append([
            InlineKeyboardButton(
                text=f"📥 Положить всё доступное ({space_left:,})", 
                callback_data=f"bank_add_do_{space_left}_{user_id}"
            )
        ])
        
    rows.append([
        InlineKeyboardButton(text="◀️ Назад", callback_data=f"bank_back_{user_id}"),
    ])

    return InlineKeyboardMarkup(inline_keyboard=rows)


@dp.callback_query(F.data.startswith("bank_add_") & ~F.data.startswith("bank_add_do_"))
async def cb_bank_add(callback: CallbackQuery):
    parts = callback.data.split("_")
    # bank_add_{user_id}
    if len(parts) != 3:
        await callback.answer("⚠️ Ошибка данных", show_alert=True)
        return

    try:
        owner_id = int(parts[2])
    except ValueError:
        await callback.answer("⚠️ Ошибка данных", show_alert=True)
        return

    if callback.from_user.id != owner_id:
        await callback.answer("❌ Это не твой банк", show_alert=True)
        return

    wallet = get_balance(owner_id)
    info = bank_get(owner_id)
    bank_balance = info["balance"]

    text = (
        f"📥 <b>Положить в банк</b>\n"
        f"\n"
        f"└─ 💰 Кошелёк: <b>{wallet:,}</b> msg\n"
        f"└─ 🏦 В банке: <b>{bank_balance:,}</b> msg\n"
        f"\n"
        f"<b>Выбери сумму:</b>"
    )

    kb = _bank_add_kb(owner_id)

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
        print(f"[BANK] Ошибка: {e}")
    await callback.answer()


@dp.callback_query(F.data.startswith("bank_add_do_"))
async def cb_bank_add_do(callback: CallbackQuery):
    parts = callback.data.split("_")
    # bank_add_do_{amount}_{user_id}
    if len(parts) != 5:
        await callback.answer("⚠️ Ошибка данных", show_alert=True)
        return

    try:
        amount = int(parts[3])
        owner_id = int(parts[4])
    except ValueError:
        await callback.answer("⚠️ Ошибка данных", show_alert=True)
        return

    if callback.from_user.id != owner_id:
        await callback.answer("❌ Это не твой банк", show_alert=True)
        return

    wallet = get_balance(owner_id)
    if wallet < amount:
        await callback.answer(f"❌ У тебя только {wallet:,} msg в кошельке", show_alert=True)
        return

    # ─── ПОКАЗЫВАЕМ ПОДТВЕРЖДЕНИЕ ───
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=f"✅ Да, положить {amount:,}",
                callback_data=f"bank_add_confirm_{amount}_{owner_id}"
            ),
            InlineKeyboardButton(
                text="❌ Отмена",
                callback_data=f"bank_add_cancel_{owner_id}"
            ),
        ]
    ])

    try:
        await callback.message.edit_text(
            f"📥 <b>Подтверди операцию</b>\n\n"
            f"└─ Ты хочешь положить: <b>{amount:,}</b> msg\n"
            f"└─ В кошельке останется: <b>{wallet - amount:,}</b> msg",
            parse_mode="HTML",
            reply_markup=kb
        )
    except Exception as e:
        print(f"[BANK] Ошибка: {e}")
    await callback.answer()

@dp.callback_query(F.data.startswith("bank_add_confirm_"))
async def cb_bank_add_confirm(callback: CallbackQuery):
    parts = callback.data.split("_")
    # bank_add_confirm_{amount}_{user_id}
    if len(parts) != 5:
        await callback.answer("⚠️ Ошибка данных", show_alert=True)
        return

    try:
        amount = int(parts[3])
        owner_id = int(parts[4])
    except ValueError:
        await callback.answer("⚠️ Ошибка данных", show_alert=True)
        return

    if callback.from_user.id != owner_id:
        await callback.answer("❌ Это не твой банк", show_alert=True)
        return

    # ТУТ УЖЕ ВЫПОЛНЯЕМ ОПЕРАЦИЮ
    ok, info, new_bank, new_wallet, _ = bank_put(owner_id, amount)
    
    if not ok:
        await callback.answer(f"❌ {info.replace('<b>', '').replace('</b>', '')}", show_alert=True)
        return

    text, kb = build_bank_text_and_kb(owner_id)

    try:
        if callback.message.photo:
            await callback.message.edit_caption(caption=text, parse_mode="HTML", reply_markup=kb)
        else:
            await callback.message.edit_text(text, parse_mode="HTML", reply_markup=kb)
    except Exception as e:
        print(f"[BANK] Ошибка: {e}")

    await callback.answer(f"📥 +{amount:,} msg")


@dp.callback_query(F.data.startswith("bank_add_cancel_"))
async def cb_bank_add_cancel(callback: CallbackQuery):
    parts = callback.data.split("_")
    # bank_add_cancel_{user_id}
    if len(parts) != 4:
        await callback.answer("⚠️ Ошибка данных", show_alert=True)
        return

    try:
        owner_id = int(parts[3])
    except ValueError:
        await callback.answer("⚠️ Ошибка данных", show_alert=True)
        return

    if callback.from_user.id != owner_id:
        await callback.answer("❌ Это не твой банк", show_alert=True)
        return

    # Возвращаемся в главное меню банка
    text, kb = build_bank_text_and_kb(owner_id)

    try:
        if callback.message.photo:
            await callback.message.edit_caption(caption=text, parse_mode="HTML", reply_markup=kb)
        else:
            await callback.message.edit_text(text, parse_mode="HTML", reply_markup=kb)
    except Exception as e:
        print(f"[BANK] Ошибка: {e}")

    await callback.answer("❌ Отменено")

@dp.callback_query(F.data.startswith("bank_back_"))
async def cb_bank_back(callback: CallbackQuery):
    parts = callback.data.split("_")
    # bank_back_{user_id}
    if len(parts) != 3:
        await callback.answer("⚠️ Ошибка данных", show_alert=True)
        return

    try:
        owner_id = int(parts[2])
    except ValueError:
        await callback.answer("⚠️ Ошибка данных", show_alert=True)
        return

    if callback.from_user.id != owner_id:
        await callback.answer("❌ Это не твой банк", show_alert=True)
        return

    text, kb = build_bank_text_and_kb(owner_id)

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
        print(f"[BANK] Ошибка: {e}")
    await callback.answer()
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

    vip = is_vip_active(user.id)

    def e(emoji_id, fallback):
        return _p(emoji_id, fallback) if vip else fallback

    E_IN    = e(PREM_IN, "📥")
    E_CHECK = e(PREM_CHECK, "✅")
    E_ERR   = e(PREM_ERR, "❌")

    args = message.text.split()[1:]
    if not args:
        # Показываем меню с кнопками
        wallet = get_balance(user.id)
        info = bank_get(user.id)
        bank_balance = info["balance"]
        
        await message.answer(
            f"{E_IN} <b>Положить в банк</b>\n\n"
            f"└─ 💰 Кошелёк: <b>{wallet:,}</b> msg\n"
            f"└─ 🏦 В банке: <b>{bank_balance:,}</b> msg\n\n"
            f"Выбери сумму:",
            parse_mode="HTML",
            reply_markup=_bank_add_kb(user.id, bank_balance)
        )
        return

    try:
        amount = int(args[0])
    except ValueError:
        await message.answer(f"😅 «{args[0]}» — это не число\n└─ Пример: /bankput 500", parse_mode="HTML")
        return

    if amount <= 0:
        await message.answer(f"{E_ERR} Сумма должна быть положительной", parse_mode="HTML")
        return

    # ТУТ БЕЗ КНОПОК — СРАЗУ КЛАДЕМ
    ok, info, new_bank, new_wallet, suggest_amount = bank_put(user.id, amount)
    
    if not ok:
        if suggest_amount > 0:
            kb = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(
                    text=f"📥 Положить {suggest_amount:,}",
                    callback_data=f"bank_put_suggest_{suggest_amount}_{user.id}"
                )]
            ])
            await message.answer(f"{E_ERR} {info}", parse_mode="HTML", reply_markup=kb)
        else:
            await message.answer(f"{E_ERR} {info}", parse_mode="HTML")
        return

    await message.answer(
        f"{E_CHECK} <b>Положено в банк</b>\n"
        f"└─ Внесено: <b>{amount:,}</b> msg\n"
        f"└─ В банке: {new_bank:,} msg\n"
        f"└─ В кошельке: {new_wallet:,} msg",
        parse_mode="HTML"
    )
# -----------------------------------
@dp.callback_query(F.data.startswith("bank_put_suggest_"))
async def cb_bank_put_suggest(callback: CallbackQuery):
    parts = callback.data.split("_")
    # Формат: bank_put_suggest_{amount}_{user_id}
    if len(parts) != 5:
        await callback.answer("⚠️ Ошибка данных", show_alert=True)
        return

    try:
        amount = int(parts[3])
        owner_id = int(parts[4])
    except ValueError:
        await callback.answer("⚠️ Ошибка данных", show_alert=True)
        return

    if callback.from_user.id != owner_id:
        await callback.answer("❌ Это не твой банк", show_alert=True)
        return

    # Выполняем пополнение на предложенную сумму
    ok, info, new_bank, new_wallet, _ = bank_put(owner_id, amount)
    
    if not ok:
        await callback.answer(f"❌ {info.replace('<b>', '').replace('</b>', '')}", show_alert=True)
        return

    # Меняем сообщение на успешное
    try:
        await callback.message.edit_text(
            f"✅ <b>Положено в банк</b>\n"
            f"└─ Внесено: <b>{amount:,}</b> msg\n"
            f"└─ В банке: {new_bank:,} msg\n"
            f"└─ В кошельке: {new_wallet:,} msg",
            parse_mode="HTML"
        )
    except Exception:
        pass

    await callback.answer(f"📥 +{amount:,} msg")


# -----------------------------------
@dp.message(Command("banktake"))
async def cmd_banktake(message: Message):
    log_cmd("📤 /banktake", message)
    user = message.from_user
    ensure_user(user)

    vip = is_vip_active(user.id)

    def e(emoji_id, fallback):
        return _p(emoji_id, fallback) if vip else fallback

    E_OUT   = e(PREM_OUT, "📤")
    E_MONEY = e(PREM_MONEY, "💰")
    E_CHECK = e(PREM_CHECK, "✅")
    E_ERR   = e(PREM_ERR, "❌")

    args = message.text.split()[1:]
    if not args:
        info = bank_get(user.id)
        if info["balance"] <= 0:
            await message.answer(
                f"{E_OUT} <b>Снять из банка</b>\n\n"
                f"└─ {E_MONEY} В банке пусто",
                parse_mode="HTML"
            )
            return

        await message.answer(
            f"{E_OUT} <b>Снять из банка</b>\n\n"
            f"└─ {E_MONEY} Доступно: <b>{info['balance']:,}</b> msg\n\n"
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
            f"{E_ERR} Сумма должна быть положительной",
            parse_mode="HTML"
        )
        return

    ok, info, new_bank, new_wallet = bank_take(user.id, amount)
    if not ok:
        await message.answer(f"{E_ERR} {info}", parse_mode="HTML")
        return

    await message.answer(
        f"{E_CHECK} <b>Снято из банка</b>\n"
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


# =========================================================
#  ПРОВЕРКА ССЫЛОК В АНОНИМКАХ
# =========================================================

import re

LINK_PATTERNS = [
    r"t\.me/",
    r"telegram\.me/",
    r"telegram\.dog/",
    r"tg://",
    r"@[a-zA-Z0-9_]{3,}",
    r"https?://",
    r"ttps://",
    r"htp://",
    r"htps://",
    r"ftp://",
    r"ftps://",
    r"www\.",
    r"wa\.me/",
    r"whatsapp\.com/",
    r"whatsapp://",
    r"viber://",
    r"viber\.com/",
    r"signal\.org/",
    r"vk\.com/",
    r"vkontakte\.ru/",
    r"ok\.ru/",
    r"instagram\.com/",
    r"instagr\.am/",
    r"facebook\.com/",
    r"fb\.com/",
    r"twitter\.com/",
    r"x\.com/",
    r"tiktok\.com/",
    r"youtube\.com/",
    r"youtu\.be/",
    r"twitch\.tv/",
    r"discord\.gg/",
    r"discord\.com/",
    r"reddit\.com/",
    r"pinterest\.com/",
    r"dropbox\.com/",
    r"drive\.google\.com/",
    r"mega\.nz/",
    r"mediafire\.com/",
    r"mega\.io/",
    r"steamcommunity\.com/",
    r"steampowered\.com/",
    r"wildberries\.ru/",
    r"ozon\.ru/",
    r"avito\.ru/",
    r"binance\.com/",
    r"bybit\.com/",
    r"crypto\.com/",
    r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b",
    r"\b[a-zA-Z0-9-]+\.(com|ru|net|org|io|me|gg|tv|info|biz|xyz|online|site|top|club|pro|app)\b",
    r"t\s*\.\s*me",
    r"@\s*[a-zA-Z0-9_]{3,}",
]


def _contains_link(text: str) -> bool:
    """Проверяет, есть ли в тексте ссылки, домены или @username."""
    if not text:
        return False
    text_lower = text.lower()
    for pattern in LINK_PATTERNS:
        if re.search(pattern, text_lower):
            return True
    return False


async def _log_link_block(user, target_id, text):
    """Логирует попытку отправки ссылки в /anon."""
    try:
        await log_to_channel(
            f"🚫 <b>Заблокирована ссылка в /anon</b>\n"
            f"└─ От: {user.full_name} (<code>{user.id}</code>)\n"
            f"└─ Кому: <code>{target_id}</code>\n"
            f"└─ Текст:\n<blockquote>{text[:200]}</blockquote>"
        )
    except Exception as e:
        print(f"[ANON-LOG] Ошибка: {e}")


# =====================================
#  /anon — анонимные сообщения
# ======================================
@dp.message(Command("anon"))
async def cmd_anon(message: Message):
    log_cmd("💌 /anon", message)
    user = message.from_user
    ensure_user(user)

    # ─── Мут анонимок ───
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

    args = message.text.split(maxsplit=1)
    
    target_id = None
    target_name = None
    text = ""

    if message.reply_to_message:
        # Если реплай — текст берем после команды
        if len(args) < 2:
            await message.answer("❌ Напиши текст: /anon [текст]", parse_mode="HTML")
            return
        text = args[1].strip()
        target_id, target_name = _find_target_by_arg(message)
    else:
        # Если без реплая — парсим аргументы: /anon @user текст или /anon ID текст
        parts = message.text.split(maxsplit=2)
        if len(parts) < 3:
            await message.answer(
                "❌ Использование:\n"
                "└─ ответь на сообщение: /anon [текст]\n"
                "└─ или /anon @username [текст]\n"
                "└─ или /anon [ID] [текст]",
                parse_mode="HTML"
            )
            return
        
        target_arg = parts[1]
        text = parts[2].strip()
        target_id, target_name = _find_target_by_arg(message, target_arg)

    if target_id is None:
        await message.answer("❌ Пользователь не найден")
        return

    # ─── Проверки ───
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

    # ─── Проверка ссылок ───
    if _contains_link(text):
        await message.answer(
            "❌ <b>Ссылки запрещены</b>\n\n"
            "Анонимки со ссылками, юзернеймами и рекламой не пропускаются.",
            parse_mode="HTML"
        )
        await _log_link_block(user, target_id, text)
        return

    # ─── Анон-щит ───
    if is_anon_shield_active(target_id):
        await message.answer(
            f"🕶️ <b>У {target_name} активен анон-щит</b>\n"
            f"└─ Анонимка не доставлена\n"
            f"└─ msg не списаны"
        )
        return

    # ─── Баланс ───
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

    # ─── Списываем заранее ───
    add_balance(user.id, -PRICE_ANON)

    # ─── Кнопка «Пожаловаться» ───
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="🚨 Пожаловаться",
            callback_data=f"anon_report_{user.id}_{target_id}"
        )]
    ])

    # ─── Отправка ───
    try:
        await bot.send_message(
            target_id,
            f"💌 <b>Анонимное сообщение</b>\n\n"
            f"<blockquote>{text}</blockquote>",
            parse_mode="HTML",
            reply_markup=kb
        )
    except Exception as e:
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



async def _send_to_moderators(text: str, kb=None):
    """Отправляет уведомление владельцу + всем senior + в лог-канал."""
    recipients = set()

    for oid in OWNER_IDS:
        recipients.add(oid)

    try:
        admins = get_all_admins()
        for uid in admins.get("senior", []):
            recipients.add(uid)
        for uid in admins.get("owner", []):
            recipients.add(uid)
    except Exception as e:
        print(f"[ANON-REPORT] Ошибка: {e}")

    for uid in recipients:
        try:
            await bot.send_message(uid, text, parse_mode="HTML", reply_markup=kb)
        except Exception:
            pass

    try:
        await bot.send_message(LOG_CHANNEL_ID, text, parse_mode="HTML", reply_markup=kb)
    except Exception:
        pass

# =====================================
#  /marry, /divorce
# =====================================
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

    args = message.text.split()[1:]
    arg = args[0] if args else None

    target_id, target_name = _find_target_by_arg(message, arg)

    if target_id is None:
        await message.answer(
            "❌ Использование:\n"
            "└─ ответь на сообщение: /marry\n"
            "└─ или /marry @username\n"
            "└─ или /marry [ID]",
            parse_mode="HTML"
        )
        return

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

    spouse_name = _couple_name(spouse_id)

    # Штраф 10%
    penalty = total * 10 // 100
    remainder = total - penalty
    half1 = remainder // 2
    half2 = remainder - half1

    ok, _, _, penalty_actual = divorce_users(user.id)
    if not ok:
        await message.answer("❌ Не удалось развестись")
        return

    my_half = half1 if user.id == u1 else half2
    spouse_half = half2 if user.id == u1 else half1

    await message.answer(
        f"💔 <b>Развод</b>\n\n"
        f"└─ Бывший супруг: {spouse_name}\n"
        f"└─ Общий счёт: {total:,} msg\n"
        f"└─ Штраф 10%: <b>-{penalty_actual:,}</b> msg (в казну)\n"
        f"└─ Твоя доля: <b>{my_half:,}</b> msg\n\n"
        f"⏳ Кулдаун на брак: 7 дней",
        parse_mode="HTML"
    )

    try:
        await bot.send_message(
            spouse_id,
            f"💔 <b>Развод</b>\n\n"
            f"└─ Бывший супруг: {_couple_name(user.id)}\n"
            f"└─ Общий счёт: {total:,} msg\n"
            f"└─ Штраф 10%: -{penalty_actual:,} msg\n"
            f"└─ Твоя доля: <b>{spouse_half:,}</b> msg\n\n"
            f"⏳ Кулдаун на брак: 7 дней",
            parse_mode="HTML"
        )
    except Exception:
        pass

    await log_to_channel(
        f"💔 <b>Развод</b>\n"
        f"└─ Пара: {_couple_name(u1)} 💍 {_couple_name(u2)}\n"
        f"└─ Штраф: <b>{penalty_actual:,}</b> msg → в казну\n"
        f"└─ Инициатор: {_couple_name(user.id)}"
    )


# ==================================
#  CALLBACK: marry (с возвратом msg при ошибке)
# ==================================
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

        # marry_users теперь возвращает (ok, err)
        ok, err = marry_users(from_id, to_id)
        if not ok:
            # ❗ Возврат msg при ошибке
            add_balance(from_id, MARRY_PRICE)
            _marry_invites.pop(invite_id, None)
            await callback.message.edit_text(f"❌ {err}")
            await callback.answer()
            return

        _marry_invites.pop(invite_id, None)

        # ─── Имена для отображения ───
        name_from = _couple_name(from_id)
        name_to = _couple_name(to_id)

        try:
            await callback.message.edit_text(
                f"💍 <b>Брак заключён!</b>\n\n"
                f"└─ {name_from} 💕 {name_to}\n\n"
                f"💰 Стоимость: {MARRY_PRICE} msg (оплатил инициатор)\n"
                f"👥 Теперь у вас общий счёт\n"
                f"💍 Смотреть пару: /couple\n"
                f"💔 Развод: /divorce",
                parse_mode="HTML"
            )
        except Exception:
            pass

        try:
            await bot.send_message(
                from_id,
                f"💍 <b>Тебе ответили «Да»!</b>\n\n"
                f"└─ Супруг: <b>{name_to}</b>\n"
                f"└─ Теперь у вас общий счёт\n"
                f"└─ /couple — данные пары",
                parse_mode="HTML"
            )
        except Exception:
            pass

        log_transaction(from_id, to_id, -MARRY_PRICE, "marry")

        # ─── Объявление в канал ───
        try:
            channel_kb = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(
                    text="💐 Поздравить",
                    url=f"https://t.me/{BOT_USERNAME}?start=gift_{from_id}_{to_id}"
                )]
            ])

            date_str = datetime.now().strftime("%d.%m.%Y")

            await bot.send_message(
                chat_id=BROADCAST_CHANNEL_ID,
                text=(
                    f"💍 <b>Свадьба!</b>\n\n"
                    f"{name_from} 💕 {name_to}\n\n"
                    f"└─ Дата: {date_str}\n"
                    f"└─ Поздравьте пару 👇"
                ),
                parse_mode="HTML",
                reply_markup=channel_kb
            )
        except Exception as e:
            print(f"[MARRY] Ошибка объявления в канал: {e}")

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
            
        target_id, target_name = _find_target_by_arg(message)
    else:
        if len(args) < 2:
            await message.answer(
                "❌ Использование:\n"
                "└─ ответь на сообщение: <code>/duel [ставка]</code>\n"
                "└─ или <code>/duel @username [ставка]</code>\n"
                "└─ или <code>/duel [ID] [ставка]</code>",
                parse_mode="HTML"
            )
            return

        target_arg = args[0]
        try:
            bet = int(args[1])
        except ValueError:
            await message.answer("❌ Ставка должна быть числом")
            return

        target_id, target_name = _find_target_by_arg(message, target_arg)

    if target_id is None:
        await message.answer("❌ Пользователь не найден")
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
        f"🎯 Аминки: 4 у каждого\n"
        f"⏳ Действует 5 минут\n\n"
        f"<i>Ждём ответа...</i>",
        parse_mode="HTML",
        reply_markup=kb
    )


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
#  ЛОГИ В КАНАЛ
# =========================================================

LOG_CHANNEL_ID = -1004394718576   # ID канала @amina_logs
LOG_ENABLED = True


async def log_to_channel(text: str):
    """Отправляет лог в канал @amina_logs."""
    if not LOG_ENABLED:
        return

    try:
        await bot.send_message(
            chat_id=LOG_CHANNEL_ID,
            text=text,
            parse_mode="HTML"
        )
    except Exception as e:
        print(f"[LOG] Ошибка отправки в канал: {e}")



# =====================================
#  /resetmsg — массовый сброс msg (90%)
# =====================================

import uuid

# Черновики подтверждения: { owner_id: {"token": str, "created_at": float} }
_reset_drafts: dict = {}


def _reset_confirm_kb(token: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="✅ Да",
                callback_data=f"resetmsg_yes_{token}"
            ),
            InlineKeyboardButton(
                text="❌ Нет",
                callback_data=f"resetmsg_no_{token}"
            ),
        ]
    ])


@dp.message(Command("resetmsg"))
async def cmd_resetmsg(message: Message):
    log_cmd("💣 /resetmsg", message)

    if message.from_user.id not in OWNER_IDS:
        await message.answer("⛔ Только для главного владельца")
        return

    if _reset_in_progress:
        await message.answer(
            "⏳ <b>Сброс уже идёт</b>\n"
            "└─ Дождись завершения",
            parse_mode="HTML"
        )
        return

    owner_id = message.from_user.id

    token = uuid.uuid4().hex[:12]
    _reset_drafts[owner_id] = {
        "token": token,
        "created_at": time.monotonic(),
    }

    await message.answer(
        "⚠️ <b>Ты точно хочешь сбросить msg?</b>\n\n"
        "└─ У всех юзеров снимется <b>90%</b> (кошелёк + банк)\n"
        "└─ У кого сумма <b>≤ 1000</b> — не тронем\n"
        "└─ Банк обнулится, остаток пойдёт в кошелёк\n"
        "└─ Каждому тронутому — уведомление в ЛС\n\n"
        "💡 Пока идёт сброс — команды будут заблокированы",
        parse_mode="HTML",
        reply_markup=_reset_confirm_kb(token)
    )


@dp.callback_query(F.data.startswith("resetmsg_no_"))
async def cb_resetmsg_no(callback: CallbackQuery):
    token = callback.data.replace("resetmsg_no_", "")

    draft = _reset_drafts.get(callback.from_user.id)
    if not draft or draft["token"] != token:
        await callback.answer("⚠️ Устарело", show_alert=True)
        return

    _reset_drafts.pop(callback.from_user.id, None)

    try:
        await callback.message.edit_text(
            "❌ <b>Сброс отменён</b>",
            parse_mode="HTML"
        )
    except Exception:
        pass
    await callback.answer("❌ Отменено")


@dp.callback_query(F.data.startswith("resetmsg_yes_"))
async def cb_resetmsg_yes(callback: CallbackQuery):
    global _reset_in_progress

    token = callback.data.replace("resetmsg_yes_", "")

    draft = _reset_drafts.get(callback.from_user.id)
    if not draft or draft["token"] != token:
        await callback.answer("⚠️ Устарело", show_alert=True)
        return

    if _reset_in_progress:
        await callback.answer("⏳ Уже идёт", show_alert=True)
        return

    # Проверка владельца
    if callback.from_user.id not in OWNER_IDS:
        await callback.answer("⛔ Нет прав", show_alert=True)
        return

    _reset_drafts.pop(callback.from_user.id, None)

    # Поднимаем флаг ДО начала любых действий
    _reset_in_progress = True

    await callback.answer("💣 Сброс запущен")

    # Сразу редактируем сообщение, чтобы второй клик не сработал
    try:
        await callback.message.edit_text(
            "⏳ <b>Сброс начался…</b>\n"
            "└─ Команды временно недоступны",
            parse_mode="HTML"
        )
    except Exception:
        pass

    # Запускаем в фоне, чтобы хендлер не висел
    asyncio.create_task(_run_resetmsg(callback.message.chat.id, callback.from_user.id))

# =====================================
#  ФАЗА 1: СБРОС (с прогрессом)
# =====================================

_reset_report_data: list = []  # глобально: данные для отчёта и уведомлений


async def _run_resetmsg(chat_id: int, owner_id: int):
    global _reset_in_progress, _reset_report_data

    _reset_report_data = []

    try:
        # ─── 1. Собираем цели ───
        print("[RESETMSG] Шаг 1: reset_get_targets()")
        try:
            targets = reset_get_targets()
            print(f"[RESETMSG] Шаг 1 OK: {len(targets)} целей")
        except Exception as e:
            import traceback
            print(f"[RESETMSG] Шаг 1 ПАДЕНИЕ: {e}\n{traceback.format_exc()}")
            return

        if not targets:
            try:
                await bot.send_message(
                    chat_id,
                    "📭 <b>Нет юзеров для сброса</b>\n"
                    "└─ У всех сумма ≤ 1000 msg",
                    parse_mode="HTML"
                )
            except Exception:
                pass
            return

        total = len(targets)

        # ─── 2. Прогресс-сообщение ───
        print("[RESETMSG] Шаг 2: send_message (progress)")
        try:
            status_msg = await bot.send_message(
                chat_id,
                f"⏳ <b>Сброс msg…</b>\n"
                f"└─ Прогресс: 0/{total}",
                parse_mode="HTML"
            )
            print("[RESETMSG] Шаг 2 OK")
        except Exception as e:
            import traceback
            print(f"[RESETMSG] Шаг 2 ПАДЕНИЕ: {e}\n{traceback.format_exc()}")
            return

        UPDATE_EVERY = 25
        processed = 0
        failed = 0

        # ─── 3. Обрабатываем каждую цель ───
        print("[RESETMSG] Шаг 3: обработка целей")
        for idx, target in enumerate(targets, start=1):
            total_amt = target["total"]

            if total_amt <= 1000:
                continue

            try:
                result = reset_apply_target(target)
                print(f"[RESETMSG] Шаг 3 OK: target {idx}, result ok={result.get('ok')}")
            except Exception as e:
                import traceback
                print(f"[RESETMSG] Шаг 3 ПАДЕНИЕ на target {idx}: {e}\n{traceback.format_exc()}")
                failed += 1
                continue

            if not result["ok"]:
                failed += 1
                continue

            _reset_report_data.append({
                "user_ids": result["user_ids"],
                "is_couple": target["is_couple"],
                "old_total": result["old_total"],
                "new_balance": result["new_balance"],
                "removed": result["removed"],
            })

            processed += 1

            if idx % UPDATE_EVERY == 0:
                try:
                    await status_msg.edit_text(
                        f"⏳ <b>Сброс msg…</b>\n"
                        f"└─ Прогресс: {idx}/{total}\n"
                        f"└─ Обработано: {processed}\n"
                        f"└─ Ошибок: {failed}",
                        parse_mode="HTML"
                    )
                except Exception:
                    pass

        print(f"[RESETMSG] Шаг 3 ИТОГ: processed={processed}, failed={failed}")

        try:
            await status_msg.edit_text(
                f"✅ <b>Сброс завершён</b>\n"
                f"└─ Обработано: {processed}\n"
                f"└─ Ошибок: {failed}\n"
                f"└─ Не тронуто (≤ 1000): {total - processed - failed}",
                parse_mode="HTML"
            )
        except Exception:
            pass

        # ─── 4. Уведомления ───
        print("[RESETMSG] Шаг 4: уведомления")
        if _reset_report_data:
            try:
                await _send_reset_notifications(chat_id)
                print("[RESETMSG] Шаг 4 OK")
            except Exception as e:
                import traceback
                print(f"[RESETMSG] Шаг 4 ПАДЕНИЕ: {e}\n{traceback.format_exc()}")

        # ─── 5. Отчёт ───
        print("[RESETMSG] Шаг 5: отчёт")
        if _reset_report_data:
            try:
                await _send_reset_report(chat_id, owner_id)
                print("[RESETMSG] Шаг 5 OK")
            except Exception as e:
                import traceback
                print(f"[RESETMSG] Шаг 5 ПАДЕНИЕ: {e}\n{traceback.format_exc()}")

    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        print(f"[RESETMSG] Критическая ошибка: {e}\n{tb}")
        try:
            await bot.send_message(
                chat_id,
                f"❌ <b>Ошибка сброса</b>\n└─ {e}",
                parse_mode="HTML"
            )
        except Exception:
            pass

    finally:
        _reset_in_progress = False
        print("[RESETMSG] Флаг блокировки снят")

# =====================================
#  ФАЗА 2: УВЕДОМЛЕНИЯ (задержка 1 сек)
# =====================================

async def _send_reset_notifications(chat_id: int):
    """
    Отправляет ЛС каждому тронутому юзеру (и обоим супругам для пар):
        Здравствуйте, у вас снято {X} msg, теперь ваш баланс: {Y} msg
    Задержка 1 сек между сообщениями.
    """
    global _reset_report_data

    if not _reset_report_data:
        return

    # ─── Собираем плоский список получателей ───
    # [(user_id, removed, new_balance), ...]
    recipients = []
    for item in _reset_report_data:
        for uid in item["user_ids"]:
            recipients.append((uid, item["removed"], item["new_balance"]))

    total = len(recipients)
    if total == 0:
        return

    # ─── Прогресс-сообщение ───
    status_msg = await bot.send_message(
        chat_id,
        f"📩 <b>Отправка уведомлений…</b>\n"
        f"└─ Прогресс: 0/{total}",
        parse_mode="HTML"
    )

    UPDATE_EVERY = 25
    sent = 0
    failed = 0

    for idx, (uid, removed, new_balance) in enumerate(recipients, start=1):
        try:
            await bot.send_message(
                uid,
                f"Здравствуйте, у вас снято {removed:,} msg, "
                f"теперь ваш баланс: {new_balance:,} msg"
            )
            sent += 1
        except Exception as e:
            failed += 1
            print(f"[RESETMSG] Не удалось уведомить {uid}: {e}")

        # Задержка 1 сек между отправками
        await asyncio.sleep(1.0)

        # Обновляем прогресс
        if idx % UPDATE_EVERY == 0:
            try:
                await status_msg.edit_text(
                    f"📩 <b>Отправка уведомлений…</b>\n"
                    f"└─ Прогресс: {idx}/{total}\n"
                    f"└─ Отправлено: {sent}\n"
                    f"└─ Ошибок: {failed}",
                    parse_mode="HTML"
                )
            except Exception:
                pass

    # Финальный прогресс
    try:
        await status_msg.edit_text(
            f"✅ <b>Уведомления отправлены</b>\n"
            f"└─ Отправлено: {sent}\n"
            f"└─ Ошибок: {failed}\n"
            f"└─ Всего: {total}",
            parse_mode="HTML"
        )
    except Exception:
        pass

# =====================================
#  ФАЗА 3: ОТЧЁТ С ПАГИНАЦИЕЙ
# =====================================

RESET_REPORT_PER_PAGE = 15
RESET_REPORT_MAX_BTN_PER_ROW = 5


def _fmt_reset_user(user_id: int) -> str:
    """@username / full_name / ID:..."""
    data = get_user(user_id)
    if not data:
        return f"ID:{user_id}"
    uname = data[1]
    fname = data[2]
    if uname:
        return f"@{uname}"
    if fname:
        return fname
    return f"ID:{user_id}"


def _build_reset_report_page(page: int) -> tuple:
    """
    Собирает страницу отчёта.
    Возвращает (text, kb) или (None, None), если данных нет.
    """
    global _reset_report_data

    if not _reset_report_data:
        return None, None

    # Сортировка по убыванию снятого
    sorted_data = sorted(
        _reset_report_data,
        key=lambda x: x["removed"],
        reverse=True
    )

    total = len(sorted_data)
    total_pages = max(1, (total + RESET_REPORT_PER_PAGE - 1) // RESET_REPORT_PER_PAGE)

    if page < 0:
        page = 0
    if page >= total_pages:
        page = total_pages - 1

    start = page * RESET_REPORT_PER_PAGE
    end = start + RESET_REPORT_PER_PAGE
    page_items = sorted_data[start:end]

    # ─── Текст ───
    lines = [
        f"📊 <b>Отчёт по сбросу msg</b>",
        f"━━━━━━━━━━━━━━━",
        f"Страница {page + 1}/{total_pages}",
        f"Всего тронуто: <b>{total}</b>",
        "",
    ]

    for i, item in enumerate(page_items, start=start + 1):
        user_ids = item["user_ids"]
        is_couple = item["is_couple"]

        if is_couple:
            name1 = _fmt_reset_user(user_ids[0])
            name2 = _fmt_reset_user(user_ids[1])
            name = f"{name1} 💍 {name2}"
        else:
            name = _fmt_reset_user(user_ids[0])

        lines.append(
            f"{i} | {name} | остаток: <b>{item['new_balance']:,}</b> "
            f"| снято: <b>{item['removed']:,}</b>"
        )

    text = "\n".join(lines)

    # ─── Пагинация: по 5 кнопок в ряд ───
    nav_buttons = []
    for p in range(total_pages):
        if p == page:
            nav_buttons.append(InlineKeyboardButton(
                text=f"• {p + 1} •",
                callback_data="resetrep_noop"
            ))
        else:
            nav_buttons.append(InlineKeyboardButton(
                text=f"{p + 1}",
                callback_data=f"resetrep_page_{p}"
            ))

    kb_rows = []
    for i in range(0, len(nav_buttons), RESET_REPORT_MAX_BTN_PER_ROW):
        kb_rows.append(nav_buttons[i:i + RESET_REPORT_MAX_BTN_PER_ROW])

    kb = InlineKeyboardMarkup(inline_keyboard=kb_rows)
    return text, kb


async def _send_reset_report(chat_id: int, owner_id: int):
    """Отправляет первую страницу отчёта."""
    text, kb = _build_reset_report_page(0)
    if text is None:
        return

    try:
        await bot.send_message(
            chat_id,
            text,
            parse_mode="HTML",
            reply_markup=kb
        )
    except Exception as e:
        print(f"[RESETMSG] Ошибка отправки отчёта: {e}")


@dp.callback_query(F.data == "resetrep_noop")
async def cb_resetrep_noop(callback: CallbackQuery):
    await callback.answer()


@dp.callback_query(F.data.startswith("resetrep_page_"))
async def cb_resetrep_page(callback: CallbackQuery):
    # Только владелец
    if callback.from_user.id not in OWNER_IDS:
        await callback.answer("⛔ Нет прав", show_alert=True)
        return

    try:
        page = int(callback.data.replace("resetrep_page_", ""))
    except ValueError:
        await callback.answer("⚠️ Ошибка данных", show_alert=True)
        return

    text, kb = _build_reset_report_page(page)
    if text is None:
        await callback.answer("⚠️ Отчёт устарел", show_alert=True)
        return

    try:
        await callback.message.edit_text(
            text,
            parse_mode="HTML",
            reply_markup=kb
        )
    except Exception as e:
        print(f"[RESETMSG] Ошибка переключения страницы: {e}")
    await callback.answer()


def _find_target_by_arg(message: Message, arg: str = None):
    """
    Универсальный поиск цели.
    Возвращает (target_id, target_name) или (None, None).
    Поддерживает: reply, @username, custom_id.
    """
    if message.reply_to_message:
        target = message.reply_to_message.from_user
        if target.is_bot:
            return None, None
        ensure_user(target)
        return target.id, target.full_name
    
    if arg:
        conn = sqlite3.connect("users.db")
        cur = conn.cursor()
        
        if arg.isdigit():
            cur.execute("SELECT user_id, full_name FROM users WHERE custom_id = ?", (int(arg),))
        else:
            uname = arg.lstrip("@")
            cur.execute("SELECT user_id, full_name FROM users WHERE LOWER(username) = LOWER(?)", (uname,))
            
        row = cur.fetchone()
        conn.close()
        
        if row:
            return row[0], row[1]
    
    return None, None

# =====================================
#  МОДЕРАЦИЯ: /warn, /unwarn, /warnlist
# =====================================
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
    
    args = first_line.split()[1:]
    arg = args[0] if args else None

    target_id, target_name = _find_target_by_arg(message, arg)

    if target_id is None:
        await message.answer(
            "❌ Использование:\n"
            "└─ ответь на сообщение: /warn\n"
            "└─ или /warn @username\n"
            "└─ или /warn [ID]\n"
            "На новой строке — причина",
            parse_mode="HTML"
        )
        return

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
        await message.answer(f"⚠️ <b>{target_name} уже забанен</b>\n└─ Сначала /unban", parse_mode="HTML")
        return

    current_count = get_warn_count(target_id)
    if current_count >= WARN_LIMIT:
        await message.answer(f"⚠️ <b>{target_name} уже имеет {WARN_LIMIT} warn</b>\n└─ Проверь /warnlist", parse_mode="HTML")
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

    await log_to_channel(
        f"⚠️ <b>Варн</b>\n"
        f"└─ Кому: {target_name} (<code>{target_id}</code>)\n"
        f"└─ Кем: {message.from_user.full_name} (<code>{actor_id}</code>)\n"
        f"└─ Причина: {reason}\n"
        f"└─ Всего: {new_count}/{WARN_LIMIT}"
    )

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

        await log_to_channel(
            f"🚫 <b>Авто-бан</b>\n"
            f"└─ Кому: {target_name} (<code>{target_id}</code>)\n"
            f"└─ Причина: {WARN_LIMIT} варнов\n"
            f"└─ Срок: {WARN_BAN_DAYS} дней"
        )


@dp.message(Command("unwarn"))
async def cmd_unwarn(message: Message):
    log_cmd("✅ /unwarn", message)
    actor_id = message.from_user.id

    if not is_moder(actor_id) and not is_senior(actor_id):
        await message.answer("⛔ Только для модераторов")
        return

    args = message.text.split()[1:]
    warn_num = None

    if message.reply_to_message:
        target_id, target_name = _find_target_by_arg(message)
        if args:
            try:
                warn_num = int(args[0])
            except ValueError:
                await message.answer(f"😅 «{args[0]}» — это не число\n└─ Пример: /unwarn 1", parse_mode="HTML")
                return
    else:
        if len(args) < 2:
            await message.answer(
                "❌ Использование:\n"
                "└─ ответь на сообщение: /unwarn [номер]\n"
                "└─ или /unwarn @username [номер]\n"
                "└─ или /unwarn [ID] [номер]\n\n"
                "Номер warn можно узнать в /warnlist",
                parse_mode="HTML"
            )
            return

        target_id, target_name = _find_target_by_arg(message, args[0])
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
            c_id = data[6] if len(data) > 6 else user_id
            name = f"@{uname}" if uname else (fname or f"ID:{user_id}")
            name = f"{name} (ID: {c_id})"

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


# ===================================
#  АДМИН-КОМАНДЫ (короткие)
# ===================================

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
    
    if message.reply_to_message or (args and args[0]):
        arg = args[0] if args else None
        to_id, to_name = _find_target_by_arg(message, arg)
        if to_id is None and (message.reply_to_message or args):
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
        await message.answer("❌ Формат:\n/anonmute @username 7\nпричина\n\n0 = навсегда\n(можно ID вместо @username)", parse_mode="HTML")
        return

    target_arg = None
    days_str = None
    
    # Если первое слово — число, но БД находит его как ID, то это ID
    if parts[0].startswith("@"):
        target_arg = parts[0]
        if len(parts) < 2:
            await message.answer("❌ Укажи срок (дней), 0 = навсегда")
            return
        days_str = parts[1]
    elif parts[0].isdigit() and len(parts) >= 2:
        target_arg = parts[0]
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

    target_id, target_name = _find_target_by_arg(message, target_arg)
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
    
    target_id, target_name = _find_target_by_arg(message, target_arg)
    if target_id is None:
        await message.answer("❌ Укажи @username, ID или ответь на сообщение")
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

    if len(changelog) > 1000:
        await message.answer("❌ Changelog слишком длинный (макс. 100)")
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
        await asyncio.sleep(0.05)

    await status_msg.edit_text(
        f"✅ <b>Рассылка завершена!</b>\n\n"
        f"└─ 📤 Отправлено: <b>{sent}</b>\n"
        f"└─ ❌ Ошибок: <b>{failed}</b>\n"
        f"└─ 👥 Всего: {len(user_ids)}",
        parse_mode="HTML"
    )


# =====================================
#  БАНЫ
# =====================================
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
            "Или ответь на сообщение:\n/ban 7\nпричина\n\n0 = навсегда\n(можно ID вместо @username)",
            parse_mode="HTML"
        )
        return

    target_arg = None
    days_str = None
    if parts[0].startswith("@") or (parts[0].isdigit() and len(parts) >= 2):
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

    target_id, target_name = _find_target_by_arg(message, target_arg)
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

    await log_to_channel(
        f"🚫 <b>Бан</b>\n"
        f"└─ Кому: {target_name} (<code>{target_id}</code>)\n"
        f"└─ Кем: {message.from_user.full_name} (<code>{actor_id}</code>)\n"
        f"└─ Причина: {reason}\n"
        f"└─ Срок: {until_text}"
    )


@dp.message(Command("unban"))
async def cmd_unban(message: Message):
    log_cmd("✅ /unban", message)
    actor_id = message.from_user.id
    if not is_senior(actor_id):
        await message.answer("⛔ Только для старших модераторов")
        return

    args = message.text.split()[1:]
    target_arg = args[0] if args else None
    
    target_id, target_name = _find_target_by_arg(message, target_arg)
    if target_id is None:
        await message.answer("❌ Укажи @username, ID или ответь на сообщение")
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
        # Достаем custom_id для отображения
        u_data = get_user(user_id)
        c_id = u_data[6] if (u_data and len(u_data) > 6) else user_id
        
        name = f"@{uname}" if uname else (fname or f"ID: {c_id}")
        lines.append(f"• {name} (ID: {c_id}) — {reason} | {status}")

    if active_count == 0:
        await message.answer("📭 Активных банов нет")
        return

    await message.answer("\n".join(lines), parse_mode="HTML")


# ====================================
#  /accdel — полное удаление аккаунта
# ====================================

@dp.message(Command("accdel"))
async def cmd_accdel(message: Message):
    log_cmd("🗑️ /accdel", message)
    actor_id = message.from_user.id

    if not is_moder(actor_id) and not is_senior(actor_id):
        await message.answer("⛔ Только для модераторов")
        return

    lines = message.text.split("\n", 1)
    first_line = lines[0].strip()
    reason = lines[1].strip() if len(lines) > 1 else "не указана"
    args = first_line.split()[1:]
    target_arg = args[0] if args else None

    target_id, target_name = _find_target_by_arg(message, target_arg)
    if target_id is None:
        await message.answer(
            "❌ Использование:\n"
            "<code>/accdel @username\n"
            "Причина</code>\n\n"
            "Или ответь на сообщение:\n"
            "<code>/accdel\n"
            "Причина</code>\n\n"
            "Или по ID:\n"
            "<code>/accdel [ID]\n"
            "Причина</code>",
            parse_mode="HTML"
        )
        return

    if target_id == actor_id:
        await message.answer("❌ Нельзя удалить свой аккаунт")
        return

    if target_id in OWNER_IDS:
        await message.answer("❌ Нельзя удалить владельца")
        return

    if has_access(target_id, "owner"):
        await message.answer("❌ Нельзя удалить владельца")
        return

    if not is_owner(actor_id):
        can, err = can_touch(actor_id, target_id)
        if not can:
            await message.answer(err)
            return

    target_data = get_user(target_id)
    if not target_data:
        await message.answer(f"❌ {target_name} не найден в БД")
        return

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Удалить",
                callback_data=f"accdel_yes_{actor_id}_{target_id}",
                icon_custom_emoji_id=PREM_DELETE
            ),
            InlineKeyboardButton(
                text="Отмена",
                callback_data=f"accdel_no_{actor_id}_{target_id}"
            ),
        ]
    ])

    await message.answer(
        f"{_p(PREM_DELETE, '🗑️')} <b>Подтверди удаление аккаунта</b>\n\n"
        f"└─ Цель: <b>{target_name}</b> (<code>{target_id}</code>)\n"
        f"└─ Причина: <b>{reason}</b>\n\n"
        f"⚠️ <b>Будут удалены ВСЕ данные:</b>\n"
        f"└─ Профиль, баланс, банк\n"
        f"└─ Достижения, статистика, платежи\n"
        f"└─ Браки (партнёр получит половину)\n"
        f"└─ Дуэли и игры (соперники получат возврат)\n"
        f"└─ Транзакции, анонимки, варны\n\n"
        f"<b>Действие необратимо!</b>",
        parse_mode="HTML",
        reply_markup=kb
    )


@dp.callback_query(F.data.startswith("accdel_yes_") | F.data.startswith("accdel_no_"))
async def cb_accdel(callback: CallbackQuery):
    data = callback.data
    actor_id = callback.from_user.id

    if data.startswith("accdel_no_"):
        parts = data.split("_")
        try:
            owner_id = int(parts[2])
            target_id = int(parts[3])
        except (ValueError, IndexError):
            await callback.answer("⚠️ Ошибка данных", show_alert=True)
            return

        if callback.from_user.id != owner_id:
            await callback.answer("❌ Это не для тебя", show_alert=True)
            return

        try:
            await callback.message.edit_text(
                f"❌ <b>Отменено</b>\n└─ Аккаунт {target_id} не удалён",
                parse_mode="HTML"
            )
        except Exception:
            pass
        await callback.answer("❌ Отменено")
        return

    if data.startswith("accdel_yes_"):
        parts = data.split("_")
        try:
            owner_id = int(parts[2])
            target_id = int(parts[3])
        except (ValueError, IndexError):
            await callback.answer("⚠️ Ошибка данных", show_alert=True)
            return

        if callback.from_user.id != owner_id:
            await callback.answer("❌ Это не для тебя", show_alert=True)
            return

        if not is_moder(actor_id) and not is_senior(actor_id):
            await callback.answer("⛔ Нет прав", show_alert=True)
            return

        if target_id in OWNER_IDS or has_access(target_id, "owner"):
            await callback.answer("❌ Нельзя удалить владельца", show_alert=True)
            return

        if not is_owner(actor_id):
            can, err = can_touch(actor_id, target_id)
            if not can:
                await callback.answer(err, show_alert=True)
                return

        target_data = get_user(target_id)
        target_name = target_data[2] if target_data else f"ID:{target_id}"

        try:
            await bot.send_message(
                target_id,
                f"{_p(PREM_DELETE, '🗑️')} <b>Твой аккаунт удалён</b>\n\n"
                f"└─ Причина: <b>уточняется у модерации</b>",
                parse_mode="HTML"
            )
        except Exception:
            pass

        ok = delete_account(target_id)

        if ok:
            try:
                await callback.message.edit_text(
                    f"{_p(PREM_CHECK, '✅')} <b>Аккаунт удалён</b>\n\n"
                    f"└─ Пользователь: <b>{target_name}</b> (<code>{target_id}</code>)\n"
                    f"└─ Все связанные данные удалены",
                    parse_mode="HTML"
                )
            except Exception:
                pass
            await callback.answer("✅ Удалено")
        else:
            try:
                await callback.message.edit_text(
                    f"{_p(PREM_ERR, '❌')} <b>Ошибка удаления</b>\n"
                    f"└─ Проверь логи",
                    parse_mode="HTML"
                )
            except Exception:
                pass
            await callback.answer("❌ Ошибка", show_alert=True)
    await log_to_channel(
          f"🗑️ <b>Удаление аккаунта</b>\n"
          f"└─ Кому: {target_name} (<code>{target_id}</code>)\n"
          f"└─ Кем: {callback.from_user.full_name} (<code>{actor_id}</code>)"
    )


# =====================================
# /addmsg, /remmsg, /setmsg, /givevip, /remvip, /stats
# =====================================

@dp.message(Command("addmsg"))
async def cmd_addmsg(message: Message):
    log_cmd("💰 /addmsg", message)
    if not is_econom(message.from_user.id):
        await message.answer("⛔ Команда только для экономистов")
        return

    args = message.text.split()[1:]
    arg = args[0] if args else None
    amount_str = None

    if message.reply_to_message:
        if args:
            amount_str = args[0]
    else:
        if len(args) < 2:
            await message.answer("❌ Укажи @username/ID или ответь на сообщение, и сумму")
            return
        amount_str = args[1]

    try:
        amount = int(amount_str) if amount_str else None
    except ValueError:
        await message.answer("❌ Сумма должна быть числом")
        return

    target_id, target_name = _find_target_by_arg(message, arg)

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
    arg = args[0] if args else None
    amount_str = None

    if message.reply_to_message:
        if args:
            amount_str = args[0]
    else:
        if len(args) < 2:
            await message.answer("❌ Укажи @username/ID или ответь на сообщение, и сумму")
            return
        amount_str = args[1]

    try:
        amount = int(amount_str) if amount_str else None
    except ValueError:
        await message.answer("❌ Сумма должна быть числом")
        return

    target_id, target_name = _find_target_by_arg(message, arg)

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
    arg = args[0] if args else None
    amount_str = None

    if message.reply_to_message:
        if args:
            amount_str = args[0]
    else:
        if len(args) < 2:
            await message.answer("❌ Укажи @username/ID или ответь на сообщение, и сумму")
            return
        amount_str = args[1]

    try:
        amount = int(amount_str) if amount_str else None
    except ValueError:
        await message.answer("❌ Сумма должна быть числом")
        return

    target_id, target_name = _find_target_by_arg(message, arg)

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
    weeks_str = None
    arg = None

    if message.reply_to_message:
        if not args:
            await message.answer("❌ Формат (reply): /givevip [недели]")
            return
        weeks_str = args[0]
    else:
        if len(args) < 2:
            await message.answer(
                "❌ Использование:\n"
                "└─ ответь на сообщение: /givevip [недели]\n"
                "└─ или /givevip @username [недели]\n"
                "└─ или /givevip [ID] [недели]"
            )
            return
        arg = args[0]
        weeks_str = args[1]

    target_id, target_name = _find_target_by_arg(message, arg)
    if target_id is None:
        await message.answer("❌ Пользователь не найден")
        return

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
    arg = args[0] if args else None

    target_id, target_name = _find_target_by_arg(message, arg)
    if target_id is None:
        await message.answer("❌ Укажи @username/ID или ответь на сообщение")
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


# =====================================
#  ДОСТУПЫ
# =====================================

CATEGORIES = {
    "econom": {
        "title": "💰 <b>Экономика</b>",
        "required": "econom",
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
        "required": "moder",
        "text": (
            "<b>Варны:</b>\n"
            "└─ /warn [@user] + причина\n"
            "└─ /unwarn [@user] [номер]\n"
            "└─ /warnlist\n\n"
            "<b>Анонимки:</b>\n"
            "└─ /anonlog [@user]\n"
            "└─ /anonmute [@user] [дней] + причина\n"
            "└─ /anonunmute [@user]"
        ),
    },
    "senior": {
        "title": "🚫 <b>Старший модератор</b>",
        "required": "senior",
        "text": (
            "<b>Баны:</b>\n"
            "└─ /ban [@user] [дней] + причина\n"
            "└─ /unban [@user]\n"
            "└─ /banlist\n\n"
            "<b>Удаление:</b>\n"
            "└─ /accdel [@user] + причина"
        ),
    },
    "owner": {
        "title": "👑 <b>Владелец</b>",
        "required": "owner",
        "text": (
            "<b>Доступы:</b>\n"
            "└─ /setaccess [@user] [уровни]\n"
            "└─ /accesslist\n\n"
            "<b>Бот:</b>\n"
            "└─ /setver [версия] + changelog\n"
            "└─ /broadcast — рассылка (через /setver)"
        ),
    },
}

def _has_category_access(user_id: int, category_key: str) -> bool:
    """Проверяет, есть ли у юзера доступ к категории."""
    if is_main_owner(user_id):
        return True

    cat = CATEGORIES.get(category_key)
    if not cat:
        return False

    required = cat.get("required")

    if required == "econom":
        return is_econom(user_id)
    if required == "moder":
        return is_moder(user_id) or is_senior(user_id) or is_owner(user_id)
    if required == "senior":
        return is_senior(user_id) or is_owner(user_id)
    if required == "owner":
        return is_owner(user_id)

    return False

def kb_main(role: str = None) -> InlineKeyboardMarkup:
    """Клавиатура /own — 4 категории."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="💰 Эконом",  callback_data="own:cat:econom"),
            InlineKeyboardButton(text="⚠️ Модер",   callback_data="own:cat:moder"),
        ],
        [
            InlineKeyboardButton(text="🚫 Сеньор",  callback_data="own:cat:senior"),
            InlineKeyboardButton(text="👑 Владелец", callback_data="own:cat:owner"),
        ],
    ])


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

# =====================================
#  ДЕВ-ИНСТРУМЕНТ: получение custom_emoji_id
# ===================================
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
    user_id = message.from_user.id

    # Проверяем, есть ли хоть какой-то доступ
    has_any = (
        is_main_owner(user_id)
        or is_owner(user_id)
        or is_senior(user_id)
        or is_moder(user_id)
        or is_econom(user_id)
    )

    if not has_any:
        await message.answer("⛔ У тебя нет прав")
        return

    await message.answer(
        "👑 <b>Панель управления</b>\n\n"
        "Выбери категорию:",
        parse_mode="HTML",
        reply_markup=kb_main(),
    )


@dp.callback_query(F.data == "own:back")
async def cb_own_back(call: CallbackQuery):
    user_id = call.from_user.id

    has_any = (
        is_main_owner(user_id)
        or is_owner(user_id)
        or is_senior(user_id)
        or is_moder(user_id)
        or is_econom(user_id)
    )

    if not has_any:
        await call.answer("⛔ Нет прав", show_alert=True)
        return

    await call.message.edit_text(
        "👑 <b>Панель управления</b>\n\n"
        "Выбери категорию:",
        parse_mode="HTML",
        reply_markup=kb_main(),
    )
    await call.answer()


@dp.callback_query(F.data.startswith("own:cat:"))
async def cb_own_cat(call: CallbackQuery):
    user_id = call.from_user.id

    key = call.data.split(":", 2)[2]

    if key not in CATEGORIES:
        await call.answer("⚠️ Категория не найдена", show_alert=True)
        return

    # ✅ ПРОВЕРКА ДОСТУПА
    if not _has_category_access(user_id, key):
        await call.answer("⛔ Нет доступа", show_alert=True)
        return

    cat = CATEGORIES[key]

    await call.message.edit_text(
        f"{cat['title']}\n\n{cat['text']}",
        parse_mode="HTML",
        reply_markup=kb_back(),
    )
    await call.answer()

@dp.message(Command("users"))
async def cmd_users(message: Message):
    log_cmd("👥 /users", message)
    
    # Проверка прав (только главный владелец)
    if message.from_user.id not in OWNER_IDS:
        await message.answer("⛔ Только для главного владельца")
        return

    # Получаем список всех ID
    user_ids = get_all_user_ids()
    total = len(user_ids)
    
    if total == 0:
        await message.answer("📭 В базе нет пользователей")
        return

    msg = await message.answer(f"⏳ Собираем данные о {total} юзерах...")

    lines = []
    # Заголовок файла
    lines.append(f"СПИСОК ПОЛЬЗОВАТЕЛЕЙ БОТА (Всего: {total})")
    lines.append("="*40)
    lines.append("{Номер} | ID / @username | Имя")
    lines.append("="*40)

    # Проходимся по базе
    for i, uid in enumerate(user_ids, start=1):
        data = get_user(uid)
        if not data:
            continue
            
        uname = data[1]
        fname = data[2]
        
        # Форматируем юзернейм и имя
        username_str = f"@{uname}" if uname else "нет"
        name_str = fname if fname else "Без имени"
        
        # Если имя содержит переносы строк, убираем их
        name_str = name_str.replace("\n", " ").replace("\r", " ")
        
        lines.append(f"{i} | {uid} / {username_str} | {name_str}")

    # Склеиваем всё в один текст
    file_content = "\n".join(lines)

    # Создаем временный файл
    filename = f"users_export_{datetime.now().strftime('%d_%m_%Y')}.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(file_content)

    # Отправляем файл
    try:
        doc = FSInputFile(filename)
        await message.answer_document(
            document=doc,
            caption=f"👥 <b>Выгрузка пользователей</b>\n└─ Всего: {total}\n└─ Формат: Номер | ID / @username | Имя",
            parse_mode="HTML"
        )
        # Удаляем сообщение "Собираем..."
        await msg.delete()
    except Exception as e:
        await message.answer(f"❌ Ошибка отправки файла: {e}")
    finally:
        # Удаляем временный файл с сервера
        if os.path.exists(filename):
            os.remove(filename)


@dp.message(Command("setaccess"))
async def cmd_setaccess(message: Message):
    log_cmd("🔑 /setaccess", message)
    actor_id = message.from_user.id

    if not is_owner(actor_id) and not is_senior(actor_id):
        await message.answer("⛔ Только для владельца или старшего модератора")
        return

    args = message.text.split()[1:]
    level_args = []
    target_arg = None

    if message.reply_to_message:
        target_id, target_name = _find_target_by_arg(message)
        level_args = args
    else:
        if len(args) < 2:
            await message.answer(
                "❌ Использование:\n"
                "└─ ответь на сообщение: /setaccess [уровни]\n"
                "└─ или /setaccess @username [уровни]\n"
                "└─ или /setaccess [ID] [уровни]\n\n"
                "Уровни: econom, moder, senior, none",
                parse_mode="HTML"
            )
            return

        target_arg = args[0]
        target_id, target_name = _find_target_by_arg(message, target_arg)
        if target_id is None:
            await message.answer("❌ Пользователь не найден")
            return
        level_args = args[1:]

    if target_id is None:
        await message.answer("❌ Пользователь не найден")
        return

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
        c_id = data[6] if len(data) > 6 else uid
        
        name = f"@{uname}" if uname else (fname or f"ID:{uid}")
        return f"{name} (ID: {c_id})"

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

# =====================================
#  /status — статус бота 
#  (только владелец)
# =====================================

BOT_START_TIME = time.time()


@dp.message(Command("status"))
async def cmd_status(message: Message):
    log_cmd("⚙️ /status", message)
    user_id = message.from_user.id

    if not is_main_owner(user_id) and not is_owner(user_id):
        await message.answer("⛔ Только для владельца")
        return

    # ─── Аптайм ───
    uptime = int(time.time() - BOT_START_TIME)
    days = uptime // 86400
    hours = (uptime % 86400) // 3600
    minutes = (uptime % 3600) // 60

    uptime_text = ""
    if days > 0:
        uptime_text += f"{days} дн. "
    if hours > 0:
        uptime_text += f"{hours} ч "
    uptime_text += f"{minutes} мин"

    # ─── Пинг до Telegram ───
    try:
        ping_start = time.monotonic()
        await bot.get_me()
        ping_ms = int((time.monotonic() - ping_start) * 1000)
        ping_text = f"{ping_ms} мс"
    except Exception as e:
        ping_text = f"❌ ошибка: {e}"

    # ─── Размер БД ───
    try:
        db_size = os.path.getsize("users.db")
        db_size_mb = db_size / (1024 * 1024)
        db_text = f"{db_size_mb:.2f} МБ"
    except Exception:
        db_text = "?"

    # ─── RAM (без psutil) ───
    try:
        import resource
        ram_kb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        ram_mb = ram_kb / 1024
        ram_text = f"{ram_mb:.1f} МБ"
    except Exception:
        ram_text = "недоступно"

    # ─── Кол-во юзеров ───
    try:
        stats = get_bot_stats()
        users_total = stats["total_users"]
        vip_count = stats["vip_users"]
        banned_count = stats["banned_users"]
    except Exception:
        users_total = vip_count = banned_count = "?"

    # ─── Онлайн за 5 мин ───
    try:
        conn = sqlite3.connect("users.db")
        cur = conn.cursor()
        threshold = (datetime.now() - timedelta(minutes=5)).isoformat()
        cur.execute("SELECT COUNT(*) FROM users WHERE last_activity > ?", (threshold,))
        online_5m = cur.fetchone()[0]
        conn.close()
    except Exception:
        online_5m = "?"

    # ─── Последний бэкап ───
    last_backup_text = "не найден"
    try:
        backups = [f for f in os.listdir(".") if f.startswith("users_backup_")]
        if backups:
            latest = max(backups, key=lambda f: os.path.getmtime(f))
            mtime = os.path.getmtime(latest)
            age_sec = int(time.time() - mtime)
            age_min = age_sec // 60
            last_backup_text = f"{latest} ({age_min} мин назад)"
    except Exception:
        pass

    text = (
        f"⚙️ <b>Статус бота</b>\n\n"
        f"⏱️ <b>Аптайм:</b> {uptime_text}\n"
        f"📡 <b>Пинг:</b> {ping_text}\n"
        f"💾 <b>RAM:</b> {ram_text}\n"
        f"📁 <b>БД:</b> {db_text}\n\n"
        f"👥 <b>Юзеры:</b>\n"
        f"└─ Всего: <b>{users_total}</b>\n"
        f"└─ С VIP: <b>{vip_count}</b>\n"
        f"└─ Забанено: <b>{banned_count}</b>\n"
        f"└─ Онлайн (5м): <b>{online_5m}</b>\n\n"
        f"💾 <b>Последний бэкап:</b>\n"
        f"└─ {last_backup_text}"
    )

    await message.answer(
        text, parse_mode="HTML",
        reply_to_message_id=message.message_id
    )



# ===================================
#  /channel — ссылка на канал
# ===================================
@dp.message(Command("channel"))
async def cmd_channel(message: Message):
    log_cmd("📢 /channel", message)

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="📢 Канал с новостями",
            url="https://t.me/Amina_updates"
        )],
        [InlineKeyboardButton(
            text="💬 Наша группа",
            url="https://t.me/chat_games_Gojo"
        )]
    ])

    await message.answer(
        "🔗 <b>Полезные ссылки</b>\n\n"
        "└─ 📢 Канал с обновлениями и анонсами\n"
        "└─ 💬 Группа для общения",
        parse_mode="HTML",
        reply_markup=kb,
        reply_to_message_id=message.message_id
    )


# =====================================
#  CATCH-ALL
# =====================================
@dp.message()
async def catch_all_messages(message: Message):
    # 1. Проверка на команды (если хендлер забыт, пишем в лог)
    if message.text and message.text.startswith("/"):
        print(f"[CATCH-ALL] Пропущена команда без хендлера: {message.text!r}")
        if message.from_user and not message.from_user.is_bot:
            await _daily_reminder(message.from_user.id, message.chat.id)
            try:
                await _pet_check_deaths(message.from_user.id)
            except Exception as e:
                print(f"[PET] Ошибка проверки: {e}")
        return

    if not message.from_user or message.from_user.is_bot:
        return

    user = message.from_user
    # Сохраняем ID чата для напоминаний
    _last_chat_ids[user.id] = message.chat.id
    
    # 2. Создаём/обновляем юзера
    try:
        ensure_user(user)
    except Exception as e:
        print(f"[CATCH-ALL] ❌ ensure_user: {e}")
        return

    # 3. Проверка питомцев
    try:
        await _pet_check_deaths(user.id)
    except Exception as e:
        print(f"[PET] Ошибка: {e}")

    # =================================
    # 4. ЛОГИКА ИИ (обращение "Амина" / "Amina")
    # =================================
    if message.text:
        text_lower = message.text.strip().lower()
        if text_lower.startswith(("amina")):
            parts = message.text.split(maxsplit=1)
            if len(parts) < 2 or not parts[1].strip():
                await message.answer("Я здесь! Напиши, что нужно сделать.")
            else:
                await _handle_ai_request(message, parts[1].strip())
            # После ИИ-запроса НЕ начисляем msg и не идём дальше
            return

    # =================================
    # 5. ОБЫЧНОЕ НАЧИСЛЕНИЕ МОНЕТ ЗА СООБЩЕНИЕ
    # =================================
    try:
        vip = is_vip_active(user.id)
    except Exception:
        vip = False

    cooldown = VIP_COOLDOWN if vip else NORMAL_COOLDOWN
    now_mono = time.monotonic()
    last = _last_reward.get(user.id, 0)

    if now_mono - last >= cooldown:
        try:
            add_msg_auto(user.id, 1)
            increment_stat(user.id, "total_messages", 1)
            _last_reward[user.id] = now_mono
        except Exception as e:
            print(f"[CATCH-ALL] ❌ add_msg_auto: {e}")
            return

    # ================================
    # 6. РЕФЕРАЛЬНАЯ СИСТЕМА
    # ================================
    try:
        referrer_id = get_referrer(user.id)
        if referrer_id:
            ref_info = get_referral(user.id)
            if ref_info:
                ref_referrer, ref_msg_count, ref_rewarded = ref_info
                if ref_rewarded == 0:
                    new_count = increment_referral_msg(user.id)
                    if new_count >= REFERRAL_THRESHOLD:
                        rewards_today = count_rewards_24h(referrer_id)
                        if rewards_today >= REFERRAL_MAX_PER_DAY:
                            mark_referral_rewarded(user.id, reward=False)
                            try:
                                await bot.send_message(
                                    referrer_id,
                                    f"💤 <b>Реферал сгорел</b>\n\n"
                                    f"└─ Лимит <b>{REFERRAL_MAX_PER_DAY}</b> награды за 24ч\n"
                                    f"└─ <b>{user.full_name}</b> не засчитан",
                                    parse_mode="HTML"
                                )
                            except Exception:
                                pass
                        else:
                            mark_referral_rewarded(user.id, reward=True)
                            add_balance(referrer_id, REFERRER_REWARD)
                            log_transaction(referrer_id, user.id, REFERRER_REWARD, "referral_reward")
                            try:
                                await bot.send_message(
                                    referrer_id,
                                    f"🎉 <b>Реферальная награда!</b>\n\n"
                                    f"└─ <b>{user.full_name}</b> набрал {REFERRAL_THRESHOLD} сообщений\n"
                                    f"└─ {_p(PREM_MONEY, '💰')} Начислено: <b>+{REFERRER_REWARD}</b> msg",
                                    parse_mode="HTML"
                                )
                            except Exception:
                                pass
    except Exception as e:
        print(f"[CATCH-ALL] ❌ referral check: {e}")

    # 7. Ежедневные напоминания и достижения
    await _daily_reminder(user.id, message.chat.id)
    await _check_and_notify_achievements(user.id, message.chat.id)



def _cleanup_old_backups():
    """Удаляет локальные бэкапы старше 24 часов."""
    try:
        now = time.time()
        removed = 0

        for filename in os.listdir("."):
            if not filename.startswith("users_backup_") or not filename.endswith(".db"):
                continue

            filepath = os.path.join(".", filename)
            try:
                # Если файл старше 24ч (86400 сек)
                if now - os.path.getmtime(filepath) > 86400:
                    os.remove(filepath)
                    removed += 1
            except Exception as e:
                print(f"[BACKUP] Ошибка удаления {filename}: {e}")

        if removed > 0:
            print(f"[BACKUP] 🗑️ Удалено старых бэкапов: {removed}")
    except Exception as e:
        print(f"[BACKUP] Ошибка очистки: {e}")

# =====================================
# бэкап базы данных
# =====================================
async def _db_backup_loop():
    """
    Отправляет резервную копию users.db владельцу раз в 2 часа.
    Безопасно копирует базу, чтобы не повредить её во время записи.
    """
    import sqlite3
    
    last_backup_time = 0
    BACKUP_INTERVAL = 2 * 60 * 60  # 2 часа в секундах

    while True:
        try:
            now = time.time()
            
            # Проверяем, прошло ли 2 часа
            if now - last_backup_time >= BACKUP_INTERVAL:
                if not os.path.exists(BACKUP_DB_PATH):
                    print(f"[BACKUP] ❌ Файл {BACKUP_DB_PATH} не найден")
                    await asyncio.sleep(60)
                    continue

                # Формируем имя файла с текущей датой и временем
                time_str = datetime.now().strftime("%d.%m_%H-%M")
                backup_filename = f"users_backup_{time_str}.db"

                try:
                    # Безопасное копирование базы (чтобы не сломать, пока бот пишет)
                    src = sqlite3.connect(BACKUP_DB_PATH)
                    dst = sqlite3.connect(backup_filename)
                    src.backup(dst)
                    dst.close()
                    src.close()

                    # Отправляем файл в ЛС
                    doc = FSInputFile(backup_filename)
                    await bot.send_document(
                        chat_id=BACKUP_OWNER_ID,
                        document=doc,
                        caption=f"📦 <b>Бэкап базы данных</b>\n└─ Время: {datetime.now().strftime('%d.%m.%Y %H:%M')}",
                        parse_mode="HTML"
                    )

                    print(f"[BACKUP] ✅ Бэкап успешно отправлен: {backup_filename}")
                    
                    # Удаляем локальный файл после отправки (чтобы не забивать диск)
                    if os.path.exists(backup_filename):
                        os.remove(backup_filename)

                    # Обновляем время последнего бэкапа
                    last_backup_time = now

                except Exception as e:
                    print(f"[BACKUP] ❌ Ошибка при создании/отправке: {e}")

        except Exception as e:
            print(f"[BACKUP] ❌ Ошибка цикла: {e}")

        # Проверяем каждую минуту, не пора ли делать бэкап
        await asyncio.sleep(60)
# =====================================



# =====================================
#  ЗАПУСК
# =====================================

async def main():
    init_db()
    treasury_ensure()
    print("Бот запущен...")
    print("Ждём сообщения...\n")
    
    asyncio.create_task(_duel_watchdog())
    asyncio.create_task(_db_backup_loop())
    print("[STARTUP] Авто-бэкап запущен")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())