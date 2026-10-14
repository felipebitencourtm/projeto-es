class Usuario:
    def __init__(self, userId, email, username, dateRegister, passwordHash):
        self.userId = userId
        self.email = email
        self.username = username
        self.dateRegister = dateRegister
        self.passwordHash = passwordHash

    def changeUsername(self, name):
        self.username = name
        return True 

    def changeEmail(self, email):
        self.email = email
        return True

    def auth(self, password):
        return password == passwordHash


