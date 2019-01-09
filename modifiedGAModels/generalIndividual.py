import random
import os
from individualLotSplitingCode import individualLotSplitingCode
from individualPreferenceCode import individualPreferenceCode
PATH = os.path.abspath('.')


# 一个完整的个体
class generalIndividual:

    def __init__(self, lotNum, lotSizes, machineNum):
        """
        self.lotNum  有多少个lot
        self.lotSizes  list，每个lot有多少个工件
        self.machineNum  有多少个机器
        """
        self.lotNum = lotNum
        self.lotSizes = lotSizes
        self.machineNum = machineNum


    def initializeIndividual(self):
        """
        随机初始化一个个体的两段编码
        self.segment1  S1,分批段
        self.segment2  S2,偏好段
        self.makespan  该个体的完工时间，初始值为一个很大的数
        """
        self.segment1 = individualLotSplitingCode(self.lotNum, self.lotSizes)
        self.segment1.initilizeLotSplitingCode()
        self.segment2 = individualPreferenceCode(self.machineNum, self.lotNum)
        self.segment2.initilizePreferenceCode()
        self.makespan = 100000

        # 这几个数据在邻域搜索时用到，在decode中更新
        self.lastLotInd = -1
        self.lastSublotInd = -1


    def mutateSegment1WithTwoSublots(self, p):
        """
        按照概率p随机选择lotSplitingVec，对其随机两个sublot的size扰动
        p  单个Vec变异的概率
        """
        self.segment1.mutateWithinLotWithTwoSublots(p)


    def mutateSegment1WithNewVec(self, p):
        """
        按照概率p随机选择lotSplitingVec，对整个向量重新初始化
        p  单个Vec变异的概率
        """
        self.segment1.mutateWithinLotWithNewVec(p)


    def mutateSegment2WithinVecWithSwap(self, p):
        """
        按照概率p随机选择preferenceVec，对Vec内两个位置swap
        p  单个Vec变异的概率
        """
        self.segment2.mutateWithinVecWithSwap(p)


    def mutateSgment2BetweenTwoVecs(self):
        """
        随机选两个preferenceVec进行swap
        """
        self.segment2.mutateBetweenVecsWithSwap()


    def crossoverBetweenSegment1s(indi1, indi2, p):
        """
        按概率p选位，交叉两个individual的segment1的位（以一个lot为一位）
        """
        for i in range(indi1.lotNum):
            if (random.random() < p):
                indi1.segment1.lotSplitingCode[i], indi2.segment1.lotSplitingCode[i] = \
                    indi2.segment1.lotSplitingCode[i], indi1.segment1.lotSplitingCode[i]


    def crossoverBetweenSegment2s(indi1, indi2, p):
        """
        按概率p选位，交叉两个individual的segment2的位（以一台机器为一位）
        """
        for i in range(indi1.machineNum):
            if (random.random() < p):
                indi1.segment2.preferenceCode[i], indi2.segment2.preferenceCode[i] = \
                    indi2.segment2.preferenceCode[i], indi1.segment2.preferenceCode[i]


    def decode(self, solutionClassName):
        """
        计算并返回完工时间
        """
        #         solu = solution(self)
        solu = solutionClassName(self)
        solu.run()
        self.makespan = solu.getMakespan()

        self.lastLotInd, self.lastSublotInd = solu.getLastFinishingSublot()


    def neighourLastSublotResize(self):
        """
        功能：
        减小最晚完工的sublot的size
        具体是，随机选取另一个sublot，把最晚完工的sublot减出来的那部分加上去
        """
        originVec = self.segment1.lotSplitingCode[self.lastLotInd].sublotSizes
        sublotNum = self.segment1.lotSplitingCode[self.lastLotInd].sublotNum

        # 至少有两个sublot而且该sublot的siez要大于1才能做以下变化
        if sublotNum > 1 and originVec[self.lastSublotInd] > 1:
            # 该减少多少size
            reduceValue = random.randint(1, originVec[self.lastSublotInd] - 1)

            # 随机选取另一个sublot
            anotherSublotInd = chooseARandomNumberExceptThis(0, sublotNum - 1, self.lastSublotInd)

            # 改变两个sublot的size
            self.segment1.lotSplitingCode[self.lastLotInd].sublotSizes[self.lastSublotInd] -= reduceValue
            self.segment1.lotSplitingCode[self.lastLotInd].sublotSizes[anotherSublotInd] += reduceValue


    def neighbourLastLotPreferenceAdvance(self):
        """
        功能：
        最晚完工的lot在随意一个机器上的优先度提前1
        """
        chosenMachineInd = random.randint(0, self.machineNum - 1)
        self.segment2.insertAJobInsideAVecEarlierOrLaterFewPos(chosenMachineInd, self.lastLotInd, 1)


    def neighbourResizeTwoSublot(self):
        """
        功能：
        随机选取一个lot，重新配置其中两个sublot的size
        """
        chosenLotInd = random.randint(0, self.lotNum - 1)
        self.segment1.lotSplitingCode[chosenLotInd].mutateTwoSublot()
        # print(chosenLotInd)


    def neighbourRepositionALot(self):
        chosenMachineInd = random.randint(0, self.machineNum - 1)
        chosenLotInd = random.randint(0, self.lotNum - 1)
        originalVec = self.segment2.preferenceCode[chosenMachineInd]
        originalPos = originalVec.index(chosenLotInd)
        newPos = chooseARandomNumberExceptThis(0, self.lotNum - 1, originalPos)

        self.segment2.insertAJobIntoAPosInsideAVec(chosenMachineInd, chosenLotInd, newPos)
        # print(chosenMachineInd)
        # print(chosenLotInd)
        # print(newPos)



from generalSolution import generalSolution
from globalVariablesAndFunctions import *


test = generalIndividual(lotNum, lotSizes, machineNum)
test.initializeIndividual()
print(test.segment2.preferenceCode)
for item in test.segment1.lotSplitingCode:
    print(item.sublotSizes)
test.decode(generalSolution)
print(test.makespan)
print('--------------')


for i in range(20):
    test.neighourLastSublotResize()
    test.decode(generalSolution)
    print(test.makespan)
print('--------------')

