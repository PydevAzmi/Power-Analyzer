import serial ,sys
import serial.tools.list_ports as List_ports
import random
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from time import sleep
import mplcursors

ports = List_ports.comports()
serialIns= serial.Serial()
l1 = []
for port in ports:
    l1.append(str(port))
print(serialIns)
print(l1[0])
serialIns.port = "com5"

serialIns.open()
print(serialIns)
serialIns.write(2)

a,b,c,d = [],[],[],[]

def sliding_window(window_size, hours=1):
    a, b, c, d = [0]*window_size, [0]*window_size, [0]*window_size, [0]*window_size
    for i in range(hours * 3600):
        for _ in range(4):
            data = serialIns.read(2)
            if b"a" in data:
                data = int(int.from_bytes(data[1:], "big")* 5 * 0.00489 * 72.1438)
                a.append(int(data))
                yield [a[i:i+window_size],"L1"]
            elif b"b" in data:
                data = int(int.from_bytes(data[1:], "big")* 5 * 0.00489 * 71.9475)
                b.append(int(data))
                yield [b[i:i+window_size],"L2"]
            elif b"c" in data:
                data = int(int.from_bytes(data[1:], "big")* 5 * 0.00489 * 71.5859)
                c.append(int(data))
                yield [c[i:i+window_size],"L3"]
            elif b"d" in data:
                data = int(int.from_bytes(data[1:], "big")* 5 * 0.00489 * 0.4462)
                d.append(int(data))
                yield [d[i:i+window_size],"Neutral"]
            print(data)

print(f" a: {len(a)},\n b: {len(b)}, \n c: {len(c)}, \n d: {len(d)}")

def animate(i, data_list:list):
    ax.clear()
    for _ in range(4):
        data = next(data_list)
        ax.plot(data[0],label=data[1])
    sleep(0.1)
    ax.set_ylim([0,350])
    ax.set_title("Voltage Changes")
    ax.set_ylabel("Voltage")
    ax.legend()
    mplcursors.cursor(hover= mplcursors.HoverMode.Transient).connect("add", lambda sel: sel.annotation.set_text(f"{sel.artist.get_label()}: {sel.target[1]:.2f}"))


data_list = sliding_window(1000,1)
fig = plt.figure()
ax = fig.add_subplot()
ani = animation.FuncAnimation(fig, animate, frames=40, fargs=(data_list,), interval=100)
plt.show()



