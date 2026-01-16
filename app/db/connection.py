import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="ILovePakistan@786",
    database="cv_analysis_system"
)
cursor = conn.cursor(dictionary=True)
print("Connected to database!")
