import wx
import os
import logging

logger = logging.getLogger('ConeCounter.FileControl')

class FileControl(wx.Panel):
    def __init__(self,*args,**kwargs):
        wx.Panel.__init__(self,*args,**kwargs)
        self.fileList={}
        self.dirpath=''
        
        btn_getFiles = wx.Button(self,-1,'Get Files')
        
        self.Bind(wx.EVT_BUTTON,self.LoadFiles)
        
        sizer=wx.BoxSizer(wx.VERTICAL)
        sizer.Add(btn_getFiles)
        
        self.SetSizer(sizer)
        
    def LoadFiles(self,event):
        dlg = wx.DirDialog(self, "Choose a directory", self.dirpath, wx.DD_DIR_MUST_EXIST)
        if dlg.ShowModal() == wx.ID_OK:
            self.dirpath = dlg.GetPath()
        dlg.Destroy()        