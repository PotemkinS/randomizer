import os
import random
import shutil
from colorama import Fore
import colorama

colorama.init(autoreset=True)


class monument_tier:
    def __init__(self, time, cost, on_upgrade, conditional_modifiers):
        self.time = time
        self.cost = cost
        self.on_upgrade = on_upgrade
        self.conditional_modifiers = conditional_modifiers


class monument:
    def __init__(self, name, start, date, time, cost, movable, move_time, starting_tier, type, build_trigger, on_built, on_destroyed, 
                 can_use, can_upgrade, keep_trigger, tiers : list[monument_tier]):
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


def get_monuments_info():
    monuments_info = []
    backup_path = '../../common/great_projects/original great projects'
    if os.path.isdir(backup_path) and len(os.listdir(backup_path)) > 0:
        dir = backup_path
    else:
        dir = '../../common/great_projects'
    files = os.listdir(dir)
    file_name = ''
    os.makedirs(backup_path, exist_ok=True)
    for filename in files:
        path = dir + '/' + filename
        if not os.path.isfile(path):
            continue
        file_name = filename
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
        move_cost = '\tmove_days_per_unit_distance = 10\n'
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
                move_cost = '\tmove_days_per_unit_distance = 10\n'
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


def generate_new_monuments(monuments_info : list[monument], file_name, modifiers, change_movable, change_available, change_cost, change_time, change_tier, add_bonus, additinional_bonus_chance, multipliers):
    file_path = f'../../common/great_projects/{file_name}'
    new_monuments = open(file_path, 'w')
    for monument in monuments_info:
        new_monuments.write(monument.name)
        new_monuments.write(monument.start)
        new_monuments.write(monument.date)
        new_monuments.write(monument.type)
        if change_movable[0] and 'canal' not in monument.type:
            if random.randint(1, 100) <= change_movable[1]:
                new_monuments.write('\tcan_be_moved = yes\n')
            else:
                new_monuments.write('\tcan_be_moved = no\n')
        else:
            new_monuments.write(monument.movable)
        new_monuments.write(monument.move_time)
        if change_tier[0]:
            new_monuments.write(f'\tstarting_tier = {random.randint(0, change_tier[1])}\n')
        else:
            new_monuments.write(monument.starting_tier)
        if change_time[0]:
            new_monuments.write(f'\ttime = {{\n\t\tmonth = {random.randint(change_time[1], change_time[2])}\n\t}}\n')
        else:
            new_monuments.write(monument.time)
        if change_cost[0]:
            new_monuments.write(f'\tbuild_cost = {random.randint(change_cost[1], change_cost[2])}\n')
        else:
            new_monuments.write(monument.cost)
        if change_available[0] and random.randint(1, 100) <= change_movable[1]:
            new_monuments.write('\tcan_use_modifiers_trigger = {}\n')
            new_monuments.write('\tcan_upgrade_trigger = {}\n')
        else:
            new_monuments.write(monument.can_upgrade)
            new_monuments.write(monument.can_use)
        new_monuments.write(monument.build_trigger)
        new_monuments.write(monument.keep_trigger)
        new_monuments.write(monument.on_built)
        new_monuments.write(monument.on_destroyed)
        mods = []
        for i in range(add_bonus):
            if random.randint(1, 100) <= additinional_bonus_chance:
                mods.append(random.choice(modifiers))
        mods.append(random.choice(modifiers))
        for i in range(len(monument.tiers)):
            new_monuments.write(f'\n\ttier_{i} = {{\n')
            if change_time[0]:
                new_monuments.write(f'\t\tupgrade_time = {{ months = {random.randint(change_time[1], change_time[2])}}}\n')
            else:
                new_monuments.write(monument.tiers[i].time)
            if change_cost[0]:
                new_monuments.write(f'\t\tcost_to_upgrade = {{ factor = {random.randint(change_cost[1], change_cost[2])}}}\n')
            else:
                new_monuments.write(monument.tiers[i].cost)
            new_monuments.write(monument.tiers[i].on_upgrade)
            for cond in monument.tiers[i].conditional_modifiers:
                new_monuments.write(cond)
            if i > 0:
                new_monuments.write('\t\tcountry_modifiers = {\n')
                for mod in mods:
                    if mod[1] != 'yes':
                        mult = round(float(mod[1])*random.randint(multipliers[i - 1][0], multipliers[i - 1][1]), 3)
                        new_monuments.write(f'\t\t\t{mod[0]} = {mult}\n')
                    else:
                        new_monuments.write(f'\t\t\t{mod[0]} = {mod[1]}\n')
                new_monuments.write('\t\t}\n')
            new_monuments.write('\t}\n')
        new_monuments.write('}\n\n')



def get_integer(message, can_be_negative = False):
    while True:
        var = input(message)
        allowed_chars = '0123456789'
        if can_be_negative:
            allowed_chars = '-0123456789'
        good_var = True
        for char in var:
            if char not in allowed_chars:
                good_var = False
                break
        if  good_var:
            return int(var)
        else:
            if can_be_negative:
                print(Fore.RED + 'number must be integer')
            else:
                print(Fore.RED + 'number must be non-negative integer')


max_start_tier = -1
min_build_time = 120
max_build_time = 480
min_build_cost = 1000
max_build_cost = 5000
movable_chance = -1
available_chance = -1

# print(Fore.GREEN + 'Explanation for the next question.\nThe generation of ideas, policies and units uses random number generation. This means that all numbers between the minimum and maximum have the same chance of being generated. Here I decided to try to add a normal distribution. This means that most modifiers will be “average” and a smaller portion will be too small or too large.\nExample how it was if the minimum number was 1 and the maximum 5 then the probability is 1=2=3=4=5.\nNow the probability with normal distribution is 1<2<3>4>5.')
# gauss_random = input('If you want normal distribution, enter 1. If you enter anything else, the probability of all events will be the same: ')

change_movable = input('If you want to change whether you can move monuments, enter 1: ') == '1'
if change_movable:
    movable_chance = get_integer('chance for monument to be movable in percent. enter from 0 to 100: ')
change_movable = (change_movable, movable_chance)

change_available = input('if you want monuments to have no requirements for use and upgrade enter 1: ') == '1'
if change_available:
    available_chance = get_integer('chance for the monument to have no requirements for use and upgrade in percent. enter from 0 to 100: ')
change_available = (change_available, available_chance)

add_bonus = get_integer('how many additional modifiers each monument can have: ')
additinional_bonus_chance = get_integer('additional modifier chance, in percent. enter from 0 to 100: ')
print('you need to answer 6 questions, two for each tier, what is the minimum and maximum multiplier for the modifiers on that tier.')
multipliers = [[1,1],[1,1],[1,1]]
while True:
    multipliers[0][0] = get_integer('minimum modifier multiplier for tier 1: ', True)
    multipliers[0][1] = get_integer('maximum modifier multiplier for tier 1: ', True)
    if multipliers[0][0] <= multipliers[0][1]:
        break
    else:
        print(Fore.RED + 'max multiplier must be equal to or greater than min multiplier')
while True:
    multipliers[1][0] = get_integer('minimum modifier multiplier for tier 2: ', True)
    multipliers[1][1] = get_integer('maximum modifier multiplier for tier 2: ', True)
    if multipliers[1][0] <= multipliers[1][1]:
        break
    else:
        print(Fore.RED + 'max multiplier must be equal to or greater than min multiplier')
while True:
    multipliers[2][0] = get_integer('minimum modifier multiplier for tier 3: ', True)
    multipliers[2][1] = get_integer('maximum modifier multiplier for tier 3: ', True)
    if multipliers[2][0] <= multipliers[2][1]:
        break
    else:
        print(Fore.RED + 'max multiplier must be equal to or greater than min multiplier')

allowed_tiers = [0,1,2,3]
change_tier = input('if you want make start tier random enter 1: ') == '1'
if change_tier:
    while True:
        max_start_tier = get_integer('enter max possible random start monument tier: ')
        if max_start_tier in allowed_tiers:
            break
        else:
            print(Fore.RED + 'max possible start monument tier can be 0-3')
change_tier = (change_tier, max_start_tier)

change_cost = input('if you want to randomize the build cost enter 1: ') == '1'
if change_cost:
    while True:
        min_build_cost = get_integer('minimum cost: ')
        max_build_cost = get_integer('maximum cost: ')
        if max_build_cost >= min_build_cost:
            break
        else:
            print(Fore.RED + 'max cost must be equal to or greater than min cost')
change_cost = (change_cost, min_build_cost, max_build_cost)

change_time = input('if you want to randomize the build time enter 1: ') == '1'
if change_time:
    while True:
        min_build_time = get_integer('minimum upgrade time in months: ')
        max_build_time = get_integer('maximum upgrade time in months: ')
        if max_build_time >= min_build_time:
            break
        else:
            print(Fore.RED + 'max time must be equal to or greater than min time')
change_time = (change_time, min_build_time, max_build_time)



modifiers = get_all_modifiers()
monuments_info, file_name = get_monuments_info()

generate_new_monuments(monuments_info, file_name, modifiers, change_movable, change_available, change_cost, change_time, change_tier, add_bonus, additinional_bonus_chance, multipliers)