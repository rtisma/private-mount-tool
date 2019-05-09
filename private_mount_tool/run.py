# -*- coding: utf-8 -*-

__version__ = "0.1.0"


import sys
import os
import argparse
import subprocess
import json
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
    b = Blkinfo()
    d = b.get_disks()
    print(d)
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

class Blkinfo(object):

    def __init__(self, exe_path='/bin/lsblk'):
        self.lsblk = SystemTool('lsblk', exe_path)
        self.lsblk.check()

    def get_all_info(self):
        # out = self.lsblk.stdout("-O --json")
        out = self.lsblk.stdout("-o FSTYPE,PARTLABEL,UUID,PARTUUID,LABEL,SIZE,MOUNTPOINT,OWNER --json")
        return json.loads(out)

    def get_disks(self):
        j = self.get_all_info()['blockdevices']

        filtered_list = []
        for d in j:
            if d['fstype'] is not None and d['fstype'] != 'squashfs':
                filtered_list.append(d)
        return filtered_list

class DiskInfo:
    fstype = None
    partlabel = None
    uuid = None
    label = None
    partuuid = None
    size = None
    mountpoint = None

    def is_mounted(self):
        return self.mountpoint is not None



def main2():
    print("Executing %s version %s." % (__name__, __version__))
    if not os.geteuid() == 0:
        sys.exit("\n[ERROR]: Only root can run this script\n")
    options = getOptions()

