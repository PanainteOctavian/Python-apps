from datetime import datetime
from functional import seq
from dateutil.relativedelta import relativedelta
from typing import Sequence


class Person:
    def __init__(self, first_name: str, last_name: str, date_of_birth: datetime, email_address: str) -> None:
        self.firstName = first_name
        self.lastName = last_name
        self.dateOfBirth = date_of_birth
        self.emailAddress = email_address

    def __repr__(self) -> str:
        return f"{self.firstName} {self.lastName}, {self.dateOfBirth.strftime('%d %b %Y')}"


if __name__ == '__main__':
    persons = seq([
        Person("Michael", "Brown", datetime(1960, 11, 3), "mbrown@example.com"),
        Person("Sarah", "Johnson", datetime(1992, 5, 13), "sjohnson@example.com"),
        Person("Emily", "Davis", datetime(1986, 2, 1), "edavis@example.com"),
        Person("David", "Wilson", datetime(1999, 11, 6), "dwilson@example.com"),
        Person("Robert", "Taylor", datetime(1975, 7, 14), "rtaylor@example.com"),
        Person("Olivia", "Martinez", datetime(2007, 5, 28), "")
    ])

    youngest: Sequence = persons.order_by(lambda person: person.dateOfBirth).last()
    oldest: Sequence = persons.order_by(lambda person: person.dateOfBirth).first()
    print(f"youngest person is: {youngest}")
    print(f"oldest person is: {oldest}\n")

    underage: Sequence = persons.filter(
        lambda person: relativedelta(datetime.now(), person.dateOfBirth).years < 18).to_list()
    print(f"underage: {underage}\n")

    emails: Sequence = persons.map(lambda person: person.emailAddress).to_list()
    print(f"emails: {emails}\n")

    emails_map: Sequence = persons.map(
        lambda person: (f"{person.firstName} {person.lastName}", person.emailAddress)).to_dict()
    print(f"emails: {emails_map}\n")

    email_person_map: Sequence = persons.map(lambda person: (person.emailAddress, person)).to_dict()
    print(email_person_map)

    people_to_celebrate_each_month: Sequence = persons.group_by(lambda person: person.dateOfBirth.month)
    print(f"birthdays each month: {people_to_celebrate_each_month}\n")

    map_by_birth_year: Sequence = persons.partition(lambda person: person.dateOfBirth.year <= 1980)
    print(f"born before / after 1980 : {map_by_birth_year}\n")

    names: str = persons.map(lambda person: person.firstName).distinct().make_string(", ")
    print(f"first names: {names}\n")

    average_age: float = persons.map(lambda person: relativedelta(datetime.now(), person.dateOfBirth).years).average()
    print(f"Average age: {average_age}\n")

    taylors: Sequence = persons.filter(lambda person: person.lastName == "Taylor").len()  # Fixed case sensitivity
    print(f"number of people called Taylor: {taylors}\n")

    optional: Sequence = persons.filter(lambda person: person.firstName == "Olivia").first(None)
    if optional is not None:
        print(optional)
    else:
        print("No one named Olivia was found")

    try:
        search_result: Sequence = next(person for person in persons if person.lastName == "Wilson")  # Fixed: searching last name
    except StopIteration:
        search_result: str = "No one with last name Wilson was found."

    print(search_result)

    no_email: bool = any(person.emailAddress == "" for person in persons)
    print(f"any with missing email: {no_email}")