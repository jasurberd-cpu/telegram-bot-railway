import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (  # <- Эта строка ОБЯЗАТЕЛЬНА
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    MessageHandler, ContextTypes, filters
)
from datetime import datetime

# Импортируем нашу новую базу данных
from database import Database

# Настройка логгирования
BOT_TOKEN = os.getenv("BOT_TOKEN")  # В кавычках ИМЯ переменной, а не её значение!
if not BOT_TOKEN:
    raise ValueError("❌ Токен не найден! Задайте переменную окружения BOT_TOKEN в настройках Koyeb")

# Уменьшаем спам от httpx
logging.getLogger("httpx").setLevel(logging.WARNING)


#    raise ValueError("❌ Токен не найден! Проверь файл .env")

# Создаём объект базы данных
db = Database()

# ==================== МНОГОЯЗЫЧНОСТЬ ====================
TEXTS = {
    'ru': {
        # Команды
        'start_admin': "Привет, @{username}! Что хотите сделать?",
        'start_client': "Привет, {nickname}! Выберите действие:",
        'start_ask_name': "Привет! Как вас зовут?",

        # Меню
        'menu_track_list': "📋 Список треков",
        'menu_add_track': "➕ Добавить трек",
        'menu_delete_track': "🗑 Удалить трек",
        'menu_change_status': "🛠 Изменить статус",
        'menu_users_list': "👥 Список пользователей",
        'menu_admins_list': "👤 Список админов",
        'menu_add_admin': "➕ Добавить админа",
        'menu_remove_admin': "❌ Удалить админа",
        'menu_view_logs': "📜 Посмотреть логи",
        'menu_user_add_track': "📦 Добавить трек",
        'menu_user_my_tracks': "📝 Мои треки",
        'menu_fill_data': "📝 Адрес",
        'menu_change_language': "🌐 Сменить язык",

        # Форма
        'form_ask_name': "👤 Введите ваше имя:",
        'form_ask_city': "🏙️ Введите ваш город:",
        'form_ask_phone': "📞 Введите ваш номер телефона:",

        # Сообщения после формы
        'form_success': "✅ <b>Данные сохранены!</b>",
        'form_name': "👤 <b>Имя:</b> {name}",
        'form_city': "🏙️ <b>Город:</b> {city}",
        'form_phone': "📞 <b>Телефон:</b> {phone}",
        'form_address_title': "📍 <b>ГОТОВЫЙ АДРЕС ДЛЯ ЗАКАЗА:</b>",
        'form_click_to_copy': "<i>Нажмите на адрес, чтобы скопировать</i>",
        'form_instruction': "<b>Инструкция:</b>",
        'form_step1': "1. Нажмите на адрес выше",
        'form_step2': "2. Выберите 'Копировать'",
        'form_step3': "3. Вставьте в поле 'Адрес доставки' в магазине",
        'form_step4': "4. Готово!",

        # Реклама
        'ads_title': "📢 <b>ПОЛЕЗНЫЕ КОНТАКТЫ</b>",
        'ads_channel': "📈 <b>Наш канал с новостями:</b>\n👉 @taror_cargo",
        'ads_manager': "👨‍💼 <b>Менеджер:</b>\n👉 @sharifovsharif1",
        'ads_contact': "💬 <b>Вопросы? Пишите!</b>",

        # Кнопки
        'btn_back': "⬅️ Назад",
        'btn_main': "⬅️ На главную",
        'btn_copy': "📋 Скопировать адрес",
        'btn_copied': "✅ Я скопировал",

        # Другое
        'no_tracks': "Треков не найдено.",
        'enter_track': "Введите ваш трек-код:",
        'track_added': "✅ Трек {track_code} добавлен для отслеживания!",
        # Треки
        'no_tracks': "Треков не найдено.",
        'enter_track': "Введите ваш трек-код:",
        'track_added': "✅ Трек {track_code} добавлен для отслеживания!",
        'track_already': "⚠️ Вы уже отслеживаете этот трек.",
        'track_not_found': "❌ Трек не найден в базе.",
        'enter_track_status': "Напишите трек и статус через пробел, например:\nCN123456 на складе",
        'track_exists': "⚠️ Такой трек уже есть",
        'track_added_admin': "✅ Трек {track_code} добавлен со статусом {status}",
        'invalid_format': "❌ Неверный формат. Используйте: ТРЕК_КОД СТАТУС",

        # Админы
        'enter_admin_id': "Введите ID нового админа:",
        'admin_added': "✅ Админ {admin_id} добавлен!",
        'admin_exists': "⚠️ Этот ID уже есть в списке админов",
        'enter_remove_admin_id': "Введите ID админа для удаления:",
        'admin_removed': "✅ Админ {admin_id} удален!",
        'enter_user_id': "Введите ID пользователя:",
        'id_must_be_number': "❌ ID должен быть числом",

        # Статусы треков
        'select_track_delete': "Выберите трек для удаления:",
        'select_track_change': "Выберите трек для изменения статуса:",
        'track_list': "Список треков:",
        'track_info': "Трек: {track_code}\nСтатус: {status}",
        'select_new_status': "Выберите новый статус для трека {track_code}:",
        'enter_new_status': "Введите новый статус для трека {track_code}:",
        'status_changed': "✅ Статус трека {track_code} изменён на {new_status}",
        'track_deleted': "🗑 Трек {track_code} удалён",
        'track_not_found_short': "Трек не найден",

        # Статус-кнопки
        'status_in_warehouse': "📦 На складе",
        'status_in_transit': "🚚 В пути",
        'status_delivered': "✅ Доставлено",
        'status_other': "🔄 Другой статус",

        # Пользователи
        'no_users': "Пока нет зарегистрированных пользователей",
        'users_list': "Список пользователей:\n{users}",
        'no_admins': "Пока нет админов",
        'admins_list': "Список админов:\n{admins}",
        'user_without_username': "Без ника",

        # Логи
        'no_logs': "Логов пока нет.",
        'last_20_actions': "📜 **Последние 20 действий:**\n",
        'track': "📦 Трек:",
        'was': "📊 Было:",
        'became': "📊 Стало:",

        # Ошибки
        'unknown_command': "Я не понимаю эту команду. Напишите /start",
        'choose_action': "Выберите действие:",

        # Пагинация
        'previous': "⬅ Предыдущая",
        'next': "Следующая ➡",
        'my_tracks': "Ваши треки:",
        'greeting': "Приятно познакомиться, {name}! Выберите действие:",
        'track_updated_notif': "📦 Трек {track_code} обновлён!\nНовый статус: {new_status}",
        'nice_to_meet': "Приятно познакомиться, {name}! Выберите действие:",
        'invalid_format_full': "❌ Неверный формат. Используйте: ТРЕК_КОД СТАТУС",
        'track_added_with_status': "✅ Трек {track_code} добавлен со статусом {status}",
        'track_exists_full': "⚠️ Такой трек уже есть",
        'admin_added_full': "✅ Админ {admin_id} добавлен!",
        'admin_exists_full': "⚠️ Этот ID уже есть в списке админов",
        'id_number': "❌ ID должен быть числом",
        'admin_removed_full': "✅ Админ {admin_id} удален!",
        'unknown_command_full': "Я не понимаю эту команду. Напишите /start",
        'change_status_menu': "Изменить статус",
        'delete_track_menu': "Удалить трек",
        # ... добавь остальные тексты по аналогии
    },

    'tj': {
        # Команды
        'start_admin': "Салом, @{username}! Чӣ мехоҳед кардан?",
        'start_client': "Салом, {nickname}! Амалро интихоб кунед:",
        'start_ask_name': "Салом! Номи шумо чӣ?",

        # Меню
        'menu_track_list': "📋 Рӯйхати трекҳо",
        'menu_add_track': "➕ Иловаи трек",
        'menu_delete_track': "🗑 Ҳазфи трек",
        'menu_change_status': "🛠 Тағири статус",
        'menu_users_list': "👥 Рӯйхати корбарон",
        'menu_admins_list': "👤 Рӯйхати админҳо",
        'menu_add_admin': "➕ Иловаи админ",
        'menu_remove_admin': "❌ Ҳазфи админ",
        'menu_view_logs': "📜 Дидани логҳо",
        'menu_user_add_track': "📦 Иловаи трек",
        'menu_user_my_tracks': "📝 Трекҳои ман",
        'menu_fill_data': "📝 Адрес",
        'menu_change_language': "🌐 Тағири забон",

        # Форма
        'form_ask_name': "👤 Номи худро ворид кунед:",
        'form_ask_city': "🏙️ Шаҳри худро ворид кунед:",
        'form_ask_phone': "📞 Рақами телефони худро ворид кунед:",

        # Сообщения после формы
        'form_success': "✅ <b>Маълумотҳо захира шуданд!</b>",
        'form_name': "👤 <b>Ном:</b> {name}",
        'form_city': "🏙️ <b>Шаҳр:</b> {city}",
        'form_phone': "📞 <b>Телефон:</b> {phone}",
        'form_address_title': "📍 <b>АДРЕСИ ОМАДА БАРОИ ФАРМОИШ:</b>",
        'form_click_to_copy': "<i>Барои нусхабардорӣ ба адрес клик кунед</i>",
        'form_instruction': "<b>Дастур:</b>",
        'form_step1': "1. Ба адреси боло клик кунед",
        'form_step2': "2. 'Нусхабардорӣ'-ро интихоб кунед",
        'form_step3': "3. Онро дар майдони 'Адреси расондан' дар мағоза гузоред",
        'form_step4': "4. Омода аст!",

        # Реклама
        'ads_title': "📢 <b>АЛОКАИ МУФИД</b>",
        'ads_channel': "📈 <b>Канали мо бо хабару ахборот:</b>\n👉 @taror_cargo",
        'ads_manager': "👨‍💼 <b>Менеҷер:</b>\n👉 @sharifovsharif1",
        'ads_contact': "💬 <b>Саволҳо? Нависед!</b>",

        # Кнопки
        'btn_back': "⬅️ Бозгашт",
        'btn_main': "⬅️ Ба асосӣ",
        'btn_copy': "📋 Нусхабардории адрес",
        'btn_copied': "✅ Ман нусхабардорӣ кардам",

        # Другое
        'no_tracks': "Трекҳо ёфт нашуд.",
        'enter_track': "Рамзи треки худро ворид кунед:",
        'track_added': "✅ Трек {track_code} барои пайгирӣ илова шуд!",
        # Треки
        'no_tracks': "Трекҳо ёфт нашуд.",
        'enter_track': "Рамзи треки худро ворид кунед:",
        'track_added': "✅ Трек {track_code} барои пайгирӣ илова шуд!",
        'track_already': "⚠️ Шумо аллакай ин трекро пайгирӣ мекунед.",
        'track_not_found': "❌ Трек дар пойгоҳ ёфт нашуд.",
        'enter_track_status': "Трек ва статусро бо фосила нависед, масалан:\nCN123456 дар анбор",
        'track_exists': "⚠️ Ин трек аллакай мавҷуд аст",
        'track_added_admin': "✅ Трек {track_code} бо статуси {status} илова шуд",
        'invalid_format': "❌ Формати нодуруст. Истифода баред: ТРЕК_КОД СТАТУС",

        # Админы
        'enter_admin_id': "ID-и админи навро ворид кунед:",
        'admin_added': "✅ Админ {admin_id} илова шуд!",
        'admin_exists': "⚠️ Ин ID аллакай дар рӯйхати админҳо мавҷуд аст",
        'enter_remove_admin_id': "ID-и админи ҳазфшавандаро ворид кунед:",
        'admin_removed': "✅ Админ {admin_id} ҳазф шуд!",
        'enter_user_id': "ID-и корбарро ворид кунед:",
        'id_must_be_number': "❌ ID бояд рақам бошад",

        # Статусы треков
        'select_track_delete': "Треки ҳазфшавандаро интихоб кунед:",
        'select_track_change': "Треки тағири статусро интихоб кунед:",
        'track_list': "Рӯйхати трекҳо:",
        'track_info': "Трек: {track_code}\nСтатус: {status}",
        'select_new_status': "Статуси нави треки {track_code}-ро интихоб кунед:",
        'enter_new_status': "Статуси нави треки {track_code}-ро ворид кунед:",
        'status_changed': "✅ Статуси треки {track_code} ба {new_status} тағир дода шуд",
        'track_deleted': "🗑 Трек {track_code} ҳазф шуд",
        'track_not_found_short': "Трек ёфт нашуд",

        # Статус-кнопки
        'status_in_warehouse': "📦 Дар анбор",
        'status_in_transit': "🚚 Дар роҳ",
        'status_delivered': "✅ Расид",
        'status_other': "🔄 Статуси дигар",

        # Пользователи
        'no_users': "То ҳол корбари сабтиномшуда нест",
        'users_list': "Рӯйхати корбарон:\n{users}",
        'no_admins': "То ҳол админ нест",
        'admins_list': "Рӯйхати админҳо:\n{admins}",
        'user_without_username': "Бе номи корбарӣ",

        # Логи
        'no_logs': "Акнун логҳо нестанд.",
        'last_20_actions': "📜 **20 амали охирин:**\n",
        'track': "📦 Трек:",
        'was': "📊 Буда:",
        'became': "📊 Шуд:",

        # Ошибки
        'unknown_command': "Ман ин фармонро намефаҳмам. /start-ро нависед",
        'choose_action': "Амалро интихоб кунед:",

        # Пагинация
        'previous': "⬅ Қаблӣ",
        'next': "Оянда ➡",
        'my_tracks': "Трекҳои шумо:",
        'greeting': "Хуш омадед, {name}! Амалро интихоб кунед:",
        'track_updated_notif': "📦 Треки {track_code} нав карда шуд!\nСтатуси нав: {new_status}",
        'nice_to_meet': "Хуш омадед, {name}! Амалро интихоб кунед:",
        'invalid_format_full': "❌ Формати нодуруст. Истифода баред: ТРЕК_КОД СТАТУС",
        'track_added_with_status': "✅ Трек {track_code} бо статуси {status} илова шуд",
        'track_exists_full': "⚠️ Ин трек аллакай мавҷуд аст",
        'admin_added_full': "✅ Админ {admin_id} илова шуд!",
        'admin_exists_full': "⚠️ Ин ID аллакай дар рӯйхати админҳо мавҷуд аст",
        'id_number': "❌ ID бояд рақам бошад",
        'admin_removed_full': "✅ Админ {admin_id} ҳазф шуд!",
        'unknown_command_full': "Ман ин фармонро намефаҳмам. /start-ро нависед",
        'change_status_menu': "Тағири статус",
        'delete_track_menu': "Ҳазфи трек",
        # ... добавь остальные тексты
    }
}

# ==================== ЯЗЫКИ ====================
async def language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Смена языка"""
    keyboard = [
        [InlineKeyboardButton("🇷🇺 Русский", callback_data="set_lang_ru"),
         InlineKeyboardButton("🇹🇯 Тоҷикӣ", callback_data="set_lang_tj")]
    ]
    await update.message.reply_text(
        "Выберите язык / Забони худро интихоб кунед:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ==================== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ====================
def is_admin(user_id):
    """Проверить, является ли пользователь админом"""
    return db.is_admin(user_id)


def get_nickname(user_id):
    """Получить никнейм пользователя"""
    user = db.get_user(user_id)
    return user['nickname'] if user else None


def set_nickname(user_id, nickname):
    """Установить никнейм пользователя"""
    db.add_user(user_id, nickname)


def back_button(context=None):
    """Создать кнопку назад с учетом языка"""
    if context and 'language' in context.user_data:
        lang = context.user_data.get('language', 'ru')
        texts = TEXTS[lang]
        text = texts['btn_back']
    else:
        text = "⬅ Назад"

    return InlineKeyboardMarkup([[InlineKeyboardButton(text, callback_data="back")]])

async def send_or_edit(update: Update, text, reply_markup=None):
    """Универсальная отправка/редактирование сообщений"""
    if update.message:
        await update.message.reply_text(text, reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup)


# ==================== ЛОГИРОВАНИЕ ====================
async def log_action(update: Update, action: str, details: str = ""):
    """Логировать действие с информацией о пользователе"""
    if update.message:
        user = update.message.from_user
    elif update.callback_query:
        user = update.callback_query.from_user
    else:
        return

    user_type = "👑 АДМИН" if is_admin(user.id) else "👤 КЛИЕНТ"
    log_message = f"{user_type} {user.username or user.id} ({user.id}): {action}"
    if details:
        log_message += f" | {details}"

    # Записываем в базу
    db.log_action(
        user_id=user.id,
        username=user.username or "",
        action=action,
        track_code="",
        old_status="",
        new_status=""
    )

    # Также печатаем в консоль
    print(f"[LOG] {datetime.now().strftime('%H:%M:%S')} {log_message}")


# ==================== ОБРАБОТКА ДАННЫХ ФОРМЫ ====================
async def process_form_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка собранных данных формы"""
    user_data = context.user_data["user_data"]
    lang = context.user_data.get('language', 'ru')
    texts = TEXTS[lang]

    name = user_data.get("name", "")
    city = user_data.get("city", "")
    phone = user_data.get("phone", "")

    # Очищаем телефон (оставляем только цифры)
    phone_clean = ''.join(filter(str.isdigit, phone))

    # Готовый адрес с подстановкой
    final_address = f"Taror_cargo 18057174350浙江省金华市义乌市长春九街48-50号 {city} {name}+{phone_clean}"

    # Логируем действие
    await log_action(update, f"заполнил данные: {name}, {city}, {phone}")

    # 1. Сообщение с данными пользователя
    await update.message.reply_text(
        f"{texts['form_success']}\n\n"
        f"{texts['form_name'].format(name=name)}\n"
        f"{texts['form_city'].format(city=city)}\n"
        f"{texts['form_phone'].format(phone=phone)}",
        parse_mode='HTML'
    )

    # 2. Сообщение с адресом (кликабельным)
    await update.message.reply_text(
        f"{texts['form_address_title']}\n\n"
        f"<code>{final_address}</code>\n\n"
        f"{texts['form_click_to_copy']}\n\n"
        f"{texts['form_instruction']}\n"
        f"{texts['form_step1']}\n"
        f"{texts['form_step2']}\n"
        f"{texts['form_step3']}\n"
        f"{texts['form_step4']}",
        parse_mode='HTML'
    )

    # 3. Сообщение с рекламой
    await update.message.reply_text(
        f"{texts['ads_title']}\n\n"
        f"{texts['ads_channel']}\n\n"
        f"{texts['ads_manager']}\n\n"
        f"{texts['ads_contact']}",
        parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton(texts['btn_main'], callback_data="back")]
        ])
    )

    # Очищаем временные данные
    context.user_data.pop("data_step", None)
    context.user_data.pop("data_steps", None)
    context.user_data.pop("user_data", None)

# ==================== СТАРТ ====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработчик команды /start
    """
    if update.message:
        user = update.message.from_user
    elif update.callback_query:
        user = update.callback_query.from_user
        await update.callback_query.answer()
    else:
        return

    # Логируем действие
    await log_action(update, "старт бота")

    # Предлагаем выбрать язык если не выбран
    if 'language' not in context.user_data:
        keyboard = [
            [InlineKeyboardButton("🇷🇺 Русский", callback_data="set_lang_ru"),
             InlineKeyboardButton("🇹🇯 Тоҷикӣ", callback_data="set_lang_tj")]
        ]
        await send_or_edit(update, "Выберите язык / Забони худро интихоб кунед:",
                           InlineKeyboardMarkup(keyboard))
        return

    lang = context.user_data.get('language', 'ru')
    texts = TEXTS[lang]

    if is_admin(user.id):
        keyboard = [
            [InlineKeyboardButton(texts['menu_track_list'], callback_data="list_tracks"),
             InlineKeyboardButton(texts['menu_add_track'], callback_data="add_track")],
            [InlineKeyboardButton(texts['menu_delete_track'], callback_data="delete_track"),
             InlineKeyboardButton(texts['menu_change_status'], callback_data="change_status")],
            [InlineKeyboardButton(texts['menu_users_list'], callback_data="list_users"),
             InlineKeyboardButton(texts['menu_admins_list'], callback_data="list_admins")],
            [InlineKeyboardButton(texts['menu_add_admin'], callback_data="add_admin"),
             InlineKeyboardButton(texts['menu_remove_admin'], callback_data="remove_admin")],
            [InlineKeyboardButton(texts['menu_view_logs'], callback_data="view_logs")],
            [InlineKeyboardButton(texts['menu_change_language'], callback_data="change_language")]
        ]

        await send_or_edit(update, texts['start_admin'].format(username=user.username),
                           InlineKeyboardMarkup(keyboard))
    else:
        nickname = get_nickname(user.id)
        if nickname:
            keyboard = [
                [InlineKeyboardButton(texts['menu_user_add_track'], callback_data="user_add_track")],
                [InlineKeyboardButton(texts['menu_user_my_tracks'], callback_data="user_my_tracks")],
                [InlineKeyboardButton(texts['menu_fill_data'], callback_data="fill_data")],
                [InlineKeyboardButton(texts['menu_change_language'], callback_data="change_language")]
            ]
            await send_or_edit(update, texts['start_client'].format(nickname=nickname),
                               InlineKeyboardMarkup(keyboard))
        else:
            await send_or_edit(update, texts['start_ask_name'])
            context.user_data["awaiting_nickname"] = True
# ==================== ПАГИНАЦИЯ ====================
PAGE_SIZE = 5


async def show_tracks_page(update, tracks_list, page, admin=True, action_prefix="", context=None):
    """
    Показать страницу с треками
    """
    if not tracks_list:
        lang = context.user_data.get('language', 'ru') if context else 'ru'
        texts = TEXTS[lang]
        await send_or_edit(update, texts['no_tracks'], back_button(context))
        return

    start_idx = page * PAGE_SIZE
    end_idx = start_idx + PAGE_SIZE
    subset = tracks_list[start_idx:end_idx]

    keyboard = []
    for track in subset:
        track_code = track['track_code']
        status = track['status']

        if action_prefix:
            callback_data = f"{action_prefix}_{track_code}"
        else:
            callback_data = f"track_{track_code}" if admin else f"user_track_{track_code}"

        keyboard.append([InlineKeyboardButton(f"{track_code} ({status})", callback_data=callback_data)])

    # Получаем язык
    lang = context.user_data.get('language', 'ru') if context else 'ru'
    texts = TEXTS[lang]

    nav_buttons = []
    if start_idx > 0:
        nav_buttons.append(InlineKeyboardButton(texts['previous'], callback_data=f"page_{page - 1}_{action_prefix}"))
    if end_idx < len(tracks_list):
        nav_buttons.append(InlineKeyboardButton(texts['next'], callback_data=f"page_{page + 1}_{action_prefix}"))

    if nav_buttons:
        keyboard.append(nav_buttons)

    keyboard.append([InlineKeyboardButton(texts['btn_back'], callback_data="back")])

    if action_prefix == "delete":
        title = texts['select_track_delete']
    elif action_prefix == "change":
        title = texts['select_track_change']
    else:
        title = texts['track_list']

    await send_or_edit(update, title, InlineKeyboardMarkup(keyboard))

# ==================== ПРОСМОТР ЛОГОВ ====================
async def show_logs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Показать последние логи из базы данных
    """
    # Получаем язык пользователя
    lang = context.user_data.get('language', 'ru')
    texts = TEXTS[lang]

    try:
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
                       SELECT l.*,
                              CASE WHEN a.user_id IS NOT NULL THEN 1 ELSE 0 END as is_admin
                       FROM logs l
                                LEFT JOIN admins a ON l.user_id = a.user_id
                       ORDER BY l.created_at DESC LIMIT 20
                       ''')

        logs_data = cursor.fetchall()
        conn.close()

        if not logs_data:
            await send_or_edit(update, texts['no_logs'], back_button(context))
            return

        # Используем переводы
        text_lines = [texts['last_20_actions']]

        for log in logs_data:
            log_id, user_id, username, action, track_code, old_status, new_status, created_at, is_admin_flag = log

            user_type = "👑 АДМИН" if is_admin_flag else "👤 КЛИЕНТ"
            user_info = f"{username or f'ID:{user_id}'}"

            log_line = f"🕒 {created_at}\n"
            log_line += f"{user_type} {user_info}\n"
            log_line += f"📝 {action}\n"

            if track_code:
                log_line += f"{texts['track']} {track_code}\n"
            if old_status:
                log_line += f"{texts['was']} {old_status}\n"
            if new_status:
                log_line += f"{texts['became']} {new_status}\n"

            text_lines.append(log_line + "─" * 30 + "\n")

        text = "".join(text_lines)
        if len(text) > 4000:
            text = text[:4000] + "\n... (показаны последние 20 записей)"

        await send_or_edit(update, text, back_button(context))

    except Exception as e:
        logging.error(f"Ошибка при чтении логов: {e}")
        error_text = f"❌ Ошибка при получении логов: {str(e)}"
        if lang == 'tj':
            error_text = f"❌ Хато дар гирифтани логҳо: {str(e)}"
        await send_or_edit(update, error_text, back_button(context))

# ==================== INLINE КНОПКИ ====================
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработчик inline кнопок
    """
    query = update.callback_query
    await query.answer()
    user = query.from_user
    data = query.data

    # Логируем нажатие кнопки
    await log_action(update, f"нажал кнопку: {data}")

    if data == "back":
        await start(update, context)
        return
    elif data.startswith("set_lang_"):
        lang = data.split("_")[2]  # ru или tj
        context.user_data['language'] = lang
        await start(update, context)  # Перезапускаем старт с выбранным языком
        return
    elif data == "change_language":
        # Показываем меню выбора языка
        keyboard = [
            [InlineKeyboardButton("🇷🇺 Русский", callback_data="set_lang_ru"),
             InlineKeyboardButton("🇹🇯 Тоҷикӣ", callback_data="set_lang_tj")],
            [InlineKeyboardButton("⬅️ Назад", callback_data="back")]
        ]

        await query.edit_message_text(
            "Выберите язык / Забони худро интихоб кунед:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    # Обработка пагинации
    if data.startswith("page_"):
        parts = data.split("_")
        page = int(parts[1])
        action_prefix = parts[2] if len(parts) > 2 else ""

        if "tracks_list" in context.user_data:
            tracks_list = context.user_data["tracks_list"]
            if action_prefix:
                await show_tracks_page(update, tracks_list, page, is_admin(user.id), action_prefix, context=context)
            else:
                await show_tracks_page(update, tracks_list, page, is_admin(user.id), context=context)
        return

    # ---------- АДМИН ----------
    if is_admin(user.id):
        # Список треков
        if data == "list_tracks":
            tracks = db.get_all_tracks()
            if not tracks:
                await send_or_edit(update, "Треков нет.", back_button(context))
                return
            context.user_data["page"] = 0
            context.user_data["tracks_list"] = tracks
            await show_tracks_page(update, tracks, 0, context=context, admin=True)
            return

        # Добавить трек
        elif data == "add_track":
            context.user_data["adding"] = True
            lang = context.user_data.get('language', 'ru')
            texts = TEXTS[lang]
            await send_or_edit(update, texts['enter_track_status'])
            return

        # Удалить трек
        elif data == "delete_track":
            tracks = db.get_all_tracks()
            lang = context.user_data.get('language', 'ru')
            texts = TEXTS[lang]

            if not tracks:
                await send_or_edit(update, texts['no_tracks'], back_button(context))
            else:
                context.user_data["page"] = 0
                context.user_data["tracks_list"] = tracks
                await show_tracks_page(update, tracks, 0, admin=True, action_prefix="delete", context=context)
            return

        # Изменить статус
        elif data == "change_status":
            tracks = db.get_all_tracks()
            lang = context.user_data.get('language', 'ru')
            texts = TEXTS[lang]

            if not tracks:
                await send_or_edit(update, texts['no_tracks'] + " для изменения статуса.", back_button(context))
            else:
                context.user_data["page"] = 0
                context.user_data["tracks_list"] = tracks
                await show_tracks_page(update, tracks, 0, admin=True, action_prefix="change", context=context)
            return

        # Список пользователей
        elif data == "list_users":
            users = db.get_all_users()
            lang = context.user_data.get('language', 'ru')
            texts = TEXTS[lang]

            if not users:
                await send_or_edit(update, texts['no_users'], back_button(context))
            else:
                user_list = "\n".join([f"{user['nickname']} (ID: {user['user_id']})" for user in users])
                await send_or_edit(update, texts['users_list'].format(users=user_list), back_button(context))
            return

        # Список админов
        elif data == "list_admins":
            admins = db.get_all_admins()
            lang = context.user_data.get('language', 'ru')
            texts = TEXTS[lang]

            if not admins:
                await send_or_edit(update, texts['no_admins'], back_button(context))
            else:
                admin_list = "\n".join(
                    [f"{admin['username'] or texts['user_without_username']} (ID: {admin['user_id']})" for admin in
                     admins])
                await send_or_edit(update, texts['admins_list'].format(admins=admin_list), back_button(context))
            return

        # Просмотр логов
        elif data == "view_logs":
            await show_logs(update, context)
            return

        # Добавить админа
        elif data == "add_admin":
            context.user_data["adding_admin"] = True
            lang = context.user_data.get('language', 'ru')
            texts = TEXTS[lang]
            await send_or_edit(update, texts['enter_admin_id'])
            return

        # Удалить админа
        elif data == "remove_admin":
            context.user_data["removing_admin"] = True
            lang = context.user_data.get('language', 'ru')
            texts = TEXTS[lang]
            await send_or_edit(update, texts['enter_remove_admin_id'])
            return

        # Выбор конкретного трека
        elif data.startswith("track_"):
            track_code = data[6:]
            track = db.get_track(track_code)
            lang = context.user_data.get('language', 'ru')
            texts = TEXTS[lang]

            if not track:
                await send_or_edit(update, texts['track_not_found_short'], back_button(context))
                return

            keyboard = [
                [InlineKeyboardButton(texts['change_status_menu'], callback_data=f"change_{track_code}")],
                [InlineKeyboardButton(texts['delete_track_menu'], callback_data=f"delete_{track_code}")],
            ]
            await send_or_edit(update, texts['track_info'].format(track_code=track_code, status=track['status']),
                               InlineKeyboardMarkup(keyboard))
            return

        # Изменение статуса конкретного трека
        elif data.startswith("change_"):
            track_code = data[7:]
            track = db.get_track(track_code)
            lang = context.user_data.get('language', 'ru')
            texts = TEXTS[lang]

            if not track:
                await send_or_edit(update, texts['track_not_found_short'], back_button(context))
                return

            keyboard = [
                [InlineKeyboardButton(texts['status_in_warehouse'], callback_data=f"setstatus_{track_code}_На складе"),
                 InlineKeyboardButton(texts['status_in_transit'], callback_data=f"setstatus_{track_code}_В пути")],
                [InlineKeyboardButton(texts['status_delivered'], callback_data=f"setstatus_{track_code}_Доставлено")],
                [InlineKeyboardButton(texts['status_other'], callback_data=f"custom_status_{track_code}")],
                [InlineKeyboardButton(texts['btn_back'], callback_data=f"track_{track_code}")]
            ]
            await send_or_edit(update, texts['select_new_status'].format(track_code=track_code),
                               InlineKeyboardMarkup(keyboard))
            return

        # Кастомный статус
        elif data.startswith("custom_status_"):
            track_code = data[14:]
            context.user_data["custom_status_for"] = track_code
            lang = context.user_data.get('language', 'ru')
            texts = TEXTS[lang]
            await send_or_edit(update, texts['enter_new_status'].format(track_code=track_code))
            return

        # Установка нового статуса
        elif data.startswith("setstatus_"):
            parts = data.split("_", 2)
            track_code = parts[1]
            new_status = parts[2]

            old_track = db.get_track(track_code)
            lang = context.user_data.get('language', 'ru')
            texts = TEXTS[lang]

            if not old_track:
                await send_or_edit(update, texts['track_not_found_short'])
                return

            old_status = old_track['status']
            db.update_track_status(track_code, new_status)

            # Логируем в базу
            db.log_action(
                user_id=user.id,
                username=user.username or "",
                action="update_status",
                track_code=track_code,
                old_status=old_status,
                new_status=new_status
            )

            # Уведомляем клиентов
            followers = db.get_track_followers(track_code)
            for follower_id in followers:
                try:
                    await context.bot.send_message(follower_id, texts['track_updated_notif'].format(track_code=track_code,
                                                                                                new_status=new_status))
                except Exception as e:
                    print(f"Не удалось отправить уведомление пользователю {follower_id}: {e}")

            await send_or_edit(update, texts['status_changed'].format(track_code=track_code, new_status=new_status))
            return

        # Удаление трека
        elif data.startswith("delete_"):
            track_code = data[7:]
            track = db.get_track(track_code)
            lang = context.user_data.get('language', 'ru')
            texts = TEXTS[lang]

            if not track:
                await send_or_edit(update, texts['track_not_found_short'])
                return

            old_status = track['status']
            db.delete_track(track_code)

            # Логируем в базу
            db.log_action(
                user_id=user.id,
                username=user.username or "",
                action="delete_track",
                track_code=track_code,
                old_status=old_status,
                new_status=""
            )

            await send_or_edit(update, texts['track_deleted'].format(track_code=track_code))
            return

    # ---------- КЛИЕНТ ----------
    else:
        if data == "user_add_track":
            context.user_data["adding_user_track"] = True
            lang = context.user_data.get('language', 'ru')
            texts = TEXTS[lang]
            await send_or_edit(update, texts['enter_track'])
            return

        elif data == "user_my_tracks":
            user_tracks = db.get_user_tracks(user.id)
            lang = context.user_data.get('language', 'ru')
            texts = TEXTS[lang]

            if not user_tracks:
                await send_or_edit(update, texts['no_tracks'], back_button(context))
            else:
                keyboard = []
                for track_info in user_tracks:
                    track_code = track_info['track_code']
                    status = track_info['status']
                    keyboard.append(
                        [InlineKeyboardButton(f"{track_code} ({status})", callback_data=f"user_track_{track_code}")])
                keyboard.append([InlineKeyboardButton(texts['btn_back'], callback_data="back")])
                await send_or_edit(update, texts['my_tracks'],
                                   InlineKeyboardMarkup(keyboard))
            return

        elif data.startswith("user_track_"):
            track_code = data[11:]
            track = db.get_track(track_code)
            lang = context.user_data.get('language', 'ru')
            texts = TEXTS[lang]

            status = track['status'] if track else texts['track_not_found_short']
            await send_or_edit(update, f"📦 Трек: {track_code}\n🔄 Статус: {status}", back_button(context))
            return

        elif data == "fill_data":
            # Начинаем сбор данных
            context.user_data["data_step"] = 0
            context.user_data["user_data"] = {}
            # Получаем язык пользователя
            lang = context.user_data.get('language', 'ru')
            texts = TEXTS[lang]
            # Шаги по порядку
            steps = [
                (texts['form_ask_name'], "name"),
                (texts['form_ask_city'], "city"),
                (texts['form_ask_phone'], "phone")
            ]

            context.user_data["data_steps"] = steps
            await send_or_edit(update, steps[0][0])
            return

        elif data.startswith("user_track_"):
            track_code = data[11:]
            track = db.get_track(track_code)
            status = track['status'] if track else "Не найдено"
            await send_or_edit(update, f"📦 Трек: {track_code}\n🔄 Статус: {status}", back_button(context))
            return


# ==================== СООБЩЕНИЯ ====================
async def messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
Обработчик
текстовых
сообщений
"""
    user = update.message.from_user
    text = update.message.text.strip()

    lang = context.user_data.get('language', 'ru')
    texts = TEXTS[lang]

    # 1. Обработка сбора данных (должен быть ПЕРВЫМ!)
    if "data_step" in context.user_data:
        step = context.user_data["data_step"]
        steps = context.user_data["data_steps"]

        if step < len(steps):
            # Сохраняем ответ
            field_name = steps[step][1]
            context.user_data["user_data"][field_name] = text

            # Увеличиваем шаг
            context.user_data["data_step"] += 1

            # Если ещё есть шаги - спрашиваем следующий
            if context.user_data["data_step"] < len(steps):
                next_step = context.user_data["data_step"]
                await update.message.reply_text(steps[next_step][0])
            else:
                # Все данные собраны - обрабатываем
                await process_form_data(update, context)
        return

    # Ник клиента
    if context.user_data.get("awaiting_nickname"):
        set_nickname(user.id, text)
        context.user_data["awaiting_nickname"] = False

        # Логируем регистрацию
        db.log_action(
            user_id=user.id,
            username=user.username or "",
            action="registration",
            track_code="",
            old_status="",
            new_status=text
        )

        keyboard = [
            [InlineKeyboardButton("📦 Добавить трек", callback_data="user_add_track")],
            [InlineKeyboardButton("📝 Мои треки", callback_data="user_my_tracks")],
            [InlineKeyboardButton("📝 Адрес", callback_data="fill_data")]
        ]
        await update.message.reply_text(f"Приятно познакомиться, {text}! Выберите действие:", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    # Добавление трека клиентом
    if context.user_data.get("adding_user_track"):
        context.user_data["adding_user_track"] = False
        track_code = text.strip().upper()

        # Проверяем, существует ли трек
        track = db.get_track(track_code)
        if track:
            # Проверяем, не подписан ли уже пользователь
            user_tracks = db.get_user_tracks(user.id)
            track_codes = [t['track_code'] for t in user_tracks]

            if track_code not in track_codes:
                db.add_user_track(user.id, track_code)

                # Логируем подписку
                db.log_action(
                    user_id=user.id,
                    username=user.username or "",
                    action="subscribe_track",
                    track_code=track_code,
                    old_status="",
                    new_status=track['status']
                )

                await update.message.reply_text(f"✅ Трек {track_code} добавлен для отслеживания!", reply_markup=back_button(context))
            else:
                await update.message.reply_text("⚠️ Вы уже отслеживаете этот трек.", reply_markup=back_button(context))
        else:
            await update.message.reply_text("❌ Трек не найден в базе.", reply_markup=back_button(context))
        return

    # Добавление нового трека админом
    if context.user_data.get("adding"):
        context.user_data["adding"] = False
        parts = text.strip().split(maxsplit=1)
        if len(parts) != 2:
            await update.message.reply_text("❌ Неверный формат. Используйте: ТРЕК_КОД СТАТУС", reply_markup=back_button(context))
        else:
            track_code, status = parts
            track_code = track_code.upper()
            if db.add_track(track_code, status):
                # Логируем добавление трека
                db.log_action(
                    user_id=user.id,
                    username=user.username or "",
                    action="add_track",
                    track_code=track_code,
                    old_status="",
                    new_status=status
                )
                await update.message.reply_text(f"✅ Трек {track_code} добавлен со статусом {status}", reply_markup=back_button(context))
            else:
                await update.message.reply_text("⚠️ Такой трек уже есть", reply_markup=back_button(context))
        return

    # Добавление нового админа
    if context.user_data.get("adding_admin"):
        context.user_data["adding_admin"] = False
        try:
            new_admin_id = int(text.strip())
            if db.add_admin(new_admin_id, ""):
                # Логируем добавление админа
                db.log_action(
                    user_id=user.id,
                    username=user.username or "",
                    action="add_admin",
                    track_code="",
                    old_status="",
                    new_status=str(new_admin_id)
                )
                await update.message.reply_text(f"✅ Админ {new_admin_id} добавлен!", reply_markup=back_button(context))
            else:
                await update.message.reply_text("⚠️ Этот ID уже есть в списке админов", reply_markup=back_button(context))
        except ValueError:
            await update.message.reply_text("❌ ID должен быть числом", reply_markup=back_button(context))
        return

    # Удаление админа
    if context.user_data.get("removing_admin"):
        context.user_data["removing_admin"] = False
        try:
            remove_id = int(text.strip())
            db.remove_admin(remove_id)

            # Логируем удаление админа
            db.log_action(
                user_id=user.id,
                username=user.username or "",
                action="remove_admin",
                track_code="",
                old_status="",
                new_status=str(remove_id)
            )

            await update.message.reply_text(f"✅ Админ {remove_id} удален!", reply_markup=back_button(context))
        except ValueError:
            await update.message.reply_text("❌ ID должен быть числом", reply_markup=back_button(context))
        return

    # Кастомный статус для трека
    if "custom_status_for" in context.user_data:
        track_code = context.user_data.pop("custom_status_for")
        new_status = text

        old_track = db.get_track(track_code)
        if not old_track:
            await update.message.reply_text("❌ Трек не найден")
            return

        old_status = old_track['status']
        db.update_track_status(track_code, new_status)

        # Логируем изменение статуса
        db.log_action(
            user_id=user.id,
            username=user.username or "",
            action="update_status_custom",
            track_code=track_code,
            old_status=old_status,
            new_status=new_status
        )

        # Уведомляем клиентов
        followers = db.get_track_followers(track_code)
        for follower_id in followers:
            try:
                await context.bot.send_message(follower_id, f"📦 Трек {track_code} обновлён!\nНовый статус: {new_status}")
            except Exception as e:
                print(f"Не удалось отправить уведомление пользователю {follower_id}: {e}")

        await update.message.reply_text(f"✅ Статус трека {track_code} изменён на {new_status}")
        return

    # Если ничего не подошло
    await update.message.reply_text("Я не понимаю эту команду. Напишите /start")

# ==================== ЗАПУСК ====================

def main():
    from aiohttp import web
    import threading
    import asyncio

    async def health_handler(request):
        return web.Response(text='OK')

    def run_server():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        app = web.Application()
        app.router.add_get('/', health_handler)
        # Важно: запускаем без web.run_app, чтобы контролировать цикл
        runner = web.AppRunner(app)
        loop.run_until_complete(runner.setup())
        site = web.TCPSite(runner, '0.0.0.0', 8000)
        loop.run_until_complete(site.start())
        print("✅ Health check сервер запущен на порту 8000")
        loop.run_forever()

    thread = threading.Thread(target=run_server, daemon=True)
    thread.start()
    # === КОНЕЦ КОДА ДЛЯ HEALTH CHECK ===
    

    """
    Основная функция запуска
    """
    print("=" * 50)
    print("🚀 Запуск бота...")
    print(f"✅ Токен: {'Установлен' if BOT_TOKEN else 'НЕ НАЙДЕН'}")
    print("=" * 50)
    
    # Создаем приложение
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, messages))
    application.add_handler(CommandHandler("language", language))
    
    print("✅ Бот запущен и готов к работе!")
    print("📱 Напиши /start в Telegram")
    
    # Запускаем polling (новый стиль)
    application.run_polling(
        drop_pending_updates=True,
        allowed_updates=Update.ALL_TYPES
    )

if __name__ == "__main__":
    try:
        print("🔄 Запуск бота...")
        application = ApplicationBuilder().token(BOT_TOKEN).build()
        
        # Добавляем обработчики
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CallbackQueryHandler(button))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, messages))
        application.add_handler(CommandHandler("language", language))
        
        print("✅ Бот готов к работе!")
        print("📱 Напиши /start в Telegram")
        
        # Простой запуск без лишних параметров
        application.run_polling()
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()












