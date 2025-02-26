import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from fpdf import FPDF
import numpy as np
import numpy_financial as npf
from sqlalchemy import create_engine, Column, Integer, String, Float, Date, MetaData, Table
from sqlalchemy.orm import sessionmaker

# Initialize database connection
DATABASE_URL = "sqlite:///jayjay_bt_app.db"
engine = create_engine(DATABASE_URL)
metadata = MetaData()
Session = sessionmaker(bind=engine)
session = Session()

# Define table structure
projects_table = Table(
    'projects', metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String),
    Column('start_date', Date),
    Column('end_date', Date),
    Column('budget', Float),
    Column('spent', Float),
    Column('status', String),
    Column('portfolio', String),
    Column('impact', Float),
    Column('deliverable', String),
    Column('timeline', String)
)
tasks_table = Table(
    'tasks', metadata,
    Column('id', Integer, primary_key=True),
    Column('project_name', String),
    Column('task', String),
    Column('priority', String),
    Column('status', String),
    Column('start_date', Date),
    Column('end_date', Date)
)
risks_table = Table(
    'risks', metadata,
    Column('id', Integer, primary_key=True),
    Column('project_name', String),
    Column('risk', String),
    Column('likelihood', Float),
    Column('impact', Float),
    Column('severity', Float),
    Column('status', String)
)
budget_table = Table(
    'budget', metadata,
    Column('id', Integer, primary_key=True),
    Column('project_name', String),
    Column('category', String),
    Column('allocated', Float),
    Column('spent', Float)
)
resources_table = Table(
    'resources', metadata,
    Column('id', Integer, primary_key=True),
    Column('project_name', String),
    Column('resource_name', String),
    Column('allocation', Float)
)
issues_table = Table(
    'issues', metadata,
    Column('id', Integer, primary_key=True),
    Column('project_name', String),
    Column('description', String),
    Column('priority', String),
    Column('status', String)
)
milestones_table = Table(
    'milestones', metadata,
    Column('id', Integer, primary_key=True),
    Column('project_name', String),
    Column('milestone', String),
    Column('due_date', Date),
    Column('status', String)
)
charter_table = Table(
    'charter', metadata,
    Column('id', Integer, primary_key=True),
    Column('project_name', String),
    Column('objective', String),
    Column('scope', String),
    Column('stakeholders', String)
)
costs_table = Table(
    'costs', metadata,
    Column('id', Integer, primary_key=True),
    Column('project_name', String),
    Column('category', String),
    Column('planned_cost', Float),
    Column('actual_cost', Float),
    Column('status', String)
)
todos_table = Table(
    'todos', metadata,
    Column('id', Integer, primary_key=True),
    Column('project_name', String),
    Column('task', String),
    Column('priority', String),
    Column('status', String),
    Column('due_date', Date)
)
portfolio_table = Table(
    'portfolio', metadata,
    Column('id', Integer, primary_key=True),
    Column('project_name', String),
    Column('portfolio_type', String)
)
calendar_table = Table(
    'calendar', metadata,
    Column('id', Integer, primary_key=True),
    Column('project_name', String),
    Column('event_name', String),
    Column('event_date', Date)
)
cost_estimations_table = Table(
    'cost_estimations', metadata,
    Column('id', Integer, primary_key=True),
    Column('project_name', String),
    Column('item', String),
    Column('estimated_cost', Float)
)
users_table = Table(
    'users', metadata,
    Column('id', Integer, primary_key=True),
    Column('username', String, unique=True),
    Column('password', String)
)

metadata.create_all(engine)

# Initialize session state
def initialize_state():
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
    if 'current_user' not in st.session_state:
        st.session_state['current_user'] = None

initialize_state()

# Set page configuration
st.set_page_config(page_title="Jay Jay Business Transformation App", layout="wide")

# Function to handle user registration
def register_user(username, password):
    if session.execute(users_table.select().where(users_table.c.username == username)).fetchone():
        return False, "Username already exists!"
    session.execute(users_table.insert().values(username=username, password=password))
    session.commit()
    return True, "User registered successfully!"

# Function to handle user login
def login_user(username, password):
    user = session.execute(users_table.select().where(users_table.c.username == username).where(users_table.c.password == password)).fetchone()
    if user:
        st.session_state['logged_in'] = True
        st.session_state['current_user'] = username
        return True, "Login successful!"
    return False, "Invalid username or password!"

# Sidebar for navigation and settings
st.sidebar.title("Jay Jay Business Transformation App")
st.sidebar.markdown("### Navigation")

categories = {
    "Project Initiation": [
        "Dashboard",
        "Project Charter",
        "Project Milestones",
        "Portfolio Tracking"
    ],
    "Project Planning": [
        "Project Schedule",
        "Task Management",
        "Resource Tracking",
        "Risk Management"
    ],
    "Budgeting and Costing": [
        "Budget Management",
        "Cost Management",
        "Cost Estimation",
        "ROI Calculation"
    ],
    "Change Management": [
        "Issue Management",
        "To-Do List",
        "Project Calendar",
        "Reporting",
        "Training and Development",
        "Visualizations"
    ]
}

selected_category = st.sidebar.selectbox("Select a category:", list(categories.keys()))

if selected_category:
    options = categories[selected_category]
    selected_section = st.sidebar.radio("Select a section:", options)

# Theme and background color selection
theme = st.sidebar.selectbox("Select Theme", ["Light", "Dark"])
background_color = st.sidebar.color_picker("Pick a Background Color", "#36523c")
form_color = st.sidebar.color_picker("Pick a Form Background Color", "#C5943A")
font_color = st.sidebar.color_picker("Pick a Font Color", "#000000")
title_font_color = st.sidebar.color_picker("Pick a Title Font Color", "#000000")

# Apply the selected background color
st.markdown(f"""
    <style>
    .main {{
        background-color: {background_color};
        color: {font_color};
    }}
    .sidebar .sidebar-content {{
        background-color: {background_color};
    }}
    .stForm {{
        background-color: {form_color};
    }}
    .stTitle {{
        color: {title_font_color};
    }}
    </style>
    """, unsafe_allow_html=True)

# User login/registration section
if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
    st.sidebar.header("Login/Register")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Login"):
        success, message = login_user(username, password)
        st.sidebar.write(message)
    if st.sidebar.button("Register"):
        success, message = register_user(username, password)
        st.sidebar.write(message)
else:
    st.sidebar.write(f"Welcome {st.session_state['current_user']}")
    if st.sidebar.button("Logout"):
        st.session_state['logged_in'] = False
        st.sidebar.write("Logged out successfully!")

# Functions for different sections
def dashboard():
    st.title("Business Transformation Project Tracker")

    with st.form("add_project_form"):
        st.subheader("Add New Project")
        project_name = st.text_input("Project Name")
        start_date = st.date_input("Start Date")
        end_date = st.date_input("End Date")
        budget = st.number_input("Budget", min_value=0)
        spent = st.number_input("Spent", min_value=0)
        status = st.selectbox("Status", ["Not Started", "In Progress", "Completed"])
        portfolio = st.selectbox("Portfolio", ["Turnaround project", "Special project", "Digitisation and automation"])
        impact = st.number_input("Impact on Business", min_value=0)
        deliverable = st.text_input("Deliverable")
        timeline = st.text_input("Timeline")
        submitted = st.form_submit_button("Add Project")
        if submitted:
            new_project = {
                'name': project_name,
                'start_date': start_date,
                'end_date': end_date,
                'budget': budget,
                'spent': spent,
                'status': status,
                'portfolio': portfolio,
                'impact': impact,
                'deliverable': deliverable,
                'timeline': timeline
            }
            session.execute(projects_table.insert().values(new_project))
            session.commit()
            st.success(f"Project added successfully! Project Name: {project_name}")

    projects = session.execute(projects_table.select()).fetchall()
    project_df = pd.DataFrame(projects, columns=['id', 'Project Name', 'Start Date', 'End Date', 'Budget', 'Spent', 'Status', 'Portfolio', 'Impact on Business', 'Deliverable', 'Timeline'])
    
    if not project_df.empty:
        project_df['Start Date'] = pd.to_datetime(project_df['Start Date'])
        project_df['End Date'] = pd.to_datetime(project_df['End Date'])

        fig_project_status = px.timeline(project_df, x_start="Start Date", x_end="End Date", y="Project Name", color="Status", title="Project Timelines and Status")
        fig_project_status.update_yaxes(categoryorder="total ascending")
        st.plotly_chart(fig_project_status, use_container_width=True)

        fig_budget_vs_spent = px.bar(project_df, x='Project Name', y=['Budget', 'Spent'], barmode='group', title="Budget vs Spent")
        st.plotly_chart(fig_budget_vs_spent, use_container_width=True)

        fig_pie = px.pie(project_df, names='Status', title="Project Status Distribution")
        st.plotly_chart(fig_pie, use_container_width=True)

        fig_scatter = px.scatter(project_df, x='Budget', y='Spent', color='Status', size='Spent', title="Budget vs Spent by Status")
        st.plotly_chart(fig_scatter, use_container_width=True)

        st.subheader("Project Data")
        st.dataframe(project_df)
    else:
        st.info("No projects to display. Please add a project.")

def project_schedule():
    st.title("Project Schedule: Monthly Activity Planning")

    project_names = [project[1] for project in session.execute(projects_table.select()).fetchall()]
    selected_project_name = st.selectbox("Select Project Name", project_names)
    
    with st.form("add_activity_form"):
        st.subheader("Add New Activity")
        month = st.selectbox("Month", ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"])
        num_activities = st.number_input("Number of Activities", min_value=0)
        submitted = st.form_submit_button("Add Activity")
        if submitted:
            activities = session.execute(f"SELECT activities FROM projects WHERE name='{selected_project_name}'").fetchone()[0]
            if not activities:
                activities = {}
            if selected_project_name not in activities:
                activities[selected_project_name] = {}
            activities[selected_project_name][month] = num_activities
            session.execute(projects_table.update().where(projects_table.c.name == selected_project_name).values(activities=activities))
            session.commit()
            st.success("Activity added successfully!")

    activities = session.execute(f"SELECT activities FROM projects WHERE name='{selected_project_name}'").fetchone()[0]
    if activities and selected_project_name in activities:
        activities_df = pd.DataFrame(list(activities[selected_project_name].items()), columns=['Month', 'Number of Activities'])
        fig_activities = px.bar(activities_df, x='Month', y='Number of Activities', title="Monthly Activities")
        st.plotly_chart(fig_activities, use_container_width=True)
    else:
        st.info("No activities to display. Please add an activity.")

def budget_management():
    st.title("Budget Management")

    project_names = [project[1] for project in session.execute(projects_table.select()).fetchall()]
    selected_project_name = st.selectbox("Select Project Name", project_names)
    
    with st.form("add_budget_form"):
        st.subheader("Add New Budget Entry")
        category = st.text_input("Category")
        allocated = st.number_input("Allocated Budget", min_value=0)
        spent = st.number_input("Spent Budget", min_value=0)
        submitted = st.form_submit_button("Add Budget Entry")
        if submitted:
            new_budget = {
                'project_name': selected_project_name,
                'category': category,
                'allocated': allocated,
                'spent': spent
            }
            session.execute(budget_table.insert().values(new_budget))
            session.commit()
            st.success("Budget entry added successfully!")

    budgets = session.execute(budget_table.select().where(budget_table.c.project_name == selected_project_name)).fetchall()
    budget_df = pd.DataFrame(budgets, columns=['id', 'Project Name', 'Category', 'Allocated', 'Spent'])
    if not budget_df.empty:
        fig_budget = px.bar(budget_df, x='Category', y=['Allocated', 'Spent'], barmode='group', title="Budget Allocation and Spending")
        st.plotly_chart(fig_budget, use_container_width=True)

        fig_pie_budget = px.pie(budget_df, names='Category', values='Allocated', title="Budget Allocation by Category")
        st.plotly_chart(fig_pie_budget, use_container_width=True)

        fig_budget_sunburst = px.sunburst(budget_df, path=['Category'], values='Spent', title="Spent Budget Sunburst")
        st.plotly_chart(fig_budget_sunburst, use_container_width=True)

        st.subheader("Budget Data")
        st.dataframe(budget_df)
        st.download_button(
            label="Download Budget Data",
            data=budget_df.to_csv(index=False),
            file_name="budget_data.csv",
            mime="text/csv"
        )
    else:
        st.info("No budget data to display for this project. Please add a budget entry.")

def resource_tracking():
    st.title("Resource Tracking")

    project_names = [project[1] for project in session.execute(projects_table.select()).fetchall()]
    selected_project_name = st.selectbox("Select Project Name", project_names)
    
    with st.form("add_resource_form"):
        st.subheader("Add New Resource")
        resource_name = st.text_input("Resource Name")
        allocation = st.number_input("Allocation Percentage", min_value=0, max_value=100)
        submitted = st.form_submit_button("Add Resource")
        if submitted:
            new_resource = {
                'project_name': selected_project_name,
                'resource_name': resource_name,
                'allocation': allocation
            }
            session.execute(resources_table.insert().values(new_resource))
            session.commit()
            st.success("Resource added successfully!")

    resources = session.execute(resources_table.select().where(resources_table.c.project_name == selected_project_name)).fetchall()
    resources_df = pd.DataFrame(resources, columns=['id', 'Project Name', 'Resource Name', 'Allocation'])
    if not resources_df.empty:
        fig_resources = px.pie(resources_df, names='Resource Name', values='Allocation', title="Resource Allocation")
        st.plotly_chart(fig_resources, use_container_width=True)

        fig_bar_resources = px.bar(resources_df, x='Resource Name', y='Allocation', title="Resource Allocation Percentage")
        st.plotly_chart(fig_bar_resources, use_container_width=True)

        fig_donut_resources = go.Figure(data=[go.Pie(labels=resources_df['Resource Name'], values=resources_df['Allocation'], hole=.3)])
        fig_donut_resources.update_layout(title_text="Resource Allocation Donut Chart")
        st.plotly_chart(fig_donut_resources, use_container_width=True)

        st.subheader("Resource Data")
        st.dataframe(resources_df)
        st.download_button(
            label="Download Resource Data",
            data=resources_df.to_csv(index=False),
            file_name="resource_data.csv",
            mime="text/csv"
        )
    else:
        st.info("No resources to display for this project. Please add a resource.")

def issue_management():
    st.title("Issue Management")

    project_names = [project[1] for project in session.execute(projects_table.select()).fetchall()]
    selected_project_name = st.selectbox("Select Project Name", project_names)
    
    with st.form("add_issue_form"):
        st.subheader("Add New Issue")
        issue_description = st.text_area("Issue Description")
        priority = st.selectbox("Priority", ["Low", "Medium", "High"])
        status = st.selectbox("Status", ["Open", "Closed"])
        submitted = st.form_submit_button("Add Issue")
        if submitted:
            new_issue = {
                'project_name': selected_project_name,
                'description': issue_description,
                'priority': priority,
                'status': status
            }
            session.execute(issues_table.insert().values(new_issue))
            session.commit()
            st.success("Issue added successfully!")

    issues = session.execute(issues_table.select().where(issues_table.c.project_name == selected_project_name)).fetchall()
    issues_df = pd.DataFrame(issues, columns=['id', 'Project Name', 'Description', 'Priority', 'Status'])
    if not issues_df.empty:
        fig_issues = px.bar(issues_df, x='Priority', y='Description', color='Status', title="Issues by Priority and Status")
        st.plotly_chart(fig_issues, use_container_width=True)

        fig_pie_issues = px.pie(issues_df, names='Priority', title="Issues Distribution by Priority")
        st.plotly_chart(fig_pie_issues, use_container_width=True)

        fig_sunburst_issues = px.sunburst(issues_df, path=['Priority', 'Status'], title="Issues Sunburst Chart")
        st.plotly_chart(fig_sunburst_issues, use_container_width=True)

        st.subheader("Issue Data")
        st.dataframe(issues_df)
        st.download_button(
            label="Download Issue Data",
            data=issues_df.to_csv(index=False),
            file_name="issue_data.csv",
            mime="text/csv"
        )
    else:
        st.info("No issues to display for this project. Please add an issue.")

def project_milestones():
    st.title("Project Milestones")

    project_names = [project[1] for project in session.execute(projects_table.select()).fetchall()]
    selected_project_name = st.selectbox("Select Project Name", project_names)
    
    with st.form("add_milestone_form"):
        st.subheader("Add New Milestone")
        milestone = st.text_input("Milestone")
        due_date = st.date_input("Due Date")
        status = st.selectbox("Status", ["Not Started", "In Progress", "Completed"])
        submitted = st.form_submit_button("Add Milestone")
        if submitted:
            new_milestone = {
                'project_name': selected_project_name,
                'milestone': milestone,
                'due_date': due_date,
                'status': status
            }
            session.execute(milestones_table.insert().values(new_milestone))
            session.commit()
            st.success("Milestone added successfully!")

    milestones = session.execute(milestones_table.select().where(milestones_table.c.project_name == selected_project_name)).fetchall()
    milestones_df = pd.DataFrame(milestones, columns=['id', 'Project Name', 'Milestone', 'Due Date', 'Status'])
    if not milestones_df.empty:
        fig_milestones = px.timeline(milestones_df, x_start="Due Date", x_end="Due Date", y="Milestone", color="Status", title="Project Milestones")
        st.plotly_chart(fig_milestones, use_container_width=True)

        fig_pie_milestones = px.pie(milestones_df, names='Status', title="Milestone Status Distribution")
        st.plotly_chart(fig_pie_milestones, use_container_width=True)

        st.subheader("Milestone Data")
        st.dataframe(milestones_df)
        st.download_button(
            label="Download Milestone Data",
            data=milestones_df.to_csv(index=False),
            file_name="milestone_data.csv",
            mime="text/csv"
        )
    else:
        st.info("No milestones to display for this project. Please add a milestone.")

def project_charter():
    st.title("Project Charter")

    project_names = [project[1] for project in session.execute(projects_table.select()).fetchall()]
    selected_project_name = st.selectbox("Select Project Name", project_names)
    
    with st.form("add_charter_form"):
        st.subheader("Add New Project Charter Entry")
        objective = st.text_input("Objective")
        scope = st.text_area("Scope")
        stakeholders = st.text_area("Stakeholders")
        submitted = st.form_submit_button("Add Charter Entry")
        if submitted:
            new_charter = {
                'project_name': selected_project_name,
                'objective': objective,
                'scope': scope,
                'stakeholders': stakeholders
            }
            session.execute(charter_table.insert().values(new_charter))
            session.commit()
            st.success("Charter entry added successfully!")

    charters = session.execute(charter_table.select().where(charter_table.c.project_name == selected_project_name)).fetchall()
    charter_df = pd.DataFrame(charters, columns=['id', 'Project Name', 'Objective', 'Scope', 'Stakeholders'])
    if not charter_df.empty:
        st.subheader("Project Charter Data")
        st.dataframe(charter_df)

        fig_sunburst_charter = px.sunburst(charter_df, path=['Objective', 'Scope'], title="Project Charter Sunburst Chart")
        st.plotly_chart(fig_sunburst_charter, use_container_width=True)
        st.download_button(
            label="Download Charter Data",
            data=charter_df.to_csv(index=False),
            file_name="charter_data.csv",
            mime="text/csv"
        )
    else:
        st.info("No charter entries to display for this project. Please add a charter entry.")

def risk_management():
    st.title("Risk Management")

    project_names = [project[1] for project in session.execute(projects_table.select()).fetchall()]
    selected_project_name = st.selectbox("Select Project Name", project_names)
    
    with st.form("add_risk_form"):
        st.subheader("Add New Risk")
        risk = st.text_input("Risk")
        likelihood = st.slider("Likelihood", 0.0, 1.0, 0.5)
        impact = st.slider("Impact", 0.0, 1.0, 0.5)
        severity = likelihood * impact
        status = st.selectbox("Status", ["Open", "Mitigated", "Closed"])
        submitted = st.form_submit_button("Add Risk")
        if submitted:
            new_risk = {
                'project_name': selected_project_name,
                'risk': risk,
                'likelihood': likelihood,
                'impact': impact,
                'severity': severity,
                'status': status
            }
            session.execute(risks_table.insert().values(new_risk))
            session.commit()
            st.success("Risk added successfully!")

    risks = session.execute(risks_table.select().where(risks_table.c.project_name == selected_project_name)).fetchall()
    risk_df = pd.DataFrame(risks, columns=['id', 'Project Name', 'Risk', 'Likelihood', 'Impact', 'Severity', 'Status'])
    if not risk_df.empty:
        fig_risks = px.scatter(risk_df, x='Likelihood', y='Impact', size='Severity', color='Status', hover_name='Risk', title="Risk Likelihood vs Impact")
        st.plotly_chart(fig_risks, use_container_width=True)

        fig_pie_risks = px.pie(risk_df, names='Status', title="Risk Status Distribution")
        st.plotly_chart(fig_pie_risks, use_container_width=True)

        st.subheader("Risk Data")
        st.dataframe(risk_df)
        st.download_button(
            label="Download Risk Data",
            data=risk_df.to_csv(index=False),
            file_name="risk_data.csv",
            mime="text/csv"
        )
    else:
        st.info("No risks to display for this project. Please add a risk.")

def cost_management():
    st.title("Cost Management")

    project_names = [project[1] for project in session.execute(projects_table.select()).fetchall()]
    selected_project_name = st.selectbox("Select Project Name", project_names)
    
    with st.form("add_cost_form"):
        st.subheader("Add New Cost Entry")
        category = st.text_input("Category")
        planned_cost = st.number_input("Planned Cost", min_value=0)
        actual_cost = st.number_input("Actual Cost", min_value=0)
        status = st.selectbox("Status", ["On Track", "Over Budget", "Under Budget"])
        submitted = st.form_submit_button("Add Cost Entry")
        if submitted:
            new_cost = {
                'project_name': selected_project_name,
                'category': category,
                'planned_cost': planned_cost,
                'actual_cost': actual_cost,
                'status': status
            }
            session.execute(costs_table.insert().values(new_cost))
            session.commit()
            st.success("Cost entry added successfully!")

    costs = session.execute(costs_table.select().where(costs_table.c.project_name == selected_project_name)).fetchall()
    cost_df = pd.DataFrame(costs, columns=['id', 'Project Name', 'Category', 'Planned Cost', 'Actual Cost', 'Status'])
    if not cost_df.empty:
        fig_costs = px.bar(cost_df, x='Category', y=['Planned Cost', 'Actual Cost'], barmode='group', title="Planned vs Actual Costs")
        st.plotly_chart(fig_costs, use_container_width=True)

        fig_pie_costs = px.pie(cost_df, names='Status', title="Cost Status Distribution")
        st.plotly_chart(fig_pie_costs, use_container_width=True)

        st.subheader("Cost Data")
        st.dataframe(cost_df)
        st.download_button(
            label="Download Cost Data",
            data=cost_df.to_csv(index=False),
            file_name="cost_data.csv",
            mime="text/csv"
        )
    else:
        st.info("No cost data to display for this project. Please add a cost entry.")

def todo_list():
    st.title("To-Do List")

    project_names = [project[1] for project in session.execute(projects_table.select()).fetchall()]
    selected_project_name = st.selectbox("Select Project Name", project_names)
    
    with st.form("add_todo_form"):
        st.subheader("Add New To-Do Item")
        task = st.text_input("Task")
        priority = st.selectbox("Priority", ["High", "Medium", "Low"])
        status = st.selectbox("Status", ["Not Started", "In Progress", "Completed"])
        due_date = st.date_input("Due Date")
        submitted = st.form_submit_button("Add To-Do Item")
        if submitted:
            new_todo = {
                'project_name': selected_project_name,
                'task': task,
                'priority': priority,
                'status': status,
                'due_date': due_date
            }
            session.execute(todos_table.insert().values(new_todo))
            session.commit()
            st.success("To-Do item added successfully!")

    todos = session.execute(todos_table.select().where(todos_table.c.project_name == selected_project_name)).fetchall()
    todo_df = pd.DataFrame(todos, columns=['id', 'Project Name', 'Task', 'Priority', 'Status', 'Due Date'])
    if not todo_df.empty:
        st.subheader("To-Do List")
        st.dataframe(todo_df)

        fig_todos = px.bar(todo_df, x='Task', y='Priority', color='Status', title="To-Do List by Priority and Status")
        st.plotly_chart(fig_todos, use_container_width=True)
        st.download_button(
            label="Download To-Do Data",
            data=todo_df.to_csv(index=False),
            file_name="todo_data.csv",
            mime="text/csv"
        )
    else:
        st.info("No to-do items to display for this project. Please add a to-do item.")

def portfolio_tracking():
    st.title("Portfolio Tracking")

    portfolios = session.execute(portfolio_table.select()).fetchall()
    portfolio_df = pd.DataFrame(portfolios, columns=['id', 'Project Name', 'Portfolio Type'])
    if not portfolio_df.empty:
        fig_portfolio = px.pie(portfolio_df, names='Portfolio Type', title="Portfolio Distribution")
        st.plotly_chart(fig_portfolio, use_container_width=True)

        fig_portfolio_timeline = px.timeline(portfolio_df, x_start="Start Date", x_end="End Date", y="Project Name", color="Portfolio Type", title="Project Portfolio Timeline")
        st.plotly_chart(fig_portfolio_timeline, use_container_width=True)

        st.subheader("Portfolio Data")
        st.dataframe(portfolio_df)
        st.download_button(
            label="Download Portfolio Data",
            data=portfolio_df.to_csv(index=False),
            file_name="portfolio_data.csv",
            mime="text/csv"
        )
    else:
        st.info("No portfolio entries to display. Please add a portfolio entry.")

def project_calendar():
    st.title("Project Calendar")

    project_names = [project[1] for project in session.execute(projects_table.select()).fetchall()]
    selected_project_name = st.selectbox("Select Project Name", project_names)
    
    with st.form("add_calendar_form"):
        st.subheader("Add New Calendar Entry")
        event_name = st.text_input("Event Name")
        event_date = st.date_input("Event Date")
        submitted = st.form_submit_button("Add Calendar Entry")
        if submitted:
            new_calendar_entry = {
                'project_name': selected_project_name,
                'event_name': event_name,
                'event_date': event_date
            }
            session.execute(calendar_table.insert().values(new_calendar_entry))
            session.commit()
            st.success("Calendar entry added successfully!")

    calendar_entries = session.execute(calendar_table.select().where(calendar_table.c.project_name == selected_project_name)).fetchall()
    calendar_df = pd.DataFrame(calendar_entries, columns=['id', 'Project Name', 'Event Name', 'Event Date'])
    if not calendar_df.empty:
        st.subheader("Project Calendar")
        st.dataframe(calendar_df)

        fig_calendar = px.timeline(calendar_df, x_start="Event Date", x_end="Event Date", y="Event Name", title="Project Calendar")
        st.plotly_chart(fig_calendar, use_container_width=True)
        st.download_button(
            label="Download Calendar Data",
            data=calendar_df.to_csv(index=False),
            file_name="calendar_data.csv",
            mime="text/csv"
        )
    else:
        st.info("No calendar entries to display for this project. Please add a calendar entry.")

def task_management():
    st.title("Task Management")

    project_names = [project[1] for project in session.execute(projects_table.select()).fetchall()]
    selected_project_name = st.selectbox("Select Project Name", project_names)
    
    with st.form("add_task_form"):
        st.subheader("Add New Task")
        task = st.text_input("Task")
        priority = st.selectbox("Priority", ["High", "Medium", "Low"])
        status = st.selectbox("Status", ["Not Started", "In Progress", "Completed"])
        start_date = st.date_input("Start Date")
        end_date = st.date_input("End Date")
        submitted = st.form_submit_button("Add Task")
        if submitted:
            new_task = {
                'project_name': selected_project_name,
                'task': task,
                'priority': priority,
                'status': status,
                'start_date': start_date,
                'end_date': end_date
            }
            session.execute(tasks_table.insert().values(new_task))
            session.commit()
            st.success("Task added successfully!")

    tasks = session.execute(tasks_table.select().where(tasks_table.c.project_name == selected_project_name)).fetchall()
    task_df = pd.DataFrame(tasks, columns=['id', 'Project Name', 'Task', 'Priority', 'Status', 'Start Date', 'End Date'])
    if not task_df.empty:
        st.subheader("Task Data")
        st.dataframe(task_df)

        fig_tasks = px.timeline(task_df, x_start="Start Date", x_end="End Date", y="Task", color="Status", title="Task Management")
        st.plotly_chart(fig_tasks, use_container_width=True)
        st.download_button(
            label="Download Task Data",
            data=task_df.to_csv(index=False),
            file_name="task_data.csv",
            mime="text/csv"
        )
    else:
        st.info("No tasks to display for this project. Please add a task.")

def gantt_chart():
    st.title("Gantt Chart")

    project_names = [project[1] for project in session.execute(projects_table.select()).fetchall()]
    selected_project_name = st.selectbox("Select Project Name", project_names)

    gantt_color = st.color_picker("Pick a Gantt Chart Bar Color", "#1f77b4")

    tasks = session.execute(tasks_table.select().where(tasks_table.c.project_name == selected_project_name)).fetchall()
    task_df = pd.DataFrame(tasks, columns=['id', 'Project Name', 'Task', 'Priority', 'Status', 'Start Date', 'End Date'])
    if not task_df.empty:
        fig_gantt = px.timeline(task_df, x_start="Start Date", x_end="End Date", y="Task", color="Priority", title="Gantt Chart")
        fig_gantt.update_traces(marker_color=gantt_color)
        st.plotly_chart(fig_gantt, use_container_width=True)
        st.download_button(
            label="Download Gantt Chart",
            data=fig_gantt.to_image(format="png"),
            file_name="gantt_chart.png",
            mime="image/png"
        )
    else:
        st.info("No tasks to display in Gantt chart.")

def cost_estimation():
    st.title("Cost Estimation")

    project_names = [project[1] for project in session.execute(projects_table.select()).fetchall()]
    selected_project_name = st.selectbox("Select Project Name", project_names)
    
    with st.form("add_cost_estimation_form"):
        st.subheader("Add New Cost Estimation")
        item = st.text_input("Item")
        estimated_cost = st.number_input("Estimated Cost", min_value=0)
        submitted = st.form_submit_button("Add Cost Estimation")
        if submitted:
            new_cost_estimation = {
                'project_name': selected_project_name,
                'item': item,
                'estimated_cost': estimated_cost
            }
            session.execute(cost_estimations_table.insert().values(new_cost_estimation))
            session.commit()
            st.success("Cost estimation added successfully!")

    cost_estimations = session.execute(cost_estimations_table.select().where(cost_estimations_table.c.project_name == selected_project_name)).fetchall()
    cost_estimations_df = pd.DataFrame(cost_estimations, columns=['id', 'Project Name', 'Item', 'Estimated Cost'])
    if not cost_estimations_df.empty:
        st.subheader("Cost Estimations")
        st.dataframe(cost_estimations_df)

        fig_cost_estimations = px.bar(cost_estimations_df, x='Item', y='Estimated Cost', title="Cost Estimations")
        st.plotly_chart(fig_cost_estimations, use_container_width=True)
        st.download_button(
            label="Download Cost Estimations Data",
            data=cost_estimations_df.to_csv(index=False),
            file_name="cost_estimations_data.csv",
            mime="text/csv"
        )
    else:
        st.info("No cost estimations to display for this project. Please add a cost estimation.")

def reporting():
    st.title("Reporting")

    st.write("Generate reports based on the data from different sections.")

    if 'projects' in st.session_state:
        st.subheader("Project Reports")
        st.dataframe(st.session_state['projects'])

    if 'tasks' in st.session_state:
        st.subheader("Task Reports")
        st.dataframe(st.session_state['tasks'])

    if 'risks' in st.session_state:
        st.subheader("Risk Reports")
        st.dataframe(st.session_state['risks'])

    if 'budget' in st.session_state:
        st.subheader("Budget Reports")
        st.dataframe(pd.DataFrame(st.session_state['budget']))

    if 'resources' in st.session_state:
        st.subheader("Resource Reports")
        st.dataframe(pd.DataFrame(st.session_state['resources']))

    if 'issues' in st.session_state:
        st.subheader("Issue Reports")
        st.dataframe(pd.DataFrame(st.session_state['issues']))

    if 'milestones' in st.session_state:
        st.subheader("Milestone Reports")
        st.dataframe(pd.DataFrame(st.session_state['milestones']))

    if 'charter' in st.session_state:
        st.subheader("Charter Reports")
        st.dataframe(pd.DataFrame(st.session_state['charter']))

    if 'costs' in st.session_state:
        st.subheader("Cost Reports")
        st.dataframe(pd.DataFrame(st.session_state['costs']))

    if 'todos' in st.session_state:
        st.subheader("To-Do List Reports")
        st.dataframe(pd.DataFrame(st.session_state['todos']))

    if 'portfolio' in st.session_state:
        st.subheader("Portfolio Reports")
        st.dataframe(pd.DataFrame(st.session_state['portfolio']))

    if 'calendar' in st.session_state:
        st.subheader("Calendar Reports")
        st.dataframe(pd.DataFrame(st.session_state['calendar']))

    if 'cost_estimations' in st.session_state:
        st.subheader("Cost Estimations Reports")
        st.dataframe(pd.DataFrame(st.session_state['cost_estimations']))

    if st.button("Download Full Report"):
        csv_data = []
        for section in [
            'projects', 'tasks', 'risks', 'budget', 'resources', 'issues', 
            'milestones', 'charter', 'costs', 'todos', 'portfolio', 
            'calendar', 'cost_estimations'
        ]:
            data = pd.DataFrame(st.session_state[section])
            csv_data.append(data.to_csv(index=False))

        full_report = '\n'.join(csv_data)
        st.download_button(
            label="Download Full Report as CSV",
            data=full_report,
            file_name="full_report.csv",
            mime="text/csv"
        )

def roi_calculation():
    st.title("ROI Calculation")

    with st.form("roi_calculation_form"):
        st.subheader("ROI Calculation")
        initial_investment = st.number_input("Initial Investment", min_value=0.0)
        cash_flows = st.text_area("Annual Cash Flows (comma separated)")
        years = st.number_input("Number of Years", min_value=1)
        submitted = st.form_submit_button("Calculate ROI")
        if submitted:
            cash_flows = list(map(float, cash_flows.split(',')))
            total_return = sum(cash_flows)
            roi = (total_return - initial_investment) / initial_investment * 100
            irr = npf.irr([-initial_investment] + cash_flows) * 100
            st.success(f"ROI: {roi:.2f}%")
            st.success(f"IRR: {irr:.2f}%")

def make_presentation():
    st.title("Make Presentation")

    class PDF(FPDF):
        def header(self):
            self.set_font("Arial", "B", 12)
            self.cell(0, 10, "Management Presentation", 0, 1, "C")

        def footer(self):
            self.set_y(-15)
            self.set_font("Arial", "I", 8)
            self.cell(0, 10, f"Page {self.page_no()}", 0, 0, "C")

    def add_chart_to_pdf(pdf, chart_title, chart_figure):
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(200, 10, txt=chart_title, ln=True, align='C')
        pdf.set_font("Arial", size=12)
        pdf.ln(10)
        pdf.image(chart_figure, x=10, y=30, w=pdf.w - 20)

    def generate_pdf():
        pdf = PDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        sections_data = {
            "Dashboard": st.session_state['projects'],
            "Tasks": st.session_state['tasks'],
            "Risks": st.session_state['risks'],
            "Budget": pd.DataFrame(st.session_state['budget']),
            "Resources": pd.DataFrame(st.session_state['resources']),
            "Issues": pd.DataFrame(st.session_state['issues']),
            "Milestones": pd.DataFrame(st.session_state['milestones']),
            "Charter": pd.DataFrame(st.session_state['charter']),
            "Costs": pd.DataFrame(st.session_state['costs']),
            "To-Dos": pd.DataFrame(st.session_state['todos']),
            "Portfolio": pd.DataFrame(st.session_state['portfolio']),
            "Calendar": pd.DataFrame(st.session_state['calendar']),
            "Cost Estimations": pd.DataFrame(st.session_state['cost_estimations']),
        }

        for section, data in sections_data.items():
            pdf.add_page()
            pdf.set_font("Arial", "B", 16)
            pdf.cell(200, 10, txt=section, ln=True, align='C')
            pdf.set_font("Arial", size=12)
            if isinstance(data, pd.DataFrame) and not data.empty:
                pdf.ln(10)
                pdf.set_font("Arial", size=10)
                for i in range(len(data)):
                    row = data.iloc[i]
                    for item in row:
                        pdf.cell(40, 10, str(item), 1)
                    pdf.ln()
            else:
                pdf.cell(200, 10, "No data available", ln=True)

        chart_sections = {
            "Project Status Timeline": generate_project_status_timeline_chart(),
            "Budget vs Spent": generate_budget_vs_spent_chart(),
            "Project Status Distribution": generate_project_status_distribution_chart(),
            "Budget vs Spent by Status": generate_budget_vs_spent_by_status_chart(),
        }

        for chart_title, chart_figure in chart_sections.items():
            if chart_figure:
                add_chart_to_pdf(pdf, chart_title, chart_figure)

        pdf_output = "presentation.pdf"
        pdf.output(pdf_output)
        return pdf_output

    # Function to generate project status timeline chart
    def generate_project_status_timeline_chart():
        project_df = st.session_state['projects']
        if not project_df.empty:
            project_df['Start Date'] = pd.to_datetime(project_df['Start Date'])
            project_df['End Date'] = pd.to_datetime(project_df['End Date'])
            fig = px.timeline(project_df, x_start="Start Date", x_end="End Date", y="Project Name", color="Status", title="Project Timelines and Status")
            fig.update_yaxes(categoryorder="total ascending")
            fig_path = "project_status.png"
            fig.write_image(fig_path)
            return fig_path
        return None

    # Function to generate budget vs spent chart
    def generate_budget_vs_spent_chart():
        project_df = st.session_state['projects']
        if not project_df.empty:
            fig = px.bar(project_df, x='Project Name', y=['Budget', 'Spent'], barmode='group', title="Budget vs Spent")
            fig_path = "budget_vs_spent.png"
            fig.write_image(fig_path)
            return fig_path
        return None

    # Function to generate project status distribution chart
    def generate_project_status_distribution_chart():
        project_df = st.session_state['projects']
        if not project_df.empty:
            fig = px.pie(project_df, names='Status', title="Project Status Distribution")
            fig_path = "project_status_distribution.png"
            fig.write_image(fig_path)
            return fig_path
        return None

    # Function to generate budget vs spent by status chart
    def generate_budget_vs_spent_by_status_chart():
        project_df = st.session_state['projects']
        if not project_df.empty:
            fig = px.scatter(project_df, x='Budget', y='Spent', color='Status', size='Spent', title="Budget vs Spent by Status")
            fig_path = "budget_vs_spent_status.png"
            fig.write_image(fig_path)
            return fig_path
        return None

    if st.button("Generate PDF"):
        pdf_file = generate_pdf()
        with open(pdf_file, "rb") as file:
            st.download_button(
                label="Download Presentation PDF",
                data=file,
                file_name=pdf_file,
                mime="application/pdf"
            )

def job_description():
    st.title("Job Description: Assistant Manager Business Transformation")

    st.header("Job Summary")
    st.write("Seeking a highly motivated and results-oriented Business Transformation Assistant Manager to play a pivotal role in leading the digitization and turnaround initiatives of our organization. You will be responsible for identifying and implementing strategic solutions that optimize processes, enhance efficiency, and ultimately drive sustainable growth.")

    st.header("Main Tasks")

    tasks = [
        ("Develop and execute comprehensive digitization plans", "Analyze current business processes and identify opportunities for automation and digital transformation."),
        ("Research and evaluate emerging technologies", "Research and evaluate emerging technologies with a focus on their potential impact on the organization."),
        ("Develop and implement a roadmap for digitization", "Develop and implement a roadmap for digitization prioritizing initiatives based on feasibility, impact, and return on investment (ROI)."),
        ("Lead turnaround projects", "Collaborate with cross-functional teams to identify and address critical areas impacting business performance."),
        ("Develop and implement turnaround plans", "Develop and implement turnaround plans encompassing cost optimization, revenue generation strategies, and process improvements."),
        ("Track progress", "Track progress, measure results, and ensure that project objectives are met within budget and timelines."),
        ("Champion a culture of continuous improvement", "Champion a culture of continuous improvement within the organization."),
        ("Develop and implement communication strategies", "Develop and implement effective communication strategies to ensure all stakeholders are informed and engaged throughout the transformation process."),
        ("Lead training initiatives", "Lead training initiatives to equip employees with the skills and knowledge necessary to adapt to new processes and technologies."),
        ("Develop and implement KPIs", "Develop and implement key performance indicators (KPIs) to track the progress and success of digitization and turnaround initiatives."),
        ("Monitor and analyze performance data", "Regularly monitor and analyze performance data, identifying areas for further improvement."),
        ("Prepare comprehensive reports", "Prepare comprehensive reports to keep senior management informed of project progress and overall business transformation efforts.")
    ]

    with st.form("add_task_form"):
        task = st.selectbox("Task", [t[0] for t in tasks])
        description = st.text_area("Description", value=[t[1] for t in tasks if t[0] == task][0])
        confirmation = st.selectbox("Confirmation of accuracy of Allocated task", ["Not Confirmed", "Confirmed"])
        remarks = st.text_area("Remarks")
        submitted = st.form_submit_button("Add Task")
        if submitted:
            new_task = pd.DataFrame({
                'Project Name': [selected_project_name],
                'Task': [task],
                'Description': [description],
                'Confirmation': [confirmation],
                'Remarks': [remarks]
            })
            st.session_state['jd_data'] = pd.concat([st.session_state['jd_data'], new_task], ignore_index=True)
            st.success("Task added successfully!")

    st.subheader("Tasks Data")
    task_df = st.session_state['jd_data']
    st.dataframe(task_df)

    if not task_df.empty:
        fig_confirmation = px.pie(task_df, names='Confirmation', title="Task Confirmation Status")
        st.plotly_chart(fig_confirmation, use_container_width=True)

# Functions for additional sections
def training_and_development():
    st.title("Training and Development")

    with st.form("add_training_form"):
        st.subheader("Add New Training Program")
        program_name = st.text_input("Program Name")
        trainer = st.text_input("Trainer")
        start_date = st.date_input("Start Date")
        end_date = st.date_input("End Date")
        status = st.selectbox("Status", ["Planned", "In Progress", "Completed"])
        submitted = st.form_submit_button("Add Training Program")
        if submitted:
            new_training = {
                'program_name': program_name,
                'trainer': trainer,
                'start_date': start_date,
                'end_date': end_date,
                'status': status
            }
            session.execute(training_table.insert().values(new_training))
            session.commit()
            st.success("Training program added successfully!")

    training = session.execute(training_table.select()).fetchall()
    training_df = pd.DataFrame(training, columns=['id', 'Program Name', 'Trainer', 'Start Date', 'End Date', 'Status'])
    if not training_df.empty:
        st.subheader("Training Programs Data")
        st.dataframe(training_df)

        fig_training = px.bar(training_df, x='Program Name', y='Status', color='Status', title="Training Programs Status")
        st.plotly_chart(fig_training, use_container_width=True)
        st.download_button(
            label="Download Training Data",
            data=training_df.to_csv(index=False),
            file_name="training_data.csv",
            mime="text/csv"
        )
    else:
        st.info("No training programs to display. Please add a training program.")

def visualizations():
    st.title("Visualizations")

    project_df = session.execute(projects_table.select()).fetchall()
    project_df = pd.DataFrame(project_df, columns=['id', 'Project Name', 'Start Date', 'End Date', 'Budget', 'Spent', 'Status', 'Portfolio', 'Impact on Business', 'Deliverable', 'Timeline'])
    if not project_df.empty:
        project_df['Start Date'] = pd.to_datetime(project_df['Start Date'])
        project_df['End Date'] = pd.to_datetime(project_df['End Date'])

        fig_project_status = px.timeline(project_df, x_start="Start Date", x_end="End Date", y="Project Name", color="Status", title="Project Timelines and Status")
        st.plotly_chart(fig_project_status, use_container_width=True)

        fig_budget_vs_spent = px.bar(project_df, x='Project Name', y=['Budget', 'Spent'], barmode='group', title="Budget vs Spent")
        st.plotly_chart(fig_budget_vs_spent, use_container_width=True)

        fig_pie = px.pie(project_df, names='Status', title="Project Status Distribution")
        st.plotly_chart(fig_pie, use_container_width=True)

        fig_scatter = px.scatter(project_df, x='Budget', y='Spent', color='Status', size='Spent', title="Budget vs Spent by Status")
        st.plotly_chart(fig_scatter, use_container_width=True)

    else:
        st.info("No projects to display. Please add a project.")

# Render the selected section
if 'logged_in' in st.session_state and st.session_state['logged_in']:
    if selected_section == "Dashboard":
        dashboard()
    elif selected_section == "Project Charter":
        project_charter()
    elif selected_section == "Project Milestones":
        project_milestones()
    elif selected_section == "Portfolio Tracking":
        portfolio_tracking()
    elif selected_section == "Project Schedule":
        project_schedule()
    elif selected_section == "Task Management":
        task_management()
    elif selected_section == "Resource Tracking":
        resource_tracking()
    elif selected_section == "Risk Management":
        risk_management()
    elif selected_section == "Budget Management":
        budget_management()
    elif selected_section == "Cost Management":
        cost_management()
    elif selected_section == "Cost Estimation":
        cost_estimation()
    elif selected_section == "ROI Calculation":
        roi_calculation()
    elif selected_section == "Issue Management":
        issue_management()
    elif selected_section == "To-Do List":
        todo_list()
    elif selected_section == "Project Calendar":
        project_calendar()
    elif selected_section == "Reporting":
        reporting()
    elif selected_section == "Training and Development":
        training_and_development()
    elif selected_section == "Visualizations":
        visualizations()
    elif selected_section == "Gantt Chart":
        gantt_chart()
else:
    st.write("Please log in to access the app.")

st.markdown('<div class="footer">Developed and undertrial by Shankar</div>', unsafe_allow_html=True)
