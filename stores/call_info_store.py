call_info_store = {}

def get_call_info_store():
    return call_info_store

def set_call_context(call_id, project_id):
    if call_id not in call_info_store:
        call_info_store[call_id] = {}
    call_info_store[call_id]['context'] = {
        'project_id': project_id
    }

def set_call_info(call_id, info_dict):
    if call_id not in call_info_store:
        call_info_store[call_id] = {}
    call_info_store[call_id]['info'] = info_dict 