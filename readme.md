I started this project because i wanted to be able to develop on an application as its running.
So i have created something that does, since it doesnt seem that anyone has done so in python.

This is differant from reload() in a few ways. 

The reload built-in defines a new set of objects within sys.modules that replaces the old ones. It doesnt change any existing instances which are based on the old objects. The old objects will still be in memory until not refrenced anymore.

Where as this loads a copy of the module into another name under sys.modules. A quick compairison is done between the original and new is done. Changed objects are then aystematically swapped out, or modified so they relect the differance found.

In its current state, this could cause bugs in the reloaded module. If you come across something, please report it.

Tested in python 2.7.5, 3.3.2 and pypy. Should work on linux also, i've done some limited tests nothing major though.

I've removed the need for a second process to scan for hardware changes. There is a downside though, now the size of the project can now effect performance.

Current to-do list:

  * Detect removed objects
  * Look into detecting renamed objects
  * Find bugs
  * Add the ability to set the location where files are monitored.
  * Look into writing unittests
  * Documentation
