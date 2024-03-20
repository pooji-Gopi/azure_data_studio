from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pyodbc
import datetime
import jwt

app = FastAPI()

# Database connection details
server = '216.48.190.212'
database = 'CN2_SimpleSolve_Prd'
username = 'sa'
password = 'Welcome@123$'

# Database connection string
conn_str = f"DRIVER=ODBC Driver 17 for SQL Server;SERVER={server};DATABASE={database};UID={username};PWD={password}"

# Database connection
conn = pyodbc.connect(conn_str)

class User(BaseModel):
    username: str
    password: str

@app.get("/users/")
async def get_users():
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tbluser")
    users = []
    for row in cursor.fetchall():
        user_data = {
            "UserID": row.UserID,
            "Name": row.Name,
            "Email": row.Email,
            "Role": row.Role,
            "UserType": row.UserType,
            "Status": row.Status,
            "Notes": row.Notes,
            "BranchName": row.BranchName,
            "Phone": row.Phone,
            "TimeZone": row.TimeZone,
            "Password": row.Password,
            "Token": row.Token,
            "TokenExpiry": row.TokenExpiry,
            "TaskBenchUserID": row.TaskBenchUserID,
            "CreatedOn": row.CreatedOn,
            "UpdatedOn": row.UpdatedOn
        }
        users.append(user_data)
    return users

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"

@app.post("/login/")
async def login(user: User):
    # Check if the provided username and password are correct
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tbluser WHERE UserName = ? AND Password = ?", (user.username, user.password))
    row = cursor.fetchone()

    if row is None:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    # If the credentials are valid, fetch user data
    user_data = {
        "UserID": row.UserID,
        "Name": row.Name,
        "Email": row.Email,
        "Role": row.Role,
        "UserType": row.UserType,
        "Status": row.Status,
        "Notes": row.Notes,
        "BranchName": row.BranchName,
        "Phone": row.Phone,
        "TimeZone": row.TimeZone,
        "Password": row.Password,
        "TaskBenchUserID": row.TaskBenchUserID,
        "CreatedOn": row.CreatedOn,
        "UpdatedOn": row.UpdatedOn
    }

    # Generate a new token
    token_data = {
        "sub": str(row.UserID),
        "username": user.username,
        "UserType": row.UserType,
        "Role": row.Role,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=1)  # Token expiry set to 1 day
    }
    token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)

    # Update the token and token expiry in the user_data dictionary
    user_data["Token"] = token
    user_data["TokenExpiry"] = token_data["exp"]

    # Update the token and token expiry in the database
    cursor.execute("UPDATE tbluser SET Token = ?, TokenExpiry = ? WHERE UserID = ?", (token, token_data["exp"], row.UserID))
    conn.commit()

    return user_data
