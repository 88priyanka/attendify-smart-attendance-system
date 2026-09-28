from database import create_tables
from auth import create_user

create_tables()

users = [
    ("Admin User", "admin@attendify.com", "Admin@123", "Admin"),
    ("Manager User", "manager@attendify.com", "Manager@123", "Manager"),
    ("Employee User", "employee@attendify.com", "Employee@123", "Employee")
]

for name, email, password, role in users:
    if create_user(name, email, password, role):
        print(f"{role} account created successfully.")
    else:
        print(f"{role} account already exists.")

print("\nTest users setup completed!")