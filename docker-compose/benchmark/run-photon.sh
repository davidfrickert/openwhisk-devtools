ab -n 5000 -c10 -p data-sleep -T application/json \
 -H "Authorization: Basic MjNiYzQ2YjEtNzFmNi00ZWQ1LThjNTQtODE2YWE0ZjhjNTAyOjEyM3pPM3haQ0xyTU42djJCS0sxZFhZRnBYbFBrY2NPRnFtMTJDZEFzTWdSVTRWck5aOWx5R1ZDR3VNREdJd1A=" \
 -H "Content-Type: application/json" -H "User-Agent: OpenWhisk-CLI/1.0 (2019-09-23T17:46:38.323+0000) linux 386"  \
 "https://localhost/api/v1/namespaces/_/actions/sleep-photon?blocking=true&result=true"
