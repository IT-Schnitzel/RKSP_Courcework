import streamlit as st
from datetime import datetime


def show(api_request):
    st.markdown("---")

    projects_response = api_request("GET", "/api/projects")
    projects = []
    if projects_response and projects_response.status_code == 200:
        projects = projects_response.json()
    project_options = ["Без проекта"] + [f"{p['id']}: {p['name']}" for p in projects]
    project_id_map = {f"{p['id']}: {p['name']}": p['id'] for p in projects}

    with st.expander("➕ Создать задачу", expanded=False):
        with st.form("create_task"):
            errors = []
            col1, col2 = st.columns(2)
            with col1:
                title = st.text_input("Название *", placeholder="Введите название задачи")
                description = st.text_area("Описание", placeholder="Подробное описание")
                assigned_to = st.number_input("ID исполнителя *", min_value=1, step=1, value=1)
            with col2:
                project_choice = st.selectbox("Проект", project_options)
                project_id = project_id_map.get(project_choice) if project_choice != "Без проекта" else None
                status = st.selectbox("Статус", ["pending", "in_progress", "completed", "cancelled", "archived"])
                priority = st.selectbox("Приоритет", ["low", "medium", "high", "urgent", "critical"])
                planned_hours = st.number_input("Плановые часы", min_value=0.0, step=0.5, value=0.0)
                deadline = st.date_input("Срок выполнения", value=None)
            submitted = st.form_submit_button("✨ Создать", use_container_width=True)
            if submitted:
                if not title:
                    errors.append("Название обязательно")
                if assigned_to < 1:
                    errors.append("ID исполнителя должен быть положительным")
                if planned_hours < 0:
                    errors.append("Часы не могут быть отрицательными")
                if deadline and deadline < datetime.now().date():
                    errors.append("Срок не может быть в прошлом")
                if errors:
                    for err in errors:
                        st.error(f"❌ {err}")
                else:
                    data = {
                        "title": title.strip(),
                        "description": description if description else None,
                        "assigned_to_id": assigned_to,
                        "project_id": project_id,
                        "status": status,
                        "priority": priority,
                        "planned_hours": planned_hours,
                        "deadline": deadline.isoformat() if deadline else None
                    }
                    resp = api_request("POST", "/api/tasks", data=data)
                    if resp and resp.status_code == 201:
                        st.success("✅ Задача создана!")
                        st.rerun()
                    elif resp:
                        st.error(f"❌ Ошибка: {resp.text}")
                    else:
                        st.error("❌ Не удалось создать задачу")

    with st.expander("🔍 Фильтры", expanded=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            status_filter = st.selectbox("Статус",
                                         ["Все", "pending", "in_progress", "completed", "cancelled", "archived"])
        with col2:
            priority_filter = st.selectbox("Приоритет", ["Все", "low", "medium", "high", "urgent", "critical"])
        with col3:
            search = st.text_input("🔎 Поиск", placeholder="По названию или описанию")

    params = {}
    if status_filter != "Все":
        params["status"] = status_filter
    if priority_filter != "Все":
        params["priority"] = priority_filter
    if search:
        params["search"] = search

    response = api_request("GET", "/api/tasks", params=params)
    if response is None:
        st.error("❌ Ошибка подключения")
        return

    if response.status_code == 200:
        tasks = response.json()
        if not tasks:
            st.info("📭 Нет задач. Создайте первую!")
        else:
            st.write(f"📋 Найдено **{len(tasks)}** задач")
            for task in tasks:
                with st.expander(f"📌 {task['title']}"):
                    col1, col2, col3 = st.columns([2, 1, 1])
                    with col1:
                        st.write(f"**Статус:** {task['status']}")
                        st.write(f"**Приоритет:** {task['priority']}")
                        st.write(f"**Исполнитель:** User #{task['assigned_to_id']}")
                        st.write(f"**Плановые часы:** {task['planned_hours']}")
                        st.write(f"**Фактические часы:** {task['actual_hours']}")
                        st.write(f"**Описание:** {task.get('description') or 'Нет описания'}")
                        if task.get('project_id'):
                            proj = next((p for p in projects if p['id'] == task['project_id']), None)
                            st.write(f"**Проект:** {proj['name'] if proj else task['project_id']}")
                        else:
                            st.write("**Проект:** Нет")
                        if task.get('deadline'):
                            st.write(f"**Срок:** {task['deadline'][:10]}")
                        st.write(f"**Создана:** {task['created_at'][:10]}")

                    with col2:
                        st.write("**Действия:**")
                        if task['status'] != 'completed':
                            if st.button(f"✅ Завершить", key=f"complete_{task['id']}"):
                                update_data = {"status": "completed"}
                                resp = api_request("PUT", f"/api/tasks/{task['id']}", data=update_data)
                                if resp and resp.status_code == 200:
                                    st.success("✅ Задача завершена!")
                                    st.rerun()
                                else:
                                    st.error("❌ Ошибка завершения")

                        if st.button(f"✏️ Редактировать", key=f"edit_{task['id']}"):
                            st.session_state.edit_task_id = task['id']
                            st.rerun()

                    with col3:
                        st.write("")
                        if st.button(f"🗑️ Удалить", key=f"delete_{task['id']}"):
                            del_resp = api_request("DELETE", f"/api/tasks/{task['id']}")
                            if del_resp and del_resp.status_code == 200:
                                st.success("✅ Задача удалена!")
                                st.rerun()
                            else:
                                st.error("❌ Ошибка удаления")

    if hasattr(st.session_state, 'edit_task_id'):
        task_id = st.session_state.edit_task_id
        response = api_request("GET", f"/api/tasks/{task_id}")
        if response and response.status_code == 200:
            task = response.json()
            st.markdown("---")
            st.subheader(f"✏️ Редактирование задачи #{task_id}")
            with st.form("edit_task_form"):
                col1, col2 = st.columns(2)
                with col1:
                    edit_title = st.text_input("Название", value=task['title'])
                    edit_description = st.text_area("Описание", value=task.get('description') or '')
                    edit_assigned_to = st.number_input("ID исполнителя", min_value=1, step=1,
                                                       value=task['assigned_to_id'])
                with col2:
                    statuses = ["pending", "in_progress", "completed", "cancelled", "archived"]
                    edit_status = st.selectbox("Статус", statuses, index=statuses.index(task['status']))
                    priorities = ["low", "medium", "high", "urgent", "critical"]
                    edit_priority = st.selectbox("Приоритет", priorities, index=priorities.index(task['priority']))
                    edit_planned_hours = st.number_input("Плановые часы", min_value=0.0, step=0.5,
                                                         value=task['planned_hours'])
                    edit_deadline = st.date_input("Срок выполнения",
                                                  value=datetime.fromisoformat(task['deadline']).date() if task.get(
                                                      'deadline') else None)

                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    if st.form_submit_button("💾 Сохранить", use_container_width=True):
                        data = {
                            "title": edit_title,
                            "description": edit_description if edit_description else None,
                            "assigned_to_id": edit_assigned_to,
                            "status": edit_status,
                            "priority": edit_priority,
                            "planned_hours": edit_planned_hours,
                            "deadline": edit_deadline.isoformat() if edit_deadline else None
                        }
                        resp = api_request("PUT", f"/api/tasks/{task_id}", data=data)
                        if resp and resp.status_code == 200:
                            st.success("✅ Задача обновлена!")
                            del st.session_state.edit_task_id
                            st.rerun()
                        else:
                            st.error("❌ Ошибка обновления")
                with col_btn2:
                    if st.form_submit_button("❌ Отмена", use_container_width=True):
                        del st.session_state.edit_task_id
                        st.rerun()