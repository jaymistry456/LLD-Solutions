# Enums
class SeatStatus:
    AVAILABLE = 1
    HELD = 2
    BOOKED = 3

class SeatType:
    NORMAL = 1
    PREMIUM = 2
    RECLINER = 3

class PaymentStatus:
    PENDING = 1
    FAILED = 2
    SUCCESS = 3

class BookingStatus:
    PENDING = 1
    CONFIRMED = 2
    CANCELLED = 3

DEFAULT_PRICING = {
    SeatType.NORMAL: 10,
    SeatType.PREMIUM: 15,
    SeatType.RECLINER: 20
}

# Movie
class Movie:
    def __init__(self, id, title, duration, language):
        self.id = id
        self.title = title
        self.duration = duration
        self.language = language

    def getId(self):
        return self.id
    
    def getTitle(self):
        return self.title
    
    def getDuration(self):
        return self.duration
    
    def getLangauge(self):
        return self.duration
    
# Theater
class Theater:
    def __init__(self, id, name, city):
        self.id = id
        self.name = name
        self.city = city

    def getId(self):
        return self.id

    def getName(self):
        return self.name
    
    def getCity(self):
        return self.city
    
# Seat
class Seat:
    def __init__(self, id, seatType, status):
        self.id = id
        self.seatType = seatType
        self.status = status
        self.lastChanged = datetime.now()

    def getId(self):
        return self.id
    
    def getSeatType(self):
        return self.seatType
    
    def getStatus(self):
        return self.status
    
    def getLastChanged(self):
        return self.lastChanged
    
    def updateStatus(self, seatStatus):
        self.status = seatStatus
        self.lastChanged = datetime.now()
    
# SeatManager
class SeatManager:
    HOLD_TIMEOUT = timedelta(minutes=5)

    def __init__(self, seats):
        self.seats = seats    # seatId -> Seat
        self.lock = Lock()
                
    def releaseExpiredHolds(self):
        with self.lock:
            curr = datetime.now()
            for seat in self.seats.values():
                if curr - seat.getLastChanged() > self.HOLD_TIMEOUT:
                    seat.updateStatus(SeatStatus.AVAILABLE)

    def view(self):
        with self.lock:
            self.releaseExpiredHolds()
            return {seatId: seat.getStatus() for seatId, seat in self.seats.items()}
        
    def hold(self, seatIds):
        with self.lock:
            self.releaseExpiredHolds()
            for seatId in seatIds:
                if seatId not in self.seats or self.seats[seatId].getStatus() != SeatStatus.AVAILABLE:
                    return False
            curr = datetime.now()
            for seatId in seatIds:
                self.seats[seatId].updateStatus(SeatStatus.HELD)
            return True
        
    def book(self, seatIds):
        with self.lock:
            self.releaseExpiredHolds()
            for seatId in seatIds:
                if seatId not in self.seats or self.seats[seatId].getStatus() != SeatStatus.HELD:
                    return False
            for seatId in seatIds:
                self.seats[seatId].setStatus(SeatStatus.BOOKED)
            return True
        
    def cancel(self, seatIds):
        with self.lock:
            self.releaseExpiredHolds()
            for seatId in seatIds:
                if seatId not in self.seats or self.seats[seatId].getStatus() != SeatStatus.BOOKED:
                    return False
            for seatId in seatIds:
                self.seats[seatId].setStatus(SeatStatus.AVAILABLE)
            return True
        
    def calculatePrice(self, seatIds):
        res = 0
        for seatId in seatIds:
            seatType = self.seats[seatId].getSeatType()
            res += DEFAULT_PRICING[seatType]
        return res
    
# Show
class Show:
    def __init__(self, id, movie, theater, seatLayout):
        self.id = id
        self.movie = movie
        self.theater = theater
        self.seatManager = SeatManager(seatLayout)

    def getId(self):
        return self.id
    
    def getMovie(self):
        return self.movie
    
    def getTheater(self):
        return self.theater
    
    def getSeatManager(self):
        return self.seatManager

# User
class User:
    def __init__(self, id, name, contact):
        self.id = id
        self.name = name
        self.contact = contact

    def getId(self):
        return self.id
    
    def getName(self):
        return self.name
    
    def getContact(self):
        return self.contact
    
# Payment
class PaymentGateway:
    def pay(self, user, amount):
        pass

class CreditCardPayment(PaymentGateway):
    def pay(self, user, amount):
        return PaymentStatus.SUCCESS
    
class DebitCardPayment(PaymentGateway):
    def pay(self, user, amount):
        return PaymentStatus.SUCCESS
    
class PaymentService:
    _instance = None
    _lock = Lock()

    def __new__(cls):
        with cls._lock:
            if not cls._instance:
                cls._instance = super().__new__(cls)
        return cls._instance
    
    def makePayment(self, paymentMethod, user, amount):
        return paymentMethod.pay(user, amount)
    
# Booking
class Booking:
    def __init__(self, id, showId, seatIds, amount, bookingStatus, createdAt):
        self.id = id
        self.showId = showId
        self.seatIds = seatIds
        self.amount = amount
        self.bookingStatus = bookingStatus
        self.createdAt = datetime.now()

# Booking System
class BookingSystem:
    def __init__(self):
        self.shows = {}    # showId -> Show
        self.bookings = {}    # bookingId -> Booking
        self.lock = Lock()

    def addShow(self, show):
        with self.lock:
            self.shows[show.getId()] = show

    def removeShow(self, showId):
        with self.lock:
            del self.shows[showId]

    def searchShows(self, title):
        res = []
        for show in self.shows.values():
            if show.getMovie().getTitle().lower() == title.lower():
                res.append(show)
        return res
    
    def createBooking(self, user, showId, seatIds, paymentMethod):
        with self.lock:
            show = self.shows[showId]
            seatManager = show.getSeatManager()
            if not show:
                return None
            # hold
            if not seatManager.hold(seatIds):
                return None
            # pyament
            amount = seatManager.calculatePrice(seatIds)
            paymentStatus = PaymentService().makePayment(paymentMethod, user, amount)
            if paymentStatus != PaymentStatus.SUCCESS:
                seatManager.cancelSeats(seatIds)
                return None
            # confirm
            seatManager.book(seatIds)
            booking = Booking(str(len(self.bookings)+1), show, seatIds, user)
            booking.updateStatus(BookingStatus.CONFIRMED)
            self.bookings[booking.getId()] = booking
            return booking