import logging
import numpy as np
import mahotas as mh
import os
logger = logging.getLogger(__name__)
class AOImage():
    """AO Image data
    Going to define this as a seperate class to hold all the image processing functions
    """
    orgImage = None

    #Define a dictionary to hold the transform parameters
    params = {'threshold':None,
              'filter':None,
              'regional_maxima':None}
    
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
        
        curImage = self.orgImage
        
        if self.params['filter'] > 0:
            curImage = self.filterImage(curImage,self.params['filter'])
        
        self.params['threshold'] = self.thresholdImage(curImage)
        self.params['regional_maxima'] = mh.regmax(curImage)
        return curImage
    
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

if __name__ == '__main__':
    logger = logging.getLogger(__name__)
    formatter = logging.Formatter('%(levelname)s - %(message)s')
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)    
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
