source ./pushgateway.sh
RESULT_FILE='result.info'

wsk -i action invoke "$1" --blocking --param sleep '1000' | tail -n +2 | jq '.annotations[] | select(.key=="waitTime" or .key == "initTime").value' > "$RESULT_FILE"

#START_TIME=$(awk '{sum+=$0} END{print sum}' "$RESULT_FILE")
START_TIME=$(sed -n 2p "$RESULT_FILE")
if [ $(cat "$RESULT_FILE" | wc -l) -gt 1 ]; then 
  
    echo "cold start took $START_TIME ms"
    push "start_cold" "$START_TIME" "$1"
else 
    echo "warm start took $START_TIME ms"
    push "start_warm" "$START_TIME" "$1"
fi
