import sched, time
from datetime import datetime
import logging
import logging.handlers

#AdafruitIO
# Import library and create instance of REST client.
from Adafruit_IO import Client
aio = Client('48eb52be9fed48d4b1fd94cd4a1e8e00')


# Import SPI library (for hardware SPI) and MCP3008 library.
import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008
from Adafruit_BME280 import *

#logging!
log_file_name = 'LogRaw.log'
logging_level = logging.INFO

# set Timed Rotating File Handler
formatter = logging.Formatter('%(asctime)s,%(name)s, %(levelname)s, %(message)s',"%Y-%m-%d %H:%M:%S")

#Rotate Every night at midnight and keep 180 logs
handler = logging.handlers.TimedRotatingFileHandler(log_file_name, when="midnight", interval=1, backupCount=180)
handler.setFormatter(formatter)

logger = logging.getLogger("Sensors")
logger.addHandler(handler)
logger.setLevel(logging_level)


#Logging Header
logger.info("Start Logging")
logger.info("ASCTime,Name,Level,1,2,3,4,5,6,7,degrees,pressure,humidity")


# Hardware SPI configuration:
SPI_PORT   = 0
SPI_DEVICE = 0
mcp = Adafruit_MCP3008.MCP3008(spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE))

#BME(Temp/Humidity/Pressure)
sensor = BME280(t_mode=BME280_OSAMPLE_8, p_mode=BME280_OSAMPLE_8, h_mode=BME280_OSAMPLE_8)


print('Reading MCP3008 values, press Ctrl-C to quit...')
# Print nice channel column headers.
print('| {0:>4} | {1:>4} | {2:>4} | {3:>4} | {4:>4} | {5:>4} | {6:>4} | {7:>4}'.format(*range(8)))
print('-' * 21)
# Main program loop.
while True:

   try:
    # Read Temp Values
    degrees = 9.0/5.0 * sensor.read_temperature() + 32
    pascals = sensor.read_pressure()
    hectopascals = pascals / 100
    humidity = sensor.read_humidity()

    # Read all the ADC channel values in a list.
    values = [0]*8
    for i in range(8):
        # The read_adc function will get the value of the specified channel (0-7).
        values[i] = mcp.read_adc(i)
    # Print the ADC values.
    print('| {0:>4} | {1:>4} | {2:>4} | {3:>4} | {4:>4} | {5:>4} | {6:>4} | {7:>4}'.format(*values) + ' Temp:{:.2f},Pressure:{:0.2f},Humidity{:0.2f}'.format(degrees,hectopascals,humidity))
    logger.info('{0:>4},{1:>4},{2:>4},{3:>4},{4:>4},{5:>4},{6:>4},{7:>4}'.format(*values) + ',{:.2f},{:0.2f},{:0.2f}'.format(degrees,hectopascals,humidity))


    try:
        aio.send('Gas_Sensor_Temp', '{:.2f}'.format(degrees))
    except Exception:
        pass
    try:
        aio.send('Gas_Sensor_Humidity', '{:.2f}'.format(humidity))
    except Exception:
        pass
    try:
            aio.send('Gas_Sensor_MQ136', '{}'.format(mcp.read_adc(0)))
    except Exception:
        pass
    try:
            aio.send('Gas_Sensor_MQ6', '{}'.format(mcp.read_adc(1)))
    except Exception:
        pass
    try:
            aio.send('Gas_Sensor_MQ135', '{}'.format(mcp.read_adc(2)))
    except Exception:
        pass
    try:
            aio.send('Gas_Sensor_MQ2', '{}'.format(mcp.read_adc(3)))
    except Exception:
        pass

    #Sleep till the minute mark
    t = datetime.now()
    sleeptime = 60 - (t.second + t.microsecond/1000000.0)
    time.sleep(sleeptime)

   except Exception as e:
    logging.exception("message")
    pass  # or you could use 'continue'
