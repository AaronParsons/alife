Aaron Parsons, Aug 2005

The point of this project is to allow little scripts (critters) to 
replicate themselves and mutate, hopefully with interesting results.  To keep 
this system stable, a second (static) script handles file and process 
management, and generally imposes rules upon the critters.

Requirements:
--------------------------------------------------------------

Pyvolve is made to run on a bash shell.  Currently, I've only tested the
scripts on Cygwin on Windows 2000 and on Fedora Core Linux, but in principle
any standard Unix/Linux system should work.  You can download Cygwin from 
www.cygwin.org -- I highly recommend it.  Evolution uses programs that come with
most standard UNIX distributions.  These are the programs you need
to have on your computer:

make, bash, python, cut, date, grep, zip/unzip, gzip/gunzip, 
echo, expr, zcat, and gmake

You also need dparser, with the python swig interfaces.  Just download it from
http://staff.washington.edu/sabbey/py_dparser/d-1.13-src.tar.gz
unpack it (tar zxf d-1.13-src.tar.gz), and follow the instructions in the
readme.  Make sure to follow the steps for building the python part.

Additionally, the scripts in ./scripts and the file 2.py need to point to the
correct location of python and bash.  You can do this automatically by
typing:
$ make conf

This should be enough to get you going.

Basic Usage:
--------------------------------------------------------------

$ make conf         configures life for your unix-like system

$ make life         starts the life program

$ make halt         brings life down gracefully.  Next time you run life, it
                    will continue where you left off.  Can take a sec, so be
                    patient.

$ make clean        gets rid of extra, remakeable files floating around.

$ make real_clean   throws out all current critters, forcing you to download a
                    new set of critters.

$ make update       syncs your version of pyvolve with the latest release.
                    Does not mess up any critters you are evolving.

$ make post         submits latest release of code to repository.  For my
                    use only.  :)

$ make demograph    groups existing critters by ancestry and gives percentage
                    of population each subgroup represents.

$ make gen_num      prints how many generations have elapsed.

$ make viewlog      shows the last several entries in the system log,
                    describing what's going on.

$ make visuals      prints an abstracted version of the script currently
                    running, highlighting in color ways in which it is 
                    different than the original script.  Red letters represent
                    items in the original which have been deleted, blue
                    letters represent items which have been added, and green
                    letters represent items which have changed in place.
                    The top pictoral is of the running script, and the 
                    bottom pictoral is of the children it produces, compared
                    against the parent (i.e., how the offspring are different
                    than the parent.  If life is running (in the background, or 
                    in another session) the display will refresh as new scripts 
                    run.  Not all mutations produce a difference
                    visible in this visualization system.

$ nohup make life &     useful command for running life in the background, and
                        keeping it active even after you log out of a machine.
                        

Known Bugs:
--------------------------------------------------------------

There are plenty, but I don't have them documented yet.

Good Luck!
