# Fivetran Zendesk Streamlit App
## 📣 Overview

The [Fivetran Zendesk Streamlit app](https://fivetran-zendesk.streamlit.app/) leverages data from the Fivetran Zendesk connector and Fivetran Zendesk data model to produce analytics ready reports. You may find the analytics ready reports within the pages of this Streamlit app (these may be found on the left pane). These dashboards have been constructed using the [zendesk__ticket_metrics](https://fivetran.github.io/dbt_zendesk/#!/model/model.zendesk.zendesk__ticket_metrics) model from the Fivetran [Zendesk dbt package](https://github.com/fivetran/dbt_zendesk). These dashboards provide an example of how you may analyze your Zendesk data.

By default this Streamlit app uses sample Dunder Mifflin Zendesk tickets data to generate the dashboards. This sample data is a replica of the `zendesk__ticket_metrics` data model output.

## 📈 Example reports

| **Page** | **Description** |
|----------|-----------------|
| [Ticket Metrics](https://fivetran-zendesk.streamlit.app/ticket_metrics) | This report is meant to provide a breakdown of all your Zendesk tickets created within a specified time frame. You can view high level metrics such as total created/solved/unsolved tickets while also being able to understand trends associated with your ticket volume broken down by attribute. |
| [Assignee Activity](https://fivetran-zendesk.streamlit.app/assignee_activity) | This report includes a breakdown of assignee activity within Zendesk and understand overall agent performance when working within tickets for the specified time frame. |
| [SLA Policies](https://fivetran-zendesk.streamlit.app/assignee_activity) | This report provides an overview of all your achieved and breached ticket SLA Policies across tickets within a specified date range. Use this report to gain insights into how you are performing against your SLA targets. |

## 🎯 Call to Action
These reports are designed to demonstrate the analytical capabilities when using the Fivetran Zendesk connector paired with the corresponding Zendesk data model. We encourage you to explore these reports and provide feedback. If you find these examples useful or have suggestions for additional content, please share your thoughts via a [GitHub issue](https://github.com/fivetran/streamlit_zendesk/issues/new). 
