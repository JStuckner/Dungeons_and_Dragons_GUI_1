'''
Created on Feb 25, 2017

@author: Josh
'''
import tkinter as tk
import time

class TimerLabel(tk.Label):
    def __init__(self, master=None):
        self.var = tk.StringVar()
        tk.Label.__init__(self, master, textvariable=self.var)
        self.var.set('0 :00')
        self.t0 = int(time.time())
        self.paused = False
        self.totalTimePaused = 0
        self.pause()
            
    
    def onUpdate(self):
        if not self.paused:
            self.tNow = int(time.time())
            self.tElapsed = self.tNow - self.t0 - self.totalTimePaused
            minute = int(self.tElapsed / 60)
            sec = self.tElapsed % 60
            if sec < 10:
                stringTime = str(minute)+' :0'+str(sec)
            else:
                stringTime = str(minute)+' :'+str(sec)
            self.var.set(stringTime)
            self.after(1000, self.onUpdate)
    
    def pause(self):
        if not self.paused:
            self.paused = True
            self.tPaused = int(time.time())
    
    def start(self):
        if self.paused:
            self.paused = False
            self.totalTimePaused += (int(time.time()) - self.tPaused)
            self.onUpdate()
            
    def reset(self):
        self.var.set('0 :00')
        self.t0 = int(time.time())
        self.paused = False
        self.totalTimePaused = 0
        self.pause()
            
class MainApp(tk.Frame):
    
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.pack()
        self.timer = TimerLabel(self)
        self.butStart = tk.Button(self, text="Start", command=self.timer.start)
        self.butPause = tk.Button(self, text="Stop", command=self.timer.pause)
        self.butReset = tk.Button(self, text="Reset", command=self.timer.reset)
        self.timer.grid(row=0,column=0)
        self.butStart.grid(row=1,column=0)
        self.butPause.grid(row=2,column=0)
        self.butReset.grid(row=3,column=0)
        
myapp = MainApp()
myapp.master.title('Timer')
myapp.mainloop()     