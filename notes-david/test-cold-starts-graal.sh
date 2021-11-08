MAX_ITER=$1

for i in $(seq 0 $MAX_ITER)
do
    ./calcColdStartGraal.sh sleep-graal
    docker stop $(docker ps --filter name=wsk0* -aq) && docker rm $(docker ps --filter name=wsk0* -aq)
   sleep 1 

done 
