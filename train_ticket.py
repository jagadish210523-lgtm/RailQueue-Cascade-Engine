import json
import os
import random
class Passenger:
    def __init__(self, name: str, age: int, gender: str, preferred_berth: str):
        """Initializes a passenger instance with sanitized booking details."""
        self.name = name.strip().title()
        self.age = int(age)
        self.gender = gender.strip().capitalize()
        self.preferred_berth = preferred_berth.strip().upper()
    def to_dict(self):
        """Converts passenger object to a clean dictionary for JSON saving."""
        return {
            "name": self.name,
            "age": self.age,
            "gender": self.gender,
            "preferred_berth": self.preferred_berth
        }
    def __str__(self):
        """Readable text representation of a passenger."""
        return f"{self.name} ({self.age}/{self.gender[0]})"
class Train:
    def __init__(self, train_name: str, total_seats: int, storage_file="train_data.json"):
        """Initializes the train data structure and loads existing bookings."""
        self.train_name = train_name
        self.total_seats = total_seats
        self.storage_file = storage_file
        self.seats = {}
        self.waiting_list = []
        if not self._load_data():
            self.generate_seats()
    def generate_seats(self):
        for seat_num in range(1, self.total_seats + 1):
            if seat_num % 3 == 1:
                berth_type = "LOWER"
            elif seat_num % 3 == 2:
                berth_type = "MIDDLE"
            else:
                berth_type = "UPPER"
            self.seats[str(seat_num)] = {
                "berth_type": berth_type,
                "is_available": True,
                "passenger": None,
                "pnr": None
            }
    def _save_data(self):
        try:
            formatted_seats = {}
            for seat_id, details in self.seats.items():
                formatted_seats[seat_id] = {
                    "berth_type": details["berth_type"],
                    "is_available": details["is_available"],
                    "pnr": details["pnr"],
                    "passenger": details["passenger"].to_dict() if details["passenger"] else None
                }
            formatted_wl = [p.to_dict() for p in self.waiting_list]
            data_to_save = {
                "seats": formatted_seats,
                "waiting_list": formatted_wl
            }
            with open(self.storage_file, 'w') as file:
                json.dump(data_to_save, file, indent=4)
        except Exception as e:
            print(f"[Storage Error] Failed to write data: {e}")
    def _load_data(self):
        if not os.path.exists(self.storage_file):
            return False
        try:
            with open(self.storage_file, 'r') as file:
                data = json.load(file)
                for seat_id, details in data["seats"].items():
                    p_data = details["passenger"]
                    passenger_obj = Passenger(p_data["name"], p_data["age"], p_data["gender"], p_data["preferred_berth"]) if p_data else None
                    self.seats[seat_id] = {
                        "berth_type": details["berth_type"],
                        "is_available": details["is_available"],
                        "pnr": details["pnr"],
                        "passenger": passenger_obj
                    }
                self.waiting_list = []
                for p_data in data["waiting_list"]:
                    self.waiting_list.append(Passenger(p_data["name"], p_data["age"], p_data["gender"], p_data["preferred_berth"]))
                return True
        except Exception:
            print("[Warning] Could not parse save file. Starting fresh.")
            return False
    def book_ticket(self, passenger: Passenger):
        pnr = random.randint(10000, 99999)
        for seat_id, details in self.seats.items():
            if details["is_available"] and details["berth_type"] == passenger.preferred_berth:
                details["is_available"] = False
                details["passenger"] = passenger
                details["pnr"] = pnr
                print(f"\n🎉 SUCCESS: Confirmed Seat {seat_id} ({details['berth_type']}) allocated! PNR: {pnr}")
                self._save_data()
                return
        for seat_id, details in self.seats.items():
            if details["is_available"]:
                details["is_available"] = False
                details["passenger"] = passenger
                details["pnr"] = pnr
                print(f"\n⚠️ PREFERENCE FULL: Allocated alternative Seat {seat_id} ({details['berth_type']}). PNR: {pnr}")
                self._save_data()
                return
        self.waiting_list.append(passenger)
        wl_position = len(self.waiting_list)
        print(f"\n🛑 TRAIN FULL: Added to Waiting List. Current Position: WL-{wl_position}")
        self._save_data()
    def cancel_ticket(self, seat_number: int):
        seat_str = str(seat_number)
        if seat_str not in self.seats:
            print("[Error] Invalid seat number entered.")
            return
        target_seat = self.seats[seat_str]
        if target_seat["is_available"]:
            print("[Error] This seat is already vacant.")
            return
        print(f"\nCancelling ticket for seat {seat_number} (PNR: {target_seat['pnr']})...")
        if len(self.waiting_list) > 0:
            promoted_passenger = self.waiting_list.pop(0)
            new_pnr = random.randint(10000, 99999)
            target_seat["passenger"] = promoted_passenger
            target_seat["pnr"] = new_pnr
            print(f"🔄 CASCADE: {promoted_passenger.name} promoted from Waitlist to Seat {seat_number}!")
        else:
            target_seat["is_available"] = True
            target_seat["passenger"] = None
            target_seat["pnr"] = None
            print(f"✅ Seat {seat_number} is now vacant.")
        self._save_data()
    def display_chart(self):
        print("\n" + "="*50)
        print(f" SEATING CHART FOR {self.train_name.upper()} ".center(50, "="))
        print(f"{'Seat':<6} {'Berth Type':<12} {'Status':<12} {'Passenger Details'}")
        print("="*50) 
        for seat_id, details in sorted(self.seats.items(), key=lambda x: int(x[0])):
            status = "VACANT" if details["is_available"] else f"PNR:{details['pnr']}"
            p_info = details["passenger"] if details["passenger"] else "-"
            print(f"{seat_id:<6} {details['berth_type']:<12} {status:<12} {p_info}")     
        print("-"*50)
        print(f"Waiting List Queue Count: {len(self.waiting_list)}")
        for idx, wl_passenger in enumerate(self.waiting_list, 1):
            print(f" - Position WL-{idx}: {wl_passenger.name}")
        print("="*50)
def main():
    my_train = Train(train_name="Deccan Express", total_seats=5)
    while True:
        print("\n=== CORE RAILWAY MANAGEMENT SYSTEM ===")
        print("1. Book a Ticket")
        print("2. Cancel a Ticket")
        print("3. View Reservation Chart")
        print("4. Exit Application")
        choice = input("\nEnter your selection (1-4): ").strip()
        if choice == "1":
            print("\n--- ENTER PASSENGER INFORMATION ---")
            name = input("Enter Name: ")
            age = input("Enter Age: ")
            gender = input("Enter Gender (M/F): ") 
            print("Available Berths: LOWER, MIDDLE, UPPER")
            berth_pref = input("Enter Choice: ").strip().upper()
            if berth_pref not in ["LOWER", "MIDDLE", "UPPER"]:
                print("[Error] Invalid berth preference chosen.")
                continue
            try:
                new_passenger = Passenger(name, age, gender, berth_pref)
                my_train.book_ticket(new_passenger)
            except ValueError:
                print("[Error] Age validation failed. Please enter an integer.")
        elif choice == "2":
            try:
                seat_to_cancel = int(input("\nEnter the Seat Number to cancel: "))
                my_train.cancel_ticket(seat_to_cancel)
            except ValueError:
                print("[Error] Please enter a valid numerical seat value.")
        elif choice == "3":
            my_train.display_chart() 
        elif choice == "4":
            print("\nSystem data saved. Closing application safely. Goodbye!")
            break
        else:
            print("[Error] Please enter a valid menu response (1-4).")
if __name__ == "__main__":
    main()