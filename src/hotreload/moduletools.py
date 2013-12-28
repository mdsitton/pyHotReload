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


def exec_(obj, glob, local=None):
    ''' 2.x/3.x compatibility for exec function '''
    try:
        exec (obj in glob, local)
    except TypeError:
        exec(obj, glob, local)


def create_function(name, module):
    ''' Create a function within a module. Then return it.'''

    code = 'def {}(): pass'.format(name)
    exec_(code, module.__dict__, None)

    function = getattr(module, name)
    return function

def package_name(path):
    ''' Return the name a file is refrenced by in sys.modules '''

    moduleNames = list(sys.modules.keys())
    for item in moduleNames:
        module = sys.modules[item]
        if hasattr(module, '__file__') and module.__file__ == path:
            return item
    return None

class ModuleManager(object):
    ''' Managing directly dealing with import mechanisms relating to modules'''
    def __init__(self, filePath, moduleName, displayName):
        self.moduleName = moduleName
        self.filePath = filePath
        self.displayName = displayName if displayName else moduleName

        # Check if is in sys.modules if its not load it.
        if self.displayName not in list(sys.modules.keys()):
            load_source_file(self.filePath, self.displayName)

        self.instance = sys.modules[self.displayName]