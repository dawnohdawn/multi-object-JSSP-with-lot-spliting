from globalVariablesAndFunctions import *
from generalIndividual import generalIndividual
from generalPopulation import  generalPopulation
from generalSolution import generalSolution
from generalGAModel import generalGAModel
from comparisonsOfAlgorithms import comparisonsOfAlgorithms
from originalGA import originalGA
from originalIMGA import originalIMGA
from threeIMGA import threeIMGA
from mainTest2 import originalGAII



class threeIMGAII(generalGAModel):

    def __init__(self, popSize, lotNum, lotSizes, machineNum):
        """
        指定了modelSize是3，individual类是generalIndividual，pop类是generalPopulation，solution类是generalSolution
        """
        super(threeIMGAII, self).__init__(3, popSize, lotNum, lotSizes, machineNum, generalIndividual, originalGAII, generalSolution)


    def getBestAndRamdomIndividualOfPopulation(self, popInd, choosePercentage):
        """
        功能：            返回某个种群最优和随机的个体

        输入：
        popInd            种群序号
        choosePercentage  最优个体和随机个体分别需要多少个
        """
        # 先确定分别要选多少个best和random个体
        chooseNum = int(choosePercentage * self.popSize / 100.0)

        # 选出最好的个体
        makespanList = [self.model[popInd].pop[i].makespan for i in range(self.popSize)]
        bestIndexs = getBestOrWorstIndexs('best', makespanList, chooseNum)

        # 从剩余个体中选出随机个体
        randomPool = [i for i in range(self.popSize) if i not in bestIndexs]
        randomIndexs = random.sample(randomPool, chooseNum)

        return bestIndexs, randomIndexs

    def getTwoGroupsOfBestIndividual(self, popInd, choosePercentage):
        """
        功能:             返回两组最优个体，随机分组
        输入：
        popInd            种群序号
        choosePercentage  最优个体和随机个体分别需要多少个
        """
        # 先确定分别要选多少个best和random个体
        chooseNum = int(choosePercentage * self.popSize / 100.0)

        # 选出最好的个体
        makespanList = [self.model[popInd].pop[i].makespan for i in range(self.popSize)]
        bestIndexs = getBestOrWorstIndexs('best', makespanList, chooseNum * 2)

        # 随机分成两组
        random.shuffle(bestIndexs)
        bestIndexs1 = bestIndexs[:chooseNum]
        bestIndexs2 = bestIndexs[chooseNum:]

        return bestIndexs1, bestIndexs2

    def migrationOfAllPops(self, mode, choosePercentage):
        """
        功能:              所有种群进行迁移

        输入：
        mode               模式，可以是'replace'，或者是'exchange'
        choosePercentage   选出choosePercentage%个个体，例如可以是10，30等
        """
        pop0Best, pop0Random = self.getBestAndRamdomIndividualOfPopulation(0, choosePercentage=choosePercentage)
        pop1Best, pop1Random = self.getBestAndRamdomIndividualOfPopulation(1, choosePercentage=choosePercentage)
        pop2Best1, pop2Best2 = self.getTwoGroupsOfBestIndividual(2, choosePercentage=choosePercentage)

        self.migrateBetweenTwoPops(mode, 0, 1, pop0Best, pop1Best)
        self.migrateBetweenTwoPops(mode, 0, 2, pop0Random, pop2Best1)
        self.migrateBetweenTwoPops(mode, 1, 2, pop1Random, pop2Best2)

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

                # 三个种群有不同的进化参数
                if popInd == 0:
                    # self.model[popInd].iterate(innerIterNum, p1, p2, 0, ps1, 0, ps3, ps4, ps5, needcalAllMakespan=0, \
                    #                            muteEveryIter=muteEveryGAIter, muteResult=muteGAResult, \
                    #                            startIter=outerIterInd * innerIterNum, \
                    #                            saveDetailsUsingDF=saveDetailsUsingDF)
                    self.model[popInd].iterate(innerIterNum, p1, p2, p3, ps1, ps2, ps3, ps4, ps5, needcalAllMakespan=0, \
                                               muteEveryIter=muteEveryGAIter, muteResult=muteGAResult, \
                                               startIter=outerIterInd * innerIterNum, \
                                               saveDetailsUsingDF=saveDetailsUsingDF, \
                                               neighbourType = 's1')
                elif popInd == 1:
                    # self.model[popInd].iterate(innerIterNum, p1, 0, p3, 0, ps2, ps3, ps4, ps5, needcalAllMakespan=0, \
                    #                            muteEveryIter=muteEveryGAIter, muteResult=muteGAResult, \
                    #                            startIter=outerIterInd * innerIterNum, \
                    #                            saveDetailsUsingDF=saveDetailsUsingDF)
                    self.model[popInd].iterate(innerIterNum, p1, p2, p3, ps1, ps2, ps3, ps4, ps5, needcalAllMakespan=0, \
                                               muteEveryIter=muteEveryGAIter, muteResult=muteGAResult, \
                                               startIter=outerIterInd * innerIterNum, \
                                               saveDetailsUsingDF=saveDetailsUsingDF, \
                                               neighbourType='s2')
                elif popInd == 2:
                    self.model[popInd].iterate(innerIterNum, p1, p2, p3, ps1, ps2, ps3, ps4, ps5, needcalAllMakespan=0, \
                                               muteEveryIter=muteEveryGAIter, muteResult=muteGAResult, \
                                               startIter=outerIterInd * innerIterNum, \
                                               saveDetailsUsingDF=saveDetailsUsingDF, \
                                               neighbourType='random')

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





# test = threeIMGA(40, lotNum, lotSizes, machineNum)
test = threeIMGAII(40, lotNum, lotSizes, machineNum)

for i in range(10):
    print('outeriter', i)
    test.modelIterate(5, 10, 0.8, 0.3, 0.3, 0.4, 0.4, 0.3, 0.3, 0.3, 'exchange', 10, muteEveryGAIter = 1,  muteGAResult = 1, \
                      muteEveryOuterIter = 0, muteOuterResult = 0, saveDetailsUsingDF = 1)
    for item in test.getMakespansOfAllIndividuals():
        print(item)
    # test.model[0].decodeAFixedIndividual(test.getBestIndividualCodes(), 'gant-outerIter-%d'%i)



# print('构建')
# threeIMGATest = threeIMGA(4, lotNum, lotSizes, machineNum)
# threeIMGAIITest = threeIMGAII(4, lotNum, lotSizes, machineNum)
# test = comparisonsOfAlgorithms([threeIMGATest, threeIMGAIITest])
# test = comparisonsOfAlgorithms([threeIMGAIITest])
#
#
# print('算法各自跑多遍')
# test.runManyTimes(2)
# print(test.makespans.head())
# print(' ')