MAX_CONCURRENCY_CLUSTER=$1
./benchmark-st.sh sleep-hotspot data-sleep $MAX_CONCURRENCY_CLUSTER
sleep 300
./benchmark-st.sh filehashing-hotspot data-filehashing $MAX_CONCURRENCY_CLUSTER
sleep 300
#./benchmark-st.sh iconify-hotspot data-iconify $MAX_CONCURRENCY_CLUSTER
#sleep 300
./benchmark-st.sh video-hotspot data-video $MAX_CONCURRENCY_CLUSTER
sleep 300
./benchmark-st.sh rest-api-hotspot data-rest $MAX_CONCURRENCY_CLUSTER
