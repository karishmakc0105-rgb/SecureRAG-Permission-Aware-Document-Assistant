
import streamlit as st
import requests

# ---------------- PAGE CONFIGURATION ----------------

st.set_page_config(
    page_title="SecureRAG | AI Document Assistant",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded"
)

API_URL = "http://127.0.0.1:8000"

# ---------------- CUSTOM CSS ----------------

st.markdown("""
<style>
.stApp {
    background-color: #F4F7FC;
}

.brand {
    color: #173B70;
    font-size: 38px;
    font-weight: 800;
    text-align: center;
}

.subtitle {
    color: #718096;
    text-align: center;
    font-size: 15px;
}

.stButton button {
    background-color: #173B70;
    color: white;
    border-radius: 9px;
    border: none;
    width: 100%;
    min-height: 42px;
    font-weight: 600;
}

.stButton button:hover {
    background-color: #24569A;
    color: white;
}

.profile-card {
    background: white;
    padding: 22px;
    border-radius: 12px;
    border: 1px solid #E1E8F0;
    margin-bottom: 12px;
}

.profile-label {
    color: #718096;
    font-size: 13px;
}

.profile-value {
    color: #173B70;
    font-size: 17px;
    font-weight: 650;
}
</style>
""", unsafe_allow_html=True)


# ---------------- SESSION STATE ----------------

defaults = {
    "access_token": None,
    "username": None,
    "profile": None,
    "messages": [],
    "page": "Chat"
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


def logout():
    st.session_state.access_token = None
    st.session_state.username = None
    st.session_state.profile = None
    st.session_state.messages = []
    st.session_state.page = "Chat"
    st.rerun()


def get_headers():
    return {
        "Authorization": f"Bearer {st.session_state.access_token}"
    }


# ---------------- PROFILE FETCH ----------------

def load_profile():

    if st.session_state.profile:
        return st.session_state.profile

    try:
        response = requests.get(
            f"{API_URL}/me",
            headers=get_headers(),
            timeout=10
        )

        if response.status_code == 200:
            st.session_state.profile = response.json()
            return st.session_state.profile

        elif response.status_code == 401:
            logout()

        else:
            st.error(f"Unable to load profile: {response.status_code}")

    except requests.exceptions.RequestException as e:
        st.error(f"Backend connection error: {e}")

    return None


# ---------------- LOGIN PAGE ----------------

def login_page():

    left, center, right = st.columns([1, 1.2, 1])

    with center:

        st.write("")
        st.write("")

        st.markdown(
            '<div class="brand">🔐 SecureRAG</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="subtitle">Permission-Aware AI Document Assistant</div>',
            unsafe_allow_html=True
        )

        st.write("")

        with st.container(border=True):

            st.markdown("### Welcome back")
            st.caption("Sign in to access your organization's secure AI assistant.")

            with st.form("login_form"):

                username = st.text_input(
                    "Username",
                    placeholder="Enter your username"
                )

                password = st.text_input(
                    "Password",
                    type="password",
                    placeholder="Enter your password"
                )

                submitted = st.form_submit_button(
                    "Sign in",
                    use_container_width=True
                )

            if submitted:

                if not username or not password:
                    st.warning("Please enter both username and password.")

                else:
                    try:
                        response = requests.post(
                            f"{API_URL}/login",
                            json={
                                "username": username,
                                "password": password
                            },
                            timeout=10
                        )

                        if response.status_code == 200:

                            data = response.json()

                            st.session_state.access_token = data["access_token"]
                            st.session_state.username = data["username"] if "username" in data else username
                            st.session_state.profile = None
                            st.session_state.messages = []
                            st.session_state.page = "Chat"

                            st.rerun()

                        elif response.status_code == 401:
                            st.error("Invalid username or password.")

                        else:
                            st.error(f"Login failed: {response.status_code}")

                    except requests.exceptions.RequestException as e:
                        st.error(f"Backend connection error: {e}")

        st.write("")

        st.markdown(
            "<p style='text-align:center;color:#8995A7;font-size:12px;'>"
            "Secure access • Role-based permissions • Tenant isolation"
            "</p>",
            unsafe_allow_html=True
        )


# ---------------- PROFILE PAGE ----------------

def profile_page(profile):

    st.title("👤 My Profile")
    st.caption("Your SecureRAG account information.")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            f"""
            <div class="profile-card">
                <div class="profile-label">Username</div>
                <div class="profile-value">{profile["username"]}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            f"""
            <div class="profile-card">
                <div class="profile-label">User ID</div>
                <div class="profile-value">{profile["user_id"]}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            f"""
            <div class="profile-card">
                <div class="profile-label">Organization / Tenant</div>
                <div class="profile-value">{profile["tenant_id"]}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        roles = ", ".join(profile["roles"])

        st.markdown(
            f"""
            <div class="profile-card">
                <div class="profile-label">Assigned Roles</div>
                <div class="profile-value">{roles}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.info(
        "Your document access is determined by your assigned organization "
        "and roles."
    )


# ---------------- ADMIN USER MANAGEMENT ----------------

def user_management_page():

    st.title("👥 User Management")
    st.caption("Register new users within your organization.")

    st.info(
        "New accounts will automatically belong to your organization. "
        "Only authorized non-admin roles can be assigned here."
    )

    with st.container(border=True):

        st.markdown("### Create a new account")

        with st.form("create_user_form"):

            new_username = st.text_input(
                "Username",
                placeholder="Enter a new username"
            )

            new_password = st.text_input(
                "Temporary password",
                type="password",
                placeholder="Minimum 8 characters"
            )

            selected_roles = st.multiselect(
                "Assign roles",
                options=["employee", "hr", "support", "security"],
                default=["employee"]
            )

            submitted = st.form_submit_button(
                "＋ Create user",
                use_container_width=True
            )

        if submitted:

            if not new_username.strip():
                st.warning("Please enter a username.")

            elif len(new_password) < 8:
                st.warning("Password must contain at least 8 characters.")

            elif not selected_roles:
                st.warning("Please select at least one role.")

            else:

                try:
                    response = requests.post(
                        f"{API_URL}/admin/users",
                        headers=get_headers(),
                        json={
                            "username": new_username.strip(),
                            "password": new_password,
                            "roles": selected_roles
                        },
                        timeout=15
                    )

                    if response.status_code == 200:

                        data = response.json()

                        st.success("User created successfully!")

                        st.write("**Account details**")
                        st.write(f"Username: {data['username']}")
                        st.write(f"User ID: {data['user_id']}")
                        st.write(f"Tenant: {data['tenant_id']}")
                        st.write(f"Roles: {', '.join(data['roles'])}")

                    elif response.status_code == 401:
                        st.error("Session expired. Please sign in again.")
                        logout()

                    elif response.status_code == 403:
                        st.error("You do not have permission to create users.")

                    elif response.status_code == 409:
                        st.error("This username already exists.")

                    else:
                        st.error(
                            f"Registration failed: {response.status_code} - "
                            f"{response.text}"
                        )

                except requests.exceptions.RequestException as e:
                    st.error(f"Backend connection error: {e}")


# ---------------- CHAT PAGE ----------------

def chat_page():

    st.title("SecureRAG Assistant 👋")

    st.caption(
        "Ask questions about your organization's accessible documents."
    )

    st.divider()

    if not st.session_state.messages:

        st.markdown("### How can I help you today?")

        st.write(
            "Ask a question and I'll retrieve relevant information "
            "from documents you are authorized to access."
        )

        col1, col2 = st.columns(2)

        with col1:
            st.info(
                "**HR information**\n\n"
                "How many annual leave days do Acme employees receive?"
            )

        with col2:
            st.info(
                "**Company policies**\n\n"
                "What are Acme's remote work rules?"
            )

    for message in st.session_state.messages:

        with st.chat_message(message["role"]):

            st.markdown(message["content"])

            if message["role"] == "assistant":

                if message.get("sources"):

                    with st.expander(
                        f"📚 View sources ({len(message['sources'])})"
                    ):

                        for source in message["sources"]:

                            st.markdown(f"**{source['title']}**")

                            st.caption(
                                f"Document ID: {source['doc_id']} "
                                f"| Relevance score: {source['score']}"
                            )

                            st.divider()

                if message.get("model"):
                    st.caption(f"Model: {message['model']}")

                if message.get("request_id"):
                    st.caption(f"Request ID: {message['request_id']}")

    question = st.chat_input("Ask something about your documents...")

    if question:

        st.session_state.messages.append({
            "role": "user",
            "content": question
        })

        with st.spinner("Searching your authorized documents..."):

            try:

                response = requests.post(
                    f"{API_URL}/ask",
                    headers=get_headers(),
                    json={
                        "question": question,
                        "top_k": 5
                    },
                    timeout=120
                )

                if response.status_code == 200:

                    data = response.json()

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": data["answer"],
                        "sources": data.get("sources", []),
                        "model": data.get("model"),
                        "request_id": data.get("request_id")
                    })

                elif response.status_code == 401:

                    st.error("Your session has expired. Please sign in again.")
                    logout()

                elif response.status_code == 403:

                    st.error("You are not authorized to perform this request.")

                else:

                    st.error(
                        f"Request failed: {response.status_code} - {response.text}"
                    )

            except requests.exceptions.RequestException as e:
                st.error(f"Unable to connect to SecureRAG: {e}")

        st.rerun()


# ---------------- MAIN DASHBOARD ----------------

def dashboard():

    profile = load_profile()

    if not profile:
        st.error("Unable to load your account. Please sign in again.")
        if st.button("Sign out"):
            logout()
        return

    is_admin = "admin" in profile["roles"]

    # Sidebar navigation
    with st.sidebar:

        st.markdown("## 🔐 SecureRAG")
        st.caption("Permission-Aware AI Assistant")

        st.divider()

        st.markdown("### 👤 Account")

        st.write(f"**{profile['username']}**")
        st.caption(f"Organization: {profile['tenant_id']}")

        st.success("Authenticated")

        st.divider()

        pages = ["Chat", "My Profile"]

        if is_admin:
            pages.append("User Management")

        selected_page = st.radio(
            "Navigation",
            pages,
            key="navigation_menu"
        )

        st.session_state.page = selected_page

        st.divider()

        st.markdown("### 💬 Workspace")

        if st.button("＋ New conversation", use_container_width=True):
            st.session_state.messages = []
            st.session_state.page = "Chat"
            st.rerun()

        st.caption(f"{len(st.session_state.messages)} messages")

        st.divider()

        if st.button("Sign out", use_container_width=True):
            logout()

        st.caption("SecureRAG • Demo version")

    # Display selected page
    if selected_page == "Chat":
        chat_page()

    elif selected_page == "My Profile":
        profile_page(profile)

    elif selected_page == "User Management" and is_admin:
        user_management_page()


# ---------------- APPLICATION ENTRY POINT ----------------

if st.session_state.access_token:
    dashboard()
else:
    login_page()
