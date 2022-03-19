set -eou pipefail

./run.sh $1 3000 1 $3 $2
sleep 120
./run.sh $1 3000 2 $3 $2
sleep 120
./run.sh $1 3000 4 $3 $2
sleep 120
./run.sh $1 3000 8 $3 $2

# reset function to concurrency=1
wsk -i action update "$1" -c "1"
