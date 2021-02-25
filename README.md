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
```
foo@bar:~$ cd ~/Downloads
foo@bar:~$ git clone https://github.com/danahynes/Asus_L410M_Numpad
foo@bar:~$ cd Asus_L410M_Numpad
```

You will need to install the python3 module 'libevdev':
```
foo@bar:~$ pip3 install libevdev
```

Once you do that, you can install by:
```
foo@bar:~$ sudo ./install.sh
```
You can also download the [latest release](http://github.com/danahynes/Asus_L410M_Numpad/releases/latest), unzip it, and run the install.sh file from there.

# Uninstalling

To uninstall, go to the git directory and run:
```
foo@bar:~$ sudo ./uninstall.sh
```

# Notes

I have not been able to get the backlight for the numpad working yet. I thought it would be mapped to the keyboard's NUMLOCK light, as it was in [the original project](https://gitlab.com/Thraen/gx735_touchpad_numpad), even though my keyboard doesn't actually have one. Testing shows the messages for the light are being sent and tracked by the system, but the hardware doesn't work yet. More testing with a working (Windows) installation is needed, but I'm too lazy to do that.

Also note that if your keyboard has a NumLock key, it's not being monitored here. My keyboard doesn't, so I didn't write any checks. The program does check for the state on startup, and I will add more code for it later (using the On Screen Keyboard) but for now, if you use a physical key or the OSK, things will get out of sync.
