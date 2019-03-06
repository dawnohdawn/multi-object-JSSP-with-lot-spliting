from generalPopulation import generalPopulation
from generalIndividual import generalIndividual
from generalSolution import generalSolution
from globalVariablesAndFunctions import *


# 构建原始单种群GA类：originalGA
class HGA(generalPopulation):
    """
    继承generalPopulation得到
    """

    def __init__(self, popSize, lotNum, lotSizes, machineNum):
        """
        指定了individual类是generalIndividual，solution类是generalSolution
        """
        super(HGA, self).__init__(popSize, lotNum, lotSizes, machineNum, generalIndividual, generalSolution)

        self.name = 'HGA'


    def iterate(self, iterNum, p1, p2, needcalAllMakespan=1, muteEveryIter=0, muteResult=0, **kw):
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

            # 轮盘赌选择父代
            roulette = calRoulette([item.makespan for item in self.pop])  # 计算轮盘list
            parentsIndexs = []
            for i in range(int(self.popSize / 2)):
                parentsIndexs.extend(chooseTwoNumByRoulette(roulette))

            # 由相邻父代两两生成子代
            newPop = []
            for i in range(int(self.popSize / 2)):
                # 找到两个父代个体，并copy给子代
                parent1 = self.pop[parentsIndexs[i * 2]]
                parent2 = self.pop[parentsIndexs[i * 2 + 1]]
                child1 = copy.deepcopy(parent1)
                child2 = copy.deepcopy(parent2)
                # 交叉
                if random.random() < p1:
                    child1.crossoverBetweenSegment1s(child2, 0.5)
                    child1.crossoverBetweenSegment2sWithPOX(child2, 0.5)
                # 变异
                for item in [child1]:
                    if random.random() < p2:
                        item.reinitializeAlotSplitingVec()
                        item.neighbourSwapTwoLotsOfAMachine()
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




# HGATest = HGA(51, lotNum, lotSizes, machineNum)
# HGATest.iterate(1000, 0.8, 0.5, needcalAllMakespan=1, muteEveryIter=0, muteResult=0)
