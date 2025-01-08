/* Copyright (c) 2024 - 2024 ANSYS, Inc. and/or its affiliates.
 * SPDX-License-Identifier: MIT
 *
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

#ifndef SWAN_CONFIG_H_
#define SWAN_CONFIG_H_

#include <stddef.h>
#include <string.h>

{{ FMI_HOOK_BEGIN }}

#define swan_assign(swan_D, swan_S, swan_sz) (memcpy((swan_D), (swan_S), (swan_sz)))
#define swan_assign_struct swan_assign
#define swan_assign_array swan_assign
#define swan_assign_union swan_assign

#define swan_assert(A) ((void)(A))
#define swan_assume(A) ((void)(A))
#define swan_guarantee(A) ((void)(A))

#if (defined(__STDC_VERSION__) && __STDC_VERSION__ >= 199901L) || __cplusplus >= 201103L
# define HAVE_STDINT_H
#elif defined(__GNUC__)
# define HAVE_STDINT_H
#endif

#ifdef HAVE_STDINT_H
# include <stdint.h>

typedef  uint_least8_t swan_uint8;
typedef   int_least8_t swan_int8;
typedef uint_least16_t swan_uint16;
typedef  int_least16_t swan_int16;
typedef uint_least32_t swan_uint32;
typedef  int_least32_t swan_int32;
typedef uint_least64_t swan_uint64;
typedef  int_least64_t swan_int64;

# define swan_lit_int64   INT64_C
# define swan_lit_uint64 UINT64_C

#elif defined(_MSC_VER)

typedef unsigned __int8  swan_uint8;
typedef          __int8  swan_int8;
typedef unsigned __int16 swan_uint16;
typedef          __int16 swan_int16;
typedef unsigned __int32 swan_uint32;
typedef          __int32 swan_int32;
typedef unsigned __int64 swan_uint64;
typedef          __int64 swan_int64;

# define swan_lit_int64(v)  (v ## i64)
# define swan_lit_uint64(v) (v ## ui64)

#else
# error unsupported compiler, edit swan_config.h
#endif
#undef HAVE_STDINT_H


typedef unsigned char swan_bool;

typedef float  swan_float32;
typedef double swan_float64;

typedef ptrdiff_t swan_size;

typedef char swan_char;

#define swan_false ((swan_bool) 0)
#define swan_true  ((swan_bool) 1)

#define swan_lit_float32(swan_C1) ((swan_float32) (swan_C1))
#define swan_lit_float64(swan_C1) ((swan_float64) (swan_C1))

#define swan_lit_size(swan_C1)   ((swan_size) (swan_C1))

#define swan_lit_uint32(swan_C1) ((swan_uint32) (swan_C1))
#define swan_lit_uint16(swan_C1) ((swan_uint16) (swan_C1))
#define swan_lit_uint8(swan_C1)  ((swan_uint8)  (swan_C1))

#define swan_lit_int32(swan_C1) ((swan_int32) (swan_C1))
#define swan_lit_int16(swan_C1) ((swan_int16) (swan_C1))
#define swan_lit_int8(swan_C1)  ((swan_int8)  (swan_C1))

#define swan_lit_char(swan_C1)   ((swan_char)  (swan_C1))



#define swan_lsl_uint64(swan_C1, swan_C2)                          \
  ((swan_uint64) ((swan_C1) << (swan_C2)) & 0xffffffffffffffffU)
#define swan_lsl_uint32(swan_C1, swan_C2)                          \
  ((swan_uint32) ((swan_C1) << (swan_C2)) & 0xffffffffU)
#define swan_lsl_uint16(swan_C1, swan_C2)                          \
  ((swan_uint16) ((swan_C1) << (swan_C2)) & 0xffffU)
#define swan_lsl_uint8(swan_C1, swan_C2)                           \
  ((swan_uint8)  ((swan_C1) << (swan_C2)) & 0xffU)

#define swan_lnot_uint64(swan_C1)           ((swan_C1) ^ 0xffffffffffffffffU)
#define swan_lnot_uint32(swan_C1)           ((swan_C1) ^ 0xffffffffU)
#define swan_lnot_uint16(swan_C1)           ((swan_C1) ^ 0xffffU)
#define swan_lnot_uint8(swan_C1)            ((swan_C1) ^ 0xffU)




#ifdef SWAN_WRAP_C_OPS

#define swan_float64_to_float32(swan_C1)    ((swan_float32) (swan_C1))
#define swan_size_to_float32(swan_C1)       ((swan_float32) (swan_C1))
#define swan_uint64_to_float32(swan_C1)     ((swan_float32) (swan_C1))
#define swan_uint32_to_float32(swan_C1)     ((swan_float32) (swan_C1))
#define swan_uint16_to_float32(swan_C1)     ((swan_float32) (swan_C1))
#define swan_uint8_to_float32(swan_C1)      ((swan_float32) (swan_C1))
#define swan_int64_to_float32(swan_C1)      ((swan_float32) (swan_C1))
#define swan_int32_to_float32(swan_C1)      ((swan_float32) (swan_C1))
#define swan_int16_to_float32(swan_C1)      ((swan_float32) (swan_C1))
#define swan_int8_to_float32(swan_C1)       ((swan_float32) (swan_C1))
#define swan_float32_to_float64(swan_C1)    ((swan_float64) (swan_C1))

#define swan_size_to_float64(swan_C1)       ((swan_float64) (swan_C1))
#define swan_uint64_to_float64(swan_C1)     ((swan_float64) (swan_C1))
#define swan_uint32_to_float64(swan_C1)     ((swan_float64) (swan_C1))
#define swan_uint16_to_float64(swan_C1)     ((swan_float64) (swan_C1))
#define swan_uint8_to_float64(swan_C1)      ((swan_float64) (swan_C1))
#define swan_int64_to_float64(swan_C1)      ((swan_float64) (swan_C1))
#define swan_int32_to_float64(swan_C1)      ((swan_float64) (swan_C1))
#define swan_int16_to_float64(swan_C1)      ((swan_float64) (swan_C1))
#define swan_int8_to_float64(swan_C1)       ((swan_float64) (swan_C1))

#define swan_float32_to_size(swan_C1)       ((swan_size) (swan_C1))
#define swan_float64_to_size(swan_C1)       ((swan_size) (swan_C1))
#define swan_uint64_to_size(swan_C1)        ((swan_size) (swan_C1))
#define swan_uint32_to_size(swan_C1)        ((swan_size) (swan_C1))
#define swan_uint16_to_size(swan_C1)        ((swan_size) (swan_C1))
#define swan_uint8_to_size(swan_C1)         ((swan_size) (swan_C1))
#define swan_int64_to_size(swan_C1)         ((swan_size) (swan_C1))
#define swan_int32_to_size(swan_C1)         ((swan_size) (swan_C1))
#define swan_int16_to_size(swan_C1)         ((swan_size) (swan_C1))
#define swan_int8_to_size(swan_C1)          ((swan_size) (swan_C1))

#define swan_float32_to_uint64(swan_C1)     ((swan_uint64) (swan_C1))
#define swan_float64_to_uint64(swan_C1)     ((swan_uint64) (swan_C1))
#define swan_size_to_uint64(swan_C1)        ((swan_uint64) (swan_C1))
#define swan_uint32_to_uint64(swan_C1)      ((swan_uint64) (swan_C1))
#define swan_uint16_to_uint64(swan_C1)      ((swan_uint64) (swan_C1))
#define swan_uint8_to_uint64(swan_C1)       ((swan_uint64) (swan_C1))
#define swan_int64_to_uint64(swan_C1)       ((swan_uint64) (swan_C1))
#define swan_int32_to_uint64(swan_C1)       ((swan_uint64) (swan_C1))
#define swan_int16_to_uint64(swan_C1)       ((swan_uint64) (swan_C1))
#define swan_int8_to_uint64(swan_C1)        ((swan_uint64) (swan_C1))

#define swan_float32_to_uint32(swan_C1)     ((swan_uint32) (swan_C1))
#define swan_float64_to_uint32(swan_C1)     ((swan_uint32) (swan_C1))
#define swan_size_to_uint32(swan_C1)        ((swan_uint32) (swan_C1))
#define swan_uint64_to_uint32(swan_C1)      ((swan_uint32) (swan_C1))
#define swan_uint16_to_uint32(swan_C1)      ((swan_uint32) (swan_C1))
#define swan_uint8_to_uint32(swan_C1)       ((swan_uint32) (swan_C1))
#define swan_int64_to_uint32(swan_C1)       ((swan_uint32) (swan_C1))
#define swan_int32_to_uint32(swan_C1)       ((swan_uint32) (swan_C1))
#define swan_int16_to_uint32(swan_C1)       ((swan_uint32) (swan_C1))
#define swan_int8_to_uint32(swan_C1)        ((swan_uint32) (swan_C1))

#define swan_float32_to_uint16(swan_C1)     ((swan_uint16) (swan_C1))
#define swan_float64_to_uint16(swan_C1)     ((swan_uint16) (swan_C1))
#define swan_size_to_uint16(swan_C1)        ((swan_uint16) (swan_C1))
#define swan_uint64_to_uint16(swan_C1)      ((swan_uint16) (swan_C1))
#define swan_uint32_to_uint16(swan_C1)      ((swan_uint16) (swan_C1))
#define swan_uint8_to_uint16(swan_C1)       ((swan_uint16) (swan_C1))
#define swan_int64_to_uint16(swan_C1)       ((swan_uint16) (swan_C1))
#define swan_int32_to_uint16(swan_C1)       ((swan_uint16) (swan_C1))
#define swan_int16_to_uint16(swan_C1)       ((swan_uint16) (swan_C1))
#define swan_int8_to_uint16(swan_C1)        ((swan_uint16) (swan_C1))

#define swan_float32_to_uint8(swan_C1)      ((swan_uint8) (swan_C1))
#define swan_float64_to_uint8(swan_C1)      ((swan_uint8) (swan_C1))
#define swan_size_to_uint8(swan_C1)         ((swan_uint8) (swan_C1))
#define swan_uint64_to_uint8(swan_C1)       ((swan_uint8) (swan_C1))
#define swan_uint32_to_uint8(swan_C1)       ((swan_uint8) (swan_C1))
#define swan_uint16_to_uint8(swan_C1)       ((swan_uint8) (swan_C1))
#define swan_int64_to_uint8(swan_C1)        ((swan_uint8) (swan_C1))
#define swan_int32_to_uint8(swan_C1)        ((swan_uint8) (swan_C1))
#define swan_int16_to_uint8(swan_C1)        ((swan_uint8) (swan_C1))
#define swan_int8_to_uint8(swan_C1)         ((swan_uint8) (swan_C1))

#define swan_float32_to_int64(swan_C1)      ((swan_int64) (swan_C1))
#define swan_float64_to_int64(swan_C1)      ((swan_int64) (swan_C1))
#define swan_size_to_int64(swan_C1)         ((swan_int64) (swan_C1))
#define swan_uint64_to_int64(swan_C1)       ((swan_int64) (swan_C1))
#define swan_uint32_to_int64(swan_C1)       ((swan_int64) (swan_C1))
#define swan_uint16_to_int64(swan_C1)       ((swan_int64) (swan_C1))
#define swan_uint8_to_int64(swan_C1)        ((swan_int64) (swan_C1))
#define swan_int32_to_int64(swan_C1)        ((swan_int64) (swan_C1))
#define swan_int16_to_int64(swan_C1)        ((swan_int64) (swan_C1))
#define swan_int8_to_int64(swan_C1)         ((swan_int64) (swan_C1))

#define swan_float32_to_int32(swan_C1)      ((swan_int32) (swan_C1))
#define swan_float64_to_int32(swan_C1)      ((swan_int32) (swan_C1))
#define swan_size_to_int32(swan_C1)         ((swan_int32) (swan_C1))
#define swan_uint64_to_int32(swan_C1)       ((swan_int32) (swan_C1))
#define swan_uint32_to_int32(swan_C1)       ((swan_int32) (swan_C1))
#define swan_uint16_to_int32(swan_C1)       ((swan_int32) (swan_C1))
#define swan_uint8_to_int32(swan_C1)        ((swan_int32) (swan_C1))
#define swan_int64_to_int32(swan_C1)        ((swan_int32) (swan_C1))
#define swan_int16_to_int32(swan_C1)        ((swan_int32) (swan_C1))
#define swan_int8_to_int32(swan_C1)         ((swan_int32) (swan_C1))

#define swan_float32_to_int16(swan_C1)      ((swan_int16) (swan_C1))
#define swan_float64_to_int16(swan_C1)      ((swan_int16) (swan_C1))
#define swan_size_to_int16(swan_C1)         ((swan_int16) (swan_C1))
#define swan_uint64_to_int16(swan_C1)       ((swan_int16) (swan_C1))
#define swan_uint32_to_int16(swan_C1)       ((swan_int16) (swan_C1))
#define swan_uint16_to_int16(swan_C1)       ((swan_int16) (swan_C1))
#define swan_uint8_to_int16(swan_C1)        ((swan_int16) (swan_C1))
#define swan_int64_to_int16(swan_C1)        ((swan_int16) (swan_C1))
#define swan_int32_to_int16(swan_C1)        ((swan_int16) (swan_C1))
#define swan_int8_to_int16(swan_C1)         ((swan_int16) (swan_C1))

#define swan_float32_to_int8(swan_C1)       ((swan_int8) (swan_C1))
#define swan_float64_to_int8(swan_C1)       ((swan_int8) (swan_C1))
#define swan_size_to_int8(swan_C1)          ((swan_int8) (swan_C1))
#define swan_uint64_to_int8(swan_C1)        ((swan_int8) (swan_C1))
#define swan_uint32_to_int8(swan_C1)        ((swan_int8) (swan_C1))
#define swan_uint16_to_int8(swan_C1)        ((swan_int8) (swan_C1))
#define swan_uint8_to_int8(swan_C1)         ((swan_int8) (swan_C1))
#define swan_int64_to_int8(swan_C1)         ((swan_int8) (swan_C1))
#define swan_int32_to_int8(swan_C1)         ((swan_int8) (swan_C1))
#define swan_int16_to_int8(swan_C1)         ((swan_int8) (swan_C1))

#define swan_ge_float32(swan_C1, swan_C2)    ((swan_C1) >= (swan_C2))
#define swan_gt_float32(swan_C1, swan_C2)    ((swan_C1) > (swan_C2))
#define swan_le_float32(swan_C1, swan_C2)    ((swan_C1) <= (swan_C2))
#define swan_lt_float32(swan_C1, swan_C2)    ((swan_C1) < (swan_C2))
#define swan_uminus_float32(swan_C1)                   (- (swan_C1))
#define swan_div_float32(swan_C1, swan_C2)   ((swan_C1) / (swan_C2))
#define swan_mult_float32(swan_C1, swan_C2)  ((swan_C1) * (swan_C2))
#define swan_minus_float32(swan_C1, swan_C2) ((swan_C1) - (swan_C2))
#define swan_plus_float32(swan_C1, swan_C2)  ((swan_C1) + (swan_C2))
#define swan_diff_float32(swan_C1, swan_C2)  ((swan_C1) != (swan_C2))
#define swan_eq_float32(swan_C1, swan_C2)    ((swan_C1) == (swan_C2))

#define swan_ge_float64(swan_C1, swan_C2)    ((swan_C1) >= (swan_C2))
#define swan_gt_float64(swan_C1, swan_C2)    ((swan_C1) > (swan_C2))
#define swan_le_float64(swan_C1, swan_C2)    ((swan_C1) <= (swan_C2))
#define swan_lt_float64(swan_C1, swan_C2)    ((swan_C1) < (swan_C2))
#define swan_uminus_float64(swan_C1)                   (- (swan_C1))
#define swan_div_float64(swan_C1, swan_C2)   ((swan_C1) / (swan_C2))
#define swan_mult_float64(swan_C1, swan_C2)  ((swan_C1) * (swan_C2))
#define swan_minus_float64(swan_C1, swan_C2) ((swan_C1) - (swan_C2))
#define swan_plus_float64(swan_C1, swan_C2)  ((swan_C1) + (swan_C2))
#define swan_diff_float64(swan_C1, swan_C2)  ((swan_C1) != (swan_C2))
#define swan_eq_float64(swan_C1, swan_C2)    ((swan_C1) == (swan_C2))

#define swan_mod_size(swan_C1, swan_C2)      ((swan_C1) % (swan_C2))
#define swan_gt_size(swan_C1, swan_C2)       ((swan_C1) > (swan_C2))
#define swan_le_size(swan_C1, swan_C2)       ((swan_C1) <= (swan_C2))
#define swan_lt_size(swan_C1, swan_C2)       ((swan_C1) < (swan_C2))
#define swan_uminus_size(swan_C1)                      (- (swan_C1))
#define swan_minus_size(swan_C1, swan_C2)    ((swan_C1) - (swan_C2))
#define swan_plus_size(swan_C1, swan_C2)     ((swan_C1) + (swan_C2))
#define swan_eq_size(swan_C1, swan_C2)       ((swan_C1) == (swan_C2))

#define swan_mod_uint64(swan_C1, swan_C2)    ((swan_C1) % (swan_C2))
#define swan_ge_uint64(swan_C1, swan_C2)     ((swan_C1) >= (swan_C2))
#define swan_gt_uint64(swan_C1, swan_C2)     ((swan_C1) > (swan_C2))
#define swan_le_uint64(swan_C1, swan_C2)     ((swan_C1) <= (swan_C2))
#define swan_lt_uint64(swan_C1, swan_C2)     ((swan_C1) < (swan_C2))
#define swan_uminus_uint64(swan_C1)                    (- (swan_C1))
#define swan_lsr_uint64(swan_C1, swan_C2)    ((swan_C1) >> (swan_C2))
#define swan_lxor_uint64(swan_C1, swan_C2)   ((swan_C1) ^ (swan_C2))
#define swan_lor_uint64(swan_C1, swan_C2)    ((swan_C1) | (swan_C2))
#define swan_land_uint64(swan_C1, swan_C2)   ((swan_C1) & (swan_C2))
#define swan_div_uint64(swan_C1, swan_C2)    ((swan_C1) / (swan_C2))
#define swan_mult_uint64(swan_C1, swan_C2)   ((swan_C1) * (swan_C2))
#define swan_minus_uint64(swan_C1, swan_C2)  ((swan_C1) - (swan_C2))
#define swan_plus_uint64(swan_C1, swan_C2)   ((swan_C1) + (swan_C2))
#define swan_diff_uint64(swan_C1, swan_C2)   ((swan_C1) != (swan_C2))
#define swan_eq_uint64(swan_C1, swan_C2)     ((swan_C1) == (swan_C2))

#define swan_mod_uint32(swan_C1, swan_C2)    ((swan_C1) % (swan_C2))
#define swan_ge_uint32(swan_C1, swan_C2)     ((swan_C1) >= (swan_C2))
#define swan_gt_uint32(swan_C1, swan_C2)     ((swan_C1) > (swan_C2))
#define swan_le_uint32(swan_C1, swan_C2)     ((swan_C1) <= (swan_C2))
#define swan_lt_uint32(swan_C1, swan_C2)     ((swan_C1) < (swan_C2))
#define swan_uminus_uint32(swan_C1)                    (- (swan_C1))
#define swan_lsr_uint32(swan_C1, swan_C2)    ((swan_C1) >> (swan_C2))
#define swan_lxor_uint32(swan_C1, swan_C2)   ((swan_C1) ^ (swan_C2))
#define swan_lor_uint32(swan_C1, swan_C2)    ((swan_C1) | (swan_C2))
#define swan_land_uint32(swan_C1, swan_C2)   ((swan_C1) & (swan_C2))
#define swan_div_uint32(swan_C1, swan_C2)    ((swan_C1) / (swan_C2))
#define swan_mult_uint32(swan_C1, swan_C2)   ((swan_C1) * (swan_C2))
#define swan_minus_uint32(swan_C1, swan_C2)  ((swan_C1) - (swan_C2))
#define swan_plus_uint32(swan_C1, swan_C2)   ((swan_C1) + (swan_C2))
#define swan_diff_uint32(swan_C1, swan_C2)   ((swan_C1) != (swan_C2))
#define swan_eq_uint32(swan_C1, swan_C2)     ((swan_C1) == (swan_C2))

#define swan_mod_uint16(swan_C1, swan_C2)    ((swan_C1) % (swan_C2))
#define swan_ge_uint16(swan_C1, swan_C2)     ((swan_C1) >= (swan_C2))
#define swan_gt_uint16(swan_C1, swan_C2)     ((swan_C1) > (swan_C2))
#define swan_le_uint16(swan_C1, swan_C2)     ((swan_C1) <= (swan_C2))
#define swan_lt_uint16(swan_C1, swan_C2)     ((swan_C1) < (swan_C2))
#define swan_uminus_uint16(swan_C1)                    (- (swan_C1))
#define swan_lsr_uint16(swan_C1, swan_C2)    ((swan_C1) >> (swan_C2))
#define swan_lxor_uint16(swan_C1, swan_C2)   ((swan_C1) ^ (swan_C2))
#define swan_lor_uint16(swan_C1, swan_C2)    ((swan_C1) | (swan_C2))
#define swan_land_uint16(swan_C1, swan_C2)   ((swan_C1) & (swan_C2))
#define swan_div_uint16(swan_C1, swan_C2)    ((swan_C1) / (swan_C2))
#define swan_mult_uint16(swan_C1, swan_C2)   ((swan_C1) * (swan_C2))
#define swan_minus_uint16(swan_C1, swan_C2)  ((swan_C1) - (swan_C2))
#define swan_plus_uint16(swan_C1, swan_C2)   ((swan_C1) + (swan_C2))
#define swan_diff_uint16(swan_C1, swan_C2)   ((swan_C1) != (swan_C2))
#define swan_eq_uint16(swan_C1, swan_C2)     ((swan_C1) == (swan_C2))

#define swan_mod_uint8(swan_C1, swan_C2)     ((swan_C1) % (swan_C2))
#define swan_ge_uint8(swan_C1, swan_C2)      ((swan_C1) >= (swan_C2))
#define swan_gt_uint8(swan_C1, swan_C2)      ((swan_C1) > (swan_C2))
#define swan_le_uint8(swan_C1, swan_C2)      ((swan_C1) <= (swan_C2))
#define swan_lt_uint8(swan_C1, swan_C2)      ((swan_C1) < (swan_C2))
#define swan_uminus_uint8(swan_C1)                     (- (swan_C1))
#define swan_lsr_uint8(swan_C1, swan_C2)     ((swan_C1) >> (swan_C2))
#define swan_lxor_uint8(swan_C1, swan_C2)    ((swan_C1) ^ (swan_C2))
#define swan_lor_uint8(swan_C1, swan_C2)     ((swan_C1) | (swan_C2))
#define swan_land_uint8(swan_C1, swan_C2)    ((swan_C1) & (swan_C2))
#define swan_div_uint8(swan_C1, swan_C2)     ((swan_C1) / (swan_C2))
#define swan_mult_uint8(swan_C1, swan_C2)    ((swan_C1) * (swan_C2))
#define swan_minus_uint8(swan_C1, swan_C2)   ((swan_C1) - (swan_C2))
#define swan_plus_uint8(swan_C1, swan_C2)    ((swan_C1) + (swan_C2))
#define swan_diff_uint8(swan_C1, swan_C2)    ((swan_C1) != (swan_C2))
#define swan_eq_uint8(swan_C1, swan_C2)      ((swan_C1) == (swan_C2))

#define swan_mod_int64(swan_C1, swan_C2)     ((swan_C1) % (swan_C2))
#define swan_ge_int64(swan_C1, swan_C2)      ((swan_C1) >= (swan_C2))
#define swan_gt_int64(swan_C1, swan_C2)      ((swan_C1) > (swan_C2))
#define swan_le_int64(swan_C1, swan_C2)      ((swan_C1) <= (swan_C2))
#define swan_lt_int64(swan_C1, swan_C2)      ((swan_C1) < (swan_C2))
#define swan_uminus_int64(swan_C1)                     (- (swan_C1))
#define swan_div_int64(swan_C1, swan_C2)     ((swan_C1) / (swan_C2))
#define swan_mult_int64(swan_C1, swan_C2)    ((swan_C1) * (swan_C2))
#define swan_minus_int64(swan_C1, swan_C2)   ((swan_C1) - (swan_C2))
#define swan_plus_int64(swan_C1, swan_C2)    ((swan_C1) + (swan_C2))
#define swan_diff_int64(swan_C1, swan_C2)    ((swan_C1) != (swan_C2))
#define swan_eq_int64(swan_C1, swan_C2)      ((swan_C1) == (swan_C2))

#define swan_mod_int32(swan_C1, swan_C2)     ((swan_C1) % (swan_C2))
#define swan_ge_int32(swan_C1, swan_C2)      ((swan_C1) >= (swan_C2))
#define swan_gt_int32(swan_C1, swan_C2)      ((swan_C1) > (swan_C2))
#define swan_le_int32(swan_C1, swan_C2)      ((swan_C1) <= (swan_C2))
#define swan_lt_int32(swan_C1, swan_C2)      ((swan_C1) < (swan_C2))
#define swan_uminus_int32(swan_C1)                     (- (swan_C1))
#define swan_div_int32(swan_C1, swan_C2)     ((swan_C1) / (swan_C2))
#define swan_mult_int32(swan_C1, swan_C2)    ((swan_C1) * (swan_C2))
#define swan_minus_int32(swan_C1, swan_C2)   ((swan_C1) - (swan_C2))
#define swan_plus_int32(swan_C1, swan_C2)    ((swan_C1) + (swan_C2))
#define swan_diff_int32(swan_C1, swan_C2)    ((swan_C1) != (swan_C2))
#define swan_eq_int32(swan_C1, swan_C2)      ((swan_C1) == (swan_C2))

#define swan_mod_int16(swan_C1, swan_C2)     ((swan_C1) % (swan_C2))
#define swan_ge_int16(swan_C1, swan_C2)      ((swan_C1) >= (swan_C2))
#define swan_gt_int16(swan_C1, swan_C2)      ((swan_C1) > (swan_C2))
#define swan_le_int16(swan_C1, swan_C2)      ((swan_C1) <= (swan_C2))
#define swan_lt_int16(swan_C1, swan_C2)      ((swan_C1) < (swan_C2))
#define swan_uminus_int16(swan_C1)                     (- (swan_C1))
#define swan_div_int16(swan_C1, swan_C2)     ((swan_C1) / (swan_C2))
#define swan_mult_int16(swan_C1, swan_C2)    ((swan_C1) * (swan_C2))
#define swan_minus_int16(swan_C1, swan_C2)   ((swan_C1) - (swan_C2))
#define swan_plus_int16(swan_C1, swan_C2)    ((swan_C1) + (swan_C2))
#define swan_diff_int16(swan_C1, swan_C2)    ((swan_C1) != (swan_C2))
#define swan_eq_int16(swan_C1, swan_C2)      ((swan_C1) == (swan_C2))

#define swan_mod_int8(swan_C1, swan_C2)      ((swan_C1) % (swan_C2))
#define swan_ge_int8(swan_C1, swan_C2)       ((swan_C1) >= (swan_C2))
#define swan_gt_int8(swan_C1, swan_C2)       ((swan_C1) > (swan_C2))
#define swan_le_int8(swan_C1, swan_C2)       ((swan_C1) <= (swan_C2))
#define swan_lt_int8(swan_C1, swan_C2)       ((swan_C1) < (swan_C2))
#define swan_uminus_int8(swan_C1)                      (- (swan_C1))
#define swan_div_int8(swan_C1, swan_C2)      ((swan_C1) / (swan_C2))
#define swan_mult_int8(swan_C1, swan_C2)     ((swan_C1) * (swan_C2))
#define swan_minus_int8(swan_C1, swan_C2)    ((swan_C1) - (swan_C2))
#define swan_plus_int8(swan_C1, swan_C2)     ((swan_C1) + (swan_C2))
#define swan_diff_int8(swan_C1, swan_C2)     ((swan_C1) != (swan_C2))
#define swan_eq_int8(swan_C1, swan_C2)       ((swan_C1) == (swan_C2))

#define swan_diff_char(swan_C1, swan_C2)     ((swan_C1) != (swan_C2))
#define swan_eq_char(swan_C1, swan_C2)       ((swan_C1) == (swan_C2))

#define swan_diff_bool(swan_C1, swan_C2)     ((swan_C1) != (swan_C2))
#define swan_eq_bool(swan_C1, swan_C2)       ((swan_C1) == (swan_C2))
#define swan_or(swan_C1, swan_C2)            ((swan_C1) | (swan_C2))
#define swan_and(swan_C1, swan_C2)           ((swan_C1) & (swan_C2))
#define swan_xor(swan_C1, swan_C2)           ((swan_C1) ^ (swan_C2))
#define swan_not(swan_C1)                    (swan_true ^ (swan_C1))
#define swan_cond(swan_C1)                   (swan_C1)

#define swan_diff(swan_C1, swan_C2)          ((swan_C1) != (swan_C2))
#define swan_eq(swan_C1, swan_C2)            ((swan_C1) == (swan_C2))
#define swan_incr(swan_C1)                   ((swan_C1)++)
#define swan_index(swan_C1, swan_C2)         ((swan_C1)[(swan_C2)])

#endif /* SWAN_WRAP_C_OPS */

{{ FMI_HOOK_END }}

#endif /* SWAN_CONFIG_H_ */
