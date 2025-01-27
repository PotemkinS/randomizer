import os
import random
import shutil
import pathlib

def generate_bonus(modifiers, multiplier, negative_chance):
    modifier = random.choice(modifiers)

    if modifier[1] != 'yes':
        negative =  random.randint(1, 100) <= negative_chance
        mult = random.randint(1, multiplier)
        value = round(float(modifier[1])*mult,3)
        if negative:
            value *= -1
        return (modifier[0], value)
    return modifier


def get_all_modifiers():
    modifiers = []
    path = '../generate_info/modifiers.txt'
    file = open(path, 'r')
    modifiers_info = file.readlines()
    file.close()
    for modifier in modifiers_info:
        modifier = modifier.replace('\n', '')
        split = modifier.split('=')
        modifiers.append((split[0], split[1]))
    return modifiers


def get_correct_info(message):
    while True:
        var = input(message)
        temp_var = var.lstrip('+')
        allowed_chars = '0123456789'
        good_var = True
        for char in temp_var:
            if char not in allowed_chars:
                good_var = False
                break
        if  good_var and float(var).is_integer():
            return int(var)
        else:
            print('number must be integer, positive(for multiplier) or non-negative(for additional modifier chance, negative modifier chance or additional bonus)')


def get_policies_info():
    policies_info = []
    backup_path = '../../common/policies/original policies'
    if os.path.isdir(backup_path) and len(os.listdir(backup_path)) > 0:
        dir = backup_path
        files = os.listdir(dir)
    else:
        dir = '../../common/policies'
        files = os.listdir(dir)
    os.makedirs(backup_path, exist_ok=True)
    for filename in files:
        path = dir + '/' + filename
        if not os.path.isfile(path):
            continue
        file = open(path, 'r', errors='ignore')
        lines = file.readlines()
        file.close()
        parentheses_counter = 0
        open_parentheses = 0
        close_parentheses = 0
        in_potential = False
        in_allow = False
        name = ''
        allow = ''
        potential = ''
        points = ''
        for line in lines:
            line = line.lower().replace('\t', '').replace(' ','')
            if line.startswith('#'):
                continue
            open_parentheses = line.count('{')
            close_parentheses = line.count('}')
            if parentheses_counter == 0 and open_parentheses > 0:
                name = line
            if line.startswith('monarch_power='):
                points = f'\t{line}\n'
            if in_potential or line.startswith('potential='):
                in_potential = True
                potential += f'\t{line}'
            if in_allow or line.startswith('allow='):
                in_allow = True
                allow += f'\t{line}'
            if parentheses_counter > 1 and (in_potential or in_allow) and parentheses_counter + open_parentheses - close_parentheses == 1:
                in_allow = False
                in_potential = False
            if parentheses_counter > 0 and parentheses_counter + open_parentheses - close_parentheses == 0:
                policies_info.append((name, points, potential, allow))
                name = ''
                allow = ''
                potential = ''
                points = ''
            parentheses_counter += open_parentheses - close_parentheses
        if not os.path.exists(backup_path + '/' + filename):
            shutil.copy(path, backup_path + '/' + filename)
            os.remove(path)
    return policies_info


def generate_new_policies(policies_info, modifiers, multiplier, add_bonus, additinional_bonus_chance, negative_chance):
    policies_path = f'../../common/policies/0000000000_{os.path.basename(pathlib.Path(os.getcwd()).parent.parent)}_random_policies47.txt'
    new_policies = open(policies_path, 'w')
    for policy in policies_info:
        new_policies.write(policy[0])
        new_policies.write(policy[1])
        new_policies.write(policy[2])
        new_policies.write(policy[3])
        bonus = generate_bonus(modifiers, multiplier, negative_chance)
        new_policies.write(f'\n\t{bonus[0]} = {bonus[1]}\n')
        for i in range(add_bonus):
            if random.randint(1, 100) <= additinional_bonus_chance:
                bonus = generate_bonus(modifiers, multiplier, negative_chance)
                new_policies.write(f'\t{bonus[0]} = {bonus[1]}\n')
        new_policies.write('\n\tai_will_do={factor=1}\n}\n\n')
    new_policies.close()


add_bonus = get_correct_info('how many additional modifiers each policy can have: ')
additinional_bonus_chance = get_correct_info('additional modifier chance, in percent. enter from 0 to 100: ')
negative_chance = get_correct_info('chance for modifier to become negative, in percent. enter from 0 to 100: ')
multiplier = get_correct_info('modifier multriplier: ')

modifiers = get_all_modifiers()
policies_info = get_policies_info()

generate_new_policies(policies_info, modifiers, multiplier, add_bonus, additinional_bonus_chance, negative_chance)