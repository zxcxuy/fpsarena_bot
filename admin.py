from database import Database
import sys
import os

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def show_menu():
    clear_screen()
    print("FPS ARENA - Панель администратора")
    print("=" * 40)
    print("1. Показать таблицу пользователей")
    print("2. Статистика базы данных")
    print("3. Очистить экран")
    print("4. Очистить таблицу(не надо)")
    print("5. Выход")
    print("=" * 40)
    

def main():
    db = Database()
    
    while True:
        show_menu()
        choice = input("Выберите действие (1-5): ").strip()
        
        if choice == '1':
            clear_screen()
            print("Таблица пользователей")
            print("=" * 40)
            result = db.show_table(limit=200)
            print(result)
            input("\nНажмите Enter для продолжения...")
        elif choice == '2':
            clear_screen()
            print("Статистика базы данных")
            print("=" * 40)
            try:
                users_count = db.get_user_count()
                notify_users = db.get_user_notify_count()
                stats = f"\nВсего пользователей: {users_count}\nПодписаны на рассылку: {notify_users}\nОхват: {(notify_users/users_count*100 if users_count > 0 else 0):.1f}%"
                print(stats)
                print("=" * 40)
            except ValueError:
                print("Ошибка: введите числовой Chat ID")
            input("\nНажмите Enter для продолжения...")
        elif choice == '3':
            clear_screen()
        elif choice == '4':
            clear_screen()
            print("ВЫ ТОЧНО ХОТИТЕ УДАЛИТЬ ТАБЛИЦУ(НЕ НАДО):")
            answer = input("(Y/N)?: ")
            if answer.lower() == "y":
                db.drop_table()
            elif answer.lower() == "n":
                print("Спасибо")
            else:
                print("Нет такой команды")
            input("\nНажмите Enter для продолжения...")
        # elif choice == '5':
        #     clear_screen()
        #     print("Статистика пулов")
        #     print("=" * 40)
        #     pool_stats = db.get_pool_stats()
        #     if isinstance(pool_stats, dict):
        #         print(f"Имя пула: {pool_stats.get('pool_name', 'N/A')}")
        #         print(f"Размер пула: {pool_stats.get('pool_size', 'N/A')}")
        #         print(f"Доступные соединения: {pool_stats.get('available_connections', 'N/A')}")
        #     else:
        #         print(pool_stats)
        #     print("=" * 40)
        #     input("\nНажмите Enter для продолжения...")
        elif choice == '5':
            print("До свидания!")
            break
        else:
            print("Пока нет такой команды :(")
            input("\nНажмите Enter для продолжения...")
            

if __name__ == "__main__":
    try:
        import tabulate
    except ImportError:
        print("Для работы админ-панели необходимо установить tabulate:")
        print("pip install tabulate")
        sys.exit(1)

    main()
