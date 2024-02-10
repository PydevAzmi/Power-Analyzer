import tkinter as tk
import customtkinter
from tkinter import * 
from PIL import Image, ImageTk
import serial
import serial.tools.list_ports as serialport

class PowerAnalyzer(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self,*args, **kwargs)

        self.title("Power Analyzer")
        self.resizable(height=0, width=0)
        ico = ImageTk.PhotoImage(Image.open(r'images.png'))
        self.iconphoto(True, ico)
        
        container = customtkinter.CTkFrame(self)
        container.pack(side="top", fill="both", expand=True)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for Frame in (StartPage ,PageOne ):
            frame = Frame(container, self)
            self.frames[Frame] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(PageOne)

    def show_frame(self, container):
        frame = self.frames[container]
        frame.tkraise()

    def set_bg(self, canvas):
        my_image = customtkinter.CTkImage(light_image=Image.open(r"background.jpeg"),
                                  size=(1030, 720))
        image_label = customtkinter.CTkLabel(canvas, image=my_image, text="")
        image_label.image = my_image
        image_label.pack()        
    
class StartPage(customtkinter.CTkFrame):
    def __init__(self, parent, controller):
        customtkinter.CTkFrame.__init__(self, parent)
        canvas = customtkinter.CTkCanvas(self)
        canvas.pack()
        controller.set_bg(canvas)

        canvas1 = customtkinter.CTkFrame(canvas, height=350, width=350,
                                        fg_color="white",bg_color="#0171B1", corner_radius=30)
        canvas1.place(relx=0.3, rely=0.25)

        label1 = customtkinter.CTkLabel(canvas1, text="Power Analyzer", font=("Arial",36) ,text_color="black")
        label1.place(relx=0.48, rely=0.15, anchor=CENTER)

        label2 = customtkinter.CTkLabel(canvas1, text="Enter Hours Range:", font=("Arial",18) ,text_color="#555555")
        label2.place(relx=0.5, rely=0.4, anchor=CENTER)

        self.hours_range_entry = customtkinter.CTkEntry(canvas1, placeholder_text="e.g., 1-24", width=200, text_color="black", fg_color="#ffffff")
        self.hours_range_entry.place(relx=0.5, rely=0.5, anchor=CENTER)
        self.hours_range_entry.bind('<Return>',command = self.start_listening)

        button = customtkinter.CTkButton(canvas1, text="Start Listening", height=50, width=200,
                                        font=("Arial",18), text_color="White", fg_color=( "#0721F4","green"),
                                        command = self.start_listening)
        button.place(relx=0.5, rely=0.75, anchor=CENTER)
        
        self.warn_lbl = customtkinter.CTkLabel(canvas1, font=("Arial",10), text="" ,text_color="red")
        self.warn_lbl.place(relx=0.5, rely=0.9, anchor=CENTER)

        self.values = self.list_ports()
        self.optionmenu_var = customtkinter.StringVar(value="Select Port")
        optionmenu = customtkinter.CTkOptionMenu(self,values=self.values,
                                                command=self.optionmenu_callback,
                                                variable=self.optionmenu_var)
        optionmenu.place(relx=0.05, rely=0.95, anchor="w")

    def start_listening(self, event=None):
        hours_range = self.hours_range_entry.get()
        com_port = self.optionmenu_var.get()
        if hours_range.isdecimal():
            if 1 <= int(hours_range) <= 24:
                if com_port != "Select Port":
                # Implement logic to start listening to data in four phases
                    print(f"Listening Started, on {com_port}")
                    self.warn_lbl.configure(text_color="green" ,text="Listening Started, please wait!")
                    
                else:
                    self.warn_lbl.configure(text_color="red" ,text="*Please Select Port!")
            else:
                self.warn_lbl.configure(text_color="red" ,text="* Invalid Input: Please enter the hours in range 1-24.")
        else:
            self.warn_lbl.configure(text_color="red" ,text="*Invalid Input, Please enter a valid numeric value for hours.")

    def list_ports(self):
        ports_list = []
        for port in serialport.comports():
            ports_list.append(str(port))
        return ports_list
    

    def optionmenu_callback(self, choice):
        print("optionmenu dropdown clicked:", choice)

class PageOne(customtkinter.CTkFrame):
    def __init__(self, parent, controller):
        customtkinter.CTkFrame.__init__(self, parent)
        canvas = customtkinter.CTkCanvas(self)
        canvas.pack()
        controller.set_bg(canvas)

        button1 = customtkinter.CTkButton(canvas,text="Open Start Page", 
                            command= lambda: controller.show_frame(StartPage))
        button1.place(relx=0.5, rely=0.5, anchor=CENTER)

        
app = PowerAnalyzer()
app.mainloop()
