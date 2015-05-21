import wx
import os
import logging
from GenericControlPanel import GenericControlPanel

logger = logging.getLogger('ConeCounter.FileControl')

class FileControl(GenericControlPanel):
    evtMoveNext, EVT_MOVE_NEXT = wx.lib.newevent.NewCommandEvent()
    evtMarkComplete, EVT_MARK_COMPLETE = wx.lib.newevent.NewCommandEvent()
    evtMarkSkip, EVT_MARK_SKIP = wx.lib.newevent.NewCommandEvent()
    
    
    def __init__(self,*args,**kwargs):
        GenericControlPanel.__init__(self,*args,**kwargs)
        self.fileList=[]
        self.dirpath=''
        
        btn_next = wx.Button(self,wx.ID_FORWARD,'Next')
        btn_complete = wx.Button(self,wx.ID_EXECUTE,'Mark Complete')
        btn_skip = wx.Button(self,wx.ID_FILE,'Skip')
                             
        lbl_notes = wx.StaticText(self,-1,'Notes:')
        txt_notes = wx.TextCtrl(self,-1,name='txt_notes',size=(200,50))

        self.Bind(wx.EVT_TEXT,self._stateChange)
        self._addControl(txt_notes)        

        sizer=wx.BoxSizer(wx.VERTICAL)
        sizer.Add(btn_next)
        sizer.Add(lbl_notes)
        sizer.Add(txt_notes)
        sizer.Add(btn_complete)
        sizer.Add(btn_skip)
        
        self.SetSizer(sizer)
        
        self.Bind(wx.EVT_BUTTON,self._MoveNext,btn_next)
        self.Bind(wx.EVT_BUTTON,self._MarkComplete,btn_complete)
        self.Bind(wx.EVT_BUTTON,self._MarkSkip,btn_skip)
        
    def _MoveNext(self,evt):
        logger.debug('Move next event detected')
        newEvt = self.evtMoveNext(wx.ID_ANY)
        wx.PostEvent(self,newEvt)    
        
    def _MarkComplete(self,evt):
        logger.debug('Mark complete event detected')
        newEvt = self.evtMarkComplete(wx.ID_ANY)
        wx.PostEvent(self,newEvt)    
    
    def _MarkSkip(self,evt):
        logger.debug('Skip event detected')
        newEvt = self.evtMarkSkip(wx.ID_ANY)
        wx.PostEvent(self,newEvt)            