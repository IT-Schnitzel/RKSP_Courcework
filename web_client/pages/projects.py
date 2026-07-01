import streamlit as st


def show(api_request):
    st.markdown("---")

    with st.expander("➕ Создать проект", expanded=False):
        with st.form("create_project"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Название *", placeholder="Введите название")
                description = st.text_area("Описание", placeholder="Описание проекта")
            with col2:
                status = st.selectbox("Статус", ["active", "completed", "frozen"])
                priority = st.number_input("Приоритет", min_value=0, value=1)
                budget = st.number_input("Бюджет", min_value=0.0, value=0.0)
            submitted = st.form_submit_button("✨ Создать", use_container_width=True)
            if submitted:
                if not name:
                    st.error("❌ Название обязательно")
                else:
                    data = {
                        "name": name.strip(),
                        "description": description if description else None,
                        "status": status,
                        "priority": priority,
                        "budget": budget if budget > 0 else None
                    }
                    resp = api_request("POST", "/api/projects", data=data)
                    if resp and resp.status_code == 201:
                        st.success("✅ Проект создан!")
                        st.rerun()
                    elif resp:
                        st.error(f"❌ Ошибка: {resp.text}")
                    else:
                        st.error("❌ Не удалось создать проект")

    response = api_request("GET", "/api/projects")
    if response is None:
        st.error("❌ Ошибка подключения")
        return

    if response.status_code == 200:
        projects = response.json()
        if not projects:
            st.info("📭 Нет проектов. Создайте первый!")
        else:
            for proj in projects:
                with st.expander(f"📁 {proj['name']}"):
                    col1, col2, col3 = st.columns([2, 1, 1])
                    with col1:
                        st.write(f"**Описание:** {proj.get('description') or 'Нет описания'}")
                        st.write(f"**Статус:** {proj.get('status', 'active')}")
                        st.write(f"**Приоритет:** {proj.get('priority', 1)}")
                        st.write(f"**Бюджет:** {proj.get('budget') or 'Не установлен'}")
                        st.write(f"**Владелец:** User #{proj.get('owner_id', '?')}")

                    with col2:
                        st.write("**Действия:**")
                        if st.button(f"✏️ Редактировать", key=f"edit_proj_{proj['id']}"):
                            st.session_state.edit_project_id = proj['id']
                            st.rerun()

                    with col3:
                        st.write("")
                        if st.button(f"🗑️ Удалить", key=f"delete_proj_{proj['id']}"):
                            del_resp = api_request("DELETE", f"/api/projects/{proj['id']}")
                            if del_resp and del_resp.status_code == 200:
                                st.success("✅ Проект удалён!")
                                st.rerun()
                            else:
                                st.error("❌ Ошибка удаления")

    if hasattr(st.session_state, 'edit_project_id'):
        proj_id = st.session_state.edit_project_id
        response = api_request("GET", f"/api/projects/{proj_id}")
        if response and response.status_code == 200:
            proj = response.json()
            st.markdown("---")
            st.subheader(f"✏️ Редактирование проекта #{proj_id}")
            with st.form("edit_project_form"):
                col1, col2 = st.columns(2)
                with col1:
                    edit_name = st.text_input("Название", value=proj['name'])
                    edit_description = st.text_area("Описание", value=proj.get('description') or '')
                with col2:
                    edit_status = st.selectbox("Статус", ["active", "completed", "frozen"],
                                               index=["active", "completed", "frozen"].index(proj['status']))
                    edit_priority = st.number_input("Приоритет", min_value=0, value=proj['priority'])
                    edit_budget = st.number_input("Бюджет", min_value=0.0, value=proj.get('budget') or 0.0)

                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    if st.form_submit_button("💾 Сохранить", use_container_width=True):
                        data = {
                            "name": edit_name,
                            "description": edit_description if edit_description else None,
                            "status": edit_status,
                            "priority": edit_priority,
                            "budget": edit_budget if edit_budget > 0 else None
                        }
                        resp = api_request("PUT", f"/api/projects/{proj_id}", data=data)
                        if resp and resp.status_code == 200:
                            st.success("✅ Проект обновлён!")
                            del st.session_state.edit_project_id
                            st.rerun()
                        else:
                            st.error("❌ Ошибка обновления")
                with col_btn2:
                    if st.form_submit_button("❌ Отмена", use_container_width=True):
                        del st.session_state.edit_project_id
                        st.rerun()