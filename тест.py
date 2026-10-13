from aiogram import Bot, Dispatcher
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.dispatcher.middlewares.base import BaseMiddleware
from typing import Any, Awaitable, Callable, Dict
import os
import asyncio
from datetime import datetime, timedelta, timezone
from aiogram.types import FSInputFile
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

TOKEN = "8397692001:AAHQCqKjPVoxQj5p7LARGfTR62lQ0Yhcw1s"
BOT_USERNAME = "Aminka_Ai_bot"
OWNER_IDS = {7564741700}
# =====================================
#  АВТО-БЭКАП БАЗЫ ДАННЫХ
# =====================================

BACKUP_OWNER_ID = 7564741700       # кому отправлять бэкапы
BACKUP_DB_PATH = "users.db"        # путь к БД
BACKUP_CHECK_INTERVAL = 60         # раз в 60 секунд проверяем


# Игровые таймауты (нужны до watchdog'ов)
TTT_TIMEOUT = 300
TTT_TURN_TIMEOUT = 60
DUEL_TIMEOUT = 300
DUEL_TURN_TIMEOUT = 60
DUEL_MIN_BET = 1000
TTT_MIN_BET = 500

PREM_DELETE = "5429137527443310063"  # 🗑️ удаление
REFERRER_REWARD = 1000    # сколько получает приглашающий
REFERRAL_REWARD = 500     # сколько получает приглашённый
REFERRAL_THRESHOLD = 20   # сколько сообщений должен написать реферал
REFERRAL_VIP_DAYS = 1     # VIP приглашённому
REFERRAL_MAX_PER_DAY = 2  # максимум наград в 24ч
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


dp.message.middleware(BanMiddleware())
dp.message.middleware(ShadowMiddleware())
dp.callback_query.middleware(ShadowCallbackMiddleware())
print("[STARTUP] BanMiddleware + ShadowMiddleware подключены")


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

# =========================================================
#  /promo — активация промокода
# =========================================================

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


# =========================================================
#  /addpromo — создание промокода (владелец)
# =========================================================

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

# =========================================================
#  /rep — репутация
# =========================================================

REP_COOLDOWN = timedelta(hours=24)


@dp.message(Command("rep"))
async def cmd_rep(message: Message):
    log_cmd("⭐ /rep", message)
    user = message.from_user
    ensure_user(user)

    target_id = None
    target_name = None

    if message.reply_to_message and not message.reply_to_message.from_user.is_bot:
        target = message.reply_to_message.from_user
        target_id = target.id
        target_name = target.full_name
        ensure_user(target)
    else:
        args = message.text.split()[1:]
        if not args or not args[0].startswith("@"):
            await message.answer(
                "⭐ <b>Репутация</b>\n\n"
                "Использование:\n"
                "└─ Ответь на сообщение: <code>/rep</code>\n"
                "└─ Или: <code>/rep @username</code>\n\n"
                "💡 Раз в 24 часа можно дать +1 или -1 к репутации",
                parse_mode="HTML"
            )
            return
        target_id, target_name = find_user_id(message, args[0])
        if target_id is None:
            await message.answer("❌ Пользователь не найден")
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
                    f"⏳ <b>Репутацию можно давать раз в 24 часа</b>\n"
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


@dp.callback_query(F.data.startswith("rep_plus_") | F.data.startswith("rep_minus_"))
async def cb_rep(callback: CallbackQuery):
    parts = callback.data.split("_")
    if len(parts) != 4:
        await callback.answer("⚠️ Ошибка данных", show_alert=True)
        return

    action = parts[1]
    actor_id = int(parts[2])
    target_id = int(parts[3])

    if callback.from_user.id != actor_id:
        await callback.answer("❌ Это не для тебя", show_alert=True)
        return

    last = get_last_rep(actor_id)
    if last:
        try:
            last_dt = datetime.fromisoformat(last)
            if datetime.now() - last_dt < REP_COOLDOWN:
                await callback.answer("⏳ Ты уже голосовал сегодня", show_alert=True)
                return
        except ValueError:
            pass

    amount = 1 if action == "plus" else -1
    new_rep = change_reputation(target_id, amount)
    set_last_rep(actor_id)

    target_data = get_user(target_id)
    target_name = target_data[2] if target_data else f"ID:{target_id}"

    emoji = "👍" if amount > 0 else "👎"

    try:
        await callback.message.edit_text(
            f"{emoji} <b>Репутация изменена</b>\n\n"
            f"└─ Кому: <b>{target_name}</b>\n"
            f"└─ Изменение: <b>{amount:+d}</b>\n"
            f"└─ Новая: <b>{new_rep}</b>",
            parse_mode="HTML"
        )
    except Exception:
        pass

    await callback.answer(f"{emoji} {amount:+d}")

    try:
        await bot.send_message(
            target_id,
            f"{emoji} <b>{callback.from_user.full_name}</b> "
            f"{'повысил' if amount > 0 else 'понизил'} тебе репутацию\n"
            f"└─ Теперь: <b>{new_rep}</b>",
            parse_mode="HTML"
        )
    except Exception:
        pass

                
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

# ====================================
# КЕЙСЫ
# ====================================

CASES = {
    "case": {
        "name": "🎁 Обычный кейс",
        "price": 1000,
        "cooldown_normal": 10 * 60,
        "cooldown_vip": 5 * 60,
        "frame_delay": 0.55,
        "msg_range": (700, 1400),
        "tiers": [
            (700, 900, 57.0),
            (900, 1150, 28.5),
            (1150, 1400, 9.5),
        ],
        "vip_chance": 5.0,
        "vip_days": 3,
    },
    "rarecase": {
        "name": "💎 Редкий кейс",
        "price": 5000,
        "cooldown_normal": 30 * 60,
        "cooldown_vip": 15 * 60,
        "frame_delay": 0.55,
        "msg_range": (4000, 7000),
        "tiers": [
            (4000, 5000, 54.0),
            (5000, 6000, 27.0),
            (6000, 7000, 9.0),
        ],
        "vip_chance": 10.0,
        "vip_days": 7,
    },
    "lcase": {
        "name": "👑 Легендарный кейс",
        "price": 25000,
        "cooldown_normal": 60 * 60,
        "cooldown_vip": 30 * 60,
        "frame_delay": 0.6,
        "msg_range": (23000, 30000),
        "tiers": [
            (23000, 25000, 51.0),
            (25000, 27500, 25.5),
            (27500, 30000, 8.5),
        ],
        "vip_chance": 15.0,
        "vip_days": 30,
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

# =========================================================
#  /cases — магазин кейсов с пагинацией
# =========================================================

CASES_PER_PAGE = 3
CASES_ORDER = ["case", "rarecase", "lcase"]


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
    ready, cooldown_text = _get_case_cooldown_info(user_id, case_key)

    emoji = case_data["name"].split()[0]
    name = " ".join(case_data["name"].split()[1:])

    msg_min, msg_max = case_data["msg_range"]

    # ─── Категории выигрыша ───
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

    # ─── Кнопка кручения ───
    btn_text = f"{emoji} Крутить ({case_data['price']:,})"
    kb_rows = [[InlineKeyboardButton(
        text=btn_text,
        callback_data=f"case_buy_{user_id}_{case_key}"
    )]]

    # ─── Навигация ───
    nav_row = []
    for p in range(len(CASES_ORDER)):
        if p == page:
            nav_row.append(InlineKeyboardButton(
                text=f"• {p + 1} •",
                callback_data="cases_noop"
            ))
        else:
            nav_row.append(InlineKeyboardButton(
                text=f"{p + 1}",
                callback_data=f"cases_page_{user_id}_{p}"
            ))
    kb_rows.append(nav_row)

    kb = InlineKeyboardMarkup(inline_keyboard=kb_rows)
    return text, kb

# =========================================================
#  /photo — получить file_id
# =========================================================

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

    # ─── Проверка кулдауна ───
    ready, cooldown_text = _get_case_cooldown_info(owner_id, case_key)
    if not ready:
        await callback.answer(
            f"⏳ Кейс на перезарядке: {cooldown_text.replace('⏱️ ', '')}",
            show_alert=True
        )
        return

    # ─── Проверка баланса ───
    balance = get_balance(owner_id)
    if balance < price:
        await callback.answer(
            f"😢 Недостаточно msg! Нужно: {price:,}, у тебя: {balance:,}",
            show_alert=True
        )
        return

    # ─── Списываем и открываем ───
    add_balance(owner_id, -price)
    log_transaction(owner_id, owner_id, -price, "case")
    set_case_cooldown(owner_id, case_key)

    kind, msg_amount, vip_days = _roll_case_item(case_data)

    if kind == "vip":
        give_vip_days(owner_id, vip_days)
    else:
        add_balance(owner_id, msg_amount)

    await callback.answer()

    # ─── Анимация в том же сообщении ───
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

    # ─── Результат ───
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

# =========================================================
#  /case, /rarecase, /lcase
# =========================================================

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
        bank_line = f"🏦 Банк: <b>{bank_info['balance']:,}</b> msg"

        text = (
            f"👤 <b>{fname}</b> | <code>{uid}</code>\n"
            f"💰 Баланс: <b>{balance:,}</b> msg\n"
            f"{bank_line}\n"
            f"👻 Имя: <b>{display_name}</b>\n"
            f"⭐ Репутация: <b>{rep}</b>\n"
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

START_PHOTO = "AgACAgIAAxkBAAIMWWrOF8WYyyI6YFFdt1voAAGprg0H-AACNB9rG471cUotKqhmO_sDxAEAAwIAA3gAAz0E"


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

    # ─── Реферальная ссылка? ───
    args = message.text.split()
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

    # ─── Кнопки ───
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🎁 Бонус", callback_data="prof_daily"),
            InlineKeyboardButton(text="👤 Профиль", callback_data="start_profile"),
        ],
        [
            InlineKeyboardButton(text="🎰 Казино", callback_data="start_casino"),
            InlineKeyboardButton(text="🏆 Топ", callback_data="start_top"),
        ],
        [
            InlineKeyboardButton(text="📖 Все команды", callback_data="start_help"),
            InlineKeyboardButton(text="📢 Канал", url="https://t.me/Amina_updates"),
        ],
    ])

    # ─── Новый юзер или старый? ───
    if is_new_referral:
        # Пришёл по рефке
        text = (
            f"{GREET} Привет, <b>{user.full_name}</b>!\n\n"
            f"{GIFT} Ты пришёл по реферальной ссылке!\n"
            f"└─ Бонус: <b>+{REFERRAL_REWARD}</b> msg\n"
            f"└─ VIP на <b>{REFERRAL_VIP_DAYS}</b> день\n\n"
            f"{MONEY} Твой баланс: <b>{get_balance(user.id):,}</b> msg\n\n"
            f"━━━━━━━━━━━━━━━\n"
            f"🎯 <b>С чего начать</b>\n"
            f"━━━━━━━━━━━━━━━\n\n"
            f"1️⃣ Забери ежедневный бонус\n"
            f"2️⃣ Открой профиль\n"
            f"3️⃣ Посмотри топ богачей\n\n"
            f"━━━━━━━━━━━━━━━"
        )
    elif balance > 0:
        # Старый юзер
        rank = get_user_rank(user.id)
        lvl = get_user_level(user.id)

        text = (
            f"{GREET} С возвращением, <b>{user.full_name}</b>!\n\n"
            f"{MONEY} Баланс: <b>{balance:,}</b> msg\n"
            f"🏆 Место: <b>#{rank}</b>\n"
            f"📊 Уровень: <b>{lvl['level']}</b>\n\n"
            f"━━━━━━━━━━━━━━━"
        )
    else:
        # Совсем новый
        text = (
            f"{GREET} Добро пожаловать в Амину, <b>{user.full_name}</b>!\n\n"
            f"Это экономический бот с валютой <b>msg</b>.\n\n"
            f"━━━━━━━━━━━━━━━\n"
            f"🎯 <b>С чего начать</b>\n"
            f"━━━━━━━━━━━━━━━\n\n"
            f"1️⃣ Забери первый бонус (500 msg)\n"
            f"2️⃣ Открой профиль\n"
            f"3️⃣ Посмотри топ богачей\n\n"
            f"━━━━━━━━━━━━━━━\n\n"
            f"Держи первый бонус 👇"
        )

    # ─── Отправляем с фото ───
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

# =========================================================
#  CALLBACK'И ДЛЯ /start
# =========================================================

@dp.callback_query(F.data == "start_profile")
async def cb_start_profile(callback: CallbackQuery):
    user = callback.from_user
    ensure_user(user)

    text, kb = _build_profile_page(user.id, user.id, 0)
    if text is None:
        await callback.answer("❌ Профиль не найден", show_alert=True)
        return

    try:
        await callback.message.edit_caption(
            caption=text, parse_mode="HTML", reply_markup=kb
        )
    except Exception:
        try:
            await callback.message.edit_text(
                text, parse_mode="HTML", reply_markup=kb
            )
        except Exception as e:
            print(f"[START] Ошибка профиля: {e}")

    await callback.answer()


@dp.callback_query(F.data == "start_casino")
async def cb_start_casino(callback: CallbackQuery):
    await callback.answer(
        "🎰 Введи /casino [ставка]\n└─ Например: /casino 100",
        show_alert=True
    )


@dp.callback_query(F.data == "start_top")
async def cb_start_top(callback: CallbackQuery):
    user = callback.from_user
    ensure_user(user)

    top = _build_top_with_marriages(user.id, 10)
    if not top:
        await callback.answer("🏆 Топ пуст", show_alert=True)
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
        [InlineKeyboardButton(
            text="👤 Мой профиль",
            callback_data="start_profile"
        )]
    ])

    try:
        await callback.message.edit_caption(
            caption=text, parse_mode="HTML", reply_markup=kb
        )
    except Exception:
        try:
            await callback.message.edit_text(
                text, parse_mode="HTML", reply_markup=kb
            )
        except Exception as e:
            print(f"[START] Ошибка топа: {e}")

    await callback.answer()


@dp.callback_query(F.data == "start_help")
async def cb_start_help(callback: CallbackQuery):
    user_id = callback.from_user.id
    is_admin = is_owner(user_id) or bool(get_user_levels(user_id))
    text, kb = _build_help_page(0, is_admin)

    try:
        await callback.message.edit_caption(
            caption=text, parse_mode="HTML", reply_markup=kb
        )
    except Exception:
        try:
            await callback.message.edit_text(
                text, parse_mode="HTML", reply_markup=kb
            )
        except Exception as e:
            print(f"[START] Ошибка помощи: {e}")

    await callback.answer()


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
        f"{LINK} <b>Твоя реферальная ссылка:</b>\n"
        f"<code>{ref_link}</code>\n\n"
        f"{USERS} Приглашено: <b>{stats['total']}</b>\n"
        f"{CHECK} Активных: <b>{stats['active']}</b>\n"
        f"⏳ В ожидании: <b>{stats['pending']}</b>\n"
        f"💤 Сгорело: <b>{stats['burned']}</b>\n\n"
        f"{MONEY} Заработано: <b>{stats['earned']:,}</b> msg\n"
        f"{GIFT} Наград сегодня: <b>{rewards_today}/{REFERRAL_MAX_PER_DAY}</b>"
        f" (осталось {left_today})\n\n"
        f"<b>Как это работает:</b>\n"
        f"└─ Ты получаешь <b>{REFERRER_REWARD}</b> msg за реферала\n"
        f"└─ Реферал должен написать <b>{REFERRAL_THRESHOLD}</b> сообщений\n"
        f"└─ Реферал получает <b>{REFERRAL_REWARD}</b> msg + VIP на {REFERRAL_VIP_DAYS} день сразу\n"
        f"└─ Лимит: <b>{REFERRAL_MAX_PER_DAY}</b> награды за 24 часа"
    )

    await message.answer(
        text, parse_mode="HTML",
        reply_to_message_id=message.message_id
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
          f"charge={payment.telegram_payment_charge_id}")

    # 🔒 Идемпотентность — не начисляем второй раз
    if has_charge_id(payment.telegram_payment_charge_id):
        await message.answer(
            "⚠️ Этот платёж уже был обработан",
            parse_mode="HTML"
        )
        return

    # 🔍 Валидация payload
    try:
        parts = payment.invoice_payload.split("_")
        if len(parts) != 3 or parts[0] != "buymsg":
            raise ValueError("Неверный формат payload")

        payload_user_id = int(parts[1])
        stars = int(parts[2])

        if payload_user_id != user.id:
            raise ValueError("Payload не совпадает с пользователем")

        if stars != payment.total_amount:
            raise ValueError("Сумма не совпадает")

        package = get_package_by_stars(stars)
        if package is None:
            raise ValueError(f"Пакет {stars}⭐ не найден")

        msg_amount, bonus = package

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

    # 🔢 Глобальный номер платежа
    payment_number = get_next_payment_number()
    payment_code = f"#paymsg{payment_number}"

    save_payment_code(payment.telegram_payment_charge_id, payment_code)

    # 🎉 Уведомляем юзера
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

    # 🏆 Проверка достижений
    await _check_and_notify_achievements(user.id, message.chat.id)

    # 📢 Лог в канал
    await log_to_channel(
        f"💳 <b>Платёж Stars</b>\n"
        f"└─ Юзер: {user.full_name} (<code>{user.id}</code>)\n"
        f"└─ Оплачено: <b>{payment.total_amount} ⭐</b>\n"
        f"└─ Начислено: <b>{msg_amount:,} msg</b>\n"
        f"└─ Код: <code>{payment_code}</code>"
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

# ====================================
# /top
# ====================================
TOP_PHOTO = "AgACAgIAAxkBAAIMZWrOHuHwMSiJVnrCGHb27_Vi0F4NAAKPH2sbjvVxSns2-0mR2kvdAQADAgADeAADPQQ"

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

    kb = InlineKeyboardMarkup(inline_keyboard=[
        row,
        [InlineKeyboardButton(
            text="👤 Мой профиль",
            callback_data=f"top_profile_{viewer_id}"
        )],
    ])
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
                "SELECT COUNT(*) FROM banks WHERE balance > ?",
                (my_bank,)
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
            medal = _top_medal(i)
            name = _format_top_name(uid)
            marker = " ← ты" if uid == viewer_id else ""
            lines.append(
                f"{medal} {name} — 🔥 <b>{streak}/7</b>{marker}"
            )

        # Твоё место
        viewer_streak = get_daily_streak(viewer_id)
        if viewer_streak > 0:
            # Считаем ранг
            try:
                conn = sqlite3.connect("users.db")
                cur = conn.cursor()
                cur.execute(
                    "SELECT COUNT(*) FROM users WHERE daily_streak > ?",
                    (viewer_streak,)
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
        await message.answer(
            text, parse_mode="HTML", reply_markup=kb,
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


@dp.callback_query(F.data.startswith("top_profile_"))
async def cb_top_profile(callback: CallbackQuery):
    parts = callback.data.split("_")
    # top_profile_{viewer_id}
    if len(parts) != 3:
        await callback.answer("⚠️ Ошибка данных", show_alert=True)
        return

    try:
        viewer_id = int(parts[2])
    except ValueError:
        await callback.answer("⚠️ Ошибка данных", show_alert=True)
        return

    if callback.from_user.id != viewer_id:
        await callback.answer("❌ Это не твой профиль", show_alert=True)
        return

    text, kb = _build_profile_page(viewer_id, viewer_id, 0)
    if text is None:
        await callback.answer("❌ Профиль не найден", show_alert=True)
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
        print(f"[TOP] Ошибка профиля: {e}")
    await callback.answer()
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
                "└─ или /gift @username [сумма]",
                parse_mode="HTML"
            )
            return

        a, b = args
        if a.startswith("@"):
            target_arg, amount_str = a, b
        elif b.startswith("@"):
            target_arg, amount_str = b, a
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

        # Ищем в БД
        conn = sqlite3.connect("users.db")
        cur = conn.cursor()
        uname = target_arg.lstrip("@")

        cur.execute(
            "SELECT user_id, full_name FROM users WHERE LOWER(username) = LOWER(?)",
            (uname,)
        )
        row = cur.fetchone()
        conn.close()

        if row is not None:
            target_id, target_name = row
        else:
            # Может, это бот? Попробуем получить через Telegram
            try:
                chat = await bot.get_chat(target_arg)
                if chat.type == "private":
                    target_id = chat.id
                    target_name = chat.full_name or chat.username or f"ID:{target_id}"
                    target_is_bot = chat.is_bot if hasattr(chat, 'is_bot') else False
                else:
                    await message.answer("❌ Не могу отправить msg в канал/группу")
                    return
            except Exception:
                await message.answer(
                    "❌ Пользователь не найден.\n"
                    "└─ Юзер должен написать боту хотя бы раз,\n"
                    "    или укажи @username правильно"
                )
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
            # Положительное — реальный перевод боту (msg исчезают из экономики)
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

            # Записываем в БД (нужна запись для бота, чтобы transfer сработал)
            # Но бота не показываем в топах
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
                f"🎁 <b>{bot_name}</b> благодарит тебя за <b>{amount:,}</b> msg!\n\n"
                f"└─ Твой баланс: {new_balance:,} msg\n\n"
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
            # Отрицательное — «подарок-шутка», ничего не делаем
            await message.answer(
                f"😏 Бот <b>{bot_name}</b> принял твой «подарок» "
                f"на <b>{amount:,}</b> msg...\n\n"
                f"└─ Но твои msg остались с тобой 😉\n"
                f"└─ Баланс: {get_balance(user.id):,} msg"
            )
            # Не логируем в транзакции
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

    # ─── Анимация ───
    msg = await message.answer(
        "🎁 <b>Открываем подарок…</b>",
        parse_mode="HTML"
    )
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

    # ─── Streak для отображения ───
    if is_bonus_day:
        display_streak = 7
    else:
        display_streak = new_streak

    # ─── Прогресс-бар ───
    filled = min(display_streak, 7)
    streak_bar = "▰" * filled + "▱" * (7 - filled)

    # ─── Следующая сумма ───
    next_amount = DAILY_AMOUNT if not vip else DAILY_VIP_AMOUNT
    bonus_amount = 2500 if not vip else 5000

    # ─── До 7-го дня ───
    days_left = 7 - display_streak

    # ─── Сборка текста ───
    vip_note = f"\n👑 VIP-бонус x2!" if vip else ""

    lines = [
        f"🎁 <b>Ежедневный бонус</b>",
        "",
        f"✅ Получено: <b>+{amount:,}</b> msg{vip_note}",
        "",
    ]

    if is_bonus_day:
        lines.append(f"🔥 <b>Streak: 7/7</b> — бонус ×5! 🎉")
        lines.append(f"{streak_bar}")
        lines.append("")
        lines.append(f"🎊 <b>Streak начинается заново!</b>")
        lines.append(f"└─ Завтра: +{next_amount:,} msg")
    else:
        lines.append(f"🔥 Streak: <b>{display_streak}/7</b>")
        lines.append(f"{streak_bar} {display_streak} дн.")
        lines.append("")
        lines.append(f"└─ Завтра: +{next_amount:,} msg")

        if days_left <= 2:
            lines.append(f"└─ 🔥 Через <b>{days_left}</b> дн. — <b>+{bonus_amount:,} msg</b> 🎉")
        else:
            lines.append(f"└─ На 7-й день: <b>+{bonus_amount:,} msg</b> 🎉")

    lines.append("")
    lines.append(f"💰 Баланс: <b>{new_balance:,}</b> msg")
    lines.append(f"⏳ Следующий: <b>через 24ч</b>")

    text = "\n".join(lines)

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
        await msg.edit_text(text, parse_mode="HTML", reply_markup=kb)
    except Exception as e:
        print(f"[DAILY] Ошибка редактирования: {e}")
        await message.answer(text, parse_mode="HTML", reply_markup=kb)

    # ─── Логируем 7-й день ───
    if is_bonus_day:
        await log_to_channel(
            f"🎁 <b>Streak 7/7!</b>\n"
            f"└─ Юзер: {user.full_name} (<code>{user.id}</code>)\n"
            f"└─ Получено: <b>+{amount:,}</b> msg"
        )

# =====================================
#  CALLBACK'И ДЛЯ /daily
# =====================================
@dp.callback_query(F.data == "daily_casino")
async def cb_daily_casino(callback: CallbackQuery):
    await callback.answer(
        "🎰 Введи: /casino [ставка]\n"
        "└─ Пример: /casino 100",
        show_alert=True
    )


@dp.callback_query(F.data == "daily_case")
async def cb_daily_case(callback: CallbackQuery):
    await callback.answer(
        "🎁 Введи: /case\n"
        "└─ Стоимость: 1000 msg",
        show_alert=True
    )


@dp.callback_query(F.data == "daily_profile")
async def cb_daily_profile(callback: CallbackQuery):
    user = callback.from_user
    text, kb = _build_profile_page(user.id, user.id, 0)
    if text is None:
        await callback.answer("❌ Профиль не найден", show_alert=True)
        return

    try:
        await callback.message.edit_text(
            text, parse_mode="HTML", reply_markup=kb
        )
    except Exception as e:
        print(f"[DAILY] Ошибка: {e}")
    await callback.answer()

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

    display = nick or fname

    if nick:
        head = f"🎭 Твой ник: <b>{nick}</b>"
    else:
        head = "🎭 Твой ник: не установлен"

    lines = [head]

    if changed_at:
        lines.append(f"└─ Изменён: {_format_time_ago(changed_at)}")

    lines.append(f"└─ В топе: <b>{display}</b> — {balance:,} msg")

    lines.append("")
    if vip:
        lines.append("📋 1–20 символов · 👑 VIP: без кулдауна")
    else:
        lines.append("📋 1–20 символов · кулдаун 24ч (VIP — без)")
    lines.append("└─ Без @ и переносов строк")

    can_change = True
    cooldown = timedelta(hours=24)

    if not vip and changed_at:
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

    if can_change or vip:
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

    kb_rows.append([
        InlineKeyboardButton(
            text="👤 Профиль",
            callback_data="nick_profile"
        )
    ])

    kb = InlineKeyboardMarkup(inline_keyboard=kb_rows)
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

        await message.answer(
            text, parse_mode="HTML", reply_markup=kb,
            reply_to_message_id=message.message_id
        )
        return

    # ─── С аргументом — установить ник ───
    new_nick = args[1].strip()

    if len(new_nick) < 1 or len(new_nick) > 20:
        await message.answer(
            "❌ Ник должен быть от 1 до 20 символов",
            reply_to_message_id=message.message_id
        )
        return

    forbidden = ["\n", "\r", "\t"]
    if any(ch in new_nick for ch in forbidden):
        await message.answer(
            "❌ Ник не должен содержать переносов строк",
            reply_to_message_id=message.message_id
        )
        return

    if "@" in new_nick:
        await message.answer(
            "❌ Ник не должен содержать @",
            reply_to_message_id=message.message_id
        )
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
                        parse_mode="HTML",
                        reply_to_message_id=message.message_id
                    )
                    return
            except ValueError:
                pass

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

    await msg.edit_text(
        f"✅ <b>Ник изменён!</b>{vip_note}\n\n"
        f"└─ Новый: <b>{new_nick}</b>\n"
        f"└─ В топе: <b>{new_nick}</b> — {get_balance(user.id):,} msg",
        parse_mode="HTML"
    )

    await log_to_channel(
        f"🎭 <b>Смена ника</b>\n"
        f"└─ Юзер: {user.full_name} (<code>{user.id}</code>)\n"
        f"└─ Новый ник: <b>{new_nick}</b>"
    )


# =====================================
#  CALLBACK'И ДЛЯ /nick
# =====================================
@dp.callback_query(F.data == "nick_change")
async def cb_nick_change(callback: CallbackQuery):
    await callback.answer(
        "🎭 Введи: /nick [новое имя]\n"
        "└─ Пример: /nick Антон\n\n"
        "💡 1–20 символов, без @ и переносов",
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
    if not vip:
        _, changed_at = get_nick(user_id)
        if changed_at:
            try:
                last_dt = datetime.fromisoformat(changed_at)
                elapsed = datetime.now() - last_dt
                if elapsed < timedelta(hours=24):
                    remaining = timedelta(hours=24) - elapsed
                    h = remaining.seconds // 3600
                    m = (remaining.seconds % 3600) // 60
                    await callback.answer(
                        f"⏳ Убрать можно через {h}ч {m}м",
                        show_alert=True
                    )
                    return
            except ValueError:
                pass

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
            f"└─ Текущий: <b>{nick}</b>\n"
            f"└─ В топе будет имя из Telegram\n\n"
            f"💡 Смена также запустит кулдаун 24ч (VIP — без)",
            parse_mode="HTML",
            reply_markup=kb
        )
    except Exception:
        pass
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
        await callback.message.edit_text(
            text, parse_mode="HTML", reply_markup=kb
        )
    except Exception:
        pass
    await callback.answer("❌ Отменено")


@dp.callback_query(F.data == "nick_profile")
async def cb_nick_profile(callback: CallbackQuery):
    user = callback.from_user
    text, kb = _build_profile_page(user.id, user.id, 0)
    if text is None:
        await callback.answer("❌ Профиль не найден", show_alert=True)
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
        print(f"[NICK] Ошибка: {e}")
    await callback.answer()


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


# =====================================
#  /rob
# =====================================
# =========================================================
#  /rob — ограбление
# =========================================================

ROB_SUCCESS_PHRASES = [
    "Ты вломился в дом {target}!\n└─ Схватил: <b>+{amount}</b> msg\n└─ И сбежал в закат 🌅",
    "Пока {target} спал, ты вынес <b>{amount}</b> msg!\n└─ Тише едешь — дальше будешь 🤫",
    "Чисто сработано! <b>+{amount}</b> msg в кармане\n└─ Никто ничего не видел 👀",
    "{target} даже не заметил пропажи!\n└─ <b>+{amount}</b> msg уже у тебя 🏃",
]

ROB_FAIL_PHRASES = [
    "Тебя поймали за руку!\n└─ Штраф: <b>-{penalty}</b> msg\n└─ Сирена 🚨 и позор",
    "{target} вызвал полицию!\n└─ Штраф: <b>-{penalty}</b> msg\n└─ Беги, пока можешь 🚓",
    "Побег не удался.\n└─ <b>-{penalty}</b> msg\n└─ Урок на будущее 😅",
    "Тебя опознали по камерам!\n└─ Штраф: <b>-{penalty}</b> msg\n└─ В следующий раз — маску 🎭",
]


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

    # ─── Проверки ───
    if target_obj and target_obj.is_bot:
        await message.answer("❌ Нельзя грабить бота")
        return

    if target_id == user.id:
        await message.answer("😄 Нельзя грабить самого себя")
        return

    if is_main_owner(target_id):
        await message.answer("❌ Нельзя грабить главного владельца")
        return

    # ─── Кулдаун ───
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

    # ─── Проверки цели ───
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

    # ─── Логика ограбления ───
    lock = get_user_lock(user.id)
    async with lock:
        robber_balance = get_balance(user.id)
        target_vip = is_vip_active(target_id)

        if target_vip:
            success_chance = 0.10
            penalty_rate = 0.10
            vip_note = " (👑 VIP)"
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

            # Случайная фраза
            phrase = random.choice(ROB_SUCCESS_PHRASES)
            body = phrase.format(target=target_name, amount=f"{steal_amount:,}")

            await message.answer(
                f"🥷 <b>УСПЕХ!</b>\n\n"
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

            # Логируем крупные
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

            # Случайная фраза
            phrase = random.choice(ROB_FAIL_PHRASES)
            body = phrase.format(target=target_name, penalty=f"{penalty:,}")

            await message.answer(
                f"🚔 <b>ПРОВАЛ!</b>\n\n"
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

            # Логируем крупные провалы
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
    rate = 0.02 if vip else 0.01
    rate_text = "2%" if vip else "1%"

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
        f"{_p(PREM_BANK, '🏦')} <b>Твой банк</b>{vip_mark}",
        "",
        f"└─ {_p(PREM_MONEY, '💰')} На счету: <b>{balance:,}</b> msg",
        f"└─ {_p(PREM_RATE, '📈')} Ставка: <b>{rate_text} в час</b>",
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

    # Положить — если есть msg в кошельке
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
        # Только снять, если кошелёк пуст
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
# =========================================================
#  CALLBACK: положить в банк
# =========================================================

def _bank_add_kb(user_id: int) -> InlineKeyboardMarkup:
    """Клавиатура быстрых сумм для пополнения."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="1к",    callback_data=f"bank_add_do_1000_{user_id}"),
            InlineKeyboardButton(text="2.5к",  callback_data=f"bank_add_do_2500_{user_id}"),
            InlineKeyboardButton(text="5к",    callback_data=f"bank_add_do_5000_{user_id}"),
        ],
        [
            InlineKeyboardButton(text="10к",   callback_data=f"bank_add_do_10000_{user_id}"),
            InlineKeyboardButton(text="50к",   callback_data=f"bank_add_do_50000_{user_id}"),
            InlineKeyboardButton(text="100к",  callback_data=f"bank_add_do_100000_{user_id}"),
        ],
        [
            InlineKeyboardButton(text="◀️ Назад", callback_data=f"bank_back_{user_id}"),
        ],
    ])


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

    ok, msg, new_bank, new_wallet = bank_put(owner_id, amount)
    if not ok:
        await callback.answer(f"❌ {msg}", show_alert=True)
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

    await callback.answer(f"📥 +{amount:,} msg")


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


# =========================================================
#  /anon — анонимные сообщения
# =========================================================

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

    target_id = None
    target_name = None

    # ─── Определяем получателя ───
    if message.reply_to_message:
        target = message.reply_to_message.from_user
        if target.is_bot:
            await message.answer("❌ Нельзя писать анонимки боту")
            return
        target_id = target.id
        target_name = target.full_name

        args = message.text.split(maxsplit=1)
        if len(args) < 2:
            await message.answer(
                "❌ Напиши текст: /anon [текст]",
                parse_mode="HTML"
            )
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
            "Анонимки со ссылками, юзернеймами и рекламой "
            "не пропускаются.",
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

# =====================================
#  /shadow 
# =====================================

@dp.message(Command("shadow"))
async def cmd_shadow(message: Message):
    log_cmd("🤫 /shadow", message)
    user_id = message.from_user.id
    ensure_user(message.from_user)

    _shadow_users[user_id] = time.monotonic() + SHADOW_DURATION
    print(f"[SHADOW-DEBUG] Пользователь {user_id} добавлен в тень. Всего: {_shadow_users}")

# ====================================
#  /accdel — полное удаление аккаунта
# ====================================

@dp.message(Command("accdel"))
async def cmd_accdel(message: Message):
    log_cmd("🗑️ /accdel", message)
    actor_id = message.from_user.id

    # Только модераторы / senior / owner
    if not is_moder(actor_id) and not is_senior(actor_id):
        await message.answer("⛔ Только для модераторов")
        return

    # Парсинг: /accdel @username на первой строке, причина — со второй
    lines = message.text.split("\n", 1)
    first_line = lines[0].strip()
    reason = lines[1].strip() if len(lines) > 1 else "не указана"

    args = first_line.split()[1:]

    # Ищем цель
    target_id = None
    target_name = None

    if message.reply_to_message:
        target = message.reply_to_message.from_user
        if target.is_bot:
            await message.answer("❌ Нельзя удалить бота")
            return
        target_id = target.id
        target_name = target.full_name
    else:
        if not args or not args[0].startswith("@"):
            await message.answer(
                "❌ Использование:\n"
                "<code>/accdel @username\n"
                "Причина</code>\n\n"
                "Или ответь на сообщение:\n"
                "<code>/accdel\n"
                "Причина</code>",
                parse_mode="HTML"
            )
            return
        target_id, target_name = find_user_id(message, args[0])
        if target_id is None:
            await message.answer("❌ Пользователь не найден")
            return

    # Антифрод
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

    # Проверяем, что юзер вообще есть в БД
    target_data = get_user(target_id)
    if not target_data:
        await message.answer(f"❌ {target_name} не найден в БД")
        return

    # Кнопки подтверждения
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
        # accdel_no_{actor}_{target}
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
        # accdel_yes_{actor}_{target}
        try:
            owner_id = int(parts[2])
            target_id = int(parts[3])
        except (ValueError, IndexError):
            await callback.answer("⚠️ Ошибка данных", show_alert=True)
            return

        if callback.from_user.id != owner_id:
            await callback.answer("❌ Это не для тебя", show_alert=True)
            return

        # Перепроверяем права (на случай, если что-то изменилось)
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

        # Пытаемся уведомить цель (до удаления)
        try:
            await bot.send_message(
                target_id,
                f"{_p(PREM_DELETE, '🗑️')} <b>Твой аккаунт удалён</b>\n\n"
                f"└─ Причина: <b>уточняется у модерации</b>",
                parse_mode="HTML"
            )
        except Exception:
            pass

        # Удаляем
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
            text="📢 Перейти в канал",
            url="https://t.me/Amina_updates"
        )]
    ])

    await message.answer(
        "📢 <b>Канал с обновлениями бота</b>\n\n"
        "└─ Новости\n"
        "└─ Обновления\n"
        "└─ Анонсы ивентов",
        parse_mode="HTML",
        reply_markup=kb,
        reply_to_message_id=message.message_id
    )

# =====================================
#  CATCH-ALL
# =====================================

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

    # ─── Реферальная проверка ───
    try:
        referrer_id = get_referrer(user.id)
        if referrer_id:
            ref_info = get_referral(user.id)
            if ref_info:
                ref_referrer, ref_msg_count, ref_rewarded = ref_info

                # Ещё не награждён и не сгорел
                if ref_rewarded == 0:
                    new_count = increment_referral_msg(user.id)

                    if new_count >= REFERRAL_THRESHOLD:
                        # Проверяем лимит реферера
                        rewards_today = count_rewards_24h(referrer_id)

                        if rewards_today >= REFERRAL_MAX_PER_DAY:
                            # Лимит исчерпан → сгорает
                            mark_referral_rewarded(user.id, reward=False)
                            try:
                                await bot.send_message(
                                    referrer_id,
                                    f"💤 <b>Реферал сгорел</b>\n\n"
                                    f"└─ Лимит <b>{REFERRAL_MAX_PER_DAY}</b> награды за 24ч исчерпан\n"
                                    f"└─ <b>{user.full_name}</b> не засчитан",
                                    parse_mode="HTML"
                                )
                            except Exception:
                                pass
                        else:
                            # Платим
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
    Раз в час (в :00 по Красноярску) отправляет users.db владельцу.
    """
    last_sent_hour = None

    while True:
        try:
            now_kr = datetime.now(timezone(timedelta(hours=7)))

            current_hour_key = (now_kr.day, now_kr.month, now_kr.hour)

            # Отправляем, если наступил новый час
            if last_sent_hour != current_hour_key:
                # Проверяем, что сейчас :00 (первая минута часа)
                # Или если мы пропустили (например, бот спал) — отправляем
                if now_kr.minute == 0 or last_sent_hour is not None:

                    # Проверяем, что файл существует
                    if not os.path.exists(BACKUP_DB_PATH):
                        print(f"[BACKUP] ❌ Файл {BACKUP_DB_PATH} не найден")
                    else:
                        # Формируем подпись
                        day = now_kr.day
                        month = now_kr.month
                        hour = now_kr.hour

                        caption = f"📦 Бэкап за {day:02d}.{month:02d} в {hour:02d}:00"

                        try:
                            # Копируем БД, чтобы не отправлять во время записи
                            backup_copy = f"users_backup_{day:02d}_{month:02d}_{hour:02d}.db"

                            # Копирование через отдельное соединение
                            import sqlite3
                            src = sqlite3.connect(BACKUP_DB_PATH)
                            dst = sqlite3.connect(backup_copy)
                            src.backup(dst)
                            dst.close()
                            src.close()

                            # Отправляем файл
                            doc = FSInputFile(backup_copy)
                            await bot.send_document(
                                chat_id=BACKUP_OWNER_ID,
                                document=doc,
                                caption=caption
                            )

                            print(f"[BACKUP] ✅ Отправлен бэкап: {caption}")

                            # Удаляем временный файл
                            try:
                                os.remove(backup_copy)
                            except Exception:
                                pass 
                            _cleanup_old_backups()

                            last_sent_hour = current_hour_key

                        except Exception as e:
                            print(f"[BACKUP] ❌ Ошибка отправки: {e}")

        except Exception as e:
            print(f"[BACKUP] ❌ Ошибка цикла: {e}")

        await asyncio.sleep(BACKUP_CHECK_INTERVAL)
# =====================================



# =====================================
#  ЗАПУСК
# =====================================

async def main():
    init_db()
    print("Бот запущен...")
    print("Ждём сообщения...\n")
    asyncio.create_task(_duel_watchdog())
    asyncio.create_task(_db_backup_loop())
    print("[STARTUP] Авто-бэкап запущен")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())