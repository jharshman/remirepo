Name:           FusionInventory-Agent-Task-ESX
Version:        2.1.0
Release:        1%{?dist}
Summary:        FusionInventory::Agent::Task::ESX Perl module
License:        GPL+
Group:          Development/Libraries
URL:            http://search.cpan.org/dist/FusionInventory-Agent-Task-ESX/
Source0:        http://www.cpan.org/modules/by-module/FusionInventory/FusionInventory-Agent-Task-ESX-%{version}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch:      noarch
BuildRequires:  perl >= 1:5.8.0
BuildRequires:  perl(ExtUtils::MakeMaker)
BuildRequires:  perl(JSON)
BuildRequires:  perl(Test::Exception)
BuildRequires:  perl(Test::MockModule)
BuildRequires:  perl(Test::MockObject)
Requires:       perl(JSON)
Requires:       perl(:MODULE_COMPAT_%(eval "`%{__perl} -V:version`"; echo $version))

%description
Description
-----------
This task allows the agent to perform remote inventory of ESX, ESXi,
vCenter server using the SOAP interface.

%prep
%setup -q

%build
%{__perl} Makefile.PL INSTALLDIRS=vendor
make %{?_smp_mflags}

%install
rm -rf $RPM_BUILD_ROOT

make pure_install PERL_INSTALL_ROOT=$RPM_BUILD_ROOT

find $RPM_BUILD_ROOT -type f -name .packlist -exec rm -f {} \;
find $RPM_BUILD_ROOT -depth -type d -exec rmdir {} 2>/dev/null \;

%{_fixperms} $RPM_BUILD_ROOT/*

%check
make test

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root,-)
%doc Changes fusioninventory-esx LICENSE MYMETA.json MYMETA.yml README
%{perl_vendorlib}/*
%{_mandir}/man3/*

%changelog
* Sun Apr 15 2012 http://blog.famillecollet.com 2.1.0-1
- Specfile autogenerated by cpanspec 1.78.
