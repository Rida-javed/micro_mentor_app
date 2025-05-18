import streamlit as st
from mentorship_core import *

if not users:
    load_users()

booking_manager = BookingManager()
payment_gateway = PaymentGateway()

st.title("MicroMentor App")

if "user" not in st.session_state:
    st.session_state.user = None
if "registered" not in st.session_state:
    st.session_state.registered = False

def register_ui():
    st.subheader("Register")
    with st.form("register_form"):
        name = st.text_input("Name")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        role = st.selectbox("Role", ["mentor", "learner"])
        submitted = st.form_submit_button("Register")
        if submitted:
            msg = register(name, email, password, role)
            if msg == "Registration successful.":
                st.success(msg)
                st.session_state.registered = True
            else:
                st.error(msg)

def login_ui():
    st.subheader("Login")
    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")
        if submitted:
            user = find_user(email, password)
            if user:
                st.session_state.user = user
                st.success("Welcome back, " + user.name + "!")
            else:
                st.error("Login failed. Check your credentials.")

def learner_dashboard(user):
    st.subheader("Learner Dashboard - " + user.name)
    choice = st.selectbox("Choose an action", ["Book Session", "View My Sessions", "Cancel Session"])

    if choice == "Book Session":
        st.write("Available Mentors:")
        mentor_emails = [u.email for u in users if u.role == "mentor"]
        if mentor_emails:
            mentor_email = st.selectbox("Choose Mentor", mentor_emails)
            topic = st.text_input("Topic")
            date = st.text_input("Date (DD-MM-YYYY)")
            if st.button("Book Session"):
                if topic.strip() == "" or date.strip() == "":
                    st.error("Topic and Date cannot be empty!")
                    return
                mentor = None
                for u in users:
                    if u.email == mentor_email:
                        mentor = u
                        break
                if mentor:
                    payment_gateway.process_payment(user, 20)
                    session = MentorshipSession(mentor, user, topic, date)
                    booking_manager.book_session(session)
                    st.success("Session booked successfully!")
                else:
                    st.error("Mentor not found.")
        else:
            st.info("No mentors available.")

    elif choice == "View My Sessions":
        st.write("Your Sessions:")
        found = False
        for session in booking_manager.sessions:
            if session.mentor == user or session.learner == user:
                st.write(session.display_session_info())
                found = True
        if not found:
            st.info("No sessions found.")

    elif choice == "Cancel Session":
        topic = st.text_input("Topic of the session to cancel")
        if st.button("Cancel Session"):
            if topic.strip() == "":
                st.error("Please enter a topic.")
            else:
                booking_manager.cancel_session(topic, user.email)
                st.success("If found, session was cancelled.")

def mentor_dashboard(user):
    st.subheader("Mentor Dashboard - " + user.name)
    st.write("Your Sessions:")
    found = False
    for session in booking_manager.sessions:
        if session.mentor == user:
            st.write(session.display_session_info())
            found = True
    if not found:
        st.info("No sessions found.")

def logout():
    st.session_state.user = None
    st.rerun()


if st.session_state.user is None:
    action = st.radio("Choose Action", ["Login", "Register"])
    if action == "Login":
        login_ui()
        if st.session_state.registered:
            st.info("You can now login with your new account!")
            st.session_state.registered = False
    else:
        register_ui()
else:
    st.sidebar.write("Logged in as: " + st.session_state.user.name + " (" + st.session_state.user.role + ")")
    if st.sidebar.button("Logout"):
        logout()
    if st.session_state.user.role == "mentor":
        mentor_dashboard(st.session_state.user)
    else:
        learner_dashboard(st.session_state.user)
