import logging
import numpy as np
import mahotas as mh
import os
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
              'curImage':None}
    
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
        self.params['regional_maxima'] = mh.regmax(curImage)
        self.params['seeds'],self.params['npoints'] = mh.label(self.params['regional_maxima'])        
    
    def getVeroniImage(self):
        if self.params['seeds'] is None:
            logger.error('Regional maxima must be discovered first')
            raise RuntimeError,"Regional maxima must be discovered first"
        return mh.segmentation.gvoronoi(self.params['seeds'])
    
    
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
        newImg = np.zeros(self.params['regional_maxima'].shape + (4,))   #create a new array of size orgImage but 4D
        newImg[:,:,1] = self.params['regional_maxima'] * 255
        newImg[:,:,3][self.params['regional_maxima']] = 1

        return newImg
    
    
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
