%define		libdir32	%{_exec_prefix}/lib
#%define		unifont		%(echo %{_datadir}/fonts/TTF/unifont/unifont-*.ttf)

%bcond_with	talpo

Name:           grub2
Version:        2.00
Release:        1
Summary:        GNU GRUB is a Multiboot boot loader

Group:          System/Kernel and hardware
License:        GPLv3+
URL:            http://www.gnu.org/software/grub/
Source0:        grub-%{version}.tar.gz
Source1:        90_persistent
Source2:        grub.default
Source3:	grub.melt
# www.4shared.com/archive/lFCl6wxL/grub_guidetar.html
Source4:	grub_guide.tar.gz
Source5:	DroidSansMonoLicense.txt
Source6:	DroidSansMono.ttf
Source7:	rosa-theme.tar.gz
Source8:	grub2-po-update.tar.gz

Patch0:		grub2-locales.patch
Patch1:		grub2-00_header.patch
Patch2:		grub2-custom-color.patch
Patch3:		grub2-move-terminal.patch
Patch4:		grub2-read-cfg.patch
Patch5:		grub2-symlink-is-garbage.patch
Patch6:		grub2-name-corrections.patch

BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-buildroot

BuildRequires:	bison
BuildRequires:  flex
#BuildRequires:	fonts-ttf-unifont
BuildRequires:	freetype2-devel
BuildRequires:	glibc-static-devel
BuildRequires:	help2man
BuildRequires:	liblzma-devel
BuildRequires:	liblzo-devel
BuildRequires:	libusb-devel
BuildRequires:	ncurses-devel
#BuildRequires:	texinfo
#BuildRequires:	texlive
%if %{with talpo}
BuildRequires:	talpo
%endif

Requires:	xorriso
Requires(post):	os-prober

Provides:   bootloader

%description
GNU GRUB is a Multiboot boot loader. It was derived from GRUB, the
GRand Unified Bootloader, which was originally designed and implemented
by Erich Stefan Boleyn.

Briefly, a boot loader is the first software program that runs when a
computer starts. It is responsible for loading and transferring control
to the operating system kernel software (such as the Hurd or Linux).
The kernel, in turn, initializes the rest of the operating system (e.g. GNU).

#-----------------------------------------------------------------------

#-----------------------------------------------------------------------
%prep
%setup -q -n grub-%{version}
%apply_patches

perl -pi -e 's/(\@image\{font_char_metrics,,,,)\.(png\})/$1$2/;'	\
	docs/grub-dev.texi

perl -pi -e "s|(^FONT_SOURCE=)|\$1%{SOURCE6}|;" configure configure.ac

sed -ri -e 's/-g"/"/g' -e "s/-Werror//g" configure.ac

perl -pi -e 's/-Werror//;' grub-core/Makefile.am

tar -xf %{SOURCE8}
pushd po-update; sh ./update.sh; popd

#-----------------------------------------------------------------------
%build
%configure						\
%if %{with talpo}
	CC=talpo					\
	CFLAGS=-fplugin-arg-melt-option=talpo-arg-file:%{SOURCE3} \
%else
	CFLAGS=""                                       \
%endif
	TARGET_LDFLAGS=-static				\
	--with-platform=pc				\
    %ifarch x86_64
	--enable-efiemu					\
    %endif
	--program-transform-name=s,grub,%{name},	\
	--libdir=%{libdir32}				\
	--libexecdir=%{libdir32}			\
	--with-grubdir=grub2				\
	--disable-werror
%make all

make html pdf

#-----------------------------------------------------------------------
%install
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

%find_lang grub

%clean
rm -rf %{buildroot}

%post
exec >/dev/null 2>&1
# Create device.map or reuse one from GRUB Legacy
cp -u /boot/grub/device.map /boot/%{name}/device.map 2>/dev/null ||
	%{_sbindir}/%{name}-mkdevicemap
# Determine the partition with /boot
BOOT_PARTITION=$(df -h /boot |(read; awk '{print $1; exit}'|sed 's/[[:digit:]]*$//'))
# (Re-)Generate core.img, but don't let it be installed in boot sector
%{_sbindir}/%{name}-install $BOOT_PARTITION
# Generate grub.cfg and add GRUB2 chainloader to menu on initial install
if [ $1 = 1 ]; then
    %{_sbindir}/%{name}-mkconfig -o /boot/%{name}/grub.cfg
fi

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
%files -f grub.lang
%defattr(-,root,root,-)
#%{libdir32}/%{name}
%{libdir32}/grub
%{_sbindir}/%{name}-*
%{_bindir}/%{name}-*
#%{_datadir}/%{name}
%{_datadir}/grub
%{_sysconfdir}/grub.d
%{_sysconfdir}/%{name}.cfg
%{_sysconfdir}/default/grub
%{_sysconfdir}/bash_completion.d/grub
%dir /boot/%{name}
%dir /boot/%{name}/locale
/boot/%{name}/themes
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


%changelog
* Tue Jan 03 2012 Paulo Andrade <pcpa@mandriva.com.br> 1.99-4
+ Revision: 750375
- Rework sample theme test script to work on a fresh svn checkout.
- Add documentation and script to test grub2 themes
- Add talpo build and melt config file for debug build (thanks to alissy)

* Thu Aug 25 2011 Paulo Andrade <pcpa@mandriva.com.br> 1.99-3
+ Revision: 696543
- Add a very simple sample grub2 mandriva theme
- Build and install pdf and html documentation.

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

* Wed Jan 02 2008 Olivier Blin <blino@mandriva.org> 0:1.95-1mdv2008.1
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

