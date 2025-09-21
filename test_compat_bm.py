#!/usr/bin/env python3
# test_libressl_compat.py

import ctypes
import sys
import os
from ctypes.util import find_library

def test_libressl_compatibility(lib_path):
    """
    Comprehensive test for LibreSSL compatibility with PyBitmessage
    """
    print(f"\n=== Testing LibreSSL library: {lib_path} ===")
    
    if not os.path.exists(lib_path):
        print(f"✗ Library not found: {lib_path}")
        return False
    
    try:
        # Load the library
        openssl = ctypes.CDLL(lib_path)
        print("✓ Library loaded successfully")
        
        # Test version functions
        version_func = None
        version = None
        
        # Try OpenSSL 1.1+ version function first
        try:
            openssl.OpenSSL_version.argtypes = [ctypes.c_int]
            openssl.OpenSSL_version.restype = ctypes.c_char_p
            version = openssl.OpenSSL_version(0)  # OPENSSL_VERSION
            version_func = "OpenSSL_version"
            print(f"✓ OpenSSL_version function found")
        except AttributeError:
            # Fall back to OpenSSL 1.0 version function
            try:
                openssl.SSLeay_version.restype = ctypes.c_char_p
                openssl.SSLeay_version.argtypes = [ctypes.c_int]
                version = openssl.SSLeay_version(0)  # SSLEAY_VERSION
                version_func = "SSLeay_version"
                print(f"✓ SSLeay_version function found")
            except AttributeError:
                print("✗ No version function found")
                return False
        
        if version:
            print(f"Library version: {version.decode()}")
        
        # Test essential functions that PyBitmessage uses
        essential_functions = [
            # Basic SSL functions
            'SSL_new', 'SSL_free', 'SSL_accept', 'SSL_connect',
            'SSL_read', 'SSL_write', 'SSL_shutdown',
            
            # Crypto functions
            'RAND_bytes', 'BN_new', 'BN_free', 'BN_bn2bin', 'BN_bin2bn',
            'EC_KEY_new_by_curve_name', 'EC_KEY_free', 'EC_KEY_generate_key',
            'EVP_aes_256_cfb128', 'EVP_aes_128_cfb128',
            'EVP_CIPHER_CTX_new', 'EVP_CIPHER_CTX_free',
            'EVP_CipherInit_ex', 'EVP_CipherUpdate', 'EVP_CipherFinal_ex',
            
            # ECC functions
            'EC_GROUP_new_by_curve_name', 'EC_POINT_new', 'EC_POINT_free',
            'ECDSA_sign', 'ECDSA_verify', 'ECDH_compute_key',
            
            # Digest functions
            'EVP_sha256', 'EVP_sha512', 'EVP_sha1', 'HMAC',
            
            # Key functions
            'EC_KEY_get0_private_key', 'EC_KEY_get0_public_key',
            'EC_KEY_set_private_key', 'EC_KEY_set_public_key',
        ]
        
        missing_functions = []
        available_functions = []
        
        for func_name in essential_functions:
            try:
                func = getattr(openssl, func_name)
                available_functions.append(func_name)
                print(f"✓ {func_name} found")
            except AttributeError:
                missing_functions.append(func_name)
                print(f"✗ {func_name} missing")
        
        # Test curve support (secp256k1 is essential for Bitcoin/Bitmessage)
        try:
            openssl.EC_KEY_new_by_curve_name.restype = ctypes.c_void_p
            openssl.EC_KEY_new_by_curve_name.argtypes = [ctypes.c_int]
            
            # Test secp256k1 curve (NID_secp256k1 = 714)
            key = openssl.EC_KEY_new_by_curve_name(714)
            if key:
                openssl.EC_KEY_free(key)
                print("✓ secp256k1 curve support available")
            else:
                print("✗ secp256k1 curve not supported")
                missing_functions.append("secp256k1_curve")
        except Exception as e:
            print(f"✗ Curve test failed: {e}")
            missing_functions.append("curve_test")
        
        # Test random number generation
        try:
            openssl.RAND_bytes.restype = ctypes.c_int
            openssl.RAND_bytes.argtypes = [ctypes.c_void_p, ctypes.c_int]
            
            buffer = ctypes.create_string_buffer(32)
            result = openssl.RAND_bytes(buffer, 32)
            if result == 1:
                print("✓ RAND_bytes works correctly")
            else:
                print("✗ RAND_bytes failed")
                missing_functions.append("RAND_bytes")
        except Exception as e:
            print(f"✗ RAND_bytes test failed: {e}")
            missing_functions.append("RAND_bytes")
        
        # Summary
        print(f"\n=== SUMMARY ===")
        print(f"Available functions: {len(available_functions)}/{len(essential_functions)}")
        print(f"Missing functions: {len(missing_functions)}")
        
        if missing_functions:
            print("Missing critical functions:")
            for func in missing_functions[:10]:  # Show first 10 missing
                print(f"  - {func}")
            if len(missing_functions) > 10:
                print(f"  ... and {len(missing_functions) - 10} more")
        
        # Compatibility assessment
        if len(missing_functions) < 5:  # Allow for some missing non-critical functions
            print("✓ Library appears to be compatible with PyBitmessage")
            return True
        else:
            print("✗ Library may not be fully compatible with PyBitmessage")
            return False
            
    except Exception as e:
        print(f"✗ Failed to load or test library: {e}")
        return False

def main():
    """Test all potential LibreSSL libraries on OpenBSD"""
    print("Testing LibreSSL compatibility for PyBitmessage")
    
    test_libraries = [
        # Your compiled version - highest priority
        "/home/libressl-2.5.0/build/ssl/libssl.so",
        "/home/libressl-2.5.0/build/crypto/libcrypto.so",
        
        # System libraries
        "/usr/lib/libssl.so",
        "/usr/lib/libcrypto.so",
        "/usr/local/lib/libssl.so",
        "/usr/local/lib/libcrypto.so",
        
        # Versioned libraries
        "/usr/lib/libssl.so.26.0",
        "/usr/lib/libcrypto.so.26.0",
        "/usr/lib/libssl.so.25.0",
        "/usr/lib/libcrypto.so.25.0",
    ]
    
    compatible_libs = []
    
    for lib_path in test_libraries:
        if test_libressl_compatibility(lib_path):
            compatible_libs.append(lib_path)
    
    print(f"\n=== FINAL RESULTS ===")
    if compatible_libs:
        print("Compatible libraries found:")
        for lib in compatible_libs:
            print(f"  ✓ {lib}")
    else:
        print("No compatible libraries found!")
        print("You may need to:")
        print("  1. Install LibreSSL: pkg_add libressl")
        print("  2. Compile a compatible version of LibreSSL")
        print("  3. Check library paths and permissions")

if __name__ == "__main__":
    main()
