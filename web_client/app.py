import streamlit as st
import requests
import os

BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000")

st.set_page_config(
    page_title="Task Manager Pro",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="collapsed"
)

if "session_id" not in st.session_state:
    st.session_state.session_id = None
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "username" not in st.session_state:
    st.session_state.username = None
if "page" not in st.session_state:
    st.session_state.page = "dashboard"

st.markdown("""
<style>
    .main .block-container {
        padding: 0 !important;
        max-width: 100% !important;
        margin: 0 !important;
    }
    .stAppViewContainer {
        padding-top: 0 !important;
    }
    .st-emotion-cache-1r6slb0 {
        padding-top: 0 !important;
    }
    .st-emotion-cache-6qob1r {
        padding: 0 !important;
    }

    .login-wrapper {
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 100vh;
        background: white;
        padding: 20px;
        margin: 0;
    }

    .login-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        width: 100%;
        max-width: 380px;
    }

    .login-logo {
        text-align: center;
        margin-bottom: 25px;
    }
    .login-logo .logo-icon {
        font-size: 3.5rem;
        display: block;
        margin-bottom: 5px;
    }
    .login-logo h1 {
        font-size: 1.8rem;
        margin: 0;
        background: linear-gradient(135deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .login-logo p {
        color: #888;
        font-size: 0.85rem;
        margin: 3px 0 0 0;
    }

    .login-card {
        background: white;
        border-radius: 16px;
        padding: 30px 30px 25px 30px;
        width: 100%;
        box-shadow: 0 10px 40px rgba(0,0,0,0.08);
        border: 1px solid #f0f0f0;
    }
    .login-card .stTabs [data-baseweb="tab-list"] {
        gap: 20px;
        border-bottom: 2px solid #eee;
        justify-content: center;
    }
    .login-card .stTabs [data-baseweb="tab"] {
        padding-bottom: 8px;
        font-weight: 500;
        color: #666;
        font-size: 0.9rem;
    }
    .login-card .stTabs [aria-selected="true"] {
        color: #667eea;
        border-bottom: 2px solid #667eea;
    }
    .login-card .stTabs [data-baseweb="tab-panel"] {
        padding-top: 15px;
    }
    .login-card .stTextInput > div {
        margin-bottom: 12px;
    }
    .login-card .stTextInput label {
        display: block;
        margin-bottom: 4px;
        color: #333;
        font-weight: 500;
        font-size: 13px;
    }
    .login-card .stTextInput input {
        width: 100%;
        padding: 10px 14px;
        border: 1px solid #ddd;
        border-radius: 10px;
        font-size: 14px;
        transition: all 0.3s;
    }
    .login-card .stTextInput input:focus {
        outline: none;
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102,126,234,0.1);
    }
    .login-card .stButton button {
        width: 100%;
        padding: 10px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border: none;
        border-radius: 10px;
        color: white;
        font-size: 15px;
        font-weight: bold;
        cursor: pointer;
        margin-top: 5px;
        transition: transform 0.2s;
    }
    .login-card .stButton button:hover {
        transform: translateY(-1px);
    }
    .login-card .form-footer {
        text-align: center;
        margin-top: 15px;
        font-size: 13px;
        color: #888;
    }
    .login-card .form-footer a {
        color: #667eea;
        text-decoration: none;
        cursor: pointer;
    }
    .login-card .password-hint {
        font-size: 12px;
        color: #999;
        margin-top: 3px;
    }

    .custom-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 0.8rem 2rem;
        border-radius: 15px;
        color: white;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
    }
    .custom-header h1 {
        font-size: 1.5rem;
        margin: 0;
    }
    .custom-header .user-info {
        display: flex;
        align-items: center;
        gap: 1rem;
    }
    .custom-header .avatar {
        width: 36px;
        height: 36px;
        border-radius: 50%;
        background: rgba(255,255,255,0.2);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1rem;
        font-weight: bold;
    }
    .sidebar-item {
        display: block;
        width: 100%;
        padding: 0.5rem 0.8rem;
        margin: 0.1rem 0;
        border-radius: 10px;
        color: #1E293B;
        font-weight: 500;
        transition: all 0.2s;
        cursor: pointer;
        text-align: left;
        background: transparent;
        border: none;
        font-size: 0.9rem;
    }
    .sidebar-item:hover {
        background: #EEF2FF;
        color: #667eea;
    }
    .sidebar-item.active {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
</style>
""", unsafe_allow_html=True)


def login(username_or_email, password):
    try:
        response = requests.post(
            f"{BACKEND_URL}/auth/login",
            json={"username_or_email": username_or_email, "password": password}
        )
        if response.status_code == 200:
            data = response.json()
            st.session_state.session_id = data["session_id"]
            st.session_state.user_id = data["user_id"]
            st.session_state.username = data["username"]
            return True
        else:
            st.error("❌ Ошибка входа: " + response.text)
            return False
    except Exception as e:
        st.error(f"❌ Ошибка подключения: {e}")
        return False


def logout():
    if st.session_state.session_id:
        try:
            requests.post(f"{BACKEND_URL}/auth/logout", params={"session_id": st.session_state.session_id})
        except:
            pass
    st.session_state.session_id = None
    st.session_state.user_id = None
    st.session_state.username = None
    st.session_state.page = "dashboard"
    st.rerun()


def api_request(method, endpoint, params=None, data=None):
    if not st.session_state.session_id:
        st.error("Не авторизован")
        return None
    url = f"{BACKEND_URL}{endpoint}"
    params = params or {}
    params["session_id"] = st.session_state.session_id
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
        if response.status_code == 401:
            st.error("Сессия истекла. Войдите заново.")
            logout()
            return None
        return response
    except Exception as e:
        st.error(f"Ошибка запроса: {e}")
        return None


def navigate_to(page):
    st.session_state.page = page
    st.rerun()


def main():
    if not st.session_state.session_id:
        st.markdown("""
        <div class="login-wrapper">
            <div class="login-container">
                <div class="login-logo">
                    <span class="logo-icon">📋</span>
                    <h1>Task Manager Pro</h1>
                    <p>Управление проектами и задачами</p>
                </div>
                <div class="login-card">
        """, unsafe_allow_html=True)

        tabs = st.tabs(["📝 Регистрация", "🔐 Вход"])
        with tabs[0]:
            with st.form("register_form"):
                reg_username = st.text_input("Логин *", placeholder="Придумайте логин")
                reg_email = st.text_input("Email *", placeholder="example@mail.com")
                reg_password = st.text_input("Пароль *", type="password", placeholder="Придумайте пароль")
                st.markdown('<div class="password-hint">Пароль должен содержать не менее 6 символов</div>',
                            unsafe_allow_html=True)
                reg_submit = st.form_submit_button("📝 Зарегистрироваться", use_container_width=True)
                if reg_submit:
                    try:
                        resp = requests.post(f"{BACKEND_URL}/auth/register", json={
                            "username": reg_username,
                            "email": reg_email,
                            "password": reg_password
                        })
                        if resp.status_code == 200:
                            st.success("✅ Регистрация успешна! Теперь войдите.")
                        else:
                            st.error("❌ Ошибка регистрации: " + resp.text)
                    except Exception as e:
                        st.error(f"❌ Ошибка: {e}")
            st.markdown('<div class="form-footer"><a>Уже есть аккаунт? Войти</a></div>', unsafe_allow_html=True)
        with tabs[1]:
            with st.form("login_form"):
                username = st.text_input("Логин или Email", placeholder="Введите логин или email")
                password = st.text_input("Пароль", type="password", placeholder="Введите пароль")
                submitted = st.form_submit_button("🔑 Войти", use_container_width=True)
                if submitted:
                    if login(username, password):
                        st.success("✅ Вход выполнен!")
                        st.rerun()
            st.markdown('<div class="form-footer"><a>Нет аккаунта? Зарегистрироваться</a></div>',
                        unsafe_allow_html=True)

        st.markdown('</div></div></div>', unsafe_allow_html=True)
        return

    st.markdown(f"""
    <div class="custom-header">
        <h1>📋 Task Manager Pro</h1>
        <div class="user-info">
            <span>👤 {st.session_state.username}</span>
            <div class="avatar">{st.session_state.username[0].upper()}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.markdown("---")
        nav_items = [
            ("📊 Дашборд", "dashboard"),
            ("✅ Задачи", "tasks"),
            ("📁 Проекты", "projects"),
            ("📈 Статистика", "stats")
        ]
        for label, page in nav_items:
            is_active = st.session_state.page == page
            if st.button(label, key=f"nav_{page}", use_container_width=True):
                navigate_to(page)

        st.markdown("---")
        if st.button("🚪 Выйти", key="logout_btn", use_container_width=True):
            logout()

    if st.session_state.page == "dashboard":
        from pages import dashboard
        dashboard.show(api_request)
    elif st.session_state.page == "tasks":
        from pages import tasks
        tasks.show(api_request)
    elif st.session_state.page == "projects":
        from pages import projects
        projects.show(api_request)
    elif st.session_state.page == "stats":
        from pages import stats
        stats.show(api_request)


if __name__ == "__main__":
    main()