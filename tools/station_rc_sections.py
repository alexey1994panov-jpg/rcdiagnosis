# -*- coding: utf-8 -*-

RC_SECTIONS = {
    '10-12СП': {'PrevSec': '1АП', 'NextSec': None, 'Switches': [{'name': '10', 'NextMi': '3П', 'NextPl': '1П', 'NextSwPl': None, 'NextSwMi': None, 'PrevSw': None}]},
    '14-16СП': {'PrevSec': None, 'NextSec': '2П', 'Switches': [{'name': '16', 'NextMi': '4П', 'NextPl': '2АП', 'NextSwPl': None, 'NextSwMi': None, 'PrevSw': None}]},
    '1-7СП': {'PrevSec': None, 'NextSec': 'НП', 'Switches': [{'name': '1', 'NextMi': '3СП', 'NextPl': None, 'NextSwPl': '5', 'NextSwMi': None, 'PrevSw': None}, {'name': '5', 'NextMi': '3П', 'NextPl': '1П', 'NextSwPl': None, 'NextSwMi': None, 'PrevSw': '1'}]},
    '1АП': {'PrevSec': '4СП', 'NextSec': '10-12СП', 'Switches': []},
    '1П': {'PrevSec': '10-12СП', 'NextSec': '1-7СП', 'Switches': []},
    '2-8СП': {'PrevSec': 'ЧП', 'NextSec': None, 'Switches': [{'name': '2', 'NextMi': '4П', 'NextPl': '6СП', 'NextSwPl': None, 'NextSwMi': None, 'PrevSw': None}]},
    '2АП': {'PrevSec': '6СП', 'NextSec': '14-16СП', 'Switches': []},
    '2П': {'PrevSec': '14-16СП', 'NextSec': '3СП', 'Switches': []},
    '3П': {'PrevSec': '10-12СП', 'NextSec': '1-7СП', 'Switches': []},
    '3СП': {'PrevSec': '2П', 'NextSec': None, 'Switches': [{'name': '3', 'NextMi': '1-7СП', 'NextPl': 'НДП', 'NextSwPl': None, 'NextSwMi': None, 'PrevSw': None}]},
    '4П': {'PrevSec': '2-8СП', 'NextSec': '14-16СП', 'Switches': []},
    '4СП': {'PrevSec': 'ЧДП', 'NextSec': None, 'Switches': [{'name': '4', 'NextMi': '6СП', 'NextPl': '1АП', 'NextSwPl': None, 'NextSwMi': None, 'PrevSw': None}]},
    '6СП': {'PrevSec': None, 'NextSec': '2АП', 'Switches': [{'name': '6', 'NextMi': '4СП', 'NextPl': '2-8СП', 'NextSwPl': None, 'NextSwMi': None, 'PrevSw': None}]},
    'НДП': {'PrevSec': '3СП', 'NextSec': None, 'Switches': []},
    'НП': {'PrevSec': '1-7СП', 'NextSec': None, 'Switches': []},
    'ЧДП': {'PrevSec': None, 'NextSec': '4СП', 'Switches': []},
    'ЧП': {'PrevSec': None, 'NextSec': '2-8СП', 'Switches': []},
}
