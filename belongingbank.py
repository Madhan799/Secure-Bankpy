import pandas as pd
import hashlib
from datetime import datetime
import os
import re
import sys

# --- TERMINAL SANITIZER (VS CODE FIX) ---
def clean_input(prompt):
    while True:
        if sys.stdin.isatty():
            sys.stdin.flush()
        raw = input(prompt)
        cleaned = re.sub(r'[^\x20-\x7E]', '', raw).strip()
        if cleaned:
            return cleaned

# --- SECURITY LAYER ---
def hash_pin(pin):
    return hashlib.sha256(pin.encode()).hexdigest()

# --- UX PERSONALIZATION ---
def get_time_greeting():
    hour = datetime.now().hour
    if hour < 12: return "Good morning"
    elif 12 <= hour < 17: return "Good afternoon"
    else: return "Good evening"

class Account:
    def __init__(self, acc_id, name, balance, pin):
        self.acc_id = acc_id
        self.name = name
        self.__balance = balance
        self.__pin = pin 

    def verify_pin(self, pin):
        return self.__pin == hash_pin(pin)

    def credit(self, amount):
        if amount <= 0:
            print(f"\n!! {self.name}, we can only add positive energy (and amounts) to your savings!")
        else:
            self.__balance += amount
            print(f"\n>> Wonderful news, {self.name}! ₹{amount} has been safely tucked away.")
            print(f">> Your growing wealth is now: ₹{self.__balance} 🌱")
            self.update_balance_file()
            self.add_transaction("Credit", amount)

    def debit(self, amount):
        if amount <= 0:
            print("\n!! Please enter a valid amount to withdraw.")
        elif amount > self.__balance:
            print(f"\n!! Oh no, {self.name}. It looks like ₹{amount} is a bit more than we have right now.")
            print(f"!! You currently have ₹{self.__balance} available for use.")
        else:
            self.__balance -= amount
            print(f"\n>> Done! ₹{amount} is on its way to you for your next adventure.")
            if self.__balance < 500:
                print(f">> Just a friendly heads-up, your balance is getting a bit cozy at ₹{self.__balance}.")
            self.update_balance_file()
            self.add_transaction("Debit", amount)

    def get_balance(self):
        return self.__balance

    def update_balance_file(self):
        try:
            df = pd.read_excel("accounts_15.xlsx")
            df.loc[df["Account ID"] == self.acc_id, "Balance"] = self.__balance
            df.to_excel("accounts_15.xlsx", index=False)
        except: pass

    def add_transaction(self, trans_type, amount):
        time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        new_tx = pd.DataFrame([{
            "Account ID": self.acc_id, "Name": self.name, 
            "Type": trans_type, "Amount": amount, "Time": time
        }])
        file = "transactions.xlsx"
        try:
            if os.path.exists(file):
                tx_df = pd.read_excel(file)
                # FUTURE-PROOF FIX: Check if empty before concat
                if tx_df.empty:
                    tx_df = new_tx
                else:
                    tx_df = pd.concat([tx_df, new_tx], ignore_index=True)
            else:
                tx_df = new_tx
            tx_df.to_excel(file, index=False)
        except:
            print(f"!! We had a tiny trouble recording this part of your story, but your balance is safe.")

    def show_transactions(self):
        try:
            data = pd.read_excel("transactions.xlsx")
            user_data = data[data["Account ID"] == self.acc_id]
            if user_data.empty:
                print(f"\n-- Your journey with us is just beginning, {self.name}! No history yet. --")
            else:
                print("\n" + "✨"*15 + f"\n   {self.name.upper()}'S STORY\n" + "✨"*15)
                print(user_data.to_string(index=False))
        except:
            print("\n!! We haven't started your storybook yet.")

    def transfer_money(self, receiver, amount):
        if amount <= 0:
            print("\n!! A gift should always carry positive value!")
        elif amount > self.__balance:
            print(f"\n!! We'd love to help you share that, but you're ₹{amount - self.__balance} short.")
        else:
            self.__balance -= amount
            receiver.__balance += amount
            self.update_balance_file()
            receiver.update_balance_file()
            self.add_transaction(f"Shared with {receiver.name}", amount)
            receiver.add_transaction(f"Gift from {self.name}", amount)
            print(f"\n>> Success! ₹{amount} shared with {receiver.name}. What a kind gesture! 🤝")

# --- INITIALIZATION ---
ACC_FILE = "accounts_15.xlsx"
if not os.path.exists(ACC_FILE):
    pd.DataFrame(columns=["Account ID", "Name", "Balance", "PIN"]).to_excel(ACC_FILE, index=False)

accounts = {}
try:
    data = pd.read_excel(ACC_FILE, dtype={"PIN": str, "Account ID": int})
    for _, row in data.iterrows():
        aid = int(row["Account ID"])
        accounts[aid] = Account(aid, row["Name"], float(row["Balance"]), str(row["PIN"]))
except: pass

# --- MAIN ENGINE ---
while True:
    print("\n" + "💖"*10)
    print("  BELONG BANK")
    print("💖"*10)
    print("1. Welcome Back (Login)")
    print("2. Join Our Family (Create Account)")
    print("3. Say Goodbye (Exit)")
    
    choice = clean_input("\nHow can we help you today? ")

    if choice == '1':
        aid_in = clean_input("Please enter your Account ID: ")
        pin_in = clean_input("And your secret 4-digit PIN: ")

        if aid_in.isdigit() and int(aid_in) in accounts:
            user = accounts[int(aid_in)]
            if user.verify_pin(pin_in):
                print(f"\n*** {get_time_greeting()}, {user.name}! It's so good to see you. ***")
                while True:
                    print(f"\n--- {user.name.upper()}'S DASHBOARD ---")
                    print("1. View My Wealth | 2. Add Funds | 3. Withdraw")
                    print("4. Share Wealth (Transfer) | 5. My Story (History) | 6. Logout")
                    u_choice = clean_input("What's on your mind? ")

                    if u_choice == '1': print(f">> {user.name}, your current balance is: ₹{user.get_balance()} 💰")
                    elif u_choice == '2':
                        try:
                            amt = float(clean_input("How much shall we add to your future today? "))
                            user.credit(amt)
                        except: print("!! Please use numbers so we can count it correctly.")
                    elif u_choice == '3':
                        try:
                            amt = float(clean_input("How much do you need for today's plans? "))
                            user.debit(amt)
                        except: print("!! Please use numbers so we can count it correctly.")
                    elif u_choice == '4':
                        try:
                            rid = int(clean_input("Who is the lucky receiver (ID)? "))
                            amt = float(clean_input("How much would you like to share? "))
                            if rid in accounts: user.transfer_money(accounts[rid], amt)
                            else: print("!! We couldn't find that person in our banking family.")
                        except: print("!! We need a valid ID and amount to share.")
                    elif u_choice == '5': user.show_transactions()
                    elif u_choice == '6':
                        print(f"\nTake care, {user.name}. Your future is safe with us. ✨")
                        break
            else: print("!! That PIN doesn't seem to match. Let's try again carefully.")
        else: print("!! We couldn't find that ID. Are you sure you've joined our family yet?")

    elif choice == '2':
        try:
            print("\n--- We're so excited to have you join us! ---")
            
            while True:
                aid_raw = clean_input("Choose your unique ID number: ")
                if aid_raw.isdigit():
                    new_id = int(aid_raw)
                    if new_id in accounts: print("!! That ID is already cherished by a family member.")
                    else: break
                else: print("!! Please use numbers for your ID.")

            name = clean_input("What shall we call you? ")

            while True:
                bal_raw = clean_input(f"Welcome, {name}! How much would you like to start your journey with? ")
                try:
                    bal = float(bal_raw)
                    if bal <= 0: print("!! A new journey deserves a fresh start! Please deposit at least ₹1.")
                    else: break
                except: print("!! Please enter the amount in numbers.")

            while True:
                pin = clean_input("Set your secret 4-digit PIN: ")
                if len(pin) == 4 and pin.isdigit(): break
                else: print("!! For your safety, the PIN must be exactly 4 numbers.")

            h_pin = hash_pin(pin)
            accounts[new_id] = Account(new_id, name, bal, h_pin)
            
            # FUTURE-PROOF SAVING LOGIC
            df = pd.read_excel(ACC_FILE)
            new_row = pd.DataFrame([{"Account ID": new_id, "Name": name, "Balance": bal, "PIN": h_pin}])
            
            if df.empty:
                df = new_row
            else:
                df = pd.concat([df, new_row], ignore_index=True)
                
            df.to_excel(ACC_FILE, index=False)
            print(f"\n*** Welcome to the family, {name}! Your journey begins now. ***")

        except: print("!! We had a little trouble setting that up. Let's try again.")

    elif choice == '3':
        print("\nThank you for spending time with Belong Bank. Have a beautiful day! 👋")
        break