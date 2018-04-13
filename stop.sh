pid=`ps aux | grep bbw.py | grep -v grep | awk '{print $2}'`
if [ ! -z "$pid" ]
then
kill -SIGINT $pid
echo "pid=$pid, killed"
else
echo "pid not found"
fi
