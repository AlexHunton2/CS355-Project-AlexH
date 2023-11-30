# https://pycryptodome.readthedocs.io/en/latest/src/signature/dsa.html
# https://pycryptodome.readthedocs.io/en/latest/src/public_key/rsa.html

from Crypto.Hash import SHA256
from Crypto.Signature import DSS
from Crypto.PublicKey import ECC
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto import Random


def sign(message, key):
	h = SHA256.new(message)
	signer = DSS.new(key, 'fips-186-3') # priv key
	signature = signer.sign(h)
	return signature

def verify(message : bytes, key, signature):
	h = SHA256.new(message)
	verifier = DSS.new(key, 'fips-186-3') # pub key
	try:
		verifier.verify(h, signature)
		return True
	except ValueError:
		return False

def encrypt(message: bytes, key : RSA.RsaKey):
	rsa_public_key = PKCS1_OAEP.new(key) # pub key
	encrypted_text = rsa_public_key.encrypt(message)
	return encrypted_text

def decrypt(cipher, key : RSA.RsaKey):
	rsa_private_key = PKCS1_OAEP.new(key) # priv key
	decrypted_text = rsa_private_key.decrypt(cipher)
	return decrypted_text

def generateRSAKey():
	random_generator = Random.new().read
	RSA_KEY = RSA.generate(2048, random_generator)
	return RSA_KEY

def generateDSSKey():
	DSS_KEY = ECC.generate(curve='P-256')
	return DSS_KEY


def encrypt_and_sign(message : str, rsa_key, dss_key):
    cipher = encrypt(message.encode(), RSA.importKey(rsa_key))
    signature = sign(cipher, dss_key)
    return [cipher, signature]

def verify_and_decrypt(cipher, rsa_key, dss_key, signature) -> bytes | None:
	if (verify(cipher, dss_key, signature)):
		return decrypt(cipher, RSA.importKey(rsa_key))