from generalGAModel import generalGAModel
from generalIndividual import generalIndividual
from generalPopulation import generalPopulation
from generalSolution import generalSolution


# 构建原始IMGA类：
class originalIMGA(generalGAModel):
    """
    继承generalGAModel得到
    """

    def __init__(self, modelSize, popSize, lotNum, lotSizes, machineNum):
        """
        指定了individual类是generalIndividual，pop类是generalPopulation，solution类是generalSolution
        """
        super(originalIMGA, self).__init__(modelSize, popSize, lotNum, lotSizes, machineNum, generalIndividual, \
                                           generalPopulation, generalSolution)