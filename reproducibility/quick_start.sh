# download reprozip files

mkdir reprozip
cd reprozip
wget "http://dpcomp-reproducibility.s3.amazonaws.com/sigmod2016.rpz?AWSAccessKeyId=AKIAJH5R657YMTEADPFA&Expires=1487083527&Signature=JEFvC1xZMdZ7v4mQOtVRmeBkYEQ%3D"
mv sigmod2016* sigmod2016.rpz
wget "http://dpcomp-reproducibility.s3.amazonaws.com/plot.rpz?AWSAccessKeyId=AKIAJH5R657YMTEADPFA&Expires=1487058535&Signature=%2FbxtWUdz3vGLKhK0STzNtMaTTZw%3D"
mv plot* plot.rpz

# unpack reprozip files

sudo reprounzip chroot setup sigmod2016.rpz sigmod2016
sudo reprounzip chroot setup plot.rpz plot

# generate experimental results

sudo reprounzip chroot run sigmod2016 --cmdline python execution/sigmod2016.py run --a1 "HB","Identity","DAWA" \
    --a2 "HB","Identity","DAWA" \
    --x1 'HEPTH','ADULTFRANK' \
    --x2 'SF-CABS-E','SF-CABS-S' \
    --d1 4096 --d2 "(128,128)" \
    --s1 1000,100000 --s2 10000,1000000 \
    --se 5 --sd 5 --out "overall-error.json"
cp sigmod2016/root/home/ubuntu/Documents/dpcomp-core/reproducibility/overall-error.json .

sudo reprounzip chroot run sigmod2016 --cmdline python execution/sigmod2016.py run --a1 "HB","Identity","DAWA" \
    --a2 "DAWA","HB" \
    --x1 'ADULTFRANK','INCOME','MDSALARY-FA','MDSALARY','NETTRACE','MEDCOST','LC-REQ-F1' \
    --x2 'SF-CABS-E','SF-CABS-S','BEIJING-CABS-E','BEIJING-CABS-S' \
    --d1 4096 --d2 "(128,128)" \
    --s1 1000 --s2 10000 \
    --se 5 --sd 5 --out "error-by-shape.json"
cp sigmod2016/root/home/ubuntu/Documents/dpcomp-core/reproducibility/error-by-shape.json .

sudo reprounzip chroot run sigmod2016 --cmdline python execution/sigmod2016.py run --a1 "Identity" \
    --a2 "DAWA","HB" \
    --x1 'HEPTH' \
    --x2 'BEIJING-CABS-E','ADULT-2D' \
    --d1 128 --d2 "(64,64)","(32,32)" \
    --s1 1000 --s2 10000,1000000 \
    --se 5 --sd 5 --out "error-by-size.json"
cp sigmod2016/root/home/ubuntu/Documents/dpcomp-core/reproducibility/error-by-size.json .

# generate figures
cp overall-error.json plot/root/home/ubuntu/Documents/dpcomp-core/reproducibility
sudo reprounzip chroot run plot --cmdline Rscript plots/plot.R -f overall-error.json -o figure_1a.pdf -t main -d 1 -q
cp plot/root/home/ubuntu/Documents/dpcomp-core/reproducibility/figure_1a.pdf .
sudo reprounzip chroot run plot --cmdline Rscript plots/plot.R -f overall-error.json -o figure_1b.pdf -t main -d 2 -q
cp plot/root/home/ubuntu/Documents/dpcomp-core/reproducibility/figure_1b.pdf .

cp error-by-shape.json plot/root/home/ubuntu/Documents/dpcomp-core/reproducibility
sudo reprounzip chroot run plot --cmdline Rscript plots/plot.R -f error-by-shape.json -o figure_2a.pdf -t shape -d 1
cp plot/root/home/ubuntu/Documents/dpcomp-core/reproducibility/figure_2a.pdf .
sudo reprounzip chroot run plot --cmdline Rscript plots/plot.R -f error-by-shape.json -o figure_2b.pdf -t shape -d 2
cp plot/root/home/ubuntu/Documents/dpcomp-core/reproducibility/figure_2b.pdf .

cp error-by-size.json plot/root/home/ubuntu/Documents/dpcomp-core/reproducibility
sudo reprounzip chroot run plot --cmdline Rscript plots/plot.R -f error-by-size.json -o figure_2c.pdf -t domain_size
cp plot/root/home/ubuntu/Documents/dpcomp-core/reproducibility/figure_2c.pdf .

# cleanup reprozip chroot folders

sudo reprounzip chroot destroy sigmod2016
sudo reprounzip chroot destroy plot
