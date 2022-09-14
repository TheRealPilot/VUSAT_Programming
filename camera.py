from picamera import PiCamera
from time import sleep
import time
from smbus2 import SMBus
# import smbus2 as smbus

class Altimeter:
    def __init__(self):
        self.pressure = 0
        self.altitude = 0
        self.temperature = 0

    def run(self, time):

        # Get I2C bus
        with SMBus(1) as bus:

            # MPL3115A2 address, 0x60(96)
            # Select control register, 0x26(38)
            #		0xB9(185)	Active mode, OSR = 128, Altimeter mode
            bus.write_byte_data(0x60, 0x26, 0xB9)
            # MPL3115A2 address, 0x60(96)
            # Select data configuration register, 0x13(19)
            #		0x07(07)	Data ready event enabled for altitude, pressure, temperature
            bus.write_byte_data(0x60, 0x13, 0x07)
            # MPL3115A2 address, 0x60(96)
            # Select control register, 0x26(38)
            #		0xB9(185)	Active mode, OSR = 128, Altimeter mode
            bus.write_byte_data(0x60, 0x26, 0xB9)

            time.sleep(1)

            # MPL3115A2 address, 0x60(96)
            # Read data back from 0x00(00), 6 bytes
            # status, tHeight MSB1, tHeight MSB, tHeight LSB, temp MSB, temp LSB
            data = bus.read_i2c_block_data(0x60, 0x00, 6)

            # Convert the data to 20-bits
            tHeight = ((data[1] * 65536) + (data[2] * 256) + (data[3] & 0xF0)) / 16
            temp = ((data[4] * 256) + (data[5] & 0xF0)) / 16
            altitude = tHeight / 16.0
            cTemp = temp / 16.0
            fTemp = cTemp * 1.8 + 32

            # MPL3115A2 address, 0x60(96)
            # Select control register, 0x26(38)
            #		0x39(57)	Active mode, OSR = 128, Barometer mode
            bus.write_byte_data(0x60, 0x26, 0x39)

            time.sleep(1)

            # MPL3115A2 address, 0x60(96)
            # Read data back from 0x00(00), 4 bytes
            # status, pres MSB1, pres MSB, pres LSB
            data = bus.read_i2c_block_data(0x60, 0x00, 4)

            # Convert the data to 20-bits
            pres = ((data[1] * 65536) + (data[2] * 256) + (data[3] & 0xF0)) / 16
            pressure = (pres / 4.0) / 1000.0

            # Output data to file
            with open('pressure.txt', 'a') as pressure_file:
                pressure_file.write(f"Pressure: {pressure:.2f} kPa")

            with open('altitude.txt', 'a') as altitude_file:
                altitude_file.write(f'Altitude: {altitude:.2f} m')

            with open('temperature.txt', 'a') as temperature_file:
                temperature_file.write(f'Temperature in Celsius: {cTemp:.2f} C')


    # def getAlt(self):
    #     return self.altitude
    #
    # def getPres(self):
    #     return self.pressure
    #
    # def getTemp(self):
    #     return self.temperature

def main() -> int:

    start = time.time()
    alt = Altimeter()

    while start.time() > 120:
        alt.run()
        with PiCamera() as camera:
            camera.resolution=(1920, 1080)
            camera.start_preview()
            camera.capture('pic{counter:03d}-{timestamp:%H-%M-%S-%f}.jpeg', format='jpeg')
            camera.stop_preview()
        time.sleep(60)             # sets capture interval to 1 minute
    return 0

if __name__ == '__main__':
    main()
