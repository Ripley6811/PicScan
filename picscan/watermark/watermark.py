#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Resizes images to 2048px and add watermark.

This program can process multiple files. Reads EXIF information and adds a
watermark that include a image and some details from EXIF.
I use this for my own images and it is not documented by you can adapt for your
own use.

:REQUIRES: image_utils.py in the PicScan package along with exiftool.exe
:PRECONDITION: ...
:POSTCONDITION: ...

:AUTHOR: Ripley6811
:ORGANIZATION: National Cheng Kung University, Department of Earth Sciences
:CONTACT: python@boun.cr
:SINCE: Wed Mar 27 23:17:58 2013
:VERSION: 0.1
:STATUS: Nascent
:TODO: ...
"""
#===============================================================================
# PROGRAM METADATA
#===============================================================================
__author__ = 'Ripley6811'
__contact__ = 'python@boun.cr'
__copyright__ = ''
__license__ = ''
__date__ = 'Wed Mar 27 23:17:58 2013'
__version__ = '0.1'

#===============================================================================
# IMPORT STATEMENTS
#===============================================================================
from numpy import linspace
import subprocess
from PIL import Image, ImageDraw, ImageChops, ImageFont
import sys
sys.path.append(r'C:\Dropbox\GitHub\PicScan\picscan')
from image_utils import DisplayImage
import os
os.chdir(r'C:\Dropbox\GitHub\PicScan\picscan')
import tkFileDialog
from os import rename, path, mkdir, listdir #, remove

#===============================================================================
# METHODS
#===============================================================================



def add_watermark1(filename, mark=None):
    im = DisplayImage(filename)
    #im.im.save(r'C:\Users\tutu\Desktop\tester.jpg')
    #image.show()
    image = im.im.convert("RGBA")
    print image
    image.thumbnail((2048,2048))
    print image
    print im.exif

    mark = r'C:\Users\tutu\Desktop\jwj.png'


    watername = ImageChops.invert( Image.open(mark))
    alpha = watername.convert("L")
    watername.putalpha(alpha)

    print watername
    width_offset = 10
    font = ImageFont.truetype("verdana.ttf", 20)
    font = ImageFont.truetype("impact.ttf", 20)
    lens = im.exif.get('Lens ID')
    if not lens:
        lens = im.exif.get('Lens')
    print lens
#    width,height = font.getsize(im.exif['Lens ID'])
    width,height = font.getsize( lens )
    width = max((240,width+2*width_offset))
    # Bar
    waterback = Image.new("RGBA", (width,120), (80,30,30,80))
    # Gradient
    waterback = Image.new("RGBA", (width,120), (40,20,20,120))

    waterback.paste(watername, (width_offset,10), watername)
    draw = ImageDraw.Draw(waterback)
    draw.text((130,5), "f/"+im.exif['Aperture'], font=font)
    draw.text((130,25), im.exif['Shutter Speed'] + ' sec', font=font)
    draw.text((130,45), "ISO "+im.exif['ISO'], font=font)
    draw.text((130,65), im.exif['Focal Length'].split('(')[0], font=font)
    draw.text((width_offset,90), lens, font=font)

    image.paste(waterback, (20, image.size[1]-120), waterback)
    #image.paste(watername, (0,0), watername)
#    image.show()

    savename = filename[:-4]+'_jwj.jpg'
    image.save( savename )
    subprocess.call(['exiftool.exe',
                     savename,
                     '-tagsFromFile',
                     filename], shell=True)


def add_watermark2(filename, mark=None):
    '''Gradient/fading grey background with white text in lower left corner.'''

    im = DisplayImage(filename)
    #im.im.save(r'C:\Users\tutu\Desktop\tester.jpg')
    #image.show()
    image = im.im.convert("RGBA")
#    print image
    image.thumbnail((2048,2048))
#    print image
#    print im.exif

    mark = r'C:\Users\tutu\Desktop\jwj.png'


    watername = ImageChops.invert( Image.open(mark))
    alpha = watername.convert("L")
    watername.putalpha(alpha)

    width_offset = 75
    font = ImageFont.truetype("verdana.ttf", 20)
    font = ImageFont.truetype("candara.ttf", 22)
    d7000font = ImageFont.truetype("impact.ttf", 18)
    lens = im.exif.get('Lens ID')
    if not lens:
        lens = im.exif.get('Lens')

    # Mapping to desired lens name for my lenses
    lens_name_correction = {
        'Unknown (26 40 5C 82 2B 34 1C 02)': 'Sigma 70-210mm f/3.5-4.5 D',
        'AF Nikkor 50mm f/1.8D': 'AF Nikkor 50mm f/1.8 D',
        '50mm f/1.8 D': 'AF Nikkor 50mm f/1.8 D',
        'AF-S DX VR Zoom-Nikkor 18-105mm f/3.5-5.6G ED': 'AF-S Nikkor 18-105mm f/3.5-5.6G ED',
        }
    if lens in lens_name_correction:
        lens = lens_name_correction[lens]

    print 'Lens ID:', im.exif.get('Lens ID')
    print 'Lens:', im.exif.get('Lens')
    print 'Writing:', lens
#    width,height = font.getsize(im.exif['Lens ID'])
    exposure_string = ( "f/"+ str(im.exif.get('Aperture')) + '   '
                    + str(im.exif.get('Shutter Speed')) + 's   '
                    + 'ISO '+ str(im.exif.get('ISO'))
#                    + '   ' + str(im.exif.get('Focal Length')).split('(')[0]
                    )
    width,height = font.getsize( exposure_string )
    try:
        lenswidth, height = font.getsize( lens )
    except:
        lenswidth = 1
    width = max([240, 120+width+2*width_offset, 120-19+lenswidth+2*width_offset])
    # Bar
    waterback = Image.new("RGBA", (width,120), (80,30,30,80))
    # Gradient
    r,g,b = 40,20,20
    height = 100
    waterback = Image.new("RGBA", (width,height), (40,20,20,120))
    waterback_alpha = Image.new("L", (1, height), 0)
    waterback_alpha.putdata( list(linspace(1,256,100).astype(int)) )
    waterback_alpha = waterback_alpha.resize( (width, height) )
    fade_w = 100.
    for i in range(int(fade_w)):
        for j in range(height):
            a = waterback_alpha.getpixel((i,j))
            waterback_alpha.putpixel((i,j), int(a*(i/fade_w)) )
            a = waterback_alpha.getpixel((width-1-i,j))
            waterback_alpha.putpixel((width-1-i,j), int(a*(i/fade_w)) )
    waterback.putalpha(waterback_alpha)

    if 'jay' in str(im.exif.get('Artist')).lower():
        waterback.paste(watername, (width_offset,14), watername)
    draw = ImageDraw.Draw(waterback)
    if 'D7000' in im.exif.get('Camera Model Name'):
        draw.text((width_offset+53,49), "&", font=d7000font)
        draw.text((width_offset+34,69), "D7000", font=d7000font)
    draw.text((width_offset+120,74), exposure_string, font=font)



    # Write name of lens on image
    try:
        draw.text((width_offset+120-19,48), lens, font=font)
    except:
        pass

    # Write focal length on image
    try:
#        draw.text((width_offset+120-19,22), im.exif.get('Artist'), font=font)
#        draw.text((width_offset+120-19,22), str(im.exif.get('Focal Length')).split('(')[0], font=font)
    except:
        pass

    image.paste(waterback, (-50, image.size[1]-100), waterback)
    #image.paste(watername, (0,0), watername)
#    image.show()

    savename = filename[:-4]+'_jwj2b.jpg'
    image.save( savename )
    subprocess.call(['exiftool.exe',
                     savename,
                     '-tagsFromFile',
                     filename], shell=True)



def add_watermark3(filename, mark=None):
    '''Simple Centered watermark.'''
    im = DisplayImage(filename)
    #im.im.save(r'C:\Users\tutu\Desktop\tester.jpg')
    #image.show()
    image = im.im.convert("RGBA")
    print image
    image.thumbnail((2048,2048))
    print image
    print im.exif

    mark = r'C:\Users\tutu\Desktop\jwj.png'


    watername = ImageChops.invert( Image.open(mark))
    alpha = watername.convert("L")
    watername.putalpha(alpha)

    print watername
    width_offset = 10
    font = ImageFont.truetype("verdana.ttf", 20)
    font = ImageFont.truetype("candara.ttf", 22)
    d7000font = ImageFont.truetype("impact.ttf", 18)
    lens = im.exif.get('Lens ID')
    if not lens:
        lens = im.exif.get('Lens')
    print lens
#    width,height = font.getsize(im.exif['Lens ID'])
    exposure_string = ( "f/"+ str(im.exif.get('Aperture')) + '   '
                    + str(im.exif.get('Shutter Speed')) + 's   '
                    + 'ISO '+ str(im.exif.get('ISO')) + '   '
                    + str(im.exif.get('Focal Length')).split('(')[0] )
    width,height = font.getsize( exposure_string )
    try:
        lenswidth, height = font.getsize( lens )
    except:
        lenswidth = 1
    width = im.size[0]
    # Bar
    waterback = Image.new("RGBA", (width,120), (80,30,30,80))
    # Gradient
    r,g,b = 40,20,20
    height = 100
    waterback = Image.new("RGBA", (width,height), (40,20,20,120))
    waterback_alpha = Image.new("L", (width,1), 0)
    waterback_alpha.putdata( list(linspace(0,256,width/2).astype(int))
                            + list(linspace(256,0,width/2).astype(int)) )
    waterback_alpha = waterback_alpha.resize( (width, height) )
    waterback.putalpha(waterback_alpha)

    if 'jay' in str(im.exif.get('Artist')).lower():
        waterback.paste(watername, (width_offset,14), watername)
    draw = ImageDraw.Draw(waterback)
    if 'D7000' in im.exif.get('Camera Model Name'):
        draw.text((63,49), "&", font=d7000font)
        draw.text((44,69), "D7000", font=d7000font)
    draw.text((130-19,48), exposure_string, font=font)

#    draw.text((130,45), , font=font)
    try:
        draw.text((130,74), lens, font=font)
    except:
        pass

    image.paste(waterback, (0, image.size[1]-100), waterback)
    #image.paste(watername, (0,0), watername)
    image.show()

#    savename = filename[:-4]+'_jwj2.jpg'
#    image.save( savename )
#    subprocess.call(['exiftool.exe',
#                     savename,
#                     '-tagsFromFile',
#                     filename], shell=True)

#===============================================================================
# MAIN METHOD AND TESTING AREA
#===============================================================================
def main():
    """Description of main()"""

    filename = tkFileDialog.askopenfilename(multiple=True, initialdir=r'C:\Dropbox\Camera Uploads\testing')
#    work_dir, selected_file = path.split(filename)
    print filename
    filename = filename.strip('{}').split('} {')

#    filename = r'C:\Dropbox\Camera Uploads\testing\2013-03-27 17.47.13.jpg'
#    filename = r'C:\Dropbox\Camera Uploads\testing\2013-03-27 13.39.35.jpg'
#    #filename = r'C:\SkyDrive\Photo Archive\2013 02 (Feb)\2013-02-08 19.34.39-2.jpg'
#    name = r'C:\Users\tutu\Desktop\jwj.png'

#    for each in listdir(work_dir):
#        add_watermark1(path.join(work_dir,each))

    if isinstance(filename, list):
        for f in filename:
            add_watermark2(f)
    else:
        add_watermark2(filename)

if __name__ == '__main__':
    main()