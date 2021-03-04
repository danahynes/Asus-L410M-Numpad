<!----------------------------------------------------------------------------->
<!-- Filename: README.md                                       /          \  -->
<!-- Project : Asus_L410M_Numpad                              |     ()     | -->
<!-- Date    : 02/17/2019                                     |            | -->
<!-- Author  : Dana Hynes                                     |   \____/   | -->
<!-- License : WTFPLv2                                         \          /  -->
<!----------------------------------------------------------------------------->

# Asus_L410M_Numpad
## "It mostly works™"

This small program runs at boot and gives you access to the numpad that co-exists with the L410M trackpad.
The code is largely inspired by [this project](https://gitlab.com/Thraen/gx735_touchpad_numpad).

![](numpad.jpg)

# Installing

To install, clone the git repo:
```bash
foo@bar:~$ cd ~/Downloads
foo@bar:~/Downloads$ git clone https://github.com/danahynes/Asus_L410M_Numpad
foo@bar:~/Downloads$ cd Asus_L410M_Numpad
```

You will need to install the python3 module 'libevdev':
```bash
foo@bar:~/Downloads/Asus_L410M_Numpad$ pip3 install libevdev
```

Once you do that, you can install by:
```bash
foo@bar:~/Downloads/Asus_L410M_Numpad$ sudo ./install.sh
```
You can also download the [latest release](http://github.com/danahynes/Asus_L410M_Numpad/releases/latest), unzip it, and run the install.sh file from there.

# Uninstalling

To uninstall, go to the git directory and run:
```bash
foo@bar:~/Downloads/Asus_L410M_Numpad$ sudo ./uninstall.sh
```

or delete the files manually:
```bash
foo@bar:~$ sudo rm /usr/bin/asus_l410m_numpad.py
foo@bar:~$ sudo rm /lib/systemd/system/asus_l410m_numpad.service
```

# Notes

If you are using Elementary OS 5, turn on the Numlock indicator by going to System Settings -> Keyboard -> Layout -> Show in panel -> Num Lock and turning it on.

To toggle the numpad mode, press and hold on the toggle area for > 2 seconds.

I have not been able to get the backlight for the numpad working yet. I thought it would be mapped to the keyboard's NUMLOCK light, as it was in [the original project](https://gitlab.com/Thraen/gx735_touchpad_numpad) (and would be the most obvious way of using it -), even though my keyboard doesn't actually have one. Testing shows the messages for the Numlock light are being sent and tracked by the system, so it's not as simple as it should be -). More testing with a working (Windows) installation and a USB or i2c sniffer is needed, but I'm WAAAAYYY too lazy to do that.

Also note that this only works IF YOUR NUMLOCK KEY IS OFF AT BOOT. Mine is, yours probably will be too, but since I don't have a reliable way to get the numlock state at boot (still futzing with X on this -),  it is assumed that it is off. Again, this will be the default state for most users, so you should be OK. IF YOUR NUMLOCK KEY IS ON AT BOOT, I can't guarantee the behavior, so YMMV.

I'll provide a little more info in case anyone can help with this:

I can run any number of shell commands from python to get the Numlock LED state, such as:
```python
subprocess.call(['numlockx', 'status'])
or
subprocess.call('xset q | grep LED'.split())[65]
```
and they work just fine when I run the program from the commandline. But when I set the program to run as a service, I get errors in journalctl saying the the subprocess returned a non-zero exit code, regardless of which command I use. I can wrap the calls in a try/except block to catch this, but then the whole call gets ignored, which is the same as not using a call at all. I'm not sure what is different when the py script gets called as a service (obviously a few ideas, like interactive vs. login shell, sh vs. bash, environment variables, etc.) but with all my Google-fu I can't find a definitive answer. So, since I can't get a reliable initial Numlock state, I'm just assuming it's off. The script starts at boot, and I feel that it's safe to assume that Numlock will be off at boot. Once the script is up and running, it monitors both the toggle area on the trackpad and the Numlock key (if you have one), as well as the Numlock from the On-Screen Keyboard (OSK) for those of us without an actual Numlock key. So I feel like I have almost all the bases covered. Using either the trackpad's toggle area and/or the OSK Numlock key seems to keep everything in sync, so I am confident in saying "It mostly works™". If anyone has any ideas on why/how running a shell command in a python3 script that runs as a service doesn't work, please let me know.

# TODO

1. get numlock state at boot
1. get backlight working

# -)
