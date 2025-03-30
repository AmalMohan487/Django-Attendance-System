from datetime import datetime

date_input = "24/3/2025"  # Example user input
corrected_date = datetime.strptime(date_input, "%d/%m/%Y").date()