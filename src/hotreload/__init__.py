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

from hotreload.fileutil import get_filename, FileChecker
from hotreload.codetools import ModuleManager, package_name

def exec_(obj, glob, local=None):
    ''' 2.x/3.x compatibility for exec function '''
    try:
        exec (obj in glob, local)
    except TypeError:
        exec(obj, glob, local)

class BaseReload(object):
    ''' Base reload infrastructure for loading modules, and reloading them. '''
    
    def default_vars(self):
        '''
            Reset class variables so that we dont have any potential issues with
            previous reload cycles interfearing with the next reload
        '''
        self.newModuleVar = None

        self.filePath = None
        self.name = None
        self.module = None
        self.moduleInstance = None
        self.moduleVars = None

        self.tempName = None
        self.moduleTemp = None
        self.moduleTempVars = None

        self.moduleTempAttrName = None
        self.moduleAttrObj = None
        self.moduleTempAttrObj = None

    def init_module(self, filePath):
        ''' Initialise module and temp module from filePath, and setup class for this reload cycle '''

        # Some basic error checking on import
        try:
            self.newModuleVar = False

            self.filePath = filePath
            self.name = package_name(filePath)
            self.module = ModuleManager(filePath, self.name, self.name)
            self.moduleInstance = self.module.instance
            self.moduleVars = vars(self.moduleInstance)

            self.tempName = self.name + '2'
            self.moduleTemp = ModuleManager(self.filePath, self.name, self.tempName)
            self.moduleTempVars = vars(self.moduleTemp.instance)

            return True
        
        except Exception as e:
            print (e)
            return False

    def create_function(self, name):
        ''' Create a function within a module. Then return it. '''
        code = 'def {}(): pass'.format(name)
        exec_(code, self.moduleInstance.__dict__, None)

        function = self.getmoduleattr(name)
        return function

    def new_function(self, name, refObject):
        ''' Swap code objects with provided refrence '''

        function = self.create_function(name)
        function.__code__ = refObject.__code__

    def new_method(self, name, refObject, parent):
        ''' Put a method into a different class by swaping code objects '''

        method = self.create_function(name)
        method.__code__ = refObject.__code__

        setattr(parent, name, method)
        self.delmoduleattr(name)

    def new_class(self, name, refObject):
        ''' Create a new class based on another class '''

        baseClasses = refObject.__bases__
        newClass = type(name, baseClasses, {})

        self.setmoduleattr(name, newClass)
        self.update_module_vars()

    def update_module_vars(self):
        ''' 
            Update some variables which are based on a module.
            This need to be done occasionally when something updates a module.
        '''
        self.moduleVars = vars(self.moduleInstance)
        self.moduleAttrObj = self.moduleVars[self.moduleTempAttrName]

    def process_class(self, orgClass, refClass):
        ''' Process and reload a class '''

        newClassVar = False

        classVars = vars(orgClass)
        classTempVars = vars(refClass)

        for classTempAttrName in list(classTempVars.keys()):

            if classTempAttrName == '__dict__' or classTempAttrName == '__doc__':
                continue

            # if the class Attribute is new set a temp value for it
            if classTempAttrName not in classVars.keys():

                setattr(orgClass, classTempAttrName, None)
                newClassVar = True

            classAttrObj = classVars[classTempAttrName]
            classTemp = classTempVars[classTempAttrName]

            hasCode = hasattr(classTemp, '__code__')

            # Verify that the variable isnt a builtin attribute
            if not (isinstance(classAttrObj, types.BuiltinFunctionType) or
                    isinstance(classAttrObj, types.GetSetDescriptorType) ):
                # New method, create it
                if newClassVar and hasCode:
                    self.new_method(classTempAttrName, classTemp, orgClass)

                # Update current method
                elif hasCode:
                    classAttrObj.__code__ = classTemp.__code__

                # New Class variable, define it properly
                elif newClassVar:
                    setattr(orgClass, classTempAttrName, classTemp)
    
    def getmoduleattr(self, name):
        return getattr(self.moduleInstance, name)

    def setmoduleattr(self, name, value):
        setattr(self.moduleInstance, name, value)
    
    def delmoduleattr(self, name):
        delattr(self.moduleInstance, name)
        
    def reload(self):
        ''' Reload a python module without replacing it '''

        for self.moduleTempAttrName in list(self.moduleTempVars.keys()):  # Module Level

            # New Module-Level, create placeholder
            if self.moduleTempAttrName not in self.moduleVars.keys():
                self.setmoduleattr(self.moduleTempAttrName, None)
                self.newModuleVar = True

            self.moduleAttrObj = self.moduleVars[self.moduleTempAttrName]
            self.moduleTempAttrObj = self.moduleTempVars[self.moduleTempAttrName]

            # Check for old style classes on python 2.7 will crash on 3
            try:
                oldStyleClass = isinstance(self.moduleTempAttrObj, types.ClassType)
            except AttributeError:
                oldStyleClass = False

            # Class Object Found
            if isinstance(self.moduleTempAttrObj, type) or oldStyleClass:

                # If its a new class create it.
                if self.newModuleVar:
                    self.new_class(self.moduleTempAttrName, self.moduleTempAttrObj)

                self.process_class(self.moduleAttrObj, self.moduleTempAttrObj)

            # Global Variable, Function, or Import(Module) Object found
            else: 

                # Verify that the variable isnt a builtin attribute
                if not isinstance(self.moduleAttrObj, types.BuiltinFunctionType):

                    hasCode = hasattr(self.moduleTempAttrObj, '__code__')

                    # New function, create it.
                    if self.newModuleVar and hasCode:
                        self.new_function(self.moduleTempAttrName, self.moduleTempAttrObj)

                    # Update current function.
                    elif hasCode:
                        self.moduleAttrObj.__code__ = self.moduleTempAttrObj.__code__

                    # New global variable, define it properly
                    elif self.newModuleVar:
                        self.setmoduleattr(self.moduleTempAttrName, self.moduleTempAttrObj)

        # unload temp module
        self.moduleTemp.delete()
        self.default_vars()

class HotReload(BaseReload):
    ''' 
        Standard class for monitoring the file system and triggering 
        reloads when things are changed
    '''
    def __init__(self, checkPaths=tuple()):
        self.fileListener = FileChecker(checkPaths)
        self.files = None

    def run(self):
        '''
            Check with FileListener if any files have been modified.
            Required to be ran in the beginning of the main loop.
         '''
        self.files = self.fileListener.check()

        for filePath in self.files:
            if self.init_module(filePath):
                self.reload()

    def stop(self):
        ''' Stop the file listener '''
        self.fileListener.stop()