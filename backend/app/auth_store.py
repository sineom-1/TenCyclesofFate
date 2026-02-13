import logging
import secrets
import sqlite3
import string
import time

import mysql.connector

from . import db

logger = logging.getLogger(__name__)

_CODE_ALPHABET = string.ascii_uppercase + string.digits


def _is_sqlite_connection(connection: object) -> bool:
    return isinstance(connection, sqlite3.Connection)


def _normalize_prefix(prefix: str) -> str:
    normalized = "".join(char for char in prefix.strip().upper() if char.isalnum())
    return normalized[:12]


def _generate_activation_code(prefix: str) -> str:
    suffix = "".join(secrets.choice(_CODE_ALPHABET) for _ in range(12))
    return f"{prefix}{suffix}"


def init_auth_tables() -> None:
    connection = db.get_db_connection()
    if connection is None:
        raise RuntimeError("数据库连接失败，无法初始化认证表")

    sqlite_mode = _is_sqlite_connection(connection)
    cursor = connection.cursor()

    try:
        if sqlite_mode:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    password_hash TEXT NOT NULL,
                    created_at INTEGER NOT NULL
                )
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS activation_codes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    code TEXT NOT NULL UNIQUE,
                    status TEXT NOT NULL DEFAULT 'unused',
                    used_by_user_id INTEGER,
                    created_at INTEGER NOT NULL,
                    used_at INTEGER,
                    FOREIGN KEY(used_by_user_id) REFERENCES users(id)
                )
                """
            )
            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_activation_codes_status
                ON activation_codes(status)
                """
            )
        else:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id BIGINT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(64) NOT NULL UNIQUE,
                    password_hash VARCHAR(255) NOT NULL,
                    created_at BIGINT NOT NULL
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS activation_codes (
                    id BIGINT AUTO_INCREMENT PRIMARY KEY,
                    code VARCHAR(64) NOT NULL UNIQUE,
                    status ENUM('unused', 'used') NOT NULL DEFAULT 'unused',
                    used_by_user_id BIGINT NULL,
                    created_at BIGINT NOT NULL,
                    used_at BIGINT NULL,
                    INDEX idx_activation_codes_status (status),
                    CONSTRAINT fk_activation_used_by_user
                        FOREIGN KEY (used_by_user_id) REFERENCES users(id)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                """
            )

        connection.commit()
    except Exception:
        connection.rollback()
        logger.exception("初始化认证数据表失败")
        raise
    finally:
        connection.close()


def get_user_by_username(username: str) -> dict | None:
    connection = db.get_db_connection()
    if connection is None:
        return None

    sqlite_mode = _is_sqlite_connection(connection)
    cursor = connection.cursor(dictionary=True) if not sqlite_mode else connection.cursor()

    try:
        if sqlite_mode:
            cursor.execute(
                "SELECT id, username, password_hash FROM users WHERE username = ?",
                (username,),
            )
            row = cursor.fetchone()
            if row is None:
                return None
            return {
                "id": int(row[0]),
                "username": row[1],
                "password_hash": row[2],
            }

        cursor.execute(
            "SELECT id, username, password_hash FROM users WHERE username = %s",
            (username,),
        )
        row = cursor.fetchone()
        if row is None:
            return None
        return {
            "id": int(row["id"]),
            "username": row["username"],
            "password_hash": row["password_hash"],
        }
    finally:
        connection.close()


def create_user_with_activation(
    username: str,
    password_hash: str,
    activation_code: str,
) -> tuple[dict | None, str | None]:
    connection = db.get_db_connection()
    if connection is None:
        return None, "db_unavailable"

    sqlite_mode = _is_sqlite_connection(connection)
    cursor = connection.cursor(dictionary=True) if not sqlite_mode else connection.cursor()
    now = int(time.time())

    try:
        if sqlite_mode:
            cursor.execute("BEGIN IMMEDIATE")

        if sqlite_mode:
            cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        else:
            cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
        if cursor.fetchone() is not None:
            connection.rollback()
            return None, "username_taken"

        if sqlite_mode:
            cursor.execute(
                "INSERT INTO users (username, password_hash, created_at) VALUES (?, ?, ?)",
                (username, password_hash, now),
            )
        else:
            cursor.execute(
                "INSERT INTO users (username, password_hash, created_at) VALUES (%s, %s, %s)",
                (username, password_hash, now),
            )

        user_id = int(cursor.lastrowid)

        if sqlite_mode:
            cursor.execute(
                """
                UPDATE activation_codes
                SET status = 'used', used_by_user_id = ?, used_at = ?
                WHERE code = ? AND status = 'unused'
                """,
                (user_id, now, activation_code),
            )
        else:
            cursor.execute(
                """
                UPDATE activation_codes
                SET status = 'used', used_by_user_id = %s, used_at = %s
                WHERE code = %s AND status = 'unused'
                """,
                (user_id, now, activation_code),
            )

        if cursor.rowcount != 1:
            connection.rollback()
            return None, "activation_invalid_or_used"

        connection.commit()
        return {"id": user_id, "username": username}, None

    except sqlite3.IntegrityError as exc:
        connection.rollback()
        error_message = str(exc)
        if "users.username" in error_message:
            return None, "username_taken"
        logger.error("创建用户失败: %s", error_message)
        return None, "db_error"
    except mysql.connector.Error as exc:
        connection.rollback()
        if exc.errno == 1062 and "users.username" in (exc.msg or ""):
            return None, "username_taken"
        logger.error("创建用户失败: %s", exc)
        return None, "db_error"
    except Exception as exc:
        connection.rollback()
        logger.exception("创建用户异常: %s", exc)
        return None, "db_error"
    finally:
        connection.close()


def create_activation_codes(count: int, prefix: str = "") -> list[str]:
    if count <= 0:
        return []

    normalized_prefix = _normalize_prefix(prefix)
    connection = db.get_db_connection()
    if connection is None:
        raise RuntimeError("数据库连接失败")

    sqlite_mode = _is_sqlite_connection(connection)
    cursor = connection.cursor()
    created_at = int(time.time())
    generated_codes: list[str] = []

    try:
        for _ in range(count):
            inserted = False
            for _ in range(10):
                code = _generate_activation_code(normalized_prefix)
                try:
                    if sqlite_mode:
                        cursor.execute(
                            """
                            INSERT INTO activation_codes (code, status, created_at)
                            VALUES (?, 'unused', ?)
                            """,
                            (code, created_at),
                        )
                    else:
                        cursor.execute(
                            """
                            INSERT INTO activation_codes (code, status, created_at)
                            VALUES (%s, 'unused', %s)
                            """,
                            (code, created_at),
                        )

                    generated_codes.append(code)
                    inserted = True
                    break
                except sqlite3.IntegrityError:
                    continue
                except mysql.connector.Error as exc:
                    if exc.errno == 1062:
                        continue
                    raise

            if not inserted:
                raise RuntimeError("激活码生成失败，请稍后重试")

        connection.commit()
        return generated_codes
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()
