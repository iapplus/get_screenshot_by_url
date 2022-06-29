import time

import requests
import json
import urllib3.exceptions as urllib3_exception
import urllib3

urllib3.disable_warnings()


def get_data_by_api(url):
    try:
        data = {}
        res = requests.post(url=url, data=data, verify=False)
        return json.loads(res.text)
    except KeyError:
        print('无法获取JSON的KEY，JSON结构有问题')
        return []
    except ConnectionError:
        print('API服务器连接问题')
        get_data_by_api(url)
    except urllib3_exception.NewConnectionError:
        print('建立连接失败')
        get_data_by_api(url)
    except urllib3_exception.MaxRetryError:
        print('尝试多次仍然无法建立连接')
        get_data_by_api(url)
    except BaseException:
        print('Max retries exceeded')
        time.sleep(3)
        get_data_by_api(url)