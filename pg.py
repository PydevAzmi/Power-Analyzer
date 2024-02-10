from tkinter import *
from PIL import Image, ImageTk

root = Tk()
root.title("Power Analyzer")
root.resizable(height=0, width=0)
canvas = Canvas(root, height = 1020, width = 710, border=0)
canvas.pack()
img = ImageTk.PhotoImage(Image.open(r"F:\\Githup Repos\\UPS\\ui\\UPS\\code\\background.jpeg"))
ico = ImageTk.PhotoImage(Image.open(r'images.png'))
root.iconphoto(True, ico)
bg = Label(canvas, image = img)
bg.pack()
 
root.mainloop()