# Enums
class PaymentStatus(Enum):
    PENDING = 1
    COMPLETE = 2
    FAILED = 3

class OrderStatus(Enum):
    PENDING = 1
    IN_PROGRESS = 2
    SHIPPED = 3
    DELIVERED = 4
    FAILED = 5
    CANCELLED = 6

# Person
class Person:
    def __init__(self, id, name):
        self.id = id
        self.name = name

    def getID(self):
        return self.id
    
    def getName(self):
        return self.name
    
class Customer(Person):
    def __init__(self, id, name, address, contact):
        super().__init__(id, name)
        self.address = address
        self.contact = contact
        self.cart = Cart(self)
        self.orderHistory = []    # list of Order

    def getAddress(self):
        return self.address
    
    def getCartItems(self):
        return self.cart.getItems()
    
    def getCartTotal(self):
        return self.cart.getCartTotal()
    
    def clearCart(self):
        self.cart = Cart(self)

    def addToOrderHistory(self, order):
        self.orderHistory.append(order)

class Seller(Person):
    def __init__(self, id, name):
        super().__init__(id, name)
        self.products = []    # list of Product

    def createProduct(self, productId, name, price, stock):
        newProduct = Product(productId, name, price, stock)
        self.products.append(newProduct)
        return newProduct

    def listProducts(self):
        return self.products
    
# Product
class Product:
    def __init__(id, name, price, stock, seller=None):
        self.id = id
        self.name = name
        self.price = price
        self.stock = stock
        self.seller = seller
        self.lock = Lock()

    def isAvailable(self, quantity):
        return self.stock >= quantity
    
    def removeStock(self, quantity):
        with self.lock:
            if self.isAvailable(quantity):
                self.stock -= quantity
                return True
            return False
        
    def addStock(self, quantity):
        with self.lock:
            self.stock += quantity

    def getPrice(self):
        return self.price

# Inventory
class Inventory:
    def __init__(self):
        self.products = {}    # productId -> Product
        self.lock = Lock()

    def addProduct(self, product):
        with self.lock:
            self.products[product.getId()] = product

    def getProductById(self, productId):
        if productId in self.products:
            return self.products[productId]
        return None
    
    def removeProduct(self, productId):
        with self.lock:
            if productId in self.products:
                del self.products[productId]

    def listProducts(self):
        return list(self.products.values())
    
# Cart
class Cart:
    def __init__(self, customer):
        self.customer = customer
        self.items = {}    # product -> quantity

    def addProduct(self, product, quantity):
        if product.removeStock(quantity):
            self.items[product] = self.items.get(product, 0) + quantity
        else:
            print("Not enough stock!")

    def removeStock(self, product):
        if product in self.items:
            self.items[product] -= 1
            if self.items[product] == 0:
                del self.items[product]

    def getCartTotal(self):
        res = 0
        for product, quantity in self.items.items():
            res += product.getPrice() * quantity
        return res
    
    def getItems(self):
        return self.items.copy()
    
# Payment
# abstract class
class PaymentGateway(ABC):
    @abstractmethod
    def pay(self, customer, amount):
        pass

class CreditCardPayment(PaymentGateway):
    def pay(self, customer, amount):
        # payment implementation
        return True
    
class DebitCardPayment(PaymentGateway):
    def pay(self, customer, amount):
        # payment implementation
        return True
    
# Singleton Payment Service
class PaymentService:
    _instance = None
    _lock = Lock()

    def __new__(cls):
        with cls._lock:
            if not cls._instance:
                cls._instance = super().__new__(cls)
        return cls._instance
    
    def makePayment(self, paymentMethod, customer, amount):
        return paymentMethod.pay(customer, amount)
    
# Order
class Order:
    def __init__(self, id, customer, items, amount, status=OrderStatus.PENDING):
        self.id = id
        self.customer = customer
        self.items = items
        self.amount = amount
        self.address = address
        self.status = status
        self.time = datetime.now()

    def updateStatus(self, status):
        self.status = status

class OrderManager:
    _instance = None
    _lock = Lock()

    def __new__(cls):
        with cls._lock:
            if not cls._instance:
                cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        self.orders = {}    # orderId -> Order
        self.orderId = 1
        self.lock = Lock()
        self.paymentService = PaymentService()

    def placeOrder(self, customer, paymentMethod):
        with self.lock:
            items = customer.getCartItems()
            totalPrice = customer.getCartTotal()
            orderId = self.orderId
            self.orderId += 1
        order = Order(orderId, customer, items, totalPrice)
        self.orders[orderId] = order
        customer.addToOrderHistory(order)
        if self.paymentService.makePayment(paymentMethod, customer, totalPrice):
            order.updateStatus(OrderStatus.IN_PROGRESS)
        else:
            order.updateStatus(OrderStatus.FAILED)
        customer.clearCart()
        return order
    
    def cancelOrder(self, orderId):
        with self.lock:
            order = self.orders[orderId]
            order.updateStatus(OrderStatus.CANCELLED)
            return True
        return False
    
# Amazon
class Amazon:
    _instance = None
    _lock = Lock()

    def __new__(cls):
        with cls._lock:
            if not cls._instance:
                cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        self.customers = {}    # id -> Customer
        self.sellers = {}    # id -> Seller
        self.inventory = Inventory()
        self.orderManager = OrderManager()

    def registerCustomer(self, id, name, address, contact):
        customer = Customer(id, name, address, contact)
        self.customers[id] = customer

    def registerSeller(self, id, name):
        seller = Seller(id, name)
        self.sellers[id] = seller

    def addProductToInventory(self, sellerId, productId, name, price, stock):
        seller = self.sellers[sellerId]
        if not seller:
            return False
        product = seller.createProduct(productId, name, price, stock)
        self.inventory.addProduct(product)
        return True
    
    def placeOrder(self, customer, paymentMethod):
        return self.orderManager.placeOrder(customer, paymentMethod)
    
    def cancelOrder(self, orderId):
        return self.orderManager.cancelOrder(orderId)