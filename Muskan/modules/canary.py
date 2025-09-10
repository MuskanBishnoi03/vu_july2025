'''
    import os, time, urllib.request, json
    import boto3

    cw = boto3.client("cloudwatch")
    URL = os.environ["TARGET_URL"]
    NAMESPACE = os.environ.get("NAMESPACE", "Canary")
    SITE = os.environ.get("SITE_NAME", "MainSite")

    def _put(metric, value, unit=None):
        datum = {"MetricName": metric, "Value": float(value),
                "Dimensions": [{"Name": "SiteName", "Value": SITE}]}
        if unit:
            datum["Unit"] = unit
        cw.put_metric_data(Namespace=NAMESPACE, MetricData=[datum])

    def handler(event, context):
        start = time.time()
        ok = 0
        latency_ms = 0.0
        try:
            with urllib.request.urlopen(URL, timeout=10) as r:
                latency_ms = (time.time() - start) * 1000.0
                # count 2xx as success; (optional) treat 3xx as success by changing <400
                ok = 1 if 200 <= r.status < 300 else 0
        except Exception:
            latency_ms = (time.time() - start) * 1000.0
            ok = 0

        _put("LatencyMs", latency_ms, unit="Milliseconds")
        _put("Availability", ok)

        return {"ok": ok, "latency_ms": round(latency_ms, 1)}
'''

'''
import os, time, urllib.request, json
import boto3
from pathlib import Path

cw = boto3.client("cloudwatch")
NAMESPACE = os.environ.get("NAMESPACE", "Canary")

def _put(site, metric, value, unit=None):
    datum = {
        "MetricName": metric,
        "Value": float(value),
        "Dimensions": [{"Name": "SiteName", "Value": site}]
    }
    if unit:
        datum["Unit"] = unit
    cw.put_metric_data(Namespace=NAMESPACE, MetricData=[datum])

def handler(event, context):
    # load websites.json packaged with Lambda
    config_path = Path(__file__).resolve().parent / "websites.json"
    with open(config_path, "r") as f:
        sites = json.load(f)

    results = []

    for site in sites:
        name = site["SITE_NAME"]
        url = site["TARGET_URL"]

        start = time.time()
        ok = 0
        latency_ms = 0.0

        try:
            with urllib.request.urlopen(url, timeout=10) as r:
                latency_ms = (time.time() - start) * 1000.0
                ok = 1 if 200 <= r.status < 300 else 0
        except Exception:
            latency_ms = (time.time() - start) * 1000.0
            ok = 0

        _put(name, "LatencyMs", latency_ms, unit="Milliseconds")
        _put(name, "Availability", ok)

        results.append({"site": name, "ok": ok, "latency_ms": round(latency_ms, 1)})

    return results
'''

import os, time, urllib.request, json
import boto3
from pathlib import Path

cw = boto3.client("cloudwatch")
NAMESPACE = os.environ.get("NAMESPACE", "Canary")

def _put(site, metric, value, unit=None):
    datum = {
        "MetricName": metric,
        "Value": float(value),
        "Dimensions": [{"Name": "SiteName", "Value": site}]
    }
    if unit:
        datum["Unit"] = unit
    cw.put_metric_data(Namespace=NAMESPACE, MetricData=[datum])

def handler(event, context):
    # websites.json lives alongside this file inside the Lambda bundle
    config_path = Path(__file__).resolve().parent / "websites.json"
    with open(config_path, "r") as f:
        sites = json.load(f)

    results = []
    for site in sites:
        name = site["SITE_NAME"]
        url = site["TARGET_URL"]

        start = time.time()
        ok = 0
        latency_ms = 0.0

        try:
            # Use a browser-like User-Agent so sites like LeetCode don't 403 us
            req = urllib.request.Request(
                url,
                headers={
                    "User-Agent": (
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/124.0.0.0 Safari/537.36"
                    ),
                    "Accept": "*/*",
                    "Connection": "close",
                },
            )
            with urllib.request.urlopen(req, timeout=10) as r:
                latency_ms = (time.time() - start) * 1000.0
                status = getattr(r, "status", r.getcode())  # works across Py versions

            # Count 2xx only as success. If you want redirects OK, switch to: status < 400
            ok = 1 if 200 == status < 300 else 0

            # Helpful log line in CloudWatch Logs
            print(f"[canary] site={name} url={url} status={status} latency_ms={latency_ms:.1f}")
        except Exception as e:
            latency_ms = (time.time() - start) * 1000.0
            ok = 0
            print(f"[canary] site={name} url={url} ERROR={e} latency_ms={latency_ms:.1f}")

        _put(name, "LatencyMs", latency_ms, unit="Milliseconds")
        _put(name, "Availability", ok)

        results.append({"site": name, "ok": ok, "latency_ms": round(latency_ms, 1)})

    return results
