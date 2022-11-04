# Food_Blog_Backend
 
Program as a combination of Python and SQL, that creates and modifies tables via SQLite3 module.  
Table *recipes* stores **name**, **description** and **amount** of ingredients (from a list) used to make particular recipe.  
User can add a new recipe or find suitable recipe based on available ingredients and preffered time.  

## How to use

### 1. Add a recipe

User input consists only 1 argument (name_pf_db) in the format: *python* *py_name* *db_name*  
*Example:* `python blog.py food_blog.db`
  
Then program will ask for data about recipe
- name
- description
- meals (format = integers split by white-space, for example `1 2 4`)
- amount (format = *amount* *measure* *ingredient*, for example `250 ml milk`)

**Possible ingredients** = breakfast, brunch, lunch, supper  
**Possible ingredients** = blackberry, blueberry, cacao, milk, strawberry, sugar  
**Possible measures** = ' ' (white-space), cup, dsp, g, l, ml, tbsp, tsp

Press *enter* to exit  

### 2. Pick a recipe

User input consists 3 arguments (name_of_db, ingredients, meals) in the format: *python* *py_name* *db_name* *--ingredients=ing_n* *--meals=meal_n*  
*Example:* `python blog.py food_blog.db --ingredients="sugar,milk" --meals="breakfast,brunch"`.  
Program will proceed to search for recipe with appropriate data.  
