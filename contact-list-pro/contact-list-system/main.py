import streamlit as st
import pickle
import os
import uuid
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import io
import base64
import csv

# Configuration
CONTACTS_FILE = "contacts_manager.pkl"
BACKUP_FOLDER = "backups"
os.makedirs(BACKUP_FOLDER, exist_ok=True)

class ContactManager:
    def __init__(self):
        self.contacts = []
        self.load_contacts()
    
    def load_contacts(self):
        """Load contacts with backup recovery"""
        try:
            if os.path.exists(CONTACTS_FILE):
                with open(CONTACTS_FILE, 'rb') as f:
                    self.contacts = pickle.load(f)
            self.create_backup()
        except Exception as e:
            st.error(f"Error loading contacts: {e}")
            if self.recover_backup():
                st.success("Recovered from backup!")

    def save_contacts(self):
        """Save with versioned backups"""
        try:
            with open(CONTACTS_FILE, 'wb') as f:
                pickle.dump(self.contacts, f)
            self.create_backup()
        except Exception as e:
            st.error(f"Error saving contacts: {e}")

    def create_backup(self):
        """Create timestamped backup"""
        backup_file = os.path.join(BACKUP_FOLDER, f"contacts_bak_{datetime.now().timestamp()}.pkl")
        with open(backup_file, 'wb') as f:
            pickle.dump(self.contacts, f)

    def recover_backup(self):
        """Recover from latest backup"""
        backups = sorted([f for f in os.listdir(BACKUP_FOLDER) if f.endswith('.pkl')], reverse=True)
        if backups:
            with open(os.path.join(BACKUP_FOLDER, backups[0]), 'rb') as f:
                self.contacts = pickle.load(f)
            return True
        return False

    def generate_avatar(self, name):
        """Generate profile avatar with initials"""
        initials = "".join([n[0].upper() for n in name.split()[:2]])
        img = Image.new('RGB', (100, 100), color=(73, 109, 137))
        d = ImageDraw.Draw(img)
        fnt = ImageFont.truetype("arial.ttf", 40)
        d.text((35, 25), initials, font=fnt, fill=(255, 255, 255))
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode()

    def add_contact(self, contact_data):
        """Add new contact with validation"""
        if not contact_data.get('name'):
            raise ValueError("Name is required")
        
        if not contact_data.get('email') and not contact_data.get('phone'):
            raise ValueError("At least one of email or phone is required")

        if contact_data.get('email') and not self.validate_email(contact_data['email']):
            raise ValueError("Invalid email format")

        if contact_data.get('phone') and not self.validate_phone(contact_data['phone']):
            raise ValueError("Invalid phone number")

        if contact_data.get('email') and any(c['email'] == contact_data['email'] for c in self.contacts):
            raise ValueError("Email already exists")

        contact_id = str(uuid.uuid4())
        self.contacts.append({
            'id': contact_id,
            **contact_data,
            'avatar': self.generate_avatar(contact_data['name']),
            'created_at': datetime.now().isoformat(),
            'last_modified': datetime.now().isoformat(),
            'tags': contact_data.get('tags', []),
            'status': 'active'
        })
        self.save_contacts()
        return contact_id

    def get_contact(self, contact_id):
        """Get single contact by ID"""
        return next((c for c in self.contacts if c['id'] == contact_id), None)

    def update_contact(self, contact_id, update_data):
        """Update contact with validation"""
        contact = self.get_contact(contact_id)
        if not contact:
            raise ValueError("Contact not found")

        if 'email' in update_data and update_data['email'] != contact['email']:
            if update_data['email'] and not self.validate_email(update_data['email']):
                raise ValueError("Invalid email format")
            if any(c['email'] == update_data['email'] for c in self.contacts if c['id'] != contact_id):
                raise ValueError("Email already exists")

        if 'phone' in update_data and update_data['phone'] and not self.validate_phone(update_data['phone']):
            raise ValueError("Invalid phone number")

        for key, value in update_data.items():
            if key in contact:
                contact[key] = value
                
        if not contact.get('email') and not contact.get('phone'):
            raise ValueError("Must have at least one of email or phone")

        contact['last_modified'] = datetime.now().isoformat()
        contact['avatar'] = self.generate_avatar(contact['name'])
        self.save_contacts()
        return True

    def delete_contact(self, contact_id):
        """Soft delete contact"""
        contact = self.get_contact(contact_id)
        if contact:
            contact['status'] = 'deleted'
            contact['last_modified'] = datetime.now().isoformat()
            self.save_contacts()
            return True
        return False

    def search_contacts(self, query=None, filters=None):
        """Search with filters"""
        results = self.contacts.copy()
        if query:
            query = query.lower()
            results = [c for c in results if (
                query in c['name'].lower() or
                query in c.get('email', '').lower() or
                query in c.get('phone', '').lower() or
                any(query in tag.lower() for tag in c.get('tags', []))
            )]
        if filters:
            if filters.get('status'):
                results = [c for c in results if c['status'] == filters['status']]
            if filters.get('tags'):
                required_tags = set(filters['tags'])
                results = [c for c in results if required_tags.issubset(set(c.get('tags', [])))]
        return sorted(results, key=lambda x: x['name'])

    @staticmethod
    def validate_email(email):
        """Basic email validation"""
        return '@' in email and '.' in email.split('@')[-1]

    @staticmethod
    def validate_phone(phone):
        """Basic phone validation"""
        return len(phone) >= 7 and phone.replace('+', '').replace(' ', '').isdigit()

    def export_csv(self):
        """Export contacts to CSV"""
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=self.contacts[0].keys() if self.contacts else [])
        writer.writeheader()
        writer.writerows(self.contacts)
        return output.getvalue()

    def import_csv(self, csv_data):
        """Import contacts from CSV"""
        reader = csv.DictReader(csv_data.decode().splitlines())
        for row in reader:
            try:
                self.add_contact(row)
            except Exception as e:
                st.error(f"Error importing row: {e}")
        self.save_contacts()

def main():
    st.set_page_config(page_title="Contact Manager", layout="wide", page_icon="📇")
    st.title("📞 Contact Management System")

    if 'manager' not in st.session_state:
        st.session_state.manager = ContactManager()

    manager = st.session_state.manager

    # Custom CSS
    st.markdown("""
    <style>
    .contact-card {padding: 20px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);}
    .avatar {border-radius: 50%; width: 80px; height: 80px;}
    .tag {background: #4CAF50; color: white; padding: 2px 8px; border-radius: 12px; font-size: 0.8em;}
    </style>
    """, unsafe_allow_html=True)

    tabs = st.tabs(["🏠 Dashboard", "➕ Add Contact", "🔍 Search", "⚙️ Settings"])
    
    with tabs[0]:
        st.subheader("Contact Overview")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Contacts", len(manager.contacts))
        with col2:
            active = len([c for c in manager.contacts if c['status'] == 'active'])
            st.metric("Active Contacts", active)
        with col3:
            st.metric("Recent Activity", datetime.now().strftime("%Y-%m-%d"))

        st.subheader("Recent Contacts")
        recent_contacts = sorted(manager.contacts, 
                              key=lambda x: x['last_modified'], reverse=True)[:5]
        for contact in recent_contacts:
            with st.container():
                cols = st.columns([1, 4, 2])
                with cols[0]:
                    st.image(f"data:image/png;base64,{contact['avatar']}", width=80)
                with cols[1]:
                    st.subheader(contact['name'])
                    st.caption(f"✉️ {contact.get('email', 'N/A')} | 📞 {contact.get('phone', 'N/A')}")
                    st.write(" ".join([f"<span class='tag'>{tag}</span>" for tag in contact.get('tags', [])]), 
                           unsafe_allow_html=True)
                with cols[2]:
                    st.caption(f"Created: {contact['created_at'][:10]}")
                    st.caption(f"Last Modified: {contact['last_modified'][:10]}")
                st.markdown("---")

    with tabs[1]:
        with st.form("add_contact_form"):
            cols = st.columns(2)
            contact_data = {
                'name': cols[0].text_input("Name*"),
                'email': cols[1].text_input("Email"),
                'phone': cols[0].text_input("Phone"),
                'company': cols[1].text_input("Company"),
                'tags': cols[0].multiselect("Tags", ["Family", "Friend", "Work", "VIP"]),
                'notes': cols[1].text_area("Notes")
            }
            st.markdown("*Required fields: Name, and at least one of Email or Phone*")
            
            if st.form_submit_button("Add Contact"):
                try:
                    contact_id = manager.add_contact(contact_data)
                    st.success(f"Contact added successfully! ID: {contact_id}")
                except Exception as e:
                    st.error(str(e))

    with tabs[2]:
        col1, col2 = st.columns([3, 1])
        query = col1.text_input("Search contacts")
        status_filter = col2.selectbox("Status", ["all", "active", "deleted"], index=1)
        
        filters = {'status': status_filter if status_filter != 'all' else None}
        results = manager.search_contacts(query, filters)
        
        st.subheader(f"Found {len(results)} contacts")
        for contact in results:
            with st.expander(f"{contact['name']} - {contact.get('email', 'No email')}"):
                cols = st.columns([1, 4])
                with cols[0]:
                    st.image(f"data:image/png;base64,{contact['avatar']}", width=100)
                with cols[1]:
                    st.write(f"**Phone:** {contact.get('phone', 'N/A')}")
                    st.write(f"**Company:** {contact.get('company', 'N/A')}")
                    st.write(f"**Tags:** {', '.join(contact.get('tags', []))}")
                    st.write(f"**Notes:** {contact.get('notes', '')}")
                    
                    if st.button("Edit", key=f"edit_{contact['id']}"):
                        st.session_state.edit_contact = contact
                    if st.button("Delete", key=f"del_{contact['id']}"):
                        manager.delete_contact(contact['id'])
                        st.rerun()

    with tabs[3]:
        st.subheader("Data Management")
        col1, col2 = st.columns(2)
        
        with col1:
            st.download_button(
                label="Export to CSV",
                data=manager.export_csv(),
                file_name="contacts_export.csv",
                mime="text/csv"
            )
        
        with col2:
            uploaded_file = st.file_uploader("Import CSV", type=["csv"])
            if uploaded_file:
                manager.import_csv(uploaded_file.getvalue())
                st.success("Contacts imported successfully!")

        st.subheader("Backup Options")
        if st.button("Create Backup"):
            manager.create_backup()
            st.success("Backup created successfully!")
        
        if st.button("Restore Last Backup"):
            if manager.recover_backup():
                st.success("Backup restored!")
            else:
                st.error("No backups available")

    if 'edit_contact' in st.session_state:
        with st.form("edit_contact_form"):
            contact = st.session_state.edit_contact
            st.subheader(f"Editing: {contact['name']}")
            
            update_data = {
                'name': st.text_input("Name", contact['name']),
                'email': st.text_input("Email", contact.get('email', '')),
                'phone': st.text_input("Phone", contact.get('phone', '')),
                'company': st.text_input("Company", contact.get('company', '')),
                'tags': st.multiselect("Tags", ["Family", "Friend", "Work", "VIP"], 
                                      default=contact.get('tags', [])),
                'notes': st.text_area("Notes", contact.get('notes', ''))
            }
            
            if st.form_submit_button("Save Changes"):
                try:
                    manager.update_contact(contact['id'], update_data)
                    del st.session_state.edit_contact
                    st.rerun()
                except Exception as e:
                    st.error(str(e))
            
            if st.form_submit_button("Cancel"):
                del st.session_state.edit_contact
                st.rerun()

if __name__ == "__main__":
    main()