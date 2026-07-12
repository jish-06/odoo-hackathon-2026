from auth import create_user
from db import init_db

init_db()

create_user("Admin User", "admin@assetflow.com", "admin@123", "admin")
create_user("Asset Manager", "manager@assetflow.com", "manager@123", "asset_manager")
create_user("Dept Head", "head@assetflow.com", "head@123", "dept_head")
create_user("Employee One", "emp@assetflow.com", "emp@123", "employee")

print("Setup complete!")