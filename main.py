from web_scraper import scrape_ica_offers
from recipe_chain_module import create_recipe_chain
from gmail_api import get_gmail_service, create_message, send_message

# 1. Scrape ICA for groceries
url = "https://www.ica.se/erbjudanden/ica-supermarket-aptiten-1003988/"
offers = scrape_ica_offers(url)

# cleaning up the offers into readble format
offers_text = "\n".join([f"{title}: {price}" for title, price in offers])

# 2. Generate recipes and shopping list
recipe_chain = create_recipe_chain(model_name="gpt-4o", temperature=0.2)
output = recipe_chain(offers_text)

recipes_text = output["recipes"]
shopping_list_text = output["shopping_list"]

# 3. Prepare email body
email_body = f"""
Hi there,

This is your Ai speaking, I've generated some recipes and a shopping list based on the current offers at ICA.

=== Recipes ===
{recipes_text}

=== Shopping List ===
{shopping_list_text}
"""

# 4. Send email
service = get_gmail_service()
msg = create_message(sender="johnavigdor@gmail.com",
                      to="johnavigdor@gmail.com",
                      subject="Your Weekly Recipes and Shopping List",
                      message_text=email_body)
send_message(service, "me", msg)