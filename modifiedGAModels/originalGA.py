from generalPopulation import generalPopulation
from generalIndividual import generalIndividual
from generalSolution import generalSolution


# 构建原始单种群GA类：originalGA
class originalGA(generalPopulation):
    """
    继承generalPopulation得到
    """

    def __init__(self, popSize, lotNum, lotSizes, machineNum):
        """
        指定了individual类是generalIndividual，solution类是generalSolution
        """
        super(originalGA, self).__init__(popSize, lotNum, lotSizes, machineNum, generalIndividual, generalSolution)
