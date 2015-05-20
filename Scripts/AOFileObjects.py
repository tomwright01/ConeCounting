import logging
import numbers
import wx
import os
import csv
logger = logging.getLogger('ConeCounter.FileObjects')

class AOFileList():
    'Iterable collection for AOFile objects'
    
    def __init__(self,*args):
        self._register = []
        self._curobj = 0
        
        for obj in args:
            self.append(obj)
                
    def append(self,obj):
        if not isinstance(obj,AOFile):
            raise TypeError()
        self._register.append(obj)
        
    def add(self,*args,**kwargs):
        newFile = AOFile(*args,**kwargs)
        self.append(newFile)

    def next(self):
        if self._curobj < len(self._register):
            obj = self._register[self._curobj]
            self._curobj = self._curobj + 1
            return obj
        else:
            self.moveFirst()
            raise StopIteration

    def __getitem__(self,item):
        return self._register[item]

    def GetIncomplete(self):
        #returns the index of incomplete records
        return [i for i,val in enumerate(self) if not val.complete]
    
    def moveFirst(self):
        self._curobj = 0
        
    def __len__(self):
        return len(self._register)
        
    def Save(self,parent,fname=None):
        if fname is None:

            dlg = wx.FileDialog(parent,"Select target",".","imagelist.csv","",wx.FD_OVERWRITE_PROMPT)
            if dlg.ShowModal() == wx.ID_OK:
                fname = os.path.join(dlg.GetDirectory(),
                                     dlg.GetFilename())
            dlg.Destroy()
            csvfile = open(fname,'wb')
            myWriter = csv.writer(csvfile, delimiter = ',',
                                  quotechar = '"', quoting = csv.QUOTE_MINIMAL)
            myWriter.writerow('Filename',
                              'TotalCones',
                              'RegionCones',
                              'Region',
                              'Notes',
                              'Complete')
            for obj in self:
                myWriter.writerow(obj.filename,
                                  obj.totalcones,
                                  obj.regioncones,
                                  obj.region,
                                  obj.notes,
                                  obj.complete)
            csvfile.close()
            
    def __iter__(self):
        return self

class AOFile():
    'Information on an AOfile'
    def __init__(self,**kwargs):
        
        if 'filename' in kwargs:
            self.filename = kwargs['filename']
        else:
            self.filename = None
        if 'totalcones' in kwargs:
            self.totalcones = kwargs['totalcones']
        else:
            self.totalcones = None
        if 'regioncones' in kwargs:
            self.regioncones = kwargs['regioncones']
        else:
            self.regioncones = None
        if 'region' in kwargs:
            self.region = kwargs['region']
        else:
            self.region = None
        if 'notes' in kwargs:
            self.notes = kwargs['notes']
        else:
            self.notes = None
        if 'complete' in kwargs:
            self.complete = kwargs['complete']
        else:
            self.complete = False

    def SetFilename(self,filename):
        self._filename=filename
        
    def GetFilename(self):
        return self._filename
    
    def SetTotalCones(self,count):
        if not isinstance(count,int):
            count = int(count)
        self._totalcones = count
        
    def GetTotalCones(self):
        return self._totalcones
        
    def SetRegionCones(self,count):
        if not isinstance(count,int):
            count = int(count)
        self._regioncones = count
        
    def GetRegionCones(self):
        return self._regioncones
    
    def SetRegion(self,region):
        if isinstance(region,basestring):
            logger.debug('Invalid region passed, expected tuple or list')
            raise TypeError()
        if len(region != 4):
            logger.debug('Invalid region passed, expected length 4')
            raise TypeError()
        if not all(isinstance(x,numbers.Integral) for x in region):
            logger.debug('Invalid region passed, expected length 4')
            raise TypeError()            
            
        self._region = region
    
    def GetRegion(self):
        return self._region
    
    def SetNotes(self,note,append = True):
        if append:
            self._notes = self._notes + note
        else:
            self._notes = note
        
    def GetNotes(self):
        return self._note
    
    def SetComplete(self,val):
        if not isinstance(val,bool):
            logger.debug('Invalid value setting complete: expected boolean')
            raise TypeError()
        self._complete = val
        
    def GetComplete(self):
        return self.complete
    
    def __repr__(self):
        return '{0},{1},{2},{3},{4},{5}'.format(self.filename,
                                                   str(self.totalcones),
                                                   str(self.regioncones),
                                                   str(self.region),
                                                   str(self.notes),
                                                   str(self.complete))
    
    filename = property(fget=GetFilename, fset=SetFilename)
    totalcones = property(fget=GetTotalCones, fset=SetTotalCones)
    regioncones = property(fget=GetRegionCones, fset=SetRegionCones)
    region = property(fget=GetRegion, fset=SetRegion)    
    notes = property(fget=GetNotes, fset=SetNotes)
    complete = property(fget=GetComplete, fset=SetComplete)
    
    
