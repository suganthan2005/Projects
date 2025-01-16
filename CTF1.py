import streamlit as st
from dataclasses import dataclass
import json
import matplotlib.pyplot as plt
import numpy as np
from datetime import date, timedelta
import os

# Goals
Calorie_Goal_limit = 3000
Protien_goal = 180
Fat_goal = 80
Carbs_goal = 300

# File paths
credentials_file = "users.json"
predefined_foods_file = "predefined_foods.json"

# Load predefined foods
try:
    with open(predefined_foods_file, "r") as file:
        predefined_foods = json.load(file)
except (FileNotFoundError, json.JSONDecodeError):
    predefined_foods = {
        "Rice (100g)": [130, 2, 0, 28],
        "Chicken Breast (100g)": [165, 31, 3, 0],
        "Apple (1 medium)": [95, 0, 0, 25],
        "Milk (1 cup)": [150, 8, 8, 12],
        "Egg (1)": [70, 6, 5, 1],
        "Banana (1 medium)": [105, 1, 0, 27],
        "Broccoli (100g)": [55, 4, 0, 11],
        "Salmon (100g)": [208, 20, 13, 0],
        "Potato (1 medium, 150g)": [110, 3, 0, 26],
        "Almonds (30g, ~23 nuts)": [160, 6, 14, 6],
        "Cheese (1 slice, 28g)": [113, 7, 9, 1],
        "Peanut Butter (2 tbsp)": [190, 8, 16, 6],
        "Oatmeal (1 cup, cooked)": [150, 6, 3, 27],
        "Avocado (1 medium)": [240, 3, 22, 12],
        "Greek Yogurt (1 cup)": [100, 10, 0, 6],
        "Dark Chocolate (28g)": [170, 2, 12, 14],
        "Tofu (100g)": [76, 8, 4, 2]
    }
    with open(predefined_foods_file, "w") as file:
        json.dump(predefined_foods, file, indent=4)

# Function to load credentials
def load_credentials():
    if not os.path.exists(credentials_file):
        with open(credentials_file, "w") as file:
            json.dump({}, file, indent=4)
        return {}
    
    try:
        with open(credentials_file, "r") as file:
            data = json.load(file)
            if isinstance(data, dict):
                return data
            else:
                st.error("Credentials file is not a valid dictionary. Resetting it.")
                with open(credentials_file, "w") as file:
                    json.dump({}, file, indent=4)
                return {}
    except (json.JSONDecodeError, ValueError):
        st.error("Error reading credentials file. Resetting it.")
        with open(credentials_file, "w") as file:
            json.dump({}, file, indent=4)
        return {}

# Function to save credentials
def save_credentials(credentials):
    with open(credentials_file, "w") as file:
        json.dump(credentials, file, indent=4)

# Load user credentials
credentials = load_credentials()

# Dataclass for food
@dataclass
class Food:
    name: str
    calories: int
    protien: int
    fat: int
    carbs: int

# Initialize session state
if "current_user" not in st.session_state:
    st.session_state.current_user = None
if "today" not in st.session_state:
    st.session_state.today = []

# Login/Signup
st.sidebar.title("User Authentication")
auth_mode = st.sidebar.radio("Choose mode", ["Login", "Signup"])

if auth_mode == "Signup":
    new_username = st.sidebar.text_input("Choose a username")
    new_password = st.sidebar.text_input("Choose a password", type="password")
    if st.sidebar.button("Signup"):
        if new_username in credentials:
            st.sidebar.error("Username already exists. Please choose a different username.")
        else:
            credentials[new_username] = {
                "password": new_password,
                "daily_logs": {}
            }
            save_credentials(credentials)
            st.sidebar.success("Signup successful! You can now log in.")

if auth_mode == "Login":
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Login"):
        if isinstance(credentials, dict) and username in credentials and credentials[username]["password"] == password:
            st.session_state.current_user = username
            st.sidebar.success(f"Welcome, {username}!")
            # Load user's daily logs
            st.session_state.today = credentials[username]["daily_logs"].get(str(date.today()), [])
        else:
            st.sidebar.error("Invalid username or password.")

# Main application
if st.session_state.current_user:
    st.title(f"Welcome, {st.session_state.current_user}!")

    # Input for adding a new food
    with st.expander("Add a New Food to Today's Log"):
        name = st.text_input("Food Name")
        calories = st.number_input("Calories", min_value=0, format="%d")
        protien = st.number_input("Protein (g)", min_value=0, format="%d")
        fat = st.number_input("Fat (g)", min_value=0, format="%d")
        carbs = st.number_input("Carbs (g)", min_value=0, format="%d")
        if st.button("Add Food"):
            food = Food(name, int(calories), int(protien), int(fat), int(carbs))
            st.session_state.today.append(vars(food))
            # Save to user's daily logs
            credentials[st.session_state.current_user]["daily_logs"][str(date.today())] = st.session_state.today
            save_credentials(credentials)
            st.success("Food added to today's log!")

    # Display predefined foods
    with st.expander("Choose from Predefined Foods"):
        if predefined_foods:
            food_names = list(predefined_foods.keys())
            selected_food = st.selectbox("Select a food", food_names)
            if st.button("Add Selected Food"):
                food_details = predefined_foods[selected_food]
                st.session_state.today.append({
                    "name": selected_food,
                    "calories": food_details[0],
                    "protien": food_details[1],
                    "fat": food_details[2],
                    "carbs": food_details[3],
                })
                # Save to user's daily logs
                credentials[st.session_state.current_user]["daily_logs"][str(date.today())] = st.session_state.today
                save_credentials(credentials)
                st.success(f"{selected_food} added to today's log!")

    # Display today's food log
    st.subheader("Today's Food Log")
    if st.session_state.today:
        for food in st.session_state.today:
            st.write(f"{food['name']} - Calories: {food['calories']}, Protein: {food['protien']}g, Fat: {food['fat']}g, Carbs: {food['carbs']}g")
    else:
        st.write("No food added yet!")

    # Visualization and Reset
    with st.expander("Visualize Progress"):
        if st.button("Reset Progress"):
            st.session_state.today = []
            credentials[st.session_state.current_user]["daily_logs"][str(date.today())] = st.session_state.today
            save_credentials(credentials)
            st.success("Progress reset for today!")

        period = st.selectbox("Select Period", ["Today", "Last 7 Days", "Last 30 Days", "Yearly"])
        if st.button("Visualize Progress"):
            today_date = date.today()
            user_logs = credentials[st.session_state.current_user]["daily_logs"]
            filtered_logs = {}

            if period == "Today":
                filtered_logs = {str(today_date): st.session_state.today}
            elif period == "Last 7 Days":
                for i in range(7):
                    day = (today_date - timedelta(days=i)).isoformat()
                    if day in user_logs:
                        filtered_logs[day] = user_logs[day]
            elif period == "Last 30 Days":
                for i in range(30):
                    day = (today_date - timedelta(days=i)).isoformat()
                    if day in user_logs:
                        filtered_logs[day] = user_logs[day]
            elif period == "Yearly":
                for log_date, entries in user_logs.items():
                    if str(today_date.year) in log_date:
                        filtered_logs[log_date] = entries

            # Summarize the data
            calorie_sum, protien_sum, fats_sum, carbs_sum = 0, 0, 0, 0
            for log_entries in filtered_logs.values():
                for food in log_entries:
                    calorie_sum += food["calories"]
                    protien_sum += food["protien"]
                    fats_sum += food["fat"]
                    carbs_sum += food["carbs"]

            # Plot the results
            fig, axs = plt.subplots(2, 2, figsize=(10, 8))

            # Macronutrients Distribution
            if protien_sum + fats_sum + carbs_sum > 0:
                axs[0, 0].pie(
                    [protien_sum, fats_sum, carbs_sum],
                    labels=["Protein", "Fat", "Carbs"],
                    autopct="%1.1f%%"
                )
                axs[0, 0].set_title("Macronutrients Distribution")
            else:
                axs[0, 0].text(0.5, 0.5, 'No Data Available',
                               horizontalalignment='center',
                               verticalalignment='center',
                               transform=axs[0, 0].transAxes)
                axs[0, 0].set_title("Macronutrients Distribution")

            # Macronutrients Progress
            axs[0, 1].bar([0, 1, 2], [protien_sum, fats_sum, carbs_sum], width=0.4, label="Consumed")
            axs[0, 1].bar([0.5, 1.5, 2.5], [Protien_goal, Fat_goal, Carbs_goal], width=0.4, label="Goal")
            axs[0, 1].set_xticks([0.25, 1.25, 2.25])
            axs[0, 1].set_xticklabels(["Protein", "Fat", "Carbs"])
            axs[0, 1].set_title("Macronutrients Progress")
            axs[0, 1].legend()

            # Calories Goal Progress
            if calorie_sum > 0:
                axs[1, 0].pie(
                    [calorie_sum, max(0, Calorie_Goal_limit - calorie_sum)],
                    labels=["Calories", "Remaining"],
                    autopct="%1.1f%%"
                )
                axs[1, 0].set_title("Calories Goal Progress")
            else:
                axs[1, 0].text(0.5, 0.5, 'No Data Available',
                               horizontalalignment='center',
                               verticalalignment='center',
                               transform=axs[1, 0].transAxes)
                axs[1, 0].set_title("Calories Goal Progress")

            # Calories Over Time
            if filtered_logs:
                dates = list(filtered_logs.keys())
                cumulative_calories = [
                    sum(food["calories"] for food in filtered_logs[day])
                    for day in dates
                ]

                # Calculate cumulative sum of calories
                cumulative_sum = np.cumsum(cumulative_calories)

                # Plot cumulative calories and goal
                axs[1, 1].plot(dates, cumulative_sum, label="Calories Eaten", marker='o')
                axs[1, 1].axhline(y=Calorie_Goal_limit, color='r', linestyle='--', label="Calorie Goal")
                axs[1, 1].legend()
                axs[1, 1].set_title("Calories Goal Over Time")
                axs[1, 1].set_xlabel("Date")
                axs[1, 1].set_ylabel("Cumulative Calories")
                axs[1, 1].tick_params(axis='x', rotation=45)
            else:
                axs[1, 1].text(
                    0.5, 0.5, 'No Data Available',
                    horizontalalignment='center',
                    verticalalignment='center',
                    transform=axs[1, 1].transAxes
                )
                axs[1, 1].set_title("Calories Goal Over Time")

            fig.tight_layout()
            st.pyplot(fig)
