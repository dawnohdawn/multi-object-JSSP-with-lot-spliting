from globalVariablesAndFunctions import *
from generalSolution import generalSolution
from generalIndividual import generalIndividual
from generalPopulation import generalPopulation


#################################
# 以下是单种群类
#################################

class myMBO(generalPopulation):
    """
    继承generalPopulation得到
    """

    def __init__(self, popSize, lotNum, lotSizes, machineNum):
        """
        指定了individual类是generalIndividual，solution类是generalSolution
        """
        super(myMBO, self).__init__(popSize, lotNum, lotSizes, machineNum, generalIndividual, generalSolution)

        # self.name = 'myMBO'

        # 每个个体的年龄
        self.age = [0 for _ in range(self.popSize)]

        # 记录每个个体的进化历史
        self.history = [[] for _ in range(self.popSize)]



    def iterate(self, bestHistory, outerIterInd, outerIterNum, iterNum, K, S, M, A, neighbourSearchMode, disturbNum, maxDisturbGap, needcalAllMakespan=1, muteEveryIter=0, muteResult=0, **kw):
        """
        功能：              简单GA迭代，可对同一个population对象连续使用
                            首次使用应把needcalAllMakespan设为1，后面应设为0以减少重复计算

        输入：
        iterNum             迭代次数
        K                   the number of neighbor solutions to be considered
        S                   the number of neighbor solutions to be shared with the next solution
        M                   number of tours
        A                   调整队形阶段的迭代次数
        neighbourSearchMode 邻域搜索模式，可以是'random','s1','s2'
        disturbNum          模糊排序中的扰乱次数百分比
        maxDisturbGap       模糊排序中的扰乱跨度
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


        # 定义aging几个阈值
        agingThreshold = [10, 40, 50]
        # agingThreshold = [10, 30, 40]
        # print('agingThreshold:', agingThreshold)


        def returnAnIndividualFromBestHistory():
            """
            功能：
            随机返回bestHistory里面一个个体

            注意：
            调用本函数的时候，注意用深copy
            """
            i = random.randint(1, len(bestHistory) - 1)
            key = sorted(list(bestHistory.keys()))[i]
            j = random.randint(0, len(bestHistory[key]) - 1)
            return bestHistory[key][j]


        def returnNeighbourFunctionRarameterByAging(birdAge):
            """
            功能：
            根据个体的age，返回应该使用的neighbourSearch参数

            输入：
            birdAge      一只鸟的age

            输出：
            para1        steps
            para2        searchTimes
            """
            # 如果不使用aging
            if 'aging' not in kw.keys():
                return [1, 1]
            # 如果使用aging
            else:
                if birdAge < agingThreshold[0]:
                    return [1, 1]
                elif birdAge >= agingThreshold[0] and birdAge < agingThreshold[1]:
                    return [1, 2]
                elif birdAge >= agingThreshold[1]:
                    # return [2, 2]
                    return [1, 2]


        def updatAgeFlag(birdAge, mode):
            """
            功能：
            当个体有进步的时候，根据个体的age，使用该函数更新ageFlag

            输入：
            birdAge      一只鸟的age
            mode         要么是succeed，要么是fail

            注意：
            本函数不适用于丢弃时ageFlag的更新
            """
            # if birdAge < agingThreshold[0]:
            #     ageFlag[0] += 1
            # elif birdAge >= agingThreshold[0] and birdAge < agingThreshold[1]:
            #     ageFlag[1] += 1
            # elif birdAge >= agingThreshold[1] and birdAge < agingThreshold[2]:
            #     ageFlag[2] += 1age
            for i in range(7):
                if birdAge in range(10 * i, 10 * (i + 1), 1):
                    # ageFlag[i] += 1
                    ageFlag[i][1] += 1
                    if mode == 'succeed':
                        ageFlag[i][0] += 1


        progress = [0 for _ in range(iterNum)]

        # 第一代在此计算所有individual的makespan
        if needcalAllMakespan == 1:
            self.calAllMakespan()

        # 每次执行iterate都要清空这个DF
        self.details = pd.DataFrame(columns=['iter', 'bestMakespan'])

        # 重新初始化每个个体的年龄
        if 'needReinitializeAge' in kw and kw['needReinitializeAge'] == 1:
            self.age = [0 for _ in range(self.popSize)]

        # 构建模糊V字队形
        leaderInd, leftWingInd, rightWingInd = fuzzyVReshape()

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
                #     print(self.age)
                #     print(self.getMakespansOfAllIndividuals())
                #     print(self.getBestIndividualCodes())

                # 先把整个种群deepcopy到newPop中，在newPop上操作
                newPop = copy.deepcopy(self.pop)

                # 领头鸟更新
                # 初始化领头鸟邻域集
                leaderNei = []
                leaderNeiMakespan = []
                # 生成K个邻域解
                for _ in range(K):
                    para = returnNeighbourFunctionRarameterByAging(self.age[leaderInd])
                    tempBird = self.pop[leaderInd].neighbourSearch(neighbourSearchMode, para[0], para[1], self.solutionClassName, inplace = 0)
                    leaderNei.append(tempBird)
                    leaderNeiMakespan.append(tempBird.makespan)
                    # 更新ageFlag
                    if min(leaderNeiMakespan) < self.pop[leaderInd].makespan:
                        updatAgeFlag(self.age[leaderInd], mode = 'succeed')
                    else:
                        updatAgeFlag(self.age[leaderInd], mode='fail')
                # 选出最好的邻域解，与领头鸟择优，更新年龄
                if min(leaderNeiMakespan) <= self.pop[leaderInd].makespan:
                    self.age[leaderInd] = 0
                    bestNeiInd = leaderNeiMakespan.index(min(leaderNeiMakespan))
                    bestNei = leaderNei[bestNeiInd]
                    newPop[leaderInd] = copy.deepcopy(bestNei)
                else:
                    self.age[leaderInd] += 1

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

                        # 下面分情况
                        # 情况1，不使用aging，或者使用aging且该个体尚年轻
                        if 'aging' not in kw.keys() or 'aging' in kw.keys() and kw['aging'] == 1 and self.age[birdInd] < agingThreshold[2]:
                            # 判断个体是否需要退化
                            if 'aging' in kw.keys() and kw['aging'] == 1 and self.age[birdInd] == agingThreshold[1] and outerIterInd >= int(outerIterNum/3)+1:
                                descendIndividual = returnAnIndividualFromBestHistory()
                                if descendIndividual.makespan > self.pop[birdInd].makespan:
                                    print('age',self.age[birdInd],'descend', self.pop[birdInd].makespan)
                                    self.pop[birdInd] = copy.deepcopy(descendIndividual)
                                    print('to', self.pop[birdInd].makespan)
                            # 交叉S次，分别挑最好的解加入邻域集
                            for _ in range(S):
                                chosenChild = self.pop[birdInd].crossoverBetweenBothSegmentsReturnBestChild(learnedBird, 0.5, 0.5, generalSolution)
                                wingNei.append(chosenChild)
                                wingNeiMakespan.append(chosenChild.makespan)
                            # 生成该鸟的邻域解，加入邻域集
                            for _ in range(K - S):
                                para = returnNeighbourFunctionRarameterByAging(self.age[birdInd])
                                tempBird = self.pop[birdInd].neighbourSearch(neighbourSearchMode, para[0], para[1], self.solutionClassName, inplace=0)
                                wingNei.append(tempBird)
                                wingNeiMakespan.append(tempBird.makespan)
                                # 更新ageFlag
                                if tempBird.makespan < self.pop[birdInd].makespan:
                                    updatAgeFlag(self.age[birdInd], mode = 'succeed')
                                else:
                                    updatAgeFlag(self.age[birdInd], mode='fail')
                            # 选出最好的邻域解，与该鸟择优
                            # 如果<=了，替换
                            if min(wingNeiMakespan) <= self.pop[birdInd].makespan:
                                bestNeiInd = wingNeiMakespan.index(min(wingNeiMakespan))
                                bestNei = wingNei[bestNeiInd]
                                newPop[birdInd] = copy.deepcopy(bestNei)
                            # 更新年龄
                            if min(wingNeiMakespan) < self.pop[birdInd].makespan:
                                self.age[birdInd] = 0
                            else:
                                self.age[birdInd] += 1
                        # 情况2：使用aging且该鸟年龄太大了，丢弃，重新初始化K个邻域解，挑最好的去替换该鸟
                        else:
                            newPop[birdInd] = copy.deepcopy(self.pop[birdInd].returnBestNewIndividuals(K, generalSolution))
                            # 记录aging策略成功次数
                            ageFlag[-1][1] += 1
                            # 更新年龄
                            self.age[birdInd] = 0

                # 每个iter后的例行公事
                # 一个iter完成，将生成好的newPop深复制给pop
                self.pop = copy.deepcopy(newPop)
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
                #     print(self.age)
                #     print(self.getMakespansOfAllIndividuals())
                #     print(self.getBestIndividualCodes())

                # 先把整个种群deepcopy到newPop中，在newPop上操作
                newPop = copy.deepcopy(self.pop)

                # 更新每一只鸟
                for birdInd in range(self.popSize):
                    # 先清空每一只鸟的邻域集
                    wingNei = []
                    wingNeiMakespan = []
                    # 确定要向哪一只鸟学习，随机选择
                    learnedBird = self.pop[random.randint(0, self.popSize - 1)]
                    # 下面分情况
                    # 情况1，不使用aging，或者使用aging且该个体尚年轻
                    if 'aging' not in kw.keys() or 'aging' in kw.keys() and kw['aging'] == 1 and self.age[birdInd] < agingThreshold[2]:
                        # 判断个体是否需要退化
                        if 'aging' in kw.keys() and kw['aging'] == 1 and self.age[birdInd] == agingThreshold[
                            1] and outerIterInd >= int(outerIterNum / 3) + 1:
                            descendIndividual = returnAnIndividualFromBestHistory()
                            if descendIndividual.makespan > self.pop[birdInd].makespan:
                                print('age', self.age[birdInd], 'descend', self.pop[birdInd].makespan)
                                self.pop[birdInd] = copy.deepcopy(descendIndividual)
                                print('to', self.pop[birdInd].makespan)
                        # 交叉S次，分别挑最好的解加入邻域集
                        for _ in range(S):
                            chosenChild = self.pop[birdInd].crossoverBetweenBothSegmentsReturnBestChild(learnedBird, 0.5, 0.5, generalSolution)
                            wingNei.append(chosenChild)
                            wingNeiMakespan.append(chosenChild.makespan)
                        # 生成该鸟的邻域解，加入邻域集
                        for _ in range(K - S):
                            para2 = returnNeighbourFunctionRarameterByAging(self.age[birdInd])
                            tempBird = self.pop[birdInd].neighbourSearch(neighbourSearchMode, para2[0], para2[1], self.solutionClassName, inplace=0)
                            wingNei.append(tempBird)
                            wingNeiMakespan.append(tempBird.makespan)
                            # 更新ageFlag
                            if tempBird.makespan < self.pop[birdInd].makespan:
                                updatAgeFlag(self.age[birdInd], mode = 'succeed')
                            else:
                                updatAgeFlag(self.age[birdInd], mode='fail')
                        # 选出最好的邻域解，与该鸟择优
                        # 如果<=了，替换
                        if min(wingNeiMakespan) <= self.pop[birdInd].makespan:
                            bestNeiInd = wingNeiMakespan.index(min(wingNeiMakespan))
                            bestNei = wingNei[bestNeiInd]
                            newPop[birdInd] = copy.deepcopy(bestNei)
                        # 更新年龄
                        if min(wingNeiMakespan) < self.pop[birdInd].makespan:
                            self.age[birdInd] = 0
                        else:
                            self.age[birdInd] += 1
                    # 情况2：使用aging且该鸟年龄太大了，丢弃，重新初始化K个邻域解，挑最好的去替换该鸟
                    else:
                        newPop[birdInd] = copy.deepcopy(self.pop[birdInd].returnBestNewIndividuals(K, generalSolution))
                        # 记录aging策略成功次数
                        ageFlag[-1][1] += 1
                        # 更新年龄
                        self.age[birdInd] = 0
                        # print('reset bird')



                # 每个iter后的例行公事
                # 一个iter完成，将生成好的newPop深复制给pop
                self.pop = copy.deepcopy(newPop)
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
            leaderInd, leftWingInd, rightWingInd = fuzzyVReshape()


        if muteResult == 0:
            print('result after %d iterations:' % iterNum, self.getBestMakespan())
            # print(min(self.getMakespansOfAllIndividuals()))
            # print(self.getMakespansOfAllIndividuals())

        # 打印progress可以看到每个种群的每一代有多少个体在交叉变异种进步了
        # print(progress)

        # print(bestHistory)



#################################
# 以下是多种群类
#################################

class myPMBO1:
    """
    成员变量：
    self.modelSize       有多少个island（种群）
    self.popSize         每个种群有多少个individual
    self.lotNum          有多少个lot
    self.lotSizes        list，每个lot有多少个工件
    self.machineNum      有多少台机器
    self.model           list，由self.modleSize个pop类组成
    self.detailsOfModel  记录每一代每一个种群的最好个体的makespan，行数=种群个数*innerIterNum*OuterIterNum
    """

    def __init__(self, modelSize, popSize, lotNum, lotSizes, machineNum):
        self.modelSize = modelSize
        self.popSize = popSize
        self.lotNum = lotNum
        self.lotSizes = lotSizes
        self.machineNum = machineNum
        self.individualClassName = generalIndividual
        self.popClassName = myMBO
        self.solutionClassName = generalSolution

        self.model = [self.popClassName(self.popSize, self.lotNum, self.lotSizes, self.machineNum) for i in range(self.modelSize)]

        self.detailsOfModel = pd.DataFrame(columns=['pop', 'iter', 'outerIter', 'bestMakespan'])

        self.name = 'myPMBO1'


    def resetModel(self):
        """
        重新初始化所有种群的所有个体
        """
        for i in range(self.modelSize):
            self.model[i].resetPop()


    def calAllModelMakespan(self):
        """
        功能：     对所有种群里所有个体计算makespan
        """
        for i in range(self.modelSize):
            self.model[i].calAllMakespan()


    def getBestMakespanOfEveryPop(self):
        """
        功能：     返回每个种群最好makespan组成的list
        """
        return [self.model[i].getBestMakespan() for i in range(self.modelSize)]


    def getBestMakespanAmongAllPops(self):
        """
        功能：     返回所有种群中最好的makespan
        """
        return min(self.getBestMakespanOfEveryPop())


    def getBestIndexOfAllPops(self):
        """
        功能：     返回所有种群中最优个体的pop序号和个体序号
        输出：
        pop序号
        个体序号
        """
        bestIndexs = [self.model[i].getBestIndividualIndex() for i in range(self.modelSize)]
        bestMakespans = self.getBestMakespanOfEveryPop()

        popInd = bestMakespans.index(min(bestMakespans))
        indiInd = bestIndexs[popInd]

        return popInd, indiInd


    def getMakespansOfAllIndividuals(self):
        """
        功能：     返回所有个体的makespan，返回一个二维的list
        """
        makespans = []
        for i in range(self.modelSize):
            makespans.append(self.model[i].getMakespansOfAllIndividuals())

        return makespans


    def getMakespansOfAllIndividualsInOneList(self):
        """
        功能：     返回所有个体的makespan，返回一个一维的list
        """
        makespans = []
        for i in range(self.modelSize):
            makespans.extend(self.model[i].getMakespansOfAllIndividuals())

        return makespans


    def getBestIndividualCodes(self):
        """
        功能：        返回最优个体的sublotNum、sublotSizes、preferenceCode，都是以list的形式
        """
        # 找到最优个体的序号
        bestPopInd, bestIndiInd = self.getBestIndexOfAllPops()

        return self.model[bestPopInd].getBestIndividualCodes()


    def getCertainIndividualOfPopulation(self, popInd, mode, choosePercentage, shuffle = 0):
        """
        功能：            返回某个种群部分个体在种群中的序号

        输入：
        popInd            种群序号
        mode              选择模式，可以是'best','worst',random'
        choosePercentage  选出choosePercentage%个个体，例如可以是10，30等

        输出：
        indexs            一个list，包含部分个体在种群中的序号
        shuffle           如果为1，则在best和worst模式下用shuffle模式，即排序与index脱钩
        """
        # 先确定要选多少个个体
        chooseNum = int(choosePercentage * self.popSize / 100.0)

        # 找出个体的索引
        if mode == 'best':
            makespanList = [self.model[popInd].pop[i].makespan for i in range(self.popSize)]
            indexs = getBestOrWorstIndexs(mode, makespanList, chooseNum, shuffle)
        elif mode == 'worst':
            makespanList = [self.model[popInd].pop[i].makespan for i in range(self.popSize)]
            indexs = getBestOrWorstIndexs(mode, makespanList, chooseNum, shuffle)
        elif mode == 'random':
            indexs = random.sample(range(self.popSize), chooseNum)

        return indexs



    def getBestAndRamdomIndividualOfPopulation(self, popInd, choosePercentage, shuffle = 0):
        """
        功能：            返回某个种群最优和随机的个体

        输入：
        popInd            种群序号
        choosePercentage  最优个体和随机个体分别需要多少个
        shuffle           如果为1，则在best和worst模式下用shuffle模式，即排序与index脱钩
        """
        # 先确定分别要选多少个best和random个体
        chooseNum = int(choosePercentage * self.popSize / 100.0)

        # 选出最好的个体
        makespanList = [self.model[popInd].pop[i].makespan for i in range(self.popSize)]
        bestIndexs = getBestOrWorstIndexs('best', makespanList, chooseNum, shuffle)

        # 从剩余个体中选出随机个体
        randomPool = [i for i in range(self.popSize) if i not in bestIndexs]
        randomIndexs = random.sample(randomPool, chooseNum)

        return bestIndexs, randomIndexs


    def migrateBetweenTwoPops(self, mode, popIndex1, popIndex2, individualIndexs1, individualIndexs2):
        """
        功能：              在两个种群之间迁移

        输入：
        mode                模式，可以是'replace'，或者是'exchange'
        popIndex1           第一个种群序号，如果模式是'replace'，则为源种群序号
        popIndex2           第二个种群序号，如果模式是'replace'，则为目标种群序号
        individualIndexs1   list，第一个种群中需要migrate的个体序号
        individualIndexs2   list，第二个种群中需要migrate的个体序号
        """
        if mode == 'replace':
            for i in range(len(individualIndexs1)):
                self.model[popIndex2].pop[individualIndexs2[i]] = copy.deepcopy(
                    self.model[popIndex1].pop[individualIndexs1[i]])  # 要深copy才保险
                # 还要记得把age改了
                self.model[popIndex2].age[individualIndexs2[i]] = copy.deepcopy(
                    self.model[popIndex1].age[individualIndexs1[i]])
        elif mode == 'exchange':
            for i in range(len(individualIndexs1)):
                self.model[popIndex1].pop[individualIndexs1[i]], self.model[popIndex2].pop[individualIndexs2[i]] = \
                    self.model[popIndex2].pop[individualIndexs2[i]], self.model[popIndex1].pop[individualIndexs1[i]]
                # 还要记得把age交换了
                self.model[popIndex1].age[individualIndexs1[i]], self.model[popIndex2].age[individualIndexs2[i]] = \
                    self.model[popIndex2].age[individualIndexs2[i]], self.model[popIndex1].age[individualIndexs1[i]]


    def migrationOfAllPops(self, mode, choosePercentage):
        """
        功能:              所有种群进行迁移

        输入：
        mode               模式，可以是'replace'，或者是'exchange'
        choosePercentage   选出choosePercentage%个个体，例如可以是10，30等
        """
        # 先生成每个种群最好和最差的个体index
        migrateIndexs = []
        for i in range(self.modelSize):
            # migrateIndexs.append(
            #     [self.getCertainIndividualOfPopulation(i, mode='best', choosePercentage=choosePercentage), \
                 # self.getCertainIndividualOfPopulation(i, mode='worst', choosePercentage=choosePercentage)])
             migrateIndexs.append(self.getBestAndRamdomIndividualOfPopulation(i, choosePercentage=choosePercentage, shuffle=1))

        # 三个种群按照0-1,1-2,2-0的顺序migration
        for i in range(self.modelSize):
            fromPop = i
            toPop = (i + 1) % self.modelSize
            self.migrateBetweenTwoPops(mode, fromPop, toPop, migrateIndexs[fromPop][0], migrateIndexs[toPop][1])


    def modelIterate(self, outerIterNum, innerIterNum, K, S, M, A, mode, migratePercentage, \
                     muteEveryMBOIter=1, muteMBOResult=1, muteEveryOuterIter=0, muteOuterResult=0, **kw):

        """
        功能：                      使用简单GA迭代来构建IMGA的迭代

        输入：
        outerIterNum                模型要进行多少次migrate
        innerIterNum                每多少个iter就要migrate一次，innerIterNum应该是(M+A)的倍数
        K                           the number of neighbor solutions to be considered
        S                           the number of neighbor solutions to be shared with the next solution
        M                           number of tours
        A                           调整队形阶段的迭代次数
        mode                        模式，可以是'replace'，或者是'exchange'
        muteEveryGAIter             如果为0，打印每次GA迭代种群中最好makespan
        muteGAResult                如果为0，打印inner迭代结束后最好makespan
        muteEveryOuterIter          如果为0，打印每次outer迭代种群中最好makespan
        muteOuterResult             如果为0，打印outer迭代结束后最好makespan

        可选输入：
        kw['saveDetailsUsingDF']   是否生成一个DataFrame来记录详细结果
        """

        # 每次都要重置这个dataframe
        self.detailsOfModel = pd.DataFrame(columns=['pop', 'iter', 'outerIter', 'bestMakespan'])

        # 第一次迭代需要手动计算所有个体的makespan
        self.calAllModelMakespan()

        # 创建并初始化BestHistory记录历史个体，只记录6个最好的makespan的分别10个个体
        # 记录所有pop里面所有个体makespan
        maxBestLen = 6
        allMakespans = self.getMakespansOfAllIndividualsInOneList()
        # makespan去重
        uniqueMakespans = set(allMakespans)
        # 找到最小的6个makespan
        minMakespans = list(uniqueMakespans)
        minMakespans.sort()
        if len(minMakespans) > maxBestLen:
            minMakespans = minMakespans[:maxBestLen]
        # 创建空的bestHistory
        self.bestHistory = {}
        for i in range(len(minMakespans)):
            self.bestHistory[minMakespans[i]] = []
        # 找到这6个makespan的各自10个个体
        for i in range(len(minMakespans)):
            for j in range(len(allMakespans)):
                if minMakespans[i] == allMakespans[j] and len(self.bestHistory[minMakespans[i]]) < 10:
                    self.bestHistory[minMakespans[i]].append(copy.deepcopy(self.model[int(j / self.popSize)].pop[int(j % self.popSize)]))
        print(self.bestHistory)

        # 外部迭代
        for outerIterInd in range(outerIterNum):

            # 内部迭代，三个pop更新
            for popInd in range(self.modelSize):
                # GA
                if 'saveDetailsUsingDF' in kw.keys() and kw['saveDetailsUsingDF'] == 1:
                    saveDetailsUsingDF = kw['saveDetailsUsingDF']
                # 三个种群分化进化
                if popInd == 0:
                    self.model[popInd].iterate(self.bestHistory, outerIterInd, outerIterNum, innerIterNum, K, S, M, A, 'random', 0.25, 0.25, needcalAllMakespan=0, \
                                               muteEveryIter=muteEveryMBOIter, muteResult=muteMBOResult, \
                                               startIter=outerIterInd * innerIterNum, \
                                               saveDetailsUsingDF=saveDetailsUsingDF, aging = 1, needReinitializeAge=0)
                elif popInd == 1:
                    self.model[popInd].iterate(self.bestHistory, outerIterInd, outerIterNum, innerIterNum, K, S, M, A, 's1', 0.25, 0.25, needcalAllMakespan=0, \
                                               muteEveryIter=muteEveryMBOIter, muteResult=muteMBOResult, \
                                               startIter=outerIterInd * innerIterNum, \
                                               saveDetailsUsingDF=saveDetailsUsingDF, aging=1, needReinitializeAge=0)
                elif popInd == 2:
                    self.model[popInd].iterate(self.bestHistory, outerIterInd, outerIterNum, innerIterNum, K, S, M, A, 's2', 0.25, 0.25, needcalAllMakespan=0, \
                                               muteEveryIter=muteEveryMBOIter, muteResult=muteMBOResult, \
                                               startIter=outerIterInd * innerIterNum, \
                                               saveDetailsUsingDF=saveDetailsUsingDF, aging=1, needReinitializeAge=0)
                print(self.model[popInd].getMakespansOfAllIndividuals())
                # print(self.model[popInd].age)

                # 记录到dataframe里
                if 'saveDetailsUsingDF' in kw.keys() and kw['saveDetailsUsingDF'] == 1:
                    self.model[popInd].details['pop'] = popInd
                    self.model[popInd].details['outerIter'] = outerIterInd
                    self.detailsOfModel = self.detailsOfModel.append(self.model[popInd].details, ignore_index=True)

            # 所有pop进化完之后，才更新一次bestHistory
            # 记录所有pop里面所有个体makespan
            if outerIterInd >= int(outerIterNum/3):
                allMakespans = self.getMakespansOfAllIndividualsInOneList()
                # makespan去重
                uniqueMakespans = set(allMakespans)
                # 找到最小的6个makespan
                minMakespans = list(uniqueMakespans)
                minMakespans.sort()
                if len(minMakespans) > 6:
                    minMakespans = minMakespans[:6]
                # 更新key
                addMakespan = sorted((set(minMakespans) - set(self.bestHistory.keys())))
                outMakespan = sorted(list(set(self.bestHistory.keys()) - set(minMakespans)))
                if len(addMakespan) == 0:  # 如果addMakespan是空的，说明不需要更新key了
                    outMakespan = []
                else:  # 如果addMakespan不是空的，说明要更新key
                    for additem in addMakespan:
                        for outitem in outMakespan:
                            if additem > outitem:
                                addMakespan.remove(additem)
                                outMakespan.remove(min(outMakespan))
                                break
                    for item in outMakespan:
                        del self.bestHistory[item]
                    for item in addMakespan:
                        self.bestHistory[item] = []
                # delcnt = 0
                # keys = sorted(list(self.bestHistory.keys()))
                # for i in range(len(minMakespans)):
                #     print('i=', i, 'minMakespans=', minMakespans, 'keys=', keys)
                #     if minMakespans[i] < keys[delcnt]:
                #         del self.bestHistory[keys[-1-i]]
                #         self.bestHistory[minMakespans[i]] = []
                #         delcnt += 1
                # 更新values
                minMakespans = sorted(list(self.bestHistory.keys()))
                for i in range(len(minMakespans)):
                    for j in range(len(allMakespans)):
                        if minMakespans[i] == allMakespans[j]:
                            # 如果还不够10个
                            if len(self.bestHistory[minMakespans[i]]) < 10 and random.random() < 0.2 or len(self.bestHistory[minMakespans[i]]) == 0:
                                self.bestHistory[minMakespans[i]].append(
                                    copy.deepcopy(self.model[int(j / self.popSize)].pop[int(j % self.popSize)]))
                            # 如果已经超过10个
                            elif len(self.bestHistory[minMakespans[i]]) >= 10 and random.random() < 0.2:
                                delpos = random.randint(0, 9)
                                del self.bestHistory[minMakespans[i]][delpos]
                                self.bestHistory[minMakespans[i]].append(
                                    copy.deepcopy(self.model[int(j / self.popSize)].pop[int(j % self.popSize)]))
                print(self.bestHistory.keys())

            # 打印完整外部迭代一代后的结果
            if muteEveryOuterIter == 0:
                print('outerIter: %d' % outerIterInd, self.getBestMakespanAmongAllPops(),
                      self.getBestMakespanOfEveryPop())

            # 每个外部迭代一代，就迁移一次，迁移的mode在此指定
            self.migrationOfAllPops(mode, choosePercentage=migratePercentage, )

        if muteOuterResult == 0:
            print('result after {num1} outerIteration and {num2} innerIteration which is {num3} in total:'. \
                  format(num1=outerIterNum, num2=innerIterNum, num3=outerIterNum * innerIterNum), \
                  self.getBestMakespanAmongAllPops())

        # 整理一下这个dataframe
        if 'saveDetailsUsingDF' in kw.keys() and kw['saveDetailsUsingDF'] == 1:
            self.detailsOfModel = self.detailsOfModel.groupby(['iter']).min()


    def decodeAFixedIndividual(self, codeLists):
        """
        功能：       输入三条编码，观察解码过程，并生成甘特图

        输入：
        codeLists    为一个list，里面放着三条编码
        """
        self.model[0].decodeAFixedIndividual(codeLists)



test = myPMBO1(3, 17, lotNum, lotSizes, machineNum)
test.modelIterate(100, 10, 3, 1, 8, 2, 'exchange', 20, muteEveryMBOIter=1, muteMBOResult=1, muteEveryOuterIter=0, muteOuterResult=0, saveDetailsUsingDF=1)
print('p2，选择个体的函数加入了shuffle，或许会提高后期跳出局部最优的能力')