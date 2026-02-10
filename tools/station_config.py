# -*- coding: utf-8 -*-

RC_10_12СП = '59'
RC_14_16СП = '94'
RC_1_7СП = '83'
RC_1АП = '47'
RC_1П = '108'
RC_2_8СП = '36'
RC_2АП = '62'
RC_2П = '90'
RC_3П = '104'
RC_3СП = '86'
RC_4П = '65'
RC_4СП = '58'
RC_6СП = '37'
RC_НДП = '98'
RC_НП = '81'
RC_ЧДП = '57'
RC_ЧП = '40'
SIG_М1 = '82'
SIG_М2 = '38'
SIG_М3 = '95'
SIG_М4 = '55'
SIG_Н = '78'
SIG_Н1 = '46'
SIG_Н2 = '61'
SIG_Н4 = '64'
SIG_НД = '100'
SIG_НМ1 = '107'
SIG_НМ2 = '89'
SIG_НМ3 = '103'
SIG_Ч = '42'
SIG_Ч1 = '114'
SIG_Ч2 = '92'
SIG_Ч3 = '117'
SIG_ЧД = '53'
SIG_ЧМ1 = '50'
SIG_ЧМ2 = '68'
SIG_ЧМ4 = '75'
SW_1 = '87'
SW_10 = '110'
SW_16 = '73'
SW_2 = '32'
SW_3 = '150'
SW_4 = '33'
SW_5 = '88'
SW_6 = '149'

GROUPS = {
    'rc_ids': ['59', '94', '83', '47', '108', '36', '62', '90', '104', '86', '65', '58', '37', '98', '81', '57', '40'],
    'switches_ids': ['87', '110', '73', '32', '150', '33', '88', '149'],
    'shunt_signals_ids': ['82', '38', '95', '55'],
    'train_signals_ids': ['78', '46', '61', '64', '100', '107', '89', '103', '42', '114', '92', '117', '53', '50', '68', '75'],
}

NODES = {
    '87': {'name': '1', 'type': 2, 'prev_links': [], 'next_links': [], 'tasks': []},
    '110': {'name': '10', 'type': 2, 'prev_links': [], 'next_links': [], 'tasks': []},
    '59': {'name': '10-12СП', 'type': 1, 'prev_links': ['1АП'], 'next_links': [], 'tasks': [{'name': 'LZ', 'class': 'Tdm.Unification.SmartTasks.LZTechTask', 'desc': 'Логическая ложная занятость РЦ'}, {'name': 'LS', 'class': 'Tdm.Unification.SmartTasks.LSTechTask', 'desc': 'Логическая ложная свободность РЦ'}]},
    '94': {'name': '14-16СП', 'type': 1, 'prev_links': [], 'next_links': ['2П'], 'tasks': [{'name': 'LZ', 'class': 'Tdm.Unification.SmartTasks.LZTechTask', 'desc': 'Логическая ложная занятость РЦ'}, {'name': 'LS', 'class': 'Tdm.Unification.SmartTasks.LSTechTask', 'desc': 'Логическая ложная свободность РЦ'}]},
    '73': {'name': '16', 'type': 2, 'prev_links': [], 'next_links': [], 'tasks': []},
    '83': {'name': '1-7СП', 'type': 1, 'prev_links': [], 'next_links': ['НП'], 'tasks': [{'name': 'LZ', 'class': 'Tdm.Unification.SmartTasks.LZTechTask', 'desc': 'Логическая ложная занятость РЦ'}, {'name': 'LS', 'class': 'Tdm.Unification.SmartTasks.LSTechTask', 'desc': 'Логическая ложная свободность РЦ'}]},
    '47': {'name': '1АП', 'type': 1, 'prev_links': ['4СП'], 'next_links': ['10-12СП'], 'tasks': [{'name': 'LZ', 'class': 'Tdm.Unification.SmartTasks.LZTechTask', 'desc': 'Логическая ложная занятость РЦ'}, {'name': 'LS', 'class': 'Tdm.Unification.SmartTasks.LSTechTask', 'desc': 'Логическая ложная свободность РЦ'}]},
    '108': {'name': '1П', 'type': 1, 'prev_links': ['10-12СП'], 'next_links': ['1-7СП'], 'tasks': [{'name': 'LZ', 'class': 'Tdm.Unification.SmartTasks.LZTechTask', 'desc': 'Логическая ложная занятость РЦ'}, {'name': 'LS', 'class': 'Tdm.Unification.SmartTasks.LSTechTask', 'desc': 'Логическая ложная свободность РЦ'}]},
    '32': {'name': '2', 'type': 2, 'prev_links': [], 'next_links': [], 'tasks': []},
    '36': {'name': '2-8СП', 'type': 1, 'prev_links': ['ЧП'], 'next_links': [], 'tasks': [{'name': 'LZ', 'class': 'Tdm.Unification.SmartTasks.LZTechTask', 'desc': 'Логическая ложная занятость РЦ'}, {'name': 'LS', 'class': 'Tdm.Unification.SmartTasks.LSTechTask', 'desc': 'Логическая ложная свободность РЦ'}]},
    '62': {'name': '2АП', 'type': 1, 'prev_links': ['6СП'], 'next_links': ['14-16СП'], 'tasks': [{'name': 'LZ', 'class': 'Tdm.Unification.SmartTasks.LZTechTask', 'desc': 'Логическая ложная занятость РЦ'}, {'name': 'LS', 'class': 'Tdm.Unification.SmartTasks.LSTechTask', 'desc': 'Логическая ложная свободность РЦ'}]},
    '90': {'name': '2П', 'type': 1, 'prev_links': ['14-16СП'], 'next_links': ['3СП'], 'tasks': [{'name': 'LZ', 'class': 'Tdm.Unification.SmartTasks.LZTechTask', 'desc': 'Логическая ложная занятость РЦ'}, {'name': 'LS', 'class': 'Tdm.Unification.SmartTasks.LSTechTask', 'desc': 'Логическая ложная свободность РЦ'}]},
    '150': {'name': '3', 'type': 2, 'prev_links': [], 'next_links': [], 'tasks': []},
    '104': {'name': '3П', 'type': 1, 'prev_links': ['10-12СП'], 'next_links': ['1-7СП'], 'tasks': [{'name': 'LZ', 'class': 'Tdm.Unification.SmartTasks.LZTechTask', 'desc': 'Логическая ложная занятость РЦ'}, {'name': 'LS', 'class': 'Tdm.Unification.SmartTasks.LSTechTask', 'desc': 'Логическая ложная свободность РЦ'}]},
    '86': {'name': '3СП', 'type': 1, 'prev_links': ['2П'], 'next_links': [], 'tasks': [{'name': 'LZ', 'class': 'Tdm.Unification.SmartTasks.LZTechTask', 'desc': 'Логическая ложная занятость РЦ'}, {'name': 'LS', 'class': 'Tdm.Unification.SmartTasks.LSTechTask', 'desc': 'Логическая ложная свободность РЦ'}]},
    '33': {'name': '4', 'type': 2, 'prev_links': [], 'next_links': [], 'tasks': []},
    '65': {'name': '4П', 'type': 1, 'prev_links': ['2-8СП'], 'next_links': ['14-16СП'], 'tasks': [{'name': 'LZ', 'class': 'Tdm.Unification.SmartTasks.LZTechTask', 'desc': 'Логическая ложная занятость РЦ'}, {'name': 'LS', 'class': 'Tdm.Unification.SmartTasks.LSTechTask', 'desc': 'Логическая ложная свободность РЦ'}]},
    '58': {'name': '4СП', 'type': 1, 'prev_links': ['ЧДП'], 'next_links': [], 'tasks': [{'name': 'LZ', 'class': 'Tdm.Unification.SmartTasks.LZTechTask', 'desc': 'Логическая ложная занятость РЦ'}, {'name': 'LS', 'class': 'Tdm.Unification.SmartTasks.LSTechTask', 'desc': 'Логическая ложная свободность РЦ'}]},
    '88': {'name': '5', 'type': 2, 'prev_links': [], 'next_links': [], 'tasks': []},
    '149': {'name': '6', 'type': 2, 'prev_links': [], 'next_links': [], 'tasks': []},
    '37': {'name': '6СП', 'type': 1, 'prev_links': [], 'next_links': ['2АП'], 'tasks': [{'name': 'LZ', 'class': 'Tdm.Unification.SmartTasks.LZTechTask', 'desc': 'Логическая ложная занятость РЦ'}, {'name': 'LS', 'class': 'Tdm.Unification.SmartTasks.LSTechTask', 'desc': 'Логическая ложная свободность РЦ'}]},
    '82': {'name': 'М1', 'type': 3, 'prev_links': ['НП'], 'next_links': ['1-7СП'], 'tasks': []},
    '38': {'name': 'М2', 'type': 3, 'prev_links': ['ЧП'], 'next_links': ['2-8СП'], 'tasks': []},
    '95': {'name': 'М3', 'type': 3, 'prev_links': ['НДП'], 'next_links': ['3СП'], 'tasks': []},
    '55': {'name': 'М4', 'type': 3, 'prev_links': ['ЧДП'], 'next_links': ['4СП'], 'tasks': []},
    '78': {'name': 'Н', 'type': 4, 'prev_links': [], 'next_links': ['НП'], 'tasks': []},
    '46': {'name': 'Н1', 'type': 4, 'prev_links': ['1АП'], 'next_links': ['4СП'], 'tasks': []},
    '61': {'name': 'Н2', 'type': 4, 'prev_links': ['2АП'], 'next_links': ['6СП'], 'tasks': []},
    '64': {'name': 'Н4', 'type': 4, 'prev_links': ['4П'], 'next_links': ['2-8СП'], 'tasks': []},
    '100': {'name': 'НД', 'type': 4, 'prev_links': [], 'next_links': ['НДП'], 'tasks': []},
    '98': {'name': 'НДП', 'type': 1, 'prev_links': ['3СП'], 'next_links': [], 'tasks': [{'name': 'LZ', 'class': 'Tdm.Unification.SmartTasks.LZTechTask', 'desc': 'Логическая ложная занятость РЦ'}, {'name': 'LS', 'class': 'Tdm.Unification.SmartTasks.LSTechTask', 'desc': 'Логическая ложная свободность РЦ'}]},
    '107': {'name': 'НМ1', 'type': 4, 'prev_links': ['1П'], 'next_links': ['10-12СП'], 'tasks': []},
    '89': {'name': 'НМ2', 'type': 4, 'prev_links': ['2П'], 'next_links': ['14-16СП'], 'tasks': []},
    '103': {'name': 'НМ3', 'type': 4, 'prev_links': ['3П'], 'next_links': ['10-12СП'], 'tasks': []},
    '81': {'name': 'НП', 'type': 1, 'prev_links': ['1-7СП'], 'next_links': [], 'tasks': [{'name': 'LZ', 'class': 'Tdm.Unification.SmartTasks.LZTechTask', 'desc': 'Логическая ложная занятость РЦ'}, {'name': 'LS', 'class': 'Tdm.Unification.SmartTasks.LSTechTask', 'desc': 'Логическая ложная свободность РЦ'}]},
    '42': {'name': 'Ч', 'type': 4, 'prev_links': [], 'next_links': ['ЧП'], 'tasks': []},
    '114': {'name': 'Ч1', 'type': 4, 'prev_links': ['1П'], 'next_links': ['1-7СП'], 'tasks': []},
    '92': {'name': 'Ч2', 'type': 4, 'prev_links': ['2П'], 'next_links': ['3СП'], 'tasks': []},
    '117': {'name': 'Ч3', 'type': 4, 'prev_links': ['3П'], 'next_links': ['1-7СП'], 'tasks': []},
    '53': {'name': 'ЧД', 'type': 4, 'prev_links': [], 'next_links': ['ЧДП'], 'tasks': []},
    '57': {'name': 'ЧДП', 'type': 1, 'prev_links': [], 'next_links': ['4СП'], 'tasks': [{'name': 'LZ', 'class': 'Tdm.Unification.SmartTasks.LZTechTask', 'desc': 'Логическая ложная занятость РЦ'}, {'name': 'LS', 'class': 'Tdm.Unification.SmartTasks.LSTechTask', 'desc': 'Логическая ложная свободность РЦ'}]},
    '50': {'name': 'ЧМ1', 'type': 4, 'prev_links': ['1АП'], 'next_links': ['10-12СП'], 'tasks': []},
    '68': {'name': 'ЧМ2', 'type': 4, 'prev_links': ['2АП'], 'next_links': ['14-16СП'], 'tasks': []},
    '75': {'name': 'ЧМ4', 'type': 4, 'prev_links': ['4П'], 'next_links': ['14-16СП'], 'tasks': []},
    '40': {'name': 'ЧП', 'type': 1, 'prev_links': [], 'next_links': ['2-8СП'], 'tasks': [{'name': 'LZ', 'class': 'Tdm.Unification.SmartTasks.LZTechTask', 'desc': 'Логическая ложная занятость РЦ'}, {'name': 'LS', 'class': 'Tdm.Unification.SmartTasks.LSTechTask', 'desc': 'Логическая ложная свободность РЦ'}]},
}

STATES_GRAPH = {
    '87': {3: 'ПК = 1 AND МК(0) = 0 AND (SwSection = 3 OR SwExclRules(0) = 1)', 4: 'ПК = 1 AND МК(0) = 0 AND SwSection = 4', 5: 'ПК = 1 AND МК(0) = 0 AND SwSection = 5', 6: 'ПК = 1 AND МК(0) = 0 AND SwSection = 6', 7: 'ПК = 1 AND МК(0) = 0 AND SwSection = 7', 8: 'ПК = 1 AND МК(0) = 0 AND SwSection = 8', 9: 'ПК = 0 AND МК(1) = 1 AND (SwSection = 3 OR SwExclRules(0) = 1)', 10: 'ПК = 0 AND МК(1) = 1 AND SwSection = 4', 11: 'ПК = 0 AND МК(1) = 1 AND SwSection = 5', 12: 'ПК = 0 AND МК(1) = 1 AND SwSection = 6', 13: 'ПК = 0 AND МК(1) = 1 AND SwSection = 7', 14: 'ПК = 0 AND МК(1) = 1 AND SwSection = 8', 15: 'ПК = 0 AND МК(0) = 0 AND (SwSection = 3 OR SwExclRules(0) = 1)', 16: 'ПК = 0 AND МК(0) = 0 AND SwSection = 4', 17: 'ПК = 0 AND МК(0) = 0 AND SwSection = 6', 18: 'ПК = 0 AND МК(0) = 0 AND SwSection = 7', 19: 'ПК = 0 AND МК(0) = 0 AND SwSection = 5', 20: 'ПК = 0 AND МК(0) = 0 AND SwSection = 8'},
    '110': {3: 'ПК = 1 AND МК(0) = 0 AND (SwSection = 3 OR SwExclRules(0) = 1)', 4: 'ПК = 1 AND МК(0) = 0 AND SwSection = 4', 5: 'ПК = 1 AND МК(0) = 0 AND SwSection = 5', 6: 'ПК = 1 AND МК(0) = 0 AND SwSection = 6', 7: 'ПК = 1 AND МК(0) = 0 AND SwSection = 7', 8: 'ПК = 1 AND МК(0) = 0 AND SwSection = 8', 9: 'ПК = 0 AND МК(1) = 1 AND (SwSection = 3 OR SwExclRules(0) = 1)', 10: 'ПК = 0 AND МК(1) = 1 AND SwSection = 4', 11: 'ПК = 0 AND МК(1) = 1 AND SwSection = 5', 12: 'ПК = 0 AND МК(1) = 1 AND SwSection = 6', 13: 'ПК = 0 AND МК(1) = 1 AND SwSection = 7', 14: 'ПК = 0 AND МК(1) = 1 AND SwSection = 8', 15: 'ПК = 0 AND МК(0) = 0 AND (SwSection = 3 OR SwExclRules(0) = 1)', 16: 'ПК = 0 AND МК(0) = 0 AND SwSection = 4', 17: 'ПК = 0 AND МК(0) = 0 AND SwSection = 6', 18: 'ПК = 0 AND МК(0) = 0 AND SwSection = 7', 19: 'ПК = 0 AND МК(0) = 0 AND SwSection = 5', 20: 'ПК = 0 AND МК(0) = 0 AND SwSection = 8'},
    '59': {8: 'П = 1 AND З(0) = 1 AND РИ(0) = 1', 7: 'П = 1 AND З(0) = 1', 6: 'П = 1', 5: 'П = 0 AND З(0) = 1 AND РИ(0) = 1', 4: 'П = 0 AND З(0) = 1', 3: 'П = 0'},
    '94': {8: 'П = 1 AND З(0) = 1 AND РИ(0) = 1', 7: 'П = 1 AND З(0) = 1', 6: 'П = 1', 5: 'П = 0 AND З(0) = 1 AND РИ(0) = 1', 4: 'П = 0 AND З(0) = 1', 3: 'П = 0'},
    '73': {3: 'ПК = 1 AND МК(0) = 0 AND (SwSection = 3 OR SwExclRules(0) = 1)', 4: 'ПК = 1 AND МК(0) = 0 AND SwSection = 4', 5: 'ПК = 1 AND МК(0) = 0 AND SwSection = 5', 6: 'ПК = 1 AND МК(0) = 0 AND SwSection = 6', 7: 'ПК = 1 AND МК(0) = 0 AND SwSection = 7', 8: 'ПК = 1 AND МК(0) = 0 AND SwSection = 8', 9: 'ПК = 0 AND МК(1) = 1 AND (SwSection = 3 OR SwExclRules(0) = 1)', 10: 'ПК = 0 AND МК(1) = 1 AND SwSection = 4', 11: 'ПК = 0 AND МК(1) = 1 AND SwSection = 5', 12: 'ПК = 0 AND МК(1) = 1 AND SwSection = 6', 13: 'ПК = 0 AND МК(1) = 1 AND SwSection = 7', 14: 'ПК = 0 AND МК(1) = 1 AND SwSection = 8', 15: 'ПК = 0 AND МК(0) = 0 AND (SwSection = 3 OR SwExclRules(0) = 1)', 16: 'ПК = 0 AND МК(0) = 0 AND SwSection = 4', 17: 'ПК = 0 AND МК(0) = 0 AND SwSection = 6', 18: 'ПК = 0 AND МК(0) = 0 AND SwSection = 7', 19: 'ПК = 0 AND МК(0) = 0 AND SwSection = 5', 20: 'ПК = 0 AND МК(0) = 0 AND SwSection = 8'},
    '83': {8: 'П = 1 AND З(0) = 1 AND РИ(0) = 1', 7: 'П = 1 AND З(0) = 1', 6: 'П = 1', 5: 'П = 0 AND З(0) = 1 AND РИ(0) = 1', 4: 'П = 0 AND З(0) = 1', 3: 'П = 0'},
    '47': {8: 'П = 1 AND З(0) = 1 AND РИ(0) = 1', 7: 'П = 1 AND З(0) = 1', 6: 'П = 1', 5: 'П = 0 AND З(0) = 1 AND РИ(0) = 1', 4: 'П = 0 AND З(0) = 1', 3: 'П = 0'},
    '108': {8: 'П = 1 AND З(0) = 1 AND РИ(0) = 1', 7: 'П = 1 AND З(0) = 1', 6: 'П = 1', 5: 'П = 0 AND З(0) = 1 AND РИ(0) = 1', 4: 'П = 0 AND З(0) = 1', 3: 'П = 0'},
    '32': {3: 'ПК = 1 AND МК(0) = 0 AND (SwSection = 3 OR SwExclRules(0) = 1)', 4: 'ПК = 1 AND МК(0) = 0 AND SwSection = 4', 5: 'ПК = 1 AND МК(0) = 0 AND SwSection = 5', 6: 'ПК = 1 AND МК(0) = 0 AND SwSection = 6', 7: 'ПК = 1 AND МК(0) = 0 AND SwSection = 7', 8: 'ПК = 1 AND МК(0) = 0 AND SwSection = 8', 9: 'ПК = 0 AND МК(1) = 1 AND (SwSection = 3 OR SwExclRules(0) = 1)', 10: 'ПК = 0 AND МК(1) = 1 AND SwSection = 4', 11: 'ПК = 0 AND МК(1) = 1 AND SwSection = 5', 12: 'ПК = 0 AND МК(1) = 1 AND SwSection = 6', 13: 'ПК = 0 AND МК(1) = 1 AND SwSection = 7', 14: 'ПК = 0 AND МК(1) = 1 AND SwSection = 8', 15: 'ПК = 0 AND МК(0) = 0 AND (SwSection = 3 OR SwExclRules(0) = 1)', 16: 'ПК = 0 AND МК(0) = 0 AND SwSection = 4', 17: 'ПК = 0 AND МК(0) = 0 AND SwSection = 6', 18: 'ПК = 0 AND МК(0) = 0 AND SwSection = 7', 19: 'ПК = 0 AND МК(0) = 0 AND SwSection = 5', 20: 'ПК = 0 AND МК(0) = 0 AND SwSection = 8'},
    '36': {8: 'П = 1 AND З(0) = 1 AND РИ(0) = 1', 7: 'П = 1 AND З(0) = 1', 6: 'П = 1', 5: 'П = 0 AND З(0) = 1 AND РИ(0) = 1', 4: 'П = 0 AND З(0) = 1', 3: 'П = 0'},
    '62': {8: 'П = 1 AND З(0) = 1 AND РИ(0) = 1', 7: 'П = 1 AND З(0) = 1', 6: 'П = 1', 5: 'П = 0 AND З(0) = 1 AND РИ(0) = 1', 4: 'П = 0 AND З(0) = 1', 3: 'П = 0'},
    '90': {8: 'П = 1 AND З(0) = 1 AND РИ(0) = 1', 7: 'П = 1 AND З(0) = 1', 6: 'П = 1', 5: 'П = 0 AND З(0) = 1 AND РИ(0) = 1', 4: 'П = 0 AND З(0) = 1', 3: 'П = 0'},
    '150': {3: 'ПК = 1 AND МК(0) = 0 AND (SwSection = 3 OR SwExclRules(0) = 1)', 4: 'ПК = 1 AND МК(0) = 0 AND SwSection = 4', 5: 'ПК = 1 AND МК(0) = 0 AND SwSection = 5', 6: 'ПК = 1 AND МК(0) = 0 AND SwSection = 6', 7: 'ПК = 1 AND МК(0) = 0 AND SwSection = 7', 8: 'ПК = 1 AND МК(0) = 0 AND SwSection = 8', 9: 'ПК = 0 AND МК(1) = 1 AND (SwSection = 3 OR SwExclRules(0) = 1)', 10: 'ПК = 0 AND МК(1) = 1 AND SwSection = 4', 11: 'ПК = 0 AND МК(1) = 1 AND SwSection = 5', 12: 'ПК = 0 AND МК(1) = 1 AND SwSection = 6', 13: 'ПК = 0 AND МК(1) = 1 AND SwSection = 7', 14: 'ПК = 0 AND МК(1) = 1 AND SwSection = 8', 15: 'ПК = 0 AND МК(0) = 0 AND (SwSection = 3 OR SwExclRules(0) = 1)', 16: 'ПК = 0 AND МК(0) = 0 AND SwSection = 4', 17: 'ПК = 0 AND МК(0) = 0 AND SwSection = 6', 18: 'ПК = 0 AND МК(0) = 0 AND SwSection = 7', 19: 'ПК = 0 AND МК(0) = 0 AND SwSection = 5', 20: 'ПК = 0 AND МК(0) = 0 AND SwSection = 8'},
    '104': {8: 'П = 1 AND З(0) = 1 AND РИ(0) = 1', 7: 'П = 1 AND З(0) = 1', 6: 'П = 1', 5: 'П = 0 AND З(0) = 1 AND РИ(0) = 1', 4: 'П = 0 AND З(0) = 1', 3: 'П = 0'},
    '86': {8: 'П = 1 AND З(0) = 1 AND РИ(0) = 1', 7: 'П = 1 AND З(0) = 1', 6: 'П = 1', 5: 'П = 0 AND З(0) = 1 AND РИ(0) = 1', 4: 'П = 0 AND З(0) = 1', 3: 'П = 0'},
    '33': {3: 'ПК = 1 AND МК(0) = 0 AND (SwSection = 3 OR SwExclRules(0) = 1)', 4: 'ПК = 1 AND МК(0) = 0 AND SwSection = 4', 5: 'ПК = 1 AND МК(0) = 0 AND SwSection = 5', 6: 'ПК = 1 AND МК(0) = 0 AND SwSection = 6', 7: 'ПК = 1 AND МК(0) = 0 AND SwSection = 7', 8: 'ПК = 1 AND МК(0) = 0 AND SwSection = 8', 9: 'ПК = 0 AND МК(1) = 1 AND (SwSection = 3 OR SwExclRules(0) = 1)', 10: 'ПК = 0 AND МК(1) = 1 AND SwSection = 4', 11: 'ПК = 0 AND МК(1) = 1 AND SwSection = 5', 12: 'ПК = 0 AND МК(1) = 1 AND SwSection = 6', 13: 'ПК = 0 AND МК(1) = 1 AND SwSection = 7', 14: 'ПК = 0 AND МК(1) = 1 AND SwSection = 8', 15: 'ПК = 0 AND МК(0) = 0 AND (SwSection = 3 OR SwExclRules(0) = 1)', 16: 'ПК = 0 AND МК(0) = 0 AND SwSection = 4', 17: 'ПК = 0 AND МК(0) = 0 AND SwSection = 6', 18: 'ПК = 0 AND МК(0) = 0 AND SwSection = 7', 19: 'ПК = 0 AND МК(0) = 0 AND SwSection = 5', 20: 'ПК = 0 AND МК(0) = 0 AND SwSection = 8'},
    '65': {8: 'П = 1 AND З(0) = 1 AND РИ(0) = 1', 7: 'П = 1 AND З(0) = 1', 6: 'П = 1', 5: 'П = 0 AND З(0) = 1 AND РИ(0) = 1', 4: 'П = 0 AND З(0) = 1', 3: 'П = 0'},
    '58': {8: 'П = 1 AND З(0) = 1 AND РИ(0) = 1', 7: 'П = 1 AND З(0) = 1', 6: 'П = 1', 5: 'П = 0 AND З(0) = 1 AND РИ(0) = 1', 4: 'П = 0 AND З(0) = 1', 3: 'П = 0'},
    '88': {3: 'ПК = 1 AND МК(0) = 0 AND (SwSection = 3 OR SwExclRules(0) = 1)', 4: 'ПК = 1 AND МК(0) = 0 AND SwSection = 4', 5: 'ПК = 1 AND МК(0) = 0 AND SwSection = 5', 6: 'ПК = 1 AND МК(0) = 0 AND SwSection = 6', 7: 'ПК = 1 AND МК(0) = 0 AND SwSection = 7', 8: 'ПК = 1 AND МК(0) = 0 AND SwSection = 8', 9: 'ПК = 0 AND МК(1) = 1 AND (SwSection = 3 OR SwExclRules(0) = 1)', 10: 'ПК = 0 AND МК(1) = 1 AND SwSection = 4', 11: 'ПК = 0 AND МК(1) = 1 AND SwSection = 5', 12: 'ПК = 0 AND МК(1) = 1 AND SwSection = 6', 13: 'ПК = 0 AND МК(1) = 1 AND SwSection = 7', 14: 'ПК = 0 AND МК(1) = 1 AND SwSection = 8', 15: 'ПК = 0 AND МК(0) = 0 AND (SwSection = 3 OR SwExclRules(0) = 1)', 16: 'ПК = 0 AND МК(0) = 0 AND SwSection = 4', 17: 'ПК = 0 AND МК(0) = 0 AND SwSection = 6', 18: 'ПК = 0 AND МК(0) = 0 AND SwSection = 7', 19: 'ПК = 0 AND МК(0) = 0 AND SwSection = 5', 20: 'ПК = 0 AND МК(0) = 0 AND SwSection = 8'},
    '149': {3: 'ПК = 1 AND МК(0) = 0 AND (SwSection = 3 OR SwExclRules(0) = 1)', 4: 'ПК = 1 AND МК(0) = 0 AND SwSection = 4', 5: 'ПК = 1 AND МК(0) = 0 AND SwSection = 5', 6: 'ПК = 1 AND МК(0) = 0 AND SwSection = 6', 7: 'ПК = 1 AND МК(0) = 0 AND SwSection = 7', 8: 'ПК = 1 AND МК(0) = 0 AND SwSection = 8', 9: 'ПК = 0 AND МК(1) = 1 AND (SwSection = 3 OR SwExclRules(0) = 1)', 10: 'ПК = 0 AND МК(1) = 1 AND SwSection = 4', 11: 'ПК = 0 AND МК(1) = 1 AND SwSection = 5', 12: 'ПК = 0 AND МК(1) = 1 AND SwSection = 6', 13: 'ПК = 0 AND МК(1) = 1 AND SwSection = 7', 14: 'ПК = 0 AND МК(1) = 1 AND SwSection = 8', 15: 'ПК = 0 AND МК(0) = 0 AND (SwSection = 3 OR SwExclRules(0) = 1)', 16: 'ПК = 0 AND МК(0) = 0 AND SwSection = 4', 17: 'ПК = 0 AND МК(0) = 0 AND SwSection = 6', 18: 'ПК = 0 AND МК(0) = 0 AND SwSection = 7', 19: 'ПК = 0 AND МК(0) = 0 AND SwSection = 5', 20: 'ПК = 0 AND МК(0) = 0 AND SwSection = 8'},
    '37': {8: 'П = 1 AND З(0) = 1 AND РИ(0) = 1', 7: 'П = 1 AND З(0) = 1', 6: 'П = 1', 5: 'П = 0 AND З(0) = 1 AND РИ(0) = 1', 4: 'П = 0 AND З(0) = 1', 3: 'П = 0'},
    '82': {6: 'МС(0) = 2 OR (С(0) = 1 AND О(1) = 0) OR O(1) = 2', 3: 'МС(1) = 0 OR С(1) = 0', 4: 'МС(0) = 1 OR С(0) = 1'},
    '38': {6: 'МС(0) = 2 OR (С(0) = 1 AND О(1) = 0) OR O(1) = 2', 3: 'МС(1) = 0 OR С(1) = 0', 4: 'МС(0) = 1 OR С(0) = 1'},
    '95': {6: 'МС(0) = 2 OR (С(0) = 1 AND О(1) = 0) OR O(1) = 2', 3: 'МС(1) = 0 OR С(1) = 0', 4: 'МС(0) = 1 OR С(0) = 1'},
    '55': {6: 'МС(0) = 2 OR (С(0) = 1 AND О(1) = 0) OR O(1) = 2', 3: 'МС(1) = 0 OR С(1) = 0', 4: 'МС(0) = 1 OR С(0) = 1'},
    '78': {3: 'С = 1 AND МС(0) = 0 AND ПС(0) = 0', 15: 'С = 0 AND МС(0) = 0 AND ПС(0) = 0 AND О(0) = 1', 16: 'С = 0 AND МС(0) = 1 AND ПС(0) = 0', 18: 'С = 0 AND МС(0) = 0 AND ПС(0) = 1 AND О(0) = 1', 19: 'С = 0 AND МС(0) = 0 AND ПС(0) = 0 AND О(0) = 0', 24: 'С = 0 AND МС(0) = 0 AND ПС(0) = 1 AND О(0) = 0', 27: 'С = 1 AND МС(0) = 0 AND ПС(0) = 1'},
    '46': {3: 'С = 1 AND МС(0) = 0 AND ПС(0) = 0', 15: 'С = 0 AND МС(0) = 0 AND ПС(0) = 0 AND О(0) = 1', 16: 'С = 0 AND МС(0) = 1 AND ПС(0) = 0', 18: 'С = 0 AND МС(0) = 0 AND ПС(0) = 1 AND О(0) = 1', 19: 'С = 0 AND МС(0) = 0 AND ПС(0) = 0 AND О(0) = 0', 24: 'С = 0 AND МС(0) = 0 AND ПС(0) = 1 AND О(0) = 0', 27: 'С = 1 AND МС(0) = 0 AND ПС(0) = 1'},
    '61': {3: 'С = 1 AND МС(0) = 0 AND ПС(0) = 0', 15: 'С = 0 AND МС(0) = 0 AND ПС(0) = 0 AND О(0) = 1', 16: 'С = 0 AND МС(0) = 1 AND ПС(0) = 0', 18: 'С = 0 AND МС(0) = 0 AND ПС(0) = 1 AND О(0) = 1', 19: 'С = 0 AND МС(0) = 0 AND ПС(0) = 0 AND О(0) = 0', 24: 'С = 0 AND МС(0) = 0 AND ПС(0) = 1 AND О(0) = 0', 27: 'С = 1 AND МС(0) = 0 AND ПС(0) = 1'},
    '64': {3: 'С = 1 AND МС(0) = 0 AND ПС(0) = 0', 15: 'С = 0 AND МС(0) = 0 AND ПС(0) = 0 AND О(0) = 1', 16: 'С = 0 AND МС(0) = 1 AND ПС(0) = 0', 18: 'С = 0 AND МС(0) = 0 AND ПС(0) = 1 AND О(0) = 1', 19: 'С = 0 AND МС(0) = 0 AND ПС(0) = 0 AND О(0) = 0', 24: 'С = 0 AND МС(0) = 0 AND ПС(0) = 1 AND О(0) = 0', 27: 'С = 1 AND МС(0) = 0 AND ПС(0) = 1'},
    '100': {3: 'С = 1 AND МС(0) = 0 AND ПС(0) = 0', 15: 'С = 0 AND МС(0) = 0 AND ПС(0) = 0 AND О(0) = 1', 16: 'С = 0 AND МС(0) = 1 AND ПС(0) = 0', 18: 'С = 0 AND МС(0) = 0 AND ПС(0) = 1 AND О(0) = 1', 19: 'С = 0 AND МС(0) = 0 AND ПС(0) = 0 AND О(0) = 0', 24: 'С = 0 AND МС(0) = 0 AND ПС(0) = 1 AND О(0) = 0', 27: 'С = 1 AND МС(0) = 0 AND ПС(0) = 1'},
    '98': {8: 'П = 1 AND З(0) = 1 AND РИ(0) = 1', 7: 'П = 1 AND З(0) = 1', 6: 'П = 1', 5: 'П = 0 AND З(0) = 1 AND РИ(0) = 1', 4: 'П = 0 AND З(0) = 1', 3: 'П = 0'},
    '107': {3: 'С = 1 AND МС(0) = 0 AND ПС(0) = 0', 15: 'С = 0 AND МС(0) = 0 AND ПС(0) = 0 AND О(0) = 1', 16: 'С = 0 AND МС(0) = 1 AND ПС(0) = 0', 18: 'С = 0 AND МС(0) = 0 AND ПС(0) = 1 AND О(0) = 1', 19: 'С = 0 AND МС(0) = 0 AND ПС(0) = 0 AND О(0) = 0', 24: 'С = 0 AND МС(0) = 0 AND ПС(0) = 1 AND О(0) = 0', 27: 'С = 1 AND МС(0) = 0 AND ПС(0) = 1'},
    '89': {3: 'С = 1 AND МС(0) = 0 AND ПС(0) = 0', 15: 'С = 0 AND МС(0) = 0 AND ПС(0) = 0 AND О(0) = 1', 16: 'С = 0 AND МС(0) = 1 AND ПС(0) = 0', 18: 'С = 0 AND МС(0) = 0 AND ПС(0) = 1 AND О(0) = 1', 19: 'С = 0 AND МС(0) = 0 AND ПС(0) = 0 AND О(0) = 0', 24: 'С = 0 AND МС(0) = 0 AND ПС(0) = 1 AND О(0) = 0', 27: 'С = 1 AND МС(0) = 0 AND ПС(0) = 1'},
    '103': {3: 'С = 1 AND МС(0) = 0 AND ПС(0) = 0', 15: 'С = 0 AND МС(0) = 0 AND ПС(0) = 0 AND О(0) = 1', 16: 'С = 0 AND МС(0) = 1 AND ПС(0) = 0', 18: 'С = 0 AND МС(0) = 0 AND ПС(0) = 1 AND О(0) = 1', 19: 'С = 0 AND МС(0) = 0 AND ПС(0) = 0 AND О(0) = 0', 24: 'С = 0 AND МС(0) = 0 AND ПС(0) = 1 AND О(0) = 0', 27: 'С = 1 AND МС(0) = 0 AND ПС(0) = 1'},
    '81': {8: 'П = 1 AND З(0) = 1 AND РИ(0) = 1', 7: 'П = 1 AND З(0) = 1', 6: 'П = 1', 5: 'П = 0 AND З(0) = 1 AND РИ(0) = 1', 4: 'П = 0 AND З(0) = 1', 3: 'П = 0'},
    '42': {3: 'С = 1 AND МС(0) = 0 AND ПС(0) = 0', 15: 'С = 0 AND МС(0) = 0 AND ПС(0) = 0 AND О(0) = 1', 16: 'С = 0 AND МС(0) = 1 AND ПС(0) = 0', 18: 'С = 0 AND МС(0) = 0 AND ПС(0) = 1 AND О(0) = 1', 19: 'С = 0 AND МС(0) = 0 AND ПС(0) = 0 AND О(0) = 0', 24: 'С = 0 AND МС(0) = 0 AND ПС(0) = 1 AND О(0) = 0', 27: 'С = 1 AND МС(0) = 0 AND ПС(0) = 1'},
    '114': {3: 'С = 1 AND МС(0) = 0 AND ПС(0) = 0', 15: 'С = 0 AND МС(0) = 0 AND ПС(0) = 0 AND О(0) = 1', 16: 'С = 0 AND МС(0) = 1 AND ПС(0) = 0', 18: 'С = 0 AND МС(0) = 0 AND ПС(0) = 1 AND О(0) = 1', 19: 'С = 0 AND МС(0) = 0 AND ПС(0) = 0 AND О(0) = 0', 24: 'С = 0 AND МС(0) = 0 AND ПС(0) = 1 AND О(0) = 0', 27: 'С = 1 AND МС(0) = 0 AND ПС(0) = 1'},
    '92': {3: 'С = 1 AND МС(0) = 0 AND ПС(0) = 0', 15: 'С = 0 AND МС(0) = 0 AND ПС(0) = 0 AND О(0) = 1', 16: 'С = 0 AND МС(0) = 1 AND ПС(0) = 0', 18: 'С = 0 AND МС(0) = 0 AND ПС(0) = 1 AND О(0) = 1', 19: 'С = 0 AND МС(0) = 0 AND ПС(0) = 0 AND О(0) = 0', 24: 'С = 0 AND МС(0) = 0 AND ПС(0) = 1 AND О(0) = 0', 27: 'С = 1 AND МС(0) = 0 AND ПС(0) = 1'},
    '117': {3: 'С = 1 AND МС(0) = 0 AND ПС(0) = 0', 15: 'С = 0 AND МС(0) = 0 AND ПС(0) = 0 AND О(0) = 1', 16: 'С = 0 AND МС(0) = 1 AND ПС(0) = 0', 18: 'С = 0 AND МС(0) = 0 AND ПС(0) = 1 AND О(0) = 1', 19: 'С = 0 AND МС(0) = 0 AND ПС(0) = 0 AND О(0) = 0', 24: 'С = 0 AND МС(0) = 0 AND ПС(0) = 1 AND О(0) = 0', 27: 'С = 1 AND МС(0) = 0 AND ПС(0) = 1'},
    '53': {3: 'С = 1 AND МС(0) = 0 AND ПС(0) = 0', 15: 'С = 0 AND МС(0) = 0 AND ПС(0) = 0 AND О(0) = 1', 16: 'С = 0 AND МС(0) = 1 AND ПС(0) = 0', 18: 'С = 0 AND МС(0) = 0 AND ПС(0) = 1 AND О(0) = 1', 19: 'С = 0 AND МС(0) = 0 AND ПС(0) = 0 AND О(0) = 0', 24: 'С = 0 AND МС(0) = 0 AND ПС(0) = 1 AND О(0) = 0', 27: 'С = 1 AND МС(0) = 0 AND ПС(0) = 1'},
    '57': {8: 'П = 1 AND З(0) = 1 AND РИ(0) = 1', 7: 'П = 1 AND З(0) = 1', 6: 'П = 1', 5: 'П = 0 AND З(0) = 1 AND РИ(0) = 1', 4: 'П = 0 AND З(0) = 1', 3: 'П = 0'},
    '50': {3: 'С = 1 AND МС(0) = 0 AND ПС(0) = 0', 15: 'С = 0 AND МС(0) = 0 AND ПС(0) = 0 AND О(0) = 1', 16: 'С = 0 AND МС(0) = 1 AND ПС(0) = 0', 18: 'С = 0 AND МС(0) = 0 AND ПС(0) = 1 AND О(0) = 1', 19: 'С = 0 AND МС(0) = 0 AND ПС(0) = 0 AND О(0) = 0', 24: 'С = 0 AND МС(0) = 0 AND ПС(0) = 1 AND О(0) = 0', 27: 'С = 1 AND МС(0) = 0 AND ПС(0) = 1'},
    '68': {3: 'С = 1 AND МС(0) = 0 AND ПС(0) = 0', 15: 'С = 0 AND МС(0) = 0 AND ПС(0) = 0 AND О(0) = 1', 16: 'С = 0 AND МС(0) = 1 AND ПС(0) = 0', 18: 'С = 0 AND МС(0) = 0 AND ПС(0) = 1 AND О(0) = 1', 19: 'С = 0 AND МС(0) = 0 AND ПС(0) = 0 AND О(0) = 0', 24: 'С = 0 AND МС(0) = 0 AND ПС(0) = 1 AND О(0) = 0', 27: 'С = 1 AND МС(0) = 0 AND ПС(0) = 1'},
    '75': {3: 'С = 1 AND МС(0) = 0 AND ПС(0) = 0', 15: 'С = 0 AND МС(0) = 0 AND ПС(0) = 0 AND О(0) = 1', 16: 'С = 0 AND МС(0) = 1 AND ПС(0) = 0', 18: 'С = 0 AND МС(0) = 0 AND ПС(0) = 1 AND О(0) = 1', 19: 'С = 0 AND МС(0) = 0 AND ПС(0) = 0 AND О(0) = 0', 24: 'С = 0 AND МС(0) = 0 AND ПС(0) = 1 AND О(0) = 0', 27: 'С = 1 AND МС(0) = 0 AND ПС(0) = 1'},
    '40': {8: 'П = 1 AND З(0) = 1 AND РИ(0) = 1', 7: 'П = 1 AND З(0) = 1', 6: 'П = 1', 5: 'П = 0 AND З(0) = 1 AND РИ(0) = 1', 4: 'П = 0 AND З(0) = 1', 3: 'П = 0'},
}
