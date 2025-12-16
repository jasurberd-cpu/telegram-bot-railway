from database import Database

db = Database()

print("=== ПРОВЕРКА БАЗЫ ДАННЫХ ===")

# Проверяем пользователей
users = db.get_all_users()
print(f"Пользователей: {len(users)}")
for user in users[:3]:  # Первые 3
    print(f"  - {user['nickname']} (ID: {user['user_id']})")

# Проверяем админов
admins = db.get_all_admins()
print(f"\nАдминов: {len(admins)}")
for admin in admins:
    print(f"  - ID: {admin['user_id']}")

# Проверяем треки
tracks = db.get_all_tracks()
print(f"\nТреков: {len(tracks)}")
for track in tracks[:3]:  # Первые 3
    print(f"  - {track['track_code']}: {track['status']}")

print("\n✅ Проверка завершена!")