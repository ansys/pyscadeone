/* Copyright (c) 2024 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
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

{{ SWAN_CONFIG_HOOK_BEGIN }}

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

# define swan_lit_i64 INT64_C
# define swan_lit_u64 UINT64_C

#elif defined(_MSC_VER)

typedef unsigned __int8  swan_uint8;
typedef          __int8  swan_int8;
typedef unsigned __int16 swan_uint16;
typedef          __int16 swan_int16;
typedef unsigned __int32 swan_uint32;
typedef          __int32 swan_int32;
typedef unsigned __int64 swan_uint64;
typedef          __int64 swan_int64;

# define swan_lit_i64(v) (v ## i64)
# define swan_lit_u64(v) (v ## ui64)

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

#define swan_lit_f32(swan_C1)  ((swan_float32) (swan_C1))
#define swan_lit_f64(swan_C1)  ((swan_float64) (swan_C1))

#define swan_lit_size(swan_C1) ((swan_size) (swan_C1))

#define swan_lit_u32(swan_C1)  ((swan_uint32) (swan_C1))
#define swan_lit_u16(swan_C1)  ((swan_uint16) (swan_C1))
#define swan_lit_u8(swan_C1)   ((swan_uint8)  (swan_C1))

#define swan_lit_i32(swan_C1)  ((swan_int32) (swan_C1))
#define swan_lit_i16(swan_C1)  ((swan_int16) (swan_C1))
#define swan_lit_i8(swan_C1)   ((swan_int8)  (swan_C1))

#define swan_lit_char(swan_C1) ((swan_char)  (swan_C1))



#define swan_lsl_u64(swan_C1, swan_C2)                          \
  ((swan_uint64) ((swan_C1) << (swan_C2)) & 0xffffffffffffffffU)
#define swan_lsl_u32(swan_C1, swan_C2)                          \
  ((swan_uint32) ((swan_C1) << (swan_C2)) & 0xffffffffU)
#define swan_lsl_u16(swan_C1, swan_C2)                          \
  ((swan_uint16) ((swan_C1) << (swan_C2)) & 0xffffU)
#define swan_lsl_u8(swan_C1, swan_C2)                           \
  ((swan_uint8)  ((swan_C1) << (swan_C2)) & 0xffU)

#define swan_lnot_u64(swan_C1)           ((swan_C1) ^ 0xffffffffffffffffU)
#define swan_lnot_u32(swan_C1)           ((swan_C1) ^ 0xffffffffU)
#define swan_lnot_u16(swan_C1)           ((swan_C1) ^ 0xffffU)
#define swan_lnot_u8(swan_C1)            ((swan_C1) ^ 0xffU)




#ifdef SWAN_WRAP_C_OPS

#define swan_f64_to_f32(swan_C1)    ((swan_float32) (swan_C1))
#define swan_size_to_f32(swan_C1)   ((swan_float32) (swan_C1))
#define swan_u64_to_f32(swan_C1)    ((swan_float32) (swan_C1))
#define swan_u32_to_f32(swan_C1)    ((swan_float32) (swan_C1))
#define swan_u16_to_f32(swan_C1)    ((swan_float32) (swan_C1))
#define swan_u8_to_f32(swan_C1)     ((swan_float32) (swan_C1))
#define swan_i64_to_f32(swan_C1)    ((swan_float32) (swan_C1))
#define swan_i32_to_f32(swan_C1)    ((swan_float32) (swan_C1))
#define swan_i16_to_f32(swan_C1)    ((swan_float32) (swan_C1))
#define swan_i8_to_f32(swan_C1)     ((swan_float32) (swan_C1))
#define swan_f32_to_f64(swan_C1)    ((swan_float64) (swan_C1))

#define swan_size_to_f64(swan_C1)   ((swan_float64) (swan_C1))
#define swan_u64_to_f64(swan_C1)    ((swan_float64) (swan_C1))
#define swan_u32_to_f64(swan_C1)    ((swan_float64) (swan_C1))
#define swan_u16_to_f64(swan_C1)    ((swan_float64) (swan_C1))
#define swan_u8_to_f64(swan_C1)     ((swan_float64) (swan_C1))
#define swan_i64_to_f64(swan_C1)    ((swan_float64) (swan_C1))
#define swan_i32_to_f64(swan_C1)    ((swan_float64) (swan_C1))
#define swan_i16_to_f64(swan_C1)    ((swan_float64) (swan_C1))
#define swan_i8_to_f64(swan_C1)     ((swan_float64) (swan_C1))

#define swan_f32_to_size(swan_C1)   ((swan_size) (swan_C1))
#define swan_f64_to_size(swan_C1)   ((swan_size) (swan_C1))
#define swan_u64_to_size(swan_C1)   ((swan_size) (swan_C1))
#define swan_u32_to_size(swan_C1)   ((swan_size) (swan_C1))
#define swan_u16_to_size(swan_C1)   ((swan_size) (swan_C1))
#define swan_u8_to_size(swan_C1)    ((swan_size) (swan_C1))
#define swan_i64_to_size(swan_C1)   ((swan_size) (swan_C1))
#define swan_i32_to_size(swan_C1)   ((swan_size) (swan_C1))
#define swan_i16_to_size(swan_C1)   ((swan_size) (swan_C1))
#define swan_i8_to_size(swan_C1)    ((swan_size) (swan_C1))

#define swan_f32_to_u64(swan_C1)    ((swan_uint64) (swan_C1))
#define swan_f64_to_u64(swan_C1)    ((swan_uint64) (swan_C1))
#define swan_size_to_u64(swan_C1)   ((swan_uint64) (swan_C1))
#define swan_u32_to_u64(swan_C1)    ((swan_uint64) (swan_C1))
#define swan_u16_to_u64(swan_C1)    ((swan_uint64) (swan_C1))
#define swan_u8_to_u64(swan_C1)     ((swan_uint64) (swan_C1))
#define swan_i64_to_u64(swan_C1)    ((swan_uint64) (swan_C1))
#define swan_i32_to_u64(swan_C1)    ((swan_uint64) (swan_C1))
#define swan_i16_to_u64(swan_C1)    ((swan_uint64) (swan_C1))
#define swan_i8_to_u64(swan_C1)     ((swan_uint64) (swan_C1))

#define swan_f32_to_u32(swan_C1)    ((swan_uint32) (swan_C1))
#define swan_f64_to_u32(swan_C1)    ((swan_uint32) (swan_C1))
#define swan_size_to_u32(swan_C1)   ((swan_uint32) (swan_C1))
#define swan_u64_to_u32(swan_C1)    ((swan_uint32) (swan_C1))
#define swan_u16_to_u32(swan_C1)    ((swan_uint32) (swan_C1))
#define swan_u8_to_u32(swan_C1)     ((swan_uint32) (swan_C1))
#define swan_i64_to_u32(swan_C1)    ((swan_uint32) (swan_C1))
#define swan_i32_to_u32(swan_C1)    ((swan_uint32) (swan_C1))
#define swan_i16_to_u32(swan_C1)    ((swan_uint32) (swan_C1))
#define swan_i8_to_u32(swan_C1)     ((swan_uint32) (swan_C1))

#define swan_f32_to_u16(swan_C1)    ((swan_uint16) (swan_C1))
#define swan_f64_to_u16(swan_C1)    ((swan_uint16) (swan_C1))
#define swan_size_to_u16(swan_C1)   ((swan_uint16) (swan_C1))
#define swan_u64_to_u16(swan_C1)    ((swan_uint16) (swan_C1))
#define swan_u32_to_u16(swan_C1)    ((swan_uint16) (swan_C1))
#define swan_u8_to_u16(swan_C1)     ((swan_uint16) (swan_C1))
#define swan_i64_to_u16(swan_C1)    ((swan_uint16) (swan_C1))
#define swan_i32_to_u16(swan_C1)    ((swan_uint16) (swan_C1))
#define swan_i16_to_u16(swan_C1)    ((swan_uint16) (swan_C1))
#define swan_i8_to_u16(swan_C1)     ((swan_uint16) (swan_C1))

#define swan_f32_to_u8(swan_C1)     ((swan_uint8) (swan_C1))
#define swan_f64_to_u8(swan_C1)     ((swan_uint8) (swan_C1))
#define swan_size_to_u8(swan_C1)    ((swan_uint8) (swan_C1))
#define swan_u64_to_u8(swan_C1)     ((swan_uint8) (swan_C1))
#define swan_u32_to_u8(swan_C1)     ((swan_uint8) (swan_C1))
#define swan_u16_to_u8(swan_C1)     ((swan_uint8) (swan_C1))
#define swan_i64_to_u8(swan_C1)     ((swan_uint8) (swan_C1))
#define swan_i32_to_u8(swan_C1)     ((swan_uint8) (swan_C1))
#define swan_i16_to_u8(swan_C1)     ((swan_uint8) (swan_C1))
#define swan_i8_to_u8(swan_C1)      ((swan_uint8) (swan_C1))

#define swan_f32_to_i64(swan_C1)    ((swan_int64) (swan_C1))
#define swan_f64_to_i64(swan_C1)    ((swan_int64) (swan_C1))
#define swan_size_to_i64(swan_C1)   ((swan_int64) (swan_C1))
#define swan_u64_to_i64(swan_C1)    ((swan_int64) (swan_C1))
#define swan_u32_to_i64(swan_C1)    ((swan_int64) (swan_C1))
#define swan_u16_to_i64(swan_C1)    ((swan_int64) (swan_C1))
#define swan_u8_to_i64(swan_C1)     ((swan_int64) (swan_C1))
#define swan_i32_to_i64(swan_C1)    ((swan_int64) (swan_C1))
#define swan_i16_to_i64(swan_C1)    ((swan_int64) (swan_C1))
#define swan_i8_to_i64(swan_C1)     ((swan_int64) (swan_C1))

#define swan_f32_to_i32(swan_C1)    ((swan_int32) (swan_C1))
#define swan_f64_to_i32(swan_C1)    ((swan_int32) (swan_C1))
#define swan_size_to_i32(swan_C1)   ((swan_int32) (swan_C1))
#define swan_u64_to_i32(swan_C1)    ((swan_int32) (swan_C1))
#define swan_u32_to_i32(swan_C1)    ((swan_int32) (swan_C1))
#define swan_u16_to_i32(swan_C1)    ((swan_int32) (swan_C1))
#define swan_u8_to_i32(swan_C1)     ((swan_int32) (swan_C1))
#define swan_i64_to_i32(swan_C1)    ((swan_int32) (swan_C1))
#define swan_i16_to_i32(swan_C1)    ((swan_int32) (swan_C1))
#define swan_i8_to_i32(swan_C1)     ((swan_int32) (swan_C1))

#define swan_f32_to_i16(swan_C1)    ((swan_int16) (swan_C1))
#define swan_f64_to_i16(swan_C1)    ((swan_int16) (swan_C1))
#define swan_size_to_i16(swan_C1)   ((swan_int16) (swan_C1))
#define swan_u64_to_i16(swan_C1)    ((swan_int16) (swan_C1))
#define swan_u32_to_i16(swan_C1)    ((swan_int16) (swan_C1))
#define swan_u16_to_i16(swan_C1)    ((swan_int16) (swan_C1))
#define swan_u8_to_i16(swan_C1)     ((swan_int16) (swan_C1))
#define swan_i64_to_i16(swan_C1)    ((swan_int16) (swan_C1))
#define swan_i32_to_i16(swan_C1)    ((swan_int16) (swan_C1))
#define swan_i8_to_i16(swan_C1)     ((swan_int16) (swan_C1))

#define swan_f32_to_i8(swan_C1)     ((swan_int8) (swan_C1))
#define swan_f64_to_i8(swan_C1)     ((swan_int8) (swan_C1))
#define swan_size_to_i8(swan_C1)    ((swan_int8) (swan_C1))
#define swan_u64_to_i8(swan_C1)     ((swan_int8) (swan_C1))
#define swan_u32_to_i8(swan_C1)     ((swan_int8) (swan_C1))
#define swan_u16_to_i8(swan_C1)     ((swan_int8) (swan_C1))
#define swan_u8_to_i8(swan_C1)      ((swan_int8) (swan_C1))
#define swan_i64_to_i8(swan_C1)     ((swan_int8) (swan_C1))
#define swan_i32_to_i8(swan_C1)     ((swan_int8) (swan_C1))
#define swan_i16_to_i8(swan_C1)     ((swan_int8) (swan_C1))

#define swan_ge_f32(swan_C1, swan_C2)      ((swan_C1) >= (swan_C2))
#define swan_gt_f32(swan_C1, swan_C2)      ((swan_C1) > (swan_C2))
#define swan_le_f32(swan_C1, swan_C2)      ((swan_C1) <= (swan_C2))
#define swan_lt_f32(swan_C1, swan_C2)      ((swan_C1) < (swan_C2))
#define swan_uminus_f32(swan_C1)                     (- (swan_C1))
#define swan_div_f32(swan_C1, swan_C2)     ((swan_C1) / (swan_C2))
#define swan_mult_f32(swan_C1, swan_C2)    ((swan_C1) * (swan_C2))
#define swan_minus_f32(swan_C1, swan_C2)   ((swan_C1) - (swan_C2))
#define swan_plus_f32(swan_C1, swan_C2)    ((swan_C1) + (swan_C2))
#define swan_diff_f32(swan_C1, swan_C2)    ((swan_C1) != (swan_C2))
#define swan_eq_f32(swan_C1, swan_C2)      ((swan_C1) == (swan_C2))

#define swan_ge_f64(swan_C1, swan_C2)      ((swan_C1) >= (swan_C2))
#define swan_gt_f64(swan_C1, swan_C2)      ((swan_C1) > (swan_C2))
#define swan_le_f64(swan_C1, swan_C2)      ((swan_C1) <= (swan_C2))
#define swan_lt_f64(swan_C1, swan_C2)      ((swan_C1) < (swan_C2))
#define swan_uminus_f64(swan_C1)                     (- (swan_C1))
#define swan_div_f64(swan_C1, swan_C2)     ((swan_C1) / (swan_C2))
#define swan_mult_f64(swan_C1, swan_C2)    ((swan_C1) * (swan_C2))
#define swan_minus_f64(swan_C1, swan_C2)   ((swan_C1) - (swan_C2))
#define swan_plus_f64(swan_C1, swan_C2)    ((swan_C1) + (swan_C2))
#define swan_diff_f64(swan_C1, swan_C2)    ((swan_C1) != (swan_C2))
#define swan_eq_f64(swan_C1, swan_C2)      ((swan_C1) == (swan_C2))

#define swan_mod_size(swan_C1, swan_C2)    ((swan_C1) % (swan_C2))
#define swan_gt_size(swan_C1, swan_C2)     ((swan_C1) > (swan_C2))
#define swan_le_size(swan_C1, swan_C2)     ((swan_C1) <= (swan_C2))
#define swan_lt_size(swan_C1, swan_C2)     ((swan_C1) < (swan_C2))
#define swan_uminus_size(swan_C1)                    (- (swan_C1))
#define swan_minus_size(swan_C1, swan_C2)  ((swan_C1) - (swan_C2))
#define swan_plus_size(swan_C1, swan_C2)   ((swan_C1) + (swan_C2))
#define swan_eq_size(swan_C1, swan_C2)     ((swan_C1) == (swan_C2))

#define swan_mod_u64(swan_C1, swan_C2)     ((swan_C1) % (swan_C2))
#define swan_ge_u64(swan_C1, swan_C2)      ((swan_C1) >= (swan_C2))
#define swan_gt_u64(swan_C1, swan_C2)      ((swan_C1) > (swan_C2))
#define swan_le_u64(swan_C1, swan_C2)      ((swan_C1) <= (swan_C2))
#define swan_lt_u64(swan_C1, swan_C2)      ((swan_C1) < (swan_C2))
#define swan_uminus_u64(swan_C1)                     (- (swan_C1))
#define swan_lsr_u64(swan_C1, swan_C2)     ((swan_C1) >> (swan_C2))
#define swan_lxor_u64(swan_C1, swan_C2)    ((swan_C1) ^ (swan_C2))
#define swan_lor_u64(swan_C1, swan_C2)     ((swan_C1) | (swan_C2))
#define swan_land_u64(swan_C1, swan_C2)    ((swan_C1) & (swan_C2))
#define swan_div_u64(swan_C1, swan_C2)     ((swan_C1) / (swan_C2))
#define swan_mult_u64(swan_C1, swan_C2)    ((swan_C1) * (swan_C2))
#define swan_minus_u64(swan_C1, swan_C2)   ((swan_C1) - (swan_C2))
#define swan_plus_u64(swan_C1, swan_C2)    ((swan_C1) + (swan_C2))
#define swan_diff_u64(swan_C1, swan_C2)    ((swan_C1) != (swan_C2))
#define swan_eq_u64(swan_C1, swan_C2)      ((swan_C1) == (swan_C2))

#define swan_mod_u32(swan_C1, swan_C2)     ((swan_C1) % (swan_C2))
#define swan_ge_u32(swan_C1, swan_C2)      ((swan_C1) >= (swan_C2))
#define swan_gt_u32(swan_C1, swan_C2)      ((swan_C1) > (swan_C2))
#define swan_le_u32(swan_C1, swan_C2)      ((swan_C1) <= (swan_C2))
#define swan_lt_u32(swan_C1, swan_C2)      ((swan_C1) < (swan_C2))
#define swan_uminus_u32(swan_C1)                     (- (swan_C1))
#define swan_lsr_u32(swan_C1, swan_C2)     ((swan_C1) >> (swan_C2))
#define swan_lxor_u32(swan_C1, swan_C2)    ((swan_C1) ^ (swan_C2))
#define swan_lor_u32(swan_C1, swan_C2)     ((swan_C1) | (swan_C2))
#define swan_land_u32(swan_C1, swan_C2)    ((swan_C1) & (swan_C2))
#define swan_div_u32(swan_C1, swan_C2)     ((swan_C1) / (swan_C2))
#define swan_mult_u32(swan_C1, swan_C2)    ((swan_C1) * (swan_C2))
#define swan_minus_u32(swan_C1, swan_C2)   ((swan_C1) - (swan_C2))
#define swan_plus_u32(swan_C1, swan_C2)    ((swan_C1) + (swan_C2))
#define swan_diff_u32(swan_C1, swan_C2)    ((swan_C1) != (swan_C2))
#define swan_eq_u32(swan_C1, swan_C2)      ((swan_C1) == (swan_C2))

#define swan_mod_u16(swan_C1, swan_C2)     ((swan_C1) % (swan_C2))
#define swan_ge_u16(swan_C1, swan_C2)      ((swan_C1) >= (swan_C2))
#define swan_gt_u16(swan_C1, swan_C2)      ((swan_C1) > (swan_C2))
#define swan_le_u16(swan_C1, swan_C2)      ((swan_C1) <= (swan_C2))
#define swan_lt_u16(swan_C1, swan_C2)      ((swan_C1) < (swan_C2))
#define swan_uminus_u16(swan_C1)                     (- (swan_C1))
#define swan_lsr_u16(swan_C1, swan_C2)     ((swan_C1) >> (swan_C2))
#define swan_lxor_u16(swan_C1, swan_C2)    ((swan_C1) ^ (swan_C2))
#define swan_lor_u16(swan_C1, swan_C2)     ((swan_C1) | (swan_C2))
#define swan_land_u16(swan_C1, swan_C2)    ((swan_C1) & (swan_C2))
#define swan_div_u16(swan_C1, swan_C2)     ((swan_C1) / (swan_C2))
#define swan_mult_u16(swan_C1, swan_C2)    ((swan_C1) * (swan_C2))
#define swan_minus_u16(swan_C1, swan_C2)   ((swan_C1) - (swan_C2))
#define swan_plus_u16(swan_C1, swan_C2)    ((swan_C1) + (swan_C2))
#define swan_diff_u16(swan_C1, swan_C2)    ((swan_C1) != (swan_C2))
#define swan_eq_u16(swan_C1, swan_C2)      ((swan_C1) == (swan_C2))

#define swan_mod_u8(swan_C1, swan_C2)      ((swan_C1) % (swan_C2))
#define swan_ge_u8(swan_C1, swan_C2)       ((swan_C1) >= (swan_C2))
#define swan_gt_u8(swan_C1, swan_C2)       ((swan_C1) > (swan_C2))
#define swan_le_u8(swan_C1, swan_C2)       ((swan_C1) <= (swan_C2))
#define swan_lt_u8(swan_C1, swan_C2)       ((swan_C1) < (swan_C2))
#define swan_uminus_u8(swan_C1)                      (- (swan_C1))
#define swan_lsr_u8(swan_C1, swan_C2)      ((swan_C1) >> (swan_C2))
#define swan_lxor_u8(swan_C1, swan_C2)     ((swan_C1) ^ (swan_C2))
#define swan_lor_u8(swan_C1, swan_C2)      ((swan_C1) | (swan_C2))
#define swan_land_u8(swan_C1, swan_C2)     ((swan_C1) & (swan_C2))
#define swan_div_u8(swan_C1, swan_C2)      ((swan_C1) / (swan_C2))
#define swan_mult_u8(swan_C1, swan_C2)     ((swan_C1) * (swan_C2))
#define swan_minus_u8(swan_C1, swan_C2)    ((swan_C1) - (swan_C2))
#define swan_plus_u8(swan_C1, swan_C2)     ((swan_C1) + (swan_C2))
#define swan_diff_u8(swan_C1, swan_C2)     ((swan_C1) != (swan_C2))
#define swan_eq_u8(swan_C1, swan_C2)       ((swan_C1) == (swan_C2))

#define swan_mod_i64(swan_C1, swan_C2)     ((swan_C1) % (swan_C2))
#define swan_ge_i64(swan_C1, swan_C2)      ((swan_C1) >= (swan_C2))
#define swan_gt_i64(swan_C1, swan_C2)      ((swan_C1) > (swan_C2))
#define swan_le_i64(swan_C1, swan_C2)      ((swan_C1) <= (swan_C2))
#define swan_lt_i64(swan_C1, swan_C2)      ((swan_C1) < (swan_C2))
#define swan_uminus_i64(swan_C1)                     (- (swan_C1))
#define swan_div_i64(swan_C1, swan_C2)     ((swan_C1) / (swan_C2))
#define swan_mult_i64(swan_C1, swan_C2)    ((swan_C1) * (swan_C2))
#define swan_minus_i64(swan_C1, swan_C2)   ((swan_C1) - (swan_C2))
#define swan_plus_i64(swan_C1, swan_C2)    ((swan_C1) + (swan_C2))
#define swan_diff_i64(swan_C1, swan_C2)    ((swan_C1) != (swan_C2))
#define swan_eq_i64(swan_C1, swan_C2)      ((swan_C1) == (swan_C2))

#define swan_mod_i32(swan_C1, swan_C2)     ((swan_C1) % (swan_C2))
#define swan_ge_i32(swan_C1, swan_C2)      ((swan_C1) >= (swan_C2))
#define swan_gt_i32(swan_C1, swan_C2)      ((swan_C1) > (swan_C2))
#define swan_le_i32(swan_C1, swan_C2)      ((swan_C1) <= (swan_C2))
#define swan_lt_i32(swan_C1, swan_C2)      ((swan_C1) < (swan_C2))
#define swan_uminus_i32(swan_C1)                     (- (swan_C1))
#define swan_div_i32(swan_C1, swan_C2)     ((swan_C1) / (swan_C2))
#define swan_mult_i32(swan_C1, swan_C2)    ((swan_C1) * (swan_C2))
#define swan_minus_i32(swan_C1, swan_C2)   ((swan_C1) - (swan_C2))
#define swan_plus_i32(swan_C1, swan_C2)    ((swan_C1) + (swan_C2))
#define swan_diff_i32(swan_C1, swan_C2)    ((swan_C1) != (swan_C2))
#define swan_eq_i32(swan_C1, swan_C2)      ((swan_C1) == (swan_C2))

#define swan_mod_i16(swan_C1, swan_C2)     ((swan_C1) % (swan_C2))
#define swan_ge_i16(swan_C1, swan_C2)      ((swan_C1) >= (swan_C2))
#define swan_gt_i16(swan_C1, swan_C2)      ((swan_C1) > (swan_C2))
#define swan_le_i16(swan_C1, swan_C2)      ((swan_C1) <= (swan_C2))
#define swan_lt_i16(swan_C1, swan_C2)      ((swan_C1) < (swan_C2))
#define swan_uminus_i16(swan_C1)                     (- (swan_C1))
#define swan_div_i16(swan_C1, swan_C2)     ((swan_C1) / (swan_C2))
#define swan_mult_i16(swan_C1, swan_C2)    ((swan_C1) * (swan_C2))
#define swan_minus_i16(swan_C1, swan_C2)   ((swan_C1) - (swan_C2))
#define swan_plus_i16(swan_C1, swan_C2)    ((swan_C1) + (swan_C2))
#define swan_diff_i16(swan_C1, swan_C2)    ((swan_C1) != (swan_C2))
#define swan_eq_i16(swan_C1, swan_C2)      ((swan_C1) == (swan_C2))

#define swan_mod_i8(swan_C1, swan_C2)      ((swan_C1) % (swan_C2))
#define swan_ge_i8(swan_C1, swan_C2)       ((swan_C1) >= (swan_C2))
#define swan_gt_i8(swan_C1, swan_C2)       ((swan_C1) > (swan_C2))
#define swan_le_i8(swan_C1, swan_C2)       ((swan_C1) <= (swan_C2))
#define swan_lt_i8(swan_C1, swan_C2)       ((swan_C1) < (swan_C2))
#define swan_uminus_i8(swan_C1)                      (- (swan_C1))
#define swan_div_i8(swan_C1, swan_C2)      ((swan_C1) / (swan_C2))
#define swan_mult_i8(swan_C1, swan_C2)     ((swan_C1) * (swan_C2))
#define swan_minus_i8(swan_C1, swan_C2)    ((swan_C1) - (swan_C2))
#define swan_plus_i8(swan_C1, swan_C2)     ((swan_C1) + (swan_C2))
#define swan_diff_i8(swan_C1, swan_C2)     ((swan_C1) != (swan_C2))
#define swan_eq_i8(swan_C1, swan_C2)       ((swan_C1) == (swan_C2))

#define swan_diff_char(swan_C1, swan_C2)   ((swan_C1) != (swan_C2))
#define swan_eq_char(swan_C1, swan_C2)     ((swan_C1) == (swan_C2))

#define swan_diff_bool(swan_C1, swan_C2)   ((swan_C1) != (swan_C2))
#define swan_eq_bool(swan_C1, swan_C2)     ((swan_C1) == (swan_C2))
#define swan_or(swan_C1, swan_C2)          ((swan_C1) | (swan_C2))
#define swan_and(swan_C1, swan_C2)         ((swan_C1) & (swan_C2))
#define swan_xor(swan_C1, swan_C2)         ((swan_C1) ^ (swan_C2))
#define swan_not(swan_C1)                  (swan_true ^ (swan_C1))
#define swan_cond(swan_C1)                 (swan_C1)

#define swan_diff(swan_C1, swan_C2)        ((swan_C1) != (swan_C2))
#define swan_eq(swan_C1, swan_C2)          ((swan_C1) == (swan_C2))
#define swan_incr(swan_C1)                 ((swan_C1)++)
#define swan_index(swan_C1, swan_C2)       ((swan_C1)[(swan_C2)])

#endif /* SWAN_WRAP_C_OPS */

{{ SWAN_CONFIG_HOOK_END }}

#endif /* SWAN_CONFIG_H_ */
