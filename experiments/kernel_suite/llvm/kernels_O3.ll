; ModuleID = 'src/kernels.c'
source_filename = "src/kernels.c"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-linux-gnu"

%struct.MaruArrayView = type { ptr, i64, i64, i64 }

@.str = private unnamed_addr constant [19 x i8] c"MATVEC %s %ld %ld\0A\00", align 1
@.str.1 = private unnamed_addr constant [5 x i8] c"PASS\00", align 1
@.str.2 = private unnamed_addr constant [5 x i8] c"FAIL\00", align 1
@.str.3 = private unnamed_addr constant [10 x i8] c"BATCH %s\0A\00", align 1
@__const.main.sx = private unnamed_addr constant [3 x i64] [i64 0, i64 65536, i64 131072], align 16
@.str.4 = private unnamed_addr constant [20 x i8] c"SOFTMAX %s sum=%ld\0A\00", align 1
@__const.main.lx = private unnamed_addr constant [3 x i64] [i64 65536, i64 131072, i64 196608], align 16
@.str.5 = private unnamed_addr constant [23 x i8] c"LAYERNORM %s mean=%ld\0A\00", align 1
@.str.6 = private unnamed_addr constant [17 x i8] c"DIFF %d %ld %ld\0A\00", align 1
@.str.7 = private unnamed_addr constant [20 x i8] c"FUSED-ATTENTION %s\0A\00", align 1
@.str.8 = private unnamed_addr constant [9 x i8] c"TOPK %s\0A\00", align 1
@.str.9 = private unnamed_addr constant [11 x i8] c"ARGMAX %s\0A\00", align 1
@.str.10 = private unnamed_addr constant [19 x i8] c"MASK %s count=%ld\0A\00", align 1
@__const.main.ik = private unnamed_addr constant [4 x i64] [i64 3, i64 7, i64 3, i64 9], align 16
@.str.11 = private unnamed_addr constant [24 x i8] c"INDEX %s c3=%ld c9=%ld\0A\00", align 1
@.str.12 = private unnamed_addr constant [25 x i8] c"FRONTIER %s derived=%ld\0A\00", align 1
@.str.13 = private unnamed_addr constant [33 x i8] c"FRONTIER-MISSING %s missing=%ld\0A\00", align 1
@__const.main.ba = private unnamed_addr constant [4 x i64] [i64 2, i64 4, i64 0, i64 0], align 16
@.str.14 = private unnamed_addr constant [14 x i8] c"BFS %s n=%ld\0A\00", align 1
@.str.15 = private unnamed_addr constant [15 x i8] c"TOPO %s n=%ld\0A\00", align 1
@__const.main.pp = private unnamed_addr constant [4 x i64] [i64 0, i64 1, i64 2, i64 3], align 16
@.str.16 = private unnamed_addr constant [15 x i8] c"UNION-FIND %s\0A\00", align 1
@.str.17 = private unnamed_addr constant [19 x i8] c"BITSET-CLOSURE %s\0A\00", align 1
@.str.18 = private unnamed_addr constant [46 x i8] c"INDEX-UPDATE %s add=%ld remove=%ld after=%ld\0A\00", align 1
@.str.19 = private unnamed_addr constant [16 x i8] c"BCE %s %ld %ld\0A\00", align 1
@.str.20 = private unnamed_addr constant [20 x i8] c"BACKWARD-MATVEC %s\0A\00", align 1
@.str.21 = private unnamed_addr constant [15 x i8] c"ADAM %s p=%ld\0A\00", align 1
@.str.22 = private unnamed_addr constant [24 x i8] c"LINEAR-RELU %s %ld %ld\0A\00", align 1
@__const.main.lg3 = private unnamed_addr constant [3 x i64] [i64 65536, i64 65536, i64 65536], align 16
@.str.23 = private unnamed_addr constant [22 x i8] c"LINEAR-LN %s sum=%ld\0A\00", align 1
@__const.main.pih = private unnamed_addr constant [3 x i64] [i64 2, i64 3, i64 5], align 16
@.str.24 = private unnamed_addr constant [20 x i8] c"INTEGRATE %s n=%ld\0A\00", align 1
@.str.25 = private unnamed_addr constant [26 x i8] c"PROOF-GATE %s invalid=%d\0A\00", align 1
@str = private unnamed_addr constant [21 x i8] c"KERNEL-SUITE-PHASE11\00", align 1

; Function Attrs: nofree nounwind sspstrong uwtable
define dso_local noundef i32 @main() local_unnamed_addr #0 {
  %1 = alloca [64 x i8], align 16
  %2 = alloca [64 x i64], align 16
  %3 = alloca [64 x i64], align 16
  %4 = alloca [64 x i64], align 16
  %5 = alloca [64 x i64], align 16
  %6 = alloca %struct.MaruArrayView, align 8
  %7 = alloca %struct.MaruArrayView, align 8
  %8 = alloca %struct.MaruArrayView, align 8
  %9 = alloca %struct.MaruArrayView, align 8
  %10 = alloca [64 x i64], align 16
  %11 = alloca %struct.MaruArrayView, align 8
  %12 = alloca [64 x i64], align 16
  %13 = alloca [64 x i64], align 16
  %14 = alloca [3 x [4 x i64]], align 16
  %15 = alloca [3 x [4 x i64]], align 16
  %16 = alloca [3 x [4 x i64]], align 16
  %17 = alloca [3 x [4 x i64]], align 16
  %18 = alloca [3 x [4 x i64]], align 16
  %19 = alloca %struct.MaruArrayView, align 8
  %20 = alloca %struct.MaruArrayView, align 8
  %21 = alloca [3 x i64], align 16
  %22 = alloca [3 x i64], align 16
  %23 = alloca %struct.MaruArrayView, align 8
  %24 = alloca %struct.MaruArrayView, align 8
  %25 = alloca %struct.MaruArrayView, align 8
  %26 = alloca %struct.MaruArrayView, align 8
  %27 = alloca [3 x [4 x i64]], align 16
  %28 = alloca [3 x [4 x i64]], align 16
  %29 = alloca [3 x [4 x i64]], align 16
  %30 = alloca [3 x [4 x i64]], align 16
  %31 = alloca [3 x [4 x i64]], align 16
  %32 = alloca [3 x [4 x i64]], align 16
  %33 = alloca [4 x i64], align 16
  %34 = alloca [4 x i64], align 16
  %35 = alloca [4 x i64], align 16
  %36 = alloca [3 x i64], align 16
  %37 = alloca [3 x i64], align 16
  %38 = alloca %struct.MaruArrayView, align 8
  %39 = alloca %struct.MaruArrayView, align 8
  %40 = alloca %struct.MaruArrayView, align 8
  %41 = alloca %struct.MaruArrayView, align 8
  %42 = alloca [3 x i64], align 16
  %43 = alloca [3 x i64], align 16
  %44 = alloca %struct.MaruArrayView, align 8
  %45 = alloca %struct.MaruArrayView, align 8
  %46 = alloca [3 x i64], align 16
  %47 = alloca [3 x i64], align 16
  %48 = alloca [3 x i64], align 16
  %49 = alloca [3 x i64], align 16
  %50 = alloca %struct.MaruArrayView, align 8
  %51 = alloca %struct.MaruArrayView, align 8
  %52 = alloca %struct.MaruArrayView, align 8
  %53 = alloca %struct.MaruArrayView, align 8
  %54 = alloca [12 x i64], align 16
  %55 = alloca [48 x i64], align 16
  %56 = alloca [12 x i64], align 16
  %57 = alloca [16 x i64], align 16
  %58 = alloca [4 x i64], align 16
  %59 = alloca [4 x i64], align 16
  %60 = alloca [4 x i64], align 16
  %61 = alloca [12 x i64], align 16
  %62 = alloca %struct.MaruArrayView, align 8
  %63 = alloca %struct.MaruArrayView, align 8
  %64 = alloca [5 x i64], align 16
  %65 = alloca [5 x i64], align 16
  %66 = alloca [3 x i64], align 16
  %67 = alloca [3 x i64], align 16
  %68 = alloca %struct.MaruArrayView, align 8
  %69 = alloca %struct.MaruArrayView, align 8
  %70 = alloca %struct.MaruArrayView, align 8
  %71 = alloca %struct.MaruArrayView, align 8
  %72 = alloca [4 x i64], align 16
  %73 = alloca [8 x i64], align 16
  %74 = alloca [4 x i64], align 16
  %75 = alloca [4 x i64], align 16
  %76 = alloca %struct.MaruArrayView, align 8
  %77 = alloca %struct.MaruArrayView, align 8
  %78 = alloca %struct.MaruArrayView, align 8
  %79 = alloca [4 x i64], align 16
  %80 = alloca [4 x i64], align 16
  %81 = alloca [4 x i64], align 16
  %82 = alloca [5 x i64], align 16
  %83 = alloca [8 x i64], align 16
  %84 = alloca [5 x i64], align 16
  %85 = alloca %struct.MaruArrayView, align 8
  %86 = alloca %struct.MaruArrayView, align 8
  %87 = alloca %struct.MaruArrayView, align 8
  %88 = alloca [3 x i64], align 16
  %89 = alloca [3 x i64], align 16
  %90 = alloca [3 x i64], align 16
  %91 = alloca %struct.MaruArrayView, align 8
  %92 = alloca %struct.MaruArrayView, align 8
  %93 = alloca %struct.MaruArrayView, align 8
  %94 = alloca [6 x i64], align 16
  %95 = tail call i32 (ptr, ...) @printf(ptr noundef nonnull dereferenceable(1) @.str, ptr noundef nonnull @.str.1, i64 noundef 65636, i64 noundef 131272)
  %96 = tail call i32 (ptr, ...) @printf(ptr noundef nonnull dereferenceable(1) @.str.3, ptr noundef nonnull @.str.1)
  call void @llvm.lifetime.start.p0(ptr nonnull %42) #9
  call void @llvm.memcpy.p0.p0.i64(ptr noundef nonnull align 16 dereferenceable(24) %42, ptr noundef nonnull align 16 dereferenceable(24) @__const.main.sx, i64 24, i1 false)
  call void @llvm.lifetime.start.p0(ptr nonnull %43) #9
  call void @llvm.lifetime.start.p0(ptr nonnull %44) #9
  store ptr %42, ptr %44, align 8, !tbaa !9
  %97 = getelementptr inbounds nuw i8, ptr %44, i64 8
  store i64 3, ptr %97, align 8, !tbaa !14
  %98 = getelementptr inbounds nuw i8, ptr %44, i64 16
  store i64 8, ptr %98, align 8, !tbaa !15
  %99 = getelementptr inbounds nuw i8, ptr %44, i64 24
  store i64 8, ptr %99, align 8, !tbaa !16
  call void @llvm.lifetime.start.p0(ptr nonnull %45) #9
  store ptr %43, ptr %45, align 8, !tbaa !9
  %100 = getelementptr inbounds nuw i8, ptr %45, i64 8
  store i64 3, ptr %100, align 8, !tbaa !14
  %101 = getelementptr inbounds nuw i8, ptr %45, i64 16
  store i64 8, ptr %101, align 8, !tbaa !15
  %102 = getelementptr inbounds nuw i8, ptr %45, i64 24
  store i64 8, ptr %102, align 8, !tbaa !16
  call fastcc void @softmax(ptr noundef %44, ptr noundef %45)
  %103 = load i64, ptr %43, align 16, !tbaa !17
  %104 = getelementptr inbounds nuw i8, ptr %43, i64 8
  %105 = load i64, ptr %104, align 8, !tbaa !17
  %106 = add nsw i64 %105, %103
  %107 = getelementptr inbounds nuw i8, ptr %43, i64 16
  %108 = load i64, ptr %107, align 16, !tbaa !17
  %109 = add nsw i64 %108, %106
  %110 = add i64 %109, -65534
  %111 = icmp ult i64 %110, 5
  %112 = select i1 %111, ptr @.str.1, ptr @.str.2
  %113 = call i32 (ptr, ...) @printf(ptr noundef nonnull dereferenceable(1) @.str.4, ptr noundef nonnull %112, i64 noundef %109)
  call void @llvm.lifetime.start.p0(ptr nonnull %46) #9
  call void @llvm.memcpy.p0.p0.i64(ptr noundef nonnull align 16 dereferenceable(24) %46, ptr noundef nonnull align 16 dereferenceable(24) @__const.main.lx, i64 24, i1 false)
  call void @llvm.lifetime.start.p0(ptr nonnull %47) #9
  call void @llvm.memcpy.p0.p0.i64(ptr noundef nonnull align 16 dereferenceable(24) %47, ptr noundef nonnull align 16 dereferenceable(24) @__const.main.lg3, i64 24, i1 false)
  call void @llvm.lifetime.start.p0(ptr nonnull %48) #9
  call void @llvm.memset.p0.i64(ptr noundef nonnull align 16 dereferenceable(24) %48, i8 0, i64 24, i1 false)
  call void @llvm.lifetime.start.p0(ptr nonnull %49) #9
  call void @llvm.lifetime.start.p0(ptr nonnull %50) #9
  store ptr %46, ptr %50, align 8, !tbaa !9
  %114 = getelementptr inbounds nuw i8, ptr %50, i64 8
  store i64 3, ptr %114, align 8, !tbaa !14
  %115 = getelementptr inbounds nuw i8, ptr %50, i64 16
  store i64 8, ptr %115, align 8, !tbaa !15
  %116 = getelementptr inbounds nuw i8, ptr %50, i64 24
  store i64 8, ptr %116, align 8, !tbaa !16
  call void @llvm.lifetime.start.p0(ptr nonnull %51) #9
  store ptr %47, ptr %51, align 8, !tbaa !9
  %117 = getelementptr inbounds nuw i8, ptr %51, i64 8
  store i64 3, ptr %117, align 8, !tbaa !14
  %118 = getelementptr inbounds nuw i8, ptr %51, i64 16
  store i64 8, ptr %118, align 8, !tbaa !15
  %119 = getelementptr inbounds nuw i8, ptr %51, i64 24
  store i64 8, ptr %119, align 8, !tbaa !16
  call void @llvm.lifetime.start.p0(ptr nonnull %52) #9
  store ptr %48, ptr %52, align 8, !tbaa !9
  %120 = getelementptr inbounds nuw i8, ptr %52, i64 8
  store i64 3, ptr %120, align 8, !tbaa !14
  %121 = getelementptr inbounds nuw i8, ptr %52, i64 16
  store i64 8, ptr %121, align 8, !tbaa !15
  %122 = getelementptr inbounds nuw i8, ptr %52, i64 24
  store i64 8, ptr %122, align 8, !tbaa !16
  call void @llvm.lifetime.start.p0(ptr nonnull %53) #9
  store ptr %49, ptr %53, align 8, !tbaa !9
  %123 = getelementptr inbounds nuw i8, ptr %53, i64 8
  store i64 3, ptr %123, align 8, !tbaa !14
  %124 = getelementptr inbounds nuw i8, ptr %53, i64 16
  store i64 8, ptr %124, align 8, !tbaa !15
  %125 = getelementptr inbounds nuw i8, ptr %53, i64 24
  store i64 8, ptr %125, align 8, !tbaa !16
  call fastcc void @layernorm(ptr noundef %50, i64 noundef 3, ptr noundef %51, ptr noundef %52, ptr noundef %53)
  %126 = load i64, ptr %49, align 16, !tbaa !17
  %127 = getelementptr inbounds nuw i8, ptr %49, i64 8
  %128 = load i64, ptr %127, align 8, !tbaa !17
  %129 = add nsw i64 %128, %126
  %130 = getelementptr inbounds nuw i8, ptr %49, i64 16
  %131 = load i64, ptr %130, align 16, !tbaa !17
  %132 = add nsw i64 %131, %129
  %133 = add i64 %132, 9
  %134 = icmp ult i64 %133, 19
  %135 = select i1 %134, ptr @.str.1, ptr @.str.2
  %136 = call i32 (ptr, ...) @printf(ptr noundef nonnull dereferenceable(1) @.str.5, ptr noundef nonnull %135, i64 noundef %132)
  call void @llvm.lifetime.start.p0(ptr nonnull %54) #9
  call void @llvm.lifetime.start.p0(ptr nonnull %55) #9
  call void @llvm.lifetime.start.p0(ptr nonnull %56) #9
  call void @llvm.lifetime.start.p0(ptr nonnull %57) #9
  call void @llvm.lifetime.start.p0(ptr nonnull %58) #9
  call void @llvm.lifetime.start.p0(ptr nonnull %59) #9
  call void @llvm.lifetime.start.p0(ptr nonnull %60) #9
  call void @llvm.lifetime.start.p0(ptr nonnull %61) #9
  store i64 -12800, ptr %54, align 16, !tbaa !17
  %137 = getelementptr inbounds nuw i8, ptr %54, i64 8
  store i64 -3328, ptr %137, align 8, !tbaa !17
  %138 = getelementptr inbounds nuw i8, ptr %54, i64 16
  store i64 6144, ptr %138, align 16, !tbaa !17
  %139 = getelementptr inbounds nuw i8, ptr %54, i64 24
  store i64 -9984, ptr %139, align 8, !tbaa !17
  %140 = getelementptr inbounds nuw i8, ptr %54, i64 32
  store i64 -512, ptr %140, align 16, !tbaa !17
  %141 = getelementptr inbounds nuw i8, ptr %54, i64 40
  store i64 8960, ptr %141, align 8, !tbaa !17
  %142 = getelementptr inbounds nuw i8, ptr %54, i64 48
  store i64 -7168, ptr %142, align 16, !tbaa !17
  %143 = getelementptr inbounds nuw i8, ptr %54, i64 56
  store i64 2304, ptr %143, align 8, !tbaa !17
  %144 = getelementptr inbounds nuw i8, ptr %54, i64 64
  store i64 11776, ptr %144, align 16, !tbaa !17
  %145 = getelementptr inbounds nuw i8, ptr %54, i64 72
  store i64 -4352, ptr %145, align 8, !tbaa !17
  %146 = getelementptr inbounds nuw i8, ptr %54, i64 80
  store i64 5120, ptr %146, align 16, !tbaa !17
  %147 = getelementptr inbounds nuw i8, ptr %54, i64 88
  store i64 -11008, ptr %147, align 8, !tbaa !17
  %148 = getelementptr inbounds nuw i8, ptr %55, i64 16
  store <2 x i64> <i64 -12800, i64 -11136>, ptr %55, align 16, !tbaa !17
  store <2 x i64> <i64 -9472, i64 -7808>, ptr %148, align 16, !tbaa !17
  %149 = getelementptr inbounds nuw i8, ptr %55, i64 32
  %150 = getelementptr inbounds nuw i8, ptr %55, i64 48
  store <2 x i64> <i64 -6144, i64 -4480>, ptr %149, align 16, !tbaa !17
  store <2 x i64> <i64 -2816, i64 -1152>, ptr %150, align 16, !tbaa !17
  %151 = getelementptr inbounds nuw i8, ptr %55, i64 64
  %152 = getelementptr inbounds nuw i8, ptr %55, i64 80
  store <2 x i64> <i64 512, i64 2176>, ptr %151, align 16, !tbaa !17
  store <2 x i64> <i64 3840, i64 5504>, ptr %152, align 16, !tbaa !17
  %153 = getelementptr inbounds nuw i8, ptr %55, i64 96
  %154 = getelementptr inbounds nuw i8, ptr %55, i64 112
  store <2 x i64> <i64 7168, i64 8832>, ptr %153, align 16, !tbaa !17
  store <2 x i64> <i64 10496, i64 12160>, ptr %154, align 16, !tbaa !17
  %155 = getelementptr inbounds nuw i8, ptr %55, i64 128
  %156 = getelementptr inbounds nuw i8, ptr %55, i64 144
  store <2 x i64> <i64 -11776, i64 -10112>, ptr %155, align 16, !tbaa !17
  store <2 x i64> <i64 -8448, i64 -6784>, ptr %156, align 16, !tbaa !17
  %157 = getelementptr inbounds nuw i8, ptr %55, i64 160
  %158 = getelementptr inbounds nuw i8, ptr %55, i64 176
  store <2 x i64> <i64 -5120, i64 -3456>, ptr %157, align 16, !tbaa !17
  store <2 x i64> <i64 -1792, i64 -128>, ptr %158, align 16, !tbaa !17
  %159 = getelementptr inbounds nuw i8, ptr %55, i64 192
  %160 = getelementptr inbounds nuw i8, ptr %55, i64 208
  store <2 x i64> <i64 1536, i64 3200>, ptr %159, align 16, !tbaa !17
  store <2 x i64> <i64 4864, i64 6528>, ptr %160, align 16, !tbaa !17
  %161 = getelementptr inbounds nuw i8, ptr %55, i64 224
  %162 = getelementptr inbounds nuw i8, ptr %55, i64 240
  store <2 x i64> <i64 8192, i64 9856>, ptr %161, align 16, !tbaa !17
  store <2 x i64> <i64 11520, i64 -12416>, ptr %162, align 16, !tbaa !17
  %163 = getelementptr inbounds nuw i8, ptr %55, i64 256
  %164 = getelementptr inbounds nuw i8, ptr %55, i64 272
  store <2 x i64> <i64 -10752, i64 -9088>, ptr %163, align 16, !tbaa !17
  store <2 x i64> <i64 -7424, i64 -5760>, ptr %164, align 16, !tbaa !17
  %165 = getelementptr inbounds nuw i8, ptr %55, i64 288
  %166 = getelementptr inbounds nuw i8, ptr %55, i64 304
  store <2 x i64> <i64 -4096, i64 -2432>, ptr %165, align 16, !tbaa !17
  store <2 x i64> <i64 -768, i64 896>, ptr %166, align 16, !tbaa !17
  %167 = getelementptr inbounds nuw i8, ptr %55, i64 320
  %168 = getelementptr inbounds nuw i8, ptr %55, i64 336
  store <2 x i64> <i64 2560, i64 4224>, ptr %167, align 16, !tbaa !17
  store <2 x i64> <i64 5888, i64 7552>, ptr %168, align 16, !tbaa !17
  %169 = getelementptr inbounds nuw i8, ptr %55, i64 352
  %170 = getelementptr inbounds nuw i8, ptr %55, i64 368
  store <2 x i64> <i64 9216, i64 10880>, ptr %169, align 16, !tbaa !17
  store <2 x i64> <i64 12544, i64 -11392>, ptr %170, align 16, !tbaa !17
  store i64 -1600, ptr %56, align 16, !tbaa !17
  %171 = getelementptr inbounds nuw i8, ptr %56, i64 8
  store i64 -1152, ptr %171, align 8, !tbaa !17
  %172 = getelementptr inbounds nuw i8, ptr %56, i64 16
  store i64 -704, ptr %172, align 16, !tbaa !17
  %173 = getelementptr inbounds nuw i8, ptr %56, i64 24
  store i64 -256, ptr %173, align 8, !tbaa !17
  %174 = getelementptr inbounds nuw i8, ptr %56, i64 32
  store i64 192, ptr %174, align 16, !tbaa !17
  %175 = getelementptr inbounds nuw i8, ptr %56, i64 40
  store i64 640, ptr %175, align 8, !tbaa !17
  %176 = getelementptr inbounds nuw i8, ptr %56, i64 48
  store i64 1088, ptr %176, align 16, !tbaa !17
  %177 = getelementptr inbounds nuw i8, ptr %56, i64 56
  store i64 1536, ptr %177, align 8, !tbaa !17
  %178 = getelementptr inbounds nuw i8, ptr %56, i64 64
  store i64 -1216, ptr %178, align 16, !tbaa !17
  %179 = getelementptr inbounds nuw i8, ptr %56, i64 72
  store i64 -768, ptr %179, align 8, !tbaa !17
  %180 = getelementptr inbounds nuw i8, ptr %56, i64 80
  store i64 -320, ptr %180, align 16, !tbaa !17
  %181 = getelementptr inbounds nuw i8, ptr %56, i64 88
  store i64 128, ptr %181, align 8, !tbaa !17
  store i64 -12800, ptr %57, align 16, !tbaa !17
  %182 = getelementptr inbounds nuw i8, ptr %57, i64 8
  store i64 -11392, ptr %182, align 8, !tbaa !17
  %183 = getelementptr inbounds nuw i8, ptr %57, i64 16
  store i64 -9984, ptr %183, align 16, !tbaa !17
  %184 = getelementptr inbounds nuw i8, ptr %57, i64 24
  store i64 -8576, ptr %184, align 8, !tbaa !17
  %185 = getelementptr inbounds nuw i8, ptr %57, i64 32
  store i64 -7168, ptr %185, align 16, !tbaa !17
  %186 = getelementptr inbounds nuw i8, ptr %57, i64 40
  store i64 -5760, ptr %186, align 8, !tbaa !17
  %187 = getelementptr inbounds nuw i8, ptr %57, i64 48
  store i64 -4352, ptr %187, align 16, !tbaa !17
  %188 = getelementptr inbounds nuw i8, ptr %57, i64 56
  store i64 -2944, ptr %188, align 8, !tbaa !17
  %189 = getelementptr inbounds nuw i8, ptr %57, i64 64
  store i64 -1536, ptr %189, align 16, !tbaa !17
  %190 = getelementptr inbounds nuw i8, ptr %57, i64 72
  store i64 -128, ptr %190, align 8, !tbaa !17
  %191 = getelementptr inbounds nuw i8, ptr %57, i64 80
  store i64 1280, ptr %191, align 16, !tbaa !17
  %192 = getelementptr inbounds nuw i8, ptr %57, i64 88
  store i64 2688, ptr %192, align 8, !tbaa !17
  %193 = getelementptr inbounds nuw i8, ptr %57, i64 96
  store i64 4096, ptr %193, align 16, !tbaa !17
  %194 = getelementptr inbounds nuw i8, ptr %57, i64 104
  store i64 5504, ptr %194, align 8, !tbaa !17
  %195 = getelementptr inbounds nuw i8, ptr %57, i64 112
  store i64 6912, ptr %195, align 16, !tbaa !17
  %196 = getelementptr inbounds nuw i8, ptr %57, i64 120
  store i64 8320, ptr %196, align 8, !tbaa !17
  call void @llvm.memset.p0.i64(ptr noundef nonnull align 16 dereferenceable(32) %60, i8 0, i64 32, i1 false), !tbaa !17
  store i64 0, ptr %58, align 16, !tbaa !17
  %197 = getelementptr inbounds nuw i8, ptr %58, i64 8
  store i64 10, ptr %197, align 8, !tbaa !17
  %198 = getelementptr inbounds nuw i8, ptr %58, i64 16
  store i64 20, ptr %198, align 16, !tbaa !17
  %199 = getelementptr inbounds nuw i8, ptr %58, i64 24
  store i64 30, ptr %199, align 8, !tbaa !17
  store <4 x i64> splat (i64 65536), ptr %59, align 16, !tbaa !17
  call void @llvm.lifetime.start.p0(ptr nonnull %62) #9
  store ptr %59, ptr %62, align 8, !tbaa !9
  %200 = getelementptr inbounds nuw i8, ptr %62, i64 8
  store i64 4, ptr %200, align 8, !tbaa !14
  %201 = getelementptr inbounds nuw i8, ptr %62, i64 16
  store i64 8, ptr %201, align 8, !tbaa !15
  %202 = getelementptr inbounds nuw i8, ptr %62, i64 24
  store i64 8, ptr %202, align 8, !tbaa !16
  call void @llvm.lifetime.start.p0(ptr nonnull %63) #9
  store ptr %60, ptr %63, align 8, !tbaa !9
  %203 = getelementptr inbounds nuw i8, ptr %63, i64 8
  store i64 4, ptr %203, align 8, !tbaa !14
  %204 = getelementptr inbounds nuw i8, ptr %63, i64 16
  store i64 8, ptr %204, align 8, !tbaa !15
  %205 = getelementptr inbounds nuw i8, ptr %63, i64 24
  store i64 8, ptr %205, align 8, !tbaa !16
  call void @llvm.lifetime.start.p0(ptr nonnull %27) #9
  call void @llvm.lifetime.start.p0(ptr nonnull %28) #9
  call void @llvm.lifetime.start.p0(ptr nonnull %29) #9
  call void @llvm.lifetime.start.p0(ptr nonnull %30) #9
  call void @llvm.lifetime.start.p0(ptr nonnull %31) #9
  call void @llvm.lifetime.start.p0(ptr nonnull %32) #9
  %206 = getelementptr inbounds nuw i8, ptr %55, i64 128
  %207 = getelementptr inbounds nuw i8, ptr %55, i64 256
  br label %265

208:                                              ; preds = %1317
  %209 = getelementptr inbounds nuw i8, ptr %38, i64 8
  %210 = getelementptr inbounds nuw i8, ptr %38, i64 16
  %211 = getelementptr inbounds nuw i8, ptr %38, i64 24
  %212 = getelementptr inbounds nuw i8, ptr %39, i64 8
  %213 = getelementptr inbounds nuw i8, ptr %39, i64 16
  %214 = getelementptr inbounds nuw i8, ptr %39, i64 24
  %215 = load i64, ptr %29, align 16, !tbaa !17
  %216 = getelementptr inbounds nuw i8, ptr %29, i64 32
  %217 = load i64, ptr %216, align 16, !tbaa !17
  %218 = getelementptr inbounds nuw i8, ptr %29, i64 64
  %219 = load i64, ptr %218, align 16, !tbaa !17
  %220 = load i64, ptr %28, align 16, !tbaa !17
  %221 = getelementptr inbounds nuw i8, ptr %28, i64 8
  %222 = load i64, ptr %221, align 8, !tbaa !17
  %223 = getelementptr inbounds nuw i8, ptr %28, i64 16
  %224 = load i64, ptr %223, align 16, !tbaa !17
  %225 = getelementptr inbounds nuw i8, ptr %28, i64 24
  %226 = load i64, ptr %225, align 8, !tbaa !17
  %227 = getelementptr inbounds nuw i8, ptr %28, i64 32
  %228 = load i64, ptr %227, align 16, !tbaa !17
  %229 = getelementptr inbounds nuw i8, ptr %28, i64 40
  %230 = load i64, ptr %229, align 8, !tbaa !17
  %231 = getelementptr inbounds nuw i8, ptr %28, i64 48
  %232 = load i64, ptr %231, align 16, !tbaa !17
  %233 = getelementptr inbounds nuw i8, ptr %28, i64 56
  %234 = load i64, ptr %233, align 8, !tbaa !17
  %235 = getelementptr inbounds nuw i8, ptr %36, i64 8
  %236 = getelementptr inbounds nuw i8, ptr %28, i64 64
  %237 = load i64, ptr %236, align 16, !tbaa !17
  %238 = getelementptr inbounds nuw i8, ptr %28, i64 72
  %239 = load i64, ptr %238, align 8, !tbaa !17
  %240 = getelementptr inbounds nuw i8, ptr %28, i64 80
  %241 = load i64, ptr %240, align 16, !tbaa !17
  %242 = getelementptr inbounds nuw i8, ptr %28, i64 88
  %243 = load i64, ptr %242, align 8, !tbaa !17
  %244 = getelementptr inbounds nuw i8, ptr %36, i64 16
  %245 = getelementptr inbounds nuw i8, ptr %37, i64 8
  %246 = getelementptr inbounds nuw i8, ptr %37, i64 16
  %247 = getelementptr inbounds nuw i8, ptr %29, i64 8
  %248 = load i64, ptr %247, align 8
  %249 = getelementptr inbounds nuw i8, ptr %29, i64 40
  %250 = load i64, ptr %249, align 8
  %251 = getelementptr inbounds nuw i8, ptr %29, i64 72
  %252 = load i64, ptr %251, align 8
  %253 = getelementptr inbounds nuw i8, ptr %29, i64 16
  %254 = load i64, ptr %253, align 16
  %255 = getelementptr inbounds nuw i8, ptr %29, i64 48
  %256 = load i64, ptr %255, align 16
  %257 = getelementptr inbounds nuw i8, ptr %29, i64 80
  %258 = load i64, ptr %257, align 16
  %259 = getelementptr inbounds nuw i8, ptr %29, i64 24
  %260 = load i64, ptr %259, align 8
  %261 = getelementptr inbounds nuw i8, ptr %29, i64 56
  %262 = load i64, ptr %261, align 8
  %263 = getelementptr inbounds nuw i8, ptr %29, i64 88
  %264 = load i64, ptr %263, align 8
  br label %1330

265:                                              ; preds = %1317, %0
  %266 = phi i64 [ 0, %0 ], [ %1321, %1317 ]
  %267 = shl nuw nsw i64 %266, 5
  %268 = getelementptr inbounds nuw i8, ptr %54, i64 %267
  call void @llvm.lifetime.start.p0(ptr nonnull %33) #9
  call void @llvm.lifetime.start.p0(ptr nonnull %34) #9
  call void @llvm.lifetime.start.p0(ptr nonnull %35) #9
  %269 = getelementptr inbounds nuw i8, ptr %268, i64 8
  %270 = getelementptr inbounds nuw i8, ptr %268, i64 16
  %271 = getelementptr inbounds nuw i8, ptr %268, i64 24
  %272 = load i8, ptr %268, align 16, !tbaa !18
  %273 = getelementptr inbounds nuw i8, ptr %268, i64 1
  %274 = load i8, ptr %273, align 1, !tbaa !18
  %275 = getelementptr inbounds nuw i8, ptr %268, i64 2
  %276 = load i8, ptr %275, align 2, !tbaa !18
  %277 = getelementptr inbounds nuw i8, ptr %268, i64 3
  %278 = load i8, ptr %277, align 1, !tbaa !18
  %279 = getelementptr inbounds nuw i8, ptr %268, i64 4
  %280 = load i8, ptr %279, align 4, !tbaa !18
  %281 = getelementptr inbounds nuw i8, ptr %268, i64 5
  %282 = load i8, ptr %281, align 1, !tbaa !18
  %283 = getelementptr inbounds nuw i8, ptr %268, i64 6
  %284 = load i8, ptr %283, align 2, !tbaa !18
  %285 = getelementptr inbounds nuw i8, ptr %268, i64 7
  %286 = load i8, ptr %285, align 1, !tbaa !18
  %287 = load i8, ptr %269, align 8, !tbaa !18
  %288 = getelementptr inbounds nuw i8, ptr %268, i64 9
  %289 = load i8, ptr %288, align 1, !tbaa !18
  %290 = getelementptr inbounds nuw i8, ptr %268, i64 10
  %291 = load i8, ptr %290, align 2, !tbaa !18
  %292 = getelementptr inbounds nuw i8, ptr %268, i64 11
  %293 = load i8, ptr %292, align 1, !tbaa !18
  %294 = getelementptr inbounds nuw i8, ptr %268, i64 12
  %295 = load i8, ptr %294, align 4, !tbaa !18
  %296 = getelementptr inbounds nuw i8, ptr %268, i64 13
  %297 = load i8, ptr %296, align 1, !tbaa !18
  %298 = getelementptr inbounds nuw i8, ptr %268, i64 14
  %299 = load i8, ptr %298, align 2, !tbaa !18
  %300 = getelementptr inbounds nuw i8, ptr %268, i64 15
  %301 = load i8, ptr %300, align 1, !tbaa !18
  %302 = load i8, ptr %270, align 16, !tbaa !18
  %303 = getelementptr inbounds nuw i8, ptr %268, i64 17
  %304 = load i8, ptr %303, align 1, !tbaa !18
  %305 = getelementptr inbounds nuw i8, ptr %268, i64 18
  %306 = load i8, ptr %305, align 2, !tbaa !18
  %307 = getelementptr inbounds nuw i8, ptr %268, i64 19
  %308 = load i8, ptr %307, align 1, !tbaa !18
  %309 = getelementptr inbounds nuw i8, ptr %268, i64 20
  %310 = load i8, ptr %309, align 4, !tbaa !18
  %311 = getelementptr inbounds nuw i8, ptr %268, i64 21
  %312 = load i8, ptr %311, align 1, !tbaa !18
  %313 = getelementptr inbounds nuw i8, ptr %268, i64 22
  %314 = load i8, ptr %313, align 2, !tbaa !18
  %315 = getelementptr inbounds nuw i8, ptr %268, i64 23
  %316 = load i8, ptr %315, align 1, !tbaa !18
  %317 = load i8, ptr %271, align 8, !tbaa !18
  %318 = getelementptr inbounds nuw i8, ptr %268, i64 25
  %319 = load i8, ptr %318, align 1, !tbaa !18
  %320 = getelementptr inbounds nuw i8, ptr %268, i64 26
  %321 = load i8, ptr %320, align 2, !tbaa !18
  %322 = getelementptr inbounds nuw i8, ptr %268, i64 27
  %323 = load i8, ptr %322, align 1, !tbaa !18
  %324 = getelementptr inbounds nuw i8, ptr %268, i64 28
  %325 = load i8, ptr %324, align 4, !tbaa !18
  %326 = getelementptr inbounds nuw i8, ptr %268, i64 29
  %327 = load i8, ptr %326, align 1, !tbaa !18
  %328 = getelementptr inbounds nuw i8, ptr %268, i64 30
  %329 = load i8, ptr %328, align 2, !tbaa !18
  %330 = getelementptr inbounds nuw i8, ptr %268, i64 31
  %331 = load i8, ptr %330, align 1, !tbaa !18
  %332 = zext i8 %317 to i64
  %333 = zext i8 %319 to i64
  %334 = shl nuw nsw i64 %333, 8
  %335 = or disjoint i64 %334, %332
  %336 = zext i8 %321 to i64
  %337 = shl nuw nsw i64 %336, 16
  %338 = or disjoint i64 %337, %335
  %339 = zext i8 %323 to i64
  %340 = shl nuw nsw i64 %339, 24
  %341 = or disjoint i64 %340, %338
  %342 = zext i8 %325 to i64
  %343 = shl nuw nsw i64 %342, 32
  %344 = or disjoint i64 %343, %341
  %345 = zext i8 %327 to i64
  %346 = shl nuw nsw i64 %345, 40
  %347 = or i64 %346, %344
  %348 = zext i8 %329 to i64
  %349 = shl nuw nsw i64 %348, 48
  %350 = or i64 %349, %347
  %351 = zext i8 %331 to i64
  %352 = shl nuw i64 %351, 56
  %353 = or i64 %352, %350
  %354 = zext i8 %302 to i64
  %355 = zext i8 %304 to i64
  %356 = shl nuw nsw i64 %355, 8
  %357 = or disjoint i64 %356, %354
  %358 = zext i8 %306 to i64
  %359 = shl nuw nsw i64 %358, 16
  %360 = or disjoint i64 %359, %357
  %361 = zext i8 %308 to i64
  %362 = shl nuw nsw i64 %361, 24
  %363 = or disjoint i64 %362, %360
  %364 = zext i8 %310 to i64
  %365 = shl nuw nsw i64 %364, 32
  %366 = or disjoint i64 %365, %363
  %367 = zext i8 %312 to i64
  %368 = shl nuw nsw i64 %367, 40
  %369 = or i64 %368, %366
  %370 = zext i8 %314 to i64
  %371 = shl nuw nsw i64 %370, 48
  %372 = or i64 %371, %369
  %373 = zext i8 %316 to i64
  %374 = shl nuw i64 %373, 56
  %375 = or i64 %374, %372
  %376 = zext i8 %287 to i64
  %377 = zext i8 %289 to i64
  %378 = shl nuw nsw i64 %377, 8
  %379 = or disjoint i64 %378, %376
  %380 = zext i8 %291 to i64
  %381 = shl nuw nsw i64 %380, 16
  %382 = or disjoint i64 %381, %379
  %383 = zext i8 %293 to i64
  %384 = shl nuw nsw i64 %383, 24
  %385 = or disjoint i64 %384, %382
  %386 = zext i8 %295 to i64
  %387 = shl nuw nsw i64 %386, 32
  %388 = or disjoint i64 %387, %385
  %389 = zext i8 %297 to i64
  %390 = shl nuw nsw i64 %389, 40
  %391 = or i64 %390, %388
  %392 = zext i8 %299 to i64
  %393 = shl nuw nsw i64 %392, 48
  %394 = or i64 %393, %391
  %395 = zext i8 %301 to i64
  %396 = shl nuw i64 %395, 56
  %397 = or i64 %396, %394
  %398 = zext i8 %272 to i64
  %399 = zext i8 %274 to i64
  %400 = shl nuw nsw i64 %399, 8
  %401 = or disjoint i64 %400, %398
  %402 = zext i8 %276 to i64
  %403 = shl nuw nsw i64 %402, 16
  %404 = or disjoint i64 %403, %401
  %405 = zext i8 %278 to i64
  %406 = shl nuw nsw i64 %405, 24
  %407 = or disjoint i64 %406, %404
  %408 = zext i8 %280 to i64
  %409 = shl nuw nsw i64 %408, 32
  %410 = or disjoint i64 %409, %407
  %411 = zext i8 %282 to i64
  %412 = shl nuw nsw i64 %411, 40
  %413 = or i64 %412, %410
  %414 = zext i8 %284 to i64
  %415 = shl nuw nsw i64 %414, 48
  %416 = or i64 %415, %413
  %417 = zext i8 %286 to i64
  %418 = shl nuw i64 %417, 56
  %419 = or i64 %418, %416
  br label %420

420:                                              ; preds = %265, %420
  %421 = phi i64 [ 0, %265 ], [ %627, %420 ]
  %422 = shl i64 %421, 5
  %423 = getelementptr i8, ptr %55, i64 %422
  %424 = load i8, ptr %423, align 16, !tbaa !18
  %425 = getelementptr inbounds nuw i8, ptr %423, i64 1
  %426 = load i8, ptr %425, align 1, !tbaa !18
  %427 = getelementptr inbounds nuw i8, ptr %423, i64 2
  %428 = load i8, ptr %427, align 2, !tbaa !18
  %429 = getelementptr inbounds nuw i8, ptr %423, i64 3
  %430 = load i8, ptr %429, align 1, !tbaa !18
  %431 = getelementptr inbounds nuw i8, ptr %423, i64 4
  %432 = load i8, ptr %431, align 4, !tbaa !18
  %433 = getelementptr inbounds nuw i8, ptr %423, i64 5
  %434 = load i8, ptr %433, align 1, !tbaa !18
  %435 = getelementptr inbounds nuw i8, ptr %423, i64 6
  %436 = load i8, ptr %435, align 2, !tbaa !18
  %437 = getelementptr inbounds nuw i8, ptr %423, i64 7
  %438 = load i8, ptr %437, align 1, !tbaa !18
  %439 = getelementptr i8, ptr %423, i64 8
  %440 = load i8, ptr %439, align 8, !tbaa !18
  %441 = getelementptr i8, ptr %423, i64 9
  %442 = load i8, ptr %441, align 1, !tbaa !18
  %443 = getelementptr i8, ptr %423, i64 10
  %444 = load i8, ptr %443, align 2, !tbaa !18
  %445 = getelementptr i8, ptr %423, i64 11
  %446 = load i8, ptr %445, align 1, !tbaa !18
  %447 = getelementptr i8, ptr %423, i64 12
  %448 = load i8, ptr %447, align 4, !tbaa !18
  %449 = getelementptr i8, ptr %423, i64 13
  %450 = load i8, ptr %449, align 1, !tbaa !18
  %451 = getelementptr i8, ptr %423, i64 14
  %452 = load i8, ptr %451, align 2, !tbaa !18
  %453 = getelementptr i8, ptr %423, i64 15
  %454 = load i8, ptr %453, align 1, !tbaa !18
  %455 = getelementptr i8, ptr %423, i64 16
  %456 = load i8, ptr %455, align 16, !tbaa !18
  %457 = getelementptr i8, ptr %423, i64 17
  %458 = load i8, ptr %457, align 1, !tbaa !18
  %459 = getelementptr i8, ptr %423, i64 18
  %460 = load i8, ptr %459, align 2, !tbaa !18
  %461 = getelementptr i8, ptr %423, i64 19
  %462 = load i8, ptr %461, align 1, !tbaa !18
  %463 = getelementptr i8, ptr %423, i64 20
  %464 = load i8, ptr %463, align 4, !tbaa !18
  %465 = getelementptr i8, ptr %423, i64 21
  %466 = load i8, ptr %465, align 1, !tbaa !18
  %467 = getelementptr i8, ptr %423, i64 22
  %468 = load i8, ptr %467, align 2, !tbaa !18
  %469 = getelementptr i8, ptr %423, i64 23
  %470 = load i8, ptr %469, align 1, !tbaa !18
  %471 = getelementptr i8, ptr %423, i64 24
  %472 = load i8, ptr %471, align 8, !tbaa !18
  %473 = getelementptr i8, ptr %423, i64 25
  %474 = load i8, ptr %473, align 1, !tbaa !18
  %475 = getelementptr i8, ptr %423, i64 26
  %476 = load i8, ptr %475, align 2, !tbaa !18
  %477 = getelementptr i8, ptr %423, i64 27
  %478 = load i8, ptr %477, align 1, !tbaa !18
  %479 = getelementptr i8, ptr %423, i64 28
  %480 = load i8, ptr %479, align 4, !tbaa !18
  %481 = getelementptr i8, ptr %423, i64 29
  %482 = load i8, ptr %481, align 1, !tbaa !18
  %483 = getelementptr i8, ptr %423, i64 30
  %484 = load i8, ptr %483, align 2, !tbaa !18
  %485 = getelementptr i8, ptr %423, i64 31
  %486 = load i8, ptr %485, align 1, !tbaa !18
  %487 = shl nsw i64 %421, 3
  %488 = getelementptr inbounds nuw i8, ptr %56, i64 %487
  %489 = load i8, ptr %488, align 8, !tbaa !18
  %490 = zext i8 %489 to i64
  %491 = getelementptr inbounds nuw i8, ptr %488, i64 1
  %492 = load i8, ptr %491, align 1, !tbaa !18
  %493 = zext i8 %492 to i64
  %494 = shl nuw nsw i64 %493, 8
  %495 = or disjoint i64 %494, %490
  %496 = getelementptr inbounds nuw i8, ptr %488, i64 2
  %497 = load i8, ptr %496, align 2, !tbaa !18
  %498 = zext i8 %497 to i64
  %499 = shl nuw nsw i64 %498, 16
  %500 = or disjoint i64 %499, %495
  %501 = getelementptr inbounds nuw i8, ptr %488, i64 3
  %502 = load i8, ptr %501, align 1, !tbaa !18
  %503 = zext i8 %502 to i64
  %504 = shl nuw nsw i64 %503, 24
  %505 = or disjoint i64 %504, %500
  %506 = getelementptr inbounds nuw i8, ptr %488, i64 4
  %507 = load i8, ptr %506, align 4, !tbaa !18
  %508 = zext i8 %507 to i64
  %509 = shl nuw nsw i64 %508, 32
  %510 = or disjoint i64 %509, %505
  %511 = getelementptr inbounds nuw i8, ptr %488, i64 5
  %512 = load i8, ptr %511, align 1, !tbaa !18
  %513 = zext i8 %512 to i64
  %514 = shl nuw nsw i64 %513, 40
  %515 = or i64 %514, %510
  %516 = getelementptr inbounds nuw i8, ptr %488, i64 6
  %517 = load i8, ptr %516, align 2, !tbaa !18
  %518 = zext i8 %517 to i64
  %519 = shl nuw nsw i64 %518, 48
  %520 = or i64 %519, %515
  %521 = getelementptr inbounds nuw i8, ptr %488, i64 7
  %522 = load i8, ptr %521, align 1, !tbaa !18
  %523 = zext i8 %522 to i64
  %524 = shl nuw i64 %523, 56
  %525 = or i64 %524, %520
  %526 = zext i8 %472 to i64
  %527 = zext i8 %474 to i64
  %528 = shl nuw nsw i64 %527, 8
  %529 = or disjoint i64 %528, %526
  %530 = zext i8 %476 to i64
  %531 = shl nuw nsw i64 %530, 16
  %532 = or disjoint i64 %531, %529
  %533 = zext i8 %478 to i64
  %534 = shl nuw nsw i64 %533, 24
  %535 = or disjoint i64 %534, %532
  %536 = zext i8 %480 to i64
  %537 = shl nuw nsw i64 %536, 32
  %538 = or disjoint i64 %537, %535
  %539 = zext i8 %482 to i64
  %540 = shl nuw nsw i64 %539, 40
  %541 = or i64 %540, %538
  %542 = zext i8 %484 to i64
  %543 = shl nuw nsw i64 %542, 48
  %544 = or i64 %543, %541
  %545 = zext i8 %486 to i64
  %546 = shl nuw i64 %545, 56
  %547 = or i64 %546, %544
  %548 = zext i8 %456 to i64
  %549 = zext i8 %458 to i64
  %550 = shl nuw nsw i64 %549, 8
  %551 = or disjoint i64 %550, %548
  %552 = zext i8 %460 to i64
  %553 = shl nuw nsw i64 %552, 16
  %554 = or disjoint i64 %553, %551
  %555 = zext i8 %462 to i64
  %556 = shl nuw nsw i64 %555, 24
  %557 = or disjoint i64 %556, %554
  %558 = zext i8 %464 to i64
  %559 = shl nuw nsw i64 %558, 32
  %560 = or disjoint i64 %559, %557
  %561 = zext i8 %466 to i64
  %562 = shl nuw nsw i64 %561, 40
  %563 = or i64 %562, %560
  %564 = zext i8 %468 to i64
  %565 = shl nuw nsw i64 %564, 48
  %566 = or i64 %565, %563
  %567 = zext i8 %470 to i64
  %568 = shl nuw i64 %567, 56
  %569 = or i64 %568, %566
  %570 = zext i8 %440 to i64
  %571 = zext i8 %442 to i64
  %572 = shl nuw nsw i64 %571, 8
  %573 = or disjoint i64 %572, %570
  %574 = zext i8 %444 to i64
  %575 = shl nuw nsw i64 %574, 16
  %576 = or disjoint i64 %575, %573
  %577 = zext i8 %446 to i64
  %578 = shl nuw nsw i64 %577, 24
  %579 = or disjoint i64 %578, %576
  %580 = zext i8 %448 to i64
  %581 = shl nuw nsw i64 %580, 32
  %582 = or disjoint i64 %581, %579
  %583 = zext i8 %450 to i64
  %584 = shl nuw nsw i64 %583, 40
  %585 = or i64 %584, %582
  %586 = zext i8 %452 to i64
  %587 = shl nuw nsw i64 %586, 48
  %588 = or i64 %587, %585
  %589 = zext i8 %454 to i64
  %590 = shl nuw i64 %589, 56
  %591 = or i64 %590, %588
  %592 = zext i8 %424 to i64
  %593 = zext i8 %426 to i64
  %594 = shl nuw nsw i64 %593, 8
  %595 = or disjoint i64 %594, %592
  %596 = zext i8 %428 to i64
  %597 = shl nuw nsw i64 %596, 16
  %598 = or disjoint i64 %597, %595
  %599 = zext i8 %430 to i64
  %600 = shl nuw nsw i64 %599, 24
  %601 = or disjoint i64 %600, %598
  %602 = zext i8 %432 to i64
  %603 = shl nuw nsw i64 %602, 32
  %604 = or disjoint i64 %603, %601
  %605 = zext i8 %434 to i64
  %606 = shl nuw nsw i64 %605, 40
  %607 = or i64 %606, %604
  %608 = zext i8 %436 to i64
  %609 = shl nuw nsw i64 %608, 48
  %610 = or i64 %609, %607
  %611 = zext i8 %438 to i64
  %612 = shl nuw i64 %611, 56
  %613 = or i64 %612, %610
  %614 = mul nsw i64 %419, %613
  %615 = ashr i64 %614, 16
  %616 = mul nsw i64 %397, %591
  %617 = ashr i64 %616, 16
  %618 = add nsw i64 %617, %615
  %619 = mul nsw i64 %375, %569
  %620 = ashr i64 %619, 16
  %621 = add nsw i64 %618, %620
  %622 = mul nsw i64 %353, %547
  %623 = ashr i64 %622, 16
  %624 = add nsw i64 %621, %623
  %625 = add nsw i64 %624, %525
  %626 = getelementptr inbounds nuw [8 x i8], ptr %33, i64 %421
  store i64 %625, ptr %626, align 8, !tbaa !17
  %627 = add nuw nsw i64 %421, 1
  %628 = icmp eq i64 %627, 4
  br i1 %628, label %629, label %420, !llvm.loop !19

629:                                              ; preds = %420
  %630 = getelementptr inbounds nuw i8, ptr %268, i64 1
  %631 = getelementptr inbounds nuw i8, ptr %268, i64 2
  %632 = getelementptr inbounds nuw i8, ptr %268, i64 3
  %633 = getelementptr inbounds nuw i8, ptr %268, i64 4
  %634 = getelementptr inbounds nuw i8, ptr %268, i64 5
  %635 = getelementptr inbounds nuw i8, ptr %268, i64 6
  %636 = getelementptr inbounds nuw i8, ptr %268, i64 7
  %637 = getelementptr inbounds nuw i8, ptr %268, i64 9
  %638 = getelementptr inbounds nuw i8, ptr %268, i64 10
  %639 = getelementptr inbounds nuw i8, ptr %268, i64 11
  %640 = getelementptr inbounds nuw i8, ptr %268, i64 12
  %641 = getelementptr inbounds nuw i8, ptr %268, i64 13
  %642 = getelementptr inbounds nuw i8, ptr %268, i64 14
  %643 = getelementptr inbounds nuw i8, ptr %268, i64 15
  %644 = getelementptr inbounds nuw i8, ptr %268, i64 17
  %645 = getelementptr inbounds nuw i8, ptr %268, i64 18
  %646 = getelementptr inbounds nuw i8, ptr %268, i64 19
  %647 = getelementptr inbounds nuw i8, ptr %268, i64 20
  %648 = getelementptr inbounds nuw i8, ptr %268, i64 21
  %649 = getelementptr inbounds nuw i8, ptr %268, i64 22
  %650 = getelementptr inbounds nuw i8, ptr %268, i64 23
  %651 = getelementptr inbounds nuw i8, ptr %268, i64 25
  %652 = getelementptr inbounds nuw i8, ptr %268, i64 26
  %653 = getelementptr inbounds nuw i8, ptr %268, i64 27
  %654 = getelementptr inbounds nuw i8, ptr %268, i64 28
  %655 = getelementptr inbounds nuw i8, ptr %268, i64 29
  %656 = getelementptr inbounds nuw i8, ptr %268, i64 30
  %657 = getelementptr inbounds nuw i8, ptr %268, i64 31
  %658 = load i8, ptr %268, align 16, !tbaa !18
  %659 = load i8, ptr %630, align 1, !tbaa !18
  %660 = load i8, ptr %631, align 2, !tbaa !18
  %661 = load i8, ptr %632, align 1, !tbaa !18
  %662 = load i8, ptr %633, align 4, !tbaa !18
  %663 = load i8, ptr %634, align 1, !tbaa !18
  %664 = load i8, ptr %635, align 2, !tbaa !18
  %665 = load i8, ptr %636, align 1, !tbaa !18
  %666 = load i8, ptr %269, align 8, !tbaa !18
  %667 = load i8, ptr %637, align 1, !tbaa !18
  %668 = load i8, ptr %638, align 2, !tbaa !18
  %669 = load i8, ptr %639, align 1, !tbaa !18
  %670 = load i8, ptr %640, align 4, !tbaa !18
  %671 = load i8, ptr %641, align 1, !tbaa !18
  %672 = load i8, ptr %642, align 2, !tbaa !18
  %673 = load i8, ptr %643, align 1, !tbaa !18
  %674 = load i8, ptr %270, align 16, !tbaa !18
  %675 = load i8, ptr %644, align 1, !tbaa !18
  %676 = load i8, ptr %645, align 2, !tbaa !18
  %677 = load i8, ptr %646, align 1, !tbaa !18
  %678 = load i8, ptr %647, align 4, !tbaa !18
  %679 = load i8, ptr %648, align 1, !tbaa !18
  %680 = load i8, ptr %649, align 2, !tbaa !18
  %681 = load i8, ptr %650, align 1, !tbaa !18
  %682 = load i8, ptr %271, align 8, !tbaa !18
  %683 = load i8, ptr %651, align 1, !tbaa !18
  %684 = load i8, ptr %652, align 2, !tbaa !18
  %685 = load i8, ptr %653, align 1, !tbaa !18
  %686 = load i8, ptr %654, align 4, !tbaa !18
  %687 = load i8, ptr %655, align 1, !tbaa !18
  %688 = load i8, ptr %656, align 2, !tbaa !18
  %689 = load i8, ptr %657, align 1, !tbaa !18
  %690 = zext i8 %682 to i64
  %691 = zext i8 %683 to i64
  %692 = shl nuw nsw i64 %691, 8
  %693 = or disjoint i64 %692, %690
  %694 = zext i8 %684 to i64
  %695 = shl nuw nsw i64 %694, 16
  %696 = or disjoint i64 %695, %693
  %697 = zext i8 %685 to i64
  %698 = shl nuw nsw i64 %697, 24
  %699 = or disjoint i64 %698, %696
  %700 = zext i8 %686 to i64
  %701 = shl nuw nsw i64 %700, 32
  %702 = or disjoint i64 %701, %699
  %703 = zext i8 %687 to i64
  %704 = shl nuw nsw i64 %703, 40
  %705 = or i64 %704, %702
  %706 = zext i8 %688 to i64
  %707 = shl nuw nsw i64 %706, 48
  %708 = or i64 %707, %705
  %709 = zext i8 %689 to i64
  %710 = shl nuw i64 %709, 56
  %711 = or i64 %710, %708
  %712 = zext i8 %674 to i64
  %713 = zext i8 %675 to i64
  %714 = shl nuw nsw i64 %713, 8
  %715 = or disjoint i64 %714, %712
  %716 = zext i8 %676 to i64
  %717 = shl nuw nsw i64 %716, 16
  %718 = or disjoint i64 %717, %715
  %719 = zext i8 %677 to i64
  %720 = shl nuw nsw i64 %719, 24
  %721 = or disjoint i64 %720, %718
  %722 = zext i8 %678 to i64
  %723 = shl nuw nsw i64 %722, 32
  %724 = or disjoint i64 %723, %721
  %725 = zext i8 %679 to i64
  %726 = shl nuw nsw i64 %725, 40
  %727 = or i64 %726, %724
  %728 = zext i8 %680 to i64
  %729 = shl nuw nsw i64 %728, 48
  %730 = or i64 %729, %727
  %731 = zext i8 %681 to i64
  %732 = shl nuw i64 %731, 56
  %733 = or i64 %732, %730
  %734 = zext i8 %666 to i64
  %735 = zext i8 %667 to i64
  %736 = shl nuw nsw i64 %735, 8
  %737 = or disjoint i64 %736, %734
  %738 = zext i8 %668 to i64
  %739 = shl nuw nsw i64 %738, 16
  %740 = or disjoint i64 %739, %737
  %741 = zext i8 %669 to i64
  %742 = shl nuw nsw i64 %741, 24
  %743 = or disjoint i64 %742, %740
  %744 = zext i8 %670 to i64
  %745 = shl nuw nsw i64 %744, 32
  %746 = or disjoint i64 %745, %743
  %747 = zext i8 %671 to i64
  %748 = shl nuw nsw i64 %747, 40
  %749 = or i64 %748, %746
  %750 = zext i8 %672 to i64
  %751 = shl nuw nsw i64 %750, 48
  %752 = or i64 %751, %749
  %753 = zext i8 %673 to i64
  %754 = shl nuw i64 %753, 56
  %755 = or i64 %754, %752
  %756 = zext i8 %658 to i64
  %757 = zext i8 %659 to i64
  %758 = shl nuw nsw i64 %757, 8
  %759 = or disjoint i64 %758, %756
  %760 = zext i8 %660 to i64
  %761 = shl nuw nsw i64 %760, 16
  %762 = or disjoint i64 %761, %759
  %763 = zext i8 %661 to i64
  %764 = shl nuw nsw i64 %763, 24
  %765 = or disjoint i64 %764, %762
  %766 = zext i8 %662 to i64
  %767 = shl nuw nsw i64 %766, 32
  %768 = or disjoint i64 %767, %765
  %769 = zext i8 %663 to i64
  %770 = shl nuw nsw i64 %769, 40
  %771 = or i64 %770, %768
  %772 = zext i8 %664 to i64
  %773 = shl nuw nsw i64 %772, 48
  %774 = or i64 %773, %771
  %775 = zext i8 %665 to i64
  %776 = shl nuw i64 %775, 56
  %777 = or i64 %776, %774
  br label %778

778:                                              ; preds = %629, %778
  %779 = phi i64 [ %985, %778 ], [ 0, %629 ]
  %780 = shl i64 %779, 5
  %781 = getelementptr i8, ptr %206, i64 %780
  %782 = load i8, ptr %781, align 16, !tbaa !18
  %783 = getelementptr inbounds nuw i8, ptr %781, i64 1
  %784 = load i8, ptr %783, align 1, !tbaa !18
  %785 = getelementptr inbounds nuw i8, ptr %781, i64 2
  %786 = load i8, ptr %785, align 2, !tbaa !18
  %787 = getelementptr inbounds nuw i8, ptr %781, i64 3
  %788 = load i8, ptr %787, align 1, !tbaa !18
  %789 = getelementptr inbounds nuw i8, ptr %781, i64 4
  %790 = load i8, ptr %789, align 4, !tbaa !18
  %791 = getelementptr inbounds nuw i8, ptr %781, i64 5
  %792 = load i8, ptr %791, align 1, !tbaa !18
  %793 = getelementptr inbounds nuw i8, ptr %781, i64 6
  %794 = load i8, ptr %793, align 2, !tbaa !18
  %795 = getelementptr inbounds nuw i8, ptr %781, i64 7
  %796 = load i8, ptr %795, align 1, !tbaa !18
  %797 = getelementptr i8, ptr %781, i64 8
  %798 = load i8, ptr %797, align 8, !tbaa !18
  %799 = getelementptr i8, ptr %781, i64 9
  %800 = load i8, ptr %799, align 1, !tbaa !18
  %801 = getelementptr i8, ptr %781, i64 10
  %802 = load i8, ptr %801, align 2, !tbaa !18
  %803 = getelementptr i8, ptr %781, i64 11
  %804 = load i8, ptr %803, align 1, !tbaa !18
  %805 = getelementptr i8, ptr %781, i64 12
  %806 = load i8, ptr %805, align 4, !tbaa !18
  %807 = getelementptr i8, ptr %781, i64 13
  %808 = load i8, ptr %807, align 1, !tbaa !18
  %809 = getelementptr i8, ptr %781, i64 14
  %810 = load i8, ptr %809, align 2, !tbaa !18
  %811 = getelementptr i8, ptr %781, i64 15
  %812 = load i8, ptr %811, align 1, !tbaa !18
  %813 = getelementptr i8, ptr %781, i64 16
  %814 = load i8, ptr %813, align 16, !tbaa !18
  %815 = getelementptr i8, ptr %781, i64 17
  %816 = load i8, ptr %815, align 1, !tbaa !18
  %817 = getelementptr i8, ptr %781, i64 18
  %818 = load i8, ptr %817, align 2, !tbaa !18
  %819 = getelementptr i8, ptr %781, i64 19
  %820 = load i8, ptr %819, align 1, !tbaa !18
  %821 = getelementptr i8, ptr %781, i64 20
  %822 = load i8, ptr %821, align 4, !tbaa !18
  %823 = getelementptr i8, ptr %781, i64 21
  %824 = load i8, ptr %823, align 1, !tbaa !18
  %825 = getelementptr i8, ptr %781, i64 22
  %826 = load i8, ptr %825, align 2, !tbaa !18
  %827 = getelementptr i8, ptr %781, i64 23
  %828 = load i8, ptr %827, align 1, !tbaa !18
  %829 = getelementptr i8, ptr %781, i64 24
  %830 = load i8, ptr %829, align 8, !tbaa !18
  %831 = getelementptr i8, ptr %781, i64 25
  %832 = load i8, ptr %831, align 1, !tbaa !18
  %833 = getelementptr i8, ptr %781, i64 26
  %834 = load i8, ptr %833, align 2, !tbaa !18
  %835 = getelementptr i8, ptr %781, i64 27
  %836 = load i8, ptr %835, align 1, !tbaa !18
  %837 = getelementptr i8, ptr %781, i64 28
  %838 = load i8, ptr %837, align 4, !tbaa !18
  %839 = getelementptr i8, ptr %781, i64 29
  %840 = load i8, ptr %839, align 1, !tbaa !18
  %841 = getelementptr i8, ptr %781, i64 30
  %842 = load i8, ptr %841, align 2, !tbaa !18
  %843 = getelementptr i8, ptr %781, i64 31
  %844 = load i8, ptr %843, align 1, !tbaa !18
  %845 = shl nsw i64 %779, 3
  %846 = getelementptr inbounds nuw i8, ptr %174, i64 %845
  %847 = load i8, ptr %846, align 8, !tbaa !18
  %848 = zext i8 %847 to i64
  %849 = getelementptr inbounds nuw i8, ptr %846, i64 1
  %850 = load i8, ptr %849, align 1, !tbaa !18
  %851 = zext i8 %850 to i64
  %852 = shl nuw nsw i64 %851, 8
  %853 = or disjoint i64 %852, %848
  %854 = getelementptr inbounds nuw i8, ptr %846, i64 2
  %855 = load i8, ptr %854, align 2, !tbaa !18
  %856 = zext i8 %855 to i64
  %857 = shl nuw nsw i64 %856, 16
  %858 = or disjoint i64 %857, %853
  %859 = getelementptr inbounds nuw i8, ptr %846, i64 3
  %860 = load i8, ptr %859, align 1, !tbaa !18
  %861 = zext i8 %860 to i64
  %862 = shl nuw nsw i64 %861, 24
  %863 = or disjoint i64 %862, %858
  %864 = getelementptr inbounds nuw i8, ptr %846, i64 4
  %865 = load i8, ptr %864, align 4, !tbaa !18
  %866 = zext i8 %865 to i64
  %867 = shl nuw nsw i64 %866, 32
  %868 = or disjoint i64 %867, %863
  %869 = getelementptr inbounds nuw i8, ptr %846, i64 5
  %870 = load i8, ptr %869, align 1, !tbaa !18
  %871 = zext i8 %870 to i64
  %872 = shl nuw nsw i64 %871, 40
  %873 = or i64 %872, %868
  %874 = getelementptr inbounds nuw i8, ptr %846, i64 6
  %875 = load i8, ptr %874, align 2, !tbaa !18
  %876 = zext i8 %875 to i64
  %877 = shl nuw nsw i64 %876, 48
  %878 = or i64 %877, %873
  %879 = getelementptr inbounds nuw i8, ptr %846, i64 7
  %880 = load i8, ptr %879, align 1, !tbaa !18
  %881 = zext i8 %880 to i64
  %882 = shl nuw i64 %881, 56
  %883 = or i64 %882, %878
  %884 = zext i8 %830 to i64
  %885 = zext i8 %832 to i64
  %886 = shl nuw nsw i64 %885, 8
  %887 = or disjoint i64 %886, %884
  %888 = zext i8 %834 to i64
  %889 = shl nuw nsw i64 %888, 16
  %890 = or disjoint i64 %889, %887
  %891 = zext i8 %836 to i64
  %892 = shl nuw nsw i64 %891, 24
  %893 = or disjoint i64 %892, %890
  %894 = zext i8 %838 to i64
  %895 = shl nuw nsw i64 %894, 32
  %896 = or disjoint i64 %895, %893
  %897 = zext i8 %840 to i64
  %898 = shl nuw nsw i64 %897, 40
  %899 = or i64 %898, %896
  %900 = zext i8 %842 to i64
  %901 = shl nuw nsw i64 %900, 48
  %902 = or i64 %901, %899
  %903 = zext i8 %844 to i64
  %904 = shl nuw i64 %903, 56
  %905 = or i64 %904, %902
  %906 = zext i8 %814 to i64
  %907 = zext i8 %816 to i64
  %908 = shl nuw nsw i64 %907, 8
  %909 = or disjoint i64 %908, %906
  %910 = zext i8 %818 to i64
  %911 = shl nuw nsw i64 %910, 16
  %912 = or disjoint i64 %911, %909
  %913 = zext i8 %820 to i64
  %914 = shl nuw nsw i64 %913, 24
  %915 = or disjoint i64 %914, %912
  %916 = zext i8 %822 to i64
  %917 = shl nuw nsw i64 %916, 32
  %918 = or disjoint i64 %917, %915
  %919 = zext i8 %824 to i64
  %920 = shl nuw nsw i64 %919, 40
  %921 = or i64 %920, %918
  %922 = zext i8 %826 to i64
  %923 = shl nuw nsw i64 %922, 48
  %924 = or i64 %923, %921
  %925 = zext i8 %828 to i64
  %926 = shl nuw i64 %925, 56
  %927 = or i64 %926, %924
  %928 = zext i8 %798 to i64
  %929 = zext i8 %800 to i64
  %930 = shl nuw nsw i64 %929, 8
  %931 = or disjoint i64 %930, %928
  %932 = zext i8 %802 to i64
  %933 = shl nuw nsw i64 %932, 16
  %934 = or disjoint i64 %933, %931
  %935 = zext i8 %804 to i64
  %936 = shl nuw nsw i64 %935, 24
  %937 = or disjoint i64 %936, %934
  %938 = zext i8 %806 to i64
  %939 = shl nuw nsw i64 %938, 32
  %940 = or disjoint i64 %939, %937
  %941 = zext i8 %808 to i64
  %942 = shl nuw nsw i64 %941, 40
  %943 = or i64 %942, %940
  %944 = zext i8 %810 to i64
  %945 = shl nuw nsw i64 %944, 48
  %946 = or i64 %945, %943
  %947 = zext i8 %812 to i64
  %948 = shl nuw i64 %947, 56
  %949 = or i64 %948, %946
  %950 = zext i8 %782 to i64
  %951 = zext i8 %784 to i64
  %952 = shl nuw nsw i64 %951, 8
  %953 = or disjoint i64 %952, %950
  %954 = zext i8 %786 to i64
  %955 = shl nuw nsw i64 %954, 16
  %956 = or disjoint i64 %955, %953
  %957 = zext i8 %788 to i64
  %958 = shl nuw nsw i64 %957, 24
  %959 = or disjoint i64 %958, %956
  %960 = zext i8 %790 to i64
  %961 = shl nuw nsw i64 %960, 32
  %962 = or disjoint i64 %961, %959
  %963 = zext i8 %792 to i64
  %964 = shl nuw nsw i64 %963, 40
  %965 = or i64 %964, %962
  %966 = zext i8 %794 to i64
  %967 = shl nuw nsw i64 %966, 48
  %968 = or i64 %967, %965
  %969 = zext i8 %796 to i64
  %970 = shl nuw i64 %969, 56
  %971 = or i64 %970, %968
  %972 = mul nsw i64 %777, %971
  %973 = ashr i64 %972, 16
  %974 = mul nsw i64 %755, %949
  %975 = ashr i64 %974, 16
  %976 = add nsw i64 %975, %973
  %977 = mul nsw i64 %733, %927
  %978 = ashr i64 %977, 16
  %979 = add nsw i64 %976, %978
  %980 = mul nsw i64 %711, %905
  %981 = ashr i64 %980, 16
  %982 = add nsw i64 %979, %981
  %983 = add nsw i64 %982, %883
  %984 = getelementptr inbounds nuw [8 x i8], ptr %34, i64 %779
  store i64 %983, ptr %984, align 8, !tbaa !17
  %985 = add nuw nsw i64 %779, 1
  %986 = icmp eq i64 %985, 4
  br i1 %986, label %987, label %778, !llvm.loop !19

987:                                              ; preds = %778
  %988 = load i8, ptr %268, align 16, !tbaa !18
  %989 = load i8, ptr %630, align 1, !tbaa !18
  %990 = load i8, ptr %631, align 2, !tbaa !18
  %991 = load i8, ptr %632, align 1, !tbaa !18
  %992 = load i8, ptr %633, align 4, !tbaa !18
  %993 = load i8, ptr %634, align 1, !tbaa !18
  %994 = load i8, ptr %635, align 2, !tbaa !18
  %995 = load i8, ptr %636, align 1, !tbaa !18
  %996 = load i8, ptr %269, align 8, !tbaa !18
  %997 = load i8, ptr %637, align 1, !tbaa !18
  %998 = load i8, ptr %638, align 2, !tbaa !18
  %999 = load i8, ptr %639, align 1, !tbaa !18
  %1000 = load i8, ptr %640, align 4, !tbaa !18
  %1001 = load i8, ptr %641, align 1, !tbaa !18
  %1002 = load i8, ptr %642, align 2, !tbaa !18
  %1003 = load i8, ptr %643, align 1, !tbaa !18
  %1004 = load i8, ptr %270, align 16, !tbaa !18
  %1005 = load i8, ptr %644, align 1, !tbaa !18
  %1006 = load i8, ptr %645, align 2, !tbaa !18
  %1007 = load i8, ptr %646, align 1, !tbaa !18
  %1008 = load i8, ptr %647, align 4, !tbaa !18
  %1009 = load i8, ptr %648, align 1, !tbaa !18
  %1010 = load i8, ptr %649, align 2, !tbaa !18
  %1011 = load i8, ptr %650, align 1, !tbaa !18
  %1012 = load i8, ptr %271, align 8, !tbaa !18
  %1013 = load i8, ptr %651, align 1, !tbaa !18
  %1014 = load i8, ptr %652, align 2, !tbaa !18
  %1015 = load i8, ptr %653, align 1, !tbaa !18
  %1016 = load i8, ptr %654, align 4, !tbaa !18
  %1017 = load i8, ptr %655, align 1, !tbaa !18
  %1018 = load i8, ptr %656, align 2, !tbaa !18
  %1019 = load i8, ptr %657, align 1, !tbaa !18
  %1020 = zext i8 %1012 to i64
  %1021 = zext i8 %1013 to i64
  %1022 = shl nuw nsw i64 %1021, 8
  %1023 = or disjoint i64 %1022, %1020
  %1024 = zext i8 %1014 to i64
  %1025 = shl nuw nsw i64 %1024, 16
  %1026 = or disjoint i64 %1025, %1023
  %1027 = zext i8 %1015 to i64
  %1028 = shl nuw nsw i64 %1027, 24
  %1029 = or disjoint i64 %1028, %1026
  %1030 = zext i8 %1016 to i64
  %1031 = shl nuw nsw i64 %1030, 32
  %1032 = or disjoint i64 %1031, %1029
  %1033 = zext i8 %1017 to i64
  %1034 = shl nuw nsw i64 %1033, 40
  %1035 = or i64 %1034, %1032
  %1036 = zext i8 %1018 to i64
  %1037 = shl nuw nsw i64 %1036, 48
  %1038 = or i64 %1037, %1035
  %1039 = zext i8 %1019 to i64
  %1040 = shl nuw i64 %1039, 56
  %1041 = or i64 %1040, %1038
  %1042 = zext i8 %1004 to i64
  %1043 = zext i8 %1005 to i64
  %1044 = shl nuw nsw i64 %1043, 8
  %1045 = or disjoint i64 %1044, %1042
  %1046 = zext i8 %1006 to i64
  %1047 = shl nuw nsw i64 %1046, 16
  %1048 = or disjoint i64 %1047, %1045
  %1049 = zext i8 %1007 to i64
  %1050 = shl nuw nsw i64 %1049, 24
  %1051 = or disjoint i64 %1050, %1048
  %1052 = zext i8 %1008 to i64
  %1053 = shl nuw nsw i64 %1052, 32
  %1054 = or disjoint i64 %1053, %1051
  %1055 = zext i8 %1009 to i64
  %1056 = shl nuw nsw i64 %1055, 40
  %1057 = or i64 %1056, %1054
  %1058 = zext i8 %1010 to i64
  %1059 = shl nuw nsw i64 %1058, 48
  %1060 = or i64 %1059, %1057
  %1061 = zext i8 %1011 to i64
  %1062 = shl nuw i64 %1061, 56
  %1063 = or i64 %1062, %1060
  %1064 = zext i8 %996 to i64
  %1065 = zext i8 %997 to i64
  %1066 = shl nuw nsw i64 %1065, 8
  %1067 = or disjoint i64 %1066, %1064
  %1068 = zext i8 %998 to i64
  %1069 = shl nuw nsw i64 %1068, 16
  %1070 = or disjoint i64 %1069, %1067
  %1071 = zext i8 %999 to i64
  %1072 = shl nuw nsw i64 %1071, 24
  %1073 = or disjoint i64 %1072, %1070
  %1074 = zext i8 %1000 to i64
  %1075 = shl nuw nsw i64 %1074, 32
  %1076 = or disjoint i64 %1075, %1073
  %1077 = zext i8 %1001 to i64
  %1078 = shl nuw nsw i64 %1077, 40
  %1079 = or i64 %1078, %1076
  %1080 = zext i8 %1002 to i64
  %1081 = shl nuw nsw i64 %1080, 48
  %1082 = or i64 %1081, %1079
  %1083 = zext i8 %1003 to i64
  %1084 = shl nuw i64 %1083, 56
  %1085 = or i64 %1084, %1082
  %1086 = zext i8 %988 to i64
  %1087 = zext i8 %989 to i64
  %1088 = shl nuw nsw i64 %1087, 8
  %1089 = or disjoint i64 %1088, %1086
  %1090 = zext i8 %990 to i64
  %1091 = shl nuw nsw i64 %1090, 16
  %1092 = or disjoint i64 %1091, %1089
  %1093 = zext i8 %991 to i64
  %1094 = shl nuw nsw i64 %1093, 24
  %1095 = or disjoint i64 %1094, %1092
  %1096 = zext i8 %992 to i64
  %1097 = shl nuw nsw i64 %1096, 32
  %1098 = or disjoint i64 %1097, %1095
  %1099 = zext i8 %993 to i64
  %1100 = shl nuw nsw i64 %1099, 40
  %1101 = or i64 %1100, %1098
  %1102 = zext i8 %994 to i64
  %1103 = shl nuw nsw i64 %1102, 48
  %1104 = or i64 %1103, %1101
  %1105 = zext i8 %995 to i64
  %1106 = shl nuw i64 %1105, 56
  %1107 = or i64 %1106, %1104
  br label %1108

1108:                                             ; preds = %987, %1108
  %1109 = phi i64 [ %1315, %1108 ], [ 0, %987 ]
  %1110 = shl i64 %1109, 5
  %1111 = getelementptr i8, ptr %207, i64 %1110
  %1112 = load i8, ptr %1111, align 16, !tbaa !18
  %1113 = getelementptr inbounds nuw i8, ptr %1111, i64 1
  %1114 = load i8, ptr %1113, align 1, !tbaa !18
  %1115 = getelementptr inbounds nuw i8, ptr %1111, i64 2
  %1116 = load i8, ptr %1115, align 2, !tbaa !18
  %1117 = getelementptr inbounds nuw i8, ptr %1111, i64 3
  %1118 = load i8, ptr %1117, align 1, !tbaa !18
  %1119 = getelementptr inbounds nuw i8, ptr %1111, i64 4
  %1120 = load i8, ptr %1119, align 4, !tbaa !18
  %1121 = getelementptr inbounds nuw i8, ptr %1111, i64 5
  %1122 = load i8, ptr %1121, align 1, !tbaa !18
  %1123 = getelementptr inbounds nuw i8, ptr %1111, i64 6
  %1124 = load i8, ptr %1123, align 2, !tbaa !18
  %1125 = getelementptr inbounds nuw i8, ptr %1111, i64 7
  %1126 = load i8, ptr %1125, align 1, !tbaa !18
  %1127 = getelementptr i8, ptr %1111, i64 8
  %1128 = load i8, ptr %1127, align 8, !tbaa !18
  %1129 = getelementptr i8, ptr %1111, i64 9
  %1130 = load i8, ptr %1129, align 1, !tbaa !18
  %1131 = getelementptr i8, ptr %1111, i64 10
  %1132 = load i8, ptr %1131, align 2, !tbaa !18
  %1133 = getelementptr i8, ptr %1111, i64 11
  %1134 = load i8, ptr %1133, align 1, !tbaa !18
  %1135 = getelementptr i8, ptr %1111, i64 12
  %1136 = load i8, ptr %1135, align 4, !tbaa !18
  %1137 = getelementptr i8, ptr %1111, i64 13
  %1138 = load i8, ptr %1137, align 1, !tbaa !18
  %1139 = getelementptr i8, ptr %1111, i64 14
  %1140 = load i8, ptr %1139, align 2, !tbaa !18
  %1141 = getelementptr i8, ptr %1111, i64 15
  %1142 = load i8, ptr %1141, align 1, !tbaa !18
  %1143 = getelementptr i8, ptr %1111, i64 16
  %1144 = load i8, ptr %1143, align 16, !tbaa !18
  %1145 = getelementptr i8, ptr %1111, i64 17
  %1146 = load i8, ptr %1145, align 1, !tbaa !18
  %1147 = getelementptr i8, ptr %1111, i64 18
  %1148 = load i8, ptr %1147, align 2, !tbaa !18
  %1149 = getelementptr i8, ptr %1111, i64 19
  %1150 = load i8, ptr %1149, align 1, !tbaa !18
  %1151 = getelementptr i8, ptr %1111, i64 20
  %1152 = load i8, ptr %1151, align 4, !tbaa !18
  %1153 = getelementptr i8, ptr %1111, i64 21
  %1154 = load i8, ptr %1153, align 1, !tbaa !18
  %1155 = getelementptr i8, ptr %1111, i64 22
  %1156 = load i8, ptr %1155, align 2, !tbaa !18
  %1157 = getelementptr i8, ptr %1111, i64 23
  %1158 = load i8, ptr %1157, align 1, !tbaa !18
  %1159 = getelementptr i8, ptr %1111, i64 24
  %1160 = load i8, ptr %1159, align 8, !tbaa !18
  %1161 = getelementptr i8, ptr %1111, i64 25
  %1162 = load i8, ptr %1161, align 1, !tbaa !18
  %1163 = getelementptr i8, ptr %1111, i64 26
  %1164 = load i8, ptr %1163, align 2, !tbaa !18
  %1165 = getelementptr i8, ptr %1111, i64 27
  %1166 = load i8, ptr %1165, align 1, !tbaa !18
  %1167 = getelementptr i8, ptr %1111, i64 28
  %1168 = load i8, ptr %1167, align 4, !tbaa !18
  %1169 = getelementptr i8, ptr %1111, i64 29
  %1170 = load i8, ptr %1169, align 1, !tbaa !18
  %1171 = getelementptr i8, ptr %1111, i64 30
  %1172 = load i8, ptr %1171, align 2, !tbaa !18
  %1173 = getelementptr i8, ptr %1111, i64 31
  %1174 = load i8, ptr %1173, align 1, !tbaa !18
  %1175 = shl nsw i64 %1109, 3
  %1176 = getelementptr inbounds nuw i8, ptr %178, i64 %1175
  %1177 = load i8, ptr %1176, align 8, !tbaa !18
  %1178 = zext i8 %1177 to i64
  %1179 = getelementptr inbounds nuw i8, ptr %1176, i64 1
  %1180 = load i8, ptr %1179, align 1, !tbaa !18
  %1181 = zext i8 %1180 to i64
  %1182 = shl nuw nsw i64 %1181, 8
  %1183 = or disjoint i64 %1182, %1178
  %1184 = getelementptr inbounds nuw i8, ptr %1176, i64 2
  %1185 = load i8, ptr %1184, align 2, !tbaa !18
  %1186 = zext i8 %1185 to i64
  %1187 = shl nuw nsw i64 %1186, 16
  %1188 = or disjoint i64 %1187, %1183
  %1189 = getelementptr inbounds nuw i8, ptr %1176, i64 3
  %1190 = load i8, ptr %1189, align 1, !tbaa !18
  %1191 = zext i8 %1190 to i64
  %1192 = shl nuw nsw i64 %1191, 24
  %1193 = or disjoint i64 %1192, %1188
  %1194 = getelementptr inbounds nuw i8, ptr %1176, i64 4
  %1195 = load i8, ptr %1194, align 4, !tbaa !18
  %1196 = zext i8 %1195 to i64
  %1197 = shl nuw nsw i64 %1196, 32
  %1198 = or disjoint i64 %1197, %1193
  %1199 = getelementptr inbounds nuw i8, ptr %1176, i64 5
  %1200 = load i8, ptr %1199, align 1, !tbaa !18
  %1201 = zext i8 %1200 to i64
  %1202 = shl nuw nsw i64 %1201, 40
  %1203 = or i64 %1202, %1198
  %1204 = getelementptr inbounds nuw i8, ptr %1176, i64 6
  %1205 = load i8, ptr %1204, align 2, !tbaa !18
  %1206 = zext i8 %1205 to i64
  %1207 = shl nuw nsw i64 %1206, 48
  %1208 = or i64 %1207, %1203
  %1209 = getelementptr inbounds nuw i8, ptr %1176, i64 7
  %1210 = load i8, ptr %1209, align 1, !tbaa !18
  %1211 = zext i8 %1210 to i64
  %1212 = shl nuw i64 %1211, 56
  %1213 = or i64 %1212, %1208
  %1214 = zext i8 %1160 to i64
  %1215 = zext i8 %1162 to i64
  %1216 = shl nuw nsw i64 %1215, 8
  %1217 = or disjoint i64 %1216, %1214
  %1218 = zext i8 %1164 to i64
  %1219 = shl nuw nsw i64 %1218, 16
  %1220 = or disjoint i64 %1219, %1217
  %1221 = zext i8 %1166 to i64
  %1222 = shl nuw nsw i64 %1221, 24
  %1223 = or disjoint i64 %1222, %1220
  %1224 = zext i8 %1168 to i64
  %1225 = shl nuw nsw i64 %1224, 32
  %1226 = or disjoint i64 %1225, %1223
  %1227 = zext i8 %1170 to i64
  %1228 = shl nuw nsw i64 %1227, 40
  %1229 = or i64 %1228, %1226
  %1230 = zext i8 %1172 to i64
  %1231 = shl nuw nsw i64 %1230, 48
  %1232 = or i64 %1231, %1229
  %1233 = zext i8 %1174 to i64
  %1234 = shl nuw i64 %1233, 56
  %1235 = or i64 %1234, %1232
  %1236 = zext i8 %1144 to i64
  %1237 = zext i8 %1146 to i64
  %1238 = shl nuw nsw i64 %1237, 8
  %1239 = or disjoint i64 %1238, %1236
  %1240 = zext i8 %1148 to i64
  %1241 = shl nuw nsw i64 %1240, 16
  %1242 = or disjoint i64 %1241, %1239
  %1243 = zext i8 %1150 to i64
  %1244 = shl nuw nsw i64 %1243, 24
  %1245 = or disjoint i64 %1244, %1242
  %1246 = zext i8 %1152 to i64
  %1247 = shl nuw nsw i64 %1246, 32
  %1248 = or disjoint i64 %1247, %1245
  %1249 = zext i8 %1154 to i64
  %1250 = shl nuw nsw i64 %1249, 40
  %1251 = or i64 %1250, %1248
  %1252 = zext i8 %1156 to i64
  %1253 = shl nuw nsw i64 %1252, 48
  %1254 = or i64 %1253, %1251
  %1255 = zext i8 %1158 to i64
  %1256 = shl nuw i64 %1255, 56
  %1257 = or i64 %1256, %1254
  %1258 = zext i8 %1128 to i64
  %1259 = zext i8 %1130 to i64
  %1260 = shl nuw nsw i64 %1259, 8
  %1261 = or disjoint i64 %1260, %1258
  %1262 = zext i8 %1132 to i64
  %1263 = shl nuw nsw i64 %1262, 16
  %1264 = or disjoint i64 %1263, %1261
  %1265 = zext i8 %1134 to i64
  %1266 = shl nuw nsw i64 %1265, 24
  %1267 = or disjoint i64 %1266, %1264
  %1268 = zext i8 %1136 to i64
  %1269 = shl nuw nsw i64 %1268, 32
  %1270 = or disjoint i64 %1269, %1267
  %1271 = zext i8 %1138 to i64
  %1272 = shl nuw nsw i64 %1271, 40
  %1273 = or i64 %1272, %1270
  %1274 = zext i8 %1140 to i64
  %1275 = shl nuw nsw i64 %1274, 48
  %1276 = or i64 %1275, %1273
  %1277 = zext i8 %1142 to i64
  %1278 = shl nuw i64 %1277, 56
  %1279 = or i64 %1278, %1276
  %1280 = zext i8 %1112 to i64
  %1281 = zext i8 %1114 to i64
  %1282 = shl nuw nsw i64 %1281, 8
  %1283 = or disjoint i64 %1282, %1280
  %1284 = zext i8 %1116 to i64
  %1285 = shl nuw nsw i64 %1284, 16
  %1286 = or disjoint i64 %1285, %1283
  %1287 = zext i8 %1118 to i64
  %1288 = shl nuw nsw i64 %1287, 24
  %1289 = or disjoint i64 %1288, %1286
  %1290 = zext i8 %1120 to i64
  %1291 = shl nuw nsw i64 %1290, 32
  %1292 = or disjoint i64 %1291, %1289
  %1293 = zext i8 %1122 to i64
  %1294 = shl nuw nsw i64 %1293, 40
  %1295 = or i64 %1294, %1292
  %1296 = zext i8 %1124 to i64
  %1297 = shl nuw nsw i64 %1296, 48
  %1298 = or i64 %1297, %1295
  %1299 = zext i8 %1126 to i64
  %1300 = shl nuw i64 %1299, 56
  %1301 = or i64 %1300, %1298
  %1302 = mul nsw i64 %1107, %1301
  %1303 = ashr i64 %1302, 16
  %1304 = mul nsw i64 %1085, %1279
  %1305 = ashr i64 %1304, 16
  %1306 = add nsw i64 %1305, %1303
  %1307 = mul nsw i64 %1063, %1257
  %1308 = ashr i64 %1307, 16
  %1309 = add nsw i64 %1306, %1308
  %1310 = mul nsw i64 %1041, %1235
  %1311 = ashr i64 %1310, 16
  %1312 = add nsw i64 %1309, %1311
  %1313 = add nsw i64 %1312, %1213
  %1314 = getelementptr inbounds nuw [8 x i8], ptr %35, i64 %1109
  store i64 %1313, ptr %1314, align 8, !tbaa !17
  %1315 = add nuw nsw i64 %1109, 1
  %1316 = icmp eq i64 %1315, 4
  br i1 %1316, label %1317, label %1108, !llvm.loop !19

1317:                                             ; preds = %1108
  %1318 = getelementptr i8, ptr %29, i64 %267
  %1319 = getelementptr i8, ptr %28, i64 %267
  %1320 = getelementptr i8, ptr %27, i64 %267
  call void @llvm.memcpy.p0.p0.i64(ptr noundef nonnull align 16 dereferenceable(32) %1320, ptr noundef nonnull align 16 dereferenceable(32) %33, i64 32, i1 false), !tbaa !17
  call void @llvm.memcpy.p0.p0.i64(ptr noundef nonnull align 16 dereferenceable(32) %1319, ptr noundef nonnull align 16 dereferenceable(32) %34, i64 32, i1 false), !tbaa !17
  call void @llvm.memcpy.p0.p0.i64(ptr noundef nonnull align 16 dereferenceable(32) %1318, ptr noundef nonnull align 16 dereferenceable(32) %35, i64 32, i1 false), !tbaa !17
  call void @llvm.lifetime.end.p0(ptr nonnull %35) #9
  call void @llvm.lifetime.end.p0(ptr nonnull %34) #9
  call void @llvm.lifetime.end.p0(ptr nonnull %33) #9
  %1321 = add nuw nsw i64 %266, 1
  %1322 = icmp eq i64 %1321, 3
  br i1 %1322, label %208, label %265, !llvm.loop !21

1323:                                             ; preds = %1330
  %1324 = getelementptr inbounds nuw i8, ptr %40, i64 8
  %1325 = getelementptr inbounds nuw i8, ptr %40, i64 16
  %1326 = getelementptr inbounds nuw i8, ptr %40, i64 24
  %1327 = getelementptr inbounds nuw i8, ptr %41, i64 8
  %1328 = getelementptr inbounds nuw i8, ptr %41, i64 16
  %1329 = getelementptr inbounds nuw i8, ptr %41, i64 24
  br label %1417

1330:                                             ; preds = %1330, %208
  %1331 = phi i64 [ 0, %208 ], [ %1415, %1330 ]
  call void @llvm.lifetime.start.p0(ptr nonnull %36) #9
  call void @llvm.lifetime.start.p0(ptr nonnull %37) #9
  %1332 = getelementptr inbounds nuw [32 x i8], ptr %27, i64 %1331
  %1333 = load i64, ptr %1332, align 16, !tbaa !17
  %1334 = getelementptr inbounds nuw i8, ptr %1332, i64 8
  %1335 = load i64, ptr %1334, align 8, !tbaa !17
  %1336 = getelementptr inbounds nuw i8, ptr %1332, i64 16
  %1337 = load i64, ptr %1336, align 16, !tbaa !17
  %1338 = getelementptr inbounds nuw i8, ptr %1332, i64 24
  %1339 = load i64, ptr %1338, align 8, !tbaa !17
  %1340 = mul nsw i64 %1333, %220
  %1341 = and i64 %1340, -65536
  %1342 = mul nsw i64 %1335, %222
  %1343 = and i64 %1342, -65536
  %1344 = add i64 %1343, %1341
  %1345 = mul nsw i64 %1337, %224
  %1346 = and i64 %1345, -65536
  %1347 = add i64 %1344, %1346
  %1348 = mul nsw i64 %1339, %226
  %1349 = add i64 %1347, %1348
  %1350 = and i64 %1349, -65536
  %1351 = sdiv i64 %1350, 131072
  store i64 %1351, ptr %36, align 16, !tbaa !17
  %1352 = mul nsw i64 %1333, %228
  %1353 = and i64 %1352, -65536
  %1354 = mul nsw i64 %1335, %230
  %1355 = and i64 %1354, -65536
  %1356 = add i64 %1355, %1353
  %1357 = mul nsw i64 %1337, %232
  %1358 = and i64 %1357, -65536
  %1359 = add i64 %1356, %1358
  %1360 = mul nsw i64 %1339, %234
  %1361 = add i64 %1359, %1360
  %1362 = and i64 %1361, -65536
  %1363 = sdiv i64 %1362, 131072
  store i64 %1363, ptr %235, align 8, !tbaa !17
  %1364 = mul nsw i64 %1333, %237
  %1365 = and i64 %1364, -65536
  %1366 = mul nsw i64 %1335, %239
  %1367 = and i64 %1366, -65536
  %1368 = add i64 %1367, %1365
  %1369 = mul nsw i64 %1337, %241
  %1370 = and i64 %1369, -65536
  %1371 = add i64 %1368, %1370
  %1372 = mul nsw i64 %1339, %243
  %1373 = add i64 %1371, %1372
  %1374 = and i64 %1373, -65536
  %1375 = sdiv i64 %1374, 131072
  store i64 %1375, ptr %244, align 16, !tbaa !17
  call void @llvm.lifetime.start.p0(ptr nonnull %38) #9
  store ptr %36, ptr %38, align 8, !tbaa !9
  store i64 3, ptr %209, align 8, !tbaa !14
  store i64 8, ptr %210, align 8, !tbaa !15
  store i64 8, ptr %211, align 8, !tbaa !16
  call void @llvm.lifetime.start.p0(ptr nonnull %39) #9
  store ptr %37, ptr %39, align 8, !tbaa !9
  store i64 3, ptr %212, align 8, !tbaa !14
  store i64 8, ptr %213, align 8, !tbaa !15
  store i64 8, ptr %214, align 8, !tbaa !16
  call fastcc void @softmax(ptr noundef %38, ptr noundef %39)
  %1376 = getelementptr inbounds nuw [32 x i8], ptr %30, i64 %1331
  %1377 = load i64, ptr %37, align 16, !tbaa !17
  %1378 = mul nsw i64 %1377, %215
  %1379 = ashr i64 %1378, 16
  %1380 = load i64, ptr %245, align 8, !tbaa !17
  %1381 = mul nsw i64 %1380, %217
  %1382 = ashr i64 %1381, 16
  %1383 = add nsw i64 %1382, %1379
  %1384 = load i64, ptr %246, align 16, !tbaa !17
  %1385 = mul nsw i64 %1384, %219
  %1386 = ashr i64 %1385, 16
  %1387 = add nsw i64 %1383, %1386
  store i64 %1387, ptr %1376, align 16, !tbaa !17
  %1388 = mul nsw i64 %1377, %248
  %1389 = ashr i64 %1388, 16
  %1390 = mul nsw i64 %1380, %250
  %1391 = ashr i64 %1390, 16
  %1392 = add nsw i64 %1391, %1389
  %1393 = mul nsw i64 %1384, %252
  %1394 = ashr i64 %1393, 16
  %1395 = add nsw i64 %1392, %1394
  %1396 = getelementptr inbounds nuw i8, ptr %1376, i64 8
  store i64 %1395, ptr %1396, align 8, !tbaa !17
  %1397 = mul nsw i64 %1377, %254
  %1398 = ashr i64 %1397, 16
  %1399 = mul nsw i64 %1380, %256
  %1400 = ashr i64 %1399, 16
  %1401 = add nsw i64 %1400, %1398
  %1402 = mul nsw i64 %1384, %258
  %1403 = ashr i64 %1402, 16
  %1404 = add nsw i64 %1401, %1403
  %1405 = getelementptr inbounds nuw i8, ptr %1376, i64 16
  store i64 %1404, ptr %1405, align 16, !tbaa !17
  %1406 = mul nsw i64 %1377, %260
  %1407 = ashr i64 %1406, 16
  %1408 = mul nsw i64 %1380, %262
  %1409 = ashr i64 %1408, 16
  %1410 = add nsw i64 %1409, %1407
  %1411 = mul nsw i64 %1384, %264
  %1412 = ashr i64 %1411, 16
  %1413 = add nsw i64 %1410, %1412
  %1414 = getelementptr inbounds nuw i8, ptr %1376, i64 24
  store i64 %1413, ptr %1414, align 8, !tbaa !17
  call void @llvm.lifetime.end.p0(ptr nonnull %39) #9
  call void @llvm.lifetime.end.p0(ptr nonnull %38) #9
  call void @llvm.lifetime.end.p0(ptr nonnull %37) #9
  call void @llvm.lifetime.end.p0(ptr nonnull %36) #9
  %1415 = add nuw nsw i64 %1331, 1
  %1416 = icmp eq i64 %1415, 3
  br i1 %1416, label %1323, label %1330, !llvm.loop !22

1417:                                             ; preds = %1637, %1323
  %1418 = phi i64 [ 0, %1323 ], [ %1902, %1637 ]
  %1419 = getelementptr inbounds nuw [32 x i8], ptr %30, i64 %1418
  %1420 = getelementptr inbounds nuw [32 x i8], ptr %32, i64 %1418
  %1421 = getelementptr inbounds nuw i8, ptr %1419, i64 8
  %1422 = getelementptr inbounds nuw i8, ptr %1419, i64 16
  %1423 = getelementptr inbounds nuw i8, ptr %1419, i64 24
  %1424 = load i64, ptr %1419, align 16
  %1425 = load i64, ptr %1421, align 8
  %1426 = load i64, ptr %1422, align 16
  %1427 = load i64, ptr %1423, align 8
  br label %1428

1428:                                             ; preds = %1417, %1428
  %1429 = phi i64 [ 0, %1417 ], [ %1635, %1428 ]
  %1430 = shl i64 %1429, 5
  %1431 = getelementptr i8, ptr %57, i64 %1430
  %1432 = load i8, ptr %1431, align 16, !tbaa !18
  %1433 = getelementptr inbounds nuw i8, ptr %1431, i64 1
  %1434 = load i8, ptr %1433, align 1, !tbaa !18
  %1435 = getelementptr inbounds nuw i8, ptr %1431, i64 2
  %1436 = load i8, ptr %1435, align 2, !tbaa !18
  %1437 = getelementptr inbounds nuw i8, ptr %1431, i64 3
  %1438 = load i8, ptr %1437, align 1, !tbaa !18
  %1439 = getelementptr inbounds nuw i8, ptr %1431, i64 4
  %1440 = load i8, ptr %1439, align 4, !tbaa !18
  %1441 = getelementptr inbounds nuw i8, ptr %1431, i64 5
  %1442 = load i8, ptr %1441, align 1, !tbaa !18
  %1443 = getelementptr inbounds nuw i8, ptr %1431, i64 6
  %1444 = load i8, ptr %1443, align 2, !tbaa !18
  %1445 = getelementptr inbounds nuw i8, ptr %1431, i64 7
  %1446 = load i8, ptr %1445, align 1, !tbaa !18
  %1447 = getelementptr i8, ptr %1431, i64 8
  %1448 = load i8, ptr %1447, align 8, !tbaa !18
  %1449 = getelementptr i8, ptr %1431, i64 9
  %1450 = load i8, ptr %1449, align 1, !tbaa !18
  %1451 = getelementptr i8, ptr %1431, i64 10
  %1452 = load i8, ptr %1451, align 2, !tbaa !18
  %1453 = getelementptr i8, ptr %1431, i64 11
  %1454 = load i8, ptr %1453, align 1, !tbaa !18
  %1455 = getelementptr i8, ptr %1431, i64 12
  %1456 = load i8, ptr %1455, align 4, !tbaa !18
  %1457 = getelementptr i8, ptr %1431, i64 13
  %1458 = load i8, ptr %1457, align 1, !tbaa !18
  %1459 = getelementptr i8, ptr %1431, i64 14
  %1460 = load i8, ptr %1459, align 2, !tbaa !18
  %1461 = getelementptr i8, ptr %1431, i64 15
  %1462 = load i8, ptr %1461, align 1, !tbaa !18
  %1463 = getelementptr i8, ptr %1431, i64 16
  %1464 = load i8, ptr %1463, align 16, !tbaa !18
  %1465 = getelementptr i8, ptr %1431, i64 17
  %1466 = load i8, ptr %1465, align 1, !tbaa !18
  %1467 = getelementptr i8, ptr %1431, i64 18
  %1468 = load i8, ptr %1467, align 2, !tbaa !18
  %1469 = getelementptr i8, ptr %1431, i64 19
  %1470 = load i8, ptr %1469, align 1, !tbaa !18
  %1471 = getelementptr i8, ptr %1431, i64 20
  %1472 = load i8, ptr %1471, align 4, !tbaa !18
  %1473 = getelementptr i8, ptr %1431, i64 21
  %1474 = load i8, ptr %1473, align 1, !tbaa !18
  %1475 = getelementptr i8, ptr %1431, i64 22
  %1476 = load i8, ptr %1475, align 2, !tbaa !18
  %1477 = getelementptr i8, ptr %1431, i64 23
  %1478 = load i8, ptr %1477, align 1, !tbaa !18
  %1479 = getelementptr i8, ptr %1431, i64 24
  %1480 = load i8, ptr %1479, align 8, !tbaa !18
  %1481 = getelementptr i8, ptr %1431, i64 25
  %1482 = load i8, ptr %1481, align 1, !tbaa !18
  %1483 = getelementptr i8, ptr %1431, i64 26
  %1484 = load i8, ptr %1483, align 2, !tbaa !18
  %1485 = getelementptr i8, ptr %1431, i64 27
  %1486 = load i8, ptr %1485, align 1, !tbaa !18
  %1487 = getelementptr i8, ptr %1431, i64 28
  %1488 = load i8, ptr %1487, align 4, !tbaa !18
  %1489 = getelementptr i8, ptr %1431, i64 29
  %1490 = load i8, ptr %1489, align 1, !tbaa !18
  %1491 = getelementptr i8, ptr %1431, i64 30
  %1492 = load i8, ptr %1491, align 2, !tbaa !18
  %1493 = getelementptr i8, ptr %1431, i64 31
  %1494 = load i8, ptr %1493, align 1, !tbaa !18
  %1495 = shl nsw i64 %1429, 3
  %1496 = getelementptr inbounds nuw i8, ptr %58, i64 %1495
  %1497 = load i8, ptr %1496, align 8, !tbaa !18
  %1498 = zext i8 %1497 to i64
  %1499 = getelementptr inbounds nuw i8, ptr %1496, i64 1
  %1500 = load i8, ptr %1499, align 1, !tbaa !18
  %1501 = zext i8 %1500 to i64
  %1502 = shl nuw nsw i64 %1501, 8
  %1503 = or disjoint i64 %1502, %1498
  %1504 = getelementptr inbounds nuw i8, ptr %1496, i64 2
  %1505 = load i8, ptr %1504, align 2, !tbaa !18
  %1506 = zext i8 %1505 to i64
  %1507 = shl nuw nsw i64 %1506, 16
  %1508 = or disjoint i64 %1507, %1503
  %1509 = getelementptr inbounds nuw i8, ptr %1496, i64 3
  %1510 = load i8, ptr %1509, align 1, !tbaa !18
  %1511 = zext i8 %1510 to i64
  %1512 = shl nuw nsw i64 %1511, 24
  %1513 = or disjoint i64 %1512, %1508
  %1514 = getelementptr inbounds nuw i8, ptr %1496, i64 4
  %1515 = load i8, ptr %1514, align 4, !tbaa !18
  %1516 = zext i8 %1515 to i64
  %1517 = shl nuw nsw i64 %1516, 32
  %1518 = or disjoint i64 %1517, %1513
  %1519 = getelementptr inbounds nuw i8, ptr %1496, i64 5
  %1520 = load i8, ptr %1519, align 1, !tbaa !18
  %1521 = zext i8 %1520 to i64
  %1522 = shl nuw nsw i64 %1521, 40
  %1523 = or i64 %1522, %1518
  %1524 = getelementptr inbounds nuw i8, ptr %1496, i64 6
  %1525 = load i8, ptr %1524, align 2, !tbaa !18
  %1526 = zext i8 %1525 to i64
  %1527 = shl nuw nsw i64 %1526, 48
  %1528 = or i64 %1527, %1523
  %1529 = getelementptr inbounds nuw i8, ptr %1496, i64 7
  %1530 = load i8, ptr %1529, align 1, !tbaa !18
  %1531 = zext i8 %1530 to i64
  %1532 = shl nuw i64 %1531, 56
  %1533 = or i64 %1532, %1528
  %1534 = zext i8 %1480 to i64
  %1535 = zext i8 %1482 to i64
  %1536 = shl nuw nsw i64 %1535, 8
  %1537 = or disjoint i64 %1536, %1534
  %1538 = zext i8 %1484 to i64
  %1539 = shl nuw nsw i64 %1538, 16
  %1540 = or disjoint i64 %1539, %1537
  %1541 = zext i8 %1486 to i64
  %1542 = shl nuw nsw i64 %1541, 24
  %1543 = or disjoint i64 %1542, %1540
  %1544 = zext i8 %1488 to i64
  %1545 = shl nuw nsw i64 %1544, 32
  %1546 = or disjoint i64 %1545, %1543
  %1547 = zext i8 %1490 to i64
  %1548 = shl nuw nsw i64 %1547, 40
  %1549 = or i64 %1548, %1546
  %1550 = zext i8 %1492 to i64
  %1551 = shl nuw nsw i64 %1550, 48
  %1552 = or i64 %1551, %1549
  %1553 = zext i8 %1494 to i64
  %1554 = shl nuw i64 %1553, 56
  %1555 = or i64 %1554, %1552
  %1556 = zext i8 %1464 to i64
  %1557 = zext i8 %1466 to i64
  %1558 = shl nuw nsw i64 %1557, 8
  %1559 = or disjoint i64 %1558, %1556
  %1560 = zext i8 %1468 to i64
  %1561 = shl nuw nsw i64 %1560, 16
  %1562 = or disjoint i64 %1561, %1559
  %1563 = zext i8 %1470 to i64
  %1564 = shl nuw nsw i64 %1563, 24
  %1565 = or disjoint i64 %1564, %1562
  %1566 = zext i8 %1472 to i64
  %1567 = shl nuw nsw i64 %1566, 32
  %1568 = or disjoint i64 %1567, %1565
  %1569 = zext i8 %1474 to i64
  %1570 = shl nuw nsw i64 %1569, 40
  %1571 = or i64 %1570, %1568
  %1572 = zext i8 %1476 to i64
  %1573 = shl nuw nsw i64 %1572, 48
  %1574 = or i64 %1573, %1571
  %1575 = zext i8 %1478 to i64
  %1576 = shl nuw i64 %1575, 56
  %1577 = or i64 %1576, %1574
  %1578 = zext i8 %1448 to i64
  %1579 = zext i8 %1450 to i64
  %1580 = shl nuw nsw i64 %1579, 8
  %1581 = or disjoint i64 %1580, %1578
  %1582 = zext i8 %1452 to i64
  %1583 = shl nuw nsw i64 %1582, 16
  %1584 = or disjoint i64 %1583, %1581
  %1585 = zext i8 %1454 to i64
  %1586 = shl nuw nsw i64 %1585, 24
  %1587 = or disjoint i64 %1586, %1584
  %1588 = zext i8 %1456 to i64
  %1589 = shl nuw nsw i64 %1588, 32
  %1590 = or disjoint i64 %1589, %1587
  %1591 = zext i8 %1458 to i64
  %1592 = shl nuw nsw i64 %1591, 40
  %1593 = or i64 %1592, %1590
  %1594 = zext i8 %1460 to i64
  %1595 = shl nuw nsw i64 %1594, 48
  %1596 = or i64 %1595, %1593
  %1597 = zext i8 %1462 to i64
  %1598 = shl nuw i64 %1597, 56
  %1599 = or i64 %1598, %1596
  %1600 = zext i8 %1432 to i64
  %1601 = zext i8 %1434 to i64
  %1602 = shl nuw nsw i64 %1601, 8
  %1603 = or disjoint i64 %1602, %1600
  %1604 = zext i8 %1436 to i64
  %1605 = shl nuw nsw i64 %1604, 16
  %1606 = or disjoint i64 %1605, %1603
  %1607 = zext i8 %1438 to i64
  %1608 = shl nuw nsw i64 %1607, 24
  %1609 = or disjoint i64 %1608, %1606
  %1610 = zext i8 %1440 to i64
  %1611 = shl nuw nsw i64 %1610, 32
  %1612 = or disjoint i64 %1611, %1609
  %1613 = zext i8 %1442 to i64
  %1614 = shl nuw nsw i64 %1613, 40
  %1615 = or i64 %1614, %1612
  %1616 = zext i8 %1444 to i64
  %1617 = shl nuw nsw i64 %1616, 48
  %1618 = or i64 %1617, %1615
  %1619 = zext i8 %1446 to i64
  %1620 = shl nuw i64 %1619, 56
  %1621 = or i64 %1620, %1618
  %1622 = mul nsw i64 %1424, %1621
  %1623 = ashr i64 %1622, 16
  %1624 = mul nsw i64 %1425, %1599
  %1625 = ashr i64 %1624, 16
  %1626 = add nsw i64 %1625, %1623
  %1627 = mul nsw i64 %1426, %1577
  %1628 = ashr i64 %1627, 16
  %1629 = add nsw i64 %1626, %1628
  %1630 = mul nsw i64 %1427, %1555
  %1631 = ashr i64 %1630, 16
  %1632 = add nsw i64 %1629, %1631
  %1633 = add nsw i64 %1632, %1533
  %1634 = getelementptr inbounds nuw [8 x i8], ptr %1420, i64 %1429
  store i64 %1633, ptr %1634, align 8, !tbaa !17
  %1635 = add nuw nsw i64 %1429, 1
  %1636 = icmp eq i64 %1635, 4
  br i1 %1636, label %1637, label %1428, !llvm.loop !19

1637:                                             ; preds = %1428
  %1638 = shl nuw nsw i64 %1418, 5
  %1639 = getelementptr i8, ptr %54, i64 %1638
  %1640 = load i8, ptr %1639, align 16, !tbaa !18
  %1641 = zext i8 %1640 to i64
  %1642 = getelementptr inbounds nuw i8, ptr %1639, i64 1
  %1643 = load i8, ptr %1642, align 1, !tbaa !18
  %1644 = zext i8 %1643 to i64
  %1645 = shl nuw nsw i64 %1644, 8
  %1646 = or disjoint i64 %1645, %1641
  %1647 = getelementptr inbounds nuw i8, ptr %1639, i64 2
  %1648 = load i8, ptr %1647, align 2, !tbaa !18
  %1649 = zext i8 %1648 to i64
  %1650 = shl nuw nsw i64 %1649, 16
  %1651 = or disjoint i64 %1650, %1646
  %1652 = getelementptr inbounds nuw i8, ptr %1639, i64 3
  %1653 = load i8, ptr %1652, align 1, !tbaa !18
  %1654 = zext i8 %1653 to i64
  %1655 = shl nuw nsw i64 %1654, 24
  %1656 = or disjoint i64 %1655, %1651
  %1657 = getelementptr inbounds nuw i8, ptr %1639, i64 4
  %1658 = load i8, ptr %1657, align 4, !tbaa !18
  %1659 = zext i8 %1658 to i64
  %1660 = shl nuw nsw i64 %1659, 32
  %1661 = or disjoint i64 %1660, %1656
  %1662 = getelementptr inbounds nuw i8, ptr %1639, i64 5
  %1663 = load i8, ptr %1662, align 1, !tbaa !18
  %1664 = zext i8 %1663 to i64
  %1665 = shl nuw nsw i64 %1664, 40
  %1666 = or i64 %1665, %1661
  %1667 = getelementptr inbounds nuw i8, ptr %1639, i64 6
  %1668 = load i8, ptr %1667, align 2, !tbaa !18
  %1669 = zext i8 %1668 to i64
  %1670 = shl nuw nsw i64 %1669, 48
  %1671 = or i64 %1670, %1666
  %1672 = getelementptr inbounds nuw i8, ptr %1639, i64 7
  %1673 = load i8, ptr %1672, align 1, !tbaa !18
  %1674 = zext i8 %1673 to i64
  %1675 = shl nuw i64 %1674, 56
  %1676 = or i64 %1675, %1671
  %1677 = getelementptr inbounds nuw [32 x i8], ptr %31, i64 %1418
  %1678 = load i64, ptr %1420, align 16, !tbaa !17
  %1679 = add nsw i64 %1678, %1676
  store i64 %1679, ptr %1677, align 16, !tbaa !17
  %1680 = getelementptr i8, ptr %1639, i64 8
  %1681 = load i8, ptr %1680, align 8, !tbaa !18
  %1682 = zext i8 %1681 to i64
  %1683 = getelementptr i8, ptr %1639, i64 9
  %1684 = load i8, ptr %1683, align 1, !tbaa !18
  %1685 = zext i8 %1684 to i64
  %1686 = shl nuw nsw i64 %1685, 8
  %1687 = or disjoint i64 %1686, %1682
  %1688 = getelementptr i8, ptr %1639, i64 10
  %1689 = load i8, ptr %1688, align 2, !tbaa !18
  %1690 = zext i8 %1689 to i64
  %1691 = shl nuw nsw i64 %1690, 16
  %1692 = or disjoint i64 %1691, %1687
  %1693 = getelementptr i8, ptr %1639, i64 11
  %1694 = load i8, ptr %1693, align 1, !tbaa !18
  %1695 = zext i8 %1694 to i64
  %1696 = shl nuw nsw i64 %1695, 24
  %1697 = or disjoint i64 %1696, %1692
  %1698 = getelementptr i8, ptr %1639, i64 12
  %1699 = load i8, ptr %1698, align 4, !tbaa !18
  %1700 = zext i8 %1699 to i64
  %1701 = shl nuw nsw i64 %1700, 32
  %1702 = or disjoint i64 %1701, %1697
  %1703 = getelementptr i8, ptr %1639, i64 13
  %1704 = load i8, ptr %1703, align 1, !tbaa !18
  %1705 = zext i8 %1704 to i64
  %1706 = shl nuw nsw i64 %1705, 40
  %1707 = or i64 %1706, %1702
  %1708 = getelementptr i8, ptr %1639, i64 14
  %1709 = load i8, ptr %1708, align 2, !tbaa !18
  %1710 = zext i8 %1709 to i64
  %1711 = shl nuw nsw i64 %1710, 48
  %1712 = or i64 %1711, %1707
  %1713 = getelementptr i8, ptr %1639, i64 15
  %1714 = load i8, ptr %1713, align 1, !tbaa !18
  %1715 = zext i8 %1714 to i64
  %1716 = shl nuw i64 %1715, 56
  %1717 = or i64 %1716, %1712
  %1718 = getelementptr inbounds nuw i8, ptr %1420, i64 8
  %1719 = load i64, ptr %1718, align 8, !tbaa !17
  %1720 = add nsw i64 %1719, %1717
  %1721 = getelementptr inbounds nuw i8, ptr %1677, i64 8
  store i64 %1720, ptr %1721, align 8, !tbaa !17
  %1722 = getelementptr i8, ptr %1639, i64 16
  %1723 = load i8, ptr %1722, align 16, !tbaa !18
  %1724 = zext i8 %1723 to i64
  %1725 = getelementptr i8, ptr %1639, i64 17
  %1726 = load i8, ptr %1725, align 1, !tbaa !18
  %1727 = zext i8 %1726 to i64
  %1728 = shl nuw nsw i64 %1727, 8
  %1729 = or disjoint i64 %1728, %1724
  %1730 = getelementptr i8, ptr %1639, i64 18
  %1731 = load i8, ptr %1730, align 2, !tbaa !18
  %1732 = zext i8 %1731 to i64
  %1733 = shl nuw nsw i64 %1732, 16
  %1734 = or disjoint i64 %1733, %1729
  %1735 = getelementptr i8, ptr %1639, i64 19
  %1736 = load i8, ptr %1735, align 1, !tbaa !18
  %1737 = zext i8 %1736 to i64
  %1738 = shl nuw nsw i64 %1737, 24
  %1739 = or disjoint i64 %1738, %1734
  %1740 = getelementptr i8, ptr %1639, i64 20
  %1741 = load i8, ptr %1740, align 4, !tbaa !18
  %1742 = zext i8 %1741 to i64
  %1743 = shl nuw nsw i64 %1742, 32
  %1744 = or disjoint i64 %1743, %1739
  %1745 = getelementptr i8, ptr %1639, i64 21
  %1746 = load i8, ptr %1745, align 1, !tbaa !18
  %1747 = zext i8 %1746 to i64
  %1748 = shl nuw nsw i64 %1747, 40
  %1749 = or i64 %1748, %1744
  %1750 = getelementptr i8, ptr %1639, i64 22
  %1751 = load i8, ptr %1750, align 2, !tbaa !18
  %1752 = zext i8 %1751 to i64
  %1753 = shl nuw nsw i64 %1752, 48
  %1754 = or i64 %1753, %1749
  %1755 = getelementptr i8, ptr %1639, i64 23
  %1756 = load i8, ptr %1755, align 1, !tbaa !18
  %1757 = zext i8 %1756 to i64
  %1758 = shl nuw i64 %1757, 56
  %1759 = or i64 %1758, %1754
  %1760 = getelementptr inbounds nuw i8, ptr %1420, i64 16
  %1761 = load i64, ptr %1760, align 16, !tbaa !17
  %1762 = add nsw i64 %1761, %1759
  %1763 = getelementptr inbounds nuw i8, ptr %1677, i64 16
  store i64 %1762, ptr %1763, align 16, !tbaa !17
  %1764 = getelementptr i8, ptr %1639, i64 24
  %1765 = load i8, ptr %1764, align 8, !tbaa !18
  %1766 = zext i8 %1765 to i64
  %1767 = getelementptr i8, ptr %1639, i64 25
  %1768 = load i8, ptr %1767, align 1, !tbaa !18
  %1769 = zext i8 %1768 to i64
  %1770 = shl nuw nsw i64 %1769, 8
  %1771 = or disjoint i64 %1770, %1766
  %1772 = getelementptr i8, ptr %1639, i64 26
  %1773 = load i8, ptr %1772, align 2, !tbaa !18
  %1774 = zext i8 %1773 to i64
  %1775 = shl nuw nsw i64 %1774, 16
  %1776 = or disjoint i64 %1775, %1771
  %1777 = getelementptr i8, ptr %1639, i64 27
  %1778 = load i8, ptr %1777, align 1, !tbaa !18
  %1779 = zext i8 %1778 to i64
  %1780 = shl nuw nsw i64 %1779, 24
  %1781 = or disjoint i64 %1780, %1776
  %1782 = getelementptr i8, ptr %1639, i64 28
  %1783 = load i8, ptr %1782, align 4, !tbaa !18
  %1784 = zext i8 %1783 to i64
  %1785 = shl nuw nsw i64 %1784, 32
  %1786 = or disjoint i64 %1785, %1781
  %1787 = getelementptr i8, ptr %1639, i64 29
  %1788 = load i8, ptr %1787, align 1, !tbaa !18
  %1789 = zext i8 %1788 to i64
  %1790 = shl nuw nsw i64 %1789, 40
  %1791 = or i64 %1790, %1786
  %1792 = getelementptr i8, ptr %1639, i64 30
  %1793 = load i8, ptr %1792, align 2, !tbaa !18
  %1794 = zext i8 %1793 to i64
  %1795 = shl nuw nsw i64 %1794, 48
  %1796 = or i64 %1795, %1791
  %1797 = getelementptr i8, ptr %1639, i64 31
  %1798 = load i8, ptr %1797, align 1, !tbaa !18
  %1799 = zext i8 %1798 to i64
  %1800 = shl nuw i64 %1799, 56
  %1801 = or i64 %1800, %1796
  %1802 = getelementptr inbounds nuw i8, ptr %1420, i64 24
  %1803 = load i64, ptr %1802, align 8, !tbaa !17
  %1804 = add nsw i64 %1803, %1801
  %1805 = getelementptr inbounds nuw i8, ptr %1677, i64 24
  store i64 %1804, ptr %1805, align 8, !tbaa !17
  call void @llvm.lifetime.start.p0(ptr nonnull %40) #9
  store ptr %1677, ptr %40, align 8, !tbaa !9
  store i64 4, ptr %1324, align 8, !tbaa !14
  store i64 8, ptr %1325, align 8, !tbaa !15
  store i64 8, ptr %1326, align 8, !tbaa !16
  call void @llvm.lifetime.start.p0(ptr nonnull %41) #9
  store ptr %1419, ptr %41, align 8, !tbaa !9
  store i64 4, ptr %1327, align 8, !tbaa !14
  store i64 8, ptr %1328, align 8, !tbaa !15
  store i64 8, ptr %1329, align 8, !tbaa !16
  call fastcc void @layernorm(ptr noundef %40, i64 noundef 4, ptr noundef nonnull readonly %62, ptr noundef nonnull readonly %63, ptr noundef %41)
  %1806 = load i64, ptr %1419, align 16, !tbaa !17
  %1807 = getelementptr i8, ptr %61, i64 %1638
  %1808 = trunc i64 %1806 to i8
  store i8 %1808, ptr %1807, align 16, !tbaa !18
  %1809 = lshr i64 %1806, 8
  %1810 = trunc i64 %1809 to i8
  %1811 = getelementptr inbounds nuw i8, ptr %1807, i64 1
  store i8 %1810, ptr %1811, align 1, !tbaa !18
  %1812 = lshr i64 %1806, 16
  %1813 = trunc i64 %1812 to i8
  %1814 = getelementptr inbounds nuw i8, ptr %1807, i64 2
  store i8 %1813, ptr %1814, align 2, !tbaa !18
  %1815 = lshr i64 %1806, 24
  %1816 = trunc i64 %1815 to i8
  %1817 = getelementptr inbounds nuw i8, ptr %1807, i64 3
  store i8 %1816, ptr %1817, align 1, !tbaa !18
  %1818 = lshr i64 %1806, 32
  %1819 = trunc i64 %1818 to i8
  %1820 = getelementptr inbounds nuw i8, ptr %1807, i64 4
  store i8 %1819, ptr %1820, align 4, !tbaa !18
  %1821 = lshr i64 %1806, 40
  %1822 = trunc i64 %1821 to i8
  %1823 = getelementptr inbounds nuw i8, ptr %1807, i64 5
  store i8 %1822, ptr %1823, align 1, !tbaa !18
  %1824 = lshr i64 %1806, 48
  %1825 = trunc i64 %1824 to i8
  %1826 = getelementptr inbounds nuw i8, ptr %1807, i64 6
  store i8 %1825, ptr %1826, align 2, !tbaa !18
  %1827 = lshr i64 %1806, 56
  %1828 = trunc nuw i64 %1827 to i8
  %1829 = getelementptr inbounds nuw i8, ptr %1807, i64 7
  store i8 %1828, ptr %1829, align 1, !tbaa !18
  %1830 = load i64, ptr %1421, align 8, !tbaa !17
  %1831 = getelementptr i8, ptr %1807, i64 8
  %1832 = trunc i64 %1830 to i8
  store i8 %1832, ptr %1831, align 8, !tbaa !18
  %1833 = lshr i64 %1830, 8
  %1834 = trunc i64 %1833 to i8
  %1835 = getelementptr i8, ptr %1807, i64 9
  store i8 %1834, ptr %1835, align 1, !tbaa !18
  %1836 = lshr i64 %1830, 16
  %1837 = trunc i64 %1836 to i8
  %1838 = getelementptr i8, ptr %1807, i64 10
  store i8 %1837, ptr %1838, align 2, !tbaa !18
  %1839 = lshr i64 %1830, 24
  %1840 = trunc i64 %1839 to i8
  %1841 = getelementptr i8, ptr %1807, i64 11
  store i8 %1840, ptr %1841, align 1, !tbaa !18
  %1842 = lshr i64 %1830, 32
  %1843 = trunc i64 %1842 to i8
  %1844 = getelementptr i8, ptr %1807, i64 12
  store i8 %1843, ptr %1844, align 4, !tbaa !18
  %1845 = lshr i64 %1830, 40
  %1846 = trunc i64 %1845 to i8
  %1847 = getelementptr i8, ptr %1807, i64 13
  store i8 %1846, ptr %1847, align 1, !tbaa !18
  %1848 = lshr i64 %1830, 48
  %1849 = trunc i64 %1848 to i8
  %1850 = getelementptr i8, ptr %1807, i64 14
  store i8 %1849, ptr %1850, align 2, !tbaa !18
  %1851 = lshr i64 %1830, 56
  %1852 = trunc nuw i64 %1851 to i8
  %1853 = getelementptr i8, ptr %1807, i64 15
  store i8 %1852, ptr %1853, align 1, !tbaa !18
  %1854 = load i64, ptr %1422, align 16, !tbaa !17
  %1855 = getelementptr i8, ptr %1807, i64 16
  %1856 = trunc i64 %1854 to i8
  store i8 %1856, ptr %1855, align 16, !tbaa !18
  %1857 = lshr i64 %1854, 8
  %1858 = trunc i64 %1857 to i8
  %1859 = getelementptr i8, ptr %1807, i64 17
  store i8 %1858, ptr %1859, align 1, !tbaa !18
  %1860 = lshr i64 %1854, 16
  %1861 = trunc i64 %1860 to i8
  %1862 = getelementptr i8, ptr %1807, i64 18
  store i8 %1861, ptr %1862, align 2, !tbaa !18
  %1863 = lshr i64 %1854, 24
  %1864 = trunc i64 %1863 to i8
  %1865 = getelementptr i8, ptr %1807, i64 19
  store i8 %1864, ptr %1865, align 1, !tbaa !18
  %1866 = lshr i64 %1854, 32
  %1867 = trunc i64 %1866 to i8
  %1868 = getelementptr i8, ptr %1807, i64 20
  store i8 %1867, ptr %1868, align 4, !tbaa !18
  %1869 = lshr i64 %1854, 40
  %1870 = trunc i64 %1869 to i8
  %1871 = getelementptr i8, ptr %1807, i64 21
  store i8 %1870, ptr %1871, align 1, !tbaa !18
  %1872 = lshr i64 %1854, 48
  %1873 = trunc i64 %1872 to i8
  %1874 = getelementptr i8, ptr %1807, i64 22
  store i8 %1873, ptr %1874, align 2, !tbaa !18
  %1875 = lshr i64 %1854, 56
  %1876 = trunc nuw i64 %1875 to i8
  %1877 = getelementptr i8, ptr %1807, i64 23
  store i8 %1876, ptr %1877, align 1, !tbaa !18
  %1878 = load i64, ptr %1423, align 8, !tbaa !17
  %1879 = getelementptr i8, ptr %1807, i64 24
  %1880 = trunc i64 %1878 to i8
  store i8 %1880, ptr %1879, align 8, !tbaa !18
  %1881 = lshr i64 %1878, 8
  %1882 = trunc i64 %1881 to i8
  %1883 = getelementptr i8, ptr %1807, i64 25
  store i8 %1882, ptr %1883, align 1, !tbaa !18
  %1884 = lshr i64 %1878, 16
  %1885 = trunc i64 %1884 to i8
  %1886 = getelementptr i8, ptr %1807, i64 26
  store i8 %1885, ptr %1886, align 2, !tbaa !18
  %1887 = lshr i64 %1878, 24
  %1888 = trunc i64 %1887 to i8
  %1889 = getelementptr i8, ptr %1807, i64 27
  store i8 %1888, ptr %1889, align 1, !tbaa !18
  %1890 = lshr i64 %1878, 32
  %1891 = trunc i64 %1890 to i8
  %1892 = getelementptr i8, ptr %1807, i64 28
  store i8 %1891, ptr %1892, align 4, !tbaa !18
  %1893 = lshr i64 %1878, 40
  %1894 = trunc i64 %1893 to i8
  %1895 = getelementptr i8, ptr %1807, i64 29
  store i8 %1894, ptr %1895, align 1, !tbaa !18
  %1896 = lshr i64 %1878, 48
  %1897 = trunc i64 %1896 to i8
  %1898 = getelementptr i8, ptr %1807, i64 30
  store i8 %1897, ptr %1898, align 2, !tbaa !18
  %1899 = lshr i64 %1878, 56
  %1900 = trunc nuw i64 %1899 to i8
  %1901 = getelementptr i8, ptr %1807, i64 31
  store i8 %1900, ptr %1901, align 1, !tbaa !18
  call void @llvm.lifetime.end.p0(ptr nonnull %41) #9
  call void @llvm.lifetime.end.p0(ptr nonnull %40) #9
  %1902 = add nuw nsw i64 %1418, 1
  %1903 = icmp eq i64 %1902, 3
  br i1 %1903, label %1904, label %1417, !llvm.loop !23

1904:                                             ; preds = %1637
  call void @llvm.lifetime.end.p0(ptr nonnull %32) #9
  call void @llvm.lifetime.end.p0(ptr nonnull %31) #9
  call void @llvm.lifetime.end.p0(ptr nonnull %30) #9
  call void @llvm.lifetime.end.p0(ptr nonnull %29) #9
  call void @llvm.lifetime.end.p0(ptr nonnull %28) #9
  call void @llvm.lifetime.end.p0(ptr nonnull %27) #9
  call void @llvm.lifetime.start.p0(ptr nonnull %14) #9
  call void @llvm.lifetime.start.p0(ptr nonnull %15) #9
  call void @llvm.lifetime.start.p0(ptr nonnull %16) #9
  call void @llvm.lifetime.start.p0(ptr nonnull %17) #9
  call void @llvm.lifetime.start.p0(ptr nonnull %18) #9
  call void @llvm.lifetime.start.p0(ptr nonnull %19) #9
  store ptr %59, ptr %19, align 8, !tbaa !9
  %1905 = getelementptr inbounds nuw i8, ptr %19, i64 8
  store i64 4, ptr %1905, align 8, !tbaa !14
  %1906 = getelementptr inbounds nuw i8, ptr %19, i64 16
  store i64 8, ptr %1906, align 8, !tbaa !15
  %1907 = getelementptr inbounds nuw i8, ptr %19, i64 24
  store i64 8, ptr %1907, align 8, !tbaa !16
  call void @llvm.lifetime.start.p0(ptr nonnull %20) #9
  store ptr %60, ptr %20, align 8, !tbaa !9
  %1908 = getelementptr inbounds nuw i8, ptr %20, i64 8
  store i64 4, ptr %1908, align 8, !tbaa !14
  %1909 = getelementptr inbounds nuw i8, ptr %20, i64 16
  store i64 8, ptr %1909, align 8, !tbaa !15
  %1910 = getelementptr inbounds nuw i8, ptr %20, i64 24
  store i64 8, ptr %1910, align 8, !tbaa !16
  %1911 = load i64, ptr %55, align 16
  %1912 = getelementptr inbounds nuw i8, ptr %55, i64 8
  %1913 = load i64, ptr %1912, align 8
  %1914 = getelementptr inbounds nuw i8, ptr %55, i64 16
  %1915 = load i64, ptr %1914, align 16
  %1916 = getelementptr inbounds nuw i8, ptr %55, i64 24
  %1917 = load i64, ptr %1916, align 8
  %1918 = getelementptr inbounds nuw i8, ptr %55, i64 32
  %1919 = load i64, ptr %1918, align 16
  %1920 = getelementptr inbounds nuw i8, ptr %55, i64 40
  %1921 = load i64, ptr %1920, align 8
  %1922 = getelementptr inbounds nuw i8, ptr %55, i64 48
  %1923 = load i64, ptr %1922, align 16
  %1924 = getelementptr inbounds nuw i8, ptr %55, i64 56
  %1925 = load i64, ptr %1924, align 8
  %1926 = getelementptr inbounds nuw i8, ptr %55, i64 64
  %1927 = load i64, ptr %1926, align 16
  %1928 = getelementptr inbounds nuw i8, ptr %55, i64 72
  %1929 = load i64, ptr %1928, align 8
  %1930 = getelementptr inbounds nuw i8, ptr %55, i64 80
  %1931 = load i64, ptr %1930, align 16
  %1932 = getelementptr inbounds nuw i8, ptr %55, i64 88
  %1933 = load i64, ptr %1932, align 8
  %1934 = getelementptr inbounds nuw i8, ptr %55, i64 96
  %1935 = load i64, ptr %1934, align 16
  %1936 = getelementptr inbounds nuw i8, ptr %55, i64 104
  %1937 = load i64, ptr %1936, align 8
  %1938 = getelementptr inbounds nuw i8, ptr %55, i64 112
  %1939 = load i64, ptr %1938, align 16
  %1940 = getelementptr inbounds nuw i8, ptr %55, i64 120
  %1941 = load i64, ptr %1940, align 8
  %1942 = load i64, ptr %206, align 16
  %1943 = getelementptr inbounds nuw i8, ptr %55, i64 136
  %1944 = load i64, ptr %1943, align 8
  %1945 = getelementptr inbounds nuw i8, ptr %55, i64 144
  %1946 = load i64, ptr %1945, align 16
  %1947 = getelementptr inbounds nuw i8, ptr %55, i64 152
  %1948 = load i64, ptr %1947, align 8
  %1949 = getelementptr inbounds nuw i8, ptr %55, i64 160
  %1950 = load i64, ptr %1949, align 16
  %1951 = getelementptr inbounds nuw i8, ptr %55, i64 168
  %1952 = load i64, ptr %1951, align 8
  %1953 = getelementptr inbounds nuw i8, ptr %55, i64 176
  %1954 = load i64, ptr %1953, align 16
  %1955 = getelementptr inbounds nuw i8, ptr %55, i64 184
  %1956 = load i64, ptr %1955, align 8
  %1957 = getelementptr inbounds nuw i8, ptr %55, i64 192
  %1958 = load i64, ptr %1957, align 16
  %1959 = getelementptr inbounds nuw i8, ptr %55, i64 200
  %1960 = load i64, ptr %1959, align 8
  %1961 = getelementptr inbounds nuw i8, ptr %55, i64 208
  %1962 = load i64, ptr %1961, align 16
  %1963 = getelementptr inbounds nuw i8, ptr %55, i64 216
  %1964 = load i64, ptr %1963, align 8
  %1965 = getelementptr inbounds nuw i8, ptr %55, i64 224
  %1966 = load i64, ptr %1965, align 16
  %1967 = getelementptr inbounds nuw i8, ptr %55, i64 232
  %1968 = load i64, ptr %1967, align 8
  %1969 = getelementptr inbounds nuw i8, ptr %55, i64 240
  %1970 = load i64, ptr %1969, align 16
  %1971 = getelementptr inbounds nuw i8, ptr %55, i64 248
  %1972 = load i64, ptr %1971, align 8
  %1973 = load i64, ptr %207, align 16
  %1974 = getelementptr inbounds nuw i8, ptr %55, i64 264
  %1975 = load i64, ptr %1974, align 8
  %1976 = getelementptr inbounds nuw i8, ptr %55, i64 272
  %1977 = load i64, ptr %1976, align 16
  %1978 = getelementptr inbounds nuw i8, ptr %55, i64 280
  %1979 = load i64, ptr %1978, align 8
  %1980 = getelementptr inbounds nuw i8, ptr %55, i64 288
  %1981 = load i64, ptr %1980, align 16
  %1982 = getelementptr inbounds nuw i8, ptr %55, i64 296
  %1983 = load i64, ptr %1982, align 8
  %1984 = getelementptr inbounds nuw i8, ptr %55, i64 304
  %1985 = load i64, ptr %1984, align 16
  %1986 = getelementptr inbounds nuw i8, ptr %55, i64 312
  %1987 = load i64, ptr %1986, align 8
  %1988 = getelementptr inbounds nuw i8, ptr %55, i64 320
  %1989 = load i64, ptr %1988, align 16
  %1990 = getelementptr inbounds nuw i8, ptr %55, i64 328
  %1991 = load i64, ptr %1990, align 8
  %1992 = getelementptr inbounds nuw i8, ptr %55, i64 336
  %1993 = load i64, ptr %1992, align 16
  %1994 = getelementptr inbounds nuw i8, ptr %55, i64 344
  %1995 = load i64, ptr %1994, align 8
  %1996 = getelementptr inbounds nuw i8, ptr %55, i64 352
  %1997 = load i64, ptr %1996, align 16
  %1998 = getelementptr inbounds nuw i8, ptr %55, i64 360
  %1999 = load i64, ptr %1998, align 8
  %2000 = getelementptr inbounds nuw i8, ptr %55, i64 368
  %2001 = load i64, ptr %2000, align 16
  %2002 = getelementptr inbounds nuw i8, ptr %55, i64 376
  %2003 = load i64, ptr %2002, align 8
  br label %2061

2004:                                             ; preds = %2061
  %2005 = getelementptr inbounds nuw i8, ptr %23, i64 8
  %2006 = getelementptr inbounds nuw i8, ptr %23, i64 16
  %2007 = getelementptr inbounds nuw i8, ptr %23, i64 24
  %2008 = getelementptr inbounds nuw i8, ptr %24, i64 8
  %2009 = getelementptr inbounds nuw i8, ptr %24, i64 16
  %2010 = getelementptr inbounds nuw i8, ptr %24, i64 24
  %2011 = load i64, ptr %16, align 16, !tbaa !17
  %2012 = getelementptr inbounds nuw i8, ptr %16, i64 32
  %2013 = load i64, ptr %2012, align 16, !tbaa !17
  %2014 = getelementptr inbounds nuw i8, ptr %16, i64 64
  %2015 = load i64, ptr %2014, align 16, !tbaa !17
  %2016 = load i64, ptr %15, align 16, !tbaa !17
  %2017 = getelementptr inbounds nuw i8, ptr %15, i64 8
  %2018 = load i64, ptr %2017, align 8, !tbaa !17
  %2019 = getelementptr inbounds nuw i8, ptr %15, i64 16
  %2020 = load i64, ptr %2019, align 16, !tbaa !17
  %2021 = getelementptr inbounds nuw i8, ptr %15, i64 24
  %2022 = load i64, ptr %2021, align 8, !tbaa !17
  %2023 = getelementptr inbounds nuw i8, ptr %15, i64 32
  %2024 = load i64, ptr %2023, align 16, !tbaa !17
  %2025 = getelementptr inbounds nuw i8, ptr %15, i64 40
  %2026 = load i64, ptr %2025, align 8, !tbaa !17
  %2027 = getelementptr inbounds nuw i8, ptr %15, i64 48
  %2028 = load i64, ptr %2027, align 16, !tbaa !17
  %2029 = getelementptr inbounds nuw i8, ptr %15, i64 56
  %2030 = load i64, ptr %2029, align 8, !tbaa !17
  %2031 = getelementptr inbounds nuw i8, ptr %21, i64 8
  %2032 = getelementptr inbounds nuw i8, ptr %15, i64 64
  %2033 = load i64, ptr %2032, align 16, !tbaa !17
  %2034 = getelementptr inbounds nuw i8, ptr %15, i64 72
  %2035 = load i64, ptr %2034, align 8, !tbaa !17
  %2036 = getelementptr inbounds nuw i8, ptr %15, i64 80
  %2037 = load i64, ptr %2036, align 16, !tbaa !17
  %2038 = getelementptr inbounds nuw i8, ptr %15, i64 88
  %2039 = load i64, ptr %2038, align 8, !tbaa !17
  %2040 = getelementptr inbounds nuw i8, ptr %21, i64 16
  %2041 = getelementptr inbounds nuw i8, ptr %22, i64 8
  %2042 = getelementptr inbounds nuw i8, ptr %22, i64 16
  %2043 = getelementptr inbounds nuw i8, ptr %16, i64 8
  %2044 = load i64, ptr %2043, align 8
  %2045 = getelementptr inbounds nuw i8, ptr %16, i64 40
  %2046 = load i64, ptr %2045, align 8
  %2047 = getelementptr inbounds nuw i8, ptr %16, i64 72
  %2048 = load i64, ptr %2047, align 8
  %2049 = getelementptr inbounds nuw i8, ptr %16, i64 16
  %2050 = load i64, ptr %2049, align 16
  %2051 = getelementptr inbounds nuw i8, ptr %16, i64 48
  %2052 = load i64, ptr %2051, align 16
  %2053 = getelementptr inbounds nuw i8, ptr %16, i64 80
  %2054 = load i64, ptr %2053, align 16
  %2055 = getelementptr inbounds nuw i8, ptr %16, i64 24
  %2056 = load i64, ptr %2055, align 8
  %2057 = getelementptr inbounds nuw i8, ptr %16, i64 56
  %2058 = load i64, ptr %2057, align 8
  %2059 = getelementptr inbounds nuw i8, ptr %16, i64 88
  %2060 = load i64, ptr %2059, align 8
  br label %2230

2061:                                             ; preds = %2061, %1904
  %2062 = phi i64 [ 0, %1904 ], [ %2228, %2061 ]
  %2063 = shl nuw nsw i64 %2062, 5
  %2064 = getelementptr inbounds nuw i8, ptr %54, i64 %2063
  %2065 = load i64, ptr %2064, align 16
  %2066 = getelementptr inbounds nuw i8, ptr %2064, i64 8
  %2067 = load i64, ptr %2066, align 8
  %2068 = getelementptr inbounds nuw i8, ptr %2064, i64 16
  %2069 = load i64, ptr %2068, align 16
  %2070 = getelementptr inbounds nuw i8, ptr %2064, i64 24
  %2071 = load i64, ptr %2070, align 8
  %2072 = mul nsw i64 %1911, %2065
  %2073 = ashr i64 %2072, 16
  %2074 = mul nsw i64 %1913, %2067
  %2075 = ashr i64 %2074, 16
  %2076 = add nsw i64 %2075, %2073
  %2077 = mul nsw i64 %1915, %2069
  %2078 = ashr i64 %2077, 16
  %2079 = add nsw i64 %2076, %2078
  %2080 = mul nsw i64 %1917, %2071
  %2081 = ashr i64 %2080, 16
  %2082 = add nsw i64 %2079, -1600
  %2083 = add nsw i64 %2082, %2081
  %2084 = mul nsw i64 %1919, %2065
  %2085 = ashr i64 %2084, 16
  %2086 = mul nsw i64 %1921, %2067
  %2087 = ashr i64 %2086, 16
  %2088 = add nsw i64 %2087, %2085
  %2089 = mul nsw i64 %1923, %2069
  %2090 = ashr i64 %2089, 16
  %2091 = add nsw i64 %2088, %2090
  %2092 = mul nsw i64 %1925, %2071
  %2093 = ashr i64 %2092, 16
  %2094 = add nsw i64 %2091, -1152
  %2095 = add nsw i64 %2094, %2093
  %2096 = mul nsw i64 %1927, %2065
  %2097 = ashr i64 %2096, 16
  %2098 = mul nsw i64 %1929, %2067
  %2099 = ashr i64 %2098, 16
  %2100 = add nsw i64 %2099, %2097
  %2101 = mul nsw i64 %1931, %2069
  %2102 = ashr i64 %2101, 16
  %2103 = add nsw i64 %2100, %2102
  %2104 = mul nsw i64 %1933, %2071
  %2105 = ashr i64 %2104, 16
  %2106 = add nsw i64 %2103, -704
  %2107 = add nsw i64 %2106, %2105
  %2108 = mul nsw i64 %1935, %2065
  %2109 = ashr i64 %2108, 16
  %2110 = mul nsw i64 %1937, %2067
  %2111 = ashr i64 %2110, 16
  %2112 = add nsw i64 %2111, %2109
  %2113 = mul nsw i64 %1939, %2069
  %2114 = ashr i64 %2113, 16
  %2115 = add nsw i64 %2112, %2114
  %2116 = mul nsw i64 %1941, %2071
  %2117 = ashr i64 %2116, 16
  %2118 = add nsw i64 %2115, -256
  %2119 = add nsw i64 %2118, %2117
  %2120 = mul nsw i64 %1942, %2065
  %2121 = ashr i64 %2120, 16
  %2122 = mul nsw i64 %1944, %2067
  %2123 = ashr i64 %2122, 16
  %2124 = add nsw i64 %2123, %2121
  %2125 = mul nsw i64 %1946, %2069
  %2126 = ashr i64 %2125, 16
  %2127 = add nsw i64 %2124, %2126
  %2128 = mul nsw i64 %1948, %2071
  %2129 = ashr i64 %2128, 16
  %2130 = add nsw i64 %2127, 192
  %2131 = add nsw i64 %2130, %2129
  %2132 = mul nsw i64 %1950, %2065
  %2133 = ashr i64 %2132, 16
  %2134 = mul nsw i64 %1952, %2067
  %2135 = ashr i64 %2134, 16
  %2136 = add nsw i64 %2135, %2133
  %2137 = mul nsw i64 %1954, %2069
  %2138 = ashr i64 %2137, 16
  %2139 = add nsw i64 %2136, %2138
  %2140 = mul nsw i64 %1956, %2071
  %2141 = ashr i64 %2140, 16
  %2142 = add nsw i64 %2139, 640
  %2143 = add nsw i64 %2142, %2141
  %2144 = mul nsw i64 %1958, %2065
  %2145 = ashr i64 %2144, 16
  %2146 = mul nsw i64 %1960, %2067
  %2147 = ashr i64 %2146, 16
  %2148 = add nsw i64 %2147, %2145
  %2149 = mul nsw i64 %1962, %2069
  %2150 = ashr i64 %2149, 16
  %2151 = add nsw i64 %2148, %2150
  %2152 = mul nsw i64 %1964, %2071
  %2153 = ashr i64 %2152, 16
  %2154 = add nsw i64 %2151, 1088
  %2155 = add nsw i64 %2154, %2153
  %2156 = mul nsw i64 %1966, %2065
  %2157 = ashr i64 %2156, 16
  %2158 = mul nsw i64 %1968, %2067
  %2159 = ashr i64 %2158, 16
  %2160 = add nsw i64 %2159, %2157
  %2161 = mul nsw i64 %1970, %2069
  %2162 = ashr i64 %2161, 16
  %2163 = add nsw i64 %2160, %2162
  %2164 = mul nsw i64 %1972, %2071
  %2165 = ashr i64 %2164, 16
  %2166 = add nsw i64 %2163, 1536
  %2167 = add nsw i64 %2166, %2165
  %2168 = mul nsw i64 %1973, %2065
  %2169 = ashr i64 %2168, 16
  %2170 = mul nsw i64 %1975, %2067
  %2171 = ashr i64 %2170, 16
  %2172 = add nsw i64 %2171, %2169
  %2173 = mul nsw i64 %1977, %2069
  %2174 = ashr i64 %2173, 16
  %2175 = add nsw i64 %2172, %2174
  %2176 = mul nsw i64 %1979, %2071
  %2177 = ashr i64 %2176, 16
  %2178 = add nsw i64 %2175, -1216
  %2179 = add nsw i64 %2178, %2177
  %2180 = mul nsw i64 %1981, %2065
  %2181 = ashr i64 %2180, 16
  %2182 = mul nsw i64 %1983, %2067
  %2183 = ashr i64 %2182, 16
  %2184 = add nsw i64 %2183, %2181
  %2185 = mul nsw i64 %1985, %2069
  %2186 = ashr i64 %2185, 16
  %2187 = add nsw i64 %2184, %2186
  %2188 = mul nsw i64 %1987, %2071
  %2189 = ashr i64 %2188, 16
  %2190 = add nsw i64 %2187, -768
  %2191 = add nsw i64 %2190, %2189
  %2192 = mul nsw i64 %1989, %2065
  %2193 = ashr i64 %2192, 16
  %2194 = mul nsw i64 %1991, %2067
  %2195 = ashr i64 %2194, 16
  %2196 = add nsw i64 %2195, %2193
  %2197 = mul nsw i64 %1993, %2069
  %2198 = ashr i64 %2197, 16
  %2199 = add nsw i64 %2196, %2198
  %2200 = mul nsw i64 %1995, %2071
  %2201 = ashr i64 %2200, 16
  %2202 = add nsw i64 %2199, -320
  %2203 = add nsw i64 %2202, %2201
  %2204 = mul nsw i64 %1997, %2065
  %2205 = ashr i64 %2204, 16
  %2206 = mul nsw i64 %1999, %2067
  %2207 = ashr i64 %2206, 16
  %2208 = add nsw i64 %2207, %2205
  %2209 = mul nsw i64 %2001, %2069
  %2210 = ashr i64 %2209, 16
  %2211 = add nsw i64 %2208, %2210
  %2212 = mul nsw i64 %2003, %2071
  %2213 = ashr i64 %2212, 16
  %2214 = add nsw i64 %2211, 128
  %2215 = add nsw i64 %2214, %2213
  %2216 = getelementptr i8, ptr %16, i64 %2063
  %2217 = getelementptr i8, ptr %15, i64 %2063
  %2218 = getelementptr i8, ptr %14, i64 %2063
  store i64 %2083, ptr %2218, align 16, !tbaa !17
  %2219 = getelementptr inbounds nuw i8, ptr %2218, i64 8
  store i64 %2095, ptr %2219, align 8, !tbaa !17
  %2220 = getelementptr inbounds nuw i8, ptr %2218, i64 16
  store i64 %2107, ptr %2220, align 16, !tbaa !17
  %2221 = getelementptr inbounds nuw i8, ptr %2218, i64 24
  store i64 %2119, ptr %2221, align 8, !tbaa !17
  store i64 %2131, ptr %2217, align 16, !tbaa !17
  %2222 = getelementptr inbounds nuw i8, ptr %2217, i64 8
  store i64 %2143, ptr %2222, align 8, !tbaa !17
  %2223 = getelementptr inbounds nuw i8, ptr %2217, i64 16
  store i64 %2155, ptr %2223, align 16, !tbaa !17
  %2224 = getelementptr inbounds nuw i8, ptr %2217, i64 24
  store i64 %2167, ptr %2224, align 8, !tbaa !17
  store i64 %2179, ptr %2216, align 16, !tbaa !17
  %2225 = getelementptr inbounds nuw i8, ptr %2216, i64 8
  store i64 %2191, ptr %2225, align 8, !tbaa !17
  %2226 = getelementptr inbounds nuw i8, ptr %2216, i64 16
  store i64 %2203, ptr %2226, align 16, !tbaa !17
  %2227 = getelementptr inbounds nuw i8, ptr %2216, i64 24
  store i64 %2215, ptr %2227, align 8, !tbaa !17
  %2228 = add nuw nsw i64 %2062, 1
  %2229 = icmp eq i64 %2228, 3
  br i1 %2229, label %2004, label %2061, !llvm.loop !24

2230:                                             ; preds = %2230, %2004
  %2231 = phi i64 [ 0, %2004 ], [ %2315, %2230 ]
  call void @llvm.lifetime.start.p0(ptr nonnull %21) #9
  call void @llvm.lifetime.start.p0(ptr nonnull %22) #9
  %2232 = getelementptr inbounds nuw [32 x i8], ptr %14, i64 %2231
  %2233 = load i64, ptr %2232, align 16, !tbaa !17
  %2234 = getelementptr inbounds nuw i8, ptr %2232, i64 8
  %2235 = load i64, ptr %2234, align 8, !tbaa !17
  %2236 = getelementptr inbounds nuw i8, ptr %2232, i64 16
  %2237 = load i64, ptr %2236, align 16, !tbaa !17
  %2238 = getelementptr inbounds nuw i8, ptr %2232, i64 24
  %2239 = load i64, ptr %2238, align 8, !tbaa !17
  %2240 = mul nsw i64 %2233, %2016
  %2241 = and i64 %2240, -65536
  %2242 = mul nsw i64 %2235, %2018
  %2243 = and i64 %2242, -65536
  %2244 = add i64 %2243, %2241
  %2245 = mul nsw i64 %2237, %2020
  %2246 = and i64 %2245, -65536
  %2247 = add i64 %2244, %2246
  %2248 = mul nsw i64 %2239, %2022
  %2249 = add i64 %2247, %2248
  %2250 = and i64 %2249, -65536
  %2251 = sdiv i64 %2250, 131072
  store i64 %2251, ptr %21, align 16, !tbaa !17
  %2252 = mul nsw i64 %2233, %2024
  %2253 = and i64 %2252, -65536
  %2254 = mul nsw i64 %2235, %2026
  %2255 = and i64 %2254, -65536
  %2256 = add i64 %2255, %2253
  %2257 = mul nsw i64 %2237, %2028
  %2258 = and i64 %2257, -65536
  %2259 = add i64 %2256, %2258
  %2260 = mul nsw i64 %2239, %2030
  %2261 = add i64 %2259, %2260
  %2262 = and i64 %2261, -65536
  %2263 = sdiv i64 %2262, 131072
  store i64 %2263, ptr %2031, align 8, !tbaa !17
  %2264 = mul nsw i64 %2233, %2033
  %2265 = and i64 %2264, -65536
  %2266 = mul nsw i64 %2235, %2035
  %2267 = and i64 %2266, -65536
  %2268 = add i64 %2267, %2265
  %2269 = mul nsw i64 %2237, %2037
  %2270 = and i64 %2269, -65536
  %2271 = add i64 %2268, %2270
  %2272 = mul nsw i64 %2239, %2039
  %2273 = add i64 %2271, %2272
  %2274 = and i64 %2273, -65536
  %2275 = sdiv i64 %2274, 131072
  store i64 %2275, ptr %2040, align 16, !tbaa !17
  call void @llvm.lifetime.start.p0(ptr nonnull %23) #9
  store ptr %21, ptr %23, align 8, !tbaa !9
  store i64 3, ptr %2005, align 8, !tbaa !14
  store i64 8, ptr %2006, align 8, !tbaa !15
  store i64 8, ptr %2007, align 8, !tbaa !16
  call void @llvm.lifetime.start.p0(ptr nonnull %24) #9
  store ptr %22, ptr %24, align 8, !tbaa !9
  store i64 3, ptr %2008, align 8, !tbaa !14
  store i64 8, ptr %2009, align 8, !tbaa !15
  store i64 8, ptr %2010, align 8, !tbaa !16
  call fastcc void @softmax(ptr noundef %23, ptr noundef %24)
  %2276 = getelementptr inbounds nuw [32 x i8], ptr %17, i64 %2231
  %2277 = load i64, ptr %22, align 16, !tbaa !17
  %2278 = mul nsw i64 %2277, %2011
  %2279 = ashr i64 %2278, 16
  %2280 = load i64, ptr %2041, align 8, !tbaa !17
  %2281 = mul nsw i64 %2280, %2013
  %2282 = ashr i64 %2281, 16
  %2283 = add nsw i64 %2282, %2279
  %2284 = load i64, ptr %2042, align 16, !tbaa !17
  %2285 = mul nsw i64 %2284, %2015
  %2286 = ashr i64 %2285, 16
  %2287 = add nsw i64 %2283, %2286
  store i64 %2287, ptr %2276, align 16, !tbaa !17
  %2288 = mul nsw i64 %2277, %2044
  %2289 = ashr i64 %2288, 16
  %2290 = mul nsw i64 %2280, %2046
  %2291 = ashr i64 %2290, 16
  %2292 = add nsw i64 %2291, %2289
  %2293 = mul nsw i64 %2284, %2048
  %2294 = ashr i64 %2293, 16
  %2295 = add nsw i64 %2292, %2294
  %2296 = getelementptr inbounds nuw i8, ptr %2276, i64 8
  store i64 %2295, ptr %2296, align 8, !tbaa !17
  %2297 = mul nsw i64 %2277, %2050
  %2298 = ashr i64 %2297, 16
  %2299 = mul nsw i64 %2280, %2052
  %2300 = ashr i64 %2299, 16
  %2301 = add nsw i64 %2300, %2298
  %2302 = mul nsw i64 %2284, %2054
  %2303 = ashr i64 %2302, 16
  %2304 = add nsw i64 %2301, %2303
  %2305 = getelementptr inbounds nuw i8, ptr %2276, i64 16
  store i64 %2304, ptr %2305, align 16, !tbaa !17
  %2306 = mul nsw i64 %2277, %2056
  %2307 = ashr i64 %2306, 16
  %2308 = mul nsw i64 %2280, %2058
  %2309 = ashr i64 %2308, 16
  %2310 = add nsw i64 %2309, %2307
  %2311 = mul nsw i64 %2284, %2060
  %2312 = ashr i64 %2311, 16
  %2313 = add nsw i64 %2310, %2312
  %2314 = getelementptr inbounds nuw i8, ptr %2276, i64 24
  store i64 %2313, ptr %2314, align 8, !tbaa !17
  call void @llvm.lifetime.end.p0(ptr nonnull %24) #9
  call void @llvm.lifetime.end.p0(ptr nonnull %23) #9
  call void @llvm.lifetime.end.p0(ptr nonnull %22) #9
  call void @llvm.lifetime.end.p0(ptr nonnull %21) #9
  %2315 = add nuw nsw i64 %2231, 1
  %2316 = icmp eq i64 %2315, 3
  br i1 %2316, label %2317, label %2230, !llvm.loop !25

2317:                                             ; preds = %2230
  %2318 = getelementptr inbounds nuw i8, ptr %26, i64 24
  %2319 = getelementptr inbounds nuw i8, ptr %26, i64 16
  %2320 = getelementptr inbounds nuw i8, ptr %26, i64 8
  %2321 = getelementptr inbounds nuw i8, ptr %25, i64 24
  %2322 = getelementptr inbounds nuw i8, ptr %25, i64 16
  %2323 = getelementptr inbounds nuw i8, ptr %25, i64 8
  %2324 = load i64, ptr %17, align 16
  %2325 = getelementptr inbounds nuw i8, ptr %17, i64 8
  %2326 = load i64, ptr %2325, align 8
  %2327 = getelementptr inbounds nuw i8, ptr %17, i64 16
  %2328 = load i64, ptr %2327, align 16
  %2329 = getelementptr inbounds nuw i8, ptr %17, i64 24
  %2330 = load i64, ptr %2329, align 8
  %2331 = mul nsw i64 %2324, -12800
  %2332 = ashr i64 %2331, 16
  %2333 = mul nsw i64 %2326, -11392
  %2334 = ashr i64 %2333, 16
  %2335 = add nsw i64 %2334, %2332
  %2336 = mul nsw i64 %2328, -9984
  %2337 = ashr i64 %2336, 16
  %2338 = add nsw i64 %2335, %2337
  %2339 = mul nsw i64 %2330, -8576
  %2340 = ashr i64 %2339, 16
  %2341 = add nsw i64 %2338, %2340
  %2342 = mul nsw i64 %2324, -7168
  %2343 = ashr i64 %2342, 16
  %2344 = mul nsw i64 %2326, -5760
  %2345 = ashr i64 %2344, 16
  %2346 = add nsw i64 %2345, %2343
  %2347 = mul nsw i64 %2328, -4352
  %2348 = ashr i64 %2347, 16
  %2349 = add nsw i64 %2346, %2348
  %2350 = mul nsw i64 %2330, -2944
  %2351 = ashr i64 %2350, 16
  %2352 = add nsw i64 %2349, 10
  %2353 = add nsw i64 %2352, %2351
  %2354 = mul nsw i64 %2324, -1536
  %2355 = ashr i64 %2354, 16
  %2356 = mul nsw i64 %2326, -128
  %2357 = ashr i64 %2356, 16
  %2358 = add nsw i64 %2357, %2355
  %2359 = mul nsw i64 %2328, 1280
  %2360 = ashr i64 %2359, 16
  %2361 = add nsw i64 %2358, %2360
  %2362 = mul nsw i64 %2330, 2688
  %2363 = ashr i64 %2362, 16
  %2364 = add nsw i64 %2361, 20
  %2365 = add nsw i64 %2364, %2363
  %2366 = ashr i64 %2324, 4
  %2367 = mul nsw i64 %2326, 5504
  %2368 = ashr i64 %2367, 16
  %2369 = add nsw i64 %2368, %2366
  %2370 = mul nsw i64 %2328, 6912
  %2371 = ashr i64 %2370, 16
  %2372 = add nsw i64 %2369, %2371
  %2373 = mul nsw i64 %2330, 8320
  %2374 = ashr i64 %2373, 16
  %2375 = add nsw i64 %2372, 30
  %2376 = add nsw i64 %2375, %2374
  %2377 = add nsw i64 %2341, -12800
  store i64 %2377, ptr %18, align 16, !tbaa !17
  %2378 = add nsw i64 %2353, -3328
  %2379 = getelementptr inbounds nuw i8, ptr %18, i64 8
  store i64 %2378, ptr %2379, align 8, !tbaa !17
  %2380 = add nsw i64 %2365, 6144
  %2381 = getelementptr inbounds nuw i8, ptr %18, i64 16
  store i64 %2380, ptr %2381, align 16, !tbaa !17
  %2382 = add nsw i64 %2376, -9984
  %2383 = getelementptr inbounds nuw i8, ptr %18, i64 24
  store i64 %2382, ptr %2383, align 8, !tbaa !17
  call void @llvm.lifetime.start.p0(ptr nonnull %25) #9
  store ptr %18, ptr %25, align 8, !tbaa !9
  store i64 4, ptr %2323, align 8, !tbaa !14
  store i64 8, ptr %2322, align 8, !tbaa !15
  store i64 8, ptr %2321, align 8, !tbaa !16
  call void @llvm.lifetime.start.p0(ptr nonnull %26) #9
  store ptr %17, ptr %26, align 8, !tbaa !9
  store i64 4, ptr %2320, align 8, !tbaa !14
  store i64 8, ptr %2319, align 8, !tbaa !15
  store i64 8, ptr %2318, align 8, !tbaa !16
  call fastcc void @layernorm(ptr noundef %25, i64 noundef 4, ptr noundef %19, ptr noundef %20, ptr noundef %26)
  %2384 = load i64, ptr %17, align 16, !tbaa !17
  %2385 = getelementptr inbounds nuw i8, ptr %17, i64 8
  %2386 = load i64, ptr %2385, align 8, !tbaa !17
  %2387 = getelementptr inbounds nuw i8, ptr %17, i64 16
  %2388 = load i64, ptr %2387, align 16, !tbaa !17
  %2389 = getelementptr inbounds nuw i8, ptr %17, i64 24
  %2390 = load i64, ptr %2389, align 8, !tbaa !17
  call void @llvm.lifetime.end.p0(ptr nonnull %26) #9
  call void @llvm.lifetime.end.p0(ptr nonnull %25) #9
  %2391 = getelementptr inbounds nuw i8, ptr %17, i64 32
  %2392 = load i64, ptr %2391, align 16
  %2393 = getelementptr inbounds nuw i8, ptr %17, i64 40
  %2394 = load i64, ptr %2393, align 8
  %2395 = getelementptr inbounds nuw i8, ptr %17, i64 48
  %2396 = load i64, ptr %2395, align 16
  %2397 = getelementptr inbounds nuw i8, ptr %17, i64 56
  %2398 = load i64, ptr %2397, align 8
  %2399 = mul nsw i64 %2392, -12800
  %2400 = ashr i64 %2399, 16
  %2401 = mul nsw i64 %2394, -11392
  %2402 = ashr i64 %2401, 16
  %2403 = add nsw i64 %2402, %2400
  %2404 = mul nsw i64 %2396, -9984
  %2405 = ashr i64 %2404, 16
  %2406 = add nsw i64 %2403, %2405
  %2407 = mul nsw i64 %2398, -8576
  %2408 = ashr i64 %2407, 16
  %2409 = add nsw i64 %2406, %2408
  %2410 = mul nsw i64 %2392, -7168
  %2411 = ashr i64 %2410, 16
  %2412 = mul nsw i64 %2394, -5760
  %2413 = ashr i64 %2412, 16
  %2414 = add nsw i64 %2413, %2411
  %2415 = mul nsw i64 %2396, -4352
  %2416 = ashr i64 %2415, 16
  %2417 = add nsw i64 %2414, %2416
  %2418 = mul nsw i64 %2398, -2944
  %2419 = ashr i64 %2418, 16
  %2420 = add nsw i64 %2417, 10
  %2421 = add nsw i64 %2420, %2419
  %2422 = mul nsw i64 %2392, -1536
  %2423 = ashr i64 %2422, 16
  %2424 = mul nsw i64 %2394, -128
  %2425 = ashr i64 %2424, 16
  %2426 = add nsw i64 %2425, %2423
  %2427 = mul nsw i64 %2396, 1280
  %2428 = ashr i64 %2427, 16
  %2429 = add nsw i64 %2426, %2428
  %2430 = mul nsw i64 %2398, 2688
  %2431 = ashr i64 %2430, 16
  %2432 = add nsw i64 %2429, 20
  %2433 = add nsw i64 %2432, %2431
  %2434 = ashr i64 %2392, 4
  %2435 = mul nsw i64 %2394, 5504
  %2436 = ashr i64 %2435, 16
  %2437 = add nsw i64 %2436, %2434
  %2438 = mul nsw i64 %2396, 6912
  %2439 = ashr i64 %2438, 16
  %2440 = add nsw i64 %2437, %2439
  %2441 = mul nsw i64 %2398, 8320
  %2442 = ashr i64 %2441, 16
  %2443 = add nsw i64 %2440, 30
  %2444 = add nsw i64 %2443, %2442
  %2445 = getelementptr inbounds nuw i8, ptr %17, i64 32
  %2446 = getelementptr inbounds nuw i8, ptr %18, i64 32
  %2447 = add nsw i64 %2409, -512
  store i64 %2447, ptr %2446, align 16, !tbaa !17
  %2448 = add nsw i64 %2421, 8960
  %2449 = getelementptr inbounds nuw i8, ptr %18, i64 40
  store i64 %2448, ptr %2449, align 8, !tbaa !17
  %2450 = add nsw i64 %2433, -7168
  %2451 = getelementptr inbounds nuw i8, ptr %18, i64 48
  store i64 %2450, ptr %2451, align 16, !tbaa !17
  %2452 = add nsw i64 %2444, 2304
  %2453 = getelementptr inbounds nuw i8, ptr %18, i64 56
  store i64 %2452, ptr %2453, align 8, !tbaa !17
  call void @llvm.lifetime.start.p0(ptr nonnull %25) #9
  store ptr %2446, ptr %25, align 8, !tbaa !9
  store i64 4, ptr %2323, align 8, !tbaa !14
  store i64 8, ptr %2322, align 8, !tbaa !15
  store i64 8, ptr %2321, align 8, !tbaa !16
  call void @llvm.lifetime.start.p0(ptr nonnull %26) #9
  store ptr %2391, ptr %26, align 8, !tbaa !9
  store i64 4, ptr %2320, align 8, !tbaa !14
  store i64 8, ptr %2319, align 8, !tbaa !15
  store i64 8, ptr %2318, align 8, !tbaa !16
  call fastcc void @layernorm(ptr noundef %25, i64 noundef 4, ptr noundef %19, ptr noundef %20, ptr noundef %26)
  %2454 = load i64, ptr %2445, align 16, !tbaa !17
  %2455 = getelementptr inbounds nuw i8, ptr %17, i64 40
  %2456 = load i64, ptr %2455, align 8, !tbaa !17
  %2457 = getelementptr inbounds nuw i8, ptr %17, i64 48
  %2458 = load i64, ptr %2457, align 16, !tbaa !17
  %2459 = getelementptr inbounds nuw i8, ptr %17, i64 56
  %2460 = load i64, ptr %2459, align 8, !tbaa !17
  call void @llvm.lifetime.end.p0(ptr nonnull %26) #9
  call void @llvm.lifetime.end.p0(ptr nonnull %25) #9
  %2461 = getelementptr inbounds nuw i8, ptr %17, i64 64
  %2462 = load i64, ptr %2461, align 16
  %2463 = getelementptr inbounds nuw i8, ptr %17, i64 72
  %2464 = load i64, ptr %2463, align 8
  %2465 = getelementptr inbounds nuw i8, ptr %17, i64 80
  %2466 = load i64, ptr %2465, align 16
  %2467 = getelementptr inbounds nuw i8, ptr %17, i64 88
  %2468 = load i64, ptr %2467, align 8
  %2469 = mul nsw i64 %2462, -12800
  %2470 = ashr i64 %2469, 16
  %2471 = mul nsw i64 %2464, -11392
  %2472 = ashr i64 %2471, 16
  %2473 = add nsw i64 %2472, %2470
  %2474 = mul nsw i64 %2466, -9984
  %2475 = ashr i64 %2474, 16
  %2476 = add nsw i64 %2473, %2475
  %2477 = mul nsw i64 %2468, -8576
  %2478 = ashr i64 %2477, 16
  %2479 = add nsw i64 %2476, %2478
  %2480 = mul nsw i64 %2462, -7168
  %2481 = ashr i64 %2480, 16
  %2482 = mul nsw i64 %2464, -5760
  %2483 = ashr i64 %2482, 16
  %2484 = add nsw i64 %2483, %2481
  %2485 = mul nsw i64 %2466, -4352
  %2486 = ashr i64 %2485, 16
  %2487 = add nsw i64 %2484, %2486
  %2488 = mul nsw i64 %2468, -2944
  %2489 = ashr i64 %2488, 16
  %2490 = add nsw i64 %2487, 10
  %2491 = add nsw i64 %2490, %2489
  %2492 = mul nsw i64 %2462, -1536
  %2493 = ashr i64 %2492, 16
  %2494 = mul nsw i64 %2464, -128
  %2495 = ashr i64 %2494, 16
  %2496 = add nsw i64 %2495, %2493
  %2497 = mul nsw i64 %2466, 1280
  %2498 = ashr i64 %2497, 16
  %2499 = add nsw i64 %2496, %2498
  %2500 = mul nsw i64 %2468, 2688
  %2501 = ashr i64 %2500, 16
  %2502 = add nsw i64 %2499, 20
  %2503 = add nsw i64 %2502, %2501
  %2504 = ashr i64 %2462, 4
  %2505 = mul nsw i64 %2464, 5504
  %2506 = ashr i64 %2505, 16
  %2507 = add nsw i64 %2506, %2504
  %2508 = mul nsw i64 %2466, 6912
  %2509 = ashr i64 %2508, 16
  %2510 = add nsw i64 %2507, %2509
  %2511 = mul nsw i64 %2468, 8320
  %2512 = ashr i64 %2511, 16
  %2513 = add nsw i64 %2510, 30
  %2514 = add nsw i64 %2513, %2512
  %2515 = getelementptr inbounds nuw i8, ptr %17, i64 64
  %2516 = getelementptr inbounds nuw i8, ptr %18, i64 64
  %2517 = add nsw i64 %2479, 11776
  store i64 %2517, ptr %2516, align 16, !tbaa !17
  %2518 = add nsw i64 %2491, -4352
  %2519 = getelementptr inbounds nuw i8, ptr %18, i64 72
  store i64 %2518, ptr %2519, align 8, !tbaa !17
  %2520 = add nsw i64 %2503, 5120
  %2521 = getelementptr inbounds nuw i8, ptr %18, i64 80
  store i64 %2520, ptr %2521, align 16, !tbaa !17
  %2522 = add nsw i64 %2514, -11008
  %2523 = getelementptr inbounds nuw i8, ptr %18, i64 88
  store i64 %2522, ptr %2523, align 8, !tbaa !17
  call void @llvm.lifetime.start.p0(ptr nonnull %25) #9
  store ptr %2516, ptr %25, align 8, !tbaa !9
  store i64 4, ptr %2323, align 8, !tbaa !14
  store i64 8, ptr %2322, align 8, !tbaa !15
  store i64 8, ptr %2321, align 8, !tbaa !16
  call void @llvm.lifetime.start.p0(ptr nonnull %26) #9
  store ptr %2461, ptr %26, align 8, !tbaa !9
  store i64 4, ptr %2320, align 8, !tbaa !14
  store i64 8, ptr %2319, align 8, !tbaa !15
  store i64 8, ptr %2318, align 8, !tbaa !16
  call fastcc void @layernorm(ptr noundef %25, i64 noundef 4, ptr noundef %19, ptr noundef %20, ptr noundef %26)
  %2524 = load i64, ptr %2515, align 16, !tbaa !17
  %2525 = getelementptr inbounds nuw i8, ptr %17, i64 72
  %2526 = load i64, ptr %2525, align 8, !tbaa !17
  %2527 = getelementptr inbounds nuw i8, ptr %17, i64 80
  %2528 = load i64, ptr %2527, align 16, !tbaa !17
  %2529 = getelementptr inbounds nuw i8, ptr %17, i64 88
  %2530 = load i64, ptr %2529, align 8, !tbaa !17
  call void @llvm.lifetime.end.p0(ptr nonnull %26) #9
  call void @llvm.lifetime.end.p0(ptr nonnull %25) #9
  call void @llvm.lifetime.end.p0(ptr nonnull %20) #9
  call void @llvm.lifetime.end.p0(ptr nonnull %19) #9
  call void @llvm.lifetime.end.p0(ptr nonnull %18) #9
  call void @llvm.lifetime.end.p0(ptr nonnull %17) #9
  call void @llvm.lifetime.end.p0(ptr nonnull %16) #9
  call void @llvm.lifetime.end.p0(ptr nonnull %15) #9
  call void @llvm.lifetime.end.p0(ptr nonnull %14) #9
  %2531 = load i64, ptr %61, align 16, !tbaa !17
  %2532 = icmp eq i64 %2531, %2384
  br i1 %2532, label %2983, label %2981

2533:                                             ; preds = %3064, %2602
  %2534 = phi i64 [ %2641, %2602 ], [ %3352, %3064 ]
  %2535 = phi i64 [ %2603, %2602 ], [ 0, %3064 ]
  %2536 = shl nsw i64 %2534, 3
  %2537 = getelementptr inbounds nuw i8, ptr %72, i64 %2536
  %2538 = load i8, ptr %2537, align 8, !tbaa !18
  %2539 = zext i8 %2538 to i64
  %2540 = getelementptr inbounds nuw i8, ptr %2537, i64 1
  %2541 = load i8, ptr %2540, align 1, !tbaa !18
  %2542 = zext i8 %2541 to i64
  %2543 = shl nuw nsw i64 %2542, 8
  %2544 = or disjoint i64 %2543, %2539
  %2545 = getelementptr inbounds nuw i8, ptr %2537, i64 2
  %2546 = load i8, ptr %2545, align 2, !tbaa !18
  %2547 = zext i8 %2546 to i64
  %2548 = shl nuw nsw i64 %2547, 16
  %2549 = or disjoint i64 %2548, %2544
  %2550 = getelementptr inbounds nuw i8, ptr %2537, i64 3
  %2551 = load i8, ptr %2550, align 1, !tbaa !18
  %2552 = zext i8 %2551 to i64
  %2553 = shl nuw nsw i64 %2552, 24
  %2554 = or disjoint i64 %2553, %2549
  %2555 = getelementptr inbounds nuw i8, ptr %2537, i64 4
  %2556 = load i8, ptr %2555, align 4, !tbaa !18
  %2557 = zext i8 %2556 to i64
  %2558 = shl nuw nsw i64 %2557, 32
  %2559 = or disjoint i64 %2558, %2554
  %2560 = getelementptr inbounds nuw i8, ptr %2537, i64 5
  %2561 = load i8, ptr %2560, align 1, !tbaa !18
  %2562 = zext i8 %2561 to i64
  %2563 = shl nuw nsw i64 %2562, 40
  %2564 = or i64 %2563, %2559
  %2565 = getelementptr inbounds nuw i8, ptr %2537, i64 6
  %2566 = load i8, ptr %2565, align 2, !tbaa !18
  %2567 = zext i8 %2566 to i64
  %2568 = shl nuw nsw i64 %2567, 48
  %2569 = or i64 %2568, %2564
  %2570 = getelementptr inbounds nuw i8, ptr %2537, i64 7
  %2571 = load i8, ptr %2570, align 1, !tbaa !18
  %2572 = zext i8 %2571 to i64
  %2573 = shl nuw i64 %2572, 56
  %2574 = or i64 %2573, %2569
  %2575 = icmp eq i64 %2574, 3
  br i1 %2575, label %2576, label %2602

2576:                                             ; preds = %2533
  %2577 = shl nsw i64 %2535, 3
  %2578 = getelementptr inbounds i8, ptr %75, i64 %2577
  %2579 = trunc i64 %2534 to i8
  store i8 %2579, ptr %2578, align 8, !tbaa !18
  %2580 = lshr i64 %2534, 8
  %2581 = trunc i64 %2580 to i8
  %2582 = getelementptr inbounds nuw i8, ptr %2578, i64 1
  store i8 %2581, ptr %2582, align 1, !tbaa !18
  %2583 = lshr i64 %2534, 16
  %2584 = trunc i64 %2583 to i8
  %2585 = getelementptr inbounds nuw i8, ptr %2578, i64 2
  store i8 %2584, ptr %2585, align 2, !tbaa !18
  %2586 = lshr i64 %2534, 24
  %2587 = trunc i64 %2586 to i8
  %2588 = getelementptr inbounds nuw i8, ptr %2578, i64 3
  store i8 %2587, ptr %2588, align 1, !tbaa !18
  %2589 = lshr i64 %2534, 32
  %2590 = trunc i64 %2589 to i8
  %2591 = getelementptr inbounds nuw i8, ptr %2578, i64 4
  store i8 %2590, ptr %2591, align 4, !tbaa !18
  %2592 = lshr i64 %2534, 40
  %2593 = trunc i64 %2592 to i8
  %2594 = getelementptr inbounds nuw i8, ptr %2578, i64 5
  store i8 %2593, ptr %2594, align 1, !tbaa !18
  %2595 = lshr i64 %2534, 48
  %2596 = trunc i64 %2595 to i8
  %2597 = getelementptr inbounds nuw i8, ptr %2578, i64 6
  store i8 %2596, ptr %2597, align 2, !tbaa !18
  %2598 = lshr i64 %2534, 56
  %2599 = trunc nuw nsw i64 %2598 to i8
  %2600 = getelementptr inbounds nuw i8, ptr %2578, i64 7
  store i8 %2599, ptr %2600, align 1, !tbaa !18
  %2601 = add nsw i64 %2535, 1
  br label %2602

2602:                                             ; preds = %2576, %2533
  %2603 = phi i64 [ %2535, %2533 ], [ %2601, %2576 ]
  %2604 = getelementptr inbounds nuw i8, ptr %74, i64 %2536
  %2605 = load i8, ptr %2604, align 8, !tbaa !18
  %2606 = zext i8 %2605 to i64
  %2607 = getelementptr inbounds nuw i8, ptr %2604, i64 1
  %2608 = load i8, ptr %2607, align 1, !tbaa !18
  %2609 = zext i8 %2608 to i64
  %2610 = shl nuw nsw i64 %2609, 8
  %2611 = or disjoint i64 %2610, %2606
  %2612 = getelementptr inbounds nuw i8, ptr %2604, i64 2
  %2613 = load i8, ptr %2612, align 2, !tbaa !18
  %2614 = zext i8 %2613 to i64
  %2615 = shl nuw nsw i64 %2614, 16
  %2616 = or disjoint i64 %2615, %2611
  %2617 = getelementptr inbounds nuw i8, ptr %2604, i64 3
  %2618 = load i8, ptr %2617, align 1, !tbaa !18
  %2619 = zext i8 %2618 to i64
  %2620 = shl nuw nsw i64 %2619, 24
  %2621 = or disjoint i64 %2620, %2616
  %2622 = getelementptr inbounds nuw i8, ptr %2604, i64 4
  %2623 = load i8, ptr %2622, align 4, !tbaa !18
  %2624 = zext i8 %2623 to i64
  %2625 = shl nuw nsw i64 %2624, 32
  %2626 = or disjoint i64 %2625, %2621
  %2627 = getelementptr inbounds nuw i8, ptr %2604, i64 5
  %2628 = load i8, ptr %2627, align 1, !tbaa !18
  %2629 = zext i8 %2628 to i64
  %2630 = shl nuw nsw i64 %2629, 40
  %2631 = or i64 %2630, %2626
  %2632 = getelementptr inbounds nuw i8, ptr %2604, i64 6
  %2633 = load i8, ptr %2632, align 2, !tbaa !18
  %2634 = zext i8 %2633 to i64
  %2635 = shl nuw nsw i64 %2634, 48
  %2636 = or i64 %2635, %2631
  %2637 = getelementptr inbounds nuw i8, ptr %2604, i64 7
  %2638 = load i8, ptr %2637, align 1, !tbaa !18
  %2639 = zext i8 %2638 to i64
  %2640 = shl nuw i64 %2639, 56
  %2641 = or i64 %2640, %2636
  %2642 = icmp sgt i64 %2641, -1
  br i1 %2642, label %2533, label %2643, !llvm.loop !26

2643:                                             ; preds = %2602, %3064
  %2644 = phi i64 [ 0, %3064 ], [ %2603, %2602 ]
  %2645 = getelementptr inbounds nuw i8, ptr %73, i64 8
  %2646 = load i8, ptr %2645, align 8, !tbaa !18
  %2647 = zext i8 %2646 to i64
  %2648 = getelementptr inbounds nuw i8, ptr %73, i64 9
  %2649 = load i8, ptr %2648, align 1, !tbaa !18
  %2650 = zext i8 %2649 to i64
  %2651 = shl nuw nsw i64 %2650, 8
  %2652 = or disjoint i64 %2651, %2647
  %2653 = getelementptr inbounds nuw i8, ptr %73, i64 10
  %2654 = load i8, ptr %2653, align 2, !tbaa !18
  %2655 = zext i8 %2654 to i64
  %2656 = shl nuw nsw i64 %2655, 16
  %2657 = or disjoint i64 %2656, %2652
  %2658 = getelementptr inbounds nuw i8, ptr %73, i64 11
  %2659 = load i8, ptr %2658, align 1, !tbaa !18
  %2660 = zext i8 %2659 to i64
  %2661 = shl nuw nsw i64 %2660, 24
  %2662 = or disjoint i64 %2661, %2657
  %2663 = getelementptr inbounds nuw i8, ptr %73, i64 12
  %2664 = load i8, ptr %2663, align 4, !tbaa !18
  %2665 = zext i8 %2664 to i64
  %2666 = shl nuw nsw i64 %2665, 32
  %2667 = or disjoint i64 %2666, %2662
  %2668 = getelementptr inbounds nuw i8, ptr %73, i64 13
  %2669 = load i8, ptr %2668, align 1, !tbaa !18
  %2670 = zext i8 %2669 to i64
  %2671 = shl nuw nsw i64 %2670, 40
  %2672 = or i64 %2671, %2667
  %2673 = getelementptr inbounds nuw i8, ptr %73, i64 14
  %2674 = load i8, ptr %2673, align 2, !tbaa !18
  %2675 = zext i8 %2674 to i64
  %2676 = shl nuw nsw i64 %2675, 48
  %2677 = or i64 %2676, %2672
  %2678 = getelementptr inbounds nuw i8, ptr %73, i64 15
  %2679 = load i8, ptr %2678, align 1, !tbaa !18
  %2680 = zext i8 %2679 to i64
  %2681 = shl nuw i64 %2680, 56
  %2682 = or i64 %2681, %2677
  %2683 = icmp sgt i64 %2682, -1
  br i1 %2683, label %2684, label %2794

2684:                                             ; preds = %2643, %2753
  %2685 = phi i64 [ %2792, %2753 ], [ %2682, %2643 ]
  %2686 = phi i64 [ %2754, %2753 ], [ 0, %2643 ]
  %2687 = shl nsw i64 %2685, 3
  %2688 = getelementptr inbounds nuw i8, ptr %72, i64 %2687
  %2689 = load i8, ptr %2688, align 8, !tbaa !18
  %2690 = zext i8 %2689 to i64
  %2691 = getelementptr inbounds nuw i8, ptr %2688, i64 1
  %2692 = load i8, ptr %2691, align 1, !tbaa !18
  %2693 = zext i8 %2692 to i64
  %2694 = shl nuw nsw i64 %2693, 8
  %2695 = or disjoint i64 %2694, %2690
  %2696 = getelementptr inbounds nuw i8, ptr %2688, i64 2
  %2697 = load i8, ptr %2696, align 2, !tbaa !18
  %2698 = zext i8 %2697 to i64
  %2699 = shl nuw nsw i64 %2698, 16
  %2700 = or disjoint i64 %2699, %2695
  %2701 = getelementptr inbounds nuw i8, ptr %2688, i64 3
  %2702 = load i8, ptr %2701, align 1, !tbaa !18
  %2703 = zext i8 %2702 to i64
  %2704 = shl nuw nsw i64 %2703, 24
  %2705 = or disjoint i64 %2704, %2700
  %2706 = getelementptr inbounds nuw i8, ptr %2688, i64 4
  %2707 = load i8, ptr %2706, align 4, !tbaa !18
  %2708 = zext i8 %2707 to i64
  %2709 = shl nuw nsw i64 %2708, 32
  %2710 = or disjoint i64 %2709, %2705
  %2711 = getelementptr inbounds nuw i8, ptr %2688, i64 5
  %2712 = load i8, ptr %2711, align 1, !tbaa !18
  %2713 = zext i8 %2712 to i64
  %2714 = shl nuw nsw i64 %2713, 40
  %2715 = or i64 %2714, %2710
  %2716 = getelementptr inbounds nuw i8, ptr %2688, i64 6
  %2717 = load i8, ptr %2716, align 2, !tbaa !18
  %2718 = zext i8 %2717 to i64
  %2719 = shl nuw nsw i64 %2718, 48
  %2720 = or i64 %2719, %2715
  %2721 = getelementptr inbounds nuw i8, ptr %2688, i64 7
  %2722 = load i8, ptr %2721, align 1, !tbaa !18
  %2723 = zext i8 %2722 to i64
  %2724 = shl nuw i64 %2723, 56
  %2725 = or i64 %2724, %2720
  %2726 = icmp eq i64 %2725, 9
  br i1 %2726, label %2727, label %2753

2727:                                             ; preds = %2684
  %2728 = shl nsw i64 %2686, 3
  %2729 = getelementptr inbounds i8, ptr %75, i64 %2728
  %2730 = trunc i64 %2685 to i8
  store i8 %2730, ptr %2729, align 8, !tbaa !18
  %2731 = lshr i64 %2685, 8
  %2732 = trunc i64 %2731 to i8
  %2733 = getelementptr inbounds nuw i8, ptr %2729, i64 1
  store i8 %2732, ptr %2733, align 1, !tbaa !18
  %2734 = lshr i64 %2685, 16
  %2735 = trunc i64 %2734 to i8
  %2736 = getelementptr inbounds nuw i8, ptr %2729, i64 2
  store i8 %2735, ptr %2736, align 2, !tbaa !18
  %2737 = lshr i64 %2685, 24
  %2738 = trunc i64 %2737 to i8
  %2739 = getelementptr inbounds nuw i8, ptr %2729, i64 3
  store i8 %2738, ptr %2739, align 1, !tbaa !18
  %2740 = lshr i64 %2685, 32
  %2741 = trunc i64 %2740 to i8
  %2742 = getelementptr inbounds nuw i8, ptr %2729, i64 4
  store i8 %2741, ptr %2742, align 4, !tbaa !18
  %2743 = lshr i64 %2685, 40
  %2744 = trunc i64 %2743 to i8
  %2745 = getelementptr inbounds nuw i8, ptr %2729, i64 5
  store i8 %2744, ptr %2745, align 1, !tbaa !18
  %2746 = lshr i64 %2685, 48
  %2747 = trunc i64 %2746 to i8
  %2748 = getelementptr inbounds nuw i8, ptr %2729, i64 6
  store i8 %2747, ptr %2748, align 2, !tbaa !18
  %2749 = lshr i64 %2685, 56
  %2750 = trunc nuw nsw i64 %2749 to i8
  %2751 = getelementptr inbounds nuw i8, ptr %2729, i64 7
  store i8 %2750, ptr %2751, align 1, !tbaa !18
  %2752 = add nsw i64 %2686, 1
  br label %2753

2753:                                             ; preds = %2727, %2684
  %2754 = phi i64 [ %2686, %2684 ], [ %2752, %2727 ]
  %2755 = getelementptr inbounds nuw i8, ptr %74, i64 %2687
  %2756 = load i8, ptr %2755, align 8, !tbaa !18
  %2757 = zext i8 %2756 to i64
  %2758 = getelementptr inbounds nuw i8, ptr %2755, i64 1
  %2759 = load i8, ptr %2758, align 1, !tbaa !18
  %2760 = zext i8 %2759 to i64
  %2761 = shl nuw nsw i64 %2760, 8
  %2762 = or disjoint i64 %2761, %2757
  %2763 = getelementptr inbounds nuw i8, ptr %2755, i64 2
  %2764 = load i8, ptr %2763, align 2, !tbaa !18
  %2765 = zext i8 %2764 to i64
  %2766 = shl nuw nsw i64 %2765, 16
  %2767 = or disjoint i64 %2766, %2762
  %2768 = getelementptr inbounds nuw i8, ptr %2755, i64 3
  %2769 = load i8, ptr %2768, align 1, !tbaa !18
  %2770 = zext i8 %2769 to i64
  %2771 = shl nuw nsw i64 %2770, 24
  %2772 = or disjoint i64 %2771, %2767
  %2773 = getelementptr inbounds nuw i8, ptr %2755, i64 4
  %2774 = load i8, ptr %2773, align 4, !tbaa !18
  %2775 = zext i8 %2774 to i64
  %2776 = shl nuw nsw i64 %2775, 32
  %2777 = or disjoint i64 %2776, %2772
  %2778 = getelementptr inbounds nuw i8, ptr %2755, i64 5
  %2779 = load i8, ptr %2778, align 1, !tbaa !18
  %2780 = zext i8 %2779 to i64
  %2781 = shl nuw nsw i64 %2780, 40
  %2782 = or i64 %2781, %2777
  %2783 = getelementptr inbounds nuw i8, ptr %2755, i64 6
  %2784 = load i8, ptr %2783, align 2, !tbaa !18
  %2785 = zext i8 %2784 to i64
  %2786 = shl nuw nsw i64 %2785, 48
  %2787 = or i64 %2786, %2782
  %2788 = getelementptr inbounds nuw i8, ptr %2755, i64 7
  %2789 = load i8, ptr %2788, align 1, !tbaa !18
  %2790 = zext i8 %2789 to i64
  %2791 = shl nuw i64 %2790, 56
  %2792 = or i64 %2791, %2787
  %2793 = icmp sgt i64 %2792, -1
  br i1 %2793, label %2684, label %2794, !llvm.loop !26

2794:                                             ; preds = %2753, %2643
  %2795 = phi i64 [ 0, %2643 ], [ %2754, %2753 ]
  %2796 = icmp eq i64 %2644, 2
  %2797 = icmp eq i64 %2795, 1
  %2798 = and i1 %2796, %2797
  %2799 = load i64, ptr %75, align 16
  %2800 = icmp eq i64 %2799, 3
  %2801 = select i1 %2798, i1 %2800, i1 false
  %2802 = select i1 %2801, ptr @.str.1, ptr @.str.2
  %2803 = call i32 (ptr, ...) @printf(ptr noundef nonnull dereferenceable(1) @.str.11, ptr noundef nonnull %2802, i64 noundef %2644, i64 noundef %2795)
  %2804 = call i32 (ptr, ...) @printf(ptr noundef nonnull dereferenceable(1) @.str.12, ptr noundef nonnull @.str.1, i64 noundef 2)
  %2805 = call i32 (ptr, ...) @printf(ptr noundef nonnull dereferenceable(1) @.str.13, ptr noundef nonnull @.str.1, i64 noundef 6)
  call void @llvm.lifetime.start.p0(ptr nonnull %79) #9
  call void @llvm.lifetime.start.p0(ptr nonnull %13) #9
  store i64 0, ptr %13, align 16, !tbaa !17
  br label %2806

2806:                                             ; preds = %2794, %2870
  %2807 = phi i64 [ %2851, %2870 ], [ 0, %2794 ]
  %2808 = phi i64 [ %2861, %2870 ], [ 0, %2794 ]
  %2809 = phi i64 [ %2871, %2870 ], [ 0, %2794 ]
  %2810 = phi i64 [ %2842, %2870 ], [ 0, %2794 ]
  %2811 = phi i64 [ %2872, %2870 ], [ 1, %2794 ]
  %2812 = getelementptr inbounds nuw [8 x i8], ptr %13, i64 %2810
  %2813 = load i64, ptr %2812, align 8, !tbaa !17
  %2814 = shl nsw i64 %2810, 3
  %2815 = getelementptr inbounds nuw i8, ptr %79, i64 %2814
  %2816 = trunc i64 %2813 to i8
  store i8 %2816, ptr %2815, align 8, !tbaa !18
  %2817 = lshr i64 %2813, 8
  %2818 = trunc i64 %2817 to i8
  %2819 = getelementptr inbounds nuw i8, ptr %2815, i64 1
  store i8 %2818, ptr %2819, align 1, !tbaa !18
  %2820 = lshr i64 %2813, 16
  %2821 = trunc i64 %2820 to i8
  %2822 = getelementptr inbounds nuw i8, ptr %2815, i64 2
  store i8 %2821, ptr %2822, align 2, !tbaa !18
  %2823 = lshr i64 %2813, 24
  %2824 = trunc i64 %2823 to i8
  %2825 = getelementptr inbounds nuw i8, ptr %2815, i64 3
  store i8 %2824, ptr %2825, align 1, !tbaa !18
  %2826 = lshr i64 %2813, 32
  %2827 = trunc i64 %2826 to i8
  %2828 = getelementptr inbounds nuw i8, ptr %2815, i64 4
  store i8 %2827, ptr %2828, align 4, !tbaa !18
  %2829 = lshr i64 %2813, 40
  %2830 = trunc i64 %2829 to i8
  %2831 = getelementptr inbounds nuw i8, ptr %2815, i64 5
  store i8 %2830, ptr %2831, align 1, !tbaa !18
  %2832 = lshr i64 %2813, 48
  %2833 = trunc i64 %2832 to i8
  %2834 = getelementptr inbounds nuw i8, ptr %2815, i64 6
  store i8 %2833, ptr %2834, align 2, !tbaa !18
  %2835 = lshr i64 %2813, 56
  %2836 = trunc nuw i64 %2835 to i8
  %2837 = getelementptr inbounds nuw i8, ptr %2815, i64 7
  store i8 %2836, ptr %2837, align 1, !tbaa !18
  %2838 = shl nsw i64 %2813, 3
  %2839 = getelementptr inbounds i8, ptr @__const.main.ba, i64 %2838
  %2840 = load i8, ptr %2839, align 8, !tbaa !18
  %2841 = zext i8 %2840 to i64
  %2842 = add nuw nsw i64 %2810, 1
  %2843 = and i64 %2841, 2
  %2844 = icmp eq i64 %2843, 0
  br i1 %2844, label %2850, label %2845

2845:                                             ; preds = %2806
  %2846 = icmp eq i64 %2807, 0
  br i1 %2846, label %2847, label %2850

2847:                                             ; preds = %2845
  %2848 = add nsw i64 %2811, 1
  %2849 = getelementptr inbounds [8 x i8], ptr %13, i64 %2811
  store i64 1, ptr %2849, align 8, !tbaa !17
  br label %2850

2850:                                             ; preds = %2847, %2845, %2806
  %2851 = phi i64 [ %2807, %2806 ], [ 1, %2847 ], [ 1, %2845 ]
  %2852 = phi i64 [ %2811, %2806 ], [ %2848, %2847 ], [ %2811, %2845 ]
  %2853 = and i64 %2841, 4
  %2854 = icmp eq i64 %2853, 0
  br i1 %2854, label %2860, label %2855

2855:                                             ; preds = %2850
  %2856 = icmp eq i64 %2808, 0
  br i1 %2856, label %2857, label %2860

2857:                                             ; preds = %2855
  %2858 = add nsw i64 %2852, 1
  %2859 = getelementptr inbounds [8 x i8], ptr %13, i64 %2852
  store i64 2, ptr %2859, align 8, !tbaa !17
  br label %2860

2860:                                             ; preds = %2857, %2855, %2850
  %2861 = phi i64 [ %2808, %2850 ], [ 1, %2857 ], [ 1, %2855 ]
  %2862 = phi i64 [ %2852, %2850 ], [ %2858, %2857 ], [ %2852, %2855 ]
  %2863 = and i64 %2841, 8
  %2864 = icmp eq i64 %2863, 0
  br i1 %2864, label %2870, label %2865

2865:                                             ; preds = %2860
  %2866 = icmp eq i64 %2809, 0
  br i1 %2866, label %2867, label %2870

2867:                                             ; preds = %2865
  %2868 = add nsw i64 %2862, 1
  %2869 = getelementptr inbounds [8 x i8], ptr %13, i64 %2862
  store i64 3, ptr %2869, align 8, !tbaa !17
  br label %2870

2870:                                             ; preds = %2867, %2865, %2860
  %2871 = phi i64 [ %2809, %2860 ], [ 1, %2867 ], [ 1, %2865 ]
  %2872 = phi i64 [ %2862, %2860 ], [ %2868, %2867 ], [ %2862, %2865 ]
  %2873 = icmp slt i64 %2842, %2872
  br i1 %2873, label %2806, label %2874, !llvm.loop !28

2874:                                             ; preds = %2870
  call void @llvm.lifetime.end.p0(ptr nonnull %13) #9
  %2875 = icmp eq i64 %2842, 3
  %2876 = load i64, ptr %79, align 16
  %2877 = icmp eq i64 %2876, 0
  %2878 = select i1 %2875, i1 %2877, i1 false
  %2879 = getelementptr inbounds nuw i8, ptr %79, i64 8
  %2880 = load i64, ptr %2879, align 8
  %2881 = icmp eq i64 %2880, 1
  %2882 = select i1 %2878, i1 %2881, i1 false
  %2883 = getelementptr inbounds nuw i8, ptr %79, i64 16
  %2884 = load i64, ptr %2883, align 16
  %2885 = icmp eq i64 %2884, 2
  %2886 = select i1 %2882, i1 %2885, i1 false
  %2887 = select i1 %2886, ptr @.str.1, ptr @.str.2
  %2888 = call i32 (ptr, ...) @printf(ptr noundef nonnull dereferenceable(1) @.str.14, ptr noundef nonnull %2887, i64 noundef %2842)
  call void @llvm.lifetime.start.p0(ptr nonnull %80) #9
  call void @llvm.lifetime.start.p0(ptr nonnull %12) #9
  store i64 0, ptr %12, align 16, !tbaa !17
  br label %2889

2889:                                             ; preds = %2943, %2874
  %2890 = phi i64 [ 1, %2874 ], [ %2946, %2943 ]
  %2891 = phi i64 [ 1, %2874 ], [ %2944, %2943 ]
  %2892 = phi i64 [ 1, %2874 ], [ %2945, %2943 ]
  %2893 = phi i64 [ 0, %2874 ], [ %2921, %2943 ]
  %2894 = phi i64 [ 1, %2874 ], [ %2947, %2943 ]
  %2895 = getelementptr inbounds nuw [8 x i8], ptr %12, i64 %2893
  %2896 = load i64, ptr %2895, align 8, !tbaa !17
  %2897 = shl nsw i64 %2893, 3
  %2898 = getelementptr inbounds nuw i8, ptr %80, i64 %2897
  %2899 = trunc i64 %2896 to i8
  store i8 %2899, ptr %2898, align 8, !tbaa !18
  %2900 = lshr i64 %2896, 8
  %2901 = trunc i64 %2900 to i8
  %2902 = getelementptr inbounds nuw i8, ptr %2898, i64 1
  store i8 %2901, ptr %2902, align 1, !tbaa !18
  %2903 = lshr i64 %2896, 16
  %2904 = trunc i64 %2903 to i8
  %2905 = getelementptr inbounds nuw i8, ptr %2898, i64 2
  store i8 %2904, ptr %2905, align 2, !tbaa !18
  %2906 = lshr i64 %2896, 24
  %2907 = trunc i64 %2906 to i8
  %2908 = getelementptr inbounds nuw i8, ptr %2898, i64 3
  store i8 %2907, ptr %2908, align 1, !tbaa !18
  %2909 = lshr i64 %2896, 32
  %2910 = trunc i64 %2909 to i8
  %2911 = getelementptr inbounds nuw i8, ptr %2898, i64 4
  store i8 %2910, ptr %2911, align 4, !tbaa !18
  %2912 = lshr i64 %2896, 40
  %2913 = trunc i64 %2912 to i8
  %2914 = getelementptr inbounds nuw i8, ptr %2898, i64 5
  store i8 %2913, ptr %2914, align 1, !tbaa !18
  %2915 = lshr i64 %2896, 48
  %2916 = trunc i64 %2915 to i8
  %2917 = getelementptr inbounds nuw i8, ptr %2898, i64 6
  store i8 %2916, ptr %2917, align 2, !tbaa !18
  %2918 = lshr i64 %2896, 56
  %2919 = trunc nuw i64 %2918 to i8
  %2920 = getelementptr inbounds nuw i8, ptr %2898, i64 7
  store i8 %2919, ptr %2920, align 1, !tbaa !18
  %2921 = add nuw nsw i64 %2893, 1
  switch i64 %2896, label %2943 [
    i64 0, label %2922
    i64 1, label %2928
  ]

2922:                                             ; preds = %2889
  %2923 = add nsw i64 %2892, -1
  %2924 = icmp eq i64 %2923, 0
  br i1 %2924, label %2925, label %2931

2925:                                             ; preds = %2922
  %2926 = add nsw i64 %2894, 1
  %2927 = getelementptr inbounds [8 x i8], ptr %12, i64 %2894
  store i64 1, ptr %2927, align 8, !tbaa !17
  br label %2931

2928:                                             ; preds = %2889
  %2929 = add nsw i64 %2891, -1
  %2930 = icmp eq i64 %2929, 0
  br i1 %2930, label %2935, label %2943

2931:                                             ; preds = %2922, %2925
  %2932 = phi i64 [ %2894, %2922 ], [ %2926, %2925 ]
  %2933 = add nsw i64 %2890, -1
  %2934 = icmp eq i64 %2933, 0
  br i1 %2934, label %2935, label %2943

2935:                                             ; preds = %2931, %2928
  %2936 = phi i64 [ %2894, %2928 ], [ %2932, %2931 ]
  %2937 = phi i64 [ 2, %2928 ], [ 3, %2931 ]
  %2938 = phi i64 [ 0, %2928 ], [ %2891, %2931 ]
  %2939 = phi i64 [ %2892, %2928 ], [ %2923, %2931 ]
  %2940 = phi i64 [ %2890, %2928 ], [ 0, %2931 ]
  %2941 = add nsw i64 %2936, 1
  %2942 = getelementptr inbounds [8 x i8], ptr %12, i64 %2936
  store i64 %2937, ptr %2942, align 8, !tbaa !17
  br label %2943

2943:                                             ; preds = %2935, %2889, %2928, %2931
  %2944 = phi i64 [ %2929, %2928 ], [ %2891, %2931 ], [ %2891, %2889 ], [ %2938, %2935 ]
  %2945 = phi i64 [ %2892, %2928 ], [ %2923, %2931 ], [ %2892, %2889 ], [ %2939, %2935 ]
  %2946 = phi i64 [ %2890, %2928 ], [ %2933, %2931 ], [ %2890, %2889 ], [ %2940, %2935 ]
  %2947 = phi i64 [ %2894, %2928 ], [ %2932, %2931 ], [ %2894, %2889 ], [ %2941, %2935 ]
  %2948 = icmp slt i64 %2921, %2947
  br i1 %2948, label %2889, label %2949, !llvm.loop !29

2949:                                             ; preds = %2943
  %2950 = load i64, ptr %80, align 16
  call void @llvm.lifetime.end.p0(ptr nonnull %12) #9
  %2951 = icmp eq i64 %2921, 4
  %2952 = icmp eq i64 %2950, 0
  %2953 = select i1 %2951, i1 %2952, i1 false
  %2954 = select i1 %2953, ptr @.str.1, ptr @.str.2
  %2955 = call i32 (ptr, ...) @printf(ptr noundef nonnull dereferenceable(1) @.str.15, ptr noundef nonnull %2954, i64 noundef %2921)
  call void @llvm.lifetime.start.p0(ptr nonnull %81) #9
  call void @llvm.memcpy.p0.p0.i64(ptr noundef nonnull align 16 dereferenceable(32) %81, ptr noundef nonnull align 16 dereferenceable(32) @__const.main.pp, i64 32, i1 false)
  %2956 = getelementptr inbounds nuw i8, ptr %81, i64 8
  store i64 0, ptr %2956, align 8, !tbaa !17
  %2957 = getelementptr inbounds nuw i8, ptr %81, i64 16
  %2958 = getelementptr inbounds nuw i8, ptr %81, i64 24
  store i64 2, ptr %2958, align 8, !tbaa !17
  br label %2959

2959:                                             ; preds = %2949, %2959
  %2960 = phi i64 [ %2965, %2959 ], [ 0, %2949 ]
  %2961 = phi ptr [ %2964, %2959 ], [ %2956, %2949 ]
  %2962 = getelementptr inbounds [8 x i8], ptr %81, i64 %2960
  %2963 = load i64, ptr %2962, align 8, !tbaa !17
  store i64 %2963, ptr %2961, align 8, !tbaa !17
  %2964 = getelementptr inbounds [8 x i8], ptr %81, i64 %2963
  %2965 = load i64, ptr %2964, align 8, !tbaa !17
  %2966 = icmp eq i64 %2965, %2963
  br i1 %2966, label %2967, label %2959, !llvm.loop !30

2967:                                             ; preds = %2959
  %2968 = load i64, ptr %2957, align 16, !tbaa !17
  %2969 = icmp eq i64 %2968, 2
  br i1 %2969, label %2978, label %2970

2970:                                             ; preds = %2967, %2970
  %2971 = phi i64 [ %2976, %2970 ], [ %2968, %2967 ]
  %2972 = phi ptr [ %2975, %2970 ], [ %2957, %2967 ]
  %2973 = getelementptr inbounds [8 x i8], ptr %81, i64 %2971
  %2974 = load i64, ptr %2973, align 8, !tbaa !17
  store i64 %2974, ptr %2972, align 8, !tbaa !17
  %2975 = getelementptr inbounds [8 x i8], ptr %81, i64 %2974
  %2976 = load i64, ptr %2975, align 8, !tbaa !17
  %2977 = icmp eq i64 %2976, %2974
  br i1 %2977, label %2978, label %2970, !llvm.loop !30

2978:                                             ; preds = %2970, %2967
  %2979 = phi i64 [ 2, %2967 ], [ %2974, %2970 ]
  %2980 = icmp eq i64 %2963, %2979
  br i1 %2980, label %3382, label %3354

2981:                                             ; preds = %2317
  %2982 = call i32 (ptr, ...) @printf(ptr noundef nonnull dereferenceable(1) @.str.6, i32 noundef 0, i64 noundef %2531, i64 noundef %2384)
  br label %2983

2983:                                             ; preds = %2317, %2981
  %2984 = phi i32 [ 0, %2981 ], [ 1, %2317 ]
  %2985 = getelementptr inbounds nuw i8, ptr %61, i64 8
  %2986 = load i64, ptr %2985, align 8, !tbaa !17
  %2987 = icmp eq i64 %2986, %2386
  br i1 %2987, label %2990, label %2988

2988:                                             ; preds = %2983
  %2989 = call i32 (ptr, ...) @printf(ptr noundef nonnull dereferenceable(1) @.str.6, i32 noundef 1, i64 noundef %2986, i64 noundef %2386)
  br label %2990

2990:                                             ; preds = %2988, %2983
  %2991 = phi i32 [ 0, %2988 ], [ %2984, %2983 ]
  %2992 = getelementptr inbounds nuw i8, ptr %61, i64 16
  %2993 = load i64, ptr %2992, align 16, !tbaa !17
  %2994 = icmp eq i64 %2993, %2388
  br i1 %2994, label %2997, label %2995

2995:                                             ; preds = %2990
  %2996 = call i32 (ptr, ...) @printf(ptr noundef nonnull dereferenceable(1) @.str.6, i32 noundef 2, i64 noundef %2993, i64 noundef %2388)
  br label %2997

2997:                                             ; preds = %2995, %2990
  %2998 = phi i32 [ 0, %2995 ], [ %2991, %2990 ]
  %2999 = getelementptr inbounds nuw i8, ptr %61, i64 24
  %3000 = load i64, ptr %2999, align 8, !tbaa !17
  %3001 = icmp eq i64 %3000, %2390
  br i1 %3001, label %3004, label %3002

3002:                                             ; preds = %2997
  %3003 = call i32 (ptr, ...) @printf(ptr noundef nonnull dereferenceable(1) @.str.6, i32 noundef 3, i64 noundef %3000, i64 noundef %2390)
  br label %3004

3004:                                             ; preds = %3002, %2997
  %3005 = phi i32 [ 0, %3002 ], [ %2998, %2997 ]
  %3006 = getelementptr inbounds nuw i8, ptr %61, i64 32
  %3007 = load i64, ptr %3006, align 16, !tbaa !17
  %3008 = icmp eq i64 %3007, %2454
  br i1 %3008, label %3011, label %3009

3009:                                             ; preds = %3004
  %3010 = call i32 (ptr, ...) @printf(ptr noundef nonnull dereferenceable(1) @.str.6, i32 noundef 4, i64 noundef %3007, i64 noundef %2454)
  br label %3011

3011:                                             ; preds = %3009, %3004
  %3012 = phi i32 [ 0, %3009 ], [ %3005, %3004 ]
  %3013 = getelementptr inbounds nuw i8, ptr %61, i64 40
  %3014 = load i64, ptr %3013, align 8, !tbaa !17
  %3015 = icmp eq i64 %3014, %2456
  br i1 %3015, label %3018, label %3016

3016:                                             ; preds = %3011
  %3017 = call i32 (ptr, ...) @printf(ptr noundef nonnull dereferenceable(1) @.str.6, i32 noundef 5, i64 noundef %3014, i64 noundef %2456)
  br label %3018

3018:                                             ; preds = %3016, %3011
  %3019 = phi i32 [ 0, %3016 ], [ %3012, %3011 ]
  %3020 = getelementptr inbounds nuw i8, ptr %61, i64 48
  %3021 = load i64, ptr %3020, align 16, !tbaa !17
  %3022 = icmp eq i64 %3021, %2458
  br i1 %3022, label %3025, label %3023

3023:                                             ; preds = %3018
  %3024 = call i32 (ptr, ...) @printf(ptr noundef nonnull dereferenceable(1) @.str.6, i32 noundef 6, i64 noundef %3021, i64 noundef %2458)
  br label %3025

3025:                                             ; preds = %3023, %3018
  %3026 = phi i32 [ 0, %3023 ], [ %3019, %3018 ]
  %3027 = getelementptr inbounds nuw i8, ptr %61, i64 56
  %3028 = load i64, ptr %3027, align 8, !tbaa !17
  %3029 = icmp eq i64 %3028, %2460
  br i1 %3029, label %3032, label %3030

3030:                                             ; preds = %3025
  %3031 = call i32 (ptr, ...) @printf(ptr noundef nonnull dereferenceable(1) @.str.6, i32 noundef 7, i64 noundef %3028, i64 noundef %2460)
  br label %3032

3032:                                             ; preds = %3030, %3025
  %3033 = phi i32 [ 0, %3030 ], [ %3026, %3025 ]
  %3034 = getelementptr inbounds nuw i8, ptr %61, i64 64
  %3035 = load i64, ptr %3034, align 16, !tbaa !17
  %3036 = icmp eq i64 %3035, %2524
  br i1 %3036, label %3039, label %3037

3037:                                             ; preds = %3032
  %3038 = call i32 (ptr, ...) @printf(ptr noundef nonnull dereferenceable(1) @.str.6, i32 noundef 8, i64 noundef %3035, i64 noundef %2524)
  br label %3039

3039:                                             ; preds = %3037, %3032
  %3040 = phi i32 [ 0, %3037 ], [ %3033, %3032 ]
  %3041 = getelementptr inbounds nuw i8, ptr %61, i64 72
  %3042 = load i64, ptr %3041, align 8, !tbaa !17
  %3043 = icmp eq i64 %3042, %2526
  br i1 %3043, label %3046, label %3044

3044:                                             ; preds = %3039
  %3045 = call i32 (ptr, ...) @printf(ptr noundef nonnull dereferenceable(1) @.str.6, i32 noundef 9, i64 noundef %3042, i64 noundef %2526)
  br label %3046

3046:                                             ; preds = %3044, %3039
  %3047 = phi i32 [ 0, %3044 ], [ %3040, %3039 ]
  %3048 = getelementptr inbounds nuw i8, ptr %61, i64 80
  %3049 = load i64, ptr %3048, align 16, !tbaa !17
  %3050 = icmp eq i64 %3049, %2528
  br i1 %3050, label %3053, label %3051

3051:                                             ; preds = %3046
  %3052 = call i32 (ptr, ...) @printf(ptr noundef nonnull dereferenceable(1) @.str.6, i32 noundef 10, i64 noundef %3049, i64 noundef %2528)
  br label %3053

3053:                                             ; preds = %3051, %3046
  %3054 = phi i32 [ 0, %3051 ], [ %3047, %3046 ]
  %3055 = getelementptr inbounds nuw i8, ptr %61, i64 88
  %3056 = load i64, ptr %3055, align 8, !tbaa !17
  %3057 = icmp eq i64 %3056, %2530
  br i1 %3057, label %3060, label %3058

3058:                                             ; preds = %3053
  %3059 = call i32 (ptr, ...) @printf(ptr noundef nonnull dereferenceable(1) @.str.6, i32 noundef 11, i64 noundef %3056, i64 noundef %2530)
  br label %3063

3060:                                             ; preds = %3053
  %3061 = freeze i32 %3054
  %3062 = icmp eq i32 %3061, 0
  br i1 %3062, label %3063, label %3064

3063:                                             ; preds = %3058, %3060
  br label %3064

3064:                                             ; preds = %3060, %3063
  %3065 = phi ptr [ @.str.2, %3063 ], [ @.str.1, %3060 ]
  %3066 = call i32 (ptr, ...) @printf(ptr noundef nonnull dereferenceable(1) @.str.7, ptr noundef nonnull %3065)
  call void @llvm.lifetime.start.p0(ptr nonnull %64) #9
  store i64 5, ptr %64, align 16
  %3067 = getelementptr inbounds nuw i8, ptr %64, i64 8
  store i64 1, ptr %3067, align 8
  %3068 = getelementptr inbounds nuw i8, ptr %64, i64 16
  store i64 9, ptr %3068, align 16
  %3069 = getelementptr inbounds nuw i8, ptr %64, i64 24
  store i64 3, ptr %3069, align 8
  %3070 = getelementptr inbounds nuw i8, ptr %64, i64 32
  store i64 7, ptr %3070, align 16
  call void @llvm.lifetime.start.p0(ptr nonnull %65) #9
  store i64 10, ptr %65, align 16
  %3071 = getelementptr inbounds nuw i8, ptr %65, i64 8
  store i64 11, ptr %3071, align 8
  %3072 = getelementptr inbounds nuw i8, ptr %65, i64 16
  store i64 12, ptr %3072, align 16
  %3073 = getelementptr inbounds nuw i8, ptr %65, i64 24
  store i64 13, ptr %3073, align 8
  %3074 = getelementptr inbounds nuw i8, ptr %65, i64 32
  store i64 14, ptr %3074, align 16
  call void @llvm.lifetime.start.p0(ptr nonnull %66) #9
  call void @llvm.lifetime.start.p0(ptr nonnull %67) #9
  call void @llvm.lifetime.start.p0(ptr nonnull %68) #9
  store ptr %64, ptr %68, align 8, !tbaa !9
  %3075 = getelementptr inbounds nuw i8, ptr %68, i64 8
  store i64 5, ptr %3075, align 8, !tbaa !14
  %3076 = getelementptr inbounds nuw i8, ptr %68, i64 16
  store i64 8, ptr %3076, align 8, !tbaa !15
  %3077 = getelementptr inbounds nuw i8, ptr %68, i64 24
  store i64 8, ptr %3077, align 8, !tbaa !16
  call void @llvm.lifetime.start.p0(ptr nonnull %69) #9
  store ptr %65, ptr %69, align 8, !tbaa !9
  %3078 = getelementptr inbounds nuw i8, ptr %69, i64 8
  store i64 5, ptr %3078, align 8, !tbaa !14
  %3079 = getelementptr inbounds nuw i8, ptr %69, i64 16
  store i64 8, ptr %3079, align 8, !tbaa !15
  %3080 = getelementptr inbounds nuw i8, ptr %69, i64 24
  store i64 8, ptr %3080, align 8, !tbaa !16
  call void @llvm.lifetime.start.p0(ptr nonnull %70) #9
  store ptr %66, ptr %70, align 8, !tbaa !9
  %3081 = getelementptr inbounds nuw i8, ptr %70, i64 8
  store i64 3, ptr %3081, align 8, !tbaa !14
  %3082 = getelementptr inbounds nuw i8, ptr %70, i64 16
  store i64 8, ptr %3082, align 8, !tbaa !15
  %3083 = getelementptr inbounds nuw i8, ptr %70, i64 24
  store i64 8, ptr %3083, align 8, !tbaa !16
  call void @llvm.lifetime.start.p0(ptr nonnull %71) #9
  store ptr %67, ptr %71, align 8, !tbaa !9
  %3084 = getelementptr inbounds nuw i8, ptr %71, i64 8
  store i64 3, ptr %3084, align 8, !tbaa !14
  %3085 = getelementptr inbounds nuw i8, ptr %71, i64 16
  store i64 8, ptr %3085, align 8, !tbaa !15
  %3086 = getelementptr inbounds nuw i8, ptr %71, i64 24
  store i64 8, ptr %3086, align 8, !tbaa !16
  call fastcc void @topk(ptr noundef %68, i64 noundef 5, ptr noundef %69, ptr noundef %70, ptr noundef %71)
  %3087 = load i64, ptr %66, align 16, !tbaa !17
  %3088 = icmp eq i64 %3087, 12
  %3089 = getelementptr inbounds nuw i8, ptr %66, i64 8
  %3090 = load i64, ptr %3089, align 8
  %3091 = icmp eq i64 %3090, 14
  %3092 = select i1 %3088, i1 %3091, i1 false
  %3093 = getelementptr inbounds nuw i8, ptr %66, i64 16
  %3094 = load i64, ptr %3093, align 16
  %3095 = icmp eq i64 %3094, 10
  %3096 = select i1 %3092, i1 %3095, i1 false
  %3097 = load i64, ptr %67, align 16
  %3098 = icmp eq i64 %3097, 9
  %3099 = select i1 %3096, i1 %3098, i1 false
  %3100 = getelementptr inbounds nuw i8, ptr %67, i64 8
  %3101 = load i64, ptr %3100, align 8
  %3102 = icmp eq i64 %3101, 7
  %3103 = select i1 %3099, i1 %3102, i1 false
  %3104 = getelementptr inbounds nuw i8, ptr %67, i64 16
  %3105 = load i64, ptr %3104, align 16
  %3106 = icmp eq i64 %3105, 5
  %3107 = select i1 %3103, i1 %3106, i1 false
  %3108 = select i1 %3107, ptr @.str.1, ptr @.str.2
  %3109 = call i32 (ptr, ...) @printf(ptr noundef nonnull dereferenceable(1) @.str.8, ptr noundef nonnull %3108)
  %3110 = load i8, ptr %64, align 16, !tbaa !18
  %3111 = getelementptr inbounds nuw i8, ptr %64, i64 1
  %3112 = load i8, ptr %3111, align 1, !tbaa !18
  %3113 = getelementptr inbounds nuw i8, ptr %64, i64 2
  %3114 = load i8, ptr %3113, align 2, !tbaa !18
  %3115 = getelementptr inbounds nuw i8, ptr %64, i64 3
  %3116 = load i8, ptr %3115, align 1, !tbaa !18
  %3117 = getelementptr inbounds nuw i8, ptr %64, i64 4
  %3118 = load i8, ptr %3117, align 4, !tbaa !18
  %3119 = getelementptr inbounds nuw i8, ptr %64, i64 5
  %3120 = load i8, ptr %3119, align 1, !tbaa !18
  %3121 = getelementptr inbounds nuw i8, ptr %64, i64 6
  %3122 = load i8, ptr %3121, align 2, !tbaa !18
  %3123 = getelementptr inbounds nuw i8, ptr %64, i64 7
  %3124 = load i8, ptr %3123, align 1, !tbaa !18
  %3125 = load i8, ptr %3067, align 8, !tbaa !18
  %3126 = getelementptr inbounds nuw i8, ptr %64, i64 9
  %3127 = load i8, ptr %3126, align 1, !tbaa !18
  %3128 = getelementptr inbounds nuw i8, ptr %64, i64 10
  %3129 = load i8, ptr %3128, align 2, !tbaa !18
  %3130 = getelementptr inbounds nuw i8, ptr %64, i64 11
  %3131 = load i8, ptr %3130, align 1, !tbaa !18
  %3132 = getelementptr inbounds nuw i8, ptr %64, i64 12
  %3133 = load i8, ptr %3132, align 4, !tbaa !18
  %3134 = getelementptr inbounds nuw i8, ptr %64, i64 13
  %3135 = load i8, ptr %3134, align 1, !tbaa !18
  %3136 = getelementptr inbounds nuw i8, ptr %64, i64 14
  %3137 = load i8, ptr %3136, align 2, !tbaa !18
  %3138 = getelementptr inbounds nuw i8, ptr %64, i64 15
  %3139 = load i8, ptr %3138, align 1, !tbaa !18
  %3140 = load i8, ptr %3068, align 16, !tbaa !18
  %3141 = getelementptr inbounds nuw i8, ptr %64, i64 17
  %3142 = load i8, ptr %3141, align 1, !tbaa !18
  %3143 = getelementptr inbounds nuw i8, ptr %64, i64 18
  %3144 = load i8, ptr %3143, align 2, !tbaa !18
  %3145 = getelementptr inbounds nuw i8, ptr %64, i64 19
  %3146 = load i8, ptr %3145, align 1, !tbaa !18
  %3147 = getelementptr inbounds nuw i8, ptr %64, i64 20
  %3148 = load i8, ptr %3147, align 4, !tbaa !18
  %3149 = getelementptr inbounds nuw i8, ptr %64, i64 21
  %3150 = load i8, ptr %3149, align 1, !tbaa !18
  %3151 = getelementptr inbounds nuw i8, ptr %64, i64 22
  %3152 = load i8, ptr %3151, align 2, !tbaa !18
  %3153 = getelementptr inbounds nuw i8, ptr %64, i64 23
  %3154 = load i8, ptr %3153, align 1, !tbaa !18
  %3155 = load i8, ptr %3069, align 8, !tbaa !18
  %3156 = getelementptr inbounds nuw i8, ptr %64, i64 25
  %3157 = load i8, ptr %3156, align 1, !tbaa !18
  %3158 = getelementptr inbounds nuw i8, ptr %64, i64 26
  %3159 = load i8, ptr %3158, align 2, !tbaa !18
  %3160 = getelementptr inbounds nuw i8, ptr %64, i64 27
  %3161 = load i8, ptr %3160, align 1, !tbaa !18
  %3162 = getelementptr inbounds nuw i8, ptr %64, i64 28
  %3163 = load i8, ptr %3162, align 4, !tbaa !18
  %3164 = getelementptr inbounds nuw i8, ptr %64, i64 29
  %3165 = load i8, ptr %3164, align 1, !tbaa !18
  %3166 = getelementptr inbounds nuw i8, ptr %64, i64 30
  %3167 = load i8, ptr %3166, align 2, !tbaa !18
  %3168 = getelementptr inbounds nuw i8, ptr %64, i64 31
  %3169 = load i8, ptr %3168, align 1, !tbaa !18
  %3170 = load i8, ptr %3070, align 16, !tbaa !18
  %3171 = zext i8 %3170 to i64
  %3172 = getelementptr inbounds nuw i8, ptr %64, i64 33
  %3173 = load i8, ptr %3172, align 1, !tbaa !18
  %3174 = zext i8 %3173 to i64
  %3175 = shl nuw nsw i64 %3174, 8
  %3176 = or disjoint i64 %3175, %3171
  %3177 = getelementptr inbounds nuw i8, ptr %64, i64 34
  %3178 = load i8, ptr %3177, align 2, !tbaa !18
  %3179 = zext i8 %3178 to i64
  %3180 = shl nuw nsw i64 %3179, 16
  %3181 = or disjoint i64 %3180, %3176
  %3182 = getelementptr inbounds nuw i8, ptr %64, i64 35
  %3183 = load i8, ptr %3182, align 1, !tbaa !18
  %3184 = zext i8 %3183 to i64
  %3185 = shl nuw nsw i64 %3184, 24
  %3186 = or disjoint i64 %3185, %3181
  %3187 = getelementptr inbounds nuw i8, ptr %64, i64 36
  %3188 = load i8, ptr %3187, align 4, !tbaa !18
  %3189 = zext i8 %3188 to i64
  %3190 = shl nuw nsw i64 %3189, 32
  %3191 = or disjoint i64 %3190, %3186
  %3192 = getelementptr inbounds nuw i8, ptr %64, i64 37
  %3193 = load i8, ptr %3192, align 1, !tbaa !18
  %3194 = zext i8 %3193 to i64
  %3195 = shl nuw nsw i64 %3194, 40
  %3196 = or i64 %3195, %3191
  %3197 = getelementptr inbounds nuw i8, ptr %64, i64 38
  %3198 = load i8, ptr %3197, align 2, !tbaa !18
  %3199 = zext i8 %3198 to i64
  %3200 = shl nuw nsw i64 %3199, 48
  %3201 = or i64 %3200, %3196
  %3202 = getelementptr inbounds nuw i8, ptr %64, i64 39
  %3203 = load i8, ptr %3202, align 1, !tbaa !18
  %3204 = zext i8 %3203 to i64
  %3205 = shl nuw i64 %3204, 56
  %3206 = or i64 %3205, %3201
  %3207 = zext i8 %3155 to i64
  %3208 = zext i8 %3157 to i64
  %3209 = shl nuw nsw i64 %3208, 8
  %3210 = or disjoint i64 %3209, %3207
  %3211 = zext i8 %3159 to i64
  %3212 = shl nuw nsw i64 %3211, 16
  %3213 = or disjoint i64 %3212, %3210
  %3214 = zext i8 %3161 to i64
  %3215 = shl nuw nsw i64 %3214, 24
  %3216 = or disjoint i64 %3215, %3213
  %3217 = zext i8 %3163 to i64
  %3218 = shl nuw nsw i64 %3217, 32
  %3219 = or disjoint i64 %3218, %3216
  %3220 = zext i8 %3165 to i64
  %3221 = shl nuw nsw i64 %3220, 40
  %3222 = or i64 %3221, %3219
  %3223 = zext i8 %3167 to i64
  %3224 = shl nuw nsw i64 %3223, 48
  %3225 = or i64 %3224, %3222
  %3226 = zext i8 %3169 to i64
  %3227 = shl nuw i64 %3226, 56
  %3228 = or i64 %3227, %3225
  %3229 = zext i8 %3140 to i64
  %3230 = zext i8 %3142 to i64
  %3231 = shl nuw nsw i64 %3230, 8
  %3232 = or disjoint i64 %3231, %3229
  %3233 = zext i8 %3144 to i64
  %3234 = shl nuw nsw i64 %3233, 16
  %3235 = or disjoint i64 %3234, %3232
  %3236 = zext i8 %3146 to i64
  %3237 = shl nuw nsw i64 %3236, 24
  %3238 = or disjoint i64 %3237, %3235
  %3239 = zext i8 %3148 to i64
  %3240 = shl nuw nsw i64 %3239, 32
  %3241 = or disjoint i64 %3240, %3238
  %3242 = zext i8 %3150 to i64
  %3243 = shl nuw nsw i64 %3242, 40
  %3244 = or i64 %3243, %3241
  %3245 = zext i8 %3152 to i64
  %3246 = shl nuw nsw i64 %3245, 48
  %3247 = or i64 %3246, %3244
  %3248 = zext i8 %3154 to i64
  %3249 = shl nuw i64 %3248, 56
  %3250 = or i64 %3249, %3247
  %3251 = zext i8 %3125 to i64
  %3252 = zext i8 %3127 to i64
  %3253 = shl nuw nsw i64 %3252, 8
  %3254 = or disjoint i64 %3253, %3251
  %3255 = zext i8 %3129 to i64
  %3256 = shl nuw nsw i64 %3255, 16
  %3257 = or disjoint i64 %3256, %3254
  %3258 = zext i8 %3131 to i64
  %3259 = shl nuw nsw i64 %3258, 24
  %3260 = or disjoint i64 %3259, %3257
  %3261 = zext i8 %3133 to i64
  %3262 = shl nuw nsw i64 %3261, 32
  %3263 = or disjoint i64 %3262, %3260
  %3264 = zext i8 %3135 to i64
  %3265 = shl nuw nsw i64 %3264, 40
  %3266 = or i64 %3265, %3263
  %3267 = zext i8 %3137 to i64
  %3268 = shl nuw nsw i64 %3267, 48
  %3269 = or i64 %3268, %3266
  %3270 = zext i8 %3139 to i64
  %3271 = shl nuw i64 %3270, 56
  %3272 = or i64 %3271, %3269
  %3273 = zext i8 %3110 to i64
  %3274 = zext i8 %3112 to i64
  %3275 = shl nuw nsw i64 %3274, 8
  %3276 = or disjoint i64 %3275, %3273
  %3277 = zext i8 %3114 to i64
  %3278 = shl nuw nsw i64 %3277, 16
  %3279 = or disjoint i64 %3278, %3276
  %3280 = zext i8 %3116 to i64
  %3281 = shl nuw nsw i64 %3280, 24
  %3282 = or disjoint i64 %3281, %3279
  %3283 = zext i8 %3118 to i64
  %3284 = shl nuw nsw i64 %3283, 32
  %3285 = or disjoint i64 %3284, %3282
  %3286 = zext i8 %3120 to i64
  %3287 = shl nuw nsw i64 %3286, 40
  %3288 = or i64 %3287, %3285
  %3289 = zext i8 %3122 to i64
  %3290 = shl nuw nsw i64 %3289, 48
  %3291 = or i64 %3290, %3288
  %3292 = zext i8 %3124 to i64
  %3293 = shl nuw i64 %3292, 56
  %3294 = or i64 %3293, %3291
  %3295 = call i64 @llvm.smax.i64(i64 %3272, i64 %3294)
  %3296 = icmp sgt i64 %3250, %3295
  %3297 = call i64 @llvm.smax.i64(i64 %3250, i64 %3295)
  %3298 = icmp sle i64 %3228, %3297
  %3299 = call i64 @llvm.smax.i64(i64 %3228, i64 %3297)
  %3300 = icmp sle i64 %3206, %3299
  %3301 = and i1 %3296, %3298
  %3302 = select i1 %3300, i1 %3301, i1 false
  %3303 = select i1 %3302, ptr @.str.1, ptr @.str.2
  %3304 = call i32 (ptr, ...) @printf(ptr noundef nonnull dereferenceable(1) @.str.9, ptr noundef nonnull %3303)
  %3305 = call i32 (ptr, ...) @printf(ptr noundef nonnull dereferenceable(1) @.str.10, ptr noundef nonnull @.str.1, i64 noundef 3)
  call void @llvm.lifetime.start.p0(ptr nonnull %72) #9
  call void @llvm.memcpy.p0.p0.i64(ptr noundef nonnull align 16 dereferenceable(32) %72, ptr noundef nonnull align 16 dereferenceable(32) @__const.main.ik, i64 32, i1 false)
  call void @llvm.lifetime.start.p0(ptr nonnull %73) #9
  call void @llvm.lifetime.start.p0(ptr nonnull %74) #9
  call void @llvm.lifetime.start.p0(ptr nonnull %75) #9
  call void @llvm.lifetime.start.p0(ptr nonnull %76) #9
  store ptr %72, ptr %76, align 8, !tbaa !9
  %3306 = getelementptr inbounds nuw i8, ptr %76, i64 8
  store i64 4, ptr %3306, align 8, !tbaa !14
  %3307 = getelementptr inbounds nuw i8, ptr %76, i64 16
  store i64 8, ptr %3307, align 8, !tbaa !15
  %3308 = getelementptr inbounds nuw i8, ptr %76, i64 24
  store i64 8, ptr %3308, align 8, !tbaa !16
  call void @llvm.lifetime.start.p0(ptr nonnull %77) #9
  store ptr %73, ptr %77, align 8, !tbaa !9
  %3309 = getelementptr inbounds nuw i8, ptr %77, i64 8
  store i64 8, ptr %3309, align 8, !tbaa !14
  %3310 = getelementptr inbounds nuw i8, ptr %77, i64 16
  store i64 8, ptr %3310, align 8, !tbaa !15
  %3311 = getelementptr inbounds nuw i8, ptr %77, i64 24
  store i64 8, ptr %3311, align 8, !tbaa !16
  call void @llvm.lifetime.start.p0(ptr nonnull %78) #9
  store ptr %74, ptr %78, align 8, !tbaa !9
  %3312 = getelementptr inbounds nuw i8, ptr %78, i64 8
  store i64 4, ptr %3312, align 8, !tbaa !14
  %3313 = getelementptr inbounds nuw i8, ptr %78, i64 16
  store i64 8, ptr %3313, align 8, !tbaa !15
  %3314 = getelementptr inbounds nuw i8, ptr %78, i64 24
  store i64 8, ptr %3314, align 8, !tbaa !16
  call fastcc void @build_index(ptr noundef %76, ptr noundef %77, ptr noundef %78)
  %3315 = getelementptr inbounds nuw i8, ptr %73, i64 24
  %3316 = load i8, ptr %3315, align 8, !tbaa !18
  %3317 = zext i8 %3316 to i64
  %3318 = getelementptr inbounds nuw i8, ptr %73, i64 25
  %3319 = load i8, ptr %3318, align 1, !tbaa !18
  %3320 = zext i8 %3319 to i64
  %3321 = shl nuw nsw i64 %3320, 8
  %3322 = or disjoint i64 %3321, %3317
  %3323 = getelementptr inbounds nuw i8, ptr %73, i64 26
  %3324 = load i8, ptr %3323, align 2, !tbaa !18
  %3325 = zext i8 %3324 to i64
  %3326 = shl nuw nsw i64 %3325, 16
  %3327 = or disjoint i64 %3326, %3322
  %3328 = getelementptr inbounds nuw i8, ptr %73, i64 27
  %3329 = load i8, ptr %3328, align 1, !tbaa !18
  %3330 = zext i8 %3329 to i64
  %3331 = shl nuw nsw i64 %3330, 24
  %3332 = or disjoint i64 %3331, %3327
  %3333 = getelementptr inbounds nuw i8, ptr %73, i64 28
  %3334 = load i8, ptr %3333, align 4, !tbaa !18
  %3335 = zext i8 %3334 to i64
  %3336 = shl nuw nsw i64 %3335, 32
  %3337 = or disjoint i64 %3336, %3332
  %3338 = getelementptr inbounds nuw i8, ptr %73, i64 29
  %3339 = load i8, ptr %3338, align 1, !tbaa !18
  %3340 = zext i8 %3339 to i64
  %3341 = shl nuw nsw i64 %3340, 40
  %3342 = or i64 %3341, %3337
  %3343 = getelementptr inbounds nuw i8, ptr %73, i64 30
  %3344 = load i8, ptr %3343, align 2, !tbaa !18
  %3345 = zext i8 %3344 to i64
  %3346 = shl nuw nsw i64 %3345, 48
  %3347 = or i64 %3346, %3342
  %3348 = getelementptr inbounds nuw i8, ptr %73, i64 31
  %3349 = load i8, ptr %3348, align 1, !tbaa !18
  %3350 = zext i8 %3349 to i64
  %3351 = shl nuw i64 %3350, 56
  %3352 = or i64 %3351, %3347
  %3353 = icmp sgt i64 %3352, -1
  br i1 %3353, label %2533, label %2643

3354:                                             ; preds = %2978
  %3355 = getelementptr inbounds [8 x i8], ptr %81, i64 %2979
  store i64 %2963, ptr %3355, align 8, !tbaa !17
  %3356 = load i64, ptr %81, align 16, !tbaa !17
  %3357 = icmp eq i64 %3356, 0
  br i1 %3357, label %3366, label %3358

3358:                                             ; preds = %3354, %3358
  %3359 = phi i64 [ %3364, %3358 ], [ %3356, %3354 ]
  %3360 = phi ptr [ %3363, %3358 ], [ %81, %3354 ]
  %3361 = getelementptr inbounds [8 x i8], ptr %81, i64 %3359
  %3362 = load i64, ptr %3361, align 8, !tbaa !17
  store i64 %3362, ptr %3360, align 8, !tbaa !17
  %3363 = getelementptr inbounds [8 x i8], ptr %81, i64 %3362
  %3364 = load i64, ptr %3363, align 8, !tbaa !17
  %3365 = icmp eq i64 %3364, %3362
  br i1 %3365, label %3366, label %3358, !llvm.loop !30

3366:                                             ; preds = %3358, %3354
  %3367 = phi i64 [ 0, %3354 ], [ %3362, %3358 ]
  %3368 = load i64, ptr %2958, align 8, !tbaa !17
  %3369 = icmp eq i64 %3368, 3
  br i1 %3369, label %3378, label %3370

3370:                                             ; preds = %3366, %3370
  %3371 = phi i64 [ %3376, %3370 ], [ %3368, %3366 ]
  %3372 = phi ptr [ %3375, %3370 ], [ %2958, %3366 ]
  %3373 = getelementptr inbounds [8 x i8], ptr %81, i64 %3371
  %3374 = load i64, ptr %3373, align 8, !tbaa !17
  store i64 %3374, ptr %3372, align 8, !tbaa !17
  %3375 = getelementptr inbounds [8 x i8], ptr %81, i64 %3374
  %3376 = load i64, ptr %3375, align 8, !tbaa !17
  %3377 = icmp eq i64 %3376, %3374
  br i1 %3377, label %3378, label %3370, !llvm.loop !30

3378:                                             ; preds = %3370, %3366
  %3379 = phi i64 [ 3, %3366 ], [ %3374, %3370 ]
  %3380 = icmp eq i64 %3367, %3379
  %3381 = select i1 %3380, ptr @.str.1, ptr @.str.2
  br label %3382

3382:                                             ; preds = %3378, %2978
  %3383 = phi ptr [ @.str.2, %2978 ], [ %3381, %3378 ]
  %3384 = call i32 (ptr, ...) @printf(ptr noundef nonnull dereferenceable(1) @.str.16, ptr noundef nonnull %3383)
  %3385 = call i32 (ptr, ...) @printf(ptr noundef nonnull dereferenceable(1) @.str.17, ptr noundef nonnull @.str.1)
  call void @llvm.lifetime.start.p0(ptr nonnull %82) #9
  store i64 3, ptr %82, align 16
  %3386 = getelementptr inbounds nuw i8, ptr %82, i64 8
  store i64 7, ptr %3386, align 8
  %3387 = getelementptr inbounds nuw i8, ptr %82, i64 16
  store i64 3, ptr %3387, align 16
  %3388 = getelementptr inbounds nuw i8, ptr %82, i64 24
  store i64 9, ptr %3388, align 8
  %3389 = getelementptr inbounds nuw i8, ptr %82, i64 32
  store i64 -1, ptr %3389, align 16
  call void @llvm.lifetime.start.p0(ptr nonnull %83) #9
  call void @llvm.lifetime.start.p0(ptr nonnull %84) #9
  call void @llvm.lifetime.start.p0(ptr nonnull %85) #9
  store ptr %82, ptr %85, align 8, !tbaa !9
  %3390 = getelementptr inbounds nuw i8, ptr %85, i64 8
  store i64 5, ptr %3390, align 8, !tbaa !14
  %3391 = getelementptr inbounds nuw i8, ptr %85, i64 16
  store i64 8, ptr %3391, align 8, !tbaa !15
  %3392 = getelementptr inbounds nuw i8, ptr %85, i64 24
  store i64 8, ptr %3392, align 8, !tbaa !16
  call void @llvm.lifetime.start.p0(ptr nonnull %86) #9
  store ptr %83, ptr %86, align 8, !tbaa !9
  %3393 = getelementptr inbounds nuw i8, ptr %86, i64 8
  store i64 8, ptr %3393, align 8, !tbaa !14
  %3394 = getelementptr inbounds nuw i8, ptr %86, i64 16
  store i64 8, ptr %3394, align 8, !tbaa !15
  %3395 = getelementptr inbounds nuw i8, ptr %86, i64 24
  store i64 8, ptr %3395, align 8, !tbaa !16
  call void @llvm.lifetime.start.p0(ptr nonnull %87) #9
  store ptr %84, ptr %87, align 8, !tbaa !9
  %3396 = getelementptr inbounds nuw i8, ptr %87, i64 8
  store i64 5, ptr %3396, align 8, !tbaa !14
  %3397 = getelementptr inbounds nuw i8, ptr %87, i64 16
  store i64 8, ptr %3397, align 8, !tbaa !15
  %3398 = getelementptr inbounds nuw i8, ptr %87, i64 24
  store i64 8, ptr %3398, align 8, !tbaa !16
  call fastcc void @build_index(ptr noundef %85, ptr noundef %86, ptr noundef %87)
  store i8 3, ptr %3389, align 16, !tbaa !18
  %3399 = getelementptr inbounds nuw i8, ptr %82, i64 33
  %3400 = getelementptr inbounds nuw i8, ptr %83, i64 24
  call void @llvm.memset.p0.i64(ptr noundef nonnull align 1 dereferenceable(7) %3399, i8 0, i64 7, i1 false)
  %3401 = load i8, ptr %3400, align 8, !tbaa !18
  %3402 = zext i8 %3401 to i64
  %3403 = getelementptr inbounds nuw i8, ptr %83, i64 25
  %3404 = load i8, ptr %3403, align 1, !tbaa !18
  %3405 = zext i8 %3404 to i64
  %3406 = shl nuw nsw i64 %3405, 8
  %3407 = or disjoint i64 %3406, %3402
  %3408 = getelementptr inbounds nuw i8, ptr %83, i64 26
  %3409 = load i8, ptr %3408, align 2, !tbaa !18
  %3410 = zext i8 %3409 to i64
  %3411 = shl nuw nsw i64 %3410, 16
  %3412 = getelementptr inbounds nuw i8, ptr %83, i64 27
  %3413 = load i8, ptr %3412, align 1, !tbaa !18
  %3414 = zext i8 %3413 to i64
  %3415 = shl nuw nsw i64 %3414, 24
  %3416 = or disjoint i64 %3415, %3407
  %3417 = or disjoint i64 %3416, %3411
  %3418 = getelementptr inbounds nuw i8, ptr %83, i64 28
  %3419 = load i8, ptr %3418, align 4, !tbaa !18
  %3420 = zext i8 %3419 to i64
  %3421 = shl nuw nsw i64 %3420, 32
  %3422 = getelementptr inbounds nuw i8, ptr %83, i64 29
  %3423 = load i8, ptr %3422, align 1, !tbaa !18
  %3424 = zext i8 %3423 to i64
  %3425 = shl nuw nsw i64 %3424, 40
  %3426 = or disjoint i64 %3421, %3425
  %3427 = or disjoint i64 %3426, %3417
  %3428 = getelementptr inbounds nuw i8, ptr %83, i64 30
  %3429 = load i8, ptr %3428, align 2, !tbaa !18
  %3430 = zext i8 %3429 to i64
  %3431 = shl nuw nsw i64 %3430, 48
  %3432 = getelementptr inbounds nuw i8, ptr %83, i64 31
  %3433 = load i8, ptr %3432, align 1, !tbaa !18
  %3434 = zext i8 %3433 to i64
  %3435 = shl nuw i64 %3434, 56
  %3436 = or disjoint i64 %3431, %3435
  %3437 = or disjoint i64 %3436, %3427
  %3438 = getelementptr inbounds nuw i8, ptr %84, i64 32
  store i8 %3401, ptr %3438, align 16, !tbaa !18
  %3439 = getelementptr inbounds nuw i8, ptr %84, i64 33
  store i8 %3404, ptr %3439, align 1, !tbaa !18
  %3440 = getelementptr inbounds nuw i8, ptr %84, i64 34
  store i8 %3409, ptr %3440, align 2, !tbaa !18
  %3441 = getelementptr inbounds nuw i8, ptr %84, i64 35
  store i8 %3413, ptr %3441, align 1, !tbaa !18
  %3442 = lshr i64 %3427, 32
  %3443 = trunc i64 %3442 to i8
  %3444 = getelementptr inbounds nuw i8, ptr %84, i64 36
  store i8 %3443, ptr %3444, align 4, !tbaa !18
  %3445 = lshr i64 %3427, 40
  %3446 = trunc nuw i64 %3445 to i8
  %3447 = getelementptr inbounds nuw i8, ptr %84, i64 37
  store i8 %3446, ptr %3447, align 1, !tbaa !18
  %3448 = lshr i64 %3437, 48
  %3449 = trunc i64 %3448 to i8
  %3450 = getelementptr inbounds nuw i8, ptr %84, i64 38
  store i8 %3449, ptr %3450, align 2, !tbaa !18
  %3451 = lshr i64 %3437, 56
  %3452 = trunc nuw i64 %3451 to i8
  %3453 = getelementptr inbounds nuw i8, ptr %84, i64 39
  store i8 %3452, ptr %3453, align 1, !tbaa !18
  store i8 4, ptr %3400, align 8, !tbaa !18
  call void @llvm.memset.p0.i64(ptr noundef nonnull align 1 dereferenceable(7) %3403, i8 0, i64 7, i1 false)
  br label %3454

3454:                                             ; preds = %3382, %3454
  %3455 = phi i64 [ %3536, %3454 ], [ 4, %3382 ]
  %3456 = phi i64 [ %3498, %3454 ], [ 0, %3382 ]
  %3457 = shl nsw i64 %3455, 3
  %3458 = getelementptr inbounds nuw i8, ptr %82, i64 %3457
  %3459 = load i8, ptr %3458, align 8, !tbaa !18
  %3460 = zext i8 %3459 to i64
  %3461 = getelementptr inbounds nuw i8, ptr %3458, i64 1
  %3462 = load i8, ptr %3461, align 1, !tbaa !18
  %3463 = zext i8 %3462 to i64
  %3464 = shl nuw nsw i64 %3463, 8
  %3465 = or disjoint i64 %3464, %3460
  %3466 = getelementptr inbounds nuw i8, ptr %3458, i64 2
  %3467 = load i8, ptr %3466, align 2, !tbaa !18
  %3468 = zext i8 %3467 to i64
  %3469 = shl nuw nsw i64 %3468, 16
  %3470 = or disjoint i64 %3469, %3465
  %3471 = getelementptr inbounds nuw i8, ptr %3458, i64 3
  %3472 = load i8, ptr %3471, align 1, !tbaa !18
  %3473 = zext i8 %3472 to i64
  %3474 = shl nuw nsw i64 %3473, 24
  %3475 = or disjoint i64 %3474, %3470
  %3476 = getelementptr inbounds nuw i8, ptr %3458, i64 4
  %3477 = load i8, ptr %3476, align 4, !tbaa !18
  %3478 = zext i8 %3477 to i64
  %3479 = shl nuw nsw i64 %3478, 32
  %3480 = or disjoint i64 %3479, %3475
  %3481 = getelementptr inbounds nuw i8, ptr %3458, i64 5
  %3482 = load i8, ptr %3481, align 1, !tbaa !18
  %3483 = zext i8 %3482 to i64
  %3484 = shl nuw nsw i64 %3483, 40
  %3485 = or i64 %3484, %3480
  %3486 = getelementptr inbounds nuw i8, ptr %3458, i64 6
  %3487 = load i8, ptr %3486, align 2, !tbaa !18
  %3488 = zext i8 %3487 to i64
  %3489 = shl nuw nsw i64 %3488, 48
  %3490 = or i64 %3489, %3485
  %3491 = getelementptr inbounds nuw i8, ptr %3458, i64 7
  %3492 = load i8, ptr %3491, align 1, !tbaa !18
  %3493 = zext i8 %3492 to i64
  %3494 = shl nuw i64 %3493, 56
  %3495 = or i64 %3494, %3490
  %3496 = icmp eq i64 %3495, 3
  %3497 = zext i1 %3496 to i64
  %3498 = add nuw nsw i64 %3456, %3497
  %3499 = getelementptr inbounds nuw i8, ptr %84, i64 %3457
  %3500 = load i8, ptr %3499, align 8, !tbaa !18
  %3501 = zext i8 %3500 to i64
  %3502 = getelementptr inbounds nuw i8, ptr %3499, i64 1
  %3503 = load i8, ptr %3502, align 1, !tbaa !18
  %3504 = zext i8 %3503 to i64
  %3505 = shl nuw nsw i64 %3504, 8
  %3506 = or disjoint i64 %3505, %3501
  %3507 = getelementptr inbounds nuw i8, ptr %3499, i64 2
  %3508 = load i8, ptr %3507, align 2, !tbaa !18
  %3509 = zext i8 %3508 to i64
  %3510 = shl nuw nsw i64 %3509, 16
  %3511 = or disjoint i64 %3510, %3506
  %3512 = getelementptr inbounds nuw i8, ptr %3499, i64 3
  %3513 = load i8, ptr %3512, align 1, !tbaa !18
  %3514 = zext i8 %3513 to i64
  %3515 = shl nuw nsw i64 %3514, 24
  %3516 = or disjoint i64 %3515, %3511
  %3517 = getelementptr inbounds nuw i8, ptr %3499, i64 4
  %3518 = load i8, ptr %3517, align 4, !tbaa !18
  %3519 = zext i8 %3518 to i64
  %3520 = shl nuw nsw i64 %3519, 32
  %3521 = or disjoint i64 %3520, %3516
  %3522 = getelementptr inbounds nuw i8, ptr %3499, i64 5
  %3523 = load i8, ptr %3522, align 1, !tbaa !18
  %3524 = zext i8 %3523 to i64
  %3525 = shl nuw nsw i64 %3524, 40
  %3526 = or i64 %3525, %3521
  %3527 = getelementptr inbounds nuw i8, ptr %3499, i64 6
  %3528 = load i8, ptr %3527, align 2, !tbaa !18
  %3529 = zext i8 %3528 to i64
  %3530 = shl nuw nsw i64 %3529, 48
  %3531 = or i64 %3530, %3526
  %3532 = getelementptr inbounds nuw i8, ptr %3499, i64 7
  %3533 = load i8, ptr %3532, align 1, !tbaa !18
  %3534 = zext i8 %3533 to i64
  %3535 = shl nuw i64 %3534, 56
  %3536 = or i64 %3535, %3531
  %3537 = icmp sgt i64 %3536, -1
  br i1 %3537, label %3454, label %3538, !llvm.loop !26

3538:                                             ; preds = %3454
  %3539 = load i8, ptr %82, align 16, !tbaa !18
  %3540 = getelementptr inbounds nuw i8, ptr %82, i64 1
  %3541 = load i8, ptr %3540, align 1, !tbaa !18
  %3542 = getelementptr inbounds nuw i8, ptr %82, i64 2
  %3543 = load i8, ptr %3542, align 2, !tbaa !18
  %3544 = getelementptr inbounds nuw i8, ptr %82, i64 3
  %3545 = load i8, ptr %3544, align 1, !tbaa !18
  %3546 = getelementptr inbounds nuw i8, ptr %82, i64 4
  %3547 = load i8, ptr %3546, align 4, !tbaa !18
  %3548 = getelementptr inbounds nuw i8, ptr %82, i64 5
  %3549 = load i8, ptr %3548, align 1, !tbaa !18
  %3550 = getelementptr inbounds nuw i8, ptr %82, i64 6
  %3551 = load i8, ptr %3550, align 2, !tbaa !18
  %3552 = getelementptr inbounds nuw i8, ptr %82, i64 7
  %3553 = load i8, ptr %3552, align 1, !tbaa !18
  store i64 -1, ptr %82, align 16
  %3554 = zext i8 %3539 to i64
  %3555 = zext i8 %3541 to i64
  %3556 = shl nuw nsw i64 %3555, 8
  %3557 = or disjoint i64 %3556, %3554
  %3558 = zext i8 %3543 to i64
  %3559 = shl nuw nsw i64 %3558, 16
  %3560 = or disjoint i64 %3559, %3557
  %3561 = zext i8 %3545 to i64
  %3562 = shl nuw nsw i64 %3561, 24
  %3563 = or disjoint i64 %3562, %3560
  %3564 = zext i8 %3547 to i64
  %3565 = shl nuw nsw i64 %3564, 32
  %3566 = or disjoint i64 %3565, %3563
  %3567 = zext i8 %3549 to i64
  %3568 = shl nuw nsw i64 %3567, 40
  %3569 = or i64 %3568, %3566
  %3570 = zext i8 %3551 to i64
  %3571 = shl nuw nsw i64 %3570, 48
  %3572 = or i64 %3571, %3569
  %3573 = zext i8 %3553 to i64
  %3574 = shl nuw i64 %3573, 56
  %3575 = or i64 %3574, %3572
  br label %3576

3576:                                             ; preds = %3538, %3576
  %3577 = phi i64 [ %3658, %3576 ], [ 4, %3538 ]
  %3578 = phi i64 [ %3620, %3576 ], [ 0, %3538 ]
  %3579 = shl nsw i64 %3577, 3
  %3580 = getelementptr inbounds nuw i8, ptr %82, i64 %3579
  %3581 = load i8, ptr %3580, align 8, !tbaa !18
  %3582 = zext i8 %3581 to i64
  %3583 = getelementptr inbounds nuw i8, ptr %3580, i64 1
  %3584 = load i8, ptr %3583, align 1, !tbaa !18
  %3585 = zext i8 %3584 to i64
  %3586 = shl nuw nsw i64 %3585, 8
  %3587 = or disjoint i64 %3586, %3582
  %3588 = getelementptr inbounds nuw i8, ptr %3580, i64 2
  %3589 = load i8, ptr %3588, align 2, !tbaa !18
  %3590 = zext i8 %3589 to i64
  %3591 = shl nuw nsw i64 %3590, 16
  %3592 = or disjoint i64 %3591, %3587
  %3593 = getelementptr inbounds nuw i8, ptr %3580, i64 3
  %3594 = load i8, ptr %3593, align 1, !tbaa !18
  %3595 = zext i8 %3594 to i64
  %3596 = shl nuw nsw i64 %3595, 24
  %3597 = or disjoint i64 %3596, %3592
  %3598 = getelementptr inbounds nuw i8, ptr %3580, i64 4
  %3599 = load i8, ptr %3598, align 4, !tbaa !18
  %3600 = zext i8 %3599 to i64
  %3601 = shl nuw nsw i64 %3600, 32
  %3602 = or disjoint i64 %3601, %3597
  %3603 = getelementptr inbounds nuw i8, ptr %3580, i64 5
  %3604 = load i8, ptr %3603, align 1, !tbaa !18
  %3605 = zext i8 %3604 to i64
  %3606 = shl nuw nsw i64 %3605, 40
  %3607 = or i64 %3606, %3602
  %3608 = getelementptr inbounds nuw i8, ptr %3580, i64 6
  %3609 = load i8, ptr %3608, align 2, !tbaa !18
  %3610 = zext i8 %3609 to i64
  %3611 = shl nuw nsw i64 %3610, 48
  %3612 = or i64 %3611, %3607
  %3613 = getelementptr inbounds nuw i8, ptr %3580, i64 7
  %3614 = load i8, ptr %3613, align 1, !tbaa !18
  %3615 = zext i8 %3614 to i64
  %3616 = shl nuw i64 %3615, 56
  %3617 = or i64 %3616, %3612
  %3618 = icmp eq i64 %3617, 3
  %3619 = zext i1 %3618 to i64
  %3620 = add nuw nsw i64 %3578, %3619
  %3621 = getelementptr inbounds nuw i8, ptr %84, i64 %3579
  %3622 = load i8, ptr %3621, align 8, !tbaa !18
  %3623 = zext i8 %3622 to i64
  %3624 = getelementptr inbounds nuw i8, ptr %3621, i64 1
  %3625 = load i8, ptr %3624, align 1, !tbaa !18
  %3626 = zext i8 %3625 to i64
  %3627 = shl nuw nsw i64 %3626, 8
  %3628 = or disjoint i64 %3627, %3623
  %3629 = getelementptr inbounds nuw i8, ptr %3621, i64 2
  %3630 = load i8, ptr %3629, align 2, !tbaa !18
  %3631 = zext i8 %3630 to i64
  %3632 = shl nuw nsw i64 %3631, 16
  %3633 = or disjoint i64 %3632, %3628
  %3634 = getelementptr inbounds nuw i8, ptr %3621, i64 3
  %3635 = load i8, ptr %3634, align 1, !tbaa !18
  %3636 = zext i8 %3635 to i64
  %3637 = shl nuw nsw i64 %3636, 24
  %3638 = or disjoint i64 %3637, %3633
  %3639 = getelementptr inbounds nuw i8, ptr %3621, i64 4
  %3640 = load i8, ptr %3639, align 4, !tbaa !18
  %3641 = zext i8 %3640 to i64
  %3642 = shl nuw nsw i64 %3641, 32
  %3643 = or disjoint i64 %3642, %3638
  %3644 = getelementptr inbounds nuw i8, ptr %3621, i64 5
  %3645 = load i8, ptr %3644, align 1, !tbaa !18
  %3646 = zext i8 %3645 to i64
  %3647 = shl nuw nsw i64 %3646, 40
  %3648 = or i64 %3647, %3643
  %3649 = getelementptr inbounds nuw i8, ptr %3621, i64 6
  %3650 = load i8, ptr %3649, align 2, !tbaa !18
  %3651 = zext i8 %3650 to i64
  %3652 = shl nuw nsw i64 %3651, 48
  %3653 = or i64 %3652, %3648
  %3654 = getelementptr inbounds nuw i8, ptr %3621, i64 7
  %3655 = load i8, ptr %3654, align 1, !tbaa !18
  %3656 = zext i8 %3655 to i64
  %3657 = shl nuw i64 %3656, 56
  %3658 = or i64 %3657, %3653
  %3659 = icmp sgt i64 %3658, -1
  br i1 %3659, label %3576, label %3660, !llvm.loop !26

3660:                                             ; preds = %3576
  %3661 = icmp eq i64 %3498, 3
  %3662 = icmp eq i64 %3575, 3
  %3663 = select i1 %3661, i1 %3662, i1 false
  %3664 = icmp eq i64 %3620, 2
  %3665 = select i1 %3663, i1 %3664, i1 false
  %3666 = select i1 %3665, ptr @.str.1, ptr @.str.2
  %3667 = call i32 (ptr, ...) @printf(ptr noundef nonnull dereferenceable(1) @.str.18, ptr noundef nonnull %3666, i64 noundef %3498, i64 noundef %3575, i64 noundef %3620)
  %3668 = call i32 (ptr, ...) @printf(ptr noundef nonnull dereferenceable(1) @.str.19, ptr noundef nonnull @.str.1, i64 noundef 45426, i64 noundef 45426)
  %3669 = call i32 (ptr, ...) @printf(ptr noundef nonnull dereferenceable(1) @.str.20, ptr noundef nonnull @.str.1)
  %3670 = call i32 (ptr, ...) @printf(ptr noundef nonnull dereferenceable(1) @.str.21, ptr noundef nonnull @.str.1, i64 noundef 6543778)
  %3671 = call i32 (ptr, ...) @printf(ptr noundef nonnull dereferenceable(1) @.str.22, ptr noundef nonnull @.str.1, i64 noundef 65536, i64 noundef 0)
  call void @llvm.lifetime.start.p0(ptr nonnull %88) #9
  call void @llvm.memcpy.p0.p0.i64(ptr noundef nonnull align 16 dereferenceable(24) %88, ptr noundef nonnull align 16 dereferenceable(24) @__const.main.lg3, i64 24, i1 false)
  call void @llvm.lifetime.start.p0(ptr nonnull %89) #9
  call void @llvm.memset.p0.i64(ptr noundef nonnull align 16 dereferenceable(24) %89, i8 0, i64 24, i1 false)
  call void @llvm.lifetime.start.p0(ptr nonnull %90) #9
  call void @llvm.lifetime.start.p0(ptr nonnull %91) #9
  store ptr %88, ptr %91, align 8, !tbaa !9
  %3672 = getelementptr inbounds nuw i8, ptr %91, i64 8
  store i64 3, ptr %3672, align 8, !tbaa !14
  %3673 = getelementptr inbounds nuw i8, ptr %91, i64 16
  store i64 8, ptr %3673, align 8, !tbaa !15
  %3674 = getelementptr inbounds nuw i8, ptr %91, i64 24
  store i64 8, ptr %3674, align 8, !tbaa !16
  call void @llvm.lifetime.start.p0(ptr nonnull %92) #9
  store ptr %89, ptr %92, align 8, !tbaa !9
  %3675 = getelementptr inbounds nuw i8, ptr %92, i64 8
  store i64 3, ptr %3675, align 8, !tbaa !14
  %3676 = getelementptr inbounds nuw i8, ptr %92, i64 16
  store i64 8, ptr %3676, align 8, !tbaa !15
  %3677 = getelementptr inbounds nuw i8, ptr %92, i64 24
  store i64 8, ptr %3677, align 8, !tbaa !16
  call void @llvm.lifetime.start.p0(ptr nonnull %93) #9
  store ptr %90, ptr %93, align 8, !tbaa !9
  %3678 = getelementptr inbounds nuw i8, ptr %93, i64 8
  store i64 3, ptr %3678, align 8, !tbaa !14
  %3679 = getelementptr inbounds nuw i8, ptr %93, i64 16
  store i64 8, ptr %3679, align 8, !tbaa !15
  %3680 = getelementptr inbounds nuw i8, ptr %93, i64 24
  store i64 8, ptr %3680, align 8, !tbaa !16
  call void @llvm.lifetime.start.p0(ptr nonnull %10) #9
  store i64 65536, ptr %10, align 16, !tbaa !17
  %3681 = getelementptr inbounds nuw i8, ptr %10, i64 8
  store i64 131072, ptr %3681, align 8, !tbaa !17
  %3682 = getelementptr inbounds nuw i8, ptr %10, i64 16
  store i64 196608, ptr %3682, align 16, !tbaa !17
  call void @llvm.lifetime.start.p0(ptr nonnull %11) #9
  store ptr %10, ptr %11, align 8, !tbaa !9
  %3683 = getelementptr inbounds nuw i8, ptr %11, i64 8
  store i64 3, ptr %3683, align 8, !tbaa !14
  %3684 = getelementptr inbounds nuw i8, ptr %11, i64 16
  store i64 8, ptr %3684, align 8, !tbaa !15
  %3685 = getelementptr inbounds nuw i8, ptr %11, i64 24
  store i64 8, ptr %3685, align 8, !tbaa !16
  call fastcc void @layernorm(ptr noundef %11, i64 noundef 3, ptr noundef nonnull readonly %91, ptr noundef nonnull readonly %92, ptr noundef nonnull readonly %93)
  call void @llvm.lifetime.end.p0(ptr nonnull %11) #9
  call void @llvm.lifetime.end.p0(ptr nonnull %10) #9
  %3686 = load i64, ptr %90, align 16, !tbaa !17
  %3687 = getelementptr inbounds nuw i8, ptr %90, i64 8
  %3688 = load i64, ptr %3687, align 8, !tbaa !17
  %3689 = add nsw i64 %3688, %3686
  %3690 = getelementptr inbounds nuw i8, ptr %90, i64 16
  %3691 = load i64, ptr %3690, align 16, !tbaa !17
  %3692 = add nsw i64 %3691, %3689
  %3693 = add i64 %3692, 9
  %3694 = icmp ult i64 %3693, 19
  %3695 = select i1 %3694, ptr @.str.1, ptr @.str.2
  %3696 = call i32 (ptr, ...) @printf(ptr noundef nonnull dereferenceable(1) @.str.23, ptr noundef nonnull %3695, i64 noundef %3692)
  call void @llvm.lifetime.start.p0(ptr nonnull %94) #9
  call void @llvm.lifetime.start.p0(ptr nonnull %1) #9
  call void @llvm.memset.p0.i64(ptr noundef nonnull align 16 dereferenceable(64) %1, i8 0, i64 64, i1 false)
  store i8 1, ptr %1, align 16, !tbaa !18
  %3697 = getelementptr inbounds nuw i8, ptr %1, i64 1
  store i8 1, ptr %3697, align 1, !tbaa !18
  %3698 = getelementptr inbounds nuw i8, ptr %1, i64 2
  %3699 = getelementptr inbounds nuw i8, ptr %1, i64 3
  %3700 = getelementptr inbounds nuw i8, ptr %1, i64 4
  %3701 = getelementptr inbounds nuw i8, ptr %1, i64 5
  store i32 0, ptr %3698, align 2
  call void @llvm.lifetime.start.p0(ptr nonnull %2) #9
  call void @llvm.lifetime.start.p0(ptr nonnull %3) #9
  call void @llvm.lifetime.start.p0(ptr nonnull %4) #9
  call void @llvm.lifetime.start.p0(ptr nonnull %5) #9
  store i64 0, ptr %2, align 16, !tbaa !17
  %3702 = getelementptr inbounds nuw i8, ptr %2, i64 8
  store i64 1, ptr %3702, align 8, !tbaa !17
  %3703 = getelementptr inbounds nuw i8, ptr %2, i64 16
  store i64 2, ptr %3703, align 16, !tbaa !17
  %3704 = getelementptr inbounds nuw i8, ptr %6, i64 8
  %3705 = getelementptr inbounds nuw i8, ptr %6, i64 16
  %3706 = getelementptr inbounds nuw i8, ptr %6, i64 24
  %3707 = getelementptr inbounds nuw i8, ptr %7, i64 8
  %3708 = getelementptr inbounds nuw i8, ptr %7, i64 16
  %3709 = getelementptr inbounds nuw i8, ptr %7, i64 24
  %3710 = getelementptr inbounds nuw i8, ptr %8, i64 8
  %3711 = getelementptr inbounds nuw i8, ptr %8, i64 16
  %3712 = getelementptr inbounds nuw i8, ptr %8, i64 24
  %3713 = getelementptr inbounds nuw i8, ptr %9, i64 8
  %3714 = getelementptr inbounds nuw i8, ptr %9, i64 16
  %3715 = getelementptr inbounds nuw i8, ptr %9, i64 24
  %3716 = getelementptr inbounds nuw i8, ptr %3, i64 8
  %3717 = getelementptr inbounds nuw i8, ptr %3, i64 16
  %3718 = getelementptr inbounds nuw i8, ptr %5, i64 8
  %3719 = getelementptr inbounds nuw i8, ptr %4, i64 8
  %3720 = getelementptr inbounds nuw i8, ptr %5, i64 16
  %3721 = getelementptr inbounds nuw i8, ptr %4, i64 16
  br label %3722

3722:                                             ; preds = %3947, %3660
  %3723 = phi i64 [ 0, %3660 ], [ %3949, %3947 ]
  %3724 = load i8, ptr %3698, align 2, !tbaa !18
  %3725 = icmp ne i8 %3724, 0
  %3726 = load i8, ptr %1, align 16
  %3727 = icmp eq i8 %3726, 0
  %3728 = select i1 %3725, i1 true, i1 %3727
  %3729 = load i8, ptr %3697, align 1
  %3730 = icmp eq i8 %3729, 0
  %3731 = select i1 %3728, i1 true, i1 %3730
  %3732 = select i1 %3731, i64 -999999999, i64 100
  store i64 %3732, ptr %3, align 16, !tbaa !17
  %3733 = load i8, ptr %3699, align 1, !tbaa !18
  %3734 = icmp ne i8 %3733, 0
  %3735 = load i8, ptr %3700, align 4
  %3736 = icmp eq i8 %3735, 0
  %3737 = select i1 %3734, i1 true, i1 %3736
  %3738 = select i1 %3737, i64 -999999999, i64 300
  store i64 %3738, ptr %3716, align 8, !tbaa !17
  %3739 = load i8, ptr %3701, align 1, !tbaa !18
  %3740 = icmp ne i8 %3739, 0
  %3741 = load i8, ptr %1, align 16
  %3742 = icmp eq i8 %3741, 0
  %3743 = select i1 %3740, i1 true, i1 %3742
  %3744 = select i1 %3743, i64 -999999999, i64 200
  store i64 %3744, ptr %3717, align 16, !tbaa !17
  call void @llvm.lifetime.start.p0(ptr nonnull %6) #9
  store ptr %2, ptr %6, align 8, !tbaa !9
  store i64 3, ptr %3704, align 8, !tbaa !14
  store i64 8, ptr %3705, align 8, !tbaa !15
  store i64 8, ptr %3706, align 8, !tbaa !16
  call void @llvm.lifetime.start.p0(ptr nonnull %7) #9
  store ptr %3, ptr %7, align 8, !tbaa !9
  store i64 3, ptr %3707, align 8, !tbaa !14
  store i64 8, ptr %3708, align 8, !tbaa !15
  store i64 8, ptr %3709, align 8, !tbaa !16
  call void @llvm.lifetime.start.p0(ptr nonnull %8) #9
  store ptr %4, ptr %8, align 8, !tbaa !9
  store i64 3, ptr %3710, align 8, !tbaa !14
  store i64 8, ptr %3711, align 8, !tbaa !15
  store i64 8, ptr %3712, align 8, !tbaa !16
  call void @llvm.lifetime.start.p0(ptr nonnull %9) #9
  store ptr %5, ptr %9, align 8, !tbaa !9
  store i64 3, ptr %3713, align 8, !tbaa !14
  store i64 8, ptr %3714, align 8, !tbaa !15
  store i64 8, ptr %3715, align 8, !tbaa !16
  call fastcc void @topk(ptr noundef %7, i64 noundef 3, ptr noundef %6, ptr noundef %8, ptr noundef %9)
  %3745 = load i64, ptr %5, align 16, !tbaa !17
  %3746 = icmp slt i64 %3745, -999999998
  br i1 %3746, label %3747, label %3748

3747:                                             ; preds = %3722
  call void @llvm.lifetime.end.p0(ptr nonnull %9) #9
  call void @llvm.lifetime.end.p0(ptr nonnull %8) #9
  call void @llvm.lifetime.end.p0(ptr nonnull %7) #9
  call void @llvm.lifetime.end.p0(ptr nonnull %6) #9
  br label %3951

3748:                                             ; preds = %3722
  %3749 = load i64, ptr %4, align 16, !tbaa !17
  %3750 = shl nsw i64 %3749, 3
  %3751 = getelementptr inbounds i8, ptr @__const.main.pih, i64 %3750
  %3752 = load i8, ptr %3751, align 8, !tbaa !18
  %3753 = zext i8 %3752 to i64
  %3754 = getelementptr inbounds nuw i8, ptr %3751, i64 1
  %3755 = load i8, ptr %3754, align 1, !tbaa !18
  %3756 = zext i8 %3755 to i64
  %3757 = shl nuw nsw i64 %3756, 8
  %3758 = or disjoint i64 %3757, %3753
  %3759 = getelementptr inbounds nuw i8, ptr %3751, i64 2
  %3760 = load i8, ptr %3759, align 2, !tbaa !18
  %3761 = zext i8 %3760 to i64
  %3762 = shl nuw nsw i64 %3761, 16
  %3763 = getelementptr inbounds nuw i8, ptr %3751, i64 3
  %3764 = load i8, ptr %3763, align 1, !tbaa !18
  %3765 = zext i8 %3764 to i64
  %3766 = shl nuw nsw i64 %3765, 24
  %3767 = or disjoint i64 %3766, %3758
  %3768 = or disjoint i64 %3767, %3762
  %3769 = getelementptr inbounds nuw i8, ptr %3751, i64 4
  %3770 = load i8, ptr %3769, align 4, !tbaa !18
  %3771 = zext i8 %3770 to i64
  %3772 = shl nuw nsw i64 %3771, 32
  %3773 = getelementptr inbounds nuw i8, ptr %3751, i64 5
  %3774 = load i8, ptr %3773, align 1, !tbaa !18
  %3775 = zext i8 %3774 to i64
  %3776 = shl nuw nsw i64 %3775, 40
  %3777 = or disjoint i64 %3772, %3776
  %3778 = or disjoint i64 %3777, %3768
  %3779 = getelementptr inbounds nuw i8, ptr %3751, i64 6
  %3780 = load i8, ptr %3779, align 2, !tbaa !18
  %3781 = zext i8 %3780 to i64
  %3782 = shl nuw nsw i64 %3781, 48
  %3783 = getelementptr inbounds nuw i8, ptr %3751, i64 7
  %3784 = load i8, ptr %3783, align 1, !tbaa !18
  %3785 = zext i8 %3784 to i64
  %3786 = shl nuw i64 %3785, 56
  %3787 = or disjoint i64 %3782, %3786
  %3788 = or disjoint i64 %3787, %3778
  %3789 = getelementptr inbounds i8, ptr %1, i64 %3788
  %3790 = load i8, ptr %3789, align 1, !tbaa !18
  %3791 = icmp eq i8 %3790, 0
  br i1 %3791, label %3792, label %3811

3792:                                             ; preds = %3748
  store i8 1, ptr %3789, align 1, !tbaa !18
  %3793 = shl nsw i64 %3723, 3
  %3794 = getelementptr inbounds i8, ptr %94, i64 %3793
  store i8 %3752, ptr %3794, align 8, !tbaa !18
  %3795 = getelementptr inbounds nuw i8, ptr %3794, i64 1
  store i8 %3755, ptr %3795, align 1, !tbaa !18
  %3796 = getelementptr inbounds nuw i8, ptr %3794, i64 2
  store i8 %3760, ptr %3796, align 2, !tbaa !18
  %3797 = getelementptr inbounds nuw i8, ptr %3794, i64 3
  store i8 %3764, ptr %3797, align 1, !tbaa !18
  %3798 = lshr i64 %3778, 32
  %3799 = trunc i64 %3798 to i8
  %3800 = getelementptr inbounds nuw i8, ptr %3794, i64 4
  store i8 %3799, ptr %3800, align 4, !tbaa !18
  %3801 = lshr i64 %3778, 40
  %3802 = trunc nuw i64 %3801 to i8
  %3803 = getelementptr inbounds nuw i8, ptr %3794, i64 5
  store i8 %3802, ptr %3803, align 1, !tbaa !18
  %3804 = lshr i64 %3788, 48
  %3805 = trunc i64 %3804 to i8
  %3806 = getelementptr inbounds nuw i8, ptr %3794, i64 6
  store i8 %3805, ptr %3806, align 2, !tbaa !18
  %3807 = lshr i64 %3788, 56
  %3808 = trunc nuw i64 %3807 to i8
  %3809 = getelementptr inbounds nuw i8, ptr %3794, i64 7
  store i8 %3808, ptr %3809, align 1, !tbaa !18
  %3810 = add nsw i64 %3723, 1
  br label %3811

3811:                                             ; preds = %3792, %3748
  %3812 = phi i32 [ 0, %3748 ], [ 1, %3792 ]
  %3813 = phi i64 [ %3723, %3748 ], [ %3810, %3792 ]
  %3814 = load i64, ptr %3718, align 8, !tbaa !17
  %3815 = icmp slt i64 %3814, -999999998
  br i1 %3815, label %3947, label %3816

3816:                                             ; preds = %3811
  %3817 = load i64, ptr %3719, align 8, !tbaa !17
  %3818 = shl nsw i64 %3817, 3
  %3819 = getelementptr inbounds i8, ptr @__const.main.pih, i64 %3818
  %3820 = load i8, ptr %3819, align 8, !tbaa !18
  %3821 = zext i8 %3820 to i64
  %3822 = getelementptr inbounds nuw i8, ptr %3819, i64 1
  %3823 = load i8, ptr %3822, align 1, !tbaa !18
  %3824 = zext i8 %3823 to i64
  %3825 = shl nuw nsw i64 %3824, 8
  %3826 = or disjoint i64 %3825, %3821
  %3827 = getelementptr inbounds nuw i8, ptr %3819, i64 2
  %3828 = load i8, ptr %3827, align 2, !tbaa !18
  %3829 = zext i8 %3828 to i64
  %3830 = shl nuw nsw i64 %3829, 16
  %3831 = getelementptr inbounds nuw i8, ptr %3819, i64 3
  %3832 = load i8, ptr %3831, align 1, !tbaa !18
  %3833 = zext i8 %3832 to i64
  %3834 = shl nuw nsw i64 %3833, 24
  %3835 = or disjoint i64 %3834, %3826
  %3836 = or disjoint i64 %3835, %3830
  %3837 = getelementptr inbounds nuw i8, ptr %3819, i64 4
  %3838 = load i8, ptr %3837, align 4, !tbaa !18
  %3839 = zext i8 %3838 to i64
  %3840 = shl nuw nsw i64 %3839, 32
  %3841 = getelementptr inbounds nuw i8, ptr %3819, i64 5
  %3842 = load i8, ptr %3841, align 1, !tbaa !18
  %3843 = zext i8 %3842 to i64
  %3844 = shl nuw nsw i64 %3843, 40
  %3845 = or disjoint i64 %3840, %3844
  %3846 = or disjoint i64 %3845, %3836
  %3847 = getelementptr inbounds nuw i8, ptr %3819, i64 6
  %3848 = load i8, ptr %3847, align 2, !tbaa !18
  %3849 = zext i8 %3848 to i64
  %3850 = shl nuw nsw i64 %3849, 48
  %3851 = getelementptr inbounds nuw i8, ptr %3819, i64 7
  %3852 = load i8, ptr %3851, align 1, !tbaa !18
  %3853 = zext i8 %3852 to i64
  %3854 = shl nuw i64 %3853, 56
  %3855 = or disjoint i64 %3850, %3854
  %3856 = or disjoint i64 %3855, %3846
  %3857 = getelementptr inbounds i8, ptr %1, i64 %3856
  %3858 = load i8, ptr %3857, align 1, !tbaa !18
  %3859 = icmp eq i8 %3858, 0
  br i1 %3859, label %3860, label %3879

3860:                                             ; preds = %3816
  store i8 1, ptr %3857, align 1, !tbaa !18
  %3861 = shl nsw i64 %3813, 3
  %3862 = getelementptr inbounds i8, ptr %94, i64 %3861
  store i8 %3820, ptr %3862, align 8, !tbaa !18
  %3863 = getelementptr inbounds nuw i8, ptr %3862, i64 1
  store i8 %3823, ptr %3863, align 1, !tbaa !18
  %3864 = getelementptr inbounds nuw i8, ptr %3862, i64 2
  store i8 %3828, ptr %3864, align 2, !tbaa !18
  %3865 = getelementptr inbounds nuw i8, ptr %3862, i64 3
  store i8 %3832, ptr %3865, align 1, !tbaa !18
  %3866 = lshr i64 %3846, 32
  %3867 = trunc i64 %3866 to i8
  %3868 = getelementptr inbounds nuw i8, ptr %3862, i64 4
  store i8 %3867, ptr %3868, align 4, !tbaa !18
  %3869 = lshr i64 %3846, 40
  %3870 = trunc nuw i64 %3869 to i8
  %3871 = getelementptr inbounds nuw i8, ptr %3862, i64 5
  store i8 %3870, ptr %3871, align 1, !tbaa !18
  %3872 = lshr i64 %3856, 48
  %3873 = trunc i64 %3872 to i8
  %3874 = getelementptr inbounds nuw i8, ptr %3862, i64 6
  store i8 %3873, ptr %3874, align 2, !tbaa !18
  %3875 = lshr i64 %3856, 56
  %3876 = trunc nuw i64 %3875 to i8
  %3877 = getelementptr inbounds nuw i8, ptr %3862, i64 7
  store i8 %3876, ptr %3877, align 1, !tbaa !18
  %3878 = add nsw i64 %3813, 1
  br label %3879

3879:                                             ; preds = %3860, %3816
  %3880 = phi i32 [ %3812, %3816 ], [ 1, %3860 ]
  %3881 = phi i64 [ %3813, %3816 ], [ %3878, %3860 ]
  %3882 = load i64, ptr %3720, align 16, !tbaa !17
  %3883 = icmp slt i64 %3882, -999999998
  br i1 %3883, label %3947, label %3884

3884:                                             ; preds = %3879
  %3885 = load i64, ptr %3721, align 16, !tbaa !17
  %3886 = shl nsw i64 %3885, 3
  %3887 = getelementptr inbounds i8, ptr @__const.main.pih, i64 %3886
  %3888 = load i8, ptr %3887, align 8, !tbaa !18
  %3889 = zext i8 %3888 to i64
  %3890 = getelementptr inbounds nuw i8, ptr %3887, i64 1
  %3891 = load i8, ptr %3890, align 1, !tbaa !18
  %3892 = zext i8 %3891 to i64
  %3893 = shl nuw nsw i64 %3892, 8
  %3894 = or disjoint i64 %3893, %3889
  %3895 = getelementptr inbounds nuw i8, ptr %3887, i64 2
  %3896 = load i8, ptr %3895, align 2, !tbaa !18
  %3897 = zext i8 %3896 to i64
  %3898 = shl nuw nsw i64 %3897, 16
  %3899 = getelementptr inbounds nuw i8, ptr %3887, i64 3
  %3900 = load i8, ptr %3899, align 1, !tbaa !18
  %3901 = zext i8 %3900 to i64
  %3902 = shl nuw nsw i64 %3901, 24
  %3903 = or disjoint i64 %3902, %3894
  %3904 = or disjoint i64 %3903, %3898
  %3905 = getelementptr inbounds nuw i8, ptr %3887, i64 4
  %3906 = load i8, ptr %3905, align 4, !tbaa !18
  %3907 = zext i8 %3906 to i64
  %3908 = shl nuw nsw i64 %3907, 32
  %3909 = getelementptr inbounds nuw i8, ptr %3887, i64 5
  %3910 = load i8, ptr %3909, align 1, !tbaa !18
  %3911 = zext i8 %3910 to i64
  %3912 = shl nuw nsw i64 %3911, 40
  %3913 = or disjoint i64 %3908, %3912
  %3914 = or disjoint i64 %3913, %3904
  %3915 = getelementptr inbounds nuw i8, ptr %3887, i64 6
  %3916 = load i8, ptr %3915, align 2, !tbaa !18
  %3917 = zext i8 %3916 to i64
  %3918 = shl nuw nsw i64 %3917, 48
  %3919 = getelementptr inbounds nuw i8, ptr %3887, i64 7
  %3920 = load i8, ptr %3919, align 1, !tbaa !18
  %3921 = zext i8 %3920 to i64
  %3922 = shl nuw i64 %3921, 56
  %3923 = or disjoint i64 %3918, %3922
  %3924 = or disjoint i64 %3923, %3914
  %3925 = getelementptr inbounds i8, ptr %1, i64 %3924
  %3926 = load i8, ptr %3925, align 1, !tbaa !18
  %3927 = icmp eq i8 %3926, 0
  br i1 %3927, label %3928, label %3947

3928:                                             ; preds = %3884
  store i8 1, ptr %3925, align 1, !tbaa !18
  %3929 = shl nsw i64 %3881, 3
  %3930 = getelementptr inbounds i8, ptr %94, i64 %3929
  store i8 %3888, ptr %3930, align 8, !tbaa !18
  %3931 = getelementptr inbounds nuw i8, ptr %3930, i64 1
  store i8 %3891, ptr %3931, align 1, !tbaa !18
  %3932 = getelementptr inbounds nuw i8, ptr %3930, i64 2
  store i8 %3896, ptr %3932, align 2, !tbaa !18
  %3933 = getelementptr inbounds nuw i8, ptr %3930, i64 3
  store i8 %3900, ptr %3933, align 1, !tbaa !18
  %3934 = lshr i64 %3914, 32
  %3935 = trunc i64 %3934 to i8
  %3936 = getelementptr inbounds nuw i8, ptr %3930, i64 4
  store i8 %3935, ptr %3936, align 4, !tbaa !18
  %3937 = lshr i64 %3914, 40
  %3938 = trunc nuw i64 %3937 to i8
  %3939 = getelementptr inbounds nuw i8, ptr %3930, i64 5
  store i8 %3938, ptr %3939, align 1, !tbaa !18
  %3940 = lshr i64 %3924, 48
  %3941 = trunc i64 %3940 to i8
  %3942 = getelementptr inbounds nuw i8, ptr %3930, i64 6
  store i8 %3941, ptr %3942, align 2, !tbaa !18
  %3943 = lshr i64 %3924, 56
  %3944 = trunc nuw i64 %3943 to i8
  %3945 = getelementptr inbounds nuw i8, ptr %3930, i64 7
  store i8 %3944, ptr %3945, align 1, !tbaa !18
  %3946 = add nsw i64 %3881, 1
  br label %3947

3947:                                             ; preds = %3928, %3884, %3879, %3811
  %3948 = phi i32 [ %3880, %3884 ], [ %3880, %3879 ], [ %3812, %3811 ], [ 1, %3928 ]
  %3949 = phi i64 [ %3881, %3884 ], [ %3881, %3879 ], [ %3813, %3811 ], [ %3946, %3928 ]
  call void @llvm.lifetime.end.p0(ptr nonnull %9) #9
  call void @llvm.lifetime.end.p0(ptr nonnull %8) #9
  call void @llvm.lifetime.end.p0(ptr nonnull %7) #9
  call void @llvm.lifetime.end.p0(ptr nonnull %6) #9
  %3950 = icmp eq i32 %3948, 0
  br i1 %3950, label %3951, label %3722, !llvm.loop !31

3951:                                             ; preds = %3947, %3747
  %3952 = phi i64 [ %3723, %3747 ], [ %3949, %3947 ]
  call void @llvm.lifetime.end.p0(ptr nonnull %5) #9
  call void @llvm.lifetime.end.p0(ptr nonnull %4) #9
  call void @llvm.lifetime.end.p0(ptr nonnull %3) #9
  call void @llvm.lifetime.end.p0(ptr nonnull %2) #9
  call void @llvm.lifetime.end.p0(ptr nonnull %1) #9
  %3953 = icmp sgt i64 %3952, 0
  br i1 %3953, label %3954, label %3989

3954:                                             ; preds = %3951
  %3955 = and i64 %3952, 1
  %3956 = icmp eq i64 %3952, 1
  br i1 %3956, label %3961, label %3957

3957:                                             ; preds = %3954
  %3958 = and i64 %3952, 9223372036854775806
  br label %3996

3959:                                             ; preds = %3996
  %3960 = icmp eq i64 %3955, 0
  br i1 %3960, label %3976, label %3961

3961:                                             ; preds = %3959, %3954
  %3962 = phi i64 [ 0, %3954 ], [ %4021, %3959 ]
  %3963 = phi i32 [ 0, %3954 ], [ %4020, %3959 ]
  %3964 = phi i32 [ 0, %3954 ], [ %4017, %3959 ]
  %3965 = phi i32 [ 0, %3954 ], [ %4014, %3959 ]
  %3966 = trunc i64 %3952 to i1
  call void @llvm.assume(i1 %3966)
  %3967 = getelementptr inbounds nuw [8 x i8], ptr %94, i64 %3962
  %3968 = load i64, ptr %3967, align 8, !tbaa !17
  %3969 = freeze i64 %3968
  %3970 = icmp eq i64 %3969, 2
  %3971 = select i1 %3970, i32 1, i32 %3965
  %3972 = icmp eq i64 %3969, 5
  %3973 = select i1 %3972, i32 1, i32 %3964
  %3974 = icmp eq i64 %3969, 3
  %3975 = select i1 %3974, i32 1, i32 %3963
  br label %3976

3976:                                             ; preds = %3959, %3961
  %3977 = phi i32 [ %4014, %3959 ], [ %3971, %3961 ]
  %3978 = phi i32 [ %4017, %3959 ], [ %3973, %3961 ]
  %3979 = phi i32 [ %4020, %3959 ], [ %3975, %3961 ]
  %3980 = icmp ne i32 %3977, 0
  %3981 = icmp ne i32 %3978, 0
  %3982 = icmp eq i64 %3952, 2
  %3983 = select i1 %3982, i1 %3980, i1 false
  %3984 = select i1 %3983, i1 %3981, i1 false
  %3985 = icmp eq i32 %3979, 0
  %3986 = freeze i1 %3984
  %3987 = select i1 %3985, ptr @.str.1, ptr @.str.2
  %3988 = select i1 %3986, ptr %3987, ptr @.str.2
  br label %3989

3989:                                             ; preds = %3976, %3951
  %3990 = phi ptr [ %3987, %3976 ], [ @.str.1, %3951 ]
  %3991 = phi i32 [ %3979, %3976 ], [ 0, %3951 ]
  %3992 = phi ptr [ %3988, %3976 ], [ @.str.2, %3951 ]
  %3993 = call i32 (ptr, ...) @printf(ptr noundef nonnull dereferenceable(1) @.str.24, ptr noundef nonnull %3992, i64 noundef %3952)
  %3994 = call i32 (ptr, ...) @printf(ptr noundef nonnull dereferenceable(1) @.str.25, ptr noundef nonnull %3990, i32 noundef %3991)
  %3995 = call i32 @puts(ptr nonnull dereferenceable(1) @str)
  call void @llvm.lifetime.end.p0(ptr nonnull %94) #9
  call void @llvm.lifetime.end.p0(ptr nonnull %93) #9
  call void @llvm.lifetime.end.p0(ptr nonnull %92) #9
  call void @llvm.lifetime.end.p0(ptr nonnull %91) #9
  call void @llvm.lifetime.end.p0(ptr nonnull %90) #9
  call void @llvm.lifetime.end.p0(ptr nonnull %89) #9
  call void @llvm.lifetime.end.p0(ptr nonnull %88) #9
  call void @llvm.lifetime.end.p0(ptr nonnull %87) #9
  call void @llvm.lifetime.end.p0(ptr nonnull %86) #9
  call void @llvm.lifetime.end.p0(ptr nonnull %85) #9
  call void @llvm.lifetime.end.p0(ptr nonnull %84) #9
  call void @llvm.lifetime.end.p0(ptr nonnull %83) #9
  call void @llvm.lifetime.end.p0(ptr nonnull %82) #9
  call void @llvm.lifetime.end.p0(ptr nonnull %81) #9
  call void @llvm.lifetime.end.p0(ptr nonnull %80) #9
  call void @llvm.lifetime.end.p0(ptr nonnull %79) #9
  call void @llvm.lifetime.end.p0(ptr nonnull %78) #9
  call void @llvm.lifetime.end.p0(ptr nonnull %77) #9
  call void @llvm.lifetime.end.p0(ptr nonnull %76) #9
  call void @llvm.lifetime.end.p0(ptr nonnull %75) #9
  call void @llvm.lifetime.end.p0(ptr nonnull %74) #9
  call void @llvm.lifetime.end.p0(ptr nonnull %73) #9
  call void @llvm.lifetime.end.p0(ptr nonnull %72) #9
  call void @llvm.lifetime.end.p0(ptr nonnull %71) #9
  call void @llvm.lifetime.end.p0(ptr nonnull %70) #9
  call void @llvm.lifetime.end.p0(ptr nonnull %69) #9
  call void @llvm.lifetime.end.p0(ptr nonnull %68) #9
  call void @llvm.lifetime.end.p0(ptr nonnull %67) #9
  call void @llvm.lifetime.end.p0(ptr nonnull %66) #9
  call void @llvm.lifetime.end.p0(ptr nonnull %65) #9
  call void @llvm.lifetime.end.p0(ptr nonnull %64) #9
  call void @llvm.lifetime.end.p0(ptr nonnull %63) #9
  call void @llvm.lifetime.end.p0(ptr nonnull %62) #9
  call void @llvm.lifetime.end.p0(ptr nonnull %61) #9
  call void @llvm.lifetime.end.p0(ptr nonnull %60) #9
  call void @llvm.lifetime.end.p0(ptr nonnull %59) #9
  call void @llvm.lifetime.end.p0(ptr nonnull %58) #9
  call void @llvm.lifetime.end.p0(ptr nonnull %57) #9
  call void @llvm.lifetime.end.p0(ptr nonnull %56) #9
  call void @llvm.lifetime.end.p0(ptr nonnull %55) #9
  call void @llvm.lifetime.end.p0(ptr nonnull %54) #9
  call void @llvm.lifetime.end.p0(ptr nonnull %53) #9
  call void @llvm.lifetime.end.p0(ptr nonnull %52) #9
  call void @llvm.lifetime.end.p0(ptr nonnull %51) #9
  call void @llvm.lifetime.end.p0(ptr nonnull %50) #9
  call void @llvm.lifetime.end.p0(ptr nonnull %49) #9
  call void @llvm.lifetime.end.p0(ptr nonnull %48) #9
  call void @llvm.lifetime.end.p0(ptr nonnull %47) #9
  call void @llvm.lifetime.end.p0(ptr nonnull %46) #9
  call void @llvm.lifetime.end.p0(ptr nonnull %45) #9
  call void @llvm.lifetime.end.p0(ptr nonnull %44) #9
  call void @llvm.lifetime.end.p0(ptr nonnull %43) #9
  call void @llvm.lifetime.end.p0(ptr nonnull %42) #9
  ret i32 0

3996:                                             ; preds = %3996, %3957
  %3997 = phi i64 [ 0, %3957 ], [ %4021, %3996 ]
  %3998 = phi i32 [ 0, %3957 ], [ %4020, %3996 ]
  %3999 = phi i32 [ 0, %3957 ], [ %4017, %3996 ]
  %4000 = phi i32 [ 0, %3957 ], [ %4014, %3996 ]
  %4001 = phi i64 [ 0, %3957 ], [ %4022, %3996 ]
  %4002 = getelementptr inbounds nuw [8 x i8], ptr %94, i64 %3997
  %4003 = load i64, ptr %4002, align 16, !tbaa !17
  %4004 = freeze i64 %4003
  %4005 = icmp eq i64 %4004, 2
  %4006 = icmp eq i64 %4004, 5
  %4007 = icmp eq i64 %4004, 3
  %4008 = getelementptr inbounds nuw [8 x i8], ptr %94, i64 %3997
  %4009 = getelementptr inbounds nuw i8, ptr %4008, i64 8
  %4010 = load i64, ptr %4009, align 8, !tbaa !17
  %4011 = freeze i64 %4010
  %4012 = icmp eq i64 %4011, 2
  %4013 = or i1 %4012, %4005
  %4014 = select i1 %4013, i32 1, i32 %4000
  %4015 = icmp eq i64 %4011, 5
  %4016 = or i1 %4015, %4006
  %4017 = select i1 %4016, i32 1, i32 %3999
  %4018 = icmp eq i64 %4011, 3
  %4019 = or i1 %4018, %4007
  %4020 = select i1 %4019, i32 1, i32 %3998
  %4021 = add nuw nsw i64 %3997, 2
  %4022 = add i64 %4001, 2
  %4023 = icmp eq i64 %4022, %3958
  br i1 %4023, label %3959, label %3996, !llvm.loop !32
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind willreturn memory(argmem: readwrite)
declare void @llvm.lifetime.start.p0(ptr captures(none)) #1

; Function Attrs: mustprogress nocallback nofree nosync nounwind willreturn memory(argmem: write)
declare void @llvm.memset.p0.i64(ptr writeonly captures(none), i8, i64, i1 immarg) #2

; Function Attrs: mustprogress nocallback nofree nosync nounwind willreturn memory(argmem: readwrite)
declare void @llvm.memcpy.p0.p0.i64(ptr noalias writeonly captures(none), ptr noalias readonly captures(none), i64, i1 immarg) #1

; Function Attrs: nofree nounwind
declare noundef i32 @printf(ptr noundef readonly captures(none), ...) local_unnamed_addr #3

; Function Attrs: nofree norecurse nosync nounwind sspstrong memory(readwrite, inaccessiblemem: none, target_mem: none) uwtable
define internal fastcc void @softmax(ptr nofree noundef nonnull readonly captures(none) %0, ptr nofree noundef nonnull readonly captures(none) %1) unnamed_addr #4 {
  %3 = load ptr, ptr %0, align 8, !tbaa !9
  %4 = getelementptr inbounds nuw i8, ptr %0, i64 16
  %5 = getelementptr inbounds nuw i8, ptr %0, i64 24
  %6 = load i64, ptr %5, align 8, !tbaa !16
  %7 = icmp sgt i64 %6, 0
  br i1 %7, label %8, label %395

8:                                                ; preds = %2
  %9 = and i64 %6, 3
  %10 = icmp ult i64 %6, 4
  br i1 %10, label %49, label %11

11:                                               ; preds = %8
  %12 = and i64 %6, 9223372036854775804
  br label %13

13:                                               ; preds = %13, %11
  %14 = phi i64 [ 0, %11 ], [ %44, %13 ]
  %15 = phi i64 [ 0, %11 ], [ %43, %13 ]
  %16 = phi i64 [ 0, %11 ], [ %45, %13 ]
  %17 = getelementptr inbounds nuw i8, ptr %3, i64 %14
  %18 = load i8, ptr %17, align 1, !tbaa !18
  %19 = zext i8 %18 to i64
  %20 = shl nsw i64 %14, 3
  %21 = shl i64 %19, %20
  %22 = or i64 %21, %15
  %23 = or disjoint i64 %14, 1
  %24 = getelementptr inbounds nuw i8, ptr %3, i64 %23
  %25 = load i8, ptr %24, align 1, !tbaa !18
  %26 = zext i8 %25 to i64
  %27 = shl nsw i64 %23, 3
  %28 = shl i64 %26, %27
  %29 = or i64 %28, %22
  %30 = or disjoint i64 %14, 2
  %31 = getelementptr inbounds nuw i8, ptr %3, i64 %30
  %32 = load i8, ptr %31, align 1, !tbaa !18
  %33 = zext i8 %32 to i64
  %34 = shl nsw i64 %30, 3
  %35 = shl i64 %33, %34
  %36 = or i64 %35, %29
  %37 = or disjoint i64 %14, 3
  %38 = getelementptr inbounds nuw i8, ptr %3, i64 %37
  %39 = load i8, ptr %38, align 1, !tbaa !18
  %40 = zext i8 %39 to i64
  %41 = shl nsw i64 %37, 3
  %42 = shl i64 %40, %41
  %43 = or i64 %42, %36
  %44 = add nuw nsw i64 %14, 4
  %45 = add i64 %16, 4
  %46 = icmp eq i64 %45, %12
  br i1 %46, label %47, label %13, !llvm.loop !33

47:                                               ; preds = %13
  %48 = icmp eq i64 %9, 0
  br i1 %48, label %66, label %49

49:                                               ; preds = %47, %8
  %50 = phi i64 [ 0, %8 ], [ %44, %47 ]
  %51 = phi i64 [ 0, %8 ], [ %43, %47 ]
  %52 = icmp ne i64 %9, 0
  tail call void @llvm.assume(i1 %52)
  br label %53

53:                                               ; preds = %53, %49
  %54 = phi i64 [ %63, %53 ], [ %50, %49 ]
  %55 = phi i64 [ %62, %53 ], [ %51, %49 ]
  %56 = phi i64 [ %64, %53 ], [ 0, %49 ]
  %57 = getelementptr inbounds nuw i8, ptr %3, i64 %54
  %58 = load i8, ptr %57, align 1, !tbaa !18
  %59 = zext i8 %58 to i64
  %60 = shl nsw i64 %54, 3
  %61 = shl i64 %59, %60
  %62 = or i64 %61, %55
  %63 = add nuw nsw i64 %54, 1
  %64 = add i64 %56, 1
  %65 = icmp eq i64 %64, %9
  br i1 %65, label %66, label %53, !llvm.loop !34

66:                                               ; preds = %53, %47
  %67 = phi i64 [ %43, %47 ], [ %62, %53 ]
  %68 = sitofp i64 %67 to double
  %69 = fmul nnan double %68, f0x3EF0000000000000
  %70 = load i64, ptr %4, align 8, !tbaa !15
  %71 = getelementptr inbounds i8, ptr %3, i64 %70
  %72 = and i64 %6, 3
  %73 = icmp ult i64 %6, 4
  br i1 %73, label %112, label %74

74:                                               ; preds = %66
  %75 = and i64 %6, 9223372036854775804
  br label %76

76:                                               ; preds = %76, %74
  %77 = phi i64 [ 0, %74 ], [ %107, %76 ]
  %78 = phi i64 [ 0, %74 ], [ %106, %76 ]
  %79 = phi i64 [ 0, %74 ], [ %108, %76 ]
  %80 = getelementptr inbounds nuw i8, ptr %71, i64 %77
  %81 = load i8, ptr %80, align 1, !tbaa !18
  %82 = zext i8 %81 to i64
  %83 = shl nsw i64 %77, 3
  %84 = shl i64 %82, %83
  %85 = or i64 %84, %78
  %86 = or disjoint i64 %77, 1
  %87 = getelementptr inbounds nuw i8, ptr %71, i64 %86
  %88 = load i8, ptr %87, align 1, !tbaa !18
  %89 = zext i8 %88 to i64
  %90 = shl nsw i64 %86, 3
  %91 = shl i64 %89, %90
  %92 = or i64 %91, %85
  %93 = or disjoint i64 %77, 2
  %94 = getelementptr inbounds nuw i8, ptr %71, i64 %93
  %95 = load i8, ptr %94, align 1, !tbaa !18
  %96 = zext i8 %95 to i64
  %97 = shl nsw i64 %93, 3
  %98 = shl i64 %96, %97
  %99 = or i64 %98, %92
  %100 = or disjoint i64 %77, 3
  %101 = getelementptr inbounds nuw i8, ptr %71, i64 %100
  %102 = load i8, ptr %101, align 1, !tbaa !18
  %103 = zext i8 %102 to i64
  %104 = shl nsw i64 %100, 3
  %105 = shl i64 %103, %104
  %106 = or i64 %105, %99
  %107 = add nuw nsw i64 %77, 4
  %108 = add i64 %79, 4
  %109 = icmp eq i64 %108, %75
  br i1 %109, label %110, label %76, !llvm.loop !33

110:                                              ; preds = %76
  %111 = icmp eq i64 %72, 0
  br i1 %111, label %129, label %112

112:                                              ; preds = %110, %66
  %113 = phi i64 [ 0, %66 ], [ %107, %110 ]
  %114 = phi i64 [ 0, %66 ], [ %106, %110 ]
  %115 = icmp ne i64 %72, 0
  tail call void @llvm.assume(i1 %115)
  br label %116

116:                                              ; preds = %116, %112
  %117 = phi i64 [ %126, %116 ], [ %113, %112 ]
  %118 = phi i64 [ %125, %116 ], [ %114, %112 ]
  %119 = phi i64 [ %127, %116 ], [ 0, %112 ]
  %120 = getelementptr inbounds nuw i8, ptr %71, i64 %117
  %121 = load i8, ptr %120, align 1, !tbaa !18
  %122 = zext i8 %121 to i64
  %123 = shl nsw i64 %117, 3
  %124 = shl i64 %122, %123
  %125 = or i64 %124, %118
  %126 = add nuw nsw i64 %117, 1
  %127 = add i64 %119, 1
  %128 = icmp eq i64 %127, %72
  br i1 %128, label %129, label %116, !llvm.loop !36

129:                                              ; preds = %116, %110
  %130 = phi i64 [ %106, %110 ], [ %125, %116 ]
  %131 = shl nsw i64 %70, 1
  %132 = getelementptr inbounds i8, ptr %3, i64 %131
  %133 = and i64 %6, 3
  %134 = icmp ult i64 %6, 4
  br i1 %134, label %173, label %135

135:                                              ; preds = %129
  %136 = and i64 %6, 9223372036854775804
  br label %137

137:                                              ; preds = %137, %135
  %138 = phi i64 [ 0, %135 ], [ %168, %137 ]
  %139 = phi i64 [ 0, %135 ], [ %167, %137 ]
  %140 = phi i64 [ 0, %135 ], [ %169, %137 ]
  %141 = getelementptr inbounds nuw i8, ptr %132, i64 %138
  %142 = load i8, ptr %141, align 1, !tbaa !18
  %143 = zext i8 %142 to i64
  %144 = shl nsw i64 %138, 3
  %145 = shl i64 %143, %144
  %146 = or i64 %145, %139
  %147 = or disjoint i64 %138, 1
  %148 = getelementptr inbounds nuw i8, ptr %132, i64 %147
  %149 = load i8, ptr %148, align 1, !tbaa !18
  %150 = zext i8 %149 to i64
  %151 = shl nsw i64 %147, 3
  %152 = shl i64 %150, %151
  %153 = or i64 %152, %146
  %154 = or disjoint i64 %138, 2
  %155 = getelementptr inbounds nuw i8, ptr %132, i64 %154
  %156 = load i8, ptr %155, align 1, !tbaa !18
  %157 = zext i8 %156 to i64
  %158 = shl nsw i64 %154, 3
  %159 = shl i64 %157, %158
  %160 = or i64 %159, %153
  %161 = or disjoint i64 %138, 3
  %162 = getelementptr inbounds nuw i8, ptr %132, i64 %161
  %163 = load i8, ptr %162, align 1, !tbaa !18
  %164 = zext i8 %163 to i64
  %165 = shl nsw i64 %161, 3
  %166 = shl i64 %164, %165
  %167 = or i64 %166, %160
  %168 = add nuw nsw i64 %138, 4
  %169 = add i64 %140, 4
  %170 = icmp eq i64 %169, %136
  br i1 %170, label %171, label %137, !llvm.loop !33

171:                                              ; preds = %137
  %172 = icmp eq i64 %133, 0
  br i1 %172, label %190, label %173

173:                                              ; preds = %171, %129
  %174 = phi i64 [ 0, %129 ], [ %168, %171 ]
  %175 = phi i64 [ 0, %129 ], [ %167, %171 ]
  %176 = icmp ne i64 %133, 0
  tail call void @llvm.assume(i1 %176)
  br label %177

177:                                              ; preds = %177, %173
  %178 = phi i64 [ %187, %177 ], [ %174, %173 ]
  %179 = phi i64 [ %186, %177 ], [ %175, %173 ]
  %180 = phi i64 [ %188, %177 ], [ 0, %173 ]
  %181 = getelementptr inbounds nuw i8, ptr %132, i64 %178
  %182 = load i8, ptr %181, align 1, !tbaa !18
  %183 = zext i8 %182 to i64
  %184 = shl nsw i64 %178, 3
  %185 = shl i64 %183, %184
  %186 = or i64 %185, %179
  %187 = add nuw nsw i64 %178, 1
  %188 = add i64 %180, 1
  %189 = icmp eq i64 %188, %133
  br i1 %189, label %190, label %177, !llvm.loop !37

190:                                              ; preds = %177, %171
  %191 = phi i64 [ %167, %171 ], [ %186, %177 ]
  %192 = sitofp i64 %130 to double
  %193 = fmul nnan double %192, f0x3EF0000000000000
  %194 = fcmp ogt double %193, %69
  %195 = select i1 %194, double %193, double %69
  %196 = sitofp i64 %191 to double
  %197 = fmul nnan double %196, f0x3EF0000000000000
  %198 = fcmp ogt double %197, %195
  %199 = select i1 %198, double %197, double %195
  %200 = and i64 %6, 3
  %201 = icmp ult i64 %6, 4
  br i1 %201, label %240, label %202

202:                                              ; preds = %190
  %203 = and i64 %6, 9223372036854775804
  br label %204

204:                                              ; preds = %204, %202
  %205 = phi i64 [ 0, %202 ], [ %235, %204 ]
  %206 = phi i64 [ 0, %202 ], [ %234, %204 ]
  %207 = phi i64 [ 0, %202 ], [ %236, %204 ]
  %208 = getelementptr inbounds nuw i8, ptr %3, i64 %205
  %209 = load i8, ptr %208, align 1, !tbaa !18
  %210 = zext i8 %209 to i64
  %211 = shl nsw i64 %205, 3
  %212 = shl i64 %210, %211
  %213 = or i64 %212, %206
  %214 = or disjoint i64 %205, 1
  %215 = getelementptr inbounds nuw i8, ptr %3, i64 %214
  %216 = load i8, ptr %215, align 1, !tbaa !18
  %217 = zext i8 %216 to i64
  %218 = shl nsw i64 %214, 3
  %219 = shl i64 %217, %218
  %220 = or i64 %219, %213
  %221 = or disjoint i64 %205, 2
  %222 = getelementptr inbounds nuw i8, ptr %3, i64 %221
  %223 = load i8, ptr %222, align 1, !tbaa !18
  %224 = zext i8 %223 to i64
  %225 = shl nsw i64 %221, 3
  %226 = shl i64 %224, %225
  %227 = or i64 %226, %220
  %228 = or disjoint i64 %205, 3
  %229 = getelementptr inbounds nuw i8, ptr %3, i64 %228
  %230 = load i8, ptr %229, align 1, !tbaa !18
  %231 = zext i8 %230 to i64
  %232 = shl nsw i64 %228, 3
  %233 = shl i64 %231, %232
  %234 = or i64 %233, %227
  %235 = add nuw nsw i64 %205, 4
  %236 = add i64 %207, 4
  %237 = icmp eq i64 %236, %203
  br i1 %237, label %238, label %204, !llvm.loop !33

238:                                              ; preds = %204
  %239 = icmp eq i64 %200, 0
  br i1 %239, label %257, label %240

240:                                              ; preds = %238, %190
  %241 = phi i64 [ 0, %190 ], [ %235, %238 ]
  %242 = phi i64 [ 0, %190 ], [ %234, %238 ]
  %243 = icmp ne i64 %200, 0
  tail call void @llvm.assume(i1 %243)
  br label %244

244:                                              ; preds = %244, %240
  %245 = phi i64 [ %254, %244 ], [ %241, %240 ]
  %246 = phi i64 [ %253, %244 ], [ %242, %240 ]
  %247 = phi i64 [ %255, %244 ], [ 0, %240 ]
  %248 = getelementptr inbounds nuw i8, ptr %3, i64 %245
  %249 = load i8, ptr %248, align 1, !tbaa !18
  %250 = zext i8 %249 to i64
  %251 = shl nsw i64 %245, 3
  %252 = shl i64 %250, %251
  %253 = or i64 %252, %246
  %254 = add nuw nsw i64 %245, 1
  %255 = add i64 %247, 1
  %256 = icmp eq i64 %255, %200
  br i1 %256, label %257, label %244, !llvm.loop !38

257:                                              ; preds = %244, %238
  %258 = phi i64 [ %234, %238 ], [ %253, %244 ]
  %259 = sitofp i64 %258 to double
  %260 = fmul nnan double %259, f0x3EF0000000000000
  %261 = fsub double %260, %199
  %262 = tail call double @exp(double noundef %261) #9
  %263 = getelementptr inbounds i8, ptr %3, i64 %70
  %264 = and i64 %6, 3
  %265 = icmp ult i64 %6, 4
  br i1 %265, label %304, label %266

266:                                              ; preds = %257
  %267 = and i64 %6, 9223372036854775804
  br label %268

268:                                              ; preds = %268, %266
  %269 = phi i64 [ 0, %266 ], [ %299, %268 ]
  %270 = phi i64 [ 0, %266 ], [ %298, %268 ]
  %271 = phi i64 [ 0, %266 ], [ %300, %268 ]
  %272 = getelementptr inbounds nuw i8, ptr %263, i64 %269
  %273 = load i8, ptr %272, align 1, !tbaa !18
  %274 = zext i8 %273 to i64
  %275 = shl nsw i64 %269, 3
  %276 = shl i64 %274, %275
  %277 = or i64 %276, %270
  %278 = or disjoint i64 %269, 1
  %279 = getelementptr inbounds nuw i8, ptr %263, i64 %278
  %280 = load i8, ptr %279, align 1, !tbaa !18
  %281 = zext i8 %280 to i64
  %282 = shl nsw i64 %278, 3
  %283 = shl i64 %281, %282
  %284 = or i64 %283, %277
  %285 = or disjoint i64 %269, 2
  %286 = getelementptr inbounds nuw i8, ptr %263, i64 %285
  %287 = load i8, ptr %286, align 1, !tbaa !18
  %288 = zext i8 %287 to i64
  %289 = shl nsw i64 %285, 3
  %290 = shl i64 %288, %289
  %291 = or i64 %290, %284
  %292 = or disjoint i64 %269, 3
  %293 = getelementptr inbounds nuw i8, ptr %263, i64 %292
  %294 = load i8, ptr %293, align 1, !tbaa !18
  %295 = zext i8 %294 to i64
  %296 = shl nsw i64 %292, 3
  %297 = shl i64 %295, %296
  %298 = or i64 %297, %291
  %299 = add nuw nsw i64 %269, 4
  %300 = add i64 %271, 4
  %301 = icmp eq i64 %300, %267
  br i1 %301, label %302, label %268, !llvm.loop !33

302:                                              ; preds = %268
  %303 = icmp eq i64 %264, 0
  br i1 %303, label %321, label %304

304:                                              ; preds = %302, %257
  %305 = phi i64 [ 0, %257 ], [ %299, %302 ]
  %306 = phi i64 [ 0, %257 ], [ %298, %302 ]
  %307 = icmp ne i64 %264, 0
  tail call void @llvm.assume(i1 %307)
  br label %308

308:                                              ; preds = %308, %304
  %309 = phi i64 [ %318, %308 ], [ %305, %304 ]
  %310 = phi i64 [ %317, %308 ], [ %306, %304 ]
  %311 = phi i64 [ %319, %308 ], [ 0, %304 ]
  %312 = getelementptr inbounds nuw i8, ptr %263, i64 %309
  %313 = load i8, ptr %312, align 1, !tbaa !18
  %314 = zext i8 %313 to i64
  %315 = shl nsw i64 %309, 3
  %316 = shl i64 %314, %315
  %317 = or i64 %316, %310
  %318 = add nuw nsw i64 %309, 1
  %319 = add i64 %311, 1
  %320 = icmp eq i64 %319, %264
  br i1 %320, label %321, label %308, !llvm.loop !39

321:                                              ; preds = %308, %302
  %322 = phi i64 [ %298, %302 ], [ %317, %308 ]
  %323 = fadd double %262, 0.000000e+00
  %324 = sitofp i64 %322 to double
  %325 = fmul nnan double %324, f0x3EF0000000000000
  %326 = fsub double %325, %199
  %327 = tail call double @exp(double noundef %326) #9
  %328 = shl nsw i64 %70, 1
  %329 = getelementptr inbounds i8, ptr %3, i64 %328
  %330 = and i64 %6, 3
  %331 = icmp ult i64 %6, 4
  br i1 %331, label %370, label %332

332:                                              ; preds = %321
  %333 = and i64 %6, 9223372036854775804
  br label %334

334:                                              ; preds = %334, %332
  %335 = phi i64 [ 0, %332 ], [ %365, %334 ]
  %336 = phi i64 [ 0, %332 ], [ %364, %334 ]
  %337 = phi i64 [ 0, %332 ], [ %366, %334 ]
  %338 = getelementptr inbounds nuw i8, ptr %329, i64 %335
  %339 = load i8, ptr %338, align 1, !tbaa !18
  %340 = zext i8 %339 to i64
  %341 = shl nsw i64 %335, 3
  %342 = shl i64 %340, %341
  %343 = or i64 %342, %336
  %344 = or disjoint i64 %335, 1
  %345 = getelementptr inbounds nuw i8, ptr %329, i64 %344
  %346 = load i8, ptr %345, align 1, !tbaa !18
  %347 = zext i8 %346 to i64
  %348 = shl nsw i64 %344, 3
  %349 = shl i64 %347, %348
  %350 = or i64 %349, %343
  %351 = or disjoint i64 %335, 2
  %352 = getelementptr inbounds nuw i8, ptr %329, i64 %351
  %353 = load i8, ptr %352, align 1, !tbaa !18
  %354 = zext i8 %353 to i64
  %355 = shl nsw i64 %351, 3
  %356 = shl i64 %354, %355
  %357 = or i64 %356, %350
  %358 = or disjoint i64 %335, 3
  %359 = getelementptr inbounds nuw i8, ptr %329, i64 %358
  %360 = load i8, ptr %359, align 1, !tbaa !18
  %361 = zext i8 %360 to i64
  %362 = shl nsw i64 %358, 3
  %363 = shl i64 %361, %362
  %364 = or i64 %363, %357
  %365 = add nuw nsw i64 %335, 4
  %366 = add i64 %337, 4
  %367 = icmp eq i64 %366, %333
  br i1 %367, label %368, label %334, !llvm.loop !33

368:                                              ; preds = %334
  %369 = icmp eq i64 %330, 0
  br i1 %369, label %387, label %370

370:                                              ; preds = %368, %321
  %371 = phi i64 [ 0, %321 ], [ %365, %368 ]
  %372 = phi i64 [ 0, %321 ], [ %364, %368 ]
  %373 = icmp ne i64 %330, 0
  tail call void @llvm.assume(i1 %373)
  br label %374

374:                                              ; preds = %374, %370
  %375 = phi i64 [ %384, %374 ], [ %371, %370 ]
  %376 = phi i64 [ %383, %374 ], [ %372, %370 ]
  %377 = phi i64 [ %385, %374 ], [ 0, %370 ]
  %378 = getelementptr inbounds nuw i8, ptr %329, i64 %375
  %379 = load i8, ptr %378, align 1, !tbaa !18
  %380 = zext i8 %379 to i64
  %381 = shl nsw i64 %375, 3
  %382 = shl i64 %380, %381
  %383 = or i64 %382, %376
  %384 = add nuw nsw i64 %375, 1
  %385 = add i64 %377, 1
  %386 = icmp eq i64 %385, %330
  br i1 %386, label %387, label %374, !llvm.loop !40

387:                                              ; preds = %374, %368
  %388 = phi i64 [ %364, %368 ], [ %383, %374 ]
  %389 = fadd double %323, %327
  %390 = sitofp i64 %388 to double
  %391 = fmul nnan double %390, f0x3EF0000000000000
  %392 = fsub double %391, %199
  %393 = tail call double @exp(double noundef %392) #9
  %394 = fadd double %389, %393
  br label %395

395:                                              ; preds = %2, %387
  %396 = phi double [ %393, %387 ], [ 1.000000e+00, %2 ]
  %397 = phi double [ %327, %387 ], [ 1.000000e+00, %2 ]
  %398 = phi double [ %262, %387 ], [ 1.000000e+00, %2 ]
  %399 = phi double [ %394, %387 ], [ 3.000000e+00, %2 ]
  %400 = getelementptr inbounds nuw i8, ptr %1, i64 16
  %401 = getelementptr inbounds nuw i8, ptr %1, i64 24
  %402 = load i64, ptr %401, align 8, !tbaa !16
  %403 = icmp sgt i64 %402, 0
  br i1 %403, label %405, label %404

404:                                              ; preds = %445, %419, %436, %395
  ret void

405:                                              ; preds = %395
  %406 = fdiv double %398, %399
  %407 = fmul double %406, 6.553600e+04
  %408 = fptosi double %407 to i64
  %409 = load ptr, ptr %1, align 8, !tbaa !9
  br label %410

410:                                              ; preds = %405, %410
  %411 = phi i64 [ %416, %410 ], [ 0, %405 ]
  %412 = shl nsw i64 %411, 3
  %413 = ashr i64 %408, %412
  %414 = trunc i64 %413 to i8
  %415 = getelementptr inbounds nuw i8, ptr %409, i64 %411
  store i8 %414, ptr %415, align 1, !tbaa !18
  %416 = add nuw nsw i64 %411, 1
  %417 = load i64, ptr %401, align 8, !tbaa !16
  %418 = icmp slt i64 %416, %417
  br i1 %418, label %410, label %419, !llvm.loop !41

419:                                              ; preds = %410
  %420 = load ptr, ptr %1, align 8, !tbaa !9
  %421 = fdiv double %397, %399
  %422 = fmul double %421, 6.553600e+04
  %423 = fptosi double %422 to i64
  %424 = load i64, ptr %400, align 8, !tbaa !15
  %425 = getelementptr inbounds i8, ptr %420, i64 %424
  %426 = icmp sgt i64 %417, 0
  br i1 %426, label %427, label %404

427:                                              ; preds = %419, %427
  %428 = phi i64 [ %433, %427 ], [ 0, %419 ]
  %429 = shl nsw i64 %428, 3
  %430 = ashr i64 %423, %429
  %431 = trunc i64 %430 to i8
  %432 = getelementptr inbounds nuw i8, ptr %425, i64 %428
  store i8 %431, ptr %432, align 1, !tbaa !18
  %433 = add nuw nsw i64 %428, 1
  %434 = load i64, ptr %401, align 8, !tbaa !16
  %435 = icmp slt i64 %433, %434
  br i1 %435, label %427, label %436, !llvm.loop !41

436:                                              ; preds = %427
  %437 = load ptr, ptr %1, align 8, !tbaa !9
  %438 = load i64, ptr %400, align 8, !tbaa !15
  %439 = icmp sgt i64 %434, 0
  %440 = fdiv double %396, %399
  %441 = fmul double %440, 6.553600e+04
  %442 = fptosi double %441 to i64
  %443 = shl nsw i64 %438, 1
  %444 = getelementptr inbounds i8, ptr %437, i64 %443
  br i1 %439, label %445, label %404

445:                                              ; preds = %436, %445
  %446 = phi i64 [ %451, %445 ], [ 0, %436 ]
  %447 = shl nsw i64 %446, 3
  %448 = ashr i64 %442, %447
  %449 = trunc i64 %448 to i8
  %450 = getelementptr inbounds nuw i8, ptr %444, i64 %446
  store i8 %449, ptr %450, align 1, !tbaa !18
  %451 = add nuw nsw i64 %446, 1
  %452 = load i64, ptr %401, align 8, !tbaa !16
  %453 = icmp slt i64 %451, %452
  br i1 %453, label %445, label %404, !llvm.loop !41
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind willreturn memory(argmem: readwrite)
declare void @llvm.lifetime.end.p0(ptr captures(none)) #1

; Function Attrs: nofree norecurse nosync nounwind sspstrong memory(readwrite, inaccessiblemem: none, target_mem: none) uwtable
define internal fastcc void @layernorm(ptr nofree noundef nonnull readonly captures(none) %0, i64 noundef range(i64 3, 5) %1, ptr nofree noundef nonnull readonly captures(none) %2, ptr nofree noundef nonnull readonly captures(none) %3, ptr nofree noundef nonnull readonly captures(none) %4) unnamed_addr #4 {
  %6 = load ptr, ptr %0, align 8, !tbaa !9
  %7 = getelementptr inbounds nuw i8, ptr %0, i64 16
  %8 = load i64, ptr %7, align 8, !tbaa !15
  %9 = getelementptr inbounds nuw i8, ptr %0, i64 24
  %10 = load i64, ptr %9, align 8, !tbaa !16
  %11 = icmp sgt i64 %10, 0
  br i1 %11, label %12, label %521

12:                                               ; preds = %5
  %13 = add nsw i64 %10, -1
  %14 = and i64 %10, 3
  %15 = icmp ult i64 %10, 4
  br i1 %15, label %54, label %16

16:                                               ; preds = %12
  %17 = and i64 %10, 9223372036854775804
  br label %18

18:                                               ; preds = %18, %16
  %19 = phi i64 [ 0, %16 ], [ %49, %18 ]
  %20 = phi i64 [ 0, %16 ], [ %48, %18 ]
  %21 = phi i64 [ 0, %16 ], [ %50, %18 ]
  %22 = getelementptr inbounds nuw i8, ptr %6, i64 %19
  %23 = load i8, ptr %22, align 1, !tbaa !18
  %24 = zext i8 %23 to i64
  %25 = shl nsw i64 %19, 3
  %26 = shl i64 %24, %25
  %27 = or i64 %26, %20
  %28 = or disjoint i64 %19, 1
  %29 = getelementptr inbounds nuw i8, ptr %6, i64 %28
  %30 = load i8, ptr %29, align 1, !tbaa !18
  %31 = zext i8 %30 to i64
  %32 = shl nsw i64 %28, 3
  %33 = shl i64 %31, %32
  %34 = or i64 %33, %27
  %35 = or disjoint i64 %19, 2
  %36 = getelementptr inbounds nuw i8, ptr %6, i64 %35
  %37 = load i8, ptr %36, align 1, !tbaa !18
  %38 = zext i8 %37 to i64
  %39 = shl nsw i64 %35, 3
  %40 = shl i64 %38, %39
  %41 = or i64 %40, %34
  %42 = or disjoint i64 %19, 3
  %43 = getelementptr inbounds nuw i8, ptr %6, i64 %42
  %44 = load i8, ptr %43, align 1, !tbaa !18
  %45 = zext i8 %44 to i64
  %46 = shl nsw i64 %42, 3
  %47 = shl i64 %45, %46
  %48 = or i64 %47, %41
  %49 = add nuw nsw i64 %19, 4
  %50 = add i64 %21, 4
  %51 = icmp eq i64 %50, %17
  br i1 %51, label %52, label %18, !llvm.loop !33

52:                                               ; preds = %18
  %53 = icmp eq i64 %14, 0
  br i1 %53, label %71, label %54

54:                                               ; preds = %52, %12
  %55 = phi i64 [ 0, %12 ], [ %49, %52 ]
  %56 = phi i64 [ 0, %12 ], [ %48, %52 ]
  %57 = icmp ne i64 %14, 0
  tail call void @llvm.assume(i1 %57)
  br label %58

58:                                               ; preds = %58, %54
  %59 = phi i64 [ %68, %58 ], [ %55, %54 ]
  %60 = phi i64 [ %67, %58 ], [ %56, %54 ]
  %61 = phi i64 [ %69, %58 ], [ 0, %54 ]
  %62 = getelementptr inbounds nuw i8, ptr %6, i64 %59
  %63 = load i8, ptr %62, align 1, !tbaa !18
  %64 = zext i8 %63 to i64
  %65 = shl nsw i64 %59, 3
  %66 = shl i64 %64, %65
  %67 = or i64 %66, %60
  %68 = add nuw nsw i64 %59, 1
  %69 = add i64 %61, 1
  %70 = icmp eq i64 %69, %14
  br i1 %70, label %71, label %58, !llvm.loop !42

71:                                               ; preds = %52, %58
  %72 = phi i64 [ %48, %52 ], [ %67, %58 ]
  %73 = getelementptr inbounds i8, ptr %6, i64 %8
  %74 = and i64 %10, 3
  %75 = icmp ult i64 %10, 4
  br i1 %75, label %114, label %76

76:                                               ; preds = %71
  %77 = and i64 %10, 9223372036854775804
  br label %78

78:                                               ; preds = %78, %76
  %79 = phi i64 [ 0, %76 ], [ %109, %78 ]
  %80 = phi i64 [ 0, %76 ], [ %108, %78 ]
  %81 = phi i64 [ 0, %76 ], [ %110, %78 ]
  %82 = getelementptr inbounds nuw i8, ptr %73, i64 %79
  %83 = load i8, ptr %82, align 1, !tbaa !18
  %84 = zext i8 %83 to i64
  %85 = shl nsw i64 %79, 3
  %86 = shl i64 %84, %85
  %87 = or i64 %86, %80
  %88 = or disjoint i64 %79, 1
  %89 = getelementptr inbounds nuw i8, ptr %73, i64 %88
  %90 = load i8, ptr %89, align 1, !tbaa !18
  %91 = zext i8 %90 to i64
  %92 = shl nsw i64 %88, 3
  %93 = shl i64 %91, %92
  %94 = or i64 %93, %87
  %95 = or disjoint i64 %79, 2
  %96 = getelementptr inbounds nuw i8, ptr %73, i64 %95
  %97 = load i8, ptr %96, align 1, !tbaa !18
  %98 = zext i8 %97 to i64
  %99 = shl nsw i64 %95, 3
  %100 = shl i64 %98, %99
  %101 = or i64 %100, %94
  %102 = or disjoint i64 %79, 3
  %103 = getelementptr inbounds nuw i8, ptr %73, i64 %102
  %104 = load i8, ptr %103, align 1, !tbaa !18
  %105 = zext i8 %104 to i64
  %106 = shl nsw i64 %102, 3
  %107 = shl i64 %105, %106
  %108 = or i64 %107, %101
  %109 = add nuw nsw i64 %79, 4
  %110 = add i64 %81, 4
  %111 = icmp eq i64 %110, %77
  br i1 %111, label %112, label %78, !llvm.loop !33

112:                                              ; preds = %78
  %113 = icmp eq i64 %74, 0
  br i1 %113, label %131, label %114

114:                                              ; preds = %112, %71
  %115 = phi i64 [ 0, %71 ], [ %109, %112 ]
  %116 = phi i64 [ 0, %71 ], [ %108, %112 ]
  %117 = icmp ne i64 %74, 0
  tail call void @llvm.assume(i1 %117)
  br label %118

118:                                              ; preds = %118, %114
  %119 = phi i64 [ %128, %118 ], [ %115, %114 ]
  %120 = phi i64 [ %127, %118 ], [ %116, %114 ]
  %121 = phi i64 [ %129, %118 ], [ 0, %114 ]
  %122 = getelementptr inbounds nuw i8, ptr %73, i64 %119
  %123 = load i8, ptr %122, align 1, !tbaa !18
  %124 = zext i8 %123 to i64
  %125 = shl nsw i64 %119, 3
  %126 = shl i64 %124, %125
  %127 = or i64 %126, %120
  %128 = add nuw nsw i64 %119, 1
  %129 = add i64 %121, 1
  %130 = icmp eq i64 %129, %74
  br i1 %130, label %131, label %118, !llvm.loop !42

131:                                              ; preds = %118, %112
  %132 = phi i64 [ %108, %112 ], [ %127, %118 ]
  %133 = add nsw i64 %132, %72
  %134 = shl nsw i64 %8, 1
  %135 = getelementptr inbounds i8, ptr %6, i64 %134
  %136 = and i64 %10, 3
  %137 = icmp ult i64 %10, 4
  br i1 %137, label %176, label %138

138:                                              ; preds = %131
  %139 = and i64 %10, 9223372036854775804
  br label %140

140:                                              ; preds = %140, %138
  %141 = phi i64 [ 0, %138 ], [ %171, %140 ]
  %142 = phi i64 [ 0, %138 ], [ %170, %140 ]
  %143 = phi i64 [ 0, %138 ], [ %172, %140 ]
  %144 = getelementptr inbounds nuw i8, ptr %135, i64 %141
  %145 = load i8, ptr %144, align 1, !tbaa !18
  %146 = zext i8 %145 to i64
  %147 = shl nsw i64 %141, 3
  %148 = shl i64 %146, %147
  %149 = or i64 %148, %142
  %150 = or disjoint i64 %141, 1
  %151 = getelementptr inbounds nuw i8, ptr %135, i64 %150
  %152 = load i8, ptr %151, align 1, !tbaa !18
  %153 = zext i8 %152 to i64
  %154 = shl nsw i64 %150, 3
  %155 = shl i64 %153, %154
  %156 = or i64 %155, %149
  %157 = or disjoint i64 %141, 2
  %158 = getelementptr inbounds nuw i8, ptr %135, i64 %157
  %159 = load i8, ptr %158, align 1, !tbaa !18
  %160 = zext i8 %159 to i64
  %161 = shl nsw i64 %157, 3
  %162 = shl i64 %160, %161
  %163 = or i64 %162, %156
  %164 = or disjoint i64 %141, 3
  %165 = getelementptr inbounds nuw i8, ptr %135, i64 %164
  %166 = load i8, ptr %165, align 1, !tbaa !18
  %167 = zext i8 %166 to i64
  %168 = shl nsw i64 %164, 3
  %169 = shl i64 %167, %168
  %170 = or i64 %169, %163
  %171 = add nuw nsw i64 %141, 4
  %172 = add i64 %143, 4
  %173 = icmp eq i64 %172, %139
  br i1 %173, label %174, label %140, !llvm.loop !33

174:                                              ; preds = %140
  %175 = icmp eq i64 %136, 0
  br i1 %175, label %193, label %176

176:                                              ; preds = %174, %131
  %177 = phi i64 [ 0, %131 ], [ %171, %174 ]
  %178 = phi i64 [ 0, %131 ], [ %170, %174 ]
  %179 = icmp ne i64 %136, 0
  tail call void @llvm.assume(i1 %179)
  br label %180

180:                                              ; preds = %180, %176
  %181 = phi i64 [ %190, %180 ], [ %177, %176 ]
  %182 = phi i64 [ %189, %180 ], [ %178, %176 ]
  %183 = phi i64 [ %191, %180 ], [ 0, %176 ]
  %184 = getelementptr inbounds nuw i8, ptr %135, i64 %181
  %185 = load i8, ptr %184, align 1, !tbaa !18
  %186 = zext i8 %185 to i64
  %187 = shl nsw i64 %181, 3
  %188 = shl i64 %186, %187
  %189 = or i64 %188, %182
  %190 = add nuw nsw i64 %181, 1
  %191 = add i64 %183, 1
  %192 = icmp eq i64 %191, %136
  br i1 %192, label %193, label %180, !llvm.loop !42

193:                                              ; preds = %180, %174
  %194 = phi i64 [ %170, %174 ], [ %189, %180 ]
  %195 = add nsw i64 %194, %133
  %196 = icmp eq i64 %1, 3
  br i1 %196, label %260, label %197

197:                                              ; preds = %193
  %198 = mul nsw i64 %8, 3
  %199 = getelementptr inbounds i8, ptr %6, i64 %198
  %200 = and i64 %10, 3
  %201 = icmp ult i64 %13, 3
  br i1 %201, label %240, label %202

202:                                              ; preds = %197
  %203 = and i64 %10, 9223372036854775804
  br label %204

204:                                              ; preds = %204, %202
  %205 = phi i64 [ 0, %202 ], [ %235, %204 ]
  %206 = phi i64 [ 0, %202 ], [ %234, %204 ]
  %207 = phi i64 [ 0, %202 ], [ %236, %204 ]
  %208 = getelementptr inbounds nuw i8, ptr %199, i64 %205
  %209 = load i8, ptr %208, align 1, !tbaa !18
  %210 = zext i8 %209 to i64
  %211 = shl nsw i64 %205, 3
  %212 = shl i64 %210, %211
  %213 = or i64 %212, %206
  %214 = or disjoint i64 %205, 1
  %215 = getelementptr inbounds nuw i8, ptr %199, i64 %214
  %216 = load i8, ptr %215, align 1, !tbaa !18
  %217 = zext i8 %216 to i64
  %218 = shl nsw i64 %214, 3
  %219 = shl i64 %217, %218
  %220 = or i64 %219, %213
  %221 = or disjoint i64 %205, 2
  %222 = getelementptr inbounds nuw i8, ptr %199, i64 %221
  %223 = load i8, ptr %222, align 1, !tbaa !18
  %224 = zext i8 %223 to i64
  %225 = shl nsw i64 %221, 3
  %226 = shl i64 %224, %225
  %227 = or i64 %226, %220
  %228 = or disjoint i64 %205, 3
  %229 = getelementptr inbounds nuw i8, ptr %199, i64 %228
  %230 = load i8, ptr %229, align 1, !tbaa !18
  %231 = zext i8 %230 to i64
  %232 = shl nsw i64 %228, 3
  %233 = shl i64 %231, %232
  %234 = or i64 %233, %227
  %235 = add nuw nsw i64 %205, 4
  %236 = add i64 %207, 4
  %237 = icmp eq i64 %236, %203
  br i1 %237, label %238, label %204, !llvm.loop !33

238:                                              ; preds = %204
  %239 = icmp eq i64 %200, 0
  br i1 %239, label %257, label %240

240:                                              ; preds = %238, %197
  %241 = phi i64 [ 0, %197 ], [ %235, %238 ]
  %242 = phi i64 [ 0, %197 ], [ %234, %238 ]
  %243 = icmp ne i64 %200, 0
  tail call void @llvm.assume(i1 %243)
  br label %244

244:                                              ; preds = %244, %240
  %245 = phi i64 [ %254, %244 ], [ %241, %240 ]
  %246 = phi i64 [ %253, %244 ], [ %242, %240 ]
  %247 = phi i64 [ %255, %244 ], [ 0, %240 ]
  %248 = getelementptr inbounds nuw i8, ptr %199, i64 %245
  %249 = load i8, ptr %248, align 1, !tbaa !18
  %250 = zext i8 %249 to i64
  %251 = shl nsw i64 %245, 3
  %252 = shl i64 %250, %251
  %253 = or i64 %252, %246
  %254 = add nuw nsw i64 %245, 1
  %255 = add i64 %247, 1
  %256 = icmp eq i64 %255, %200
  br i1 %256, label %257, label %244, !llvm.loop !42

257:                                              ; preds = %244, %238
  %258 = phi i64 [ %234, %238 ], [ %253, %244 ]
  %259 = add nsw i64 %258, %195
  br label %260

260:                                              ; preds = %257, %193
  %261 = phi i64 [ %259, %257 ], [ %195, %193 ]
  %262 = sdiv i64 %261, %1
  %263 = and i64 %10, 3
  %264 = icmp ult i64 %13, 3
  br i1 %264, label %303, label %265

265:                                              ; preds = %260
  %266 = and i64 %10, 9223372036854775804
  br label %267

267:                                              ; preds = %267, %265
  %268 = phi i64 [ 0, %265 ], [ %298, %267 ]
  %269 = phi i64 [ 0, %265 ], [ %297, %267 ]
  %270 = phi i64 [ 0, %265 ], [ %299, %267 ]
  %271 = getelementptr inbounds nuw i8, ptr %6, i64 %268
  %272 = load i8, ptr %271, align 1, !tbaa !18
  %273 = zext i8 %272 to i64
  %274 = shl nsw i64 %268, 3
  %275 = shl i64 %273, %274
  %276 = or i64 %275, %269
  %277 = or disjoint i64 %268, 1
  %278 = getelementptr inbounds nuw i8, ptr %6, i64 %277
  %279 = load i8, ptr %278, align 1, !tbaa !18
  %280 = zext i8 %279 to i64
  %281 = shl nsw i64 %277, 3
  %282 = shl i64 %280, %281
  %283 = or i64 %282, %276
  %284 = or disjoint i64 %268, 2
  %285 = getelementptr inbounds nuw i8, ptr %6, i64 %284
  %286 = load i8, ptr %285, align 1, !tbaa !18
  %287 = zext i8 %286 to i64
  %288 = shl nsw i64 %284, 3
  %289 = shl i64 %287, %288
  %290 = or i64 %289, %283
  %291 = or disjoint i64 %268, 3
  %292 = getelementptr inbounds nuw i8, ptr %6, i64 %291
  %293 = load i8, ptr %292, align 1, !tbaa !18
  %294 = zext i8 %293 to i64
  %295 = shl nsw i64 %291, 3
  %296 = shl i64 %294, %295
  %297 = or i64 %296, %290
  %298 = add nuw nsw i64 %268, 4
  %299 = add i64 %270, 4
  %300 = icmp eq i64 %299, %266
  br i1 %300, label %301, label %267, !llvm.loop !33

301:                                              ; preds = %267
  %302 = icmp eq i64 %263, 0
  br i1 %302, label %320, label %303

303:                                              ; preds = %301, %260
  %304 = phi i64 [ 0, %260 ], [ %298, %301 ]
  %305 = phi i64 [ 0, %260 ], [ %297, %301 ]
  %306 = icmp ne i64 %263, 0
  tail call void @llvm.assume(i1 %306)
  br label %307

307:                                              ; preds = %307, %303
  %308 = phi i64 [ %317, %307 ], [ %304, %303 ]
  %309 = phi i64 [ %316, %307 ], [ %305, %303 ]
  %310 = phi i64 [ %318, %307 ], [ 0, %303 ]
  %311 = getelementptr inbounds nuw i8, ptr %6, i64 %308
  %312 = load i8, ptr %311, align 1, !tbaa !18
  %313 = zext i8 %312 to i64
  %314 = shl nsw i64 %308, 3
  %315 = shl i64 %313, %314
  %316 = or i64 %315, %309
  %317 = add nuw nsw i64 %308, 1
  %318 = add i64 %310, 1
  %319 = icmp eq i64 %318, %263
  br i1 %319, label %320, label %307, !llvm.loop !43

320:                                              ; preds = %307, %301
  %321 = phi i64 [ %297, %301 ], [ %316, %307 ]
  %322 = sub nsw i64 %321, %262
  %323 = mul nsw i64 %322, %322
  %324 = lshr i64 %323, 16
  %325 = getelementptr inbounds i8, ptr %6, i64 %8
  %326 = and i64 %10, 3
  %327 = icmp ult i64 %13, 3
  br i1 %327, label %366, label %328

328:                                              ; preds = %320
  %329 = and i64 %10, 9223372036854775804
  br label %330

330:                                              ; preds = %330, %328
  %331 = phi i64 [ 0, %328 ], [ %361, %330 ]
  %332 = phi i64 [ 0, %328 ], [ %360, %330 ]
  %333 = phi i64 [ 0, %328 ], [ %362, %330 ]
  %334 = getelementptr inbounds nuw i8, ptr %325, i64 %331
  %335 = load i8, ptr %334, align 1, !tbaa !18
  %336 = zext i8 %335 to i64
  %337 = shl nsw i64 %331, 3
  %338 = shl i64 %336, %337
  %339 = or i64 %338, %332
  %340 = or disjoint i64 %331, 1
  %341 = getelementptr inbounds nuw i8, ptr %325, i64 %340
  %342 = load i8, ptr %341, align 1, !tbaa !18
  %343 = zext i8 %342 to i64
  %344 = shl nsw i64 %340, 3
  %345 = shl i64 %343, %344
  %346 = or i64 %345, %339
  %347 = or disjoint i64 %331, 2
  %348 = getelementptr inbounds nuw i8, ptr %325, i64 %347
  %349 = load i8, ptr %348, align 1, !tbaa !18
  %350 = zext i8 %349 to i64
  %351 = shl nsw i64 %347, 3
  %352 = shl i64 %350, %351
  %353 = or i64 %352, %346
  %354 = or disjoint i64 %331, 3
  %355 = getelementptr inbounds nuw i8, ptr %325, i64 %354
  %356 = load i8, ptr %355, align 1, !tbaa !18
  %357 = zext i8 %356 to i64
  %358 = shl nsw i64 %354, 3
  %359 = shl i64 %357, %358
  %360 = or i64 %359, %353
  %361 = add nuw nsw i64 %331, 4
  %362 = add i64 %333, 4
  %363 = icmp eq i64 %362, %329
  br i1 %363, label %364, label %330, !llvm.loop !33

364:                                              ; preds = %330
  %365 = icmp eq i64 %326, 0
  br i1 %365, label %383, label %366

366:                                              ; preds = %364, %320
  %367 = phi i64 [ 0, %320 ], [ %361, %364 ]
  %368 = phi i64 [ 0, %320 ], [ %360, %364 ]
  %369 = icmp ne i64 %326, 0
  tail call void @llvm.assume(i1 %369)
  br label %370

370:                                              ; preds = %370, %366
  %371 = phi i64 [ %380, %370 ], [ %367, %366 ]
  %372 = phi i64 [ %379, %370 ], [ %368, %366 ]
  %373 = phi i64 [ %381, %370 ], [ 0, %366 ]
  %374 = getelementptr inbounds nuw i8, ptr %325, i64 %371
  %375 = load i8, ptr %374, align 1, !tbaa !18
  %376 = zext i8 %375 to i64
  %377 = shl nsw i64 %371, 3
  %378 = shl i64 %376, %377
  %379 = or i64 %378, %372
  %380 = add nuw nsw i64 %371, 1
  %381 = add i64 %373, 1
  %382 = icmp eq i64 %381, %326
  br i1 %382, label %383, label %370, !llvm.loop !43

383:                                              ; preds = %370, %364
  %384 = phi i64 [ %360, %364 ], [ %379, %370 ]
  %385 = sub nsw i64 %384, %262
  %386 = mul nsw i64 %385, %385
  %387 = lshr i64 %386, 16
  %388 = add nuw nsw i64 %387, %324
  %389 = shl nsw i64 %8, 1
  %390 = getelementptr inbounds i8, ptr %6, i64 %389
  %391 = and i64 %10, 3
  %392 = icmp ult i64 %13, 3
  br i1 %392, label %431, label %393

393:                                              ; preds = %383
  %394 = and i64 %10, 9223372036854775804
  br label %395

395:                                              ; preds = %395, %393
  %396 = phi i64 [ 0, %393 ], [ %426, %395 ]
  %397 = phi i64 [ 0, %393 ], [ %425, %395 ]
  %398 = phi i64 [ 0, %393 ], [ %427, %395 ]
  %399 = getelementptr inbounds nuw i8, ptr %390, i64 %396
  %400 = load i8, ptr %399, align 1, !tbaa !18
  %401 = zext i8 %400 to i64
  %402 = shl nsw i64 %396, 3
  %403 = shl i64 %401, %402
  %404 = or i64 %403, %397
  %405 = or disjoint i64 %396, 1
  %406 = getelementptr inbounds nuw i8, ptr %390, i64 %405
  %407 = load i8, ptr %406, align 1, !tbaa !18
  %408 = zext i8 %407 to i64
  %409 = shl nsw i64 %405, 3
  %410 = shl i64 %408, %409
  %411 = or i64 %410, %404
  %412 = or disjoint i64 %396, 2
  %413 = getelementptr inbounds nuw i8, ptr %390, i64 %412
  %414 = load i8, ptr %413, align 1, !tbaa !18
  %415 = zext i8 %414 to i64
  %416 = shl nsw i64 %412, 3
  %417 = shl i64 %415, %416
  %418 = or i64 %417, %411
  %419 = or disjoint i64 %396, 3
  %420 = getelementptr inbounds nuw i8, ptr %390, i64 %419
  %421 = load i8, ptr %420, align 1, !tbaa !18
  %422 = zext i8 %421 to i64
  %423 = shl nsw i64 %419, 3
  %424 = shl i64 %422, %423
  %425 = or i64 %424, %418
  %426 = add nuw nsw i64 %396, 4
  %427 = add i64 %398, 4
  %428 = icmp eq i64 %427, %394
  br i1 %428, label %429, label %395, !llvm.loop !33

429:                                              ; preds = %395
  %430 = icmp eq i64 %391, 0
  br i1 %430, label %448, label %431

431:                                              ; preds = %429, %383
  %432 = phi i64 [ 0, %383 ], [ %426, %429 ]
  %433 = phi i64 [ 0, %383 ], [ %425, %429 ]
  %434 = icmp ne i64 %391, 0
  tail call void @llvm.assume(i1 %434)
  br label %435

435:                                              ; preds = %435, %431
  %436 = phi i64 [ %445, %435 ], [ %432, %431 ]
  %437 = phi i64 [ %444, %435 ], [ %433, %431 ]
  %438 = phi i64 [ %446, %435 ], [ 0, %431 ]
  %439 = getelementptr inbounds nuw i8, ptr %390, i64 %436
  %440 = load i8, ptr %439, align 1, !tbaa !18
  %441 = zext i8 %440 to i64
  %442 = shl nsw i64 %436, 3
  %443 = shl i64 %441, %442
  %444 = or i64 %443, %437
  %445 = add nuw nsw i64 %436, 1
  %446 = add i64 %438, 1
  %447 = icmp eq i64 %446, %391
  br i1 %447, label %448, label %435, !llvm.loop !43

448:                                              ; preds = %435, %429
  %449 = phi i64 [ %425, %429 ], [ %444, %435 ]
  %450 = sub nsw i64 %449, %262
  %451 = mul nsw i64 %450, %450
  %452 = lshr i64 %451, 16
  %453 = add nuw nsw i64 %452, %388
  %454 = icmp eq i64 %1, 3
  br i1 %454, label %521, label %455

455:                                              ; preds = %448
  %456 = mul nsw i64 %8, 3
  %457 = getelementptr inbounds i8, ptr %6, i64 %456
  %458 = and i64 %10, 3
  %459 = icmp ult i64 %13, 3
  br i1 %459, label %498, label %460

460:                                              ; preds = %455
  %461 = and i64 %10, 9223372036854775804
  br label %462

462:                                              ; preds = %462, %460
  %463 = phi i64 [ 0, %460 ], [ %493, %462 ]
  %464 = phi i64 [ 0, %460 ], [ %492, %462 ]
  %465 = phi i64 [ 0, %460 ], [ %494, %462 ]
  %466 = getelementptr inbounds nuw i8, ptr %457, i64 %463
  %467 = load i8, ptr %466, align 1, !tbaa !18
  %468 = zext i8 %467 to i64
  %469 = shl nsw i64 %463, 3
  %470 = shl i64 %468, %469
  %471 = or i64 %470, %464
  %472 = or disjoint i64 %463, 1
  %473 = getelementptr inbounds nuw i8, ptr %457, i64 %472
  %474 = load i8, ptr %473, align 1, !tbaa !18
  %475 = zext i8 %474 to i64
  %476 = shl nsw i64 %472, 3
  %477 = shl i64 %475, %476
  %478 = or i64 %477, %471
  %479 = or disjoint i64 %463, 2
  %480 = getelementptr inbounds nuw i8, ptr %457, i64 %479
  %481 = load i8, ptr %480, align 1, !tbaa !18
  %482 = zext i8 %481 to i64
  %483 = shl nsw i64 %479, 3
  %484 = shl i64 %482, %483
  %485 = or i64 %484, %478
  %486 = or disjoint i64 %463, 3
  %487 = getelementptr inbounds nuw i8, ptr %457, i64 %486
  %488 = load i8, ptr %487, align 1, !tbaa !18
  %489 = zext i8 %488 to i64
  %490 = shl nsw i64 %486, 3
  %491 = shl i64 %489, %490
  %492 = or i64 %491, %485
  %493 = add nuw nsw i64 %463, 4
  %494 = add i64 %465, 4
  %495 = icmp eq i64 %494, %461
  br i1 %495, label %496, label %462, !llvm.loop !33

496:                                              ; preds = %462
  %497 = icmp eq i64 %458, 0
  br i1 %497, label %515, label %498

498:                                              ; preds = %496, %455
  %499 = phi i64 [ 0, %455 ], [ %493, %496 ]
  %500 = phi i64 [ 0, %455 ], [ %492, %496 ]
  %501 = icmp ne i64 %458, 0
  tail call void @llvm.assume(i1 %501)
  br label %502

502:                                              ; preds = %502, %498
  %503 = phi i64 [ %512, %502 ], [ %499, %498 ]
  %504 = phi i64 [ %511, %502 ], [ %500, %498 ]
  %505 = phi i64 [ %513, %502 ], [ 0, %498 ]
  %506 = getelementptr inbounds nuw i8, ptr %457, i64 %503
  %507 = load i8, ptr %506, align 1, !tbaa !18
  %508 = zext i8 %507 to i64
  %509 = shl nsw i64 %503, 3
  %510 = shl i64 %508, %509
  %511 = or i64 %510, %504
  %512 = add nuw nsw i64 %503, 1
  %513 = add i64 %505, 1
  %514 = icmp eq i64 %513, %458
  br i1 %514, label %515, label %502, !llvm.loop !43

515:                                              ; preds = %502, %496
  %516 = phi i64 [ %492, %496 ], [ %511, %502 ]
  %517 = sub nsw i64 %516, %262
  %518 = mul nsw i64 %517, %517
  %519 = lshr i64 %518, 16
  %520 = add nuw nsw i64 %519, %453
  br label %521

521:                                              ; preds = %448, %515, %5
  %522 = phi i64 [ 0, %5 ], [ %262, %515 ], [ %262, %448 ]
  %523 = phi i64 [ 0, %5 ], [ %520, %515 ], [ %453, %448 ]
  %524 = udiv i64 %523, %1
  %525 = add nuw nsw i64 %524, 1
  br label %526

526:                                              ; preds = %521, %526
  %527 = phi i64 [ %528, %526 ], [ 0, %521 ]
  %528 = add nuw nsw i64 %527, 1
  %529 = mul nuw nsw i64 %528, %528
  %530 = icmp samesign ugt i64 %529, %525
  br i1 %530, label %531, label %526, !llvm.loop !44

531:                                              ; preds = %526
  %532 = icmp eq i64 %527, 0
  br i1 %532, label %535, label %533

533:                                              ; preds = %531
  %534 = udiv i64 4294967296, %527
  br label %535

535:                                              ; preds = %531, %533
  %536 = phi i64 [ %534, %533 ], [ 0, %531 ]
  %537 = getelementptr inbounds nuw i8, ptr %2, i64 16
  %538 = getelementptr inbounds nuw i8, ptr %2, i64 24
  %539 = getelementptr inbounds nuw i8, ptr %3, i64 16
  %540 = getelementptr inbounds nuw i8, ptr %3, i64 24
  %541 = getelementptr inbounds nuw i8, ptr %4, i64 16
  %542 = getelementptr inbounds nuw i8, ptr %4, i64 24
  br label %544

543:                                              ; preds = %767
  ret void

544:                                              ; preds = %535, %767
  %545 = phi i64 [ 0, %535 ], [ %768, %767 ]
  %546 = load ptr, ptr %0, align 8, !tbaa !9
  %547 = load i64, ptr %7, align 8, !tbaa !15
  %548 = mul nsw i64 %547, %545
  %549 = getelementptr inbounds i8, ptr %546, i64 %548
  %550 = load i64, ptr %9, align 8, !tbaa !16
  %551 = icmp sgt i64 %550, 0
  br i1 %551, label %552, label %610

552:                                              ; preds = %544
  %553 = and i64 %550, 3
  %554 = icmp ult i64 %550, 4
  br i1 %554, label %593, label %555

555:                                              ; preds = %552
  %556 = and i64 %550, 9223372036854775804
  br label %557

557:                                              ; preds = %557, %555
  %558 = phi i64 [ 0, %555 ], [ %588, %557 ]
  %559 = phi i64 [ 0, %555 ], [ %587, %557 ]
  %560 = phi i64 [ 0, %555 ], [ %589, %557 ]
  %561 = getelementptr inbounds nuw i8, ptr %549, i64 %558
  %562 = load i8, ptr %561, align 1, !tbaa !18
  %563 = zext i8 %562 to i64
  %564 = shl nsw i64 %558, 3
  %565 = shl i64 %563, %564
  %566 = or i64 %565, %559
  %567 = or disjoint i64 %558, 1
  %568 = getelementptr inbounds nuw i8, ptr %549, i64 %567
  %569 = load i8, ptr %568, align 1, !tbaa !18
  %570 = zext i8 %569 to i64
  %571 = shl nsw i64 %567, 3
  %572 = shl i64 %570, %571
  %573 = or i64 %572, %566
  %574 = or disjoint i64 %558, 2
  %575 = getelementptr inbounds nuw i8, ptr %549, i64 %574
  %576 = load i8, ptr %575, align 1, !tbaa !18
  %577 = zext i8 %576 to i64
  %578 = shl nsw i64 %574, 3
  %579 = shl i64 %577, %578
  %580 = or i64 %579, %573
  %581 = or disjoint i64 %558, 3
  %582 = getelementptr inbounds nuw i8, ptr %549, i64 %581
  %583 = load i8, ptr %582, align 1, !tbaa !18
  %584 = zext i8 %583 to i64
  %585 = shl nsw i64 %581, 3
  %586 = shl i64 %584, %585
  %587 = or i64 %586, %580
  %588 = add nuw nsw i64 %558, 4
  %589 = add i64 %560, 4
  %590 = icmp eq i64 %589, %556
  br i1 %590, label %591, label %557, !llvm.loop !33

591:                                              ; preds = %557
  %592 = icmp eq i64 %553, 0
  br i1 %592, label %610, label %593

593:                                              ; preds = %591, %552
  %594 = phi i64 [ 0, %552 ], [ %588, %591 ]
  %595 = phi i64 [ 0, %552 ], [ %587, %591 ]
  %596 = icmp ne i64 %553, 0
  tail call void @llvm.assume(i1 %596)
  br label %597

597:                                              ; preds = %597, %593
  %598 = phi i64 [ %607, %597 ], [ %594, %593 ]
  %599 = phi i64 [ %606, %597 ], [ %595, %593 ]
  %600 = phi i64 [ %608, %597 ], [ 0, %593 ]
  %601 = getelementptr inbounds nuw i8, ptr %549, i64 %598
  %602 = load i8, ptr %601, align 1, !tbaa !18
  %603 = zext i8 %602 to i64
  %604 = shl nsw i64 %598, 3
  %605 = shl i64 %603, %604
  %606 = or i64 %605, %599
  %607 = add nuw nsw i64 %598, 1
  %608 = add i64 %600, 1
  %609 = icmp eq i64 %608, %553
  br i1 %609, label %610, label %597, !llvm.loop !45

610:                                              ; preds = %591, %597, %544
  %611 = phi i64 [ 0, %544 ], [ %587, %591 ], [ %606, %597 ]
  %612 = sub nsw i64 %611, %522
  %613 = mul nsw i64 %612, %536
  %614 = ashr i64 %613, 16
  %615 = load ptr, ptr %2, align 8, !tbaa !9
  %616 = load i64, ptr %537, align 8, !tbaa !15
  %617 = mul nsw i64 %616, %545
  %618 = getelementptr inbounds i8, ptr %615, i64 %617
  %619 = load i64, ptr %538, align 8, !tbaa !16
  %620 = icmp sgt i64 %619, 0
  br i1 %620, label %621, label %683

621:                                              ; preds = %610
  %622 = and i64 %619, 3
  %623 = icmp ult i64 %619, 4
  br i1 %623, label %662, label %624

624:                                              ; preds = %621
  %625 = and i64 %619, 9223372036854775804
  br label %626

626:                                              ; preds = %626, %624
  %627 = phi i64 [ 0, %624 ], [ %657, %626 ]
  %628 = phi i64 [ 0, %624 ], [ %656, %626 ]
  %629 = phi i64 [ 0, %624 ], [ %658, %626 ]
  %630 = getelementptr inbounds nuw i8, ptr %618, i64 %627
  %631 = load i8, ptr %630, align 1, !tbaa !18
  %632 = zext i8 %631 to i64
  %633 = shl nsw i64 %627, 3
  %634 = shl i64 %632, %633
  %635 = or i64 %634, %628
  %636 = or disjoint i64 %627, 1
  %637 = getelementptr inbounds nuw i8, ptr %618, i64 %636
  %638 = load i8, ptr %637, align 1, !tbaa !18
  %639 = zext i8 %638 to i64
  %640 = shl nsw i64 %636, 3
  %641 = shl i64 %639, %640
  %642 = or i64 %641, %635
  %643 = or disjoint i64 %627, 2
  %644 = getelementptr inbounds nuw i8, ptr %618, i64 %643
  %645 = load i8, ptr %644, align 1, !tbaa !18
  %646 = zext i8 %645 to i64
  %647 = shl nsw i64 %643, 3
  %648 = shl i64 %646, %647
  %649 = or i64 %648, %642
  %650 = or disjoint i64 %627, 3
  %651 = getelementptr inbounds nuw i8, ptr %618, i64 %650
  %652 = load i8, ptr %651, align 1, !tbaa !18
  %653 = zext i8 %652 to i64
  %654 = shl nsw i64 %650, 3
  %655 = shl i64 %653, %654
  %656 = or i64 %655, %649
  %657 = add nuw nsw i64 %627, 4
  %658 = add i64 %629, 4
  %659 = icmp eq i64 %658, %625
  br i1 %659, label %660, label %626, !llvm.loop !33

660:                                              ; preds = %626
  %661 = icmp eq i64 %622, 0
  br i1 %661, label %679, label %662

662:                                              ; preds = %660, %621
  %663 = phi i64 [ 0, %621 ], [ %657, %660 ]
  %664 = phi i64 [ 0, %621 ], [ %656, %660 ]
  %665 = icmp ne i64 %622, 0
  tail call void @llvm.assume(i1 %665)
  br label %666

666:                                              ; preds = %666, %662
  %667 = phi i64 [ %676, %666 ], [ %663, %662 ]
  %668 = phi i64 [ %675, %666 ], [ %664, %662 ]
  %669 = phi i64 [ %677, %666 ], [ 0, %662 ]
  %670 = getelementptr inbounds nuw i8, ptr %618, i64 %667
  %671 = load i8, ptr %670, align 1, !tbaa !18
  %672 = zext i8 %671 to i64
  %673 = shl nsw i64 %667, 3
  %674 = shl i64 %672, %673
  %675 = or i64 %674, %668
  %676 = add nuw nsw i64 %667, 1
  %677 = add i64 %669, 1
  %678 = icmp eq i64 %677, %622
  br i1 %678, label %679, label %666, !llvm.loop !46

679:                                              ; preds = %666, %660
  %680 = phi i64 [ %656, %660 ], [ %675, %666 ]
  %681 = mul nsw i64 %680, %614
  %682 = ashr i64 %681, 16
  br label %683

683:                                              ; preds = %679, %610
  %684 = phi i64 [ 0, %610 ], [ %682, %679 ]
  %685 = load ptr, ptr %3, align 8, !tbaa !9
  %686 = load i64, ptr %539, align 8, !tbaa !15
  %687 = mul nsw i64 %686, %545
  %688 = getelementptr inbounds i8, ptr %685, i64 %687
  %689 = load i64, ptr %540, align 8, !tbaa !16
  %690 = icmp sgt i64 %689, 0
  br i1 %690, label %691, label %749

691:                                              ; preds = %683
  %692 = and i64 %689, 3
  %693 = icmp ult i64 %689, 4
  br i1 %693, label %732, label %694

694:                                              ; preds = %691
  %695 = and i64 %689, 9223372036854775804
  br label %696

696:                                              ; preds = %696, %694
  %697 = phi i64 [ 0, %694 ], [ %727, %696 ]
  %698 = phi i64 [ 0, %694 ], [ %726, %696 ]
  %699 = phi i64 [ 0, %694 ], [ %728, %696 ]
  %700 = getelementptr inbounds nuw i8, ptr %688, i64 %697
  %701 = load i8, ptr %700, align 1, !tbaa !18
  %702 = zext i8 %701 to i64
  %703 = shl nsw i64 %697, 3
  %704 = shl i64 %702, %703
  %705 = or i64 %704, %698
  %706 = or disjoint i64 %697, 1
  %707 = getelementptr inbounds nuw i8, ptr %688, i64 %706
  %708 = load i8, ptr %707, align 1, !tbaa !18
  %709 = zext i8 %708 to i64
  %710 = shl nsw i64 %706, 3
  %711 = shl i64 %709, %710
  %712 = or i64 %711, %705
  %713 = or disjoint i64 %697, 2
  %714 = getelementptr inbounds nuw i8, ptr %688, i64 %713
  %715 = load i8, ptr %714, align 1, !tbaa !18
  %716 = zext i8 %715 to i64
  %717 = shl nsw i64 %713, 3
  %718 = shl i64 %716, %717
  %719 = or i64 %718, %712
  %720 = or disjoint i64 %697, 3
  %721 = getelementptr inbounds nuw i8, ptr %688, i64 %720
  %722 = load i8, ptr %721, align 1, !tbaa !18
  %723 = zext i8 %722 to i64
  %724 = shl nsw i64 %720, 3
  %725 = shl i64 %723, %724
  %726 = or i64 %725, %719
  %727 = add nuw nsw i64 %697, 4
  %728 = add i64 %699, 4
  %729 = icmp eq i64 %728, %695
  br i1 %729, label %730, label %696, !llvm.loop !33

730:                                              ; preds = %696
  %731 = icmp eq i64 %692, 0
  br i1 %731, label %749, label %732

732:                                              ; preds = %730, %691
  %733 = phi i64 [ 0, %691 ], [ %727, %730 ]
  %734 = phi i64 [ 0, %691 ], [ %726, %730 ]
  %735 = icmp ne i64 %692, 0
  tail call void @llvm.assume(i1 %735)
  br label %736

736:                                              ; preds = %736, %732
  %737 = phi i64 [ %746, %736 ], [ %733, %732 ]
  %738 = phi i64 [ %745, %736 ], [ %734, %732 ]
  %739 = phi i64 [ %747, %736 ], [ 0, %732 ]
  %740 = getelementptr inbounds nuw i8, ptr %688, i64 %737
  %741 = load i8, ptr %740, align 1, !tbaa !18
  %742 = zext i8 %741 to i64
  %743 = shl nsw i64 %737, 3
  %744 = shl i64 %742, %743
  %745 = or i64 %744, %738
  %746 = add nuw nsw i64 %737, 1
  %747 = add i64 %739, 1
  %748 = icmp eq i64 %747, %692
  br i1 %748, label %749, label %736, !llvm.loop !47

749:                                              ; preds = %730, %736, %683
  %750 = phi i64 [ 0, %683 ], [ %726, %730 ], [ %745, %736 ]
  %751 = add nsw i64 %750, %684
  %752 = load ptr, ptr %4, align 8, !tbaa !9
  %753 = load i64, ptr %541, align 8, !tbaa !15
  %754 = mul nsw i64 %753, %545
  %755 = getelementptr inbounds i8, ptr %752, i64 %754
  %756 = load i64, ptr %542, align 8, !tbaa !16
  %757 = icmp sgt i64 %756, 0
  br i1 %757, label %758, label %767

758:                                              ; preds = %749, %758
  %759 = phi i64 [ %764, %758 ], [ 0, %749 ]
  %760 = shl nsw i64 %759, 3
  %761 = ashr i64 %751, %760
  %762 = trunc i64 %761 to i8
  %763 = getelementptr inbounds nuw i8, ptr %755, i64 %759
  store i8 %762, ptr %763, align 1, !tbaa !18
  %764 = add nuw nsw i64 %759, 1
  %765 = load i64, ptr %542, align 8, !tbaa !16
  %766 = icmp slt i64 %764, %765
  br i1 %766, label %758, label %767, !llvm.loop !41

767:                                              ; preds = %758, %749
  %768 = add nuw nsw i64 %545, 1
  %769 = icmp eq i64 %768, %1
  br i1 %769, label %543, label %544, !llvm.loop !48
}

; Function Attrs: nofree norecurse nosync nounwind sspstrong memory(readwrite, inaccessiblemem: none, target_mem: none) uwtable
define internal fastcc void @topk(ptr nofree noundef nonnull readonly captures(none) %0, i64 noundef range(i64 3, 6) %1, ptr nofree noundef nonnull readonly captures(none) %2, ptr nofree noundef nonnull readonly captures(none) %3, ptr nofree noundef nonnull readonly captures(none) %4) unnamed_addr #4 {
  %6 = alloca i64, align 16
  %7 = alloca i64, align 8
  %8 = alloca i64, align 16
  %9 = alloca i64, align 16
  %10 = alloca i64, align 8
  %11 = alloca i64, align 16
  call void @llvm.lifetime.start.p0(ptr nonnull %6)
  call void @llvm.lifetime.start.p0(ptr nonnull %7)
  call void @llvm.lifetime.start.p0(ptr nonnull %8)
  call void @llvm.lifetime.start.p0(ptr nonnull %9)
  call void @llvm.lifetime.start.p0(ptr nonnull %10)
  call void @llvm.lifetime.start.p0(ptr nonnull %11)
  store i64 -1, ptr %6, align 16, !tbaa !17
  store i64 -1, ptr %7, align 8, !tbaa !17
  store i64 -1, ptr %8, align 16, !tbaa !17
  store i64 -999999999, ptr %9, align 16, !tbaa !17
  store i64 -999999999, ptr %10, align 8, !tbaa !17
  store i64 -999999999, ptr %11, align 16, !tbaa !17
  %12 = load ptr, ptr %0, align 8, !tbaa !9
  %13 = getelementptr inbounds nuw i8, ptr %0, i64 16
  %14 = load i64, ptr %13, align 8, !tbaa !15
  %15 = getelementptr inbounds nuw i8, ptr %0, i64 24
  %16 = load i64, ptr %15, align 8, !tbaa !16
  %17 = icmp sgt i64 %16, 0
  %18 = getelementptr inbounds nuw i8, ptr %2, i64 16
  %19 = getelementptr inbounds nuw i8, ptr %2, i64 24
  br i1 %17, label %20, label %180

20:                                               ; preds = %5
  %21 = and i64 %16, 3
  %22 = icmp ult i64 %16, 4
  %23 = and i64 %16, 9223372036854775804
  %24 = icmp eq i64 %21, 0
  %25 = icmp ne i64 %21, 0
  br label %26

26:                                               ; preds = %20, %139
  %27 = phi i64 [ %140, %139 ], [ 0, %20 ]
  %28 = mul nsw i64 %14, %27
  %29 = getelementptr inbounds i8, ptr %12, i64 %28
  br i1 %22, label %151, label %30

30:                                               ; preds = %26, %30
  %31 = phi i64 [ %61, %30 ], [ 0, %26 ]
  %32 = phi i64 [ %60, %30 ], [ 0, %26 ]
  %33 = phi i64 [ %62, %30 ], [ 0, %26 ]
  %34 = getelementptr inbounds nuw i8, ptr %29, i64 %31
  %35 = load i8, ptr %34, align 1, !tbaa !18
  %36 = zext i8 %35 to i64
  %37 = shl nsw i64 %31, 3
  %38 = shl i64 %36, %37
  %39 = or i64 %38, %32
  %40 = or disjoint i64 %31, 1
  %41 = getelementptr inbounds nuw i8, ptr %29, i64 %40
  %42 = load i8, ptr %41, align 1, !tbaa !18
  %43 = zext i8 %42 to i64
  %44 = shl nsw i64 %40, 3
  %45 = shl i64 %43, %44
  %46 = or i64 %45, %39
  %47 = or disjoint i64 %31, 2
  %48 = getelementptr inbounds nuw i8, ptr %29, i64 %47
  %49 = load i8, ptr %48, align 1, !tbaa !18
  %50 = zext i8 %49 to i64
  %51 = shl nsw i64 %47, 3
  %52 = shl i64 %50, %51
  %53 = or i64 %52, %46
  %54 = or disjoint i64 %31, 3
  %55 = getelementptr inbounds nuw i8, ptr %29, i64 %54
  %56 = load i8, ptr %55, align 1, !tbaa !18
  %57 = zext i8 %56 to i64
  %58 = shl nsw i64 %54, 3
  %59 = shl i64 %57, %58
  %60 = or i64 %59, %53
  %61 = add nuw nsw i64 %31, 4
  %62 = add i64 %33, 4
  %63 = icmp eq i64 %62, %23
  br i1 %63, label %150, label %30, !llvm.loop !33

64:                                               ; preds = %167
  %65 = load i64, ptr %10, align 8, !tbaa !17
  %66 = icmp sgt i64 %168, %65
  br i1 %66, label %145, label %67

67:                                               ; preds = %64
  %68 = load i64, ptr %11, align 16, !tbaa !17
  %69 = icmp sgt i64 %168, %68
  br i1 %69, label %70, label %139

70:                                               ; preds = %145, %142, %67
  %71 = phi ptr [ %8, %67 ], [ %147, %142 ], [ %147, %145 ]
  %72 = phi ptr [ %11, %67 ], [ %146, %142 ], [ %146, %145 ]
  store i64 %168, ptr %72, align 8, !tbaa !17
  %73 = load ptr, ptr %2, align 8, !tbaa !9
  %74 = load i64, ptr %18, align 8, !tbaa !15
  %75 = mul nsw i64 %74, %27
  %76 = getelementptr inbounds i8, ptr %73, i64 %75
  %77 = load i64, ptr %19, align 8, !tbaa !16
  %78 = icmp sgt i64 %77, 0
  br i1 %78, label %79, label %137

79:                                               ; preds = %70
  %80 = and i64 %77, 3
  %81 = icmp ult i64 %77, 4
  br i1 %81, label %120, label %82

82:                                               ; preds = %79
  %83 = and i64 %77, 9223372036854775804
  br label %84

84:                                               ; preds = %84, %82
  %85 = phi i64 [ 0, %82 ], [ %115, %84 ]
  %86 = phi i64 [ 0, %82 ], [ %114, %84 ]
  %87 = phi i64 [ 0, %82 ], [ %116, %84 ]
  %88 = getelementptr inbounds nuw i8, ptr %76, i64 %85
  %89 = load i8, ptr %88, align 1, !tbaa !18
  %90 = zext i8 %89 to i64
  %91 = shl nsw i64 %85, 3
  %92 = shl i64 %90, %91
  %93 = or i64 %92, %86
  %94 = or disjoint i64 %85, 1
  %95 = getelementptr inbounds nuw i8, ptr %76, i64 %94
  %96 = load i8, ptr %95, align 1, !tbaa !18
  %97 = zext i8 %96 to i64
  %98 = shl nsw i64 %94, 3
  %99 = shl i64 %97, %98
  %100 = or i64 %99, %93
  %101 = or disjoint i64 %85, 2
  %102 = getelementptr inbounds nuw i8, ptr %76, i64 %101
  %103 = load i8, ptr %102, align 1, !tbaa !18
  %104 = zext i8 %103 to i64
  %105 = shl nsw i64 %101, 3
  %106 = shl i64 %104, %105
  %107 = or i64 %106, %100
  %108 = or disjoint i64 %85, 3
  %109 = getelementptr inbounds nuw i8, ptr %76, i64 %108
  %110 = load i8, ptr %109, align 1, !tbaa !18
  %111 = zext i8 %110 to i64
  %112 = shl nsw i64 %108, 3
  %113 = shl i64 %111, %112
  %114 = or i64 %113, %107
  %115 = add nuw nsw i64 %85, 4
  %116 = add i64 %87, 4
  %117 = icmp eq i64 %116, %83
  br i1 %117, label %118, label %84, !llvm.loop !33

118:                                              ; preds = %84
  %119 = icmp eq i64 %80, 0
  br i1 %119, label %137, label %120

120:                                              ; preds = %118, %79
  %121 = phi i64 [ 0, %79 ], [ %115, %118 ]
  %122 = phi i64 [ 0, %79 ], [ %114, %118 ]
  %123 = icmp ne i64 %80, 0
  tail call void @llvm.assume(i1 %123)
  br label %124

124:                                              ; preds = %124, %120
  %125 = phi i64 [ %134, %124 ], [ %121, %120 ]
  %126 = phi i64 [ %133, %124 ], [ %122, %120 ]
  %127 = phi i64 [ %135, %124 ], [ 0, %120 ]
  %128 = getelementptr inbounds nuw i8, ptr %76, i64 %125
  %129 = load i8, ptr %128, align 1, !tbaa !18
  %130 = zext i8 %129 to i64
  %131 = shl nsw i64 %125, 3
  %132 = shl i64 %130, %131
  %133 = or i64 %132, %126
  %134 = add nuw nsw i64 %125, 1
  %135 = add i64 %127, 1
  %136 = icmp eq i64 %135, %80
  br i1 %136, label %137, label %124, !llvm.loop !49

137:                                              ; preds = %118, %124, %70
  %138 = phi i64 [ 0, %70 ], [ %114, %118 ], [ %133, %124 ]
  store i64 %138, ptr %71, align 8, !tbaa !17
  br label %139

139:                                              ; preds = %67, %137
  %140 = add nuw nsw i64 %27, 1
  %141 = icmp eq i64 %140, %1
  br i1 %141, label %171, label %26, !llvm.loop !50

142:                                              ; preds = %145
  %143 = load i64, ptr %9, align 16, !tbaa !17
  store i64 %143, ptr %10, align 8, !tbaa !17
  %144 = load i64, ptr %6, align 16, !tbaa !17
  store i64 %144, ptr %7, align 8, !tbaa !17
  br label %70

145:                                              ; preds = %167, %64
  %146 = phi ptr [ %10, %64 ], [ %9, %167 ]
  %147 = phi ptr [ %7, %64 ], [ %6, %167 ]
  %148 = load i64, ptr %10, align 8, !tbaa !17
  store i64 %148, ptr %11, align 16, !tbaa !17
  %149 = load i64, ptr %7, align 8, !tbaa !17
  store i64 %149, ptr %8, align 16, !tbaa !17
  br i1 %170, label %142, label %70

150:                                              ; preds = %30
  br i1 %24, label %167, label %151

151:                                              ; preds = %150, %26
  %152 = phi i64 [ 0, %26 ], [ %61, %150 ]
  %153 = phi i64 [ 0, %26 ], [ %60, %150 ]
  tail call void @llvm.assume(i1 %25)
  br label %154

154:                                              ; preds = %154, %151
  %155 = phi i64 [ %164, %154 ], [ %152, %151 ]
  %156 = phi i64 [ %163, %154 ], [ %153, %151 ]
  %157 = phi i64 [ %165, %154 ], [ 0, %151 ]
  %158 = getelementptr inbounds nuw i8, ptr %29, i64 %155
  %159 = load i8, ptr %158, align 1, !tbaa !18
  %160 = zext i8 %159 to i64
  %161 = shl nsw i64 %155, 3
  %162 = shl i64 %160, %161
  %163 = or i64 %162, %156
  %164 = add nuw nsw i64 %155, 1
  %165 = add i64 %157, 1
  %166 = icmp eq i64 %165, %21
  br i1 %166, label %167, label %154, !llvm.loop !51

167:                                              ; preds = %154, %150
  %168 = phi i64 [ %60, %150 ], [ %163, %154 ]
  %169 = load i64, ptr %9, align 16, !tbaa !17
  %170 = icmp sgt i64 %168, %169
  br i1 %170, label %145, label %64

171:                                              ; preds = %268, %139
  %172 = getelementptr inbounds nuw i8, ptr %3, i64 16
  %173 = getelementptr inbounds nuw i8, ptr %3, i64 24
  %174 = getelementptr inbounds nuw i8, ptr %4, i64 16
  %175 = getelementptr inbounds nuw i8, ptr %4, i64 24
  %176 = load i64, ptr %6, align 16, !tbaa !17
  %177 = load ptr, ptr %3, align 8, !tbaa !9
  %178 = load i64, ptr %173, align 8, !tbaa !16
  %179 = icmp sgt i64 %178, 0
  br i1 %179, label %272, label %281

180:                                              ; preds = %5, %268
  %181 = phi i64 [ %269, %268 ], [ -999999999, %5 ]
  %182 = phi i64 [ %270, %268 ], [ 0, %5 ]
  %183 = icmp slt i64 %181, 0
  br i1 %183, label %260, label %184

184:                                              ; preds = %180
  %185 = load i64, ptr %10, align 8, !tbaa !17
  %186 = icmp slt i64 %185, 0
  br i1 %186, label %260, label %187

187:                                              ; preds = %184
  %188 = load i64, ptr %11, align 16, !tbaa !17
  %189 = icmp slt i64 %188, 0
  br i1 %189, label %190, label %268

190:                                              ; preds = %260, %265, %187
  %191 = phi ptr [ %8, %187 ], [ %262, %265 ], [ %262, %260 ]
  %192 = phi ptr [ %11, %187 ], [ %261, %265 ], [ %261, %260 ]
  store i64 0, ptr %192, align 8, !tbaa !17
  %193 = load ptr, ptr %2, align 8, !tbaa !9
  %194 = load i64, ptr %18, align 8, !tbaa !15
  %195 = mul nsw i64 %194, %182
  %196 = getelementptr inbounds i8, ptr %193, i64 %195
  %197 = load i64, ptr %19, align 8, !tbaa !16
  %198 = icmp sgt i64 %197, 0
  %199 = load i64, ptr %9, align 16, !tbaa !17
  br i1 %198, label %200, label %258

200:                                              ; preds = %190
  %201 = and i64 %197, 3
  %202 = icmp ult i64 %197, 4
  br i1 %202, label %241, label %203

203:                                              ; preds = %200
  %204 = and i64 %197, 9223372036854775804
  br label %205

205:                                              ; preds = %205, %203
  %206 = phi i64 [ 0, %203 ], [ %236, %205 ]
  %207 = phi i64 [ 0, %203 ], [ %235, %205 ]
  %208 = phi i64 [ 0, %203 ], [ %237, %205 ]
  %209 = getelementptr inbounds nuw i8, ptr %196, i64 %206
  %210 = load i8, ptr %209, align 1, !tbaa !18
  %211 = zext i8 %210 to i64
  %212 = shl nsw i64 %206, 3
  %213 = shl i64 %211, %212
  %214 = or i64 %213, %207
  %215 = or disjoint i64 %206, 1
  %216 = getelementptr inbounds nuw i8, ptr %196, i64 %215
  %217 = load i8, ptr %216, align 1, !tbaa !18
  %218 = zext i8 %217 to i64
  %219 = shl nsw i64 %215, 3
  %220 = shl i64 %218, %219
  %221 = or i64 %220, %214
  %222 = or disjoint i64 %206, 2
  %223 = getelementptr inbounds nuw i8, ptr %196, i64 %222
  %224 = load i8, ptr %223, align 1, !tbaa !18
  %225 = zext i8 %224 to i64
  %226 = shl nsw i64 %222, 3
  %227 = shl i64 %225, %226
  %228 = or i64 %227, %221
  %229 = or disjoint i64 %206, 3
  %230 = getelementptr inbounds nuw i8, ptr %196, i64 %229
  %231 = load i8, ptr %230, align 1, !tbaa !18
  %232 = zext i8 %231 to i64
  %233 = shl nsw i64 %229, 3
  %234 = shl i64 %232, %233
  %235 = or i64 %234, %228
  %236 = add nuw nsw i64 %206, 4
  %237 = add i64 %208, 4
  %238 = icmp eq i64 %237, %204
  br i1 %238, label %239, label %205, !llvm.loop !33

239:                                              ; preds = %205
  %240 = icmp eq i64 %201, 0
  br i1 %240, label %258, label %241

241:                                              ; preds = %239, %200
  %242 = phi i64 [ 0, %200 ], [ %236, %239 ]
  %243 = phi i64 [ 0, %200 ], [ %235, %239 ]
  %244 = icmp ne i64 %201, 0
  tail call void @llvm.assume(i1 %244)
  br label %245

245:                                              ; preds = %245, %241
  %246 = phi i64 [ %255, %245 ], [ %242, %241 ]
  %247 = phi i64 [ %254, %245 ], [ %243, %241 ]
  %248 = phi i64 [ %256, %245 ], [ 0, %241 ]
  %249 = getelementptr inbounds nuw i8, ptr %196, i64 %246
  %250 = load i8, ptr %249, align 1, !tbaa !18
  %251 = zext i8 %250 to i64
  %252 = shl nsw i64 %246, 3
  %253 = shl i64 %251, %252
  %254 = or i64 %253, %247
  %255 = add nuw nsw i64 %246, 1
  %256 = add i64 %248, 1
  %257 = icmp eq i64 %256, %201
  br i1 %257, label %258, label %245, !llvm.loop !52

258:                                              ; preds = %239, %245, %190
  %259 = phi i64 [ 0, %190 ], [ %235, %239 ], [ %254, %245 ]
  store i64 %259, ptr %191, align 8, !tbaa !17
  br label %268

260:                                              ; preds = %184, %180
  %261 = phi ptr [ %10, %184 ], [ %9, %180 ]
  %262 = phi ptr [ %7, %184 ], [ %6, %180 ]
  %263 = load i64, ptr %10, align 8, !tbaa !17
  store i64 %263, ptr %11, align 16, !tbaa !17
  %264 = load i64, ptr %7, align 8, !tbaa !17
  store i64 %264, ptr %8, align 16, !tbaa !17
  br i1 %183, label %265, label %190

265:                                              ; preds = %260
  %266 = load i64, ptr %9, align 16, !tbaa !17
  store i64 %266, ptr %10, align 8, !tbaa !17
  %267 = load i64, ptr %6, align 16, !tbaa !17
  store i64 %267, ptr %7, align 8, !tbaa !17
  br label %190

268:                                              ; preds = %187, %258
  %269 = phi i64 [ %199, %258 ], [ %181, %187 ]
  %270 = add nuw nsw i64 %182, 1
  %271 = icmp eq i64 %270, %1
  br i1 %271, label %171, label %180, !llvm.loop !50

272:                                              ; preds = %171, %272
  %273 = phi i64 [ %278, %272 ], [ 0, %171 ]
  %274 = shl nsw i64 %273, 3
  %275 = ashr i64 %176, %274
  %276 = trunc i64 %275 to i8
  %277 = getelementptr inbounds nuw i8, ptr %177, i64 %273
  store i8 %276, ptr %277, align 1, !tbaa !18
  %278 = add nuw nsw i64 %273, 1
  %279 = load i64, ptr %173, align 8, !tbaa !16
  %280 = icmp slt i64 %278, %279
  br i1 %280, label %272, label %281, !llvm.loop !41

281:                                              ; preds = %272, %171
  %282 = phi i64 [ %178, %171 ], [ %279, %272 ]
  %283 = load i64, ptr %9, align 16, !tbaa !17
  %284 = load ptr, ptr %4, align 8, !tbaa !9
  %285 = load i64, ptr %175, align 8, !tbaa !16
  %286 = icmp sgt i64 %285, 0
  br i1 %286, label %287, label %298

287:                                              ; preds = %281, %287
  %288 = phi i64 [ %293, %287 ], [ 0, %281 ]
  %289 = shl nsw i64 %288, 3
  %290 = ashr i64 %283, %289
  %291 = trunc i64 %290 to i8
  %292 = getelementptr inbounds nuw i8, ptr %284, i64 %288
  store i8 %291, ptr %292, align 1, !tbaa !18
  %293 = add nuw nsw i64 %288, 1
  %294 = load i64, ptr %175, align 8, !tbaa !16
  %295 = icmp slt i64 %293, %294
  br i1 %295, label %287, label %296, !llvm.loop !41

296:                                              ; preds = %287
  %297 = load i64, ptr %173, align 8, !tbaa !16
  br label %298

298:                                              ; preds = %296, %281
  %299 = phi i64 [ %294, %296 ], [ %285, %281 ]
  %300 = phi i64 [ %297, %296 ], [ %282, %281 ]
  %301 = load i64, ptr %7, align 8, !tbaa !17
  %302 = load ptr, ptr %3, align 8, !tbaa !9
  %303 = load i64, ptr %172, align 8, !tbaa !15
  %304 = getelementptr inbounds i8, ptr %302, i64 %303
  %305 = icmp sgt i64 %300, 0
  br i1 %305, label %306, label %317

306:                                              ; preds = %298, %306
  %307 = phi i64 [ %312, %306 ], [ 0, %298 ]
  %308 = shl nsw i64 %307, 3
  %309 = ashr i64 %301, %308
  %310 = trunc i64 %309 to i8
  %311 = getelementptr inbounds nuw i8, ptr %304, i64 %307
  store i8 %310, ptr %311, align 1, !tbaa !18
  %312 = add nuw nsw i64 %307, 1
  %313 = load i64, ptr %173, align 8, !tbaa !16
  %314 = icmp slt i64 %312, %313
  br i1 %314, label %306, label %315, !llvm.loop !41

315:                                              ; preds = %306
  %316 = load i64, ptr %175, align 8, !tbaa !16
  br label %317

317:                                              ; preds = %315, %298
  %318 = phi i64 [ %313, %315 ], [ %300, %298 ]
  %319 = phi i64 [ %316, %315 ], [ %299, %298 ]
  %320 = load i64, ptr %10, align 8, !tbaa !17
  %321 = load ptr, ptr %4, align 8, !tbaa !9
  %322 = load i64, ptr %174, align 8, !tbaa !15
  %323 = getelementptr inbounds i8, ptr %321, i64 %322
  %324 = icmp sgt i64 %319, 0
  br i1 %324, label %325, label %336

325:                                              ; preds = %317, %325
  %326 = phi i64 [ %331, %325 ], [ 0, %317 ]
  %327 = shl nsw i64 %326, 3
  %328 = ashr i64 %320, %327
  %329 = trunc i64 %328 to i8
  %330 = getelementptr inbounds nuw i8, ptr %323, i64 %326
  store i8 %329, ptr %330, align 1, !tbaa !18
  %331 = add nuw nsw i64 %326, 1
  %332 = load i64, ptr %175, align 8, !tbaa !16
  %333 = icmp slt i64 %331, %332
  br i1 %333, label %325, label %334, !llvm.loop !41

334:                                              ; preds = %325
  %335 = load i64, ptr %173, align 8, !tbaa !16
  br label %336

336:                                              ; preds = %334, %317
  %337 = phi i64 [ %332, %334 ], [ %319, %317 ]
  %338 = phi i64 [ %335, %334 ], [ %318, %317 ]
  %339 = load i64, ptr %8, align 16, !tbaa !17
  %340 = load ptr, ptr %3, align 8, !tbaa !9
  %341 = load i64, ptr %172, align 8, !tbaa !15
  %342 = shl nsw i64 %341, 1
  %343 = getelementptr inbounds i8, ptr %340, i64 %342
  %344 = icmp sgt i64 %338, 0
  br i1 %344, label %345, label %356

345:                                              ; preds = %336, %345
  %346 = phi i64 [ %351, %345 ], [ 0, %336 ]
  %347 = shl nsw i64 %346, 3
  %348 = ashr i64 %339, %347
  %349 = trunc i64 %348 to i8
  %350 = getelementptr inbounds nuw i8, ptr %343, i64 %346
  store i8 %349, ptr %350, align 1, !tbaa !18
  %351 = add nuw nsw i64 %346, 1
  %352 = load i64, ptr %173, align 8, !tbaa !16
  %353 = icmp slt i64 %351, %352
  br i1 %353, label %345, label %354, !llvm.loop !41

354:                                              ; preds = %345
  %355 = load i64, ptr %175, align 8, !tbaa !16
  br label %356

356:                                              ; preds = %354, %336
  %357 = phi i64 [ %355, %354 ], [ %337, %336 ]
  %358 = load i64, ptr %11, align 16, !tbaa !17
  %359 = load ptr, ptr %4, align 8, !tbaa !9
  %360 = load i64, ptr %174, align 8, !tbaa !15
  %361 = shl nsw i64 %360, 1
  %362 = getelementptr inbounds i8, ptr %359, i64 %361
  %363 = icmp sgt i64 %357, 0
  br i1 %363, label %364, label %373

364:                                              ; preds = %356, %364
  %365 = phi i64 [ %370, %364 ], [ 0, %356 ]
  %366 = shl nsw i64 %365, 3
  %367 = ashr i64 %358, %366
  %368 = trunc i64 %367 to i8
  %369 = getelementptr inbounds nuw i8, ptr %362, i64 %365
  store i8 %368, ptr %369, align 1, !tbaa !18
  %370 = add nuw nsw i64 %365, 1
  %371 = load i64, ptr %175, align 8, !tbaa !16
  %372 = icmp slt i64 %370, %371
  br i1 %372, label %364, label %373, !llvm.loop !41

373:                                              ; preds = %364, %356
  call void @llvm.lifetime.end.p0(ptr nonnull %9)
  call void @llvm.lifetime.end.p0(ptr nonnull %10)
  call void @llvm.lifetime.end.p0(ptr nonnull %11)
  call void @llvm.lifetime.end.p0(ptr nonnull %6)
  call void @llvm.lifetime.end.p0(ptr nonnull %7)
  call void @llvm.lifetime.end.p0(ptr nonnull %8)
  ret void
}

; Function Attrs: nofree norecurse nosync nounwind sspstrong memory(readwrite, inaccessiblemem: none, target_mem: none) uwtable
define internal fastcc void @build_index(ptr nofree noundef nonnull readonly captures(none) %0, ptr nofree noundef nonnull readonly captures(none) %1, ptr nofree noundef nonnull readonly captures(none) %2) unnamed_addr #4 {
  %4 = getelementptr inbounds nuw i8, ptr %1, i64 16
  %5 = getelementptr inbounds nuw i8, ptr %1, i64 24
  %6 = load i64, ptr %5, align 8, !tbaa !16
  %7 = icmp sgt i64 %6, 0
  br i1 %7, label %22, label %8

8:                                                ; preds = %107, %30, %41, %53, %65, %77, %89, %101, %3
  %9 = phi i64 [ %6, %3 ], [ %28, %30 ], [ %99, %101 ], [ %87, %89 ], [ %75, %77 ], [ %63, %65 ], [ %51, %53 ], [ %39, %41 ], [ %111, %107 ]
  %10 = getelementptr inbounds nuw i8, ptr %0, i64 16
  %11 = getelementptr inbounds nuw i8, ptr %0, i64 24
  %12 = getelementptr inbounds nuw i8, ptr %2, i64 16
  %13 = getelementptr inbounds nuw i8, ptr %2, i64 24
  %14 = load ptr, ptr %0, align 8, !tbaa !9
  %15 = load i64, ptr %11, align 8, !tbaa !16
  %16 = icmp sgt i64 %15, 0
  br i1 %16, label %17, label %169

17:                                               ; preds = %8
  %18 = and i64 %15, 3
  %19 = icmp ult i64 %15, 4
  br i1 %19, label %149, label %20

20:                                               ; preds = %17
  %21 = and i64 %15, 9223372036854775804
  br label %113

22:                                               ; preds = %3
  %23 = load ptr, ptr %1, align 8, !tbaa !9
  br label %24

24:                                               ; preds = %22, %24
  %25 = phi i64 [ %27, %24 ], [ 0, %22 ]
  %26 = getelementptr inbounds nuw i8, ptr %23, i64 %25
  store i8 -1, ptr %26, align 1, !tbaa !18
  %27 = add nuw nsw i64 %25, 1
  %28 = load i64, ptr %5, align 8, !tbaa !16
  %29 = icmp slt i64 %27, %28
  br i1 %29, label %24, label %30, !llvm.loop !41

30:                                               ; preds = %24
  %31 = load ptr, ptr %1, align 8, !tbaa !9
  %32 = load i64, ptr %4, align 8, !tbaa !15
  %33 = getelementptr inbounds i8, ptr %31, i64 %32
  %34 = icmp sgt i64 %28, 0
  br i1 %34, label %35, label %8

35:                                               ; preds = %30, %35
  %36 = phi i64 [ %38, %35 ], [ 0, %30 ]
  %37 = getelementptr inbounds nuw i8, ptr %33, i64 %36
  store i8 -1, ptr %37, align 1, !tbaa !18
  %38 = add nuw nsw i64 %36, 1
  %39 = load i64, ptr %5, align 8, !tbaa !16
  %40 = icmp slt i64 %38, %39
  br i1 %40, label %35, label %41, !llvm.loop !41

41:                                               ; preds = %35
  %42 = load ptr, ptr %1, align 8, !tbaa !9
  %43 = load i64, ptr %4, align 8, !tbaa !15
  %44 = shl nsw i64 %43, 1
  %45 = getelementptr inbounds i8, ptr %42, i64 %44
  %46 = icmp sgt i64 %39, 0
  br i1 %46, label %47, label %8

47:                                               ; preds = %41, %47
  %48 = phi i64 [ %50, %47 ], [ 0, %41 ]
  %49 = getelementptr inbounds nuw i8, ptr %45, i64 %48
  store i8 -1, ptr %49, align 1, !tbaa !18
  %50 = add nuw nsw i64 %48, 1
  %51 = load i64, ptr %5, align 8, !tbaa !16
  %52 = icmp slt i64 %50, %51
  br i1 %52, label %47, label %53, !llvm.loop !41

53:                                               ; preds = %47
  %54 = load ptr, ptr %1, align 8, !tbaa !9
  %55 = load i64, ptr %4, align 8, !tbaa !15
  %56 = mul nsw i64 %55, 3
  %57 = getelementptr inbounds i8, ptr %54, i64 %56
  %58 = icmp sgt i64 %51, 0
  br i1 %58, label %59, label %8

59:                                               ; preds = %53, %59
  %60 = phi i64 [ %62, %59 ], [ 0, %53 ]
  %61 = getelementptr inbounds nuw i8, ptr %57, i64 %60
  store i8 -1, ptr %61, align 1, !tbaa !18
  %62 = add nuw nsw i64 %60, 1
  %63 = load i64, ptr %5, align 8, !tbaa !16
  %64 = icmp slt i64 %62, %63
  br i1 %64, label %59, label %65, !llvm.loop !41

65:                                               ; preds = %59
  %66 = load ptr, ptr %1, align 8, !tbaa !9
  %67 = load i64, ptr %4, align 8, !tbaa !15
  %68 = shl nsw i64 %67, 2
  %69 = getelementptr inbounds i8, ptr %66, i64 %68
  %70 = icmp sgt i64 %63, 0
  br i1 %70, label %71, label %8

71:                                               ; preds = %65, %71
  %72 = phi i64 [ %74, %71 ], [ 0, %65 ]
  %73 = getelementptr inbounds nuw i8, ptr %69, i64 %72
  store i8 -1, ptr %73, align 1, !tbaa !18
  %74 = add nuw nsw i64 %72, 1
  %75 = load i64, ptr %5, align 8, !tbaa !16
  %76 = icmp slt i64 %74, %75
  br i1 %76, label %71, label %77, !llvm.loop !41

77:                                               ; preds = %71
  %78 = load ptr, ptr %1, align 8, !tbaa !9
  %79 = load i64, ptr %4, align 8, !tbaa !15
  %80 = mul nsw i64 %79, 5
  %81 = getelementptr inbounds i8, ptr %78, i64 %80
  %82 = icmp sgt i64 %75, 0
  br i1 %82, label %83, label %8

83:                                               ; preds = %77, %83
  %84 = phi i64 [ %86, %83 ], [ 0, %77 ]
  %85 = getelementptr inbounds nuw i8, ptr %81, i64 %84
  store i8 -1, ptr %85, align 1, !tbaa !18
  %86 = add nuw nsw i64 %84, 1
  %87 = load i64, ptr %5, align 8, !tbaa !16
  %88 = icmp slt i64 %86, %87
  br i1 %88, label %83, label %89, !llvm.loop !41

89:                                               ; preds = %83
  %90 = load ptr, ptr %1, align 8, !tbaa !9
  %91 = load i64, ptr %4, align 8, !tbaa !15
  %92 = mul nsw i64 %91, 6
  %93 = getelementptr inbounds i8, ptr %90, i64 %92
  %94 = icmp sgt i64 %87, 0
  br i1 %94, label %95, label %8

95:                                               ; preds = %89, %95
  %96 = phi i64 [ %98, %95 ], [ 0, %89 ]
  %97 = getelementptr inbounds nuw i8, ptr %93, i64 %96
  store i8 -1, ptr %97, align 1, !tbaa !18
  %98 = add nuw nsw i64 %96, 1
  %99 = load i64, ptr %5, align 8, !tbaa !16
  %100 = icmp slt i64 %98, %99
  br i1 %100, label %95, label %101, !llvm.loop !41

101:                                              ; preds = %95
  %102 = load ptr, ptr %1, align 8, !tbaa !9
  %103 = load i64, ptr %4, align 8, !tbaa !15
  %104 = mul nsw i64 %103, 7
  %105 = getelementptr inbounds i8, ptr %102, i64 %104
  %106 = icmp sgt i64 %99, 0
  br i1 %106, label %107, label %8

107:                                              ; preds = %101, %107
  %108 = phi i64 [ %110, %107 ], [ 0, %101 ]
  %109 = getelementptr inbounds nuw i8, ptr %105, i64 %108
  store i8 -1, ptr %109, align 1, !tbaa !18
  %110 = add nuw nsw i64 %108, 1
  %111 = load i64, ptr %5, align 8, !tbaa !16
  %112 = icmp slt i64 %110, %111
  br i1 %112, label %107, label %8, !llvm.loop !41

113:                                              ; preds = %113, %20
  %114 = phi i64 [ 0, %20 ], [ %144, %113 ]
  %115 = phi i64 [ 0, %20 ], [ %143, %113 ]
  %116 = phi i64 [ 0, %20 ], [ %145, %113 ]
  %117 = getelementptr inbounds nuw i8, ptr %14, i64 %114
  %118 = load i8, ptr %117, align 1, !tbaa !18
  %119 = zext i8 %118 to i64
  %120 = shl nsw i64 %114, 3
  %121 = shl i64 %119, %120
  %122 = or i64 %121, %115
  %123 = or disjoint i64 %114, 1
  %124 = getelementptr inbounds nuw i8, ptr %14, i64 %123
  %125 = load i8, ptr %124, align 1, !tbaa !18
  %126 = zext i8 %125 to i64
  %127 = shl nsw i64 %123, 3
  %128 = shl i64 %126, %127
  %129 = or i64 %128, %122
  %130 = or disjoint i64 %114, 2
  %131 = getelementptr inbounds nuw i8, ptr %14, i64 %130
  %132 = load i8, ptr %131, align 1, !tbaa !18
  %133 = zext i8 %132 to i64
  %134 = shl nsw i64 %130, 3
  %135 = shl i64 %133, %134
  %136 = or i64 %135, %129
  %137 = or disjoint i64 %114, 3
  %138 = getelementptr inbounds nuw i8, ptr %14, i64 %137
  %139 = load i8, ptr %138, align 1, !tbaa !18
  %140 = zext i8 %139 to i64
  %141 = shl nsw i64 %137, 3
  %142 = shl i64 %140, %141
  %143 = or i64 %142, %136
  %144 = add nuw nsw i64 %114, 4
  %145 = add i64 %116, 4
  %146 = icmp eq i64 %145, %21
  br i1 %146, label %147, label %113, !llvm.loop !33

147:                                              ; preds = %113
  %148 = icmp eq i64 %18, 0
  br i1 %148, label %166, label %149

149:                                              ; preds = %147, %17
  %150 = phi i64 [ 0, %17 ], [ %144, %147 ]
  %151 = phi i64 [ 0, %17 ], [ %143, %147 ]
  %152 = icmp ne i64 %18, 0
  tail call void @llvm.assume(i1 %152)
  br label %153

153:                                              ; preds = %153, %149
  %154 = phi i64 [ %163, %153 ], [ %150, %149 ]
  %155 = phi i64 [ %162, %153 ], [ %151, %149 ]
  %156 = phi i64 [ %164, %153 ], [ 0, %149 ]
  %157 = getelementptr inbounds nuw i8, ptr %14, i64 %154
  %158 = load i8, ptr %157, align 1, !tbaa !18
  %159 = zext i8 %158 to i64
  %160 = shl nsw i64 %154, 3
  %161 = shl i64 %159, %160
  %162 = or i64 %161, %155
  %163 = add nuw nsw i64 %154, 1
  %164 = add i64 %156, 1
  %165 = icmp eq i64 %164, %18
  br i1 %165, label %166, label %153, !llvm.loop !53

166:                                              ; preds = %153, %147
  %167 = phi i64 [ %143, %147 ], [ %162, %153 ]
  %168 = srem i64 %167, 8
  br label %169

169:                                              ; preds = %166, %8
  %170 = phi i64 [ 0, %8 ], [ %168, %166 ]
  %171 = load ptr, ptr %1, align 8, !tbaa !9
  %172 = load i64, ptr %4, align 8, !tbaa !15
  %173 = mul nsw i64 %172, %170
  %174 = getelementptr inbounds i8, ptr %171, i64 %173
  %175 = icmp sgt i64 %9, 0
  br i1 %175, label %176, label %234

176:                                              ; preds = %169
  %177 = and i64 %9, 3
  %178 = icmp ult i64 %9, 4
  br i1 %178, label %217, label %179

179:                                              ; preds = %176
  %180 = and i64 %9, 9223372036854775804
  br label %181

181:                                              ; preds = %181, %179
  %182 = phi i64 [ 0, %179 ], [ %212, %181 ]
  %183 = phi i64 [ 0, %179 ], [ %211, %181 ]
  %184 = phi i64 [ 0, %179 ], [ %213, %181 ]
  %185 = getelementptr inbounds nuw i8, ptr %174, i64 %182
  %186 = load i8, ptr %185, align 1, !tbaa !18
  %187 = zext i8 %186 to i64
  %188 = shl nsw i64 %182, 3
  %189 = shl i64 %187, %188
  %190 = or i64 %189, %183
  %191 = or disjoint i64 %182, 1
  %192 = getelementptr inbounds nuw i8, ptr %174, i64 %191
  %193 = load i8, ptr %192, align 1, !tbaa !18
  %194 = zext i8 %193 to i64
  %195 = shl nsw i64 %191, 3
  %196 = shl i64 %194, %195
  %197 = or i64 %196, %190
  %198 = or disjoint i64 %182, 2
  %199 = getelementptr inbounds nuw i8, ptr %174, i64 %198
  %200 = load i8, ptr %199, align 1, !tbaa !18
  %201 = zext i8 %200 to i64
  %202 = shl nsw i64 %198, 3
  %203 = shl i64 %201, %202
  %204 = or i64 %203, %197
  %205 = or disjoint i64 %182, 3
  %206 = getelementptr inbounds nuw i8, ptr %174, i64 %205
  %207 = load i8, ptr %206, align 1, !tbaa !18
  %208 = zext i8 %207 to i64
  %209 = shl nsw i64 %205, 3
  %210 = shl i64 %208, %209
  %211 = or i64 %210, %204
  %212 = add nuw nsw i64 %182, 4
  %213 = add i64 %184, 4
  %214 = icmp eq i64 %213, %180
  br i1 %214, label %215, label %181, !llvm.loop !33

215:                                              ; preds = %181
  %216 = icmp eq i64 %177, 0
  br i1 %216, label %234, label %217

217:                                              ; preds = %215, %176
  %218 = phi i64 [ 0, %176 ], [ %212, %215 ]
  %219 = phi i64 [ 0, %176 ], [ %211, %215 ]
  %220 = icmp ne i64 %177, 0
  tail call void @llvm.assume(i1 %220)
  br label %221

221:                                              ; preds = %221, %217
  %222 = phi i64 [ %231, %221 ], [ %218, %217 ]
  %223 = phi i64 [ %230, %221 ], [ %219, %217 ]
  %224 = phi i64 [ %232, %221 ], [ 0, %217 ]
  %225 = getelementptr inbounds nuw i8, ptr %174, i64 %222
  %226 = load i8, ptr %225, align 1, !tbaa !18
  %227 = zext i8 %226 to i64
  %228 = shl nsw i64 %222, 3
  %229 = shl i64 %227, %228
  %230 = or i64 %229, %223
  %231 = add nuw nsw i64 %222, 1
  %232 = add i64 %224, 1
  %233 = icmp eq i64 %232, %177
  br i1 %233, label %234, label %221, !llvm.loop !54

234:                                              ; preds = %215, %221, %169
  %235 = phi i64 [ 0, %169 ], [ %211, %215 ], [ %230, %221 ]
  %236 = load ptr, ptr %2, align 8, !tbaa !9
  %237 = load i64, ptr %13, align 8, !tbaa !16
  %238 = icmp sgt i64 %237, 0
  br i1 %238, label %239, label %253

239:                                              ; preds = %234, %239
  %240 = phi i64 [ %245, %239 ], [ 0, %234 ]
  %241 = shl nsw i64 %240, 3
  %242 = ashr i64 %235, %241
  %243 = trunc i64 %242 to i8
  %244 = getelementptr inbounds nuw i8, ptr %236, i64 %240
  store i8 %243, ptr %244, align 1, !tbaa !18
  %245 = add nuw nsw i64 %240, 1
  %246 = load i64, ptr %13, align 8, !tbaa !16
  %247 = icmp slt i64 %245, %246
  br i1 %247, label %239, label %248, !llvm.loop !41

248:                                              ; preds = %239
  %249 = load ptr, ptr %1, align 8, !tbaa !9
  %250 = load i64, ptr %4, align 8, !tbaa !15
  %251 = load i64, ptr %5, align 8, !tbaa !16
  %252 = mul nsw i64 %250, %170
  br label %253

253:                                              ; preds = %248, %234
  %254 = phi i64 [ %252, %248 ], [ %173, %234 ]
  %255 = phi i64 [ %251, %248 ], [ %9, %234 ]
  %256 = phi ptr [ %249, %248 ], [ %171, %234 ]
  %257 = getelementptr inbounds i8, ptr %256, i64 %254
  %258 = icmp sgt i64 %255, 0
  br i1 %258, label %259, label %265

259:                                              ; preds = %253, %259
  %260 = phi i64 [ %262, %259 ], [ 0, %253 ]
  %261 = getelementptr inbounds nuw i8, ptr %257, i64 %260
  store i8 0, ptr %261, align 1, !tbaa !18
  %262 = add nuw nsw i64 %260, 1
  %263 = load i64, ptr %5, align 8, !tbaa !16
  %264 = icmp slt i64 %262, %263
  br i1 %264, label %259, label %265, !llvm.loop !41

265:                                              ; preds = %259, %253
  %266 = phi i64 [ %255, %253 ], [ %263, %259 ]
  %267 = load ptr, ptr %0, align 8, !tbaa !9
  %268 = load i64, ptr %10, align 8, !tbaa !15
  %269 = getelementptr inbounds i8, ptr %267, i64 %268
  %270 = load i64, ptr %11, align 8, !tbaa !16
  %271 = icmp sgt i64 %270, 0
  br i1 %271, label %272, label %333

272:                                              ; preds = %265
  %273 = and i64 %270, 3
  %274 = icmp ult i64 %270, 4
  br i1 %274, label %313, label %275

275:                                              ; preds = %272
  %276 = and i64 %270, 9223372036854775804
  br label %277

277:                                              ; preds = %277, %275
  %278 = phi i64 [ 0, %275 ], [ %308, %277 ]
  %279 = phi i64 [ 0, %275 ], [ %307, %277 ]
  %280 = phi i64 [ 0, %275 ], [ %309, %277 ]
  %281 = getelementptr inbounds nuw i8, ptr %269, i64 %278
  %282 = load i8, ptr %281, align 1, !tbaa !18
  %283 = zext i8 %282 to i64
  %284 = shl nsw i64 %278, 3
  %285 = shl i64 %283, %284
  %286 = or i64 %285, %279
  %287 = or disjoint i64 %278, 1
  %288 = getelementptr inbounds nuw i8, ptr %269, i64 %287
  %289 = load i8, ptr %288, align 1, !tbaa !18
  %290 = zext i8 %289 to i64
  %291 = shl nsw i64 %287, 3
  %292 = shl i64 %290, %291
  %293 = or i64 %292, %286
  %294 = or disjoint i64 %278, 2
  %295 = getelementptr inbounds nuw i8, ptr %269, i64 %294
  %296 = load i8, ptr %295, align 1, !tbaa !18
  %297 = zext i8 %296 to i64
  %298 = shl nsw i64 %294, 3
  %299 = shl i64 %297, %298
  %300 = or i64 %299, %293
  %301 = or disjoint i64 %278, 3
  %302 = getelementptr inbounds nuw i8, ptr %269, i64 %301
  %303 = load i8, ptr %302, align 1, !tbaa !18
  %304 = zext i8 %303 to i64
  %305 = shl nsw i64 %301, 3
  %306 = shl i64 %304, %305
  %307 = or i64 %306, %300
  %308 = add nuw nsw i64 %278, 4
  %309 = add i64 %280, 4
  %310 = icmp eq i64 %309, %276
  br i1 %310, label %311, label %277, !llvm.loop !33

311:                                              ; preds = %277
  %312 = icmp eq i64 %273, 0
  br i1 %312, label %330, label %313

313:                                              ; preds = %311, %272
  %314 = phi i64 [ 0, %272 ], [ %308, %311 ]
  %315 = phi i64 [ 0, %272 ], [ %307, %311 ]
  %316 = icmp ne i64 %273, 0
  tail call void @llvm.assume(i1 %316)
  br label %317

317:                                              ; preds = %317, %313
  %318 = phi i64 [ %327, %317 ], [ %314, %313 ]
  %319 = phi i64 [ %326, %317 ], [ %315, %313 ]
  %320 = phi i64 [ %328, %317 ], [ 0, %313 ]
  %321 = getelementptr inbounds nuw i8, ptr %269, i64 %318
  %322 = load i8, ptr %321, align 1, !tbaa !18
  %323 = zext i8 %322 to i64
  %324 = shl nsw i64 %318, 3
  %325 = shl i64 %323, %324
  %326 = or i64 %325, %319
  %327 = add nuw nsw i64 %318, 1
  %328 = add i64 %320, 1
  %329 = icmp eq i64 %328, %273
  br i1 %329, label %330, label %317, !llvm.loop !55

330:                                              ; preds = %317, %311
  %331 = phi i64 [ %307, %311 ], [ %326, %317 ]
  %332 = srem i64 %331, 8
  br label %333

333:                                              ; preds = %330, %265
  %334 = phi i64 [ 0, %265 ], [ %332, %330 ]
  %335 = load ptr, ptr %1, align 8, !tbaa !9
  %336 = load i64, ptr %4, align 8, !tbaa !15
  %337 = mul nsw i64 %336, %334
  %338 = getelementptr inbounds i8, ptr %335, i64 %337
  %339 = icmp sgt i64 %266, 0
  br i1 %339, label %340, label %398

340:                                              ; preds = %333
  %341 = and i64 %266, 3
  %342 = icmp ult i64 %266, 4
  br i1 %342, label %381, label %343

343:                                              ; preds = %340
  %344 = and i64 %266, 9223372036854775804
  br label %345

345:                                              ; preds = %345, %343
  %346 = phi i64 [ 0, %343 ], [ %376, %345 ]
  %347 = phi i64 [ 0, %343 ], [ %375, %345 ]
  %348 = phi i64 [ 0, %343 ], [ %377, %345 ]
  %349 = getelementptr inbounds nuw i8, ptr %338, i64 %346
  %350 = load i8, ptr %349, align 1, !tbaa !18
  %351 = zext i8 %350 to i64
  %352 = shl nsw i64 %346, 3
  %353 = shl i64 %351, %352
  %354 = or i64 %353, %347
  %355 = or disjoint i64 %346, 1
  %356 = getelementptr inbounds nuw i8, ptr %338, i64 %355
  %357 = load i8, ptr %356, align 1, !tbaa !18
  %358 = zext i8 %357 to i64
  %359 = shl nsw i64 %355, 3
  %360 = shl i64 %358, %359
  %361 = or i64 %360, %354
  %362 = or disjoint i64 %346, 2
  %363 = getelementptr inbounds nuw i8, ptr %338, i64 %362
  %364 = load i8, ptr %363, align 1, !tbaa !18
  %365 = zext i8 %364 to i64
  %366 = shl nsw i64 %362, 3
  %367 = shl i64 %365, %366
  %368 = or i64 %367, %361
  %369 = or disjoint i64 %346, 3
  %370 = getelementptr inbounds nuw i8, ptr %338, i64 %369
  %371 = load i8, ptr %370, align 1, !tbaa !18
  %372 = zext i8 %371 to i64
  %373 = shl nsw i64 %369, 3
  %374 = shl i64 %372, %373
  %375 = or i64 %374, %368
  %376 = add nuw nsw i64 %346, 4
  %377 = add i64 %348, 4
  %378 = icmp eq i64 %377, %344
  br i1 %378, label %379, label %345, !llvm.loop !33

379:                                              ; preds = %345
  %380 = icmp eq i64 %341, 0
  br i1 %380, label %398, label %381

381:                                              ; preds = %379, %340
  %382 = phi i64 [ 0, %340 ], [ %376, %379 ]
  %383 = phi i64 [ 0, %340 ], [ %375, %379 ]
  %384 = icmp ne i64 %341, 0
  tail call void @llvm.assume(i1 %384)
  br label %385

385:                                              ; preds = %385, %381
  %386 = phi i64 [ %395, %385 ], [ %382, %381 ]
  %387 = phi i64 [ %394, %385 ], [ %383, %381 ]
  %388 = phi i64 [ %396, %385 ], [ 0, %381 ]
  %389 = getelementptr inbounds nuw i8, ptr %338, i64 %386
  %390 = load i8, ptr %389, align 1, !tbaa !18
  %391 = zext i8 %390 to i64
  %392 = shl nsw i64 %386, 3
  %393 = shl i64 %391, %392
  %394 = or i64 %393, %387
  %395 = add nuw nsw i64 %386, 1
  %396 = add i64 %388, 1
  %397 = icmp eq i64 %396, %341
  br i1 %397, label %398, label %385, !llvm.loop !56

398:                                              ; preds = %379, %385, %333
  %399 = phi i64 [ 0, %333 ], [ %375, %379 ], [ %394, %385 ]
  %400 = load ptr, ptr %2, align 8, !tbaa !9
  %401 = load i64, ptr %12, align 8, !tbaa !15
  %402 = getelementptr inbounds i8, ptr %400, i64 %401
  %403 = load i64, ptr %13, align 8, !tbaa !16
  %404 = icmp sgt i64 %403, 0
  br i1 %404, label %405, label %419

405:                                              ; preds = %398, %405
  %406 = phi i64 [ %411, %405 ], [ 0, %398 ]
  %407 = shl nsw i64 %406, 3
  %408 = ashr i64 %399, %407
  %409 = trunc i64 %408 to i8
  %410 = getelementptr inbounds nuw i8, ptr %402, i64 %406
  store i8 %409, ptr %410, align 1, !tbaa !18
  %411 = add nuw nsw i64 %406, 1
  %412 = load i64, ptr %13, align 8, !tbaa !16
  %413 = icmp slt i64 %411, %412
  br i1 %413, label %405, label %414, !llvm.loop !41

414:                                              ; preds = %405
  %415 = load ptr, ptr %1, align 8, !tbaa !9
  %416 = load i64, ptr %4, align 8, !tbaa !15
  %417 = load i64, ptr %5, align 8, !tbaa !16
  %418 = mul nsw i64 %416, %334
  br label %419

419:                                              ; preds = %414, %398
  %420 = phi i64 [ %418, %414 ], [ %337, %398 ]
  %421 = phi i64 [ %417, %414 ], [ %266, %398 ]
  %422 = phi ptr [ %415, %414 ], [ %335, %398 ]
  %423 = getelementptr inbounds i8, ptr %422, i64 %420
  %424 = icmp sgt i64 %421, 0
  br i1 %424, label %425, label %433

425:                                              ; preds = %419, %425
  %426 = phi i64 [ %430, %425 ], [ 0, %419 ]
  %427 = icmp eq i64 %426, 0
  %428 = zext i1 %427 to i8
  %429 = getelementptr inbounds nuw i8, ptr %423, i64 %426
  store i8 %428, ptr %429, align 1, !tbaa !18
  %430 = add nuw nsw i64 %426, 1
  %431 = load i64, ptr %5, align 8, !tbaa !16
  %432 = icmp slt i64 %430, %431
  br i1 %432, label %425, label %433, !llvm.loop !41

433:                                              ; preds = %425, %419
  %434 = phi i64 [ %421, %419 ], [ %431, %425 ]
  %435 = load ptr, ptr %0, align 8, !tbaa !9
  %436 = load i64, ptr %10, align 8, !tbaa !15
  %437 = shl nsw i64 %436, 1
  %438 = getelementptr inbounds i8, ptr %435, i64 %437
  %439 = load i64, ptr %11, align 8, !tbaa !16
  %440 = icmp sgt i64 %439, 0
  br i1 %440, label %441, label %502

441:                                              ; preds = %433
  %442 = and i64 %439, 3
  %443 = icmp ult i64 %439, 4
  br i1 %443, label %482, label %444

444:                                              ; preds = %441
  %445 = and i64 %439, 9223372036854775804
  br label %446

446:                                              ; preds = %446, %444
  %447 = phi i64 [ 0, %444 ], [ %477, %446 ]
  %448 = phi i64 [ 0, %444 ], [ %476, %446 ]
  %449 = phi i64 [ 0, %444 ], [ %478, %446 ]
  %450 = getelementptr inbounds nuw i8, ptr %438, i64 %447
  %451 = load i8, ptr %450, align 1, !tbaa !18
  %452 = zext i8 %451 to i64
  %453 = shl nsw i64 %447, 3
  %454 = shl i64 %452, %453
  %455 = or i64 %454, %448
  %456 = or disjoint i64 %447, 1
  %457 = getelementptr inbounds nuw i8, ptr %438, i64 %456
  %458 = load i8, ptr %457, align 1, !tbaa !18
  %459 = zext i8 %458 to i64
  %460 = shl nsw i64 %456, 3
  %461 = shl i64 %459, %460
  %462 = or i64 %461, %455
  %463 = or disjoint i64 %447, 2
  %464 = getelementptr inbounds nuw i8, ptr %438, i64 %463
  %465 = load i8, ptr %464, align 1, !tbaa !18
  %466 = zext i8 %465 to i64
  %467 = shl nsw i64 %463, 3
  %468 = shl i64 %466, %467
  %469 = or i64 %468, %462
  %470 = or disjoint i64 %447, 3
  %471 = getelementptr inbounds nuw i8, ptr %438, i64 %470
  %472 = load i8, ptr %471, align 1, !tbaa !18
  %473 = zext i8 %472 to i64
  %474 = shl nsw i64 %470, 3
  %475 = shl i64 %473, %474
  %476 = or i64 %475, %469
  %477 = add nuw nsw i64 %447, 4
  %478 = add i64 %449, 4
  %479 = icmp eq i64 %478, %445
  br i1 %479, label %480, label %446, !llvm.loop !33

480:                                              ; preds = %446
  %481 = icmp eq i64 %442, 0
  br i1 %481, label %499, label %482

482:                                              ; preds = %480, %441
  %483 = phi i64 [ 0, %441 ], [ %477, %480 ]
  %484 = phi i64 [ 0, %441 ], [ %476, %480 ]
  %485 = icmp ne i64 %442, 0
  tail call void @llvm.assume(i1 %485)
  br label %486

486:                                              ; preds = %486, %482
  %487 = phi i64 [ %496, %486 ], [ %483, %482 ]
  %488 = phi i64 [ %495, %486 ], [ %484, %482 ]
  %489 = phi i64 [ %497, %486 ], [ 0, %482 ]
  %490 = getelementptr inbounds nuw i8, ptr %438, i64 %487
  %491 = load i8, ptr %490, align 1, !tbaa !18
  %492 = zext i8 %491 to i64
  %493 = shl nsw i64 %487, 3
  %494 = shl i64 %492, %493
  %495 = or i64 %494, %488
  %496 = add nuw nsw i64 %487, 1
  %497 = add i64 %489, 1
  %498 = icmp eq i64 %497, %442
  br i1 %498, label %499, label %486, !llvm.loop !57

499:                                              ; preds = %486, %480
  %500 = phi i64 [ %476, %480 ], [ %495, %486 ]
  %501 = srem i64 %500, 8
  br label %502

502:                                              ; preds = %499, %433
  %503 = phi i64 [ 0, %433 ], [ %501, %499 ]
  %504 = load ptr, ptr %1, align 8, !tbaa !9
  %505 = load i64, ptr %4, align 8, !tbaa !15
  %506 = mul nsw i64 %505, %503
  %507 = getelementptr inbounds i8, ptr %504, i64 %506
  %508 = icmp sgt i64 %434, 0
  br i1 %508, label %509, label %567

509:                                              ; preds = %502
  %510 = and i64 %434, 3
  %511 = icmp ult i64 %434, 4
  br i1 %511, label %550, label %512

512:                                              ; preds = %509
  %513 = and i64 %434, 9223372036854775804
  br label %514

514:                                              ; preds = %514, %512
  %515 = phi i64 [ 0, %512 ], [ %545, %514 ]
  %516 = phi i64 [ 0, %512 ], [ %544, %514 ]
  %517 = phi i64 [ 0, %512 ], [ %546, %514 ]
  %518 = getelementptr inbounds nuw i8, ptr %507, i64 %515
  %519 = load i8, ptr %518, align 1, !tbaa !18
  %520 = zext i8 %519 to i64
  %521 = shl nsw i64 %515, 3
  %522 = shl i64 %520, %521
  %523 = or i64 %522, %516
  %524 = or disjoint i64 %515, 1
  %525 = getelementptr inbounds nuw i8, ptr %507, i64 %524
  %526 = load i8, ptr %525, align 1, !tbaa !18
  %527 = zext i8 %526 to i64
  %528 = shl nsw i64 %524, 3
  %529 = shl i64 %527, %528
  %530 = or i64 %529, %523
  %531 = or disjoint i64 %515, 2
  %532 = getelementptr inbounds nuw i8, ptr %507, i64 %531
  %533 = load i8, ptr %532, align 1, !tbaa !18
  %534 = zext i8 %533 to i64
  %535 = shl nsw i64 %531, 3
  %536 = shl i64 %534, %535
  %537 = or i64 %536, %530
  %538 = or disjoint i64 %515, 3
  %539 = getelementptr inbounds nuw i8, ptr %507, i64 %538
  %540 = load i8, ptr %539, align 1, !tbaa !18
  %541 = zext i8 %540 to i64
  %542 = shl nsw i64 %538, 3
  %543 = shl i64 %541, %542
  %544 = or i64 %543, %537
  %545 = add nuw nsw i64 %515, 4
  %546 = add i64 %517, 4
  %547 = icmp eq i64 %546, %513
  br i1 %547, label %548, label %514, !llvm.loop !33

548:                                              ; preds = %514
  %549 = icmp eq i64 %510, 0
  br i1 %549, label %567, label %550

550:                                              ; preds = %548, %509
  %551 = phi i64 [ 0, %509 ], [ %545, %548 ]
  %552 = phi i64 [ 0, %509 ], [ %544, %548 ]
  %553 = icmp ne i64 %510, 0
  tail call void @llvm.assume(i1 %553)
  br label %554

554:                                              ; preds = %554, %550
  %555 = phi i64 [ %564, %554 ], [ %551, %550 ]
  %556 = phi i64 [ %563, %554 ], [ %552, %550 ]
  %557 = phi i64 [ %565, %554 ], [ 0, %550 ]
  %558 = getelementptr inbounds nuw i8, ptr %507, i64 %555
  %559 = load i8, ptr %558, align 1, !tbaa !18
  %560 = zext i8 %559 to i64
  %561 = shl nsw i64 %555, 3
  %562 = shl i64 %560, %561
  %563 = or i64 %562, %556
  %564 = add nuw nsw i64 %555, 1
  %565 = add i64 %557, 1
  %566 = icmp eq i64 %565, %510
  br i1 %566, label %567, label %554, !llvm.loop !58

567:                                              ; preds = %548, %554, %502
  %568 = phi i64 [ 0, %502 ], [ %544, %548 ], [ %563, %554 ]
  %569 = load ptr, ptr %2, align 8, !tbaa !9
  %570 = load i64, ptr %12, align 8, !tbaa !15
  %571 = shl nsw i64 %570, 1
  %572 = getelementptr inbounds i8, ptr %569, i64 %571
  %573 = load i64, ptr %13, align 8, !tbaa !16
  %574 = icmp sgt i64 %573, 0
  br i1 %574, label %575, label %589

575:                                              ; preds = %567, %575
  %576 = phi i64 [ %581, %575 ], [ 0, %567 ]
  %577 = shl nsw i64 %576, 3
  %578 = ashr i64 %568, %577
  %579 = trunc i64 %578 to i8
  %580 = getelementptr inbounds nuw i8, ptr %572, i64 %576
  store i8 %579, ptr %580, align 1, !tbaa !18
  %581 = add nuw nsw i64 %576, 1
  %582 = load i64, ptr %13, align 8, !tbaa !16
  %583 = icmp slt i64 %581, %582
  br i1 %583, label %575, label %584, !llvm.loop !41

584:                                              ; preds = %575
  %585 = load ptr, ptr %1, align 8, !tbaa !9
  %586 = load i64, ptr %4, align 8, !tbaa !15
  %587 = load i64, ptr %5, align 8, !tbaa !16
  %588 = mul nsw i64 %586, %503
  br label %589

589:                                              ; preds = %584, %567
  %590 = phi i64 [ %588, %584 ], [ %506, %567 ]
  %591 = phi i64 [ %587, %584 ], [ %434, %567 ]
  %592 = phi ptr [ %585, %584 ], [ %504, %567 ]
  %593 = getelementptr inbounds i8, ptr %592, i64 %590
  %594 = icmp sgt i64 %591, 0
  br i1 %594, label %595, label %604

595:                                              ; preds = %589, %595
  %596 = phi i64 [ %601, %595 ], [ 0, %589 ]
  %597 = shl nsw i64 %596, 3
  %598 = lshr i64 2, %597
  %599 = trunc nuw nsw i64 %598 to i8
  %600 = getelementptr inbounds nuw i8, ptr %593, i64 %596
  store i8 %599, ptr %600, align 1, !tbaa !18
  %601 = add nuw nsw i64 %596, 1
  %602 = load i64, ptr %5, align 8, !tbaa !16
  %603 = icmp slt i64 %601, %602
  br i1 %603, label %595, label %604, !llvm.loop !41

604:                                              ; preds = %595, %589
  %605 = phi i64 [ %591, %589 ], [ %602, %595 ]
  %606 = load ptr, ptr %0, align 8, !tbaa !9
  %607 = load i64, ptr %10, align 8, !tbaa !15
  %608 = mul nsw i64 %607, 3
  %609 = getelementptr inbounds i8, ptr %606, i64 %608
  %610 = load i64, ptr %11, align 8, !tbaa !16
  %611 = icmp sgt i64 %610, 0
  br i1 %611, label %612, label %673

612:                                              ; preds = %604
  %613 = and i64 %610, 3
  %614 = icmp ult i64 %610, 4
  br i1 %614, label %653, label %615

615:                                              ; preds = %612
  %616 = and i64 %610, 9223372036854775804
  br label %617

617:                                              ; preds = %617, %615
  %618 = phi i64 [ 0, %615 ], [ %648, %617 ]
  %619 = phi i64 [ 0, %615 ], [ %647, %617 ]
  %620 = phi i64 [ 0, %615 ], [ %649, %617 ]
  %621 = getelementptr inbounds nuw i8, ptr %609, i64 %618
  %622 = load i8, ptr %621, align 1, !tbaa !18
  %623 = zext i8 %622 to i64
  %624 = shl nsw i64 %618, 3
  %625 = shl i64 %623, %624
  %626 = or i64 %625, %619
  %627 = or disjoint i64 %618, 1
  %628 = getelementptr inbounds nuw i8, ptr %609, i64 %627
  %629 = load i8, ptr %628, align 1, !tbaa !18
  %630 = zext i8 %629 to i64
  %631 = shl nsw i64 %627, 3
  %632 = shl i64 %630, %631
  %633 = or i64 %632, %626
  %634 = or disjoint i64 %618, 2
  %635 = getelementptr inbounds nuw i8, ptr %609, i64 %634
  %636 = load i8, ptr %635, align 1, !tbaa !18
  %637 = zext i8 %636 to i64
  %638 = shl nsw i64 %634, 3
  %639 = shl i64 %637, %638
  %640 = or i64 %639, %633
  %641 = or disjoint i64 %618, 3
  %642 = getelementptr inbounds nuw i8, ptr %609, i64 %641
  %643 = load i8, ptr %642, align 1, !tbaa !18
  %644 = zext i8 %643 to i64
  %645 = shl nsw i64 %641, 3
  %646 = shl i64 %644, %645
  %647 = or i64 %646, %640
  %648 = add nuw nsw i64 %618, 4
  %649 = add i64 %620, 4
  %650 = icmp eq i64 %649, %616
  br i1 %650, label %651, label %617, !llvm.loop !33

651:                                              ; preds = %617
  %652 = icmp eq i64 %613, 0
  br i1 %652, label %670, label %653

653:                                              ; preds = %651, %612
  %654 = phi i64 [ 0, %612 ], [ %648, %651 ]
  %655 = phi i64 [ 0, %612 ], [ %647, %651 ]
  %656 = icmp ne i64 %613, 0
  tail call void @llvm.assume(i1 %656)
  br label %657

657:                                              ; preds = %657, %653
  %658 = phi i64 [ %667, %657 ], [ %654, %653 ]
  %659 = phi i64 [ %666, %657 ], [ %655, %653 ]
  %660 = phi i64 [ %668, %657 ], [ 0, %653 ]
  %661 = getelementptr inbounds nuw i8, ptr %609, i64 %658
  %662 = load i8, ptr %661, align 1, !tbaa !18
  %663 = zext i8 %662 to i64
  %664 = shl nsw i64 %658, 3
  %665 = shl i64 %663, %664
  %666 = or i64 %665, %659
  %667 = add nuw nsw i64 %658, 1
  %668 = add i64 %660, 1
  %669 = icmp eq i64 %668, %613
  br i1 %669, label %670, label %657, !llvm.loop !59

670:                                              ; preds = %657, %651
  %671 = phi i64 [ %647, %651 ], [ %666, %657 ]
  %672 = srem i64 %671, 8
  br label %673

673:                                              ; preds = %670, %604
  %674 = phi i64 [ 0, %604 ], [ %672, %670 ]
  %675 = load ptr, ptr %1, align 8, !tbaa !9
  %676 = load i64, ptr %4, align 8, !tbaa !15
  %677 = mul nsw i64 %676, %674
  %678 = getelementptr inbounds i8, ptr %675, i64 %677
  %679 = icmp sgt i64 %605, 0
  br i1 %679, label %680, label %738

680:                                              ; preds = %673
  %681 = and i64 %605, 3
  %682 = icmp ult i64 %605, 4
  br i1 %682, label %721, label %683

683:                                              ; preds = %680
  %684 = and i64 %605, 9223372036854775804
  br label %685

685:                                              ; preds = %685, %683
  %686 = phi i64 [ 0, %683 ], [ %716, %685 ]
  %687 = phi i64 [ 0, %683 ], [ %715, %685 ]
  %688 = phi i64 [ 0, %683 ], [ %717, %685 ]
  %689 = getelementptr inbounds nuw i8, ptr %678, i64 %686
  %690 = load i8, ptr %689, align 1, !tbaa !18
  %691 = zext i8 %690 to i64
  %692 = shl nsw i64 %686, 3
  %693 = shl i64 %691, %692
  %694 = or i64 %693, %687
  %695 = or disjoint i64 %686, 1
  %696 = getelementptr inbounds nuw i8, ptr %678, i64 %695
  %697 = load i8, ptr %696, align 1, !tbaa !18
  %698 = zext i8 %697 to i64
  %699 = shl nsw i64 %695, 3
  %700 = shl i64 %698, %699
  %701 = or i64 %700, %694
  %702 = or disjoint i64 %686, 2
  %703 = getelementptr inbounds nuw i8, ptr %678, i64 %702
  %704 = load i8, ptr %703, align 1, !tbaa !18
  %705 = zext i8 %704 to i64
  %706 = shl nsw i64 %702, 3
  %707 = shl i64 %705, %706
  %708 = or i64 %707, %701
  %709 = or disjoint i64 %686, 3
  %710 = getelementptr inbounds nuw i8, ptr %678, i64 %709
  %711 = load i8, ptr %710, align 1, !tbaa !18
  %712 = zext i8 %711 to i64
  %713 = shl nsw i64 %709, 3
  %714 = shl i64 %712, %713
  %715 = or i64 %714, %708
  %716 = add nuw nsw i64 %686, 4
  %717 = add i64 %688, 4
  %718 = icmp eq i64 %717, %684
  br i1 %718, label %719, label %685, !llvm.loop !33

719:                                              ; preds = %685
  %720 = icmp eq i64 %681, 0
  br i1 %720, label %738, label %721

721:                                              ; preds = %719, %680
  %722 = phi i64 [ 0, %680 ], [ %716, %719 ]
  %723 = phi i64 [ 0, %680 ], [ %715, %719 ]
  %724 = icmp ne i64 %681, 0
  tail call void @llvm.assume(i1 %724)
  br label %725

725:                                              ; preds = %725, %721
  %726 = phi i64 [ %735, %725 ], [ %722, %721 ]
  %727 = phi i64 [ %734, %725 ], [ %723, %721 ]
  %728 = phi i64 [ %736, %725 ], [ 0, %721 ]
  %729 = getelementptr inbounds nuw i8, ptr %678, i64 %726
  %730 = load i8, ptr %729, align 1, !tbaa !18
  %731 = zext i8 %730 to i64
  %732 = shl nsw i64 %726, 3
  %733 = shl i64 %731, %732
  %734 = or i64 %733, %727
  %735 = add nuw nsw i64 %726, 1
  %736 = add i64 %728, 1
  %737 = icmp eq i64 %736, %681
  br i1 %737, label %738, label %725, !llvm.loop !60

738:                                              ; preds = %719, %725, %673
  %739 = phi i64 [ 0, %673 ], [ %715, %719 ], [ %734, %725 ]
  %740 = load ptr, ptr %2, align 8, !tbaa !9
  %741 = load i64, ptr %12, align 8, !tbaa !15
  %742 = mul nsw i64 %741, 3
  %743 = getelementptr inbounds i8, ptr %740, i64 %742
  %744 = load i64, ptr %13, align 8, !tbaa !16
  %745 = icmp sgt i64 %744, 0
  br i1 %745, label %746, label %760

746:                                              ; preds = %738, %746
  %747 = phi i64 [ %752, %746 ], [ 0, %738 ]
  %748 = shl nsw i64 %747, 3
  %749 = ashr i64 %739, %748
  %750 = trunc i64 %749 to i8
  %751 = getelementptr inbounds nuw i8, ptr %743, i64 %747
  store i8 %750, ptr %751, align 1, !tbaa !18
  %752 = add nuw nsw i64 %747, 1
  %753 = load i64, ptr %13, align 8, !tbaa !16
  %754 = icmp slt i64 %752, %753
  br i1 %754, label %746, label %755, !llvm.loop !41

755:                                              ; preds = %746
  %756 = load ptr, ptr %1, align 8, !tbaa !9
  %757 = load i64, ptr %4, align 8, !tbaa !15
  %758 = load i64, ptr %5, align 8, !tbaa !16
  %759 = mul nsw i64 %757, %674
  br label %760

760:                                              ; preds = %755, %738
  %761 = phi i64 [ %759, %755 ], [ %677, %738 ]
  %762 = phi i64 [ %758, %755 ], [ %605, %738 ]
  %763 = phi ptr [ %756, %755 ], [ %675, %738 ]
  %764 = getelementptr inbounds i8, ptr %763, i64 %761
  %765 = icmp sgt i64 %762, 0
  br i1 %765, label %766, label %775

766:                                              ; preds = %760, %766
  %767 = phi i64 [ %772, %766 ], [ 0, %760 ]
  %768 = shl nsw i64 %767, 3
  %769 = lshr i64 3, %768
  %770 = trunc nuw nsw i64 %769 to i8
  %771 = getelementptr inbounds nuw i8, ptr %764, i64 %767
  store i8 %770, ptr %771, align 1, !tbaa !18
  %772 = add nuw nsw i64 %767, 1
  %773 = load i64, ptr %5, align 8, !tbaa !16
  %774 = icmp slt i64 %772, %773
  br i1 %774, label %766, label %775, !llvm.loop !41

775:                                              ; preds = %766, %760
  ret void
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind willreturn memory(errnomem: write)
declare double @exp(double noundef) local_unnamed_addr #5

; Function Attrs: nofree nounwind
declare noundef i32 @puts(ptr noundef readonly captures(none)) local_unnamed_addr #6

; Function Attrs: nocallback nocreateundeforpoison nofree nosync nounwind speculatable willreturn memory(none)
declare i64 @llvm.smax.i64(i64, i64) #7

; Function Attrs: nocallback nofree nosync nounwind willreturn memory(inaccessiblemem: write)
declare void @llvm.assume(i1 noundef) #8

attributes #0 = { nofree nounwind sspstrong uwtable "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #1 = { mustprogress nocallback nofree nosync nounwind willreturn memory(argmem: readwrite) }
attributes #2 = { mustprogress nocallback nofree nosync nounwind willreturn memory(argmem: write) }
attributes #3 = { nofree nounwind "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #4 = { nofree norecurse nosync nounwind sspstrong memory(readwrite, inaccessiblemem: none, target_mem: none) uwtable "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #5 = { mustprogress nocallback nofree nosync nounwind willreturn memory(errnomem: write) "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #6 = { nofree nounwind }
attributes #7 = { nocallback nocreateundeforpoison nofree nosync nounwind speculatable willreturn memory(none) }
attributes #8 = { nocallback nofree nosync nounwind willreturn memory(inaccessiblemem: write) }
attributes #9 = { nounwind }

!llvm.module.flags = !{!0, !1, !2}
!llvm.ident = !{!3}
!llvm.errno.tbaa = !{!4}

!0 = !{i32 8, !"PIC Level", i32 2}
!1 = !{i32 7, !"PIE Level", i32 2}
!2 = !{i32 7, !"uwtable", i32 2}
!3 = !{!"clang version 23.1.4"}
!4 = !{!5, !6, i64 0}
!5 = !{!"__libc_errno", !6, i64 0}
!6 = !{!"int", !7, i64 0}
!7 = !{!"omnipotent char", !8, i64 0}
!8 = !{!"Simple C/C++ TBAA"}
!9 = !{!10, !11, i64 0}
!10 = !{!"", !11, i64 0, !13, i64 8, !13, i64 16, !13, i64 24}
!11 = !{!"p1 omnipotent char", !12, i64 0}
!12 = !{!"any pointer", !7, i64 0}
!13 = !{!"long", !7, i64 0}
!14 = !{!10, !13, i64 8}
!15 = !{!10, !13, i64 16}
!16 = !{!10, !13, i64 24}
!17 = !{!13, !13, i64 0}
!18 = !{!7, !7, i64 0}
!19 = distinct !{!19, !20}
!20 = !{!"llvm.loop.mustprogress"}
!21 = distinct !{!21, !20}
!22 = distinct !{!22, !20}
!23 = distinct !{!23, !20}
!24 = distinct !{!24, !20}
!25 = distinct !{!25, !20}
!26 = distinct !{!26, !20, !27}
!27 = !{!"llvm.loop.unswitch.partial.disable"}
!28 = distinct !{!28, !20, !27}
!29 = distinct !{!29, !20}
!30 = distinct !{!30, !20}
!31 = distinct !{!31, !20}
!32 = distinct !{!32, !20}
!33 = distinct !{!33, !20}
!34 = distinct !{!34, !35}
!35 = !{!"llvm.loop.unroll.disable"}
!36 = distinct !{!36, !35}
!37 = distinct !{!37, !35}
!38 = distinct !{!38, !35}
!39 = distinct !{!39, !35}
!40 = distinct !{!40, !35}
!41 = distinct !{!41, !20}
!42 = distinct !{!42, !35}
!43 = distinct !{!43, !35}
!44 = distinct !{!44, !20}
!45 = distinct !{!45, !35}
!46 = distinct !{!46, !35}
!47 = distinct !{!47, !35}
!48 = distinct !{!48, !20}
!49 = distinct !{!49, !35}
!50 = distinct !{!50, !20}
!51 = distinct !{!51, !35}
!52 = distinct !{!52, !35}
!53 = distinct !{!53, !35}
!54 = distinct !{!54, !35}
!55 = distinct !{!55, !35}
!56 = distinct !{!56, !35}
!57 = distinct !{!57, !35}
!58 = distinct !{!58, !35}
!59 = distinct !{!59, !35}
!60 = distinct !{!60, !35}
