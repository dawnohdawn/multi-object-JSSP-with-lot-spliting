from generalPopulation import generalPopulation
from generalIndividual import generalIndividual
from generalSolution import generalSolution
from globalVariablesAndFunctions import *


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



        # 定义aging几个阈值
        # agingThreshold = [20, 40, 50]
        agingThreshold = [10, 30, 40]
        # print('agingThreshold:', agingThreshold)


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
                    return [2, 2]


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

        # 记录每个个体的进化历史
        self.history = [[] for _ in range(self.popSize)]

        # 构建模糊V字队形
        leaderInd, leftWingInd, rightWingInd = fuzzyVReshape()
        # leaderInd, leftWingInd, rightWingInd = VInitial()

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
                if(iterInd % 1 == 0):
                #     print(self.age)
                    print(self.getMakespansOfAllIndividuals())
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
                    tempBird = self.pop[leaderInd].neighbourSearch('random', para[0], para[1], self.solutionClassName, inplace = 0)
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
                            # 交叉S次，分别挑最好的解加入邻域集
                            for _ in range(S):
                                chosenChild = self.pop[birdInd].crossoverBetweenBothSegmentsReturnBestChild(learnedBird, 0.5, 0.5, generalSolution)
                                wingNei.append(chosenChild)
                                wingNeiMakespan.append(chosenChild.makespan)
                            # 生成该鸟的邻域解，加入邻域集
                            for _ in range(K - S):
                                para = returnNeighbourFunctionRarameterByAging(self.age[birdInd])
                                tempBird = self.pop[birdInd].neighbourSearch('random', para[0], para[1], self.solutionClassName, inplace=0)
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

                # # 左右翼跟随鸟更新
                # for wingInd in [leftWingInd, rightWingInd]:
                #     for birdInd in wingInd:
                #         # 如果是第一只跟随鸟，就从领头鸟那里获得邻域解
                #         if birdInd == wingInd[0]:
                #             # 初始化跟随鸟邻域集，找出领头鸟最好的S个邻域解，加入邻域集
                #             bestAheadInd = getBestOrWorstIndexs('best', leaderNeiMakespan, S)
                #             wingNei = [leaderNei[i] for i in bestAheadInd]
                #             wingNeiMakespan = [leaderNeiMakespan[i] for i in bestAheadInd]
                #         # 生成该鸟的邻域解，加入邻域集
                #         for _ in range(K - S):
                #             tempBird = self.pop[birdInd].neighbourSearch('random_simple', 1, 1,
                #                                                          self.solutionClassName, inplace=0)
                #             wingNei.append(tempBird)
                #             wingNeiMakespan.append(tempBird.makespan)
                #         # 选出最好的邻域解，与该鸟择优
                #         if min(wingNeiMakespan) <= self.pop[birdInd].makespan:
                #             # 替换该鸟
                #             bestNeiInd = wingNeiMakespan.index(min(wingNeiMakespan))
                #             bestNei = wingNei[bestNeiInd]
                #             newPop[birdInd] = copy.deepcopy(bestNei)
                #             # 删除替换的鸟，更新邻域集以备下一只鸟使用
                #             del wingNei[bestNeiInd]
                #             del wingNeiMakespan[bestNeiInd]
                #             # 将邻域解最好的S个解保留，其他删掉
                #             bestAheadInd = getBestOrWorstIndexs('best', wingNeiMakespan, S)
                #             wingNei = [i for j, i in enumerate(wingNei) if j in bestAheadInd]
                #             wingNeiMakespan = [i for j, i in enumerate(wingNeiMakespan) if
                #                                j in bestAheadInd]


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
                if(iterInd % 1 == 0):
                    # print(self.age)
                    print(self.getMakespansOfAllIndividuals())
                    # print(self.getBestIndividualCodes())

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
                        # 交叉S次，分别挑最好的解加入邻域集
                        for _ in range(S):
                            chosenChild = self.pop[birdInd].crossoverBetweenBothSegmentsReturnBestChild(learnedBird, 0.5, 0.5, generalSolution)
                            wingNei.append(chosenChild)
                            wingNeiMakespan.append(chosenChild.makespan)
                        # 生成该鸟的邻域解，加入邻域集
                        for _ in range(K - S):
                            para2 = returnNeighbourFunctionRarameterByAging(self.age[birdInd])
                            tempBird = self.pop[birdInd].neighbourSearch('random', para2[0], para2[1], self.solutionClassName, inplace=0)
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
            # leaderInd, leftWingInd, rightWingInd = VReshape(leaderInd, leftWingInd, rightWingInd)


        if muteResult == 0:
            print('result after %d iterations:' % iterNum, self.getBestMakespan())
            # print(min(self.getMakespansOfAllIndividuals()))
            # print(self.getMakespansOfAllIndividuals())

        # 打印progress可以看到每个种群的每一代有多少个体在交叉变异种进步了
        # print(progress)



# test = myMBO1(51, lotNum, lotSizes, machineNum)
# test.iterate(10, 3, 1, 8, 2, 0.2, 0.1, needcalAllMakespan=1, muteEveryIter=0, muteResult=0, startIter=0, saveDetailsUsingDF=1,  needReinitializeAge=1)

# test.getBestIndividualCodes()
# test.getMakespansOfAllIndividuals()