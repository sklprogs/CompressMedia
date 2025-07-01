#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import os
import re
import ffmpy
from PIL import Image

from skl_shared.localize import _
from skl_shared.message.controller import Message, rep
from skl_shared.graphics.root.controller import ROOT
from skl_shared.graphics.icon.controller import ICON
from skl_shared.graphics.progress_bar.controller import PROGRESS
from skl_shared.paths import File as shFile, Directory, Home, PDIR, Path
from skl_shared.time import Timer
from skl_shared.logic import com


ICON.set(PDIR.add('..', 'resources', 'CompressMedia.png'))
ROOT.set_icon()
ihome = Home('CompressMedia')
PATH = ihome.add_share(_('not processed'))
PATHW = ihome.add_share(_('processed'))
IMAGE_TYPES = ('.jpg', '.jpeg')
VIDEO_TYPES = ('.mp4', '.3gp', '.avi')


class File:
    
    def __init__(self):
        self.source = ''
        self.basename = ''
        self.filename = ''
        self.target = ''
        self.targetdir = ''
        self.date = ''
        self.Image = False
        self.Video = False
        self.Failed = False
        self.Skipped = False



class Converter:
    
    def __init__(self, path, pathw, image_quality=65, Optimize=True, ConvertVideo=True):
        self.ifiles = []
        self.path = path
        self.pathw = pathw
        self.Success = True
        self.image_quality = image_quality
        self.Optimize = Optimize
        self.ConvertVideo = ConvertVideo
    
    def get_ready(self):
        return [ifile for ifile in self.ifiles \
               if not ifile.Skipped and not ifile.Failed]
    
    def report(self):
        f = '[CompressMedia] compress_media.Converter.report'
        if not self.Success:
            rep.cancel(f)
            return
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
            percent = round((100 * size_diff) / old_size)
        else:
            percent = 0
        old_size = com.get_human_size(old_size, True)
        new_size = com.get_human_size(new_size, True)
        size_diff = com.get_human_size(size_diff, True)
        sub = _('Processed data: {}').format(old_size)
        mes.append(sub)
        sub = _('Converted data: {}').format(new_size)
        mes.append(sub)
        sub = _('Compression: {} ({}%)').format(size_diff, percent)
        mes.append(sub)
        delta = com.get_human_time(self.itimer.end())
        sub = _('The operation has taken {}').format(delta)
        mes.append(sub)
        mes = '\n'.join(mes)
        Message(f, mes, True).show_info()
    
    def skip_existing(self):
        f = '[CompressMedia] compress_media.Converter.skip_existing'
        if not self.Success:
            rep.cancel(f)
            return
        for ifile in self.ifiles:
            if os.path.exists(ifile.target):
                ifile.Skipped = True
    
    def convert(self):
        f = '[CompressMedia] compress_media.Converter.convert'
        if not self.Success:
            rep.cancel(f)
            return
        PROGRESS.set_title(_('Convert Media Files'))
        PROGRESS.set_value(0)
        PROGRESS.set_max(len(self.get_ready()))
        PROGRESS.show()
        for ifile in self.ifiles:
            if ifile.Skipped or ifile.Failed:
                continue
            PROGRESS.update()
            mes = _('Process "{}" ({}/{})').format(ifile.filename, PROGRESS.get_value() + 1, PROGRESS.get_max())
            PROGRESS.set_info(mes)
            if ifile.Image:
                if not self._convert_photo(ifile.source, ifile.target):
                    ifile.Failed = True
            elif ifile.Video:
                if self.ConvertVideo:
                    if not self._convert_video(ifile.source, ifile.target):
                        ifile.Failed = True
                elif not shFile(ifile.source, ifile.target).copy():
                    ifile.Failed = True
            PROGRESS.inc()
        PROGRESS.close()
    
    def get_size(self):
        f = '[CompressMedia] compress_media.Converter.get_size'
        if not self.Success:
            rep.cancel(f)
            return(0, 0)
        ''' We should only consider successfully processed files, since taking
            into account failed or skipped files can give a user a false
            impression that a lot of space can be freed.
        '''
        old_size = 0
        new_size = 0
        ifiles = self.get_ready()
        for ifile in ifiles:
            old_size += shFile(ifile.source).get_size()
            new_size += shFile(ifile.target).get_size()
        return(old_size, new_size)
    
    def _convert_video(self, file, filew):
        f = '[CompressMedia] compress_media.Converter._convert_video'
        try:
            ffmpy.FFmpeg(inputs={file: None}, outputs={filew: None}).run()
            return True
        except Exception as e:
            self.rep_failed(f, e)
    
    def rep_failed(self, f, e):
        mes = _('Third-party module has failed!\n\nDetails: {}').format(e)
        Message(f, mes).show_error()
    
    def _convert_photo(self, file, filew):
        f = '[CompressMedia] compress_media.Converter._convert_photo'
        try:
            iimage = Image.open(file)
            iimage.save(fp = filew, optimize = self.Optimize
                       ,quality = self.image_quality)
            iimage.close()
            return True
        except Exception as e:
            self.rep_failed(f, e)
    
    def set_target(self):
        f = '[CompressMedia] compress_media.Converter.set_target'
        if not self.Success:
            rep.cancel(f)
            return
        for ifile in self.ifiles:
            ifile.targetdir = os.path.join(self.pathw, ifile.date)
            if ifile.Image:
                ifile.target = os.path.join(ifile.targetdir, ifile.filename)
            elif ifile.Video:
                # We explicitly convert all videos to MP4
                ifile.target = os.path.join(ifile.targetdir
                                           ,ifile.basename + '.mp4')
    
    def create_folders(self):
        f = '[CompressMedia] compress_media.Converter.create_folders'
        if not self.Success:
            rep.cancel(f)
            return
        folders = [ifile.targetdir for ifile in self.ifiles]
        folders = sorted(set(folders))
        for folder in folders:
            if Path(folder).create():
                continue
            for ifile in self.ifiles:
                if ifile.targetdir == folder:
                    ifile.Failed = True
    
    def check(self):
        f = '[CompressMedia] compress_media.Converter.check'
        if not self.path or not self.pathw:
            self.Success = False
            rep.empty(f)
            return
        self.idir = Directory(self.path)
        self.Success = self.idir.Success and Path(self.pathw).create()
        if self.Success:
            self.idirw = Directory(self.pathw)
    
    def _get_date_android6(self, basename):
        match = re.match('(IMG|VID)_(\d\d\d\d)(\d\d)(\d\d)_.*', basename)
        if match:
            return f'{match.group(2)}-{match.group(3)}-{match.group(4)}'
    
    def _get_date_android10(self, basename):
        match = re.match('(\d\d\d\d)(\d\d)(\d\d)_.*', basename)
        if match:
            return f'{match.group(1)}-{match.group(2)}-{match.group(3)}'
    
    def _get_date_winphone(self, basename):
        match = re.match('WP_(\d\d\d\d)(\d\d)(\d\d)_\d\d_\d\d_\d\d_*', basename)
        if match:
            return f'{match.group(1)}-{match.group(2)}-{match.group(3)}'
    
    def set_date(self):
        f = '[CompressMedia] compress_media.Converter.set_date'
        if not self.Success:
            rep.cancel(f)
            return
        for ifile in self.ifiles:
            date = self._get_date_android6(ifile.basename)
            if not date:
                date = self._get_date_android10(ifile.basename)
            if not date:
                date = self._get_date_winphone(ifile.basename)
            if date:
                ifile.date = date
            else:
                ifile.Skipped = True
    
    def get_useful(self):
        f = '[CompressMedia] compress_media.Converter.get_useful'
        if not self.get_ready():
            self.Success = False
            mes = _('Empty output is not allowed!')
            Message(f, mes).show_warning()
    
    def get_files(self):
        f = '[CompressMedia] compress_media.Converter.get_files'
        if not self.Success:
            rep.cancel(f)
            return
        files = self.idir.get_subfiles()
        if not files:
            self.Success = False
            rep.empty(f)
            return
        for i in range(len(files)):
            ifile = File()
            ifile.source = files[i]
            ipath = Path(files[i])
            ifile.basename = ipath.get_basename()
            ifile.filename = ipath.get_filename()
            ext_low = ipath.get_ext_low()
            if ext_low in IMAGE_TYPES:
                ifile.Image = True
            elif ext_low in VIDEO_TYPES:
                ifile.Video = True
            else:
                ifile.Skipped = True
            self.ifiles.append(ifile)
    
    def run(self):
        f = '[CompressMedia] compress_media.Converter.run'
        self.itimer = Timer(f)
        self.itimer.start()
        self.check()
        self.get_files()
        self.set_date()
        self.get_useful()
        self.set_target()
        self.skip_existing()
        self.create_folders()
        self.convert()
        self.report()


if __name__ == '__main__':
    f = '[CompressMedia] compress_media.__main__'
    Converter(PATH, PATHW, ConvertVideo=False).run()
    mes = _('Goodbye!')
    Message(f, mes).show_debug()
    ROOT.end()
