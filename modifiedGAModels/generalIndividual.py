import random
import os
import copy
from individualLotSplitingCode import individualLotSplitingCode
from individualPreferenceCode import individualPreferenceCode
from generalSolution import generalSolution
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


    def reinitializeAlotSplitingVec(self):
        """
        功能：
        随机选取一条lotSplitingVec，重新初始化
        """
        selectedInd = random.randint(0, self.lotNum - 1)
        self.segment1.lotSplitingCode[selectedInd].initializeLotSplitingVec()


    def returnBestNewIndividuals(self, n, solutionClassName):
        """
        功能：
        随机初始化几个新个体，返回最优个体

        输入：
        n                   随机初始化n个新个体
        solutionClassName   solution类名字
        """
        individualList = []
        individualListMakespan = []
        for i in range(n):
            newIndividual = generalIndividual(self.lotNum, self.lotSizes, self.machineNum)
            newIndividual.initializeIndividual()
            newIndividual.decode(solutionClassName)
            individualList.append(newIndividual)
            individualListMakespan.append(newIndividual.makespan)
        return individualList[individualListMakespan.index(min(individualListMakespan))]



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


    def crossoverBetweenSegment1s(indi1, indi2, p, inplace = 1):
        """
        按概率p选位，交叉两个individual的segment1的位（以一个lot为一位）

        inplace      如果为1，则替换indi1和indi2个体，如果为0，则返回两个子代
        """
        # 如果要替换
        if inplace == 1:
            for i in range(indi1.lotNum):
                if random.random() < p:
                    indi1.segment1.lotSplitingCode[i], indi2.segment1.lotSplitingCode[i] = \
                        indi2.segment1.lotSplitingCode[i], indi1.segment1.lotSplitingCode[i]
        # 如果不用替换，则返回两个子代
        else:
            indi1Copy = copy.deepcopy(indi1)
            indi2Copy = copy.deepcopy(indi2)
            for i in range(indi1Copy.lotNum):
                if random.random() < p:
                    indi1Copy.segment1.lotSplitingCode[i], indi2Copy.segment1.lotSplitingCode[i] = \
                        indi2Copy.segment1.lotSplitingCode[i], indi1Copy.segment1.lotSplitingCode[i]
            return indi1Copy, indi2Copy


    def crossoverBetweenSegment2s(indi1, indi2, p, inplace = 1):
        """
        按概率p选位，交叉两个individual的segment2的位（以一台机器为一位）

        inplace      如果为01，则替换indi1和indi2个体，如果为0，则返回两个子代
        """
        # 如果需要替换
        if inplace == 1:
            for i in range(indi1.machineNum):
                if (random.random() < p):
                    indi1.segment2.preferenceCode[i], indi2.segment2.preferenceCode[i] = \
                        indi2.segment2.preferenceCode[i], indi1.segment2.preferenceCode[i]
        # 如果不需要替换，则返回两个子代
        else:
            indi1Copy = copy.deepcopy(indi1)
            indi2Copy = copy.deepcopy(indi2)
            for i in range(indi1Copy.machineNum):
                if random.random() < p:
                    indi1Copy.segment2.preferenceCode[i], indi2Copy.segment2.preferenceCode[i] = \
                        indi2Copy.segment2.preferenceCode[i], indi1Copy.segment2.preferenceCode[i]
            return indi1Copy, indi2Copy


    def crossoverBetweenSegment2sWithPOX(self, indi2, p):
        """
        功能：
        s2交叉的第二种方法，POX
        先按p的概率选择几个job，在所有preferenceVec中，这几个job的位置不变，其他job的顺序用indi2的

        输入：
        indi2       另一个个体
        p           选job的概率
        """
        # 选择不变的job
        selectedJobs = [i for i in range(self.lotNum) if random.random() < p]
        while len(selectedJobs) % self.lotNum == 0 or len(selectedJobs) == self.lotNum - 1:
            selectedJobs = [i for i in range(self.lotNum) if random.random() < p]
        notSelectedJobs = [i for i in range(self.lotNum) if i not in selectedJobs]

        # 将notSelectedJobs在各个vec的位置都找出来
        indi1Pos = [[i for i in range(self.lotNum) if self.segment2.preferenceCode[vecInd][i] in notSelectedJobs] for vecInd in range(self.machineNum)]
        indi2Pos = [[i for i in range(self.lotNum) if indi2.segment2.preferenceCode[vecInd][i] in notSelectedJobs] for vecInd in range(self.machineNum)]

        # 将notSelectedJobs在各个vec的顺序找出来
        indi1Order = [[item for item in self.segment2.preferenceCode[vecInd] if item in notSelectedJobs] for vecInd in range(self.machineNum)]
        indi2Order = [[item for item in indi2.segment2.preferenceCode[vecInd] if item in notSelectedJobs] for vecInd in range(self.machineNum)]

        # 改变
        for vecInd in range(self.machineNum):
            for posInd in range(len(indi2Order[0])):
                self.segment2.preferenceCode[vecInd][indi1Pos[vecInd][posInd]] = copy.deepcopy(indi2Order[vecInd][posInd])
        for vecInd in range(self.machineNum):
            for posInd in range(len(indi1Order[0])):
                indi2.segment2.preferenceCode[vecInd][indi2Pos[vecInd][posInd]] = copy.deepcopy(indi1Order[vecInd][posInd])

        # print(selectedJobs)


    def crossoverBetweenBothSegments(indi1, indi2, p1, p2, inplace = 1):
        """
        功能：
        同时对s1和s2交叉

        输入：
        indi2       第二个父代
        p1          s1交叉的选位概率
        p2          s2交叉的选位概率
        inplace     如果为1，则替换indi1和indi2个体，如果为0，则返回两个子代

        输出：
        如果inplace为0，则返回两个子代

        注意：
        本函数不计算makespan
        """
        # 如果要替换
        if inplace == 1:
            #交叉s1
            for i in range(indi1.lotNum):
                if random.random() < p1:
                    indi1.segment1.lotSplitingCode[i], indi2.segment1.lotSplitingCode[i] = \
                        indi2.segment1.lotSplitingCode[i], indi1.segment1.lotSplitingCode[i]
            # 交叉s2
            for i in range(indi1.machineNum):
                if random.random() < p2:
                    indi1.segment2.preferenceCode[i], indi2.segment2.preferenceCode[i] = \
                        indi2.segment2.preferenceCode[i], indi1.segment2.preferenceCode[i]
        # 如果不需要替换
        else:
            indi1Copy = copy.deepcopy(indi1)
            indi2Copy = copy.deepcopy(indi2)
            # 交叉s1
            for i in range(indi1Copy.lotNum):
                if random.random() < p1:
                    indi1Copy.segment1.lotSplitingCode[i], indi2Copy.segment1.lotSplitingCode[i] = \
                        indi2Copy.segment1.lotSplitingCode[i], indi1Copy.segment1.lotSplitingCode[i]
            # 交叉s2
            for i in range(indi1Copy.machineNum):
                if random.random() < p2:
                    indi1Copy.segment2.preferenceCode[i], indi2Copy.segment2.preferenceCode[i] = \
                        indi2Copy.segment2.preferenceCode[i], indi1Copy.segment2.preferenceCode[i]
            return indi1Copy, indi2Copy

    def crossoverBetweenBothSegmentsReturnBestChild(self, indi2, p1, p2, solutionClassName):
        """
        功能：
        同时对s1s2交叉，计算子代的makespan，并返回最优的子代

        输入：
        indi2       第二个父代
        p1          s1交叉的选位概率
        p2          s2交叉的选位概率
        solutionClassName    用于decode的sulution类名字

        输出：
        优秀子代
        """
        child1, child2 = self.crossoverBetweenBothSegments(indi2, p1, p2, inplace=0)
        child1.decode(solutionClassName)
        child2.decode(solutionClassName)
        if child1.makespan < child2.makespan:
            return child1
        else:
            return child2


    def crossoverBetweenBothSegmentsReturnAllChild(self, indi2, p1, p2, solutionClassName):
        """
        功能：
        同时对s1s2交叉，计算子代的makespan，并返回所有的子代

        输入：
        indi2       第二个父代
        p1          s1交叉的选位概率
        p2          s2交叉的选位概率
        solutionClassName    用于decode的sulution类名字

        输出：
        优秀子代
        """
        child1, child2 = self.crossoverBetweenBothSegments(indi2, p1, p2, inplace=0)
        child1.decode(solutionClassName)
        child2.decode(solutionClassName)

        return child1, child2



    def decode(self, solutionClassName):
        """
        计算并返回完工时间
        """
        #         solu = solution(self)
        solu = solutionClassName(self)
        solu.run()
        self.makespan = solu.getMakespan()
        self.loadStd = solu.getLoadStd()

        self.lastLotInd, self.lastSublotInd = solu.getLastFinishingSublot()


    def neighourLastSublotResize(self):
        """
        功能：
        s1邻域算子 S1N1
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
        s2邻域算子 S2N1
        最晚完工的lot在随意一个机器上的优先度提前1
        """
        chosenMachineInd = random.randint(0, self.machineNum - 1)
        self.segment2.insertAJobInsideAVecEarlierOrLaterFewPos(chosenMachineInd, self.lastLotInd, 1)


    def neighbourResizeTwoSublot(self):
        """
        功能：
        s1邻域算子  S1N2
        随机选取一个lot，重新配置其中两个sublot的size
        """
        chosenLotInd = random.randint(0, self.lotNum - 1)
        self.segment1.lotSplitingCode[chosenLotInd].mutateTwoSublot()
        # print(chosenLotInd)


    def neighbourRepositionALot(self):
        """
        功能：
        s2邻域算子  S2N2
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
        s1邻域算子  S1N3
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
            if sublotNum < lotSize and sublotNum < maxLotNums[chosenLotInd]:  # 要保证当前sublotNum不能到达最大Num数
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


    def neighbourSwapTwoLotsOfAMachine(self):
        """
        功能：
        s2邻域算子 S2N3
        随机选取一台机器，随机选取两个lot号，swap两个基因位
        """
        chosenMachineInd = random.randint(0, self.machineNum - 1)
        chosenLotInd1, chosenLotInd2 = chooseTwoNumByRandom(self.lotNum - 1)
        self.segment2.swapTwoJobsInsideAvec(chosenMachineInd, chosenLotInd1, chosenLotInd2)


    def neighbourInverseLotsOfAMachine(self):
        """
        功能：
        s2邻域算子 S2N4
        随机选取一台机器，随机选取两个lot号，inverse这两个号之间的所有基因，包括头尾
        """
        chosenMachineInd = random.randint(0, self.machineNum - 1)
        chosenLotInd1, chosenLotInd2 = chooseTwoNumByRandom(self.lotNum - 1)
        # 要确保chosenLotInd1比chosenLotInd2小
        if chosenLotInd1 > chosenLotInd2:
            chosenLotInd1, chosenLotInd2 = chosenLotInd2, chosenLotInd1
        self.segment2.inverseInsideAVec(chosenMachineInd, chosenLotInd1, chosenLotInd2)


    def coarseGrainNeibourS1(self):
        """
        功能：
        s1粗粒度邻域算子
        随机选取S1的一个vec，检查该个体在coarseGrain表里面的序号，寻找其序号附近的vec替代原vec

        注意：
        寻找范围为前后10%的vec，四舍五入
        """
        chosenLotInd = random.randint(0, self.lotNum - 1)
        neighbourRnge = round(len(S1ExhaustiveList[chosenLotInd]) * 0.13)  # 计算寻找范围
        chosenVec = self.segment1.lotSplitingCode[chosenLotInd].sublotSizes
        chosenVec.sort()  # 排序，才能与S1ExhaustiveList匹配

        # 寻找该个体在S1ExhaustiveList的序号
        exhaustiveIndex = S1ExhaustiveList[chosenLotInd].index(chosenVec)

        # 选择附近的序号，要确保选的不是原序号
        chosenNeighbourIndex = (exhaustiveIndex + random.randint(-neighbourRnge, neighbourRnge)) % len(S1ExhaustiveList[chosenLotInd])
        while chosenNeighbourIndex == exhaustiveIndex:
            chosenNeighbourIndex = (exhaustiveIndex + random.randint(-neighbourRnge, neighbourRnge)) % len(
                S1ExhaustiveList[chosenLotInd])

        # 换掉
        newVec = S1ExhaustiveList[chosenLotInd][chosenNeighbourIndex]
        self.segment1.lotSplitingCode[chosenLotInd].sublotSizes = newVec
        self.segment1.lotSplitingCode[chosenLotInd].sublotNum = len(newVec)  # 更新完vec之后，记得更新sublotNum


    def coarseGrainNeibourS2(self):
        """
        功能：
        s2粗粒度邻域算子
        随机选取S2的一个vec，检查该个体在coarseGrain表里面的序号，寻找其序号附近的vec替代原vec
        """
        chosenMachineInd = random.randint(0, self.machineNum - 1)
        neighbourRnge = round(len(S2ExhaustiveList) * 0.13)  # 计算寻找范围
        chosenVec = self.segment2.preferenceCode[chosenMachineInd]

        # 寻找该个体在S2ExhaustiveList的序号
        exhaustiveIndex = S2ExhaustiveList.index(chosenVec)

        # 选择附近的序号，要确保选的不是原序号
        chosenNeighbourIndex = (exhaustiveIndex + random.randint(-neighbourRnge, neighbourRnge)) % len(
            S2ExhaustiveList)
        while chosenNeighbourIndex == exhaustiveIndex:
            chosenNeighbourIndex = (exhaustiveIndex + random.randint(-neighbourRnge, neighbourRnge)) % len(
                S2ExhaustiveList)

        # 换掉
        self.segment2.preferenceCode[chosenMachineInd] = S2ExhaustiveList[chosenNeighbourIndex]



    def neighbourSearch(self, neighbour, steps, searchTimes, solutionClassName, inplace = 1):
        """
        功能：
        对个体进行不同模式的邻域搜索

        输入：
        neighbour           邻域模式，random是随机，s1是针对segment1随机，s2是针对segment2随机，s1n1,s1n2,s1n3,s2n1,s2n2,s2n3,s2n4
        steps               由原个体走step步，step步之后才择优
        searchTimes         走多少次完整的step步
        solutionClassName
        inplace             如果为1，则使用邻域搜索的结果更新该解，如果为0，则不更新该解，不管好坏，输出搜索结果

        注意：
        这里有个bug，如果连走好几个step，self.lastLotInd和self.lastSublotInd都要在每一个step后都通过decode算出来
        """
        individualList = []
        individualMakespanList = []

        for _ in range(searchTimes):
            # 深copy
            searchCopy = copy.deepcopy(self)
            # 开始step步的搜索，不需要择优
            for _ in range(steps):
                # 各种模式预备好
                if neighbour == 'random':  # 所有上述邻域算子的随机
                    neighbourType = random.randint(0, 8)
                elif neighbour == 's1':
                    neighbourType = random.randint(0, 3)
                elif neighbour == 's2':
                    neighbourType = random.randint(0, 4)
                elif neighbour == 'random_simple':  # 这里是没有启发式邻域算子的random
                    availableType = [1, 2, 4, 5, 6]
                    neighbour = 'random'
                    neighbourType = availableType[random.randint(0, 4)]
                elif neighbour == 'coarse':  # 粗粒度邻域算组随机
                    neighbourType = random.randint(0, 1)
                elif neighbour == 'fine':  # 细粒度邻域算子随机
                    availableType = [0, 1, 2, 3, 4, 5, 6]
                    neighbour = 'random'
                    neighbourType = availableType[random.randint(0, 6)]
                elif neighbour == 's1&s2':
                    neighbourType1 = random.randint(0, 3)
                    neighbourType2 = random.randint(0, 4)
                # 对该copy动手
                if neighbour == 's1n1' or neighbour == 'random' and neighbourType == 0 or neighbour == 's1' and neighbourType == 0:
                    searchCopy.decode(solutionClassName)
                    searchCopy.neighourLastSublotResize()
                    neighbour = 's1n1'
                elif neighbour == 's1n2' or neighbour == 'random' and neighbourType == 1 or neighbour == 's1' and neighbourType == 1:
                    searchCopy.neighbourResizeTwoSublot()
                    neighbour = 's1n2'
                elif neighbour == 's1n3' or neighbour == 'random' and neighbourType == 2 or neighbour == 's1' and neighbourType == 2:
                    searchCopy.nerghbourIncreaseOrDecreaseASublotNum()
                    neighbour = 's1n3'
                elif neighbour == 's2n1' or neighbour == 'random' and neighbourType == 3 or neighbour == 's2' and neighbourType == 0:
                    searchCopy.decode(solutionClassName)
                    searchCopy.neighbourLastLotPreferenceAdvance()
                    neighbour = 's2n1'
                elif neighbour == 's2n2' or neighbour == 'random' and neighbourType == 4 or neighbour == 's2' and neighbourType == 1:
                    searchCopy.neighbourRepositionALot()
                    neighbour = 's2n2'
                elif neighbour == 's2n3' or neighbour == 'random' and neighbourType == 5 or neighbour == 's2' and neighbourType == 2:
                    searchCopy.neighbourSwapTwoLotsOfAMachine()
                    neighbour = 's2n3'
                elif neighbour == 's2n4' or neighbour == 'random' and neighbourType == 6 or neighbour == 's2' and neighbourType == 3:
                    searchCopy.neighbourInverseLotsOfAMachine()
                    neighbour = 's2n4'
                elif neighbour == 's1coarse' or neighbour == 'random' and neighbourType == 7 or neighbour == 'coarse' and neighbourType == 0\
                        or neighbour == 's1' and neighbourType == 3:
                    searchCopy.coarseGrainNeibourS1()
                    neighbour = 's1coarse'
                elif neighbour == 's2coarse' or neighbour == 'random' and neighbourType == 8 or neighbour == 'coarse' and neighbourType == 1\
                        or neighbour == 's2' and neighbourType == 4:
                    searchCopy.coarseGrainNeibourS2()
                    neighbour = 's2coarse'
                elif neighbour == 's1&s2':
                    if neighbourType1 == 0:
                        searchCopy.decode(solutionClassName)
                        searchCopy.neighourLastSublotResize()
                        neighbour = 's1n1'
                    elif neighbourType1 == 1:
                        searchCopy.neighbourResizeTwoSublot()
                        neighbour = 's1n2'
                    elif neighbourType1 == 2:
                        searchCopy.nerghbourIncreaseOrDecreaseASublotNum()
                        neighbour = 's1n1'
                    elif neighbourType1 == 3:
                        searchCopy.coarseGrainNeibourS1()
                        neighbour = 's1coarse'
                    if neighbourType2 == 0:
                        searchCopy.decode(solutionClassName)
                        searchCopy.neighbourLastLotPreferenceAdvance()
                        neighbour = 's2n1'
                    elif neighbourType2 == 1:
                        searchCopy.neighbourRepositionALot()
                        neighbour = 's2n2'
                    elif neighbourType2 == 2:
                        searchCopy.neighbourSwapTwoLotsOfAMachine()
                        neighbour = 's2n3'
                    elif neighbourType2 == 3:
                        searchCopy.neighbourInverseLotsOfAMachine()
                        neighbour = 's2n4'
                    elif neighbourType2 == 4:
                        searchCopy.coarseGrainNeibourS2()
                        neighbour = 's2coarse'

            # 解码，加入集合
            searchCopy.decode(solutionClassName)
            individualList.append(searchCopy)
            individualMakespanList.append(searchCopy.makespan)

        # 选出searchTimes个个体中最好的一个
        bestIndividual = individualList[individualMakespanList.index(min(individualMakespanList))]

        # 如果要替换
        if inplace == 1:
            # <=才去替换
            if bestIndividual.makespan <= self.makespan:
                self.segment1 = copy.deepcopy(bestIndividual.segment1)
                self.segment2 = copy.deepcopy(bestIndividual.segment2)
                self.makespan = copy.deepcopy(bestIndividual.makespan)
                self.lastLotInd = bestIndividual.lastLotInd
                self.lastSublotInd = bestIndividual.lastSublotInd

        # 如果不用替换
        else:
            if bestIndividual.makespan < self.makespan:
                neighbourCounts[neighbour] += 1
            return bestIndividual






# # 测试单个邻域算子
# test = generalIndividual(lotNum, lotSizes, machineNum)
# test.initializeIndividual()
# test2 = generalIndividual(lotNum, lotSizes, machineNum)
# test2.initializeIndividual()
#
# print('parent1')
# for item in test.segment1.lotSplitingCode:
#     print(item.sublotSizes)
# print(test.segment2.preferenceCode)
# test.decode(generalSolution)
# print(test.makespan)
#
# # print('parent2')
# # for item in test2.segment1.lotSplitingCode:
# #     print(item.sublotSizes)
# # print(test2.segment2.preferenceCode)
# # test2.decode(generalSolution)
# # print(test2.makespan)
#
# print('after')
# # test.crossoverBetweenSegment2sWithPOX(test2, 0.5)
# test.reinitializeAlotSplitingVec()
# # test.neighbourSwapTwoLotsOfAMachine()
# # test.neighbourInverseLotsOfAMachine()
# # test.coarseGrainNeibourS2()
# # test3, test4 = test.crossoverBetweenBothSegments(test2, 0.5, 0.5, inplace = 0)
# # test3, test4 = test.crossoverBetweenBothSegments(test2, 0.5, 0.5, inplace = 0)
# # test5 = test.crossoverBetweenBothSegmentsReturnBestChild(test2, 0.5, 0.5, generalSolution)
# # for item in test.segment1.lotSplitingCode:
# #     print(item.sublotSizes)
#
# print('parent1')
# for item in test.segment1.lotSplitingCode:
#     print(item.sublotSizes)
# print(test.segment2.preferenceCode)
# test.decode(generalSolution)
# print(test.makespan)
#
# # print('parent2')
# # for item in test2.segment1.lotSplitingCode:
# #     print(item.sublotSizes)
# # print(test2.segment2.preferenceCode)
# # test2.decode(generalSolution)
# # print(test2.makespan)
#
# # print('child1')
# # for item in test3.segment1.lotSplitingCode:
# #     print(item.sublotSizes)
# # print(test3.segment2.preferenceCode)
# # test3.decode(generalSolution)
# # print(test3.makespan)
# #
# # print('child2')
# # for item in test4.segment1.lotSplitingCode:
# #     print(item.sublotSizes)
# # print(test4.segment2.preferenceCode)
# # test4.decode(generalSolution)
# # print(test4.makespan)
# #
# # print('child3')
# # for item in test5.segment1.lotSplitingCode:
# #     print(item.sublotSizes)
# # print(test5.segment2.preferenceCode)
# # test5.decode(generalSolution)
# # print(test5.makespan)



# # 测试多步邻域算子
# test = generalIndividual(lotNum, lotSizes, machineNum)
# test.initializeIndividual()
# for item in test.segment1.lotSplitingCode:
#     print(item.sublotSizes)
# print(test.segment2.preferenceCode)
# test.decode(generalSolution)
# print(test.makespan)
# print('--------------')
#
# # list1 = [6, 1, 7, 4]
# # list2 = [[1, 1, 4, 8, 1, 5], [20], [4, 2, 2, 2, 2, 4, 4], [1, 4, 9, 6]]
# # list3 = [[1, 2, 0, 3], [1, 2, 0, 3], [1, 3, 0, 2], [1, 3, 0, 2], [3, 2, 1, 0], [1, 2, 0, 3]]
#
# # for ind in range(lotNum):
# #     test.segment1.lotSplitingCode[ind].sublotNum = list1[ind]
# #     test.segment1.lotSplitingCode[ind].sublotSizes = list2[ind]
# # test.segment2.preferenceCode = list3
# # test.decode(generalSolution)
#
# # new = test.neighbourSearch('s1coarse', 1, 10, generalSolution,inplace = 0)
# test.neighbourSearch('s1coarse', 1, 10, generalSolution)
#
# print('after')
#
# for item in test.segment1.lotSplitingCode:
#     print(item.sublotSizes)
# print(test.segment2.preferenceCode)
# test.decode(generalSolution)
# print(test.makespan)
#
# # print(new.makespan)
# # for item in new.segment1.lotSplitingCode:
# #     print(item.sublotSizes)
# # print(new.segment2.preferenceCode)
# # print(new.makespan)




# test.nerghbourIncreaseOrDecreaseASublotNum()
# for item in test.segment1.lotSplitingCode:
#     print(item.sublotSizes)
#
# for i in range(20):
#     test.nerghbourIncreaseOrDecreaseASublotNum()
#     test.decode(generalSolution)
#     print(test.makespan)
# print('--------------')



# test = generalIndividual(lotNum, lotSizes, machineNum)
# test2 = test.returnBestNewIndividuals(3, generalSolution)
# print(test2.makespan)