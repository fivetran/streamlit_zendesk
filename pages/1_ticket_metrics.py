import streamlit as st
import plost
import pandas as pd
import numpy as np
from datetime import datetime
from functions.filters import date_filter, optional_filters, filter_data
from functions.variables import database_schema_variables, destination_selection

## Apply standard page settings.
st.set_page_config(
    layout="wide",
    initial_sidebar_state="expanded",
)

# Hide sidebar with custom query param (used for embeding the app in Fivetran)
hide_sidebar = st.query_params.get('hide_sidebar', 'false').lower() == 'true'
if hide_sidebar:
    st.markdown(
        """
        <style>
            [data-testid="stSidebar"] {
                display: none;
            }
        </style>
        """,
        unsafe_allow_html=True
    )

st.sidebar.header('Data Connection Variables')
destination = destination_selection()
database, schema = database_schema_variables()

st.title('Zendesk Ticket Metrics')

if destination in ("BigQuery","Snowflake") and (database in ("Database", "None") or schema in ("Schema", "None")):
    st.warning('To leverage your own internal data, you will need to fork this repo and deploy as your own Streamlit app. Please see the README for additional details.')
else:
    ## Define the top level date filter
    data, d = date_filter(dest=destination, db=database, sc=schema)

    ## Include the optional filters as well
    filter_dict, selected_groups, selected_brands, selected_channels, selected_forms, selected_submitter_roles, selected_req_organizations = optional_filters(data_ref=data, include_assignee=False)

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
                st.subheader('Created tickets')
                ticket_created_count = len(data_date_filtered)
                st.metric("Count of created tickets", ticket_created_count, delta=None, delta_color="normal", help=None, label_visibility="visible")

            with col2:
                st.subheader('Unsolved tickets')
                ticket_unsolved_count = len(data_date_filtered.query("`status` != 'solved'"))
                st.metric("Count of unsolved tickets", ticket_unsolved_count, delta=None, delta_color="normal", help=None, label_visibility="visible")

            with col3:
                st.subheader('Solved tickets')
                ticket_unsolved_count = len(data_date_filtered.query("`status` == 'solved'"))
                st.metric("Count of solved tickets", ticket_unsolved_count, delta=None, delta_color="normal", help=None, label_visibility="visible")
            #####################################################################################################

            #####################################################################################################
            ## Bar chart: Tickets created by hour
            st.subheader('Tickets created by hour')
            ticket_by_hour_data = data_date_filtered.copy()

            ticket_by_hour_data['created_timestamp'] = pd.to_datetime(ticket_by_hour_data['created_timestamp'])
            ticket_by_hour_data['hour'] = ticket_by_hour_data['created_timestamp'].dt.hour
            # Count the number of tickets created each hour
            hourly_tickets = ticket_by_hour_data.groupby('hour')['ticket_id'].count()
            # Calculate the percentage
            total_tickets = hourly_tickets.sum()
            hourly_percentage = ((hourly_tickets / total_tickets) * 100).round(2)

            st.bar_chart(hourly_percentage)
            #####################################################################################################

            #####################################################################################################
            ## Bar chart: Average tickets created by day of week
            st.subheader('Average tickets created by day of week')
            avg_ticket_by_day_week = data_date_filtered.copy()

            # Convert 'created_at' to datetime and extract day of week if it's not already in that format
            avg_ticket_by_day_week['created_at'] = pd.to_datetime(avg_ticket_by_day_week['created_at'])
            avg_ticket_by_day_week['day_of_week'] = avg_ticket_by_day_week['created_at'].dt.day_name()

            # Define the correct order for days of the week
            correct_order = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
            avg_ticket_by_day_week['day_of_week'] = pd.Categorical(avg_ticket_by_day_week['day_of_week'], categories=correct_order, ordered=True)

            # Group by day of week and count tickets
            daily_tickets = avg_ticket_by_day_week.groupby('day_of_week')['ticket_id'].count()

            # Calculate the average
            total_days = len(avg_ticket_by_day_week['created_at'].dt.normalize().unique())
            average_daily_tickets = (daily_tickets / total_days).round(2)

            # Plot the time series using Streamlit
            st.bar_chart(average_daily_tickets)
            #####################################################################################################

            #####################################################################################################
            ## Bar chart for tickets created and solved by date
            st.subheader('Tickets created by date')
            tickets_solve_date = data_date_filtered.copy()

            # Convert 'created_at' and 'first_solved_at' to datetime, make them timezone naive, and extract date
            tickets_solve_date['created_at'] = pd.to_datetime(tickets_solve_date['created_at']).dt.tz_localize(None).dt.date
            tickets_solve_date['first_solved_at'] = pd.to_datetime(tickets_solve_date['first_solved_at']).dt.tz_localize(None).dt.date

            # Group by date and count the number of tickets created each day
            created_tickets = tickets_solve_date.groupby('created_at').size()

            # Filter rows where 'first_solved_at' is not null, and group by 'created_at' to count
            solved_tickets = tickets_solve_date[tickets_solve_date['first_solved_at'].notna()].groupby('created_at').size()

            # Combine the data into one DataFrame and fill NaN values with 0
            df_counts = pd.concat([created_tickets, solved_tickets], axis=1)
            df_counts.columns = ['Created Tickets', 'Solved Tickets']
            df_counts = df_counts.fillna(0)
            # Reset the index to make 'date' a column in the DataFrame
            df_counts.reset_index(inplace=True)
            df_counts.rename(columns={'index':'Date'}, inplace=True)
            # Convert the dates to string in 'YYYY-MM-DD' format
            df_counts['created_at'] = df_counts['created_at'].apply(lambda x: x.strftime('%m-%d'))

            # Plot the time series using Streamlit
            # pt.bar_chart(df_counts)
            plost.bar_chart(
                data=df_counts,
                bar='created_at',
                value=['Created Tickets', 'Solved Tickets'],
                direction='horizontal',
                group=True
            )
            #####################################################################################################

            #####################################################################################################
            # Ticket by selected attributes
            option = st.selectbox(
                'Please select an attribute to drill down',
                ('ticket_brand', 'ticket_channel', 'ticket_form', 'ticket_group', 'ticket_priority', 'ticket_type')
            )

            att_data = data_date_filtered.copy()
            st.write('You selected:', option)

            st.subheader('Tickets by selected attribute (top 10)')
            # Count the number of occurrences of each unique brand name
            attribute_counts = att_data[option].value_counts()

            # Keep only the top 10 brands
            top_attributes = attribute_counts.nlargest(10)

            # Convert the counts to percentages
            top_attributes_percentages = top_attributes / top_attributes.sum() * 100

            # Plot the percentages using Streamlit
            st.bar_chart(top_attributes_percentages)
            #####################################################################################################

            #####################################################################################################
            ## Tickets created by date and selected attribute
            st.subheader('Tickets created by date and selected attribute (top 10)')
            att_data['created_at'] = pd.to_datetime(att_data['created_at']).dt.tz_localize(None).dt.date.astype(str)

            df_counts = att_data.groupby(['created_at', option]).size().reset_index(name='Number of Tickets')

            pivot_df = df_counts.pivot(index='created_at', columns=option, values='Number of Tickets')

            # Display the plot in Streamlit
            st.bar_chart(pivot_df)
            #####################################################################################################

            st.markdown('---')

            #####################################################################################################
            # Charts for tickets created per year by month
            st.subheader('Tickets created by month/year')
            # Extract year and month from the date
            data['created_at'] = pd.to_datetime(data['created_at'])
            data['year'] = data['created_at'].dt.year
            data['month'] = data['created_at'].dt.month

            # Get the list of unique years
            years = sorted(data['year'].unique())

            # Sidebar multiselect for years
            selected_years = st.multiselect('Select years', years, default=years)

            # Filter data for selected years
            df_selected = data[data['year'].isin(selected_years)]

            # Group by year and month and count the number of tickets
            df_counts = df_selected.groupby(['year', 'month']).size().reset_index(name='Number of Tickets')

            # Pivot the data for the plot
            df_pivot = df_counts.pivot(index='month', columns='year', values='Number of Tickets')

            # Display the plot in Streamlit
            st.bar_chart(df_pivot)
            #####################################################################################################

    else:
        st.warning('Please ensure both start date and end date are selected.')

