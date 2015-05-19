import logging
import numpy as np
import mahotas as mh
import os

from scipy import stats

logger = logging.getLogger('ConeCounter.AOImage')

class AOImage():
    """AO Image data
    Going to define this as a seperate class to hold all the image processing functions
    """
    orgImage = None

    #Define a dictionary to hold the transform parameters
    params = {'threshold':None,
              'filter':None,
              'regional_maxima':None,
              'overlay':None,
              'seeds':None,
              'nPoints':None,
              'curImage':None,
              'min_cone_size':None,
              'cone_display_size':1}
    
    def __init__(self,image=None):
        if image is not None:
            self.setOriginal(image)
        
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
        if self.params['seeds'] is None:
            logger.error('Regional maxima must be discovered first')
            raise RuntimeError,"Regional maxima must be discovered first"
        return mh.segmentation.gvoronoi(self.params['seeds'])
    
    def countCones(self):
        self.params['regional_maxima'] = mh.regmax(self.params['curImage'])
        self.params['seeds'],self.params['npoints'] = mh.label(self.params['regional_maxima'])        
        logger.debug('found %s cones before filter',self.params['npoints']) 
        if self.params['min_cone_size'] > 0:
            mask = np.ones((self.params['min_cone_size'],self.params['min_cone_size']))
            self.params['regional_maxima'] = mh.dilate(self.params['regional_maxima'],mask)
            self.params['regional_maxima'] = mh.regmax(self.params['regional_maxima'])
            self.params['seeds'],self.params['npoints'] = mh.label(self.params['regional_maxima'])        
        logger.debug('found %s cones after filter',self.params['npoints']) 
        if np.count_nonzero(self.params['seeds']) != self.params['npoints']:
            #Some regional maxima are not points
            self._filterMaxima()
            
    def getConeCounts(self):
        #returns two values, total number of cones and number of cones in current region
        mask = np.bool(self.orgImage.shape)
        
        
    def setOriginal(self,image):
        if not isinstance(image,np.ndarray):
            logger.error("Invalid image type: %s supplied",type(image))
            raise TypeError,"Invalid image supplied, expected ndarray"
        self.orgImage = image

        
    def thresholdImage(self,image):
        self.params['threshold'] = mh.thresholding.otsu(np.uint8(image))
        
    def filterImage(self,image,sd):
        return mh.gaussian_filter(image,sd)
        
    def setFilter(self,value):
        if not isinstance(value,int):
            value = int(value)
        self.params['filter'] = value
        
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
        image = image[:,:,0]
        if image.size == 1:
            #There are problems with some greyscale png images
            logger.error('Invalid image: %s provided: is it grayscale png?',fname)
            raise TypeError,"Invalid image type"       
    
        self.setOriginal(image)
        
    def getMaximaImage(self):
        """returns an RGBA type array suitable for overlay"""
        r = self.params['display_cone_size'] + 1 #use this value for now....
        #generate a circle mask
        [y,x] = np.ogrid[-r:r,-r:r]
        mask = x*x + y*y <= r
        
        newImg = np.zeros(self.params['seeds'].shape + (4,),dtype=np.uint8)   #create a new array of size orgImage but 4D
        newImg[:,:,1] = self.params['seeds'] > 0
        newImg[:,:,1] = mh.dilate(newImg[:,:,1],mask) * 255
        newImg[:,:,3][newImg[:,:,1]>0] = 1

        return np.float64(newImg)
    
    def _filterMaxima(self):
        #replace seeds that are larger than one pixel with the center of mass
        frequencies = stats.itemfreq(self.params['seeds'])
        frequencies = frequencies[frequencies[:,0]>0,:] #remove the 0 values
        frequencies = frequencies[frequencies[:,1]>1,:] #isolate only values with counts >1
        for lab in frequencies[:,0]:
            coords = np.argwhere(self.params['seeds']==lab)
            self.params['seeds'][self.params['seeds']==lab] = 0 #remove the current label
            [y,x] = np.apply_along_axis(np.mean,0,coords)
            self.params['seeds'][y,x]=lab
            
    def filterPointsByDistance(self):
        #TODO
        pass
    
if __name__ == '__main__':
    logger = logging.getLogger(__name__)
    formatter = logging.Formatter('%(levelname)s - %(message)s')
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)    
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
