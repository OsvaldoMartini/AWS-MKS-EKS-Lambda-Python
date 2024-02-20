import hmac
import hashlib
import base64

def verify_hmac_signature(request):
    secret_key = b'your_secret_key'
    received_signature = request.headers.get('X-Zuora-Signature')
    received_payload = request.data

    computed_signature = base64.b64encode(hmac.new(secret_key, received_payload, hashlib.sha256).digest()).decode('utf-8')

    return hmac.compare_digest(computed_signature, received_signature)

@app.route('/your/endpoint', methods=['POST'])
def your_endpoint():
    if verify_hmac_signature(request):
        # HMAC signature is valid, proceed with your API logic
        return jsonify({'message': 'Your API endpoint logic here'})
    else:
        # HMAC signature is invalid, reject the request
        return jsonify({'error': 'Invalid HMAC signature'}), 401
