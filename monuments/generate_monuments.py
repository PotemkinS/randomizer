import os
import random
import shutil


class monument_tier:
    def __init__(self, time, cost, on_upgrade, conditional_modifiers):
        self.time = time
        self.cost = cost
        self.on_upgrade = on_upgrade
        self.conditional_modifiers = conditional_modifiers


class monument:
    def __init__(self, name, start, date, time, cost, movable, move_time, starting_tier, type, build_trigger, on_built, on_destroyed, 
                 can_use, can_upgrade, keep_trigger, tiers):
        self.name = name
        self.start = start
        self.date = date
        self.cost = cost
        self.time = time
        self.movable = movable
        self.move_time = move_time
        self.starting_tier = starting_tier
        self.type = type
        self.build_trigger = build_trigger
        self.on_built = on_built
        self.on_destroyed = on_destroyed
        self.can_use = can_use
        self.can_upgrade = can_upgrade
        self.keep_trigger = keep_trigger
        self.tiers = tiers


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

    local_modifiers = []
    path = '../generate_info/local_modifiers.txt'
    file = open(path, 'r')
    local_modifiers_info = file.readlines()
    file.close()
    for local_modifier in local_modifiers_info:
        local_modifier = local_modifier.replace('\n', '')
        split = local_modifier.split('=')
        local_modifiers.append((split[0], split[1]))

    return modifiers, local_modifiers


def get_monuments_info():
    monuments_info = []
    backup_path = '../../common/great_projects/original great projects'
    dir = '../../common/great_projects'
    files = os.listdir(dir)
    file_name = ''
    os.makedirs(backup_path, exist_ok=True)
    for filename in files:
        file_name = filename
        path = dir + '/' + filename
        if not os.path.isfile(path):
            continue
        file = open(path, 'r', errors='ignore')
        lines = file.readlines()
        file.close()
        parentheses_counter = 0
        open_parentheses = 0
        close_parentheses = 0
        name = ''
        start = ''
        date = ''
        time = ''
        cost = ''
        mobavle = ''
        move_cost = ''
        start_tier = ''
        type = ''
        build_trigger = ''
        on_built = ''
        on_destroyed = ''
        can_use = ''
        can_upgrade = ''
        keep_trigger = ''
        tier_time = ''
        tier_cost = ''
        tier_on_upgrade = ''
        tier_conditional = []
        tiers = []
        in_tier = False
        in_time = False
        in_built_trigger = False
        in_on_built = False
        in_on_destroyed = False
        in_cas_use = False
        in_can_upgrade = False
        in_can_keep = False
        in_tier_time = False
        in_tier_cost = False
        in_tier_on_upgrade = False
        in_tier_conditional = False
        any_multiline = lambda: in_tier or in_time or in_built_trigger or in_on_built or in_on_destroyed or in_cas_use or in_can_upgrade or in_can_keep
        for line in lines:
            copyline = line.replace('\t','').replace(' ','').replace('\n', '')
            if copyline.startswith('#'):
                continue
            open_parentheses = copyline.count('{')
            close_parentheses = copyline.count('}')
            if parentheses_counter == 0 and open_parentheses > 0:
                name = line
            if in_tier or copyline.startswith('tier_'):
                in_tier = True
                if in_tier_conditional or copyline.startswith('conditional_modifier='):
                    in_tier_conditional = True
                    tier_conditional += line
                elif in_tier_time or copyline.startswith('upgrade_time='):
                    in_tier_time = True
                    tier_time += line
                elif in_tier_cost or copyline.startswith('cost_to_upgrade='):
                    in_tier_cost = True
                    tier_cost += line
                elif in_tier_on_upgrade or copyline.startswith('on_upgraded='):
                    in_tier_on_upgrade = True
                    tier_on_upgrade += line
                if in_tier and parentheses_counter + open_parentheses - close_parentheses == 2:
                    in_tier_time = False
                    in_tier_cost = False
                    in_tier_on_upgrade = False
                    in_tier_conditional = False
            elif copyline.startswith('start='):
                start = line
            elif copyline.startswith('date='):
                date = line
            elif in_time or copyline.startswith('time='):
                in_time = True
                time += line
            elif copyline.startswith('build_cost='):
                cost = line
            elif copyline.startswith('can_be_moved='):
                mobavle = line
            elif copyline.startswith('move_days_per_unit_distance='):
                move_cost = line
            elif copyline.startswith('starting_tier='):
                start_tier = line
            elif copyline.startswith('type='):
                type = line
            elif in_built_trigger or copyline.startswith('build_trigger='):
                in_built_trigger = True
                build_trigger += line
            elif in_on_built or copyline.startswith('on_built='):
                in_on_built = True
                on_built += line 
            elif in_on_destroyed or copyline.startswith('on_destroyed='):
                in_on_destroyed = True
                on_destroyed += line
            elif in_cas_use or copyline.startswith('can_use_modifiers_trigger='):
                in_cas_use = True
                can_use += line
            elif in_can_upgrade or copyline.startswith('can_upgrade_trigger='):
                in_can_upgrade = True
                can_upgrade += line
            elif in_can_keep or copyline.startswith('keep_trigger='):
                in_can_keep = True
                keep_trigger += line 
            if any_multiline() and parentheses_counter + open_parentheses - close_parentheses == 1:
                if in_tier:
                    tiers.append(monument_tier(tier_time, tier_cost, tier_on_upgrade, tier_conditional))
                    tier_time = ''
                    tier_cost = ''
                    tier_on_upgrade = ''
                    tier_conditional = []
                in_tier = False
                in_time = False
                in_built_trigger = False
                in_on_built = False
                in_on_destroyed = False
                in_cas_use = False
                in_can_upgrade = False
                in_can_keep = False
            if parentheses_counter > 0 and parentheses_counter + open_parentheses - close_parentheses == 0:
                monuments_info.append(monument(name, start, date, time, cost, mobavle, move_cost, start_tier, type, build_trigger, on_built, on_destroyed, can_use, can_upgrade, keep_trigger, tiers))
                name = ''
                start = ''
                date = ''
                time = ''
                cost = ''
                mobavle = ''
                move_cost = ''
                start_tier = ''
                type = ''
                build_trigger = ''
                on_built = ''
                on_destroyed = ''
                can_use = ''
                can_upgrade = ''
                keep_trigger = ''
                tiers = []
            parentheses_counter += open_parentheses - close_parentheses
        if not os.path.exists(backup_path + '/' + filename):
            shutil.copy(path, backup_path + '/' + filename)
            open(path, 'w').close()
    return monuments_info, file_name


def generate_new_monuments(monuments_info, modifiers, multiplier, add_bonus, additinional_bonus_chance, negative_chance, file_name):
    a = 1 


def get_correct_info(message, error_message):
    while True:
        var = input(message)
        allowed_chars = '0123456789'
        good_var = True
        for char in var:
            if char not in allowed_chars:
                good_var = False
                break
        if  good_var and float(var).is_integer():
            return int(var)
        else:
            print(error_message)


start_tier = ''
max_tier = -1
build_time = ''
min_build_time = 120
max_build_time = 480
build_cost = ''
min_build_cost = 1000
max_build_cost = 5000
unit_specialisation = ''
local_specialisation = ''
movable = ''
available_for_all = ''
normal_random = ''

add_bonus = get_correct_info('how many additional modifiers each idea can have: ')
additinional_bonus_chance = get_correct_info('additional modifier chance, in percent. enter from 0 to 100: ')
negative_chance = get_correct_info('chance for modifier to become negative, in percent. enter from 0 to 100: ')
multiplier = get_correct_info('modifier multriplier: ')

allowed_tiers = [0,1,2,3]
change_tier = input() == '1'
if change_tier:
    while max_start_tier not in allowed_tiers:
        max_start_tier = get_correct_info('')

change_cost = input() == '1'
if change_cost:
    while max_start_tier not in allowed_tiers:
        max_start_tier = get_correct_info('')


modifiers, local_modifiers = get_all_modifiers()
monuments_info, file_name = get_monuments_info()