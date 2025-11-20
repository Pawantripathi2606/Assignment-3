"""
- Name :pawan tripathi
- Enrollment number : 0157AL231147
- Batch : 5 (MTF) - 2027
- Batch Time : 10:30 AM


"""


import json
import os
import random
from datetime import datetime

# --- Configuration and File Paths ---
USERS_FILE = 'users.json'
SCORES_FILE = 'scores.json'
# Ensure all three question files are present in the directory
QUESTIONS_FILES = {
    'dsa': 'questions_dsa.txt',
    'dbms': 'questions_dbms.txt',
    'python': 'questions_python.txt',
}
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'adminpass'

# --- Utility Functions for File Operations ---

def load_data(filepath, default_value):
    """Loads data from a JSON file or returns a default value if the file does not exist."""
    if not os.path.exists(filepath):
        # print(f"File not found: {filepath}. Returning default data.")
        return default_value
    try:
        with open(filepath, 'r') as f:
            # Handle empty files or invalid JSON
            content = f.read().strip()
            if not content:
                # print(f"File {filepath} is empty. Returning default data.")
                return default_value
            f.seek(0) # Reset file pointer to beginning for json.load
            return json.loads(content)
    except (json.JSONDecodeError, IOError, Exception) as e:
        print(f"Warning: Could not read {filepath} due to error: {e}. Starting with default data.")
        return default_value

def save_data(filepath, data):
    """Saves data to a JSON file."""
    try:
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=4)
    except IOError:
        print(f"Error: Could not write data to {filepath}.")

def load_questions(category):
    """Loads questions from a specific category text file."""
    filepath = QUESTIONS_FILES.get(category.lower())
    if not filepath or not os.path.exists(filepath):
        print(f"Error: Question file for '{category}' not found at {filepath}.")
        return []

    questions = []
    try:
        with open(filepath, 'r') as f:
            content = f.read().strip()
            # Split content into question blocks based on '---' delimiter
            q_blocks = content.split('---')

            for block in q_blocks:
                block = block.strip()
                if not block:
                    continue

                lines = [line.strip() for line in block.split('\n') if line.strip()]
                if len(lines) < 6:
                    print(f"Warning: Skipping malformed question block in {filepath}.")
                    continue

                question_text = lines[0]
                options = [lines[1], lines[2], lines[3], lines[4]]
                correct_answer = lines[5].upper()

                # Basic validation for correct answer
                if correct_answer not in ['A', 'B', 'C', 'D']:
                    print(f"Warning: Skipping question with invalid answer key '{correct_answer}'.")
                    continue

                questions.append({
                    'question': question_text,
                    'options': options,
                    'answer': correct_answer
                })
    except IOError as e:
        print(f"Error reading question file {filepath}: {e}")
        return []
    
    # Only return between 5 to 10 questions randomly
    random.shuffle(questions)
    # Ensure at least 1 question is returned if the list is not empty
    max_questions = len(questions)
    if max_questions == 0:
        return []
    
    # Select between 5 and 10 questions, but no more than available
    num_to_select = min(max_questions, random.randint(5, 10))
    return questions[:num_to_select]

# --- Classes ---

class User:
    """Represents a standard student user."""
    def __init__(self, username, password, name, email, branch, year, contact, enrollment=None):
        self.username = username
        self.password = password
        self.name = name
        self.email = email
        self.branch = branch
        self.year = year
        self.contact = contact
        self.enrollment = enrollment if enrollment else self.generate_enrollment()

    def to_dict(self):
        # Exclude sensitive info like password if saving to a public facing format, but keeping for internal file storage
        return {
            'username': self.username,
            'password': self.password,
            'name': self.name,
            'email': self.email,
            'branch': self.branch,
            'year': self.year,
            'contact': self.contact,
            'enrollment': self.enrollment
        }
    
    @staticmethod
    def from_dict(data):
        return User(**data)

    def generate_enrollment(self):
        # Simple enrollment generation: first 3 letters of name + current timestamp
        name_prefix = self.name[:3].upper().ljust(3, 'X')
        timestamp = datetime.now().strftime("%y%m%d%H%M%S")
        return f"{name_prefix}-{timestamp}"

class Admin(User):
    """Represents an admin user."""
    def __init__(self, username, password):
        # Admin does not need all the fields of User, but inherits them for simplicity
        super().__init__(username, password, 'Admin', 'admin@quiz.com', 'N/A', 'N/A', 'N/A', 'ADM-001')
        self.is_admin = True
    
    def to_dict(self):
        return {'username': self.username, 'password': self.password, 'is_admin': True}

# --- Core Application Logic ---

class QuizApp:
    def __init__(self):
        # Load all data on startup
        self.users_data = load_data(USERS_FILE, {})
        self.scores_data = load_data(SCORES_FILE, [])
        self.current_user = None
        self._initialize_admin()

    def _initialize_admin(self):
        """Ensures the default admin account exists."""
        if ADMIN_USERNAME not in self.users_data:
            admin = Admin(ADMIN_USERNAME, ADMIN_PASSWORD)
            self.users_data[ADMIN_USERNAME] = admin.to_dict()
            self._save_users() # Save admin immediately
        # If the admin account exists but somehow lost the 'is_admin' flag (due to old save format), fix it
        elif 'is_admin' not in self.users_data[ADMIN_USERNAME]:
             self.users_data[ADMIN_USERNAME]['is_admin'] = True
             self._save_users()

    def _save_users(self):
        """Saves the current user data back to the file."""
        save_data(USERS_FILE, self.users_data)

    def _save_scores(self):
        """Saves the current score data back to the file."""
        save_data(SCORES_FILE, self.scores_data)

    def registration(self):
        """Handles user registration."""
        print("\n--- User Registration ---")
        username = input("Enter new Username: ").strip()
        if username in self.users_data:
            print("Username already exists. Please choose a different one.")
            return
        if not username:
            print("Username cannot be empty.")
            return

        password = input("Enter Password: ").strip()
        if not password:
            print("Password cannot be empty.")
            return
            
        name = input("Enter Full Name: ").strip()
        email = input("Enter Email: ").strip()
        branch = input("Enter Branch (e.g., CS, IT): ").strip()
        year = input("Enter Year (e.g., First, Second): ").strip()
        contact = input("Enter Contact Number: ").strip()

        new_user = User(username, password, name, email, branch, year, contact)
        self.users_data[username] = new_user.to_dict()
        self._save_users()
        print(f"\nRegistration Successful! Your enrollment ID is: {new_user.enrollment}")
        print("Please log in to continue.")

    def login(self):
        """Handles user and admin login."""
        print("\n--- Login ---")
        username = input("Enter Username: ").strip()
        password = input("Enter Password: ").strip()

        user_details = self.users_data.get(username)

        if user_details and user_details.get('password') == password:
            if user_details.get('is_admin'):
                # Admin login: Admin details are fixed
                self.current_user = Admin(username, password)
                print(f"\nWelcome, Admin! Access granted.")
                self.admin_menu()
            else:
                # Regular user login: Load full profile
                self.current_user = User.from_dict(user_details)
                print(f"\nWelcome, {self.current_user.name}! You are logged in.")
                self.user_menu()
        else:
            print("\nInvalid username or password.")

    def logout(self):
        """Logs out the current user."""
        if self.current_user:
            print(f"Goodbye, {self.current_user.name}!")
        self.current_user = None

    def admin_menu(self):
        """Menu for Admin users."""
        while self.current_user and self.current_user.username == ADMIN_USERNAME:
            print("\n--- Admin Menu ---")
            print("1. View All User Scores")
            print("2. Logout")
            choice = input("Enter your choice (1-2): ").strip()

            if choice == '1':
                self.view_all_scores()
            elif choice == '2':
                self.logout()
            else:
                print("Invalid choice. Please try again.")

    def user_menu(self):
        """Main menu for logged-in students."""
        while self.current_user:
            print("\n--- User Menu ---")
            print("1. Attempt Quiz")
            print("2. View My Scores")
            print("3. Update Profile")
            print("4. View Profile")
            print("5. Logout")
            
            choice = input("Enter your choice (1-5): ").strip()

            if choice == '1':
                self.attempt_quiz()
            elif choice == '2':
                self.view_scores()
            elif choice == '3':
                self.update_profile()
            elif choice == '4':
                self.view_profile()
            elif choice == '5':
                self.logout()
            else:
                print("Invalid choice. Please try again.")

    # --- Quiz Functions ---

    def attempt_quiz(self):
        """Allows the user to attempt a quiz."""
        print("\n--- Select Quiz Category ---")
        categories = sorted(QUESTIONS_FILES.keys()) # Sorts categories for consistent display
        print("Available categories:")
        for i, cat in enumerate(categories):
            print(f"  {i+1}. {cat.upper()}")
        
        choice = input("Enter category number or name (e.g., 1 or DSA): ").strip()
        
        category = None
        try:
            if choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(categories):
                    category = categories[idx]
            else:
                if choice.lower() in categories:
                    category = choice.lower()
        except ValueError:
            pass # Handled by the check below

        if not category:
            print("Invalid category selection.")
            return

        questions = load_questions(category)
        if not questions:
            print(f"No questions loaded for {category.upper()}. Check the corresponding text file.")
            return

        print(f"\n--- Starting {category.upper()} Quiz ({len(questions)} Questions) ---")
        input("Press Enter to begin...")

        score = 0
        total_questions = len(questions)

        for i, q_data in enumerate(questions):
            print(f"\n{'='*50}\nQuestion {i+1} of {total_questions}: {q_data['question']}")
            
            # Display options (A, B, C, D)
            for option in q_data['options']:
                print(f"  {option}")

            # Loop for valid input
            while True:
                user_answer = input("Your answer (A/B/C/D): ").strip().upper()
                if user_answer in ['A', 'B', 'C', 'D']:
                    break
                print("Invalid input. Please enter A, B, C, or D.")

            if user_answer == q_data['answer']:
                print("Correct!")
                score += 1
            else:
                print(f"Incorrect. The correct answer was: {q_data['answer']}")
        
        # Save score
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        score_entry = {
            'enrollment': self.current_user.enrollment,
            'name': self.current_user.name,
            'category': category.upper(),
            'score': score,
            'total_marks': total_questions,
            'datetime': timestamp
        }

        self.scores_data.append(score_entry)
        self._save_scores()

        print(f"\n{'='*50}")
        print("--- Quiz Finished ---")
        print(f"Your final score: {score}/{total_questions}")
        print(f"Score saved successfully at {timestamp}.")
        print('='*50)

    def view_scores(self):
        """Displays the current user's quiz history."""
        print("\n--- Your Quiz History ---")
        my_scores = [s for s in self.scores_data if s['enrollment'] == self.current_user.enrollment]
        
        if not my_scores:
            print("You have not attempted any quizzes yet.")
            return

        print(f"{'Category':<10} | {'Score':<10} | {'Date/Time':<20}")
        print("-" * 43)
        for s in my_scores:
            print(f"{s['category']:<10} | {s['score']}/{s['total_marks']:<7} | {s['datetime']:<20}")

    def view_all_scores(self):
        """(Admin Function) Displays all users' quiz history."""
        print("\n--- All Users' Quiz History ---")
        if not self.scores_data:
            print("No quiz scores recorded yet.")
            return

        print(f"{'Enrollment':<15} | {'Category':<10} | {'Score':<10} | {'Date/Time':<20}")
        print("-" * 60)
        for s in self.scores_data:
            print(f"{s['enrollment']:<15} | {s['category']:<10} | {s['score']}/{s['total_marks']:<7} | {s['datetime']:<20}")
    
    # --- Profile Management Functions ---

    def view_profile(self):
        """Displays the current user's profile information."""
        print("\n--- Your Profile ---")
        user = self.current_user
        print(f"  Name: {user.name}")
        print(f"  Enrollment ID: {user.enrollment}")
        print(f"  Username: {user.username}")
        print(f"  Email: {user.email}")
        print(f"  Branch: {user.branch}")
        print(f"  Year: {user.year}")
        print(f"  Contact: {user.contact}")

    def update_profile(self):
        """Allows the user to update their profile details."""
        print("\n--- Update Profile ---")
        user = self.current_user
        
        print(f"Current Name: {user.name}")
        user.name = input(f"Enter New Name (or press Enter to keep current): ").strip() or user.name

        print(f"Current Email: {user.email}")
        user.email = input(f"Enter New Email (or press Enter to keep current): ").strip() or user.email
        
        print(f"Current Branch: {user.branch}")
        user.branch = input(f"Enter New Branch (or press Enter to keep current): ").strip() or user.branch

        print(f"Current Year: {user.year}")
        user.year = input(f"Enter New Year (or press Enter to keep current): ").strip() or user.year
        
        print(f"Current Contact: {user.contact}")
        user.contact = input(f"Enter New Contact (or press Enter to keep current): ").strip() or user.contact

        # Update the current user object and the main user data structure
        self.current_user = User(
            user.username, user.password, user.name, user.email, user.branch, user.year, user.contact, user.enrollment
        )
        self.users_data[user.username] = self.current_user.to_dict()
        self._save_users()
        print("\nProfile updated successfully!")
        self.view_profile() # Show updated profile

# --- Main Program Execution ---

def main():
    """The main entry point for the Quiz Application."""
    app = QuizApp()

    while True:
        print("\n===============================")
        print("    STUDENT QUIZ APPLICATION")
        print("===============================")
        print("1. User Registration")
        print("2. User/Admin Login")
        print("3. Exit")
        
        choice = input("Enter your choice (1-3): ").strip()

        if choice == '1':
            app.registration()
        elif choice == '2':
            app.login()
        elif choice == '3':
            print("\nThank you for using the Quiz App. Goodbye!")
            break
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")

if __name__ == "__main__":
    main()