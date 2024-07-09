# Power Analyzer
### Overview
Power Analyzer is a comprehensive tool designed for monitoring and analyzing power consumption over a specified period.
The application provides real-time data visualization and records voltage variations for different electrical phases (L1, L2, L3) and Neutral.
The data is saved in an SQLite database for future reference and analysis.

### Features
- Real-time data acquisition from a serial port.
- Visualization of voltage data over time.
- Storing and retrieving records from an SQLite database.
- Fullscreen mode for enhanced visualization.
- Multi-threaded data acquisition to ensure smooth operation.
- Supports Arabic text reshaping for UI elements.

### Requirements
- Python 3.7+
- Required Python libraries:
    - Threading
    - tkinter
    - customtkinter
    - PIL (Pillow)
    - serial
    - matplotlib
    - mplcursors
    - arabic_reshaper
    - bidi.algorithm
    - sqlite3

### Installation
1- Clone the repository:
  ```
  git clone https://github.com/PydevAzmi/Power-Analyzer.git
  cd Power-Analyzer
  ```
  
2- Install required libraries:
  ```
  pip install -r requirements.txt
  
  ```

3- Ensure you have an SQLite database file named PowerAnalyzer.db with the following table structure:
  ```
  python init_sql.py
  ```

4- Run the application:
  ```
  python tk-power-analyzer.py
  ```

### Acknowledgments
- Developed using various open-source libraries and tools.

### License
- This project is licensed under the MIT License.

