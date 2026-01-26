from face.register import register_patient
from face.recognize import recognize_face
from tools.medication_menu import medication_menu
from tools.delete_patient import delete_patient
def main():
    while True:
        print("\n1. Register Patient")
        print("2. Recognize Patient")
        print("3. Medication Menu")
        print("4. Delete Patient")
        print("5. Logs")
        print("q. Quit")

        choice = input("Choose option: ").strip()

        if choice == "1":
            register_patient()
        elif choice == "2":
            recognize_face()
        elif choice == "3":
            medication_menu()
        elif choice == "4":
            delete_patient()
        elif choice == "5":
            from tools.logger import view_logs
            view_logs()
        elif choice.lower() == "q":
            break
        else:
            print("[ERROR] Invalid choice")

if __name__ == "__main__":
    main()
