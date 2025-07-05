#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import os

from skl_shared.localize import _
from skl_shared.message.controller import Message, rep
from skl_shared.logic import Text
from skl_shared.launch import Launch
from skl_shared.table import Table
from skl_shared.paths import Path, Directory as shDirectory, Home
from skl_shared.graphics.root.controller import ROOT
from skl_shared.graphics.debug.controller import DEBUG as shDEBUG

DEBUG = False


class Directory:
    
    def __init__(self):
        self.no = 1
        self.src = ''
        self.src_rel = ''
        self.dst = ''
        self.dst_rel = ''



class HandleDir:
    
    def __init__(self, obj):
        self.desc = ''
        self.files = []
        self.formats = ('.jpg', '.jpeg', '.mp4', '.3gp', '.avi')
        self.Success = True
        self.obj = obj
        self.check()
    
    def debug(self):
        f = '[CompressMedia] rename_photos.HandleDir.debug'
        if not DEBUG:
            rep.lazy(f)
            return
        if not self.Success:
            rep.cancel(f)
            return
        if not self.files:
            rep.empty(f)
            return
        mes = list(self.files)
        mes.insert(0, _('MEDIA FILES:'))
        shDEBUG.reset(f, '\n'.join(mes))
        shDEBUG.show()
    
    def rename(self):
        f = '[CompressMedia] rename_photos.HandleDir.rename'
        if not self.Success:
            rep.cancel(f)
            return
        if not self.desc:
            self.Success = False
            rep.empty(f)
            return
        self.obj.dst_rel = f'{self.obj.src_rel} - {self.desc}'
        dirname = Path(self.obj.src).get_dirname()
        self.obj.dst = os.path.join(dirname, self.obj.dst_rel)
        shDirectory(self.obj.src, self.obj.dst).move()
    
    def input_desc(self):
        f = '[CompressMedia] rename_photos.HandleDir.input_desc'
        if not self.Success:
            rep.cancel(f)
            return
        mes = _('Input a description of this date: ')
        self.desc = input(mes)
    
    def show_images(self):
        f = '[CompressMedia] rename_photos.HandleDir.show_images'
        if not self.Success:
            rep.cancel(f)
            return
        if not self.files:
            self.Success = False
            rep.empty(f)
            return
        Launch(self.files[0]).launch_default()
    
    def run(self):
        self.check()
        self.set_files()
        self.debug()
        self.show_images()
        self.input_desc()
        self.rename()
    
    def set_files(self):
        f = '[CompressMedia] rename_photos.HandleDir.set_files'
        if not self.Success:
            rep.cancel(f)
            return
        subfiles = self.idir.get_subfiles()
        if not subfiles:
            self.Success = False
            mes = _('Empty output is not allowed!')
            Message(f, mes).show_warning()
            return
        for file in subfiles:
            if Path(file).get_ext_low() in self.formats:
                self.files.append(file)
    
    def check(self):
        f = '[CompressMedia] rename_photos.HandleDir.check'
        if not self.obj:
            self.Success = False
            rep.empty(f)
            return
        self.idir = shDirectory(self.obj.src)
        self.Success = self.idir.Success



class RenamePhotos:
    
    def __init__(self):
        self.Success = True
        self.idirs = []
        self.set_path()
    
    def set_path(self):
        f = '[CompressMedia] rename_photos.RenamePhotos.set_path'
        if not self.Success:
            rep.cancel(f)
            return
        self.path = Home('CompressMedia').add_share(_('processed'))
        self.idir = shDirectory(self.path)
        self.Success = self.idir.Success
    
    def loop(self):
        f = '[CompressMedia] rename_photos.RenamePhotos.loop'
        if not self.Success:
            rep.cancel(f)
            return
        for idir in self.idirs:
            HandleDir(idir).run()
    
    def debug(self):
        f = '[CompressMedia] rename_photos.RenamePhotos.debug'
        if not DEBUG:
            rep.lazy(f)
            return
        if not self.Success:
            rep.cancel(f)
            return
        iterable = []
        for idir in self.idirs:
            iterable.append([idir.no, idir.src, idir.src_rel, idir.dst
                           ,idir.dst_rel])
        headers = (_('#'), _('SOURCE'), _('SOURCE (REL)'), _('TARGET')
                  ,_('TARGET (REL)'))
        #,encloser = '"'
        mes = Table(headers = headers
                   ,iterable = iterable
                   ,Transpose = True
                   ,sep = '   ').run()
        shDEBUG.reset(f, mes)
        shDEBUG.show()
    
    def set_dirs(self):
        f = '[CompressMedia] rename_photos.RenamePhotos.set_dirs'
        if not self.Success:
            rep.cancel(f)
            return
        dirs = self.idir.get_dirs()
        reldirs = self.idir.reldirs
        if not dirs or not reldirs:
            self.Success = False
            mes = _('Empty output is not allowed!')
            Message(f, mes).show_warning()
            return
        for i in range(len(dirs)):
            itext = Text(reldirs[i])
            if not itext.has_cyrillic() and not itext.has_latin():
                idir = Directory()
                idir.no = i + 1
                idir.src = dirs[i]
                idir.src_rel = reldirs[i]
                self.idirs.append(idir)
    
    def run(self):
        self.set_dirs()
        self.debug()
        self.loop()


if __name__ == '__main__':
    f = '[CompressMedia] rename_photos.__main__'
    RenamePhotos().run()
    mes = _('Goodbye!')
    Message(f, mes).show_debug()
    ROOT.end()
