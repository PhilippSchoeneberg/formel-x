build-all: build-android

build-android: clean
	#buildozer android release
	mv bin/F bin/FormelX-release.aab
	jarsigner -verbose -sigalg SHA256withRSA -digestalg SHA-256 -keystore my-release-key.keystore bin/FormelX-release.aab my-key-alias
	jarsigner -verify -verbose -certs bin/FormelX-release.aab
	zipalign -v -p 4 bin/FormelX-release.aab bin/FormelX-release-aligned.aab

clean:
	rm -fr bin/
