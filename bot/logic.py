import json
import os
import shutil
# use your path here
catalog1 = 'your path'


def create_dirs(dir, user):
    os.chdir(f'{catalog1}')
    if not os.path.isdir(f'{user}'):
        os.mkdir(f'{user}')
    os.chdir(f'{catalog1}\\{user}')
    if not os.path.isdir(f'{dir}'):
        os.mkdir(f'{dir}')
    os.chdir(f'{catalog1}\\{user}\\{dir}')


def del_dir(first, second):
    shutil.rmtree(path=first)
    shutil.rmtree(path=second)


with open('languages.json', 'r', encoding='UTF-8') as data:
    data = json.load(data)
