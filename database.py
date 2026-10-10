import sqlite3
from datetime import datetime, timedelta, timezone

DB_PATH = "users.db"


# =====================================
#  ИНИЦИАЛИЗАЦИЯ БД
# =====================================

def init_db():
    """Создаёт таблицы и добавляет недостающие колонки."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id       INTEGER PRIMARY KEY,
            username      TEXT,
            full_name     TEXT,
            msg_count     INTEGER DEFAULT 0,
            vip_until     TEXT,
            last_daily    TEXT,
            last_activity TEXT,
            daily_streak  INTEGER DEFAULT 0
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS bans (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id      INTEGER,
            reason       TEXT,
            banned_at    TEXT,
            banned_until TEXT,
            banned_by    INTEGER
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            from_id     INTEGER,
            to_id       INTEGER,
            amount      INTEGER,
            kind        TEXT,
            created_at  TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS banks (
            user_id          INTEGER PRIMARY KEY,
            balance          INTEGER DEFAULT 0,
            last_interest_at TEXT,
            total_earned     INTEGER DEFAULT 0
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS anon_messages (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            from_id    INTEGER,
            to_id      INTEGER,
            text       TEXT,
            created_at TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS anon_mutes (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id      INTEGER,
            reason       TEXT,
            muted_at     TEXT,
            muted_until  TEXT,
            muted_by     INTEGER
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS bot_info (
            key   TEXT PRIMARY KEY,
            value TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS shop_items (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            name            TEXT,
            price           INTEGER,
            effect_type     TEXT,
            duration_hours  INTEGER,
            limit_total     INTEGER DEFAULT 0,
            limit_per_user  INTEGER DEFAULT 0,
            visible_to      TEXT DEFAULT 'all',
            sold_count      INTEGER DEFAULT 0,
            created_at      TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS user_purchases (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id      INTEGER,
            item_id      INTEGER,
            purchased_at TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS access_levels (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id   INTEGER,
            level     TEXT,
            added_by  INTEGER,
            added_at  TEXT,
            UNIQUE(user_id, level)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS warns (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id    INTEGER,
            reason     TEXT,
            warned_by  INTEGER,
            warned_at  TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS case_cooldowns (
            user_id     INTEGER,
            case_type   TEXT,
            last_open   TEXT,
            PRIMARY KEY (user_id, case_type)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS marriages (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            user1_id     INTEGER,
            user2_id     INTEGER,
            married_at   TEXT,
            balance      INTEGER DEFAULT 0
        )
    """)
	
	# Таблица для платежей (в init_db)
    cur.execute("""
   	 CREATE TABLE IF NOT EXISTS payments (
   	     id                       INTEGER PRIMARY KEY AUTOINCREMENT,
   	     user_id                  INTEGER,
       	 stars_amount             INTEGER,
      	  msg_amount               INTEGER,
     	   telegram_charge_id       TEXT,
     	   provider_charge_id       TEXT,
    	    created_at               TEXT
    )
""")

    cur.execute("""
   	 CREATE TABLE IF NOT EXISTS tictactoe (
    	    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    	    player_x_id    INTEGER,
    	    player_o_id    INTEGER,
   	     bet            INTEGER,
  	      board          TEXT,
  	      turn_id        INTEGER,
 	       status         TEXT DEFAULT 'pending',
     	   message_id     INTEGER,
     	   chat_id        INTEGER,
    	    created_at     TEXT,
   	     last_move_at   TEXT
  	  )
	""")

# =====================================
#  ПЛАТЕЖИ (TELEGRAM STARS)
# =====================================

def log_payment(user_id: int, stars: int, msg: int,
                telegram_charge_id: str, provider_charge_id: str):
    """Логирует успешный платёж Stars."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO payments "
        "(user_id, stars_amount, msg_amount, telegram_charge_id, "
        "provider_charge_id, created_at) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (user_id, stars, msg, telegram_charge_id,
         provider_charge_id, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()


def has_charge_id(charge_id: str) -> bool:
    """Проверяет, не был ли уже обработан этот платёж."""
    if not charge_id:
        return False

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "SELECT 1 FROM payments WHERE telegram_charge_id = ? LIMIT 1",
        (charge_id,)
    )
    row = cur.fetchone()
    conn.close()
    return row is not None


def get_payment_stats() -> dict:
    """Статистика по платежам: количество, звёзды, msg."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "SELECT COUNT(*), "
        "COALESCE(SUM(stars_amount), 0), "
        "COALESCE(SUM(msg_amount), 0) "
        "FROM payments"
    )
    row = cur.fetchone()
    conn.close()
    return {
        "total_payments": row[0],
        "total_stars":    row[1],
        "total_msg":      row[2],
    }


def get_user_payments(user_id: int, limit: int = 10):
    """История платежей конкретного юзера."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "SELECT stars_amount, msg_amount, telegram_charge_id, created_at "
        "FROM payments WHERE user_id = ? "
        "ORDER BY id DESC LIMIT ?",
        (user_id, limit)
    )
    rows = cur.fetchall()
    conn.close()
    return rows
	
    cur.execute("""
    	CREATE TABLE IF NOT EXISTS tictactoe (
        	id             INTEGER PRIMARY KEY AUTOINCREMENT,
       	 player_x_id    INTEGER,
      	  player_o_id    INTEGER,
   	     bet            INTEGER,
  	      board          TEXT,        -- "---------" (9 символов: X, O, -)
    	    turn_id        INTEGER,     -- чей сейчас ход
     	   status         TEXT DEFAULT 'pending',  -- pending / active / done
    	    message_id     INTEGER,
    	    chat_id        INTEGER,
    	    created_at     TEXT,
    	    last_move_at   TEXT
  	  )
	""")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS duels (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            challenger_id  INTEGER,
            opponent_id    INTEGER,
            bet            INTEGER,
            status         TEXT DEFAULT 'pending',
            hp1            INTEGER DEFAULT 3,
            hp2            INTEGER DEFAULT 3,
            am1            INTEGER DEFAULT 3,
            am2            INTEGER DEFAULT 3,
            turn           INTEGER DEFAULT 0,
            message_id     INTEGER,
            chat_id        INTEGER,
            move1          TEXT,
            move2          TEXT,
            used_heal1     INTEGER DEFAULT 0,
            used_heal2     INTEGER DEFAULT 0,
            created_at     TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS user_stats (
            user_id            INTEGER PRIMARY KEY,
            total_messages     INTEGER DEFAULT 0,
            total_casino_games INTEGER DEFAULT 0,
            total_casino_losses INTEGER DEFAULT 0,
            total_robs         INTEGER DEFAULT 0,
            total_gifts_sent   INTEGER DEFAULT 0,
            total_duel_wins    INTEGER DEFAULT 0
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS achievements (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id      INTEGER,
            ach_id       TEXT,
            unlocked_at  TEXT,
            UNIQUE(user_id, ach_id)
        )
    """)

    # Миграция users
    cur.execute("PRAGMA table_info(users)")
    existing_cols = {row[1] for row in cur.fetchall()}
    needed = {
        "username":           "TEXT",
        "full_name":          "TEXT",
        "msg_count":          "INTEGER DEFAULT 0",
        "vip_until":          "TEXT",
        "last_daily":         "TEXT",
        "last_activity":      "TEXT",
        "daily_streak":       "INTEGER DEFAULT 0",
        "nick":               "TEXT",
        "nick_changed_at":    "TEXT",
        "last_rob":           "TEXT",
        "triple_until":       "TEXT",
        "shield_until":       "TEXT",
        "hide_balance_until": "TEXT",
        "anon_shield_until":  "TEXT",
        "lucky_until":        "TEXT",
        "custom_title":       "TEXT",
        "title_changed_at":   "TEXT",
    }
    for col, col_type in needed.items():
        if col not in existing_cols:
            cur.execute(f"ALTER TABLE users ADD COLUMN {col} {col_type}")
            print(f"[DB] Добавлена колонка: users.{col}")

    # Миграция marriages — добавить balance
    cur.execute("PRAGMA table_info(marriages)")
    marry_cols = {row[1] for row in cur.fetchall()}
    if "balance" not in marry_cols:
        cur.execute("ALTER TABLE marriages ADD COLUMN balance INTEGER DEFAULT 0")
        print("[DB] Добавлена колонка: marriages.balance")

    conn.commit()
    conn.close()


# =====================================
#  ЮЗЕРЫ
# =====================================

def ensure_user(user) -> dict:
    """Создаёт пользователя, если его нет. Возвращает dict."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT user_id FROM users WHERE user_id = ?", (user.id,))
    if cur.fetchone() is None:
        cur.execute(
            "INSERT INTO users (user_id, username, full_name, msg_count, vip_until, last_daily, last_activity) "
            "VALUES (?, ?, ?, 0, NULL, NULL, ?)",
            (user.id, user.username, user.full_name, datetime.now().isoformat())
        )
    else:
        cur.execute(
            "UPDATE users SET username = ?, full_name = ?, last_activity = ? WHERE user_id = ?",
            (user.username, user.full_name, datetime.now().isoformat(), user.id)
        )
    conn.commit()

    cur.execute(
        "SELECT user_id, username, full_name, msg_count, vip_until, last_daily "
        "FROM users WHERE user_id = ?",
        (user.id,)
    )
    row = cur.fetchone()
    conn.close()
    return {
        "user_id": row[0],
        "username": row[1],
        "full_name": row[2],
        "msg_count": row[3],
        "vip_until": row[4],
        "last_daily": row[5],
    }


def get_user(user_id: int):
    """Возвращает строку пользователя или None."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "SELECT user_id, username, full_name, msg_count, vip_until, last_daily "
        "FROM users WHERE user_id = ?",
        (user_id,)
    )
    row = cur.fetchone()
    conn.close()
    return row


def change_balance(user_id: int, amount: int) -> int:
    """Начисляет (+) или списывает (-) msg. Возвращает новый баланс."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "UPDATE users SET msg_count = msg_count + ? WHERE user_id = ?",
        (amount, user_id)
    )
    conn.commit()
    cur.execute("SELECT msg_count FROM users WHERE user_id = ?", (user_id,))
    row = cur.fetchone()
    new_balance = row[0] if row else 0
    conn.close()
    return new_balance


def add_msg(user_id: int, amount: int):
    """Начисляет msg без транзакции."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "UPDATE users SET msg_count = msg_count + ? WHERE user_id = ?",
        (amount, user_id)
    )
    conn.commit()
    conn.close()


def log_transaction(from_id, to_id, amount, kind):
    """Пишет транзакцию в историю."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO transactions (from_id, to_id, amount, kind, created_at) "
        "VALUES (?, ?, ?, ?, ?)",
        (from_id, to_id, amount, kind, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()


# =====================================
#  🔧 FIX: АТОМАРНЫЙ ПЕРЕВОД
# =====================================

def transfer_msg(from_id: int, to_id: int, amount: int) -> tuple:
    """Перевод msg. Атомарная транзакция. Возвращает (успех, сообщение)."""
    if from_id == to_id:
        return False, "Нельзя переводить самому себе"
    if amount <= 0:
        return False, "Сумма должна быть положительной"
    if amount > 1_000_000_000:
        return False, "Слишком большая сумма"

    from_married = is_married(from_id)
    to_married = is_married(to_id)

    # Получатель должен существовать
    to_data = get_user(to_id)
    if to_data is None:
        return False, "Получатель не найден"

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    try:
        cur.execute("BEGIN")

        # Списываем у отправителя
        if from_married:
            cur.execute(
                "UPDATE marriages SET balance = balance - ? "
                "WHERE (user1_id = ? OR user2_id = ?) AND balance >= ?",
                (amount, from_id, from_id, amount)
            )
        else:
            cur.execute(
                "UPDATE users SET msg_count = msg_count - ? "
                "WHERE user_id = ? AND msg_count >= ?",
                (amount, from_id, amount)
            )

        if cur.rowcount == 0:
            conn.rollback()
            return False, "Недостаточно msg"

        # Начисляем получателю
        if to_married:
            cur.execute(
                "UPDATE marriages SET balance = balance + ? "
                "WHERE user1_id = ? OR user2_id = ?",
                (amount, to_id, to_id)
            )
            # Если получатель в браке, но marriages-строки нет (race) — 
            # тогда fallback на личный счёт
            if cur.rowcount == 0:
                cur.execute(
                    "UPDATE users SET msg_count = msg_count + ? WHERE user_id = ?",
                    (amount, to_id)
                )
        else:
            cur.execute(
                "UPDATE users SET msg_count = msg_count + ? WHERE user_id = ?",
                (amount, to_id)
            )

        # Логируем транзакцию
        cur.execute(
            "INSERT INTO transactions (from_id, to_id, amount, kind, created_at) "
            "VALUES (?, ?, ?, ?, ?)",
            (from_id, to_id, amount, "transfer", datetime.now().isoformat())
        )

        conn.commit()
        return True, "ok"
    except Exception as e:
        conn.rollback()
        print(f"[DB] transfer_msg error: {e}")
        return False, "Ошибка БД"
    finally:
        conn.close()


# =====================================
#  🔧 FIX: АТОМАРНАЯ ПОКУПКА VIP
# =====================================

def buy_vip(user_id: int, weeks: int) -> tuple:
    """Покупка VIP. 1 неделя = 1000 msg. Атомарная."""
    if weeks <= 0:
        return False, "Количество недель должно быть положительным"

    cost = weeks * 1000

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    try:
        cur.execute("BEGIN")

        # Получаем текущий vip_until
        cur.execute("SELECT vip_until FROM users WHERE user_id = ?", (user_id,))
        row = cur.fetchone()
        if not row:
            conn.rollback()
            return False, "Пользователь не найден"

        vip_until = row[0]
        now = datetime.now()

        if vip_until:
            try:
                base = datetime.fromisoformat(vip_until)
                if base < now:
                    base = now
            except ValueError:
                base = now
        else:
            base = now

        new_until = base + timedelta(weeks=weeks)

        # 🔧 Списываем стоимость АТОМАРНО (проверка баланса в SQL)
        if is_married(user_id):
            cur.execute(
                "UPDATE marriages SET balance = balance - ? "
                "WHERE (user1_id = ? OR user2_id = ?) AND balance >= ?",
                (cost, user_id, user_id, cost)
            )
        else:
            cur.execute(
                "UPDATE users SET msg_count = msg_count - ? "
                "WHERE user_id = ? AND msg_count >= ?",
                (cost, user_id, cost)
            )

        if cur.rowcount == 0:
            conn.rollback()
            return False, f"Недостаточно msg (нужно {cost})"

        # Обновляем vip_until
        cur.execute(
            "UPDATE users SET vip_until = ? WHERE user_id = ?",
            (new_until.isoformat(), user_id)
        )

        # Логируем
        cur.execute(
            "INSERT INTO transactions (from_id, to_id, amount, kind, created_at) "
            "VALUES (?, ?, ?, ?, ?)",
            (user_id, user_id, -cost, "buy_vip", now.isoformat())
        )

        conn.commit()
        return True, new_until.isoformat()
    except Exception as e:
        conn.rollback()
        print(f"[DB] buy_vip error: {e}")
        return False, "Ошибка БД"
    finally:
        conn.close()


def is_vip_active(user_id: int) -> bool:
    """Проверяет, активен ли VIP."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT vip_until FROM users WHERE user_id = ?", (user_id,))
    row = cur.fetchone()
    conn.close()
    if not row or not row[0]:
        return False
    try:
        until = datetime.fromisoformat(row[0])
        return until > datetime.now()
    except ValueError:
        return False


# =====================================
#  ВЛАДЕЛЕЦ: УПРАВЛЕНИЕ VIP
# =====================================

def give_vip(user_id: int, weeks: int):
    """Выдаёт VIP на N недель."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT vip_until FROM users WHERE user_id = ?", (user_id,))
    row = cur.fetchone()
    if not row:
        conn.close()
        return None

    vip_until = row[0]
    now = datetime.now()

    if vip_until:
        try:
            base = datetime.fromisoformat(vip_until)
            if base < now:
                base = now
        except ValueError:
            base = now
    else:
        base = now

    new_until = base + timedelta(weeks=weeks)

    cur.execute(
        "UPDATE users SET vip_until = ? WHERE user_id = ?",
        (new_until.isoformat(), user_id)
    )
    conn.commit()
    conn.close()
    return new_until.isoformat()


def give_vip_days(user_id: int, days: int):
    """Выдаёт VIP на N дней."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT vip_until FROM users WHERE user_id = ?", (user_id,))
    row = cur.fetchone()
    if not row:
        conn.close()
        return None

    vip_until = row[0]
    now = datetime.now()

    if vip_until:
        try:
            base = datetime.fromisoformat(vip_until)
            if base < now:
                base = now
        except ValueError:
            base = now
    else:
        base = now

    new_until = base + timedelta(days=days)

    cur.execute(
        "UPDATE users SET vip_until = ? WHERE user_id = ?",
        (new_until.isoformat(), user_id)
    )
    conn.commit()
    conn.close()
    return new_until.isoformat()


def remove_vip(user_id: int):
    """Снимает VIP."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("UPDATE users SET vip_until = NULL WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()


# =====================================
#  DAILY
# =====================================

def get_last_daily(user_id: int):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT last_daily FROM users WHERE user_id = ?", (user_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return None
    return row[0]


# 🔧 FIX: claim_daily — атомарная (last_daily + начисление в одной транзакции)
def claim_daily(user_id: int, amount: int):
    """Клеймит daily и начисляет msg. Атомарная."""
    now_iso = datetime.now().isoformat()

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    try:
        cur.execute("BEGIN")

        # Обновляем last_daily
        cur.execute(
            "UPDATE users SET last_daily = ? WHERE user_id = ?",
            (now_iso, user_id)
        )

        # Начисляем msg (учитывая брак)
        if is_married(user_id):
            cur.execute(
                "UPDATE marriages SET balance = balance + ? "
                "WHERE user1_id = ? OR user2_id = ?",
                (amount, user_id, user_id)
            )
        else:
            cur.execute(
                "UPDATE users SET msg_count = msg_count + ? WHERE user_id = ?",
                (amount, user_id)
            )

        # Логируем
        cur.execute(
            "INSERT INTO transactions (from_id, to_id, amount, kind, created_at) "
            "VALUES (?, ?, ?, ?, ?)",
            (user_id, user_id, amount, "daily", now_iso)
        )

        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"[DB] claim_daily error: {e}")
        conn.close()
        return 0
    finally:
        try:
            conn.close()
        except Exception:
            pass

    return get_balance(user_id)


def get_daily_streak(user_id: int) -> int:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT daily_streak FROM users WHERE user_id = ?", (user_id,))
    row = cur.fetchone()
    conn.close()
    if not row or row[0] is None:
        return 0
    return row[0]


def set_daily_streak(user_id: int, streak: int):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("UPDATE users SET daily_streak = ? WHERE user_id = ?", (streak, user_id))
    conn.commit()
    conn.close()


# =====================================
#  ТОП / РАНГ / ИСТОРИЯ
# =====================================

def get_top(limit: int = 10):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "SELECT user_id, username, full_name, msg_count FROM users "
        "ORDER BY msg_count DESC LIMIT ?",
        (limit,)
    )
    rows = cur.fetchall()
    conn.close()
    return rows


def get_top_bank(limit: int = 10):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "SELECT b.user_id, u.username, u.full_name, b.balance "
        "FROM banks b "
        "LEFT JOIN users u ON u.user_id = b.user_id "
        "WHERE b.balance > 0 "
        "ORDER BY b.balance DESC LIMIT ?",
        (limit,)
    )
    rows = cur.fetchall()
    conn.close()
    return rows


def _all_effective_balances() -> dict:
    """Возвращает {user_id: effective_balance} с учётом браков."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT user_id, msg_count FROM users")
    users_rows = cur.fetchall()
    cur.execute("SELECT user1_id, user2_id, balance FROM marriages")
    marry_rows = cur.fetchall()
    conn.close()

    married_ids = set()
    scores = {}

    for u1, u2, bal in marry_rows:
        married_ids.add(u1)
        married_ids.add(u2)
        scores[u1] = bal
        scores[u2] = bal

    for uid, msg in users_rows:
        if uid in married_ids:
            continue
        scores[uid] = msg

    return scores


def get_user_rank(user_id: int) -> int:
    """Возвращает место в топе с учётом браков."""
    my_balance = get_balance(user_id)
    scores = _all_effective_balances()

    higher = sum(1 for b in scores.values() if b > my_balance)
    return higher + 1


def get_history(user_id: int, limit: int = 10):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "SELECT from_id, to_id, amount, kind, created_at FROM transactions "
        "WHERE from_id = ? OR to_id = ? "
        "ORDER BY id DESC LIMIT ?",
        (user_id, user_id, limit)
    )
    rows = cur.fetchall()
    conn.close()
    return rows


# =====================================
#  УРОВНИ
# =====================================

POSITIVE_TIERS = [
    (5,     20,    "🌱 Новичок"),
    (10,    40,    "📚 Знает базу"),
    (20,    80,    "🧠 Знаток"),
    (50,    120,   "💼 Профи"),
    (100,   200,   "🏆 Мастер"),
    (200,   300,   "💎 Эксперт"),
    (500,   500,   "👑 Гуру"),
    (1000,  1000,  "🌟 Легенда"),
    (2000,  2000,  "🔥 Титан"),
    (5000,  5000,  "⚡ Полубог"),
    (10000, 10000, "🌌 Бессмертный"),
]

NEGATIVE_TIERS = [
    (5,     20,    "🍂 Новичок-должник"),
    (10,    40,    "🕳️ Уходит в минус"),
    (20,    80,    "💸 Должник"),
    (50,    120,   "📉 Всё плохо"),
    (100,   200,   "☠️ На дне"),
    (200,   300,   "⛓️ В кабале"),
    (500,   500,   "💀 Банкрот"),
    (1000,  1000,  "🕱 Обречённый"),
    (2000,  2000,  "🌑 Тень"),
    (5000,  5000,  "🕳️ Бездна"),
    (10000, 10000, "⬛ Несуществующий"),
]

MAX_LEVEL = 10000


def _calc_from_tiers(msg_count: int, tiers: list) -> dict:
    remaining = abs(msg_count)
    prev_max = 0

    for max_level, per_level, title in tiers:
        levels_in_tier = max_level - prev_max
        tier_xp = levels_in_tier * per_level

        if remaining < tier_xp:
            level_in_tier = remaining // per_level
            level = prev_max + level_in_tier + 1
            current_progress = remaining % per_level
            return {
                "level": level,
                "title": title,
                "current_progress": current_progress,
                "next_required": per_level,
            }

        remaining -= tier_xp
        prev_max = max_level

    max_lvl, per_lvl, title = tiers[-1]
    return {
        "level": max_lvl,
        "title": title,
        "current_progress": 0,
        "next_required": per_lvl,
    }


def calc_level(msg_count: int) -> dict:
    if msg_count < 0:
        base = _calc_from_tiers(msg_count, NEGATIVE_TIERS)
        base["level"] = -base["level"]
        base["is_negative"] = True
        return base

    if msg_count == 0:
        return {
            "level": 0,
            "title": "⚪ Ноль",
            "current_progress": 0,
            "next_required": 20,
            "is_negative": False,
        }

    base = _calc_from_tiers(msg_count, POSITIVE_TIERS)
    base["is_negative"] = False
    return base


def get_user_level(user_id: int) -> dict:
    balance = get_balance(user_id)
    return calc_level(balance)


# =====================================
#  БАНЫ
# =====================================

def add_ban(user_id: int, reason: str, days: int, banned_by: int):
    now = datetime.now()
    banned_until = None if days == 0 else (now + timedelta(days=days)).isoformat()

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO bans (user_id, reason, banned_at, banned_until, banned_by) "
        "VALUES (?, ?, ?, ?, ?)",
        (user_id, reason, now.isoformat(), banned_until, banned_by)
    )
    conn.commit()
    conn.close()
    return banned_until


def get_active_ban(user_id: int):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "SELECT reason, banned_until, banned_at FROM bans "
        "WHERE user_id = ? ORDER BY id DESC LIMIT 1",
        (user_id,)
    )
    row = cur.fetchone()
    conn.close()

    if not row:
        return None

    reason, banned_until, banned_at = row

    if banned_until is None:
        return (reason, None, banned_at)

    try:
        until_dt = datetime.fromisoformat(banned_until)
    except ValueError:
        return None

    if until_dt > datetime.now():
        return (reason, banned_until, banned_at)

    return None


def remove_ban(user_id: int):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("DELETE FROM bans WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()


def list_bans():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        SELECT b.user_id, b.reason, b.banned_until, b.banned_at, u.username, u.full_name
        FROM bans b
        LEFT JOIN users u ON u.user_id = b.user_id
        WHERE b.id IN (SELECT MAX(id) FROM bans GROUP BY user_id)
        ORDER BY b.id DESC
    """)
    rows = cur.fetchall()
    conn.close()
    return rows


# =====================================
#  БАНК
# =====================================

KRASNOYARSK_TZ = timezone(timedelta(hours=7))


def _now_krasnoyarsk() -> datetime:
    return datetime.now(KRASNOYARSK_TZ).replace(tzinfo=None)


def _hours_since_last_00(last_dt: datetime, now: datetime) -> tuple:
    last_full = last_dt.replace(minute=0, second=0, microsecond=0)
    now_full = now.replace(minute=0, second=0, microsecond=0)

    if now_full < last_full:
        return 0, last_full

    hours = int((now_full - last_full).total_seconds() // 3600)

    if hours == 0:
        return 0, last_full

    return hours, now_full


def bank_ensure(user_id: int):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT user_id FROM banks WHERE user_id = ?", (user_id,))
    if cur.fetchone() is None:
        cur.execute(
            "INSERT INTO banks (user_id, balance, last_interest_at, total_earned) "
            "VALUES (?, 0, ?, 0)",
            (user_id, _now_krasnoyarsk().isoformat())
        )
        conn.commit()
    conn.close()


# 🔧 FIX: _calc_interest всегда обновляет last_interest_at,
#         даже если earned = 0 (иначе маленькие балансы не накопятся никогда)
def _calc_interest(user_id: int) -> int:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "SELECT balance, last_interest_at FROM banks WHERE user_id = ?",
        (user_id,)
    )
    row = cur.fetchone()
    if not row:
        conn.close()
        return 0

    balance, last_at = row
    if not last_at:
        conn.close()
        return 0

    try:
        last_dt = datetime.fromisoformat(last_at)
    except ValueError:
        conn.close()
        return 0

    now = _now_krasnoyarsk()
    hours, last_full = _hours_since_last_00(last_dt, now)

    if hours <= 0:
        conn.close()
        return 0

    vip = is_vip_active(user_id)
    rate = 0.02 if vip else 0.01

    earned = int(balance * rate * hours) if balance > 0 else 0

    # 🔧 FIX: обновляем last_interest_at ВСЕГДА, даже если earned = 0
    cur.execute(
        "UPDATE banks SET balance = balance + ?, "
        "last_interest_at = ?, "
        "total_earned = total_earned + ? "
        "WHERE user_id = ?",
        (earned, last_full.isoformat(), earned, user_id)
    )
    conn.commit()
    conn.close()
    return earned


def bank_get(user_id: int) -> dict:
    bank_ensure(user_id)
    earned = _calc_interest(user_id)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "SELECT balance, last_interest_at, total_earned FROM banks WHERE user_id = ?",
        (user_id,)
    )
    row = cur.fetchone()
    conn.close()

    if not row:
        return {"balance": 0, "last_interest_at": None, "total_earned": 0, "earned_now": 0}

    return {
        "balance": row[0],
        "last_interest_at": row[1],
        "total_earned": row[2],
        "earned_now": earned,
    }


# 🔧 FIX: bank_put атомарный
def bank_put(user_id: int, amount: int) -> tuple:
    if amount <= 0:
        return False, "Сумма должна быть положительной", 0, 0

    bank_ensure(user_id)
    _calc_interest(user_id)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    try:
        cur.execute("BEGIN")

        # Списываем из кошелька атомарно
        if is_married(user_id):
            cur.execute(
                "UPDATE marriages SET balance = balance - ? "
                "WHERE (user1_id = ? OR user2_id = ?) AND balance >= ?",
                (amount, user_id, user_id, amount)
            )
        else:
            cur.execute(
                "UPDATE users SET msg_count = msg_count - ? "
                "WHERE user_id = ? AND msg_count >= ?",
                (amount, user_id, amount)
            )

        if cur.rowcount == 0:
            conn.rollback()
            wallet = get_balance(user_id)
            return False, f"Недостаточно msg в кошельке (у тебя {wallet})", 0, 0

        # Зачисляем в банк
        cur.execute(
            "UPDATE banks SET balance = balance + ? WHERE user_id = ?",
            (amount, user_id)
        )

        cur.execute("SELECT balance FROM banks WHERE user_id = ?", (user_id,))
        new_bank = cur.fetchone()[0]

        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"[DB] bank_put error: {e}")
        conn.close()
        return False, "Ошибка БД", 0, 0
    finally:
        try:
            conn.close()
        except Exception:
            pass

    new_wallet = get_balance(user_id)
    return True, "ok", new_bank, new_wallet


# 🔧 FIX: bank_take атомарный
def bank_take(user_id: int, amount: int) -> tuple:
    if amount <= 0:
        return False, "Сумма должна быть положительной", 0, 0

    bank_ensure(user_id)
    _calc_interest(user_id)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    try:
        cur.execute("BEGIN")

        # Списываем из банка атомарно
        cur.execute(
            "UPDATE banks SET balance = balance - ? "
            "WHERE user_id = ? AND balance >= ?",
            (amount, user_id, amount)
        )

        if cur.rowcount == 0:
            conn.rollback()
            cur.execute("SELECT balance FROM banks WHERE user_id = ?", (user_id,))
            row = cur.fetchone()
            bank_balance = row[0] if row else 0
            conn.close()
            return False, f"В банке только {bank_balance} msg", 0, 0

        # Начисляем в кошелёк
        if is_married(user_id):
            cur.execute(
                "UPDATE marriages SET balance = balance + ? "
                "WHERE user1_id = ? OR user2_id = ?",
                (amount, user_id, user_id)
            )
            if cur.rowcount == 0:
                # Fallback
                cur.execute(
                    "UPDATE users SET msg_count = msg_count + ? WHERE user_id = ?",
                    (amount, user_id)
                )
        else:
            cur.execute(
                "UPDATE users SET msg_count = msg_count + ? WHERE user_id = ?",
                (amount, user_id)
            )

        cur.execute("SELECT balance FROM banks WHERE user_id = ?", (user_id,))
        new_bank = cur.fetchone()[0]

        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"[DB] bank_take error: {e}")
        conn.close()
        return False, "Ошибка БД", 0, 0
    finally:
        try:
            conn.close()
        except Exception:
            pass

    new_wallet = get_balance(user_id)
    return True, "ok", new_bank, new_wallet


# =====================================
#  НИК
# =====================================

def get_nick(user_id: int):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT nick, nick_changed_at FROM users WHERE user_id = ?", (user_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return None, None
    return row[0], row[1]


def set_nick(user_id: int, nick: str):
    now = datetime.now().isoformat()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "UPDATE users SET nick = ?, nick_changed_at = ? WHERE user_id = ?",
        (nick, now, user_id)
    )
    conn.commit()
    conn.close()


# =====================================
#  ТИТУЛ
# =====================================

def get_title(user_id: int):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT custom_title, title_changed_at FROM users WHERE user_id = ?", (user_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return None, None
    return row[0], row[1]


def set_title(user_id: int, title: str):
    now = datetime.now().isoformat()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "UPDATE users SET custom_title = ?, title_changed_at = ? WHERE user_id = ?",
        (title, now, user_id)
    )
    conn.commit()
    conn.close()


def clear_title(user_id: int):
    now = datetime.now().isoformat()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "UPDATE users SET custom_title = NULL, title_changed_at = ? WHERE user_id = ?",
        (now, user_id)
    )
    conn.commit()
    conn.close()


# =====================================
#  ОГРАБЛЕНИЕ
# =====================================

def get_last_rob(user_id: int):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT last_rob FROM users WHERE user_id = ?", (user_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return None
    return row[0]


def set_last_rob(user_id: int):
    now = datetime.now().isoformat()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("UPDATE users SET last_rob = ? WHERE user_id = ?", (now, user_id))
    conn.commit()
    conn.close()


# =====================================
#  ЭФФЕКТЫ (магазин)
# =====================================

def get_shield_until(user_id: int):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT shield_until FROM users WHERE user_id = ?", (user_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return None
    return row[0]


def set_shield_until(user_id: int, iso_until: str):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("UPDATE users SET shield_until = ? WHERE user_id = ?", (iso_until, user_id))
    conn.commit()
    conn.close()


def is_shield_active(user_id: int) -> bool:
    until = get_shield_until(user_id)
    if not until:
        return False
    try:
        return datetime.fromisoformat(until) > datetime.now()
    except ValueError:
        return False


def get_hide_balance_until(user_id: int):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT hide_balance_until FROM users WHERE user_id = ?", (user_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return None
    return row[0]


def set_hide_balance_until(user_id: int, iso_until: str):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "UPDATE users SET hide_balance_until = ? WHERE user_id = ?",
        (iso_until, user_id)
    )
    conn.commit()
    conn.close()


def is_hide_balance_active(user_id: int) -> bool:
    until = get_hide_balance_until(user_id)
    if not until:
        return False
    try:
        return datetime.fromisoformat(until) > datetime.now()
    except ValueError:
        return False


def get_anon_shield_until(user_id: int):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT anon_shield_until FROM users WHERE user_id = ?", (user_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return None
    return row[0]


def set_anon_shield_until(user_id: int, iso_until: str):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "UPDATE users SET anon_shield_until = ? WHERE user_id = ?",
        (iso_until, user_id)
    )
    conn.commit()
    conn.close()


def is_anon_shield_active(user_id: int) -> bool:
    until = get_anon_shield_until(user_id)
    if not until:
        return False
    try:
        return datetime.fromisoformat(until) > datetime.now()
    except ValueError:
        return False


def get_lucky_until(user_id: int):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT lucky_until FROM users WHERE user_id = ?", (user_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return None
    return row[0]


def set_lucky_until(user_id: int, iso_until: str):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "UPDATE users SET lucky_until = ? WHERE user_id = ?",
        (iso_until, user_id)
    )
    conn.commit()
    conn.close()


def is_lucky_active(user_id: int) -> bool:
    until = get_lucky_until(user_id)
    if not until:
        return False
    try:
        return datetime.fromisoformat(until) > datetime.now()
    except ValueError:
        return False


# =====================================
#  АНОНИМКИ
# =====================================

def log_anon(from_id: int, to_id: int, text: str):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO anon_messages (from_id, to_id, text, created_at) "
        "VALUES (?, ?, ?, ?)",
        (from_id, to_id, text, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()


def get_anon_logs(limit: int = 20, to_id: int = None):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    if to_id is not None:
        cur.execute(
            "SELECT from_id, to_id, text, created_at FROM anon_messages "
            "WHERE to_id = ? ORDER BY id DESC LIMIT ?",
            (to_id, limit)
        )
    else:
        cur.execute(
            "SELECT from_id, to_id, text, created_at FROM anon_messages "
            "ORDER BY id DESC LIMIT ?",
            (limit,)
        )
    rows = cur.fetchall()
    conn.close()
    return rows


# =====================================
#  МУТ АНОНИМОК
# =====================================

def add_anon_mute(user_id: int, reason: str, days: int, muted_by: int):
    now = datetime.now()
    muted_until = None if days == 0 else (now + timedelta(days=days)).isoformat()

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO anon_mutes (user_id, reason, muted_at, muted_until, muted_by) "
        "VALUES (?, ?, ?, ?, ?)",
        (user_id, reason, now.isoformat(), muted_until, muted_by)
    )
    conn.commit()
    conn.close()
    return muted_until


def get_active_anon_mute(user_id: int):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "SELECT reason, muted_until, muted_at FROM anon_mutes "
        "WHERE user_id = ? ORDER BY id DESC LIMIT 1",
        (user_id,)
    )
    row = cur.fetchone()
    conn.close()

    if not row:
        return None

    reason, muted_until, muted_at = row

    if muted_until is None:
        return (reason, None, muted_at)

    try:
        until_dt = datetime.fromisoformat(muted_until)
    except ValueError:
        return None

    if until_dt > datetime.now():
        return (reason, muted_until, muted_at)

    return None


def remove_anon_mute(user_id: int):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("DELETE FROM anon_mutes WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()


# =====================================
#  ИНФО О БОТЕ
# =====================================

def get_bot_info(key: str):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT value FROM bot_info WHERE key = ?", (key,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return None
    return row[0]


def set_bot_info(key: str, value: str):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "INSERT OR REPLACE INTO bot_info (key, value) VALUES (?, ?)",
        (key, value)
    )
    conn.commit()
    conn.close()


# =====================================
#  НОВОСТИ РАЗРАБОТКИ (SOON)
# =====================================

def get_bot_soon():
    return get_bot_info("soon")


def set_bot_soon(text: str):
    set_bot_info("soon", text)


def clear_bot_soon():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("DELETE FROM bot_info WHERE key = ?", ("soon",))
    conn.commit()
    conn.close()


# =====================================
#  СТАТИСТИКА БОТА
# =====================================

# 🔧 FIX: wallet_msg = total_msg - bank_msg (было wallet_msg = total_msg, что неверно)
def get_bot_stats() -> dict:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM users")
    total_users = cur.fetchone()[0]

    cur.execute(
        "SELECT COUNT(*) FROM users WHERE vip_until > ?",
        (datetime.now().isoformat(),)
    )
    vip_users = cur.fetchone()[0]

    cur.execute(
        "SELECT COUNT(DISTINCT user_id) FROM bans "
        "WHERE banned_until IS NULL OR banned_until > ?",
        (datetime.now().isoformat(),)
    )
    banned_users = cur.fetchone()[0]

    cur.execute("SELECT COALESCE(SUM(balance), 0) FROM banks")
    bank_msg = cur.fetchone()[0]

    # 🔧 Правильный подсчёт wallet_msg:
    # = сумма личных балансов у холостых
    # + сумма брачных балансов (один раз на пару, не на каждого супруга)

    # 1) Личные балансы — только у тех, кто НЕ в браке
    cur.execute("""
        SELECT COALESCE(SUM(msg_count), 0) FROM users
        WHERE user_id NOT IN (
            SELECT user1_id FROM marriages
            UNION
            SELECT user2_id FROM marriages
        )
    """)
    singles_msg = cur.fetchone()[0]

    # 2) Брачные балансы — сумма balance из marriages (уже один раз на пару)
    cur.execute("SELECT COALESCE(SUM(balance), 0) FROM marriages")
    marriages_msg = cur.fetchone()[0]

    wallet_msg = singles_msg + marriages_msg
    total_msg = wallet_msg + bank_msg

    # Средний баланс — по пользователям (в браке считаем одну пару как 1 юзера? или как 2?)
    # Оставим как раньше — по scores, но только для топа
    avg_balance = (wallet_msg // total_users) if total_users > 0 else 0

    # Топ-1 — по эффективному балансу (для брака — сумма пары)
    scores = _all_effective_balances()
    top1_name = "—"
    top1_balance = 0
    if scores:
        top1_uid = max(scores, key=scores.get)
        top1_balance = scores[top1_uid]
        data = get_user(top1_uid)
        if data:
            uname, fname = data[1], data[2]
            top1_name = f"@{uname}" if uname else (fname or f"ID:{top1_uid}")
        else:
            top1_name = f"ID:{top1_uid}"

    return {
        "total_users": total_users,
        "vip_users": vip_users,
        "banned_users": banned_users,
        "total_msg": total_msg,
        "bank_msg": bank_msg,
        "wallet_msg": wallet_msg,
        "avg_balance": avg_balance,
        "top1_name": top1_name,
        "top1_balance": top1_balance,
    }


# =====================================
#  МАГАЗИН
# =====================================

def add_shop_item(name: str, price: int, effect_type: str,
                  duration_hours: int, limit_total: int,
                  limit_per_user: int, visible_to: str) -> int:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO shop_items "
        "(name, price, effect_type, duration_hours, limit_total, limit_per_user, visible_to, sold_count, created_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, 0, ?)",
        (name, price, effect_type, duration_hours,
         limit_total, limit_per_user, visible_to,
         datetime.now().isoformat())
    )
    conn.commit()
    item_id = cur.lastrowid
    conn.close()
    return item_id


def remove_shop_item(item_id: int) -> bool:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("DELETE FROM shop_items WHERE id = ?", (item_id,))
    changed = cur.rowcount > 0
    conn.commit()
    conn.close()
    return changed


def get_shop_item(item_id: int):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "SELECT id, name, price, effect_type, duration_hours, "
        "limit_total, limit_per_user, visible_to, sold_count "
        "FROM shop_items WHERE id = ?",
        (item_id,)
    )
    row = cur.fetchone()
    conn.close()
    return row


def get_shop_items(visible_filter: str = None):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    if visible_filter is None:
        cur.execute(
            "SELECT id, name, price, effect_type, duration_hours, "
            "limit_total, limit_per_user, visible_to, sold_count "
            "FROM shop_items ORDER BY id"
        )
    else:
        if visible_filter == "owner":
            allowed = ("all", "vip", "owner")
        elif visible_filter == "vip":
            allowed = ("all", "vip")
        else:
            allowed = ("all",)

        placeholders = ",".join("?" * len(allowed))
        cur.execute(
            f"SELECT id, name, price, effect_type, duration_hours, "
            f"limit_total, limit_per_user, visible_to, sold_count "
            f"FROM shop_items WHERE visible_to IN ({placeholders}) ORDER BY id",
            allowed
        )

    rows = cur.fetchall()
    conn.close()
    return rows


def get_user_purchases_count(user_id: int, item_id: int) -> int:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "SELECT COUNT(*) FROM user_purchases WHERE user_id = ? AND item_id = ?",
        (user_id, item_id)
    )
    count = cur.fetchone()[0]
    conn.close()
    return count


def log_purchase(user_id: int, item_id: int):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO user_purchases (user_id, item_id, purchased_at) VALUES (?, ?, ?)",
        (user_id, item_id, datetime.now().isoformat())
    )
    cur.execute("UPDATE shop_items SET sold_count = sold_count + 1 WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()


# =====================================
#  УРОВНИ ДОСТУПА
# =====================================

VALID_LEVELS = ("econom", "moder", "senior", "owner")


def add_access(user_id: int, level: str, added_by: int) -> bool:
    if level not in VALID_LEVELS:
        return False

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO access_levels (user_id, level, added_by, added_at) "
            "VALUES (?, ?, ?, ?)",
            (user_id, level, added_by, datetime.now().isoformat())
        )
        conn.commit()
        result = True
    except sqlite3.IntegrityError:
        result = False
    conn.close()
    return result


def remove_access(user_id: int, level: str) -> bool:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "DELETE FROM access_levels WHERE user_id = ? AND level = ?",
        (user_id, level)
    )
    changed = cur.rowcount > 0
    conn.commit()
    conn.close()
    return changed


def get_user_levels(user_id: int) -> list:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "SELECT level FROM access_levels WHERE user_id = ?",
        (user_id,)
    )
    rows = cur.fetchall()
    conn.close()
    return [row[0] for row in rows]


def has_access(user_id: int, level: str) -> bool:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "SELECT 1 FROM access_levels WHERE user_id = ? AND level = ? LIMIT 1",
        (user_id, level)
    )
    row = cur.fetchone()
    conn.close()
    return row is not None


def get_all_admins() -> dict:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT user_id, level FROM access_levels")
    rows = cur.fetchall()
    conn.close()

    result = {"econom": [], "moder": [], "senior": [], "owner": []}
    for user_id, level in rows:
        if level in result:
            result[level].append(user_id)
    return result


# =====================================
#  ПРЕДУПРЕЖДЕНИЯ (WARN)
# =====================================

WARN_LIMIT = 3
WARN_BAN_DAYS = 7


def add_warn(user_id: int, reason: str, warned_by: int) -> int:
    now = datetime.now().isoformat()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO warns (user_id, reason, warned_by, warned_at) "
        "VALUES (?, ?, ?, ?)",
        (user_id, reason, warned_by, now)
    )
    conn.commit()
    warn_id = cur.lastrowid
    conn.close()
    return warn_id


def get_user_warns(user_id: int):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "SELECT id, reason, warned_by, warned_at FROM warns "
        "WHERE user_id = ? ORDER BY id",
        (user_id,)
    )
    rows = cur.fetchall()
    conn.close()
    return rows


def get_warn_count(user_id: int) -> int:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM warns WHERE user_id = ?", (user_id,))
    count = cur.fetchone()[0]
    conn.close()
    return count


def remove_warn(warn_id: int) -> bool:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("DELETE FROM warns WHERE id = ?", (warn_id,))
    changed = cur.rowcount > 0
    conn.commit()
    conn.close()
    return changed


def clear_warns(user_id: int):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("DELETE FROM warns WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()


def get_all_warned():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        SELECT user_id, COUNT(*) as cnt
        FROM warns
        GROUP BY user_id
        ORDER BY cnt DESC, user_id
    """)
    rows = cur.fetchall()
    conn.close()

    result = []
    for user_id, count in rows:
        warns = get_user_warns(user_id)
        result.append((user_id, count, warns))
    return result


# =====================================
#  КЕЙСЫ
# =====================================

def get_case_cooldown(user_id: int, case_type: str):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "SELECT last_open FROM case_cooldowns WHERE user_id = ? AND case_type = ?",
        (user_id, case_type)
    )
    row = cur.fetchone()
    conn.close()
    if not row:
        return None
    return row[0]


def set_case_cooldown(user_id: int, case_type: str):
    now = datetime.now().isoformat()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "INSERT OR REPLACE INTO case_cooldowns (user_id, case_type, last_open) "
        "VALUES (?, ?, ?)",
        (user_id, case_type, now)
    )
    conn.commit()
    conn.close()


def clear_case_cooldown(user_id: int, case_type: str):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "DELETE FROM case_cooldowns WHERE user_id = ? AND case_type = ?",
        (user_id, case_type)
    )
    conn.commit()
    conn.close()


# =====================================
#  БРАК
# =====================================

def get_marriage(user_id: int):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "SELECT id, user1_id, user2_id, balance FROM marriages "
        "WHERE user1_id = ? OR user2_id = ?",
        (user_id, user_id)
    )
    row = cur.fetchone()
    conn.close()
    return row


def get_spouse(user_id: int):
    row = get_marriage(user_id)
    if not row:
        return None
    _, u1, u2, _ = row
    return u2 if u1 == user_id else u1


def is_married(user_id: int) -> bool:
    return get_spouse(user_id) is not None


def get_marriage_balance(user_id: int) -> int:
    row = get_marriage(user_id)
    if not row:
        return 0
    return row[3]


def change_marriage_balance(user_id: int, amount: int) -> int:
    row = get_marriage(user_id)
    if not row:
        return 0

    marriage_id = row[0]

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "UPDATE marriages SET balance = balance + ? WHERE id = ?",
        (amount, marriage_id)
    )
    conn.commit()
    cur.execute("SELECT balance FROM marriages WHERE id = ?", (marriage_id,))
    new_balance = cur.fetchone()[0]
    conn.close()
    return new_balance


# 🔧 FIX: marry_users — проверка fetchone() is not None
def marry_users(user1_id: int, user2_id: int) -> bool:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute(
        "SELECT 1 FROM marriages WHERE user1_id IN (?, ?) OR user2_id IN (?, ?)",
        (user1_id, user2_id, user1_id, user2_id)
    )
    if cur.fetchone():
        conn.close()
        return False

    cur.execute("SELECT msg_count FROM users WHERE user_id = ?", (user1_id,))
    row1 = cur.fetchone()
    if not row1:
        conn.close()
        return False
    bal1 = row1[0]

    cur.execute("SELECT msg_count FROM users WHERE user_id = ?", (user2_id,))
    row2 = cur.fetchone()
    if not row2:
        conn.close()
        return False
    bal2 = row2[0]

    total = bal1 + bal2

    cur.execute("UPDATE users SET msg_count = 0 WHERE user_id = ?", (user1_id,))
    cur.execute("UPDATE users SET msg_count = 0 WHERE user_id = ?", (user2_id,))

    cur.execute(
        "INSERT INTO marriages (user1_id, user2_id, married_at, balance) "
        "VALUES (?, ?, ?, ?)",
        (user1_id, user2_id, datetime.now().isoformat(), total)
    )

    conn.commit()
    conn.close()
    return True


# 🔧 FIX: divorce_users — не теряет 1 msg, ДОБАВЛЯЕТ к личному балансу
def divorce_users(user_id: int) -> tuple:
    row = get_marriage(user_id)
    if not row:
        return False, 0, 0

    marriage_id, u1, u2, balance = row

    # Не теряем копейку при нечётной сумме
    half1 = balance // 2
    half2 = balance - half1  # остаток отдаём второму

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("DELETE FROM marriages WHERE id = ?", (marriage_id,))
    # ДОБАВЛЯЕМ к существующему балансу (а не перезаписываем)
    cur.execute("UPDATE users SET msg_count = msg_count + ? WHERE user_id = ?", (half1, u1))
    cur.execute("UPDATE users SET msg_count = msg_count + ? WHERE user_id = ?", (half2, u2))

    conn.commit()
    conn.close()

    return True, half1, half2


def get_marriage_date(user_id: int):
    row = get_marriage(user_id)
    if not row:
        return None

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT married_at FROM marriages WHERE id = ?", (row[0],))
    r = cur.fetchone()
    conn.close()
    return r[0] if r else None


# =====================================
#  ОБЁРТКИ БАЛАНСА (учитывают брак)
# =====================================

def get_balance(user_id: int) -> int:
    """Возвращает баланс: общий (если в браке) или личный."""
    if is_married(user_id):
        return get_marriage_balance(user_id)

    data = get_user(user_id)
    return data[3] if data else 0


def add_balance(user_id: int, amount: int) -> int:
    """Меняет баланс: общий (если в браке) или личный."""
    if is_married(user_id):
        return change_marriage_balance(user_id, amount)

    return change_balance(user_id, amount)


def add_msg_auto(user_id: int, amount: int):
    """Начисляет msg в общий счёт (если женат) или личный."""
    if is_married(user_id):
        change_marriage_balance(user_id, amount)
    else:
        add_msg(user_id, amount)


# 🔧 FIX: set_balance — учитывает брак через обёртку
def set_balance(user_id: int, amount: int):
    """Устанавливает баланс точно (для админов). Учитывает брак."""
    if is_married(user_id):
        row = get_marriage(user_id)
        if not row:
            return
        marriage_id = row[0]
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("UPDATE marriages SET balance = ? WHERE id = ?", (amount, marriage_id))
        conn.commit()
        conn.close()
    else:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("UPDATE users SET msg_count = ? WHERE user_id = ?", (amount, user_id))
        conn.commit()
        conn.close()


# =====================================
#  РАССЫЛКА
# =====================================

def get_all_user_ids() -> list:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT user_id FROM users")
    rows = cur.fetchall()
    conn.close()
    return [row[0] for row in rows]


# =====================================
#  ДУЭЛИ
# =====================================

def duel_create(challenger_id: int, opponent_id: int, bet: int) -> int:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO duels (challenger_id, opponent_id, bet, status, created_at) "
        "VALUES (?, ?, ?, 'pending', ?)",
        (challenger_id, opponent_id, bet, datetime.now().isoformat())
    )
    conn.commit()
    duel_id = cur.lastrowid
    conn.close()
    return duel_id


def duel_get(duel_id: int):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "SELECT id, challenger_id, opponent_id, bet, status, "
        "hp1, hp2, am1, am2, turn, message_id, chat_id, "
        "move1, move2, used_heal1, used_heal2, created_at "
        "FROM duels WHERE id = ?",
        (duel_id,)
    )
    row = cur.fetchone()
    conn.close()
    return row


def duel_update(duel_id: int, **fields):
    if not fields:
        return
    keys = ", ".join(f"{k} = ?" for k in fields.keys())
    values = list(fields.values()) + [duel_id]

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(f"UPDATE duels SET {keys} WHERE id = ?", values)
    conn.commit()
    conn.close()


def duel_delete(duel_id: int):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("DELETE FROM duels WHERE id = ?", (duel_id,))
    conn.commit()
    conn.close()


def get_user_duel(user_id: int):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "SELECT id, challenger_id, opponent_id, bet, status, "
        "hp1, hp2, am1, am2, turn, message_id, chat_id, "
        "move1, move2, used_heal1, used_heal2, created_at "
        "FROM duels "
        "WHERE (challenger_id = ? OR opponent_id = ?) "
        "AND status IN ('pending', 'active') "
        "ORDER BY id DESC LIMIT 1",
        (user_id, user_id)
    )
    row = cur.fetchone()
    conn.close()
    return row


# =====================================
#  USER_STATS
# =====================================

def ensure_user_stats(user_id: int):
    """Создаёт запись статистики, если её нет."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT user_id FROM user_stats WHERE user_id = ?", (user_id,))
    if cur.fetchone() is None:
        cur.execute(
            "INSERT INTO user_stats (user_id) VALUES (?)",
            (user_id,)
        )
        conn.commit()
    conn.close()


def get_user_stats(user_id: int) -> dict:
    """Возвращает статистику юзера."""
    ensure_user_stats(user_id)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "SELECT total_messages, total_casino_games, total_casino_losses, "
        "total_robs, total_gifts_sent, total_duel_wins "
        "FROM user_stats WHERE user_id = ?",
        (user_id,)
    )
    row = cur.fetchone()
    conn.close()

    if not row:
        return {
            "total_messages": 0,
            "total_casino_games": 0,
            "total_casino_losses": 0,
            "total_robs": 0,
            "total_gifts_sent": 0,
            "total_duel_wins": 0,
        }

    return {
        "total_messages": row[0],
        "total_casino_games": row[1],
        "total_casino_losses": row[2],
        "total_robs": row[3],
        "total_gifts_sent": row[4],
        "total_duel_wins": row[5],
    }


def increment_stat(user_id: int, stat: str, amount: int = 1):
    """Увеличивает счётчик статистики."""
    valid_stats = (
        "total_messages", "total_casino_games", "total_casino_losses",
        "total_robs", "total_gifts_sent", "total_duel_wins"
    )
    if stat not in valid_stats:
        return

    ensure_user_stats(user_id)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        f"UPDATE user_stats SET {stat} = {stat} + ? WHERE user_id = ?",
        (amount, user_id)
    )
    conn.commit()
    conn.close()


# =====================================
#  ДОСТИЖЕНИЯ
# =====================================

ACHIEVEMENTS = [
    ("first_step",      "🎯", "Первый шаг",      "total_messages",     1),
    ("talker",          "💬", "Болтун",          "total_messages",     1000),
    ("super_talker",    "💬", "Супер болтун",    "total_messages",     5000),
    ("mega_talker",     "💬", "Мега болтун",     "total_messages",     10000),
    ("saver",           "💰", "Накопитель",      "msg_count",          100000),
    ("millionaire",     "💎", "Миллионер",       "msg_count",          1000000),
    ("multimillionaire","🏆", "Мультимиллионер", "msg_count",          10000000),
    ("gangster",        "🥷", "Гангстер",        "total_robs",         10),
    ("generous",        "💸", "Щедрый",          "total_gifts_sent",   50000),
    ("rockefeller",     "🏦", "Рокфеллер",       "bank_balance",       1000000),
    ("worker",          "🔥", "Трудяга",         "daily_streak",       30),
    ("top1",            "👑", "Топ-1",           "top_rank",           1),
    ("gambler",         "🎰", "Азартный",        "total_casino_games", 100),
    ("ludoman",         "🎲", "Лудоман",         "total_casino_losses",1000000),
    ("family_man",      "💍", "Семьянин",        "marriage_days",      30),
    ("gladiator",       "⚔️", "Гладиатор",       "total_duel_wins",    10),
]


def get_achievement_info(ach_id: str):
    """Возвращает (emoji, название, тип, порог) или None."""
    for aid, emoji, name, field, threshold in ACHIEVEMENTS:
        if aid == ach_id:
            return emoji, name, field, threshold
    return None


def unlock_achievement(user_id: int, ach_id: str) -> bool:
    """Открывает достижение. Возвращает True, если открыто впервые."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO achievements (user_id, ach_id, unlocked_at) "
            "VALUES (?, ?, ?)",
            (user_id, ach_id, datetime.now().isoformat())
        )
        conn.commit()
        result = True
    except sqlite3.IntegrityError:
        result = False
    conn.close()
    return result


def get_user_achievements(user_id: int) -> list:
    """Возвращает список ID открытых достижений."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "SELECT ach_id FROM achievements WHERE user_id = ?",
        (user_id,)
    )
    rows = cur.fetchall()
    conn.close()
    return [row[0] for row in rows]


def get_achievement_count(user_id: int) -> int:
    """Количество открытых достижений."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "SELECT COUNT(*) FROM achievements WHERE user_id = ?",
        (user_id,)
    )
    count = cur.fetchone()[0]
    conn.close()
    return count


def get_next_achievement(user_id: int):
    """Возвращает следующее незакрытое достижение."""
    unlocked = set(get_user_achievements(user_id))

    for ach_id, emoji, name, field, threshold in ACHIEVEMENTS:
        if ach_id in unlocked:
            continue

        current = _get_achievement_value(user_id, field)
        percent = min(100, int((current / threshold) * 100)) if threshold > 0 else 0

        return (ach_id, emoji, name, current, threshold, percent)

    return None


def _get_achievement_value(user_id: int, field: str) -> int:
    """Возвращает значение поля для проверки достижения."""
    if field == "msg_count":
        return get_balance(user_id)

    if field == "bank_balance":
        bank_info = bank_get(user_id)
        return bank_info["balance"]

    if field == "daily_streak":
        return get_daily_streak(user_id)

    if field == "top_rank":
        rank = get_user_rank(user_id)
        return 1 if rank == 1 else 999999

    if field == "marriage_days":
        if not is_married(user_id):
            return 0
        married_at = get_marriage_date(user_id)
        if not married_at:
            return 0
        try:
            m_dt = datetime.fromisoformat(married_at)
            diff = datetime.now() - m_dt
            return diff.days
        except ValueError:
            return 0

    stats = get_user_stats(user_id)
    return stats.get(field, 0)


def check_all_achievements(user_id: int) -> list:
    """Проверяет все достижения и открывает новые."""
    unlocked = set(get_user_achievements(user_id))
    new_achievements = []

    for ach_id, emoji, name, field, threshold in ACHIEVEMENTS:
        if ach_id in unlocked:
            continue

        current = _get_achievement_value(user_id, field)

        if current >= threshold:
            if unlock_achievement(user_id, ach_id):
                new_achievements.append((ach_id, emoji, name))

    return new_achievements
    
    
def get_stale_duels(timeout_seconds: int) -> list:
    """Возвращает дуэли, где время последнего действия истекло.

    Точнее: где turn (чей ход) не менялся > timeout_seconds.
    Но у нас нет поля 'last_turn_at'. Добавим простую логику:
    все активные дуэли старше timeout_seconds от created_at.
    """
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    threshold = (datetime.now() - timedelta(seconds=timeout_seconds)).isoformat()
    cur.execute(
        "SELECT id FROM duels "
        "WHERE status = 'active' AND created_at < ?",
        (threshold,)
    )
    rows = cur.fetchall()
    conn.close()
    return [row[0] for row in rows]


def get_pending_duels_older_than(timeout_seconds: int) -> list:
    """Дуэли в pending старше timeout — их нужно удалить (приглашение истекло)."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    threshold = (datetime.now() - timedelta(seconds=timeout_seconds)).isoformat()
    cur.execute(
        "SELECT id FROM duels "
        "WHERE status = 'pending' AND created_at < ?",
        (threshold,)
    )
    rows = cur.fetchall()
    conn.close()
    return [row[0] for row in rows]
    
# =====================================
#  КРЕСТИКИ-НОЛИКИ
# =====================================

def ttt_create(player_x_id: int, player_o_id: int, bet: int) -> int:
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