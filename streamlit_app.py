import streamlit as st
import json
from transformers import pipeline

# Load the menu data
def load_menu():
    try:
        with open('menu.json', 'r') as file:
            return json.load(file)
    except Exception as e:
        st.error(f"Error loading menu data: {e}")
        return {}

def save_menu(menu_data):
    try:
        with open('menu.json', 'w') as file:
            json.dump(menu_data, file, indent=4)
    except Exception as e:
        st.error(f"Error saving menu data: {e}")

menu_data = load_menu()

# Initialize the chatbot
chatbot = pipeline('text-generation', model='microsoft/DialoGPT-medium')

# Function to get a response from the chatbot
def get_response(input_text):
    global menu_data
    input_text_lower = input_text.lower()
    
    # Check if the user is asking for the menu or a specific price
    if 'menu' in input_text_lower:
        response = "Today's menu:\n" + "\n".join([f"{item}: ${price}" for item, price in menu_data.get('menu', {}).items()])
    elif any(item.lower() in input_text_lower for item in menu_data.get('menu', {})):
        item_name = next(item for item in menu_data['menu'] if item.lower() in input_text_lower)
        response = f"The price of {item_name} is ${menu_data['menu'][item_name]}"
    elif 'timings' in input_text_lower:
        response = "Restaurant timings:\n" + "\n".join([f"{day}: {time}" for day, time in menu_data.get('timings', {}).items()])
    elif 'location' in input_text_lower or 'place' in input_text_lower:
        response = f"The restaurant is located at: {menu_data.get('location', 'Not specified')}"
    elif 'contact' in input_text_lower:
        contact_info = menu_data.get('contact', {})
        response = f"Contact us at:\nPhone: {contact_info.get('phone', 'Not specified')}\nEmail: {contact_info.get('email', 'Not specified')}\nWebsite: {contact_info.get('website', 'Not specified')}"
    elif 'specials' in input_text_lower:
        response = "Today's specials:\n" + "\n".join([f"{day}: {special}" for day, special in menu_data.get('specials', {}).items()])
    elif 'order' in input_text_lower:
        response = "Sure, you can place your order. Please specify the items and quantities."
    else:
        response = chatbot(input_text, max_length=50, truncation=True)[0]['generated_text']
    
    return response

# Streamlit interface
st.title("Restaurant Chatbot")

# Chat section
st.header("Chat with the Bot")
user_input = st.text_input("You:", "What is on the menu?")
if st.button("Send"):
    response = get_response(user_input)
    st.text_area("Chatbot:", value=response, height=200, max_chars=None, key=None)

# Update menu section
st.header("Update Menu")
menu_item = st.text_input("Menu Item:")
menu_price = st.number_input("Price:", min_value=0.0, step=0.01)

if st.button("Update Menu"):
    if menu_item and menu_price >= 0:
        menu_data.setdefault('menu', {})[menu_item] = menu_price
        save_menu(menu_data)
        st.success(f"Menu updated with {menu_item}: ${menu_price}")

# Update timings section
st.header("Update Restaurant Timings")
timings = {}
for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]:
    timings[day] = st.text_input(f"{day}:", value=menu_data.get('timings', {}).get(day, ''))
if st.button("Update Timings"):
    menu_data['timings'] = timings
    save_menu(menu_data)
    st.success("Restaurant timings updated")

# Update location section
st.header("Update Restaurant Location")
restaurant_location = st.text_input("Restaurant Location:", value=menu_data.get('location', ''))
if st.button("Update Location"):
    menu_data['location'] = restaurant_location
    save_menu(menu_data)
    st.success(f"Restaurant location updated to: {restaurant_location}")

# Update contact section
st.header("Update Restaurant Contact Info")
contact_phone = st.text_input("Phone:", value=menu_data.get('contact', {}).get('phone', ''))
contact_email = st.text_input("Email:", value=menu_data.get('contact', {}).get('email', ''))
contact_website = st.text_input("Website:", value=menu_data.get('contact', {}).get('website', ''))
if st.button("Update Contact Info"):
    menu_data['contact'] = {
        "phone": contact_phone,
        "email": contact_email,
        "website": contact_website
    }
    save_menu(menu_data)
    st.success("Restaurant contact information updated")

# Update specials section
st.header("Update Daily Specials")
specials = {}
for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]:
    specials[day] = st.text_input(f"{day} Special:", value=menu_data.get('specials', {}).get(day, ''))
if st.button("Update Specials"):
    menu_data['specials'] = specials
    save_menu(menu_data)
    st.success("Daily specials updated")

# Display current menu
st.header("Current Menu")
st.json(menu_data.get('menu', {}))

# Display restaurant timings
st.header("Restaurant Timings")
st.json(menu_data.get('timings', {}))

# Display restaurant location
st.header("Restaurant Location")
st.write(menu_data.get('location', 'Not set'))

# Display restaurant contact information
st.header("Restaurant Contact Information")
st.write(menu_data.get('contact', 'Not set'))

# Display daily specials
st.header("Daily Specials")
st.json(menu_data.get('specials', {}))

# Order taking section
st.header("Place an Order")
order_details = st.text_area("Order Details:", "Item1: Quantity, Item2: Quantity, ...")
if st.button("Place Order"):
    st.success(f"Your order has been placed: {order_details}")
