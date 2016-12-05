typedef struct _item {
    double error;
    double c1;
    double c2;
} item_t;

item_t clustersplit(double* list, int pos, int size);
double l1_distance(double* vec, int start, int end, double avg);
