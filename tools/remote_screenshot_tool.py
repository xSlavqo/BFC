# tools/remote_screenshot_tool.py
import socket
import json
import base64
from PIL import Image
import io
import numpy as np
import time

class SimpleRemoteClient:
    def __init__(self, laptop_ip, port):
        self.laptop_ip = laptop_ip
        self.port = port

    def send_command(self, command_name, *args, **kwargs):
        try:
            cleaned_kwargs = {}
            for k, v in kwargs.items():
                if k == 'bbox' and isinstance(v, (tuple, list)):
                    cleaned_kwargs[k] = tuple(int(x) for x in v)
                elif isinstance(v, np.integer):
                    cleaned_kwargs[k] = int(v)
                else:
                    cleaned_kwargs[k] = v
            
            cleaned_args = []
            for arg in args:
                if isinstance(arg, np.integer):
                    cleaned_args.append(int(arg))
                else:
                    cleaned_args.append(arg)

            message = {'command': command_name, 'args': cleaned_args, 'kwargs': cleaned_kwargs}
            
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((self.laptop_ip, self.port))
                s.sendall(json.dumps(message).encode('utf-8'))
                
                response_data = b""
                while True:
                    chunk = s.recv(4096 * 8) 
                    if not chunk:
                        break
                    response_data += chunk
                    try:
                        response = json.loads(response_data.decode('utf-8'))
                        break
                    except json.JSONDecodeError:
                        if not chunk:
                            break
                        continue 
                
                if not response_data or 'command' not in message:
                    return None

                if response.get('status') == 'success':
                    return response.get('result')
                else:
                    return None
        except ConnectionRefusedError:
            return None
        except socket.timeout:
            return None
        except Exception as e:
            return None

    def grab_screenshot_remote(self, bbox=None):
        encoded_image = self.send_command('grab_screenshot', bbox=bbox)
        if encoded_image:
            try:
                decoded_image = base64.b64decode(encoded_image)
                image_stream = io.BytesIO(decoded_image)
                return Image.open(image_stream)
            except Exception as e:
                return None
        return None

def get_remote_screenshot_tool(laptop_ip, port):
    client = SimpleRemoteClient(laptop_ip, port)
    screenshot = client.grab_screenshot_remote(bbox=None) # Zawsze cały ekran
    if screenshot:
        return screenshot
    else:
        return None

if __name__ == '__main__':
    LAPTOP_IP = '192.168.1.11'
    PORT = 65432

    full_screenshot = get_remote_screenshot_tool(LAPTOP_IP, PORT)
    if full_screenshot:
        full_screenshot.save("remote_full_screenshot_tool.png")
    else:
        pass # Handle error if needed
