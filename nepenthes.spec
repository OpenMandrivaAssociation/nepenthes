%define _localstatedir  %{_var}

Name:                   nepenthes
Version:                0.2.2
Release:                %mkrel 8
Epoch:                  0
Summary:                Low-interaction honeypot
Group:                  Development/Other
License:                GPL
URL:                    https://nepenthes.mwcollect.org/
Source0:                http://downloads.sourceforge.net/sourceforge/nepenthes/nepenthes-%{version}.tar.bz2
Source1:                nepenthes.init
Source2:                nepenthes.logrotate
Patch0:                 nepenthes-0.1.7-path.patch
Patch1:                 nepenthes-0.1.7-no-rpath.patch
Patch2:                 nepenthes-0.1.7-no-docs.patch
Patch3:                 nepenthes-0.2.0-curl.patch
Patch4:                 nepenthes-gcc43.diff
Patch5:                 nepenthes-0.2.2-fix-missing-include.patch
Patch6:			nepenthes-0.2.2-fix-build-gcc44.patch
Requires(post):         rpm-helper
Requires(postun):       rpm-helper
Requires(pre):          rpm-helper
Requires(preun):        rpm-helper
BuildRequires:          bison
BuildRequires:          chrpath
BuildRequires:          flex
BuildRequires:          gcc-c++
%if 0
BuildRequires:          iptables-devel
%else
BuildConflicts:         iptables-devel
%endif
BuildRequires:          adns-devel
BuildRequires:          cap-devel
BuildRequires:          curl-devel
BuildRequires:          magic-devel
BuildRequires:          mysql-devel
BuildRequires:          pcap-devel
BuildRequires:          pcre-devel
BuildRequires:          postgresql-devel
BuildRequires:          prelude-devel
BuildConflicts:         ssh-devel
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

%description
Nepenthes is a low interaction honeypot like honeyd or mwcollect. Low 
Interaction Honeypots emulate _known_ vulnerabilities to collect 
information about potential attacks. Nepenthes is designed to emulate 
vulnerabilties worms use to spread, and to capture these worms. As there 
are many possible ways for worms to spread, Nepenthes is modular. There 
are module interface to

    * resolve dns asynchronous
    * emulate vulnerabilities
    * download files
    * submit the downloaded files
    * trigger events (sounds abstract and it is abstract but is still 
      quite useful)
    * shellcode handler

%prep
%setup -q
%patch0 -p1
%patch1 -p1
%patch2 -p1
#%%patch3 -p1
%patch4 -p1
%patch5 -p1
%patch6 -p0
%{__perl} -pi -e 's|/usr/lib|%{_libdir}|g' conf/nepenthes.conf.dist
%{__perl} -pi -e 's| -Werror| -fPIC|g' `find . -type f -name Makefile.am -o -name Makefile.in`
%{_bindir}/autoreconf -i --force

%build
%serverbuild
%configure2_5x \
               --disable-ipq \
               --enable-pcap \
               --enable-debug-logging \
               --disable-ssh \
               --with-mysql-include=%{_includedir}/mysql \
               --enable-mysql \
               --with-postgre-include=%{_includedir}/pgsql \
               --enable-postgre \
               --enable-lfs \
               --enable-dnsresolve-adns \
               --enable-prelude \
               --enable-capabilities
%make

%install
%{__rm} -rf %{buildroot}
%{__mkdir_p} %{buildroot}%{_sysconfdir}/nepenthes/signatures
%{makeinstall_std}

%{__rm} -rf %{buildroot}%{_libdir}/nepenthes/*.{,l}a
%{_bindir}/chrpath -d %{buildroot}%{_libdir}/nepenthes/*.so

%{__mkdir_p} %{buildroot}%{_sbindir}
%{__mv} %{buildroot}/usr/bin/nepenthes %{buildroot}%{_sbindir}/nepenthes

%{__mkdir_p} %{buildroot}%{_logdir}/nepenthes
/bin/touch %{buildroot}%{_logdir}/{nepenthes.log,nepenthes/{logged_downloads,logged_submissions,pcap}}

%{__mkdir_p} %{buildroot}%{_var}/lib/{,nepenthes/{binaries,hexdumps}}

%{__rm} -f %{buildroot}%{_sysconfdir}/nepenthes/nepenthes.conf.dist

%{__mkdir_p} %{buildroot}%{_initrddir}
%{__install} -m 0755 %{SOURCE1} %{buildroot}%{_initrddir}/%{name}

%{__mkdir_p} %{buildroot}%{_sysconfdir}/logrotate.d
%{__cp} -a %{SOURCE2} %{buildroot}%{_sysconfdir}/logrotate.d/%{name}

%{__perl} -pi -e 's/\r$//g' doc/README.VFS

%clean
%{__rm} -rf %{buildroot}

%pre
%_pre_useradd nepenthes %{_var}/lib/nepenthes /bin/false

%preun
%_preun_service nepenthes

%post
%create_ghostfile %{_logdir}/%{name}.log root nepenthes 0660
%create_ghostfile %{_logdir}/nepenthes/logged_downloads root nepenthes 0660
%create_ghostfile %{_logdir}/nepenthes/logged_submissions root nepenthes 0660

%_post_service nepenthes

%postun
%_postun_userdel nepenthes

%files
%defattr(0644,root,root,0755)
%doc AUTHORS CHANGES COPYING INSTALL README doc/README.VFS doc/logo-shaded.svg
%attr(0755,root,root) %{_sbindir}/nepenthes
%dir %{_libdir}/nepenthes
%attr(0755,root,root) %{_libdir}/nepenthes/*.so
%{_mandir}/man8/nepenthes.8*
%dir %{_sysconfdir}/nepenthes
%config(noreplace) %{_sysconfdir}/nepenthes/*.conf
%dir %{_sysconfdir}/nepenthes/signatures
%config(noreplace) %{_sysconfdir}/nepenthes/signatures/*.sc
%attr(0755,root,root) %{_initrddir}/%{name}
%attr(0775,root,nepenthes) %{_var}/lib/nepenthes
%attr(0775,root,nepenthes) %dir %{_logdir}/nepenthes
%attr(0775,root,nepenthes) %dir %{_logdir}/nepenthes/pcap
%ghost %attr(0660,root,nepenthes) %{_logdir}/nepenthes.log
%ghost %attr(0660,root,nepenthes) %{_logdir}/nepenthes/logged_downloads
%ghost %attr(0660,root,nepenthes) %{_logdir}/nepenthes/logged_submissions
%attr(0755,nepenthes,nepenthes) %{_var}/spool/nepenthes
%config(noreplace) %attr(0644,root,root) %{_sysconfdir}/logrotate.d/%{name}
