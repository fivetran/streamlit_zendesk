import streamlit as st
from datetime import datetime, timedelta
from functions.query import query_results

def date_filter(dest, db, sc, md='ticket'):
    current_date = datetime.today().date()
    start_of_week = current_date - timedelta(days=(current_date.weekday() + 1) % 7)
    end_of_week = start_of_week + timedelta(days=6)

    data = query_results(destination=dest, database=db, schema=sc, model=md)

    # Define top level filters
    ## Time frame for all chats on the page
    d = st.date_input(
        "(Required) Select your date range",
        (start_of_week, end_of_week)
    )

    return data, d

def optional_filters(data_ref, include_assignee):
    opt1, opt2, opt3 = st.columns(3)
    with opt1:
        selected_groups = st.multiselect('(Optional) Groups to filter', data_ref['ticket_group'].unique(), default=None)
    with opt2:
        selected_brands = st.multiselect('(Optional) Brands to filter', data_ref['ticket_brand'].unique(), default=None)
    with opt3:
        selected_channels = st.multiselect('(Optional) Channels to filter', data_ref['ticket_channel'].unique(), default=None)

    opt3, opt4, opt5 = st.columns(3)
    with opt3:
        selected_forms = st.multiselect('(Optional) Forms to filter', data_ref['ticket_form'].unique(), default=None)
    with opt4:
        selected_submitter_roles = st.multiselect('(Optional) Submitter roles to filter', data_ref['submitter_role'].unique(), default=None)
    with opt5:
        selected_req_organizations = st.multiselect('(Optional) Requester orgs to filter', data_ref['requester_organization'].unique(), default=None)

    if include_assignee:
        selected_assignee = st.multiselect('(Optional) Assignee(s) to filter', data_ref['assignee_name'].unique(), default=None)
        filter_dict = {'ticket_group': selected_groups, 'ticket_brand': selected_brands, 'ticket_channel': selected_channels, 'ticket_form': selected_forms,'submitter_role': selected_submitter_roles, 'requester_organization': selected_req_organizations, 'assignee_name': selected_assignee}
        
        return filter_dict, selected_groups, selected_brands, selected_channels, selected_forms, selected_submitter_roles, selected_req_organizations, selected_assignee

    else:
        filter_dict = {'ticket_group': selected_groups, 'ticket_brand': selected_brands, 'ticket_channel': selected_channels, 'ticket_form': selected_forms,'submitter_role': selected_submitter_roles, 'requester_organization': selected_req_organizations}
        
        return filter_dict, selected_groups, selected_brands, selected_channels, selected_forms, selected_submitter_roles, selected_req_organizations

def sla_optional_filters(data_ref):
    opt1, opt2, opt3 = st.columns(3)
    with opt1:
        selected_sla_name = st.multiselect('(Optional) SLA policy name to filter', data_ref['sla_policy_name'].unique(), default=None)
    with opt2:
        selected_metric = st.multiselect('(Optional) SLA metric to filter', data_ref['metric'].unique(), default=None)
    with opt3:
        selected_group = st.multiselect('(Optional) Groups to filter', data_ref['ticket_group'].unique(), default=None)

    opt4, opt5, opt6 = st.columns(3)
    with opt4:
        selected_req_organizations = st.multiselect('(Optional) Requester orgs to filter', data_ref['requester_organization'].unique(), default=None)
    with opt5:
        selected_brands = st.multiselect('(Optional) Brands to filter', data_ref['ticket_brand'].unique(), default=None)
    with opt6:
        selected_forms = st.multiselect('(Optional) Forms to filter', data_ref['ticket_form'].unique(), default=None)

    filter_dict = {'sla_policy_name': selected_sla_name, 'metric': selected_metric, 'ticket_group': selected_group, 'requester_organization': selected_req_organizations,'ticket_brand': selected_brands, 'ticket_form': selected_forms}
    
    return filter_dict, selected_sla_name, selected_metric, selected_group, selected_req_organizations, selected_brands, selected_forms

def filter_data(start, end, data_ref, filter_dictionary, model='ticket'):
    if model == "ticket":
        data_date_filtered = data_ref.query("`created_at` >= @start and `created_at` <= @end")
    elif model == "sla": 
        data_date_filtered = data_ref.query("`sla_applied_at` >= @start and `sla_applied_at` <= @end")
        
    for k, v in filter_dictionary.items():
        if len(v) == 0 or None in v:
            data_date_filtered = data_date_filtered
        else:
            list_var = []
            for i in v:
                list_var.append(i)
            list_var_tuple = tuple(list_var)
            data_date_filtered = data_date_filtered.query(f"`{k}` in {list_var_tuple}")

    return data_date_filtered