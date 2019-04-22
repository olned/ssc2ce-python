# Simple package for Deribit API v2 websocket

## Description
The package use [aiohttp](https://aiohttp.readthedocs.io) 

API description look at [Deribit API v2 websocket](https://docs.deribit.com/v2/?python#json-rpc)



## Run examples from a clone

If you clone repository you can run examples from the root directory.
```.env
$ PYTHONPATH=.:$PYTHONPATH python examples/public.py
```

The private.py example uses [python-dotenv](https://github.com/theskumar/python-dotenv), you must install it if you want the example to work right out of the box or make the corresponding changes.
```bash
$ pip install python-dotenv
```
or make the corresponding changes, just removed followed code:
```python
    from dotenv import load_dotenv
    dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
    load_dotenv(dotenv_path)
```
To run the private.py example, you must either fill in the .env file or set the environment variables DERIBIT_CLIENT_ID and DERIBIT_CLIENT_SECRET. Look at .env_default. 
```bash
$ PYTHONPATH=.:$PYTHONPATH DERIBIT_CLIENT_ID=YOU_ACCESS_KEY DERIBIT_CLIENT_SECRET=YOU_ACCESS_SECRET python examples/private.py
```
