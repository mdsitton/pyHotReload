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
import os

from fileutil import load_source_file, get_path

def bind_method(previous, new, method):
    ''' Takes a method from one class and binds it to another '''
    boundMethod = getattr(previous, method).__get__(new, previous)
    setattr(new, method, boundMethod)

def diff(x, y):
    ''' Return the differance between two tuples '''
    return tuple(set(x) - set(y))

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

    def __sub__(self, other):
        ''' Determine difference between two versions of a module. '''
        return diff(self.get_keys(), other.get_keys())
