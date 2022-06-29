import configparser
import datetime
import logging
import os
import re
import platform
from telnetlib import EC
import urllib.parse as urlparse

import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import ui
from logging import handlers


def get_chrome_driver():
    chrome_options = Options()
    # options.add_argument('--proxy-server={}'.format('43.248.125.211:16816'))
    # chrome_options.add_argument('--headless')  # 无头模式
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument('enable-automation')
    # chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument("--disable-setuid-sandbox")

    chrome_options.add_argument("--disable-browser-side-navigation")
    chrome_options.add_argument('disable-infobars')
    chrome_options.add_argument('--window-size=1920,1080')  # 设置窗口界面大小
    chrome_options.add_argument('--disable-browser-side-navigation')
    # chrome_options.add_experimental_option('prefs', {'profile.default_content_setting_values': {'images': 3, }})

    # 谷歌文档提到需要加上这个属性来规避bug
    chrome_options.add_argument('--disable-gpu')
    # 最大化运行（全屏窗口）,不设置，取元素会报错
    chrome_options.add_argument('--start-maximized')
    # chrome_options.headless = True
    # 无图模式
    # chrome_options.add_argument('blink-settings=imagesEnabled=false')
    chrome_options.add_argument('--disable-plugins')
    chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    # chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    if platform.system() == 'Windows':
        driver = webdriver.Chrome(options=chrome_options)
    else:
        driver = webdriver.Chrome(executable_path='./chromedriver',
                                  options=chrome_options)
    return driver


def log_youtube(info):
    return get_logger('youtube').info(info)


def get_logger(filename):
    # logger = logging.getLogger()
    # logging_format = logging.Formatter('%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')
    # # rotahandler = handlers.RotatingFileHandler(os.path.join('root’, 'logs/my'), maxBytes=1024 * 1024 * 100)
    # rotating_handler = handlers.TimedRotatingFileHandler(os.path.join('root', 'logs/day'), when='s')
    # rotating_handler.setLevel(logging.DEBUG)
    # rotating_handler.setFormatter(logging_format)
    # logger.addHandler(rotating_handler)
    # return logger

    log_format = "%(levelname)s %(asctime)s - %(message)s"
    logging.basicConfig(filename=f"log/{filename}.log",
                        filemode="a",
                        format=log_format,
                        level=logging.INFO)
    return logging.getLogger()


# 播放时长转分钟
def conv_time_to_minutes(duration):
    if duration == '' or duration == 0:
        return 0
    split_array = duration.split(':')
    split_array_len = len(split_array)
    if split_array_len == 2:
        return int(split_array[0])
    elif split_array_len == 3:
        return int(split_array[0]) * 60 + int(split_array[1])
    else:
        return 0


# 亿万次 万次 次 转数字
def conv_views_to_number(views):
    if views == 0 or views == '':
        return 0
    if views.find('万') != -1:
        return int(float(views.split('万')[0]) * 1_0000)
    elif views.find('亿') != -1:
        return int(float(views.split('亿')[0]) * 1_0000_0000)
    elif views.find('次观看') != -1:
        return int(views.replace('次观看', ''))
    else:
        return 0


def conv_subscribe_to_number(views):
    if views == 0 or views == '':
        return 0
    if views.find('万') != -1:
        return int(float(views.split('万')[0]) * 1_0000)
    elif views.find('亿') != -1:
        return int(float(views.split('亿')[0]) * 1_0000_0000)
    elif views.find('位订阅') != -1:
        return int(views.replace('位订阅者', ''))
    else:
        return 0


# 日期（年-月-日）减小时，结果为日期（年-月-日）
def date_minus_hour(hours):
    now = datetime.datetime.now()
    date_format = '%Y-%m-%d'
    return (now + datetime.timedelta(hours=hours)).strftime(date_format)


# 计算几天前返回日期（年-月-日）
def before_days_to_date(days):
    now = datetime.datetime.now()
    date_format = '%Y-%m-%d'
    ddd = (now + datetime.timedelta(days=-days)).strftime(date_format)
    return ddd


# youtube 几个月前、几周前、几年前等转换为大概日期（年-月-日）
def conv_str_to_date(date):
    if date == '':
        return ''
    if date.find('直播') != -1:
        return date
    elif date.find('年') != -1:
        return before_days_to_date(int(date.split('年')[0]) * 365)
    elif date.find('个月') != -1:
        return before_days_to_date(int(date.split('个月')[0]) * 30)
    elif date.find('周') != -1:
        return before_days_to_date(int(date.split('周')[0]) * 7)
    elif date.find('天') != -1:
        return before_days_to_date(int(date.split('天')[0]))
    elif date.find('小时') != -1:
        return date_minus_hour(int(date.split('小时')[0]))
    else:
        return date


# 一直等待某元素可见，默认超时10秒
def is_visible(driver, locator, timeout=10):
    try:
        ui.WebDriverWait(driver, timeout).until(EC.visibility_of_element_located((By.XPATH, locator)))
        return True
    except TimeoutException:
        return False


# 一直等待某个元素消失，默认超时10秒
def is_not_visible(driver, locator, timeout=10):
    try:
        ui.WebDriverWait(driver, timeout).until_not(EC.visibility_of_element_located((By.XPATH, locator)))
        return True
    except TimeoutException:
        return False


def fetch_link_from_youtube_link(url):
    # 如果url链接中包含'redirect?event=channel_description&redir_token'，那么就进行抽取
    # 否则直接返回
    if url.find('redirect?event=channel_description') != -1:
        return urlparse.parse_qs(urlparse.urlparse(url).query)['q'][0];
    else:
        return url


def social_link_classification(url, social_type):
    tmp = ''
    for i in url:
        if i.find(social_type) != -1:
            return i
        else:
            tmp = ''
    return tmp


# 从社交媒体数组排除一部分链接
def clean_social_urls(url_array):
    temp = []
    will_deleted = ['youtube', 'facebook', 'tiktok', 'instagram', 'twitter']
    for i in range(0, len(url_array)):
        for j in range(0, len(will_deleted)):
            if url_array[i].find(will_deleted[j]) != -1:
                temp.append(url_array[i])

    a = set(url_array)
    b = set(temp)
    return a.difference(b)


# 获取全局配置
def get_global_config(key):
    if platform.system() == 'Windows':
        file_path = '.\\config\\config.ini'
    else:
        file_path = os.getcwd() + '/config/config.ini'
    config = configparser.ConfigParser()
    config.read_file(open(file_path, encoding='UTF-8'), 'rb')
    val = config.get('global', key)
    return val


# 提取邮箱
def get_emails_from_str(content):
    return ','.join(re.findall(
        r'([a-zA-Z0-9_.+-]+@[a-pr-zA-PRZ0-9-]+\.[a-zA-Z0-9-.]+)', content))


# 取掉最后斜杠
def remove_final_slash(str_):
    length = len(str_)
    if length == '':
        return str_
    elif str_[-1] == '/':
        return str_[0:length - 1]
    else:
        return str_


def append_row_to_file(filename: str, header_column: [], data):
    csv_name = f'export{os.sep}{filename}'
    try:
        if os.path.exists(csv_name):
            df = pd.DataFrame(data)
            df.to_csv(csv_name, mode='a', header=False, index=False, encoding='utf_8_sig')
        else:
            # TODO
            df = pd.DataFrame(data,
                              columns=header_column)
            df.to_csv(csv_name, index=False, encoding='utf_8_sig')
    except PermissionError:
        raise Exception('PermissionError ')
