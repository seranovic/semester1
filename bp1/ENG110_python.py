import serial as serial
import struct
import time
from typing import Tuple, List

def get_eng110_data(port: str = '/dev/ttyUSB0', baudrate: int = 9600, timeout: float = 2.0) -> Tuple[bytes, bytes, List[float]]:
    """
    Get data from ENG110 device over serial communication.-
    
    Args:
        port: Serial port name (e.g., 'COM3' on Windows, '/dev/ttyUSB0' on Linux)
        baudrate: Baud rate for serial communication (default: 9600)
        timeout: Read timeout in seconds (default: 2.0)
    
    Returns:
        Tuple containing:
        - data: List of 13 float values representing:
              [V, A, W, VAr, VA, Ws, time, freq, cos(w), cos(phi)]
               - V        : True RMS-Voltage [Volt]
               - A        : True RMS-Current [Amp]
               - W        : True effect [Watt]
               - VAr      : Blind Effect, sqrt(VA^2-W^2) [Only for sinus) [Watt]
               - VA       : Apparent effect, V*A [Only for sinus) [Watt]
               - Ws       : Logged energy in Ws [J]
               - time     : Time sins start of logging [s]
               - freq     : Frequency [Hz]
               - w        : Measured phase angle
               - cos(phi) : cos of Calculated phase angle W/VA
    Raises:
        serial.SerialException: If serial port cannot be opened
        ValueError: If response length is incorrect
    """
    
    # Command to get data from ENG110
    command = bytes([2, 5, 149, 97, 3])
    
    # Open serial port
    ser = serial.Serial(port=port, baudrate=baudrate, timeout=timeout)
    
    try:
        # Empty the buffer
        if ser.in_waiting > 0:
            ser.read(ser.in_waiting)
        
        # Send command
        ser.write(command)
        
        # Read 63 bytes of response
        response = ser.read(63)
        
        # Validate response length
        if len(response) != 63:
            raise ValueError(f"Expected 63 bytes, received {len(response)} bytes")
        
        # Extract time and date (bytes 4-9, which are indices 3-8 in Python)
        time_date = response[3:9]
        
        # Extract 13 floats from bytes 10-61 (indices 9-61 in Python)
        # Each float is 4 bytes, single precision (little-endian)
        data = []
        for i in range(9, 53, 4):  # Start at byte 10 (index 9), step by 4
            # Extract 4 bytes and convert to single precision float (little-endian)
            float_bytes = response[i:i+4]
            value = struct.unpack('<f', float_bytes)[0]  # '<f' = little-endian float
            data.append(value)
        
        return  data
    
    finally:
        # Always close the port
        ser.close()


# Example usage
if __name__ == "__main__":
    # Replace with your actual serial port
    PORT = '/dev/ttyUSB0'  # Windows example, use '/dev/ttyUSB0' for Linux
    
    try:
        # Get data 10 times with 1 second pause
        for j in range(10):
            values = get_eng110_data()
            
            # Print the 10 float values
            #print(" ".join(f"{val:6.2f}" for val in values))

            print(f"""
            V = {values[0]:6.2f}, A = {values[1]:6.2f}, W = {values[2]:6.2f},
            VAr =  {values[3]:6.2f}, VA =  {values[4]:6.2f}
            Ws =  {values[5]:6.2f}, time =  {values[6]:6.2f}
            freq =  {values[7]:6.2f}, w =  {values[8]:6.2f}, cos(phi) =  {values[9]:6.2f}
            """)

            time.sleep(1)
            
    except serial.SerialException as e:
        print(f"Serial communication error: {e}")
    except ValueError as e:
        print(f"Data validation error: {e}")
    
        
