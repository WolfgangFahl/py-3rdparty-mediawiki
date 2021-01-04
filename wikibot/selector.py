'''
Created on 2020-12-20

'''
from tkinter import *
from tkinter import ttk

class Selector:

    SELECT_ALL = "Select All"
    SELECT_NONE = "Select None"

    def __init__(self, pages):
        self.pages = pages
        self.var = dict()
        self.count = 1
        self.globalSelector = None

    def createWindow(self, root, action, title, description):
        # Title
        rowCounter = 0
        root.title(title)
        root.resizable(0, 0)
        desc = ttk.Label(root, text=description)
        desc.grid(row=rowCounter)
        rowCounter += 1

        # Global selector
        self.globalSelector = ttk.Checkbutton(root,
                                              text=Selector.SELECT_ALL,
                                              command=lambda: self.actionGlobalSelector(root))
        self.globalSelector.state(['!alternate'])
        self.globalSelector.grid(row=rowCounter, sticky=W, padx=9)
        rowCounter += 1
        s = ttk.Separator(root, orient=HORIZONTAL)
        s.grid(row=rowCounter)

        # List with a selectable items
        rowspanOfList = min(len(self.pages), 10)
        listFrame = ScrollableFrame(root)
        listFrame.grid(row=rowCounter, sticky='WE', rowspan=rowspanOfList, columnspan=1)
        for child in self.pages:
            self.var[child] = IntVar(root)
            chk = Checkbutton(listFrame.scrollableFrame,
                              text=child,
                              variable=self.var[child],
                              command=lambda: self.updateGlobalSelector())
            chk.grid(row=self.count, sticky='w')
            self.count += 1
        rowCounter += rowspanOfList + 1

        # Control functions
        controlFrame = ttk.Frame(root)
        controlFrame.grid(row=rowCounter, sticky=E, pady=4)
        Button(controlFrame,
               text=action,
               command=lambda: self.remove_states(self, self.pages, self.var, root)
               ).pack(side=RIGHT)
        Button(controlFrame, text='Quit', command=lambda: self.quit(root)).pack(side=RIGHT)
        rowCounter += 1

    def remove_states(self, f, pages, var, root):
        self.pages = [elem for elem in pages if var[elem].get() != 0]
        root.quit()
        self.close(root)

    def quit(self, root):
        self.pages = []
        root.quit()
        self.close(root)

    def close(self, root):
        root.destroy()

    def getUpdatedPages(self):
        return self.pages

    def actionGlobalSelector(self, root):
        if self.globalSelector.instate(['selected']):
            self.globalSelector['text'] = Selector.SELECT_NONE
            for btn in self.var.values():
                btn.set(1)
        else:
            self.globalSelector['text'] = Selector.SELECT_ALL
            for btn in self.var.values():
                btn.set(0)

    def updateGlobalSelector(self):
        """
        Updates the state of the global selector. Checks if the states of the list items matches the state of the gloabl
        state and alters the state of the global state accordingly.
        Returns:
        """
        if self.globalSelector.instate(['alternate']):
            all_selected = True
            for v in self.var.values():
                if v.get() == 0:
                    all_selected = False
                    break
            if all_selected:
                self.globalSelector.state(['selected'])
                self.globalSelector.state(['!alternate'])
        elif self.globalSelector.instate(['selected']):
            self.globalSelector.state(['alternate'])
        else:
            pass

    @staticmethod
    def select(selectionList, action="Confirm", title="Selection", description=""):
        """
        Creates a GUI in which the user can select a subset of the provided selectionList.
        The user can quit the selection resulting in the return of an empty list.
        Args:
            selectionList:
            action: name of the action the selection performs. Default is select
            title: title of the created window
            description: Instructions for the user (consequence of the selection)
        Returns:
            user selected subset of the given selectionList
        """
        root = Tk()
        GUI = Selector(selectionList)
        GUI.createWindow(root, action, title, description)
        root.protocol("WM_DELETE_WINDOW", lambda: GUI.quit(root))
        root.mainloop()
        selectionList = GUI.getUpdatedPages()
        return selectionList


class ScrollableFrame(ttk.Frame):
    def __init__(self, container, rowspan=1, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        canvas = Canvas(self)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollableFrame = ttk.Frame(canvas)
        self.scrollableFrame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )
        canvas.create_window((0, 0), window=self.scrollableFrame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.grid()
        scrollbar.grid(row=0, column=1, sticky='nse')

