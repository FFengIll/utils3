from typing import List, Dict, Any

import array


def intlist2bytes(data: List[int]):
    res = array.array('B', data).tobytes()
    return res


def intlist2str(data: List[int]):
    res = array.array('B', data).tostring()
    return res
