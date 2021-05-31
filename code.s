	.globl main
main:
	push %ebp
	movl %esp, %ebp
	movl $10, %eax 
	push %eax
	movl $2, %eax 
	pop %ecx
	push %eax
	push %ecx
	pop %eax
	pop %ecx
	cdq
	idivl %ecx
	push %eax
	movl $3, %eax 
	pop %ecx
	push %eax
	push %ecx
	pop %eax
	pop %ecx
	subl %ecx, %eax
	push %eax
	movl $2, %eax 
	push %eax
	movl $4, %eax 
	push %eax
	movl $3, %eax 
	pop %ecx
	push %eax
	push %ecx
	pop %eax
	pop %ecx
	subl %ecx, %eax
	pop %ecx
	imul %ecx, %eax
	pop %ecx
	push %eax
	push %ecx
	pop %eax
	pop %ecx
	subl %ecx, %eax
	push %eax
	movl $16, %eax 
	push %eax
	movl $2, %eax 
	pop %ecx
	push %eax
	push %ecx
	pop %eax
	pop %ecx
	shr %ecx, %eax
	push %eax
	movl $1, %eax 
	push %eax
	movl $3, %eax 
	pop %ecx
	push %eax
	push %ecx
	pop %eax
	pop %ecx
	shl %ecx, %eax
	pop %ecx
	imul %ecx, %eax
	pop %ecx
	addl %ecx, %eax
	push %eax
	movl $13, %eax 
	push %eax
	movl $2, %eax 
	pop %ecx
	push %eax
	push %ecx
	pop %eax
	pop %ecx
	cdq
	idivl %ecx
	movl %edx, %eax 
	pop %ecx
	addl %ecx, %eax
	pushl %eax
	movl -4(%ebp), %eax
	push %eax
	movl $5, %eax 
	pop %ecx
	cmpl %eax, %ecx
	movl $0, %eax
	setg %al
	cmpl $0, %eax
	je _else0
	movl -4(%ebp), %eax
	push %eax
	movl $2, %eax 
	pop %ecx
	push %eax
	push %ecx
	pop %eax
	pop %ecx
	subl %ecx, %eax
	jmp _end_if0
_else0:
	movl $33, %eax 
_end_if0:
	movl %eax, -4(%ebp)
	movl $2, %eax 
	push %eax
	movl $2, %eax 
	pop %ecx
	and %ecx, %eax
	push %eax
	movl $4, %eax 
	push %eax
	movl -4(%ebp), %eax
	pop %ecx
	xor %ecx, %eax
	pop %ecx
	or %ecx, %eax
	pushl %eax
	movl -4(%ebp), %eax
	push %eax
	movl $32, %eax 
	pop %ecx
	cmpl %eax, %ecx
	movl $0, %eax
	sete %al
	cmpl $0, %eax
	je _else1
	movl -4(%ebp), %eax
	push %eax
	movl -8(%ebp), %eax
	pop %ecx
	addl %ecx, %eax
	push %eax
	movl -4(%ebp), %eax
	pop %ecx
	push %eax
	push %ecx
	pop %eax
	pop %ecx
	subl %ecx, %eax
	movl %eax, -8(%ebp)
	addl $0, %esp
	jmp _end_if1
_else1:
	movl $34, %eax 
	movl %eax, -8(%ebp)
	addl $0, %esp
_end_if1:
	movl $3, %eax 
	pushl %eax
	addl $4, %esp
_loop_begin0:
	movl -8(%ebp), %eax
	push %eax
	movl $40, %eax 
	pop %ecx
	cmpl %eax, %ecx
	movl $0, %eax
	setl %al
	cmpl $0, %eax
	je _loop_end0
	movl -8(%ebp), %eax
	push %eax
	movl $2, %eax 
	pop %ecx
	addl %ecx, %eax
	movl %eax, -8(%ebp)
	addl $0, %esp
	jmp _loop_begin0
_loop_end0:
_loop_begin1:
_loop_begin2:
	movl -8(%ebp), %eax
	push %eax
	movl $1, %eax 
	pop %ecx
	push %eax
	push %ecx
	pop %eax
	pop %ecx
	subl %ecx, %eax
	movl %eax, -8(%ebp)
	addl $0, %esp
	movl -8(%ebp), %eax
	push %eax
	movl $38, %eax 
	pop %ecx
	cmpl %eax, %ecx
	movl $0, %eax
	setge %al
	cmpl $0, %eax
	jne _loop_begin2
	addl $0, %esp
	movl -8(%ebp), %eax
	push %eax
	movl $500, %eax 
	pop %ecx
	cmpl %eax, %ecx
	movl $0, %eax
	setge %al
	cmpl $0, %eax
	jne _loop_begin1
	movl $0, %eax 
	pushl %eax
_loop_begin3:
	movl -12(%ebp), %eax
	push %eax
	movl $5, %eax 
	pop %ecx
	cmpl %eax, %ecx
	movl $0, %eax
	setl %al
	cmpl $0, %eax
	je _loop_end1
	movl -8(%ebp), %eax
	push %eax
	movl -12(%ebp), %eax
	pop %ecx
	addl %ecx, %eax
	movl %eax, -8(%ebp)
	addl $0, %esp
	movl $1, %eax 
	addl %eax, -12(%ebp)
	jmp _loop_begin3
_loop_end1:
	addl $4, %esp
	movl -8(%ebp), %eax
	movl %ebp, %esp
	pop %ebp
	ret
