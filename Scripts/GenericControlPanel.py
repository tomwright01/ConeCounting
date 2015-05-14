import wx
import wx.lib.newevent

evtStateChange, EVT_STATE_CHANGE = wx.lib.newevent.NewEvent()

class GenericControlPanel(wx.Panel):
    """This is a generic panel for handling controls
    It defines a custom event EVT_STATE_CHANGE that should be fired whenever a widget that the parent needs to know about is updated
    """
    name=None
    def __init__(self,parent,name):
        wx.Panel.__init__(self,parent)
        self.name=name
        
    def _stateChange(self,ev):
        newEvt = evtStateChange(src=self.name,
                             value=evt.GetEventObject().GetValue())
        wx.PostEvent(parent,newEvt)