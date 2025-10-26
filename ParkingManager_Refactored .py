"""
ParkingManager.py - Refactored Parking Management System

This module implements a complete parking management system using proven
design patterns and SOLID principles.

Design Patterns Applied:
1. Strategy Pattern: Pluggable pricing strategies based on vehicle type
2. Observer Pattern: Notify subscribers when spaces become available
3. Factory Pattern: Already implemented in Vehicle module

Improvements:
- Separation of concerns (parking vs. pricing logic)
- Extensible pricing strategies
- Type-safe vehicle handling
- Proper error handling and validation
- Event notification system
"""

from abc import ABC, abstractmethod
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable
import sys
import os

# Try to import from Vehicle_Refactored
try:
    from Vehicle_Refactored import Vehicle, VehicleType, ChargingCapability, VehicleFactory, VehicleSpecification, Car, Truck, Motorcycle, Bus
except ImportError:
    # Fallback if imports fail
    pass


class ParkingSpaceSize(Enum):
    """
    Enumeration of parking space sizes.
    
    Provides clear categorization of parking spaces to match vehicle requirements.
    """
    COMPACT = "COMPACT"
    STANDARD = "STANDARD"
    LARGE = "LARGE"


class ParkingSpaceStatus(Enum):
    """
    Enumeration of parking space states.
    
    Enables clear state management and event-driven notifications.
    """
    AVAILABLE = "AVAILABLE"
    OCCUPIED = "OCCUPIED"
    RESERVED = "RESERVED"
    MAINTENANCE = "MAINTENANCE"


@dataclass
class ParkingSpace:
    """
    Value Object representing a specific parking space.
    
    Benefits:
    - Immutable identity for the space
    - Clear encapsulation of space properties
    - Easy to track and manage
    """
    space_id: str
    size: ParkingSpaceSize
    status: ParkingSpaceStatus = field(default=ParkingSpaceStatus.AVAILABLE)
    floor: int = 1
    location: str = ""  # e.g., "A3", "B2"

    def __post_init__(self):
        """Validate space properties."""
        if not self.space_id or not self.space_id.strip():
            raise ValueError("Space ID cannot be empty")
        if self.floor < 1:
            raise ValueError("Floor number must be positive")

    def is_available(self) -> bool:
        """Check if space is available for parking."""
        return self.status == ParkingSpaceStatus.AVAILABLE

    def __str__(self) -> str:
        return f"Space {self.space_id} (Floor {self.floor}, {self.size.value})"


@dataclass
class ParkingTicket:
    """
    Value Object representing a parking ticket/entry.
    
    Tracks entry and exit times, vehicle information, and charges.
    """
    ticket_id: str
    vehicle: Vehicle
    space: ParkingSpace
    entry_time: datetime
    exit_time: Optional[datetime] = None
    charge_amount: float = 0.0

    def is_active(self) -> bool:
        """Check if vehicle is currently parked."""
        return self.exit_time is None

    def get_duration_hours(self) -> float:
        """Get parking duration in hours."""
        end_time = self.exit_time or datetime.now()
        duration = end_time - self.entry_time
        return duration.total_seconds() / 3600

    def __str__(self) -> str:
        status = "ACTIVE" if self.is_active() else "COMPLETED"
        return (f"Ticket {self.ticket_id}: {self.vehicle.registration_number} "
                f"in {self.space} [{status}]")


# ============================================================================
# STRATEGY PATTERN: Pricing Strategies
# ============================================================================

class PricingStrategy(ABC):
    """
    Abstract base class for parking fee calculation strategies.
    
    **Why Strategy Pattern?**
    - Different vehicle types and facilities may have different pricing
    - Strategies can be changed at runtime
    - New pricing models don't require modifying existing code
    - Testing is easier with interchangeable strategies
    
    **Open-Closed Principle:** Open for extension (new pricing strategies),
    closed for modification (ParkingManager doesn't change).
    """

    @abstractmethod
    def calculate_fee(self, ticket: ParkingTicket) -> float:
        """
        Calculate parking fee for a ticket.
        
        Args:
            ticket: The parking ticket with vehicle and duration info
        
        Returns:
            Calculated fee in currency units
        """
        pass

    @abstractmethod
    def get_strategy_name(self) -> str:
        """Get a descriptive name for this strategy."""
        pass


class BasicPricingStrategy(PricingStrategy):
    """
    Simple hourly rate strategy with vehicle-type variations.
    
    Example implementation of a pricing strategy:
    - Motorcycles: $5/hour
    - Cars: $10/hour
    - Trucks/Buses: $15/hour
    """

    def __init__(self):
        """Initialize with base rates for each vehicle type."""
        self._base_rates = {
            VehicleType.MOTORCYCLE: 5.0,
            VehicleType.CAR: 10.0,
            VehicleType.TRUCK: 15.0,
            VehicleType.BUS: 15.0,
        }
        self._minimum_charge = 2.0

    def calculate_fee(self, ticket: ParkingTicket) -> float:
        """
        Calculate fee based on vehicle type and duration.
        
        Args:
            ticket: Parking ticket
        
        Returns:
            Calculated fee
        """
        duration_hours = max(ticket.get_duration_hours(), 0.5)  # Minimum 30 minutes
        vehicle_type = ticket.vehicle.get_type()
        hourly_rate = self._base_rates.get(vehicle_type, 10.0)
        fee = duration_hours * hourly_rate
        return max(fee, self._minimum_charge)

    def get_strategy_name(self) -> str:
        return "Basic Hourly Rate"


class PeakHourPricingStrategy(PricingStrategy):
    """
    Dynamic pricing strategy with peak/off-peak rates.
    
    Peak hours (9-11 AM, 5-7 PM): 1.5x multiplier
    Off-peak: 1x multiplier
    Night (10 PM - 6 AM): 0.5x multiplier
    """

    def __init__(self):
        """Initialize with base rates."""
        self._base_rates = {
            VehicleType.MOTORCYCLE: 5.0,
            VehicleType.CAR: 10.0,
            VehicleType.TRUCK: 15.0,
            VehicleType.BUS: 15.0,
        }

    def _get_peak_multiplier(self, dt: datetime) -> float:
        """Determine pricing multiplier based on time of day."""
        hour = dt.hour
        
        # Peak hours: 9-11 AM and 5-7 PM
        if (9 <= hour < 12) or (17 <= hour < 19):
            return 1.5
        # Night: 10 PM - 6 AM
        elif hour >= 22 or hour < 6:
            return 0.5
        # Off-peak
        else:
            return 1.0

    def calculate_fee(self, ticket: ParkingTicket) -> float:
        """Calculate fee with peak-hour multiplier."""
        duration_hours = max(ticket.get_duration_hours(), 0.5)
        vehicle_type = ticket.vehicle.get_type()
        hourly_rate = self._base_rates.get(vehicle_type, 10.0)
        
        # Use peak multiplier from entry time
        multiplier = self._get_peak_multiplier(ticket.entry_time)
        
        fee = duration_hours * hourly_rate * multiplier
        return max(fee, 2.0)

    def get_strategy_name(self) -> str:
        return "Peak Hour Dynamic Pricing"


class SubscriptionPricingStrategy(PricingStrategy):
    """
    Flat-rate subscription pricing with unlimited parking.
    
    Example:
    - Motorcycles: $50/month
    - Cars: $100/month
    - Trucks: $150/month
    """

    def __init__(self):
        """Initialize with subscription rates."""
        self._subscription_rates = {
            VehicleType.MOTORCYCLE: 50.0,
            VehicleType.CAR: 100.0,
            VehicleType.TRUCK: 150.0,
            VehicleType.BUS: 150.0,
        }

    def calculate_fee(self, ticket: ParkingTicket) -> float:
        """
        For subscription pricing, calculate daily charge.
        
        Args:
            ticket: Parking ticket
        
        Returns:
            Daily charge (subscription_rate / 30)
        """
        vehicle_type = ticket.vehicle.get_type()
        monthly_rate = self._subscription_rates.get(vehicle_type, 100.0)
        daily_rate = monthly_rate / 30
        duration_days = max(ticket.get_duration_hours() / 24, 1)
        return duration_days * daily_rate

    def get_strategy_name(self) -> str:
        return "Subscription Pricing"


class EvChargingPricingStrategy(PricingStrategy):
    """
    Special pricing for electric vehicles using charging stations.
    
    Combines parking fee with charging cost:
    - Base parking: 50% of regular vehicle type rate
    - Charging: $0.50 per kWh
    """

    def __init__(self):
        """Initialize with base rates."""
        self._base_rates = {
            VehicleType.MOTORCYCLE: 2.5,
            VehicleType.CAR: 5.0,
            VehicleType.TRUCK: 7.5,
            VehicleType.BUS: 7.5,
        }
        self._charging_rate_per_kwh = 0.50

    def calculate_fee(self, ticket: ParkingTicket) -> float:
        """
        Calculate fee including charging costs if applicable.
        
        Args:
            ticket: Parking ticket (vehicle may have ChargingCapability)
        
        Returns:
            Total fee (parking + charging)
        """
        duration_hours = max(ticket.get_duration_hours(), 0.5)
        vehicle_type = ticket.vehicle.get_type()
        
        # Base parking fee (50% of regular)
        hourly_rate = self._base_rates.get(vehicle_type, 5.0)
        parking_fee = duration_hours * hourly_rate
        
        # Charging fee (if vehicle has charging capability)
        charging_fee = 0.0
        if isinstance(ticket.vehicle, ChargingCapability):
            # Estimate: assume some energy was consumed
            estimated_consumption = duration_hours * 5.0  # 5 kWh per hour average
            charging_fee = estimated_consumption * self._charging_rate_per_kwh
        
        total_fee = parking_fee + charging_fee
        return max(total_fee, 2.0)

    def get_strategy_name(self) -> str:
        return "EV Charging-Aware Pricing"


# ============================================================================
# OBSERVER PATTERN: Event Notifications
# ============================================================================

class ParkingEventObserver(ABC):
    """
    Observer interface for parking system events.
    
    **Why Observer Pattern?**
    - Decouples event producers from event consumers
    - Multiple subscribers can react to same event
    - Foundation for real-time monitoring and notifications
    - Easy to add new subscribers without modifying ParkingManager
    """

    @abstractmethod
    def on_vehicle_entry(self, ticket: ParkingTicket) -> None:
        """Called when vehicle enters parking."""
        pass

    @abstractmethod
    def on_vehicle_exit(self, ticket: ParkingTicket) -> None:
        """Called when vehicle exits parking."""
        pass

    @abstractmethod
    def on_space_available(self, space: ParkingSpace) -> None:
        """Called when a space becomes available."""
        pass


class LoggingObserver(ParkingEventObserver):
    """Observer that logs parking events."""

    def on_vehicle_entry(self, ticket: ParkingTicket) -> None:
        """Log vehicle entry."""
        print(f"[LOG] Vehicle entry: {ticket}")

    def on_vehicle_exit(self, ticket: ParkingTicket) -> None:
        """Log vehicle exit and charge."""
        print(f"[LOG] Vehicle exit: {ticket.vehicle.registration_number}, "
              f"Charge: ${ticket.charge_amount:.2f}")

    def on_space_available(self, space: ParkingSpace) -> None:
        """Log space availability."""
        print(f"[LOG] Space available: {space}")


class ChargingStationObserver(ParkingEventObserver):
    """Observer that manages EV charging stations."""

    def __init__(self):
        """Initialize charging station observer."""
        self._charging_sessions: Dict[str, ChargingCapability] = {}

    def on_vehicle_entry(self, ticket: ParkingTicket) -> None:
        """Allocate charging spot if EV."""
        if isinstance(ticket.vehicle, ChargingCapability):
            self._charging_sessions[ticket.vehicle.registration_number] = ticket.vehicle
            print(f"[CHARGING] EV charging session started for {ticket.vehicle.registration_number}")

    def on_vehicle_exit(self, ticket: ParkingTicket) -> None:
        """End charging session."""
        if ticket.vehicle.registration_number in self._charging_sessions:
            ev = self._charging_sessions.pop(ticket.vehicle.registration_number)
            print(f"[CHARGING] EV charging session ended. "
                  f"Final charge: {ev.charge_percentage:.1f}%")

    def on_space_available(self, space: ParkingSpace) -> None:
        """Charging stations don't respond to general space availability."""
        pass


class AvailabilityNotificationObserver(ParkingEventObserver):
    """Observer that notifies users of available spaces."""

    def __init__(self):
        """Initialize notification observer."""
        self._waitlist: List[Callable] = []

    def subscribe_to_availability(self, callback: Callable[[ParkingSpace], None]) -> None:
        """Subscribe to availability notifications."""
        self._waitlist.append(callback)

    def on_vehicle_entry(self, ticket: ParkingTicket) -> None:
        """Entry events don't affect availability."""
        pass

    def on_vehicle_exit(self, ticket: ParkingTicket) -> None:
        """Exit events don't directly notify (space_available event does)."""
        pass

    def on_space_available(self, space: ParkingSpace) -> None:
        """Notify all subscribers when space becomes available."""
        print(f"[NOTIFICATION] Space available: {space}")
        for callback in self._waitlist:
            try:
                callback(space)
            except Exception as e:
                print(f"[ERROR] Notification callback failed: {e}")


# ============================================================================
# MAIN PARKING MANAGER
# ============================================================================

class ParkingManager:
    """
    Main parking lot management system.
    
    **Responsibilities:**
    - Manage parking spaces and their allocation
    - Track parked vehicles
    - Calculate parking fees
    - Notify observers of events
    
    **Design Improvements:**
    - Pluggable pricing strategy (Strategy pattern)
    - Event notification system (Observer pattern)
    - Proper encapsulation and type safety
    - Comprehensive error handling
    
    This class demonstrates the Single Responsibility Principle by delegating
    pricing calculations to strategies and not hardcoding fee logic.
    """

    def __init__(self, pricing_strategy: PricingStrategy):
        """
        Initialize the parking manager.
        
        Args:
            pricing_strategy: The pricing strategy to use for fee calculation
        """
        self._spaces: Dict[str, ParkingSpace] = {}
        self._active_tickets: Dict[str, ParkingTicket] = {}  # registration_number -> ticket
        self._completed_tickets: List[ParkingTicket] = []
        self._observers: List[ParkingEventObserver] = []
        self._pricing_strategy = pricing_strategy
        self._next_ticket_id_counter = 1000

    # ========== Space Management ==========

    def add_parking_space(self, space: ParkingSpace) -> None:
        """
        Add a new parking space to the lot.
        
        Args:
            space: ParkingSpace to add
        
        Raises:
            ValueError: If space ID already exists
        """
        if space.space_id in self._spaces:
            raise ValueError(f"Space {space.space_id} already exists")
        self._spaces[space.space_id] = space

    def add_multiple_spaces(self, spaces: List[ParkingSpace]) -> None:
        """
        Add multiple parking spaces at once.
        
        Args:
            spaces: List of ParkingSpace objects
        """
        for space in spaces:
            self.add_parking_space(space)

    def get_available_spaces(self, size: Optional[ParkingSpaceSize] = None) -> List[ParkingSpace]:
        """
        Get available parking spaces.
        
        Args:
            size: Optional filter by space size
        
        Returns:
            List of available spaces
        """
        available = [space for space in self._spaces.values()
                    if space.is_available()]
        
        if size:
            available = [space for space in available if space.size == size]
        
        return available

    def get_available_space_count(self, size: Optional[ParkingSpaceSize] = None) -> int:
        """Get count of available spaces."""
        return len(self.get_available_spaces(size))

    def get_occupancy_rate(self) -> float:
        """
        Get parking lot occupancy percentage.
        
        Returns:
            Occupancy rate (0-100)
        """
        if not self._spaces:
            return 0.0
        occupied = sum(1 for space in self._spaces.values()
                      if space.status == ParkingSpaceStatus.OCCUPIED)
        return (occupied / len(self._spaces)) * 100

    # ========== Vehicle Entry/Exit ==========

    def park_vehicle(self, vehicle: Vehicle) -> ParkingTicket:
        """
        Park a vehicle in an appropriate space.
        
        Args:
            vehicle: Vehicle to park
        
        Returns:
            ParkingTicket for the vehicle
        
        Raises:
            ValueError: If no appropriate space available or vehicle already parked
        """
        # Check if vehicle already parked
        if vehicle.registration_number in self._active_tickets:
            raise ValueError(f"Vehicle {vehicle.registration_number} is already parked")

        # Find appropriate space
        required_size = vehicle.get_parking_space_size()
        size_enum = ParkingSpaceSize[required_size]
        available_spaces = self.get_available_spaces(size_enum)
        
        if not available_spaces:
            raise ValueError(f"No available {required_size} space for {vehicle}")

        # Allocate space
        space = available_spaces[0]
        space.status = ParkingSpaceStatus.OCCUPIED

        # Create ticket
        ticket = ParkingTicket(
            ticket_id=f"TKT{self._next_ticket_id_counter}",
            vehicle=vehicle,
            space=space,
            entry_time=datetime.now()
        )
        self._next_ticket_id_counter += 1

        # Store ticket
        self._active_tickets[vehicle.registration_number] = ticket

        # Notify observers
        self._notify_entry(ticket)

        return ticket

    def retrieve_vehicle(self, registration_number: str) -> ParkingTicket:
        """
        Remove a vehicle from parking and calculate fee.
        
        Args:
            registration_number: Vehicle registration number
        
        Returns:
            Completed ParkingTicket with charge
        
        Raises:
            ValueError: If vehicle not found in parking
        """
        if registration_number not in self._active_tickets:
            raise ValueError(f"Vehicle {registration_number} not found in parking")

        ticket = self._active_tickets.pop(registration_number)
        ticket.exit_time = datetime.now()

        # Calculate fee
        ticket.charge_amount = self._pricing_strategy.calculate_fee(ticket)

        # Free up space
        ticket.space.status = ParkingSpaceStatus.AVAILABLE

        # Store completed ticket
        self._completed_tickets.append(ticket)

        # Notify observers
        self._notify_exit(ticket)
        self._notify_space_available(ticket.space)

        return ticket

    # ========== Pricing & Revenue ==========

    def set_pricing_strategy(self, strategy: PricingStrategy) -> None:
        """
        Change the pricing strategy at runtime.
        
        Args:
            strategy: New pricing strategy
        """
        print(f"[INFO] Changing pricing strategy to: {strategy.get_strategy_name()}")
        self._pricing_strategy = strategy

    def get_current_strategy_name(self) -> str:
        """Get name of current pricing strategy."""
        return self._pricing_strategy.get_strategy_name()

    def get_total_revenue(self) -> float:
        """Calculate total revenue from all completed tickets."""
        return sum(ticket.charge_amount for ticket in self._completed_tickets)

    def get_revenue_by_vehicle_type(self) -> Dict[VehicleType, float]:
        """Get revenue breakdown by vehicle type."""
        revenue = {}
        for ticket in self._completed_tickets:
            vtype = ticket.vehicle.get_type()
            revenue[vtype] = revenue.get(vtype, 0.0) + ticket.charge_amount
        return revenue

    # ========== Observer Management ==========

    def attach_observer(self, observer: ParkingEventObserver) -> None:
        """Attach an observer to receive events."""
        self._observers.append(observer)

    def detach_observer(self, observer: ParkingEventObserver) -> None:
        """Detach an observer."""
        if observer in self._observers:
            self._observers.remove(observer)

    def _notify_entry(self, ticket: ParkingTicket) -> None:
        """Notify all observers of vehicle entry."""
        for observer in self._observers:
            observer.on_vehicle_entry(ticket)

    def _notify_exit(self, ticket: ParkingTicket) -> None:
        """Notify all observers of vehicle exit."""
        for observer in self._observers:
            observer.on_vehicle_exit(ticket)

    def _notify_space_available(self, space: ParkingSpace) -> None:
        """Notify all observers of space availability."""
        for observer in self._observers:
            observer.on_space_available(space)

    # ========== Reporting ==========

    def get_parked_vehicles(self) -> List[Vehicle]:
        """Get list of currently parked vehicles."""
        return [ticket.vehicle for ticket in self._active_tickets.values()]

    def get_parking_summary(self) -> Dict:
        """Get comprehensive parking lot summary."""
        total_spaces = len(self._spaces)
        occupied = sum(1 for space in self._spaces.values()
                      if space.status == ParkingSpaceStatus.OCCUPIED)
        available = total_spaces - occupied

        return {
            "total_spaces": total_spaces,
            "occupied_spaces": occupied,
            "available_spaces": available,
            "occupancy_rate": self.get_occupancy_rate(),
            "pricing_strategy": self.get_current_strategy_name(),
            "total_revenue": self.get_total_revenue(),
            "active_vehicles": len(self._active_tickets),
            "total_transactions": len(self._completed_tickets),
        }

    def print_summary(self) -> None:
        """Print parking lot summary to console."""
        summary = self.get_parking_summary()
        print("\n" + "="*60)
        print("PARKING LOT SUMMARY")
        print("="*60)
        for key, value in summary.items():
            if isinstance(value, float):
                print(f"{key:<25}: {value:.2f}")
            else:
                print(f"{key:<25}: {value}")
        print("="*60 + "\n")


# ============================================================================
# Example Usage & Testing
# ============================================================================

if __name__ == "__main__":
    print("="*70)
    print("PARKING MANAGEMENT SYSTEM - DEMONSTRATION")
    print("="*70)

    # Initialize parking manager with basic pricing
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
        ParkingSpace("L1", ParkingSpaceSize.LARGE, floor=2, location="C1"),
    ]
    manager.add_multiple_spaces(spaces)

    print(f"\nInitial Available Spaces: {manager.get_available_space_count()}")

    # Park some vehicles
    print("\n--- Parking Vehicles ---")
    
    car_spec = VehicleSpecification("ABC123", "Honda", "Civic", "Blue")
    car = Car(car_spec)
    ticket1 = manager.park_vehicle(car)
    print(f"Parked: {car}, Ticket: {ticket1.ticket_id}")

    motorcycle_spec = VehicleSpecification("MOT456", "Harley", "Street", "Black")
    motorcycle = manager.park_vehicle(VehicleFactory.create_vehicle(
        VehicleType.MOTORCYCLE, "MOT456", "Harley", "Street", "Black"
    ))
    print(f"Parked motorcycle")

    # Create and park an electric vehicle
    print("\n--- EV Charging ---")
    ev_car = VehicleFactory.create_electric_vehicle(
        VehicleType.CAR, "TESLA01", "Tesla", "Model 3", "White", max_charge_kwh=75
    )
    ev_car.charge(50)  # Charge to 50 kWh
    print(f"Created EV: {ev_car}")
    ticket_ev = manager.park_vehicle(ev_car)

    # Display occupancy
    print(f"\nCurrent Occupancy: {manager.get_occupancy_rate():.1f}%")
    print(f"Available Spaces: {manager.get_available_space_count()}")

    # Simulate time passing
    print("\n--- Simulating Parking Time ---")
    ticket1.entry_time = datetime.now() - timedelta(hours=2)

    # Retrieve vehicles
    print("\n--- Retrieving Vehicles ---")
    exit_ticket1 = manager.retrieve_vehicle("ABC123")
    print(f"Retrieved vehicle, Charge: ${exit_ticket1.charge_amount:.2f}")

    exit_ticket_ev = manager.retrieve_vehicle("TESLA01")
    print(f"Retrieved EV, Charge: ${exit_ticket_ev.charge_amount:.2f}")

    # Display final summary
    manager.print_summary()

    # Display revenue breakdown
    print("Revenue by Vehicle Type:")
    for vtype, amount in manager.get_revenue_by_vehicle_type().items():
        print(f"  {vtype.value}: ${amount:.2f}")

    # Demonstrate strategy switching
    print("\n--- Switching to Peak Hour Pricing ---")
    manager.set_pricing_strategy(PeakHourPricingStrategy())
    print(f"Current Strategy: {manager.get_current_strategy_name()}")
