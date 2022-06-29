import datetime
import threading
import queue
from concurrent.futures import ThreadPoolExecutor
import time
import api
import cv2
import numpy as np
import utils
import os

from qiniu import Auth, put_file, etag

# 截图翻译锁，同一时刻只有一个窗口能操作
lock = threading.Lock()
lock.acquire()
lock.release()

access_key = '_9AXty01pMpW1FseLSYoJBAf0as0rs7rgb2iyHfb'
secret_key = 'ufZTabeOcqaUZhbZFsdEh1_FhUQ3fa24Vf2eggxw'
qiniu_auth = Auth(access_key, secret_key)
bucket_name = '41d8cd98f00b204e9800998'


class BoundedThreadPoolExecutor(ThreadPoolExecutor):
    def __init__(self, max_workers=None, thread_name_prefix=''):
        super().__init__(max_workers, thread_name_prefix)
        self._work_queue = queue.Queue(max_workers)


q = queue.Queue(maxsize=100)


# def auto_translate(mac, window):
#     try:
#         if platform.system() == 'Darwin':
#             right_click_location = mac[0]
#             translate_button = mac[1]
#         elif platform.system() == 'Windows':
#             right_click_location = window[0]
#             translate_button = window[1]
#         pyautogui.click(right_click_location[0], right_click_location[1], button='right')
#         pyautogui.click(translate_button[0], translate_button[1])
#         time.sleep(1)
#         pyautogui.click(right_click_location[0], right_click_location[1], button='right')
#         pyautogui.click(translate_button[0], translate_button[1])
#         time.sleep(1)
#     except Exception:
#         pass


def request_api_timing():
    while True:
        if q.empty():
            json_text = api.get_data_by_api('https://tool.we-lock.com/api/Marketing/GetData/HotelsTopsites')
            urls = json_text['data']
            for url in urls:
                q.put(url)
        time.sleep(1)


thread_test = threading.Thread(target=request_api_timing)
thread_test.start()


def get_screenshot_by_url(driver, url):
    try:
        driver.get(f"https://{url}")
        driver.execute_script(f"document.documentElement.scrollTop=0")
        time.sleep(1)
        height = driver.execute_script("return document.documentElement.clientHeight")
        url_without_http = url.replace('https://', '').replace('/', '')
        image_1 = f"images/{url_without_http}_1.png"
        image_2 = f"images/{url_without_http}_2.png"

        image_name = f"{url_without_http}.png"
        image_merge = f"images{os.sep}{image_name}"
        lock.acquire()  # 加锁开始
        # auto_translate(mac=[(60, 150), (188, 370)], window=[(27, 188), (82, 421)])
        driver.save_screenshot(image_1)
        # driver.execute_script(f"document.documentElement.scrollTop={height}")
        time.sleep(1.2)
        driver.execute_script(f"window.scrollBy(0,{height})")
        time.sleep(2)
        driver.save_screenshot(image_2)
        time.sleep(0.3)
        img_out = np.concatenate((cv2.imread(image_1), cv2.imread(image_2)), axis=0)
        cv2.imwrite(image_merge, img_out)
        os.remove(image_1)
        os.remove(image_2)
        utils.append_row_to_file(
            'upload.csv',
            ['图片名称', '抓取日期'],
            [[image_merge,
              datetime.datetime.strftime(datetime.datetime.now(),
                                         '%Y-%m-%d %H:%M:%S')]])
        # 阿里云上传开始
        token = qiniu_auth.upload_token(bucket_name, image_name, 3600)
        ret, info = put_file(token, image_name, image_merge, version='v2')
        print(ret, info)
        os.remove(image_merge)
        # 阿里云上传结束
        lock.release()  # 加锁结束

        driver.quit()
        driver.close()

    except Exception as e:
        print("get_screenshot_by_url", e)
        lock.release()
        driver.quit()
        driver.close()


def task():
    while True:
        if not q.empty():
            url = q.get()
            driver = utils.get_chrome_driver()
            get_screenshot_by_url(driver, url)
            driver.quit()
            driver.close()


def thread_test_func_1():
    with BoundedThreadPoolExecutor(max_workers=4) as t:  # 创建一个最大容纳数量为n的线程池
        while True:
            t.submit(task)


thread_test1 = threading.Thread(target=thread_test_func_1)
thread_test1.start()
