#!/usr/bin/env python3

import re
import json
import subprocess
import unicodedata

def remove_accents(input_str):
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return ''.join([c for c in nfkd_form if not unicodedata.combining(c)])

def execute_command(cmd):
    result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
    return result.stdout.strip()

tags_uid = {}
projects_uid = {}
children_uid = {}
name_uid = {}

energy_uid = {}
priority_uid = {}
estimatedtime_uid = {}

action_uid_list = []
next_uid_list = []

tags = {}
projects = {}

file_path = "projetos.trln"
data = json.load(open(file_path))
for i in data['nodes']:
    if 'Tags' in i['format']:
        tags_uid[i['uid']] = i['data']['Nome']
    if i['format'] == 'Projeto':
        projects_uid[i['uid']] = i['data']['Nome']
    if i['format'] == 'Action':
        action_uid_list.append(i['uid'])
        if 'Energy' in i['data']:
            energy_uid[i['uid']] = i['data']['Energy']
        if 'Priority' in i['data']:
            priority_uid[i['uid']] = i['data']['Priority']
        if 'EstimatedTime' in i['data']:
            estimatedtime_uid[i['uid']] = i['data']['EstimatedTime']

    if i['format'] == 'Next':
        next_uid_list.append(i['uid'])
    children_uid[i['uid']] = i['children']
    name_uid[i['uid']] = i['data']['Nome']

for t in tags_uid:
    s = [t]
    tags[t] = tags_uid[t]
    while s != []:
        k = s.pop()
        for c in children_uid[k]:
            tags[c] = tags[k]
            s.append(c)

for k in action_uid_list:
    energy = energy_uid.get(k, '')
    priority = priority_uid.get(k, '')
    estimatedTime = estimatedtime_uid.get(k, '')
    currentTags = remove_accents(tags.get(k, '').lower().replace(" ", ""))
    if currentTags != '':
        currentTags = '+' + currentTags
    desc = re.sub(r'[()/]', '', name_uid[k])
    output = execute_command(f'task tuid:{k} count')
    if output == '0':
        print(f'Adicionando {k} {desc}')
        execute_command(f'task add {currentTags} {desc} tuid:{k} energy:{energy} priority:{priority} estimated:{estimatedTime}')
    else:
        print(f'Modificando {k} {desc}')
        execute_command(f'task tuid:{k} modify {currentTags} {desc} tuid:{k} energy:{energy} priority:{priority} estimated:{estimatedTime}')

print()
print('Tasks not met anymore on treeline:')
filter_str = " and ".join(f"tuid != {val}" for val in action_uid_list)
subprocess.run(f'task esforco {filter_str}', shell=True)
