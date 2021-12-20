'''
Created on 2020-12-20

'''


class Selector:
    '''
    selector class
    '''

    def __init__(self, items):
        """
            Constructor
        """
        import tkinter as tk 
        self.items = items
        self.items = list(map(str, self.items))
        self.var = dict()
        self.count = 1
        self.checkvar = tk.IntVar(value=1)
        self.label_test = tk.StringVar()
        self.label_test.set("Select None")
        self.quitProgram = False

    def createWindow(self, root, action, title, description):
        """
            create the Window for the selection list
            Args:
               root(tk.App Object): tk.App opened object
               action(str): Type of Action
               title(str): Title of Window
               description(str): Description of Task to do
           Returns:
               None
        """
        import tkinter as tk 
        # Title
        rowCounter = 0
        root.title(title)    #set window title to given title string
        root.resizable(1, 1) #set so the window can be resized by user

        # finding optimal window size
        items_by_len = sorted(self.items, key=len)
        longest_string = items_by_len[-1]

        # Setting Message to description string
        desc = tk.Message(root, text=description)
        desc.bind("<Configure>", lambda e: desc.configure(width=e.width - 10))
        desc.pack(side="top", fill=tk.X)

        # Frame creation for Listbox
        frameList = tk.Frame(root)

        items = tk.StringVar(root)
        items.set(self.items)
        listbox = tk.Listbox(frameList, listvariable=items, selectmode="multiple", width=len(longest_string)+5)
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        listbox.select_set(0, tk.END)

        # Frame creation for select all/none checkbox
        frameSelect = tk.Frame(root)
        frameSelect.pack(side=tk.TOP, fill=tk.BOTH)
        frameList.pack(fill=tk.BOTH, expand=True)

        # label and checkbutton creation
        label = tk.Label(frameSelect, textvariable=self.label_test)
        check = tk.Checkbutton(frameSelect, text="", variable=self.checkvar,
                            command=lambda: self.select_all(listbox))
        check.pack(side=tk.LEFT, anchor="sw")
        label.pack(side=tk.LEFT, anchor="sw")

        # Scrollbar binding and creation
        scrollbar = tk.Scrollbar(frameList)
        scrollbar.pack(side=tk.RIGHT, fill=tk.BOTH)
        listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=listbox.yview)
        listbox.bind("<<ListboxSelect>>", self.updateCheck)

        #Frame for Action and Quit Buttons
        frameControl = tk.Frame(root)
        frameControl.pack(side=tk.BOTTOM, fill=tk.X)

        # Action and Quit button creation
        actionBtn = tk.Button(frameControl, text=action, bg='green', fg='white', command=lambda: self.updatePages(root, listbox))
        actionBtn.pack(side=tk.LEFT, anchor="sw")
        quitBtn = tk.Button(frameControl, text="Quit", bg='red', fg='white', command=lambda: self.quitSelector(root))
        quitBtn.pack(side=tk.RIGHT, anchor="se")

        #To destroy window and exit program if cross button is pressed
        root.protocol("WM_DELETE_WINDOW", lambda: self.quitSelector(root))

    def updateCheck(self, event):
        """
            Helper function to change state of select all checkbox
            Returns:
                event(Tk event Object): All registered events on Tkinter
        """
        if len(event.widget.curselection()) < len(self.items): #check if any item is deselected
            self.label_test.set("Select All")
            self.checkvar.set(0)
        elif len(event.widget.curselection()) == len(self.items):
            self.label_test.set("Select None")
            self.checkvar.set(1)

    def select_all(self, listbox):
        """
            Button helper function to select all list items
            Returns:
                listbox(Tk Listbox Object): listbox to update to all items
        """
        import tkinter as tk 
        if self.checkvar.get():
            listbox.select_set(0, tk.END)
            self.label_test.set("Select None")
        else:
            listbox.select_clear(0, tk.END)
            self.label_test.set("Select All")

    def updatePages(self, root, listbox):
        """
            Update function to remove unselected items from list
            Args:
                root(tk.App Object): tk.App opened object
                listbox(TK listbox Object): listbox to update
            Returns:
                None
        """
        self.items = [listbox.get(idx) for idx in listbox.curselection()] #Remove unselected items from list
        root.destroy()

    def quitSelector(self, root):
        """
            Quit the python program when Quit Button is pressed.
            Args:
                root(tk.App Object): tk.App opened object
            Returns:
                None
        """
        root.destroy()
        self.items = 'Q'


    def getUpdatedPages(self):
        """
           Getter function for the class variable items
           Returns:
               items(list): List of pages selected in GUI by user
       """
        return self.items


    @staticmethod
    def select(selectionList, action="Select", title="Selection", description=""):
        """
        Creates a GUI in which the user can select a subset of the provided selectionList.
        The user can quit the selection resulting in the return of an empty list.
        :param selectionList:
        :param action: name of the action the selection performs. Default is select
        :param title: title of the created window
        :param description: Instructions for the user (consequence of the selection)
        :return: user selected subset of the given selectionList
        """
        import tkinter as tk 
        root = tk.Tk()
        GUI = Selector(selectionList)   # Tkinter Object creation
        GUI.createWindow(root, action, title, description)  # create Window with given parameters
        root.mainloop()     # Run GUI loop
        selectionList = GUI.getUpdatedPages()   # Get selected items
        return selectionList


