%{!?pear_metadir: %global pear_metadir %{pear_phpdir}}
%{!?__pear: %{expand: %%global __pear %{_bindir}/pear}}
%global pear_name    Horde_Vfs
%global pear_channel pear.horde.org

# currently tests are not ready
# Fatal error: Access to undeclared static property: Horde_Vfs_SmbTest::$reason in
%global with_tests   %{?_with_tests:1}%{!?_with_tests:0}

Name:           php-horde-Horde-Vfs
Version:        2.0.4
Release:        3%{?dist}
Summary:        Virtual File System API

Group:          Development/Libraries
License:        LGPLv2
URL:            http://pear.horde.org
Source0:        http://%{pear_channel}/get/%{pear_name}-%{version}.tgz

# https://github.com/horde/horde/pull/29
Patch0:         %{name}-shebang.patch

BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root
BuildArch:      noarch
BuildRequires:  php-common >= 5.3.0
BuildRequires:  php-pear(PEAR) >= 1.7.0
BuildRequires:  php-channel(%{pear_channel})
BuildRequires:  gettext
%if %{with_tests}
# To run unit tests
BuildRequires:  php-pear(%{pear_channel}/Horde_Test) >= 2.1.0
BuildRequires:  php-pear(%{pear_channel}/Horde_Db) >= 2.0.0
%endif

Requires(post): %{__pear}
Requires(postun): %{__pear}
Requires:       php-common >= 5.3.0
Requires:       php-date
Requires:       php-pcre
Requires:       php-posix
Requires:       php-pear(PEAR) >= 1.7.0
Requires:       php-channel(%{pear_channel})
Requires:       php-pear(%{pear_channel}/Horde_Exception) >= 2.0.0
Conflicts:      php-pear(%{pear_channel}/Horde_Exception) >= 3.0.0
Requires:       php-pear(%{pear_channel}/Horde_Translation) >= 2.0.0
Conflicts:      php-pear(%{pear_channel}/Horde_Translation) >= 3.0.0
Requires:       php-pear(%{pear_channel}/Horde_Util) >= 2.0.0
Conflicts:      php-pear(%{pear_channel}/Horde_Util) >= 3.0.0
# Optionnal
Requires:       php-ftp
Requires:       php-pecl(ssh2)
Requires:       php-pear(%{pear_channel}/Horde_Auth) >= 2.0.0
Conflicts:      php-pear(%{pear_channel}/Horde_Auth) >= 3.0.0
Requires:       php-pear(%{pear_channel}/Horde_Db) >= 2.0.0
Conflicts:      php-pear(%{pear_channel}/Horde_Db) >= 3.0.0
Requires:       php-pear(%{pear_channel}/Horde_Kolab_Session) >= 2.0.0
Conflicts:      php-pear(%{pear_channel}/Horde_Kolab_Session) >= 3.0.0
Requires:       php-pear(%{pear_channel}/Horde_Mime) >= 2.0.0
Conflicts:      php-pear(%{pear_channel}/Horde_Mime) >= 3.0.0
Requires:       php-pear(%{pear_channel}/Horde_Perms) >= 2.0.0
Conflicts:      php-pear(%{pear_channel}/Horde_Perms) >= 3.0.0
# skip Horde_Core (avoid circular dependency)

Provides:       php-pear(%{pear_channel}/%{pear_name}) = %{version}


%description
This package provides a Virtual File System API, with backends for:

* SQL
* FTP
* Local filesystems
* Hybrid SQL and filesystem
* Samba
* SSH2/SFTP
* IMAP (Kolab)

Reading, writing and listing of files are all supported, and there are both
object-based and array-based interfaces to directory listings.


%prep
%setup -q -c

%patch0 -p0 -b .shebang

cd %{pear_name}-%{version}

# Don't install .po and .pot files
# Remove checksum for .mo, as we regenerate them
sed -e '/%{pear_name}.po/d' \
    -e '/Horde_Other.po/d' \
    -e '/%{pear_name}.mo/s/md5sum=.*name=/name=/' \
    ../package.xml >%{name}.xml


%build
cd %{pear_name}-%{version}

# Regenerate the locales
for po in $(find locale -name \*.po)
do
   msgfmt $po -o $(dirname $po)/$(basename $po .po).mo
done


%install
cd %{pear_name}-%{version}
%{__pear} install --nodeps --packagingroot %{buildroot} %{name}.xml

# Clean up unnecessary files
rm -rf %{buildroot}%{pear_metadir}/.??*

# Install XML package description
mkdir -p %{buildroot}%{pear_xmldir}
install -pm 644 %{name}.xml %{buildroot}%{pear_xmldir}

# Locales
for loc in locale/{??,??_??}
do
    lang=$(basename $loc)
    test -d %{buildroot}%{pear_datadir}/%{pear_name}/$loc \
         && echo "%%lang(${lang%_*}) %{pear_datadir}/%{pear_name}/$loc"
done | tee ../%{pear_name}.lang


%check
%if %{with_tests}
cd %{pear_name}-%{version}/test/$(echo %{pear_name} | sed -e s:_:/:g)
phpunit \
   -d date.timezone=UTC \
   -d include_path=%{buildroot}%{pear_phpdir}:.:%{pear_phpdir} \
   .
%else
: Test disabled, missing '--with tests' option.
%endif


%post
%{__pear} install --nodeps --soft --force --register-only \
    %{pear_xmldir}/%{name}.xml >/dev/null || :

%postun
if [ $1 -eq 0 ] ; then
    %{__pear} uninstall --nodeps --ignore-errors --register-only \
        %{pear_channel}/%{pear_name} >/dev/null || :
fi


%files -f %{pear_name}.lang
%defattr(-,root,root,-)
%doc %{pear_docdir}/%{pear_name}
%{_bindir}/horde-vfs
%{pear_xmldir}/%{name}.xml
%{pear_phpdir}/Horde/Vfs
%{pear_phpdir}/Horde/Vfs.php
%{pear_testdir}/%{pear_name}
%dir %{pear_datadir}/%{pear_name}
%dir %{pear_datadir}/%{pear_name}/locale
%{pear_datadir}/%{pear_name}/migration


%changelog
* Sun Feb 10 2013 Remi Collet <remi@fedoraproject.org> - 2.0.4-3
- fix shebang, https://github.com/horde/horde/pull/29

* Sun Feb 10 2013 Remi Collet <remi@fedoraproject.org> - 2.0.4-2
- cleanups for review

* Thu Jan 10 2013 Remi Collet <RPMS@FamilleCollet.com> - 2.0.4-1
- Update to 2.0.4 for remi repo
- add option for test (need investigation)

* Tue Nov 27 2012 Remi Collet <RPMS@FamilleCollet.com> - 2.0.3-1
- Update to 2.0.3 for remi repo

* Sat Nov 17 2012 Remi Collet <RPMS@FamilleCollet.com> - 2.0.2-2
- enable test

* Thu Nov 15 2012 Remi Collet <RPMS@FamilleCollet.com> - 2.0.2-1
- Update to 2.0.2 for remi repo
- disable test are a newer Horde_Test is required
  http://bugs.horde.org/ticket/11710

* Wed Nov  7 2012 Remi Collet <RPMS@FamilleCollet.com> - 2.0.1-1
- Update to 2.0.1 for remi repo

* Sat Nov  3 2012 Remi Collet <RPMS@FamilleCollet.com> - 2.0.0-1
- Update to 2.0.0 for remi repo

* Thu Jun 21 2012 Nick Bebout <nb@fedoraproject.org> - 1.0.9-1
- Upgrade to 1.0.9

* Sat Jan 28 2012 Nick Bebout <nb@fedoraproject.org> - 1.0.8-1
- Initial package
