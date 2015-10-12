# This file is part of Viper - https://github.com/viper-framework/viper
# See the file 'LICENSE' for copying permission.

import os
import sys
import math
import string
import hashlib

from viper.common.out import *

try:
    import magic
except ImportError:
    pass

# Taken from the Python Cookbook.
def path_split_all(path):
    allparts = []
    while 1:
        parts = os.path.split(path)
        if parts[0] == path:
            allparts.insert(0, parts[0])
            break
        elif parts[1] == path:
            allparts.insert(0, parts[1])
            break
        else:
            path = parts[0]
            allparts.insert(0, parts[1])

    return allparts

# The following couple of functions are redundant.
# TODO: find a way to better integrate these generic methods
# with the ones available in the File class.
def get_type(data):
    try:
        ms = magic.open(magic.MAGIC_NONE)
        ms.load()
        file_type = ms.buffer(data)
    except:
        try:
            file_type = magic.from_buffer(data)
        except:
            return ''
    finally:
        try:
            ms.close()
        except:
            pass

    return file_type

def get_md5(data):
    md5 = hashlib.md5()
    md5.update(data)
    return md5.hexdigest()

def string_clean(line):
    try:
        return [x for x in line if x in string.printable]
    except:
        return line

# Snippet taken from:
# https://gist.github.com/sbz/1080258
def hexdump(src, length=16, maxlines=None):
    FILTER = ''.join([(len(repr(chr(x))) == 3) and chr(x) or '.' for x in range(256)])
    lines = []
    for c in range(0, len(src), length):
        chars = src[c:c+length]
        hex = ' '.join(["%02x" % ord(x) for x in chars])
        printable = ''.join(["%s" % ((ord(x) <= 127 and FILTER[ord(x)]) or '.') for x in chars])
        lines.append("%04x  %-*s  %s\n" % (c, length*3, hex, printable))

        if maxlines:
            if len(lines) == maxlines:
                break

    return ''.join(lines)

# Snippet taken from:
# http://stackoverflow.com/questions/5194057/better-way-to-convert-file-sizes-in-python
def convert_size(size):
   size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
   if (size>0):
        i = int(math.floor(math.log(size,1024)))
        p = math.pow(1024,i)
        s = round(size/p,2)
        if (s > 0):
                return '%s %s' % (s,size_name[i])
   else:
       return '0B'

def print_output(output, filename=None):
	if not output:
		return
	if filename:
		with open(filename.strip(), 'a') as out:
			for entry in output:
				if entry['type'] == 'info':
					out.write('[*] {0}\n'.format(entry['data']))
				elif entry['type'] == 'item':
					out.write('  [-] {0}\n'.format(entry['data']))
				elif entry['type'] == 'warning':
					out.write('[!] {0}\n'.format(entry['data']))
				elif entry['type'] == 'error':
					out.write('[!] {0}\n'.format(entry['data']))
				elif entry['type'] == 'success':
					out.write('[+] {0}\n'.format(entry['data']))
				elif entry['type'] == 'table':
					out.write(str(table(
						header=entry['data']['header'],
						rows=entry['data']['rows']
					)))
					out.write('\n')
				else:
					out.write('{0}\n'.format(entry['data']))
		print_success("Output written to {0}".format(filename))
	else:
		for entry in output:
			if entry['type'] == 'info':
				print_info(entry['data'])
			elif entry['type'] == 'item':
				print_item(entry['data'])
			elif entry['type'] == 'warning':
				print_warning(entry['data'])
			elif entry['type'] == 'error':
				print_error(entry['data'])
			elif entry['type'] == 'success':
				print_success(entry['data'])
			elif entry['type'] == 'table':
				print(table(
					header=entry['data']['header'],
					rows=entry['data']['rows']
				))
			else:
				print(entry['data'])
