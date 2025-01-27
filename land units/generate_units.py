import random
import os
import shutil
from colorama import Fore
import colorama

colorama.init()

def get_unit_info(path):
    tech_group = ''
    type = ''
    trigger = ''
    parentheses_counter = 0
    open_parentheses = 0
    close_parentheses = 0
    in_trigger = False
    file = open(path, 'r', errors='ignore')
    lines = file.readlines()
    file.close()
    for line in lines:
        line = line.lower().replace('\t', '').replace(' ','').replace('\n', '')
        if line.startswith('#'):
            continue
        if 'unit_type=' in line:
            tech_group = line[10:]
        elif 'type=' in line:
            type = line[5:]
            if type == 'heavy_ship' or type == 'light_ship' or type == 'galley' or type == 'transport':
                return False, 1
        if in_trigger or 'trigger=' in line:
            in_trigger = True
            open_parentheses = line.count('{')
            close_parentheses = line.count('}')
            trigger +=line
            parentheses_counter += open_parentheses - close_parentheses
            if parentheses_counter == 0:
                in_trigger = False
    return True, (os.path.basename(path), type, tech_group, trigger)


def get_all_units():
    backup_path = '../../common/units/original units'
    if not os.path.isdir(backup_path):
        os.makedirs(backup_path, exist_ok=True)
    dir = '../../common/units'
    units = {}
    files = os.listdir(dir)
    for filename in files:
        path = dir + '/' + filename
        if not os.path.isfile(path):
            continue
        add, unit = get_unit_info(path)
        if not os.path.exists(backup_path + '/' + filename) and add:
            shutil.copy(path, backup_path + '/' + filename)
            print(path)
        if add:
            units[filename[:-4]] = unit
            os.remove(path)
    return units

def get_correct_info(message):
    while True:
        var = input(Fore.YELLOW + message)
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
            print(Fore.RED + 'all numbers must be positive integers(except minimum pips which may be zero)')


def get_tech_group_to_unit(units):
    dir = '../../common/technologies'
    files = os.listdir(dir)
    for filename in files:
        path = dir + '/' + filename
        if not os.path.isfile(path):
            continue
        file = open(path, 'r', errors='ignore')
        text = file.read().lower().replace('\t', '').replace(' ', '')
        file.seek(0)
        if 'monarch_power=mil' in text:
            tech = -1
            tech_group_to_unit = {}
            tech_group_techs = {}
            lines = file.readlines()
            for line in lines:
                if line.startswith('#'):
                    continue
                line = line.lower().replace('\t', '').replace(' ', '').replace('\n', '')
                if 'technology={' in line:
                    tech += 1
                elif line.startswith('enable='):
                    unit_name = line[7:]
                    if unit_name in units:
                        tech_group = units[unit_name][2]
                        if tech_group in tech_group_to_unit:
                            tech_group_to_unit[tech_group][unit_name] = tech
                            unit_type = units[unit_name][1]
                            match unit_type:
                                case 'infantry':
                                    tech_group_techs[tech_group][0].add(tech)
                                case 'cavalry':
                                    tech_group_techs[tech_group][1].add(tech)
                                case 'artillery':
                                    tech_group_techs[tech_group][2].add(tech)
                        else:
                            tech_group_to_unit[tech_group] = {unit_name: tech}
                            tech_group_techs[tech_group] = [set(),set(),set()]
                            unit_type = units[unit_name][1]
                            match unit_type:
                                case 'infantry':
                                    tech_group_techs[tech_group][0].add(tech)
                                case 'cavalry':
                                    tech_group_techs[tech_group][1].add(tech)
                                case 'artillery':
                                    tech_group_techs[tech_group][2].add(tech)
    all_tech_groups = []
    for group in tech_group_techs:
        all_tech_groups.append(group)
        inf = list(tech_group_techs[group][0])
        cav = list(tech_group_techs[group][1])
        art = list(tech_group_techs[group][2])
        tech_group_techs[group] = [inf, cav, art]
    on_action_path = '../../common/on_actions/random_force_unit_switch.txt'
    if not os.path.isdir('../../common/on_actions'):
        os.mkdir('../../common/on_actions')
    if len(all_tech_groups) > 1:
        if os.path.isfile(on_action_path):
            os.remove(on_action_path)
        file = open(on_action_path, 'w')
        file.write('on_mil_tech_taken = {\n')
        for i in range(len(all_tech_groups)):
            if all_tech_groups[i] == '':
                continue
            if i == len(all_tech_groups) - 1:
                old_group = all_tech_groups[i]
                new_group = all_tech_groups[i - 1]
            else:
                old_group = all_tech_groups[i]
                new_group = all_tech_groups[i + 1]
            if new_group == '' or new_group == old_group:
                new_group = all_tech_groups[0]
                if new_group == '' or new_group == old_group:
                    new_group = all_tech_groups[1]
                elif (new_group == '' or new_group == old_group) and len(all_tech_groups) > 2:
                    new_group = all_tech_groups[2]
                else:
                    continue
            file.write(f'\tif = {{\n\t\tlimit = {{\n\t\t\tunit_type = {old_group}\n\t\t}}\n\t\tchange_unit_type = {new_group}\n\t\tchange_unit_type = {old_group}\n\t}}\n')
        file.write('}')
        file.close()
    return tech_group_to_unit, tech_group_techs, tech + 1


def add_next_tech(units, tech_group_to_unit, tech_group_techs, max_tech):
    new_units = {}
    for unitname in units:
        tech_group = units[unitname][2]
        if tech_group not in tech_group_to_unit or unitname not in tech_group_to_unit[tech_group]:
            continue
        tech = tech_group_to_unit[tech_group][unitname]
        unit_type = units[unitname][1]
        match unit_type:
            case 'infantry':
                type = 0
            case 'cavalry':
                type = 1
            case 'artillery':
                type = 2
        tech_index = tech_group_techs[tech_group][type].index(tech)
        if tech_index < len(tech_group_techs[tech_group][type]) - 1:
            next_tech = tech_group_techs[tech_group][type][tech_index + 1]
        else:
            next_tech = max_tech
        new_units[unitname] = (units[unitname][0], units[unitname][1], units[unitname][2], units[unitname][3], next_tech)
    return new_units
        

def generate_units(units, charachteristics, min_pips, max_pips, min_manpower, max_manpower, 
               max_cav_maneuver, max_inf_maneuver, max_art_maneuver):
    dir = '../../common/units'
    for unitname in units:
        unit = units[unitname]
        path = dir + '/' + unit[0]
        file = open(path, 'w')
        file.write(f'type = {unit[1]}\nunit_type = {unit[2]}\n')
        for ch in charachteristics:
            file.write(f'{ch} = {random.randint(min_pips, max_pips)}\n')
        if min_manpower != 1 or max_manpower != 1:
            file.write(f'manpower = {random.randint(min_manpower, max_manpower)/1000.0}\n')
        maneuvr = ''
        type = unit[1]
        if max_inf_maneuver != 'classic':
            if type == 'infantry':
                maneuvr = random.randint(1, max_inf_maneuver)
            if type =='cavalry':
                maneuvr = random.randint(1, max_cav_maneuver)
            if type =='artillery':
                maneuvr = random.randint(1, max_art_maneuver)
        else:
            if type == 'infantry':
                maneuvr = 1
            if type =='cavalry':
                maneuvr = 2
            if type =='artillery':
                maneuvr = 1
        file.write(f'maneuver = {maneuvr}\n')
        if unit[3] == '':
            file.write(f'trigger = {{\n\tNOT = {{\n\t\tmil_tech = {unit[4]}\n\t}}\n}}')
        else:
            file.write(unit[3])
        file.close()


min_pips = 0
max_pips = 0
while True:
    min_pips = get_correct_info('minimum number of pips for units: ')
    max_pips = get_correct_info('maximum number of pips for units(maximum is 11 set by game): ')
    if min_pips <= max_pips:
        break
    else:
        print(Fore.RED + 'min pips should be lower or equal to max pips')

charachteristics = ['offensive_morale','defensive_morale', 'offensive_fire', 
                    'defensive_fire', 'offensive_shock','defensive_shock']

add_maneuvr = input(Fore.YELLOW + 'if you want to randomize the flanking range enter 1 otherwise enter something else: ')
if add_maneuvr == '1':
    print(Fore.GREEN + '1 is minimum. enter the maximum for each unit type')
    print(Fore.GREEN + 'base game inf = 1, cav = 2, art = 1')
    max_inf_maneuver = get_correct_info('infrantry maximum flanking range: ')
    max_cav_maneuver = get_correct_info('cavalry maximum flanking range: ')
    max_art_maneuver = get_correct_info('artillery maximum flanking range: ')
else:
    max_cav_maneuver = 'classic'
    max_inf_maneuver = 'classic'
    max_art_maneuver = 'classic'

print(Fore.GREEN + 'the next option can be fun but weird.')
add_manpower = input(Fore.YELLOW + 'If you want to randomize the size of the regiments, enter 1, otherwise enter something else: ')
if add_manpower == '1':
    print(Fore.GREEN + 'in base game all regiments is 1000')
    while True:
        min_manpower = get_correct_info('enter a positive integer number of soldiers in the regiment, which will be the minimum for example 300: ')
        max_manpower= get_correct_info('enter a positive integer number of soldiers in the regiment, which will be the maximum for example 1500: ')
        if min_manpower > 0 and max_manpower >= min_manpower:
            break
        else:
            print(Fore.RED + 'min manpower should be more than 0 and lower or equal to max manpower')
else:
    min_manpower = 1000
    max_manpower = 1000

units = get_all_units()
tech_group_to_unit, tech_group_techs, max_tech = get_tech_group_to_unit(units)
units = add_next_tech(units, tech_group_to_unit, tech_group_techs, max_tech)

generate_units(units, charachteristics, min_pips, max_pips, min_manpower, max_manpower, 
               max_cav_maneuver, max_inf_maneuver, max_art_maneuver)