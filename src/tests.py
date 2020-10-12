#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import copy

import skl_shared.shared as sh
from skl_shared.localize import _


class File:
    
    def __init__(self):
        self.filename = ''
        self.file = ''
        self.filew = ''
        self.old_size = 0
        self.new_size = 0
        self.compression = ''


class Compression:
    
    def __init__(self,path,pathw):
        self.ifiles = []
        self.path = path
        self.pathw = pathw
        self.Success = True
    
    def sort(self):
        f = '[CompressMedia] tests.Compression.sort'
        if self.Success:
            timer = sh.Timer(f)
            timer.start()
            rates = [ifile.compression for ifile in self.ifiles]
            rates.sort(reverse=True)
            ifiles = []
            for rate in rates:
                for ifile in self.ifiles:
                    if ifile.compression == rate:
                        ifiles.append(copy.copy(ifile))
                        self.ifiles.remove(ifile)
                        break
            self.ifiles = ifiles
            timer.end()
        else:
            sh.com.cancel(f)
    
    def report(self):
        f = '[CompressMedia] tests.Compression.report'
        if self.Success:
            nos = [i + 1 for i in range(len(self.ifiles))]
            '''
            old_sizes = [sh.com.get_human_size(ifile.old_size) \
                         for ifile in self.ifiles
                        ]
            '''
            new_sizes = [sh.com.get_human_size(ifile.new_size) \
                         for ifile in self.ifiles
                        ]
            compression = ['{}%'.format(ifile.compression) \
                           for ifile in self.ifiles
                          ]
            files = [ifile.file for ifile in self.ifiles]
            filesw = [ifile.filew for ifile in self.ifiles]
            iterable = [nos,files,filesw,new_sizes,compression]
            headers = (_('#'),_('INPUT FILE'),_('OUTPUT FILE')
                      ,_('NEW SIZE'),_('COMPRESSION')
                      )
            mes = sh.FastTable (iterable = iterable
                               ,headers  = headers
                               ).run()
            sh.com.run_fast_debug(f,mes)
        else:
            sh.com.cancel(f)
    
    def run(self):
        self.check()
        self.get_files()
        self.set_compression()
        self.sort()
        self.report()
        
    def check(self):
        f = '[CompressMedia] tests.Compression.check'
        self.idir = sh.Directory(self.path)
        self.idirw = sh.Directory(self.pathw)
        self.Success = self.idir.Success and self.idirw.Success
    
    def set_compression(self):
        f = '[CompressMedia] tests.Compression.set_compression'
        if self.Success:
            for ifile in self.ifiles:
                if ifile.old_size:
                    ifile.compression = ((ifile.old_size - ifile.new_size) * 100) / ifile.old_size
                    ifile.compression = round(ifile.compression)
        else:
            sh.com.cancel(f)
    
    def get_files(self):
        f = '[CompressMedia] tests.Compression.get_files'
        if self.Success:
            files = self.idir.get_subfiles()
            filesw = self.idirw.get_subfiles()
            for file in files:
                ifile = File()
                ifile.file = file
                ifile.filename = sh.Path(file).get_filename()
                ifile.old_size = sh.File(file).get_size()
                self.ifiles.append(ifile)
            for filew in filesw:
                filename = sh.Path(filew).get_filename()
                for ifile in self.ifiles:
                    if ifile.filename == filename:
                        ifile.filew = filew
                        ifile.new_size = sh.File(filew).get_size()
        else:
            sh.com.cancel(f)
        

if __name__ == '__main__':
    path = '/media/WD/MY_PHOTOS/Смартфон'
    pathw = '/home/pete/tmp/Смартфон (конвертировано)'
    Compression(path,pathw).run()
