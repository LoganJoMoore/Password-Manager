import os, time
import pandas as pd
from cryptography.fernet import Fernet

csvFile = 'data.csv'    #Main Files - Global
keyFile = 'key.key'
pinFile = 'pin.csv'

def create_csv():
    data = {'Name': [], 'Website': [], 'Email': [], 'Password': []}
    df = pd.DataFrame(data)
    df.to_csv(csvFile, index = False)

def create_pin(pin, key):
    encrypted_pin = encrypt_password(pin, key)
    data = {'PIN': [encrypted_pin]}
    df = pd.DataFrame(data)
    df.to_csv(pinFile, index = False)

def reset_pin(key):
    attempts = 3
    old_pin = 0
    pin = get_pin(key)
    while old_pin != pin:
        if attempts == 0:
            print("Exiting Pin Reset")
            break
        old_pin = (input("\nEnter old pin: "))
        if old_pin == pin:
            reset_pin = input("What would you like the updated pin to be?: ")
            encrypted_pin = encrypt_password(reset_pin, key)

            data = {'PIN': [encrypted_pin]}
            df = pd.DataFrame(data)
            df.to_csv(pinFile, index = False)

            print("Pin has successfully been updated!")
            break
        attempts -= 1
        print(f"Incorrect pin. you have {attempts} more attempts left.")

def get_pin(key):
    df = pd.read_csv(pinFile)
    dfS = df[df['PIN'].str.contains('', na = False, case = False)]
    pin = dfS.loc[0, 'PIN']
    pin = decrypt_password(pin, key)
    return pin

def create_key():
    key = Fernet.generate_key()
    with open(keyFile, "wb") as file:
        file.write(key)
    return key

def load_key():
    file = open(keyFile, "rb")
    key = file.read()
    file.close()
    return key

def encrypt_password(account_password, key):
    fer = Fernet(key)
    encrypted_password = fer.encrypt(account_password.encode()).decode()
    return encrypted_password

def decrypt_password(find_password, key):
    fer = Fernet(key)
    decrypted_password = fer.decrypt(find_password.encode()).decode()
    return decrypted_password

def add_account(key):
    account_name = input("\nEnter name of the account: ")

    df = pd.read_csv(csvFile)

    if account_name in df['Name'].values:
        print("Name already exists. Going back to menu.")
        return

    account_website = input("Enter website of the account: ")
    account_email = input("Enter email of the account: ")
    account_password = input("Enter password of the account: ")
    encrypted_password = encrypt_password(account_password, key)
    
    data_input = {'Name': [account_name], 'Website': [account_website], 'Email': [account_email], 'Password': [encrypted_password]}
    df = pd.DataFrame(data_input)
    df.to_csv(csvFile, mode = 'a', header = False, index = False)

    print("Account has successfully been added!")

def show_account(key):
    try:
        search_name = input("\nWhat is the name of the account?: ")
        df = pd.read_csv(csvFile)
        dfS = df[df['Name'] == search_name]
        index = df.loc[df['Name'] == search_name].index[0]

        find_name = dfS.loc[index, 'Name']
        find_website = dfS.loc[index, 'Website']
        find_email = dfS.loc[index, 'Email']
        find_password = dfS.loc[index, 'Password']
        
        decrypted_password = (decrypt_password(find_password, key))

        print(f"\nAccount Name: {find_name}")
        print(f"Account Website: {find_website}")
        print(f"Account Email: {find_email}")
        print(f"Account Password: {decrypted_password}")
    except(UnboundLocalError, IndexError):
        print("Invalid account name. Going back to menu.")

def show_all_accounts():
    df = pd.read_csv(csvFile)
    dfS = df[df['Name'].str.contains('',na = False, case = False)]

    print("\nAccounts:")
    count = 1

    for index, row in dfS.iterrows():
        print(f"{count}. {dfS.loc[index, 'Name']}")
        count += 1

def update_account(key):
    df = pd.read_csv(csvFile)

    try:
        old_name = input("\nWhat is the name of the account you want to update?: ")
        index = df.loc[df['Name'] == old_name].index[0]
    except(IndexError, KeyError):
        print("Invalid account name. Going back to menu.")
        return

    update_name = input("What would like the new name to be?: ")
    update_website = input("What would you like the website name to be?: ")
    update_email = input("What would you like the email to be?: ")
    update_password = input("What would you like the password to be?: ")
    encrypted_password = encrypt_password(update_password, key)

    df.loc[index, ['Name', 'Website', 'Email', 'Password']] = [update_name, update_website, update_email, encrypted_password]
    df.to_csv(csvFile, index = False)

    print("Account has successfully been updated!")

def remove_account(key):
    df = pd.read_csv(csvFile)

    try:
        delete_name = input("\nWhat is the name of the account you want to remove?: ")
        index = df.loc[df['Name'] == delete_name].index[0]
    except(IndexError, KeyError):
        print("Invalid account name. Going back to menu.")
        return
    
    check_password = input(f"To confirm, enter the password for {delete_name}: ")
    if check_password != decrypt_password(df.loc[index, 'Password'], key):
        print("Wrong password. Going back to menu.")
        return

    df.drop([index], axis = 0, inplace = True)
    df.to_csv(csvFile, index = False)

    print("Account has successfully been deleted!")

def main():

    isCSV = os.path.isfile(csvFile)     #Checking for Files
    isKey = os.path.isfile(keyFile)
    isPIN = os.path.isfile(pinFile)
    
    print("\nWelcome to Password Manager!")

    if not isCSV:
        create_csv()
        
    if not isKey:
        key = create_key()
    else:
        key = load_key()
    
    if not isPIN:
        pin = input("Create your new pin: ")
        create_pin(pin, key)

    pin = get_pin(key)
    input_pin = 0
    attempts = 3

    while input_pin != pin:     #Verify PIN to Enter Password Manager
        if attempts == 0:
            print("Exiting Password Manager.")
            quit()
        input_pin = (input("Enter your pin to unlock: "))
        if input_pin == pin:
            break
        attempts -= 1
        print(f"Incorrect pin. you have {attempts} more attempts left.")

    while True:     #Options
        print("\nWhat would you like to do?")
        print("1. Add an Account")
        print("2. Show an Account")
        print("3. Update Account")
        print("4. Remove Account")
        print("5. List ALL Accounts")
        print("6. Reset PIN")
        print("7. Exit")

        options = ['1', '2', '3', '4', '5', '6', '7']
        sleep_time = 2

        while True:     #Enter choice(1/2/3...)
            user_choice = (input("Enter your choice (1/2/3/4/5/6/7): "))
            if user_choice in options: 
                user_choice = int(user_choice)
                break
            else: 
                print("\nThat is not a valid option/number. Please try again.")
            
        if user_choice == 1:        #Add Account
            add_account(key)
            time.sleep(sleep_time)
        
        if user_choice == 2:        #Show Account
            show_account(key)
            time.sleep(sleep_time)

        if user_choice == 3:        #Update Account
            update_account(key)
            time.sleep(sleep_time)

        if user_choice == 4:        #Remove Account
            remove_account(key)
            time.sleep(sleep_time)

        if user_choice == 5:        #Show ALL Accounts
            show_all_accounts()
            time.sleep(sleep_time)

        if user_choice == 6:        #Reset PIN
            reset_pin(key)
            time.sleep(sleep_time)

        if user_choice == 7:        #Exit Password Manager
            print("Now Exiting...")
            time.sleep(sleep_time/2)
            quit()

main()
