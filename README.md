# libressl-2.5.0 (should)similar to OpenSSL 1.0.2k
https://ftp.openbsd.org/pub/OpenBSD/LibreSSL/
# experimental for pybitmessage on linux and bsd:
for comparison with libressl 2.7.0 (old-openssl 1.1.0)
# install
### rm /usr/bin/openssl
### cd /libressl-2.5.0
### mkdir build
### cd build
### cmake ..
### make
### make test
### sudo make install
## pybitmessage+++set libcrypto.so +++ libssl.so +++ at openssl.py+++libdir.append("/path/libssl.so")+++libdir.append("/path/libcrypto.so")
