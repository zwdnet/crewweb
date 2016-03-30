# -*- coding:utf-8 -*-

import re
import urllib.request
import urllib
import matplotlib.pyplot as plt
import numpy as np
import jieba
import time

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

while queue and cnt < maxCount:
    url = queue.popleft()
    visited |= {url}
    print('已经抓取:' + str(cnt) + '  正在抓取 <----  ' + url + "队列链接数" + str(len(queue)))
    cnt += 1

    try:
        req = urllib.request.Request(url)# headers=webheader)
        urlop = urllib.request.urlopen(req, timeout=5)
    except:
        print("抓取%s失败" % url)
        continue

    try:
        data = urlop.read().decode('utf-8')
    except:
        continue

    linkre = re.compile("href=['\"]([^\"'>]*?)['\"].*?")
    urlNum = 0
    for x in linkre.findall(data):
        if 'http' in x and x not in visited and urlNum < maxNum:
            queue.append(x)
            urlNum += 1
    word = re.compile("[\u4e00-\u9fa5]+") #只爬中文
    for s in word.findall(data):
        output.write(s)

    #暂停一段时间，防止服务器负荷过重
    time.sleep(0.01)

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
p1 = plt.plot(x, y)
p2 = plt.plot(x, y1)
plt.show()
