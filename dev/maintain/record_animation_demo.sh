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

    source ~/code/progiter/dev/maintain/record_animation_demo.sh

'

### START ###

export WINDOWID
WINDOWID=$(xdotool getwindowfocus)
echo "WINDOWID = $WINDOWID"
xwininfo -id "$WINDOWID"
#xdotool windowsize "$WINDOWID" 811 501
xdotool windowsize "$WINDOWID" 620 320
cls

echo '
import time
import vimtk
from vimtk.xctrl import XCtrl;
vimtk.Clipboard.copy("ipython")
sleeptime = 0.5
time.sleep(sleeptime)
XCtrl.send_keys("ctrl+shift+v", sleeptime)
XCtrl.send_keys("KP_Enter", sleeptime)
vimtk.Clipboard.copy("""
import progiter
import time
for i in progiter.ProgIter(range(1000)):
    time.sleep(0.023)
""".lstrip())
time.sleep(sleeptime)
XCtrl.send_keys("ctrl+shift+v", sleeptime)
XCtrl.send_keys("KP_Enter", sleeptime)

# Wait until the progiter script finishes
# to paste in an exit command
time.sleep(0.023 * 1001)

vimtk.Clipboard.copy("exit")
time.sleep(sleeptime)
XCtrl.send_keys("ctrl+shift+v", sleeptime)
XCtrl.send_keys("KP_Enter", sleeptime)

# Another exit to stop the recording
vimtk.Clipboard.copy("exit")
time.sleep(sleeptime)
XCtrl.send_keys("ctrl+shift+v", sleeptime)
XCtrl.send_keys("KP_Enter", sleeptime)
' > _progiter_demo.py

# Start this file and immdiately start recording
python _progiter_demo.py&
clear
# Start recording
ttyrec progiter_demo_rec

### END ###

# Optional: can replay the sequence
ttyplay progiter_demo_rec

ttygif progiter_demo_rec -f
