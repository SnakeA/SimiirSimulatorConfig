import unittest
import shutil
from SimulatorConfigurator import SimulatorConfigurator

class SimulatorConfiguratorTestCase(unittest.TestCase):

    # SetUp - Define an input configuration file and the simiir path
    def setUp(self):
        inputXMLfile = 'UnitTests/TestData/testInput.xml'
        simiirPath = '/home/angelos/IntellSearchAgent2/simiir/'
        flag = ''
        self.simConfg = SimulatorConfigurator(inputXMLfile,simiirPath, flag)

        self.simConfg.build_dictionary()
        self.simConfg.tidy_dictionary()

        self.simConfg.appendSimiirPath()
        self.simConfg.get_permutations()

        self.simConfg.generate_markup_userFiles()
        self.simConfg.generate_markup_simulationFiles()

    def tearDown(self):
        self.simConfg = None
        # Delete Created Dir
        shutil.rmtree('./UnitTests/TestData/exampleSimData')


    # Test if the number of simulated users, based on the input provided, is correct
    def test_numOf_simulated_users(self):
        self.assertEqual(len(self.simConfg.userConfigPaths),6 ,'Wrong number of simulated users')

    # Test if the number of simulation cofiguration files, based on the input provided, is correct
    def test_numOf_simulation_configuration_files(self):
        self.assertEqual(len(self.simConfg.simulConfigPaths), 2, 'Wrong number of simulation configuration files')


if __name__ == '__main__':
    unittest.main()