/* MIT exploration candidate (not a frozen pilot method): persisted8 backward
 * search plus singleton locate-and-verify. Known components: text-position
 * suffix-array sampling for locate and direct text comparison. The text and
 * samples are rebuilt by walking LF from every sentinel row, as Ropebwt3's
 * ssa.c does, so they share the multi-string BWT's own row coordinates. */
#include <string.h>
#include "cache.c"

typedef struct {
    idx_t *b;              /* rank2a index plus persisted 8-mer table */
    int ss, d, thr;        /* s = 1<<ss; probation checks; locate if > thr symbols remain */
    uint64_t n, m;         /* BWT rows; sentinels (strings) */
    uint64_t *mark;        /* n bits: string-local offset of row % s == 0 */
    uint32_t *blk;         /* marked rows before each 512-row block */
    uint32_t *samp;        /* global text position of each marked row, row order */
    uint64_t *txt, ntxt;   /* 2 bits/symbol (A..T -> 0..3); separators/N read as 0 */
    uint64_t *exc, nexc;   /* sorted (position << 3 | symbol) of separators (0) and N (5) */
    uint64_t bytes;        /* bytes of the structures added to persisted8 */
} sv_t;

static inline int lf(const rld_t *e, uint64_t *k) {
    uint64_t ok[6]; int c = rld_rank1a(e, *k, ok);
    if (c) *k = e->cnt[c] + ok[c];
    return c;
}
static int cmp64(const void *a, const void *b) {
    uint64_t x = *(const uint64_t*)a, y = *(const uint64_t*)b; return x < y ? -1 : x > y;
}
static int push(uint64_t **a, uint64_t *n, uint64_t *cap, uint64_t x) {
    if (*n == *cap) { uint64_t *y = realloc(*a, (*cap *= 2) * 8); if (!y) return 0; *a = y; }
    (*a)[(*n)++] = x; return 1;
}
static inline uint64_t mrank(const sv_t *p, uint64_t k) {
    uint64_t r = p->blk[k >> 9], w = k >> 6;
    for (uint64_t i = (k >> 9) << 3; i < w; i++) r += __builtin_popcountll(p->mark[i]);
    return r + __builtin_popcountll(p->mark[w] & ((1ULL << (k & 63)) - 1));
}

void sv_close(void *v) {
    sv_t *p = v; if (!p) return;
    close_index(p->b); free(p->mark); free(p->blk); free(p->samp); free(p->txt); free(p->exc); free(p);
}

void *sv_load(const char *index, const char *table, int ss, int d) {
    if (ss < 1 || ss > 10 || d < 0) return NULL;
    sv_t *p = calloc(1, sizeof(*p)); if (!p) return NULL;
    p->b = load_cached(index, table, 8);
    if (!p->b) { free(p); return NULL; }
    const rld_t *e = p->b->e;
    uint64_t s = 1ULL << ss, *len = NULL, *base = NULL, *pairs = NULL, np = 0, ne = 0, cap = 0;
    p->ss = ss; p->d = d; p->thr = (int)(s / 2 + 1); p->n = e->cnt[6]; p->m = e->cnt[1];
    if (p->n >= (1ULL << 32) || p->m == 0) goto fail;
    len = calloc(p->m, 8); base = calloc(p->m + 1, 8);
    if (!len || !base) goto fail;
    for (uint64_t j = 0; j < p->m; j++) { uint64_t k = j; while (lf(e, &k)) len[j]++; }
    for (uint64_t j = 0; j < p->m; j++) base[j + 1] = base[j] + len[j] + 1;  /* separator after each string */
    p->ntxt = base[p->m];
    if (p->ntxt != p->n) goto fail;  /* every row is one text symbol or one sentinel */
    p->txt = calloc((p->ntxt + 31) / 32, 8); p->mark = calloc((p->n + 63) / 64, 8);
    p->blk = calloc((p->n >> 9) + 2, 4); pairs = malloc(((p->n >> ss) + p->m + 1) * 8);
    cap = p->m + 1024; p->exc = malloc(cap * 8);
    if (!p->txt || !p->mark || !p->blk || !pairs || !p->exc) goto fail;
    for (uint64_t j = 0; j < p->m; j++) {
        uint64_t k = j, t = len[j]; int c;
        if (!push(&p->exc, &ne, &cap, (base[j] + len[j]) << 3)) goto fail;  /* separator, symbol 0 */
        while ((c = lf(e, &k))) {
            uint64_t pos = base[j] + --t;
            if (c <= 4) p->txt[pos >> 5] |= (uint64_t)(c - 1) << ((pos & 31) * 2);
            else if (!push(&p->exc, &ne, &cap, pos << 3 | (uint64_t)c)) goto fail;
            if ((t & (s - 1)) == 0) {
                p->mark[k >> 6] |= 1ULL << (k & 63);
                pairs[np++] = k << 32 | pos;
            }
        }
        if (t != 0) goto fail;
    }
    qsort(pairs, np, 8, cmp64); qsort(p->exc, ne, 8, cmp64); p->nexc = ne;
    p->samp = malloc((np ? np : 1) * 4); if (!p->samp) goto fail;
    for (uint64_t i = 0; i < np; i++) p->samp[i] = (uint32_t)pairs[i];
    for (uint64_t b = 0, r = 0; b <= (p->n >> 9); b++) {
        p->blk[b] = (uint32_t)r;
        for (uint64_t w = b << 3; w < (b + 1) << 3 && w < (p->n + 63) / 64; w++) r += __builtin_popcountll(p->mark[w]);
    }
    p->bytes = (p->n + 63) / 64 * 8 + ((p->n >> 9) + 2) * 4 + np * 4 + (p->ntxt + 31) / 32 * 8 + ne * 8;
    free(len); free(base); free(pairs);
    return p;
fail:
    free(len); free(base); free(pairs); sv_close(p); return NULL;
}

uint64_t sv_bytes(void *v) { return ((sv_t*)v)->bytes; }

/* Text symbol 0..5 at a global position (tests and exception path). */
int sv_sym(void *v, uint64_t x) {
    sv_t *p = v; if (x >= p->ntxt) return -1;
    uint64_t lo = 0, hi = p->nexc;
    while (lo < hi) { uint64_t mid = (lo + hi) / 2; if ((p->exc[mid] >> 3) < x) lo = mid + 1; else hi = mid; }
    if (lo < p->nexc && (p->exc[lo] >> 3) == x) return (int)(p->exc[lo] & 7);
    return 1 + (int)((p->txt[x >> 5] >> ((x & 31) * 2)) & 3);
}

/* Global text position of the suffix at BWT row k (rows >= m only). */
int64_t sv_locate(void *v, uint64_t k) {
    sv_t *p = v; const rld_t *e = p->b->e; uint64_t steps = 0;
    if (k < p->m || k >= p->n) return -1;
    while (!((p->mark[k >> 6] >> (k & 63)) & 1)) {
        if (!lf(e, &k) || ++steps >= (1ULL << p->ss)) return -1;
    }
    return (int64_t)(p->samp[mrank(p, k)] + steps);
}

/* 1 if q[0..r) equals the text just before global position pos, else 0. */
static uint64_t verify(sv_t *p, const uint8_t *q, int r, uint64_t pos) {
    if (pos < (uint64_t)r) return 0;
    uint64_t a = pos - r, lo = 0, hi = p->nexc;
    while (lo < hi) { uint64_t mid = (lo + hi) / 2; if ((p->exc[mid] >> 3) < a) lo = mid + 1; else hi = mid; }
    if (lo < p->nexc && (p->exc[lo] >> 3) < pos) {
        for (int j = 0; j < r; j++) if (sv_sym(p, a + j) != q[j]) return 0;
        return 1;
    }
    for (int j = 0; j < r; j++) {
        uint64_t x = a + j;
        if (q[j] > 4 || (int)((p->txt[x >> 5] >> ((x & 31) * 2)) & 3) != q[j] - 1) return 0;
    }
    return 1;
}

#ifdef SV_TRACE
uint64_t sv_located = 0;
#endif
uint64_t sv_count(void *v, const uint8_t *s, int len) {
    sv_t *p = v; idx_t *b = p->b; const rld_t *e = b->e;
    if (len <= 0) return UINT64_MAX;
    for (int j = 0; j < len; j++) if (s[j] < 1 || s[j] > 5) return UINT64_MAX;
    uint64_t k = 0, l = e->cnt[6]; int i = len - 1, single = 0;
    if (len >= b->seed) {
        size_t code = 0; int good = 1;
        for (int j = len - b->seed; j < len; j++) { if (s[j] > 4) { good = 0; break; } code = (code << 2) | (s[j] - 1); }
        if (good) { k = b->lo[code]; l = b->hi[code]; i -= b->seed; }
    }
    for (; i >= 0 && k < l; i--) {
        if (l - k == 1 && ++single > p->d && i + 1 > p->thr) {
            int64_t pos = sv_locate(p, k);
#ifdef SV_TRACE
            sv_located++;           /* test build only: locate path taken */
#endif
#ifdef SV_MUTANT
            if (pos >= 0) pos += 1; /* negative control: off-by-one locate */
#endif
            return pos < 0 ? UINT64_MAX : verify(p, s, i + 1, (uint64_t)pos);
        }
        step(e, s[i], 0, &k, &l);
    }
    return l - k;
}

uint64_t sv_batch(void *v, const uint8_t *seq, const int32_t *offsets, const int32_t *lens, size_t n, int reps, uint64_t *out) {
    uint64_t sum = 0;
    for (int r = 0; r < reps; r++) for (size_t i = 0; i < n; i++) { out[i] = sv_count(v, seq + offsets[i], lens[i]); sum += out[i]; }
    return sum;
}
