#!/usr/bin/env python3
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Library General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor Boston, MA 02110-1301, USA

# Copyright 2012 Andrew Holmes <andrew.g.r.holmes@gmail.com>

"""
The CPIO file format is a common UNIX archive standard which collects file
system objects into a single stream of bytes.  This module provides tools to
create, read and write CPIO archives.
"""

import io
import os
import os.path
import stat
import struct


__all__ = [
    'is_cpiofile',
    'CpioInode',
    'CpioInfo',
    'CpioError',
    'HeaderError',
    'ChecksumError']


#------------------------------------------------------------------------------
# CPIO Constants
#------------------------------------------------------------------------------

BLOCKSIZE = 512

NEW_MAGIC = b'070701'
"""New ASCII (newc) magic."""
CRC_MAGIC = b'070702'
"""New CRC (crc) magic."""
OLD_MAGIC = b'070707'
"""Portable ASCII (oldc) magic."""
BIN_MAGIC = 0o070707
"""Old Binary (bin) magic."""

NEW_STRUCT = '=6s 8s 8s 8s 8s 8s 8s 8s 8s 8s 8s 8s 8s 8s'
OLD_STRUCT = '=6s 6s 6s 6s 6s 6s 6s 6s 11s 6s 11s'
BIN_STRUCT = '13H'


#------------------------------------------------------------------------------
# cpiofile Constants
#------------------------------------------------------------------------------

NEW_FORMAT = 0
"""New ASCII (newc) format."""
CRC_FORMAT = 1
"""New CRC (crc) format."""
OLD_FORMAT = 2
"""Portable ASCII (oldc) format."""
BIN_FORMAT = 3
"""Old Binary (bin) format."""


#------------------------------------------------------------------------------
# Exceptions
#------------------------------------------------------------------------------

class CpioError(Exception):
    """Base class for cpio exceptions"""
    pass


class HeaderError(CpioError):
    """
    The base class for header errors.  Both :exc:`ChecksumError` and
    :exc:`FormatError` inherit from this exception.
    """
    pass


class ChecksumError(HeaderError):
    """Raised when a checksum of an member's data doesn't match its header."""
    pass


class FormatError(HeaderError):
    """
    This may be raised by CpioInfo when an unsupported format is encountered
    or by CpioFile if an unexpected format change is detected mid-archive.
    """
    pass


#------------------------------------------------------------------------------
# Public Methods
#------------------------------------------------------------------------------

def is_cpiofile(self, path):
    """
    Return True if *path* is a cpio archive file, that the cpiofile module can
    read.
    """
    with io.open(path, 'rb') as fileobj:
        buf = fileobj.read(6)

        if buf in (NEW_MAGIC, CRC_MAGIC, OLD_MAGIC):
            return True
        if struct.unpack('<H', buf[:2])[0] == BIN_MAGIC:
            return True
        if struct.unpack('>H', buf[:2])[0] == BIN_MAGIC:
            return True


def checksum32(bytes):
    """Return a 32-bit unsigned sum of *bytes*."""
    return sum(ord(byte) for byte in bytes) & 0xFFFFFFFF


#------------------------------------------------------------------------------
# Classes
#------------------------------------------------------------------------------

class SubFile(object):
    pass


class CpioInfo(object):
    """
    Informational class which holds the details about an archive member given
    by a cpio header.  CpioInfo objects are returned by CpioFile.getmember(),
    CpioFile.getmembers() and CpioFile.getcpioinfo() and are usually created
    internally.
    """

    __slots__ = ['dev',
                 'ino',
                 'mode',
                 'uid',
                 'gid',
                 'nlink',
                 'mtime',
                 'rdev',
                 'size',
                 'check',
                 'name']

    dev = 0
    ino =

    def __init__(self):
        """."""

        self.dev = 0
        """Number of the device the inode resides on."""
        self.ino = 0
        """Inode number on disk."""
        self.mode = 0
        """Inode protection mode.

        .. note::
            The :mod:`stat` module provides functions that may be useful."""
        self.uid = 0
        """User id of the owner."""
        self.gid = 0
        """Group id of the owner."""
        self.nlink = 0
        """Number of links to the inode."""
        self.mtime = 0
        """Time of last modification."""
        self.rdev = 0
        """Number of the device type."""
        self.size = 0
        """Size of the file data in bytes."""
        self.check = None
        """32-bit checksum of the file data (New CRC format only)."""
        self.link = None
        """The target path (symbolic links only)."""
        self.name = b'TRAILER!!!'
        """Pathname of the member."""

    def __getattr__(self, name):
        if name in self:
            return self[name]
        else:
            raise KeyError

    def __setattr__(self, name, value):
        self[name] = value

    def __eq__(self, other):
        """
        Members are considered equal if they are linked to the same inode and
        device numbers (eg. hardlinks).
        """
        return (isinstance(other, self.__class__)
                and self.ino == other.ino
                and self.dev == other.dev)


class CpioFile(object):
    """
    The CpioFile object provides an interface to a cpio archive.  Each archive
    member is represented by a CpioInfo object, see CpioInfo Objects for
    details.

    A CpioFile object can be used as a context manager in a with statement.
    It will automatically be closed when the block is completed.  Please note
    that in the event of an exception an archive opened for writing will not
    be finalized; only the internally used file object will be closed.
    """

    _members = []
    _struct = None
    _fileobj = None

    #FIXME
    def __init__(self, path=None, mode='rb', fileobj=None, format=NEW_FORMAT,
                       ignore_zeroes=False, dereference=False):
        """
        The new class instance is based on *fileobj*, which may be any binary
        mode file object which supports read(), write() and seek() methods.
        If *fileobj* is None then *path* will be used to provide a file
        object.

        The *mode* argument must be either 'rb' or 'wb'.  The default is 'rb'
        either if *path* is given or if *fileobj* is read-write.

        The *format* argument should be one of :const:`NEW_FORMAT`,
        :const:`CRC_FORMAT`, :const:`OLD_FORMAT` or :const:`BIN_FORMAT`.
        """
        # Check *mode*
        if '+' in mode:
            raise ValueError('read-write mode not supported')

        if 'b' not in mode:
            mode += 'b'

        # Check *fileobj*/*path*
        if fileobj or path:
            self._fileobj = fileobj or io.open(path, mode)
        else:
            raise ValueError('either fileobj or path must be given')

        # Check format
        if format not in (NEW_FORMAT, CRC_FORMAT, OLD_FORMAT, BIN_FORMAT):
            raise ValueError('unknown format')
        elif not self._fileobj.readable():
            #FIXME setup stuct object
            pass

        #FIXME If the file object is readable and a known format, read it
        if self._fileobj.readable():

            self._read()

    def __enter__(self):
        return self

    def __exit__(self, extype, exvalue, extraceback):
        if extype is None:
            return self.close()

    def __iter__(self):
        return iter(self._members)

    def __repr__(self):
        s = repr(self._fileobj)
        return '<cpio ' + s[1:-1] + ' ' + hex(id(self)) + '>'

    #--------------------------------------------------------------------------
    # Private Methods
    #--------------------------------------------------------------------------

    def _read_new(self):
        pass

    def _read_old(self):
        pass

    def _read_bin(self):
        pass

    #--------------------------------------------------------------------------
    # Public Methods
    #--------------------------------------------------------------------------

    #FIXME
    def add(self, name, arcname=None, recursive=True, filter=None):
        """
        Add the file *name* to the archive.  *name* may be any type of file
        (directory, fifo, symbolic link, etc.). If given, *arcname* specifies
        an alternative name for the file in the archive.  Directories are
        added recursively by default. This can be avoided by setting
        *recursive* to False. *filter* is a function that expects a CpioInfo
        object argument and returns the changed CpioInfo object, if it returns
        None the CpioInfo object will be excluded from the archive.
        """
        pass

    #FIXME
    def addfile(self, cpioinfo, fileobj=None):
        """
        Add the CpioInfo object *cpioinfo* to the archive.  If *fileobj* is
        given, CpioInfo.size bytes are read from it and added to the archive.
        You can create CpioInfo objects using getcpioinfo().

        .. note::
            On Windows platforms, *fileobj* should always be opened with mode
            'rb' to avoid irritation about the file size.
        """
        # check mode

        tarinfo = copy.copy(tarinfo)

        buf = tarinfo.tobuf(self.format, self.encoding, self.errors)
        self._fileobj.write(buf)
        self.offset += len(buf)

        # If there's data to follow, append it.
        if fileobj is not None:
            copyfileobj(fileobj, self._fileobj, tarinfo.size)
            blocks, remainder = divmod(tarinfo.size, BLOCKSIZE)
            if remainder > 0:
                self._fileobj.write(NUL * (BLOCKSIZE - remainder))
                blocks += 1
            self.offset += blocks * BLOCKSIZE

        self.members.append(tarinfo)

    #FIXME
    def close(self):
        """
        Close the :class:`CpioFile`.  In write-mode, a trailer is appended to
        the archive.
        """
        if self._fileobj is None:
            return

        #if self._fileobj.writable():
        #    self._write_member(CpioInfo(self._fileobj))

        self._fileobj = None

    def closed(self):
        """True if the stream is closed."""
        return self._fileobj is None

    #FIXME
    def extract(self, member, path=".", set_attrs=True):
        """
        Extract a member from the archive to the current working directory,
        using its full name. Its file information is extracted as accurately
        as possible. *member* may be a filename or a TarInfo object.  You can
        specify a different directory using *path*. File attributes (owner,
        mtime, mode) are set unless *set_attrs* is False.

        .. warning::
           Never extract archives from untrusted sources without prior
           inspection. It is possible that files are created outside of path,
           e.g. members that have absolute filenames starting with "/" or
           filenames with two dots "..".
        """
        if isinstance(member, str):
            # cpioinfo = self.getmember(member)
            pass
        else:
            # cpioinfo = member
            pass

        path = os.path.join(path, member.name)

        # Create a file on disk for the appropriate type
        if stat.S_ISDIR(member.mode):
            os.mkdir(path, member.mode & 0o777)
        #FIXME: hardlinks
        elif stat.S_ISREG(member.mode):
            with io.open(path, 'wb') as pathobj:
                member.seek(0)
                pathobj.write(member.read())
        #FIXME: unix only
        elif os.name == 'posix':
            if stat.S_ISLNK(member.mode):
                os.symlink(member.target, path)
            else:
                os.mknod(path, member.mode, member.dev)

    #FIXME
    def extractall(self, path='.', members=None):
        """
        Extract all members from the archive to the current working directory
        and set owner, modification time and permissions on directories
        afterwards.  *path* specifies a different directory to extract to.
        *members* is optional and must be a subset of the list returned by
        getmembers().

        .. warning::
           See the warning for :meth:`extract`.
        """
        directories = []

        if members is None:
            members = self

        for cpioinfo in members:
            if stat.S_ISDIR(cpioinfo.mode):
                directories.append(cpioinfo)

            self.extract(cpioinfo, path, set_attrs=not stat.S_ISDIR(cpioinfo))

        # Reverse sort directories.
        directories.sort(key=lambda a: a.name)
        directories.reverse()

        # Set correct owner, mtime and filemode on directories.
        for cpioinfo in directories:
            pass
            # dirpath = os.path.join(path, cpioinfo.name)

    #FIXME
    def extractfile(self, member):
        """*undocumented*"""
        pass

    #FIXME
    def getcpioinfo(self, name, arcname=None, fileobj=None):
        """."""
        pass

    #FIXME
    def getmember(self):
        """."""
        pass

    #FIXME
    def getmembers(self):
        """."""
        pass

    #FIXME
    def getnames(self):
        """Return a list of member names."""
        return [member.name for member in self]

    #FIXME
    def list(self):
        """."""
        pass

    #FIXME
    def next(self):
        """."""
        pass

    #FIXME
    def readable(self):
        return self._fileobj.readable()


#------------------------------------------------------------------------------
# cpiofile CLI
#------------------------------------------------------------------------------

#FIXME
def main():
    """*undocumented*"""
    with CpioFile('src/test.newc.cpio') as cpio:
        #cpio.extractall(b'test')
        print(cpio.getnames())


if __name__ == "__main__":
    main()
