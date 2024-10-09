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

            # cursor.execute('CREATE TABLE IF NOT EXISTS ;')
            #
            # cursor.execute('CREATE TABLE IF NOT EXISTS ;')

            connection.commit()

    # f"DO UPDATE SET money_received = s{abs(channel_id)}.money_received + {revenue};")

    @staticmethod
    async def add_points(user_id: int, points: int):
        """Функция добавляет очки пользователям"""
        with sqlite3.connect('gratitude.db') as connection:
            cursor = connection.cursor()
            cursor.execute(f'INSERT INTO all_users (user_id, points_count, points_balance)'
                           f'VALUES ({user_id}, {points}, {points})'
                           f'ON CONFLICT (user_id)'
                           f'DO UPDATE SET points_count = all_users.points_count + {points},'
                           f'points_balance = all_users.points_balance + {points}')
