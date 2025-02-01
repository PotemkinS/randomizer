import os
import random
import shutil


def is_idea_groups_file(text):
    text = text.lower().replace('\t', '').replace(' ','')
    adm = 'category=adm'
    dip = 'category=dip'
    mil = 'category=mil'
    return adm in text or dip in text or mil in text


def generate_bonus(modifiers, multiplier, negative_chance):
    modifier = random.choice(modifiers)
    negative =  random.randint(1, 100) <= negative_chance
    while modifier[1] == 'yes' and negative:
         modifier == random.choice(modifiers)
    if modifier[1] != 'yes':
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


def get_ideas_info():
    ideas_info = []
    backup_path = '../../common/ideas/original idea groups'
    if os.path.isdir(backup_path) and len(os.listdir(backup_path)) > 0:
        dir = backup_path
        files = os.listdir(dir)
    else:
        dir = '../../common/ideas'
        files = os.listdir(dir)
    os.makedirs(backup_path, exist_ok=True)
    file_name = ''
    for filename in files:
        path = dir + '/' + filename
        if not os.path.isfile(path):
            continue
        file = open(path, 'r', errors='ignore')
        if not is_idea_groups_file(file.read()):
            continue
        file_name = filename
        file.seek(0)
        lines = file.readlines()
        file.close()
        parentheses_counter = 0
        open_parentheses = 0
        close_parentheses = 0
        in_trigger = False
        name = ''
        category = ''
        trigger = ''
        ideas = []
        for line in lines:
            line = line.replace('\t', '').replace(' ','')
            if line.startswith('#'):
                continue
            open_parentheses = line.count('{')
            close_parentheses = line.count('}')
            if 'category=' in line:
                category = f'\t{line}'
            if parentheses_counter == 0 and open_parentheses > 0:
                name = line
            elif in_trigger or line.startswith('trigger='):
                in_trigger = True
                trigger += f'\t{line}'
            elif parentheses_counter == 1 and open_parentheses > 0 and not line.startswith('bonus=') and not line.startswith('ai_will_do='):
                ideas.append(f'\t{line}')
            if parentheses_counter > 1 and  in_trigger and parentheses_counter + open_parentheses - close_parentheses == 1:
                in_trigger = False
            if parentheses_counter > 0 and parentheses_counter + open_parentheses - close_parentheses == 0:
                ideas_info.append((name, category, trigger, ideas))
                name = ''
                category = ''
                trigger = ''
                ideas = []
            parentheses_counter += open_parentheses - close_parentheses
        if not os.path.exists(backup_path + '/' + filename):
            shutil.copy(path, backup_path + '/' + filename)
            open(path, 'w').close()
    return ideas_info, file_name


def generate_new_ideas(ideas_info, modifiers, multiplier, add_bonus, additinional_bonus_chance, negative_chance, file_name):
    ideas_path = f'../../common/ideas/{file_name}'
    new_ideas = open(ideas_path, 'w')
    for ideas in ideas_info:
        new_ideas.write(ideas[0])
        new_ideas.write(ideas[1])
        new_ideas.write(ideas[2])
        bonus = generate_bonus(modifiers, multiplier, negative_chance)
        new_ideas.write(f'\tbonus = {{\n\t\t{bonus[0]} = {bonus[1]}\n\t}}\n')
        for idea in ideas[3]:
            bonus = generate_bonus(modifiers, multiplier, negative_chance)
            new_ideas.write(idea)
            new_ideas.write(f'\t{bonus[0]} = {bonus[1]}\n')
            for i in range(add_bonus):
                if random.randint(1, 100) <= additinional_bonus_chance:
                    bonus = generate_bonus(modifiers, multiplier, negative_chance)
                    new_ideas.write(f'\t{bonus[0]} = {bonus[1]}\n')
            new_ideas.write('\t}\n')
        new_ideas.write('\n\tai_will_do={factor=1}\n}\n\n')
    new_ideas.close()


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


add_bonus = get_correct_info('how many additional modifiers each idea can have: ')
additinional_bonus_chance = get_correct_info('additional modifier chance, in percent. enter from 0 to 100: ')
negative_chance = get_correct_info('chance for modifier to become negative, in percent. enter from 0 to 100: ')
multiplier = get_correct_info('modifier multiplier: ')

modifiers = get_all_modifiers()
ideas_info, file_name = get_ideas_info()

generate_new_ideas(ideas_info, modifiers, multiplier, add_bonus, additinional_bonus_chance, negative_chance, file_name)