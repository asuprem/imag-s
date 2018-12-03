import sqlite3
import json

_PUSH = '{'
_POP = '}'

def get_cursors(path):
    conn_obj = sqlite3.connect(path, check_same_thread=False)
    return conn_obj.cursor()

def get_node_ids(path):
    cursor = get_cursors(path)
    ids = dict(cursor.execute('Select synset,id from synset_count'))
    cursor.close()
    return ids

def par_iterate(par_i_str):
    for idx,item in enumerate(par_i_str):
        if item == '{':
            return par_i_str[idx:]
    return ''

def par_check(i_counter, i_str, obj_read):
    # This code checsk aprenthesis and returns a complete json object for extraction
    if not obj_read:
        #i.e. we are starting again, so there may be gaps:
        i_str = par_iterate(i_str)
    for idx, item in enumerate(i_str):
        if item == _PUSH:
            i_counter+=1
        if item == _POP:
            i_counter-=1
        if i_counter == 0:
            try:
                temp_json = json.loads(obj_read+i_str[:idx+1])
                return i_counter, i_str[:idx+1], par_iterate(i_str[idx+1:])
            except ValueError:
                i_counter+=1
    return i_counter, i_str, ''
