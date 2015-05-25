import logging
import numpy as np
import mahotas as mh
import os

import scipy.stats

logger = logging.getLogger('ConeCounter.AOImage')

class ConeCounts():
    """Object to hold cone count data"""
    def __init__(self):
        self.RegionalMaxima = None;
        self.Seeds=None;
        self.nPoints = None;
        self.dirty_rm = False;
        self.dirty_seeds = False;
        self.dirty_npoints = False;
        
    def SetRegionalMaxima(self,val):
        if not np.array_equal(self.RegionalMaxima,val):
            self.RegionalMaxima = val
            self.dirty_rm = True
        else:
            self.dirty_rm=False
            
    def SetSeeds(self,val):
        if not np.array_equal(self.Seeds,val):
            self.Seeds = val
            self.dirty_seeds = True
        else:
            self.dirty_seeds = False
            
    def SetNpoints(self,val):
        if not np.array_equal(self.nPoints,val):
            self.nPoints = val
            self.dirty_npoints = True
        else:
            self.dirty_npoints = False
            
    def IsDirty(self):
        return any([self.dirty_rm,self.dirty_seeds,self.dirty_npoints])
            
        
class AOImage():
    """AO Image data
    Going to define this as a seperate class to hold all the image processing functions
    """
    orgImage = None

    #Define a dictionary to hold the transform parameters
    params = {'threshold':None,
              'filter':None,
              'dirtyFilter':0,
              'filteredImage':None,
              'overlay':None,
              'curImage':None,
              'min_cone_size':None,
              'cone_display_size':1,
              'cones':None}
    
    def __init__(self,image=None):
        self.params = {'threshold':None,
                       'filter':None,
                       'dirtyFilter':0,
                       'filteredImage':None,
                       'overlay':None,
                       'curImage':None,
                       'min_cone_size':None,
                       'cone_display_size':1,
                       'cones':None}
        if image is not None:
            self.setOriginal(image)
        self.ConeCounts = ConeCounts()
        
    def getOriginal(self):
        return self.orgImage
    
    def getCurrent(self):
        #return the current image after any transformations have been applied
        if self.orgImage is None:
            #handle the case where an image hasn't been loaded.
            return None
        self.procImage()
        return self.params['curImage']

    def procImage(self):
        curImage = self.orgImage
                
        if self.params['filter'] > 0:
            curImage = self.filterImage(curImage,self.params['filter'])
        
        self.params['curImage'] = curImage
        self.params['threshold'] = self.thresholdImage(curImage)
        self.countCones()
        
    
    def getVeroniImage(self):
        if self.ConeCounts.Seeds is None:
            logger.error('Regional maxima must be discovered first')
            raise RuntimeError,"Regional maxima must be discovered first"
        return mh.segmentation.gvoronoi(self.ConeCounts.Seeds)
    
    def countCones(self):
        self.ConeCounts.SetRegionalMaxima(mh.regmax(self.params['curImage']))
        s,ncones=mh.label(self.ConeCounts.RegionalMaxima)        
        self.ConeCounts.SetSeeds(s)
        self.ConeCounts.SetNpoints(ncones)
        
        if self.params['min_cone_size'] > 0:
            mask = np.ones((self.params['min_cone_size'],self.params['min_cone_size']))
            rm=mh.dilate(self.ConeCounts.RegionalMaxima,mask)
            self.ConeCounts.SetRegionalMaxima(mh.regmax(rm))
            s,ncones = mh.label(self.ConeCounts.RegionalMaxima)
            self.ConeCounts.SetSeeds(s)
            self.ConeCounts.SetNpoints(ncones)


        #self.segmentCones()

    def segmentCones(self):
        """Function to take regional maxima and segment the cones from them"""
        dist = mh.distance(self.orgImage > self.params['threshold'])
        dist = dist.max() - dist
        dist = dist = dist - dist.min()
        dist = dist/float(dist.ptp()) * 255
        dist = dist.astype(np.uint8)
        self.params['cones'] = mh.cwatershed(dist, self.ConeCounts.Seeds)
            
    def GetConeCounts(self,region):
        """returns two values, total number of cones and number of cones in current region
        region = (xmin,xmax,ymax,ymin)"""
        if self.ConeCounts.Seeds is None:
            return (None,None)
        
        seeds = self.ConeCounts.Seeds
        mask = np.ones(self.orgImage.shape,np.bool)
        mask[region[3]:region[2],region[0]:region[1]] = 0
        at_border = np.unique(seeds[mask]) #select seeds falling outside of the borders
        for obj in at_border:
            seeds[seeds == obj] = 0
        [seeds,ncones] = mh.label(seeds)
        return (self.ConeCounts.nPoints,ncones)
        
    def SetOriginal(self,image):
        if not isinstance(image,np.ndarray):
            logger.error("Invalid image type: %s supplied",type(image))
            raise TypeError,"Invalid image supplied, expected ndarray"
        self.orgImage = image

        
    def thresholdImage(self,image):
        self.params['threshold'] = mh.thresholding.otsu(np.uint8(image))
        
    def filterImage(self,image,sd):
        if self.params['dirtyFilter']:
            self.params['filteredImage'] = mh.gaussian_filter(image,sd)
            self.params['dirtyFilter'] = 0
        return self.params['filteredImage']
        
    def setFilter(self,value):
        if not isinstance(value,int):
            value = int(value)
        if self.params['filter'] != value:
            self.params['filter'] = value
            self.params['dirtyFilter'] = 1
            
        
    def setMinConeSize(self,value):
        if not isinstance(value,int):
            value = int(value)
        self.params['min_cone_size'] = value
        
    def setDisplayConeSize(self,value):
        if not isinstance(value,int):
            value = int(value)
        self.params['display_cone_size'] = value
        
    def loadFrame(self, fname):
        """Load a frame from a file"""
        if not os.path.isfile(fname):
            logger.error('Invalid filename: %s provided',fname)
            raise IOError
        
        image = mh.imread(fname)
        if len(image.shape) > 2:
            image = image[:,:,0]
        if image.size == 1:
            #There are problems with some greyscale png images
            logger.error('Invalid image: %s provided: is it grayscale png?',fname)
            raise TypeError,"Invalid image type"       
    
        self.SetOriginal(image)
        
    def getMaximaImage(self):
        """returns an RGBA type array suitable for overlay"""
        r = self.params['display_cone_size'] + 1 #use this value for now....
        #generate a circle mask
        [y,x] = np.ogrid[-r:r,-r:r]
        mask = x*x + y*y <= r
        
        if np.count_nonzero(self.ConeCounts.Seeds) != self.ConeCounts.nPoints:
            #Some regional maxima are not points
            #this is a slow function, only required for display
            self._filterMaxima()
        
        newImg = np.zeros(self.ConeCounts.Seeds.shape + (4,),dtype=np.uint8)   #create a new array of size orgImage but 4D
        newImg[:,:,1] = self.ConeCounts.Seeds > 0
        newImg[:,:,1] = mh.dilate(newImg[:,:,1],mask) * 255
        newImg[:,:,3][newImg[:,:,1]>0] = 1

        return np.float64(newImg)

    
    def _filterMaxima(self):
        #replace seeds that are larger than one pixel with the center of mass
        frequencies = scipy.stats.itemfreq(self.ConeCounts.Seeds)
        frequencies = frequencies[frequencies[:,0]>0,:] #remove the 0 values
        frequencies = frequencies[frequencies[:,1]>1,:] #isolate only values with counts >1
        seeds = self.ConeCounts.Seeds
        for lab in frequencies[:,0]:
            coords = np.argwhere(seeds==lab)
            seeds[seeds==lab] = 0 #remove the current label
            [y,x] = np.apply_along_axis(np.mean,0,coords)
            seeds[y,x]=lab
        self.ConeCounts.SetSeeds(seeds)
        
    def filterPointsByDistance(self):
        #TODO
        pass
    
    def GetImageSize(self):
        """Returns a tuple containing the image size
        GetImageSize = (xmin,xmax,ymax,ymin)"""
        s = self.orgImage.shape
        
        return (0,s[1],s[0],0)
    
if __name__ == '__main__':
    logger = logging.getLogger(__name__)
    formatter = logging.Formatter('%(levelname)s - %(message)s')
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)    
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
