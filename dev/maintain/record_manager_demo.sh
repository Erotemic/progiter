#!/bin/bash
__doc__='

Requires:
    sudo apt-get install imagemagick ttyrec gcc x11-apps make git -y

    cd "$HOME"/code
    git clone https://github.com/icholy/ttygif.git
    cd ttygif
    PREFIX=$HOME/.local make
    PREFIX=$HOME/.local make install

Instructions:

    Execute this file in bash, dont do anything while it works because there is
    a script running in the background sending copy / paste commands.

    source ~/code/progiter/dev/maintain/record_manager_demo.sh

'

### START ###

export WINDOWID
WINDOWID=$(xdotool getwindowfocus)
echo "WINDOWID = $WINDOWID"
xwininfo -id "$WINDOWID"
#xdotool windowsize "$WINDOWID" 1011 501
xdotool windowsize "$WINDOWID" 811 501

cls

echo '

import time
import vimtk
from vimtk.xctrl import XCtrl;

vimtk.Clipboard.copy("bash")
sleeptime = 0.5
time.sleep(sleeptime)

#XCtrl.send_keys("ctrl+shift+v", sleeptime)
#XCtrl.send_keys("KP_Enter", sleeptime)

vimtk.Clipboard.copy("""
DEMO_PROGRESS=1 xdoctest -m progiter.manager __doc__
""".lstrip())
time.sleep(sleeptime)
XCtrl.send_keys("ctrl+shift+v", sleeptime)
XCtrl.send_keys("KP_Enter", sleeptime)

# Wait until the progiter script finishes
# to paste in an exit command
time.sleep(50)

vimtk.Clipboard.copy("exit")
time.sleep(sleeptime)
XCtrl.send_keys("ctrl+shift+v", sleeptime)
XCtrl.send_keys("KP_Enter", sleeptime)

# Another exit to stop the recording
vimtk.Clipboard.copy("exit")
time.sleep(sleeptime)
XCtrl.send_keys("ctrl+shift+v", sleeptime)
XCtrl.send_keys("KP_Enter", sleeptime)
' > manager_demo.py

__test__="
python manager_demo.py&
"

# Start this file and immdiately start recording
python manager_demo.py&
clear
# Start recording
ttyrec manager_demo_rec

### END ###

# Optional: can replay the sequence
ttyplay manager_demo_rec

ttygif manager_demo_rec -f
