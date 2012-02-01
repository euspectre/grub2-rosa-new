%define		libdir32	%{_exec_prefix}/lib

Name:           grub2
Version:        1.99
Release:        2
Summary:        GNU GRUB is a Multiboot boot loader

Group:          System/Kernel and hardware
License:        GPLv3+
URL:            http://www.gnu.org/software/grub/
Source0:        http://alpha.gnu.org/pub/gnu/grub/grub-%{version}.tar.xz
Source1:        90_persistent
Source2:        grub.default
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-buildroot

BuildRequires:	bison
BuildRequires:  flex
BuildRequires:	freetype2-devel
BuildRequires:	glibc-static-devel
BuildRequires:	help2man
BuildRequires:	liblzo-devel
BuildRequires:	libusb-devel
BuildRequires:	ncurses-devel
BuildRequires:	texinfo
BuildRequires:	liblzma-devel

Requires(preun):drakxtools-backend
Requires(post): drakxtools-backend

%description
GNU GRUB is a Multiboot boot loader. It was derived from GRUB, the
GRand Unified Bootloader, which was originally designed and implemented
by Erich Stefan Boleyn.

Briefly, a boot loader is the first software program that runs when a
computer starts. It is responsible for loading and transferring control
to the operating system kernel software (such as the Hurd or Linux).
The kernel, in turn, initializes the rest of the operating system (e.g. GNU).

%prep
%setup -q -n grub-%{version}

%build
%configure						\
	CFLAGS=""					\
	TARGET_LDFLAGS=-static				\
	--with-platform=pc				\
%ifarch x86_64
	--enable-efiemu					\
%endif
	--enable-grub-emu-usb				\
	--program-transform-name=s,grub,%{name},	\
	--libdir=%{libdir32}				\
	--libexecdir=%{libdir32}
%make

%install
%makeinstall_std

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

%find_lang grub

%clean
rm -rf %{buildroot}

%post
exec >/dev/null 2>&1
# Create device.map or reuse one from GRUB Legacy
cp -u /boot/grub/device.map /boot/%{name}/device.map 2>/dev/null ||
	%{_sbindir}/%{name}-mkdevicemap
# Determine the partition with /boot
BOOT_PARTITION=$(df -h /boot |(read; awk '{print $1; exit}'))
# (Re-)Generate core.img, but don't let it be installed in boot sector
%{_sbindir}/%{name}-install --grub-setup=/bin/true $BOOT_PARTITION
# Generate grub.cfg and add GRUB2 chainloader to menu on initial install
if [ $1 = 1 ]; then
    %{_sbindir}/bootloader-config --action add-entry --image /boot/%{name}/core.img --label 'Chainload GRUB2'
    %{_sbindir}/%{name}-mkconfig -o /boot/%{name}/grub.cfg
fi

%preun
exec >/dev/null
if [ $1 = 0 ]; then
    # Remove GRUB2 from bootloader menu on final remove
    %{_sbindir}/bootloader-config --action remove-entry --image /boot/%{name}/core.img
    # XXX Ugly
    rm -f /boot/%{name}/*.mod
    rm -f /boot/%{name}/*.img
    rm -f /boot/%{name}/*.lst
    rm -f /boot/%{name}/*.o
    rm -f /boot/%{name}/device.map
fi

%files -f grub.lang
%defattr(-,root,root,-)
%{libdir32}/%{name}
%{libdir32}/grub
%{_sbindir}/%{name}-*
%{_bindir}/%{name}-*
%{_sysconfdir}/grub.d
%{_sysconfdir}/%{name}.cfg
%{_sysconfdir}/default/grub
%{_sysconfdir}/bash_completion.d/grub
%dir /boot/%{name}
%dir /boot/%{name}/locale
# Actually, this is replaced by update-grub from scriptlets,
# but it takes care of modified persistent part
%config(noreplace) /boot/%{name}/grub.cfg
%doc COPYING INSTALL NEWS README THANKS TODO ChangeLog
%{_infodir}/%{name}.info*
%{_infodir}/grub-dev.info*
%{_mandir}/man1/%{name}-*.1*
%{_mandir}/man8/%{name}-*.8*
# RPM filetriggers
%{_filetriggers_dir}/%{name}.*


%changelog
* Thu Jul 07 2011 Per Øyvind Karlsen <peroyvind@mandriva.org> 1.99-2
+ Revision: 689083
- build with xz support

* Thu Jun 02 2011 Paulo Andrade <pcpa@mandriva.com.br> 1.99-1
+ Revision: 682534
- Cleanup to better match upstream, and update to latest upstream release

* Sat Oct 23 2010 Andrey Borzenkov <arvidjaar@mandriva.org> 1.98-2mdv2011.0
+ Revision: 587770
- add menu entry "Chainload GRUB2" to default bootloader on first install
  create default grub.cfg on first install
- use filetriggers instead of standard triggers to update grub.cfg on
  kernel add/remove. Every kernel package has unique name in Mandriva
  and plain triggers do not support wildcards
- source2: update /etc/defaut/grub
  * set distributor to Mandriva
  * use splash=silent instead of "guiet rhgb" in GRUB_CMDLINE_LINUX_DEFAULT,
  not GRUB_CMDLINE_LINUX
  * do not generate rescue line by default, it is not done in grub1

* Mon Oct 11 2010 Andrey Borzenkov <arvidjaar@mandriva.org> 1.98-1mdv2011.0
+ Revision: 584979
- buildrequires help2man
- buildrequires texinfo for makeinfo
- package info and man pages

  + Per Øyvind Karlsen <peroyvind@mandriva.org>
    - new release: 1.98
      * partially sync with fedora
    - add missing buildrequires

  + Thierry Vignaud <tv@mandriva.org>
    - rebuild

  + Jérôme Soyer <saispo@mandriva.org>
    - New upstream release

* Sun Nov 16 2008 Tomasz Pawel Gajc <tpg@mandriva.org> 0:1.96-1mdv2009.1
+ Revision: 303844
- update to new version 1.96
- fix file list
- new license policy
- spec file clean

* Thu Jul 24 2008 Thierry Vignaud <tv@mandriva.org> 0:1.95-3mdv2009.0
+ Revision: 246647
- rebuild

* Wed Jan 02 2008 Olivier Blin <oblin@mandriva.com> 0:1.95-1mdv2008.1
+ Revision: 140742
- restore BuildRoot

  + Thierry Vignaud <tv@mandriva.org>
    - kill re-definition of %%buildroot on Pixel's request


* Sat Jan 20 2007 David Walluck <walluck@mandriva.org> 1.95-1mdv2007.0
+ Revision: 111172
- BuildRequires: bison
- Import grub2

* Sat Jan 20 2007 David Walluck <walluck@mandriva.org> 0:1.95-1mdv2007.1
- new grub

