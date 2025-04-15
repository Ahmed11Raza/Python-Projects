import csv
import datetime
import os.path
import logging
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
from googleapiclient.errors import HttpError

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("attendance_marker.log"), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Google Sheets API scopes
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

class AttendanceMarker:
    def __init__(self, credentials_file='credentials.json'):
        """
        Initialize the AttendanceMarker with Google Sheets API credentials.
        
        Args:
            credentials_file: Path to the service account credentials JSON file
        """
        self.credentials_file = credentials_file
        self.service = None
        
    def authenticate(self):
        """Authenticate with Google Sheets API"""
        try:
            credentials = Credentials.from_service_account_file(
                self.credentials_file, scopes=SCOPES)
            self.service = build('sheets', 'v4', credentials=credentials)
            logger.info("Successfully authenticated with Google Sheets API")
            return True
        except Exception as e:
            logger.error(f"Authentication failed: {str(e)}")
            return False
    
    def read_names_from_csv(self, csv_file):
        """
        Read names from a CSV file.
        
        Args:
            csv_file: Path to the CSV file containing names
            
        Returns:
            List of names from the CSV file
        """
        names = []
        try:
            with open(csv_file, 'r', newline='', encoding='utf-8') as file:
                reader = csv.reader(file)
                header = next(reader, None)  # Skip header row if present
                
                # Determine which column contains names
                name_column = 0
                if header:
                    for i, col in enumerate(header):
                        if 'name' in col.lower():
                            name_column = i
                            break
                
                # Read names from the determined column
                for row in reader:
                    if row and len(row) > name_column:
                        name = row[name_column].strip()
                        if name:  # Only add non-empty names
                            names.append(name)
            
            logger.info(f"Successfully read {len(names)} names from {csv_file}")
            return names
        except Exception as e:
            logger.error(f"Error reading CSV file: {str(e)}")
            return []
    
    def get_date_column(self, spreadsheet_id, sheet_name):
        """
        Find the column for today's date or create a new one.
        
        Args:
            spreadsheet_id: ID of the Google Sheet
            sheet_name: Name of the sheet within the spreadsheet
            
        Returns:
            Column letter for today's date
        """
        try:
            # Get today's date in the format DD/MM/YYYY
            today = datetime.datetime.now().strftime("%d/%m/%Y")
            
            # Get current sheet data to find the date row
            result = self.service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range=f"{sheet_name}!A1:Z1"
            ).execute()
            
            header_row = result.get('values', [[]])[0]
            
            # Check if today's date is already in the header
            date_col = None
            for i, cell in enumerate(header_row):
                if cell == today:
                    date_col = chr(65 + i)  # Convert index to column letter (A, B, C, etc.)
                    logger.info(f"Found existing column {date_col} for today's date")
                    break
            
            # If today's date is not found, add it as a new column
            if not date_col:
                next_col = chr(65 + len(header_row))  # Next available column
                
                # Update the header with today's date
                self.service.spreadsheets().values().update(
                    spreadsheetId=spreadsheet_id,
                    range=f"{sheet_name}!{next_col}1",
                    valueInputOption="USER_ENTERED",
                    body={"values": [[today]]}
                ).execute()
                
                date_col = next_col
                logger.info(f"Created new column {date_col} for today's date")
            
            return date_col
            
        except HttpError as e:
            logger.error(f"Error accessing Google Sheet: {str(e)}")
            return None
    
    def get_name_rows(self, spreadsheet_id, sheet_name, names):
        """
        Find row numbers for each name in the spreadsheet.
        
        Args:
            spreadsheet_id: ID of the Google Sheet
            sheet_name: Name of the sheet within the spreadsheet
            names: List of names to find
            
        Returns:
            Dictionary mapping names to row numbers
        """
        try:
            # Get all names from the first column
            result = self.service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range=f"{sheet_name}!A:A"
            ).execute()
            
            sheet_names = result.get('values', [])
            name_to_row = {}
            
            # Create mapping of names to row numbers (1-indexed for Sheets API)
            for i, row in enumerate(sheet_names):
                if row and row[0].strip():
                    sheet_name = row[0].strip().lower()
                    for name in names:
                        if name.lower() == sheet_name:
                            name_to_row[name] = i + 1  # +1 because Sheets API is 1-indexed
            
            # Log names that weren't found
            missing_names = [name for name in names if name not in name_to_row]
            if missing_names:
                logger.warning(f"Could not find rows for names: {', '.join(missing_names)}")
            
            logger.info(f"Found rows for {len(name_to_row)}/{len(names)} names")
            return name_to_row
            
        except HttpError as e:
            logger.error(f"Error accessing Google Sheet: {str(e)}")
            return {}
    
    def mark_attendance(self, spreadsheet_id, sheet_name, name_to_row, date_column, mark="P"):
        """
        Mark attendance in the Google Sheet.
        
        Args:
            spreadsheet_id: ID of the Google Sheet
            sheet_name: Name of the sheet within the spreadsheet
            name_to_row: Dictionary mapping names to row numbers
            date_column: Column letter for the date
            mark: Attendance mark to use (default "P" for Present)
            
        Returns:
            Number of successfully marked attendees
        """
        try:
            # Prepare batch update
            batch_data = []
            for name, row in name_to_row.items():
                batch_data.append({
                    "range": f"{sheet_name}!{date_column}{row}",
                    "values": [[mark]]
                })
            
            if not batch_data:
                logger.warning("No attendance to mark")
                return 0
            
            # Execute batch update
            body = {
                'valueInputOption': 'USER_ENTERED',
                'data': batch_data
            }
            
            result = self.service.spreadsheets().values().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body=body
            ).execute()
            
            updated_cells = result.get('totalUpdatedCells', 0)
            logger.info(f"Successfully marked attendance for {updated_cells} students")
            return updated_cells
            
        except HttpError as e:
            logger.error(f"Error marking attendance: {str(e)}")
            return 0
    
    def process_attendance(self, spreadsheet_id, sheet_name, csv_file, mark="P"):
        """
        Process attendance by reading names from CSV and marking in Google Sheet.
        
        Args:
            spreadsheet_id: ID of the Google Sheet
            sheet_name: Name of the sheet within the spreadsheet
            csv_file: Path to CSV file containing names
            mark: Attendance mark to use (default "P" for Present)
            
        Returns:
            Boolean indicating success or failure
        """
        # Authenticate with Google Sheets API
        if not self.authenticate():
            return False
        
        # Read names from CSV
        names = self.read_names_from_csv(csv_file)
        if not names:
            logger.error("No names found in CSV file")
            return False
        
        # Get column for today's date
        date_column = self.get_date_column(spreadsheet_id, sheet_name)
        if not date_column:
            return False
        
        # Get row numbers for names
        name_to_row = self.get_name_rows(spreadsheet_id, sheet_name, names)
        if not name_to_row:
            logger.error("Could not find any names in the spreadsheet")
            return False
        
        # Mark attendance
        updated_cells = self.mark_attendance(spreadsheet_id, sheet_name, name_to_row, date_column, mark)
        
        return updated_cells > 0

def main():
    # Configuration
    SPREADSHEET_ID = 'your_spreadsheet_id_here'
    SHEET_NAME = 'Attendance'
    CSV_FILE = 'attendance.csv'
    CREDENTIALS_FILE = 'credentials.json'
    
    # Initialize attendance marker
    marker = AttendanceMarker(credentials_file=CREDENTIALS_FILE)
    
    # Process attendance
    success = marker.process_attendance(SPREADSHEET_ID, SHEET_NAME, CSV_FILE)
    
    if success:
        logger.info("Attendance marking completed successfully")
    else:
        logger.error("Attendance marking failed")

if __name__ == "__main__":
    main()


SPREADSHEET_ID = 'your_spreadsheet_id_here'  # Replace with your Sheet ID
SHEET_NAME = 'Attendance'  # Replace with your sheet tab name
CSV_FILE = 'attendance.csv'  # Path to your CSV file
CREDENTIALS_FILE = 'credentials.json'  # Path to your credentials file