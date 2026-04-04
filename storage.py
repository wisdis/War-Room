import sqlite3
import json

DB_PATH = "database.db"


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        balance INTEGER DEFAULT 0,
        income INTEGER DEFAULT 0,
        population INTEGER DEFAULT 0,
        stability INTEGER DEFAULT 0
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        description TEXT,
        price INTEGER DEFAULT 0,
        buffs TEXT,
        debuffs TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS shop (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        price INTEGER NOT NULL,
        allowed_roles TEXT,
        blocked_roles TEXT,
        buffs TEXT,
        debuffs TEXT,
        quantity INTEGER DEFAULT 1
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS role_income (
        role_id INTEGER PRIMARY KEY,
        income INTEGER DEFAULT 0,
        population INTEGER DEFAULT 0,
        stability INTEGER DEFAULT 0
    )
    """)

    conn.commit()
    conn.close()


def get_user(user_id: int):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("SELECT user_id FROM users WHERE user_id=?", (user_id,))
    exists = cur.fetchone()

    if not exists:
        cur.execute("""
        INSERT INTO users (user_id, balance, income, population, stability)
        VALUES (?, 0, 0, 0, 0)
        """, (user_id,))
        conn.commit()

    conn.close()


def add_money(user_id: int, amount: int):
    get_user(user_id)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("UPDATE users SET balance = balance + ? WHERE user_id=?", (amount, user_id))
    cur.execute("UPDATE users SET balance = 0 WHERE balance < 0 AND user_id=?", (user_id,))

    conn.commit()
    conn.close()


def get_balance(user_id: int):
    get_user(user_id)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("SELECT balance FROM users WHERE user_id=?", (user_id,))
    bal = cur.fetchone()[0]

    conn.close()
    return bal


def get_user_stats(user_id: int):
    get_user(user_id)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("SELECT income, population, stability FROM users WHERE user_id=?", (user_id,))
    row = cur.fetchone()

    conn.close()
    return {"income": row[0], "population": row[1], "stability": row[2]}


def update_user_stats(user_id: int, income=0, population=0, stability=0):
    get_user(user_id)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
    UPDATE users
    SET income = income + ?, population = population + ?, stability = stability + ?
    WHERE user_id=?
    """, (income, population, stability, user_id))

    conn.commit()
    conn.close()


def add_item_to_user(user_id: int, item: dict):
    get_user(user_id)

    buffs = json.dumps(item.get("buffs", {}), ensure_ascii=False)
    debuffs = json.dumps(item.get("debuffs", {}), ensure_ascii=False)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO items (user_id, name, description, price, buffs, debuffs)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        item.get("name"),
        item.get("description"),
        item.get("price", 0),
        buffs,
        debuffs
    ))

    conn.commit()
    conn.close()


def get_user_items(user_id: int):
    get_user(user_id)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("SELECT name, description, price, buffs, debuffs FROM items WHERE user_id=?", (user_id,))
    rows = cur.fetchall()

    conn.close()

    result = []
    for r in rows:
        result.append({
            "name": r[0],
            "description": r[1],
            "price": r[2],
            "buffs": json.loads(r[3]) if r[3] else {},
            "debuffs": json.loads(r[4]) if r[4] else {}
        })
    return result


def apply_item_effects(user_id: int, item: dict):
    buffs = item.get("buffs", {})
    debuffs = item.get("debuffs", {})

    income = buffs.get("income", 0) + debuffs.get("income", 0)
    population = buffs.get("population", 0) + debuffs.get("population", 0)
    stability = buffs.get("stability", 0) + debuffs.get("stability", 0)

    update_user_stats(user_id, income, population, stability)
    add_item_to_user(user_id, item)


def get_shop_items():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("SELECT name, description, price, allowed_roles, blocked_roles, buffs, debuffs FROM shop")
    rows = cur.fetchall()
    conn.close()

    items = []
    for r in rows:
        items.append({
            "name": r[0],
            "description": r[1],
            "price": r[2],
            "allowed_roles": json.loads(r[3]) if r[3] else [],
            "blocked_roles": json.loads(r[4]) if r[4] else [],
            "buffs": json.loads(r[5]) if r[5] else {},
            "debuffs": json.loads(r[6]) if r[6] else {}
        })
    return items


def add_shop_item(item: dict):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO shop (name, description, price, allowed_roles, blocked_roles, buffs, debuffs)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        item.get("name"),
        item.get("description"),
        item.get("price", 0),
        json.dumps(item.get("allowed_roles", []), ensure_ascii=False),
        json.dumps(item.get("blocked_roles", []), ensure_ascii=False),
        json.dumps(item.get("buffs", {}), ensure_ascii=False),
        json.dumps(item.get("debuffs", {}), ensure_ascii=False)
    ))

    conn.commit()
    conn.close()


def set_role_income(role_id: int, income=0, population=0, stability=0):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO role_income (role_id, income, population, stability)
    VALUES (?, ?, ?, ?)
    ON CONFLICT(role_id) DO UPDATE SET
        income=excluded.income,
        population=excluded.population,
        stability=excluded.stability
    """, (role_id, income, population, stability))

    conn.commit()
    conn.close()


def remove_role_income(role_id: int):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("DELETE FROM role_income WHERE role_id=?", (role_id,))
    conn.commit()
    conn.close()


def get_all_role_income():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("SELECT role_id, income, population, stability FROM role_income")
    rows = cur.fetchall()
    conn.close()

    data = {}
    for r in rows:
        data[r[0]] = {"income": r[1], "population": r[2], "stability": r[3]}
    return data
