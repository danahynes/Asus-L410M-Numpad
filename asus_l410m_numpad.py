#------------------------------------------------------------------------------#
# Filename: asus_l410m_numpad.py                                 /          \  #
# Project : Asus_L410M_Numpad                                   |     ()     | #
# Date    : 02/17/2021                                          |            | #
# Author  : Dana Hynes                                          |   \____/   | #
# License : WTFPLv2                                              \          /  #
#------------------------------------------------------------------------------#
# Inspired by https://gitlab.com/Thraen/gx735_touchpad_numpad                  #
#------------------------------------------------------------------------------#

#imports
import fcntl
import libevdev
import os
import re
import subprocess
import sys
import time

# get touchpad event handler
touchpad_found = False
if os.path.exists('/proc/bus/input/devices'):
    with open('/proc/bus/input/devices', 'r') as f:
        lines = f.readlines()

        # walk through the file
        for line in lines:
            if 'TOUCHPAD' in line.upper():
                touchpad_found = True
                continue
            if touchpad_found:
                if 'Handlers=' in line:
                    parts = line.split(' ')
                    event = parts[2]
                    event = event.split('event')
                    event = event[1]
                    touchpad_id = event
                    break

# no touchpad, no laundry
if not touchpad_found:
    print('Touchpad not found, freaking out...')
    sys.exit(1)

# try to connect to touchpad
if os.path.exists('/dev/input/event' + str(touchpad_id)):

    # create a file descriptor (pipe) for the touchpad
    fd_touchpad = open('/dev/input/event' + str(touchpad_id), 'rb')

    # set file descriptor (pipe) to non-blocking
    fcntl.fcntl(fd_touchpad, fcntl.F_SETFL, os.O_NONBLOCK)

    # get a device object (end point) for the file descriptor (pipe)
    touchpad = libevdev.Device(fd_touchpad)

# no touchpad, no laundry
else:
    print('Could not open connection to touchpad, freaking out...')
    sys.exit(1)

# retrieve touchpad dimensions
info = touchpad.absinfo[libevdev.EV_ABS.ABS_X]
(min_x, max_x) = (info.minimum, info.maximum)
info = touchpad.absinfo[libevdev.EV_ABS.ABS_Y]
(min_y, max_y) = (info.minimum, info.maximum)

# create a new keyboard device to send numpad events
dev_fake_kbd = libevdev.Device()
dev_fake_kbd.name = "Asus_L410M_Numpad"
dev_fake_kbd.enable(libevdev.EV_KEY.KEY_KP1)
dev_fake_kbd.enable(libevdev.EV_KEY.KEY_KP2)
dev_fake_kbd.enable(libevdev.EV_KEY.KEY_KP3)
dev_fake_kbd.enable(libevdev.EV_KEY.KEY_KP4)
dev_fake_kbd.enable(libevdev.EV_KEY.KEY_KP5)
dev_fake_kbd.enable(libevdev.EV_KEY.KEY_KP6)
dev_fake_kbd.enable(libevdev.EV_KEY.KEY_KP7)
dev_fake_kbd.enable(libevdev.EV_KEY.KEY_KP8)
dev_fake_kbd.enable(libevdev.EV_KEY.KEY_KP9)
dev_fake_kbd.enable(libevdev.EV_KEY.KEY_KP0)
dev_fake_kbd.enable(libevdev.EV_KEY.KEY_KPCOMMA)    # decimal
dev_fake_kbd.enable(libevdev.EV_KEY.KEY_KPENTER)
dev_fake_kbd.enable(libevdev.EV_KEY.KEY_KPSLASH)
dev_fake_kbd.enable(libevdev.EV_KEY.KEY_KPASTERISK)
dev_fake_kbd.enable(libevdev.EV_KEY.KEY_KPMINUS)
dev_fake_kbd.enable(libevdev.EV_KEY.KEY_KPPLUS)
dev_fake_kbd.enable(libevdev.EV_KEY.KEY_BACKSPACE)
dev_fake_kbd.enable(libevdev.EV_KEY.KEY_LEFTSHIFT)  # for percent (shift-5)
dev_fake_kbd.enable(libevdev.EV_KEY.KEY_5)          # for percent (shift-5)
dev_fake_kbd.enable(libevdev.EV_KEY.KEY_KPEQUAL)
dev_fake_kbd.enable(libevdev.EV_KEY.KEY_NUMLOCK)    # for toggle
fake_kbd = dev_fake_kbd.create_uinput_device()

# helper functions
def ptInRect(pt, rect):
    if (rect[0] <= pt[0] <= rect[2]) and (rect[1] <= pt[1] <= rect[3]):
        return True
    else:
        return False

# global variables
current_x = 0
current_y = 0
pt = (0, 0)
toggle = False
start_time = 0
shift = False
value = 0

# get numlock state
numlock = False
x = subprocess.check_output('xset q | grep LED', shell=True)[65]
if (x == 50):
    numlock = True

# sync numlock state with touchpad
if numlock:
    touchpad.grab()
else:
    touchpad.ungrab()

# get rect dimensions for toggle button
toggle_w = (max_x / 10)
toggle_h = (max_y / 9)
toggle_x = (max_x - toggle_w)
toggle_y = 0
toggle_rect = (toggle_x, toggle_y, (toggle_x + toggle_w), (toggle_y + toggle_h))

# get col(x) dimensions for keys and toggle
# expressed as each col's x start
col_width = (max_x / 5)
col_0 = 0
col_1 = (col_0 + col_width)
col_2 = (col_1 + col_width)
col_3 = (col_2 + col_width)
col_4 = (col_3 + col_width)
cols = [
    col_0,
    col_1,
    col_2,
    col_3,
    col_4
]

# get row(y) dimensions for keys and toggle
# expressed as each row's y start
row_height = ((max_y - toggle_h) / 4)
row_0 = toggle_h
row_1 = (row_0 + row_height)
row_2 = (row_1 + row_height)
row_3 = (row_2 + row_height)
rows = [
    row_0,
    row_1,
    row_2,
    row_3
]

# rects for keys - rect = (x, y, (x + w), (y + h))
rect_1 =            (cols[0], rows[2], cols[0] + col_width, rows[2] + row_height)
rect_2 =            (cols[1], rows[2], cols[1] + col_width, rows[2] + row_height)
rect_3 =            (cols[2], rows[2], cols[2] + col_width, rows[2] + row_height)
rect_4 =            (cols[0], rows[1], cols[0] + col_width, rows[1] + row_height)
rect_5 =            (cols[1], rows[1], cols[1] + col_width, rows[1] + row_height)
rect_6 =            (cols[2], rows[1], cols[2] + col_width, rows[1] + row_height)
rect_7 =            (cols[0], rows[0], cols[0] + col_width, rows[0] + row_height)
rect_8 =            (cols[1], rows[0], cols[1] + col_width, rows[0] + row_height)
rect_9 =            (cols[2], rows[0], cols[2] + col_width, rows[0] + row_height)
rect_0 =            (cols[0], rows[3], cols[0] + col_width, rows[3] + row_height)
rect_comma =        (cols[1], rows[3], cols[1] + col_width, rows[3] + row_height)
rect_enter =        (cols[2], rows[3], cols[2] + col_width, rows[3] + row_height)
rect_slash =        (cols[3], rows[0], cols[3] + col_width, rows[0] + row_height)
rect_asterisk =     (cols[3], rows[1], cols[3] + col_width, rows[1] + row_height)
rect_minus =        (cols[3], rows[2], cols[3] + col_width, rows[2] + row_height)
rect_plus =         (cols[3], rows[3], cols[3] + col_width, rows[3] + row_height)
# backspace key is two rows high
rect_backspace =    (cols[4], rows[0], cols[4] + col_width, rows[0] + (row_height * 2))
rect_percent =      (cols[4], rows[2], cols[4] + col_width, rows[2] + row_height)
rect_equals =       (cols[4], rows[3], cols[4] + col_width, rows[3] + row_height)

# main loop
while True:

    # look at each event from touchpad
    for e in touchpad.events():

        # get the current touch position
        if e.matches(libevdev.EV_ABS.ABS_MT_POSITION_X):
            current_x = e.value
            pt = (current_x, current_y)
            if toggle and not ptInRect(pt, toggle_rect):
                toggle = False

        if e.matches(libevdev.EV_ABS.ABS_MT_POSITION_Y):
            current_y = e.value
            pt = (current_x, current_y)
            if toggle and not ptInRect(pt, toggle_rect):
                toggle = False

        # if it was a finger event
        if e.matches(libevdev.EV_KEY.BTN_TOOL_FINGER):

            # start of touch
            if (e.value == 1):

                # save current as point
                pt = (current_x, current_y)

                # if touch starts as a toggle
                if ptInRect(pt, toggle_rect):
                     toggle = True
                     start_time = time.time()

                # if we are using numpad
                if numlock:

                    # reset value
                    shift = False
                    value = 0

                    # find the key we pressed on
                    if ptInRect(pt, rect_1):
                        value = libevdev.EV_KEY.KEY_KP1
                    if ptInRect(pt, rect_2):
                        value = libevdev.EV_KEY.KEY_KP2
                    if ptInRect(pt, rect_3):
                        value = libevdev.EV_KEY.KEY_KP3
                    if ptInRect(pt, rect_4):
                        value = libevdev.EV_KEY.KEY_KP4
                    if ptInRect(pt, rect_5):
                        value = libevdev.EV_KEY.KEY_KP5
                    if ptInRect(pt, rect_6):
                        value = libevdev.EV_KEY.KEY_KP6
                    if ptInRect(pt, rect_7):
                        value = libevdev.EV_KEY.KEY_KP7
                    if ptInRect(pt, rect_8):
                        value = libevdev.EV_KEY.KEY_KP8
                    if ptInRect(pt, rect_9):
                        value = libevdev.EV_KEY.KEY_KP9
                    if ptInRect(pt, rect_0):
                        value = libevdev.EV_KEY.KEY_KP0
                    if ptInRect(pt, rect_comma):
                        value = libevdev.EV_KEY.KEY_KPCOMMA
                    if ptInRect(pt, rect_enter):
                        value = libevdev.EV_KEY.KEY_KPENTER
                    if ptInRect(pt, rect_slash):
                        value = libevdev.EV_KEY.KEY_KPSLASH
                    if ptInRect(pt, rect_asterisk):
                        value = libevdev.EV_KEY.KEY_KPASTERISK
                    if ptInRect(pt, rect_minus):
                        value = libevdev.EV_KEY.KEY_KPMINUS
                    if ptInRect(pt, rect_plus):
                        value = libevdev.EV_KEY.KEY_KPPLUS
                    if ptInRect(pt, rect_backspace):
                        value = libevdev.EV_KEY.KEY_BACKSPACE
                    if ptInRect(pt, rect_percent):

                        # percent key needs shift + 5
                        shift = True
                        value = libevdev.EV_KEY.KEY_5
                    if ptInRect(pt, rect_equals):
                        value = libevdev.EV_KEY.KEY_KPEQUAL

                    # if we pressed on a known key
                    if (value != 0):

                        # press shift if we need percent sign
                        if shift:
                            try:
                                events = [
                                    libevdev.InputEvent(libevdev.EV_KEY.KEY_LEFTSHIFT, 1),
                                    libevdev.InputEvent(libevdev.EV_SYN.SYN_REPORT, 0)
                                ]
                                fake_kbd.send_events(events)
                            except OSError as e:
                                pass

                        # press the appropriate key
                        try:
                            events = [
                                libevdev.InputEvent(value, 1),
                                libevdev.InputEvent(libevdev.EV_SYN.SYN_REPORT, 0)
                            ]
                            fake_kbd.send_events(events)
                        except OSError as e:
                            pass

            # end of touch
            if (e.value == 0):

                # if a key was pressed
                if (value != 0):

                    # release key
                    try:
                        events = [
                            libevdev.InputEvent(value, 0),
                            libevdev.InputEvent(libevdev.EV_SYN.SYN_REPORT, 0)
                        ]
                        fake_kbd.send_events(events)
                    except OSError as e:
                        pass

                    # release shift key if it was the percent
                    if shift:
                        try:
                            events = [
                                libevdev.InputEvent(libevdev.EV_KEY.KEY_LEFTSHIFT, 0),
                                libevdev.InputEvent(libevdev.EV_SYN.SYN_REPORT, 0)
                            ]
                            fake_kbd.send_events(events)
                        except OSError as e:
                            pass

                # clear flags and value
                toggle = False
                start_time = 0
                shift = False
                value = 0

        # N.B. this block matches ANY event

        # if the tap started at the toggle switch
        if toggle:

            # if it was held long enough
            if ((time.time() - start_time) >= 2):

                # reset flag
                toggle = False
                start_time = 0

                # toggle state
                numlock = not numlock

                # grab or ungrab touchpad
                if numlock:
                    touchpad.grab()
                else:
                    touchpad.ungrab()

                # send numlock key for indicator
                try:
                    events = [
                        libevdev.InputEvent(libevdev.EV_KEY.KEY_NUMLOCK, 1),
                        libevdev.InputEvent(libevdev.EV_SYN.SYN_REPORT, 0)
                    ]
                    fake_kbd.send_events(events)
                    events = [
                        libevdev.InputEvent(libevdev.EV_KEY.KEY_NUMLOCK, 0),
                        libevdev.InputEvent(libevdev.EV_SYN.SYN_REPORT, 0)
                    ]
                    fake_kbd.send_events(events)
                except OSError as e:
                    pass


    # don't use all cpu time!
    time.sleep(0.1)

# close file descriptor
fd_touchpad.close()

# -)
