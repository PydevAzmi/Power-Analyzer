import ctypes
import json
import sqlite3

import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import *
import customtkinter as ctk

import serial
import serial.tools.list_ports as serialport

from PIL import Image, ImageTk
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import datetime
import mplcursors

import arabic_reshaper
from bidi.algorithm import get_display


# pyinstaller -n "Power Analyzer" -i media/images.png --onefile -w power_analyzer.py

class PowerAnalyzer(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.title("Power Analyzer")
        self.resizable(height=0, width=0)
        ico = ImageTk.PhotoImage(Image.open(r'media\\images.png'))
        self.iconphoto(True, ico)
        # get screen width and height
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        # calculate position x and y coordinates
        x = (screen_width - 1030) / 2
        y = (screen_height - 720) / 3
        self.geometry('%dx%d+%d+%d' % (1030, 720, x, y))

        container = ctk.CTkFrame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for Frame in (StartPage, PageOne):
            frame = Frame(container, self)
            self.frames[Frame] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(PageOne)

    def show_frame(self, container):
        frame = self.frames[container]
        frame.tkraise()

    def set_bg(self, canvas):
        my_image = ctk.CTkImage(
            light_image=Image.open(r"media\\power1- background.jpg"),
            size=(1030, 720)
        )

        image_label = ctk.CTkLabel(
            canvas,
            image=my_image,
            text="",
        )

        image_label.image = my_image
        image_label.pack()


class StartPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        ctk.CTkFrame.__init__(self, parent)
        canvas = ctk.CTkCanvas(self)
        canvas.pack()
        controller.set_bg(canvas)

        canvas1 = ctk.CTkFrame(
            canvas,
            height=400,
            width=400,
            fg_color="white",
            bg_color="#0171B1",
            corner_radius=30,
        )
        canvas1.place(relx=0.35, rely=0.25)

        label1 = ctk.CTkLabel(
            canvas1,
            text="Power Analyzer",
            font=("Scripts", 36),
            text_color="black",
        )
        label1.place(relx=0.5, rely=0.1, anchor=CENTER)

        label2 = ctk.CTkLabel(
            canvas1,
            text="Hours :",
            font=("Scripts", 18),
            text_color="#555555",
        )
        label2.place(relx=0.5, rely=0.23, anchor=CENTER)

        self.hours_range_entry = ctk.CTkEntry(
            canvas1,
            placeholder_text="e.g., 0.1-168",
            width=200,
            text_color="black",
            fg_color="#ffffff",
        )
        self.hours_range_entry.place(relx=0.5, rely=0.3, anchor=CENTER)

        label3 = ctk.CTkLabel(
            canvas1,
            text="Location Name:",
            font=("Scripts", 18),
            text_color="#555555"
        )
        label3.place(relx=0.5, rely=0.43, anchor=CENTER)

        self.located_at = ctk.CTkEntry(
            canvas1,
            placeholder_text="e.g., Warsha",
            width=200,
            text_color="black",
            fg_color="#ffffff",
        )
        self.located_at.place(relx=0.5, rely=0.5, anchor=CENTER)

        button = ctk.CTkButton(
            canvas1,
            text="Start Listening",
            height=50,
            width=200,
            font=("Scripts", 18),
            text_color="White",
            fg_color=("#0721F4", "green"),
            command=lambda: self.start_listening(controller),
        )
        button.place(relx=0.5, rely=0.65, anchor=CENTER)

        button = ctk.CTkButton(
            canvas1,
            text="Recordes",
            height=50,
            width=200,
            font=("Scripts", 18),
            text_color="White",
            fg_color=("#0721F4", "green"),
            command=lambda: self.view_data(),
        )
        button.place(relx=0.5, rely=0.8, anchor=CENTER)

        self.warn_lbl = ctk.CTkLabel(
            canvas1,
            font=("Scripts", 12),
            text="",
            text_color="red",
        )
        self.warn_lbl.place(relx=0.5, rely=0.90, anchor=CENTER)

        self.values = self.list_ports()
        self.optionmenu_var = ctk.StringVar(value="Select Port!")
        self.optionmenu = ctk.CTkOptionMenu(
            canvas,
            bg_color="blue",
            values=self.values,
            # command=self.optionmenu_callback,
            variable=self.optionmenu_var,
        )
        self.optionmenu.place(relx=0.1, rely=0.96, anchor="w")

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
        try:
            hours_range = float(hours_range)
        except Exception as e:
            self.warn_lbl.configure(
                text_color="red",
                text="* Invalid Input, Please Enter Correct Numeric Value"
            )
        else:
            if 0.1 <= hours_range <= 168:
                if com_port != "Select Port!":
                    controller.show_frame(PageOne)
                    instance = controller.frames[PageOne]
                    PageOne.open_connection(instance, com_port, hours_range, located_at)
                else:
                    values = self.list_ports()
                    self.optionmenu.configure(values=values)
                    self.warn_lbl.configure(
                        text_color="red",
                        text="* Please Select Port!"
                    )
            else:
                self.warn_lbl.configure(
                    text_color="red",
                    text="* Invalid, Please enter the hours in range 0.1-168."
                )

    def view_data(self):
        conn = sqlite3.connect('PowerAnalyzer.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Power_Analyzer")
        rows = cursor.fetchall()
        conn.close()

        def show_values(event):
            item = tree.selection()[0]
            values = tree.item(item, 'values')
            conn = sqlite3.connect('PowerAnalyzer.db')
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM Power_Analyzer WHERE id ={values[-1]};")
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
        tree["columns"] = ("Place", "Hours", "Time", "ID")
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
        root.mainloop()
        plt.close()

    def ploting(self, plot_list: list, plot_label: str, plot_text: str, plot_color: str, start_time):
        fig = plt.figure(num=f"Power Analyzer")
        plot_text = get_display(arabic_reshaper.reshape(plot_text))
        fig.suptitle(plot_text, fontsize=16)
        ax = fig.add_subplot()
        ax.clear()
        li = json.loads(plot_list)
        ax.plot(li, label=plot_label, color=plot_color)
        ax.set_ylim([0, 350])
        ax.set_ylabel("Voltage")
        ax.set_xlabel("Number of Values")
        maximum = max(li)
        label = []
        label.append(f"{plot_label} : max : {maximum}")
        ax.legend(label)
        mplcursors.cursor(multiple=True).connect("add", lambda sel: sel.annotation.set_text(
            f"{sel.artist.get_label()} : {sel.target[1]:.2f} \n{(start_time + (datetime.timedelta(seconds=sel.target[0]))).strftime('%I:%M:%S')}"))
        plt.show()

    def plotingall(self, plot_list: list, plot_text: str, start_time):
        fig = plt.figure(num=f"Power Analyzer")
        plot_text = get_display(arabic_reshaper.reshape(plot_text))
        fig.suptitle(plot_text, fontsize=16)
        ax = fig.add_subplot()
        ax.clear()
        L1 = json.loads(plot_list[0])
        ax.plot(L1, label="L1", color="Red")
        L2 = json.loads(plot_list[1])
        ax.plot(L2, label="L2", color="Green")
        L3 = json.loads(plot_list[2])
        ax.plot(L3, label="L3", color="Yellow")
        Neutral = json.loads(plot_list[3])
        ax.plot(Neutral, label="Neutral", color="Black")
        ax.set_ylim([0, 350])
        ax.set_ylabel("Voltage")
        ax.set_xlabel("Time")
        ax.legend([
            f"L1, Max: {max(L1)}",
            f"L2, Max: {max(L2)}",
            f"L3, Max: {max(L3)}", 
            f"Neutral, Max: {max(Neutral)}"])
        mplcursors.cursor(multiple=True).connect("add", lambda sel: sel.annotation.set_text(
            f"{sel.artist.get_label()} : {sel.target[1]:.2f} \n{(start_time + (datetime.timedelta(seconds=sel.target[0]))).strftime('%I:%M:%S')}"))
        plt.show()


class PageOne(ctk.CTkFrame):
    def __init__(self, parent, controller):
        ctk.CTkFrame.__init__(self, parent)
        canvas = ctk.CTkCanvas(self)
        canvas.pack()
        controller.set_bg(canvas)
        self.START_TIME = datetime.datetime.now()
        self.today = datetime.date.today()
        self.text = "Power Analyzer"
        self.located_at = "Power Analyzer"
        self.hours = 0

        self.serialIns = serial.Serial()
        self.l1_max, self.a = 0, []
        self.l2_max, self.b = 0, []
        self.l3_max, self.c = 0, []
        self.nu_max, self.d = 0, []

        self.fig_name = "Power_Analyzer"
        canvas1 = ctk.CTkFrame(
            canvas,
            height=400,
            width=400,
            fg_color="white",
            bg_color="#0171B1",
            corner_radius=30,
        )
        canvas1.place(relx=0.3, rely=0.25)
        
        label1 = ctk.CTkLabel(
            canvas1,
            text="Power Analyzer",
            font=("Scripts", 36),
            text_color="black",
        )
        label1.place(relx=0.5, rely=0.1, anchor=CENTER)

        button1 = ctk.CTkButton(
            canvas1,
            text="Colse Connection",
            height=50,
            width=200,
            font=("Scripts", 18),
            text_color="White",
            fg_color=("#FF3838"),
            command=lambda: self.close_connection(controller),
        )
        button1.place(relx=0.5, rely=0.8, anchor=CENTER)

        self.label1 = ctk.CTkLabel(
            canvas1,
            text="",
            font=("Scripts", 14),
            text_color="black",
        )
        self.label1.place(relx=0.5, rely=0.9, anchor=CENTER)

    def open_connection(self, com_port, hours_range, located_at):
        self.serialIns.port = str(com_port[:4])
        try:
            self.serialIns.open()
            if self.serialIns.isOpen():
                self.label1.configure(
                    text_color="green",
                    text=f"Serial connection opened on port {self.serialIns.port}"
                )
                self.serialIns.write(int(hours_range) + 1)
                self.data_list = self.sliding_window(10, (hours_range))
                self.fig_name = located_at
                self.located_at = located_at if located_at != "" else "قياس التغيرات الكهربيه"
                self.text = get_display(arabic_reshaper.reshape(self.located_at))
                self.fig = plt.figure(num=f"Power Analyzer")
                self.fig.suptitle(self.text, fontsize=16)
                self.ax = self.fig.add_subplot()
                self.ani = animation.FuncAnimation(
                    self.fig,
                    self.animate,
                    frames=40,
                    fargs=(self.data_list,),
                    interval=150)
                plt.show()
            else:
                self.label1.configure(
                    text_color="red",
                    text=f"Failed to open serial connection on port {self.serialIns.port}"
                )
        except Exception as e:
            print(f"Error during serial start: {e}")
            self.label1.configure(
                text_color="red",
                text=f"Error during serial start"
            )

    def sliding_window(self, window_size, hours=1):
        self.a, self.b, self.c, self.d = [0] * window_size, [0] * window_size, [0] * window_size, [0] * window_size
        self.hours = hours
        for _ in range(int(self.hours) * 3600):
            for _ in range(4):
                data = self.serialIns.read()
                if b"a" in data:
                    data = self.serialIns.read()
                    data = int(int.from_bytes(data, "big") * 5 * 0.00489 * 72.1438)
                    self.a.append(int(data))
                    self.l1_max = data if data > self.l1_max else self.l1_max
                    yield (self.a, "L1", "red", data, self.l1_max)
                    continue

                elif b"b" in data:
                    data = self.serialIns.read()
                    data = int(int.from_bytes(data, "big") * 5 * 0.00489 * 71.9475)
                    self.b.append(int(data))
                    self.l2_max = data if data > self.l2_max else self.l2_max
                    yield (self.b, "L2", "green", data, self.l2_max)
                    continue

                elif b"c" in data:
                    data = self.serialIns.read()
                    data = int(int.from_bytes(data, "big") * 5 * 0.00489 * 71.5859)
                    self.c.append(int(data))
                    self.l3_max = data if data > self.l3_max else self.l3_max
                    yield (self.c, "L3", "yellow", data, self.l3_max)
                    continue

                elif b"d" in data:
                    data = self.serialIns.read()
                    data = int(int.from_bytes(data, "big") * 5 * 0.00489 * 0.4462)
                    self.d.append(int(data))
                    self.nu_max = data if data > self.nu_max else self.nu_max
                    yield (self.d, "Neutral", "black", data, self.nu_max)
                    continue

    def animate(self, i, data_list: list):
        self.ax.clear()
        legend_labels = []
        # to view legend in order :
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

        self.ax.xaxis.set_major_formatter(
            plt.FuncFormatter(lambda x, _: (self.START_TIME + datetime.timedelta(seconds=x)).strftime('%I:%M:%S %p')))
        for tick in self.ax.get_xticklabels():
            tick.set_rotation(30)

        self.ax.legend(labels=legend_labels)
        mplcursors.cursor(hover=mplcursors.HoverMode.NoHover).connect("add", lambda sel: sel.annotation.set_text(
            f"{sel.artist.get_label()} : {sel.target[1]:.2f} \n{(self.START_TIME + (datetime.timedelta(seconds=sel.target[0]))).strftime('%I:%M:%S')}"))

    def close_connection(self, controller):
        # self.fig.savefig(f"records/{self.fig_name}-{self.today}.png")
        plt.close()
        self.serialIns.close()
        connection_obj = sqlite3.connect('PowerAnalyzer.db')
        cursor_obj = connection_obj.cursor()
        l1_values_list_str = json.dumps(self.a)
        l2_values_list_str = json.dumps(self.b)
        l3_values_list_str = json.dumps(self.c)
        neutral_values_list_str = json.dumps(self.d)
        insert_query = 'INSERT INTO Power_Analyzer (location, l1_values, l2_values, l3_values, neutral_values, hours, start_time, day) VALUES (?, ?, ?, ?, ?, ?, ?, ?)'
        cursor_obj.execute(
            insert_query,
            (
                self.located_at,
                l1_values_list_str,
                l2_values_list_str,
                l3_values_list_str,
                neutral_values_list_str,
                self.hours,
                self.START_TIME,
                self.today
            ))
        connection_obj.commit()
        connection_obj.close()

        controller.show_frame(StartPage)
        self.l1_max = 0
        self.l2_max = 0
        self.l3_max = 0
        self.nu_max = 0


# Define Windows API constants
ES_CONTINUOUS = 0x80000000
ES_SYSTEM_REQUIRED = 0x00000001
# Prevent the system from entering sleep mode
ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS | ES_SYSTEM_REQUIRED)

app = PowerAnalyzer()
def window_exit():
    close = messagebox.askyesno("Exit?", "Are you sure you want to exit without saving?")
    if close:
        app.destroy()

app.protocol("WM_DELETE_WINDOW", window_exit)
app.mainloop()
