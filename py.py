import sqlite3
import os
from datetime import datetime

class RecipeApp:
    def __init__(self, db_name='recipes.db'):
        self.db_name = db_name
        self.init_db()
    
    def init_db(self):
        """Инициализация базы данных и создание таблиц"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # Таблица рецептов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS recipes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT,
                cooking_time INTEGER,
                difficulty TEXT,
                instructions TEXT,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Таблица ингредиентов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ingredients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                recipe_id INTEGER,
                name TEXT NOT NULL,
                quantity TEXT,
                unit TEXT,
                FOREIGN KEY (recipe_id) REFERENCES recipes (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def clear_screen(self):
        """Очистка экрана терминала"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def display_menu(self):
        """Отображение главного меню"""
        self.clear_screen()
        print("=" * 50)
        print("        ПРИЛОЖЕНИЕ ДЛЯ УПРАВЛЕНИЯ РЕЦЕПТАМИ")
        print("=" * 50)
        print("1. Добавить новый рецепт")
        print("2. Просмотреть все рецепты")
        print("3. Поиск рецептов")
        print("4. Удалить рецепт")
        print("5. Выйти из приложения")
        print("=" * 50)
    
    def add_recipe(self):
        """Добавление нового рецепта"""
        self.clear_screen()
        print("ДОБАВЛЕНИЕ НОВОГО РЕЦЕПТА")
        print("-" * 30)
        
        # Ввод основной информации о рецепте
        name = input("Название рецепта: ")
        category = input("Категория (например, суп, десерт, основное блюдо): ")
        cooking_time = input("Время приготовления (в минутах): ")
        difficulty = input("Сложность (легко/средне/сложно): ")
        
        print("\nВведите инструкции по приготовлению:")
        print("(введите 'конец' на отдельной строке для завершения)")
        instructions_lines = []
        while True:
            line = input()
            if line.lower() == 'конец':
                break
            instructions_lines.append(line)
        
        instructions = '\n'.join(instructions_lines)
        
        # Ввод ингредиентов
        print("\nДОБАВЛЕНИЕ ИНГРЕДИЕНТОВ")
        print("(введите 'готово' для завершения)")
        ingredients = []
        
        while True:
            print(f"\nИнгредиент #{len(ingredients) + 1}:")
            ing_name = input("  Название: ")
            if ing_name.lower() == 'готово':
                break
            
            quantity = input("  Количество: ")
            unit = input("  Единица измерения (г, мл, шт. и т.д.): ")
            
            ingredients.append({
                'name': ing_name,
                'quantity': quantity,
                'unit': unit
            })
        
        # Сохранение в базу данных
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        try:
            # Сохраняем рецепт
            cursor.execute('''
                INSERT INTO recipes (name, category, cooking_time, difficulty, instructions)
                VALUES (?, ?, ?, ?, ?)
            ''', (name, category, cooking_time, difficulty, instructions))
            
            recipe_id = cursor.lastrowid
            
            # Сохраняем ингредиенты
            for ingredient in ingredients:
                cursor.execute('''
                    INSERT INTO ingredients (recipe_id, name, quantity, unit)
                    VALUES (?, ?, ?, ?)
                ''', (recipe_id, ingredient['name'], ingredient['quantity'], ingredient['unit']))
            
            conn.commit()
            print(f"\n✅ Рецепт '{name}' успешно добавлен!")
            
        except Exception as e:
            conn.rollback()
            print(f"\n❌ Ошибка при добавлении рецепта: {e}")
        
        finally:
            conn.close()
        
        input("\nНажмите Enter для продолжения...")
    
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
    
    def search_recipes(self):
        """Поиск рецептов"""
        self.clear_screen()
        print("ПОИСК РЕЦЕПТОВ")
        print("-" * 30)
        print("1. По названию")
        print("2. По категории")
        print("3. По ингредиенту")
        print("4. Назад")
        
        choice = input("\nВыберите вариант поиска: ")
        
        if choice == '1':
            self.search_by_name()
        elif choice == '2':
            self.search_by_category()
        elif choice == '3':
            self.search_by_ingredient()
    
    def search_by_name(self):
        """Поиск по названию"""
        search_term = input("\nВведите название для поиска: ")
        
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, name, category, cooking_time, difficulty 
            FROM recipes 
            WHERE name LIKE ? 
            ORDER BY name
        ''', (f'%{search_term}%',))
        
        self.display_search_results(cursor.fetchall(), f"результаты поиска по '{search_term}'")
        conn.close()
    
    def search_by_category(self):
        """Поиск по категории"""
        # Сначала покажем доступные категории
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('SELECT DISTINCT category FROM recipes WHERE category IS NOT NULL')
        categories = [row[0] for row in cursor.fetchall()]
        
        if categories:
            print("\nДоступные категории:")
            for i, category in enumerate(categories, 1):
                print(f"{i}. {category}")
        
        search_term = input("\nВведите категорию для поиска: ")
        
        cursor.execute('''
            SELECT id, name, category, cooking_time, difficulty 
            FROM recipes 
            WHERE category LIKE ? 
            ORDER BY name
        ''', (f'%{search_term}%',))
        
        self.display_search_results(cursor.fetchall(), f"рецепты в категории '{search_term}'")
        conn.close()
    
    def search_by_ingredient(self):
        """Поиск по ингредиенту"""
        search_term = input("\nВведите ингредиент для поиска: ")
        
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT DISTINCT r.id, r.name, r.category, r.cooking_time, r.difficulty
            FROM recipes r
            JOIN ingredients i ON r.id = i.recipe_id
            WHERE i.name LIKE ?
            ORDER BY r.name
        ''', (f'%{search_term}%',))
        
        self.display_search_results(cursor.fetchall(), f"рецепты с ингредиентом '{search_term}'")
        conn.close()
    
    def display_search_results(self, recipes, title):
        """Отображение результатов поиска"""
        self.clear_screen()
        print(f"РЕЗУЛЬТАТЫ ПОИСКА: {title.upper()}")
        print("-" * 50)
        
        if not recipes:
            print("Рецепты не найдены.")
        else:
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
    
    def view_recipe_details(self, recipe_id):
        """Просмотр детальной информации о рецепте"""
        self.clear_screen()
        
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # Получаем информацию о рецепте
        cursor.execute('SELECT * FROM recipes WHERE id = ?', (recipe_id,))
        recipe = cursor.fetchone()
        
        if not recipe:
            print("Рецепт не найден.")
            conn.close()
            input("\nНажмите Enter для продолжения...")
            return
        
        # Получаем ингредиенты
        cursor.execute('SELECT name, quantity, unit FROM ingredients WHERE recipe_id = ?', (recipe_id,))
        ingredients = cursor.fetchall()
        
        conn.close()
        
        # Отображаем информацию
        id, name, category, cooking_time, difficulty, instructions, created_date = recipe
        
        print(f"РЕЦЕПТ: {name}")
        print("=" * 50)
        print(f"Категория: {category}")
        print(f"Время приготовления: {cooking_time} минут")
        print(f"Сложность: {difficulty}")
        print(f"Добавлен: {created_date}")
        
        print("\nИНГРЕДИЕНТЫ:")
        print("-" * 30)
        for i, (ing_name, quantity, unit) in enumerate(ingredients, 1):
            if unit:
                print(f"{i}. {ing_name} - {quantity} {unit}")
            else:
                print(f"{i}. {ing_name} - {quantity}")
        
        print("\nИНСТРУКЦИЯ ПРИГОТОВЛЕНИЯ:")
        print("-" * 40)
        print(instructions)
        
        print("\n" + "=" * 50)
        input("\nНажмите Enter для продолжения...")
    
    def delete_recipe(self):
        """Удаление рецепта"""
        self.clear_screen()
        print("УДАЛЕНИЕ РЕЦЕПТА")
        print("-" * 30)
        
        # Сначала покажем все рецепты
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('SELECT id, name FROM recipes ORDER BY name')
        recipes = cursor.fetchall()
        conn.close()
        
        if not recipes:
            print("Нет рецептов для удаления.")
            input("\nНажмите Enter для продолжения...")
            return
        
        print("Доступные рецепты:")
        for id, name in recipes:
            print(f"{id}. {name}")
        
        try:
            recipe_id = int(input("\nВведите ID рецепта для удаления: "))
            
            # Подтверждение удаления
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute('SELECT name FROM recipes WHERE id = ?', (recipe_id,))
            recipe_name = cursor.fetchone()
            
            if not recipe_name:
                print("Рецепт с таким ID не найден.")
            else:
                confirm = input(f"Вы уверены, что хотите удалить рецепт '{recipe_name[0]}'? (да/нет): ")
                if confirm.lower() == 'да':
                    # Удаляем ингредиенты сначала (из-за внешнего ключа)
                    cursor.execute('DELETE FROM ingredients WHERE recipe_id = ?', (recipe_id,))
                    cursor.execute('DELETE FROM recipes WHERE id = ?', (recipe_id,))
                    conn.commit()
                    print(f"✅ Рецепт '{recipe_name[0]}' успешно удален!")
                else:
                    print("Удаление отменено.")
            
            conn.close()
            
        except ValueError:
            print("❌ Пожалуйста, введите корректный ID.")
        
        input("\nНажмите Enter для продолжения...")
    
    def run(self):
        """Запуск основного цикла приложения"""
        while True:
            self.display_menu()
            choice = input("Выберите действие (1-5): ")
            
            if choice == '1':
                self.add_recipe()
            elif choice == '2':
                self.view_all_recipes()
            elif choice == '3':
                self.search_recipes()
            elif choice == '4':
                self.delete_recipe()
            elif choice == '5':
                print("\nДо свидания!")
                break
            else:
                print("\n❌ Неверный выбор. Пожалуйста, выберите от 1 до 5.")
                input("Нажмите Enter для продолжения...")

# Запуск приложения
if __name__ == "__main__":
    app = RecipeApp()
    app.run()