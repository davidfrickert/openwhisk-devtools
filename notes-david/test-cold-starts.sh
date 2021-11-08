MAX_ITER=$1

for i in $(seq 0 $MAX_ITER)
do
    ./calcColdStart.sh sleep-photon
    docker stop $(docker ps --filter name=wsk0* -aq) && docker rm $(docker ps --filter name=wsk0* -aq)
   sleep 1 

done 
