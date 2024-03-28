import json
import sqlite3
import matplotlib.pyplot as plt
import mplcursors
import datetime
import tkinter as tk
from tkinter import ttk
import customtkinter
from tkinter import messagebox

def view_data():
    # Connect to the SQLite database
    conn = sqlite3.connect('PowerAnalyzer.db')
    cursor = conn.cursor()

    # Execute the SELECT statement
    cursor.execute("SELECT * FROM Power_Analyzer")

    # Fetch all rows
    rows = cursor.fetchall()

    # Close the connection
    conn.close()

    # Function to display values in a popup
    def show_values(event):
        item = tree.selection()[0]
        values = tree.item(item, 'values')
        conn = sqlite3.connect('PowerAnalyzer.db')
        cursor = conn.cursor()
        cursor.execute(f"""
            SELECT * FROM Power_Analyzer WHERE id ={values[2]};""")
        # Fetch all rows
        rows = cursor.fetchall()

        # Close the connection
        conn.close()
        list = rows[0][2]
        start_time = datetime.datetime.fromisoformat(rows[0][7])
        ploting(list, "L1", rows[0][1], "red", start_time)
        #messagebox.showinfo("Row Values", rows[0][2])

    # Create a Tkinter window
    root = customtkinter.CTk()
    root.title("View Data")

    # Create a Treeview widget
    tree = ttk.Treeview(root)
    tree["columns"] = ("Place", "Hours", "ID")
    tree.heading("#0", text="ID")
    tree.heading("Place", text="Place")
    tree.heading("Hours", text="Hours")
    tree.heading("ID", text="ID")
    # Insert data into the Treeview
    for row in rows:
        tree.insert("", "end", text=row[0], values=(row[1], row[6], row[0]))

    tree.pack(expand=True, fill="both")

    # Bind double-click event to show values in popup
    tree.bind("<Double-1>", show_values)

    root.mainloop()
    plt.close()

def ploting( plot_list:list, plot_label:str, plot_text:str, plot_color:str, strat_time ):
    fig = plt.figure(num=f"Power Analyzer")
    fig.suptitle(plot_text, fontsize=16)                                      
    ax = fig.add_subplot()
    li = json.loads(plot_list)
    ax.plot(li, label=plot_label, color=plot_color)
    ax.set_ylim([0, 350])
    ax.set_ylabel("Voltage")
    ax.set_xlabel("Time")
    ax.legend([plot_label])
    mplcursors.cursor(multiple=True).connect("add", lambda sel: sel.annotation.set_text(f"{sel.artist.get_label()} : {sel.target[1]:.2f} \n{ (strat_time + (datetime.timedelta(seconds=sel.target[0]))).strftime('%I:%M:%S')}"))
    plt.show()

# Call the function to view data
view_data()
