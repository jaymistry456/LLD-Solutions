# Enums
class VoteType(Enum):
    UP = 1
    DOWN = 2

# Post
class Post:
    def __init__(self, id, author, content):
        self.id = id
        self.author = author
        self.content = content
        self.createdAt = datetime.now()
        self.votes = {}    # userId -> VoteType
        self.comments = []
        self.score = 0

    def addComment(self, comment):
        self.comments.append(comment)

    def vote(self, user, voteType):
        if voteType == VoteType.UP:
            self.score += 1
            self.votes[user.getUserId()] = VoteType.UP
        else:
            self.score -= 1
            self.votes[user.getUserId()] = VoteType.DOWN
    
    def getScore(self):
        return self.score
    
# Question
class Question(Post):
    def __init__(self, id, author, content, tags):
        super().__init__(id, author, content)
        self.tags = tags
        self.answers = []

    def addAnswer(self, answer):
        self.answers.append(answer)

    def getContent(self):
        return self.content
    
    def getTags(self):
        return self.tags.copy()

# Answer
class Answer(Post):
    def __init__(self, id, author, content, question):
        super().__init__(id, author, content)
        self.question = question

# Comment
class Comment:
    def __init__(self, id, author, content):
        self.id = id
        self.author = author
        self.content = content

# User
class User:
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.reputation = 0

    def updateReputation(self, points):
        self.reputation += points

# Stack Overflow
class StackOverflow:
    def __init__(self):
        self.users = {}    # userId -> User
        self.questions = {}    # questionId -> Question
        self.answers = {}    # answerId -> Answer
        self.comments = {}    # commentId -> Comment
        self.postCounter = 1
        self.commentCounter = 1

    def regiserUser(self, userId, name):
        user = User(userId, name)
        self.users[userId] = user
        return user
    
    def postQuestions(self, author, content, tags):
        question = Question(self.postCounter, author, content, tags)
        self.questions[self.postCounter] = question
        self.postCounter += 1
        return question
    
    def postAnswer(self, author, content, question):
        answer = Answer(self.postCounter, author, content, question)
        self.answers[self.postCounter] = answer
        self.postCounter += 1
        return answer
    
    def postComment(self, author, content, post):
        comment = Comment(self.commentCounter, author, content)
        self.comments[self.commentCounter] = comment
        self.commentCounter += 1
        post.addComment(comment)
        return comment
    
    def vote(self, user, post, voteType):
        post.vote(user, voteType)

    def searchByKeyword(self, keyword):
        res = []
        for q in self.questions.values():
            if keyword.lower() in q.getContent().lower():
                res.append(q)
        return res
    
    def searchByTag(self, tag):
        res = []
        for q in self.questions.values():
            for t in q.getTags():
                if t == tag:
                    res.append(q)
        return res