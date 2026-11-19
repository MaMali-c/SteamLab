#!/usr/bin/env python3
"""Print an actual API calculation, also checking h = u + P*v."""
import json
import sys
import urllib.request

base = sys.argv[1].rstrip("/") if len(sys.argv) > 1 else "http://localhost:8000"
payload = {"input_pair": "T_P", "values": {"T":300.0,"P":500.0}}
request = urllib.request.Request(base + "/api/calculate", data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"})
with urllib.request.build_opener(urllib.request.ProxyHandler({})).open(request, timeout=20) as response:
    result = json.load(response)
p = result["full_state"]
assert abs(p["h"] - p["u"] - p["P"] * p["v"]) < 1e-7, "Energy identity failed"
print(json.dumps({"request": payload, "response": result, "energy_identity": "passed"}, indent=2))
