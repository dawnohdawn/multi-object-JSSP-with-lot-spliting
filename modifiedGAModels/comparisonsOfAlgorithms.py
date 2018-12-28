from generalPopulation import generalPopulation
from generalGAModel import generalGAModel
from globalVariablesAndFunctions import *

class comparisonsOfAlgorithms:
    """
    专门构建一个类来做算法对比实验
    有多种功能
    """

    def __init__(self, algorithms):

        """
        输入：         几个算法类的对象组成的list
        """
        self.algorithms = algorithms
        self.algorithmNum = len(algorithms)

        # 构建一个dataframe，记录每次run各个算法的最后结果
        self.columnNames = []
        for algorithmInd in range(self.algorithmNum):
            self.columnNames.append(
                '%s' % (str(type(self.algorithms[algorithmInd])).strip('>').strip('\'').split('.')[-1]))
        self.makespans = pd.DataFrame(columns=self.columnNames)

        # 构建一个list，记录每run的最优个体的编码
        self.bestCodes = []

        # 构建一个dataframe，记录单次运行的收敛过程
        self.oneRunData = pd.DataFrame(columns=self.columnNames)

    def runManyTimes(self, runNum, restart=1):
        """
        功能：        传入的多个算法，跑runNum遍
        """
        # 如果restart为0的话，不用清空历史记录和历史最优编码
        if restart == 1:
            self.makespans = pd.DataFrame(columns=self.columnNames)
            self.bestCodes = []

        # 开始循环run
        for runInd in range(runNum):
            # 开始循环每个算法
            makespansOfThisRun = []
            for algorithmInd in range(self.algorithmNum):
                # 注意不同的对象要使用不同的操作
                if type(self.algorithms[algorithmInd]).__bases__[0] == generalPopulation:
                    # 除了第一次run不用reset model之外，其他run都要
                    if runInd != 0:
                        self.algorithms[algorithmInd].resetPop()
                    self.algorithms[algorithmInd].iterate(1000, 0.5, 0.5, 0.5, 0.5, 0.5, 0.3, 0.3, 0.3,
                                                          needCalAllMakespan=1, \
                                                          muteEveryIter=1, muteResult=0, startIter=0,
                                                          saveDetailsUsingDF=1)
                    makespansOfThisRun.append(self.algorithms[algorithmInd].getBestMakespan())
                    self.bestCodes.append([self.algorithms[algorithmInd].getBestMakespan(),
                                           self.algorithms[algorithmInd].getBestIndividualCodes()])
                elif type(self.algorithms[algorithmInd]).__bases__[0] == generalGAModel:
                    # 除了第一次run不用reset model之外，其他run都要
                    if runInd != 0:
                        self.algorithms[algorithmInd].resetModel()
                    self.algorithms[algorithmInd].modelIterate(100, 10, 0.5, 0.5, 0.5, 0.5, 0.5, 0.3, 0.3, 0.3,
                                                               'exchange', 10, \
                                                               muteEveryGAIter=1, muteGAResult=1, muteEveryOuterIter=1, \
                                                               muteOuterResult=0, saveDetailsUsingDF=1)
                    makespansOfThisRun.append(self.algorithms[algorithmInd].getBestMakespanAmongAllPops())
                    self.bestCodes.append([self.algorithms[algorithmInd].getBestMakespanAmongAllPops(),
                                           self.algorithms[algorithmInd].getBestIndividualCodes()])
            self.makespans.loc[len(self.makespans)] = makespansOfThisRun


    def saveMakespansDF(self, filename):
        """
        功能          把makespans存到csv
        """
        self.makespans.to_csv(PATH + "\\" + filename, header=True)


    def plotOneRun(self, fileName, restart=1):
        """
        功能：        记录各个算法一次run的收敛过程
        """
        # 如果restart为0的话，不用清空历史记录
        if restart == 1:
            self.oneRunData = pd.DataFrame(columns=self.columnNames)

        for algorithmInd in range(self.algorithmNum):

            if type(self.algorithms[algorithmInd]).__bases__[0] == generalPopulation:
                self.algorithms[algorithmInd].iterate(200, 0.5, 0.5, 0.5, 0.5, 0.5, 0.3, 0.3, 0.3, needCalAllMakespan=1, \
                                                      muteEveryIter=1, muteResult=0, startIter=0, saveDetailsUsingDF=1)
                self.oneRunData[self.columnNames[algorithmInd]] = self.algorithms[algorithmInd].details. \
                    set_index(["iter"])['bestMakespan']
            elif type(self.algorithms[algorithmInd]).__bases__[0] == generalGAModel:
                self.algorithms[algorithmInd].modelIterate(20, 10, 0.5, 0.5, 0.5, 0.5, 0.5, 0.3, 0.3, 0.3, 'exchange',
                                                           10, \
                                                           muteEveryGAIter=1, muteGAResult=1, muteEveryOuterIter=1, \
                                                           muteOuterResult=0, saveDetailsUsingDF=1)
                self.oneRunData[self.columnNames[algorithmInd]] = self.algorithms[algorithmInd].detailsOfModel[
                    "bestMakespan"]

        self.oneRunData.plot()
        plt.savefig(PATH + "\\" + fileName, dpi=160)
        plt.show()
        print('figure saved as %s !' % fileName)
