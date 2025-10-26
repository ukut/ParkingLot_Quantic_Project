# Microservices Architecture for Multi-Facility EV-Enabled Parking System

## Part 1: Domain-Driven Design Analysis

### 1.1 Problem Statement

**Current State**: Single parking lot with basic management
**Future State**: Multi-facility parking network with EV charging

**Business Requirements**:
- Manage multiple parking facilities simultaneously
- Support electric vehicle charging stations
- Real-time space availability across facilities
- Unified reservation system
- Revenue tracking and reporting
- Multi-tenant support (different pricing per facility)
- Scalability for geographic expansion

---

### 1.2 Core Domain Identification

The parking business operates across several distinct domains:

```
┌─────────────────────────────────────────────┐
│     EasyParkPlus Parking Operations          │
│                                               │
│  ┌──────────────┐  ┌──────────────┐         │
│  │  CORE DOMAIN │  │  SUB-DOMAINS │         │
│  └──────────────┘  └──────────────┘         │
│                                               │
│  • Parking Space    • Vehicle Mgmt           │
│    Management       • EV Charging           │
│  • Vehicle Entry    • Billing               │
│    & Exit           • Analytics             │
│  • Reservations     • Facilities            │
│                       Management            │
└─────────────────────────────────────────────┘
```

#### Core Domain: Parking Operations
The primary business value - managing parking spaces and vehicles

#### Sub-Domain 1: Vehicle Management
Managing vehicle information, types, and tracking

#### Sub-Domain 2: Electric Vehicle Charging
New capability - managing EV charging infrastructure and sessions

#### Sub-Domain 3: Reservation System
Allowing customers to book spaces in advance

#### Sub-Domain 4: Facility Management
Managing multiple facilities, capacity, and operations

#### Sub-Domain 5: Billing & Revenue
Tracking charges, payments, and revenue reporting

#### Sub-Domain 6: Monitoring & Analytics
Real-time metrics, occupancy tracking, and business intelligence

---

### 1.3 Bounded Contexts

Bounded contexts define the boundaries where a particular domain model applies.

```
┌─────────────────────────────────────────────────────────────────┐
│                    ORGANIZATIONAL CONTEXT                        │
├──────────────┬──────────────┬──────────────┬────────────────────┤
│ Parking      │ Reservation  │   Charging   │   Billing &        │
│ Context      │ Context      │   Context    │   Revenue Context  │
│              │              │              │                    │
│ • Spaces     │ • Reserv'ns  │ • Stations   │ • Invoices         │
│ • Vehicles   │ • Slots      │ • Sessions   │ • Payments         │
│ • Entry/Exit │ • Booking    │ • Energy     │ • Reports          │
│ • Occupancy  │ • Releases   │ • Hardware   │ • Analytics        │
└──────────────┴──────────────┴──────────────┴────────────────────┘
```

### 1.4 Key Entities and Value Objects

#### Parking Context Entities:
```
Entity: Parking Space
├─ Attributes:
│  ├─ space_id (identity)
│  ├─ facility_id
│  ├─ size (COMPACT, STANDARD, LARGE)
│  ├─ status (AVAILABLE, OCCUPIED, RESERVED, MAINTENANCE)
│  └─ location (aisle, level, position)
├─ Behaviors:
│  ├─ occupy(vehicle)
│  ├─ release()
│  └─ reserve()
└─ Value Objects:
   ├─ SpaceLocation (floor, aisle, number)
   └─ SpaceSize (enum)

Entity: Parking Session
├─ Attributes:
│  ├─ session_id (identity)
│  ├─ vehicle_id
│  ├─ space_id
│  ├─ facility_id
│  ├─ entry_time
│  ├─ exit_time
│  └─ charge_amount
├─ Behaviors:
│  ├─ begin_session()
│  ├─ end_session()
│  └─ calculate_charge()
└─ Value Objects:
   ├─ SessionDuration
   └─ ChargeAmount (currency, value)
```

#### Charging Context Entities:
```
Entity: Charging Station
├─ Attributes:
│  ├─ station_id (identity)
│  ├─ facility_id
│  ├─ type (Level1, Level2, DCFC)
│  ├─ status (AVAILABLE, IN_USE, MAINTENANCE, OFFLINE)
│  └─ connector_type (CCS, Tesla, CHAdeMO)
├─ Behaviors:
│  ├─ start_charging_session()
│  ├─ stop_charging_session()
│  └─ update_hardware_status()
└─ Value Objects:
   ├─ ChargingLevel (enum)
   ├─ Power (kW)
   └─ ConnectorType (enum)

Entity: Charging Session
├─ Attributes:
│  ├─ charging_session_id (identity)
│  ├─ vehicle_id
│  ├─ station_id
│  ├─ start_time
│  ├─ end_time
│  ├─ energy_kwh
│  ├─ cost
│  └─ status (ACTIVE, COMPLETED, INTERRUPTED)
├─ Behaviors:
│  ├─ start_charging()
│  ├─ pause_charging()
│  ├─ resume_charging()
│  ├─ stop_charging()
│  └─ calculate_charge()
└─ Value Objects:
   ├─ EnergyAmount (kWh)
   ├─ Duration
   └─ Cost (currency)
```

#### Reservation Context Entities:
```
Entity: Reservation
├─ Attributes:
│  ├─ reservation_id (identity)
│  ├─ vehicle_id
│  ├─ facility_id
│  ├─ desired_space_size
│  ├─ start_time
│  ├─ end_time
│  ├─ status (PENDING, CONFIRMED, CANCELLED, EXPIRED)
│  └─ customer_id
├─ Behaviors:
│  ├─ confirm()
│  ├─ cancel()
│  └─ expire()
└─ Value Objects:
   ├─ ReservationWindow (start_time, end_time)
   └─ SpacePreference
```

#### Billing Context Entities:
```
Entity: Invoice
├─ Attributes:
│  ├─ invoice_id (identity)
│  ├─ customer_id
│  ├─ facility_id
│  ├─ session_ids (references)
│  ├─ line_items
│  ├─ total_amount
│  ├─ issue_date
│  ├─ due_date
│  └─ status (DRAFT, SENT, PAID, OVERDUE)
├─ Behaviors:
│  ├─ add_charge()
│  ├─ finalize()
│  ├─ send()
│  └─ mark_paid()
└─ Value Objects:
   ├─ LineItem
   └─ Money (amount, currency)

Entity: Payment
├─ Attributes:
│  ├─ payment_id (identity)
│  ├─ invoice_id
│  ├─ amount
│  ├─ payment_method
│  ├─ timestamp
│  └─ reference
├─ Behaviors:
│  ├─ process()
│  ├─ refund()
│  └─ confirm()
└─ Value Objects:
   └─ Money (amount, currency)
```

---

### 1.5 Ubiquitous Language

Common terminology used across the organization:

#### Parking Domain:
- **Facility**: A parking lot location
- **Parking Space**: Individual spot where vehicle can park
- **Space Size**: COMPACT (motorcycles), STANDARD (cars), LARGE (trucks/buses)
- **Session**: Period when vehicle is parked
- **Entry**: Vehicle arriving at facility
- **Exit**: Vehicle leaving facility
- **Occupancy Rate**: Percentage of spaces currently occupied
- **Availability**: Number of free spaces of specific size

#### Charging Domain:
- **Charging Station**: Equipment providing electrical power
- **Charger Level**: Level 1 (120V), Level 2 (240V), DCFC (480V+)
- **Charging Session**: Period when vehicle is charging
- **Energy**: Amount of electrical energy delivered (kWh)
- **State of Charge (SoC)**: Current battery percentage
- **Connector Type**: CCS, Tesla, CHAdeMO, etc.
- **Charging Rate**: Power delivery speed (kW)

#### Reservation Domain:
- **Reservation**: Advance booking of parking space
- **Reservation Window**: Time period for reservation
- **Confirmation**: Agreement to hold space for customer
- **Cancellation**: Release of reserved space

#### Billing Domain:
- **Charge**: Fee for parking or charging
- **Invoice**: Bill sent to customer
- **Line Item**: Individual charge on invoice
- **Payment**: Customer payment for invoice
- **Revenue**: Income from parking and charging

---

### 1.6 Aggregate Design

Aggregates are clusters of objects treated as single unit for data consistency.

#### Parking Aggregate:
```
Aggregate Root: ParkingFacility
├─ Parking Spaces (collection)
├─ Occupancy Rules (value object)
├─ Pricing Strategy (value object)
└─ Facility Configuration (value object)

Invariants to maintain:
- Spaces cannot exceed capacity
- Only one vehicle per space
- Cannot exit vehicle not in facility
- Space status must be valid (AVAILABLE, OCCUPIED, RESERVED, MAINTENANCE)
```

#### Charging Aggregate:
```
Aggregate Root: ChargingStation
├─ Charging Sessions (collection)
├─ Power Configuration (value object)
└─ Maintenance Schedule (value object)

Invariants to maintain:
- Only one charging session per station at a time
- Power delivery within hardware limits
- Must verify connector compatibility
- Prevent charging if station offline
```

#### Reservation Aggregate:
```
Aggregate Root: Reservation
├─ Customer Reference (value object)
├─ Facility Reference (value object)
├─ Space Allocation (reference to Parking aggregate)
└─ Time Window (value object)

Invariants to maintain:
- Reservation duration must be positive
- Cannot reserve in the past
- Cannot overlap with other reservations for same space
- Must release space on expiration
```

#### Billing Aggregate:
```
Aggregate Root: Invoice
├─ Line Items (collection)
├─ Customer Reference (value object)
├─ Payment Records (collection)
└─ Amount Summary (value object)

Invariants to maintain:
- Total must equal sum of line items
- Cannot modify finalized invoice
- All line items must be non-negative
- Payment cannot exceed total amount
```

---

## Part 2: Microservices Architecture

### 2.1 Service Decomposition

Based on bounded contexts, we identify microservices:

```
┌─────────────────────────────────────────────────────────────────┐
│               API GATEWAY / LOAD BALANCER                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────┐  ┌──────────────────┐                   │
│  │  Parking Service │  │ Reservation Svc  │                   │
│  ├──────────────────┤  ├──────────────────┤                   │
│  │ • Space Mgmt     │  │ • Reservations   │                   │
│  │ • Entry/Exit     │  │ • Bookings       │                   │
│  │ • Occupancy      │  │ • Cancellations  │                   │
│  │ • Status         │  │ • Availability   │                   │
│  │                  │  │ • Confirmations  │                   │
│  └────────┬─────────┘  └────────┬─────────┘                   │
│           │                     │                              │
│  ┌────────▼──────────┐  ┌──────▼─────────────┐               │
│  │ Charging Service │  │  Facility Service  │               │
│  ├────────────────┤  ├────────────────────┤               │
│  │ • Stations      │  │ • Facility Config  │               │
│  │ • Sessions      │  │ • Multi-tenancy    │               │
│  │ • Energy Track  │  │ • Capacity Mgmt    │               │
│  │ • Hardware Mgmt │  │ • Operations       │               │
│  └────────┬────────┘  └──────┬─────────────┘               │
│           │                  │                              │
│  ┌────────▼─────────────────▼──────────┐                  │
│  │    Billing & Revenue Service       │                  │
│  ├──────────────────────────────────┤                  │
│  │ • Invoices                        │                  │
│  │ • Payments                        │                  │
│  │ • Reports                         │                  │
│  │ • Revenue Analytics               │                  │
│  └────────┬─────────────────────────┘                   │
│           │                                              │
│  ┌────────▼─────────────────────────────────┐          │
│  │  Monitoring & Analytics Service         │          │
│  ├────────────────────────────────────────┤          │
│  │ • Real-time Metrics                     │          │
│  │ • Occupancy Tracking                    │          │
│  │ • Performance Analysis                  │          │
│  │ • Predictive Analytics                  │          │
│  └─────────────────────────────────────────┘          │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Microservice Specifications

#### Service 1: Parking Service

**Responsibility**: Core parking space and vehicle management

**Key Operations**:
- Register parking space
- Update space status
- Record vehicle entry
- Record vehicle exit
- Query space availability
- Calculate occupancy rates

**Database Schema**:
```
Table: parking_spaces
├─ space_id (PK)
├─ facility_id (FK)
├─ size (enum)
├─ status (enum)
├─ location_floor
├─ location_aisle
├─ location_number
├─ last_updated
└─ created_at

Table: parking_sessions
├─ session_id (PK)
├─ vehicle_id
├─ space_id (FK)
├─ facility_id (FK)
├─ entry_time
├─ exit_time
├─ charge_amount
├─ created_at
└─ updated_at

Table: vehicles
├─ vehicle_id (PK)
├─ registration_number (UNIQUE)
├─ make
├─ model
├─ color
├─ vehicle_type (enum)
├─ is_electric (boolean)
├─ owner_id (FK to User Service)
└─ created_at
```

**External API Endpoints**:
```
POST /parking/v1/spaces
  Create new parking space
  Request: { facility_id, size, location }
  Response: { space_id, status, location }

GET /parking/v1/spaces/{facility_id}
  List all spaces in facility
  Query params: ?status=AVAILABLE&size=STANDARD
  Response: [{ space_id, size, status, location }]

POST /parking/v1/sessions/entry
  Record vehicle entry
  Request: { vehicle_id, space_id, facility_id }
  Response: { session_id, entry_time }

POST /parking/v1/sessions/{session_id}/exit
  Record vehicle exit
  Request: { exit_time, charge_amount }
  Response: { session_id, duration_hours, charge_amount }

GET /parking/v1/occupancy/{facility_id}
  Get occupancy metrics
  Response: { 
    total_spaces, occupied_spaces, available_spaces,
    occupancy_rate, availability_by_size
  }
```

**Service-to-Service APIs**:
```
Internal: GET /parking/internal/sessions/{session_id}
  Used by Billing Service to calculate charges
  
Internal: GET /parking/internal/spaces/{space_id}/status
  Used by Reservation Service to verify space availability
  
Internal: POST /parking/internal/sessions/{session_id}/validate
  Used by Charging Service to verify parking session exists
```

**Events Published**:
```
parking.vehicle.entered
  { vehicle_id, space_id, facility_id, timestamp }

parking.vehicle.exited
  { vehicle_id, space_id, session_id, facility_id, timestamp }

parking.space.occupied
  { space_id, facility_id, timestamp }

parking.space.released
  { space_id, facility_id, timestamp }

parking.occupancy.threshold
  { facility_id, occupancy_rate, timestamp }
```

---

#### Service 2: Reservation Service

**Responsibility**: Parking space reservations

**Key Operations**:
- Create reservation
- Confirm reservation
- Cancel reservation
- Check availability windows
- Release reserved space
- Prevent double-booking

**Database Schema**:
```
Table: reservations
├─ reservation_id (PK)
├─ customer_id (FK)
├─ facility_id (FK)
├─ space_id (FK)
├─ desired_size (enum)
├─ start_time
├─ end_time
├─ status (enum: PENDING, CONFIRMED, CANCELLED, EXPIRED)
├─ created_at
├─ confirmed_at
├─ cancelled_at
└─ expires_at

Table: reservation_holds
├─ hold_id (PK)
├─ reservation_id (FK)
├─ space_id (FK)
├─ held_until
├─ created_at
└─ released_at

Index: reservations (facility_id, start_time, end_time)
Index: reservations (customer_id, status)
Index: reservations (space_id, status, end_time)
```

**External API Endpoints**:
```
POST /reservations/v1/create
  Create new reservation
  Request: { 
    customer_id, facility_id, desired_space_size,
    start_time, end_time 
  }
  Response: { reservation_id, status, confirmation_code }

GET /reservations/v1/{reservation_id}
  Get reservation details
  Response: { reservation_id, space_id, status, times, customer_id }

POST /reservations/v1/{reservation_id}/confirm
  Confirm pending reservation
  Response: { reservation_id, status, parking_details }

POST /reservations/v1/{reservation_id}/cancel
  Cancel reservation
  Response: { reservation_id, status, cancellation_reason }

GET /reservations/v1/availability
  Check availability
  Query params: ?facility_id=&start_time=&end_time=&size=
  Response: { 
    available_slots, available_spaces,
    next_available_time, pricing_estimate
  }
```

**Service-to-Service APIs**:
```
Internal: GET /reservations/internal/facility/{facility_id}/available-windows
  Used by Parking Service to find available reservation windows

Internal: POST /reservations/internal/validate-arrival
  Used by Parking Service to verify customer has valid reservation
```

**Events Published**:
```
reservation.created
  { reservation_id, customer_id, facility_id, start_time, end_time }

reservation.confirmed
  { reservation_id, space_id, confirmation_code }

reservation.cancelled
  { reservation_id, reason }

reservation.expired
  { reservation_id, facility_id }
```

---

#### Service 3: Charging Service

**Responsibility**: EV charging station management and energy tracking

**Key Operations**:
- Register charging station
- Start charging session
- Update charging progress
- Stop charging session
- Track energy consumption
- Monitor hardware status
- Queue vehicles for charging

**Database Schema**:
```
Table: charging_stations
├─ station_id (PK)
├─ facility_id (FK)
├─ charger_level (enum: LEVEL1, LEVEL2, DCFC)
├─ connector_type (enum: CCS, Tesla, CHAdeMO)
├─ power_rating_kw
├─ status (enum: AVAILABLE, IN_USE, MAINTENANCE, OFFLINE)
├─ warranty_expiry
├─ last_maintenance
├─ created_at
└─ updated_at

Table: charging_sessions
├─ charging_session_id (PK)
├─ parking_session_id (FK)
├─ station_id (FK)
├─ vehicle_id
├─ start_time
├─ stop_time
├─ pause_count
├─ total_pause_duration
├─ energy_delivered_kwh
├─ cost
├─ status (enum: ACTIVE, PAUSED, COMPLETED, INTERRUPTED)
├─ created_at
└─ updated_at

Table: charging_queue
├─ queue_id (PK)
├─ vehicle_id
├─ facility_id (FK)
├─ arrival_time
├─ desired_capacity_kwh
├─ estimated_wait_time
├─ status (enum: WAITING, CHARGING, COMPLETED, CANCELLED)
└─ created_at

Index: charging_sessions (station_id, status, start_time)
Index: charging_sessions (vehicle_id, status)
```

**External API Endpoints**:
```
POST /charging/v1/stations
  Register new charging station
  Request: { 
    facility_id, charger_level, connector_type, 
    power_rating_kw 
  }
  Response: { station_id, status }

GET /charging/v1/stations/{facility_id}
  List charging stations at facility
  Response: [{ 
    station_id, charger_level, connector_type,
    power_rating_kw, status, availability 
  }]

POST /charging/v1/sessions/start
  Start charging session
  Request: { 
    vehicle_id, parking_session_id, station_id,
    target_charge_percent 
  }
  Response: { charging_session_id, start_time, estimated_duration }

GET /charging/v1/sessions/{charging_session_id}
  Get charging session status
  Response: { 
    session_id, vehicle_id, station_id, energy_delivered_kwh,
    current_rate_kw, time_remaining, estimated_cost
  }

POST /charging/v1/sessions/{charging_session_id}/stop
  Stop charging session
  Request: { stop_time, reason }
  Response: { session_id, energy_delivered_kwh, total_cost }

GET /charging/v1/availability
  Check station availability
  Query params: ?facility_id=&connector_type=
  Response: [{ station_id, wait_time, estimated_ready_time }]
```

**Service-to-Service APIs**:
```
Internal: POST /charging/internal/sessions/validate
  Used by Billing Service to validate charging session

Internal: GET /charging/internal/sessions/{session_id}/energy
  Used by Billing Service to get energy consumed for billing
```

**Events Published**:
```
charging.session.started
  { charging_session_id, vehicle_id, station_id, start_time }

charging.session.updated
  { charging_session_id, energy_delivered_kwh, current_rate_kw }

charging.session.completed
  { charging_session_id, energy_delivered_kwh, total_cost }

charging.station.status.changed
  { station_id, facility_id, previous_status, current_status }

charging.queue.position.changed
  { vehicle_id, queue_position, estimated_wait_time }
```

---

#### Service 4: Facility Service

**Responsibility**: Multi-facility management and configuration

**Key Operations**:
- Register new facility
- Configure facility capacity and pricing
- Manage multi-tenancy
- Track facility operations
- Generate facility reports
- Support different pricing strategies per facility

**Database Schema**:
```
Table: facilities
├─ facility_id (PK)
├─ name
├─ address
├─ city
├─ state
├─ postal_code
├─ latitude
├─ longitude
├─ total_capacity
├─ compact_spaces_count
├─ standard_spaces_count
├─ large_spaces_count
├─ charging_stations_count
├─ pricing_strategy (enum: BASIC, PEAK_HOUR, SUBSCRIPTION, EV_OPTIMIZED)
├─ opening_time
├─ closing_time
├─ operating_days
├─ tenant_id (FK)
├─ status (enum: ACTIVE, INACTIVE, MAINTENANCE)
├─ created_at
└─ updated_at

Table: pricing_configurations
├─ config_id (PK)
├─ facility_id (FK)
├─ vehicle_type (enum)
├─ hourly_rate
├─ daily_max
├─ monthly_rate
├─ peak_hour_multiplier
├─ night_rate_multiplier
├─ ev_charging_rate_per_kwh
├─ reservation_fee
├─ effective_from
├─ effective_to
└─ created_at

Table: facility_operations
├─ operation_id (PK)
├─ facility_id (FK)
├─ operation_date
├─ total_entries
├─ total_exits
├─ average_duration_hours
├─ peak_hour
├─ peak_occupancy_rate
├─ revenue_generated
├─ created_at
└─ updated_at

Index: facilities (tenant_id, status)
Index: pricing_configurations (facility_id, effective_from, effective_to)
```

**External API Endpoints**:
```
POST /facilities/v1/register
  Register new facility
  Request: { 
    name, address, capacity_breakdown,
    pricing_strategy, tenant_id 
  }
  Response: { facility_id, status }

GET /facilities/v1/{facility_id}
  Get facility details
  Response: { 
    facility_id, name, address, capacity,
    current_occupancy, pricing, operating_hours
  }

PUT /facilities/v1/{facility_id}/pricing
  Update pricing configuration
  Request: { vehicle_type, hourly_rate, daily_max, ... }
  Response: { facility_id, pricing_config }

GET /facilities/v1/{facility_id}/status
  Get current facility status
  Response: { 
    facility_id, occupancy_rate, available_spaces,
    average_turnaround, peak_hours, current_revenue_rate
  }

GET /facilities/v1/{facility_id}/operations-summary
  Get operations summary for date range
  Query params: ?start_date=&end_date=
  Response: { 
    total_transactions, total_revenue,
    average_session_duration, peak_hours_analysis
  }
```

**Service-to-Service APIs**:
```
Internal: GET /facilities/internal/{facility_id}/config
  Used by other services to get facility configuration

Internal: GET /facilities/internal/{facility_id}/pricing-strategy
  Used by Billing Service to get pricing strategy
```

**Events Published**:
```
facility.registered
  { facility_id, name, capacity }

facility.capacity.threshold
  { facility_id, occupancy_rate, available_spaces }

facility.operations.summary
  { facility_id, total_transactions, revenue, date }
```

---

#### Service 5: Billing & Revenue Service

**Responsibility**: Charge calculation, invoicing, and revenue tracking

**Key Operations**:
- Calculate parking charges
- Calculate EV charging costs
- Generate invoices
- Process payments
- Track revenue
- Generate financial reports
- Manage discounts and promotions

**Database Schema**:
```
Table: charges
├─ charge_id (PK)
├─ parking_session_id (FK)
├─ charging_session_id (FK, nullable)
├─ facility_id (FK)
├─ customer_id (FK)
├─ charge_type (enum: PARKING, CHARGING, RESERVATION, PENALTY)
├─ amount
├─ currency
├─ description
├─ created_at
└─ created_at

Table: invoices
├─ invoice_id (PK)
├─ customer_id (FK)
├─ facility_id (FK)
├─ invoice_date
├─ due_date
├─ total_amount
├─ currency
├─ status (enum: DRAFT, ISSUED, PAID, OVERDUE, CANCELLED)
├─ issue_date
├─ paid_date
├─ created_at
└─ updated_at

Table: invoice_line_items
├─ line_item_id (PK)
├─ invoice_id (FK)
├─ charge_id (FK)
├─ description
├─ quantity
├─ unit_price
├─ total_amount
└─ created_at

Table: payments
├─ payment_id (PK)
├─ invoice_id (FK)
├─ amount
├─ currency
├─ payment_method (enum: CREDIT_CARD, DEBIT_CARD, DIGITAL_WALLET)
├─ payment_processor_id
├─ status (enum: PENDING, COMPLETED, FAILED, REFUNDED)
├─ transaction_date
├─ confirmation_code
├─ created_at
└─ updated_at

Table: revenue_summary
├─ summary_id (PK)
├─ facility_id (FK)
├─ report_date
├─ parking_revenue
├─ charging_revenue
├─ reservation_revenue
├─ total_revenue
├─ transaction_count
├─ created_at
└─ updated_at

Index: charges (customer_id, created_at)
Index: invoices (customer_id, status, due_date)
Index: invoices (facility_id, invoice_date)
Index: payments (invoice_id, status)
Index: revenue_summary (facility_id, report_date)
```

**External API Endpoints**:
```
POST /billing/v1/charges/calculate
  Calculate charge for session
  Request: { parking_session_id, charging_session_id }
  Response: { charge_id, amount, breakdown { parking, charging, fees } }

GET /billing/v1/invoices/{customer_id}
  Get customer invoices
  Query params: ?status=&from_date=&to_date=
  Response: [{ 
    invoice_id, total_amount, status, due_date,
    line_items, payment_status
  }]

POST /billing/v1/invoices/{invoice_id}/pay
  Process payment for invoice
  Request: { payment_method, amount }
  Response: { payment_id, status, confirmation_code }

GET /billing/v1/revenue-summary/{facility_id}
  Get revenue summary for facility
  Query params: ?start_date=&end_date=&grouping=DAILY|WEEKLY|MONTHLY
  Response: [{ 
    date, parking_revenue, charging_revenue,
    total_revenue, transaction_count 
  }]

GET /billing/v1/customer-summary/{customer_id}
  Get customer billing summary
  Response: { 
    customer_id, total_spent, active_invoices,
    payment_history, loyalty_status
  }
```

**Service-to-Service APIs**:
```
Internal: GET /billing/internal/charges/{charge_id}
  Used by other services to get charge details

Internal: POST /billing/internal/charges/batch
  Used by backend jobs to process bulk charging
```

**Events Consumed**:
```
parking.vehicle.exited
  → Calculate parking charge, add to invoice

charging.session.completed
  → Calculate charging cost, add to invoice

Events Published**:
```
billing.charge.created
  { charge_id, customer_id, amount, charge_type }

billing.invoice.issued
  { invoice_id, customer_id, total_amount, due_date }

billing.payment.received
  { payment_id, customer_id, amount, timestamp }

billing.revenue.summary
  { facility_id, report_date, total_revenue }
```

---

#### Service 6: Monitoring & Analytics Service

**Responsibility**: Real-time metrics, analytics, and reporting

**Key Operations**:
- Track occupancy rates in real-time
- Generate occupancy reports
- Analyze peak hours
- Predict availability
- Generate business intelligence reports
- Alert on threshold violations
- Track performance metrics

**Database Schema** (Time-Series Optimized):
```
Table: occupancy_metrics (Time-Series)
├─ metric_id (PK)
├─ facility_id (FK)
├─ timestamp
├─ occupancy_rate
├─ occupied_spaces
├─ available_spaces
├─ available_compact_spaces
├─ available_standard_spaces
├─ available_large_spaces
├─ active_sessions
├─ active_charging_sessions
└─ created_at

Table: performance_metrics (Time-Series)
├─ metric_id (PK)
├─ facility_id (FK)
├─ timestamp
├─ entries_count
├─ exits_count
├─ average_session_duration_minutes
├─ revenue_rate_per_hour
├─ peak_occupancy
└─ created_at

Table: alerts
├─ alert_id (PK)
├─ facility_id (FK)
├─ alert_type (enum: HIGH_OCCUPANCY, LOW_AVAILABILITY, HIGH_REVENUE)
├─ threshold_value
├─ current_value
├─ created_at
├─ acknowledged_at
└─ acknowledged_by

Table: daily_reports
├─ report_id (PK)
├─ facility_id (FK)
├─ report_date
├─ total_transactions
├─ total_revenue
├─ average_occupancy_rate
├─ peak_hour
├─ peak_occupancy_rate
├─ least_busy_hour
├─ average_session_duration
├─ created_at
└─ updated_at

Index: occupancy_metrics (facility_id, timestamp DESC)
Index: performance_metrics (facility_id, timestamp DESC)
Index: daily_reports (facility_id, report_date DESC)
```

**External API Endpoints**:
```
GET /analytics/v1/occupancy/{facility_id}
  Get current occupancy
  Response: { 
    facility_id, occupancy_rate, occupied_spaces,
    available_by_size, trending, forecast
  }

GET /analytics/v1/occupancy/{facility_id}/history
  Get occupancy history
  Query params: ?start_date=&end_date=&interval=HOURLY|DAILY
  Response: [{ timestamp, occupancy_rate, available_spaces }]

GET /analytics/v1/peak-hours/{facility_id}
  Get peak hours analysis
  Response: { 
    facility_id, peak_hours, peak_occupancy,
    least_busy_hours, seasonal_patterns
  }

GET /analytics/v1/performance/{facility_id}
  Get facility performance metrics
  Query params: ?start_date=&end_date=
  Response: { 
    total_transactions, total_revenue, average_duration,
    revenue_per_transaction, customer_satisfaction
  }

GET /analytics/v1/forecast/{facility_id}
  Get occupancy forecast
  Query params: ?hours_ahead=24
  Response: { 
    facility_id, forecast_points: [{ 
      timestamp, predicted_occupancy, confidence_level 
    }]
  }

GET /analytics/v1/alerts/{facility_id}
  Get active alerts
  Response: [{ 
    alert_id, alert_type, message, severity,
    created_at, acknowledged
  }]
```

**Events Consumed**:
```
parking.vehicle.entered → Update occupancy metrics
parking.vehicle.exited → Update occupancy metrics
parking.space.occupied → Update metrics
parking.space.released → Update metrics
billing.payment.received → Update revenue metrics
charging.session.completed → Update charging metrics
```

**No External Events Published** (internal analytics only)

---

### 2.3 API Gateway

The API Gateway serves as single entry point for all client requests:

**Responsibilities**:
- Request routing to appropriate service
- Authentication and authorization
- Rate limiting and throttling
- Request/response logging
- API versioning
- Request transformation
- Load balancing
- CORS handling

**Routes**:
```
/api/v1/parking/* → Parking Service
/api/v1/reservations/* → Reservation Service
/api/v1/charging/* → Charging Service
/api/v1/facilities/* → Facility Service
/api/v1/billing/* → Billing Service
/api/v1/analytics/* → Analytics Service
/api/v1/health → Health Check Service
```

---

### 2.4 Communication Patterns

#### Synchronous (Request-Response):
- **API Gateway → Services**: Client requests
- **Service → Service**: When immediate response needed
  - Parking Service → Facility Service (get config)
  - Reservation Service → Parking Service (check availability)
  - Billing Service → Charging Service (get energy used)

#### Asynchronous (Event-Driven):
- **Message Queue/Event Bus**: Service events
  - Parking Service publishes: vehicle.entered, vehicle.exited, space.released
  - Charging Service publishes: session.started, session.completed
  - Billing Service consumes: vehicle.exited, charging.session.completed
  - Analytics Service consumes: all events

**Implementation Options**:
- **RabbitMQ**: For reliable message queuing
- **Apache Kafka**: For high-throughput event streaming
- **AWS SNS/SQS**: For cloud-native deployment
- **Azure Event Hubs**: For Azure deployments

---

### 2.5 Data Management Strategy

#### Database per Service:
Each microservice has its own database for autonomy:

```
┌──────────────────────────────────────────────────┐
│           Database Per Service Pattern             │
├──────────────────────────────────────────────────┤
│                                                  │
│  Parking Service DB          Charging Service DB │
│  ┌────────────────┐          ┌──────────────┐   │
│  │ spaces         │          │ stations     │   │
│  │ sessions       │          │ sessions     │   │
│  │ vehicles       │          │ queue        │   │
│  └────────────────┘          └──────────────┘   │
│                                                  │
│  Reservation Service DB      Facility Service DB│
│  ┌────────────────┐          ┌──────────────┐   │
│  │ reservations   │          │ facilities   │   │
│  │ holds          │          │ pricing      │   │
│  │ availability   │          │ operations   │   │
│  └────────────────┘          └──────────────┘   │
│                                                  │
│  Billing Service DB          Analytics Service DB
│  ┌────────────────┐          ┌──────────────┐   │
│  │ charges        │          │ metrics      │   │
│  │ invoices       │          │ reports      │   │
│  │ payments       │          │ alerts       │   │
│  │ revenue        │          │ forecasts    │   │
│  └────────────────┘          └──────────────┘   │
│                                                  │
└──────────────────────────────────────────────────┘
```

**Benefits**:
- ✅ Service autonomy: schema changes don't affect other services
- ✅ Technology diversity: use best database per service needs
- ✅ Scaling: each service scaled independently
- ✅ Failure isolation: one DB issue doesn't break entire system

**Consistency Management**:
- **Eventual Consistency**: Via events and async processing
- **Saga Pattern**: For multi-service transactions
  - Example: Parking exit transaction
    1. Record exit (Parking Service)
    2. Calculate charge (Billing Service)
    3. Create invoice (Billing Service)
    4. Update occupancy (Analytics Service)

**Database Choices**:
- **PostgreSQL**: Primary relational database for transactional services
- **Time-Series DB** (InfluxDB, Prometheus): Analytics and metrics
- **Redis**: Caching and session management
- **Elasticsearch**: Logging and search

---

### 2.6 Deployment Architecture

```
┌─────────────────────────────────────────────────────┐
│         Kubernetes Cluster / Cloud Platform         │
├─────────────────────────────────────────────────────┤
│                                                      │
│  ┌──────────────────────────────────────────────┐  │
│  │ API Gateway (Load Balanced)                  │  │
│  │ - Request routing                            │  │
│  │ - Authentication                             │  │
│  │ - Rate limiting                              │  │
│  └──────────────────────────────────────────────┘  │
│         ↓         ↓         ↓         ↓             │
│  ┌──────────┐ ┌────────┐ ┌────────┐ ┌────────┐   │
│  │ Parking  │ │Charging│ │Billing │ │Analytics│   │
│  │ Service  │ │Service │ │Service │ │Service │   │
│  │(x3 pods)│ │(x2 pods│ │(x2 pods│ │(x2 pods│   │
│  └──────────┘ └────────┘ └────────┘ └────────┘   │
│                                                     │
│  ┌──────────┐ ┌──────────┐ ┌─────────────────┐   │
│  │Reservation│ │ Facility │ │ Message Broker   │  │
│  │  Service │ │ Service  │ │ (RabbitMQ/Kafka) │  │
│  │(x2 pods)│ │(x1 pod)  │ │ (x3 nodes)      │  │
│  └──────────┘ └──────────┘ └─────────────────┘   │
│                                                     │
│  ┌─────────────────────────────────────────────┐  │
│  │ Data Layer (PostgreSQL, Redis, Time-Series) │  │
│  │ - Master-Replica setup for high availability│  │
│  │ - Automated backups                         │  │
│  │ - Replication across AZs                    │  │
│  └─────────────────────────────────────────────┘  │
│                                                     │
│  ┌─────────────────────────────────────────────┐  │
│  │ Observability Stack                         │  │
│  │ - Prometheus (metrics)                      │  │
│  │ - ELK Stack (logging)                       │  │
│  │ - Jaeger (tracing)                          │  │
│  │ - Alert Manager (alerts)                    │  │
│  └─────────────────────────────────────────────┘  │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

### 2.7 Security Architecture

**Authentication & Authorization**:
- OAuth 2.0 / OpenID Connect for user authentication
- JWT tokens for API authentication
- Role-Based Access Control (RBAC) for authorization
- Service-to-service authentication via mTLS

**Data Security**:
- Encryption at rest for all databases
- TLS/SSL for data in transit
- Database credentials in secure vault (HashiCorp Vault)
- PCI DSS compliance for payment processing

**API Security**:
- API key validation
- Rate limiting per client
- Input validation and sanitization
- SQL injection prevention (parameterized queries)
- CORS policy enforcement

---

### 2.8 Monitoring & Logging

**Metrics Collection**:
- Request latency per service
- Error rates and types
- Database query performance
- Message queue depth
- Resource utilization (CPU, memory, disk)

**Distributed Tracing**:
- Trace requests across services
- Identify performance bottlenecks
- Debug issues in microservice architecture

**Centralized Logging**:
- ELK Stack (Elasticsearch, Logstash, Kibana)
- Structured logging (JSON format)
- Log aggregation and search
- Alert on error patterns

---

### 2.9 Scalability Considerations

**Horizontal Scaling**:
- Services deployed in multiple pods
- Load balancer distributes traffic
- Auto-scaling based on CPU/memory metrics

**Database Scaling**:
- Read replicas for read-heavy services (Analytics)
- Partitioning for large tables (charges, invoices by date)
- Connection pooling

**Message Queue Scaling**:
- Message broker in cluster mode
- Topic partitioning for parallelism
- Consumer group scaling

**Caching Strategy**:
- Redis for session and frequent queries
- Cache invalidation on updates
- Distributed cache across services

---

## Part 3: Implementation Roadmap

### Phase 1: Monolith Refactoring (Weeks 1-4)
- Apply design patterns to existing code ✅ (Completed)
- Implement improved Vehicle and ParkingManager classes
- Add comprehensive testing

### Phase 2: Service Foundation (Weeks 5-8)
- Set up microservices infrastructure
- Implement API Gateway
- Deploy message broker

### Phase 3: Core Services (Weeks 9-16)
- Implement Parking Service
- Implement Billing Service
- Implement Analytics Service

### Phase 4: Advanced Features (Weeks 17-24)
- Implement Charging Service
- Implement Reservation Service
- Implement Facility Service

### Phase 5: Integration & Testing (Weeks 25-28)
- End-to-end integration testing
- Load testing
- Security testing

### Phase 6: Deployment & Operations (Weeks 29+)
- Production deployment
- Monitoring setup
- Operational runbooks

---

## Conclusion

This microservices architecture provides:

1. **Scalability**: Each service can scale independently
2. **Resilience**: Failure isolation between services
3. **Flexibility**: Services can be developed and deployed independently
4. **Technology Diversity**: Each service can use best-fit technology
5. **Business Alignment**: Services map to business domains
6. **Future Growth**: Easy to add new facilities, pricing models, EV charging

The architecture supports EasyParkPlus's expansion to multiple facilities while maintaining operational excellence through clear service boundaries, event-driven communication, and comprehensive monitoring.
