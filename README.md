# Overview

A set of scripts to build reports based on pagerduty incidents or datadog warnings.

Very hastily written / poor quality - sorry !:)

# Usage

## Pageduty report

`python generate_pagerduty_report.py --api-key your-api-key --service-id your-service-id`

Example: `python generate_pagerduty_report.py --start_date="2020-11-17" --end_date="2020-11-22" --service_id=example --api_key=exampleexample-exampl --freq_report `

* To get your API key, visit [pagerduty](https://attentivemobile.pagerduty.com/) -> My Profile -> User Settings -> "Create API User Token"
* To get your service id, visit [pagerduty](https://attentivemobile.pagerduty.com/) -> Service directory -> Your Service. Then copy the service ID from the URL
  * e.g. in https://attentivemobile.pagerduty.com/service-directory/PSMEHHA the PSMEHHA is for the analytics team.


## Datadog report

`ruby datadog_report.rb "your-datadog-api-key-secret-id" "datadog-application-key" "slack-group" "start-date" "end-date"`

Example: `ruby datadog.rb "prod/analytics/analytics_dd_api_key" "6ab1c29dedffffffffffffffffffffffff" "slack-analytics-alerts" "2020-11-01" "2020-11-08" >> datadog_report.csv`

* Auth is done through AWS secrets manager, so you will need access to the analytics datadog API key in secrets managerand to be authenticated using SAML. To see if you have access, you can run the below:
  * `aws secretsmanager get-secret-value --secret-id prod/analytics/analytics_dd_api_key`
* You will also need the datadog application key. You can get this by visiting [here](https://app.datadoghq.com/access/application-keys) and hovering over "Report Generation"
* If you have access to `prod/analytics/analytics_dd_api_key` then `ruby "prod/analytics/analytics_dd_api_key" "slack-group"` should work for you
* The `slack-group` is a search string used to match your slack group. 
  * E.g. `slack-analytics-alerts` will match monitors firing for the [analytic's team's notifications](https://app.datadoghq.com/monitors/manage?q=notification%3Aslack-analytics-alerts)

