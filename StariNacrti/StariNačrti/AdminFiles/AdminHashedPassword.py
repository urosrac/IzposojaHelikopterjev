import hashlib
HashedPassword = hashlib.sha256("admin".encode()).hexdigest()
print(HashedPassword)
