# run a plugin, get a result
curl -X POST "http://localhost:8050/ga4gh/testbed/v1/tests" -H "accept: application/json" -H "Content-Type: application/json" -d "@test.json" > result.json

# post result to dashboard
curl -X POST "http://localhost:8060/ga4gh/testbed/v1/dashboard" -H "accept: application/json" -H "Content-Type: application/json" -d "@result.json"
