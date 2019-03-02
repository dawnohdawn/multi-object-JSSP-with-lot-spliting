from generalPopulation import generalPopulation
from generalIndividual import generalIndividual
from generalSolution import generalSolution
from globalVariablesAndFunctions import *


# 构建原始单种群GA类：originalGA
class originalMBO(generalPopulation):
    """
    继承generalPopulation得到
    """

    def __init__(self, popSize, lotNum, lotSizes, machineNum):
        """
        指定了individual类是generalIndividual，solution类是generalSolution
        """
        super(originalMBO, self).__init__(popSize, lotNum, lotSizes, machineNum, generalIndividual, generalSolution)

        self.name = 'originalMBO'


    def iterate(self, iterNum, K, S, M, needcalAllMakespan=1, muteEveryIter=0, muteResult=0, **kw):
        """
        功能：              简单GA迭代，可对同一个population对象连续使用
                            首次使用应把needcalAllMakespan设为1，后面应设为0以减少重复计算

        输入：
        iterNum             迭代次数
        K                   the number of neighbor solutions to be considered
        S                   the number of neighbor solutions to be shared with the next solution
        M                   number of tours
        needcalAllMakespan  在循环迭代之前是否需要计算全部个体的makespan，默认为1
        muteEveryIter       如果为0，打印每次迭代种群中最好makespan
        muteResult          如果为0，打印迭代结束后最好makespan

        可选输入：
        kw['startIter']     输出的迭代代数从此号码开始，如果不指定就从0开始
        kw['saveDetailsUsingDF']  是否把每一代的最好makespan都记录在一个DataFrame即self.details

        注意：
        MBO的popsize一定要设为奇数
        """
        progress = [0 for _ in range(iterNum)]

        # 第一代在此计算所有individual的makespan
        if needcalAllMakespan == 1:
            self.calAllMakespan()

        # 每次执行iterate都要清空这个DF
        self.details = pd.DataFrame(columns=['iter', 'bestMakespan'])

        # 构建V字队形
        leaderInd = random.randint(0, self.popSize - 1)  # 领头鸟
        leftWingInd = []  # 左翼序号
        rightWingInd = []  # 右翼序号
        followerInd = list(range(self.popSize))  # 左右翼可选的序号
        followerInd.remove(leaderInd)
        random.shuffle(followerInd)
        for i in range(int(len(followerInd) / 2)):
            leftWingInd.append(followerInd[2 * i])
            rightWingInd.append(followerInd[2 * i + 1])

        # for intervalInd in range(intervalNum):
        for intervalInd in range(int (iterNum / M)):
            # 一轮interval开始，一轮interval包含iterNum个iter

            # 先针对当前队形进行iterInd次的更新
            for m in range(M):
                # 一次iter开始

                #重新计算iterNum
                iterInd = intervalInd * M + m

                # 先把整个种群deepcopy到newPop中，在newPop上操作
                newPop = copy.deepcopy(self.pop)

                # 领头鸟更新
                # 初始化领头鸟邻域集
                leaderNei = []
                leaderNeiMakespan = []
                # 先生成K个邻域解
                for _ in range(K):
                    tempBird = self.pop[leaderInd].neighbourSearch('random_simple', 1, 1, self.solutionClassName, inplace = 0)
                    leaderNei.append(tempBird)
                    leaderNeiMakespan.append(tempBird.makespan)
                # 选出最好的邻域解，与领头鸟择优
                if min(leaderNeiMakespan) <= self.pop[leaderInd].makespan:
                    # 替换领头鸟
                    bestNeiInd = leaderNeiMakespan.index(min(leaderNeiMakespan))
                    bestNei = leaderNei[bestNeiInd]
                    newPop[leaderInd] = copy.deepcopy(bestNei)
                    # 删除替换的鸟，更新领头鸟邻域集以备跟随鸟使用
                    del leaderNei[bestNeiInd]
                    del leaderNeiMakespan[bestNeiInd]

                # 左右翼跟随鸟更新
                for wingInd in [leftWingInd, rightWingInd]:
                    for birdInd in wingInd:
                        # 如果是第一只跟随鸟，就从领头鸟那里获得邻域解
                        if birdInd == wingInd[0]:
                            # 初始化跟随鸟邻域集，找出领头鸟最好的S个邻域解，加入邻域集
                            bestAheadInd = getBestOrWorstIndexs('best', leaderNeiMakespan, S)
                            wingNei = [leaderNei[i] for i in bestAheadInd]
                            wingNeiMakespan = [leaderNeiMakespan[i] for i in bestAheadInd]
                        # 生成该鸟的邻域解，加入邻域集
                        for _ in range(K - S):
                            tempBird = self.pop[birdInd].neighbourSearch('random_simple', 1, 1, self.solutionClassName, inplace = 0)
                            wingNei.append(tempBird)
                            wingNeiMakespan.append(tempBird.makespan)
                        # 选出最好的邻域解，与该鸟择优
                        if min(wingNeiMakespan) <= self.pop[birdInd].makespan:
                            # 替换该鸟
                            bestNeiInd = wingNeiMakespan.index(min(wingNeiMakespan))
                            bestNei = wingNei[bestNeiInd]
                            newPop[birdInd] = copy.deepcopy(bestNei)
                            # 删除替换的鸟，更新邻域集以备下一只鸟使用
                            del wingNei[bestNeiInd]
                            del wingNeiMakespan[bestNeiInd]
                            # 将邻域解最好的S个解保留，其他删掉
                            bestAheadInd = getBestOrWorstIndexs('best', wingNeiMakespan, S)
                            wingNei = [i for j, i in enumerate(wingNei) if j in bestAheadInd]
                            wingNeiMakespan = [i for j, i in enumerate(wingNeiMakespan) if j in bestAheadInd]

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

            # 变换队形，把领头鸟退到队尾
            if newPop[leftWingInd[0]].makespan < newPop[rightWingInd[0]].makespan:
                leftWingInd.append(leaderInd)
                leaderInd = leftWingInd[0]
                del leftWingInd[0]
            else:
                rightWingInd.append(leaderInd)
                leaderInd = rightWingInd[0]
                del rightWingInd[0]

        if muteResult == 0:
            print('result after %d iterations:' % iterNum, self.getBestMakespan())
            # print(min(self.getMakespansOfAllIndividuals()))
            # print(self.getMakespansOfAllIndividuals())

        # 打印progress可以看到每个种群的每一代有多少个体在交叉变异种进步了
        # print(progress)



# test = originalMBO(51, lotNum, lotSizes, machineNum)
# test.iterate(40, 3, 1, 10, needcalAllMakespan=1, muteEveryIter=0, muteResult=0, startIter=0, saveDetailsUsingDF=1)

# test.getBestIndividualCodes()
# test.getMakespansOfAllIndividuals()
