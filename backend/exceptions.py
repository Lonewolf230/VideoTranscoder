class S3UploadError(Exception):
    pass

class DatabaseError(Exception):
    pass

class VideoNotFoundError(Exception):
    pass

class SQSMessageError(Exception):
    pass

class UserCreationFailedError(Exception):
    pass

class UserLoginFailedError(Exception):
    def __init__(self, message,status_code):
        self.status_code=status_code
        super().__init__(message)

class UserLogoutFailedError(Exception):
    pass

class JWTTokenError(Exception):
    
    def __init__(self,status_code,message):
        self.status_code=status_code
        super().__init__(message)

class RedisError(Exception):
    pass
