build-all: build-android

build-android: clean
	buildozer android release
	mv bin/*.aab bin/formelx-release.aab
	jarsigner -verbose -sigalg SHA256withRSA -digestalg SHA-256 -keystore my-release-key.keystore bin/formelx-release.aab my-key-alias
	jarsigner -verify -verbose -certs bin/formelx-release.aab
	zipalign -v -p 4 bin/formelx-release.aab bin/formelx-release-aligned.aab

clean:
	rm -fr bin/
