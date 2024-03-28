from drf_yasg import openapi

info = openapi.Info(
        title="ClimateTwin API",
        default_version='v1',
        description="""\
        Climate Twin is a **geospatial game API** that matches users to a randomly selected location anywhere in the world with a similar climate, finds historical sites or ruins nearby, and allows users to **create items** from these places and gift them to other users.
        
        In CT, there is a magical connection between two separate places that have similar weather. These places become more accessible and alive, for a brief period of time. Users bring a little of their weather with them, and the API takes note of wind direction/speed clashes, or harmonies, and also returns an interaction profile.
        
        The item concept here is bare-bones. My intention is to eventually return a whole boatload of interesting/unique weather comparison data for front-end developers to implement item design systems with.

        This project can be forked from my GitHub [here](https://github.com/zandra-handz/ClimateTwin).

        
        **Features**
        -Find and explore other places in the world with a similar current climate
        -Browse nearby historical sites and create/collect treasures
        -Befriend, gift treasures, and send messages to other users
        -View archive of all places you have visited
        

        **Authentication**
        -Uses token authentication.


        **Instructions to test**
        -auth/token/login and enter 'sara' and 'string1234'.
        -Copy token, click on Authorize button on the top right, and enter 'Token' + the token string you copied.
        -Now you should be able to test the endpoints! All data is dummy data.


        """,
        #terms_of_service="https://www.jaseci.org",
        contact=openapi.Contact(email="badrainbowz@gmail.com")
        #license=openapi.License(name="Awesome IP")
)

#python manage.py generate_swagger --format yaml > api_documentation.yaml
