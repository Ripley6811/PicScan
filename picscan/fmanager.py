#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Contains all os related functions.

Maintains a list of all JPGs and NEFs in the working directory.
Manages the loading, moving and deleting of files.

:REQUIRES: PIL
:PRECONDITION: ...
:POSTCONDITION: ...

:AUTHOR: Ripley6811
:ORGANIZATION: National Cheng Kung University, Department of Earth Sciences
:CONTACT: python@boun.cr
:SINCE: Mon Mar 18 15:04:45 2013
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
__date__ = 'Mon Mar 18 15:04:45 2013'
__version__ = '0.1'

#===============================================================================
# IMPORT STATEMENTS
#===============================================================================

#import os  # os.walk(basedir) FOR GETTING DIR STRUCTURE
import tkFileDialog
from os import rename, path, mkdir, listdir #, remove
from collections import OrderedDict
import thread
import time





class FileManager:
    curr = None # pointer to current index in jpg_list
    thread_tasks = []

    def __init__(self, work_dir='', nef_dir='',
                 use_saved_folder=False,
                 include_saved_files=False,):
        """Get a list of jpeg and NEF filenames from the directory where the user
        selected a file.

        Pass an initial directory as the first parameter.

        """
        # Get JPG directory
        while True:
            filename = tkFileDialog.askopenfilename(
#                            filetypes=[("JPEG", ".jpg"),("NEF", ".nef")],
                            initialdir=work_dir if work_dir else None,
                            )
            self.dir, selected_file = path.split(filename)
            # Check filename is JPG
            selected_file = selected_file.lower()
            if selected_file.endswith(('jpg','nef')):
                break

        # Set up NEF directory
        self.nef_dir = nef_dir if (nef_dir and path.exists(nef_dir)) else self.dir


        # Store other default directories
        self.trash_dir = self.dir + '/trash'
        self.jpg_dest = self.dir + '/JPG'
        self.nef_dest = self.dir + '/NEF'
        self.use_saved_folder = use_saved_folder
        self.include_saved_files = include_saved_files

        # Create list of JPG and NEF in working directories
        self.get_image_list(include_saved_files)


        # Find index of selected file in JPG list, default to 0
#        print 'selected file', selected_file, selected_file in self.imfiles
        try:
            self.curr = self.imfiles.index(selected_file)
        except:
            print 'file not found!'
            self.curr = 0 if len(self.imfiles) > 0 else None


    def get_image_list(self, include_save_folder=False):
        '''Create lists of jpg and nef file paths.

        Names are stored as a tuple (directory, filename).
        '''
#        self.jpg_list = []
#        self.nef_list = []
        self.imfiles = []
        self.imshow = []

        # Get list of JPG and NEF from work directory
        for each in listdir(self.dir):
            each = each.lower()
            if each.endswith(('jpg','nef')):
                self.imfiles.append( each )
                if each.endswith('nef') and jpg(each) in self.imfiles:
                    self.imshow.append(False)
                else:
                    self.imshow.append(True)


        self.imfiles.sort()

        # Sort JPG list by filename. NEF list does not need sorting
#        self.imfiles.sort(key=lambda x: x[1])



    def hasNEF(self):
        '''Returns True is NEF exists for the current image.'''
        return nef(self.imfiles[self.curr]) in self.imfiles
    def hasJPG(self):
        '''Returns True is NEF exists for the current image.'''
        return jpg(self.imfiles[self.curr]) in self.imfiles



    def get_filename(self):
        return self.dir, self.imfiles[self.curr]


    def newNEFdir(self, new_dir=r'C:/' ):
        # Get NEF dir from user
        self.new_dir = tkFileDialog.askdirectory(initialdir=new_dir)
        # Get new list of NEF files
        self.nef_list = []
        for each in listdir(self.nef_dir):
            if each.lower().endswith('nef'):
                self.nef_list.append(each.lower())



    def delALL(self):
        '''Moves the current JPG and NEF to trash folder.
        '''
        self.move_curr(False, False)


    def saveJPG(self):
        '''Moves the current JPG to save folder and moves NEF to trash.
        '''
        self.move_curr(True, False)


    def saveNEF(self):
        '''Moves the current NEF to save folder and moves JPG to trash.
        '''
        # Remove and store name of JPG
        self.move_curr(False, True)


    def saveALL(self):
        self.move_curr(True, True)


    def move_curr(self, saveJPG=True, saveNEF=True ):
        '''File operations on the JPG and NEF files for an image.

        saveJPG and saveNEF control whether JPGs and NEFs are moved to a
        save folder or to a trash folder.
        If both saveJPG and saveNEF are True, then NEF is moved to a NEF folder
        within the save folder.

        False, True = NEF copy -> save, NEF -> save backup, JPG -> trash
        True, True = JPG -> save, NEF -> save backup
        True, False = JPG -> save, NEF -> trash
        False, False = NEF and JPG -> trash
        '''
        # Remove and store name of JPG
        jpg_file = jpg(self.imfiles[self.curr])

        # Does NEF exist, get tuple
        nef_file = nef(self.imfiles[self.curr])

        self.undo = []


        if not path.exists(self.trash_dir):
            print "Making 'trash' directory"
            mkdir( self.trash_dir )

        if self.use_saved_folder:
            if not path.exists(self.jpg_dest):
                print "Making 'JPG' directory"
                mkdir( self.jpg_dest )
            if not path.exists(self.nef_dest):
                print "Making 'NEF' directory"
                mkdir( self.nef_dest )


        tasks = []
        if self.hasNEF():
            # Move NEF
            if saveNEF and self.use_saved_folder:
                tasks.append( "rename(path.join( self.dir, '" + nef_file
                                        + "'), path.join( self.nef_dest, '" + nef_file + "' ) )" )
                self.undo.append( (path.join( self.dir, nef_file ),
                                   path.join( self.nef_dest, nef_file ) ) )
            if not saveNEF:
                tasks.append( "rename(path.join( self.dir,'" + nef_file
                                        + "'), path.join( self.trash_dir, '" + nef_file + "' ) )" )
                self.undo.append( (path.join( self.dir, nef_file ),
                                   path.join( self.trash_dir, nef_file ) ) )
                self.imshow[self.imfiles.index(nef_file)] = False


        if self.hasJPG():
            # Move JPG
            if saveJPG and self.use_saved_folder:
                tasks.append( "rename(path.join( self.dir,'" + jpg_file
                                        + "'), path.join( self.jpg_dest, '" + jpg_file + "' ) )" )
                self.undo.append( (path.join( self.dir, jpg_file ),
                                   path.join( self.jpg_dest, jpg_file ) ) )
            if not saveJPG and not saveNEF:
                tasks.append( "rename(path.join( self.dir,'" + jpg_file
                                        + "'), path.join( self.trash_dir, '" + jpg_file + "' ) )" )
                self.undo.append( (path.join( self.dir, jpg_file ),
                                   path.join( self.trash_dir, jpg_file ) ) )
                self.imshow[self.imfiles.index(jpg_file)] = False

#        try:
        thread.start_new_thread( self.run_tasks, (tasks,) )
#        except:
#            print "Error: unable to start thread.\n", tasks

#        self.get_image_list()

        # Make sure curr points to an available file
        nJPGs = len(self.imfiles)
        self.curr += 1
        self.curr %= nJPGs
        while self.imshow[self.curr] == False:
            if nJPGs == 0:
                self.curr = None
                break
            self.curr += 1
            self.curr %= nJPGs
            if True not in self.imshow:
                self.curr == None
                break


    def undo_last(self):
        '''TODO: create undo method'''
        for each in self.undo:
            rename( each[1], each[0] )

            dirfile = path.split(each[0])
            dirfile = (dirfile[0].lower(),dirfile[1].lower())
            if each[0].lower().endswith('.jpg') and dirfile not in self.jpg_list:
                self.jpg_list.append( dirfile )
                self.jpg_list.sort(key=lambda x: x[1])
                self.curr = self.jpg_list.index(dirfile)
            elif each[0].lower().endswith('.nef') and dirfile not in self.nef_list:
                self.nef_list.append( dirfile )


    def load(self, offset=0, change_curr=True):
        '''Loads the curr JPG.

        Set offset to +/-1 to load the next or prev image.
        Set change_curr to False to preload or peek at a filename
        '''
        if not change_curr:
            tmp = self.curr
        newi = self.curr + offset
        if offset != 0:
            # Assert new index exists
            if 0 <= newi < len(self.imfiles):
                if self.imshow[newi]:
                    self.curr += offset
                else:
                    return self.load(offset+offset/abs(offset))
        pth = path.join( self.dir, self.imfiles[self.curr] )
        if not change_curr:
            self.curr = tmp
        return pth


    def run_tasks(self, tasks):
        while tasks:
            exec( tasks.pop(0) )
        self.get_image_list()

def nef(filename):
    '''Converts *.jpg filename to *.nef filename.'''
    return filename[:-4] + '.nef'
def jpg(filename):
    '''Converts *.nef filename to *.jpg filename.'''
    return filename[:-4] + '.jpg'
