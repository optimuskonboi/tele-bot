import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime
import schedule
import time
import requests
import json

with open('config.json') as config_file:
    config = json.load(config_file)

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets",
         "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]

creds = ServiceAccountCredentials.from_json_keyfile_name('key.json', scope)
client = gspread.authorize(creds)

sheet = client.open_by_url(config['sheet_url']).sheet1

current_index = 1

def send_telegram_message(message=""):
    token = config['token']
    chat_id = config['chat_id']
    try:
        url = f'https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={message}'
        response = requests.get(url)
        return response
    except Exception as e:
        print("Error send message telegram: ", e)
        return None

def send_daily_alert():
    global current_index
    attempts = 0
    while attempts < 3:
        try:
            data = sheet.get_all_values()
            total_rows = len(data)

            while current_index < total_rows:
                person = data[current_index][1]
                if person.strip() == "":
                    current_index = 1
                    continue
                incidense_response_day = data[current_index][0]
                phone_number, time_on_air = find_info_person(person, data)

                if person and phone_number:
                    message = f"Cập nhật ứng cứu sự cố:\nNgày: {incidense_response_day}\nTên: {person}\nSố điện thoại: {phone_number}\n"
                    if len(time_on_air) == 0:
                        time_on_air = "Tôi trực được 24/24"
                    message += f"Thời gian On-air: {time_on_air}"
                    print(message)
                    send_telegram_message(message=message)
                    current_index += 1
                    return
                else:
                    current_index += 1
                    if current_index >= total_rows:
                        current_index = 1
            attempts += 1
        except Exception as e:
            print(f"Lỗi khi lấy thông tin người ứng cứu sự cố: {e}")
            send_telegram_message(message="Có lỗi xảy ra khi lấy thông tin người ứng cứu sự cố")
            attempts += 1
            time.sleep(60)

def find_info_person(name, data):
    for i in range(1, len(data)):
        if data[i][4] == name:
            return data[i][5], data[i][6]
    return None, None

schedule.every().day.at("22:00").do(send_daily_alert)

current_index=13
send_daily_alert()
while True:
    schedule.run_pending()
    time.sleep(60)