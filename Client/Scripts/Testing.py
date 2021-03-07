from tkinter import *
from PIL import Image, ImageTk

root = Tk()
root.configure(background='red')


photo = ImageTk.PhotoImage(file ="../Pictures/building_plot_hovered.png")
bg = ImageTk.PhotoImage(file = "../Pictures/Catan_Background.png")


canvas = Canvas(root, bg="black", width=700, height=400)
canvas.pack()

bt = Button(canvas, image = photo, borderwidth=0, highlightthickness=0)
canvas.create_window(100, 100, window=bt, width=40, height=40)
mainloop()