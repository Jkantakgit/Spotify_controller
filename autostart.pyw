import os
import threading
import time


def start():
    os.system('cmd /k "C:/Users/PetrH/Desktop/Python/Python_bot/python_bot.py"')


second_t = threading.Thread(target=start, daemon=True)
second_t.start()

os.system('cmd /k "c:/Users/PetrH/Desktop/Python/Apps/main.pyw"')
