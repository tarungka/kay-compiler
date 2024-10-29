mov rax, 3
mov [x], rax
mov rax, [x]
cmp rax, [3.0]
je end_if
mov rax, 10
mov [b], rax
push [5.0]
call print
pop rax
end_if: