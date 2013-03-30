#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Sorting program for JPG+NEF image pairs.

Main program and GUI for PicScan program. The program creates a "save" folder
and a "trash" folder within the folder of images. Use WASD to sort images into
these folders. A "NEF_backup" folder is created within the "save" folder.

Controls:
    Mousewheel, left key, right key = Goto prev or next image in folder.
    Mousewheel down and scroll = Change size of full-size "zoom" window.
    Mouse left button + move = "Zoom" window appears when clicking on image.
    Mouse right button = Same as left button, but window dissappears when
        button is released.
    Spacebar, mouse right click = Removes the "zoom" window.
    w = Move NEF to save folder and put a copy to backup folder. (w=keep NEF only)
    a = Move JPG to save folder and move NEF to backup folder. (a=keep all)
    s = Move JPG to save folder and move NEF to trash folder. (s=keep JPG only)
    d = Move JPG and NEF to trash folder. (d=delete both)
    e = Undo last move


:REQUIRES: PIL
:PRECONDITION: ...
:POSTCONDITION: ...

:AUTHOR: Ripley6811
:ORGANIZATION: National Cheng Kung University, Department of Earth Sciences
:CONTACT: python@boun.cr
:SINCE: Sun Jan 20 11:12:17 2013
:VERSION: 0.1
:STATUS: Nascent

:TODO: Add Sphinx documentation to methods
:TODO: Preload images and show thumbnails at bottom, allow turning off and on.
:TODO: Detect and show how many similar images are in folder
:TODO: Option to create 'save' folder or use current folder.
:TODO: Option to show contents of both working and save folders.
:TODO: Clear last image when there are none left in folder. Prompt for new folder maybe.
:TODO: Make black square with data semi-transparent.
:TODO: Show more metadata like file size, pixel size
:TODO: Mark photos whether a 'decision' has been made. Be able to toggle just showing ones that haven't.
:TODO: Add NEF viewing or place holder thumbnail.
"""

from pylab import *  # IMPORTS NumPy.*, SciPy.*, and matplotlib.*
import os  # os.walk(basedir) FOR GETTING DIR STRUCTURE
#from Tkinter import *
import Tkinter
#import tkFileDialog # askopenfilename, asksaveasfilename, askdirectory
from tkSimpleDialog import askstring
from PIL import Image, ImageTk, ImageDraw
#import thread
#import time
#from collections import namedtuple
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg

import pickle
from image_utils import DisplayImage
from fmanager import FileManager



class PicScan_GUI(Tkinter.Tk):

    # Make translucent background for EXIF data
    layer = []
    boxwidth = 360
    boxheight = 1000
    for i in range(boxheight):
        layer += [255-i/4]*boxwidth

    alpha = Image.new("L", (boxwidth,boxheight))
    alpha.putdata( layer, 1, 0 )
    exif_bg = Image.new("RGBA", (boxwidth,boxheight), (70,70,70,0))
    exif_bg.putalpha(alpha)





    def load_settings(self, run_location ):
        try:
            with open( run_location + '\settings.ini', 'r' ) as rfile:
                self.dat = pickle.load(rfile)
            rfile.close()
            print 'Settings loaded'

        except IOError: # If file does not exist
            self.dat = dict( # DEFAULT SETTINGS
                                dir_work=os.getcwd(),
                                jpg_dir = u'C:/',
                                nef_dir = u'C:/',
                                number_of_tiles = 1,
                                mode=0,
                                geometry='1900x1000+0+0',
                                maxWidth = 1900,
                                maxHeight = 1000,
                                tileborder = 1,
                                main_zoom = 0,
                                selectedImage = [0],
                                focalPixel = (0.5,0.5),
                                sobel = False,
                                scale = 1.0,
                                histogram = True,
                                )
            with open( run_location + '\settings.ini', 'w' ) as wfile:
                pickle.dump(self.dat, wfile)
            wfile.close()
            print 'Restored default settings'


    def __init__(self, parent):
        Tkinter.Tk.__init__(self, parent)
        self.parent = parent

        self.initialize()

    def initialize(self):
        self.run_location = os.getcwd()
        self.load_settings( os.getcwd() )
        self.b1press = None
        self.subwinsize = 150

        try:
            os.chdir( self.dat['dir_work'] )
        except WindowsError:
            self.set_work_dir()


        # CREATE THE MENU BAR
        self.create_menu()
        self.create_top_controls()

        # LEFT HAND SIDE CONTROLS
#        self.create_left_controls()

        # MAIN SCREEN CANVAS BINDINGS
        self.create_image_canvas()
        self.exif_bg = ImageTk.PhotoImage(self.exif_bg)

        # WINDOW PLACEMENT ON SCREEN
        try:
            self.geometry( self.dat['geometry'] ) # INITIAL POSITION OF TK WINDOW
        except KeyError:
            self.geometry( self.default_settings['geometry'] ) # INITIAL POSITION OF TK WINDOW

        self.update()
        self.canvas.bind('<Configure>', self.resize )

        # FINISHED GUI SETUP
        self.load_image()

        self.print_settings( 'Settings on initialization' )



    def create_menu(self):
        # MAIN MENU BAR
        menubar = Tkinter.Menu(self)

        # FILE MENU OPTIONS: LOAD, SAVE, EXIT...
        filemenu = Tkinter.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Load image", command=self.load_image)
        filemenu.add_separator()

        ALIGN_MODES = [
                "Align by pixel position",
                "Align by matching"
                ]

        self.rb = Tkinter.StringVar()
        self.rb.set(ALIGN_MODES[1]) # initialize

        for mode in ALIGN_MODES:
            filemenu.add_radiobutton(label=mode, variable=self.rb, value=mode,
                                     command=self.change_click_mode)


        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.endsession)
        menubar.add_cascade(label="File", menu=filemenu)

        # HDR MENU OPTIONS
        hdrmenu = Tkinter.Menu(menubar, tearoff=0)
        #TODO: Add HDR options
        menubar.add_cascade(label="HDR", menu=hdrmenu)

        # SFM MENU OPTIONS
        sfmmenu = Tkinter.Menu(menubar, tearoff=0)
        #TODO: Add SFM options
        menubar.add_cascade(label="SFM", menu=sfmmenu)

        # HELP MENU OPTIONS: OPEN LADYBUG API HELP, OPEN WORKING DIRECTORY
        helpmenu = Tkinter.Menu(menubar, tearoff=0)
        helpmenu.add_command(label="About", command=hello)
        helpmenu.add_cascade(label="Open Working Directory", command=self.openWorkingDir)
        menubar.add_cascade(label="Help", menu=helpmenu)

        # SET AND SHOW MENU
        self.config(menu=menubar)


    def create_top_controls(self):
        '''Show the location of the working jpg and nef directories.

        Two text buttons that show and change the working directories.
        Program will search for NEF in both locations.
        One button for auto-move NEFs from JPG folder to NEF folder if found.
        or just put option in menu bar and set default for 'on'.
        '''

        address_bar = Tkinter.Frame(self)
        address_bar_jpg_line = Tkinter.Frame(address_bar)
        address_bar_nef_line = Tkinter.Frame(address_bar)

        self.jpg_dir = Tkinter.StringVar()
        self.jpg_dir.set(self.dat.get('jpg_dir') )
        self.nef_dir = Tkinter.StringVar()
        self.nef_dir.set(self.dat.get('nef_dir') )

        Tkinter.Label(address_bar_jpg_line, text='JPG Dir').pack(side=Tkinter.LEFT,padx=0,pady=0)
        jpg_dir = Tkinter.Button(address_bar_jpg_line,
                                 textvariable=self.jpg_dir,
                                 command=self.set_new_jpg_dir)
        jpg_dir.pack(side=Tkinter.LEFT,padx=0,pady=0, fill='x')

        Tkinter.Label(address_bar_nef_line, text='NEF Dir').pack(side=Tkinter.LEFT,padx=0,pady=0)
        nef_dir = Tkinter.Button(address_bar_nef_line,
                                 textvariable=self.nef_dir,
                                 command=self.set_new_nef_dir)
        nef_dir.pack(side=Tkinter.LEFT,padx=0,pady=0)

        address_bar_jpg_line.pack(side=Tkinter.LEFT)
        address_bar_nef_line.pack(side=Tkinter.LEFT)
        Tkinter.Label(address_bar, text='A:Save All, S:Save JPG, W:Save NEF, D:Delete Both').pack(side=Tkinter.LEFT,padx=0,pady=0)
        address_bar.pack(side=Tkinter.TOP)




    def create_image_canvas(self):
        self.canvas = Tkinter.Canvas(self, width=self.dat['maxWidth'], height=self.dat['maxHeight'], bg='black')
        self.canvas.bind("<ButtonPress-1>", self.click_pt) # DETERMINE NEW POINT OR GRAB EXISTING
        self.canvas.bind("<ButtonPress-3>", self.click_pt) # DETERMINE NEW POINT OR GRAB EXISTING
#        self.canvas.bind("<ButtonRelease-1>", self.endMotion) # FINALIZE BUTTON ACTION
        self.canvas.bind("<ButtonRelease-3>", self.kill_zoom)
        self.bind("<space>", self.kill_zoom)
        self.canvas.bind("<B1-Motion>", self.shiftImage)
        self.canvas.bind("<B3-Motion>", self.shiftImage)
        self.bind("<Key>", self.keypress)
        self.bind("<Delete>", self.deletekey)
        self.bind("<Escape>", self.endsession)
        self.bind("<Left>", self.change_image)
        self.bind("<Right>", self.change_image)

        self.canvas.bind_all("<MouseWheel>", self.change_image)
        self.bind_all("<Up>", self.change_image)
        self.bind_all("<Down>", self.change_image)

        self.canvas.pack(side=Tkinter.RIGHT, expand=Tkinter.YES, fill=Tkinter.BOTH)


#        self.f = plt.Figure(figsize=(5.0,1.0), dpi=100, facecolor='w', edgecolor='w')
#        self.dataPlot = FigureCanvasTkAgg(self.f, master=self.canvas)
#        self.dataPlot.get_tk_widget().pack(side=Tkinter.BOTTOM)




    def load_image(self, curr_dir=''):
        """Load the images from the list of filenames.

        """
        use_saved_folder = False
        try:
            self.fman = FileManager(self.fman.work_dir, use_saved_folder=use_saved_folder)
        except:
            self.fman = FileManager(use_saved_folder=use_saved_folder)

        self.disp_image = DisplayImage( self.fman.load() )

        self.show_image()




    def set_new_jpg_dir(self):
        self.fman = FileManager()
        self.jpg_dir.set(self.fman.jpg_dir)
        self.dat['jpg_dir'] = self.fman.jpg_dir



    def set_new_nef_dir(self):
        new_dir = self.fman.newNEFdir( self.nef_dir.get() )

        self.nef_dir.set( new_dir )
        self.dat['nef_dir'] = new_dir




    def show_image(self):
        """Then crop and display the images in the tiles."""

        self.canvas.delete('text')
        self.canvas.delete('thumbnail')
        self.canvas.delete('zoom')

        if self.disp_image == None:
            return


        maxW = self.dat['maxWidth']
        tileW = maxW / 1
        tileH = self.dat['maxHeight']

        # Crop, anchor and display image
        self.disp_image.set_thumbnail( (tileW-2,tileH-2), self.dat['main_zoom'] )
        self.canvas.create_image(self.disp_image.anchor,
                                 image=self.disp_image.thumbnail,
                                 anchor=Tkinter.NW, tags='thumbnail')
#        self.disp_image.set_box( (0+600, 0+600, tileW+600, tileH+600) )
#        self.canvas.create_image( (tileW, 1), image=self.disp_image.image(), anchor=Tkinter.NW, tags='thumbnail')

        # Overlay info and icons
        self.canvas.create_image((0,0), image=self.exif_bg, anchor=Tkinter.NW, tags='text')


        # Display Histogram and EXIF data
        histo_offset = 0
        if self.dat.get('histogram'):
            self.canvas.create_image( (5,2), image=self.disp_image.get_histogram((350,30)), anchor=Tkinter.NW, tags='thumbnail')
            histo_offset = 34

        for i, each in enumerate(self.fman.get_filename()):
            self.canvas.create_text( (5, histo_offset+i*15), text=each, anchor=Tkinter.NW,
                                 fill='yellow', tags='text')
        if self.fman.hasNEF():
            self.canvas.create_text( (5, histo_offset+30), text='NEF available', anchor=Tkinter.NW,
                                 fill='yellow', tags='text')
        else:
            self.canvas.create_text( (5, histo_offset+30), text='NEF not found', anchor=Tkinter.NW,
                                 fill='grey', tags='text')
        self.canvas.create_text( (5, histo_offset+45), text=str(int(self.disp_image.scale*100))+'%', anchor=Tkinter.NW,
                                 fill='yellow', tags='text')
        for i, each in enumerate(self.disp_image.get_exif()):
            try:
                self.canvas.create_text( (5,histo_offset+60+i*15), text=each + ' - ' + self.disp_image.exif[each], anchor=Tkinter.NW,
                                 fill='yellow', tags='text')
            except:
                print 'error>>>', i, each


        # Display 'zoom' window
        if self.b1press:
            zoom_image = self.get_crop()
            # Calculate placement of full-size window
            placement = (self.b1press[0]-self.subwinsize, self.b1press[1]-self.subwinsize)
            self.canvas.create_image( placement, image=zoom_image, anchor=Tkinter.NW, tags='zoom')




    def show_zoom(self):
            image = self.disp_image.image(sobel=self.dat['sobel'])
            self.canvas.create_image( tile[:2], image=image, anchor=Tkinter.NW, tags='image' )




#    def change_mode(self):
#        self.get_thumbs()
#        self.refresh_display()

    def change_click_mode(self):
        print "i'm in!", self.rb.get()
#        if self.rb.get() == "Window Selection":
#            print "Window Selection"
#        if self.rb.get() == "Heading Selection":
#            print "Heading Selection"
#        if self.rb.get() == "Object Selection":
#            print "Object Selection"
#        if self.rb.get() == "Measure Distance":
#            print "Measure Distance"
#        if self.rb.get() == "Off":
#            print "Off"
#
#        self.refresh_display()



    def resize(self, event):
        self.dat['maxWidth'] = event.width
        self.dat['maxHeight'] = event.height
        self.dat['geometry'] = str(event.width) + 'x' + str(event.height) + '+0+0'
        self.canvas.config(width = event.width, height = event.height)

        self.show_image()



    def click_pt(self, event):
        if event.widget == self.canvas:
            # GET ASSOCIATED IMAGE
            self.b1press = (event.x, event.y)

            if self.disp_image != None:
                if self.disp_image.point( self.b1press ):
                    self.disp_image.set_box_center( self.b1press )
            else:
                return # IF NO ASSOCIATED IMAGE IS FOUND

            self.draw_zoom()


    def draw_zoom(self):
        self.canvas.delete('zoom')

        print 'creating zoom'
        zoom_image = self.get_crop()
        # Calculate placement of full-size window
        placement = (self.b1press[0]-self.subwinsize, self.b1press[1]-self.subwinsize)
        self.canvas.create_image( placement, image=zoom_image, anchor=Tkinter.NW, tags='zoom')




    def get_crop(self):
        ret_pt = self.disp_image.point(self.b1press)
        self.full_image = self.disp_image.image_full( ret_pt, radius=self.subwinsize )
        return self.full_image



    def shiftImage(self, event):
        self.b1press = (event.x,event.y)
        if event.widget == self.canvas and self.disp_image.point( self.b1press ):
            self.draw_zoom()





    def endMotion(self, event):
        self.inmotion = False



    def change_image(self, event):
#        print event.type,'|', event.char,'|', event.keysym,'|', event.keycode,'|', event.state

        # IF WHEEL TURNED, NOT HELD DOWN
        if (event.keycode == 37 and event.keysym == 'Left') or \
            (event.keycode == 120 and event.state == 8): # 10 is with caps lock
            self.next_image(event, -1)
            return
        elif (event.keycode == 39 and event.keysym == 'Right') or \
            (event.keycode == -120 and event.state == 8): # 10 is with caps lock
            self.next_image(event, 1)
            return

#
        # IF WHEEL BUTTON DOWN AND TURNED
        elif (event.keycode == 38 and event.keysym == 'Up') or \
            (event.state == 520 and event.keycode == 120):
            self.subwinsize += 25
        elif (event.keycode == 40 and event.keysym == 'Down') or \
            (event.state == 520 and event.keycode == -120):
            self.subwinsize -= 25

        if self.b1press:
            self.draw_zoom()



    def keypress(self, event):
        if event.char and event.char in 'asdwhe':
            if   event.char == 'd': self.fman.delALL()
            elif event.char == 'w': self.fman.saveNEF()
            elif event.char == 's': self.fman.saveJPG()
            elif event.char == 'a': self.fman.saveALL()
            elif event.char == 'h':
                self.dat['histogram'] = not self.dat.get('histogram')
                self.f.set_visible( self.dat['histogram'] )
            elif event.char == 'e': self.fman.undo_last()

            self.disp_image = DisplayImage( self.fman.load() )
            self.show_image()
#        print 'event.char', event.char


    def kill_zoom(self, event):
        self.b1press = None
        self.canvas.delete('zoom')



    def next_image(self, event, val=0):
        try:
            self.disp_image = DisplayImage( self.fman.load(val) )
        except:
            self.disp_image = None

        self.show_image()



    def deletekey(self, event):
        if self.disp_image:

            self.fman.delALL()
            self.disp_image = DisplayImage( self.fman.load() )
            self.show_image()



    def refresh_display(self):
        #print 'Refreshing'
        self.refreshImage()
        self.display_mask()
        self.get_drawing()
        self.refreshPolygon()
        self.refreshText()



    def display_mask(self):
        if self.rb.get() == "Window Selection":
            if not self.dat.get('subwindows'):
                w,h = self.disp_images[0].size
                self.dat['subwindows'] = \
                    [array([(0,int(h*.3)),(0,int(h*.6)),(w,int(h*.6)),(w,int(h*.3))])
                        for i in range(5)]

            mask = Image.new('RGBA', [int(each) for each in self.geometry().split('+')[0].split('x')])

            alpha = Image.new('L', mask.size, 100)
            draw_alpha = ImageDraw.Draw(alpha)
            for dimage in self.disp_images:
                if dimage == None:
                    break
                cam = dimage.ID % 10
                draw_alpha.polygon([dimage.to_disp_pt(xy) for xy in self.dat['subwindows'][cam]],
                                    fill=0)
            mask.putalpha( alpha )
            self.mask = ImageTk.PhotoImage( mask )
            self.canvas.create_image((0,0), image=self.mask, anchor=Tkinter.NW, tags='image' )
        elif self.rb.get() == "Heading Selection":
            mask = Image.new('RGBA', [int(each) for each in self.geometry().split('+')[0].split('x')])

            alpha = Image.new('L', mask.size, 100)
            draw_alpha = ImageDraw.Draw(alpha)
            for dimage in self.disp_images:
                if dimage == None:
                    break
                cam = dimage.ID % 10
                if self.dat.get('im_forward'):
                    fcam, xpos = self.dat.get('im_forward')
                    if cam == fcam:
                        draw_alpha.polygon([dimage.to_disp_pt((xpos-10,0)),
                                            dimage.to_disp_pt((xpos-10,dimage.size[1])),
                                            dimage.to_disp_pt((xpos+10,dimage.size[1])),
                                            dimage.to_disp_pt((xpos+10,0))],
                                            fill=0)
            mask.putalpha( alpha )
            self.mask = ImageTk.PhotoImage( mask )
            self.canvas.create_image((0,0), image=self.mask, anchor=Tkinter.NW, tags='image' )





    def refreshImage(self):
        self.canvas.delete('image')


        for dimage in self.disp_images[:nImage]:
            if dimage:
                imref = dimage.image()
                self.canvas.create_image(dimage.anchor, image=imref, anchor=Tkinter.NW, tags='image' )





    def endsession(self):
        with open( self.run_location + '\settings.ini', 'w' ) as wfile:
            pickle.dump(self.dat, wfile)
        wfile.close()
        self.quit()




    def sup(self, x):
        if isinstance(x,list):
            for i, each in enumerate(x):
                x[i] = each*1616./self.dat['imagesize'][1]
            return x
        return x*1616./self.dat['imagesize'][1]
    def sdown(self, x):
        if isinstance(x,list):
            for i, each in enumerate(x):
                x[i] = each*self.dat['imagesize'][1]/1616.
            return x
        return x*self.dat['imagesize'][1]/1616.



    def openWorkingDir(self):
        print 'Opening current working directory'
        os.startfile(os.getcwd())



    def set_work_dir(self):
        self.dat['dir_work'] = askdirectory(title='Choose a directory to store all session related files')





    def print_settings(self, string):
        print string + ':'
        for k in self.dat:
            print '\t', k, ':', self.dat[k]





def hello():
    print 'Please assign this option'





if __name__ == '__main__':
    app = PicScan_GUI(None)
    app.title('PicScan')
    app.mainloop()