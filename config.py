from authomatic.providers import oauth2, oauth1
CONFIG = {
    
    'tw': { # Your internal provider name
           
        # Provider class
        'class_': oauth1.Twitter,
        
        # Twitter is an AuthorizationProvider so we need to set several other properties too:
        'consumer_key': 'xNJ4jPIc76zseIOPDtGENySNU',
        'consumer_secret': 'ARVGqLatNQNZUGlSpIkLVX9ySxCng25N3aSLjPSWa4G8lv44JU'
    }
}