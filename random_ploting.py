import random 
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from time import sleep

def sliding_window(window_size):
    data_list =[220]*window_size
    if len(data_list) < window_size:
       return data_list
    for i in range(500 - window_size + 1):
        rand = random.randint(210,230)
        data_list.append(rand)
        yield data_list[i:i+window_size]


def animate(i, data_list:list):
    ax.clear()
    ax.plot(next(data_list))
    ax.plot(next(data_list))
    sleep(0.1)
    ax.set_ylim([140, 260])                                
    ax.set_title("Voltage Changes")                        
    ax.set_ylabel("Voltage")  

data_list = sliding_window(50)
fig = plt.figure()                                      
ax = fig.add_subplot()                                  

ani = animation.FuncAnimation(fig, animate, frames=40, fargs=(data_list,), interval=100) 
plt.show()