import streamlit as st
import pandas as pd
import datetime
import openai
import time

# Set your OpenAI API key
openai.api_key = st.secrets["APIKEY"]

# Initialize session state for reminders
if 'reminders' not in st.session_state:
    st.session_state.reminders = []

# Function to calculate daily completion percentage and generate advice
def generate_advice(title, due_date):
    days_left = (due_date - datetime.datetime.now()).days
    if days_left > 0:
        daily_percentage = 100 / days_left
        prompt = (f"The reminder '{title}' is due in {days_left} days."
                  f" Suggest strategies to complete it by finishing {daily_percentage:.2f}% daily.")
        try:
            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=prompt,
                max_tokens=100
            )
            return response.choices[0].text.strip()
        except Exception as e:
            return f"Error generating advice: {str(e)}"
    else:
        return "The deadline has already passed. Try to prioritize overdue tasks!"

# Sidebar for adding a new reminder
st.sidebar.header("Add a New Reminder")
category = st.sidebar.text_input("Category")
title = st.sidebar.text_input("Title")
details = st.sidebar.text_area("Details")
due_date = st.sidebar.date_input("Due Date", min_value=datetime.date.today())
due_time = st.sidebar.time_input("Due Time")
completion_level = st.sidebar.slider("Completion Level (%)", 0, 100, 0)

if st.sidebar.button("Add Reminder"):
    #check if reminder already exisis
    existing_titles = [reminder['Title'] for reminder in st.session_state.reminders]
if title in existing_titles:
    st.sidebar.error("A reminder with this title already exists. Please use a different title.")
else:
    reminder = {
        'Category': category,
        'Title': title,
        'Details': details,
        'Due Date': datetime.datetime.combine(due_date, due_time),
        'Completion': completion_level,
        'Advice': generate_advice(title, datetime.datetime.combine(due_date, due_time))
    }
    st.session_state.reminders.append(reminder)
    st.sidebar.success("Reminder added successfully!")

# Main app
st.title("Reminder Web Application")

# Group reminders by category
categories = list(set([reminder['Category'] for reminder in st.session_state.reminders]))
selected_category = st.selectbox("Filter by Category", options=["All"] + categories)

filtered_reminders = (
    st.session_state.reminders if selected_category == "All" 
    else [r for r in st.session_state.reminders if r['Category'] == selected_category]
)

if filtered_reminders:
    for reminder in filtered_reminders:
        st.subheader(f"{reminder['Category']} - {reminder['Title']}")
        st.write(f"**Details:** {reminder['Details']}")
        st.write(f"**Due Date:** {reminder['Due Date']}")
        st.write(f"**Completion Level:** {reminder['Completion']}%")
        st.write(f"**Advice:** {reminder['Advice']}")

        # Update completion level
        new_completion = st.slider(
            f"Update Completion Level for '{reminder['Title']}'", 
            0, 100, reminder['Completion'], key=reminder['Title']
        )
        reminder['Completion'] = new_completion

        # Check if the due date is near
        days_left = (reminder['Due Date'] - datetime.datetime.now()).days
        if 0 < days_left <= 3:
            st.warning(f"Reminder '{reminder['Title']}' is due in {days_left} days!")
        #Mark reminder as complete
        if reminder['Completion'] == 100:
            st.success(f"Reminder '{reminder['Title']}' complete!! Good job!")
            time.sleep(10) # Wait for 10 seconds
            st.session_state.reminders.remove(reminder)
        #Delete reminder buton
        if st.buton(f"Delete '{reminder['Title']}", key=f"delete_{reminder['Title']}"):
            st.session_state.reminders.remove(reminder)
            st.success(f"Reminder '{reminder['Title']}' deleted.")
else:
    st.info("No reminders found in this category.")
