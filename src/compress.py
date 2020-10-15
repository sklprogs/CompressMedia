#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import os
import re
import ffmpy
from PIL import Image

import skl_shared.shared as sh
from skl_shared.localize import _


ICON = sh.objs.get_pdir().add('..','resources','CompressMedia.gif')
#PATH = sh.objs.get_home().add('tmp','Смартфон')
#PATHW = sh.objs.home.add('tmp','Смартфон (конвертировано)')
PATH = '/media/WD/MY_PHOTOS/Смартфон'
PATHW = '/media/WD/MY_PHOTOS/Смартфон (конвертировано)'


class File:
    
    def __init__(self):
        self.source = ''
        self.relpath = ''
        self.filename = ''
        self.target = ''
        self.targetdir = ''
        self.date = ''
        self.Image = False
        self.Video = False
        self.Failed = False
        self.Skipped = False



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



class Converter:
    
    def __init__(self,path,pathw,image_quality=65,Optimize=True):
        self.ifiles = []
        self.path = path
        self.pathw = pathw
        self.Success = True
        self.image_quality = image_quality
        self.Optimize = Optimize
    
    def get_ready(self):
        return [ifile for ifile in self.ifiles \
                if not ifile.Skipped and not ifile.Failed
               ]
    
    def report(self):
        f = '[CompressMedia] compress.Converter.report'
        if self.Success:
            mes = []
            skipped = [ifile for ifile in self.ifiles if ifile.Skipped]
            failed = [ifile for ifile in self.ifiles if ifile.Failed]
            sub = _('Files in total: {}').format(len(self.ifiles))
            mes.append(sub)
            sub = _('Skipped files: {}').format(len(skipped))
            mes.append(sub)
            sub = _('Failed files: {}').format(len(failed))
            mes.append(sub)
            old_size, new_size = self.get_size()
            size_diff = old_size - new_size
            # Avoid ZeroDivisionError
            if old_size:
                percent = round((100*size_diff)/old_size)
            else:
                percent = 0
            old_size = sh.com.get_human_size(old_size,True)
            new_size = sh.com.get_human_size(new_size,True)
            size_diff = sh.com.get_human_size(size_diff,True)
            sub = _('Processed data: {}').format(old_size)
            mes.append(sub)
            sub = _('Converted data: {}').format(new_size)
            mes.append(sub)
            sub = _('Compression: {} ({}%)').format(size_diff,percent)
            mes.append(sub)
            delta = sh.com.get_human_time(self.itimer.end())
            sub = _('The operation has taken {}').format(delta)
            mes.append(sub)
            mes = '\n'.join(mes)
            sh.objs.get_mes(f,mes).show_info()
        else:
            sh.com.cancel(f)
    
    def skip_existing(self):
        f = '[CompressMedia] compress.Converter.skip_existing'
        if self.Success:
            for ifile in self.ifiles:
                if os.path.exists(ifile.target):
                    ifile.Skipped = True
        else:
            sh.com.cancel(f)
    
    def convert(self):
        f = '[CompressMedia] compress.Converter.convert'
        if self.Success:
            objs.get_progress().show()
            cur = 0
            total = len(self.get_ready())
            for ifile in self.ifiles:
                if not ifile.Skipped and not ifile.Failed:
                    mes = _('Process "{}" ({}/{})')
                    mes = mes.format(ifile.relpath,cur+1,total)
                    sh.objs.get_mes(f,mes,True).show_info()
                    objs.progress.set_text(mes)
                    objs.progress.update(cur,total)
                    if ifile.Image:
                        if not self._convert_photo (ifile.source
                                                   ,ifile.target
                                                   ):
                            ifile.Failed = True
                    elif ifile.Video:
                        if not self._convert_video (ifile.source
                                                   ,ifile.target
                                                   ):
                            ifile.Failed = True
                    cur += 1
            objs.progress.close()
        else:
            sh.com.cancel(f)
    
    def get_size(self):
        f = '[CompressMedia] compress.Converter.get_size'
        old_size = 0
        new_size = 0
        if self.Success:
            ''' We should only consider successfully processed files,
                since taking into account failed or skipped files can
                give a user a false impression that a lot of space can
                be freed.
            '''
            ifiles = self.get_ready()
            for ifile in ifiles:
                old_size += sh.File(ifile.source).get_size()
                new_size += sh.File(ifile.target).get_size()
        else:
            sh.com.cancel(f)
        return(old_size,new_size)
    
    def _convert_video(self,file,filew):
        try:
            ffmpy.FFmpeg (inputs  = {file:None}
                         ,outputs = {filew:None}
                         ).run()
            return True
        except Exception as e:
            self.rep_failed(f,e)
    
    def rep_failed(self,f,e):
        mes = _('Third-party module has failed!\n\nDetails: {}')
        mes = mes.format(e)
        sh.objs.get_mes(f,mes,True).show_error()
    
    def _convert_photo(self,file,filew):
        try:
            iimage = Image.open(file)
            iimage.save (fp       = filew
                        ,optimize = self.Optimize
                        ,quality  = self.image_quality
                        )
            iimage.close()
            return True
        except Exception as e:
            self.rep_failed(f,e)
    
    def set_target(self):
        f = '[CompressMedia] compress.Converter.set_target'
        if self.Success:
            for ifile in self.ifiles:
                ifile.targetdir = os.path.join(self.pathw,ifile.date)
                if ifile.Image:
                    ifile.target = os.path.join (ifile.targetdir
                                                ,ifile.relpath
                                                )
                elif ifile.Video:
                    ifile.target = os.path.join (ifile.targetdir
                                                ,ifile.filename+'.mp4'
                                                )
        else:
            sh.com.cancel(f)
    
    def create_folders(self):
        f = '[CompressMedia] compress.Converter.create_folders'
        if self.Success:
            folders = [ifile.targetdir for ifile in self.ifiles]
            folders = sorted(set(folders))
            for folder in folders:
                if not sh.Path(folder).create():
                    for ifile in self.ifiles:
                        if ifile.targetdir == folder:
                            ifile.Failed = True
        else:
            sh.com.cancel(f)
    
    def check(self):
        f = '[CompressMedia] compress.Converter.check'
        if self.path and self.pathw:
            self.idir = sh.Directory(self.path)
            self.Success = self.idir.Success \
                           and sh.Path(self.pathw).create()
            if self.Success:
                self.idirw = sh.Directory(self.pathw)
        else:
            self.Success = False
            sh.com.rep_empty(f)
    
    def get_date(self):
        f = '[CompressMedia] compress.Converter.get_date'
        if self.Success:
            pattern = '(IMG|VID)_(\d\d\d\d)(\d\d)(\d\d)_.*'
            for ifile in self.ifiles:
                match = re.match(pattern,ifile.relpath)
                if match:
                    if match.group(1) == 'IMG':
                        ifile.Image = True
                    else:
                        ifile.Video = True
                    ifile.date = '{}-{}-{}'.format (match.group(2)
                                                   ,match.group(3)
                                                   ,match.group(4)
                                                   )
                else:
                    ifile.Skipped = True
            if not self.get_ready():
                self.Success = False
                mes = _('Empty output is not allowed!')
                sh.objs.get_mes(f,mes,True).show_warning()
        else:
            sh.com.cancel(f)
    
    def get_files(self):
        f = '[CompressMedia] compress.Converter.get_files'
        if self.Success:
            files = self.idir.get_files()
            relfiles = self.idir.get_rel_files()
            if files and relfiles:
                for i in range(len(files)):
                    ifile = File()
                    ifile.source = files[i]
                    ifile.relpath = relfiles[i]
                    ifile.filename = sh.Path(ifile.relpath).get_filename()
                    self.ifiles.append(ifile)
            else:
                self.Success = False
                sh.com.rep_empty(f)
        else:
            sh.com.cancel(f)
    
    def run(self):
        f = '[CompressMedia] compress.Converter.run'
        self.itimer = sh.Timer(f)
        self.itimer.start()
        self.check()
        self.get_files()
        self.get_date()
        self.set_target()
        self.skip_existing()
        self.create_folders()
        self.convert()
        self.report()


objs = Objects()


if __name__ == '__main__':
    f = '__main__'
    sh.com.start()
    Converter(PATH,PATHW).run()
    mes = _('Goodbye!')
    sh.objs.get_mes(f,mes,True).show_debug()
    sh.com.end()
