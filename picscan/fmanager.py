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


class FileManager:
    curr = None # pointer to current index in jpg_list

    def __init__(self, work_dir='', nef_dir='',
                 use_saved_folder=False,
                 include_saved_files=False,):
        """Get a list of jpeg filenames from the directory where the user
        selected a file.

        Pass an initial directory as the first parameter.

        """
        # Get JPG directory
        while True:
            filename = tkFileDialog.askopenfilename(
                            filetypes=[("JPEG", ".jpg"),],
                            initialdir=work_dir if work_dir else None,
                            )
            self.work_dir, selected_file = path.split(filename)
            # Check filename is JPG
            if selected_file.lower().endswith('jpg'):
                break

        # Set up NEF directory
        self.nef_dir = nef_dir if (nef_dir and path.exists(nef_dir)) else self.work_dir


        # Store other default directories
        self.trash_dir = self.work_dir + '/trash'
        self.jpg_dest = self.work_dir + '/JPG'
        self.nef_dest = self.work_dir + '/NEF'
        self.use_saved_folder = use_saved_folder
        self.include_saved_files = include_saved_files

        # Create list of JPG and NEF in working directories
        self.get_image_list(include_saved_files)


        # Find index of selected file in JPG list, default to 0
        try:
            self.curr = self.jpg_list.index((self.work_dir,selected_file))
        except:
            print 'file not found!'
            self.curr = 0 if len(self.jpg_list) > 0 else None


    def get_image_list(self, include_save_folder=False):
        '''Create lists of jpg and nef file paths.

        Names are stored as a tuple (directory, filename).
        '''
        self.jpg_list = []
        self.nef_list = []

        # Get list of JPG and NEF from work directory
        for each in listdir(self.work_dir):
            if each.lower().endswith('jpg'):
                self.jpg_list.append((self.work_dir,each.lower()))
            elif each.lower().endswith('nef'):
                self.nef_list.append((self.work_dir,each.lower()))

        # If nef source dir is different than work dir, add to list
        if self.nef_dir != self.work_dir:
            for each in listdir(self.nef_dir):
                if each.lower().endswith('nef'):
                    self.nef_list.append((self.nef_dir,each.lower()))

        # If already saved JPG and NEF are desired, add to respective lists
        if include_save_folder:
            for each in listdir(self.jpg_dest):
                if each.lower().endswith('jpg'):
                    self.jpg_list.append((self.jpg_dest,each.lower()))
                elif each.lower().endswith('nef'):
                    # NEF without JPGs will not be shown
                    self.nef_list.append((self.jpg_dest,each.lower()))
            for each in listdir(self.nef_dest):
                if each.lower().endswith('nef'):
                    self.nef_list.append((self.nef_dest,each.lower()))

        # Sort JPG list by filename. NEF list does not need sorting
        self.jpg_list.sort(key=lambda x: x[1])



    def hasNEF(self):
        '''Returns True is NEF exists for the current image.'''
        nef_file = nef(self.jpg_list[self.curr][1])
        # Try to find index in NEF list, else set index to -1
        try:
            nef_index = [n[1] for n in self.nef_list].index(nef_file)
        except:
            nef_index = -1
        # Return the NEF filename or False
        if nef_index >= 0:
            return self.nef_list[nef_index]
        else:
            return False


    def get_filename(self):
        return self.jpg_list[self.curr]


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
        '''Moves the current NEF to save folder and moves JPG to trash.

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
        jpg_file = self.jpg_list[self.curr]

        # Does NEF exist, get tuple
        nef_file = self.hasNEF()

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


        if nef_file:
            # Move NEF
            if saveNEF and self.use_saved_folder:
                rename(path.join( *nef_file ),
                       path.join( self.nef_dest, nef_file[1] ) )
                self.nef_list.remove(nef_file)
                self.undo.append( (path.join( *nef_file ),
                                   path.join( self.nef_dest, nef_file[1] ) ) )
            if not saveNEF:
                rename( path.join( *nef_file ),
                        path.join( self.trash_dir, nef_file[1] ) )
                self.nef_list.remove(nef_file)
                self.undo.append( (path.join( *nef_file ),
                                   path.join( self.trash_dir, nef_file[1] ) ) )

        # Move JPG
        if saveJPG and self.use_saved_folder:
            rename( path.join( *jpg_file ),
                    path.join( self.jpg_dest, jpg_file[1] ) )
            self.jpg_list.remove(jpg_file)
            self.undo.append( (path.join( *jpg_file ),
                               path.join( self.jpg_dest, jpg_file[1] ) ) )
        if not saveJPG and not saveNEF:
            rename( path.join( *jpg_file ),
                    path.join( self.trash_dir, jpg_file[1] ) )
            self.jpg_list.remove(jpg_file)
            self.undo.append( (path.join( *jpg_file ),
                               path.join( self.trash_dir, jpg_file[1] ) ) )
        # If attempting to only save a non-existant NEF, then do nothing
        elif not saveJPG and saveNEF and nef_file:
            rename( path.join( *jpg_file ),
                    path.join( self.trash_dir, jpg_file[1] ) )
            self.jpg_list.remove(jpg_file)
            self.undo.append( (path.join( *jpg_file ),
                               path.join( self.trash_dir, jpg_file[1] ) ) )


        # Make sure curr points to an available file
        nJPGs = len(self.jpg_list)
        if self.curr >= nJPGs and nJPGs > 0:
            self.curr = nJPGs - 1
        elif nJPGs == 0:
            self.curr = None


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


    def load(self, offset=0):
        '''Loads the curr JPG.

        Set offset to +/-1 to load the next or prev image.
        '''
        if offset != 0:
            # Assert new index exists
            if 0 <= (self.curr + offset) < len(self.jpg_list):
                self.curr += offset
        return path.join( *self.jpg_list[self.curr] )


def nef(jpg_filename):
    '''Converts *.jpg filename to *.nef filename.'''
    return jpg_filename[:-4] + '.nef'
