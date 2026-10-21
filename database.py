import sqlite3
from datetime import datetime, timedelta, timezone

DB_PATH = "users.db"
BOT_TREASURY_ID = 8572154161  # @Aminka_Ai_bot — казна бота

# =====================================
#  ИНИЦИАЛИЗАЦИЯ БД
# =====================================

def init_db():
    """Создаёт таблицы и добавляет недостающие колонки."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
    	CREATE TABLE IF NOT EXISTS promocodes (
     	   id            INTEGER PRIMARY KEY AUTOINCREMENT,
     	   code          TEXT UNIQUE,
      	  reward_type   TEXT,
     	   reward_value  INTEGER,
      	  max_uses      INTEGER DEFAULT 0,
       	 used_count    INTEGER DEFAULT 0,
       	 created_at    TEXT
    )
""")

    cur.execute("""
    CREATE TABLE IF NOT EXISTS ball_cooldowns (
        user_id     INTEGER PRIMARY KEY,
        last_asked  TEXT
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
    CREATE TABLE IF NOT EXISTS user_pets (
        id                INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id           INTEGER,
        pet_type          TEXT,
        pet_name          TEXT UNIQUE,
        mood              INTEGER DEFAULT 50,
        fed_at            TEXT,
        created_at        TEXT,
        is_active         INTEGER DEFAULT 0,
        death_notified    INTEGER DEFAULT 0
    )
""")

    cur.execute("""
    CREATE TABLE IF NOT EXISTS pet_action_cooldowns (
        pet_id    INTEGER,
        action    TEXT,
        last_at   TEXT,
        PRIMARY KEY (pet_id, action)
    )
""")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS promo_activations (
   	     id           INTEGER PRIMARY KEY AUTOINCREMENT,
    	    user_id      INTEGER,
   	     code         TEXT,
   	     activated_at TEXT,
   	     UNIQUE(user_id, code)
    )
""")
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
    
    cur.execute("PRAGMA table_info(payments)")
    payments_cols = {row[1] for row in cur.fetchall()}
    if "payment_code" not in payments_cols:
    	cur.execute("ALTER TABLE payments ADD COLUMN payment_code TEXT")
    	print("[DB] Добавлена колонка: payments.payment_code")

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
    
    cur.execute("""
 	   CREATE TABLE IF NOT EXISTS referrals (
       	 id            INTEGER PRIMARY KEY AUTOINCREMENT,
   	     referrer_id   INTEGER,
    	    referral_id   INTEGER UNIQUE,
    	    joined_at     TEXT,
   	     msg_count     INTEGER DEFAULT 0,
    	    rewarded      INTEGER DEFAULT 0,
    	    rewarded_at   TEXT
    )
""")

    # Миграция users
    cur.execute("PRAGMA table_info(users)")
    existing_cols = {row[1] for row in cur.fetchall()}
    needed = {
        "username":           "TEXT",
        "full_name":          "TEXT",
        "msg_count":          "INTEGER DEFAULT 0",
        "last_divorce_at":    "TEXT",
        "vip_until":          "TEXT",
        "last_daily":         "TEXT",
        "last_activity":      "TEXT",
        "reputation":        "INTEGER DEFAULT 0",
        "last_rep_at":       "TEXT",
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
        "referrer_id":        "INTEGER",
    }
    for col, col_type in needed.items():
        if col not in existing_cols:
            cur.execute(f"ALTER TABLE users ADD COLUMN {col} {col_type}")
            print(f"[DB] Добавлена колонка: users.{col}")
            
	# Миграция marriages — last_case_at
    cur.execute("PRAGMA table_info(marriages)")
    marry_cols = {row[1] for row in cur.fetchall()}
    if "last_case_at" not in marry_cols:
        cur.execute("ALTER TABLE marriages ADD COLUMN last_case_at TEXT")
        print("[DB] Добавлена колонка: marriages.last_case_at")
    
    # Миграция marriages — добавить balance
    cur.execute("PRAGMA table_info(marriages)")
    marry_cols = {row[1] for row in cur.fetchall()}
    if "balance" not in marry_cols:
        cur.execute("ALTER TABLE marriages ADD COLUMN balance INTEGER DEFAULT 0")
        print("[DB] Добавлена колонка: marriages.balance")

    conn.commit()
    conn.close()


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

def get_next_payment_number() -> int:
    """
    Возвращает следующий глобальный номер платежа.
    Счётчик хранится в bot_info, не сбрасывается.
    """
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    try:
        cur.execute("BEGIN")

        cur.execute("SELECT value FROM bot_info WHERE key = 'payment_counter'")
        row = cur.fetchone()

        if row:
            current = int(row[0])
        else:
            current = 0

        new_value = current + 1

        cur.execute(
            "INSERT OR REPLACE INTO bot_info (key, value) VALUES (?, ?)",
            ("payment_counter", str(new_value))
        )

        conn.commit()
        return new_value
    except Exception as e:
        conn.rollback()
        print(f"[DB] get_next_payment_number error: {e}")
        return 0
    finally:
        conn.close()


def save_payment_code(charge_id: str, code: str):
    """Сохраняет код платежа в БД по telegram_charge_id."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "UPDATE payments SET payment_code = ? WHERE telegram_charge_id = ?",
        (code, charge_id)
    )
    conn.commit()
    conn.close()


def find_payment_by_code(code: str):
    """Ищет платёж по коду. Возвращает строку или None."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "SELECT user_id, stars_amount, msg_amount, telegram_charge_id, created_at "
        "FROM payments WHERE payment_code = ?",
        (code,)
    )
    row = cur.fetchone()
    conn.close()
    return row

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

    cost = weeks * 2000

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
        "WHERE user_id != ? "
        "ORDER BY msg_count DESC LIMIT ?",
        (BOT_TREASURY_ID, limit)
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
        "WHERE b.balance > 0 AND b.user_id != ? "
        "ORDER BY b.balance DESC LIMIT ?",
        (BOT_TREASURY_ID, limit)
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
        # Пропускаем пары с казной
        if BOT_TREASURY_ID in (u1, u2):
            continue
        married_ids.add(u1)
        married_ids.add(u2)
        scores[u1] = bal
        scores[u2] = bal

    for uid, msg in users_rows:
        if uid in married_ids:
            continue
        if uid == BOT_TREASURY_ID:
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
    (5,         20,      "🥉 Стажёр"),
    (10,        30,      "🌱 Новичок"),
    (20,        50,      "📚 Знает базу"),
    (35,        80,      "📖 Ученик"),
    (60,        120,     "🧠 Знаток"),
    (100,       180,     "💼 Профи"),
    (160,       250,     "💡 Эксперт"),
    (250,       350,     "🎯 Специалист"),
    (400,       500,     "🏆 Мастер"),
    (650,       700,     "⭐ Мэтр"),
    (1000,      1000,    "💎 Ас"),
    (1500,      1400,    "👑 Гуру"),
    (2300,      2000,    "🥇 Виртуоз"),
    (3500,      2800,    "🌟 Легенда"),
    (5000,      4000,    "🔥 Титан"),
    (7500,      5500,    "⚡ Полубог"),
    (10000,     7500,    "🌌 Бессмертный"),
    (15000,     10000,   "💫 Ветеран"),
    (22000,     14000,   "🌠 Архимаг"),
    (32000,     20000,   "🌀 Демиург"),
    (45000,     28000,   "🎆 Божество"),
    (65000,     40000,   "♾️ Абсолют"),
    (90000,     55000,   "🛸 Сверхновая"),
    (130000,    75000,   "🌌 Вечность"),
    (180000,    100000,  "🏛️ Творец"),
    (250000,    140000,  "🔮 Оракул"),
    (350000,    200000,  "🌞 Солнце"),
    (500000,    280000,  "🌟 Супернова"),
    (700000,    400000,  "🪐 Галактика"),
    (1000000,   600000,  "👁️ Всёвидящий"),
]

NEGATIVE_TIERS = [
    (5,         20,      "🍂 Первый минус"),
    (10,        30,      "🌧️ Должок"),
    (20,        50,      "🕳️ Уходит в минус"),
    (35,        80,      "📉 Плохо дело"),
    (60,        120,     "💸 Должник"),
    (100,       180,     "🥀 Всё хуже"),
    (160,       250,     "⚠️ Опасно"),
    (250,       350,     "🕱 На грани"),
    (400,       500,     "☠️ На дне"),
    (650,       700,     "⛓️ В кабале"),
    (1000,      1000,    "🩸 Кровный долг"),
    (1500,      1400,    "💀 Банкрот"),
    (2300,      2000,    "🪦 Похоронен"),
    (3500,      2800,    "🕷️ Забвение"),
    (5000,      4000,    "🌑 Тень"),
    (7500,      5500,    "🕳️ Бездна"),
    (10000,     7500,    "⬛ Несуществующий"),
    (15000,     10000,   "🕱 Обречённый"),
    (22000,     14000,   "💀 Мертвец"),
    (32000,     20000,   "⚰️ Погребённый"),
    (45000,     28000,   "🌀 Ничто"),
    (65000,     40000,   "❌ Отрицание"),
    (90000,     55000,   "🩻 Разложение"),
    (130000,    75000,   "🕯️ Угасший"),
    (180000,    100000,  "⚱️ Прах"),
    (250000,    140000,  "🪦 Забвение"),
    (350000,    200000,  "💀 Вечное проклятие"),
    (500000,    280000,  "🌑 Тьма"),
    (700000,    400000,  "🕳️ Бездна бездн"),
    (1000000,   600000,  "⚫ Абсолютное ничто"),
]

MAX_LEVEL = 1_000_000


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

    # Правильный подсчёт wallet_msg:
    # = сумма личных балансов у холостых
    # + сумма брачных балансов (один раз на пару, не на каждого супруга)
    cur.execute("""
        SELECT COALESCE(SUM(msg_count), 0) FROM users
        WHERE user_id NOT IN (
            SELECT user1_id FROM marriages
            UNION
            SELECT user2_id FROM marriages
        )
    """)
    singles_msg = cur.fetchone()[0]

    cur.execute("SELECT COALESCE(SUM(balance), 0) FROM marriages")
    marriages_msg = cur.fetchone()[0]

    wallet_msg = singles_msg + marriages_msg
    total_msg = wallet_msg + bank_msg

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


def marry_users(user1_id: int, user2_id: int) -> tuple:
    """
    Создаёт брак. Проверяет кулдаун 7 дней после развода.
    Возвращает (ok: bool, error: str).
    """
    if user1_id == user2_id:
        return False, "Нельзя жениться на себе"

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Уже в браке?
    cur.execute(
        "SELECT 1 FROM marriages WHERE user1_id IN (?, ?) OR user2_id IN (?, ?)",
        (user1_id, user2_id, user1_id, user2_id)
    )
    if cur.fetchone():
        conn.close()
        return False, "Один из вас уже в браке"

    # Кулдаун после развода
    cur.execute(
        "SELECT user_id, last_divorce_at FROM users WHERE user_id IN (?, ?)",
        (user1_id, user2_id)
    )
    rows = cur.fetchall()
    for uid, last_div in rows:
        if last_div:
            try:
                last_dt = datetime.fromisoformat(last_div)
                elapsed = datetime.now() - last_dt
                if elapsed < timedelta(days=7):
                    remaining = timedelta(days=7) - elapsed
                    d = remaining.days
                    h = remaining.seconds // 3600
                    conn.close()
                    return False, f"⏳ Кулдаун после развода: {d} дн. {h} ч"
            except ValueError:
                pass

    # Балансы
    cur.execute("SELECT msg_count FROM users WHERE user_id = ?", (user1_id,))
    row1 = cur.fetchone()
    if not row1:
        conn.close()
        return False, "Пользователь не найден"

    cur.execute("SELECT msg_count FROM users WHERE user_id = ?", (user2_id,))
    row2 = cur.fetchone()
    if not row2:
        conn.close()
        return False, "Пользователь не найден"

    total = row1[0] + row2[0]

    cur.execute("UPDATE users SET msg_count = 0 WHERE user_id = ?", (user1_id,))
    cur.execute("UPDATE users SET msg_count = 0 WHERE user_id = ?", (user2_id,))

    cur.execute(
        "INSERT INTO marriages (user1_id, user2_id, married_at, balance) "
        "VALUES (?, ?, ?, ?)",
        (user1_id, user2_id, datetime.now().isoformat(), total)
    )

    conn.commit()
    conn.close()
    return True, "ok"


def divorce_users(user_id: int) -> tuple:
    """
    Развод. 10% сгорает в казну, 90% делится пополам.
    Обоим ставится кулдаун на брак (last_divorce_at).
    Возвращает (ok, half1, half2, penalty).
    """
    row = get_marriage(user_id)
    if not row:
        return False, 0, 0, 0

    marriage_id, u1, u2, balance = row

    # Штраф 10%
    penalty = balance * 10 // 100
    remainder = balance - penalty

    # Делим пополам (остаток от нечётной — второму)
    half1 = remainder // 2
    half2 = remainder - half1

    now_iso = datetime.now().isoformat()

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("DELETE FROM marriages WHERE id = ?", (marriage_id,))
    cur.execute("UPDATE users SET msg_count = msg_count + ? WHERE user_id = ?", (half1, u1))
    cur.execute("UPDATE users SET msg_count = msg_count + ? WHERE user_id = ?", (half2, u2))

    # Кулдаун обоим
    cur.execute(
        "UPDATE users SET last_divorce_at = ? WHERE user_id IN (?, ?)",
        (now_iso, u1, u2)
    )

    conn.commit()
    conn.close()

    # Штраф → в казну
    if penalty > 0:
        add_balance(BOT_TREASURY_ID, penalty)
        log_transaction(u1, BOT_TREASURY_ID, penalty, "divorce_penalty")

    return True, half1, half2, penalty


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


# =====================================
#  WATCHDOG: ДУЭЛИ
# =====================================

def get_stale_duels(timeout_seconds: int) -> list:
    """Возвращает дуэли, где время последнего действия истекло."""
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


# =====================================
#  РЕФЕРАЛЬНАЯ ПРОГРАММА
# =====================================

def get_referrer(user_id: int):
    """Кто пригласил юзера. None если без реферера."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT referrer_id FROM users WHERE user_id = ?", (user_id,))
    row = cur.fetchone()
    conn.close()
    if not row or row[0] is None:
        return None
    return row[0]


def set_referrer(referral_id: int, referrer_id: int) -> bool:
    """Записывает реферера. Только если у referral_id ещё нет реферера."""
    if referral_id == referrer_id:
        return False

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Проверяем, что у referral_id нет реферера
    cur.execute("SELECT referrer_id FROM users WHERE user_id = ?", (referral_id,))
    row = cur.fetchone()
    if not row or row[0] is not None:
        conn.close()
        return False

    # Проверяем, что referrer_id не забанен навсегда
    # (антифрод — если реферер забанен, не засчитываем)

    now = datetime.now().isoformat()

    cur.execute(
        "UPDATE users SET referrer_id = ? WHERE user_id = ?",
        (referrer_id, referral_id)
    )
    cur.execute(
        "INSERT OR IGNORE INTO referrals "
        "(referrer_id, referral_id, joined_at, msg_count, rewarded, rewarded_at) "
        "VALUES (?, ?, ?, 0, 0, NULL)",
        (referrer_id, referral_id, now)
    )
    conn.commit()
    conn.close()
    return True


def increment_referral_msg(referral_id: int) -> int:
    """Инкрементит счётчик сообщений реферала. Возвращает новое значение."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "UPDATE referrals SET msg_count = msg_count + 1 "
        "WHERE referral_id = ? AND rewarded = 0",
        (referral_id,)
    )
    conn.commit()
    cur.execute(
        "SELECT msg_count FROM referrals WHERE referral_id = ?",
        (referral_id,)
    )
    row = cur.fetchone()
    conn.close()
    return row[0] if row else 0


def get_referral(referral_id: int):
    """Возвращает (referrer_id, msg_count, rewarded)."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "SELECT referrer_id, msg_count, rewarded FROM referrals "
        "WHERE referral_id = ?",
        (referral_id,)
    )
    row = cur.fetchone()
    conn.close()
    return row


def count_rewards_24h(referrer_id: int) -> int:
    """Сколько наград получил реферер за последние 24 часа."""
    threshold = (datetime.now() - timedelta(hours=24)).isoformat()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "SELECT COUNT(*) FROM referrals "
        "WHERE referrer_id = ? AND rewarded = 1 "
        "AND rewarded_at > ?",
        (referrer_id, threshold)
    )
    count = cur.fetchone()[0]
    conn.close()
    return count


def mark_referral_rewarded(referral_id: int, reward: bool = True):
    """Отмечает реферала как вознаграждённого (reward=1) или сгоревшего (reward=-1)."""
    now = datetime.now().isoformat()
    value = 1 if reward else -1
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "UPDATE referrals SET rewarded = ?, rewarded_at = ? "
        "WHERE referral_id = ?",
        (value, now, referral_id)
    )
    conn.commit()
    conn.close()


def get_referral_stats(referrer_id: int) -> dict:
    """Статистика реферера для /ref."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Всего приглашено
    cur.execute(
        "SELECT COUNT(*) FROM referrals WHERE referrer_id = ?",
        (referrer_id,)
    )
    total = cur.fetchone()[0]

    # Активных (rewarded = 1)
    cur.execute(
        "SELECT COUNT(*) FROM referrals WHERE referrer_id = ? AND rewarded = 1",
        (referrer_id,)
    )
    active = cur.fetchone()[0]

    # Сгоревших (rewarded = -1)
    cur.execute(
        "SELECT COUNT(*) FROM referrals WHERE referrer_id = ? AND rewarded = -1",
        (referrer_id,)
    )
    burned = cur.fetchone()[0]

    # В ожидании (rewarded = 0)
    cur.execute(
        "SELECT COUNT(*) FROM referrals WHERE referrer_id = ? AND rewarded = 0",
        (referrer_id,)
    )
    pending = cur.fetchone()[0]

    conn.close()

    return {
        "total": total,
        "active": active,
        "burned": burned,
        "pending": pending,
        "earned": active * 2000,
    }

# =====================================
#  УДАЛЕНИЕ АККАУНТА
# =====================================

def delete_account(user_id: int) -> bool:
    """
    Полностью удаляет аккаунт и все связанные данные.
    Возвращает True при успехе.
    """
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    try:
        # 1) Если в браке — разводим (баланс делится пополам)
        marriage = get_marriage(user_id)
        if marriage:
            divorce_users(user_id)

        # 2) Активные TTT-партии — возвращаем ставку сопернику
        cur.execute(
            "SELECT id, player_x_id, player_o_id, bet FROM tictactoe "
            "WHERE (player_x_id = ? OR player_o_id = ?) "
            "AND status = 'active'",
            (user_id, user_id)
        )
        for gid, x_id, o_id, bet in cur.fetchall():
            opponent_id = o_id if x_id == user_id else x_id
            add_balance(opponent_id, bet)  # возвращаем ставку соперника
            log_transaction(opponent_id, user_id, bet, "accdel_ttt_refund")
            cur.execute("DELETE FROM tictactoe WHERE id = ?", (gid,))

        # Pending TTT — просто удаляем
        cur.execute(
            "DELETE FROM tictactoe WHERE (player_x_id = ? OR player_o_id = ?)",
            (user_id, user_id)
        )

        # 3) Активные дуэли — возвращаем ставку сопернику
        cur.execute(
            "SELECT id, challenger_id, opponent_id, bet FROM duels "
            "WHERE (challenger_id = ? OR opponent_id = ?) "
            "AND status IN ('pending', 'active')",
            (user_id, user_id)
        )
        for did, ch_id, op_id, bet in cur.fetchall():
            opponent_id = op_id if ch_id == user_id else ch_id
            add_balance(opponent_id, bet)
            log_transaction(opponent_id, user_id, bet, "accdel_duel_refund")
            cur.execute("DELETE FROM duels WHERE id = ?", (did,))

        # 4) Удаляем все записи по user_id
        tables_by_user = [
            "bans",
            "warns",
            "banks",
            "anon_mutes",
            "user_purchases",
            "access_levels",
            "case_cooldowns",
            "achievements",
            "user_stats",
            "payments",
        ]
        for table in tables_by_user:
            cur.execute(f"DELETE FROM {table} WHERE user_id = ?", (user_id,))

        # 5) anon_messages — где from_id или to_id
        cur.execute(
            "DELETE FROM anon_messages WHERE from_id = ? OR to_id = ?",
            (user_id, user_id)
        )

        # 6) transactions — где from_id или to_id
        cur.execute(
            "DELETE FROM transactions WHERE from_id = ? OR to_id = ?",
            (user_id, user_id)
        )

        # 7) referrals — где referrer_id или referral_id
        cur.execute(
            "DELETE FROM referrals WHERE referrer_id = ? OR referral_id = ?",
            (user_id, user_id)
        )

        # 8) Снимаем referrer_id у тех, кого этот юзер пригласил
        cur.execute(
            "UPDATE users SET referrer_id = NULL WHERE referrer_id = ?",
            (user_id,)
        )

        # 9) Сама запись users — в самом конце
        cur.execute("DELETE FROM users WHERE user_id = ?", (user_id,))

        conn.commit()
        return True

    except Exception as e:
        conn.rollback()
        print(f"[DB] delete_account error: {e}")
        return False
    finally:
        conn.close()

# =====================================
#  ПРОМОКОДЫ
# =====================================

def promo_create(code: str, reward_type: str, reward_value: int, max_uses: int = 0) -> bool:
    """Создаёт промокод. reward_type: 'msg' или 'vip'."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO promocodes (code, reward_type, reward_value, max_uses, used_count, created_at) "
            "VALUES (?, ?, ?, ?, 0, ?)",
            (code.upper(), reward_type, reward_value, max_uses, datetime.now().isoformat())
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def promo_get(code: str):
    """Возвращает строку промокода или None."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "SELECT id, code, reward_type, reward_value, max_uses, used_count "
        "FROM promocodes WHERE code = ?",
        (code.upper(),)
    )
    row = cur.fetchone()
    conn.close()
    return row


def promo_activate(user_id: int, code: str) -> tuple:
    """Активирует промокод. Возвращает (ok, message, reward_type, reward_value)."""
    code = code.upper()
    promo = promo_get(code)

    if not promo:
        return False, "Промокод не найден", None, None

    p_id, p_code, p_type, p_value, p_max, p_used = promo

    if p_max > 0 and p_used >= p_max:
        return False, "Промокод использован максимальное число раз", None, None

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "SELECT 1 FROM promo_activations WHERE user_id = ? AND code = ?",
        (user_id, code)
    )
    if cur.fetchone():
        conn.close()
        return False, "Ты уже активировал этот промокод", None, None

    try:
        cur.execute("BEGIN")
        cur.execute(
            "INSERT INTO promo_activations (user_id, code, activated_at) "
            "VALUES (?, ?, ?)",
            (user_id, code, datetime.now().isoformat())
        )
        cur.execute(
            "UPDATE promocodes SET used_count = used_count + 1 WHERE code = ?",
            (code,)
        )
        conn.commit()
        return True, "ok", p_type, p_value
    except Exception as e:
        conn.rollback()
        print(f"[PROMO] Ошибка: {e}")
        return False, "Ошибка БД", None, None
    finally:
        conn.close()


def promo_delete(code: str) -> bool:
    """Удаляет промокод."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("DELETE FROM promocodes WHERE code = ?", (code.upper(),))
    changed = cur.rowcount > 0
    conn.commit()
    conn.close()
    return changed


def promo_list():
    """Список всех промокодов."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "SELECT code, reward_type, reward_value, max_uses, used_count, created_at "
        "FROM promocodes ORDER BY id DESC"
    )
    rows = cur.fetchall()
    conn.close()
    return rows


# =====================================
#  РЕПУТАЦИЯ
# =====================================

def get_reputation(user_id: int) -> int:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT reputation FROM users WHERE user_id = ?", (user_id,))
    row = cur.fetchone()
    conn.close()
    return row[0] if row and row[0] is not None else 0


def get_last_rep(user_id: int):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT last_rep_at FROM users WHERE user_id = ?", (user_id,))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else None


def set_last_rep(user_id: int):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "UPDATE users SET last_rep_at = ? WHERE user_id = ?",
        (datetime.now().isoformat(), user_id)
    )
    conn.commit()
    conn.close()


def change_reputation(user_id: int, amount: int) -> int:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "UPDATE users SET reputation = reputation + ? WHERE user_id = ?",
        (amount, user_id)
    )
    conn.commit()
    cur.execute("SELECT reputation FROM users WHERE user_id = ?", (user_id,))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else 0

# =====================================
#  ТОП ПО STREAK
# =====================================
def get_top_streak(limit: int = 15):
    """Возвращает топ по streak (только streak > 0, без казны)."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        SELECT user_id, daily_streak FROM users
        WHERE daily_streak > 0 AND user_id != ?
        ORDER BY daily_streak DESC LIMIT ?
    """, (BOT_TREASURY_ID, limit))
    rows = cur.fetchall()
    conn.close()
    return rows

# =====================================
#  ИСТОРИЯ ПО КАТЕГОРИЯМ
# =====================================

def get_history_by_kinds(user_id: int, kinds: list, limit: int = 10, offset: int = 0):
    """Возвращает транзакции по списку типов."""
    if not kinds:
        return []

    placeholders = ",".join("?" * len(kinds))
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        f"SELECT from_id, to_id, amount, kind, created_at FROM transactions "
        f"WHERE (from_id = ? OR to_id = ?) "
        f"AND kind IN ({placeholders}) "
        f"ORDER BY id DESC LIMIT ? OFFSET ?",
        (user_id, user_id, *kinds, limit, offset)
    )
    rows = cur.fetchall()
    conn.close()
    return rows


def get_history_count_by_kinds(user_id: int, kinds: list) -> int:
    """Возвращает количество транзакций по типам."""
    if not kinds:
        return 0

    placeholders = ",".join("?" * len(kinds))
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        f"SELECT COUNT(*) FROM transactions "
        f"WHERE (from_id = ? OR to_id = ?) "
        f"AND kind IN ({placeholders})",
        (user_id, user_id, *kinds)
    )
    count = cur.fetchone()[0]
    conn.close()
    return count


def get_history_summary_24h(user_id: int) -> dict:
    """Возвращает итоги за 24 часа: приход, расход, чистая."""
    threshold = (datetime.now() - timedelta(hours=24)).isoformat()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "SELECT amount FROM transactions "
        "WHERE (from_id = ? OR to_id = ?) AND created_at > ?",
        (user_id, user_id, threshold)
    )
    rows = cur.fetchall()
    conn.close()

    income = 0
    expense = 0
    for (amount,) in rows:
        if amount > 0:
            income += amount
        elif amount < 0:
            expense += abs(amount)

    return {
        "income": income,
        "expense": expense,
        "net": income - expense,
    }

# =====================================
#  МАГИЧЕСКИЙ ШАР (/ball)
# =====================================

def get_ball_cooldown(user_id: int):
    """Возвращает ISO-строку последнего вопроса или None."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT last_asked FROM ball_cooldowns WHERE user_id = ?", (user_id,))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else None


def set_ball_cooldown(user_id: int):
    """Записывает текущее время как момент последнего вопроса."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "INSERT OR REPLACE INTO ball_cooldowns (user_id, last_asked) VALUES (?, ?)",
        (user_id, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()

# =====================================
#  ПИТОМЦЫ
# =====================================

PET_TYPES = {
    # обычный кейс
    "cat":       ("🐱", "Кот",      "common"),
    "dog":       ("🐶", "Собака",   "common"),
    "snake":     ("🐍", "Змея",     "common"),
    "hamster":   ("🐹", "Хомяк",    "common"),
    # редкий кейс
    "mouse":     ("🐭", "Мышь",     "rare"),
    "rabbit":    ("🐰", "Заяц",     "rare"),
    "turtle":    ("🐢", "Черепаха", "rare"),
    "fish":      ("🐟", "Рыбка",    "rare"),
    "bear":      ("🐻", "Медведь",  "rare"),
    "fox":       ("🦊", "Лиса",     "rare"),
}

PET_ACTION_COOLDOWN = timedelta(hours=1)
PET_FEED_COOLDOWN = timedelta(hours=12)
PET_DEATH_TIME = timedelta(hours=36)
PET_FEED_PRICE = 500
PET_MOOD_DECAY_PER_HOUR = 20
PET_MOOD_MAX = 100
PET_NAME_MAX_LEN = 15
PET_RENAME_PRICE = 1000


def pet_is_name_taken(name: str) -> bool:
    """Проверяет, занято ли имя (регистр не важен)."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "SELECT 1 FROM user_pets WHERE LOWER(pet_name) = LOWER(?) LIMIT 1",
        (name.strip(),)
    )
    row = cur.fetchone()
    conn.close()
    return row is not None


def pet_add(user_id: int, pet_type: str, pet_name: str) -> int:
    """
    Добавляет питомца. Возвращает pet_id или 0 при ошибке.
    Первый питомец автоматически становится активным.
    """
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    try:
        # Есть ли уже питомцы?
        cur.execute("SELECT COUNT(*) FROM user_pets WHERE user_id = ?", (user_id,))
        count = cur.fetchone()[0]
        is_active = 1 if count == 0 else 0

        now = datetime.now().isoformat()
        cur.execute(
            "INSERT INTO user_pets "
            "(user_id, pet_type, pet_name, mood, fed_at, created_at, is_active, death_notified) "
            "VALUES (?, ?, ?, 100, ?, ?, ?, 0)",
            (user_id, pet_type, pet_name.strip(), now, now, is_active)
        )
        conn.commit()
        return cur.lastrowid
    except sqlite3.IntegrityError:
        return 0
    except Exception as e:
        print(f"[DB] pet_add error: {e}")
        return 0
    finally:
        conn.close()


def pet_get_by_user(user_id: int) -> list:
    """Все питомцы юзера."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "SELECT id, user_id, pet_type, pet_name, mood, fed_at, created_at, is_active, death_notified "
        "FROM user_pets WHERE user_id = ? ORDER BY is_active DESC, id",
        (user_id,)
    )
    rows = cur.fetchall()
    conn.close()
    return rows


def pet_get_by_id(pet_id: int):
    """Один питомец по ID."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "SELECT id, user_id, pet_type, pet_name, mood, fed_at, created_at, is_active, death_notified "
        "FROM user_pets WHERE id = ?",
        (pet_id,)
    )
    row = cur.fetchone()
    conn.close()
    return row


def pet_get_active(user_id: int):
    """Активный питомец юзера."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "SELECT id, user_id, pet_type, pet_name, mood, fed_at, created_at, is_active, death_notified "
        "FROM user_pets WHERE user_id = ? AND is_active = 1 LIMIT 1",
        (user_id,)
    )
    row = cur.fetchone()
    conn.close()
    return row


def pet_set_active(user_id: int, pet_id: int):
    """Делает питомца активным (снимает флаг у остальных)."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("UPDATE user_pets SET is_active = 0 WHERE user_id = ?", (user_id,))
    cur.execute(
        "UPDATE user_pets SET is_active = 1 WHERE id = ? AND user_id = ?",
        (pet_id, user_id)
    )
    conn.commit()
    conn.close()


def pet_count(user_id: int) -> int:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM user_pets WHERE user_id = ?", (user_id,))
    count = cur.fetchone()[0]
    conn.close()
    return count


def pet_rename(pet_id: int, new_name: str) -> bool:
    """Меняет имя. Возвращает True при успехе."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    try:
        cur.execute(
            "UPDATE user_pets SET pet_name = ? WHERE id = ?",
            (new_name.strip(), pet_id)
        )
        conn.commit()
        return cur.rowcount > 0
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def pet_feed(pet_id: int):
    """Обновляет время кормления."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "UPDATE user_pets SET fed_at = ?, death_notified = 0 WHERE id = ?",
        (datetime.now().isoformat(), pet_id)
    )
    conn.commit()
    conn.close()


def pet_delete(pet_id: int):
    """Удаляет питомца."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("DELETE FROM user_pets WHERE id = ?", (pet_id,))
    cur.execute("DELETE FROM pet_action_cooldowns WHERE pet_id = ?", (pet_id,))
    conn.commit()
    conn.close()


def pet_update_mood(pet_id: int, mood: int):
    """Устанавливает настроение (0-100)."""
    if mood < 0:
        mood = 0
    if mood > PET_MOOD_MAX:
        mood = PET_MOOD_MAX

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("UPDATE user_pets SET mood = ? WHERE id = ?", (mood, pet_id))
    conn.commit()
    conn.close()


def pet_set_death_notified(pet_id: int):
    """Помечает, что уведомление о смерти отправлено."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("UPDATE user_pets SET death_notified = 1 WHERE id = ?", (pet_id,))
    conn.commit()
    conn.close()


def pet_action_get_cooldown(pet_id: int, action: str):
    """Возвращает ISO-строку последнего действия или None."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "SELECT last_at FROM pet_action_cooldowns WHERE pet_id = ? AND action = ?",
        (pet_id, action)
    )
    row = cur.fetchone()
    conn.close()
    return row[0] if row else None


def pet_action_set_cooldown(pet_id: int, action: str):
    """Ставит кулдаун на действие."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "INSERT OR REPLACE INTO pet_action_cooldowns (pet_id, action, last_at) "
        "VALUES (?, ?, ?)",
        (pet_id, action, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()

def pet_get_status(pet_id: int) -> dict:
    """
    Возвращает статус питомца:
    - fed_at (ISO)
    - hours_left_until_hungry: часов до голода (0 = голоден)
    - hours_left_until_death: часов до смерти (0 = пора умирать)
    - is_hungry: bool
    - is_dying: bool (осталось <1ч до смерти)
    - hours_since_fed: сколько прошло
    """
    pet = pet_get_by_id(pet_id)
    if not pet:
        return None

    fed_at = pet[5]
    if not fed_at:
        return {
            "fed_at": None,
            "hours_left_until_hungry": 0,
            "hours_left_until_death": 0,
            "is_hungry": True,
            "is_dying": True,
            "hours_since_fed": 999,
        }

    try:
        fed_dt = datetime.fromisoformat(fed_at)
    except ValueError:
        return None

    now = datetime.now()
    elapsed = now - fed_dt
    elapsed_hours = elapsed.total_seconds() / 3600

    hours_until_hungry = max(0, 12 - elapsed_hours)
    hours_until_death = max(0, 36 - elapsed_hours)

    return {
        "fed_at": fed_at,
        "hours_left_until_hungry": hours_until_hungry,
        "hours_left_until_death": hours_until_death,
        "is_hungry": elapsed_hours >= 12,
        "is_dying": 0 < hours_until_death <= 1,
        "hours_since_fed": elapsed_hours,
    }

# =====================================
#  АДМИН: УПРАВЛЕНИЕ БАНКОМ ЮЗЕРА
# =====================================

def bank_admin_add(user_id: int, amount: int) -> int:
    """
    Админ: добавить msg в банк (из воздуха).
    Возвращает новый баланс банка.
    """
    if amount <= 0:
        return 0

    bank_ensure(user_id)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    try:
        cur.execute(
            "UPDATE banks SET balance = balance + ? WHERE user_id = ?",
            (amount, user_id)
        )
        conn.commit()

        cur.execute("SELECT balance FROM banks WHERE user_id = ?", (user_id,))
        row = cur.fetchone()
        return row[0] if row else amount
    except Exception as e:
        conn.rollback()
        print(f"[DB] bank_admin_add error: {e}")
        return 0
    finally:
        conn.close()


def bank_admin_remove(user_id: int, amount: int) -> int:
    """
    Админ: снять msg из банка (в никуда).
    Возвращает новый баланс банка.
    """
    if amount <= 0:
        return 0

    bank_ensure(user_id)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    try:
        cur.execute(
            "UPDATE banks SET balance = MAX(0, balance - ?) WHERE user_id = ?",
            (amount, user_id)
        )
        conn.commit()

        cur.execute("SELECT balance FROM banks WHERE user_id = ?", (user_id,))
        row = cur.fetchone()
        return row[0] if row else 0
    except Exception as e:
        conn.rollback()
        print(f"[DB] bank_admin_remove error: {e}")
        return 0
    finally:
        conn.close()

# =====================================
#  МАССОВЫЙ СБРОС MSG (/resetmsg)
# =====================================
def reset_get_targets() -> list:
    """
    Возвращает список целей для сброса.
    Каждый элемент:
        {
            "is_couple": bool,
            "user_ids": [int, ...],   # 1 или 2
            "total": int,             # кошелёк + банк (сумма пары для брака)
        }
    Пропускает пары-дубликаты (берёт только первого супруга).
    Пропускает казну бота.
    """
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # 1) Все браки
    cur.execute("SELECT user1_id, user2_id, balance FROM marriages")
    marriages = cur.fetchall()

    married_users = set()
    marriage_map = {}
    for u1, u2, bal in marriages:
        married_users.add(u1)
        married_users.add(u2)
        marriage_map[u1] = (u2, bal)
        marriage_map[u2] = (u1, bal)

    # 2) Все банки
    cur.execute("SELECT user_id, balance FROM banks")
    bank_map = {uid: bal for uid, bal in cur.fetchall()}

    # 3) Все холостые (без казны)
    cur.execute(
        "SELECT user_id, msg_count FROM users "
        "WHERE user_id != ? AND user_id NOT IN ("
        "  SELECT user1_id FROM marriages "
        "  UNION SELECT user2_id FROM marriages"
        ")",
        (BOT_TREASURY_ID,)
    )
    singles = cur.fetchall()

    conn.close()

    targets = []
    seen_pairs = set()

    # ─── Пары ───
    for uid in married_users:
        if uid == BOT_TREASURY_ID:
            continue
        spouse_id, common_balance = marriage_map[uid]
        if spouse_id == BOT_TREASURY_ID:
            continue

        pair_key = tuple(sorted([uid, spouse_id]))
        if pair_key in seen_pairs:
            continue
        seen_pairs.add(pair_key)

        total = (
            common_balance
            + bank_map.get(uid, 0)
            + bank_map.get(spouse_id, 0)
        )

        if total <= 0:
            continue

        targets.append({
            "is_couple": True,
            "user_ids": [pair_key[0], pair_key[1]],
            "total": total,
        })

    # ─── Холостые ───
    for uid, msg_count in singles:
        total = msg_count + bank_map.get(uid, 0)
        if total <= 0:
            continue
        targets.append({
            "is_couple": False,
            "user_ids": [uid],
            "total": total,
        })

    return targets


def reset_apply_target(target: dict) -> dict:
    """
    Применяет сброс к одной цели (юзер или пара).
    Возвращает:
        {
            "ok": bool,
            "user_ids": [...],
            "old_total": int,
            "new_balance": int,
            "removed": int,
        }
    Логика:
      1. Банк(и) → в общий котёл (кошелёк / marriages.balance)
      2. Котёл делим на 10
      3. Остаток → кошелёк / marriages.balance, банк(и) = 0
    """
    user_ids = target["user_ids"]
    is_couple = target["is_couple"]

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    try:
        cur.execute("BEGIN")

        if is_couple:
            u1, u2 = user_ids

            # Текущий общий счёт
            cur.execute(
                "SELECT id, balance FROM marriages "
                "WHERE (user1_id = ? AND user2_id = ?) "
                "   OR (user1_id = ? AND user2_id = ?)",
                (u1, u2, u2, u1)
            )
            row = cur.fetchone()
            if not row:
                conn.rollback()
                return {"ok": False, "user_ids": user_ids,
                        "old_total": 0, "new_balance": 0, "removed": 0}

            marriage_id, common_balance = row

            # Банки обоих
            cur.execute(
                "SELECT user_id, balance FROM banks WHERE user_id IN (?, ?)",
                (u1, u2)
            )
            banks = cur.fetchall()
            bank_total = sum(b for _, b in banks)

            old_total = common_balance + bank_total

            # Обнуляем банки
            if banks:
                cur.execute(
                    "UPDATE banks SET balance = 0 WHERE user_id IN (?, ?)",
                    (u1, u2)
                )

            # Новый баланс = 10%
            new_balance = old_total // 10
            removed = old_total - new_balance

            cur.execute(
                "UPDATE marriages SET balance = ? WHERE id = ?",
                (new_balance, marriage_id)
            )

        else:
            uid = user_ids[0]

            # Кошелёк
            cur.execute("SELECT msg_count FROM users WHERE user_id = ?", (uid,))
            row = cur.fetchone()
            wallet = row[0] if row else 0

            # Банк
            cur.execute("SELECT balance FROM banks WHERE user_id = ?", (uid,))
            row = cur.fetchone()
            bank = row[0] if row else 0

            old_total = wallet + bank

            # Обнуляем банк
            if bank > 0:
                cur.execute(
                    "UPDATE banks SET balance = 0 WHERE user_id = ?",
                    (uid,)
                )

            new_balance = old_total // 10
            removed = old_total - new_balance

            cur.execute(
                "UPDATE users SET msg_count = ? WHERE user_id = ?",
                (new_balance, uid)
            )

        conn.commit()

        return {
            "ok": True,
            "user_ids": user_ids,
            "old_total": old_total,
            "new_balance": new_balance,
            "removed": removed,
        }

    except Exception as e:
        conn.rollback()
        print(f"[DB] reset_apply_target error: {e}")
        return {"ok": False, "user_ids": user_ids,
                "old_total": 0, "new_balance": 0, "removed": 0}
    finally:
        conn.close()


def reset_get_user_balance(user_id: int) -> int:
    """Возвращает актуальный баланс юзера после сброса (для уведомления)."""
    return get_balance(user_id)

def title_is_taken(title: str, exclude_user_id: int = None) -> bool:
    """
    Проверяет, занят ли титул (регистр не важен).
    exclude_user_id — игнорировать этого юзера (при смене своего же титула).
    """
    if not title:
        return False

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    if exclude_user_id is not None:
        cur.execute(
            "SELECT 1 FROM users "
            "WHERE LOWER(custom_title) = LOWER(?) AND user_id != ? "
            "LIMIT 1",
            (title.strip(), exclude_user_id)
        )
    else:
        cur.execute(
            "SELECT 1 FROM users "
            "WHERE LOWER(custom_title) = LOWER(?) "
            "LIMIT 1",
            (title.strip(),)
        )

    row = cur.fetchone()
    conn.close()
    return row is not None

# =====================================
#  КАЗНА БОТА
# =====================================

def treasury_get_balance() -> int:
    """Возвращает баланс казны бота."""
    data = get_user(BOT_TREASURY_ID)
    return data[3] if data else 0


def treasury_ensure():
    """Создаёт запись казны, если её нет."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT user_id FROM users WHERE user_id = ?", (BOT_TREASURY_ID,))
    if cur.fetchone() is None:
        cur.execute(
            "INSERT INTO users (user_id, username, full_name, msg_count, last_activity) "
            "VALUES (?, ?, ?, 0, ?)",
            (BOT_TREASURY_ID, "Aminka_Ai_bot", "Казна бота", datetime.now().isoformat())
        )
        conn.commit()
        print(f"[DB] Создана казна бота: {BOT_TREASURY_ID}")
    conn.close()


# =====================================
#  СВАДЕБНЫЙ КЕЙС
# =====================================

WEDDING_CASE_COOLDOWN = timedelta(hours=24)


def wedding_case_get_cooldown(user_id: int):
    """Возвращает ISO-строку последнего открытия кейса парой или None."""
    row = get_marriage(user_id)
    if not row:
        return None

    marriage_id = row[0]

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "SELECT last_case_at FROM marriages WHERE id = ?",
        (marriage_id,)
    )
    r = cur.fetchone()
    conn.close()
    return r[0] if r else None


def wedding_case_set_cooldown(user_id: int):
    """Ставит кулдаун кейса паре."""
    row = get_marriage(user_id)
    if not row:
        return

    marriage_id = row[0]

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "UPDATE marriages SET last_case_at = ? WHERE id = ?",
        (datetime.now().isoformat(), marriage_id)
    )
    conn.commit()
    conn.close()


# =====================================
#  ПОДАРОК ПАРЕ
# =====================================

def gift_to_couple(from_id: int, couple_user_id: int, amount: int) -> tuple:
    """
    Дарит msg паре (в общий счёт).
    from_id — кто дарит
    couple_user_id — любой из супругов пары
    Возвращает (ok: bool, error: str, new_balance: int)
    """
    if amount <= 0:
        return False, "Сумма должна быть положительной", 0

    # Проверка: пара в браке?
    row = get_marriage(couple_user_id)
    if not row:
        return False, "Эта пара больше не вместе", 0

    marriage_id, u1, u2, _ = row

    # Нельзя дарить своей же паре
    if from_id in (u1, u2):
        return False, "Нельзя дарить своей же паре", 0

    # Используем атомарный подход
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    try:
        cur.execute("BEGIN")

        # Списываем у дарителя (учитывая его брак)
        if is_married(from_id):
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
            return False, "Недостаточно msg", 0

        # Зачисляем паре
        cur.execute(
            "UPDATE marriages SET balance = balance + ? WHERE id = ?",
            (amount, marriage_id)
        )

        cur.execute("SELECT balance FROM marriages WHERE id = ?", (marriage_id,))
        new_balance = cur.fetchone()[0]

        # Логируем
        cur.execute(
            "INSERT INTO transactions (from_id, to_id, amount, kind, created_at) "
            "VALUES (?, ?, ?, ?, ?)",
            (from_id, u1, amount, "gift_couple", datetime.now().isoformat())
        )

        conn.commit()
        return True, "ok", new_balance
    except Exception as e:
        conn.rollback()
        print(f"[DB] gift_to_couple error: {e}")
        return False, "Ошибка БД", 0
    finally:
        conn.close()


# =====================================
#  РЕЙТИНГ ПАР
# =====================================

def get_top_couples(limit: int = 10) -> list:
    """Топ пар по общему счёту."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "SELECT user1_id, user2_id, balance FROM marriages "
        "ORDER BY balance DESC LIMIT ?",
        (limit,)
    )
    rows = cur.fetchall()
    conn.close()
    return rows


def get_couple_rank(user_id: int) -> int:
    """Место пары в рейтинге или 0, если не в браке."""
    row = get_marriage(user_id)
    if not row:
        return 0

    my_balance = row[3]

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "SELECT COUNT(*) FROM marriages WHERE balance > ?",
        (my_balance,)
    )
    higher = cur.fetchone()[0]
    conn.close()
    return higher + 1


# =====================================
#  ДАННЫЕ ПАРЫ ДЛЯ /couple
# =====================================

def get_couple_info(user_id: int) -> dict:
    """
    Возвращает данные пары:
        {
            "ok": bool,
            "error": str,
            "user1_id", "user2_id",
            "balance": int,
            "married_at": str,
            "days_together": int,
            "bank1": int, "bank2": int,
            "last_case_at": str|None,
        }
    """
    row = get_marriage(user_id)
    if not row:
        return {"ok": False, "error": "Ты не в браке"}

    marriage_id, u1, u2, balance = row

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "SELECT married_at, last_case_at FROM marriages WHERE id = ?",
        (marriage_id,)
    )
    r = cur.fetchone()
    conn.close()

    married_at = r[0] if r else None
    last_case_at = r[1] if r and len(r) > 1 else None

    days_together = 0
    if married_at:
        try:
            m_dt = datetime.fromisoformat(married_at)
            days_together = (datetime.now() - m_dt).days
        except ValueError:
            pass

    # Банки обоих
    b1 = bank_get(u1)["balance"]
    b2 = bank_get(u2)["balance"]

    return {
        "ok": True,
        "user1_id": u1,
        "user2_id": u2,
        "balance": balance,
        "married_at": married_at,
        "days_together": days_together,
        "bank1": b1,
        "bank2": b2,
        "last_case_at": last_case_at,
    }



