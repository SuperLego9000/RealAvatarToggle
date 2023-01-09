import json
import glob
from os import path as Path
import os
import math

from pythonosc import udp_client
client = udp_client.SimpleUDPClient("127.0.0.1", 9000)
pageSize=5
def getAvatars():
    """returns list of absolute filepaths to osc avatars"""
    p=os.environ.get("HOMEDRIVE")+r"/Users/"+os.environ.get("username")+r"/AppData/LocalLow"
    search=p+r'/VRChat/VRChat/OSC'
    search=glob.glob(search+r'/usr_*')[0]
    search+=r'/Avatars/'+r"avtr*.json"

    #search.replace("/", "/")
    files = glob.glob(search)
    for x,file in enumerate(files):
        files[x]=str(file.replace("\\","/"))
    return files
def deleteAvatars():
    for path in getAvatars():
        print(f"deleting {path}")
        os.remove(path)
class Avatar:
    def dump(self):
        for _,v in enumerate(self.parameters):
            print(v['name'])
            print("  "+v['address'])
    def __init__(self,path:str):
        #print(f"loading {path}")
        with open(path, "r") as read_file:
            st=read_file.read()
            try:st=st.split("ï»¿")[1]
            except:st=st[3:]
            self.data = json.loads(st)
        self.name=self.data["name"]
        self.parameters=[]
        for _,toggle in enumerate(self.data["parameters"]):
            try:
                toggle['input']
                self.parameters.append({
                    "name" : toggle["name"],
                    "type" : toggle["input"]["type"],
                    "address" : toggle["input"]["address"],
                })
            except:pass
        self.p={}
        for param in self.parameters:
            try:self.p[param['type']]
            except:self.p[param['type']]=[]
            self.p[param['type']].append(param)