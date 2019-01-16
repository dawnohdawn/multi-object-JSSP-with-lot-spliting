from globalVariablesAndFunctions import *
PATH = os.path.abspath('.')


# 种群类
class generalPopulation:
    """
    由多个individual组成的种群，具有GA的选择、交叉、变异功能

    self.popSize     种群容量
    self.lotNum      有多少个lot
    self.lotSizes    list，每个lot有多少个工件
    self.machineNum  机器数量
    self.details     记录本种群每次迭代DataFrame
    self.individualClassName   个体类名称
    self.solutionClassName  用于解码的类名称，方面后面替换为多目标的solution
    self.pop         由individual构成的list
    """

    def __init__(self, popSize, lotNum, lotSizes, machineNum, individualClassName, solutionClassName):

        self.popSize = popSize
        self.lotNum = lotNum
        self.lotSizes = lotSizes
        self.machineNum = machineNum
        self.individualClassName = individualClassName
        self.solutionClassName = solutionClassName

        self.pop = [self.individualClassName(lotNum, lotSizes, machineNum) for i in range(popSize)]
        for item in self.pop:
            item.initializeIndividual()

        self.details = pd.DataFrame(columns=['iter', 'bestMakespan'])


    def resetPop(self):
        """
        重新随机生成新种群
        """
        for item in self.pop:
            item.initializeIndividual()


    def calAllMakespan(self):
        """
        对本种群内所有个体解码，计算每个个体的完工时间
        """
        for item in self.pop:
            item.decode(self.solutionClassName)


    def getBestMakespan(self):
        """
        功能：       返回整个种群最好的makespan
        """
        return min([item.makespan for item in self.pop])


    def getMakespansOfAllIndividuals(self):
        """
        功能：       返回种群中所有个体的makespan，返回一个list
        """
        makespans = []
        for i in range(self.popSize):
            makespans.append(self.pop[i].makespan)

        return makespans


    def getBestIndividualIndex(self):
        """
        功能：       返回最优个体的序号
        """
        return self.getMakespansOfAllIndividuals().index(self.getBestMakespan())


    def getBestIndividualsIndexs(self, chooseNum):
        """
        功能：            返回最优的多个个体的序号

        输入：
        chooseNum  选出chooseNum个个体，例如可以是2,4等

        输出：
        indexs            一个list，包含部分个体在种群中的序号
        """
        # 先确定要选多少个个体
        # chooseNum = int(choosePercentage * self.popSize / 100.0)

        # 找出个体的序号
        makespanList = [self.pop[i].makespan for i in range(self.popSize)]
        indexs = getBestOrWorstIndexs('best', makespanList, chooseNum)

        return indexs


    def getBestIndividualCodes(self):
        """
        功能：        返回最优个体的sublotNum、sublotSizes、preferenceCode，都是以list的形式
        """
        # 找到最优个体的序号
        bestInd = self.getBestIndividualIndex()

        # 取出编码
        sublotNum = []
        sublotSizes = []
        preferenceCode = []
        for item in self.pop[bestInd].segment1.lotSplitingCode:
            sublotNum.append(item.sublotNum)
        for item in self.pop[bestInd].segment1.lotSplitingCode:
            sublotSizes.append(item.sublotSizes)
        preferenceCode = self.pop[bestInd].segment2.preferenceCode

        return sublotNum, sublotSizes, preferenceCode


    def iterate_old(self, iterNum, p1, p2, p3, ps1, ps2, ps3, ps4, ps5, needcalAllMakespan=1, muteEveryIter=0, muteResult=0,
                **kw):
        """
        版本信息：           版本一
        在tempPop的个体上轮盘赌选择两个个体交叉变异，在同一次迭代中，有个体会跟不同的个体交叉变异多次，有个体会得不到交叉变异，但依然保留在tempPop中
        这不符合原始GA的过程，所以才有了版本二

        功能：              简单GA迭代，可对同一个population对象连续使用
                            首次使用应把needcalAllMakespan设为1，后面应设为0以减少重复计算

        输入：
        iterNum             迭代次数
        p1                  交叉概率
        p2                  segment1变异概率
        p3                  segment2变异概率
        ps1~ps5             分别是segment1交叉位概率，segment2交叉位概率，segment1的vec内两sublot变异位概率，
                            segment1的vec重初始化位概率，segment2的vec内部swap变异位概率（注意：一个vec作为一位）
        needcalAllMakespan  在循环迭代之前是否需要计算全部个体的makespan，默认为1
        muteEveryIter       如果为0，打印每次迭代种群中最好makespan
        muteResult          如果为0，打印迭代结束后最好makespan

        可选输入：
        kw['startIter']     输出的迭代代数从此号码开始，如果不指定就从0开始
        kw['saveDetailsUsingDF']  是否把每一代的最好makespan都记录在一个DataFrame即self.details
        """
        # 第一代在此计算所有individual的makespan
        if needcalAllMakespan == 1:
            self.calAllMakespan()

        # 每次执行iterate都要清空这个DF
        self.details = pd.DataFrame(columns=['iter', 'bestMakespan'])

        # 开始迭代
        for iterInd in range(iterNum):

            # 计算轮盘list
            roulette = calRoulette([item.makespan for item in self.pop])

            # 创建self.pop的副本，下面对副本进行交叉变异的操作
            tempPop = copy.deepcopy(self.pop)

            # selectedInd = []

            # 随机选择两个个体进行segment1和segment2交叉
            for i in range(int(self.popSize / 2)):
                if (random.random() < p1):
                    pos1, pos2 = chooseTwoNumByRoulette(roulette)
                    tempPop[pos1].crossoverBetweenSegment1s(tempPop[pos2], ps1)  # 有50%的位进行交换
                    tempPop[pos1].crossoverBetweenSegment2s(tempPop[pos2], ps2)

            #         selectedInd.extend([pos1, pos2])
            # print(selectedInd)


            # 随机选择个体对segment1变异
            for item in tempPop:
                if (random.random() < p2):
                    if (random.random() < 0.5):
                        item.mutateSegment1WithTwoSublots(ps3)
                    else:
                        item.mutateSegment1WithNewVec(ps4)
            # 随机选择个体对segment2变异
            for item in tempPop:
                if (random.random() < p3):
                    if (random.random() < 0.5):
                        item.mutateSegment2WithinVecWithSwap(ps5)
                    else:
                        item.mutateSgment2BetweenTwoVecs()

            # 择优保留
            for item in tempPop:
                item.decode(self.solutionClassName)
            for i in range(self.popSize):
                if (tempPop[i].makespan < self.pop[i].makespan):
                    self.pop[i] = copy.deepcopy(tempPop[i])


            # 如果mute为0，才去打印每次迭代最好makespan
            if muteEveryIter == 0:
                if 'startIter' in kw.keys():
                    print('iter%d:' % (iterInd + kw['startIter']), self.getBestMakespan())
                else:
                    print('iter%d:' % (iterInd), self.getBestMakespan())

            # 如果saveDetailsUsingDF为1，那么把细节记录到成员变量self.details中
            if 'saveDetailsUsingDF' in kw.keys() and kw['saveDetailsUsingDF'] == 1:
                if 'startIter' in kw.keys():
                    self.details.loc[len(self.details)] = [iterInd + kw['startIter'], self.getBestMakespan()]
                else:
                    self.details.loc[len(self.details)] = [iterInd, self.getBestMakespan()]

                    #         if 'saveDetailsUsingDF' in kw.keys() and kw['saveDetailsUsingDF'] == 1:
                    #             self.details.set_index(["iter"], inplace=True)

        if muteResult == 0:
            print('result after %d iterations:' % iterNum, self.getBestMakespan())


    def iterate_old_git(self, iterNum, p1, p2, p3, ps1, ps2, ps3, ps4, ps5, needcalAllMakespan=1, muteEveryIter=0, muteResult=0,
                **kw):
        """
        功能：              简单GA迭代，可对同一个population对象连续使用
                            首次使用应把needcalAllMakespan设为1，后面应设为0以减少重复计算
        输入：
        iterNum             迭代次数
        p1                  交叉概率
        p2                  segment1变异概率
        p3                  segment2变异概率
        ps1~ps5             分别是segment1交叉位概率，segment2交叉位概率，segment1的vec内两sublot变异位概率，
                            segment1的vec重初始化位概率，segment2的vec内部swap变异位概率（注意：一个vec作为一位）
        needcalAllMakespan  在循环迭代之前是否需要计算全部个体的makespan，默认为1
        muteEveryIter       如果为0，打印每次迭代种群中最好makespan
        muteResult          如果为0，打印迭代结束后最好makespan
        可选输入：
        kw['startIter']     输出的迭代代数从此号码开始，如果不指定就从0开始
        kw['saveDetailsUsingDF']  是否把每一代的最好makespan都记录在一个DataFrame即self.details
        """
        # 第一代在此计算所有individual的makespan
        if needcalAllMakespan == 1:
            self.calAllMakespan()

        # 每次执行iterate都要清空这个DF
        self.details = pd.DataFrame(columns=['iter', 'bestMakespan'])

        # 开始迭代
        for iterInd in range(iterNum):

            # 计算轮盘list
            roulette = calRoulette([item.makespan for item in self.pop])

            # 创建self.pop的副本，下面对副本进行交叉变异的操作
            tempPop = copy.deepcopy(self.pop)

            # 随机选择两个个体进行segment1和segment2交叉
            for i in range(int(self.popSize / 2)):
                if (random.random() < p1):
                    pos1, pos2 = chooseTwoNumByRoulette(roulette)
                    tempPop[pos1].crossoverBetweenSegment1s(tempPop[pos2], ps1)  # 有50%的位进行交换
                    tempPop[pos1].crossoverBetweenSegment2s(tempPop[pos2], ps2)
            # 随机选择个体对segment1变异
            for item in tempPop:
                if (random.random() < p2):
                    if (random.random() < 0.5):
                        item.mutateSegment1WithTwoSublots(ps3)
                    else:
                        item.mutateSegment1WithNewVec(ps4)
            # 随机选择个体对segment2变异
            for item in tempPop:
                if (random.random() < p3):
                    if (random.random() < 0.5):
                        item.mutateSegment2WithinVecWithSwap(ps5)
                    else:
                        item.mutateSgment2BetweenTwoVecs()

            # 择优保留
            for item in tempPop:
                item.decode(self.solutionClassName)
            for i in range(self.popSize):
                if (tempPop[i].makespan < self.pop[i].makespan):
                    self.pop[i] = copy.deepcopy(tempPop[i])
                    #                     self.pop[i].makespan = tempPop[i].makespan

            # 如果mute为0，才去打印每次迭代最好makespan
            if muteEveryIter == 0:
                if 'startIter' in kw.keys():
                    print('iter%d:' % (iterInd + kw['startIter']), self.getBestMakespan())
                else:
                    print('iter%d:' % (iterInd), self.getBestMakespan())

            # 如果saveDetailsUsingDF为1，那么把细节记录到成员变量self.details中
            if 'saveDetailsUsingDF' in kw.keys() and kw['saveDetailsUsingDF'] == 1:
                if 'startIter' in kw.keys():
                    self.details.loc[len(self.details)] = [iterInd + kw['startIter'], self.getBestMakespan()]
                else:
                    self.details.loc[len(self.details)] = [iterInd, self.getBestMakespan()]

                    #         if 'saveDetailsUsingDF' in kw.keys() and kw['saveDetailsUsingDF'] == 1:
                    #             self.details.set_index(["iter"], inplace=True)

        if muteResult == 0:
            print('result after %d iterations:' % iterNum, self.getBestMakespan())




    def iterate(self, iterNum, p1, p2, p3, ps1, ps2, ps3, ps4, ps5, needcalAllMakespan=1, muteEveryIter=0,
                 muteResult=0, **kw):
        """
        功能：              简单GA迭代，可对同一个population对象连续使用
                            首次使用应把needcalAllMakespan设为1，后面应设为0以减少重复计算

        输入：
        iterNum             迭代次数
        p1                  交叉概率
        p2                  segment1变异概率
        p3                  segment2变异概率
        ps1~ps5             分别是segment1交叉位概率，segment2交叉位概率，segment1的vec内两sublot变异位概率，
                            segment1的vec重初始化位概率，segment2的vec内部swap变异位概率（注意：一个vec作为一位）
        needcalAllMakespan  在循环迭代之前是否需要计算全部个体的makespan，默认为1
        muteEveryIter       如果为0，打印每次迭代种群中最好makespan
        muteResult          如果为0，打印迭代结束后最好makespan

        可选输入：
        kw['startIter']     输出的迭代代数从此号码开始，如果不指定就从0开始
        kw['saveDetailsUsingDF']  是否把每一代的最好makespan都记录在一个DataFrame即self.details
        """
        progress = [0 for _ in range(iterNum)]

        # 第一代在此计算所有individual的makespan
        if needcalAllMakespan == 1:
            self.calAllMakespan()

        # 每次执行iterate都要清空这个DF
        self.details = pd.DataFrame(columns=['iter', 'bestMakespan'])

        # 开始迭代
        for iterInd in range(iterNum):

            # 构建父代的序号集，从上一代中选择个体，有以下五种方法
            # 1-无放回选择
            parentsIndexs = [i for i in range(self.popSize)]
            random.shuffle(parentsIndexs)
            # 2-有放回选择-轮盘赌
            # roulette = calRoulette([item.makespan for item in self.pop])  # 计算轮盘list
            # parentsIndexs = []
            # for i in range(int(self.popSize / 2)):
            #     parentsIndexs.extend(chooseTwoNumByRoulette(roulette))
            # 3-有放回选择-锦标赛
            # parentsIndexs = []
            # for i in range(int(self.popSize / 2)):
            #     parentsIndexs.extend(chooseTwoNumByTournament([item.makespan for item in self.pop], 3))
            # 4-有放回选择-随机选
            # parentsIndexs = []
            # for i in range(int(self.popSize / 2)):
            #     parentsIndexs.extend(chooseTwoNumByRandom(self.popSize - 1))
            # 5-有放回选择-线性排名轮盘赌
            # roulette = calRouletteWithRank([item.makespan for item in self.pop], 0.6)  # 计算轮盘list
            # parentsIndexs = []
            # for i in range(int(self.popSize / 2)):
            #     parentsIndexs.extend(chooseTwoNumByRoulette(roulette))

            # 随机选取parentsIndexs的两个位置，把上次迭代两个最优个体的序号替换进去
            # bestInd1, bestInd2 = self.getBestIndividualsIndexs(2)
            # replacePos1, replacePos2 = chooseTwoNumByRandom(self.popSize - 1)
            # parentsIndexs[replacePos1] = bestInd1
            # parentsIndexs[replacePos2] = bestInd2
            # 随机选取parentsIndexs的一个位置，把上次迭代最优个体的序号替换进去
            # bestInd = self.getBestIndividualsIndexs(1)[0]
            # replacePos = random.randint(0, self.popSize - 1)
            # parentsIndexs[replacePos] = bestInd

            # 由相邻父代两两生成子代
            newPop = []
            for i in range(int(self.popSize / 2)):
                # 找到两个父代个体，并copy给子代
                parent1 = self.pop[parentsIndexs[i * 2]]
                parent2 = self.pop[parentsIndexs[i * 2 + 1]]
                child1 = copy.deepcopy(parent1)
                child2 = copy.deepcopy(parent2)
                # 交叉
                if (random.random() < p1):
                    child1.crossoverBetweenSegment1s(child2, ps1)
                    child1.crossoverBetweenSegment2s(child2, ps2)
                # segment1变异
                for item in [child1, child2]:
                    if random.random() < p2:
                        if (random.random() < 0.5):
                            item.mutateSegment1WithTwoSublots(ps3)
                        else:
                            item.mutateSegment1WithNewVec(ps4)
                # segment2变异
                for item in [child1, child2]:
                    if random.random() < p3:
                        if (random.random() < 0.5):
                            item.mutateSegment2WithinVecWithSwap(ps5)
                        else:
                            item.mutateSgment2BetweenTwoVecs()
                # 计算两个子代个体的makespan
                for item in [child1, child2]:
                    item.decode(self.solutionClassName)
                # 子代与父代四个择优，最优两者放入newPop
                # parentsAndChildren = [parent1, parent2, child1, child2]
                # parentsAndChildrenMakespans = [item.makespan for item in parentsAndChildren]
                # betterIndividualIndexs = getBestOrWorstIndexs('best', parentsAndChildrenMakespans, 2)
                # newPop.extend([parentsAndChildren[ind] for ind in betterIndividualIndexs])
                # 子代父代两两择优
                if child1.makespan < parent1.makespan:
                    newPop.append(child1)
                    progress[iterInd] += 1
                else:
                    newPop.append(parent1)
                if child2.makespan < parent2.makespan:
                    newPop.append(child2)
                    progress[iterInd] += 1
                else:
                    newPop.append(parent2)

            # 将生成好的newPop深复制给pop
            self.pop = copy.deepcopy(newPop)
            # print(self.getMakespansOfAllIndividuals())

            # 如果mute为0，才去打印每次迭代最好makespan
            if muteEveryIter == 0:
                if 'startIter' in kw.keys():
                    print('iter%d:' % (iterInd + kw['startIter']), self.getBestMakespan())
                else:
                    print('iter%d:' % (iterInd), self.getBestMakespan())

            # 如果saveDetailsUsingDF为1，那么把细节记录到成员变量self.details中
            if 'saveDetailsUsingDF' in kw.keys() and kw['saveDetailsUsingDF'] == 1:
                if 'startIter' in kw.keys():
                    self.details.loc[len(self.details)] = [iterInd + kw['startIter'], self.getBestMakespan()]
                else:
                    self.details.loc[len(self.details)] = [iterInd, self.getBestMakespan()]

                    #         if 'saveDetailsUsingDF' in kw.keys() and kw['saveDetailsUsingDF'] == 1:
                    #             self.details.set_index(["iter"], inplace=True)

        if muteResult == 0:
            print('result after %d iterations:' % iterNum, self.getBestMakespan())
            # print(min(self.getMakespansOfAllIndividuals()))
            # print(self.getMakespansOfAllIndividuals())

        # 打印progress可以看到每个种群的每一代有多少个体在交叉变异种进步了
        # print(progress)



    def decodeAFixedIndividual(self, codeLists, filename):
        """
        功能：       输入三条编码，观察解码过程，并生成甘特图

        输入：
        codeLists    为一个list，里面放着三条编码
        filename     一个文件前缀名，例如'gantData'
        """
        sublotNum = codeLists[0]
        sublotSizes = codeLists[1]
        preferenceCode = codeLists[2]

        # 创建新个体，初始化，并赋值
        bestIndividual = self.individualClassName(lotNum, lotSizes, machineNum)
        bestIndividual.initializeIndividual()
        for i, item in enumerate(bestIndividual.segment1.lotSplitingCode):
            item.sublotNum = sublotNum[i]
            item.sublotSizes = sublotSizes[i]
        bestIndividual.segment2.preferenceCode = preferenceCode

        # 解码，生成甘特时间表
        solu = self.solutionClassName(bestIndividual)
        solu.run(mute=1)
        # solu.printResults()
        solu.generateGantTimetable(filename = "gantFiles\\" + filename)
        print('makespan: ', solu.getMakespan())

        # 绘制甘特图
        csvName = filename + '.csv'
        pngName = filename + '.png'
        drawGantChart(fromFilename = "gantFiles\\" + csvName, toFilename = "gantFiles\\" + pngName)
        print('gantChart figure', pngName, 'done: {}'.format(PATH + "\\gantFiles\\" + pngName))



