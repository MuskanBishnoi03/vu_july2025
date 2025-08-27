
# Welcome to your CDK Python project!

# AWS CDK – 1-URL Website Canary (Python)

This project deploys one Python *AWS Lambda* that checks the health of *Medilink's website* every 5 minutes and sends two CloudWatch metrics per site:

- *Availability* – 1 (HTTP 2xx) or 0 (failure/timeout)
- *LatencyMs* – end-to-end HTTP time in *milliseconds*

Default target (editible in modules/sites.json):
- *Medilinks* – https://medilinks.com.au/
-

---

## What gets deployed

- *Lambda*: WebCanary (handler canary.handler)  
  Reads modules/sites.json, probes each URL (with a friendly User-Agent), and publishes metrics to the *Canary* namespace with SiteName=<name>.

- *EventBridge Rule: CanarySchedule – runs **every 5 minutes*.

- *CloudWatch Metrics* (per site):  
  Canary/Availability (Average 5m) and Canary/LatencyMs (p95 5m).

- *CloudWatch Alarms* (per site):  
  - *Latency p95 > 2000 ms* (1× 5-minute period, missing data = not breaching)  
  - *Availability < 1.0* (there was at least one failure in the 5-minute window)

- *CloudWatch Dashboard*: url-canary-dashboard  
  One graph per site (Latency on left axis, Availability on right axis), two KPI tiles per site, plus an Alarm Status widget.

---





