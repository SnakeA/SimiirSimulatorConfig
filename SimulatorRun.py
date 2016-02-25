__author__ = 'angelos'
import subprocess
import os
import sys
import time
import xml.dom.minidom
from utilities import read_file_to_string
import datetime as dt



# def read_file_to_string(filename):
#     """
#     Given a filename, opens the file and returns the contents as a string.
#     """
#     with open (filename, "r") as myfile:
#         data=myfile.read().replace('\n', '')
#
#     return data

class SimulatorRun():


    def __init__(self, simulationsPath, simiirWorkingPath, numOfRuns):
        self.simulationsPath = simulationsPath
        self.simiirWorkingPath = simiirWorkingPath
        self.numOfRuns = numOfRuns
        self.numOfProcesses = 4
        self.list_of_SimConfigs = []
        self.listOfRuns = []

    def readSimulPathsFile(self):
        """
        Get the Simulation Config. Paths from the file specified and append them to a list
        """
        with open(self.simulationsPath,'r') as f:
            for line in f:
                self.list_of_SimConfigs.append(line.replace("\n",""))

        f.close()

    def prepareConfigFile(self):
        """
        Take a simulation configuration (path) and according to the number of runs needed created the appropriate dirs
        and temporary simulation configuration files and append their full path to a list
        """
        for simConfigPath in self.list_of_SimConfigs:

            fileData = read_file_to_string(simConfigPath)
            fileName = simConfigPath.split('/')[-1][:-4]

            #Remove the fileName from the simConfigPath and thats the baseDir
            baseDir = simConfigPath.split(fileName)[0]

            currRun = 1

            while (currRun <= self.numOfRuns):

                # Format the baseDir in the current Simulation Configuration File
                currRun_fileData = fileData.replace('{0}','output')
                currRun_fileData = currRun_fileData.replace('{1}',fileName)
                currRun_fileData = currRun_fileData.replace('{2}', str(currRun))


                xmlData = xml.dom.minidom.parseString(currRun_fileData)
                newBaseDir = os.path.join(baseDir, 'output/'+fileName+'/'+str(currRun))
                newFileName = fileName + '_Run-' +str(currRun) + '.xml'

                #Create the directory if it does not exist
                if not os.path.exists(newBaseDir):
                    os.makedirs(newBaseDir)

                with open(baseDir+newFileName, "w") as f:
                    f.write(xmlData.toprettyxml())
                self.listOfRuns.append(baseDir+newFileName)
                currRun += 1

    def simRun(self):

        curr_position = None
        simultProcesses = []

        finished_processes = []
        n1=dt.datetime.now()

        FNULL = open(os.devnull, 'w')



        fileLogDir = os.path.dirname(self.simulationsPath)
        log1 = open(fileLogDir + '/log.txt', 'a')

        # Set working Dir to simiir dir
        os.chdir(os.path.dirname(sys.argv[2]))

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
                       finished_processes.append(simultProcesses[process_indx].pid)
                       process_done_indx.append(process_indx)

                   process_indx +=1

                print ('------------------------------------------------------------------')
                print 'Finished Processes: ' + str(finished_processes)

                # if all the process are still working
                # sleep for a while
                if len(process_done_indx) == 0:
                    print 'Time elapsed: ' + str((dt.datetime.now() - n1).seconds)
                    time.sleep(3)
                    print 'Sleep for a while...'
                    continue


                # If the end of the list of runs is reached
                # Wait till all process finish and exit the loop
                if (curr_position == len(self.listOfRuns)):
                    print 'wait until processes are finished...'
                    for curr_process in simultProcesses:
                        curr_process.communicate()
                        finished_processes.append(curr_process.pid)
                        print 'Process with id:' + str(curr_process.pid) + ' is now Done!'
                    break


                # Otherwise (if a process is finished), create a new one with the appropriate files
                for index in process_done_indx:
                    print 'Starting Next Process...'
                    simultProcesses[index] = subprocess.Popen(['python', 'run_simiir.py', self.listOfRuns[curr_position]],stdin=FNULL, stdout=FNULL,stderr=log1, )
                    curr_position += 1
                    if (curr_position == len(self.listOfRuns)):
                        break

        print ("... Done! Num. of Simulations run: " + str(curr_position) + ' out of ' + str(len(self.listOfRuns)) + ' total simulations!')
        print ('==================================================================\nSimulations Run Successfully ' + str(finished_processes) + '\n==================================================================')


def usage(filename):
        """
        Prints the usage to stdout.
        """
        print "Usage: python {0} <simulation_paths_file> <simiir_workingDir> <num_of_runs>".format(filename)
        print "Where:"
        print "  <simulation_paths_file>: the text file which contains the paths to the simulation configuration files."
        print "  <simiir_workingDir>: the path to the simiir toolkit to be set as the current working directory (where the run_python.py exists)."
        print "  <num_of_runs>:(Default: 1) Number that each simulation will run."


def main():
    if len(sys.argv) > 2 and len(sys.argv) < 5:

        #Default Number of runs
        numOfRuns = 1

        if len(sys.argv) > 3:
            numOfRuns = int(sys.argv[3])

        simRunner = SimulatorRun(sys.argv[1], sys.argv[2], numOfRuns)

        simRunner.readSimulPathsFile()
        simRunner.prepareConfigFile()


        # Run simulations
        simRunner.simRun()

        sys.exit(0)

    # Invalid number of command-line parameters, print usage.
    usage(sys.argv[0])
    sys.exit(1)

if __name__ == '__main__':
    main()