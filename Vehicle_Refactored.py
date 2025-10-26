"""
Vehicle.py - Refactored Vehicle Management System

This module implements a unified vehicle hierarchy using proper OO principles.
It eliminates the duplicate ElectricVehicle hierarchy by using the Decorator pattern
to add charging capabilities to any vehicle type.

Design Improvements:
1. Single unified Vehicle hierarchy (eliminates code duplication)
2. Abstract base class for type safety
3. Immutable value object pattern for vehicle specifications
4. Decorator pattern for charging capability
5. Proper encapsulation and separation of concerns
"""

from abc import ABC, abstractmethod
from enum import Enum
from dataclasses import dataclass
from typing import Optional


class VehicleType(Enum):
    """
    Enum for vehicle types - provides type safety and prevents string-based
    type identification throughout the codebase.
    
    Benefits:
    - Eliminates magic strings
    - IDE autocomplete support
    - Exhaustiveness checking in switch-like statements
    """
    CAR = "Car"
    TRUCK = "Truck"
    MOTORCYCLE = "Motorcycle"
    BUS = "Bus"


@dataclass(frozen=True)
class VehicleSpecification:
    """
    Value Object representing immutable vehicle specifications.
    
    Benefits:
    - Immutability prevents accidental modifications
    - Value-based equality comparison
    - Easier to use in sets/dicts
    - Clear semantic intent
    
    This follows the Value Object pattern from Domain-Driven Design,
    distinguishing between vehicles with identical specs and unique vehicles.
    """
    registration_number: str
    make: str
    model: str
    color: str

    def __post_init__(self):
        """Validate specifications upon creation."""
        if not self.registration_number or not self.registration_number.strip():
            raise ValueError("Registration number cannot be empty")
        if not self.make or not self.make.strip():
            raise ValueError("Make cannot be empty")
        if not self.model or not self.model.strip():
            raise ValueError("Model cannot be empty")
        if not self.color or not self.color.strip():
            raise ValueError("Color cannot be empty")


class Vehicle(ABC):
    """
    Abstract base class for all vehicles.
    
    Implements the Template Method pattern where concrete vehicle types
    define their specific behavior through getType().
    
    Design improvements over original:
    - Abstract base ensures all vehicles implement required methods
    - Encapsulated specification data in immutable Value Object
    - Private attributes with public interface (proper encapsulation)
    - Separation of vehicle identity from parking context
    """

    def __init__(self, specification: VehicleSpecification):
        """
        Initialize a vehicle with its specifications.
        
        Args:
            specification: VehicleSpecification value object containing
                          registration_number, make, model, color
        """
        self._specification = specification

    @property
    def registration_number(self) -> str:
        """Get the vehicle's registration number."""
        return self._specification.registration_number

    @property
    def make(self) -> str:
        """Get the vehicle manufacturer."""
        return self._specification.make

    @property
    def model(self) -> str:
        """Get the vehicle model."""
        return self._specification.model

    @property
    def color(self) -> str:
        """Get the vehicle color."""
        return self._specification.color

    @property
    def specification(self) -> VehicleSpecification:
        """Get the complete vehicle specification (immutable)."""
        return self._specification

    @abstractmethod
    def get_type(self) -> VehicleType:
        """
        Return the vehicle type. Must be implemented by subclasses.
        
        Returns:
            VehicleType enum value identifying the vehicle category
        """
        pass

    @abstractmethod
    def get_parking_space_size(self) -> str:
        """
        Return the required parking space size for this vehicle.
        
        This allows different vehicle types to specify their space requirements,
        supporting the Strategy pattern for space allocation.
        
        Returns:
            str describing the space requirement (e.g., "COMPACT", "STANDARD", "LARGE")
        """
        pass

    def __str__(self) -> str:
        """String representation for logging and debugging."""
        return (f"{self.get_type().value} ({self.make} {self.model}) "
                f"- Registration: {self.registration_number}, Color: {self.color}")

    def __eq__(self, other) -> bool:
        """Vehicles are equal if their registration numbers match."""
        if not isinstance(other, Vehicle):
            return False
        return self.registration_number == other.registration_number

    def __hash__(self) -> int:
        """Hash based on registration number for use in sets/dicts."""
        return hash(self.registration_number)


class Car(Vehicle):
    """
    Concrete implementation for standard automobiles.
    
    A Car requires standard parking spaces and follows typical
    parking lot pricing rules.
    """

    def get_type(self) -> VehicleType:
        """Car vehicles have type CAR."""
        return VehicleType.CAR

    def get_parking_space_size(self) -> str:
        """Cars require standard parking spaces."""
        return "STANDARD"


class Truck(Vehicle):
    """
    Concrete implementation for trucks/large vehicles.
    
    Trucks require larger parking spaces due to their size.
    """

    def get_type(self) -> VehicleType:
        """Truck vehicles have type TRUCK."""
        return VehicleType.TRUCK

    def get_parking_space_size(self) -> str:
        """Trucks require large parking spaces."""
        return "LARGE"


class Motorcycle(Vehicle):
    """
    Concrete implementation for motorcycles/scooters.
    
    Motorcycles require compact parking spaces due to their small size.
    """

    def get_type(self) -> VehicleType:
        """Motorcycle vehicles have type MOTORCYCLE."""
        return VehicleType.MOTORCYCLE

    def get_parking_space_size(self) -> str:
        """Motorcycles require compact parking spaces."""
        return "COMPACT"


class Bus(Vehicle):
    """
    Concrete implementation for buses/large public transport vehicles.
    
    Buses require the largest parking spaces and may have special
    parking area requirements.
    """

    def get_type(self) -> VehicleType:
        """Bus vehicles have type BUS."""
        return VehicleType.BUS

    def get_parking_space_size(self) -> str:
        """Buses require large parking spaces."""
        return "LARGE"


# ============================================================================
# DECORATOR PATTERN: ChargingCapability
# ============================================================================

class ChargingCapability:
    """
    Decorator that adds charging capability to any vehicle.
    
    **Why Decorator Pattern Instead of ElectricVehicle Hierarchy?**
    
    Problems with original approach:
    - Duplicate class hierarchies (Vehicle + ElectricVehicle)
    - Creates explosion of combinations: ElectricCar, ElectricTruck, etc.
    - Difficult to add other capabilities (e.g., AutonomousDriving)
    - Violates Single Responsibility Principle
    - Code duplication
    
    Benefits of Decorator Pattern:
    - Compose behavior at runtime: any vehicle can become electric
    - No duplicate hierarchies
    - Scalable: adding more capabilities (autonomous, GPS, etc.) is clean
    - Follows Open-Closed Principle: open for extension, closed for modification
    - Single Responsibility: vehicle definition vs. charging logic separated
    
    Example usage:
        spec = VehicleSpecification("ABC123", "Tesla", "Model 3", "White")
        car = Car(spec)
        electric_car = ChargingCapability(car, max_charge=100)
        print(electric_car.get_type())  # VehicleType.CAR
        electric_car.charge(50)
    """

    def __init__(self, vehicle: Vehicle, max_charge_kwh: float = 100.0):
        """
        Initialize a vehicle with charging capability.
        
        Args:
            vehicle: The vehicle to decorate with charging capability
            max_charge_kwh: Maximum battery capacity in kWh (default: 100 kWh)
        
        Raises:
            ValueError: If max_charge_kwh is not positive
        """
        if max_charge_kwh <= 0:
            raise ValueError("Maximum charge must be positive")
        
        self._vehicle = vehicle
        self._max_charge_kwh = max_charge_kwh
        self._current_charge_kwh = 0.0

    @property
    def max_charge(self) -> float:
        """Get maximum battery capacity in kWh."""
        return self._max_charge_kwh

    @property
    def current_charge(self) -> float:
        """Get current battery charge in kWh."""
        return self._current_charge_kwh

    @property
    def charge_percentage(self) -> float:
        """Get current charge as percentage (0-100)."""
        return (self._current_charge_kwh / self._max_charge_kwh) * 100

    def charge(self, amount_kwh: float) -> float:
        """
        Charge the vehicle battery.
        
        Args:
            amount_kwh: Amount of energy to add in kWh
        
        Returns:
            Actual amount charged (may be less if battery fills)
        
        Raises:
            ValueError: If amount_kwh is not positive
        """
        if amount_kwh < 0:
            raise ValueError("Charge amount cannot be negative")
        
        remaining_capacity = self._max_charge_kwh - self._current_charge_kwh
        actual_charge = min(amount_kwh, remaining_capacity)
        self._current_charge_kwh += actual_charge
        return actual_charge

    def discharge(self, amount_kwh: float) -> float:
        """
        Discharge the vehicle battery (simulate usage).
        
        Args:
            amount_kwh: Amount of energy to consume in kWh
        
        Returns:
            Actual amount discharged
        
        Raises:
            ValueError: If amount_kwh is not positive
        """
        if amount_kwh < 0:
            raise ValueError("Discharge amount cannot be negative")
        
        actual_discharge = min(amount_kwh, self._current_charge_kwh)
        self._current_charge_kwh -= actual_discharge
        return actual_discharge

    def is_fully_charged(self) -> bool:
        """Check if battery is at maximum capacity."""
        return self._current_charge_kwh >= self._max_charge_kwh

    def is_low_battery(self, threshold_percent: float = 20.0) -> bool:
        """
        Check if battery is below threshold percentage.
        
        Args:
            threshold_percent: Battery percentage threshold (default: 20%)
        
        Returns:
            True if current charge is below threshold
        """
        return self.charge_percentage < threshold_percent

    # Delegation: forward vehicle property access to decorated vehicle
    @property
    def registration_number(self) -> str:
        """Get the vehicle's registration number."""
        return self._vehicle.registration_number

    @property
    def make(self) -> str:
        """Get the vehicle manufacturer."""
        return self._vehicle.make

    @property
    def model(self) -> str:
        """Get the vehicle model."""
        return self._vehicle.model

    @property
    def color(self) -> str:
        """Get the vehicle color."""
        return self._vehicle.color

    def get_type(self) -> VehicleType:
        """Get the underlying vehicle type."""
        return self._vehicle.get_type()

    def get_parking_space_size(self) -> str:
        """Get the underlying vehicle's space requirement."""
        return self._vehicle.get_parking_space_size()

    def __str__(self) -> str:
        """String representation including charging capability."""
        base_str = str(self._vehicle)
        return (f"🔌 {base_str} [Battery: {self.charge_percentage:.1f}% "
                f"({self._current_charge_kwh:.1f}/{self._max_charge_kwh:.1f} kWh)]")


# ============================================================================
# FACTORY PATTERN: VehicleFactory
# ============================================================================

class VehicleFactory:
    """
    Factory for creating vehicle instances safely and consistently.
    
    **Benefits:**
    - Centralizes vehicle creation logic
    - Enables validation of creation parameters
    - Reduces coupling between client code and vehicle classes
    - Single point of change for vehicle instantiation
    - Supports future extensions (logging, tracking, etc.)
    
    This implements the Factory Method pattern, providing a single
    interface for creating different vehicle types.
    """

    _VEHICLE_TYPES = {
        VehicleType.CAR: Car,
        VehicleType.TRUCK: Truck,
        VehicleType.MOTORCYCLE: Motorcycle,
        VehicleType.BUS: Bus,
    }

    @staticmethod
    def create_vehicle(vehicle_type: VehicleType,
                      registration_number: str,
                      make: str,
                      model: str,
                      color: str) -> Vehicle:
        """
        Create a vehicle instance with validation.
        
        Args:
            vehicle_type: The type of vehicle to create (VehicleType enum)
            registration_number: Vehicle registration/license plate
            make: Vehicle manufacturer
            model: Vehicle model name
            color: Vehicle color
        
        Returns:
            Vehicle instance of the specified type
        
        Raises:
            ValueError: If parameters are invalid or vehicle type unknown
        """
        if vehicle_type not in VehicleFactory._VEHICLE_TYPES:
            raise ValueError(f"Unknown vehicle type: {vehicle_type}")
        
        # Create specification (validation happens in VehicleSpecification)
        spec = VehicleSpecification(registration_number, make, model, color)
        
        # Create and return vehicle instance
        vehicle_class = VehicleFactory._VEHICLE_TYPES[vehicle_type]
        return vehicle_class(spec)

    @staticmethod
    def create_electric_vehicle(vehicle_type: VehicleType,
                               registration_number: str,
                               make: str,
                               model: str,
                               color: str,
                               max_charge_kwh: float = 100.0) -> ChargingCapability:
        """
        Create an electric vehicle (vehicle with charging capability).
        
        This method demonstrates the power of composition: we create a regular
        vehicle and decorate it with charging capability.
        
        Args:
            vehicle_type: The type of vehicle to create
            registration_number: Vehicle registration/license plate
            make: Vehicle manufacturer
            model: Vehicle model name
            color: Vehicle color
            max_charge_kwh: Maximum battery capacity (default: 100 kWh)
        
        Returns:
            ChargingCapability-decorated vehicle instance
        
        Raises:
            ValueError: If parameters are invalid
        """
        base_vehicle = VehicleFactory.create_vehicle(
            vehicle_type, registration_number, make, model, color
        )
        return ChargingCapability(base_vehicle, max_charge_kwh)


# ============================================================================
# Example Usage
# ============================================================================

if __name__ == "__main__":
    # Create a regular car
    spec_car = VehicleSpecification("ABC123", "Honda", "Civic", "Blue")
    car = Car(spec_car)
    print(f"Regular Car: {car}")
    print(f"Type: {car.get_type().value}")
    print(f"Space Required: {car.get_parking_space_size()}\n")

    # Create an electric car using factory
    electric_car = VehicleFactory.create_electric_vehicle(
        VehicleType.CAR, "XYZ789", "Tesla", "Model 3", "White", max_charge_kwh=75
    )
    print(f"Electric Car: {electric_car}")
    electric_car.charge(50)
    print(f"After charging 50 kWh: {electric_car}\n")

    # Create a motorcycle
    motorcycle = VehicleFactory.create_vehicle(
        VehicleType.MOTORCYCLE, "MOT456", "Harley", "Street 750", "Black"
    )
    print(f"Motorcycle: {motorcycle}")
    print(f"Space Required: {motorcycle.get_parking_space_size()}\n")

    # Create an electric motorcycle
    electric_motorcycle = VehicleFactory.create_electric_vehicle(
        VehicleType.MOTORCYCLE, "EMT999", "Zero", "SR", "Silver", max_charge_kwh=12
    )
    print(f"Electric Motorcycle: {electric_motorcycle}")
    electric_motorcycle.charge(10)
    print(f"Charge Status: {electric_motorcycle.charge_percentage:.1f}%")
