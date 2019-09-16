# EMUSEREMA Multiprotocol Session and Redirect Manager

## Supported protocols

- SSH
- VNC
- RDP
- General URLs

## Primarily supported clients

- OpenSSH
- RealVNC
- Microsoft Remote Desktop (`mstsc.exe`)
- Any browser capable of running JavaScript (jstree) for generic URL launch

## Secondarily supported clients

- PuTTY and its derivatives
- xfreerdp - FreeRDP X11 client

## TODO

- [ ] Support for inheritance of PuTTY default settings
- [ ] Integrate WSSH better
- [ ] Setup and usage instructions
- [ ] Support OpenSSL as redirect method (for routing cleartext TCP sessions based on SNI header)
- [ ] Support for a general TCP service for use with stunnel / haproxy / socat
- [ ] Support for mosh
