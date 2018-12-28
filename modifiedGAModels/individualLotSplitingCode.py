import random
import os
from singleLotSplitingVec import singleLotSplitingVec
PATH = os.path.abspath('.')


# 一个个体所有lot的lotSplitingCode
class individualLotSplitingCode:

    def __init__(self, lotNum, lotSizes):
        """
        self.lotNum  一个个体有多少个lot
        self.lotSizes  list，每个lot有多少个工件
        """
        self.lotNum = lotNum
        self.lotSizes = lotSizes


    def initilizeLotSplitingCode(self):
        """
        根据lotSizes初始化lotNum个lotSplitingVec，随机初始化
        self.lotSplitingCode  list，一个个体所有lot的lotSplitingVec组成的list
        """
        self.lotSplitingCode = []
        for num in self.lotSizes:
            self.lotSplitingCode.append(singleLotSplitingVec(num))
        for item in self.lotSplitingCode:
            item.initializeLotSplitingVec()


    def mutateWithinLotWithTwoSublots(self, p):
        """
        按照概率p来随机抽取lot进行lot内两个sublotSize的变异
        p        单个Vec变异的概率
        """
        for item in self.lotSplitingCode:
            if (random.random() < p):
                item.mutateTwoSublot()


    def mutateWithinLotWithNewVec(self, p):
        """
        按照概率p来随机抽取lot进行lot内分批方案vec重新随机初始化
        p       单个Vec变异的概率
        """
        for item in self.lotSplitingCode:
            if (random.random() < p):
                item.initializeLotSplitingVec()
