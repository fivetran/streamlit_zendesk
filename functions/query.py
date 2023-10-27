import streamlit as st
import pandas as pd
from google.oauth2 import service_account
from google.cloud import bigquery

# Grab global variables
destination = st.session_state.destination
database = st.session_state.database 
schema = st.session_state.schema

# Perform query.
# Uses st.cache_data to only rerun when the query changes or after 10 min.
@st.cache_data(ttl=600)
def run_query(query):
    # Create API client.
    credentials = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"]
    )
    client = bigquery.Client(credentials=credentials)
    query_job = client.query(query)
    rows_raw = query_job.result()
    # Convert to list of dicts. Required for st.cache_data to hash the return value.
    rows = [dict(row) for row in rows_raw]
    return rows

def query_results(destination, database, schema, model='ticket'):
    if destination == "BigQuery" and model == "ticket":
        query = run_query(
            "select "\
                "ticket_id,"\
                "created_at,"\
                "cast(created_at as timestamp) as created_timestamp,"\
                "status,"\
                "first_solved_at,"\
                "ticket_brand_name as ticket_brand,"\
                "created_channel as ticket_channel,"\
                "ticket_form_name as ticket_form,"\
                "group_name as ticket_group,"\
                "priority as ticket_priority,"\
                "type as ticket_type,"\
                "submitter_role,"\
                "requester_organization_name as requester_organization,"\
                "is_one_touch_resolution,"\
                "is_two_touch_resolution,"\
                "is_multi_touch_resolution,"\
                "first_assignment_to_resolution_calendar_minutes,"\
                "requester_wait_time_in_calendar_minutes,"\
                "ticket_satisfaction_score,"\
                "first_reply_time_calendar_minutes,"\
                "last_assignment_to_resolution_calendar_minutes,"\
                "final_resolution_calendar_minutes,"\
                "assignee_name "\
            "from `" + database + "." + schema + ".zendesk__ticket_metrics`"
        )
    elif destination == "Snowflake" and model == "ticket":
        conn = st.experimental_connection('snowpark')
        query_job = conn.query(
            "select "\
                "ticket_id,"\
                "created_at,"\
                "cast(created_at as timestamp) as created_timestamp,"\
                "status,"\
                "first_solved_at,"\
                "ticket_brand_name as ticket_brand,"\
                "created_channel as ticket_channel,"\
                "ticket_form_name as ticket_form,"\
                "group_name as ticket_group,"\
                "priority as ticket_priority,"\
                "type as ticket_type,"\
                "submitter_role,"\
                "requester_organization_name as requester_organization,"\
                "is_one_touch_resolution,"\
                "is_two_touch_resolution,"\
                "is_multi_touch_resolution,"\
                "first_assignment_to_resolution_calendar_minutes,"\
                "requester_wait_time_in_calendar_minutes,"\
                "ticket_satisfaction_score,"\
                "first_reply_time_calendar_minutes,"\
                "last_assignment_to_resolution_calendar_minutes,"\
                "final_resolution_calendar_minutes,"\
                "assignee_name "\
            "from " + database + "." + schema + ".zendesk__ticket_metrics"
        )


    elif destination == "BigQuery" and model == "sla":
        query = run_query(
            "select "\
                "sla.sla_event_id, "\
                "sla.ticket_id, "\
                "sla.sla_policy_name, "\
                "sla.metric, "\
                "sla.sla_applied_at, "\
                "sla.target, "\
                "sla.in_business_hours, "\
                "sla.sla_breach_at, "\
                "sla.sla_elapsed_time, "\
                "sla.is_active_sla, "\
                "sla.is_sla_breach, "\
                "ticket.group_name as ticket_group, "\
                "ticket.ticket_brand_name as ticket_brand, "\
                "ticket.ticket_form_name as ticket_form, "\
                "ticket.requester_organization_name as requester_organization, "\
                "ticket.created_channel as ticket_channel "\
        "from " + database + "." + schema + ".zendesk__sla_policies as sla "\
        "left join " + database + "." + schema + ".zendesk__ticket_metrics as ticket "\
            "on sla.ticket_id = ticket.ticket_id "
        )
        raw_results = query_job.result()
        # Convert to list of dicts. Required for st.cache_data to hash the return value.
        query = [dict(row) for row in raw_results]

    elif destination not in ("Snowflake", "BigQuery") and model == 'ticket':
        query = pd.read_csv('data/dunder_mifflin_tickets.csv')

        ## Convert csv fields for time conversions later on
        query['created_timestamp'] = pd.to_datetime(query['created_timestamp'])
        query['created_at'] = pd.to_datetime(query['created_at'])
        query['first_solved_at'] = pd.to_datetime(query['first_solved_at'])

    if model == 'ticket':
        data = pd.DataFrame(query, columns=['ticket_id','created_at','created_timestamp','status','first_solved_at','ticket_brand','ticket_channel','ticket_form','ticket_group','ticket_priority','ticket_type','submitter_role','requester_organization','is_one_touch_resolution','is_two_touch_resolution','is_multi_touch_resolution','first_assignment_to_resolution_calendar_minutes','requester_wait_time_in_calendar_minutes','ticket_satisfaction_score','first_reply_time_calendar_minutes','last_assignment_to_resolution_calendar_minutes','final_resolution_calendar_minutes','assignee_name'])

        # Get the data into the app and specify any datatypes if needed.
        data_load_state = st.text('Loading data...')
        data['created_at'] = data['created_at'].dt.date
        data['first_solved_at'] = data['first_solved_at'].dt.date
        data_load_state.text("Done! (using st.cache_data)")

    elif model == 'sla':
        data = pd.DataFrame(query, columns=['sla_event_id','ticket_id','sla_policy_name','metric','sla_applied_at','target','in_business_hours','sla_breach_at','sla_elapsed_time','is_active_sla','is_sla_breach','ticket_group','ticket_brand','ticket_form','requester_organization','ticket_channel'])

        # Get the data into the app and specify any datatypes if needed.
        data_load_state = st.text('Loading data...')
        data['sla_applied_at'] = data['sla_applied_at'].dt.date
        data_load_state.text("Done! (using st.cache_data)")

    return data