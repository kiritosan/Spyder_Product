import requests
from bs4 import BeautifulSoup
import pandas as pd
import itertools

categories = ['ballistic-protection','shelters-ballistic-protection','anti-terrorism-eod','anti-ballistic-material','riot-control-gears','swat-duty-gears','military-clothing-boots','military-gear-equipment']
ori_url = "https://www.compassint.cn/{categorie}/page/"

# 输入url 取得response
def fetch(url):
    return requests.get(url)
    
# 传入商品页url purl 获取商品详细信息和tags 然后做成dataframe格式的商品信息扩展表格
def fetch_pdetail(purl):
    print(f'当前商品详情页url为{purl}')
    print('从商品详情页获得描述和标签')
    r = fetch(purl)
    print('抓取purl成功')
    soup = BeautifulSoup(r.content, 'html.parser')
    pdetail = soup.find_all("section", class_='entry detail-panel')[0].get_text()
    tags = soup.find_all("section", class_='entry detail-panel disabled')[0].get_text()
    # ca0 = soup.find_all("a", {'itemprop':'breadcrumb'})[2].get_text()
    # ca1 = soup.find_all("a", {'itemprop':'breadcrumb'})[3].get_text()
    # ca = 'Prouduts' + ' > ' + ca0 + ' > ' + ca1 + ", " + 'Prouduts' + ' > ' + ca0 + ", " + 'Prouduts'
    # ca = 'Prouduts' + ' > ' + ca0 + ", " + 'Prouduts'
    print('抓取描述和标签成功')
    return pdetail, tags

# 输入response 获取商品名 商品图片 商品链接 得到一页商品的商品基础信息
def process(res):
    # 制作存储数据的箱子
    # column = ['ID','类型','SKU','名称','已发布','是推荐产品？','在列表页可见','简短描述','描述','促销开始日期','促销截止日期''税状态','税类','有货？','库存','库存不足','允许缺货下单？','单独出售？','重量(kg)','长度(cm)','宽度 (cm)','高度 (cm)','允许顾客评价？','购物备注','促销价格','常规售价','分类','标签','运费类','图片','下载限制','下载的过期天数','父级','分组产品','交叉销售','交叉销售','外部链接','按钮文本','位置']
    l = []
    # l_tmp = []
    # 想要column = ['名称','图片','描述'，'标签'] 先获取名称图片 和商品页url 再从商品页url里面获取描述和标签
    # column = ['名称','图片','商品页url']
    column = ['名称','图片','描述','标签']
    soup = BeautifulSoup(res.content, 'html.parser')
    product = soup.find_all("div", class_="pd-img")
    # 先做标签然后在贴到相应的商品上面 标签先做出来了 比如第五件商品贴完后 先做出n=6 (第六个商品的标签) 然后在贴到产品上面对应
    # n=1 最后加等1
    for i in product:
        pname = i.find('img').get('alt')
        pimg = i.find('img').get('src')
        purl = i.find('a').get('href')
        # 得到描述和标签
        pdetail, tags = fetch_pdetail(purl)
        l.append([pname,pimg,pdetail,tags])
    return pd.DataFrame(columns = column, data = l)
    
# 创建data仓库
data = []
data = pd.DataFrame(data,columns = ['名称','图片','描述','标签'])
for categorie in categories:
    # 构建不同分类的网址
    url = ori_url.format(categorie = categorie)
    print(f'当前正在抓取{categorie}分类')
    for page in itertools.count(1):
        url0 = url + str(page)
        print(url0)
        res = fetch(url0)
        if res.status_code != 200:
            print('本分类已没有页面,开始抓取下一个分类')
            break
        data0 = process(res)
        print('--------------------该页提取数据完成--------------------')
        data = pd.concat([data, data0], axis=0, ignore_index=True)
        print('-----------------------数据已存储-----------------------')

data.to_csv('Product.csv',index=0,encoding="utf_8_sig")
