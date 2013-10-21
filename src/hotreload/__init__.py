# Copyright (c) 2013, Matthew Sitton. 
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met: 

# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer. 
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution. 

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import sys

from hotreload.filelistener import FileListener
from hotreload.fileutil import get_filename, get_path
from hotreload.moduletools import ModuleManager, create_function


def reload_module(filePath):
    ''' Reload a python module without replacing it '''

    newModuleVar = False
    newClassVar = False

    exemptList = ('__name__', '__builtins__', '__file__', '__package__')

    # Load main module
    name = get_filename(filePath)
    module = ModuleManager(filePath, name, name)
    moduleInstance = module.instance
    moduleVars = vars(moduleInstance)

    tempName = name + '2'
    moduleTemp = ModuleManager(filePath, name, tempName)
    moduleTempVars = vars(moduleTemp.instance)

    for moduleTempAttrName in list(moduleTempVars.keys()):  # Module Level

        # New Module-Level object
        if moduleTempAttrName not in moduleVars.keys():
            setattr(moduleInstance, moduleTempAttrName, None)
            newModuleVar = True

        moduleAttrObj = moduleVars[moduleTempAttrName]
        moduleTempAttrObj = moduleTempVars[moduleTempAttrName]

        # Class Object Found
        if isinstance(moduleTempAttrObj, type):

            # If the class is new create it
            if newModuleVar:
                baseClasses = moduleTempAttrObj.__bases__
                newClass = type(moduleTempAttrName, baseClasses, {})
                setattr(moduleInstance, moduleTempAttrName, newClass)

                moduleVars = vars(moduleInstance)
                moduleAttrObj = moduleVars[moduleTempAttrName]

            classVars = vars(moduleAttrObj)
            classTempVars = vars(moduleTempAttrObj)

            # Objects within Class
            for classTempAttrName in list(classTempVars.keys()):

                # if the class Attribute is new set a temp value for it
                if classTempAttrName not in classVars.keys():
                    setattr(moduleAttrObj, classTempAttrName, None)
                    newClassVar = True

                classAttrObj = classVars[classTempAttrName]
                classTemp = classTempVars[classTempAttrName]

                hasCode = hasattr(classTemp, '__code__')

                # New method, create it
                if newClassVar and hasCode:
                    method = create_function(classTempAttrName, moduleInstance)
                    method.__code__ = classTemp.__code__

                    setattr(moduleAttrObj, classTempAttrName, method)
                    delattr(moduleInstance, classTempAttrName)

                # Update current method
                elif hasCode:
                    classAttrObj.__code__ = classTemp.__code__

                # New Class variable, define it properly
                elif newClassVar:
                    setattr(moduleAttrObj, classTempAttrName, classTemp)

        # Global Variable, Function, or Import(Module) Object found
        else: 

            # Verify that the variable isnt a builtin attribute
            # TODO: Finish adding more builtin attributes or make it detect them
            if moduleTempAttrName not in exemptList:

                hasCode = hasattr(moduleTempAttrObj, '__code__')

                # New function, create it.
                if newModuleVar and hasCode:
                    function = create_function(moduleTempAttrName, moduleInstance)
                    function.__code__ = moduleTempAttrObj.__code__

                # Update current function.
                elif hasCode:
                    moduleAttrObj.__code__ = moduleTempAttrObj.__code__

                # New global variable, define it properly
                elif newModuleVar:
                    setattr(moduleInstance, moduleTempAttrName, moduleTempAttrObj)

    # unload temp module
    del sys.modules[tempName]

class HotReload(object):
    ''' Facilitates detecting and reloading of any python module located within
        the folder structure of the first launched script.
    '''

    def __init__(self):
        self.fileListener = FileListener(get_path())

    def run(self):
        ''' Check with FileListener if any files have been modified.
            Required to be ran in the beginning of the main loop.
         '''

        for filePath in self.fileListener.check():
            reload_module(filePath)
    def stop(self):
        self.fileListener.stop()