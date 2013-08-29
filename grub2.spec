%define		libdir32	%{_exec_prefix}/lib
%define platform pc
%define efi 1
#%define		unifont		%(echo %{_datadir}/fonts/TTF/unifont/unifont-*.ttf)

%global efi %{ix86} x86_64

%bcond_with	talpo

Name:		grub2
Version:	2.00
Release:	22
Summary:	GNU GRUB is a Multiboot boot loader

Group:		System/Kernel and hardware
License:	GPLv3+
URL:		http://www.gnu.org/software/grub/
Source0:	grub-%{version}.tar.gz
Source1:	90_persistent
Source2:	grub.default
Source3:	grub.melt
# www.4shared.com/archive/lFCl6wxL/grub_guidetar.html
Source4:	grub_guide.tar.gz
Source5:	DroidSansMonoLicense.txt
Source6:	DroidSansMono.ttf
Source7:	rosa-theme.tar.gz
Source8:	grub2-po-update.tar.gz
Source9:	update-grub2
Source10:	README.urpmi
Source11:	grub2.rpmlintrc
Source12:	42_efi

Patch0:		grub2-locales.patch
Patch1:		grub2-00_header.patch
Patch2:		grub2-custom-color.patch
Patch3:		grub2-move-terminal.patch
Patch4:		grub2-read-cfg.patch
Patch5:		grub2-symlink-is-garbage.patch
Patch6:		grub2-name-corrections.patch
Patch7:		grub2-10_linux.patch
Patch8:		grub2-theme-not_selected_item_box.patch
Patch9:         grub-2.00.Linux.remove.patch
Patch10:	grub2-mkfont-fix.patch
Patch11:	grub2-2.00-class-via-os-prober.patch

# Fedora patches:
# https://bugzilla.redhat.com/show_bug.cgi?id=857936
# Patch100:		grub2-2.00-fda-add-fw_path-search_v2.patch
# Add support for entering the firmware setup screen.
# Patch101:		grub2-2.00-fda-Add-fwsetup.patch
# Don't decrease efi memory map size
# Patch102:		grub2-2.00-fda-dont-decrease-mmap-size.patch
# IBM client architecture (CAS) reboot support
# Patch103:		grub2-2.00-fda-cas-reboot-support.patch
# Read chunks in smaller blocks
# Patch104:		grub2-2.00-fda-efidisk-ahci-workaround.patch
# Fix crash on http: https://bugzilla.redhat.com/show_bug.cgi?id=860834
# Patch105:		grub2-2.00-fda-fix-http-crash.patch
# Issue separate DNS queries for ipv4 and ipv6
# Patch106:		grub2-2.00-fda-Issue-separate-DNS-queries-for-ipv4-and-ipv6.patch
# Don't allow insmod when secure boot is enabled
# Patch107:		grub2-2.00-fda-no-insmod-on-sb.patch
# Add support for crappy cd craparino
# Patch108:		grub2-2.00-fda-cdpath.patch
# Add support for linuxefi
# Patch109:	grub2-2.00-fda-linuxefi.patch
# Use "linuxefi" and "initrdefi" where appropriate
# Patch110:	grub2-2.00-fda-use-linuxefi.patch
# Fix parallel build
# Patch111:	grub2-2.00-parallel-build.patch
# Add new command lsefi
# Patch112:	grub2-2.00-fda-new-command-lsefi.patch

#Mageia patches
# Fix autoreconf warnings
Patch200:	grub2-2.00-mga-fix_AM_PROG_MKDIR_P-configure.ac.patch

BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

BuildRequires:	bison
BuildRequires:	flex
BuildRequires:	ruby
#BuildRequires:	fonts-ttf-unifont
BuildRequires:	freetype2-devel
BuildRequires:	glibc-static-devel
BuildRequires:	help2man
BuildRequires:	liblzma-devel
BuildRequires:	liblzo-devel
BuildRequires:	libusb-devel
BuildRequires:	ncurses-devel
BuildRequires:	texlive
#BuildRequires:	texlive-texinfo
BuildRequires:	texinfo
BuildRequires:	pkgconfig(devmapper)
BuildRequires:	autogen
%if %{with talpo}
BuildRequires:	talpo
%endif
# For updating Makefile template after patch 12
BuildRequires:	autogen

Requires:	xorriso
Requires:	rosa-release-common
Requires(post):	os-prober

Provides:	bootloader
Provides:	grub2bootloader

Suggests:	%{name}-rosa-theme = %{version}-%{release}

%description
GNU GRUB is a Multiboot boot loader. It was derived from GRUB, the
GRand Unified Bootloader, which was originally designed and implemented
by Erich Stefan Boleyn.

Briefly, a boot loader is the first software program that runs when a
computer starts. It is responsible for loading and transferring control
to the operating system kernel software (such as the Hurd or Linux).
The kernel, in turn, initializes the rest of the operating system (e.g. GNU).

#-----------------------------------------------------------------------

%ifarch %{efi}
%package efi
Summary:        GRUB for EFI systems
Group:          System/Kernel and hardware
Suggests:	efibootmgr

%description efi
The GRand Unified Bootloader (GRUB) is a highly configurable and customizable
bootloader with modular architecture. 

It support rich variety of kernel formats, file systems, computer 
architectures and hardware devices.  This subpackage provides support 
for EFI systems.
%endif

#-----------------------------------------------------------------------

%package rosa-theme
Summary:	Provides a graphical theme with a custom ROSA background for grub2
Group:		System/Kernel and hardware

Requires:	grub2bootloader
Provides:	grub2theme
BuildArch:	noarch

%description rosa-theme
This package provides a custom Mageia graphical theme.
It is provided as a separate package so it may be easily excluded from
minimal installations where a graphical theme is not required.

#-----------------------------------------------------------------------
%prep
%setup -q -n grub-%{version}
%apply_patches
./autogen.sh

perl -pi -e 's/(\@image\{font_char_metrics,,,,)\.(png\})/$1$2/;'	\
	docs/grub-dev.texi

perl -pi -e "s|(^FONT_SOURCE=)|\$1%{SOURCE6}|;" configure configure.ac

sed -ri -e 's/-g"/"/g' -e "s/-Werror//g" configure.ac

perl -pi -e 's/-Werror//;' grub-core/Makefile.am

tar -xf %{SOURCE8}
pushd po-update; sh ./update.sh; popd
cd ..
%ifarch %{efi}
cp -r grub-%{version} grub-efi-%{version}
ls
%endif

#-----------------------------------------------------------------------
%build
cd ..
%ifarch %{efi}
cd grub-efi-%{version}
%configure                                              \
%if %{with talpo}
	CC=talpo                                        \
	CFLAGS=-fplugin-arg-melt-option=talpo-arg-file:%{SOURCE3} \
%else
	CFLAGS=""                                       \
%endif
	TARGET_LDFLAGS=-static                          \
	--with-platform=efi                             \
	--program-transform-name=s,grub,%{name}-efi,    \
	--libdir=%{libdir32}                            \
	--libexecdir=%{libdir32}                        \
	--with-grubdir=grub2                            \
	--disable-werror                                \
	--enable-grub-emu-usb							\
	--enable-grub-mkfont
%make all

make html pdf
%ifarch %{ix86}
%define grubefiarch i386-efi
%else
%define grubefiarch %{_arch}-efi
%endif
./grub-mkimage -O %{grubefiarch} -p /EFI/rosa/%{name}-efi -o grub.efi -d grub-core part_gpt hfsplus fat \
        ext2 btrfs normal chain boot configfile linux appleldr minicmd \
        loadbios reboot halt search font gfxterm echo video efi_gop efi_uga
cd ..
%endif

cd grub-%{version}
%configure                                              \
%if %{with talpo}
	CC=talpo                                        \
	CFLAGS=-fplugin-arg-melt-option=talpo-arg-file:%{SOURCE3} \
%else
	CFLAGS=""                                       \
%endif
	TARGET_LDFLAGS=-static                          \
	--with-platform=pc                              \
    %ifarch x86_64
	--enable-efiemu                                 \
    %endif
	--program-transform-name=s,grub,%{name},        \
	--libdir=%{libdir32}                            \
	--libexecdir=%{libdir32}                        \
	--with-grubdir=grub2                            \
	--disable-werror                                \
	--enable-grub-emu-usb							\
	--enable-grub-mkfont
%make all

make html pdf
#-----------------------------------------------------------------------
%install
cp %{SOURCE10} .
%ifarch %{efi}
cd ..
cd grub-efi-%{version}
%makeinstall_std
%makeinstall_std -C docs install-pdf install-html
mv -f %{buildroot}%{_docdir}/grub %{buildroot}%{_docdir}/%{name}
install -m644 COPYING INSTALL NEWS README THANKS TODO ChangeLog	\
	%{buildroot}%{_docdir}/%{name}
mv $RPM_BUILD_ROOT/etc/bash_completion.d/grub $RPM_BUILD_ROOT/etc/bash_completion.d/grub-efi

# (bor) grub.info is harcoded in sources
mv %{buildroot}%{_infodir}/grub.info %{buildroot}%{_infodir}/grub2.info

# Script that makes part of grub.cfg persist across updates
install -m 755 %{SOURCE1} %{buildroot}%{_sysconfdir}/grub.d/

# Ghost config file
install -m 755 -d $RPM_BUILD_ROOT/boot/efi/EFI/rosa/
install -d $RPM_BUILD_ROOT/boot/efi/EFI/rosa/%{name}-efi
touch $RPM_BUILD_ROOT/boot/efi/EFI/rosa/%{name}-efi/grub.cfg
ln -s ../boot/efi/EFI/rosa/%{name}-efi/grub.cfg $RPM_BUILD_ROOT%{_sysconfdir}/%{name}-efi.cfg

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
install -m 755 grub.efi %{buildroot}/boot/efi/EFI/rosa/%{name}-efi/grub.efi
cd ..
%endif
cd grub-%{version}
######EFI
%makeinstall_std
%makeinstall_std -C docs install-pdf install-html
mv -f %{buildroot}%{_docdir}/grub %{buildroot}%{_docdir}/%{name}
install -m644 COPYING INSTALL NEWS README THANKS TODO ChangeLog	\
	%{buildroot}%{_docdir}/%{name}

# (bor) grub.info is harcoded in sources
mv %{buildroot}%{_infodir}/grub.info %{buildroot}%{_infodir}/grub2.info

# Script that makes part of grub.cfg persist across updates
install -m 755 %{SOURCE1} %{buildroot}%{_sysconfdir}/grub.d/

# Ghost config file
install -d %{buildroot}/boot/%{name}
install -d %{buildroot}/boot/%{name}/locale
touch %{buildroot}/boot/%{name}/grub.cfg
ln -s ../boot/%{name}/grub.cfg %{buildroot}%{_sysconfdir}/%{name}.cfg

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
%{_sbindir}/%{name}-mkconfig -o /boot/%{name}/grub.cfg
EOF
	chmod 0755 %{name}.script
	popd
}

%__mkdir_p %{buildroot}/boot/%{name}/themes/
tar -xf %{SOURCE7} -C %{buildroot}/boot/%{name}/themes

#mv -f %{buildroot}/%{libdir32}/grub %{buildroot}/%{libdir32}/%{name}
#mv -f %{buildroot}/%{_datadir}/grub %{buildroot}/%{_datadir}/%{name}

# Windows EFI entry
install -m 755 %{SOURCE12} %{buildroot}%{_sysconfdir}/grub.d

%find_lang grub

#drop all zero-length file
#find %{buildroot} -size 0 -delete

#Copy font to properly place
%__mkdir_p %{buildroot}/boot/%{name}/fonts/
cp -f %{buildroot}%{_datadir}/grub/unicode.pf2 %{buildroot}/boot/%{name}/fonts/

%post
exec >/dev/null 2>&1
# Create device.map or reuse one from GRUB Legacy
cp -u /boot/grub/device.map /boot/%{name}/device.map 2>/dev/null ||
	%{_sbindir}/%{name}-mkdevicemap
# Determine the partition with /boot
BOOT_PARTITION=$(df -h /boot |(read; awk '{print $1; exit}'|sed 's/[[:digit:]]*$//'))
# (Re-)Generate core.img, but don't let it be installed in boot sector
%{_sbindir}/%{name}-install $BOOT_PARTITION
# Regenerate configure on install or update
%{_sbindir}/update-grub2
#bugfix: error message before loading of grub2 menu on boot
cp -f /boot/grub2/locale/en@quot.mo /boot/grub2/locale/en.mo

#delete non-needing doubling rpmsave and rpmnew files
rm -f /etc/grub.d/*.rpmsave
rm -f /etc/grub.d/*.rpmnew

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

%post rosa-theme
# Remove all previous theme from config
sed -i '/GRUB_THEME=*/d' %{_sysconfdir}/default/grub
sed -i '/GRUB_BACKGROUND=*/d' %{_sysconfdir}/default/grub
# Remove trailing blank lines from /etc/default/grub
sed -i -e :a -e '/^\n*$/{$d;N;};/\n$/ba' %{_sysconfdir}/default/grub
# Check that /etc/default/grub ends in a linefeed
[ "$(tail -n 1 %{_sysconfdir}/default/grub | wc --lines)" = "1" ] || echo >> %{_sysconfdir}/default/grub
# Add theme
echo "GRUB_THEME=\"/boot/grub2/themes/rosa/theme.txt\"" >> %{_sysconfdir}/default/grub
echo "GRUB_BACKGROUND=\"/boot/grub2/themes/rosa/terminal_background.png\"" >> %{_sysconfdir}/default/grub

#ostun rosa-theme
#exec > /var/log/%{name}_theme_postun.log 2>&1
# Only if uninstalling theme
#if [ $1 -eq 0 ]; then
# Remove theme from config
#sed -i '/GRUB_THEME=\/boot\/grub2\/themes\/rosa\/theme.txt/d' %{_sysconfdir}/default/grub
#fi

#-----------------------------------------------------------------------
%files -f grub.lang
%defattr(-,root,root,-)
#%{libdir32}/%{name}
%{libdir32}/grub/*-%{platform}
#%{_sbindir}/%{name}-*
#%{_bindir}/%{name}-*
%{_sbindir}/update-grub2
%{_bindir}/%{name}-editenv
%{_bindir}/%{name}-fstest
%{_bindir}/%{name}-kbdcomp
%{_bindir}/%{name}-menulst2cfg
%{_bindir}/%{name}-mkfont
%{_bindir}/%{name}-mkimage
%{_bindir}/%{name}-mklayout
%{_bindir}/%{name}-mkpasswd-pbkdf2
%{_bindir}/%{name}-mkrelpath
%{_bindir}/%{name}-mkrescue
%{_bindir}/%{name}-mkstandalone
%{_bindir}/%{name}-script-check
%{_sbindir}/%{name}-bios-setup
%{_sbindir}/%{name}-install
%{_sbindir}/%{name}-mkconfig
%{_sbindir}/%{name}-mknetdir
%{_sbindir}/%{name}-ofpathname
%{_sbindir}/%{name}-probe
%{_sbindir}/%{name}-reboot
%{_sbindir}/%{name}-set-default
%{_sbindir}/%{name}-sparc64-setup
#%{_datadir}/%{name}
%{_datadir}/grub
%attr(0700,root,root) %dir %{_sysconfdir}/grub.d
%{_sysconfdir}/grub.d/README
%config %{_sysconfdir}/grub.d/??_*
%{_sysconfdir}/%{name}.cfg
%attr(0644,root,root) %config %{_sysconfdir}/default/grub
#attr(0644,root,root) %config(noreplace) %{_sysconfdir}/default/grub
%{_sysconfdir}/bash_completion.d/grub
%dir /boot/%{name}
%dir /boot/%{name}/locale
# Actually, this is replaced by update-grub from scriptlets,
# but it takes care of modified persistent part
%config(noreplace) /boot/%{name}/grub.cfg
%doc %{_docdir}/%{name}
%{_infodir}/%{name}.info*
%{_infodir}/grub-dev.info*
%{_mandir}/man1/%{name}-*.1*
%{_mandir}/man8/%{name}-*.8*
# RPM filetriggers
%{_filetriggers_dir}/%{name}.*
%exclude /boot/%{name}/fonts/unicode.pf2


%files efi 
%defattr(-,root,root,-)
%attr(0755,root,root) %dir /boot/efi/EFI/rosa/grub2-efi
%attr(0755,root,root) /boot/efi/EFI/rosa/grub2-efi/grub.efi
%attr(0755,root,rott) %ghost %config(noreplace) /boot/efi/EFI/rosa/grub2-efi/grub.cfg
/etc/bash_completion.d/grub-efi
%{libdir32}/grub/%{_arch}-efi/
%{_sbindir}/%{name}-efi*
%{_bindir}/%{name}-efi*
#%{_datadir}/grub
#%{_sysconfdir}/grub.d
%config(noreplace) %{_sysconfdir}/%{name}-efi.cfg

# Actually, this is replaced by update-grub from scriptlets,
# but it takes care of modified persistent part
#%config(noreplace) /boot/efi/EFI/rosa/%{name}-efi/grub.cfg
# RPM filetriggers
#%{_filetriggers_dir}/%{name}.*

%files rosa-theme
/boot/%{name}/fonts/unicode.pf2
%dir /boot/%{name}/themes/rosa
/boot/%{name}/themes/rosa/*


%changelog
* Wed Aug 29 2013 akdengi <akdengi> - 2.00-20
- add EFI patches from Fedora and generate properly menu items for Windows efi if it found in system
- split common package and theme package

* Wed May 08 2013 Aleksandr Kazantcev <akdengi>
- Deletw quiet from default grub menu
- Add acpi_backlight=vendor and acpi_osi=Linux for properly support notebooks

* Tue Jan 03 2012 Paulo Andrade <pcpa@mandriva.com.br> 1.99-4
+ Revision: 750375
- Rework sample theme test script to work on a fresh svn checkout.
- Add documentation and script to test grub2 themes
- Add talpo build and melt config file for debug build (thanks to alissy)
