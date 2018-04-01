#!/bin/bash
serial=`cat /proc/cpuinfo | grep Serial | cut -d ' ' -f 2`

rclone move /home/pi/BingBinWall/images/ bingbinDrive:/$serial/images/ --delete-after
rclone copy /home/pi/BingBinWall/logs/ bingbinDrive:/$serial/logs/ --delete-after
