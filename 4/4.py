from collections import UserDict
import re
from datetime import datetime, timedelta 
import pickle

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    pass

class Birthday(Field):
    def __init__(self, value):
        pattern = r"^(0[1-9]|[12][0-9]|3[01])\.(0[1-9]|1[0-2])\.(\d{4})$"
        if not re.match(pattern, value):
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
        else:
            self.value = datetime.strptime(value, "%d.%m.%Y").date()
            

class Phone(Field):
    pattern = r'^\d{10}$'
    def __init__(self, value):
        if re.match(self.pattern, value):
            super().__init__(value)
        else:
            raise ValueError("Wrong number format, number should contain 10 digits")

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone (self, phone):
        phone = Phone(phone)
        self.phones.append(phone)

    def add_birthday (self, birthday):
        birthday = Birthday(birthday)
        self.birthday = birthday.value
    
    def remove_phone(self, phone):
        for p in self.phones:
            if p.value == phone:  
                self.phones.remove(p)
                return
        raise ValueError("Phone not found in the record")
        
    def edit_phone(self, old_phone, new_phone):
        for p in self.phones:  
            if p.value == old_phone:  
                p.value = new_phone 
                return  
        raise ValueError("Phone not found in the record")  
            
        
    def find_phone(self, phone):
        for p in self.phones:  
            if p.value == phone:  
                return  p.value
        raise ValueError("Phone not found in the record")  


    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}, birthday: {self.birthday}"

class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name, None)

    def delete(self, name):
        if name in self.data:
            del self.data[name]
        else:
            raise KeyError(f"Record with name '{name}' not found")
        
def get_upcoming_birthdays(contacts):
    today_date = datetime.today().date()
    birthday_period_end = today_date + timedelta(days=7)
    upcoming_birthdays = []

    for user in contacts:
        if not user.birthday:
            continue  

        user_birthday_this_year = user.birthday.replace(year=today_date.year)

        if user_birthday_this_year < today_date:
            user_birthday_this_year = user_birthday_this_year.replace(year=today_date.year + 1)

        if today_date <= user_birthday_this_year <= birthday_period_end:
            if user_birthday_this_year.weekday() in [5, 6]:  
                days_to_monday = 7 - user_birthday_this_year.weekday()
                user_birthday_this_year += timedelta(days=days_to_monday)

            upcoming_birthdays.append({
                "name": user.name.value,
                "congratulation_date": user_birthday_this_year.strftime("%Y-%m-%d")
            })

    if not upcoming_birthdays:
        print("В найближчі 7 днів немає дат для привітання")
        return []

    print("Список привітань на цьому тижні:", upcoming_birthdays)
    return upcoming_birthdays




def parse_input(user_input):
    if not user_input.strip():  
        return "", []  
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, args

def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError:
            return "Give me name and phone please."
        except KeyError:
            return "There is no contact with this name."
        except IndexError:
            return "Give me name."
        except Exception as e:
            return f"An unexpected error occurred: {str(e)}"
    return inner

@input_error
def add_contact(args, book: AddressBook):
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message


@input_error
def change_contact(args, book: AddressBook):
    name, old_phone, new_phone = args
    message = "Phone updated."
    record = book.find(name)
    if record is None:
        return "There is no contact with this name"
    phone_found = None
    for phone in record.phones:
        if phone.value == old_phone:
            phone_found = phone
            break
    if phone_found:
        phone_found.value = new_phone 
        return message
    else:
        return "There is no such phone in this contact"

@input_error
def add_day_of_birthday(args, book: AddressBook):
    name, birthday = args
    record = book.find(name)
    if record is None:
        return "There is no contact with this name"
    if record.birthday is None:
        record.add_birthday(birthday)
        message = f"Birthday added to record {name}."
        return message
    return "Birthday already exists for this contact."

@input_error
def show_day_of_birthday (args, book: AddressBook):
    name = args[0]
    record = book.find(name)
    if record.birthday is None:
        return "This record dont have information about birthday"
    return f"{name}'s birthday: {record.birthday}"
    
    

@input_error
def show_phone(args, book: AddressBook):
    name = args[0]
    record = book.find(name)
    if record is None:
        return "There is no contact with this name"  
    phone_numbers = "; ".join(str(phone) for phone in record.phones)
    return f"{name}'s phone numbers {phone_numbers}"

def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook() 


def main():
    book = load_data()
    print(book)
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, args = parse_input(user_input)

        if command in ["close", "exit"]:
            save_data(book)
            print("Good bye!")
            break
        elif command == "":
            print("You didn't enter any command. Please try again.")
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, book))
        elif command == "change":
            print(change_contact(args, book))
        elif command == "show":
            print(show_phone(args, book))
        elif command == "add-birthday":
            print(add_day_of_birthday(args, book))
        elif command == "show-birthday":
            print(show_day_of_birthday(args, book))
        elif command == "birthdays":
            print(get_upcoming_birthdays(book.values()))
        elif command == "all":
            print("Contacts:")
            for p in book.values():
                print(p)
        else:
            print("Invalid command.")


if __name__ == "__main__":
    main()