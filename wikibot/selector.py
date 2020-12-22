'''
Created on 2020-12-20

'''
from tkinter import *
from tkinter import ttk

class Selector:
    def __init__(self,pages):
        self.pages= pages
        self.var = dict()
        self.count = 1
    def createWindow(self, root):
        print(self.pages)
        for child in self.pages:
            self.var[child]=IntVar()
            chk = Checkbutton(root, text=child, variable=self.var[child]).grid(row=self.count,sticky= W)
            self.count += 1
        Button(root, text='Push', command=lambda : self.remove_states(self,self.pages,self.var,root)).grid(row=self.count+1, sticky=W, pady=4)
        Button(root, text='Quit', command=root.quit).grid(row=self.count+2, sticky=W, pady=4)
    def remove_states(self,f,pages,var,root):
        self.pages= [ elem for elem in pages if var[elem].get()!= 0]
        root.quit()
    def getUpdatedPages(self):
        return self.pages
    
    
    @staticmethod
    def select(selectionList):
        root=Tk()
        GUI=Selector(selectionList)
        GUI.createWindow(root)
        root.mainloop()
        selectionList=GUI.getUpdatedPages()
        return selectionList