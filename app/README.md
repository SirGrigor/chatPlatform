Project structure:
```
/learning_platform_chat
|-- app
|   |-- __init__.py
|   |-- main.py                      # FastAPI application entry point, setups the application.
|   |-- dependencies.py              # Defines global dependencies, including authentication dependencies.
|
|-- api
|   |-- __init__.py
|   |-- api_v1
|   |   |-- __init__.py
|   |   |-- endpoints
|   |   |   |-- __init__.py
|   |   |   |-- auth.py              # New endpoint for handling authentication and token refresh.
|   |   |   |-- chat.py              # Manages WebSocket endpoints for chat, using JWT for user & course identification.
|   |   |   |-- course.py            # Provides endpoints for course CRUD operations, secured by user roles.
|   |   |   |-- document.py          # Handles document upload/download, associating documents with courses.
|   |   |   |-- user.py              # Facilitates user registration and management.
|
|-- core
|   |-- __init__.py
|   |-- config.py                    # Configuration settings, including JWT secret keys and expiration times.
|
|-- db
|   |-- __init__.py
|   |-- base_class.py                # Base class for SQLAlchemy models.
|   |-- session.py                   # Manages database session lifecycle.
|   |-- models
|   |   |-- __init__.py
|   |   |-- user.py                  # User model.
|   |   |-- course.py                # Course model.
|   |   |-- chat_session.py          # Chat session model.
|   |   |-- message.py               # Message model.
|   |   |-- document.py              # Document model.
|   |   |-- refresh_token.py         # New model for storing refresh tokens.
|
|-- schemas
|   |-- __init__.py
|   |-- auth.py                      # New schema for authentication requests and token responses.
|   |-- user.py                      # User data validation and serialization.
|   |-- course.py                    # Course data structures.
|   |-- chat.py                      # Chat message data structures.
|   |-- document.py                  # Document management schemas.
|
|-- services
|   |-- __init__.py
|   |-- jwt_manager.py               # Manages JWT creation, validation, and handling refresh tokens.
|   |-- chat_service.py              # Chat functionality logic.
|   |-- course_service.py            # Course management logic.
|   |-- document_service.py          # Document storage and retrieval logic.
|   |-- user_service.py              # User account management workflows.
|
|-- websocket
|   |-- __init__.py
|   |-- connection_manager.py        # WebSocket communication integrated with RabbitMQ.
|
|-- widgets
    |-- chatWidget.js                # Client-side chat widget for external integration.
```

Entity-Relationship Diagram:
```
GPT
Based on the updated project structure incorporating refresh tokens and JWT management for user authentication and WebSocket communication, here is a detailed entity map outlining each entity, its fields, and the relationships between them:

Entity Map
User Entity
Fields:
UserID: Primary Key, unique identifier for the user.
Username: User's chosen username, unique across the system.
Email: User's email address, unique and used for login.
PasswordHash: Hashed representation of the user's password for secure storage.
UserType: Enum distinguishing between 'Admin', 'InteractiveUser', and 'ExternalUser'.
CreatedAt: Timestamp of when the user account was created.
UpdatedAt: Timestamp of the last update to the user account.

Course Entity
Fields:
CourseID: Primary Key, unique identifier for the course.
Title: Name of the course.
Description: Detailed description of what the course covers.
WidgetToken: A unique token used to securely link chat sessions to this course.
CreatedBy: Foreign Key linking to the User entity (UserID) who created the course.
CreatedAt: Timestamp of when the course was created.
UpdatedAt: Timestamp of the last update to the course.

Document Entity
Fields:
DocumentID: Primary Key, unique identifier for the document.
CourseID: Foreign Key linking to the Course entity (CourseID) the document is associated with.
Filename: Name of the document file.
Filepath: Path or URL where the document file is stored.
FileType: Type of the document (e.g., PDF, TXT).
CreatedAt: Timestamp of when the document was uploaded.
UpdatedAt: Timestamp of the last update to the document.

Chat Session Entity
Fields:
SessionID: Primary Key, unique identifier for the chat session.
ExternalUserID: Foreign Key linking to the User entity (UserID), specifically for External Users.
CourseToken: The WidgetToken from the Course entity used to associate the chat session with a specific course.
IsActive: Boolean indicating whether the chat session is currently active.
StartedAt: Timestamp of when the chat session started.
EndedAt: Timestamp of when the chat session ended, nullable for ongoing sessions.

Message Entity
Fields:
MessageID: Primary Key, unique identifier for the message.
SessionID: Foreign Key linking to the Chat Session entity (SessionID) the message belongs to.
Text: The content of the message.
IsUserMessage: Boolean indicating whether the message was sent by the user or is a system/GPT-generated response.
CreatedAt: Timestamp of when the message was sent.

Refresh Token Entity
Fields:
RefreshTokenID: Primary Key, unique identifier for the refresh token.
UserID: Foreign Key linking to the User entity (UserID) the refresh token is issued to.
Token: The actual refresh token string, unique and securely generated.
ExpiresAt: Timestamp of when the refresh token expires.
CreatedAt: Timestamp of when the refresh token was issued.

Relationships Overview
User to Courses: One-to-Many (An admin or interactive user can create and manage multiple courses).
Course to Documents: One-to-Many (A course can have multiple associated documents for course materials).
Course to Chat Sessions: One-to-Many through WidgetToken (A course can have multiple chat sessions initiated via its unique WidgetToken).
Chat Session to Messages: One-to-Many (A chat session can contain multiple messages between the user and the system/GPT).
User to Refresh Tokens: One-to-Many (A user can have multiple refresh tokens issued, particularly useful if logging in from different devices).
``` 

Database Schema
Based on the entity map and relationships, the database schema can be designed using SQLAlchemy, a popular ORM for Python. The schema will consist of tables representing each entity and their relationships, ensuring data integrity and efficient querying.

```
Database Schema

Users Table
UserID: INT or UUID, Primary Key, Auto-increment (for INT)
Username: VARCHAR(255), Unique, Not Null
Email: VARCHAR(255), Unique, Not Null
PasswordHash: VARCHAR(255), Not Null
UserType: ENUM('Admin', 'InteractiveUser', 'ExternalUser'), Not Null
CreatedAt: TIMESTAMP, Not Null
UpdatedAt: TIMESTAMP, Not Null

Courses Table
CourseID: INT or UUID, Primary Key, Auto-increment (for INT)
Title: VARCHAR(255), Not Null
Description: TEXT, Not Null
WidgetToken: VARCHAR(255), Unique, Not Null
CreatedBy: INT or UUID, Foreign Key (Users.UserID), Not Null
CreatedAt: TIMESTAMP, Not Null
UpdatedAt: TIMESTAMP, Not Null

Documents Table
DocumentID: INT or UUID, Primary Key, Auto-increment (for INT)
CourseID: INT or UUID, Foreign Key (Courses.CourseID), Not Null
Filename: VARCHAR(255), Not Null
Filepath: TEXT, Not Null
FileType: VARCHAR(50), Not Null
CreatedAt: TIMESTAMP, Not Null
UpdatedAt: TIMESTAMP, Not Null

Chat Sessions Table
SessionID: INT or UUID, Primary Key, Auto-increment (for INT)
ExternalUserID: INT or UUID, Foreign Key (Users.UserID), Nullable
CourseToken: VARCHAR(255), Not Null
IsActive: BOOLEAN, Not Null
StartedAt: TIMESTAMP, Not Null
EndedAt: TIMESTAMP, Nullable

Messages Table
MessageID: INT or UUID, Primary Key, Auto-increment (for INT)
SessionID: INT or UUID, Foreign Key (Chat Sessions.SessionID), Not Null
Text: TEXT, Not Null
IsUserMessage: BOOLEAN, Not Null
CreatedAt: TIMESTAMP, Not Null

Refresh Tokens Table
RefreshTokenID: INT or UUID, Primary Key, Auto-increment (for INT)
UserID: INT or UUID, Foreign Key (Users.UserID), Not Null
Token: VARCHAR(255), Unique, Not Null
ExpiresAt: TIMESTAMP, Not Null
CreatedAt: TIMESTAMP, Not Null

Indexes and Constraints
Primary Keys (UserID, CourseID, DocumentID, SessionID, MessageID, RefreshTokenID) ensure uniqueness for each record in their respective tables.
Foreign Keys (CreatedBy in Courses, CourseID in Documents, ExternalUserID and CourseToken in Chat Sessions, SessionID in Messages, UserID in Refresh Tokens) establish relationships between tables. For example, CreatedBy in Courses references UserID in Users.
Unique constraints on Username, Email, WidgetToken, and Token (Refresh Token) prevent duplicates for these critical fields.
Indexes on foreign key columns and frequently queried fields like Email, WidgetToken, and CourseToken improve query performance.
```
