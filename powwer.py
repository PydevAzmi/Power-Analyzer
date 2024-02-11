import tkinter as tk
import customtkinter
from tkinter import * 
from PIL import Image, ImageTk
import serial
import serial.tools.list_ports as serialport
import random 
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from time import sleep


class PowerAnalyzer(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self,*args, **kwargs)

        self.title("Power Analyzer")
        self.resizable(height=0, width=0)
        ico = ImageTk.PhotoImage(Image.open(r'media\\images.png'))
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

        self.show_frame(StartPage)

    def show_frame(self, container):
        frame = self.frames[container]
        frame.tkraise()

    def set_bg(self, canvas):
        my_image = customtkinter.CTkImage(light_image=Image.open(r"media\\background.jpeg"),size=(1030, 720))
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
                                        command =lambda: self.start_listening(controller))
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
                    print(f"Listening Started, on {com_port}")
                    self.warn_lbl.configure(text_color="green" ,text="Listening Started, please wait!")
                    # Logic to navigate to PageOne
                    event.show_frame(PageOne)
                else:
                    self.warn_lbl.configure(text_color="red" ,text="* Please Select Port!")
            else:
                self.warn_lbl.configure(text_color="red" ,text="* Invalid Input: Please enter the hours in range 1-24.")
        else:
            self.warn_lbl.configure(text_color="red" ,text="* Invalid Input, Please enter a valid numeric value for hours.")

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

        # Create a FigureCanvasTkAgg widget to embed the matplotlib plot
        self.canvas = FigureCanvasTkAgg(plt.Figure(figsize=(5, 4), tight_layout=True), master=canvas)
        self.canvas.get_tk_widget().pack()

        # Customize your plot here
        self.ax = self.canvas.figure.add_subplot(111)
        self.ax.set_ylim([140, 260])
        self.ax.set_title("Voltage Changes")
        self.ax.set_ylabel("Voltage")
        self.data_list = self.sliding_window(50)
        # Animate the plot
        ani = animation.FuncAnimation(self.canvas.figure, self.animate, frames=40, fargs=(self.data_list,), interval=100)

        button1 = customtkinter.CTkButton(canvas, text="Open Start Page",
                                          command=lambda: controller.show_frame(StartPage))
        button1.place(relx=0.5, rely=0.9, anchor=CENTER)

    def sliding_window(self, window_size):
        data_list =[220]*window_size
        if len(data_list) < window_size:
            return data_list
        for i in range(500 - window_size + 1):
            rand = random.randint(210,230)
            data_list.append(rand)
            yield data_list[i:i+window_size]
    def animate(self, i, data_list):
        self.ax.clear()
        # Customize your plot update logic here
        self.ax.plot(next(data_list))
        self.ax.plot(next(data_list))
        self.ax.plot(next(data_list))
        self.ax.plot(next(data_list))
        self.ax.set_ylim([140, 260])
        self.ax.set_title("Voltage Changes")
        self.ax.set_ylabel("Voltage")


app = PowerAnalyzer()
app.mainloop()
