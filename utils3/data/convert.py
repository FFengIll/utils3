from typing import List, Dict, Any

import array
# time 主要提供时间点（绝对时间）的操作
import time
# datetime 主要提供相对时间的操作（如多少天，多少秒），包含日期和时刻的处理
import datetime


def intlist2bytes(data: List[int]):
    res = array.array('B', data).tobytes()
    return res


def intlist2str(data: List[int]):
    res = array.array('B', data).tostring()
    return res


def sec2time_str(second: int):
    local = time.localtime(second)
    res = time.strftime('%Y-%m-%d %H:%M:%S', local)
    return res


def ms2time_str(ms: int):
    return sec2time_str(int(ms / 1000))


def sec2date_time_str(second) -> str:
    res = datetime.timedelta(seconds=second)
    print(res)
    return str(res)


if __name__ == "__main__":
    sec2date_time_str(10000000)
