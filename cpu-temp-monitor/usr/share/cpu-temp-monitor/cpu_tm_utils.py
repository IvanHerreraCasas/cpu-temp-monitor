import subprocess
import os
import sys

def open_file(file_path):
    os.system(f"xdg-open {file_path}")

def open_image(path):
    imageViewerFromCommandLine = {'linux':'xdg-open',
                                  'win32':'explorer',
                                  'darwin':'open'}[sys.platform]
    subprocess.run([imageViewerFromCommandLine, path])

