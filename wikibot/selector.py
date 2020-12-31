'''
Created on 2020-12-29
  @author:     Musaab Khan
  @copyright:  Musaab Khan. All rights reserved.

'''

import tkinter as tk
import sys


class Selector:
    """
    Selector Class for the GUI to select.
    """

    def __init__(self, debug=False):
        """
            Constructor
        """
        self.items = ''
        self.var = dict()
        self.count = 1
        self.debug = debug

    def __init__(self, items, debug=False):
        """
            Parameterized Constructor
        """
        self.items = items
        self.var = dict()
        self.count = 1
        self.debug = debug

    def createWindow(self, root):
        """
             create the Window for the selection list
             Args:
                root(tk.App Object): tk.App opened object
            Returns:
                None
        """
        self.items = list(map(str, self.items))
        items_by_len = sorted(self.items, key=len)
        longest_string = items_by_len[-1]
        s_long_string = items_by_len[-2]
        root.grid_rowconfigure(0, weight=1)
        root.columnconfigure(0, weight=1)

        frame_main = tk.Frame(root)
        frame_main.grid(sticky='news')

        allvar = tk.IntVar()
        allvar.set(1)
        tk.Checkbutton(frame_main, text="Select All", command=lambda: self.select_all(allvar), variable=allvar).grid(
            row=0, sticky='w', column=0)

        # Create a frame for the canvas with non-zero row&column weights
        frame_canvas = tk.Frame(frame_main)
        frame_canvas.grid(row=1, column=0, pady=(5, 0), sticky='nw')
        frame_canvas.grid_rowconfigure(0, weight=1)
        frame_canvas.grid_columnconfigure(0, weight=1)
        # Set grid_propagate to False to allow 5-by-5 buttons resizing later
        frame_canvas.grid_propagate(False)

        canvas = tk.Canvas(frame_canvas)
        canvas.grid(row=0, column=0, sticky="news")
        scrollbar = tk.Scrollbar(frame_canvas, orient='vertical', command=canvas.yview)
        scrollbar.grid(row=0, column=2, sticky='ns')
        canvas.configure(yscrollcommand=scrollbar.set)

        frame_list = tk.Frame(canvas)
        canvas.create_window((0, 0), window=frame_list, anchor='nw')

        colvar = 0
        self.count = 2
        for child in self.items:
            if self.count % 2 != 0:
                colvar = 1
            else:
                colvar = 0
            self.var[str(child)] = tk.IntVar()
            self.var[str(child)].set(1)

            tk.Checkbutton(frame_list, text=child, variable=self.var[str(child)]) \
                .grid(row=int(self.count / 2), sticky='nw', column=colvar)
            self.count += 1

        tk.Button(frame_main, text='Push', command=lambda: self.remove_states(self.items,
                                                                              self.var, root),bg='green', fg='white').grid(row=2,
                                                                                                    sticky='nw', padx=10,
                                                                                                    column=0)

        tk.Button(frame_main, text='Quit', command=lambda: self.quitSelector(root), bg='red', fg='white').grid(row=2, sticky='ne',
                                                                                         padx=10, column=0)

        frame_list.update_idletasks()

        frame_canvas.config(width=(len(longest_string) * 7)+(len(s_long_string)*7) + 80, height=300)
        # Set the canvas scrolling region
        canvas.config(scrollregion=canvas.bbox("all"))

        mousescroll = lambda x: canvas.yview_scroll(int(-1 * (x.delta / 120)), "units")
        canvas.bind_all("<MouseWheel>", mousescroll)
        root.protocol("WM_DELETE_WINDOW", lambda: self.quitSelector(root))

    def quitSelector(self, root):
        """
            Quit the python program when Quit Button is pressed.
            Args:
                root(tk.App Object): tk.App opened object
            Returns:
                None
        """
        root.destroy()
        sys.exit(0)

    def remove_states(self, items, var, root):
        """
            Quit the python program when Quit Button is pressed.
            Args:
                items(list): list of objects in selection
                var(dict): Dictionary of list items and their Tkinter selection values.
                root(tk.App Object): tk.App opened object
            Returns:
                None
        """
        if self.debug:
            print("-----Starting to remove unselected states-------")
            print("List of Items:")
            print(self.items)
            print("-----Processing-----")
        self.items = [elem for elem in items if var[str(elem)].get() != 0]
        if self.debug:
            print('List of items after processing')
            print(self.items)
            print('-----end-----')
        root.destroy()


    def getUpdateditems(self):
        """
            Getter function for the class variable items
            Returns:
                items(list): List of pages selected in GUI by user
        """
        return self.items

    def select_all(self, allvar):
        """
            Getter function for the class variable items
            Returns:
                items(list): List of pages selected in GUI by user
        """
        if allvar.get():
            for item in self.items:
                v = self.var[str(item)]
                if v.get() == 0:
                    v.set(1)
        else:
            for item in self.items:
                v = self.var[str(item)]
                if v.get():
                    v.set(0)

    @staticmethod
    def select(selectionList):
        """
        Static Function for starting the GUI Window
        Args:
            selectionList(list): List of things to select from
        Returns:
            selectionList(list): List of pages selected in GUI by user
        """
        root = tk.Tk()
        GUI = Selector(selectionList)
        GUI.createWindow(root)
        root.mainloop()
        selectionList = GUI.getUpdateditems()
        return selectionList