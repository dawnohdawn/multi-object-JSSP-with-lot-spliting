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