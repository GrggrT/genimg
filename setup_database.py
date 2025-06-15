# setup_database.py
import sqlite3
import os
from config import DATABASE_PATH

def create_database():
    """Создает базу данных и необходимые таблицы, если их нет."""
    if os.path.exists(DATABASE_PATH):
        print(f"База данных '{DATABASE_PATH}' уже существует.")
        return

    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        # Создаем таблицу для кэширования информации о командах и логотипах
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS teams_cache (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            team_name_normalized TEXT NOT NULL UNIQUE,
            logo_filename TEXT,
            api_source TEXT,
            last_updated_ts INTEGER
        );
        """)
        
        conn.commit()
        conn.close()
        print(f"База данных успешно создана: {DATABASE_PATH}")

    except Exception as e:
        print(f"!!! Ошибка при создании базы данных: {e}")

if __name__ == "__main__":
    create_database() 