import sqlite3
from datetime import datetime


def view_logs(limit=50):
    """Просмотр последних логов из базы"""
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()

    cursor.execute('''
                   SELECT l.*,
                          CASE WHEN a.user_id IS NOT NULL THEN 1 ELSE 0 END as is_admin
                   FROM logs l
                            LEFT JOIN admins a ON l.user_id = a.user_id
                   ORDER BY l.created_at DESC LIMIT ?
                   ''', (limit,))

    logs = cursor.fetchall()
    conn.close()

    print(f"\n{'=' * 60}")
    print(f"📜 ПОСЛЕДНИЕ {len(logs)} ДЕЙСТВИЙ:")
    print(f"{'=' * 60}\n")

    for log in logs:
        log_id, user_id, username, action, track_code, old_status, new_status, created_at, is_admin = log

        user_type = "👑 АДМИН" if is_admin else "👤 КЛИЕНТ"

        print(f"🕒 {created_at}")
        print(f"{user_type} {username or f'ID:{user_id}'}")
        print(f"📝 Действие: {action}")

        if track_code:
            print(f"📦 Трек: {track_code}")
        if old_status:
            print(f"📊 Было: {old_status}")
        if new_status:
            print(f"📊 Стало: {new_status}")

        print("-" * 40)


if __name__ == "__main__":
    view_logs(100)