from machine import Pin, ADC, PWM
from time import sleep
import uasyncio
from math import log
from pico_library import Motor
global r1, r2, M1_step, M1_dir, M2_step, M2_dir

M_pins = [
    [Pin(2, Pin.OUT), Pin(3, Pin.OUT), Pin(4, Pin.OUT), Pin(5, Pin.OUT)],
    [Pin(6, Pin.OUT), Pin(7, Pin.OUT), Pin(8, Pin.OUT), Pin(9, Pin.OUT)]
    ]
motors = []
pot1 = ADC(Pin(26, Pin.OUT))
pot2 = ADC(Pin(27, Pin.OUT))
r1 = 0
r2 = 0
heater_pwm = PWM(Pin(22), freq=20000, duty_u16=0)

class Motor:
    def __init__(self, dir_pin, step_pin, threshold=4000):
        self.step_pin = motor_pwm = PWM(step_pin, freq=0, duty_u16=32768)
        self.dir_pin = dir_pin
        self.threshold = threshold
        self.speed = 0

    async def write(self):
        while True:
            
            if self.speed > 0:
                self.dir_pin.on()
            else:
                self.dir_pin.off()
            
            if 1 < abs(self.speed) < self.threshold:
                #print(str(self.speed))
                self.step_pin.freq(speed)
            else:
                self.step_pin.freq(0)
                await uasyncio.sleep(0.01)


async def update_temperature():
    t = 0
    t_array = []
    resistance_pin = ADC(Pin(28, Pin.IN))
    beta = 3950
    def_t = 25+273.15
    def_r = 100000
    
    while True:
        thermistor_output = resistance_pin.read_u16()
        resistance = 100000/(thermistor_output/(65536 - thermistor_output))
        t = def_t*beta/(def_t*log(resistance/def_r)+beta) - 273.15
        t_array.append(t)
        if len(t_array)>25:
            t_array.pop(0)
        t_mean = 0
        for i in t_array:
            t_mean += i
        t_mean = t_mean/len(t_array)
        print(t_mean)
        await uasyncio.sleep(0.05)


async def read_pot():
    global r1, r2, pot1, pot2
    while True:
        r1 = r1 + (pot1.read_u16() - 32768 - r1) / 3
        r2 = r2 + (pot2.read_u16() - 32768 - r2) / 3
        motors[0].speed = 60/r1
        motors[1].speed = 60/r2
        #print(str(r1) + "   " + str(r2))
        await uasyncio.sleep(0.05)

def motor_startup():
    for i in range(4):
        motors.append(Motor(M_pins[0][i], M_pins[1][i]))
    for i in motors:
        i.speed = 0.000001
        loop.create_task(i.write())


def main():
    global loop
    """while True:
        for i in range(655):
            heater_pwm.duty_u16(i*100)
            print(i*100)
            sleep(0.01)"""
    
    #heater_pwm.duty_u16(1000)
    
    loop = uasyncio.get_event_loop()
    #motor_startup()
    loop.create_task(update_temperature())
    #loop.create_task(read_pot())
    loop.run_forever()


if __name__ == "__main__":
    main()
    
