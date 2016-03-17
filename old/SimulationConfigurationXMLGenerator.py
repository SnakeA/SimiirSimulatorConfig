from xml.dom import minidom

__author__ = 'angelos'

# The following python script generates Simulation Configuration (XML) files
# for the simiir toolkit based on user input

from xml.etree.ElementTree import ElementTree, Element
import xml.etree.ElementTree as etree
import os.path


# Set SimulationConfigurationId
def setSimConfigId():
    simConfigId = raw_input('Enter Simulation Configuration id: ')
    return simConfigId

# Set Output Base Directory
def setOutBaseDir():
    outBaseDir = raw_input('Enter output Base Directory (Blank for Default): ')

    if not outBaseDir:
        return '../example_sims/output/'

    return outBaseDir


# Set Topics (conifgurations)
def setTopics():
    topicsIn = raw_input('Enter Topic(s) (i.e. 365,465): ')
    return topicsIn.split(',')


# Set Users (conifgurations)
def setUsers():
    usersIn = raw_input('Enter User(s) (i.e. smart_user,fixed_depth_user): ')
    return usersIn.split(',')


# Set Retrieval Model
def setRetrModel():
    retrModel = raw_input('Enter Retrieval Model (TFID, BM25 or PL2(default)): ')

    retrModel = retrModel.lower()

    # Default Retrieval Model is PL2
    if retrModel == 'tfid':
        return '0'
    elif retrModel == 'bm25':
        return '1'
    else:
        return '2'


# Set Directory & File Name
def setDirFileName():
    save_path = raw_input('Enter Full Directory to save the File(Leave Blank for current dir): ')

    if not save_path:
        save_path = './'

    if not (os.path.exists(save_path)):
        print('Enter an existing directory')
        return setDirFileName()

    fileName = raw_input('Enter File Name(Leave Blank: configuration): ')

    # default name if left blank
    if not fileName:
        fileName = 'configuration'

    completeName = os.path.join(save_path, fileName + ".xml")
    return completeName


# Append a topic
def addTopic(topic1):
    topic = Element('topic')
    topic.set('id', topic1)
    topic.set('filename', '../example_data/topics/topic.' + topic1)
    topic.set('qrelsFilename', '../example_data/qrels/trec2005.qrels')

    return topic


# Append a user
def addUser(user1):
    user = Element('user')
    user.set('configurationFile', '../example_sims/users/' + user1 + '.xml')

    return user


# XML Generator function.
def xmlGenerator(simConfigId, outBaseDir, topicsSellected, usersSellected, retModel, completeNameDir):
    root = Element('simulationConfiguration')
    root.set('id', simConfigId)

    # Tree Element
    tree = ElementTree(root)

    # Output
    output = Element('output')

    # Output Keys & Values
    output.set('baseDirectory', outBaseDir)
    output.set('saveInteractionLog', 'true')
    output.set('saveRelevanceJudgments', 'true')
    output.set('trec_eval', 'true')

    root.append(output)

    # Topics
    topics = Element('topics')

    # Append all sellected Topics
    for topic1 in topicsSellected:
        topics.append(addTopic(topic1))

    root.append(topics)


    # Users
    users = Element('users')

    # Append all sellected Users
    for user1 in usersSellected:
        users.append(addUser(user1))

    root.append(users)

    # Search Interface
    searchInterface = Element('searchInterface')
    searchInterface.set('class', 'WhooshSearchInterface')

    # Attributes - (Search Interface)
    searchInterfaceAttr1 = Element('attribute')
    searchInterfaceAttr2 = Element('attribute')
    searchInterfaceAttr3 = Element('attribute')


    # searchInterfaceAttr 1 keys & Values
    searchInterfaceAttr1.set('name', 'whoosh_index_dir')
    searchInterfaceAttr1.set('type', 'string')
    searchInterfaceAttr1.set('value', '../example_data/fullindex')
    searchInterfaceAttr1.set('is_argument', 'true')

    # searchInterfaceAttr 2 keys & Values
    searchInterfaceAttr2.set('name', 'implicit_or')
    searchInterfaceAttr2.set('type', 'boolean')
    searchInterfaceAttr2.set('value', '1')
    searchInterfaceAttr2.set('is_argument', 'true')

    # searchInterfaceAttr 3 keys & Values - Retrieval Model
    searchInterfaceAttr3.set('name', 'model')
    searchInterfaceAttr3.set('type', 'integer')
    searchInterfaceAttr3.set('value', retModel)
    searchInterfaceAttr3.set('is_argument', 'true')

    searchInterface.append(searchInterfaceAttr1)
    searchInterface.append(searchInterfaceAttr2)
    searchInterface.append(searchInterfaceAttr3)

    root.append(searchInterface)

    #Write to file as pretty XML
    xmlstr = minidom.parseString(etree.tostring(root)).toprettyxml(indent="   ")
    with open(completeNameDir, "w") as f:
        f.write(xmlstr)


while(True):
    # Call XML generator with setters
    xmlGenerator(setSimConfigId(), setOutBaseDir(), setTopics(), setUsers(), setRetrModel(), setDirFileName())

    generateAnother = raw_input('Would you like to generate another XML file?(y/n): ')
    if generateAnother.lower() == 'n':
        break