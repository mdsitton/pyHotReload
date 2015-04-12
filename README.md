pyHotReload allows developers to patch code while running, while still keeping the current state of the program.

hotreload is differant from reload() in a few ways. The reload built-in only overwrites the previous version of a module in sys.modules. It doesnt change any existing instances which are based on the old objects. The old objects will still be in memory until not refrenced anymore.

pyHotReload initializes a copy of the module into another name under sys.modules. The original module, and the new version are compared. Changed objects are then systematically swapped out, or modified so they relect the differance found.

In its current alpha state, there will be bugs causing the reloaded module to diverge from what it should be. If you come across something that doesn't work properly please report it.

Tested with python 2.7.5, 3.3.2 and pypy with Windows, OSX, and Linux.

Current to-do list:
  * Detect removed objects
  * Look into detecting renamed objects
  * Verify __slots__ support.
  * Verify and fix properties.
  * Find bugs
  * Write unittests
  * Better document the project.
