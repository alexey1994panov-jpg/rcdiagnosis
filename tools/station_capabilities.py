from typing import Dict, List

RC_CAPABILITIES: Dict[str, Dict] = {
    # Стрелочные секции — замыкание возможно
    '59':  {'can_lock': True,  'is_endpoint': False, 'allowed_detectors': [1,2,3,5,7,8,9,10,11,12,13], 'allowed_ls_detectors': [1,2,4,5,6,9], 'task_lz_number': 41149,  'task_ls_number': 41150},
    '94':  {'can_lock': True,  'is_endpoint': False, 'allowed_detectors': [1,2,3,5,7,8,9,10,11,12,13], 'allowed_ls_detectors': [1,2,4,5,6,9], 'task_lz_number': 41149,  'task_ls_number': 41150},
    '83':  {'can_lock': True,  'is_endpoint': False, 'allowed_detectors': [1,2,3,5,7,8,9,10,11,12,13], 'allowed_ls_detectors': [1,2,4,5,6,9], 'task_lz_number': 41149,  'task_ls_number': 41150},
    '47':  {'can_lock': True,  'is_endpoint': False, 'allowed_detectors': [1,2,3,5,7,8,9,10,11,12,13], 'allowed_ls_detectors': [1,2,4,5,6,9], 'task_lz_number': 41149,  'task_ls_number': 41150},
    '36':  {'can_lock': True,  'is_endpoint': False, 'allowed_detectors': [1,2,3,5,7,8,9,10,11,12,13], 'allowed_ls_detectors': [1,2,4,5,6,9], 'task_lz_number': 41149,  'task_ls_number': 41150},
    '62':  {'can_lock': True,  'is_endpoint': False, 'allowed_detectors': [1,2,3,5,7,8,9,10,11,12,13], 'allowed_ls_detectors': [1,2,4,5,6,9], 'task_lz_number': 41149,  'task_ls_number': 41150},
    '86':  {'can_lock': True,  'is_endpoint': False, 'allowed_detectors': [1,2,3,5,7,8,9,10,11,12,13], 'allowed_ls_detectors': [1,2,4,5,6,9], 'task_lz_number': 41149,  'task_ls_number': 41150},
   
    '58':  {'can_lock': True,  'is_endpoint': False, 'allowed_detectors': [1,2,3,5,7,8,9,10,11,12,13], 'allowed_ls_detectors': [1,2,4,5,6,9], 'task_lz_number': 41149,  'task_ls_number': 41150},
    '37':  {'can_lock': True,  'is_endpoint': False, 'allowed_detectors': [1,2,3,5,7,8,9,10,11,12,13], 'allowed_ls_detectors': [1,2,4,5,6,9], 'task_lz_number': 41149,  'task_ls_number': 41150},
    '108': {'can_lock': True, 'is_endpoint': False,  'allowed_detectors': [1,2,3,5,7,8,9,10,11,12,13], 'allowed_ls_detectors': [1,2,4,5,6,9], 'task_lz_number': 41149,  'task_ls_number': 41150},
    '90': {'can_lock': True, 'is_endpoint': False,  'allowed_detectors': [1,2,3,5,7,8,9,10,11,12,13], 'allowed_ls_detectors': [1,2,4,5,6,9], 'task_lz_number': 41149,  'task_ls_number': 41150},
    '104': {'can_lock': True, 'is_endpoint': False,  'allowed_detectors': [1,2,3,5,7,8,9,10,11,12,13], 'allowed_ls_detectors': [1,2,4,5,6,9], 'task_lz_number': 41149,  'task_ls_number': 41150},
    
    
    # Без замыкания
     '65':  {'can_lock': False,  'is_endpoint': False, 'allowed_detectors': [4,6], 'allowed_ls_detectors': [1,2,4,5,6,9], 'task_lz_number': 41149,  'task_ls_number': 41150},
    
    # Конечные РЦ (перегоны)
    '98':  {'can_lock': True,  'is_endpoint': True,  'allowed_detectors': [1,2,3,5,7,8,9,11,12], 'allowed_ls_detectors': [1,2,4,5,6,9], 'task_lz_number': 41149,  'task_ls_number': 41150},
    '81':  {'can_lock': True,  'is_endpoint': True,  'allowed_detectors': [1,2,3,5,7,8,9,11,12], 'allowed_ls_detectors': [1,2,4,5,6,9], 'task_lz_number': 41149,  'task_ls_number': 41150},
    '57':  {'can_lock': True,  'is_endpoint': True,  'allowed_detectors': [1,2,3,5,7,8,9,11,12], 'allowed_ls_detectors': [1,2,4,5,6,9], 'task_lz_number': 41149,  'task_ls_number': 41150},
    '40':  {'can_lock': True,  'is_endpoint': True,  'allowed_detectors': [1,2,3,5,7,8,9,11,12], 'allowed_ls_detectors': [1,2,4,5,6,9], 'task_lz_number': 41149,  'task_ls_number': 41150},
}