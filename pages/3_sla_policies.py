import streamlit as st
import plost
import pandas as pd
import numpy as np
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
                sla_achieved_count = len(data_date_filtered.query("`is_sla_breach` == 0"))
                total_sla_count = data_date_filtered['sla_event_id'].nunique()  # Calculate the total number of distinct sla IDs
                sla_achievement_rate = (sla_achieved_count / total_sla_count) * 100
                st.metric("SLA achievement rate",  value=f'{sla_achievement_rate:.2f}%', delta=None, delta_color="normal", help=None, label_visibility="visible")

            with col2:
                st.subheader('SLA breached tickets')
                # Filter data_date_filtered to select rows where 'is_sla_breach' is True (1).
                breached_tickets = data_date_filtered[data_date_filtered['is_sla_breach'] == 1]
                # Calculate the total count of unique ticket IDs for SLA breached tickets.
                breached_ticket_count = breached_tickets['ticket_id'].nunique()
                st.metric("SLA breached tickets", breached_ticket_count, delta=None, delta_color="normal", help=None, label_visibility="visible")

            with col3:
                st.subheader('SLA achieved tickets')
                achieved_tickets = data_date_filtered[data_date_filtered['is_sla_breach'] == 0]
                achieved_ticket_count = achieved_tickets['ticket_id'].nunique()
                st.metric("SLA achieved tickets", achieved_ticket_count, delta=None, delta_color="normal", help=None, label_visibility="visible")

            col4, col5 = st.columns(2)
            with col4:
                st.subheader('SLA active tickets')
                active_tickets = data_date_filtered[data_date_filtered['is_active_sla'] == 0]
                active_ticket_count = active_tickets['ticket_id'].nunique()
                st.metric("SLA active tickets", active_ticket_count, delta=None, delta_color="normal", help=None, label_visibility="visible")

            with col5:
                st.subheader('SLA active breached tickets')
                active_breached_tickets = data_date_filtered[(data_date_filtered['is_sla_breach'] == 1) & (data_date_filtered['is_active_sla'] == 0)]
                active_ticket_count = active_breached_tickets['ticket_id'].nunique() 
                st.metric("SLA active tickets", active_ticket_count, delta=None, delta_color="normal", help=None, label_visibility="visible")

            #####################################################################################################

            st.markdown('---')

            #################################################################################################### 
            # Create an area chart using st.area_chart.
            st.subheader('Achieved vs. breached completed SLA policies')
            sla_policies_date = data_date_filtered.copy()

            # Convert 'sla_applied_at' to datetime, make them timezone naive, and extract date
            sla_policies_date['sla_applied_at'] = sla_policies_date['sla_applied_at'].dt.date
            
            # Filter and count achieved and breached SLAs
            completed_slas = sla_policies_date[sla_policies_date['is_active_sla'] == 0]
            breached_slas = completed_slas[completed_slas['is_sla_breach'] == 1]
            achieved_slas = completed_slas[completed_slas['is_sla_breach'] == 0]

            # Group and count achieved and breached SLAs by date
            breached_counts = breached_slas.groupby('sla_applied_at').size()
            achieved_counts = achieved_slas.groupby('sla_applied_at').size()

            # Merge the counts into a single DataFrame
            combined_counts = pd.DataFrame({'Breached SLAs': breached_counts, 'Achieved SLAs': achieved_counts}).fillna(0)

            # Reset the index to make 'sla_applied_at' a column in the DataFrame
            combined_counts.reset_index(inplace=True)

            # Convert the dates to string in 'YYYY-MM-DD' format
            combined_counts['sla_applied_at'] = combined_counts['sla_applied_at'].apply(lambda x: x.strftime('%m-%d'))

            # Create an area chart with Streamlit
            plost.area_chart(
                data=combined_counts,
                x='sla_applied_at',
                y=['Breached SLAs', 'Achieved SLAs'],
                use_container_width=True
            )
            #####################################################################################################

            #####################################################################################################
            ## Bar chart: Achieved and breached completed SLA policies by selected attribute (top 10 breached):
            
            
            st.subheader('Achieved SLA Policies, top 10')
            option = st.selectbox(
                'Please select an attribute to drill down',
                ('sla_policy_name', 'ticket_brand', 'ticket_channel', 'ticket_form', 'ticket_group')
            ) 

            option_to_value = {
                'sla_policy_name': 'Value for sla_policy_name',
                'ticket_brand': 'Value for ticket_brand',
                'ticket_channel': 'Value for ticket_channel',
                'ticket_form': 'Value for ticket_form',
                'ticket_group': 'Value for ticket_group',
                'ticket_priority': 'Value for ticket_priority',
                'ticket_type': 'Value for ticket_type'
            }

            # Filter data based on the selected attribute and is_active_sla
            att_data = data_date_filtered.copy()
            filtered_data = att_data[(att_data['is_active_sla'] == 0) & (att_data['is_sla_breach'] == 0)]

            # Count the number of occurrences of each unique value for the selected attribute
            achieved_ticket_count = filtered_data[option].value_counts()

            # Keep only the top 10 values
            top_attributes = achieved_ticket_count.nlargest(10)

            # Create a bar chart for achieved SLAs
            st.bar_chart(top_attributes, use_container_width=True)

            st.subheader('Breached SLA Policies, top 10')
            # Filter data based on the selected attribute and is_active_sla
            filtered_data = att_data[(att_data['is_active_sla'] == 0) & (att_data['is_sla_breach'] == 1)]

            # Count the number of occurrences of each unique value for the selected attribute
            attribute_counts = filtered_data[option].value_counts()

            # Keep only the top 10 values
            top_attributes = attribute_counts.nlargest(10)

            # Create a bar chart for breached SLAs
            st.bar_chart(top_attributes, use_container_width=True)

            # st.subheader('Achieved and Breached SLA Policies, top 10')
            # options = st.selectbox(
            #     'Please select an attribute',
            #     ('sla_policy_name', 'ticket_brand', 'ticket_channel', 'ticket_form', 'ticket_group')
            # )
            
            # att_data = data_date_filtered.copy()
            # # Create DataFrames for achieved and breached SLAs
            # achieved_slas = att_data[(att_data['is_active_sla'] == 0) & (att_data['is_sla_breach'] == 0)]
            # breached_slas = att_data[(att_data['is_active_sla'] == 0) & (att_data['is_sla_breach'] == 1)]
 
            # # Count unique ticket IDs for achieved and breached SLAs
            # achieved_ticket_counts = achieved_slas['ticket_id'].nunique()
            # breached_ticket_counts = breached_slas['ticket_id'].nunique()

            # achieved_attribute_counts = achieved_slas[options].value_counts()
            # breached_attribute_counts = breached_slas[options].value_counts()

            # top_achieved_attributes = achieved_attribute_counts.nlargest(10).reset_index()
            # top_breached_attributes = breached_attribute_counts.nlargest(10).reset_index()
            
            # # Create DataFrames for visualization
            # data_to_visualize = pd.DataFrame({
            #     'Category': ['Achieved SLAs'] * 10 + ['Breached SLAs'] * 10,
            #     'Attribute': top_achieved_attributes['index'].tolist() + top_breached_attributes['index'].tolist(),
            #     'Count': top_achieved_attributes[option].tolist() + top_breached_attributes[option].tolist()
            # })
            
            # # Create a bar chart using Streamlit
            # st.bar_chart(data_to_visualize, use_container_width=True)
            #####################################################################################################

            #####################################################################################################
            ## Line chart: SLA target breaches by hour of day
            st.subheader('SLA target breaches by hour of day')
            sla_breaches_by_hour_data = data_date_filtered.copy()

            sla_breaches_by_hour_data['sla_breach_at'] = pd.to_datetime(sla_breaches_by_hour_data['sla_breach_at'])
            sla_breaches_by_hour_data['hour'] = sla_breaches_by_hour_data['sla_breach_at'].dt.hour
            # Count the number of tickets created each hour
            hourly_slas = sla_breaches_by_hour_data.groupby('hour')['sla_event_id'].count()
            # Calculate the percentage
            total_slas = hourly_slas.sum()
            hourly_percentage = ((hourly_slas / total_slas) * 100).round(2)

            st.line_chart(hourly_percentage)


            #####################################################################################################

            #####################################################################################################
            ## Bar chart: SLA target breaches by day of week
            st.subheader('SLA target breaches by day of week')
            sla_breaches_by_day_week = data_date_filtered.copy()

            # Convert 'created_at' to datetime and extract day of week if it's not already in that format
            sla_breaches_by_day_week['sla_breach_at'] = pd.to_datetime(sla_breaches_by_day_week['sla_breach_at'])
            sla_breaches_by_day_week['day_of_week'] = sla_breaches_by_day_week['sla_breach_at'].dt.dayofweek

            # Count the number of tickets created each day of the week
            daily_breaches = sla_breaches_by_day_week.groupby('day_of_week')['ticket_id'].count()

            # Calculate the average
            total_days = len(sla_breaches_by_day_week['sla_breach_at'].dt.normalize().unique())
            average_daily_breaches = (daily_breaches / total_days).round(2)

            # Create a dictionary to map day of week numbers to names
            days = {0:'Mon', 1:'Tue', 2:'Wed', 3:'Thu', 4:'Fri', 5:'Sat', 6:'Sun'}
            average_daily_breaches.index = average_daily_breaches.index.map(days)

            # Convert to DataFrame for easier sorting
            df_breaches = average_daily_breaches.reset_index()
            df_breaches.columns = ['Day', 'Average Breaches']

            # Custom sort order
            ordered_days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
            df_breaches['Day'] = pd.Categorical(df_breaches['Day'], categories=ordered_days, ordered=True)
            df_breaches = df_breaches.sort_values('Day')

            # Plot the time series using Streamlit
            st.bar_chart(df_breaches.set_index('Day'))

    else:
        st.warning('Please ensure both start date and end date are selected.')