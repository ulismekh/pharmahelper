
def generate_recipe(items):
    """
    Формирует учебный рецепт из списка препаратов.
    """

    recipe = []

    for index, item in enumerate(items, start=1):
        drug = item["drug"]

        recipe.append({
            "number": index,
            "name": drug.name,
            "latin_name": drug.latin_name,
            "latin_genitive": drug.latin_genitive,
            "dosage_form": item["dosage_form"],
            "dose": item["dose"],
            "quantity": item["quantity"],
            "instructions": item["instructions"],
        })

    return recipe
