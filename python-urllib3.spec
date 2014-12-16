%if 0%{?fedora}
%global with_python3 1
%else
%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print (get_python_lib())")}
%endif

%global srcname urllib3

Name:           python-%{srcname}
Version:        1.10
Release:        1%{?dist}
Summary:        Python HTTP library with thread-safe connection pooling and file post

License:        MIT
URL:            http://urllib3.readthedocs.org/
Source0:        http://pypi.python.org/packages/source/u/%{srcname}/%{srcname}-%{version}.tar.gz

# Remove logging-clear-handlers from setup.cfg because it's not available in RHEL6's nose
Patch100:       python-urllib3-old-nose-compat.patch

BuildArch:      noarch

Requires:       ca-certificates

# Previously bundled things:
Requires:       python-six
Requires:       python-backports-ssl_match_hostname

%if 0%{?rhel} && 0%{?rhel} <= 6
BuildRequires:  python-ordereddict
Requires:       python-ordereddict
%endif

BuildRequires:  python2-devel
# For unittests
BuildRequires:  python-nose
BuildRequires:  python-mock
BuildRequires:  python-six
BuildRequires:  python-backports-ssl_match_hostname
BuildRequires:  python-tornado

%if 0%{?with_python3}
BuildRequires:  python3-devel
# For unittests
BuildRequires:  python3-nose
BuildRequires:  python3-mock
BuildRequires:  python3-six
BuildRequires:  python3-tornado
%endif # with_python3

%description
Python HTTP module with connection pooling and file POST abilities.

%if 0%{?with_python3}
%package -n python3-%{srcname}
Requires:       ca-certificates
Requires:       python3-six
# Note: Will not run with python3 < 3.2 (unless python3-backports-ssl_match_hostname is created)
Summary:        Python3 HTTP library with thread-safe connection pooling and file post
%description -n python3-%{srcname}
Python3 HTTP module with connection pooling and file POST abilities.
%endif # with_python3


%prep
%setup -q -n %{srcname}-%{version}

%if 0%{?rhel} && 0%{?rhel} <= 6
%patch100 -p1
%endif

%if 0%{?with_python3}
rm -rf %{py3dir}
cp -a . %{py3dir}
%endif # with_python3

%build
%{__python2} setup.py build

%if 0%{?with_python3}
pushd %{py3dir}
%{__python3} setup.py build
popd
%endif # with_python3

%install
rm -rf %{buildroot}
%{__python2} setup.py install --skip-build --root %{buildroot}

rm -rf %{buildroot}/%{python2_sitelib}/urllib3/packages/six.py*
rm -rf %{buildroot}/%{python2_sitelib}/urllib3/packages/ssl_match_hostname/

mkdir -p %{buildroot}/%{python2_sitelib}/urllib3/packages/
ln -s ../../six.py %{buildroot}/%{python2_sitelib}/urllib3/packages/six.py
ln -s ../../backports/ssl_match_hostname %{buildroot}/%{python2_sitelib}/urllib3/packages/ssl_match_hostname

# Copy in six.py just for the test suite.
cp %{python2_sitelib}/six.* %{buildroot}/%{python2_sitelib}/.
cp -r %{python2_sitelib}/backports %{buildroot}/%{python2_sitelib}/.
ls -alh %{buildroot}/%{python2_sitelib}/urllib3/packages/
ls -alh %{buildroot}/%{python2_sitelib}

# dummyserver is part of the unittest framework
rm -rf %{buildroot}%{python2_sitelib}/dummyserver

%if 0%{?with_python3}
pushd %{py3dir}
%{__python3} setup.py install --skip-build --root %{buildroot}

rm -rf %{buildroot}/%{python3_sitelib}/urllib3/packages/six.py*
rm -rf %{buildroot}/%{python3_sitelib}/urllib3/packages/ssl_match_hostname/

mkdir -p %{buildroot}/%{python3_sitelib}/urllib3/packages/
ln -s ../../six.py %{buildroot}/%{python3_sitelib}/urllib3/packages/six.py

# Copy in six.py just for the test suite.
cp %{python3_sitelib}/six.* %{buildroot}/%{python3_sitelib}/.
ls -alh %{buildroot}/%{python3_sitelib}

# dummyserver is part of the unittest framework
rm -rf %{buildroot}%{python3_sitelib}/dummyserver
popd
%endif # with_python3

%check
nosetests

# And after its done, remove our copied in bits
rm -rf %{buildroot}/%{python2_sitelib}/six*
rm -rf %{buildroot}/%{python2_sitelib}/backports*

%if 0%{?with_python3}
pushd %{py3dir}
nosetests-%{python3_version}
popd

# And after its done, remove our copied in bits
rm -rf %{buildroot}/%{python3_sitelib}/six*
rm -rf %{buildroot}/%{python3_sitelib}/__pycache__*
%endif # with_python3

%files
%{!?_licensedir:%global license %%doc}
%license LICENSE.txt
%doc CHANGES.rst README.rst CONTRIBUTORS.txt
# For noarch packages: sitelib
%{python2_sitelib}/urllib3/
%{python2_sitelib}/urllib3-*.egg-info

%if 0%{?with_python3}
%files -n python3-%{srcname}
%{!?_licensedir:%global license %%doc}
%license LICENSE.txt
# For noarch packages: sitelib
%{python3_sitelib}/urllib3/
%{python3_sitelib}/urllib3-*.egg-info
%endif # with_python3

%changelog
* Sun Dec 14 2014 Ralph Bean <rbean@redhat.com> - 1.10-1
- Latest upstream 1.10, for python-requests-2.5.0.
- Re-do unbundling without patch, with symlinks.
- Modernize python2 macros.

* Wed Nov 05 2014 Ralph Bean <rbean@redhat.com> - 1.9.1-1
- Latest upstream, 1.9.1 for latest python-requests.

* Mon Aug  4 2014 Tom Callaway <spot@fedoraproject.org> - 1.8.2-4
- fix license handling

* Sun Jun 08 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.8.2-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Wed May 14 2014 Bohuslav Kabrda <bkabrda@redhat.com> - 1.8.2-2
- Rebuilt for https://fedoraproject.org/wiki/Changes/Python_3.4

* Mon Apr 21 2014 Arun S A G <sagarun@gmail.com> - 1.8.2-1
- Update to latest upstream version

* Mon Oct 28 2013 Ralph Bean <rbean@redhat.com> - 1.7.1-2
- Update patch to find ca_certs in the correct location.

* Wed Sep 25 2013 Ralph Bean <rbean@redhat.com> - 1.7.1-1
- Latest upstream with support for a new timeout class and py3.4.

* Wed Aug 28 2013 Ralph Bean <rbean@redhat.com> - 1.7-3
- Bump release again, just to push an unpaired update.

* Mon Aug 26 2013 Ralph Bean <rbean@redhat.com> - 1.7-2
- Bump release to pair an update with python-requests.

* Thu Aug 22 2013 Ralph Bean <rbean@redhat.com> - 1.7-1
- Update to latest upstream.
- Removed the accept-header proxy patch which is included in upstream now.
- Removed py2.6 compat patch which is included in upstream now.

* Sun Aug 04 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.5-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Tue Jun 11 2013 Toshio Kuratomi <toshio@fedoraproject.org> - 1.5-6
- Fix Requires of python-ordereddict to only apply to RHEL

* Fri Mar  1 2013 Toshio Kuratomi <toshio@fedoraproject.org> - 1.5-5
- Unbundling finished!

* Fri Mar 01 2013 Ralph Bean <rbean@redhat.com> - 1.5-4
- Upstream patch to fix Accept header when behind a proxy.
- Reorganize patch numbers to more clearly distinguish them.

* Wed Feb 27 2013 Ralph Bean <rbean@redhat.com> - 1.5-3
- Renamed patches to python-urllib3-*
- Fixed ssl check patch to use the correct cert path for Fedora.
- Included dependency on ca-certificates
- Cosmetic indentation changes to the .spec file.

* Tue Feb  5 2013 Toshio Kuratomi <toshio@fedoraproject.org> - 1.5-2
- python3-tornado BR and run all unittests on python3

* Mon Feb 04 2013 Toshio Kuratomi <toshio@fedoraproject.org> 1.5-1
- Initial fedora build.
