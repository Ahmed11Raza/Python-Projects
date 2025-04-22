import sqlite3
import streamlit as st
import hashlib
from datetime import datetime

# Database initialization
def init_db():
    conn = sqlite3.connect('social_media.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password_hash TEXT, bio TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS posts
                 (id INTEGER PRIMARY KEY, content TEXT, timestamp DATETIME, user_id INTEGER,
                  FOREIGN KEY (user_id) REFERENCES users(id))''')
    c.execute('''CREATE TABLE IF NOT EXISTS friends
                 (user1_id INTEGER, user2_id INTEGER, 
                  PRIMARY KEY (user1_id, user2_id),
                  FOREIGN KEY (user1_id) REFERENCES users(id),
                  FOREIGN KEY (user2_id) REFERENCES users(id))''')
    c.execute('''CREATE TABLE IF NOT EXISTS friend_requests
                 (from_user_id INTEGER, to_user_id INTEGER, 
                  PRIMARY KEY (from_user_id, to_user_id),
                  FOREIGN KEY (from_user_id) REFERENCES users(id),
                  FOREIGN KEY (to_user_id) REFERENCES users(id))''')
    conn.commit()
    conn.close()

# Hash password for security
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# User class for handling user-related operations
class User:
    def __init__(self, id, username, password_hash, bio):
        self.id = id
        self.username = username
        self.password_hash = password_hash
        self.bio = bio

    @classmethod
    def get_by_username(cls, username):
        conn = sqlite3.connect('social_media.db')
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE username = ?', (username,))
        row = c.fetchone()
        conn.close()
        return cls(*row) if row else None

    @classmethod
    def create(cls, username, password, bio=""):
        password_hash = hash_password(password)
        conn = sqlite3.connect('social_media.db')
        c = conn.cursor()
        c.execute('INSERT INTO users (username, password_hash, bio) VALUES (?, ?, ?)', 
                 (username, password_hash, bio))
        conn.commit()
        user_id = c.lastrowid
        conn.close()
        return cls(user_id, username, password_hash, bio)

    def create_post(self, content):
        conn = sqlite3.connect('social_media.db')
        c = conn.cursor()
        c.execute('INSERT INTO posts (content, timestamp, user_id) VALUES (?, ?, ?)', 
                 (content, datetime.now(), self.id))
        conn.commit()
        conn.close()

    def get_posts(self):
        conn = sqlite3.connect('social_media.db')
        c = conn.cursor()
        c.execute('SELECT * FROM posts WHERE user_id = ? ORDER BY timestamp DESC', (self.id,))
        rows = c.fetchall()
        conn.close()
        return [Post(*row) for row in rows]

    def get_friends(self):
        conn = sqlite3.connect('social_media.db')
        c = conn.cursor()
        c.execute('''SELECT u.* FROM users u
                     JOIN friends f ON (u.id = f.user1_id OR u.id = f.user2_id)
                     WHERE (f.user1_id = ? OR f.user2_id = ?) AND u.id != ?''', 
                     (self.id, self.id, self.id))
        rows = c.fetchall()
        conn.close()
        return [User(*row) for row in rows]

    def get_pending_requests(self):
        conn = sqlite3.connect('social_media.db')
        c = conn.cursor()
        c.execute('''SELECT u.* FROM users u
                     JOIN friend_requests fr ON u.id = fr.from_user_id
                     WHERE fr.to_user_id = ?''', (self.id,))
        rows = c.fetchall()
        conn.close()
        return [User(*row) for row in rows]

    def send_friend_request(self, to_user):
        conn = sqlite3.connect('social_media.db')
        c = conn.cursor()
        c.execute('INSERT OR IGNORE INTO friend_requests (from_user_id, to_user_id) VALUES (?, ?)', 
                 (self.id, to_user.id))
        conn.commit()
        conn.close()

    def accept_friend_request(self, from_user):
        conn = sqlite3.connect('social_media.db')
        c = conn.cursor()
        c.execute('SELECT * FROM friend_requests WHERE from_user_id = ? AND to_user_id = ?', 
                 (from_user.id, self.id))
        if c.fetchone():
            user1_id, user2_id = min(self.id, from_user.id), max(self.id, from_user.id)
            c.execute('INSERT OR IGNORE INTO friends (user1_id, user2_id) VALUES (?, ?)', 
                     (user1_id, user2_id))
            c.execute('DELETE FROM friend_requests WHERE from_user_id = ? AND to_user_id = ?', 
                     (from_user.id, self.id))
            conn.commit()
        conn.close()

    def reject_friend_request(self, from_user):
        conn = sqlite3.connect('social_media.db')
        c = conn.cursor()
        c.execute('DELETE FROM friend_requests WHERE from_user_id = ? AND to_user_id = ?', 
                 (from_user.id, self.id))
        conn.commit()
        conn.close()

    def update_bio(self, new_bio):
        conn = sqlite3.connect('social_media.db')
        c = conn.cursor()
        c.execute('UPDATE users SET bio = ? WHERE id = ?', (new_bio, self.id))
        conn.commit()
        conn.close()
        self.bio = new_bio

# Post class for representing user posts
class Post:
    def __init__(self, id, content, timestamp, user_id):
        self.id = id
        self.content = content
        self.timestamp = timestamp
        self.user_id = user_id

# Streamlit UI
def main():
    init_db()
    
    # Initialize session state
    if 'current_user' not in st.session_state:
        st.session_state['current_user'] = None

    # Login/Register page
    if st.session_state['current_user'] is None:
        st.title("Social Media Platform")
        choice = st.selectbox("Login or Register", ["Login", "Register"])
        
        if choice == "Login":
            username = st.text_input("Username", key="login_username")
            password = st.text_input("Password", type="password", key="login_password")
            if st.button("Login"):
                user = User.get_by_username(username)
                if user and user.password_hash == hash_password(password):
                    st.session_state['current_user'] = user
                    st.success(f"Welcome back, {username}!")
                else:
                    st.error("Invalid username or password")
        
        elif choice == "Register":
            username = st.text_input("Username", key="reg_username")
            password = st.text_input("Password", type="password", key="reg_password")
            bio = st.text_area("Bio (optional)", key="reg_bio")
            if st.button("Register"):
                if User.get_by_username(username):
                    st.error("Username already taken")
                else:
                    User.create(username, password, bio)
                    st.success("Registration successful! Please log in.")
    
    # Main app interface
    else:
        user = st.session_state['current_user']
        st.sidebar.title(f"Welcome, {user.username}")
        page = st.sidebar.selectbox("Navigate", ["Home", "Profile", "Friends", "Logout"])

        if page == "Home":
            st.title("Home Feed")
            content = st.text_area("Share an update", key="post_content")
            if st.button("Post Update"):
                if content.strip():
                    user.create_post(content)
                    st.success("Update posted!")
                else:
                    st.warning("Post cannot be empty")

            st.subheader("Your Feed")
            friends = user.get_friends()
            friend_ids = [f.id for f in friends] + [user.id]
            conn = sqlite3.connect('social_media.db')
            c = conn.cursor()
            placeholders = ','.join('?' * len(friend_ids))
            c.execute(f'SELECT * FROM posts WHERE user_id IN ({placeholders}) ORDER BY timestamp DESC', 
                     friend_ids)
            posts = [Post(*row) for row in c.fetchall()]
            conn.close()
            for post in posts:
                author = User.get_by_username(
                    next(u.username for u in [user] + friends if u.id == post.user_id)
                )
                st.markdown(f"**{author.username}** ({post.timestamp}): {post.content}")

        elif page == "Profile":
            st.title("Your Profile")
            st.write(f"**Username:** {user.username}")
            st.write(f"**Bio:** {user.bio or 'No bio yet'}")
            new_bio = st.text_area("Update your bio", value=user.bio, key="profile_bio")
            if st.button("Save Bio"):
                user.update_bio(new_bio)
                st.success("Bio updated!")
            
            st.subheader("Your Posts")
            for post in user.get_posts():
                st.write(f"{post.timestamp}: {post.content}")

        elif page == "Friends":
            st.title("Friends Management")
            
            st.subheader("Pending Friend Requests")
            requests = user.get_pending_requests()
            if not requests:
                st.write("No pending requests")
            for req in requests:
                col1, col2, col3 = st.columns([2, 1, 1])
                col1.write(req.username)
                if col2.button("Accept", key=f"accept_{req.id}"):
                    user.accept_friend_request(req)
                    st.success(f"Accepted {req.username} as a friend")
                if col3.button("Reject", key=f"reject_{req.id}"):
                    user.reject_friend_request(req)
                    st.success(f"Rejected request from {req.username}")

            st.subheader("Your Friends")
            friends = user.get_friends()
            if not friends:
                st.write("No friends yet")
            for friend in friends:
                st.write(friend.username)

            st.subheader("Add a Friend")
            search = st.text_input("Search by username", key="friend_search")
            if search:
                conn = sqlite3.connect('social_media.db')
                c = conn.cursor()
                c.execute('SELECT * FROM users WHERE username LIKE ? AND id != ?', 
                         (f'%{search}%', user.id))
                results = [User(*row) for row in c.fetchall()]
                conn.close()
                friend_ids = [f.id for f in friends]
                for u in results:
                    if u.id not in friend_ids:
                        if st.button(f"Send request to {u.username}", key=f"req_{u.id}"):
                            user.send_friend_request(u)
                            st.success(f"Request sent to {u.username}")

        elif page == "Logout":
            st.session_state['current_user'] = None
            st.success("Logged out successfully")

if __name__ == "__main__":
    main()