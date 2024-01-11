import pandas as pd
import matplotlib.pyplot as plt

class BudgetCalculator:
    def __init__(self, initial_budget, exchange_duration):
        self.initial_budget = initial_budget
        self.remaining_budget = initial_budget
        self.exchange_duration = exchange_duration
        self.expenses = []

    def calculate_budget(self):
        monthly_budget = self.initial_budget / self.exchange_duration
        weekly_budget = monthly_budget / 4
        return monthly_budget, weekly_budget

    def record_expense(self, amount, description):
        self.expenses.append({'Amount': amount, 'Description': description})
        self.remaining_budget -= amount

    def display_summary(self):
        monthly_budget, weekly_budget = self.calculate_budget()

        print("\nBudget Summary:")
        print(f"Initial Budget: ${self.initial_budget}")
        print(f"Remaining Budget: ${self.remaining_budget}")
        print(f"Monthly Budget: ${monthly_budget}")
        print(f"Weekly Budget: ${weekly_budget}")
        print("\nExpenses:")
        if not self.expenses:
            print("No expenses recorded yet.")
        else:
            expenses_df = pd.DataFrame(self.expenses)
            print(expenses_df)

    def visualize_budget(self):
        monthly_budget, _ = self.calculate_budget()
        remaining_budget_percentage = (self.remaining_budget / monthly_budget) * 100
        spent_percentage = 100 - remaining_budget_percentage

        labels = 'Remaining Budget', 'Spent'
        sizes = [remaining_budget_percentage, spent_percentage]
        colors = ['lightcoral', 'lightblue']
        explode = (0.1, 0)

        plt.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%', shadow=True, startangle=140)
        plt.axis('equal')
        plt.title('Budget Visualization')
        plt.show()


# Example Usage:
initial_budget = float(input("Enter initial budget for the exchange: "))
exchange_duration = int(input("Enter the duration of the exchange (in months): "))

budget_calculator = BudgetCalculator(initial_budget, exchange_duration)

while True:
    print("\nOptions:")
    print("1. Record Expense")
    print("2. Display Budget Summary")
    print("3. Visualize Budget")
    print("4. Exit")

    choice = input("Enter your choice (1-4): ")

    if choice == '1':
        amount = float(input("Enter expense amount: "))
        description = input("Enter expense description: ")
        budget_calculator.record_expense(amount, description)
    elif choice == '2':
        budget_calculator.display_summary()
    elif choice == '3':
        budget_calculator.visualize_budget()
    elif choice == '4':
        break
    else:
        print("Invalid choice. Please enter a number between 1 and 4.")
