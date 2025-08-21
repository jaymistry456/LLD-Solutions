from enum import Enum
from threading import Lock
from abc import ABC
from datetime import datetime


# =========================
# Guest
# =========================
class Guest:
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


# =========================
# Room
# =========================
class RoomType(Enum):
    SINGLE = 1
    DOUBLE = 2
    DELUXE = 3

class RoomStatus(Enum):
    AVAILABLE = 1
    RESERVED = 2
    OCCUPIED = 3

class Room:
    def __init__(self, roomNo, roomType, price):
        self.roomNo = roomNo
        self.roomType = roomType
        self.price = price
        self.roomStatus = RoomStatus.AVAILABLE

    def getRoomNo(self):
        return self.roomNo

    def getRoomType(self):
        return self.roomType

    def getPrice(self):
        return self.price

    def getRoomStatus(self):
        return self.roomStatus

    def _updateStatus(self, status):
        self.roomStatus = status

    def reserve(self):
        self._updateStatus(RoomStatus.RESERVED)

    def occupy(self):
        self._updateStatus(RoomStatus.OCCUPIED)

    def release(self):
        self._updateStatus(RoomStatus.AVAILABLE)


class RoomManager:
    def __init__(self):
        self.rooms = {}    # roomNo -> Room
        self._lock = Lock()

    def addRoom(self, room):
        with self._lock:
            self.rooms[room.getRoomNo()] = room

    def getAvailableRooms(self, roomType):
        with self._lock:
            return [
                room for room in self.rooms.values()
                if room.getRoomType() == roomType and room.getRoomStatus() == RoomStatus.AVAILABLE
            ]


# =========================
# Booking
# =========================
class BookingStatus(Enum):
    PENDING = 1
    CONFIRMED = 2
    CANCELLED = 3
    COMPLETED = 4

class Booking:
    def __init__(self, bookingNo, guest, room, checkIn, checkOut, price):
        self.bookingNo = bookingNo
        self.guest = guest
        self.room = room
        self.checkIn = checkIn
        self.checkOut = checkOut
        self.price = price
        self.bookingStatus = BookingStatus.PENDING

    def _updateStatus(self, status):
        self.bookingStatus = status

    def confirm(self):
        self._updateStatus(BookingStatus.CONFIRMED)
        self.room.reserve()

    def cancel(self):
        self._updateStatus(BookingStatus.CANCELLED)
        self.room.release()

    def complete(self):
        self._updateStatus(BookingStatus.COMPLETED)
        self.room.release()


class BookingManager:
    _instance = None
    _lock = Lock()

    def __new__(cls):
        with cls._lock:
            if not cls._instance:
                cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self.bookings = {}    # bookingNo -> Booking
        self.bookingCounter = 0
        self._lock = Lock()

    def createBooking(self, guest, room, checkIn, checkOut, price):
        with self._lock:
            if room.getRoomStatus() != RoomStatus.AVAILABLE:
                return None
            self.bookingCounter += 1
            booking = Booking(self.bookingCounter, guest, room, checkIn, checkOut, price)
            booking.confirm()
            self.bookings[self.bookingCounter] = booking
            return booking

    def cancelBooking(self, bookingId):
        with self._lock:
            if bookingId not in self.bookings:
                return False
            self.bookings[bookingId].cancel()
            return True


# =========================
# Payment
# =========================
class PaymentStatus(Enum):
    PENDING = 1
    SUCCESS = 2
    FAILED = 3

class PaymentGateway(ABC):
    def pay(self, amount):
        pass

class CreditCardPayment(PaymentGateway):
    def pay(self, amount):
        return PaymentStatus.SUCCESS

class DebitCardPayment(PaymentGateway):
    def pay(self, amount):
        return PaymentStatus.SUCCESS

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


# =========================
# Hotel Management System (Facade)
# =========================
class HotelManagementSystem:
    def __init__(self):
        self.roomManager = RoomManager()
        self.bookingManager = BookingManager()
        self.paymentService = PaymentService()

    def addRoom(self, room):
        self.roomManager.addRoom(room)

    def searchAvailableRooms(self, roomType):
        return self.roomManager.getAvailableRooms(roomType)

    def bookRoom(self, guest, room, checkIn, checkOut, paymentMethod):
        price = room.getPrice()
        paymentStatus = self.paymentService.processPayment(paymentMethod, price)
        if paymentStatus == PaymentStatus.SUCCESS:
            return self.bookingManager.createBooking(guest, room, checkIn, checkOut, price)
        return None

    def cancelBooking(self, bookingId):
        return self.bookingManager.cancelBooking(bookingId)
