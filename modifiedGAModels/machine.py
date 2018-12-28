# 机器类
class machine:

    def __init__(self):
        """
        self.idleMoment  从此刻开始，机器空闲了
        self.assignedList  list，已经被安排到该机器的工件，格式为[lot号，sublot号，sublot工件数，工序号]
        self.idlePeriods  该机器的空闲时间段，格式为[起始时间，结束时间]
        self.waitingList  从solution对象属性allMachineWaitingList中挑选出来符合条件的待加工工序
        self.waitingListTime  self.waitingList对应的时间list，里面每一个时间表示，idleMoment后多少时间之后，该sublot的该工序完成，
                            此时间包含等待时间和工序准备时间（如果有的话）
        self.waitingListTimePreparing   每个工序的工序准备时间，如果跟上一个工序lot类型一样的话，为0
        self.chosenOperation  本机器本次所选择的工序
        self.chosenOperationTime  本机器所选择的的工序所需时间
        """
        self.idleMoment = 0
        self.assignedList = []
        self.idlePeriods = []

        self.waitingList = []
        self.waitingListTime = []
        self.waitingListTimePreparing = []
        self.chosenOperation = 0
        self.chosenOperationTime = 0