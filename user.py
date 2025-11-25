import sqlite3
import os
from datetime import datetime

class RecipeViewerApp:
    def __init__(self, db_name='recipes.db'):
        self.db_name = db_name
        self.check_database()
    
    def check_database(self):
        """Проверка существования базы данных"""
        if not os.path.exists(self.db_name):
            print("❌ База данных рецептов не найдена!")
            print("Пожалуйста, сначала создайте базу данных с рецептами.")
            exit()
    
    def clear_screen(self):
        """Очистка экрана терминала"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def display_menu(self):
        """Отображение главного меню"""
        self.clear_screen()
        print("=" * 50)
        print("        ПРОСМОТР РЕЦЕПТОВ")
        print("=" * 50)
        print("1. Просмотреть все рецепты")
        print("2. Поиск рецептов по названию")
        print("3. Поиск рецептов по категории")
        print("4. Поиск рецептов по ингредиенту")
        print("5. Показать все категории")
        print("6. Выйти из приложения")
        print("=" * 50)
    
    def view_all_recipes(self):
        """Просмотр всех рецептов"""
        self.clear_screen()
        print("ВСЕ РЕЦЕПТЫ")
        print("-" * 50)
        
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, name, category, cooking_time, difficulty 
            FROM recipes 
            ORDER BY name
        ''')
        
        recipes = cursor.fetchall()
        
        if not recipes:
            print("Рецепты не найдены.")
        else:
            print(f"Найдено рецептов: {len(recipes)}\n")
            for recipe in recipes:
                id, name, category, cooking_time, difficulty = recipe
                print(f"{id}. {name}")
                print(f"   Категория: {category} | Время: {cooking_time} мин | Сложность: {difficulty}")
                print()
        
        conn.close()
        
        # Опция просмотра деталей рецепта
        if recipes:
            choice = input("Введите ID рецепта для подробного просмотра (или Enter для возврата): ")
            if choice.isdigit():
                self.view_recipe_details(int(choice))
        else:
            input("\nНажмите Enter для продолжения...")
    
    def search_by_name(self):
        """Поиск по названию"""
        self.clear_screen()
        print("ПОИСК РЕЦЕПТОВ ПО НАЗВАНИЮ")
        print("-" * 35)
        
        search_term = input("Введите название для поиска: ")
        
        if not search_term.strip():
            print("❌ Пожалуйста, введите текст для поиска.")
            input("\nНажмите Enter для продолжения...")
            return
        
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, name, category, cooking_time, difficulty 
            FROM recipes 
            WHERE name LIKE ? 
            ORDER BY name
        ''', (f'%{search_term}%',))
        
        recipes = cursor.fetchall()
        conn.close()
        
        self.display_search_results(recipes, f"результаты поиска по '{search_term}'")
    
    def search_by_category(self):
        """Поиск по категории"""
        self.clear_screen()
        print("ПОИСК РЕЦЕПТОВ ПО КАТЕГОРИИ")
        print("-" * 35)
        
        # Сначала покажем доступные категории
        categories = self.get_categories()
        if categories:
            print("\nДоступные категории:")
            for category in categories:
                print(f"  - {category}")
        
        search_term = input("\nВведите категорию для поиска: ")
        
        if not search_term.strip():
            print("❌ Пожалуйста, введите категорию для поиска.")
            input("\nНажмите Enter для продолжения...")
            return
        
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, name, category, cooking_time, difficulty 
            FROM recipes 
            WHERE category LIKE ? 
            ORDER BY name
        ''', (f'%{search_term}%',))
        
        recipes = cursor.fetchall()
        conn.close()
        
        self.display_search_results(recipes, f"рецепты в категории '{search_term}'")
    
    def search_by_ingredient(self):
        """Поиск по ингредиенту"""
        self.clear_screen()
        print("ПОИСК РЕЦЕПТОВ ПО ИНГРЕДИЕНТУ")
        print("-" * 38)
        
        search_term = input("Введите ингредиент для поиска: ")
        
        if not search_term.strip():
            print("❌ Пожалуйста, введите ингредиент для поиска.")
            input("\nНажмите Enter для продолжения...")
            return
        
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT DISTINCT r.id, r.name, r.category, r.cooking_time, r.difficulty
            FROM recipes r
            JOIN ingredients i ON r.id = i.recipe_id
            WHERE i.name LIKE ?
            ORDER BY r.name
        ''', (f'%{search_term}%',))
        
        recipes = cursor.fetchall()
        conn.close()
        
        self.display_search_results(recipes, f"рецепты с ингредиентом '{search_term}'")
    
    def get_categories(self):
        """Получение списка всех категорий"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('SELECT DISTINCT category FROM recipes WHERE category IS NOT NULL ORDER BY category')
        categories = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        return categories
    
    def show_all_categories(self):
        """Показать все категории и рецепты в них"""
        self.clear_screen()
        print("ВСЕ КАТЕГОРИИ РЕЦЕПТОВ")
        print("-" * 35)
        
        categories = self.get_categories()
        
        if not categories:
            print("Категории не найдены.")
            input("\nНажмите Enter для продолжения...")
            return
        
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        for i, category in enumerate(categories, 1):
            print(f"\n{i}. КАТЕГОРИЯ: {category}")
            print("-" * 30)
            
            cursor.execute('''
                SELECT id, name, cooking_time, difficulty 
                FROM recipes 
                WHERE category = ? 
                ORDER BY name
            ''', (category,))
            
            recipes = cursor.fetchall()
            
            if recipes:
                for recipe in recipes:
                    id, name, cooking_time, difficulty = recipe
                    print(f"   {id}. {name} ({cooking_time} мин, {difficulty})")
            else:
                print("   Рецепты не найдены")
        
        conn.close()
        
        # Опция просмотра деталей рецепта
        choice = input("\nВведите ID рецепта для подробного просмотра (или Enter для возврата): ")
        if choice.isdigit():
            self.view_recipe_details(int(choice))
    
    def display_search_results(self, recipes, title):
        """Отображение результатов поиска"""
        self.clear_screen()
        print(f"РЕЗУЛЬТАТЫ ПОИСКА: {title.upper()}")
        print("-" * 50)
        
        if not recipes:
            print("Рецепты не найдены.")
        else:
            print(f"Найдено рецептов: {len(recipes)}\n")
            for recipe in recipes:
                id, name, category, cooking_time, difficulty = recipe
                print(f"{id}. {name}")
                print(f"   Категория: {category} | Время: {cooking_time} мин | Сложность: {difficulty}")
                print()
        
        # Опция просмотра деталей рецепта
        if recipes:
            choice = input("Введите ID рецепта для подробного просмотра (или Enter для возврата): ")
            if choice.isdigit():
                self.view_recipe_details(int(choice))
        else:
            input("\nНажмиte Enter для продолжения...")
    
    def view_recipe_details(self, recipe_id):
        """Просмотр детальной информации о рецепте"""
        self.clear_screen()
        
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # Получаем информацию о рецепте
        cursor.execute('SELECT * FROM recipes WHERE id = ?', (recipe_id,))
        recipe = cursor.fetchone()
        
        if not recipe:
            print("❌ Рецепт не найден.")
            conn.close()
            input("\nНажмите Enter для продолжения...")
            return
        
        # Получаем ингредиенты
        cursor.execute('SELECT name, quantity, unit FROM ingredients WHERE recipe_id = ? ORDER BY id', (recipe_id,))
        ingredients = cursor.fetchall()
        
        conn.close()
        
        # Отображаем информацию
        id, name, category, cooking_time, difficulty, instructions, created_date = recipe
        
        print(f"🍳 РЕЦЕПТ: {name}")
        print("=" * 60)
        print(f"📁 Категория: {category}")
        print(f"⏱️  Время приготовления: {cooking_time} минут")
        print(f"🎯 Сложность: {difficulty}")
        print(f"📅 Добавлен: {created_date}")
        
        print("\n🛒 ИНГРЕДИЕНТЫ:")
        print("-" * 30)
        if ingredients:
            for i, (ing_name, quantity, unit) in enumerate(ingredients, 1):
                if quantity and unit:
                    print(f"  {i}. {ing_name} - {quantity} {unit}")
                elif quantity:
                    print(f"  {i}. {ing_name} - {quantity}")
                else:
                    print(f"  {i}. {ing_name}")
        else:
            print("  Ингредиенты не указаны")
        
        print("\n👨‍🍳 ИНСТРУКЦИЯ ПРИГОТОВЛЕНИЯ:")
        print("-" * 40)
        if instructions:
            print(instructions)
        else:
            print("Инструкция не указана")
        
        print("\n" + "=" * 60)
        
        # Дополнительные опции
        print("\nДополнительные опции:")
        print("1. Вернуться к списку рецептов")
        print("2. Поиск другого рецепта")
        print("3. Выйти в главное меню")
        
        choice = input("\nВыберите действие (1-3): ")
        
        if choice == '1':
            # Возврат к предыдущему списку не реализован для простоты
            pass
        elif choice == '2':
            self.search_by_name()
    
    def get_statistics(self):
        """Получение статистики по рецептам"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # Общее количество рецептов
        cursor.execute('SELECT COUNT(*) FROM recipes')
        total_recipes = cursor.fetchone()[0]
        
        # Количество категорий
        cursor.execute('SELECT COUNT(DISTINCT category) FROM recipes WHERE category IS NOT NULL')
        total_categories = cursor.fetchone()[0]
        
        # Самый быстрый рецепт
        cursor.execute('SELECT name, cooking_time FROM recipes WHERE cooking_time IS NOT NULL ORDER BY cooking_time LIMIT 1')
        fastest_recipe = cursor.fetchone()
        
        conn.close()
        
        return {
            'total_recipes': total_recipes,
            'total_categories': total_categories,
            'fastest_recipe': fastest_recipe
        }
    
    def show_welcome_screen(self):
        """Показать приветственный экран со статистикой"""
        self.clear_screen()
        print("=" * 60)
        print("             ДОБРО ПОЖАЛОВАТЬ В КОЛЛЕКЦИЮ РЕЦЕПТОВ!")
        print("=" * 60)
        
        stats = self.get_statistics()
        
        print(f"\n📊 Статистика:")
        print(f"   Всего рецептов: {stats['total_recipes']}")
        print(f"   Всего категорий: {stats['total_categories']}")
        
        if stats['fastest_recipe']:
            name, time = stats['fastest_recipe']
            print(f"   Самый быстрый рецепт: '{name}' ({time} минут)")
        
        print("\n" + "=" * 60)
        input("\nНажмите Enter для продолжения...")
    
    def run(self):
        """Запуск основного цикла приложения"""
        self.show_welcome_screen()
        
        while True:
            self.display_menu()
            choice = input("Выберите действие (1-6): ")
            
            if choice == '1':
                self.view_all_recipes()
            elif choice == '2':
                self.search_by_name()
            elif choice == '3':
                self.search_by_category()
            elif choice == '4':
                self.search_by_ingredient()
            elif choice == '5':
                self.show_all_categories()
            elif choice == '6':
                print("\nДо свидания! Приятного аппетита! 🍽️")
                break
            else:
                print("\n❌ Неверный выбор. Пожалуйста, выберите от 1 до 6.")
                input("Нажмите Enter для продолжения...")

# Запуск приложения
if __name__ == "__main__":
    app = RecipeViewerApp()
    app.run()
    