# -*- coding:utf-8 -*-

import re
import urllib.request
import urllib
import matplotlib.pyplot as plt
import numpy as np
import jieba
import time
from bs4 import BeautifulSoup

from collections import deque
from Tools.Scripts.treesync import raw_input


queue = deque()

visited = set()
url = raw_input("输入种子网页:")
maxCount = int(raw_input("输入最大网页数:"))
if maxCount <= 0:
    maxCount = 10
maxNum = 5 #加入队列的连接数，限制为前5个。
queue.append(url)
cnt = 0
output =  open("result.txt", "w+", encoding = "utf-8")
linkCount = len(queue)

headers={'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0',
         'Accept':'	text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
         'Accept-Encoding':'gzip, deflate',
         'Accept-Language':'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
         'Connection':'keep-alive',
         #'Host':url,
         #'Referer':url,
         'X-Requested-With':'XMLHttpRequest'}
bCrew = True

while queue:
    url = queue.popleft()
    visited |= {url}
    print('已经抓取:' + str(cnt) + '  正在抓取 <----  ' + url + "队列链接数" + str(len(queue)))
    cnt += 1

    try:
        req = urllib.request.Request(url)# headers=webheader)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0')
        req.add_header('Accept-Language', 'zh-CN,zh')
        #req.add_header('Referer', url)
        urlop = urllib.request.urlopen(req, timeout=5)
    except:
        print("抓取%s失败" % url)
        continue

    try:
        data = urlop.read().decode('utf-8')
    except:
        continue

    #爬链接，如果已爬到的链接没有超过maxCount并且之前也没超过,则抓取，否则，跳过。
    if bCrew:
        linkre = re.compile("href=['\"]([^\"'>]*?)['\"].*?")
        urlNum = 0
        for x in linkre.findall(data):
            if 'http' in x and x not in visited and urlNum < maxNum:
                queue.append(x)
                urlNum += 1
    if len(queue) > maxCount:
        bCrew = False
    soup = BeautifulSoup(data, "lxml")
    data = soup.get_text()
    word = re.compile("[\u4e00-\u9fa5]+") #只爬中文
    for s in word.findall(data):
        output.write(s)
    #暂停一段时间，防止服务器负荷过重
    #time.sleep(0.01)

print("结束")
output.close()

#处理数据
inputFile = open("result.txt", "r", encoding = "utf-8")
outFile = open("fenci.txt", "w+", encoding = "utf-8")
static = {}
text = inputFile.read()
analy = jieba.cut(text, cut_all=False)
wordlist = []
for s in analy:
    wordlist.append(s+" ")
    static[s] = 0
outFile.writelines(wordlist)
inputFile.close()
outFile.close()

#数据展示
inputFile = open("fenci.txt", "r", encoding="utf-8")
allWords = []
line = inputFile.readline()
while line:
    list = line.split(" ")
    for word in list:
        allWords.append(word)
    line = inputFile.readline()
inputFile.close()
for i in allWords:
    if i in static.keys():
        static[i] += 1
static = sorted(static.items(), key = lambda d:d[1], reverse=True)
print(static)
staResult = []
x = []
n = len(static)
for i in range(0, n):
    x.append(i)
    staResult.append(static[i][1])
print(staResult)
result = open("static.txt", "w+", encoding="utf-8")
result.write(str(static))
result.close()

#数据拟合
y = np.log(staResult)
z = np.polyfit(x, y, 1)
p1 = np.poly1d(z)
y1 = p1(x)

#绘图
p1 = plt.plot(x, y, 'r*')
p2 = plt.plot(x, y1)
plt.show()
