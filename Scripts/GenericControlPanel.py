import wx
import wx.lib.newevent
import logging

logger = logging.getLogger('ConeCounter.GenericControlPanel')




class GenericControlPanel(wx.Panel):
    """This is a generic panel for handling controls
    It defines a custom event EVT_STATE_CHANGE that should be fired whenever a widget that the parent needs to know about is updated
    """
    name=None
    myControls = {}
    evtStateChange, EVT_STATE_CHANGE = wx.lib.newevent.NewEvent()
    
    def __init__(self,parent,name):
        wx.Panel.__init__(self,parent)
        self.name=name
        
    def _stateChange(self,evt):
        logger.debug('State change event detected')
        newEvt = self.evtStateChange(pnlName=self.name,
                                     src=evt.GetEventObject().Name,
                                     value=evt.GetEventObject().GetValue())
        wx.PostEvent(self,newEvt)
        
    def _addControl(self,control):
        self.myControls[control.Name]=control.GetValue()
                
    def registerControls(self):
        """Function to register controls with the parent
        """
        return self.myControls    