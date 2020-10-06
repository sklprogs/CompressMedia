#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import os
import re
import ffmpy
from PIL import Image

import skl_shared.shared as sh
from skl_shared.localize import _

QUALITY = 65
#PATH = '/media/WD/MY_PHOTOS/Смартфон'
PATH = '/home/pete/tmp/TestSmartphone'

ICON = sh.objs.get_pdir().add ('..','resources'
                              ,'DownsizeSmartphone.gif'
                              )


class Objects:
    
    def __init__(self):
        self.progress = None
    
    def get_progress(self):
        if self.progress is None:
            self.progress = sh.ProgressBar (title = _('Conversion progress')
                                           ,icon  = ICON
                                           )
            self.progress.add()
        return self.progress



class Compress:
    
    def __init__(self,Debug=False):
        self.Debug = Debug
        self.files = []
        self.folders = []
        self.nomatch = []
        self.path = PATH
        self.relfiles = []
        self.renamed = []
        self.Success = True
    
    def convert_videos(self):
        f = '[CompressMedia] compress.Compress.convert_videos'
        if self.Success:
            videos = [file for file in self.relfiles \
                      if file.startswith('VID')
                     ]
            tcount = len(videos)
            scount = 0
            objs.get_progress().show()
            for i in range(len(self.renamed)):
                if self.relfiles[i].startswith('VID'):
                    mes = _('Process "{}" ({}/{})')
                    mes = mes.format (self.relfiles[i]
                                     ,scount + 1
                                     ,tcount
                                     )
                    sh.objs.get_mes(f,mes,True).show_info()
                    objs.progress.set_text(mes)
                    objs.progress.update(scount,tcount)
                    if self._convert_video(self.renamed[i]):
                        scount += 1
            objs.progress.close()
            if scount == tcount:
                mes = _('All videos have been processed successfuly')
                sh.objs.get_mes(f,mes,True).show_info()
            else:
                mes = _('Videos processed successfuly: {}/{}')
                mes = mes.format(scount,tcount)
                sh.objs.get_mes(f,mes,True).show_warning()
        else:
            sh.com.cancel(f)
    
    def convert(self):
        f = '[CompressMedia] compress.Compress.convert'
        if self.Success:
            old_size = self.calculate_size()
            self.convert_photos()
            self.convert_videos()
            new_size = self.calculate_size()
            diff_size = sh.com.get_human_size (bsize     = old_size - new_size
                                              ,LargeOnly = True
                                              )
            mes = _('Freed space: {}').format(diff_size)
            sh.objs.get_mes(f,mes).show_info()
        else:
            sh.com.cancel(f)
    
    def _debug_renamed(self):
        mes = ['"{}"'.format(file) for file in self.renamed]
        return _('Renamed files:') + '\n' + '\n'.join(mes)
    
    def calculate_size(self):
        f = '[CompressMedia] compress.Compress.calculate_size'
        size = 0
        if self.Success:
            for file in self.renamed:
                size += sh.File(file).get_size()
        else:
            sh.com.cancel(f)
        return size
    
    def _convert_video(self,filew):
        try:
            ffmpy.FFmpeg (inputs  = {file:None}
                         ,outputs = {filew:None}
                         ).run()
        except Exception as e:
            mes = _('Third-party module has failed!\n\nDetails: {}')
            mes = mes.format(e)
            sh.objs.get_mes(f,mes,True).show_error()
    
    def _convert_photo(self,filew):
        try:
            iimage = Image.open(filew)
            iimage.save(filew,optimize=True,quality=QUALITY)
            iimage.close()
            return True
        except Exception as e:
            mes = _('Third-party module has failed!\n\nDetails: {}')
            mes = mes.format(e)
            sh.objs.get_mes(f,mes,True).show_error()
    
    def convert_photos(self):
        f = '[CompressMedia] compress.Compress.convert_photos'
        if self.Success:
            photos = [file for file in self.relfiles \
                      if file.startswith('IMG')
                     ]
            tcount = len(photos)
            scount = 0
            objs.get_progress().show()
            for i in range(len(self.renamed)):
                if self.relfiles[i].startswith('IMG'):
                    mes = _('Process "{}" ({}/{})')
                    mes = mes.format (self.relfiles[i]
                                     ,scount + 1
                                     ,tcount
                                     )
                    sh.objs.get_mes(f,mes,True).show_info()
                    objs.progress.set_text(mes)
                    objs.progress.update(scount,tcount)
                    if self._convert_photo(self.renamed[i]):
                        scount += 1
            objs.progress.close()
            if scount == tcount:
                mes = _('All photos have been processed successfuly')
                sh.objs.get_mes(f,mes,True).show_info()
            else:
                mes = _('Photos processed successfuly: {}/{}')
                mes = mes.format(scount,tcount)
                sh.objs.get_mes(f,mes,True).show_warning()
        else:
            sh.com.cancel(f)
    
    def rename(self):
        f = '[CompressMedia] compress.Compress.rename'
        if self.Success:
            for i in range(len(self.renamed)):
                if not sh.File(self.files[i],self.renamed[i]).move():
                    self.Success = False
                    break
        else:
            sh.com.cancel(f)
    
    def set_renamed(self):
        f = '[CompressMedia] compress.Compress.set_renamed'
        if self.Success:
            for i in range(len(self.relfiles)):
                renamed = os.path.join(self.folders[i],self.relfiles[i])
                self.renamed.append(renamed)
                if not self.renamed:
                    self.Success = False
                    mes = _('Empty output is not allowed!')
                    sh.objs.get_mes(f,mes,True).show_warning()
        else:
            sh.com.cancel(f)
    
    def create_folders(self):
        f = '[CompressMedia] compress.Compress.create_folders'
        if self.Success:
            folders = sorted(set(self.folders))
            for folder in folders:
                if not sh.Path(folder).create():
                    self.Success = False
                    break
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
        f = '[CompressMedia] compress.Compress.debug'
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
        f = '[CompressMedia] compress.Compress.check'
        self.idir = sh.Directory(self.path)
        self.Success = self.idir.Success
    
    def set_folders(self):
        f = '[CompressMedia] compress.Compress.set_folders'
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
        f = '[CompressMedia] compress.Compress.get_files'
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
        self.create_folders()
        self.set_renamed()
        self.rename()
        self.convert()
        self.debug()


objs = Objects()


if __name__ == '__main__':
    f = '__main__'
    sh.com.start()
    Compress(False).run()
    mes = _('Goodbye!')
    sh.objs.get_mes(f,mes,True).show_debug()
    sh.com.end()
