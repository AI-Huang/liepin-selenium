#!/usr/bin/env python3
"""获取 pyecharts 城市坐标并保存到 JSON 文件

该脚本从 pyecharts.datasets.COORDINATES 获取所有中国城市的坐标信息，
并结合省份映射信息，保存到 cn_city_province_map.json 文件中。

输出格式参考 template.json:
{
    "城市名": {
        "province": "省份名",
        "lat": 纬度,
        "lon": 经度
    }
}
"""

import json
import os

from pyecharts.datasets import COORDINATES

# 导入省份映射函数
# from .city_province_mapper import get_province


def save_city_coordinates(output_file: str = "cn_city_province_map.json") -> None:
    """保存城市坐标和省份信息到 JSON 文件

    :param output_file: 输出文件路径，默认为 cn_city_province_map.json
    :type output_file: str
    """
    # 获取 pyecharts 中的所有城市
    cities = list(COORDINATES.keys())
    print(f"发现 {len(cities)} 个城市")

    # 构建城市数据字典
    city_data = {}
    for city in cities:
        # 获取坐标 (lng, lat)
        coord = COORDINATES[city]
        lon, lat = coord[0], coord[1]

        # 获取省份
        # province = get_province(city)

        # 添加到字典
        city_data[city] = {"province": "", "lat": lat, "lon": lon}

    # 获取输出文件的绝对路径
    output_path = os.path.join(os.path.dirname(__file__), output_file)

    # 保存到 JSON 文件
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(city_data, f, ensure_ascii=False, indent=2)

    print(f"已保存 {len(city_data)} 条城市数据到 {output_path}")


if __name__ == "__main__":
    save_city_coordinates()
