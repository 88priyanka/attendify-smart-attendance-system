import streamlit as st
import pandas as pd
from datetime import datetime

from database import get_connection, create_tables
from auth import login_user
from attendance import (
    mark_attendance,
    logout_user,
    get_today_attendance
)
from employee_management import (
    get_departments,
    add_employee,
    get_all_employees,
    update_employee,
    deactivate_employee
)
from anomaly_detection import (
    detect_employee_anomalies
)
from analytics import (
    get_attendance_summary,
    get_daily_attendance,
    get_department_attendance,
    get_attendance_data
)
from alerts import (
    get_all_alerts,
    get_unresolved_alerts,
    resolve_alert,
    get_unresolved_alert_count
)
from leave_management import (
    create_leave_request,
    get_employee_leave_requests,
    get_all_leave_requests,
    update_leave_status
)


# =====================================================
# PAGE CONFIGURATION
# =====================================================

st.set_page_config(
    page_title="Attendify",
    page_icon="🕒",
    layout="wide"
)


# =====================================================
# DATABASE INITIALIZATION
# =====================================================

create_tables()


# =====================================================
# SESSION STATE
# =====================================================

if "user" not in st.session_state:
    st.session_state.user = None


# =====================================================
# LOGIN PAGE
# =====================================================

if st.session_state.user is None:

    st.title("🕒 Attendify")

    st.subheader(
        "Smart Employee Attendance & Anomaly Detection System"
    )

    st.divider()

    col1, col2 = st.columns([1, 1])

    with col1:

        st.header("🔐 Login")

        email = st.text_input(
            "Email"
        )

        password = st.text_input(
            "Password",
            type="password"
        )

        if st.button(
            "Login",
            use_container_width=True
        ):

            if not email or not password:

                st.warning(
                    "Please enter email and password."
                )

            else:

                user = login_user(
                    email,
                    password
                )

                if user:

                    st.session_state.user = user

                    st.success(
                        "Login successful!"
                    )

                    st.rerun()

                else:

                    st.error(
                        "Invalid email or password."
                    )

    with col2:

        st.header("🏢 Attendify")

        st.write(
            """
            Attendify is a smart employee attendance
            management system designed for modern
            workplaces.
            """
        )

        st.write("### Features")

        st.write(
            """
            ✅ Employee Attendance

            ✅ Login & Logout Tracking

            ✅ Working Hours Calculation

            ✅ Employee Management

            ✅ Leave Management

            ✅ Attendance Analytics

            ✅ Anomaly Detection

            ✅ Automated Alerts
            """
        )

    st.stop()


# =====================================================
# LOGGED-IN USER
# =====================================================

user = st.session_state.user


# =====================================================
# SIDEBAR
# =====================================================

with st.sidebar:

    st.title("🕒 Attendify")

    st.caption(
        "Smart Attendance Management"
    )

    st.divider()

    st.write(
        f"👋 Welcome, **{user['name']}**"
    )

    st.write(
        f"👤 Role: **{user['role']}**"
    )
    # -------------------------------------------------
    # ALERT NOTIFICATION
    # -------------------------------------------------

    if user["role"] != "Employee":

        alert_count = get_unresolved_alert_count()

        if alert_count > 0:

            st.warning(
                f"🔔 {alert_count} unresolved alert(s)"
            )

    # -------------------------------------------------
    # NAVIGATION
    # -------------------------------------------------

    if user["role"] == "Employee":

        employee_pages = [
            "My Dashboard",
            "My Attendance",
            "Leave Management"
        ]

        if "page" not in st.session_state:

            st.session_state["page"] = "My Dashboard"

        page = st.radio(
            "Navigation",
            employee_pages,
            index=employee_pages.index(
                st.session_state["page"]
            )
        )

        st.session_state["page"] = page

    else:

        company_pages = [
            "Company Dashboard",
            "Attendance",
            "Employee Management",
            "Leave Requests",
            "Analytics",
            "Anomaly Detection",
            "Alerts"
        ]

        if "page" not in st.session_state:

            st.session_state["page"] = "Company Dashboard"

        page = st.radio(
            "Navigation",
            company_pages,
            index=company_pages.index(
                st.session_state["page"]
            )
        )

        st.session_state["page"] = page

    st.divider()
    st.caption("Account")

    # -------------------------------------------------
    # LOGOUT
    # -------------------------------------------------

    if st.button(
        "🚪 Logout",
        use_container_width=True
    ):

        st.session_state.user = None
        st.session_state.pop("page", None)

        st.rerun()

# =====================================================
# EMPLOYEE DASHBOARD
# =====================================================

if user["role"] == "Employee" and page == "My Dashboard":

    st.title("👤 Employee Dashboard")

    st.write(
        f"Welcome back, **{user['name']}**!"
    )

    st.divider()

    # -------------------------------------------------
    # QUICK ACTIONS
    # -------------------------------------------------

    st.subheader("⚡ Quick Actions")

    col1, col2 = st.columns(2)

    with col1:

        if st.button(
            "🕐 View My Attendance",
            use_container_width=True
        ):

            st.session_state["page"] = "My Attendance"
            st.rerun()

    with col2:

        if st.button(
            "🏖️ Manage Leave",
            use_container_width=True
        ):

            st.session_state["page"] = "Leave Management"
            st.rerun()

    # -------------------------------------------------
    # EMPLOYEE INFORMATION
    # -------------------------------------------------

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
    users.name,
    users.email,
    departments.department_name
FROM users
LEFT JOIN departments
ON users.department_id = departments.id
WHERE users.id = ?
    """, (user["id"],))

    employee_info = cursor.fetchone()

    connection.close()

    if employee_info:

        employee_name = employee_info[0]
        employee_email = employee_info[1]
        department_name = employee_info[2] or "Not Assigned"

    else:

        employee_name = user["name"]
        employee_email = "-"
        department_name = "Not Assigned"


    # -------------------------------------------------
    # EMPLOYEE PROFILE
    # -------------------------------------------------

    
    st.subheader("👤 My Profile")

    profile_col1, profile_col2, profile_col3 = st.columns(3)

    with profile_col1:
        st.metric("👤 Employee", user["name"])

    with profile_col2:
        st.metric("📧 Email", user["email"])

    with profile_col3:
        st.metric("🏢 Department", department_name)


    # -------------------------------------------------
    # TODAY'S ATTENDANCE
    # -------------------------------------------------

    connection = get_connection()
    cursor = connection.cursor()

    today = datetime.now().strftime(
        "%Y-%m-%d"
    )

    cursor.execute("""
        SELECT
            attendance_date,
            login_time,
            logout_time,
            status,
            working_hours
        FROM attendance
        WHERE user_id = ?
        AND attendance_date = ?
    """, (
        user["id"],
        today
    ))

    today_record = cursor.fetchone()

    connection.close()


    # -------------------------------------------------
    # ATTENDANCE HISTORY SUMMARY
    # -------------------------------------------------

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            COUNT(*),
            SUM(
                CASE
                    WHEN status = 'Present'
                    THEN 1
                    ELSE 0
                END
            ),
            SUM(
                CASE
                    WHEN status = 'Late'
                    THEN 1
                    ELSE 0
                END
            ),
            AVG(
                CASE
                    WHEN working_hours IS NOT NULL
                    THEN working_hours
                    ELSE 0
                END
            )
        FROM attendance
        WHERE user_id = ?
    """, (user["id"],))

    attendance_summary = cursor.fetchone()

    connection.close()


    total_records = (
        attendance_summary[0]
        if attendance_summary and attendance_summary[0]
        else 0
    )

    present_count = (
        attendance_summary[1]
        if attendance_summary and attendance_summary[1]
        else 0
    )

    late_count = (
        attendance_summary[2]
        if attendance_summary and attendance_summary[2]
        else 0
    )

    average_hours = (
        attendance_summary[3]
        if attendance_summary and attendance_summary[3]
        else 0
    )


    # -------------------------------------------------
    # LEAVE SUMMARY
    # -------------------------------------------------

    leave_requests = get_employee_leave_requests(
        user["id"]
    )

    total_leave_requests = len(
        leave_requests
    )

    approved_leave = sum(
        1
        for request in leave_requests
        if request[5] == "Approved"
    )

    pending_leave = sum(
        1
        for request in leave_requests
        if request[5] == "Pending"
    )


    # -------------------------------------------------
    # PERSONAL SUMMARY
    # -------------------------------------------------

    st.subheader(
        "📊 My Attendance Summary"
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "📋 Total Records",
            total_records
        )

    with col2:

        st.metric(
            "🟢 Present",
            present_count
        )

    with col3:

        st.metric(
            "🟠 Late",
            late_count
        )

    with col4:

        st.metric(
            "⏱️ Avg Working Hours",
            f"{float(average_hours):.2f}"
        )

    attendance_percentage = (
        ((present_count + late_count) / total_records) * 100
        if total_records > 0
        else 0
    )

    st.metric(
        "📈 Attendance Percentage",
        f"{attendance_percentage:.1f}%"
    )

    st.divider()

        # -------------------------------------------------
    # LEAVE SUMMARY
    # -------------------------------------------------

    st.subheader(
        "🏖️ Leave Overview"
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "📝 Total Requests",
            total_leave_requests
        )

    with col2:

        st.metric(
            "✅ Approved",
            approved_leave
        )

    with col3:

        st.metric(
            "⏳ Pending",
            pending_leave
        )

    with col4:

        rejected_leave = total_leave_requests - approved_leave - pending_leave

        st.metric(
            "❌ Rejected",
            rejected_leave
        )

    st.divider()


    # -------------------------------------------------
    # TODAY'S ATTENDANCE
    # -------------------------------------------------

    st.subheader(
        "🕐 Today's Attendance"
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        status = (
            today_record[3]
            if today_record
            else "Not Marked"
        )

        st.metric(
            "📌 Status",
            status
        )

    with col2:

        login_time = (
            today_record[1]
            if today_record
            else "-"
        )

        if login_time:

            login_time = str(
                login_time
            )

            if " " in login_time:

                login_time = (
                    login_time.split(" ")[-1]
                )

        st.metric(
            "🟢 Login",
            login_time
        )

    with col3:

        logout_time = (
            today_record[2]
            if today_record
            else "-"
        )

        if logout_time:

            logout_time = str(
                logout_time
            )

            if " " in logout_time:

                logout_time = (
                    logout_time.split(" ")[-1]
                )

        st.metric(
            "🔴 Logout",
            logout_time
        )

    with col4:

        working_hours = (
            today_record[4]
            if today_record
            and today_record[4] is not None
            else 0
        )

        st.metric(
            "⏱️ Today Hours",
            f"{float(working_hours):.2f}"
        )


    st.divider()


    # -------------------------------------------------
    # ATTENDANCE ACTIONS
    # -------------------------------------------------

    st.subheader(
        "🕐 Attendance Actions"
    )

    already_logged_in = False
    already_logged_out = False

    if today_record:

        if today_record[1]:

            already_logged_in = True

        if today_record[2]:

            already_logged_out = True


    col1, col2 = st.columns(2)


    # -------------------------------------------------
    # MARK ATTENDANCE
    # -------------------------------------------------

    with col1:

        if already_logged_in:

            st.button(
                "✅ Attendance Marked",
                disabled=True,
                use_container_width=True
            )

        else:

            if st.button(
                "🟢 Mark Attendance",
                use_container_width=True
            ):

                success = mark_attendance(
                    user["id"]
                )

                if success:

                    detect_employee_anomalies(
                        user["id"]
                    )

                    st.success(
                        "Attendance marked successfully!"
                    )

                    st.rerun()

                else:

                    st.warning(
                        "Today's attendance is already marked."
                    )


    # -------------------------------------------------
    # LOGOUT ATTENDANCE
    # -------------------------------------------------

    with col2:

        if not already_logged_in:

            st.button(
                "🔒 Logout Attendance",
                disabled=True,
                use_container_width=True
            )

        elif already_logged_out:

            st.button(
                "✅ Logout Completed",
                disabled=True,
                use_container_width=True
            )

            st.success(
                "✅ Today's attendance is completed."
            )

        else:

            if st.button(
                "🔴 Logout Attendance",
                use_container_width=True
            ):

                success = logout_user(
                    user["id"]
                )

                if success:

                    detect_employee_anomalies(
                        user["id"]
                    )

                    st.success(
                        "Logout recorded successfully!"
                    )

                    st.rerun()

                else:

                    st.warning(
                        "No active attendance record found."
                    )
    # -------------------------------------------------
    # RECENT ATTENDANCE
    # -------------------------------------------------

    st.divider()

    st.subheader(
        "📋 Recent Attendance"
    )

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            attendance_date,
            login_time,
            logout_time,
            status,
            working_hours
        FROM attendance
        WHERE user_id = ?
        ORDER BY attendance_date DESC
        LIMIT 5
    """, (user["id"],))

    recent_records = cursor.fetchall()

    connection.close()

    if recent_records:

        recent_df = pd.DataFrame(
            recent_records,
            columns=[
                "Date",
                "Login Time",
                "Logout Time",
                "Status",
                "Working Hours"
            ]
        )

        st.dataframe(
            recent_df,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info(
            "📭 No recent attendance records found."
        )
# =====================================================
# EMPLOYEE ATTENDANCE
# =====================================================

elif user["role"] == "Employee" and page == "My Attendance":

    st.title("📅 My Attendance")
    st.write("View your complete attendance history.")
    st.divider()

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            attendance_date,
            login_time,
            logout_time,
            status,
            working_hours
        FROM attendance
        WHERE user_id = ?
        ORDER BY attendance_date DESC
    """, (user["id"],))

    attendance_records = cursor.fetchall()

    connection.close()

    if attendance_records:

        attendance_df = pd.DataFrame(
            attendance_records,
            columns=[
                "Date",
                "Login Time",
                "Logout Time",
                "Status",
                "Working Hours"
            ]
        )

        # Attendance Summary
        total_records = len(attendance_df)

        present_count = len(
            attendance_df[
                attendance_df["Status"].astype(str).str.lower() == "present"
            ]
        )

        late_count = len(
            attendance_df[
                attendance_df["Status"].astype(str).str.lower() == "late"
            ]
        )

        avg_hours = attendance_df["Working Hours"].mean()

        st.subheader("📊 Attendance Summary")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("📋 Total Records", total_records)

        with col2:
            st.metric("🟢 Present", present_count)

        with col3:
            st.metric("🟠 Late", late_count)

        with col4:
            st.metric(
                "⏱️ Avg Hours",
                f"{avg_hours:.2f}"
            )

        st.divider()

        st.subheader("📋 Attendance History")

        st.dataframe(
            attendance_df,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info(
            "📭 No attendance records found."
        )

# =====================================================
# EMPLOYEE LEAVE MANAGEMENT
# =====================================================

elif user["role"] == "Employee" and page == "Leave Management":

    st.title("🏖️ Leave Management")
    st.write("Apply for leave and track your leave requests.")
    st.divider()

    st.subheader("📝 Apply for Leave")

    with st.form("leave_application_form"):

        leave_type = st.selectbox(
            "Leave Type",
            [
                "Casual Leave",
                "Sick Leave",
                "Emergency Leave",
                "Personal Leave"
            ]
        )

        col1, col2 = st.columns(2)

        with col1:
            start_date = st.date_input(
                "📅 Start Date"
            )

        with col2:
            end_date = st.date_input(
                "📅 End Date"
            )

        reason = st.text_area(
            "📝 Reason",
            placeholder="Enter the reason for your leave..."
        )

        submit_leave = st.form_submit_button(
            "📤 Submit Leave Request",
            use_container_width=True
        )

        if submit_leave:

            if end_date < start_date:

                st.error(
                    "❌ End date cannot be before start date."
                )

            elif not reason.strip():

                st.error(
                    "❌ Please enter a reason for the leave."
                )

            else:

                connection = get_connection()
                cursor = connection.cursor()

                cursor.execute("""
                    INSERT INTO leave_requests
                    (
                        user_id,
                        leave_type,
                        start_date,
                        end_date,
                        reason,
                        status
                    )
                    VALUES (?, ?, ?, ?, ?, 'Pending')
                """, (
                    user["id"],
                    leave_type,
                    start_date,
                    end_date,
                    reason
                ))

                connection.commit()
                connection.close()

                st.success(
                    "✅ Leave request submitted successfully!"
                )
        st.divider()

    st.subheader("📋 My Leave Requests")

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            leave_type,
            start_date,
            end_date,
            reason,
            status
        FROM leave_requests
        WHERE user_id = ?
        ORDER BY id DESC
    """, (user["id"],))

    leave_records = cursor.fetchall()

    connection.close()

    # Leave Summary

    total_requests = len(leave_records)

    approved_count = sum(
        1 for record in leave_records
        if str(record[4]).lower() == "approved"
    )

    pending_count = sum(
        1 for record in leave_records
        if str(record[4]).lower() == "pending"
    )

    rejected_count = sum(
        1 for record in leave_records
        if str(record[4]).lower() == "rejected"
    )

    st.subheader("📊 Leave Summary")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("📋 Total Requests", total_requests)

    with col2:
        st.metric("✅ Approved", approved_count)

    with col3:
        st.metric("⏳ Pending", pending_count)

    with col4:
        st.metric("❌ Rejected", rejected_count)

    st.divider()

    if leave_records:

        leave_df = pd.DataFrame(
            leave_records,
            columns=[
                "Leave Type",
                "Start Date",
                "End Date",
                "Reason",
                "Status"
            ]
        )

        st.dataframe(
            leave_df,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info(
            "📭 No leave requests found."
        )

# =====================================================
# COMPANY DASHBOARD
# =====================================================

elif user["role"] in ["Admin", "Manager"] and page == "Company Dashboard":

    st.title("🕒 Attendify — Company Dashboard")

    st.caption(
        "Smart Employee Attendance & Anomaly Detection System"
    )

    st.write(
        "Overview of employee attendance and workplace activity."
    )

    st.divider()

    # -------------------------------------------------
    # DASHBOARD SUMMARY
    # -------------------------------------------------

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM users
        WHERE role = 'Employee'
    """)

    total_employees = cursor.fetchone()[0]

    today = datetime.now().strftime("%Y-%m-%d")

    cursor.execute("""
        SELECT COUNT(*)
        FROM attendance
        WHERE attendance_date = ?
    """, (today,))

    present_today = cursor.fetchone()[0]

    connection.close()

    active_alerts = get_unresolved_alert_count()
    absent_today = max(total_employees - present_today, 0)

    # -------------------------------------------------
    # TODAY'S SUMMARY
    # -------------------------------------------------
    st.subheader("📊 Today's Overview")
    st.caption("Quick summary of the company's current attendance status.")

    st.divider()
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("👥 Total Employees", total_employees)

    with col2:
        st.metric("🟢 Present Today", present_today)

    with col3:
        st.metric("🔴 Absent Today", absent_today)

    with col4:
        st.metric("⚠️ Active Alerts", active_alerts)

    st.divider()

    # -------------------------------------------------
    # OVERALL ATTENDANCE SUMMARY
    # -------------------------------------------------

    summary = get_attendance_summary()

    total_records = summary[0]
    present_count = summary[1]
    late_count = summary[2]
    average_hours = summary[3]
    
    st.divider()

    st.subheader("📈 Overall Attendance")
    st.caption("Attendance statistics across the company.")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("📋 Attendance Records", total_records)

    with col2:
        st.metric("🟢 Present", present_count)

    with col3:
        st.metric("🟠 Late", late_count)

    with col4:
        st.metric("⏱️ Avg Working Hours", f"{average_hours:.2f}")

    st.divider()

    # -------------------------------------------------
    # DEPARTMENT-WISE ATTENDANCE
    # -------------------------------------------------
    st.divider()

    st.subheader("🏢 Department-wise Attendance")
    st.caption(
        "Compare attendance activity across departments."
    )
    
    department_data = get_department_attendance()

    if not department_data.empty:

        # Show department attendance table
        st.dataframe(
            department_data,
            use_container_width=True,
            hide_index=True
        )

        st.subheader(
            "📊 Attendance by Department"
        )

        st.bar_chart(
            department_data.set_index(
                "department_name"
            )
        )

    else:

        st.info(
            "📭 No department attendance data available."
        )

        # -------------------------------------------------
    # ALERT STATUS
    # -------------------------------------------------

    if active_alerts > 0:

        st.warning(
            f"🔔 There are {active_alerts} unresolved attendance alerts."
        )

    else:

        st.success(
            "✅ No unresolved attendance alerts."
        )

    st.divider()

    # -------------------------------------------------
    # QUICK ACTIONS
    # -------------------------------------------------

    st.subheader("⚡ Quick Actions")

    st.caption(
        "Quickly access the most frequently used management features."
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        if st.button(
            "👥 Employee Management",
            use_container_width=True
        ):

            st.session_state["page"] = "Employee Management"
            st.rerun()

    with col2:

        if st.button(
            "📊 Attendance",
            use_container_width=True
        ):

            st.session_state["page"] = "Attendance"
            st.rerun()

    with col3:

        if st.button(
            "📝 Leave Requests",
            use_container_width=True
        ):

            st.session_state["page"] = "Leave Requests"
            st.rerun()

    with col4:

        if st.button(
            "⚠️ Attendance Alerts",
            use_container_width=True
        ):

            st.session_state["page"] = "Alerts"
            st.rerun()
# =====================================================
# COMPANY ATTENDANCE
# =====================================================

elif user["role"] in ["Admin", "Manager"] and page == "Attendance":

    st.title("📊 Attendance Management")

    st.write(
        "View and filter employee attendance records."
    )

    st.divider()

    # -------------------------------------------------
    # GET ALL ATTENDANCE RECORDS
    # -------------------------------------------------

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            attendance.attendance_date,
            users.name,
            users.email,
            users.role,
            attendance.login_time,
            attendance.logout_time,
            attendance.status,
            attendance.working_hours
        FROM attendance
        JOIN users
        ON attendance.user_id = users.id
        ORDER BY attendance.attendance_date DESC
    """)

    attendance_data = cursor.fetchall()

    connection.close()

    if attendance_data:

        df = pd.DataFrame(
            attendance_data,
            columns=[
                "Date",
                "Employee",
                "Email",
                "Role",
                "Login Time",
                "Logout Time",
                "Status",
                "Working Hours"
            ]
        )

        # -------------------------------------------------
        # ATTENDANCE FILTERS
        # -------------------------------------------------

        st.subheader("🔎 Attendance Filters")

        filter_col1, filter_col2, filter_col3 = st.columns(3)

        with filter_col1:
            employee_filter = st.selectbox(
                "👤 Employee",
                ["All"] + sorted(
                    df["Employee"].dropna().unique().tolist()
                )
            )

        with filter_col2:
            status_filter = st.selectbox(
                "📌 Status",
                ["All", "Present", "Late"]
            )

        with filter_col3:
            search_text = st.text_input(
                "🔍 Search",
                placeholder="Employee or email..."
            )

        filtered_df = df.copy()

        if employee_filter != "All":
            filtered_df = filtered_df[
                filtered_df["Employee"] == employee_filter
            ]

        if status_filter != "All":
            filtered_df = filtered_df[
                filtered_df["Status"].astype(str).str.lower()
                == status_filter.lower()
            ]

        if search_text:
            search_text = search_text.lower().strip()
            filtered_df = filtered_df[
                filtered_df["Employee"].astype(str).str.lower().str.contains(
                    search_text, na=False
                )
                |
                filtered_df["Email"].astype(str).str.lower().str.contains(
                    search_text, na=False
                )
            ]

        st.divider()
        st.subheader("📌 Attendance Summary")

        total_records = len(filtered_df)
        present_count = len(
            filtered_df[
                filtered_df["Status"].astype(str).str.lower() == "present"
            ]
        )
        late_count = len(
            filtered_df[
                filtered_df["Status"].astype(str).str.lower() == "late"
            ]
        )

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("👥 Total Records", total_records)
        with col2:
            st.metric("🟢 Present", present_count)
        with col3:
            st.metric("🟠 Late", late_count)

        st.divider()
        st.subheader("📋 Employee Attendance")

        if not filtered_df.empty:
            st.dataframe(
                filtered_df,
                use_container_width=True,
                hide_index=True
            )

            st.divider()
            st.subheader("📥 Attendance Report")

            csv_data = filtered_df.to_csv(index=False).encode("utf-8")

            st.download_button(
                label="⬇️ Download Attendance Report",
                data=csv_data,
                file_name="attendance_report.csv",
                mime="text/csv",
                use_container_width=True
            )

        else:
            st.info(
                "📭 No attendance records match the selected filters."
            )

    else:
        st.info(
            "📭 No attendance records found."
        )

# EMPLOYEE MANAGEMENT
# =====================================================

elif user["role"] in ["Admin", "Manager"] and page == "Employee Management":

    st.title("👥 Employee Management")

    st.write(
        "Add and manage company employees."
    )

    st.divider()

    # =====================================================
    # ADD EMPLOYEE
    # =====================================================

    st.subheader("➕ Add Employee")

    departments = get_departments()

    department_names = [
        department[1]
        for department in departments
    ]

    with st.form("employee_form"):

        name = st.text_input(
            "Employee Name"
        )

        email = st.text_input(
            "Employee Email"
        )

        password = st.text_input(
            "Temporary Password",
            type="password"
        )

        selected_department = st.selectbox(
            "Department",
            department_names
        )

        add_employee_button = st.form_submit_button(
            "Add Employee",
            use_container_width=True
        )

        if add_employee_button:

            if not name or not email or not password:

                st.warning(
                    "Please fill all required fields."
                )

            else:

                department_id = next(
                    department[0]
                    for department in departments
                    if department[1] == selected_department
                )

                success = add_employee(
                    name,
                    email,
                    password,
                    department_id
                )

                if success:

                    st.success(
                        "Employee added successfully!"
                    )

                    st.rerun()

                else:

                    st.error(
                        "Email already exists."
                    )

    st.divider()

    # =====================================================
    # EMPLOYEE LIST
    # =====================================================

    st.subheader("📋 Employee List")

    # -------------------------------------------------
    # EMPLOYEE SEARCH & FILTER
    # -------------------------------------------------

    search_col1, search_col2, search_col3 = st.columns(3)

    with search_col1:

        search_text = st.text_input(
            "🔎 Search Employee",
            placeholder="Name or email..."
        )

    with search_col2:

        department_filter = st.selectbox(
            "🏢 Department",
            ["All"] + department_names
        )

    with search_col3:

        status_filter = st.selectbox(
            "📌 Status",
            ["All", "Active", "Inactive"]
        )

    # -------------------------------------------------
    # GET EMPLOYEES
    # -------------------------------------------------

    employees = get_all_employees()

    filtered_employees = []

    for employee in employees:

        employee_id = employee[0]
        employee_name = employee[1]
        employee_email = employee[2]
        employee_department = employee[3]
        employee_status = employee[5]

        if search_text:

            search_value = search_text.lower()

            if (
                search_value not in employee_name.lower()
                and search_value not in employee_email.lower()
            ):
                continue

        if (
            department_filter != "All"
            and employee_department != department_filter
        ):
            continue

        if status_filter != "All":

            if (
                status_filter == "Active"
                and employee_status != 1
            ):
                continue

            if (
                status_filter == "Inactive"
                and employee_status != 0
            ):
                continue

        filtered_employees.append(employee)

    # -------------------------------------------------
    # EMPLOYEE TABLE
    # -------------------------------------------------

    if filtered_employees:

        employee_df = pd.DataFrame(
            filtered_employees,
            columns=[
                "ID",
                "Name",
                "Email",
                "Department",
                "Created At",
                "Active"
            ]
        )

        employee_df["Status"] = employee_df["Active"].apply(
            lambda x: "🟢 Active" if x == 1 else "🔴 Inactive"
        )

        employee_df.drop(
            columns=["Active"],
            inplace=True
        )

        st.dataframe(
            employee_df,
            use_container_width=True,
            hide_index=True
        )

        st.divider()

        # -------------------------------------------------
        # EDIT EMPLOYEE
        # -------------------------------------------------

        st.subheader("✏️ Edit Employee")

        employee_options = {
            f"{employee[1]} ({employee[2]})": employee
            for employee in filtered_employees
        }

        selected_employee_label = st.selectbox(
            "Select Employee",
            list(employee_options.keys()),
            key="edit_employee"
        )

        selected_employee = employee_options[
            selected_employee_label
        ]

        selected_employee_id = selected_employee[0]
        current_name = selected_employee[1]
        current_email = selected_employee[2]
        current_department = selected_employee[3]

        edit_col1, edit_col2 = st.columns(2)

        with edit_col1:

            edit_name = st.text_input(
                "Employee Name",
                value=current_name,
                key="edit_name"
            )

            edit_email = st.text_input(
                "Employee Email",
                value=current_email,
                key="edit_email"
            )

        with edit_col2:

            edit_department = st.selectbox(
                "Department",
                department_names,
                index=(
                    department_names.index(current_department)
                    if current_department in department_names
                    else 0
                ),
                key="edit_department"
            )

        if st.button(
            "💾 Update Employee",
            use_container_width=True
        ):

            if (
                not edit_name.strip()
                or not edit_email.strip()
            ):

                st.warning(
                    "Please fill all required fields."
                )

            else:

                department_id = next(
                    department[0]
                    for department in departments
                    if department[1] == edit_department
                )

                success = update_employee(
                    selected_employee_id,
                    edit_name.strip(),
                    edit_email.strip(),
                    department_id
                )

                if success:

                    st.success(
                        "✅ Employee updated successfully!"
                    )

                    st.rerun()

        st.divider()

        # -------------------------------------------------
        # DEACTIVATE EMPLOYEE
        # -------------------------------------------------

        st.subheader("🚫 Deactivate Employee")

        active_employee_options = {
            label: employee
            for label, employee in employee_options.items()
            if employee[5] == 1
        }

        if active_employee_options:

            deactivate_employee_label = st.selectbox(
                "Select Employee to Deactivate",
                list(active_employee_options.keys()),
                key="deactivate_employee"
            )

            deactivate_employee_data = active_employee_options[
                deactivate_employee_label
            ]

            deactivate_employee_id = deactivate_employee_data[0]

            if st.button(
                "🚫 Deactivate Employee",
                use_container_width=True
            ):

                success = deactivate_employee(
                    deactivate_employee_id
                )

                if success:

                    st.success(
                        "✅ Employee deactivated successfully!"
                    )

                    st.rerun()

        else:

            st.info(
                "ℹ️ No active employees available to deactivate."
            )

    else:

        st.info(
            "📭 No employees found."
        )

# LEAVE REQUESTS
# =====================================================

elif user["role"] in ["Admin", "Manager"] and page == "Leave Requests":

    st.title("🏖️ Leave Requests")
    st.write("Review and manage employee leave requests.")
    st.divider()

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            leave_requests.id,
            users.name,
            users.email,
            leave_requests.leave_type,
            leave_requests.start_date,
            leave_requests.end_date,
            leave_requests.reason,
            leave_requests.status
        FROM leave_requests
        JOIN users ON leave_requests.user_id = users.id
        ORDER BY leave_requests.id DESC
    """)

    leave_requests = cursor.fetchall()

    connection.close()

    if leave_requests:

        leave_df = pd.DataFrame(
            leave_requests,
            columns=[
                "ID",
                "Employee",
                "Email",
                "Leave Type",
                "Start Date",
                "End Date",
                "Reason",
                "Status"
            ]
        )

        st.subheader("📋 All Leave Requests")

        st.dataframe(
            leave_df,
            use_container_width=True,
            hide_index=True
        )

        st.divider()

        st.subheader("⚙️ Manage Leave Requests")

        for request in leave_requests:

            request_id = request[0]
            employee_name = request[1]
            leave_type = request[3]
            start_date = request[4]
            end_date = request[5]
            reason = request[6]
            status = request[7]

            st.write(
                f"👤 **{employee_name}** | "
                f"🏖️ {leave_type} | "
                f"📅 {start_date} → {end_date}"
            )

            st.write(
                f"📝 Reason: {reason}"
            )

            st.write(
                f"📌 Status: **{status}**"
            )

            if status == "Pending":

                col1, col2 = st.columns(2)

                with col1:

                    if st.button(
                        "✅ Approve",
                        key=f"approve_{request_id}",
                        use_container_width=True
                    ):

                        connection = get_connection()
                        cursor = connection.cursor()

                        cursor.execute("""
                            UPDATE leave_requests
                            SET status = 'Approved'
                            WHERE id = ?
                        """, (request_id,))

                        connection.commit()
                        connection.close()

                        st.success(
                            "✅ Leave request approved!"
                        )

                        st.rerun()

                with col2:

                    if st.button(
                        "❌ Reject",
                        key=f"reject_{request_id}",
                        use_container_width=True
                    ):

                        connection = get_connection()
                        cursor = connection.cursor()

                        cursor.execute("""
                            UPDATE leave_requests
                            SET status = 'Rejected'
                            WHERE id = ?
                        """, (request_id,))

                        connection.commit()
                        connection.close()

                        st.warning(
                            "❌ Leave request rejected!"
                        )

                        st.rerun()

            st.divider()

    else:

        st.info(
            "📭 No leave requests found."
        )

# =====================================================
# ANALYTICS
# =====================================================

elif user["role"] in ["Admin", "Manager"] and page == "Analytics":

    st.title("📈 Attendance Analytics")

    st.write(
        "Analyze employee attendance and working-hour patterns."
    )

    st.divider()


    summary = get_attendance_summary()

    total_records = summary[0]
    present_count = summary[1]
    late_count = summary[2]
    average_hours = summary[3]


    col1, col2, col3, col4 = st.columns(4)


    with col1:

        st.metric(
            "📋 Total Records",
            total_records
        )


    with col2:

        st.metric(
            "🟢 Present",
            present_count
        )


    with col3:

        st.metric(
            "🟠 Late",
            late_count
        )


    with col4:

        st.metric(
            "⏱️ Average Hours",
            f"{average_hours:.2f}"
        )


    st.divider()


    st.subheader(
        "📅 Daily Attendance"
    )


    daily_data = get_daily_attendance()


    if not daily_data.empty:

        st.dataframe(
            daily_data,
            use_container_width=True,
            hide_index=True
        )

        st.line_chart(
            daily_data.set_index(
                "attendance_date"
            )
        )


    st.subheader(
        "🏢 Department Attendance"
    )


    department_data = get_department_attendance()


    if not department_data.empty:

        st.dataframe(
            department_data,
            use_container_width=True,
            hide_index=True
        )

        st.bar_chart(
            department_data.set_index(
                "department_name"
            )
        )


    st.subheader(
        "⏱️ Employee Working Hours"
    )


    attendance_data = get_attendance_data()


    if not attendance_data.empty:

        st.dataframe(
            attendance_data,
            use_container_width=True,
            hide_index=True
        )

        if (
            "name" in attendance_data.columns
            and
            "working_hours" in attendance_data.columns
        ):

            employee_hours = (
                attendance_data
                .groupby("name")["working_hours"]
                .mean()
                .reset_index()
            )

            st.bar_chart(
                employee_hours.set_index("name")
            )


# =====================================================
# ANOMALY DETECTION
# =====================================================

elif user["role"] in ["Admin", "Manager"] and page == "Anomaly Detection":

    st.title("🚨 Anomaly Detection")

    st.write(
        "Detect unusual employee attendance patterns."
    )

    st.divider()


    employees = get_all_employees()

    if employees:

        all_anomalies = []
        employee_anomalies = []


        # -------------------------------------------------
        # SCAN ALL EMPLOYEES
        # -------------------------------------------------

        for employee in employees:

            employee_id = employee[0]
            employee_name = employee[1]
            employee_email = employee[2]

            anomalies = detect_employee_anomalies(
                employee_id
            )


            if anomalies:

                employee_anomalies.append({
                    "name": employee_name,
                    "email": employee_email,
                    "anomalies": anomalies
                })


                for anomaly in anomalies:

                    all_anomalies.append({
                        "employee": employee_name,
                        "type": anomaly["type"],
                        "severity": anomaly["severity"],
                        "message": anomaly["message"]
                    })


        # -------------------------------------------------
        # ANOMALY SUMMARY
        # -------------------------------------------------

        st.subheader(
            "📊 Anomaly Summary"
        )


        total_anomalies = len(
            all_anomalies
        )


        high_count = sum(
            1
            for anomaly in all_anomalies
            if anomaly["severity"] == "High"
        )


        medium_count = sum(
            1
            for anomaly in all_anomalies
            if anomaly["severity"] == "Medium"
        )


        low_count = sum(
            1
            for anomaly in all_anomalies
            if anomaly["severity"] == "Low"
        )


        employees_with_anomalies = len(
            employee_anomalies
        )


        total_employees = len(
            employees
        )


        col1, col2, col3, col4, col5 = st.columns(5)


        with col1:

            st.metric(
                "👥 Employees Scanned",
                total_employees
            )


        with col2:

            st.metric(
                "🚨 Total Anomalies",
                total_anomalies
            )


        with col3:

            st.metric(
                "⚠️ Employees Affected",
                employees_with_anomalies
            )


        with col4:

            st.metric(
                "🔴 High Severity",
                high_count
            )


        with col5:

            st.metric(
                "🟠 Medium Severity",
                medium_count
            )


        st.divider()


        # -------------------------------------------------
        # ANOMALY TYPE BREAKDOWN
        # -------------------------------------------------

        st.subheader(
            "📋 Anomaly Type Breakdown"
        )


        if all_anomalies:

            anomaly_type_counts = {}


            for anomaly in all_anomalies:

                anomaly_type = anomaly["type"]

                anomaly_type_counts[
                    anomaly_type
                ] = anomaly_type_counts.get(
                    anomaly_type,
                    0
                ) + 1


            breakdown_df = pd.DataFrame(
                list(
                    anomaly_type_counts.items()
                ),
                columns=[
                    "Anomaly Type",
                    "Count"
                ]
            )


            breakdown_df = breakdown_df.sort_values(
                "Count",
                ascending=False
            )


            col1, col2 = st.columns(2)


            with col1:

                st.dataframe(
                    breakdown_df,
                    use_container_width=True,
                    hide_index=True
                )


            with col2:

                st.bar_chart(
                    breakdown_df.set_index(
                        "Anomaly Type"
                    )
                )


        else:

            st.success(
                "🎉 No anomalies detected across employees."
            )


        st.divider()


        # -------------------------------------------------
        # EMPLOYEE-WISE ANOMALIES
        # -------------------------------------------------

        st.subheader(
            "👥 Employee-wise Anomalies"
        )


        if employee_anomalies:

            for employee_data in employee_anomalies:

                employee_name = employee_data["name"]
                employee_email = employee_data["email"]
                anomalies = employee_data["anomalies"]


                st.markdown(
                    f"### 👤 {employee_name}"
                )


                st.write(
                    f"📧 {employee_email}"
                )


                for anomaly in anomalies:

                    severity = anomaly["severity"]


                    if severity == "High":

                        st.error(
                            f"🔴 **{anomaly['type']}** — "
                            f"{anomaly['message']}"
                        )


                    elif severity == "Medium":

                        st.warning(
                            f"🟠 **{anomaly['type']}** — "
                            f"{anomaly['message']}"
                        )


                    else:

                        st.info(
                            f"🔵 **{anomaly['type']}** — "
                            f"{anomaly['message']}"
                        )


                st.divider()


        else:

            st.success(
                "✅ All employees currently have normal attendance patterns."
            )


    else:

        st.info(
            "No employees available."
        )


# =====================================================
# ALERTS
# =====================================================

elif user["role"] in ["Admin", "Manager"] and page == "Alerts":

    st.title("🔔 Attendance Alerts")

    st.write(
        "Monitor and resolve attendance-related alerts."
    )

    st.divider()


    alerts = get_all_alerts()


    # -------------------------------------------------
    # ALERT SUMMARY
    # -------------------------------------------------

    unresolved_count = sum(
        1
        for alert in alerts
        if alert[7] == 0
    )


    resolved_count = sum(
        1
        for alert in alerts
        if alert[7] == 1
    )


    col1, col2, col3 = st.columns(3)


    with col1:

        st.metric(
            "🔔 Total Alerts",
            len(alerts)
        )


    with col2:

        st.metric(
            "⚠️ Active Alerts",
            unresolved_count
        )


    with col3:

        st.metric(
            "✅ Resolved Alerts",
            resolved_count
        )


    st.divider()


    # -------------------------------------------------
    # ALERT LIST
    # -------------------------------------------------

    if alerts:

        for alert in alerts:

            (
                alert_id,
                employee_name,
                employee_email,
                alert_type,
                message,
                severity,
                created_at,
                is_resolved
            ) = alert


            if severity == "High":

                icon = "🔴"

            elif severity == "Medium":

                icon = "🟠"

            else:

                icon = "🔵"


            with st.container():

                st.subheader(
                    f"{icon} {alert_type}"
                )


                st.write(
                    f"👤 **Employee:** {employee_name}"
                )


                st.write(
                    f"📧 **Email:** {employee_email}"
                )


                st.write(
                    f"🕒 **Created:** {created_at}"
                )


                st.write(
                    f"📌 **Severity:** {severity}"
                )


                st.write(
                    f"📝 **Message:** {message}"
                )


                if is_resolved == 0:

                    if st.button(
                        "✅ Resolve Alert",
                        key=f"resolve_{alert_id}",
                        use_container_width=True
                    ):

                        resolve_alert(
                            alert_id
                        )

                        st.success(
                            "Alert resolved successfully."
                        )

                        st.rerun()


                else:

                    st.success(
                        "✅ This alert has been resolved."
                    )


                st.divider()


    else:

        st.success(
            "🎉 No alerts found."
        )
