; ModuleID = 'src/kernels.c'
source_filename = "src/kernels.c"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-linux-gnu"

%struct.MaruArrayView = type { ptr, i64, i64, i64 }

@__const.main.x = private unnamed_addr constant [3 x i64] [i64 65536, i64 131072, i64 196608], align 16
@__const.main.b = private unnamed_addr constant [2 x i64] [i64 100, i64 200], align 16
@.str = private unnamed_addr constant [19 x i8] c"MATVEC %s %ld %ld\0A\00", align 1
@.str.1 = private unnamed_addr constant [5 x i8] c"PASS\00", align 1
@.str.2 = private unnamed_addr constant [5 x i8] c"FAIL\00", align 1
@.str.3 = private unnamed_addr constant [10 x i8] c"BATCH %s\0A\00", align 1
@__const.main.sx = private unnamed_addr constant [3 x i64] [i64 0, i64 65536, i64 131072], align 16
@.str.4 = private unnamed_addr constant [20 x i8] c"SOFTMAX %s sum=%ld\0A\00", align 1
@__const.main.lx = private unnamed_addr constant [3 x i64] [i64 65536, i64 131072, i64 196608], align 16
@__const.main.g = private unnamed_addr constant [3 x i64] [i64 65536, i64 65536, i64 65536], align 16
@.str.5 = private unnamed_addr constant [23 x i8] c"LAYERNORM %s mean=%ld\0A\00", align 1
@.str.6 = private unnamed_addr constant [17 x i8] c"DIFF %d %ld %ld\0A\00", align 1
@.str.7 = private unnamed_addr constant [20 x i8] c"FUSED-ATTENTION %s\0A\00", align 1
@.str.8 = private unnamed_addr constant [9 x i8] c"TOPK %s\0A\00", align 1
@.str.9 = private unnamed_addr constant [11 x i8] c"ARGMAX %s\0A\00", align 1
@__const.main.ms = private unnamed_addr constant [4 x i64] [i64 5, i64 6, i64 7, i64 8], align 16
@__const.main.mv = private unnamed_addr constant [4 x i64] [i64 1, i64 0, i64 1, i64 1], align 16
@.str.10 = private unnamed_addr constant [19 x i8] c"MASK %s count=%ld\0A\00", align 1
@__const.main.ik = private unnamed_addr constant [4 x i64] [i64 3, i64 7, i64 3, i64 9], align 16
@.str.11 = private unnamed_addr constant [24 x i8] c"INDEX %s c3=%ld c9=%ld\0A\00", align 1
@__const.main.pfh = private unnamed_addr constant [3 x i64] [i64 2, i64 3, i64 5], align 16
@__const.main.pfm = private unnamed_addr constant [3 x i64] [i64 3, i64 4, i64 16], align 16
@.str.12 = private unnamed_addr constant [25 x i8] c"FRONTIER %s derived=%ld\0A\00", align 1
@.str.13 = private unnamed_addr constant [33 x i8] c"FRONTIER-MISSING %s missing=%ld\0A\00", align 1
@__const.main.ba = private unnamed_addr constant [4 x i64] [i64 2, i64 4, i64 0, i64 0], align 16
@.str.14 = private unnamed_addr constant [14 x i8] c"BFS %s n=%ld\0A\00", align 1
@__const.main.ptu = private unnamed_addr constant [3 x i64] [i64 0, i64 1, i64 0], align 16
@__const.main.ptv = private unnamed_addr constant [3 x i64] [i64 1, i64 2, i64 3], align 16
@.str.15 = private unnamed_addr constant [15 x i8] c"TOPO %s n=%ld\0A\00", align 1
@__const.main.pp = private unnamed_addr constant [4 x i64] [i64 0, i64 1, i64 2, i64 3], align 16
@.str.16 = private unnamed_addr constant [15 x i8] c"UNION-FIND %s\0A\00", align 1
@__const.main.ca = private unnamed_addr constant [4 x i64] [i64 2, i64 4, i64 0, i64 0], align 16
@.str.17 = private unnamed_addr constant [19 x i8] c"BITSET-CLOSURE %s\0A\00", align 1
@.str.18 = private unnamed_addr constant [46 x i8] c"INDEX-UPDATE %s add=%ld remove=%ld after=%ld\0A\00", align 1
@.str.19 = private unnamed_addr constant [16 x i8] c"BCE %s %ld %ld\0A\00", align 1
@__const.main.bw = private unnamed_addr constant [4 x i64] [i64 65536, i64 0, i64 0, i64 65536], align 16
@__const.main.bdy = private unnamed_addr constant [2 x i64] [i64 131072, i64 196608], align 16
@.str.20 = private unnamed_addr constant [20 x i8] c"BACKWARD-MATVEC %s\0A\00", align 1
@.str.21 = private unnamed_addr constant [15 x i8] c"ADAM %s p=%ld\0A\00", align 1
@__const.main.lw = private unnamed_addr constant [4 x i64] [i64 65536, i64 0, i64 0, i64 65536], align 16
@__const.main.lb2 = private unnamed_addr constant [2 x i64] [i64 0, i64 -131072], align 16
@__const.main.lx2 = private unnamed_addr constant [2 x i64] [i64 65536, i64 65536], align 16
@.str.22 = private unnamed_addr constant [24 x i8] c"LINEAR-RELU %s %ld %ld\0A\00", align 1
@__const.main.lx3 = private unnamed_addr constant [3 x i64] [i64 65536, i64 131072, i64 196608], align 16
@__const.main.lg3 = private unnamed_addr constant [3 x i64] [i64 65536, i64 65536, i64 65536], align 16
@.str.23 = private unnamed_addr constant [22 x i8] c"LINEAR-LN %s sum=%ld\0A\00", align 1
@__const.main.pih = private unnamed_addr constant [3 x i64] [i64 2, i64 3, i64 5], align 16
@__const.main.pibm = private unnamed_addr constant [3 x i64] [i64 3, i64 16, i64 1], align 16
@__const.main.pisc = private unnamed_addr constant [3 x i64] [i64 100, i64 300, i64 200], align 16
@.str.24 = private unnamed_addr constant [20 x i8] c"INTEGRATE %s n=%ld\0A\00", align 1
@.str.25 = private unnamed_addr constant [26 x i8] c"PROOF-GATE %s invalid=%d\0A\00", align 1
@.str.26 = private unnamed_addr constant [22 x i8] c"KERNEL-SUITE-PHASE11\0A\00", align 1

; Function Attrs: noinline nounwind optnone sspstrong uwtable
define dso_local i32 @main() #0 {
  %1 = alloca i32, align 4
  %2 = alloca [6 x i64], align 16
  %3 = alloca [3 x i64], align 16
  %4 = alloca [2 x i64], align 16
  %5 = alloca %struct.MaruArrayView, align 8
  %6 = alloca %struct.MaruArrayView, align 8
  %7 = alloca %struct.MaruArrayView, align 8
  %8 = alloca [2 x i64], align 16
  %9 = alloca i64, align 8
  %10 = alloca i64, align 8
  %11 = alloca [6 x i64], align 16
  %12 = alloca %struct.MaruArrayView, align 8
  %13 = alloca [4 x i64], align 16
  %14 = alloca [3 x i64], align 16
  %15 = alloca [3 x i64], align 16
  %16 = alloca %struct.MaruArrayView, align 8
  %17 = alloca %struct.MaruArrayView, align 8
  %18 = alloca i64, align 8
  %19 = alloca i32, align 4
  %20 = alloca [3 x i64], align 16
  %21 = alloca [3 x i64], align 16
  %22 = alloca [3 x i64], align 16
  %23 = alloca [3 x i64], align 16
  %24 = alloca %struct.MaruArrayView, align 8
  %25 = alloca %struct.MaruArrayView, align 8
  %26 = alloca %struct.MaruArrayView, align 8
  %27 = alloca %struct.MaruArrayView, align 8
  %28 = alloca i64, align 8
  %29 = alloca i32, align 4
  %30 = alloca [12 x i64], align 16
  %31 = alloca [48 x i64], align 16
  %32 = alloca [12 x i64], align 16
  %33 = alloca [16 x i64], align 16
  %34 = alloca [4 x i64], align 16
  %35 = alloca [4 x i64], align 16
  %36 = alloca [4 x i64], align 16
  %37 = alloca [12 x i64], align 16
  %38 = alloca [12 x i64], align 16
  %39 = alloca i32, align 4
  %40 = alloca i32, align 4
  %41 = alloca i32, align 4
  %42 = alloca i32, align 4
  %43 = alloca i32, align 4
  %44 = alloca %struct.MaruArrayView, align 8
  %45 = alloca %struct.MaruArrayView, align 8
  %46 = alloca %struct.MaruArrayView, align 8
  %47 = alloca %struct.MaruArrayView, align 8
  %48 = alloca %struct.MaruArrayView, align 8
  %49 = alloca %struct.MaruArrayView, align 8
  %50 = alloca %struct.MaruArrayView, align 8
  %51 = alloca %struct.MaruArrayView, align 8
  %52 = alloca i32, align 4
  %53 = alloca i32, align 4
  %54 = alloca [5 x i64], align 16
  %55 = alloca [5 x i64], align 16
  %56 = alloca [3 x i64], align 16
  %57 = alloca [3 x i64], align 16
  %58 = alloca %struct.MaruArrayView, align 8
  %59 = alloca %struct.MaruArrayView, align 8
  %60 = alloca %struct.MaruArrayView, align 8
  %61 = alloca %struct.MaruArrayView, align 8
  %62 = alloca i32, align 4
  %63 = alloca [4 x i64], align 16
  %64 = alloca [4 x i64], align 16
  %65 = alloca [4 x i64], align 16
  %66 = alloca %struct.MaruArrayView, align 8
  %67 = alloca %struct.MaruArrayView, align 8
  %68 = alloca %struct.MaruArrayView, align 8
  %69 = alloca i64, align 8
  %70 = alloca i32, align 4
  %71 = alloca [4 x i64], align 16
  %72 = alloca [8 x i64], align 16
  %73 = alloca [4 x i64], align 16
  %74 = alloca [4 x i64], align 16
  %75 = alloca %struct.MaruArrayView, align 8
  %76 = alloca %struct.MaruArrayView, align 8
  %77 = alloca %struct.MaruArrayView, align 8
  %78 = alloca %struct.MaruArrayView, align 8
  %79 = alloca i64, align 8
  %80 = alloca i64, align 8
  %81 = alloca i32, align 4
  %82 = alloca [6 x i64], align 16
  %83 = alloca [3 x i64], align 16
  %84 = alloca [3 x i64], align 16
  %85 = alloca [6 x i64], align 16
  %86 = alloca %struct.MaruArrayView, align 8
  %87 = alloca %struct.MaruArrayView, align 8
  %88 = alloca %struct.MaruArrayView, align 8
  %89 = alloca %struct.MaruArrayView, align 8
  %90 = alloca i64, align 8
  %91 = alloca i32, align 4
  %92 = alloca [6 x i64], align 16
  %93 = alloca [6 x i64], align 16
  %94 = alloca %struct.MaruArrayView, align 8
  %95 = alloca %struct.MaruArrayView, align 8
  %96 = alloca i64, align 8
  %97 = alloca [4 x i64], align 16
  %98 = alloca [4 x i64], align 16
  %99 = alloca %struct.MaruArrayView, align 8
  %100 = alloca %struct.MaruArrayView, align 8
  %101 = alloca i64, align 8
  %102 = alloca i32, align 4
  %103 = alloca [3 x i64], align 16
  %104 = alloca [3 x i64], align 16
  %105 = alloca [4 x i64], align 16
  %106 = alloca %struct.MaruArrayView, align 8
  %107 = alloca %struct.MaruArrayView, align 8
  %108 = alloca %struct.MaruArrayView, align 8
  %109 = alloca i64, align 8
  %110 = alloca i32, align 4
  %111 = alloca [4 x i64], align 16
  %112 = alloca i64, align 8
  %113 = alloca i64, align 8
  %114 = alloca i64, align 8
  %115 = alloca i32, align 4
  %116 = alloca [4 x i64], align 16
  %117 = alloca [4 x i64], align 16
  %118 = alloca %struct.MaruArrayView, align 8
  %119 = alloca %struct.MaruArrayView, align 8
  %120 = alloca i32, align 4
  %121 = alloca [5 x i64], align 16
  %122 = alloca [8 x i64], align 16
  %123 = alloca [5 x i64], align 16
  %124 = alloca [5 x i64], align 16
  %125 = alloca %struct.MaruArrayView, align 8
  %126 = alloca %struct.MaruArrayView, align 8
  %127 = alloca %struct.MaruArrayView, align 8
  %128 = alloca %struct.MaruArrayView, align 8
  %129 = alloca i64, align 8
  %130 = alloca i64, align 8
  %131 = alloca i64, align 8
  %132 = alloca i32, align 4
  %133 = alloca i64, align 8
  %134 = alloca i64, align 8
  %135 = alloca i32, align 4
  %136 = alloca [4 x i64], align 16
  %137 = alloca [2 x i64], align 16
  %138 = alloca [2 x i64], align 16
  %139 = alloca %struct.MaruArrayView, align 8
  %140 = alloca %struct.MaruArrayView, align 8
  %141 = alloca %struct.MaruArrayView, align 8
  %142 = alloca i32, align 4
  %143 = alloca i64, align 8
  %144 = alloca i64, align 8
  %145 = alloca i64, align 8
  %146 = alloca i64, align 8
  %147 = alloca i32, align 4
  %148 = alloca [4 x i64], align 16
  %149 = alloca [2 x i64], align 16
  %150 = alloca [2 x i64], align 16
  %151 = alloca [2 x i64], align 16
  %152 = alloca %struct.MaruArrayView, align 8
  %153 = alloca %struct.MaruArrayView, align 8
  %154 = alloca %struct.MaruArrayView, align 8
  %155 = alloca %struct.MaruArrayView, align 8
  %156 = alloca i32, align 4
  %157 = alloca [9 x i64], align 16
  %158 = alloca [3 x i64], align 16
  %159 = alloca [3 x i64], align 16
  %160 = alloca [3 x i64], align 16
  %161 = alloca [3 x i64], align 16
  %162 = alloca [3 x i64], align 16
  %163 = alloca %struct.MaruArrayView, align 8
  %164 = alloca %struct.MaruArrayView, align 8
  %165 = alloca %struct.MaruArrayView, align 8
  %166 = alloca %struct.MaruArrayView, align 8
  %167 = alloca %struct.MaruArrayView, align 8
  %168 = alloca %struct.MaruArrayView, align 8
  %169 = alloca i64, align 8
  %170 = alloca i32, align 4
  %171 = alloca i32, align 4
  %172 = alloca [6 x i64], align 16
  %173 = alloca [3 x i64], align 16
  %174 = alloca [3 x i64], align 16
  %175 = alloca [3 x i64], align 16
  %176 = alloca [6 x i64], align 16
  %177 = alloca %struct.MaruArrayView, align 8
  %178 = alloca %struct.MaruArrayView, align 8
  %179 = alloca %struct.MaruArrayView, align 8
  %180 = alloca %struct.MaruArrayView, align 8
  %181 = alloca %struct.MaruArrayView, align 8
  %182 = alloca i64, align 8
  %183 = alloca i32, align 4
  %184 = alloca i32, align 4
  %185 = alloca i32, align 4
  %186 = alloca i64, align 8
  %187 = alloca i32, align 4
  store i32 0, ptr %1, align 4
  call void @llvm.memset.p0.i64(ptr align 16 %2, i8 0, i64 48, i1 false)
  %188 = getelementptr inbounds [6 x i64], ptr %2, i32 0, i32 0
  store i64 65536, ptr %188, align 16
  %189 = getelementptr inbounds [6 x i64], ptr %2, i32 0, i32 4
  store i64 65536, ptr %189, align 16
  call void @llvm.memcpy.p0.p0.i64(ptr align 16 %3, ptr align 16 @__const.main.x, i64 24, i1 false)
  call void @llvm.memcpy.p0.p0.i64(ptr align 16 %4, ptr align 16 @__const.main.b, i64 16, i1 false)
  %190 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %5, i32 0, i32 0
  %191 = getelementptr inbounds [6 x i64], ptr %2, i64 0, i64 0
  store ptr %191, ptr %190, align 8
  %192 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %5, i32 0, i32 1
  store i64 6, ptr %192, align 8
  %193 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %5, i32 0, i32 2
  store i64 8, ptr %193, align 8
  %194 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %5, i32 0, i32 3
  store i64 8, ptr %194, align 8
  %195 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %6, i32 0, i32 0
  %196 = getelementptr inbounds [3 x i64], ptr %3, i64 0, i64 0
  store ptr %196, ptr %195, align 8
  %197 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %6, i32 0, i32 1
  store i64 3, ptr %197, align 8
  %198 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %6, i32 0, i32 2
  store i64 8, ptr %198, align 8
  %199 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %6, i32 0, i32 3
  store i64 8, ptr %199, align 8
  %200 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %7, i32 0, i32 0
  %201 = getelementptr inbounds [2 x i64], ptr %4, i64 0, i64 0
  store ptr %201, ptr %200, align 8
  %202 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %7, i32 0, i32 1
  store i64 2, ptr %202, align 8
  %203 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %7, i32 0, i32 2
  store i64 8, ptr %203, align 8
  %204 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %7, i32 0, i32 3
  store i64 8, ptr %204, align 8
  %205 = getelementptr inbounds [2 x i64], ptr %8, i64 0, i64 0
  call void @matvec(ptr noundef %5, i64 noundef 2, i64 noundef 3, ptr noundef %6, ptr noundef %7, ptr noundef %205)
  %206 = call i64 @qmul(i64 noundef 65536, i64 noundef 65536)
  %207 = add nsw i64 100, %206
  store i64 %207, ptr %9, align 8
  %208 = call i64 @qmul(i64 noundef 65536, i64 noundef 131072)
  %209 = add nsw i64 200, %208
  store i64 %209, ptr %10, align 8
  %210 = getelementptr inbounds [2 x i64], ptr %8, i64 0, i64 0
  %211 = load i64, ptr %210, align 16
  %212 = load i64, ptr %9, align 8
  %213 = icmp eq i64 %211, %212
  br i1 %213, label %214, label %219

214:                                              ; preds = %0
  %215 = getelementptr inbounds [2 x i64], ptr %8, i64 0, i64 1
  %216 = load i64, ptr %215, align 8
  %217 = load i64, ptr %10, align 8
  %218 = icmp eq i64 %216, %217
  br label %219

219:                                              ; preds = %214, %0
  %220 = phi i1 [ false, %0 ], [ %218, %214 ]
  %221 = zext i1 %220 to i64
  %222 = select i1 %220, ptr @.str.1, ptr @.str.2
  %223 = getelementptr inbounds [2 x i64], ptr %8, i64 0, i64 0
  %224 = load i64, ptr %223, align 16
  %225 = getelementptr inbounds [2 x i64], ptr %8, i64 0, i64 1
  %226 = load i64, ptr %225, align 8
  %227 = call i32 (ptr, ...) @printf(ptr noundef @.str, ptr noundef %222, i64 noundef %224, i64 noundef %226)
  call void @llvm.memset.p0.i64(ptr align 16 %11, i8 0, i64 48, i1 false)
  %228 = getelementptr inbounds [6 x i64], ptr %11, i32 0, i32 0
  store i64 65536, ptr %228, align 16
  %229 = getelementptr inbounds [6 x i64], ptr %11, i32 0, i32 1
  store i64 131072, ptr %229, align 8
  %230 = getelementptr inbounds [6 x i64], ptr %11, i32 0, i32 2
  store i64 196608, ptr %230, align 16
  %231 = getelementptr inbounds [6 x i64], ptr %11, i32 0, i32 3
  store i64 131072, ptr %231, align 8
  %232 = getelementptr inbounds [6 x i64], ptr %11, i32 0, i32 4
  store i64 196608, ptr %232, align 16
  %233 = getelementptr inbounds [6 x i64], ptr %11, i32 0, i32 5
  store i64 262144, ptr %233, align 8
  %234 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %12, i32 0, i32 0
  %235 = getelementptr inbounds [6 x i64], ptr %11, i64 0, i64 0
  store ptr %235, ptr %234, align 8
  %236 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %12, i32 0, i32 1
  store i64 6, ptr %236, align 8
  %237 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %12, i32 0, i32 2
  store i64 8, ptr %237, align 8
  %238 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %12, i32 0, i32 3
  store i64 8, ptr %238, align 8
  %239 = getelementptr inbounds [4 x i64], ptr %13, i64 0, i64 0
  call void @batched(ptr noundef %5, i64 noundef 2, i64 noundef 3, ptr noundef %12, ptr noundef %7, i64 noundef 2, ptr noundef %239)
  %240 = getelementptr inbounds [4 x i64], ptr %13, i64 0, i64 0
  %241 = load i64, ptr %240, align 16
  %242 = load i64, ptr %9, align 8
  %243 = icmp eq i64 %241, %242
  br i1 %243, label %244, label %249

244:                                              ; preds = %219
  %245 = getelementptr inbounds [4 x i64], ptr %13, i64 0, i64 1
  %246 = load i64, ptr %245, align 8
  %247 = load i64, ptr %10, align 8
  %248 = icmp eq i64 %246, %247
  br label %249

249:                                              ; preds = %244, %219
  %250 = phi i1 [ false, %219 ], [ %248, %244 ]
  %251 = zext i1 %250 to i64
  %252 = select i1 %250, ptr @.str.1, ptr @.str.2
  %253 = call i32 (ptr, ...) @printf(ptr noundef @.str.3, ptr noundef %252)
  call void @llvm.memcpy.p0.p0.i64(ptr align 16 %14, ptr align 16 @__const.main.sx, i64 24, i1 false)
  %254 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %16, i32 0, i32 0
  %255 = getelementptr inbounds [3 x i64], ptr %14, i64 0, i64 0
  store ptr %255, ptr %254, align 8
  %256 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %16, i32 0, i32 1
  store i64 3, ptr %256, align 8
  %257 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %16, i32 0, i32 2
  store i64 8, ptr %257, align 8
  %258 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %16, i32 0, i32 3
  store i64 8, ptr %258, align 8
  %259 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %17, i32 0, i32 0
  %260 = getelementptr inbounds [3 x i64], ptr %15, i64 0, i64 0
  store ptr %260, ptr %259, align 8
  %261 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %17, i32 0, i32 1
  store i64 3, ptr %261, align 8
  %262 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %17, i32 0, i32 2
  store i64 8, ptr %262, align 8
  %263 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %17, i32 0, i32 3
  store i64 8, ptr %263, align 8
  call void @softmax(ptr noundef %16, i64 noundef 3, ptr noundef %17)
  store i64 0, ptr %18, align 8
  store i32 0, ptr %19, align 4
  br label %264

264:                                              ; preds = %274, %249
  %265 = load i32, ptr %19, align 4
  %266 = icmp slt i32 %265, 3
  br i1 %266, label %267, label %277

267:                                              ; preds = %264
  %268 = load i32, ptr %19, align 4
  %269 = sext i32 %268 to i64
  %270 = getelementptr inbounds [3 x i64], ptr %15, i64 0, i64 %269
  %271 = load i64, ptr %270, align 8
  %272 = load i64, ptr %18, align 8
  %273 = add nsw i64 %272, %271
  store i64 %273, ptr %18, align 8
  br label %274

274:                                              ; preds = %267
  %275 = load i32, ptr %19, align 4
  %276 = add nsw i32 %275, 1
  store i32 %276, ptr %19, align 4
  br label %264, !llvm.loop !5

277:                                              ; preds = %264
  %278 = load i64, ptr %18, align 8
  %279 = icmp sge i64 %278, 65534
  br i1 %279, label %280, label %283

280:                                              ; preds = %277
  %281 = load i64, ptr %18, align 8
  %282 = icmp sle i64 %281, 65538
  br label %283

283:                                              ; preds = %280, %277
  %284 = phi i1 [ false, %277 ], [ %282, %280 ]
  %285 = zext i1 %284 to i64
  %286 = select i1 %284, ptr @.str.1, ptr @.str.2
  %287 = load i64, ptr %18, align 8
  %288 = call i32 (ptr, ...) @printf(ptr noundef @.str.4, ptr noundef %286, i64 noundef %287)
  call void @llvm.memcpy.p0.p0.i64(ptr align 16 %20, ptr align 16 @__const.main.lx, i64 24, i1 false)
  call void @llvm.memcpy.p0.p0.i64(ptr align 16 %21, ptr align 16 @__const.main.g, i64 24, i1 false)
  call void @llvm.memset.p0.i64(ptr align 16 %22, i8 0, i64 24, i1 false)
  %289 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %24, i32 0, i32 0
  %290 = getelementptr inbounds [3 x i64], ptr %20, i64 0, i64 0
  store ptr %290, ptr %289, align 8
  %291 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %24, i32 0, i32 1
  store i64 3, ptr %291, align 8
  %292 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %24, i32 0, i32 2
  store i64 8, ptr %292, align 8
  %293 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %24, i32 0, i32 3
  store i64 8, ptr %293, align 8
  %294 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %25, i32 0, i32 0
  %295 = getelementptr inbounds [3 x i64], ptr %21, i64 0, i64 0
  store ptr %295, ptr %294, align 8
  %296 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %25, i32 0, i32 1
  store i64 3, ptr %296, align 8
  %297 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %25, i32 0, i32 2
  store i64 8, ptr %297, align 8
  %298 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %25, i32 0, i32 3
  store i64 8, ptr %298, align 8
  %299 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %26, i32 0, i32 0
  %300 = getelementptr inbounds [3 x i64], ptr %22, i64 0, i64 0
  store ptr %300, ptr %299, align 8
  %301 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %26, i32 0, i32 1
  store i64 3, ptr %301, align 8
  %302 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %26, i32 0, i32 2
  store i64 8, ptr %302, align 8
  %303 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %26, i32 0, i32 3
  store i64 8, ptr %303, align 8
  %304 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %27, i32 0, i32 0
  %305 = getelementptr inbounds [3 x i64], ptr %23, i64 0, i64 0
  store ptr %305, ptr %304, align 8
  %306 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %27, i32 0, i32 1
  store i64 3, ptr %306, align 8
  %307 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %27, i32 0, i32 2
  store i64 8, ptr %307, align 8
  %308 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %27, i32 0, i32 3
  store i64 8, ptr %308, align 8
  call void @layernorm(ptr noundef %24, i64 noundef 3, ptr noundef %25, ptr noundef %26, ptr noundef %27)
  store i64 0, ptr %28, align 8
  store i32 0, ptr %29, align 4
  br label %309

309:                                              ; preds = %319, %283
  %310 = load i32, ptr %29, align 4
  %311 = icmp slt i32 %310, 3
  br i1 %311, label %312, label %322

312:                                              ; preds = %309
  %313 = load i32, ptr %29, align 4
  %314 = sext i32 %313 to i64
  %315 = getelementptr inbounds [3 x i64], ptr %23, i64 0, i64 %314
  %316 = load i64, ptr %315, align 8
  %317 = load i64, ptr %28, align 8
  %318 = add nsw i64 %317, %316
  store i64 %318, ptr %28, align 8
  br label %319

319:                                              ; preds = %312
  %320 = load i32, ptr %29, align 4
  %321 = add nsw i32 %320, 1
  store i32 %321, ptr %29, align 4
  br label %309, !llvm.loop !7

322:                                              ; preds = %309
  %323 = load i64, ptr %28, align 8
  %324 = icmp slt i64 %323, 10
  br i1 %324, label %325, label %328

325:                                              ; preds = %322
  %326 = load i64, ptr %28, align 8
  %327 = icmp sgt i64 %326, -10
  br label %328

328:                                              ; preds = %325, %322
  %329 = phi i1 [ false, %322 ], [ %327, %325 ]
  %330 = zext i1 %329 to i64
  %331 = select i1 %329, ptr @.str.1, ptr @.str.2
  %332 = load i64, ptr %28, align 8
  %333 = call i32 (ptr, ...) @printf(ptr noundef @.str.5, ptr noundef %331, i64 noundef %332)
  store i32 0, ptr %39, align 4
  br label %334

334:                                              ; preds = %347, %328
  %335 = load i32, ptr %39, align 4
  %336 = icmp slt i32 %335, 12
  br i1 %336, label %337, label %350

337:                                              ; preds = %334
  %338 = load i32, ptr %39, align 4
  %339 = mul nsw i32 %338, 37
  %340 = srem i32 %339, 100
  %341 = sub nsw i32 %340, 50
  %342 = mul nsw i32 %341, 256
  %343 = sext i32 %342 to i64
  %344 = load i32, ptr %39, align 4
  %345 = sext i32 %344 to i64
  %346 = getelementptr inbounds [12 x i64], ptr %30, i64 0, i64 %345
  store i64 %343, ptr %346, align 8
  br label %347

347:                                              ; preds = %337
  %348 = load i32, ptr %39, align 4
  %349 = add nsw i32 %348, 1
  store i32 %349, ptr %39, align 4
  br label %334, !llvm.loop !8

350:                                              ; preds = %334
  store i32 0, ptr %40, align 4
  br label %351

351:                                              ; preds = %364, %350
  %352 = load i32, ptr %40, align 4
  %353 = icmp slt i32 %352, 48
  br i1 %353, label %354, label %367

354:                                              ; preds = %351
  %355 = load i32, ptr %40, align 4
  %356 = mul nsw i32 %355, 13
  %357 = srem i32 %356, 200
  %358 = sub nsw i32 %357, 100
  %359 = mul nsw i32 %358, 128
  %360 = sext i32 %359 to i64
  %361 = load i32, ptr %40, align 4
  %362 = sext i32 %361 to i64
  %363 = getelementptr inbounds [48 x i64], ptr %31, i64 0, i64 %362
  store i64 %360, ptr %363, align 8
  br label %364

364:                                              ; preds = %354
  %365 = load i32, ptr %40, align 4
  %366 = add nsw i32 %365, 1
  store i32 %366, ptr %40, align 4
  br label %351, !llvm.loop !9

367:                                              ; preds = %351
  store i32 0, ptr %41, align 4
  br label %368

368:                                              ; preds = %381, %367
  %369 = load i32, ptr %41, align 4
  %370 = icmp slt i32 %369, 12
  br i1 %370, label %371, label %384

371:                                              ; preds = %368
  %372 = load i32, ptr %41, align 4
  %373 = mul nsw i32 %372, 7
  %374 = srem i32 %373, 50
  %375 = sub nsw i32 %374, 25
  %376 = mul nsw i32 %375, 64
  %377 = sext i32 %376 to i64
  %378 = load i32, ptr %41, align 4
  %379 = sext i32 %378 to i64
  %380 = getelementptr inbounds [12 x i64], ptr %32, i64 0, i64 %379
  store i64 %377, ptr %380, align 8
  br label %381

381:                                              ; preds = %371
  %382 = load i32, ptr %41, align 4
  %383 = add nsw i32 %382, 1
  store i32 %383, ptr %41, align 4
  br label %368, !llvm.loop !10

384:                                              ; preds = %368
  store i32 0, ptr %42, align 4
  br label %385

385:                                              ; preds = %398, %384
  %386 = load i32, ptr %42, align 4
  %387 = icmp slt i32 %386, 16
  br i1 %387, label %388, label %401

388:                                              ; preds = %385
  %389 = load i32, ptr %42, align 4
  %390 = mul nsw i32 %389, 11
  %391 = srem i32 %390, 200
  %392 = sub nsw i32 %391, 100
  %393 = mul nsw i32 %392, 128
  %394 = sext i32 %393 to i64
  %395 = load i32, ptr %42, align 4
  %396 = sext i32 %395 to i64
  %397 = getelementptr inbounds [16 x i64], ptr %33, i64 0, i64 %396
  store i64 %394, ptr %397, align 8
  br label %398

398:                                              ; preds = %388
  %399 = load i32, ptr %42, align 4
  %400 = add nsw i32 %399, 1
  store i32 %400, ptr %42, align 4
  br label %385, !llvm.loop !11

401:                                              ; preds = %385
  store i32 0, ptr %43, align 4
  br label %402

402:                                              ; preds = %418, %401
  %403 = load i32, ptr %43, align 4
  %404 = icmp slt i32 %403, 4
  br i1 %404, label %405, label %421

405:                                              ; preds = %402
  %406 = load i32, ptr %43, align 4
  %407 = mul nsw i32 %406, 10
  %408 = sext i32 %407 to i64
  %409 = load i32, ptr %43, align 4
  %410 = sext i32 %409 to i64
  %411 = getelementptr inbounds [4 x i64], ptr %34, i64 0, i64 %410
  store i64 %408, ptr %411, align 8
  %412 = load i32, ptr %43, align 4
  %413 = sext i32 %412 to i64
  %414 = getelementptr inbounds [4 x i64], ptr %35, i64 0, i64 %413
  store i64 65536, ptr %414, align 8
  %415 = load i32, ptr %43, align 4
  %416 = sext i32 %415 to i64
  %417 = getelementptr inbounds [4 x i64], ptr %36, i64 0, i64 %416
  store i64 0, ptr %417, align 8
  br label %418

418:                                              ; preds = %405
  %419 = load i32, ptr %43, align 4
  %420 = add nsw i32 %419, 1
  store i32 %420, ptr %43, align 4
  br label %402, !llvm.loop !12

421:                                              ; preds = %402
  %422 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %44, i32 0, i32 0
  %423 = getelementptr inbounds [12 x i64], ptr %30, i64 0, i64 0
  store ptr %423, ptr %422, align 8
  %424 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %44, i32 0, i32 1
  store i64 12, ptr %424, align 8
  %425 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %44, i32 0, i32 2
  store i64 8, ptr %425, align 8
  %426 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %44, i32 0, i32 3
  store i64 8, ptr %426, align 8
  %427 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %45, i32 0, i32 0
  %428 = getelementptr inbounds [48 x i64], ptr %31, i64 0, i64 0
  store ptr %428, ptr %427, align 8
  %429 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %45, i32 0, i32 1
  store i64 48, ptr %429, align 8
  %430 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %45, i32 0, i32 2
  store i64 8, ptr %430, align 8
  %431 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %45, i32 0, i32 3
  store i64 8, ptr %431, align 8
  %432 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %46, i32 0, i32 0
  %433 = getelementptr inbounds [12 x i64], ptr %32, i64 0, i64 0
  store ptr %433, ptr %432, align 8
  %434 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %46, i32 0, i32 1
  store i64 12, ptr %434, align 8
  %435 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %46, i32 0, i32 2
  store i64 8, ptr %435, align 8
  %436 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %46, i32 0, i32 3
  store i64 8, ptr %436, align 8
  %437 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %47, i32 0, i32 0
  %438 = getelementptr inbounds [16 x i64], ptr %33, i64 0, i64 0
  store ptr %438, ptr %437, align 8
  %439 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %47, i32 0, i32 1
  store i64 16, ptr %439, align 8
  %440 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %47, i32 0, i32 2
  store i64 8, ptr %440, align 8
  %441 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %47, i32 0, i32 3
  store i64 8, ptr %441, align 8
  %442 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %48, i32 0, i32 0
  %443 = getelementptr inbounds [4 x i64], ptr %34, i64 0, i64 0
  store ptr %443, ptr %442, align 8
  %444 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %48, i32 0, i32 1
  store i64 4, ptr %444, align 8
  %445 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %48, i32 0, i32 2
  store i64 8, ptr %445, align 8
  %446 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %48, i32 0, i32 3
  store i64 8, ptr %446, align 8
  %447 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %49, i32 0, i32 0
  %448 = getelementptr inbounds [4 x i64], ptr %35, i64 0, i64 0
  store ptr %448, ptr %447, align 8
  %449 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %49, i32 0, i32 1
  store i64 4, ptr %449, align 8
  %450 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %49, i32 0, i32 2
  store i64 8, ptr %450, align 8
  %451 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %49, i32 0, i32 3
  store i64 8, ptr %451, align 8
  %452 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %50, i32 0, i32 0
  %453 = getelementptr inbounds [4 x i64], ptr %36, i64 0, i64 0
  store ptr %453, ptr %452, align 8
  %454 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %50, i32 0, i32 1
  store i64 4, ptr %454, align 8
  %455 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %50, i32 0, i32 2
  store i64 8, ptr %455, align 8
  %456 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %50, i32 0, i32 3
  store i64 8, ptr %456, align 8
  %457 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %51, i32 0, i32 0
  %458 = getelementptr inbounds [12 x i64], ptr %37, i64 0, i64 0
  store ptr %458, ptr %457, align 8
  %459 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %51, i32 0, i32 1
  store i64 12, ptr %459, align 8
  %460 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %51, i32 0, i32 2
  store i64 8, ptr %460, align 8
  %461 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %51, i32 0, i32 3
  store i64 8, ptr %461, align 8
  call void @fused_attention(ptr noundef %44, ptr noundef %45, ptr noundef %46, ptr noundef %47, ptr noundef %48, ptr noundef %49, ptr noundef %50, ptr noundef %51)
  %462 = getelementptr inbounds [12 x i64], ptr %30, i64 0, i64 0
  %463 = getelementptr inbounds [48 x i64], ptr %31, i64 0, i64 0
  %464 = getelementptr inbounds [12 x i64], ptr %32, i64 0, i64 0
  %465 = getelementptr inbounds [16 x i64], ptr %33, i64 0, i64 0
  %466 = getelementptr inbounds [4 x i64], ptr %34, i64 0, i64 0
  %467 = getelementptr inbounds [4 x i64], ptr %35, i64 0, i64 0
  %468 = getelementptr inbounds [4 x i64], ptr %36, i64 0, i64 0
  %469 = getelementptr inbounds [12 x i64], ptr %38, i64 0, i64 0
  call void @fused_attention_ref(ptr noundef %462, ptr noundef %463, ptr noundef %464, ptr noundef %465, ptr noundef %466, ptr noundef %467, ptr noundef %468, ptr noundef %469)
  store i32 1, ptr %52, align 4
  store i32 0, ptr %53, align 4
  br label %470

470:                                              ; preds = %495, %421
  %471 = load i32, ptr %53, align 4
  %472 = icmp slt i32 %471, 12
  br i1 %472, label %473, label %498

473:                                              ; preds = %470
  %474 = load i32, ptr %53, align 4
  %475 = sext i32 %474 to i64
  %476 = getelementptr inbounds [12 x i64], ptr %37, i64 0, i64 %475
  %477 = load i64, ptr %476, align 8
  %478 = load i32, ptr %53, align 4
  %479 = sext i32 %478 to i64
  %480 = getelementptr inbounds [12 x i64], ptr %38, i64 0, i64 %479
  %481 = load i64, ptr %480, align 8
  %482 = icmp ne i64 %477, %481
  br i1 %482, label %483, label %494

483:                                              ; preds = %473
  %484 = load i32, ptr %53, align 4
  %485 = load i32, ptr %53, align 4
  %486 = sext i32 %485 to i64
  %487 = getelementptr inbounds [12 x i64], ptr %37, i64 0, i64 %486
  %488 = load i64, ptr %487, align 8
  %489 = load i32, ptr %53, align 4
  %490 = sext i32 %489 to i64
  %491 = getelementptr inbounds [12 x i64], ptr %38, i64 0, i64 %490
  %492 = load i64, ptr %491, align 8
  %493 = call i32 (ptr, ...) @printf(ptr noundef @.str.6, i32 noundef %484, i64 noundef %488, i64 noundef %492)
  store i32 0, ptr %52, align 4
  br label %494

494:                                              ; preds = %483, %473
  br label %495

495:                                              ; preds = %494
  %496 = load i32, ptr %53, align 4
  %497 = add nsw i32 %496, 1
  store i32 %497, ptr %53, align 4
  br label %470, !llvm.loop !13

498:                                              ; preds = %470
  %499 = load i32, ptr %52, align 4
  %500 = icmp ne i32 %499, 0
  %501 = zext i1 %500 to i64
  %502 = select i1 %500, ptr @.str.1, ptr @.str.2
  %503 = call i32 (ptr, ...) @printf(ptr noundef @.str.7, ptr noundef %502)
  call void @llvm.memset.p0.i64(ptr align 16 %54, i8 0, i64 40, i1 false)
  %504 = getelementptr inbounds [5 x i64], ptr %54, i32 0, i32 0
  store i64 5, ptr %504, align 16
  %505 = getelementptr inbounds [5 x i64], ptr %54, i32 0, i32 1
  store i64 1, ptr %505, align 8
  %506 = getelementptr inbounds [5 x i64], ptr %54, i32 0, i32 2
  store i64 9, ptr %506, align 16
  %507 = getelementptr inbounds [5 x i64], ptr %54, i32 0, i32 3
  store i64 3, ptr %507, align 8
  %508 = getelementptr inbounds [5 x i64], ptr %54, i32 0, i32 4
  store i64 7, ptr %508, align 16
  call void @llvm.memset.p0.i64(ptr align 16 %55, i8 0, i64 40, i1 false)
  %509 = getelementptr inbounds [5 x i64], ptr %55, i32 0, i32 0
  store i64 10, ptr %509, align 16
  %510 = getelementptr inbounds [5 x i64], ptr %55, i32 0, i32 1
  store i64 11, ptr %510, align 8
  %511 = getelementptr inbounds [5 x i64], ptr %55, i32 0, i32 2
  store i64 12, ptr %511, align 16
  %512 = getelementptr inbounds [5 x i64], ptr %55, i32 0, i32 3
  store i64 13, ptr %512, align 8
  %513 = getelementptr inbounds [5 x i64], ptr %55, i32 0, i32 4
  store i64 14, ptr %513, align 16
  %514 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %58, i32 0, i32 0
  %515 = getelementptr inbounds [5 x i64], ptr %54, i64 0, i64 0
  store ptr %515, ptr %514, align 8
  %516 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %58, i32 0, i32 1
  store i64 5, ptr %516, align 8
  %517 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %58, i32 0, i32 2
  store i64 8, ptr %517, align 8
  %518 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %58, i32 0, i32 3
  store i64 8, ptr %518, align 8
  %519 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %59, i32 0, i32 0
  %520 = getelementptr inbounds [5 x i64], ptr %55, i64 0, i64 0
  store ptr %520, ptr %519, align 8
  %521 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %59, i32 0, i32 1
  store i64 5, ptr %521, align 8
  %522 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %59, i32 0, i32 2
  store i64 8, ptr %522, align 8
  %523 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %59, i32 0, i32 3
  store i64 8, ptr %523, align 8
  %524 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %60, i32 0, i32 0
  %525 = getelementptr inbounds [3 x i64], ptr %56, i64 0, i64 0
  store ptr %525, ptr %524, align 8
  %526 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %60, i32 0, i32 1
  store i64 3, ptr %526, align 8
  %527 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %60, i32 0, i32 2
  store i64 8, ptr %527, align 8
  %528 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %60, i32 0, i32 3
  store i64 8, ptr %528, align 8
  %529 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %61, i32 0, i32 0
  %530 = getelementptr inbounds [3 x i64], ptr %57, i64 0, i64 0
  store ptr %530, ptr %529, align 8
  %531 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %61, i32 0, i32 1
  store i64 3, ptr %531, align 8
  %532 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %61, i32 0, i32 2
  store i64 8, ptr %532, align 8
  %533 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %61, i32 0, i32 3
  store i64 8, ptr %533, align 8
  call void @topk(ptr noundef %58, i64 noundef 5, i64 noundef 3, ptr noundef %59, ptr noundef %60, ptr noundef %61)
  %534 = getelementptr inbounds [3 x i64], ptr %56, i64 0, i64 0
  %535 = load i64, ptr %534, align 16
  %536 = icmp eq i64 %535, 12
  br i1 %536, label %537, label %557

537:                                              ; preds = %498
  %538 = getelementptr inbounds [3 x i64], ptr %56, i64 0, i64 1
  %539 = load i64, ptr %538, align 8
  %540 = icmp eq i64 %539, 14
  br i1 %540, label %541, label %557

541:                                              ; preds = %537
  %542 = getelementptr inbounds [3 x i64], ptr %56, i64 0, i64 2
  %543 = load i64, ptr %542, align 16
  %544 = icmp eq i64 %543, 10
  br i1 %544, label %545, label %557

545:                                              ; preds = %541
  %546 = getelementptr inbounds [3 x i64], ptr %57, i64 0, i64 0
  %547 = load i64, ptr %546, align 16
  %548 = icmp eq i64 %547, 9
  br i1 %548, label %549, label %557

549:                                              ; preds = %545
  %550 = getelementptr inbounds [3 x i64], ptr %57, i64 0, i64 1
  %551 = load i64, ptr %550, align 8
  %552 = icmp eq i64 %551, 7
  br i1 %552, label %553, label %557

553:                                              ; preds = %549
  %554 = getelementptr inbounds [3 x i64], ptr %57, i64 0, i64 2
  %555 = load i64, ptr %554, align 16
  %556 = icmp eq i64 %555, 5
  br label %557

557:                                              ; preds = %553, %549, %545, %541, %537, %498
  %558 = phi i1 [ false, %549 ], [ false, %545 ], [ false, %541 ], [ false, %537 ], [ false, %498 ], [ %556, %553 ]
  %559 = zext i1 %558 to i32
  store i32 %559, ptr %62, align 4
  %560 = load i32, ptr %62, align 4
  %561 = icmp ne i32 %560, 0
  %562 = zext i1 %561 to i64
  %563 = select i1 %561, ptr @.str.1, ptr @.str.2
  %564 = call i32 (ptr, ...) @printf(ptr noundef @.str.8, ptr noundef %563)
  %565 = call i64 @argmax(ptr noundef %58, i64 noundef 5)
  %566 = icmp eq i64 %565, 2
  %567 = zext i1 %566 to i64
  %568 = select i1 %566, ptr @.str.1, ptr @.str.2
  %569 = call i32 (ptr, ...) @printf(ptr noundef @.str.9, ptr noundef %568)
  call void @llvm.memcpy.p0.p0.i64(ptr align 16 %63, ptr align 16 @__const.main.ms, i64 32, i1 false)
  call void @llvm.memcpy.p0.p0.i64(ptr align 16 %64, ptr align 16 @__const.main.mv, i64 32, i1 false)
  %570 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %66, i32 0, i32 0
  %571 = getelementptr inbounds [4 x i64], ptr %63, i64 0, i64 0
  store ptr %571, ptr %570, align 8
  %572 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %66, i32 0, i32 1
  store i64 4, ptr %572, align 8
  %573 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %66, i32 0, i32 2
  store i64 8, ptr %573, align 8
  %574 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %66, i32 0, i32 3
  store i64 8, ptr %574, align 8
  %575 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %67, i32 0, i32 0
  %576 = getelementptr inbounds [4 x i64], ptr %64, i64 0, i64 0
  store ptr %576, ptr %575, align 8
  %577 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %67, i32 0, i32 1
  store i64 4, ptr %577, align 8
  %578 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %67, i32 0, i32 2
  store i64 8, ptr %578, align 8
  %579 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %67, i32 0, i32 3
  store i64 8, ptr %579, align 8
  %580 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %68, i32 0, i32 0
  %581 = getelementptr inbounds [4 x i64], ptr %65, i64 0, i64 0
  store ptr %581, ptr %580, align 8
  %582 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %68, i32 0, i32 1
  store i64 4, ptr %582, align 8
  %583 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %68, i32 0, i32 2
  store i64 8, ptr %583, align 8
  %584 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %68, i32 0, i32 3
  store i64 8, ptr %584, align 8
  %585 = call i64 @mask_scores(ptr noundef %66, ptr noundef %67, i64 noundef 4, ptr noundef %68)
  store i64 %585, ptr %69, align 8
  %586 = load i64, ptr %69, align 8
  %587 = icmp eq i64 %586, 3
  br i1 %587, label %588, label %604

588:                                              ; preds = %557
  %589 = getelementptr inbounds [4 x i64], ptr %65, i64 0, i64 0
  %590 = load i64, ptr %589, align 16
  %591 = icmp eq i64 %590, 5
  br i1 %591, label %592, label %604

592:                                              ; preds = %588
  %593 = getelementptr inbounds [4 x i64], ptr %65, i64 0, i64 1
  %594 = load i64, ptr %593, align 8
  %595 = icmp eq i64 %594, -999999999
  br i1 %595, label %596, label %604

596:                                              ; preds = %592
  %597 = getelementptr inbounds [4 x i64], ptr %65, i64 0, i64 2
  %598 = load i64, ptr %597, align 16
  %599 = icmp eq i64 %598, 7
  br i1 %599, label %600, label %604

600:                                              ; preds = %596
  %601 = getelementptr inbounds [4 x i64], ptr %65, i64 0, i64 3
  %602 = load i64, ptr %601, align 8
  %603 = icmp eq i64 %602, 8
  br label %604

604:                                              ; preds = %600, %596, %592, %588, %557
  %605 = phi i1 [ false, %596 ], [ false, %592 ], [ false, %588 ], [ false, %557 ], [ %603, %600 ]
  %606 = zext i1 %605 to i32
  store i32 %606, ptr %70, align 4
  %607 = load i32, ptr %70, align 4
  %608 = icmp ne i32 %607, 0
  %609 = zext i1 %608 to i64
  %610 = select i1 %608, ptr @.str.1, ptr @.str.2
  %611 = load i64, ptr %69, align 8
  %612 = call i32 (ptr, ...) @printf(ptr noundef @.str.10, ptr noundef %610, i64 noundef %611)
  call void @llvm.memcpy.p0.p0.i64(ptr align 16 %71, ptr align 16 @__const.main.ik, i64 32, i1 false)
  %613 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %75, i32 0, i32 0
  %614 = getelementptr inbounds [4 x i64], ptr %71, i64 0, i64 0
  store ptr %614, ptr %613, align 8
  %615 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %75, i32 0, i32 1
  store i64 4, ptr %615, align 8
  %616 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %75, i32 0, i32 2
  store i64 8, ptr %616, align 8
  %617 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %75, i32 0, i32 3
  store i64 8, ptr %617, align 8
  %618 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %76, i32 0, i32 0
  %619 = getelementptr inbounds [8 x i64], ptr %72, i64 0, i64 0
  store ptr %619, ptr %618, align 8
  %620 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %76, i32 0, i32 1
  store i64 8, ptr %620, align 8
  %621 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %76, i32 0, i32 2
  store i64 8, ptr %621, align 8
  %622 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %76, i32 0, i32 3
  store i64 8, ptr %622, align 8
  %623 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %77, i32 0, i32 0
  %624 = getelementptr inbounds [4 x i64], ptr %73, i64 0, i64 0
  store ptr %624, ptr %623, align 8
  %625 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %77, i32 0, i32 1
  store i64 4, ptr %625, align 8
  %626 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %77, i32 0, i32 2
  store i64 8, ptr %626, align 8
  %627 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %77, i32 0, i32 3
  store i64 8, ptr %627, align 8
  %628 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %78, i32 0, i32 0
  %629 = getelementptr inbounds [4 x i64], ptr %74, i64 0, i64 0
  store ptr %629, ptr %628, align 8
  %630 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %78, i32 0, i32 1
  store i64 4, ptr %630, align 8
  %631 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %78, i32 0, i32 2
  store i64 8, ptr %631, align 8
  %632 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %78, i32 0, i32 3
  store i64 8, ptr %632, align 8
  call void @build_index(ptr noundef %75, i64 noundef 4, i64 noundef 8, ptr noundef %76, ptr noundef %77)
  %633 = call i64 @index_lookup(ptr noundef %75, i64 noundef 4, ptr noundef %76, i64 noundef 8, ptr noundef %77, i64 noundef 3, ptr noundef %78)
  store i64 %633, ptr %79, align 8
  %634 = call i64 @index_lookup(ptr noundef %75, i64 noundef 4, ptr noundef %76, i64 noundef 8, ptr noundef %77, i64 noundef 9, ptr noundef %78)
  store i64 %634, ptr %80, align 8
  %635 = load i64, ptr %79, align 8
  %636 = icmp eq i64 %635, 2
  br i1 %636, label %637, label %644

637:                                              ; preds = %604
  %638 = load i64, ptr %80, align 8
  %639 = icmp eq i64 %638, 1
  br i1 %639, label %640, label %644

640:                                              ; preds = %637
  %641 = getelementptr inbounds [4 x i64], ptr %74, i64 0, i64 0
  %642 = load i64, ptr %641, align 16
  %643 = icmp eq i64 %642, 3
  br label %644

644:                                              ; preds = %640, %637, %604
  %645 = phi i1 [ false, %637 ], [ false, %604 ], [ %643, %640 ]
  %646 = zext i1 %645 to i32
  store i32 %646, ptr %81, align 4
  %647 = load i32, ptr %81, align 4
  %648 = icmp ne i32 %647, 0
  %649 = zext i1 %648 to i64
  %650 = select i1 %648, ptr @.str.1, ptr @.str.2
  %651 = load i64, ptr %79, align 8
  %652 = load i64, ptr %80, align 8
  %653 = call i32 (ptr, ...) @printf(ptr noundef @.str.11, ptr noundef %650, i64 noundef %651, i64 noundef %652)
  call void @llvm.memset.p0.i64(ptr align 16 %82, i8 0, i64 48, i1 false)
  %654 = getelementptr inbounds [6 x i64], ptr %82, i32 0, i32 0
  store i64 1, ptr %654, align 16
  %655 = getelementptr inbounds [6 x i64], ptr %82, i32 0, i32 1
  store i64 1, ptr %655, align 8
  call void @llvm.memcpy.p0.p0.i64(ptr align 16 %83, ptr align 16 @__const.main.pfh, i64 24, i1 false)
  call void @llvm.memcpy.p0.p0.i64(ptr align 16 %84, ptr align 16 @__const.main.pfm, i64 24, i1 false)
  %656 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %86, i32 0, i32 0
  %657 = getelementptr inbounds [6 x i64], ptr %82, i64 0, i64 0
  store ptr %657, ptr %656, align 8
  %658 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %86, i32 0, i32 1
  store i64 6, ptr %658, align 8
  %659 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %86, i32 0, i32 2
  store i64 8, ptr %659, align 8
  %660 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %86, i32 0, i32 3
  store i64 8, ptr %660, align 8
  %661 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %87, i32 0, i32 0
  %662 = getelementptr inbounds [3 x i64], ptr %83, i64 0, i64 0
  store ptr %662, ptr %661, align 8
  %663 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %87, i32 0, i32 1
  store i64 3, ptr %663, align 8
  %664 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %87, i32 0, i32 2
  store i64 8, ptr %664, align 8
  %665 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %87, i32 0, i32 3
  store i64 8, ptr %665, align 8
  %666 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %88, i32 0, i32 0
  %667 = getelementptr inbounds [3 x i64], ptr %84, i64 0, i64 0
  store ptr %667, ptr %666, align 8
  %668 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %88, i32 0, i32 1
  store i64 3, ptr %668, align 8
  %669 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %88, i32 0, i32 2
  store i64 8, ptr %669, align 8
  %670 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %88, i32 0, i32 3
  store i64 8, ptr %670, align 8
  %671 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %89, i32 0, i32 0
  %672 = getelementptr inbounds [6 x i64], ptr %85, i64 0, i64 0
  store ptr %672, ptr %671, align 8
  %673 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %89, i32 0, i32 1
  store i64 6, ptr %673, align 8
  %674 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %89, i32 0, i32 2
  store i64 8, ptr %674, align 8
  %675 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %89, i32 0, i32 3
  store i64 8, ptr %675, align 8
  %676 = call i64 @frontier_closure(ptr noundef %86, i64 noundef 6, ptr noundef %87, ptr noundef %88, i64 noundef 3, ptr noundef %89)
  store i64 %676, ptr %90, align 8
  %677 = load i64, ptr %90, align 8
  %678 = icmp eq i64 %677, 2
  br i1 %678, label %679, label %687

679:                                              ; preds = %644
  %680 = getelementptr inbounds [6 x i64], ptr %85, i64 0, i64 0
  %681 = load i64, ptr %680, align 16
  %682 = icmp eq i64 %681, 2
  br i1 %682, label %683, label %687

683:                                              ; preds = %679
  %684 = getelementptr inbounds [6 x i64], ptr %85, i64 0, i64 1
  %685 = load i64, ptr %684, align 8
  %686 = icmp eq i64 %685, 3
  br label %687

687:                                              ; preds = %683, %679, %644
  %688 = phi i1 [ false, %679 ], [ false, %644 ], [ %686, %683 ]
  %689 = zext i1 %688 to i32
  store i32 %689, ptr %91, align 4
  %690 = load i32, ptr %91, align 4
  %691 = icmp ne i32 %690, 0
  %692 = zext i1 %691 to i64
  %693 = select i1 %691, ptr @.str.1, ptr @.str.2
  %694 = load i64, ptr %90, align 8
  %695 = call i32 (ptr, ...) @printf(ptr noundef @.str.12, ptr noundef %693, i64 noundef %694)
  call void @llvm.memset.p0.i64(ptr align 16 %92, i8 0, i64 48, i1 false)
  %696 = getelementptr inbounds [6 x i64], ptr %92, i32 0, i32 0
  store i64 1, ptr %696, align 16
  %697 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %94, i32 0, i32 0
  %698 = getelementptr inbounds [6 x i64], ptr %92, i64 0, i64 0
  store ptr %698, ptr %697, align 8
  %699 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %94, i32 0, i32 1
  store i64 6, ptr %699, align 8
  %700 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %94, i32 0, i32 2
  store i64 8, ptr %700, align 8
  %701 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %94, i32 0, i32 3
  store i64 8, ptr %701, align 8
  %702 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %95, i32 0, i32 0
  %703 = getelementptr inbounds [6 x i64], ptr %93, i64 0, i64 0
  store ptr %703, ptr %702, align 8
  %704 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %95, i32 0, i32 1
  store i64 6, ptr %704, align 8
  %705 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %95, i32 0, i32 2
  store i64 8, ptr %705, align 8
  %706 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %95, i32 0, i32 3
  store i64 8, ptr %706, align 8
  %707 = call i64 @frontier_missing(ptr noundef %94, i64 noundef 6, ptr noundef %87, ptr noundef %88, i64 noundef 3, ptr noundef %95)
  store i64 %707, ptr %96, align 8
  %708 = load i64, ptr %96, align 8
  %709 = icmp eq i64 %708, 6
  br i1 %709, label %710, label %718

710:                                              ; preds = %687
  %711 = getelementptr inbounds [6 x i64], ptr %93, i64 0, i64 0
  %712 = load i64, ptr %711, align 16
  %713 = icmp eq i64 %712, 1
  br i1 %713, label %714, label %718

714:                                              ; preds = %710
  %715 = getelementptr inbounds [6 x i64], ptr %93, i64 0, i64 1
  %716 = load i64, ptr %715, align 8
  %717 = icmp eq i64 %716, 2
  br label %718

718:                                              ; preds = %714, %710, %687
  %719 = phi i1 [ false, %710 ], [ false, %687 ], [ %717, %714 ]
  %720 = zext i1 %719 to i64
  %721 = select i1 %719, ptr @.str.1, ptr @.str.2
  %722 = load i64, ptr %96, align 8
  %723 = call i32 (ptr, ...) @printf(ptr noundef @.str.13, ptr noundef %721, i64 noundef %722)
  call void @llvm.memcpy.p0.p0.i64(ptr align 16 %97, ptr align 16 @__const.main.ba, i64 32, i1 false)
  %724 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %99, i32 0, i32 0
  %725 = getelementptr inbounds [4 x i64], ptr %97, i64 0, i64 0
  store ptr %725, ptr %724, align 8
  %726 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %99, i32 0, i32 1
  store i64 4, ptr %726, align 8
  %727 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %99, i32 0, i32 2
  store i64 8, ptr %727, align 8
  %728 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %99, i32 0, i32 3
  store i64 8, ptr %728, align 8
  %729 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %100, i32 0, i32 0
  %730 = getelementptr inbounds [4 x i64], ptr %98, i64 0, i64 0
  store ptr %730, ptr %729, align 8
  %731 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %100, i32 0, i32 1
  store i64 4, ptr %731, align 8
  %732 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %100, i32 0, i32 2
  store i64 8, ptr %732, align 8
  %733 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %100, i32 0, i32 3
  store i64 8, ptr %733, align 8
  %734 = call i64 @bfs(ptr noundef %99, i64 noundef 4, i64 noundef 0, ptr noundef %100)
  store i64 %734, ptr %101, align 8
  %735 = load i64, ptr %101, align 8
  %736 = icmp eq i64 %735, 3
  br i1 %736, label %737, label %749

737:                                              ; preds = %718
  %738 = getelementptr inbounds [4 x i64], ptr %98, i64 0, i64 0
  %739 = load i64, ptr %738, align 16
  %740 = icmp eq i64 %739, 0
  br i1 %740, label %741, label %749

741:                                              ; preds = %737
  %742 = getelementptr inbounds [4 x i64], ptr %98, i64 0, i64 1
  %743 = load i64, ptr %742, align 8
  %744 = icmp eq i64 %743, 1
  br i1 %744, label %745, label %749

745:                                              ; preds = %741
  %746 = getelementptr inbounds [4 x i64], ptr %98, i64 0, i64 2
  %747 = load i64, ptr %746, align 16
  %748 = icmp eq i64 %747, 2
  br label %749

749:                                              ; preds = %745, %741, %737, %718
  %750 = phi i1 [ false, %741 ], [ false, %737 ], [ false, %718 ], [ %748, %745 ]
  %751 = zext i1 %750 to i32
  store i32 %751, ptr %102, align 4
  %752 = load i32, ptr %102, align 4
  %753 = icmp ne i32 %752, 0
  %754 = zext i1 %753 to i64
  %755 = select i1 %753, ptr @.str.1, ptr @.str.2
  %756 = load i64, ptr %101, align 8
  %757 = call i32 (ptr, ...) @printf(ptr noundef @.str.14, ptr noundef %755, i64 noundef %756)
  call void @llvm.memcpy.p0.p0.i64(ptr align 16 %103, ptr align 16 @__const.main.ptu, i64 24, i1 false)
  call void @llvm.memcpy.p0.p0.i64(ptr align 16 %104, ptr align 16 @__const.main.ptv, i64 24, i1 false)
  %758 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %106, i32 0, i32 0
  %759 = getelementptr inbounds [3 x i64], ptr %103, i64 0, i64 0
  store ptr %759, ptr %758, align 8
  %760 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %106, i32 0, i32 1
  store i64 3, ptr %760, align 8
  %761 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %106, i32 0, i32 2
  store i64 8, ptr %761, align 8
  %762 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %106, i32 0, i32 3
  store i64 8, ptr %762, align 8
  %763 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %107, i32 0, i32 0
  %764 = getelementptr inbounds [3 x i64], ptr %104, i64 0, i64 0
  store ptr %764, ptr %763, align 8
  %765 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %107, i32 0, i32 1
  store i64 3, ptr %765, align 8
  %766 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %107, i32 0, i32 2
  store i64 8, ptr %766, align 8
  %767 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %107, i32 0, i32 3
  store i64 8, ptr %767, align 8
  %768 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %108, i32 0, i32 0
  %769 = getelementptr inbounds [4 x i64], ptr %105, i64 0, i64 0
  store ptr %769, ptr %768, align 8
  %770 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %108, i32 0, i32 1
  store i64 4, ptr %770, align 8
  %771 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %108, i32 0, i32 2
  store i64 8, ptr %771, align 8
  %772 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %108, i32 0, i32 3
  store i64 8, ptr %772, align 8
  %773 = call i64 @topo(ptr noundef %106, ptr noundef %107, i64 noundef 3, i64 noundef 4, ptr noundef %108)
  store i64 %773, ptr %109, align 8
  %774 = load i64, ptr %109, align 8
  %775 = icmp eq i64 %774, 4
  br i1 %775, label %776, label %780

776:                                              ; preds = %749
  %777 = getelementptr inbounds [4 x i64], ptr %105, i64 0, i64 0
  %778 = load i64, ptr %777, align 16
  %779 = icmp eq i64 %778, 0
  br label %780

780:                                              ; preds = %776, %749
  %781 = phi i1 [ false, %749 ], [ %779, %776 ]
  %782 = zext i1 %781 to i32
  store i32 %782, ptr %110, align 4
  %783 = load i32, ptr %110, align 4
  %784 = icmp ne i32 %783, 0
  %785 = zext i1 %784 to i64
  %786 = select i1 %784, ptr @.str.1, ptr @.str.2
  %787 = load i64, ptr %109, align 8
  %788 = call i32 (ptr, ...) @printf(ptr noundef @.str.15, ptr noundef %786, i64 noundef %787)
  call void @llvm.memcpy.p0.p0.i64(ptr align 16 %111, ptr align 16 @__const.main.pp, i64 32, i1 false)
  %789 = getelementptr inbounds [4 x i64], ptr %111, i64 0, i64 0
  %790 = call i64 @uf_union(ptr noundef %789, i64 noundef 0, i64 noundef 1)
  store i64 %790, ptr %112, align 8
  %791 = getelementptr inbounds [4 x i64], ptr %111, i64 0, i64 0
  %792 = call i64 @uf_union(ptr noundef %791, i64 noundef 2, i64 noundef 3)
  store i64 %792, ptr %113, align 8
  %793 = getelementptr inbounds [4 x i64], ptr %111, i64 0, i64 0
  %794 = call i64 @uf_union(ptr noundef %793, i64 noundef 1, i64 noundef 2)
  store i64 %794, ptr %114, align 8
  %795 = load i64, ptr %112, align 8
  %796 = icmp eq i64 %795, 1
  br i1 %796, label %797, label %809

797:                                              ; preds = %780
  %798 = load i64, ptr %113, align 8
  %799 = icmp eq i64 %798, 1
  br i1 %799, label %800, label %809

800:                                              ; preds = %797
  %801 = load i64, ptr %114, align 8
  %802 = icmp eq i64 %801, 1
  br i1 %802, label %803, label %809

803:                                              ; preds = %800
  %804 = getelementptr inbounds [4 x i64], ptr %111, i64 0, i64 0
  %805 = call i64 @uf_find(ptr noundef %804, i64 noundef 0)
  %806 = getelementptr inbounds [4 x i64], ptr %111, i64 0, i64 0
  %807 = call i64 @uf_find(ptr noundef %806, i64 noundef 3)
  %808 = icmp eq i64 %805, %807
  br label %809

809:                                              ; preds = %803, %800, %797, %780
  %810 = phi i1 [ false, %800 ], [ false, %797 ], [ false, %780 ], [ %808, %803 ]
  %811 = zext i1 %810 to i32
  store i32 %811, ptr %115, align 4
  %812 = load i32, ptr %115, align 4
  %813 = icmp ne i32 %812, 0
  %814 = zext i1 %813 to i64
  %815 = select i1 %813, ptr @.str.1, ptr @.str.2
  %816 = call i32 (ptr, ...) @printf(ptr noundef @.str.16, ptr noundef %815)
  call void @llvm.memcpy.p0.p0.i64(ptr align 16 %116, ptr align 16 @__const.main.ca, i64 32, i1 false)
  %817 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %118, i32 0, i32 0
  %818 = getelementptr inbounds [4 x i64], ptr %116, i64 0, i64 0
  store ptr %818, ptr %817, align 8
  %819 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %118, i32 0, i32 1
  store i64 4, ptr %819, align 8
  %820 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %118, i32 0, i32 2
  store i64 8, ptr %820, align 8
  %821 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %118, i32 0, i32 3
  store i64 8, ptr %821, align 8
  %822 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %119, i32 0, i32 0
  %823 = getelementptr inbounds [4 x i64], ptr %117, i64 0, i64 0
  store ptr %823, ptr %822, align 8
  %824 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %119, i32 0, i32 1
  store i64 4, ptr %824, align 8
  %825 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %119, i32 0, i32 2
  store i64 8, ptr %825, align 8
  %826 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %119, i32 0, i32 3
  store i64 8, ptr %826, align 8
  call void @bitset_closure(ptr noundef %118, i64 noundef 4, ptr noundef %119)
  %827 = getelementptr inbounds [4 x i64], ptr %117, i64 0, i64 0
  %828 = load i64, ptr %827, align 16
  %829 = icmp eq i64 %828, 6
  br i1 %829, label %830, label %834

830:                                              ; preds = %809
  %831 = getelementptr inbounds [4 x i64], ptr %117, i64 0, i64 1
  %832 = load i64, ptr %831, align 8
  %833 = icmp eq i64 %832, 4
  br label %834

834:                                              ; preds = %830, %809
  %835 = phi i1 [ false, %809 ], [ %833, %830 ]
  %836 = zext i1 %835 to i32
  store i32 %836, ptr %120, align 4
  %837 = load i32, ptr %120, align 4
  %838 = icmp ne i32 %837, 0
  %839 = zext i1 %838 to i64
  %840 = select i1 %838, ptr @.str.1, ptr @.str.2
  %841 = call i32 (ptr, ...) @printf(ptr noundef @.str.17, ptr noundef %840)
  call void @llvm.memset.p0.i64(ptr align 16 %121, i8 0, i64 40, i1 false)
  %842 = getelementptr inbounds [5 x i64], ptr %121, i32 0, i32 0
  store i64 3, ptr %842, align 16
  %843 = getelementptr inbounds [5 x i64], ptr %121, i32 0, i32 1
  store i64 7, ptr %843, align 8
  %844 = getelementptr inbounds [5 x i64], ptr %121, i32 0, i32 2
  store i64 3, ptr %844, align 16
  %845 = getelementptr inbounds [5 x i64], ptr %121, i32 0, i32 3
  store i64 9, ptr %845, align 8
  %846 = getelementptr inbounds [5 x i64], ptr %121, i32 0, i32 4
  store i64 -1, ptr %846, align 16
  %847 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %125, i32 0, i32 0
  %848 = getelementptr inbounds [5 x i64], ptr %121, i64 0, i64 0
  store ptr %848, ptr %847, align 8
  %849 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %125, i32 0, i32 1
  store i64 5, ptr %849, align 8
  %850 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %125, i32 0, i32 2
  store i64 8, ptr %850, align 8
  %851 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %125, i32 0, i32 3
  store i64 8, ptr %851, align 8
  %852 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %126, i32 0, i32 0
  %853 = getelementptr inbounds [8 x i64], ptr %122, i64 0, i64 0
  store ptr %853, ptr %852, align 8
  %854 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %126, i32 0, i32 1
  store i64 8, ptr %854, align 8
  %855 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %126, i32 0, i32 2
  store i64 8, ptr %855, align 8
  %856 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %126, i32 0, i32 3
  store i64 8, ptr %856, align 8
  %857 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %127, i32 0, i32 0
  %858 = getelementptr inbounds [5 x i64], ptr %123, i64 0, i64 0
  store ptr %858, ptr %857, align 8
  %859 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %127, i32 0, i32 1
  store i64 5, ptr %859, align 8
  %860 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %127, i32 0, i32 2
  store i64 8, ptr %860, align 8
  %861 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %127, i32 0, i32 3
  store i64 8, ptr %861, align 8
  %862 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %128, i32 0, i32 0
  %863 = getelementptr inbounds [5 x i64], ptr %124, i64 0, i64 0
  store ptr %863, ptr %862, align 8
  %864 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %128, i32 0, i32 1
  store i64 5, ptr %864, align 8
  %865 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %128, i32 0, i32 2
  store i64 8, ptr %865, align 8
  %866 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %128, i32 0, i32 3
  store i64 8, ptr %866, align 8
  call void @build_index(ptr noundef %125, i64 noundef 4, i64 noundef 8, ptr noundef %126, ptr noundef %127)
  call void @index_add(ptr noundef %125, ptr noundef %126, i64 noundef 8, ptr noundef %127, i64 noundef 4, i64 noundef 3)
  %867 = call i64 @index_lookup(ptr noundef %125, i64 noundef 5, ptr noundef %126, i64 noundef 8, ptr noundef %127, i64 noundef 3, ptr noundef %128)
  store i64 %867, ptr %129, align 8
  %868 = call i64 @index_remove(ptr noundef %125, i64 noundef 0)
  store i64 %868, ptr %130, align 8
  %869 = call i64 @index_lookup(ptr noundef %125, i64 noundef 5, ptr noundef %126, i64 noundef 8, ptr noundef %127, i64 noundef 3, ptr noundef %128)
  store i64 %869, ptr %131, align 8
  %870 = load i64, ptr %129, align 8
  %871 = icmp eq i64 %870, 3
  br i1 %871, label %872, label %878

872:                                              ; preds = %834
  %873 = load i64, ptr %130, align 8
  %874 = icmp eq i64 %873, 3
  br i1 %874, label %875, label %878

875:                                              ; preds = %872
  %876 = load i64, ptr %131, align 8
  %877 = icmp eq i64 %876, 2
  br label %878

878:                                              ; preds = %875, %872, %834
  %879 = phi i1 [ false, %872 ], [ false, %834 ], [ %877, %875 ]
  %880 = zext i1 %879 to i32
  store i32 %880, ptr %132, align 4
  %881 = load i32, ptr %132, align 4
  %882 = icmp ne i32 %881, 0
  %883 = zext i1 %882 to i64
  %884 = select i1 %882, ptr @.str.1, ptr @.str.2
  %885 = load i64, ptr %129, align 8
  %886 = load i64, ptr %130, align 8
  %887 = load i64, ptr %131, align 8
  %888 = call i32 (ptr, ...) @printf(ptr noundef @.str.18, ptr noundef %884, i64 noundef %885, i64 noundef %886, i64 noundef %887)
  %889 = call i64 @bce_q16(i64 noundef 0, i64 noundef 65536)
  store i64 %889, ptr %133, align 8
  %890 = call i64 @bce_q16(i64 noundef 0, i64 noundef 0)
  store i64 %890, ptr %134, align 8
  %891 = load i64, ptr %133, align 8
  %892 = icmp sgt i64 %891, 45000
  br i1 %892, label %893, label %902

893:                                              ; preds = %878
  %894 = load i64, ptr %133, align 8
  %895 = icmp slt i64 %894, 46000
  br i1 %895, label %896, label %902

896:                                              ; preds = %893
  %897 = load i64, ptr %134, align 8
  %898 = icmp sgt i64 %897, 45000
  br i1 %898, label %899, label %902

899:                                              ; preds = %896
  %900 = load i64, ptr %134, align 8
  %901 = icmp slt i64 %900, 46000
  br label %902

902:                                              ; preds = %899, %896, %893, %878
  %903 = phi i1 [ false, %896 ], [ false, %893 ], [ false, %878 ], [ %901, %899 ]
  %904 = zext i1 %903 to i32
  store i32 %904, ptr %135, align 4
  %905 = load i32, ptr %135, align 4
  %906 = icmp ne i32 %905, 0
  %907 = zext i1 %906 to i64
  %908 = select i1 %906, ptr @.str.1, ptr @.str.2
  %909 = load i64, ptr %133, align 8
  %910 = load i64, ptr %134, align 8
  %911 = call i32 (ptr, ...) @printf(ptr noundef @.str.19, ptr noundef %908, i64 noundef %909, i64 noundef %910)
  call void @llvm.memcpy.p0.p0.i64(ptr align 16 %136, ptr align 16 @__const.main.bw, i64 32, i1 false)
  call void @llvm.memcpy.p0.p0.i64(ptr align 16 %137, ptr align 16 @__const.main.bdy, i64 16, i1 false)
  %912 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %139, i32 0, i32 0
  %913 = getelementptr inbounds [4 x i64], ptr %136, i64 0, i64 0
  store ptr %913, ptr %912, align 8
  %914 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %139, i32 0, i32 1
  store i64 4, ptr %914, align 8
  %915 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %139, i32 0, i32 2
  store i64 8, ptr %915, align 8
  %916 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %139, i32 0, i32 3
  store i64 8, ptr %916, align 8
  %917 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %140, i32 0, i32 0
  %918 = getelementptr inbounds [2 x i64], ptr %137, i64 0, i64 0
  store ptr %918, ptr %917, align 8
  %919 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %140, i32 0, i32 1
  store i64 2, ptr %919, align 8
  %920 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %140, i32 0, i32 2
  store i64 8, ptr %920, align 8
  %921 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %140, i32 0, i32 3
  store i64 8, ptr %921, align 8
  %922 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %141, i32 0, i32 0
  %923 = getelementptr inbounds [2 x i64], ptr %138, i64 0, i64 0
  store ptr %923, ptr %922, align 8
  %924 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %141, i32 0, i32 1
  store i64 2, ptr %924, align 8
  %925 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %141, i32 0, i32 2
  store i64 8, ptr %925, align 8
  %926 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %141, i32 0, i32 3
  store i64 8, ptr %926, align 8
  call void @backward_matvec(ptr noundef %139, i64 noundef 2, i64 noundef 2, ptr noundef %140, ptr noundef %141)
  %927 = getelementptr inbounds [2 x i64], ptr %138, i64 0, i64 0
  %928 = load i64, ptr %927, align 16
  %929 = icmp eq i64 %928, 131072
  br i1 %929, label %930, label %934

930:                                              ; preds = %902
  %931 = getelementptr inbounds [2 x i64], ptr %138, i64 0, i64 1
  %932 = load i64, ptr %931, align 8
  %933 = icmp eq i64 %932, 196608
  br label %934

934:                                              ; preds = %930, %902
  %935 = phi i1 [ false, %902 ], [ %933, %930 ]
  %936 = zext i1 %935 to i32
  store i32 %936, ptr %142, align 4
  %937 = load i32, ptr %142, align 4
  %938 = icmp ne i32 %937, 0
  %939 = zext i1 %938 to i64
  %940 = select i1 %938, ptr @.str.1, ptr @.str.2
  %941 = call i32 (ptr, ...) @printf(ptr noundef @.str.20, ptr noundef %940)
  store i64 0, ptr %143, align 8
  store i64 0, ptr %144, align 8
  store i64 6553600, ptr %145, align 8
  store i64 1, ptr %146, align 8
  br label %942

942:                                              ; preds = %949, %934
  %943 = load i64, ptr %146, align 8
  %944 = icmp sle i64 %943, 3
  br i1 %944, label %945, label %952

945:                                              ; preds = %942
  %946 = load i64, ptr %145, align 8
  %947 = load i64, ptr %146, align 8
  %948 = call i64 @adam_step(i64 noundef %946, i64 noundef 655360, ptr noundef %143, ptr noundef %144, i64 noundef %947, i64 noundef 3277, i64 noundef 58982, i64 noundef 64225, i64 noundef 655)
  store i64 %948, ptr %145, align 8
  br label %949

949:                                              ; preds = %945
  %950 = load i64, ptr %146, align 8
  %951 = add nsw i64 %950, 1
  store i64 %951, ptr %146, align 8
  br label %942, !llvm.loop !14

952:                                              ; preds = %942
  %953 = load i64, ptr %145, align 8
  %954 = icmp slt i64 %953, 6553600
  br i1 %954, label %955, label %958

955:                                              ; preds = %952
  %956 = load i64, ptr %145, align 8
  %957 = icmp sgt i64 %956, 0
  br label %958

958:                                              ; preds = %955, %952
  %959 = phi i1 [ false, %952 ], [ %957, %955 ]
  %960 = zext i1 %959 to i32
  store i32 %960, ptr %147, align 4
  %961 = load i32, ptr %147, align 4
  %962 = icmp ne i32 %961, 0
  %963 = zext i1 %962 to i64
  %964 = select i1 %962, ptr @.str.1, ptr @.str.2
  %965 = load i64, ptr %145, align 8
  %966 = call i32 (ptr, ...) @printf(ptr noundef @.str.21, ptr noundef %964, i64 noundef %965)
  call void @llvm.memcpy.p0.p0.i64(ptr align 16 %148, ptr align 16 @__const.main.lw, i64 32, i1 false)
  call void @llvm.memcpy.p0.p0.i64(ptr align 16 %149, ptr align 16 @__const.main.lb2, i64 16, i1 false)
  call void @llvm.memcpy.p0.p0.i64(ptr align 16 %150, ptr align 16 @__const.main.lx2, i64 16, i1 false)
  %967 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %152, i32 0, i32 0
  %968 = getelementptr inbounds [4 x i64], ptr %148, i64 0, i64 0
  store ptr %968, ptr %967, align 8
  %969 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %152, i32 0, i32 1
  store i64 4, ptr %969, align 8
  %970 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %152, i32 0, i32 2
  store i64 8, ptr %970, align 8
  %971 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %152, i32 0, i32 3
  store i64 8, ptr %971, align 8
  %972 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %153, i32 0, i32 0
  %973 = getelementptr inbounds [2 x i64], ptr %149, i64 0, i64 0
  store ptr %973, ptr %972, align 8
  %974 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %153, i32 0, i32 1
  store i64 2, ptr %974, align 8
  %975 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %153, i32 0, i32 2
  store i64 8, ptr %975, align 8
  %976 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %153, i32 0, i32 3
  store i64 8, ptr %976, align 8
  %977 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %154, i32 0, i32 0
  %978 = getelementptr inbounds [2 x i64], ptr %150, i64 0, i64 0
  store ptr %978, ptr %977, align 8
  %979 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %154, i32 0, i32 1
  store i64 2, ptr %979, align 8
  %980 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %154, i32 0, i32 2
  store i64 8, ptr %980, align 8
  %981 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %154, i32 0, i32 3
  store i64 8, ptr %981, align 8
  %982 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %155, i32 0, i32 0
  %983 = getelementptr inbounds [2 x i64], ptr %151, i64 0, i64 0
  store ptr %983, ptr %982, align 8
  %984 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %155, i32 0, i32 1
  store i64 2, ptr %984, align 8
  %985 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %155, i32 0, i32 2
  store i64 8, ptr %985, align 8
  %986 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %155, i32 0, i32 3
  store i64 8, ptr %986, align 8
  call void @fused_linear_relu(ptr noundef %152, ptr noundef %153, i64 noundef 2, i64 noundef 2, ptr noundef %154, ptr noundef %155)
  %987 = getelementptr inbounds [2 x i64], ptr %151, i64 0, i64 0
  %988 = load i64, ptr %987, align 16
  %989 = icmp eq i64 %988, 65536
  br i1 %989, label %990, label %994

990:                                              ; preds = %958
  %991 = getelementptr inbounds [2 x i64], ptr %151, i64 0, i64 1
  %992 = load i64, ptr %991, align 8
  %993 = icmp eq i64 %992, 0
  br label %994

994:                                              ; preds = %990, %958
  %995 = phi i1 [ false, %958 ], [ %993, %990 ]
  %996 = zext i1 %995 to i32
  store i32 %996, ptr %156, align 4
  %997 = load i32, ptr %156, align 4
  %998 = icmp ne i32 %997, 0
  %999 = zext i1 %998 to i64
  %1000 = select i1 %998, ptr @.str.1, ptr @.str.2
  %1001 = getelementptr inbounds [2 x i64], ptr %151, i64 0, i64 0
  %1002 = load i64, ptr %1001, align 16
  %1003 = getelementptr inbounds [2 x i64], ptr %151, i64 0, i64 1
  %1004 = load i64, ptr %1003, align 8
  %1005 = call i32 (ptr, ...) @printf(ptr noundef @.str.22, ptr noundef %1000, i64 noundef %1002, i64 noundef %1004)
  call void @llvm.memset.p0.i64(ptr align 16 %157, i8 0, i64 72, i1 false)
  %1006 = getelementptr inbounds [9 x i64], ptr %157, i32 0, i32 0
  store i64 65536, ptr %1006, align 16
  %1007 = getelementptr inbounds [9 x i64], ptr %157, i32 0, i32 4
  store i64 65536, ptr %1007, align 16
  %1008 = getelementptr inbounds [9 x i64], ptr %157, i32 0, i32 8
  store i64 65536, ptr %1008, align 16
  call void @llvm.memset.p0.i64(ptr align 16 %158, i8 0, i64 24, i1 false)
  call void @llvm.memcpy.p0.p0.i64(ptr align 16 %159, ptr align 16 @__const.main.lx3, i64 24, i1 false)
  call void @llvm.memcpy.p0.p0.i64(ptr align 16 %160, ptr align 16 @__const.main.lg3, i64 24, i1 false)
  call void @llvm.memset.p0.i64(ptr align 16 %161, i8 0, i64 24, i1 false)
  %1009 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %163, i32 0, i32 0
  %1010 = getelementptr inbounds [9 x i64], ptr %157, i64 0, i64 0
  store ptr %1010, ptr %1009, align 8
  %1011 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %163, i32 0, i32 1
  store i64 9, ptr %1011, align 8
  %1012 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %163, i32 0, i32 2
  store i64 8, ptr %1012, align 8
  %1013 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %163, i32 0, i32 3
  store i64 8, ptr %1013, align 8
  %1014 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %164, i32 0, i32 0
  %1015 = getelementptr inbounds [3 x i64], ptr %158, i64 0, i64 0
  store ptr %1015, ptr %1014, align 8
  %1016 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %164, i32 0, i32 1
  store i64 3, ptr %1016, align 8
  %1017 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %164, i32 0, i32 2
  store i64 8, ptr %1017, align 8
  %1018 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %164, i32 0, i32 3
  store i64 8, ptr %1018, align 8
  %1019 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %165, i32 0, i32 0
  %1020 = getelementptr inbounds [3 x i64], ptr %159, i64 0, i64 0
  store ptr %1020, ptr %1019, align 8
  %1021 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %165, i32 0, i32 1
  store i64 3, ptr %1021, align 8
  %1022 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %165, i32 0, i32 2
  store i64 8, ptr %1022, align 8
  %1023 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %165, i32 0, i32 3
  store i64 8, ptr %1023, align 8
  %1024 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %166, i32 0, i32 0
  %1025 = getelementptr inbounds [3 x i64], ptr %160, i64 0, i64 0
  store ptr %1025, ptr %1024, align 8
  %1026 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %166, i32 0, i32 1
  store i64 3, ptr %1026, align 8
  %1027 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %166, i32 0, i32 2
  store i64 8, ptr %1027, align 8
  %1028 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %166, i32 0, i32 3
  store i64 8, ptr %1028, align 8
  %1029 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %167, i32 0, i32 0
  %1030 = getelementptr inbounds [3 x i64], ptr %161, i64 0, i64 0
  store ptr %1030, ptr %1029, align 8
  %1031 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %167, i32 0, i32 1
  store i64 3, ptr %1031, align 8
  %1032 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %167, i32 0, i32 2
  store i64 8, ptr %1032, align 8
  %1033 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %167, i32 0, i32 3
  store i64 8, ptr %1033, align 8
  %1034 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %168, i32 0, i32 0
  %1035 = getelementptr inbounds [3 x i64], ptr %162, i64 0, i64 0
  store ptr %1035, ptr %1034, align 8
  %1036 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %168, i32 0, i32 1
  store i64 3, ptr %1036, align 8
  %1037 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %168, i32 0, i32 2
  store i64 8, ptr %1037, align 8
  %1038 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %168, i32 0, i32 3
  store i64 8, ptr %1038, align 8
  call void @fused_linear_ln(ptr noundef %163, ptr noundef %164, i64 noundef 3, i64 noundef 3, ptr noundef %165, ptr noundef %166, ptr noundef %167, ptr noundef %168)
  store i64 0, ptr %169, align 8
  store i32 0, ptr %170, align 4
  br label %1039

1039:                                             ; preds = %1049, %994
  %1040 = load i32, ptr %170, align 4
  %1041 = icmp slt i32 %1040, 3
  br i1 %1041, label %1042, label %1052

1042:                                             ; preds = %1039
  %1043 = load i32, ptr %170, align 4
  %1044 = sext i32 %1043 to i64
  %1045 = getelementptr inbounds [3 x i64], ptr %162, i64 0, i64 %1044
  %1046 = load i64, ptr %1045, align 8
  %1047 = load i64, ptr %169, align 8
  %1048 = add nsw i64 %1047, %1046
  store i64 %1048, ptr %169, align 8
  br label %1049

1049:                                             ; preds = %1042
  %1050 = load i32, ptr %170, align 4
  %1051 = add nsw i32 %1050, 1
  store i32 %1051, ptr %170, align 4
  br label %1039, !llvm.loop !15

1052:                                             ; preds = %1039
  %1053 = load i64, ptr %169, align 8
  %1054 = icmp slt i64 %1053, 10
  br i1 %1054, label %1055, label %1058

1055:                                             ; preds = %1052
  %1056 = load i64, ptr %169, align 8
  %1057 = icmp sgt i64 %1056, -10
  br label %1058

1058:                                             ; preds = %1055, %1052
  %1059 = phi i1 [ false, %1052 ], [ %1057, %1055 ]
  %1060 = zext i1 %1059 to i32
  store i32 %1060, ptr %171, align 4
  %1061 = load i32, ptr %171, align 4
  %1062 = icmp ne i32 %1061, 0
  %1063 = zext i1 %1062 to i64
  %1064 = select i1 %1062, ptr @.str.1, ptr @.str.2
  %1065 = load i64, ptr %169, align 8
  %1066 = call i32 (ptr, ...) @printf(ptr noundef @.str.23, ptr noundef %1064, i64 noundef %1065)
  call void @llvm.memset.p0.i64(ptr align 16 %172, i8 0, i64 48, i1 false)
  %1067 = getelementptr inbounds [6 x i64], ptr %172, i32 0, i32 0
  store i64 1, ptr %1067, align 16
  %1068 = getelementptr inbounds [6 x i64], ptr %172, i32 0, i32 1
  store i64 1, ptr %1068, align 8
  call void @llvm.memcpy.p0.p0.i64(ptr align 16 %173, ptr align 16 @__const.main.pih, i64 24, i1 false)
  call void @llvm.memcpy.p0.p0.i64(ptr align 16 %174, ptr align 16 @__const.main.pibm, i64 24, i1 false)
  call void @llvm.memcpy.p0.p0.i64(ptr align 16 %175, ptr align 16 @__const.main.pisc, i64 24, i1 false)
  %1069 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %177, i32 0, i32 0
  %1070 = getelementptr inbounds [6 x i64], ptr %172, i64 0, i64 0
  store ptr %1070, ptr %1069, align 8
  %1071 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %177, i32 0, i32 1
  store i64 6, ptr %1071, align 8
  %1072 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %177, i32 0, i32 2
  store i64 8, ptr %1072, align 8
  %1073 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %177, i32 0, i32 3
  store i64 8, ptr %1073, align 8
  %1074 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %178, i32 0, i32 0
  %1075 = getelementptr inbounds [3 x i64], ptr %173, i64 0, i64 0
  store ptr %1075, ptr %1074, align 8
  %1076 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %178, i32 0, i32 1
  store i64 3, ptr %1076, align 8
  %1077 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %178, i32 0, i32 2
  store i64 8, ptr %1077, align 8
  %1078 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %178, i32 0, i32 3
  store i64 8, ptr %1078, align 8
  %1079 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %179, i32 0, i32 0
  %1080 = getelementptr inbounds [3 x i64], ptr %174, i64 0, i64 0
  store ptr %1080, ptr %1079, align 8
  %1081 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %179, i32 0, i32 1
  store i64 3, ptr %1081, align 8
  %1082 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %179, i32 0, i32 2
  store i64 8, ptr %1082, align 8
  %1083 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %179, i32 0, i32 3
  store i64 8, ptr %1083, align 8
  %1084 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %180, i32 0, i32 0
  %1085 = getelementptr inbounds [3 x i64], ptr %175, i64 0, i64 0
  store ptr %1085, ptr %1084, align 8
  %1086 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %180, i32 0, i32 1
  store i64 3, ptr %1086, align 8
  %1087 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %180, i32 0, i32 2
  store i64 8, ptr %1087, align 8
  %1088 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %180, i32 0, i32 3
  store i64 8, ptr %1088, align 8
  %1089 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %181, i32 0, i32 0
  %1090 = getelementptr inbounds [6 x i64], ptr %176, i64 0, i64 0
  store ptr %1090, ptr %1089, align 8
  %1091 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %181, i32 0, i32 1
  store i64 6, ptr %1091, align 8
  %1092 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %181, i32 0, i32 2
  store i64 8, ptr %1092, align 8
  %1093 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %181, i32 0, i32 3
  store i64 8, ptr %1093, align 8
  %1094 = call i64 @integrated_derive(ptr noundef %177, i64 noundef 6, ptr noundef %178, ptr noundef %179, ptr noundef %180, i64 noundef 3, ptr noundef %181)
  store i64 %1094, ptr %182, align 8
  store i32 0, ptr %183, align 4
  store i32 0, ptr %184, align 4
  store i32 0, ptr %185, align 4
  store i64 0, ptr %186, align 8
  br label %1095

1095:                                             ; preds = %1118, %1058
  %1096 = load i64, ptr %186, align 8
  %1097 = load i64, ptr %182, align 8
  %1098 = icmp slt i64 %1096, %1097
  br i1 %1098, label %1099, label %1121

1099:                                             ; preds = %1095
  %1100 = load i64, ptr %186, align 8
  %1101 = getelementptr inbounds [6 x i64], ptr %176, i64 0, i64 %1100
  %1102 = load i64, ptr %1101, align 8
  %1103 = icmp eq i64 %1102, 2
  br i1 %1103, label %1104, label %1105

1104:                                             ; preds = %1099
  store i32 1, ptr %183, align 4
  br label %1105

1105:                                             ; preds = %1104, %1099
  %1106 = load i64, ptr %186, align 8
  %1107 = getelementptr inbounds [6 x i64], ptr %176, i64 0, i64 %1106
  %1108 = load i64, ptr %1107, align 8
  %1109 = icmp eq i64 %1108, 5
  br i1 %1109, label %1110, label %1111

1110:                                             ; preds = %1105
  store i32 1, ptr %184, align 4
  br label %1111

1111:                                             ; preds = %1110, %1105
  %1112 = load i64, ptr %186, align 8
  %1113 = getelementptr inbounds [6 x i64], ptr %176, i64 0, i64 %1112
  %1114 = load i64, ptr %1113, align 8
  %1115 = icmp eq i64 %1114, 3
  br i1 %1115, label %1116, label %1117

1116:                                             ; preds = %1111
  store i32 1, ptr %185, align 4
  br label %1117

1117:                                             ; preds = %1116, %1111
  br label %1118

1118:                                             ; preds = %1117
  %1119 = load i64, ptr %186, align 8
  %1120 = add nsw i64 %1119, 1
  store i64 %1120, ptr %186, align 8
  br label %1095, !llvm.loop !16

1121:                                             ; preds = %1095
  %1122 = load i64, ptr %182, align 8
  %1123 = icmp eq i64 %1122, 2
  br i1 %1123, label %1124, label %1134

1124:                                             ; preds = %1121
  %1125 = load i32, ptr %183, align 4
  %1126 = icmp ne i32 %1125, 0
  br i1 %1126, label %1127, label %1134

1127:                                             ; preds = %1124
  %1128 = load i32, ptr %184, align 4
  %1129 = icmp ne i32 %1128, 0
  br i1 %1129, label %1130, label %1134

1130:                                             ; preds = %1127
  %1131 = load i32, ptr %185, align 4
  %1132 = icmp ne i32 %1131, 0
  %1133 = xor i1 %1132, true
  br label %1134

1134:                                             ; preds = %1130, %1127, %1124, %1121
  %1135 = phi i1 [ false, %1127 ], [ false, %1124 ], [ false, %1121 ], [ %1133, %1130 ]
  %1136 = zext i1 %1135 to i32
  store i32 %1136, ptr %187, align 4
  %1137 = load i32, ptr %187, align 4
  %1138 = icmp ne i32 %1137, 0
  %1139 = zext i1 %1138 to i64
  %1140 = select i1 %1138, ptr @.str.1, ptr @.str.2
  %1141 = load i64, ptr %182, align 8
  %1142 = call i32 (ptr, ...) @printf(ptr noundef @.str.24, ptr noundef %1140, i64 noundef %1141)
  %1143 = load i32, ptr %185, align 4
  %1144 = icmp ne i32 %1143, 0
  %1145 = xor i1 %1144, true
  %1146 = zext i1 %1145 to i64
  %1147 = select i1 %1145, ptr @.str.1, ptr @.str.2
  %1148 = load i32, ptr %185, align 4
  %1149 = call i32 (ptr, ...) @printf(ptr noundef @.str.25, ptr noundef %1147, i32 noundef %1148)
  %1150 = call i32 (ptr, ...) @printf(ptr noundef @.str.26)
  ret i32 0
}

; Function Attrs: nocallback nofree nosync nounwind willreturn memory(argmem: write)
declare void @llvm.memset.p0.i64(ptr writeonly captures(none), i8, i64, i1 immarg) #1

; Function Attrs: nocallback nofree nosync nounwind willreturn memory(argmem: readwrite)
declare void @llvm.memcpy.p0.p0.i64(ptr noalias writeonly captures(none), ptr noalias readonly captures(none), i64, i1 immarg) #2

; Function Attrs: noinline nounwind optnone sspstrong uwtable
define internal void @matvec(ptr noundef %0, i64 noundef %1, i64 noundef %2, ptr noundef %3, ptr noundef %4, ptr noundef %5) #0 {
  %7 = alloca ptr, align 8
  %8 = alloca i64, align 8
  %9 = alloca i64, align 8
  %10 = alloca ptr, align 8
  %11 = alloca ptr, align 8
  %12 = alloca ptr, align 8
  %13 = alloca i64, align 8
  %14 = alloca i64, align 8
  %15 = alloca i64, align 8
  store ptr %0, ptr %7, align 8
  store i64 %1, ptr %8, align 8
  store i64 %2, ptr %9, align 8
  store ptr %3, ptr %10, align 8
  store ptr %4, ptr %11, align 8
  store ptr %5, ptr %12, align 8
  store i64 0, ptr %13, align 8
  br label %16

16:                                               ; preds = %51, %6
  %17 = load i64, ptr %13, align 8
  %18 = load i64, ptr %8, align 8
  %19 = icmp slt i64 %17, %18
  br i1 %19, label %20, label %54

20:                                               ; preds = %16
  store i64 0, ptr %14, align 8
  store i64 0, ptr %15, align 8
  br label %21

21:                                               ; preds = %39, %20
  %22 = load i64, ptr %15, align 8
  %23 = load i64, ptr %9, align 8
  %24 = icmp slt i64 %22, %23
  br i1 %24, label %25, label %42

25:                                               ; preds = %21
  %26 = load ptr, ptr %7, align 8
  %27 = load i64, ptr %13, align 8
  %28 = load i64, ptr %9, align 8
  %29 = mul nsw i64 %27, %28
  %30 = load i64, ptr %15, align 8
  %31 = add nsw i64 %29, %30
  %32 = call i64 @getv(ptr noundef %26, i64 noundef %31)
  %33 = load ptr, ptr %10, align 8
  %34 = load i64, ptr %15, align 8
  %35 = call i64 @getv(ptr noundef %33, i64 noundef %34)
  %36 = call i64 @qmul(i64 noundef %32, i64 noundef %35)
  %37 = load i64, ptr %14, align 8
  %38 = add nsw i64 %37, %36
  store i64 %38, ptr %14, align 8
  br label %39

39:                                               ; preds = %25
  %40 = load i64, ptr %15, align 8
  %41 = add nsw i64 %40, 1
  store i64 %41, ptr %15, align 8
  br label %21, !llvm.loop !17

42:                                               ; preds = %21
  %43 = load i64, ptr %14, align 8
  %44 = load ptr, ptr %11, align 8
  %45 = load i64, ptr %13, align 8
  %46 = call i64 @getv(ptr noundef %44, i64 noundef %45)
  %47 = add nsw i64 %43, %46
  %48 = load ptr, ptr %12, align 8
  %49 = load i64, ptr %13, align 8
  %50 = getelementptr inbounds i64, ptr %48, i64 %49
  store i64 %47, ptr %50, align 8
  br label %51

51:                                               ; preds = %42
  %52 = load i64, ptr %13, align 8
  %53 = add nsw i64 %52, 1
  store i64 %53, ptr %13, align 8
  br label %16, !llvm.loop !18

54:                                               ; preds = %16
  ret void
}

; Function Attrs: noinline nounwind optnone sspstrong uwtable
define internal i64 @qmul(i64 noundef %0, i64 noundef %1) #0 {
  %3 = alloca i64, align 8
  %4 = alloca i64, align 8
  store i64 %0, ptr %3, align 8
  store i64 %1, ptr %4, align 8
  %5 = load i64, ptr %3, align 8
  %6 = load i64, ptr %4, align 8
  %7 = mul nsw i64 %5, %6
  %8 = ashr i64 %7, 16
  ret i64 %8
}

declare i32 @printf(ptr noundef, ...) #3

; Function Attrs: noinline nounwind optnone sspstrong uwtable
define internal void @batched(ptr noundef %0, i64 noundef %1, i64 noundef %2, ptr noundef %3, ptr noundef %4, i64 noundef %5, ptr noundef %6) #0 {
  %8 = alloca ptr, align 8
  %9 = alloca i64, align 8
  %10 = alloca i64, align 8
  %11 = alloca ptr, align 8
  %12 = alloca ptr, align 8
  %13 = alloca i64, align 8
  %14 = alloca ptr, align 8
  %15 = alloca i64, align 8
  %16 = alloca %struct.MaruArrayView, align 8
  store ptr %0, ptr %8, align 8
  store i64 %1, ptr %9, align 8
  store i64 %2, ptr %10, align 8
  store ptr %3, ptr %11, align 8
  store ptr %4, ptr %12, align 8
  store i64 %5, ptr %13, align 8
  store ptr %6, ptr %14, align 8
  store i64 0, ptr %15, align 8
  br label %17

17:                                               ; preds = %46, %7
  %18 = load i64, ptr %15, align 8
  %19 = load i64, ptr %13, align 8
  %20 = icmp slt i64 %18, %19
  br i1 %20, label %21, label %49

21:                                               ; preds = %17
  %22 = load ptr, ptr %11, align 8
  call void @llvm.memcpy.p0.p0.i64(ptr align 8 %16, ptr align 8 %22, i64 32, i1 false)
  %23 = load ptr, ptr %11, align 8
  %24 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %23, i32 0, i32 0
  %25 = load ptr, ptr %24, align 8
  %26 = load i64, ptr %15, align 8
  %27 = load i64, ptr %10, align 8
  %28 = mul nsw i64 %26, %27
  %29 = load ptr, ptr %11, align 8
  %30 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %29, i32 0, i32 2
  %31 = load i64, ptr %30, align 8
  %32 = mul nsw i64 %28, %31
  %33 = getelementptr inbounds i8, ptr %25, i64 %32
  %34 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %16, i32 0, i32 0
  store ptr %33, ptr %34, align 8
  %35 = load i64, ptr %10, align 8
  %36 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %16, i32 0, i32 1
  store i64 %35, ptr %36, align 8
  %37 = load ptr, ptr %8, align 8
  %38 = load i64, ptr %9, align 8
  %39 = load i64, ptr %10, align 8
  %40 = load ptr, ptr %12, align 8
  %41 = load ptr, ptr %14, align 8
  %42 = load i64, ptr %15, align 8
  %43 = load i64, ptr %9, align 8
  %44 = mul nsw i64 %42, %43
  %45 = getelementptr inbounds i64, ptr %41, i64 %44
  call void @matvec(ptr noundef %37, i64 noundef %38, i64 noundef %39, ptr noundef %16, ptr noundef %40, ptr noundef %45)
  br label %46

46:                                               ; preds = %21
  %47 = load i64, ptr %15, align 8
  %48 = add nsw i64 %47, 1
  store i64 %48, ptr %15, align 8
  br label %17, !llvm.loop !19

49:                                               ; preds = %17
  ret void
}

; Function Attrs: noinline nounwind optnone sspstrong uwtable
define internal void @softmax(ptr noundef %0, i64 noundef %1, ptr noundef %2) #0 {
  %4 = alloca ptr, align 8
  %5 = alloca i64, align 8
  %6 = alloca ptr, align 8
  %7 = alloca double, align 8
  %8 = alloca i64, align 8
  %9 = alloca double, align 8
  %10 = alloca [64 x double], align 16
  %11 = alloca double, align 8
  %12 = alloca i64, align 8
  %13 = alloca i64, align 8
  store ptr %0, ptr %4, align 8
  store i64 %1, ptr %5, align 8
  store ptr %2, ptr %6, align 8
  %14 = load ptr, ptr %4, align 8
  %15 = call i64 @getv(ptr noundef %14, i64 noundef 0)
  %16 = sitofp i64 %15 to double
  %17 = fdiv double %16, 6.553600e+04
  store double %17, ptr %7, align 8
  store i64 1, ptr %8, align 8
  br label %18

18:                                               ; preds = %34, %3
  %19 = load i64, ptr %8, align 8
  %20 = load i64, ptr %5, align 8
  %21 = icmp slt i64 %19, %20
  br i1 %21, label %22, label %37

22:                                               ; preds = %18
  %23 = load ptr, ptr %4, align 8
  %24 = load i64, ptr %8, align 8
  %25 = call i64 @getv(ptr noundef %23, i64 noundef %24)
  %26 = sitofp i64 %25 to double
  %27 = fdiv double %26, 6.553600e+04
  store double %27, ptr %9, align 8
  %28 = load double, ptr %9, align 8
  %29 = load double, ptr %7, align 8
  %30 = fcmp ogt double %28, %29
  br i1 %30, label %31, label %33

31:                                               ; preds = %22
  %32 = load double, ptr %9, align 8
  store double %32, ptr %7, align 8
  br label %33

33:                                               ; preds = %31, %22
  br label %34

34:                                               ; preds = %33
  %35 = load i64, ptr %8, align 8
  %36 = add nsw i64 %35, 1
  store i64 %36, ptr %8, align 8
  br label %18, !llvm.loop !20

37:                                               ; preds = %18
  store double 0.000000e+00, ptr %11, align 8
  store i64 0, ptr %12, align 8
  br label %38

38:                                               ; preds = %58, %37
  %39 = load i64, ptr %12, align 8
  %40 = load i64, ptr %5, align 8
  %41 = icmp slt i64 %39, %40
  br i1 %41, label %42, label %61

42:                                               ; preds = %38
  %43 = load ptr, ptr %4, align 8
  %44 = load i64, ptr %12, align 8
  %45 = call i64 @getv(ptr noundef %43, i64 noundef %44)
  %46 = sitofp i64 %45 to double
  %47 = fdiv double %46, 6.553600e+04
  %48 = load double, ptr %7, align 8
  %49 = fsub double %47, %48
  %50 = call double @exp(double noundef %49) #6
  %51 = load i64, ptr %12, align 8
  %52 = getelementptr inbounds [64 x double], ptr %10, i64 0, i64 %51
  store double %50, ptr %52, align 8
  %53 = load i64, ptr %12, align 8
  %54 = getelementptr inbounds [64 x double], ptr %10, i64 0, i64 %53
  %55 = load double, ptr %54, align 8
  %56 = load double, ptr %11, align 8
  %57 = fadd double %56, %55
  store double %57, ptr %11, align 8
  br label %58

58:                                               ; preds = %42
  %59 = load i64, ptr %12, align 8
  %60 = add nsw i64 %59, 1
  store i64 %60, ptr %12, align 8
  br label %38, !llvm.loop !21

61:                                               ; preds = %38
  store i64 0, ptr %13, align 8
  br label %62

62:                                               ; preds = %76, %61
  %63 = load i64, ptr %13, align 8
  %64 = load i64, ptr %5, align 8
  %65 = icmp slt i64 %63, %64
  br i1 %65, label %66, label %79

66:                                               ; preds = %62
  %67 = load ptr, ptr %6, align 8
  %68 = load i64, ptr %13, align 8
  %69 = load i64, ptr %13, align 8
  %70 = getelementptr inbounds [64 x double], ptr %10, i64 0, i64 %69
  %71 = load double, ptr %70, align 8
  %72 = load double, ptr %11, align 8
  %73 = fdiv double %71, %72
  %74 = fmul double %73, 6.553600e+04
  %75 = fptosi double %74 to i64
  call void @setv(ptr noundef %67, i64 noundef %68, i64 noundef %75)
  br label %76

76:                                               ; preds = %66
  %77 = load i64, ptr %13, align 8
  %78 = add nsw i64 %77, 1
  store i64 %78, ptr %13, align 8
  br label %62, !llvm.loop !22

79:                                               ; preds = %62
  ret void
}

; Function Attrs: noinline nounwind optnone sspstrong uwtable
define internal void @layernorm(ptr noundef %0, i64 noundef %1, ptr noundef %2, ptr noundef %3, ptr noundef %4) #0 {
  %6 = alloca ptr, align 8
  %7 = alloca i64, align 8
  %8 = alloca ptr, align 8
  %9 = alloca ptr, align 8
  %10 = alloca ptr, align 8
  %11 = alloca i64, align 8
  %12 = alloca i64, align 8
  %13 = alloca i64, align 8
  %14 = alloca i64, align 8
  %15 = alloca i64, align 8
  %16 = alloca i64, align 8
  %17 = alloca i64, align 8
  %18 = alloca i64, align 8
  store ptr %0, ptr %6, align 8
  store i64 %1, ptr %7, align 8
  store ptr %2, ptr %8, align 8
  store ptr %3, ptr %9, align 8
  store ptr %4, ptr %10, align 8
  store i64 0, ptr %11, align 8
  store i64 0, ptr %12, align 8
  br label %19

19:                                               ; preds = %29, %5
  %20 = load i64, ptr %12, align 8
  %21 = load i64, ptr %7, align 8
  %22 = icmp slt i64 %20, %21
  br i1 %22, label %23, label %32

23:                                               ; preds = %19
  %24 = load ptr, ptr %6, align 8
  %25 = load i64, ptr %12, align 8
  %26 = call i64 @getv(ptr noundef %24, i64 noundef %25)
  %27 = load i64, ptr %11, align 8
  %28 = add nsw i64 %27, %26
  store i64 %28, ptr %11, align 8
  br label %29

29:                                               ; preds = %23
  %30 = load i64, ptr %12, align 8
  %31 = add nsw i64 %30, 1
  store i64 %31, ptr %12, align 8
  br label %19, !llvm.loop !23

32:                                               ; preds = %19
  %33 = load i64, ptr %11, align 8
  %34 = load i64, ptr %7, align 8
  %35 = sdiv i64 %33, %34
  store i64 %35, ptr %13, align 8
  store i64 0, ptr %14, align 8
  store i64 0, ptr %15, align 8
  br label %36

36:                                               ; preds = %51, %32
  %37 = load i64, ptr %15, align 8
  %38 = load i64, ptr %7, align 8
  %39 = icmp slt i64 %37, %38
  br i1 %39, label %40, label %54

40:                                               ; preds = %36
  %41 = load ptr, ptr %6, align 8
  %42 = load i64, ptr %15, align 8
  %43 = call i64 @getv(ptr noundef %41, i64 noundef %42)
  %44 = load i64, ptr %13, align 8
  %45 = sub nsw i64 %43, %44
  store i64 %45, ptr %16, align 8
  %46 = load i64, ptr %16, align 8
  %47 = load i64, ptr %16, align 8
  %48 = call i64 @qmul(i64 noundef %46, i64 noundef %47)
  %49 = load i64, ptr %14, align 8
  %50 = add nsw i64 %49, %48
  store i64 %50, ptr %14, align 8
  br label %51

51:                                               ; preds = %40
  %52 = load i64, ptr %15, align 8
  %53 = add nsw i64 %52, 1
  store i64 %53, ptr %15, align 8
  br label %36, !llvm.loop !24

54:                                               ; preds = %36
  %55 = load i64, ptr %7, align 8
  %56 = load i64, ptr %14, align 8
  %57 = sdiv i64 %56, %55
  store i64 %57, ptr %14, align 8
  %58 = load i64, ptr %14, align 8
  %59 = add nsw i64 %58, 1
  %60 = call i64 @qsqrt(i64 noundef %59)
  %61 = call i64 @qdiv(i64 noundef 65536, i64 noundef %60)
  store i64 %61, ptr %17, align 8
  store i64 0, ptr %18, align 8
  br label %62

62:                                               ; preds = %84, %54
  %63 = load i64, ptr %18, align 8
  %64 = load i64, ptr %7, align 8
  %65 = icmp slt i64 %63, %64
  br i1 %65, label %66, label %87

66:                                               ; preds = %62
  %67 = load ptr, ptr %10, align 8
  %68 = load i64, ptr %18, align 8
  %69 = load ptr, ptr %6, align 8
  %70 = load i64, ptr %18, align 8
  %71 = call i64 @getv(ptr noundef %69, i64 noundef %70)
  %72 = load i64, ptr %13, align 8
  %73 = sub nsw i64 %71, %72
  %74 = load i64, ptr %17, align 8
  %75 = call i64 @qmul(i64 noundef %73, i64 noundef %74)
  %76 = load ptr, ptr %8, align 8
  %77 = load i64, ptr %18, align 8
  %78 = call i64 @getv(ptr noundef %76, i64 noundef %77)
  %79 = call i64 @qmul(i64 noundef %75, i64 noundef %78)
  %80 = load ptr, ptr %9, align 8
  %81 = load i64, ptr %18, align 8
  %82 = call i64 @getv(ptr noundef %80, i64 noundef %81)
  %83 = add nsw i64 %79, %82
  call void @setv(ptr noundef %67, i64 noundef %68, i64 noundef %83)
  br label %84

84:                                               ; preds = %66
  %85 = load i64, ptr %18, align 8
  %86 = add nsw i64 %85, 1
  store i64 %86, ptr %18, align 8
  br label %62, !llvm.loop !25

87:                                               ; preds = %62
  ret void
}

; Function Attrs: noinline nounwind optnone sspstrong uwtable
define internal void @fused_attention(ptr noundef %0, ptr noundef %1, ptr noundef %2, ptr noundef %3, ptr noundef %4, ptr noundef %5, ptr noundef %6, ptr noundef %7) #0 {
  %9 = alloca ptr, align 8
  %10 = alloca ptr, align 8
  %11 = alloca ptr, align 8
  %12 = alloca ptr, align 8
  %13 = alloca ptr, align 8
  %14 = alloca ptr, align 8
  %15 = alloca ptr, align 8
  %16 = alloca ptr, align 8
  %17 = alloca [3 x [4 x i64]], align 16
  %18 = alloca [3 x [4 x i64]], align 16
  %19 = alloca [3 x [4 x i64]], align 16
  %20 = alloca [3 x [4 x i64]], align 16
  %21 = alloca [3 x [4 x i64]], align 16
  %22 = alloca [3 x [4 x i64]], align 16
  %23 = alloca i64, align 8
  %24 = alloca %struct.MaruArrayView, align 8
  %25 = alloca [4 x i64], align 16
  %26 = alloca [4 x i64], align 16
  %27 = alloca [4 x i64], align 16
  %28 = alloca %struct.MaruArrayView, align 8
  %29 = alloca %struct.MaruArrayView, align 8
  %30 = alloca %struct.MaruArrayView, align 8
  %31 = alloca %struct.MaruArrayView, align 8
  %32 = alloca %struct.MaruArrayView, align 8
  %33 = alloca i32, align 4
  %34 = alloca i64, align 8
  %35 = alloca [3 x i64], align 16
  %36 = alloca [3 x i64], align 16
  %37 = alloca i64, align 8
  %38 = alloca %struct.MaruArrayView, align 8
  %39 = alloca %struct.MaruArrayView, align 8
  %40 = alloca i32, align 4
  %41 = alloca i64, align 8
  %42 = alloca i64, align 8
  %43 = alloca i64, align 8
  %44 = alloca %struct.MaruArrayView, align 8
  %45 = alloca %struct.MaruArrayView, align 8
  %46 = alloca i32, align 4
  %47 = alloca %struct.MaruArrayView, align 8
  %48 = alloca %struct.MaruArrayView, align 8
  %49 = alloca i32, align 4
  store ptr %0, ptr %9, align 8
  store ptr %1, ptr %10, align 8
  store ptr %2, ptr %11, align 8
  store ptr %3, ptr %12, align 8
  store ptr %4, ptr %13, align 8
  store ptr %5, ptr %14, align 8
  store ptr %6, ptr %15, align 8
  store ptr %7, ptr %16, align 8
  store i64 0, ptr %23, align 8
  br label %50

50:                                               ; preds = %152, %8
  %51 = load i64, ptr %23, align 8
  %52 = icmp slt i64 %51, 3
  br i1 %52, label %53, label %155

53:                                               ; preds = %50
  %54 = load ptr, ptr %9, align 8
  call void @llvm.memcpy.p0.p0.i64(ptr align 8 %24, ptr align 8 %54, i64 32, i1 false)
  %55 = load ptr, ptr %9, align 8
  %56 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %55, i32 0, i32 0
  %57 = load ptr, ptr %56, align 8
  %58 = load i64, ptr %23, align 8
  %59 = mul nsw i64 %58, 4
  %60 = load ptr, ptr %9, align 8
  %61 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %60, i32 0, i32 2
  %62 = load i64, ptr %61, align 8
  %63 = mul nsw i64 %59, %62
  %64 = getelementptr inbounds i8, ptr %57, i64 %63
  %65 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %24, i32 0, i32 0
  store ptr %64, ptr %65, align 8
  %66 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %24, i32 0, i32 1
  store i64 4, ptr %66, align 8
  %67 = load ptr, ptr %11, align 8
  call void @llvm.memcpy.p0.p0.i64(ptr align 8 %28, ptr align 8 %67, i64 32, i1 false)
  %68 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %28, i32 0, i32 1
  store i64 4, ptr %68, align 8
  %69 = load ptr, ptr %10, align 8
  %70 = getelementptr inbounds [4 x i64], ptr %25, i64 0, i64 0
  call void @matvec(ptr noundef %69, i64 noundef 4, i64 noundef 4, ptr noundef %24, ptr noundef %28, ptr noundef %70)
  %71 = load ptr, ptr %11, align 8
  call void @llvm.memcpy.p0.p0.i64(ptr align 8 %29, ptr align 8 %71, i64 32, i1 false)
  %72 = load ptr, ptr %11, align 8
  %73 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %72, i32 0, i32 0
  %74 = load ptr, ptr %73, align 8
  %75 = load ptr, ptr %11, align 8
  %76 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %75, i32 0, i32 2
  %77 = load i64, ptr %76, align 8
  %78 = mul nsw i64 4, %77
  %79 = getelementptr inbounds i8, ptr %74, i64 %78
  %80 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %29, i32 0, i32 0
  store ptr %79, ptr %80, align 8
  %81 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %29, i32 0, i32 1
  store i64 4, ptr %81, align 8
  %82 = load ptr, ptr %10, align 8
  call void @llvm.memcpy.p0.p0.i64(ptr align 8 %30, ptr align 8 %82, i64 32, i1 false)
  %83 = load ptr, ptr %10, align 8
  %84 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %83, i32 0, i32 0
  %85 = load ptr, ptr %84, align 8
  %86 = load ptr, ptr %10, align 8
  %87 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %86, i32 0, i32 2
  %88 = load i64, ptr %87, align 8
  %89 = mul nsw i64 16, %88
  %90 = getelementptr inbounds i8, ptr %85, i64 %89
  %91 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %30, i32 0, i32 0
  store ptr %90, ptr %91, align 8
  %92 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %30, i32 0, i32 1
  store i64 16, ptr %92, align 8
  %93 = getelementptr inbounds [4 x i64], ptr %26, i64 0, i64 0
  call void @matvec(ptr noundef %30, i64 noundef 4, i64 noundef 4, ptr noundef %24, ptr noundef %29, ptr noundef %93)
  %94 = load ptr, ptr %11, align 8
  call void @llvm.memcpy.p0.p0.i64(ptr align 8 %31, ptr align 8 %94, i64 32, i1 false)
  %95 = load ptr, ptr %11, align 8
  %96 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %95, i32 0, i32 0
  %97 = load ptr, ptr %96, align 8
  %98 = load ptr, ptr %11, align 8
  %99 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %98, i32 0, i32 2
  %100 = load i64, ptr %99, align 8
  %101 = mul nsw i64 8, %100
  %102 = getelementptr inbounds i8, ptr %97, i64 %101
  %103 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %31, i32 0, i32 0
  store ptr %102, ptr %103, align 8
  %104 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %31, i32 0, i32 1
  store i64 4, ptr %104, align 8
  %105 = load ptr, ptr %10, align 8
  call void @llvm.memcpy.p0.p0.i64(ptr align 8 %32, ptr align 8 %105, i64 32, i1 false)
  %106 = load ptr, ptr %10, align 8
  %107 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %106, i32 0, i32 0
  %108 = load ptr, ptr %107, align 8
  %109 = load ptr, ptr %10, align 8
  %110 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %109, i32 0, i32 2
  %111 = load i64, ptr %110, align 8
  %112 = mul nsw i64 32, %111
  %113 = getelementptr inbounds i8, ptr %108, i64 %112
  %114 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %32, i32 0, i32 0
  store ptr %113, ptr %114, align 8
  %115 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %32, i32 0, i32 1
  store i64 16, ptr %115, align 8
  %116 = getelementptr inbounds [4 x i64], ptr %27, i64 0, i64 0
  call void @matvec(ptr noundef %32, i64 noundef 4, i64 noundef 4, ptr noundef %24, ptr noundef %31, ptr noundef %116)
  store i32 0, ptr %33, align 4
  br label %117

117:                                              ; preds = %148, %53
  %118 = load i32, ptr %33, align 4
  %119 = icmp slt i32 %118, 4
  br i1 %119, label %120, label %151

120:                                              ; preds = %117
  %121 = load i32, ptr %33, align 4
  %122 = sext i32 %121 to i64
  %123 = getelementptr inbounds [4 x i64], ptr %25, i64 0, i64 %122
  %124 = load i64, ptr %123, align 8
  %125 = load i64, ptr %23, align 8
  %126 = getelementptr inbounds [3 x [4 x i64]], ptr %17, i64 0, i64 %125
  %127 = load i32, ptr %33, align 4
  %128 = sext i32 %127 to i64
  %129 = getelementptr inbounds [4 x i64], ptr %126, i64 0, i64 %128
  store i64 %124, ptr %129, align 8
  %130 = load i32, ptr %33, align 4
  %131 = sext i32 %130 to i64
  %132 = getelementptr inbounds [4 x i64], ptr %26, i64 0, i64 %131
  %133 = load i64, ptr %132, align 8
  %134 = load i64, ptr %23, align 8
  %135 = getelementptr inbounds [3 x [4 x i64]], ptr %18, i64 0, i64 %134
  %136 = load i32, ptr %33, align 4
  %137 = sext i32 %136 to i64
  %138 = getelementptr inbounds [4 x i64], ptr %135, i64 0, i64 %137
  store i64 %133, ptr %138, align 8
  %139 = load i32, ptr %33, align 4
  %140 = sext i32 %139 to i64
  %141 = getelementptr inbounds [4 x i64], ptr %27, i64 0, i64 %140
  %142 = load i64, ptr %141, align 8
  %143 = load i64, ptr %23, align 8
  %144 = getelementptr inbounds [3 x [4 x i64]], ptr %19, i64 0, i64 %143
  %145 = load i32, ptr %33, align 4
  %146 = sext i32 %145 to i64
  %147 = getelementptr inbounds [4 x i64], ptr %144, i64 0, i64 %146
  store i64 %142, ptr %147, align 8
  br label %148

148:                                              ; preds = %120
  %149 = load i32, ptr %33, align 4
  %150 = add nsw i32 %149, 1
  store i32 %150, ptr %33, align 4
  br label %117, !llvm.loop !26

151:                                              ; preds = %117
  br label %152

152:                                              ; preds = %151
  %153 = load i64, ptr %23, align 8
  %154 = add nsw i64 %153, 1
  store i64 %154, ptr %23, align 8
  br label %50, !llvm.loop !27

155:                                              ; preds = %50
  store i64 0, ptr %34, align 8
  br label %156

156:                                              ; preds = %222, %155
  %157 = load i64, ptr %34, align 8
  %158 = icmp slt i64 %157, 3
  br i1 %158, label %159, label %225

159:                                              ; preds = %156
  store i64 0, ptr %37, align 8
  br label %160

160:                                              ; preds = %174, %159
  %161 = load i64, ptr %37, align 8
  %162 = icmp slt i64 %161, 3
  br i1 %162, label %163, label %177

163:                                              ; preds = %160
  %164 = load i64, ptr %34, align 8
  %165 = getelementptr inbounds [3 x [4 x i64]], ptr %17, i64 0, i64 %164
  %166 = getelementptr inbounds [4 x i64], ptr %165, i64 0, i64 0
  %167 = load i64, ptr %37, align 8
  %168 = getelementptr inbounds [3 x [4 x i64]], ptr %18, i64 0, i64 %167
  %169 = getelementptr inbounds [4 x i64], ptr %168, i64 0, i64 0
  %170 = call i64 @adot(ptr noundef %166, ptr noundef %169, i64 noundef 4)
  %171 = call i64 @qdiv(i64 noundef %170, i64 noundef 131072)
  %172 = load i64, ptr %37, align 8
  %173 = getelementptr inbounds [3 x i64], ptr %35, i64 0, i64 %172
  store i64 %171, ptr %173, align 8
  br label %174

174:                                              ; preds = %163
  %175 = load i64, ptr %37, align 8
  %176 = add nsw i64 %175, 1
  store i64 %176, ptr %37, align 8
  br label %160, !llvm.loop !28

177:                                              ; preds = %160
  %178 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %38, i32 0, i32 0
  %179 = getelementptr inbounds [3 x i64], ptr %35, i64 0, i64 0
  store ptr %179, ptr %178, align 8
  %180 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %38, i32 0, i32 1
  store i64 3, ptr %180, align 8
  %181 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %38, i32 0, i32 2
  store i64 8, ptr %181, align 8
  %182 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %38, i32 0, i32 3
  store i64 8, ptr %182, align 8
  %183 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %39, i32 0, i32 0
  %184 = getelementptr inbounds [3 x i64], ptr %36, i64 0, i64 0
  store ptr %184, ptr %183, align 8
  %185 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %39, i32 0, i32 1
  store i64 3, ptr %185, align 8
  %186 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %39, i32 0, i32 2
  store i64 8, ptr %186, align 8
  %187 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %39, i32 0, i32 3
  store i64 8, ptr %187, align 8
  call void @softmax(ptr noundef %38, i64 noundef 3, ptr noundef %39)
  store i32 0, ptr %40, align 4
  br label %188

188:                                              ; preds = %218, %177
  %189 = load i32, ptr %40, align 4
  %190 = icmp slt i32 %189, 4
  br i1 %190, label %191, label %221

191:                                              ; preds = %188
  store i64 0, ptr %41, align 8
  store i64 0, ptr %42, align 8
  br label %192

192:                                              ; preds = %208, %191
  %193 = load i64, ptr %42, align 8
  %194 = icmp slt i64 %193, 3
  br i1 %194, label %195, label %211

195:                                              ; preds = %192
  %196 = load i64, ptr %42, align 8
  %197 = getelementptr inbounds [3 x [4 x i64]], ptr %19, i64 0, i64 %196
  %198 = load i32, ptr %40, align 4
  %199 = sext i32 %198 to i64
  %200 = getelementptr inbounds [4 x i64], ptr %197, i64 0, i64 %199
  %201 = load i64, ptr %200, align 8
  %202 = load i64, ptr %42, align 8
  %203 = getelementptr inbounds [3 x i64], ptr %36, i64 0, i64 %202
  %204 = load i64, ptr %203, align 8
  %205 = call i64 @qmul(i64 noundef %201, i64 noundef %204)
  %206 = load i64, ptr %41, align 8
  %207 = add nsw i64 %206, %205
  store i64 %207, ptr %41, align 8
  br label %208

208:                                              ; preds = %195
  %209 = load i64, ptr %42, align 8
  %210 = add nsw i64 %209, 1
  store i64 %210, ptr %42, align 8
  br label %192, !llvm.loop !29

211:                                              ; preds = %192
  %212 = load i64, ptr %41, align 8
  %213 = load i64, ptr %34, align 8
  %214 = getelementptr inbounds [3 x [4 x i64]], ptr %20, i64 0, i64 %213
  %215 = load i32, ptr %40, align 4
  %216 = sext i32 %215 to i64
  %217 = getelementptr inbounds [4 x i64], ptr %214, i64 0, i64 %216
  store i64 %212, ptr %217, align 8
  br label %218

218:                                              ; preds = %211
  %219 = load i32, ptr %40, align 4
  %220 = add nsw i32 %219, 1
  store i32 %220, ptr %40, align 4
  br label %188, !llvm.loop !30

221:                                              ; preds = %188
  br label %222

222:                                              ; preds = %221
  %223 = load i64, ptr %34, align 8
  %224 = add nsw i64 %223, 1
  store i64 %224, ptr %34, align 8
  br label %156, !llvm.loop !31

225:                                              ; preds = %156
  store i64 0, ptr %43, align 8
  br label %226

226:                                              ; preds = %312, %225
  %227 = load i64, ptr %43, align 8
  %228 = icmp slt i64 %227, 3
  br i1 %228, label %229, label %315

229:                                              ; preds = %226
  %230 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %44, i32 0, i32 0
  %231 = load i64, ptr %43, align 8
  %232 = getelementptr inbounds [3 x [4 x i64]], ptr %20, i64 0, i64 %231
  %233 = getelementptr inbounds [4 x i64], ptr %232, i64 0, i64 0
  store ptr %233, ptr %230, align 8
  %234 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %44, i32 0, i32 1
  store i64 4, ptr %234, align 8
  %235 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %44, i32 0, i32 2
  store i64 8, ptr %235, align 8
  %236 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %44, i32 0, i32 3
  store i64 8, ptr %236, align 8
  %237 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %45, i32 0, i32 0
  %238 = load i64, ptr %43, align 8
  %239 = getelementptr inbounds [3 x [4 x i64]], ptr %22, i64 0, i64 %238
  %240 = getelementptr inbounds [4 x i64], ptr %239, i64 0, i64 0
  store ptr %240, ptr %237, align 8
  %241 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %45, i32 0, i32 1
  store i64 4, ptr %241, align 8
  %242 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %45, i32 0, i32 2
  store i64 8, ptr %242, align 8
  %243 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %45, i32 0, i32 3
  store i64 8, ptr %243, align 8
  %244 = load ptr, ptr %12, align 8
  %245 = load ptr, ptr %13, align 8
  %246 = load i64, ptr %43, align 8
  %247 = getelementptr inbounds [3 x [4 x i64]], ptr %22, i64 0, i64 %246
  %248 = getelementptr inbounds [4 x i64], ptr %247, i64 0, i64 0
  call void @matvec(ptr noundef %244, i64 noundef 4, i64 noundef 4, ptr noundef %44, ptr noundef %245, ptr noundef %248)
  store i32 0, ptr %46, align 4
  br label %249

249:                                              ; preds = %272, %229
  %250 = load i32, ptr %46, align 4
  %251 = icmp slt i32 %250, 4
  br i1 %251, label %252, label %275

252:                                              ; preds = %249
  %253 = load ptr, ptr %9, align 8
  %254 = load i64, ptr %43, align 8
  %255 = mul nsw i64 %254, 4
  %256 = load i32, ptr %46, align 4
  %257 = sext i32 %256 to i64
  %258 = add nsw i64 %255, %257
  %259 = call i64 @getv(ptr noundef %253, i64 noundef %258)
  %260 = load i64, ptr %43, align 8
  %261 = getelementptr inbounds [3 x [4 x i64]], ptr %22, i64 0, i64 %260
  %262 = load i32, ptr %46, align 4
  %263 = sext i32 %262 to i64
  %264 = getelementptr inbounds [4 x i64], ptr %261, i64 0, i64 %263
  %265 = load i64, ptr %264, align 8
  %266 = add nsw i64 %259, %265
  %267 = load i64, ptr %43, align 8
  %268 = getelementptr inbounds [3 x [4 x i64]], ptr %21, i64 0, i64 %267
  %269 = load i32, ptr %46, align 4
  %270 = sext i32 %269 to i64
  %271 = getelementptr inbounds [4 x i64], ptr %268, i64 0, i64 %270
  store i64 %266, ptr %271, align 8
  br label %272

272:                                              ; preds = %252
  %273 = load i32, ptr %46, align 4
  %274 = add nsw i32 %273, 1
  store i32 %274, ptr %46, align 4
  br label %249, !llvm.loop !32

275:                                              ; preds = %249
  %276 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %47, i32 0, i32 0
  %277 = load i64, ptr %43, align 8
  %278 = getelementptr inbounds [3 x [4 x i64]], ptr %21, i64 0, i64 %277
  %279 = getelementptr inbounds [4 x i64], ptr %278, i64 0, i64 0
  store ptr %279, ptr %276, align 8
  %280 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %47, i32 0, i32 1
  store i64 4, ptr %280, align 8
  %281 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %47, i32 0, i32 2
  store i64 8, ptr %281, align 8
  %282 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %47, i32 0, i32 3
  store i64 8, ptr %282, align 8
  %283 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %48, i32 0, i32 0
  %284 = load i64, ptr %43, align 8
  %285 = getelementptr inbounds [3 x [4 x i64]], ptr %20, i64 0, i64 %284
  %286 = getelementptr inbounds [4 x i64], ptr %285, i64 0, i64 0
  store ptr %286, ptr %283, align 8
  %287 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %48, i32 0, i32 1
  store i64 4, ptr %287, align 8
  %288 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %48, i32 0, i32 2
  store i64 8, ptr %288, align 8
  %289 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %48, i32 0, i32 3
  store i64 8, ptr %289, align 8
  %290 = load ptr, ptr %14, align 8
  %291 = load ptr, ptr %15, align 8
  call void @layernorm(ptr noundef %47, i64 noundef 4, ptr noundef %290, ptr noundef %291, ptr noundef %48)
  store i32 0, ptr %49, align 4
  br label %292

292:                                              ; preds = %308, %275
  %293 = load i32, ptr %49, align 4
  %294 = icmp slt i32 %293, 4
  br i1 %294, label %295, label %311

295:                                              ; preds = %292
  %296 = load ptr, ptr %16, align 8
  %297 = load i64, ptr %43, align 8
  %298 = mul nsw i64 %297, 4
  %299 = load i32, ptr %49, align 4
  %300 = sext i32 %299 to i64
  %301 = add nsw i64 %298, %300
  %302 = load i64, ptr %43, align 8
  %303 = getelementptr inbounds [3 x [4 x i64]], ptr %20, i64 0, i64 %302
  %304 = load i32, ptr %49, align 4
  %305 = sext i32 %304 to i64
  %306 = getelementptr inbounds [4 x i64], ptr %303, i64 0, i64 %305
  %307 = load i64, ptr %306, align 8
  call void @setv(ptr noundef %296, i64 noundef %301, i64 noundef %307)
  br label %308

308:                                              ; preds = %295
  %309 = load i32, ptr %49, align 4
  %310 = add nsw i32 %309, 1
  store i32 %310, ptr %49, align 4
  br label %292, !llvm.loop !33

311:                                              ; preds = %292
  br label %312

312:                                              ; preds = %311
  %313 = load i64, ptr %43, align 8
  %314 = add nsw i64 %313, 1
  store i64 %314, ptr %43, align 8
  br label %226, !llvm.loop !34

315:                                              ; preds = %226
  ret void
}

; Function Attrs: noinline nounwind optnone sspstrong uwtable
define internal void @fused_attention_ref(ptr noundef %0, ptr noundef %1, ptr noundef %2, ptr noundef %3, ptr noundef %4, ptr noundef %5, ptr noundef %6, ptr noundef %7) #0 {
  %9 = alloca ptr, align 8
  %10 = alloca ptr, align 8
  %11 = alloca ptr, align 8
  %12 = alloca ptr, align 8
  %13 = alloca ptr, align 8
  %14 = alloca ptr, align 8
  %15 = alloca ptr, align 8
  %16 = alloca ptr, align 8
  %17 = alloca [3 x [4 x i64]], align 16
  %18 = alloca [3 x [4 x i64]], align 16
  %19 = alloca [3 x [4 x i64]], align 16
  %20 = alloca [3 x [4 x i64]], align 16
  %21 = alloca [3 x [4 x i64]], align 16
  %22 = alloca [3 x [4 x i64]], align 16
  %23 = alloca %struct.MaruArrayView, align 8
  %24 = alloca %struct.MaruArrayView, align 8
  %25 = alloca %struct.MaruArrayView, align 8
  %26 = alloca %struct.MaruArrayView, align 8
  %27 = alloca %struct.MaruArrayView, align 8
  %28 = alloca %struct.MaruArrayView, align 8
  %29 = alloca i32, align 4
  %30 = alloca %struct.MaruArrayView, align 8
  %31 = alloca [4 x i64], align 16
  %32 = alloca [4 x i64], align 16
  %33 = alloca [4 x i64], align 16
  %34 = alloca %struct.MaruArrayView, align 8
  %35 = alloca %struct.MaruArrayView, align 8
  %36 = alloca %struct.MaruArrayView, align 8
  %37 = alloca %struct.MaruArrayView, align 8
  %38 = alloca %struct.MaruArrayView, align 8
  %39 = alloca i32, align 4
  %40 = alloca i32, align 4
  %41 = alloca [3 x i64], align 16
  %42 = alloca [3 x i64], align 16
  %43 = alloca i32, align 4
  %44 = alloca %struct.MaruArrayView, align 8
  %45 = alloca %struct.MaruArrayView, align 8
  %46 = alloca i32, align 4
  %47 = alloca i64, align 8
  %48 = alloca i32, align 4
  %49 = alloca i32, align 4
  %50 = alloca %struct.MaruArrayView, align 8
  %51 = alloca i32, align 4
  %52 = alloca %struct.MaruArrayView, align 8
  %53 = alloca %struct.MaruArrayView, align 8
  %54 = alloca i32, align 4
  store ptr %0, ptr %9, align 8
  store ptr %1, ptr %10, align 8
  store ptr %2, ptr %11, align 8
  store ptr %3, ptr %12, align 8
  store ptr %4, ptr %13, align 8
  store ptr %5, ptr %14, align 8
  store ptr %6, ptr %15, align 8
  store ptr %7, ptr %16, align 8
  %55 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %23, i32 0, i32 0
  %56 = load ptr, ptr %10, align 8
  store ptr %56, ptr %55, align 8
  %57 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %23, i32 0, i32 1
  store i64 48, ptr %57, align 8
  %58 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %23, i32 0, i32 2
  store i64 8, ptr %58, align 8
  %59 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %23, i32 0, i32 3
  store i64 8, ptr %59, align 8
  %60 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %24, i32 0, i32 0
  %61 = load ptr, ptr %11, align 8
  store ptr %61, ptr %60, align 8
  %62 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %24, i32 0, i32 1
  store i64 12, ptr %62, align 8
  %63 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %24, i32 0, i32 2
  store i64 8, ptr %63, align 8
  %64 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %24, i32 0, i32 3
  store i64 8, ptr %64, align 8
  %65 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %25, i32 0, i32 0
  %66 = load ptr, ptr %12, align 8
  store ptr %66, ptr %65, align 8
  %67 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %25, i32 0, i32 1
  store i64 16, ptr %67, align 8
  %68 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %25, i32 0, i32 2
  store i64 8, ptr %68, align 8
  %69 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %25, i32 0, i32 3
  store i64 8, ptr %69, align 8
  %70 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %26, i32 0, i32 0
  %71 = load ptr, ptr %13, align 8
  store ptr %71, ptr %70, align 8
  %72 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %26, i32 0, i32 1
  store i64 4, ptr %72, align 8
  %73 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %26, i32 0, i32 2
  store i64 8, ptr %73, align 8
  %74 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %26, i32 0, i32 3
  store i64 8, ptr %74, align 8
  %75 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %27, i32 0, i32 0
  %76 = load ptr, ptr %14, align 8
  store ptr %76, ptr %75, align 8
  %77 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %27, i32 0, i32 1
  store i64 4, ptr %77, align 8
  %78 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %27, i32 0, i32 2
  store i64 8, ptr %78, align 8
  %79 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %27, i32 0, i32 3
  store i64 8, ptr %79, align 8
  %80 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %28, i32 0, i32 0
  %81 = load ptr, ptr %15, align 8
  store ptr %81, ptr %80, align 8
  %82 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %28, i32 0, i32 1
  store i64 4, ptr %82, align 8
  %83 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %28, i32 0, i32 2
  store i64 8, ptr %83, align 8
  %84 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %28, i32 0, i32 3
  store i64 8, ptr %84, align 8
  store i32 0, ptr %29, align 4
  br label %85

85:                                               ; preds = %163, %8
  %86 = load i32, ptr %29, align 4
  %87 = icmp slt i32 %86, 3
  br i1 %87, label %88, label %166

88:                                               ; preds = %85
  %89 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %30, i32 0, i32 0
  %90 = load ptr, ptr %9, align 8
  %91 = load i32, ptr %29, align 4
  %92 = mul nsw i32 %91, 4
  %93 = sext i32 %92 to i64
  %94 = getelementptr inbounds i64, ptr %90, i64 %93
  store ptr %94, ptr %89, align 8
  %95 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %30, i32 0, i32 1
  store i64 4, ptr %95, align 8
  %96 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %30, i32 0, i32 2
  store i64 8, ptr %96, align 8
  %97 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %30, i32 0, i32 3
  store i64 8, ptr %97, align 8
  call void @llvm.memcpy.p0.p0.i64(ptr align 8 %34, ptr align 8 %24, i64 32, i1 false)
  call void @llvm.memcpy.p0.p0.i64(ptr align 8 %35, ptr align 8 %24, i64 32, i1 false)
  call void @llvm.memcpy.p0.p0.i64(ptr align 8 %36, ptr align 8 %24, i64 32, i1 false)
  %98 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %24, i32 0, i32 0
  %99 = load ptr, ptr %98, align 8
  %100 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %34, i32 0, i32 0
  store ptr %99, ptr %100, align 8
  %101 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %34, i32 0, i32 1
  store i64 4, ptr %101, align 8
  %102 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %24, i32 0, i32 0
  %103 = load ptr, ptr %102, align 8
  %104 = getelementptr inbounds i8, ptr %103, i64 32
  %105 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %35, i32 0, i32 0
  store ptr %104, ptr %105, align 8
  %106 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %35, i32 0, i32 1
  store i64 4, ptr %106, align 8
  %107 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %24, i32 0, i32 0
  %108 = load ptr, ptr %107, align 8
  %109 = getelementptr inbounds i8, ptr %108, i64 64
  %110 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %36, i32 0, i32 0
  store ptr %109, ptr %110, align 8
  %111 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %36, i32 0, i32 1
  store i64 4, ptr %111, align 8
  call void @llvm.memcpy.p0.p0.i64(ptr align 8 %37, ptr align 8 %23, i64 32, i1 false)
  call void @llvm.memcpy.p0.p0.i64(ptr align 8 %38, ptr align 8 %23, i64 32, i1 false)
  %112 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %23, i32 0, i32 0
  %113 = load ptr, ptr %112, align 8
  %114 = getelementptr inbounds i8, ptr %113, i64 128
  %115 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %37, i32 0, i32 0
  store ptr %114, ptr %115, align 8
  %116 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %37, i32 0, i32 1
  store i64 16, ptr %116, align 8
  %117 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %23, i32 0, i32 0
  %118 = load ptr, ptr %117, align 8
  %119 = getelementptr inbounds i8, ptr %118, i64 256
  %120 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %38, i32 0, i32 0
  store ptr %119, ptr %120, align 8
  %121 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %38, i32 0, i32 1
  store i64 16, ptr %121, align 8
  %122 = getelementptr inbounds [4 x i64], ptr %31, i64 0, i64 0
  call void @matvec(ptr noundef %23, i64 noundef 4, i64 noundef 4, ptr noundef %30, ptr noundef %34, ptr noundef %122)
  %123 = getelementptr inbounds [4 x i64], ptr %32, i64 0, i64 0
  call void @matvec(ptr noundef %37, i64 noundef 4, i64 noundef 4, ptr noundef %30, ptr noundef %35, ptr noundef %123)
  %124 = getelementptr inbounds [4 x i64], ptr %33, i64 0, i64 0
  call void @matvec(ptr noundef %38, i64 noundef 4, i64 noundef 4, ptr noundef %30, ptr noundef %36, ptr noundef %124)
  store i32 0, ptr %39, align 4
  br label %125

125:                                              ; preds = %159, %88
  %126 = load i32, ptr %39, align 4
  %127 = icmp slt i32 %126, 4
  br i1 %127, label %128, label %162

128:                                              ; preds = %125
  %129 = load i32, ptr %39, align 4
  %130 = sext i32 %129 to i64
  %131 = getelementptr inbounds [4 x i64], ptr %31, i64 0, i64 %130
  %132 = load i64, ptr %131, align 8
  %133 = load i32, ptr %29, align 4
  %134 = sext i32 %133 to i64
  %135 = getelementptr inbounds [3 x [4 x i64]], ptr %17, i64 0, i64 %134
  %136 = load i32, ptr %39, align 4
  %137 = sext i32 %136 to i64
  %138 = getelementptr inbounds [4 x i64], ptr %135, i64 0, i64 %137
  store i64 %132, ptr %138, align 8
  %139 = load i32, ptr %39, align 4
  %140 = sext i32 %139 to i64
  %141 = getelementptr inbounds [4 x i64], ptr %32, i64 0, i64 %140
  %142 = load i64, ptr %141, align 8
  %143 = load i32, ptr %29, align 4
  %144 = sext i32 %143 to i64
  %145 = getelementptr inbounds [3 x [4 x i64]], ptr %18, i64 0, i64 %144
  %146 = load i32, ptr %39, align 4
  %147 = sext i32 %146 to i64
  %148 = getelementptr inbounds [4 x i64], ptr %145, i64 0, i64 %147
  store i64 %142, ptr %148, align 8
  %149 = load i32, ptr %39, align 4
  %150 = sext i32 %149 to i64
  %151 = getelementptr inbounds [4 x i64], ptr %33, i64 0, i64 %150
  %152 = load i64, ptr %151, align 8
  %153 = load i32, ptr %29, align 4
  %154 = sext i32 %153 to i64
  %155 = getelementptr inbounds [3 x [4 x i64]], ptr %19, i64 0, i64 %154
  %156 = load i32, ptr %39, align 4
  %157 = sext i32 %156 to i64
  %158 = getelementptr inbounds [4 x i64], ptr %155, i64 0, i64 %157
  store i64 %152, ptr %158, align 8
  br label %159

159:                                              ; preds = %128
  %160 = load i32, ptr %39, align 4
  %161 = add nsw i32 %160, 1
  store i32 %161, ptr %39, align 4
  br label %125, !llvm.loop !35

162:                                              ; preds = %125
  br label %163

163:                                              ; preds = %162
  %164 = load i32, ptr %29, align 4
  %165 = add nsw i32 %164, 1
  store i32 %165, ptr %29, align 4
  br label %85, !llvm.loop !36

166:                                              ; preds = %85
  store i32 0, ptr %40, align 4
  br label %167

167:                                              ; preds = %239, %166
  %168 = load i32, ptr %40, align 4
  %169 = icmp slt i32 %168, 3
  br i1 %169, label %170, label %242

170:                                              ; preds = %167
  store i32 0, ptr %43, align 4
  br label %171

171:                                              ; preds = %188, %170
  %172 = load i32, ptr %43, align 4
  %173 = icmp slt i32 %172, 3
  br i1 %173, label %174, label %191

174:                                              ; preds = %171
  %175 = load i32, ptr %40, align 4
  %176 = sext i32 %175 to i64
  %177 = getelementptr inbounds [3 x [4 x i64]], ptr %17, i64 0, i64 %176
  %178 = getelementptr inbounds [4 x i64], ptr %177, i64 0, i64 0
  %179 = load i32, ptr %43, align 4
  %180 = sext i32 %179 to i64
  %181 = getelementptr inbounds [3 x [4 x i64]], ptr %18, i64 0, i64 %180
  %182 = getelementptr inbounds [4 x i64], ptr %181, i64 0, i64 0
  %183 = call i64 @adot(ptr noundef %178, ptr noundef %182, i64 noundef 4)
  %184 = call i64 @qdiv(i64 noundef %183, i64 noundef 131072)
  %185 = load i32, ptr %43, align 4
  %186 = sext i32 %185 to i64
  %187 = getelementptr inbounds [3 x i64], ptr %41, i64 0, i64 %186
  store i64 %184, ptr %187, align 8
  br label %188

188:                                              ; preds = %174
  %189 = load i32, ptr %43, align 4
  %190 = add nsw i32 %189, 1
  store i32 %190, ptr %43, align 4
  br label %171, !llvm.loop !37

191:                                              ; preds = %171
  %192 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %44, i32 0, i32 0
  %193 = getelementptr inbounds [3 x i64], ptr %41, i64 0, i64 0
  store ptr %193, ptr %192, align 8
  %194 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %44, i32 0, i32 1
  store i64 3, ptr %194, align 8
  %195 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %44, i32 0, i32 2
  store i64 8, ptr %195, align 8
  %196 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %44, i32 0, i32 3
  store i64 8, ptr %196, align 8
  %197 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %45, i32 0, i32 0
  %198 = getelementptr inbounds [3 x i64], ptr %42, i64 0, i64 0
  store ptr %198, ptr %197, align 8
  %199 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %45, i32 0, i32 1
  store i64 3, ptr %199, align 8
  %200 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %45, i32 0, i32 2
  store i64 8, ptr %200, align 8
  %201 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %45, i32 0, i32 3
  store i64 8, ptr %201, align 8
  call void @softmax(ptr noundef %44, i64 noundef 3, ptr noundef %45)
  store i32 0, ptr %46, align 4
  br label %202

202:                                              ; preds = %235, %191
  %203 = load i32, ptr %46, align 4
  %204 = icmp slt i32 %203, 4
  br i1 %204, label %205, label %238

205:                                              ; preds = %202
  store i64 0, ptr %47, align 8
  store i32 0, ptr %48, align 4
  br label %206

206:                                              ; preds = %224, %205
  %207 = load i32, ptr %48, align 4
  %208 = icmp slt i32 %207, 3
  br i1 %208, label %209, label %227

209:                                              ; preds = %206
  %210 = load i32, ptr %48, align 4
  %211 = sext i32 %210 to i64
  %212 = getelementptr inbounds [3 x [4 x i64]], ptr %19, i64 0, i64 %211
  %213 = load i32, ptr %46, align 4
  %214 = sext i32 %213 to i64
  %215 = getelementptr inbounds [4 x i64], ptr %212, i64 0, i64 %214
  %216 = load i64, ptr %215, align 8
  %217 = load i32, ptr %48, align 4
  %218 = sext i32 %217 to i64
  %219 = getelementptr inbounds [3 x i64], ptr %42, i64 0, i64 %218
  %220 = load i64, ptr %219, align 8
  %221 = call i64 @qmul(i64 noundef %216, i64 noundef %220)
  %222 = load i64, ptr %47, align 8
  %223 = add nsw i64 %222, %221
  store i64 %223, ptr %47, align 8
  br label %224

224:                                              ; preds = %209
  %225 = load i32, ptr %48, align 4
  %226 = add nsw i32 %225, 1
  store i32 %226, ptr %48, align 4
  br label %206, !llvm.loop !38

227:                                              ; preds = %206
  %228 = load i64, ptr %47, align 8
  %229 = load i32, ptr %40, align 4
  %230 = sext i32 %229 to i64
  %231 = getelementptr inbounds [3 x [4 x i64]], ptr %20, i64 0, i64 %230
  %232 = load i32, ptr %46, align 4
  %233 = sext i32 %232 to i64
  %234 = getelementptr inbounds [4 x i64], ptr %231, i64 0, i64 %233
  store i64 %228, ptr %234, align 8
  br label %235

235:                                              ; preds = %227
  %236 = load i32, ptr %46, align 4
  %237 = add nsw i32 %236, 1
  store i32 %237, ptr %46, align 4
  br label %202, !llvm.loop !39

238:                                              ; preds = %202
  br label %239

239:                                              ; preds = %238
  %240 = load i32, ptr %40, align 4
  %241 = add nsw i32 %240, 1
  store i32 %241, ptr %40, align 4
  br label %167, !llvm.loop !40

242:                                              ; preds = %167
  store i32 0, ptr %49, align 4
  br label %243

243:                                              ; preds = %327, %242
  %244 = load i32, ptr %49, align 4
  %245 = icmp slt i32 %244, 3
  br i1 %245, label %246, label %330

246:                                              ; preds = %243
  %247 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %50, i32 0, i32 0
  %248 = load i32, ptr %49, align 4
  %249 = sext i32 %248 to i64
  %250 = getelementptr inbounds [3 x [4 x i64]], ptr %20, i64 0, i64 %249
  %251 = getelementptr inbounds [4 x i64], ptr %250, i64 0, i64 0
  store ptr %251, ptr %247, align 8
  %252 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %50, i32 0, i32 1
  store i64 4, ptr %252, align 8
  %253 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %50, i32 0, i32 2
  store i64 8, ptr %253, align 8
  %254 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %50, i32 0, i32 3
  store i64 8, ptr %254, align 8
  %255 = load i32, ptr %49, align 4
  %256 = sext i32 %255 to i64
  %257 = getelementptr inbounds [3 x [4 x i64]], ptr %21, i64 0, i64 %256
  %258 = getelementptr inbounds [4 x i64], ptr %257, i64 0, i64 0
  call void @matvec(ptr noundef %25, i64 noundef 4, i64 noundef 4, ptr noundef %50, ptr noundef %26, ptr noundef %258)
  store i32 0, ptr %51, align 4
  br label %259

259:                                              ; preds = %285, %246
  %260 = load i32, ptr %51, align 4
  %261 = icmp slt i32 %260, 4
  br i1 %261, label %262, label %288

262:                                              ; preds = %259
  %263 = load ptr, ptr %9, align 8
  %264 = load i32, ptr %49, align 4
  %265 = mul nsw i32 %264, 4
  %266 = load i32, ptr %51, align 4
  %267 = add nsw i32 %265, %266
  %268 = sext i32 %267 to i64
  %269 = getelementptr inbounds i64, ptr %263, i64 %268
  %270 = load i64, ptr %269, align 8
  %271 = load i32, ptr %49, align 4
  %272 = sext i32 %271 to i64
  %273 = getelementptr inbounds [3 x [4 x i64]], ptr %21, i64 0, i64 %272
  %274 = load i32, ptr %51, align 4
  %275 = sext i32 %274 to i64
  %276 = getelementptr inbounds [4 x i64], ptr %273, i64 0, i64 %275
  %277 = load i64, ptr %276, align 8
  %278 = add nsw i64 %270, %277
  %279 = load i32, ptr %49, align 4
  %280 = sext i32 %279 to i64
  %281 = getelementptr inbounds [3 x [4 x i64]], ptr %22, i64 0, i64 %280
  %282 = load i32, ptr %51, align 4
  %283 = sext i32 %282 to i64
  %284 = getelementptr inbounds [4 x i64], ptr %281, i64 0, i64 %283
  store i64 %278, ptr %284, align 8
  br label %285

285:                                              ; preds = %262
  %286 = load i32, ptr %51, align 4
  %287 = add nsw i32 %286, 1
  store i32 %287, ptr %51, align 4
  br label %259, !llvm.loop !41

288:                                              ; preds = %259
  %289 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %52, i32 0, i32 0
  %290 = load i32, ptr %49, align 4
  %291 = sext i32 %290 to i64
  %292 = getelementptr inbounds [3 x [4 x i64]], ptr %22, i64 0, i64 %291
  %293 = getelementptr inbounds [4 x i64], ptr %292, i64 0, i64 0
  store ptr %293, ptr %289, align 8
  %294 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %52, i32 0, i32 1
  store i64 4, ptr %294, align 8
  %295 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %52, i32 0, i32 2
  store i64 8, ptr %295, align 8
  %296 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %52, i32 0, i32 3
  store i64 8, ptr %296, align 8
  %297 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %53, i32 0, i32 0
  %298 = load i32, ptr %49, align 4
  %299 = sext i32 %298 to i64
  %300 = getelementptr inbounds [3 x [4 x i64]], ptr %20, i64 0, i64 %299
  %301 = getelementptr inbounds [4 x i64], ptr %300, i64 0, i64 0
  store ptr %301, ptr %297, align 8
  %302 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %53, i32 0, i32 1
  store i64 4, ptr %302, align 8
  %303 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %53, i32 0, i32 2
  store i64 8, ptr %303, align 8
  %304 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %53, i32 0, i32 3
  store i64 8, ptr %304, align 8
  call void @layernorm(ptr noundef %52, i64 noundef 4, ptr noundef %27, ptr noundef %28, ptr noundef %53)
  store i32 0, ptr %54, align 4
  br label %305

305:                                              ; preds = %323, %288
  %306 = load i32, ptr %54, align 4
  %307 = icmp slt i32 %306, 4
  br i1 %307, label %308, label %326

308:                                              ; preds = %305
  %309 = load i32, ptr %49, align 4
  %310 = sext i32 %309 to i64
  %311 = getelementptr inbounds [3 x [4 x i64]], ptr %20, i64 0, i64 %310
  %312 = load i32, ptr %54, align 4
  %313 = sext i32 %312 to i64
  %314 = getelementptr inbounds [4 x i64], ptr %311, i64 0, i64 %313
  %315 = load i64, ptr %314, align 8
  %316 = load ptr, ptr %16, align 8
  %317 = load i32, ptr %49, align 4
  %318 = mul nsw i32 %317, 4
  %319 = load i32, ptr %54, align 4
  %320 = add nsw i32 %318, %319
  %321 = sext i32 %320 to i64
  %322 = getelementptr inbounds i64, ptr %316, i64 %321
  store i64 %315, ptr %322, align 8
  br label %323

323:                                              ; preds = %308
  %324 = load i32, ptr %54, align 4
  %325 = add nsw i32 %324, 1
  store i32 %325, ptr %54, align 4
  br label %305, !llvm.loop !42

326:                                              ; preds = %305
  br label %327

327:                                              ; preds = %326
  %328 = load i32, ptr %49, align 4
  %329 = add nsw i32 %328, 1
  store i32 %329, ptr %49, align 4
  br label %243, !llvm.loop !43

330:                                              ; preds = %243
  ret void
}

; Function Attrs: noinline nounwind optnone sspstrong uwtable
define internal void @topk(ptr noundef %0, i64 noundef %1, i64 noundef %2, ptr noundef %3, ptr noundef %4, ptr noundef %5) #0 {
  %7 = alloca ptr, align 8
  %8 = alloca i64, align 8
  %9 = alloca i64, align 8
  %10 = alloca ptr, align 8
  %11 = alloca ptr, align 8
  %12 = alloca ptr, align 8
  %13 = alloca [64 x i64], align 16
  %14 = alloca [64 x i64], align 16
  %15 = alloca i64, align 8
  %16 = alloca i64, align 8
  %17 = alloca i64, align 8
  %18 = alloca i64, align 8
  %19 = alloca i64, align 8
  %20 = alloca i64, align 8
  %21 = alloca i64, align 8
  store ptr %0, ptr %7, align 8
  store i64 %1, ptr %8, align 8
  store i64 %2, ptr %9, align 8
  store ptr %3, ptr %10, align 8
  store ptr %4, ptr %11, align 8
  store ptr %5, ptr %12, align 8
  store i64 0, ptr %15, align 8
  br label %22

22:                                               ; preds = %31, %6
  %23 = load i64, ptr %15, align 8
  %24 = load i64, ptr %9, align 8
  %25 = icmp slt i64 %23, %24
  br i1 %25, label %26, label %34

26:                                               ; preds = %22
  %27 = load i64, ptr %15, align 8
  %28 = getelementptr inbounds [64 x i64], ptr %13, i64 0, i64 %27
  store i64 -1, ptr %28, align 8
  %29 = load i64, ptr %15, align 8
  %30 = getelementptr inbounds [64 x i64], ptr %14, i64 0, i64 %29
  store i64 -999999999, ptr %30, align 8
  br label %31

31:                                               ; preds = %26
  %32 = load i64, ptr %15, align 8
  %33 = add nsw i64 %32, 1
  store i64 %33, ptr %15, align 8
  br label %22, !llvm.loop !44

34:                                               ; preds = %22
  store i64 0, ptr %16, align 8
  br label %35

35:                                               ; preds = %104, %34
  %36 = load i64, ptr %16, align 8
  %37 = load i64, ptr %8, align 8
  %38 = icmp slt i64 %36, %37
  br i1 %38, label %39, label %107

39:                                               ; preds = %35
  %40 = load ptr, ptr %7, align 8
  %41 = load i64, ptr %16, align 8
  %42 = call i64 @getv(ptr noundef %40, i64 noundef %41)
  store i64 %42, ptr %17, align 8
  %43 = load i64, ptr %9, align 8
  store i64 %43, ptr %18, align 8
  store i64 0, ptr %19, align 8
  br label %44

44:                                               ; preds = %57, %39
  %45 = load i64, ptr %19, align 8
  %46 = load i64, ptr %9, align 8
  %47 = icmp slt i64 %45, %46
  br i1 %47, label %48, label %60

48:                                               ; preds = %44
  %49 = load i64, ptr %17, align 8
  %50 = load i64, ptr %19, align 8
  %51 = getelementptr inbounds [64 x i64], ptr %14, i64 0, i64 %50
  %52 = load i64, ptr %51, align 8
  %53 = icmp sgt i64 %49, %52
  br i1 %53, label %54, label %56

54:                                               ; preds = %48
  %55 = load i64, ptr %19, align 8
  store i64 %55, ptr %18, align 8
  br label %60

56:                                               ; preds = %48
  br label %57

57:                                               ; preds = %56
  %58 = load i64, ptr %19, align 8
  %59 = add nsw i64 %58, 1
  store i64 %59, ptr %19, align 8
  br label %44, !llvm.loop !45

60:                                               ; preds = %54, %44
  %61 = load i64, ptr %18, align 8
  %62 = load i64, ptr %9, align 8
  %63 = icmp slt i64 %61, %62
  br i1 %63, label %64, label %103

64:                                               ; preds = %60
  %65 = load i64, ptr %9, align 8
  %66 = sub nsw i64 %65, 1
  store i64 %66, ptr %20, align 8
  br label %67

67:                                               ; preds = %84, %64
  %68 = load i64, ptr %20, align 8
  %69 = load i64, ptr %18, align 8
  %70 = icmp sgt i64 %68, %69
  br i1 %70, label %71, label %87

71:                                               ; preds = %67
  %72 = load i64, ptr %20, align 8
  %73 = sub nsw i64 %72, 1
  %74 = getelementptr inbounds [64 x i64], ptr %14, i64 0, i64 %73
  %75 = load i64, ptr %74, align 8
  %76 = load i64, ptr %20, align 8
  %77 = getelementptr inbounds [64 x i64], ptr %14, i64 0, i64 %76
  store i64 %75, ptr %77, align 8
  %78 = load i64, ptr %20, align 8
  %79 = sub nsw i64 %78, 1
  %80 = getelementptr inbounds [64 x i64], ptr %13, i64 0, i64 %79
  %81 = load i64, ptr %80, align 8
  %82 = load i64, ptr %20, align 8
  %83 = getelementptr inbounds [64 x i64], ptr %13, i64 0, i64 %82
  store i64 %81, ptr %83, align 8
  br label %84

84:                                               ; preds = %71
  %85 = load i64, ptr %20, align 8
  %86 = add nsw i64 %85, -1
  store i64 %86, ptr %20, align 8
  br label %67, !llvm.loop !46

87:                                               ; preds = %67
  %88 = load i64, ptr %17, align 8
  %89 = load i64, ptr %18, align 8
  %90 = getelementptr inbounds [64 x i64], ptr %14, i64 0, i64 %89
  store i64 %88, ptr %90, align 8
  %91 = load ptr, ptr %10, align 8
  %92 = icmp ne ptr %91, null
  br i1 %92, label %93, label %97

93:                                               ; preds = %87
  %94 = load ptr, ptr %10, align 8
  %95 = load i64, ptr %16, align 8
  %96 = call i64 @getv(ptr noundef %94, i64 noundef %95)
  br label %99

97:                                               ; preds = %87
  %98 = load i64, ptr %16, align 8
  br label %99

99:                                               ; preds = %97, %93
  %100 = phi i64 [ %96, %93 ], [ %98, %97 ]
  %101 = load i64, ptr %18, align 8
  %102 = getelementptr inbounds [64 x i64], ptr %13, i64 0, i64 %101
  store i64 %100, ptr %102, align 8
  br label %103

103:                                              ; preds = %99, %60
  br label %104

104:                                              ; preds = %103
  %105 = load i64, ptr %16, align 8
  %106 = add nsw i64 %105, 1
  store i64 %106, ptr %16, align 8
  br label %35, !llvm.loop !47

107:                                              ; preds = %35
  store i64 0, ptr %21, align 8
  br label %108

108:                                              ; preds = %123, %107
  %109 = load i64, ptr %21, align 8
  %110 = load i64, ptr %9, align 8
  %111 = icmp slt i64 %109, %110
  br i1 %111, label %112, label %126

112:                                              ; preds = %108
  %113 = load ptr, ptr %11, align 8
  %114 = load i64, ptr %21, align 8
  %115 = load i64, ptr %21, align 8
  %116 = getelementptr inbounds [64 x i64], ptr %13, i64 0, i64 %115
  %117 = load i64, ptr %116, align 8
  call void @setv(ptr noundef %113, i64 noundef %114, i64 noundef %117)
  %118 = load ptr, ptr %12, align 8
  %119 = load i64, ptr %21, align 8
  %120 = load i64, ptr %21, align 8
  %121 = getelementptr inbounds [64 x i64], ptr %14, i64 0, i64 %120
  %122 = load i64, ptr %121, align 8
  call void @setv(ptr noundef %118, i64 noundef %119, i64 noundef %122)
  br label %123

123:                                              ; preds = %112
  %124 = load i64, ptr %21, align 8
  %125 = add nsw i64 %124, 1
  store i64 %125, ptr %21, align 8
  br label %108, !llvm.loop !48

126:                                              ; preds = %108
  ret void
}

; Function Attrs: noinline nounwind optnone sspstrong uwtable
define internal i64 @argmax(ptr noundef %0, i64 noundef %1) #0 {
  %3 = alloca ptr, align 8
  %4 = alloca i64, align 8
  %5 = alloca i64, align 8
  %6 = alloca i64, align 8
  %7 = alloca i64, align 8
  %8 = alloca i64, align 8
  store ptr %0, ptr %3, align 8
  store i64 %1, ptr %4, align 8
  store i64 0, ptr %5, align 8
  %9 = load ptr, ptr %3, align 8
  %10 = call i64 @getv(ptr noundef %9, i64 noundef 0)
  store i64 %10, ptr %6, align 8
  store i64 1, ptr %7, align 8
  br label %11

11:                                               ; preds = %26, %2
  %12 = load i64, ptr %7, align 8
  %13 = load i64, ptr %4, align 8
  %14 = icmp slt i64 %12, %13
  br i1 %14, label %15, label %29

15:                                               ; preds = %11
  %16 = load ptr, ptr %3, align 8
  %17 = load i64, ptr %7, align 8
  %18 = call i64 @getv(ptr noundef %16, i64 noundef %17)
  store i64 %18, ptr %8, align 8
  %19 = load i64, ptr %8, align 8
  %20 = load i64, ptr %6, align 8
  %21 = icmp sgt i64 %19, %20
  br i1 %21, label %22, label %25

22:                                               ; preds = %15
  %23 = load i64, ptr %8, align 8
  store i64 %23, ptr %6, align 8
  %24 = load i64, ptr %7, align 8
  store i64 %24, ptr %5, align 8
  br label %25

25:                                               ; preds = %22, %15
  br label %26

26:                                               ; preds = %25
  %27 = load i64, ptr %7, align 8
  %28 = add nsw i64 %27, 1
  store i64 %28, ptr %7, align 8
  br label %11, !llvm.loop !49

29:                                               ; preds = %11
  %30 = load i64, ptr %5, align 8
  ret i64 %30
}

; Function Attrs: noinline nounwind optnone sspstrong uwtable
define internal i64 @mask_scores(ptr noundef %0, ptr noundef %1, i64 noundef %2, ptr noundef %3) #0 {
  %5 = alloca ptr, align 8
  %6 = alloca ptr, align 8
  %7 = alloca i64, align 8
  %8 = alloca ptr, align 8
  %9 = alloca i64, align 8
  %10 = alloca i64, align 8
  %11 = alloca i64, align 8
  %12 = alloca i64, align 8
  store ptr %0, ptr %5, align 8
  store ptr %1, ptr %6, align 8
  store i64 %2, ptr %7, align 8
  store ptr %3, ptr %8, align 8
  store i64 0, ptr %9, align 8
  store i64 0, ptr %10, align 8
  br label %13

13:                                               ; preds = %39, %4
  %14 = load i64, ptr %10, align 8
  %15 = load i64, ptr %7, align 8
  %16 = icmp slt i64 %14, %15
  br i1 %16, label %17, label %42

17:                                               ; preds = %13
  %18 = load ptr, ptr %6, align 8
  %19 = load i64, ptr %10, align 8
  %20 = call i64 @getv(ptr noundef %18, i64 noundef %19)
  store i64 %20, ptr %11, align 8
  %21 = load ptr, ptr %5, align 8
  %22 = load i64, ptr %10, align 8
  %23 = call i64 @getv(ptr noundef %21, i64 noundef %22)
  store i64 %23, ptr %12, align 8
  %24 = load ptr, ptr %8, align 8
  %25 = load i64, ptr %10, align 8
  %26 = load i64, ptr %11, align 8
  %27 = icmp ne i64 %26, 0
  br i1 %27, label %28, label %30

28:                                               ; preds = %17
  %29 = load i64, ptr %12, align 8
  br label %31

30:                                               ; preds = %17
  br label %31

31:                                               ; preds = %30, %28
  %32 = phi i64 [ %29, %28 ], [ -999999999, %30 ]
  call void @setv(ptr noundef %24, i64 noundef %25, i64 noundef %32)
  %33 = load i64, ptr %11, align 8
  %34 = icmp ne i64 %33, 0
  br i1 %34, label %35, label %38

35:                                               ; preds = %31
  %36 = load i64, ptr %9, align 8
  %37 = add nsw i64 %36, 1
  store i64 %37, ptr %9, align 8
  br label %38

38:                                               ; preds = %35, %31
  br label %39

39:                                               ; preds = %38
  %40 = load i64, ptr %10, align 8
  %41 = add nsw i64 %40, 1
  store i64 %41, ptr %10, align 8
  br label %13, !llvm.loop !50

42:                                               ; preds = %13
  %43 = load i64, ptr %9, align 8
  ret i64 %43
}

; Function Attrs: noinline nounwind optnone sspstrong uwtable
define internal void @build_index(ptr noundef %0, i64 noundef %1, i64 noundef %2, ptr noundef %3, ptr noundef %4) #0 {
  %6 = alloca ptr, align 8
  %7 = alloca i64, align 8
  %8 = alloca i64, align 8
  %9 = alloca ptr, align 8
  %10 = alloca ptr, align 8
  %11 = alloca i64, align 8
  %12 = alloca i64, align 8
  %13 = alloca i64, align 8
  store ptr %0, ptr %6, align 8
  store i64 %1, ptr %7, align 8
  store i64 %2, ptr %8, align 8
  store ptr %3, ptr %9, align 8
  store ptr %4, ptr %10, align 8
  store i64 0, ptr %11, align 8
  br label %14

14:                                               ; preds = %21, %5
  %15 = load i64, ptr %11, align 8
  %16 = load i64, ptr %8, align 8
  %17 = icmp slt i64 %15, %16
  br i1 %17, label %18, label %24

18:                                               ; preds = %14
  %19 = load ptr, ptr %9, align 8
  %20 = load i64, ptr %11, align 8
  call void @setv(ptr noundef %19, i64 noundef %20, i64 noundef -1)
  br label %21

21:                                               ; preds = %18
  %22 = load i64, ptr %11, align 8
  %23 = add nsw i64 %22, 1
  store i64 %23, ptr %11, align 8
  br label %14, !llvm.loop !51

24:                                               ; preds = %14
  store i64 0, ptr %12, align 8
  br label %25

25:                                               ; preds = %43, %24
  %26 = load i64, ptr %12, align 8
  %27 = load i64, ptr %7, align 8
  %28 = icmp slt i64 %26, %27
  br i1 %28, label %29, label %46

29:                                               ; preds = %25
  %30 = load ptr, ptr %6, align 8
  %31 = load i64, ptr %12, align 8
  %32 = call i64 @getv(ptr noundef %30, i64 noundef %31)
  %33 = load i64, ptr %8, align 8
  %34 = srem i64 %32, %33
  store i64 %34, ptr %13, align 8
  %35 = load ptr, ptr %10, align 8
  %36 = load i64, ptr %12, align 8
  %37 = load ptr, ptr %9, align 8
  %38 = load i64, ptr %13, align 8
  %39 = call i64 @getv(ptr noundef %37, i64 noundef %38)
  call void @setv(ptr noundef %35, i64 noundef %36, i64 noundef %39)
  %40 = load ptr, ptr %9, align 8
  %41 = load i64, ptr %13, align 8
  %42 = load i64, ptr %12, align 8
  call void @setv(ptr noundef %40, i64 noundef %41, i64 noundef %42)
  br label %43

43:                                               ; preds = %29
  %44 = load i64, ptr %12, align 8
  %45 = add nsw i64 %44, 1
  store i64 %45, ptr %12, align 8
  br label %25, !llvm.loop !52

46:                                               ; preds = %25
  ret void
}

; Function Attrs: noinline nounwind optnone sspstrong uwtable
define internal i64 @index_lookup(ptr noundef %0, i64 noundef %1, ptr noundef %2, i64 noundef %3, ptr noundef %4, i64 noundef %5, ptr noundef %6) #0 {
  %8 = alloca ptr, align 8
  %9 = alloca i64, align 8
  %10 = alloca ptr, align 8
  %11 = alloca i64, align 8
  %12 = alloca ptr, align 8
  %13 = alloca i64, align 8
  %14 = alloca ptr, align 8
  %15 = alloca i64, align 8
  %16 = alloca i64, align 8
  %17 = alloca i64, align 8
  store ptr %0, ptr %8, align 8
  store i64 %1, ptr %9, align 8
  store ptr %2, ptr %10, align 8
  store i64 %3, ptr %11, align 8
  store ptr %4, ptr %12, align 8
  store i64 %5, ptr %13, align 8
  store ptr %6, ptr %14, align 8
  %18 = load i64, ptr %13, align 8
  %19 = load i64, ptr %11, align 8
  %20 = srem i64 %18, %19
  store i64 %20, ptr %15, align 8
  store i64 0, ptr %16, align 8
  %21 = load ptr, ptr %10, align 8
  %22 = load i64, ptr %15, align 8
  %23 = call i64 @getv(ptr noundef %21, i64 noundef %22)
  store i64 %23, ptr %17, align 8
  br label %24

24:                                               ; preds = %39, %7
  %25 = load i64, ptr %17, align 8
  %26 = icmp sge i64 %25, 0
  br i1 %26, label %27, label %43

27:                                               ; preds = %24
  %28 = load ptr, ptr %8, align 8
  %29 = load i64, ptr %17, align 8
  %30 = call i64 @getv(ptr noundef %28, i64 noundef %29)
  %31 = load i64, ptr %13, align 8
  %32 = icmp eq i64 %30, %31
  br i1 %32, label %33, label %38

33:                                               ; preds = %27
  %34 = load ptr, ptr %14, align 8
  %35 = load i64, ptr %16, align 8
  %36 = add nsw i64 %35, 1
  store i64 %36, ptr %16, align 8
  %37 = load i64, ptr %17, align 8
  call void @setv(ptr noundef %34, i64 noundef %35, i64 noundef %37)
  br label %38

38:                                               ; preds = %33, %27
  br label %39

39:                                               ; preds = %38
  %40 = load ptr, ptr %12, align 8
  %41 = load i64, ptr %17, align 8
  %42 = call i64 @getv(ptr noundef %40, i64 noundef %41)
  store i64 %42, ptr %17, align 8
  br label %24, !llvm.loop !53

43:                                               ; preds = %24
  %44 = load i64, ptr %16, align 8
  ret i64 %44
}

; Function Attrs: noinline nounwind optnone sspstrong uwtable
define internal i64 @frontier_closure(ptr noundef %0, i64 noundef %1, ptr noundef %2, ptr noundef %3, i64 noundef %4, ptr noundef %5) #0 {
  %7 = alloca ptr, align 8
  %8 = alloca i64, align 8
  %9 = alloca ptr, align 8
  %10 = alloca ptr, align 8
  %11 = alloca i64, align 8
  %12 = alloca ptr, align 8
  %13 = alloca [64 x i8], align 16
  %14 = alloca i64, align 8
  %15 = alloca i64, align 8
  %16 = alloca i32, align 4
  %17 = alloca i64, align 8
  %18 = alloca i64, align 8
  %19 = alloca i64, align 8
  %20 = alloca i32, align 4
  %21 = alloca i64, align 8
  store ptr %0, ptr %7, align 8
  store i64 %1, ptr %8, align 8
  store ptr %2, ptr %9, align 8
  store ptr %3, ptr %10, align 8
  store i64 %4, ptr %11, align 8
  store ptr %5, ptr %12, align 8
  call void @llvm.memset.p0.i64(ptr align 16 %13, i8 0, i64 64, i1 false)
  store i64 0, ptr %14, align 8
  br label %22

22:                                               ; preds = %35, %6
  %23 = load i64, ptr %14, align 8
  %24 = load i64, ptr %8, align 8
  %25 = icmp slt i64 %23, %24
  br i1 %25, label %26, label %38

26:                                               ; preds = %22
  %27 = load ptr, ptr %7, align 8
  %28 = load i64, ptr %14, align 8
  %29 = call i64 @getv(ptr noundef %27, i64 noundef %28)
  %30 = icmp ne i64 %29, 0
  %31 = zext i1 %30 to i32
  %32 = trunc i32 %31 to i8
  %33 = load i64, ptr %14, align 8
  %34 = getelementptr inbounds [64 x i8], ptr %13, i64 0, i64 %33
  store i8 %32, ptr %34, align 1
  br label %35

35:                                               ; preds = %26
  %36 = load i64, ptr %14, align 8
  %37 = add nsw i64 %36, 1
  store i64 %37, ptr %14, align 8
  br label %22, !llvm.loop !54

38:                                               ; preds = %22
  store i64 0, ptr %15, align 8
  store i32 1, ptr %16, align 4
  br label %39

39:                                               ; preds = %95, %38
  %40 = load i32, ptr %16, align 4
  %41 = icmp ne i32 %40, 0
  br i1 %41, label %42, label %96

42:                                               ; preds = %39
  store i32 0, ptr %16, align 4
  store i64 0, ptr %17, align 8
  br label %43

43:                                               ; preds = %92, %42
  %44 = load i64, ptr %17, align 8
  %45 = load i64, ptr %11, align 8
  %46 = icmp slt i64 %44, %45
  br i1 %46, label %47, label %95

47:                                               ; preds = %43
  %48 = load ptr, ptr %9, align 8
  %49 = load i64, ptr %17, align 8
  %50 = call i64 @getv(ptr noundef %48, i64 noundef %49)
  store i64 %50, ptr %18, align 8
  %51 = load i64, ptr %18, align 8
  %52 = getelementptr inbounds [64 x i8], ptr %13, i64 0, i64 %51
  %53 = load i8, ptr %52, align 1
  %54 = icmp ne i8 %53, 0
  br i1 %54, label %55, label %56

55:                                               ; preds = %47
  br label %92

56:                                               ; preds = %47
  %57 = load ptr, ptr %10, align 8
  %58 = load i64, ptr %17, align 8
  %59 = call i64 @getv(ptr noundef %57, i64 noundef %58)
  store i64 %59, ptr %19, align 8
  store i32 1, ptr %20, align 4
  store i64 0, ptr %21, align 8
  br label %60

60:                                               ; preds = %78, %56
  %61 = load i64, ptr %21, align 8
  %62 = load i64, ptr %8, align 8
  %63 = icmp slt i64 %61, %62
  br i1 %63, label %64, label %81

64:                                               ; preds = %60
  %65 = load i64, ptr %19, align 8
  %66 = load i64, ptr %21, align 8
  %67 = lshr i64 %65, %66
  %68 = and i64 %67, 1
  %69 = icmp ne i64 %68, 0
  br i1 %69, label %70, label %77

70:                                               ; preds = %64
  %71 = load i64, ptr %21, align 8
  %72 = getelementptr inbounds [64 x i8], ptr %13, i64 0, i64 %71
  %73 = load i8, ptr %72, align 1
  %74 = icmp ne i8 %73, 0
  br i1 %74, label %76, label %75

75:                                               ; preds = %70
  store i32 0, ptr %20, align 4
  br label %81

76:                                               ; preds = %70
  br label %77

77:                                               ; preds = %76, %64
  br label %78

78:                                               ; preds = %77
  %79 = load i64, ptr %21, align 8
  %80 = add nsw i64 %79, 1
  store i64 %80, ptr %21, align 8
  br label %60, !llvm.loop !55

81:                                               ; preds = %75, %60
  %82 = load i32, ptr %20, align 4
  %83 = icmp ne i32 %82, 0
  br i1 %83, label %84, label %91

84:                                               ; preds = %81
  %85 = load i64, ptr %18, align 8
  %86 = getelementptr inbounds [64 x i8], ptr %13, i64 0, i64 %85
  store i8 1, ptr %86, align 1
  %87 = load ptr, ptr %12, align 8
  %88 = load i64, ptr %15, align 8
  %89 = add nsw i64 %88, 1
  store i64 %89, ptr %15, align 8
  %90 = load i64, ptr %18, align 8
  call void @setv(ptr noundef %87, i64 noundef %88, i64 noundef %90)
  store i32 1, ptr %16, align 4
  br label %91

91:                                               ; preds = %84, %81
  br label %92

92:                                               ; preds = %91, %55
  %93 = load i64, ptr %17, align 8
  %94 = add nsw i64 %93, 1
  store i64 %94, ptr %17, align 8
  br label %43, !llvm.loop !56

95:                                               ; preds = %43
  br label %39, !llvm.loop !57

96:                                               ; preds = %39
  %97 = load i64, ptr %15, align 8
  ret i64 %97
}

; Function Attrs: noinline nounwind optnone sspstrong uwtable
define internal i64 @frontier_missing(ptr noundef %0, i64 noundef %1, ptr noundef %2, ptr noundef %3, i64 noundef %4, ptr noundef %5) #0 {
  %7 = alloca ptr, align 8
  %8 = alloca i64, align 8
  %9 = alloca ptr, align 8
  %10 = alloca ptr, align 8
  %11 = alloca i64, align 8
  %12 = alloca ptr, align 8
  %13 = alloca i64, align 8
  %14 = alloca i64, align 8
  %15 = alloca i64, align 8
  %16 = alloca i64, align 8
  %17 = alloca i32, align 4
  %18 = alloca i64, align 8
  store ptr %0, ptr %7, align 8
  store i64 %1, ptr %8, align 8
  store ptr %2, ptr %9, align 8
  store ptr %3, ptr %10, align 8
  store i64 %4, ptr %11, align 8
  store ptr %5, ptr %12, align 8
  store i64 0, ptr %13, align 8
  store i64 0, ptr %14, align 8
  br label %19

19:                                               ; preds = %69, %6
  %20 = load i64, ptr %14, align 8
  %21 = load i64, ptr %11, align 8
  %22 = icmp slt i64 %20, %21
  br i1 %22, label %23, label %72

23:                                               ; preds = %19
  %24 = load ptr, ptr %9, align 8
  %25 = load i64, ptr %14, align 8
  %26 = call i64 @getv(ptr noundef %24, i64 noundef %25)
  store i64 %26, ptr %15, align 8
  %27 = load ptr, ptr %7, align 8
  %28 = load i64, ptr %15, align 8
  %29 = call i64 @getv(ptr noundef %27, i64 noundef %28)
  %30 = icmp ne i64 %29, 0
  br i1 %30, label %31, label %32

31:                                               ; preds = %23
  br label %69

32:                                               ; preds = %23
  %33 = load ptr, ptr %10, align 8
  %34 = load i64, ptr %14, align 8
  %35 = call i64 @getv(ptr noundef %33, i64 noundef %34)
  store i64 %35, ptr %16, align 8
  store i32 0, ptr %17, align 4
  store i64 0, ptr %18, align 8
  br label %36

36:                                               ; preds = %57, %32
  %37 = load i64, ptr %18, align 8
  %38 = load i64, ptr %8, align 8
  %39 = icmp slt i64 %37, %38
  br i1 %39, label %40, label %60

40:                                               ; preds = %36
  %41 = load i64, ptr %16, align 8
  %42 = load i64, ptr %18, align 8
  %43 = lshr i64 %41, %42
  %44 = and i64 %43, 1
  %45 = icmp ne i64 %44, 0
  br i1 %45, label %46, label %56

46:                                               ; preds = %40
  %47 = load ptr, ptr %7, align 8
  %48 = load i64, ptr %18, align 8
  %49 = call i64 @getv(ptr noundef %47, i64 noundef %48)
  %50 = icmp ne i64 %49, 0
  br i1 %50, label %56, label %51

51:                                               ; preds = %46
  %52 = load ptr, ptr %12, align 8
  %53 = load i64, ptr %13, align 8
  %54 = add nsw i64 %53, 1
  store i64 %54, ptr %13, align 8
  %55 = load i64, ptr %18, align 8
  call void @setv(ptr noundef %52, i64 noundef %53, i64 noundef %55)
  store i32 1, ptr %17, align 4
  br label %60

56:                                               ; preds = %46, %40
  br label %57

57:                                               ; preds = %56
  %58 = load i64, ptr %18, align 8
  %59 = add nsw i64 %58, 1
  store i64 %59, ptr %18, align 8
  br label %36, !llvm.loop !58

60:                                               ; preds = %51, %36
  %61 = load i32, ptr %17, align 4
  %62 = icmp ne i32 %61, 0
  br i1 %62, label %63, label %68

63:                                               ; preds = %60
  %64 = load ptr, ptr %12, align 8
  %65 = load i64, ptr %13, align 8
  %66 = add nsw i64 %65, 1
  store i64 %66, ptr %13, align 8
  %67 = load i64, ptr %15, align 8
  call void @setv(ptr noundef %64, i64 noundef %65, i64 noundef %67)
  br label %68

68:                                               ; preds = %63, %60
  br label %69

69:                                               ; preds = %68, %31
  %70 = load i64, ptr %14, align 8
  %71 = add nsw i64 %70, 1
  store i64 %71, ptr %14, align 8
  br label %19, !llvm.loop !59

72:                                               ; preds = %19
  %73 = load i64, ptr %13, align 8
  ret i64 %73
}

; Function Attrs: noinline nounwind optnone sspstrong uwtable
define internal i64 @bfs(ptr noundef %0, i64 noundef %1, i64 noundef %2, ptr noundef %3) #0 {
  %5 = alloca ptr, align 8
  %6 = alloca i64, align 8
  %7 = alloca i64, align 8
  %8 = alloca ptr, align 8
  %9 = alloca [64 x i64], align 16
  %10 = alloca [64 x i64], align 16
  %11 = alloca i64, align 8
  %12 = alloca i64, align 8
  %13 = alloca i64, align 8
  %14 = alloca i64, align 8
  %15 = alloca i64, align 8
  %16 = alloca i64, align 8
  store ptr %0, ptr %5, align 8
  store i64 %1, ptr %6, align 8
  store i64 %2, ptr %7, align 8
  store ptr %3, ptr %8, align 8
  call void @llvm.memset.p0.i64(ptr align 16 %9, i8 0, i64 512, i1 false)
  store i64 0, ptr %11, align 8
  store i64 0, ptr %12, align 8
  store i64 0, ptr %13, align 8
  %17 = load i64, ptr %7, align 8
  %18 = getelementptr inbounds [64 x i64], ptr %9, i64 0, i64 %17
  store i64 1, ptr %18, align 8
  %19 = load i64, ptr %7, align 8
  %20 = load i64, ptr %12, align 8
  %21 = add nsw i64 %20, 1
  store i64 %21, ptr %12, align 8
  %22 = getelementptr inbounds [64 x i64], ptr %10, i64 0, i64 %20
  store i64 %19, ptr %22, align 8
  br label %23

23:                                               ; preds = %66, %4
  %24 = load i64, ptr %11, align 8
  %25 = load i64, ptr %12, align 8
  %26 = icmp slt i64 %24, %25
  br i1 %26, label %27, label %67

27:                                               ; preds = %23
  %28 = load i64, ptr %11, align 8
  %29 = add nsw i64 %28, 1
  store i64 %29, ptr %11, align 8
  %30 = getelementptr inbounds [64 x i64], ptr %10, i64 0, i64 %28
  %31 = load i64, ptr %30, align 8
  store i64 %31, ptr %14, align 8
  %32 = load ptr, ptr %8, align 8
  %33 = load i64, ptr %13, align 8
  %34 = add nsw i64 %33, 1
  store i64 %34, ptr %13, align 8
  %35 = load i64, ptr %14, align 8
  call void @setv(ptr noundef %32, i64 noundef %33, i64 noundef %35)
  %36 = load ptr, ptr %5, align 8
  %37 = load i64, ptr %14, align 8
  %38 = call i64 @getv(ptr noundef %36, i64 noundef %37)
  store i64 %38, ptr %15, align 8
  store i64 0, ptr %16, align 8
  br label %39

39:                                               ; preds = %63, %27
  %40 = load i64, ptr %16, align 8
  %41 = load i64, ptr %6, align 8
  %42 = icmp slt i64 %40, %41
  br i1 %42, label %43, label %66

43:                                               ; preds = %39
  %44 = load i64, ptr %15, align 8
  %45 = load i64, ptr %16, align 8
  %46 = lshr i64 %44, %45
  %47 = and i64 %46, 1
  %48 = icmp ne i64 %47, 0
  br i1 %48, label %49, label %62

49:                                               ; preds = %43
  %50 = load i64, ptr %16, align 8
  %51 = getelementptr inbounds [64 x i64], ptr %9, i64 0, i64 %50
  %52 = load i64, ptr %51, align 8
  %53 = icmp ne i64 %52, 0
  br i1 %53, label %61, label %54

54:                                               ; preds = %49
  %55 = load i64, ptr %16, align 8
  %56 = getelementptr inbounds [64 x i64], ptr %9, i64 0, i64 %55
  store i64 1, ptr %56, align 8
  %57 = load i64, ptr %16, align 8
  %58 = load i64, ptr %12, align 8
  %59 = add nsw i64 %58, 1
  store i64 %59, ptr %12, align 8
  %60 = getelementptr inbounds [64 x i64], ptr %10, i64 0, i64 %58
  store i64 %57, ptr %60, align 8
  br label %61

61:                                               ; preds = %54, %49
  br label %62

62:                                               ; preds = %61, %43
  br label %63

63:                                               ; preds = %62
  %64 = load i64, ptr %16, align 8
  %65 = add nsw i64 %64, 1
  store i64 %65, ptr %16, align 8
  br label %39, !llvm.loop !60

66:                                               ; preds = %39
  br label %23, !llvm.loop !61

67:                                               ; preds = %23
  %68 = load i64, ptr %13, align 8
  ret i64 %68
}

; Function Attrs: noinline nounwind optnone sspstrong uwtable
define internal i64 @topo(ptr noundef %0, ptr noundef %1, i64 noundef %2, i64 noundef %3, ptr noundef %4) #0 {
  %6 = alloca ptr, align 8
  %7 = alloca ptr, align 8
  %8 = alloca i64, align 8
  %9 = alloca i64, align 8
  %10 = alloca ptr, align 8
  %11 = alloca [64 x i64], align 16
  %12 = alloca [64 x i64], align 16
  %13 = alloca i64, align 8
  %14 = alloca i64, align 8
  %15 = alloca i64, align 8
  %16 = alloca i64, align 8
  %17 = alloca i64, align 8
  %18 = alloca i64, align 8
  %19 = alloca i64, align 8
  %20 = alloca i64, align 8
  store ptr %0, ptr %6, align 8
  store ptr %1, ptr %7, align 8
  store i64 %2, ptr %8, align 8
  store i64 %3, ptr %9, align 8
  store ptr %4, ptr %10, align 8
  call void @llvm.memset.p0.i64(ptr align 16 %11, i8 0, i64 512, i1 false)
  store i64 0, ptr %13, align 8
  store i64 0, ptr %14, align 8
  store i64 0, ptr %15, align 8
  store i64 0, ptr %16, align 8
  br label %21

21:                                               ; preds = %32, %5
  %22 = load i64, ptr %16, align 8
  %23 = load i64, ptr %8, align 8
  %24 = icmp slt i64 %22, %23
  br i1 %24, label %25, label %35

25:                                               ; preds = %21
  %26 = load ptr, ptr %7, align 8
  %27 = load i64, ptr %16, align 8
  %28 = call i64 @getv(ptr noundef %26, i64 noundef %27)
  %29 = getelementptr inbounds [64 x i64], ptr %11, i64 0, i64 %28
  %30 = load i64, ptr %29, align 8
  %31 = add nsw i64 %30, 1
  store i64 %31, ptr %29, align 8
  br label %32

32:                                               ; preds = %25
  %33 = load i64, ptr %16, align 8
  %34 = add nsw i64 %33, 1
  store i64 %34, ptr %16, align 8
  br label %21, !llvm.loop !62

35:                                               ; preds = %21
  store i64 0, ptr %17, align 8
  br label %36

36:                                               ; preds = %51, %35
  %37 = load i64, ptr %17, align 8
  %38 = load i64, ptr %9, align 8
  %39 = icmp slt i64 %37, %38
  br i1 %39, label %40, label %54

40:                                               ; preds = %36
  %41 = load i64, ptr %17, align 8
  %42 = getelementptr inbounds [64 x i64], ptr %11, i64 0, i64 %41
  %43 = load i64, ptr %42, align 8
  %44 = icmp eq i64 %43, 0
  br i1 %44, label %45, label %50

45:                                               ; preds = %40
  %46 = load i64, ptr %17, align 8
  %47 = load i64, ptr %14, align 8
  %48 = add nsw i64 %47, 1
  store i64 %48, ptr %14, align 8
  %49 = getelementptr inbounds [64 x i64], ptr %12, i64 0, i64 %47
  store i64 %46, ptr %49, align 8
  br label %50

50:                                               ; preds = %45, %40
  br label %51

51:                                               ; preds = %50
  %52 = load i64, ptr %17, align 8
  %53 = add nsw i64 %52, 1
  store i64 %53, ptr %17, align 8
  br label %36, !llvm.loop !63

54:                                               ; preds = %36
  br label %55

55:                                               ; preds = %97, %54
  %56 = load i64, ptr %13, align 8
  %57 = load i64, ptr %14, align 8
  %58 = icmp slt i64 %56, %57
  br i1 %58, label %59, label %98

59:                                               ; preds = %55
  %60 = load i64, ptr %13, align 8
  %61 = add nsw i64 %60, 1
  store i64 %61, ptr %13, align 8
  %62 = getelementptr inbounds [64 x i64], ptr %12, i64 0, i64 %60
  %63 = load i64, ptr %62, align 8
  store i64 %63, ptr %18, align 8
  %64 = load ptr, ptr %10, align 8
  %65 = load i64, ptr %15, align 8
  %66 = add nsw i64 %65, 1
  store i64 %66, ptr %15, align 8
  %67 = load i64, ptr %18, align 8
  call void @setv(ptr noundef %64, i64 noundef %65, i64 noundef %67)
  store i64 0, ptr %19, align 8
  br label %68

68:                                               ; preds = %94, %59
  %69 = load i64, ptr %19, align 8
  %70 = load i64, ptr %8, align 8
  %71 = icmp slt i64 %69, %70
  br i1 %71, label %72, label %97

72:                                               ; preds = %68
  %73 = load ptr, ptr %6, align 8
  %74 = load i64, ptr %19, align 8
  %75 = call i64 @getv(ptr noundef %73, i64 noundef %74)
  %76 = load i64, ptr %18, align 8
  %77 = icmp eq i64 %75, %76
  br i1 %77, label %78, label %93

78:                                               ; preds = %72
  %79 = load ptr, ptr %7, align 8
  %80 = load i64, ptr %19, align 8
  %81 = call i64 @getv(ptr noundef %79, i64 noundef %80)
  store i64 %81, ptr %20, align 8
  %82 = load i64, ptr %20, align 8
  %83 = getelementptr inbounds [64 x i64], ptr %11, i64 0, i64 %82
  %84 = load i64, ptr %83, align 8
  %85 = add nsw i64 %84, -1
  store i64 %85, ptr %83, align 8
  %86 = icmp eq i64 %85, 0
  br i1 %86, label %87, label %92

87:                                               ; preds = %78
  %88 = load i64, ptr %20, align 8
  %89 = load i64, ptr %14, align 8
  %90 = add nsw i64 %89, 1
  store i64 %90, ptr %14, align 8
  %91 = getelementptr inbounds [64 x i64], ptr %12, i64 0, i64 %89
  store i64 %88, ptr %91, align 8
  br label %92

92:                                               ; preds = %87, %78
  br label %93

93:                                               ; preds = %92, %72
  br label %94

94:                                               ; preds = %93
  %95 = load i64, ptr %19, align 8
  %96 = add nsw i64 %95, 1
  store i64 %96, ptr %19, align 8
  br label %68, !llvm.loop !64

97:                                               ; preds = %68
  br label %55, !llvm.loop !65

98:                                               ; preds = %55
  %99 = load i64, ptr %15, align 8
  ret i64 %99
}

; Function Attrs: noinline nounwind optnone sspstrong uwtable
define internal i64 @uf_union(ptr noundef %0, i64 noundef %1, i64 noundef %2) #0 {
  %4 = alloca i64, align 8
  %5 = alloca ptr, align 8
  %6 = alloca i64, align 8
  %7 = alloca i64, align 8
  store ptr %0, ptr %5, align 8
  store i64 %1, ptr %6, align 8
  store i64 %2, ptr %7, align 8
  %8 = load ptr, ptr %5, align 8
  %9 = load i64, ptr %6, align 8
  %10 = call i64 @uf_find(ptr noundef %8, i64 noundef %9)
  store i64 %10, ptr %6, align 8
  %11 = load ptr, ptr %5, align 8
  %12 = load i64, ptr %7, align 8
  %13 = call i64 @uf_find(ptr noundef %11, i64 noundef %12)
  store i64 %13, ptr %7, align 8
  %14 = load i64, ptr %6, align 8
  %15 = load i64, ptr %7, align 8
  %16 = icmp eq i64 %14, %15
  br i1 %16, label %17, label %18

17:                                               ; preds = %3
  store i64 0, ptr %4, align 8
  br label %23

18:                                               ; preds = %3
  %19 = load i64, ptr %6, align 8
  %20 = load ptr, ptr %5, align 8
  %21 = load i64, ptr %7, align 8
  %22 = getelementptr inbounds i64, ptr %20, i64 %21
  store i64 %19, ptr %22, align 8
  store i64 1, ptr %4, align 8
  br label %23

23:                                               ; preds = %18, %17
  %24 = load i64, ptr %4, align 8
  ret i64 %24
}

; Function Attrs: noinline nounwind optnone sspstrong uwtable
define internal i64 @uf_find(ptr noundef %0, i64 noundef %1) #0 {
  %3 = alloca ptr, align 8
  %4 = alloca i64, align 8
  store ptr %0, ptr %3, align 8
  store i64 %1, ptr %4, align 8
  br label %5

5:                                                ; preds = %12, %2
  %6 = load ptr, ptr %3, align 8
  %7 = load i64, ptr %4, align 8
  %8 = getelementptr inbounds i64, ptr %6, i64 %7
  %9 = load i64, ptr %8, align 8
  %10 = load i64, ptr %4, align 8
  %11 = icmp ne i64 %9, %10
  br i1 %11, label %12, label %27

12:                                               ; preds = %5
  %13 = load ptr, ptr %3, align 8
  %14 = load ptr, ptr %3, align 8
  %15 = load i64, ptr %4, align 8
  %16 = getelementptr inbounds i64, ptr %14, i64 %15
  %17 = load i64, ptr %16, align 8
  %18 = getelementptr inbounds i64, ptr %13, i64 %17
  %19 = load i64, ptr %18, align 8
  %20 = load ptr, ptr %3, align 8
  %21 = load i64, ptr %4, align 8
  %22 = getelementptr inbounds i64, ptr %20, i64 %21
  store i64 %19, ptr %22, align 8
  %23 = load ptr, ptr %3, align 8
  %24 = load i64, ptr %4, align 8
  %25 = getelementptr inbounds i64, ptr %23, i64 %24
  %26 = load i64, ptr %25, align 8
  store i64 %26, ptr %4, align 8
  br label %5, !llvm.loop !66

27:                                               ; preds = %5
  %28 = load i64, ptr %4, align 8
  ret i64 %28
}

; Function Attrs: noinline nounwind optnone sspstrong uwtable
define internal void @bitset_closure(ptr noundef %0, i64 noundef %1, ptr noundef %2) #0 {
  %4 = alloca ptr, align 8
  %5 = alloca i64, align 8
  %6 = alloca ptr, align 8
  %7 = alloca [64 x i64], align 16
  %8 = alloca i64, align 8
  %9 = alloca i64, align 8
  %10 = alloca i64, align 8
  %11 = alloca i64, align 8
  store ptr %0, ptr %4, align 8
  store i64 %1, ptr %5, align 8
  store ptr %2, ptr %6, align 8
  store i64 0, ptr %8, align 8
  br label %12

12:                                               ; preds = %22, %3
  %13 = load i64, ptr %8, align 8
  %14 = load i64, ptr %5, align 8
  %15 = icmp slt i64 %13, %14
  br i1 %15, label %16, label %25

16:                                               ; preds = %12
  %17 = load ptr, ptr %4, align 8
  %18 = load i64, ptr %8, align 8
  %19 = call i64 @getv(ptr noundef %17, i64 noundef %18)
  %20 = load i64, ptr %8, align 8
  %21 = getelementptr inbounds [64 x i64], ptr %7, i64 0, i64 %20
  store i64 %19, ptr %21, align 8
  br label %22

22:                                               ; preds = %16
  %23 = load i64, ptr %8, align 8
  %24 = add nsw i64 %23, 1
  store i64 %24, ptr %8, align 8
  br label %12, !llvm.loop !67

25:                                               ; preds = %12
  store i64 0, ptr %9, align 8
  br label %26

26:                                               ; preds = %56, %25
  %27 = load i64, ptr %9, align 8
  %28 = load i64, ptr %5, align 8
  %29 = icmp slt i64 %27, %28
  br i1 %29, label %30, label %59

30:                                               ; preds = %26
  store i64 0, ptr %10, align 8
  br label %31

31:                                               ; preds = %52, %30
  %32 = load i64, ptr %10, align 8
  %33 = load i64, ptr %5, align 8
  %34 = icmp slt i64 %32, %33
  br i1 %34, label %35, label %55

35:                                               ; preds = %31
  %36 = load i64, ptr %10, align 8
  %37 = getelementptr inbounds [64 x i64], ptr %7, i64 0, i64 %36
  %38 = load i64, ptr %37, align 8
  %39 = load i64, ptr %9, align 8
  %40 = lshr i64 %38, %39
  %41 = and i64 %40, 1
  %42 = icmp ne i64 %41, 0
  br i1 %42, label %43, label %51

43:                                               ; preds = %35
  %44 = load i64, ptr %9, align 8
  %45 = getelementptr inbounds [64 x i64], ptr %7, i64 0, i64 %44
  %46 = load i64, ptr %45, align 8
  %47 = load i64, ptr %10, align 8
  %48 = getelementptr inbounds [64 x i64], ptr %7, i64 0, i64 %47
  %49 = load i64, ptr %48, align 8
  %50 = or i64 %49, %46
  store i64 %50, ptr %48, align 8
  br label %51

51:                                               ; preds = %43, %35
  br label %52

52:                                               ; preds = %51
  %53 = load i64, ptr %10, align 8
  %54 = add nsw i64 %53, 1
  store i64 %54, ptr %10, align 8
  br label %31, !llvm.loop !68

55:                                               ; preds = %31
  br label %56

56:                                               ; preds = %55
  %57 = load i64, ptr %9, align 8
  %58 = add nsw i64 %57, 1
  store i64 %58, ptr %9, align 8
  br label %26, !llvm.loop !69

59:                                               ; preds = %26
  store i64 0, ptr %11, align 8
  br label %60

60:                                               ; preds = %70, %59
  %61 = load i64, ptr %11, align 8
  %62 = load i64, ptr %5, align 8
  %63 = icmp slt i64 %61, %62
  br i1 %63, label %64, label %73

64:                                               ; preds = %60
  %65 = load ptr, ptr %6, align 8
  %66 = load i64, ptr %11, align 8
  %67 = load i64, ptr %11, align 8
  %68 = getelementptr inbounds [64 x i64], ptr %7, i64 0, i64 %67
  %69 = load i64, ptr %68, align 8
  call void @setv(ptr noundef %65, i64 noundef %66, i64 noundef %69)
  br label %70

70:                                               ; preds = %64
  %71 = load i64, ptr %11, align 8
  %72 = add nsw i64 %71, 1
  store i64 %72, ptr %11, align 8
  br label %60, !llvm.loop !70

73:                                               ; preds = %60
  ret void
}

; Function Attrs: noinline nounwind optnone sspstrong uwtable
define internal void @index_add(ptr noundef %0, ptr noundef %1, i64 noundef %2, ptr noundef %3, i64 noundef %4, i64 noundef %5) #0 {
  %7 = alloca ptr, align 8
  %8 = alloca ptr, align 8
  %9 = alloca i64, align 8
  %10 = alloca ptr, align 8
  %11 = alloca i64, align 8
  %12 = alloca i64, align 8
  %13 = alloca i64, align 8
  store ptr %0, ptr %7, align 8
  store ptr %1, ptr %8, align 8
  store i64 %2, ptr %9, align 8
  store ptr %3, ptr %10, align 8
  store i64 %4, ptr %11, align 8
  store i64 %5, ptr %12, align 8
  %14 = load i64, ptr %12, align 8
  %15 = load i64, ptr %9, align 8
  %16 = srem i64 %14, %15
  store i64 %16, ptr %13, align 8
  %17 = load ptr, ptr %7, align 8
  %18 = load i64, ptr %11, align 8
  %19 = load i64, ptr %12, align 8
  call void @setv(ptr noundef %17, i64 noundef %18, i64 noundef %19)
  %20 = load ptr, ptr %10, align 8
  %21 = load i64, ptr %11, align 8
  %22 = load ptr, ptr %8, align 8
  %23 = load i64, ptr %13, align 8
  %24 = call i64 @getv(ptr noundef %22, i64 noundef %23)
  call void @setv(ptr noundef %20, i64 noundef %21, i64 noundef %24)
  %25 = load ptr, ptr %8, align 8
  %26 = load i64, ptr %13, align 8
  %27 = load i64, ptr %11, align 8
  call void @setv(ptr noundef %25, i64 noundef %26, i64 noundef %27)
  ret void
}

; Function Attrs: noinline nounwind optnone sspstrong uwtable
define internal i64 @index_remove(ptr noundef %0, i64 noundef %1) #0 {
  %3 = alloca ptr, align 8
  %4 = alloca i64, align 8
  %5 = alloca i64, align 8
  store ptr %0, ptr %3, align 8
  store i64 %1, ptr %4, align 8
  %6 = load ptr, ptr %3, align 8
  %7 = load i64, ptr %4, align 8
  %8 = call i64 @getv(ptr noundef %6, i64 noundef %7)
  store i64 %8, ptr %5, align 8
  %9 = load ptr, ptr %3, align 8
  %10 = load i64, ptr %4, align 8
  call void @setv(ptr noundef %9, i64 noundef %10, i64 noundef -1)
  %11 = load i64, ptr %5, align 8
  ret i64 %11
}

; Function Attrs: noinline nounwind optnone sspstrong uwtable
define internal i64 @bce_q16(i64 noundef %0, i64 noundef %1) #0 {
  %3 = alloca i64, align 8
  %4 = alloca i64, align 8
  %5 = alloca double, align 8
  %6 = alloca double, align 8
  %7 = alloca double, align 8
  store i64 %0, ptr %3, align 8
  store i64 %1, ptr %4, align 8
  %8 = load i64, ptr %3, align 8
  %9 = sitofp i64 %8 to double
  %10 = fdiv double %9, 6.553600e+04
  store double %10, ptr %5, align 8
  %11 = load i64, ptr %4, align 8
  %12 = sitofp i64 %11 to double
  %13 = fdiv double %12, 6.553600e+04
  store double %13, ptr %6, align 8
  %14 = load double, ptr %6, align 8
  %15 = load double, ptr %5, align 8
  %16 = fneg double %15
  %17 = call double @exp(double noundef %16) #6
  %18 = fadd double 1.000000e+00, %17
  %19 = fdiv double 1.000000e+00, %18
  %20 = call double @log(double noundef %19) #6
  %21 = load double, ptr %6, align 8
  %22 = fsub double 1.000000e+00, %21
  %23 = load double, ptr %5, align 8
  %24 = fneg double %23
  %25 = call double @exp(double noundef %24) #6
  %26 = fadd double 1.000000e+00, %25
  %27 = fdiv double 1.000000e+00, %26
  %28 = fsub double 1.000000e+00, %27
  %29 = call double @log(double noundef %28) #6
  %30 = fmul double %22, %29
  %31 = call double @llvm.fmuladd.f64(double %14, double %20, double %30)
  %32 = fneg double %31
  store double %32, ptr %7, align 8
  %33 = load double, ptr %7, align 8
  %34 = fmul double %33, 6.553600e+04
  %35 = fptosi double %34 to i64
  ret i64 %35
}

; Function Attrs: noinline nounwind optnone sspstrong uwtable
define internal void @backward_matvec(ptr noundef %0, i64 noundef %1, i64 noundef %2, ptr noundef %3, ptr noundef %4) #0 {
  %6 = alloca ptr, align 8
  %7 = alloca i64, align 8
  %8 = alloca i64, align 8
  %9 = alloca ptr, align 8
  %10 = alloca ptr, align 8
  %11 = alloca i64, align 8
  %12 = alloca i64, align 8
  %13 = alloca i64, align 8
  store ptr %0, ptr %6, align 8
  store i64 %1, ptr %7, align 8
  store i64 %2, ptr %8, align 8
  store ptr %3, ptr %9, align 8
  store ptr %4, ptr %10, align 8
  store i64 0, ptr %11, align 8
  br label %14

14:                                               ; preds = %44, %5
  %15 = load i64, ptr %11, align 8
  %16 = load i64, ptr %8, align 8
  %17 = icmp slt i64 %15, %16
  br i1 %17, label %18, label %47

18:                                               ; preds = %14
  store i64 0, ptr %12, align 8
  store i64 0, ptr %13, align 8
  br label %19

19:                                               ; preds = %37, %18
  %20 = load i64, ptr %13, align 8
  %21 = load i64, ptr %7, align 8
  %22 = icmp slt i64 %20, %21
  br i1 %22, label %23, label %40

23:                                               ; preds = %19
  %24 = load ptr, ptr %6, align 8
  %25 = load i64, ptr %13, align 8
  %26 = load i64, ptr %8, align 8
  %27 = mul nsw i64 %25, %26
  %28 = load i64, ptr %11, align 8
  %29 = add nsw i64 %27, %28
  %30 = call i64 @getv(ptr noundef %24, i64 noundef %29)
  %31 = load ptr, ptr %9, align 8
  %32 = load i64, ptr %13, align 8
  %33 = call i64 @getv(ptr noundef %31, i64 noundef %32)
  %34 = call i64 @qmul(i64 noundef %30, i64 noundef %33)
  %35 = load i64, ptr %12, align 8
  %36 = add nsw i64 %35, %34
  store i64 %36, ptr %12, align 8
  br label %37

37:                                               ; preds = %23
  %38 = load i64, ptr %13, align 8
  %39 = add nsw i64 %38, 1
  store i64 %39, ptr %13, align 8
  br label %19, !llvm.loop !71

40:                                               ; preds = %19
  %41 = load ptr, ptr %10, align 8
  %42 = load i64, ptr %11, align 8
  %43 = load i64, ptr %12, align 8
  call void @setv(ptr noundef %41, i64 noundef %42, i64 noundef %43)
  br label %44

44:                                               ; preds = %40
  %45 = load i64, ptr %11, align 8
  %46 = add nsw i64 %45, 1
  store i64 %46, ptr %11, align 8
  br label %14, !llvm.loop !72

47:                                               ; preds = %14
  ret void
}

; Function Attrs: noinline nounwind optnone sspstrong uwtable
define internal i64 @adam_step(i64 noundef %0, i64 noundef %1, ptr noundef %2, ptr noundef %3, i64 noundef %4, i64 noundef %5, i64 noundef %6, i64 noundef %7, i64 noundef %8) #0 {
  %10 = alloca i64, align 8
  %11 = alloca i64, align 8
  %12 = alloca ptr, align 8
  %13 = alloca ptr, align 8
  %14 = alloca i64, align 8
  %15 = alloca i64, align 8
  %16 = alloca i64, align 8
  %17 = alloca i64, align 8
  %18 = alloca i64, align 8
  %19 = alloca double, align 8
  %20 = alloca double, align 8
  %21 = alloca double, align 8
  %22 = alloca double, align 8
  %23 = alloca double, align 8
  %24 = alloca double, align 8
  %25 = alloca double, align 8
  %26 = alloca double, align 8
  %27 = alloca double, align 8
  store i64 %0, ptr %10, align 8
  store i64 %1, ptr %11, align 8
  store ptr %2, ptr %12, align 8
  store ptr %3, ptr %13, align 8
  store i64 %4, ptr %14, align 8
  store i64 %5, ptr %15, align 8
  store i64 %6, ptr %16, align 8
  store i64 %7, ptr %17, align 8
  store i64 %8, ptr %18, align 8
  %28 = load i64, ptr %16, align 8
  %29 = sitofp i64 %28 to double
  %30 = fdiv double %29, 6.553600e+04
  store double %30, ptr %19, align 8
  %31 = load i64, ptr %17, align 8
  %32 = sitofp i64 %31 to double
  %33 = fdiv double %32, 6.553600e+04
  store double %33, ptr %20, align 8
  %34 = load ptr, ptr %12, align 8
  %35 = load i64, ptr %34, align 8
  %36 = sitofp i64 %35 to double
  %37 = fdiv double %36, 6.553600e+04
  store double %37, ptr %21, align 8
  %38 = load ptr, ptr %13, align 8
  %39 = load i64, ptr %38, align 8
  %40 = sitofp i64 %39 to double
  %41 = fdiv double %40, 6.553600e+04
  store double %41, ptr %22, align 8
  %42 = load i64, ptr %11, align 8
  %43 = sitofp i64 %42 to double
  %44 = fdiv double %43, 6.553600e+04
  store double %44, ptr %23, align 8
  %45 = load i64, ptr %15, align 8
  %46 = sitofp i64 %45 to double
  %47 = fdiv double %46, 6.553600e+04
  store double %47, ptr %24, align 8
  %48 = load double, ptr %19, align 8
  %49 = load double, ptr %21, align 8
  %50 = load double, ptr %19, align 8
  %51 = fsub double 1.000000e+00, %50
  %52 = load double, ptr %23, align 8
  %53 = fmul double %51, %52
  %54 = call double @llvm.fmuladd.f64(double %48, double %49, double %53)
  store double %54, ptr %21, align 8
  %55 = load double, ptr %20, align 8
  %56 = load double, ptr %22, align 8
  %57 = load double, ptr %20, align 8
  %58 = fsub double 1.000000e+00, %57
  %59 = load double, ptr %23, align 8
  %60 = fmul double %58, %59
  %61 = load double, ptr %23, align 8
  %62 = fmul double %60, %61
  %63 = call double @llvm.fmuladd.f64(double %55, double %56, double %62)
  store double %63, ptr %22, align 8
  %64 = load double, ptr %21, align 8
  %65 = load double, ptr %19, align 8
  %66 = load i64, ptr %14, align 8
  %67 = sitofp i64 %66 to double
  %68 = call double @pow(double noundef %65, double noundef %67) #6
  %69 = fsub double 1.000000e+00, %68
  %70 = fdiv double %64, %69
  store double %70, ptr %25, align 8
  %71 = load double, ptr %22, align 8
  %72 = load double, ptr %20, align 8
  %73 = load i64, ptr %14, align 8
  %74 = sitofp i64 %73 to double
  %75 = call double @pow(double noundef %72, double noundef %74) #6
  %76 = fsub double 1.000000e+00, %75
  %77 = fdiv double %71, %76
  store double %77, ptr %26, align 8
  %78 = load i64, ptr %10, align 8
  %79 = sitofp i64 %78 to double
  %80 = fdiv double %79, 6.553600e+04
  %81 = load double, ptr %24, align 8
  %82 = load double, ptr %25, align 8
  %83 = fmul double %81, %82
  %84 = load double, ptr %26, align 8
  %85 = call double @sqrt(double noundef %84) #6
  %86 = load i64, ptr %18, align 8
  %87 = sitofp i64 %86 to double
  %88 = fdiv double %87, 6.553600e+04
  %89 = fadd double %85, %88
  %90 = fdiv double %83, %89
  %91 = fsub double %80, %90
  store double %91, ptr %27, align 8
  %92 = load double, ptr %21, align 8
  %93 = fmul double %92, 6.553600e+04
  %94 = fptosi double %93 to i64
  %95 = load ptr, ptr %12, align 8
  store i64 %94, ptr %95, align 8
  %96 = load double, ptr %22, align 8
  %97 = fmul double %96, 6.553600e+04
  %98 = fptosi double %97 to i64
  %99 = load ptr, ptr %13, align 8
  store i64 %98, ptr %99, align 8
  %100 = load double, ptr %27, align 8
  %101 = fmul double %100, 6.553600e+04
  %102 = fptosi double %101 to i64
  ret i64 %102
}

; Function Attrs: noinline nounwind optnone sspstrong uwtable
define internal void @fused_linear_relu(ptr noundef %0, ptr noundef %1, i64 noundef %2, i64 noundef %3, ptr noundef %4, ptr noundef %5) #0 {
  %7 = alloca ptr, align 8
  %8 = alloca ptr, align 8
  %9 = alloca i64, align 8
  %10 = alloca i64, align 8
  %11 = alloca ptr, align 8
  %12 = alloca ptr, align 8
  %13 = alloca [64 x i64], align 16
  %14 = alloca i64, align 8
  store ptr %0, ptr %7, align 8
  store ptr %1, ptr %8, align 8
  store i64 %2, ptr %9, align 8
  store i64 %3, ptr %10, align 8
  store ptr %4, ptr %11, align 8
  store ptr %5, ptr %12, align 8
  %15 = load ptr, ptr %7, align 8
  %16 = load i64, ptr %9, align 8
  %17 = load i64, ptr %10, align 8
  %18 = load ptr, ptr %11, align 8
  %19 = load ptr, ptr %8, align 8
  %20 = getelementptr inbounds [64 x i64], ptr %13, i64 0, i64 0
  call void @matvec(ptr noundef %15, i64 noundef %16, i64 noundef %17, ptr noundef %18, ptr noundef %19, ptr noundef %20)
  store i64 0, ptr %14, align 8
  br label %21

21:                                               ; preds = %39, %6
  %22 = load i64, ptr %14, align 8
  %23 = load i64, ptr %9, align 8
  %24 = icmp slt i64 %22, %23
  br i1 %24, label %25, label %42

25:                                               ; preds = %21
  %26 = load ptr, ptr %12, align 8
  %27 = load i64, ptr %14, align 8
  %28 = load i64, ptr %14, align 8
  %29 = getelementptr inbounds [64 x i64], ptr %13, i64 0, i64 %28
  %30 = load i64, ptr %29, align 8
  %31 = icmp sgt i64 %30, 0
  br i1 %31, label %32, label %36

32:                                               ; preds = %25
  %33 = load i64, ptr %14, align 8
  %34 = getelementptr inbounds [64 x i64], ptr %13, i64 0, i64 %33
  %35 = load i64, ptr %34, align 8
  br label %37

36:                                               ; preds = %25
  br label %37

37:                                               ; preds = %36, %32
  %38 = phi i64 [ %35, %32 ], [ 0, %36 ]
  call void @setv(ptr noundef %26, i64 noundef %27, i64 noundef %38)
  br label %39

39:                                               ; preds = %37
  %40 = load i64, ptr %14, align 8
  %41 = add nsw i64 %40, 1
  store i64 %41, ptr %14, align 8
  br label %21, !llvm.loop !73

42:                                               ; preds = %21
  ret void
}

; Function Attrs: noinline nounwind optnone sspstrong uwtable
define internal void @fused_linear_ln(ptr noundef %0, ptr noundef %1, i64 noundef %2, i64 noundef %3, ptr noundef %4, ptr noundef %5, ptr noundef %6, ptr noundef %7) #0 {
  %9 = alloca ptr, align 8
  %10 = alloca ptr, align 8
  %11 = alloca i64, align 8
  %12 = alloca i64, align 8
  %13 = alloca ptr, align 8
  %14 = alloca ptr, align 8
  %15 = alloca ptr, align 8
  %16 = alloca ptr, align 8
  %17 = alloca [64 x i64], align 16
  %18 = alloca %struct.MaruArrayView, align 8
  store ptr %0, ptr %9, align 8
  store ptr %1, ptr %10, align 8
  store i64 %2, ptr %11, align 8
  store i64 %3, ptr %12, align 8
  store ptr %4, ptr %13, align 8
  store ptr %5, ptr %14, align 8
  store ptr %6, ptr %15, align 8
  store ptr %7, ptr %16, align 8
  %19 = load ptr, ptr %9, align 8
  %20 = load i64, ptr %11, align 8
  %21 = load i64, ptr %12, align 8
  %22 = load ptr, ptr %13, align 8
  %23 = load ptr, ptr %10, align 8
  %24 = getelementptr inbounds [64 x i64], ptr %17, i64 0, i64 0
  call void @matvec(ptr noundef %19, i64 noundef %20, i64 noundef %21, ptr noundef %22, ptr noundef %23, ptr noundef %24)
  %25 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %18, i32 0, i32 0
  %26 = getelementptr inbounds [64 x i64], ptr %17, i64 0, i64 0
  store ptr %26, ptr %25, align 8
  %27 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %18, i32 0, i32 1
  %28 = load i64, ptr %11, align 8
  store i64 %28, ptr %27, align 8
  %29 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %18, i32 0, i32 2
  store i64 8, ptr %29, align 8
  %30 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %18, i32 0, i32 3
  store i64 8, ptr %30, align 8
  %31 = load i64, ptr %11, align 8
  %32 = load ptr, ptr %14, align 8
  %33 = load ptr, ptr %15, align 8
  %34 = load ptr, ptr %16, align 8
  call void @layernorm(ptr noundef %18, i64 noundef %31, ptr noundef %32, ptr noundef %33, ptr noundef %34)
  ret void
}

; Function Attrs: noinline nounwind optnone sspstrong uwtable
define internal i64 @integrated_derive(ptr noundef %0, i64 noundef %1, ptr noundef %2, ptr noundef %3, ptr noundef %4, i64 noundef %5, ptr noundef %6) #0 {
  %8 = alloca ptr, align 8
  %9 = alloca i64, align 8
  %10 = alloca ptr, align 8
  %11 = alloca ptr, align 8
  %12 = alloca ptr, align 8
  %13 = alloca i64, align 8
  %14 = alloca ptr, align 8
  %15 = alloca [64 x i8], align 16
  %16 = alloca i64, align 8
  %17 = alloca [64 x i64], align 16
  %18 = alloca [64 x i64], align 16
  %19 = alloca [64 x i64], align 16
  %20 = alloca [64 x i64], align 16
  %21 = alloca i64, align 8
  %22 = alloca i64, align 8
  %23 = alloca i32, align 4
  %24 = alloca i64, align 8
  %25 = alloca i64, align 8
  %26 = alloca i64, align 8
  %27 = alloca i64, align 8
  %28 = alloca i64, align 8
  %29 = alloca %struct.MaruArrayView, align 8
  %30 = alloca %struct.MaruArrayView, align 8
  %31 = alloca %struct.MaruArrayView, align 8
  %32 = alloca %struct.MaruArrayView, align 8
  %33 = alloca i64, align 8
  %34 = alloca i64, align 8
  %35 = alloca i64, align 8
  store ptr %0, ptr %8, align 8
  store i64 %1, ptr %9, align 8
  store ptr %2, ptr %10, align 8
  store ptr %3, ptr %11, align 8
  store ptr %4, ptr %12, align 8
  store i64 %5, ptr %13, align 8
  store ptr %6, ptr %14, align 8
  call void @llvm.memset.p0.i64(ptr align 16 %15, i8 0, i64 64, i1 false)
  store i64 0, ptr %16, align 8
  br label %36

36:                                               ; preds = %49, %7
  %37 = load i64, ptr %16, align 8
  %38 = load i64, ptr %9, align 8
  %39 = icmp slt i64 %37, %38
  br i1 %39, label %40, label %52

40:                                               ; preds = %36
  %41 = load ptr, ptr %8, align 8
  %42 = load i64, ptr %16, align 8
  %43 = call i64 @getv(ptr noundef %41, i64 noundef %42)
  %44 = icmp ne i64 %43, 0
  %45 = zext i1 %44 to i32
  %46 = trunc i32 %45 to i8
  %47 = load i64, ptr %16, align 8
  %48 = getelementptr inbounds [64 x i8], ptr %15, i64 0, i64 %47
  store i8 %46, ptr %48, align 1
  br label %49

49:                                               ; preds = %40
  %50 = load i64, ptr %16, align 8
  %51 = add nsw i64 %50, 1
  store i64 %51, ptr %16, align 8
  br label %36, !llvm.loop !74

52:                                               ; preds = %36
  store i64 0, ptr %21, align 8
  br label %53

53:                                               ; preds = %61, %52
  %54 = load i64, ptr %21, align 8
  %55 = load i64, ptr %13, align 8
  %56 = icmp slt i64 %54, %55
  br i1 %56, label %57, label %64

57:                                               ; preds = %53
  %58 = load i64, ptr %21, align 8
  %59 = load i64, ptr %21, align 8
  %60 = getelementptr inbounds [64 x i64], ptr %17, i64 0, i64 %59
  store i64 %58, ptr %60, align 8
  br label %61

61:                                               ; preds = %57
  %62 = load i64, ptr %21, align 8
  %63 = add nsw i64 %62, 1
  store i64 %63, ptr %21, align 8
  br label %53, !llvm.loop !75

64:                                               ; preds = %53
  store i64 0, ptr %22, align 8
  store i32 1, ptr %23, align 4
  br label %65

65:                                               ; preds = %176, %64
  %66 = load i32, ptr %23, align 4
  %67 = icmp ne i32 %66, 0
  br i1 %67, label %68, label %177

68:                                               ; preds = %65
  store i32 0, ptr %23, align 4
  store i64 0, ptr %24, align 8
  br label %69

69:                                               ; preds = %114, %68
  %70 = load i64, ptr %24, align 8
  %71 = load i64, ptr %13, align 8
  %72 = icmp slt i64 %70, %71
  br i1 %72, label %73, label %117

73:                                               ; preds = %69
  %74 = load ptr, ptr %10, align 8
  %75 = load i64, ptr %24, align 8
  %76 = call i64 @getv(ptr noundef %74, i64 noundef %75)
  store i64 %76, ptr %25, align 8
  %77 = load ptr, ptr %12, align 8
  %78 = load i64, ptr %24, align 8
  %79 = call i64 @getv(ptr noundef %77, i64 noundef %78)
  store i64 %79, ptr %26, align 8
  %80 = load i64, ptr %25, align 8
  %81 = getelementptr inbounds [64 x i8], ptr %15, i64 0, i64 %80
  %82 = load i8, ptr %81, align 1
  %83 = icmp ne i8 %82, 0
  br i1 %83, label %84, label %85

84:                                               ; preds = %73
  store i64 -999999999, ptr %26, align 8
  br label %110

85:                                               ; preds = %73
  %86 = load ptr, ptr %11, align 8
  %87 = load i64, ptr %24, align 8
  %88 = call i64 @getv(ptr noundef %86, i64 noundef %87)
  store i64 %88, ptr %27, align 8
  store i64 0, ptr %28, align 8
  br label %89

89:                                               ; preds = %106, %85
  %90 = load i64, ptr %28, align 8
  %91 = load i64, ptr %9, align 8
  %92 = icmp slt i64 %90, %91
  br i1 %92, label %93, label %109

93:                                               ; preds = %89
  %94 = load i64, ptr %27, align 8
  %95 = load i64, ptr %28, align 8
  %96 = lshr i64 %94, %95
  %97 = and i64 %96, 1
  %98 = icmp ne i64 %97, 0
  br i1 %98, label %99, label %105

99:                                               ; preds = %93
  %100 = load i64, ptr %28, align 8
  %101 = getelementptr inbounds [64 x i8], ptr %15, i64 0, i64 %100
  %102 = load i8, ptr %101, align 1
  %103 = icmp ne i8 %102, 0
  br i1 %103, label %105, label %104

104:                                              ; preds = %99
  store i64 -999999999, ptr %26, align 8
  br label %109

105:                                              ; preds = %99, %93
  br label %106

106:                                              ; preds = %105
  %107 = load i64, ptr %28, align 8
  %108 = add nsw i64 %107, 1
  store i64 %108, ptr %28, align 8
  br label %89, !llvm.loop !76

109:                                              ; preds = %104, %89
  br label %110

110:                                              ; preds = %109, %84
  %111 = load i64, ptr %26, align 8
  %112 = load i64, ptr %24, align 8
  %113 = getelementptr inbounds [64 x i64], ptr %18, i64 0, i64 %112
  store i64 %111, ptr %113, align 8
  br label %114

114:                                              ; preds = %110
  %115 = load i64, ptr %24, align 8
  %116 = add nsw i64 %115, 1
  store i64 %116, ptr %24, align 8
  br label %69, !llvm.loop !77

117:                                              ; preds = %69
  %118 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %29, i32 0, i32 0
  %119 = getelementptr inbounds [64 x i64], ptr %17, i64 0, i64 0
  store ptr %119, ptr %118, align 8
  %120 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %29, i32 0, i32 1
  %121 = load i64, ptr %13, align 8
  store i64 %121, ptr %120, align 8
  %122 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %29, i32 0, i32 2
  store i64 8, ptr %122, align 8
  %123 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %29, i32 0, i32 3
  store i64 8, ptr %123, align 8
  %124 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %30, i32 0, i32 0
  %125 = getelementptr inbounds [64 x i64], ptr %18, i64 0, i64 0
  store ptr %125, ptr %124, align 8
  %126 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %30, i32 0, i32 1
  %127 = load i64, ptr %13, align 8
  store i64 %127, ptr %126, align 8
  %128 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %30, i32 0, i32 2
  store i64 8, ptr %128, align 8
  %129 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %30, i32 0, i32 3
  store i64 8, ptr %129, align 8
  %130 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %31, i32 0, i32 0
  %131 = getelementptr inbounds [64 x i64], ptr %19, i64 0, i64 0
  store ptr %131, ptr %130, align 8
  %132 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %31, i32 0, i32 1
  %133 = load i64, ptr %13, align 8
  store i64 %133, ptr %132, align 8
  %134 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %31, i32 0, i32 2
  store i64 8, ptr %134, align 8
  %135 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %31, i32 0, i32 3
  store i64 8, ptr %135, align 8
  %136 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %32, i32 0, i32 0
  %137 = getelementptr inbounds [64 x i64], ptr %20, i64 0, i64 0
  store ptr %137, ptr %136, align 8
  %138 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %32, i32 0, i32 1
  %139 = load i64, ptr %13, align 8
  store i64 %139, ptr %138, align 8
  %140 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %32, i32 0, i32 2
  store i64 8, ptr %140, align 8
  %141 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %32, i32 0, i32 3
  store i64 8, ptr %141, align 8
  %142 = load i64, ptr %13, align 8
  %143 = load i64, ptr %13, align 8
  call void @topk(ptr noundef %30, i64 noundef %142, i64 noundef %143, ptr noundef %29, ptr noundef %31, ptr noundef %32)
  store i64 0, ptr %33, align 8
  br label %144

144:                                              ; preds = %173, %117
  %145 = load i64, ptr %33, align 8
  %146 = load i64, ptr %13, align 8
  %147 = icmp slt i64 %145, %146
  br i1 %147, label %148, label %176

148:                                              ; preds = %144
  %149 = load i64, ptr %33, align 8
  %150 = getelementptr inbounds [64 x i64], ptr %19, i64 0, i64 %149
  %151 = load i64, ptr %150, align 8
  store i64 %151, ptr %34, align 8
  %152 = load i64, ptr %33, align 8
  %153 = getelementptr inbounds [64 x i64], ptr %20, i64 0, i64 %152
  %154 = load i64, ptr %153, align 8
  %155 = icmp sle i64 %154, -999999999
  br i1 %155, label %156, label %157

156:                                              ; preds = %148
  br label %176

157:                                              ; preds = %148
  %158 = load ptr, ptr %10, align 8
  %159 = load i64, ptr %34, align 8
  %160 = call i64 @getv(ptr noundef %158, i64 noundef %159)
  store i64 %160, ptr %35, align 8
  %161 = load i64, ptr %35, align 8
  %162 = getelementptr inbounds [64 x i8], ptr %15, i64 0, i64 %161
  %163 = load i8, ptr %162, align 1
  %164 = icmp ne i8 %163, 0
  br i1 %164, label %165, label %166

165:                                              ; preds = %157
  br label %173

166:                                              ; preds = %157
  %167 = load i64, ptr %35, align 8
  %168 = getelementptr inbounds [64 x i8], ptr %15, i64 0, i64 %167
  store i8 1, ptr %168, align 1
  %169 = load ptr, ptr %14, align 8
  %170 = load i64, ptr %22, align 8
  %171 = add nsw i64 %170, 1
  store i64 %171, ptr %22, align 8
  %172 = load i64, ptr %35, align 8
  call void @setv(ptr noundef %169, i64 noundef %170, i64 noundef %172)
  store i32 1, ptr %23, align 4
  br label %173

173:                                              ; preds = %166, %165
  %174 = load i64, ptr %33, align 8
  %175 = add nsw i64 %174, 1
  store i64 %175, ptr %33, align 8
  br label %144, !llvm.loop !78

176:                                              ; preds = %156, %144
  br label %65, !llvm.loop !79

177:                                              ; preds = %65
  %178 = load i64, ptr %22, align 8
  ret i64 %178
}

; Function Attrs: noinline nounwind optnone sspstrong uwtable
define internal i64 @getv(ptr noundef %0, i64 noundef %1) #0 {
  %3 = alloca ptr, align 8
  %4 = alloca i64, align 8
  store ptr %0, ptr %3, align 8
  store i64 %1, ptr %4, align 8
  %5 = load ptr, ptr %3, align 8
  %6 = load i64, ptr %4, align 8
  %7 = call i64 @mav_get(ptr noundef %5, i64 noundef %6)
  ret i64 %7
}

; Function Attrs: noinline nounwind optnone sspstrong uwtable
define internal i64 @mav_get(ptr noundef %0, i64 noundef %1) #0 {
  %3 = alloca ptr, align 8
  %4 = alloca i64, align 8
  %5 = alloca ptr, align 8
  %6 = alloca i64, align 8
  %7 = alloca i64, align 8
  store ptr %0, ptr %3, align 8
  store i64 %1, ptr %4, align 8
  %8 = load ptr, ptr %3, align 8
  %9 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %8, i32 0, i32 0
  %10 = load ptr, ptr %9, align 8
  %11 = load i64, ptr %4, align 8
  %12 = load ptr, ptr %3, align 8
  %13 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %12, i32 0, i32 2
  %14 = load i64, ptr %13, align 8
  %15 = mul nsw i64 %11, %14
  %16 = getelementptr inbounds i8, ptr %10, i64 %15
  store ptr %16, ptr %5, align 8
  store i64 0, ptr %6, align 8
  store i64 0, ptr %7, align 8
  br label %17

17:                                               ; preds = %34, %2
  %18 = load i64, ptr %7, align 8
  %19 = load ptr, ptr %3, align 8
  %20 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %19, i32 0, i32 3
  %21 = load i64, ptr %20, align 8
  %22 = icmp slt i64 %18, %21
  br i1 %22, label %23, label %37

23:                                               ; preds = %17
  %24 = load ptr, ptr %5, align 8
  %25 = load i64, ptr %7, align 8
  %26 = getelementptr inbounds i8, ptr %24, i64 %25
  %27 = load i8, ptr %26, align 1
  %28 = zext i8 %27 to i64
  %29 = load i64, ptr %7, align 8
  %30 = mul nsw i64 8, %29
  %31 = shl i64 %28, %30
  %32 = load i64, ptr %6, align 8
  %33 = or i64 %32, %31
  store i64 %33, ptr %6, align 8
  br label %34

34:                                               ; preds = %23
  %35 = load i64, ptr %7, align 8
  %36 = add nsw i64 %35, 1
  store i64 %36, ptr %7, align 8
  br label %17, !llvm.loop !80

37:                                               ; preds = %17
  %38 = load i64, ptr %6, align 8
  ret i64 %38
}

; Function Attrs: nounwind
declare double @exp(double noundef) #4

; Function Attrs: noinline nounwind optnone sspstrong uwtable
define internal void @setv(ptr noundef %0, i64 noundef %1, i64 noundef %2) #0 {
  %4 = alloca ptr, align 8
  %5 = alloca i64, align 8
  %6 = alloca i64, align 8
  %7 = alloca ptr, align 8
  %8 = alloca i64, align 8
  store ptr %0, ptr %4, align 8
  store i64 %1, ptr %5, align 8
  store i64 %2, ptr %6, align 8
  %9 = load ptr, ptr %4, align 8
  %10 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %9, i32 0, i32 0
  %11 = load ptr, ptr %10, align 8
  %12 = load i64, ptr %5, align 8
  %13 = load ptr, ptr %4, align 8
  %14 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %13, i32 0, i32 2
  %15 = load i64, ptr %14, align 8
  %16 = mul nsw i64 %12, %15
  %17 = getelementptr inbounds i8, ptr %11, i64 %16
  store ptr %17, ptr %7, align 8
  store i64 0, ptr %8, align 8
  br label %18

18:                                               ; preds = %34, %3
  %19 = load i64, ptr %8, align 8
  %20 = load ptr, ptr %4, align 8
  %21 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %20, i32 0, i32 3
  %22 = load i64, ptr %21, align 8
  %23 = icmp slt i64 %19, %22
  br i1 %23, label %24, label %37

24:                                               ; preds = %18
  %25 = load i64, ptr %6, align 8
  %26 = load i64, ptr %8, align 8
  %27 = mul nsw i64 8, %26
  %28 = ashr i64 %25, %27
  %29 = and i64 %28, 255
  %30 = trunc i64 %29 to i8
  %31 = load ptr, ptr %7, align 8
  %32 = load i64, ptr %8, align 8
  %33 = getelementptr inbounds i8, ptr %31, i64 %32
  store i8 %30, ptr %33, align 1
  br label %34

34:                                               ; preds = %24
  %35 = load i64, ptr %8, align 8
  %36 = add nsw i64 %35, 1
  store i64 %36, ptr %8, align 8
  br label %18, !llvm.loop !81

37:                                               ; preds = %18
  ret void
}

; Function Attrs: noinline nounwind optnone sspstrong uwtable
define internal i64 @qdiv(i64 noundef %0, i64 noundef %1) #0 {
  %3 = alloca i64, align 8
  %4 = alloca i64, align 8
  store i64 %0, ptr %3, align 8
  store i64 %1, ptr %4, align 8
  %5 = load i64, ptr %4, align 8
  %6 = icmp ne i64 %5, 0
  br i1 %6, label %7, label %12

7:                                                ; preds = %2
  %8 = load i64, ptr %3, align 8
  %9 = mul nsw i64 %8, 65536
  %10 = load i64, ptr %4, align 8
  %11 = sdiv i64 %9, %10
  br label %13

12:                                               ; preds = %2
  br label %13

13:                                               ; preds = %12, %7
  %14 = phi i64 [ %11, %7 ], [ 0, %12 ]
  ret i64 %14
}

; Function Attrs: noinline nounwind optnone sspstrong uwtable
define internal i64 @qsqrt(i64 noundef %0) #0 {
  %2 = alloca i64, align 8
  %3 = alloca i64, align 8
  %4 = alloca i64, align 8
  store i64 %0, ptr %3, align 8
  %5 = load i64, ptr %3, align 8
  %6 = icmp sle i64 %5, 0
  br i1 %6, label %7, label %8

7:                                                ; preds = %1
  store i64 0, ptr %2, align 8
  br label %22

8:                                                ; preds = %1
  store i64 0, ptr %4, align 8
  br label %9

9:                                                ; preds = %17, %8
  %10 = load i64, ptr %4, align 8
  %11 = add nsw i64 %10, 1
  %12 = load i64, ptr %4, align 8
  %13 = add nsw i64 %12, 1
  %14 = mul nsw i64 %11, %13
  %15 = load i64, ptr %3, align 8
  %16 = icmp sle i64 %14, %15
  br i1 %16, label %17, label %20

17:                                               ; preds = %9
  %18 = load i64, ptr %4, align 8
  %19 = add nsw i64 %18, 1
  store i64 %19, ptr %4, align 8
  br label %9, !llvm.loop !82

20:                                               ; preds = %9
  %21 = load i64, ptr %4, align 8
  store i64 %21, ptr %2, align 8
  br label %22

22:                                               ; preds = %20, %7
  %23 = load i64, ptr %2, align 8
  ret i64 %23
}

; Function Attrs: noinline nounwind optnone sspstrong uwtable
define internal i64 @adot(ptr noundef %0, ptr noundef %1, i64 noundef %2) #0 {
  %4 = alloca ptr, align 8
  %5 = alloca ptr, align 8
  %6 = alloca i64, align 8
  %7 = alloca i64, align 8
  %8 = alloca i64, align 8
  store ptr %0, ptr %4, align 8
  store ptr %1, ptr %5, align 8
  store i64 %2, ptr %6, align 8
  store i64 0, ptr %7, align 8
  store i64 0, ptr %8, align 8
  br label %9

9:                                                ; preds = %25, %3
  %10 = load i64, ptr %8, align 8
  %11 = load i64, ptr %6, align 8
  %12 = icmp slt i64 %10, %11
  br i1 %12, label %13, label %28

13:                                               ; preds = %9
  %14 = load ptr, ptr %4, align 8
  %15 = load i64, ptr %8, align 8
  %16 = getelementptr inbounds i64, ptr %14, i64 %15
  %17 = load i64, ptr %16, align 8
  %18 = load ptr, ptr %5, align 8
  %19 = load i64, ptr %8, align 8
  %20 = getelementptr inbounds i64, ptr %18, i64 %19
  %21 = load i64, ptr %20, align 8
  %22 = call i64 @qmul(i64 noundef %17, i64 noundef %21)
  %23 = load i64, ptr %7, align 8
  %24 = add nsw i64 %23, %22
  store i64 %24, ptr %7, align 8
  br label %25

25:                                               ; preds = %13
  %26 = load i64, ptr %8, align 8
  %27 = add nsw i64 %26, 1
  store i64 %27, ptr %8, align 8
  br label %9, !llvm.loop !83

28:                                               ; preds = %9
  %29 = load i64, ptr %7, align 8
  ret i64 %29
}

; Function Attrs: nounwind
declare double @log(double noundef) #4

; Function Attrs: nocallback nocreateundeforpoison nofree nosync nounwind speculatable willreturn memory(none)
declare double @llvm.fmuladd.f64(double, double, double) #5

; Function Attrs: nounwind
declare double @pow(double noundef, double noundef) #4

; Function Attrs: nounwind
declare double @sqrt(double noundef) #4

attributes #0 = { noinline nounwind optnone sspstrong uwtable "frame-pointer"="all" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #1 = { nocallback nofree nosync nounwind willreturn memory(argmem: write) }
attributes #2 = { nocallback nofree nosync nounwind willreturn memory(argmem: readwrite) }
attributes #3 = { "frame-pointer"="all" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #4 = { nounwind "frame-pointer"="all" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #5 = { nocallback nocreateundeforpoison nofree nosync nounwind speculatable willreturn memory(none) }
attributes #6 = { nounwind }

!llvm.module.flags = !{!0, !1, !2, !3}
!llvm.ident = !{!4}

!0 = !{i32 8, !"PIC Level", i32 2}
!1 = !{i32 7, !"PIE Level", i32 2}
!2 = !{i32 7, !"uwtable", i32 2}
!3 = !{i32 7, !"frame-pointer", i32 2}
!4 = !{!"clang version 23.1.4"}
!5 = distinct !{!5, !6}
!6 = !{!"llvm.loop.mustprogress"}
!7 = distinct !{!7, !6}
!8 = distinct !{!8, !6}
!9 = distinct !{!9, !6}
!10 = distinct !{!10, !6}
!11 = distinct !{!11, !6}
!12 = distinct !{!12, !6}
!13 = distinct !{!13, !6}
!14 = distinct !{!14, !6}
!15 = distinct !{!15, !6}
!16 = distinct !{!16, !6}
!17 = distinct !{!17, !6}
!18 = distinct !{!18, !6}
!19 = distinct !{!19, !6}
!20 = distinct !{!20, !6}
!21 = distinct !{!21, !6}
!22 = distinct !{!22, !6}
!23 = distinct !{!23, !6}
!24 = distinct !{!24, !6}
!25 = distinct !{!25, !6}
!26 = distinct !{!26, !6}
!27 = distinct !{!27, !6}
!28 = distinct !{!28, !6}
!29 = distinct !{!29, !6}
!30 = distinct !{!30, !6}
!31 = distinct !{!31, !6}
!32 = distinct !{!32, !6}
!33 = distinct !{!33, !6}
!34 = distinct !{!34, !6}
!35 = distinct !{!35, !6}
!36 = distinct !{!36, !6}
!37 = distinct !{!37, !6}
!38 = distinct !{!38, !6}
!39 = distinct !{!39, !6}
!40 = distinct !{!40, !6}
!41 = distinct !{!41, !6}
!42 = distinct !{!42, !6}
!43 = distinct !{!43, !6}
!44 = distinct !{!44, !6}
!45 = distinct !{!45, !6}
!46 = distinct !{!46, !6}
!47 = distinct !{!47, !6}
!48 = distinct !{!48, !6}
!49 = distinct !{!49, !6}
!50 = distinct !{!50, !6}
!51 = distinct !{!51, !6}
!52 = distinct !{!52, !6}
!53 = distinct !{!53, !6}
!54 = distinct !{!54, !6}
!55 = distinct !{!55, !6}
!56 = distinct !{!56, !6}
!57 = distinct !{!57, !6}
!58 = distinct !{!58, !6}
!59 = distinct !{!59, !6}
!60 = distinct !{!60, !6}
!61 = distinct !{!61, !6}
!62 = distinct !{!62, !6}
!63 = distinct !{!63, !6}
!64 = distinct !{!64, !6}
!65 = distinct !{!65, !6}
!66 = distinct !{!66, !6}
!67 = distinct !{!67, !6}
!68 = distinct !{!68, !6}
!69 = distinct !{!69, !6}
!70 = distinct !{!70, !6}
!71 = distinct !{!71, !6}
!72 = distinct !{!72, !6}
!73 = distinct !{!73, !6}
!74 = distinct !{!74, !6}
!75 = distinct !{!75, !6}
!76 = distinct !{!76, !6}
!77 = distinct !{!77, !6}
!78 = distinct !{!78, !6}
!79 = distinct !{!79, !6}
!80 = distinct !{!80, !6}
!81 = distinct !{!81, !6}
!82 = distinct !{!82, !6}
!83 = distinct !{!83, !6}
