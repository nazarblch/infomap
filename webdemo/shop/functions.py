import os
from settings import YML_UPLOAD_PATH

def download(url, localpath):
    """Copy the contents of a file from a given URL
     to a local file.
     """
    import urllib
    webFile = urllib.urlopen(url)
    localFile = open(localpath, 'w')
    localFile.write(webFile.read())
    webFile.close()
    localFile.close()






def save_upload( uploaded, filename, raw_data, request ):
    try:
        from io import FileIO, BufferedWriter

        filename = os.path.join(os.path.abspath(os.path.dirname(__file__)), YML_UPLOAD_PATH + str(filename))

        with BufferedWriter( FileIO( filename, "wb" ) ) as dest:

            # if the "advanced" upload, read directly from the HTTP request
            # with the Django 1.3 functionality
            if raw_data:
                foo = uploaded.read( 1024 )
                while foo:
                    dest.write( foo )
                    foo = uploaded.read( 1024 )
            # if not raw, it was a form upload so read in the normal Django chunks fashion
            else:
                for c in uploaded.chunks( ):
                    dest.write( c )

            request.session['ymlfile'] = filename
            return True

    except IOError, e:
        # could not open the file most likely
        print e
        return False
