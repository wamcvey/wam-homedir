#!/bin/sh
# Write some text on the Babylon 5 image/background to identify the lab machine

#	-box darkslategrey \

base_image=Babylon5_1024x768.jpg 
convert $base_image \
	-density 144 \
	-stroke black -pointsize 36 \
	-fill yellow  \
	-gravity NorthEast  \
	-draw "text 0,0 \"$1\""  $1.jpg

echo "$0: Wrote image out to $1.jpg" >&2


