# Card
class Card:
    def __init__(self, cardNo, PIN, accountId):
        self.cardNo = cardNo
        self.PIN = PIN
        self.accountId = accountId

    def cardNo(self):
        return self.cardNo
    
    def getPIN(self):
        return self.PIN

# Account
class Account:
    def __init__(self, accountId, balance):
        self.accountId = accountId
        self.balance = balance
        self.lock = Lock()

    def getAccountId(self):
        return self.accountId
    
    def getBalance(self):
        return self.balance

    def deposit(self, amount):
        with self.lock:
            self.balance += amount

    def withdraw(self, amount):
        with self.lock:
            if self.balance < amount:
                return False
            self.balance -= amount
            return True
        
# Bank Server
class BankServer:
    def __init__(self):
        self.accounts = {}    # accountId -> Account
        self.cards = {}    # cardNo -> Card

    def addAccount(self, account):
        self.accounts[account.getAccountId()] = account

    def addCard(self, card):
        self.cards[card.getCardNo()] = card

    def validatePIN(self, currCardNo, PIN):
        for cardNo, card in self.cards.items():
            if cardNo == currCardNo:
                if card.getPIN() == PIN:
                    return True
            else:
                return False
        return False
    
    def getAccount(self, currCardNo):
        if currCardNo not in self.cards:
            return None
        card = self.cards[currCardNo]
        return self.accounts[card.getAccountId()]
    
# Cash Dispenser
class CashDispenser:
    def __init__(self, initialCash):
        self.cash = initialCash
        self.lock = Lock()

    def dispenseCash(self, amount):
        with self.lock:
            if amount > self.cash:
                return False
            self.cash -= amount
            return True
        
    def depositCash(self, amount):
        with self.lock:
            self.cash += amount

# Transaction
class Transaction(ABC):
    @abstractmethod
    def execute(self):
        pass

class BalanceEnquiry:
    def __init__(self, account):
        self.account = account

    def execute(self):
        self.account.getBalance()

class CashWithdrawal:
    def __init__(self, account, amount, dispenser):
        self.account = account
        self.amount = amount
        self.dispenser = dispenser

    def execute(self):
        return self.account.withdraw(self.amount) and self.dispenser.dispenseCash(amount)

class CashDeposit:
    def __init__(self, account, amount, dispenser):
        self.account = account
        self.amount = amount
        self.dispenser = dispenser

    def execute(self):
        self.account.deposit(self.amount)
        self.dispenser.depositCash(self.amount)

# ATM
class ATM:
    def __init__(self, bankServer, dispenser):
        self.bankServer = bankServer
        self.dispenser = dispenser
        self.currCard = None
        self.authenticated = False
    
    def insertCard(self, cardNo, PIN):
        if self.bankServer.validatePIN(cardNo, PIN):
            self.currCard = cardNo
            self.authenticated = True
            return True
        return False
    
    def performTransaction(self, transaction):
        if self.authenticated:
            transaction.execute()
            return True
        return False
    
    def ejectCard(self):
        self.currCard = None
        self.authenticated = False