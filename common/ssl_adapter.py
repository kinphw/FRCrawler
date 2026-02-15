import ssl
import requests
from requests.adapters import HTTPAdapter
from urllib3.poolmanager import PoolManager
from urllib3.util.ssl_ import create_urllib3_context

class LegacySSLAdapter(HTTPAdapter):
    """
    SSL Adapter to handle legacy SSL/TLS versions and ciphers.
    Useful for sites that use older security standards (e.g., some government sites).
    """
    def init_poolmanager(self, connections, maxsize, block=False, **pool_kwargs):
        context = create_urllib3_context()
        context.load_default_certs()
        
        # Critical for OpenSSL 3+ to work with legacy servers
        # This allows 1024-bit keys and older ciphers
        try:
            context.set_ciphers('DEFAULT@SECLEVEL=1')
        except Exception:
            pass

        self.poolmanager = PoolManager(
            num_pools=connections,
            maxsize=maxsize,
            block=block,
            ssl_context=context,
            **pool_kwargs
        )

def get_legacy_session(pool_maxsize=10):
    """Returns a requests Session with the LegacySSLAdapter mounted."""
    session = requests.Session()
    adapter = LegacySSLAdapter(pool_maxsize=pool_maxsize)
    session.mount('https://', adapter)
    return session
