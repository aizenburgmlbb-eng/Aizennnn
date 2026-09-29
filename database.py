import sqlite3

DB_PATH = "users.db"


def _conn():
    return sqlite3.connect(DB_PATH)


def init_db():
    with _conn() as c:
        c.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id      INTEGER PRIMARY KEY,
                username     TEXT,
                display_name TEXT,
                msg_count    INTEGER DEFAULT 0
            )
        """)
        c.execute("CREATE INDEX IF NOT EXISTS idx_msg_count ON users(msg_count DESC)")


def ensure_user(user_id, username=None):
    """Создаёт запись, если нет. Обновляет username, если изменился."""
    with _conn() as c:
        c.execute("""
            INSERT INTO users (user_id, username, msg_count)
            VALUES (?, ?, 0)
            ON CONFLICT(user_id) DO UPDATE SET
                username = COALESCE(excluded.username, users.username)
        """, (user_id, username))


def set_display_name(user_id, name, username=None):
    """Создаёт запись при необходимости и ставит display_name."""
    ensure_user(user_id, username)
    with _conn() as c:
        c.execute("UPDATE users SET display_name = ? WHERE user_id = ?", (name, user_id))


def delete_display_name(user_id):
    """Убирает display_name. Возвращает True, если пользователь был."""
    with _conn() as c:
        cur = c.execute("SELECT 1 FROM users WHERE user_id = ?", (user_id,))
        if not cur.fetchone():
            return False
        c.execute("UPDATE users SET display_name = NULL WHERE user_id = ?", (user_id,))
        return True


def increment_msg(user_id, username=None):
    """+1 к msg_count. Создаёт запись, если нет."""
    ensure_user(user_id, username)
    with _conn() as c:
        c.execute("UPDATE users SET msg_count = msg_count + 1 WHERE user_id = ?", (user_id,))


def add_msgs(user_id, n):
    """+n к msg_count. Возвращает False, если юзера нет."""
    with _conn() as c:
        cur = c.execute("SELECT 1 FROM users WHERE user_id = ?", (user_id,))
        if not cur.fetchone():
            return False
        c.execute("UPDATE users SET msg_count = msg_count + ? WHERE user_id = ?", (n, user_id))
        return True


def remove_msgs(user_id, n):
    """-n к msg_count (мин. 0). Возвращает False, если юзера нет."""
    with _conn() as c:
        cur = c.execute("SELECT msg_count FROM users WHERE user_id = ?", (user_id,))
        row = cur.fetchone()
        if not row:
            return False
        new_val = max(0, row[0] - n)
        c.execute("UPDATE users SET msg_count = ? WHERE user_id = ?", (new_val, user_id))
        return True


def get_user(user_id):
    """Возвращает dict или None."""
    with _conn() as c:
        cur = c.execute("""
            SELECT user_id, username, display_name, msg_count
            FROM users WHERE user_id = ?
        """, (user_id,))
        row = cur.fetchone()
        if not row:
            return None
        return {
            "user_id": row[0],
            "username": row[1],
            "display_name": row[2],
            "msg_count": row[3],
        }


def get_top(limit=10):
    """Топ по msg_count. Только с msg_count > 0."""
    with _conn() as c:
        cur = c.execute("""
            SELECT user_id, username, display_name, msg_count
            FROM users
            WHERE msg_count > 0
            ORDER BY msg_count DESC
            LIMIT ?
        """, (limit,))
        return [
            {"user_id": r[0], "username": r[1], "display_name": r[2], "msg_count": r[3]}
            for r in cur.fetchall()
        ]