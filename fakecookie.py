import requests
import re
import string
import os
import threading
import random
import time
from queue import Queue
# Привет, этот бот магазин cookie и не только сделан JealLeal(vzxdev)
# Если ты не разбираешь в python советую не чего не трогать
# Чтобы загрузить куки оптом запиши куки в строчку в файле cookies.txt.
# Данный код раньше использовался в нашем боте
# По всем вопросам - https://t.me/HelpVoixBot 
outputfile = open("cookies.txt", "a")

x = 0
cookies = []
intro = "_|WARNING:-DO-NOT-SHARE-THIS.--Sharing-this-will-allow-someone-to-log-in-as-you-and-to-steal-your-ROBUX-and-items.|_"
n = 0
c = int(input("How many cookies do you want to generate? \n"))
letters = 'ABCDEF'

while x < c:


    cookies =  intro +  ''.join(random.choices(letters + string.digits, k=732))

    x = x + 1
    
    f = open('Cookies.txt', "a+")
    f.write(f'{cookies}\n')
    f.close()
    

if __name__ == '__main__':

    number_of_threads = 900
    print_lock = threading.Lock()
    cookie_queue = Queue()
    url = 'https://accountinformation.roblox.com/v1/birthdate'

        
    cookie_queue.join()

outputfile.close()

t1 = time.time()
print('Done! IF any valid cookies were found, they have been added to the hits.txt file!')
input("Press enter to exit.")




 