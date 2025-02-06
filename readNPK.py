import serial
import time
import struct

def read_npk():
    try:
        # Configure serial port (adjust port name as needed)
        ser = serial.Serial(
            port='/dev/ttyUSB0',  # Change this to match your system (e.g., 'COM3' on Windows)
            baudrate=9600,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=1
        )
        
        #Nitrogen Read
        # Send command in hex
        command = bytes.fromhex('0103001E0001E40C')
        ser.write(command)
        
        # Read response (expecting 7 bytes: 01 03 02 XX XX B8 44)
        response = ser.read(7)
        
        if len(response) == 7:
            # Extract the nitrogen value (XX XX)
            nitrogen_value = struct.unpack('>H', response[3:5])[0]
            print(f'Nitrogen Value: {nitrogen_value}')
        else:
            print('Invalid response length:', response)
            
        #Phosphorus Read
        # Send command in hex
        command = bytes.fromhex('0103001F0001B5CC')
        ser.write(command)
        
        # Read response (expecting 7 bytes: 01 03 02 XX XX B8 44)
        response = ser.read(7)
        
        if len(response) == 7:
            # Extract the Phosphorus value (XX XX)
            Phosphorus_value = struct.unpack('>H', response[3:5])[0]
            print(f'Phosphorus Value: {Phosphorus_value}')
        else:
            print('Invalid response length:', response)
            
        #Potassium Read
        # Send command in hex
        command = bytes.fromhex('01030020000185C0')
        ser.write(command)
        
        # Read response (expecting 7 bytes: 01 03 02 XX XX B8 44)
        response = ser.read(7)
        
        if len(response) == 7:
            # Extract the Potassium value (XX XX)
            Potassium_value = struct.unpack('>H', response[3:5])[0]
            print(f'Potassium Value: {Potassium_value}')
        else:
            print('Invalid response length:', response)
        
        ser.close()
        
        ser.close()
        
        
        
    except serial.SerialException as e:
        print('Serial Exception:', e)
    except Exception as e:
        print('Error:', e)

if __name__ == "__main__":
    while True:
        read_npk()
        time.sleep(5)
