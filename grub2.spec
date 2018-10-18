%define libdir32 %{_exec_prefix}/lib
%define platform pc
%define efi 1

%global efi %{ix86} x86_64

# Do not build HTML and PDF documentation by default.
%bcond_with	doc
%bcond_with	pdf

Summary:	GRUB is a boot loader
Name:		grub2
Version:	2.02
Release:	1
License:	GPLv3+
Group:		System/Kernel and hardware
Url:		http://www.gnu.org/software/grub/
Source0:	ftp://ftp.gnu.org/gnu/grub/grub-%{version}.tar.xz
Source2:	grub.default
Source8:	grub2-po-update.tar.gz
Source9:	update-grub2
Source11:	grub2.rpmlintrc

# Upstream patches. Keep them first to simplify future rebases.
Patch1:		01-strtoull-Fix-behaviour-on-chars-between-9-and-a.patch
Patch2:		02-Allow-GRUB-to-mount-ext2-3-4-filesystems-that-have-t.patch
Patch4:		04-crypto-Fix-use-after-free.patch
Patch5:		05-Fix-a-segfault-in-lsefi.patch
Patch6:		06-udf-Fix-reading-label-lvd.ident-is-dstring.patch
Patch7:		07-xfs-Don-t-attempt-to-iterate-over-empty-directory.patch
Patch8:		08-Make-grub-install-check-for-errors-from-efibootmgr.patch
Patch9:		09-x86-64-Treat-R_X86_64_PLT32-as-R_X86_64_PC32.patch
Patch10:	10-Fix-packed-not-aligned-error-on-GCC-8.patch
Patch11:	11-fs-Add-F2FS-support.patch
Patch12:	12-grub-probe-Don-t-skip-dev-mapper-dm-devices.patch
Patch13:	13-xfs-Accept-filesystem-with-sparse-inodes.patch
Patch14:	14-efi-console-Fix-the-enter-key-not-working-on-x86-tab.patch
Patch15:	15-i386-linux-Add-support-for-ext_lfb_base.patch
Patch16:	16-ahci-Increase-time-out-from-10-s-to-32-s.patch
Patch17:	17-tsc-Change-default-tsc-calibration-method-to-pmtimer.patch
Patch18:	18-yylex-Explicilty-cast-fprintf-to-void.patch
Patch19:	19-bufio-Round-up-block-size-to-power-of-2.patch
Patch22:	22-python-Use-AM_PATH_PYTHON-to-determine-interpreter-f.patch
Patch23:	23-osdep-linux-Convert-partition-start-to-disk-sector-l.patch
Patch24:	24-msdos-Fix-overflow-in-converting-partition-start-and.patch

# Patches from RHEL, Fedora and Ubuntu
Patch501:	501-Don-t-say-GNU-Linux-in-generated-menus.patch
Patch502:	502-fix-http-crash.patch
Patch503:	503-no-insmod-on-sb.patch
Patch520:	520-Add-support-for-linuxefi.patch
Patch521:	521-Use-linuxefi-and-initrdefi-where-appropriate.patch
Patch522:	522-Add-support-for-UEFI-operating-systems-returned-by-o.patch
Patch523:	523-Honor-a-symlink-when-generating-configuration-by-gru.patch
Patch524:	524-Fix-race-in-EFI-validation.patch
Patch525:	525-Use-device-part-of-chainloader-target-if-present.patch
Patch526:	526-Add-secureboot-support-on-efi-chainloader.patch
Patch527:	527-Make-any-of-the-loaders-that-link-in-efi-mode-honor-.patch
Patch528:	528-Rework-linux-command.patch
Patch529:	529-Rework-linux16-command.patch
Patch530:	530-Re-work-some-intricacies-of-PE-loading.patch
# Part of "Load arm with SB enabled" which affects x86 as well and is needed
# for subsequent patches.
Patch531:	531-Move-grub_efi_linux_boot-into-a-separate-file.patch
Patch532:	532-Rework-even-more-of-efi-chainload-so-non-sb-cases-wo.patch
Patch533:	533-linuxefi-fix-double-free-on-verification-failure.patch
Patch534:	534-efi-chainloader-fix-wrong-sanity-check-in-relocate_c.patch
Patch535:	535-efi-chainloader-truncate-overlong-relocation-section.patch
Patch536:	536-linuxefi-minor-cleanups.patch
Patch537:	537-Handle-multi-arch-64-on-32-boot-in-linuxefi-loader.patch
Patch538:	538-Clean-up-some-errors-in-the-linuxefi-loader.patch
Patch539:	539-Fix-one-more-coverity-complaint.patch
Patch560:	560-Don-t-write-messages-to-the-screen.patch
Patch561:	561-Don-t-print-GNU-GRUB-header.patch
Patch562:	562-Don-t-add-to-highlighted-row.patch
Patch563:	563-Message-string-cleanups.patch
Patch564:	564-Fix-border-spacing-now-that-we-aren-t-displaying-it.patch
Patch565:	565-Use-the-correct-indentation-for-the-term-help-text.patch
Patch566:	566-Indent-menu-entries.patch
Patch567:	567-Fix-margins.patch
Patch568:	568-Use-2-instead-of-1-for-our-right-hand-margin-so-line.patch
Patch569:	569-Don-t-draw-a-border-around-the-menu.patch
Patch570:	570-Use-the-standard-margin-for-the-timeout-string.patch

# Patches from Virtuozzo/VZLinux (some are reworked and updated variants
# of the patches used in ROSA before)
Patch1002:	vl-1002-gfx-terminal-background.patch
Patch1003:	vl-1003-gfx-cut-long-titles-using-ellipsis.patch
Patch1004:	vl-1004-Support-showing-UEFI-logo-when-booting-in-UEFI.patch

# ROSA-specific patches
Patch2001:	grub2-read-cfg.patch
Patch2002:	grub2-unifont-path.patch
Patch2003:	grub2-improved-boot-menu.patch
Patch2004:	grub2-30_os-prober-loading-messages.patch
Patch2005:	grub2-Install-signed-images-if-UEFI-Secure-Boot-is-enabled.patch
Patch2006:	grub2-support-grub.cfg-links.patch
Patch2007:	grub2-10_linux_hibernate_fix.patch
Patch2008:	grub2-make-sure-configure-finds-DejaVu-fonts.patch

BuildRequires:	autogen
BuildRequires:	automake
BuildRequires:	bison
BuildRequires:	binutils
BuildRequires:	flex
BuildRequires:	fonts-ttf-unifont >= 6.2
# DejaVu fonts can be used by some themes.
BuildRequires:	fonts-ttf-dejavu
BuildRequires:	help2man
BuildRequires:	texinfo
%if %{with pdf}
BuildRequires:	texlive-collection-texinfo
BuildRequires:	texlive-epsf
BuildRequires:	texlive-latex
%endif
BuildRequires:	glibc-static-devel
BuildRequires:	liblzo-devel
BuildRequires:	bzip2-devel
BuildRequires:	pkgconfig(devmapper)
BuildRequires:	pkgconfig(freetype2)
BuildRequires:	pkgconfig(liblzma)
BuildRequires:	pkgconfig(libusb)
BuildRequires:	pkgconfig(ncurses)
BuildRequires:	pkgconfig(fuse)

Requires:	grub2-theme
Requires:	xorriso
Requires(post):	os-prober >= 1.74
Requires:	e2fsprogs >= 1.42.13
# Some of the scripts from /etc/grub.d/ may use perl.
Requires:	perl
Suggests:	grub2-theme-rosa

Provides:	bootloader
Provides:	grub2bootloader

%description
GRUB is a highly configurable and customizable boot loader with modular
architecture.  It supports a rich variety of kernel formats, file systems,
computer architectures and hardware devices.

%files -f pc/grub.lang
%{libdir32}/grub/*-%{platform}
%{_sbindir}/update-grub2
%{_bindir}/%{name}-editenv
%{_bindir}/%{name}-file
%{_bindir}/%{name}-fstest
%{_bindir}/%{name}-glue-efi
%{_bindir}/%{name}-kbdcomp
%{_bindir}/%{name}-menulst2cfg
%{_bindir}/%{name}-mkfont
%{_bindir}/%{name}-mkimage
%{_bindir}/%{name}-mklayout
%{_bindir}/%{name}-mknetdir
%{_bindir}/%{name}-mkpasswd-pbkdf2
%{_bindir}/%{name}-mkrelpath
%{_bindir}/%{name}-mkrescue
%{_bindir}/%{name}-mkstandalone
%{_bindir}/%{name}-mount
%{_bindir}/%{name}-render-label
%{_bindir}/%{name}-script-check
%{_bindir}/%{name}-syslinux2cfg
%{_sbindir}/%{name}-bios-setup
%{_sbindir}/%{name}-install
%{_sbindir}/%{name}-macbless
%{_sbindir}/%{name}-mkconfig
%{_sbindir}/%{name}-ofpathname
%{_sbindir}/%{name}-probe
%{_sbindir}/%{name}-reboot
%{_sbindir}/%{name}-set-default
%{_sbindir}/%{name}-sparc64-setup
%{_datadir}/grub
%attr(0700,root,root) %dir %{_sysconfdir}/grub.d
%{_sysconfdir}/grub.d/README
%config %{_sysconfdir}/grub.d/??_*
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/default/grub
%{_sysconfdir}/bash_completion.d/grub
%dir /boot/%{name}
%dir /boot/%{name}/locale
%if %{with doc}
%doc %{_docdir}/%{name}
%endif
%{_infodir}/%{name}.info*
%{_infodir}/grub-dev.info*
%{_mandir}/*/%{name}-*
%exclude %{_mandir}/*/%{name}-efi-*
# RPM filetriggers
%{_filetriggers_dir}/%{name}.*
%dir /boot/%{name}/fonts
/boot/%{name}/fonts/unicode.pf2

%post
exec >/dev/null 2>&1
# Create device.map or reuse one from GRUB Legacy
cp -u /boot/grub/device.map /boot/%{name}/device.map 2>/dev/null ||
	%{_sbindir}/%{name}-mkdevicemap
#bugfix: error message before loading of grub2 menu on boot
cp -f /boot/grub2/locale/en@quot.mo /boot/grub2/locale/en.mo

%preun
exec >/dev/null
if [ $1 = 0 ]; then
    # XXX Ugly
    rm -f /boot/%{name}/*.mod
    rm -f /boot/%{name}/*.img
    rm -f /boot/%{name}/*.lst
    rm -f /boot/%{name}/*.o
    rm -f /boot/%{name}/device.map
fi

%posttrans
# grub2 package can be installed either standalone (on the systems with
# legacy BIOS) and as a dependency for grub2-efi* (on UEFI systems).
# In the latter case, that package is responsible for the installation
# of the boot loader and for updating of /boot/grub2/grub.cfg.
# grub2 package should not do it.
if [ ! -d /sys/firmware/efi ]; then
	# Determine the partition with /boot
	BOOT_PARTITION=$(df -h /boot | (read; awk '{print $1; exit}'|sed 's/[[:digit:]]*$//'))
	# (Re-)Generate core.img, but don't let it be installed in boot sector
	%{_sbindir}/%{name}-install $BOOT_PARTITION
	# Regenerate configure on install or update
	%{_sbindir}/update-grub2
fi
#-----------------------------------------------------------------------

%ifarch %{efi}
%package efi-common
Summary:	GRUB for EFI systems
Group:		System/Kernel and hardware
Suggests:	efibootmgr
# TODO: require efibootmgr >= 16: needed to support dual-boot and such.

%description efi-common
The GRand Unified Bootloader (GRUB) is a highly configurable and customizable
bootloader with modular architecture.

It support rich variety of kernel formats, file systems, computer 
architectures and hardware devices.

This package contains provides tools and settings needed to support EFI
systems but does not install GRUB binaries into /boot/efi/EFI/rosa/. This is
because signed binaries from "grub-efi" package should go there.

This package, in turn, contains unsigned GRUB binaries, in
%{_datadir}/grub2-efi/. If a user wants to use them they need to copy these
images into /boot/efi/EFI/rosa/ manually, sign them if required, etc.

%files efi-common
/etc/bash_completion.d/grub-efi
%{libdir32}/grub/%{_arch}-efi/
%{_sbindir}/%{name}-efi*
%{_bindir}/%{name}-efi*
%{_mandir}/*/%{name}-efi-*
%dir %{_datadir}/%{name}-efi
%{_datadir}/%{name}-efi/*.efi
%endif

#-----------------------------------------------------------------------

%prep
%setup -q -n grub-%{version}
%apply_patches

sed -ri -e 's/-Werror//g' configure.ac
sed -ri -e 's/-Werror //g' grub-core/Makefile.am

autoreconf -fvi

tar -xf %{SOURCE8}
pushd po-update; sh ./update.sh; popd

%build

export CONFIGURE_TOP="$PWD"
%ifarch %{efi}
mkdir -p efi
pushd efi
%configure2_5x \
	CFLAGS="" \
	TARGET_LDFLAGS=-static \
	--with-platform=efi \
	--program-transform-name=s,grub,%{name}-efi, \
	--libdir=%{libdir32} \
	--libexecdir=%{libdir32} \
	--with-grubdir=grub2 \
	--disable-werror \
	--enable-grub-mkfont
%make all

%if %{with doc}
make html
%endif
%if %{with pdf}
make pdf
%endif
%ifarch %{ix86}
%define grubefiarch i386-efi
%else
%define grubefiarch %{_arch}-efi
%endif

COMMON_MODULES="
	all_video appleldr boot btrfs cat chain configfile echo
	efifwsetup efi_gop efi_uga ext2 fat font gettext
	gfxmenu gfxterm gfxterm_background
	gzio halt hfsplus jpeg keystatus linux linuxefi loadbios loadenv
	loopback lsefi  lsefimmap lsefisystab lssal lvm mdraid09 mdraid1x
	memdisk minicmd normal part_apple part_gpt part_msdos png
	raid5rec raid6rec reboot reiserfs search
	search_fs_file search_fs_uuid search_label sleep squash4 test
	true video xfs
"
./grub-mkimage -O %{grubefiarch} -p /EFI/rosa -o grub.efi -d grub-core ${COMMON_MODULES}
./grub-mkimage -O %{grubefiarch} -p /BOOT/EFI -o grubcd.efi -d grub-core ${COMMON_MODULES} iso9660

popd
%endif

mkdir -p pc
pushd pc
%configure2_5x \
	CFLAGS="" \
	TARGET_LDFLAGS=-static \
	--with-platform=pc \
    %ifarch x86_64
	--enable-efiemu \
    %endif
	--program-transform-name=s,grub,%{name}, \
	--libdir=%{libdir32} \
	--libexecdir=%{libdir32} \
	--with-grubdir=grub2 \
	--disable-werror \
	--enable-grub-mkfont
%make all

%if %{with doc}
make html
%endif
%if %{with pdf}
make pdf
%endif

popd

%install
%ifarch %{efi}
cd efi
%makeinstall_std
%if %{with doc}
%makeinstall_std -C docs install-html
%endif
%if %{with pdf}
%makeinstall_std -C docs install-pdf
%endif
mv %{buildroot}%{_infodir}/grub.info %{buildroot}%{_infodir}/grub2.info
mv %{buildroot}/etc/bash_completion.d/grub %{buildroot}/etc/bash_completion.d/grub-efi

# Install ELF files modules and images were created from into
# the shadow root, where debuginfo generator will grab them from
find %{buildroot} -name '*.mod' -o -name '*.img' |
while read MODULE
do
        BASE=$(echo $MODULE |sed -r "s,.*/([^/]*)\.(mod|img),\1,")
        # Symbols from .img files are in .exec files, while .mod
        # modules store symbols in .elf. This is just because we
        # have both boot.img and boot.mod ...
        EXT=$(echo $MODULE |grep -q '.mod' && echo '.elf' || echo '.exec')
        TGT=$(echo $MODULE |sed "s,%{buildroot},.debugroot,")
#        install -m 755 -D $BASE$EXT $TGT
done

install -d %{buildroot}/%{_datadir}/%{name}-efi/
install -m 755 grub.efi %{buildroot}%{_datadir}/%{name}-efi/
install -m 755 grubcd.efi %{buildroot}%{_datadir}/%{name}-efi/

cd ..
%endif
cd pc
######EFI
%makeinstall_std
%if %{with doc}
%makeinstall_std -C docs install-html
mv -f %{buildroot}%{_docdir}/grub %{buildroot}%{_docdir}/%{name}
%endif
%if %{with pdf}
%makeinstall_std -C docs install-pdf
%endif

# (bor) grub.info is harcoded in sources
mv %{buildroot}%{_infodir}/grub.info %{buildroot}%{_infodir}/grub2.info

install -d %{buildroot}/boot/%{name}
install -d %{buildroot}/boot/%{name}/locale

# Install ELF files modules and images were created from into
# the shadow root, where debuginfo generator will grab them from
find %{buildroot} -name '*.mod' -o -name '*.img' |
while read MODULE
do
        BASE=$(echo $MODULE |sed -r "s,.*/([^/]*)\.(mod|img),\1,")
        # Symbols from .img files are in .exec files, while .mod
        # modules store symbols in .elf. This is just because we
        # have both boot.img and boot.mod ...
        EXT=$(echo $MODULE |grep -q '.mod' && echo '.elf' || echo '.exec')
        TGT=$(echo $MODULE |sed "s,%{buildroot},.debugroot,")
done
# Defaults
install -m 644 -D %{SOURCE2} %{buildroot}%{_sysconfdir}/default/grub

#Add more useful update-grub2 script
install -m 755 -D %{SOURCE9} %{buildroot}%{_sbindir}

# Install filetriggers to update grub.cfg on kernel add or remove
install -d %{buildroot}%{_filetriggers_dir}
pushd %{buildroot}%{_filetriggers_dir} && {
	cat > %{name}.filter << EOF
^./boot/vmlinuz-
EOF
	cat > %{name}.script << EOF
#!/bin/sh
%{_sbindir}/update-grub2
EOF
	chmod 0755 %{name}.script
	popd
}

%find_lang grub

#Copy font to properly place
mkdir -p %{buildroot}/boot/%{name}/fonts/
cp -f %{buildroot}%{_datadir}/grub/unicode.pf2 %{buildroot}/boot/%{name}/fonts/
