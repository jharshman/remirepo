# remirepo spec file for php-Faker, from Fedora:
#
# Fedora spec file for php-Faker
#
# Copyright (c) 2012-2016 Shawn Iwinski <shawn.iwinski@gmail.com>
#
# License: MIT
# http://opensource.org/licenses/MIT
#
# Please preserve changelog entries
#

%global github_owner     fzaninotto
%global github_name      Faker
%global github_version   1.5.0
%global github_commit    d0190b156bcca848d401fb80f31f504f37141c8d

%global composer_vendor  fzaninotto
%global composer_project faker

# "php": ">=5.3.3"
%global php_min_ver 5.3.3

# Build using "--without tests" to disable tests
%global with_tests  %{?_without_tests:0}%{!?_without_tests:1}

%{!?phpdir:  %global phpdir  %{_datadir}/php}

Name:          php-%{github_name}
Version:       %{github_version}
Release:       5%{?dist}
Summary:       A PHP library that generates fake data

Group:         Development/Libraries
License:       MIT
URL:           https://github.com/%{github_owner}/%{github_name}
Source0:       %{url}/archive/%{github_commit}/%{name}-%{github_version}-%{github_commit}.tar.gz

BuildRoot:     %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch:     noarch
# Tests
%if %{with_tests}
## composer.json
BuildRequires: php(language) >= %{php_min_ver}
BuildRequires: php-composer(phpunit/phpunit)
## phpcompatinfo (computed from version 1.5.0)
BuildRequires: php-curl
BuildRequires: php-date
BuildRequires: php-filter
BuildRequires: php-hash
BuildRequires: php-intl
BuildRequires: php-mbstring
BuildRequires: php-pcre
BuildRequires: php-reflection
BuildRequires: php-spl
## Autoloader
BuildRequires: php-composer(symfony/class-loader)
%endif

# composer.json
Requires:      php(language) >= %{php_min_ver}
# composer.json: optional
Requires:      php-intl
# phpcompatinfo (computed from version 1.5.0)
Requires:      php-curl
Requires:      php-date
Requires:      php-hash
Requires:      php-mbstring
Requires:      php-pcre
Requires:      php-reflection
Requires:      php-spl
# Autoloader
Requires:      php-composer(symfony/class-loader)
# Weak dependencies
%if 0%{?fedora} >= 21
Suggests:      php-composer(doctrine/orm)
%endif

# php-{COMPOSER_VENDOR}-{COMPOSER_PROJECT}
Provides:      php-%{composer_vendor}-%{composer_project}           = %{version}-%{release}
# Composer
Provides:      php-composer(%{composer_vendor}/%{composer_project}) = %{version}

%description
Faker is a PHP library that generates fake data for you. Whether you need
to bootstrap your database, create good-looking XML documents, fill-in your
persistence to stress test it, or anonymize data taken from a production
service, Faker is for you.

Faker is heavily inspired by Perl's Data::Faker [1], and by Ruby's Faker [2].

Autoloader: %{phpdir}/Faker/autoload.php

Optional:
* CakePHP (http://cakephp.org/)
* Doctrine ORM (php-doctrine-orm)
* Mandango (http://mandango.org/)
* Propel (http://propelorm.org/)

[1] http://search.cpan.org/~jasonk/Data-Faker/
[2] http://faker.rubyforge.org/


%prep
%setup -qn %{github_name}-%{github_commit}

: Remove executable bits
: https://github.com/fzaninotto/Faker/pull/593
chmod a-x \
    src/Faker/Provider/sl_SI/Address.php \
    src/Faker/Provider/sl_SI/Internet.php \
    src/Faker/Provider/sl_SI/Payment.php \
    src/Faker/Provider/sl_SI/PhoneNumber.php \
    test/Faker/Provider/ja_JP/PersonTest.php

: Create autoloader
cat <<'AUTOLOAD' | tee src/Faker/autoload.php
<?php
/**
 * Autoloader for %{name} and its' dependencies
 * (created by %{name}-%{version}-%{release}).
 *
 * @return \Symfony\Component\ClassLoader\ClassLoader
 */

if (!isset($fedoraClassLoader) || !($fedoraClassLoader instanceof \Symfony\Component\ClassLoader\ClassLoader)) {
    if (!class_exists('Symfony\\Component\\ClassLoader\\ClassLoader', false)) {
        require_once '%{phpdir}/Symfony/Component/ClassLoader/ClassLoader.php';
    }

    $fedoraClassLoader = new \Symfony\Component\ClassLoader\ClassLoader();
    $fedoraClassLoader->register();
}

$fedoraClassLoader->addPrefix('Faker\\', dirname(__DIR__));

return $fedoraClassLoader;
AUTOLOAD


%build
# Empty build section, nothing to build


%install
rm -rf %{buildroot}
mkdir -p %{buildroot}%{phpdir}
cp -rp src/%{github_name} %{buildroot}%{phpdir}/


%check
%if %{with_tests}
: Skip tests that require downloading content
sed 's/function testDownloadWithDefaults/function SKIP_testDownloadWithDefaults/' \
    -i test/Faker/Provider/ImageTest.php
: Skip tests with erratic results in Koschei
sed -e '/561059108101825/d' \
    -e '/601100099013942/d' \
    -i test/Faker/Calculator/LuhnTest.php

%{_bindir}/phpunit --verbose \
    --bootstrap %{buildroot}%{phpdir}/Faker/autoload.php

if which php70; then
  php70 %{_bindir}/phpunit --verbose \
    --bootstrap %{buildroot}%{phpdir}/Faker/autoload.php
fi
%else
: Tests skipped
%endif


%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root,-)
%{!?_licensedir:%global license %%doc}
%license LICENSE
%doc *.md
%doc composer.json
%{phpdir}/%{github_name}


%changelog
* Sat Mar 12 2016 Shawn Iwinski <shawn.iwinski@gmail.com> - 1.5.0-5
- Add standard "php-{COMPOSER_VENDOR}-{COMPOSER_PROJECT}" provides
- Updated autoloader

* Fri Mar 11 2016 Remi Collet <remi@fedoraproject.org> - 1.5.0-4
- skip tests with erratic results in Koschei

* Sat May 30 2015 Shawn Iwinski <shawn.iwinski@gmail.com> - 1.5.0-1
- Updated to 1.5.0 (BZ #1226339)
- Packaged autoloader
- %%license usage

* Sun Jun  8 2014 Remi Collet <RPMS@FamilleCollet.com> - 1.4.0-1
- backport 1.3.0 for remi repo.

* Sun Jun 08 2014 Shawn Iwinski <shawn.iwinski@gmail.com> - 1.4.0-1
- Updated to 1.4.0 (BZ #1105815)
- Added php-composer(fzaninotto/faker) virtual provide
- Made Doctrine pkg optional instead of required
- Added option to build without tests

* Mon Dec 30 2013 Remi Collet <RPMS@FamilleCollet.com> - 1.3.0-1
- backport 1.3.0 for remi repo.

* Sun Dec 29 2013 Shawn Iwinski <shawn.iwinski@gmail.com> 1.3.0-1
- Updated to 1.3.0 (BZ #1044436)
- Spec cleanup

* Wed Jun 12 2013 Remi Collet <RPMS@FamilleCollet.com> - 1.2.0-1
- backport 1.2.0 for remi repo.

* Mon Jun 10 2013 Shawn Iwinski <shawn.iwinski@gmail.com> 1.2.0-1
- Updated to 1.2.0
- Added php-mbstring require
- Updates per new Fedora packaging guidelines for Git repos

* Wed Dec 19 2012 Remi Collet <RPMS@FamilleCollet.com> - 1.1.0-2
- backport 1.1.0 for remi repo.

* Sun Dec  9 2012 Shawn Iwinski <shawn.iwinski@gmail.com> 1.1.0-2
- Added php-pear(pear.doctrine-project.org/DoctrineCommon) require

* Sun Dec  9 2012 Shawn Iwinski <shawn.iwinski@gmail.com> 1.1.0-1
- Initial package
