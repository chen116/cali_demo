#/bin/bash


function letsgo {

  BASE_TASK="/root/mytools/myapp"
  RELEASETS="/root/liblitmus/release_ts"
  ST_TRACE="/root/ft_tools/st-trace-schedule"

  SPIN_PIDS=""

  PROG="vic"
  DIR="run-data"
  declare -a NEW_SPIN_PIDS
  SchedNames="GSN-EDF"

  j=0
  DESIRED_WCET=$1
  BASE=30000
  fft_size_or_iter=$(($DESIRED_WCET * $BASE))
  while true; do

    echo "Starting st_trace"
    ${ST_TRACE} -s mk &
    ST_TRACE_PID="$!"
    echo "st_trace pid: ${ST_TRACE_PID}"
    sleep 1


    

    echo "Switching to $sched plugin"
    # echo "$sched" > /proc/litmus/active_plugin
    /root/liblitmus/setsched GSN-EDF
    sleep 1

    #read wcet and period from the dist file
    num_tasks=1
    echo "Setting up processes"
    for nt in `seq 1 $num_tasks`;
      do
        # wcet(ms) period(ms) duration(s) mode appname fft_size/iter
        $BASE_TASK 400 400 1 4 $PROG $fft_size_or_iter &
        SPIN_PIDS="$SPIN_PIDS $!"
        NEW_SPIN_PIDS[`expr $nt - 1`]="$!"
    done
    sleep 1

    #echo "catting log"
    #cat /dev/litmus/log > log.txt &
    #LOG_PID="$!"
    #sleep 1
    echo "Doing release..."
    $RELEASETS

    echo "Waiting for processes..."
    # wait ${SPIN_PIDS}

    for i in "${NEW_SPIN_PIDS[@]}"
      do
        wait $i
      done
    unset NEW_SPIN_PIDS

    echo "Done wait, sleeping"
    sleep 1
    echo "Killing log"
    kill ${LOG_PID}
    sleep 1
    echo "Sending SIGUSR1 to st_trace"
    kill -USR1 ${ST_TRACE_PID}
    echo "Waiting for st_trace..."
    wait ${ST_TRACE_PID}
    sleep 1

    mkdir -p "$DIR"/
    mkdir "$DIR"/"$PROG"
    mv /dev/shm/*.bin "$DIR"/"$PROG"/

    python find_wcet.py $DESIRED_WCET
    # fft_size_or_iter=${fft_size_or_iter::-100}
    overshoot=$(head -n 1 overshoot)
    if [ "$overshoot" == "1" ]
      then 
        fft_size_or_iter=$(($fft_size_or_iter - $BASE))
        echo "see a overshoot, final loop count: $fft_size_or_iter"
        echo desired_wcet ms: "$DESIRED_WCET" >> result
        echo fft_size_or_iter: "$fft_size_or_iter" >> result
        break
    fi
    if [ "$overshoot" == "0" ]
      then 
        echo "no overshoot, loop count: $fft_size_or_iter"
    fi
    fft_size_or_iter=$(($fft_size_or_iter + $BASE))

  done


  j=$((j+1))
  #mv log.txt "$DIR"/"$sched"_$rep/
  sleep 1
  echo "Done! Collect your logs."


  echo "DONE!"
}

for desired_wcet in 40 150 250 
  do 
      letsgo $desired_wcet
  done





