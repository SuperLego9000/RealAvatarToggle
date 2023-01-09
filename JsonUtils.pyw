import json
def write(what,where):
    what=what
    clear(where)
    with open("data_file.json", "w") as write_file:
        json.dump(what, write_file)
    return True
def clear(what):
    with open(what,'w') as cleared:cleared.close()
    return True
def read(read):
    import re
    '''returns data'''
    read=read.replace("/","\\")
    with open(read, "r") as read_file:
        st=read_file.read()
        data = json.loads(st)
    return data