I started this out of the want to be able to develop a program without having to restart it.

I messed with the reload function a bit and wasnt happy that it didnt automatically update the old instances.
So i have created something that does, its no more than a proof of concept for the moment but it will get there.

I have quite a lot more to finish on this. So far it only replaces the methods of a class, no variables or anything.

Current to-do list:
	Try and detect imported modules and functions from those modules excluding them from reload.
	Detect if a source file is within a package and do the right thing when changing it in sys.modules.
	Do variable replacement
	Try to not always replace everything, be selective about it.
	Add support for global variables, functions, and class variables
	Re-structure the file change detection code into a class.
	Ill think of more later :P
