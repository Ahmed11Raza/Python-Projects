import streamlit as st
import pickle
import os
from datetime import datetime
from abc import ABC, abstractmethod

# Abstract base class for Person
class Person(ABC):
    def __init__(self, id, name, email):
        self._id = id
        self._name = name
        self._email = email
        
    @property
    def id(self):
        return self._id
        
    @property
    def name(self):
        return self._name
        
    @property
    def email(self):
        return self._email
    
    @abstractmethod
    def get_role(self):
        pass
    
    def __str__(self):
        return f"{self._name} ({self.get_role()})"

# Instructor class inherits from Person
class Instructor(Person):
    def __init__(self, id, name, email, department, rank):
        super().__init__(id, name, email)
        self._department = department
        self._rank = rank
        self._courses = []
        
    @property
    def department(self):
        return self._department
        
    @property
    def rank(self):
        return self._rank
        
    @property
    def courses(self):
        return self._courses
    
    def add_course(self, course):
        if course not in self._courses:
            self._courses.append(course)
            
    def remove_course(self, course):
        if course in self._courses:
            self._courses.remove(course)
            
    def get_role(self):
        return "Instructor"

# Student class inherits from Person
class Student(Person):
    def __init__(self, id, name, email, major):
        super().__init__(id, name, email)
        self._major = major
        self._enrolled_courses = []
        self._grades = {}  # course_id: grade
        
    @property
    def major(self):
        return self._major
        
    @property
    def enrolled_courses(self):
        return self._enrolled_courses
        
    @property
    def grades(self):
        return self._grades
    
    def enroll_course(self, course):
        if course not in self._enrolled_courses and course.has_capacity():
            self._enrolled_courses.append(course)
            course.add_student(self)
            return True
        return False
            
    def drop_course(self, course):
        if course in self._enrolled_courses:
            self._enrolled_courses.remove(course)
            course.remove_student(self)
            if course.id in self._grades:
                del self._grades[course.id]
            return True
        return False
    
    def assign_grade(self, course, grade):
        if course in self._enrolled_courses:
            self._grades[course.id] = grade
            return True
        return False
    
    def get_gpa(self):
        if not self._grades:
            return 0.0
        
        grade_points = {'A': 4.0, 'B': 3.0, 'C': 2.0, 'D': 1.0, 'F': 0.0}
        total_points = sum(grade_points.get(g, 0) for g in self._grades.values())
        return total_points / len(self._grades)
    
    def get_role(self):
        return "Student"

# Course class
class Course:
    def __init__(self, id, title, department, max_capacity, credits):
        self._id = id
        self._title = title
        self._department = department
        self._max_capacity = max_capacity
        self._credits = credits
        self._instructor = None
        self._students = []
        self._schedule = []  # List of session objects
        
    @property
    def id(self):
        return self._id
        
    @property
    def title(self):
        return self._title
        
    @property
    def department(self):
        return self._department
        
    @property
    def max_capacity(self):
        return self._max_capacity
        
    @property
    def credits(self):
        return self._credits
        
    @property
    def instructor(self):
        return self._instructor
        
    @property
    def students(self):
        return self._students
        
    @property
    def schedule(self):
        return self._schedule
    
    def set_instructor(self, instructor):
        if self._instructor:
            self._instructor.remove_course(self)
        
        self._instructor = instructor
        if instructor:
            instructor.add_course(self)
            
    def add_student(self, student):
        if len(self._students) < self._max_capacity and student not in self._students:
            self._students.append(student)
            return True
        return False
            
    def remove_student(self, student):
        if student in self._students:
            self._students.remove(student)
            return True
        return False
    
    def has_capacity(self):
        return len(self._students) < self._max_capacity
    
    def add_session(self, session):
        self._schedule.append(session)
        
    def remove_session(self, session):
        if session in self._schedule:
            self._schedule.remove(session)
    
    def __str__(self):
        instructor_name = self._instructor.name if self._instructor else "No instructor assigned"
        return f"{self._id} - {self._title} ({instructor_name})"

# Session class to represent course schedule
class Session:
    def __init__(self, day, start_time, end_time, location):
        self._day = day
        self._start_time = start_time
        self._end_time = end_time
        self._location = location
        
    @property
    def day(self):
        return self._day
        
    @property
    def start_time(self):
        return self._start_time
        
    @property
    def end_time(self):
        return self._end_time
        
    @property
    def location(self):
        return self._location
    
    def __str__(self):
        return f"{self._day}, {self._start_time}-{self._end_time} at {self._location}"

# University class to manage everything
class University:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(University, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self._students = {}  # id: Student object
        self._instructors = {}  # id: Instructor object
        self._courses = {}  # id: Course object
        self._departments = set()
        self._initialized = True
        
    def add_student(self, student):
        self._students[student.id] = student
        
    def add_instructor(self, instructor):
        self._instructors[instructor.id] = instructor
        self._departments.add(instructor.department)
        
    def add_course(self, course):
        self._courses[course.id] = course
        self._departments.add(course.department)
        
    def get_student(self, student_id):
        return self._students.get(student_id)
        
    def get_instructor(self, instructor_id):
        return self._instructors.get(instructor_id)
        
    def get_course(self, course_id):
        return self._courses.get(course_id)
    
    def get_all_students(self):
        return list(self._students.values())
        
    def get_all_instructors(self):
        return list(self._instructors.values())
        
    def get_all_courses(self):
        return list(self._courses.values())
    
    def get_departments(self):
        return sorted(list(self._departments))
    
    def save_data(self, filename="university_data.pkl"):
        data = {
            "students": self._students,
            "instructors": self._instructors,
            "courses": self._courses,
            "departments": self._departments
        }
        
        with open(filename, 'wb') as file:
            pickle.dump(data, file)
    
    def load_data(self, filename="university_data.pkl"):
        if os.path.exists(filename):
            with open(filename, 'rb') as file:
                data = pickle.load(file)
                
                self._students = data.get("students", {})
                self._instructors = data.get("instructors", {})
                self._courses = data.get("courses", {})
                self._departments = data.get("departments", set())

# Let's create the Streamlit UI
def main():
    st.set_page_config(page_title="University Course Management System", layout="wide")
    
    # Initialize the university system
    university = University()
    try:
        university.load_data()
    except Exception as e:
        st.error(f"Error loading data: {e}")
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    pages = ["Dashboard", "Courses", "Instructors", "Students", "Enrollments", "Reports"]
    selection = st.sidebar.radio("Go to", pages)
    
    # Dashboard page
    if selection == "Dashboard":
        st.title("University Course Management System")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Courses", len(university.get_all_courses()))
        
        with col2:
            st.metric("Total Students", len(university.get_all_students()))
        
        with col3:
            st.metric("Total Instructors", len(university.get_all_instructors()))
        
        st.subheader("Departments")
        for dept in university.get_departments():
            st.write(f"- {dept}")
    
    # Courses page
    elif selection == "Courses":
        st.title("Course Management")
        
        tab1, tab2 = st.tabs(["View Courses", "Add Course"])
        
        with tab1:
            st.subheader("All Courses")
            courses = university.get_all_courses()
            
            if not courses:
                st.info("No courses available. Add some courses first.")
            else:
                for course in courses:
                    with st.expander(f"{course.id} - {course.title}"):
                        st.write(f"**Department:** {course.department}")
                        st.write(f"**Credits:** {course.credits}")
                        st.write(f"**Capacity:** {len(course.students)}/{course.max_capacity}")
                        
                        st.write("**Instructor:**")
                        if course.instructor:
                            st.write(f"- {course.instructor.name} ({course.instructor.email})")
                        else:
                            st.write("No instructor assigned")
                        
                        st.write("**Schedule:**")
                        if course.schedule:
                            for session in course.schedule:
                                st.write(f"- {session}")
                        else:
                            st.write("No sessions scheduled")
                        
                        # Actions
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button(f"Edit Course {course.id}"):
                                st.session_state.edit_course_id = course.id
                        
                        with col2:
                            if st.button(f"Delete Course {course.id}"):
                                del university._courses[course.id]
                                university.save_data()
                                st.experimental_rerun()
        
        with tab2:
            st.subheader("Add New Course")
            
            course_id = st.text_input("Course ID (e.g., CS101)")
            course_title = st.text_input("Course Title")
            course_dept = st.text_input("Department")
            course_capacity = st.number_input("Maximum Capacity", min_value=1, value=30)
            course_credits = st.number_input("Credits", min_value=1, max_value=6, value=3)
            
            # Instructor selection
            instructors = university.get_all_instructors()
            instructor_options = ["None"] + [f"{i.id} - {i.name}" for i in instructors]
            selected_instructor = st.selectbox("Assign Instructor", instructor_options)
            
            # Schedule
            st.subheader("Add Schedule (Optional)")
            add_schedule = st.checkbox("Add a class session")
            
            sessions = []
            if add_schedule:
                col1, col2 = st.columns(2)
                with col1:
                    day = st.selectbox("Day", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
                    location = st.text_input("Location (Room/Building)")
                
                with col2:
                    start_time = st.time_input("Start Time")
                    end_time = st.time_input("End Time")
                
                if st.button("Add Session"):
                    session = Session(day, start_time.strftime("%H:%M"), end_time.strftime("%H:%M"), location)
                    sessions.append(session)
                    st.success("Session added!")
            
            if st.button("Create Course"):
                if not course_id or not course_title or not course_dept:
                    st.error("Course ID, Title, and Department are required.")
                elif course_id in university._courses:
                    st.error(f"Course ID {course_id} already exists.")
                else:
                    new_course = Course(course_id, course_title, course_dept, course_capacity, course_credits)
                    
                    # Add sessions
                    for session in sessions:
                        new_course.add_session(session)
                    
                    # Assign instructor if selected
                    if selected_instructor != "None":
                        instructor_id = selected_instructor.split(" - ")[0]
                        instructor = university.get_instructor(instructor_id)
                        if instructor:
                            new_course.set_instructor(instructor)
                    
                    university.add_course(new_course)
                    university.save_data()
                    st.success(f"Course {course_id} created successfully!")
                    st.experimental_rerun()
    
    # Instructors page
    elif selection == "Instructors":
        st.title("Instructor Management")
        
        tab1, tab2 = st.tabs(["View Instructors", "Add Instructor"])
        
        with tab1:
            st.subheader("All Instructors")
            instructors = university.get_all_instructors()
            
            if not instructors:
                st.info("No instructors available. Add some instructors first.")
            else:
                for instructor in instructors:
                    with st.expander(f"{instructor.id} - {instructor.name}"):
                        st.write(f"**Email:** {instructor.email}")
                        st.write(f"**Department:** {instructor.department}")
                        st.write(f"**Rank:** {instructor.rank}")
                        
                        st.write("**Courses:**")
                        if instructor.courses:
                            for course in instructor.courses:
                                st.write(f"- {course.id} - {course.title}")
                        else:
                            st.write("No courses assigned")
                        
                        # Actions
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button(f"Edit Instructor {instructor.id}"):
                                st.session_state.edit_instructor_id = instructor.id
                        
                        with col2:
                            if st.button(f"Delete Instructor {instructor.id}"):
                                # Remove instructor from courses first
                                for course in instructor.courses.copy():
                                    course.set_instructor(None)
                                
                                del university._instructors[instructor.id]
                                university.save_data()
                                st.experimental_rerun()
        
        with tab2:
            st.subheader("Add New Instructor")
            
            instructor_id = st.text_input("Instructor ID")
            instructor_name = st.text_input("Full Name")
            instructor_email = st.text_input("Email")
            instructor_dept = st.text_input("Department")
            instructor_rank = st.selectbox("Rank", ["Professor", "Associate Professor", "Assistant Professor", "Lecturer", "Adjunct"])
            
            if st.button("Create Instructor"):
                if not instructor_id or not instructor_name or not instructor_email or not instructor_dept:
                    st.error("All fields are required.")
                elif instructor_id in university._instructors:
                    st.error(f"Instructor ID {instructor_id} already exists.")
                else:
                    new_instructor = Instructor(instructor_id, instructor_name, instructor_email, instructor_dept, instructor_rank)
                    university.add_instructor(new_instructor)
                    university.save_data()
                    st.success(f"Instructor {instructor_name} created successfully!")
                    st.experimental_rerun()
    
    # Students page
    elif selection == "Students":
        st.title("Student Management")
        
        tab1, tab2 = st.tabs(["View Students", "Add Student"])
        
        with tab1:
            st.subheader("All Students")
            students = university.get_all_students()
            
            if not students:
                st.info("No students available. Add some students first.")
            else:
                for student in students:
                    with st.expander(f"{student.id} - {student.name}"):
                        st.write(f"**Email:** {student.email}")
                        st.write(f"**Major:** {student.major}")
                        st.write(f"**GPA:** {student.get_gpa():.2f}")
                        
                        st.write("**Enrolled Courses:**")
                        if student.enrolled_courses:
                            for course in student.enrolled_courses:
                                grade = student.grades.get(course.id, "Not graded")
                                st.write(f"- {course.id} - {course.title} (Grade: {grade})")
                        else:
                            st.write("Not enrolled in any courses")
                        
                        # Actions
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button(f"Edit Student {student.id}"):
                                st.session_state.edit_student_id = student.id
                        
                        with col2:
                            if st.button(f"Delete Student {student.id}"):
                                # Drop all courses first
                                for course in student.enrolled_courses.copy():
                                    student.drop_course(course)
                                
                                del university._students[student.id]
                                university.save_data()
                                st.experimental_rerun()
        
        with tab2:
            st.subheader("Add New Student")
            
            student_id = st.text_input("Student ID")
            student_name = st.text_input("Full Name")
            student_email = st.text_input("Email")
            student_major = st.text_input("Major")
            
            if st.button("Create Student"):
                if not student_id or not student_name or not student_email or not student_major:
                    st.error("All fields are required.")
                elif student_id in university._students:
                    st.error(f"Student ID {student_id} already exists.")
                else:
                    new_student = Student(student_id, student_name, student_email, student_major)
                    university.add_student(new_student)
                    university.save_data()
                    st.success(f"Student {student_name} created successfully!")
                    st.experimental_rerun()
    
    # Enrollments page
    elif selection == "Enrollments":
        st.title("Course Enrollments")
        
        students = university.get_all_students()
        courses = university.get_all_courses()
        
        if not students:
            st.warning("No students in the system. Please add students first.")
        elif not courses:
            st.warning("No courses in the system. Please add courses first.")
        else:
            st.subheader("Enroll Students in Courses")
            
            col1, col2 = st.columns(2)
            
            with col1:
                selected_student_str = st.selectbox(
                    "Select Student", 
                    [f"{student.id} - {student.name}" for student in students]
                )
                student_id = selected_student_str.split(" - ")[0]
                student = university.get_student(student_id)
            
            with col2:
                # Filter out courses the student is already enrolled in
                available_courses = [course for course in courses if course not in student.enrolled_courses]
                
                if not available_courses:
                    st.info("Student is already enrolled in all available courses.")
                else:
                    selected_course_str = st.selectbox(
                        "Select Course", 
                        [f"{course.id} - {course.title}" for course in available_courses]
                    )
                    course_id = selected_course_str.split(" - ")[0]
                    course = university.get_course(course_id)
                    
                    if st.button("Enroll Student"):
                        if course.has_capacity():
                            if student.enroll_course(course):
                                university.save_data()
                                st.success(f"Successfully enrolled {student.name} in {course.title}")
                                st.experimental_rerun()
                            else:
                                st.error("Failed to enroll student. They may already be enrolled in this course.")
                        else:
                            st.error(f"Course {course.title} has reached maximum capacity.")
            
            st.subheader("Current Enrollments")
            for student in students:
                if student.enrolled_courses:
                    with st.expander(f"{student.name}'s Enrollments"):
                        for course in student.enrolled_courses:
                            col1, col2, col3 = st.columns([3, 2, 1])
                            
                            with col1:
                                st.write(f"{course.id} - {course.title}")
                            
                            with col2:
                                grade = student.grades.get(course.id, "Not graded")
                                if grade != "Not graded":
                                    st.write(f"Grade: {grade}")
                                else:
                                    # Create a dropdown to assign grades
                                    new_grade = st.selectbox(
                                        f"Assign grade for {course.id}",
                                        ["Not graded", "A", "B", "C", "D", "F"],
                                        key=f"grade_{student.id}_{course.id}"
                                    )
                                    
                                    if new_grade != "Not graded" and st.button(f"Save grade for {course.id}", key=f"save_{student.id}_{course.id}"):
                                        student.assign_grade(course, new_grade)
                                        university.save_data()
                                        st.success(f"Grade {new_grade} assigned to {student.name} for {course.title}")
                                        st.experimental_rerun()
                            
                            with col3:
                                if st.button(f"Drop {course.id}", key=f"drop_{student.id}_{course.id}"):
                                    student.drop_course(course)
                                    university.save_data()
                                    st.success(f"{student.name} dropped from {course.title}")
                                    st.experimental_rerun()
    
    # Reports page
    elif selection == "Reports":
        st.title("Reports")
        
        report_type = st.selectbox(
            "Select Report Type",
            ["Course Enrollment Statistics", "Student Performance", "Instructor Teaching Load"]
        )
        
        if report_type == "Course Enrollment Statistics":
            st.subheader("Course Enrollment Statistics")
            
            courses = university.get_all_courses()
            if not courses:
                st.info("No courses available to generate reports.")
            else:
                # Prepare data for visualization
                course_names = [course.id for course in courses]
                enrollments = [len(course.students) for course in courses]
                capacities = [course.max_capacity for course in courses]
                
                # Display as a table
                enrollment_data = {
                    "Course": course_names,
                    "Enrolled": enrollments,
                    "Capacity": capacities,
                    "Fill Rate (%)": [round(e/c*100, 1) for e, c in zip(enrollments, capacities)]
                }
                
                st.table(enrollment_data)
                
                # Export option
                if st.button("Export Report"):
                    st.success("Report would be exported here (feature not implemented in this demo)")
        
        elif report_type == "Student Performance":
            st.subheader("Student Performance Report")
            
            students = university.get_all_students()
            if not students:
                st.info("No students available to generate reports.")
            else:
                # Show GPA distribution
                gpas = [student.get_gpa() for student in students]
                
                # Display as a table
                performance_data = {
                    "Student ID": [student.id for student in students],
                    "Name": [student.name for student in students],
                    "Major": [student.major for student in students],
                    "Courses Enrolled": [len(student.enrolled_courses) for student in students],
                    "GPA": [f"{student.get_gpa():.2f}" for student in students]
                }
                
                st.table(performance_data)
                
                # Export option
                if st.button("Export Report"):
                    st.success("Report would be exported here (feature not implemented in this demo)")
        
        elif report_type == "Instructor Teaching Load":
            st.subheader("Instructor Teaching Load Report")
            
            instructors = university.get_all_instructors()
            if not instructors:
                st.info("No instructors available to generate reports.")
            else:
                # Display as a table
                load_data = {
                    "Instructor ID": [instructor.id for instructor in instructors],
                    "Name": [instructor.name for instructor in instructors],
                    "Department": [instructor.department for instructor in instructors],
                    "Courses": [len(instructor.courses) for instructor in instructors],
                    "Total Students": [
                        sum(len(course.students) for course in instructor.courses) 
                        for instructor in instructors
                    ]
                }
                
                st.table(load_data)
                
                # Export option
                if st.button("Export Report"):
                    st.success("Report would be exported here (feature not implemented in this demo)")

    # Save data before exiting
    try:
        university.save_data()
    except Exception as e:
        st.error(f"Error saving data: {e}")

if __name__ == "__main__":
    main()