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

import fnmatch
import time
import os
from multiprocessing import Queue, Process


class FileListener(object):
    ''' Constantly check if a file has changed  '''

    def __init__(self, path):

        self.queue = Queue()
        self.proc = Process(target=self.file_listener, args=(path, self.queue))
        self.proc.start()

    def file_listener(self, path, queue):
        ''' check the filesystem if any times in the current path have changed.
            Must use either multiprocessing or threading
        '''
        running = True
        filesInfo = []
        oldFilesInfo = None

        while running:
            time.sleep(0.05) # To reduce cpu usage

            del oldFilesInfo
            oldFilesInfo = filesInfo
            filesInfo = []

            for root, dirname, filenames in os.walk(path):
                for fileName in fnmatch.filter(filenames, '*.py'):
                    filePath = os.sep.join((root, fileName))
                    filesInfo.append((filePath, os.path.getmtime(filePath)))

            data = tuple(set(filesInfo) - set(oldFilesInfo))

            if data and oldFilesInfo:
                data = tuple(item[0] for item in data)
                queue.put(data)

            else:
                del data

    def check(self):
        ''' Run a check to see if any files have changed.
         '''

        # Check if any file changes have been posted
        try:
            changedFiles = self.queue.get_nowait()
        except:
            changedFiles = None

        return changedFiles
