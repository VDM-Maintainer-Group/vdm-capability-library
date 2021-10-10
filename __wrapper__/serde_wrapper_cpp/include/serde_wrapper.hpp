#ifndef __SERDE_WRAPPER_H__
#define __SERDE_WRAPPER_H__

#include <string.h>
#include "rapidjson/document.h"
#include "rapidjson/writer.h"
#include "rapidjson/stringbuffer.h"

#define string (const char *)

using namespace rapidjson;

//Reference: https://stackoverflow.com/questions/12447557/can-we-have-recursive-macros

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
#define __ARGS_EXTRACT0(...)

/* Jsonify arguments claim */
#define __JSONIFY_ARGS_CLAIM_5(type, arg, ...) \
        //TODO:
        __JSONIFY_ARGS_CLAIM_4(__VA_ARGS__)


/* Export JSONIFY_FUNC_# */
#define __JSONIFY_FUNC(num, restype, func, ...) \
        string func(string args) {
            Document d;
            d.parse(args);

            __JSONIFY_ARGS_CLAIM_##num(__VA_ARGS__)
            Value ret( __origin_##func( ___ARGS_EXTRACT_##num(__VA_ARGS__) ) );

            return ret.GetString();
        }
        restype __origin_##func()

#define JSONIFY_FUNC_0(...) __JSONIFY_FUNC(0, __VA_ARGS__)
#define JSONIFY_FUNC_1(...) __JSONIFY_FUNC(1, __VA_ARGS__)
#define JSONIFY_FUNC_2(...) __JSONIFY_FUNC(2, __VA_ARGS__)
#define JSONIFY_FUNC_3(...) __JSONIFY_FUNC(3, __VA_ARGS__)
#define JSONIFY_FUNC_4(...) __JSONIFY_FUNC(4, __VA_ARGS__)
#define JSONIFY_FUNC_5(...) __JSONIFY_FUNC(5, __VA_ARGS__)

#endif