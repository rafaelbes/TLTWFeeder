#!/usr/bin/env python3

import re
import json
import subprocess
import unicodedata
from datetime import datetime
from collections import deque
from typing import List
from datetime import datetime, time

def convert_to_taskwarrior_format(date_str):
    dt = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S.%f')
    tw_format = dt.strftime('%Y-%m-%dT%H:%M:%S')
    return tw_format

def remove_accents(input_str):
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return ''.join([c for c in nfkd_form if not unicodedata.combining(c)])

def execute_command(cmd):
    result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
    return result.stdout.strip()

tags_uid = {}
projects_uid = {}
hide_projects_uid = {}
children_uid = {}
name_uid = {}

energy_uid = {}
priority_uid = {}
estimatedtime_uid = {}
duedatetime_uid = {}
horariocomercial_uid = {}

action_uid_list = []
next_uid_list = []
wait_uid_list = []
check_uid_list = []

tags = {}
hide = {}

# Get the current datetime
current_datetime = datetime.now()
is_weekday = current_datetime.weekday() in range(0, 5)
is_working_hours = time(8, 0) <= current_datetime.time() <= time(16, 0)
is_weekday_and_working_hours = is_weekday and is_working_hours

file_path = "/home/rafael/projetos.trln"
data = json.load(open(file_path))
for i in data['nodes']:
    current_uid = i['uid']
    if 'Tags' in i['format']:
        tags_uid[current_uid] = i['data']['Nome']
    if i['format'] == 'Project':
        projects_uid[current_uid] = i['data']['Nome']
    if i['format'] == 'HideProject' or i['format'] == 'RedProject':
        hide_projects_uid[current_uid] = i['data']['Nome']
    if i['format'] == 'Espera':
        wait_uid_list.append(current_uid)
    if i['format'] == 'Checagem':
        check_uid_list.append(current_uid)
    if i['format'] == 'Action':
        action_uid_list.append(current_uid)
        #print(f'Detected action: {i["data"]}')
        if 'Energy' in i['data']:
            energy_uid[current_uid] = i['data']['Energy']
        if 'Priority' in i['data']:
            priority_uid[current_uid] = i['data']['Priority']
        if 'EstimatedTime' in i['data']:
            estimatedtime_uid[current_uid] = i['data']['EstimatedTime']
        if 'DueDateTime' in i['data']:
            if i['data']['DueDateTime'] == '':
                duedatetime_uid[current_uid] = ''
            else:
                duedatetime_uid[current_uid] = convert_to_taskwarrior_format(i['data']['DueDateTime'])
        if 'HorarioComercial' in i['data']:
            print(f"Horario comercial em {i['data']['Nome']}")
            horariocomercial_uid[current_uid] = (i['data']['HorarioComercial'] == 'True')
    if i['format'] == 'Next':
        next_uid_list.append(current_uid)

    children_uid[current_uid] = i['children']
    name_uid[current_uid] = i['data']['Nome']

print(f'Horario comercial: {is_weekday_and_working_hours}')

for uid in tags_uid:
    s = [uid]
    tags[uid] = tags_uid[uid]
    while s != []:
        k = s.pop()
        for c in children_uid[k]:
            tags[c] = tags[k]
            s.append(c)

for uid in hide_projects_uid:
    s = [uid]
    hide[uid] = True
    while s != []:
        k = s.pop()
        for c in children_uid[k]:
            hide[c] = True
            s.append(c)

hidden_msgs = []
blocked_msgs = []
added_msgs = []
modified_msgs = []

for k in action_uid_list:
    energy = energy_uid.get(k, '')
    priority = priority_uid.get(k, '')
    estimatedTime = estimatedtime_uid.get(k, '')
    duedatetime = duedatetime_uid.get(k, '')
    currentTags = remove_accents(tags.get(k, '').lower().replace(" ", ""))
    if currentTags != '':
        currentTags = '+' + currentTags
    hide_property = hide.get(k, False)
    desc = re.sub(r'[()/]', '', name_uid[k])

    if hide_property:
        hidden_msgs.append(f'H {k} {desc[:50]}')
        wait = 'someday'
    elif len(children_uid[k]) > 0:
        blocked_msgs.append(f'B {k} {desc[:50]}')
        wait = 'someday'
    else:
        wait = ''

    if not is_weekday_and_working_hours and horariocomercial_uid.get(k, False):
        wait = 'someday'

    output = execute_command(f'task tuid:{k} count')
    if output == '0':
        added_msgs.append(f'+ {k} {desc[:50]}')
        execute_command(f'task add {currentTags} {desc} tuid:{k} energy:{energy} priority:{priority} estimated:{estimatedTime} due:{duedatetime} wait:{wait}')
    else:
        modified_msgs.append(f'M {k} {desc[:50]}')
        execute_command(f'task tuid:{k} modify {currentTags} {desc} tuid:{k} energy:{energy} priority:{priority} estimated:{estimatedTime} due:{duedatetime} wait:{wait}')

print()
print('++ Hidden tasks:')
for i in hidden_msgs:
    print(i)

print()
print('++ Blocked tasks:')
for i in blocked_msgs:
    print(i)

print()
print('++ Added tasks:')
for i in added_msgs:
    print(i)

print()
print('++ Wait list:')
for k in wait_uid_list:
    desc = re.sub(r'[()/]', '', name_uid[k])
    print(f'- {desc}')

print()
print('++ Check list:')
for k in check_uid_list:
    desc = re.sub(r'[()/]', '', name_uid[k])
    print(f'- {desc}')

print()
print('++ Tasks not met anymore on treeline:')
filter_str = " and ".join(f"tuid != {val}" for val in action_uid_list)
subprocess.run(f'task esforco {filter_str}', shell=True)
