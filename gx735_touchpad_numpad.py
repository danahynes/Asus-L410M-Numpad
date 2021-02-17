from libevdev import Device, InputEvent, EV_ABS, EV_KEY, EV_LED, EV_SYN
from fcntl import fcntl, F_SETFL
from time import sleep, time
import sys
from os import O_NONBLOCK



# Look into the devices file #
#tries=5
# while tries > 0:

#     keyboard_detected = 0
#     touchpad_detected = 0
#
#     with open('/proc/bus/input/devices', 'r') as f:
#
#         lines = f.readlines()
#         for line in lines:
#             # Look for the touchpad #
#             if touchpad_detected == 0 and "Name=\"ELAN" in line and "Mouse" not in line:
#                 touchpad_detected = 1
#
#             if touchpad_detected == 1:
#                 if "H: " in line:
#                     touchpad = line.split("event")[1]
#                     touchpad = touchpad.split(" ")[0]
#                     touchpad_detected = 2
#             # Look for the keyboard (numlock) #
#             if keyboard_detected == 0 and ("Asus Keyboard" in line or "N-KEY" in line):
#                 keyboard_detected = 1
#
#             if keyboard_detected == 1:
#                 if "H: " in line:
#                     keyboard = line.split("event")[1]
#                     keyboard = keyboard.split(" ")[0]
#                 if "ff98007a000007ff" in line:
#                     keyboard_detected = 2
#             # Stop looking if both have been found #
#             if keyboard_detected == 2 and touchpad_detected == 2:
#                 break
#
#     if keyboard_detected != 2 or touchpad_detected != 2:
#         tries -= 1
#         if tries == 0:
#             if keyboard_detected != 2:
#                 print("Can't find keyboard, code " + str(keyboard_detected))
#             if touchpad_detected != 2:
#                 print("Can't find touchpad, code " + str(touchpad_detected))
#             sys.exit(1)
#     else:
#         break

#     sleep(0.1)

touchpad = 14
#keyboard = 15




# Start monitoring the touchpad #
fd_t = open('/dev/input/event' + str(touchpad), 'rb')
fcntl(fd_t, F_SETFL, O_NONBLOCK)
d_t = Device(fd_t)

# Retrieve touchpad dimensions #
ai = d_t.absinfo[EV_ABS.ABS_X]
(minx, maxx) = (ai.minimum, ai.maximum)
ai = d_t.absinfo[EV_ABS.ABS_Y]
(miny, maxy) = (ai.minimum, ai.maximum)

# Start monitoring the keyboard (numlock) #
# fd_k = open('/dev/input/event' + str(keyboard), 'rb')
# fcntl(fd_k, F_SETFL, O_NONBLOCK)
# d_k = Device(fd_k)

# Create a new keyboard device to send numpad events #
dev = Device()
dev.name = "Asus Touchpad/Numpad"
dev.enable(EV_KEY.KEY_KP1)
dev.enable(EV_KEY.KEY_KP2)
dev.enable(EV_KEY.KEY_KP3)
dev.enable(EV_KEY.KEY_KP4)
dev.enable(EV_KEY.KEY_KP5)
dev.enable(EV_KEY.KEY_KP6)
dev.enable(EV_KEY.KEY_KP7)
dev.enable(EV_KEY.KEY_KP8)
dev.enable(EV_KEY.KEY_KP9)
dev.enable(EV_KEY.KEY_KP0)
dev.enable(EV_KEY.KEY_KPSLASH)
dev.enable(EV_KEY.KEY_KPASTERISK)
dev.enable(EV_KEY.KEY_KPMINUS)
dev.enable(EV_KEY.KEY_KPPLUS)
dev.enable(EV_KEY.KEY_KPCOMMA)      # decimal
dev.enable(EV_KEY.KEY_KPENTER)
dev.enable(EV_KEY.KEY_KPEQUAL)
dev.enable(EV_KEY.KEY_BACKSPACE)
dev.enable(EV_KEY.KEY_LEFTSHIFT)    # for percent (shift-5)
dev.enable(EV_KEY.KEY_5)            # for percent (shift-5)
dev.enable(EV_KEY.KEY_NUMLOCK)

udev = dev.create_uinput_device()
start = 0
toggle = False
numlock = False
x = 0
y = 0
pressed = 0
shift = False
value = 0

# Process events while running #
while True:

    # If keyboard sends numlock event, enable/disable touchpad events #
    # for e in d_k.events():
    #     if e.matches(EV_LED.LED_NUML):
    #         numlock = not numlock
    #         if numlock:
    #             d_t.grab()
    #         else:
    #             d_t.ungrab()

    # If touchpad sends tap events, convert x/y position to numlock key and send it #
    for e in d_t.events():

        # if the tap started at the toggle switch
        if toggle:

            # if it was held long enough
            if time() - start >= 2:

                # reset flag
                toggle = False

                # toggle flag
                numlock = not numlock

                # grab or ungrab pad
                if numlock:
                    d_t.grab()
                else:
                    d_t.ungrab()

                # send numlock key for indicator
                try:
                    events = [InputEvent(EV_KEY.KEY_NUMLOCK, 1),
                        InputEvent(EV_SYN.SYN_REPORT, 0)]
                    udev.send_events(events)
                    events = [InputEvent(EV_KEY.KEY_NUMLOCK, 0),
                        InputEvent(EV_SYN.SYN_REPORT, 0)]
                    udev.send_events(events)
                except OSError as e:
                    pass

        # Get x position on first touch
        if e.matches(EV_ABS.ABS_MT_POSITION_X) and pressed == 0:
            x = e.value

        # Get y position on first touch
        if e.matches(EV_ABS.ABS_MT_POSITION_Y) and pressed == 0:
            y = e.value

        # If tap #
        if e.matches(EV_KEY.BTN_TOOL_FINGER):

            # Start of tap #
            if e.value == 1 and pressed == 0:
                pressed = 1
                shift = False
                value = 0

                try:
                    if y > 0.78 * maxy:
                        if x > 0.8 * maxx:
                            value = EV_KEY.KEY_KPEQUAL
                        elif x > 0.6 * maxx:
                            value = EV_KEY.KEY_KPPLUS
                        elif x > 0.4 * maxx:
                            value = EV_KEY.KEY_KPENTER
                        elif x > 0.2 * maxx:
                            value = EV_KEY.KEY_KPCOMMA
                        else:
                            value = EV_KEY.KEY_KP0
                    elif y > 0.56 * maxy:
                        if x > 0.8 * maxx:
                            shift = True
                            try:
                                events = [InputEvent(EV_KEY.KEY_LEFTSHIFT, 1),
                                    InputEvent(EV_SYN.SYN_REPORT, 0)]
                                udev.send_events(events)
                            except OSError as e:
                                pass
                            value = EV_KEY.KEY_5
                        elif x > 0.6 * maxx:
                            value = EV_KEY.KEY_KPMINUS
                        elif x > 0.4 * maxx:
                            value = EV_KEY.KEY_KP3
                        elif x > 0.2 * maxx:
                            value = EV_KEY.KEY_KP2
                        else:
                            value = EV_KEY.KEY_KP1
                    elif y > 0.34 * maxy:
                        if x > 0.8 * maxx:
                            value = EV_KEY.KEY_BACKSPACE
                        elif x > 0.6 * maxx:
                            value = EV_KEY.KEY_KPASTERISK
                        elif x > 0.4 * maxx:
                            value = EV_KEY.KEY_KP6
                        elif x > 0.2 * maxx:
                            value = EV_KEY.KEY_KP5
                        else:
                            value = EV_KEY.KEY_KP4
                    elif y > 0.12 * maxy:
                        if x > 0.8 * maxx:
                            value = EV_KEY.KEY_BACKSPACE
                        elif x > 0.6 * maxx:
                            value = EV_KEY.KEY_KPSLASH
                        elif x > 0.4 * maxx:
                            value = EV_KEY.KEY_KP9
                        elif x > 0.2 * maxx:
                            value = EV_KEY.KEY_KP8
                        else:
                            value = EV_KEY.KEY_KP7
                    else:
                        if x > 0.9 * maxx:
                            value = EV_KEY.KEY_NUMLOCK
                            start = time()
                            toggle = True
                            continue
                        else:
                            continue

                    if numlock:
                        # Send press key event #
                        events = [InputEvent(value, 1),
                            InputEvent(EV_SYN.SYN_REPORT, 0)]
                        udev.send_events(events)
                except OSError as e:
                    pass

            # If end of tap, send release key event #
            if e.value == 0:
                pressed = 0

                try:
                    events = [InputEvent(value, 0),
                        InputEvent(EV_SYN.SYN_REPORT, 0)]
                    udev.send_events(events)
                except OSError as e:
                    pass

                if shift:
                    shift = False
                    try:
                        events = [InputEvent(EV_KEY.KEY_LEFTSHIFT, 0),
                            InputEvent(EV_SYN.SYN_REPORT, 0)]
                        udev.send_events(events)
                    except OSError as e:
                        pass




    sleep(0.1)

# Close file descriptors #
fd_k.close()
fd_t.close()
