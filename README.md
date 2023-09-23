# TLTWFeeder

Python tool to sync action itens from TreeLine to TaskWarrior tasks

**CAUTION: This tool is still under development and has not been thoroughly tested. It may not behave as expected, so use it with extreme caution and always back up your data.**

# Introduction

This tool is useful for who use:

1. [TreeLine](https://github.com/doug-101/TreeLine)
2. [TaskWarrior](https://github.com/GothenburgBitFactory/taskwarrior)
3. GTD: Getting Things Done

- TreeLine is an useful tool that provide a hierarchical view of itens
- TaskWarrior is an incredible task management tool
- GTD is a productivity method

## TreeLine setup

This tool supposes that the user uses TreeLine with nodes that are associated with actions (or tasks).

These nodes in TreeLine should be of the type 'Action' with 4 fields:

1. Nome (text type)
2. Energy (choose type 'L/M/H')
3. Priority (choose type 'L/M/H')
4. EstimatedTime (numeric '#')

As TaskWarrior uses tags concept, which can be associated with 'context' in GTD terminology, the user can add TreeLine Action nodes inside any node that has the string 'Tags'. The field 'Nome' of these 'Tags' nodes will be propagated to all descendants. For example, if the user has a node with type 'Tags' and the field 'Nome' with 'Computer', then all descendants Action nodes will have +Computer when translated to taskwarrior. If there are multiple 'Tags' nodes, only one is used.

## TaskWarrior setup

Now, in order to match TaskWarrior tasks, TreeLine action itens and GTD actions, one should add three UDA fields on TaskWarrior: energy and estimated time to accomplish the task, and tuid (the TreeLine unique identifier). They can be defined as follow in .taskrc:

```bash
uda.energy.type=string
uda.energy.label=energy
uda.energy.values=H,M,L

uda.estimated.type=numeric
uda.estimated.label=estimated

uda.tuid.type=string
uda.tuid.label=TreeLine
```

## What it does

updateTaskWarrior.py check, for each Action itens, if it is already on TaskWarrior using the TreeLine UID (tuid). In this case, the TaskWarrior task is updated. Otherwise, a new task is added. After that, updateTaskWarrior.py output all TaskWarrior itens that do not have their 'tuid' in TreeLine (this is useful as you can just delete directly on TreeLine and with this list, mark all of them as done on TaskWarrior).