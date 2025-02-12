# Shamlessly stolen from https://api.smugmug.com/api/v2/doc/tutorial/oauth/non-web.html, with a a few tweaks 
import json
from rauth import OAuth1Service, OAuth1Session
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode
import sys
import os
from pathlib import Path


class SmugmugServiceException(Exception):
    def __init__(self,msg):
        super().__init__(msg)

class SmugmugService:

    api_key=None
    api_secret=None
    OAUTH_ORIGIN = 'https://secure.smugmug.com'
    REQUEST_TOKEN_URL = OAUTH_ORIGIN + '/services/oauth/1.0a/getRequestToken'
    ACCESS_TOKEN_URL = OAUTH_ORIGIN + '/services/oauth/1.0a/getAccessToken'
    AUTHORIZE_URL = OAUTH_ORIGIN + '/services/oauth/1.0a/authorize'
    API_ORIGIN = 'https://api.smugmug.com'

    def __init__( self ):
        pass

    def validate_config( self ):
        try:
            step="opening config.json"
            with open( self.get_configfilename(), "r" ) as fp:
                configobj=json.load( fp )
                if type(configobj) is not dict \
                        or 'api_key' not in configobj \
                        or 'api_secret' not in configobj\
                        or type(configobj['api_key']) is not str \
                        or type(configobj['api_secret']) is not str:
                            raise SmugmugServiceException( f"{self.get_configfilename()} doesn't contain a valid key/secret" )
            self.api_key = configobj['api_key']
            self.api_secret = configobj['api_secret']

        except Exception as e:
            raise SmugmugServiceException( f"Exception {e} during {step}" )      
        
    def get_configfilename( self ):
         return( os.path.join( Path.home(), ".smugcli", "config.json"))
    
    def get_accessfilename( self ):
         return( os.path.join(  Path.home(), ".smugcli", "access.json"))
        

    def get_oauth_service(self):
        oauth_service=None
        if (not self.api_key or not self.api_key):
            raise SmugmugServiceException( f"Someone forgot to call validate_config before calling get_oauth_service...")
        try:
            step="Creating OAuth1Service"
            oauth_service = OAuth1Service(
                    name='smugmug-oauth-web-demo',
                    consumer_key=self.api_key,
                    consumer_secret=self.api_secret,
                    request_token_url=self.REQUEST_TOKEN_URL,
                    access_token_url=self.ACCESS_TOKEN_URL,
                    authorize_url=self.AUTHORIZE_URL,
                    base_url=self.API_ORIGIN + '/api/v2')
        except Exception as e:
                raise SmugmugServiceException( f"Exception {e} during {step}" )
        return oauth_service


    def add_auth_params(self, auth_url, access=None, permissions=None):
        if access is None and permissions is None:
            return auth_url
        parts = urlsplit(auth_url)
        query = parse_qsl(parts.query, True)
        if access is not None:
            query.append(('Access', access))
        if permissions is not None:
            query.append(('Permissions', permissions))
        return urlunsplit((
            parts.scheme,
            parts.netloc,
            parts.path,
            urlencode(query, True),
            parts.fragment))

    def create_access_token( self ):

        # if get oauth service fails, pass exception directly back
        service = self.get_oauth_service( )
        step=""
        try:
            step="get_request_token"
            # First, we need a request token and secret, which SmugMug will give us.
            # We are specifying "oob" (out-of-band) as the callback because we don't
            # have a website for SmugMug to call back to.
            rt, rts = service.get_request_token(params={'oauth_callback': 'oob'})
 
            # Second, we need to give the user the web URL where they can authorize our
            # application.
            step="add auth parameters"
            auth_url = self.add_auth_params(
                    service.get_authorize_url(rt), access='Full', permissions='Modify')
            print('Go to %s in a web browser.' % auth_url)

            step="input parameters"
            # Once the user has authorized our application, they will be given a
            # six-digit verifier code. Our third step is to ask the user to enter that
            # code:
            sys.stdout.write('Enter the six-digit code: ')
            sys.stdout.flush()
            verifier = sys.stdin.readline().strip()

            # Finally, we can use the verifier code, along with the request token and
            # secret, to sign a request for an access token.
            step="get access token"
            at, ats = service.get_access_token(rt, rts, params={'oauth_verifier': verifier})

            # The access token we have received is valid forever, unless the user
            # revokes it.  Let's make one example API request to show that the access
            # token works.
            step="store access token"
            accessobj={ 'access_token': at, 'access_token_secret': ats}
            with open( self.get_accessfilename(), "w") as fp:
                  json.dump( accessobj, fp )

            step="authuser verification"
            session = OAuth1Session(
                service.consumer_key,
                service.consumer_secret,
                access_token=at,
                access_token_secret=ats)
            print(session.get(
                self.API_ORIGIN + '/api/v2!authuser',
                headers={'Accept': 'application/json'}).text)
        except Exception as e:
            raise SmugmugServiceException( f"Exception {e} during {step}" )

    def get_session(self):
        step=""
        session=None
        try:
            if (not self.api_key or not self.api_key):
                raise SmugmugServiceException( f"Someone forgot to call validate_config before calling get_session...")
            step="opening access.json"
            with open( self.get_accessfilename(), "r" ) as fp:
                accessobj=json.load( fp )
                if type(accessobj) is not dict \
                        or 'access_token' not in accessobj \
                        or 'access_token_secret' not in accessobj\
                        or type(accessobj['access_token']) is not str \
                        or type(accessobj['access_token_secret']) is not str:
                            raise SmugmugServiceException( f"{self.get_accessfilename()} doesn't contain a valid key/secret" )
                
            step="creating oauth session"
            session = OAuth1Session(
                self.api_key,
                self.api_secret,
                access_token=accessobj['access_token'],
                access_token_secret=accessobj['access_token_secret'])

        except Exception as e:
            raise SmugmugServiceException( f"Exception {e} during {step}" )
        return session
    
    def get_api_base( self ):
         return( self.API_ORIGIN )
    

        


