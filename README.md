README

 1. What is pysos?
 2. What is the advantage of pysos over xsos?
 3. How do I install pysos?
 4. How do I use pysos 
 5. When is feature xxx going to be included?



#WHAT IS PYSOS?

Pysos is a Python re-write of xsos, which is a bash utility written by Ryan Sawhill. 
Pysos (and thus xsos) is used to parse sosreports and present related data is a more human-friendly style,
and in the process get to the interesting bits of the data, rather than having to manually sift through loads of log files and similar.


Pysos can also run on a local system, and for most modules this can be done on the fly using the bits under, for example, the /proc filesystem. 
In other locations, a temporary file is generated and then fed to pysos in the same manner as if pysos was running on a sosreport. 
The end result is the same however, in that pertinent data is parse, formatted and presented in a human-friendly style.


Pysos is written for Python2.7. 

#ADVANTAGE OF PYSOS OVER XSOS

There are a number of advantages to having the program written in Python over BASH. 
First and foremost is efficiency and speed. Python will naturally be more efficient than BASH, and also handles file manipulation faster.

For very large sosreports, or for example sosreports run from RHEV hypervisors, BASH could take a long time to parse the large number of vNICs created. 

For example, running against a hypervisor with roughly 100 vNICs, which is not unreasonable for a large RHEV deployment using several networks for each VM, `xsos -in` could take several seconds to parse. By comparison, pysos will generate the same information (and more for some areas) in roughly 0.15 seconds. 

Additionally, as the program matures the hope is to add plug-ins from contributors. 
While most people know how to get around in BASH, more people are more comfortable with coding for Python than BASH scripting. Also, Python is for many people easier to read, debug and in general work with over BASH. 



#INSTALLING PYSOS


Installing pysos is very easy. While in the future pysos will be maintained via RPMs and thus yum, as of right now pysos is a singular file, which can be placed in $PATH. For system wide access, the easiest place to put the pysos file is /bin/pysos. 

Once in /bin, you can use pysos simply via the 'pysos' command - you do NOT have to use 'python' to run it. 


#USING PYSOS

From the output of --help:

>$ pysos --help
usage: pysos [-h] [-a] [-b] [-o] [-k] [-c] [-m] [-d] [-l] [-e] [-g] [-i] [-n]
            [--net] [-s] [-t] [-r] [--db]
             target [target ...]

>positional arguments:
  target         Target directory, aka the sosreport root. Use "/" to run
                 locally


The syntax is straight forward enough: `pysos [args] [target directory]` 

So, if you wanted to print OS and Memory information, you'd use: `pysos -om sosreport-directory`

Or, you could run it on your local system with: `pysos -om /`



#FEATURE REQUESTS


I'm always looking to improve pysos, so if you have a request for a specific feature please let me know on the GitHub page. **Please** remember however that the main goal of pysos is to parse output from a `sosreport` so the feature must be able to work solely on the information gathered from a `sosreport`. 



