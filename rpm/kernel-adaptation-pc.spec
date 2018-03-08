Name:       kernel-adaptation-pc

%define kernel_version_build %{version}-%{release}
%define kernel_devel_dir %{_prefix}/src/kernels/%{kernel_version_build}
%define kernel_version %{version}
%define kernel_arch x86

Summary:    Kernel Adaptation PC
Version:    3.6.11
Release:    8
Group:      Kernel/Linux Kernel
License:    GPLv2
Source0:    %{name}-%{version}.tar.bz2
Requires(pre): kmod
Requires(pre): mkinitrd >= 6.0.39-1
BuildRequires:  pkgconfig(ncurses)
Provides:   kernel = %{kernel_version}

%description
Kernel for PC.

%package devel
Summary:    Devel files for PC kernel
Group:      Development/System
Requires:   %{name} = %{version}-%{release}
Provides:   kernel-devel = %{kernel_version}

%description devel
Devel for PC kernel

%prep
%setup -q -n %{name}-%{version}

%build
# These have been installed in kernel/arch/*/configs/
make %{_arch}_sailfish_defconfig

# Verify the config meets the current Mer requirements
#/usr/bin/mer_verify_config .config

perl -p -i -e "s/^EXTRAVERSION.*/EXTRAVERSION = -%{release}/" Makefile
make %{?_smp_mflags} bzImage
make %{?_smp_mflags} modules

%install
rm -rf %{buildroot}

# Modules
make INSTALL_MOD_PATH=%{buildroot} modules_install
mkdir -p %{buildroot}/lib/modules/%{kernel_version_build}/
touch %{buildroot}/lib/modules/%{kernel_version_build}/modules.dep
find %{buildroot}/lib/modules/%{kernel_version_build} -name "*.ko" -type f -exec chmod u+x {} \;

# /boot
mkdir -p %{buildroot}/boot/

install -m 755 arch/%{kernel_arch}/boot/bzImage %{buildroot}/boot/vmlinuz-%{kernel_version_build}

install -m 755 .config %{buildroot}/boot/config-%{kernel_version_build}
install -m 755 System.map %{buildroot}/boot/
install -m 755 System.map %{buildroot}/boot/System.map-%{kernel_version_build}

# And save the headers/makefiles etc for building modules against
#
# This all looks scary, but the end result is supposed to be:
# * all arch relevant include/ files
# * all Makefile/Kconfig files
# * all script/ files

mkdir -p %{buildroot}/%{kernel_devel_dir}

# dirs for additional modules per module-init-tools, kbuild/modules.txt
# first copy everything
cp --parents `find  -type f -name "Makefile*" -o -name "Kconfig*"` %{buildroot}/%{kernel_devel_dir}
cp Module.symvers %{buildroot}/%{kernel_devel_dir}
cp System.map %{buildroot}/%{kernel_devel_dir}
if [ -s Module.markers ]; then
cp Module.markers %{buildroot}/%{kernel_devel_dir}
fi
# then drop all but the needed Makefiles/Kconfig files
rm -rf %{buildroot}/%{kernel_devel_dir}/Documentation
rm -rf %{buildroot}/%{kernel_devel_dir}/scripts
rm -rf %{buildroot}/%{kernel_devel_dir}/include

# Copy all scripts
cp .config %{buildroot}/%{kernel_devel_dir}
cp -a scripts %{buildroot}/%{kernel_devel_dir}
if [ -d arch/%{karch}/scripts ]; then
cp -a arch/%{kernel_arch}/scripts %{buildroot}/%{kernel_devel_dir}/arch/%{kernel_arch}
fi
# FIXME - what's this trying to do ... if *lds expands to multiple files the -f test will fail.
if [ -f arch/%{karch}/*lds ]; then
cp -a arch/%{kernel_arch}/*lds %{buildroot}/%{kernel_devel_dir}/arch/%{kernel_arch}/
fi
# Clean any .o files from the 'scripts'
find %{buildroot}/%{kernel_devel_dir}/scripts/ -name \*.o -print0 | xargs -0 rm -f

# arch-specific include files
cp -a --parents arch/%{kernel_arch}/include %{buildroot}/%{kernel_devel_dir}

# normal include files
mkdir -p %{buildroot}/%{kernel_devel_dir}/include

# copy only include/* directories
cp -a $(find include -mindepth 1 -maxdepth 1 -type d) %{buildroot}/%{kernel_devel_dir}/include

# Make sure the Makefile and version.h have a matching timestamp so that
# external modules can be built. Also .conf
touch -r %{buildroot}/%{kernel_devel_dir}/Makefile %{buildroot}/%{kernel_devel_dir}/include/linux/version.h
touch -r %{buildroot}/%{kernel_devel_dir}/.config %{buildroot}/%{kernel_devel_dir}/include/linux/autoconf.h

# Copy .config to include/config/auto.conf so "make prepare" is unnecessary.
cp %{buildroot}/%{kernel_devel_dir}/.config %{buildroot}/%{kernel_devel_dir}/include/config/auto.conf

%post
depmod -a %{kernel_version_build} || :
/sbin/new-kernel-pkg --package kernel-adaptation-pc --mkinitrd --depmod --install %{kernel_version_build} || exit $?\

%files
%defattr(-,root,root,-)
/lib/modules/%{kernel_version_build}/*
/boot/System.map-%{kernel_version_build}
/boot/config-%{kernel_version_build}
# do we need this? should it be versioned only for x86
/boot/System.map
/boot/vmlinuz-%{kernel_version_build}
/lib/firmware/*

%files devel
%defattr(-,root,root,-)
/%{_prefix}/src/kernels/%{kernel_version_build}/*
/%{_prefix}/src/kernels/%{kernel_version_build}/.config
