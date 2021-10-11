#ifndef __SERDE_WRAPPER_H__
#define __SERDE_WRAPPER_H__

#include "rapidjson/document.h"
#include "rapidjson/writer.h"
#include "rapidjson/stringbuffer.h"

#define String (const char *)

using namespace rapidjson;

/* Jsonify argument one-by-one */
#define CLAIM_ARG_int(x)        auto x = (int) d[#x].GetInt();
#define CLAIM_ARG_uint(x)       auto x = (unsigned) d[#x].GetUint();
#define CLAIM_ARG_int64(x)      auto x = (int64_t) d[#x].GetInt64();
#define CLAIM_ARG_uint64(x)     auto x = (uint64_t) d[#x].GetUint64();
#define CLAIM_ARG_bool(x)       auto x = (bool) d[#x].GetBool();
#define CLAIM_ARG_float(x)      auto x = (float) d[#x].GetDouble();
#define CLAIM_ARG_double(x)     auto x = (double) d[#x].GetDouble();
#define CLAIM_ARG_String(x)     auto x = (String) d[#x].GetString();
//TODO: GetArray (sized and un-sized)
//TODO: GetObject (general deserialization)

/* Arguments extraction */
#define __ARGS_EXTRACT_5(type, arg, ...) \
        arg, __ARGS_EXTRACT_4(__VA_ARGS__)
#define __ARGS_EXTRACT_4(type, arg, ...) \
        arg, __ARGS_EXTRACT_3(__VA_ARGS__)
#define __ARGS_EXTRACT_3(type, arg, ...) \
        arg, __ARGS_EXTRACT_2(__VA_ARGS__)
#define __ARGS_EXTRACT_2(type, arg, ...) \
        arg, __ARGS_EXTRACT_1(__VA_ARGS__)
#define __ARGS_EXTRACT_1(type, arg, ...) \
        arg
#define __ARGS_EXTRACT_0(...)

/* Arguments concatenate */
#define __ARGS_CONCAT_5(type, arg, ...) \
        type arg, __ARGS_CONCAT_4(__VA_ARGS__)
#define __ARGS_CONCAT_4(type, arg, ...) \
        type arg, __ARGS_CONCAT_3(__VA_ARGS__)
#define __ARGS_CONCAT_3(type, arg, ...) \
        type arg, __ARGS_CONCAT_2(__VA_ARGS__)
#define __ARGS_CONCAT_2(type, arg, ...) \
        type arg, __ARGS_CONCAT_1(__VA_ARGS__)
#define __ARGS_CONCAT_1(type, arg, ...) \
        type arg
#define __ARGS_CONCAT_0(...)

/* Jsonify arguments claim */
#define __JSONIFY_ARGS_CLAIM_5(type, arg, ...)  \
        CLAIM_ARG_##type(arg)                   \
        __JSONIFY_ARGS_CLAIM_4(__VA_ARGS__)
#define __JSONIFY_ARGS_CLAIM_4(type, arg, ...)  \
        CLAIM_ARG_##type(arg)                   \
        __JSONIFY_ARGS_CLAIM_3(__VA_ARGS__)
#define __JSONIFY_ARGS_CLAIM_3(type, arg, ...)  \
        CLAIM_ARG_##type(arg)                   \
        __JSONIFY_ARGS_CLAIM_2(__VA_ARGS__)
#define __JSONIFY_ARGS_CLAIM_2(type, arg, ...)  \
        CLAIM_ARG_##type(arg)                   \
        __JSONIFY_ARGS_CLAIM_1(__VA_ARGS__)
#define __JSONIFY_ARGS_CLAIM_1(type, arg, ...)  \
        CLAIM_ARG_##type(arg)
#define __JSONIFY_ARGS_CLAIM_0(...)

/* Export JSONIFY_FUNC_# */
#define __JSONIFY_FUNC(num, restype, func, ...)                                         \
        String func(String args) {                                                      \
            Document d;                                                                 \
            d.parse(args);                                                              \
            __JSONIFY_ARGS_CLAIM_##num(__VA_ARGS__)                                     \
            Value ret( __origin_##func( __ARGS_EXTRACT_##num(__VA_ARGS__) ) );          \
            return ret.GetString();                                                     \
        }                                                                               \
        restype __origin_##func( __ARGS_CONCAT_##num(__VA_ARGS__) )

#define JSONIFY_FUNC_0(...) __JSONIFY_FUNC(0, __VA_ARGS__)
#define JSONIFY_FUNC_1(...) __JSONIFY_FUNC(1, __VA_ARGS__)
#define JSONIFY_FUNC_2(...) __JSONIFY_FUNC(2, __VA_ARGS__)
#define JSONIFY_FUNC_3(...) __JSONIFY_FUNC(3, __VA_ARGS__)
#define JSONIFY_FUNC_4(...) __JSONIFY_FUNC(4, __VA_ARGS__)
#define JSONIFY_FUNC_5(...) __JSONIFY_FUNC(5, __VA_ARGS__)

/**
 * Example 1:
 * JSONIFY_FUNC_1(int, square, int, num) {
 * // int square(int num) {
 *     return num * num;
 * }
*/

#endif