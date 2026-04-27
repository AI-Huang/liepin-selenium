import csv
import re

from pyecharts import options as opts
from pyecharts.charts import Bar, Geo, Map, Pie
from pyecharts.globals import (
    ChartType,
    CurrentConfig,
    NotebookType,
    SymbolType,
    ThemeType,
)

companys = {}
propertiesdict = {}
scaledict = {}
industrydict = {}

propertiesjobnum = {}
industryjobnum = {}
catagoryjobnum = {}
citys = {}


def opencsv():
    global companys, propertiesdict, scaledict, industrydict, propertiesjobnum, industryjobnum, catagoryjobnum, citys
    with open("data/raw/data.csv", "r", encoding="utf-8") as fp:
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
            city = re.search(r"^\w*([.\w*$])", line["where"]).group()

            # 检查是否已有公司信息
            if line["companyname"] not in companys:
                # 建立公司字典
                companys[line["companyname"]] = line["companyname"]

                #  统计公司规模
                if line["scale"] != "":
                    if line["scale"] not in scaledict:
                        scaledict[line["scale"]] = 1
                    else:
                        scaledict[line["scale"]] += 1

                if re.search(r"\d*", line["num"]).group() != "":
                    line["num"] = int(line["num"])

                    # 统计企业类别
                    if line["properties"] != "":
                        if line["properties"] not in propertiesjobnum:
                            propertiesjobnum[line["properties"]] = line["num"]
                        else:
                            propertiesjobnum[line["properties"]] += line["num"]
                    # 统计行业类型
                    if line["industry"] not in industryjobnum:
                        industryjobnum[line["industry"]] = line["num"]
                    else:
                        industryjobnum[line["industry"]] += line["num"]
                    # 统计岗位需求
                    if line["catagory"] not in catagoryjobnum:
                        catagoryjobnum[line["catagory"]] = line["num"]
                    else:
                        catagoryjobnum[line["catagory"]] += line["num"]
                    # 统计个城市岗位数
                    if city not in citys:
                        citys[city] = line["num"]
                    else:
                        citys[city] += line["num"]
            # print(line)
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
    def show(self, data, title, theme=ThemeType.WHITE, center=["50%", "40%"]):
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
        pie.render(title + ".html")


class drawBar:
    def show(self, data, title, theme=ThemeType.WHITE):
        bar = (
            Bar(init_opts=opts.InitOpts(theme=theme))
            .add_xaxis(list(data.keys()))
            .add_yaxis(title, list(data.values()))
            .set_global_opts(title_opts=opts.TitleOpts(title=title))
            .render(title + ".html")
        )


class drawMap:
    def show(self, data, maptype="china", title="China-Map"):
        map = (
            Map()
            .add(
                series_name="岗位数",
                data_pair=list(data.items()),
                maptype="china",
                zoom=1,
                center=[105, 38],
            )
            .set_global_opts(
                title_opts=opts.TitleOpts(title=title),
                visualmap_opts=opts.VisualMapOpts(
                    max_=9999,
                    is_piecewise=True,
                    pieces=[
                        {"max": 9, "min": 0, "label": "0-9", "color": "#FFE4E1"},
                        {"max": 99, "min": 10, "label": "10-99", "color": "#FF7F50"},
                        {
                            "max": 499,
                            "min": 100,
                            "label": "100-499",
                            "color": "#F08080",
                        },
                        {
                            "max": 999,
                            "min": 500,
                            "label": "500-999",
                            "color": "#CD5C5C",
                        },
                        {
                            "max": 9999,
                            "min": 1000,
                            "label": ">=1000",
                            "color": "#8B0000",
                        },
                    ],
                ),
            )
        )
        map.render(title + ".html")


def draw():
    opencsv()
    drawproperties = drawPie()
    drawproperties.show(propertiesjobnum, "企业类型占比统计")
    drawindustry = drawPie()
    drawindustry.show(industryjobnum, "企业从事行业比例统计", center=["65%", "60%"])
    drawscale = drawBar()
    drawscale.show(scaledict, "企业规模统计", ThemeType.LIGHT)
    drawcatagory = drawBar()
    drawcatagory.show(catagoryjobnum, "各岗位需求统计")
    map = drawMap()
    map.show(data=citys, title="全国各城市就业岗位统计")


if __name__ == "__main__":
    opencsv()
    drawproperties = drawPie()
    drawproperties.show(propertiesjobnum, "企业类型占比统计")
    drawindustry = drawPie()
    drawindustry.show(industryjobnum, "企业从事行业比例统计", center=["65%", "60%"])
    drawscale = drawBar()
    drawscale.show(scaledict, "企业规模统计", ThemeType.LIGHT)
    drawcatagory = drawBar()
    drawcatagory.show(catagoryjobnum, "各岗位需求统计")
    map = drawMap()
    map.show(data=citys, title="全国各城市就业岗位统计")
