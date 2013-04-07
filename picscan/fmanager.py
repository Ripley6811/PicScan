#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Contains all os related functions.

Maintains a list of all JPGs and NEFs in the working directory.
Manages the loading, moving and deleting of files.

:REQUIRES: PIL
:TODO: ...

:AUTHOR: Ripley6811
:ORGANIZATION: National Cheng Kung University, Department of Earth Sciences
:CONTACT: python@boun.cr
:SINCE: Mon Mar 18 15:04:45 2013
:VERSION: 0.3
:STATUS: Rewriting
"""
#===============================================================================
# PROGRAM METADATA
#===============================================================================
__author__ = 'Ripley6811'
__contact__ = 'python@boun.cr'
__copyright__ = ''
__license__ = ''
__date__ = 'Mon Mar 18 15:04:45 2013'
__version__ = '0.3'

#===============================================================================
# IMPORT STATEMENTS
#===============================================================================

#import os  # os.walk(basedir) FOR GETTING DIR STRUCTURE
import tkFileDialog
import os
from collections import OrderedDict
import thread
import time





class FileManager:
    curr = None # pointer to current index in jpg_list
    thread_tasks = [] # tasks that are completed on a thread
    undo_tasks = [] # keep list to undo actions

    def __init__(self, init_image,
                       move_trash=True,
                       move_saved=False,):
        """Get a list of JPG, NEF, or DNG filenames from the directory where the user
        selected a file.

        :type init_image: string
        :arg  init_image: Full path to initial folder and image.
        :type move_trash: boolean
        :arg  move_trash: Deletions are moved to a sub-folder
        :type move_saved: boolean
        :arg  move_saved: Saved images are moved to a sub-folder
        """
        # Get JPG directory
        #XXX: Move to Main program
#        while True:
#            filename = tkFileDialog.askopenfilename(
##                            filetypes=[("JPEG", ".jpg"),("NEF", ".nef")],
#                            initialdir=work_dir if work_dir else None,
#                            )

        # Store working directory path and current file name
        self.dir, selected_file = os.path.split(init_image)

        # Store other default directories
        self.trash_dir = self.dir + '/trash'
        self.saved_dir = self.dir + '/saved'
        self.move_trash = move_trash
        self.move_saved = move_saved
        if move_trash and not os.path.exists( self.trash_dir ):
            os.mkdir( self.trash_dir )
        if move_saved and not os.path.exists( self.saved_dir ):
            os.mkdir( self.saved_dir )


        # Create list of JPG and NEF in working directories
        self.create_image_list()


        # Find index of selected file in JPG list, default to 0
#        print 'selected file', selected_file, selected_file in self.imfiles
        try:
            self.curr = self.imfiles.index(selected_file)
        except:
            print 'Selected file not found or not an image! Loading first available image.'
            self.curr = 0 if len(self.imfiles) > 0 else None


    def create_image_list( self ):
        '''Create lists of jpg, nef and dng file paths in a directory.

        '''
        self.imfiles = []
        self.imshow = []

        # Get list of JPG and NEF from work directory
        for each in os.listdir(self.dir):
            each = each.lower()
            if each.endswith(('jpg','nef','dng')):
                self.imfiles.append( each )
#                if each.endswith('nef') and jpg(each) in self.imfiles:
#                    self.imshow.append(False)
#                else:
#                    self.imshow.append(True)


        self.imfiles.sort()



    def get_filename(self):
        return self.dir, self.imfiles[self.curr]


#    def newNEFdir(self, new_dir=r'C:/' ):
#        # Get NEF dir from user
#        self.new_dir = tkFileDialog.askdirectory(initialdir=new_dir)
#        # Get new list of NEF files
#        self.nef_list = []
#        for each in listdir(self.nef_dir):
#            if each.lower().endswith('nef'):
#                self.nef_list.append(each.lower())



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


    def save_image(self):
        if self.move_saved:
            filename = self.imfiles.pop(self.curr)
            self.undo_tasks.append( "os.rename(os.path.join( self.saved_dir, r'" + filename
                              + "'), os.path.join( self.dir, r'" + filename + "' ) )" )
            os.rename( os.path.join( self.dir, filename ),
                       os.path.join( self.saved_dir, filename ) )
        else:
            self.curr += 1


    def trash_image(self):
        if self.move_trash:
            filename = self.imfiles.pop(self.curr)
            self.undo_tasks.append( "os.rename(os.path.join( self.trash_dir, r'" + filename
                              + "'), os.path.join( self.dir, r'" + filename + "' ) )" )
            os.rename( os.path.join( self.dir, filename ),
                       os.path.join( self.trash_dir, filename ) )
        else:
            self.curr += 1



#    def move_curr(self, saveJPG=True, saveNEF=True ):
#        '''File operations on the JPG and NEF files for an image.
#
#        saveJPG and saveNEF control whether JPGs and NEFs are moved to a
#        save folder or to a trash folder.
#        If both saveJPG and saveNEF are True, then NEF is moved to a NEF folder
#        within the save folder.
#
#        False, True = NEF copy -> save, NEF -> save backup, JPG -> trash
#        True, True = JPG -> save, NEF -> save backup
#        True, False = JPG -> save, NEF -> trash
#        False, False = NEF and JPG -> trash
#        '''
#        # Remove and store name of JPG
#        jpg_file = jpg(self.imfiles[self.curr])
#
#        # Does NEF exist, get tuple
#        nef_file = nef(self.imfiles[self.curr])
#
#        self.undo = []
#
#
#        if not path.exists(self.trash_dir):
#            print "Making 'trash' directory"
#            mkdir( self.trash_dir )
#
#        if self.use_saved_folder:
#            if not path.exists(self.jpg_dest):
#                print "Making 'JPG' directory"
#                mkdir( self.jpg_dest )
#            if not path.exists(self.nef_dest):
#                print "Making 'NEF' directory"
#                mkdir( self.nef_dest )
#
#
#        tasks = []
#        if self.hasNEF():
#            # Move NEF
#            if saveNEF and self.use_saved_folder:
#                tasks.append( "rename(path.join( self.dir, '" + nef_file
#                                        + "'), path.join( self.nef_dest, '" + nef_file + "' ) )" )
#                self.undo.append( (path.join( self.dir, nef_file ),
#                                   path.join( self.nef_dest, nef_file ) ) )
#            if not saveNEF:
#                tasks.append( "rename(path.join( self.dir,'" + nef_file
#                                        + "'), path.join( self.trash_dir, '" + nef_file + "' ) )" )
#                self.undo.append( (path.join( self.dir, nef_file ),
#                                   path.join( self.trash_dir, nef_file ) ) )
#                self.imshow[self.imfiles.index(nef_file)] = False
#
#
#        if self.hasJPG():
#            # Move JPG
#            if saveJPG and self.use_saved_folder:
#                tasks.append( "rename(path.join( self.dir,'" + jpg_file
#                                        + "'), path.join( self.jpg_dest, '" + jpg_file + "' ) )" )
#                self.undo.append( (path.join( self.dir, jpg_file ),
#                                   path.join( self.jpg_dest, jpg_file ) ) )
#            if not saveJPG and not saveNEF:
#                tasks.append( "rename(path.join( self.dir,'" + jpg_file
#                                        + "'), path.join( self.trash_dir, '" + jpg_file + "' ) )" )
#                self.undo.append( (path.join( self.dir, jpg_file ),
#                                   path.join( self.trash_dir, jpg_file ) ) )
#                self.imshow[self.imfiles.index(jpg_file)] = False
#
##        try:
#        thread.start_new_thread( self.run_tasks, (tasks,) )
##        except:
##            print "Error: unable to start thread.\n", tasks
#
##        self.get_image_list()
#
#        # Make sure curr points to an available file
#        nJPGs = len(self.imfiles)
#        self.curr += 1
#        self.curr %= nJPGs
#        while self.imshow[self.curr] == False:
#            if nJPGs == 0:
#                self.curr = None
#                break
#            self.curr += 1
#            self.curr %= nJPGs
#            if True not in self.imshow:
#                self.curr == None
#                break


    def undo_last(self):
        '''Reverses last movement (rename) of a file.'''
        if len(self.undo_tasks):
            exec( self.undo_tasks.pop() )


    def load(self, offset=0, change_curr=True):
        '''Loads the curr JPG.

        Set offset to +/-1 to load the next or prev image.
        Set change_curr to False to preload or peek at a filename
        '''
        # Ensure current pointer points to list item
        self.curr %= len(self.imfiles)

        if not change_curr:
            tmp = self.curr
        newi = self.curr + offset
        if offset != 0:
            # Assert new index exists
            if 0 <= newi < len(self.imfiles):
#                if self.imshow[newi]:
                    self.curr += offset
#                else:
#                    return self.load(offset+offset/abs(offset))
        pth = os.path.join( self.dir, self.imfiles[self.curr] )
        if not change_curr:
            self.curr = tmp
        return pth


    def run_tasks(self, tasks):
        while tasks:
            exec( tasks.pop(0) )
        self.get_image_list()


    def hasNEF(self):
        '''Returns True is NEF exists for the current image.'''
        return nef(self.imfiles[self.curr]) in self.imfiles

    def hasJPG(self):
        '''Returns True is JPG exists for the current image.'''
        return jpg(self.imfiles[self.curr]) in self.imfiles

    def hasDNG(self):
        '''Returns True is DNG exists for the current image.'''
        return dng(self.imfiles[self.curr]) in self.imfiles


def nef(filename):
    '''Converts filename to *.nef filename.'''
    return '.'.join( (filename.rsplit('.',1)[0], 'nef') )

def jpg(filename):
    '''Converts filename to *.jpg filename.'''
    return '.'.join( (filename.rsplit('.',1)[0], 'jpg') )

def dng(filename):
    '''Converts filename to *.dng filename.'''
    return '.'.join( (filename.rsplit('.',1)[0], 'dng') )
