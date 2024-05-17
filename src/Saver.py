import os
from os.path import exists
import re

class Saver:

    def __init__( self, fileext ):
        self.basename = os.getcwd()
        self.fileext = '.' + fileext + '.csv'
    
    @staticmethod
    def clean_foldername( foldername ):
        return re.sub( r'[^a-zA-Z0-9_-]', '', foldername )
    
    def compute_foldername( self, subfolder ):
        return self.basename + "/" + self.clean_foldername( subfolder )

    def make_filename( self, folder, progr ):
        return folder + "/SNA" + "{:04d}".format(progr) + self.fileext

    def ensure_folder_exists( self, folder ):
        os.makedirs( folder, exist_ok=True )

    def compute_filename( self, subfolder ):
        folder = self.compute_foldername( subfolder )
        self.ensure_folder_exists( folder )

        progr = 0
        while( exists( self.make_filename( folder, progr ) ) ):
            progr += 1

        return self.make_filename( folder, progr )
    
    def save( self, subfolder, content ):
        saving_on = self.compute_filename( subfolder )
        with open( saving_on, 'w' ) as file:
            file.write(content)
        return saving_on