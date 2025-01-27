import os
import shutil
import pathlib


backup_path = '../../common/ideas/original idea groups'
original_path = '../../common/ideas'
if os.path.isdir(backup_path):
    os.remove(f'../../common/ideas/0000000000_{os.path.basename(pathlib.Path(os.getcwd()).parent.parent)}_random_idea_groups47.txt')
    files = os.listdir(backup_path)
    for file in files:
        path = backup_path + '/' + file
        shutil.copy(path, original_path)
        os.remove(path)
    shutil.rmtree(backup_path)