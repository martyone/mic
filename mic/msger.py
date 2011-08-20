#!/usr/bin/python -tt
# vim: ai ts=4 sts=4 et sw=4

#    Copyright (c) 2009 Intel Corporation
#
#    This program is free software; you can redistribute it and/or modify it
#    under the terms of the GNU General Public License as published by the Free
#    Software Foundation; version 2 of the License
#
#    This program is distributed in the hope that it will be useful, but
#    WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
#    or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
#    for more details.
#
#    You should have received a copy of the GNU General Public License along
#    with this program; if not, write to the Free Software Foundation, Inc., 59
#    Temple Place - Suite 330, Boston, MA 02111-1307, USA.

import os,sys
import re

__ALL__ = ['set_mode', 'set_loglevel', 'raw' 'debug', 'verbose', 'info', 'warning', 'error', 'ask']

# COLORs in ANSI
INFO_COLOR = 32 # green
WARN_COLOR = 33 # yellow
ERR_COLOR  = 31 # red
ASK_COLOR  = 34 # blue
NO_COLOR = 0

PREFIX_RE = re.compile('^<(.*?)>\s*(.*)')

INTERACTIVE = True

LOG_LEVELS = {
                'quiet': 0,
                'normal': 1,
                'verbose': 2,
                'debug': 3,
             }
LOG_LEVEL = 1

def _color_print(head, color, msg = None, stream = sys.stdout, level = 'normal'):

    if LOG_LEVELS[level] > LOG_LEVEL:
        # skip
        return

    colored = True
    if color == NO_COLOR or \
       not stream.isatty() or \
       os.getenv('ANSI_COLORS_DISABLED') is not None:
        colored = False

    if head.startswith('\r'):
        # need not \n at last
        newline = False
    else:
        newline = True

    if colored:
        head = '\033[%dm%s:\033[0m ' %(color, head)
        if not newline:
            # ESC cmd to clear line
            head = '\033[2K' + head
    else:
        if head:
            head += ': '

    if msg:
        stream.write('%s%s' % (head, msg))
        if newline:
            stream.write('\n')
    else:
        stream.write('%s ' % head)

    stream.flush()

def _color_perror(head, color, msg, level = 'normal'):
    _color_print(head, color, msg, sys.stderr, level)

def _split_msg(head, msg):
    if msg.startswith('\n'):
        # means print \n at first
        msg = msg.lstrip()
        head = '\n' + head

    elif msg.startswith('\r'):
        # means print \r at first
        msg = msg.lstrip()
        head = '\r' + head

    m = PREFIX_RE.match(msg)
    if m:
        head += ' <%s>' % m.group(1)
        msg = m.group(2)

    return head, msg

def set_loglevel(level):
    global LOG_LEVEL
    if level not in LOG_LEVELS:
        # no effect
        return

    LOG_LEVEL = LOG_LEVELS[level]

def set_mode(interactive):
    global INTERACTIVE
    if interactive:
        INTERACTIVE = True
    else:
        INTERACTIVE = False

def raw(msg):
    head, msg = _split_msg('', msg)
    _color_print(head, NO_COLOR, msg)

def info(msg):
    head, msg = _split_msg('Info', msg)
    _color_print(head, INFO_COLOR, msg)

def verbose(msg):
    head, msg = _split_msg('Verbose', msg)
    _color_print(head, INFO_COLOR, msg, level = 'verbose')

def warning(msg):
    head, msg = _split_msg('Warning', msg)
    _color_perror(head, WARN_COLOR, msg)

def debug(msg):
    head, msg = _split_msg('Debug', msg)
    _color_perror(head, ERR_COLOR, msg, level = 'debug')

def error(msg):
    head, msg = _split_msg('Error', msg)
    _color_perror(head, ERR_COLOR, msg)
    sys.exit(1)

def ask(msg, default=True):
    _color_print('Q', ASK_COLOR, '')
    try:
        if default:
            msg += '(Y/n) '
        else:
            msg += '(y/N) '
        if INTERACTIVE:
            repl = raw_input(msg)
            if repl.lower() == 'y':
                return True
            elif repl.lower() == 'n':
                return False
            else:
                return default

        else:
            sys.stdout.write('%s ' % msg)
            if default:
                sys.stdout.write('Y\n')
            else:
                sys.stdout.write('N\n')
            return default
    except KeyboardInterrupt:
        sys.stdout.write('\n')
        sys.exit(2)