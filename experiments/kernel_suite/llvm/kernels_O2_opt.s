	.att_syntax
	.file	"kernels.c"
	.text
	.globl	main                            # -- Begin function main
	.prefalign	4, .Lfunc_end0, nop
	.type	main,@function
main:                                   # @main
	.cfi_startproc
# %bb.0:
	pushq	%rbp
	.cfi_def_cfa_offset 16
	.cfi_offset %rbp, -16
	movq	%rsp, %rbp
	.cfi_def_cfa_register %rbp
	pushq	%r14
	pushq	%rbx
	subq	$5504, %rsp                     # imm = 0x1580
	.cfi_offset %rbx, -32
	.cfi_offset %r14, -24
	movq	%fs:40, %rax
	movq	%rax, -24(%rbp)
	movl	$0, -5500(%rbp)
	leaq	-80(%rbp), %rdi
	xorl	%esi, %esi
	movl	$48, %edx
	callq	memset@PLT
	movq	$65536, -80(%rbp)               # imm = 0x10000
	movq	$65536, -48(%rbp)               # imm = 0x10000
	movq	.L__const.main.lx3, %rax
	movq	%rax, -112(%rbp)
	movq	.L__const.main.lx3+8, %rax
	movq	%rax, -104(%rbp)
	movq	.L__const.main.lx3+16, %rax
	movq	%rax, -96(%rbp)
	movq	.L__const.main.b, %rax
	movq	%rax, -128(%rbp)
	movq	.L__const.main.b+8, %rax
	movq	%rax, -120(%rbp)
	leaq	-80(%rbp), %rax
	movq	%rax, -3152(%rbp)
	movq	$6, -3144(%rbp)
	movq	$8, -3136(%rbp)
	movq	$8, -3128(%rbp)
	leaq	-112(%rbp), %rax
	movq	%rax, -3184(%rbp)
	movq	$3, -3176(%rbp)
	movq	$8, -3168(%rbp)
	movq	$8, -3160(%rbp)
	leaq	-128(%rbp), %rax
	movq	%rax, -3216(%rbp)
	movq	$2, -3208(%rbp)
	movq	$8, -3200(%rbp)
	movq	$8, -3192(%rbp)
	leaq	-144(%rbp), %r9
	leaq	-3152(%rbp), %rdi
	leaq	-3184(%rbp), %rcx
	leaq	-3216(%rbp), %r8
	movl	$2, %esi
	movl	$3, %edx
	callq	matvec
	movl	$65536, %edi                    # imm = 0x10000
	movl	$65536, %esi                    # imm = 0x10000
	callq	qmul
	addq	$100, %rax
	movq	%rax, -5472(%rbp)
	movl	$65536, %edi                    # imm = 0x10000
	movl	$131072, %esi                   # imm = 0x20000
	callq	qmul
	addq	$200, %rax
	movq	%rax, -5464(%rbp)
	movq	-144(%rbp), %rcx
	xorl	%eax, %eax
	cmpq	-5472(%rbp), %rcx
	jne	.LBB0_2
# %bb.1:
	movq	-136(%rbp), %rax
	cmpq	-5464(%rbp), %rax
	sete	%al
.LBB0_2:
	movabsq	$.L.str.2, %rsi
	movabsq	$.L.str.1, %rcx
	testb	$1, %al
	cmovneq	%rcx, %rsi
	movq	-144(%rbp), %rdx
	movq	-136(%rbp), %rcx
	movabsq	$.L.str, %rdi
	movb	$0, %al
	callq	printf@PLT
	leaq	-192(%rbp), %rdi
	xorl	%esi, %esi
	movl	$48, %edx
	callq	memset@PLT
	movq	$65536, -192(%rbp)              # imm = 0x10000
	movq	$131072, -184(%rbp)             # imm = 0x20000
	movq	$196608, -176(%rbp)             # imm = 0x30000
	movq	$131072, -168(%rbp)             # imm = 0x20000
	movq	$196608, -160(%rbp)             # imm = 0x30000
	movq	$262144, -152(%rbp)             # imm = 0x40000
	leaq	-192(%rbp), %rax
	movq	%rax, -3248(%rbp)
	movq	$6, -3240(%rbp)
	movq	$8, -3232(%rbp)
	movq	$8, -3224(%rbp)
	leaq	-224(%rbp), %rcx
	leaq	-3152(%rbp), %rdi
	leaq	-3248(%rbp), %rsi
	leaq	-3216(%rbp), %rdx
	callq	batched
	movq	-224(%rbp), %rcx
	xorl	%eax, %eax
	cmpq	-5472(%rbp), %rcx
	jne	.LBB0_4
# %bb.3:
	movq	-216(%rbp), %rax
	cmpq	-5464(%rbp), %rax
	sete	%al
.LBB0_4:
	movabsq	$.L.str.2, %rsi
	movabsq	$.L.str.1, %rcx
	testb	$1, %al
	cmovneq	%rcx, %rsi
	movabsq	$.L.str.3, %rdi
	movb	$0, %al
	callq	printf@PLT
	movq	.L__const.main.sx, %rax
	movq	%rax, -256(%rbp)
	movq	.L__const.main.sx+8, %rax
	movq	%rax, -248(%rbp)
	movq	.L__const.main.sx+16, %rax
	movq	%rax, -240(%rbp)
	leaq	-256(%rbp), %rax
	movq	%rax, -3280(%rbp)
	movq	$3, -3272(%rbp)
	movq	$8, -3264(%rbp)
	movq	$8, -3256(%rbp)
	leaq	-288(%rbp), %rax
	movq	%rax, -3312(%rbp)
	movq	$3, -3304(%rbp)
	movq	$8, -3296(%rbp)
	movq	$8, -3288(%rbp)
	leaq	-3280(%rbp), %rdi
	leaq	-3312(%rbp), %rsi
	callq	softmax
	movq	$0, -5264(%rbp)
	movl	$0, -5220(%rbp)
.LBB0_5:                                # =>This Inner Loop Header: Depth=1
	cmpl	$3, -5220(%rbp)
	jge	.LBB0_8
# %bb.6:                                #   in Loop: Header=BB0_5 Depth=1
	movslq	-5220(%rbp), %rax
	movq	-288(%rbp,%rax,8), %rax
	addq	-5264(%rbp), %rax
	movq	%rax, -5264(%rbp)
# %bb.7:                                #   in Loop: Header=BB0_5 Depth=1
	movl	-5220(%rbp), %eax
	addl	$1, %eax
	movl	%eax, -5220(%rbp)
	jmp	.LBB0_5
.LBB0_8:
	xorl	%eax, %eax
	cmpq	$65534, -5264(%rbp)             # imm = 0xFFFE
	jl	.LBB0_10
# %bb.9:
	cmpq	$65538, -5264(%rbp)             # imm = 0x10002
	setle	%al
.LBB0_10:
	movabsq	$.L.str.2, %rsi
	movabsq	$.L.str.1, %rcx
	testb	$1, %al
	cmovneq	%rcx, %rsi
	movq	-5264(%rbp), %rdx
	movabsq	$.L.str.4, %rdi
	movb	$0, %al
	callq	printf@PLT
	movq	.L__const.main.lx3, %rax
	movq	%rax, -320(%rbp)
	movq	.L__const.main.lx3+8, %rax
	movq	%rax, -312(%rbp)
	movq	.L__const.main.lx3+16, %rax
	movq	%rax, -304(%rbp)
	movq	.L__const.main.lg3, %rax
	movq	%rax, -352(%rbp)
	movq	.L__const.main.lg3+8, %rax
	movq	%rax, -344(%rbp)
	movq	.L__const.main.lg3+16, %rax
	movq	%rax, -336(%rbp)
	leaq	-384(%rbp), %rdi
	xorl	%esi, %esi
	movl	$24, %edx
	callq	memset@PLT
	leaq	-320(%rbp), %rax
	movq	%rax, -3344(%rbp)
	movq	$3, -3336(%rbp)
	movq	$8, -3328(%rbp)
	movq	$8, -3320(%rbp)
	leaq	-352(%rbp), %rax
	movq	%rax, -3376(%rbp)
	movq	$3, -3368(%rbp)
	movq	$8, -3360(%rbp)
	movq	$8, -3352(%rbp)
	leaq	-384(%rbp), %rax
	movq	%rax, -3408(%rbp)
	movq	$3, -3400(%rbp)
	movq	$8, -3392(%rbp)
	movq	$8, -3384(%rbp)
	leaq	-416(%rbp), %rax
	movq	%rax, -3440(%rbp)
	movq	$3, -3432(%rbp)
	movq	$8, -3424(%rbp)
	movq	$8, -3416(%rbp)
	leaq	-3344(%rbp), %rdi
	leaq	-3376(%rbp), %rdx
	leaq	-3408(%rbp), %rcx
	leaq	-3440(%rbp), %r8
	movl	$3, %esi
	callq	layernorm
	movq	$0, -5256(%rbp)
	movl	$0, -5216(%rbp)
.LBB0_11:                               # =>This Inner Loop Header: Depth=1
	cmpl	$3, -5216(%rbp)
	jge	.LBB0_14
# %bb.12:                               #   in Loop: Header=BB0_11 Depth=1
	movslq	-5216(%rbp), %rax
	movq	-416(%rbp,%rax,8), %rax
	addq	-5256(%rbp), %rax
	movq	%rax, -5256(%rbp)
# %bb.13:                               #   in Loop: Header=BB0_11 Depth=1
	movl	-5216(%rbp), %eax
	addl	$1, %eax
	movl	%eax, -5216(%rbp)
	jmp	.LBB0_11
.LBB0_14:
	xorl	%eax, %eax
	cmpq	$10, -5256(%rbp)
	jge	.LBB0_16
# %bb.15:
	cmpq	$-10, -5256(%rbp)
	setg	%al
.LBB0_16:
	movabsq	$.L.str.2, %rsi
	movabsq	$.L.str.1, %rcx
	testb	$1, %al
	cmovneq	%rcx, %rsi
	movq	-5256(%rbp), %rdx
	movabsq	$.L.str.5, %rdi
	movb	$0, %al
	callq	printf@PLT
	movl	$0, -5208(%rbp)
.LBB0_17:                               # =>This Inner Loop Header: Depth=1
	cmpl	$12, -5208(%rbp)
	jge	.LBB0_20
# %bb.18:                               #   in Loop: Header=BB0_17 Depth=1
	imull	$37, -5208(%rbp), %eax
	movl	$100, %ecx
	cltd
	idivl	%ecx
	subl	$50, %edx
	shll	$8, %edx
	movslq	%edx, %rax
	movslq	-5208(%rbp), %rcx
	movq	%rax, -512(%rbp,%rcx,8)
# %bb.19:                               #   in Loop: Header=BB0_17 Depth=1
	movl	-5208(%rbp), %eax
	addl	$1, %eax
	movl	%eax, -5208(%rbp)
	jmp	.LBB0_17
.LBB0_20:
	movl	$0, -5204(%rbp)
.LBB0_21:                               # =>This Inner Loop Header: Depth=1
	cmpl	$48, -5204(%rbp)
	jge	.LBB0_24
# %bb.22:                               #   in Loop: Header=BB0_21 Depth=1
	imull	$13, -5204(%rbp), %eax
	movl	$200, %ecx
	cltd
	idivl	%ecx
	subl	$100, %edx
	shll	$7, %edx
	movslq	%edx, %rax
	movslq	-5204(%rbp), %rcx
	movq	%rax, -896(%rbp,%rcx,8)
# %bb.23:                               #   in Loop: Header=BB0_21 Depth=1
	movl	-5204(%rbp), %eax
	addl	$1, %eax
	movl	%eax, -5204(%rbp)
	jmp	.LBB0_21
.LBB0_24:
	movl	$0, -5200(%rbp)
.LBB0_25:                               # =>This Inner Loop Header: Depth=1
	cmpl	$12, -5200(%rbp)
	jge	.LBB0_28
# %bb.26:                               #   in Loop: Header=BB0_25 Depth=1
	imull	$7, -5200(%rbp), %eax
	movl	$50, %ecx
	cltd
	idivl	%ecx
	subl	$25, %edx
	shll	$6, %edx
	movslq	%edx, %rax
	movslq	-5200(%rbp), %rcx
	movq	%rax, -992(%rbp,%rcx,8)
# %bb.27:                               #   in Loop: Header=BB0_25 Depth=1
	movl	-5200(%rbp), %eax
	addl	$1, %eax
	movl	%eax, -5200(%rbp)
	jmp	.LBB0_25
.LBB0_28:
	movl	$0, -5196(%rbp)
.LBB0_29:                               # =>This Inner Loop Header: Depth=1
	cmpl	$16, -5196(%rbp)
	jge	.LBB0_32
# %bb.30:                               #   in Loop: Header=BB0_29 Depth=1
	imull	$11, -5196(%rbp), %eax
	movl	$200, %ecx
	cltd
	idivl	%ecx
	subl	$100, %edx
	shll	$7, %edx
	movslq	%edx, %rax
	movslq	-5196(%rbp), %rcx
	movq	%rax, -1120(%rbp,%rcx,8)
# %bb.31:                               #   in Loop: Header=BB0_29 Depth=1
	movl	-5196(%rbp), %eax
	addl	$1, %eax
	movl	%eax, -5196(%rbp)
	jmp	.LBB0_29
.LBB0_32:
	movl	$0, -5192(%rbp)
.LBB0_33:                               # =>This Inner Loop Header: Depth=1
	cmpl	$4, -5192(%rbp)
	jge	.LBB0_36
# %bb.34:                               #   in Loop: Header=BB0_33 Depth=1
	imull	$10, -5192(%rbp), %eax
	cltq
	movslq	-5192(%rbp), %rcx
	movq	%rax, -1152(%rbp,%rcx,8)
	movslq	-5192(%rbp), %rax
	movq	$65536, -1184(%rbp,%rax,8)      # imm = 0x10000
	movslq	-5192(%rbp), %rax
	movq	$0, -1216(%rbp,%rax,8)
# %bb.35:                               #   in Loop: Header=BB0_33 Depth=1
	movl	-5192(%rbp), %eax
	addl	$1, %eax
	movl	%eax, -5192(%rbp)
	jmp	.LBB0_33
.LBB0_36:
	leaq	-512(%rbp), %rax
	movq	%rax, -3472(%rbp)
	movq	$12, -3464(%rbp)
	movq	$8, -3456(%rbp)
	movq	$8, -3448(%rbp)
	leaq	-896(%rbp), %rax
	movq	%rax, -3504(%rbp)
	movq	$48, -3496(%rbp)
	movq	$8, -3488(%rbp)
	movq	$8, -3480(%rbp)
	leaq	-992(%rbp), %rax
	movq	%rax, -3536(%rbp)
	movq	$12, -3528(%rbp)
	movq	$8, -3520(%rbp)
	movq	$8, -3512(%rbp)
	leaq	-1120(%rbp), %rax
	movq	%rax, -3568(%rbp)
	movq	$16, -3560(%rbp)
	movq	$8, -3552(%rbp)
	movq	$8, -3544(%rbp)
	leaq	-1152(%rbp), %rax
	movq	%rax, -3600(%rbp)
	movq	$4, -3592(%rbp)
	movq	$8, -3584(%rbp)
	movq	$8, -3576(%rbp)
	leaq	-1184(%rbp), %rax
	movq	%rax, -3632(%rbp)
	movq	$4, -3624(%rbp)
	movq	$8, -3616(%rbp)
	movq	$8, -3608(%rbp)
	leaq	-1216(%rbp), %rax
	movq	%rax, -3664(%rbp)
	movq	$4, -3656(%rbp)
	movq	$8, -3648(%rbp)
	movq	$8, -3640(%rbp)
	leaq	-1312(%rbp), %rax
	movq	%rax, -3696(%rbp)
	movq	$12, -3688(%rbp)
	movq	$8, -3680(%rbp)
	movq	$8, -3672(%rbp)
	leaq	-3472(%rbp), %rdi
	leaq	-3504(%rbp), %rsi
	leaq	-3536(%rbp), %rdx
	leaq	-3568(%rbp), %rcx
	leaq	-3600(%rbp), %r8
	leaq	-3632(%rbp), %r9
	leaq	-3664(%rbp), %rax
	leaq	-3696(%rbp), %r10
	movq	%rax, (%rsp)
	movq	%r10, 8(%rsp)
	callq	fused_attention
	leaq	-512(%rbp), %rdi
	leaq	-896(%rbp), %rsi
	leaq	-992(%rbp), %rdx
	leaq	-1120(%rbp), %rcx
	leaq	-1152(%rbp), %r8
	leaq	-1184(%rbp), %r9
	leaq	-1216(%rbp), %rax
	leaq	-1408(%rbp), %r10
	movq	%rax, (%rsp)
	movq	%r10, 8(%rsp)
	callq	fused_attention_ref
	movl	$1, -5276(%rbp)
	movl	$0, -5188(%rbp)
.LBB0_37:                               # =>This Inner Loop Header: Depth=1
	cmpl	$12, -5188(%rbp)
	jge	.LBB0_42
# %bb.38:                               #   in Loop: Header=BB0_37 Depth=1
	movslq	-5188(%rbp), %rax
	movq	-1312(%rbp,%rax,8), %rax
	movslq	-5188(%rbp), %rcx
	cmpq	-1408(%rbp,%rcx,8), %rax
	je	.LBB0_40
# %bb.39:                               #   in Loop: Header=BB0_37 Depth=1
	movl	-5188(%rbp), %esi
	movslq	-5188(%rbp), %rax
	movq	-1312(%rbp,%rax,8), %rdx
	movslq	-5188(%rbp), %rax
	movq	-1408(%rbp,%rax,8), %rcx
	movabsq	$.L.str.6, %rdi
	movb	$0, %al
	callq	printf@PLT
	movl	$0, -5276(%rbp)
.LBB0_40:                               #   in Loop: Header=BB0_37 Depth=1
	jmp	.LBB0_41
.LBB0_41:                               #   in Loop: Header=BB0_37 Depth=1
	movl	-5188(%rbp), %eax
	addl	$1, %eax
	movl	%eax, -5188(%rbp)
	jmp	.LBB0_37
.LBB0_42:
	movl	-5276(%rbp), %eax
	movabsq	$.L.str.2, %rsi
	movabsq	$.L.str.1, %rcx
	cmpl	$0, %eax
	cmovneq	%rcx, %rsi
	movabsq	$.L.str.7, %rdi
	movb	$0, %al
	callq	printf@PLT
	leaq	-1456(%rbp), %rdi
	xorl	%esi, %esi
	movl	$40, %edx
	callq	memset@PLT
	movq	$5, -1456(%rbp)
	movq	$1, -1448(%rbp)
	movq	$9, -1440(%rbp)
	movq	$3, -1432(%rbp)
	movq	$7, -1424(%rbp)
	leaq	-1504(%rbp), %rdi
	xorl	%esi, %esi
	movl	$40, %edx
	callq	memset@PLT
	movq	$10, -1504(%rbp)
	movq	$11, -1496(%rbp)
	movq	$12, -1488(%rbp)
	movq	$13, -1480(%rbp)
	movq	$14, -1472(%rbp)
	leaq	-1456(%rbp), %rax
	movq	%rax, -3728(%rbp)
	movq	$5, -3720(%rbp)
	movq	$8, -3712(%rbp)
	movq	$8, -3704(%rbp)
	leaq	-1504(%rbp), %rax
	movq	%rax, -3760(%rbp)
	movq	$5, -3752(%rbp)
	movq	$8, -3744(%rbp)
	movq	$8, -3736(%rbp)
	leaq	-1536(%rbp), %rax
	movq	%rax, -3792(%rbp)
	movq	$3, -3784(%rbp)
	movq	$8, -3776(%rbp)
	movq	$8, -3768(%rbp)
	leaq	-1568(%rbp), %rax
	movq	%rax, -3824(%rbp)
	movq	$3, -3816(%rbp)
	movq	$8, -3808(%rbp)
	movq	$8, -3800(%rbp)
	leaq	-3728(%rbp), %rdi
	leaq	-3760(%rbp), %rcx
	leaq	-3792(%rbp), %r8
	leaq	-3824(%rbp), %r9
	movl	$5, %esi
	movl	$3, %edx
	callq	topk
	xorl	%eax, %eax
	cmpq	$12, -1536(%rbp)
	jne	.LBB0_48
# %bb.43:
	xorl	%eax, %eax
	cmpq	$14, -1528(%rbp)
	jne	.LBB0_48
# %bb.44:
	xorl	%eax, %eax
	cmpq	$10, -1520(%rbp)
	jne	.LBB0_48
# %bb.45:
	xorl	%eax, %eax
	cmpq	$9, -1568(%rbp)
	jne	.LBB0_48
# %bb.46:
	xorl	%eax, %eax
	cmpq	$7, -1560(%rbp)
	jne	.LBB0_48
# %bb.47:
	cmpq	$5, -1552(%rbp)
	sete	%al
.LBB0_48:
	andb	$1, %al
	movzbl	%al, %eax
	movl	%eax, -5372(%rbp)
	movl	-5372(%rbp), %eax
	movabsq	$.L.str.2, %rsi
	movabsq	$.L.str.1, %rcx
	cmpl	$0, %eax
	cmovneq	%rcx, %rsi
	movabsq	$.L.str.8, %rdi
	movb	$0, %al
	callq	printf@PLT
	leaq	-3728(%rbp), %rdi
	callq	argmax
	movabsq	$.L.str.2, %rsi
	movabsq	$.L.str.1, %rcx
	cmpq	$2, %rax
	cmoveq	%rcx, %rsi
	movabsq	$.L.str.9, %rdi
	movb	$0, %al
	callq	printf@PLT
	movq	.L__const.main.ms, %rax
	movq	%rax, -1600(%rbp)
	movq	.L__const.main.ms+8, %rax
	movq	%rax, -1592(%rbp)
	movq	.L__const.main.ms+16, %rax
	movq	%rax, -1584(%rbp)
	movq	.L__const.main.ms+24, %rax
	movq	%rax, -1576(%rbp)
	movq	.L__const.main.mv, %rax
	movq	%rax, -1632(%rbp)
	movq	.L__const.main.mv+8, %rax
	movq	%rax, -1624(%rbp)
	movq	.L__const.main.mv+16, %rax
	movq	%rax, -1616(%rbp)
	movq	.L__const.main.mv+24, %rax
	movq	%rax, -1608(%rbp)
	leaq	-1600(%rbp), %rax
	movq	%rax, -3856(%rbp)
	movq	$4, -3848(%rbp)
	movq	$8, -3840(%rbp)
	movq	$8, -3832(%rbp)
	leaq	-1632(%rbp), %rax
	movq	%rax, -3888(%rbp)
	movq	$4, -3880(%rbp)
	movq	$8, -3872(%rbp)
	movq	$8, -3864(%rbp)
	leaq	-1664(%rbp), %rax
	movq	%rax, -3920(%rbp)
	movq	$4, -3912(%rbp)
	movq	$8, -3904(%rbp)
	movq	$8, -3896(%rbp)
	leaq	-3856(%rbp), %rdi
	leaq	-3888(%rbp), %rsi
	leaq	-3920(%rbp), %rdx
	callq	mask_scores
	movq	%rax, -5456(%rbp)
	xorl	%eax, %eax
	cmpq	$3, -5456(%rbp)
	jne	.LBB0_53
# %bb.49:
	xorl	%eax, %eax
	cmpq	$5, -1664(%rbp)
	jne	.LBB0_53
# %bb.50:
	xorl	%eax, %eax
	cmpq	$-999999999, -1656(%rbp)        # imm = 0xC4653601
	jne	.LBB0_53
# %bb.51:
	xorl	%eax, %eax
	cmpq	$7, -1648(%rbp)
	jne	.LBB0_53
# %bb.52:
	cmpq	$8, -1640(%rbp)
	sete	%al
.LBB0_53:
	andb	$1, %al
	movzbl	%al, %eax
	movl	%eax, -5368(%rbp)
	movl	-5368(%rbp), %eax
	movabsq	$.L.str.2, %rsi
	movabsq	$.L.str.1, %rcx
	cmpl	$0, %eax
	cmovneq	%rcx, %rsi
	movq	-5456(%rbp), %rdx
	movabsq	$.L.str.10, %rdi
	movb	$0, %al
	callq	printf@PLT
	movq	.L__const.main.ik, %rax
	movq	%rax, -1696(%rbp)
	movq	.L__const.main.ik+8, %rax
	movq	%rax, -1688(%rbp)
	movq	.L__const.main.ik+16, %rax
	movq	%rax, -1680(%rbp)
	movq	.L__const.main.ik+24, %rax
	movq	%rax, -1672(%rbp)
	leaq	-1696(%rbp), %rax
	movq	%rax, -3952(%rbp)
	movq	$4, -3944(%rbp)
	movq	$8, -3936(%rbp)
	movq	$8, -3928(%rbp)
	leaq	-1760(%rbp), %rax
	movq	%rax, -3984(%rbp)
	movq	$8, -3976(%rbp)
	movq	$8, -3968(%rbp)
	movq	$8, -3960(%rbp)
	leaq	-1792(%rbp), %rax
	movq	%rax, -4016(%rbp)
	movq	$4, -4008(%rbp)
	movq	$8, -4000(%rbp)
	movq	$8, -3992(%rbp)
	leaq	-1824(%rbp), %rax
	movq	%rax, -4048(%rbp)
	movq	$4, -4040(%rbp)
	movq	$8, -4032(%rbp)
	movq	$8, -4024(%rbp)
	leaq	-3952(%rbp), %rdi
	leaq	-3984(%rbp), %rsi
	leaq	-4016(%rbp), %rdx
	callq	build_index
	leaq	-3952(%rbp), %rdi
	leaq	-3984(%rbp), %rdx
	leaq	-4016(%rbp), %rcx
	leaq	-4048(%rbp), %r9
	movl	$4, %esi
	movl	$3, %r8d
	callq	index_lookup
	movq	%rax, -5448(%rbp)
	leaq	-3952(%rbp), %rdi
	leaq	-3984(%rbp), %rdx
	leaq	-4016(%rbp), %rcx
	leaq	-4048(%rbp), %r9
	movl	$4, %esi
	movl	$9, %r8d
	callq	index_lookup
	movq	%rax, -5440(%rbp)
	xorl	%eax, %eax
	cmpq	$2, -5448(%rbp)
	jne	.LBB0_56
# %bb.54:
	xorl	%eax, %eax
	cmpq	$1, -5440(%rbp)
	jne	.LBB0_56
# %bb.55:
	cmpq	$3, -1824(%rbp)
	sete	%al
.LBB0_56:
	andb	$1, %al
	movzbl	%al, %eax
	movl	%eax, -5364(%rbp)
	movl	-5364(%rbp), %eax
	movabsq	$.L.str.2, %rsi
	movabsq	$.L.str.1, %rcx
	cmpl	$0, %eax
	cmovneq	%rcx, %rsi
	movq	-5448(%rbp), %rdx
	movq	-5440(%rbp), %rcx
	movabsq	$.L.str.11, %rdi
	movb	$0, %al
	callq	printf@PLT
	leaq	-1872(%rbp), %rdi
	xorl	%esi, %esi
	movl	$48, %edx
	callq	memset@PLT
	movq	$1, -1872(%rbp)
	movq	$1, -1864(%rbp)
	movq	.L__const.main.pih, %rax
	movq	%rax, -1904(%rbp)
	movq	.L__const.main.pih+8, %rax
	movq	%rax, -1896(%rbp)
	movq	.L__const.main.pih+16, %rax
	movq	%rax, -1888(%rbp)
	movq	.L__const.main.pfm, %rax
	movq	%rax, -1936(%rbp)
	movq	.L__const.main.pfm+8, %rax
	movq	%rax, -1928(%rbp)
	movq	.L__const.main.pfm+16, %rax
	movq	%rax, -1920(%rbp)
	leaq	-1872(%rbp), %rax
	movq	%rax, -4080(%rbp)
	movq	$6, -4072(%rbp)
	movq	$8, -4064(%rbp)
	movq	$8, -4056(%rbp)
	leaq	-1904(%rbp), %rax
	movq	%rax, -4112(%rbp)
	movq	$3, -4104(%rbp)
	movq	$8, -4096(%rbp)
	movq	$8, -4088(%rbp)
	leaq	-1936(%rbp), %rax
	movq	%rax, -4144(%rbp)
	movq	$3, -4136(%rbp)
	movq	$8, -4128(%rbp)
	movq	$8, -4120(%rbp)
	leaq	-1984(%rbp), %rax
	movq	%rax, -4176(%rbp)
	movq	$6, -4168(%rbp)
	movq	$8, -4160(%rbp)
	movq	$8, -4152(%rbp)
	leaq	-4080(%rbp), %rdi
	leaq	-4112(%rbp), %rsi
	leaq	-4144(%rbp), %rdx
	leaq	-4176(%rbp), %rcx
	callq	frontier_closure
	movq	%rax, -5432(%rbp)
	xorl	%eax, %eax
	cmpq	$2, -5432(%rbp)
	jne	.LBB0_59
# %bb.57:
	xorl	%eax, %eax
	cmpq	$2, -1984(%rbp)
	jne	.LBB0_59
# %bb.58:
	cmpq	$3, -1976(%rbp)
	sete	%al
.LBB0_59:
	andb	$1, %al
	movzbl	%al, %eax
	movl	%eax, -5360(%rbp)
	movl	-5360(%rbp), %eax
	movabsq	$.L.str.2, %rsi
	movabsq	$.L.str.1, %rcx
	cmpl	$0, %eax
	cmovneq	%rcx, %rsi
	movq	-5432(%rbp), %rdx
	movabsq	$.L.str.12, %rdi
	movb	$0, %al
	callq	printf@PLT
	leaq	-2032(%rbp), %rdi
	xorl	%esi, %esi
	movl	$48, %edx
	callq	memset@PLT
	movq	$1, -2032(%rbp)
	leaq	-2032(%rbp), %rax
	movq	%rax, -4208(%rbp)
	movq	$6, -4200(%rbp)
	movq	$8, -4192(%rbp)
	movq	$8, -4184(%rbp)
	leaq	-2080(%rbp), %rax
	movq	%rax, -4240(%rbp)
	movq	$6, -4232(%rbp)
	movq	$8, -4224(%rbp)
	movq	$8, -4216(%rbp)
	leaq	-4208(%rbp), %rdi
	leaq	-4112(%rbp), %rsi
	leaq	-4144(%rbp), %rdx
	leaq	-4240(%rbp), %rcx
	callq	frontier_missing
	movq	%rax, -5424(%rbp)
	xorl	%eax, %eax
	cmpq	$6, -5424(%rbp)
	jne	.LBB0_62
# %bb.60:
	xorl	%eax, %eax
	cmpq	$1, -2080(%rbp)
	jne	.LBB0_62
# %bb.61:
	cmpq	$2, -2072(%rbp)
	sete	%al
.LBB0_62:
	movabsq	$.L.str.2, %rsi
	movabsq	$.L.str.1, %rcx
	testb	$1, %al
	cmovneq	%rcx, %rsi
	movq	-5424(%rbp), %rdx
	movabsq	$.L.str.13, %rdi
	movb	$0, %al
	callq	printf@PLT
	movq	.L__const.main.ca, %rax
	movq	%rax, -2112(%rbp)
	movq	.L__const.main.ca+8, %rax
	movq	%rax, -2104(%rbp)
	movq	.L__const.main.ca+16, %rax
	movq	%rax, -2096(%rbp)
	movq	.L__const.main.ca+24, %rax
	movq	%rax, -2088(%rbp)
	leaq	-2112(%rbp), %rax
	movq	%rax, -4272(%rbp)
	movq	$4, -4264(%rbp)
	movq	$8, -4256(%rbp)
	movq	$8, -4248(%rbp)
	leaq	-2144(%rbp), %rax
	movq	%rax, -4304(%rbp)
	movq	$4, -4296(%rbp)
	movq	$8, -4288(%rbp)
	movq	$8, -4280(%rbp)
	leaq	-4272(%rbp), %rdi
	leaq	-4304(%rbp), %rsi
	callq	bfs
	movq	%rax, -5416(%rbp)
	xorl	%eax, %eax
	cmpq	$3, -5416(%rbp)
	jne	.LBB0_66
# %bb.63:
	xorl	%eax, %eax
	cmpq	$0, -2144(%rbp)
	jne	.LBB0_66
# %bb.64:
	xorl	%eax, %eax
	cmpq	$1, -2136(%rbp)
	jne	.LBB0_66
# %bb.65:
	cmpq	$2, -2128(%rbp)
	sete	%al
.LBB0_66:
	andb	$1, %al
	movzbl	%al, %eax
	movl	%eax, -5356(%rbp)
	movl	-5356(%rbp), %eax
	movabsq	$.L.str.2, %rsi
	movabsq	$.L.str.1, %rcx
	cmpl	$0, %eax
	cmovneq	%rcx, %rsi
	movq	-5416(%rbp), %rdx
	movabsq	$.L.str.14, %rdi
	movb	$0, %al
	callq	printf@PLT
	movq	.L__const.main.ptu, %rax
	movq	%rax, -2176(%rbp)
	movq	.L__const.main.ptu+8, %rax
	movq	%rax, -2168(%rbp)
	movq	.L__const.main.ptu+16, %rax
	movq	%rax, -2160(%rbp)
	movq	.L__const.main.ptv, %rax
	movq	%rax, -2208(%rbp)
	movq	.L__const.main.ptv+8, %rax
	movq	%rax, -2200(%rbp)
	movq	.L__const.main.ptv+16, %rax
	movq	%rax, -2192(%rbp)
	leaq	-2176(%rbp), %rax
	movq	%rax, -4336(%rbp)
	movq	$3, -4328(%rbp)
	movq	$8, -4320(%rbp)
	movq	$8, -4312(%rbp)
	leaq	-2208(%rbp), %rax
	movq	%rax, -4368(%rbp)
	movq	$3, -4360(%rbp)
	movq	$8, -4352(%rbp)
	movq	$8, -4344(%rbp)
	leaq	-2240(%rbp), %rax
	movq	%rax, -4400(%rbp)
	movq	$4, -4392(%rbp)
	movq	$8, -4384(%rbp)
	movq	$8, -4376(%rbp)
	leaq	-4336(%rbp), %rdi
	leaq	-4368(%rbp), %rsi
	leaq	-4400(%rbp), %rdx
	callq	topo
	movq	%rax, -5408(%rbp)
	xorl	%eax, %eax
	cmpq	$4, -5408(%rbp)
	jne	.LBB0_68
# %bb.67:
	cmpq	$0, -2240(%rbp)
	sete	%al
.LBB0_68:
	andb	$1, %al
	movzbl	%al, %eax
	movl	%eax, -5352(%rbp)
	movl	-5352(%rbp), %eax
	movabsq	$.L.str.2, %rsi
	movabsq	$.L.str.1, %rcx
	cmpl	$0, %eax
	cmovneq	%rcx, %rsi
	movq	-5408(%rbp), %rdx
	movabsq	$.L.str.15, %rdi
	movb	$0, %al
	callq	printf@PLT
	movq	.L__const.main.pp, %rax
	movq	%rax, -2272(%rbp)
	movq	.L__const.main.pp+8, %rax
	movq	%rax, -2264(%rbp)
	movq	.L__const.main.pp+16, %rax
	movq	%rax, -2256(%rbp)
	movq	.L__const.main.pp+24, %rax
	movq	%rax, -2248(%rbp)
	leaq	-2272(%rbp), %rdi
	xorl	%esi, %esi
	movl	$1, %edx
	callq	uf_union
	movq	%rax, -5496(%rbp)
	leaq	-2272(%rbp), %rdi
	movl	$2, %esi
	movl	$3, %edx
	callq	uf_union
	movq	%rax, -5488(%rbp)
	leaq	-2272(%rbp), %rdi
	movl	$1, %esi
	movl	$2, %edx
	callq	uf_union
	movq	%rax, -5480(%rbp)
	xorl	%eax, %eax
	cmpq	$1, -5496(%rbp)
	jne	.LBB0_72
# %bb.69:
	xorl	%eax, %eax
	cmpq	$1, -5488(%rbp)
	jne	.LBB0_72
# %bb.70:
	xorl	%eax, %eax
	cmpq	$1, -5480(%rbp)
	jne	.LBB0_72
# %bb.71:
	leaq	-2272(%rbp), %rdi
	xorl	%esi, %esi
	callq	uf_find
	movq	%rax, %rbx
	leaq	-2272(%rbp), %rdi
	movl	$3, %esi
	callq	uf_find
	cmpq	%rax, %rbx
	sete	%al
.LBB0_72:
	andb	$1, %al
	movzbl	%al, %eax
	movl	%eax, -5348(%rbp)
	movl	-5348(%rbp), %eax
	movabsq	$.L.str.2, %rsi
	movabsq	$.L.str.1, %rcx
	cmpl	$0, %eax
	cmovneq	%rcx, %rsi
	movabsq	$.L.str.16, %rdi
	movb	$0, %al
	callq	printf@PLT
	movq	.L__const.main.ca, %rax
	movq	%rax, -2304(%rbp)
	movq	.L__const.main.ca+8, %rax
	movq	%rax, -2296(%rbp)
	movq	.L__const.main.ca+16, %rax
	movq	%rax, -2288(%rbp)
	movq	.L__const.main.ca+24, %rax
	movq	%rax, -2280(%rbp)
	leaq	-2304(%rbp), %rax
	movq	%rax, -4432(%rbp)
	movq	$4, -4424(%rbp)
	movq	$8, -4416(%rbp)
	movq	$8, -4408(%rbp)
	leaq	-2336(%rbp), %rax
	movq	%rax, -4464(%rbp)
	movq	$4, -4456(%rbp)
	movq	$8, -4448(%rbp)
	movq	$8, -4440(%rbp)
	leaq	-4432(%rbp), %rdi
	leaq	-4464(%rbp), %rsi
	callq	bitset_closure
	xorl	%eax, %eax
	cmpq	$6, -2336(%rbp)
	jne	.LBB0_74
# %bb.73:
	cmpq	$4, -2328(%rbp)
	sete	%al
.LBB0_74:
	andb	$1, %al
	movzbl	%al, %eax
	movl	%eax, -5344(%rbp)
	movl	-5344(%rbp), %eax
	movabsq	$.L.str.2, %rsi
	movabsq	$.L.str.1, %rcx
	cmpl	$0, %eax
	cmovneq	%rcx, %rsi
	movabsq	$.L.str.17, %rdi
	movb	$0, %al
	callq	printf@PLT
	leaq	-2384(%rbp), %rdi
	xorl	%esi, %esi
	movl	$40, %edx
	callq	memset@PLT
	movq	$3, -2384(%rbp)
	movq	$7, -2376(%rbp)
	movq	$3, -2368(%rbp)
	movq	$9, -2360(%rbp)
	movq	$-1, -2352(%rbp)
	leaq	-2384(%rbp), %rax
	movq	%rax, -4496(%rbp)
	movq	$5, -4488(%rbp)
	movq	$8, -4480(%rbp)
	movq	$8, -4472(%rbp)
	leaq	-2448(%rbp), %rax
	movq	%rax, -4528(%rbp)
	movq	$8, -4520(%rbp)
	movq	$8, -4512(%rbp)
	movq	$8, -4504(%rbp)
	leaq	-2496(%rbp), %rax
	movq	%rax, -4560(%rbp)
	movq	$5, -4552(%rbp)
	movq	$8, -4544(%rbp)
	movq	$8, -4536(%rbp)
	leaq	-2544(%rbp), %rax
	movq	%rax, -4592(%rbp)
	movq	$5, -4584(%rbp)
	movq	$8, -4576(%rbp)
	movq	$8, -4568(%rbp)
	leaq	-4496(%rbp), %rdi
	leaq	-4528(%rbp), %rsi
	leaq	-4560(%rbp), %rdx
	callq	build_index
	leaq	-4496(%rbp), %rdi
	leaq	-4528(%rbp), %rsi
	leaq	-4560(%rbp), %rdx
	callq	index_add
	leaq	-4496(%rbp), %rdi
	leaq	-4528(%rbp), %rdx
	leaq	-4560(%rbp), %rcx
	leaq	-4592(%rbp), %r9
	movl	$5, %esi
	movl	$3, %r8d
	callq	index_lookup
	movq	%rax, -5400(%rbp)
	leaq	-4496(%rbp), %rdi
	callq	index_remove
	movq	%rax, -5392(%rbp)
	leaq	-4496(%rbp), %rdi
	leaq	-4528(%rbp), %rdx
	leaq	-4560(%rbp), %rcx
	leaq	-4592(%rbp), %r9
	movl	$5, %esi
	movl	$3, %r8d
	callq	index_lookup
	movq	%rax, -5384(%rbp)
	xorl	%eax, %eax
	cmpq	$3, -5400(%rbp)
	jne	.LBB0_77
# %bb.75:
	xorl	%eax, %eax
	cmpq	$3, -5392(%rbp)
	jne	.LBB0_77
# %bb.76:
	cmpq	$2, -5384(%rbp)
	sete	%al
.LBB0_77:
	andb	$1, %al
	movzbl	%al, %eax
	movl	%eax, -5340(%rbp)
	movl	-5340(%rbp), %eax
	movabsq	$.L.str.2, %rsi
	movabsq	$.L.str.1, %rcx
	cmpl	$0, %eax
	cmovneq	%rcx, %rsi
	movq	-5400(%rbp), %rdx
	movq	-5392(%rbp), %rcx
	movq	-5384(%rbp), %r8
	movabsq	$.L.str.18, %rdi
	movb	$0, %al
	callq	printf@PLT
	movl	$65536, %edi                    # imm = 0x10000
	callq	bce_q16
	movq	%rax, -5312(%rbp)
	xorl	%edi, %edi
	callq	bce_q16
	movq	%rax, -5304(%rbp)
	xorl	%eax, %eax
	cmpq	$45000, -5312(%rbp)             # imm = 0xAFC8
	jle	.LBB0_81
# %bb.78:
	xorl	%eax, %eax
	cmpq	$46000, -5312(%rbp)             # imm = 0xB3B0
	jge	.LBB0_81
# %bb.79:
	xorl	%eax, %eax
	cmpq	$45000, -5304(%rbp)             # imm = 0xAFC8
	jle	.LBB0_81
# %bb.80:
	cmpq	$46000, -5304(%rbp)             # imm = 0xB3B0
	setl	%al
.LBB0_81:
	andb	$1, %al
	movzbl	%al, %eax
	movl	%eax, -5336(%rbp)
	movl	-5336(%rbp), %eax
	movabsq	$.L.str.2, %rsi
	movabsq	$.L.str.1, %rcx
	cmpl	$0, %eax
	cmovneq	%rcx, %rsi
	movq	-5312(%rbp), %rdx
	movq	-5304(%rbp), %rcx
	movabsq	$.L.str.19, %rdi
	movb	$0, %al
	callq	printf@PLT
	movq	.L__const.main.lw, %rax
	movq	%rax, -2576(%rbp)
	movq	.L__const.main.lw+8, %rax
	movq	%rax, -2568(%rbp)
	movq	.L__const.main.lw+16, %rax
	movq	%rax, -2560(%rbp)
	movq	.L__const.main.lw+24, %rax
	movq	%rax, -2552(%rbp)
	movq	.L__const.main.bdy, %rax
	movq	%rax, -2592(%rbp)
	movq	.L__const.main.bdy+8, %rax
	movq	%rax, -2584(%rbp)
	leaq	-2576(%rbp), %rax
	movq	%rax, -4624(%rbp)
	movq	$4, -4616(%rbp)
	movq	$8, -4608(%rbp)
	movq	$8, -4600(%rbp)
	leaq	-2592(%rbp), %rax
	movq	%rax, -4656(%rbp)
	movq	$2, -4648(%rbp)
	movq	$8, -4640(%rbp)
	movq	$8, -4632(%rbp)
	leaq	-2608(%rbp), %rax
	movq	%rax, -4688(%rbp)
	movq	$2, -4680(%rbp)
	movq	$8, -4672(%rbp)
	movq	$8, -4664(%rbp)
	leaq	-4624(%rbp), %rdi
	leaq	-4656(%rbp), %rsi
	leaq	-4688(%rbp), %rdx
	callq	backward_matvec
	xorl	%eax, %eax
	cmpq	$131072, -2608(%rbp)            # imm = 0x20000
	jne	.LBB0_83
# %bb.82:
	cmpq	$196608, -2600(%rbp)            # imm = 0x30000
	sete	%al
.LBB0_83:
	andb	$1, %al
	movzbl	%al, %eax
	movl	%eax, -5332(%rbp)
	movl	-5332(%rbp), %eax
	movabsq	$.L.str.2, %rsi
	movabsq	$.L.str.1, %rcx
	cmpl	$0, %eax
	cmovneq	%rcx, %rsi
	movabsq	$.L.str.20, %rdi
	movb	$0, %al
	callq	printf@PLT
	movq	$0, -4696(%rbp)
	movq	$0, -4704(%rbp)
	movq	$6553600, -5248(%rbp)           # imm = 0x640000
	movq	$1, -5288(%rbp)
.LBB0_84:                               # =>This Inner Loop Header: Depth=1
	cmpq	$3, -5288(%rbp)
	jg	.LBB0_87
# %bb.85:                               #   in Loop: Header=BB0_84 Depth=1
	movq	-5248(%rbp), %rdi
	movq	-5288(%rbp), %rcx
	leaq	-4696(%rbp), %rsi
	leaq	-4704(%rbp), %rdx
	callq	adam_step
	movq	%rax, -5248(%rbp)
# %bb.86:                               #   in Loop: Header=BB0_84 Depth=1
	movq	-5288(%rbp), %rax
	addq	$1, %rax
	movq	%rax, -5288(%rbp)
	jmp	.LBB0_84
.LBB0_87:
	xorl	%eax, %eax
	cmpq	$6553600, -5248(%rbp)           # imm = 0x640000
	jge	.LBB0_89
# %bb.88:
	cmpq	$0, -5248(%rbp)
	setg	%al
.LBB0_89:
	andb	$1, %al
	movzbl	%al, %eax
	movl	%eax, -5328(%rbp)
	movl	-5328(%rbp), %eax
	movabsq	$.L.str.2, %rsi
	movabsq	$.L.str.1, %rcx
	cmpl	$0, %eax
	cmovneq	%rcx, %rsi
	movq	-5248(%rbp), %rdx
	movabsq	$.L.str.21, %rdi
	movb	$0, %al
	callq	printf@PLT
	movq	.L__const.main.lw, %rax
	movq	%rax, -2640(%rbp)
	movq	.L__const.main.lw+8, %rax
	movq	%rax, -2632(%rbp)
	movq	.L__const.main.lw+16, %rax
	movq	%rax, -2624(%rbp)
	movq	.L__const.main.lw+24, %rax
	movq	%rax, -2616(%rbp)
	movq	.L__const.main.lb2, %rax
	movq	%rax, -2656(%rbp)
	movq	.L__const.main.lb2+8, %rax
	movq	%rax, -2648(%rbp)
	movq	.L__const.main.lx2, %rax
	movq	%rax, -2672(%rbp)
	movq	.L__const.main.lx2+8, %rax
	movq	%rax, -2664(%rbp)
	leaq	-2640(%rbp), %rax
	movq	%rax, -4736(%rbp)
	movq	$4, -4728(%rbp)
	movq	$8, -4720(%rbp)
	movq	$8, -4712(%rbp)
	leaq	-2656(%rbp), %rax
	movq	%rax, -4768(%rbp)
	movq	$2, -4760(%rbp)
	movq	$8, -4752(%rbp)
	movq	$8, -4744(%rbp)
	leaq	-2672(%rbp), %rax
	movq	%rax, -4800(%rbp)
	movq	$2, -4792(%rbp)
	movq	$8, -4784(%rbp)
	movq	$8, -4776(%rbp)
	leaq	-2688(%rbp), %rax
	movq	%rax, -4832(%rbp)
	movq	$2, -4824(%rbp)
	movq	$8, -4816(%rbp)
	movq	$8, -4808(%rbp)
	leaq	-4736(%rbp), %rdi
	leaq	-4768(%rbp), %rsi
	leaq	-4800(%rbp), %rdx
	leaq	-4832(%rbp), %rcx
	callq	fused_linear_relu
	xorl	%eax, %eax
	cmpq	$65536, -2688(%rbp)             # imm = 0x10000
	jne	.LBB0_91
# %bb.90:
	cmpq	$0, -2680(%rbp)
	sete	%al
.LBB0_91:
	andb	$1, %al
	movzbl	%al, %eax
	movl	%eax, -5324(%rbp)
	movl	-5324(%rbp), %eax
	movabsq	$.L.str.2, %rsi
	movabsq	$.L.str.1, %rcx
	cmpl	$0, %eax
	cmovneq	%rcx, %rsi
	movq	-2688(%rbp), %rdx
	movq	-2680(%rbp), %rcx
	movabsq	$.L.str.22, %rdi
	movb	$0, %al
	callq	printf@PLT
	leaq	-2768(%rbp), %rdi
	xorl	%esi, %esi
	movl	$72, %edx
	callq	memset@PLT
	movq	$65536, -2768(%rbp)             # imm = 0x10000
	movq	$65536, -2736(%rbp)             # imm = 0x10000
	movq	$65536, -2704(%rbp)             # imm = 0x10000
	leaq	-2800(%rbp), %rdi
	xorl	%esi, %esi
	movl	$24, %edx
	callq	memset@PLT
	movq	.L__const.main.lx3, %rax
	movq	%rax, -2832(%rbp)
	movq	.L__const.main.lx3+8, %rax
	movq	%rax, -2824(%rbp)
	movq	.L__const.main.lx3+16, %rax
	movq	%rax, -2816(%rbp)
	movq	.L__const.main.lg3, %rax
	movq	%rax, -2864(%rbp)
	movq	.L__const.main.lg3+8, %rax
	movq	%rax, -2856(%rbp)
	movq	.L__const.main.lg3+16, %rax
	movq	%rax, -2848(%rbp)
	leaq	-2896(%rbp), %rdi
	xorl	%esi, %esi
	movl	$24, %edx
	callq	memset@PLT
	leaq	-2768(%rbp), %rax
	movq	%rax, -4864(%rbp)
	movq	$9, -4856(%rbp)
	movq	$8, -4848(%rbp)
	movq	$8, -4840(%rbp)
	leaq	-2800(%rbp), %rax
	movq	%rax, -4896(%rbp)
	movq	$3, -4888(%rbp)
	movq	$8, -4880(%rbp)
	movq	$8, -4872(%rbp)
	leaq	-2832(%rbp), %rax
	movq	%rax, -4928(%rbp)
	movq	$3, -4920(%rbp)
	movq	$8, -4912(%rbp)
	movq	$8, -4904(%rbp)
	leaq	-2864(%rbp), %rax
	movq	%rax, -4960(%rbp)
	movq	$3, -4952(%rbp)
	movq	$8, -4944(%rbp)
	movq	$8, -4936(%rbp)
	leaq	-2896(%rbp), %rax
	movq	%rax, -4992(%rbp)
	movq	$3, -4984(%rbp)
	movq	$8, -4976(%rbp)
	movq	$8, -4968(%rbp)
	leaq	-2928(%rbp), %rax
	movq	%rax, -5024(%rbp)
	movq	$3, -5016(%rbp)
	movq	$8, -5008(%rbp)
	movq	$8, -5000(%rbp)
	leaq	-4864(%rbp), %rdi
	leaq	-4896(%rbp), %rsi
	leaq	-4928(%rbp), %rdx
	leaq	-4960(%rbp), %rcx
	leaq	-4992(%rbp), %r8
	leaq	-5024(%rbp), %r9
	callq	fused_linear_ln
	movq	$0, -5240(%rbp)
	movl	$0, -5212(%rbp)
.LBB0_92:                               # =>This Inner Loop Header: Depth=1
	cmpl	$3, -5212(%rbp)
	jge	.LBB0_95
# %bb.93:                               #   in Loop: Header=BB0_92 Depth=1
	movslq	-5212(%rbp), %rax
	movq	-2928(%rbp,%rax,8), %rax
	addq	-5240(%rbp), %rax
	movq	%rax, -5240(%rbp)
# %bb.94:                               #   in Loop: Header=BB0_92 Depth=1
	movl	-5212(%rbp), %eax
	addl	$1, %eax
	movl	%eax, -5212(%rbp)
	jmp	.LBB0_92
.LBB0_95:
	xorl	%eax, %eax
	cmpq	$10, -5240(%rbp)
	jge	.LBB0_97
# %bb.96:
	cmpq	$-10, -5240(%rbp)
	setg	%al
.LBB0_97:
	andb	$1, %al
	movzbl	%al, %eax
	movl	%eax, -5320(%rbp)
	movl	-5320(%rbp), %eax
	movabsq	$.L.str.2, %rsi
	movabsq	$.L.str.1, %rcx
	cmpl	$0, %eax
	cmovneq	%rcx, %rsi
	movq	-5240(%rbp), %rdx
	movabsq	$.L.str.23, %rdi
	movb	$0, %al
	callq	printf@PLT
	leaq	-2976(%rbp), %rdi
	xorl	%esi, %esi
	movl	$48, %edx
	callq	memset@PLT
	movq	$1, -2976(%rbp)
	movq	$1, -2968(%rbp)
	movq	.L__const.main.pih, %rax
	movq	%rax, -3008(%rbp)
	movq	.L__const.main.pih+8, %rax
	movq	%rax, -3000(%rbp)
	movq	.L__const.main.pih+16, %rax
	movq	%rax, -2992(%rbp)
	movq	.L__const.main.pibm, %rax
	movq	%rax, -3040(%rbp)
	movq	.L__const.main.pibm+8, %rax
	movq	%rax, -3032(%rbp)
	movq	.L__const.main.pibm+16, %rax
	movq	%rax, -3024(%rbp)
	movq	.L__const.main.pisc, %rax
	movq	%rax, -3072(%rbp)
	movq	.L__const.main.pisc+8, %rax
	movq	%rax, -3064(%rbp)
	movq	.L__const.main.pisc+16, %rax
	movq	%rax, -3056(%rbp)
	leaq	-2976(%rbp), %rax
	movq	%rax, -5056(%rbp)
	movq	$6, -5048(%rbp)
	movq	$8, -5040(%rbp)
	movq	$8, -5032(%rbp)
	leaq	-3008(%rbp), %rax
	movq	%rax, -5088(%rbp)
	movq	$3, -5080(%rbp)
	movq	$8, -5072(%rbp)
	movq	$8, -5064(%rbp)
	leaq	-3040(%rbp), %rax
	movq	%rax, -5120(%rbp)
	movq	$3, -5112(%rbp)
	movq	$8, -5104(%rbp)
	movq	$8, -5096(%rbp)
	leaq	-3072(%rbp), %rax
	movq	%rax, -5152(%rbp)
	movq	$3, -5144(%rbp)
	movq	$8, -5136(%rbp)
	movq	$8, -5128(%rbp)
	leaq	-3120(%rbp), %rax
	movq	%rax, -5184(%rbp)
	movq	$6, -5176(%rbp)
	movq	$8, -5168(%rbp)
	movq	$8, -5160(%rbp)
	leaq	-5056(%rbp), %rdi
	leaq	-5088(%rbp), %rsi
	leaq	-5120(%rbp), %rdx
	leaq	-5152(%rbp), %rcx
	leaq	-5184(%rbp), %r8
	callq	integrated_derive
	movq	%rax, -5296(%rbp)
	movl	$0, -5272(%rbp)
	movl	$0, -5268(%rbp)
	movl	$0, -5224(%rbp)
	movq	$0, -5232(%rbp)
.LBB0_98:                               # =>This Inner Loop Header: Depth=1
	movq	-5232(%rbp), %rax
	cmpq	-5296(%rbp), %rax
	jge	.LBB0_107
# %bb.99:                               #   in Loop: Header=BB0_98 Depth=1
	movq	-5232(%rbp), %rax
	cmpq	$2, -3120(%rbp,%rax,8)
	jne	.LBB0_101
# %bb.100:                              #   in Loop: Header=BB0_98 Depth=1
	movl	$1, -5272(%rbp)
.LBB0_101:                              #   in Loop: Header=BB0_98 Depth=1
	movq	-5232(%rbp), %rax
	cmpq	$5, -3120(%rbp,%rax,8)
	jne	.LBB0_103
# %bb.102:                              #   in Loop: Header=BB0_98 Depth=1
	movl	$1, -5268(%rbp)
.LBB0_103:                              #   in Loop: Header=BB0_98 Depth=1
	movq	-5232(%rbp), %rax
	cmpq	$3, -3120(%rbp,%rax,8)
	jne	.LBB0_105
# %bb.104:                              #   in Loop: Header=BB0_98 Depth=1
	movl	$1, -5224(%rbp)
.LBB0_105:                              #   in Loop: Header=BB0_98 Depth=1
	jmp	.LBB0_106
.LBB0_106:                              #   in Loop: Header=BB0_98 Depth=1
	movq	-5232(%rbp), %rax
	addq	$1, %rax
	movq	%rax, -5232(%rbp)
	jmp	.LBB0_98
.LBB0_107:
	xorl	%eax, %eax
	cmpq	$2, -5296(%rbp)
	jne	.LBB0_111
# %bb.108:
	xorl	%eax, %eax
	cmpl	$0, -5272(%rbp)
	je	.LBB0_111
# %bb.109:
	xorl	%eax, %eax
	cmpl	$0, -5268(%rbp)
	je	.LBB0_111
# %bb.110:
	cmpl	$0, -5224(%rbp)
	setne	%al
	xorb	$-1, %al
.LBB0_111:
	movzbl	%al, %eax
	andl	$1, %eax
	movl	%eax, -5316(%rbp)
	movl	-5316(%rbp), %eax
	testl	%eax, %eax
	movl	$.L.str.1, %ebx
	movl	$.L.str.2, %r14d
	movl	$.L.str.2, %esi
	cmovneq	%rbx, %rsi
	movq	-5296(%rbp), %rdx
	movl	$.L.str.24, %edi
	xorl	%eax, %eax
	callq	printf@PLT
	movl	-5224(%rbp), %edx
	testl	%edx, %edx
	cmovneq	%r14, %rbx
	movl	$.L.str.25, %edi
	movq	%rbx, %rsi
	xorl	%eax, %eax
	callq	printf@PLT
	movl	$.L.str.26, %edi
	xorl	%eax, %eax
	callq	printf@PLT
	movq	%fs:40, %rax
	movq	-24(%rbp), %rcx
	cmpq	%rcx, %rax
	jne	.LBB0_113
# %bb.112:                              # %SP_return
	xorl	%eax, %eax
	addq	$5504, %rsp                     # imm = 0x1580
	popq	%rbx
	popq	%r14
	popq	%rbp
	.cfi_def_cfa %rsp, 8
	retq
.LBB0_113:                              # %CallStackCheckFailBlk
	.cfi_def_cfa %rbp, 16
	callq	__stack_chk_fail@PLT
.Lfunc_end0:
	.size	main, .Lfunc_end0-main
	.cfi_endproc
                                        # -- End function
	.prefalign	4, .Lfunc_end1, nop     # -- Begin function matvec
	.type	matvec,@function
matvec:                                 # @matvec
	.cfi_startproc
# %bb.0:
	pushq	%rbp
	.cfi_def_cfa_offset 16
	.cfi_offset %rbp, -16
	movq	%rsp, %rbp
	.cfi_def_cfa_register %rbp
	pushq	%rbx
	subq	$72, %rsp
	.cfi_offset %rbx, -24
	movq	%rdi, -80(%rbp)
	movq	%rsi, -72(%rbp)
	movq	%rdx, -40(%rbp)
	movq	%rcx, -64(%rbp)
	movq	%r8, -56(%rbp)
	movq	%r9, -48(%rbp)
	movq	$0, -16(%rbp)
.LBB1_1:                                # =>This Loop Header: Depth=1
                                        #     Child Loop BB1_3 Depth 2
	movq	-16(%rbp), %rax
	cmpq	-72(%rbp), %rax
	jge	.LBB1_8
# %bb.2:                                #   in Loop: Header=BB1_1 Depth=1
	movq	$0, -32(%rbp)
	movq	$0, -24(%rbp)
.LBB1_3:                                #   Parent Loop BB1_1 Depth=1
                                        # =>  This Inner Loop Header: Depth=2
	movq	-24(%rbp), %rax
	cmpq	-40(%rbp), %rax
	jge	.LBB1_6
# %bb.4:                                #   in Loop: Header=BB1_3 Depth=2
	movq	-80(%rbp), %rdi
	movq	-16(%rbp), %rsi
	imulq	-40(%rbp), %rsi
	addq	-24(%rbp), %rsi
	callq	getv
	movq	%rax, %rbx
	movq	-64(%rbp), %rdi
	movq	-24(%rbp), %rsi
	callq	getv
	movq	%rbx, %rdi
	movq	%rax, %rsi
	callq	qmul
	addq	-32(%rbp), %rax
	movq	%rax, -32(%rbp)
# %bb.5:                                #   in Loop: Header=BB1_3 Depth=2
	movq	-24(%rbp), %rax
	addq	$1, %rax
	movq	%rax, -24(%rbp)
	jmp	.LBB1_3
.LBB1_6:                                #   in Loop: Header=BB1_1 Depth=1
	movq	-32(%rbp), %rbx
	movq	-56(%rbp), %rdi
	movq	-16(%rbp), %rsi
	callq	getv
	addq	%rax, %rbx
	movq	-48(%rbp), %rax
	movq	-16(%rbp), %rcx
	movq	%rbx, (%rax,%rcx,8)
# %bb.7:                                #   in Loop: Header=BB1_1 Depth=1
	movq	-16(%rbp), %rax
	addq	$1, %rax
	movq	%rax, -16(%rbp)
	jmp	.LBB1_1
.LBB1_8:
	addq	$72, %rsp
	popq	%rbx
	popq	%rbp
	.cfi_def_cfa %rsp, 8
	retq
.Lfunc_end1:
	.size	matvec, .Lfunc_end1-matvec
	.cfi_endproc
                                        # -- End function
	.prefalign	4, .Lfunc_end2, nop     # -- Begin function qmul
	.type	qmul,@function
qmul:                                   # @qmul
	.cfi_startproc
# %bb.0:
	pushq	%rbp
	.cfi_def_cfa_offset 16
	.cfi_offset %rbp, -16
	movq	%rsp, %rbp
	.cfi_def_cfa_register %rbp
	movq	%rdi, -16(%rbp)
	movq	%rsi, -8(%rbp)
	movq	-16(%rbp), %rax
	imulq	-8(%rbp), %rax
	sarq	$16, %rax
	popq	%rbp
	.cfi_def_cfa %rsp, 8
	retq
.Lfunc_end2:
	.size	qmul, .Lfunc_end2-qmul
	.cfi_endproc
                                        # -- End function
	.prefalign	4, .Lfunc_end3, nop     # -- Begin function batched
	.type	batched,@function
batched:                                # @batched
	.cfi_startproc
# %bb.0:
	pushq	%rbp
	.cfi_def_cfa_offset 16
	.cfi_offset %rbp, -16
	movq	%rsp, %rbp
	.cfi_def_cfa_register %rbp
	subq	$112, %rsp
	movq	%fs:40, %rax
	movq	%rax, -8(%rbp)
	movq	%rdi, -104(%rbp)
	movq	$2, -72(%rbp)
	movq	$3, -64(%rbp)
	movq	%rsi, -56(%rbp)
	movq	%rdx, -96(%rbp)
	movq	$2, -88(%rbp)
	movq	%rcx, -80(%rbp)
	movq	$0, -48(%rbp)
.LBB3_1:                                # =>This Inner Loop Header: Depth=1
	movq	-48(%rbp), %rax
	cmpq	-88(%rbp), %rax
	jge	.LBB3_4
# %bb.2:                                #   in Loop: Header=BB3_1 Depth=1
	movq	-56(%rbp), %rax
	movq	(%rax), %rcx
	movq	%rcx, -40(%rbp)
	movq	8(%rax), %rcx
	movq	%rcx, -32(%rbp)
	movq	16(%rax), %rcx
	movq	%rcx, -24(%rbp)
	movq	24(%rax), %rax
	movq	%rax, -16(%rbp)
	movq	-56(%rbp), %rax
	movq	(%rax), %rax
	movq	-48(%rbp), %rcx
	imulq	-64(%rbp), %rcx
	movq	-56(%rbp), %rdx
	imulq	16(%rdx), %rcx
	addq	%rcx, %rax
	movq	%rax, -40(%rbp)
	movq	-64(%rbp), %rax
	movq	%rax, -32(%rbp)
	movq	-104(%rbp), %rdi
	movq	-72(%rbp), %rsi
	movq	-64(%rbp), %rdx
	movq	-96(%rbp), %r8
	movq	-80(%rbp), %r9
	movq	-48(%rbp), %rax
	imulq	-72(%rbp), %rax
	shlq	$3, %rax
	addq	%rax, %r9
	leaq	-40(%rbp), %rcx
	callq	matvec
# %bb.3:                                #   in Loop: Header=BB3_1 Depth=1
	movq	-48(%rbp), %rax
	addq	$1, %rax
	movq	%rax, -48(%rbp)
	jmp	.LBB3_1
.LBB3_4:
	movq	%fs:40, %rax
	movq	-8(%rbp), %rcx
	cmpq	%rcx, %rax
	jne	.LBB3_6
# %bb.5:                                # %SP_return
	addq	$112, %rsp
	popq	%rbp
	.cfi_def_cfa %rsp, 8
	retq
.LBB3_6:                                # %CallStackCheckFailBlk
	.cfi_def_cfa %rbp, 16
	callq	__stack_chk_fail@PLT
.Lfunc_end3:
	.size	batched, .Lfunc_end3-batched
	.cfi_endproc
                                        # -- End function
	.section	.rodata.cst8,"aM",@progbits,8
	.p2align	3, 0x0                          # -- Begin function softmax
.LCPI4_0:
	.quad	0x40f0000000000000              # double 65536
	.text
	.prefalign	4, .Lfunc_end4, nop
	.type	softmax,@function
softmax:                                # @softmax
	.cfi_startproc
# %bb.0:
	pushq	%rbp
	.cfi_def_cfa_offset 16
	.cfi_offset %rbp, -16
	movq	%rsp, %rbp
	.cfi_def_cfa_register %rbp
	subq	$608, %rsp                      # imm = 0x260
	movq	%fs:40, %rax
	movq	%rax, -8(%rbp)
	movq	%rdi, -584(%rbp)
	movq	$3, -576(%rbp)
	movq	%rsi, -600(%rbp)
	movq	-584(%rbp), %rdi
	xorl	%esi, %esi
	callq	getv
	cvtsi2sd	%rax, %xmm0
	movsd	.LCPI4_0(%rip), %xmm1           # xmm1 = [6.5536E+4,0.0E+0]
	divsd	%xmm1, %xmm0
	movsd	%xmm0, -568(%rbp)
	movq	$1, -552(%rbp)
.LBB4_1:                                # =>This Inner Loop Header: Depth=1
	movq	-552(%rbp), %rax
	cmpq	-576(%rbp), %rax
	jge	.LBB4_6
# %bb.2:                                #   in Loop: Header=BB4_1 Depth=1
	movq	-584(%rbp), %rdi
	movq	-552(%rbp), %rsi
	callq	getv
	cvtsi2sd	%rax, %xmm0
	movsd	.LCPI4_0(%rip), %xmm1           # xmm1 = [6.5536E+4,0.0E+0]
	divsd	%xmm1, %xmm0
	movsd	%xmm0, -592(%rbp)
	movsd	-592(%rbp), %xmm0               # xmm0 = mem[0],zero
	ucomisd	-568(%rbp), %xmm0
	jbe	.LBB4_4
# %bb.3:                                #   in Loop: Header=BB4_1 Depth=1
	movsd	-592(%rbp), %xmm0               # xmm0 = mem[0],zero
	movsd	%xmm0, -568(%rbp)
.LBB4_4:                                #   in Loop: Header=BB4_1 Depth=1
	jmp	.LBB4_5
.LBB4_5:                                #   in Loop: Header=BB4_1 Depth=1
	movq	-552(%rbp), %rax
	addq	$1, %rax
	movq	%rax, -552(%rbp)
	jmp	.LBB4_1
.LBB4_6:
	xorps	%xmm0, %xmm0
	movsd	%xmm0, -560(%rbp)
	movq	$0, -536(%rbp)
.LBB4_7:                                # =>This Inner Loop Header: Depth=1
	movq	-536(%rbp), %rax
	cmpq	-576(%rbp), %rax
	jge	.LBB4_10
# %bb.8:                                #   in Loop: Header=BB4_7 Depth=1
	movq	-584(%rbp), %rdi
	movq	-536(%rbp), %rsi
	callq	getv
	cvtsi2sd	%rax, %xmm0
	movsd	.LCPI4_0(%rip), %xmm1           # xmm1 = [6.5536E+4,0.0E+0]
	divsd	%xmm1, %xmm0
	subsd	-568(%rbp), %xmm0
	callq	exp@PLT
	movq	-536(%rbp), %rax
	movsd	%xmm0, -528(%rbp,%rax,8)
	movq	-536(%rbp), %rax
	movsd	-528(%rbp,%rax,8), %xmm0        # xmm0 = mem[0],zero
	addsd	-560(%rbp), %xmm0
	movsd	%xmm0, -560(%rbp)
# %bb.9:                                #   in Loop: Header=BB4_7 Depth=1
	movq	-536(%rbp), %rax
	addq	$1, %rax
	movq	%rax, -536(%rbp)
	jmp	.LBB4_7
.LBB4_10:
	movq	$0, -544(%rbp)
.LBB4_11:                               # =>This Inner Loop Header: Depth=1
	movq	-544(%rbp), %rax
	cmpq	-576(%rbp), %rax
	jge	.LBB4_14
# %bb.12:                               #   in Loop: Header=BB4_11 Depth=1
	movq	-600(%rbp), %rdi
	movq	-544(%rbp), %rsi
	movq	-544(%rbp), %rax
	movsd	-528(%rbp,%rax,8), %xmm0        # xmm0 = mem[0],zero
	divsd	-560(%rbp), %xmm0
	movsd	.LCPI4_0(%rip), %xmm1           # xmm1 = [6.5536E+4,0.0E+0]
	mulsd	%xmm1, %xmm0
	cvttsd2si	%xmm0, %rdx
	callq	setv
# %bb.13:                               #   in Loop: Header=BB4_11 Depth=1
	movq	-544(%rbp), %rax
	addq	$1, %rax
	movq	%rax, -544(%rbp)
	jmp	.LBB4_11
.LBB4_14:
	movq	%fs:40, %rax
	movq	-8(%rbp), %rcx
	cmpq	%rcx, %rax
	jne	.LBB4_16
# %bb.15:                               # %SP_return
	addq	$608, %rsp                      # imm = 0x260
	popq	%rbp
	.cfi_def_cfa %rsp, 8
	retq
.LBB4_16:                               # %CallStackCheckFailBlk
	.cfi_def_cfa %rbp, 16
	callq	__stack_chk_fail@PLT
.Lfunc_end4:
	.size	softmax, .Lfunc_end4-softmax
	.cfi_endproc
                                        # -- End function
	.prefalign	4, .Lfunc_end5, nop     # -- Begin function layernorm
	.type	layernorm,@function
layernorm:                              # @layernorm
	.cfi_startproc
# %bb.0:
	pushq	%rbp
	.cfi_def_cfa_offset 16
	.cfi_offset %rbp, -16
	movq	%rsp, %rbp
	.cfi_def_cfa_register %rbp
	pushq	%r15
	pushq	%r14
	pushq	%rbx
	subq	$104, %rsp
	.cfi_offset %rbx, -40
	.cfi_offset %r14, -32
	.cfi_offset %r15, -24
	movq	%rdi, -80(%rbp)
	movq	%rsi, -48(%rbp)
	movq	%rdx, -128(%rbp)
	movq	%rcx, -120(%rbp)
	movq	%r8, -112(%rbp)
	movq	$0, -72(%rbp)
	movq	$0, -64(%rbp)
.LBB5_1:                                # =>This Inner Loop Header: Depth=1
	movq	-64(%rbp), %rax
	cmpq	-48(%rbp), %rax
	jge	.LBB5_4
# %bb.2:                                #   in Loop: Header=BB5_1 Depth=1
	movq	-80(%rbp), %rdi
	movq	-64(%rbp), %rsi
	callq	getv
	addq	-72(%rbp), %rax
	movq	%rax, -72(%rbp)
# %bb.3:                                #   in Loop: Header=BB5_1 Depth=1
	movq	-64(%rbp), %rax
	addq	$1, %rax
	movq	%rax, -64(%rbp)
	jmp	.LBB5_1
.LBB5_4:
	movq	-72(%rbp), %rax
	cqto
	idivq	-48(%rbp)
	movq	%rax, -96(%rbp)
	movq	$0, -40(%rbp)
	movq	$0, -56(%rbp)
.LBB5_5:                                # =>This Inner Loop Header: Depth=1
	movq	-56(%rbp), %rax
	cmpq	-48(%rbp), %rax
	jge	.LBB5_8
# %bb.6:                                #   in Loop: Header=BB5_5 Depth=1
	movq	-80(%rbp), %rdi
	movq	-56(%rbp), %rsi
	callq	getv
	subq	-96(%rbp), %rax
	movq	%rax, -88(%rbp)
	movq	-88(%rbp), %rdi
	movq	-88(%rbp), %rsi
	callq	qmul
	addq	-40(%rbp), %rax
	movq	%rax, -40(%rbp)
# %bb.7:                                #   in Loop: Header=BB5_5 Depth=1
	movq	-56(%rbp), %rax
	addq	$1, %rax
	movq	%rax, -56(%rbp)
	jmp	.LBB5_5
.LBB5_8:
	movq	-48(%rbp), %rcx
	movq	-40(%rbp), %rax
	cqto
	idivq	%rcx
	movq	%rax, -40(%rbp)
	movq	-40(%rbp), %rdi
	addq	$1, %rdi
	callq	qsqrt
	movl	$65536, %edi                    # imm = 0x10000
	movq	%rax, %rsi
	callq	qdiv
	movq	%rax, -104(%rbp)
	movq	$0, -32(%rbp)
.LBB5_9:                                # =>This Inner Loop Header: Depth=1
	movq	-32(%rbp), %rax
	cmpq	-48(%rbp), %rax
	jge	.LBB5_12
# %bb.10:                               #   in Loop: Header=BB5_9 Depth=1
	movq	-112(%rbp), %r14
	movq	-32(%rbp), %rbx
	movq	-80(%rbp), %rdi
	movq	-32(%rbp), %rsi
	callq	getv
	subq	-96(%rbp), %rax
	movq	-104(%rbp), %rsi
	movq	%rax, %rdi
	callq	qmul
	movq	%rax, %r15
	movq	-128(%rbp), %rdi
	movq	-32(%rbp), %rsi
	callq	getv
	movq	%r15, %rdi
	movq	%rax, %rsi
	callq	qmul
	movq	%rax, %r15
	movq	-120(%rbp), %rdi
	movq	-32(%rbp), %rsi
	callq	getv
	addq	%rax, %r15
	movq	%r14, %rdi
	movq	%rbx, %rsi
	movq	%r15, %rdx
	callq	setv
# %bb.11:                               #   in Loop: Header=BB5_9 Depth=1
	movq	-32(%rbp), %rax
	addq	$1, %rax
	movq	%rax, -32(%rbp)
	jmp	.LBB5_9
.LBB5_12:
	addq	$104, %rsp
	popq	%rbx
	popq	%r14
	popq	%r15
	popq	%rbp
	.cfi_def_cfa %rsp, 8
	retq
.Lfunc_end5:
	.size	layernorm, .Lfunc_end5-layernorm
	.cfi_endproc
                                        # -- End function
	.prefalign	4, .Lfunc_end6, nop     # -- Begin function fused_attention
	.type	fused_attention,@function
fused_attention:                        # @fused_attention
	.cfi_startproc
# %bb.0:
	pushq	%rbp
	.cfi_def_cfa_offset 16
	.cfi_offset %rbp, -16
	movq	%rsp, %rbp
	.cfi_def_cfa_register %rbp
	subq	$1264, %rsp                     # imm = 0x4F0
	movq	24(%rbp), %rax
	movq	16(%rbp), %rax
	movq	%fs:40, %rax
	movq	%rax, -8(%rbp)
	movq	%rdi, -1192(%rbp)
	movq	%rsi, -1160(%rbp)
	movq	%rdx, -1152(%rbp)
	movq	%rcx, -1224(%rbp)
	movq	%r8, -1216(%rbp)
	movq	%r9, -1208(%rbp)
	movq	$0, -1144(%rbp)
.LBB6_1:                                # =>This Loop Header: Depth=1
                                        #     Child Loop BB6_3 Depth 2
	cmpq	$3, -1144(%rbp)
	jge	.LBB6_8
# %bb.2:                                #   in Loop: Header=BB6_1 Depth=1
	movq	-1192(%rbp), %rax
	movq	(%rax), %rcx
	movq	%rcx, -784(%rbp)
	movq	8(%rax), %rcx
	movq	%rcx, -776(%rbp)
	movq	16(%rax), %rcx
	movq	%rcx, -768(%rbp)
	movq	24(%rax), %rax
	movq	%rax, -760(%rbp)
	movq	-1192(%rbp), %rax
	movq	(%rax), %rax
	movq	-1144(%rbp), %rcx
	shlq	$2, %rcx
	movq	-1192(%rbp), %rdx
	imulq	16(%rdx), %rcx
	addq	%rcx, %rax
	movq	%rax, -784(%rbp)
	movq	$4, -776(%rbp)
	movq	-1152(%rbp), %rax
	movq	(%rax), %rcx
	movq	%rcx, -816(%rbp)
	movq	8(%rax), %rcx
	movq	%rcx, -808(%rbp)
	movq	16(%rax), %rcx
	movq	%rcx, -800(%rbp)
	movq	24(%rax), %rax
	movq	%rax, -792(%rbp)
	movq	$4, -808(%rbp)
	movq	-1160(%rbp), %rdi
	leaq	-624(%rbp), %r9
	leaq	-784(%rbp), %rcx
	leaq	-816(%rbp), %r8
	movl	$4, %esi
	movl	$4, %edx
	callq	matvec
	movq	-1152(%rbp), %rax
	movq	(%rax), %rcx
	movq	%rcx, -848(%rbp)
	movq	8(%rax), %rcx
	movq	%rcx, -840(%rbp)
	movq	16(%rax), %rcx
	movq	%rcx, -832(%rbp)
	movq	24(%rax), %rax
	movq	%rax, -824(%rbp)
	movq	-1152(%rbp), %rax
	movq	(%rax), %rax
	movq	-1152(%rbp), %rcx
	movq	16(%rcx), %rcx
	shlq	$2, %rcx
	addq	%rcx, %rax
	movq	%rax, -848(%rbp)
	movq	$4, -840(%rbp)
	movq	-1160(%rbp), %rax
	movq	(%rax), %rcx
	movq	%rcx, -880(%rbp)
	movq	8(%rax), %rcx
	movq	%rcx, -872(%rbp)
	movq	16(%rax), %rcx
	movq	%rcx, -864(%rbp)
	movq	24(%rax), %rax
	movq	%rax, -856(%rbp)
	movq	-1160(%rbp), %rax
	movq	(%rax), %rax
	movq	-1160(%rbp), %rcx
	movq	16(%rcx), %rcx
	shlq	$4, %rcx
	addq	%rcx, %rax
	movq	%rax, -880(%rbp)
	movq	$16, -872(%rbp)
	leaq	-656(%rbp), %r9
	leaq	-880(%rbp), %rdi
	leaq	-784(%rbp), %rcx
	leaq	-848(%rbp), %r8
	movl	$4, %esi
	movl	$4, %edx
	callq	matvec
	movq	-1152(%rbp), %rax
	movq	(%rax), %rcx
	movq	%rcx, -912(%rbp)
	movq	8(%rax), %rcx
	movq	%rcx, -904(%rbp)
	movq	16(%rax), %rcx
	movq	%rcx, -896(%rbp)
	movq	24(%rax), %rax
	movq	%rax, -888(%rbp)
	movq	-1152(%rbp), %rax
	movq	(%rax), %rax
	movq	-1152(%rbp), %rcx
	movq	16(%rcx), %rcx
	shlq	$3, %rcx
	addq	%rcx, %rax
	movq	%rax, -912(%rbp)
	movq	$4, -904(%rbp)
	movq	-1160(%rbp), %rax
	movq	(%rax), %rcx
	movq	%rcx, -944(%rbp)
	movq	8(%rax), %rcx
	movq	%rcx, -936(%rbp)
	movq	16(%rax), %rcx
	movq	%rcx, -928(%rbp)
	movq	24(%rax), %rax
	movq	%rax, -920(%rbp)
	movq	-1160(%rbp), %rax
	movq	(%rax), %rax
	movq	-1160(%rbp), %rcx
	movq	16(%rcx), %rcx
	shlq	$5, %rcx
	addq	%rcx, %rax
	movq	%rax, -944(%rbp)
	movq	$16, -936(%rbp)
	leaq	-688(%rbp), %r9
	leaq	-944(%rbp), %rdi
	leaq	-784(%rbp), %rcx
	leaq	-912(%rbp), %r8
	movl	$4, %esi
	movl	$4, %edx
	callq	matvec
	movl	$0, -1108(%rbp)
.LBB6_3:                                #   Parent Loop BB6_1 Depth=1
                                        # =>  This Inner Loop Header: Depth=2
	cmpl	$4, -1108(%rbp)
	jge	.LBB6_6
# %bb.4:                                #   in Loop: Header=BB6_3 Depth=2
	movslq	-1108(%rbp), %rax
	movq	-624(%rbp,%rax,8), %rax
	movq	-1144(%rbp), %rcx
	leaq	-112(%rbp), %rdx
	shlq	$5, %rcx
	addq	%rcx, %rdx
	movslq	-1108(%rbp), %rcx
	movq	%rax, (%rdx,%rcx,8)
	movslq	-1108(%rbp), %rax
	movq	-656(%rbp,%rax,8), %rax
	movq	-1144(%rbp), %rcx
	leaq	-208(%rbp), %rdx
	shlq	$5, %rcx
	addq	%rcx, %rdx
	movslq	-1108(%rbp), %rcx
	movq	%rax, (%rdx,%rcx,8)
	movslq	-1108(%rbp), %rax
	movq	-688(%rbp,%rax,8), %rax
	movq	-1144(%rbp), %rcx
	leaq	-304(%rbp), %rdx
	shlq	$5, %rcx
	addq	%rcx, %rdx
	movslq	-1108(%rbp), %rcx
	movq	%rax, (%rdx,%rcx,8)
# %bb.5:                                #   in Loop: Header=BB6_3 Depth=2
	movl	-1108(%rbp), %eax
	addl	$1, %eax
	movl	%eax, -1108(%rbp)
	jmp	.LBB6_3
.LBB6_6:                                #   in Loop: Header=BB6_1 Depth=1
	jmp	.LBB6_7
.LBB6_7:                                #   in Loop: Header=BB6_1 Depth=1
	movq	-1144(%rbp), %rax
	addq	$1, %rax
	movq	%rax, -1144(%rbp)
	jmp	.LBB6_1
.LBB6_8:
	movq	$0, -1184(%rbp)
.LBB6_9:                                # =>This Loop Header: Depth=1
                                        #     Child Loop BB6_11 Depth 2
                                        #     Child Loop BB6_15 Depth 2
                                        #       Child Loop BB6_17 Depth 3
	cmpq	$3, -1184(%rbp)
	jge	.LBB6_24
# %bb.10:                               #   in Loop: Header=BB6_9 Depth=1
	movq	$0, -1176(%rbp)
.LBB6_11:                               #   Parent Loop BB6_9 Depth=1
                                        # =>  This Inner Loop Header: Depth=2
	cmpq	$3, -1176(%rbp)
	jge	.LBB6_14
# %bb.12:                               #   in Loop: Header=BB6_11 Depth=2
	movq	-1184(%rbp), %rax
	leaq	-112(%rbp), %rdi
	shlq	$5, %rax
	addq	%rax, %rdi
	movq	-1176(%rbp), %rax
	leaq	-208(%rbp), %rsi
	shlq	$5, %rax
	addq	%rax, %rsi
	callq	adot
	movq	%rax, %rdi
	movl	$131072, %esi                   # imm = 0x20000
	callq	qdiv
	movq	-1176(%rbp), %rcx
	movq	%rax, -720(%rbp,%rcx,8)
# %bb.13:                               #   in Loop: Header=BB6_11 Depth=2
	movq	-1176(%rbp), %rax
	addq	$1, %rax
	movq	%rax, -1176(%rbp)
	jmp	.LBB6_11
.LBB6_14:                               #   in Loop: Header=BB6_9 Depth=1
	leaq	-720(%rbp), %rax
	movq	%rax, -976(%rbp)
	movq	$3, -968(%rbp)
	movq	$8, -960(%rbp)
	movq	$8, -952(%rbp)
	leaq	-752(%rbp), %rax
	movq	%rax, -1008(%rbp)
	movq	$3, -1000(%rbp)
	movq	$8, -992(%rbp)
	movq	$8, -984(%rbp)
	leaq	-976(%rbp), %rdi
	leaq	-1008(%rbp), %rsi
	callq	softmax
	movl	$0, -1132(%rbp)
.LBB6_15:                               #   Parent Loop BB6_9 Depth=1
                                        # =>  This Loop Header: Depth=2
                                        #       Child Loop BB6_17 Depth 3
	cmpl	$4, -1132(%rbp)
	jge	.LBB6_22
# %bb.16:                               #   in Loop: Header=BB6_15 Depth=2
	movq	$0, -1200(%rbp)
	movq	$0, -1168(%rbp)
.LBB6_17:                               #   Parent Loop BB6_9 Depth=1
                                        #     Parent Loop BB6_15 Depth=2
                                        # =>    This Inner Loop Header: Depth=3
	cmpq	$3, -1168(%rbp)
	jge	.LBB6_20
# %bb.18:                               #   in Loop: Header=BB6_17 Depth=3
	movq	-1168(%rbp), %rax
	leaq	-304(%rbp), %rcx
	shlq	$5, %rax
	addq	%rax, %rcx
	movslq	-1132(%rbp), %rax
	movq	(%rcx,%rax,8), %rdi
	movq	-1168(%rbp), %rax
	movq	-752(%rbp,%rax,8), %rsi
	callq	qmul
	addq	-1200(%rbp), %rax
	movq	%rax, -1200(%rbp)
# %bb.19:                               #   in Loop: Header=BB6_17 Depth=3
	movq	-1168(%rbp), %rax
	addq	$1, %rax
	movq	%rax, -1168(%rbp)
	jmp	.LBB6_17
.LBB6_20:                               #   in Loop: Header=BB6_15 Depth=2
	movq	-1200(%rbp), %rax
	movq	-1184(%rbp), %rcx
	leaq	-400(%rbp), %rdx
	shlq	$5, %rcx
	addq	%rcx, %rdx
	movslq	-1132(%rbp), %rcx
	movq	%rax, (%rdx,%rcx,8)
# %bb.21:                               #   in Loop: Header=BB6_15 Depth=2
	movl	-1132(%rbp), %eax
	addl	$1, %eax
	movl	%eax, -1132(%rbp)
	jmp	.LBB6_15
.LBB6_22:                               #   in Loop: Header=BB6_9 Depth=1
	jmp	.LBB6_23
.LBB6_23:                               #   in Loop: Header=BB6_9 Depth=1
	movq	-1184(%rbp), %rax
	addq	$1, %rax
	movq	%rax, -1184(%rbp)
	jmp	.LBB6_9
.LBB6_24:
	movq	$0, -1120(%rbp)
.LBB6_25:                               # =>This Loop Header: Depth=1
                                        #     Child Loop BB6_27 Depth 2
                                        #     Child Loop BB6_31 Depth 2
	cmpq	$3, -1120(%rbp)
	jge	.LBB6_36
# %bb.26:                               #   in Loop: Header=BB6_25 Depth=1
	movq	-1120(%rbp), %rax
	leaq	-400(%rbp), %rcx
	shlq	$5, %rax
	addq	%rax, %rcx
	movq	%rcx, -1040(%rbp)
	movq	$4, -1032(%rbp)
	movq	$8, -1024(%rbp)
	movq	$8, -1016(%rbp)
	movq	-1120(%rbp), %rax
	leaq	-592(%rbp), %rcx
	shlq	$5, %rax
	addq	%rax, %rcx
	movq	%rcx, -1256(%rbp)
	movq	$4, -1248(%rbp)
	movq	$8, -1240(%rbp)
	movq	$8, -1232(%rbp)
	movq	-1224(%rbp), %rdi
	movq	-1216(%rbp), %r8
	movq	-1120(%rbp), %rax
	leaq	-592(%rbp), %r9
	shlq	$5, %rax
	addq	%rax, %r9
	leaq	-1040(%rbp), %rcx
	movl	$4, %esi
	movl	$4, %edx
	callq	matvec
	movl	$0, -1124(%rbp)
.LBB6_27:                               #   Parent Loop BB6_25 Depth=1
                                        # =>  This Inner Loop Header: Depth=2
	cmpl	$4, -1124(%rbp)
	jge	.LBB6_30
# %bb.28:                               #   in Loop: Header=BB6_27 Depth=2
	movq	-1192(%rbp), %rdi
	movq	-1120(%rbp), %rsi
	shlq	$2, %rsi
	movslq	-1124(%rbp), %rax
	addq	%rax, %rsi
	callq	getv
	movq	-1120(%rbp), %rcx
	leaq	-592(%rbp), %rdx
	shlq	$5, %rcx
	addq	%rcx, %rdx
	movslq	-1124(%rbp), %rcx
	addq	(%rdx,%rcx,8), %rax
	movq	-1120(%rbp), %rcx
	leaq	-496(%rbp), %rdx
	shlq	$5, %rcx
	addq	%rcx, %rdx
	movslq	-1124(%rbp), %rcx
	movq	%rax, (%rdx,%rcx,8)
# %bb.29:                               #   in Loop: Header=BB6_27 Depth=2
	movl	-1124(%rbp), %eax
	addl	$1, %eax
	movl	%eax, -1124(%rbp)
	jmp	.LBB6_27
.LBB6_30:                               #   in Loop: Header=BB6_25 Depth=1
	movq	-1120(%rbp), %rax
	leaq	-496(%rbp), %rcx
	shlq	$5, %rax
	addq	%rax, %rcx
	movq	%rcx, -1072(%rbp)
	movq	$4, -1064(%rbp)
	movq	$8, -1056(%rbp)
	movq	$8, -1048(%rbp)
	movq	-1120(%rbp), %rax
	leaq	-400(%rbp), %rcx
	shlq	$5, %rax
	addq	%rax, %rcx
	movq	%rcx, -1104(%rbp)
	movq	$4, -1096(%rbp)
	movq	$8, -1088(%rbp)
	movq	$8, -1080(%rbp)
	movq	-1208(%rbp), %rdx
	movq	16(%rbp), %rcx
	leaq	-1072(%rbp), %rdi
	leaq	-1104(%rbp), %r8
	movl	$4, %esi
	callq	layernorm
	movl	$0, -1128(%rbp)
.LBB6_31:                               #   Parent Loop BB6_25 Depth=1
                                        # =>  This Inner Loop Header: Depth=2
	cmpl	$4, -1128(%rbp)
	jge	.LBB6_34
# %bb.32:                               #   in Loop: Header=BB6_31 Depth=2
	movq	24(%rbp), %rdi
	movq	-1120(%rbp), %rsi
	shlq	$2, %rsi
	movslq	-1128(%rbp), %rax
	addq	%rax, %rsi
	movq	-1120(%rbp), %rax
	leaq	-400(%rbp), %rcx
	shlq	$5, %rax
	addq	%rax, %rcx
	movslq	-1128(%rbp), %rax
	movq	(%rcx,%rax,8), %rdx
	callq	setv
# %bb.33:                               #   in Loop: Header=BB6_31 Depth=2
	movl	-1128(%rbp), %eax
	addl	$1, %eax
	movl	%eax, -1128(%rbp)
	jmp	.LBB6_31
.LBB6_34:                               #   in Loop: Header=BB6_25 Depth=1
	jmp	.LBB6_35
.LBB6_35:                               #   in Loop: Header=BB6_25 Depth=1
	movq	-1120(%rbp), %rax
	addq	$1, %rax
	movq	%rax, -1120(%rbp)
	jmp	.LBB6_25
.LBB6_36:
	movq	%fs:40, %rax
	movq	-8(%rbp), %rcx
	cmpq	%rcx, %rax
	jne	.LBB6_38
# %bb.37:                               # %SP_return
	addq	$1264, %rsp                     # imm = 0x4F0
	popq	%rbp
	.cfi_def_cfa %rsp, 8
	retq
.LBB6_38:                               # %CallStackCheckFailBlk
	.cfi_def_cfa %rbp, 16
	callq	__stack_chk_fail@PLT
.Lfunc_end6:
	.size	fused_attention, .Lfunc_end6-fused_attention
	.cfi_endproc
                                        # -- End function
	.prefalign	4, .Lfunc_end7, nop     # -- Begin function fused_attention_ref
	.type	fused_attention_ref,@function
fused_attention_ref:                    # @fused_attention_ref
	.cfi_startproc
# %bb.0:
	pushq	%rbp
	.cfi_def_cfa_offset 16
	.cfi_offset %rbp, -16
	movq	%rsp, %rbp
	.cfi_def_cfa_register %rbp
	subq	$1392, %rsp                     # imm = 0x570
	movq	24(%rbp), %rax
	movq	16(%rbp), %rax
	movq	%fs:40, %rax
	movq	%rax, -8(%rbp)
	movq	%rdi, -1352(%rbp)
	movq	%rsi, -1392(%rbp)
	movq	%rdx, -1384(%rbp)
	movq	%rcx, -1376(%rbp)
	movq	%r8, -1368(%rbp)
	movq	%r9, -1360(%rbp)
	movq	-1392(%rbp), %rax
	movq	%rax, -784(%rbp)
	movq	$48, -776(%rbp)
	movq	$8, -768(%rbp)
	movq	$8, -760(%rbp)
	movq	-1384(%rbp), %rax
	movq	%rax, -816(%rbp)
	movq	$12, -808(%rbp)
	movq	$8, -800(%rbp)
	movq	$8, -792(%rbp)
	movq	-1376(%rbp), %rax
	movq	%rax, -848(%rbp)
	movq	$16, -840(%rbp)
	movq	$8, -832(%rbp)
	movq	$8, -824(%rbp)
	movq	-1368(%rbp), %rax
	movq	%rax, -880(%rbp)
	movq	$4, -872(%rbp)
	movq	$8, -864(%rbp)
	movq	$8, -856(%rbp)
	movq	-1360(%rbp), %rax
	movq	%rax, -912(%rbp)
	movq	$4, -904(%rbp)
	movq	$8, -896(%rbp)
	movq	$8, -888(%rbp)
	movq	16(%rbp), %rax
	movq	%rax, -944(%rbp)
	movq	$4, -936(%rbp)
	movq	$8, -928(%rbp)
	movq	$8, -920(%rbp)
	movl	$0, -1308(%rbp)
.LBB7_1:                                # =>This Loop Header: Depth=1
                                        #     Child Loop BB7_3 Depth 2
	cmpl	$3, -1308(%rbp)
	jge	.LBB7_8
# %bb.2:                                #   in Loop: Header=BB7_1 Depth=1
	movq	-1352(%rbp), %rax
	movl	-1308(%rbp), %ecx
	shll	$2, %ecx
	movslq	%ecx, %rcx
	shlq	$3, %rcx
	addq	%rcx, %rax
	movq	%rax, -976(%rbp)
	movq	$4, -968(%rbp)
	movq	$8, -960(%rbp)
	movq	$8, -952(%rbp)
	movq	-816(%rbp), %rax
	movq	%rax, -1008(%rbp)
	movq	-808(%rbp), %rax
	movq	%rax, -1000(%rbp)
	movq	-800(%rbp), %rax
	movq	%rax, -992(%rbp)
	movq	-792(%rbp), %rax
	movq	%rax, -984(%rbp)
	movq	-816(%rbp), %rax
	movq	%rax, -1040(%rbp)
	movq	-808(%rbp), %rax
	movq	%rax, -1032(%rbp)
	movq	-800(%rbp), %rax
	movq	%rax, -1024(%rbp)
	movq	-792(%rbp), %rax
	movq	%rax, -1016(%rbp)
	movq	-816(%rbp), %rax
	movq	%rax, -1072(%rbp)
	movq	-808(%rbp), %rax
	movq	%rax, -1064(%rbp)
	movq	-800(%rbp), %rax
	movq	%rax, -1056(%rbp)
	movq	-792(%rbp), %rax
	movq	%rax, -1048(%rbp)
	movq	-816(%rbp), %rax
	movq	%rax, -1008(%rbp)
	movq	$4, -1000(%rbp)
	movq	-816(%rbp), %rax
	addq	$32, %rax
	movq	%rax, -1040(%rbp)
	movq	$4, -1032(%rbp)
	movq	-816(%rbp), %rax
	addq	$64, %rax
	movq	%rax, -1072(%rbp)
	movq	$4, -1064(%rbp)
	movq	-784(%rbp), %rax
	movq	%rax, -1104(%rbp)
	movq	-776(%rbp), %rax
	movq	%rax, -1096(%rbp)
	movq	-768(%rbp), %rax
	movq	%rax, -1088(%rbp)
	movq	-760(%rbp), %rax
	movq	%rax, -1080(%rbp)
	movq	-784(%rbp), %rax
	movq	%rax, -1136(%rbp)
	movq	-776(%rbp), %rax
	movq	%rax, -1128(%rbp)
	movq	-768(%rbp), %rax
	movq	%rax, -1120(%rbp)
	movq	-760(%rbp), %rax
	movq	%rax, -1112(%rbp)
	movq	-784(%rbp), %rax
	addq	$128, %rax
	movq	%rax, -1104(%rbp)
	movq	$16, -1096(%rbp)
	movq	-784(%rbp), %rax
	addq	$256, %rax                      # imm = 0x100
	movq	%rax, -1136(%rbp)
	movq	$16, -1128(%rbp)
	leaq	-624(%rbp), %r9
	leaq	-784(%rbp), %rdi
	leaq	-976(%rbp), %rcx
	leaq	-1008(%rbp), %r8
	movl	$4, %esi
	movl	$4, %edx
	callq	matvec
	leaq	-656(%rbp), %r9
	leaq	-1104(%rbp), %rdi
	leaq	-976(%rbp), %rcx
	leaq	-1040(%rbp), %r8
	movl	$4, %esi
	movl	$4, %edx
	callq	matvec
	leaq	-688(%rbp), %r9
	leaq	-1136(%rbp), %rdi
	leaq	-976(%rbp), %rcx
	leaq	-1072(%rbp), %r8
	movl	$4, %esi
	movl	$4, %edx
	callq	matvec
	movl	$0, -1304(%rbp)
.LBB7_3:                                #   Parent Loop BB7_1 Depth=1
                                        # =>  This Inner Loop Header: Depth=2
	cmpl	$4, -1304(%rbp)
	jge	.LBB7_6
# %bb.4:                                #   in Loop: Header=BB7_3 Depth=2
	movslq	-1304(%rbp), %rax
	movq	-624(%rbp,%rax,8), %rax
	movslq	-1308(%rbp), %rcx
	leaq	-112(%rbp), %rdx
	shlq	$5, %rcx
	addq	%rcx, %rdx
	movslq	-1304(%rbp), %rcx
	movq	%rax, (%rdx,%rcx,8)
	movslq	-1304(%rbp), %rax
	movq	-656(%rbp,%rax,8), %rax
	movslq	-1308(%rbp), %rcx
	leaq	-208(%rbp), %rdx
	shlq	$5, %rcx
	addq	%rcx, %rdx
	movslq	-1304(%rbp), %rcx
	movq	%rax, (%rdx,%rcx,8)
	movslq	-1304(%rbp), %rax
	movq	-688(%rbp,%rax,8), %rax
	movslq	-1308(%rbp), %rcx
	leaq	-304(%rbp), %rdx
	shlq	$5, %rcx
	addq	%rcx, %rdx
	movslq	-1304(%rbp), %rcx
	movq	%rax, (%rdx,%rcx,8)
# %bb.5:                                #   in Loop: Header=BB7_3 Depth=2
	movl	-1304(%rbp), %eax
	addl	$1, %eax
	movl	%eax, -1304(%rbp)
	jmp	.LBB7_3
.LBB7_6:                                #   in Loop: Header=BB7_1 Depth=1
	jmp	.LBB7_7
.LBB7_7:                                #   in Loop: Header=BB7_1 Depth=1
	movl	-1308(%rbp), %eax
	addl	$1, %eax
	movl	%eax, -1308(%rbp)
	jmp	.LBB7_1
.LBB7_8:
	movl	$0, -1332(%rbp)
.LBB7_9:                                # =>This Loop Header: Depth=1
                                        #     Child Loop BB7_11 Depth 2
                                        #     Child Loop BB7_15 Depth 2
                                        #       Child Loop BB7_17 Depth 3
	cmpl	$3, -1332(%rbp)
	jge	.LBB7_24
# %bb.10:                               #   in Loop: Header=BB7_9 Depth=1
	movl	$0, -1328(%rbp)
.LBB7_11:                               #   Parent Loop BB7_9 Depth=1
                                        # =>  This Inner Loop Header: Depth=2
	cmpl	$3, -1328(%rbp)
	jge	.LBB7_14
# %bb.12:                               #   in Loop: Header=BB7_11 Depth=2
	movslq	-1332(%rbp), %rax
	leaq	-112(%rbp), %rdi
	shlq	$5, %rax
	addq	%rax, %rdi
	movslq	-1328(%rbp), %rax
	leaq	-208(%rbp), %rsi
	shlq	$5, %rax
	addq	%rax, %rsi
	callq	adot
	movq	%rax, %rdi
	movl	$131072, %esi                   # imm = 0x20000
	callq	qdiv
	movslq	-1328(%rbp), %rcx
	movq	%rax, -720(%rbp,%rcx,8)
# %bb.13:                               #   in Loop: Header=BB7_11 Depth=2
	movl	-1328(%rbp), %eax
	addl	$1, %eax
	movl	%eax, -1328(%rbp)
	jmp	.LBB7_11
.LBB7_14:                               #   in Loop: Header=BB7_9 Depth=1
	leaq	-720(%rbp), %rax
	movq	%rax, -1168(%rbp)
	movq	$3, -1160(%rbp)
	movq	$8, -1152(%rbp)
	movq	$8, -1144(%rbp)
	leaq	-752(%rbp), %rax
	movq	%rax, -1200(%rbp)
	movq	$3, -1192(%rbp)
	movq	$8, -1184(%rbp)
	movq	$8, -1176(%rbp)
	leaq	-1168(%rbp), %rdi
	leaq	-1200(%rbp), %rsi
	callq	softmax
	movl	$0, -1324(%rbp)
.LBB7_15:                               #   Parent Loop BB7_9 Depth=1
                                        # =>  This Loop Header: Depth=2
                                        #       Child Loop BB7_17 Depth 3
	cmpl	$4, -1324(%rbp)
	jge	.LBB7_22
# %bb.16:                               #   in Loop: Header=BB7_15 Depth=2
	movq	$0, -1344(%rbp)
	movl	$0, -1320(%rbp)
.LBB7_17:                               #   Parent Loop BB7_9 Depth=1
                                        #     Parent Loop BB7_15 Depth=2
                                        # =>    This Inner Loop Header: Depth=3
	cmpl	$3, -1320(%rbp)
	jge	.LBB7_20
# %bb.18:                               #   in Loop: Header=BB7_17 Depth=3
	movslq	-1320(%rbp), %rax
	leaq	-304(%rbp), %rcx
	shlq	$5, %rax
	addq	%rax, %rcx
	movslq	-1324(%rbp), %rax
	movq	(%rcx,%rax,8), %rdi
	movslq	-1320(%rbp), %rax
	movq	-752(%rbp,%rax,8), %rsi
	callq	qmul
	addq	-1344(%rbp), %rax
	movq	%rax, -1344(%rbp)
# %bb.19:                               #   in Loop: Header=BB7_17 Depth=3
	movl	-1320(%rbp), %eax
	addl	$1, %eax
	movl	%eax, -1320(%rbp)
	jmp	.LBB7_17
.LBB7_20:                               #   in Loop: Header=BB7_15 Depth=2
	movq	-1344(%rbp), %rax
	movslq	-1332(%rbp), %rcx
	leaq	-400(%rbp), %rdx
	shlq	$5, %rcx
	addq	%rcx, %rdx
	movslq	-1324(%rbp), %rcx
	movq	%rax, (%rdx,%rcx,8)
# %bb.21:                               #   in Loop: Header=BB7_15 Depth=2
	movl	-1324(%rbp), %eax
	addl	$1, %eax
	movl	%eax, -1324(%rbp)
	jmp	.LBB7_15
.LBB7_22:                               #   in Loop: Header=BB7_9 Depth=1
	jmp	.LBB7_23
.LBB7_23:                               #   in Loop: Header=BB7_9 Depth=1
	movl	-1332(%rbp), %eax
	addl	$1, %eax
	movl	%eax, -1332(%rbp)
	jmp	.LBB7_9
.LBB7_24:
	movl	$0, -1300(%rbp)
.LBB7_25:                               # =>This Loop Header: Depth=1
                                        #     Child Loop BB7_27 Depth 2
                                        #     Child Loop BB7_31 Depth 2
	cmpl	$3, -1300(%rbp)
	jge	.LBB7_36
# %bb.26:                               #   in Loop: Header=BB7_25 Depth=1
	movslq	-1300(%rbp), %rax
	leaq	-400(%rbp), %rcx
	shlq	$5, %rax
	addq	%rax, %rcx
	movq	%rcx, -1232(%rbp)
	movq	$4, -1224(%rbp)
	movq	$8, -1216(%rbp)
	movq	$8, -1208(%rbp)
	movslq	-1300(%rbp), %rax
	leaq	-496(%rbp), %r9
	shlq	$5, %rax
	addq	%rax, %r9
	leaq	-848(%rbp), %rdi
	leaq	-1232(%rbp), %rcx
	leaq	-880(%rbp), %r8
	movl	$4, %esi
	movl	$4, %edx
	callq	matvec
	movl	$0, -1312(%rbp)
.LBB7_27:                               #   Parent Loop BB7_25 Depth=1
                                        # =>  This Inner Loop Header: Depth=2
	cmpl	$4, -1312(%rbp)
	jge	.LBB7_30
# %bb.28:                               #   in Loop: Header=BB7_27 Depth=2
	movq	-1352(%rbp), %rax
	movl	-1300(%rbp), %ecx
	shll	$2, %ecx
	addl	-1312(%rbp), %ecx
	movslq	%ecx, %rcx
	movq	(%rax,%rcx,8), %rax
	movslq	-1300(%rbp), %rcx
	leaq	-496(%rbp), %rdx
	shlq	$5, %rcx
	addq	%rcx, %rdx
	movslq	-1312(%rbp), %rcx
	addq	(%rdx,%rcx,8), %rax
	movslq	-1300(%rbp), %rcx
	leaq	-592(%rbp), %rdx
	shlq	$5, %rcx
	addq	%rcx, %rdx
	movslq	-1312(%rbp), %rcx
	movq	%rax, (%rdx,%rcx,8)
# %bb.29:                               #   in Loop: Header=BB7_27 Depth=2
	movl	-1312(%rbp), %eax
	addl	$1, %eax
	movl	%eax, -1312(%rbp)
	jmp	.LBB7_27
.LBB7_30:                               #   in Loop: Header=BB7_25 Depth=1
	movslq	-1300(%rbp), %rax
	leaq	-592(%rbp), %rcx
	shlq	$5, %rax
	addq	%rax, %rcx
	movq	%rcx, -1264(%rbp)
	movq	$4, -1256(%rbp)
	movq	$8, -1248(%rbp)
	movq	$8, -1240(%rbp)
	movslq	-1300(%rbp), %rax
	leaq	-400(%rbp), %rcx
	shlq	$5, %rax
	addq	%rax, %rcx
	movq	%rcx, -1296(%rbp)
	movq	$4, -1288(%rbp)
	movq	$8, -1280(%rbp)
	movq	$8, -1272(%rbp)
	leaq	-1264(%rbp), %rdi
	leaq	-912(%rbp), %rdx
	leaq	-944(%rbp), %rcx
	leaq	-1296(%rbp), %r8
	movl	$4, %esi
	callq	layernorm
	movl	$0, -1316(%rbp)
.LBB7_31:                               #   Parent Loop BB7_25 Depth=1
                                        # =>  This Inner Loop Header: Depth=2
	cmpl	$4, -1316(%rbp)
	jge	.LBB7_34
# %bb.32:                               #   in Loop: Header=BB7_31 Depth=2
	movslq	-1300(%rbp), %rax
	leaq	-400(%rbp), %rcx
	shlq	$5, %rax
	addq	%rax, %rcx
	movslq	-1316(%rbp), %rax
	movq	(%rcx,%rax,8), %rax
	movq	24(%rbp), %rcx
	movl	-1300(%rbp), %edx
	shll	$2, %edx
	addl	-1316(%rbp), %edx
	movslq	%edx, %rdx
	movq	%rax, (%rcx,%rdx,8)
# %bb.33:                               #   in Loop: Header=BB7_31 Depth=2
	movl	-1316(%rbp), %eax
	addl	$1, %eax
	movl	%eax, -1316(%rbp)
	jmp	.LBB7_31
.LBB7_34:                               #   in Loop: Header=BB7_25 Depth=1
	jmp	.LBB7_35
.LBB7_35:                               #   in Loop: Header=BB7_25 Depth=1
	movl	-1300(%rbp), %eax
	addl	$1, %eax
	movl	%eax, -1300(%rbp)
	jmp	.LBB7_25
.LBB7_36:
	movq	%fs:40, %rax
	movq	-8(%rbp), %rcx
	cmpq	%rcx, %rax
	jne	.LBB7_38
# %bb.37:                               # %SP_return
	addq	$1392, %rsp                     # imm = 0x570
	popq	%rbp
	.cfi_def_cfa %rsp, 8
	retq
.LBB7_38:                               # %CallStackCheckFailBlk
	.cfi_def_cfa %rbp, 16
	callq	__stack_chk_fail@PLT
.Lfunc_end7:
	.size	fused_attention_ref, .Lfunc_end7-fused_attention_ref
	.cfi_endproc
                                        # -- End function
	.prefalign	4, .Lfunc_end8, nop     # -- Begin function topk
	.type	topk,@function
topk:                                   # @topk
	.cfi_startproc
# %bb.0:
	pushq	%rbp
	.cfi_def_cfa_offset 16
	.cfi_offset %rbp, -16
	movq	%rsp, %rbp
	.cfi_def_cfa_register %rbp
	subq	$1152, %rsp                     # imm = 0x480
	movq	%fs:40, %rax
	movq	%rax, -8(%rbp)
	movq	%rdi, -1144(%rbp)
	movq	%rsi, -1136(%rbp)
	movq	%rdx, -1072(%rbp)
	movq	%rcx, -1112(%rbp)
	movq	%r8, -1128(%rbp)
	movq	%r9, -1120(%rbp)
	movq	$0, -1096(%rbp)
.LBB8_1:                                # =>This Inner Loop Header: Depth=1
	movq	-1096(%rbp), %rax
	cmpq	-1072(%rbp), %rax
	jge	.LBB8_4
# %bb.2:                                #   in Loop: Header=BB8_1 Depth=1
	movq	-1096(%rbp), %rax
	movq	$-1, -528(%rbp,%rax,8)
	movq	-1096(%rbp), %rax
	movq	$-999999999, -1040(%rbp,%rax,8) # imm = 0xC4653601
# %bb.3:                                #   in Loop: Header=BB8_1 Depth=1
	movq	-1096(%rbp), %rax
	addq	$1, %rax
	movq	%rax, -1096(%rbp)
	jmp	.LBB8_1
.LBB8_4:
	movq	$0, -1064(%rbp)
.LBB8_5:                                # =>This Loop Header: Depth=1
                                        #     Child Loop BB8_7 Depth 2
                                        #     Child Loop BB8_15 Depth 2
	movq	-1064(%rbp), %rax
	cmpq	-1136(%rbp), %rax
	jge	.LBB8_24
# %bb.6:                                #   in Loop: Header=BB8_5 Depth=1
	movq	-1144(%rbp), %rdi
	movq	-1064(%rbp), %rsi
	callq	getv
	movq	%rax, -1104(%rbp)
	movq	-1072(%rbp), %rax
	movq	%rax, -1088(%rbp)
	movq	$0, -1080(%rbp)
.LBB8_7:                                #   Parent Loop BB8_5 Depth=1
                                        # =>  This Inner Loop Header: Depth=2
	movq	-1080(%rbp), %rax
	cmpq	-1072(%rbp), %rax
	jge	.LBB8_12
# %bb.8:                                #   in Loop: Header=BB8_7 Depth=2
	movq	-1104(%rbp), %rax
	movq	-1080(%rbp), %rcx
	cmpq	-1040(%rbp,%rcx,8), %rax
	jle	.LBB8_10
# %bb.9:                                #   in Loop: Header=BB8_5 Depth=1
	movq	-1080(%rbp), %rax
	movq	%rax, -1088(%rbp)
	jmp	.LBB8_13
.LBB8_10:                               #   in Loop: Header=BB8_7 Depth=2
	jmp	.LBB8_11
.LBB8_11:                               #   in Loop: Header=BB8_7 Depth=2
	movq	-1080(%rbp), %rax
	addq	$1, %rax
	movq	%rax, -1080(%rbp)
	jmp	.LBB8_7
.LBB8_12:                               # %.loopexit
                                        #   in Loop: Header=BB8_5 Depth=1
	jmp	.LBB8_13
.LBB8_13:                               #   in Loop: Header=BB8_5 Depth=1
	movq	-1088(%rbp), %rax
	cmpq	-1072(%rbp), %rax
	jge	.LBB8_22
# %bb.14:                               #   in Loop: Header=BB8_5 Depth=1
	movq	-1072(%rbp), %rax
	subq	$1, %rax
	movq	%rax, -1056(%rbp)
.LBB8_15:                               #   Parent Loop BB8_5 Depth=1
                                        # =>  This Inner Loop Header: Depth=2
	movq	-1056(%rbp), %rax
	cmpq	-1088(%rbp), %rax
	jle	.LBB8_18
# %bb.16:                               #   in Loop: Header=BB8_15 Depth=2
	movq	-1056(%rbp), %rax
	subq	$1, %rax
	movq	-1040(%rbp,%rax,8), %rax
	movq	-1056(%rbp), %rcx
	movq	%rax, -1040(%rbp,%rcx,8)
	movq	-1056(%rbp), %rax
	subq	$1, %rax
	movq	-528(%rbp,%rax,8), %rax
	movq	-1056(%rbp), %rcx
	movq	%rax, -528(%rbp,%rcx,8)
# %bb.17:                               #   in Loop: Header=BB8_15 Depth=2
	movq	-1056(%rbp), %rax
	addq	$-1, %rax
	movq	%rax, -1056(%rbp)
	jmp	.LBB8_15
.LBB8_18:                               #   in Loop: Header=BB8_5 Depth=1
	movq	-1104(%rbp), %rax
	movq	-1088(%rbp), %rcx
	movq	%rax, -1040(%rbp,%rcx,8)
	cmpq	$0, -1112(%rbp)
	je	.LBB8_20
# %bb.19:                               #   in Loop: Header=BB8_5 Depth=1
	movq	-1112(%rbp), %rdi
	movq	-1064(%rbp), %rsi
	callq	getv
	jmp	.LBB8_21
.LBB8_20:                               #   in Loop: Header=BB8_5 Depth=1
	movq	-1064(%rbp), %rax
.LBB8_21:                               #   in Loop: Header=BB8_5 Depth=1
	movq	-1088(%rbp), %rcx
	movq	%rax, -528(%rbp,%rcx,8)
.LBB8_22:                               #   in Loop: Header=BB8_5 Depth=1
	jmp	.LBB8_23
.LBB8_23:                               #   in Loop: Header=BB8_5 Depth=1
	movq	-1064(%rbp), %rax
	addq	$1, %rax
	movq	%rax, -1064(%rbp)
	jmp	.LBB8_5
.LBB8_24:
	movq	$0, -1048(%rbp)
.LBB8_25:                               # =>This Inner Loop Header: Depth=1
	movq	-1048(%rbp), %rax
	cmpq	-1072(%rbp), %rax
	jge	.LBB8_28
# %bb.26:                               #   in Loop: Header=BB8_25 Depth=1
	movq	-1128(%rbp), %rdi
	movq	-1048(%rbp), %rsi
	movq	-1048(%rbp), %rax
	movq	-528(%rbp,%rax,8), %rdx
	callq	setv
	movq	-1120(%rbp), %rdi
	movq	-1048(%rbp), %rsi
	movq	-1048(%rbp), %rax
	movq	-1040(%rbp,%rax,8), %rdx
	callq	setv
# %bb.27:                               #   in Loop: Header=BB8_25 Depth=1
	movq	-1048(%rbp), %rax
	addq	$1, %rax
	movq	%rax, -1048(%rbp)
	jmp	.LBB8_25
.LBB8_28:
	movq	%fs:40, %rax
	movq	-8(%rbp), %rcx
	cmpq	%rcx, %rax
	jne	.LBB8_30
# %bb.29:                               # %SP_return
	addq	$1152, %rsp                     # imm = 0x480
	popq	%rbp
	.cfi_def_cfa %rsp, 8
	retq
.LBB8_30:                               # %CallStackCheckFailBlk
	.cfi_def_cfa %rbp, 16
	callq	__stack_chk_fail@PLT
.Lfunc_end8:
	.size	topk, .Lfunc_end8-topk
	.cfi_endproc
                                        # -- End function
	.prefalign	4, .Lfunc_end9, nop     # -- Begin function argmax
	.type	argmax,@function
argmax:                                 # @argmax
	.cfi_startproc
# %bb.0:
	pushq	%rbp
	.cfi_def_cfa_offset 16
	.cfi_offset %rbp, -16
	movq	%rsp, %rbp
	.cfi_def_cfa_register %rbp
	subq	$48, %rsp
	movq	%rdi, -40(%rbp)
	movq	$5, -48(%rbp)
	movq	$0, -32(%rbp)
	movq	-40(%rbp), %rdi
	xorl	%esi, %esi
	callq	getv
	movq	%rax, -24(%rbp)
	movq	$1, -8(%rbp)
.LBB9_1:                                # =>This Inner Loop Header: Depth=1
	movq	-8(%rbp), %rax
	cmpq	-48(%rbp), %rax
	jge	.LBB9_6
# %bb.2:                                #   in Loop: Header=BB9_1 Depth=1
	movq	-40(%rbp), %rdi
	movq	-8(%rbp), %rsi
	callq	getv
	movq	%rax, -16(%rbp)
	movq	-16(%rbp), %rax
	cmpq	-24(%rbp), %rax
	jle	.LBB9_4
# %bb.3:                                #   in Loop: Header=BB9_1 Depth=1
	movq	-16(%rbp), %rax
	movq	%rax, -24(%rbp)
	movq	-8(%rbp), %rax
	movq	%rax, -32(%rbp)
.LBB9_4:                                #   in Loop: Header=BB9_1 Depth=1
	jmp	.LBB9_5
.LBB9_5:                                #   in Loop: Header=BB9_1 Depth=1
	movq	-8(%rbp), %rax
	addq	$1, %rax
	movq	%rax, -8(%rbp)
	jmp	.LBB9_1
.LBB9_6:
	movq	-32(%rbp), %rax
	addq	$48, %rsp
	popq	%rbp
	.cfi_def_cfa %rsp, 8
	retq
.Lfunc_end9:
	.size	argmax, .Lfunc_end9-argmax
	.cfi_endproc
                                        # -- End function
	.prefalign	4, .Lfunc_end10, nop    # -- Begin function mask_scores
	.type	mask_scores,@function
mask_scores:                            # @mask_scores
	.cfi_startproc
# %bb.0:
	pushq	%rbp
	.cfi_def_cfa_offset 16
	.cfi_offset %rbp, -16
	movq	%rsp, %rbp
	.cfi_def_cfa_register %rbp
	subq	$64, %rsp
	movq	%rdi, -64(%rbp)
	movq	%rsi, -56(%rbp)
	movq	$4, -48(%rbp)
	movq	%rdx, -40(%rbp)
	movq	$0, -16(%rbp)
	movq	$0, -8(%rbp)
.LBB10_1:                               # =>This Inner Loop Header: Depth=1
	movq	-8(%rbp), %rax
	cmpq	-48(%rbp), %rax
	jge	.LBB10_9
# %bb.2:                                #   in Loop: Header=BB10_1 Depth=1
	movq	-56(%rbp), %rdi
	movq	-8(%rbp), %rsi
	callq	getv
	movq	%rax, -24(%rbp)
	movq	-64(%rbp), %rdi
	movq	-8(%rbp), %rsi
	callq	getv
	movq	%rax, -32(%rbp)
	movq	-40(%rbp), %rdi
	movq	-8(%rbp), %rsi
	cmpq	$0, -24(%rbp)
	je	.LBB10_4
# %bb.3:                                #   in Loop: Header=BB10_1 Depth=1
	movq	-32(%rbp), %rdx
	jmp	.LBB10_5
.LBB10_4:                               #   in Loop: Header=BB10_1 Depth=1
	movq	$-999999999, %rdx               # imm = 0xC4653601
	jmp	.LBB10_5
.LBB10_5:                               #   in Loop: Header=BB10_1 Depth=1
	callq	setv
	cmpq	$0, -24(%rbp)
	je	.LBB10_7
# %bb.6:                                #   in Loop: Header=BB10_1 Depth=1
	movq	-16(%rbp), %rax
	addq	$1, %rax
	movq	%rax, -16(%rbp)
.LBB10_7:                               #   in Loop: Header=BB10_1 Depth=1
	jmp	.LBB10_8
.LBB10_8:                               #   in Loop: Header=BB10_1 Depth=1
	movq	-8(%rbp), %rax
	addq	$1, %rax
	movq	%rax, -8(%rbp)
	jmp	.LBB10_1
.LBB10_9:
	movq	-16(%rbp), %rax
	addq	$64, %rsp
	popq	%rbp
	.cfi_def_cfa %rsp, 8
	retq
.Lfunc_end10:
	.size	mask_scores, .Lfunc_end10-mask_scores
	.cfi_endproc
                                        # -- End function
	.prefalign	4, .Lfunc_end11, nop    # -- Begin function build_index
	.type	build_index,@function
build_index:                            # @build_index
	.cfi_startproc
# %bb.0:
	pushq	%rbp
	.cfi_def_cfa_offset 16
	.cfi_offset %rbp, -16
	movq	%rsp, %rbp
	.cfi_def_cfa_register %rbp
	pushq	%r14
	pushq	%rbx
	subq	$64, %rsp
	.cfi_offset %rbx, -32
	.cfi_offset %r14, -24
	movq	%rdi, -80(%rbp)
	movq	$4, -72(%rbp)
	movq	$8, -56(%rbp)
	movq	%rsi, -40(%rbp)
	movq	%rdx, -64(%rbp)
	movq	$0, -32(%rbp)
.LBB11_1:                               # =>This Inner Loop Header: Depth=1
	movq	-32(%rbp), %rax
	cmpq	-56(%rbp), %rax
	jge	.LBB11_4
# %bb.2:                                #   in Loop: Header=BB11_1 Depth=1
	movq	-40(%rbp), %rdi
	movq	-32(%rbp), %rsi
	movq	$-1, %rdx
	callq	setv
# %bb.3:                                #   in Loop: Header=BB11_1 Depth=1
	movq	-32(%rbp), %rax
	addq	$1, %rax
	movq	%rax, -32(%rbp)
	jmp	.LBB11_1
.LBB11_4:
	movq	$0, -24(%rbp)
.LBB11_5:                               # =>This Inner Loop Header: Depth=1
	movq	-24(%rbp), %rax
	cmpq	-72(%rbp), %rax
	jge	.LBB11_8
# %bb.6:                                #   in Loop: Header=BB11_5 Depth=1
	movq	-80(%rbp), %rdi
	movq	-24(%rbp), %rsi
	callq	getv
	cqto
	idivq	-56(%rbp)
	movq	%rdx, -48(%rbp)
	movq	-64(%rbp), %rbx
	movq	-24(%rbp), %r14
	movq	-40(%rbp), %rdi
	movq	-48(%rbp), %rsi
	callq	getv
	movq	%rbx, %rdi
	movq	%r14, %rsi
	movq	%rax, %rdx
	callq	setv
	movq	-40(%rbp), %rdi
	movq	-48(%rbp), %rsi
	movq	-24(%rbp), %rdx
	callq	setv
# %bb.7:                                #   in Loop: Header=BB11_5 Depth=1
	movq	-24(%rbp), %rax
	addq	$1, %rax
	movq	%rax, -24(%rbp)
	jmp	.LBB11_5
.LBB11_8:
	addq	$64, %rsp
	popq	%rbx
	popq	%r14
	popq	%rbp
	.cfi_def_cfa %rsp, 8
	retq
.Lfunc_end11:
	.size	build_index, .Lfunc_end11-build_index
	.cfi_endproc
                                        # -- End function
	.prefalign	4, .Lfunc_end12, nop    # -- Begin function index_lookup
	.type	index_lookup,@function
index_lookup:                           # @index_lookup
	.cfi_startproc
# %bb.0:
	pushq	%rbp
	.cfi_def_cfa_offset 16
	.cfi_offset %rbp, -16
	movq	%rsp, %rbp
	.cfi_def_cfa_register %rbp
	subq	$80, %rsp
	movq	%rdi, -72(%rbp)
	movq	%rsi, -80(%rbp)
	movq	%rdx, -64(%rbp)
	movq	$8, -56(%rbp)
	movq	%rcx, -48(%rbp)
	movq	%r8, -24(%rbp)
	movq	%r9, -40(%rbp)
	movq	-24(%rbp), %rax
	cqto
	idivq	-56(%rbp)
	movq	%rdx, -32(%rbp)
	movq	$0, -16(%rbp)
	movq	-64(%rbp), %rdi
	movq	-32(%rbp), %rsi
	callq	getv
	movq	%rax, -8(%rbp)
.LBB12_1:                               # =>This Inner Loop Header: Depth=1
	cmpq	$0, -8(%rbp)
	jl	.LBB12_6
# %bb.2:                                #   in Loop: Header=BB12_1 Depth=1
	movq	-72(%rbp), %rdi
	movq	-8(%rbp), %rsi
	callq	getv
	cmpq	-24(%rbp), %rax
	jne	.LBB12_4
# %bb.3:                                #   in Loop: Header=BB12_1 Depth=1
	movq	-40(%rbp), %rdi
	movq	-16(%rbp), %rsi
	movq	%rsi, %rax
	addq	$1, %rax
	movq	%rax, -16(%rbp)
	movq	-8(%rbp), %rdx
	callq	setv
.LBB12_4:                               #   in Loop: Header=BB12_1 Depth=1
	jmp	.LBB12_5
.LBB12_5:                               #   in Loop: Header=BB12_1 Depth=1
	movq	-48(%rbp), %rdi
	movq	-8(%rbp), %rsi
	callq	getv
	movq	%rax, -8(%rbp)
	jmp	.LBB12_1
.LBB12_6:
	movq	-16(%rbp), %rax
	addq	$80, %rsp
	popq	%rbp
	.cfi_def_cfa %rsp, 8
	retq
.Lfunc_end12:
	.size	index_lookup, .Lfunc_end12-index_lookup
	.cfi_endproc
                                        # -- End function
	.prefalign	4, .Lfunc_end13, nop    # -- Begin function frontier_closure
	.type	frontier_closure,@function
frontier_closure:                       # @frontier_closure
	.cfi_startproc
# %bb.0:
	pushq	%rbp
	.cfi_def_cfa_offset 16
	.cfi_offset %rbp, -16
	movq	%rsp, %rbp
	.cfi_def_cfa_register %rbp
	subq	$192, %rsp
	movq	%fs:40, %rax
	movq	%rax, -8(%rbp)
	movq	%rdi, -192(%rbp)
	movq	$6, -144(%rbp)
	movq	%rsi, -184(%rbp)
	movq	%rdx, -176(%rbp)
	movq	$3, -168(%rbp)
	movq	%rcx, -160(%rbp)
	leaq	-80(%rbp), %rdi
	xorl	%esi, %esi
	movl	$64, %edx
	callq	memset@PLT
	movq	$0, -112(%rbp)
.LBB13_1:                               # =>This Inner Loop Header: Depth=1
	movq	-112(%rbp), %rax
	cmpq	-144(%rbp), %rax
	jge	.LBB13_4
# %bb.2:                                #   in Loop: Header=BB13_1 Depth=1
	movq	-192(%rbp), %rdi
	movq	-112(%rbp), %rsi
	callq	getv
	cmpq	$0, %rax
	setne	%al
	andb	$1, %al
	movzbl	%al, %eax
	movq	-112(%rbp), %rcx
	movb	%al, -80(%rbp,%rcx)
# %bb.3:                                #   in Loop: Header=BB13_1 Depth=1
	movq	-112(%rbp), %rax
	addq	$1, %rax
	movq	%rax, -112(%rbp)
	jmp	.LBB13_1
.LBB13_4:
	movq	$0, -136(%rbp)
	movl	$1, -84(%rbp)
.LBB13_5:                               # =>This Loop Header: Depth=1
                                        #     Child Loop BB13_7 Depth 2
                                        #       Child Loop BB13_11 Depth 3
	cmpl	$0, -84(%rbp)
	je	.LBB13_24
# %bb.6:                                #   in Loop: Header=BB13_5 Depth=1
	movl	$0, -84(%rbp)
	movq	$0, -104(%rbp)
.LBB13_7:                               #   Parent Loop BB13_5 Depth=1
                                        # =>  This Loop Header: Depth=2
                                        #       Child Loop BB13_11 Depth 3
	movq	-104(%rbp), %rax
	cmpq	-168(%rbp), %rax
	jge	.LBB13_23
# %bb.8:                                #   in Loop: Header=BB13_7 Depth=2
	movq	-184(%rbp), %rdi
	movq	-104(%rbp), %rsi
	callq	getv
	movq	%rax, -128(%rbp)
	movq	-128(%rbp), %rax
	cmpb	$0, -80(%rbp,%rax)
	je	.LBB13_10
# %bb.9:                                #   in Loop: Header=BB13_7 Depth=2
	jmp	.LBB13_22
.LBB13_10:                              #   in Loop: Header=BB13_7 Depth=2
	movq	-176(%rbp), %rdi
	movq	-104(%rbp), %rsi
	callq	getv
	movq	%rax, -152(%rbp)
	movl	$1, -116(%rbp)
	movq	$0, -96(%rbp)
.LBB13_11:                              #   Parent Loop BB13_5 Depth=1
                                        #     Parent Loop BB13_7 Depth=2
                                        # =>    This Inner Loop Header: Depth=3
	movq	-96(%rbp), %rax
	cmpq	-144(%rbp), %rax
	jge	.LBB13_18
# %bb.12:                               #   in Loop: Header=BB13_11 Depth=3
	movq	-152(%rbp), %rax
	movq	-96(%rbp), %rcx
                                        # kill: def $cl killed $rcx
	shrq	%cl, %rax
	andq	$1, %rax
	cmpq	$0, %rax
	je	.LBB13_16
# %bb.13:                               #   in Loop: Header=BB13_11 Depth=3
	movq	-96(%rbp), %rax
	cmpb	$0, -80(%rbp,%rax)
	jne	.LBB13_15
# %bb.14:                               #   in Loop: Header=BB13_7 Depth=2
	movl	$0, -116(%rbp)
	jmp	.LBB13_19
.LBB13_15:                              #   in Loop: Header=BB13_11 Depth=3
	jmp	.LBB13_16
.LBB13_16:                              #   in Loop: Header=BB13_11 Depth=3
	jmp	.LBB13_17
.LBB13_17:                              #   in Loop: Header=BB13_11 Depth=3
	movq	-96(%rbp), %rax
	addq	$1, %rax
	movq	%rax, -96(%rbp)
	jmp	.LBB13_11
.LBB13_18:                              # %.loopexit
                                        #   in Loop: Header=BB13_7 Depth=2
	jmp	.LBB13_19
.LBB13_19:                              #   in Loop: Header=BB13_7 Depth=2
	cmpl	$0, -116(%rbp)
	je	.LBB13_21
# %bb.20:                               #   in Loop: Header=BB13_7 Depth=2
	movq	-128(%rbp), %rax
	movb	$1, -80(%rbp,%rax)
	movq	-160(%rbp), %rdi
	movq	-136(%rbp), %rsi
	movq	%rsi, %rax
	addq	$1, %rax
	movq	%rax, -136(%rbp)
	movq	-128(%rbp), %rdx
	callq	setv
	movl	$1, -84(%rbp)
.LBB13_21:                              #   in Loop: Header=BB13_7 Depth=2
	jmp	.LBB13_22
.LBB13_22:                              #   in Loop: Header=BB13_7 Depth=2
	movq	-104(%rbp), %rax
	addq	$1, %rax
	movq	%rax, -104(%rbp)
	jmp	.LBB13_7
.LBB13_23:                              #   in Loop: Header=BB13_5 Depth=1
	jmp	.LBB13_5
.LBB13_24:
	movq	-136(%rbp), %rax
	movq	%fs:40, %rcx
	movq	-8(%rbp), %rdx
	cmpq	%rdx, %rcx
	jne	.LBB13_26
# %bb.25:                               # %SP_return
	addq	$192, %rsp
	popq	%rbp
	.cfi_def_cfa %rsp, 8
	retq
.LBB13_26:                              # %CallStackCheckFailBlk
	.cfi_def_cfa %rbp, 16
	callq	__stack_chk_fail@PLT
.Lfunc_end13:
	.size	frontier_closure, .Lfunc_end13-frontier_closure
	.cfi_endproc
                                        # -- End function
	.prefalign	4, .Lfunc_end14, nop    # -- Begin function frontier_missing
	.type	frontier_missing,@function
frontier_missing:                       # @frontier_missing
	.cfi_startproc
# %bb.0:
	pushq	%rbp
	.cfi_def_cfa_offset 16
	.cfi_offset %rbp, -16
	movq	%rsp, %rbp
	.cfi_def_cfa_register %rbp
	subq	$96, %rsp
	movq	%rdi, -56(%rbp)
	movq	$6, -96(%rbp)
	movq	%rsi, -88(%rbp)
	movq	%rdx, -80(%rbp)
	movq	$3, -72(%rbp)
	movq	%rcx, -48(%rbp)
	movq	$0, -24(%rbp)
	movq	$0, -16(%rbp)
.LBB14_1:                               # =>This Loop Header: Depth=1
                                        #     Child Loop BB14_5 Depth 2
	movq	-16(%rbp), %rax
	cmpq	-72(%rbp), %rax
	jge	.LBB14_16
# %bb.2:                                #   in Loop: Header=BB14_1 Depth=1
	movq	-88(%rbp), %rdi
	movq	-16(%rbp), %rsi
	callq	getv
	movq	%rax, -40(%rbp)
	movq	-56(%rbp), %rdi
	movq	-40(%rbp), %rsi
	callq	getv
	cmpq	$0, %rax
	je	.LBB14_4
# %bb.3:                                #   in Loop: Header=BB14_1 Depth=1
	jmp	.LBB14_15
.LBB14_4:                               #   in Loop: Header=BB14_1 Depth=1
	movq	-80(%rbp), %rdi
	movq	-16(%rbp), %rsi
	callq	getv
	movq	%rax, -64(%rbp)
	movl	$0, -28(%rbp)
	movq	$0, -8(%rbp)
.LBB14_5:                               #   Parent Loop BB14_1 Depth=1
                                        # =>  This Inner Loop Header: Depth=2
	movq	-8(%rbp), %rax
	cmpq	-96(%rbp), %rax
	jge	.LBB14_11
# %bb.6:                                #   in Loop: Header=BB14_5 Depth=2
	movq	-64(%rbp), %rax
	movq	-8(%rbp), %rcx
                                        # kill: def $cl killed $rcx
	shrq	%cl, %rax
	andq	$1, %rax
	cmpq	$0, %rax
	je	.LBB14_9
# %bb.7:                                #   in Loop: Header=BB14_5 Depth=2
	movq	-56(%rbp), %rdi
	movq	-8(%rbp), %rsi
	callq	getv
	cmpq	$0, %rax
	jne	.LBB14_9
# %bb.8:                                #   in Loop: Header=BB14_1 Depth=1
	movq	-48(%rbp), %rdi
	movq	-24(%rbp), %rsi
	movq	%rsi, %rax
	addq	$1, %rax
	movq	%rax, -24(%rbp)
	movq	-8(%rbp), %rdx
	callq	setv
	movl	$1, -28(%rbp)
	jmp	.LBB14_12
.LBB14_9:                               #   in Loop: Header=BB14_5 Depth=2
	jmp	.LBB14_10
.LBB14_10:                              #   in Loop: Header=BB14_5 Depth=2
	movq	-8(%rbp), %rax
	addq	$1, %rax
	movq	%rax, -8(%rbp)
	jmp	.LBB14_5
.LBB14_11:                              # %.loopexit
                                        #   in Loop: Header=BB14_1 Depth=1
	jmp	.LBB14_12
.LBB14_12:                              #   in Loop: Header=BB14_1 Depth=1
	cmpl	$0, -28(%rbp)
	je	.LBB14_14
# %bb.13:                               #   in Loop: Header=BB14_1 Depth=1
	movq	-48(%rbp), %rdi
	movq	-24(%rbp), %rsi
	movq	%rsi, %rax
	addq	$1, %rax
	movq	%rax, -24(%rbp)
	movq	-40(%rbp), %rdx
	callq	setv
.LBB14_14:                              #   in Loop: Header=BB14_1 Depth=1
	jmp	.LBB14_15
.LBB14_15:                              #   in Loop: Header=BB14_1 Depth=1
	movq	-16(%rbp), %rax
	addq	$1, %rax
	movq	%rax, -16(%rbp)
	jmp	.LBB14_1
.LBB14_16:
	movq	-24(%rbp), %rax
	addq	$96, %rsp
	popq	%rbp
	.cfi_def_cfa %rsp, 8
	retq
.Lfunc_end14:
	.size	frontier_missing, .Lfunc_end14-frontier_missing
	.cfi_endproc
                                        # -- End function
	.prefalign	4, .Lfunc_end15, nop    # -- Begin function bfs
	.type	bfs,@function
bfs:                                    # @bfs
	.cfi_startproc
# %bb.0:
	pushq	%rbp
	.cfi_def_cfa_offset 16
	.cfi_offset %rbp, -16
	movq	%rsp, %rbp
	.cfi_def_cfa_register %rbp
	subq	$1120, %rsp                     # imm = 0x460
	movq	%fs:40, %rax
	movq	%rax, -8(%rbp)
	movq	%rdi, -1120(%rbp)
	movq	$4, -1112(%rbp)
	movq	$0, -1088(%rbp)
	movq	%rsi, -1104(%rbp)
	leaq	-528(%rbp), %rdi
	xorl	%esi, %esi
	movl	$512, %edx                      # imm = 0x200
	callq	memset@PLT
	movq	$0, -1072(%rbp)
	movq	$0, -1056(%rbp)
	movq	$0, -1064(%rbp)
	movq	-1088(%rbp), %rax
	movq	$1, -528(%rbp,%rax,8)
	movq	-1088(%rbp), %rax
	movq	-1056(%rbp), %rcx
	movq	%rcx, %rdx
	addq	$1, %rdx
	movq	%rdx, -1056(%rbp)
	movq	%rax, -1040(%rbp,%rcx,8)
.LBB15_1:                               # =>This Loop Header: Depth=1
                                        #     Child Loop BB15_3 Depth 2
	movq	-1072(%rbp), %rax
	cmpq	-1056(%rbp), %rax
	jge	.LBB15_11
# %bb.2:                                #   in Loop: Header=BB15_1 Depth=1
	movq	-1072(%rbp), %rax
	movq	%rax, %rcx
	addq	$1, %rcx
	movq	%rcx, -1072(%rbp)
	movq	-1040(%rbp,%rax,8), %rax
	movq	%rax, -1080(%rbp)
	movq	-1104(%rbp), %rdi
	movq	-1064(%rbp), %rsi
	movq	%rsi, %rax
	addq	$1, %rax
	movq	%rax, -1064(%rbp)
	movq	-1080(%rbp), %rdx
	callq	setv
	movq	-1120(%rbp), %rdi
	movq	-1080(%rbp), %rsi
	callq	getv
	movq	%rax, -1096(%rbp)
	movq	$0, -1048(%rbp)
.LBB15_3:                               #   Parent Loop BB15_1 Depth=1
                                        # =>  This Inner Loop Header: Depth=2
	movq	-1048(%rbp), %rax
	cmpq	-1112(%rbp), %rax
	jge	.LBB15_10
# %bb.4:                                #   in Loop: Header=BB15_3 Depth=2
	movq	-1096(%rbp), %rax
	movq	-1048(%rbp), %rcx
                                        # kill: def $cl killed $rcx
	shrq	%cl, %rax
	andq	$1, %rax
	cmpq	$0, %rax
	je	.LBB15_8
# %bb.5:                                #   in Loop: Header=BB15_3 Depth=2
	movq	-1048(%rbp), %rax
	cmpq	$0, -528(%rbp,%rax,8)
	jne	.LBB15_7
# %bb.6:                                #   in Loop: Header=BB15_3 Depth=2
	movq	-1048(%rbp), %rax
	movq	$1, -528(%rbp,%rax,8)
	movq	-1048(%rbp), %rax
	movq	-1056(%rbp), %rcx
	movq	%rcx, %rdx
	addq	$1, %rdx
	movq	%rdx, -1056(%rbp)
	movq	%rax, -1040(%rbp,%rcx,8)
.LBB15_7:                               #   in Loop: Header=BB15_3 Depth=2
	jmp	.LBB15_8
.LBB15_8:                               #   in Loop: Header=BB15_3 Depth=2
	jmp	.LBB15_9
.LBB15_9:                               #   in Loop: Header=BB15_3 Depth=2
	movq	-1048(%rbp), %rax
	addq	$1, %rax
	movq	%rax, -1048(%rbp)
	jmp	.LBB15_3
.LBB15_10:                              #   in Loop: Header=BB15_1 Depth=1
	jmp	.LBB15_1
.LBB15_11:
	movq	-1064(%rbp), %rax
	movq	%fs:40, %rcx
	movq	-8(%rbp), %rdx
	cmpq	%rdx, %rcx
	jne	.LBB15_13
# %bb.12:                               # %SP_return
	addq	$1120, %rsp                     # imm = 0x460
	popq	%rbp
	.cfi_def_cfa %rsp, 8
	retq
.LBB15_13:                              # %CallStackCheckFailBlk
	.cfi_def_cfa %rbp, 16
	callq	__stack_chk_fail@PLT
.Lfunc_end15:
	.size	bfs, .Lfunc_end15-bfs
	.cfi_endproc
                                        # -- End function
	.prefalign	4, .Lfunc_end16, nop    # -- Begin function topo
	.type	topo,@function
topo:                                   # @topo
	.cfi_startproc
# %bb.0:
	pushq	%rbp
	.cfi_def_cfa_offset 16
	.cfi_offset %rbp, -16
	movq	%rsp, %rbp
	.cfi_def_cfa_register %rbp
	subq	$1152, %rsp                     # imm = 0x480
	movq	%fs:40, %rax
	movq	%rax, -8(%rbp)
	movq	%rdi, -1144(%rbp)
	movq	%rsi, -1120(%rbp)
	movq	$3, -1112(%rbp)
	movq	$4, -1136(%rbp)
	movq	%rdx, -1128(%rbp)
	leaq	-528(%rbp), %rdi
	xorl	%esi, %esi
	movl	$512, %edx                      # imm = 0x200
	callq	memset@PLT
	movq	$0, -1088(%rbp)
	movq	$0, -1064(%rbp)
	movq	$0, -1080(%rbp)
	movq	$0, -1072(%rbp)
.LBB16_1:                               # =>This Inner Loop Header: Depth=1
	movq	-1072(%rbp), %rax
	cmpq	-1112(%rbp), %rax
	jge	.LBB16_4
# %bb.2:                                #   in Loop: Header=BB16_1 Depth=1
	movq	-1120(%rbp), %rdi
	movq	-1072(%rbp), %rsi
	callq	getv
	movq	-528(%rbp,%rax,8), %rcx
	addq	$1, %rcx
	movq	%rcx, -528(%rbp,%rax,8)
# %bb.3:                                #   in Loop: Header=BB16_1 Depth=1
	movq	-1072(%rbp), %rax
	addq	$1, %rax
	movq	%rax, -1072(%rbp)
	jmp	.LBB16_1
.LBB16_4:
	movq	$0, -1056(%rbp)
.LBB16_5:                               # =>This Inner Loop Header: Depth=1
	movq	-1056(%rbp), %rax
	cmpq	-1136(%rbp), %rax
	jge	.LBB16_10
# %bb.6:                                #   in Loop: Header=BB16_5 Depth=1
	movq	-1056(%rbp), %rax
	cmpq	$0, -528(%rbp,%rax,8)
	jne	.LBB16_8
# %bb.7:                                #   in Loop: Header=BB16_5 Depth=1
	movq	-1056(%rbp), %rax
	movq	-1064(%rbp), %rcx
	movq	%rcx, %rdx
	addq	$1, %rdx
	movq	%rdx, -1064(%rbp)
	movq	%rax, -1040(%rbp,%rcx,8)
.LBB16_8:                               #   in Loop: Header=BB16_5 Depth=1
	jmp	.LBB16_9
.LBB16_9:                               #   in Loop: Header=BB16_5 Depth=1
	movq	-1056(%rbp), %rax
	addq	$1, %rax
	movq	%rax, -1056(%rbp)
	jmp	.LBB16_5
.LBB16_10:
	jmp	.LBB16_11
.LBB16_11:                              # =>This Loop Header: Depth=1
                                        #     Child Loop BB16_13 Depth 2
	movq	-1088(%rbp), %rax
	cmpq	-1064(%rbp), %rax
	jge	.LBB16_21
# %bb.12:                               #   in Loop: Header=BB16_11 Depth=1
	movq	-1088(%rbp), %rax
	movq	%rax, %rcx
	addq	$1, %rcx
	movq	%rcx, -1088(%rbp)
	movq	-1040(%rbp,%rax,8), %rax
	movq	%rax, -1104(%rbp)
	movq	-1128(%rbp), %rdi
	movq	-1080(%rbp), %rsi
	movq	%rsi, %rax
	addq	$1, %rax
	movq	%rax, -1080(%rbp)
	movq	-1104(%rbp), %rdx
	callq	setv
	movq	$0, -1048(%rbp)
.LBB16_13:                              #   Parent Loop BB16_11 Depth=1
                                        # =>  This Inner Loop Header: Depth=2
	movq	-1048(%rbp), %rax
	cmpq	-1112(%rbp), %rax
	jge	.LBB16_20
# %bb.14:                               #   in Loop: Header=BB16_13 Depth=2
	movq	-1144(%rbp), %rdi
	movq	-1048(%rbp), %rsi
	callq	getv
	cmpq	-1104(%rbp), %rax
	jne	.LBB16_18
# %bb.15:                               #   in Loop: Header=BB16_13 Depth=2
	movq	-1120(%rbp), %rdi
	movq	-1048(%rbp), %rsi
	callq	getv
	movq	%rax, -1096(%rbp)
	movq	-1096(%rbp), %rax
	movq	-528(%rbp,%rax,8), %rcx
	addq	$-1, %rcx
	movq	%rcx, -528(%rbp,%rax,8)
	cmpq	$0, %rcx
	jne	.LBB16_17
# %bb.16:                               #   in Loop: Header=BB16_13 Depth=2
	movq	-1096(%rbp), %rax
	movq	-1064(%rbp), %rcx
	movq	%rcx, %rdx
	addq	$1, %rdx
	movq	%rdx, -1064(%rbp)
	movq	%rax, -1040(%rbp,%rcx,8)
.LBB16_17:                              #   in Loop: Header=BB16_13 Depth=2
	jmp	.LBB16_18
.LBB16_18:                              #   in Loop: Header=BB16_13 Depth=2
	jmp	.LBB16_19
.LBB16_19:                              #   in Loop: Header=BB16_13 Depth=2
	movq	-1048(%rbp), %rax
	addq	$1, %rax
	movq	%rax, -1048(%rbp)
	jmp	.LBB16_13
.LBB16_20:                              #   in Loop: Header=BB16_11 Depth=1
	jmp	.LBB16_11
.LBB16_21:
	movq	-1080(%rbp), %rax
	movq	%fs:40, %rcx
	movq	-8(%rbp), %rdx
	cmpq	%rdx, %rcx
	jne	.LBB16_23
# %bb.22:                               # %SP_return
	addq	$1152, %rsp                     # imm = 0x480
	popq	%rbp
	.cfi_def_cfa %rsp, 8
	retq
.LBB16_23:                              # %CallStackCheckFailBlk
	.cfi_def_cfa %rbp, 16
	callq	__stack_chk_fail@PLT
.Lfunc_end16:
	.size	topo, .Lfunc_end16-topo
	.cfi_endproc
                                        # -- End function
	.prefalign	4, .Lfunc_end17, nop    # -- Begin function uf_union
	.type	uf_union,@function
uf_union:                               # @uf_union
	.cfi_startproc
# %bb.0:
	pushq	%rbp
	.cfi_def_cfa_offset 16
	.cfi_offset %rbp, -16
	movq	%rsp, %rbp
	.cfi_def_cfa_register %rbp
	subq	$32, %rsp
	movq	%rdi, -24(%rbp)
	movq	%rsi, -16(%rbp)
	movq	%rdx, -8(%rbp)
	movq	-24(%rbp), %rdi
	movq	-16(%rbp), %rsi
	callq	uf_find
	movq	%rax, -16(%rbp)
	movq	-24(%rbp), %rdi
	movq	-8(%rbp), %rsi
	callq	uf_find
	movq	%rax, -8(%rbp)
	movq	-16(%rbp), %rax
	cmpq	-8(%rbp), %rax
	jne	.LBB17_2
# %bb.1:
	movq	$0, -32(%rbp)
	jmp	.LBB17_3
.LBB17_2:
	movq	-16(%rbp), %rax
	movq	-24(%rbp), %rcx
	movq	-8(%rbp), %rdx
	movq	%rax, (%rcx,%rdx,8)
	movq	$1, -32(%rbp)
.LBB17_3:
	movq	-32(%rbp), %rax
	addq	$32, %rsp
	popq	%rbp
	.cfi_def_cfa %rsp, 8
	retq
.Lfunc_end17:
	.size	uf_union, .Lfunc_end17-uf_union
	.cfi_endproc
                                        # -- End function
	.prefalign	4, .Lfunc_end18, nop    # -- Begin function uf_find
	.type	uf_find,@function
uf_find:                                # @uf_find
	.cfi_startproc
# %bb.0:
	pushq	%rbp
	.cfi_def_cfa_offset 16
	.cfi_offset %rbp, -16
	movq	%rsp, %rbp
	.cfi_def_cfa_register %rbp
	movq	%rdi, -16(%rbp)
	movq	%rsi, -8(%rbp)
.LBB18_1:                               # =>This Inner Loop Header: Depth=1
	movq	-16(%rbp), %rax
	movq	-8(%rbp), %rcx
	movq	(%rax,%rcx,8), %rax
	cmpq	-8(%rbp), %rax
	je	.LBB18_3
# %bb.2:                                #   in Loop: Header=BB18_1 Depth=1
	movq	-16(%rbp), %rax
	movq	-16(%rbp), %rcx
	movq	-8(%rbp), %rdx
	movq	(%rcx,%rdx,8), %rcx
	movq	(%rax,%rcx,8), %rax
	movq	-16(%rbp), %rcx
	movq	-8(%rbp), %rdx
	movq	%rax, (%rcx,%rdx,8)
	movq	-16(%rbp), %rax
	movq	-8(%rbp), %rcx
	movq	(%rax,%rcx,8), %rax
	movq	%rax, -8(%rbp)
	jmp	.LBB18_1
.LBB18_3:
	movq	-8(%rbp), %rax
	popq	%rbp
	.cfi_def_cfa %rsp, 8
	retq
.Lfunc_end18:
	.size	uf_find, .Lfunc_end18-uf_find
	.cfi_endproc
                                        # -- End function
	.prefalign	4, .Lfunc_end19, nop    # -- Begin function bitset_closure
	.type	bitset_closure,@function
bitset_closure:                         # @bitset_closure
	.cfi_startproc
# %bb.0:
	pushq	%rbp
	.cfi_def_cfa_offset 16
	.cfi_offset %rbp, -16
	movq	%rsp, %rbp
	.cfi_def_cfa_register %rbp
	subq	$592, %rsp                      # imm = 0x250
	movq	%fs:40, %rax
	movq	%rax, -8(%rbp)
	movq	%rdi, -584(%rbp)
	movq	$4, -568(%rbp)
	movq	%rsi, -576(%rbp)
	movq	$0, -560(%rbp)
.LBB19_1:                               # =>This Inner Loop Header: Depth=1
	movq	-560(%rbp), %rax
	cmpq	-568(%rbp), %rax
	jge	.LBB19_4
# %bb.2:                                #   in Loop: Header=BB19_1 Depth=1
	movq	-584(%rbp), %rdi
	movq	-560(%rbp), %rsi
	callq	getv
	movq	-560(%rbp), %rcx
	movq	%rax, -528(%rbp,%rcx,8)
# %bb.3:                                #   in Loop: Header=BB19_1 Depth=1
	movq	-560(%rbp), %rax
	addq	$1, %rax
	movq	%rax, -560(%rbp)
	jmp	.LBB19_1
.LBB19_4:
	movq	$0, -552(%rbp)
.LBB19_5:                               # =>This Loop Header: Depth=1
                                        #     Child Loop BB19_7 Depth 2
	movq	-552(%rbp), %rax
	cmpq	-568(%rbp), %rax
	jge	.LBB19_14
# %bb.6:                                #   in Loop: Header=BB19_5 Depth=1
	movq	$0, -544(%rbp)
.LBB19_7:                               #   Parent Loop BB19_5 Depth=1
                                        # =>  This Inner Loop Header: Depth=2
	movq	-544(%rbp), %rax
	cmpq	-568(%rbp), %rax
	jge	.LBB19_12
# %bb.8:                                #   in Loop: Header=BB19_7 Depth=2
	movq	-544(%rbp), %rax
	movq	-528(%rbp,%rax,8), %rax
	movq	-552(%rbp), %rcx
                                        # kill: def $cl killed $rcx
	shrq	%cl, %rax
	andq	$1, %rax
	cmpq	$0, %rax
	je	.LBB19_10
# %bb.9:                                #   in Loop: Header=BB19_7 Depth=2
	movq	-552(%rbp), %rax
	movq	-528(%rbp,%rax,8), %rax
	movq	-544(%rbp), %rcx
	orq	-528(%rbp,%rcx,8), %rax
	movq	%rax, -528(%rbp,%rcx,8)
.LBB19_10:                              #   in Loop: Header=BB19_7 Depth=2
	jmp	.LBB19_11
.LBB19_11:                              #   in Loop: Header=BB19_7 Depth=2
	movq	-544(%rbp), %rax
	addq	$1, %rax
	movq	%rax, -544(%rbp)
	jmp	.LBB19_7
.LBB19_12:                              #   in Loop: Header=BB19_5 Depth=1
	jmp	.LBB19_13
.LBB19_13:                              #   in Loop: Header=BB19_5 Depth=1
	movq	-552(%rbp), %rax
	addq	$1, %rax
	movq	%rax, -552(%rbp)
	jmp	.LBB19_5
.LBB19_14:
	movq	$0, -536(%rbp)
.LBB19_15:                              # =>This Inner Loop Header: Depth=1
	movq	-536(%rbp), %rax
	cmpq	-568(%rbp), %rax
	jge	.LBB19_18
# %bb.16:                               #   in Loop: Header=BB19_15 Depth=1
	movq	-576(%rbp), %rdi
	movq	-536(%rbp), %rsi
	movq	-536(%rbp), %rax
	movq	-528(%rbp,%rax,8), %rdx
	callq	setv
# %bb.17:                               #   in Loop: Header=BB19_15 Depth=1
	movq	-536(%rbp), %rax
	addq	$1, %rax
	movq	%rax, -536(%rbp)
	jmp	.LBB19_15
.LBB19_18:
	movq	%fs:40, %rax
	movq	-8(%rbp), %rcx
	cmpq	%rcx, %rax
	jne	.LBB19_20
# %bb.19:                               # %SP_return
	addq	$592, %rsp                      # imm = 0x250
	popq	%rbp
	.cfi_def_cfa %rsp, 8
	retq
.LBB19_20:                              # %CallStackCheckFailBlk
	.cfi_def_cfa %rbp, 16
	callq	__stack_chk_fail@PLT
.Lfunc_end19:
	.size	bitset_closure, .Lfunc_end19-bitset_closure
	.cfi_endproc
                                        # -- End function
	.prefalign	4, .Lfunc_end20, nop    # -- Begin function index_add
	.type	index_add,@function
index_add:                              # @index_add
	.cfi_startproc
# %bb.0:
	pushq	%rbp
	.cfi_def_cfa_offset 16
	.cfi_offset %rbp, -16
	movq	%rsp, %rbp
	.cfi_def_cfa_register %rbp
	pushq	%r14
	pushq	%rbx
	subq	$64, %rsp
	.cfi_offset %rbx, -32
	.cfi_offset %r14, -24
	movq	%rdi, -72(%rbp)
	movq	%rsi, -48(%rbp)
	movq	$8, -64(%rbp)
	movq	%rdx, -56(%rbp)
	movq	$4, -24(%rbp)
	movq	$3, -40(%rbp)
	movq	-40(%rbp), %rax
	cqto
	idivq	-64(%rbp)
	movq	%rdx, -32(%rbp)
	movq	-72(%rbp), %rdi
	movq	-24(%rbp), %rsi
	movq	-40(%rbp), %rdx
	callq	setv
	movq	-56(%rbp), %rbx
	movq	-24(%rbp), %r14
	movq	-48(%rbp), %rdi
	movq	-32(%rbp), %rsi
	callq	getv
	movq	%rbx, %rdi
	movq	%r14, %rsi
	movq	%rax, %rdx
	callq	setv
	movq	-48(%rbp), %rdi
	movq	-32(%rbp), %rsi
	movq	-24(%rbp), %rdx
	callq	setv
	addq	$64, %rsp
	popq	%rbx
	popq	%r14
	popq	%rbp
	.cfi_def_cfa %rsp, 8
	retq
.Lfunc_end20:
	.size	index_add, .Lfunc_end20-index_add
	.cfi_endproc
                                        # -- End function
	.prefalign	4, .Lfunc_end21, nop    # -- Begin function index_remove
	.type	index_remove,@function
index_remove:                           # @index_remove
	.cfi_startproc
# %bb.0:
	pushq	%rbp
	.cfi_def_cfa_offset 16
	.cfi_offset %rbp, -16
	movq	%rsp, %rbp
	.cfi_def_cfa_register %rbp
	subq	$32, %rsp
	movq	%rdi, -16(%rbp)
	movq	$0, -8(%rbp)
	movq	-16(%rbp), %rdi
	movq	-8(%rbp), %rsi
	callq	getv
	movq	%rax, -24(%rbp)
	movq	-16(%rbp), %rdi
	movq	-8(%rbp), %rsi
	movq	$-1, %rdx
	callq	setv
	movq	-24(%rbp), %rax
	addq	$32, %rsp
	popq	%rbp
	.cfi_def_cfa %rsp, 8
	retq
.Lfunc_end21:
	.size	index_remove, .Lfunc_end21-index_remove
	.cfi_endproc
                                        # -- End function
	.section	.rodata.cst8,"aM",@progbits,8
	.p2align	3, 0x0                          # -- Begin function bce_q16
.LCPI22_0:
	.quad	0x40f0000000000000              # double 65536
.LCPI22_1:
	.quad	0x3ff0000000000000              # double 1
	.text
	.prefalign	4, .Lfunc_end22, nop
	.type	bce_q16,@function
bce_q16:                                # @bce_q16
	.cfi_startproc
# %bb.0:
	pushq	%rbp
	.cfi_def_cfa_offset 16
	.cfi_offset %rbp, -16
	movq	%rsp, %rbp
	.cfi_def_cfa_register %rbp
	subq	$64, %rsp
	movq	$0, -64(%rbp)
	movq	%rdi, -56(%rbp)
	cvtsi2sdq	-64(%rbp), %xmm0
	movsd	.LCPI22_0(%rip), %xmm1          # xmm1 = [6.5536E+4,0.0E+0]
	divsd	%xmm1, %xmm0
	movsd	%xmm0, -16(%rbp)
	cvtsi2sdq	-56(%rbp), %xmm0
	movsd	.LCPI22_0(%rip), %xmm1          # xmm1 = [6.5536E+4,0.0E+0]
	divsd	%xmm1, %xmm0
	movsd	%xmm0, -8(%rbp)
	movsd	-8(%rbp), %xmm0                 # xmm0 = mem[0],zero
	movsd	%xmm0, -40(%rbp)                # 8-byte Spill
	movsd	-16(%rbp), %xmm0                # xmm0 = mem[0],zero
	movq	%xmm0, %rax
	movabsq	$-9223372036854775808, %rcx     # imm = 0x8000000000000000
	xorq	%rcx, %rax
	movq	%rax, %xmm0
	callq	exp@PLT
	movsd	.LCPI22_1(%rip), %xmm1          # xmm1 = [1.0E+0,0.0E+0]
	addsd	%xmm0, %xmm1
	movsd	.LCPI22_1(%rip), %xmm0          # xmm0 = [1.0E+0,0.0E+0]
	divsd	%xmm1, %xmm0
	callq	log@PLT
	movsd	%xmm0, -32(%rbp)                # 8-byte Spill
	movsd	.LCPI22_1(%rip), %xmm0          # xmm0 = [1.0E+0,0.0E+0]
	subsd	-8(%rbp), %xmm0
	movsd	%xmm0, -24(%rbp)                # 8-byte Spill
	movsd	-16(%rbp), %xmm0                # xmm0 = mem[0],zero
	movq	%xmm0, %rax
	movabsq	$-9223372036854775808, %rcx     # imm = 0x8000000000000000
	xorq	%rcx, %rax
	movq	%rax, %xmm0
	callq	exp@PLT
	movsd	.LCPI22_1(%rip), %xmm1          # xmm1 = [1.0E+0,0.0E+0]
	addsd	%xmm0, %xmm1
	movsd	.LCPI22_1(%rip), %xmm2          # xmm2 = [1.0E+0,0.0E+0]
	divsd	%xmm1, %xmm2
	movsd	.LCPI22_1(%rip), %xmm0          # xmm0 = [1.0E+0,0.0E+0]
	subsd	%xmm2, %xmm0
	callq	log@PLT
	movsd	-24(%rbp), %xmm1                # 8-byte Reload
                                        # xmm1 = mem[0],zero
	mulsd	%xmm0, %xmm1
	movsd	-40(%rbp), %xmm0                # 8-byte Reload
                                        # xmm0 = mem[0],zero
	mulsd	-32(%rbp), %xmm0                # 8-byte Folded Reload
	addsd	%xmm1, %xmm0
	movq	%xmm0, %rax
	movabsq	$-9223372036854775808, %rcx     # imm = 0x8000000000000000
	xorq	%rcx, %rax
	movq	%rax, %xmm0
	movsd	%xmm0, -48(%rbp)
	movsd	.LCPI22_0(%rip), %xmm0          # xmm0 = [6.5536E+4,0.0E+0]
	mulsd	-48(%rbp), %xmm0
	cvttsd2si	%xmm0, %rax
	addq	$64, %rsp
	popq	%rbp
	.cfi_def_cfa %rsp, 8
	retq
.Lfunc_end22:
	.size	bce_q16, .Lfunc_end22-bce_q16
	.cfi_endproc
                                        # -- End function
	.prefalign	4, .Lfunc_end23, nop    # -- Begin function backward_matvec
	.type	backward_matvec,@function
backward_matvec:                        # @backward_matvec
	.cfi_startproc
# %bb.0:
	pushq	%rbp
	.cfi_def_cfa_offset 16
	.cfi_offset %rbp, -16
	movq	%rsp, %rbp
	.cfi_def_cfa_register %rbp
	pushq	%rbx
	subq	$72, %rsp
	.cfi_offset %rbx, -24
	movq	%rdi, -72(%rbp)
	movq	$2, -64(%rbp)
	movq	$2, -40(%rbp)
	movq	%rsi, -56(%rbp)
	movq	%rdx, -48(%rbp)
	movq	$0, -24(%rbp)
.LBB23_1:                               # =>This Loop Header: Depth=1
                                        #     Child Loop BB23_3 Depth 2
	movq	-24(%rbp), %rax
	cmpq	-40(%rbp), %rax
	jge	.LBB23_8
# %bb.2:                                #   in Loop: Header=BB23_1 Depth=1
	movq	$0, -32(%rbp)
	movq	$0, -16(%rbp)
.LBB23_3:                               #   Parent Loop BB23_1 Depth=1
                                        # =>  This Inner Loop Header: Depth=2
	movq	-16(%rbp), %rax
	cmpq	-64(%rbp), %rax
	jge	.LBB23_6
# %bb.4:                                #   in Loop: Header=BB23_3 Depth=2
	movq	-72(%rbp), %rdi
	movq	-16(%rbp), %rsi
	imulq	-40(%rbp), %rsi
	addq	-24(%rbp), %rsi
	callq	getv
	movq	%rax, %rbx
	movq	-56(%rbp), %rdi
	movq	-16(%rbp), %rsi
	callq	getv
	movq	%rbx, %rdi
	movq	%rax, %rsi
	callq	qmul
	addq	-32(%rbp), %rax
	movq	%rax, -32(%rbp)
# %bb.5:                                #   in Loop: Header=BB23_3 Depth=2
	movq	-16(%rbp), %rax
	addq	$1, %rax
	movq	%rax, -16(%rbp)
	jmp	.LBB23_3
.LBB23_6:                               #   in Loop: Header=BB23_1 Depth=1
	movq	-48(%rbp), %rdi
	movq	-24(%rbp), %rsi
	movq	-32(%rbp), %rdx
	callq	setv
# %bb.7:                                #   in Loop: Header=BB23_1 Depth=1
	movq	-24(%rbp), %rax
	addq	$1, %rax
	movq	%rax, -24(%rbp)
	jmp	.LBB23_1
.LBB23_8:
	addq	$72, %rsp
	popq	%rbx
	popq	%rbp
	.cfi_def_cfa %rsp, 8
	retq
.Lfunc_end23:
	.size	backward_matvec, .Lfunc_end23-backward_matvec
	.cfi_endproc
                                        # -- End function
	.section	.rodata.cst8,"aM",@progbits,8
	.p2align	3, 0x0                          # -- Begin function adam_step
.LCPI24_0:
	.quad	0x40f0000000000000              # double 65536
.LCPI24_1:
	.quad	0x3ff0000000000000              # double 1
	.text
	.prefalign	4, .Lfunc_end24, nop
	.type	adam_step,@function
adam_step:                              # @adam_step
	.cfi_startproc
# %bb.0:
	pushq	%rbp
	.cfi_def_cfa_offset 16
	.cfi_offset %rbp, -16
	movq	%rsp, %rbp
	.cfi_def_cfa_register %rbp
	subq	$176, %rsp
	movq	%rdi, -176(%rbp)
	movq	$655360, -168(%rbp)             # imm = 0xA0000
	movq	%rsi, -64(%rbp)
	movq	%rdx, -56(%rbp)
	movq	%rcx, -48(%rbp)
	movq	$3277, -160(%rbp)               # imm = 0xCCD
	movq	$58982, -152(%rbp)              # imm = 0xE666
	movq	$64225, -144(%rbp)              # imm = 0xFAE1
	movq	$655, -136(%rbp)                # imm = 0x28F
	cvtsi2sdq	-152(%rbp), %xmm0
	movsd	.LCPI24_0(%rip), %xmm1          # xmm1 = [6.5536E+4,0.0E+0]
	divsd	%xmm1, %xmm0
	movsd	%xmm0, -40(%rbp)
	cvtsi2sdq	-144(%rbp), %xmm0
	movsd	.LCPI24_0(%rip), %xmm1          # xmm1 = [6.5536E+4,0.0E+0]
	divsd	%xmm1, %xmm0
	movsd	%xmm0, -32(%rbp)
	movq	-64(%rbp), %rax
	cvtsi2sdq	(%rax), %xmm0
	movsd	.LCPI24_0(%rip), %xmm1          # xmm1 = [6.5536E+4,0.0E+0]
	divsd	%xmm1, %xmm0
	movsd	%xmm0, -16(%rbp)
	movq	-56(%rbp), %rax
	cvtsi2sdq	(%rax), %xmm0
	movsd	.LCPI24_0(%rip), %xmm1          # xmm1 = [6.5536E+4,0.0E+0]
	divsd	%xmm1, %xmm0
	movsd	%xmm0, -8(%rbp)
	cvtsi2sdq	-168(%rbp), %xmm0
	movsd	.LCPI24_0(%rip), %xmm1          # xmm1 = [6.5536E+4,0.0E+0]
	divsd	%xmm1, %xmm0
	movsd	%xmm0, -24(%rbp)
	cvtsi2sdq	-160(%rbp), %xmm0
	movsd	.LCPI24_0(%rip), %xmm1          # xmm1 = [6.5536E+4,0.0E+0]
	divsd	%xmm1, %xmm0
	movsd	%xmm0, -128(%rbp)
	movsd	-40(%rbp), %xmm0                # xmm0 = mem[0],zero
	movsd	-16(%rbp), %xmm1                # xmm1 = mem[0],zero
	movsd	.LCPI24_1(%rip), %xmm2          # xmm2 = [1.0E+0,0.0E+0]
	subsd	-40(%rbp), %xmm2
	mulsd	-24(%rbp), %xmm2
	mulsd	%xmm1, %xmm0
	addsd	%xmm2, %xmm0
	movsd	%xmm0, -16(%rbp)
	movsd	-32(%rbp), %xmm0                # xmm0 = mem[0],zero
	movsd	-8(%rbp), %xmm1                 # xmm1 = mem[0],zero
	movsd	.LCPI24_1(%rip), %xmm2          # xmm2 = [1.0E+0,0.0E+0]
	subsd	-32(%rbp), %xmm2
	mulsd	-24(%rbp), %xmm2
	mulsd	-24(%rbp), %xmm2
	mulsd	%xmm1, %xmm0
	addsd	%xmm2, %xmm0
	movsd	%xmm0, -8(%rbp)
	movsd	-16(%rbp), %xmm0                # xmm0 = mem[0],zero
	movsd	%xmm0, -72(%rbp)                # 8-byte Spill
	movsd	-40(%rbp), %xmm0                # xmm0 = mem[0],zero
	cvtsi2sdq	-48(%rbp), %xmm1
	callq	pow@PLT
	movsd	.LCPI24_1(%rip), %xmm1          # xmm1 = [1.0E+0,0.0E+0]
	subsd	%xmm0, %xmm1
	movsd	-72(%rbp), %xmm0                # 8-byte Reload
                                        # xmm0 = mem[0],zero
	divsd	%xmm1, %xmm0
	movsd	%xmm0, -120(%rbp)
	movsd	-8(%rbp), %xmm0                 # xmm0 = mem[0],zero
	movsd	%xmm0, -80(%rbp)                # 8-byte Spill
	movsd	-32(%rbp), %xmm0                # xmm0 = mem[0],zero
	cvtsi2sdq	-48(%rbp), %xmm1
	callq	pow@PLT
	movsd	.LCPI24_1(%rip), %xmm1          # xmm1 = [1.0E+0,0.0E+0]
	subsd	%xmm0, %xmm1
	movsd	-80(%rbp), %xmm0                # 8-byte Reload
                                        # xmm0 = mem[0],zero
	divsd	%xmm1, %xmm0
	movsd	%xmm0, -112(%rbp)
	cvtsi2sdq	-176(%rbp), %xmm1
	movsd	.LCPI24_0(%rip), %xmm0          # xmm0 = [6.5536E+4,0.0E+0]
	divsd	%xmm0, %xmm1
	movsd	%xmm1, -96(%rbp)                # 8-byte Spill
	movsd	-128(%rbp), %xmm0               # xmm0 = mem[0],zero
	mulsd	-120(%rbp), %xmm0
	movsd	%xmm0, -88(%rbp)                # 8-byte Spill
	movsd	-112(%rbp), %xmm0               # xmm0 = mem[0],zero
	callq	sqrt@PLT
	cvtsi2sdq	-136(%rbp), %xmm1
	movsd	.LCPI24_0(%rip), %xmm2          # xmm2 = [6.5536E+4,0.0E+0]
	divsd	%xmm2, %xmm1
	addsd	%xmm1, %xmm0
	movsd	-88(%rbp), %xmm1                # 8-byte Reload
                                        # xmm1 = mem[0],zero
	divsd	%xmm0, %xmm1
	movsd	-96(%rbp), %xmm0                # 8-byte Reload
                                        # xmm0 = mem[0],zero
	subsd	%xmm1, %xmm0
	movsd	%xmm0, -104(%rbp)
	movsd	.LCPI24_0(%rip), %xmm0          # xmm0 = [6.5536E+4,0.0E+0]
	mulsd	-16(%rbp), %xmm0
	cvttsd2si	%xmm0, %rax
	movq	-64(%rbp), %rcx
	movq	%rax, (%rcx)
	movsd	.LCPI24_0(%rip), %xmm0          # xmm0 = [6.5536E+4,0.0E+0]
	mulsd	-8(%rbp), %xmm0
	cvttsd2si	%xmm0, %rax
	movq	-56(%rbp), %rcx
	movq	%rax, (%rcx)
	movsd	.LCPI24_0(%rip), %xmm0          # xmm0 = [6.5536E+4,0.0E+0]
	mulsd	-104(%rbp), %xmm0
	cvttsd2si	%xmm0, %rax
	addq	$176, %rsp
	popq	%rbp
	.cfi_def_cfa %rsp, 8
	retq
.Lfunc_end24:
	.size	adam_step, .Lfunc_end24-adam_step
	.cfi_endproc
                                        # -- End function
	.prefalign	4, .Lfunc_end25, nop    # -- Begin function fused_linear_relu
	.type	fused_linear_relu,@function
fused_linear_relu:                      # @fused_linear_relu
	.cfi_startproc
# %bb.0:
	pushq	%rbp
	.cfi_def_cfa_offset 16
	.cfi_offset %rbp, -16
	movq	%rsp, %rbp
	.cfi_def_cfa_register %rbp
	subq	$592, %rsp                      # imm = 0x250
	movq	%fs:40, %rax
	movq	%rax, -8(%rbp)
	movq	%rdi, -584(%rbp)
	movq	%rsi, -576(%rbp)
	movq	$2, -544(%rbp)
	movq	$2, -568(%rbp)
	movq	%rdx, -560(%rbp)
	movq	%rcx, -552(%rbp)
	movq	-584(%rbp), %rdi
	movq	-544(%rbp), %rsi
	movq	-568(%rbp), %rdx
	movq	-560(%rbp), %rcx
	movq	-576(%rbp), %r8
	leaq	-528(%rbp), %r9
	callq	matvec
	movq	$0, -536(%rbp)
.LBB25_1:                               # =>This Inner Loop Header: Depth=1
	movq	-536(%rbp), %rax
	cmpq	-544(%rbp), %rax
	jge	.LBB25_7
# %bb.2:                                #   in Loop: Header=BB25_1 Depth=1
	movq	-552(%rbp), %rdi
	movq	-536(%rbp), %rsi
	movq	-536(%rbp), %rax
	cmpq	$0, -528(%rbp,%rax,8)
	jle	.LBB25_4
# %bb.3:                                #   in Loop: Header=BB25_1 Depth=1
	movq	-536(%rbp), %rax
	movq	-528(%rbp,%rax,8), %rdx
	jmp	.LBB25_5
.LBB25_4:                               #   in Loop: Header=BB25_1 Depth=1
	xorl	%edx, %edx
	jmp	.LBB25_5
.LBB25_5:                               #   in Loop: Header=BB25_1 Depth=1
	callq	setv
# %bb.6:                                #   in Loop: Header=BB25_1 Depth=1
	movq	-536(%rbp), %rax
	addq	$1, %rax
	movq	%rax, -536(%rbp)
	jmp	.LBB25_1
.LBB25_7:
	movq	%fs:40, %rax
	movq	-8(%rbp), %rcx
	cmpq	%rcx, %rax
	jne	.LBB25_9
# %bb.8:                                # %SP_return
	addq	$592, %rsp                      # imm = 0x250
	popq	%rbp
	.cfi_def_cfa %rsp, 8
	retq
.LBB25_9:                               # %CallStackCheckFailBlk
	.cfi_def_cfa %rbp, 16
	callq	__stack_chk_fail@PLT
.Lfunc_end25:
	.size	fused_linear_relu, .Lfunc_end25-fused_linear_relu
	.cfi_endproc
                                        # -- End function
	.prefalign	4, .Lfunc_end26, nop    # -- Begin function fused_linear_ln
	.type	fused_linear_ln,@function
fused_linear_ln:                        # @fused_linear_ln
	.cfi_startproc
# %bb.0:
	pushq	%rbp
	.cfi_def_cfa_offset 16
	.cfi_offset %rbp, -16
	movq	%rsp, %rbp
	.cfi_def_cfa_register %rbp
	pushq	%rbx
	subq	$616, %rsp                      # imm = 0x268
	.cfi_offset %rbx, -24
	movq	%fs:40, %rax
	movq	%rax, -16(%rbp)
	movq	%rdi, -624(%rbp)
	movq	%rsi, -616(%rbp)
	movq	$3, -568(%rbp)
	movq	$3, -608(%rbp)
	movq	%rdx, -600(%rbp)
	movq	%rcx, -592(%rbp)
	movq	%r8, -584(%rbp)
	movq	%r9, -576(%rbp)
	movq	-624(%rbp), %rdi
	movq	-568(%rbp), %rsi
	movq	-608(%rbp), %rdx
	movq	-600(%rbp), %rcx
	movq	-616(%rbp), %r8
	leaq	-528(%rbp), %rbx
	movq	%rbx, %r9
	callq	matvec
	movq	%rbx, -560(%rbp)
	movq	-568(%rbp), %rax
	movq	%rax, -552(%rbp)
	movq	$8, -544(%rbp)
	movq	$8, -536(%rbp)
	movq	-568(%rbp), %rsi
	movq	-592(%rbp), %rdx
	movq	-584(%rbp), %rcx
	movq	-576(%rbp), %r8
	leaq	-560(%rbp), %rdi
	callq	layernorm
	movq	%fs:40, %rax
	movq	-16(%rbp), %rcx
	cmpq	%rcx, %rax
	jne	.LBB26_2
# %bb.1:                                # %SP_return
	addq	$616, %rsp                      # imm = 0x268
	popq	%rbx
	popq	%rbp
	.cfi_def_cfa %rsp, 8
	retq
.LBB26_2:                               # %CallStackCheckFailBlk
	.cfi_def_cfa %rbp, 16
	callq	__stack_chk_fail@PLT
.Lfunc_end26:
	.size	fused_linear_ln, .Lfunc_end26-fused_linear_ln
	.cfi_endproc
                                        # -- End function
	.prefalign	4, .Lfunc_end27, nop    # -- Begin function integrated_derive
	.type	integrated_derive,@function
integrated_derive:                      # @integrated_derive
	.cfi_startproc
# %bb.0:
	pushq	%rbp
	.cfi_def_cfa_offset 16
	.cfi_offset %rbp, -16
	movq	%rsp, %rbp
	.cfi_def_cfa_register %rbp
	subq	$2416, %rsp                     # imm = 0x970
	movq	%fs:40, %rax
	movq	%rax, -8(%rbp)
	movq	%rdi, -2408(%rbp)
	movq	$6, -2352(%rbp)
	movq	%rsi, -2344(%rbp)
	movq	%rdx, -2400(%rbp)
	movq	%rcx, -2392(%rbp)
	movq	$3, -2264(%rbp)
	movq	%r8, -2384(%rbp)
	leaq	-80(%rbp), %rdi
	xorl	%esi, %esi
	movl	$64, %edx
	callq	memset@PLT
	movq	$0, -2312(%rbp)
.LBB27_1:                               # =>This Inner Loop Header: Depth=1
	movq	-2312(%rbp), %rax
	cmpq	-2352(%rbp), %rax
	jge	.LBB27_4
# %bb.2:                                #   in Loop: Header=BB27_1 Depth=1
	movq	-2408(%rbp), %rdi
	movq	-2312(%rbp), %rsi
	callq	getv
	cmpq	$0, %rax
	setne	%al
	andb	$1, %al
	movzbl	%al, %eax
	movq	-2312(%rbp), %rcx
	movb	%al, -80(%rbp,%rcx)
# %bb.3:                                #   in Loop: Header=BB27_1 Depth=1
	movq	-2312(%rbp), %rax
	addq	$1, %rax
	movq	%rax, -2312(%rbp)
	jmp	.LBB27_1
.LBB27_4:
	movq	$0, -2304(%rbp)
.LBB27_5:                               # =>This Inner Loop Header: Depth=1
	movq	-2304(%rbp), %rax
	cmpq	-2264(%rbp), %rax
	jge	.LBB27_8
# %bb.6:                                #   in Loop: Header=BB27_5 Depth=1
	movq	-2304(%rbp), %rax
	movq	-2304(%rbp), %rcx
	movq	%rax, -592(%rbp,%rcx,8)
# %bb.7:                                #   in Loop: Header=BB27_5 Depth=1
	movq	-2304(%rbp), %rax
	addq	$1, %rax
	movq	%rax, -2304(%rbp)
	jmp	.LBB27_5
.LBB27_8:
	movq	$0, -2336(%rbp)
	movl	$1, -2276(%rbp)
.LBB27_9:                               # =>This Loop Header: Depth=1
                                        #     Child Loop BB27_11 Depth 2
                                        #       Child Loop BB27_15 Depth 3
                                        #     Child Loop BB27_26 Depth 2
	cmpl	$0, -2276(%rbp)
	je	.LBB27_35
# %bb.10:                               #   in Loop: Header=BB27_9 Depth=1
	movl	$0, -2276(%rbp)
	movq	$0, -2272(%rbp)
.LBB27_11:                              #   Parent Loop BB27_9 Depth=1
                                        # =>  This Loop Header: Depth=2
                                        #       Child Loop BB27_15 Depth 3
	movq	-2272(%rbp), %rax
	cmpq	-2264(%rbp), %rax
	jge	.LBB27_25
# %bb.12:                               #   in Loop: Header=BB27_11 Depth=2
	movq	-2344(%rbp), %rdi
	movq	-2272(%rbp), %rsi
	callq	getv
	movq	%rax, -2376(%rbp)
	movq	-2392(%rbp), %rdi
	movq	-2272(%rbp), %rsi
	callq	getv
	movq	%rax, -2328(%rbp)
	movq	-2376(%rbp), %rax
	cmpb	$0, -80(%rbp,%rax)
	je	.LBB27_14
# %bb.13:                               #   in Loop: Header=BB27_11 Depth=2
	movq	$-999999999, -2328(%rbp)        # imm = 0xC4653601
	jmp	.LBB27_23
.LBB27_14:                              #   in Loop: Header=BB27_11 Depth=2
	movq	-2400(%rbp), %rdi
	movq	-2272(%rbp), %rsi
	callq	getv
	movq	%rax, -2368(%rbp)
	movq	$0, -2296(%rbp)
.LBB27_15:                              #   Parent Loop BB27_9 Depth=1
                                        #     Parent Loop BB27_11 Depth=2
                                        # =>    This Inner Loop Header: Depth=3
	movq	-2296(%rbp), %rax
	cmpq	-2352(%rbp), %rax
	jge	.LBB27_21
# %bb.16:                               #   in Loop: Header=BB27_15 Depth=3
	movq	-2368(%rbp), %rax
	movq	-2296(%rbp), %rcx
                                        # kill: def $cl killed $rcx
	shrq	%cl, %rax
	andq	$1, %rax
	cmpq	$0, %rax
	je	.LBB27_19
# %bb.17:                               #   in Loop: Header=BB27_15 Depth=3
	movq	-2296(%rbp), %rax
	cmpb	$0, -80(%rbp,%rax)
	jne	.LBB27_19
# %bb.18:                               #   in Loop: Header=BB27_11 Depth=2
	movq	$-999999999, -2328(%rbp)        # imm = 0xC4653601
	jmp	.LBB27_22
.LBB27_19:                              #   in Loop: Header=BB27_15 Depth=3
	jmp	.LBB27_20
.LBB27_20:                              #   in Loop: Header=BB27_15 Depth=3
	movq	-2296(%rbp), %rax
	addq	$1, %rax
	movq	%rax, -2296(%rbp)
	jmp	.LBB27_15
.LBB27_21:                              # %.loopexit
                                        #   in Loop: Header=BB27_11 Depth=2
	jmp	.LBB27_22
.LBB27_22:                              #   in Loop: Header=BB27_11 Depth=2
	jmp	.LBB27_23
.LBB27_23:                              #   in Loop: Header=BB27_11 Depth=2
	movq	-2328(%rbp), %rax
	movq	-2272(%rbp), %rcx
	movq	%rax, -1104(%rbp,%rcx,8)
# %bb.24:                               #   in Loop: Header=BB27_11 Depth=2
	movq	-2272(%rbp), %rax
	addq	$1, %rax
	movq	%rax, -2272(%rbp)
	jmp	.LBB27_11
.LBB27_25:                              #   in Loop: Header=BB27_9 Depth=1
	leaq	-592(%rbp), %rax
	movq	%rax, -2160(%rbp)
	movq	-2264(%rbp), %rax
	movq	%rax, -2152(%rbp)
	movq	$8, -2144(%rbp)
	movq	$8, -2136(%rbp)
	leaq	-1104(%rbp), %rax
	movq	%rax, -2192(%rbp)
	movq	-2264(%rbp), %rax
	movq	%rax, -2184(%rbp)
	movq	$8, -2176(%rbp)
	movq	$8, -2168(%rbp)
	leaq	-1616(%rbp), %rax
	movq	%rax, -2224(%rbp)
	movq	-2264(%rbp), %rax
	movq	%rax, -2216(%rbp)
	movq	$8, -2208(%rbp)
	movq	$8, -2200(%rbp)
	leaq	-2128(%rbp), %rax
	movq	%rax, -2256(%rbp)
	movq	-2264(%rbp), %rax
	movq	%rax, -2248(%rbp)
	movq	$8, -2240(%rbp)
	movq	$8, -2232(%rbp)
	movq	-2264(%rbp), %rsi
	movq	-2264(%rbp), %rdx
	leaq	-2192(%rbp), %rdi
	leaq	-2160(%rbp), %rcx
	leaq	-2224(%rbp), %r8
	leaq	-2256(%rbp), %r9
	callq	topk
	movq	$0, -2288(%rbp)
.LBB27_26:                              #   Parent Loop BB27_9 Depth=1
                                        # =>  This Inner Loop Header: Depth=2
	movq	-2288(%rbp), %rax
	cmpq	-2264(%rbp), %rax
	jge	.LBB27_33
# %bb.27:                               #   in Loop: Header=BB27_26 Depth=2
	movq	-2288(%rbp), %rax
	movq	-1616(%rbp,%rax,8), %rax
	movq	%rax, -2360(%rbp)
	movq	-2288(%rbp), %rax
	cmpq	$-999999999, -2128(%rbp,%rax,8) # imm = 0xC4653601
	jg	.LBB27_29
# %bb.28:                               #   in Loop: Header=BB27_9 Depth=1
	jmp	.LBB27_34
.LBB27_29:                              #   in Loop: Header=BB27_26 Depth=2
	movq	-2344(%rbp), %rdi
	movq	-2360(%rbp), %rsi
	callq	getv
	movq	%rax, -2320(%rbp)
	movq	-2320(%rbp), %rax
	cmpb	$0, -80(%rbp,%rax)
	je	.LBB27_31
# %bb.30:                               #   in Loop: Header=BB27_26 Depth=2
	jmp	.LBB27_32
.LBB27_31:                              #   in Loop: Header=BB27_26 Depth=2
	movq	-2320(%rbp), %rax
	movb	$1, -80(%rbp,%rax)
	movq	-2384(%rbp), %rdi
	movq	-2336(%rbp), %rsi
	movq	%rsi, %rax
	addq	$1, %rax
	movq	%rax, -2336(%rbp)
	movq	-2320(%rbp), %rdx
	callq	setv
	movl	$1, -2276(%rbp)
.LBB27_32:                              #   in Loop: Header=BB27_26 Depth=2
	movq	-2288(%rbp), %rax
	addq	$1, %rax
	movq	%rax, -2288(%rbp)
	jmp	.LBB27_26
.LBB27_33:                              # %.loopexit1
                                        #   in Loop: Header=BB27_9 Depth=1
	jmp	.LBB27_34
.LBB27_34:                              #   in Loop: Header=BB27_9 Depth=1
	jmp	.LBB27_9
.LBB27_35:
	movq	-2336(%rbp), %rax
	movq	%fs:40, %rcx
	movq	-8(%rbp), %rdx
	cmpq	%rdx, %rcx
	jne	.LBB27_37
# %bb.36:                               # %SP_return
	addq	$2416, %rsp                     # imm = 0x970
	popq	%rbp
	.cfi_def_cfa %rsp, 8
	retq
.LBB27_37:                              # %CallStackCheckFailBlk
	.cfi_def_cfa %rbp, 16
	callq	__stack_chk_fail@PLT
.Lfunc_end27:
	.size	integrated_derive, .Lfunc_end27-integrated_derive
	.cfi_endproc
                                        # -- End function
	.prefalign	4, .Lfunc_end28, nop    # -- Begin function getv
	.type	getv,@function
getv:                                   # @getv
	.cfi_startproc
# %bb.0:
	pushq	%rbp
	.cfi_def_cfa_offset 16
	.cfi_offset %rbp, -16
	movq	%rsp, %rbp
	.cfi_def_cfa_register %rbp
	subq	$16, %rsp
	movq	%rdi, -16(%rbp)
	movq	%rsi, -8(%rbp)
	movq	-16(%rbp), %rdi
	movq	-8(%rbp), %rsi
	callq	mav_get
	addq	$16, %rsp
	popq	%rbp
	.cfi_def_cfa %rsp, 8
	retq
.Lfunc_end28:
	.size	getv, .Lfunc_end28-getv
	.cfi_endproc
                                        # -- End function
	.prefalign	4, .Lfunc_end29, nop    # -- Begin function mav_get
	.type	mav_get,@function
mav_get:                                # @mav_get
	.cfi_startproc
# %bb.0:
	pushq	%rbp
	.cfi_def_cfa_offset 16
	.cfi_offset %rbp, -16
	movq	%rsp, %rbp
	.cfi_def_cfa_register %rbp
	movq	%rdi, -24(%rbp)
	movq	%rsi, -40(%rbp)
	movq	-24(%rbp), %rax
	movq	(%rax), %rax
	movq	-40(%rbp), %rcx
	movq	-24(%rbp), %rdx
	imulq	16(%rdx), %rcx
	addq	%rcx, %rax
	movq	%rax, -32(%rbp)
	movq	$0, -16(%rbp)
	movq	$0, -8(%rbp)
.LBB29_1:                               # =>This Inner Loop Header: Depth=1
	movq	-8(%rbp), %rax
	movq	-24(%rbp), %rcx
	cmpq	24(%rcx), %rax
	jge	.LBB29_4
# %bb.2:                                #   in Loop: Header=BB29_1 Depth=1
	movq	-32(%rbp), %rax
	movq	-8(%rbp), %rcx
	movzbl	(%rax,%rcx), %eax
	movq	-8(%rbp), %rcx
	shlq	$3, %rcx
                                        # kill: def $cl killed $rcx
	shlq	%cl, %rax
	orq	-16(%rbp), %rax
	movq	%rax, -16(%rbp)
# %bb.3:                                #   in Loop: Header=BB29_1 Depth=1
	movq	-8(%rbp), %rax
	addq	$1, %rax
	movq	%rax, -8(%rbp)
	jmp	.LBB29_1
.LBB29_4:
	movq	-16(%rbp), %rax
	popq	%rbp
	.cfi_def_cfa %rsp, 8
	retq
.Lfunc_end29:
	.size	mav_get, .Lfunc_end29-mav_get
	.cfi_endproc
                                        # -- End function
	.prefalign	4, .Lfunc_end30, nop    # -- Begin function setv
	.type	setv,@function
setv:                                   # @setv
	.cfi_startproc
# %bb.0:
	pushq	%rbp
	.cfi_def_cfa_offset 16
	.cfi_offset %rbp, -16
	movq	%rsp, %rbp
	.cfi_def_cfa_register %rbp
	movq	%rdi, -16(%rbp)
	movq	%rsi, -40(%rbp)
	movq	%rdx, -32(%rbp)
	movq	-16(%rbp), %rax
	movq	(%rax), %rax
	movq	-40(%rbp), %rcx
	movq	-16(%rbp), %rdx
	imulq	16(%rdx), %rcx
	addq	%rcx, %rax
	movq	%rax, -24(%rbp)
	movq	$0, -8(%rbp)
.LBB30_1:                               # =>This Inner Loop Header: Depth=1
	movq	-8(%rbp), %rax
	movq	-16(%rbp), %rcx
	cmpq	24(%rcx), %rax
	jge	.LBB30_4
# %bb.2:                                #   in Loop: Header=BB30_1 Depth=1
	movq	-32(%rbp), %rax
	movq	-8(%rbp), %rcx
	shlq	$3, %rcx
                                        # kill: def $cl killed $rcx
	sarq	%cl, %rax
	andq	$255, %rax
	movq	-24(%rbp), %rcx
	movq	-8(%rbp), %rdx
	movb	%al, (%rcx,%rdx)
# %bb.3:                                #   in Loop: Header=BB30_1 Depth=1
	movq	-8(%rbp), %rax
	addq	$1, %rax
	movq	%rax, -8(%rbp)
	jmp	.LBB30_1
.LBB30_4:
	popq	%rbp
	.cfi_def_cfa %rsp, 8
	retq
.Lfunc_end30:
	.size	setv, .Lfunc_end30-setv
	.cfi_endproc
                                        # -- End function
	.prefalign	4, .Lfunc_end31, nop    # -- Begin function qdiv
	.type	qdiv,@function
qdiv:                                   # @qdiv
	.cfi_startproc
# %bb.0:
	pushq	%rbp
	.cfi_def_cfa_offset 16
	.cfi_offset %rbp, -16
	movq	%rsp, %rbp
	.cfi_def_cfa_register %rbp
	movq	%rdi, -16(%rbp)
	movq	%rsi, -8(%rbp)
	cmpq	$0, -8(%rbp)
	je	.LBB31_2
# %bb.1:
	movq	-16(%rbp), %rax
	shlq	$16, %rax
	cqto
	idivq	-8(%rbp)
	jmp	.LBB31_3
.LBB31_2:
	xorl	%eax, %eax
	jmp	.LBB31_3
.LBB31_3:
	popq	%rbp
	.cfi_def_cfa %rsp, 8
	retq
.Lfunc_end31:
	.size	qdiv, .Lfunc_end31-qdiv
	.cfi_endproc
                                        # -- End function
	.prefalign	4, .Lfunc_end32, nop    # -- Begin function qsqrt
	.type	qsqrt,@function
qsqrt:                                  # @qsqrt
	.cfi_startproc
# %bb.0:
	pushq	%rbp
	.cfi_def_cfa_offset 16
	.cfi_offset %rbp, -16
	movq	%rsp, %rbp
	.cfi_def_cfa_register %rbp
	movq	%rdi, -16(%rbp)
	cmpq	$0, -16(%rbp)
	jg	.LBB32_2
# %bb.1:
	movq	$0, -24(%rbp)
	jmp	.LBB32_6
.LBB32_2:
	movq	$0, -8(%rbp)
.LBB32_3:                               # =>This Inner Loop Header: Depth=1
	movq	-8(%rbp), %rax
	addq	$1, %rax
	movq	-8(%rbp), %rcx
	addq	$1, %rcx
	imulq	%rcx, %rax
	cmpq	-16(%rbp), %rax
	jg	.LBB32_5
# %bb.4:                                #   in Loop: Header=BB32_3 Depth=1
	movq	-8(%rbp), %rax
	addq	$1, %rax
	movq	%rax, -8(%rbp)
	jmp	.LBB32_3
.LBB32_5:
	movq	-8(%rbp), %rax
	movq	%rax, -24(%rbp)
.LBB32_6:
	movq	-24(%rbp), %rax
	popq	%rbp
	.cfi_def_cfa %rsp, 8
	retq
.Lfunc_end32:
	.size	qsqrt, .Lfunc_end32-qsqrt
	.cfi_endproc
                                        # -- End function
	.prefalign	4, .Lfunc_end33, nop    # -- Begin function adot
	.type	adot,@function
adot:                                   # @adot
	.cfi_startproc
# %bb.0:
	pushq	%rbp
	.cfi_def_cfa_offset 16
	.cfi_offset %rbp, -16
	movq	%rsp, %rbp
	.cfi_def_cfa_register %rbp
	subq	$48, %rsp
	movq	%rdi, -40(%rbp)
	movq	%rsi, -32(%rbp)
	movq	$4, -24(%rbp)
	movq	$0, -16(%rbp)
	movq	$0, -8(%rbp)
.LBB33_1:                               # =>This Inner Loop Header: Depth=1
	movq	-8(%rbp), %rax
	cmpq	-24(%rbp), %rax
	jge	.LBB33_4
# %bb.2:                                #   in Loop: Header=BB33_1 Depth=1
	movq	-40(%rbp), %rax
	movq	-8(%rbp), %rcx
	movq	(%rax,%rcx,8), %rdi
	movq	-32(%rbp), %rax
	movq	-8(%rbp), %rcx
	movq	(%rax,%rcx,8), %rsi
	callq	qmul
	addq	-16(%rbp), %rax
	movq	%rax, -16(%rbp)
# %bb.3:                                #   in Loop: Header=BB33_1 Depth=1
	movq	-8(%rbp), %rax
	addq	$1, %rax
	movq	%rax, -8(%rbp)
	jmp	.LBB33_1
.LBB33_4:
	movq	-16(%rbp), %rax
	addq	$48, %rsp
	popq	%rbp
	.cfi_def_cfa %rsp, 8
	retq
.Lfunc_end33:
	.size	adot, .Lfunc_end33-adot
	.cfi_endproc
                                        # -- End function
	.type	.L__const.main.b,@object        # @__const.main.b
	.section	.rodata.cst16,"aM",@progbits,16
	.p2align	4, 0x0
.L__const.main.b:
	.quad	100                             # 0x64
	.quad	200                             # 0xc8
	.size	.L__const.main.b, 16

	.type	.L.str,@object                  # @.str
	.section	.rodata.str1.1,"aMS",@progbits,1
.L.str:
	.asciz	"MATVEC %s %ld %ld\n"
	.size	.L.str, 19

	.type	.L.str.1,@object                # @.str.1
.L.str.1:
	.asciz	"PASS"
	.size	.L.str.1, 5

	.type	.L.str.2,@object                # @.str.2
.L.str.2:
	.asciz	"FAIL"
	.size	.L.str.2, 5

	.type	.L.str.3,@object                # @.str.3
.L.str.3:
	.asciz	"BATCH %s\n"
	.size	.L.str.3, 10

	.type	.L__const.main.sx,@object       # @__const.main.sx
	.section	.rodata,"a",@progbits
	.p2align	4, 0x0
.L__const.main.sx:
	.quad	0                               # 0x0
	.quad	65536                           # 0x10000
	.quad	131072                          # 0x20000
	.size	.L__const.main.sx, 24

	.type	.L.str.4,@object                # @.str.4
	.section	.rodata.str1.1,"aMS",@progbits,1
.L.str.4:
	.asciz	"SOFTMAX %s sum=%ld\n"
	.size	.L.str.4, 20

	.type	.L.str.5,@object                # @.str.5
.L.str.5:
	.asciz	"LAYERNORM %s mean=%ld\n"
	.size	.L.str.5, 23

	.type	.L.str.6,@object                # @.str.6
.L.str.6:
	.asciz	"DIFF %d %ld %ld\n"
	.size	.L.str.6, 17

	.type	.L.str.7,@object                # @.str.7
.L.str.7:
	.asciz	"FUSED-ATTENTION %s\n"
	.size	.L.str.7, 20

	.type	.L.str.8,@object                # @.str.8
.L.str.8:
	.asciz	"TOPK %s\n"
	.size	.L.str.8, 9

	.type	.L.str.9,@object                # @.str.9
.L.str.9:
	.asciz	"ARGMAX %s\n"
	.size	.L.str.9, 11

	.type	.L__const.main.ms,@object       # @__const.main.ms
	.section	.rodata.cst32,"aM",@progbits,32
	.p2align	4, 0x0
.L__const.main.ms:
	.quad	5                               # 0x5
	.quad	6                               # 0x6
	.quad	7                               # 0x7
	.quad	8                               # 0x8
	.size	.L__const.main.ms, 32

	.type	.L__const.main.mv,@object       # @__const.main.mv
	.p2align	4, 0x0
.L__const.main.mv:
	.quad	1                               # 0x1
	.quad	0                               # 0x0
	.quad	1                               # 0x1
	.quad	1                               # 0x1
	.size	.L__const.main.mv, 32

	.type	.L.str.10,@object               # @.str.10
	.section	.rodata.str1.1,"aMS",@progbits,1
.L.str.10:
	.asciz	"MASK %s count=%ld\n"
	.size	.L.str.10, 19

	.type	.L__const.main.ik,@object       # @__const.main.ik
	.section	.rodata.cst32,"aM",@progbits,32
	.p2align	4, 0x0
.L__const.main.ik:
	.quad	3                               # 0x3
	.quad	7                               # 0x7
	.quad	3                               # 0x3
	.quad	9                               # 0x9
	.size	.L__const.main.ik, 32

	.type	.L.str.11,@object               # @.str.11
	.section	.rodata.str1.1,"aMS",@progbits,1
.L.str.11:
	.asciz	"INDEX %s c3=%ld c9=%ld\n"
	.size	.L.str.11, 24

	.type	.L__const.main.pfm,@object      # @__const.main.pfm
	.section	.rodata,"a",@progbits
	.p2align	4, 0x0
.L__const.main.pfm:
	.quad	3                               # 0x3
	.quad	4                               # 0x4
	.quad	16                              # 0x10
	.size	.L__const.main.pfm, 24

	.type	.L.str.12,@object               # @.str.12
	.section	.rodata.str1.1,"aMS",@progbits,1
.L.str.12:
	.asciz	"FRONTIER %s derived=%ld\n"
	.size	.L.str.12, 25

	.type	.L.str.13,@object               # @.str.13
.L.str.13:
	.asciz	"FRONTIER-MISSING %s missing=%ld\n"
	.size	.L.str.13, 33

	.type	.L.str.14,@object               # @.str.14
.L.str.14:
	.asciz	"BFS %s n=%ld\n"
	.size	.L.str.14, 14

	.type	.L__const.main.ptu,@object      # @__const.main.ptu
	.section	.rodata,"a",@progbits
	.p2align	4, 0x0
.L__const.main.ptu:
	.quad	0                               # 0x0
	.quad	1                               # 0x1
	.quad	0                               # 0x0
	.size	.L__const.main.ptu, 24

	.type	.L__const.main.ptv,@object      # @__const.main.ptv
	.p2align	4, 0x0
.L__const.main.ptv:
	.quad	1                               # 0x1
	.quad	2                               # 0x2
	.quad	3                               # 0x3
	.size	.L__const.main.ptv, 24

	.type	.L.str.15,@object               # @.str.15
	.section	.rodata.str1.1,"aMS",@progbits,1
.L.str.15:
	.asciz	"TOPO %s n=%ld\n"
	.size	.L.str.15, 15

	.type	.L__const.main.pp,@object       # @__const.main.pp
	.section	.rodata.cst32,"aM",@progbits,32
	.p2align	4, 0x0
.L__const.main.pp:
	.quad	0                               # 0x0
	.quad	1                               # 0x1
	.quad	2                               # 0x2
	.quad	3                               # 0x3
	.size	.L__const.main.pp, 32

	.type	.L.str.16,@object               # @.str.16
	.section	.rodata.str1.1,"aMS",@progbits,1
.L.str.16:
	.asciz	"UNION-FIND %s\n"
	.size	.L.str.16, 15

	.type	.L__const.main.ca,@object       # @__const.main.ca
	.section	.rodata.cst32,"aM",@progbits,32
	.p2align	4, 0x0
.L__const.main.ca:
	.quad	2                               # 0x2
	.quad	4                               # 0x4
	.quad	0                               # 0x0
	.quad	0                               # 0x0
	.size	.L__const.main.ca, 32

	.type	.L.str.17,@object               # @.str.17
	.section	.rodata.str1.1,"aMS",@progbits,1
.L.str.17:
	.asciz	"BITSET-CLOSURE %s\n"
	.size	.L.str.17, 19

	.type	.L.str.18,@object               # @.str.18
.L.str.18:
	.asciz	"INDEX-UPDATE %s add=%ld remove=%ld after=%ld\n"
	.size	.L.str.18, 46

	.type	.L.str.19,@object               # @.str.19
.L.str.19:
	.asciz	"BCE %s %ld %ld\n"
	.size	.L.str.19, 16

	.type	.L__const.main.bdy,@object      # @__const.main.bdy
	.section	.rodata.cst16,"aM",@progbits,16
	.p2align	4, 0x0
.L__const.main.bdy:
	.quad	131072                          # 0x20000
	.quad	196608                          # 0x30000
	.size	.L__const.main.bdy, 16

	.type	.L.str.20,@object               # @.str.20
	.section	.rodata.str1.1,"aMS",@progbits,1
.L.str.20:
	.asciz	"BACKWARD-MATVEC %s\n"
	.size	.L.str.20, 20

	.type	.L.str.21,@object               # @.str.21
.L.str.21:
	.asciz	"ADAM %s p=%ld\n"
	.size	.L.str.21, 15

	.type	.L__const.main.lw,@object       # @__const.main.lw
	.section	.rodata.cst32,"aM",@progbits,32
	.p2align	4, 0x0
.L__const.main.lw:
	.quad	65536                           # 0x10000
	.quad	0                               # 0x0
	.quad	0                               # 0x0
	.quad	65536                           # 0x10000
	.size	.L__const.main.lw, 32

	.type	.L__const.main.lb2,@object      # @__const.main.lb2
	.section	.rodata.cst16,"aM",@progbits,16
	.p2align	4, 0x0
.L__const.main.lb2:
	.quad	0                               # 0x0
	.quad	-131072                         # 0xfffffffffffe0000
	.size	.L__const.main.lb2, 16

	.type	.L__const.main.lx2,@object      # @__const.main.lx2
	.p2align	4, 0x0
.L__const.main.lx2:
	.quad	65536                           # 0x10000
	.quad	65536                           # 0x10000
	.size	.L__const.main.lx2, 16

	.type	.L.str.22,@object               # @.str.22
	.section	.rodata.str1.1,"aMS",@progbits,1
.L.str.22:
	.asciz	"LINEAR-RELU %s %ld %ld\n"
	.size	.L.str.22, 24

	.type	.L__const.main.lx3,@object      # @__const.main.lx3
	.section	.rodata,"a",@progbits
	.p2align	4, 0x0
.L__const.main.lx3:
	.quad	65536                           # 0x10000
	.quad	131072                          # 0x20000
	.quad	196608                          # 0x30000
	.size	.L__const.main.lx3, 24

	.type	.L__const.main.lg3,@object      # @__const.main.lg3
	.p2align	4, 0x0
.L__const.main.lg3:
	.quad	65536                           # 0x10000
	.quad	65536                           # 0x10000
	.quad	65536                           # 0x10000
	.size	.L__const.main.lg3, 24

	.type	.L.str.23,@object               # @.str.23
	.section	.rodata.str1.1,"aMS",@progbits,1
.L.str.23:
	.asciz	"LINEAR-LN %s sum=%ld\n"
	.size	.L.str.23, 22

	.type	.L__const.main.pih,@object      # @__const.main.pih
	.section	.rodata,"a",@progbits
	.p2align	4, 0x0
.L__const.main.pih:
	.quad	2                               # 0x2
	.quad	3                               # 0x3
	.quad	5                               # 0x5
	.size	.L__const.main.pih, 24

	.type	.L__const.main.pibm,@object     # @__const.main.pibm
	.p2align	4, 0x0
.L__const.main.pibm:
	.quad	3                               # 0x3
	.quad	16                              # 0x10
	.quad	1                               # 0x1
	.size	.L__const.main.pibm, 24

	.type	.L__const.main.pisc,@object     # @__const.main.pisc
	.p2align	4, 0x0
.L__const.main.pisc:
	.quad	100                             # 0x64
	.quad	300                             # 0x12c
	.quad	200                             # 0xc8
	.size	.L__const.main.pisc, 24

	.type	.L.str.24,@object               # @.str.24
	.section	.rodata.str1.1,"aMS",@progbits,1
.L.str.24:
	.asciz	"INTEGRATE %s n=%ld\n"
	.size	.L.str.24, 20

	.type	.L.str.25,@object               # @.str.25
.L.str.25:
	.asciz	"PROOF-GATE %s invalid=%d\n"
	.size	.L.str.25, 26

	.type	.L.str.26,@object               # @.str.26
.L.str.26:
	.asciz	"KERNEL-SUITE-PHASE11\n"
	.size	.L.str.26, 22

	.ident	"clang version 23.1.4"
	.section	".note.GNU-stack","",@progbits
