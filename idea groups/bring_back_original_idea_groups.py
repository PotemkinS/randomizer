import os
import shutil


backup_path = '../../common/ideas/original idea groups'
original_path = '../../common/ideas'
if os.path.isdir(backup_path):
    files = os.listdir(backup_path)
    for file in files:
        path = backup_path + '/' + file
        shutil.copy(path, original_path)
        os.remove(path)
    shutil.rmtree(backup_path)