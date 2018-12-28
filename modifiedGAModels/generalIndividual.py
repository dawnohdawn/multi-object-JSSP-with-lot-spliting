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




