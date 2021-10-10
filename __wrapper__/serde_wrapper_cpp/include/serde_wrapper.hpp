#ifndef __SERDE_WRAPPER_H__
#define __SERDE_WRAPPER_H__

#include <string.h>
#include "rapidjson/document.h"
#include "rapidjson/writer.h"
#include "rapidjson/stringbuffer.h"

#define string (const char *)
#define __is_type(x, _type) (strncmp(x,_type,strlen(_type))==0)
#define is_int(x) (__is_type(x, "int") || __is_type(x, "uint"))
#define is_double(x) (__is_type(x, "float") || __is_type(x, "double"))
#define is_bool(x) (__is_type(x, "bool"))
#define is_char false
#define is_string false

using namespace rapidjson;

#define ___ARGS_EXTRACT(type, arg, ...) \
        arg, ___ARGS_EXTRACT(__VA_ARGS__)

#define __JSONIFY_ARGS_CLAIM(type, arg, ...) \
        //TODO:
        __JSONIFY_ARGS_CLAIM(__VA_ARGS__)

#define JSONIFY_FUNC(restype, func, ...) \
        string func(string args) {
            Document d;
            d.parse(args);

            __JSONIFY_ARGS_CLAIM(__VA_ARGS__)
            
            Value ret( __origin_##func( ___ARGS_EXTRACT(__VA_ARGS__) ) );
            return ret.GetString();
        }
        restype __origin_##func()

#endif