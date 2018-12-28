from globalVariablesAndFunctions import *
from generalIndividual import generalIndividual
from generalPopulation import  generalPopulation
from generalSolution import generalSolution
from generalGAModel import generalGAModel
from comparisonsOfAlgorithms import comparisonsOfAlgorithms
from originalGA import originalGA
from originalIMGA import originalIMGA
from threeIMGA import threeIMGA


# comparisonsOfAlgorithms类测试

print('构建')
originalGATest = originalGA(201, lotNum, lotSizes, machineNum)
originalIMGATest = originalIMGA(3, 67, lotNum, lotSizes, machineNum)
threeIMGATest = threeIMGA(67, lotNum, lotSizes, machineNum)
test = comparisonsOfAlgorithms([originalGATest, originalIMGATest, threeIMGATest])


print('算法各自跑多遍')
test.runManyTimes(10)
print(test.makespans.head())
print(' ')


# print('单次运行算法收敛对比')
# test.plotOneRun('convergComparison.png')
# print(test.oneRunData.head())
# print(' ')




