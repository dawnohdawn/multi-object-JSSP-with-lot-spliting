from machine import machine
from globalVariablesAndFunctions import *
PATH = os.path.abspath('.')


# 解码算子类，传入generalIndividual
class generalSolution:

    def __init__(self, generalIndividual):
        """
        self.machineList  由self.machineNum个machine对象构成的list
        self.allMachineWaitingList  待加工的工序构成的list，每个元素格式为[lot号，sublot号，sublotSize，工序号，可以开始加工的时间]
        self.idleMomentList  每台机器的idletime，从self.machineList同步而来，用来方便选择下一台需要安排工件的机器
        self.sublotOperationAssignment  每个sublot的每个工序都由哪个机器加工，起止时间是多少，每个元素格式为[机器号，起始时间，结束时间]
        """
        # 从generalIndividual同步而来的信息
        self.lotSplitingCode = [item.sublotSizes for item in generalIndividual.segment1.lotSplitingCode]
        self.preferenceCode = generalIndividual.segment2.preferenceCode
        self.lotNum = generalIndividual.lotNum
        self.machineNum = generalIndividual.machineNum

        # 下面是主要变量
        self.machineList = [machine() for i in range(self.machineNum)]
        self.idleMomentList = [item.idleMoment for item in self.machineList]
        self.allMachineWaitingList = []
        self.sublotOperationAssignment = [[[] for sublot in lot] for lot in self.lotSplitingCode]


    def assignCodesToSolution(self, sublotSizes, preferenceCode):
        """
        功能：      直接给定sublotSizes, preferenceCode，方便后面根据此码解码调度
        """
        self.lotSplitingCode = sublotSizes
        self.preferenceCode = preferenceCode


    def initializeAllMachineWaitingList(self):
        """
        把所有lot的所有sublot的工序0放入self.allMachineWaitingList
        """
        for lotInd, lot in enumerate(self.lotSplitingCode):
            for sublotInd, sublotSize in enumerate(lot):
                self.allMachineWaitingList.append([lotInd, sublotInd, sublotSize, 0, 0])


    def chooseTheNextMachine(self):
        """
        self.idleMomentList一定要在每次选机器前重新由self.machineList生成出来，不能偷懒
        chosenIndex  返回值，是选中的机器的index
        后面可以补充：
        ①相同idleMoment的多台机器，加入规则选择好的一个，而不是随便选
        """
        self.idleMomentList = [item.idleMoment for item in self.machineList]

        # 选出最先idle的，且能加工工序类别总数最少的机器
        alternativeMachine = []
        for i, item in enumerate(self.idleMomentList):
            if (item == min(self.idleMomentList)):
                alternativeMachine.append(i)
        alternativeMachinePriority = [operationNumOfMachine[i] for i in alternativeMachine]
        chosenIndex = alternativeMachine[alternativeMachinePriority.index(min(alternativeMachinePriority))]

        # 选择最先idle的机器
        #         chosenIndex = self.idleMomentList.index(min(self.idleMomentList))

        return chosenIndex


    def generateWaitingList(self, machineInd, usePreparingTime=1):
        """
        对一台机器生成waitingList和waitingListTime，即从allMachineWaitingList选出符合条件的工序
        machineInd  是机器的号码，从0开始数
        usePreparingTime  是否使用工序准备时间
        """
        # 先清空该机器的waitingList和waitingListTime
        self.machineList[machineInd].waitingList = []
        self.machineList[machineInd].waitingListTime = []
        self.machineList[machineInd].waitingListTimePreparing = []

        # 构建waitingList
        # 选择能给该机器加工，而且在idleMoment时刻已经能开始加工，或者在idleMoment可以提前工序准备的工件
        if (usePreparingTime == 1):
            for item in self.allMachineWaitingList:
                if (machineInd in machineMatrix[item[0]][item[3]] and item[4] - self.machineList[machineInd].idleMoment \
                        <= preparingTimeMatrix[item[0]][item[3]][machineInd]):
                    self.machineList[machineInd].waitingList.append(item)
        # 选择能给该机器加工，而且在idleMoment时刻已经能开始加工的工件
        else:
            for item in self.allMachineWaitingList:
                if (machineInd in machineMatrix[item[0]][item[3]] and item[4] <= self.machineList[machineInd].idleMoment):
                    self.machineList[machineInd].waitingList.append(item)

                    # 构建和waitingListTime
        for item in self.machineList[machineInd].waitingList:
            tempTime = timeMatrix[item[0]][item[3]][machineInd] * item[2]
            # 如果算上工序准备时间，考虑提前工序准备，要对tempTime进行如下改造
            if (usePreparingTime == 1):
                # 与上一个工序为非同类
                if not (len(self.machineList[machineInd].assignedList) > 0 and item[0] == self.machineList[machineInd].assignedList[-1][0]):
                    tempTime += preparingTimeMatrix[item[0]][item[3]][machineInd]
                    self.machineList[machineInd].waitingListTimePreparing. append(preparingTimeMatrix[item[0]][item[3]][machineInd])


                # 与上一个工序为同类
                else:
                    if (self.machineList[machineInd].idleMoment < item[4]):
                        tempTime += (item[4] - self.machineList[machineInd].idleMoment)
                    self.machineList[machineInd].waitingListTimePreparing.append(0)
            self.machineList[machineInd].waitingListTime.append(tempTime)


    def chooseAndAssignOperation(self, machineInd, usePreference=1):
        """
        让一台机器从其waitingList选择一个工序，并插入到时间轴中，并维护self.allMachineWaitingList
        后面可以补充：
        ①用时相同的多个工序，加入规则选择好的一个，而不是选完工时间最小的那个
        ②插入时间轴前，检查空闲时间段能不能插入
        machineInd  是机器的号码，从0开始数
        usePreference  是否使用PreferenceCode来指导工件选择
        """
        # 如果使用Preference来选择工件的话，要重新生成waitingList和waitingListTime
        if (usePreference == 1 and len(self.machineList[machineInd].waitingList) != 0):
            # 从该机器的waitingList选择该机器偏好度最靠前的工序集合，放在tempList中
            for ind in self.preferenceCode[machineInd]:
                tempList = []
                tempListTime = []
                waitingListTimePreparing = []
                for i, item in enumerate(self.machineList[machineInd].waitingList):
                    if (item[0] == ind):
                        tempList.append(item)
                        tempListTime.append(self.machineList[machineInd].waitingListTime[i])
                        waitingListTimePreparing.append(self.machineList[machineInd].waitingListTimePreparing[i])
                if (len(tempList) > 0):
                    break
            # 用tempList覆盖掉该机器的waitingList和waitingListTime
            self.machineList[machineInd].waitingList = tempList
            self.machineList[machineInd].waitingListTime = tempListTime
            self.machineList[machineInd].waitingListTimePreparing = waitingListTimePreparing

        # 如果waitinglist有元素，选择一个来加工
        if (len(self.machineList[machineInd].waitingList) != 0):
            # 选择工序、工序在waitingList里面的序号、sublot该工序的加工时间
            index = self.machineList[machineInd].waitingListTime.index(
                min(self.machineList[machineInd].waitingListTime))
            #             index = [item[2] for item in self.machineList[machineInd].waitingList].index(max([item[2] for item in self.machineList[machineInd].waitingList]))
            operation = self.machineList[machineInd].waitingList[index]
            time = self.machineList[machineInd].waitingListTime[index]
            timePreparing = self.machineList[machineInd].waitingListTimePreparing[index]
            # 更新相关信息
            self.machineList[machineInd].chosenOperation = operation
            self.machineList[machineInd].chosenOperationTime = time
            #             self.machineList[machineInd].assignedList.append(operation)
            # (lot号，sublot号，工件数，工序号，最早看额开始时间，实际开始时间，实际结束时间，准备工序时间)
            self.machineList[machineInd].assignedList. \
                append(
                operation[:] + [self.machineList[machineInd].idleMoment, self.machineList[machineInd].idleMoment + time,
                                timePreparing])
            # 插入到时间轴里，更新idleMoment
            self.machineList[machineInd].idleMoment += time
            # 更新各种信息
            self.sublotOperationAssignment[operation[0]][operation[1]].\
                append([machineInd, self.machineList[machineInd].idleMoment - time, self.machineList[machineInd].idleMoment])
            # 将该工序从self.allMachineWaitingList删除，将该sublot的下一个工序加入self.allMachineWaitingList
            self.allMachineWaitingList.remove(operation)
            if operation[3] != lotOpeartionNumList[operation[0]] - 1:
                self.allMachineWaitingList.append(
                    operation[:3][:] + [operation[3] + 1, self.machineList[machineInd].idleMoment])
        # 如果waitinglist没有元素，那么把idleMoment加入到idlePeriods
        else:
            self.machineList[machineInd].idleMoment += 1
            self.machineList[machineInd].chosenOperation = 0
            self.machineList[machineInd].chosenOperationTime = 0
            if (len(self.machineList[machineInd].idlePeriods) != 0 and self.machineList[machineInd].idlePeriods[-1][
                -1] == self.machineList[machineInd].idleMoment - 1):  # 如果最新一段空闲时间段跟此刻idleMoment是连续的，那么在那基础上扩展就行
                self.machineList[machineInd].idlePeriods[-1][-1] = self.machineList[machineInd].idleMoment
            else:
                self.machineList[machineInd].idlePeriods.append(
                    [self.machineList[machineInd].idleMoment - 1, self.machineList[machineInd].idleMoment])


    def run(self, mute=1):
        """
        自动求解调度方案
        mute  等于1时，不打印求解过程
        """
        #  初始化
        self.initializeAllMachineWaitingList()
        if (mute != 1):
            print('allMachineWaitingList: ', self.allMachineWaitingList)

            #  开始循环求解
        #         for i in range(80):
        while (len(self.allMachineWaitingList) != 0):

            chosenMachine = self.chooseTheNextMachine()

            if (mute != 1):
                print('idleMomentList: ', self.idleMomentList)
                print('chosenMachine: ', chosenMachine)

            self.generateWaitingList(machineInd=chosenMachine)

            if (mute != 1):
                print('waitingList: ', self.machineList[chosenMachine].waitingList)
                print('waitingListTime: ', self.machineList[chosenMachine].waitingListTime)
                print('waitingListTimePreparing: ', self.machineList[chosenMachine].waitingListTimePreparing)

            self.chooseAndAssignOperation(chosenMachine)

            if (mute != 1):
                print('waitingList: ', self.machineList[chosenMachine].waitingList)
                print('waitingListTime: ', self.machineList[chosenMachine].waitingListTime)

                print('chosenOperation: ', self.machineList[chosenMachine].chosenOperation)
                print('chosenOperationTime: ', self.machineList[chosenMachine].chosenOperationTime)

                print('assignedList: ', self.machineList[chosenMachine].assignedList)
                print('idleMoment: ', self.machineList[chosenMachine].idleMoment)
                print('idlePeriods: ', self.machineList[chosenMachine].idlePeriods)
                print('allMachineWaitingList: ', self.allMachineWaitingList)
                print('sublotOperationAssignment', self.sublotOperationAssignment)
                print(' ')

        # 最后把多余的idlePeriods删掉，才能得到准确的idleMoment和idlePeriods
        for i in range(self.machineNum):
            if (len(self.machineList[i].idlePeriods) != 0):
                if (self.machineList[i].idlePeriods[-1][-1] == self.machineList[i].idleMoment):
                    self.machineList[i].idleMoment = self.machineList[i].idlePeriods[-1][0]
                    del (self.machineList[i].idlePeriods[-1])


    def printResults(self):
        """
        打印run()的调度方案信息
        """
        print('assignment for each machine')
        for i, item in enumerate(self.machineList):
            print('for machine %i: ' % i, item.assignedList)
        print('idlePeriods for each machine')
        for i, item in enumerate(self.machineList):
            print('for machine %i: ' % i, item.idlePeriods)
        print('completion time for each machine: ', [item.idleMoment for item in self.machineList])
        print('total completion time: ', max([item.idleMoment for item in self.machineList]))
        print('sublotOperationAssignment for each sublot:')
        for i, lot in enumerate(self.sublotOperationAssignment):
            print('for lot%d: ' % i)
            print(lot)


    def getLastFinishingMachineInd(self):
        """
        功能：
        返回最晚完工的机器号

        输出：
        一个机器index
        """
        finishingTimes = [item.idleMoment for item in self.machineList]

        return finishingTimes.index(max(finishingTimes))


    def getLastFinishingSublot(self):
        """
        功能：
        返回最晚完成加工的sublot的lot序号，sublot序号

        输出：
        lot序号，sublot序号
        """
        lastMachine = self.getLastFinishingMachineInd()
        lastSublot = self.machineList[lastMachine].assignedList[-1]   # (lot号，sublot号，工件数，工序号，最早看开始时间，实际开始时间，实际结束时间，准备工序时间)

        return lastSublot[0], lastSublot[1]


    def getMakespan(self):
        """
        返回完工时间
        """
        return max([item.idleMoment for item in self.machineList])


    def generateGantTimetable(self, filename='gantData'):
        """
        为该solution生成甘特图时间表
        filename  csv文件路径
        """
        csvName = filename + '.csv'
        # pngName = filename + '.png'

        gantData = []
        for machInd, machine in enumerate(self.machineList):
            for item in machine.assignedList:
                if (item[7] != 0):
                    gantData.append(['M%d' % machInd, item[5], item[5] + item[7], '*'])
                gantData.append(['M%d' % machInd, item[5] + item[7], item[6], '{lotInd}-{sublotInd}-{operationInd}'.\
                                format(lotInd=item[0], sublotInd=item[1], operationInd=item[3])])
        df = pd.DataFrame(gantData, columns=["Machine", "Start", "Finish", "Title"])
        df.to_csv(PATH + "\\" + csvName, header=False)
        print('gantChart timetable', csvName, 'done: {}'.format(PATH + "\\" + csvName))

        # drawGantChart(fromFilename = csvName, toFilename = pngName)
        # print('gantChart figure', pngName, 'done: {}'.format(PATH + "\\" + pngName))


