__author__ = 'angelos'
import os
import csv
import sys

#Clears output folder
def clearOutFolder(folder):
    for file in os.listdir(folder):
        file_path = os.path.join(folder, file)

        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
            #elif os.path.isdir(file_path): shutil.rmtree(file_path)
        except Exception, e:
            print e

# Writes evaluation measures for each simulation run to CSV file
def writeCsvFile(data,fileOutPath):
    fileOut = open(fileOutPath, 'w')

    try:
        writer = csv.writer(fileOut)
        writer.writerow(('Run', 'IR Model','Topic','Query Generator','Stopping Strategy',
                          'Stopping Strategy Value','CG_Value', 'Total Queries Issued',
                         'Total Snippets Examined', 'Total Documents Examined', 'Total Documents Marked Relevant', 'Mean Depth Value',
                         'Total Time Taken','Map', 'P@5', 'P@10', 'P@15', 'P@20', 'P@30')
                         )

        for item in data:
            lineSplit = item.split(',')
            writer.writerow((lineSplit[0],lineSplit[1],lineSplit[2],lineSplit[3],lineSplit[4],lineSplit[5],lineSplit[6], lineSplit[7],
                             lineSplit[8], lineSplit[9], lineSplit[10], lineSplit[11], lineSplit[12], lineSplit[13], lineSplit[14],
                             lineSplit[15], lineSplit[16], lineSplit[17], lineSplit[18]))

    finally:
        fileOut.close()


#Find the relevance of the marked-as-relevant documents in the qrels files
def cgCalculator(simiirDir,relevantDocs, topic):

    cg = 0
    fileName = os.path.join(simiirDir,'example_data/qrels/trec2005.qrels')
    with open(fileName, 'r') as qrelFile:

        for docId in relevantDocs:

            for line in qrelFile:
                if (docId in line) and (topic in line):
                    #print 'CG for '+ docId +' ' + line.split(' ')[3]
                    cg = cg + int(line.split(' ')[3])

            #return to beginning of file
            qrelFile.seek(0)

    return cg

def extractLogFileInfo(fileIn):
    """
    Given the logFile of a Run, extract & return:
      - Documents that marked as relevant
      - Total Queries Issued
      - Total Snippets Examined
      - Total Documents Examined
      - Total Documents Marked Relevant
    """

    relevantDocs = []
    total_queries_issued = ''
    total_snips_examined = ''
    total_docs_examined = ''
    total_docs_markedRel = ''
    total_time_taken = ''

    for line in fileIn:
        if 'CONSIDERED_RELEVANT' in line:
            relevantDocs.append(line.split(' ')[5].replace('\n',''))
        elif 'TOTAL_QUERIES_ISSUED' in line:
            total_queries_issued = line.split(' ')[-1].replace('\n','')
        elif 'TOTAL_SNIPPETS_EXAMINED' in line:
            total_snips_examined = line.split(' ')[-1].replace('\n','')
        elif 'TOTAL_DOCUMENTS_EXAMINED' in line:
            total_docs_examined = line.split(' ')[-1].replace('\n','')
        elif 'TOTAL_DOCUMENTS_MARKED_RELEVANT' in line:
            total_docs_markedRel = line.split(' ')[-1].replace('\n','')
        #This is to extract the total time taken
        if 'ACTION' in line:
            total_time_taken = line.split(' ')[3]


    return (relevantDocs, total_queries_issued, total_snips_examined, total_docs_examined, total_docs_markedRel, total_time_taken)

def extractOutFileInfo(fileIn):
    """
    Given the outFile of a Run, extract & return:
      - MAP value
      - P values (@5, @10, @15, @20, @30)
    """
    map1 =''
    p5 = ''
    p10 = ''
    p15 = ''
    p20 = ''
    p30 = ''

    for line in fileIn:

        if 'map' in line and 'gm_map' not in line:
            map1 =line.split('\t')[-1].replace('\n','')
        elif 'P_5 ' in line:
            p5 = line.split('\t')[-1].replace('\n','')
        elif 'P_10 ' in line:
            p10 = line.split('\t')[-1].replace('\n','')
        elif 'P_15 ' in line:
            p15 = line.split('\t')[-1].replace('\n','')
        elif 'P_20 ' in line:
            p20 = line.split('\t')[-1].replace('\n','')
        elif 'P_30 ' in line:
            p30 = line.split('\t')[-1].replace('\n','')

    return (map1,p5,p10,p15,p20,p30)

def usage(filename):
    """
    Prints the usage to stdout.
    """
    print "Usage: python {0} <simiir_path>".format(filename)
    print "Where:"
    print "  <input_dir>: the path to the output files of the simulator i.e. /home/Simulator/output."
    print "  <simiir_path>: the path to the simiir toolkit i.e. /home/simiir."
    print "  <file_out>: specify a directory and name for the output CSV file i.e. /home/out.csv."


if __name__ == '__main__':
    if len(sys.argv) > 3 and len(sys.argv) < 5:

        data = []
        dataDict ={}
        indir = sys.argv[1]
        simiirDir = sys.argv[2]
        fileOutPath = sys.argv[3]

        #Iterates through all the .log files in the output dir
        for root, dirs, filenames in os.walk(indir):
            for fileName in filenames:
                if '.log' in fileName:

                    logFile = open(os.path.join(root, fileName),'r')
                    outFile = open(os.path.join(root,fileName[:-4]+'.out'),'r')
                    relevantDocs, total_queries_issued, total_snips_examined, total_docs_examined, total_docs_markedRel, total_time_taken = extractLogFileInfo(logFile)
                    map1, p5, p10, p15, p20, p30 = extractOutFileInfo(outFile)


                    #Extract topic from fileName
                    topic = fileName.split('-')[2]
                    #Caclulate the CG value
                    cgValue = cgCalculator(simiirDir,relevantDocs, topic)

                    #Extract some more Information from fileName & root path
                    titles = fileName.split('_')
                    run = root.split('/')[-1]
                    model = titles[1]
                    queryGenerator = titles[3]
                    stoppingStrategy = titles[4].split('-')[0]
                    stoppingStrategyVal = titles[4].split('-')[1][:-4]

                    #Calculate mean depth value

                    if total_snips_examined =='' or total_queries_issued == '':
                        mean_depth = ''
                    else:
                        mean_depth = float(total_snips_examined)/float(total_queries_issued)
                        mean_depth = str(mean_depth)

                    #Append the information in a list
                    data.append(run + ',' + model + ',' + topic + ',' + queryGenerator + ',' +stoppingStrategy + ','
                                + stoppingStrategyVal + ',' + str(cgValue) + ',' + total_queries_issued + ',' +
                                total_snips_examined + ',' + total_docs_examined + ',' + total_docs_markedRel + ',' + mean_depth + ',' + total_time_taken
                                + ',' + map1 + ',' + p5 + ',' + p10 + ',' + p15 + ','
                                + p20 + ',' + p30)



        writeCsvFile(data, fileOutPath)
        #clearOutFolder(indir)
        sys.exit(0)

    # Invalid number of command-line parameters, print usage.
    usage(sys.argv[0])
    sys.exit(1)


