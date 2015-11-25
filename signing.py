"""
<Program Name>
  signing.py

<Author>
  Casey McGinley
  Fernando Maymi
  Catherine Eng
  Justin Valcarel
  Wilson Li

<Started>
  November 22, 2015

<Copyright>
  See LICENSE for licensing information.

<Purpose>
  To sign and verify the metadata.
"""

import tuf
import tuf.keys
import tuf.sig
import tuf.util


def print_object(obj_desc, object):
  # Return on prints, potentially remove this function
  #return
  verbose = 0
  if (verbose != 0):
  	return
  print obj_desc + "\n==============================\n" 
  print object
  print "\n==============================\n" 





def sign_json(orig_data):
  """
  <Purpose>
    Return a dictionary of the original data with
    the added fields 'signed' and 'signatures'.

    'signed' will contain a dictionary of the form:
    {'keytype': 'rsa',
     'keyid': keyid,
     'keyval': {'public': '-----BEGIN RSA PUBLIC KEY----- ...',
                'private': ''}}

    Note that the private key will be cleared in the resulting dictionary.

    'signatures' will contain a dictionary of the form:
    {'keyid': 'f30a0870d026980100c0573bd557394f8c1bbd6...',
     'method': '...',
     'sig': '...'}.

    The signing process will use the generated RSA keys 
    and the data to generate the signature.

  <Arguments>
    orig_data:
      Data object used to generate the signature.

  <Exceptions>
    tuf.FormatError, if 'rsakey_dict' does not have the correct format.

    tuf.UnsupportedLibraryError, if an unsupported or unavailable library is
    detected.

    TypeError, if a private key is not defined for 'rsakey_dict'.

  <Side Effects>
    A 'keys.txt' file containing the encrypted RSA keys will be created.

  <Returns>
    A dictionary containing the original data with the addition
    of the 'signed' and 'signatures' fields.
  """

  # Create a copy to prevent modifying original data.
  data = orig_data.copy()

  # Use generated RSA keys to create signature.
  rsakey_dict = tuf.keys.generate_rsa_key()
  rsa_signature = tuf.sig.generate_rsa_signature(data, rsakey_dict)

  # The RSA keys need to be encrypted before it is stored locally
  encrypted_keys = tuf.keys.encrypt_key(rsakey_dict, "badpassword")
  fileobj = open('keys.txt', 'w')
  fileobj.write(encrypted_keys)
  fileobj.close()

  # Update metadata with public key and signature.
  rsakey_dict['keyval']['private'] = ''
  data['signed'] = rsakey_dict
  data['signatures'] = rsa_signature

  return data





def verify_json(data):
  """
  <Purpose>
    Determine whether the private key belonging to 'key_dict' produced
    'signatures' in 'data'. 
    
    The public key found in 'key_dict', the 'method' and 'sig' objects 
    contained in 'signatures' of 'data', and the other metadata in 'data' 
    will be used to complete the verification.

  <Arguments>
    data:
      A dictionary containing the metadata with the
      'signed' and 'signatures' fields.

  <Exceptions>
    tuf.FormatError, raised if either 'signed' or 'signatures' fields
    in 'data' are improperly formatted.
    
    tuf.UnsupportedLibraryError, if an unsupported or unavailable library is
    detected.
    
    tuf.UnknownMethodError.  Raised if the signing method used by
    'signatures' field in 'data' is not one supported.

  <Side Effects>
    None.

  <Returns>
    Boolean. True if the signature is legitimate for the data.
    False otherwise.  
  """

  # Create a copy to prevent modifying original data.
  canonicalData = data.copy()

  # Decrypt the locally stored encrypted keys to use for verification.
  fileobj = open('keys.txt', 'r')
  encrypted_key = fileobj.read()
  key_dict = tuf.keys.decrypt_key(encrypted_key, "badpassword")
  fileobj.close()

  # Verification on metadata needs to be in canonical JSON,
  # and have the 'signed' and 'signatures' key-value pairs removed. 
  del canonicalData['signed']
  del canonicalData['signatures']
  canonicalData = tuf.formats.encode_canonical(canonicalData)
  #verify_state = tuf.keys.verify_signature(data['signed'], data['signatures'], canonicalData)
  verify_state = tuf.keys.verify_signature(key_dict, data['signatures'], canonicalData)

  return verify_state





def run_test1():
  # Setup for dictionary and sign json 
  data = {'Name': 'Zara', 'Age': 7, 'Class': 'First'}
  retdata = sign_json(data)

  # GOOD DATA - testing verify_json
  print "Good Test:  "
  print verify_json(retdata)

  # BAD DATA - testing verify_json
  print "Bad Test:  "
  xdata = retdata
  xdata['Name'] = 'FakeName'
  print verify_json(xdata)