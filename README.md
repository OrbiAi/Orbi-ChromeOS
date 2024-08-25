# UNSTABLE, UNSECURE, UNDOCUMENTED, WIP
# Orbi for Chrome OS
## How to use
- Server:
Clone this repository, install the requirements via pip and run both connector.py and main.py
- Client (Chromebook):
> [!IMPORTANT]
> New Chrome versions require HTTPS to screenshare. To bypass this, go to chrome://flags, find #unsafely-treat-insecure-origin-as-secure and set it to http://ip:port. Please note that this will send your screenshots unencrypted.

Navigate to http://server-ip:1337/connector in Chrome, then click the 3 dots at the top right and click on "Save and share", then "Create shortcut". Make sure the name is "Orbi Connector" and "Run in a window" is checked. Do the same for http://server-ip:1337/. Make sure that connector.py is running and start Orbi Connector. It will ask you for permissions to share your screen, allow that. After 75 seconds it should take the first capture, which will be visible in the main Orbi app.
