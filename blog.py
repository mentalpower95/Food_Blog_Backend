import sqlite3
import argparse


def arguments():
    parser = argparse.ArgumentParser(description="Accepts database name and optional values")
    parser.add_argument("db_name", help="Database name")
    parser.add_argument("--ingredients", type=str, help="List of ingredients split by ','")
    parser.add_argument("--meals", type=str, help="List of meals split by ','")
    return parser.parse_args()


class FoodBlog:

    def __init__(self, database, ingredients, meals):
        self.data = {"meals": ("breakfast", "brunch", "lunch", "supper"),
                     "ingredients": ("milk", "cacao", "strawberry", "blueberry", "blackberry", "sugar"),
                     "measures": ("ml", "g", "l", "cup", "tbsp", "tsp", "dsp", "")}
        self.conn = sqlite3.connect(database)
        self.cur = self.conn.cursor()
        self.ingredients = ingredients
        self.meals = meals
        self.create_tables()

    def create_tables(self):
        if len(self.cur.execute('''SELECT name FROM sqlite_master WHERE type='table';''').fetchall()):
            return
        self.cur.execute("PRAGMA foreign_keys = ON")
        self.cur.execute('''CREATE TABLE IF NOT EXISTS meals (
                         meal_id INTEGER PRIMARY KEY,
                         meal_name TEXT UNIQUE NOT NULL);
                         ''')
        self.cur.execute('''CREATE TABLE IF NOT EXISTS ingredients (
                         ingredient_id INTEGER PRIMARY KEY,
                         ingredient_name TEXT UNIQUE NOT NULL);
                         ''')
        self.cur.execute('''CREATE TABLE IF NOT EXISTS measures (
                         measure_id INTEGER PRIMARY KEY,
                         measure_name TEXT UNIQUE);
                         ''')
        self.cur.execute('''CREATE TABLE IF NOT EXISTS recipes (
                         recipe_id INTEGER PRIMARY KEY,
                         recipe_name TEXT NOT NULL,
                         recipe_description TEXT);
                         ''')
        self.cur.execute('''CREATE TABLE IF NOT EXISTS serve (
                         serve_id INTEGER PRIMARY KEY,
                         recipe_id INTEGER NOT NULL,
                         meal_id INTEGER NOT NULL,
                         FOREIGN KEY(recipe_id) REFERENCES recipes(recipe_id),
                         FOREIGN KEY(meal_id) REFERENCES meals(meal_id));
                         ''')
        self.cur.execute('''CREATE TABLE IF NOT EXISTS quantity (
                         quantity_id INTEGER PRIMARY KEY,
                         measure_id INTEGER NOT NULL,
                         ingredient_id INTEGER NOT NULL,
                         quantity INTEGER NOT NULL,
                         recipe_id INTEGER NOT NULL,
                         FOREIGN KEY (measure_id) REFERENCES measures(measure_id),
                         FOREIGN KEY (ingredient_id) REFERENCES ingredients(ingredient_id),
                         FOREIGN KEY (recipe_id) REFERENCES recipes(recipe_id));
                         ''')

        for table in self.data.keys():
            for n in range(len(self.data[table])):
                self.cur.execute(f"INSERT INTO {table} VALUES ({n + 1}, '{self.data[table][n]}')")

        self.conn.commit()

    def add_recipe(self):
        while True:
            print("Pass the empty recipe name to exit.")
            new_name = input("Recipe name: ")
            if new_name == "":
                break
            else:
                new_description = input("Recipe description: ")
            last_row = self.cur.execute(f"INSERT INTO recipes (recipe_name, recipe_description) "
                                        f"VALUES ('{new_name}', '{new_description}');").lastrowid
            self.proposed_meals(last_row)
            self.quantity_of_ingredient(last_row)
            self.conn.commit()
        self.conn.close()

    def proposed_meals(self, recipe):
        print("1) breakfast  2) brunch  3) lunch  4) supper")
        new_meals = [int(i) for i in input("When the dish can be served: ").split(" ")]
        for meal in new_meals:
            self.cur.execute(f"INSERT INTO serve (recipe_id, meal_id)"
                             f"VALUES ({recipe}, {meal});")

    def quantity_of_ingredient(self, recipe):
        while True:
            values = input("Input quantity of ingredients <press enter to stop>: ")
            if values == "":
                break
            else:
                values = [x for x in values.split(" ")]
            if len(values) == 2:
                values.insert(1, "")
                measure_check = 1
            else:
                measure_check = self.cur.execute(f"SELECT COUNT(*) FROM measures "
                                                 f"WHERE measure_name LIKE '%{values[1]}%';").fetchone()[0]
            ingredient_check = self.cur.execute(f"SELECT COUNT(*) FROM ingredients "
                                                f"WHERE ingredient_name LIKE '%{values[2]}%';").fetchone()[0]

            if measure_check != 1 or ingredient_check != 1:
                print("The ingredient is not conclusive!")
            else:
                m_id = self.cur.execute(f'''SELECT measure_id FROM measures 
                                        WHERE measure_name LIKE '%{values[1]}%';''').fetchone()[0]
                i_id = self.cur.execute(f'''SELECT ingredient_id FROM ingredients 
                                        WHERE ingredient_name LIKE '%{values[2]}%';''').fetchone()[0]
                self.cur.execute(f'''INSERT INTO quantity (quantity, recipe_id, measure_id, ingredient_id) 
                                 VALUES ({values[0]}, {recipe}, {m_id}, {i_id});''')

    def find_recipes(self):
        ingredients, meals = self.ingredients.split(','), self.meals.split(',')
        self.cur.execute(
            '''CREATE VIEW IF NOT EXISTS all_tables AS 
            SELECT * FROM meals AS m
            JOIN serve AS s ON m.meal_id=s.meal_id
            JOIN recipes AS r ON s.recipe_id=r.recipe_id
            JOIN quantity AS q ON r.recipe_id=q.recipe_id
            JOIN ingredients AS i ON q.ingredient_id=i.ingredient_id;'''
        )

        start_query = """SELECT recipe_name FROM all_tables AS a 
        WHERE ingredient_name = '{}'""".format(ingredients[0])

        exists_query = """AND EXISTS (SELECT recipe_name FROM all_tables 
        WHERE ingredient_name = '{}' AND recipe_name = a.recipe_name)"""

        meals = "', '".join(meals)
        ingredients = " ".join([exists_query.format(x) for x in ingredients[1:]])
        full_query = f"""{start_query} {ingredients} AND meal_name in ('{meals}') ORDER BY recipe_name;"""
        recipes = self.cur.execute(full_query).fetchall()
        if len(recipes) > 0:
            suitable_recipes = ", ".join([x[0] for x in recipes])
            print(f'Recipes selected for you: {suitable_recipes}')
        else:
            print('There are no such recipes in the database.')

        self.conn.close()


if __name__ == '__main__':
    args = arguments()
    food_blog_backend = FoodBlog(args.db_name, args.ingredients, args.meals)
    if food_blog_backend.ingredients is None:
        food_blog_backend.add_recipe()
    else:
        food_blog_backend.find_recipes()
