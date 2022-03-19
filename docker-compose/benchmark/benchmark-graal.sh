MAX_CONCURRENCY_CLUSTER=$1
./benchmark.sh sleep-graal data-sleep $MAX_CONCURRENCY_CLUSTER
sleep 300
./benchmark.sh filehashing-graal data-filehashing $MAX_CONCURRENCY_CLUSTER
sleep 300
#./benchmark.sh iconify-graal data-iconify $MAX_CONCURRENCY_CLUSTER
#sleep 300
./benchmark.sh video-graal data-video $MAX_CONCURRENCY_CLUSTER
sleep 300
./benchmark.sh rest-api-graal data-rest $MAX_CONCURRENCY_CLUSTER
