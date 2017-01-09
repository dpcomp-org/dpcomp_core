#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <ctime>
#include "mtrand.h"

//////////////////////////////////////
// auxilary functions 
inline int sgn(double x) {
    if ( x>0 ) return 1;
    if ( x==0 ) return 0;
    return -1;
}

inline double dabs(double x)    {
    return (x<0)?-x:x;
}
// end of auxilary functions
//////////////////////////////////////

//////////////////////////////////////
// tree heap operations
const double err_tolerance = 1E-8;

struct node  {
    int count;
    double key;
    int fix;
    double sum;
    node *left, *right;
    node(double _k) : count(1), key(_k), fix(rand()), sum(_k) { left=right=0; }
};

struct res  {
    int lct, rct;
    double lsum, rsum;
    res() : lct(0), rct(0), lsum(0), rsum(0) {}
};

void left_rot(node *&x) {
    node *y = x->right;
    if ( y == 0 ) return;
    x->right = y->left;
    y->left = x;
    x = y;

    x->count = 1;
    x->sum = x->key;
    y = x->left;
    if ( y!= 0 ) {
        y->count = 1;
        y->sum = y->key;
        if ( y->left != 0 )    {
            y->count += y->left->count;
            y->sum += y->left->sum;
        }
        if ( y->right != 0 )    {
            y->count += y->right->count;
            y->sum += y->right->sum;
        }
        x->count += y->count;
        x->sum += y->sum;
    }
    if ( x->right != 0 )    {
        x->count += x->right->count;
        x->sum += x->right->sum;
    }
}

void right_rot(node *&x) {
    node *y = x->left;
    if ( y == 0 ) return;
    x->left = y->right;
    y->right = x;
    x = y;

    x->count = 1;
    x->sum = x->key;
    y = x->right;
    if ( y!= 0 ) {
        y->count = 1;
        y->sum = y->key;
        if ( y->left != 0 )    {
            y->count += y->left->count;
            y->sum += y->left->sum;
        }
        if ( y->right != 0 )    {
            y->count += y->right->count;
            y->sum += y->right->sum;
        }
        x->count += y->count;
        x->sum += y->sum;
    }
    if ( x->left != 0 )    {
        x->count += x->left->count;
        x->sum += x->left->sum;
    }
}

void insert(node *&x, double _k)   {
    if ( x == 0 )   {
        x = new node(_k);
        x->left = x->right = 0;
    }
    else if ( _k < x->key )  {
        x->count ++;
        x->sum += _k;
        insert(x->left, _k);
        if (x->left->fix < x->fix) right_rot(x);
    }
    else    {
        x->count ++;
        x->sum += _k;
        insert(x->right, _k);
        if (x->right->fix < x->fix) left_rot(x);
    }
}

void delnode(node *x)   {
    if ( x == 0 ) return;
    delnode(x->left);
    delnode(x->right);
    if ( x->left != 0 ) delete x->left;
    if ( x->right != 0 ) delete x->right;
}

bool remove(node *&x, double _k)   {
    if ( x == 0 ) return false;
    if ( _k < x->key - err_tolerance)  {
        if ( remove(x->left, _k) )  {
            x->count --;
            x->sum -= _k;
        }
    }
    else if ( _k > x->key + err_tolerance) {
        if ( remove(x->right, _k) ) {
            x->count --;
            x->sum -= _k;
        }
    }
    else if ( x->left ==0 || x->right == 0 )   {
        node *y = x;
        x = ( x->left == 0 ) ? x->right : x->left;
        delete y;
    }
    else if ( x->left->fix < x->right->fix )    {
        right_rot(x);
        if ( remove(x->right, _k) ) {
            x->count --;
            x->sum -= _k;
        }
    }
    else    {
        left_rot(x);
        if ( remove(x->left, _k) )  {
            x->count --;
            x->sum -= _k;
        }
    }

    return true;
}

res* search(node *x, double e)    {
    res* cur;
    if ( x == 0 ) return new res();
    if ( e < x->key )   {
        cur = search(x->left, e);
        cur->rct ++;
        cur->rsum += x->key;
        if ( x->right != 0 )    {
            cur->rct += x->right->count;
            cur->rsum += x->right->sum;
        }
    }
    else    {
        cur = search(x->right, e);
        cur->lct ++;
        cur->lsum += x->key;
        if ( x->left != 0 ) {
            cur->lct += x->left->count;
            cur->lsum += x->left->sum;
        }
    }
    return cur;
}

// end of tree heap 
//////////////////////////////////////

////////////////////////////////////////////////////////////////////////////
// Noisy L1 partition with interval buckets of size 2^k
void L1partition_approx(int *hist, int n1, double* x, int n, double epsilon, double ratio, long seed)    {
    double **score = new double*[n];
    double invepsilon1 = 1.0 / (epsilon*ratio);
    double invepsilon2 = 1.0 / (epsilon - epsilon*ratio);
    double invn = 1.0 / n;
    int m = int(log((double)n) / log((double)2)) + 1;
    MTRand53 rnum;
    rnum.seed(seed);

    for (int i=0;i<n; i++)  {
        score[i] = new double[m];
    }

    int len = 1, off = 0;
    while ( len <= n )   {
		// for each length (len), compute the score of all buckets with this length
        node* root = new node(x[0]);
        double sum = x[0];
        double invlen = 1.0/len;
        for (int i=1; i<len; i++) {
            insert(root, x[i]);
            sum += x[i];
        }
        for (int i=len-1; i<n; i++) {
            double avg = double(sum) / len;
            double r = 0.5 - rnum();
            double lap =  0;
            if ( len > 1 )
                lap = (2.0 - invlen - invn)*invepsilon1*sgn(r)*log(1.0-2.0*dabs(r));
            res* loc = search(root, avg);
            score[i][off] = (loc->lct - loc->rct)*avg - loc->lsum + loc->rsum;
            score[i][off] += invepsilon2 + lap;
            score[i][off] = (score[i][off] < invepsilon2) ? invepsilon2 : score[i][off];
            delete loc;
            if ( i < n-1 )  {
                sum += x[i+1] - x[i-len+1];
                insert(root, x[i+1]);
                remove(root, x[i-len+1]);
            }
        }
        len <<= 1;
        off ++;
        delnode(root);
        if (root!=0) delete root;
    }

    double *cumscore = new double[n+1];
    int *lbound = new int[n+1];
    cumscore[0] = 0;
    lbound[0] = -1;
    for (int i=0; i<n; i++) {
        cumscore[i+1] = cumscore[i] + score[i][0];
        lbound[i+1] = i;
        for (int j=1, len=2; len<=i+1; len<<=1, j++) {
            double curscore = cumscore[i-len+1] + score[i][j];
            if ( curscore <= cumscore[i+1] ) {
                lbound[i+1] = i-len+1;
                cumscore[i+1] = curscore;
            }
        }
    }
    
    int j = n;
    for (int i=0; i<=n && j>-1; i++) {
        hist[i] = j;
        j = lbound[j];
    }

    for (int i=0; i<n; i++)
        delete []score[i];

    delete []score;
    delete []cumscore;
    delete []lbound;
}

////////////////////////////////////////////////////////////////////////////
// Noisy L1 partition with all interval buckets

// compute the score of all partitions starts at x
double* cumabserr(double *x, int n)   {
    double* err = new double[n];
    double sum = x[0];
    node *root = new node(x[0]);
    err[0] = 0;
    for (int i=1; i<n; i++) {
        sum += x[i];
        double avg = double(sum) / (i+1);
        insert(root, x[i]);
        res* loc = search(root, avg);
        err[i] = (loc->lct - loc->rct)*avg - loc->lsum + loc->rsum;
        delete loc;
    }
    delnode(root);
    if (root!=0) delete root;
    return err;
}


void L1partition(int *hist, int n1, double* x, int n, double epsilon, double ratio, long seed)    {

    double **score = new double*[n];
    double invepsilon1 = 1.0 / (epsilon*ratio);
    double invepsilon2 = 1.0 / (epsilon - epsilon*ratio);
    MTRand53 rnum;
    rnum.seed(seed);
    for (int i=0; i<n; i++) {
        score[i] = cumabserr(x+i, n-i);
        for (int j=0; j<n-i; j++)   {
            double r = 0.5 - rnum();
            double lap =  0;
            if ( j > 0 )
                lap = (2.0-1.0/(j+1)-1.0/n)*invepsilon1*sgn(r)*log(1.0-2.0*dabs(r));
            score[i][j] += invepsilon2 + lap;
            score[i][j] = (score[i][j] < invepsilon2)? invepsilon2 : score[i][j];
        }
    }

    double *cumscore = new double[n+1];
    int *lbound = new int[n+1];
    cumscore[0] = 0;
    lbound[0] = -1;
    for (int i=0; i<n; i++) {
        cumscore[i+1] = cumscore[i] + score[i][0];
        lbound[i+1] = i;
        for (int j=0; j<i; j++) {
            double curscore = cumscore[j] + score[j][i-j];
            if ( curscore < cumscore[i+1] ) {
                lbound[i+1] = j;
                cumscore[i+1] = curscore;
            }
        }
    }
    
    int j = n;
    for (int i=0; i<=n && j>-1; i++) {
        hist[i] = j;
        j = lbound[j];
    }

    for (int i=0; i<n; i++)
        delete []score[i];

    delete []score;
    delete []cumscore;
    delete []lbound;
}
////////////////////////////////////////////////////////////////////////////
