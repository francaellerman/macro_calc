import csv
from sympy import Symbol, nsolve
import pprint

#class food_dict(dict):
    
#    def protein_energy(self):
#        return self['protein'] / self['calories']

def update_foods() -> dict:
    global foods
    def food_dict(row) -> dict:
        row['mass'] = 1.0
        row['calories'] = float(row['calories'])
        row['protein'] = float(row['protein'])
        return row
    with open('foods.csv') as csvfile:
        foods = {row['name']: food_dict(row) for row in csv.DictReader(csvfile)}

update_foods()

def make_ratio_formulae(food_ratios: dict, field: str, symbol_flag: str) -> tuple:
    global foods
    unit_var = Symbol(f'unit_{symbol_flag}')
    def ratio_formula(symbol: Symbol, ratio: float, field: str):
        return symbol * foods[symbol.name][field] / ratio - unit_var
    return (ratio_formula(symbol, ratio, field) for symbol, ratio in food_ratios.items())

def make_added_formula(input_foods: set, field: str, total: float):
    formulae = {symbol * foods[symbol.name][field] for symbol in input_foods}
    return sum(formulae) - total

def strings_to_symbols(food_dict: dict) -> dict:
    return {Symbol(name, positive=True): ratio for name, ratio in
            food_dict.items()}

def make_meal(high_protein_foods: dict, low_protein_foods: dict, calories:
              float, protein_to_calories: float, ratio_field: str):
    global foods
    high_protein_foods = strings_to_symbols(high_protein_foods)
    low_protein_foods = strings_to_symbols(low_protein_foods)
    input_foods: set = dict(list(high_protein_foods.items()) 
                       + list(low_protein_foods.items())).keys()
    calories_formula = make_added_formula(input_foods, 'calories', calories)
    protein_formula = make_added_formula(input_foods, 'protein', calories
                                         * protein_to_calories)
    high_protein_ratio_formulae: tuple = make_ratio_formulae(high_protein_foods,
                                                      ratio_field, 'high')
    low_protein_ratio_formulae: tuple = make_ratio_formulae(low_protein_foods,
                                                     ratio_field, 'low')
    #Seems like in SymPy you must list _all_ variables for nsolve regardless
    #of whether you want their value
    vars_tuple: tuple = tuple(input_foods) + tuple([Symbol('unit_high'), Symbol('unit_low')])
    formulae: tuple = (calories_formula, protein_formula) + tuple(high_protein_ratio_formulae) + tuple(low_protein_ratio_formulae)
    all_solutions = nsolve(formulae, vars_tuple,
                           tuple([20] * len(vars_tuple)), dict=True)[0]
    pprint.pprint({key.name: all_solutions[key] for key in input_foods})
