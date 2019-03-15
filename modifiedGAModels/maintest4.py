from globalVariablesAndFunctions import *
from comparisonsOfAlgorithms import comparisonsOfAlgorithms
from originalGA import originalGA
from originalMBO import originalMBO
from originalMBO_newNeighbours import originalMBO_newNeighbours
from myMBO1 import myMBO1
from originalIMGA import originalIMGA
from NIMGA import NIMGA
from HGA import HGA
from myPMBO2 import myPMBO1


print('构建')
myMBO1Test = myMBO1(51, lotNum, lotSizes, machineNum)
myPMBO1Test = myPMBO1(3, 29, lotNum, lotSizes, machineNum)
originalMBOTest = originalMBO(51, lotNum, lotSizes, machineNum)
originalMBO_newNeighboursTest = originalMBO_newNeighbours(51, lotNum, lotSizes, machineNum)
originalIMGATest = originalIMGA(3, 18, lotNum, lotSizes, machineNum)
NIMGATest = NIMGA(18, lotNum, lotSizes, machineNum)
HGATest = HGA(52, lotNum, lotSizes, machineNum)



print('跑多遍')
test = comparisonsOfAlgorithms([myPMBO1Test])
test.runManyTimes(20)

# print('收敛曲线')
# test = comparisonsOfAlgorithms([myMBO1Test])
# # test = comparisonsOfAlgorithms([originalMBO_newNeighboursTest])
# # test = comparisonsOfAlgorithms([myMBO1Test])
# test.plotOneRun('myMBO1+aging-P1')

print('p{}，{}，PCCMBO+aging机制，跑20次'.format(problemInd, [item.name for item in test.algorithms]))


"""
result = np.array(list(test.makespans.myPMBO1)) 
result.mean()
result.std()
result.min()
result.max()
"""

