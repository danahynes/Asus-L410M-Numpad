#!/usr/bin/env python3
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
import logging
import os
import sys
import time

# set up logging
logging.basicConfig(filename = '/var/log/asus_l410m_numpad.log',
    level = logging.DEBUG, format = '%(asctime)s - %(message)s')

# just let users know its starting
logging.debug('---------------------------------------------------------------')
logging.debug('Starting script')

#-------------------------------------------------------------------------------
# helper functions
#-------------------------------------------------------------------------------

# returns a libevdev device for the given name
def get_device(device_name):

    # assume no device
    device_found = False
    device_id = -1
    device = None

    # check if file exists
    if os.path.exists('/proc/bus/input/devices'):

        # read file
        with open('/proc/bus/input/devices', 'r') as f:
            lines = f.readlines()

            # walk through the file
            for line in lines:
                if device_name.upper() in line.upper():

                    # keep walking
                    device_found = True
                    continue

                # found keyboard
                if device_found:

                    # keep walking to find handlers line
                    if 'HANDLERS' in line.upper():

                        # get array of handlers
                        handlers = line.split('=')[-1]

                        # get array of handlers
                        handler_array = handlers.split(' ')

                        # find event
                        for handler in handler_array:
                            if 'EVENT' in handler.upper():
                                event = handler.upper().split('EVENT')

                                # save it
                                device_id = event[-1]
                                break

                        # no more to do here
                        break

    # no device, no laundry
    if not device_found or device_id == -1:
        return None

    # try to connect to device
    if os.path.exists('/dev/input/event' + str(device_id)):

        # create a file descriptor (pipe) for the keyboard
        fd_device = open('/dev/input/event' + str(device_id), 'rb')

        # set file descriptor (pipe) to non-blocking
        try:
            fcntl.fcntl(fd_device, fcntl.F_SETFL, os.O_NONBLOCK)
        except ValueError as err:
            logging.debug(str(err))
            return None

        # get a device object (end point) for the file descriptor (pipe)
        try:
            device = libevdev.Device(fd_device)
        except libevdev.device.InvalidFileError as err:
            logging.debug(str(err))
            return None

        # return found (or not found) device
        return device

# returns the rect that the point is in, or None
def get_current_rect():

    # the default result is none
    result_rect = None

    # loop through all rects
    for rect in all_rects:

        # if pt in rect
        if (
            (rect[0] <= current_pt[0] <= rect[2]) and
            (rect[1] <= current_pt[1] <= rect[3])
        ):

            # the result rect
            result_rect = rect
            break

    # return result rect (or default none)
    return result_rect

# use numpad device to press all keys for rect
def send_keys_down():

    # if rect is valid
    if start_rect != None:
        list_size = len(start_rect)
        num_keys = (list_size - 4)
        rect_keys = start_rect[-num_keys:]

        # press all keys for rect
        for key in rect_keys:
            try:
                events = [
                    libevdev.InputEvent(key, 1),
                    libevdev.InputEvent(libevdev.EV_SYN.SYN_REPORT, 0)
                ]
                numpad.send_events(events)
            except OSError as err:
                logging.debug(str(err))

# use numpad device to release all keys for rect (in reverse order)
def send_keys_up_and_reset():

    # use glabal vars when assigning values
    global current_rect
    global current_pt
    global start_rect
    global start_numlock

    # if rect is valid
    if start_rect != None:
        list_size = len(start_rect)
        num_keys = (list_size - 4)
        rect_keys = start_rect[-num_keys:]

        # release all keys for rect
        for key in reversed(rect_keys):
            try:
                events = [
                    libevdev.InputEvent(key, 0),
                    libevdev.InputEvent(libevdev.EV_SYN.SYN_REPORT, 0)
                ]
                numpad.send_events(events)
            except OSError as err:
                logging.debug(str(err))

    # reset variables
    current_pt = [-1, -1]
    start_rect = None
    current_rect = None
    start_numlock = 0

# check if current_pt is in same rect
def check_same_rect_or_bail():

    # use glabal vars when assigning values
    global current_rect

    # are we really watching events?
    if current_rect == rect_numlock or numlock_state:

        # find out where the finger is
        current_rect = get_current_rect()

        # if finger is down and not in same rect
        if (current_rect != start_rect and current_rect != None and
                start_rect != None):

            # rekease the appropriate keys
            send_keys_up_and_reset()

# get current numlock state and grab/ungrab touchpad`
def check_numlock_state():

    global numlock_state

    # get initial numlock_state
    numlock_state = keyboard.value[libevdev.EV_LED.LED_NUML]

    # grab if on
    if numlock_state:
        touchpad.grab()

    # ungrab if off
    else:
        touchpad.ungrab()

#-------------------------------------------------------------------------------
# Initialize
#-------------------------------------------------------------------------------

# get keyboard
keyboard = get_device('KEYBOARD')

# no device, no laundry
if keyboard == None:
    logging.debug('Could not find keyboard, freaking out...')
    sys.exit(1)

# get touchpad
touchpad = get_device('TOUCHPAD')

# no device, no laundry
if touchpad == None:
    logging.debug('Could not find touchpad, freaking out...')
    sys.exit(1)

# retrieve touchpad dimensions
size_info_x = touchpad.absinfo[libevdev.EV_ABS.ABS_X]
min_x = size_info_x.minimum
max_x = size_info_x.maximum
size_info_y = touchpad.absinfo[libevdev.EV_ABS.ABS_Y]
min_y = size_info_y.minimum
max_y = size_info_y.maximum

# N.B. Not to scale, numlock rect is about half as wide as other columns, and
# about half as high as other rows. It overlaps in the x direction but not the
# y. All number rows are about equal, and all number columns are about equal.
# That means the numlock column is about 1/10 total width and all number columns
# are about 1/5 total width.
# And numlock row is about 1/9 total height and all number rows are about
# (total height - numlock height)/4 of total height.
# The size of the numlock rect was slightly inflated to adjust for fat fingers.
# |============================================================================|
# |                                                                |  numlock  |
# |----------------------------------------------------------------------------|
# |             |             |             |             |                    |
# |      7      |      8      |      9      |      /      |                    |
# |             |             |             |             |                    |
# |-------------------------------------------------------       backspace     |
# |             |             |             |             |                    |
# |      4      |      5      |      6      |      *      |                    |
# |             |             |             |             |                    |
# |----------------------------------------------------------------------------|
# |             |             |             |             |                    |
# |      1      |      2      |      3      |      -      |         %          |
# |             |             |             |             |                    |
# |----------------------------------------------------------------------------|
# |             |             |             |             |                    |
# |      0      |      .      |    Enter    |      +      |         =          |
# |             |             |             |             |                    |
# |============================================================================|

# get rect dimensions for toggle button
numlock_width = (max_x * 0.11)
numlock_height = (max_y * 0.13)
numlock_x = (max_x - numlock_width)
numlock_y = 0

# get col(x) dimensions for keys
# expressed as each col's x start
col_width = (max_x * 0.20)
cols = [
    0,
    (col_width * 1),
    (col_width * 2),
    (col_width * 3),
    (col_width * 4)
]

# get row(y) dimensions for keys
# expressed as each row's y start
row_height = ((max_y - numlock_height) * 0.25)
rows = [
    numlock_height,
    (numlock_height + (row_height * 1)),
    (numlock_height + (row_height * 2)),
    (numlock_height + (row_height * 3)),
]

# create a list of keys that the numpad supports
# N.B. order is inportant here to assign keys to rects
keys = [
    libevdev.EV_KEY.KEY_NUMLOCK,    # for toggle
    libevdev.EV_KEY.KEY_KP1,
    libevdev.EV_KEY.KEY_KP2,
    libevdev.EV_KEY.KEY_KP3,
    libevdev.EV_KEY.KEY_KP4,
    libevdev.EV_KEY.KEY_KP5,
    libevdev.EV_KEY.KEY_KP6,
    libevdev.EV_KEY.KEY_KP7,
    libevdev.EV_KEY.KEY_KP8,
    libevdev.EV_KEY.KEY_KP9,
    libevdev.EV_KEY.KEY_KP0,
    libevdev.EV_KEY.KEY_KPCOMMA,    # decimal
    libevdev.EV_KEY.KEY_KPENTER,
    libevdev.EV_KEY.KEY_KPSLASH,
    libevdev.EV_KEY.KEY_KPASTERISK,
    libevdev.EV_KEY.KEY_KPMINUS,
    libevdev.EV_KEY.KEY_KPPLUS,
    libevdev.EV_KEY.KEY_BACKSPACE,
    libevdev.EV_KEY.KEY_LEFTSHIFT,  # for percent (shift-5)
    libevdev.EV_KEY.KEY_5,          # for percent (shift-5)
    libevdev.EV_KEY.KEY_KPEQUAL
]

# rects for keys - rect = (x, y, (x + w), (y + h), libevdev.EV_KEY.KEY_*, ...)
rect_numlock =      [numlock_x, numlock_y,  (numlock_x + numlock_width),    (numlock_y + numlock_height),   keys[0]]
rect_1 =            [cols[0],   rows[2],    (cols[0] + col_width),          (rows[2] + row_height),         keys[1]]
rect_2 =            [cols[1],   rows[2],    (cols[1] + col_width),          (rows[2] + row_height),         keys[2]]
rect_3 =            [cols[2],   rows[2],    (cols[2] + col_width),          (rows[2] + row_height),         keys[3]]
rect_4 =            [cols[0],   rows[1],    (cols[0] + col_width),          (rows[1] + row_height),         keys[4]]
rect_5 =            [cols[1],   rows[1],    (cols[1] + col_width),          (rows[1] + row_height),         keys[5]]
rect_6 =            [cols[2],   rows[1],    (cols[2] + col_width),          (rows[1] + row_height),         keys[6]]
rect_7 =            [cols[0],   rows[0],    (cols[0] + col_width),          (rows[0] + row_height),         keys[7]]
rect_8 =            [cols[1],   rows[0],    (cols[1] + col_width),          (rows[0] + row_height),         keys[8]]
rect_9 =            [cols[2],   rows[0],    (cols[2] + col_width),          (rows[0] + row_height),         keys[9]]
rect_0 =            [cols[0],   rows[3],    (cols[0] + col_width),          (rows[3] + row_height),         keys[10]]
rect_comma =        [cols[1],   rows[3],    (cols[1] + col_width),          (rows[3] + row_height),         keys[11]]
rect_enter =        [cols[2],   rows[3],    (cols[2] + col_width),          (rows[3] + row_height),         keys[12]]
rect_slash =        [cols[3],   rows[0],    (cols[3] + col_width),          (rows[0] + row_height),         keys[13]]
rect_asterisk =     [cols[3],   rows[1],    (cols[3] + col_width),          (rows[1] + row_height),         keys[14]]
rect_minus =        [cols[3],   rows[2],    (cols[3] + col_width),          (rows[2] + row_height),         keys[15]]
rect_plus =         [cols[3],   rows[3],    (cols[3] + col_width),          (rows[3] + row_height),         keys[16]]
# backspace key is two rows high
rect_backspace =    [cols[4],   rows[0],    (cols[4] + col_width),          (rows[0] + (row_height * 2)),   keys[17]]
# precent needs two keys (shift and 5)
rect_percent =      [cols[4],   rows[2],    (cols[4] + col_width),          (rows[2] + row_height),         keys[18], keys[19]]
rect_equal =        [cols[4],   rows[3],    (cols[4] + col_width),          (rows[3] + row_height),         keys[20]]

# create array of recognized rects
all_rects = [
    rect_numlock,
    rect_1,
    rect_2,
    rect_3,
    rect_4,
    rect_5,
    rect_6,
    rect_7,
    rect_8,
    rect_9,
    rect_0,
    rect_comma,
    rect_enter,
    rect_slash,
    rect_asterisk,
    rect_minus,
    rect_plus,
    rect_backspace,
    rect_percent,
    rect_equal
]

# create a new keyboard device to send numpad events
dev_numpad = libevdev.Device()
dev_numpad.name = "Asus_L410M_Numpad"
for key in keys:
    dev_numpad.enable(key)
numpad = dev_numpad.create_uinput_device()

# constants
TOGGLE_HOLD_TIME = 2

# global variables
current_pt = [0, 0] # [x, y]
start_rect = None
current_rect = None
numlock_state = False
start_numlock = 0

# get initial numlock_state
check_numlock_state()

#-------------------------------------------------------------------------------
# Main loop
#-------------------------------------------------------------------------------

while True:

    # look at each event from keyboard
    for e in keyboard.events():

        # if it's the numlock key
        if e.matches(libevdev.EV_LED.LED_NUML):

            # get current numlock_state
            check_numlock_state()

    # look at each event from touchpad
    for e in touchpad.events():

        # move in x direction
        if e.matches(libevdev.EV_ABS.ABS_MT_POSITION_X):

            # save x position of finger
            current_pt[0] = e.value

            # check if finger moved out of rect
            check_same_rect_or_bail()

        # move in y direction
        elif e.matches(libevdev.EV_ABS.ABS_MT_POSITION_Y):

            # save y position of finger
            current_pt[1] = e.value

            # check if finger moved out of rect
            check_same_rect_or_bail()

        # if it was a one finger event
        elif e.matches(libevdev.EV_KEY.BTN_TOOL_FINGER):

            # one finger down
            if e.value == 1:

                # find out where the finger went down
                start_rect = get_current_rect()
                current_rect = start_rect

                # if finger in numlock area
                if start_rect == rect_numlock:
                    start_numlock = time.time()

                # finger is somewhere else
                else:

                    # if numlock on, send number key(s)
                    if numlock_state:
                        send_keys_down()
                        #touchpad.grab()

            # one finger up
            elif e.value == 0:

                # release the hounds! (er, keys)
                send_keys_up_and_reset()
                #touchpad.ungrab()

#-------------------------------------------------------------------------------

        # more than one finger event
        # elif (
        #     e.matches(libevdev.EV_KEY.BTN_TOOL_DOUBLETAP) or
        #     e.matches(libevdev.EV_KEY.BTN_TOOL_TRIPLETAP) or
        #     e.matches(libevdev.EV_KEY.BTN_TOOL_QUADTAP) or
        #     e.matches(libevdev.EV_KEY.BTN_TOOL_QUINTTAP)
        # ):
        #
        #     # if numpad is on
        #     if numlock_state:
        #
        #         # reset everything
        #         send_keys_up_and_reset()
        #         touchpad.ungrab()

#-------------------------------------------------------------------------------

    # N.B. this code is called every time through the loop
    if (

        # if finger is in numlock rect
        start_rect == rect_numlock and

        # and hasn't moved out
        current_rect == rect_numlock and

        # and if it was held long enough
        ((time.time() - start_numlock) >= TOGGLE_HOLD_TIME)
    ):

        # send the numlock key
        send_keys_down()

        # rekease the numlock key
        send_keys_up_and_reset()

    # give somebody else a chance will ya!
    time.sleep(0.1)

# ungrab touchpad if it was grabbed
touchpad.ungrab()

# -)
