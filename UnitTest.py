import unittest
from SimulatorConfigurator import SimulatorConfigurator

class SimulatorConfiguratorTestCase(unittest.TestCase):

    # Testing given an example Input XML file
    def setUp(self):
        inputXMLfile = 'exampleInput.xml'
        simiirPath = '/home/angelos/IntellSearchAgent2/simiir/'
        self.simConfg = SimulatorConfigurator(inputXMLfile,simiirPath)

        self.simConfg.build_dictionary()
        self.simConfg.tidy_dictionary()

        self.simConfg.appendSimiirPath()
        self.simConfg.get_permutations()

        self.simConfg.generate_markup_userFiles()
        self.simConfg.generate_markup_simulationFiles()

    def tearDown(self):
        self.simConfg = None

    def test_numOf_simulated_users(self):
        self.assertEqual(len(self.simConfg.userConfigPaths),6 ,'Wrong number of simulated users')

    def test_numOf_simulation_configuration_files(self):
        self.assertEqual(len(self.simConfg.simulConfigPaths), 3, 'Wrong number of simulation configuration files')






# class SetUp(unittest.TestCase):
#     def setUp(self):
#         dictionary_repr = build_dictionary("exampleInput.xml")
#         self.dict_repr = dictionary_repr
#
# class testBuidDictMethod(SetUp):
#     def runTest(self):
#         self.assertIn("simulationConfiguration",self.dict_repr)
#         self.assertIn("@baseDir",self.dict_repr["simulationConfiguration"], "Base Directory component not found!")
#         self.assertIn("searchContext", self.dict_repr["simulationConfiguration"], "Search Context component not found!")
#         self.assertIn("topics", self.dict_repr["simulationConfiguration"], "Topic(s) not found!")
#         self.assertIn("queryGenerator", self.dict_repr["simulationConfiguration"], "Query Generator component not found!")
#         self.assertIn("stoppingDecisionMaker", self.dict_repr["simulationConfiguration"], "Stopping Decision Maker component not found!")
#         self.assertIn("searchInterface", self.dict_repr["simulationConfiguration"], "Search Interface component not found!")
#         self.assertIn("logger", self.dict_repr["simulationConfiguration"], "Logger component not found!")
#         self.assertIn("textClassifiers", self.dict_repr["simulationConfiguration"], "Text Classifiers component not found!")
#
#
# class testTidyDictMethod(SetUp):
#     def runTest(self):
#         tidy_dictionary(self.dict_repr)
#         self.assertIs(type(self.dict_repr["simulationConfiguration"]["searchContext"]), list)
#         self.assertIs(type(self.dict_repr["simulationConfiguration"]["topics"]), list)
#         self.assertIs(type(self.dict_repr["simulationConfiguration"]["queryGenerator"]), list)
#         self.assertIs(type(self.dict_repr["simulationConfiguration"]["textClassifiers"]["documentClassifier"]), list)
#         self.assertIs(type(self.dict_repr["simulationConfiguration"]["textClassifiers"]["snippetClassifier"]), list)
#         self.assertIs(type(self.dict_repr["simulationConfiguration"]["logger"]), list)
#         self.assertIs(type(self.dict_repr["simulationConfiguration"]["stoppingDecisionMaker"]), list)
#         self.assertIs(type(self.dict_repr["simulationConfiguration"]["searchInterface"]), list)
#
#         #print self.dict_repr["simulationConfiguration"]["queryGenerator"][0]["type"]

if __name__ == '__main__':
    unittest.main()