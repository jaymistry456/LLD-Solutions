# Enums
class VehicleType(Enum):
    BIKE = 1
    CAR = 2
    TRUCK = 3

class SpotType(Enum):
    COMPACT = 1
    LARGE = 2
    HANDICAPPED = 3

# Vehicle
class Vehicle:
    def __init__(self, vehicleNum, vehicleType):
        self.vehicleNum = vehicleNum
        self.vehicleType = vehicleType

    def getVehicleNum(self):
        return self.vehicleType
    
    def getVehicleType(self):
        return self.vehicleType
    
# Parking Spot
class ParkingSpot:
    def __init__(self, spotId, spotType, vehicle=None):
        self.spotId = spotId
        self.spotType = spotType
        self.vehicle = vehicle

    def getSpotId(self):
        return self.spotId
    
    def getSpotType(self):
        return self.spotType
    
    def getVehicle(self):
        return self.vehicle
    
    def isAvailable(self):
        return self.vehicle == None
    
    def assignVehicle(self, vehicle):
        if self.isAvailable():
            self.vehicle = vehicle
            return True
        return False
    
    def releaseVehicle(self):
        if self.vehicle != None:
            self.vehicle = None
            return True
        return False
    
# Parking Floor
class ParkingFloors:
    def __init__(self, floorNum, compact, large, handicapped):
        self.floorNum = floorNum
        self.parkingSpots = []    # List of parking spots
        for i in range(compact):
            self.parkingSpots.append(f"C{i}_F{self.floorNum}", SpotType.COMPACT)
        for i in range(large):
            self.parkingSpots.append(f"L{i}_F{self.floorNum}", SpotType.LARGE)
        for i in range(handicapped):
            self.parkingSpots.append(f"H{i}_F{self.floorNum}", SpotType.HANDICAPPED)
    
    def getParkingSpots(self):
        return self.parkingSpots
    
# Parking Lot
class ParkingLot:
    def __init__(self, totalFloors, compact, large, handicapped):
        self.totalFloors = totalFloors
        self.parkingFloors = []    # list of parking floors
        for i in range(self.totalFloors):
            self.parkingFloors.append(ParkingFloor(i, compact, large, handicapped))

    def getRequiredSpotType(self, vehicleType, isHandicapped):
        if vehicleType == VehicleType.BIKE or vehicleType == VehicleType.CAR:
            if isHandicapped:
                return SpotType.HANDICAPPED
            else:
                return SpotType.COMPACT
        else:
            return SpotType.LARGE
        

    def getParkingFloors(self):
        return self.parkingFloors
        
# Parking Ticket
class ParkingTicket:
    def __init__(self, vehicle, spotId, floor):
        self.vehicle = vehicle
        self.spotId = spotId
        self.floor = floor
        self.issueTime = datetime.now()

    def getSpotId(self):
        return self.spotId

    def getFloor(self):
        return self.floor

    def getTicket():
        return f"Ticket(vehicle={self.vehcile.getVehcileNum()}, spotId={self.spotId.getSpotId()}, floor={self.floor.getFloorNum()}, issueTime={self.issueTime})"
    
# Parking System
class ParkingSystem:
    _instance = None
    _lock = Lock()

    @staticmethod
    def getInstance(self, parkingLot):
        if not ParkingSystem._instance:
            with ParkingSystem._lock:
                ParkingSystem._instance = ParkingSystem(parkingLot)
        return ParkingSystem._instance

    def __init__(self, parkingLot):
        self.parkingLot = parkingLot
        self.activeTickets = {}    # vehicleNum -> ticket

    def park(self, vehicle, isHandicapped):
        requiredSpotType = self.parkingLot.getRequiredSpotType(vehicle.getVehicleType(), isHandicapped)
        for floor in self.parkingLot.getParkingsFloors():
            for spot in floor.getParkingSpots():
                if spot.getSpotType() == requiredSpotType:
                    res = spot.assignVehicle(vehicle)
                    if not res:
                        continue
                    ticket = ParkingTicket(vehicle, spot.getSpotId(), floor.getFloorNum())
                    self.activeTickets[vehicle.getVehicleNum()] = ticket
                    return ticket
        return None
    
    def unpark(self, ticket):
        floor = ticket.getFloor()
        spotId = ticket.getSpotId()
        for spot in floor.getParkingSpots():
            if spot.getSpotId() == spotId:
                res = spot.releaseVehicle()
                if res:
                    del self.activeTickets[ticket.getVehcileNum()]
                    return True
        return False