#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Display image management class.

Handles all image manipulation using PIL.
This class stores a full-size image and display position. It allows extraction
of a thumbnail of any size, converting points from display location to image
location. (Tried OpenCV, but images displayed faster in Tkinter with PIL.)


:REQUIRES: exiftool.exe 'http://www.sno.phy.queensu.ca/~phil/exiftool/'
:PRECONDITION: ...
:POSTCONDITION: ...

:AUTHOR: Ripley6811
:ORGANIZATION: National Cheng Kung University, Department of Earth Sciences
:CONTACT: python@boun.cr
:SINCE: Thu Jan 31 19:51:08 2013
:VERSION: 0.2
:STATUS: Nascent
:TODO: Make exiftool.exe optional. If unavailable then revert to PIL methods.
"""
#===============================================================================
# PROGRAM METADATA
#===============================================================================
__author__ = 'Ripley6811'
__contact__ = 'python@boun.cr'
__copyright__ = ''
__license__ = ''
__date__ = 'Thu Jan 31 19:51:08 2013'
__version__ = '0.2'

#===============================================================================
# IMPORT STATEMENTS
#===============================================================================
from os import remove
from PIL import Image, ImageDraw, ImageTk, ExifTags, ImageFilter
#from numpy import *  # IMPORTS ndarray(), arange(), zeros(), ones()
from collections import OrderedDict
import cv2
import subprocess
from StringIO import StringIO


#===============================================================================
# DISPLAY_IMAGE CLASS
#===============================================================================
class DisplayImage:
    '''Structure for holding an image and info on how it is displayed on screen.
    '''
    def __init__(self, im_filename, ID=0, anchor=(0,0), scale=1.0, fit=(0,0)):
        '''Accepts PIL image. 'fit' overrides 'scale' if given as a parameter.
        '''
        self.ID = ID
        self.filename = im_filename


        if self.filename.endswith('nef'):
            self.im = get_exiftool_jpeg( im_filename )
        elif self.filename.endswith('jpg'):
            self.im = Image.open( im_filename )
#        else:
#            self.filename = im_filename + '.jpg'
#            self.im = Image.open( self.filename )

        self.scale = scale
        self.fit = fit # SET THE RETURN SCALING BY THE AREA IT MUST FIT INSIDE
        self.anchor = anchor # WHERE TOPLEFT OF IMAGE WILL BE PLACED IN DISPLAY AREA

        self.fit_scale() # OVERRIDES SCALE PARAMETER IF FIT IS SET

        self.thumbnail = None

        self.exif = OrderedDict()



        #TODO: Use exiftool.exe if available otherwise use the simpler PIL tool
        self.get_exiftool_exif()

        if self.exif['Orientation'] == 'Rotate 270 CW':
            self.im = self.im.rotate(90)
        if self.exif['Orientation'] == 'Rotate 90 CW':
            self.im = self.im.rotate(270)
        self.size = self.im.size
        self.cropbox = (0, 0, self.size[0], self.size[1])
        self.focus = (self.size[0]/2,self.size[1]/2)



    def set_box(self, box):
        '''Set the display region of image.

        Arg is a 4-tuple defining the left, upper, right, and lower pixel
        coordinate. Same as in the crop method of PIL Image class.
        '''
        newbox = list(box)
        print box
        boxW = box[2] - box[0]
        boxH = box[3] - box[1]
        if box[0] < 0:
            newbox[0] -= box[0]
            newbox[2] -= box[0]
        if box[1] < 0:
            newbox[1] -= box[1]
            newbox[3] -= box[1]
        if box[2] > self.size[0] - boxW:
            newbox[0] -= box[2] - self.size[0] - boxW
            newbox[2] -= box[2] - self.size[0] - boxW
        if box[3] > self.size[1] - boxH:
            newbox[1] -= box[3] - self.size[1] - boxH
            newbox[3] -= box[3] - self.size[1] - boxH

        self.cropbox = newbox
        self.fit_scale()

    def set_box_center(self, coord):
        im_coord = self.point( coord )
        boxW = self.cropbox[2]-self.cropbox[0]
        boxH = self.cropbox[3]-self.cropbox[1]
        self.cropbox = (im_coord[0]-boxW/2,
                        im_coord[1]-boxH/2,
                        im_coord[0]+boxW/2,
                        im_coord[1]+boxH/2,)



    def move_box(self, dx, dy):
        a,b,c,d = self.cropbox
        self.cropbox = (a+dx,b+dy,c+dx,d+dy)



    def set_fit(self, dxdy, zoom=False):
        '''Set desired size in pixels of final return image.

        :PARAMETERS:
            *dxdy* --- A tuple giving the desired width and height.

        '''
        assert dxdy[0] > 0 and dxdy[1] > 0
        self.fit = tuple(dxdy)
        if zoom:
            self.fit = 10000,dxdy[1]
        self.fit_scale()



    def fit_scale(self):
        if self.fit[0] > 0 and self.fit[1] > 0:
            cropsize = (self.cropbox[2] - self.cropbox[0], self.cropbox[3] - self.cropbox[1])
            self.scale = min(self.fit[0] / float(cropsize[0]), self.fit[1] / float(cropsize[1]))


    def set_thumbnail(self, tsize, zoom=False):
        self.thumbnail = self.im.copy()
        if zoom:
            scale = max(tsize[0]/float(self.size[0]),tsize[1]/float(self.size[1]))
            self.thumbnail = self.im.resize( tuple( int(x * scale) for x in self.size) )
            yoffset = (self.thumbnail.size[0] - tsize[0]) / 2
            xoffset = (self.thumbnail.size[1] - tsize[1]) / 2
            self.thumbnail = self.thumbnail.crop( (yoffset,
                                                   xoffset,
                                                   self.thumbnail.size[0]-yoffset,
                                                   self.thumbnail.size[1]-xoffset ) )
            self.thumbnail = ImageTk.PhotoImage( self.thumbnail )
        else:
            scale = min(tsize[0]/float(self.size[0]),tsize[1]/float(self.size[1]))

            self.thumbnail = self.im.resize( tuple( int(x * scale) for x in self.size) )
            self.anchor = ((tsize[0]-self.thumbnail.size[0])/2, 0)
            self.thumbnail = ImageTk.PhotoImage( self.thumbnail )
        self.scale = scale


    def get_exif(self):
        tags = ['File Name', 'Directory', 'File Size', 'Image Size',
                'File Creation Date/Time', 'Date/Time Original',
             'Make', 'Camera Model Name',
             'Artist', 'Copyright', 'User Comment',
             'Aperture',
             'Shutter Speed',
             'ISO',
             'Focal Length',
             'Lens ID',
#             'Date/Time Original', 'Create Date',
#             'Image Width', 'Image Height',
             'Orientation',
             'Exposure Compensation','Exposure Program',
             'Flash',
             'White Balance', 'Focus Mode',
             'Exposure Difference', 'Exposure Tuning',
             'Active D-Lighting',
             'Lens',
             'Focus Distance',
             'Shutter Count',
             'AF Fine Tune Adj',
             'Color Space',
             'Exposure Mode', 'Contrast', 'Saturation',
             'Sharpness','Auto Focus',
             'Depth Of Field', 'Field Of View',
#             'Keywords',
             ]

        ex = self.exif
#        print ex.keys()
#        print ex['Orientation']

        exifsubset = OrderedDict()

        for tag in tags:
            exifsubset[tag] = self.exif.get(tag)

#        make = ex.get('Make')
#        model = ex.get('Model')
#
#        if ex.get('Model'): exifsubset['Model'] = ex.get('Model')
#        extime = ex.get('ExposureTime')
#        if extime:
#            exifsubset.append( 'Speed: ' + '{:.4f}'.format( extime[0]/float(extime[1])) + ' (1/'+str(extime[1]/extime[0]) + ')' )
#        aperture = ex.get('FNumber')
#        if aperture:
#            exifsubset.append( 'Aperture: f/' + str( aperture[0]/float(aperture[1]) ) )
#        iso = ex.get('ISOSpeedRatings')
#        if iso:
#            exifsubset.append( 'ISO speed: ' + str( iso ) )
#        flen = ex.get('FocalLength')
#        if flen:
#            exifsubset.append( 'FocalLength: ' + str( flen[0]/float(flen[1]))  + 'mm' )
#        if ex.get('Flash'):
#            exifsubset


#        print self.exif
#        print type(self.exif)
#        if self.exif.get('MakerNote'):
#            print repr(self.exif.get('MakerNote'))

        return exifsubset


    def get_exiftool_exif(self):
        exifdata = subprocess.check_output(['exiftool.exe',
                                 self.filename], shell=True)
        exifdata = exifdata.splitlines()
        for i, each in enumerate(exifdata):
            tag,val = each.split(': ', 1)
            self.exif[tag.strip()] = val.strip()



    def get_exiftool_thumbnail(self):
        try:
            im_binary = subprocess.check_output(['exiftool.exe',
                                                  self.filename,
                                                  '-thumbnailimage',
                                                  '-b'], shell=True)
            image = Image.open( StringIO(im_binary) )
            return image
        except:
            return None



    def get_exiftool_preview(self):
        try:
            im_binary = subprocess.check_output(['exiftool.exe',
                                                  self.filename,
                                                  '-previewimage',
                                                  '-b'], shell=True)
            image = Image.open( StringIO(im_binary) )
            return image
        except:
            return None



    def get_histogram(self, size=(256,50)):
        '''Returns a list of lists.'''
        hdat = self.im.histogram()
        scale = max( (max(hdat[20:230]) / 256, 1) )
        him = Image.new("RGB", (256,1))
        rgb_tuplist = [(min((255,hdat[i] / scale)),
                        min((255,hdat[i+256] / scale)),
                        min((255,hdat[i+512] / scale)))
                        for i in range(256)]

        him.putdata(rgb_tuplist, 1, 0)
        him = him.resize(size)
#        him.show()
        self.him = ImageTk.PhotoImage( him )

        return self.him


    def point(self, xy):
        '''Translates the point on display window to pixel coordinate of whole
        image. Returns False if point is not within image.

        This method can be used to test if a clicked point was on this image.
        Can use this method to retrieve the image coordinate of a clicked point.
        '''
        axy = self.anchor
        cxy = (int((xy[0]-axy[0]) / self.scale), int((xy[1]-axy[1]) / self.scale))

#        boxspan = self.box_span()
#        for i in xrange(2):
#            if xy[i] < self.anchor[i] or xy[i] > axy[i] + boxspan[i]:
#                return False
#        # SUBTRACT ANCHOR COORD, REVERSE SCALING, AND ADD CROPPED DISTANCE BACK
#        retval = ((xy[0] - axy[0] + cxy[0])/self.scale,
#                  (xy[1] - axy[1] + cxy[1])/self.scale )
        xmax,ymax = self.size
        if cxy[0] < xmax and cxy[1] < ymax:
            return cxy
        else:
            return False



    def box_span(self):
        return (int((self.cropbox[2] - self.cropbox[0])*self.scale),
                int((self.cropbox[3] - self.cropbox[1])*self.scale))



    def image(self, Tk=True, sobel=False):
        '''Retrieve a copy of the cropped and resized portion of this image.

        Default is to return a Tkinter compatible image.

        @kwarg Tk: True for Tkinter image, False for PIL
        '''
#        self.imcopy = self.im.copy()
#        if self.scale != 1.0:
#            self.imcopy = cv2.resize(self.im, (0,0), fx=self.scale, fy=self.scale)
#        x0,y0,x1,y1 = self.cropbox
#        dx = (x1-x0)/2
#        dy = (y1-y0)/2
#        fx, fy = self.focus
#        print 'crop', fy-dy,fy+dy,fx-dx,fx+dx
#        self.imcopy = self.imcopy[fy-dy:fy+dy,fx-dx:fx+dx]
#        self.imcopy.thumbnail(tuple([int(each * self.scale) for each in self.size]))
#        if sobel:
##            self.imcopy = self.imcopy.filter(ImageFilter.FIND_EDGES)
#            self.imcopy = cv2.Sobel(self.imcopy, ddepth=-1, dx=1, dy=1, ksize=5)
        if Tk == True:
            self.imcopy = ImageTk.PhotoImage(self.im.crop(self.cropbox) )
        return self.imcopy



    def image_full(self, pt=None, radius=100, Tk=True):
        if pt:
            self.imcopy = self.im.crop( (pt[0]-radius, pt[1]-radius, pt[0]+radius, pt[1]+radius) )
        else:
            self.imcopy = self.im.copy()
#        print 'pt', pt, radius
#        print 'size', self.imcopy.size
        if Tk == True:
            self.imcopy = ImageTk.PhotoImage( self.imcopy )
        return self.imcopy


    def make_jpg(self):
        savename = self.filename[:-4]+'.jpg'
#        if self.exif['Orientation'] == 'Rotate 270 CW':
#            self.im.rotate(270).save( savename, quality=99 )
#        elif self.exif['Orientation'] == 'Rotate 90 CW':
#            self.im.rotate(90).save( savename, quality=99 )
#        else:
        self.im.save( savename, quality=99 )
        subprocess.call(['exiftool.exe',
                         savename,
                         '-tagsFromFile',
                         self.filename], shell=True)
        subprocess.call(['exiftool.exe',
                         savename,
                         '-Orientation=Horizontal (normal)'], shell=True)
        remove(savename + '_original')



    def to_disp_pt(self, pt):
        '''Scale down and offset image points for display.

        Image point -> Disp point.
        '''
        axy = self.anchor
        cxy = (self.cropbox[0], self.cropbox[1])
        return (pt[0]*self.scale - cxy[0]*self.scale + axy[0],
                pt[1]*self.scale - cxy[1]*self.scale + axy[1])


def get_exiftool_jpeg(filename):
    try:
        im_binary = subprocess.check_output(['exiftool.exe',
                                              filename,
                                              '-JpgFromRaw',
                                              '-b'], shell=True)
        image = Image.open( StringIO(im_binary) )
        return image
    except:
        return None