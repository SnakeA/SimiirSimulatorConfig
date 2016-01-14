__author__ = 'angelos'
import subprocess
import os
import sys
import time
import xml.dom.minidom



def read_file_to_string(filename):
    """
    Given a filename, opens the file and returns the contents as a string.
    """
    with open (filename, "r") as myfile:
        data=myfile.read().replace('\n', '')

    return data

def readSimulPathsFile(path):
    """
    Get the Simulation Config. Paths from the file specified and add them to a list
    """

    list_of_SimConfigs =[]

    with open(path,'r') as f:
        for line in f:
            list_of_SimConfigs.append(line.replace("\n",""))

    f.close()
    return list_of_SimConfigs


def prepareConfigFile(simConfigPath, numOfRuns, list_of_runs):
    """
    Take a simulation configuration (path) and according to the number of runs needed created the appropriate dirs
    and temporary simulation configuration files and append their full path to a list
    """
    fileData = read_file_to_string(simConfigPath)
    fileName = simConfigPath.split('/')[-1][:-4]

    #Remove the fileName from the simConfigPath and thats the baseDir
    baseDir = simConfigPath.split(fileName)[0]

    currRun = 1

    while (currRun <= numOfRuns):

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
        list_of_runs.append(baseDir+newFileName)
        currRun += 1


def usage(filename):
    """
    Prints the usage to stdout.
    """
    print "Usage: python {0} <simulation_paths_file> <simiir_workingDir> <num_of_runs>".format(filename)
    print "Where:"
    print "  <simulation_paths_file>: the text file which contains the paths to the simulation configuration files."
    print "  <simiir_workingDir>: the path to the simiir toolkit to be set as the current working directory (where the run_python.py exists)."
    print "  <num_of_runs>:(Default: 1) Number that each simulation will run."



if __name__ == '__main__':
    if len(sys.argv) > 2 and len(sys.argv) < 5:


        #Default Number of runs
        numOfRuns = 1

        if len(sys.argv) > 3:
            numOfRuns = int(sys.argv[3])

        #Contains all the simulation configuration files
        list_of_SimConfigs = readSimulPathsFile(sys.argv[1])

        #Contains the simulation configuration files to be run.
        list_of_runs = []

        currRun = 0
        for simConfigPath in list_of_SimConfigs:
            prepareConfigFile(simConfigPath,numOfRuns,list_of_runs)

        print (list_of_runs)

        #Current position in the list of runs
        curr_position = None
        process = None
        simultProcesses = []

        #Default Processes running simultaneously
        processesAtATime = 4

        # Set working Dir to simiir dir
        os.chdir(os.path.dirname(sys.argv[2]))

        finished_processes = []

        while (True):

            # Initialize - Start first run
            if curr_position is None:
                curr_position = 0
                while (len(simultProcesses) < processesAtATime):
                    simultProcesses.append(subprocess.Popen(['python', 'run_simiir.py', list_of_runs[curr_position]],stdout=subprocess.PIPE, stderr=subprocess.PIPE))
                    curr_position += 1
                    if (curr_position == len(list_of_runs)):
                        break

            else:

                process_indx = 0
                addNewProcess = False
                process_done_indx = []

                while process_indx < len(simultProcesses):
                   if simultProcesses[process_indx].poll() is None:
                       print 'Process' + str(process_indx) + '/' +str(processesAtATime) + ' still working...'
                   else:
                       print 'Process' + str(process_indx) + '/' +str(processesAtATime) + ' Done!'
                       finished_processes.append(simultProcesses[process_indx])
                       addNewProcess = True
                       process_done_indx.append(process_indx)

                   process_indx +=1

                print simultProcesses

                # if all the process are still working
                # sleep for a while
                if len(process_done_indx) == 0:
                    time.sleep(3)
                    print 'Sleep for a while...'
                    continue


                # If the end of the list of runs is reached
                # Wait till all process finish and exit the loop
                if (curr_position == len(list_of_runs)):
                    print 'wait until processes are finished...'
                    for curr_process in simultProcesses:
                        curr_process.communicate()
                        finished_processes.append(curr_process)
                        print 'Process ' + str(curr_process) + ' is now Done!'
                    break


                # Otherwise (if a process is finished), create a new one with the appropriate files
                for index in process_done_indx:
                    print 'Starting Next Process...'
                    simultProcesses[index] = subprocess.Popen(['python', 'run_simiir.py', list_of_runs[curr_position]],stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    curr_position += 1
                    if (curr_position == len(list_of_runs)):
                        break

        print ("... Done! Simulations run: " + str(curr_position))
        print finished_processes
        sys.exit()

    # Invalid number of command-line parameters, print usage.
    usage(sys.argv[0])
    sys.exit(1)