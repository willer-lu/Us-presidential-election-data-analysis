import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import numpy as np


#读取文件
candidates = pd.read_csv("weball20.txt", sep = '|')
ccl = pd.read_csv("ccl.txt", sep = '|')
itcont = pd.read_csv('itcont_2020_20200722_20200820.txt', sep='|',low_memory=False)# 避免类型歧义

#将两个表合并  会合并相同的列
ccl = pd.merge(ccl, candidates)
#提取出所需要的列  捐赠识别号 候选人ID 候选人姓名
ccl = pd.DataFrame(ccl, columns=['CMTE_ID','CAND_ID', 'CAND_NAME'])

c_itcont = pd.merge(ccl,itcont)
# 提取需要的数据列 候选人姓名 捐款人姓名 捐款人所在州  捐款日期 捐款数额
c_itcont = pd.DataFrame(c_itcont, columns=[ 'CAND_NAME','NAME', 'STATE','TRANSACTION_AMT', 'TRANSACTION_DT'])

c_itcont['CAND_NAME'].fillna(method='ffill',inplace=True)#缺失数据处理,用前一个非缺失值填充
c_itcont['STATE'].fillna(method='ffill',inplace=True)
c_itcont['NAME'].fillna(method='ffill',inplace=True)
c_itcont['TRANSACTION_AMT'].fillna(method='ffill',inplace=True)
c_itcont['TRANSACTION_DT'].fillna(method='ffill',inplace=True)

TotalDonation = c_itcont.groupby('STATE')  #按州分组
STATE = []
for state,value in TotalDonation:
    STATE.append(state)
# 获取每个州获捐款的总额  其中DT列无意义
TotalDonation = c_itcont.groupby('STATE').sum()   # 分组后的州是有序的
TotalDonation['STATE'] = STATE                    # 添加STATE这一列 使其适应绘图函数
fig = px.choropleth(TotalDonation, locations='STATE', color="TRANSACTION_AMT",range_color=(0, 21000000),#设置颜色
                    locationmode = 'USA-states',
                    scope="usa",                # 美国地图
                    title='USA Presidential Votes Counts')
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})   # 更新轨迹的可见性
fig.show()


# 计算每个总统候选人所获得的捐款总额，并排序
sort = c_itcont.groupby("CAND_NAME").sum().sort_values("TRANSACTION_AMT",ascending=False)
name3 = list(sort.index[0:3])  # 取前三位


# 将Date列修改为字符串型 修改日期格式  提取出月份与日期
c_itcont['TRANSACTION_DT'] = c_itcont['TRANSACTION_DT'] .astype(str)
c_itcont['TRANSACTION_DT'] = [i[0]+'-'+i[1:3] for i in c_itcont['TRANSACTION_DT'] ]
# 获取日期列表作为X轴
x = list(c_itcont[c_itcont['CAND_NAME'] == name3[0]].groupby("TRANSACTION_DT")['TRANSACTION_AMT'].sum().index)

money = [[],[],[]]
# 获得每日单独的捐款金额 并求每日的累积
for i in range(3):
    money[i] = list(c_itcont[c_itcont['CAND_NAME'] == name3[i]].groupby("TRANSACTION_DT")['TRANSACTION_AMT'].sum())
    money[i] = list(np.array(money[i]).cumsum(axis=0))

# 绘制折线图
fig = plt.figure(figsize=(16, 8), dpi=100)
plt.xticks(rotation=40)
plt.xlabel('date')
plt.ylabel('money')
plt.plot(x, money[0], marker='o', label='BIDEN, JOSEPH R JR', color='blue')
plt.plot(x, money[1], marker='o', label='TRUMP, DONALD J.', color='green')
plt.plot(x, money[2], marker='o', label='SULLIVAN, DAN', color='red')
plt.legend(loc='upper left')
plt.grid(alpha=0.1)
plt.title('Trends in donations for the top three candidates')
plt.show()

# 选出根据上问获得捐款额最多的候选人
MAXpeople = c_itcont[c_itcont['CAND_NAME']=='BIDEN, JOSEPH R JR']
# 将所有捐赠者姓名连接成一个字符串
data = ' '.join(MAXpeople["NAME"].tolist())
# 生成词云图
wc = WordCloud(
     background_color="white",  # 设置背景为白色
     width=1920,  # 设置图片的宽度
     height=1080,  # 设置图片的高度
     margin=10,  # 设置图片的边缘
     max_font_size=120,# 显示的最大的字体大小
     random_state=20,  # 为每个单词返回一个PIL颜色
 ).generate_from_text(data)
plt.imshow(wc.recolor()) #绘图
# 去掉坐标轴
plt.axis("off")
plt.show()  #展示