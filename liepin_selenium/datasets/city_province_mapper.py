"""城市到省份映射模块

该模块提供城市名称到省份名称的映射功能，支持多种映射方式：

1. **手动映射**：覆盖全国主要城市的预定义映射表
2. **地理编码**：使用 geopy 进行地理编码（可选）
3. **首字符推断**：根据城市首字推断省份
4. **兜底逻辑**：自动添加省/市/自治区后缀

模块特性：
- 支持批量处理城市列表
- 支持构建缓存文件
- 优雅处理地理编码不可用的情况
"""

import json
import os
from functools import lru_cache
from typing import Dict, Optional

# 加载 pyecharts 的城市坐标数据
try:
    from pyecharts.datasets import COORDINATES
except ImportError:
    COORDINATES = {}

# 尝试导入 geopy，如果失败则禁用地理编码
try:
    from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
    from geopy.geocoders import Nominatim

    GEOCODING_AVAILABLE = True
except ImportError:
    GEOCODING_AVAILABLE = False


def load_province_cities() -> Dict[str, str]:
    """从 province_cities.json 加载城市-省份映射

    :return: 城市到省份的映射字典
    :rtype: Dict[str, str]
    """
    mapping = {}
    json_path = os.path.join(os.path.dirname(__file__), "province_cities.json")

    if os.path.exists(json_path):
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        for province, cities in data.items():
            for city in cities:
                # 标准化城市名称（移除"市"后缀以匹配 pyechart）
                normalized_city = (
                    city.replace("市", "")
                    .replace("区", "")
                    .replace("县", "")
                    .replace("州", "")
                )
                mapping[normalized_city] = province
                # 同时保留原始城市名映射
                mapping[city] = province

    return mapping


# 从 province_cities.json 构建城市-省份映射字典（符合 pyechart 名字规范）
MANUAL_MAPPING = load_province_cities()

# 初始化地理编码器（如果可用）
geolocator = None
if GEOCODING_AVAILABLE:
    try:
        geolocator = Nominatim(user_agent="liepin-selenium", timeout=10)
    except Exception:
        geolocator = None


@lru_cache(maxsize=1000)
def get_province_by_geocode(city_name: str) -> Optional[str]:
    """使用 geopy 地理编码获取城市所属省份

    :param city_name: 城市名称
    :type city_name: str
    :return: 省份名称，如果无法获取则返回 None
    :rtype: Optional[str]
    """
    if not geolocator:
        return None

    try:
        location = geolocator.geocode(city_name + " 中国", exactly_one=True)
        if location:
            address = location.address
            address_parts = address.split(", ")
            for part in address_parts:
                if "省" in part or "自治区" in part or "市" in part:
                    return part.strip()
        return None
    except (GeocoderTimedOut, GeocoderUnavailable, ValueError, Exception):
        return None


def get_province_only_in_manual_mapping(city_name: str) -> str:
    """仅使用手动映射表获取城市所属省份

    :param city_name: 城市名称
    :type city_name: str
    :return: 省份名称
    :rtype: str
    """
    # 1. 首先尝试直接匹配
    if city_name in MANUAL_MAPPING:
        return MANUAL_MAPPING[city_name]

    # 2. 尝试去掉常见后缀后匹配
    suffixes = ["市", "省", "区", "县", "州", "镇", "乡"]
    normalized_city = city_name
    for suffix in suffixes:
        normalized_city = normalized_city.replace(suffix, "")

    if normalized_city in MANUAL_MAPPING:
        return MANUAL_MAPPING[normalized_city]

    # 3. 处理"上海市市辖区"这种组合情况
    # 检查城市名是否包含已知的省份名称
    for province in MANUAL_MAPPING.values():
        if province in city_name:
            return province

    # 4. 尝试去掉末尾的"市辖区"、"区"等
    special_suffixes = ["市辖区", "辖区", "城区"]
    temp_city = city_name
    for suffix in special_suffixes:
        if temp_city.endswith(suffix):
            temp_city = temp_city[: -len(suffix)]
            if temp_city in MANUAL_MAPPING:
                return MANUAL_MAPPING[temp_city]

    # 5. 检查是否是直辖市的特殊情况
    municipality_mapping = {
        "北京市": "北京市",
        "天津市": "天津市",
        "上海市": "上海市",
        "重庆市": "重庆市",
    }
    for municipality in municipality_mapping:
        if municipality in city_name or municipality[:-1] in city_name:
            return municipality

    raise ValueError(f"无法确定城市 '{city_name}' 的省份")


def get_province(city_name: str) -> str:
    """获取城市所属省份

    映射优先级：
    1. MANUAL_MAPPING 映射表（从 province_cities.json 构建）
    2. geopy 地理编码（如果可用）
    3. 首字符推断规则
    4. 兜底逻辑（添加省/市/自治区后缀）

    :param city_name: 城市名称
    :type city_name: str
    :return: 省份名称
    :rtype: str
    """
    # 先检查原始城市名是否在映射中
    if city_name in MANUAL_MAPPING:
        return MANUAL_MAPPING[city_name]
    # 标准化城市名称（移除常见后缀）
    normalized_city = (
        city_name.replace("市", "")
        .replace("省", "")
        .replace("区", "")
        .replace("县", "")
        .replace("州", "")
    )

    # 优先使用 MANUAL_MAPPING
    if normalized_city in MANUAL_MAPPING:
        return MANUAL_MAPPING[normalized_city]

    # 尝试使用地理编码
    result = get_province_by_geocode(normalized_city)
    if result:
        return result

    # 特殊处理直辖市
    if normalized_city in ["北京", "天津", "上海", "重庆"]:
        return normalized_city + "市"

    # 特殊处理自治区
    if normalized_city in ["内蒙古", "广西", "西藏", "宁夏", "新疆"]:
        return normalized_city + "自治区"

    # 兜底：返回城市名+"省"（可能不准确，但至少格式正确）
    return normalized_city + "省"


def get_address(lat: float, lng: float) -> Optional[str]:
    """根据经纬度获取详细地址

    :param lat: 纬度
    :type lat: float
    :param lng: 经度
    :type lng: float
    :return: 详细地址字符串，如果无法获取则返回 None
    :rtype: Optional[str]
    """
    if not geolocator:
        return None

    try:
        loc = geolocator.reverse(f"{lat},{lng}", timeout=10)
        return loc.address if loc else None
    except (GeocoderTimedOut, GeocoderUnavailable, ValueError, Exception):
        return None


def batch_get_provinces(city_list: list) -> Dict[str, str]:
    """批量获取城市列表对应的省份

    :param city_list: 城市名称列表
    :type city_list: list
    :return: 城市到省份的映射字典
    :rtype: Dict[str, str]
    """
    result = {}
    for city in city_list:
        result[city] = get_province(city)
    return result
