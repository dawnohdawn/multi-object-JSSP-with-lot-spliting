from generalGAModel import generalGAModel
from generalIndividual import generalIndividual
from generalPopulation import generalPopulation
from generalSolution import generalSolution
from globalVariablesAndFunctions import *


# 构建原始IMGA类：
class NIMGA(generalGAModel):
    """
    继承generalGAModel得到
    来自An effective new island model genetic algorithm for job shop scheduling problem
    """

    def __init__(self, popSize, lotNum, lotSizes, machineNum):
        """
        指定了individual类是generalIndividual，pop类是generalPopulation，solution类是generalSolution
        """
        super(NIMGA, self).__init__(3, popSize, lotNum, lotSizes, machineNum, generalIndividual, \
                                           generalPopulation, generalSolution)

        self.name = 'NIMGA'


    def getXthWorstIndividualOfPopulation(self, popInd, X):
        """
        功能：            返回某个种群第X差的个体在种群中的序号

        输入：
        popInd            种群序号
        X                 第X差，从0开始数

        输出：
        indexs            一个list，在种群中的序号
        """
        makespanList = [item.makespan for item in self.model[popInd].pop]
        sortedMakespanList = sorted(makespanList, reverse=True)
        indexs = [makespanList.index(sortedMakespanList[X])]

        return indexs


    def migrationOfAllPops(self, migrateIndex):
        """
        功能:              所有种群进行迁移，用replace

        输入：
        migrateIndex       第几次执行migrate，从0开始数
        """
        makespanLists = [[item.makespan for item in self.model[i].pop] for i in range(3)]
        replaceIndvidual = [\
            copy.deepcopy(self.model[2].pop[self.getXthWorstIndividualOfPopulation(2, migrateIndex % self.popSize)[0]]), \
            copy.deepcopy(self.model[0].pop[self.getXthWorstIndividualOfPopulation(0, migrateIndex % self.popSize)[0]]), \
            copy.deepcopy(self.model[1].pop[self.getXthWorstIndividualOfPopulation(1, migrateIndex % self.popSize)[0]])]
        replacedIndexs = [ \
            self.getXthWorstIndividualOfPopulation(0, 0)[0], \
            self.getXthWorstIndividualOfPopulation(1, 0)[0], \
            self.getXthWorstIndividualOfPopulation(2, 0)[0]]
        self.model[0].pop[replacedIndexs[0]] = replaceIndvidual[0]
        self.model[1].pop[replacedIndexs[1]] = replaceIndvidual[1]
        self.model[2].pop[replacedIndexs[2]] = replaceIndvidual[2]


    def modelIterate(self, iterNum, p1, p2, p3, \
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
        outerIterInd = -1
        iterInd = -1

        while(iterInd < iterNum):

            outerIterInd += 1

            migrateFlag = 0
            old_bestMakespansOfEveryPop = self.getBestMakespanOfEveryPop()
            innerIterInd = -1
            notChangeTimes = 0

            # 内部迭代
            while(migrateFlag == 0 and iterInd < iterNum):

                innerIterInd += 1
                iterInd += 1

                # 每个pop进行一次iter
                for popInd in range(self.modelSize):
                    # GA
                    if 'saveDetailsUsingDF' in kw.keys() and kw['saveDetailsUsingDF'] == 1:
                        saveDetailsUsingDF = kw['saveDetailsUsingDF']
                        self.model[popInd].iterate_NIMGA(popInd, 1, p1, p2, p3, needcalAllMakespan=0, \
                                               muteEveryIter=1, muteResult=muteEveryGAIter, \
                                               startIter=iterInd, \
                                               saveDetailsUsingDF=saveDetailsUsingDF)
                    # 记录到dataframe里
                    if 'saveDetailsUsingDF' in kw.keys() and kw['saveDetailsUsingDF'] == 1:
                        self.model[popInd].details['pop'] = popInd
                        self.model[popInd].details['outerIter'] = iterInd
                        self.detailsOfModel = self.detailsOfModel.append(self.model[popInd].details, ignore_index=True)

                if muteGAResult == 0:
                    print('Iter: %d' % iterInd, self.getBestMakespanAmongAllPops(),
                          self.getBestMakespanOfEveryPop())

                # 判断这三个种群多久没有变化了
                if old_bestMakespansOfEveryPop == self.getBestMakespanOfEveryPop():
                    notChangeTimes += 1
                else:
                    notChangeTimes = 0
                old_bestMakespansOfEveryPop = self.getBestMakespanOfEveryPop()

                # 判断是否需要migrate了
                if notChangeTimes >= 9:
                    migrateFlag = 1
                    print('not chage for 10 iters')

            # 迁移
            self.migrationOfAllPops(outerIterInd)
            print('migrate done!！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！')

            # 打印完整外部迭代一代后的结果
            if muteEveryOuterIter == 0:
                print('after migrate: %d' % outerIterInd, self.getBestMakespanAmongAllPops(),
                      self.getBestMakespanOfEveryPop())

        if muteOuterResult == 0:
            print('result after {num1} outerIteration which is {num3} in total:'. \
                  format(num1=outerIterInd, num3=iterNum), \
                  self.getBestMakespanAmongAllPops())
        # 整理一下这个dataframe
        if 'saveDetailsUsingDF' in kw.keys() and kw['saveDetailsUsingDF'] == 1:
            self.detailsOfModel = self.detailsOfModel.groupby(['iter']).min()


# NIMGATest = NIMGA(18, lotNum, lotSizes, machineNum)
# NIMGATest.modelIterate(500, 0.8, 0.5, 0.5, muteEveryGAIter = 1,  \
#                        muteGAResult = 0, muteEveryOuterIter = 0, muteOuterResult = 0, saveDetailsUsingDF = 1)







