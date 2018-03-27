#!/bin/bash

# start pi-timolo...
echo "starting pi-tomolo..."
/home/pi/pi-timolo/pi-tomolo.sh
# /home/pi/pi-timolo/pi-tomolo.py
# python3 /home/pi/pi-timolo/pi-tomolo.py
# python3 /home/pi/pi-timolo/pi-tomolo.py >/dev/null 2>&1 &

# monitor photo folder
inotifywait -m /home/pi/BingBinWallImages -e create -e moved_to |
    while read path action file; do
        echo "The file '$file' appeared in directory '$path' via '$action'"
		
		#stop pi-tomolo.py
		pi_timolo_pid=$( pgrep -f pi-timolo.py )
		sudo kill $pi_timolo_pid
		
        # classify and change led color
		echo "classifying..."
		python3 /home/pi/BingBinWall/src/bbw.py -f "/home/pi/BingBinWallImages/$file"
		#RC=$?
		#rc=$?; if [[ $rc != 0 ]]; then exit $rc; fi
		
		# restart pi-tomolo
		echo "starting pi-tomolo..."
		/home/pi/pi-timolo/pi-tomolo.sh
		# python3 /home/pi/pi-timolo/pi-timolo.py >/dev/null 2>&1 &
    done