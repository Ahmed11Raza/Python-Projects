import pandas as pd
import numpy as np
import joblib
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, roc_curve, auc
import streamlit as st
import pickle
import os
from datetime import datetime
import base64
import io

# Set page configuration
st.set_page_config(
    page_title="Loan Approval Predictor",
    page_icon="💰",
    layout="wide"
)

# Application title and description
st.title("Loan Approval Predictor")
st.markdown("""
This application predicts whether your loan application is likely to be approved based on 
various financial and personal factors. Adjust the parameters below to see how they affect
your approval chances.
""")

# Function to train or load model
def get_model():
    model_path = "loan_approval_model.pkl"
    
    # Check if model exists
    if os.path.exists(model_path):
        # Load existing model
        with open(model_path, 'rb') as file:
            model = pickle.load(file)
        return model
    else:
        # Generate synthetic data for demonstration
        st.info("No trained model found. Training a new model with synthetic data...")
        
        # Generate synthetic data
        np.random.seed(42)
        n_samples = 1000
        
        # Generate features
        credit_scores = np.random.randint(300, 850, n_samples)
        incomes = np.random.randint(20000, 200000, n_samples)
        loan_amounts = np.random.randint(5000, 500000, n_samples)
        loan_terms = np.random.choice([36, 60, 84, 120, 180, 240, 360], n_samples)
        employment_years = np.random.randint(0, 30, n_samples)
        debt_to_income = np.random.uniform(0, 0.6, n_samples)
        
        # Generate education and employment type categories
        education = np.random.choice(['High School', 'Bachelor', 'Master', 'PhD'], n_samples)
        employment_type = np.random.choice(['Full-time', 'Part-time', 'Self-employed', 'Unemployed'], n_samples)
        
        # Create DataFrame
        data = pd.DataFrame({
            'credit_score': credit_scores,
            'annual_income': incomes,
            'loan_amount': loan_amounts,
            'loan_term': loan_terms,
            'employment_years': employment_years,
            'debt_to_income': debt_to_income,
            'education': education,
            'employment_type': employment_type
        })
        
        # Generate target (loan approval) with a reasonable model
        # Higher credit scores, income, and employment years increase approval chance
        # Higher loan amounts and debt-to-income reduce approval chance
        
        approval_score = (
            (data['credit_score'] - 300) / 550 * 0.35 +  # Credit score (normalized)
            (np.log10(data['annual_income']) - 4) / 2 * 0.25 +  # Log income
            (1 - data['loan_amount'] / 500000) * 0.15 +  # Inverse loan amount
            (data['employment_years'] / 30) * 0.15 +  # Employment years
            (1 - data['debt_to_income'] / 0.6) * 0.1  # Inverse debt-to-income
        )
        
        # Education bonus
        edu_bonus = pd.Series(0, index=range(n_samples))
        edu_bonus[data['education'] == 'Bachelor'] = 0.05
        edu_bonus[data['education'] == 'Master'] = 0.08
        edu_bonus[data['education'] == 'PhD'] = 0.1
        
        # Employment type impact
        emp_impact = pd.Series(0, index=range(n_samples))
        emp_impact[data['employment_type'] == 'Part-time'] = -0.1
        emp_impact[data['employment_type'] == 'Self-employed'] = -0.05
        emp_impact[data['employment_type'] == 'Unemployed'] = -0.4
        
        approval_score = approval_score + edu_bonus + emp_impact
        
        # Add some randomness
        approval_score += np.random.normal(0, 0.1, n_samples)
        
        # Convert to binary outcome
        data['loan_approved'] = (approval_score > 0.5).astype(int)
        
        # Split the data
        X = data.drop('loan_approved', axis=1)
        y = data['loan_approved']
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Define preprocessing for numeric features
        numeric_features = ['credit_score', 'annual_income', 'loan_amount', 'loan_term', 
                           'employment_years', 'debt_to_income']
        numeric_transformer = StandardScaler()
        
        # Define preprocessing for categorical features
        categorical_features = ['education', 'employment_type']
        categorical_transformer = OneHotEncoder(handle_unknown='ignore')
        
        # Combine preprocessing steps
        preprocessor = ColumnTransformer(
            transformers=[
                ('num', numeric_transformer, numeric_features),
                ('cat', categorical_transformer, categorical_features)
            ])
        
        # Create and train the model pipeline
        model = Pipeline(steps=[
            ('preprocessor', preprocessor),
            ('classifier', RandomForestClassifier(n_estimators=100, random_state=42))
        ])
        
        model.fit(X_train, y_train)
        
        # Evaluate the model
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        st.success(f"Model trained successfully with {accuracy:.2%} accuracy")
        
        # Save the model
        with open(model_path, 'wb') as file:
            pickle.dump(model, file)
        
        return model

# Create tabs for different sections
tab1, tab2, tab3 = st.tabs(["Loan Predictor", "Model Insights", "Application History"])

with tab1:
    # Get the model
    model = get_model()

    # Create columns for layout
    col1, col2 = st.columns([1, 1])

    with col1:
        st.header("Applicant Information")
        
        # Credit score
        credit_score = st.slider("Credit Score", 300, 850, 650, 5,
                                help="Your current credit score between 300-850")
        
        # Annual Income
        annual_income = st.slider("Annual Income ($)", 20000, 200000, 60000, 1000,
                                help="Your total annual income before taxes")
        
        # Loan Amount
        loan_amount = st.slider("Loan Amount ($)", 5000, 500000, 100000, 5000,
                              help="The loan amount you're applying for")
        
        # Loan Term
        loan_term = st.selectbox("Loan Term (months)", 
                                [36, 60, 84, 120, 180, 240, 360], 
                                index=1,
                                help="The term of the loan in months")
        
        # Employment Years
        employment_years = st.slider("Years of Employment", 0, 30, 5, 1,
                                    help="Number of years in current employment")
        
        # Debt to Income Ratio
        debt_to_income = st.slider("Debt-to-Income Ratio", 0.0, 0.6, 0.3, 0.01,
                                  help="Your monthly debt payments divided by your gross monthly income")
        
        # Education Level
        education = st.selectbox("Education Level", 
                                ["High School", "Bachelor", "Master", "PhD"], 
                                index=1,
                                help="Your highest level of education")
        
        # Employment Type
        employment_type = st.selectbox("Employment Type", 
                                      ["Full-time", "Part-time", "Self-employed", "Unemployed"], 
                                      index=0,
                                      help="Your current employment status")
    
    with col2:
        st.header("Loan Approval Prediction")
        
        # Create a DataFrame for prediction
        input_data = pd.DataFrame({
            'credit_score': [credit_score],
            'annual_income': [annual_income],
            'loan_amount': [loan_amount],
            'loan_term': [loan_term],
            'employment_years': [employment_years],
            'debt_to_income': [debt_to_income],
            'education': [education],
            'employment_type': [employment_type]
        })
        
        # Get prediction
        prediction_proba = model.predict_proba(input_data)[0][1]
        prediction = model.predict(input_data)[0]
        
        # Display gauge chart for probability
        fig, ax = plt.subplots(figsize=(8, 4))
        
        # Create gauge chart
        gauge_colors = ['#FF0000', '#FFA500', '#FFFF00', '#008000']
        sns.set_style('whitegrid')
        
        # Draw the gauge
        gauge = np.linspace(0, 1, 100)
        ax.barh(y=0, width=1, height=0.5, color='lightgrey')
        ax.barh(y=0, width=prediction_proba, height=0.5, color=gauge_colors[int(prediction_proba*3.99)])
        
        # Add needle pointer
        needle_length = 0.25
        ax.arrow(prediction_proba, -0.1, 0, needle_length, head_width=0.03, 
                head_length=0.05, fc='black', ec='black')
        
        # Add text
        ax.text(0.5, -0.3, f'Approval Probability: {prediction_proba:.2%}', 
                ha='center', va='center', fontsize=12, fontweight='bold')
        
        # Add low/medium/high markers
        ax.text(0.1, 0.15, 'Low', ha='center', va='center', fontsize=10)
        ax.text(0.35, 0.15, 'Medium', ha='center', va='center', fontsize=10)
        ax.text(0.65, 0.15, 'High', ha='center', va='center', fontsize=10)
        ax.text(0.9, 0.15, 'Very High', ha='center', va='center', fontsize=10)
        
        # Format the chart
        ax.set_xlim(0, 1)
        ax.set_ylim(-0.5, 0.5)
        ax.axis('off')
        
        st.pyplot(fig)
        
        # Display approval result
        if prediction == 1:
            st.success("**APPROVED:** Based on the provided information, your loan application is likely to be approved.")
        else:
            st.error("**DENIED:** Based on the provided information, your loan application is likely to be denied.")
        
        # Recommendations
        st.subheader("Recommendations for Improving Approval Chances:")
        recommendations = []
        
        if credit_score < 700:
            recommendations.append("Work on improving your credit score. Consider paying down credit card balances and ensuring all payments are made on time.")
        
        if debt_to_income > 0.4:
            recommendations.append("Reduce your debt-to-income ratio by paying down existing debt or increasing your income.")
        
        if employment_years < 2:
            recommendations.append("Lenders typically prefer longer employment history. If possible, apply after you have at least 2 years at your current job.")
        
        if loan_amount > annual_income * 0.8:
            recommendations.append("Consider applying for a smaller loan amount. The requested amount may be high relative to your annual income.")
        
        if not recommendations:
            recommendations.append("Your application metrics look good! To further improve chances, ensure all application details are accurate and documentation is complete.")
        
        for rec in recommendations:
            st.markdown(f"- {rec}")
    
    # Save application button
    if st.button("Save This Application"):
        # Create a dictionary with the current inputs
        current_inputs = {
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'credit_score': credit_score,
            'annual_income': annual_income,
            'loan_amount': loan_amount,
            'loan_term': loan_term,
            'employment_years': employment_years,
            'debt_to_income': debt_to_income,
            'education': education,
            'employment_type': employment_type,
            'approval_probability': f"{prediction_proba:.2%}",
            'predicted_approval': "Approved" if prediction == 1 else "Denied"
        }
        
        # Convert to DataFrame
        df_inputs = pd.DataFrame([current_inputs])
        
        # Check if the file exists
        if os.path.exists('saved_loan_applications.csv'):
            df_inputs.to_csv('saved_loan_applications.csv', mode='a', header=False, index=False)
        else:
            df_inputs.to_csv('saved_loan_applications.csv', index=False)
        
        st.success("Application saved successfully!")

with tab2:
    st.header("Model Insights")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Feature Importance")
        
        # Extract the RandomForestClassifier from the pipeline
        rf_classifier = model.named_steps['classifier']
        
        # Get feature names after preprocessing
        preprocessor = model.named_steps['preprocessor']
        cat_features = preprocessor.transformers_[1][1].get_feature_names_out(
            ['education', 'employment_type']
        )
        feature_names = np.append(['credit_score', 'annual_income', 'loan_amount', 'loan_term', 
                                  'employment_years', 'debt_to_income'], cat_features)
        
        # Get feature importances
        importances = rf_classifier.feature_importances_
        
        # Create DataFrame for visualization
        feature_importance = pd.DataFrame({
            'Feature': feature_names,
            'Importance': importances
        })
        
        # Sort by importance
        feature_importance = feature_importance.sort_values('Importance', ascending=False).head(8)
        
        # Plot feature importance
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.barplot(x='Importance', y='Feature', data=feature_importance, palette='viridis')
        plt.title('Top Features Affecting Loan Approval')
        plt.tight_layout()
        
        st.pyplot(fig)
    
    with col2:
        st.subheader("Your Application vs. Average Approved Application")
        
        # Generate synthetic "average" approved applicant
        avg_approved = {
            'credit_score': 720,
            'annual_income': 85000,
            'loan_amount': 150000,
            'employment_years': 8,
            'debt_to_income': 0.32
        }
        
        # Create comparison data
        comparison_data = pd.DataFrame({
            'Metric': list(avg_approved.keys()),
            'Your Value': [credit_score, annual_income, loan_amount, employment_years, debt_to_income],
            'Avg. Approved Value': list(avg_approved.values())
        })
        
        # Format the values for display
        comparison_data['Your Value'] = comparison_data.apply(
            lambda x: f"${int(x['Your Value']):,}" if 'income' in x['Metric'] or 'amount' in x['Metric'] 
            else (f"{x['Your Value']:.2%}" if 'ratio' in x['Metric'] else x['Your Value']),
            axis=1
        )
        
        comparison_data['Avg. Approved Value'] = comparison_data.apply(
            lambda x: f"${int(x['Avg. Approved Value']):,}" if 'income' in x['Metric'] or 'amount' in x['Metric'] 
            else (f"{x['Avg. Approved Value']:.2%}" if 'ratio' in x['Metric'] else x['Avg. Approved Value']),
            axis=1
        )
        
        # Display the comparison table
        st.table(comparison_data)
        
        # Plot radar chart comparing user values to average approved values
        st.subheader("Profile Comparison")
        
        # Prepare data for radar chart
        categories = ['Credit Score', 'Annual Income', 'Loan Amount', 'Employment Years', 'Debt-to-Income']
        
        # Normalize values to 0-1 scale for comparison
        N = len(categories)
        
        # Your values
        your_values = [
            (credit_score - 300) / 550,  # Credit score normalized to 0-1
            (annual_income - 20000) / 180000,  # Income normalized
            1 - (loan_amount - 5000) / 495000,  # Inverse loan amount (lower is better)
            employment_years / 30,  # Employment years normalized
            1 - debt_to_income / 0.6  # Inverse debt-to-income (lower is better)
        ]
        
        # Average approved values
        avg_values = [
            (avg_approved['credit_score'] - 300) / 550,
            (avg_approved['annual_income'] - 20000) / 180000,
            1 - (avg_approved['loan_amount'] - 5000) / 495000,
            avg_approved['employment_years'] / 30,
            1 - avg_approved['debt_to_income'] / 0.6
        ]
        
        # Set up the radar chart
        angles = np.linspace(0, 2*np.pi, N, endpoint=False).tolist()
        
        # Close the loop
        your_values += [your_values[0]]
        avg_values += [avg_values[0]]
        angles += [angles[0]]
        
        # Create the plot
        fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
        
        # Plot your values and average values
        ax.plot(angles, your_values, 'o-', linewidth=2, label='Your Values')
        ax.fill(angles, your_values, alpha=0.25)
        ax.plot(angles, avg_values, 'o-', linewidth=2, label='Avg. Approved')
        ax.fill(angles, avg_values, alpha=0.25)
        
        # Set category labels
        ax.set_thetagrids(np.degrees(angles[:-1]), categories)
        
        # Add legend
        ax.legend(loc='upper right', bbox_to_anchor=(0.1, 0.1))
        
        st.pyplot(fig)

    # Scenario Analysis
    st.header("Scenario Analysis")
    st.write("See how changing specific factors affects your approval probability")
    
    analysis_col1, analysis_col2 = st.columns([1, 1])
    
    with analysis_col1:
        # Select factor to analyze
        factor_to_analyze = st.selectbox(
            "Select factor to analyze",
            ['credit_score', 'annual_income', 'loan_amount', 'loan_term', 'employment_years', 'debt_to_income']
        )
        
        # Get current input data
        scenario_data = input_data.copy()
        
        # Create range for the selected factor
        if factor_to_analyze == 'credit_score':
            range_values = np.linspace(300, 850, 20)
            x_label = 'Credit Score'
        elif factor_to_analyze == 'annual_income':
            range_values = np.linspace(20000, 200000, 20)
            x_label = 'Annual Income ($)'
        elif factor_to_analyze == 'loan_amount':
            range_values = np.linspace(5000, 500000, 20)
            x_label = 'Loan Amount ($)'
        elif factor_to_analyze == 'loan_term':
            range_values = np.array([36, 60, 84, 120, 180, 240, 360])
            x_label = 'Loan Term (months)'
        elif factor_to_analyze == 'employment_years':
            range_values = np.linspace(0, 30, 20)
            x_label = 'Employment Years'
        elif factor_to_analyze == 'debt_to_income':
            range_values = np.linspace(0, 0.6, 20)
            x_label = 'Debt-to-Income Ratio'
        
        # Calculate probabilities for each value
        probabilities = []
        for value in range_values:
            temp_data = scenario_data.copy()
            temp_data[factor_to_analyze] = value
            probabilities.append(model.predict_proba(temp_data)[0][1])
    
    with analysis_col2:
        # Plot the scenario analysis
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Mark current value with a vertical line
        current_value = input_data[factor_to_analyze].values[0]
        current_idx = np.abs(range_values - current_value).argmin()
        current_prob = probabilities[current_idx]
        
        # Plot the probability curve
        ax.plot(range_values, probabilities, 'b-', linewidth=2)
        ax.axvline(x=current_value, color='r', linestyle='--', label=f'Current: {current_value:.2f}')
        ax.axhline(y=0.5, color='g', linestyle='--', label='Approval Threshold')
        
        # Add a marker at the current value
        ax.plot(current_value, current_prob, 'ro', markersize=8)
        
        # Format axes
        ax.set_xlabel(x_label)
        ax.set_ylabel('Approval Probability')
        ax.set_title(f'How {x_label} Affects Approval Probability')
        ax.legend()
        
        # Set y-axis limits
        ax.set_ylim(0, 1)
        
        # Format x-axis to include currency symbols if needed
        if factor_to_analyze in ['annual_income', 'loan_amount']:
            # Format x-axis labels with dollar signs
            from matplotlib.ticker import FuncFormatter
            def currency_formatter(x, pos):
                return f"${x:,.0f}"
            ax.xaxis.set_major_formatter(FuncFormatter(currency_formatter))
        
        # Show the plot
        st.pyplot(fig)

    # Show what-if analysis
    st.header("What-If Analysis")
    
    what_if_col1, what_if_col2, what_if_col3 = st.columns([1, 1, 1])
    
    with what_if_col1:
        what_if_credit = st.number_input("Credit Score", min_value=300, max_value=850, value=credit_score)
    
    with what_if_col2:
        what_if_income = st.number_input("Annual Income ($)", min_value=20000, max_value=200000, value=annual_income)
    
    with what_if_col3:
        what_if_debt = st.number_input("Debt-to-Income Ratio", min_value=0.0, max_value=0.6, value=debt_to_income, step=0.01)
    
    # Create what-if scenario data
    what_if_data = input_data.copy()
    what_if_data['credit_score'] = what_if_credit
    what_if_data['annual_income'] = what_if_income
    what_if_data['debt_to_income'] = what_if_debt
    
    # Get prediction for what-if scenario
    what_if_prob = model.predict_proba(what_if_data)[0][1]
    what_if_pred = model.predict(what_if_data)[0]
    
    # Show the results
    what_if_result_col1, what_if_result_col2 = st.columns([1, 1])
    
    with what_if_result_col1:
        st.metric(
            label="Original Approval Probability", 
            value=f"{prediction_proba:.2%}",
            delta=None
        )
    
    with what_if_result_col2:
        st.metric(
            label="What-If Approval Probability", 
            value=f"{what_if_prob:.2%}", 
            delta=f"{what_if_prob - prediction_proba:.2%}"
        )
    
    # Show approval status
    if what_if_pred == 1:
        st.success("With these changes, your application would likely be **APPROVED**")
    else:
        st.error("With these changes, your application would likely still be **DENIED**")

with tab3:
    st.header("Application History")
    
    # Display saved applications if any exist
    if os.path.exists('saved_loan_applications.csv'):
        saved_df = pd.read_csv('saved_loan_applications.csv')
        
        # Show data
        st.dataframe(saved_df)
        
        # Download csv
        def get_csv_download_link(df):
            csv = df.to_csv(index=False)
            b64 = base64.b64encode(csv.encode()).decode()
            href = f'<a href="data:file/csv;base64,{b64}" download="loan_applications.csv">Download CSV</a>'
            return href
        
        st.markdown(get_csv_download_link(saved_df), unsafe_allow_html=True)
        
        # Visualize application history
        if len(saved_df) > 1:
            st.subheader("Application History Analysis")
            
            # Timeline of applications
            fig, ax = plt.subplots(figsize=(10, 6))
            
            # Convert approval probability to numeric
            saved_df['approval_numeric'] = saved_df['approval_probability'].str.rstrip('%').astype(float) / 100
            
            # Plot timeline
            ax.plot(saved_df['timestamp'], saved_df['approval_numeric'], 'o-', linewidth=2)
            ax.set_xlabel('Application Date')
            ax.set_ylabel('Approval Probability')
            ax.set_title('Approval Probability Over Time')
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            st.pyplot(fig)
            
            # Compare key metrics across applications
            st.subheader("Key Metrics Comparison")
            
            # Select metrics to compare
            metrics_to_compare = ['credit_score', 'annual_income', 'loan_amount', 'debt_to_income']
            
            # Prepare data for visualization
            metric_fig, metric_axes = plt.subplots(2, 2, figsize=(12, 10))
            metric_axes = metric_axes.flatten()
            
            for i, metric in enumerate(metrics_to_compare):
                metric_axes[i].plot(saved_df['timestamp'], saved_df[metric], 'o-', linewidth=2)
                metric_axes[i].set_title(f'{metric.replace("_", " ").title()} Over Time')
                metric_axes[i].set_xlabel('Application Date')
                metric_axes[i].set_ylabel(metric.replace("_", " ").title())
                plt.setp(metric_axes[i].xaxis.get_majorticklabels(), rotation=45)
            
            plt.tight_layout()
            st.pyplot(metric_fig)
        
        # Option to clear history
        if st.button("Clear Application History"):
            if os.path.exists('saved_loan_applications.csv'):
                os.remove('saved_loan_applications.csv')
                st.success("Application history has been cleared!")
                st.experimental_rerun()
    else:
        st.info("No saved applications found. Save an application to see it here.")

# Add a footer
st.markdown("---")
st.markdown("""
<div style="text-align: center">
    <p>Loan Approval Predictor v2.0 | Created for demonstration purposes only</p>
    <p>This application uses a machine learning model trained on synthetic data.</p>
    <p>⚠️ Do not use for actual loan decisions. Consult a financial professional.</p>
</div>
""", unsafe_allow_html=True)

# Add a help sidebar
with st.sidebar:
    st.header("Help & Information")
    
    with st.expander("What is this app?"):
        st.write("""
        This application uses machine learning to predict whether a loan application would be approved or denied
        based on various financial and personal factors. It is for educational purposes only and should not be
        used for actual loan decisions.
        """)
    
    with st.expander("How to use this app?"):
        st.write("""
        1. Adjust the sliders and dropdowns to input your financial information
        2. View the prediction result and approval probability
        3. Check the recommendations to improve your chances
        4. Save your application to track changes over time
        5. Explore the Model Insights tab to understand what factors matter most
        """)
    
    with st.expander("What does each input mean?"):
        st.markdown("""
        - **Credit Score**: A number between 300-850 that represents your creditworthiness
        - **Annual Income**: Your total yearly income before taxes
        - **Loan Amount**: The amount of money you're requesting to borrow
        - **Loan Term**: The duration of the loan in months
        - **Employment Years**: How long you've been at your current job
        - **Debt-to-Income Ratio**: Your monthly debt payments divided by your gross monthly income
        - **Education Level**: Your highest completed level of education
        - **Employment Type**: Your current employment status
        """)
    
    with st.expander("How does the model work?"):
        st.write("""
        The model uses a Random Forest Classifier, which is a machine learning algorithm that makes predictions
        based on patterns it finds in training data. It considers all the inputs you provide and computes a
        probability that your loan would be approved. For demonstration purposes, this app uses synthetic data
        to train the model.
        """)