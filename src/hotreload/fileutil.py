# Copyright (c) 2013-2014, Matthew Sitton. 
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
import time
import multiprocessing
try:  # Python 3
    from importlib.machinery import SourceFileLoader
    from queue import Empty
except ImportError:  # Python 2
    from imp import load_source
    from Queue import Empty

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

def checker(path, queue, qin):
    running = True
    oldFilesInfo = None
    filesInfo = []

    while running:
        try:
            time.sleep(0.05)
            
            del oldFilesInfo
            oldFilesInfo = filesInfo
            filesInfo = []
            
            for item in path:
                for root, dirName, filenames in os.walk(item):
                    for fileName in filenames:
                        if fileName[-3:] == '.py':
                            filePath = os.sep.join((root, fileName))
                            filesInfo.append((filePath, os.path.getmtime(filePath)))

            changedFiles = tuple(item[0] for item in set(filesInfo) - set(oldFilesInfo))
            if changedFiles and oldFilesInfo:
                queue.put(changedFiles)
            
            try:
                running = qin.get_nowait()
            except Empty:
                running = True
        except KeyboardInterrupt:
            pass

class FileChecker(object):
    ''' Track when an if a file has changed '''

    def __init__(self, path):
        self.path = path

        if not self.path:
            self.path = (get_path(),)

        self.queue = multiprocessing.Queue()
        self.queueBack = multiprocessing.Queue()
        self.thread = multiprocessing.Process(target=checker, args=(self.path, self.queue, self.queueBack))
        self.thread.start()

    def check(self):
        ''' Run a check to see if any files have changed.
         '''
        try:
            changedFiles = self.queue.get_nowait()
        except:
            changedFiles = ()

        return changedFiles

    def stop(self):
        self.queueBack.put(False)