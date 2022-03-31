set -eou pipefail
APP="$1"
MAIN="$2"
DATA="{\"value\":$(cat "$3")}"

function do_graal_benchmark_docker {
  start_time=$(date +%s.%3N)
  docker-compose -f docker-compose-graal.yml up -d  --force-recreate
  until curl -s -S -X POST localhost:8080/run -d "$DATA" > /dev/null; do echo "nop"; done
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

function do_hotspot_benchmark_docker {
  start_time=$(date +%s.%3N)
  docker-compose -f docker-compose-hotspot.yml up -d  --force-recreate
  start_init_time=$(date +%s.%3N)
  python3 ./invoke.py init ch.ethz.systems.Sleep sleep.jar
  end_init_time=$(date +%s.%3N)
  curl -s -S -X POST localhost:8080/run -d "$DATA" > /dev/null
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

function do_graal_benchmark {
  start_time=$(date +%s.%3N)
  start_graal
  PID=$!
  until curl -s -S -X POST localhost:8080/run -d "$DATA"; do
    :
  done
  echo ""
  end_time=$(date +%s.%3N)
  elapsed=$(echo "scale=0; ($end_time - $start_time) * 1000 / 1" | bc)
  echo "Took $elapsed ms to cold start graal function"

  invoke_measured
  invoke_measured
  invoke_measured
  invoke_measured
    kill $PID
}

function do_hotspot_benchmark {
  start_time=$(date +%s.%3N)
  start_hotspot
  PID=$!
  start_init_time=$(date +%s.%3N)
  python3 ./invoke.py init "$MAIN" jars/"$APP".jar
  end_init_time=$(date +%s.%3N)
  curl -s -S -X POST localhost:8080/run -d "$DATA" > /dev/null
  echo ""
  end_time=$(date +%s.%3N)
  elapsed=$(echo "scale=0; ($end_time - $start_time) * 1000 / 1" | bc)
  elapsed_init=$(echo "scale=0; ($end_init_time - $start_init_time) * 1000 / 1" | bc)
  echo "Took $elapsed ms to cold start hotspot function and $elapsed_init ms to initialize"

  invoke_measured
  invoke_measured
  invoke_measured
  invoke_measured
    kill $PID
}

function invoke_measured() {
  start_time=$(date +%s.%3N)
  curl -s -S -X POST localhost:8080/run -d '{"value": {"time": "1000"}}' > /dev/null
  end_time=$(date +%s.%3N)
  elapsed=$(echo "scale=0; ($end_time - $start_time) * 1000 / 1" | bc)
  echo "Took $elapsed ms to invoke function"
}

start_hotspot() {
   java --add-opens java.base/jdk.internal.reflect=ALL-UNNAMED --add-exports java.base/jdk.internal.reflect=ALL-UNNAMED -Dfile.encoding=UTF-8 -Xmx32m -Xms32m -XX:+UseSerialGC -Xloggc:/tmp/container.gc -Xjit:verbose="{compileStart|compileEnd|inlining},vlog=/tmp/container.jit" -XcompilationThreads1 -Xshareclasses:cacheDir=./javaSharedCache,readonly -Xquickstart -jar ./proxy-all.jar >/dev/null &
#    java -Xmx32m -Xms32m -XX:+UseSerialGC -jar ./proxy-all.jar >/dev/null &
}

start_graal() {
  ./apps/app-"$APP" >/dev/null &
}

do_graal_benchmark
sleep 2
do_hotspot_benchmark
