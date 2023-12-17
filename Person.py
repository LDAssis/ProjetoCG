import random
class Person:
    def __init__(self, id, centerX, centerY, sensiW, sensiH):
        self.id = id
        self.centerX = centerX
        self.centerY = centerY
        self.sensiW = sensiW #Controls variation sensitivity. Greater sensitivity tolerates greater variation in X and Y position
        self.sensiH = sensiH  # Controls variation sensitivity. Greater sensitivity tolerates greater variation in X and Y position
        self.historyX = []
        self.historyY = []
        self.timeoutPerson = 0
        self.color = (random.randint(0, 255),random.randint(0, 255) ,random.randint(0, 255))
        self.isInvasion = False
        self.isSecure = False

    def attPos(self, centerX, centerY):
        self.historyX.insert(0,self.centerX)
        self.historyY.insert(0, self.centerY)
        self.centerX = centerX
        self.centerY = centerY
        if len(self.historyX) > 100:
            del self.historyX[-1]
            del self.historyY[-1]

    def addTimeout(self): #Count how many times this person don't appear in video, 10 frames is limit
        self.timeoutPerson = self.timeoutPerson + 1

    def isMe(self, centerX, centerY):
        if (abs(self.centerX - centerX) < self.sensiH):
            if (abs(self.centerY - centerY) < self.sensiW):
                return True
        return False