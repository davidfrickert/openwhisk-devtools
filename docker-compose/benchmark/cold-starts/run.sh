function do_graal_benchmark {
  start_time=$(date +%s.%3N)
  docker-compose -f docker-compose-graal.yml up -d  --force-recreate
  curl -s -S -X POST localhost:8080/run -d '{"value": {"time": "1000"}}' > /dev/null
  echo ""
  end_time=$(date +%s.%3N)
  elapsed=$(echo "scale=0; ($end_time - $start_time) * 1000 / 1" | bc)
  echo "Took $elapsed ms to cold start graal function"

  invoke_measured
  invoke_measured
  invoke_measured
  invoke_measured

  docker rm -f $(docker ps -aqf 'name=sleep')
}

function do_hotspot_benchmark {
  start_time=$(date +%s.%3N)
  docker-compose -f docker-compose-hotspot.yml up -d  --force-recreate
  start_init_time=$(date +%s.%3N)
  python3 ./invoke.py init ch.ethz.systems.Sleep sleep.jar
  end_init_time=$(date +%s.%3N)
  curl -s -S -X POST localhost:8080/run -d '{"value": {"time": "1000"}}' > /dev/null
  echo ""
  end_time=$(date +%s.%3N)
  elapsed=$(echo "scale=0; ($end_time - $start_time) * 1000 / 1" | bc)
  elapsed_init=$(echo "scale=0; ($end_init_time - $start_init_time) * 1000 / 1" | bc)
  echo "Took $elapsed ms to cold start hotspot function and $elapsed_init ms to initialize"

  invoke_measured
  invoke_measured
  invoke_measured
  invoke_measured

  docker rm -f $(docker ps -aqf 'name=sleep')
}

function invoke_measured() {
  start_time=$(date +%s.%3N)
  curl -s -S -X POST localhost:8080/run -d '{"value": {"time": "1000"}}' > /dev/null
  end_time=$(date +%s.%3N)
  elapsed=$(echo "scale=0; ($end_time - $start_time) * 1000 / 1" | bc)
  echo "Took $elapsed ms to invoke function"
}

do_graal_benchmark
sleep 2
do_hotspot_benchmark
