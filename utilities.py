import os
import sys
import inspect
import importlib


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