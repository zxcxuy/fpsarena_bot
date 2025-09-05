import mysql.connector
from mysql.connector import pooling

DB_CONFIG = {
    'port': 3306,
    'host': '127.0.0.1',
    'user': 'a1160348_fpsbot',
    'database': 'a1160348_fpsbot',
    'password': 'ujdAbLZ4'
}

try:
    connection_pool = pooling.MySQLConnectionPool(
        pool_name="fpsarena_pool",
        pool_size=10,
        host=DB_CONFIG['host'],
        database=DB_CONFIG['database'],
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password'],
        port=DB_CONFIG['port'],
        pool_reset_session=True,
        autocommit=True
    )
    print("Пул соединений успешно создан")
except:
    print("Ошибка создания пула соединений")
    connection_pool = None

TOKENS = {
    "test": '6695763786:AAEfIpSlWcwvJ5igqfTDvFYIf2omx4lfaOA',
    "main": '7847362610:AAG-hjbWWf4sV3XnLL80fJ9jMNq3iYza9-4'
}

admins = [1291104485, 5626687400, 1804140510]