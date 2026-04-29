import csv
import os
import re

from pyecharts import options as opts
from pyecharts.charts import Bar, Geo, Map, Pie
from pyecharts.globals import ThemeType

from liepin_selenium.datasets import get_province_only_in_manual_mapping

companys = {}
propertiesdict = {}
scaledict = {}
industrydict = {}

propertiesjobnum = {}
industryjobnum = {}
catagoryjobnum = {}
citys = {}


def opencsv(csv_path="data/raw/data.csv", encoding="utf-8") -> None:
    global companys, propertiesdict, scaledict, industrydict, propertiesjobnum, industryjobnum, catagoryjobnum, citys
    with open(csv_path, "r", encoding=encoding) as fp:
        csvdata = csv.DictReader(
            fp,
            [
                "job",
                "salary",
                "where",
                "time",
                "catagory",
                "num",
                "createtime",
                "companyname",
                "properties",
                "scale",
                "industry",
            ],
        )
        for line in csvdata:
            if line["job"] == "job":
                continue

            if re.search(r"\d*", line["num"]).group() != "":
                line["num"] = re.search(r"\d*", line["num"]).group()
            city_match = re.search(r"^[\u4e00-\u9fa5]+", line["where"])
            city = city_match.group() if city_match else line["where"][:2]

            if line["companyname"] not in companys:
                companys[line["companyname"]] = line["companyname"]

                if line["scale"] != "":
                    if line["scale"] not in scaledict:
                        scaledict[line["scale"]] = 1
                    else:
                        scaledict[line["scale"]] += 1

                if re.search(r"\d*", line["num"]).group() != "":
                    line["num"] = int(line["num"])

                    if line["properties"] != "":
                        if line["properties"] not in propertiesjobnum:
                            propertiesjobnum[line["properties"]] = line["num"]
                        else:
                            propertiesjobnum[line["properties"]] += line["num"]
                    if line["industry"] not in industryjobnum:
                        industryjobnum[line["industry"]] = line["num"]
                    else:
                        industryjobnum[line["industry"]] += line["num"]
                    if line["catagory"] not in catagoryjobnum:
                        catagoryjobnum[line["catagory"]] = line["num"]
                    else:
                        catagoryjobnum[line["catagory"]] += line["num"]
                    if city not in citys:
                        citys[city] = line["num"]
                    else:
                        citys[city] += line["num"]
    threshold = int(sum(industryjobnum.values()) * 0.01)
    temp = {key: value for key, value in industryjobnum.items() if value < threshold}
    industryjobnum = {
        key: value for key, value in industryjobnum.items() if value >= threshold
    }
    scaledict = dict(sorted(scaledict.items(), key=lambda d: d[0], reverse=False))
    if "其他" not in industryjobnum:
        industryjobnum["其他"] = sum(temp.values())
    else:
        industryjobnum["其他"] += sum(temp.values())


class drawPie:
    def show(
        self,
        data,
        title,
        theme=ThemeType.WHITE,
        center=["50%", "40%"],
        output_dir="figures",
    ):
        os.makedirs(output_dir, exist_ok=True)
        pie = (
            Pie(init_opts=opts.InitOpts(theme=theme))
            .add(
                title,
                [list(z) for z in zip(data.keys(), data.values())],
                center=center,
                radius=["20%", "35%"],
            )
            .set_global_opts(
                title_opts=opts.TitleOpts(title=title),
                legend_opts=opts.LegendOpts(
                    orient="vertical", pos_top="15%", pos_left="2%"
                ),
            )
            .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {d}"))
        )
        pie.render(os.path.join(output_dir, title + ".html"))


class drawBar:
    def show(self, data, title, theme=ThemeType.WHITE, output_dir="figures"):
        os.makedirs(output_dir, exist_ok=True)
        bar = (
            Bar(init_opts=opts.InitOpts(theme=theme))
            .add_xaxis(list(data.keys()))
            .add_yaxis(title, list(data.values()))
            .set_global_opts(title_opts=opts.TitleOpts(title=title))
            .render(os.path.join(output_dir, title + ".html"))
        )


class DrawMapProvince:

    def show(self, data, title="全国各省份就业岗位统计", output_dir="figures"):
        os.makedirs(output_dir, exist_ok=True)

        province_data = {}
        for city, value in data.items():

            try:
                province = get_province_only_in_manual_mapping(city)
            except ValueError as e:
                print(
                    f"get_province_only_in_manual_mapping({city}) 错误：错误信息：{e}"
                )
                continue

            if province not in province_data:
                province_data[province] = 0
            province_data[province] += value

        if not province_data:
            print("警告：没有有效的省份数据")
            return

        max_value = max(province_data.values())

        map_chart = (
            Map()
            .add(
                series_name="岗位数量",
                data_pair=list(province_data.items()),
                maptype="china",
                is_map_symbol_show=False,
            )
            .set_global_opts(
                title_opts=opts.TitleOpts(title=title),
                visualmap_opts=opts.VisualMapOpts(
                    max_=max(max_value, 100),
                    is_piecewise=True,
                    pieces=[
                        {"max": 9, "min": 0, "label": "0-9", "color": "#FFE4E1"},
                        {"max": 99, "min": 10, "label": "10-99", "color": "#FFCC99"},
                        {
                            "max": 299,
                            "min": 100,
                            "label": "100-299",
                            "color": "#FF9966",
                        },
                        {
                            "max": 499,
                            "min": 300,
                            "label": "300-499",
                            "color": "#FF6666",
                        },
                        {"max": 9999, "min": 500, "label": ">=500", "color": "#CC0033"},
                    ],
                ),
            )
        )
        map_chart.render(os.path.join(output_dir, title + ".html"))
        print(f"地图已生成：{os.path.join(output_dir, title + '.html')}")


class DrawMapCity:
    def show(self, data, title="全国各城市就业岗位统计", output_dir="figures"):
        os.makedirs(output_dir, exist_ok=True)

        # 过滤掉非中国城市（检查是否在 pyecharts.COORDINATES 中）
        from pyecharts.datasets import COORDINATES

        city_data = []
        for city, value in data.items():
            # 检查城市是否在中国坐标数据中
            if city in COORDINATES:
                city_data.append([city, value])
            else:
                # 尝试去掉"市"等后缀后再检查
                normalized_city = (
                    city.replace("市", "")
                    .replace("省", "")
                    .replace("区", "")
                    .replace("县", "")
                )
                if normalized_city in COORDINATES:
                    city_data.append([normalized_city, value])
                else:
                    print(f"警告：跳过未知城市 '{city}'（非中国城市或坐标不存在）")

        if not city_data:
            print("警告：没有有效的城市数据")
            return

        max_value = max([v for _, v in city_data])

        map_chart = (
            Geo()
            .add_schema(
                maptype="china",
                # 使用浅色背景（移除深色设置，使用默认或浅色）
                itemstyle_opts=opts.ItemStyleOpts(color="#E8E8E8", border_color="#666"),
            )
            .add(
                series_name="岗位数量",
                data_pair=city_data,
                type_="scatter",
                symbol_size=10,
            )
            .set_series_opts(
                label_opts=opts.LabelOpts(is_show=False),
                # 移除涟漪效果（可选）
                effect_opts=opts.EffectOpts(is_show=True, scale=3),
            )
            .set_global_opts(
                title_opts=opts.TitleOpts(title=title),
                visualmap_opts=opts.VisualMapOpts(
                    max_=max(max_value, 100),
                    is_piecewise=True,
                    pieces=[
                        {"max": 9, "min": 0, "label": "0-9", "color": "#FFE4E1"},
                        {"max": 99, "min": 10, "label": "10-99", "color": "#FFCC99"},
                        {
                            "max": 299,
                            "min": 100,
                            "label": "100-299",
                            "color": "#FF9966",
                        },
                        {
                            "max": 499,
                            "min": 300,
                            "label": "300-499",
                            "color": "#FF6666",
                        },
                        {"max": 9999, "min": 500, "label": ">=500", "color": "#CC0033"},
                    ],
                ),
            )
        )
        map_chart.render(os.path.join(output_dir, title + ".html"))
        print(f"城市地图已生成：{os.path.join(output_dir, title + '.html')}")


def draw(csv_path="data/raw/data.csv", encoding="utf-8", output_dir="figures"):
    opencsv(csv_path, encoding)
    drawproperties = drawPie()
    drawproperties.show(propertiesjobnum, "企业类型占比统计", output_dir=output_dir)
    drawindustry = drawPie()
    drawindustry.show(
        industryjobnum,
        "企业从事行业比例统计",
        center=["65%", "60%"],
        output_dir=output_dir,
    )
    drawscale = drawBar()
    drawscale.show(scaledict, "企业规模统计", ThemeType.LIGHT, output_dir=output_dir)
    drawcatagory = drawBar()
    drawcatagory.show(catagoryjobnum, "各岗位需求统计", output_dir=output_dir)

    # 绘制省份色块图
    map_province = DrawMapProvince()
    map_province.show(data=citys, title="全国各省份就业岗位统计", output_dir=output_dir)

    # 绘制城市点状图
    map_city = DrawMapCity()
    map_city.show(data=citys, title="全国各城市就业岗位统计", output_dir=output_dir)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="猎聘数据可视化工具")
    parser.add_argument(
        "--csv", type=str, default="data/raw/data.csv", help="CSV文件路径"
    )
    parser.add_argument("--encoding", type=str, default="utf-8", help="文件编码")
    parser.add_argument(
        "--output-dir", type=str, default="figures", help="图表输出目录"
    )
    args = parser.parse_args()

    draw(csv_path=args.csv, encoding=args.encoding, output_dir=args.output_dir)
