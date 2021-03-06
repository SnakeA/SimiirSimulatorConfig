__author__ = 'Angelos Constantinides'
import os
import itertools
import sys
from lxml import etree
from xml.etree import cElementTree
from collections import defaultdict
from utilities import read_file_to_string, get_available_classes


class SimulatorConfigurator():

    def __init__(self, inputXMLfile, simiirPath, flag):
        self.simiirPath = simiirPath
        self.inputXMLfile = inputXMLfile
        self.simulationBaseDir = ''
        self.dictRepr = None
        self.userConfigPaths = []
        self.simulConfigPaths = []
        self.userPermutations = []
        self.simulationPermutations = []
        self.userFlag = flag

    def build_dictionary(self):
            """
            Turns the XML configuration file into a Python dictionary object.
            The nested function recursive_generation() is unsurprisingly recursive.
            """
            def recursive_generation(t):
                """
                Nested helper function that recursively loops through an XML node to construct a dictionary.
                Solution from http://stackoverflow.com/a/10077069 (2013-01-19)
                """
                d = {t.tag: {} if t.attrib else None}
                children = list(t)

                if children:
                    dd = defaultdict(list)

                    for dc in map(recursive_generation, children):
                        for k, v in dc.iteritems():
                            dd[k].append(v)

                    d = {t.tag: {k:v[0] if len(v) == 1 else v for k, v in dd.iteritems()}}

                if t.attrib:
                    d[t.tag].update(('@' + k, v) for k, v in t.attrib.iteritems())

                if t.text:
                    text = t.text.strip()

                    if children or t.attrib:
                        if text:
                            d[t.tag]['#text'] = text
                    else:
                        d[t.tag] = text

                return d

            config_file = etree.parse(self.inputXMLfile)
            string_repr = etree.tostring(config_file, pretty_print=True)
            element_tree = cElementTree.XML(string_repr)

            self.dictRepr = recursive_generation(element_tree)





    def tidy_dictionary(self):
        """
        Create a list for the specified reference and add type
        (Adapted from https://github.com/leifos/simiir/blob/master/simiir/sim_config_generator/sim_config_generator.py
        & modified as required)
        """

        def to_list(ref, specified_type):

            if type(ref.keys()[0]) == dict:
                ref = [ref[ref.keys()[0]]]

            ref = ref[ref.keys()[0]]

            if type(ref) == dict:
                ref = [ref]

            for entry in ref:
                entry['type'] = specified_type

            return ref

        """
        Lists for the User Configuration
        """
        self.dictRepr['simulationConfiguration']['queryGenerator'] = to_list(self.dictRepr['simulationConfiguration']['queryGenerator'], 'queryGenerator')
        self.dictRepr['simulationConfiguration']['textClassifiers']['snippetClassifier'] = to_list(self.dictRepr['simulationConfiguration']['textClassifiers']['snippetClassifier'], 'snippetClassifier')
        self.dictRepr['simulationConfiguration']['textClassifiers']['documentClassifier'] = to_list(self.dictRepr['simulationConfiguration']['textClassifiers']['documentClassifier'], 'documentClassifier')
        self.dictRepr['simulationConfiguration']['stoppingDecisionMaker'] = to_list(self.dictRepr['simulationConfiguration']['stoppingDecisionMaker'], 'stoppingDecisionMaker')
        self.dictRepr['simulationConfiguration']['logger'] = to_list(self.dictRepr['simulationConfiguration']['logger'], 'logger')
        self.dictRepr['simulationConfiguration']['searchContext'] = to_list(self.dictRepr['simulationConfiguration']['searchContext'], 'searchContext')

        """
        Lists for the Simulator Configuration
        """
        self.dictRepr['simulationConfiguration']['topics'] = to_list(self.dictRepr['simulationConfiguration']['topics'], 'topics')
        self.dictRepr['simulationConfiguration']['searchInterface'] = to_list(self.dictRepr['simulationConfiguration']['searchInterface'], 'searchInterface')



    def get_permutations(self):
        """
        Contains a list of tuples, with each tuple containing dictionaries representing a particular combination.
        Note that topics are ignored; these are stored within the simulation configuration file.
        (Adapted from https://github.com/leifos/simiir/blob/master/simiir/sim_config_generator/sim_config_generator.py
        & modified as required)
        """
        query_generators = self.dictRepr['simulationConfiguration']['queryGenerator']
        snippet_classifiers = self.dictRepr['simulationConfiguration']['textClassifiers']['snippetClassifier']
        document_classifiers = self.dictRepr['simulationConfiguration']['textClassifiers']['documentClassifier']
        decision_makers = self.dictRepr['simulationConfiguration']['stoppingDecisionMaker']
        loggers = self.dictRepr['simulationConfiguration']['logger']
        search_contexts = self.dictRepr['simulationConfiguration']['searchContext']
        search_interfaces = self.dictRepr['simulationConfiguration']['searchInterface']




        self.userPermutations = list(itertools.product(query_generators,
                                                        snippet_classifiers,
                                                        document_classifiers,
                                                        decision_makers,
                                                        loggers,
                                                        search_contexts))

        self.simulationPermutations = list(itertools.product(search_interfaces))



    def generate_topics(self):
        """
        Generates a list of XML elements representing the topic(s) to be used in the simulation.
        https://github.com/leifos/simiir/blob/master/simiir/sim_config_generator/sim_config_generator.py
        """
        def generate_topic_markup(entry):
            topic_markup = read_file_to_string('base_files/topic.xml')
            topic_markup = topic_markup.format(entry['@id'],
                                               entry['@filename'],
                                               entry['@qrelsFilename'])
            return topic_markup

        topics_list = self.dictRepr['simulationConfiguration']['topics']
        topics_str = ""

        for entry in topics_list:
            topics_str = "{0}{1}".format(topics_str, generate_topic_markup(entry))

        return topics_str

    def generate_user_entries(self):
        """
        Returns a series of XML components for user objects in the simulation file.
        https://github.com/leifos/simiir/blob/master/simiir/sim_config_generator/sim_config_generator.py
        """
        entry_list = ""

        for entry in self.userConfigPaths:
            user_markup = read_file_to_string('base_files/user_entry.xml')
            entry_list = "{0}{1}".format(entry_list, user_markup.format(entry))

        return entry_list


    def create_attribute_markup(self, attribute_dict):
        """
        Given a dictionary representing an attribute, returns the associated XML markup for that attribute component.
        https://github.com/leifos/simiir/blob/master/simiir/sim_config_generator/sim_config_generator.py
        """
        attribute_markup = read_file_to_string('base_files/attribute.xml')
        value = attribute_dict['@value'].replace('[[ base_dir ]]', self.simulationBaseDir)

        attribute_markup = attribute_markup.format(attribute_dict['@name'],
                                                   attribute_dict['@type'],
                                                   value,
                                                   attribute_dict['@is_argument'])

        return attribute_markup

    def generate_search_interface_markup(self, dict_repr):
        """
        Returns markup for the search interface component.
        https://github.com/leifos/simiir/blob/master/simiir/sim_config_generator/sim_config_generator.py
        """
        interface_markup = read_file_to_string('base_files/interface.xml')
        interface_entry = dict_repr['simulation']['searchInterface']
        attribute_markup_concat = ''

        for attribute in interface_entry['attributes']:
            attribute_markup = read_file_to_string('base_files/attribute.xml')
            attribute_markup = attribute_markup.format(attribute['@name'], attribute['@type'], attribute['@value'], attribute['@is_argument'])
            attribute_markup_concat = '{0}{1}'.format(attribute_markup_concat, attribute_markup)

        return interface_markup.format(dict_repr['simulation']['searchInterface']['class'], attribute_markup_concat)



    def generate_markup_userFiles(self):
        """
        Given a tuple of dictionary objects, generates the markup & create files for the associated users.
        Returns a list with the full paths of the user config. files
        """

        user_files = []
        baseDir = self.dictRepr['simulationConfiguration']['@baseDir']

        # Check if the Directory has / character
        if baseDir[-1] =='/':
            baseDir = baseDir[:-1]
            self.simulationBaseDir = os.path.join(os.path.dirname(os.path.abspath(baseDir)),baseDir.split('/')[-1])

        else:
            self.simulationBaseDir = os.path.join(os.path.dirname(os.path.abspath(baseDir)),baseDir.split('/')[-1])


        componentsPath = os.path.join(self.simiirPath,'simiir')

        j=1
        for iteration in self.userPermutations:
            user_markup_components = {
                'id': None,
                'queryGenerator': {'class': None, 'attributes': None, 'attributes_py': None},
                'snippetClassifier': {'class': None, 'attributes': None, 'attributes_py': None},
                'documentClassifier': {'class': None, 'attributes': None, 'attributes_py': None},
                'stoppingDecisionMaker': {'class': None, 'attributes': None, 'attributes_py': None},
                'logger': {'class': None, 'attributes': None, 'attributes_py': None},
                'searchContext': {'class': None, 'attributes': None, 'attributes_py': None},
            }

            """
            Extract the components for the user configuration for this iteration
            """


            for component in iteration:

                component_type = component['type']
                user_markup_components[component_type]['class'] = component['@name']

                if 'attribute' in component:
                    component_attributes = component['attribute']
                    user_markup_components[component_type]['attributes_py'] = component_attributes

                    if type(component_attributes) == dict:
                        user_markup_components[component_type]['attributes'] = self.create_attribute_markup(component_attributes)
                    else:
                        for attribute in component_attributes:
                            if user_markup_components[component_type]['attributes'] is None:
                                user_markup_components[component_type]['attributes'] = ""
                            user_markup_components[component_type]['attributes'] = "{0}{1}".format(user_markup_components[component_type]['attributes'], self.create_attribute_markup(attribute))


            # File Name includes queryGenerator_StoppinStrategy-Value
            fileName = '/user_{0}_{1}-{2}-{3}.xml'.format(user_markup_components['queryGenerator']['class'],
                                                     user_markup_components['stoppingDecisionMaker']['class'],
                                                     user_markup_components['stoppingDecisionMaker']['attributes'].split('value="')[1].split('"')[0],
                                                      str(j))
            j=j+1

            # Extract User Id from File name
            user_base_id = fileName[6:-4]

            # Validate Stopping Decision Maker Component
            if user_markup_components['stoppingDecisionMaker']['class'] not in get_available_classes(componentsPath,'stopping_decision_makers'):
                print 'The Stopping Decision Maker component ' + user_markup_components['stoppingDecisionMaker']['class'] + ' does not exist. Please ensure that you have typed the name correctly!'
                sys.exit(2)

            # Validate Query Generator Component
            if user_markup_components['queryGenerator']['class'] not in get_available_classes(componentsPath,'query_generators'):
                print 'The Query Generator component  ' + user_markup_components['queryGenerator']['class'] + ' does not exist. Please ensure that you have typed the name correctly!'
                sys.exit(2)


            """
            Prepare String markup for user configuration
            """
            user_markup = read_file_to_string('base_files/user.xml')
            user_markup = user_markup.format(
                user_base_id,
                user_markup_components['queryGenerator']['class'],
                user_markup_components['queryGenerator']['attributes'] if user_markup_components['queryGenerator']['attributes'] is not None else "",
                user_markup_components['snippetClassifier']['class'],
                user_markup_components['snippetClassifier']['attributes'] if user_markup_components['snippetClassifier']['attributes'] is not None else "",
                user_markup_components['documentClassifier']['class'],
                user_markup_components['documentClassifier']['attributes'] if user_markup_components['documentClassifier']['attributes'] is not None else "",
                user_markup_components['stoppingDecisionMaker']['class'],
                user_markup_components['stoppingDecisionMaker']['attributes'] if user_markup_components['stoppingDecisionMaker']['attributes'] is not None else "",
                user_markup_components['logger']['class'],
                user_markup_components['logger']['attributes'] if user_markup_components['logger']['attributes'] is not None else "",
                user_markup_components['searchContext']['class'],
                user_markup_components['searchContext']['attributes'] if user_markup_components['searchContext']['attributes'] is not None else "")


            """
            Create the user configuration file
            """
            filePath = self.simulationBaseDir + fileName
            user_files.append(filePath)


            if not os.path.exists(os.path.dirname(filePath)):
                os.makedirs(os.path.dirname(filePath))

            with open(filePath, "w") as user_file:
                user_file.write(user_markup)

            user_file.close()


        self.userConfigPaths = user_files



    def generate_markup_simulationFiles(self):
        """
        Given a tuple of dictionary objects,topics and users generates the markup & create files for the associated simulations.
        Returns the a list with the full paths of the simulation config. files
        """

        simulation_files = []

        #Count Iterations
        i=0
        for iteration in self.simulationPermutations:

            simulation_markup_components = {
                'id': None,
                'searchInterface': {'class': None, 'attributes': None, 'attributes_py': None}
            }

            """
            Extract the components for the simulation configuration for this iteration
            """
            for component in iteration:
                component_type = component['type']
                simulation_markup_components[component_type]['class'] = component['@name']

                if 'attribute' in component:
                    component_attributes = component['attribute']
                    simulation_markup_components[component_type]['attributes_py'] = component_attributes

                    if type(component_attributes) == dict:
                        simulation_markup_components[component_type]['attributes'] = self.create_attribute_markup(component_attributes)
                    else:
                        for attribute in component_attributes:
                            if simulation_markup_components[component_type]['attributes'] is None:
                                simulation_markup_components[component_type]['attributes'] = ""
                            simulation_markup_components[component_type]['attributes'] = "{0}{1}".format(simulation_markup_components[component_type]['attributes'], self.create_attribute_markup(attribute))


            """
            Find Retrival Model
            """
            retrModelVal=-1

            for comp in self.dictRepr['simulationConfiguration']['searchInterface'][i]['attribute']:
                if comp['@name'] == 'model':
                    retrModelVal = comp['@value']

            retrModels = {'0': 'TFIDF', '1': 'BM25', '2': 'PL2', '-1':''}

            retrModel = retrModels[retrModelVal]

            #Generate users and topics

            #If user flag set, users will be set to sim.Config files at a later state
            if self.userFlag == '-u':
                users = "{3}"
            else:
                users = self.generate_user_entries()

            topics = self.generate_topics()

            """
            Construct the simulation configuration markup
            """
            simulation_markup = read_file_to_string('base_files/simulation.xml')
            simulation_markup = simulation_markup.format('trec_{0}_simulation-{1}'.format(retrModel,str(i)),
                                                     os.path.join(self.simulationBaseDir, '{0}/{1}/{2}'),
                                                     topics,
                                                     users,
                                                     simulation_markup_components['searchInterface']['class'],
                                                     simulation_markup_components['searchInterface']['attributes'] if simulation_markup_components['searchInterface']['attributes'] is not None else "")



            """
            Create the simulation configuration file
            """
            fileName ='/trec_{0}_simulation-{1}.xml'.format(retrModel,str(i))

            i = i +1

            filePath = self.simulationBaseDir + fileName
            simulation_files.append(filePath)

            if not os.path.exists(os.path.dirname(filePath)):
                os.makedirs(os.path.dirname(filePath))

            with open(filePath, "w") as user_file:
                user_file.write(simulation_markup)

            user_file.close()
        self.simulConfigPaths = simulation_files




    def appendSimiirPath(self):
        """
        Given a dictionary form of the XML files and the full Simiir toolkit path, appends it to the approprirate attributes
        """

        """
        For topics
        """
        for topic in self.dictRepr['simulationConfiguration']['topics']:
            topic['@qrelsFilename']="{0}{1}".format(self.simiirPath,topic['@qrelsFilename'])
            topic['@filename'] = "{0}{1}".format(self.simiirPath,topic['@filename'])

        """
        For the Search Interface
        """
        for searchInterface in self.dictRepr['simulationConfiguration']['searchInterface']:
            searchInterface['attribute'][0]['@value'] ='{0}{1}'.format(self.simiirPath, searchInterface['attribute'][0]['@value'])

        """
        For the Query Generator
        """
        for queryGenerator in self.dictRepr['simulationConfiguration']['queryGenerator']:
            queryGenerator['attribute']['@value'] = "{0}{1}".format(self.simiirPath,queryGenerator['attribute']['@value'])

        """
        For the document Classifier
        """
        for textClassifier in self.dictRepr['simulationConfiguration']['textClassifiers']['documentClassifier']:
            if 'attribute' not in textClassifier:
                break
            else:
                textClassifier['attribute'][0]['@value'] = "{0}{1}".format(self.simiirPath,textClassifier['attribute'][0]['@value'])

        """
        For the snippet Classifier
        """
        for snippetClassifier in self.dictRepr['simulationConfiguration']['textClassifiers']['snippetClassifier']:
            if 'attribute' not in snippetClassifier:
                break
            else:
                snippetClassifier['attribute'][0]['@value'] = "{0}{1}".format(self.simiirPath,snippetClassifier['attribute'][0]['@value'])

    def generateSimulationPathsFile(self):
        """
        Create a text file with the path of each simulation configuration
        """
        write_path = os.path.join(self.simulationBaseDir,'simulationPaths.txt')
        with open(write_path, "w") as file:
                for SimulationPath in self.simulConfigPaths:
                    file.write(SimulationPath+"\n")
        file.close()

        if self.userFlag == '-u':
            write_path = os.path.join(self.simulationBaseDir,'userPaths.txt')
            with open(write_path, "w") as file:
                    for userPath in self.userConfigPaths:
                        file.write(userPath+"\n")
            file.close()


def usage(filename):
    """
    Prints the usage to stdout.
    """
    print "Usage: python {0} <xml_source> <simiir_path> <-u>(optional)".format(filename)
    print "Where:"
    print "  <xml_source>: the source XML file from which to generate simulation configuration files. See example.xml."
    print "  <simiir_path>: the path to the simiir toolkit. (i.e. home/simiir)"
    print "  <-u>: This flag is used when user configurations will be appended at a later state (i.e. with PreRolled Qrels)"


def main():

    if len(sys.argv) > 2:

        simiirPathabs = os.path.abspath(sys.argv[2])

        if len(sys.argv) == 4:
            flag = sys.argv[3]
        else:
            flag = ''

        sim1 = SimulatorConfigurator(sys.argv[1],simiirPathabs, flag)

        sim1.build_dictionary()

        sim1.tidy_dictionary()

        sim1.appendSimiirPath()
        sim1.get_permutations()

        sim1.generate_markup_userFiles()
        sim1.generate_markup_simulationFiles()

        sim1.generateSimulationPathsFile()

        print '... the necessary files were created!'

        sys.exit(0)

    # Invalid number of command-line parameters, print usage.
    usage(sys.argv[0])
    sys.exit(1)

if __name__ == '__main__':
    main()
