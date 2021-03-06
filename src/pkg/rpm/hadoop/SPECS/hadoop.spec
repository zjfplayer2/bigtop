#
# Hadoop RPM spec file
#
%define hadoop_name hadoop
%define etc_hadoop /etc/%{name}
%define config_hadoop %{etc_hadoop}/conf
%define lib_hadoop_dirname /usr/lib
%define lib_hadoop %{lib_hadoop_dirname}/%{name}
%define log_hadoop_dirname /var/log
%define log_hadoop %{log_hadoop_dirname}/%{name}
%define bin_hadoop %{_bindir}
%define man_hadoop %{_mandir}
%define doc_hadoop %{_docdir}/%{name}-%{hadoop_version}
%define src_hadoop /usr/src/%{name}
%define hadoop_username mapred
%define hadoop_services namenode secondarynamenode datanode jobtracker tasktracker
# Hadoop outputs built binaries into %{hadoop_build}
%define hadoop_build_path build
%define static_images_dir src/webapps/static/images

%ifarch i386
%global hadoop_arch Linux-i386-32
%endif
%ifarch amd64 x86_64
%global hadoop_arch Linux-amd64-64
%endif


%if  %{!?suse_version:1}0
# brp-repack-jars uses unzip to expand jar files
# Unfortunately aspectjtools-1.6.5.jar pulled by ivy contains some files and directories without any read permission
# and make whole process to fail.
# So for now brp-repack-jars is being deactivated until this is fixed.
# See CDH-2151
%define __os_install_post \
    /usr/lib/rpm/redhat/brp-compress ; \
    /usr/lib/rpm/redhat/brp-strip-static-archive %{__strip} ; \
    /usr/lib/rpm/redhat/brp-strip-comment-note %{__strip} %{__objdump} ; \
    /usr/lib/rpm/brp-python-bytecompile ; \
    %{nil}

%define alternatives_cmd alternatives

%global initd_dir %{_sysconfdir}/rc.d/init.d

%else

# Only tested on openSUSE 11.4. le'ts update it for previous release when confirmed
%if 0%{suse_version} > 1130
%define suse_check \# Define an empty suse_check for compatibility with older sles
%endif

# Deactivating symlinks checks
%define __os_install_post \
    %{suse_check} ; \
    /usr/lib/rpm/brp-compress ; \
    %{nil}

%define alternatives_cmd update-alternatives

%global initd_dir %{_sysconfdir}/rc.d

%endif


# Even though we split the RPM into arch and noarch, it still will build and install
# the entirety of hadoop. Defining this tells RPM not to fail the build
# when it notices that we didn't package most of the installed files.
%define _unpackaged_files_terminate_build 0

# RPM searches perl files for dependancies and this breaks for non packaged perl lib
# like thrift so disable this
%define _use_internal_dependency_generator 0

Name: %{hadoop_name}
Version: %{hadoop_version}
Release: %{hadoop_release}
Summary: Hadoop is a software platform for processing vast amounts of data
License: Apache License v2.0
URL: http://hadoop.apache.org/core/
Group: Development/Libraries
Source0: %{name}-%{hadoop_base_version}.tar.gz
Source1: hadoop.default
Source2: hadoop-init.tmpl
Source3: hadoop-init.tmpl.suse
Source4: hadoop.1
Source5: hadoop-fuse-dfs.1
Buildroot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires: lzo-devel, python >= 2.4, git, fuse-devel,fuse, automake, autoconf
Requires: sh-utils, textutils, /usr/sbin/useradd, /usr/sbin/usermod, /sbin/chkconfig, /sbin/service
Provides: hadoop

# RHEL6 provides natively java
%if 0%{?rhel} == 6
BuildRequires: java-1.6.0-sun-devel
Requires: java-1.6.0-sun
%else
BuildRequires: jdk >= 1.6
Requires: jre >= 1.6
%endif

%if  %{?suse_version:1}0
BuildRequires: libfuse2, libopenssl-devel, gcc-c++, ant, ant-nodeps, ant-trax
# Required for init scripts
Requires: insserv
%else
BuildRequires: fuse-libs, libtool, redhat-rpm-config
# Required for init scripts
Requires: redhat-lsb
%endif

%description
Hadoop is a software platform that lets one easily write and
run applications that process vast amounts of data.

Here's what makes Hadoop especially useful:
* Scalable: Hadoop can reliably store and process petabytes.
* Economical: It distributes the data and processing across clusters
              of commonly available computers. These clusters can number
              into the thousands of nodes.
* Efficient: By distributing the data, Hadoop can process it in parallel
             on the nodes where the data is located. This makes it
             extremely rapid.
* Reliable: Hadoop automatically maintains multiple copies of data and
            automatically redeploys computing tasks based on failures.

Hadoop implements MapReduce, using the Hadoop Distributed File System (HDFS).
MapReduce divides applications into many small blocks of work. HDFS creates
multiple replicas of data blocks for reliability, placing them on compute
nodes around the cluster. MapReduce can then process the data where it is
located.


%package namenode
Summary: The Hadoop namenode manages the block locations of HDFS files
Group: System/Daemons
Requires: %{name} = %{version}-%{release}

%description namenode
The Hadoop Distributed Filesystem (HDFS) requires one unique server, the
namenode, which manages the block locations of files on the filesystem.


%package secondarynamenode
Summary: Hadoop Secondary namenode
Group: System/Daemons
Requires: %{name} = %{version}-%{release}

%description secondarynamenode
The Secondary Name Node periodically compacts the Name Node EditLog
into a checkpoint.  This compaction ensures that Name Node restarts
do not incur unnecessary downtime.


%package jobtracker
Summary: Hadoop Job Tracker
Group: System/Daemons
Requires: %{name} = %{version}-%{release}

%description jobtracker
The jobtracker is a central service which is responsible for managing
the tasktracker services running on all nodes in a Hadoop Cluster.
The jobtracker allocates work to the tasktracker nearest to the data
with an available work slot.


%package datanode
Summary: Hadoop Data Node
Group: System/Daemons
Requires: %{name} = %{version}-%{release}

%description datanode
The Data Nodes in the Hadoop Cluster are responsible for serving up
blocks of data over the network to Hadoop Distributed Filesystem
(HDFS) clients.


%package tasktracker
Summary: Hadoop Task Tracker
Group: System/Daemons
Requires: %{name} = %{version}-%{release}

%description tasktracker
The tasktracker has a fixed number of work slots.  The jobtracker
assigns MapReduce work to the tasktracker that is nearest the data
with an available work slot.


%package conf-pseudo
Summary: Hadoop installation in pseudo-distributed mode
Group: System/Daemons
Requires: %{name} = %{version}-%{release}, %{name}-namenode = %{version}-%{release}, %{name}-datanode = %{version}-%{release}, %{name}-secondarynamenode = %{version}-%{release}, %{name}-tasktracker = %{version}-%{release}, %{name}-jobtracker = %{version}-%{release}

%description conf-pseudo
Installation of this RPM will setup your machine to run in pseudo-distributed mode
where each Hadoop daemon runs in a separate Java process.

%package doc
Summary: Hadoop Documentation
Group: Documentation
Obsoletes: %{name}-docs
%description doc
Documentation for Hadoop

%package source
Summary: Source code for Hadoop
Group: System/Daemons
AutoReq: no

%description source
The Java source code for Hadoop and its contributed packages. This is handy when
trying to debug programs that depend on Hadoop.

#%package fuse
#Summary: Mountable HDFS
#Group: Development/Libraries
#Requires: %{name} = %{version}-%{release}, fuse
#AutoReq: no
#
#%if  %{?suse_version:1}0
#Requires: libfuse2
#%else
#Requires: fuse-libs
#%endif
#
#
#%description fuse
#These projects (enumerated below) allow HDFS to be mounted (on most flavors of Unix) as a standard file system using the mount command. Once mounted, the user can operate on an instance of hdfs using standard Unix utilities such as 'ls', 'cd', 'cp', 'mkdir', 'find', 'grep', or use standard Posix libraries like open, write, read, close from C, C++, Python, Ruby, Perl, Java, bash, etc.

%package native
Summary: Native libraries for Hadoop Compression
Group: Development/Libraries
Requires: %{name} = %{version}-%{release}
AutoReq: no

%description native
Native libraries for Hadoop compression

%package libhdfs
Summary: Hadoop Filesystem Library
Group: Development/Libraries
Requires: %{name} = %{version}-%{release}
# TODO: reconcile libjvm
AutoReq: no

# RHEL6 provides natively java
%if 0%{?rhel} == 6
BuildRequires: java-1.6.0-sun-devel
Requires: java-1.6.0-sun
%else
BuildRequires: jdk >= 1.6
Requires: jre >= 1.6
%endif

%description libhdfs
Hadoop Filesystem Library

%package pipes
Summary: Hadoop Pipes Library
Group: Development/Libraries
Requires: %{name} = %{version}-%{release}

%description pipes
Hadoop Pipes Library


%prep
%setup -n %{name}-%{hadoop_base_version}

%build
# This assumes that you installed Java JDK 6 via RPM
# This assumes that you installed Java JDK 5 i386 via RPM
# This assumes that you installed Forrest and set FORREST_HOME

ant -Dversion=%{version} \
    -Djava5.home=$JAVA5_HOME \
    -Dforrest.home=$FORREST_HOME \
    -Dcompile.native=true \
	 -Dhadoop.conf.dir=/etc/hadoop/conf \
	 -Dlibhdfs=1 \
	 -Dcompile.c++=true \
	 -Djdiff.build.dir=build/docs/jdiff-cloudera \
	 api-report bin-package compile-contrib package

%clean
%__rm -rf $RPM_BUILD_ROOT

#########################
#### INSTALL SECTION ####
#########################
%install
%__rm -rf $RPM_BUILD_ROOT

%__install -d -m 0755 $RPM_BUILD_ROOT/%{lib_hadoop}

bash $RPM_SOURCE_DIR/install_hadoop.sh \
  --distro-dir=$RPM_SOURCE_DIR \
  --build-dir=$PWD/build/%{name}-%{version} \
  --src-dir=$RPM_BUILD_ROOT%{src_hadoop} \
  --lib-dir=$RPM_BUILD_ROOT%{lib_hadoop} \
  --system-lib-dir=%{_libdir} \
  --etc-dir=$RPM_BUILD_ROOT%{etc_hadoop} \
  --prefix=$RPM_BUILD_ROOT \
  --doc-dir=$RPM_BUILD_ROOT%{doc_hadoop} \
  --example-dir=$RPM_BUILD_ROOT%{doc_hadoop}/examples \
  --native-build-string=%{hadoop_arch} \
  --installed-lib-dir=%{lib_hadoop} \
  --man-dir=$RPM_BUILD_ROOT%{man_hadoop} \


# Init.d scripts
%__install -d -m 0755 $RPM_BUILD_ROOT/%{initd_dir}/


%if  %{?suse_version:1}0
orig_init_file=$RPM_SOURCE_DIR/hadoop-init.tmpl.suse
%else
orig_init_file=$RPM_SOURCE_DIR/hadoop-init.tmpl
%endif

# Generate the init.d scripts
for service in %{hadoop_services}
do
       init_file=$RPM_BUILD_ROOT/%{initd_dir}/%{name}-${service}
       %__cp $orig_init_file $init_file
       %__sed -i -e 's|@HADOOP_COMMON_ROOT@|%{lib_hadoop}|' $init_file
       %__sed -i -e "s|@HADOOP_DAEMON@|${service}|" $init_file
       %__sed -i -e 's|@HADOOP_CONF_DIR@|%{config_hadoop}|' $init_file


       case "$service" in
         hadoop_services|namenode|secondarynamenode|datanode)
             %__sed -i -e 's|@HADOOP_DAEMON_USER@|hdfs|' $init_file
             ;;
         jobtracker|tasktracker)
             %__sed -i -e 's|@HADOOP_DAEMON_USER@|mapred|' $init_file
             ;;
       esac

       chmod 755 $init_file
done
%__install -d -m 0755 $RPM_BUILD_ROOT/etc/default
%__cp $RPM_SOURCE_DIR/hadoop.default $RPM_BUILD_ROOT/etc/default/hadoop


# /var/lib/hadoop/cache
%__install -d -m 1777 $RPM_BUILD_ROOT/var/lib/%{name}/cache
# /var/log/hadoop
%__install -d -m 0755 $RPM_BUILD_ROOT/var/log
%__install -d -m 0775 $RPM_BUILD_ROOT/var/run/%{name}
%__install -d -m 0775 $RPM_BUILD_ROOT/%{log_hadoop}


%pre
getent group hadoop >/dev/null || groupadd -r hadoop
getent group hdfs >/dev/null   || groupadd -r hdfs
getent group mapred >/dev/null || groupadd -r mapred

getent passwd mapred >/dev/null || /usr/sbin/useradd --comment "Hadoop MapReduce" --shell /bin/bash -M -r -g mapred -G hadoop --home %{lib_hadoop} mapred

# Create an hdfs user if one does not already exist.
getent passwd hdfs >/dev/null || /usr/sbin/useradd --comment "Hadoop HDFS" --shell /bin/bash -M -r -g hdfs -G hadoop --home %{lib_hadoop} hdfs


%post
%{alternatives_cmd} --install %{config_hadoop} %{name}-conf %{etc_hadoop}/conf.empty 10
%{alternatives_cmd} --install %{bin_hadoop}/%{hadoop_name} %{hadoop_name}-default %{bin_hadoop}/%{name} 20 \
  --slave %{log_hadoop_dirname}/%{hadoop_name} %{hadoop_name}-log %{log_hadoop} \
  --slave %{lib_hadoop_dirname}/%{hadoop_name} %{hadoop_name}-lib %{lib_hadoop} \
  --slave /etc/%{hadoop_name} %{hadoop_name}-etc %{etc_hadoop} \
  --slave %{man_hadoop}/man1/%{hadoop_name}.1.gz %{hadoop_name}-man %{man_hadoop}/man1/%{name}.1.gz


%preun
if [ "$1" = 0 ]; then
  # Stop any services that might be running
  for service in %{hadoop_services}
  do
     service hadoop-$service stop 1>/dev/null 2>/dev/null || :
  done
  %{alternatives_cmd} --remove %{name}-conf %{etc_hadoop}/conf.empty
  %{alternatives_cmd} --remove %{hadoop_name}-default %{bin_hadoop}/%{name}
fi

%files
%defattr(-,root,root)
%config %{etc_hadoop}/conf.empty
/etc/default/hadoop
%{lib_hadoop}
%{bin_hadoop}/%{name}
%{man_hadoop}/man1/hadoop.1.gz
%attr(0775,root,hadoop) /var/run/%{name}
%attr(0775,root,hadoop) %{log_hadoop}

%files doc
%defattr(-,root,root)
%doc %{doc_hadoop}

%files source
%defattr(-,root,root)
%{src_hadoop}



# Service file management RPMs
%define service_macro() \
%files %1 \
%defattr(-,root,root) \
%{initd_dir}/%{name}-%1 \
%{lib_hadoop}/bin/hadoop-daemon.sh \
%post %1 \
chkconfig --add %{name}-%1 \
\
%preun %1 \
if [ "$1" = 0 ]; then \
  service %{name}-%1 stop > /dev/null \
  chkconfig --del %{name}-%1 \
fi
%service_macro namenode
%service_macro secondarynamenode
%service_macro datanode
%service_macro jobtracker
%service_macro tasktracker

# Pseudo-distributed Hadoop installation
%post conf-pseudo
%{alternatives_cmd} --install %{config_hadoop} %{name}-conf %{etc_hadoop}/conf.pseudo 30

if [ ! -e %{etc_hadoop}/conf ]; then
  ln -s %{etc_hadoop}/conf.pseudo %{etc_hadoop}/conf
fi

nn_dfs_dir="/var/lib/%{name}/cache/hadoop/dfs"
if [ -z "$(ls -A $nn_dfs_dir 2>/dev/null)" ]; then
   HADOOP_NAMENODE_USER=hdfs hadoop --config %{etc_hadoop}/conf.pseudo namenode -format 2>/dev/null 1>/dev/null || :
fi

%files conf-pseudo
%defattr(-,root,root)
%config %attr(755,root,root) %{etc_hadoop}/conf.pseudo
%dir %attr(0755,root,hadoop) /var/lib/%{name}
%dir %attr(1777,root,hadoop) /var/lib/%{name}/cache

%preun conf-pseudo
if [ "$1" = 0 ]; then
        %{alternatives_cmd} --remove %{name}-conf %{etc_hadoop}/conf.pseudo
        rm -f %{etc_hadoop}/conf
fi

%files native
%defattr(-,root,root)
%{lib_hadoop}/lib/native

#%files fuse
#%defattr(-,root,root)
#%attr(0755,root,root) %{bin_hadoop}/hadoop-fuse-dfs
#%attr(0755,root,root) %{man_hadoop}/man1/hadoop-fuse-dfs.1.gz

%files pipes
%defattr(-,root,root)
%{_libdir}/libhadooppipes*
%{_libdir}/libhadooputil*
%{_includedir}/hadoop/*

%files libhdfs
%defattr(-,root,root)
%{_libdir}/libhdfs*
%{_includedir}/hdfs.h
# -devel should be its own package
%doc %{_docdir}/libhdfs-devel

