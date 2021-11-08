function push() {
    URL="http://10.147.18.110:9092/metrics/job/$3"
    echo "Posting metric to $URL"
    echo "$1 $2" | curl --data-binary @- "$URL"	
}
