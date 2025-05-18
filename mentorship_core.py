import random
import os

class User:
    def __init__(self, name, email, password, role):
        self.name = name
        self.email = email
        self.password = password
        self.role = role
        self.phone = None
        self.subjects = []
        self.custom_subject = None

    def display_info(self):
        return "Name: " + self.name + ", Role: " + self.role

    def display_full_info(self):
        return "Name: " + self.name + ", Email: " + self.email + ", Role: " + self.role

class MentorshipSession:
    def __init__(self, mentor, learner, topic, date, status="scheduled"):
        self.mentor = mentor
        self.learner = learner
        self.topic = topic
        self.date = date
        self.status = status

    def display_session_info(self):
        return "Mentor: " + self.mentor.name + ", Learner: " + self.learner.name + ", Date: " + self.date + ", Topic: " + self.topic + ", Status: " + self.status

    def update_status(self, new_status):
        self.status = new_status

class BookingManager:
    def __init__(self):
        self.sessions = []

    def book_session(self, session):
        self.sessions.append(session)
        print("Session booked successfully.")

    def view_user_sessions(self, user):
        found = False
        for session in self.sessions:
            if session.mentor == user or session.learner == user:
                print(session.display_session_info())
                found = True
        if not found:
            print("No sessions found.")

    def cancel_session(self, topic, learner_email):
        for session in self.sessions:
            if session.topic == topic and session.learner.email == learner_email:
                session.update_status("cancelled")
                print("Session cancelled.")
                return
        print("Session not found.")

class PaymentGateway:
    def __init__(self):
        self.payments = {}

    def process_payment(self, user, amount):
        txn_id = "TXN" + str(random.randint(10000, 99999))
        self.payments[txn_id] = {"user": user.email, "amount": amount, "status": "paid"}
        print("Payment of " + str(amount) + " completed. Transaction ID: " + txn_id)

users = []

def load_users():
    if os.path.exists("users.txt"):
        with open("users.txt", "r") as f:
            for line in f:
                parts = line.strip().split("|")
                if len(parts) == 4:
                    name, email, password, role = parts
                    users.append(User(name, email, password, role))
                elif len(parts) == 6:
                    name, email, password, role, category, subject = parts
                    user = User(name, email, password, role)
                    user.category = category
                    user.subject = subject
                    users.append(user)

def save_users():
    with open("users.txt", "w") as f:
        for user in users:
            if user.role == "mentor":
                category = user.category if hasattr(user, 'category') else ""
                subject = user.subject if hasattr(user, 'subject') else ""
                line = user.name + "|" + user.email + "|" + user.password + "|" + user.role + "|" + category + "|" + subject
            else:
                line = user.name + "|" + user.email + "|" + user.password + "|" + user.role
            f.write(line + "\n")

def find_user(email, password):
    for user in users:
        if user.email == email and user.password == password:
            return user
    return None

def register(name, email, password, role, phone="", subjects=None, custom_subject=None):
    for user in users:
        if user.email == email:
            return "Email already exists."

    new_user = User(name, email, password, role)
    new_user.phone = phone
    new_user.subjects = subjects if subjects else []
    new_user.custom_subject = custom_subject
    users.append(new_user)
    save_users()
    return "Registration successful."

def main():
    booking_manager = BookingManager()
    payment_gateway = PaymentGateway()
    load_users()

    while True:
        print("\n--- Mentorship App ---")
        print("1. Register")
        print("2. Login")
        print("3. Exit")
        action = input("Choose: ")

        if action == "1":
            name = input("Name: ")
            email = input("Email: ")
            password = input("Password: ")
            role = input("Role (mentor/learner): ")
            phone = input("Phone (optional): ")
            subjects = []

            if role == "mentor":
                subject_input = input("Enter subjects (comma separated): ")
                subjects = [s.strip() for s in subject_input.split(",")] if subject_input else []

            msg = register(name, email, password, role, phone, subjects)
            print(msg)

        elif action == "2":
            email = input("Email: ")
            password = input("Password: ")
            user = find_user(email, password)
            if user:
                print("Login successful.")
                if user.role == "mentor":
                    mentor_dashboard(user, booking_manager)
                else:
                    user_dashboard(user, booking_manager, payment_gateway)
            else:
                print("Login failed.")

        elif action == "3":
            print("Goodbye.")
            break
        else:
            print("Invalid option.")

def user_dashboard(user, booking_manager, payment_gateway):
    while True:
        print("\n--- Learner Dashboard ---")
        print("Welcome, " + user.name)
        print("1. Book Session")
        print("2. View My Sessions")
        print("3. Cancel a Session")
        print("4. Logout")
        choice = input("Choose: ")

        if choice == "1":
            print("\nSubjects Offered:")
            all_subjects = set()
            for u in users:
                if u.role == "mentor":
                    all_subjects.update(u.subjects)
            subject_list = list(all_subjects)
            if not subject_list:
                print("No subjects available.")
                continue
            for i in range(len(subject_list)):
                print(str(i + 1) + ". " + subject_list[i])
            try:
                idx = int(input("Select subject number: ")) - 1
                if 0 <= idx < len(subject_list):
                    selected_subject = subject_list[idx]
                else:
                    print("Invalid selection.")
                    continue
            except:
                print("Invalid input.")
                continue

            print("\nMentors for subject: " + selected_subject)
            mentors = [u for u in users if u.role == "mentor" and selected_subject in u.subjects]
            if not mentors:
                print("No mentors found.")
                continue
            for m in mentors:
                print("- " + m.name + " (" + m.email + ")")

            mentor_email = input("Enter mentor email: ")
            mentor = None
            for m in mentors:
                if m.email == mentor_email:
                    mentor = m
                    break
            if not mentor:
                print("Mentor not found.")
                continue

            topic = input("Enter topic: ")
            date = input("Enter date (DD-MM-YYYY): ")
            payment_gateway.process_payment(user, 20)
            session = MentorshipSession(mentor, user, topic, date)
            booking_manager.book_session(session)

        elif choice == "2":
            booking_manager.view_user_sessions(user)

        elif choice == "3":
            topic = input("Enter topic to cancel: ")
            booking_manager.cancel_session(topic, user.email)

        elif choice == "4":
            print("Logged out.")
            break

        else:
            print("Invalid input.")

def mentor_dashboard(user, booking_manager):
    while True:
        print("\n--- Mentor Dashboard ---")
        print("Welcome, " + user.name)
        print("1. View My Sessions")
        print("2. Logout")
        choice = input("Choose: ")

        if choice == "1":
            booking_manager.view_user_sessions(user)
        elif choice == "2":
            print("Logged out.")
            break
        else:
            print("Invalid input.")

main()

