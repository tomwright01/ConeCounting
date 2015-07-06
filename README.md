# ConeCounting
A wxpython app for automatic cone counting of AO-SLO images

Requires the mahotas image processing library http://mahotas.rtfd.org/

Usage: python ConeCounts.py

Can be used to process a single image file (File>Open File) or bulk process a directory of images `File > Open Dir`.
If bulk processing is selected all image files in the selected directory will be processed. Images are presented in a random order. Progress can be saved `File>Save Progress` and loaded `File> Load Progress`.

The filter parameter is the inital radius of a gaussian filter (in pixels). The Minimum cone size parameter removes cones that are closer than n pixels together.
By default all cones in an image are counted (this can be slow). A sub-region of the image can be selected using the 'zoom' toolbar button. Coordinates of the zoomed region are saved and the cone count in that region displayed.
