# AI Expense Categorizer & Spending Analyzer

## Project Objective
A beginner-friendly web application where a user can enter an expense (e.g., "Zomato dinner - ₹450"), and the application uses a simple Machine Learning model to automatically predict the category (e.g., Food). It saves the expense in a database and updates an interactive dashboard showing spending statistics, charts, transactions, and AI-generated spending insights.

## Features
- **Add Expense with AI**: Enter an expense description, and the ML model predicts the most likely category.
- **Interactive Dashboard**: View total expenses, average spending, and dynamic charts (Doughnut and Bar charts).
- **Transaction Management**: View, filter by category, search, and delete expenses.
- **Analytics Page**: Deep-dive visualizations of spending habits.
- **AI Insights**: Dynamically generated insights based on your spending patterns.
- **Fully Local**: Runs entirely on localhost with no paid APIs or external services.

## Technology Stack
- **Backend**: Python, Flask
- **Database**: SQLite
- **Machine Learning**: Scikit-learn (TF-IDF Vectorizer, Logistic Regression), Pandas
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5, Chart.js

## AI/ML Methodology
This project uses Natural Language Processing (NLP) to categorize text descriptions into predefined categories (Food, Travel, Shopping, Bills, Education, Entertainment, Healthcare, Other).
1. **TF-IDF Vectorizer**: Converts the text (like "Zomato dinner") into a sequence of numbers (a vector). It gives higher importance to unique words that help define a category (like "Zomato") and lower importance to common words.
2. **Logistic Regression**: A classification algorithm that learns the mathematical relationship between the TF-IDF vectors and their correct categories during the training phase. When given a new vector, it predicts the probability of it belonging to each category and selects the highest one.

## Database Structure
Database: `expenses.db`
Table: `expenses`
- `id` (INTEGER, Primary Key)
- `description` (TEXT)
- `amount` (REAL)
- `category` (TEXT)
- `date` (TEXT)
- `created_at` (TIMESTAMP)

## Project Architecture & Folder Structure
```
ai-expense-analyzer/
│
├── app.py                 # Main Flask application and routes
├── train_model.py         # Script to train and save the ML model
├── expense_dataset.csv    # Training data for the ML model
├── requirements.txt       # Python dependencies
├── README.md              # Project documentation
│
├── model/                 # Folder storing the trained models
│   ├── vectorizer.pkl
│   └── classifier.pkl
│
├── templates/             # HTML files for the frontend
│   ├── base.html          # Layout template
│   ├── dashboard.html     # Main dashboard
│   ├── add_expense.html   # Form to add expense and trigger ML
│   ├── transactions.html  # Table to view and filter data
│   ├── analytics.html     # Detailed charts
│   └── insights.html      # AI generated text insights
│
└── static/
    └── css/
        └── style.css      # Custom styling
```

## Installation Steps
1. Make sure Python 3 is installed on your computer.
2. Open a terminal and navigate to the project directory.
3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running Instructions
1. First, train the Machine Learning model:
   ```bash
   python train_model.py
   ```
   *This reads the CSV, trains the model, and creates the `.pkl` files in the `model/` folder.*

2. Next, start the Flask web server:
   ```bash
   python app.py
   ```

3. Open your web browser and go to:
   ```text
   http://127.0.0.1:5000
   ```

## Example Inputs to Try
- **Description**: Zomato dinner -> **Prediction**: Food
- **Description**: Uber ride -> **Prediction**: Travel
- **Description**: Amazon shoes -> **Prediction**: Shopping
- **Description**: Electricity bill -> **Prediction**: Bills
- **Description**: College fees -> **Prediction**: Education
- **Description**: Netflix subscription -> **Prediction**: Entertainment

## Future Scope
- User authentication and login system.
- Personal budget setting and alerts.
- Receipt image scanning using OCR.
- Integration with bank APIs for automatic transaction fetching.
- Deployment to a cloud platform like Heroku or AWS.
