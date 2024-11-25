import sqlite3

# connection object
connection_obj = sqlite3.connect('PowerAnalyzer.db')

# cursor object
cursor_obj = connection_obj.cursor()

# Drop the Power_Analyzer table if already exists.
cursor_obj.execute("DROP TABLE IF EXISTS Power_Analyzer")

# Creating table
table = """
CREATE TABLE Power_Analyzer (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    location VARCHAR(255),
    l1_values TEXT,
    l2_values TEXT,
    l3_values TEXT,
    neutral_values TEXT,
    hours FLOAT,
    start_time TEXT,
    day TEXT
);
"""

insert= """
INSERT INTO Power_Analyzer (location, l1_values, hours) VALUES ('New York', '1.23,4.56,7.89', 5.5);
"""
delete = """
DELETE FROM Power_Analyzer WHERE ID=25 ;
"""
cursor_obj.execute(table)

cursor_obj.execute("""
SELECT * FROM Power_Analyzer;
""")

rows = cursor_obj.fetchall()
for row in rows:
    print(row)
    
connection_obj.commit()
# Close the connection
connection_obj.close()
