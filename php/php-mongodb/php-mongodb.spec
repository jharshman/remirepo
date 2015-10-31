# remirepo/fedora spec file for php-mongodb
#
# Copyright (c) 2015 Remi Collet
# License: CC-BY-SA
# http://creativecommons.org/licenses/by-sa/4.0/
#
# Please, preserve the changelog entries
#
%global gh_commit    39cb5bf858b7989f16b4f1c960f08fb4349fa666
%global gh_short     %(c=%{gh_commit}; echo ${c:0:7})
%global gh_owner     mongodb
#global gh_date      20150820
%global gh_project   mongo-php-library
# Test suite not ready
# see https://github.com/mongodb/mongo-php-library/issues/41
%global with_tests   0%{?_with_tests:1}
%global psr0         MongoDB
%global prever       alpha1

Name:           php-%{gh_owner}
Version:        1.0.0
Release:        0.1.%{prever}%{?dist}
Summary:        MongoDB driver library

Group:          Development/Libraries
License:        ASL 2.0
URL:            https://github.com/%{gh_owner}/%{gh_project}
Source0:        https://github.com/%{gh_owner}/%{gh_project}/archive/%{gh_commit}/%{gh_project}-%{version}%{?prever}-%{?gh_short}.tar.gz

# Autoloader
Source1:        %{name}-autoload.php

BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch:      noarch
%if %{with_tests}
BuildRequires:  php(language) >= 5.4
BuildRequires:  php-reflection
BuildRequires:  php-spl
BuildRequires:  php-pecl(mongodb)
BuildRequires:  php-composer(phpunit/phpunit)
BuildRequires:  mongodb-server
# For autoloader
BuildRequires:  php-composer(symfony/class-loader)
%endif

# From composer.json, "require": {
#        "php": ">=5.4"
#        "ext-mongodb": "^1.0.0"
Requires:       php(language) >= 5.4
Requires:       php-pecl(mongodb)
# From phpcompatinfo report for 1.0.0alpha1
Requires:       php-reflection
Requires:       php-spl
# For autoloader
Requires:       php-composer(symfony/class-loader)

# Composer
Provides:       php-composer(%{gh_owner}/%{gh_owner}) = %{version}%{?prever}


%description
This library provides a high-level abstraction around the lower-level drivers
for PHP and HHVM (i.e. the mongodb extension).

While the extension provides a limited API for executing commands, queries,
and write operations, this library implements an API similar to that of the
legacy PHP driver. It contains abstractions for client, database, and
collection objects, and provides methods for CRUD operations and common
commands (e.g. index and collection management).

To use this library, you just have to add, in your project:
  require_once '%{_datadir}/php/%{psr0}/autoload.php';


%prep
%setup -q -n %{gh_project}-%{gh_commit}

cp %{SOURCE1} src/autoload.php


%build
# Nothing


%install
rm -rf     %{buildroot}
mkdir -p   %{buildroot}%{_datadir}/php
cp -pr src %{buildroot}%{_datadir}/php/%{psr0}


%check
%if %{with_tests}
: Run a server
mkdir dbtest
mongod \
  --journal \
  --logpath     $PWD/server.log \
  --pidfilepath $PWD/server.pid \
  --dbpath      $PWD/dbtest \
  --fork

cat << 'EOF' | tee tests/bootstrap.php
<?php
// Library
require_once '%{buildroot}%{_datadir}/php/%{psr0}/autoload.php';

// Test suite
require_once '%{_datadir}/php/Symfony/Component/ClassLoader/Psr4ClassLoader.php';
$Loader = new \Symfony\Component\ClassLoader\Psr4ClassLoader();
$Loader->addPrefix("MongoDB\\Tests\\", __DIR__);
$Loader->register();
EOF

: Run the test suite
%{_bindir}/phpunit --verbose || RET=1

: Cleanup
[ -s server.pid ] && kill $(cat server.pid)

exit $RET
%else
: Test suite disabled
%endif


%clean
rm -rf %{buildroot}


%files
%defattr(-,root,root,-)
%{!?_licensedir:%global license %%doc}
%license LICENSE
%doc composer.json
%doc README.md
%doc RELEASE-*
%doc docs
%doc examples
%{_datadir}/php/%{psr0}


%changelog
* Sat Oct 31 2015 Remi Collet <remi@fedoraproject.org> - 1.0.0-0.1.alpha1
- initial package