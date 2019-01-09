from globalVariablesAndFunctions import *
from generalIndividual import generalIndividual
from generalPopulation import  generalPopulation
from generalSolution import generalSolution
from generalGAModel import generalGAModel
from comparisonsOfAlgorithms import comparisonsOfAlgorithms
from originalGA import originalGA
from originalIMGA import originalIMGA
from threeIMGA import threeIMGA


# test = threeIMGA(67, lotNum, lotSizes, machineNum)
# test = originalIMGA(3, 66, lotNum, lotSizes, machineNum)
# for i in range(10):
#     print('outeriter', i)
#     test.modelIterate(1, 1, 0.8, 0.3, 0.3, 0.4, 0.4, 0.3, 0.3, 0.3, 'exchange', 10, muteEveryGAIter = 1,  muteGAResult = 1, \
#                       muteEveryOuterIter = 0, muteOuterResult = 0, saveDetailsUsingDF = 1)
#     for item in test.getMakespansOfAllIndividuals():
#         print(item)
#     test.model[0].decodeAFixedIndividual(test.getBestIndividualCodes(), 'gant-outerIter-%d'%i)



# test = generalPopulation(200, lotNum, lotSizes, machineNum, generalIndividual, generalSolution)
# for i in range(1000):
#     print('outeriter', i)
#     test.iterate(1, 0.5, 0.5, 0.5, 0.5, 0.5, 0.3, 0.3, 0.3, needcalAllMakespan=1, muteEveryIter=1, muteResult=0,
#                  startIter=100, saveDetailsUsingDF=1)
#     print(test.getMakespansOfAllIndividuals())






