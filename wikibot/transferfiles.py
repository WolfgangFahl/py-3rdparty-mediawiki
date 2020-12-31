#%%
from tkinter import *
#%%
def drawGui(files):
    root = Tk()
    root.title('Select Files you want to transfer')
    root.iconbitmap('icon.ico')
    root.geometry("400x500")
    #multiplefiles
    mult=[]
    all_array=[]
    

    # Create frame
    my_frame = Frame(root)
    my_scrollbar = Scrollbar(my_frame, orient=VERTICAL,bg='#be6f20')

    #Listbox!
    my_listbox = Listbox(my_frame,width=50,yscrollcommand= my_scrollbar.set,selectmode=MULTIPLE)

    #configure scrollbar
    my_scrollbar.config(command=my_listbox.yview)
    my_scrollbar.pack(sid=RIGHT,fill=Y)
    my_frame.pack()

    my_listbox.pack(pady=15)



    for i in files:
        my_listbox.insert(END, i)
    #it will delete the file
    
    def selectAll():
        #print(my_listbox.get(0, END))
        nonlocal all_array
        all_array = my_listbox.get(0, END)
        my_label2.config(text='All Files have been selected. Now you can transfer them')
    def select():

        #print(my_listbox.curselection())
        nonlocal mult
        mult=my_listbox.curselection()
        my_label1.config(text='Files have been selected. Now you can transfer them')

    def transferFiles():
        my_label.config(text='Now you can close this application. The files are transering')

    #my_button_d = Button(root, text="Remove files", command=delete ,font='Raleway', bg="#206fbe", fg='Black')
    #my_button_d.pack(pady=10)
    my_button_s = Button(root, text="Select files",command=select, font='Raleway', bg="#206fbe", fg='Black')
    my_button_s.pack(pady=10)

    #different labels to generate text on screen when pressing different buttons
    
    global my_label
    my_label=Label(root,text='')
    my_label.pack(pady=5)
    

    global my_label1
    my_label1 = Label(root, text='')
    my_label1.pack(pady=5)
    global my_label2
    my_label2 = Label(root, text='')
    my_label2.pack(pady=5)
    if not files:
        my_label1.config(text='Empty: there are no files available in this domain.')

    my_button_sall= Button (root,text='Select All',command=selectAll, font='Raleway', bg="#206fbe", fg='Black')
    my_button_sall.pack()
    my_button_tran = Button(root, text='Transfer', command=transferFiles, font='Raleway', bg="#be205f", fg='Black')
    my_button_tran.pack()
    root.mainloop()
    return (mult,all_array)
