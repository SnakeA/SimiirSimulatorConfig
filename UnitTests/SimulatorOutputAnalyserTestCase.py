__author__ = 'Angelos Constantinides'

import unittest
from SimulatorConfigurator import SimulatorConfigurator
from SimulatorRun import SimulatorRun
from SimulatorOutputAnalyser import SimulatorOutputAnalyser
import shutil
import os

class SimulatorOutputAnalyserTestCase(unittest.TestCase):

    # SetUp - Define an input configuration file and the simiir path
    def setUp(self):
        inputXMLfile = './UnitTests/TestData/testInput2.xml'
        simiirPath = '/home/angelos/IntellSearchAgent2/simiir/'
        flag = ''

        numOfRuns = 5

        # Create SimulatorConfigurator Object
        self.simConfg = SimulatorConfigurator(inputXMLfile,simiirPath, flag)

        self.simConfg.build_dictionary()
        self.simConfg.tidy_dictionary()

        self.simConfg.appendSimiirPath()
        self.simConfg.get_permutations()

        self.simConfg.generate_markup_userFiles()
        self.simConfg.generate_markup_simulationFiles()

        self.simConfg.generateSimulationPathsFile()

        currDir = os.getcwd()


        # Create  SimulatorRun object
        self.simRun = SimulatorRun('./UnitTests/TestData/exampleSimData/simulationPaths.txt', os.path.join(simiirPath,'simiir/'), numOfRuns, flag)

        self.simRun.readSimulPathsFile()
        self.simRun.prepareConfigFile()

        workingDir = os.getcwd()

        self.simRun.simRun()

        # set workingDir to prevDir (since simRun() changes it)
        os.chdir(workingDir)

        # Create SimulatorOutputAnalyser object
        self.simAnalyser = SimulatorOutputAnalyser('./UnitTests/TestData/exampleSimData/output', simiirPath, './UnitTests/TestData/exampleSimData/sum.csv')


    def tearDown(self):
        self.simRun = None
        # Delete created directory and contents
        shutil.rmtree('./UnitTests/TestData/exampleSimData')


    # Test number of lines to be written in the csv are correct
    def test_numOf_lines_csv_data(self):

        self.simAnalyser.appendSimData()
        self.simAnalyser.writeCsvFile()

        numberOfLines = len(self.simConfg.userConfigPaths) * self.simRun.numOfRuns * len(self.simConfg.simulConfigPaths)

        self.assertEqual(len(self.simAnalyser.data_out), numberOfLines , 'Wrong size of data for the CSV file')

    # Test if the csv file has been successfully created
    def test_csv_file_existence(self):

        self.simAnalyser.appendSimData()
        self.simAnalyser.writeCsvFile()

        self.assertEqual(os.path.isfile('./UnitTests/TestData/exampleSimData/sum.csv'), True , 'csv File Does not exist in the specified dir!')



if __name__ == '__main__':
    unittest.main()