# Shamlessly stolen from https://api.smugmug.com/api/v2/doc/tutorial/oauth/non-web.html, with a a few tweaks 
import json
from requests_oauthlib import OAuth1Session
import sys
import os
from pathlib import Path


class SmugmugServiceException(Exception):
    def __init__(self,msg):
        super().__init__(msg)

class SmugmugService:

    OAUTH_ORIGIN = 'https://secure.smugmug.com'
    REQUEST_TOKEN_URL = OAUTH_ORIGIN + '/services/oauth/1.0a/getRequestToken'
    ACCESS_TOKEN_URL = OAUTH_ORIGIN + '/services/oauth/1.0a/getAccessToken'
    AUTHORIZE_URL = OAUTH_ORIGIN + '/services/oauth/1.0a/authorize'
    API_ORIGIN = 'https://api.smugmug.com'

    def __init__( self ):
        self.api_key = None
        self.api_secret = None

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
        
    def create_access_token( self ):

        if (not self.api_key or not self.api_key):
            raise SmugmugServiceException( f"Someone forgot to call validate_config before calling get_oauth_service...")
        step=""
        try:
            step="get_request_token"
            # First, we need a request token and secret, which SmugMug will give us.
            # We are specifying "oob" (out-of-band) as the callback because we don't
            # have a website for SmugMug to call back to.
            session=OAuth1Session(self.api_key, client_secret=self.api_secret, callback_uri="oob")
            response=session.fetch_request_token(self.REQUEST_TOKEN_URL)
 
            # Second, we need to give the user the web URL where they can authorize our
            # application.
            step="get auth code"
            auth_url = session.authorization_url(self.AUTHORIZE_URL, Access='Full', Permissions='Modify')
            print(f'Go to {auth_url} in a web browser.')

            step="input code"
            # Once the user has authorized our application, they will be given a
            # six-digit verifier code. Our third step is to ask the user to enter that
            # code:
            sys.stdout.write('Enter the six-digit code from the browser: ')
            sys.stdout.flush()
            verifier = sys.stdin.readline().strip()

            # Finally, we can use the verifier code, along with the request token and
            # secret, to sign a request for an access token.
            step="get access token"
            response=session.fetch_access_token(self.ACCESS_TOKEN_URL,verifier=verifier)
            at=response.get("oauth_token")
            ats=response.get("oauth_token_secret")

            # Validate the session
            step="validate access token"
            #print(session.get(
            #    self.API_ORIGIN + '/api/v2!authuser',
            #    headers={'Accept': 'application/json'}).text)
            
            # The access token we have received is valid forever, unless the user
            # revokes it, store it.
            step="store access token"
            accessobj={ 'access_token': at, 'access_token_secret': ats}
            with open( self.get_accessfilename(), "w") as fp:
                  json.dump( accessobj, fp )

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
                resource_owner_key=accessobj['access_token'],
                resource_owner_secret=accessobj['access_token_secret'])

        except Exception as e:
            raise SmugmugServiceException( f"Exception {e} during {step}" )
        return session
    
    def get_api_base( self ):
         return( self.API_ORIGIN )
    

        


