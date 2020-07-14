import spoonacular as sp
api = sp.API("7c521b34d4db4e29b629e6f340cb15f1")


ing = ["chicken", "lettuce", "tomato"]
response = api.search_recipes_by_ingredients(ingredients = ing, number = 1)
data = response.json()
print(data)

print("=====INSTRUCTIONS===== \n ")
response = api.get_analyzed_recipe_instructions(id = (data[0]["id"]))
inst = response.json()
print(inst)

print("=====URL===== \n ")
response = api.get_recipe_information(id = (data[0]["id"]))
url = response.json()
print(url["sourceUrl"])