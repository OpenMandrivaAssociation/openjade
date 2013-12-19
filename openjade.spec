%define prerel	pre1
%define sgmlbase %{_datadir}/sgml
%define major	0
%define libname %mklibname %{name} %{major}
%define devname %mklibname %{name} -d

Summary:	Parser and tools for SGML + DSSSL
Name:		openjade
Version:	1.3.3
Release:	0.%{prerel}.13
License:	BSD
Group:		Publishing
Url:		http://openjade.sourceforge.net/
Source0:	http://download.sourceforge.net/openjade/%{name}-%{version}-%{prerel}.tar.bz2
# (gb) 1.3.2-12mdk libtool fixes, don't bother with either aclocal nor autoconf
# NOTE: this directly applies to configure
Patch0:		openjade-1.3.2-libtool.patch
Patch1:		openjade-gcc43.diff
Patch2:		openjade-deplibs.patch
Patch3:		openjade-ppc64.patch
Patch4:		openjade-getoptperl.patch
Patch5:		openjade-1.3.2-gcc46.patch
#Patch6:		sptrintf_long_openjade1.3.3.patch
Patch7:		openjade-nola.patch
Patch8:		openjade-1.3.3-fix-confusion-over-Char-type.patch

BuildRequires:	opensp-devel
Requires:	sgml-common
Requires:	OpenSP

%description
 Jade (James' DSSSL Engine) is an implementation of the DSSSL style
language -- Document Style Semantics and Specification Language -- 
an ISO standard for formatting SGML (and XML) documents.

%package -n %{libname}
Group:          Publishing
Summary:        Shared library files for openjade

%description -n %{libname}
Shared library files for openjade.

%package -n %{devname}
Group:          Development/C
Summary:        Development files for openjade
Requires:       %{name} = %{version}-%release
Requires:	%{libname} = %{version}-%release
Provides:       %{name}-devel
Obsoletes:	%{_lib}openjade0-devel < 1.3.3-0.pre1.11

%description -n %{devname}
Files for development from the openjade package.

%prep
%setup -qn %{name}-%{version}-%{prerel}
%apply_patches

%build
cp config/configure.in .
export CXXFLAGS="%optflags -fpermissive -DSP_MULTI_BYTE=1"
%configure2_5x \
	--enable-static \
	--enable-http \
	--enable-default-catalog=%{_sysconfdir}/sgml/catalog  \
	--enable-default-search-path=%{sgmlbase} \
	--datadir=%{sgmlbase}/%{name}-%{version} \
	--enable-splibdir=%{_libdir}

%make

%install
# NOTE: in installing I am also copying a bunch of .h files into
# $(prefix)/include/sp/{generic,include,lib}.  This is so that the
# library API can be used.  It's an ugly kludge, and the best way
# would be for James Clark to tell us what the appropriate list of
# files to be included is.

mkdir -p %{buildroot}{%{_libdir},%{_bindir},%{_includedir}/sp/generic,%{_includedir}/sp/include,%{_includedir}/sp/lib}
mkdir -p %{buildroot}%{sgmlbase}/%{name}-%{version}/{pubtext,unicode}

%makeinstall install-man datadir=%{buildroot}/%{sgmlbase}

# Why do this file gets installed here ???
rm -f %{buildroot}%{sgmlbase}/builtins.dsl

# oMy, othis ois osilly.
ln -s openjade %{buildroot}/%{_bindir}/jade
for file in nsgmls sgmlnorm spam spent sx ; do
  ln -s o$file %{buildroot}/%{_bindir}/$file
done

mv %{buildroot}%{_bindir}/sx %{buildroot}%{_bindir}/sgml2xml
install generic/*.h %{buildroot}%{_includedir}/sp/generic/
install include/*.h %{buildroot}%{_includedir}/sp/include/
cp dsssl/builtins.dsl dsssl/catalog %{buildroot}%{sgmlbase}/%{name}-%{version}/
install pubtext/* %{buildroot}%{sgmlbase}/%{name}-%{version}/pubtext
#install unicode/* %{buildroot}%{sgmlbase}/%{name}-%{version}/unicode
cp dsssl/dsssl.dtd dsssl/style-sheet.dtd dsssl/fot.dtd %{buildroot}%{sgmlbase}/%{name}-%{version}/

cd %{buildroot}%{sgmlbase}
ln -s %{name}-%{version} %{name}

ln -s %{name}-%{version}/pubtext/xml.dcl xml.dcl
ln -s %{name}-%{version}/pubtext/xml.soc xml.soc
ln -s %{name}-%{version}/pubtext/html.dcl html.dcl
ln -s %{name}-%{version}/pubtext/html.soc html.soc

mkdir -p %{buildroot}%{_sysconfdir}/sgml
touch %{buildroot}%{_sysconfdir}/sgml/dsssl-%{version}.cat \
 %{buildroot}%{_sysconfdir}/sgml/dsssl.cat \
 %{buildroot}%{_sysconfdir}/sgml/catalog

# Those are in sgml-common now
rm -f	%{buildroot}%{_datadir}/sgml/html.soc \
	%{buildroot}%{_datadir}/sgml/xml.dic \
	%{buildroot}%{_datadir}/sgml/xml.soc

# Remove unpackaged symlink
rm -rf %{buildroot}%{_datadir}/sgml/openjade

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

%files
%doc doc/ jadedoc/ dsssl/ pubtext/  README VERSION
%ghost %config(noreplace) %{_sysconfdir}/sgml/dsssl*.cat
%ghost %config(noreplace) %{_sysconfdir}/sgml/catalog
%{_bindir}/*
%{sgmlbase}/%{name}-%{version}
%{sgmlbase}/*.dcl
%{_mandir}/*/*

%files -n %{libname}
%{_libdir}/lib*.so.*

%files -n %{devname}
%{_includedir}/sp
%{_libdir}/lib*.so
%{_libdir}/lib*a

