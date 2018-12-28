from globalVariablesAndFunctions import *
PATH = os.path.abspath('.')


# 多种群模型类
class generalGAModel:
    """
    成员变量：
    self.modelSize       有多少个island（种群）
    self.popSize         每个种群有多少个individual
    self.lotNum          有多少个lot
    self.lotSizes        list，每个lot有多少个工件
    self.machineNum      有多少台机器
    self.model           list，由self.modleSize个pop类组成
    self.detailsOfModel  记录每一代每一个种群的最好个体的makespan，行数=种群个数*innerIterNum*OuterIterNum
    self.individualClassName  使用哪个individual类
    self.popClassName    使用哪个pop类
    self.solutionClassName  使用哪个solution类
    """

    def __init__(self, modelSize, popSize, lotNum, lotSizes, machineNum, individualClassName, popClassName,
                 solutionClassName):
        self.modelSize = modelSize
        self.popSize = popSize
        self.lotNum = lotNum
        self.lotSizes = lotSizes
        self.machineNum = machineNum
        self.individualClassName = individualClassName
        self.popClassName = popClassName
        self.solutionClassName = solutionClassName

        self.model = [
            self.popClassName(self.popSize, self.lotNum, self.lotSizes, self.machineNum, self.individualClassName, \
                              self.solutionClassName) for i in range(self.modelSize)]

        self.detailsOfModel = pd.DataFrame(columns=['pop', 'iter', 'outerIter', 'bestMakespan'])


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


    def getBestIndividualCodes(self):
        """
        功能：        返回最优个体的sublotNum、sublotSizes、preferenceCode，都是以list的形式
        """
        # 找到最优个体的序号
        bestPopInd, bestIndiInd = self.getBestIndexOfAllPops()

        return self.model[bestPopInd].getBestIndividualCodes()


    def getCertainIndividualOfPopulation(self, popInd, mode, choosePercentage):
        """
        功能：            返回某个种群部分个体在种群中的序号

        输入：
        popInd            种群序号
        mode              选择模式，可以是'best','worst',random'
        choosePercentage  选出choosePercentage%个个体，例如可以是10，30等

        输出：
        indexs            一个list，包含部分个体在种群中的序号
        """
        # 先确定要选多少个个体
        chooseNum = int(choosePercentage * self.popSize / 100.0)

        # 找出个体的索引
        if mode == 'best':
            makespanList = [self.model[popInd].pop[i].makespan for i in range(self.popSize)]
            indexs = getBestOrWorstIndexs(mode, makespanList, chooseNum)
        elif mode == 'worst':
            makespanList = [self.model[popInd].pop[i].makespan for i in range(self.popSize)]
            indexs = getBestOrWorstIndexs(mode, makespanList, chooseNum)
        elif mode == 'random':
            indexs = random.sample(range(self.popSize), chooseNum)

        return indexs


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
        elif mode == 'exchange':
            for i in range(len(individualIndexs1)):
                self.model[popIndex1].pop[individualIndexs1[i]], self.model[popIndex2].pop[individualIndexs2[i]] = \
                    self.model[popIndex2].pop[individualIndexs2[i]], self.model[popIndex1].pop[individualIndexs1[i]]


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
            migrateIndexs.append(
                [self.getCertainIndividualOfPopulation(i, mode='best', choosePercentage=choosePercentage), \
                 self.getCertainIndividualOfPopulation(i, mode='worst', choosePercentage=choosePercentage)])

        # 三个种群按照0-1,1-2,2-0的顺序migration
        for i in range(self.modelSize):
            fromPop = i
            toPop = (i + 1) % self.modelSize
            self.migrateBetweenTwoPops(mode, fromPop, toPop, migrateIndexs[fromPop][0], migrateIndexs[toPop][1])


    def modelIterate(self, outerIterNum, innerIterNum, p1, p2, p3, ps1, ps2, ps3, ps4, ps5, mode, migratePercentage, \
                     muteEveryGAIter=1, muteGAResult=1, muteEveryOuterIter=0, muteOuterResult=0, **kw):

        """
        功能：                      使用简单GA迭代来构建IMGA的迭代

        输入：
        outerIterNum                模型要进行多少次migrate
        innerIterNum                每多少个iter就要migrate一次
        p1                          交叉概率
        p2                          segment1变异概率
        p3                          segment2变异概率
        ps1~ps5                     分别是segment1交叉位概率，segment2交叉位概率，segment1的vec内两sublot变异位概率，
                                    segment1的vec重初始化位概率，segment2的vec内部swap变异位概率（注意：一个vec作为一位）
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

        # 外部迭代
        for outerIterInd in range(outerIterNum):

            # 内部迭代
            for popInd in range(self.modelSize):
                # GA
                if 'saveDetailsUsingDF' in kw.keys() and kw['saveDetailsUsingDF'] == 1:
                    saveDetailsUsingDF = kw['saveDetailsUsingDF']
                self.model[popInd].iterate(innerIterNum, p1, p2, p3, ps1, ps2, ps3, ps4, ps5, needcalAllMakespan=0, \
                                           muteEveryIter=muteEveryGAIter, muteResult=muteGAResult, \
                                           startIter=outerIterInd * innerIterNum, \
                                           saveDetailsUsingDF=saveDetailsUsingDF)
                # 记录到dataframe里
                if 'saveDetailsUsingDF' in kw.keys() and kw['saveDetailsUsingDF'] == 1:
                    self.model[popInd].details['pop'] = popInd
                    self.model[popInd].details['outerIter'] = outerIterInd
                    self.detailsOfModel = self.detailsOfModel.append(self.model[popInd].details, ignore_index=True)
                    #                     self.detailsOfModel = pd.concat([self.detailsOfModel, self.model[popInd].details], ignore_index=True)

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

