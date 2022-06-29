import api
import os

# result = api.get_data_by_api('https://tool.we-lock.com/api/Marketing/GetData/HotelsTopsites')
# print(result)

file_list = os.listdir('images')
for f in file_list:
    sign = f.split('.')[-2][-1]
    if sign == '1' or sign == '2':
        os.remove(f"./images/{f}")
    else:
        pass