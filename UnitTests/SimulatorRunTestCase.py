import unittest
import os
from SimulatorConfigurator import SimulatorConfigurator
from SimulatorRun import SimulatorRun
import shutil
import os

class SimulatorRunTestCase(unittest.TestCase):

    # SetUp - Define an input configuration file and the simiir path
    def setUp(self):
        inputXMLfile = './UnitTests/TestData/testInput2.xml'
        simiirPath = '/home/angelos/IntellSearchAgent2/simiir/'
        flag = ''

        numOfRuns = 5

        # Run the SimulatorConfigurator to create the necessary test files
        self.simConfg = SimulatorConfigurator(inputXMLfile,simiirPath, flag)

        self.simConfg.build_dictionary()
        self.simConfg.tidy_dictionary()

        self.simConfg.appendSimiirPath()
        self.simConfg.get_permutations()

        self.simConfg.generate_markup_userFiles()
        self.simConfg.generate_markup_simulationFiles()

        self.simConfg.generateSimulationPathsFile()

        currDir = os.getcwd()

        # Initialize the SimulatorRun class an required
        self.simRun = SimulatorRun('./UnitTests/TestData/exampleSimData/simulationPaths.txt', os.path.join(simiirPath,'simiir/'), numOfRuns, flag)

        self.simRun.readSimulPathsFile()
        self.simRun.prepareConfigFile()


    def tearDown(self):
        self.simRun = None
        # Delete created directory and contents
        shutil.rmtree('./UnitTests/TestData/exampleSimData')

    # Test if the number of Runs is correct
    def test_numOf_runs(self):
        self.assertEqual(self.simRun.numOfRuns, 5,'Wrong number of runs')

    # Test if the number of simulation cofiguration files to be run, based on the input provided, is correct
    def test_numOf_simulation_configuration_files(self):
        self.assertEqual(len(self.simRun.listOfRuns), 10, 'Wrong number of simulation configuration to run')

    # Test return code after simulations run
    def test_numOf_simulation_configuration_files2(self):
        workingDir = os.getcwd()

        returnCode = self.simRun.simRun()

        # set workingDir to prevDir (since simRun() changes it)
        os.chdir(workingDir)
        self.assertEqual(returnCode, 0, 'Simulation Run Was not successful')

    # Test if the simulation runs were actually performed by looking at the COMPLETED files
    def test_runs_by_COMPLETED_files(self):
        workingDir = os.getcwd()

        returnCode = self.simRun.simRun()

        # set workingDir to prevDir (since simRun() changes it)
        os.chdir(workingDir)

        countCompleted = 0
        for dirName, subdirList, fileList in os.walk("./UnitTests/TestData/exampleSimData"):
            for fname in fileList:
                if fname == 'COMPLETED':
                    countCompleted +=1

        self.assertEqual(countCompleted, 10, 'Not all the required runs were completed!')

if __name__ == '__main__':
    unittest.main()