import json
import ssl
import http.client
from urllib.parse import urlparse
import tempfile
import os
from django.conf import settings


class JsonRpcClient:
    def __init__(self, endpoint):
        self.endpoint = endpoint
        self.request_id = 1

    def _create_temp_cert_files(self):
        """Создание файлов из строки сертификатов"""
        cert_file = tempfile.NamedTemporaryFile(delete=False)
        key_file = tempfile.NamedTemporaryFile(delete=False)

        cert_file.write(settings.CERT_DATA.encode())
        key_file.write(settings.KEY_DATA.encode())

        cert_file.close()
        key_file.close()

        return cert_file.name, key_file.name

    def _cleanup_temp_files(self, cert_file, key_file):
        os.unlink(cert_file)
        os.unlink(key_file)

    def call_method(self, method, params=None):
        """Вызов клиента"""
        if params is None:
            params = {}

        payload = {
            'jsonrpc': '2.0',
            'method': method,
            'params': params,
            'id': self.request_id
        }

        cert_file, key_file = self._create_temp_cert_files()

        try:
            url = urlparse(self.endpoint)
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            context.load_cert_chain(certfile=cert_file, keyfile=key_file)

            conn = http.client.HTTPSConnection(
                url.netloc,
                context=context
            )

            headers = {'Content-Type': 'application/json'}
            conn.request('POST', url.path, json.dumps(payload), headers)

            response = conn.getresponse()
            response_data = response.read().decode()
            conn.close()

            return json.loads(response_data)

        except Exception as e:
            return {
                'error': {
                    'code': -32603,
                    'message': str(e)
                }
            }
        finally:
            self._cleanup_temp_files(cert_file, key_file)
            self.request_id += 1
