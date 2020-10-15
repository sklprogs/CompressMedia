#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import os

import skl_shared.shared as sh
from skl_shared.localize import _

import compress as cm


class Commands(cm.Converter):
    
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.check()
        self.get_files()
        self.get_date()
        self.set_target()
    
    def replace_original(self):
        f = '[CompressMedia] utils.Commands.replace_original'
        if self.Success:
            mes = []
            for ifile in self.ifiles:
                if os.path.exists(ifile.target) and not ifile.Failed:
                    bname = sh.Path(ifile.target).get_basename()
                    new_mod_dir = os.path.join (self.path
                                               ,str(ifile.date)
                                               )
                    new_mod_file = os.path.join(new_mod_dir,bname)
                    mes.append('===================================')
                    sub = _('Create "{}"').format(new_mod_dir)
                    mes.append(sub)
                    sub = _('Move: "{}" -> "{}"')
                    sub = sub.format(ifile.target,new_mod_file)
                    mes.append(sub)
                    sub = _('Delete "{}"').format(ifile.source)
                    mes.append(sub)
            mes = '\n'.join(mes)
            sh.com.run_fast_debug(f,mes)
        else:
            sh.com.cancel(f)


com = Commands(cm.PATH,cm.PATHW)


if __name__ == '__main__':
    f = '[CompressMedia] utils.__main__'
    com.replace_original()
