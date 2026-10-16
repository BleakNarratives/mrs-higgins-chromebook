import os
import json
import time
import sys

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    header = r"""
  __________________________________________________________________
 /                                                                  \
 |   ____________________________________________________________   |
 |  |                                                            |  |
 |  |  MRS. HIGGINS FRONT DESK v1.0 (1984)                       |  |
 |  |  Status: NON-FILTERED SMOKE DETECTED                       |  |
 |  |____________________________________________________________|  |
 |                                                                  |
 |      [ 1 ] DAILY BRIEFING        [ 2 ] THE LEDGER                |
 |      [ 3 ] SHIP IT! (Pipeline)   [ 4 ] QUIT                      |
 |                                                                  |
 \__________________________________________________________________/
          ||                                      ||
    ______||______________________________________||______
   /                                                      \
  /    ( )  ( )  ( )        [ MOTHBALLS ]       ( )  ( )   \
 /__________________________________________________________\
    """
    print(header)

def show_briefing():
    clear()
    print("--- DAILY BRIEFING ---")
    os.system('python3 briefing.py')
    input("\nPress ENTER to return to desk...")

def show_ledger():
    clear()
    print("--- THE LEDGER ---")
    if os.path.exists('the_ledger_report.txt'):
        with open('the_ledger_report.txt', 'r') as f:
            print(f.read())
    else:
        print("No ledger report found. Run the pipeline first.")
    input("\nPress ENTER to return to desk...")

def ship_it():
    clear()
    print("!!! INITIATING PIPELINE !!!")
    print("Mrs. Higgins is typing furiously...")
    time.sleep(1)
    os.system('bash mrs_higgins.sh')
    print("\n--- PIPELINE COMPLETE ---")
    input("\nPress ENTER to return to desk...")

def main():
    while True:
        clear()
        print_header()
        print("\n[Mrs. Higgins] \"What do you want? I'm busy.\"\n")
        choice = input("Select an option: ")

        if choice == '1':
            show_briefing()
        elif choice == '2':
            show_ledger()
        elif choice == '3':
            ship_it()
        elif choice == '4':
            print("\n\"Finally. Don't let the door hit you.\"")
            break
        else:
            print("\n\"Are you illiterate? Pick 1, 2, 3, or 4.\"")
            time.sleep(1)

if __name__ == "__main__":
    main()
