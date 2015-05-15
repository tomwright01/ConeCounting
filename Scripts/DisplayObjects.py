import wx
from GenericControlPanel import GenericControlPanel
import logging
logger = logging.getLogger('ConeCounter.DisplayObjects')

class ControlPanel(GenericControlPanel):
    """A wx.panel to hold the main gui controls"""
    def __init__(self,parent,name):
        GenericControlPanel.__init__(self,parent,name)

        
        flt = BoundSpinCtrl(self,-1,'Filter',0,10,0)
        self.Bind(wx.EVT_SPINCTRL,self.on_update_spin)

        sizer=wx.GridBagSizer()
        sizer.Add(flt, pos=(0,0))
        #sizer.Add(pnl_disp, pos=(1,0))
        
        self.SetSizer(sizer)
    
    def on_update_spin(self,event):
        event.Skip()

class DisplayPanel(GenericControlPanel):
        """A panel containing controls for displaying the image
        """
        def __init__(self,parent,name):
            GenericControlPanel.__init__(self,parent,name)
            sizer = wx.BoxSizer(wx.VERTICAL)
            
            chkb_show_overlay = wx.CheckBox(self,-1,'Show overlay',name='chkb_show_overlay')
            self.Bind(wx.EVT_CHECKBOX,self._stateChange)
            self.Bind(GenericControlPanel.EVT_STATE_CHANGE,self.on_state_change)
            
            self._addControl(chkb_show_overlay)
            
            sizer.Add(chkb_show_overlay)
            self.SetSizer(sizer)
        
        def on_state_change(self,event):
            logger.debug('state change event detected')
            event.Skip()
            pass
        
        
class BoundSpinCtrl(wx.Panel):
    """A static text box with a spincontrol"""
    def __init__(self,parent,ID,name,minVal,maxVal,initVal):
        wx.Panel.__init__(self,parent,ID)
        self.value = initVal
        self.name = name
        
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        label = wx.StaticText(self,label=name)
        self.sc = wx.SpinCtrl(self,value=str(initVal))
        self.sc.SetRange(minVal,maxVal)
        self.Bind(wx.EVT_SPINCTRL,self.on_update_spin)
        
        sizer.Add(label)
        sizer.Add(self.sc)
        
        self.SetSizer(sizer)
        #sizer.Fit(self)
        
    def on_update_spin(self,event):
        self.value = self.sc.GetValue()
        event.SetEventObject(self) #Change the originating object to be the boundCtrl
        #logger.debug('Caught spin event at bound control')
        event.Skip()
        
    def getValue(self):
        return self.value
    
    def getName(self):
        return self.name