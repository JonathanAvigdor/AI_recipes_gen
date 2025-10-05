import os
import streamlit as st
from web_scraper.scraper import scrape_ica_offers
from recipe_chain_module.recipe_chain import create_recipe_chain
from gmail_api.gmail_sender import get_gmail_service, create_message, send_message

# ---- Safe secrets load (works locally & on Cloud) ----
RUN_ENV = os.environ.get("RUN_ENV", "")
try:
    # On Streamlit Cloud this will exist; locally it may not
    RUN_ENV = st.secrets.get("RUN_ENV", RUN_ENV)
    # Pass OPENAI key to env for langchain_openai
    os.environ["OPENAI_API_KEY"] = st.secrets.get("OPENAI_API_KEY", os.environ.get("OPENAI_API_KEY", ""))
except Exception:
    pass

# IMPORTANT: write RUN_ENV back to environment so scraper.py can read it
os.environ["RUN_ENV"] = RUN_ENV or os.environ.get("RUN_ENV", "")
IS_CLOUD = (os.environ["RUN_ENV"].lower() == "cloud")

st.set_page_config(page_title="AI Recipe Generator", page_icon="🍝", layout="centered")
st.title("🍝 AI Recipe Generator (ICA Offers)")
mode_label = "🌐 Cloud mode (requests+bs4)" if IS_CLOUD else "💻 Local mode (Selenium preferred)"
st.caption(f"Paste your ICA store offers URL, preview deals, generate AI recipes + shopping list, and send to your email.  \n**Mode:** {mode_label}")

# -----------------------------
# Helpers
# -----------------------------
def _offers_to_text(offers):
    # offers is list of tuples (title, price)
    return "\n".join([f"{title}: {price}" for title, price in offers])

def _show_offers_table(offers):
    st.subheader("📦 Weekly Offers")
    st.dataframe(
        [{"Product": t, "Price/Deal": p} for t, p in offers],
        use_container_width=True
    )

def _show_ai_results(recipes_text: str, shopping_list_text: str):
    tab1, tab2 = st.tabs(["📖 Recipes", "🛒 Shopping List"])
    with tab1:
        st.markdown(f"```\n{recipes_text}\n```")
    with tab2:
        st.markdown(f"```\n{shopping_list_text}\n```")

# -----------------------------
# Form
# -----------------------------
with st.form("ica_form"):
    ica_url = st.text_input(
        "ICA store offers URL",
        placeholder="https://www.ica.se/erbjudanden/ica-xxxx-xxxxxxx/"
    )
    user_email = st.text_input(
        "Your email (to send results)",
        placeholder="name@example.com"
    )
    submitted = st.form_submit_button("Fetch Offers")

# -----------------------------
# Handle submit: scrape offers
# -----------------------------
if submitted:
    if not ica_url.strip():
        st.error("Please paste an ICA offers URL.")
    else:
        with st.spinner("Fetching weekly offers…"):
            try:
                offers = scrape_ica_offers(ica_url)
                if not offers:
                    st.warning("No offers found. Check the URL and try again.")
                else:
                    st.success(f"Found {len(offers)} offers")
                    st.session_state["offers"] = offers
                    st.session_state["user_email"] = user_email.strip()
                    # Clear previous AI results if URL changed
                    st.session_state.pop("recipes_text", None)
                    st.session_state.pop("shopping_list_text", None)
            except Exception as e:
                st.error(f"Error while scraping: {e}")

# -----------------------------
# Show offers (if available)
# -----------------------------
if "offers" in st.session_state and st.session_state["offers"]:
    _show_offers_table(st.session_state["offers"])

    # Button to generate AI results (keeps costs under control)
    if st.button("🤖 Generate Recipes & Shopping List"):
        offers_text = _offers_to_text(st.session_state["offers"])
        with st.spinner("Generating recipes and shopping list with AI…"):
            try:
                run_chain = create_recipe_chain(model_name="gpt-4o", temperature=0.2)
                out = run_chain(offers_text)
                st.session_state["recipes_text"] = out["recipes"]
                st.session_state["shopping_list_text"] = out["shopping_list"]
                st.success("AI generation complete ✅")
            except Exception as e:
                st.error(f"AI generation failed: {e}")

# -----------------------------
# Show AI results (if available)
# -----------------------------
if st.session_state.get("recipes_text") and st.session_state.get("shopping_list_text"):
    _show_ai_results(st.session_state["recipes_text"], st.session_state["shopping_list_text"])

    # Email sending (hide on Cloud where Gmail OAuth won't work)
    user_email_saved = st.session_state.get("user_email", "").strip()
    if IS_CLOUD:
        st.info("Email sending is available on local runs. On Streamlit Cloud, Gmail OAuth is disabled.")
    else:
        if user_email_saved:
            if st.button("📧 Send to my email"):
                try:
                    service = get_gmail_service()
                    body = (
                        "Hi!\n\nHere are your AI-generated recipes and shopping list from ICA offers.\n\n"
                        "=== Recipes ===\n\n" + st.session_state["recipes_text"] +
                        "\n\n=== Shopping List ===\n\n" + st.session_state["shopping_list_text"] +
                        "\n\n— Sent automatically by your AI Recipe Generator"
                    )
                    msg = create_message(
                        sender="me",
                        to=user_email_saved,
                        subject="Your ICA-based recipes & shopping list",
                        message_text=body
                    )
                    send_message(service, "me", msg)
                    st.success("Email sent! 🎉 Check your inbox.")
                except Exception as e:
                    st.error(f"Email failed: {e}")
        else:
            st.info("Enter your email in the form above to enable the Send button.")
else:
    if "offers" not in st.session_state or not st.session_state["offers"]:
        st.info("Submit the form to preview offers.")
    else:
        st.info("Click “Generate Recipes & Shopping List” to create AI results.")
