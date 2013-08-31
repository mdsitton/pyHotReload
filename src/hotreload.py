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
from multiprocessing import Queue, Process

from fileutil import file_listener, get_filename, get_path
from moduletools import ModuleManager, diff


def bind_method(previous, new, method):
    ''' Takes a method from one class and binds it to another '''

    boundMethod = getattr(previous, method).__get__(new, previous)
    setattr(new, method, boundMethod)


class HotReload(object):
    ''' Facilitates detecting and reloading of any python module located within
        the folder structure of the first launched script.
    '''
    def __init__(self):
        
        filePath = get_path()
        self.queue = Queue()

        self.proc = Process(target=file_listener, args=(filePath, self.queue))
        self.proc.start()

    def reload_module(self, filePath):
        ''' Reload a python module '''

        # Load main module
        name = get_filename(filePath)
        module = ModuleManager(filePath, name, name)
        moduleVars = vars(module.instance)

        # Load updated module
        nameTemp = name + '2'
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

                    if not hasattr(classTempAttribObject, '__call__'):
                        print ('found {}'.format(classTempAttib))
                    else:
                        print ('found {} :D'.format(classTempAttib))

                    if moduleTempAttrib == 'ModuleManager':
                        print (classAttribObject)
            else: # Its a global variable
                pass # Not Implemented

        # unload temp module
        del moduleTempVars
        del moduleTemp
        del sys.modules[nameTemp]

    def run(self):
        ''' Run a check to see if any files have changed.
            Required to be ran in the beginning of the main loop.
         '''

        # Check if any file changes have been posted
        try:
            changedFiles = self.queue.get_nowait()
        except:
            changedFiles = None

        # if they have 
        if changedFiles:
            for filePath in changedFiles:
                self.reload_module(filePath)
