from api.oanda import OandaApi
from infrastructure.instrument_collection import instrumentCollection
from streaming.bot import Bot

if __name__ == "__main__":
    instrumentCollection.LoadInstruments("./data")
    bot = Bot()
    bot.runStreamer()
    # api = OandaApi()
    #  GBP_JPY dir:-1 gain:0.0923 sl:188.5435 tp:188.3897
    # api.place_trade("GBP_JPY", 100, -1,
    #                     188.5435, 188.3897)