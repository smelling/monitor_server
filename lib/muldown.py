__author__ = 'safetydoor'

import sys
import os
import time
import urllib
from threading import Thread

local_proxies = {'http': 'http://217.169.209.2:6666'}

class AxelPython(Thread, urllib.FancyURLopener):
    '''Multi-thread downloading class.

        run() is a vitural method of Thread.
    '''
    def __init__(self, threadname, url, filename, ranges=0, proxies={}):
        Thread.__init__(self, name=threadname)
        urllib.FancyURLopener.__init__(self, proxies)
        self.name = threadname
        self.url = url
        self.filename = filename
        self.ranges = ranges
        self.downloaded = 0

    def run(self):
        '''vertual function in Thread'''
        try:
            self.downloaded = os.path.getsize( self.filename )
        except OSError:
            #print 'never downloaded'
            self.downloaded = 0

        # rebuild start poind
        self.startpoint = self.ranges[0] + self.downloaded

        # This part is completed
        if self.startpoint >= self.ranges[1]:
            print 'Part %s has been downloaded over.' % self.filename
            return

        self.oneTimeSize = 16384 #16kByte/time
        print 'task %s will download from %d to %d' % (self.name, self.startpoint, self.ranges[1])

        self.addheader("Range", "bytes=%d-%d" % (self.startpoint, self.ranges[1]))

        self.urlhandle = self.open( self.url )

        data = self.urlhandle.read( self.oneTimeSize )
        while data:
            filehandle = open( self.filename, 'ab+' )
            filehandle.write( data )
            filehandle.close()

            self.downloaded += len( data )
            #print "%s" % (self.name)
            #progress = u'\r...'

            data = self.urlhandle.read( self.oneTimeSize )

class MulDown(object):

    def GetUrlFileSize(self,url, proxies={}):
        urlHandler = urllib.urlopen( url, proxies=proxies )
        headers = urlHandler.info().headers
        length = 0
        for header in headers:
            if header.find('Length') != -1:
                length = header.split(':')[-1].strip()
                length = int(length)
        return length

    def SpliteBlocks(self,totalsize, blocknumber):
        blocksize = totalsize/blocknumber
        ranges = []
        for i in range(0, blocknumber-1):
            ranges.append((i*blocksize, i*blocksize +blocksize - 1))
        ranges.append(( blocksize*(blocknumber-1), totalsize -1 ))

        return ranges
    def islive(self,tasks):
        for task in tasks:
            if task.isAlive():
                return True
        return False

    def paxel(self,url, output, blocks=6, proxies=local_proxies):
        ''' paxel
        '''
        size = self.GetUrlFileSize( url, proxies )
        ranges = self.SpliteBlocks( size, blocks )
        name =output
        threadname = [ "thread_%d" % i for i in range(0, blocks) ]
        filename = [ name+"_%d" % i for i in range(0, blocks) ]

        tasks = []
        for i in range(0,blocks):
            task = AxelPython( threadname[i], url, filename[i], ranges[i] )
            task.setDaemon( True )
            task.start()
            tasks.append( task )

        time.sleep(1)
        while self.islive(tasks):
            downloaded = sum( [task.downloaded for task in tasks] )
            process = downloaded/float(size)*100
            show = u'\rFilesize:%d Downloaded:%d Completed:%.2f%%' % (size, downloaded, process)
            sys.stdout.write(show)
            sys.stdout.flush()
            time.sleep(1)

        filehandle = open( output, 'wb+' )
        for i in filename:
            f = open( i, 'rb' )
            filehandle.write( f.read() )
            f.close()
            try:
                os.remove(i)
                pass
            except:
                pass

        filehandle.close()
    def down(self,url,savepath,blocks=4, proxies={}):
        self.paxel( url, savepath, blocks=blocks, proxies=proxies)
        return True

if __name__ == '__main__':
    # pro ={'http': 'http://217.169.209.2:6666'}
    # url = "http://cdn.bitbucket.org/pypa/setuptools/downloads/setuptools-1.4b1.tar.gz"
    # output = 'd:/1.gz'
    # mul = MulDown()
    # mul.paxel( url, output, blocks=4, proxies=pro )
    # print 'xxxxxxxxxxxxxxxxxxx'
    pass