from random import *
from uuid import *

def randomUUID():
    idlist = []

    uuid = uuid4()
    if uuid not in idlist:
        idlist.append(uuid)    
        return uuid
    else: return randomUUID()