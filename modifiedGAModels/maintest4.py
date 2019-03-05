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
test.runManyTimes(20)

# print('收敛曲线')
# test = comparisonsOfAlgorithms([myMBO1Test])
# # test = comparisonsOfAlgorithms([originalMBO_newNeighboursTest])
# # test = comparisonsOfAlgorithms([myMBO1Test])
# test.plotOneRun('myMBO1+aging-P1')

# print('p1跑1次myMBO1，观察185个体是怎么变为184的，是交叉，还是邻域搜索？邻域搜索的话是一步还是两步？')
print('p4，myMBO1+aging，1000iter跑20次，agingThreshold=[10, 30, 40]')
# print('p1，myMBO1+aging，收敛图，使用了相同的random seed')

"""
result = np.array(list(test.makespans.myMBO1)) 
result.mean()
result.std()
result.min()
result.max()
"""

