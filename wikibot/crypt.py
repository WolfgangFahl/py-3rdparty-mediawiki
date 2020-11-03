'''
Created on 25.03.2020

@author: wf
'''
from Crypto.Hash import MD5
from Crypto.Cipher import DES
import base64
import secrets
import string
import os
import warnings

class Crypt(object):
    '''
    Python implementation of PBEWithMD5AndDES
    see
    https://github.com/binsgit/PBEWithMD5AndDES
    and
    https://gist.github.com/rohitshampur/da5f79c34260150aafc1
    
    converted to class
'''
    def __init__(self,cypher,iterations=20,salt=None):
        ''' construct me with the given cypher iterations and salt 
        '''
        # avoid annoying
        #  /opt/local/Library/Frameworks/Python.framework/Versions/3.8/lib/python3.8/site-packages/Crypto/Cipher/blockalgo.py:141: DeprecationWarning: PY_SSIZE_T_CLEAN will be required for '#' formats
        warnings.filterwarnings("ignore", category=DeprecationWarning) 
 
        self.cypher=cypher.encode('utf-8')
        self.iterations=iterations
        if salt is None:
            self.salt=os.urandom(8)
        else:
            self.salt=salt.encode('utf-8')      
        pass
    
    @staticmethod
    def getRandomString(rlen=32):
        #https://docs.python.org/3/library/secrets.html
        alphabet = string.ascii_letters + string.digits
        rstring = ''.join(secrets.choice(alphabet) for i in range(rlen))
        return rstring
    
    @staticmethod
    def getRandomCrypt(cypherLen=32):
        cypher=Crypt.getRandomString(cypherLen)
        salt=Crypt.getRandomString(8)
        crypt=Crypt(cypher,salt=salt)
        return crypt;
    
    def getCrypt(self):
        '''
        get my DES crypt
        '''
        hasher = MD5.new()
        hasher.update(self.cypher)
        hasher.update(self.salt)
        result = hasher.digest()
    
        for i in range(1, self.iterations):
            hasher = MD5.new()
            hasher.update(result)
            result = hasher.digest()
        return DES.new(result[:8], DES.MODE_CBC, result[8:16])
    
    def encrypt(self,msg):
        '''
        encrypt the given message
        '''
        plaintext_to_encrypt = msg
        # Pad plaintext per RFC 2898 Section 6.1
        padding = 8 - len(plaintext_to_encrypt) % 8
        plaintext_to_encrypt += chr(padding) * padding
        encoder = self.getCrypt()
        encrypted = encoder.encrypt(plaintext_to_encrypt)
        b64enc=base64.b64encode(encrypted).decode('utf-8')
        return b64enc

    def decrypt(self,encoded):
        '''
        decrypt the given message 
        '''
        enc = base64.b64decode(encoded)
        decoder = self.getCrypt()
        decryptedb = decoder.decrypt(enc)
        decrypted=decryptedb.decode('utf-8')
        return decrypted.rstrip('\2,\1,\3,\4,\5,\6,\7,\0,\b')
    

if __name__ == "__main__":
    msg = "hello, world"
    cypher = "mycypher"
    c=Crypt(cypher)
    s = c.encrypt(msg)
    print (s)
    d=c.decrypt(s)
    print (d)