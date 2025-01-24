%global package_speccommit da68efd6f3a3bafb066a0dd02596d9986e6750d5
%global usver 1.26.15
%global xsver 4
%global xsrel %{xsver}%{?xscount}%{?xshash}
%bcond_with tests

Name:           python-urllib3
Version:        1.26.15
Release: %{?xsrel}%{?dist}
Summary:        HTTP library with thread-safe connection pooling, file post, and more

# SPDX
License:        MIT
URL:            https://github.com/urllib3/urllib3
Source0: urllib3-1.26.15.tar.gz
Patch0: 4855d71.patch

Source1: pyproject_wheel.py

# Accomodate the test to the changed behavior of SSLContext.shared_ciphers() in CPython
# See: https://github.com/python/cpython/issues/96931

BuildArch:      noarch

BuildRequires:  python3-devel

%if 0%{?xenserver} < 9
BuildRequires:  python3-wheel
%endif

%if %{with tests}
# Test dependencies are listed only in dev-requirements.txt. Because there are
# linters and coverage tools mixed in, and exact versions are pinned, we resort
# to manual listing.
# mock==3.0.5: patched out in %%prep
# coverage~=6.0;python_version>="3.6": omitted linter/coverage tool
# tornado==6.1.0;python_version>="3.6"
BuildRequires:  %{py3_dist tornado} >= 6.1
# PySocks==1.7.1
BuildRequires:  %{py3_dist PySocks} >= 1.7.1
# win-inet-pton==1.1.0: Windows-only workaround
# pytest==6.2.4; python_version>="3.10"
BuildRequires:  %{py3_dist pytest} >= 6.2.4
# pytest-timeout==1.4.2
BuildRequires:  %{py3_dist pytest-timeout} >= 1.4.2
# pytest-freezegun==0.4.2
BuildRequires:  %{py3_dist pytest-freezegun} >= 0.4.2
# flaky==3.7.0: not really required
# trustme==0.7.0
BuildRequires:  %{py3_dist trustme} >= 0.7
# cryptography==38.0.3;python_version>="3.6": associated with the deprecated
#                                             “secure” extra
# python-dateutil==2.8.1
BuildRequires:  %{py3_dist python-dateutil} >= 2.8.1
# gcp-devrel-py-tools==0.0.16: not used in offline testing
%endif

%global _description %{expand:
urllib3 is a powerful, user-friendly HTTP client for Python. urllib3 brings
many critical features that are missing from the Python standard libraries:

  • Thread safety.
  • Connection pooling.
  • Client-side SSL/TLS verification.
  • File uploads with multipart encoding.
  • Helpers for retrying requests and dealing with HTTP redirects.
  • Support for gzip, deflate, brotli, and zstd encoding.
  • Proxy support for HTTP and SOCKS.
  • 100% test coverage.}

%description %{_description}


%package -n python3-urllib3
Summary:        %{summary}

BuildRequires:  ca-certificates
Requires:       ca-certificates

%if 0%{?xenserver} >= 9
# There has historically been a manual hard dependency on python3-idna.
BuildRequires:  %{py3_dist idna}
Requires:       %{py3_dist idna}

# Unbundled
BuildRequires:  %{py3_dist six} >= 1.16
Requires:       %{py3_dist six} >= 1.16

# There has historically been a manual hard dependency on python3-pysocks;
# since bringing it in is the sole function of python3-urllib3+socks, we just
# depend on that instead.
Requires:       python3-urllib3+socks = %{version}-%{release}
%endif

%description -n python3-urllib3 %{_description}


# We do NOT package the “secure” extra because it is deprecated; see:
# “Deprecate the pyOpenSSL TLS implementation and [secure] extra”
# https://github.com/urllib3/urllib3/issues/2680
%pyproject_extras_subpkg -n python3-urllib3 brotli socks


%prep
%autosetup -p1 -n urllib3-%{version}
# Make sure that the RECENT_DATE value doesn't get too far behind what the current date is.
# RECENT_DATE must not be older that 2 years from the build time, or else test_recent_date
# (from test/test_connection.py) would fail. However, it shouldn't be to close to the build time either,
# since a user's system time could be set to a little in the past from what build time is (because of timezones,
# corner cases, etc). As stated in the comment in src/urllib3/connection.py:
#   When updating RECENT_DATE, move it to within two years of the current date,
#   and not less than 6 months ago.
#   Example: if Today is 2018-01-01, then RECENT_DATE should be any date on or
#   after 2016-01-01 (today - 2 years) AND before 2017-07-01 (today - 6 months)
# There is also a test_ssl_wrong_system_time test (from test/with_dummyserver/test_https.py) that tests if
# user's system time isn't set as too far in the past, because it could lead to SSL verification errors.
# That is why we need RECENT_DATE to be set at most 2 years ago (or else test_ssl_wrong_system_time would
# result in false positive), but before at least 6 month ago (so this test could tolerate user's system time being
# set to some time in the past, but not to far away from the present).
# Next few lines update RECENT_DATE dynamically.
recent_date=$(date --date "7 month ago" +"%Y, %_m, %_d")
sed -i "s/^RECENT_DATE = datetime.date(.*)/RECENT_DATE = datetime.date($recent_date)/" src/urllib3/connection.py

# Use the standard library instead of a backport
sed -i -e 's/^import mock/from unittest import mock/' \
       -e 's/^from mock import /from unittest.mock import /' \
    test/*.py docs/conf.py


%if 0%{?xenserver} >= 9
%generate_buildrequires
# Generate BR’s from packaged extras even when tests are disabled, to ensure
# the extras metapackages are installable if the build succeeds.
%pyproject_buildrequires -x brotli,socks
%endif


%build
%if 0%{?xenserver} < 9
echo "from setuptools import setup

setup(name=\"%{name}\",
      version='%{version}',
     )" > ./setup.py
/usr/bin/python3 -Bs %{SOURCE1} /builddir/build /BUILD/urllib3-%{version}/pyproject-wheeldir
%else
%pyproject_wheel
%endif


%install
%if 0%{?xenserver} < 9
/usr/bin/python3 -m pip install --root %{buildroot} --prefix /usr --no-deps --disable-pip-version-check --verbose --ignore-installed --no-index --no-cache-dir --find-links /builddir/build/BUILD/urllib3-%{version}/pyproject-wheeldir
%else
%pyproject_install

# Unbundle the Python 3 build
rm -rf %{buildroot}/%{python3_sitelib}/urllib3/packages/six.py
rm -rf %{buildroot}/%{python3_sitelib}/urllib3/packages/__pycache__/six.*

mkdir -p %{buildroot}/%{python3_sitelib}/urllib3/packages/
ln -s %{python3_sitelib}/six.py %{buildroot}/%{python3_sitelib}/urllib3/packages/six.py
ln -s %{python3_sitelib}/__pycache__/six.cpython-%{python3_version_nodots}.opt-1.pyc \
      %{buildroot}/%{python3_sitelib}/urllib3/packages/__pycache__/
ln -s %{python3_sitelib}/__pycache__/six.cpython-%{python3_version_nodots}.pyc \
      %{buildroot}/%{python3_sitelib}/urllib3/packages/__pycache__/

%pyproject_save_files urllib3
%endif

%if 0%{?xenserver} < 9
# Copy source files to buildroot manually
mkdir -p %{buildroot}%{python3_sitelib}/urllib3
cp -r %{_builddir}/urllib3-%{version}/src/urllib3 %{buildroot}%{python3_sitelib}/
find %{buildroot}%{python3_sitelib}/urllib3
%endif


%if %{with tests}
%check
# Drop the dummyserver tests in koji.  They fail there in real builds, but not
# in scratch builds (weird).
ignore="${ignore-} --ignore=test/with_dummyserver/"
# Don't run the Google App Engine tests
ignore="${ignore-} --ignore=test/appengine/"
# Lots of these tests started failing, even for old versions, so it has something
# to do with Fedora in particular. They don't fail in upstream build infrastructure
ignore="${ignore-} --ignore=test/contrib/"
# Tests for Python built without SSL, but Fedora builds with SSL. These tests
# fail when combined with the unbundling of backports-ssl_match_hostname
ignore="${ignore-} --ignore=test/test_no_ssl.py"
%pytest -v ${ignore-}
%endif


%if 0%{?xenserver} < 9
%files -n python3-urllib3
%dir %{python3_sitelib}/urllib3
%dir %{python3_sitelib}/urllib3/__pycache__
%dir %{python3_sitelib}/urllib3/contrib
%dir %{python3_sitelib}/urllib3/contrib/__pycache__
%dir %{python3_sitelib}/urllib3/contrib/_securetransport
%dir %{python3_sitelib}/urllib3/contrib/_securetransport/__pycache__
%dir %{python3_sitelib}/urllib3/packages
%dir %{python3_sitelib}/urllib3/packages/__pycache__
%dir %{python3_sitelib}/urllib3/packages/backports
%dir %{python3_sitelib}/urllib3/packages/backports/__pycache__
%dir %{python3_sitelib}/urllib3/util
%dir %{python3_sitelib}/urllib3/util/__pycache__
%{python3_sitelib}/urllib3/__init__.py
%{python3_sitelib}/urllib3/__pycache__/__init__.cpython-*.pyc
%{python3_sitelib}/urllib3/__pycache__/_collections.cpython-*.pyc
%{python3_sitelib}/urllib3/__pycache__/_version.cpython-*.pyc
%{python3_sitelib}/urllib3/__pycache__/connection.cpython-*.pyc
%{python3_sitelib}/urllib3/__pycache__/connectionpool.cpython-*.pyc
%{python3_sitelib}/urllib3/__pycache__/exceptions.cpython-*.pyc
%{python3_sitelib}/urllib3/__pycache__/fields.cpython-*.pyc
%{python3_sitelib}/urllib3/__pycache__/filepost.cpython-*.pyc
%{python3_sitelib}/urllib3/__pycache__/poolmanager.cpython-*.pyc
%{python3_sitelib}/urllib3/__pycache__/request.cpython-*.pyc
%{python3_sitelib}/urllib3/__pycache__/response.cpython-*.pyc
%{python3_sitelib}/urllib3/_collections.py
%{python3_sitelib}/urllib3/_version.py
%{python3_sitelib}/urllib3/connection.py
%{python3_sitelib}/urllib3/connectionpool.py
%{python3_sitelib}/urllib3/contrib/__init__.py
%{python3_sitelib}/urllib3/contrib/__pycache__/__init__.cpython-*.pyc
%{python3_sitelib}/urllib3/contrib/__pycache__/_appengine_environ.cpython-*.pyc
%{python3_sitelib}/urllib3/contrib/__pycache__/appengine.cpython-*.pyc
%{python3_sitelib}/urllib3/contrib/__pycache__/ntlmpool.cpython-*.pyc
%{python3_sitelib}/urllib3/contrib/__pycache__/pyopenssl.cpython-*.pyc
%{python3_sitelib}/urllib3/contrib/__pycache__/securetransport.cpython-*.pyc
%{python3_sitelib}/urllib3/contrib/__pycache__/socks.cpython-*.pyc
%{python3_sitelib}/urllib3/contrib/_appengine_environ.py
%{python3_sitelib}/urllib3/contrib/_securetransport/__init__.py
%{python3_sitelib}/urllib3/contrib/_securetransport/__pycache__/__init__.cpython-*.pyc
%{python3_sitelib}/urllib3/contrib/_securetransport/__pycache__/bindings.cpython-*.pyc
%{python3_sitelib}/urllib3/contrib/_securetransport/__pycache__/low_level.cpython-*.pyc
%{python3_sitelib}/urllib3/contrib/_securetransport/bindings.py
%{python3_sitelib}/urllib3/contrib/_securetransport/low_level.py
%{python3_sitelib}/urllib3/contrib/appengine.py
%{python3_sitelib}/urllib3/contrib/ntlmpool.py
%{python3_sitelib}/urllib3/contrib/pyopenssl.py
%{python3_sitelib}/urllib3/contrib/securetransport.py
%{python3_sitelib}/urllib3/contrib/socks.py
%{python3_sitelib}/urllib3/exceptions.py
%{python3_sitelib}/urllib3/fields.py
%{python3_sitelib}/urllib3/filepost.py
%{python3_sitelib}/urllib3/packages/__init__.py
%{python3_sitelib}/urllib3/packages/__pycache__/__init__.cpython-*.pyc
%{python3_sitelib}/urllib3/packages/__pycache__/six.cpython-*.pyc
%{python3_sitelib}/urllib3/packages/backports/__init__.py
%{python3_sitelib}/urllib3/packages/backports/__pycache__/__init__.cpython-*.pyc
%{python3_sitelib}/urllib3/packages/backports/__pycache__/makefile.cpython-*.pyc
%{python3_sitelib}/urllib3/packages/backports/makefile.py
%{python3_sitelib}/urllib3/packages/six.py
%{python3_sitelib}/urllib3/poolmanager.py
%{python3_sitelib}/urllib3/request.py
%{python3_sitelib}/urllib3/response.py
%{python3_sitelib}/urllib3/util/__init__.py
%{python3_sitelib}/urllib3/util/__pycache__/__init__.cpython-*.pyc
%{python3_sitelib}/urllib3/util/__pycache__/connection.cpython-*.pyc
%{python3_sitelib}/urllib3/util/__pycache__/proxy.cpython-*.pyc
%{python3_sitelib}/urllib3/util/__pycache__/queue.cpython-*.pyc
%{python3_sitelib}/urllib3/util/__pycache__/request.cpython-*.pyc
%{python3_sitelib}/urllib3/util/__pycache__/response.cpython-*.pyc
%{python3_sitelib}/urllib3/util/__pycache__/retry.cpython-*.pyc
%{python3_sitelib}/urllib3/util/__pycache__/ssl_.cpython-*.pyc
%{python3_sitelib}/urllib3/util/__pycache__/ssl_match_hostname.cpython-*.pyc
%{python3_sitelib}/urllib3/util/__pycache__/ssltransport.cpython-*.pyc
%{python3_sitelib}/urllib3/util/__pycache__/timeout.cpython-*.pyc
%{python3_sitelib}/urllib3/util/__pycache__/url.cpython-*.pyc
%{python3_sitelib}/urllib3/util/__pycache__/wait.cpython-*.pyc
%{python3_sitelib}/urllib3/util/connection.py
%{python3_sitelib}/urllib3/util/proxy.py
%{python3_sitelib}/urllib3/util/queue.py
%{python3_sitelib}/urllib3/util/request.py
%{python3_sitelib}/urllib3/util/response.py
%{python3_sitelib}/urllib3/util/retry.py
%{python3_sitelib}/urllib3/util/ssl_.py
%{python3_sitelib}/urllib3/util/ssl_match_hostname.py
%{python3_sitelib}/urllib3/util/ssltransport.py
%{python3_sitelib}/urllib3/util/timeout.py
%{python3_sitelib}/urllib3/util/url.py
%{python3_sitelib}/urllib3/util/wait.py
%doc CHANGES.rst README.rst
%else
%files -n python3-urllib3 -f %{pyproject_files}
%doc CHANGES.rst README.rst
%endif


%changelog
* Mon Aug 19 2024 Marcus Granado <marcus.granado@cloud.com> - 1.26.15-4
- Bump release and rebuild

* Fri Aug 09 2024 Marcus Granado <marcus.granado@cloud.com> - 1.26.15-3
- Bump release and rebuild

* Fri Jul 07 2023 Tim Smith <tim.smith@citrix.com> - 1.26.15-1
- Initial import

