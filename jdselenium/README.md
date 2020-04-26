# jdselenium
### 爬取目标：

***使用scrapy和selenium爬取京东商城指定关键字商品信息***

### 项目准备：

**pycharm**:scrapy, urllib, lxml, selenium,pymongo等第三方库
**mongodb**

### 项目流程：

1、新建项目

2、定义item

3、对接selenium

4、解析爬虫

5、存储结果

6、配置setting文件

7、执行爬虫

#### 1 新建项目（终端CMD输入）

新建一个项目：

```
scrapy startproject jdselenium
```

新建一个spider：

```
cd jdselenium
scrapy genspider jd www.jd.com
```

#### 2 定义item

暂时定义商品名称、价格、评价数、在售商和图片链接地址

##### 初步实现Spider的start_requests()方法。

```
def start_requests(self):
    for keyword in self.settings.get('KEYWORDS'):
        for page in range(1,self.settings.get('MAX_PAGE') + 1):
            url = self.base_url + quote(keyword)
            yield scrapy.Request(url=url,callback=self.parse,meta={'page':page},dont_filter=True)
```

#### 3 scrapy对接selenium
实现一个下载器中间件，在process_request中对接selenium即可
这里需要注意，需要滑动到页面最下面才会加载完每页的60条数据，否则只有前30条数据
翻页直接点击页面最后的页码对应超链接或者跳转到多少页实现

#### 4 解析页面

直接采用xpath解析，先抓大后取小的原则

#### 5 存储结果

通过实现一个Item Pipeline即可

#### 6 配置settings文件

配置settings文件，将项目中使用到的配置项在settings文件中配置
同时激活下载中间件和item pipeline

#### 7 运行爬虫，mongodb数据库查看结果
