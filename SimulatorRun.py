__author__ = 'Angelos Constantinides'
import subprocess
import os
import sys
import time
import xml.dom.minidom
from utilities import read_file_to_string
import datetime as dt
import multiprocessing


class SimulatorRun():

    def __init__(self, simulationsPath, simiirWorkingPath, numOfRuns, flag):
        self.simulationsPath = simulationsPath
        self.simiirWorkingPath = simiirWorkingPath
        self.numOfRuns = numOfRuns
        self.numOfProcesses = multiprocessing.cpu_count() # CHANGE this to adjust simultaneous processes!
        self.list_of_SimConfigs = []
        self.list_of_UserConfigs = [] # when flag is used
        self.listOfRuns = []
        self.listOfRefinedUserConfig = [] # when flag is used
        self.flag = flag

    def readSimulPathsFile(self):
        """
        Get the Simulation Config. Paths from the file specified and append them to a list
        """
        with open(self.simulationsPath,'r') as f:
            for line in f:
                self.list_of_SimConfigs.append(line.replace("\n",""))

        f.close()

        # If the flag is used, there should also be a userPaths file.
        if self.flag == '-u':
            with open(os.path.join(os.path.dirname(self.simulationsPath),'userPaths.txt'),'r') as f:
                for line in f:
                    self.list_of_UserConfigs.append(line.replace("\n",""))
            f.close()


    def prepareUserPreRolledFiles(self):
        """
        If the -u flag is used, replicate each user configuration file and append the appripriate PreRolled relevance judgment (qrels) file on
        each replication based on the number of runs (i.e. preRolled1.mark , preRolled2.mark etc)
        """

        runId =1
        for userConfPath in self.list_of_UserConfigs:
            i = 1
            while i <= self.numOfRuns:
                # Read the current User File
                fileData1 = read_file_to_string(userConfPath)

                #Append the number of PreRolled File
                currRun_fileData1 = fileData1.replace('{9}',str(i))
                xmlData1 = xml.dom.minidom.parseString(currRun_fileData1)


                tempFileName = os.path.basename(userConfPath)
                tempFileName = tempFileName.split('-')[0] + '-' + tempFileName.split('-')[1]

                baseDirect = os.path.dirname(userConfPath)

                newFileName = os.path.join(baseDirect,tempFileName+'_ID-'+str(runId) + '.xml')

                #Write the file
                with open(newFileName, "w") as f:
                    f.write(xmlData1.toprettyxml())
                f.close()


                #Append path to list
                self.listOfRefinedUserConfig.append(newFileName)
                i = i + 1
                runId = runId +1


    def prepareConfigFile(self):
        """
        Take a simulation configuration (path) and according to the number of runs needed created the appropriate dirs
        and temporary simulation configuration files and append their full path to a list
        """

        # If flag is used create users with preRolled qrles files
        if self.flag == '-u':
            self.prepareUserPreRolledFiles()

        # Replicate the base simulation configuration files according to the number of runs required.
        for simConfigPath in self.list_of_SimConfigs:

            fileData = read_file_to_string(simConfigPath)
            fileName = simConfigPath.split('/')[-1][:-4]

            #Remove the fileName from the simConfigPath and thats the baseDir
            baseDir = simConfigPath.split(fileName)[0]

            # userConfig counter
            counter = 1

            currRun = 1
            userConfStratPointer = 0
            while (currRun <= self.numOfRuns):

                # Format the baseDir in the current Simulation Configuration File
                currRun_fileData = fileData.replace('{0}','output')
                currRun_fileData = currRun_fileData.replace('{1}',fileName)
                currRun_fileData = currRun_fileData.replace('{2}', str(currRun))


                # If flag is set append appropriate user configurations to each simulation Configuration file
                if self.flag == '-u':

                    entry_list = ""
                    withinUserConfPointer = 0

                    # Append the appropriate number/portion of simulated user configurations (w. PreRolled relevance) to the specific simulation configuration
                    # (i.e. each simulation configurtaion run to include the appropriate user configuration (e.g. simulation_Run1 - > user1 (... prerolled1.mark))
                    while counter <= ((len(self.listOfRefinedUserConfig)/self.numOfRuns) * currRun):
                        user_markup = read_file_to_string('base_files/user_entry.xml')
                        entry_list = "{0}{1}".format(entry_list, user_markup.replace('{0}',self.listOfRefinedUserConfig[userConfStratPointer + withinUserConfPointer]))
                        counter = counter + 1
                        withinUserConfPointer = withinUserConfPointer + self.numOfRuns


                    #Append the appropriate user file paths to the appropriate simulation configuration file
                    currRun_fileData = currRun_fileData.replace('{3}',entry_list)

                userConfStratPointer += 1

                xmlData = xml.dom.minidom.parseString(currRun_fileData)
                newBaseDir = os.path.join(baseDir, 'output/'+fileName+'/'+str(currRun))
                newFileName = fileName + '_Run-' +str(currRun) + '.xml'

                #Create the directory if it does not exist and then the necessary simulation configuration file
                if not os.path.exists(newBaseDir):
                    os.makedirs(newBaseDir)

                with open(baseDir+newFileName, "w") as f:
                    f.write(xmlData.toprettyxml())

                #Append the new conf File to the list of Runs
                self.listOfRuns.append(baseDir+newFileName)
                currRun += 1

    def simRun(self):

        curr_position = None
        simultProcesses = []

        finished_processes = set()
        startTime = dt.datetime.now()

        FNULL = open(os.devnull, 'w')

        fileLogDir = os.path.dirname(self.simulationsPath)
        log1 = open(fileLogDir + '/log.txt', 'a')

        # Set working Dir to simiir dir
        os.chdir(os.path.dirname(self.simiirWorkingPath))

        print 'Number of Simulations to be run: ' + str(len(self.listOfRuns)) + '\n=================================================================='

        while (True):

            # Initialize - Start first run
            # Start as many processes as the user specified
            if curr_position is None:
                curr_position = 0
                while (len(simultProcesses) < self.numOfProcesses):
                    simultProcesses.append(subprocess.Popen(['python', 'run_simiir.py', self.listOfRuns[curr_position]],stdin=FNULL, stdout=FNULL,stderr=log1,))
                    curr_position += 1
                    if (curr_position == len(self.listOfRuns)):
                        break

            # If this is not the first run
            else:
                process_indx = 0
                process_done_indx = []

                # Check all the current processes for their status
                while process_indx < len(simultProcesses):
                   if simultProcesses[process_indx].poll() is None:
                       print 'Process with id: ' + str(simultProcesses[process_indx].pid) + ' still working! Simultaneous processes: ' +str(self.numOfProcesses) + ' Total Simulations: ' + str(len(self.listOfRuns))
                   else:
                       print 'Process with id: ' + str(simultProcesses[process_indx].pid) + ' is Done! Simultaneous processes running: ' +str(self.numOfProcesses) + ' Total Simulations: ' + str(len(self.listOfRuns))
                       finished_processes.add(simultProcesses[process_indx].pid)
                       process_done_indx.append(process_indx)

                   process_indx +=1

                print ('------------------------------------------------------------------')
                print 'Finished Processes: ' + str(list(finished_processes))

                # if all the process are still working
                # sleep for a while
                if len(process_done_indx) == 0:
                    print 'Time elapsed: ' + str((dt.datetime.now() - startTime).seconds)
                    time.sleep(3)
                    print 'Sleep for a while...'
                    continue


                # If the end of the list of runs is reached
                # Wait till all process finish and exit the loop
                if (curr_position == len(self.listOfRuns)):
                    print 'wait until last processes are completed...'
                    for curr_process in simultProcesses:
                        curr_process.communicate()
                        print 'Time elapsed: ' + str((dt.datetime.now() - startTime).seconds)
                        finished_processes.add(curr_process.pid)
                        print 'Process with id:' + str(curr_process.pid) + ' is now Done!'
                    break


                # Otherwise (if a process is finished), create a new one with the appropriate files
                for index in process_done_indx:
                    print 'Starting Next Process...'
                    simultProcesses[index] = subprocess.Popen(['python', 'run_simiir.py', self.listOfRuns[curr_position]],stdin=FNULL, stdout=FNULL,stderr=log1, )
                    curr_position += 1
                    if (curr_position == len(self.listOfRuns)):
                        break

        print ("... Done! Num. of Processess successfully completed: " + str(curr_position) + ' out of ' + str(len(self.listOfRuns)) + ' total processess!')
        print ('==================================================================\nProcessess Successfully Completed ' + str(list(finished_processes)) + '\n==================================================================')
        return 0

def usage(filename):
        """
        Prints the usage to stdout.
        """
        print "Usage: python {0} <simulation_paths_file> <simiir_path> <num_of_runs>(optional) <-u>".format(filename)
        print "Where:"
        print "  <simulation_paths_file>: the text file which contains the paths to the simulation configuration files."
        print "  <simiir_path>: the path to the simiir toolkit. (i.e. home/simiir)"
        print "  <num_of_runs>:(Default: 1) Number that each simulation will run."
        print "  <-u>: This flag is used when user configurations will be appended at a later state (i.e. with PreRolled Qrels)"


def main():
    if len(sys.argv) > 2:

        #Default Number of runs
        numOfRuns = 1

        #Get the number of runs
        if len(sys.argv) > 3:
            numOfRuns = int(sys.argv[3])

        #check if flag is specified as an arg
        if len(sys.argv) > 4:
            if sys.argv[4] == '-u':
                flag = '-u'
            else:
                flag = ''
        else:
            flag =''

        simiirPath = os.path.abspath(sys.argv[2])
        simRunner = SimulatorRun(os.path.abspath(sys.argv[1]), os.path.join(simiirPath,'simiir/'), numOfRuns, flag)

        simRunner.readSimulPathsFile()
        simRunner.prepareConfigFile()

        # Get user input
        user_In = raw_input("Appropriate Files and Folders have been Created.\nMake changes if needed and enter 's' to Run the experiments: ")

        if user_In == 's':
            # Run simulations
            simRunner.simRun()
        sys.exit(0)

    # Invalid number of command-line parameters, print usage.
    usage(sys.argv[0])
    sys.exit(1)

if __name__ == '__main__':
    main()