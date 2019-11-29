import tkinter as tk
import random

def update():
    l.config(text=str(random.random()))
    root.after(1000, update)


root = tk.Tk()
l = tk.Label(text='0')
l.pack()
root.after(1000, update)
root.mainloop()