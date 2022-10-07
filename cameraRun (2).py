from picamera import PiCamera
from time import sleep
import time
from smbus2 import SMBus
import FaBo9Axis_MPU9250
import sys

class humidity:
    def __init__(self):
        self.humidity = 0
        self.temperature = 0

    def run2(self, time):
        with SMBus(1) as bus:

            # SHT31 address, 0x44(68)
            bus.write_i2c_block_data(0x44, 0x2C, [0x06])

            time.sleep(0.5)

            # SHT31 address, 0x44(68)
            # Read data back from 0x00(00), 6 bytes
            # Temp MSB, Temp LSB, Temp CRC, Humididty MSB, Humidity LSB, Humidity CRC
            data = bus.read_i2c_block_data(0x44, 0x00, 6)

            # Convert the data
            temp = data[0] * 256 + data[1]
            cTemp = -45 + (175 * temp / 65535.0)
            # fTemp = -49 + (315 * temp / 65535.0)
            humidity = 100 * (data[3] * 256 + data[4]) / 65535.0

            # Output data to screen
            with open('humidity.txt', 'a') as humidity_file:
                humidity_file.write(f"Relative Humidity: {humidity:.2f} %RH\n")

            with open('temperature1.txt', 'a') as temperature1_file:
                temperature1_file.write(f'Temperature in Celsius: {cTemp:.2f} C\n')

class Altimeter:
    def __init__(self):
        self.pressure = 0
        self.altitude = 0
        self.temperature = 0

    def run(self, time):

        # Get I2C bus
        with SMBus(1) as bus:
            time.sleep(0.25)
            # MPL3115A2 address, 0x60(96)
            # Select control register, 0x26(38)
            #		0xB9(185)	Active mode, OSR = 128, Altimeter mode
            bus.write_byte_data(0x60, 0x26, 0xB9,True)
            # MPL3115A2 address, 0x60(96)
            # Select data configuration register, 0x13(19)
            #		0x07(07)	Data ready event enabled for altitude, pressure, temperature
            bus.write_byte_data(0x60, 0x13, 0x07,True)
            # MPL3115A2 address, 0x60(96)
            # Select control register, 0x26(38)
            #		0xB9(185)	Active mode, OSR = 128, Altimeter mode
            bus.write_byte_data(0x60, 0x26, 0xB9,True)

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
                pressure_file.write(f"Pressure: {pressure:.2f} kPa\n")

            with open('altitude.txt', 'a') as altitude_file:
                altitude_file.write(f'Altitude: {altitude:.2f} m\n')

            with open('temperature.txt', 'a') as temperature_file:
                temperature_file.write(f'Temperature in Celsius: {cTemp:.2f} C\n')


    # def getAlt(self):
    #     return self.altitude
    #
    # def getPres(self):
    #     return self.pressure
    #
    # def getTemp(self):
    #     return self.temperature

def imu():
    mpu9250 = FaBo9Axis_MPU9250.MPU9250()

    accel = mpu9250.readAccel()
    with open('acceleration.txt', 'a') as acceleration_file:
        acceleration_file.write(f"Ax: {accel['x']} m/s^2\n")
    with open('acceleration.txt', 'a') as acceleration_file:
        acceleration_file.write(f"Ay: {accel['y']} m/s^2\n")
    with open('acceleration.txt', 'a') as acceleration_file:
        acceleration_file.write(f"Az: {accel['z']} m/s^2\n\n")

    gyro = mpu9250.readGyro()
    with open('gyroscope.txt', 'a') as gyroscope_file:
        gyroscope_file.write(f"Ax: {gyro['x']} rad/s\n")
    with open('gyroscope.txt', 'a') as gyroscope_file:
        gyroscope_file.write(f"Ay: {gyro['y']} rad/s\n")
    with open('gyroscope.txt', 'a') as gyroscope_file:
        gyroscope_file.write(f"Az: {gyro['z']} rad/s\n")

    mag = mpu9250.readMagnet()
    with open('magnet.txt', 'a') as magnet_file:
        magnet_file.write(f"Ax: {mag['x']} uT\n")
        magnet_file.write(f"Ay: {mag['y']} uT\n")
    with open('magnet.txt', 'a') as magnet_file:
        magnet_file.write(f"Ay: {mag['y']} uT\n")
    with open('magnet.txt', 'a') as magnet_file:
        magnet_file.write(f"Az: {mag['z']} uT\n")

def main() -> int:
    duration = int(sys.argv[1])
    for i in range(duration):
        alt = Altimeter()
        hum = humidity()
        time.sleep(1)
        alt.run(time)
        hum.run2(time)
        imu()
        with PiCamera() as camera:
            camera.resolution=(1920, 1080)
            camera.start_preview()
            camera.capture(f'/home/pi/pictures/picture{i}.jpeg', format='jpeg')
            camera.stop_preview()
        time.sleep(6.5)       # sets capture interval to 1 minute
    return 0

if __name__ == '__main__':
    main()
