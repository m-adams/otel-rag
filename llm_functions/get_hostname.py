import socket
import unittest

definition = {
    "name": "get_hostname",
    "description": "Get the hostname of the machine.",
    "parameters": {
        "type": "object",
        "properties": {},
        "required": []
    }
}

def get_hostname():
    return socket.gethostname()

class TestGetHostname(unittest.TestCase):
    def test_get_hostname(self):
        hostname = get_hostname()
        self.assertIsInstance(hostname, str)
        self.assertTrue(len(hostname) > 0)

if __name__ == "__main__":
    #unittest.main()
    print(get_hostname())