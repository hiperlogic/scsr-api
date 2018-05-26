import json
from six.moves.urllib.request import urlopen
from functools import wraps
from flask import request, jsonify, _request_ctx_stack
from flask_cors import cross_origin
from jose import jwt
import datetime
from sys_app.models.base_auth import App, Access


from sys_app import AuthError

AUTH0_DOMAIN = "hiperlogic.eu.auth0.com"
AUTH0_AUDIENCE = "https://gamegesis.com/app/"
SCOPE = "user"
RESPONSE_TYPE = "code"
CLIENT_ID = "sUiAT6EdmA4GA4eMwh3T3IODdivUQLgz"
REDIRECT_URI = "192.168.1.101:5000"
STATE = "TESTE"
ALGORITHMS = ["RS256"]

def app_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        app_id = request.headers.get('X-APP-ID')
        app_token = request.headers.get('X-APP-TOKEN')
        if app_id is None or app_token is None:
            error = {"code":"X-APP-ID_OR_X-APP-TOKEN_MISSING"}
            return jsonify({
                "error": error
            }), 403
        app = App.objects.filter(app_id=app_id).first()
        if not app:
            error={"code":"INVALID_CREDENTIALS"}
            return jsonify({"error": error}), 403
        access = Access.objects.filter(app=app).first()
        if(not access):
            error={"code":"INVALID_CREDENTIALS"}
            return jsonify({"error": error}), 403
        if access.token != app_token:
            error={"code":"INVALID_CREDENTIALS"}
            return jsonify({"error": error}), 403
        if access.expires < datetime.datetime.utcnow():
            
            error={"code":"TOKEN_EXPIRED"}
            return jsonify({"error": error}), 403

        return f(*args, **kwargs)
    return decorated_function


def get_token_auth_header():
    """Obtains the access token from the Authorization Header
    """
    print("Get Token")
    auth = request.headers.get("Authorization", None)
    print("Auth: "+str(auth))
    if not auth:
        raise AuthError.AuthError({"code": "authorization_header_missing",
                        "description":
                            "Authorization header is expected"}, 401)

    parts = auth.split()

    if parts[0].lower() != "bearer":
        raise AuthError.AuthError({"code": "invalid_header",
                        "description":
                            "Authorization header must start with"
                            " Bearer"}, 401)
    elif len(parts) == 1:
        raise AuthError.AuthError({"code": "invalid_header",
                        "description": "Token not found"}, 401)
    elif len(parts) > 2:
        raise AuthError.AuthError({"code": "invalid_header",
                        "description":
                            "Authorization header must be"
                            " Bearer token"}, 401)

    token = parts[1]
    return token


def requires_scope(required_scope):
    """Determines if the required scope is present in the access token
    Args:
        required_scope (str): The scope required to access the resource
    """
    print("scope")
    token = get_token_auth_header()
    unverified_claims = jwt.get_unverified_claims(token)
    if unverified_claims.get("scope"):
        token_scopes = unverified_claims["scope"].split()
        for token_scope in token_scopes:
            if token_scope == required_scope:
                return True
    return False


def requires_auth(f):
    """Determines if the access token is valid
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        print("Auth")
        token = get_token_auth_header()
        print("Token: "+ token)
        url="https://"+AUTH0_DOMAIN+"/.well-known/jwks.json"
        jsonurl = urlopen(url)
        print("===================================")
        byteStream=jsonurl.read()
        decoded = byteStream.decode("utf-8")
        print("ByteStream")
        print(byteStream)
        print("decoded")
        print(decoded)
        print("===================================")
        jwks = json.loads(decoded)
        try:
            unverified_header = jwt.get_unverified_header(token)
        except jwt.JWTError:
            raise AuthError.AuthError({"code": "invalid_header",
                            "description":
                                "Invalid header. "
                                "Use an RS256 signed JWT Access Token"}, 401)
        if unverified_header["alg"] == "HS256":
            raise AuthError.AuthError({"code": "invalid_header",
                            "description":
                                "Invalid header. "
                                "Use an RS256 signed JWT Access Token"}, 401)
        rsa_key = {}
        for key in jwks["keys"]:
            if key["kid"] == unverified_header["kid"]:
                rsa_key = {
                    "kty": key["kty"],
                    "kid": key["kid"],
                    "use": key["use"],
                    "n": key["n"],
                    "e": key["e"]
                }
        if rsa_key:
            try:
                payload = jwt.decode(
                    token,
                    rsa_key,
                    algorithms=ALGORITHMS,
                    audience=AUTH0_AUDIENCE,
                    issuer="https://"+AUTH0_DOMAIN+"/"
                )
            except jwt.ExpiredSignatureError:
                raise AuthError.AuthError({"code": "token_expired",
                                "description": "token is expired"}, 401)
            except jwt.JWTClaimsError:
                raise AuthError.AuthError({"code": "invalid_claims",
                                "description":
                                    "incorrect claims,"
                                    " please check the audience and issuer"}, 401)
            except Exception:
                raise AuthError.AuthError({"code": "invalid_header",
                                "description":
                                    "Unable to parse authentication"
                                    " token."}, 400)

            _request_ctx_stack.top.current_user = payload
            return f(*args, **kwargs)
        raise AuthError.AuthError({"code": "invalid_header",
                        "description": "Unable to find appropriate key"}, 400)
    return decorated


