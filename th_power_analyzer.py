import json
import ctypes
import sqlite3

import queue
import threading

import tkinter as tk
import customtkinter 
from tkinter import messagebox, ttk
from tkinter import *
from PIL import Image, ImageTk

import serial
import serial.tools.list_ports as serialport

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import datetime
import time

import mplcursors
import arabic_reshaper
from bidi.algorithm import get_display



class PowerAnalyzer(tk.Tk):
   def __init__(self, *args, **kwargs):
      tk.Tk.__init__(self,*args, **kwargs)
      self.title("Power Analyzer V0")
      self.resizable(height=0, width=0)
      #self.attributes("-zoomed", True)
      self.attributes("-fullscreen", True)
      ico = ImageTk.PhotoImage(Image.open(r'media/power1- background.jpg'))
      self.iconphoto(True, ico)
      
      # get screen width and height
      self.screen_width = self.winfo_screenwidth()
      self.screen_height = self.winfo_screenheight()
      
      # calculate position x and y coordinates
      x = (self.screen_width - 1030)/2
      y = (self.screen_height - 720)/3
      #self.geometry('%dx%d+%d+%d' % (1030, 720, x, y))
      
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
      my_image = customtkinter.CTkImage(light_image=Image.open(r"media/power1- background.jpg"),size=(self.screen_width, self.screen_height))
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
         height=400,
         width=400,
         fg_color="white",
         bg_color="#0171B1", 
         corner_radius=30,
         )
      canvas1.place(relx=0.35, rely=0.25)

      label1 = customtkinter.CTkLabel(
         canvas1,
         text="Power Analyzer", 
         font=("Scripts",36) ,
         text_color="black",
         )
      label1.place(relx=0.5, rely=0.1, anchor=CENTER)

      label2_text = get_display( arabic_reshaper.reshape(": ادخل عدد ساعات الرصد"))
      label2 = customtkinter.CTkLabel(
         canvas1, 
         text=label2_text, 
         font=("Scripts",18) ,
         text_color="#555555",
         )
      label2.place(relx=0.5, rely=0.23, anchor=CENTER)
      self.sv = StringVar()
      self.hours_range_entry = customtkinter.CTkEntry(
         canvas1, 
         placeholder_text="e.g., 0.1-168",
         textvariable=self.sv, 
         validate="focusout",
         validatecommand=self.hours_callback,
         width=200, 
         text_color="black", 
         fg_color="#ffffff",
         )
      self.hours_range_entry.place(relx=0.5, rely=0.3, anchor=CENTER)

      label3_text = get_display( arabic_reshaper.reshape(": ادخل اسم المكان"))

      label3 = customtkinter.CTkLabel(
         canvas1, 
         text=label3_text ,
         font=("Scripts",18) ,
         text_color="#555555"
         )
      label3.place(relx=0.5, rely=0.43, anchor=CENTER)
      
      self.located_at = customtkinter.CTkEntry(
         canvas1, 
         placeholder_text="e.g., Warsha", 
         width=200, 
         text_color="black", 
         fg_color="#ffffff",
         )
      self.located_at.place(relx=0.5, rely=0.5, anchor=CENTER)
      start_text = get_display( arabic_reshaper.reshape("ابدأ الرصد"))

      button = customtkinter.CTkButton(
         canvas1,
         text=start_text,
         height=50, 
         width=200,
         font=("Scripts",18), 
         text_color="White", 
         fg_color=( "#0721F4","green"),
         command =lambda: self.start_listening(controller),
         )
      button.place(relx=0.5, rely=0.65, anchor=CENTER)
      records_text = get_display( arabic_reshaper.reshape("المحفوظات"))
      
      button = customtkinter.CTkButton(
         canvas1,
         text=records_text,
         height=50, 
         width=200,
         font=("Scripts",18), 
         text_color="White", 
         fg_color=( "#0721F4","green"),
         command =lambda: self.view_data(),
         )
      button.place(relx=0.5, rely=0.8, anchor=CENTER)

      self.warn_lbl = customtkinter.CTkLabel(
         canvas1, 
         font=("Scripts", 12), 
         text="" ,
         text_color="red",
         )
      self.warn_lbl.place(relx=0.5, rely=0.90, anchor=CENTER)

      self.values = self.list_ports()
      self.optionmenu_var = customtkinter.StringVar(value="Select Port!" )
      self.optionmenu = customtkinter.CTkOptionMenu(
         canvas1,
         bg_color= "transparent",
         values=self.values,
         #command=self.optionmenu_callback,
         variable=self.optionmenu_var,
         )
      self.optionmenu.place(relx=0.1, rely=0.96, anchor="w")
 
   def list_ports(self):
      ports_list = [str(port.device) for port in serialport.comports()]
      return ports_list
   
   def optionmenu_callback(self, choice):
      print("optionmenu dropdown clicked:", choice)
      
   def hours_callback(self):
      text =''
      try:
         hours = float(self.sv.get()) or 0
      except:
         self.warn_lbl.configure(
            text_color="red",
            text="* Invalid, Please Enter Correct Numeric Value"
            )
         return True 
      else:
         if not 0.1 <= (hours) <= 168:
            self.warn_lbl.configure(
               text_color="red" ,
               text="* Invalid, Please Enter The Hours In Range 0.1:168."
               )
         else:
            self.warn_lbl.configure(
            text_color="green",
            text=text)
         return True


   def start_listening(self, controller):
      hours_range = float(self.sv.get())
      com_port = self.optionmenu_var.get()
      located_at = self.located_at.get()
      if 0.1 <= hours_range <= 168:
         if com_port != "Select Port!":
            controller.show_frame(PageOne)
            instance =  controller.frames[PageOne]
            PageOne.open_connection(instance, com_port, hours_range, located_at, controller)
         else:
            values = self.list_ports()
            self.optionmenu.configure( values = values)
            self.warn_lbl.configure(
               text_color="red" ,
               text="* Please Select Port!"
               )

   def view_data(self):
      conn = sqlite3.connect('PowerAnalyzer.db')
      cursor = conn.cursor()
      cursor.execute("SELECT * FROM Power_Analyzer")
      rows = cursor.fetchall()
      conn.close()

      def  delete_value(evemt):       
         item = tree.selection()[0]
         values = tree.item(item, 'values')
         record_id = values[-1]
         conn = sqlite3.connect('PowerAnalyzer.db')
         cursor = conn.cursor()
         cursor.execute(f"DELETE FROM Power_Analyzer WHERE id = {record_id}")
         conn.commit()
         conn.close()
         tree.delete(item)

      def show_values(event):
         item = tree.selection()[0]
         values = tree.item(item, 'values')
         conn = sqlite3.connect('PowerAnalyzer.db')
         cursor = conn.cursor()
         cursor.execute(f"""
            SELECT * FROM Power_Analyzer WHERE id ={values[-1]};""")
         rows = cursor.fetchall()
         conn.close()
         L1 = rows[0][2]
         L2 = rows[0][3]
         L3 = rows[0][4]
         Neutral = rows[0][5]
         start_time = datetime.datetime.fromisoformat(rows[0][7])
         self.ploting(L1, "L1", rows[0][1], "red", start_time)
         self.ploting(L2, "L2", rows[0][1], "green", start_time)
         self.ploting(L3, "L3", rows[0][1], "yellow", start_time)
         self.ploting(Neutral, "Neutral", rows[0][1], "black", start_time)
         self.plotingall([L1, L2, L3, Neutral], rows[0][1], start_time)

      root = tk.Tk()
      root.title("View Data")
      tree = ttk.Treeview(root)
      tree["columns"] = ("Place", "Hours","Time", "ID")
      tree.heading("#0", text="ID")
      tree.heading("Place", text="Place")
      tree.heading("Hours", text="Hours")
      tree.heading("Time", text="Time")
      tree.heading("ID", text="ID")
      for row in rows:
         tree.insert(
            "",
            "end",
            text=row[0],
            values=(row[1], row[6], row[7], row[0]))
         
      tree.pack(expand=True, fill="both")
      tree.bind("<Double-1>", show_values)
      tree.bind("<Return>", show_values)
      tree.bind("<Delete>", delete_value)
      root.mainloop()
      plt.close()

   def ploting(self, plot_list:list, plot_label:str, plot_text:str, plot_color:str, start_time):
      fig = plt.figure(num=f"Power Analyzer")
      fig.suptitle(plot_text, fontsize=16)                                      
      ax = fig.add_subplot()
      ax.clear()
      li = json.loads(plot_list)
      ax.plot(li, label=plot_label, color=plot_color)
      ax.set_ylim([0, 350])
      ax.set_ylabel("Voltage")
      ax.set_xlabel("Time")
      maximum = max(li)
      label = []
      label.append(f"{plot_label} : max : {maximum}")
      ax.legend(label)
      ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: (start_time + datetime.timedelta(seconds=x*1.03)).strftime('%I:%M:%S %p')))
      for tick in ax.get_xticklabels():
         tick.set_rotation(30)
      mplcursors.cursor(multiple=True).connect("add", lambda sel: sel.annotation.set_text(f"{sel.artist.get_label()} : {sel.target[1]:.2f} \n{ (start_time + (datetime.timedelta(seconds=sel.target[0]))).strftime('%I:%M:%S %p')}"))
      plt.show()

   def plotingall(self, plot_list:list, plot_text:str, start_time ):
      fig = plt.figure(num=f"Power Analyzer")
      fig.suptitle(plot_text, fontsize=16)
      ax = fig.add_subplot()
      ax.clear()
      L1= json.loads(plot_list[0])
      ax.plot(L1, label="L1", color="Red")
      L2= json.loads(plot_list[1])
      ax.plot(L2, label="L2", color="Green")
      L3= json.loads(plot_list[2])
      ax.plot(L3, label="L3", color="Yellow")
      Neutral= json.loads(plot_list[3])
      ax.plot(Neutral, label="Neutral", color="Black")
      ax.set_ylim([0, 350])
      ax.set_ylabel("Voltage")
      ax.set_xlabel("Time")
      ax.legend([f"L1, Max: {max(L1)}", f"L2, Max: {max(L2)}", f"L3, Max: {max(L3)}", f"Neutral, Max: {max(Neutral)}"])
      ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: (start_time + datetime.timedelta(seconds=x*1.03)).strftime('%I:%M:%S %p')))
      for tick in ax.get_xticklabels():
         tick.set_rotation(30) 
      mplcursors.cursor(multiple=True).connect("add", lambda sel: sel.annotation.set_text(f"{sel.artist.get_label()} : {sel.target[1]:.2f} \n{ (start_time + (datetime.timedelta(seconds=sel.target[0]))).strftime('%I:%M:%S %p')}"))
      plt.show()
 
class PageOne(customtkinter.CTkFrame):
   def __init__(self, parent, controller):
      customtkinter.CTkFrame.__init__(self, parent)
      canvas = customtkinter.CTkCanvas(self)
      canvas.pack()
      controller.set_bg(canvas)
      self.screen_width = self.winfo_screenwidth()
      self.screen_height = self.winfo_screenheight()
      self.controller = controller
      #start from here ....
      self.data_queue = queue.Queue()
      self.serial_instance = serial.Serial()
      self.serial_instance.baudrate = 9600
      self.labels_values = {b'a': [], b'b': [], b'c': [], b'd': []}
      self.labels_factors = {b'a': 1.76391591, b'b': 1.759116375, b'c': 1.7502752549999998, b'd': 0.01090959}
      
      self.stop_event = threading.Event()
      
      self.hours = 1
      self.start_time = datetime.datetime.now()
      self.today = datetime.date.today()
      self.end_time = self.start_time + datetime.timedelta(seconds=3600)
      
      self.text = self.located_at = "Power Analyzer"
      
      canvas1 = customtkinter.CTkFrame(
         canvas,
         height=400,
         width=400,
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
      label1.place(relx=0.5, rely=0.1, anchor=CENTER)

      button1 = customtkinter.CTkButton(
         canvas1,
         text="Colse Connection",
         height=50, 
         width=200,
         font=("Scripts",18), 
         text_color="White", 
         fg_color=("#FF3838"),
         command= lambda: self.close_connection(),
         )
      button1.place(relx=0.5, rely=0.8, anchor=CENTER)

      self.label1 = customtkinter.CTkLabel(
         canvas1,
         text="", 
         font=("Scripts",14) ,
         text_color="black",
         )
      self.label1.place(relx=0.5, rely=0.9, anchor=CENTER)

   def open_connection(self, com_port, hours_range, located_at, controller):
      self.start_time = datetime.datetime.now()
      self.controller = controller
      self.serial_instance.port = com_port
      self.read_thread = threading.Thread(target = self.read_serial_data)
      self.hours = hours_range
      self.end_time = self.start_time + datetime.timedelta(seconds = hours_range * 3600)
      try :
         self.serial_instance.open()
         if self.serial_instance.isOpen():
            self.label1.configure(
               text_color="green", 
               text=f"Serial connection opened on port {self.serial_instance.port}")
               
            self.read_thread.start()
            

            self.located_at = located_at if located_at != "" else "قياس التغيرات الكهربيه"
            self.text = get_display(arabic_reshaper.reshape(self.located_at))
            self.fig = plt.figure(num=f"Power Analyzer", figsize = (self.screen_width/100, self.screen_height/100))
            self.fig.suptitle(self.text, fontsize=16)                   
            self.ax = self.fig.add_subplot()

            anim = animation.FuncAnimation(self.fig, func=self.animate, frames=40, interval=100, repeat=True)
            
            manager = plt.get_current_fig_manager()
            manager.full_screen_toggle()
            
            plt.subplots_adjust(bottom = 0.13)
            plt.show()
         else:
            self.label1.configure(
               text_color="red", 
               text=f"Failed to open serial connection on port {self.serial_instance.port}"
               )
               
      except Exception as e:
         print(f"Error during serial start: {e}")
         self.label1.configure(
            text_color="red", 
            text=f"Error during serial start: {e}"
            )
            
   def read_serial_data(self):
      current_label = b''
      while not self.stop_event.is_set():
         if datetime.datetime.now() >= self.end_time:
            self.close_connection()
            break
            
         data = self.serial_instance.read(1)
         if len(data) == 1:
             if data in self.labels_factors:
                 current_label = data
             elif current_label:
                 value = int(int.from_bytes(data, 'big') * self.labels_factors[current_label])
                 self.data_queue.put((current_label, value))
                 #print(current_label, value)
                 current_label = None
    
   def update_values(self):
      while not self.data_queue.empty():
         label, value = self.data_queue.get()
         self.labels_values[label].append(value)
            
   def update_plot(self):
      legend_labels = []
      legend_labels_order = {b"a": ["L1", "red"], b"b": ["L2", "green"], b"c": ["L3", "yellow"], b"d": ["Neutral", "black"]}
      for label, ch in legend_labels_order.items():
         data = self.labels_values.get(label)
         if data:
             self.ax.plot(data, label=ch[0], color=ch[1])
             legend_labels.append(f"{ch[0]}: {data[-1]}  max: {max(data)}")
         else:
             legend_labels.append(f"{ch[0]}: N/A")

      self.ax.legend(labels=legend_labels)
      self.ax.set_ylim([0, 350])
      self.ax.set_ylabel("Voltage")
      self.ax.set_xlabel("Time")
      
      self.ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: (self.start_time + datetime.timedelta(seconds=x*1.03)).strftime('%I:%M:%S %p')))
      for tick in self.ax.get_xticklabels():
         tick.set_rotation(25)
      mplcursors.cursor(hover=mplcursors.HoverMode.NoHover).connect(
         "add",
         lambda sel: sel.annotation.set_text(f"{sel.artist.get_label()} : {sel.target[1]:.2f} \n{(self.start_time + datetime.timedelta(seconds=int(sel.target[0]))).strftime('%I:%M:%S %p')}")
      )

   def animate(self, i):
      self.update_values()
      self.ax.clear()
      self.update_plot()

   def close_connection(self):
      self.stop_event.set()
      try:
        self.read_thread.join()
      except Exception as w:
         print(w)
      time.sleep(1)
      self.serial_instance.close()
      plt.close()
      self.stop_event.clear()
      
      # Save Records to Database
      connection_obj = sqlite3.connect('PowerAnalyzer.db')
      cursor_obj = connection_obj.cursor()
      l1_values_list_str = json.dumps(self.labels_values[b'a'])
      l2_values_list_str = json.dumps(self.labels_values[b'b'])
      l3_values_list_str = json.dumps(self.labels_values[b'c'])
      neutral_values_list_str = json.dumps(self.labels_values[b'd'])
      insert_query = 'INSERT INTO Power_Analyzer (location, l1_values, l2_values, l3_values, neutral_values, hours, start_time, day) VALUES (?, ?, ?, ?, ?, ?, ?, ?)'
      cursor_obj.execute(
         insert_query,
         (
            self.text,
            l1_values_list_str,
            l2_values_list_str,
            l3_values_list_str,
            neutral_values_list_str,
            self.hours,
            self.start_time,
            self.today
            ))
      connection_obj.commit()
      connection_obj.close()
      self.labels_values = {b'a': [], b'b': [], b'c': [], b'd': []}
      self.controller.show_frame(StartPage)

# Define Windows API constants
ES_CONTINUOUS = 0x80000000
ES_SYSTEM_REQUIRED = 0x00000001
# Prevent the system from entering sleep mode
ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS | ES_SYSTEM_REQUIRED)

app = PowerAnalyzer()

def window_exit():
   close = messagebox.askyesno("Exit?", "Are you sure you want to exit without saving?", icon=messagebox.WARNING, default=messagebox.NO)
   if close:
      plt.close()
      app.destroy()

app.protocol("WM_DELETE_WINDOW", window_exit)
app.mainloop()


