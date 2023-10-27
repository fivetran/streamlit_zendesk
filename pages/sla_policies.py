import streamlit as st
from functions.filters import date_filter
from functions.filters import date_filter, sla_optional_filters, filter_data
from functions.variables import database_schema_variables, destination_selection

st.sidebar.header('Data Connection Variables')
destination = destination_selection()
database, schema = database_schema_variables()

st.title('Zendesk SLA Policies')


if destination in ("BigQuery","Snowflake") and (database in ("Database", "None") or schema in ("Schema", "None")):
    st.warning('To leverage your own internal data, you will need to fork this repo and deploy as your own Streamlit app. Please see the README for additional details.')
else:
    ## Define the top level date filter
    data, d = date_filter(dest=destination, db=database, sc=schema, md="sla")

    filter_dict, selected_sla_name, selected_metric, selected_group, selected_req_organizations, selected_req_organizations, selected_forms = sla_optional_filters(data_ref=data)
    ## End filter section
    st.markdown('---')

    ## Only generate the tiles if date range is populated
    if d is not None and len(d) == 2:
        start_date, end_date = d
        if start_date is not None:

            ## Filter data based on filters applied
            data_date_filtered = filter_data(start=start_date, end=end_date, data_ref=data, filter_dictionary=filter_dict, model="sla")

            #####################################################################################################
            ## KPIs and Metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.subheader('SLA achievement rate')
                achieved_slas = data_date_filtered[data_date_filtered['is_sla_breach'] == 0]
                achieved_sla_count = len(achieved_slas)
                sla_achievement_rate = (data_date_filtered['achieved_sla_count'].sum() / len(data_date_filtered)) * 100
                st.metric("SLA achievement rate",  value=f'{sla_achievement_rate:.2f}%', delta=None, delta_color="normal", help=None, label_visibility="visible")

            with col2:
                st.subheader('SLA breached tickets')
                breached_tickets = data_date_filtered[data_date_filtered['is_sla_breach'] == 1]
                breached_ticket_ids = set(breached_tickets['ticket_id'].unique())
                breached_ticket_count = len(breached_ticket_ids)
                st.metric("SLA breached tickets", breached_ticket_count, delta=None, delta_color="normal", help=None, label_visibility="visible")

            with col3:
                st.subheader('SLA achieved tickets')
                achieved_tickets = data_date_filtered[data_date_filtered['is_sla_breach'] == 0]
                achieved_ticket_ids = set(achieved_tickets['ticket_id'].unique())
                achieved_ticket_count = len(achieved_ticket_ids)
                st.metric("SLA achieved tickets", achieved_ticket_count, delta=None, delta_color="normal", help=None, label_visibility="visible")

            #####################################################################################################

            st.markdown('---')

            #####################################################################################################
  

            st.table(data_date_filtered.copy().head(10))
            # Calculate the number of pages
            n_pages = (len(grouped) - 1) // rows_per_page + 1

            # Create a state object to hold the current page
            if 'page' not in st.session_state:
                st.session_state.page = 0

            # Display the current page
            start = st.session_state.page * rows_per_page
            end = (st.session_state.page + 1) * rows_per_page
            st.table(grouped.iloc[start:end])

            # Display prev and next buttons
            if st.button('Prev'):
                st.session_state.page -= 1
            if st.button('Next'):
                st.session_state.page += 1

            # Ensure page stays within range
            st.session_state.page = max(0, min(st.session_state.page, n_pages - 1))

    else:
        st.warning('Please ensure both start date and end date are selected.')