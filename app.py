from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
from dateutil import parser  # More flexible date parsing

app = Flask(__name__)
CORS(app)

@app.route('/analyze', methods=['POST'])
def analyze_expenses():
    try:
        data = request.get_json()
        if not data or 'expenses' not in data:
            return jsonify({"error": "No expenses provided"}), 400

        expenses = data['expenses']
        
        if not expenses:
            return jsonify({
                "data": [],
                "insight": "No expenses found for the selected period."
            })

        # ✅ Use dateutil.parser for flexible date handling
        processed_expenses = []
        for exp in expenses:
            try:
                # Parse any date format automatically
                parsed_date = parser.parse(exp['date'])
                expense_copy = exp.copy()
                expense_copy['_parsed_date'] = parsed_date
                processed_expenses.append(expense_copy)
            except (KeyError, ValueError, TypeError) as e:
                print(f"Skipping expense {exp.get('_id', 'unknown')}: {e}")
                continue

        # Sort by parsed date
        processed_expenses.sort(key=lambda x: x['_parsed_date'])

        # Group by month-year
        monthly_data = {}
        for exp in processed_expenses:
            d = exp['_parsed_date']
            key = f"{d.year}-{d.month:02d}"
            monthly_data.setdefault(key, 0)
            monthly_data[key] += exp['amount']

        # Convert to list and sort
        monthly_list = [{"month": key, "amount": amt} for key, amt in monthly_data.items()]
        monthly_list.sort(key=lambda x: x['month'])  # String sort works for YYYY-MM format

        # Generate insight (same as before)
        if len(monthly_list) >= 2:
            prev, curr = monthly_list[-2], monthly_list[-1]
            change = ((curr["amount"] - prev["amount"]) / prev["amount"]) * 100 if prev["amount"] != 0 else 0
            trend = "increased" if change > 0 else "decreased" if change < 0 else "remained the same"
            insight = f"Your expenses have {trend} by {abs(change):.2f}% compared to last month."
        elif len(monthly_list) == 1:
            insight = "This is your first month of tracking expenses. Keep it up!"
        else:
            insight = "Not enough data to generate insights."

        return jsonify({
            "data": monthly_list,
            "insight": insight
        })

    except Exception as e:
        print(f"Error in analyze_expenses: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "service": "Flask AI Service"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
