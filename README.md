# JSON-RPC Client with TLS Authentication

Django project for interacting with JSON-RPC 2.0 service using mutual TLS authentication.

## Installation

### Windows
```bash
git clone https://github.com/HRAON88/test_jsonrpc.git
```
```bash
cd test_jsonrpc
```
```bash
python -m venv venv
```
```bash
.\venv\Scripts\activate
```
```bash
pip install django
```
```bash
python manage.py runserver
```

### Linux/MacOS
```bash
git clone https://github.com/HRAON88/test_jsonrpc.git
```
```bash 
cd test_jsonrpc
```
```bash
python3 -m venv venv
```
```bash
source venv/bin/activate
```
```bash
pip install django
```
```bash
python manage.py runserver
```


## Features
- JSON-RPC 2.0 API method calls
- Client certificate authentication
- User interface for sending requests
- API response display

## Usage
1. Open http://127.0.0.1:8000
2. Enter method name ("auth.check")
3. Add parameters if needed
4. Send request

## Testing
```bash
python manage.py test
```

