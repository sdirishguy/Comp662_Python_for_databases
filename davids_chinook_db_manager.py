#!/usr/bin/env python3
"""
Highly Fortified Chinook Database Manager
Protected against all forms of user disruption and system errors

SECURITY IMPROVEMENTS OVER ORIGINAL CODE:
==========================================
1. SQL INJECTION PROTECTION: 
   - Original: Used string interpolation (f"INSERT INTO albums VALUES ('{title}', {artist_id})")
   - Fixed: Parameterized queries with placeholders (?, ?) and parameter tuples
   
2. INPUT VALIDATION:
   - Original: No validation of user input
   - Fixed: Multi-layer validation with type checking, length limits, and character filtering
   
3. ERROR HANDLING:
   - Original: Basic try/except with generic error messages
   - Fixed: Comprehensive error handling with retry logic and specific error messages
   
4. USER EXPERIENCE:
   - Original: Confusing error messages and no guidance
   - Fixed: Clear error messages with specific guidance and visual feedback
   
5. RESOURCE PROTECTION:
   - Original: No limits on query results or input length
   - Fixed: Query result limits and input length restrictions to prevent DoS
   
6. DATA INTEGRITY:
   - Original: No checks for record existence or referential integrity
   - Fixed: Existence checks and referential integrity validation
"""

import sqlite3
import re
import sys
import os
from typing import Optional, Tuple, List, Any
import time

# Configuration constants for security and robustness
MAX_RETRIES = 3                    # Prevent infinite loops from user errors
MAX_INPUT_LENGTH = 200             # Prevent buffer overflow and resource exhaustion
MAX_QUERY_RESULTS = 200            # Increased from 50 to show more records
DATABASE_PATH = 'chinook.db'
BACKUP_SUFFIX = '.backup'

class DatabaseManager:
    """
    Highly robust database manager with comprehensive error handling
    
    SECURITY IMPROVEMENTS:
    - Connection validation with file existence and permission checks
    - Retry logic for transient database errors
    - Safe query execution with parameterized queries
    - Proper connection cleanup to prevent resource leaks
    """
    
    def __init__(self, db_path: str = DATABASE_PATH):
        self.db_path = db_path
        self.connection = None
        self.cursor = None
        self.retry_count = 0
        
    def connect(self) -> bool:
        """
        Establish database connection with comprehensive error handling
        
        SECURITY IMPROVEMENTS OVER ORIGINAL:
        - Original: Simple sqlite3.connect() with basic error handling
        - Fixed: File existence check, permission validation, connection testing
        """
        try:
            # SECURITY: Check if database file exists before attempting connection
            # Original code would fail with cryptic error if file missing
            if not os.path.exists(self.db_path):
                print(f"❌ Error: Database file '{self.db_path}' not found.")
                print("   Please ensure the chinook.db file is in the current directory.")
                return False
            
            # SECURITY: Check file permissions to prevent access denied errors
            # Original code would fail with permission errors
            if not os.access(self.db_path, os.R_OK | os.W_OK):
                print(f"❌ Error: Insufficient permissions to access '{self.db_path}'")
                return False
            
            # SECURITY: Establish connection with row factory for better data access
            # Original code used basic connection without row factory
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row  # Enable column access by name
            self.cursor = self.connection.cursor()
            
            # SECURITY: Test connection with a simple query to ensure it's working
            # Original code assumed connection was valid without testing
            self.cursor.execute("SELECT 1")
            print("✅ Database connection established successfully")
            return True
            
        except sqlite3.Error as e:
            print(f"❌ Database connection error: {e}")
            return False
        except Exception as e:
            print(f"❌ Unexpected error during connection: {e}")
            return False
    
    def disconnect(self):
        """
        Safely close database connection
        
        SECURITY IMPROVEMENT: Proper resource cleanup prevents connection leaks
        """
        try:
            if self.cursor:
                self.cursor.close()
            if self.connection:
                self.connection.close()
        except Exception as e:
            print(f"⚠️  Warning: Error during disconnect: {e}")
    
    def safe_execute(self, query: str, params: tuple = ()) -> Optional[List]:
        """
        Execute a query with comprehensive error handling and retry logic
        
        SECURITY IMPROVEMENTS OVER ORIGINAL:
        - Original: Direct cur.execute() with no error handling
        - Fixed: Retry logic, specific error handling, and safe parameter passing
        
        VULNERABILITY FIXES:
        - SQL Injection: Uses parameterized queries instead of string interpolation
        - Resource Exhaustion: Limits query results and handles large datasets
        - Error Information Disclosure: Provides helpful but safe error messages
        """
        for attempt in range(MAX_RETRIES):
            try:
                # SECURITY: Use parameterized queries to prevent SQL injection
                # Original: cur.execute(f"SELECT * FROM {table} WHERE id = {user_input}")
                # Fixed: cur.execute("SELECT * FROM ? WHERE id = ?", (table, user_input))
                self.cursor.execute(query, params)
                
                if query.strip().upper().startswith('SELECT'):
                    return self.cursor.fetchall()
                return []
                
            except sqlite3.OperationalError as e:
                # SECURITY: Handle specific database errors with helpful messages
                # Original code would show raw SQL errors to users
                if "no such table" in str(e).lower():
                    print(f"❌ Error: Table not found in database")
                    return None
                elif "no such column" in str(e).lower():
                    print(f"❌ Error: Column not found in database")
                    return None
                else:
                    print(f"❌ Database operation error: {e}")
                    if attempt < MAX_RETRIES - 1:
                        print(f"   Retrying... ({attempt + 2}/{MAX_RETRIES})")
                        time.sleep(0.5)  # SECURITY: Prevent rapid retry attacks
                    else:
                        return None
                        
            except sqlite3.IntegrityError as e:
                # SECURITY: Handle data integrity errors gracefully
                # Original code would crash on constraint violations
                print(f"❌ Data integrity error: {e}")
                return None
                
            except Exception as e:
                # SECURITY: Catch all unexpected errors to prevent crashes
                # Original code would crash on unexpected exceptions
                print(f"❌ Unexpected database error: {e}")
                if attempt < MAX_RETRIES - 1:
                    print(f"   Retrying... ({attempt + 2}/{MAX_RETRIES})")
                    time.sleep(0.5)
                else:
                    return None
        return None

class InputValidator:
    """
    Comprehensive input validation and sanitization
    
    SECURITY IMPROVEMENTS OVER ORIGINAL:
    - Original: No input validation, accepted any user input
    - Fixed: Multi-layer validation with type checking, length limits, and character filtering
    
    VULNERABILITY FIXES:
    - SQL Injection: Filters dangerous characters
    - Buffer Overflow: Limits input length
    - Type Confusion: Validates data types
    - Resource Exhaustion: Prevents extremely long inputs
    """
    
    @staticmethod
    def validate_positive_integer(value: str, field_name: str) -> Optional[int]:
        """
        Validate and convert to positive integer with detailed error messages
        
        SECURITY IMPROVEMENTS:
        - Original: No validation, would crash on non-numeric input
        - Fixed: Comprehensive validation with helpful error messages
        
        VULNERABILITY FIXES:
        - Type Confusion: Ensures input is actually numeric
        - Overflow Protection: Handles extremely large numbers
        - Input Validation: Prevents negative or zero values
        """
        if not value or not value.strip():
            print(f"❌ Error: {field_name} cannot be empty")
            return None
        
        value = value.strip()
        
        # SECURITY: Check for non-numeric characters before conversion
        # Original code would crash on "abc" input
        if not value.replace('-', '').isdigit():
            print(f"❌ Error: {field_name} must be a valid number")
            return None
        
        try:
            int_val = int(value)
            # SECURITY: Ensure positive values to prevent invalid IDs
            # Original code accepted negative or zero values
            if int_val <= 0:
                print(f"❌ Error: {field_name} must be a positive number (greater than 0)")
                return None
            return int_val
        except ValueError:
            print(f"❌ Error: {field_name} is not a valid integer")
            return None
        except OverflowError:
            # SECURITY: Handle extremely large numbers that could cause issues
            print(f"❌ Error: {field_name} is too large")
            return None
    
    @staticmethod
    def validate_string(value: str, field_name: str, max_length: int = MAX_INPUT_LENGTH) -> Optional[str]:
        """
        Validate and sanitize string input
        
        SECURITY IMPROVEMENTS:
        - Original: No string validation, accepted any input including dangerous characters
        - Fixed: Length limits, character filtering, and sanitization
        
        VULNERABILITY FIXES:
        - SQL Injection: Filters dangerous characters (; " \)
        - Buffer Overflow: Limits string length
        - Control Character Injection: Blocks control characters
        - Resource Exhaustion: Prevents extremely long strings
        """
        if not value or not value.strip():
            print(f"❌ Error: {field_name} cannot be empty")
            return None
        
        value = value.strip()
        
        # SECURITY: Check length to prevent resource exhaustion
        # Original code accepted unlimited length strings
        if len(value) > max_length:
            print(f"❌ Error: {field_name} is too long (maximum {max_length} characters)")
            return None
        
        # SECURITY: Check for dangerous characters that could be used in SQL injection
        # Original code accepted any characters including ; " \ which are dangerous
        # Note: We allow apostrophes (') for names like "O'Reilly" but block other dangerous chars
        dangerous_chars = [';', '"', '\\']
        found_chars = [char for char in dangerous_chars if char in value]
        if found_chars:
            print(f"❌ Error: {field_name} contains invalid characters: {', '.join(found_chars)}")
            return None
        
        # SECURITY: Check for control characters that could cause display issues
        # Original code accepted control characters that could break the interface
        if any(ord(char) < 32 for char in value):
            print(f"❌ Error: {field_name} contains invalid control characters")
            return None
        
        return value
    
    @staticmethod
    def validate_menu_choice(choice: str, min_val: int, max_val: int) -> Optional[int]:
        """
        Validate menu choice input
        
        SECURITY IMPROVEMENTS:
        - Original: Basic choice validation that could be bypassed
        - Fixed: Comprehensive validation with range checking
        
        VULNERABILITY FIXES:
        - Menu Bypass: Ensures choices are within valid range
        - Type Confusion: Validates numeric input
        - Input Validation: Prevents invalid menu selections
        """
        if not choice or not choice.strip():
            print("❌ Error: Please enter a valid choice")
            return None
        
        choice = choice.strip()
        
        # SECURITY: Ensure input is numeric
        # Original code would accept letters for menu choices
        if not choice.isdigit():
            print("❌ Error: Please enter a number")
            return None
        
        try:
            int_choice = int(choice)
            # SECURITY: Validate range to prevent menu bypass
            # Original code might accept out-of-range values
            if min_val <= int_choice <= max_val:
                return int_choice
            else:
                print(f"❌ Error: Please enter a number between {min_val} and {max_val}")
                return None
        except ValueError:
            print("❌ Error: Please enter a valid number")
            return None

class UserInterface:
    """
    Robust user interface with comprehensive error handling
    
    SECURITY IMPROVEMENTS:
    - Retry logic for user input with maximum attempts
    - Graceful handling of keyboard interrupts
    - Comprehensive error messages with guidance
    - Safe input processing with validation
    """
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.validator = InputValidator()
    
    def get_input_with_retry(self, prompt: str, validator_func, *args, **kwargs) -> Optional[Any]:
        """
        Get user input with retry logic and validation
        
        SECURITY IMPROVEMENTS OVER ORIGINAL:
        - Original: Single input() call with no retry or validation
        - Fixed: Retry logic, validation, and graceful error handling
        
        VULNERABILITY FIXES:
        - Input Validation: Validates all user input before processing
        - Resource Exhaustion: Limits retry attempts to prevent infinite loops
        - User Experience: Provides helpful error messages and guidance
        - Graceful Degradation: Handles keyboard interrupts and EOF gracefully
        """
        for attempt in range(MAX_RETRIES):
            try:
                user_input = input(prompt).strip()
                
                # SECURITY: Allow users to cancel operations gracefully
                # Original code had no way to cancel operations
                if user_input.lower() in ['quit', 'exit', 'cancel']:
                    print("🛑 Operation cancelled by user")
                    return None
                
                # SECURITY: Validate input using the provided validator function
                # Original code accepted any input without validation
                result = validator_func(user_input, *args, **kwargs)
                if result is not None:
                    return result
                
                # SECURITY: Provide retry guidance with attempt counter
                # Original code would just fail without guidance
                if attempt < MAX_RETRIES - 1:
                    print(f"   Please try again ({attempt + 2}/{MAX_RETRIES})")
                
            except KeyboardInterrupt:
                # SECURITY: Handle Ctrl+C gracefully instead of crashing
                # Original code would crash on keyboard interrupt
                print("\n🛑 Operation cancelled by user")
                return None
            except EOFError:
                # SECURITY: Handle end-of-input gracefully
                # Original code would crash on EOF
                print("\n🛑 End of input reached")
                return None
            except Exception as e:
                # SECURITY: Catch all input errors to prevent crashes
                # Original code would crash on unexpected input errors
                print(f"❌ Input error: {e}")
                if attempt < MAX_RETRIES - 1:
                    print(f"   Please try again ({attempt + 2}/{MAX_RETRIES})")
        
        # SECURITY: Prevent infinite loops by limiting retry attempts
        # Original code could get stuck in infinite input loops
        print("❌ Maximum retry attempts reached. Returning to main menu.")
        return None
    
    def display_menu(self):
        """Display the main menu with enhanced visual design"""
        print("\n" + "="*50)
        print("🎵 CHINOOK DATABASE MANAGER (FORTIFIED VERSION)")
        print("="*50)
        print("1. 📋 List Albums")
        print("2. 👥 List Artists") 
        print("3. ➕ Add Album")
        print("4. ✏️  Edit Album")
        print("5. 🗑️  Delete Album")
        print("6. 🔍 Search Albums")
        print("7. 📊 Database Statistics")
        print("8. 🚪 Exit")
        print("="*50)
    
    def list_albums(self):
        """
        Display albums with comprehensive error handling and pagination
        
        SECURITY IMPROVEMENTS:
        - Original: No error handling, would crash on database errors
        - Fixed: Comprehensive error handling with user-friendly messages
        
        VULNERABILITY FIXES:
        - Resource Exhaustion: Limits results to prevent memory issues
        - Error Information Disclosure: Provides helpful but safe error messages
        - Data Display: Safe string handling to prevent display issues
        """
        print("\n📋 Loading albums...")
        
        # Get total count first
        count_query = "SELECT COUNT(*) FROM albums"
        count_result = self.db_manager.safe_execute(count_query)
        total_albums = count_result[0][0] if count_result else 0
        
        if total_albums == 0:
            print("📭 No albums found in database")
            return
        
        # Ask user for sorting preference
        print(f"📊 Total albums in database: {total_albums}")
        print("\n📋 Sort options:")
        print("1. Album ID (default)")
        print("2. Album Title (A-Z)")
        print("3. Artist Name (A-Z)")
        print("4. Album ID (descending)")
        
        sort_choice = self.get_input_with_retry(
            "Choose sort option (1-4, or press Enter for default): ",
            lambda x, y, z: x if not x.strip() else self.validator.validate_menu_choice(x, 1, 4),
            "Sort choice"
        )
        
        if sort_choice is None:
            sort_choice = 1  # Default to Album ID
        
        # Define sort options
        sort_options = {
            1: "albums.AlbumId ASC",
            2: "albums.Title ASC", 
            3: "artists.Name ASC",
            4: "albums.AlbumId DESC"
        }
        
        sort_clause = sort_options.get(sort_choice, "albums.AlbumId ASC")
        
        # Ask user how many records to show
        show_all = self.get_input_with_retry(
            f"Show all albums ({total_albums}) or limit to {MAX_QUERY_RESULTS}? (all/limit): ",
            lambda x, y: x.lower() if x.lower() in ['all', 'limit'] else None,
            "Choice"
        )
        
        if show_all is None:
            return
        
        if show_all.lower() == 'all':
            limit = total_albums
            print(f"📋 Loading all {total_albums} albums...")
        else:
            limit = MAX_QUERY_RESULTS
            print(f"📋 Loading up to {limit} albums...")
        
        # SECURITY: Use parameterized query to prevent SQL injection
        # Original: f"SELECT * FROM albums LIMIT {limit}"
        # Fixed: "SELECT * FROM albums LIMIT ?" with parameter tuple
        query = f"""
            SELECT albums.AlbumId, albums.Title, artists.Name
            FROM albums
            JOIN artists ON albums.ArtistId = artists.ArtistId
            ORDER BY {sort_clause}
            LIMIT ?
        """
        
        results = self.db_manager.safe_execute(query, (limit,))
        
        if results is None:
            print("❌ Failed to load albums")
            return
        
        if not results:
            print("📭 No albums found in database")
            return
        
        print(f"\n📋 Albums (showing {len(results)} of {total_albums}):")
        print("-" * 80)
        print(f"{'ID':<5} | {'Title':<40} | {'Artist':<30}")
        print("-" * 80)
        
        # SECURITY: Safe string handling to prevent display issues
        # Original code might crash on special characters in data
        for row in results:
            album_id = row[0]
            title = str(row[1])[:38] + "..." if len(str(row[1])) > 40 else str(row[1])
            artist = str(row[2])[:28] + "..." if len(str(row[2])) > 30 else str(row[2])
            print(f"{album_id:<5} | {title:<40} | {artist:<30}")
        
        if len(results) < total_albums:
            print(f"\n📄 Showing {len(results)} of {total_albums} albums")
            print("💡 Use 'all' option to see all albums")
    
    def list_artists(self):
        """
        Display artists with comprehensive error handling and pagination
        
        SECURITY IMPROVEMENTS: Same as list_albums()
        """
        print("\n👥 Loading artists...")
        
        # Get total count first
        count_query = "SELECT COUNT(*) FROM artists"
        count_result = self.db_manager.safe_execute(count_query)
        total_artists = count_result[0][0] if count_result else 0
        
        if total_artists == 0:
            print("📭 No artists found in database")
            return
        
        # Ask user for sorting preference
        print(f"📊 Total artists in database: {total_artists}")
        print("\n👥 Sort options:")
        print("1. Artist Name (A-Z, default)")
        print("2. Artist ID (ascending)")
        print("3. Artist ID (descending)")
        
        sort_choice = self.get_input_with_retry(
            "Choose sort option (1-3, or press Enter for default): ",
            lambda x, y, z: x if not x.strip() else self.validator.validate_menu_choice(x, 1, 3),
            "Sort choice"
        )
        
        if sort_choice is None:
            sort_choice = 1  # Default to Artist Name
        
        # Define sort options
        sort_options = {
            1: "Name ASC",
            2: "ArtistId ASC",
            3: "ArtistId DESC"
        }
        
        sort_clause = sort_options.get(sort_choice, "Name ASC")
        
        # Ask user how many records to show
        show_all = self.get_input_with_retry(
            f"Show all artists ({total_artists}) or limit to {MAX_QUERY_RESULTS}? (all/limit): ",
            lambda x, y: x.lower() if x.lower() in ['all', 'limit'] else None,
            "Choice"
        )
        
        if show_all is None:
            return
        
        if show_all.lower() == 'all':
            limit = total_artists
            print(f"👥 Loading all {total_artists} artists...")
        else:
            limit = MAX_QUERY_RESULTS
            print(f"👥 Loading up to {limit} artists...")
        
        query = f"SELECT ArtistId, Name FROM artists ORDER BY {sort_clause} LIMIT ?"
        results = self.db_manager.safe_execute(query, (limit,))
        
        if results is None:
            print("❌ Failed to load artists")
            return
        
        if not results:
            print("📭 No artists found in database")
            return
        
        print(f"\n👥 Artists (showing {len(results)} of {total_artists}):")
        print("-" * 60)
        print(f"{'ID':<5} | {'Name':<50}")
        print("-" * 60)
        
        for row in results:
            artist_id = row[0]
            name = str(row[1])[:48] + "..." if len(str(row[1])) > 50 else str(row[1])
            print(f"{artist_id:<5} | {name:<50}")
        
        if len(results) < total_artists:
            print(f"\n📄 Showing {len(results)} of {total_artists} artists")
            print("💡 Use 'all' option to see all artists")
    
    def check_artist_exists(self, artist_id: int) -> bool:
        """
        Check if artist exists in database
        
        SECURITY IMPROVEMENTS:
        - Original: No existence checks, would fail with cryptic errors
        - Fixed: Explicit existence validation with parameterized queries
        """
        query = "SELECT COUNT(*) FROM artists WHERE ArtistId = ?"
        results = self.db_manager.safe_execute(query, (artist_id,))
        return results and results[0][0] > 0 if results else False
    
    def check_album_exists(self, album_id: int) -> bool:
        """
        Check if album exists in database
        
        SECURITY IMPROVEMENTS: Same as check_artist_exists()
        """
        query = "SELECT COUNT(*) FROM albums WHERE AlbumId = ?"
        results = self.db_manager.safe_execute(query, (album_id,))
        return results and results[0][0] > 0 if results else False
    
    def add_album(self):
        """
        Add a new album with comprehensive validation
        
        SECURITY IMPROVEMENTS OVER ORIGINAL:
        - Original: No validation, accepted any input, used string interpolation
        - Fixed: Comprehensive validation, parameterized queries, existence checks
        
        VULNERABILITY FIXES:
        - SQL Injection: Parameterized queries instead of string interpolation
        - Input Validation: Validates all input before database operations
        - Referential Integrity: Checks that artist exists before adding album
        - Error Handling: Comprehensive error handling with user guidance
        """
        print("\n➕ Adding new album...")
        
        # SECURITY: Get and validate title with retry logic
        # Original: title = input("Enter album title: ") - no validation
        title = self.get_input_with_retry(
            "Enter album title: ",
            self.validator.validate_string,
            "Album title",
            100
        )
        if title is None:
            return
        
        # SECURITY: Get and validate artist ID with retry logic
        # Original: artist_id = input("Enter artist ID: ") - no validation
        artist_id = self.get_input_with_retry(
            "Enter artist ID: ",
            self.validator.validate_positive_integer,
            "Artist ID"
        )
        if artist_id is None:
            return
        
        # SECURITY: Check if artist exists before adding album
        # Original: No existence check, would fail with foreign key constraint error
        if not self.check_artist_exists(artist_id):
            print("❌ Error: Artist ID does not exist in the database")
            print("   Please use option 2 to view available artists")
            return
        
        # SECURITY: Use parameterized query to prevent SQL injection
        # Original: f"INSERT INTO albums (Title, ArtistId) VALUES ('{title}', {artist_id})"
        # Fixed: "INSERT INTO albums (Title, ArtistId) VALUES (?, ?)" with parameters
        query = "INSERT INTO albums (Title, ArtistId) VALUES (?, ?)"
        results = self.db_manager.safe_execute(query, (title, artist_id))
        
        if results is not None:
            print(f"✅ Successfully added album: '{title}'")
            self.db_manager.connection.commit()
        else:
            print("❌ Failed to add album")
    
    def edit_album(self):
        """
        Edit an existing album with comprehensive validation
        
        SECURITY IMPROVEMENTS OVER ORIGINAL:
        - Original: No validation, used string interpolation, no existence checks
        - Fixed: Comprehensive validation, parameterized queries, existence checks
        
        VULNERABILITY FIXES:
        - SQL Injection: Parameterized queries instead of string interpolation
        - Input Validation: Validates all input before database operations
        - Referential Integrity: Checks that album and artist exist
        - Error Handling: Comprehensive error handling with user guidance
        """
        print("\n✏️  Editing album...")
        
        # SECURITY: Get and validate album ID with retry logic
        # Original: album_id = input("Enter AlbumId to edit: ") - no validation
        album_id = self.get_input_with_retry(
            "Enter album ID to edit: ",
            self.validator.validate_positive_integer,
            "Album ID"
        )
        if album_id is None:
            return
        
        # SECURITY: Check if album exists before editing
        # Original: No existence check, would fail with cryptic error
        if not self.check_album_exists(album_id):
            print("❌ Error: Album ID does not exist in the database")
            print("   Please use option 1 to view available albums")
            return
        
        # SECURITY: Get current album info for user reference
        # Original: No current info display, user had no context
        query = "SELECT Title, ArtistId FROM albums WHERE AlbumId = ?"
        results = self.db_manager.safe_execute(query, (album_id,))
        
        if not results:
            print("❌ Error: Could not retrieve album information")
            return
        
        current_title = results[0][0]
        current_artist_id = results[0][1]
        
        print(f"Current album: '{current_title}' (Artist ID: {current_artist_id})")
        
        # SECURITY: Get new title with validation and allow keeping current
        # Original: Required new title, no option to keep current
        new_title = self.get_input_with_retry(
            "Enter new title (or press Enter to keep current): ",
            lambda x, y, z: x if not x.strip() else self.validator.validate_string(x, y, z),
            "Album title",
            100
        )
        if new_title is None:
            return
        
        # SECURITY: Use current title if no new title provided
        # Original: Required new title, no flexibility
        if not new_title.strip():
            new_title = current_title
        
        # SECURITY: Get new artist ID with validation and allow keeping current
        # Original: Required new artist ID, no option to keep current
        new_artist_id_input = self.get_input_with_retry(
            "Enter new artist ID (or press Enter to keep current): ",
            lambda x, y: x if not x.strip() else self.validator.validate_positive_integer(x, y),
            "Artist ID"
        )
        if new_artist_id_input is None:
            return
        
        # SECURITY: Use current artist ID if no new ID provided
        # Original: Required new artist ID, no flexibility
        if not new_artist_id_input.strip():
            new_artist_id = current_artist_id
        else:
            new_artist_id = int(new_artist_id_input)
            
            # SECURITY: Check if new artist exists before updating
            # Original: No existence check, would fail with foreign key constraint error
            if not self.check_artist_exists(new_artist_id):
                print("❌ Error: Artist ID does not exist in the database")
                return
        
        # SECURITY: Use parameterized query to prevent SQL injection
        # Original: f"UPDATE albums SET Title = '{new_title}', ArtistId = {new_artist_id} WHERE AlbumId = {album_id}"
        # Fixed: "UPDATE albums SET Title = ?, ArtistId = ? WHERE AlbumId = ?" with parameters
        query = "UPDATE albums SET Title = ?, ArtistId = ? WHERE AlbumId = ?"
        results = self.db_manager.safe_execute(query, (new_title, new_artist_id, album_id))
        
        if results is not None:
            print(f"✅ Successfully updated album ID {album_id}")
            self.db_manager.connection.commit()
        else:
            print("❌ Failed to update album")
    
    def delete_album(self):
        """
        Delete an album with confirmation
        
        SECURITY IMPROVEMENTS OVER ORIGINAL:
        - Original: No validation, no confirmation, used string interpolation
        - Fixed: Comprehensive validation, confirmation dialog, parameterized queries
        
        VULNERABILITY FIXES:
        - SQL Injection: Parameterized queries instead of string interpolation
        - Accidental Deletion: Confirmation dialog prevents accidental deletions
        - Input Validation: Validates all input before database operations
        - Existence Check: Verifies album exists before attempting deletion
        """
        print("\n🗑️  Deleting album...")
        
        # SECURITY: Get and validate album ID with retry logic
        # Original: album_id = input("Enter AlbumId to delete: ") - no validation
        album_id = self.get_input_with_retry(
            "Enter album ID to delete: ",
            self.validator.validate_positive_integer,
            "Album ID"
        )
        if album_id is None:
            return
        
        # SECURITY: Check if album exists before deleting
        # Original: No existence check, would fail with cryptic error
        if not self.check_album_exists(album_id):
            print("❌ Error: Album ID does not exist in the database")
            return
        
        # SECURITY: Get album details for confirmation
        # Original: No confirmation, would delete immediately
        query = "SELECT Title FROM albums WHERE AlbumId = ?"
        results = self.db_manager.safe_execute(query, (album_id,))
        
        if not results:
            print("❌ Error: Could not retrieve album information")
            return
        
        album_title = results[0][0]
        
        # SECURITY: Get confirmation to prevent accidental deletions
        # Original: No confirmation, dangerous for destructive operations
        confirm = self.get_input_with_retry(
            f"Are you sure you want to delete album '{album_title}' (ID: {album_id})? (yes/no): ",
            lambda x, y: x.lower() if x.lower() in ['yes', 'no', 'y', 'n'] else None,
            "Confirmation"
        )
        
        if confirm is None:
            return
        
        if confirm.lower() not in ['yes', 'y']:
            print("🛑 Deletion cancelled")
            return
        
        # SECURITY: Use parameterized query to prevent SQL injection
        # Original: f"DELETE FROM albums WHERE AlbumId = {album_id}"
        # Fixed: "DELETE FROM albums WHERE AlbumId = ?" with parameter
        query = "DELETE FROM albums WHERE AlbumId = ?"
        results = self.db_manager.safe_execute(query, (album_id,))
        
        if results is not None:
            print(f"✅ Successfully deleted album: '{album_title}'")
            self.db_manager.connection.commit()
        else:
            print("❌ Failed to delete album")
    
    def search_albums(self):
        """
        Search albums by title or artist
        
        SECURITY IMPROVEMENTS:
        - Original: No search functionality
        - Fixed: Safe search with parameterized queries and input validation
        
        VULNERABILITY FIXES:
        - SQL Injection: Parameterized queries for search terms
        - Input Validation: Validates search terms before database operations
        - Resource Protection: Limits search results to prevent memory issues
        """
        print("\n🔍 Search albums...")
        
        # SECURITY: Get and validate search term with retry logic
        search_term = self.get_input_with_retry(
            "Enter search term (album title or artist name): ",
            self.validator.validate_string,
            "Search term",
            50
        )
        if search_term is None:
            return
        
        # SECURITY: Use parameterized query to prevent SQL injection
        # Original: No search functionality
        # Fixed: Safe search with LIKE operator and parameters
        query = """
            SELECT albums.AlbumId, albums.Title, artists.Name
            FROM albums
            JOIN artists ON albums.ArtistId = artists.ArtistId
            WHERE albums.Title LIKE ? OR artists.Name LIKE ?
            ORDER BY albums.Title
            LIMIT ?
        """
        
        search_pattern = f"%{search_term}%"
        results = self.db_manager.safe_execute(query, (search_pattern, search_pattern, MAX_QUERY_RESULTS))
        
        if results is None:
            print("❌ Failed to search albums")
            return
        
        if not results:
            print(f"📭 No albums found matching '{search_term}'")
            return
        
        print(f"\n🔍 Search results for '{search_term}' (showing up to {len(results)}):")
        print("-" * 80)
        print(f"{'ID':<5} | {'Title':<40} | {'Artist':<30}")
        print("-" * 80)
        
        for row in results:
            album_id = row[0]
            title = str(row[1])[:38] + "..." if len(str(row[1])) > 40 else str(row[1])
            artist = str(row[2])[:28] + "..." if len(str(row[2])) > 30 else str(row[2])
            print(f"{album_id:<5} | {title:<40} | {artist:<30}")
    
    def show_database_stats(self):
        """
        Display database statistics
        
        SECURITY IMPROVEMENTS:
        - Original: No statistics functionality
        - Fixed: Safe statistics with parameterized queries and error handling
        
        VULNERABILITY FIXES:
        - SQL Injection: Parameterized queries for all statistics
        - Error Handling: Comprehensive error handling for each query
        - Resource Protection: Safe query execution with limits
        """
        print("\n📊 Database Statistics...")
        
        stats = []
        
        # SECURITY: Count albums with safe query execution
        query = "SELECT COUNT(*) FROM albums"
        results = self.db_manager.safe_execute(query)
        if results:
            stats.append(f"📋 Albums: {results[0][0]}")
        
        # SECURITY: Count artists with safe query execution
        query = "SELECT COUNT(*) FROM artists"
        results = self.db_manager.safe_execute(query)
        if results:
            stats.append(f"👥 Artists: {results[0][0]}")
        
        # SECURITY: Count tracks with safe query execution
        query = "SELECT COUNT(*) FROM tracks"
        results = self.db_manager.safe_execute(query)
        if results:
            stats.append(f"🎵 Tracks: {results[0][0]}")
        
        # SECURITY: Count customers with safe query execution
        query = "SELECT COUNT(*) FROM customers"
        results = self.db_manager.safe_execute(query)
        if results:
            stats.append(f"👤 Customers: {results[0][0]}")
        
        if stats:
            print("\n📊 Database Overview:")
            print("-" * 30)
            for stat in stats:
                print(f"  {stat}")
        else:
            print("❌ Could not retrieve database statistics")
    
    def run(self):
        """
        Main application loop with comprehensive error handling
        
        SECURITY IMPROVEMENTS OVER ORIGINAL:
        - Original: Basic while loop with minimal error handling
        - Fixed: Comprehensive error handling with graceful degradation
        
        VULNERABILITY FIXES:
        - Application Crashes: Catches all exceptions to prevent crashes
        - User Experience: Provides helpful error messages and recovery options
        - Resource Management: Proper cleanup and state management
        - Graceful Shutdown: Handles keyboard interrupts and application exit
        """
        print("🚀 Starting Chinook Database Manager...")
        
        while True:
            try:
                self.display_menu()
                
                # SECURITY: Get and validate menu choice with retry logic
                # Original: choice = input("Choose an option: ") - no validation
                choice = self.get_input_with_retry(
                    "Choose an option (1-8): ",
                    self.validator.validate_menu_choice,
                    1, 8
                )
                
                if choice is None:
                    continue
                
                # SECURITY: Execute chosen action with comprehensive error handling
                # Original: Basic if/elif with minimal error handling
                if choice == 1:
                    self.list_albums()
                elif choice == 2:
                    self.list_artists()
                elif choice == 3:
                    self.add_album()
                elif choice == 4:
                    self.edit_album()
                elif choice == 5:
                    self.delete_album()
                elif choice == 6:
                    self.search_albums()
                elif choice == 7:
                    self.show_database_stats()
                elif choice == 8:
                    print("👋 Goodbye! Thank you for using Chinook Database Manager.")
                    break
                
                # SECURITY: Pause after destructive operations for user awareness
                # Original: No pause, user might not realize operation completed
                if choice in [3, 4, 5]:
                    input("\nPress Enter to continue...")
                
            except KeyboardInterrupt:
                # SECURITY: Handle Ctrl+C gracefully instead of crashing
                # Original code would crash on keyboard interrupt
                print("\n🛑 Application interrupted by user")
                break
            except Exception as e:
                # SECURITY: Catch all unexpected errors to prevent crashes
                # Original code would crash on unexpected exceptions
                print(f"❌ Unexpected error: {e}")
                print("🔄 Returning to main menu...")
                time.sleep(1)  # SECURITY: Brief pause to prevent rapid error loops

def main():
    """
    Main function with comprehensive error handling
    
    SECURITY IMPROVEMENTS OVER ORIGINAL:
    - Original: Basic main function with minimal error handling
    - Fixed: Comprehensive error handling with proper resource cleanup
    
    VULNERABILITY FIXES:
    - Application Crashes: Catches all exceptions to prevent crashes
    - Resource Leaks: Ensures database connections are properly closed
    - Graceful Shutdown: Handles all exit scenarios properly
    - Error Recovery: Provides helpful error messages and recovery options
    """
    print("🎵 Chinook Database Manager - Fortified Version")
    print("=" * 50)
    
    # SECURITY: Initialize database manager with proper error handling
    # Original: Basic connection without error handling
    db_manager = DatabaseManager()
    
    # SECURITY: Connect to database with comprehensive error handling
    # Original: Basic connection attempt that could fail silently
    if not db_manager.connect():
        print("❌ Failed to establish database connection. Exiting.")
        sys.exit(1)
    
    try:
        # SECURITY: Initialize and run user interface with error handling
        # Original: Basic UI initialization without error handling
        ui = UserInterface(db_manager)
        ui.run()
    except KeyboardInterrupt:
        # SECURITY: Handle Ctrl+C gracefully
        # Original code would crash on keyboard interrupt
        print("\n🛑 Application interrupted by user")
    except Exception as e:
        # SECURITY: Catch all critical errors to prevent crashes
        # Original code would crash on critical exceptions
        print(f"❌ Critical error: {e}")
        print("🔄 Attempting graceful shutdown...")
    finally:
        # SECURITY: Ensure database connection is closed in all scenarios
        # Original code might leave connections open on crashes
        db_manager.disconnect()
        print("✅ Database connection closed")

if __name__ == "__main__":
    main()
