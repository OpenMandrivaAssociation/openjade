%define name openjade
%define version 1.3.3
%define prerel pre1
%define release %mkrel 0.%prerel.4
%define sgmlbase %{_datadir}/sgml
%define major 0
%define libname %mklibname %{name} %{major}
%define libnamedev %mklibname %{name} %{major} -d

Summary: Parser and tools for SGML + DSSSL
Name: %{name}
Version: %{version}
Release: %{release}
Url: http://openjade.sourceforge.net/
Source: http://download.sourceforge.net/openjade/openjade-%{version}-%prerel.tar.bz2
# (gb) 1.3.2-12mdk libtool fixes, don't bother with either aclocal nor autoconf
# NOTE: this directly applies to configure
Patch0: openjade-1.3.2-libtool.patch

License: BSD
Group: Publishing
BuildRoot: %{_tmppath}/%{name}-buildroot
Obsoletes: jade
Provides: jade = %version-%release
Requires: sgml-common >= 0.6.3-8mdk, %libname = %version-%release
BuildRequires: OpenSP-devel
Requires: OpenSP

%description
 Jade (James' DSSSL Engine) is an implementation of the DSSSL style
language -- Document Style Semantics and Specification Language -- 
an ISO standard for formatting SGML (and XML) documents.

%package -n %libname
Group:          Publishing
Summary:        Shared library files for openjade

%description -n %libname
Shared library files for openjade.

%package -n %libnamedev
Group:          Development/C
Summary:        Development files for openjade
Requires:       %name = %version-%release, %libname = %version-%release
Provides:       lib%{name}-devel, openjade-devel

%description -n %libnamedev
Files for development from the openjade package.


%prep

%setup -q -n %name-%version-%prerel
%patch0 -p1 -b .libtool

%build
cp config/configure.in .
%configure2_5x --enable-static --enable-http \
 --enable-default-catalog=%{_sysconfdir}/sgml/catalog  \
 --enable-default-search-path=%{sgmlbase} \
 --datadir=%{sgmlbase}/%{name}-%{version}

%make

%install
# NOTE: in installing I am also copying a bunch of .h files into
# $(prefix)/include/sp/{generic,include,lib}.  This is so that the
# library API can be used.  It's an ugly kludge, and the best way
# would be for James Clark to tell us what the appropriate list of
# files to be included is.

[ -n "$RPM_BUILD_ROOT" -a "$RPM_BUILD_ROOT" != / ] && rm -rf $RPM_BUILD_ROOT

mkdir -p $RPM_BUILD_ROOT{%{_libdir},%{_bindir},%{_includedir}/sp/generic,%{_includedir}/sp/include,%{_includedir}/sp/lib}
mkdir -p $RPM_BUILD_ROOT%{sgmlbase}/%{name}-%{version}/{pubtext,unicode}

%makeinstall install-man datadir=$RPM_BUILD_ROOT/%{sgmlbase}

# Why do this file gets installed here ???
rm -f $RPM_BUILD_ROOT%{sgmlbase}/builtins.dsl

# oMy, othis ois osilly.
ln -s openjade $RPM_BUILD_ROOT/%{_bindir}/jade
for file in nsgmls sgmlnorm spam spent sx ; do
  ln -s o$file $RPM_BUILD_ROOT/%{_bindir}/$file
done

mv $RPM_BUILD_ROOT%{_bindir}/sx $RPM_BUILD_ROOT%{_bindir}/sgml2xml
install generic/*.h $RPM_BUILD_ROOT%{_includedir}/sp/generic/
install include/*.h $RPM_BUILD_ROOT%{_includedir}/sp/include/
cp dsssl/builtins.dsl dsssl/catalog $RPM_BUILD_ROOT%{sgmlbase}/%{name}-%{version}/
install pubtext/* $RPM_BUILD_ROOT%{sgmlbase}/%{name}-%{version}/pubtext
#install unicode/* $RPM_BUILD_ROOT%{sgmlbase}/%{name}-%{version}/unicode
cp dsssl/dsssl.dtd dsssl/style-sheet.dtd dsssl/fot.dtd $RPM_BUILD_ROOT%{sgmlbase}/%{name}-%{version}/

cd $RPM_BUILD_ROOT%{sgmlbase}
ln -s %{name}-%{version} %{name}

ln -s %{name}-%{version}/pubtext/xml.dcl xml.dcl
ln -s %{name}-%{version}/pubtext/xml.soc xml.soc
ln -s %{name}-%{version}/pubtext/html.dcl html.dcl
ln -s %{name}-%{version}/pubtext/html.soc html.soc

mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/sgml
touch $RPM_BUILD_ROOT%{_sysconfdir}/sgml/dsssl-%{version}.cat \
 $RPM_BUILD_ROOT%{_sysconfdir}/sgml/dsssl.cat \
 $RPM_BUILD_ROOT%{_sysconfdir}/sgml/catalog

# Remove unpackaged symlink
rm -rf ${RPM_BUILD_ROOT}%{_datadir}/sgml/openjade

%post

# remove openjade-1.3 catalog if referenced
bads=`find %{_sysconfdir}/sgml -type f -exec grep -l %{name}-1.3 {} \;`
for f in $bads; do 
	%{_bindir}/xmlcatalog --sgml --noout --del $f %{sgmlbase}/%{name}-1.3/catalog;
done
if [ -e %{_sysconfdir}/sgml/catalog ] && [ "$(grep 'sgml-docbook-*.cat' %{_sysconfdir}/sgml/catalog)" != "" ]; then \
%{_bindir}/xmlcatalog --sgml --noout --del %{_sysconfdir}/sgml/catalog '%{_sysconfdir}/sgml/sgml-docbook-*.cat'; fi

# Add new catalogs
touch %{_sysconfdir}/sgml/dsssl-%{version}.cat
for i in %{_sysconfdir}/sgml/dsssl-%{version}.cat %{_sysconfdir}/sgml/{x,sg}ml-docbook-*.cat; do
  [ -e $i ] && %{_bindir}/xmlcatalog --sgml --noout --add \
  	$i %{sgmlbase}/%{name}/catalog
done
ln -s -f %{_sysconfdir}/sgml/dsssl-%{version}.cat %{_sysconfdir}/sgml/dsssl.cat

%pre
cd %{sgmlbase}
if [ -L %{name} ]; then
 rm -f %{name}
fi
ln -sf %{name}-%{version} %{name}

%triggerpostun -- openjade <= 1.3.1-6mdk
# we are in the obligation to use a triggerpostun because we have
# to be sure that the files from the old package are removed else
# rpm will remove all the files in /usr/share/sgml.
# Fred [Wed May 15 11:15:42 2002]
if [ ! -L %{sgmlbase}/%{name} ]; then
	cd %{sgmlbase}
	rm -rf %{name}
	ln -sf %{name}-%{version} %{name}
fi


%postun
# Do not remove if upgrade
if [ "$1" = "0" ]; then 
  if [ -x %{_bindir}/xmlcatalog ]; then
    for i in %{_sysconfdir}/sgml/dsssl-%{version}.cat %{_sysconfdir}/sgml/sgml-docbook-*.cat %{_sysconfdir}/sgml/xml-docbook-*.cat; do
        [ -e $i ] && %{_bindir}/xmlcatalog --sgml --noout --del \
		  $i %{sgmlbase}/%{name}/catalog
    done
  fi
    rm -f %{_sysconfdir}/sgml/dsssl.cat %{sgmlbase}/%{name}
# Is it last docbook catalog?
    if [ ! -e %{_sysconfdir}/sgml/dsssl-%{version}.cat ]; then 
	rm -f %{_sysconfdir}/sgml/sgml-docbook.cat
	OTHERCAT=`ls %{_sysconfdir}/sgml/dsssl-?.?.cat 2> /dev/null | head --lines 1`
	if [ -n "$OTHERCAT" ]; then ln -sf $OTHERCAT %{_sysconfdir}/sgml/dsssl.cat; fi
    fi
fi


%post   -p /sbin/ldconfig -n %libname
%postun -p /sbin/ldconfig -n %libname

%clean 
rm -rf $RPM_BUILD_ROOT 

%files
%defattr(-,root,root)
%doc doc/ jadedoc/ dsssl/ pubtext/  README VERSION
%ghost %config(noreplace) %{_sysconfdir}/sgml/dsssl*.cat
%ghost %config(noreplace) %{_sysconfdir}/sgml/catalog
%{_bindir}/*
%{sgmlbase}/%{name}-%{version}
%{sgmlbase}/*.dcl
%{sgmlbase}/*.soc
%{_mandir}/*/*

%files -n %libname
%defattr(-,root,root)
%{_libdir}/lib*.so.*

%files -n %libnamedev
%defattr(-,root,root)
%{_includedir}/sp
%{_libdir}/lib*.so
%{_libdir}/lib*a
