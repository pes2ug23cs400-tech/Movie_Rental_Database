# frontend.py

import streamlit as st
import requests
import pandas as pd

# --- CONFIGURATION ---
API_BASE_URL = "http://127.0.0.1:5000/api"

# --- HELPER FUNCTIONS FOR API INTERACTION ---

def get_auth_header():
    """Returns the authorization header if a token is available."""
    if 'token' in st.session_state and st.session_state.token:
        return {'Authorization': f'Bearer {st.session_state.token}'}
    return {}



def api_request(method, endpoint, json=None, is_login=False):
    """A centralized function to make API requests with safer error handling."""
    url = f"{API_BASE_URL}/{endpoint}"
    headers = {} if is_login else get_auth_header()

    try:
        response = requests.request(method, url, headers=headers, json=json)

        # If unauthorized, tell the user explicitly
        if response.status_code == 401:
            st.error("Unauthorized: Your session may have expired. Please log in again.")
            st.session_state.logged_in = False
            st.session_state.token = None
            st.rerun()

        # Raise HTTPError for other bad responses
        response.raise_for_status()

        # Return JSON safely if possible
        try:
            return response.json()
        except ValueError:
            # Handle cases where backend didn't return valid JSON
            st.error(f"Unexpected non-JSON response from API ({response.status_code}): {response.text}")
            return None

    except requests.exceptions.HTTPError as err:
        # Try to extract structured error info if possible
        try:
            error_json = err.response.json()
            msg = error_json.get("msg") or error_json.get("error") or str(error_json)
        except ValueError:
            msg = err.response.text or str(err)
        st.error(f"API Error [{err.response.status_code}]: {msg}")

    except requests.exceptions.RequestException as err:
        st.error(f"Connection Error: {err}")

    return None


# --- AUTHENTICATION PAGES ---

def show_login_page():
    """Displays the login form."""
    st.subheader("Staff Login")
    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")

        if submitted:
            response = api_request("post", "login", json={"email": email, "password": password}, is_login=True)
            if response and 'access_token' in response:
                st.session_state.logged_in = True
                st.session_state.token = response['access_token']
                st.session_state.role = response.get('role', 'Staff').lower()
                st.success("Login Successful!")
                st.rerun() # Rerun the script to reflect the logged-in state
            else:
                st.session_state.logged_in = False
                if not st.session_state.get('error_displayed'):
                     # This check avoids showing the default error from api_request and a specific one here
                    st.error("Invalid email or password.")
                    st.session_state.error_displayed = True # A flag to avoid double error messages


def logout():
    """Logs the user out by clearing session state."""
    st.session_state.logged_in = False
    st.session_state.token = None
    st.session_state.role = None
    st.success("You have been logged out.")
    st.rerun()


# --- UI RENDERING FUNCTIONS FOR CRUD OPERATIONS ---

def render_management_page(title, endpoint, columns, required_fields, manager_only=False):
    """
    A generic function to render a CRUD management page.
    Args:
        title (str): The title of the page.
        endpoint (str): The API endpoint (e.g., 'customers').
        columns (dict): A dictionary mapping database field names to user-friendly names.
        required_fields (list): A list of fields required for creation.
        manager_only (bool): If True, restricts access to managers.
    """
    if manager_only and st.session_state.role != 'manager':
        st.warning("You do not have permission to access this page.")
        return
        
    st.title(f"Manage {title}")

    # --- Display Data ---
    st.subheader(f"All {title}")
    data = api_request("get", endpoint)
    if data is not None:
        if data:
            df = pd.DataFrame(data)
            display_cols = [col for col in columns.keys() if col in df.columns]
            st.dataframe(df[display_cols].rename(columns=columns))
        else:
            st.info(f"No {title} found.")

    col1, col2 = st.columns(2)

    # --- Create Form ---
    with col1:
        st.subheader(f"Add New {title[:-1]}")
        with st.form(f"add_{endpoint}", clear_on_submit=True):
            inputs = {field: st.text_input(label) for field, label in columns.items() if field != 'id'}
            submitted = st.form_submit_button(f"Add {title[:-1]}")
            
            if submitted:
                # Basic validation
                if all(inputs.get(field) for field in required_fields):
                    api_request("post", endpoint, json=inputs)
                    st.success(f"{title[:-1]} added successfully!")
                    st.rerun()
                else:
                    st.warning(f"Please fill in all required fields: {', '.join(required_fields)}")

    # --- Update/Delete Form ---
    with col2:
        st.subheader(f"Update/Delete {title[:-1]}")
        if data:
            item_ids = [item['id'] for item in data]
            selected_id = st.selectbox(f"Select {title[:-1]} ID to manage", options=item_ids)
            selected_item = next((item for item in data if item['id'] == selected_id), None)

            if selected_item:
                with st.form(f"update_{endpoint}"):
                    update_inputs = {
                        field: st.text_input(label, value=selected_item.get(field, '')) 
                        for field, label in columns.items() if field != 'id'
                    }
                    
                    update_submitted = st.form_submit_button(f"Update {title[:-1]}")
                    delete_submitted = st.form_submit_button(f"DELETE {title[:-1]}", help=f"This will permanently delete the selected {title[:-1]}.")

                    if update_submitted:
                        api_request("put", f"{endpoint}/{selected_id}", json=update_inputs)
                        st.success(f"{title[:-1]} updated successfully!")
                        st.rerun()
                    
                    if delete_submitted:
                        api_request("delete", f"{endpoint}/{selected_id}")
                        st.success(f"{title[:-1]} deleted successfully!")
                        st.rerun()


def render_rentals_page():
    st.title("Manage Rentals")
    rentals = api_request("get", "rentals")
    if not rentals:
        st.info("No rentals found.")
        return

    filter_status = st.radio("Filter:", ["Active Only", "All History"], horizontal=True)
    rentals.sort(key=lambda x: x['id'], reverse=True)

    for rental in rentals:
        is_active_rental = rental.get('return_date') is None
        if filter_status == "Active Only" and not is_active_rental:
            continue

        with st.container(border=True):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.subheader(f"Rental #{rental['id']}")
                st.caption(f"Customer ID: {rental.get('customer_id')} | Rented: {rental.get('rental_date')}")

            # Show each item in the rental
            if 'items' in rental and rental['items']:
                st.write("---")
                for item in rental['items']:
                    ic1, ic2, ic3 = st.columns([3, 2, 2])
                    with ic1:
                        # You might need to fetch movie details if your API doesn't provide title here
                        st.write(f"**Inventory ID:** {item.get('inventory_id')}")
                    with ic2:
                        if item.get('returned'):
                            st.markdown("✅ Returned")
                        else:
                            st.markdown("⏳ **Active**")
                    with ic3:
                        # Show return button ONLY if item is NOT yet returned
                        if not item.get('returned'):
                            if st.button("📥 Return Item", key=f"ret_item_{item['rental_item_id']}", type="primary"):
                                with st.spinner("Processing..."):
                                    # THIS FIXES THE ERROR: Sending 'rental_item_id' as expected by routes.py
                                    res = api_request("post", "returns", json={"rental_item_id": item['rental_item_id']})
                                    if res:
                                        st.success("Item returned!")
                                        time.sleep(1)
                                        st.rerun()
            else:
                st.warning("No items found for this rental record.")

# --- MAIN APP LOGIC ---
def main():
    st.set_page_config(page_title="Movie Rental System", layout="wide")

    # Initialize session state variables if they don't exist
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'token' not in st.session_state:
        st.session_state.token = None
    if 'role' not in st.session_state:
        st.session_state.role = None


    if not st.session_state.logged_in:
        show_login_page()
    else:
        st.sidebar.title("Navigation")
        st.sidebar.write(f"Welcome, {st.session_state.role.capitalize()}!")
        st.sidebar.button("Logout", on_click=logout)

        # Define pages available to all staff
        pages = {
            "Customers": lambda: render_management_page("Customers", "customers", 
                                                      {"id": "ID", "first_name": "First Name", "last_name": "Last Name", "email": "Email", "phone": "Phone", "address": "Address"},
                                                      ["first_name", "last_name", "email"]),
            "Movies": lambda: render_management_page("Movies", "movies",
                                                   {"id": "ID", "title": "Title", "description": "Description", "release_year": "Release Year", "genre_id": "Genre ID", "format_id": "Format ID"},
                                                   ["title", "genre_id"]),
            "Rentals": lambda: render_rentals_page(),
            # Add other staff pages here if needed (e.g., Rentals, Inventory)
        }
        
        # Add manager-only pages
        if st.session_state.role == 'manager':
            manager_pages = {
                "Staff": lambda: render_management_page("Staff", "staff",
                                                      {"id": "ID", "first_name": "First Name", "last_name": "Last Name", "email": "Email", "phone": "Phone", "role_id": "Role ID", "password": "Password"},
                                                      ["first_name", "last_name", "email", "password", "role_id"], manager_only=True),
                "Genres": lambda: render_management_page("Genres", "genres", 
                                                        {"id": "ID", "name": "Name", "description": "Description"}, 
                                                        ["name"], manager_only=True),
                "Formats": lambda: render_management_page("Formats", "formats", 
                                                         {"id": "ID", "name": "Name", "description": "Description"}, 
                                                         ["name"], manager_only=True),
                "Roles": lambda: render_management_page("Roles", "roles", 
                                                       {"id": "ID", "name": "Name", "description": "Description"}, 
                                                       ["name"], manager_only=True),
                 "Membership Tiers": lambda: render_management_page("Membership Tiers", "membership-tiers",
                                                        {"id": "ID", "name": "Name", "description": "Description", "rental_limit": "Rental Limit", "rental_period_days": "Rental Period (Days)", "price": "Price"},
                                                        ["name", "price"], manager_only=True),
            }
            pages.update(manager_pages)

        selection = st.sidebar.radio("Go to", list(pages.keys()))
        
        # Call the function corresponding to the selection
        page_function = pages[selection]
        page_function()

if __name__ == "__main__":
    main()