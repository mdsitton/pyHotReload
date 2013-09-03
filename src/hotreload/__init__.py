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
import types

from hotreload.filelistener import FileListener
from hotreload.fileutil import get_filename, get_path
from hotreload.moduletools import ModuleManager, bind_method


class HotReload(object):
    ''' Facilitates detecting and reloading of any python module located within
        the folder structure of the first launched script.
    '''

    def __init__(self):

        filePath = get_path()
        self.fileListener = FileListener(filePath)

    def reload_module(self, filePath):
        ''' Reload a python module '''

        # Load main module
        name = get_filename(filePath)
        module = ModuleManager(filePath, name, name)
        moduleInstance = module.instance
        moduleVars = vars(moduleInstance)


        # The following if statement is a hack to allow global variables to work.
        # It keeps the temp module around until the next reload,
        # because the original module now has small references to it.
        # Deleting the module from sys.modules causes global variables to become None
        # Inside methods swapped from the temp module, which is all of them.
        # Load updated module
        nameTemp = name + '2'
        if nameTemp in sys.modules.keys():
            del sys.modules[nameTemp]
        moduleTemp = ModuleManager(filePath, name, nameTemp)
        moduleTempVars = vars(moduleTemp.instance)

        for moduleTempAttrib in list(moduleTempVars.keys()):  # Module Level

            moduleAttribObject = moduleVars[moduleTempAttrib]
            moduleTempAttribObject = moduleTempVars[moduleTempAttrib]

            # Is it a class?
            if isinstance(moduleTempAttribObject, type):

                classVars = vars(moduleAttribObject)
                classTempVars = vars(moduleTempAttribObject)

                for classTempAttib in list(classTempVars.keys()): # Class Level

                    classAttribObject = classVars[classTempAttib]
                    classTempAttribObject = classTempVars[classTempAttib]
                     
                    if hasattr(classTempAttribObject, '__call__'):
                        bind_method(moduleTempAttribObject, moduleAttribObject, classTempAttib)
                    
            else: # Its a global variable or function

                # Skip imported module
                if isinstance(moduleTempAttribObject, types.ModuleType):
                    continue

                # Verify that the variable isnt a builtin attribute
                valuesNotChange = ('__name__', '__builtins__', '__file__', '__package__')

                if moduleTempAttrib not in valuesNotChange:
                    setattr(moduleInstance, moduleTempAttrib, moduleTempAttribObject)

        # unload temp module container class keep the module in sys.modules
        del moduleTempVars
        del moduleTemp

    def run(self):
        ''' Check with FileListener if any files have been modified.
            Required to be ran in the beginning of the main loop.
         '''
         
        changedFiles = self.fileListener.check()

        # if they have 
        if changedFiles:
            for filePath in changedFiles:
                self.reload_module(filePath)
