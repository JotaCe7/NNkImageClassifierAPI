import hashlib
from os.path import splitext, basename


def allowed_file(filename:str):
    """
    Checks if the format for the file received is acceptable. For this
    particular case, we must accept only image files. This is, files with
    extension ".png", ".jpg", ".jpeg" or ".gif".

    Parameters
    ----------
    filename : str
        Filename from werkzeug.datastructures.FileStorage file.

    Returns
    -------
    bool
        True if the file is an image, False otherwise.
    """
    # Current implementation will allow any kind of file.
    # TODO
    valid_extensions = [".png", ".jpg", ".jpeg", ".gif"]
    extension = splitext(filename.lower())[1]
    is_allowed = True if extension in valid_extensions else False

    print(extension)
    return is_allowed


def get_file_hash(file):
    """
    Returns a new filename based on the file content using MD5 hashing.
    It uses hashlib.md5() function from Python standard library to get
    the hash.

    Parameters
    ----------
    file : werkzeug.datastructures.FileStorage
        File sent by user.

    Returns
    -------
    str
        New filename based in md5 file hash.
    """
    # Current implementation will return the original file name.
    # TODO
    data = file.read()
    md5hash = hashlib.md5(data).hexdigest()
    extension = splitext(file.filename)[1]
    hashed_name = md5hash + extension
    file.seek(0)
    return hashed_name
