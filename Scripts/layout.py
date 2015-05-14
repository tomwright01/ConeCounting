import wx

class MyFrame(wx.Frame):
    """This will be the main window"""
    
    def __init__(self,parent,title):
        wx.Frame.__init__(self,parent,title=title,size=(800,600))
        
        self.left=LeftPanel(self)
        self.right=RightPanel(self)
        
        sizer=wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.left,2,wx.EXPAND)
        sizer.Add(self.right,1,wx.EXPAND)
        
        self.SetAutoLayout(True)
        self.SetSizer(sizer)
        self.Layout()
        self.Show(True)
        
class LeftPanel(wx.Panel):
    """This will be the left panel
    """
    def __init__(self,parent):
        wx.Panel.__init__(self,parent)
        self.SetBackgroundColour((123,0,0))
        
class RightPanel(wx.Panel):
    """This will be the left panel
    """
    def __init__(self,parent):
        wx.Panel.__init__(self,parent)
        self.SetBackgroundColour((0,123,0))

        subPanel = SubPanel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(subPanel)
        self.SetSizer(sizer)
        
class SubPanel(wx.Panel):
    """This is a subpanel containing controls
    """
    def __init__(self,parent):
        wx.Panel.__init__(self,parent)
        self.SetBackgroundColour((0,0,123))
        btn1 = wx.Button(self,-1,'Button 1')
        btn2 = wx.Button(self,-1,'Button 2')
        
        sizer=wx.BoxSizer(wx.VERTICAL)
        sizer.Add(btn1,wx.EXPAND)
        sizer.Add(btn2,wx.EXPAND)
        
        self.SetSizer(sizer)
        
        
if __name__ == '__main__':
    app = wx.App(False)
    frame = MyFrame(None,'ConeCounter')
    frame.Show()
    app.MainLoop()