import tkinter as tk
import customtkinter
from tkinter import * 
from PIL import Image, ImageTk
import serial
import mplcursors
import serial.tools.list_ports as serialport
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from time import sleep


class PowerAnalyzer(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self,*args, **kwargs)
        #customtkinter.CTk.__init__(self,*args, **kwargs)
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
        image_label = customtkinter.CTkLabel(canvas,
                                             image=my_image, 
                                             text="")
        image_label.image = my_image
        image_label.pack()        
    
class StartPage(customtkinter.CTkFrame):
    def __init__(self, parent, controller):
        customtkinter.CTkFrame.__init__(self, parent)
        canvas = customtkinter.CTkCanvas(self)
        canvas.pack()
        controller.set_bg(canvas)
        self.serialIns= serial.Serial()
        self.a, self.b, self.c, self.d = [],[],[],[]

        canvas1 = customtkinter.CTkFrame(canvas,
                                        height=350,
                                        width=350,
                                        fg_color="white",
                                        bg_color="#0171B1", 
                                        corner_radius=30)
        canvas1.place(relx=0.3, rely=0.25)
        label1 = customtkinter.CTkLabel(canvas1,
                                        text="Power Analyzer", 
                                        font=("Arial",36) ,
                                        text_color="black")
        label1.place(relx=0.48, rely=0.15, anchor=CENTER)
        label2 = customtkinter.CTkLabel(canvas1, 
                                        text="Enter Hours Range:", 
                                        font=("Arial",18) ,
                                        text_color="#555555")
        label2.place(relx=0.5, rely=0.4, anchor=CENTER)
        self.hours_range_entry = customtkinter.CTkEntry(canvas1, 
                                                        placeholder_text="e.g., 1-24", 
                                                        width=200, 
                                                        text_color="black", 
                                                        fg_color="#ffffff")
        self.hours_range_entry.place(relx=0.5, rely=0.5, anchor=CENTER)
        self.hours_range_entry.bind('<Return>',command =lambda event: self.start_listening(controller))
        button = customtkinter.CTkButton(canvas1,
                                        text="Start Listening",
                                        height=50, 
                                        width=200,
                                        font=("Arial",18), 
                                        text_color="White", 
                                        fg_color=( "#0721F4","green"),
                                        command =lambda: self.start_listening(controller))
        button.place(relx=0.5, rely=0.75, anchor=CENTER)
        
        self.warn_lbl = customtkinter.CTkLabel(canvas1, 
                                               font=("Arial",10), 
                                               text="" ,
                                               text_color="red")
        self.warn_lbl.place(relx=0.5, rely=0.9, anchor=CENTER)

        self.values = self.list_ports()
        self.optionmenu_var = customtkinter.StringVar(value="Select Port")
        optionmenu = customtkinter.CTkOptionMenu(self,
                                                values=self.values,
                                                command=self.optionmenu_callback,
                                                variable=self.optionmenu_var)
        optionmenu.place(relx=0.05, rely=0.95, anchor="w")

    def start_listening(self, controller):
        hours_range = self.hours_range_entry.get()
        com_port = self.optionmenu_var.get()
        if hours_range.isdecimal():
            if 1 <= int(hours_range) <= 24:
                if com_port != "Select Port":
                    print(f"Listening Started, on {com_port}")
                    self.warn_lbl.configure(text_color="green" ,text="Listening Started, please wait!")
                    # Navigate to PageOne
                    controller.show_frame(PageOne)
                    # Implement logic to start listening to data in four phases
                    
                    print(str(com_port[:4]))
                    self.serialIns.port = str(com_port[:4])
                    self.serialIns.open()
                    self.serialIns.write(int(hours_range))
                    print(self.serialIns)
                    data_list = self.sliding_window(900, int(hours_range))
                    self.fig = plt.figure()                                      
                    self.ax = self.fig.add_subplot()                                  
                    self.ani = animation.FuncAnimation(self.fig, self.animate, frames=40, fargs=(data_list,), interval=100) 
                    plt.show()                 
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


    def sliding_window(self, window_size, hours=1):
        self.a, self.b, self.c, self.d = [100]*window_size, [10]*window_size, [20]*window_size, [220]*window_size
        for i in range(hours * 3600):
            for _ in range(4):
                data = self.serialIns.read(2)
                print(data)
                if b"a" in data:
                    data = int(int.from_bytes(data[1:], "big")* 5 * 0.00489 * 72.1438)
                    self.a.append(int(data))
                    yield [self.a,"L1"]
                elif b"b" in data:
                    data = int(int.from_bytes(data[1:], "big")* 5 * 0.00489 * 71.9475)
                    self.b.append(int(data))
                    yield [self.b,"L2"]
                elif b"c" in data:
                    data = int(int.from_bytes(data[1:], "big")* 5 * 0.00489 * 71.5859)
                    self.c.append(int(data))
                    yield [self.c,"L3"]
                elif b"d" in data:
                    data = int(int.from_bytes(data[1:], "big")* 5 * 0.00489 * 0.4462)
                    self.d.append(int(data))
                    yield [self.d,"Neutral"]
                

    def animate(self,i, data_list:list):
        self.ax.clear()
        for _ in range(4):
            data = next(data_list)
            self.ax.plot(data[0],label=data[1])
        self.ax.set_ylim([140, 260])
        self.ax.set_title("Voltage Changes")                        
        self.ax.set_ylabel("Voltage") 
        self.ax.legend()
        mplcursors.cursor(hover= mplcursors.HoverMode.Transient).connect("add", lambda sel: sel.annotation.set_text(f"{sel.artist.get_label()}: {sel.target[1]:.2f}"))
        
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

