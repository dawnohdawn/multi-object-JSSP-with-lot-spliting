import random
import os

PATH = os.path.abspath('.')


# 一个个体所有机器的preferenceCode
class individualPreferenceCode:
    """
    注意：lot号从0开始数
    """

    def __init__(self, machineNum, lotNum):
        """
        self.machineNum  机器数量
        self.lotNum  一个个体有多少个lot
        """
        self.machineNum = machineNum
        self.lotNum = lotNum


    def initilizePreferenceCode(self):
        """
        随机初始化self.machineNum台机器的preferenceCode
        self.preferenceCode list，一个个体所有机器的preferenceVec组成的list
        """
        self.preferenceCode = []
        for i in range(self.machineNum):
            preferenceVec = [item for item in range(self.lotNum)]
            random.shuffle(preferenceVec)
            self.preferenceCode.append(preferenceVec)


    def mutateWithinVecWithSwap(self, p):
        """
        按照概率p选取机器的preferenceVec进行Vec内两点swap
        p  单个Vec变异的概率
        """
        for item in self.preferenceCode:
            if (random.random() < p):
                pos1 = random.randint(1, self.lotNum) - 1
                pos2 = random.randint(1, self.lotNum) - 1
                while (pos1 == pos2):
                    pos2 = random.randint(1, self.lotNum) - 1
                item[pos1], item[pos2] = item[pos2], item[pos1]


    def mutateBetweenVecsWithSwap(self):
        """
        随机抽取两个preferenceVec，swap
        """
        pos1 = random.randint(1, self.machineNum) - 1
        pos2 = random.randint(1, self.machineNum) - 1
        while (pos1 == pos2):
            pos2 = random.randint(1, self.machineNum) - 1
        self.preferenceCode[pos1], self.preferenceCode[pos2] = self.preferenceCode[pos2], self.preferenceCode[pos1]


    def insertAJobIntoAPosInsideAVec(self, vecInd, jobInd, insertPos):
        """
        功能：
        将序号为vecInd的Vec里面，序号为jobInd的工件，插入位置insertPos，可前插可后插

        输入：
        vecInd:      改变哪个机器的vec
        jobInd:      改变哪个job的位置
        insertPos:   插到哪个位置
        """
        self.preferenceCode[vecInd].remove(jobInd)
        self.preferenceCode[vecInd].insert(insertPos, jobInd)


    def insertAJobInsideAVecEarlierOrLaterFewPos(self, vecInd, jobInd, gap):
        """
        功能：
        将序号为vecInd的Vec里面，序号为jobInd的工件，插入比原位置更前earlier的位置

        输入：
        vecInd:      改变哪个机器的vec
        jobInd:      改变哪个job的位置
        gap:         提前或者延后多少，可为正数为提前，负数为延后
        """
        originInd = self.preferenceCode[vecInd].index(jobInd)
        newInd = originInd - gap
        if newInd < 0:
            newInd = 0
        if newInd > self.machineNum:
            newInd = self.machineNum - 1

        self.insertAJobIntoAPosInsideAVec(vecInd, jobInd, newInd)


    def inverseInsideAVec(self, vecInd, lotInd1, lotInd2):
        """
        功能：
        将序号为vecInd的Vec里面，lotInd1到lotInd2之间的所有基因位倒序

        输入：
        vecInd:      改变哪个机器的vec
        lotInd1:     倒序段的起始基因位
        lotInd2:     倒序段的结束基因位

        注意：
        本函数会自动检查lotInd1是否比lotInd2小，如果不是，就调换二者的值
        在调用本函数之前，需要确保lotInd1不等于lotInd2，否则该函数没效果
        """
        # 自动检查lotInd1是否比lotInd2小
        if lotInd1 > lotInd2:
            lotInd1, lotInd2 = lotInd2, lotInd1
        # lotInd1不等于lotInd2才会有inverse
        elif lotInd1 != lotInd2:
            self.preferenceCode[vecInd][lotInd1: lotInd2 + 1] = reversed(self.preferenceCode[vecInd][lotInd1: lotInd2 + 1])


    def swapTwoJobsInsideAvec(self, vecInd, lotInd1, lotInd2):
        """
        功能：
        将序号为vecInd的Vec里面，lotInd1和lotInd2两个基因交换

        输入：
        vecInd:      改变哪个机器的vec
        lotInd1:     待交换位置的基因位1
        lotInd2:     待交换位置的基因位2

        注意：
        在调用本函数之前，需要确保lotInd1不等于lotInd2，否则该函数没效果
        """
        # lotInd1不等于lotInd2才会有swap
        if lotInd1 != lotInd2:
            self.preferenceCode[vecInd][lotInd1], self.preferenceCode[vecInd][lotInd2] = \
                self.preferenceCode[vecInd][lotInd2], self.preferenceCode[vecInd][lotInd1]




# test = individualPreferenceCode(5, 10)
# test.initilizePreferenceCode()
# print(test.preferenceCode)
# # test.insertAJobInsideAVecEarlierOrLaterFewPos(0, 3, -1)
# test.inverseInsideAVec(0,2,6)
# # test.swapTwoJobsInsideAvec(0, 0, 9)
# print(test.preferenceCode)