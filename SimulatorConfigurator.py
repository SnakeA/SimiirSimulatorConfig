import os
import itertools
import sys
import importlib
import inspect
from lxml import etree
from xml.etree import cElementTree
from collections import defaultdict



def get_available_classes(componentsPath, component):
    """
    Given the componentsPath (i.e. where the components (queryGen, StoppingDec etc) are located) and the specific component
    Import all modules and return the names of the valid classes.
    This is used for input validation purposes
    """
    sys.path.append(componentsPath)

    finalPath = os.path.join(componentsPath,component)

    modules = []
    classes = set()

    # List through the modules in the specified package, ignoring __init__.py, and append them to a list.
    for f in os.listdir(finalPath):
        if f.endswith('.py') and not f.startswith('__init__'):
            modules.append('{0}.{1}'.format(component, os.path.splitext(f)[0]))

    module_references = []

    # Attempt to import each module in turn so we can access its classes
    for module in modules:
        module_references.append(importlib.import_module(module))


    # Now loop through each module, looking at the classes within it - and then add each class to a set of valid classes.
    for module in module_references:
        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj):
                classes.add(name)

    return classes

def read_file_to_string(filename):
    """
    Given a filename, opens the file and returns the contents as a string.
    https://github.com/leifos/simiir/blob/master/simiir/sim_config_generator/sim_config_generator.py
    """
    f = open(filename, 'r')
    file_str = ""

    for line in f:
        file_str = "{0}{1}".format(file_str, line)

    f.close()
    return file_str

def build_dictionary(input_filename):
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

    config_file = etree.parse(input_filename)
    string_repr = etree.tostring(config_file, pretty_print=True)
    element_tree = cElementTree.XML(string_repr)

    return recursive_generation(element_tree)

def tidy_dictionary(dict_repr):

    """
    Create a list for the specified reference and add type
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
    dict_repr['simulationConfiguration']['queryGenerator'] = to_list(dict_repr['simulationConfiguration']['queryGenerator'], 'queryGenerator')
    dict_repr['simulationConfiguration']['textClassifiers']['snippetClassifier'] = to_list(dict_repr['simulationConfiguration']['textClassifiers']['snippetClassifier'], 'snippetClassifier')
    dict_repr['simulationConfiguration']['textClassifiers']['documentClassifier'] = to_list(dict_repr['simulationConfiguration']['textClassifiers']['documentClassifier'], 'documentClassifier')
    dict_repr['simulationConfiguration']['stoppingDecisionMaker'] = to_list(dict_repr['simulationConfiguration']['stoppingDecisionMaker'], 'stoppingDecisionMaker')
    dict_repr['simulationConfiguration']['logger'] = to_list(dict_repr['simulationConfiguration']['logger'], 'logger')
    dict_repr['simulationConfiguration']['searchContext'] = to_list(dict_repr['simulationConfiguration']['searchContext'], 'searchContext')

    """
    Lists for the Simulator Configuration
    """
    dict_repr['simulationConfiguration']['topics'] = to_list(dict_repr['simulationConfiguration']['topics'], 'topics')
    dict_repr['simulationConfiguration']['searchInterface'] = to_list(dict_repr['simulationConfiguration']['searchInterface'], 'searchInterface')



def get_permutations(dict_repr,type):
    """
    Contains a list of tuples, with each tuple containing dictionaries representing a particular combination.
    Note that topics are ignored; these are stored within the simulation configuration file.
    """
    query_generators = dict_repr['simulationConfiguration']['queryGenerator']
    snippet_classifiers = dict_repr['simulationConfiguration']['textClassifiers']['snippetClassifier']
    document_classifiers = dict_repr['simulationConfiguration']['textClassifiers']['documentClassifier']
    decision_makers = dict_repr['simulationConfiguration']['stoppingDecisionMaker']
    loggers =  dict_repr['simulationConfiguration']['logger']
    search_contexts = dict_repr['simulationConfiguration']['searchContext']
    search_interfaces = dict_repr['simulationConfiguration']['searchInterface']



    if type == 'user':
        return list(itertools.product(query_generators,
                                      snippet_classifiers,
                                      document_classifiers,
                                      decision_makers,
                                      loggers,
                                      search_contexts))
    else:
        return list(itertools.product(search_interfaces))

def create_attribute_markup(attribute_dict):
    """
    Given a dictionary representing an attribute, returns the associated XML markup for that attribute component.
    """
    attribute_markup = read_file_to_string('base_files/attribute.xml')
    value = attribute_dict['@value'].replace('[[ base_dir ]]', simulation_base_dir)

    attribute_markup = attribute_markup.format(attribute_dict['@name'],
                                               attribute_dict['@type'],
                                               value,
                                               attribute_dict['@is_argument'])

    return attribute_markup

def generate_topics(dict_repr):
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

    topics_list = dict_repr['simulationConfiguration']['topics']
    topics_str = ""

    for entry in topics_list:
        topics_str = "{0}{1}".format(topics_str, generate_topic_markup(entry))

    return topics_str

def generate_user_entries(user_permuatation_list):
    """
    Returns a series of XML components for user objects in the simulation file.
    https://github.com/leifos/simiir/blob/master/simiir/sim_config_generator/sim_config_generator.py
    """
    entry_list = ""

    for entry in user_permuatation_list:
        user_markup = read_file_to_string('base_files/user_entry.xml')
        entry_list = "{0}{1}".format(entry_list, user_markup.format(entry))

    return entry_list

def generate_search_interface_markup(dict_repr):
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



def generate_markup_userFiles(dict_repr, permutations, simiirPath):
    """
    Given a tuple of dictionary objects, generates the markup & create files for the associated users. Returns a list with the full paths of the user config. files
    """

    user_files = []

    global simulation_base_dir
    simulation_base_dir = dict_repr['simulationConfiguration']['@baseDir']

    componentsPath = os.path.join(simiirPath,'simiir')

    for iteration in permutations:
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
                    user_markup_components[component_type]['attributes'] = create_attribute_markup(component_attributes)
                else:
                    for attribute in component_attributes:
                        if user_markup_components[component_type]['attributes'] is None:
                            user_markup_components[component_type]['attributes'] = ""
                        user_markup_components[component_type]['attributes'] = "{0}{1}".format(user_markup_components[component_type]['attributes'], create_attribute_markup(attribute))


        # File Name includes queryGenerator_StoppinStrategy-Value
        fileName = '/user_{0}_{1}-{2}.xml'.format(user_markup_components['queryGenerator']['class'],
                                                 user_markup_components['stoppingDecisionMaker']['class'],
                                                 user_markup_components['stoppingDecisionMaker']['attributes'].split('value="')[1].split('"')[0])

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
        filePath = simulation_base_dir + fileName
        user_files.append(filePath)


        if not os.path.exists(os.path.dirname(filePath)):
            os.makedirs(os.path.dirname(filePath))

        with open(filePath, "w") as user_file:
            user_file.write(user_markup)

        user_file.close()


    return user_files



def generate_markup_simulationFiles(dict_repr,permutation,users,topics):
    """
    Given a tuple of dictionary objects,topics and users generates the markup & create files for the associated simulations.
    Returns the a list with the full paths of the simulation config. files
    """

    simulation_files = []

    #Count Iterations
    i=0
    for iteration in permutation:

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
                    simulation_markup_components[component_type]['attributes'] = create_attribute_markup(component_attributes)
                else:
                    for attribute in component_attributes:
                        if simulation_markup_components[component_type]['attributes'] is None:
                            simulation_markup_components[component_type]['attributes'] = ""
                        simulation_markup_components[component_type]['attributes'] = "{0}{1}".format(simulation_markup_components[component_type]['attributes'], create_attribute_markup(attribute))


        """
        Find Retrival Model
        """
        retrModelVal=-1

        for comp in dict_repr['simulationConfiguration']['searchInterface'][i]['attribute']:
            if comp['@name'] == 'model':
                retrModelVal = comp['@value']

        if retrModelVal =='0':
            retrModel = 'TFIDF'
        elif retrModelVal == '1':
            retrModel = 'BM25'
        elif retrModelVal == '2':
            retrModel = 'PL2'
        else:
            retrModel = ''


        """
        Construct the simulation configuration markup
        """
        simulation_markup = read_file_to_string('base_files/simulation.xml')
        simulation_markup = simulation_markup.format('trec_{0}_simulation-{1}'.format(retrModel,str(i)),
                                                 os.path.join(dict_repr['simulationConfiguration']['@baseDir'], '{0}/{1}/{2}'),
                                                 topics,
                                                 users,
                                                 simulation_markup_components['searchInterface']['class'],
                                                 simulation_markup_components['searchInterface']['attributes'] if simulation_markup_components['searchInterface']['attributes'] is not None else "")



        """
        Create the simulation configuration file
        """
        fileName ='/trec_{0}_simulation-{1}.xml'.format(retrModel,str(i))

        i = i +1

        filePath = simulation_base_dir + fileName

        simulation_files.append(filePath)

        if not os.path.exists(os.path.dirname(filePath)):
            os.makedirs(os.path.dirname(filePath))

        with open(filePath, "w") as user_file:
            user_file.write(simulation_markup)

        user_file.close()
    return  simulation_files




def appendSimiirPath(dict_repr,simiirPath):
    """
    Given a dictionary form of the XML files and the full Simiir toolkit path, appends it to the approprirate attributes
    """

    """
    For topics
    """
    for topic in dict_repr['simulationConfiguration']['topics']:
        topic['@qrelsFilename']="{0}{1}".format(simiirPath,topic['@qrelsFilename'])
        topic['@filename'] = "{0}{1}".format(simiirPath,topic['@filename'])

    """
    For the Search Interface
    """
    for searchInterface in dict_repr['simulationConfiguration']['searchInterface']:
        searchInterface['attribute'][0]['@value'] ='{0}{1}'.format(simiirPath, searchInterface['attribute'][0]['@value'])

    """
    For the Query Generator
    """
    for queryGenerator in dict_repr['simulationConfiguration']['queryGenerator']:
        queryGenerator['attribute']['@value'] = "{0}{1}".format(simiirPath,queryGenerator['attribute']['@value'])

    """
    For the document Classifier
    """
    for textClassifier in dict_repr['simulationConfiguration']['textClassifiers']['documentClassifier']:
        textClassifier['attribute'][0]['@value'] = "{0}{1}".format(simiirPath,textClassifier['attribute'][0]['@value'])

    """
    For the snippet Classifier
    """
    for snippetClassifier in dict_repr['simulationConfiguration']['textClassifiers']['snippetClassifier']:
        snippetClassifier['attribute'][0]['@value'] = "{0}{1}".format(simiirPath,snippetClassifier['attribute'][0]['@value'])

def generateSimulationPathsFile(simulationFiles):
    """
    Create a text file with the path of each simulation configuration
    """

    with open(simulation_base_dir + "/simulationPaths.txt", "w") as file:
            for SimulationPath in simulationFiles:
                file.write(SimulationPath+"\n")
    file.close()

def usage(filename):
    """
    Prints the usage to stdout.
    """
    print "Usage: python {0} <xml_source> <simiir_path>".format(filename)
    print "Where:"
    print "  <xml_source>: the source XML file from which to generate simulation configuration files. See example.xml."
    print "  <simiir_path>: the path to the simiir toolkit."

if __name__ == '__main__':
    if len(sys.argv) > 2 and len(sys.argv) < 4:

        simiirPath = os.path.abspath(sys.argv[2])

        #componentsPath = os.path.join(simiirPath,'simiir')

        #get_available_classes(componentsPath,'stopping_decision_makers')

        dict_repr = build_dictionary(sys.argv[1])
        tidy_dictionary(dict_repr)

        appendSimiirPath(dict_repr,simiirPath)

        permutations_Users = get_permutations(dict_repr,'user')
        userFiles = generate_markup_userFiles(dict_repr, permutations_Users,simiirPath)

        permutations_Simulator = get_permutations(dict_repr,'simulator')
        users = generate_user_entries(userFiles)
        topics = generate_topics(dict_repr)
        simulationFiles = generate_markup_simulationFiles(dict_repr,permutations_Simulator,users,topics)

        generateSimulationPathsFile(simulationFiles)

        sys.exit(0)

    # Invalid number of command-line parameters, print usage.
    usage(sys.argv[0])
    sys.exit(1)