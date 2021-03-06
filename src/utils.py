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
            failed = []
            mes = _('Do you REALLY want to replace your original files with converted ones?\n\nIt is highly recommended to create a backup first.')
            if sh.objs.get_mes(f,mes).show_question():
                objs.get_progress().show()
                for i in range(len(self.ifiles)):
                    mes = _('Move "{}" ({}/{})')
                    mes = mes.format (self.ifiles[i].relpath
                                     ,i + 1
                                     ,len(self.ifiles)
                                     )
                    sh.objs.get_mes(f,mes,True).show_info()
                    objs.progress.set_text(mes)
                    objs.progress.update(i,len(self.ifiles))
                    if os.path.exists(self.ifiles[i].target) \
                    and not self.ifiles[i].Failed:
                        bname = sh.Path(self.ifiles[i].target).get_basename()
                        new_mod_dir = os.path.join (self.path
                                                   ,str(self.ifiles[i].date)
                                                   )
                        new_mod_file = os.path.join(new_mod_dir,bname)
                        if new_mod_file in (self.ifiles[i].source
                                           ,self.ifiles[i].target
                                           ):
                            mes = _('Wrong input data: "{}"!')
                            mes = mes.format(new_mod_file)
                            sh.objs.get_mes(f,mes,True).show_warning()
                            failed.append(self.ifiles[i].target)
                        else:
                            if sh.Path(new_mod_dir).create():
                                if sh.File (self.ifiles[i].target
                                           ,new_mod_file
                                           ).move():
                                    if not sh.File(self.ifiles[i].source).delete():
                                        failed.append(self.ifiles[i].source)
                                else:
                                    failed.append(self.ifiles[i].target)
                            else:
                                failed.append(self.ifiles[i].target)
                objs.progress.close()
                if failed:
                    mes = _('Failed to process the following files:')
                    mes = mes + '\n' + '\n'.join(failed)
                    sh.objs.get_mes(f,mes).show_warning()
                else:
                    mes = _('Operation was a success.\nProcessed files: {}.')
                    mes = mes.format(len(self.ifiles))
                    sh.objs.get_mes(f,mes).show_info()
            else:
                mes = _('Operation has been canceled by the user.')
                objs.get_mes(f,mes,True).show_info()
        else:
            sh.com.cancel(f)



class Objects:
    
    def __init__(self):
        self.progress = None
    
    def get_progress(self):
        if self.progress is None:
            self.progress = sh.ProgressBar (title = _('Operation progress')
                                           ,icon = cm.ICON
                                           )
            self.progress.add()
        return self.progress


com = Commands(cm.PATH,cm.PATHW)
objs = Objects()


if __name__ == '__main__':
    f = '[CompressMedia] utils.__main__'
    sh.com.start()
    com.replace_original()
    mes = _('Goodbye!')
    sh.objs.get_mes(f,mes,True).show_debug()
    sh.com.end()
