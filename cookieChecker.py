import os
import json
import requests
from colorama import Fore, init, Back, Style

# Привет, этот бот магазин cookie и не только сделан JealLeal(vzxdev)
# Если ты не разбираешь в python советую не чего не трогать
# Чтобы загрузить куки оптом запиши куки в строчку в файле cookies.txt.
# Данный код раньше использовался в нашем боте
# По всем вопросам - https://t.me/HelpVoixBot 


# Открываем файл с куками
valid = 0
invalid = 0
with open("cookies.txt", "r", encoding="utf-8") as file:
    lines = file.readlines()

# Папки для сохранения файлов
output_dir = "files"
output_dir2 = "tov"

# Создаем папки, если они не существуют
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
if not os.path.exists(output_dir2):
    os.makedirs(output_dir2)

# Счетчик для номера линии
line_counter = 1

def save_cookie(cookie):
    global line_counter
    req = requests.Session()
    req.cookies['.ROBLOSECURITY'] = cookie
    try:
        r = req.get('https://www.roblox.com/mobileapi/userinfo')
        if 'mobileapi/user' in r.url:
            valid += 1
            next
            print(Fore.GREEN + "Valid Cookie Found")
            txt_filename = os.path.join(output_dir, f"{line_counter}.txt")
            with open(txt_filename, "w", encoding="utf-8") as txt_file:
                txt_file.write(cookie)

            # Путь к файлу для JSON
            output_txt = f'files/{line_counter}.txt'
            
            # Создаем JSON-файл для магазина
            json_data = {
                "name": f"Roblox Cookie | №{line_counter}",
                "price": 100,  # Укажите цену товара
                "file": output_txt,  # Путь к файлу с куки
            }
            
            json_filename = os.path.join(output_dir2, f"cookie{line_counter}.json")
            with open(json_filename, "w", encoding="utf-8") as json_file:
                json.dump(json_data, json_file, ensure_ascii=False, indent=4)
            
            print(f"Сохранено: {txt_filename} и {json_filename}")
            line_counter += 1

        else:
            
            invalid += 1
            print("Невалид куки, недопуск к продаже")
            return False
            
    except:
        print("Невалид куки, недопуск к продаже")
        return False
    # Сохраняем куки в текстовый файл
    
def main():
    for line in lines:
        line = line.strip()  # Удаляем лишние пробелы и переносы строк
        if line:  # Проверяем, что строка не пустая
            save_cookie(line)
        else:
            print("Пустая строка. Пропущено.")

if __name__ == "__main__":
    main()
