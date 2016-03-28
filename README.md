# SimiirSimulatorConfig
An experimental pipeline for the SimIIR framework, consisting of three python scripts

Requires the SimIIR framework(https://github.com/leifos/simiir) , the ifind libraries(https://github.com/leifos/ifind) and the trec_eval tool http://trec.nist.gov/trec_eval/.
Add SimIIR & ifind to pythonpath, and trec_eval to PATH.
Requirements are included & are the same as those of the SimIIR framework.


## SimulatorConfigurator.py

The first script of the pipeline. Takes an XML file as input (see ###xml Inputs for examples) as well as the path to the base dir of the SimIIR framework and an optional -u flag in case of pre-rolled relevance judgment files
Parses the input XML file and generates the appropriate simulation and user configuration files for the SimIIR framework, as well as a text file with the absolute paths to the sim. configuration files

type python SimulatorConfigurator.py for usage msg!


## SimulatorRun.py

The second script of the pipeline. Takes the text file with the absolute paths to the sim. configuration files. Requires the path to the SimIIr framework, as well as the number of runs for the specified simulations (default=1). Finally the optional -u flag in case of pre-rolled relevance judgment files
Replicates the sim. configurations as well as the user configurations (if pre-rolled relevance judmgents are used) the required number of , generates the appropriate dirs for each run and runs the simulator.

type python SimulatorRun.py for usage msg!

## SimulatorOutputAnalyser.py

The final script. Takes the output file of the simulator, the path to the SimIIR framewrok as well as the path to the output CSV file that it would generate.
Traverses the output dir of the simulator, extracts evaluation measures as well as information about each simulation run and generates a summary CSV file.

type python SimulatorOutputAnalyser.py for usage msg!

## utilities.py

Includes helper methods for the aforementioned scripts

###UnitTests
A Test case is implemented for each one of the components. See HowToRunTests.txt inside the UnitTests dir for instructions how to run the tests.

###base_files
These are the base files used by the SimulatorConfigurator.py script in order to impose the structure of various components

###xml Inputs
These include some example XML base input files for the experimental pipeline.
