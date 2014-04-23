#!/usr/bin/python
import sys
import os
import crypt
from threading import Thread
import threading
import math
#import thread
import optparse


class myThread (threading.Thread):
    def __init__(self, threadID, name, lines,salt,cryptPass):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
	self.lines=lines
	self.salt=salt
	self.cryptPass=cryptPass
	
    def run(self):
        cracker(self.lines,self.salt,self.cryptPass,self.threadID)

__passwordFound__=False
__password__=""

def testPass(zfile,cryptPass):
    test=cryptPass.split("$")
    salt="$"+test[1]+"$"+test[2]
    dictFile= open(zfile,'r')

    lines=dictFile.readlines()
    numberOflines=len(lines)

    number_of_threads=_getThreads()
    threads=[]
    
    start=0
    end=(int)(math.floor(numberOflines/number_of_threads))
    for i in range(number_of_threads):
	threads.append(myThread(i,"thread"+str(i),lines[start:end],salt,cryptPass))
	start+=(int)(math.floor(numberOflines/number_of_threads))
	end+=start

    for _thread in threads:
	_thread.start()
	
    cracker(lines[end:],salt,cryptPass,"thread0")

 

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

    passFile=open(zname)
    for line in passFile.readlines():
        if ":" in line:
            user=line.split(":")[0]
            cryptPass=line.split(":")[1].strip(" ")
            print "[*] cracking password for "+user
            testPass(dname,cryptPass)
    print("hrllo")

def cracker(lines,salt,cryptPass,thread_name):
    for word in lines:
	    global __passwordFound__
	    global __password__
	    if(not __passwordFound__):
		    word=word.strip("\n")
		    cryptWord=crypt.crypt(word,salt)
		    if (cryptWord==cryptPass):
			print "[+] Password found: "+word+" using Thread "+str(thread_name)+" \n"
			__passwordFound__=True
			__password__= word
			exit(0)
		    else:
			print "[-] tried password "+word +" with no success using Thread "+ str(thread_name) +"\n"

def _getThreads():
    """ Returns the number of available threads on a posix/win based system """
    if sys.platform == 'win32':
        return (int)(os.environ['NUMBER_OF_PROCESSORS'])
    else:
        return (int)(os.popen('grep -c cores /proc/cpuinfo').read())

main()
