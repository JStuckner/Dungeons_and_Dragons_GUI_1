'''
Created on Feb 23, 2017

@author: Josh
'''
import tkinter as tk
from tkinter.font import Font
import random
import os
import glob
import json
import numpy as np
import re
import time
from tkinter.scrolledtext import ScrolledText  
import ast
from tables.tabula import rollTable, getTableNames, getTableGroups

# Returns the modifier of a stat.
def getMod(stat):
    stat = int(stat)
    return int(stat/2)-5

def loadPCs():
    PCs = []
    for file in glob.glob('characters/*.txt'):
        json_data=open(file).read() 
        PC = json.loads(json_data)
        PC['hp'] = PC['maxHP']
        PCs.append(PC)
    return PCs
            
def loadMonsters():
    published = "files/beastiary.json"
    custom = 'files/custom_monsters.json'
    json_data=open(published).read()        
    monsters = json.loads(json_data)
    json_data=open(custom).read()
    custom_monsters = json.loads(json_data)
    for monster in custom_monsters['monster']:
        monsters['monster'].append(monster)
    return monsters['monster']

def loadSpells():
    file = r"files/spells.json"
    json_data=open(file).read()        
    spells = json.loads(json_data)
      
    return spells["spell"]

def loadRules():
    file = r"files/rules.json"
    json_data=open(file, encoding="utf8").read()        
    rules = json.loads(json_data)
    return rules["rule"]
    
def loadOther():
    file = r"files/character.json"
    json_data=open(file, encoding="utf8").read()        
    other = json.loads(json_data)
    other = other['compendium']
    
    types = ['race','background','feat','spell','class']
    for type in types:
        for item in other[type]:
            item['my_type'] = type
            
    out = []
    for type in types:
        for thing in other[type]:
            out.append(thing)

    return out

def loadItems():
    file = r"files/items.json"
    json_data=open(file, encoding="utf8").read()        
    items = json.loads(json_data)

    return items["compendium"]["item"]    

def rest():
    for PC in PCs:
        PC['hp'] = PC['maxHP']   

    
def parseDice(dice):
    number = int(dice.group(1))
    size   = int(dice.group(2))
    op     = dice.group(3)
    mod    = int(dice.group(4) or 0)
    total = 0
    for _ in range(0, number):
        total = total + random.randint(1, size)

    if op == "+":
        total += mod
    elif op == "-":
        total -= mod
    elif op == "*":
        total *= mod
    elif op == "x":
        total *= mod
    elif op == "/":
        total /= mod

    return str(total)

def roll(string):
    string = string.replace('(','')
    string = string.replace(')','')
    diceRegex = "^(\d+)d(\d+)(?:([-x+*/])(\d+))?"
    dice = string.split()
    total = 0
    for i in range(len(dice)):
        diceMatch = re.match(diceRegex, dice[i])
        if diceMatch != None:
                quantity = parseDice(diceMatch)
                total += int(quantity)
                #print(dice[i],'=',quantity)

    return total

def size(string):
    d = {"L":"Large",
         "M":"Medium",
         "H":"Huge",
         "G":"Gargantuan",
         "T":"Tiny",
         "S":"Small"}
    return d['string']

class TimerLabel(tk.Label):
    def __init__(self, master=None, bd=1):
        self.var = tk.StringVar()
        tk.Label.__init__(self, master, textvariable=self.var,
                          bd=bd, relief=tk.SOLID)
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

class AutoScrollbar(tk.Scrollbar):
    '''
    A scrollbar that hides itself if it's not needed. 
    Only works if you use the grid geometry manager.
    '''
    def set(self, lo, hi):
        if float(lo) <= 0.0 and float(hi) >= 1.0:
            self.grid_remove()
        else:
            self.grid()
        tk.Scrollbar.set(self, lo, hi)

    def pack(self, *args, **kwargs):
        raise tk.TclError('Cannot use pack with this widget.')

    def place(self, *args, **kwargs):
        raise tk.TclError('Cannot use pack with this widget.')
    
class ScrollableFrame(tk.Frame):
    def __init__(self, top, *args, **kwargs):
        tk.Frame.__init__(self, top, *args, **kwargs)

        hscrollbar = AutoScrollbar(self, orient = tk.HORIZONTAL)
        hscrollbar.grid(row = 1, column = 0, sticky = 'ew')

        vscrollbar = AutoScrollbar(self, orient = tk.VERTICAL)
        vscrollbar.grid(row = 0, column = 1, sticky = 'ns')

        self.canvas = tk.Canvas(self, xscrollcommand = hscrollbar.set,
                              yscrollcommand = vscrollbar.set)
        self.canvas.grid(row = 0, column = 0, sticky = 'nsew')

        hscrollbar.config(command = self.canvas.xview)
        vscrollbar.config(command = self.canvas.yview)

        # Make the canvas expandable
        self.grid_rowconfigure(0, weight = 1)
        self.grid_columnconfigure(0, weight = 1)

        # Create the canvas contents
        self.frame = tk.Frame(self.canvas)
        self.frame.rowconfigure(1, weight = 1)
        self.frame.columnconfigure(1, weight = 1)

        self.canvas.create_window(0, 0, window = self.frame, anchor = 'nw')
        self.canvas.config(scrollregion = self.canvas.bbox('all'))    
        
        self.frame.bind('<Configure>', self.frame_changed)

    def frame_changed(self, event):
        self.frame.update_idletasks()
        self.canvas.config(scrollregion = self.canvas.bbox('all'))    
        
class selectCombatants(tk.Toplevel):
    
    def __init__(self, master=None, fighters=None):
        tk.Toplevel.__init__(self, master)
        self.title('Choose combatants')
        self.transient(master)
        self.master = master
        self.fighters = fighters
        
        # Get characters
        self.characterList = []
        self.monsters = loadMonsters()
        for PC in PCs:
            self.characterList.append(PC["name"])
        for monster in self.monsters:
            self.characterList.append(monster["name"])
        
        # Create Widgets
        self.search_var = tk.StringVar()
        self.listnumber_var = tk.StringVar()
        self.search_var.trace("w", lambda name, index, mode: self.updateList())
        self.entry = tk.Entry(self, textvariable=self.search_var, width=13)
        self.listFrom = tk.Listbox(self, width=45, height=15)
        self.scrollbar = tk.Scrollbar(self, orient=tk.VERTICAL)
        self.listTo = tk.Listbox(self, width=45, height=15, 
                    selectmode=tk.EXTENDED, yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.listTo.yview)
        self.butSetupIn = tk.Button(self, text="Add ->", 
                                    command=lambda:self.addList())
        self.butSetupOut = tk.Button(self, text="<- Remove", 
                                     command=lambda:self.removeList())
        self.butSetupFight = tk.Button(self, text="Fight!", 
                        command=lambda:self.goFight())
        self.txtSetupNum = tk.Entry(self, width=3, 
                                    textvariable=self.listnumber_var)
        self.varRollHP = tk.BooleanVar()
        self.checkRollHP = tk.Checkbutton(self, text="Roll for HP", 
                                      variable=self.varRollHP)
        self.checkRollHP.select()
        
        # Pack widgets.        
        self.entry.grid(row=0, column=0, padx=10, pady=3)
        self.listFrom.grid(row=1, column=0, padx=10, pady=3, rowspan=10)
        self.listTo.grid(row=1, column=2, padx=0,pady=3, rowspan=10)
        self.scrollbar.grid(row=1, column=3, rowspan=10, sticky=tk.N+tk.S+tk.W)
        self.txtSetupNum.grid(row=3, column=1, padx=5, pady=2)
        self.butSetupIn.grid(row=4, column=1, padx=5, pady=2)
        self.butSetupOut.grid(row=5, column=1, padx=5, pady=2)
        self.butSetupFight.grid(row=7,column=1, padx=5, pady=20)
        self.checkRollHP.grid(row=8, column=1)

        # Call to poplulate initial lists        
        self.updateList()
        self.startToList()  
        self.protocol("WM_DELETE_WINDOW", self.cancel)
        self.geometry("+%d+%d" % (master.winfo_rootx()+50,
                                  master.winfo_rooty()+50))    
        self.entry.focus_set()            
        self.wait_window(self)
             
    def startToList(self):
        if self.fighters is None:
            for PC in PCs:
                self.listTo.insert(tk.END, PC["name"]) 
                   
    def updateList(self):
        search_term = self.search_var.get()
        self.listFrom.delete(0,tk.END)

        if 'cr=' in search_term.lower():
            crList = []

            cr = search_term.lower().split('cr=')[1]
                                
            search_term= ''
            for monster in self.monsters:
                if monster['cr'] == cr:
                    crList.append(monster["name"])
            for item in crList:
                if search_term.lower() in item.lower():
                    self.listFrom.insert(tk.END, item)        

            
        else:
            for item in self.characterList:
                if search_term.lower() in item.lower():
                    self.listFrom.insert(tk.END, item)        
        
    def addList(self):
        toAdd = self.listFrom.get(self.listFrom.curselection())
        numAdd = 1
        try:
            numAdd = int(self.listnumber_var.get())
        except:
            pass

        for _ in range(numAdd):
            self.listTo.insert(tk.END, toAdd)     
            
    def removeList(self):
        removes = self.listTo.curselection()
        for i in range(len(removes)):
            self.listTo.delete(removes[i]-i)
            
    def goFight(self):   
        self.withdraw()
        self.update_idletasks()
        
        self.rollHP = self.varRollHP.get()
        
        # Get list of combatants
        if self.fighters is None:
            self.fighters = []
        for item in self.listTo.get(0,tk.END):
            for PC in PCs:
                if item.lower() == PC["name"].lower():
                    self.fighters.append(PC)        
            for monster in self.monsters:
                if item.lower() == monster["name"].lower():
                    self.fighters.append(monster.copy())
                           
        self.cancel()
        
    def cancel(self):
        self.master.focus_set()
        self.destroy()
        
class Items(tk.Toplevel):
    def __init__(self, master=None):
        tk.Toplevel.__init__(self, master)
        self.title('Items')
        self.itemSearch_var = tk.StringVar()
        self.itemSearch_var.trace("w", self.updateItemList)
        self.items= loadItems()
        self.itemList = []
        for key in self.items:
            #print(key)
            self.itemList.append(key["name"])
            
        self.infoFrame = tk.Frame(self, width=600, height=800)
        self.txtInfo = tk.Text(self.infoFrame, wrap=tk.WORD, bg='#F3E7CA')
        self.txtInfo.pack(fill=tk.BOTH, expand=True)
        self.infoFrame.grid(row=0, column=1, rowspan=4, padx=5, pady=5)
        
        self.itemEntry = tk.Entry(self, textvariable=self.itemSearch_var, width=13)
        self.listItems = tk.Listbox(self, width=45, height=15)
        self.listItems.bind('<<ListboxSelect>>', self.getItemInfo)
        self.itemInfo = tk.Button(self, text="Info", command=self.getItemInfo)
        self.itemEntry.grid(row=0, column=0, padx=5, pady=5)
        self.listItems.grid(row=1, column=0, padx=5, pady=5)
        self.itemInfo.grid(row=2, column=0, padx=5, pady=5)
        self.updateItemList()
        
    def updateItemList(self, *args):
        search_term = self.itemSearch_var.get()
        self.listItems.delete(0,tk.END)

        for item in self.itemList:
            if search_term.lower() in item.lower():
                self.listItems.insert(tk.END, item)

    def getItemInfo(self, *args):
        statdic = {'name':'Name',
                   'type':'Type',
                   'weight':'Weight',
                   'dmg1':'Damage 1',
                   'dmg2':'Damage 2',
                   'dmgType':'Damage type',
                   'property':'Property',
                   'rarity':'Rarity'}
        
        idx = self.listItems.curselection()
        selection = self.listItems.get(idx,idx)[0]

        for key in self.items:
            if key['name'] == selection:
                f = key

        t = self.txtInfo
        t.delete('0.0',tk.END)  
        
        stats = ['name', 'type', 'weight','dmg1','dmg2','dmgType',
                 'property',
                 'range','roll','rarity']
        for stat in stats:
            if f.get(stat) is not None:
                try:
                    t.insert(tk.END, statdic[stat])
                except KeyError:
                    t.insert(tk.END, stat.title())
                t.insert(tk.END, ': ')
                t.insert(tk.END, f[stat])
                t.insert(tk.END, '\n')  
        
        if f.get('text'):
            t.insert(tk.END, '\n')
            t.insert(tk.END, 'Text:')
            for text in f['text']:
                t.insert(tk.END, '  ')
                t.insert(tk.END, text)
                t.insert(tk.END, '\n')
                
        if f.get('modifier') is not None:
            t.insert(tk.END, '\n')
            t.insert(tk.END, 'Modifiers:')
            for i in range(len(f['modifier'])):
                try:
                    if f['modifier'][i].get('-category') is not None:
                        t.insert(tk.END, '\n  Category: ')
                        t.insert(tk.END, f['modifier'][i]['-category'])
                    if f['modifier'][i].get('#text') is not None:
                        t.insert(tk.END, '\n  Text: ')
                        t.insert(tk.END, f['modifier'][i]['#text'])                
                    t.insert(tk.END, '\n')
                except KeyError:
                    if f['modifier'].get('name') is not None:
                        t.insert(tk.END, '\n  name:')
                        t.insert(tk.END, f['modifier']['name'])
                    if f['modifier'].get('modifier') is not None:
                        t.insert(tk.END, '\n  attack:')
                        
                        t.insert(tk.END, f['modifier']['attack'])
                    if f['modifier'].get('text') is not None:
                        t.insert(tk.END, '\n  text:')
                        t.insert(tk.END, f['modifier']['text'])                
                    t.insert(tk.END, '\n')
                    break #Stupid way to exit loop. 
                       
class Spells(tk.Toplevel):
    def __init__(self, master=None, fighters=None):
        tk.Toplevel.__init__(self, master)
        self.title('Spells')
        self.spellSearch_var = tk.StringVar()
        self.spellSearch_var.trace("w", self.updateSpellList)
        self.spells= loadSpells()
        self.spellList = []
        for key in self.spells:
            #print(key)
            self.spellList.append(key["name"])
            
        self.infoFrame = tk.Frame(self, width=600, height=800)
        self.txtInfo = tk.Text(self.infoFrame, wrap=tk.WORD, bg='#F3E7CA')
        self.txtInfo.pack(fill=tk.BOTH, expand=True)
        self.infoFrame.grid(row=0, column=1, rowspan=4, padx=5, pady=5)
        
        self.spellEntry = tk.Entry(self, textvariable=self.spellSearch_var, width=13)
        self.listSpells = tk.Listbox(self, width=45, height=15)
        self.listSpells.bind('<<ListboxSelect>>', self.getSpellInfo)
        self.spellInfo = tk.Button(self, text="Info", command=self.getSpellInfo)
        self.spellEntry.grid(row=0, column=0, padx=5, pady=5)
        self.listSpells.grid(row=1, column=0, padx=5, pady=5)
        self.spellInfo.grid(row=2, column=0, padx=5, pady=5)
        self.updateSpellList()
        
    def updateSpellList(self, *args):
        search_term = self.spellSearch_var.get()
        self.listSpells.delete(0,tk.END)

        for item in self.spellList:
            if search_term.lower() in item.lower():
                self.listSpells.insert(tk.END, item)

    def getSpellInfo(self, *args):
        idx = self.listSpells.curselection()
        selection = self.listSpells.get(idx,idx)[0]

        for key in self.spells:
            if key['name'] == selection:
                s = key

        t = self.txtInfo
        t.delete('0.0',tk.END)            
        t.insert('1.1', '\n\n\n\n\n\n\n\n\n\n')
        
        t.insert('1.1', 'Name: ')
        t.insert('1.7', s['name'])    
        t.insert('2.1', 'Level: ')
        t.insert('2.8', s['level'])
        t.insert('3.1', 'Classes: ')
        t.insert('3.10', s['classes'])
        t.insert('4.1', 'School: ')
        t.insert('4.9', s['school']) 
        t.insert('5.1', 'Range: ')
        t.insert('5.8', s['range'])    
        t.insert('6.1', 'Components: ')
        t.insert('6.13', s['components']) 
        t.insert('7.1', 'Duration: ')
        t.insert('7.11', s['duration'])
        t.insert('8.1', 'Roll: ')
        t.insert('8.7', s.get('roll', 'N/A'))
        t.insert('9.1', 'Cast time: ')
        t.insert('9.11', s.get('time'))
        
        if type(s["text"]) is str:
            t.insert(tk.END, s["text"])
            t.insert(tk.END, '\n')
        else:
            for text in s["text"]:
                t.insert(tk.END, text)
                t.insert(tk.END, '\n')      

class Rules(tk.Toplevel):
    def __init__(self, master=None):
        tk.Toplevel.__init__(self, master)
        self.title('Rules')
        self.ruleSearch_var = tk.StringVar()
        self.ruleSearch_var.trace("w", self.updateRuleList)
        self.rules= loadRules()
        self.ruleList = []
        for key in self.rules:
            #print(key)
            self.ruleList.append(key["name"])
            
        self.infoFrame = tk.Frame(self, width=600, height=800)
        self.txtInfo = tk.Text(self.infoFrame, wrap=tk.WORD, bg='#F3E7CA')
        self.txtInfo.pack(fill=tk.BOTH, expand=True)
        self.infoFrame.grid(row=0, column=1, rowspan=4, padx=5, pady=5)
        
        self.ruleEntry = tk.Entry(self, textvariable=self.ruleSearch_var, width=13)
        self.listRules = tk.Listbox(self, width=45, height=15)
        self.listRules.bind('<<ListboxSelect>>', self.getRuleInfo)
        self.ruleInfo = tk.Button(self, text="Info", command=self.getRuleInfo)
        self.ruleEntry.grid(row=0, column=0, padx=5, pady=5)
        self.listRules.grid(row=1, column=0, padx=5, pady=5)
        self.ruleInfo.grid(row=2, column=0, padx=5, pady=5)
        self.updateRuleList()            
        
    def updateRuleList(self, *args):
        search_term = self.ruleSearch_var.get()
        self.listRules.delete(0,tk.END)

        for item in self.ruleList:
            if search_term.lower() in item.lower():
                self.listRules.insert(tk.END, item)
                
    def getRuleInfo(self, *args):
        idx = self.listRules.curselection()
        selection = self.listRules.get(idx,idx)[0]

        for key in self.rules:
            if key['name'] == selection:
                f = key

        t = self.txtInfo
        t.delete('0.0',tk.END)  
        t.insert(tk.END, f['name']+'\n\n')
        
        if len(f['text'][0]) == 1:
            t.insert(tk.END, f['text'])
            t.insert(tk.END, '\n')
        else:
            for text in f['text']:
                t.insert(tk.END, text)
                t.insert(tk.END, '\n')
                
class Other(tk.Toplevel):
    def __init__(self, master=None):
        tk.Toplevel.__init__(self, master)
        self.title('Items')
        self.itemSearch_var = tk.StringVar()
        self.itemSearch_var.trace("w", self.updateItemList)
        self.items= loadOther()
        self.itemList = []
        for key in self.items:
            self.itemList.append(key["name"])
            
        self.infoFrame = tk.Frame(self, width=600, height=800)
        self.txtInfo = tk.Text(self.infoFrame, wrap=tk.WORD, bg='#F3E7CA')
        self.txtInfo.pack(fill=tk.BOTH, expand=True)
        self.infoFrame.grid(row=0, column=1, rowspan=4, padx=5, pady=5)
        
        self.itemEntry = tk.Entry(self, textvariable=self.itemSearch_var, width=13)
        self.listItems = tk.Listbox(self, width=45, height=15)
        self.listItems.bind('<<ListboxSelect>>', self.getItemInfo)
        self.itemInfo = tk.Button(self, text="Info", command=self.getItemInfo)
        self.itemEntry.grid(row=0, column=0, padx=5, pady=5)
        self.listItems.grid(row=1, column=0, padx=5, pady=5)
        self.itemInfo.grid(row=2, column=0, padx=5, pady=5)
        self.updateItemList()
        
    def updateItemList(self, *args):
        search_term = self.itemSearch_var.get()
        self.listItems.delete(0,tk.END)

        for item in self.itemList:
            if search_term.lower() in item.lower():
                self.listItems.insert(tk.END, item)

    def getItemInfo(self, *args):
        
        statdic = {'name':'Name',
                   'weight':'Weight',
                   'dmg1':'Damage 1',
                   'dmg2':'Damage 2',
                   'dmgType':'Damage type',
                   'property':'Property',
                   'rarity':'Rarity'}
        
        idx = self.listItems.curselection()
        selection = self.listItems.get(idx,idx)[0]

        for key in self.items:
            if key['name'] == selection:
                f = key

        t = self.txtInfo
        t.delete('0.0',tk.END)  
        t.insert(tk.END, f['my_type'].title() + ' - ' + f['name'] + '\n')
        
        stats = ['size','speed','ability', 'proficiency',
                 'level','components','duration','classes',
                 'time','school',
                 'weight','dmg1','dmg2','dmgType',
                 'property','prerequisite',
                 'range','roll','rarity']
        for stat in stats:
            if f.get(stat) is not None:
                try:
                    t.insert(tk.END, statdic[stat])
                except KeyError:
                    t.insert(tk.END, stat.title())
                t.insert(tk.END, ': ')
                t.insert(tk.END, f[stat])
                t.insert(tk.END, '\n')  
        
        if f.get('text'):
            t.insert(tk.END, '\n')
            t.insert(tk.END, 'Text:')
            for text in f['text']:
                t.insert(tk.END, '  ')
                t.insert(tk.END, text)
                t.insert(tk.END, '\n')
                
        if f.get('trait') is not None:
            t.insert(tk.END, '\n\n')
            t.insert(tk.END, 'Traits:')
            for i in range(len(f['trait'])):
                try:
                    if f['trait'][i].get('name') is not None:
                        t.insert(tk.END, '\n  name: ')
                        t.insert(tk.END, f['trait'][i]['name'])
                    if f['trait'][i].get('trait') is not None:
                        t.insert(tk.END, '\n  attack: ')
                        t.insert(tk.END, f['trait'][i]['attack'])
                    if f['trait'][i].get('text') is not None:
                        t.insert(tk.END, '\n  text: ')
                    if  len(f['trait'][i]['text'][0]) == 1:
                        t.insert(tk.END, f['trait'][i]['text'])
                    else:
                        for text in f['trait'][i]['text']:
                            text.strip('\n')
                            t.insert(tk.END, '\n    ' + text)             
                    t.insert(tk.END, '\n')
                except KeyError:
                    if f['trait'].get('name') is not None:
                        t.insert(tk.END, '\n  name: ')
                        t.insert(tk.END, f['trait']['name'])
                    if f['trait'].get('trait') is not None:
                        t.insert(tk.END, '\n  attack: ')
                        
                        t.insert(tk.END, f['trait']['attack'])
                    if f['trait'].get('text') is not None:
                        t.insert(tk.END, '\n  text: ')
                        t.insert(tk.END, f['trait']['text'])                
                    t.insert(tk.END, '\n')
                    break #Stupid way to exit loop.   
                    
        if f.get('modifier') is not None:
            t.insert(tk.END, '\n')
            t.insert(tk.END, 'Modifiers:')
            for i in range(len(f['modifier'])):
                try:
                    if f['modifier'][i].get('-category') is not None:
                        t.insert(tk.END, '\n  Category: ')
                        t.insert(tk.END, f['modifier'][i]['-category'])
                    if f['modifier'][i].get('#text') is not None:
                        t.insert(tk.END, '\n  Text: ')
                        t.insert(tk.END, f['modifier'][i]['#text'])                
                    t.insert(tk.END, '\n')
                except KeyError:
                    if f['modifier'].get('name') is not None:
                        t.insert(tk.END, '\n  name:')
                        t.insert(tk.END, f['modifier']['name'])
                    if f['modifier'].get('modifier') is not None:
                        t.insert(tk.END, '\n  attack:')
                        
                        t.insert(tk.END, f['modifier']['attack'])
                    if f['modifier'].get('text') is not None:
                        t.insert(tk.END, '\n  text:')
                        t.insert(tk.END, f['modifier']['text'])                
                    t.insert(tk.END, '\n')
                    break #Stupid way to exit loop. 
            
class Combat(tk.Toplevel):
    
    def __init__(self, fighters, rollHP, master=None):
        tk.Toplevel.__init__(self, master)
        self.title('Combat')

        #self.geometry('200x100')
        
        # Variables.
        self.fighters = fighters
        self.rollHP = rollHP
        self.damage = tk.StringVar()
        self.adjustedDamage = tk.StringVar()
        self.varModDamage = tk.IntVar()
        self.damage.trace('w', self.updateDamageVar)
        self.nameWidth = 5
        self.canvasStartWidth = 500
        self.canvasWidth = self.nameWidth + self.canvasStartWidth
        self.varRoll = tk.StringVar()
        self.whoseTurn = 0
        pad = 5
        
        self.varInfo = tk.StringVar()
        self.varInfo.set(self.fighters[0])
        self.varInfo.trace('w', self.updateInfo)

        # Frames
        self.miscFrame = tk.Frame(self, relief=tk.SOLID, bd=1, width=600, height=200)
        self.fightFrame = tk.Frame(self, relief=tk.SOLID, bd=1, width=600, height=300)
        self.infoFrame = tk.Frame(self, relief=tk.SOLID, bd=1, width=1, height=1)
        self.miscFrame.grid(row=0, column=0, padx=5, pady=5, ipadx=5, ipady=5)        
        self.fightFrame.grid(row=1, column=0, padx=5, pady=5, ipadx=5, ipady=5)
        self.infoFrame.grid(row=0, column=1, padx=5, pady=5, ipadx=5, ipady=5, rowspan=2)

        #self.miscFrame.columnconfigure(0, weight=1)
        
        # infoFrame
        self.textInfo = ScrolledText(self.infoFrame, wrap=tk.WORD, bg='#F3E7CA')
        self.textInfo.pack(expand=True, fill=tk.BOTH)
        
        # miscFrame
        self.miscFrameOptions = tk.Frame(self.miscFrame)
        self.miscFrameDamge = tk.Frame(self.miscFrame)
        self.txtDamage = tk.Entry(self.miscFrameDamge, textvariable=self.damage)
        self.labelDamage = tk.Label(self.miscFrameDamge, text="Damage:")
        self.butAddFighters = tk.Button(self.miscFrameOptions, text="Add fighters", 
                                        command=self.addFighters)
        self.miscFrameRoll = tk.Frame(self.miscFrame)
        self.textRoll = tk.Entry(self.miscFrameRoll, textvariable=self.varRoll, width=10)
        self.labelRoll = tk.Label(self.miscFrameRoll, text="Dice:")
        self.butRollDice = tk.Button(self.miscFrameRoll, text="Roll", command=self.rollDice)
        self.miscFrameTurn = tk.Frame(self.miscFrame)
        self.butNextTurn = tk.Button(self.miscFrameTurn, text="Next turn", command = self.nextTurn)
        self.butPrevTurn = tk.Button(self.miscFrameTurn, text="Previous turn", 
                                     command = self.prevTurn)
        self.miscFrameMod = tk.Frame(self.miscFrame)
        self.radFull = tk.Radiobutton(self.miscFrameMod, text="Full damage",
                                      variable=self.varModDamage, value=1, 
                                      command=self.updateDamageVar)
        self.radFull.select()
        self.radHalf = tk.Radiobutton(self.miscFrameMod, text="Half damage",
                                      variable=self.varModDamage, value=2, 
                                      command=self.updateDamageVar)
        self.radQuart = tk.Radiobutton(self.miscFrameMod, text="Quarter damage",
                                      variable=self.varModDamage, value=4, 
                                      command=self.updateDamageVar) 
        self.butRest = tk.Button(self.miscFrameOptions, text="Rest", command=self.rest)     

        self.miscFrame.grid(row=0, column=0, padx=pad, pady=pad)
        self.miscFrameOptions.grid(row=0, column=0, padx=pad, pady=pad)
        self.butAddFighters.grid(row=0,column=0, padx=pad, pady=pad)
        self.butRest.grid(row=0, column=1, padx=pad, pady=pad)
        self.miscFrameDamge.grid(row=1,column=0, padx=pad, pady=pad)
        self.labelDamage.grid(row=0,column=0, padx=pad, pady=pad)
        self.txtDamage.grid(row=0, column=1, padx=5, pady=5)
        self.miscFrameMod.grid(row=2,column=0, padx=pad, pady=pad)
        self.radFull.grid(row=0, column=0, padx=5, pady=5)
        self.radHalf.grid(row=0, column=1, padx=5, pady=5)
        self.radQuart.grid(row=0, column=2, padx=5, pady=5)
        self.miscFrameRoll.grid(row=3,column=0, padx=pad, pady=pad)       
        self.butRollDice.grid(row=0, column=2, padx=pad, pady=pad)
        self.labelRoll.grid(row=0, column=0, padx=pad, pady=pad)
        self.textRoll.grid(row=0, column=1, padx=pad, pady=pad)
        self.miscFrameTurn.grid(row=4,column=0, padx=pad, pady=pad) 
        self.butNextTurn.grid(row=0, column=1, padx=pad, pady=pad)
        self.butPrevTurn.grid(row=0, column=0, padx=pad, pady=pad)    
                   
        # Header labels
        self.hFrame = tk.Frame(self.fightFrame)
        headings = ["Init", "Name", "Tag", "AC", "HP", "Turn", "Total"]
        widths = [5,self.nameWidth,17,3,3,10, 10]
        numHeaders = len(headings)
        self.headingLabels = []
        for i, heading in enumerate(headings):
            self.headingLabels.append(tk.Label(self.hFrame, text=heading, width=widths[i], anchor='w', justify=tk.LEFT))
            self.headingLabels[i].grid(row=0, column=i) 
                    
        # Scrolling combat frame widgets.

        self.cFrame = tk.Frame(self.fightFrame, bd=0)
        self.cCanvas = tk.Canvas(self.cFrame, bd=0)
        self.insideFrame = tk.Frame(self.cCanvas, bd=0)
        self.cScroll = tk.Scrollbar(self.cFrame, orient='vertical', command=self.cCanvas.yview)
        self.cCanvas.configure(yscrollcommand=self.cScroll.set)
        self.cScroll.pack(side='right', fill='y')
        self.cCanvas.pack(side='left')
        self.cCanvas.create_window((0,0), window=self.insideFrame,anchor='nw')
        self.insideFrame.bind('<Configure>', self.frameConfig)
        self.combatFrames = []
        for fighter in self.fighters:
            self.combatFrames.append(
                CombatFrame(self.insideFrame,fighter,self.adjustedDamage, self.rollHP, self.varInfo))
            # Potentially increase the space for combatant names.
            self.nameWidth = max(self.nameWidth,len(fighter['name']))
            self.canvasWidth = self.nameWidth + self.canvasStartWidth
        self.configureCombatFrame()
        startFrame = self.combatFrames[self.order['index'][0]]
        startFrame.configure(bd=2, relief=tk.SOLID)
        
        self.cFrame.bind("<Enter>", self._bound_to_mousewheel)
        self.cFrame.bind("<Leave>", self._unbound_to_mousewheel)
            
        
        
                   
        # Arrange widgets
        self.cFrame.grid(row=1, column=0, columnspan=numHeaders,padx=0, pady=pad, ipadx=0, ipady=0)
        self.arrangeCombatants()
        self.hFrame.grid(row=0, column=0)

    def rest(self):
        rest()
        for c in self.combatFrames:
            for PC in PCs:
                if c.c['name'] == PC['name']:
                    c.HP.set(PC['hp']) 
                        
    def updateDamageVar(self, *args):
        try:
            self.adjustedDamage.set(str(int(int(self.damage.get())/self.varModDamage.get())))
        except ValueError:
            pass

    def nextTurn(self):
        self.whoseTurn +=1
        
        if self.whoseTurn > len(self.fighters)-1:
            self.whoseTurn = 0
        for frame in self.combatFrames:
            frame.configure(bd=0)
            frame.turnTimer.pause()
            frame.totalTimer.pause()
        active = self.combatFrames[self.order['index'][self.whoseTurn]]
        active.configure(bd=2, relief=tk.SOLID)
        active.totalTimer.start()
        active.turnTimer.reset()
        active.turnTimer.start()

    def prevTurn(self):
        self.whoseTurn -=2
        if self.whoseTurn < -1:
            self.whoseTurn = len(self.fighters)-2
        self.nextTurn()
        
    def rollDice(self):
        string = self.varRoll.get()
        total = roll(string)
        self.damage.set(total)

    def addFighters(self):
        numberOld = len(self.fighters)
        selectDialog = selectCombatants(self, self.fighters)
        rollHP = selectDialog.rollHP
        numberNew = len(selectDialog.fighters) -numberOld
        newFighters = []
        if numberNew > 0:
            newFighters = self.fighters[-numberNew:]
        for fighter in newFighters:
            self.combatFrames.append(
                CombatFrame(self.insideFrame,fighter,self.damage, rollHP, self.varInfo))  
            self.nameWidth = max(self.nameWidth,len(fighter['name']))
            self.canvasWidth = self.nameWidth + self.canvasStartWidth
             
        self.configureCombatFrame()
       
    def configureCombatFrame(self):
        # Reconfigure combat frame    
        height = min(400, len(self.fighters)*32)
        self.cCanvas.configure(height=height, width=self.canvasWidth)        
        self.arrangeCombatants()
        self.headingLabels[1].configure(width=self.nameWidth)   
        
        for frame in self.combatFrames:
            frame.lblName.configure(width=self.nameWidth)    
            
        self.hFrame.grid(row=0, column=0)
        self.cScroll.pack(side='right', fill='y')
        self.cCanvas.pack(side='left')
        
    def arrangeCombatants(self):   
        self.order = np.zeros(len(self.combatFrames),
                         dtype=[('index', (int)),('roll', (int))])
        for idx, frame in enumerate(self.combatFrames):
            self.order['index'][idx]=idx
            self.order['roll'][idx]=frame.init

        # Sort Initiative
        self.order['roll'] = -self.order['roll']
        self.order.sort(order='roll')
        self.order['roll'] = -self.order['roll']
        
        for i in range(len(self.order)):
            self.combatFrames[self.order['index'][i]].grid(row=i, column=0)
        
    def _bound_to_mousewheel(self, event):
        self.bind_all("<MouseWheel>", self.onMouseWheel)  
    
    def _unbound_to_mousewheel(self, event):
        self.unbind_all("<MouseWheel>") 
        
    def updateInfo(self, *args):
        
        
        # Font information
        red = '#8A1717'
        name = Font(size=28, weight='bold')
        type = Font(size=8, slant='italic')
        stat = Font(size=12)
        
        
        
        
        text = self.varInfo.get()
        #text = text.replace("'", "\"")
        f = ast.literal_eval(text)
        t = self.textInfo
        t.delete('0.0',tk.END)
        t.insert('1.1', '\n\n\n\n\n\n\n\n')
        

        t.insert('1.1', f['name'])
        t.tag_add("name", "1.0","1.100")
        t.tag_config("name", foreground=red, font=name)
        t.insert('2.1', 'Ac: ')
        t.insert('2.7', f['ac'])
        t.insert('3.1', 'HP: ')
        t.insert('3.7', f['hp'])

        t.insert('5.1', '  Str    Dex    Con    Int    Wis    Cha ')
        Str = str(f['str'])+'('+str(getMod(int(f['str'])))+')      '
        t.insert('6.1',Str)
        dex = str(f['dex'])+'('+str(getMod(int(f['dex'])))+')     '
        t.insert('6.8',dex)
        con = str(f['con'])+'('+str(getMod(int(f['con'])))+')     '
        t.insert('6.15',con)
        Int = str(f['int'])+'('+str(getMod(int(f['int'])))+')     '
        t.insert('6.22',Int)
        wis = str(f['wis'])+'('+str(getMod(int(f['wis'])))+')     '
        t.insert('6.29',wis)
        cha = str(f['cha'])+'('+str(getMod(int(f['cha'])))+')     '
        t.insert('6.36',cha)

        stats = ['cr', 'type', 'alignment', 'speed', 'save', 'skill', 'senses',
                'passive', 'languages', 'immune', 'resist', 'vulnerable',
                 'bonuscarry', 'spellDC',
                 'maxHP','init']
        for stat in stats:
            if f.get(stat) is not None:
                t.insert(tk.END, stat.title())
                t.insert(tk.END, ': ')
                t.insert(tk.END, f[stat])
                t.insert(tk.END, '\n')

        if f.get('trait') is not None:
            t.insert(tk.END, '\n\n')
            t.insert(tk.END, 'Traits:')
            for i in range(len(f['trait'])):
                try:
                    if f['trait'][i].get('name') is not None:
                        t.insert(tk.END, '\n  name:')
                        t.insert(tk.END, f['trait'][i]['name'])
                    if f['trait'][i].get('trait') is not None:
                        t.insert(tk.END, '\n  attack:')
                        t.insert(tk.END, f['trait'][i]['attack'])
                    if f['trait'][i].get('text') is not None:
                        t.insert(tk.END, '\n  text:')
                        t.insert(tk.END, f['trait'][i]['text'])                
                    t.insert(tk.END, '\n')
                except KeyError:
                    if f['trait'].get('name') is not None:
                        t.insert(tk.END, '\n  name:')
                        t.insert(tk.END, f['trait']['name'])
                    if f['trait'].get('trait') is not None:
                        t.insert(tk.END, '\n  attack:')
                        
                        t.insert(tk.END, f['trait']['attack'])
                    if f['trait'].get('text') is not None:
                        t.insert(tk.END, '\n  text:')
                        t.insert(tk.END, f['trait']['text'])                
                    t.insert(tk.END, '\n')
                    break #Stupid way to exit loop.

                    
        if f.get('action') is not None:
            t.insert(tk.END, '\n\n')
            t.insert(tk.END, 'Actions:')
            for i in range(len(f['action'])):
                try:
                    if f['action'][i].get('name') is not None:
                        t.insert(tk.END, '\n  name:')
                        t.insert(tk.END, f['action'][i]['name'])
                    if f['action'][i].get('attack') is not None:
                        t.insert(tk.END, '\n  attack:')
                        t.insert(tk.END, f['action'][i]['attack'])
                    if f['action'][i].get('text') is not None:
                        t.insert(tk.END, '\n  text:')
                        t.insert(tk.END, f['action'][i]['text'])                
                    t.insert(tk.END, '\n')
                except KeyError:
                    if f['action'].get('name') is not None:
                        t.insert(tk.END, '\n  name:')
                        t.insert(tk.END, f['action']['name'])
                    if f['action'].get('attack') is not None:
                        t.insert(tk.END, '\n  attack:')
                        t.insert(tk.END, f['action']['attack'])
                    if f['action'].get('text') is not None:
                        t.insert(tk.END, '\n  text:')
                        t.insert(tk.END, f['action']['text'])                
                    t.insert(tk.END, '\n')
                    break #Stupid way to exit loop.

            
        if f.get('legendary') is not None:
            t.insert(tk.END, '\n\n')
            t.insert(tk.END, 'Legendary:')
            for i in range(len(f['legendary'])):
                try:
                    if f['legendary'][i].get('name') is not None:
                        t.insert(tk.END, '\n  name:')
                        t.insert(tk.END, f['legendary'][i]['name'])
                    if f['legendary'][i].get('attack') is not None:
                        t.insert(tk.END, '\n  attack:')
                        t.insert(tk.END, f['legendary'][i]['attack'])
                    if f['legendary'][i].get('text') is not None:
                        t.insert(tk.END, '\n  text:')
                        t.insert(tk.END, f['legendary'][i]['text'])                
                    t.insert(tk.END, '\n')
                except KeyError:
                    if f['legendary'].get('name') is not None:
                        t.insert(tk.END, '\n  name:')
                        t.insert(tk.END, f['legendary']['name'])
                    if f['legendary'].get('attack') is not None:
                        t.insert(tk.END, '\n  attack:')
                        t.insert(tk.END, f['legendary']['attack'])
                    if f['legendary'].get('text') is not None:
                        t.insert(tk.END, '\n  text:')
                        t.insert(tk.END, f['legendary']['text'])                
                    t.insert(tk.END, '\n')                
                    break #Stupid way to exit loop. 
        
    def frameConfig(self, event):   
        height = min(600, len(self.fighters)*32)
        self.cCanvas.configure(scrollregion=self.cCanvas.bbox("all"),width=self.canvasWidth,height=height)
        
    def onMouseWheel(self, event):
        self.cCanvas.yview_scroll(int(-1*event.delta/120), "units")
                                
class CombatFrame(tk.Frame):

    def __init__(self, parent, combatant, dmgVar, rollHP, info=None):
        
        tk.Frame.__init__(self, parent)
        self.c = combatant
        self.info = info

        
        # Format data type mismatch between monsters and pc
        if type(self.c['ac']) is str:
            self.c['ac'] = int(self.c['ac'].split()[0])
        if type(self.c['hp']) is str: 
            if rollHP: 
                try:
                    hp = self.c['hp'].split()[1]
                    self.c['hp'] = roll(hp)
                except AttributeError:
                    self.c['hp'] = int(self.c['hp'].split()[0]) 
            else:
                self.c['hp'] = int(self.c['hp'].split()[0])          
       
        # Variables
        self.dmgVar = dmgVar
        self.HP = tk.StringVar(self)
        self.HP.set(self.c['hp'])
        self.HP.trace("w", self.HPTrace)  

            
                      
        # Roll initiative
        if 'init' not in self.c:
            self.c['init'] = getMod(self.c['dex'])
            
        if 'initadv' in self.c and self.c['initadv'] == 1: 
            #if combatant has advantage on init.
            self.init = (max(random.randint(1,20),random.randint(1,20)) + 
                         self.c['init'])
        else:
            self.init = random.randint(1,20) + self.c['init']
            
        # Create GUI elements
        self.lblInit = tk.Label(self, text=self.init, width=2)
        self.lblName = tk.Label(self, text=self.c['name'], width=10, anchor='w')
        self.textHP = tk.Entry(self, textvariable=self.HP, width=4)
        self.lblTag = tk.Entry(self, width=20)
        self.lblAc = tk.Label(self, text=self.c['ac'], width=2)
        self.butHit = tk.Button(self, text='Hit', command=self.hit)
        self.butInfo = tk.Button(self, text='Info', command=self.updateInfo)
        self.turnTimer = TimerLabel(self, bd=1)
        self.totalTimer = TimerLabel(self, bd=1)
                
        # Pack GUI elements.
        pad = 3
        self.lblInit.grid(row=0, column=0, padx=pad, pady=pad)
        self.lblName.grid(row=0, column=1, padx=pad, pady=pad)
        self.lblTag.grid(row=0, column=2, padx=pad, pady=pad)
        self.lblAc.grid(row=0, column=3, padx=pad, pady=pad)
        self.textHP.grid(row=0, column=4, padx=pad, pady=pad)
        self.butHit.grid(row=0, column=5, padx=pad, pady=pad)
        self.butInfo.grid(row=0, column=6, padx=pad, pady=pad)
        self.turnTimer.grid(row=0, column=7, padx=pad, pady=pad)
        self.totalTimer.grid(row=0, column=8, padx=pad, pady=pad)

    def hit(self):
        try:
            newHP = int(self.HP.get())-int(self.dmgVar.get())
            self.HP.set(str(newHP))
        except ValueError:
            print("Check the user input, ", os.getlogin(), '.', sep='')
  
    def HPTrace(self, *args):
        try:
            self.c['hp'] = int(self.HP.get())
        except ValueError:
            if self.HP.get() != '':
                print("Check the user input, ", os.getlogin(), '.', sep='')
                
    def updateInfo(self):
        # Info is a passed tkinter variable with a trace command.
        # When it is changed, the Combat class updates the info box.
        self.info.set(self.c)

class Tables(tk.Toplevel):
    
    def __init__(self, master=None):
        tk.Toplevel.__init__(self, master)
        self.title('Random tables')
        # Frame
        self.frame = tk.Frame(self)
        self.frame.grid(row=0, column=0)

        #Roll Table        
        groups = getTableGroups()
        tables = getTableNames(groups[0])

        self.groupvar = tk.StringVar(self)
        self.groupvar.set(groups[0])
        self.tablevar = tk.StringVar(self)
        self.tablevar.set(tables[0])
        self.txtTablevar = tk.StringVar(self)

        self.groupvar.trace('w', self.update_options)
        
        self.group = tk.OptionMenu(self.frame, self.groupvar, *groups)
        self.table = tk.OptionMenu(self.frame, self.tablevar, *tables)
        self.txtTable = tk.Entry(self.frame, width=6)
        self.butTable = tk.Button(self.frame,
                                  text="Roll on table",
                                  command=lambda:self.roll((self.groupvar.get(),self.tablevar.get(),self.txtTable.get())))


        self.group.grid(row=0, column=0)
        self.table.grid(row=0, column=1)
        self.txtTable.grid(row=0, column=2)
        self.butTable.grid(row=0, column=3)

    def update_options(self, *args):
        tables = getTableNames(self.groupvar.get())
        menu = self.table['menu']
        menu.delete(0,'end')
        for i in tables:
            menu.add_command(label=i, command=lambda val=i:self.tablevar.set(val))
        self.tablevar.set(tables[0])

    def roll(self, argv):
        output = rollTable(argv, retString=True)

        # Find the total gold value of the treasure.
        
        if argv[0] == 'treasure':
            total = 0
            flagMult = 1
            interp = re.sub(',','',output) #Delete commas
            interp = re.sub("\)",'',interp)
            interp = re.sub("\(",'',interp)
            interp = interp.split()
            for i, word in enumerate(interp):
                # Flag '2x' or 'ix' to multiply next gold value
                if word[-1] == 'x':
                    try:
                        flagMult = int(word[:-1])
                        
                    except:
                        pass                       
                        
                if word == 'cp':
                    total += flagMult*int(interp[i-1])/100
                    flagMult = 1
                if word == 'sp':
                    total += flagMult*int(interp[i-1])/10
                    flagMult = 1
                if word == 'gp':
                    total += flagMult*int(interp[i-1])
                    flagMult = 1
                if word == 'pp':
                    total += flagMult*int(interp[i-1])*10
                    flagMult = 1
                    
            output += ' TOTAL GOLD VALUE: ' + str(total) + '(' + str(total/4) + ').\n' 
            
        #self.write(output)
        print(output)
             

class MainApp(tk.Frame):
    
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.pack()
        width = 200
        height = 200
        pad= 5
        
        self.combatFrame = tk.LabelFrame(self, text="Combat related:", 
                                         width=width, height=height,
                                         padx=pad, pady=pad)
        self.rulesFrame = tk.LabelFrame(self, text="Info/Rules:",
                                        width=width, height=height,
                                        padx=pad, pady=pad)
        self.utilFrame = tk.LabelFrame(self, text="Utility:",
                                       width=width, height=height,
                                       padx=pad, pady=pad)
        self.combatFrame.grid(row=0, column=0)
        self.rulesFrame.grid(row=1, column=0)
        self.utilFrame.grid(row=2, column=0)
        self.combatFrame.columnconfigure(0, pad=10)
        self.combatFrame.columnconfigure(1, pad=10)
        self.rulesFrame.columnconfigure(0, pad=10)
        self.rulesFrame.columnconfigure(1, pad=10)
        self.rulesFrame.columnconfigure(2, pad=10)
        self.rulesFrame.columnconfigure(3, pad=10)
        
        self.butFight = tk.Button(self.combatFrame, text="Fight", command=self.fight, padx=pad, pady=pad)
        self.butFight.grid(row=0,column=0)
        self.butRest = tk.Button(self.combatFrame, text="Rest", command=rest, padx=pad, pady=pad)
        self.butRest.grid(row=0,column=1)
        
        self.butSpells = tk.Button(self.rulesFrame, text="Spells", command=self.spells, padx=pad, pady=pad)
        self.butSpells.grid(row=0, column=0)       
        self.butItems = tk.Button(self.rulesFrame, text="Items", command=self.items, padx=pad, pady=pad)
        self.butItems.grid(row=0, column=1)      
        self.butOther = tk.Button(self.rulesFrame, text="Character", command=self.other, padx=pad, pady=pad)
        self.butOther.grid(row=0, column=2)    
        self.butRules = tk.Button(self.rulesFrame, text="Rules", command=self.rules, padx=pad, pady=pad)
        self.butRules.grid(row=0, column=3)

        self.butTables = tk.Button(self.utilFrame, text="Random Tables", command=self.tables, padx=pad, pady=pad)
        self.butTables.grid(row=0, column=0)
        
    def fight(self):
        selectDialog = selectCombatants(self)
        fighters = selectDialog.fighters
        rollHP = selectDialog.rollHP
        Combat(fighters, rollHP)
        
    def spells(self):
        Spells()
        
    def items(self):
        Items()

    def other(self):
        Other()
        
    def rules(self):
        Rules()

    def tables(self):
        Tables()

if __name__ == "__main__":  
    PCs = loadPCs()    
    myapp = MainApp()
    myapp.master.title('DnD GUI')
    myapp.mainloop()      

