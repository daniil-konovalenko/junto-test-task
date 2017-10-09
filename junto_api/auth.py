from django.contrib.auth.models import User
import jwt
import datetime


def generate_access_token(user: User,
                          expires: datetime.datetime,
                          secret: str) -> str:
        
        token = jwt.encode(
            {
                'user_id': user.id,
                'exp': expires,
            },
            key=secret,
            algorithm='HS256').decode()
        
        return token
