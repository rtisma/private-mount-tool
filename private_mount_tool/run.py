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
    print(i.get_mount_options())
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
        s1 = map(lambda x: DiskInfo(x), blockdevices)
        s2 = filter(lambda x: BlkinfoProcessor.__is_processable(x.fstype), s1)
        s3 = filter(lambda x: mounted is None or x.is_mounted() is mounted, s2)
        return list(s3)

    def __get_all_info(self):
        # out = self.lsblk.stdout("-O --json")
        out = self.lsblk.stdout("-o FSTYPE,PARTLABEL,UUID,PARTUUID,LABEL,SIZE,MOUNTPOINT,OWNER,NAME --json")
        return json.loads(out)

    @classmethod
    def __is_processable(cls, fstype):
        return fstype is not None and fstype != 'squashfs'

class DiskInfo:

    def __init__(self, data):
        self._data = data

    @property
    def fstype(self):
        return self._data['fstype']

    @property
    def name(self):
        return self._data['name']

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

    def get_mount_options(self):
        header = ['id', 'name', 'uuid', 'size', 'fstype', 'label' ]
        unmounted_disks = self.__blkinfoProcessor.get_disks(mounted=False)
        rows = []
        count = 0
        for x in unmounted_disks:
            count = count + 1
            rows.append([count, x.name, x.uuid, x.size, x.fstype, x.label])
        return tabulate(rows, header)



def main2():
    print("Executing %s version %s." % (__name__, __version__))
    if not os.geteuid() == 0:
        sys.exit("\n[ERROR]: Only root can run this script\n")
    options = getOptions()

