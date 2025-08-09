# FormulaX
The source code of the mobile application "FormelX"

## Installation
- To install the project, first clone it via `git clone https://github.com/PhilippSchoeneberg/FormelX.git`
- Then create a virtual environment using at least python version 3.11
- Finally, install the necessary libraries using `pip install -r requirements.txt`

## Publication
### Android
- Increase numeric version number in the "buildozer.spec" file by 1
- Create Android App Bundle (.aab) using `buildozer android release`
- Rename the file to `formelx-release.aab`
- Sign the file using `jarsigner -verbose -sigalg SHA256withRSA -digestalg SHA-256 -keystore my-release-key.keystore bin/formelx-release.aab my-key-alias`
- Verify the signature using `jarsigner -verify -verbose -certs bin/formelx-release.aab`
- Zipalign the file using `zipalign -v -p 4 bin/formelx-release.aab bin/formelx-release-aligned.aab`
