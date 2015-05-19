import wx
from GenericControlPanel import GenericControlPanel
import logging
logger = logging.getLogger('ConeCounter.DisplayObjects')

class ControlPanel(GenericControlPanel):
    """A wx.panel to hold the main gui controls"""
    def __init__(self,parent,name):
        GenericControlPanel.__init__(self,parent,name)

        
        flt = BoundSpinCtrl(self,-1,'filter','Filter',0,10,0)
        min_cone_size = BoundSpinCtrl(self,-1,'min_cone_size','Minimum cone size',0,10,0)

        self.Bind(wx.EVT_SPINCTRL,self._stateChange)
        self._addControl(flt)
        self._addControl(min_cone_size)
        
        sizer=wx.BoxSizer(wx.VERTICAL)
        sizer.Add(flt, flag=wx.ALIGN_RIGHT)
        sizer.Add(min_cone_size, flag=wx.ALIGN_RIGHT)
        
        self.SetSizer(sizer)
    

class DisplayPanel(GenericControlPanel):
        """A panel containing controls for displaying the image
        """
        def __init__(self,parent,name):
            GenericControlPanel.__init__(self,parent,name)
            sizer = wx.BoxSizer(wx.VERTICAL)
            
            chkb_show_overlay = wx.CheckBox(self,-1,'Show overlay',name='chkb_show_overlay')
            cmb_select_base_image = wx.ComboBox(self,-1,value='Current',
                                                choices=['Current','Original'],
                                                style=wx.CB_READONLY,
                                                name='cmb_select_base_image')
            
            display_cone_size = BoundSpinCtrl(self, -1, 'display_cone_size', 'Marker Size', 1, 
                                             10, 
                                             1)
            self.Bind(wx.EVT_CHECKBOX,self._stateChange)
            self.Bind(wx.EVT_COMBOBOX,self._stateChange)
            self.Bind(wx.EVT_SPINCTRL,self._stateChange)
            
            self.Bind(GenericControlPanel.EVT_STATE_CHANGE,self.on_state_change)
            
            self._addControl(chkb_show_overlay)
            self._addControl(cmb_select_base_image)
            self._addControl(display_cone_size)    
            
            sizer.Add(cmb_select_base_image)
            sizer.Add(chkb_show_overlay)
            sizer.Add(display_cone_size)
            self.SetSizer(sizer)
        
        def on_state_change(self,event):
            logger.debug('state change event detected')
            event.Skip()
            pass
        
        
class BoundSpinCtrl(wx.Panel):
    """A static text box with a spincontrol"""
    def __init__(self,parent,ID,name,label,minVal,maxVal,initVal):
        wx.Panel.__init__(self,parent,ID)
        self.value = initVal
        self.Name = name
        
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        label = wx.StaticText(self,label=label)
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
        
    def GetValue(self):
        return self.value
    
    def GetName(self):
        return self.name


class ResultsPanel(wx.Panel):
    """Class for displaying the results"""
    def __init__(self,parent,name):
        wx.Panel.__init__(self,parent)
        self.name=name
        self.myControls = {}
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        self.lbl_ncones_total = wx.StaticText(self,label='Total cones: None')
        self.lbl_ncones_region = wx.StaticText(self,label='Region cones: None')
        
        sizer.Add(self.lbl_ncones_total)
        sizer.Add(self.lbl_ncones_region)
        
        self.SetSizer(sizer)
        
    def updateConeCounts(self,value):
        """Update hte text displayed in the cone count labels
        value = (totalCount,regionCount)"""
        self.lbl_ncones_total.SetLabel('Total cones: {}'.format(value[0]))
        self.lbl_ncones_region.SetLabel('Region cones: {}'.format(value[1]))