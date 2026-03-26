# schemata-c

C data library for [Nostr](https://nostr.com/) protocol JSON schemas. This is the C equivalent of [`schemata-rs`](https://github.com/nostrability/schemata-rs) and the [`@nostrability/schemata`](https://github.com/nostrability/schemata) npm package.

Schemas are generated from the [schemata](https://github.com/nostrability/schemata) `dist/` build via a Python script that produces C source with binary-search lookup. 367 schemas are embedded as static string literals.

## Related projects

| Project | Language | Role |
|---------|----------|------|
| [nostrability/schemata](https://github.com/nostrability/schemata) | JSON/JS | Canonical schema definitions |
| [schemata-validator-c](https://github.com/nostrability/schemata-validator-c) | C | Validator using this library |
| [schemata-rs](https://github.com/nostrability/schemata-rs) | Rust | Rust equivalent |

## Usage

Add as a CMake subdirectory:

```cmake
add_subdirectory(path/to/schemata-c)
target_link_libraries(my_target PRIVATE schemata)
```

```c
#include <schemata/schemata.h>
#include <stdio.h>

int main(void) {
    /* Look up a schema by name */
    const char *schema = schemata_get("kind1Schema");
    if (schema) {
        printf("kind 1 schema: %.60s...\n", schema);
    }

    /* Iterate all keys */
    size_t count;
    const char *const *keys = schemata_keys(&count);
    printf("%zu schemas available\n", count);
    for (size_t i = 0; i < count; i++) {
        printf("  %s\n", keys[i]);
    }

    return 0;
}
```

## API

| Function | Description |
|----------|-------------|
| `schemata_get(key)` | Look up a schema by export name. Returns static JSON string, or `NULL` if not found. |
| `schemata_keys(&count)` | Return sorted array of all schema keys. Sets `count` to the number of keys. |
| `schemata_count()` | Return the total number of embedded schemas. |

All returned pointers are to static data and must not be freed.

## Build & test

```sh
mkdir build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Debug
make
ctest -V
```

Requires [cmocka](https://cmocka.org/) for tests (auto-detected via `pkg-config`). Disable with `-DSCHEMATA_BUILD_TESTS=OFF`.

## License

GPL-3.0-or-later
