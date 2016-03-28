__author__ = 'Angelos Constantinides'
import os
import csv
import sys


class SimulatorOutputAnalyser():
    def __init__(self, input_dir, simiir_path, file_out):
        self.input_dir = input_dir
        self.file_out = file_out
        self.simiir_path = simiir_path
        self.data_out = []

    def writeCsvFile(self):
        """
        Provided the data from the object, write them to the csv file specified
        """
        fileOut = open(self.file_out, 'w')

        try:
            writer = csv.writer(fileOut)
            writer.writerow(('Run', 'IR Model', 'Topic', 'Query Generator', 'Stopping Strategy',
                             'Stopping Strategy Value', 'CG_Value', 'Total Queries Issued',
                             'Total Snippets Examined', 'Total Documents Examined', 'Total Documents Marked Relevant',
                             'Mean Depth Value',
                             'Total Time Taken', 'Map', 'P@5', 'P@10', 'P@15', 'P@20', 'P@30')
                            )

            for item in self.data_out:
                lineSplit = item.split(',')
                writer.writerow((lineSplit[0], lineSplit[1], lineSplit[2], lineSplit[3], lineSplit[4], lineSplit[5],
                                 lineSplit[6], lineSplit[7],
                                 lineSplit[8], lineSplit[9], lineSplit[10], lineSplit[11], lineSplit[12], lineSplit[13],
                                 lineSplit[14],
                                 lineSplit[15], lineSplit[16], lineSplit[17], lineSplit[18]))

        finally:
            fileOut.close()

    def cgCalculator(self, relevantDocs, topic):
        """
        Given the relevant documents and the topic of a simulation run retrun the Cumulative Gain
        using the qrels file
        """

        cg = 0
        fileName = os.path.join(self.simiir_path, 'example_data/qrels/trec2005.qrels')
        with open(fileName, 'r') as qrelFile:

            for docId in relevantDocs:

                for line in qrelFile:
                    if (docId in line) and (topic in line):
                        cg = cg + int(line.split(' ')[3])

                # return to beginning of file
                qrelFile.seek(0)

        return cg

    def meanDepthCalculator(self, total_snips_examined, total_queries_issued):
        """
        Given the total snippets examined and total queries issued return the mean depth of the simulation run
        """
        if total_snips_examined == '' or total_queries_issued == '':
            mean_depth = '0'
        else:
            mean_depth = float(total_snips_examined) / float(total_queries_issued)
            mean_depth = str(mean_depth)

        return mean_depth

    def extractLogFileInfo(self, fileIn):
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
                relevantDocs.append(line.split(' ')[5].replace('\n', ''))
            elif 'TOTAL_QUERIES_ISSUED' in line:
                total_queries_issued = line.split(' ')[-1].replace('\n', '')
            elif 'TOTAL_SNIPPETS_EXAMINED' in line:
                total_snips_examined = line.split(' ')[-1].replace('\n', '')
            elif 'TOTAL_DOCUMENTS_EXAMINED' in line:
                total_docs_examined = line.split(' ')[-1].replace('\n', '')
            elif 'TOTAL_DOCUMENTS_MARKED_RELEVANT' in line:
                total_docs_markedRel = line.split(' ')[-1].replace('\n', '')
            # This is to extract the total time taken
            if 'ACTION' in line:
                total_time_taken = line.split(' ')[3]

        return (relevantDocs, total_queries_issued, total_snips_examined, total_docs_examined, total_docs_markedRel,
                total_time_taken)

    def appendSimData(self):
        """
        Parse the necessary information and append them into a data structure
        """
        for root, dirs, filenames in os.walk(self.input_dir):
            for fileName in filenames:
                if '.log' in fileName:

                    logFile = open(os.path.join(root, fileName), 'r')
                    outFile = open(os.path.join(root, fileName[:-4] + '.out'), 'r')

                    relevantDocs, total_queries_issued, total_snips_examined, total_docs_examined, total_docs_markedRel, total_time_taken = self.extractLogFileInfo(
                        logFile)
                    map1, p5, p10, p15, p20, p30 = self.extractOutFileInfo(outFile)

                    # Extract topic from fileName
                    topic = fileName.split('-')[2]

                    # Caclulate the CG value
                    cgValue = self.cgCalculator(relevantDocs, topic)
                    mean_depth = self.meanDepthCalculator(total_snips_examined, total_queries_issued)

                    # Extract some more Information from fileName & root path
                    titles = fileName.split('_')
                    run = root.split('/')[-1]

                    model = titles[1]
                    queryGenerator = titles[3]
                    stoppingStrategy = titles[4].split('-')[0]
                    stoppingStrategyVal = titles[4].split('-')[1]

                    self.data_out.append(run + ',' + model + ',' + topic + ',' + queryGenerator + ',' + stoppingStrategy + ','
                                         + stoppingStrategyVal + ',' + str(cgValue) + ',' + total_queries_issued + ',' +
                                         total_snips_examined + ',' + total_docs_examined + ',' + total_docs_markedRel + ',' + mean_depth + ',' + total_time_taken
                                         + ',' + map1 + ',' + p5 + ',' + p10 + ',' + p15 + ','
                                         + p20 + ',' + p30)

    def extractOutFileInfo(self, fileIn):
        """
        Given the outFile of a Run, extract & return:
          - MAP value
          - P values (@5, @10, @15, @20, @30)
        """
        map1 = '0'
        p5 = '0'
        p10 = '0'
        p15 = '0'
        p20 = '0'
        p30 = '0'

        for line in fileIn:

            if 'map' in line and 'gm_map' not in line:
                map1 = line.split('\t')[-1].replace('\n', '')
            elif 'P_5 ' in line:
                p5 = line.split('\t')[-1].replace('\n', '')
            elif 'P_10 ' in line:
                p10 = line.split('\t')[-1].replace('\n', '')
            elif 'P_15 ' in line:
                p15 = line.split('\t')[-1].replace('\n', '')
            elif 'P_20 ' in line:
                p20 = line.split('\t')[-1].replace('\n', '')
            elif 'P_30 ' in line:
                p30 = line.split('\t')[-1].replace('\n', '')

        return (map1, p5, p10, p15, p20, p30)




def usage(filename):
    """
    Prints the usage to stdout.
    """
    print "Usage: python {0} <simiir_path>".format(filename)
    print "Where:"
    print "  <input_dir>: the path to the output files of the simulator i.e. /home/Simulator/output."
    print "  <simiir_path>: the path to the simiir toolkit. (i.e. home/simiir)"
    print "  <file_out>: specify a directory and name for the output CSV file i.e. /home/out.csv."


def main():
    if len(sys.argv) > 3 and len(sys.argv) < 5:

        simAnalyser = SimulatorOutputAnalyser(sys.argv[1], sys.argv[2], sys.argv[3])
        simAnalyser.appendSimData()
        simAnalyser.writeCsvFile()

        print "The output file was successfully created to the following path: " + simAnalyser.file_out

        sys.exit(0)

    # Invalid number of command-line parameters, print usage.
    usage(sys.argv[0])
    sys.exit(1)


if __name__ == '__main__':
    main()
