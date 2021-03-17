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

# get keyboard event handler
keyboard_found = False
keyboard_id = -1
keyboard = None

# check if file exists
if os.path.exists('/proc/bus/input/devices'):

    # read file
    with open('/proc/bus/input/devices', 'r') as f:
        lines = f.readlines()

        # walk through the file
        for line in lines:
            if 'KEYBOARD' in line.upper():

                # keep walking
                keyboard_found = True
                continue

            # found keyboard
            if keyboard_found:

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
                            keyboard_id = event[-1]
                            break

                    # no more to do here
                    break

# no keyboard, no laundry
if not keyboard_found or keyboard_id == -1:
    logging.debug('Keyboard not found, freaking out...')
    sys.exit(1)

# try to connect to keyboard
if os.path.exists('/dev/input/event' + str(keyboard_id)):

    # create a file descriptor (pipe) for the keyboard
    fd_keyboard = open('/dev/input/event' + str(keyboard_id), 'rb')

    # set file descriptor (pipe) to non-blocking
    try:
        fcntl.fcntl(fd_keyboard, fcntl.F_SETFL, os.O_NONBLOCK)
    except ValueError as err:
        pass

    # get a device object (end point) for the file descriptor (pipe)
    try:
        keyboard = libevdev.Device(fd_keyboard)
    except libevdev.device.InvalidFileError as err:
        pass

# no keyboard, no laundry
if keyboard == None:
    logging.debug('Could not open connection to keyboard, freaking out...')
    sys.exit(1)

# get touchpad
touchpad_found = False
touchpad_id = -1
touchpad = None

# check if file exists
if os.path.exists('/proc/bus/input/devices'):

    # read file
    with open('/proc/bus/input/devices', 'r') as f:
        lines = f.readlines()

        # walk through the file to find touchpad
        for line in lines:
            if 'TOUCHPAD' in line.upper():

                # keep walking
                touchpad_found = True
                continue

            # found touchpad device
            if touchpad_found:

                # keep walking to find handlers line
                if 'HANDLERS' in line.upper():

                    # save everything after equals sign
                    handlers = line.split('=')[-1]

                    # get array of handlers
                    handler_array = handlers.split(' ')

                    # find event
                    for handler in handler_array:
                        if 'EVENT' in handler.upper():
                            event = handler.upper().split('EVENT')

                            # save it
                            touchpad_id = event[-1]
                            break

                    # no more to do here
                    break

# no touchpad, no laundry
if not touchpad_found or touchpad_id == -1:
    logging.debug('Touchpad not found, freaking out...')
    sys.exit(1)

# try to connect to touchpad
if os.path.exists('/dev/input/event' + str(touchpad_id)):

    # create a file descriptor (pipe) for the touchpad
    fd_touchpad = open('/dev/input/event' + str(touchpad_id), 'rb')

    # set file descriptor (pipe) to non-blocking
    try:
        fcntl.fcntl(fd_touchpad, fcntl.F_SETFL, os.O_NONBLOCK)
    except ValueError as err:
        pass

    # get a device object (end point) for the file descriptor (pipe)
    try:
        touchpad = libevdev.Device(fd_touchpad)
    except libevdev.device.InvalidFileError as err:
        pass

# no touchpad, no laundry
if touchpad == None:
    logging.debug('Could not open connection to touchpad, freaking out...')
    sys.exit(1)

# retrieve touchpad dimensions
size_info_x = touchpad.absinfo[libevdev.EV_ABS.ABS_X]
(min_x, max_x) = (size_info_x.minimum, size_info_x.maximum)
size_info_y = touchpad.absinfo[libevdev.EV_ABS.ABS_Y]
(min_y, max_y) = (size_info_y.minimum, size_info_y.maximum)

# create a new keyboard device to send numpad events
dev_numpad = libevdev.Device()
dev_numpad.name = "Asus_L410M_Numpad"
dev_numpad.enable(libevdev.EV_KEY.KEY_KP1)
dev_numpad.enable(libevdev.EV_KEY.KEY_KP2)
dev_numpad.enable(libevdev.EV_KEY.KEY_KP3)
dev_numpad.enable(libevdev.EV_KEY.KEY_KP4)
dev_numpad.enable(libevdev.EV_KEY.KEY_KP5)
dev_numpad.enable(libevdev.EV_KEY.KEY_KP6)
dev_numpad.enable(libevdev.EV_KEY.KEY_KP7)
dev_numpad.enable(libevdev.EV_KEY.KEY_KP8)
dev_numpad.enable(libevdev.EV_KEY.KEY_KP9)
dev_numpad.enable(libevdev.EV_KEY.KEY_KP0)
dev_numpad.enable(libevdev.EV_KEY.KEY_KPCOMMA)    # decimal
dev_numpad.enable(libevdev.EV_KEY.KEY_KPENTER)
dev_numpad.enable(libevdev.EV_KEY.KEY_KPSLASH)
dev_numpad.enable(libevdev.EV_KEY.KEY_KPASTERISK)
dev_numpad.enable(libevdev.EV_KEY.KEY_KPMINUS)
dev_numpad.enable(libevdev.EV_KEY.KEY_KPPLUS)
dev_numpad.enable(libevdev.EV_KEY.KEY_BACKSPACE)
dev_numpad.enable(libevdev.EV_KEY.KEY_LEFTSHIFT)  # for percent (shift-5)
dev_numpad.enable(libevdev.EV_KEY.KEY_5)          # for percent (shift-5)
dev_numpad.enable(libevdev.EV_KEY.KEY_KPEQUAL)
dev_numpad.enable(libevdev.EV_KEY.KEY_NUMLOCK)    # for toggle
numpad = dev_numpad.create_uinput_device()

# get rect dimensions for toggle button
toggle_w = (max_x * 0.10)
toggle_h = (max_y * 0.12)
toggle_x = (max_x - toggle_w)
toggle_y = 0
toggle_rect = (toggle_x, toggle_y, (toggle_x + toggle_w), (toggle_y + toggle_h))

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
row_height = ((max_y - toggle_h) * 0.25)
rows = [
    toggle_h,
    (toggle_h + (row_height * 1)),
    (toggle_h + (row_height * 2)),
    (toggle_h + (row_height * 3)),
]

# rects for keys - rect = (x, y, (x + w), (y + h))
rect_1 = (cols[0], rows[2], (cols[0] + col_width), (rows[2] + row_height))
rect_2 = (cols[1], rows[2], (cols[1] + col_width), (rows[2] + row_height))
rect_3 = (cols[2], rows[2], (cols[2] + col_width), (rows[2] + row_height))
rect_4 = (cols[0], rows[1], (cols[0] + col_width), (rows[1] + row_height))
rect_5 = (cols[1], rows[1], (cols[1] + col_width), (rows[1] + row_height))
rect_6 = (cols[2], rows[1], (cols[2] + col_width), (rows[1] + row_height))
rect_7 = (cols[0], rows[0], (cols[0] + col_width), (rows[0] + row_height))
rect_8 = (cols[1], rows[0], (cols[1] + col_width), (rows[0] + row_height))
rect_9 = (cols[2], rows[0], (cols[2] + col_width), (rows[0] + row_height))
rect_0 = (cols[0], rows[3], (cols[0] + col_width), (rows[3] + row_height))
rect_comma = (cols[1], rows[3], (cols[1] + col_width), (rows[3] + row_height))
rect_enter = (cols[2], rows[3], (cols[2] + col_width), (rows[3] + row_height))
rect_slash = (cols[3], rows[0], (cols[3] + col_width), (rows[0] + row_height))
rect_asterisk = (cols[3], rows[1], (cols[3] + col_width),
    (rows[1] + row_height))
rect_minus = (cols[3], rows[2], (cols[3] + col_width), (rows[2] + row_height))
rect_plus = (cols[3], rows[3], (cols[3] + col_width), (rows[3] + row_height))
# backspace key is two rows high
rect_backspace = (cols[4], rows[0], (cols[4] + col_width),
    (rows[0] + (row_height * 2)))
rect_percent = (cols[4], rows[2], (cols[4] + col_width), (rows[2] + row_height))
rect_equals = (cols[4], rows[3], (cols[4] + col_width), (rows[3] + row_height))

all_rects = [
    toggle_rect,
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
    rect_equals
]

# helper functions

# returns true if a point(x, y) lies inside a rect(x, y, w, h)
def ptInRect(pt, rect):
    if (rect[0] <= pt[0] <= rect[2]) and (rect[1] <= pt[1] <= rect[3]):
        return True
    else:
        return False

#-------------------------------------------------------------------------------

# constants
TOGGLE_HOLD_TIME = 2

# global variables
numlock = False

# main loop
while True:

    # look at each event from keyboard
    for e in keyboard.events():

        # if it's the numlock key
        if e.matches(libevdev.EV_LED.LED_NUML):

            # flip flag
            numlock = not numlock

            # only change once - numlock is now True
            if numlock:
                touchpad.grab()
                print('Numpad is on')

            # only change once - numlock is now False
            else:
                touchpad.ungrab()
                print('Numpad is off')




    # don't use all cpu time!
    time.sleep(0.1)

# ungrab touchpad if it was grabbed
touchpad.ungrab()

# close file descriptor
fd_touchpad.close()
fd_keyboard.close()






# current_x = 0
# current_y = 0
# pt = (0, 0)
# toggle = False
# start_toggle_time = 0
# shift = False
# value = 0



    # # look at each event from touchpad
    # for e in touchpad.events():
    #
    #     # get the current touch position
    #     if e.matches(libevdev.EV_ABS.ABS_MT_POSITION_X):
    #
    #         # save current as point
    #         current_x = e.value
    #
    #         # bail on toggle if finger moved too far
    #         pt = (current_x, current_y)
    #         if toggle and not ptInRect(pt, toggle_rect):
    #             toggle = False
    #
    #     if e.matches(libevdev.EV_ABS.ABS_MT_POSITION_Y):
    #
    #         # save current as point
    #         current_y = e.value
    #
    #         # bail on toggle if finger moved too far
    #         pt = (current_x, current_y)
    #         if toggle and not ptInRect(pt, toggle_rect):
    #             toggle = False
    #
    #     # if it was a finger event
    #     if e.matches(libevdev.EV_KEY.BTN_TOOL_FINGER):
    #
    #         # start of touch
    #         if (e.value == 1):
    #
    #             # save current as point
    #             pt = (current_x, current_y)
    #
    #             # if touch starts as a toggle
    #             if ptInRect(pt, toggle_rect):
    #                  toggle = True
    #                  start_toggle_time = time.time()
    #
    #             # if we are using numpad
    #             if numlock:
    #
    #                 # reset value
    #                 shift = False
    #                 value = 0
    #
    #                 # find the key we pressed on
    #                 if ptInRect(pt, rect_1):
    #                     value = libevdev.EV_KEY.KEY_KP1
    #                 elif ptInRect(pt, rect_2):
    #                     value = libevdev.EV_KEY.KEY_KP2
    #                 elif ptInRect(pt, rect_3):
    #                     value = libevdev.EV_KEY.KEY_KP3
    #                 elif ptInRect(pt, rect_4):
    #                     value = libevdev.EV_KEY.KEY_KP4
    #                 elif ptInRect(pt, rect_5):
    #                     value = libevdev.EV_KEY.KEY_KP5
    #                 elif ptInRect(pt, rect_6):
    #                     value = libevdev.EV_KEY.KEY_KP6
    #                 elif ptInRect(pt, rect_7):
    #                     value = libevdev.EV_KEY.KEY_KP7
    #                 elif ptInRect(pt, rect_8):
    #                     value = libevdev.EV_KEY.KEY_KP8
    #                 elif ptInRect(pt, rect_9):
    #                     value = libevdev.EV_KEY.KEY_KP9
    #                 elif ptInRect(pt, rect_0):
    #                     value = libevdev.EV_KEY.KEY_KP0
    #                 elif ptInRect(pt, rect_comma):
    #                     value = libevdev.EV_KEY.KEY_KPCOMMA
    #                 elif ptInRect(pt, rect_enter):
    #                     value = libevdev.EV_KEY.KEY_KPENTER
    #                 elif ptInRect(pt, rect_slash):
    #                     value = libevdev.EV_KEY.KEY_KPSLASH
    #                 elif ptInRect(pt, rect_asterisk):
    #                     value = libevdev.EV_KEY.KEY_KPASTERISK
    #                 elif ptInRect(pt, rect_minus):
    #                     value = libevdev.EV_KEY.KEY_KPMINUS
    #                 elif ptInRect(pt, rect_plus):
    #                     value = libevdev.EV_KEY.KEY_KPPLUS
    #                 elif ptInRect(pt, rect_backspace):
    #                     value = libevdev.EV_KEY.KEY_BACKSPACE
    #                 elif ptInRect(pt, rect_percent):
    #
    #                     # percent key needs shift + 5
    #                     shift = True
    #                     value = libevdev.EV_KEY.KEY_5
    #                 elif ptInRect(pt, rect_equals):
    #                     value = libevdev.EV_KEY.KEY_KPEQUAL
    #
    #                 # if we pressed on a known key
    #                 if (value != 0):
    #
    #                     # press shift if we need percent sign
    #                     if shift:
    #                         try:
    #                             events = [
    #                                 libevdev.InputEvent(
    #                                     libevdev.EV_KEY.KEY_LEFTSHIFT, 1
    #                                 ),
    #                                 libevdev.InputEvent(
    #                                     libevdev.EV_SYN.SYN_REPORT, 0
    #                                 )
    #                             ]
    #                             numpad.send_events(events)
    #                         except OSError as err:
    #                             logging.debug(str(err))
    #
    #                     # press the appropriate key
    #                     try:
    #                         events = [
    #                             libevdev.InputEvent(value, 1),
    #                             libevdev.InputEvent(
    #                                 libevdev.EV_SYN.SYN_REPORT, 0
    #                             )
    #                         ]
    #                         numpad.send_events(events)
    #                     except OSError as err:
    #                         logging.debug(str(err))
    #
    #         # end of touch
    #         if (e.value == 0):
    #
    #             # if a key was pressed
    #             if (value != 0):
    #
    #                 # release key
    #                 try:
    #                     events = [
    #                         libevdev.InputEvent(value, 0),
    #                         libevdev.InputEvent(libevdev.EV_SYN.SYN_REPORT, 0)
    #                     ]
    #                     numpad.send_events(events)
    #                 except OSError as err:
    #                     logging.debug(str(err))
    #
    #                 # release shift key if it was the percent
    #                 if shift:
    #                     try:
    #                         events = [
    #                             libevdev.InputEvent(
    #                                 libevdev.EV_KEY.KEY_LEFTSHIFT, 0
    #                             ),
    #                             libevdev.InputEvent(
    #                                 libevdev.EV_SYN.SYN_REPORT, 0
    #                             )
    #                         ]
    #                         numpad.send_events(events)
    #                     except OSError as err:
    #                         logging.debug(str(err))
    #
    #             # clear flags and value
    #             toggle = False
    #             start_toggle_time = 0
    #             shift = False
    #             value = 0
    #
    #     # N.B. this block matches ANY event
    #
    #     # if the tap started at the toggle switch
    #     if toggle:
    #
    #         # if it was held long enough
    #         if ((time.time() - start_toggle_time) >= secs_to_toggle):
    #
    #             # reset flag
    #             toggle = False
    #             start_toggle_time = 0
    #
    #             # send numlock key for indicator
    #             try:
    #                 events = [
    #                     libevdev.InputEvent(libevdev.EV_KEY.KEY_NUMLOCK, 1),
    #                     libevdev.InputEvent(libevdev.EV_SYN.SYN_REPORT, 0)
    #                 ]
    #                 numpad.send_events(events)
    #                 events = [
    #                     libevdev.InputEvent(libevdev.EV_KEY.KEY_NUMLOCK, 0),
    #                     libevdev.InputEvent(libevdev.EV_SYN.SYN_REPORT, 0)
    #                 ]
    #                 numpad.send_events(events)
    #             except OSError as err:
    #                 logging.debug(str(err))


# -)
