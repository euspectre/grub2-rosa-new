#!/bin/sh

# - Assume grub2 is installed
# - Assume sudo for all commands
# - Note that if you had grub2 installed before addition of the
#   sample theme, it may be easier to get the theme to work in
#   qemu by just running "rpm -e grub2; urpmi grub2" to have it
#   properly configured.

root=`mktemp -d "${TMPDIR:-/tmp}/tmp.XXXXXXXXXX"` || exit 1
mkdir -p $root/boot/grub
sudo cp -fa /boot/grub2/* $root/boot/grub

# make it easy to do some customization tests
if [ ! -f grub.cfg ]; then
    sudo cp /boot/grub2/grub.cfg .
    sudo chown `whoami`:`groups | sed -e 's| .*||'` grub.cfg
fi
perl -pi -e 's|(\s+set gfxpayload=keep)|#$1|;' \
	 -e "s|(set root=).*|\$1'(hd0)'|;" \
	 -e 's|(if loadfont ).*(/share/grub2/unicode.pf2 ; then)|$1/usr$2|;' \
	 -e 's|(/boot/grub)2(/themes)|$1$2|;' \
	 -e 's|(search --no-floppy --fs-uuid.*)|#$1|;' \
	grub.cfg
sudo cp grub.cfg $root/boot/grub

mkdir -p $root/usr/share/grub2
sudo cp -f /usr/share/grub2/*.pf2 $root/usr/share/grub2

# make it easy to do some customization tests
if [ ! -f theme.txt ]; then
    if [ -f /boot/grub2/themes/mandriva/theme.txt ]; then
	sudo cp /boot/grub2/themes/mandriva/theme.txt .
	sudo chown `whoami`:`groups | sed -e 's| .*||'` theme.txt
    else
	cp `dirname $0`/theme.txt .
    fi
fi
sudo cp theme.txt $root/boot/grub/themes/mandriva

sudo grub2-mkrescue -o grub.image $root
sudo chown `whoami`:`groups | sed -e 's| .*||'` theme.txt
qemu grub.image
