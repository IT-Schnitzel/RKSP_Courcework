import streamlit as st


def show(api_request):
    st.title("📊 Дашборд")
    st.markdown("---")

    response = api_request("GET", "/api/stats/overview")
    if response is None:
        st.error("❌ Ошибка подключения")
        return

    if response.status_code == 200:
        stats = response.json()

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📋 Всего задач", stats["total_tasks"])
        with col2:
            st.metric("✅ Завершено", stats["completed_tasks"], f"{stats['completion_rate']:.1f}%")
        with col3:
            st.metric("⚠️ Просрочено", stats["overdue_tasks"], delta_color="inverse")
        with col4:
            st.metric("📈 Выполнено", f"{stats['completion_rate']:.1f}%")

        st.markdown("---")

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("📊 Распределение по статусам")
            if stats["status_distribution"]:
                st.bar_chart({item["status"]: item["count"] for item in stats["status_distribution"]})
            else:
                st.info("Нет данных")

        with col2:
            st.subheader("🎯 Распределение по приоритетам")
            if stats["priority_distribution"]:
                st.bar_chart({item["priority"]: item["count"] for item in stats["priority_distribution"]})
            else:
                st.info("Нет данных")

        st.markdown("---")
        st.subheader("👥 Загрузка исполнителей")
        if stats["user_workload"]:
            data = {}
            for w in stats["user_workload"]:
                data[f"{w['username']} (план)"] = w["planned_hours"]
                data[f"{w['username']} (факт)"] = w["actual_hours"]
            st.bar_chart(data)
        else:
            st.info("Нет данных о загрузке")
    else:
        st.error(f"❌ Ошибка загрузки дашборда: {response.text}")