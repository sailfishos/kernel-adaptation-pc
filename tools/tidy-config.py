#! /usr/bin/python

# Reduce a defconfig file to the minimum needed to produce an identical config.
# Run this from the kernel toplevel directory.
# Usage:
#    python ../tools/tidy-config.py SRCARCH ARCH
# (example arguments: x86 i386)
# WARNING: make a backup of the defconfig file first.

import sys
import os.path
import subprocess

NULL=open("/dev/null", "w")

def make_config(srcarch, arch):
    subprocess.check_call(["make", "SRCARCH=" + srcarch, "ARCH=" + arch, "defconfig"], stdout=NULL)
    return open(".config").read()

def shorten_defconfig(srcarch, arch, defconfig_fname, good_config):
    defconfig_lines = open(defconfig_fname).readlines()
    defconfig_keep = []
    for i in range(len(defconfig_lines)):
        print "Testing " + defconfig_lines[i].rstrip("\n") + " ... ",
        new_defconfig = defconfig_keep + defconfig_lines[i+1:]
        open(defconfig_fname, "w").writelines(new_defconfig)
        if make_config(srcarch, arch) != good_config:
            defconfig_keep.append(defconfig_lines[i])
            print "keep"
        else:
            print
    open(defconfig_fname, "w").writelines(defconfig_keep)

def main(argv):
    if len(argv) != 3:
        print ("Usage: %s srcarch arch\n" % argv[0])
        return 2
    srcarch = argv[1]
    arch = argv[2]
    defconfig_fname = "arch/%s/configs/%s_defconfig" % (srcarch, arch)
    if not os.path.exists(defconfig_fname):
        print ("defconfig not found: %s" % defconfig_fname)

    good_config = make_config(srcarch, arch)
    shorten_defconfig(srcarch, arch, defconfig_fname, good_config)

if __name__ == "__main__":
    sys.exit(main(sys.argv))
