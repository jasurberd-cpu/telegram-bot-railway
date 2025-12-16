import os  # <-- ДОБАВЬ ЭТУ СТРОКУ!
import pandas as pd
import sqlite3
from database import Database

db = Database()

print("Начинаю перенос данных из Excel в базу данных...")

# 1. Перенос пользователей
if os.path.exists("users.xlsx"):
    print("Переношу пользователей...")
    df_users = pd.read_excel("users.xlsx")
    for _, row in df_users.iterrows():
        db.add_user(row['user_id'], row['nickname'])
    print(f"Перенесено пользователей: {len(df_users)}")
else:
    print("Файл users.xlsx не найден")

# 2. Перенос админов
if os.path.exists("admins.xlsx"):
    print("Переношу админов...")
    df_admins = pd.read_excel("admins.xlsx")
    for _, row in df_admins.iterrows():
        db.add_admin(row['user_id'], row.get('username', ''))
    print(f"Перенесено админов: {len(df_admins)}")
else:
    print("Файл admins.xlsx не найден")

# 3. Перенос треков
if os.path.exists("tracks.xlsx"):
    print("Переношу треки...")
    df_tracks = pd.read_excel("tracks.xlsx")
    for _, row in df_tracks.iterrows():
        db.add_track(row['track'], row['status'])
    print(f"Перенесено треков: {len(df_tracks)}")
else:
    print("Файл tracks.xlsx не найден")

# 4. Перенос подписок пользователей
if os.path.exists("user_tracks.xlsx"):
    print("Переношу подписки пользователей...")
    df_user_tracks = pd.read_excel("user_tracks.xlsx")
    for _, row in df_user_tracks.iterrows():
        db.add_user_track(row['user_id'], row['track'])
    print(f"Перенесено подписок: {len(df_user_tracks)}")
else:
    print("Файл user_tracks.xlsx не найден")

print("✅ Перенос данных завершен!")
print(f"Файл базы данных: bot.db")