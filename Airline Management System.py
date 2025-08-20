from datetime import datetime
from threading import Lock
from enum import Enum
from abc import ABC, abstractmethod

# Passenger
class Passenger:
    def __init__(self, id, name, contact, email):
        self.id = id
        self.name = name
        self.contact = contact
        self.email = email

    def getId(self):
        return self.id
    
    def getName(self):
        return self.name
    
    def getContact(self):
        return self.contact
    
    def getEmail(self):
        return self.email

# Flight
class Flight:
    def __init__(self, flightNo, src, dest, departureTime, arrivalTime):
        self.flightNo = flightNo
        self.src = src
        self.dest = dest
        self.departureTime = departureTime
        self.arrivalTime = arrivalTime
        self.availableSeats = []   # list of Seat objects

    def getFlightNo(self):
        return self.flightNo
    
    def getSrc(self):
        return self.src
    
    def getDest(self):
        return self.dest
    
    def getDepartureTime(self):
        return self.departureTime
    
    def getArrivalTime(self):
        return self.arrivalTime
    
    def getDepartureDate(self):
        return self.departureTime.date()

# Aircraft
class Aircraft:
    def __init__(self, tailNo, totalSeats, model):
        self.tailNo = tailNo
        self.totalSeats = totalSeats
        self.model = model

    def getTailNo(self):
        return self.tailNo

# Seat
class SeatStatus(Enum):
    AVAILABLE = 1
    OCCUPIED = 2

class SeatType(Enum):
    ECONOMY = 1
    BUSINESS = 2
    FIRST_CLASS = 3

class Seat:
    def __init__(self, seatNo, seatType):
        self.seatNo = seatNo
        self.seatType = seatType
        self.seatStatus = SeatStatus.AVAILABLE

    def reserveSeat(self):
        self.seatStatus = SeatStatus.OCCUPIED

    def cancelSeat(self):
        self.seatStatus = SeatStatus.AVAILABLE

# Booking
class BookingStatus(Enum):
    CONFIRMED = 1
    CANCELLED = 2
    PENDING = 3

class Booking:
    def __init__(self, bookingNo, passenger, flight, seat, price):
        self.bookingNo = bookingNo
        self.passenger = passenger
        self.flight = flight
        self.seat = seat
        self.price = price
        self.bookingStatus = BookingStatus.CONFIRMED
        self.createdAt = datetime.now()

    def cancelBooking(self):
        self.bookingStatus = BookingStatus.CANCELLED
        self.seat.cancelSeat()

# BookingManager (Singleton)
class BookingManager:
    _instance = None
    _lock = Lock()

    def __new__(cls):
        with cls._lock:
            if not cls._instance:
                cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        self.bookingCounter = 0
        self.bookings = {}    # bookingNo -> Booking

    def createBooking(self, passenger, flight, seat, price):
        with self._lock:
            if seat.seatStatus != SeatStatus.AVAILABLE:
                return None
            seat.reserveSeat()
            self.bookingCounter += 1
            newBooking = Booking(self.bookingCounter, passenger, flight, seat, price)
            self.bookings[self.bookingCounter] = newBooking
            return newBooking
    
    def cancelBooking(self, bookingNo):
        with self._lock:
            if bookingNo in self.bookings:
                self.bookings[bookingNo].cancelBooking()
                return True
            return False

# Payment
class PaymentGateway(ABC):
    @abstractmethod
    def pay(self, amount):
        pass

class CreditCardPayment(PaymentGateway):
    def pay(self, amount):
        return True
    
class DebitCardPayment(PaymentGateway):
    def pay(self, amount):
        return True

class PaymentService:
    _instance = None
    _lock = Lock()

    def __new__(cls):
        with cls._lock:
            if not cls._instance:
                cls._instance = super().__new__(cls)
        return cls._instance
    
    def processPayment(self, paymentMethod, amount):
        return paymentMethod.pay(amount)

# FlightSearch
class FlightSearch:
    def __init__(self, flights):
        self.flights = flights  # dict flightNo -> Flight

    def searchFlights(self, src, dest, date):
        res = []
        for flight in self.flights.values():
            if (flight.getSrc() == src 
                and flight.getDest() == dest 
                and flight.getDepartureDate() == date):
                res.append(flight)
        return res

# Airline Management System
class AirlineManagementSystem:
    def __init__(self):
        self.flights = {}    # flightNo -> Flight
        self.aircrafts = {}  # tailNo -> Aircraft
        self.flightSearch = FlightSearch(self.flights)
        self.bookingManager = BookingManager()
        self.paymentService = PaymentService()

    def addFlight(self, flight):
        self.flights[flight.getFlightNo()] = flight

    def removeFlight(self, flightNo):
        if flightNo in self.flights:
            del self.flights[flightNo]

    def addAircraft(self, aircraft):
        self.aircrafts[aircraft.getTailNo()] = aircraft

    def searchFlights(self, src, dest, date):
        return self.flightSearch.searchFlights(src, dest, date)
    
    def bookFlight(self, passenger, flight, seat, price, paymentMethod):
        booking = self.bookingManager.createBooking(passenger, flight, seat, price)
        if booking and self.paymentService.processPayment(paymentMethod, price):
            return booking
        return None
    
    def cancelBooking(self, bookingNo):
        return self.bookingManager.cancelBooking(bookingNo)