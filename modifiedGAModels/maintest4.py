from globalVariablesAndFunctions import *
from comparisonsOfAlgorithms import comparisonsOfAlgorithms
from originalGA import originalGA
from originalMBO import originalMBO


print('构建')
originalMBOTest = originalMBO(51, lotNum, lotSizes, machineNum)


print('最原始的MBO，跑多遍')
test = comparisonsOfAlgorithms([originalMBOTest])
test.runManyTimes(20)
print(test.makespans.head())
print(' ')

"""
result = np.array(list(test.makespans.originalMBO)) 
result.mean()
result.std()
result.min()
result.max()
"""

