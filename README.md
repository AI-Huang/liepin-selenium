# Python程序设计报告

## 一、项目背景与需求分析

### 1.项目背景

本项目目标是在疫情下的就业难问题通过数据分析，在毕业生结合自身发展需要的情况下为就业的方向提供一定的数据参考。

### 2.需求分析

分析企业招聘的岗位需求在全国各地区的分布情况及各类型岗位的需求，以及对招聘企业的行业分析及规模进行统计。

## 二、概要设计

### 1.技术栈选型

使用selenium框架作为爬虫的主体，BeautifulSoup实现HTML数据解析，数据分析部分使用re模块做正则匹配以进行统计，数据保存部分使用csv模块进行读写爬取到的数据，pyecharts模块实现数据可视化。

### 2.系统架构

该爬虫使用了多进程+多线程的结构共分为4大模块，分别为主进程控制模块、爬虫模块、数据存储模块、数据可视化模块，分别对应main.py，spider.py，savedata.py，showdata.py。

目录树为

```
liepin-selenium
│  acquire.py
│  data.csv
│  geckodriver.exe
│  geckodriver.log
│  main.py
│  requestPage.py
│  savefile.py
│  showdata.py
│  spider.py
│  企业从事行业比例统计.html
│  企业类型占比统计.html
│  企业规模统计.html
│  全国各城市就业岗位统计.html
│  各岗位需求统计.html
│  
├─.idea
│  │  .gitignore
│  │  liepin-selenium.iml
│  │  misc.xml
│  │  modules.xml
│  │  workspace.xml
│  │  
│  └─inspectionProfiles
│          profiles_settings.xml
│          
└─__pycache__
        acquire.cpython-38.pyc
        dataprocess.cpython-38.pyc
        requestPage.cpython-38.pyc
        savefile.cpython-38.pyc
        showdata.cpython-38.pyc
        spider.cpython-38.pyc
        thread.cpython-38.pyc
```

mian.py是主进程，spider和savedata均为子进程，spider中的连个爬虫均分为两个线程。

### 3.数据爬取总体流程

程序从main.py文件中的`if __name__ == '__main__':`开始程序将创建并初始化一个拥有两个线程的线程池,随后将初始化用于进程间通信的消息队列，然后创建两个进程池共享的dict分别用于存储进程PID和程序停止信号量。然后启动spider和savedata两个进程并等待输入程序停止指令。

spider.py文件中的start函数将创建两个线程以调用两个爬虫各自的启动函数启动爬虫。其中一个爬虫爬取职位列表页，另一个爬取职位详情页，爬取职位列表页的爬虫将通过线程间消息传递把从列表页上获取到的详情页URL传递给职位详情页爬虫，该过程使用线程间通信的互斥锁方案以保护数据不会。

savedata.py文件将通过消息队列获取从spider传递过来的数据并存逐条存如csv格式文件中，待检测到停止信号后停止写入然后调用绘图函数进行数据分析及可视化。

当主进程捕获到输入字符`q`后将把用于传递程序停止信号的dict值设为`False`，然后各进程将检测到该信号然后结束进程。savedata进程在退出前将调用showdata中的绘图函数进行数据分析和绘图并存为HTML文件。

## 三、详细设计

### 1、数据源说明

由于数据源过多在此不进行详细列举，仅说明URL的公共路径

职位列表页URL：`https://campus.liepin.com/sojob/pn<page number>`

各职位详情页URL：`https://campus.liepin.com/job/<jobid>`

职位列表页仅提取职位详情页的URL，职位详情页将提取8个字段分别是`job　salary　where　time　catagory　num　createtime　company`，其中`company`字段包含`companyname properties scale industry`这4个字段。并存为dict。

### 2、数据表设计

本程序使用csv格式文件存储数据。数据按照职位进行存储，每一个职位一行，数据名称与字段名对应关系如下表所示

| 中文名称 | 字段名      | 数据类型 | 是否主外键 |
| -------- | ----------- | -------- | ---------- |
| 职位     | job         | string   |            |
| 薪资     | salary      | string   |            |
| 工作地点 | where       | string   |            |
| 时间     | time        | string   |            |
| 岗位     | catagory    | string   |            |
| 招聘人数 | num         | string   |            |
| 创建时间 | createtime  | string   |            |
| 企业名称 | companyname | string   |            |
| 企业性质 | properties  | string   |            |
| 企业规模 | scale       | string   |            |
| 所处行业 | industry    | string   |            |

### 3、具体问题解决方案

在实现多进程过程中，起初仅单独创建两个进程通过传入Queue对象的方式共享队列，但仍多进程队列消息无法传递的问题，经过调试发现传入的Queue对象与源对象所存储的内存地址不同，等同与创建了一个Queue对象副本，故无法进行进程间消息的传递，后使用进程池的方法，用Manager对象创建Queue对象并传入子进程成功解决了进程间消息无法传递传递问题。

在实现多线程时仅使用 产生了死锁问题，后经过查阅资料引用了《cookbook》中的实例完美解决该问题（即acquire.py中的代码）。

## 四、数据分析或可视化

### 1.岗位需求统计

从该图中可以得出哪些种岗位的市场需求较大，哪些最少结合当今的社会发展可规划未来的个人发展方向。也可结合个人情况分析未来哪些职业的发展前景较好，并为之指定发展计划。（不足，数据多比较难看，实际为动态图可选择想看的数据）

![岗位需求统计](./figures/msedge_90NhjeHN5x.png)

### 2.全国各城市提供的就业岗位统计

通过分析该数据可以为个人未来在哪个城市发展提供参考，结合其它统计数据可分析出

![全国各城市岗位统计](./figures/msedge_pfpYcPVROt.png)

### 3.企业类型统计

该统计可为以后的个人发展提供参考，由于不同类型的企业其管理理念、价值观、以及企业文化的不同，结合个人生涯规划为以后的应聘目标提供参考。

![image-20201230210634533](./figures/msedge_Cs1J1JotSa.png)

### 4.企业所处行业统计

根据企业从事行业可毕业生选择企业做好规划和铺垫。

![image-20201230210509248](./figures/msedge_SncxsmcIy4.png)

### 5.企业规模统计

通过企业规模统计可对不同规模的企业数进行统计，为其他如投资公司、初创企业孵化平台提供数据支持。

![image-20201230210836341](./figures/msedge_aO8YYUhIUU.png)

## 五、结论与展望

### 1.结论

实现了猎聘校招网页的爬取、数据的存储以及简单的数据分析和可视化。

### 2.展望

企业所处行业分析数据整合不够完整，有些相关数据没有合并，行业薪资没有分析、以及企业规模与薪资的关系、职位类型与应聘要求间的关系没有分析等。没有使用数据库。未来还可做网页实时动态可视化分析。

## 附录

### main.py

```python
import multiprocessing
import spider
import savefile
import time

if __name__ == '__main__':
    print("Program Started...")

    pool = multiprocessing.Pool(2)
    manager = multiprocessing.Manager()
    data = manager.Queue()
    # save = manager.Queue()
    pidlist = manager.dict()
    single = manager.dict()
    single.update({'spider':True, 'spiderstate':False, 'savedatastate':False})
    spiderProcess = pool.apply_async(spider.startspider, (data, single, pidlist,))
    savefileProcess = pool.apply_async(savefile.start, (data, single, pidlist,))
    time.sleep(3)
    print('ProcessPID' + str(pidlist))
    while single['spider']:
        key = input('输入<q>退出:')
        if key == 'q':

            single['spider'] = False
            time.sleep(20)
            time.sleep(20)
            print('quit')
```

### spider.py

```python
from bs4 import BeautifulSoup
import threading
import requestPage
import random, time
import acquire
import os
import thread

x_lock = threading.Lock()
y_lock = threading.Lock()

detailpageurls = []
spidersingle = True

class listpage(requestPage.Browser):

    def start_url(self, starturl):
        self.get_page(starturl, self.parse)

    def parse(self, response):
        soup = BeautifulSoup(response, 'lxml')
        joblist = soup.find('div', 'main').find('ul', 'super-jobs job-lists')
        urls = joblist.find_all('a','ellipsis')[::2]
        with acquire.acquire(x_lock, y_lock):
            detailpageurls.extend(urls)
        nextpage = soup.find('div', 'searchResultPagination').find_all('a')[-1]
        delay = random.randrange(25, 45)
        time.sleep(delay)
        if spidersingle == True:
            self.follow(nextpage['href'], self.parse)




class detailpage(requestPage.Browser):
    def __init__(self, browser, queue):
        super(detailpage, self).__init__(browser)
        self.queue = queue
    def start_url(self):

        urls = []
        while True:
            with acquire.acquire(y_lock, x_lock):
                if len(detailpageurls):
                    alabels = detailpageurls
                    urls.extend(alabels)
                    detailpageurls.clear()
            if len(urls):
                self.get_page(urls[0]['href'], self.parse)
                del urls[0]
                time.sleep(random.randrange(0,4))
            else:
                time.sleep(3)

    def parse(self, response):
        # print(self.queue)
        global detailpageurls
        soup = BeautifulSoup(response, 'lxml')
        jobtitle = soup.find('div','job-brief wrap')
        jobdescribe = soup.find('div', 'job-desc').find('p')
        company = soup.find('div', 'company-address').find('div', 'company-desc')
        companyinfo = {}
        companyinfolist = company.find_all('p')
        companyinfo['companyname'] = company.find('a').text

        companyinfo['properties'] = companyinfolist[0].text[3::]
        companyinfo['scale'] = companyinfolist[1].text[3::]
        companyinfo['industry'] = companyinfolist[2].text[3::]
        item = {}
        item['job'] = jobtitle.find('h1','job-name').text
        item['salary'] = jobtitle.find('span','salary').text
        item['where'] = jobtitle.find('span', 'where').text
        item['time'] = jobtitle.find('span', 'time').text
        item['catagory'] = jobtitle.find('span','catagory').text
        item['num'] = jobtitle.find('span', 'num').text
        item['createtime'] = jobtitle.find('span', 'create-time').text
        item['company'] = companyinfo
        self.queue.put(item)

def startlistpagespider():
    print('listspider已运行')
    browser = listpage("Firefox")
    browser.start_url('https://campus.liepin.com/sojob/')

def startpagespider(queue):
    print('pagespider已运行')
    browser = detailpage("Firefox", queue)
    browser.start_url()


def startspider(queue, single, processpid):
    processpid['spider'] = os.getpid()
    listpagespider = threading.Thread(target=startlistpagespider)
    listpagespider.start()
    getdetailpage = threading.Thread(target=startpagespider, args=(queue,))
    getdetailpage.start()
    while single['spider']:
        pass
    else:
        global spidersingle
        spidersingle = False
        listpagespider.join()
        getdetailpage.join()
        print('stop spider')
        single['spiderstate'] = True


if __name__ == '__main__':
    listpagespider = threading.Thread(target=startlistpagespider)
    listpagespider.start()
    getdetailpage = threading.Thread(target=startpagespider)
    getdetailpage.start()

```

### requestsPage.py

```python
from selenium import webdriver

from selenium.webdriver.common.keys import Keys

class Browser(object):
    def __init__(self, browser="Chrome"):
        try:
            if browser == "Chrome":
                self.driver = webdriver.Chrome()
            elif browser == "Firefox":
                self.driver = webdriver.Firefox()
            else:
                self.driver = webdriver.Safari()
        except Exception as error:
            print(error)

    # 虚函数,用于防止回调函数报错
    def parse(self, callback):
        pass
    # 仅用于网页爬取,使用回调函数进行处理
    def get_page(self, url, callback=parse):
        try:
            self.driver.get(url)
            callback(self.driver.page_source)
            return self.driver.page_source
        except Exception as error:
            return error

    def follow(self, url, callback=parse):
        try:
            if type(url) is str:
                    self.get_page(url, callback)
            elif type(url) is list:
                for aurl in url:
                    if type(aurl) is str:
                        self.get_page(aurl, callback)
        except Exception as error:

            return error


    def followall(self, urls, callback=parse):
        try:
            for url in urls:
                self.get_page(url, callback)
        except Exception as error:
            return error

    def find_element(self, label, value):
        return self.driver.find_element(label, value)


    def send_keys(self, element, value):
        try:
            element.send_keys(value)
        except Exception as error:
            print(error)
            print('The element param need a object of element.')
            return (error)

    def clear_content(self, element):
        try:
            element.clear()
        except Exception as error:
            print(error)
            print('The element param need a object of element.')
            return (error)



    def close(self):
        self.driver.close()



def parse(response):
    assert "Python" in browser.driver.title
    elem = browser.driver.find_element_by_name("q")
    elem.clear()
    elem.send_keys("pycon")
    browser.send_keys(elem, Keys.RETURN)
    assert "No resutls found." not in browser.driver.page_source
    print(type(elem))
    print(elem)
    browser.get_page("https://www.baidu.com/")


if __name__ == '__main__':
    browser = Browser("Firefox")
    browser.get_page("http://www.python.org/", parse)
    browser.close()
```

### acquire.py

```python
import threading
from contextlib import contextmanager

# Thread-local state to stored information on locks already acquired
_local = threading.local()

@contextmanager
def acquire(*locks):
    # Sort locks by object identifier
    locks = sorted(locks, key=lambda x: id(x))

    # Make sure lock order of previously acquired locks is not violated
    acquired = getattr(_local,'acquired',[])
    if acquired and max(id(lock) for lock in acquired) >= id(locks[0]):
        raise RuntimeError('Lock Order Violation')

    # Acquire all of the locks
    acquired.extend(locks)
    _local.acquired = acquired

    try:
        for lock in locks:
            lock.acquire()
        yield
    finally:
        # Release locks in reverse order of acquisition
        for lock in reversed(locks):
            lock.release()
        del acquired[-len(locks):]
```

### savefile.py

```python
import os, csv, showdata

def start(queue, single, processpid):
    processpid['savedata'] = os.getpid()
    print('savedata已启动')
    with open('data.csv','w', newline='') as fp:
        csvdata = csv.DictWriter(fp, ['job', 'salary', 'where', 'time', 'catagory', 'num', 'createtime', 'companyname', 'properties', 'scale', 'industry'])
        csvdata.writeheader()
        while single['spider']:
            data = queue.get()
            data.update(data['company'])
            del data['company']
            csvdata.writerow(data)
        else:
            single['savedatastate'] = True
            showdata.draw()
            print('stop savedata')
```

### showdata.py

```python
import csv, re
from pyecharts import options as opts
from pyecharts.charts import Geo, Bar, Pie, Map
from pyecharts.globals import ChartType, SymbolType, ThemeType
from pyecharts.globals import CurrentConfig, NotebookType


companys = {}
propertiesdict = {}
scaledict = {}
industrydict = {}

propertiesjobnum = {}
industryjobnum = {}
catagoryjobnum = {}
citys = {}

def opencsv():
    global  companys, propertiesdict, scaledict, industrydict, propertiesjobnum, industryjobnum, catagoryjobnum, citys
    with open('data.csv','r') as fp:
        csvdata = csv.DictReader(fp, ['job', 'salary', 'where', 'time', 'catagory', 'num', 'createtime', 'companyname', 'properties', 'scale', 'industry'])
        for line in csvdata :
            if line['job'] == 'job':
                continue

            if re.search(r'\d*', line['num']).group() != '':
                line['num'] = re.search(r'\d*', line['num']).group()
            city = re.search(r'^\w*([.\w*$])', line['where']).group()


            # 检查是否已有公司信息
            if line['companyname'] not in companys:
                # 建立公司字典
                companys[line['companyname']] = line['companyname']

                #  统计公司规模
                if line['scale'] != '':
                    if line['scale'] not in scaledict:
                        scaledict[line['scale']] = 1
                    else:
                        scaledict[line['scale']] += 1

                if re.search(r'\d*', line['num']).group() != '':
                    line['num'] = int(line['num'])

                    # 统计企业类别
                    if line['properties'] != '':
                        if line['properties'] not in propertiesjobnum:
                            propertiesjobnum[line['properties']] = line['num']
                        else:
                            propertiesjobnum[line['properties']] += line['num']
                    # 统计行业类型
                    if line['industry'] not in industryjobnum:
                        industryjobnum[line['industry']] = line['num']
                    else:
                        industryjobnum[line['industry']] += line['num']
                    # 统计岗位需求
                    if line['catagory'] not in catagoryjobnum:
                        catagoryjobnum[line['catagory']] = line['num']
                    else:
                        catagoryjobnum[line['catagory']] += line['num']
                    #统计个城市岗位数
                    if (city not in citys):
                        citys[city] = line['num']
                    else:
                        citys[city] += line['num']
            # print(line)
    threshold = int(sum(industryjobnum.values()) * 0.01)
    temp = {key: value for key, value in industryjobnum.items() if value < threshold}
    industryjobnum = {key: value for key, value in industryjobnum.items() if value >= threshold}
    scaledict = dict(sorted(scaledict.items(), key=lambda d: d[0], reverse=False))
    if '其他' not in industryjobnum:
        industryjobnum['其他'] = sum(temp.values())
    else:
        industryjobnum['其他'] += sum(temp.values())

class drawPie():
    def show(self, data, title, theme=ThemeType.WHITE, center=["50%", "40%"]):
        pie = (
            Pie(init_opts=opts.InitOpts(theme=theme))
                .add(title, [list(z) for z in zip(data.keys(), data.values())], center=center, radius=["20%", "35%"])
                .set_global_opts(title_opts=opts.TitleOpts(title=title),
                                 legend_opts=opts.LegendOpts(orient="vertical", pos_top="15%", pos_left="2%"))
                .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {d}"))
        )
        pie.render(title + '.html')


class drawBar():
    def show(self, data, title, theme=ThemeType.WHITE):
        bar = (
            Bar(init_opts=opts.InitOpts(theme=theme))
            .add_xaxis(list(data.keys()))
            .add_yaxis(title, list(data.values()))
                .set_global_opts(title_opts=opts.TitleOpts(title=title))
            .render(title + '.html')
        )

class drawMap():
    def show(self, data, maptype='china', title='China-Map'):
        map = (
            Map()
                .add(series_name="岗位数", data_pair=list(data.items()), maptype="china", zoom=1, center=[105, 38])
                .set_global_opts(
                title_opts=opts.TitleOpts(title=title),
                visualmap_opts=opts.VisualMapOpts(max_=9999, is_piecewise=True,
                                                  pieces=[{"max": 9, "min": 0, "label": "0-9", "color": "#FFE4E1"},
                                                          {"max": 99, "min": 10, "label": "10-99", "color": "#FF7F50"},
                                                          {"max": 499, "min": 100, "label": "100-499",
                                                           "color": "#F08080"},
                                                          {"max": 999, "min": 500, "label": "500-999",
                                                           "color": "#CD5C5C"},
                                                          {"max": 9999, "min": 1000, "label": ">=1000",
                                                           "color": "#8B0000"}]
                                                  )
            )
        )
        map.render(title + '.html')

def draw():
    opencsv()
    drawproperties = drawPie()
    drawproperties.show(propertiesjobnum, '企业类型占比统计')
    drawindustry = drawPie()
    drawindustry.show(industryjobnum, '企业从事行业比例统计', center=['65%', '60%'])
    drawscale = drawBar()
    drawscale.show(scaledict, '企业规模统计', ThemeType.LIGHT)
    drawcatagory = drawBar()
    drawcatagory.show(catagoryjobnum, '各岗位需求统计')
    map = drawMap()
    map.show(data=citys, title='全国各城市就业岗位统计')


if __name__ == '__main__':
    opencsv()
    drawproperties = drawPie()
    drawproperties.show(propertiesjobnum, '企业类型占比统计')
    drawindustry = drawPie()
    drawindustry.show(industryjobnum, '企业从事行业比例统计', center=['65%', '60%'])
    drawscale= drawBar()
    drawscale.show(scaledict, '企业规模统计', ThemeType.LIGHT)
    drawcatagory = drawBar()
    drawcatagory.show(catagoryjobnum, '各岗位需求统计')
    map = drawMap()
    map.show(data=citys, title='全国各城市就业岗位统计')
```

## 参考文献

[《cookbook》12.5 防止死锁的加锁机制](https://python3-cookbook.readthedocs.io/zh_CN/latest/c12/p05_locking_with_deadlock_avoidance.html#id1)
