unity-scope-everpad
===================

Ubuntu Unity 7 scope search plugin that enables information from [Everpad](https://github.com/nvbn/everpad) to be searched and displayed in the Dash.
As it use Unity 7 API, it is compatible with Ubuntu 13.10+.

Installation
============
Clone repository and build deb package:
```
  git clone https://github.com/SlavikZ/unity-scope-everpad
  cd unity-scope-everpad
  dpkg-buildpackage -b -rfakeroot -uc
```
Install deb package:
```
  cd ..
  sudo dpkg -i unity-scope-everpad_0.0.1_all.deb
```
(Optional) Add everpad scope to master scope list (you may also use dconf-editor GUI tools):
```
dconf write /com/canonical/unity/dash/scopes "['home.scope', 'applications.scope', 'files.scope', 'video.scope', 'music.scope', 'photos.scope', 'social.scope', 'everpad.scope']"
```
Reboot system
