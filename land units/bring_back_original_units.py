import os
import shutil


backup_path = '../../common/units/original units'
original_path = '../../common/units'
on_action_path = '../../common/on_actions/random_force_unit_switch.txt'
if os.path.isdir(backup_path):
    files = os.listdir(backup_path)
    for file in files:
        path = backup_path + '/' + file
        shutil.copy(path, original_path)
        os.remove(path)
        print(path)
    shutil.rmtree(backup_path)
    os.remove(on_action_path)