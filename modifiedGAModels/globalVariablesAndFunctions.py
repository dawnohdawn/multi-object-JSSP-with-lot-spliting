import numpy as np
import random
import copy
import pandas as pd
import heapq
import os
import gc
import time
import matplotlib
import matplotlib.pyplot as plt
PATH = os.path.abspath('.')


# 全局变量


problemInd = 2

""" 
problemInd               问题编号，需要手动指定
timeMatrix               每种lot的每个工序由不同的机器加工需要多少时间
preparingTimeMatrix      工序准备时间
lotNum                   有多少个lot
machineMatrix            每种lot的每个工序都可以由哪几台机器加工
lotOpeartionNumList      list，每种lot各有多少个工序
machineNum               有多少台机器
operationNumOfMachine    每台机器可以加工多少个不同的工序
"""

# P1：4X6问题，来自王海燕
if (problemInd == 1):
    timeMatrix = [[{0: 2, 1: 3, 2: 4}, {1: 3, 3: 2, 4: 4}, {0: 1, 1: 4, 2: 5}], \
                  [{0: 3, 2: 5, 4: 2}, {0: 4, 1: 3, 4: 6}, {2: 4, 4: 7, 5: 11}], \
                  [{0: 5, 1: 6}, {1: 4, 3: 3, 4: 5}, {2: 13, 4: 9, 5: 12}], \
                  [{0: 9, 2: 7, 3: 9}, {1: 6, 3: 4, 5: 5}, {0: 1, 2: 3, 5: 3}]]

    preparingTimeMatrix = [[{0: 2, 1: 3, 2: 4}, {1: 3, 3: 2, 4: 4}, {0: 1, 1: 4, 2: 5}], \
                           [{0: 3, 2: 5, 4: 2}, {0: 4, 1: 3, 4: 6}, {2: 4, 4: 7, 5: 11}], \
                           [{0: 5, 1: 6}, {1: 4, 3: 3, 4: 5}, {2: 13, 4: 9, 5: 12}], \
                           [{0: 9, 2: 7, 3: 9}, {1: 6, 3: 4, 5: 5}, {0: 1, 2: 3, 5: 3}]]

    lotSizes = [8, 8, 8, 8]

# P2：4X6问题，来自王海燕
elif (problemInd == 2):
    timeMatrix = [[{0: 2, 1: 3, 2: 4}, {1: 3, 3: 2, 4: 4}, {0: 1, 1: 2, 2: 5}], \
                  [{0: 3, 2: 5, 4: 2}, {0: 4, 1: 3, 4: 6}, {2: 4, 4: 7, 5: 11}], \
                  [{0: 5, 1: 6}, {1: 4, 3: 3, 4: 5}, {2: 13, 4: 9, 5: 12}], \
                  [{0: 9, 2: 7, 3: 9}, {1: 6, 3: 4, 5: 5}, {0: 1, 2: 3, 5: 3}]]

    preparingTimeMatrix = [[{0: 2, 1: 3, 2: 4}, {1: 3, 3: 2, 4: 4}, {0: 1, 1: 2, 2: 5}], \
                           [{0: 3, 2: 5, 4: 2}, {0: 4, 1: 3, 4: 6}, {2: 4, 4: 7, 5: 11}], \
                           [{0: 5, 1: 6}, {1: 4, 3: 3, 4: 5}, {2: 13, 4: 9, 5: 12}], \
                           [{0: 9, 2: 7, 3: 9}, {1: 6, 3: 4, 5: 5}, {0: 1, 2: 3, 5: 3}]]

    lotSizes = [20, 20, 20, 20]

# P3：6X6问题，来自王海燕
elif (problemInd == 3):
    timeMatrix = [[{0: 2}, {2: 3, 3: 2}, {1: 2, 3: 2, 4: 3, 5: 2}, {1: 5, 3: 6}, {2: 2, 5: 2}, {1: 1, 4: 1}], \
                  [{1: 2, 3: 1}, {2: 4}, {0: 8, 4: 7, 5: 7}, {1: 4, 2: 5, 3: 5}, {2: 1, 5: 1}, {1: 4, 4: 5}], \
                  [{0: 4, 2: 5}, {1: 5, 3: 5}, {2: 1, 4: 1}, {1: 6, 4: 7}, {1: 2, 2: 2, 5: 3}], \
                  [{0: 4, 3: 4}, {2: 2}, {1: 4, 3: 3, 5: 3}, {2: 6, 4: 5}, {0: 6}, {1: 3, 3: 2, 4: 2}], \
                  [{0: 2, 3: 3}, {1: 5, 4: 4}, {2: 1, 3: 1}, {2: 3, 5: 2}, {1: 3, 2: 2}, {4: 2}], \
                  [{0: 2, 2: 3, 4: 2}, {1: 4, 4: 3}, {3: 6, 5: 6}, {1: 2, 3: 2}, {2: 1}, {0: 2, 3: 3, 4: 2}]]

    preparingTimeMatrix = [[{0: 1}, {2: 2, 3: 1}, {1: 1, 3: 2, 4: 2, 5: 1}, {1: 3, 3: 2}, {2: 1, 5: 1}, {1: 1, 4: 1}], \
                           [{1: 1, 3: 1}, {2: 2}, {0: 2, 4: 2, 5: 3}, {1: 2, 2: 1, 3: 2}, {2: 1, 5: 1}, {1: 2, 4: 1}], \
                           [{0: 2, 2: 2}, {1: 3, 3: 2}, {2: 1, 4: 1}, {1: 3, 4: 2}, {1: 2, 2: 1, 5: 1}], \
                           [{0: 2, 3: 1}, {2: 1}, {1: 1, 3: 1, 5: 1}, {2: 2, 4: 2}, {0: 1}, {1: 1, 3: 2, 4: 1}], \
                           [{0: 1, 3: 1}, {1: 1, 4: 1}, {2: 1, 3: 1}, {2: 1, 5: 1}, {1: 1, 2: 2}, {4: 2}], \
                           [{0: 1, 2: 1, 4: 2}, {1: 1, 4: 2}, {3: 2, 5: 1}, {1: 1, 3: 1}, {2: 2}, {0: 2, 3: 1, 4: 2}]]
    lotSizes = [10, 10, 10, 10, 10, 10]

# P4：6X6问题，来自王海燕
elif (problemInd == 4):
    timeMatrix = [[{0: 2}, {2: 3, 3: 2}, {1: 2, 3: 2, 4: 3, 5: 2}, {1: 5, 3: 6}, {2: 2, 5: 2}, {1: 1, 4: 1}], \
                  [{1: 2, 3: 1}, {2: 4}, {0: 8, 4: 7, 5: 7}, {1: 4, 2: 5, 3: 5}, {2: 1, 5: 1}, {1: 4, 4: 5}], \
                  [{0: 4, 2: 5}, {1: 5, 3: 5}, {2: 1, 4: 1}, {1: 6, 4: 7}, {1: 2, 2: 2, 5: 3}], \
                  [{0: 4, 3: 4}, {2: 2}, {1: 4, 3: 3, 5: 3}, {2: 6, 4: 5}, {0: 6}, {1: 3, 3: 2, 4: 2}], \
                  [{0: 2, 3: 3}, {1: 4, 4: 4}, {2: 1, 3: 1}, {2: 3, 5: 2}, {1: 3, 2: 2}, {4: 2}], \
                  [{0: 2, 2: 3, 4: 2}, {1: 4, 4: 3}, {3: 6, 5: 6}, {1: 2, 3: 2}, {2: 1}, {0: 2, 3: 3, 4: 2}]]

    preparingTimeMatrix = [[{0: 1}, {2: 2, 3: 1}, {1: 1, 3: 2, 4: 2, 5: 1}, {1: 3, 3: 2}, {2: 1, 5: 1}, {1: 1, 4: 1}], \
                           [{1: 1, 3: 1}, {2: 2}, {0: 2, 4: 2, 5: 3}, {1: 2, 2: 1, 3: 2}, {2: 1, 5: 1}, {1: 2, 4: 1}], \
                           [{0: 2, 2: 2}, {1: 3, 3: 2}, {2: 1, 4: 1}, {1: 3, 4: 2}, {1: 2, 2: 1, 5: 1}], \
                           [{0: 2, 3: 1}, {2: 1}, {1: 1, 3: 1, 5: 1}, {2: 2, 4: 2}, {0: 1}, {1: 1, 3: 2, 4: 1}], \
                           [{0: 1, 3: 1}, {1: 1, 4: 1}, {2: 1, 3: 1}, {2: 1, 5: 1}, {1: 1, 2: 2}, {4: 2}], \
                           [{0: 1, 2: 1, 4: 2}, {1: 1, 4: 2}, {3: 2, 5: 1}, {1: 1, 3: 1}, {2: 2}, {0: 2, 3: 1, 4: 2}]]
    lotSizes = [20, 20, 20, 20, 20, 20]

# P5：5X12问题，来自ZHAO
elif (problemInd == 5):
    timeMatrix = [[{5: 5, 6: 7, 7: 8}, {4: 10}, {3: 2}, {4: 5}, {10: 12, 11: 14}], \
                  [{5: 5, 6: 9, 7: 6}, {8: 3, 9: 4}, {1: 4, 2: 4}, {1: 15, 2: 7}, {1: 5, 2: 5}, {10: 10, 11: 8}], \
                  [{5: 5, 6: 7, 7: 8}, {5: 6, 6: 6, 7: 10}, {8: 4, 9: 5}, {1: 15, 2: 14}, {1: 5, 2: 3},
                   {10: 10, 11: 11}], \
                  [{4: 6}, {0: 4}, {8: 3, 9: 5}, {4: 5}, {10: 6, 11: 9}], \
                  [{5: 5, 6: 6, 7: 6}, {5: 5, 6: 5, 7: 6}, {8: 5, 9: 5}, {3: 6}, {1: 9, 2: 10}, {1: 5, 2: 4},
                   {10: 9, 11: 10}]]

    preparingTimeMatrix = [[{5: 5, 6: 5, 7: 5}, {4: 2}, {3: 4}, {4: 2}, {10: 0, 11: 0}], \
                           [{5: 5, 6: 4, 7: 7}, {8: 0, 9: 0}, {1: 8, 2: 3}, {1: 4, 2: 7}, {1: 3, 2: 3}, {10: 0, 11: 0}], \
                           [{5: 4, 6: 6, 7: 6}, {5: 6, 6: 8, 7: 6}, {8: 0, 9: 0}, {1: 5, 2: 3}, {1: 3, 2: 1},
                            {10: 0, 11: 0}], \
                           [{4: 2}, {0: 2}, {8: 0, 9: 0}, {4: 3}, {10: 0, 11: 0}], \
                           [{5: 4, 6: 4, 7: 5}, {5: 6, 6: 6, 7: 6}, {8: 0, 9: 0}, {3: 4}, {1: 2, 2: 4}, {1: 2, 2: 2},
                            {10: 0, 11: 0}]]
    lotSizes = [600, 500, 1800, 2000, 500]

# 由上面两个矩阵计算得到一些全局变量

lotNum = len(timeMatrix)

machineMatrix = [[[item for item in operation.keys()] for operation in lot] for lot in timeMatrix]

lotOpeartionNumList = [len(item) for item in timeMatrix]

temp1 = []
temp2 = []
operationNumOfMachine = []
for i, item in enumerate(timeMatrix):
    temp1.extend(item * lotSizes[i])
for i, item in enumerate(temp1):
    temp1[i] = list(item.keys())
for item in temp1:
    temp2.extend(item)

machineNum = len(set(temp2))

for i in range(machineNum):
    operationNumOfMachine.append(temp2.count(i))

# # 打印上述所有参数
# print('timeMatrix: ')
# for item in timeMatrix:
#     print(item)
# print('preparingTimeMatrix: ')
# for item in preparingTimeMatrix:
#     print(item)
# print('lotSizes: ', lotSizes)
# print('lotNum: ', lotNum)
# print('machineMatrix: ')
# for item in machineMatrix:
#     print(item)
# print('lotOpeartionNumList: ', lotOpeartionNumList)
# print('machineNum: ', machineNum)
# print('operationNumOfMachine: ', operationNumOfMachine)



# 一些全局函数

def chooseARandomNumberExceptThis(minNum, maxNum, num):
    """
    功能：
    随机取除了num以外的0~N的整数

    输入：
    N       0~N为范围
    num     不能取的那个数

    输出：
    一个随机数
    """
    if minNum == maxNum:
        return minNum

    chosenNum = random.randint(minNum, maxNum)
    while chosenNum == num:
        chosenNum = random.randint(minNum, maxNum)

    return chosenNum


def chooseTwoNumByRandom(N):
    """
    功能：         随机选择两个不重复的[0,N]的随机整数

    输出：
    pos1, pos2     两个随机整数
    """
    pos1 = random.randint(0, N)
    pos2 = random.randint(0, N)
    while pos1 == pos2:
        pos2 = random.randint(0, N)

    return pos1, pos2


def chooseOneNumByTournament(makespanList, N):
    """
    功能：          用锦标赛法选择一个个体，即从随机N个体中选出最好的一个个体

    输入：
    makespanList    输入一个完工时间的list
    N               随机个体的个数，一般为3

    输出：
    chosenIndex     被选中的个体的序号，范围为[0,len(makespanList)-1]
    """
    competitorsIndexs = [random.randint(0, len(makespanList) - 1) for i in range(N)]
    competitorsMakespans = [makespanList[item] for item in competitorsIndexs]

    return competitorsIndexs[competitorsMakespans.index(min(competitorsMakespans))]


def chooseTwoNumByTournament(makespanList, N):
    """
    功能：          用锦标赛法选出两个不同的个体

    输入：
    makespanList    输入一个完工时间的list
    N               随机个体的个数，一般为3

    输出：
    chosenIndexs     被选中的两个个体的序号，范围为[0,len(makespanList)-1]
    """
    pos1 = chooseOneNumByTournament(makespanList, N)
    pos2 = chooseOneNumByTournament(makespanList, N)
    while pos1 == pos2:
        pos2 = chooseOneNumByTournament(makespanList, N)

    return pos1, pos2


def calRoulette(makespanList):
    """
    版本信息：     ver2
                  该版本不会改变传入makespanList的值

    功能：        由完工时间列表先计算fitness，再计算轮盘

    输入：
    makespanList  输入一个完工时间的list

    输出：
    roulette      输出一个轮盘概率list
    """
    makespanMax = max(makespanList)
    fitnessList = []
    for i in range(len(makespanList)):
        fitnessList.append(makespanMax - makespanList[i] + 1)
    fitnessSum = sum(fitnessList)
    for i in range(len(fitnessList)):
        fitnessList[i] /= fitnessSum
    roulette = []
    temp = 0
    for i in range(len(fitnessList)):
        temp += fitnessList[i]
        roulette.append(temp)
    return roulette


def calRoulette_old(makespanList):
    """
    版本信息：     ver1
                  发现该函数会改变传入makespanList的值，所以写了第二版

    功能：        由完工时间列表先计算fitness，再计算轮盘

    输入：
    makespanList  输入一个完工时间的list

    输出：
    roulette      输出一个轮盘概率list
    """
    makespanMax = max(makespanList)
    for i in range(len(makespanList)):
        makespanList[i] = makespanMax - makespanList[i] + 1
    makespanSum = sum(makespanList)
    for i in range(len(makespanList)):
        makespanList[i] /= makespanSum
    roulette = []
    temp = 0
    for i in range(len(makespanList)):
        temp += makespanList[i]
        roulette.append(temp)
    return roulette


def calRouletteWithRank(makespanList, Nmin):
    """
    功能：         计算基于排序的轮盘 Linear Ranking Selection

    输入：
    makespanList  输入一个完工时间的list
    Nmin          最差个体在种群中出现次数的期望值，Nmax=2-Nmin
                  根据'Gradual distributed real-coded genetic algorithms'，Nmin越小，seletive pressure越大，给较优个体的机会越多

    输出：
    roulette      输出一个轮盘概率list
    """
    rankList = pd.Series(makespanList)
    rankList = list(rankList.rank(method='average'))

    Nmax = 2 - Nmin
    pList = [(Nmax - (Nmax - Nmin) * (item - 1) / (len(rankList) - 1)) / len(rankList) for item in rankList]

    roulette = []
    temp = 0
    for i in range(len(pList)):
        temp += pList[i]
        roulette.append(temp)

    return roulette


def chooseOneNumByRoulette(roulette):
    """
    用轮盘来随机选取一个数
    roulette      输入一个轮盘概率list
    i             输出一个[0,len(roulette)-1]的随机数
    """
    randNum = random.random()
    for i in range(len(roulette)):
        if (randNum < roulette[i]):
            break
    return i


def chooseTwoNumByRoulette(roulette):
    """
    用轮盘赌来随机选取两个不同的数
    roulette      输入一个轮盘概率list
    pos1, pos2    输出两个不同的[0,len(roulette)-1]的随机数
    """
    pos1 = chooseOneNumByRoulette(roulette)
    pos2 = chooseOneNumByRoulette(roulette)
    while (pos1 == pos2):
        pos2 = chooseOneNumByRoulette(roulette)
    return pos1, pos2


def getBestOrWorstIndexs(mode, makespanList, indNum):
    """
    功能：         找出给定makespanList中最好或者最坏的indNum个个体

    输入：
    mode           选择模式，可以是'best','worst'
    makespanList   list，给定完工时间列表
    indNum         要选出多少个

    输出：
    indexs         一个list，里面是individual在pop中的序号
    """

    indexs = []
    temp = copy.deepcopy(makespanList)

    if mode == 'best':
        Inf = 99999999
        for i in range(indNum):
            indexs.append(temp.index(min(temp)))
            temp[temp.index(min(temp))] = Inf
    elif mode == 'worst':
        Inf = 0
        for i in range(indNum):
            indexs.append(temp.index(max(temp)))
            temp[temp.index(max(temp))] = Inf

    return indexs



def drawGantChart(fromFilename = 'gantData.csv', toFilename = 'gantFig.png'):
    """
    使用甘特图时间表绘制甘特图
    fromFilename  时间表csv文件名
    toFilename    甘特图文件名
    如果想改变颜色，颜色名参考：https://matplotlib.org/users/colors.html
    """
    plt.rcParams['font.sans-serif']=['SimHei'] # 用来正常显示中文标签
    plt.rcParams['axes.unicode_minus']=False # 用来正常显示负号

    height=16 # 柱体高度，设为2的整数倍，方便Y轴label居中，如果设的过大，柱体间的间距就看不到了，需要修改下面间隔为更大的值
    interval=4 # 柱体间的间隔
    # colors = ("turquoise","crimson","black","red","yellow","green","brown","blue") # 颜色，不够再加
    colors = ("wheat","tan","lavender","lightblue","silver","pink") # 颜色，不够再加
    # colors = ("ivory","ivory","ivory","ivory","ivory","ivory") # 颜色，不够再加
    x_label=u"调度时刻" # 设置x轴label

    # df = pd.read_csv(io.StringIO(data), header=None, names=["Machine", "Start", "Finish","Title"] )
    df = pd.read_csv(PATH+"\\"+fromFilename, header=None, names=["Machine", "Start", "Finish","Title"])
    df["Diff"] = df.Finish - df.Start
    fig,ax=plt.subplots(figsize=(30,10))
    labels=[]
    count=0;
    for i,machine in enumerate(df.groupby("Machine")):
        labels.append(machine[0])
        data=machine[1]
        for index,row in data.iterrows():
    #         ax.broken_barh([(row["Start"],row["Diff"])], ((height+interval)*i+interval,height), facecolors=colors[i], edgecolor='brown')
    #         ax.broken_barh([(row["Start"],row["Diff"])], ((height+interval)*i+interval,height), facecolors='ivory', edgecolor='brown')
            if(row["Title"] == '*'):
                ax.broken_barh([(row["Start"],row["Diff"])], ((height+interval)*i+interval,height), facecolors='navy', edgecolor='brown')
            else:
#                 ax.broken_barh([(row["Start"],row["Diff"])], ((height+interval)*i+interval,height), facecolors=colors[int(row['Title'][0])], edgecolor='brown')
                ax.broken_barh([(row["Start"],row["Diff"])], ((height+interval)*i+interval,height), facecolors=colors[int(row['Title'].split('-')[0])], edgecolor='brown')  # 使显示的lot号、sublot号、机器号都能适用于一位数以上的
#             plt.text(row["Start"], (height+interval)*(i+1),row['Title'],fontsize=10)  # fontsize='x-small'
            plt.text(row["Start"], (height+interval)*(i+1)-height/2,row['Title'],fontsize=10)  # fontsize='x-small'
            if(row["Finish"] > count):
                count = row["Finish"]
    ax.set_ylim(0, (height+interval)*len(labels)+interval)
    ax.set_xlim(0, count+2)
    ax.set_xlabel(x_label)
    ax.set_yticks(range(int(interval+height/2),(height+interval)*len(labels),(height+interval)))
    ax.set_yticklabels(labels)
    # ax.grid(True) # 显示网格
    ax.xaxis.grid(True) # 只显示x轴网格
    # ax.yaxis.grid(True) # 只显示y轴网格
    plt.savefig(PATH+"\\"+toFilename,dpi=160)
    # plt.show()