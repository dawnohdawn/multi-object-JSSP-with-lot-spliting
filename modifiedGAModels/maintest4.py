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
from myPMBO1 import PMBO1
from microMBO1 import microMBO1
from microMBO2 import microMBO2
from MOMBO1 import MOMBO1


print('构建')
myMBO1Test = myMBO1(51, lotNum, lotSizes, machineNum)
myPMBO1Test = myPMBO1(3, 29, lotNum, lotSizes, machineNum)
PMBO1Test = PMBO1(3, 29, lotNum, lotSizes, machineNum)
originalMBOTest = originalMBO(51, lotNum, lotSizes, machineNum)
originalMBO_newNeighboursTest = originalMBO_newNeighbours(51, lotNum, lotSizes, machineNum)
originalIMGATest = originalIMGA(3, 18, lotNum, lotSizes, machineNum)
NIMGATest = NIMGA(18, lotNum, lotSizes, machineNum)
HGATest = HGA(52, lotNum, lotSizes, machineNum)
microMBO1Test = microMBO1(5, lotNum, lotSizes, machineNum)
microMBO2Test = microMBO2(5, lotNum, lotSizes, machineNum)
MOMBO1Test = MOMBO1(51, lotNum, lotSizes, machineNum)



# print('跑多遍')
test = comparisonsOfAlgorithms([microMBO1Test])
# test = comparisonsOfAlgorithms([microMBO2Test])
# test = comparisonsOfAlgorithms([MOMBO1Test])
print('p{}，{}，跑5次'.format(problemInd, [item.name for item in test.algorithms]))
test.runManyTimes(5)

# print('收敛曲线')
# # test = comparisonsOfAlgorithms([myPMBO1Test])
# test = comparisonsOfAlgorithms([myMBO1Test])
# # test = comparisonsOfAlgorithms([originalMBO_newNeighboursTest])
# test.plotOneRun('MBO+adjust-P{}'.format(problemInd))
# print('p{}，MBO+adjust'.format(problemInd))




"""
result = np.array(list(test.makespans.myMBO1)) 
result.mean()
result.std()
result.min()
result.max()
"""

