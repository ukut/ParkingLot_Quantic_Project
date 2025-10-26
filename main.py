"""
main.py - Parking Management System Interactive Demo

This script demonstrates all features of the refactored parking management system:
- Factory Pattern for vehicle creation
- Strategy Pattern for dynamic pricing
- Decorator Pattern for electric vehicles
- Observer Pattern for event notifications

Run this script to see the system in action!
"""

from datetime import datetime, timedelta
from Vehicle_Refactored import (
    Vehicle, VehicleType, VehicleSpecification, VehicleFactory,
    ChargingCapability, Car, Truck, Motorcycle, Bus
)
from ParkingManager_Refactored import (
    ParkingManager, ParkingSpace, ParkingSpaceSize, ParkingSpaceStatus,
    BasicPricingStrategy, PeakHourPricingStrategy, LoggingObserver,
    ChargingStationObserver
)


def print_header(title):
    """Print a formatted section header."""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)


def print_subheader(title):
    """Print a formatted subsection header."""
    print(f"\n>>> {title}")
    print("-" * 70)


def demo_factory_pattern():
    """Demonstrate the Factory Pattern."""
    print_header("DEMO 1: FACTORY PATTERN - Vehicle Creation")
    
    print_subheader("Creating vehicles using VehicleFactory")
    print("The factory encapsulates all vehicle creation logic.\n")
    
    # Create various vehicle types
    vehicles = [
        VehicleFactory.create_vehicle(
            VehicleType.CAR, "ABC123", "Honda", "Civic", "Blue"
        ),
        VehicleFactory.create_vehicle(
            VehicleType.MOTORCYCLE, "MOT456", "Harley", "Street 750", "Black"
        ),
        VehicleFactory.create_vehicle(
            VehicleType.TRUCK, "TRK789", "Ford", "F-150", "White"
        ),
        VehicleFactory.create_vehicle(
            VehicleType.BUS, "BUS001", "Mercedes", "Sprinter", "Silver"
        ),
    ]
    
    print("Created vehicles:")
    for vehicle in vehicles:
        print(f"  • {vehicle}")
        print(f"    - Type: {vehicle.get_type().value}")
        print(f"    - Parking Space: {vehicle.get_parking_space_size()}\n")
    
    print("✓ Factory Pattern Benefits:")
    print("  - Centralized creation logic (easy to modify)")
    print("  - Type safety (validation happens here)")
    print("  - Loose coupling (client doesn't need to know implementation)")


def demo_decorator_pattern():
    """Demonstrate the Decorator Pattern for electric vehicles."""
    print_header("DEMO 2: DECORATOR PATTERN - Electric Vehicles")
    
    print_subheader("Adding charging capability to regular vehicles")
    print("Using the Decorator pattern, we can add features to any vehicle.\n")
    
    # Create regular vehicles
    regular_car = VehicleFactory.create_vehicle(
        VehicleType.CAR, "CAR001", "Toyota", "Camry", "Red"
    )
    print(f"Regular Car: {regular_car}\n")
    
    # Decorate with charging capability
    electric_car = VehicleFactory.create_electric_vehicle(
        VehicleType.CAR, "EV001", "Tesla", "Model 3", "White", max_charge_kwh=75
    )
    print(f"Electric Car (decorated): {electric_car}\n")
    
    # Charge the vehicle
    print("Charging the electric car...")
    charged = electric_car.charge(50)
    print(f"  Charged: {charged} kWh")
    print(f"  Battery: {electric_car.charge_percentage:.1f}%")
    print(f"  Status: {electric_car}\n")
    
    # Simulate vehicle usage
    print("Simulating vehicle usage (discharge 20 kWh)...")
    discharged = electric_car.discharge(20)
    print(f"  Discharged: {discharged} kWh")
    print(f"  Battery: {electric_car.charge_percentage:.1f}%")
    print(f"  Status: {electric_car}\n")
    
    # Check battery status
    if electric_car.is_low_battery(threshold_percent=50):
        print("⚠️  Battery is low! Needs charging soon.\n")
    
    # Create electric motorcycle
    print("Creating an electric motorcycle...")
    electric_moto = VehicleFactory.create_electric_vehicle(
        VehicleType.MOTORCYCLE, "EMOTO01", "Zero", "SR", "Silver", max_charge_kwh=12
    )
    electric_moto.charge(10)
    print(f"Electric Motorcycle: {electric_moto}\n")
    
    print("✓ Decorator Pattern Benefits:")
    print("  - Add features to objects dynamically")
    print("  - Combine multiple decorators if needed")
    print("  - Avoids explosion of subclasses (ElectricCar, ElectricTruck, etc.)")


def demo_parking_basic():
    """Demonstrate basic parking operations."""
    print_header("DEMO 3: PARKING OPERATIONS - Basic")
    
    print_subheader("Setting up parking lot")
    
    # Create parking manager with basic pricing
    manager = ParkingManager(BasicPricingStrategy())
    
    # Add observers
    manager.attach_observer(LoggingObserver())
    charging_observer = ChargingStationObserver()
    manager.attach_observer(charging_observer)
    
    # Create parking spaces
    spaces = [
        ParkingSpace("C1", ParkingSpaceSize.COMPACT, floor=1, location="A1"),
        ParkingSpace("C2", ParkingSpaceSize.COMPACT, floor=1, location="A2"),
        ParkingSpace("S1", ParkingSpaceSize.STANDARD, floor=1, location="B1"),
        ParkingSpace("S2", ParkingSpaceSize.STANDARD, floor=1, location="B2"),
        ParkingSpace("S3", ParkingSpaceSize.STANDARD, floor=2, location="B3"),
        ParkingSpace("L1", ParkingSpaceSize.LARGE, floor=2, location="C1"),
    ]
    manager.add_multiple_spaces(spaces)
    print(f"Created parking lot with {len(spaces)} spaces\n")
    
    print_subheader("Parking vehicles")
    
    # Create vehicles
    car = VehicleFactory.create_vehicle(
        VehicleType.CAR, "ABC123", "Honda", "Civic", "Blue"
    )
    motorcycle = VehicleFactory.create_vehicle(
        VehicleType.MOTORCYCLE, "MOT456", "Harley", "Street", "Black"
    )
    truck = VehicleFactory.create_vehicle(
        VehicleType.TRUCK, "TRK789", "Ford", "F-150", "White"
    )
    
    # Park vehicles
    ticket1 = manager.park_vehicle(car)
    print(f"✓ Car parked: {ticket1.ticket_id} in {ticket1.space}\n")
    
    ticket2 = manager.park_vehicle(motorcycle)
    print(f"✓ Motorcycle parked: {ticket2.ticket_id} in {ticket2.space}\n")
    
    ticket3 = manager.park_vehicle(truck)
    print(f"✓ Truck parked: {ticket3.ticket_id} in {ticket3.space}\n")
    
    # Show occupancy
    print_subheader("Parking lot status")
    print(f"Occupancy Rate: {manager.get_occupancy_rate():.1f}%")
    print(f"Available Spaces: {manager.get_available_space_count()}")
    print(f"Occupied Spaces: {len(manager.get_parked_vehicles())}\n")
    
    print_subheader("Retrieving vehicles")
    
    # Simulate time passing
    ticket1.entry_time = datetime.now() - timedelta(hours=2)
    ticket2.entry_time = datetime.now() - timedelta(minutes=45)
    
    # Retrieve vehicles
    exit1 = manager.retrieve_vehicle("ABC123")
    print(f"✓ Car retrieved: Charge = ${exit1.charge_amount:.2f}")
    print(f"  Duration: {exit1.get_duration_hours():.2f} hours\n")
    
    exit2 = manager.retrieve_vehicle("MOT456")
    print(f"✓ Motorcycle retrieved: Charge = ${exit2.charge_amount:.2f}")
    print(f"  Duration: {exit2.get_duration_hours():.2f} hours\n")
    
    # Show updated occupancy
    print(f"Available Spaces After Exit: {manager.get_available_space_count()}")
    print(f"Remaining Vehicles: {len(manager.get_parked_vehicles())}\n")
    
    return manager


def demo_strategy_pattern(manager):
    """Demonstrate the Strategy Pattern for pricing."""
    print_header("DEMO 4: STRATEGY PATTERN - Dynamic Pricing")
    
    print_subheader("Switching pricing strategies")
    print("The Strategy pattern allows us to change algorithms at runtime.\n")
    
    # Create multiple vehicles
    vehicles_data = [
        (VehicleType.CAR, "CA001", "Toyota", "Camry", "Red"),
        (VehicleType.CAR, "CA002", "Honda", "Accord", "Blue"),
        (VehicleType.MOTORCYCLE, "MO001", "Suzuki", "GSX-R", "Black"),
        (VehicleType.MOTORCYCLE, "MO002", "Yamaha", "YZF-R1", "White"),
    ]
    
    print("Current Strategy: Basic Hourly Rate")
    print(f"Current Strategy Name: {manager.get_current_strategy_name()}\n")
    
    print("Parking vehicles with BASIC pricing...")
    tickets = []
    for vtype, reg, make, model, color in vehicles_data:
        vehicle = VehicleFactory.create_vehicle(vtype, reg, make, model, color)
        ticket = manager.park_vehicle(vehicle)
        tickets.append(ticket)
    
    # Simulate time passing
    for i, ticket in enumerate(tickets):
        ticket.entry_time = datetime.now() - timedelta(hours=3)
    
    print("Retrieving all vehicles with BASIC pricing...")
    basic_charges = {}
    for reg, _, _, _, _ in vehicles_data:
        exit_ticket = manager.retrieve_vehicle(reg)
        basic_charges[reg] = exit_ticket.charge_amount
        print(f"  {reg}: ${exit_ticket.charge_amount:.2f}")
    
    print("\n" + "-"*70)
    print("SWITCHING TO PEAK HOUR PRICING...")
    manager.set_pricing_strategy(PeakHourPricingStrategy())
    print(f"New Strategy Name: {manager.get_current_strategy_name()}\n")
    
    # Park same vehicles again with peak hour strategy
    print("Parking same vehicles with PEAK HOUR pricing...")
    tickets2 = []
    for vtype, reg, make, model, color in vehicles_data:
        vehicle = VehicleFactory.create_vehicle(vtype, reg, make, model, color)
        # Modify reg number for second parking
        vehicle._specification.registration_number = reg + "_2"
        ticket = manager.park_vehicle(vehicle)
        tickets2.append(ticket)
    
    # Set entry time to peak hour (10 AM)
    peak_time = datetime.now().replace(hour=10, minute=0, second=0)
    for ticket in tickets2:
        ticket.entry_time = peak_time - timedelta(hours=3)
    
    print("Retrieving vehicles parked during PEAK HOURS...")
    peak_charges = {}
    for i, (vtype, reg, _, _, _) in enumerate(vehicles_data):
        exit_ticket = manager.retrieve_vehicle(reg + "_2")
        peak_charges[reg] = exit_ticket.charge_amount
        print(f"  {reg}: ${exit_ticket.charge_amount:.2f}")
    
    print("\n" + "-"*70)
    print("COMPARISON:")
    print(f"{'Vehicle':<10} {'Basic':<12} {'Peak Hour':<12} {'Difference'}")
    print("-"*70)
    for reg in basic_charges:
        basic = basic_charges[reg]
        peak = peak_charges[reg]
        diff = peak - basic
        print(f"{reg:<10} ${basic:>10.2f} ${peak:>10.2f} ${diff:>10.2f}")
    
    print("\n✓ Strategy Pattern Benefits:")
    print("  - Change algorithm at runtime without modifying code")
    print("  - Easy to add new strategies (implement interface)")
    print("  - Each strategy is independently testable")
    print("  - Follows Open/Closed Principle")


def demo_observer_pattern():
    """Demonstrate the Observer Pattern."""
    print_header("DEMO 5: OBSERVER PATTERN - Event Notifications")
    
    print_subheader("Observers receive notifications of events")
    print("The Observer pattern enables loose coupling between components.\n")
    
    # Create parking manager
    manager = ParkingManager(BasicPricingStrategy())
    
    # Attach observers
    logging_observer = LoggingObserver()
    charging_observer = ChargingStationObserver()
    
    manager.attach_observer(logging_observer)
    manager.attach_observer(charging_observer)
    
    print("Attached observers:")
    print("  1. LoggingObserver - Logs all events")
    print("  2. ChargingStationObserver - Detects electric vehicles\n")
    
    # Add parking spaces
    spaces = [
        ParkingSpace("S1", ParkingSpaceSize.STANDARD, floor=1, location="A1"),
    ]
    manager.add_multiple_spaces(spaces)
    
    print_subheader("Event 1: Parking a regular vehicle")
    car = VehicleFactory.create_vehicle(
        VehicleType.CAR, "REG001", "Honda", "Civic", "Blue"
    )
    ticket = manager.park_vehicle(car)
    print()
    
    print_subheader("Event 2: Parking an electric vehicle")
    ev = VehicleFactory.create_electric_vehicle(
        VehicleType.CAR, "EV001", "Tesla", "Model 3", "White", max_charge_kwh=75
    )
    ev.charge(40)
    ticket_ev = manager.park_vehicle(ev)
    print()
    
    print_subheader("Event 3: Retrieving vehicles (space becomes available)")
    manager.retrieve_vehicle("REG001")
    print()
    
    print("✓ Observer Pattern Benefits:")
    print("  - Decouples event producer from event consumers")
    print("  - Easy to add/remove observers")
    print("  - Multiple observers can react to same event")


def demo_reporting():
    """Demonstrate reporting and analytics."""
    print_header("DEMO 6: REPORTING & ANALYTICS")
    
    print_subheader("Setting up parking lot with multiple transactions")
    
    # Create parking manager
    manager = ParkingManager(BasicPricingStrategy())
    manager.attach_observer(LoggingObserver())
    
    # Add parking spaces
    spaces = [
        ParkingSpace("C1", ParkingSpaceSize.COMPACT, floor=1, location="A1"),
        ParkingSpace("C2", ParkingSpaceSize.COMPACT, floor=1, location="A2"),
        ParkingSpace("S1", ParkingSpaceSize.STANDARD, floor=1, location="B1"),
        ParkingSpace("S2", ParkingSpaceSize.STANDARD, floor=1, location="B2"),
        ParkingSpace("L1", ParkingSpaceSize.LARGE, floor=2, location="C1"),
    ]
    manager.add_multiple_spaces(spaces)
    
    # Simulate multiple parking transactions
    print("Processing multiple parking transactions...\n")
    
    transactions = [
        (VehicleType.CAR, "A123", "Toyota", "Camry", "Red", 2),
        (VehicleType.CAR, "B456", "Honda", "Accord", "Blue", 1.5),
        (VehicleType.MOTORCYCLE, "M789", "Harley", "Street", "Black", 0.75),
        (VehicleType.TRUCK, "T001", "Ford", "F-150", "White", 3),
        (VehicleType.CAR, "C111", "Tesla", "Model 3", "Silver", 4),
    ]
    
    for vtype, reg, make, model, color, hours in transactions:
        vehicle = VehicleFactory.create_vehicle(vtype, reg, make, model, color)
        ticket = manager.park_vehicle(vehicle)
        # Simulate time passed
        ticket.entry_time = datetime.now() - timedelta(hours=hours)
        manager.retrieve_vehicle(reg)
        print(f"✓ {vtype.value}: {reg} - {hours} hours")
    
    print("\n" + "-"*70)
    print_subheader("Parking Lot Summary")
    
    summary = manager.get_parking_summary()
    print(f"Total Spaces: {summary['total_spaces']}")
    print(f"Occupied Spaces: {summary['occupied_spaces']}")
    print(f"Available Spaces: {summary['available_spaces']}")
    print(f"Occupancy Rate: {summary['occupancy_rate']:.1f}%")
    print(f"Active Vehicles: {summary['active_vehicles']}")
    print(f"Total Transactions: {summary['total_transactions']}")
    print(f"Current Strategy: {summary['pricing_strategy']}")
    print(f"Total Revenue: ${summary['total_revenue']:.2f}\n")
    
    print_subheader("Revenue Breakdown by Vehicle Type")
    revenue_by_type = manager.get_revenue_by_vehicle_type()
    total = sum(revenue_by_type.values())
    for vtype, amount in revenue_by_type.items():
        percentage = (amount / total * 100) if total > 0 else 0
        print(f"  {vtype.value:<15}: ${amount:>8.2f} ({percentage:>5.1f}%)")
    print(f"  {'TOTAL':<15}: ${total:>8.2f} (100.0%)")


def main():
    """Run all demonstrations."""
    print("\n")
    print("╔" + "═"*68 + "╗")
    print("║" + " "*68 + "║")
    print("║" + "PARKING MANAGEMENT SYSTEM - DESIGN PATTERNS DEMO".center(68) + "║")
    print("║" + " "*68 + "║")
    print("╚" + "═"*68 + "╝")
    
    print("\nThis demo showcases:")
    print("  • Factory Pattern - Encapsulating object creation")
    print("  • Decorator Pattern - Adding features dynamically")
    print("  • Strategy Pattern - Pluggable algorithms")
    print("  • Observer Pattern - Event-driven notifications")
    print("  • SOLID Principles - Maintainable, extensible code")
    
    try:
        # Run demos
        demo_factory_pattern()
        demo_decorator_pattern()
        manager = demo_parking_basic()
        demo_strategy_pattern(manager)
        demo_observer_pattern()
        demo_reporting()
        
        # Final message
        print_header("DEMO COMPLETE!")
        print("\n✓ All design patterns demonstrated successfully!")
        print("\nNext steps:")
        print("  1. Modify the code and experiment with different scenarios")
        print("  2. Add new vehicle types in Vehicle_Refactored.py")
        print("  3. Create new pricing strategies in ParkingManager_Refactored.py")
        print("  4. Build a web interface using Flask or FastAPI")
        print("\nHappy parking! 🚗\n")
        
    except Exception as e:
        print(f"\n❌ Error during demo: {e}")
        print("Make sure both Vehicle_Refactored.py and ParkingManager_Refactored.py are in the same directory.")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
