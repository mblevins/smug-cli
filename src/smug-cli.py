#! /bin/python
# CLI for flickr APIs
import click
import logging
from functools import wraps
import traceback
from smugmug_service import SmugmugService, SmugmugServiceException
import json
import re
import sys


logging.basicConfig(level=logging.INFO)
log = logging.getLogger("smug-cli")

class Context(object):
    smugmug=None
    debug=False
    def __init__(self, smugmug_service=None, debug=False):
        self.smugmug = smugmug_service
        self.debug = debug

class ApiHelper:
    smugmug_service=None
    session=None
    user=None
    api_base=None
    def __init__( self, smugmug_service ):
        self.smugmug_service = smugmug_service
        self.session=smugmug_service.get_session()

    def request( self, op, ep, data=None, params=None ):
        if not self.session:
            raise Exception( "session not available")
        headers={ 'Accept': 'application/json' }
        if (data):
            headers['Content-Type'] = 'application/json'
        if not params:
            params={}
        response=self.session.request( op, f"{self.get_api_base()}{ep}", headers=headers, json=data, params=params ) 
        # always reaise exception for http errors
        response.raise_for_status()
        return( response.json() )

    def get_api_base(self):
        if (not self.api_base):
            self.api_base = self.smugmug_service.get_api_base()
        return self.api_base 

    def get_user(self):
        if (not self.user):
            userobj=self.request( 'GET', '/api/v2!authuser' )
            self.user = userobj['Response']['User']['NickName']
        return self.user 

def command_wrapper(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except SmugmugServiceException as e:
            log.error(f"Error during smugmug service setup {e}")
            log.debug(traceback.format_exc())

@click.group()
@click.option('--debug', is_flag=True, help='Turn on debug statements',default=False)
@click.pass_context
def cli(ctx, debug ):
    # todo: turn on root DEBUG
    root = logging.getLogger()
    root.setLevel(logging.WARNING)
    if (debug):
        log.setLevel(logging.DEBUG)
    try:
        ctx.obj = Context( SmugmugService( ), debug )
        ctx.obj.smugmug.validate_config()
    except SmugmugServiceException as e:
        log.error(f"Error during smugmug service setup {e}")
        log.debug(traceback.format_exc())
        raise click.Abort()
        

@cli.command()
@click.pass_context
def authorize(ctx):
    try:
        ctx.obj.smugmug.create_access_token()
    except SmugmugServiceException as e:
        log.error(f"Error during smugmug service setup {e}")
        log.debug(traceback.format_exc())


def filter_output( orig_list, filter_keys ):
    return( [{k:v for (k,v) in l.items() if k in filter_keys} for l in orig_list] )


@cli.command()
@click.option('--raw', is_flag=True, help='Raw json',default=False)
@click.pass_context
def list_albums(ctx, raw ):
    """List albums
    """

    try:
        helper=ApiHelper( ctx.obj.smugmug )
        url=f"/api/v2/user/{helper.get_user()}!albums"
        album_list=[]
        params={'count': 100, 'start': 1 }
        while url:
            listobj=helper.request('GET', url, params=params )
            album_list.extend( listobj['Response']['Album'] )
            if ('NextPage' in listobj['Response']['Pages']):
                # seems to be a bug in the rqeuests lib, need to pass query params as options, the 
                # nextpage URL isn't working
                params={'count': 100, 
                        'start': listobj['Response']['Pages']['Start'] + listobj['Response']['Pages']['Count']}
            else:
                url=None
        if raw:
            print(json.dumps( {'Album': album_list}, indent=2))
        else:
            filter_keys=['UrlName', 'Name', 'AlbumKey', 'NodeID', 'Date']
            print(json.dumps( {'Album': filter_output( album_list, filter_keys)}, indent=2))
    except SmugmugServiceException as e:
        log.error(f"Error during smugmug service setup {e}")
        log.debug(traceback.format_exc())


def rename_helper( album, date ):
    """Come up with a new album name
    Returns an object with UrlName, Name
    """

    photo_year=date[0:4]

    # encode year
    # year may be off from photo year
    warnings=False
    found_likely_date = re.search(r"([12][789012][0-9][0-9])",album)
    if (found_likely_date):
        # if we found a date, remove it
        found_index=found_likely_date.start()
        if (found_likely_date.group(1) != photo_year):
            log.warning(f"{album} had encoded date of {found_likely_date.group(1)}, didn't match album date of {photo_year}, using album_date")
            photo_year=found_likely_date.group(1) 
            warnings=True
        # date is encoded, but in wrong place
        if found_index == len(album) - 4:
            # year is at end, remove it
            if (album[found_index-1] != "-" and album[found_index-1] != " "):
                log.error(f"{album} has weird encoded date")
                return None
            # one of these will work
            album=album.replace(f"-{photo_year}","",1)
            album=album.replace(f" {photo_year}","",1)
        elif album[found_index+4] == "-" or album[found_index+4] == " ":
            # year is in middle, remove it
            # one of these will work
            album=album.replace(f"{photo_year}-","",1)
            album=album.replace(f"{photo_year} ","",1)
        else:
            # dunno
            log.error(f"{album} has weird encoded date")
            return None
    album=f"{photo_year}-{album}"    

    return( {'UrlName': re.sub(r'[^a-zA-Z0-9-]', '', album),
             'Name': album })

@cli.command()
@click.pass_context
def create_rename_list(ctx):
    """Given a list from listalbums, suggest a new name for the album
    """
    inobj=json.load( sys.stdin )
    outobj={'RenamedAlbums': []}
    for old_album in inobj['Album']:
        new_album=rename_helper( old_album['Name'],  old_album['Date'] )
        if (new_album):
            if (new_album['Name'] != old_album['Name']):
                new_album['Date'] = old_album['Date']
                new_album['AlbumKey'] = old_album['AlbumKey']
                new_album['NodeID'] = old_album['NodeID']
                new_album['OldName'] = old_album['Name']
                outobj['RenamedAlbums'].append( new_album )
            else:
                log.info(f"Album {old_album['Name']} didn't change")
        else:
                # put this in with an error flag, easier to fix that way
                new_album={}
                new_album['UrlName'] = old_album['UrlName']
                new_album['Name'] = old_album['Name']
                new_album['AlbumKey'] = old_album['AlbumKey']
                new_album['NodeID'] = old_album['NodeID']
                new_album['OldName'] = old_album['Name']   
                new_album['Error'] = True
                outobj['RenamedAlbums'].append( new_album )    
    json.dump( outobj, sys.stdout, indent=2)

@cli.command()
@click.pass_context
def bulk_rename(ctx):
    """Given a list from create_rename_list, rename the albums
    """
    try:
        helper=ApiHelper( ctx.obj.smugmug )
        inobj=json.load( sys.stdin )
        for album in inobj['RenamedAlbums']:
            if not "Error" in album:
                updateobj={}
                updateobj['UrlName']=album['UrlName']
                updateobj['Name']=album['Name']
                helper.request(
                    'PATCH',
                    f"/api/v2/album/{album['AlbumKey']}",
                    data=updateobj)
    except SmugmugServiceException as e:
        log.error(f"Error during smugmug service setup {e}")
        log.debug(traceback.format_exc())

    
@cli.command()
@click.option('--album', is_flag=True, help='Smugmyg album page',default=False)
@click.pass_context
def create_photo_md(ctx, album):
    """Create a markdown page with photos
    """
        

if __name__ == '__main__':
    cli()


