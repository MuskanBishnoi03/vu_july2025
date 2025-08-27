
# Welcome to your CDK Python project!

# AWS CDK – 1-URL Website Canary (Python)

This project deploys one Python *AWS Lambda* that checks the health of *Medilink's website* every 5 minutes and sends two CloudWatch metrics per site:

- *Availability* – 1 (HTTP 2xx) or 0 (failure/timeout)
- *LatencyMs* – end-to-end HTTP time in *milliseconds*

Availability is going to show that how frequently the website is available and latency will tell us about the loading time of site. If it takes more time to load, as per our application if more than 0.5 sec, it will give us an alarm. 

Default target (editible in modules/sites.json):
- *Medilinks* – https://medilinks.com.au/

We will going to monitor this website's working.

---

## What gets deployed

- *Lambda*: WebCanary (handler canary.handler) file
  Reads modules/sites.json, probes each URL (with a friendly User-Agent), and publishes metrics to the *Canary* namespace with SiteName=<name>.
  WE can define the code for website to collect availability and latency in canary file.
  This will take code from canary file and add it to the infrastructure in stack file.

- We scheduled the canary file to run  cloudwatch every 5 min

- *CloudWatch Metrics* (per site):  
  Canary/Availability (Average 5m) : this will run cloudwatch every 5 mins and update it on the
  and Canary/LatencyMs (p95 5m). For latency, it will show alarm every 2 secs if it takes more time.

- *CloudWatch Alarms* (per site):  
  - *Latency p95: If  it goes up by 2 sec, it wil show alarm
  - *Availability < 1 or 0, if it shows 1 it is working and if 0 then not.

- *CloudWatch Dashboard*: url-canary-dashboard  
  One graph per site (Latency on left axis, Availability on right axis)
  Graph shows the statistucs for both of the metrics.

---





