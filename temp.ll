; ModuleID = 'my_program'
source_filename = "my_program.c"
target datalayout = "e-m:e-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-unknown-linux-gnu"

@x = common global float 3, align 4
load float, float* @x, align 4
load float, float* @3.0, align 4
br i1 %cond, label %then, label %else
then:
@b = common global float 10, align 4
load float, float* @5.0, align 4
call void @print()
br label %end_if
else:
br label %end_if
end_if: