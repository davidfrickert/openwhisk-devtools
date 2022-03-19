ACTION_NAME="$1"
RUN_FOR_SECS="$2"
CONCURRENCY="$3"
CONCURRENCY_MAX="$4"
DATA_FILE="$5"

wsk -i action update "$ACTION_NAME" -c "$CONCURRENCY"

#-v3
ab -t"$RUN_FOR_SECS" -n50000000 -s 120 -c"$CONCURRENCY_MAX" -p "$DATA_FILE" -T application/json -H "Authorization: Basic MjNiYzQ2YjEtNzFmNi00ZWQ1LThjNTQtODE2YWE0ZjhjNTAyOjEyM3pPM3haQ0xyTU42djJCS0sxZFhZRnBYbFBrY2NPRnFtMTJDZEFzTWdSVTRWck5aOWx5R1ZDR3VNREdJd1A=" \
	-H "Content-Type: application/json" -H "User-Agent: OpenWhisk-CLI/1.0 (2019-09-23T17:46:38.323+0000) linux 386"  \
 "https://146.193.41.200/api/v1/namespaces/_/actions/$ACTION_NAME?blocking=true&result=true" 
