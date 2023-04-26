from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
def token(user,seconds):
    s=Serializer('admin@123',seconds)
    return s.dumps({'user':user}).decode('utf-8')
