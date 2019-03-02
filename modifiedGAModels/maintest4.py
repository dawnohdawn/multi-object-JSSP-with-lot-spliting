from globalVariablesAndFunctions import *
from comparisonsOfAlgorithms import comparisonsOfAlgorithms
from originalGA import originalGA
from originalMBO import originalMBO
from originalMBO_newNeighbours import originalMBO_newNeighbours
from myMBO1 import myMBO1

print('构建')
originalMBOTest = originalMBO(51, lotNum, lotSizes, machineNum)
originalMBO_newNeighboursTest = originalMBO_newNeighbours(51, lotNum, lotSizes, machineNum)
myMBO1Test = myMBO1(51, lotNum, lotSizes, machineNum)


print('跑多遍')
test = comparisonsOfAlgorithms([myMBO1Test])
test.runManyTimes(2)

# print('收敛曲线')
# # test = comparisonsOfAlgorithms([originalMBOTest, originalMBO_newNeighboursTest])
# test = comparisonsOfAlgorithms([originalMBO_newNeighboursTest])
# # test = comparisonsOfAlgorithms([originalMBOTest])
# test.plotOneRun('OMBO & OMBO+NEI')

print('p3跑10次originalMBO_newNeighboursTest，补充结果，跑完了')

"""
result = np.array(list(test.makespans.originalMBO_newNeighbours)) 
result.mean()
result.std()
result.min()
result.max()
"""

