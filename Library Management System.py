from enum import Enum
from abc import ABC, abstractmethod
from threading import Lock
from datetime import datetime

# Constants
MAX_BORROWED_BOOKS = 5
MAX_BORROW_DAYS = 10
FINE_PER_DAY = 2


# Enums
class BookStatus(Enum):
    AVAILABLE = "AVAILABLE"
    BORROWED = "BORROWED"
    RESERVED = "RESERVED"
    LOST = "LOST"


# Book Class
class Book:
    def __init__(self, isbn, title, year, authors):
        self.isbn = isbn
        self.title = title
        self.year = year
        self.authors = authors  # fixed assignment
        self.bookStatus = BookStatus.AVAILABLE

    def getISBN(self):
        return self.isbn

    def getTitle(self):
        return self.title

    def getYear(self):
        return self.year

    def getAuthors(self):
        return self.authors

    def setStatus(self, bookStatus):
        self.bookStatus = bookStatus

    def getStatus(self):
        return self.bookStatus


# Search Strategies
class SearchStrategy(ABC):
    @abstractmethod
    def search(self, books, keyword):
        pass


class SearchByTitle(SearchStrategy):
    def search(self, books, keyword):
        return [book for book in books if keyword.lower() in book.getTitle().lower()]


class SearchByAuthor(SearchStrategy):
    def search(self, books, keyword):
        return [book for book in books if keyword.lower() in [a.lower() for a in book.getAuthors()]]


class SearchByYear(SearchStrategy):
    def search(self, books, keyword):
        return [book for book in books if str(keyword) == str(book.getYear())]


# Person base class
class Person:
    def __init__(self, personId, name, email, contact):
        self.personId = personId
        self.name = name
        self.email = email
        self.contact = contact

    def getId(self):
        return self.personId


# Member
class Member(Person):
    def __init__(self, memberId, name, email, contact):
        super().__init__(memberId, name, email, contact)
        self.borrowedBooks = {}  # isbn -> (book, borrowDate)

    def canBorrow(self):
        return len(self.borrowedBooks) < MAX_BORROWED_BOOKS

    def borrowBook(self, book):
        self.borrowedBooks[book.getISBN()] = (book, datetime.now())

    def returnBook(self, book):
        isbn = book.getISBN()
        if isbn in self.borrowedBooks:
            book, borrowDate = self.borrowedBooks.pop(isbn)
            return borrowDate
        return None


# Librarian
class Librarian(Person):
    def __init__(self, librarianId, name, email, contact):
        super().__init__(librarianId, name, email, contact)
        self.libraryManager = LibraryManager.getInstance()

    def addBook(self, book):
        self.libraryManager.addBook(book)

    def removeBook(self, isbn):
        self.libraryManager.removeBook(isbn)


# Library Manager
class LibraryManager:
    _instance = None
    _instanceLock = Lock()

    @staticmethod
    def getInstance():
        if not LibraryManager._instance:
            with LibraryManager._instanceLock:
                if not LibraryManager._instance:
                    LibraryManager._instance = LibraryManager()
        return LibraryManager._instance

    def __init__(self):
        self.books = {}  # ISBN -> Book
        self.members = {}  # memberId -> Member
        self.booksLock = Lock()
        self.membersLock = Lock()

    def addBook(self, book):
        with self.booksLock:
            if book.getISBN() not in self.books:
                self.books[book.getISBN()] = book

    def removeBook(self, isbn):
        with self.booksLock:
            if isbn in self.books:
                self.books.pop(isbn)

    def registerMember(self, member):
        with self.membersLock:
            if member.getId() not in self.members:
                self.members[member.getId()] = member

    def removeMember(self, memberId):
        with self.membersLock:
            if memberId in self.members:
                self.members.pop(memberId)

    def search(self, searchStrategy, keyword):
        return searchStrategy.search(self.books.values(), keyword)

    def borrowBook(self, memberId, isbn):
        member = self.members.get(memberId)
        book = self.books.get(isbn)
        if member and book and member.canBorrow() and book.getStatus() == BookStatus.AVAILABLE:
            member.borrowBook(book)
            book.setStatus(BookStatus.BORROWED)
            print(f"[Library] Book '{book.getTitle()}' borrowed by {member.name}")
        else:
            print(f"[Library] Cannot borrow book '{isbn}'.")

    def returnBook(self, memberId, isbn):
        member = self.members.get(memberId)
        book = self.books.get(isbn)
        if not member or not book:
            print("[Library] Invalid return attempt.")
            return 0

        borrowDate = member.returnBook(book)
        if borrowDate:
            book.setStatus(BookStatus.AVAILABLE)
            fine = self.calculateFine(borrowDate, datetime.now())
            print(f"[Library] Book returned. Fine: ₹{fine}")
            return fine
        else:
            print("[Library] Book was not borrowed.")
            return 0

    def calculateFine(self, borrowDate, returnDate):
        return max(0, (returnDate - borrowDate).days - MAX_BORROW_DAYS) * FINE_PER_DAY