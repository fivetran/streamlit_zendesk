import streamlit as st
import plost
import pandas as pd
import numpy as np
from datetime import datetime
from functions.filters import date_filter, optional_filters, filter_data
from functions.variables import database_schema_variables, destination_selection

st.sidebar.header('Data Connection Variables')
destination = destination_selection()
database, schema = database_schema_variables()

st.title('Zendesk Assignee Activity')

if database == "Database" or schema == "Schema":
    st.warning('To leverage your own internal data, you will need to fork this repo and deploy as your own Streamlit app. Please see the README for additional details.')
else:
    ## Define the top level date filter
    data, d = date_filter(dest=destination, db=database, sc=schema)
    ## Include the optional filters as well
    filter_dict, selected_groups, selected_brands, selected_channels, selected_forms, selected_submitter_roles, selected_req_organizations, selected_assignee = optional_filters(data_ref=data, include_assignee=True)


    ## End filter section
    st.markdown('---')

    ## Only generate the tiles if date range is populated
    if d is not None and len(d) == 2:
        start_date, end_date = d
        if start_date is not None:

            ## Filter data based on filters applied
            data_date_filtered = filter_data(start=start_date, end=end_date, data_ref=data, filter_dictionary=filter_dict)

            #####################################################################################################
            ## KPIs and Metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.subheader('Solved tickets')
                ticket_unsolved_count = len(data_date_filtered.query("`status` == 'solved'"))
                st.metric("Count of solved tickets", ticket_unsolved_count, delta=None, delta_color="normal", help=None, label_visibility="visible")

            with col2:
                st.subheader('One touch tickets')
                one_touch_resolution_percentage = (data_date_filtered['is_one_touch_resolution'].sum() / len(data_date_filtered)) * 100
                st.metric("One touch tickets percent", value=f'{one_touch_resolution_percentage:.2f}%', delta=None, delta_color="normal", help=None, label_visibility="visible")

            with col3:
                st.subheader('Two touch tickets')
                two_touch_resolution_percentage = (data_date_filtered['is_two_touch_resolution'].sum() / len(data_date_filtered)) * 100
                st.metric("Two touch tickets percent", value=f'{two_touch_resolution_percentage:.2f}%', delta=None, delta_color="normal", help=None, label_visibility="visible")

            col4, col5 = st.columns(2)
            with col4:
                st.subheader('Requester wait time median')
                median_wait_time = data_date_filtered['requester_wait_time_in_calendar_minutes'].median()
                st.metric("Median Requester Wait Time", f"{median_wait_time} minutes", delta=None)

            with col5:
                st.subheader('Assignment to resolution')
                median_time = data_date_filtered['first_assignment_to_resolution_calendar_minutes'].median()
                st.metric(label="Median time from first assignment to full resolution", value=f'{median_time} minutes', delta=None)
            #####################################################################################################

            st.markdown('---')

            #####################################################################################################
            col1, col2 = st.columns(2)
            with col1:
                st.subheader('Good vs bad satisfaction tickets')
                satisfaction_data = data_date_filtered.copy()
                satisfaction_data = satisfaction_data.dropna(subset=['ticket_satisfaction_score'])

                # Calculate the counts of each satisfaction score
                satisfaction_counts = satisfaction_data['ticket_satisfaction_score'].value_counts()
                
                # Convert counts to percentages
                satisfaction_percentages = (satisfaction_counts / satisfaction_data['ticket_satisfaction_score'].count() * 100).round(2)
                satisfaction_percentages = satisfaction_percentages.reset_index().rename(columns={'index':'Satisfaction Score', 'count':'percent'})
                satisfaction_percentages = satisfaction_percentages.reset_index().rename(columns={'index':'Satisfaction Score', 'ticket_satisfaction_score':'rating'})

                # # Display a pie chart in Streamlit
                plost.pie_chart(
                    data=satisfaction_percentages,
                    theta='percent',
                    color='rating'
                )

            with col2:
                st.subheader('Tickets by requester wait time brackets')
                adj_date_filter = data_date_filtered.copy()
                adj_date_filter['requester_wait_time_in_calendar_minutes'] = pd.cut(adj_date_filter['requester_wait_time_in_calendar_minutes'], 
                                                                bins=[0, 60, np.inf], 
                                                                labels=['0-1 hours', '>7 hours'])

                # Count the number of tickets in each category
                wait_time_counts = adj_date_filter['requester_wait_time_in_calendar_minutes'].value_counts()

                # Calculate the percentages
                wait_time_percentages = (wait_time_counts / len(adj_date_filter) * 100).round(2)

                # Convert to DataFrame for easier plotting
                df_wait_time = pd.DataFrame({'Category': wait_time_percentages.index, 
                                            'Percentage': wait_time_percentages.values})

                # Plot in Streamlit
                st.bar_chart(df_wait_time.set_index('Category'))
            #####################################################################################################

            st.markdown('---')

            #####################################################################################################
            st.subheader('Created tickets and median requester wait time by date')

            grouped_data = data_date_filtered.copy()
            grouped_data['created_at'] = pd.to_datetime(grouped_data['created_at']).dt.tz_localize(None).dt.date
            grouped_data['requester_wait_time_in_calendar_minutes'] = pd.to_numeric(grouped_data['requester_wait_time_in_calendar_minutes'], errors='coerce')

            # Group by date and calculate median requester wait time and ticket counts
            df_grouped = grouped_data.groupby('created_at').agg({'requester_wait_time_in_calendar_minutes': 'median', 
                                                                        'ticket_id': 'count'}).reset_index()
            # Rename columns for clarity
            df_grouped.rename(columns={'requester_wait_time_in_calendar_minutes': 'Median Wait Time', 'ticket_id': 'Number of Tickets'}, inplace=True)

            # Convert the dates to string format for better display in Streamlit
            df_grouped['created_at'] = df_grouped['created_at'].apply(lambda x: x.strftime('%m-%d'))
            
            # Create the bar chart in Streamlit
            plost.bar_chart(
                data=df_grouped,
                bar='created_at',
                value=['Median Wait Time', 'Number of Tickets'],
                direction='horizontal',
                group=True
            )
            #####################################################################################################

            st.markdown('---')

            #####################################################################################################
            st.subheader('Assignee activity')
            st.caption('Median metrics reported in hours')

            table_data = data_date_filtered.copy()
            table_data['requester_wait_time_in_calendar_minutes'] = pd.to_numeric(table_data['requester_wait_time_in_calendar_minutes'], errors='coerce')

            # Group by assignee_name and calculate metrics
            grouped = table_data.groupby('assignee_name').agg(
                solved_tickets_count=pd.NamedAgg(column='status', aggfunc=lambda x: (x == 'solved').sum()),
                first_reply_time_median=pd.NamedAgg(column='first_reply_time_calendar_minutes', aggfunc=lambda x: round(x.median() / 60, 2)),
                requester_wait_time_median=pd.NamedAgg(column='requester_wait_time_in_calendar_minutes', aggfunc=lambda x: round(x.median() / 60, 2)),
                last_assignment_resolution_time_median=pd.NamedAgg(column='last_assignment_to_resolution_calendar_minutes', aggfunc=lambda x: round(x.median() / 60, 2)),
                final_resolution_time_median=pd.NamedAgg(column='final_resolution_calendar_minutes', aggfunc=lambda x: round(x.median() / 60, 2))
            )

            # Reset the index to make 'assignee_name' a column in the DataFrame
            grouped.reset_index(inplace=True)

            rows_per_page = 10

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

            # Display the table in Streamlit
            # st.table(grouped)

    else:
        st.warning('Please ensure both start date and end date are selected.')