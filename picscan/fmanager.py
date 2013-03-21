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
from os import rename, remove, path, mkdir, listdir
from shutil import copy2
from PIL import Image


class FileManager:
    curr = None # pointer to current index in jpg_list

    def __init__(self, jpg_dir='', nef_dir='', trash_dir='', save_dir=''):
        """Get a list of jpeg filenames from the directory where the user
        selected a file.

        """
        # Set up JPG directory
        if not jpg_dir:
            filename = tkFileDialog.askopenfilename( filetypes=[("JPEG", ".jpg"),] )
            jpg_dir, selected_file = path.split(filename)
            # Check filename is JPG
            if not selected_file.lower().endswith('jpg'):
                selected_file = ''

        # Set up NEF directory
        if not nef_dir or not path.exists(nef_dir):
            nef_dir = jpg_dir

        # Set up TRASH directory
        if not trash_dir or not path.exists(trash_dir):
            trash_dir = jpg_dir + '/trash'
            if not path.exists(trash_dir):
                mkdir( trash_dir )

        # Set up SAVE directory
        if not save_dir or not path.exists(save_dir):
            save_dir = jpg_dir + '/save'
            if not path.exists(save_dir):
                mkdir( save_dir )
            if not path.exists(save_dir + '/NEF_backup'):
                mkdir( save_dir + '/NEF_backup' )

        # Store global values
        self.jpg_dir = jpg_dir
        self.nef_dir = nef_dir
        self.trash_dir = trash_dir
        self.save_dir = save_dir
        self.savenef_dir = save_dir + '/NEF_backup'

        # Create list of JPG and NEF in working directories
        self.jpg_list = []
        self.nef_list = []
        for each in listdir(self.jpg_dir):
            if each.lower().endswith('jpg'):
                self.jpg_list.append(each.lower())
        for each in listdir(self.nef_dir):
            if each.lower().endswith('nef'):
                self.nef_list.append(each.lower())
        # Sort JPG list. NEF list does not need sorting
        self.jpg_list.sort()

        # Find index of selected file in JPG list, default to 0
        try:
            self.curr = self.jpg_list.index(selected_file)
        except:
            self.curr = 0 if len(self.jpg_list) > 0 else None



    def hasNEF(self):
        '''Returns True is NEF exists for the current image.'''
        return (self.jpg_list[self.curr][:-4] + '.nef') in self.nef_list


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

        TODO: Make an option for permanently deleting NEF.
        '''
        self.move_curr(False, False, True)


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


    def move_curr(self, saveJPG=True, saveNEF=True, deleteNEF=False ):
        '''Moves the current NEF to save folder and moves JPG to trash.

        saveJPG and saveNEF control whether JPGs and NEFs are moved to a
        save folder or to a trash folder.
        If both saveJPG and saveNEF are True, then NEF is moved to a NEF folder
        within the save folder.
        deleteNEF will permanently delete NEF instead of moving to trash.

        False, True = NEF copy -> save, NEF -> save backup, JPG -> trash
        True, True = JPG -> save, NEF -> save backup
        True, False = JPG -> save, NEF -> trash
        False, False = NEF and JPG -> trash
        '''
        # Remove and store name of JPG
        jpg_file = self.jpg_list.pop(self.curr)

        # Does NEF exist
        nef_file = jpg_file[:-4] + '.nef'
        if nef_file in self.nef_list:
            # Move NEF
            if saveNEF:
                if not path.exists(self.savenef_dir):
                    print self.savenef_dir
                    mkdir( self.savenef_dir )
                if not saveJPG: # Put a copy in the save folder
                    copy2(path.join( self.nef_dir, nef_file ),
                          path.join( self.save_dir, nef_file ) )
                # Transfer NEF to save folder's NEF backup
                rename(path.join( self.nef_dir, nef_file ),
                       path.join( self.savenef_dir, nef_file ) )
            elif deleteNEF:
                remove( path.join( self.nef_dir, nef_file ) )
            else:
                rename( path.join( self.nef_dir, nef_file ),
                        path.join( self.trash_dir, nef_file ) )
            self.nef_list.remove(nef_file)

        # Move JPG
        if saveJPG:
            rename( path.join( self.jpg_dir, jpg_file ),
                    path.join( self.save_dir, jpg_file ) )
        else:
            rename( path.join( self.jpg_dir, jpg_file ),
                    path.join( self.trash_dir, jpg_file ) )

        # Make sure curr points to an available file
        nJPGs = len(self.jpg_list)
        if self.curr >= nJPGs and nJPGs > 0:
            self.curr = nJPGs - 1
        elif nJPGs == 0:
            self.curr = None


    def load(self, offset=0):
        '''Loads the curr JPG.

        Set offset to +/-1 to load the next or prev image.
        '''
        if offset != 0:
            # Assert new index exists
            if 0 <= (self.curr + offset) < len(self.jpg_list):
                self.curr += offset
        return Image.open( path.join( self.jpg_dir, self.jpg_list[self.curr] ) )