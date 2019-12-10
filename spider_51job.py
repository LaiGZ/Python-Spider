
import random
import re,pymongo
import time
import requests
from lxml import etree
#连接数据库
client=pymongo.MongoClient('localhost',27017)
db=client['py_DB']
#计数器
n=1
p=1
#代理UA
def get_ua():
	user_agents = [
		'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36 OPR/26.0.1656.60',
		'Opera/8.0 (Windows NT 5.1; U; en)',
		'Mozilla/5.0 (Windows NT 5.1; U; en; rv:1.8.1) Gecko/20061208 Firefox/2.0.0 Opera 9.50',
		'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; en) Opera 9.50',
		'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:34.0) Gecko/20100101 Firefox/34.0',
		'Mozilla/5.0 (X11; U; Linux x86_64; zh-CN; rv:1.9.2.10) Gecko/20100922 Ubuntu/10.10 (maverick) Firefox/3.6.10',
		'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/534.57.2 (KHTML, like Gecko) Version/5.1.7 Safari/534.57.2 ',
		'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36',
		'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
		'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/534.16 (KHTML, like Gecko) Chrome/10.0.648.133 Safari/534.16',
		'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.101 Safari/537.36',
		'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko',
		'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.11 TaoBrowser/2.0 Safari/536.11',
		'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.71 Safari/537.1 LBBROWSER',
		'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E)',
		'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.84 Safari/535.11 SE 2.X MetaSr 1.0',
		'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SV1; QQDownload 732; .NET4.0C; .NET4.0E; SE 2.X MetaSr 1.0) ',
	]
	user_agent = random.choice(user_agents) #random.choice(),从列表中随机抽取一个对象
	return user_agent
ua=get_ua()
headers = {'User-Agent': ua}

def get_html(url):
    response = requests.get(url, headers=headers)
    data = response.content.decode('gbk')
    html = etree.HTML(data)
    return html

def get_job_list(url):
    html = get_html(url)
    joburl=html.xpath('//*[@class="el"]/p/span/a/@href')
    for url in joburl:
        get_job_info(url)

def clearData(data):
    if '月' in data:
        if '万' in data:
            data=data.split('万')[0]
            low = int(float(data.split('-')[0]) * 10000)
            hight = int(float(data.split('-')[1]) * 10000)
            avg = int((low + hight) / 2)
            return [low,hight,avg]


        if '千' in data:
            data=data.split('千')[0]
            low=int(float(data.split('-')[0])*1000)
            hight = int(float(data.split('-')[1])*1000)
            avg=int((low+hight)/2)
            return [low,hight,avg]
    if '年' in data:
        if '万' in data:
            data = data.split('万')[0]
            low = int(float(data.split('-')[0]) * 10000/12)
            hight = int(float(data.split('-')[1]) * 10000/12)
            avg = int((low + hight) / 2)
            return [low,hight,avg]

def get_job_info(url):
    response = requests.get(url, headers=headers)
    print(response.url)
    try:
        data = response.content.decode('gbk')
        html = etree.HTML(data)
    except:
        return
    job_info={}
    try:
        text = html.xpath('//*[@class="research"]/p/text()')[0]
    except:
        text=''

    if '很抱歉' in text:
        print('很抱歉')
        return
    else:
        try:
            #职位ID
            job_info['jobId']=re.search(r'\d{8,9}',url).group(0)
            #标题
            job_info['title']=html.xpath('//h1/text()')[0]
            info=html.xpath('//*[@class="msg ltype"]/text()')
            #工资
            pay=html.xpath('//*[@class="cn"]/strong/text()')[0]
            pay=clearData(pay)
            job_info['lowpay']=pay[0]
            job_info['hightpay']=pay[1]
            job_info['avgpay']=pay[2]
            if len(info)==4:
                #工作地点
                job_info['area']=info[0].replace('\xa0','')
                #经验要求
                job_info['experience']=info[1].replace('\xa0','')
                #学历要求
                job_info['education']=info[2].replace('\xa0','')
                #发布时间
                job_info['releaseTime']=info[3].replace('\xa0','').split('发')[0]
            else:
                # 工作地点
                area= info[0].replace('\xa0', '')
                if '-' in area:
                    area=area.split('-')[0]
                job_info['area'] = area
                # 经验要求
                job_info['experience'] = info[1].replace('\xa0', '')
                # 学历要求
                job_info['education'] = info[2].replace('\xa0', '')
                # 发布时间
                job_info['releaseTime'] = info[4].replace('\xa0', '').split('发')[0]
            #公司名字
            job_info['company']=html.xpath('//*[@class="cname"]/a[1]/text()')[0]
            #公司url
            job_info['company_url'] = html.xpath('//*[@class="cname"]/a[1]/@href')[0]
            #公司福利
            welfare=html.xpath('//*[@class="jtag"]/div/span/text()')
            job_info['tag']=(',').join(welfare)
            #职位信息
            jobinfo=html.xpath('//*[@class="bmsg job_msg inbox"]/p/text()')
            job_info['jobinfo']=''.join(jobinfo)
            #过滤一些数据
            if '人' not in job_info['education']:
                save_job_info(job_info)
                
                
            # save_job_info(job_info)

        except Exception as err:
            print(err)
            return

def save_job_info(job):
    global  n
    try:
        db.job_51.insert(job)
        print('%d条数据插入成功！'%(n))
        n+=1
    except Exception as e:
        print(e)
    pass

def start(keyword):
    global  n
    #获取page数量
    # html=get_html('https://search.51job.com/list/000000,000000,0000,00,9,99,Java%25E5%25BC%2580%25E5%258F%2591,2,1.html')
    # pages=html.xpath('//*[@class="rt"][2]/text()')
    # page=pages[2].encode('utf-8').decode().split('/')[1].strip()
    
    #目的是爬取的是全国的数据，page太多，手动控制爬取页面数，前60页，大概有2300多条数据
    for i in range(1,61):
        url='https://search.51job.com/list/000000,000000,0000,00,9,99,'+keyword+',2,'+str(i)+'.html'
        get_job_list(url)
        print('完成了第%d页'%(i))
        time.sleep(2)



#职位名称
key='python'
start(key)
