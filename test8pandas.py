#We import pandas here in order to save and manipulate our expenses
import pandas as pd

#Keeps track of the student budget, expense, and provide functionality to record budget-related information
class CalculateurBudget:
    #we use init to initialize the object's attributes, setting the initial value of the budget
    def __init__(self, initial_budget, exchange_duration):
        self.initial_budget = initial_budget
        self.remaining_budget = initial_budget
        self.exchange_duration = exchange_duration
        self.expenses = []

#Function that's responsible for calculating the monthly and weekly budgets 
    def calcul_budget(self):
        monthly_budget = self.initial_budget / self.exchange_duration
        weekly_budget = monthly_budget / 4
        return monthly_budget, weekly_budget

#Function that's responsible for recording every expense inputted 
    def journal_depenses(self, amount, description):
        self.expenses.append({'Montant': amount, 'Description': description})
        self.remaining_budget -= amount

#Function that prints a summary of the exchange student's including 
#initial budget, remaining budget, monthly budget, and weekly budget. 
#It also prints a table of recorded expenses, the use of pandas is used to present the expenses in a structured and readable way format
    def bilan_financier(self):
        monthly_budget, weekly_budget = self.calcul_budget()

        print("\nBilan Financier:")
        print(f"Budget Initial: ${self.initial_budget}")
        print(f"Budget Restant: ${self.remaining_budget}")
        print(f"Budget Mensuel: ${monthly_budget}")
        print(f"Budget Hebdomadaire: ${weekly_budget}")
        print("\nDépense:")
        if not self.expenses:
            print("Aucune dépense enregistrée.")
        else:
            expenses_df = pd.DataFrame(self.expenses)
            print(expenses_df)

#Function that saves the budget-related data to a CSV file
    def save_to_file(self, filename):
        data = {
            'Budget Initial': [self.initial_budget],
            'Budget Restant': [self.remaining_budget],
            'Dépense': self.expenses
        }
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False)
        print(f"Data saved to {filename}")
        
#Function that reads the budget-related data back from a CSV file, updating the object's attributes accordingly
    def load_from_file(self, filename):
        try:
            df = pd.read_csv(filename)
            self.initial_budget = df['Budget Initial'][0]
            self.remaining_budget = df['Budget Restant'][0]
            self.expenses = eval(df['Dépenses'][0])
            print(f"Data loaded from {filename}")
        except FileNotFoundError:
            print(f"File {filename} not found. No data loaded.")

#User interaction here with the the Budget Calculator for the Exchange:
initial_budget = float(input("Entrez le budget initial pour l'échange: "))
exchange_duration = int(input("Entrez la durée de l'échange (en mois): "))

budget_calculator = CalculateurBudget(initial_budget, exchange_duration)

while True:
    print("\nOptions:")
    print("1. Journal de dépenses")
    print("2. Vue Budgetaire")
    print("3. Save to File")
    print("4. Load from File")
    print("5. Exit")

    choice = input("Entrez votre choix (1-5): ")

    if choice == '1':
        amount = float(input("Entrez le montant de la dépense: "))
        description = input("Entrez la déscription de la dépense: ")
        budget_calculator.journal_depenses(amount, description)
    elif choice == '2':
        budget_calculator.bilan_financier()
    elif choice == '3':
        filename = input("Entrez le nom du fichier pour enregistrer les données: ")
        budget_calculator.save_to_file(filename)
    elif choice == '4':
        filename = input("Entrez le nom du fichier pour charger les données: ")
        budget_calculator.load_from_file(filename)
    elif choice == '5':
        break
    else:
        print("Choix invalide. Veuillez entrez un numéro entre 1 à 5.")