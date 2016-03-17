__author__ = 'angelos'

# The following python script generates User Configuration (XML) files
# for the simiir toolkit based on user input (of Text File Input)

from xml.etree.ElementTree import ElementTree,Element
import xml.etree.ElementTree as etree
import os.path
from xml.dom import minidom


#Inputs

#Set UserConfigurationId
def setUserConfigId():
    userConfigId = raw_input('Enter User Configuration id: ')
    return userConfigId

#Set QueryGenerator
def setQueryGen():
    queryGeneratorIn = raw_input('Enter Query Generator Component: ')
    return queryGeneratorIn

#Set StoppingDecisionMaker & Value
def setStopDeciMaker():
    stoppingDecisionMakerIn = raw_input('Enter Stopping Decision Maker: ')


    if stoppingDecisionMakerIn == 'FixedDepthDecisionMaker':
        stopDecMakerValType ='depth'

    elif stoppingDecisionMakerIn == 'SequentialNonrelDecisionMakerSkip':
        stopDecMakerValType ='nonrelevant_threshold'
    else:
        print'Specify a known Stopping Decision Maker (i.e. FixedDepthDecisionMaker, SequentialNonrelDecisionMakerSkip)'
        return setStopDeciMaker()

    stopDecMakerVal = raw_input('Enter ' + stopDecMakerValType + ' value: ')

    return {1:stoppingDecisionMakerIn, 2:str(stopDecMakerVal), 3:stopDecMakerValType }

#Set Directory & File Name
def setDirFileName():

    save_path = raw_input('Enter Full Directory to save the File(Leave Blank for current dir): ')

    if not save_path:
        save_path='./'

    if not (os.path.exists(save_path)):
        print('Enter an existing directory')
        return setDirFileName()

    fileName = raw_input('Enter File Name(Leave Blank: user): ')

    #default name if left blank
    if not fileName:
        fileName = 'user'

    completeName = os.path.join(save_path, fileName+".xml")
    return completeName


#XML Generator function.
def xmlGenerator(userConfigId, queryGeneratorIn, stoppingDecisionMakerIn, stopDecMakerValType, stopDecMakerVal, completeNameDir):

    root = Element('userConfiguration')
    root.set('id',userConfigId)

    #Tree Element
    tree = ElementTree(root)

    #Query Generator
    queryGenerator = Element('queryGenerator')
    queryGenerator.set('class',queryGeneratorIn)

    root.append(queryGenerator)

    #Attributes - (Query Generator)
    queryGenAttr = Element('attribute')
    queryGenerator.append(queryGenAttr)

    # queryGenAttr keys & values
    queryGenAttr.set('name', 'stopword_file')
    queryGenAttr.set('type', 'string')
    queryGenAttr.set('value', '../example_data/terms/stopwords.txt')
    queryGenAttr.set('is_argument', 'true')

    # Text Classifier
    textClassifiers=Element('textClassifiers')
    root.append(textClassifiers)

    #Snippet Classifier
    snippetClassifier=Element('snippetClassifier')
    snippetClassifier.set('class','InformedTrecTextClassifier')
    textClassifiers.append(snippetClassifier)

    # Attributes - (Snippet Classifier)
    snippClasAttr1=Element('attribute')
    snippClasAttr2=Element('attribute')
    snippClasAttr3=Element('attribute')

    # snippClasAttr 1 keys & Values
    snippClasAttr1.set('name', 'qrel_file')
    snippClasAttr1.set('type', 'string')
    snippClasAttr1.set('value', '../example_data/qrels/trec2005.qrels.all')
    snippClasAttr1.set('is_argument', 'true')

    # snippClasAttr 2 keys & Values
    # Clicking a relevant snippet Probability
    snippClasAttr2.set('name', 'rprob')
    snippClasAttr2.set('type', 'float')
    snippClasAttr2.set('value', '0.36')
    snippClasAttr2.set('is_argument', 'true')

    # snippClasAttr 3 keys & Values
    # Clicking a non-relevant snippet
    snippClasAttr3.set('name', 'nprob')
    snippClasAttr3.set('type', 'float')
    snippClasAttr3.set('value', '0.21')
    snippClasAttr3.set('is_argument', 'true')

    snippetClassifier.append(snippClasAttr1)
    snippetClassifier.append(snippClasAttr2)
    snippetClassifier.append(snippClasAttr3)

    #Document Classifier
    documentClassifier=Element('documentClassifier')
    documentClassifier.set('class','InformedTrecTextClassifier')
    textClassifiers.append(documentClassifier)

    # Attributes - (Document Classifier)
    docClasAttr1=Element('attribute')
    docClasAttr2=Element('attribute')
    docClasAttr3=Element('attribute')

    # docClasAttr 1 keys & Values
    docClasAttr1.set('name', 'qrel_file')
    docClasAttr1.set('type', 'string')
    docClasAttr1.set('value', '../example_data/qrels/trec2005.qrels.all')
    docClasAttr1.set('is_argument', 'true')

    # docClasAttr 2 keys & Values
    # Marking a relevant document
    docClasAttr2.set('name', 'rprob')
    docClasAttr2.set('type', 'float')
    docClasAttr2.set('value', '0.71')
    docClasAttr2.set('is_argument', 'true')

    # docClasAttr 3 keys & Values
    # Marking a non-relevant document
    docClasAttr3.set('name', 'nprob')
    docClasAttr3.set('type', 'float')
    docClasAttr3.set('value', '0.53')
    docClasAttr3.set('is_argument', 'true')

    documentClassifier.append(docClasAttr1)
    documentClassifier.append(docClasAttr2)
    documentClassifier.append(docClasAttr3)

    #Stopping Decision Maker
    stoppingDecisionMaker=Element('stoppingDecisionMaker')
    stoppingDecisionMaker.set('class',stoppingDecisionMakerIn)
    root.append(stoppingDecisionMaker)

    # Attributes - (Stopping Decision Maker)
    stopDecMakAttr=Element('attribute')
    stopDecMakAttr.set('name', stopDecMakerValType)
    stopDecMakAttr.set('type', 'integer')
    stopDecMakAttr.set('value', stopDecMakerVal)
    stopDecMakAttr.set('is_argument', 'true')

    stoppingDecisionMaker.append(stopDecMakAttr)


    #Logger
    logger=Element('logger')
    logger.set('class','FixedCostLogger')
    root.append(logger)


    # Attributes - (Logger)
    logAttr1=Element('attribute')
    logAttr2=Element('attribute')
    logAttr3=Element('attribute')
    logAttr4=Element('attribute')
    logAttr5=Element('attribute')
    logAttr6=Element('attribute')

    # logAttr 1 keys & Values
    logAttr1.set('name', 'time_limit')
    logAttr1.set('type', 'integer')
    logAttr1.set('value', '1200')
    logAttr1.set('is_argument', 'true')

    # logAttr 2 keys & Values
    logAttr2.set('name', 'query_cost')
    logAttr2.set('type', 'float')
    logAttr2.set('value', '15.1')
    logAttr2.set('is_argument', 'true')

    # logAttr 3 keys & Values
    logAttr3.set('name', 'document_cost')
    logAttr3.set('type', 'float')
    logAttr3.set('value', '21.45')
    logAttr3.set('is_argument', 'true')

    # logAttr 4 keys & Values
    logAttr4.set('name', 'snippet_cost')
    logAttr4.set('type', 'float')
    logAttr4.set('value', '1.3')
    logAttr4.set('is_argument', 'true')

    # logAttr 5 keys & Values
    logAttr5.set('name', 'serp_results_cost')
    logAttr5.set('type', 'float')
    logAttr5.set('value', '1.1')
    logAttr5.set('is_argument', 'true')

    # logAttr 6 keys & Values
    logAttr6.set('name', 'mark_document_cost')
    logAttr6.set('type', 'float')
    logAttr6.set('value', '2.57')
    logAttr6.set('is_argument', 'true')

    logger.append(logAttr1)
    logger.append(logAttr2)
    logger.append(logAttr3)
    logger.append(logAttr4)
    logger.append(logAttr5)
    logger.append(logAttr6)

    #Search Context
    searchContext=Element('searchContext')
    searchContext.set('class','SearchContextRevisedRelevance')
    root.append(searchContext)


    xmlstr = minidom.parseString(etree.tostring(root)).toprettyxml(indent="   ")
    with open(completeNameDir, "w") as f:
        f.write(xmlstr)


# Read From File Function
def setTextFile():

    path = raw_input('Please enter the full directory to the file: ')

    try:
        with open(path,'r') as f:
            for line in f:
                lineList = line.split(',')

                #Call xmlGenerator for each line
                xmlGenerator(lineList[0],lineList[1],lineList[2],lineList[3],lineList[4],lineList[5].replace('\n', '').replace('\r', ''))

    except (OSError, IOError) as e:
        print 'Please enter the correct dir to an existing file'
        setTextFile()



## Main ##

option = raw_input('Input From File(y/n): ')

if option.lower() == 'y':
    setTextFile()
else:
    while(True):
        # Get User Input
        userConfigId = setUserConfigId()
        queryGen = setQueryGen()
        decMakerDict = setStopDeciMaker()
        dirFileName = setDirFileName()

        print dirFileName

        # XML gen. function call
        #           (UserConfig.ID,Query Gen.Comp,Stop. Deci. Maker, S.D.M Type(i.e depth ..etc), S.D.M Value, Dir+Filename.xml
        xmlGenerator(userConfigId, queryGen, decMakerDict[1], decMakerDict[2], decMakerDict[3], dirFileName)

        #Prompt to generate more XML files
        generateAnother = raw_input('Would you like to generate another XML file?(y/n): ')
        if generateAnother.lower() == 'n':
            break
