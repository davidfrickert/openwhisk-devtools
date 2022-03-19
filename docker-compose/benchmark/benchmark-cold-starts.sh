set -eou pipefail

./run-cold-starts.sh $1 1000 1 $3 $2
sleep 120
./run-cold-starts.sh $1 1000 2 $3 $2
sleep 120
./run-cold-starts.sh $1 1000 4 $3 $2
sleep 120
./run-cold-starts.sh $1 1000 8 $3 $2

# reset function to concurrency=1
wsk -i action update "$1" -c "1"
