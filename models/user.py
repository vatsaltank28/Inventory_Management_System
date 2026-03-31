class User:
    def __init__(self, user_id, username, password, role):
        self.user_id = user_id
        self.username = username
        self.password = password  # Plain text for demo purposes, hash in production
        self.role = role  # 'admin' or 'user'

    def __repr__(self):
        return f"<User {self.username} ({self.role})>"
