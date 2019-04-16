from shutil import make_archive, copy2, copytree, copymode, copystat, move, rmtree
from tempfile import mkdtemp
from logging import info, basicConfig
from os.path import isdir, join
from re import search
#-t, --target-directory=DIRECTORY
#              copy all SOURCE arguments into DIRECTORY
#-T, --no-target-directory
#              treat DEST as a normal file
#-v, --verbose
#              explain what is being done
#-R, -r, --recursive
#              copy directories recursively
#--preserve[=ATTR_LIST]
#              preserve the specified attributes (default:
#              mode,ownership,timestamps), if possible additional attributes:
#              context, links, xattr, all
#-a, --archive
#              same as -dR --preserve=all
#-i, --interactive
#              prompt before overwrite (overrides a previous -n option)

# Check if the wanted archive format can be used also returns it
def getFormat(path):
    # Reference for any ztar format
    reference = {'.tar.gz':'gztar', '.tar.bz':'bztar', '.tar.xz':'.xztar'}
    if path[-4:] in ('.zip', '.tar'):
        archive_format = path[-3:]
    else:
        if reference.setdefault(path[-7:], False):
            archive_format = reference[path[-7:]]
        else:
            archive_format = 'zip'
    # Debug
    info(f'Using: {archive_format}')
    return archive_format
class CPHandler:
    def __init__(self):
        self.__source = None
        self.__dest = None
        self.__verbose = True

    def setDest(self, dest):
        dest = dest.replace('\\', '/')
        if '/' not in dest:
            dest = './' + dest
        self.__dest = dest

    def setSource(self, source):
        source = source.replace('\\', '/')
        if '/' not in source:
            source = './' + source
        self.__source = source

    # Create archieve of a folder
    def archive(self):
        temporal_location = mkdtemp()
        try:
            # Get the archive format
            archive_format = getFormat(self.__dest)
            # Temporary archive name
            temporary_name = str(hash(self.__dest)-hash(self.__source))[1:]
            # Create a temporal location to save only a moment the archive
            # This way we except having a archive inside another (infinite loop)
            # Temporal archive path
            archive_name = join(temporal_location, temporary_name)
            # Make a archive of the source directory
            make_archive(archive_name, archive_format, self.__source, self.__source, verbose=self.__verbose,)
            # When the format wanted is not zip or tar
            if len(archive_format) > 3:
                archive_format = f'tar.{archive_format[:2]}'
            # Move the archive created to the wanted destination
            move(f'{archive_name}.{archive_format}', self.__dest)
            info('Done, archive successfully created')
        except Exception as e:
            info(str(e))
            pass
        finally:
            # remove that tempory folder created and everything inside it
            rmtree(temporal_location)
            info('Temporary file removed')