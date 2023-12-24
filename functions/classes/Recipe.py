class Ingredient:
    def __init__(self, token, quantity, reserves):
        self.token = token
        self.quantity = quantity
        self.reserves = reserves

class Recipe:
    def __init__(self, token, ingredients, reserves):
        self.token = token
        self.ingredients = ingredients
        self.reserves = reserves
