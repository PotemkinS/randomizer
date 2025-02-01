import os
import random
import shutil
from colorama import Fore
import colorama


colorama.init(autoreset=True)


class buff:
    def __init__(self, buff, value, idea_count = 0):
        self.buff = buff
        self.value = value
        self.idea_count = idea_count


class tech_file:
    def __init__(self, points, ahead, techs : list[list[buff]], instituts : list[str], years : list[str], effects : list[str], 
    buffs : list[buff], units : list[list[buff]], ideas_tech : list[str], buildings_and_spy : list[list[buff]], ideas_str : list[str]):
        self.points = points
        self.ideas_tech = ideas_tech
        self.ideas_str = ideas_str
        self.build_and_spy = buildings_and_spy
        self.ahead = ahead
        self.units = units
        self.techs = techs
        self.instituts = instituts
        self.years = years
        self.effects = effects
        self.buffs = buffs


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


def generate_bonus(modifiers, multiplier):
    while True:
        modifier = random.choice(modifiers)
        if modifier[1] == 'yes':
            continue
        else:
            mult = random.randint(1, multiplier)
            value = round(float(modifier[1])*mult,3)
            return (modifier[0], value)


def get_technologies_info(keep_idea, keep_units, keep_buildings):
    technologies_info = []
    backup_path = '../../common/technologies/original technologies'
    if os.path.isdir(backup_path) and len(os.listdir(backup_path)) > 0:
        dir = backup_path
    else:
        dir = '../../common/technologies'
    files = os.listdir(dir)
    os.makedirs(backup_path, exist_ok=True)
    for filename in files:
        path = dir + '/' + filename
        if not os.path.isfile(path):
            continue
        file = open(path, 'r', errors='ignore')
        text = file.read().lower().replace('\t','').replace(' ', '')
        file.seek(0)
        lines = file.readlines()
        file.close()
        points = ''
        if 'monarch_power=adm' in text:
            adm_tech = True
            points = 'monarch_power = ADM\n'
        if 'monarch_power=mil' in text:
            mil_tech = True
            points = 'monarch_power = MIL\n'
        if 'monarch_power=dip' in text:
            dip_tech = True
            points = 'monarch_power = DIP\n'
        if not adm_tech and not dip_tech and not mil_tech:
            continue
        parentheses_counter = 0
        open_parentheses = 0
        close_parentheses = 0
        in_ahead = False
        ahead = ''
        in_institut = False
        institut = ''
        instituts = []
        in_effect = False
        effect = ''
        effects = []
        year = ''
        years = []
        techs = []
        tech_buffs = []
        all_buffs = []
        ideas_tech = []
        ideas_str = []
        ideas = ''
        units = []
        current_tech_units = []
        builings_and_spy = []
        current_tech_b_and_s = []
        in_technology = False
        for line in lines:
            copyline = line.replace('\t','').replace(' ','').replace('\n', '')
            if copyline.startswith('#'):
                continue
            open_parentheses = copyline.count('{')
            close_parentheses = copyline.count('}')
            if copyline.startswith('technology={'):
                 in_technology = True
            elif in_ahead or copyline.startswith('ahead_of_time='):
                in_ahead = True
                ahead += line
            elif copyline.startswith('year='):
                year = line
            elif in_institut or copyline.startswith('expects_institution='):
                in_institut = True
                institut += line
            elif in_effect  or copyline.startswith('effect='):
                in_effect = True
                effect += line
            elif '=' in copyline and in_technology:
                split = copyline.split('=')
                baff = buff(split[0], split[1])
                if split[0] == 'allowed_idea_groups':
                    ideas = line
                    ideas_str.append(ideas)
                if keep_buildings and split[1] == 'yes':
                    current_tech_b_and_s.append(baff)
                elif keep_units and split[0] == 'enable':
                    current_tech_units.append(baff)
                else:
                    tech_buffs.append(baff)
            if parentheses_counter > 0 and parentheses_counter + open_parentheses - close_parentheses == 1:
                in_effect = False
                in_institut = False
            elif parentheses_counter > 0 and parentheses_counter + open_parentheses - close_parentheses == 0:
                if not in_ahead:
                    ideas_tech.append(ideas)
                    ideas = ''
                    instituts.append(institut)
                    institut = ''
                    years.append(year)
                    year = ''
                    effects.append(effect)
                    effect = ''
                    techs.append(tech_buffs)
                    all_buffs += tech_buffs
                    tech_buffs = []
                    units.append(current_tech_units)
                    current_tech_units = []
                    builings_and_spy.append(current_tech_b_and_s)
                    current_tech_b_and_s = []
                in_ahead = False
                in_technology = False
            parentheses_counter += open_parentheses - close_parentheses
        if not os.path.exists(backup_path + '/' + filename):
            shutil.copy(path, backup_path + '/' + filename)
        technologies_info.append(tech_file(points, ahead, techs, instituts, years, effects, all_buffs, units, ideas_tech, builings_and_spy, ideas_str))
    return technologies_info


def generate_new_technologies(technologies_info : list[tech_file], modifiers, randomize_ahead_of_time, ahead_bonus_count, 
                              multiplier, random_order_false_filling_true, keep_idea, keep_units, keep_build_and_spy, even_filling):
    for tech in technologies_info:

        tech_count = len(tech.techs)

        if random_order_false_filling_true:
            if even_filling:
                low = len(tech.buffs)//len(tech.techs)
                spread = [low]*tech_count
                for i in range(tech_count):
                    if sum(spread) < len(tech.buffs):
                        spread[i] += 1
                    else:
                        break
            else:
                spread = [0]*len(tech.techs)
                for _ in range(len(tech.buffs)):
                    spread[random.randint(0, tech_count - 1)] += 1
                random.shuffle(spread)
            buff_per_tech = []
            bonus_str = []
            baff = []
            for i in range(tech_count):
                while True:
                    if len(tech.buffs) > 0 and len(bonus_str) < spread[i]:
                        s = random.choice(tech.buffs)
                        if s.buff != 'enable' and s.buff in bonus_str and s.value != 'yes':
                            index = [y.buff for y in baff].index(s.buff)
                            if s.buff == 'allowed_idea_groups':
                                baff[index].value = s.value
                                baff[index].idea_count += 1
                            else:
                                baff[index].value = float(s.value) + float(baff[index].value)
                        else:
                            baff.append(s)
                        bonus_str.append(s.buff)
                        tech.buffs.remove(s)
                    if len(bonus_str) == spread[i]:
                        buff_per_tech.append(baff)
                        baff = []
                        bonus_str = []
                        break
        else:
            order = []
            while len(order) < tech_count:
                number = random.randint(0, tech_count - 1)
                if number in order:
                    continue
                order.append(number)

        if tech.points == 'monarch_power = ADM\n':
            file_name = 'adm.txt'
        if tech.points == 'monarch_power = MIL\n':
            file_name = 'mil.txt'
        if tech.points == 'monarch_power = DIP\n':
            file_name = 'dip.txt'
        technologies_path = f'../../common/technologies/{file_name}'
        new_technologies = open(technologies_path, 'w')

        new_technologies.write(tech.points)

        if randomize_ahead_of_time:
            ahead_bonuses = []
            for i in range(ahead_bonus_count):
                ahead_bonuses.append(generate_bonus(modifiers, multiplier))
        if randomize_ahead_of_time:
            new_technologies.write('ahead_of_time = {\n')
            for bonus in ahead_bonuses:
                new_technologies.write(f'\t{bonus[0]} = {bonus[1]}\n')
            new_technologies.write('}\n\n')
        else:
            new_technologies.write(tech.ahead)

        for i in range(tech_count):
            new_technologies.write('technology = {\n')
            new_technologies.write(tech.years[i])
            new_technologies.write(tech.instituts[i])
            if keep_build_and_spy:
                for b_and_s in tech.build_and_spy[i]:
                    new_technologies.write(f'\t{b_and_s.buff} = {b_and_s.value}\n')
            if keep_idea and tech.ideas_tech[i] != '':
                idea = tech.ideas_str.pop(0)
                new_technologies.write(idea)
            if keep_units:
                for unit in tech.units[i]:
                    new_technologies.write(f'\t{unit.buff} = {unit.value}\n')
            if random_order_false_filling_true:
                source = buff_per_tech[i]
            else:
                source = tech.techs[order[i]]
            for baff in source:
                if baff.buff == 'allowed_idea_groups' and not keep_idea:
                    for i in range(buff.idea_count):
                        idea = tech.ideas_str.pop(0)
                    new_technologies.write(idea)
                elif baff.buff != 'allowed_idea_groups':
                    new_technologies.write(f'\t{baff.buff} = {baff.value}\n')
            new_technologies.write('}\n\n')
        new_technologies.close()


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


ahead_bonus_count = 0
multiplier = 0
even_filling = False
randomize_ahead_of_time = input('if you want to randomize ahead of time, enter 1: ') == '1'
if randomize_ahead_of_time:
    ahead_bonus_count = get_integer('the number of bonuses ahead of time will contain: ') 
    multiplier = get_integer('modifier multiplier: ')
random_order_false_filling_true = input('if you want to change only the order of technologies but keep the content of technologies enter 1 (if you enter something else all bonuses will be the same but combinations within technologies will be different): ') != '1'
if random_order_false_filling_true:
    even_filling = input('if you want the bonuses to be evenly distributed across technologies enter 1 (otherwise technologies will contain a random number of bonuses): ') == '1'
keep_idea = input('if you want the levels containing ideas to stay the same, enter 1:  ') == '1'
keep_units = input('if you want the levels containing units to stay the same, enter 1: ') == '1'
keep_buildings_and_spy = input('If you want levels containing buildings, diplomatic actions, governments (for those who do not have dharma probably), force march, the ability to drill troops do not change - enter 1: ') == '1'

modifiers = get_all_modifiers()
technologies_info = get_technologies_info(keep_idea, keep_units, keep_buildings_and_spy)
generate_new_technologies(technologies_info, modifiers, randomize_ahead_of_time, ahead_bonus_count, multiplier,
                           random_order_false_filling_true, keep_idea, keep_units, keep_buildings_and_spy, even_filling)