API_KEY = "69f109a1f4f5cc5df743768870afa57d-7eeba7f9b30b063c75a4c3e6fceeb083"
ACCOUNT_ID = "101-004-29766214-001"
OANDA_URL = "https://api-fxpractice.oanda.com/v3"
SECURE_HEADER ={
            'Authorization': f"Bearer {API_KEY}",
            "Content-Type":"application/json"
        }

server = "127.0.0.1" #"34.27.137.217" #"34.44.106.133" # "34.122.154.40"  #
BUY = 1
SELL = -1
NONE = 0


my_lot_size = 0.01*2
report_loss_threashold = -0.46*2
