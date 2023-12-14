from threading import Thread
import random
import requests

URL = "http://localhost:5500/api/login"

DATA = [{'username' : 'Amruth', 'password' : 'idk'}, {'username' : 'DDD', 'password' : 'ff'}]

flag = False

def send_req():
    while not flag:
        data_to_send = random.choice(DATA)
        requests.post(URL, json=data_to_send)


threads = []
for i in range(10):
    threads.append(Thread(target=send_req))


try:
    for i in range(10):
        threads[i].start()
except KeyboardInterrupt as e:
    flag = not flag
    for i in range(10):
        threads[i].join()

