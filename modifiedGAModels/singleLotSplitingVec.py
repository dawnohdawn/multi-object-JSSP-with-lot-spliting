import numpy as np
import random
import os
PATH = os.path.abspath('.')


# 一个lot的lotSplitingVector
class singleLotSplitingVec:
    """
    类含义：          一个lot的分批情况

    成员变量：
    self.lotSize      本批共有多少个工件
    self.sublotNum    子批数
    self.sublotSizes  list，每个子批包含多少个工件
    """

    def __init__(self, lotSize):
        """
        输入：
        lotSize     本批共有多少个工件
        """
        self.lotSize = lotSize


    def initializeLotSplitingVec(self):
        """
        功能：     随机初始化一个批的分批方案向量

        注意：     创建对象后需要使用该函数初始化后才有self.sublotNum和self.sublotSizes成员变量
        """
        # 随机生成子批数量，可限制子批数量，也可以不限制子批数量
        #         self.sublotNum = random.randint(1, int(np.log2(self.lotSize)))
        #         self.sublotNum = random.randint(1, 2 * int(np.sqrt(self.lotSize)))
        #         self.lotNum = random.randint(1, self.lotSize)  #
        if (self.lotSize > 100):
            self.sublotNum = random.randint(1, 2 * int(np.sqrt(100)))  # 超100的就不分那么多sublot了
        # if (self.lotSize > 0):
        #     self.sublotNum = 1  # 超100的就不分那么多sublot了
        else:
            self.sublotNum = random.randint(1, 2 * int(np.sqrt(self.lotSize)))

            # 随机生成每一个子批的批量
        self.sublotSizes = [1] * self.sublotNum
        cnt = self.sublotNum
        while (cnt < self.lotSize):
            self.sublotSizes[random.randint(1, self.sublotNum) - 1] += 1
            cnt += 1


    def mutateTwoSublot(self):
        """
        功能：      lot内变异两个sublot的size，即变异一个分批方案向量
        随机选择两个子批，重新随机生成这两个子批的批量，使之与变异前不同
        """
        if (self.sublotNum > 1):  # 当子批数大于1的时候，才可以发生变异
            # 随机选择两个子批
            pos1 = random.randint(1, self.sublotNum) - 1
            pos2 = random.randint(1, self.sublotNum) - 1
            while (pos1 == pos2):
                pos2 = random.randint(1, self.sublotNum) - 1

            # 重新生成两个子批的批量数
            sumSize = self.sublotSizes[pos1] + self.sublotSizes[pos2]
            if (sumSize > 3):  # 如果选中的是两个1的sublot，或者是一个1一个2的sublot，则不进行变异，如果不是这种情况，才有以下的变异
                newSize1 = random.randint(1, sumSize - 1)
                while (newSize1 == self.sublotSizes[pos1] or newSize1 == self.sublotSizes[pos2]):
                    newSize1 = random.randint(1, sumSize - 1)
                self.sublotSizes[pos1] = newSize1
                self.sublotSizes[pos2] = sumSize - newSize1
