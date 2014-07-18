%define		libdir32	%{_exec_prefix}/lib
%define platform pc
%define efi 1

%global efi %{ix86} x86_64

%bcond_with	talpo

Name:		grub2
Version:	2.00
Release:	53
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
Source8:	grub2-po-update.tar.gz
Source9:	update-grub2
Source10:	README.urpmi
Source11:	grub2.rpmlintrc
Source12:	42_efi
Source13:   43_resque
Source14:	grub2-cfg-mod

Patch0:		grub2-locales.patch
Patch1:		grub2-00_header.patch
Patch2:		grub2-custom-color.patch
Patch3:		grub2-move-terminal.patch
Patch4:		grub2-read-cfg.patch
Patch5:		grub2-symlink-is-garbage.patch
Patch6:		grub2-name-corrections.patch
Patch8:		grub2-theme-not_selected_item_box.patch
Patch9:         grub-2.00.Linux.remove.patch
Patch10:	grub2-mkfont-fix.patch
Patch11:	grub2-2.00-class-via-os-prober.patch
Patch12:        grub-2.00.safe.patch
Patch13:	grub-2.00-unifont-path.patch
Patch14:	grub-2.00-proportional-scale.patch
Patch15:        grub-2.00.30_os-prober.options.patch
# Build with freetype 2.5.1 and higher
Patch16:	grub-2.00-freetype-2.5.1.patch
Patch18:        grub-2.00.fix.build.flex.patch


# Fedora patches:
# https://bugzilla.redhat.com/show_bug.cgi?id=857936
Patch100:		grub2-2.00-fda-add-fw_path-search_v2.patch
# Add support for entering the firmware setup screen.
Patch101:		grub2-2.00-fda-Add-fwsetup.patch
# Don't decrease efi memory map size
Patch102:		grub2-2.00-fda-dont-decrease-mmap-size.patch
# IBM client architecture (CAS) reboot support
Patch103:		grub2-2.00-fda-cas-reboot-support.patch
# Read chunks in smaller blocks
Patch104:		grub2-2.00-fda-efidisk-ahci-workaround.patch
# Fix crash on http: https://bugzilla.redhat.com/show_bug.cgi?id=860834
Patch105:		grub2-2.00-fda-fix-http-crash.patch
# Issue separate DNS queries for ipv4 and ipv6
Patch106:		grub2-2.00-fda-Issue-separate-DNS-queries-for-ipv4-and-ipv6.patch
# Don't allow insmod when secure boot is enabled
Patch107:		grub2-2.00-fda-no-insmod-on-sb.patch
# Add support for crappy cd craparino
Patch108:		grub2-2.00-fda-cdpath.patch
# Add support for linuxefi
Patch109:	grub2-2.00-fda-linuxefi.patch
# Use "linuxefi" and "initrdefi" where appropriate
Patch110:	grub2-2.00-fda-use-linuxefi.patch
# Fix parallel build
Patch111:	grub2-2.00-parallel-build.patch

#Mageia patches
# Fix autoreconf warnings
Patch200:	grub2-2.00-mga-fix_AM_PROG_MKDIR_P-configure.ac.patch

# ROSA quick fix. Need rediff previous patch
Patch500:	grub2-10_linux_hibernate_fix.patch

Patch501:	grub2-2.00-gnulib-compatibility.patch
Patch502:	grub2-2.00-os-prober-efi-support.patch
Patch503:	grub2-2.00-improved-boot-menu.patch
Patch504:	grub2-2.00-cut-long-menu-titles.patch
Patch505:       grub-2.00.texi.diff
Patch506:       grub-2.00.autoreconf.patch

BuildRequires:	bison
BuildRequires:	flex
BuildRequires:	ruby
BuildRequires:	fonts-ttf-unifont >= 6.2
BuildRequires:	freetype2-devel
BuildRequires:	glibc-static-devel
BuildRequires:	help2man
BuildRequires:	liblzma-devel
BuildRequires:	liblzo-devel
BuildRequires:	libusb-devel
BuildRequires:	ncurses-devel
BuildRequires:	texinfo
BuildRequires:	texlive-latex
# BuildRequires:  texlive-scheme-tetex
BuildRequires:	texlive-epsf
BuildRequires:	pkgconfig(devmapper)
BuildRequires:	autogen
%if %{with talpo}
BuildRequires:	talpo
%endif
# For updating Makefile template after patch 12
BuildRequires:	autogen

Requires:	xorriso
Requires:	rosa-release-common
Requires:	grub2-theme
Requires(post):	os-prober

Provides:	bootloader
Provides:	grub2bootloader

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

%prep
%setup -q -n grub-%{version}
%apply_patches
perl -pi -e 's/(\@image\{font_char_metrics,,,,)\.(png\})/$1$2/;' \
        docs/grub-dev.texi

sed -ri -e 's/-g"/"/g' -e "s/-Werror//g" configure.ac

perl -pi -e 's/-Werror//;' grub-core/Makefile.am
export GRUB_CONTRIB="$PWD/grub-extras"
aclocal --force -Im4 -I/usr/share/aclocal --install
./autogen.sh

%build
export CONFIGURE_TOP="$PWD"
%ifarch %{efi}
mkdir -p efi
pushd efi
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
	--with-grubdir=grub2                           \
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
popd
%endif

mkdir -p pc
cd pc
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
cd efi
%makeinstall_std
%makeinstall_std -C docs install-pdf install-html
mv %{buildroot}%{_infodir}/grub.info %{buildroot}%{_infodir}/grub2.info
#install -m644 COPYING INSTALL NEWS README THANKS TODO ChangeLog	\
#	%{buildroot}%{_docdir}/%{name}
mv %{buildroot}/etc/bash_completion.d/grub %{buildroot}/etc/bash_completion.d/grub-efi


# Script that makes part of grub.cfg persist across updates
install -m 755 %{SOURCE1} %{buildroot}%{_sysconfdir}/grub.d/

# Ghost config file
 install -m 755 -d %{buildroot}/boot/efi/EFI/rosa/
 install -d %{buildroot}/boot/efi/EFI/rosa/%{name}-efi
 touch %{buildroot}/boot/efi/EFI/rosa/%{name}-efi/grub.cfg
 ln -s ../boot/efi/EFI/rosa/%{name}-efi/grub.cfg %{buildroot}%{_sysconfdir}/%{name}-efi.cfg

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
cd pc
######EFI
%makeinstall_std
%makeinstall_std -C docs install-pdf install-html
mv -f %{buildroot}%{_docdir}/grub %{buildroot}%{_docdir}/%{name}
#install -m644 COPYING INSTALL NEWS README THANKS TODO ChangeLog	\
#	%{buildroot}%{_docdir}/%{name}

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

#mv -f %{buildroot}/%{libdir32}/grub %{buildroot}/%{libdir32}/%{name}
#mv -f %{buildroot}/%{_datadir}/grub %{buildroot}/%{_datadir}/%{name}

# Windows EFI entry
install -m 755 %{SOURCE12} %{buildroot}%{_sysconfdir}/grub.d

# repair section
install -m 755 %{SOURCE13} %{buildroot}%{_sysconfdir}/grub.d

# <akdengi> install programm to change option in /etc/default/grub
install -m 755 %{SOURCE14} %{buildroot}%{_sbindir}/grub2-cfg-mod


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

#-----------------------------------------------------------------------
%files -f pc/grub.lang
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
%{_sbindir}/grub2-cfg-mod
#%{_datadir}/%{name}
%{_datadir}/grub
%attr(0700,root,root) %dir %{_sysconfdir}/grub.d
%{_sysconfdir}/grub.d/README
%config %{_sysconfdir}/grub.d/??_*
%{_sysconfdir}/%{name}.cfg
#%attr(0644,root,root) %config %{_sysconfdir}/default/grub
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/default/grub
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
%dir /boot/%{name}/fonts
/boot/%{name}/fonts/unicode.pf2


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
