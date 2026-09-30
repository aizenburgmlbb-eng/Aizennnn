import sqlite3
from datetime import datetime, timedelta

DB_PATH = "users.db"


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
            last_activity TEXT
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

    # Миграция старых баз
    cur.execute("PRAGMA table_info(users)")
    existing_cols = {row[1] for row in cur.fetchall()}
    needed = {
        "username":      "TEXT",
        "full_name":     "TEXT",
        "msg_count":     "INTEGER DEFAULT 0",
        "vip_until":     "TEXT",
        "last_daily":    "TEXT",
        "last_activity": "TEXT",
    }
    for col, col_type in needed.items():
        if col not in existing_cols:
            cur.execute(f"ALTER TABLE users ADD COLUMN {col} {col_type}")
            print(f"[DB] Добавлена колонка: {col}")

    conn.commit()
    conn.close()


def ensure_user(user) -> dict:
    """Создаёт пользователя, если его нет. Обновляет имя/юзернейм. Возвращает dict."""
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
    new_balance = cur.fetchone()[0]
    conn.close()
    return new_balance


def add_msg(user_id: int, amount: int):
    """Просто начислить msg (без транзакции)."""
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


def transfer_msg(from_id: int, to_id: int, amount: int) -> tuple[bool, str]:
    """Перевод msg. Возвращает (успех, сообщение)."""
    if from_id == to_id:
        return False, "Нельзя переводить самому себе"
    if amount <= 0:
        return False, "Сумма должна быть положительной"

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT msg_count FROM users WHERE user_id = ?", (from_id,))
    row = cur.fetchone()
    if row is None:
        conn.close()
        return False, "Отправитель не найден"
    if row[0] < amount:
        conn.close()
        return False, "Недостаточно msg"

    cur.execute("SELECT user_id FROM users WHERE user_id = ?", (to_id,))
    if cur.fetchone() is None:
        conn.close()
        return False, "Получатель не найден"

    cur.execute("UPDATE users SET msg_count = msg_count - ? WHERE user_id = ?", (amount, from_id))
    cur.execute("UPDATE users SET msg_count = msg_count + ? WHERE user_id = ?", (amount, to_id))
    cur.execute(
        "INSERT INTO transactions (from_id, to_id, amount, kind, created_at) VALUES (?, ?, ?, ?, ?)",
        (from_id, to_id, amount, "transfer", datetime.now().isoformat())
    )
    conn.commit()
    conn.close()
    return True, "ok"


def buy_vip(user_id: int, weeks: int) -> tuple[bool, str]:
    """Покупка VIP. 1 неделя = 1000 msg."""
    if weeks <= 0:
        return False, "Количество недель должно быть положительным"

    cost = weeks * 1000

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT msg_count, vip_until FROM users WHERE user_id = ?", (user_id,))
    row = cur.fetchone()
    if row is None:
        conn.close()
        return False, "Пользователь не найден"

    balance, vip_until = row
    if balance < cost:
        conn.close()
        return False, f"Недостаточно msg (нужно {cost}, у тебя {balance})"

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
        "UPDATE users SET msg_count = msg_count - ?, vip_until = ? WHERE user_id = ?",
        (cost, new_until.isoformat(), user_id)
    )
    cur.execute(
        "INSERT INTO transactions (from_id, to_id, amount, kind, created_at) VALUES (?, ?, ?, ?, ?)",
        (user_id, user_id, -cost, "buy_vip", now.isoformat())
    )
    conn.commit()
    conn.close()
    return True, new_until.isoformat()


def is_vip_active(user_id: int) -> bool:
    """Проверяет, активен ли VIP у пользователя."""
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


def get_last_daily(user_id: int):
    """Возвращает дату последнего /daily или None."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT last_daily FROM users WHERE user_id = ?", (user_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return None
    return row[0]


def claim_daily(user_id: int, amount: int):
    """Записывает дату /daily и начисляет msg. Возвращает новый баланс."""
    now_iso = datetime.now().isoformat()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "UPDATE users SET msg_count = msg_count + ?, last_daily = ? WHERE user_id = ?",
        (amount, now_iso, user_id)
    )
    cur.execute(
        "INSERT INTO transactions (from_id, to_id, amount, kind, created_at) "
        "VALUES (?, ?, ?, ?, ?)",
        (user_id, user_id, amount, "daily", now_iso)
    )
    conn.commit()
    cur.execute("SELECT msg_count FROM users WHERE user_id = ?", (user_id,))
    new_balance = cur.fetchone()[0]
    conn.close()
    return new_balance

def get_top(limit: int = 10):
    """Возвращает список топ-N юзеров: (user_id, username, full_name, msg_count)."""
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


def get_user_rank(user_id: int) -> int:
    """Возвращает место пользователя в топе (1 — самый богатый)."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT msg_count FROM users WHERE user_id = ?", (user_id,))
    row = cur.fetchone()
    if row is None:
        conn.close()
        return 0
    balance = row[0]
    cur.execute("SELECT COUNT(*) FROM users WHERE msg_count > ?", (balance,))
    higher = cur.fetchone()[0]
    conn.close()
    return higher + 1


def get_history(user_id: int, limit: int = 10):
    """Возвращает последние транзакции юзера:
    (from_id, to_id, amount, kind, created_at).
    """
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

