import random
import os
import copy
from individualLotSplitingCode import individualLotSplitingCode
from individualPreferenceCode import individualPreferenceCode
from globalVariablesAndFunctions import *
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
        s1邻域算子
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
        s2邻域算子
        最晚完工的lot在随意一个机器上的优先度提前1
        """
        chosenMachineInd = random.randint(0, self.machineNum - 1)
        self.segment2.insertAJobInsideAVecEarlierOrLaterFewPos(chosenMachineInd, self.lastLotInd, 1)


    def neighbourResizeTwoSublot(self):
        """
        功能：
        s1邻域算子
        随机选取一个lot，重新配置其中两个sublot的size
        """
        chosenLotInd = random.randint(0, self.lotNum - 1)
        self.segment1.lotSplitingCode[chosenLotInd].mutateTwoSublot()
        # print(chosenLotInd)


    def neighbourRepositionALot(self):
        """
        功能：
        s2邻域算子
        随机选取一台机器的一个lot，随机插入到另一个位置
        """
        chosenMachineInd = random.randint(0, self.machineNum - 1)
        chosenLotInd = random.randint(0, self.lotNum - 1)
        originalVec = self.segment2.preferenceCode[chosenMachineInd]
        originalPos = originalVec.index(chosenLotInd)
        newPos = chooseARandomNumberExceptThis(0, self.lotNum - 1, originalPos)

        self.segment2.insertAJobIntoAPosInsideAVec(chosenMachineInd, chosenLotInd, newPos)
        # print(chosenMachineInd)
        # print(chosenLotInd)
        # print(newPos)


    def nerghbourIncreaseOrDecreaseASublotNum(self):
        """
        功能：
        s1邻域算子
        随机选取一个lot，增加或者减小1个sublot
        """
        # 选一个lot
        chosenLotInd = random.randint(0, self.lotNum - 1)
        increaseFlag = random.randint(0, 1)
        lotSize = self.segment1.lotSplitingCode[chosenLotInd].lotSize
        sublotNum = self.segment1.lotSplitingCode[chosenLotInd].sublotNum
        sublotSizes = self.segment1.lotSplitingCode[chosenLotInd].sublotSizes
        # 如果是增加一个sublot
        if increaseFlag:
            if sublotNum < lotSize:
                # 选一个sublotSize非1的sublot
                chosenSublotInd = random.randint(0, sublotNum - 1)
                while sublotSizes[chosenSublotInd] == 1:
                    chosenSublotInd = random.randint(0, sublotNum - 1)
                # 改变sublotNum
                self.segment1.lotSplitingCode[chosenLotInd].sublotNum += 1
                # 改变sublotSizes
                volum = random.randint(1, sublotSizes[chosenSublotInd] - 1)
                self.segment1.lotSplitingCode[chosenLotInd].sublotSizes[chosenSublotInd] -= volum
                self.segment1.lotSplitingCode[chosenLotInd].sublotSizes.append(volum)
        else:
            if sublotNum > 1:
                # 选两个sublot
                chosenSublotInd1 = random.randint(0, sublotNum - 1)
                chosenSublotInd2 = chooseARandomNumberExceptThis(0, sublotNum - 1 , chosenSublotInd1)
                # 改变sublotNum
                self.segment1.lotSplitingCode[chosenLotInd].sublotNum -= 1
                # 改变sublotSizes
                self.segment1.lotSplitingCode[chosenLotInd].sublotSizes[chosenSublotInd1] += self.segment1.lotSplitingCode[chosenLotInd].sublotSizes[chosenSublotInd2]
                del self.segment1.lotSplitingCode[chosenLotInd].sublotSizes[chosenSublotInd2]


    def neighbourSearch(self, neighbour, steps, searchTimes, solutionClassName):
        """
        功能：
        对个体进行不同模式的邻域搜索

        输入：
        neighbour           邻域模式，random是随机，s1是针对segment1随机，s2是针对segment2随机，s1n1,s1n2,s1n3,s2n1,s2n2
        steps               由原个体走step步，step步之后才择优
        searchTimes         走多少次完整的step步
        solutionClassName

        注意：
        这里有个bug，如果连走好几个step，self.lastLotInd和self.lastSublotInd都要在每一个step后都通过decode算出来
        """
        for _ in range(searchTimes):
            # 深copy
            searchCopy = copy.deepcopy(self)
            # 开始step步的搜索，不需要择优
            for _ in range(steps):
                # 各种模式预备好
                if neighbour == 'random':
                    neighbourType = random.randint(0, 4)
                elif neighbour == 's1':
                    neighbourType = random.randint(0, 2)
                elif neighbour == 's2':
                    neighbourType = random.randint(0, 1)
                # 对该copy动手
                if neighbour == 's1n1' or neighbour == 'random' and neighbourType == 0 or neighbour == 's1' and neighbourType == 0:
                    searchCopy.decode(solutionClassName)
                    searchCopy.neighourLastSublotResize()
                elif neighbour == 's1n2' or neighbour == 'random' and neighbourType == 1 or neighbour == 's1' and neighbourType == 1:
                    searchCopy.neighbourResizeTwoSublot()
                elif neighbour == 's1n3' or neighbour == 'random' and neighbourType == 2 or neighbour == 's1' and neighbourType == 2:
                    searchCopy.nerghbourIncreaseOrDecreaseASublotNum()
                elif neighbour == 's2n1' or neighbour == 'random' and neighbourType == 3 or neighbour == 's2' and neighbourType == 0:
                    searchCopy.decode(solutionClassName)
                    searchCopy.neighbourLastLotPreferenceAdvance()
                elif neighbour == 's2n2' or neighbour == 'random' and neighbourType == 4 or neighbour == 's2' and neighbourType == 1:
                    searchCopy.neighbourRepositionALot()
            # 择优
            searchCopy.decode(solutionClassName)
            if searchCopy.makespan <= self.makespan:
                if neighbour[1] == '1':
                    self.segment1 = copy.deepcopy(searchCopy.segment1)
                elif neighbour[1] == '2':
                    self.segment2 = copy.deepcopy(searchCopy.segment2)
                self.makespan = copy.deepcopy(searchCopy.makespan)
                self.lastLotInd = searchCopy.lastLotInd
                self.lastSublotInd = searchCopy.lastSublotInd
                # print(self.makespan)







# from generalSolution import generalSolution
# from globalVariablesAndFunctions import *
#
#
# test = generalIndividual(lotNum, lotSizes, machineNum)
# test.initializeIndividual()
# print(test.segment2.preferenceCode)
# for item in test.segment1.lotSplitingCode:
#     print(item.sublotSizes)
# test.decode(generalSolution)
# print(test.makespan)
# print('--------------')
#
# list1 = [6, 1, 7, 4]
# list2 = [[1, 1, 4, 8, 1, 5], [20], [4, 2, 2, 2, 2, 4, 4], [1, 4, 9, 6]]
# list3 = [[1, 2, 0, 3], [1, 2, 0, 3], [1, 3, 0, 2], [1, 3, 0, 2], [3, 2, 1, 0], [1, 2, 0, 3]]
#
# # list1 = [8, 2, 6, 2]
# # list2 = [[4, 1, 4, 3, 1, 1, 3, 3], [1, 19], [3, 2, 3, 4, 4, 4], [12, 8]]
# # list3 = [[1, 2, 3, 0], [1, 2, 0, 3], [3, 1, 0, 2], [3, 0, 2, 1], [2, 3, 1, 0], [2, 0, 1, 3]]
#
# for ind in range(lotNum):
#     test.segment1.lotSplitingCode[ind].sublotNum = list1[ind]
#     test.segment1.lotSplitingCode[ind].sublotSizes = list2[ind]
# test.segment2.preferenceCode = list3
#
# test.decode(generalSolution)
# print(test.makespan)
# print('--------------')
#
# test.neighbourSearch('s2', 3, 10, generalSolution)
# print(test.makespan)
#
# # test.nerghbourIncreaseOrDecreaseASublotNum()
# # for item in test.segment1.lotSplitingCode:
# #     print(item.sublotSizes)

# for i in range(20):
#     test.nerghbourIncreaseOrDecreaseASublotNum()
#     test.decode(generalSolution)
#     print(test.makespan)
# print('--------------')

