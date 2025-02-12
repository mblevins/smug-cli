
import json


a=[3,4]
b=[1,2]
c=[5,6]

a.extend( b )
a.extend( c )
print( json.dumps( a  ) )