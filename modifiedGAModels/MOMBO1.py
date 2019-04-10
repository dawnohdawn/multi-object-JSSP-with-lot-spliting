from generalPopulation import generalPopulation
from generalIndividual import generalIndividual
from generalSolution import generalSolution
from globalVariablesAndFunctions import *


class MOMBO1(generalPopulation):
    """
    继承generalPopulation得到
    """

    def __init__(self, popSize, lotNum, lotSizes, machineNum):
        """
        指定了individual类是generalIndividual，solution类是generalSolution
        """
        super(MOMBO1, self).__init__(popSize, lotNum, lotSizes, machineNum, generalIndividual, generalSolution)

        self.name = 'MOMBO1'


        # 每个个体的年龄
        self.age = [0 for _ in range(self.popSize)]



    def iterate(self, iterNum, K, S, M, A, disturbNum=0.2, maxDisturbGap=0.1, needcalAllMakespan=1, muteEveryIter=0, muteResult=0, **kw):
        """
        功能：              简单GA迭代，可对同一个population对象连续使用
                            首次使用应把needcalAllMakespan设为1，后面应设为0以减少重复计算

        输入：
        iterNum             迭代次数
        K                   the number of neighbor solutions to be considered
        S                   the number of neighbor solutions to be shared with the next solution
        M                   number of tours
        A                   调整队形阶段的迭代次数
        needcalAllMakespan  在循环迭代之前是否需要计算全部个体的makespan，默认为1
        muteEveryIter       如果为0，打印每次迭代种群中最好makespan
        muteResult          如果为0，打印迭代结束后最好makespan

        可选输入：
        kw['startIter']            输出的迭代代数从此号码开始，如果不指定就从0开始
        kw['saveDetailsUsingDF']   是否把每一代的最好makespan都记录在一个DataFrame即self.details
        kw['aging']                如果为1，则记录每个个体的年龄，在队形调整阶段根据年龄使用不同邻域算子
        kw['needReinitializeAge']  如果为1，则在本函数内对age重新初始化

        注意：
        MBO的popsize一定要设为奇数
        """

        # 多目标的准备工作
        EMNum = 20
        RPMNum = 30
        NRPMNum = 10
        changePopInterval = 15
        changePopRPMInterval = 10
        changePopNRPMInterval = 50

        self.RPM = [generalIndividual(lotNum, lotSizes, machineNum) for i in range(RPMNum)]
        for item in self.RPM:
            item.initializeIndividual()
            item.decode(generalSolution)
        self.NRPM = [generalIndividual(lotNum, lotSizes, machineNum) for i in range(NRPMNum)]
        for item in self.NRPM:
            item.initializeIndividual()
            item.decode(generalSolution)
        self.EM = []



        # print([item.loadStd for item in self.RPM])
        # print([item.loadStd for item in self.NRPM])

        # 先定义一些内部函数
        def fuzzyVReshape():
            """
            功能：
            对pop所有鸟进行模糊排序，构建V字形的领头鸟，左右翼跟随鸟

            输出：
            领头鸟号
            左翼跟随鸟序号,list
            右翼跟随鸟序号,list
            """
            # 生成被打乱的排序
            indexMakespanDict =dict(zip(list(range(self.popSize)), self.getMakespansOfAllIndividuals()))
            sortedIndex = [item[0] for item in sorted(indexMakespanDict.items(), key=lambda x: x[1], reverse=False)]
            disturbedIndex = disturbList(sortedIndex, int(self.popSize * disturbNum), int(self.popSize * maxDisturbGap))
            # 安排领头鸟，左右翼跟随鸟
            leaderind = disturbedIndex[0]
            del disturbedIndex[0]
            leftWingind = [disturbedIndex[i] for i in range(self.popSize -1) if i % 2 == 0]
            rightWingind = [disturbedIndex[i] for i in range(self.popSize -1) if i % 2 == 1]

            return leaderind, leftWingind, rightWingind


        def VInitial():
            """
            仿照fuzzyVReshape写一个初始构建V字型的函数
            """
            indexs = [i for i in range(self.popSize)]
            random.shuffle(indexs)
            leaderind = indexs[0]
            del indexs[0]
            leftWingind = [indexs[i] for i in range(self.popSize - 1) if i % 2 == 0]
            rightWingind = [indexs[i] for i in range(self.popSize - 1) if i % 2 == 1]

            return leaderind, leftWingind, rightWingind


        def VReshape(leaderind, leftWingind, rightWingind):
            """
            仿照fuzzyVReshape写一个调整V字型的函数
            """
            LeaderInd = copy.deepcopy(leaderind)
            LeftWingInd = copy.deepcopy(leftWingind)
            RightWingInd = copy.deepcopy(rightWingind)

            if self.pop[LeftWingInd[0]].makespan < self.pop[RightWingInd[0]].makespan:
                LeftWingInd.append(LeaderInd)
                LeaderInd = LeftWingInd[0]
                del LeftWingInd[0]
            else:
                RightWingInd.append(LeaderInd)
                LeaderInd = RightWingInd[0]
                del RightWingInd[0]

            return LeaderInd, LeftWingInd, RightWingInd



        def dorminate(indi1, indi2):
            """
            功能：判断两个个体的支配关系
            输出：如果个体1支配个体2，则返回1，若个体2支配个体1，则返回2，若互补支配，则返回0
            如果相同，则返回3
            """
            # 如果个体1支配个体2
            if indi1.makespan <= indi2.makespan and indi1.loadStd <= indi2.loadStd \
                    and (indi1.makespan < indi2.makespan or indi1.loadStd < indi2.loadStd):
                return 1
            elif indi2.makespan <= indi1.makespan and indi2.loadStd <= indi1.loadStd \
                    and (indi2.makespan < indi1.makespan or indi2.loadStd < indi1.loadStd):
                return 2
            elif indi2.makespan == indi1.makespan and indi2.loadStd == indi1.loadStd:
                return 3
            else:
                return 0

        def findNDIndividual():
            """
            功能：把pop中的非支配个体找出来，返回序号
            """
            # 计算每个个体被支配了多少次
            DiList = []  # 支配i的个体数
            iDList = []  # i支配的个体数
            for i in range(len(self.pop)):
                Di = 0
                iD = 0
                for j in range(len(self.pop)):
                    if i != j:
                        is_do = dorminate(self.pop[i], self.pop[j])
                        if is_do == 1:
                            iD += 1
                        elif is_do == 2:
                            Di += 1
                DiList.append(Di)
                iDList.append(iD)

            NDList = []
            for i in range(len(self.pop)):
                if DiList[i] == 0:
                    NDList.append(i)
            return NDList


        def NSGAIIsort():
            """
            功能：对allIndividual做NSGAII的排序

            输出：选择后的popSize个个体
            """
            # 计算每个个体被支配了多少次
            DiList = [] # 支配i的个体数
            iDList = [] # i支配的个体数
            for i in range(len(allIndividual)):
                Di = 0
                iD = 0
                for j in range(len(allIndividual)):
                    if i != j:
                        is_do = dorminate(allIndividual[i], allIndividual[j])
                        if is_do == 1:
                            iD += 1
                        elif is_do == 2:
                            Di += 1
                DiList.append(Di)
                iDList.append(iD)
            # print(DiList, iDList)

            # 分层
            frontNum = len(set(DiList))
            front = list(set(DiList))
            front.sort()
            frontList = []
            for frontInd in front:
                thisFront = []
                for ind in range(len(allIndividual)):
                    if DiList[ind] == frontInd:
                        thisFront.append(ind)
                frontList.append(thisFront)
            # print(frontList)

            # 找到需要算密度的那一层
            sumNum = 0
            for i in range(frontNum):
                sumNum += len(frontList[i])
                if sumNum > self.popSize:
                    break
            calInd = i
            # print('calInd:', calInd)

            # 计算calInd层之前已经有多少个个体了
            beforeiNum = 0
            if calInd > 0:
                for i in range(calInd):
                    beforeiNum += len(frontList[i])
            # print("前面的个体有", beforeiNum)

            # 存放下一代的个体
            nextIndicidual = []
            # 先把frontList的前calInd层存进去，一共beforeiNum个个体
            for i in range(calInd):
                for j in range(len(frontList[i])):
                    nextIndicidual.append(copy.deepcopy(allIndividual[frontList[i][j]]))

            # beforeiNum不足popSize大，而且那一层个体数大于2，才要去计算那一层的密度，最后把个体加入nextIndicidual
            if beforeiNum < self.popSize and len(frontList[calInd]) > 2:
                thisMakespan = [item.makespan for item in [allIndividual[ind] for ind in frontList[calInd]]]
                thisLoadStd = [item.loadStd for item in [allIndividual[ind] for ind in frontList[calInd]]]
                dense = [0 for i in range(len(thisMakespan))]
                makespanSort = sorted(enumerate(thisMakespan), key=lambda x:x[1])
                # print('thisMakespan', thisMakespan)
                # print('thisLoadStd', thisLoadStd)
                # print('makespanSort', makespanSort)
                for i in range(len(thisMakespan)):
                    # 如果是排第一的个体
                    if i == 0:
                        dense[makespanSort[i][0]] += (thisMakespan[makespanSort[i+1][0]] + 300)
                        dense[makespanSort[i][0]] += (thisLoadStd[makespanSort[i+1][0]] + 40)
                    # 如果是排最后的个体
                    elif i == len(thisMakespan)-1 :
                        dense[makespanSort[i][0]] += (thisMakespan[makespanSort[i - 1][0]] + 300)
                        dense[makespanSort[i][0]] += (thisLoadStd[makespanSort[i - 1][0]] + 40)
                    # 如果是排中间的个体
                    else:
                        dense[makespanSort[i][0]] += thisMakespan[makespanSort[i + 1][0]]
                        dense[makespanSort[i][0]] += thisLoadStd[makespanSort[i + 1][0]]
                        dense[makespanSort[i][0]] += thisMakespan[makespanSort[i - 1][0]]
                        dense[makespanSort[i][0]] += thisLoadStd[makespanSort[i - 1][0]]
                # print('dense', dense)
                denseSort = sorted(enumerate(dense), key=lambda x:x[1], reverse = True)

                for i in range(self.popSize - beforeiNum):
                    nextIndicidual.append(copy.deepcopy(allIndividual[frontList[calInd][denseSort[i][0]]]))

            # beforeiNum不足popSize大，而且那一层个体数等于2，那一层不可能只有1个个体，那么随机选一个加入nextIndicidual
            elif beforeiNum < self.popSize and len(frontList[calInd]) <= 2:
                nextIndicidual.append(copy.deepcopy(allIndividual[frontList[calInd][0]]))
            # print('下一代', [item.makespan for item in nextIndicidual])
            # print('下一代', [item.loadStd for item in nextIndicidual])

            return nextIndicidual


        def NSGAIIsortTemp():
            """
            功能：对单个个体的所有邻域做NSGAII的排序

            输出：选择后的1个个体
            """
            # 计算每个个体被支配了多少次
            DiList = [] # 支配i的个体数
            iDList = [] # i支配的个体数
            for i in range(len(tempIndividual)):
                Di = 0
                iD = 0
                for j in range(len(tempIndividual)):
                    if i != j:
                        is_do = dorminate(tempIndividual[i], tempIndividual[j])
                        if is_do == 1:
                            iD += 1
                        elif is_do == 2:
                            Di += 1
                DiList.append(Di)
                iDList.append(iD)
            # print(DiList, iDList)

            # 分层
            frontNum = len(set(DiList))
            front = list(set(DiList))
            front.sort()
            frontList = []
            for frontInd in front:
                thisFront = []
                for ind in range(len(tempIndividual)):
                    if DiList[ind] == frontInd:
                        thisFront.append(ind)
                frontList.append(thisFront)
            # print(frontList)

            # 第一层，如果只有一个个体，则直接返回该个体，如果有两个个体，则返回任意一个，如果有两个以上个体，则计算密度值，返回密度最小的
            calInd = 0
            if len(frontList[0]) <= 2:
                nextIndicidual = copy.deepcopy(tempIndividual[frontList[0][0]])
            else:
                thisMakespan = [item.makespan for item in [tempIndividual[ind] for ind in frontList[0]]]
                thisLoadStd = [item.loadStd for item in [tempIndividual[ind] for ind in frontList[0]]]
                dense = [0 for i in range(len(thisMakespan))]
                makespanSort = sorted(enumerate(thisMakespan), key=lambda x: x[1])
                # print('thisMakespan', thisMakespan)
                # print('thisLoadStd', thisLoadStd)
                # print('makespanSort', makespanSort)
                for i in range(len(thisMakespan)):
                    # 如果是排第一的个体
                    if i == 0:
                        dense[makespanSort[i][0]] += (thisMakespan[makespanSort[i + 1][0]] + 300)
                        dense[makespanSort[i][0]] += (thisLoadStd[makespanSort[i + 1][0]] + 40)
                    # 如果是排最后的个体
                    elif i == len(thisMakespan) - 1:
                        dense[makespanSort[i][0]] += (thisMakespan[makespanSort[i - 1][0]] + 300)
                        dense[makespanSort[i][0]] += (thisLoadStd[makespanSort[i - 1][0]] + 40)
                    # 如果是排中间的个体
                    else:
                        dense[makespanSort[i][0]] += thisMakespan[makespanSort[i + 1][0]]
                        dense[makespanSort[i][0]] += thisLoadStd[makespanSort[i + 1][0]]
                        dense[makespanSort[i][0]] += thisMakespan[makespanSort[i - 1][0]]
                        dense[makespanSort[i][0]] += thisLoadStd[makespanSort[i - 1][0]]
                # print('dense', dense)
                denseSort = sorted(enumerate(dense), key=lambda x: x[1], reverse=True)
                nextIndicidual = copy.deepcopy(tempIndividual[frontList[0][denseSort[0][0]]])
            return  nextIndicidual





################################################################
#
################################################################

        progress = [0 for _ in range(iterNum)]

        # 第一代在此计算所有individual的makespan
        if needcalAllMakespan == 1:
            self.calAllMakespan()

        # 每次执行iterate都要清空这个DF
        self.details = pd.DataFrame(columns=['iter', 'bestMakespan'])

        # 记录每个个体的进化历史
        self.history = [[] for _ in range(self.popSize)]

        # 构建模糊V字队形
        # leaderInd, leftWingInd, rightWingInd = fuzzyVReshape()
        leaderInd, leftWingInd, rightWingInd = VInitial()

        for intervalInd in range(int (iterNum / (M + A))):
            # 一轮interval开始，一轮interval包含(M + A)个iter

            # 使用当前V字型进行M次的更新
            for m in range(M):
                # 一次iter开始

                # 记录个体进化历史
                for i in range(self.popSize):
                    self.history[i].append(self.pop[i].makespan)

                #重新计算iterNum
                iterInd = intervalInd * (M + A) + m

                # 每50iter打印一次内部信息
                # if(iterInd % 1 == 0):
                    # print(self.getMakespansOfAllIndividuals())
                    # print([item.loadStd for item in self.pop])

                # 用PM来初始化种群
                # if iterInd % changePopInterval == 0:
                #     allNum = len(self.RPM) + len(self.NRPM)
                #     selectedNum = random.sample(range(0, allNum), self.popSize)
                #     for i in range(self.popSize):
                #         if selectedNum[i] < len(self.RPM):
                #             self.pop[i] = copy.deepcopy(self.RPM[selectedNum[i]])
                #         else:
                #             self.pop[i] = copy.deepcopy(self.NRPM[selectedNum[i] - len(self.RPM)])
                #     print('重新生成pop')

                # 先把整个种群deepcopy到newPop中，在newPop上操作
                newPop = copy.deepcopy(self.pop)

                # 记录本iter所有个体
                allIndividual = []
                allIndividual.extend(copy.deepcopy(self.pop))

                # 领头鸟更新
                # 初始化领头鸟邻域集
                leaderNei = []
                leaderNeiMakespan = []
                # 生成K个邻域解
                tempIndividual = [self.pop[leaderInd]]
                for _ in range(K):
                    tempBird = self.pop[leaderInd].neighbourSearch('s1&s2', 1, 1, self.solutionClassName, inplace = 0)
                    leaderNei.append(tempBird)
                    leaderNeiMakespan.append(tempBird.makespan)

                    if tempBird.makespan != self.pop[leaderInd].makespan and tempBird.loadStd != self.pop[leaderInd].loadStd:
                        allIndividual.append(tempBird)
                        tempIndividual.append(tempBird)
                # 选出最好的邻域解，与领头鸟择优
                bestNei = NSGAIIsortTemp()
                newPop[leaderInd] = copy.deepcopy(bestNei)
                # if min(leaderNeiMakespan) <= self.pop[leaderInd].makespan:
                #     bestNeiInd = leaderNeiMakespan.index(min(leaderNeiMakespan))
                #     bestNei = leaderNei[bestNeiInd]
                #     newPop[leaderInd] = copy.deepcopy(bestNei)

                # 左右翼跟随鸟更新
                for wingInd in [leftWingInd, rightWingInd]:
                    for indOfWingInd, birdInd in enumerate(wingInd):
                        # 先清空每一只鸟的邻域集
                        wingNei = []
                        wingNeiMakespan = []
                        # 确定要向哪一只鸟学习
                        if birdInd == wingInd[0]:  # 如果是第一只跟随鸟，就跟领头鸟交叉
                            learnedBird = self.pop[leaderInd]
                        else:  # 如果不是领头鸟，则跟前一只鸟交叉
                            learnedBird = self.pop[wingInd[indOfWingInd - 1]]
                        # 交叉S次，分别挑最好的解加入邻域集
                        tempIndividual = [self.pop[birdInd]]
                        for _ in range(S):
                            chosenChild = self.pop[birdInd].crossoverBetweenBothSegmentsReturnBestChild(learnedBird, 0.5, 0.5, generalSolution)
                            wingNei.append(chosenChild)
                            wingNeiMakespan.append(chosenChild.makespan)

                            child1, child2 = self.pop[birdInd].crossoverBetweenBothSegmentsReturnAllChild(learnedBird, 0.5, 0.5, generalSolution)
                            if child1.makespan != self.pop[birdInd].makespan and child1.loadStd != self.pop[birdInd].loadStd:
                                allIndividual.append(child1)
                                tempIndividual.append(child1)
                            if child2.makespan != self.pop[birdInd].makespan and child2.loadStd != self.pop[birdInd].loadStd:
                                allIndividual.append(child2)
                                tempIndividual.append(child2)
                            # allIndividual.extend([child1, child2])
                        # 生成该鸟的邻域解，加入邻域集
                        for _ in range(K - S):
                            tempBird = self.pop[birdInd].neighbourSearch('s1&s2', 1, 1, self.solutionClassName, inplace=0)
                            wingNei.append(tempBird)
                            wingNeiMakespan.append(tempBird.makespan)

                            if tempBird.makespan != self.pop[birdInd].makespan and tempBird.loadStd != self.pop[birdInd].loadStd:
                                allIndividual.append(tempBird)
                                tempIndividual.append(tempBird)
                        # 选出最好的邻域解，与该鸟择优
                        # 如果<=了，替换
                        bestNei = NSGAIIsortTemp()
                        newPop[birdInd] = copy.deepcopy(bestNei)
                        # if min(wingNeiMakespan) <= self.pop[birdInd].makespan:
                        #     bestNeiInd = wingNeiMakespan.index(min(wingNeiMakespan))
                        #     bestNei = wingNei[bestNeiInd]
                        #     newPop[birdInd] = copy.deepcopy(bestNei)



                # self.pop = copy.deepcopy(NSGAIIsort())
                self.pop = copy.deepcopy(newPop)
                # print('新种群', [(item.makespan, item.loadStd) for item in self.pop])

                # 更新EM
                # 如果EM是空的，全部放进去
                if len(self.EM) == 0:
                    NDIdividualInd = []
                    NDIdividualInd = findNDIndividual()
                    for i in range(len(NDIdividualInd)):
                        self.EM.append(copy.deepcopy(self.pop[NDIdividualInd[i]]))
                # 如果EM不是空的，ND个体逐个检查是否被EM里的个体支配，不支配的才加进去，并删除原EM个体，互不支配，但是还有空位的时候也加进去
                else:
                    NDIdividualInd = findNDIndividual()
                    # 先检查ND个体有没有与EM个体相同的，如果有，则删掉ND个体
                    for ind in NDIdividualInd:
                        for item in self.EM:
                            is_dor = dorminate(self.pop[ind], item)
                            if is_dor == 3:
                                NDIdividualInd.remove(ind)
                                break
                    # 再让剩余的ND个体与EM个体对比
                    for i in range(len(NDIdividualInd)):
                        for item in self.EM:
                            is_dor = dorminate(self.pop[NDIdividualInd[i]], item)
                            # 如果ND个体被EM个体支配，则不要该ND个体
                            if is_dor == 2:
                                break
                            # 如果是完全相同的个体，也不要加
                            elif is_dor == 3:
                                break
                            # 如果ND个体支配了EM的个体，则要删除EM的该个体
                            elif is_dor == 1:
                                # del self.EM[j]
                                self.EM.remove(item)
                        # 没有break的ND个体i，要么是支配EM里的某些个体，要么是跟EM个体互不支配，都加进去EM里
                        if is_dor != 2 and is_dor != 3:
                            self.EM.append(copy.deepcopy(self.pop[NDIdividualInd[i]]))
                # 如果EM满了，需要删掉密度大的
                if len(self.EM) > EMNum:
                    EMMakespan = [item.makespan for item in self.EM]
                    EMLoadStd = [item.loadStd for item in self.EM]
                    dense = [0 for i in range(len(EMMakespan))]
                    makespanSort = sorted(enumerate(EMMakespan), key=lambda x: x[1])
                    # print('thisMakespan', thisMakespan)
                    # print('thisLoadStd', thisLoadStd)
                    # print('makespanSort', makespanSort)
                    for i in range(len(EMMakespan)):
                        # 如果是排第一的个体
                        if i == 0:
                            dense[makespanSort[i][0]] += (EMMakespan[makespanSort[i + 1][0]] + 300)
                            dense[makespanSort[i][0]] += (EMMakespan[makespanSort[i + 1][0]] + 40)
                        # 如果是排最后的个体
                        elif i == len(EMMakespan) - 1:
                            dense[makespanSort[i][0]] += (EMMakespan[makespanSort[i - 1][0]] + 300)
                            dense[makespanSort[i][0]] += (EMMakespan[makespanSort[i - 1][0]] + 40)
                        # 如果是排中间的个体
                        else:
                            dense[makespanSort[i][0]] += EMMakespan[makespanSort[i + 1][0]]
                            dense[makespanSort[i][0]] += EMMakespan[makespanSort[i + 1][0]]
                            dense[makespanSort[i][0]] += EMMakespan[makespanSort[i - 1][0]]
                            dense[makespanSort[i][0]] += EMMakespan[makespanSort[i - 1][0]]
                    # print('dense', dense)
                    denseSort = sorted(enumerate(dense), key=lambda x: x[1])
                    del self.EM[denseSort[0][0]]  # 删掉密度最大的那个个体
                # print('EM', [(i.makespan, i.loadStd) for i in self.EM])

                # # 更新RPM
                # # 先从RPM选出两个个体，选出两个支配解
                # if iterInd % changePopRPMInterval == 0:
                #     # print('RPM', [i.makespan for i in self.RPM])
                #     # print('RPM', [i.loadStd for i in self.RPM])
                #     NDIdividualInd = findNDIndividual()
                #     RPMInds = random.sample(range(0, len(self.RPM)), 2)
                #     if len(NDIdividualInd) > 2:
                #         NDInds = random.sample(range(0, len(NDIdividualInd)), 2)
                #     else:
                #         NDInds = [i for i in range(len(NDIdividualInd))]
                #     # print('RPMInds', [self.RPM[i].makespan for i in RPMInds])
                #     # print('RPMInds', [self.RPM[i].loadStd for i in RPMInds])
                #     # print('NDInds', [self.pop[NDIdividualInd[i]].makespan for i in NDInds])
                #     # print('NDInds', [self.pop[NDIdividualInd[i]].loadStd for i in NDInds])
                #     # 替换RPM那两个解
                #     if len(NDInds) == 1:
                #         if dorminate(self.pop[NDIdividualInd[NDInds[0]]], self.RPM[RPMInds[0]]) == 1:
                #             del self.RPM[RPMInds[0]]
                #             self.RPM.append(copy.deepcopy(self.pop[NDIdividualInd[NDInds[0]]]))
                #         elif dorminate(self.pop[NDIdividualInd[NDInds[0]]], self.RPM[RPMInds[1]]) == 1:
                #             del self.RPM[RPMInds[1]]
                #             self.RPM.append(copy.deepcopy(self.pop[NDIdividualInd[NDInds[0]]]))
                #     else:
                #         if dorminate(self.pop[NDIdividualInd[NDInds[0]]], self.RPM[RPMInds[0]]) == 1:
                #             del self.RPM[RPMInds[0]]
                #             self.RPM.append(copy.deepcopy(self.pop[NDIdividualInd[NDInds[0]]]))
                #         if dorminate(self.pop[NDIdividualInd[NDInds[1]]], self.RPM[RPMInds[1]]) == 1:
                #             del self.RPM[RPMInds[1]]
                #             self.RPM.append(copy.deepcopy(self.pop[NDIdividualInd[NDInds[1]]]))
                #     print('RPM', [(i.makespan, i.loadStd) for i in self.RPM])
                #     # print('RPM', [i.loadStd for i in self.RPM])
                #
                # # 定期重新设置NRPM
                # if iterInd % changePopNRPMInterval == 0:
                #     self.NRPM = [generalIndividual(lotNum, lotSizes, machineNum) for i in range(NRPMNum)]
                #     for item in self.NRPM:
                #         item.initializeIndividual()
                #         item.decode(generalSolution)

                # 每个iter后的例行公事
                # 一个iter完成，将生成好的newPop深复制给pop
                # self.pop = copy.deepcopy(newPop)
                # 记录本iter，pop中最好的个体
                bestMakespan = self.getBestMakespan()
                # 如果mute为0，才去打印每次迭代最好makespan
                if muteEveryIter == 0:
                    if 'startIter' in kw.keys():
                        print('iter%d:' % (iterInd + kw['startIter']), bestMakespan)
                    else:
                        print('iter%d:' % (iterInd), bestMakespan)
                # 如果saveDetailsUsingDF为1，那么把细节记录到成员变量self.details中
                if 'saveDetailsUsingDF' in kw.keys() and kw['saveDetailsUsingDF'] == 1:
                    if 'startIter' in kw.keys():
                        self.details.loc[len(self.details)] = [iterInd + kw['startIter'], bestMakespan]
                    else:
                        self.details.loc[len(self.details)] = [iterInd, bestMakespan]






            # 队形调整阶段
            for a in range(A):
                # 一次iter开始

                # 记录个体进化历史
                for i in range(self.popSize):
                    self.history[i].append(self.pop[i].makespan)

                # 重新计算iterNum
                iterInd = intervalInd * (M + A) + M + a

                # 每50iter打印一次内部信息
                # if(iterInd % 1 == 0):
                    # print(self.getMakespansOfAllIndividuals())
                    # print([item.loadStd for item in self.pop])

                # 用PM来初始化种群
                # if iterInd % changePopInterval == 0:
                #     allNum = len(self.RPM) + len(self.NRPM)
                #     selectedNum = random.sample(range(0, allNum), self.popSize)
                #     for i in range(self.popSize):
                #         if selectedNum[i] < len(self.RPM):
                #             self.pop[i] = copy.deepcopy(self.RPM[selectedNum[i]])
                #         else:
                #             self.pop[i] = copy.deepcopy(self.NRPM[selectedNum[i] - len(self.RPM)])
                #     print('重新生成pop')

                # 先把整个种群deepcopy到newPop中，在newPop上操作
                newPop = copy.deepcopy(self.pop)

                # 记录本iter所有个体
                allIndividual = []
                allIndividual.extend(copy.deepcopy(self.pop))
                # print('lala', [item.makespan for item in allIndividual])

                # 更新每一只鸟
                for birdInd in range(self.popSize):
                    # 先清空每一只鸟的邻域集
                    wingNei = []
                    wingNeiMakespan = []
                    # 确定要向哪一只鸟学习，随机选择
                    learnedBird = self.pop[random.randint(0, self.popSize - 1)]

                    # 交叉S次，分别挑最好的解加入邻域集
                    tempIndividual = [self.pop[birdInd]]
                    for _ in range(S):
                        chosenChild = self.pop[birdInd].crossoverBetweenBothSegmentsReturnBestChild(learnedBird, 0.5, 0.5, generalSolution)
                        wingNei.append(chosenChild)
                        wingNeiMakespan.append(chosenChild.makespan)

                        child1, child2 = self.pop[birdInd].crossoverBetweenBothSegmentsReturnAllChild(learnedBird, 0.5, 0.5, generalSolution)
                        if child1.makespan != self.pop[birdInd].makespan and child1.loadStd != self.pop[birdInd].loadStd:
                            allIndividual.append(child1)
                            tempIndividual.append(child1)
                        if child2.makespan != self.pop[birdInd].makespan and child2.loadStd != self.pop[birdInd].loadStd:
                            allIndividual.append(child2)
                            tempIndividual.append(child2)
                        # allIndividual.extend([child1, child2])
                    # 生成该鸟的邻域解，加入邻域集
                    for _ in range(K - S):
                        tempBird = self.pop[birdInd].neighbourSearch('s1&s2', 1, 1, self.solutionClassName, inplace=0)
                        wingNei.append(tempBird)
                        wingNeiMakespan.append(tempBird.makespan)

                        if tempBird.makespan != self.pop[birdInd].makespan and tempBird.loadStd != self.pop[birdInd].loadStd:
                            allIndividual.append(tempBird)
                            tempIndividual.append(tempBird)
                    # 选出最好的邻域解，与该鸟择优
                    # 如果<=了，替换
                    bestNei = NSGAIIsortTemp()
                    newPop[birdInd] = copy.deepcopy(bestNei)
                    # if min(wingNeiMakespan) <= self.pop[birdInd].makespan:
                    #     bestNeiInd = wingNeiMakespan.index(min(wingNeiMakespan))
                    #     bestNei = wingNei[bestNeiInd]
                    #     newPop[birdInd] = copy.deepcopy(bestNei)

                # self.pop = copy.deepcopy(NSGAIIsort())
                self.pop = copy.deepcopy(newPop)
                # print('新种群', [(item.makespan, item.loadStd) for item in self.pop])


                # 更新EM
                # 如果EM是空的，全部放进去
                if len(self.EM) == 0:
                    NDIdividualInd = []
                    NDIdividualInd = findNDIndividual()
                    for i in range(len(NDIdividualInd)):
                        self.EM.append(copy.deepcopy(self.pop[NDIdividualInd[i]]))
                # 如果EM不是空的，ND个体逐个检查是否被EM里的个体支配，不支配的才加进去，并删除原EM个体，互不支配，但是还有空位的时候也加进去
                else:
                    NDIdividualInd = findNDIndividual()
                    # 先检查ND个体有没有与EM个体相同的，如果有，则删掉ND个体
                    for ind in NDIdividualInd:
                        for item in self.EM:
                            is_dor = dorminate(self.pop[ind], item)
                            if is_dor == 3:
                                NDIdividualInd.remove(ind)
                                break
                    # 再让剩余的ND个体与EM个体对比
                    for i in range(len(NDIdividualInd)):
                        for item in self.EM:
                            is_dor = dorminate(self.pop[NDIdividualInd[i]], item)
                            # 如果ND个体被EM个体支配，则不要该ND个体
                            if is_dor == 2:
                                break
                            # 如果是完全相同的个体，也不要加
                            elif is_dor == 3:
                                break
                            # 如果ND个体支配了EM的个体，则要删除EM的该个体
                            elif is_dor == 1:
                                # del self.EM[j]
                                self.EM.remove(item)
                        # 没有break的ND个体i，要么是支配EM里的某些个体，要么是跟EM个体互不支配，都加进去EM里
                        if is_dor != 2 and is_dor != 3:
                            self.EM.append(copy.deepcopy(self.pop[NDIdividualInd[i]]))
                # 如果EM满了，需要删掉密度大的
                if len(self.EM) > EMNum:
                    EMMakespan = [item.makespan for item in self.EM]
                    EMLoadStd = [item.loadStd for item in self.EM]
                    dense = [0 for i in range(len(EMMakespan))]
                    makespanSort = sorted(enumerate(EMMakespan), key=lambda x: x[1])
                    # print('thisMakespan', thisMakespan)
                    # print('thisLoadStd', thisLoadStd)
                    # print('makespanSort', makespanSort)
                    for i in range(len(EMMakespan)):
                        # 如果是排第一的个体
                        if i == 0:
                            # dense[makespanSort[i][0]] += (EMMakespan[makespanSort[i + 1][0]] + 300)
                            # dense[makespanSort[i][0]] += (EMMakespan[makespanSort[i + 1][0]] + 40)
                            dense[makespanSort[i][0]] += (EMMakespan[makespanSort[i + 1][0]] / max(EMMakespan) + max(EMMakespan))
                            dense[makespanSort[i][0]] += (EMLoadStd[makespanSort[i + 1][0]] / max(EMLoadStd) + max(EMLoadStd))
                        # 如果是排最后的个体
                        elif i == len(EMMakespan) - 1:
                            dense[makespanSort[i][0]] += (EMMakespan[makespanSort[i - 1][0]] / max(EMMakespan) + max(EMMakespan))
                            dense[makespanSort[i][0]] += (EMLoadStd[makespanSort[i - 1][0]] / max(EMLoadStd) + max(EMLoadStd))
                        # 如果是排中间的个体
                        else:
                            dense[makespanSort[i][0]] += (EMMakespan[makespanSort[i + 1][0]] / max(EMMakespan))
                            dense[makespanSort[i][0]] += (EMLoadStd[makespanSort[i + 1][0]] / max(EMMakespan))
                            dense[makespanSort[i][0]] += (EMMakespan[makespanSort[i - 1][0]] / max(EMMakespan))
                            dense[makespanSort[i][0]] += (EMLoadStd[makespanSort[i - 1][0]] / max(EMMakespan))
                    # print('dense', dense)
                    denseSort = sorted(enumerate(dense), key=lambda x: x[1])
                    del self.EM[denseSort[0][0]]  # 删掉密度最大的那个个体
                # print('EM', [(i.makespan, i.loadStd) for i in self.EM])


                # # 更新RPM
                # # 先从RPM选出两个个体，选出两个支配解
                # if iterInd % changePopRPMInterval == 0:
                #     # print('RPM', [i.makespan for i in self.RPM])
                #     # print('RPM', [i.loadStd for i in self.RPM])
                #     NDIdividualInd = findNDIndividual()
                #     RPMInds = random.sample(range(0, len(self.RPM)), 2)
                #     if len(NDIdividualInd) > 2:
                #         NDInds = random.sample(range(0, len(NDIdividualInd)), 2)
                #     else:
                #         NDInds = [i for i in range(len(NDIdividualInd))]
                #     # print('RPMInds', [self.RPM[i].makespan for i in RPMInds])
                #     # print('RPMInds', [self.RPM[i].loadStd for i in RPMInds])
                #     # print('NDInds', [self.pop[NDIdividualInd[i]].makespan for i in NDInds])
                #     # print('NDInds', [self.pop[NDIdividualInd[i]].loadStd for i in NDInds])
                #     # 替换RPM那两个解
                #     if len(NDInds) == 1:
                #         if dorminate(self.pop[NDIdividualInd[NDInds[0]]], self.RPM[RPMInds[0]]) == 1:
                #             del self.RPM[RPMInds[0]]
                #             self.RPM.append(copy.deepcopy(self.pop[NDIdividualInd[NDInds[0]]]))
                #         elif dorminate(self.pop[NDIdividualInd[NDInds[0]]], self.RPM[RPMInds[1]]) == 1:
                #             del self.RPM[RPMInds[1]]
                #             self.RPM.append(copy.deepcopy(self.pop[NDIdividualInd[NDInds[0]]]))
                #     else:
                #         if dorminate(self.pop[NDIdividualInd[NDInds[0]]], self.RPM[RPMInds[0]]) == 1:
                #             del self.RPM[RPMInds[0]]
                #             self.RPM.append(copy.deepcopy(self.pop[NDIdividualInd[NDInds[0]]]))
                #         if dorminate(self.pop[NDIdividualInd[NDInds[1]]], self.RPM[RPMInds[1]]) == 1:
                #             del self.RPM[RPMInds[1]]
                #             self.RPM.append(copy.deepcopy(self.pop[NDIdividualInd[NDInds[1]]]))
                #     print('RPM', [(i.makespan, i.loadStd) for i in self.RPM])
                #     # print('RPM', [i.loadStd for i in self.RPM])
                #
                # # 定期重新设置NRPM
                # if iterInd % changePopNRPMInterval == 0:
                #     self.NRPM = [generalIndividual(lotNum, lotSizes, machineNum) for i in range(NRPMNum)]
                #     for item in self.NRPM:
                #         item.initializeIndividual()
                #         item.decode(generalSolution)

                # 每个iter后的例行公事
                # 一个iter完成，将生成好的newPop深复制给pop
                # self.pop = copy.deepcopy(newPop)
                # 记录本iter，pop中最好的个体
                bestMakespan = self.getBestMakespan()
                # 如果mute为0，才去打印每次迭代最好makespan
                if muteEveryIter == 0:
                    if 'startIter' in kw.keys():
                        print('iter%d:' % (iterInd + kw['startIter']), bestMakespan)
                    else:
                        print('iter%d:' % (iterInd), bestMakespan)
                # 如果saveDetailsUsingDF为1，那么把细节记录到成员变量self.details中
                if 'saveDetailsUsingDF' in kw.keys() and kw['saveDetailsUsingDF'] == 1:
                    if 'startIter' in kw.keys():
                        self.details.loc[len(self.details)] = [iterInd + kw['startIter'], bestMakespan]
                    else:
                        self.details.loc[len(self.details)] = [iterInd, bestMakespan]


            # 变换队形，重新构建模糊V字队形
            leaderInd, leftWingInd, rightWingInd = VInitial()
            # leaderInd, leftWingInd, rightWingInd = VReshape(leaderInd, leftWingInd, rightWingInd)


        if muteResult == 0:
            print('result after %d iterations:' % iterNum, self.getBestMakespan())
            # print(min(self.getMakespansOfAllIndividuals()))
            # print(self.getMakespansOfAllIndividuals())
            print('last EM', [(i.makespan, i.loadStd) for i in self.EM])

        # 打印progress可以看到每个种群的每一代有多少个体在交叉变异种进步了
        # print(progress)



# test = myMBO1(51, lotNum, lotSizes, machineNum)
# test.iterate(10, 3, 1, 8, 2, 0.2, 0.1, needcalAllMakespan=1, muteEveryIter=0, muteResult=0, startIter=0, saveDetailsUsingDF=1,  needReinitializeAge=1)

# test.getBestIndividualCodes()
# test.getMakespansOfAllIndividuals()