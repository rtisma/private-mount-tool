# -*- coding: utf-8 -*-

__version__ = "0.1.0"


import sys
import os
import argparse
import subprocess
import json
from tabulate import tabulate
from .utils import check_executable,check_state


def getOptions():
    version_str = '%(prog)s' + " Version %s" % str(__version__)
    parser = argparse.ArgumentParser(description="Tool to manage mounting of disks", add_help=True)

    parser.add_argument('--version',
            action="version",
            help="Prints program version and exits",
            version=version_str)

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-c", "--configure",
                        action="store_true", dest="configure", default=False,
                        help="Interactively configure")
    # configure lsblk tool, default is /bin/lsblk

    group.add_argument("-a", "--attach",
                       action="store_true", dest="attach", default=False,
                       help="Interactively attach a device")
    group.add_argument("-d", "--detach",
                       action="store_true", dest="detach", default=False,
                       help="Interactively detach a device")

    options = parser.parse_args()

    return options



# command line
def main():
    print("Executing %s version %s." % (__name__, __version__))
    b = BlkinfoProcessor()
    i = InteractiveDisplay(b)
    print(i.show_all_drives())
    print(i.show_attachable_drives())
    print(i.show_detachable_drives())
    print("sdf")

##################
# Common
##################

class SystemTool(object):
    def __init__(self, name, path):
        self.name = name
        self.path = path

    def check(self):
        check_executable(self.path)

    def call(self, argument_string):
        out = subprocess.run(self.path+" "+argument_string,
                             shell=True,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             check=True )
        out.check_returncode()
        check_state(out.stderr is None or len(out.stderr) == 0, "The following error occured: {}", out.stderr)
        return out

    def stdout(self, argument_string, sep='\\n'):
        out = self.call(argument_string)
        return out.stdout

class BlkinfoProcessor(object):

    def __init__(self, exe_path='/bin/lsblk'):
        self.lsblk = SystemTool('lsblk', exe_path)
        self.lsblk.check()

    def get_disks(self, mounted=None):
        blockdevices = self.__get_all_info()['blockdevices']
        return list(
            filter(lambda x: BlkinfoProcessor.__filter(x, mounted),
                   map(lambda x: DiskInfo(x), blockdevices)))

    def __get_all_info(self):
        # out = self.lsblk.stdout("-O --json")
        out = self.lsblk.stdout("-o FSTYPE,PARTLABEL,UUID,PARTUUID,LABEL,SIZE,MOUNTPOINT,OWNER,KNAME --json")
        return json.loads(out)

    @classmethod
    def __filter(cls, diskInfo, mounted):
        return BlkinfoProcessor.__is_correct_fstype(diskInfo) and BlkinfoProcessor.__is_processable(diskInfo, mounted)

    @classmethod
    def __is_correct_fstype(cls, diskInfo):
        fstype = diskInfo.fstype
        return fstype is not None and fstype != 'squashfs'

    @classmethod
    def __is_processable(cls, diskInfo, mounted):
        return mounted is None or diskInfo.is_mounted() == mounted

class DiskInfo:

    def __init__(self, data):
        self._data = data

    @property
    def fstype(self):
        return self._data['fstype']

    @property
    def kname(self):
        return self._data['kname']

    @property
    def mountpoint(self):
        return self._data['mountpoint']

    @property
    def partuuid(self):
        return self._data['partuuid']

    @property
    def size(self):
        return self._data['size']

    @property
    def label(self):
        return self._data['label']

    @property
    def uuid(self):
        return self._data['uuid']

    def is_mounted(self):
        return self.mountpoint is not None

class InteractiveDisplay:

    def __init__(self, blkinfoProcessor):
        self.__blkinfoProcessor = blkinfoProcessor

    def show_all_drives(self):
        return self.__get_options(mounted=None)

    def show_attachable_drives(self):
        return self.__get_options(mounted=False)

    def show_detachable_drives(self):
        return self.__get_options(mounted=True)

    def __get_options(self, mounted):
        header = ['id', 'kname', 'uuid', 'size', 'fstype', 'label', 'mountpoint']
        unmounted_disks = self.__blkinfoProcessor.get_disks(mounted=mounted)
        rows = []
        count = 0
        for x in unmounted_disks:
            count = count + 1
            rows.append([count, x.kname, x.uuid, x.size, x.fstype, x.label, x.mountpoint])
        return tabulate(rows, header)



def main2():
    print("Executing %s version %s." % (__name__, __version__))
    if not os.geteuid() == 0:
        sys.exit("\n[ERROR]: Only root can run this script\n")
    options = getOptions()

