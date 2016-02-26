#!/bin/bash

args=("$@")
echo "${args[0]}"

if [[ "${args[0]}" =  "start" ]];
then
	start-dfs.sh
	start-yarn.sh
	mr-jobhistory-daemon.sh start historyserver	
	hadoop dfsadmin -safemode leave
	echo "hadoop started.."
elif [[ "${args[0]}" = "stop" ]];
then
	stop-dfs.sh
	stop-yarn.sh
	mr-jobhistory-daemon.sh stop historyserver
	echo "hadoop stopped.."
fi
