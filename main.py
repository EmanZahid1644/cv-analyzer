import mysql.connector

# Connection
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="ILovePakistan@786",
    database="cv_analysis_system"
)

cursor = conn.cursor(dictionary=True)
print("Connected to database!")

# Example: Fetch all tables
cursor.execute("SHOW TABLES")
for table in cursor.fetchall():
    print(table)
