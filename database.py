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
                           'user_status VARCHAR(255));')

            cursor.execute('CREATE TABLE IF NOT EXISTS status ('
                           'status_name VARCHAR(255) PRIMARY KEY,'
                           'points_need INT);')
            #
            # cursor.execute('CREATE TABLE IF NOT EXISTS ;')

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
    async def add_status(status_name: str, points_need: int):
        """Добавление нового статуса в базу"""
        with sqlite3.connect('gratitude.db') as connection:
            cursor = connection.cursor()
            cursor.execute(f'INSERT INTO status (status_name, points_need)'
                           f'VALUES ("{status_name}", {points_need})'
                           f'ON CONFLICT (status_name)'
                           f'DO UPDATE SET points_need = {points_need};')
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
