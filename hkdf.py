from __future__ import division

import hmac
import hashlib
import sys

if sys.version_info[0] == 3:
	buffer = lambda x: x

def hkdf_extract(salt, input_key_material, hash=hashlib.sha512):
	'''
	Extract a pseudorandom key suitable for use with hkdf_expand
	from the input_key_material and a salt using HMAC with the
	provided hash (default SHA-512).

	salt should be a random, application-specific byte string. If
	salt is None or the empty string, an all-zeros string of the same
	length as the hash's block size will be used instead per the RFC.

	See the HKDF RFC and paper for usage notes.
	'''
	hash_len = hash().digest_size
	if salt == None or len(salt) == 0:
		salt = bytearray((0,) * hash_len)
	return hmac.new(bytes(salt), buffer(input_key_material), hash).digest()

def hkdf_expand(pseudo_random_key, info=b"", length=32, hash=hashlib.sha512):
	'''
	Expand `pseudo_random_key` and `info` into a key of length `bytes` using
	HKDF's expand function based on HMAC with the provided hash (default
	SHA-512). See the HKDF RFC and paper for usage notes.
	'''
	hash_len = hash().digest_size
	length = int(length)
	if length > 255 * hash_len:
		raise Exception("Cannot expand to more than 255 * %d = %d bytes using the specified hash function" %\
			(hash_len, 255 * hash_len))
	blocks_needed = length // hash_len + (0 if length % hash_len == 0 else 1) # ceil
	okm = b""
	output_block = b""
	for counter in range(blocks_needed):
		output_block = hmac.new(pseudo_random_key, buffer(output_block + info + bytearray((counter + 1,))),\
			hash).digest()
		okm += output_block
	return okm[:length]

class Hkdf(object):
	'''
	Wrapper class for HKDF extract and expand functions
	'''
	def __init__(self, salt, input_key_material, hash=hashlib.sha256):
		'''
		Extract a pseudorandom key from `salt` and `input_key_material` arguments.

		See the HKDF RFC for guidance on setting these values. The constructor
		optionally takes a `hash` arugment defining the hash function use,
		defaulting to hashlib.sha256.
		'''
		self._hash = hash
		self._prk = hkdf_extract(salt, input_key_material, self._hash)
	def expand(self, info=b"", length=32):
		'''
		Generate output key material based on an `info` value

		Arguments:
		- info - context to generate the OKM
		- length - length in bytes of the key to generate

		See the HKDF RFC for guidance.
		'''
		return hkdf_expand(self._prk, info, length, self._hash)
