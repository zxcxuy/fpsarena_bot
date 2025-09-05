import mysql.connector
from mysql.connector import Error
from tabulate import tabulate
import config
import time

class Database:
    def __init__(self):
        self.pool = config.connection_pool
        self.create_table()
    
    def get_connection(self):
        """Получить соединение из пула"""
        if not self.pool:
            print("Пул соединений не доступен")
            return None
        
        try:
            connection = self.pool.get_connection()
            return connection
        except Error as e:
            print(f"Ошибка получения соединения из пула: {e}")
            return None

    def create_table(self):
        """Создание таблиц если они не существуют"""
        connection = self.get_connection()
        if not connection:
            print("Нет подключения к базе данных")
            return False
            
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        chat_id BIGINT UNIQUE NOT NULL,
                        username VARCHAR(100),
                        first_name VARCHAR(100),
                        last_name VARCHAR(100),
                        notify BOOLEAN DEFAULT TRUE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                """)
                
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS broadcast_content (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        content_text TEXT,
                        file_id VARCHAR(255),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                """)
                
            connection.commit()
            print("Таблицы users и broadcast_content готовы к работе")
            return True
        except Error as e:
            print(f"Ошибка создания таблиц: {e}")
            return False
        finally:
            if connection and connection.is_connected():
                connection.close()
                
    def drop_table(self):
        """Удаление таблицы users"""
        connection = self.get_connection()
        if not connection:
            print("Нет подключения к базе данных")
            return False
            
        try:
            with connection.cursor() as cursor:
                cursor.execute("DROP TABLE IF EXISTS users")
            connection.commit()
            print("Таблица users удалена")
            return True
        except Error as e:
            print(f"Ошибка удаления таблицы: {e}")
            return False
        finally:
            if connection and connection.is_connected():
                connection.close()
                
    def show_table(self, limit=100):
        """Показать таблицу пользователей"""
        connection = self.get_connection()
        if not connection:
            return "Нет подключения к базе данных"
            
        try:
            with connection.cursor() as cursor:
                cursor.execute(f"""
                    SELECT 
                        id,
                        chat_id,
                        COALESCE(username, 'N/A') as username,
                        COALESCE(first_name, 'N/A') as first_name,
                        COALESCE(last_name, 'N/A') as last_name,
                        CASE WHEN notify THEN '+' ELSE '-' END as notify,
                        DATE_FORMAT(created_at, '%d.%m.%Y %H:%i') as created
                    FROM users 
                    ORDER BY created_at DESC 
                    LIMIT {limit}
                """)
                rows = cursor.fetchall()
                
                if rows:
                    pretty_columns = ['ID', 'Chat ID', 'Username', 'Имя', 'Фамилия', 'Рассылка', 'Дата регистрации']
                    table = tabulate(
                        rows, 
                        headers=pretty_columns,
                        tablefmt='grid',
                        stralign='left',
                        numalign='left'
                    )
                    return table
                else:
                    return "Таблица пользователей пуста"
        except Error as e:
            return f"Ошибка при получении данных: {e}"
        finally:
            if connection and connection.is_connected():
                connection.close()

    def add_user(self, chat_id, username=None, first_name=None, last_name=None):
        """Добавление или обновление пользователя"""
        connection = self.get_connection()
        if not connection:
            print("Нет подключения к базе данных")
            return False
            
        try:
            with connection.cursor() as cursor:
                # Проверяем существование пользователя
                cursor.execute("SELECT id FROM users WHERE chat_id = %s", (chat_id,))
                existing_user = cursor.fetchone()
                
                if existing_user:
                    # Обновляем существующего пользователя
                    cursor.execute("""
                        UPDATE users 
                        SET username = COALESCE(%s, username),
                            first_name = COALESCE(%s, first_name),
                            last_name = COALESCE(%s, last_name)
                        WHERE chat_id = %s
                    """, (username, first_name, last_name, chat_id))
                else:
                    # Добавляем нового пользователя
                    cursor.execute("""
                        INSERT INTO users (chat_id, username, first_name, last_name, notify)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (chat_id, username, first_name, last_name, True))
                    
            connection.commit()
            return True
        except Error as e:
            print(f"Ошибка добавления/обновления пользователя: {e}")
            return False
        finally:
            if connection and connection.is_connected():
                connection.close()
                
    def toggle_user_notify(self, chat_id):
        """Переключение статуса рассылки"""
        connection = self.get_connection()
        if not connection:
            print("Нет подключения к базе данных")
            return None
            
        try:
            with connection.cursor() as cursor:
                # Получаем текущий статус
                cursor.execute("SELECT notify FROM users WHERE chat_id = %s", (chat_id,))
                result = cursor.fetchone()
                
                if result is None:
                    print(f"Пользователь с chat_id {chat_id} не найден")
                    return None
                    
                current_status = result[0]
                new_status = not current_status
                
                # Обновляем статус
                cursor.execute(
                    "UPDATE users SET notify = %s WHERE chat_id = %s",
                    (new_status, chat_id)
                )
                
            connection.commit()
            print(f"Рассылка для пользователя {chat_id} {'включена' if new_status else 'выключена'}")
            return new_status
            
        except Error as e:
            print(f"Ошибка переключения рассылки: {e}")
            return None
        finally:
            if connection and connection.is_connected():
                connection.close()

    def get_user_count(self):
        """Получение количества пользователей"""
        connection = self.get_connection()
        if not connection:
            print("Нет подключения к базе данных")
            return 0
            
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM users")
                count = cursor.fetchone()[0]
                return count
        except Error as e:
            print(f"Ошибка получения количества пользователей: {e}")
            return 0
        finally:
            if connection and connection.is_connected():
                connection.close()
                
    def get_user_notify_count(self):
        """Получение количества пользователей с включенной рассылкой"""
        connection = self.get_connection()
        if not connection:
            print("Нет подключения к базе данных")
            return 0
            
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM users WHERE notify = TRUE")
                count = cursor.fetchone()[0]
                return count
        except Error as e:
            print(f"Ошибка получения количества пользователей подписанных на рассылку: {e}")
            return 0
        finally:
            if connection and connection.is_connected():
                connection.close()
                
    def get_users_notify(self):
        """Получение пользователей с включенной рассылкой"""
        connection = self.get_connection()
        if not connection:
            print("Нет подключения к базе данных")
            return []
            
        try:
            with connection.cursor(dictionary=True) as cursor:
                cursor.execute("SELECT chat_id FROM users WHERE notify = TRUE")
                users = cursor.fetchall()
                return users
        except Error as e:
            print(f"Ошибка получения пользователей: {e}")
            return []
        finally:
            if connection and connection.is_connected():
                connection.close()
                
    def save_broadcast_content(self, content_text=None, file_id=None):
        """Сохранение контента рассылки"""
        connection = self.get_connection()
        if not connection:
            print("Нет подключения к базе данных")
            return False
            
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO broadcast_content (content_text, file_id)
                    VALUES (%s, %s)
                """, (content_text, file_id))
                
            connection.commit()
            content_id = cursor.lastrowid
            print(f"Контент рассылки сохранен (ID: {content_id})")
            return content_id
        except Error as e:
            print(f"Ошибка сохранения контента рассылки: {e}")
            return False
        finally:
            if connection and connection.is_connected():
                connection.close()

    def get_last_broadcast_content(self, limit=1):
        """Получение последнего контента рассылки"""
        connection = self.get_connection()
        if not connection:
            print("Нет подключения к базе данных")
            return []
            
        try:
            with connection.cursor(dictionary=True) as cursor:
                cursor.execute("""
                    SELECT 
                        id,
                        content_text,
                        file_id,
                        created_at,
                        CASE 
                            WHEN file_id IS NOT NULL AND content_text IS NOT NULL THEN 'photo_text'
                            WHEN file_id IS NOT NULL THEN 'photo'
                            ELSE 'text'
                        END as content_type
                    FROM broadcast_content 
                    ORDER BY created_at DESC 
                    LIMIT %s
                """, (limit,))
                
                content = cursor.fetchall()
                return content
        except Error as e:
            print(f"Ошибка получения контента рассылок: {e}")
            return []
        finally:
            if connection and connection.is_connected():
                connection.close()

    def close(self):
        """Закрытие пула соединений (вызывается при завершении работы)"""
        try:
            if self.pool:
                self.pool.close()
                print("Пул соединений закрыт")
        except Exception as e:
            print(f"Ошибка при закрытии пула соединений: {e}")
            
    def get_pool_stats(self):
        """Получение статистики пула соединений"""
        if not self.pool:
            return "Пул не инициализирован"
            
        try:
            stats = {
                "pool_name": self.pool.pool_name,
                "pool_size": self.pool.pool_size,
                "available_connections": getattr(self.pool, '_cnx_queue', {}).qsize() if hasattr(self.pool, '_cnx_queue') else "N/A"
            }
            return stats
        except Exception as e:
            return f"Ошибка получения статистики пула: {e}"