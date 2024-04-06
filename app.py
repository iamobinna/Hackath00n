import streamlit as st
import pandas as pd
from PyPDF2 import PdfReader

def main():
    st.set_page_config(page_title="Recipe Book Calorie Counter")
    st.title("Food Calorie Counter")

    # User Details
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Name")
        age = st.number_input("Age")
        weight = st.number_input("Weight (kg)")
    with col2:
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        height = st.number_input("Height (cm)")

    # File selection
    uploaded_file = st.file_uploader("Upload Recipe Book", type=["pdf", "csv"])

    if uploaded_file:
        st.write("File Uploaded")
        st.write(f"File Type: {uploaded_file.type}")

    if st.button("Process"):
        if not (name and age and weight and gender and height):
            st.error("Please fill in your details.")
        elif not uploaded_file:
            st.error("Now kindly upload a file.")
        else:
            if uploaded_file.type == "text/csv":
                df = pd.read_csv(uploaded_file)
                process_csv(df)
            elif uploaded_file.type == "application/pdf":
                process_pdf(uploaded_file, name, age, weight, gender, height)
            else:
                st.error("Unsupported file format. Please upload a CSV or PDF file.")

def process_csv(df):
    st.write("Processing CSV file...")
    st.write("Recipe Book Contents:")
    st.write(df)
    total_calories, warnings = calculate_total_calories(df)
    st.write(f"Total Calories: {total_calories}")
    if warnings:
        st.write("Warnings:")
        for warning in warnings:
            st.write(warning)

def calculate_total_calories(df):
    total_calories = 0
    warnings = []
    for index, row in df.iterrows():
        food = row['Food']
        weight_in_grams = row.get('Weight(g)', None)
        calories_per_100g = row.get('Calories/100g', None)
        if weight_in_grams is None or calories_per_100g is None:
            warnings.append(f"Warning: Missing parameter for food '{food}'")
            continue
        try:
            weight_in_grams = float(weight_in_grams)
            calories_per_100g = float(calories_per_100g)
        except ValueError:
            warnings.append(f"Warning: Invalid parameter value for food '{food}'")
            continue
        food_calories = (weight_in_grams / 100) * calories_per_100g
        total_calories += food_calories
    return total_calories, warnings

def process_pdf(uploaded_file, name, age, weight, gender, height):
    st.write("Processing PDF file...")
    pdf_text = ""
    reader = PdfReader(uploaded_file)
    for page_num in range(len(reader.pages)):
        page = reader.pages[page_num]
        pdf_text += page.extract_text()

    # Parse the text to extract food items, portion sizes, and calorie content
    # Here, I assume that the text contains lines with food items, portion sizes, and calorie content
    # You may need to adjust this parsing logic based on the actual structure of your PDF
    lines = pdf_text.split('\n')
    data = {'Food': [], 'Portion Size': [], 'Calorie Content': []}
    for line in lines:
        parts = line.split(',')
        if len(parts) == 3:
            data['Food'].append(parts[0].strip())
            data['Portion Size'].append(parts[1].strip())
            data['Calorie Content'].append(parts[2].strip())
    df = pd.DataFrame(data)

    st.write("Extracted Data from PDF:")
    st.write(df)

    show_summary_and_advice(df, name, age, weight, gender, height)


def show_summary_and_advice(df, name, age, weight, gender, height):
    # Calculate BMR based on gender
    if gender == "Male":
        bmr = 66 + (13.7 * weight) + (5 * height) - (6.8 * age)
    else:
        bmr = 655 + (9.6 * weight) + (1.8 * height) - (4.7 * age)
    # Calculate total calories per day needed
    if age < 30:
        total_calories_needed = bmr * 1.55  # Assuming moderate activity level for young adults
    else:
        total_calories_needed = bmr * 1.375  # Assuming light activity level for adults
    # Display total calories per day needed
    st.subheader("Total Calories per Day Needed")
    st.write(f"{total_calories_needed:.2f} kcal/day")
    # Generate advice based on user information
    advice = generate_advice(age, weight, gender, height)
    # Display advice
    st.subheader("Advice")
    st.write(advice)

    # Display food items with checkboxes
    st.subheader("Select Food Items:")
    st.write("DataFrame before selecting food items:")
    st.write(df)

    selected_items = st.checkbox(df['Food'], key='checkbox')
    selected_calories = 0
    for index, row in df.iterrows():
        if row['Food'] in selected_items:
            weight_in_grams = row.get('Weight(g)', None)
            calories_per_100g = row.get('Calories/100g', None)
            if weight_in_grams is not None and calories_per_100g is not None:
                try:
                    weight_in_grams = float(weight_in_grams)
                    calories_per_100g = float(calories_per_100g)
                    food_calories = (weight_in_grams / 100) * calories_per_100g
                    selected_calories += food_calories
                except ValueError:
                    st.warning(f"Invalid parameter value for food '{row['Food']}'")
            else:
                st.warning(f"Missing parameter for food '{row['Food']}'")
    st.subheader("Total Calories of Selected Items:")
    st.write(f"{selected_calories:.2f} kcal")

def generate_advice(age, weight, gender, height):
    advice = "Here is some advice based on your information:"
    # Calculate BMR based on gender
    if gender == "Male":
        bmr = 66 + (13.7 * weight) + (5 * height) - (6.8 * age)
    else:
        bmr = 655 + (9.6 * weight) + (1.8 * height) - (4.7 * age)
    if age < 30:
        advice += "\n- You are young, so focus on building healthy eating habits early."
    else:
        advice += "\n- Make sure to maintain a balanced diet to support your overall health."
    # Adjust advice based on BMI and BMR
    bmi = weight / ((height / 100) ** 2)
    if bmi > 25:
        advice += "\n- Consider reducing your calorie intake to achieve a healthy BMI."
    if bmr < 1200:  # Considering a very low BMR
        advice += "\n- Your Basal Metabolic Rate (BMR) seems very low. Please consult a healthcare professional."
    return advice

if __name__ == "__main__":
    main()
