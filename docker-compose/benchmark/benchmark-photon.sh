MAX_CONCURRENCY_CLUSTER=$1
./benchmark.sh sleep-photon data-sleep $MAX_CONCURRENCY_CLUSTER
sleep 300
./benchmark.sh filehashing-photon data-filehashing $MAX_CONCURRENCY_CLUSTER
sleep 300
./benchmark.sh iconify-photon data-iconify $MAX_CONCURRENCY_CLUSTER
