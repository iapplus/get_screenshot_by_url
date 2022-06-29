# import os
# import platform
# import time
# import api
# import utils
# import cv2
# import numpy as np
# import pyautogui
#
# pyautogui.FAILSAFE = False
# pyautogui.PAUSE = 1
#
# driver = utils.get_chrome_driver()
#
# def auto_translate(mac, window):
#     if platform.system() == 'Darwin':
#         right_click_location = mac[0]
#         translate_button = mac[1]
#     elif platform.system() == 'Windows':
#         right_click_location = window[0]
#         translate_button = window[1]
#     pyautogui.click(right_click_location[0], right_click_location[1], button='right')
#     pyautogui.click(translate_button[0], translate_button[1])
#     time.sleep(1)
#     pyautogui.click(right_click_location[0], right_click_location[1], button='right')
#     pyautogui.click(translate_button[0], translate_button[1])
#     time.sleep(1)
#
#
# while True:
#     json_text = api.get_data_by_api('https://tool.we-lock.com/api/Marketing/GetData/HotelsTopsites')
#     urls = json_text['data']
#     for url in urls:
#         try:
#             driver.get(f"https://{url}")
#             driver.execute_script(f"document.documentElement.scrollTop=0")
#             time.sleep(1)
#             height = driver.execute_script("return document.documentElement.clientHeight")
#             url_without_http = url.replace('https://', '').replace('/', '')
#             image_1 = f"images/{url_without_http}_1.png"
#             image_2 = f"images/{url_without_http}_2.png"
#             image_merged = f"images/{url_without_http}.png"
#             auto_translate(mac=[(60, 150), (188, 370)], window=[(60, 150), (188, 370)])
#
#             driver.save_screenshot(image_1)
#             # driver.execute_script(f"document.documentElement.scrollTop={height}")
#             time.sleep(1)
#             driver.execute_script(f"window.scrollBy(0,{height})")
#             time.sleep(1)
#             driver.save_screenshot(image_2)
#             img_out = np.concatenate((cv2.imread(image_1), cv2.imread(image_2)), axis=0)
#             cv2.imwrite(image_merged, img_out)
#             os.remove(image_1)
#             os.remove(image_2)
#         except Exception as e:
#             print(e)
#             pass
#     break
