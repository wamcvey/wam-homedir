#!/bin/sh

# . $HOME/.bash_profile

# Set up some paths and envinvorment variables useful for running X
if [ -d /usr/openwin ]
then
	OPENWINHOME=/usr/openwin ; export OPENWINHOME
	HELPPATH=$OPENWINHOME/lib/help; export HELPPATH
fi

xrdb -load ${HOME}/.Xdefaults

xmodmap ${HOME}/.xmodmaprc

ssh-add
# sh -c "tail -f /var/log/messages | osd_cat -a 60 -o 15  -f fixed -d 30 -s 1 -p bottom -c red  &"
exec gnome-session

# Old stuff
# if gnome-session isn't installed, try setting up a reasonable non-gnome
# environment
for wm in gnome-session openbox wmaker fvwm2 piewm fvwm95-2 fvwm vuesession dtsession tvtwm twm mwm olvwm olwm 
do
	if whence $wm > /dev/null
	then
		exec $wm
	fi
done

#enable screen saver for 10 minutes
xset s 600 &

xcb &
xsetbg -gamma 1.3 /usr/X11R6/lib/backgrounds/cglurlow8.bmp
sh -c "xautolock &"

#Console Window
CONSOLE=true xterm -T "Console: $DISPLAY" -n "Console: $DISPLAY" \
	-C +ut -tm "erase" -geometry 80x17+2-5
