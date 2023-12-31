# Fivetran Zendesk Streamlit App
## 📣 Overview

The [Fivetran Zendesk Streamlit app](https://fivetran-zendesk.streamlit.app/) leverages data from the Fivetran Zendesk connector and Fivetran Zendesk data model to produce analytics ready reports. You may find the analytics ready reports within the pages of this Streamlit app (these may be found on the left pane). These dashboards have been constructed using the [zendesk__ticket_metrics](https://fivetran.github.io/dbt_zendesk/#!/model/model.zendesk.zendesk__ticket_metrics) model from the Fivetran [Zendesk dbt package](https://github.com/fivetran/dbt_zendesk). These dashboards provide an example of how you may analyze your Zendesk data.

By default this Streamlit app uses sample Dunder Mifflin Zendesk tickets data to generate the dashboards. This sample data is a replica of the `zendesk__ticket_metrics` data model output. If you would like to leverage this app with your own data, you may follow the instructions within the below Installation and Deployment section.

## 📈 Provided reports

| **Page** | **Description** |
|----------|-----------------|
| [Ticket Metrics](https://fivetran-zendesk.streamlit.app/1_ticket_metrics) | This report is meant to provide a breakdown of all your Zendesk tickets created within a specified time frame. You can view high level metrics such as total created/solved/unsolved tickets while also being able to understand trends associated with your ticket volume broken down by attribute. |
| [Assignee Activity](https://fivetran-zendesk.streamlit.app/2_assignee_activity) | This report includes a breakdown of assignee activity within Zendesk and understand overall agent performance when working within tickets for the specified time frame. |
| [SLA Policies](https://fivetran-zendesk.streamlit.app/3_sla_policies) | This report provides an overview of all your achieved and breached ticket SLA Policies across tickets within a specified date range. Use this report to gain insights into how you are performing against your SLA targets. |

# 🎯 How do I use this Streamlit app?
As previously mentioned this Streamlit App is publicly deployed using sample Dunder Mifflin Zendesk ticket data. This is to show an example of the types of analysis that may be performed with modeled Zendesk data synced and transformed with Fivetran. However, this Streamlit App has been designed to be also be forked and customize to leverage other data sources. If you wish to leverage this Streamlit App with your own modeled Zendesk data, you may follow the below steps.

## Step 1: Prerequisites
To use this Streamlit app, you must have the following:

- At least one Fivetran Zendesk connector syncing data into your destination.
- A **BigQuery** or **Snowflake** destination.

## Step 2: Data models
You will need to have ran the [Fivetran dbt_zendesk data model](https://github.com/fivetran/dbt_zendesk) to transform your raw Zendesk data into analytics ready tables. Please refer to the data model documentation for instructions on how to run the data models. If you would like to have Fivetran run these data models for you, you may also leverage the [Fivetran Zendesk Quickstart Data Model](https://fivetran.com/docs/transformations/quickstart) for an easier experience.

## Step 3: Fork this repository
To leverage this Streamlit App with your own data, you will need to fork this repo. To learn more about forking repos you may refer to the [GitHub docs](https://docs.github.com/en/get-started/quickstart/fork-a-repo).

## Step 4: Run your forked Streamlit app
Once you have forked the repo, you will need to clone the repo locally to run it and make any minor adjustments. To do this you will perform the following:
- Start a virtual environment and install the requirements. You can use the following commands to create a venv and setup the environment with the appropriate dependencies:
```zsh
python3 -m pip install --user virtualenv && 
python3 -m venv env && 
source env/bin/activate && 
python3 -m pip install --upgrade pip && 
pip3 install -r requirements.txt
```
- If using BigQuery: Obtain/Create a BigQuery Service account with `BigQuery Data Editor` and `BigQuery User` permissions and access to the zendesk__ticket_metrics table.
- If using Snowflake: Obtain/Create an account with access permissions to the zendesk__ticket_metrics model generated by the table.
- Store the credential for your account in a `secrets.toml` file stored within the `.streamlit/` folder.
- Run `streamlit run zendesk.py` in your terminal to deploy the app on your local host.
- Change the Destination variable in the app to be either BigQuery or Snowflake
- Modify the Database and Schema variables in the app to be your designated database.schema where the zendesk__ticket_metrics table resides.