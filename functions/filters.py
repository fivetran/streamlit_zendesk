import streamlit as st
from datetime import datetime, timedelta
from functions.query import query_results

def date_filter(dest, db, sc):
    data = query_results(destination=dest, database=db, schema=sc)

    # Extract the maximum date from your data
    latest_date_in_data = max(data['created_at'])

    # Compute the end of the week for the latest date
    end_of_week = latest_date_in_data - timedelta(days=(latest_date_in_data.weekday() - 6))

    # Compute the start of the two-week period
    start_of_two_weeks = end_of_week - timedelta(days=13)

    # Check if the dates are already in session state, otherwise set them
    if 'start_date' not in st.session_state:
        st.session_state.start_date = start_of_two_weeks
    if 'end_date' not in st.session_state:
        st.session_state.end_date = end_of_week

    # Use the session state dates for the date_input
    date_range = st.date_input(
        "(Required) Select your date range",
        (st.session_state.start_date, st.session_state.end_date)
    )

    # Update the session state with the selected dates
    st.session_state.start_date, st.session_state.end_date = date_range

    return data, date_range

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

def filter_data(start, end, data_ref, filter_dictionary):
    data_date_filtered = data_ref.query("`created_at` >= @start and `created_at` <= @end")
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