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

            st.table(data_date_filtered.copy().head(10))
