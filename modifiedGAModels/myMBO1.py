from generalPopulation import generalPopulation
from generalIndividual import generalIndividual
from generalSolution import generalSolution
from globalVariablesAndFunctions import *


# 构建原始单种群GA类：originalGA
class myMBO1(generalPopulation):
    """
    继承generalPopulation得到
    """

    def __init__(self, popSize, lotNum, lotSizes, machineNum):
        """
        指定了individual类是generalIndividual，solution类是generalSolution
        """
        super(myMBO1, self).__init__(popSize, lotNum, lotSizes, machineNum, generalIndividual, generalSolution)

        self.name = 'myMBO1'



    def iterate(self, iterNum, K, S, M, A, needcalAllMakespan=1, muteEveryIter=0, muteResult=0, **kw):
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
        kw['startIter']     输出的迭代代数从此号码开始，如果不指定就从0开始
        kw['saveDetailsUsingDF']  是否把每一代的最好makespan都记录在一个DataFrame即self.details

        注意：
        MBO的popsize一定要设为奇数
        """

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
            disturbedIndex = disturbList(sortedIndex, int(self.popSize * 0.15), int(self.popSize * 0.1))
            # 安排领头鸟，左右翼跟随鸟
            leaderind = disturbedIndex[0]
            del disturbedIndex[0]
            leftWingind = [disturbedIndex[i] for i in range(self.popSize -1) if i % 2 == 0]
            rightWingind = [disturbedIndex[i] for i in range(self.popSize -1) if i % 2 == 1]

            return leaderind, leftWingind, rightWingind


        progress = [0 for _ in range(iterNum)]

        # 第一代在此计算所有individual的makespan
        if needcalAllMakespan == 1:
            self.calAllMakespan()

        # 每次执行iterate都要清空这个DF
        self.details = pd.DataFrame(columns=['iter', 'bestMakespan'])

        # 构建模糊V字队形
        leaderInd, leftWingInd, rightWingInd = fuzzyVReshape()

        # for intervalInd in range(intervalNum):
        for intervalInd in range(int (iterNum / (M + A))):
            # 一轮interval开始，一轮interval包含iterNum个iter

            # 先针对当前队形进行iterInd次的更新
            for m in range(M):
                # 一次iter开始

                #重新计算iterNum
                iterInd = intervalInd * (M + A) + m

                # 先把整个种群deepcopy到newPop中，在newPop上操作
                newPop = copy.deepcopy(self.pop)

                # 领头鸟更新
                # 初始化领头鸟邻域集
                leaderNei = []
                leaderNeiMakespan = []
                # 先生成K个邻域解
                for _ in range(K):
                    tempBird = self.pop[leaderInd].neighbourSearch('random', 1, 1, self.solutionClassName, inplace = 0)
                    leaderNei.append(tempBird)
                    leaderNeiMakespan.append(tempBird.makespan)
                # 选出最好的邻域解，与领头鸟择优
                if min(leaderNeiMakespan) <= self.pop[leaderInd].makespan:
                    # 替换领头鸟
                    bestNeiInd = leaderNeiMakespan.index(min(leaderNeiMakespan))
                    bestNei = leaderNei[bestNeiInd]
                    newPop[leaderInd] = copy.deepcopy(bestNei)

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
                        for _ in range(S):
                            # 交叉得到两个子代
                            child1, child2 = self.pop[birdInd].crossoverBetweenBothSegments(learnedBird, 0.5, 0.5, inplace = 0)
                            children = [child1, child2]
                            # 计算完工时间
                            for item in children:
                                item.decode(self.solutionClassName)
                            childrenMakespan = [item.makespan for item in children]
                            # 选择较好的一个子代，放入邻域集
                            chosenChild = children[childrenMakespan.index(min(childrenMakespan))]
                            wingNei.append(chosenChild)
                            wingNeiMakespan.append(chosenChild.makespan)
                        # 生成该鸟的邻域解，加入邻域集
                        for _ in range(K - S):
                            tempBird = self.pop[birdInd].neighbourSearch('random', 1, 1, self.solutionClassName, inplace = 0)
                            wingNei.append(tempBird)
                            wingNeiMakespan.append(tempBird.makespan)
                        # 选出最好的邻域解，与该鸟择优
                        if min(wingNeiMakespan) <= self.pop[birdInd].makespan:
                            # 替换该鸟
                            bestNeiInd = wingNeiMakespan.index(min(wingNeiMakespan))
                            bestNei = wingNei[bestNeiInd]
                            newPop[birdInd] = copy.deepcopy(bestNei)

                # 一个iter完成，将生成好的newPop深复制给pop
                self.pop = copy.deepcopy(newPop)
                # print(self.getMakespansOfAllIndividuals())

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

                        #         if 'saveDetailsUsingDF' in kw.keys() and kw['saveDetailsUsingDF'] == 1:
                        #             self.details.set_index(["iter"], inplace=True)

            # 队形调整阶段
            for a in range(A):
                # 一次iter开始

                # 重新计算iterNum
                iterInd = intervalInd * (M + A) + M + a

                # 先把整个种群deepcopy到newPop中，在newPop上操作
                newPop = copy.deepcopy(self.pop)

                # 更新每一只鸟
                for birdInd in range(self.popSize):
                    # 先清空每一只鸟的邻域集
                    wingNei = []
                    wingNeiMakespan = []
                    # 确定要向哪一只鸟学习，随机选择
                    learnedBird = self.pop[random.randint(0, self.popSize - 1)]
                    # 交叉S次，分别挑最好的解加入邻域集
                    for _ in range(S):
                        # 交叉得到两个子代
                        child1, child2 = self.pop[birdInd].crossoverBetweenBothSegments(learnedBird, 0.5, 0.5, inplace=0)
                        children = [child1, child2]
                        # 计算完工时间
                        for item in children:
                            item.decode(self.solutionClassName)
                        childrenMakespan = [item.makespan for item in children]
                        # 选择较好的一个子代，放入邻域集
                        chosenChild = children[childrenMakespan.index(min(childrenMakespan))]
                        wingNei.append(chosenChild)
                        wingNeiMakespan.append(chosenChild.makespan)
                    # 生成该鸟的邻域解，加入邻域集
                    for _ in range(K - S):
                        tempBird = self.pop[birdInd].neighbourSearch('random', 1, 1, self.solutionClassName, inplace=0)
                        wingNei.append(tempBird)
                        wingNeiMakespan.append(tempBird.makespan)
                    # 选出最好的邻域解，与该鸟择优
                    if min(wingNeiMakespan) <= self.pop[birdInd].makespan:
                        # 替换该鸟
                        bestNeiInd = wingNeiMakespan.index(min(wingNeiMakespan))
                        bestNei = wingNei[bestNeiInd]
                        newPop[birdInd] = copy.deepcopy(bestNei)

            # 变换队形，重新构建模糊V字队形
            leaderInd, leftWingInd, rightWingInd = fuzzyVReshape()

            # 变换队形，把领头鸟退到队尾
            # if newPop[leftWingInd[0]].makespan < newPop[rightWingInd[0]].makespan:
            #     leftWingInd.append(leaderInd)
            #     leaderInd = leftWingInd[0]
            #     del leftWingInd[0]
            # else:
            #     rightWingInd.append(leaderInd)
            #     leaderInd = rightWingInd[0]
            #     del rightWingInd[0]

        if muteResult == 0:
            print('result after %d iterations:' % iterNum, self.getBestMakespan())
            # print(min(self.getMakespansOfAllIndividuals()))
            # print(self.getMakespansOfAllIndividuals())

        # 打印progress可以看到每个种群的每一代有多少个体在交叉变异种进步了
        # print(progress)



# test = myMBO1(51, lotNum, lotSizes, machineNum)
# test.iterate(30, 3, 1, 8, 2, needcalAllMakespan=1, muteEveryIter=0, muteResult=0, startIter=0, saveDetailsUsingDF=1)

# test.getBestIndividualCodes()
# test.getMakespansOfAllIndividuals()