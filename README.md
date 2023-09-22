# TLTWFeeder
Python tool to sync action itens from TreeLine to TaskWarrior tasks

# Introduction

This tool is useful for who use:

1. [TreeLine](https://github.com/doug-101/TreeLine)
2. [TaskWarrior](https://github.com/GothenburgBitFactory/taskwarrior)
3. GTD: Getting Things Done

- TreeLine is an useful tool that provide a hierarchical view of itens
- TaskWarrior is an incredible task management tool
- GTD is a produtivity method

## TreeLine setup

This tool supposes that the user uses TreeLine with nodes that are associated with actions (or tasks).

These nodes in TreeLine should be of the type 'Action' with 4 fields:

1. Nome (text type)
2. Energy (choose type 'L/M/H')
3. Priority (choose type 'L/M/H')
4. EstimatedTime (numeric '#')

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
