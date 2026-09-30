from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.dispatcher.middlewares.base import BaseMiddleware
from typing import Any, Awaitable, Callable, Dict
import asyncio
import random
import sqlite3
import time
from datetime import datetime, timedelta

from database import (
    init_db, ensure_user, get_user, change_balance, add_msg,
    transfer_msg, buy_vip, log_transaction, is_vip_active,
    get_last_daily, claim_daily,
    get_top, get_user_rank, get_history,
)

TOKEN = "8572154161:AAEcHzZnnI_CPAnxFSc2YbTkMgA3Aq79fNg"

bot = Bot(token=TOKEN)
dp = Dispatcher()


# =========================================================
#  МИДЛВАРЬ: +1 msg за сообщение (не за команды), с антифлудом
# =========================================================

_last_reward: dict[int, float] = {}

NORMAL_COOLDOWN = 2.0   # сек между начислениями для обычных
VIP_COOLDOWN = 1.0      # сек между начислениями для VIP


class MsgRewardMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        if event.from_user and not event.from_user.is_bot:
            user = event.from_user
            ensure_user(user)

            # Не начисляем за команды
            is_command = event.text and event.text.startswith("/")
            if not is_command:
                vip = is_vip_active(user.id)
                cooldown = VIP_COOLDOWN if vip else NORMAL_COOLDOWN

                now = time.monotonic()
                last = _last_reward.get(user.id, 0)
                if now - last >= cooldown:
                    add_msg(user.id, 1)
                    _last_reward[user.id] = now

        return await handler(event, data)


dp.message.middleware(MsgRewardMiddleware())


# =========================================================
#  ВСПОМОГАТЕЛЬНОЕ
# =========================================================

def log_cmd(name: str, message: Message):
    """Печатает в консоль, кто какую команду вызвал."""
    user = message.from_user
    user_info = f"@{user.username}" if user.username else f"ID: {user.id}"
    time_str = datetime.now().strftime("%H:%M")
    print(f"\n[{time_str}] {name} | {user_info} | {user.full_name}")


# =========================================================
#  КОНСТАНТЫ /daily
# =========================================================

DAILY_AMOUNT = 500
DAILY_VIP_AMOUNT = 1000
DAILY_COOLDOWN = timedelta(hours=24)


# =========================================================
#  /help
# =========================================================

@dp.message(Command("help"))
async def cmd_help(message: Message):
    log_cmd("📖 /help", message)
    await message.answer(
        "📖 <b>Доступные команды:</b>\n\n"
        "👤 <code>/profile</code> — твой профиль\n"
        "💰 <code>/balance</code> — баланс и VIP\n"
        "🏆 <code>/top</code> — топ-10 богачей\n"
        "📜 <code>/history</code> — последние транзакции\n"
        "💸 <code>/pay [сумма]</code> — перевод (в ответ на сообщение)\n"
        "💸 <code>/pay @username [сумма]</code> — перевод по нику\n"
        "👑 <code>/buyvip [недели]</code> — VIP (1 нед = 1000 msg)\n"
        "🎁 <code>/daily</code> — ежедневный бонус (500 msg)\n"
        "🎰 <code>/casino [ставка]</code> — казино (шанс 45%, x2)\n"
        "📖 <code>/help</code> — этот список\n\n"
        "<b>Как заработать msg:</b>\n"
        "└─ +1 msg за сообщение (раз в 2 сек)\n"
        "└─ Для VIP: +1 msg раз в 1 сек 👑",
        parse_mode="HTML"
    )


# =========================================================
#  /balance
# =========================================================

@dp.message(Command("balance"))
async def cmd_balance(message: Message):
    log_cmd("💰 /balance", message)
    data = ensure_user(message.from_user)

    vip_line = ""
    if data["vip_until"]:
        try:
            until = datetime.fromisoformat(data["vip_until"])
            if until > datetime.now():
                vip_line = f"\n└─ 👑 VIP до {until.strftime('%d.%m.%Y %H:%M')}"
        except ValueError:
            pass

    await message.answer(
        f"💰 <b>Твой баланс</b>\n"
        f"└─ {data['msg_count']} msg{vip_line}",
        parse_mode="HTML"
    )


# =========================================================
#  /profile
# =========================================================

@dp.message(Command("profile"))
async def cmd_profile(message: Message):
    log_cmd("👤 /profile", message)

    # Свой профиль или чужой (если ответили на сообщение)
    target = message.from_user
    if message.reply_to_message and not message.reply_to_message.from_user.is_bot:
        target = message.reply_to_message.from_user

    ensure_user(target)
    data = get_user(target.id)

    if not data:
        await message.answer("❌ Профиль не найден")
        return

    uid, uname, fname, balance, vip_until, last_daily = data
    rank = get_user_rank(uid)

    # VIP статус
    vip_line = "└─ 👑 VIP: нет"
    if vip_until:
        try:
            until = datetime.fromisoformat(vip_until)
            if until > datetime.now():
                vip_line = f"└─ 👑 VIP до {until.strftime('%d.%m.%Y %H:%M')}"
        except ValueError:
            pass

    # Daily
    daily_line = "└─ 🎁 /daily: доступен"
    if last_daily:
        try:
            last_dt = datetime.fromisoformat(last_daily)
            elapsed = datetime.now() - last_dt
            if elapsed < DAILY_COOLDOWN:
                remaining = DAILY_COOLDOWN - elapsed
                h = remaining.seconds // 3600
                m = (remaining.seconds % 3600) // 60
                daily_line = f"└─ 🎁 /daily: через {h} ч {m} мин"
        except ValueError:
            pass

    await message.answer(
        f"👤 <b>Профиль</b>\n\n"
        f"└─ ID: <code>{uid}</code>\n"
        f"└─ Юзернейм: @{uname or '—'}\n"
        f"└─ Имя: {fname}\n"
        f"└─ 💰 Баланс: <b>{balance}</b> msg\n"
        f"{vip_line}\n"
        f"{daily_line}\n"
        f"└─ 🏆 Место в топе: <b>#{rank}</b>",
        parse_mode="HTML"
    )


# =========================================================
#  /top
# =========================================================

@dp.message(Command("top"))
async def cmd_top(message: Message):
    log_cmd("🏆 /top", message)
    user = message.from_user
    ensure_user(user)

    top = get_top(10)
    if not top:
        await message.answer("Пока пусто 🤷")
        return

    medals = {1: "🥇", 2: "🥈", 3: "🥉"}
    lines = ["🏆 <b>Топ-10 по балансу</b>\n"]
    for i, (uid, uname, fname, balance) in enumerate(top, start=1):
        medal = medals.get(i, f"{i}.")
        name = f"@{uname}" if uname else fname
        marker = " ← ты" if uid == user.id else ""
        lines.append(f"{medal} {name} — <b>{balance}</b> msg{marker}")

    my_rank = get_user_rank(user.id)
    my_data = get_user(user.id)
    my_balance = my_data[3] if my_data else 0

    if my_rank > 10:
        lines.append(f"\n📍 Ты на {my_rank} месте — {my_balance} msg")

    await message.answer("\n".join(lines), parse_mode="HTML")


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
        await message.answer("📭 История пуста")
        return

    kind_emoji = {
        "transfer":    "💸",
        "buy_vip":     "👑",
        "casino_win":  "🎰",
        "casino_lose": "🎰",
        "daily":       "🎁",
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
                lines.append(f"{emoji} → перевод <b>-{abs(amount)}</b> msg | {date_str}")
            else:
                lines.append(f"{emoji} ← перевод <b>+{abs(amount)}</b> msg | {date_str}")
        elif kind == "daily":
            lines.append(f"{emoji} бонус <b>+{abs(amount)}</b> msg | {date_str}")
        elif kind == "buy_vip":
            lines.append(f"{emoji} покупка VIP <b>{amount}</b> msg | {date_str}")
        elif kind == "casino_win":
            lines.append(f"{emoji} казино победа <b>+{abs(amount)}</b> msg | {date_str}")
        elif kind == "casino_lose":
            lines.append(f"{emoji} казино проигрыш <b>{amount}</b> msg | {date_str}")
        else:
            lines.append(f"{emoji} {kind} <b>{amount}</b> msg | {date_str}")

    await message.answer("\n".join(lines), parse_mode="HTML")


# =========================================================
#  /pay
# =========================================================

@dp.message(Command("pay"))
async def cmd_pay(message: Message):
    log_cmd("💸 /pay", message)
    user = message.from_user

    args = message.text.split()[1:]
    target_id = None
    target_name = None
    amount = None

    if message.reply_to_message:
        # Перевод в ответ на сообщение
        if len(args) != 1:
            await message.answer(
                "❌ Формат: ответь на сообщение и напиши <code>/pay [сумма]</code>",
                parse_mode="HTML"
            )
            return
        try:
            amount = int(args[0])
        except ValueError:
            await message.answer("❌ Сумма должна быть числом")
            return
        target = message.reply_to_message.from_user
        if target.is_bot:
            await message.answer("❌ Нельзя переводить боту")
            return
        target_id = target.id
        target_name = target.full_name
        ensure_user(target)
    else:
        # Перевод по @username
        if len(args) != 2:
            await message.answer(
                "❌ Использование:\n"
                "└─ ответь на сообщение и напиши <code>/pay [сумма]</code>\n"
                "└─ или <code>/pay @username [сумма]</code>",
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
            await message.answer("❌ Сумма должна быть числом")
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

    ok, info = transfer_msg(user.id, target_id, amount)
    if not ok:
        await message.answer(f"❌ {info}")
        return

    await message.answer(
        f"✅ Перевод выполнен!\n"
        f"└─ Кому: {target_name}\n"
        f"└─ Сумма: {amount} msg"
    )


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
            "❌ Использование: <code>/buyvip [недели]</code>\n"
            "└─ 1 неделя = 1000 msg",
            parse_mode="HTML"
        )
        return

    try:
        weeks = int(args[0])
    except ValueError:
        await message.answer("❌ Количество недель должно быть числом")
        return

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
        f"⚡ Теперь ты получаешь +1 msg раз в 1 сек!",
        parse_mode="HTML"
    )


# =========================================================
#  /casino
# =========================================================

@dp.message(Command("casino"))
async def cmd_casino(message: Message):
    log_cmd("🎰 /casino", message)
    user = message.from_user

    args = message.text.split()[1:]
    if len(args) != 1:
        await message.answer(
            "❌ Использование: <code>/casino [ставка]</code>",
            parse_mode="HTML"
        )
        return

    try:
        bet = int(args[0])
    except ValueError:
        await message.answer("❌ Ставка должна быть числом")
        return

    if bet <= 0:
        await message.answer("❌ Ставка должна быть положительной")
        return

    data = get_user(user.id)
    balance = data[3]
    if balance < bet:
        await message.answer(f"❌ Недостаточно msg (баланс: {balance})")
        return

    # Стартовое сообщение и анимация
    msg = await message.answer("🎰 <b>Крутим барабаны…</b>", parse_mode="HTML")

    slots = ["🍒", "🍋", "🍊", "💎", "7️⃣", "⭐"]
    for _ in range(6):
        line = " | ".join(random.choices(slots, k=3))
        await asyncio.sleep(0.35)
        try:
            await msg.edit_text(
                f"🎰 <b>Крутим барабаны…</b>\n\n{line}",
                parse_mode="HTML"
            )
        except Exception:
            pass

    # Финальный результат
    win = random.random() < 0.45
    final = " | ".join(random.choices(slots, k=3))

    if win:
        new_balance = change_balance(user.id, bet)
        log_transaction(user.id, user.id, bet, "casino_win")
        result_text = (
            f"🎰 <b>Крутим барабаны…</b>\n\n"
            f"{final}\n\n"
            f"🎉 <b>Победа!</b>\n"
            f"└─ Ставка: {bet} msg\n"
            f"└─ Выигрыш: +{bet} msg\n"
            f"└─ Баланс: {new_balance} msg"
        )
    else:
        new_balance = change_balance(user.id, -bet)
        log_transaction(user.id, user.id, -bet, "casino_lose")
        result_text = (
            f"🎰 <b>Крутим барабаны…</b>\n\n"
            f"{final}\n\n"
            f"😢 <b>Проигрыш…</b>\n"
            f"└─ Ставка: {bet} msg\n"
            f"└─ Потеряно: -{bet} msg\n"
            f"└─ Баланс: {new_balance} msg"
        )

    await msg.edit_text(result_text, parse_mode="HTML")


# =========================================================
#  /daily
# =========================================================

@dp.message(Command("daily"))
async def cmd_daily(message: Message):
    log_cmd("🎁 /daily", message)
    user = message.from_user
    ensure_user(user)

    last = get_last_daily(user.id)
    now = datetime.now()

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
        except ValueError:
            pass

    vip = is_vip_active(user.id)
    amount = DAILY_VIP_AMOUNT if vip else DAILY_AMOUNT

    # Анимация
    msg = await message.answer("🎁 <b>Открываем подарок…</b>", parse_mode="HTML")
    frames = ["📦", "📦✨", "🎁", "🎁✨", "🎉🎁", "🎉🎁✨"]
    for frame in frames:
        await asyncio.sleep(0.3)
        try:
            await msg.edit_text(
                f"🎁 <b>Открываем подарок…</b>\n\n{frame}",
                parse_mode="HTML"
            )
        except Exception:
            pass

    new_balance = claim_daily(user.id, amount)
    vip_note = "\n└─ 👑 VIP-бонус x2!" if vip else ""

    await msg.edit_text(
        f"🎁 <b>Ежедневный бонус получен!</b>\n\n"
        f"🎉 +{amount} msg{vip_note}\n"
        f"└─ Баланс: {new_balance} msg\n\n"
        f"Следующий бонус — через 24 часа.",
        parse_mode="HTML"
    )


# =========================================================
#  ЗАПУСК
# =========================================================

async def main():
    init_db()
    print("Бот запущен...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())