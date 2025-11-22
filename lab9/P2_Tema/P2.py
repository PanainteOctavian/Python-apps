from abc import ABCMeta, abstractmethod
from typing import List, Union

class State(metaclass=ABCMeta):
    pass

class Observer(metaclass=ABCMeta):
    @abstractmethod
    def update(self, parameter: Union[State, float]) -> None:
        ...

class Observable(metaclass=ABCMeta):
    @abstractmethod
    def attach(self, observer: Observer) -> None:
        ...

    @abstractmethod
    def detach(self, observer: Observer) -> None:
        ...

    @abstractmethod
    def notify_all(self) -> None:
        ...

class ChoiceObserver(Observer):
    def update(self, parameter: State) -> None:
        if isinstance(parameter, SelectProduct):
            print("Se selecteaza produsul...")
        elif isinstance(parameter, CocaCola):
            print("S-a selectat Coca-Cola(7 lei).")
        elif isinstance(parameter, Pepsi):
            print("S-a selectat Pepsi(6.5 lei).")
        elif isinstance(parameter, Sprite):
            print("S-a selectat Sprite(6.1 lei).")


class SelectProductSTM(Observable):
    def __init__(self) -> None:
        self.__observers: List[ChoiceObserver] = []
        self.__select_product_state: SelectProduct = SelectProduct(self)
        self.__coca_cola_state: CocaCola = CocaCola(self)
        self.__pepsi_state: Pepsi = Pepsi(self)
        self.__sprite_state: Sprite = Sprite(self)
        self.__current_state: State = self.__select_product_state

    def attach(self, observer: ChoiceObserver) -> None:
        print("S-a atasat un observer pentru selectarea produsului!")
        self.__observers.append(observer)

    def detach(self, observer: ChoiceObserver) -> None:
        print("S-a detasat un observer pentru selectarea produsului!")
        self.__observers.remove(observer)

    def notify_all(self) -> None:
        print("Se notifica observerii...")
        for observer in self.__observers:
            observer.update(self.__current_state)

    def get_state(self):
        if isinstance(self.__current_state, CocaCola):
            return self.__coca_cola_state
        if isinstance(self.__current_state, Pepsi):
            return self.__pepsi_state
        return self.__sprite_state

    def choose_another_product(self, state: str) -> None:
        if state == "CocaCola":
            self.__current_state = self.__coca_cola_state
        elif state == "Pepsi":
            self.__current_state = self.__pepsi_state
        elif state == "Sprite":
            self.__current_state = self.__sprite_state
        elif state == "Select":
            self.__current_state = self.__select_product_state
            self.__current_state.choose()


class SelectProduct(State):
    def __init__(self, state_machine: SelectProductSTM) -> None:
        self.__state_machine: SelectProductSTM = state_machine
        self.__price: float

    def choose(self) -> None:
        option: int = -1
        while option < 1 or option > 4:
            print("1. CocaCola(7 lei)")
            print("2. Pepsi(6.5 lei)")
            print("3. Sprite(6.1 lei)")
            option: int = int(input("Dati optiunea: "))
            if option < 1 or option > 4:
                print("Optiune imposibila!")
            else:
                if option == 1:
                    self.__state_machine.choose_another_product("CocaCola")
                elif option == 2:
                    self.__state_machine.choose_another_product("Pepsi")
                elif option == 3:
                    self.__state_machine.choose_another_product("Sprite")


class CocaCola(State):
    def __init__(self, state_machine: SelectProductSTM) -> None:
        self.__state_machine: SelectProductSTM = state_machine
        self.__price: float = 7.0

    def get_price(self) -> float:
        return self.__price


class Pepsi(State):
    def __init__(self, state_machine: SelectProductSTM) -> None:
        self.__state_machine: SelectProductSTM = state_machine
        self.__price: float = 6.5

    def get_price(self) -> float:
        return self.__price


class Sprite(State):
    def __init__(self, state_machine: SelectProductSTM) -> None:
        self.__state_machine: SelectProductSTM = state_machine
        self.__price: float = 6.1

    def get_price(self) -> float:
        return self.__price


class DisplayObserver(Observer):
    def update(self, parameter: float) -> None:
        print(f"Aparatul are {parameter} lei.")


class TakeMoneySTM(Observable):
    def __init__(self) -> None:
        self.__observers: List[DisplayObserver] = []
        self.__wait_state: WaitingForClient = WaitingForClient(self)
        self.__insert_money_state: InsertMoney = InsertMoney(self)
        self.__current_state: State = self.__wait_state
        self.__money: float = 0.0

    def attach(self, observer: DisplayObserver) -> None:
        print("S-a atasat un observer pentru luarea banilor!")
        self.__observers.append(observer)

    def detach(self, observer: DisplayObserver) -> None:
        print("S-a detasat un observer pentru luarea banilor!")
        self.__observers.remove(observer)

    def notify_all(self) -> None:
        print("Se notifica observerii...")
        for observer in self.__observers:
            observer.update(self.__money)

    def add_money(self, value: float) -> None:
        self.__money += value
        self.notify_all()

    def update_amount_of_money(self, value: float) -> None:
        self.__money = value
        self.notify_all()

    def get_money(self) -> float:
        return self.__money

    def get_state(self):
        if isinstance(self.__current_state, WaitingForClient):
            return self.__wait_state
        return self.__insert_money_state

    def change_state(self) -> None:
        if isinstance(self.__current_state, WaitingForClient):
            self.__current_state = self.__insert_money_state
        else:
            self.__current_state = self.__wait_state


class WaitingForClient(State):
    def __init__(self, state_machine: TakeMoneySTM) -> None:
        self.__state_machine: TakeMoneySTM = state_machine

    def client_arrived(self) -> None:
        print("Se asteapta un client...")
        input("Apasati orice tasta pentru a incepe.")
        print("Clientul a ajuns.")
        self.__state_machine.change_state()


class InsertMoney(State):
    def __init__(self, state_machine: TakeMoneySTM) -> None:
        self.__state_machine: TakeMoneySTM = state_machine

    def insert_10bani(self) -> None:
        self.__state_machine.add_money(0.1)

    def insert_50bani(self) -> None:
        self.__state_machine.add_money(0.5)

    def insert_1leu(self) -> None:
        self.__state_machine.add_money(1)

    def insert_5lei(self) -> None:
        self.__state_machine.add_money(5)

    def insert_10lei(self) -> None:
        self.__state_machine.add_money(10)


class VendingMachineSTM:
    def __init__(self) -> None:
        self.__take_money_stm: TakeMoneySTM = TakeMoneySTM()
        self.__select_product_stm: SelectProductSTM = SelectProductSTM()
        self.__take_money_stm.attach(DisplayObserver())
        self.__select_product_stm.attach(ChoiceObserver())

    def proceed_to_checkout(self) -> None:
        self.__select_product_stm.choose_another_product("Select")
        price: float = self.__select_product_stm.get_state().get_price()
        self.__take_money_stm.get_state().client_arrived()
        while self.__take_money_stm.get_money() < price:
            print(f"Pretul produsului este {price}, dumneavoasta aveti doar {self.__take_money_stm.get_money()}, cat doriti sa puneti: ")
            option: int = -1
            while option < 1 or option > 5:
                print("1. 10 bani")
                print("2. 50 bani")
                print("3. 1 leu")
                print("4. 5 lei")
                print("5. 10 lei")
                option: int = int(input("Dati optiunea: "))
                if option < 1 or option > 5:
                    print("Optiune imposibila!")
                else:
                    if option == 1:
                        self.__take_money_stm.get_state().insert_10bani()
                    elif option == 2:
                        self.__take_money_stm.get_state().insert_50bani()
                    elif option == 3:
                        self.__take_money_stm.get_state().insert_1leu()
                    elif option == 4:
                        self.__take_money_stm.get_state().insert_5lei()
                    elif option == 5:
                        self.__take_money_stm.get_state().insert_10lei()
            if self.__take_money_stm.get_money() >= price:
                print("S-a eliberat produsul!")
                print("Doriti sa selectati un alt produs sau sa luati restul?")
                option: int = -1
                while option < 1 or option > 2:
                    print("1. Selectati alt produs")
                    print("2. Luati restul")
                    option: int = int(input("Dati optiunea: "))
                    if option < 1 or option > 2:
                        print("Optiune imposibila!")
                    else:
                        if option == 1:
                                self.__select_product_stm.choose_another_product("Select")
                                self.__take_money_stm.add_money(-price)
                                price: float = self.__select_product_stm.get_state().get_price()
                                self.__take_money_stm.change_state()
                                self.__take_money_stm.get_state().client_arrived()
                        else:
                                self.__take_money_stm.update_amount_of_money(0)
                                print("S-a eliberat restul, o zi buna!")
                                return


if __name__ == "__main__":
    VendingMachineSTM().proceed_to_checkout()
