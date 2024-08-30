import os
import platform

def open_file(file_path):
    """
    Opens a file using the default application for that file type.
    
    :param file_path: The path to the file to be opened
    """
    try:
        if platform.system() == 'Darwin':       # macOS
            os.system(f'open "{file_path}"')
        elif platform.system() == 'Windows':    # Windows
            os.system(f'start "" "{file_path}"')
        else:                                   # Linux and other Unix-like
            os.system(f'xdg-open "{file_path}"')
    except Exception as e:
        print(f"Error opening {file_path}: {str(e)}")
