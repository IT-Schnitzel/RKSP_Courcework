import streamlit as st
from datetime import datetime


def show(api_request):
    st.markdown("---")
    response = api_request("GET", "/api/stats/overview")
    if response is None:
        st.error("❌ Ошибка подключения")
        return

    if response.status_code == 200:
        stats = response.json()

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📝 Всего задач", stats["total_tasks"])
        with col2:
            st.metric("✅ Завершено", stats["completed_tasks"])
        with col3:
            st.metric("⚠️ Просрочено", stats["overdue_tasks"], delta_color="inverse")
        with col4:
            st.metric("📈 Выполнено", f"{stats['completion_rate']:.1f}%")

        st.markdown("---")

        st.subheader("📊 Распределение по статусам")
        if stats["status_distribution"]:
            st.bar_chart({item["status"]: item["count"] for item in stats["status_distribution"]})
        else:
            st.info("Нет данных")

        st.subheader("🎯 Распределение по приоритетам")
        if stats["priority_distribution"]:
            st.bar_chart({item["priority"]: item["count"] for item in stats["priority_distribution"]})
        else:
            st.info("Нет данных")

        st.markdown("---")
        st.subheader("👥 Загрузка исполнителей")
        workload = stats.get("user_workload", [])
        if workload:
            import pandas as pd
            df = pd.DataFrame(workload)
            df = df.rename(columns={
                "username": "Исполнитель",
                "task_count": "Задач",
                "planned_hours": "Плановые часы",
                "actual_hours": "Фактические часы"
            })
            st.dataframe(df, use_container_width=True)
        else:
            st.info("Нет данных о загрузке")

        st.markdown("---")
        st.subheader("⚠️ Просроченные задачи")
        tasks_resp = api_request("GET", "/api/tasks")
        if tasks_resp and tasks_resp.status_code == 200:
            tasks = tasks_resp.json()
            today = datetime.now().date()
            overdue_tasks = [t for t in tasks if
                             t.get('deadline') and t['status'] != 'completed' and datetime.fromisoformat(
                                 t['deadline'][:10]).date() < today]
            if overdue_tasks:
                for t in overdue_tasks:
                    st.markdown(f"""
                    <div style="background:#f8d7da; padding:0.8rem 1rem; border-radius:8px; margin-bottom:0.5rem; border-left:4px solid #dc3545;">
                        <div><strong>📌 {t['title']}</strong> — исполнитель: #{t['assigned_to_id']}</div>
                        <div style="font-size:0.85rem; color:#721c24;">Срок: {t['deadline'][:10]} | Просрочено</div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.success("✅ Нет просроченных задач")
        else:
            st.info("Не удалось загрузить задачи")
    else:
        st.error(f"❌ Ошибка загрузки статистики: {response.text}")