import tkinter as tk
from tkinter import *
import customtkinter 
from PIL import Image, ImageTk
import serial
import serial.tools.list_ports as serialport
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import datetime 
import mplcursors
import arabic_reshaper
from bidi.algorithm import get_display


class PowerAnalyzer(tk.Tk):
   def __init__(self, *args, **kwargs):
      tk.Tk.__init__(self,*args, **kwargs)
      self.title("Power Analyzer")
      self.resizable(height=0, width=0)
      ico = ImageTk.PhotoImage(Image.open(r'media\\images.png'))
      self.iconphoto(True, ico)

      # get screen width and height
      screen_width = self.winfo_screenwidth()
      screen_height = self.winfo_screenheight()

      # calculate position x and y coordinates
      x = (screen_width - 1030)/2
      y = (screen_height - 720)/3
      self.geometry('%dx%d+%d+%d' % (1030, 720, x, y))

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
      image_label = customtkinter.CTkLabel(
         canvas,
         image=my_image, 
         text="",
         )
      image_label.image = my_image
      image_label.pack()    


class StartPage(customtkinter.CTkFrame):
   def __init__(self, parent, controller):
      customtkinter.CTkFrame.__init__(self, parent)
      canvas = customtkinter.CTkCanvas(self)
      canvas.pack()
      controller.set_bg(canvas)

      canvas1 = customtkinter.CTkFrame(
         canvas,
         height=350,
         width=350,
         fg_color="white",
         bg_color="#0171B1", 
         corner_radius=30,
         )
      canvas1.place(relx=0.3, rely=0.25)

      label1 = customtkinter.CTkLabel(
         canvas1,
         text="Power Analyzer", 
         font=("Scripts",36) ,
         text_color="black",
         )
      label1.place(relx=0.48, rely=0.15, anchor=CENTER)

      label2 = customtkinter.CTkLabel(
         canvas1, 
         text=": ادخل عدد ساعات الرصد", 
         font=("Scripts",18) ,
         text_color="#555555",
         )
      label2.place(relx=0.5, rely=0.3, anchor=CENTER)

      self.hours_range_entry = customtkinter.CTkEntry(
         canvas1, 
         placeholder_text="e.g., 1-24", 
         width=200, 
         text_color="black", 
         fg_color="#ffffff",
         )
      self.hours_range_entry.place(relx=0.5, rely=0.4, anchor=CENTER)

      label3 = customtkinter.CTkLabel(
         canvas1, 
         text= ": ادخل اسم المكان",
         font=("Scripts",18) ,
         text_color="#555555"
         )
      label3.place(relx=0.5, rely=0.5, anchor=CENTER)
      
      self.located_at = customtkinter.CTkEntry(
         canvas1, 
         placeholder_text="e.g., Warsha", 
         width=200, 
         text_color="black", 
         fg_color="#ffffff",
         )
      self.located_at.place(relx=0.5, rely=0.6, anchor=CENTER)

      button = customtkinter.CTkButton(
         canvas1,
         text="ابدأ الرصد",
         height=50, 
         width=200,
         font=("Scripts",18), 
         text_color="White", 
         fg_color=( "#0721F4","green"),
         command =lambda: self.start_listening(controller),
         )
      button.place(relx=0.5, rely=0.8, anchor=CENTER)
      
      self.warn_lbl = customtkinter.CTkLabel(
         canvas1, 
         font=("Scripts", 12), 
         text="" ,
         text_color="red",
         )
      self.warn_lbl.place(relx=0.5, rely=0.95, anchor=CENTER)

      self.values = self.list_ports()
      self.optionmenu_var = customtkinter.StringVar(value="Select Port!" )
      self.optionmenu = customtkinter.CTkOptionMenu(
         self,
         bg_color= "transparent",
         values=self.values,
         command=self.optionmenu_callback,
         variable=self.optionmenu_var,
         )
      self.optionmenu.place(relx=0.05, rely=0.95, anchor="w")
 
   def list_ports(self):
      ports_list = []
      for port in serialport.comports():
         ports_list.append(str(port))
      return ports_list


   def optionmenu_callback(self, choice):
      print("optionmenu dropdown clicked:", choice)


   def start_listening(self, controller):
      hours_range = self.hours_range_entry.get()
      com_port = self.optionmenu_var.get()
      located_at = self.located_at.get()
      if hours_range.isdecimal():
         if 1 <= int(hours_range) <= 24:
            if com_port != "Select Port!":
               controller.show_frame(PageOne)
               instance =  controller.frames[PageOne]
               PageOne.open_connection(instance, com_port, hours_range, located_at)
            else:
               values = self.list_ports()
               self.optionmenu.configure( values = values)
               self.warn_lbl.configure(
                  text_color="red" ,
                  text="* Please Select Port!"
                  )
         else:
            self.warn_lbl.configure(
               text_color="red",
               text="* Invalid, Please enter the hours in range 1-24."
               )
      else:
         self.warn_lbl.configure(
            text_color="red" ,
            text="* Invalid, Please enter a valid numeric value for hours."
            )


class PageOne(customtkinter.CTkFrame):
   def __init__(self, parent, controller):
      customtkinter.CTkFrame.__init__(self, parent)
      canvas = customtkinter.CTkCanvas(self)
      canvas.pack()
      controller.set_bg(canvas)
      self.serialIns= serial.Serial()
      self.START_TIME = datetime.datetime.now()
      self.l1_max, self.a = 0, []
      self.l2_max, self.b = 0, []
      self.l3_max, self.c = 0, []
      self.nu_max, self.d = 0, []
      self.fig_name = "Power_Analyzer"
      button1 = customtkinter.CTkButton(
         canvas,
         text="Colse Connection",
         height=50, 
         width=200,
         font=("Scripts",18), 
         text_color="White", 
         fg_color=("#FF3838"),
         command= lambda: self.close_connection(controller),
         )
      button1.place(relx=0.5, rely=0.5, anchor=CENTER)

      self.label1 = customtkinter.CTkLabel(
         canvas,
         text="", 
         font=("Scripts",18) ,
         text_color="black",
         )
      self.label1.place(relx=0.5, rely=0.15, anchor=CENTER)


   def open_connection(self, com_port, hours_range, located_at):
      self.serialIns.port = str(com_port[:4])
      try :
         self.serialIns.open()
         if self.serialIns.isOpen():
            self.label1.configure(
               text_color="green", 
               text=f"Serial connection opened on port {self.serialIns.port}"
               )
            self.serialIns.write(int(hours_range))
            self.data_list = self.sliding_window(1, int(hours_range))
            self.fig_name = located_at
            located_at = located_at if located_at != "" else "قياس التغيرات الكهربيه"
            text = get_display( arabic_reshaper.reshape(located_at))
            self.fig = plt.figure(num=f"Power Analyzer")
            self.fig.suptitle(text, fontsize=16)                                      
            self.ax = self.fig.add_subplot()                              
            self.ani = animation.FuncAnimation(
               self.fig, 
               self.animate, 
               frames=40, 
               fargs=(self.data_list,), 
               interval=150) 
            plt.show() 
         else:
            print("Failed to open serial connection.")
            self.label1.configure(
               text_color="red", 
               text=f"Failed to open serial connection on port {self.serialIns.port}"
               )
            
      except Exception as e:
         print(f"Error during serial start: {e}")
         self.label1.configure(
            text_color="red", 
            text=f"Error during serial start: {e}"
            )
         

   def sliding_window(self, window_size, hours=1):
      self.a, self.b, self.c, self.d = [0]*window_size, [0]*window_size, [0]*window_size, [0]*window_size
      for i in range(hours * 3600):
         for _ in range(4): 
            data = self.serialIns.read(2)
            if b"a" in data:
               data = int(int.from_bytes(data[1:], "big")* 5 * 0.00489 * 72.1438)
               self.a.append(int(data))
               self.l1_max = data if data > self.l1_max else self.l1_max
               yield (self.a, "L1", "red", data, self.l1_max)
            elif b"b" in data:
               data = int(int.from_bytes(data[1:], "big")* 5 * 0.00489 * 71.9475)
               self.b.append(int(data))
               self.l2_max = data if data > self.l2_max else self.l2_max
               yield (self.b, "L2", "green", data, self.l2_max)
            elif b"c" in data:
               data = int(int.from_bytes(data[1:], "big")* 5 * 0.00489 * 71.5859)
               self.c.append(int(data))
               self.l3_max = data if data > self.l3_max else self.l3_max
               yield (self.c, "L3", "yellow", data, self.l3_max)
            elif b"d" in data:
               data = int(int.from_bytes(data[1:], "big")* 5 * 0.00489 * 0.4462)
               self.d.append(int(data))
               self.nu_max = data if data > self.nu_max else self.nu_max
               yield (self.d, "Neutral", "black", data, self.nu_max)


   def animate(self,i, data_list:list):
      self.ax.clear()
      legend_labels = []
      legend_labels_order = ["L1", "L2", "L3", "Neutral"] 
      for label in legend_labels_order:
         for _ in range(4):
            data = next(data_list)
            if data[1] == label:
               self.ax.plot(data[0], label=data[1], color=data[2])
               self.ax.legend(labels=legend_labels)
               legend_labels.append(f"{data[1]}: {data[3]}  Max :{data[4]}")
               break

      self.ax.set_ylim([0, 350])
      self.ax.set_ylabel("Voltage")
      self.ax.set_xlabel("Time")

      self.ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: (self.START_TIME + datetime.timedelta(seconds=x)).strftime('%I:%M %p')))
      for tick in self.ax.get_xticklabels():
         tick.set_rotation(30)

      self.ax.legend(labels=legend_labels)
      mplcursors.cursor(hover= mplcursors.HoverMode.NoHover).connect("add", lambda sel: sel.annotation.set_text(f"{sel.artist.get_label()} : {sel.target[1]:.2f}"))
   
   def close_connection(self, controller):
      today  = datetime.date.today()
      self.fig.savefig(f"records/{self.fig_name}-{today}.png")
      plt.close()
      self.serialIns.close()
      controller.show_frame(StartPage)
      self.l1_max = 0
      self.l2_max = 0
      self.l3_max = 0
      self.nu_max = 0

app = PowerAnalyzer()
app.mainloop()