# cats-api

This API was made for Hack Club's [RaspAPI](https://raspapi.hackclub.com/).
- Flask API for viewing/uploading/deleting cat images
- Uses JWT authentication
- Swagger documentation (Flask-RESTX)
- Stores user data using SQLite
   
You can check out the live API demo [here](https://cats-api.boki.hackclub.app/).  
I've also made a demo website which utilises the API. You can check out the [live demo](https://cats.boki.hackclub.app/) or access the [repository](https://github.com/bojanradjenovic/cats).
## Installation
1. Clone the repository  
  ```git clone https://github.com/bojanradjenovic/cats-api.git```
2. Navigate to the repository directory  
   ```cd cats-api```
3. Make a virtual environment (recommended)
4. Install the required dependencies  
   ```pip install -r requirements.txt```
6. Fill out the configuration file (rename to config.json afterwards)
7. Run the app!

## Swagger API Documentation

Once the server is running, you can access the API documentation at:

```
http://localhost:5000
```
or at the address you specified.
