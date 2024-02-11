import serial ,sys
import serial.tools.list_ports as List_ports
ports = List_ports.comports()
serialIns= serial.Serial()
l1 = []
for port in ports:
    l1.append(str(port))
print(serialIns)
print(l1[0])
serialIns.port = input("Enter serial port: ")

serialIns.open()
print(serialIns)
serialIns.write(int (input("How much houres do you want ? ")))

while True:
    data = serialIns.read()
    print(data)
    data += serialIns.readline(serialIns.in_waiting)
    sys.stdout.flush()







