# FormulaX
The source code of the mobile application "FormulaX".

## Installation
- To install the project first clone it via `git clone https://github.com/PhilippSchoeneberg/FormulaX.git`
- Then install all submodules via `git submodule update --init --recursive`
- After that rename the installed repository "KivyMd" to something else.
- Next copy the package "kivymd" from the renamed repository into the folder "ext" .
- Finally delete the original repository as well as the newly shown "init.py".

## Publication
### Android
- Increase version number in the "buildozer.spec" file by 1
- Create Android App Bundle (.aab) using `buildozer android release`
- Rename the file to `FormulaX-release.aab`
- Sign the file using `jarsigner -verbose -sigalg SHA256withRSA -digestalg SHA-256 -keystore my-release-key.keystore bin/FormulaX-release.aab my-key-alias`
- Verify the signature using `jarsigner -verify -verbose -certs bin/FormulaX-release.aab`
- Zipalign the file using `zipalign -v -p 4 bin/FormulaX-release.aab bin/FormulaX-release-aligned.aab`
