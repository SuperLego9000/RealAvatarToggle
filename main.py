from tkinter import messagebox as tkms
import customtkinter as ctk
from pythonosc import udp_client
import PIL
client = udp_client.SimpleUDPClient("127.0.0.1", 9000)

import AvatarUtils as avi
import re
avatarPattern=re.compile(r'[^\x20-\x7F]')


class ParamWidget(ctk.CTkFrame):
    constTypeValues={
        "int":["slider",[0,255,1]],
        "float":["slider",[0,1,100]],
        "bool":["toggle"]
    }
    paramValue=None
    displayValue=None

    def __init__(self,controlFrame,paramTypeName):
        self.paramEnum=paramTypeName
        self.controlFrame=controlFrame
        super().__init__(controlFrame)
        title=ctk.CTkLabel(self,text=paramTypeName)

        self.displayValue=ctk.StringVar()
        display=ctk.CTkEntry(self,textvariable=self.displayValue)
        display.bind("<Return>",self._displayCallback)#lambda:self._update(self.display.get()))
        #self.displayValue.trace_ad('w',lambda:self._update(self.displayValue))

        settings=self.constTypeValues[paramTypeName]
        style=settings[0]
        if style=="slider":
            self.inputObject=ctk.CTkSlider(self,from_=settings[1][0],to=settings[1][1],number_of_steps=settings[1][2]*settings[1][1],command=self._update)
            self._update(round((settings[1][0]+settings[1][1])/2)*1.0)
        elif style=="toggle":
            self.inputObject=ctk.CTkCheckBox(self,text='',offvalue=False,onvalue=True,command=lambda:self._update(inputObject.get()))
            self._update(False)
        else:raise ValueError(paramTypeName)
        

        title.pack()
        display.pack()
        self.inputObject.pack()
    def _displayCallback(self,*a,**b):
        settings=self.constTypeValues[self.paramEnum]
        maxValue=(settings[1][0]+settings[1][1])
        self.inputObject.set(eval(self.displayValue.get()))
    def _update(self,inputValue):
        self.controlFrame.value=inputValue
        self.paramValue=inputValue
        if type(inputValue)==bool:
            self.displayValue.set(["False","True"][int(inputValue)])
        elif type(inputValue)==int or type(inputValue)==float or type(inputValue)==str:
            inputValue=float(inputValue)
            self.displayValue.set(str(round(inputValue,3)).ljust(4,'0'))
        else:
            self.displayValue.set("ERROR")


class AvatarToggle(ctk.CTk):
    avatars=[]
    params=[]
    selectedAvatar=None
    selectedParam=None
    def __init__(self):
        #init window
        super().__init__()
        self.title("RealAvatarToggle")
        self.geometry("300x200+50+50")
        self.minsize(300,200)
        self.maxsize(350,300)
        #self.resizable(False,False)
        self.attributes("-alpha",0.9)
        ctk.set_appearance_mode("dark")
        #init gui
        self.grid_rowconfigure((0,1,2,3,4), weight=1)
        self.grid_columnconfigure(0,weight=10)
        self.grid_columnconfigure(1,weight=1)
        
        self.selectedAvatar=ctk.StringVar()
        self.selectedAvatar.set("Avatar")
        self.updateAvatars()
        self.selectAvatar=ctk.CTkComboBox(
            self,values=["ERROR"],
            command=self._avatarSelected,variable=self.selectedAvatar,
            fg_color="#565b5e"
        )

        self.selectedParam=ctk.StringVar()
        self.selectedParam.set("Parameter")
        self.selectParam=ctk.CTkComboBox(
            self,values=["ERROR"],
            command=self._paramSelected,variable=self.selectedParam,
            fg_color="#565b5e"
        )

        
        reset=ctk.CTkButton(self,width=25,height=25,text="reload",#text="reset",
        image=ctk.CTkImage(dark_image=PIL.Image.open("src\\reload.png"),size=(25,25)),
        command=self.updateAvatars
        )

        delete=ctk.CTkButton(self,width=25,height=25,text="delete",
        image=ctk.CTkImage(dark_image=PIL.Image.open("src\\delete.png"),size=(25,25)),
        command=self._deletePrompt,
        fg_color="red",
        hover_color="#c00"
        )
        

        self.controlFrame=ctk.CTkFrame(self,height=75)
        self.controlFrames=[ParamWidget(self.controlFrame, ["int",'float','bool'][i]) for i in range(3)] #setup 3 frames inside controlframe and put into list controlframes
        send=ctk.CTkButton(self,text="send"
        ,command=self._sendOSC,
        fg_color="green",
        hover_color="#004d00"
        )


        spacing=1
        reset.grid(row=0,column=0,sticky="NWES",
        padx=spacing,pady=spacing,)
        delete.grid(row=0,column=1,sticky="NWES",
        padx=spacing,pady=spacing,)
        self.selectAvatar.grid(row=1,column=0,columnspan=2,sticky="NWES",
        padx=spacing,pady=spacing,)
        self.selectParam.grid(row=2,column=0,columnspan=2,sticky="NWES",
        padx=spacing,pady=spacing,)
        self.controlFrame.grid(row=3,column=0,columnspan=2,sticky="NWES",
        padx=spacing,pady=spacing,)
        send.grid(row=4,column=0,columnspan=2,sticky="NWES",
        padx=spacing,pady=spacing,)

    def changeControlFrame(self,typeEnum):
        for frame in self.controlFrames:
            frame.forget()
        if typeEnum!=-1:
            self.controlFrames[typeEnum].pack(fill='both')#expand=1)
    def _deletePrompt(self):
        print("asking delete prompt...")
        cont=tkms.askokcancel("WARNING","HEY STINKY, this will delete all of your local osc cache!\nthis is useful for shortening the avatar select list.\n\ncontinue?")
        if cont:
            print("deleting osc cache...")
            avi.deleteAvatars()
            self.changeControlFrame(-1)
            self.avatars=[]
            self.params=[]
            self.selectAvatar.configure(values=["ERROR"])
            self.selectParam.configure(values=["ERROR"])
            self.selectAvatar.set("Avatar")
            self.selectParam.set("Parameter")
        else:print("cancelled delete")
    def _paramSelected(self,paramName):
        print(f"selected param '{paramName}'")
        param=None
        for _param in self.params:
            if _param['name']==paramName:
                param=_param
                break
        if not param:raise ValueError("avatar missing param")
        self.changeControlFrame(["int","float","bool"].index(param['type'].lower()))
    def _sendOSC(self):
        param=None
        paramName=self.selectedParam.get()
        for _param in self.params:
            if _param['name']==paramName:
                param=_param
                break
        if not param:raise ValueError("avatar missing param")
        client.send_message(param["address"],self.controlFrame.value)
        print("sent OSC")

    def _avatarSelected(self,avatar):
        print(f"selected avatar '{avatar}'")
        self.changeControlFrame(1)
        self.changeControlFrame(-1)
        self.updateParams()
    def updateParams(self):
        print("  loading avatar params...")
        avatar=None
        for avi in self.avatars: #find avatar object by name
            if self.selectedAvatar.get()==avi.name:
                avatar=avi
                break
        if not avatar:
            print("ERROR: selected avatar does not exist")
            return
        try:
            self.params=avi.parameters
            self.selectParam.configure(values=[a['name'] for a in avi.parameters])
            self.selectParam.set("None")
            self.changeControlFrame(-1)
            print("  avatar params loaded")
        except:print("error loading params, avatar doesn't have any?")

    def updateAvatars(self):
        print("avatars updating...")
        self.avatars=[]
        for _,path in enumerate(avi.getAvatars()):
            self.avatars.append(avi.Avatar(path))
        try:
            self.selectAvatar.configure(values=[a.name for a in self.avatars])
            print("avatars updated")
            #print([a.name for a in self.avatars])
        except:print("  error setting selectAvatar values\n  fixing...")
    def start(self):
        self.updateAvatars()
        self.mainloop()
        #user closed the window
if __name__ =="__main__":
    app=AvatarToggle()
    app.start()