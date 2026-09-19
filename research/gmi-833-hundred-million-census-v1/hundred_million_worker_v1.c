#include <errno.h>
#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct {
    uint32_t a, b, c;
    uint64_t count;
    uint8_t used;
} Entry;

typedef struct {
    Entry *slots;
    size_t capacity;
    size_t used;
} Map;

static uint64_t mix64(uint64_t x) {
    x += UINT64_C(0x9e3779b97f4a7c15);
    x = (x ^ (x >> 30)) * UINT64_C(0xbf58476d1ce4e5b9);
    x = (x ^ (x >> 27)) * UINT64_C(0x94d049bb133111eb);
    return x ^ (x >> 31);
}

static uint64_t key_hash(uint32_t a, uint32_t b, uint32_t c) {
    return mix64((uint64_t)a ^ (mix64((uint64_t)b) << 1) ^ (mix64((uint64_t)c) << 7));
}

static void die(const char *message) {
    fprintf(stderr, "%s\n", message);
    exit(2);
}

static void map_init(Map *map, size_t capacity) {
    map->slots = calloc(capacity, sizeof(Entry));
    if (map->slots == NULL) die("cannot allocate semantic map");
    map->capacity = capacity;
    map->used = 0;
}

static void map_insert_raw(Map *map, uint32_t a, uint32_t b, uint32_t c, uint64_t count) {
    size_t mask = map->capacity - 1;
    size_t index = (size_t)key_hash(a, b, c) & mask;
    while (map->slots[index].used) {
        Entry *entry = &map->slots[index];
        if (entry->a == a && entry->b == b && entry->c == c) {
            entry->count += count;
            return;
        }
        index = (index + 1) & mask;
    }
    map->slots[index] = (Entry){a, b, c, count, 1};
    map->used++;
}

static void map_grow(Map *map) {
    Map grown;
    map_init(&grown, map->capacity * 2);
    for (size_t i = 0; i < map->capacity; i++) {
        Entry *entry = &map->slots[i];
        if (entry->used) map_insert_raw(&grown, entry->a, entry->b, entry->c, entry->count);
    }
    free(map->slots);
    *map = grown;
}

static void map_increment(Map *map, uint32_t a, uint32_t b, uint32_t c) {
    if ((map->used + 1) * 10 >= map->capacity * 7) map_grow(map);
    map_insert_raw(map, a, b, c, 1);
}

static uint32_t pack_observation(uint32_t terminal, const uint32_t *output, uint32_t length) {
    uint32_t packed = terminal * 7u + length;
    for (uint32_t i = 0; i < 6; i++) {
        packed = packed * 8u + (i < length ? output[i] + 1u : 0u);
    }
    return packed;
}

static uint32_t observe(const uint32_t *instructions, uint32_t labels, uint32_t word_kind) {
    uint32_t reg = 0, pc = 0, input_position = 0, output[6], output_length = 0;
    uint32_t input_length = word_kind == 0 ? 0u : 1u;
    uint32_t input_value = word_kind == 2 ? 1u : 0u;
    uint32_t terminal = 2u;
    uint32_t n2 = labels * labels;

    for (uint32_t step = 0; step < 6; step++) {
        uint32_t digit = instructions[pc];
        if (digit < labels) {
            if (input_position >= input_length) {
                terminal = 1u;
                break;
            }
            reg = input_value;
            input_position++;
            pc = digit;
        } else if (digit < 2u * labels) {
            reg++;
            pc = digit - labels;
        } else if (digit < 2u * labels + n2) {
            uint32_t offset = digit - 2u * labels;
            uint32_t nonzero = offset / labels;
            uint32_t zero = offset % labels;
            if (reg > 0) {
                reg--;
                pc = nonzero;
            } else {
                pc = zero;
            }
        } else if (digit < 3u * labels + n2) {
            output[output_length++] = reg;
            pc = digit - (2u * labels + n2);
        } else {
            terminal = 0u;
            break;
        }
    }
    return pack_observation(terminal, output, output_length);
}

static void print_u128(__uint128_t value) {
    char buffer[64];
    size_t length = 0;
    if (value == 0) {
        putchar('0');
        return;
    }
    while (value > 0) {
        buffer[length++] = (char)('0' + value % 10);
        value /= 10;
    }
    while (length > 0) putchar(buffer[--length]);
}

static int compare_entries(const void *left_raw, const void *right_raw) {
    const Entry *left = left_raw, *right = right_raw;
    if (left->a != right->a) return left->a < right->a ? -1 : 1;
    if (left->b != right->b) return left->b < right->b ? -1 : 1;
    if (left->c != right->c) return left->c < right->c ? -1 : 1;
    return 0;
}

static uint64_t parse_u64(const char *text, const char *label) {
    char *end = NULL;
    errno = 0;
    unsigned long long value = strtoull(text, &end, 10);
    if (errno || end == text || *end != '\0') {
        fprintf(stderr, "invalid %s\n", label);
        exit(2);
    }
    return (uint64_t)value;
}

int main(int argc, char **argv) {
    if (argc != 4) die("usage: worker LABELS START COUNT");
    uint64_t labels64 = parse_u64(argv[1], "labels");
    uint64_t start = parse_u64(argv[2], "start");
    uint64_t count = parse_u64(argv[3], "count");
    if (labels64 < 1 || labels64 > 5 || count == 0) die("worker arguments outside frozen scope");
    uint32_t labels = (uint32_t)labels64;
    uint32_t q = 1u + 3u * labels + labels * labels;
    uint64_t population = 1;
    for (uint32_t i = 0; i < labels; i++) population *= q;
    if (start > population || count > population - start) die("rank interval outside stratum");

    Map semantics;
    map_init(&semantics, 1024);
    __uint128_t rank_sum = 0, rank_square_sum = 0;
    uint64_t rank_digest = UINT64_C(0xcbf29ce484222325);
    uint64_t semantic_digest = UINT64_C(0x84222325cbf29ce4);

    for (uint64_t rank = start; rank < start + count; rank++) {
        uint64_t residual = rank;
        uint32_t instructions[5] = {0, 0, 0, 0, 0};
        for (uint32_t reverse = labels; reverse > 0; reverse--) {
            instructions[reverse - 1] = (uint32_t)(residual % q);
            residual /= q;
        }
        if (residual != 0) die("unrank residual nonzero");
        uint64_t rerank = 0;
        for (uint32_t i = 0; i < labels; i++) rerank = rerank * q + instructions[i];
        if (rerank != rank) die("rank/unrank round-trip failed");

        uint32_t a = observe(instructions, labels, 0);
        uint32_t b = observe(instructions, labels, 1);
        uint32_t c = observe(instructions, labels, 2);
        map_increment(&semantics, a, b, c);
        rank_sum += rank;
        rank_square_sum += (__uint128_t)rank * rank;
        rank_digest = (rank_digest ^ mix64(rank + ((uint64_t)labels << 56))) * UINT64_C(0x100000001b3);
        semantic_digest = (semantic_digest ^ key_hash(a, b, c) ^ mix64(rank)) * UINT64_C(0x100000001b3);
    }

    Entry *ordered = malloc(semantics.used * sizeof(Entry));
    if (ordered == NULL) die("cannot allocate sorted semantic entries");
    size_t position = 0;
    for (size_t i = 0; i < semantics.capacity; i++) {
        if (semantics.slots[i].used) ordered[position++] = semantics.slots[i];
    }
    if (position != semantics.used) die("semantic map accounting drift");
    qsort(ordered, position, sizeof(Entry), compare_entries);

    printf("META\t%" PRIu32 "\t%" PRIu32 "\t%" PRIu64 "\t%" PRIu64 "\t%" PRIu64 "\n",
           labels, q, population, start, count);
    printf("MOMENTS\t");
    print_u128(rank_sum);
    printf("\t");
    print_u128(rank_square_sum);
    printf("\t%016" PRIx64 "\t%016" PRIx64 "\n", rank_digest, semantic_digest);
    for (size_t i = 0; i < position; i++) {
        Entry *entry = &ordered[i];
        printf("SEM\t%" PRIu32 "\t%" PRIu32 "\t%" PRIu32 "\t%" PRIu64 "\n",
               entry->a, entry->b, entry->c, entry->count);
    }
    printf("END\t%zu\t%" PRIu64 "\n", position, count);

    free(ordered);
    free(semantics.slots);
    return 0;
}
