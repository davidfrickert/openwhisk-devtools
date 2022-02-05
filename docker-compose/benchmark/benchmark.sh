set -eou pipefail

./run.sh $1 300 1 $3 $2
sleep 120
./run.sh $1 300 2 $3 $2
sleep 120
./run.sh $1 300 4 $3 $2
sleep 120
./run.sh $1 300 8 $3 $2
