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

try:  # Python 3
    from importlib.machinery import SourceFileLoader
except ImportError:  # Python 2
    from imp import load_source


def load_source_file(pathName, name):
    ''' Load source file from the specified file
        Returns module, and puts it as specified alias in sys.module.
    '''
    # In python 3 parts of imp needed are deprecated, we use importlib instead.
    try: # Python 3
        SourceFileLoader(name, pathName).load_module(name)
    except NameError: # Python 2
        load_source(name, pathName)

    return sys.modules[name]


def package_name(path):
    ''' Return the name a file is refrenced by in sys.modules '''

    moduleNames = list(sys.modules.keys())
    for item in moduleNames:
        module = sys.modules[item]
        if hasattr(module, '__file__') and (module.__file__ == path or module.__file__ == (path + 'c')):
            return item
    return None


def calculate_intermed(module):
    ''' Return dict of user-define vars and objects in module.'''
    irDict = {}
    if isinstance(module, types.ModuleType):
        modVars = vars(module)
    elif isinstance(module, dict):
        modVars = module

    for var in modVars:
        # Skip builtins
        if isinstance(self.moduleAttrObj, types.BuiltinFunctionType):
            continue

        try:
            oldStyleClass = isinstance(self.moduleTempAttrObj, types.ClassType)
        except AttributeError:
            oldStyleClass = False

        hasCode = hasattr(self.moduleTempAttrObj, '__code__')

        # Classes
        if isinstance(modVars[var], type) or oldStyleClass:
            irClassDict = {}
            cls = modVars[var]
            for clsVar in cls:
                # Skip readonly attributes and built-ins
                if (clsVar == '__dict__' or clsVar == '__doc__' or
                        isinstance(cls[clsVar], types.BuiltinFunctionType) or
                        isinstance(cls[clsVar], types.GetSetDescriptorType)):
                    continue

                irClassDict[clsVar] = cls[clsVar]

            irDict[var] = irClassDict

        # Global Variables, Functions, Imported Modules
        else:
            irDict[var] = modVars[var]


class ModuleManager(object):
    ''' Manage import mechanisms relating to modules '''
    def __init__(self, filePath, moduleName, displayName):
        self.moduleName = moduleName
        self.filePath = filePath
        self.displayName = displayName if displayName else moduleName

        # Check if is in sys.modules if its not load it.
        if self.displayName not in list(sys.modules.keys()):
            load_source_file(self.filePath, self.displayName)

        self.instance = sys.modules[self.displayName]

    def delete(self):
        del self.instance
        del sys.modules[self.displayName]


class DiffDict(object):
    def __init__(self, current, past):
        self.current = current
        self.past = past

        self.currentKeySet = set(self.current.keys()) 
        self.pastKeySet = set(self.past.keys())

        # Returns a set with values common to both
        # used for calculating added, and removed keys
        self.common = self.currentKeySet & pastKeySet

    def added(self):
        return tuple(self.currentKeySet - self.common)

    def removed(self):
        return tuple(self.pastKeySet - self.common)
