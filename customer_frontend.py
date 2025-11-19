import streamlit as st
import requests
import pandas as pd
import json
import time

# ====================================
# ⚙️ CONFIGURATION
# ====================================
API_BASE_URL = "http://127.0.0.1:5000/api"


# ====================================
# 🔗 API HELPER FUNCTION
# ====================================
def api_request(method, endpoint, data=None, token=None, params=None):
    """Centralized API request handler with error handling."""
    url = f"{API_BASE_URL}/{endpoint}"
    headers = {'Authorization': f'Bearer {token}'} if token else {}

    try:
        resp = requests.request(method, url, headers=headers, json=data, params=params)
        resp.raise_for_status()
        return resp.json()

    except requests.exceptions.HTTPError as err:
        try:
            ej = err.response.json()
            msg = ej.get("error") or ej.get("msg") or err.response.text
            details = ej.get("details")
            st.error(f"API Error: {msg}" + (f" — {details}" if details else ""))
        except ValueError:
            st.error(f"API Error: {err.response.text}")
        return None

    except requests.exceptions.RequestException as err:
        st.error(f"Connection Error: {err}")
        return None


# ====================================
# 🔐 AUTHENTICATION
# ====================================
def show_auth_page():
    st.title("Welcome to MovieFlix ")
    auth_option = st.radio("Choose an option", ["Login", "Sign Up"])

    # --- LOGIN ---
    if auth_option == "Login":
        with st.form("login_form"):
            st.subheader("Customer Login")
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login")

            if submitted:
                response = api_request("post", "customer/login", data={"email": email, "password": password})
                if response and 'access_token' in response:
                    st.session_state.logged_in = True
                    st.session_state.token = response['access_token']
                    st.session_state.customer_name = response.get('first_name', 'Customer')
                    st.session_state.customer_id = response.get('customer_id')  # ✅ Add this
                    st.success("Login Successful!")
                    st.rerun()


    # --- SIGN UP ---
    elif auth_option == "Sign Up":
        with st.form("signup_form"):
            st.subheader("Create a New Account")
            first_name = st.text_input("First Name")
            last_name = st.text_input("Last Name")
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Sign Up")

            if submitted:
                signup_data = {
                    "first_name": first_name,
                    "last_name": last_name,
                    "email": email,
                    "password": password
                }
                response = api_request("post", "customer/signup", data=signup_data)
                if response:
                    st.success(response.get("message", "Signup successful! Please log in."))


# ====================================
# 🚪 LOGOUT
# ====================================
def logout():
    st.session_state.clear()
    st.success("Logged out successfully.")
    st.rerun()


import streamlit as st
import time

def show_movie_catalog():
    st.title("🎬 Movie Catalog")
    token = st.session_state.get("token")

    # --- 🔍 Live Search ---
    def clear_search():
        st.session_state.search_input = ""
        st.rerun()

    col1, col2 = st.columns([10, 1])
    with col1:
        search = st.text_input(
            "🔍 Search by title",
            key="search_input",
            placeholder="Type a movie title..."
        )
    with col2:
        st.button("❌", help="Clear search", use_container_width=True, on_click=clear_search)

    # --- Debounce ---
    if "last_search" not in st.session_state:
        st.session_state.last_search = ""
    if search != st.session_state.last_search:
        st.session_state.last_search = search
        time.sleep(0.25)
        st.rerun()

    # --- Fetch Movies ---
    params = {"q": search} if search else None
    movies = api_request("get", "catalog", token=token, params=params)

    if not movies:
        st.info("No movies found.")
        return

    # --- Display Movie Grid ---
    cols = st.columns(3)
    for i, movie in enumerate(movies):
        with cols[i % 3]:
            with st.container(border=True):
                # --- Movie Poster ---
                poster_url = movie.get("poster_url") or "https://via.placeholder.com/400x600?text=No+Image"
                if not poster_url.startswith("http"):
                    poster_url = "https://via.placeholder.com/400x600?text=No+Image"
                st.image(poster_url, use_container_width=True, caption=movie.get("title", "Untitled"))

                # --- Movie Info ---
                rating = movie.get('rating', 0)
                count = movie.get('review_count', 0)
                price = float(movie.get("price") or 0.0)  # ✅ Ensures DB price shows correctly

                st.caption(f"{movie.get('genre', 'Unknown')} | {movie.get('release_year', '')}")
                st.write(movie.get("description", "No description.")[:100] + "...")
                st.markdown(
                    f"<p style='color:#FFD700'><b>💰 Price:</b> ₹{price:.2f}</p>",
                    unsafe_allow_html=True
                )

                # --- Rent Button ---
                if st.button("🎟️ Rent Now", key=f"rent_{movie['id']}", use_container_width=True, type="primary"):
                    st.session_state[f"show_confirm_{movie['id']}"] = True

                # --- Rent Confirmation Popup ---
                if st.session_state.get(f"show_confirm_{movie['id']}", False):
                    st.markdown(
                        f"""
                        <div style="
                            display: flex;
                            justify-content: center;
                            align-items: center;
                            margin-top: 20px;
                            margin-bottom: 10px;">
                            <div style="
                                background-color: #1E1E1E;
                                border: 2px solid #FFD700;
                                border-radius: 16px;
                                padding: 25px 20px;
                                width: 85%;
                                box-shadow: 0 0 25px rgba(255,215,0,0.6);
                                text-align: center;
                                color: white;
                                transition: all 0.3s ease;">
                                <h4 style='color:#FFD700; margin-bottom:5px;'>Confirm Rent — {movie['title']}</h4>
                                <p>💵 <b>Price:</b> ₹{price:.2f}</p>
                                <p style="margin-bottom: 20px;">Confirm your payment below:</p>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                    # --- Buttons Row ---
                    confirm_col, cancel_col = st.columns(2)
                    with confirm_col:
                        if st.button("✅ Confirm Payment", key=f"confirm_{movie['id']}", use_container_width=True):
                            with st.spinner("Processing payment... 💳"):
                                time.sleep(1.5)

                            rent_res = api_request(
                                "post", "customer/checkout",
                                token=token,
                                data={"movie_ids": [movie["id"]], "method": "Card"}
                            )

                            if rent_res:
                                st.success(f"✅ Payment Successful! Enjoy '{movie['title']}' 🎬")
                                st.session_state[f"show_confirm_{movie['id']}"] = False
                                time.sleep(1.5)
                                st.rerun()
                            else:
                                st.error("Payment failed. Please try again.")

                    with cancel_col:
                        if st.button("❌ Cancel", key=f"cancel_{movie['id']}", use_container_width=True):
                            st.session_state[f"show_confirm_{movie['id']}"] = False
                            st.info("Payment cancelled.")

                # --- Reviews Section ---
                with st.expander("See Reviews"):
                    if count > 0:
                        reviews = api_request("get", f"movies/{movie['id']}/reviews", token=token)
                        if reviews:
                            for r in reviews:
                                reviewer = r.get('reviewer', 'Anonymous')
                                date = r.get('date', 'Unknown Date')
                                rating_val = int(r.get('rating', 0))
                                comment = r.get('comment', '')
                                st.markdown(f"**{reviewer}** — {date}")
                                st.caption("⭐" * rating_val)
                                st.write(comment)
                                st.divider()
                        else:
                            st.info("No reviews found.")
                    else:
                        st.info("No reviews yet for this movie.")

import streamlit as st
import time

# def show_my_rentals_page():
#     st.title("📜 My Rentals")
#     token = st.session_state.get("token")

#     rentals = api_request("get", "customer/rentals", token=token)

#     if not rentals:
#         st.info("You haven't rented any movies yet.")
#         return

#     for rental in rentals:
#         st.subheader(f"Rental #{rental.get('id', '?')} — {rental.get('rental_date', 'Unknown Date')}")
#         st.caption(f"Return by: {rental.get('due_date', 'N/A')}")

#         movies = rental.get("movies", [])
#         for movie in movies:
#             col1, col2 = st.columns([1, 3])

#             with col1:
#                 poster_url = movie.get("poster_url", "https://via.placeholder.com/200x300?text=No+Image")
#                 st.image(poster_url, width=120)

#             with col2:
#                 title = movie.get("title", "Unknown Title")
#                 rental_item_id = movie.get("rental_item_id")
#                 returned = movie.get("returned", False)
#                 returned_at = movie.get("returned_at")

#                 st.markdown(f"🎬 **{title}**")
#                 st.caption(movie.get("genre", "Unknown Genre"))
#                 st.markdown(f"💰 **Price:** ₹{movie.get('price', 0):.2f}")
#                 st.write(movie.get("description", "No description available.")[:120] + "...")

#                 # ✅ If returned, show status instead of button
#                 if returned:
#                     st.success(f"✅ Returned on {returned_at or 'N/A'}")
#                 else:
#                     # --- Return Button ---
#                     if st.button(
#                         f"🔙 Return '{title}'",
#                         key=f"return_{rental.get('id', '?')}_{rental_item_id}",
#                         use_container_width=True,
#                         type="primary",
#                     ):
#                         if not rental_item_id:
#                             st.error("⚠️ Missing rental_item_id. Cannot process return.")
#                         else:
#                             with st.spinner(f"Processing return for '{title}'..."):
#                                 time.sleep(1.2)

#                             return_response = api_request(
#                                 "post", "returns",  # your backend route
#                                 token=token,
#                                 data={"rental_item_id": rental_item_id}
#                             )

#                             if return_response and "message" in return_response:
#                                 late_fee = return_response.get("late_fee_charged", 0.0)
#                                 if late_fee > 0:
#                                     st.warning(f"Returned with ₹{late_fee:.2f} late fee.")
#                                 else:
#                                     st.success(f"✅ '{title}' returned successfully!")
#                                 time.sleep(1)
#                                 st.rerun()
#                             else:
#                                 st.error("❌ Failed to return movie. Please try again later.")

#         st.markdown("---")

def show_my_rentals_page():
    st.title("📜 My Rentals")
    token = st.session_state.get("token")

    rentals = api_request("get", "customer/rentals", token=token)

    if not rentals:
        st.info("You haven't rented any movies yet.")
        return

    for rental in rentals:
        st.subheader(f"Rental #{rental.get('id', '?')} — {rental.get('rental_date', 'Unknown Date')}")
        st.caption(f"Return by: {rental.get('due_date', 'N/A')}")

        movies = rental.get("movies", [])
        for movie in movies:
            col1, col2 = st.columns([1, 3])

            with col1:
                poster_url = movie.get("poster_url", "https://via.placeholder.com/200x300?text=No+Image")
                st.image(poster_url, width=120)

            with col2:
                title = movie.get("title", "Unknown Title")
                rental_item_id = movie.get("rental_item_id")
                returned = movie.get("returned", False)
                returned_at = movie.get("returned_at")

                st.markdown(f"🎬 **{title}**")
                st.caption(movie.get("genre", "Unknown Genre"))
                st.markdown(f"💰 **Price:** ₹{movie.get('price', 0):.2f}")
                st.write(movie.get("description", "No description available.")[:120] + "...")

                # ✅ If returned, show status instead of button
                if returned:
                    st.success(f"✅ Returned on {returned_at or 'N/A'}")

                    # --- Late Fee Button ---
                    if st.button(f"💰 Check Late Fee for Rental #{rental.get('id')}", key=f"fee_{rental.get('id')}"):
                        fee_res = api_request("get", f"customer/late_fee/{rental.get('id')}", token=token)
                        if fee_res and "late_fee" in fee_res:
                            fee = fee_res["late_fee"]
                            if fee > 0:
                                st.warning(f"⚠️ Late Fee Due: ₹{fee:.2f}")
                            else:
                                st.info("✅ No late fee for this rental.")
                        else:
                            st.error("❌ Unable to fetch late fee. Please try again later.")

                else:
                    # --- Return Button ---
                    if st.button(
                        f"🔙 Return '{title}'",
                        key=f"return_{rental.get('id', '?')}_{rental_item_id}",
                        use_container_width=True,
                        type="primary",
                    ):
                        if not rental_item_id:
                            st.error("⚠️ Missing rental_item_id. Cannot process return.")
                        else:
                            with st.spinner(f"Processing return for '{title}'..."):
                                time.sleep(1.2)

                            return_response = api_request(
                                "post", "returns",  # your backend route
                                token=token,
                                data={"rental_item_id": rental_item_id}
                            )

                            if return_response and "message" in return_response:
                                late_fee = return_response.get("late_fee_charged", 0.0)
                                if late_fee > 0:
                                    st.warning(f"Returned with ₹{late_fee:.2f} late fee.")
                                else:
                                    st.success(f"✅ '{title}' returned successfully!")
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error("❌ Failed to return movie. Please try again later.")

        st.markdown("---")



# ====================================
# ⭐ POST REVIEW
# ====================================
def show_post_review_page():
    st.title("⭐ Rate a Movie")
    token = st.session_state.get("token")

    # === Fetch movie catalog ===
    movies = api_request("get", "catalog", token=token)
    if not movies:
        st.error("Could not load movie list.")
        return

    movie_titles = {m["title"]: m["id"] for m in movies}
    selected_title = st.selectbox("🎬 Choose a movie", list(movie_titles.keys()))
    movie_id = movie_titles[selected_title]

    # === Review submission form ===
    with st.container(border=True):
        st.subheader("📝 Post Your Review")
        with st.form("review_form", clear_on_submit=True):
            rating = st.slider("Rating", 1, 5, 5)
            comment = st.text_area("Comment", placeholder="What did you like or dislike?")
            submitted = st.form_submit_button("Submit Review", type="primary")

            if submitted:
                if not comment.strip():
                    st.warning("Please write a comment before submitting.")
                else:
                    res = api_request(
                        "post", "customer/review",
                        token=token,
                        data={"movie_id": movie_id, "rating": rating, "comment": comment}
                    )
                    if res:
                        st.success("✅ Thank you for your review!")
                        time.sleep(1)
                        st.rerun()

    # === Show existing reviews ===
    st.subheader(f"💬 Reviews for '{selected_title}'")
    reviews = api_request("get", f"movies/{movie_id}/reviews", token=token)

    if not reviews:
        st.info("No reviews yet. Be the first to review this movie!")
        return

    current_user = st.session_state.get("customer_name", "").split()[0]  # e.g., "Alice" from "Alice K."
    for r in reviews:
        reviewer = r.get("reviewer", "Anonymous")
        review_id = r.get("id")
        stars = "⭐" * int(r.get("rating", 0))
        date = r.get("date", "Unknown Date")
        comment = r.get("comment", "")
        review_owner_id = r.get("customer_id")

        with st.container(border=True):
            col1, col2 = st.columns([6, 1])
            with col1:
                st.markdown(f"**{reviewer}** — {date}")
                st.caption(f"{stars} ({r.get('rating', 0)}/5)")
                st.write(comment)
            with col2:
                # ✅ Only show delete button for logged-in user's own reviews
                if review_owner_id == st.session_state.get("customer_id"):
                    if st.button("🗑️ Delete", key=f"del_{review_id}", use_container_width=True):
                        st.warning("Are you sure you want to delete this review?")
                        confirm_col1, confirm_col2 = st.columns(2)
                        with confirm_col1:
                            if st.button("✅ Yes", key=f"yes_{review_id}"):
                                res = api_request("delete", f"customer/review/{review_id}", token=token)
                                if res:
                                    st.success(res.get("message", "Review deleted successfully!"))
                                    time.sleep(1)
                                    st.rerun()
                        with confirm_col2:
                            if st.button("❌ Cancel", key=f"no_{review_id}"):
                                st.info("Deletion cancelled.")



# ====================================
# 💳 PAYMENT HISTORY
# ====================================
def show_payment_history_page():
    st.title("💳 Payment History")
    token = st.session_state.get("token")
    payments = api_request("get", "customer/payments", token=token)

    if not payments:
        st.info("No payments found.")
        return

    df = pd.DataFrame(payments)
    st.dataframe(df[["id", "amount", "method", "payment_date"]])


# ====================================
# 🧭 MAIN NAVIGATION
# ====================================
def main():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        show_auth_page()
    else:
        st.sidebar.title(f"Welcome, {st.session_state.customer_name}! 👋")
        page = st.sidebar.radio("Navigate", [
            "Movie Catalog",
            "My Rentals",
            "Post Review",
            "Payment History"
        ])
        st.sidebar.button("Logout", on_click=logout)

        if page == "Movie Catalog":
            show_movie_catalog()
        elif page == "My Rentals":
            show_my_rentals_page()
        elif page == "Post Review":
            show_post_review_page()
        elif page == "Payment History":
            show_payment_history_page()


# ====================================
# 🚀 RUN APP
# ====================================
if __name__ == "__main__":
    main()
