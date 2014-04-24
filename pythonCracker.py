#!/usr/bin/python
import sys
import os
import crypt
from threading import Thread
import threading
import math
#import thread
import optparse

#overrinfing thread so i can use it the way i want
class myThread (threading.Thread):
    def __init__(self, threadID, name, lines,salt,cryptPass):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
	self.lines=lines
	self.salt=salt
	self.cryptPass=cryptPass
	
    def run(self):#when the thread starts begin cracking
        cracker(self.lines,self.salt,self.cryptPass,self.threadID)

#global variable to stop all the threads when the password is found
__passwordFound__=False
__password__=""

#the shadow file is of format name:$hashtype$salt
def testPass(zfile,cryptPass):
    test=cryptPass.split("$")
    salt="$"+test[1]+"$"+test[2]#detecting salt
    dictFile= open(zfile,'r')

    lines=dictFile.readlines()
    numberOflines=len(lines)

    #get the number of threads on the computer
    number_of_threads=_getThreads()
    threads=[] #to store the threads
    
    
    start=0
    end=(int)(math.floor(numberOflines/number_of_threads))#split the dictionary according to the number of cores
    for i in range(number_of_threads):
	threads.append(myThread(i,"thread"+str(i),lines[start:end],salt,cryptPass))#initialize each thread with his porchin of dictionary to crack it
	start+=(int)(math.floor(numberOflines/number_of_threads))#used to give the next thread his portion of the dictionary
	end+=start

    for _thread in threads:
	_thread.start()#start all the threads
	
    cracker(lines[end:],salt,cryptPass,"thread0")#there will be some few words to test in the dictionary test them 

 

def main():
    parser=optparse.OptionParser("usage: -f <shadow file> -d <dictionary>")
    parser.add_option("-f",dest="zname",type="string",help="specify the file file containing the hash")
    parser.add_option("-d",dest="dname",type="string",help="specify a dictionary")
    (options,args)=parser.parse_args();
    if(options.zname==None)|(options.dname==None):
        print parser.usage
        exit(0)
    else:
        zname=options.zname
        dname=options.dname

    passFile=open(zname)#open the shadow file
    for line in passFile.readlines():
        if ":" in line:
            user=line.split(":")[0]#the first column is the username
            cryptPass=line.split(":")[1].strip(" ")#hash + salt is here
            print "[*] cracking password for "+user
            testPass(dname,cryptPass)
 

def cracker(lines,salt,cryptPass,thread_name):
    for word in lines:
	    global __passwordFound__
	    global __password__
	    if(not __passwordFound__):
		    word=word.strip("\n")
		    cryptWord=crypt.crypt(word,salt)#encrypt the password in the dictionary
		    if (cryptWord==cryptPass):#compare the hashes if they are the same then we found our password
			print "[+] Password found: "+word+" using Thread "+str(thread_name)+" \n"
			__passwordFound__=True
			__password__= word
			exit(0)
		    else:
			print "[-] tried password "+word +" with no success using Thread "+ str(thread_name) +"\n"#hashes do not match 

def _getThreads():
    """ Returns the number of available threads on a posix/win based system """
    if sys.platform == 'win32':
        return (int)(os.environ['NUMBER_OF_PROCESSORS'])
    else:
        return (int)(os.popen('grep -c cores /proc/cpuinfo').read())

main()
