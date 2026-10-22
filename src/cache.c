/* MIT pilot extension. Format is native-endian; Python binds hashes and ABI. */
#include <stdio.h>
#include <string.h>
#include "count.c"

int save_table(void *v, const char *path) {
    idx_t *p = v;
    if (!p || !p->seed) return -1;
    FILE *f = fopen(path, "wb");
    if (!f) return -1;
    uint64_t header[3] = {0x4441484341434831ULL, (uint64_t)p->seed, p->e->cnt[6]};
    size_t n = (size_t)1 << (2*p->seed);
    int ok = fwrite(header, sizeof(uint64_t), 3, f) == 3 &&
             fwrite(p->lo, sizeof(uint64_t), n, f) == n &&
             fwrite(p->hi, sizeof(uint64_t), n, f) == n;
    if (fclose(f)) ok = 0;
    return ok ? 0 : -1;
}

void *load_cached(const char *index, const char *table, int seed) {
    if (seed < 1 || seed > 8) return NULL;
    idx_t *p = load_index(index, 0);
    if (!p) return NULL;
    FILE *f = fopen(table, "rb");
    if (!f) { close_index(p); return NULL; }
    uint64_t header[3];
    size_t n = (size_t)1 << (2*seed);
    int ok = fread(header, sizeof(uint64_t), 3, f) == 3 &&
             header[0] == 0x4441484341434831ULL && header[1] == (uint64_t)seed &&
             header[2] == p->e->cnt[6];
    p->lo = malloc(n * sizeof(uint64_t));
    p->hi = malloc(n * sizeof(uint64_t));
    ok = ok && p->lo && p->hi;
    if (ok) ok = fread(p->lo, sizeof(uint64_t), n, f) == n &&
                 fread(p->hi, sizeof(uint64_t), n, f) == n && fgetc(f) == EOF;
    if (ok) for (size_t i = 0; i < n; i++)
        if (p->lo[i] > p->hi[i] || p->hi[i] > p->e->cnt[6]) { ok = 0; break; }
    fclose(f);
    if (!ok) { close_index(p); return NULL; }
    p->seed = seed;
    return p;
}
