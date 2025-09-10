AWS Webhealth Monitoring System 
# AWS CDK – 3-URL Website Canary (Python)

This will going to moniter availability and latency for the 3 websites and then publish those metrics to cloudwatch, trigger alarms if it crosses the given threshold , sends notification via SNS and then log those alrms in a dynamodb table format. 

This project deploys one Python *AWS Lambda* that checks the health of * given websites* every 5 minutes and sends two CloudWatch metrics per site:
The metrics are:
- *Availability* – 1 (HTTP 2xx) or 0 (failure/timeout)
- *LatencyMs* – end-to-end HTTP time in *milliseconds*

Availability is going to show that how frequently the website is available and latency will tell us about the loading time of site. If it takes more time to load, as per our application if more than 0.5 sec, it will give us an alarm. 

Default target (editible in modules/sites.json):
- *Medilinks* – "https://medilinks.com.au/"
- *skiptq* –   "https://skiptq.com/"
- *Leetcode* –  "https://leetcode.com/"
 We will going to monitor these website's working.

---

## What gets deployed

-*Lambda*: WebCanary (handler canary.handler) file:
   First of all, the lambda function will be launched and  will perform monitoring. It will send an http request to the target url  and then record its availability and latency.
  Reads modules/sites.json, probes each URL (with a friendly User-Agent), and publishes metrics to the *Canary* namespace with SiteName=<name>.
  WE can define the code for website to collect availability and latency in canary file.
  This will take code from canary file and add it to the infrastructure in stack file.

- We scheduled the canary file to run  cloudwatch every 5 min   



- *CloudWatch Metrics* (per site):  These are the numbers pushed by canary file.
  Canary/Availability (Average 5m) : this will run cloudwatch every 5 mins and update it on the AWS dashboard.
  and Canary/LatencyMs (p95 5m). For latency, it will show alarm every 2 secs if it takes more time to load. 
  Here we used timeout of 30s and then we also had to attach it IAM policies

<img width="1919" height="810" alt="image" src="https://github.com/user-attachments/assets/57ae73d8-de4c-47f9-8189-965755d38a72" />


- *CloudWatch Alarms* (per site):  
  - After putting the data into metrics we will going to use alarms. They will get triggered if  
  - *Latency : If  it goes up by 2 sec, it wil show alarm
  - *Availability < 1 or 0, if it shows 1 it is working and if 0 then not.
  Each alarm is bound to give us SNS notifications 

<img width="1919" height="928" alt="image" src="https://github.com/user-attachments/assets/8fb4708b-efa4-47d9-9462-5ded49071314" />


- *CloudWatch Dashboard*: url-canary-dashboard  
  -One graph per site (Latency on left axis, Availability on right axis)
  -Graph shows the statistucs for both of the metrics. Here we used 3 websites so there is going to be graph of these 3. 
   With these graphs, its easy to analyse the alarms.

  Like for medilink, the graph would be
  <img width="1846" height="934" alt="image" src="https://github.com/user-attachments/assets/71c8d075-2ff4-4f07-b929-b2c718a93e09" />



- *SNS*:
   When the metrice is published and there is any alarms, then it will automatically gets notified. We will going to get notifications on oiur registered email. These notifications will help in detecting and solving the issues in less time.
<img width="1915" height="917" alt="image" src="https://github.com/user-attachments/assets/ce4b4b00-e12b-4c10-932c-d28c2730a53a" />

- Alarm Logger: We used one sepererate file alarms to write  alarms. This will also going to  write event data  into dynamodb
  And then this file also have the dynamodb table access and will  insert alarm events into dynamodb table with an unique id. 
---

- *DynamoDB Table*:
  This table will store all the data of the alarms. Whenever an alarm triggers and the user is notified, the data will automatically get stores in this table. Which will then used to improve the application by looking what was wrong. 
The billing mode in this will be pay per request

The table would look like this

<img width="1910" height="951" alt="image" src="https://github.com/user-attachments/assets/40ee6f37-0c68-426b-970a-15d658cf5417" />


# What operaters can check:
-For the cloudwatch metrics, they can check real time metrics on cloudwatch dashboard. Which will going to show the graph for availability and latency. 

-For SNS and  alarms, they can check SNS in AWS consol which will show topics and subscription. In subscription, we can check the email where it is going to give notifucations.

-then check email for notification.

-For the tables, they can check dynamodb tables and then go to explore items, it will show the table content there for all the alarms that are logged. 

