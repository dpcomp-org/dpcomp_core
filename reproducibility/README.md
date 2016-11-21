# Reprozip

The execution environment can be packed into a reprozip archive and subsequently
unpacked using the steps below. Note that currently neither packing nor unpacking
can be performed under OSX or Windows. Before proceeding, please be sure to setup
your environment and perform initialization as described in the top-level README
as well as any instructions in the README files in both the plots and execution
sub-directories.

## Packing

```bash
sudo apt-get install libsqlite3-dev
pip install reprozip==1.0.6
reprozip trace python execution/sigmod2016.py run --a1 ALL --a2 ALL --x1 ALL --x2 ALL --d1 4096 --d2 "(128,128)" --s1 1000 --s2 10000 --se 2 --sd 2 --out "overall-error.json"
reprozip pack sigmod2016.rpz
cp overall-error.json error-by-size.json
cp overall-error.json error-by-shape.json
reprozip trace Rscript plots/plot.R -f overall-error.json -t main -d 1; Rscript plots/plot.R -f error-by-shape.json -t shape -d 1; Rscript plots/plot.R -f error-by-size.json -t domain_size -d 2
reprozip pack plot.rpz
```

## Unpacking

The following sequence of commands is appropriate for a debian linux environment.
It has been tested on a fresh installation of Ubuntu 14.04. To begin, launch the
host machine and copy to it the file sigmod2016.rpz.

```bash
sudo apt-get update
sudo apt-get install python-pip python-dev libffi-dev libssl-dev libsqlite3-dev
sudo pip install -U pip
sudo pip install cryptography reprounzip[all]
sudo reprounzip chroot setup sigmod2016.rpz sigmod2016
sudo reprounzip chroot setup plot.rpz plot
```

RedHat EL7 requires the following package setup before using pip.

```bash
curl "https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm" > epel-release-latest-7.noarch.rpm
sudo yum install epel-release-latest-7.noarch.rpm
sudo yum install sqlite-devel gcc libffi-devel python-devel openssl-devel
```

### Example execution

```bash
sudo reprounzip chroot run sigmod2016 --cmdline python scripts/execution/sigmod2016.py run --a1 "EFPA","AHP*" --a2 "QuadTree" --x1 "HEPTH","ADULTFRANK" --x2 "ADULT-2D" --d1 256 --d2 "(32,32)" --s1 1000 --s2 100 --se 4 --sd 4
```

Note that the result file will appear in the same folder where it did on the old files
system (which is now a subdirectory of the chroot folder).

### Cleanup

It is very important to cleanup properly if you wish to continue to use the host
operating system. If the reprozip folder is deleted without unmounting, then you
will likely wipe out the system /dev folder amoung other.

```bash
sudo reprounzip chroot destroy sigmod2016
sudo reprounzip chroot destroy plot
```
