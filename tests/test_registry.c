#include <stdarg.h>
#include <stddef.h>
#include <setjmp.h>
#include <stdint.h>
#include <cmocka.h>
#include <string.h>

#include "schemata/schemata.h"

static void test_known_schema_exists(void **state)
{
    (void)state;
    const char *json = schemata_get("kind1Schema");
    assert_non_null(json);
    /* Should contain "kind":1 or "const":1 somewhere */
    assert_non_null(strstr(json, "\"kind\""));
}

static void test_unknown_schema_returns_null(void **state)
{
    (void)state;
    const char *json = schemata_get("nonexistentSchema");
    assert_null(json);
}

static void test_null_key_returns_null(void **state)
{
    (void)state;
    const char *json = schemata_get(NULL);
    assert_null(json);
}

static void test_count_greater_than_100(void **state)
{
    (void)state;
    size_t count = schemata_count();
    assert_true(count > 100);
}

static void test_keys_sorted(void **state)
{
    (void)state;
    size_t count = 0;
    const char *const *keys = schemata_keys(&count);
    assert_true(count > 0);
    for (size_t i = 1; i < count; i++) {
        assert_true(strcmp(keys[i - 1], keys[i]) < 0);
    }
}

static void test_nip11_schema_exists(void **state)
{
    (void)state;
    const char *json = schemata_get("nip11Schema");
    assert_non_null(json);
}

static void test_tag_schema_exists(void **state)
{
    (void)state;
    const char *json = schemata_get("eTagSchema");
    assert_non_null(json);
}

static void test_message_schema_exists(void **state)
{
    (void)state;
    const char *json = schemata_get("relayNoticeSchema");
    assert_non_null(json);
}

int main(void)
{
    const struct CMUnitTest tests[] = {
        cmocka_unit_test(test_known_schema_exists),
        cmocka_unit_test(test_unknown_schema_returns_null),
        cmocka_unit_test(test_null_key_returns_null),
        cmocka_unit_test(test_count_greater_than_100),
        cmocka_unit_test(test_keys_sorted),
        cmocka_unit_test(test_nip11_schema_exists),
        cmocka_unit_test(test_tag_schema_exists),
        cmocka_unit_test(test_message_schema_exists),
    };
    return cmocka_run_group_tests(tests, NULL, NULL);
}
