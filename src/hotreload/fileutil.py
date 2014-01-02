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

import os
import sys
try:  # Python 3
    from importlib.machinery import SourceFileLoader
except ImportError:  # Python 2
    from imp import load_source

# These are functions to help with file related tasks

def get_path():
    ''' get the current path '''

    fullPath = os.path.realpath(sys.path[0])

    if 'py' in fullPath.split('.'):
        fullPath = os.sep.join(fullPath.split(os.sep)[-1])

    return fullPath


def get_filename(filePath):
    ''' Return a file from a path without the extension '''
    return os.path.basename(filePath).split('.')[0]


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


class FileChecker(object):
    ''' Track when an if a file has changed '''

    def __init__(self, path):
        self.path = path

        self.oldFilesInfo = None
        self.filesInfo = []

        # Run check once to populate initial values
        self.check()

    def check(self):
        ''' Run a check to see if any files have changed.
         '''

        del self.oldFilesInfo
        self.oldFilesInfo = self.filesInfo
        self.filesInfo = []

        for root, dirname, filenames in os.walk(self.path):
            filenames = [item for item in filenames if item[-3:] == '.py']
            for fileName in filenames:
                filePath = os.sep.join((root, fileName))
                self.filesInfo.append((filePath, os.path.getmtime(filePath)))

        changedFiles = tuple(item[0] for item in set(self.filesInfo) - set(self.oldFilesInfo))
        return changedFiles