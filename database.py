import sqlite3


class BotBase:
    """Класс для реализации базы данных и методов для взаимодействия с ней"""

    @staticmethod
    async def check_db_structure():
        """Создаем при первом подключении, а в последующем проверяем, таблицы необходимые для работы бота"""
        with sqlite3.connect('gratitude.db') as connection:
            cursor = connection.cursor()
            # В боте будут использованы двое показателей очков.
            # Один для статуса (нельзя убавить), второй как баланс (можно списать)
            cursor.execute('CREATE TABLE IF NOT EXISTS all_users ('
                           'user_id BIGINT PRIMARY KEY,'
                           'points_count INT,'
                           'points_balance INT,'
                           'user_status VARCHAR(255),'
                           'last_achievement INT);')

            cursor.execute('CREATE TABLE IF NOT EXISTS status ('
                           'status_name VARCHAR(255) UNIQUE ON CONFLICT REPLACE,'
                           'points_need INT PRIMARY KEY);')

            cursor.execute('CREATE TABLE IF NOT EXISTS settings ('
                           'set_name VARCHAR(255) UNIQUE ON CONFLICT REPLACE,'
                           'set_content TEXT);')

            cursor.execute('CREATE TABLE IF NOT EXISTS gratitude_list ('
                           'word VARCHAR(255) UNIQUE ON CONFLICT REPLACE);')

            cursor.execute('CREATE TABLE IF NOT EXISTS chats_list ('
                           'chat_id BIGINT UNIQUE ON CONFLICT REPLACE);')

            connection.commit()

    @staticmethod
    async def add_points(user_id: int, points: int):
        """Функция добавляет очки пользователям"""
        with sqlite3.connect('gratitude.db') as connection:
            cursor = connection.cursor()
            cursor.execute(f'INSERT INTO all_users (user_id, points_count, points_balance)'
                           f'VALUES ({user_id}, {points}, {points})'
                           f'ON CONFLICT (user_id)'
                           f'DO UPDATE SET points_count = all_users.points_count + {points},'
                           f'points_balance = all_users.points_balance + {points};')
            connection.commit()

    @staticmethod
    async def reduce_reputation(user_id: int, rep: int):
        with sqlite3.connect('gratitude.db') as connection:
            """Списание репутации"""
            cursor = connection.cursor()
            cursor.execute(f'UPDATE all_users SET points_count = all_users.points_count - {rep} '
                           f'WHERE user_id = {user_id};')
            connection.commit()

    @staticmethod
    async def drop_user(user_id: int):
        """Удаляем из базы того, кто покинул чат"""
        with sqlite3.connect('gratitude.db') as connection:
            cursor = connection.cursor()
            cursor.execute(f'DELETE FROM all_users WHERE user_id = {user_id};')
            connection.commit()

    @staticmethod
    async def reduce_user_balance(user_id: int, points: int):
        """Списание очков с баланса пользователя """
        with sqlite3.connect('gratitude.db') as connection:
            cursor = connection.cursor()
            cursor.execute(f'UPDATE all_users SET points_balance = all_users.points_balance - {points} '
                           f'WHERE user_id = {user_id};')
            connection.commit()

    @staticmethod
    async def get_user_info(user_id: int):
        """Выдаем всю информацию по пользователю"""
        with sqlite3.connect('gratitude.db') as connection:
            cursor = connection.cursor()
            user_info = cursor.execute(f'SELECT * FROM all_users WHERE user_id = {user_id}').fetchall()
            return user_info[0]  # Так как база возвращает список картежей

    @staticmethod
    async def get_user_points(user_id: int):
        """Очки пользователя"""
        with sqlite3.connect('gratitude.db') as connection:
            try:
                cursor = connection.cursor()
                user_info = cursor.execute(f'SELECT points_count FROM all_users WHERE user_id = {user_id}').fetchall()
                return user_info[0][0]  # Так как база возвращает список картежей
            except IndexError:
                return None

    @staticmethod
    async def get_all_users():
        """Достаем всех юзеров для рейтинга"""
        with sqlite3.connect('gratitude.db') as connection:
            cursor = connection.cursor()
            user_info = cursor.execute(f'SELECT * FROM all_users ORDER BY points_count DESC LIMIT 10').fetchall()
            return user_info

    @staticmethod
    async def get_user_points_status_achievements(user_id: int):
        """Достаем из базы сразу все что нужно для замера достижений и статуса"""
        with sqlite3.connect('gratitude.db') as connection:
            cursor = connection.cursor()
            user_status = cursor.execute(f'SELECT points_count, user_status, last_achievement '
                                         f'FROM all_users WHERE user_id = {user_id}').fetchall()
            return user_status[0]  # Так как база возвращает список картежей

    @staticmethod
    async def set_user_status(user_id: int, status: str):
        """Устанавливаем новый статус пользователю"""
        with sqlite3.connect('gratitude.db') as connection:
            cursor = connection.cursor()
            cursor.execute(f'UPDATE all_users SET user_status = "{status}" WHERE user_id = {user_id};')
            connection.commit()

    @staticmethod
    async def set_last_achievement(user_id: int, last_ach: int):
        """Фиксируем получение порога достижения"""
        with sqlite3.connect('gratitude.db') as connection:
            cursor = connection.cursor()
            cursor.execute(f'UPDATE all_users SET last_achievement = {last_ach} WHERE user_id = {user_id};')
            connection.commit()

    @staticmethod
    async def add_status(status_name: str, points_need: int):
        """Добавление нового статуса в базу"""
        with sqlite3.connect('gratitude.db') as connection:
            cursor = connection.cursor()
            cursor.execute(f'INSERT INTO status (status_name, points_need)'
                           f'VALUES ("{status_name}", {points_need})'
                           f'ON CONFLICT (points_need)'
                           f'DO UPDATE SET status_name = "{status_name}";')
            connection.commit()

    @staticmethod
    async def remove_status(status_name: str):
        """Удаление статуса из БД"""
        with sqlite3.connect('gratitude.db') as connection:
            cursor = connection.cursor()
            cursor.execute(f'DELETE FROM status WHERE status_name = "{status_name}";')
            connection.commit()

    @staticmethod
    async def get_all_status():
        """Достаем все статусы из базы"""
        with sqlite3.connect('gratitude.db') as connection:
            cursor = connection.cursor()
            all_status = cursor.execute(f'SELECT * FROM status').fetchall()
            return all_status

    @staticmethod
    async def set_new_setting(set_name: str, set_content):
        """Устанавливаем настройку"""
        with sqlite3.connect('gratitude.db') as connection:
            cursor = connection.cursor()
            cursor.execute(f'INSERT INTO settings (set_name, set_content) VALUES ("{set_name}", "{set_content}");')
            connection.commit()

    @staticmethod
    async def drop_setting(set_name: str):
        """Удаляем настройку"""
        with sqlite3.connect('gratitude.db') as connection:
            cursor = connection.cursor()
            cursor.execute(f'DELETE FROM settings WHERE set_name = "{set_name}";')
            connection.commit()

    @staticmethod
    async def get_all_settings():
        """Достаем все настройки"""
        with sqlite3.connect('gratitude.db') as connection:
            cursor = connection.cursor()
            all_settings = cursor.execute(f'SELECT * FROM settings').fetchall()
            return all_settings

    @staticmethod
    async def add_gratitude_word(word: str):
        """Добавляем слова благодарности"""
        with sqlite3.connect('gratitude.db') as connection:
            cursor = connection.cursor()
            cursor.execute(f'INSERT INTO gratitude_list (word) VALUES ("{word}");')
            connection.commit()

    @staticmethod
    async def remove_gratitude_word(word: str):
        """Удаляем слова благодарности"""
        with sqlite3.connect('gratitude.db') as connection:
            cursor = connection.cursor()
            cursor.execute(f'DELETE FROM gratitude_list WHERE word = "{word}";')
            connection.commit()

    @staticmethod
    async def get_gratitude_list():
        with sqlite3.connect('gratitude.db') as connection:
            cursor = connection.cursor()
            all_words = cursor.execute(f'SELECT * FROM gratitude_list').fetchall()
            return all_words

    @staticmethod
    async def add_chat(chat_id: int):
        """Добавление чата в БД"""
        with sqlite3.connect('gratitude.db') as connection:
            cursor = connection.cursor()
            cursor.execute(f'INSERT INTO chats_list (chat_id) VALUES ({chat_id});')
            connection.commit()

    @staticmethod
    async def remove_chat(chat_id: int):
        """Удаляем чат из БД"""
        with sqlite3.connect('gratitude.db') as connection:
            cursor = connection.cursor()
            cursor.execute(f'DELETE FROM chats_list WHERE chat_id = {chat_id};')
            connection.commit()

    @staticmethod
    async def get_chats():
        """Достаем все чаты"""
        with sqlite3.connect('gratitude.db') as connection:
            cursor = connection.cursor()
            all_chats = cursor.execute(f'SELECT * FROM chats_list').fetchall()
            return all_chats
