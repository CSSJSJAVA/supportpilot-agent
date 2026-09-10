"""SupportPilot 数据库层。

负责订单（orders）与售后工单（tickets）的建表、种子数据与读写封装。

相对原版的修改：
1. 删除重复的 ALTER TABLE 检查（原代码复制粘贴了两遍）。
2. 删除成组的重复 UPDATE：hours_since_payment 并入种子数据一次写入。
3. 统一缩进与代码格式。
4. DB_PATH 不再是相对路径：基于 __file__ 定位到项目根目录，
   从任意工作目录启动都能找到同一个数据库文件；
   可通过环境变量 SUPPORTPILOT_DB_PATH 覆盖。
5. 补上原代码缺失的 tickets 建表语句（原 init_db 只建了 orders，
   create_ticket_in_db 直接往 tickets 插数据，全新环境首次运行会报
   "no such table: tickets"）。
"""

import os
import sqlite3
from contextlib import closing
from pathlib import Path

# db.py 位于 src/supportpilot/db.py，项目根目录是其上三级：
# parents[0]=supportpilot, parents[1]=src, parents[2]=项目根目录
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = Path(
    os.environ.get("SUPPORTPILOT_DB_PATH") or _PROJECT_ROOT / "supportpilot.db"
)

# ---------------------------------------------------------------------------
# 连接与建表
# ---------------------------------------------------------------------------


def _connect() -> sqlite3.Connection:
    """创建数据库连接。"""
    return sqlite3.connect(DB_PATH)


def _table_columns(cursor: sqlite3.Cursor, table: str) -> set:
    """返回指定表的全部列名，用于旧库兼容性检查。"""
    cursor.execute(f"PRAGMA table_info({table})")
    return {row[1] for row in cursor.fetchall()}


def _ensure_orders_schema(cursor: sqlite3.Cursor) -> None:
    """创建 orders 表；兼容旧库，缺少 hours_since_payment 列时补建。"""
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS orders (
            order_id TEXT PRIMARY KEY,
            customer_name TEXT,
            product_name TEXT,
            payment_status TEXT,
            shipping_status TEXT,
            estimated_delivery TEXT
        )
        """
    )
    if "hours_since_payment" not in _table_columns(cursor, "orders"):
        cursor.execute(
            """
            ALTER TABLE orders
            ADD COLUMN hours_since_payment INTEGER NOT NULL DEFAULT 0
            """
        )


def _ensure_tickets_schema(cursor: sqlite3.Cursor) -> None:
    """创建 tickets 表（原版缺失，已补上）。"""
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


# ---------------------------------------------------------------------------
# 种子数据
# ---------------------------------------------------------------------------

# 订单种子数据（hours_since_payment 用于物流超时的确定性判断）
_ORDER_SEEDS = [
    {
        "order_id": "A1001",
        "customer_name": "张三",
        "product_name": "无线蓝牙耳机",
        "payment_status": "已付款",
        "shipping_status": "等待仓库发货",
        "estimated_delivery": "预计 2 天内发货",
        "hours_since_payment": 72,
    },
    {
        "order_id": "A1002",
        "customer_name": "李四",
        "product_name": "机械键盘",
        "payment_status": "已付款",
        "shipping_status": "运输中",
        "estimated_delivery": "预计明天送达",
        "hours_since_payment": 30,
    },
    {
        "order_id": "A1003",
        "customer_name": "王五",
        "product_name": "27 英寸显示器",
        "payment_status": "已付款",
        "shipping_status": "已签收",
        "estimated_delivery": "已于昨日送达",
        "hours_since_payment": 96,
    },
    {
        "order_id": "A1004",
        "customer_name": "赵六",
        "product_name": "智能手环",
        "payment_status": "已付款",
        "shipping_status": "等待仓库发货",
        "estimated_delivery": "预计尽快发货",
        "hours_since_payment": 60,
    },
]


def _seed_orders(cursor: sqlite3.Cursor) -> None:
    """写入订单种子数据。已存在的订单不覆盖（幂等）。"""
    cursor.executemany(
        """
        INSERT OR IGNORE INTO orders (
            order_id,
            customer_name,
            product_name,
            payment_status,
            shipping_status,
            estimated_delivery,
            hours_since_payment
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                o["order_id"],
                o["customer_name"],
                o["product_name"],
                o["payment_status"],
                o["shipping_status"],
                o["estimated_delivery"],
                o["hours_since_payment"],
            )
            for o in _ORDER_SEEDS
        ],
    )


def init_db() -> None:
    """初始化数据库：建表 + 写入种子数据。可安全重复调用。"""
    with closing(_connect()) as conn:
        cursor = conn.cursor()
        _ensure_orders_schema(cursor)
        _ensure_tickets_schema(cursor)
        _seed_orders(cursor)
        conn.commit()


# ---------------------------------------------------------------------------
# 订单读写
# ---------------------------------------------------------------------------


def get_order_from_db(order_id: str) -> dict | None:
    """根据订单号查询订单，不存在返回 None。"""
    with closing(_connect()) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT
                order_id,
                customer_name,
                product_name,
                payment_status,
                shipping_status,
                estimated_delivery,
                hours_since_payment
            FROM orders
            WHERE order_id = ?
            """,
            (order_id,),
        )
        row = cursor.fetchone()

    if row is None:
        return None

    return {
        "order_id": row[0],
        "customer_name": row[1],
        "product_name": row[2],
        "payment_status": row[3],
        "shipping_status": row[4],
        "estimated_delivery": row[5],
        "hours_since_payment": row[6],
    }


# ---------------------------------------------------------------------------
# 工单读写
# ---------------------------------------------------------------------------

_TICKET_COLUMNS = (
    "ticket_id, order_id, issue_type, description, status"
)


def _ticket_from_row(row: tuple) -> dict:
    """把查询结果行转换为工单字典。"""
    return {
        "ticket_id": row[0],
        "order_id": row[1],
        "issue_type": row[2],
        "description": row[3],
        "status": row[4],
    }


def create_ticket_in_db(order_id: str, issue_type: str, description: str) -> int:
    """创建售后工单，返回新工单号。"""
    with closing(_connect()) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO tickets (order_id, issue_type, description, status)
            VALUES (?, ?, ?, '已创建')
            """,
            (order_id, issue_type, description),
        )
        ticket_id = cursor.lastrowid
        conn.commit()
    return ticket_id


def get_ticket_from_db(ticket_id: int) -> dict | None:
    """根据工单号查询工单，不存在返回 None。"""
    with closing(_connect()) as conn:
        cursor = conn.cursor()
        cursor.execute(
            f"""
            SELECT {_TICKET_COLUMNS}
            FROM tickets
            WHERE ticket_id = ?
            """,
            (ticket_id,),
        )
        row = cursor.fetchone()

    return _ticket_from_row(row) if row is not None else None


def update_ticket_status_in_db(ticket_id: int, new_status: str) -> bool:
    """更新工单状态，返回是否更新成功（目标工单是否存在）。"""
    with closing(_connect()) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE tickets
            SET status = ?
            WHERE ticket_id = ?
            """,
            (new_status, ticket_id),
        )
        updated = cursor.rowcount > 0
        conn.commit()
    return updated


def find_open_ticket_by_order_and_type(order_id: str, issue_type: str) -> dict | None:
    """查找同一订单下尚未解决的同类型工单（取最新一条），没有则返回 None。"""
    with closing(_connect()) as conn:
        cursor = conn.cursor()
        cursor.execute(
            f"""
            SELECT {_TICKET_COLUMNS}
            FROM tickets
            WHERE order_id = ?
              AND issue_type = ?
              AND status != '已解决'
            ORDER BY ticket_id DESC
            LIMIT 1
            """,
            (order_id, issue_type),
        )
        row = cursor.fetchone()

    return _ticket_from_row(row) if row is not None else None
