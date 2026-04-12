
from __future__ import annotations
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "rostos.db"

def reset_db() -> None:
    """Remove completamente o arquivo do banco de dados, simulando o primeiro acesso."""
    db_path = get_db_path()
    if db_path.exists():
        db_path.unlink()  # Remove o arquivo do banco


def get_connection() -> sqlite3.Connection:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DB_PATH)


def get_db_path() -> Path:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    return DB_PATH


def ensure_db() -> None:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS rostos (
            ord_id INTEGER PRIMARY KEY AUTOINCREMENT,
            rosto_embeddings BLOB NOT NULL,
            id_rosto TEXT NOT NULL,
            nome TEXT,
            numero_imagem INTEGER NOT NULL,
            turma TEXT NOT NULL,
            data_imagem TEXT NOT NULL,
            origem_nome TEXT
        )
        """
    )
    _ensure_columns(cursor)
    conn.commit()
    conn.close()


def _ensure_columns(cursor: sqlite3.Cursor) -> None:
    cursor.execute("PRAGMA table_info(rostos)")
    columns = {row[1] for row in cursor.fetchall()}

    if "rosto_embeddings" not in columns and "rosto" in columns:
        cursor.execute("ALTER TABLE rostos RENAME COLUMN rosto TO rosto_embeddings")
        columns.add("rosto_embeddings")

    if "rosto_embeddings" not in columns:
        cursor.execute("ALTER TABLE rostos ADD COLUMN rosto_embeddings BLOB")

    if "origem_nome" not in columns:
        cursor.execute("ALTER TABLE rostos ADD COLUMN origem_nome TEXT")


def fetch_df(query: str, params: tuple[Any, ...] = ()) -> pd.DataFrame:
    conn = get_connection()
    try:
        return pd.read_sql_query(query, conn, params=params)
    finally:
        conn.close()


def execute(query: str, params: tuple[Any, ...] = ()) -> None:
    conn = get_connection()
    try:
        conn.execute(query, params)
        conn.commit()
    finally:
        conn.close()


def execute_many(query: str, values: list[tuple[Any, ...]]) -> None:
    if not values:
        return
    conn = get_connection()
    try:
        conn.executemany(query, values)
        conn.commit()
    finally:
        conn.close()


def next_image_number() -> int:
    df = fetch_df("SELECT COALESCE(MAX(numero_imagem), 0) AS max_num FROM rostos")
    return int(df.iloc[0]["max_num"]) + 1 if not df.empty else 1


def export_db_bytes() -> bytes:
    """Return the current SQLite file bytes for download/backup."""
    ensure_db()
    db_path = get_db_path()
    return db_path.read_bytes()


def import_db_bytes(db_bytes: bytes, create_restore_point: bool = True) -> str:
    """Replace the current SQLite file from uploaded bytes and validate schema.

    Returns the restore point path when it is created.
    """
    if not db_bytes:
        raise ValueError("Arquivo de backup vazio.")

    # SQLite files start with this fixed header.
    if len(db_bytes) < 16 or db_bytes[:16] != b"SQLite format 3\x00":
        raise ValueError("Backup invalido: arquivo nao parece ser um SQLite valido.")

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    db_path = get_db_path()

    restore_path = ""
    if create_restore_point and db_path.exists():
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        restore_file = DATA_DIR / f"rostos_backup_antes_restore_{stamp}.db"
        restore_file.write_bytes(db_path.read_bytes())
        restore_path = str(restore_file)

    db_path.write_bytes(db_bytes)

    # Validate that the uploaded file can be opened and has required schema.
    ensure_db()
    return restore_path
