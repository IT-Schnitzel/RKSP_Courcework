import sys
import requests
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, IntPrompt, FloatPrompt, Confirm
from rich.panel import Panel
from rich import print as rprint
from datetime import datetime

BASE_URL = "http://localhost:8000"  # change if needed
session_id = None
user_id = None

console = Console()

def api_request(method, endpoint, params=None, data=None):
    global session_id
    url = f"{BASE_URL}{endpoint}"
    if session_id:
        params = params or {}
        params["session_id"] = session_id
    try:
        if method == "GET":
            response = requests.get(url, params=params)
        elif method == "POST":
            response = requests.post(url, params=params, json=data)
        elif method == "PUT":
            response = requests.put(url, params=params, json=data)
        elif method == "DELETE":
            response = requests.delete(url, params=params)
        else:
            raise ValueError("Unsupported method")
        return response
    except Exception as e:
        console.print(f"[red]Request error: {e}[/red]")
        return None

def login():
    global session_id, user_id
    console.print(Panel("Login", style="bold blue"))
    username = Prompt.ask("Username or Email")
    password = Prompt.ask("Password", password=True)
    response = api_request("POST", "/auth/login", data={"username_or_email": username, "password": password})
    if response and response.status_code == 200:
        data = response.json()
        session_id = data["session_id"]
        user_id = data["user_id"]
        console.print(f"[green]Login successful. Welcome {data['username']}![/green]")
        return True
    else:
        console.print("[red]Login failed[/red]")
        return False

def register():
    console.print(Panel("Register", style="bold blue"))
    username = Prompt.ask("Username")
    email = Prompt.ask("Email")
    password = Prompt.ask("Password", password=True)
    response = api_request("POST", "/auth/register", data={"username": username, "email": email, "password": password})
    if response and response.status_code == 200:
        console.print("[green]Registration successful. Please login.[/green]")
        return True
    else:
        console.print("[red]Registration failed[/red]")
        return False

def logout():
    global session_id
    if session_id:
        api_request("POST", "/auth/logout")
        session_id = None
        console.print("[yellow]Logged out[/yellow]")

def list_tasks():
    response = api_request("GET", "/api/tasks")
    if response and response.status_code == 200:
        tasks = response.json()
        if not tasks:
            console.print("No tasks found.")
            return
        table = Table(title="Tasks")
        table.add_column("ID", style="cyan")
        table.add_column("Title")
        table.add_column("Status")
        table.add_column("Priority")
        table.add_column("Assigned")
        table.add_column("Deadline")
        for t in tasks:
            table.add_row(
                str(t["id"]),
                t["title"][:30],
                t["status"],
                t["priority"],
                str(t["assigned_to_id"]),
                t["deadline"][:10] if t["deadline"] else "N/A"
            )
        console.print(table)
    else:
        console.print("[red]Failed to fetch tasks[/red]")

def create_task():
    console.print(Panel("Create Task", style="bold green"))
    title = Prompt.ask("Title")
    description = Prompt.ask("Description", default="")
    assigned_id = IntPrompt.ask("Assigned User ID")
    project_id = IntPrompt.ask("Project ID (0 for none)", default=0)
    status = Prompt.ask("Status", choices=["pending","in_progress","completed","cancelled","archived"], default="pending")
    priority = Prompt.ask("Priority", choices=["low","medium","high","urgent","critical"], default="medium")
    planned_hours = FloatPrompt.ask("Planned hours", default=0.0)
    deadline_str = Prompt.ask("Deadline (YYYY-MM-DD)", default="")
    deadline = None
    if deadline_str:
        try:
            deadline = datetime.strptime(deadline_str, "%Y-%m-%d").isoformat()
        except:
            console.print("[red]Invalid date format[/red]")
            return
    data = {
        "title": title,
        "description": description,
        "assigned_to_id": assigned_id,
        "project_id": project_id if project_id != 0 else None,
        "status": status,
        "priority": priority,
        "planned_hours": planned_hours,
        "deadline": deadline
    }
    response = api_request("POST", "/api/tasks", data=data)
    if response and response.status_code == 201:
        console.print("[green]Task created[/green]")
    else:
        console.print("[red]Failed to create task[/red]")

def update_task():
    task_id = IntPrompt.ask("Task ID")
    response_get = api_request("GET", f"/api/tasks/{task_id}")
    if not response_get or response_get.status_code != 200:
        console.print("[red]Task not found[/red]")
        return
    task = response_get.json()
    console.print("Enter new values (leave blank to keep current):")
    title = Prompt.ask("Title", default=task["title"])
    description = Prompt.ask("Description", default=task["description"] or "")
    status = Prompt.ask("Status", choices=["pending","in_progress","completed","cancelled","archived"], default=task["status"])
    priority = Prompt.ask("Priority", choices=["low","medium","high","urgent","critical"], default=task["priority"])
    planned_hours = FloatPrompt.ask("Planned hours", default=task["planned_hours"])
    deadline_str = Prompt.ask("Deadline (YYYY-MM-DD)", default=task["deadline"][:10] if task["deadline"] else "")
    deadline = None
    if deadline_str:
        try:
            deadline = datetime.strptime(deadline_str, "%Y-%m-%d").isoformat()
        except:
            console.print("[red]Invalid date format[/red]")
            return
    data = {}
    if title != task["title"]: data["title"] = title
    if description != (task["description"] or ""): data["description"] = description
    if status != task["status"]: data["status"] = status
    if priority != task["priority"]: data["priority"] = priority
    if planned_hours != task["planned_hours"]: data["planned_hours"] = planned_hours
    if deadline != (task["deadline"][:10] if task["deadline"] else ""): data["deadline"] = deadline
    if data:
        response = api_request("PUT", f"/api/tasks/{task_id}", data=data)
        if response and response.status_code == 200:
            console.print("[green]Task updated[/green]")
        else:
            console.print("[red]Update failed[/red]")
    else:
        console.print("No changes made.")

def delete_task():
    task_id = IntPrompt.ask("Task ID")
    hard = Confirm.ask("Hard delete? (y/n)", default=False)
    response = api_request("DELETE", f"/api/tasks/{task_id}", params={"hard": hard})
    if response and response.status_code == 200:
        console.print("[green]Task deleted[/green]")
    else:
        console.print("[red]Delete failed[/red]")

def list_projects():
    response = api_request("GET", "/api/projects")
    if response and response.status_code == 200:
        projects = response.json()
        if not projects:
            console.print("No projects found.")
            return
        table = Table(title="Projects")
        table.add_column("ID", style="cyan")
        table.add_column("Name")
        table.add_column("Status")
        table.add_column("Priority")
        table.add_column("Budget")
        for p in projects:
            table.add_row(
                str(p["id"]),
                p["name"],
                p["status"],
                str(p["priority"]),
                str(p["budget"]) if p["budget"] else "N/A"
            )
        console.print(table)
    else:
        console.print("[red]Failed to fetch projects[/red]")

def create_project():
    console.print(Panel("Create Project", style="bold green"))
    name = Prompt.ask("Name")
    description = Prompt.ask("Description", default="")
    status = Prompt.ask("Status", choices=["active","completed","frozen"], default="active")
    priority = IntPrompt.ask("Priority", default=1)
    budget = FloatPrompt.ask("Budget", default=0.0)
    data = {
        "name": name,
        "description": description,
        "status": status,
        "priority": priority,
        "budget": budget if budget > 0 else None
    }
    response = api_request("POST", "/api/projects", data=data)
    if response and response.status_code == 201:
        console.print("[green]Project created[/green]")
    else:
        console.print("[red]Failed to create project[/red]")

def stats():
    response = api_request("GET", "/api/stats/overview")
    if response and response.status_code == 200:
        stats = response.json()
        console.print(Panel(f"[bold]Overview[/bold]\nTotal: {stats['total_tasks']}\nCompleted: {stats['completed_tasks']}\nOverdue: {stats['overdue_tasks']}\nCompletion Rate: {stats['completion_rate']:.1f}%", style="bold cyan"))
        if stats["status_distribution"]:
            table = Table(title="Status Distribution")
            table.add_column("Status")
            table.add_column("Count")
            for item in stats["status_distribution"]:
                table.add_row(item["status"], str(item["count"]))
            console.print(table)
        if stats["user_workload"]:
            table = Table(title="User Workload")
            table.add_column("User")
            table.add_column("Planned")
            table.add_column("Actual")
            table.add_column("Tasks")
            for w in stats["user_workload"]:
                table.add_row(w["username"], str(w["planned_hours"]), str(w["actual_hours"]), str(w["task_count"]))
            console.print(table)
    else:
        console.print("[red]Failed to fetch stats[/red]")

def main():
    global session_id
    console.print(Panel("Task Manager CLI", style="bold yellow"))
    while True:
        if not session_id:
            console.print("\n[bold]Main Menu (not logged in)[/bold]")
            console.print("1. Login")
            console.print("2. Register")
            console.print("3. Exit")
            choice = Prompt.ask("Choose", choices=["1","2","3"])
            if choice == "1":
                if login():
                    continue
            elif choice == "2":
                register()
            else:
                break
        else:
            console.print("\n[bold]Main Menu[/bold]")
            console.print("1. List Tasks")
            console.print("2. Create Task")
            console.print("3. Update Task")
            console.print("4. Delete Task")
            console.print("5. List Projects")
            console.print("6. Create Project")
            console.print("7. Statistics")
            console.print("8. Logout")
            console.print("9. Exit")
            choice = Prompt.ask("Choose", choices=["1","2","3","4","5","6","7","8","9"])
            if choice == "1":
                list_tasks()
            elif choice == "2":
                create_task()
            elif choice == "3":
                update_task()
            elif choice == "4":
                delete_task()
            elif choice == "5":
                list_projects()
            elif choice == "6":
                create_project()
            elif choice == "7":
                stats()
            elif choice == "8":
                logout()
            else:
                break

if __name__ == "__main__":
    main()