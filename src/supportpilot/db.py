import sqlite3


DB_PATH = "supportpilot.db"


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS tickets (
            ticket_id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id TEXT NOT NULL,
            issue_type TEXT NOT NULL,
            description TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT '已创建'
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS orders (
            order_id TEXT PRIMARY KEY,
            customer_name TEXT NOT NULL,
            product_name TEXT NOT NULL,
            payment_status TEXT NOT NULL,
            shipping_status TEXT NOT NULL,
            estimated_delivery TEXT
        )
        """
    )

    cursor.executemany(
        """
        INSERT OR IGNORE INTO orders (
            order_id,
            customer_name,
            product_name,
            payment_status,
            shipping_status,
            estimated_delivery
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        [
            (
                "A1001",
                "张三",
                "无线蓝牙耳机",
                "已付款",
                "等待仓库发货",
                "预计 2 天内发货",
            ),
            (
                "A1002",
                "李四",
                "机械键盘",
                "已付款",
                "运输中",
                "预计明天送达",
            ),
            (
                "A1003",
                "王五",
                "27 英寸显示器",
                "已付款",
                "已签收",
                "已于昨日送达",
            ),
        ],
    )

    conn.commit()
    conn.close()


def get_order_from_db(order_id: str) -> dict | None:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            order_id,
            customer_name,
            product_name,
            payment_status,
            shipping_status,
            estimated_delivery
        FROM orders
        WHERE order_id = ?
        """,
        (order_id,),
    )

    row = cursor.fetchone()
    conn.close()

    if row is None:
        return None

    return {
        "order_id": row[0],
        "customer_name": row[1],
        "product_name": row[2],
        "payment_status": row[3],
        "shipping_status": row[4],
        "estimated_delivery": row[5],
    }
def create_ticket_in_db(
    order_id: str,
    issue_type: str,
    description: str,
) -> int:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO tickets (
            order_id,
            issue_type,
            description,
            status
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            order_id,
            issue_type,
            description,
            "已创建",
        ),
    )

    ticket_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return ticket_id
def get_ticket_from_db(ticket_id: int) -> dict | None:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            ticket_id,
            order_id,
            issue_type,
            description,
            status
        FROM tickets
        WHERE ticket_id = ?
        """,
        (ticket_id,),
    )

    row = cursor.fetchone()
    conn.close()

    if row is None:
        return None

    return {
        "ticket_id": row[0],
        "order_id": row[1],
        "issue_type": row[2],
        "description": row[3],
        "status": row[4],
    }
def update_ticket_status_in_db(
    ticket_id: int,
    new_status: str,
) -> bool:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE tickets
        SET status = ?
        WHERE ticket_id = ?
        """,
        (
            new_status,
            ticket_id,
        ),
    )

    updated = cursor.rowcount > 0

    conn.commit()
    conn.close()

    return updated