import sqlite3
from datetime import datetime
import logging

# Настройка логгирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Database:
    def __init__(self, db_name='bot.db'):
        self.db_name = db_name
        self.init_db()

    def get_connection(self):
        """Подключение к базе данных"""
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row  # Чтобы получать строки как словари
        return conn

    def init_db(self):
        """Создание таблиц, если их нет"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Таблица пользователей
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS users
                       (
                           id
                           INTEGER
                           PRIMARY
                           KEY
                           AUTOINCREMENT,
                           user_id
                           INTEGER
                           UNIQUE,
                           nickname
                           TEXT,
                           registered_at
                           TIMESTAMP
                           DEFAULT
                           CURRENT_TIMESTAMP
                       )
                       ''')

        # Таблица админов
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS admins
                       (
                           id
                           INTEGER
                           PRIMARY
                           KEY
                           AUTOINCREMENT,
                           user_id
                           INTEGER
                           UNIQUE,
                           username
                           TEXT,
                           added_at
                           TIMESTAMP
                           DEFAULT
                           CURRENT_TIMESTAMP
                       )
                       ''')

        # Таблица треков
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS tracks
                       (
                           id
                           INTEGER
                           PRIMARY
                           KEY
                           AUTOINCREMENT,
                           track_code
                           TEXT
                           UNIQUE,
                           status
                           TEXT,
                           created_at
                           TIMESTAMP
                           DEFAULT
                           CURRENT_TIMESTAMP,
                           updated_at
                           TIMESTAMP
                           DEFAULT
                           CURRENT_TIMESTAMP
                       )
                       ''')

        # Таблица подписок пользователей на треки
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS user_tracks
                       (
                           id
                           INTEGER
                           PRIMARY
                           KEY
                           AUTOINCREMENT,
                           user_id
                           INTEGER,
                           track_code
                           TEXT,
                           date_added
                           TIMESTAMP
                           DEFAULT
                           CURRENT_TIMESTAMP,
                           FOREIGN
                           KEY
                       (
                           user_id
                       ) REFERENCES users
                       (
                           user_id
                       ),
                           FOREIGN KEY
                       (
                           track_code
                       ) REFERENCES tracks
                       (
                           track_code
                       ),
                           UNIQUE
                       (
                           user_id,
                           track_code
                       )
                           )
                       ''')

        # Таблица логов
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS logs
                       (
                           id
                           INTEGER
                           PRIMARY
                           KEY
                           AUTOINCREMENT,
                           user_id
                           INTEGER,
                           username
                           TEXT,
                           action
                           TEXT,
                           track_code
                           TEXT,
                           old_status
                           TEXT,
                           new_status
                           TEXT,
                           created_at
                           TIMESTAMP
                           DEFAULT
                           CURRENT_TIMESTAMP
                       )
                       ''')

        conn.commit()
        conn.close()
        logger.info("База данных инициализирована")

    # -------------------- МЕТОДЫ ДЛЯ ПОЛЬЗОВАТЕЛЕЙ --------------------

    def get_user(self, user_id):
        """Получить пользователя по ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        user = cursor.fetchone()
        conn.close()
        return dict(user) if user else None

    def add_user(self, user_id, nickname):
        """Добавить нового пользователя"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                'INSERT INTO users (user_id, nickname) VALUES (?, ?)',
                (user_id, nickname)
            )
            conn.commit()
            logger.info(f"Добавлен пользователь: {user_id} - {nickname}")
            return True
        except sqlite3.IntegrityError:
            # Пользователь уже существует
            cursor.execute(
                'UPDATE users SET nickname = ? WHERE user_id = ?',
                (nickname, user_id)
            )
            conn.commit()
            logger.info(f"Обновлен пользователь: {user_id} - {nickname}")
            return True
        except Exception as e:
            logger.error(f"Ошибка добавления пользователя: {e}")
            return False
        finally:
            conn.close()

    def get_all_users(self):
        """Получить всех пользователей"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users ORDER BY registered_at DESC')
        users = cursor.fetchall()
        conn.close()
        return [dict(user) for user in users]

    # -------------------- МЕТОДЫ ДЛЯ АДМИНОВ --------------------

    def is_admin(self, user_id):
        """Проверить, является ли пользователь админом"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM admins WHERE user_id = ?', (user_id,))
        admin = cursor.fetchone()
        conn.close()
        return admin is not None

    def add_admin(self, user_id, username=""):
        """Добавить админа"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                'INSERT INTO admins (user_id, username) VALUES (?, ?)',
                (user_id, username)
            )
            conn.commit()
            logger.info(f"Добавлен админ: {user_id} - {username}")
            return True
        except sqlite3.IntegrityError:
            logger.warning(f"Админ {user_id} уже существует")
            return False
        finally:
            conn.close()

    def remove_admin(self, user_id):
        """Удалить админа"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM admins WHERE user_id = ?', (user_id,))
        conn.commit()
        conn.close()
        logger.info(f"Удален админ: {user_id}")

    def get_all_admins(self):
        """Получить всех админов"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM admins ORDER BY added_at DESC')
        admins = cursor.fetchall()
        conn.close()
        return [dict(admin) for admin in admins]

    # -------------------- МЕТОДЫ ДЛЯ ТРЕКОВ --------------------

    def add_track(self, track_code, status="На складе"):
        """Добавить новый трек"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                'INSERT INTO tracks (track_code, status) VALUES (?, ?)',
                (track_code, status)
            )
            conn.commit()
            logger.info(f"Добавлен трек: {track_code} - {status}")
            return True
        except sqlite3.IntegrityError:
            logger.warning(f"Трек {track_code} уже существует")
            return False
        finally:
            conn.close()

    def get_track(self, track_code):
        """Получить трек по коду"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM tracks WHERE track_code = ?', (track_code,))
        track = cursor.fetchone()
        conn.close()
        return dict(track) if track else None

    def get_all_tracks(self):
        """Получить все треки"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM tracks ORDER BY created_at DESC')
        tracks = cursor.fetchall()
        conn.close()
        return [dict(track) for track in tracks]

    def update_track_status(self, track_code, new_status):
        """Обновить статус трека"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
                       UPDATE tracks
                       SET status     = ?,
                           updated_at = CURRENT_TIMESTAMP
                       WHERE track_code = ?
                       ''', (new_status, track_code))
        conn.commit()
        conn.close()
        logger.info(f"Обновлен статус трека {track_code}: {new_status}")

    def delete_track(self, track_code):
        """Удалить трек"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM tracks WHERE track_code = ?', (track_code,))
        cursor.execute('DELETE FROM user_tracks WHERE track_code = ?', (track_code,))
        conn.commit()
        conn.close()
        logger.info(f"Удален трек: {track_code}")

    # -------------------- МЕТОДЫ ДЛЯ ПОЛЬЗОВАТЕЛЕЙ И ТРЕКОВ --------------------

    def get_user_tracks(self, user_id):
        """Получить все треки пользователя"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
                       SELECT t.track_code, t.status, ut.date_added
                       FROM user_tracks ut
                                JOIN tracks t ON ut.track_code = t.track_code
                       WHERE ut.user_id = ?
                       ORDER BY ut.date_added DESC
                       ''', (user_id,))
        tracks = cursor.fetchall()
        conn.close()
        return [dict(track) for track in tracks]

    def add_user_track(self, user_id, track_code):
        """Добавить трек для отслеживания пользователем"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                'INSERT INTO user_tracks (user_id, track_code) VALUES (?, ?)',
                (user_id, track_code)
            )
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()

    def get_track_followers(self, track_code):
        """Получить всех пользователей, отслеживающих трек"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'SELECT user_id FROM user_tracks WHERE track_code = ?',
            (track_code,)
        )
        followers = cursor.fetchall()
        conn.close()
        return [follower[0] for follower in followers]

    def log_action(self, user_id, username, action, track_code="", old_status="", new_status=""):
        """Логировать действие"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
                       INSERT INTO logs (user_id, username, action, track_code, old_status, new_status)
                       VALUES (?, ?, ?, ?, ?, ?)
                       ''', (user_id, username, action, track_code, old_status, new_status))
        conn.commit()
        conn.close()