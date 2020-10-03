#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import os
import re

import skl_shared.shared as sh
from skl_shared.localize import _


class RenamePhotos:
    
    def __init__(self,Debug=False):
        self.Debug = Debug
        self.files = []
        self.folders = []
        self.nomatch = []
        #self.path = '/media/WD/MY_PHOTOS/Смартфон'
        self.path = '/tmp/TestSmartphone'
        self.relfiles = []
        self.renamed = []
        self.Success = True
    
    def _debug_renamed(self):
        mes = ['"{}"'.format(file) for file in self.renamed]
        return _('Renamed files:') + '\n' + '\n'.join(mes)
    
    def rename(self):
        f = '[DownsizeSmartphone] controller.RenamePhotos.rename'
        if self.Success:
            pass
        else:
            sh.com.cancel(f)
    
    def set_renamed(self):
        f = '[DownsizeSmartphone] controller.RenamePhotos.set_renamed'
        if self.Success:
            for i in range(len(self.relfiles)):
                renamed = os.path.join(self.folders[i],self.relfiles[i])
                self.renamed.append(renamed)
        else:
            sh.com.cancel(f)
    
    def create_folders(self):
        f = '[DownsizeSmartphone] controller.RenamePhotos.create_folders'
        if self.Success:
            folders = sorted(set(self.folders))
            for folder in folders:
                sh.Path(folder).create()
        else:
            sh.com.cancel(f)
    
    def _debug_files(self):
        mes = ['"{}"'.format(file) for file in self.files]
        return _('Files:') + '\n' + '\n'.join(mes)
    
    def _debug_folders(self):
        folders = sorted(set(self.folders))
        mes = ['"{}"'.format(folder) for folder in folders]
        mes = '\n'.join(mes)
        return _('Folders (without duplicates):') + '\n' + mes
    
    def _debug_nomatch(self):
        mes = ['"{}"'.format(nomatch) for nomatch in self.nomatch]
        return _('Non-compliant files:') + '\n' + '\n'.join(mes)
    
    def debug(self):
        f = '[DownsizeSmartphone] controller.RenamePhotos.debug'
        if self.Debug:
            if self.Success:
                mes = [self._debug_files(),self._debug_folders()
                      ,self._debug_nomatch(),self._debug_renamed()
                      ]
                mes = '\n\n'.join(mes)
                sh.com.run_fast_debug(f,mes)
            else:
                sh.com.cancel(f)
        else:
            sh.com.rep_lazy(f)
    
    def check(self):
        f = '[DownsizeSmartphone] controller.RenamePhotos.check'
        self.idir = sh.Directory(self.path)
        self.Success = self.idir.Success
    
    def set_folders(self):
        f = '[DownsizeSmartphone] controller.RenamePhotos.set_folders'
        if self.Success:
            pattern = '(IMG|VID)_(\d\d\d\d)(\d\d)(\d\d)_'
            all_count = len(self.files)
            i = 0
            while i < len(self.relfiles):
                match = re.match(pattern,self.relfiles[i])
                if match:
                    date = '{}-{}-{}'.format (match.group(2)
                                             ,match.group(3)
                                             ,match.group(4)
                                             )
                    self.folders.append(os.path.join(self.path,date))
                else:
                    self.nomatch.append(self.files[i])
                    del self.files[i]
                    del self.relfiles[i]
                    i -= 1
                i += 1
            mes = _('Files to be processed: {}/{}')
            mes = mes.format(len(self.files),all_count)
            sh.objs.get_mes(f,mes,True).show_info()
            if not self.folders:
                self.Success = False
                mes = _('Empty output is not allowed!')
                sh.objs.get_mes(f,mes,True).show_warning()
        else:
            sh.com.cancel(f)
    
    def get_files(self):
        f = '[DownsizeSmartphone] controller.RenamePhotos.get_files'
        if self.Success:
            self.files = self.idir.get_files()
            self.relfiles = self.idir.get_rel_files()
            if not self.files or not self.relfiles:
                self.Success = False
                mes = _('Empty output is not allowed!')
                sh.objs.get_mes(f,mes,True).show_warning()
        else:
            sh.com.cancel(f)
    
    def run(self):
        self.check()
        self.get_files()
        self.set_folders()
        #self.create_folders()
        self.set_renamed()
        self.rename()
        self.debug()


if __name__ == '__main__':
    f = '__main__'
    sh.com.start()
    RenamePhotos(True).run()
    mes = _('Goodbye!')
    sh.objs.get_mes(f,mes,True).show_debug()
    sh.com.end()
