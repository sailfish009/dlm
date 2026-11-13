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
@.str.22 = private unnamed_addr constant [21 x i8] c"KERNEL-SUITE-PHASE8\0A\00", align 1

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
  store i32 0, ptr %1, align 4
  call void @llvm.memset.p0.i64(ptr align 16 %2, i8 0, i64 48, i1 false)
  %148 = getelementptr inbounds [6 x i64], ptr %2, i32 0, i32 0
  store i64 65536, ptr %148, align 16
  %149 = getelementptr inbounds [6 x i64], ptr %2, i32 0, i32 4
  store i64 65536, ptr %149, align 16
  call void @llvm.memcpy.p0.p0.i64(ptr align 16 %3, ptr align 16 @__const.main.x, i64 24, i1 false)
  call void @llvm.memcpy.p0.p0.i64(ptr align 16 %4, ptr align 16 @__const.main.b, i64 16, i1 false)
  %150 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %5, i32 0, i32 0
  %151 = getelementptr inbounds [6 x i64], ptr %2, i64 0, i64 0
  store ptr %151, ptr %150, align 8
  %152 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %5, i32 0, i32 1
  store i64 6, ptr %152, align 8
  %153 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %5, i32 0, i32 2
  store i64 8, ptr %153, align 8
  %154 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %5, i32 0, i32 3
  store i64 8, ptr %154, align 8
  %155 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %6, i32 0, i32 0
  %156 = getelementptr inbounds [3 x i64], ptr %3, i64 0, i64 0
  store ptr %156, ptr %155, align 8
  %157 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %6, i32 0, i32 1
  store i64 3, ptr %157, align 8
  %158 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %6, i32 0, i32 2
  store i64 8, ptr %158, align 8
  %159 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %6, i32 0, i32 3
  store i64 8, ptr %159, align 8
  %160 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %7, i32 0, i32 0
  %161 = getelementptr inbounds [2 x i64], ptr %4, i64 0, i64 0
  store ptr %161, ptr %160, align 8
  %162 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %7, i32 0, i32 1
  store i64 2, ptr %162, align 8
  %163 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %7, i32 0, i32 2
  store i64 8, ptr %163, align 8
  %164 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %7, i32 0, i32 3
  store i64 8, ptr %164, align 8
  %165 = getelementptr inbounds [2 x i64], ptr %8, i64 0, i64 0
  call void @matvec(ptr noundef %5, i64 noundef 2, i64 noundef 3, ptr noundef %6, ptr noundef %7, ptr noundef %165)
  %166 = call i64 @qmul(i64 noundef 65536, i64 noundef 65536)
  %167 = add nsw i64 100, %166
  store i64 %167, ptr %9, align 8
  %168 = call i64 @qmul(i64 noundef 65536, i64 noundef 131072)
  %169 = add nsw i64 200, %168
  store i64 %169, ptr %10, align 8
  %170 = getelementptr inbounds [2 x i64], ptr %8, i64 0, i64 0
  %171 = load i64, ptr %170, align 16
  %172 = load i64, ptr %9, align 8
  %173 = icmp eq i64 %171, %172
  br i1 %173, label %174, label %179

174:                                              ; preds = %0
  %175 = getelementptr inbounds [2 x i64], ptr %8, i64 0, i64 1
  %176 = load i64, ptr %175, align 8
  %177 = load i64, ptr %10, align 8
  %178 = icmp eq i64 %176, %177
  br label %179

179:                                              ; preds = %174, %0
  %180 = phi i1 [ false, %0 ], [ %178, %174 ]
  %181 = zext i1 %180 to i64
  %182 = select i1 %180, ptr @.str.1, ptr @.str.2
  %183 = getelementptr inbounds [2 x i64], ptr %8, i64 0, i64 0
  %184 = load i64, ptr %183, align 16
  %185 = getelementptr inbounds [2 x i64], ptr %8, i64 0, i64 1
  %186 = load i64, ptr %185, align 8
  %187 = call i32 (ptr, ...) @printf(ptr noundef @.str, ptr noundef %182, i64 noundef %184, i64 noundef %186)
  call void @llvm.memset.p0.i64(ptr align 16 %11, i8 0, i64 48, i1 false)
  %188 = getelementptr inbounds [6 x i64], ptr %11, i32 0, i32 0
  store i64 65536, ptr %188, align 16
  %189 = getelementptr inbounds [6 x i64], ptr %11, i32 0, i32 1
  store i64 131072, ptr %189, align 8
  %190 = getelementptr inbounds [6 x i64], ptr %11, i32 0, i32 2
  store i64 196608, ptr %190, align 16
  %191 = getelementptr inbounds [6 x i64], ptr %11, i32 0, i32 3
  store i64 131072, ptr %191, align 8
  %192 = getelementptr inbounds [6 x i64], ptr %11, i32 0, i32 4
  store i64 196608, ptr %192, align 16
  %193 = getelementptr inbounds [6 x i64], ptr %11, i32 0, i32 5
  store i64 262144, ptr %193, align 8
  %194 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %12, i32 0, i32 0
  %195 = getelementptr inbounds [6 x i64], ptr %11, i64 0, i64 0
  store ptr %195, ptr %194, align 8
  %196 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %12, i32 0, i32 1
  store i64 6, ptr %196, align 8
  %197 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %12, i32 0, i32 2
  store i64 8, ptr %197, align 8
  %198 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %12, i32 0, i32 3
  store i64 8, ptr %198, align 8
  %199 = getelementptr inbounds [4 x i64], ptr %13, i64 0, i64 0
  call void @batched(ptr noundef %5, i64 noundef 2, i64 noundef 3, ptr noundef %12, ptr noundef %7, i64 noundef 2, ptr noundef %199)
  %200 = getelementptr inbounds [4 x i64], ptr %13, i64 0, i64 0
  %201 = load i64, ptr %200, align 16
  %202 = load i64, ptr %9, align 8
  %203 = icmp eq i64 %201, %202
  br i1 %203, label %204, label %209

204:                                              ; preds = %179
  %205 = getelementptr inbounds [4 x i64], ptr %13, i64 0, i64 1
  %206 = load i64, ptr %205, align 8
  %207 = load i64, ptr %10, align 8
  %208 = icmp eq i64 %206, %207
  br label %209

209:                                              ; preds = %204, %179
  %210 = phi i1 [ false, %179 ], [ %208, %204 ]
  %211 = zext i1 %210 to i64
  %212 = select i1 %210, ptr @.str.1, ptr @.str.2
  %213 = call i32 (ptr, ...) @printf(ptr noundef @.str.3, ptr noundef %212)
  call void @llvm.memcpy.p0.p0.i64(ptr align 16 %14, ptr align 16 @__const.main.sx, i64 24, i1 false)
  %214 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %16, i32 0, i32 0
  %215 = getelementptr inbounds [3 x i64], ptr %14, i64 0, i64 0
  store ptr %215, ptr %214, align 8
  %216 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %16, i32 0, i32 1
  store i64 3, ptr %216, align 8
  %217 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %16, i32 0, i32 2
  store i64 8, ptr %217, align 8
  %218 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %16, i32 0, i32 3
  store i64 8, ptr %218, align 8
  %219 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %17, i32 0, i32 0
  %220 = getelementptr inbounds [3 x i64], ptr %15, i64 0, i64 0
  store ptr %220, ptr %219, align 8
  %221 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %17, i32 0, i32 1
  store i64 3, ptr %221, align 8
  %222 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %17, i32 0, i32 2
  store i64 8, ptr %222, align 8
  %223 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %17, i32 0, i32 3
  store i64 8, ptr %223, align 8
  call void @softmax(ptr noundef %16, i64 noundef 3, ptr noundef %17)
  store i64 0, ptr %18, align 8
  store i32 0, ptr %19, align 4
  br label %224

224:                                              ; preds = %234, %209
  %225 = load i32, ptr %19, align 4
  %226 = icmp slt i32 %225, 3
  br i1 %226, label %227, label %237

227:                                              ; preds = %224
  %228 = load i32, ptr %19, align 4
  %229 = sext i32 %228 to i64
  %230 = getelementptr inbounds [3 x i64], ptr %15, i64 0, i64 %229
  %231 = load i64, ptr %230, align 8
  %232 = load i64, ptr %18, align 8
  %233 = add nsw i64 %232, %231
  store i64 %233, ptr %18, align 8
  br label %234

234:                                              ; preds = %227
  %235 = load i32, ptr %19, align 4
  %236 = add nsw i32 %235, 1
  store i32 %236, ptr %19, align 4
  br label %224, !llvm.loop !5

237:                                              ; preds = %224
  %238 = load i64, ptr %18, align 8
  %239 = icmp sge i64 %238, 65534
  br i1 %239, label %240, label %243

240:                                              ; preds = %237
  %241 = load i64, ptr %18, align 8
  %242 = icmp sle i64 %241, 65538
  br label %243

243:                                              ; preds = %240, %237
  %244 = phi i1 [ false, %237 ], [ %242, %240 ]
  %245 = zext i1 %244 to i64
  %246 = select i1 %244, ptr @.str.1, ptr @.str.2
  %247 = load i64, ptr %18, align 8
  %248 = call i32 (ptr, ...) @printf(ptr noundef @.str.4, ptr noundef %246, i64 noundef %247)
  call void @llvm.memcpy.p0.p0.i64(ptr align 16 %20, ptr align 16 @__const.main.lx, i64 24, i1 false)
  call void @llvm.memcpy.p0.p0.i64(ptr align 16 %21, ptr align 16 @__const.main.g, i64 24, i1 false)
  call void @llvm.memset.p0.i64(ptr align 16 %22, i8 0, i64 24, i1 false)
  %249 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %24, i32 0, i32 0
  %250 = getelementptr inbounds [3 x i64], ptr %20, i64 0, i64 0
  store ptr %250, ptr %249, align 8
  %251 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %24, i32 0, i32 1
  store i64 3, ptr %251, align 8
  %252 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %24, i32 0, i32 2
  store i64 8, ptr %252, align 8
  %253 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %24, i32 0, i32 3
  store i64 8, ptr %253, align 8
  %254 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %25, i32 0, i32 0
  %255 = getelementptr inbounds [3 x i64], ptr %21, i64 0, i64 0
  store ptr %255, ptr %254, align 8
  %256 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %25, i32 0, i32 1
  store i64 3, ptr %256, align 8
  %257 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %25, i32 0, i32 2
  store i64 8, ptr %257, align 8
  %258 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %25, i32 0, i32 3
  store i64 8, ptr %258, align 8
  %259 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %26, i32 0, i32 0
  %260 = getelementptr inbounds [3 x i64], ptr %22, i64 0, i64 0
  store ptr %260, ptr %259, align 8
  %261 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %26, i32 0, i32 1
  store i64 3, ptr %261, align 8
  %262 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %26, i32 0, i32 2
  store i64 8, ptr %262, align 8
  %263 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %26, i32 0, i32 3
  store i64 8, ptr %263, align 8
  %264 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %27, i32 0, i32 0
  %265 = getelementptr inbounds [3 x i64], ptr %23, i64 0, i64 0
  store ptr %265, ptr %264, align 8
  %266 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %27, i32 0, i32 1
  store i64 3, ptr %266, align 8
  %267 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %27, i32 0, i32 2
  store i64 8, ptr %267, align 8
  %268 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %27, i32 0, i32 3
  store i64 8, ptr %268, align 8
  call void @layernorm(ptr noundef %24, i64 noundef 3, ptr noundef %25, ptr noundef %26, ptr noundef %27)
  store i64 0, ptr %28, align 8
  store i32 0, ptr %29, align 4
  br label %269

269:                                              ; preds = %279, %243
  %270 = load i32, ptr %29, align 4
  %271 = icmp slt i32 %270, 3
  br i1 %271, label %272, label %282

272:                                              ; preds = %269
  %273 = load i32, ptr %29, align 4
  %274 = sext i32 %273 to i64
  %275 = getelementptr inbounds [3 x i64], ptr %23, i64 0, i64 %274
  %276 = load i64, ptr %275, align 8
  %277 = load i64, ptr %28, align 8
  %278 = add nsw i64 %277, %276
  store i64 %278, ptr %28, align 8
  br label %279

279:                                              ; preds = %272
  %280 = load i32, ptr %29, align 4
  %281 = add nsw i32 %280, 1
  store i32 %281, ptr %29, align 4
  br label %269, !llvm.loop !7

282:                                              ; preds = %269
  %283 = load i64, ptr %28, align 8
  %284 = icmp slt i64 %283, 10
  br i1 %284, label %285, label %288

285:                                              ; preds = %282
  %286 = load i64, ptr %28, align 8
  %287 = icmp sgt i64 %286, -10
  br label %288

288:                                              ; preds = %285, %282
  %289 = phi i1 [ false, %282 ], [ %287, %285 ]
  %290 = zext i1 %289 to i64
  %291 = select i1 %289, ptr @.str.1, ptr @.str.2
  %292 = load i64, ptr %28, align 8
  %293 = call i32 (ptr, ...) @printf(ptr noundef @.str.5, ptr noundef %291, i64 noundef %292)
  store i32 0, ptr %39, align 4
  br label %294

294:                                              ; preds = %307, %288
  %295 = load i32, ptr %39, align 4
  %296 = icmp slt i32 %295, 12
  br i1 %296, label %297, label %310

297:                                              ; preds = %294
  %298 = load i32, ptr %39, align 4
  %299 = mul nsw i32 %298, 37
  %300 = srem i32 %299, 100
  %301 = sub nsw i32 %300, 50
  %302 = mul nsw i32 %301, 256
  %303 = sext i32 %302 to i64
  %304 = load i32, ptr %39, align 4
  %305 = sext i32 %304 to i64
  %306 = getelementptr inbounds [12 x i64], ptr %30, i64 0, i64 %305
  store i64 %303, ptr %306, align 8
  br label %307

307:                                              ; preds = %297
  %308 = load i32, ptr %39, align 4
  %309 = add nsw i32 %308, 1
  store i32 %309, ptr %39, align 4
  br label %294, !llvm.loop !8

310:                                              ; preds = %294
  store i32 0, ptr %40, align 4
  br label %311

311:                                              ; preds = %324, %310
  %312 = load i32, ptr %40, align 4
  %313 = icmp slt i32 %312, 48
  br i1 %313, label %314, label %327

314:                                              ; preds = %311
  %315 = load i32, ptr %40, align 4
  %316 = mul nsw i32 %315, 13
  %317 = srem i32 %316, 200
  %318 = sub nsw i32 %317, 100
  %319 = mul nsw i32 %318, 128
  %320 = sext i32 %319 to i64
  %321 = load i32, ptr %40, align 4
  %322 = sext i32 %321 to i64
  %323 = getelementptr inbounds [48 x i64], ptr %31, i64 0, i64 %322
  store i64 %320, ptr %323, align 8
  br label %324

324:                                              ; preds = %314
  %325 = load i32, ptr %40, align 4
  %326 = add nsw i32 %325, 1
  store i32 %326, ptr %40, align 4
  br label %311, !llvm.loop !9

327:                                              ; preds = %311
  store i32 0, ptr %41, align 4
  br label %328

328:                                              ; preds = %341, %327
  %329 = load i32, ptr %41, align 4
  %330 = icmp slt i32 %329, 12
  br i1 %330, label %331, label %344

331:                                              ; preds = %328
  %332 = load i32, ptr %41, align 4
  %333 = mul nsw i32 %332, 7
  %334 = srem i32 %333, 50
  %335 = sub nsw i32 %334, 25
  %336 = mul nsw i32 %335, 64
  %337 = sext i32 %336 to i64
  %338 = load i32, ptr %41, align 4
  %339 = sext i32 %338 to i64
  %340 = getelementptr inbounds [12 x i64], ptr %32, i64 0, i64 %339
  store i64 %337, ptr %340, align 8
  br label %341

341:                                              ; preds = %331
  %342 = load i32, ptr %41, align 4
  %343 = add nsw i32 %342, 1
  store i32 %343, ptr %41, align 4
  br label %328, !llvm.loop !10

344:                                              ; preds = %328
  store i32 0, ptr %42, align 4
  br label %345

345:                                              ; preds = %358, %344
  %346 = load i32, ptr %42, align 4
  %347 = icmp slt i32 %346, 16
  br i1 %347, label %348, label %361

348:                                              ; preds = %345
  %349 = load i32, ptr %42, align 4
  %350 = mul nsw i32 %349, 11
  %351 = srem i32 %350, 200
  %352 = sub nsw i32 %351, 100
  %353 = mul nsw i32 %352, 128
  %354 = sext i32 %353 to i64
  %355 = load i32, ptr %42, align 4
  %356 = sext i32 %355 to i64
  %357 = getelementptr inbounds [16 x i64], ptr %33, i64 0, i64 %356
  store i64 %354, ptr %357, align 8
  br label %358

358:                                              ; preds = %348
  %359 = load i32, ptr %42, align 4
  %360 = add nsw i32 %359, 1
  store i32 %360, ptr %42, align 4
  br label %345, !llvm.loop !11

361:                                              ; preds = %345
  store i32 0, ptr %43, align 4
  br label %362

362:                                              ; preds = %378, %361
  %363 = load i32, ptr %43, align 4
  %364 = icmp slt i32 %363, 4
  br i1 %364, label %365, label %381

365:                                              ; preds = %362
  %366 = load i32, ptr %43, align 4
  %367 = mul nsw i32 %366, 10
  %368 = sext i32 %367 to i64
  %369 = load i32, ptr %43, align 4
  %370 = sext i32 %369 to i64
  %371 = getelementptr inbounds [4 x i64], ptr %34, i64 0, i64 %370
  store i64 %368, ptr %371, align 8
  %372 = load i32, ptr %43, align 4
  %373 = sext i32 %372 to i64
  %374 = getelementptr inbounds [4 x i64], ptr %35, i64 0, i64 %373
  store i64 65536, ptr %374, align 8
  %375 = load i32, ptr %43, align 4
  %376 = sext i32 %375 to i64
  %377 = getelementptr inbounds [4 x i64], ptr %36, i64 0, i64 %376
  store i64 0, ptr %377, align 8
  br label %378

378:                                              ; preds = %365
  %379 = load i32, ptr %43, align 4
  %380 = add nsw i32 %379, 1
  store i32 %380, ptr %43, align 4
  br label %362, !llvm.loop !12

381:                                              ; preds = %362
  %382 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %44, i32 0, i32 0
  %383 = getelementptr inbounds [12 x i64], ptr %30, i64 0, i64 0
  store ptr %383, ptr %382, align 8
  %384 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %44, i32 0, i32 1
  store i64 12, ptr %384, align 8
  %385 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %44, i32 0, i32 2
  store i64 8, ptr %385, align 8
  %386 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %44, i32 0, i32 3
  store i64 8, ptr %386, align 8
  %387 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %45, i32 0, i32 0
  %388 = getelementptr inbounds [48 x i64], ptr %31, i64 0, i64 0
  store ptr %388, ptr %387, align 8
  %389 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %45, i32 0, i32 1
  store i64 48, ptr %389, align 8
  %390 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %45, i32 0, i32 2
  store i64 8, ptr %390, align 8
  %391 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %45, i32 0, i32 3
  store i64 8, ptr %391, align 8
  %392 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %46, i32 0, i32 0
  %393 = getelementptr inbounds [12 x i64], ptr %32, i64 0, i64 0
  store ptr %393, ptr %392, align 8
  %394 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %46, i32 0, i32 1
  store i64 12, ptr %394, align 8
  %395 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %46, i32 0, i32 2
  store i64 8, ptr %395, align 8
  %396 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %46, i32 0, i32 3
  store i64 8, ptr %396, align 8
  %397 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %47, i32 0, i32 0
  %398 = getelementptr inbounds [16 x i64], ptr %33, i64 0, i64 0
  store ptr %398, ptr %397, align 8
  %399 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %47, i32 0, i32 1
  store i64 16, ptr %399, align 8
  %400 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %47, i32 0, i32 2
  store i64 8, ptr %400, align 8
  %401 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %47, i32 0, i32 3
  store i64 8, ptr %401, align 8
  %402 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %48, i32 0, i32 0
  %403 = getelementptr inbounds [4 x i64], ptr %34, i64 0, i64 0
  store ptr %403, ptr %402, align 8
  %404 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %48, i32 0, i32 1
  store i64 4, ptr %404, align 8
  %405 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %48, i32 0, i32 2
  store i64 8, ptr %405, align 8
  %406 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %48, i32 0, i32 3
  store i64 8, ptr %406, align 8
  %407 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %49, i32 0, i32 0
  %408 = getelementptr inbounds [4 x i64], ptr %35, i64 0, i64 0
  store ptr %408, ptr %407, align 8
  %409 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %49, i32 0, i32 1
  store i64 4, ptr %409, align 8
  %410 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %49, i32 0, i32 2
  store i64 8, ptr %410, align 8
  %411 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %49, i32 0, i32 3
  store i64 8, ptr %411, align 8
  %412 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %50, i32 0, i32 0
  %413 = getelementptr inbounds [4 x i64], ptr %36, i64 0, i64 0
  store ptr %413, ptr %412, align 8
  %414 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %50, i32 0, i32 1
  store i64 4, ptr %414, align 8
  %415 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %50, i32 0, i32 2
  store i64 8, ptr %415, align 8
  %416 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %50, i32 0, i32 3
  store i64 8, ptr %416, align 8
  %417 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %51, i32 0, i32 0
  %418 = getelementptr inbounds [12 x i64], ptr %37, i64 0, i64 0
  store ptr %418, ptr %417, align 8
  %419 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %51, i32 0, i32 1
  store i64 12, ptr %419, align 8
  %420 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %51, i32 0, i32 2
  store i64 8, ptr %420, align 8
  %421 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %51, i32 0, i32 3
  store i64 8, ptr %421, align 8
  call void @fused_attention(ptr noundef %44, ptr noundef %45, ptr noundef %46, ptr noundef %47, ptr noundef %48, ptr noundef %49, ptr noundef %50, ptr noundef %51)
  %422 = getelementptr inbounds [12 x i64], ptr %30, i64 0, i64 0
  %423 = getelementptr inbounds [48 x i64], ptr %31, i64 0, i64 0
  %424 = getelementptr inbounds [12 x i64], ptr %32, i64 0, i64 0
  %425 = getelementptr inbounds [16 x i64], ptr %33, i64 0, i64 0
  %426 = getelementptr inbounds [4 x i64], ptr %34, i64 0, i64 0
  %427 = getelementptr inbounds [4 x i64], ptr %35, i64 0, i64 0
  %428 = getelementptr inbounds [4 x i64], ptr %36, i64 0, i64 0
  %429 = getelementptr inbounds [12 x i64], ptr %38, i64 0, i64 0
  call void @fused_attention_ref(ptr noundef %422, ptr noundef %423, ptr noundef %424, ptr noundef %425, ptr noundef %426, ptr noundef %427, ptr noundef %428, ptr noundef %429)
  store i32 1, ptr %52, align 4
  store i32 0, ptr %53, align 4
  br label %430

430:                                              ; preds = %455, %381
  %431 = load i32, ptr %53, align 4
  %432 = icmp slt i32 %431, 12
  br i1 %432, label %433, label %458

433:                                              ; preds = %430
  %434 = load i32, ptr %53, align 4
  %435 = sext i32 %434 to i64
  %436 = getelementptr inbounds [12 x i64], ptr %37, i64 0, i64 %435
  %437 = load i64, ptr %436, align 8
  %438 = load i32, ptr %53, align 4
  %439 = sext i32 %438 to i64
  %440 = getelementptr inbounds [12 x i64], ptr %38, i64 0, i64 %439
  %441 = load i64, ptr %440, align 8
  %442 = icmp ne i64 %437, %441
  br i1 %442, label %443, label %454

443:                                              ; preds = %433
  %444 = load i32, ptr %53, align 4
  %445 = load i32, ptr %53, align 4
  %446 = sext i32 %445 to i64
  %447 = getelementptr inbounds [12 x i64], ptr %37, i64 0, i64 %446
  %448 = load i64, ptr %447, align 8
  %449 = load i32, ptr %53, align 4
  %450 = sext i32 %449 to i64
  %451 = getelementptr inbounds [12 x i64], ptr %38, i64 0, i64 %450
  %452 = load i64, ptr %451, align 8
  %453 = call i32 (ptr, ...) @printf(ptr noundef @.str.6, i32 noundef %444, i64 noundef %448, i64 noundef %452)
  store i32 0, ptr %52, align 4
  br label %454

454:                                              ; preds = %443, %433
  br label %455

455:                                              ; preds = %454
  %456 = load i32, ptr %53, align 4
  %457 = add nsw i32 %456, 1
  store i32 %457, ptr %53, align 4
  br label %430, !llvm.loop !13

458:                                              ; preds = %430
  %459 = load i32, ptr %52, align 4
  %460 = icmp ne i32 %459, 0
  %461 = zext i1 %460 to i64
  %462 = select i1 %460, ptr @.str.1, ptr @.str.2
  %463 = call i32 (ptr, ...) @printf(ptr noundef @.str.7, ptr noundef %462)
  call void @llvm.memset.p0.i64(ptr align 16 %54, i8 0, i64 40, i1 false)
  %464 = getelementptr inbounds [5 x i64], ptr %54, i32 0, i32 0
  store i64 5, ptr %464, align 16
  %465 = getelementptr inbounds [5 x i64], ptr %54, i32 0, i32 1
  store i64 1, ptr %465, align 8
  %466 = getelementptr inbounds [5 x i64], ptr %54, i32 0, i32 2
  store i64 9, ptr %466, align 16
  %467 = getelementptr inbounds [5 x i64], ptr %54, i32 0, i32 3
  store i64 3, ptr %467, align 8
  %468 = getelementptr inbounds [5 x i64], ptr %54, i32 0, i32 4
  store i64 7, ptr %468, align 16
  call void @llvm.memset.p0.i64(ptr align 16 %55, i8 0, i64 40, i1 false)
  %469 = getelementptr inbounds [5 x i64], ptr %55, i32 0, i32 0
  store i64 10, ptr %469, align 16
  %470 = getelementptr inbounds [5 x i64], ptr %55, i32 0, i32 1
  store i64 11, ptr %470, align 8
  %471 = getelementptr inbounds [5 x i64], ptr %55, i32 0, i32 2
  store i64 12, ptr %471, align 16
  %472 = getelementptr inbounds [5 x i64], ptr %55, i32 0, i32 3
  store i64 13, ptr %472, align 8
  %473 = getelementptr inbounds [5 x i64], ptr %55, i32 0, i32 4
  store i64 14, ptr %473, align 16
  %474 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %58, i32 0, i32 0
  %475 = getelementptr inbounds [5 x i64], ptr %54, i64 0, i64 0
  store ptr %475, ptr %474, align 8
  %476 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %58, i32 0, i32 1
  store i64 5, ptr %476, align 8
  %477 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %58, i32 0, i32 2
  store i64 8, ptr %477, align 8
  %478 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %58, i32 0, i32 3
  store i64 8, ptr %478, align 8
  %479 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %59, i32 0, i32 0
  %480 = getelementptr inbounds [5 x i64], ptr %55, i64 0, i64 0
  store ptr %480, ptr %479, align 8
  %481 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %59, i32 0, i32 1
  store i64 5, ptr %481, align 8
  %482 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %59, i32 0, i32 2
  store i64 8, ptr %482, align 8
  %483 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %59, i32 0, i32 3
  store i64 8, ptr %483, align 8
  %484 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %60, i32 0, i32 0
  %485 = getelementptr inbounds [3 x i64], ptr %56, i64 0, i64 0
  store ptr %485, ptr %484, align 8
  %486 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %60, i32 0, i32 1
  store i64 3, ptr %486, align 8
  %487 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %60, i32 0, i32 2
  store i64 8, ptr %487, align 8
  %488 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %60, i32 0, i32 3
  store i64 8, ptr %488, align 8
  %489 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %61, i32 0, i32 0
  %490 = getelementptr inbounds [3 x i64], ptr %57, i64 0, i64 0
  store ptr %490, ptr %489, align 8
  %491 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %61, i32 0, i32 1
  store i64 3, ptr %491, align 8
  %492 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %61, i32 0, i32 2
  store i64 8, ptr %492, align 8
  %493 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %61, i32 0, i32 3
  store i64 8, ptr %493, align 8
  call void @topk(ptr noundef %58, i64 noundef 5, i64 noundef 3, ptr noundef %59, ptr noundef %60, ptr noundef %61)
  %494 = getelementptr inbounds [3 x i64], ptr %56, i64 0, i64 0
  %495 = load i64, ptr %494, align 16
  %496 = icmp eq i64 %495, 12
  br i1 %496, label %497, label %517

497:                                              ; preds = %458
  %498 = getelementptr inbounds [3 x i64], ptr %56, i64 0, i64 1
  %499 = load i64, ptr %498, align 8
  %500 = icmp eq i64 %499, 14
  br i1 %500, label %501, label %517

501:                                              ; preds = %497
  %502 = getelementptr inbounds [3 x i64], ptr %56, i64 0, i64 2
  %503 = load i64, ptr %502, align 16
  %504 = icmp eq i64 %503, 10
  br i1 %504, label %505, label %517

505:                                              ; preds = %501
  %506 = getelementptr inbounds [3 x i64], ptr %57, i64 0, i64 0
  %507 = load i64, ptr %506, align 16
  %508 = icmp eq i64 %507, 9
  br i1 %508, label %509, label %517

509:                                              ; preds = %505
  %510 = getelementptr inbounds [3 x i64], ptr %57, i64 0, i64 1
  %511 = load i64, ptr %510, align 8
  %512 = icmp eq i64 %511, 7
  br i1 %512, label %513, label %517

513:                                              ; preds = %509
  %514 = getelementptr inbounds [3 x i64], ptr %57, i64 0, i64 2
  %515 = load i64, ptr %514, align 16
  %516 = icmp eq i64 %515, 5
  br label %517

517:                                              ; preds = %513, %509, %505, %501, %497, %458
  %518 = phi i1 [ false, %509 ], [ false, %505 ], [ false, %501 ], [ false, %497 ], [ false, %458 ], [ %516, %513 ]
  %519 = zext i1 %518 to i32
  store i32 %519, ptr %62, align 4
  %520 = load i32, ptr %62, align 4
  %521 = icmp ne i32 %520, 0
  %522 = zext i1 %521 to i64
  %523 = select i1 %521, ptr @.str.1, ptr @.str.2
  %524 = call i32 (ptr, ...) @printf(ptr noundef @.str.8, ptr noundef %523)
  %525 = call i64 @argmax(ptr noundef %58, i64 noundef 5)
  %526 = icmp eq i64 %525, 2
  %527 = zext i1 %526 to i64
  %528 = select i1 %526, ptr @.str.1, ptr @.str.2
  %529 = call i32 (ptr, ...) @printf(ptr noundef @.str.9, ptr noundef %528)
  call void @llvm.memcpy.p0.p0.i64(ptr align 16 %63, ptr align 16 @__const.main.ms, i64 32, i1 false)
  call void @llvm.memcpy.p0.p0.i64(ptr align 16 %64, ptr align 16 @__const.main.mv, i64 32, i1 false)
  %530 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %66, i32 0, i32 0
  %531 = getelementptr inbounds [4 x i64], ptr %63, i64 0, i64 0
  store ptr %531, ptr %530, align 8
  %532 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %66, i32 0, i32 1
  store i64 4, ptr %532, align 8
  %533 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %66, i32 0, i32 2
  store i64 8, ptr %533, align 8
  %534 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %66, i32 0, i32 3
  store i64 8, ptr %534, align 8
  %535 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %67, i32 0, i32 0
  %536 = getelementptr inbounds [4 x i64], ptr %64, i64 0, i64 0
  store ptr %536, ptr %535, align 8
  %537 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %67, i32 0, i32 1
  store i64 4, ptr %537, align 8
  %538 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %67, i32 0, i32 2
  store i64 8, ptr %538, align 8
  %539 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %67, i32 0, i32 3
  store i64 8, ptr %539, align 8
  %540 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %68, i32 0, i32 0
  %541 = getelementptr inbounds [4 x i64], ptr %65, i64 0, i64 0
  store ptr %541, ptr %540, align 8
  %542 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %68, i32 0, i32 1
  store i64 4, ptr %542, align 8
  %543 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %68, i32 0, i32 2
  store i64 8, ptr %543, align 8
  %544 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %68, i32 0, i32 3
  store i64 8, ptr %544, align 8
  %545 = call i64 @mask_scores(ptr noundef %66, ptr noundef %67, i64 noundef 4, ptr noundef %68)
  store i64 %545, ptr %69, align 8
  %546 = load i64, ptr %69, align 8
  %547 = icmp eq i64 %546, 3
  br i1 %547, label %548, label %564

548:                                              ; preds = %517
  %549 = getelementptr inbounds [4 x i64], ptr %65, i64 0, i64 0
  %550 = load i64, ptr %549, align 16
  %551 = icmp eq i64 %550, 5
  br i1 %551, label %552, label %564

552:                                              ; preds = %548
  %553 = getelementptr inbounds [4 x i64], ptr %65, i64 0, i64 1
  %554 = load i64, ptr %553, align 8
  %555 = icmp eq i64 %554, -999999999
  br i1 %555, label %556, label %564

556:                                              ; preds = %552
  %557 = getelementptr inbounds [4 x i64], ptr %65, i64 0, i64 2
  %558 = load i64, ptr %557, align 16
  %559 = icmp eq i64 %558, 7
  br i1 %559, label %560, label %564

560:                                              ; preds = %556
  %561 = getelementptr inbounds [4 x i64], ptr %65, i64 0, i64 3
  %562 = load i64, ptr %561, align 8
  %563 = icmp eq i64 %562, 8
  br label %564

564:                                              ; preds = %560, %556, %552, %548, %517
  %565 = phi i1 [ false, %556 ], [ false, %552 ], [ false, %548 ], [ false, %517 ], [ %563, %560 ]
  %566 = zext i1 %565 to i32
  store i32 %566, ptr %70, align 4
  %567 = load i32, ptr %70, align 4
  %568 = icmp ne i32 %567, 0
  %569 = zext i1 %568 to i64
  %570 = select i1 %568, ptr @.str.1, ptr @.str.2
  %571 = load i64, ptr %69, align 8
  %572 = call i32 (ptr, ...) @printf(ptr noundef @.str.10, ptr noundef %570, i64 noundef %571)
  call void @llvm.memcpy.p0.p0.i64(ptr align 16 %71, ptr align 16 @__const.main.ik, i64 32, i1 false)
  %573 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %75, i32 0, i32 0
  %574 = getelementptr inbounds [4 x i64], ptr %71, i64 0, i64 0
  store ptr %574, ptr %573, align 8
  %575 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %75, i32 0, i32 1
  store i64 4, ptr %575, align 8
  %576 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %75, i32 0, i32 2
  store i64 8, ptr %576, align 8
  %577 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %75, i32 0, i32 3
  store i64 8, ptr %577, align 8
  %578 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %76, i32 0, i32 0
  %579 = getelementptr inbounds [8 x i64], ptr %72, i64 0, i64 0
  store ptr %579, ptr %578, align 8
  %580 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %76, i32 0, i32 1
  store i64 8, ptr %580, align 8
  %581 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %76, i32 0, i32 2
  store i64 8, ptr %581, align 8
  %582 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %76, i32 0, i32 3
  store i64 8, ptr %582, align 8
  %583 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %77, i32 0, i32 0
  %584 = getelementptr inbounds [4 x i64], ptr %73, i64 0, i64 0
  store ptr %584, ptr %583, align 8
  %585 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %77, i32 0, i32 1
  store i64 4, ptr %585, align 8
  %586 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %77, i32 0, i32 2
  store i64 8, ptr %586, align 8
  %587 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %77, i32 0, i32 3
  store i64 8, ptr %587, align 8
  %588 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %78, i32 0, i32 0
  %589 = getelementptr inbounds [4 x i64], ptr %74, i64 0, i64 0
  store ptr %589, ptr %588, align 8
  %590 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %78, i32 0, i32 1
  store i64 4, ptr %590, align 8
  %591 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %78, i32 0, i32 2
  store i64 8, ptr %591, align 8
  %592 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %78, i32 0, i32 3
  store i64 8, ptr %592, align 8
  call void @build_index(ptr noundef %75, i64 noundef 4, i64 noundef 8, ptr noundef %76, ptr noundef %77)
  %593 = call i64 @index_lookup(ptr noundef %75, i64 noundef 4, ptr noundef %76, i64 noundef 8, ptr noundef %77, i64 noundef 3, ptr noundef %78)
  store i64 %593, ptr %79, align 8
  %594 = call i64 @index_lookup(ptr noundef %75, i64 noundef 4, ptr noundef %76, i64 noundef 8, ptr noundef %77, i64 noundef 9, ptr noundef %78)
  store i64 %594, ptr %80, align 8
  %595 = load i64, ptr %79, align 8
  %596 = icmp eq i64 %595, 2
  br i1 %596, label %597, label %604

597:                                              ; preds = %564
  %598 = load i64, ptr %80, align 8
  %599 = icmp eq i64 %598, 1
  br i1 %599, label %600, label %604

600:                                              ; preds = %597
  %601 = getelementptr inbounds [4 x i64], ptr %74, i64 0, i64 0
  %602 = load i64, ptr %601, align 16
  %603 = icmp eq i64 %602, 3
  br label %604

604:                                              ; preds = %600, %597, %564
  %605 = phi i1 [ false, %597 ], [ false, %564 ], [ %603, %600 ]
  %606 = zext i1 %605 to i32
  store i32 %606, ptr %81, align 4
  %607 = load i32, ptr %81, align 4
  %608 = icmp ne i32 %607, 0
  %609 = zext i1 %608 to i64
  %610 = select i1 %608, ptr @.str.1, ptr @.str.2
  %611 = load i64, ptr %79, align 8
  %612 = load i64, ptr %80, align 8
  %613 = call i32 (ptr, ...) @printf(ptr noundef @.str.11, ptr noundef %610, i64 noundef %611, i64 noundef %612)
  call void @llvm.memset.p0.i64(ptr align 16 %82, i8 0, i64 48, i1 false)
  %614 = getelementptr inbounds [6 x i64], ptr %82, i32 0, i32 0
  store i64 1, ptr %614, align 16
  %615 = getelementptr inbounds [6 x i64], ptr %82, i32 0, i32 1
  store i64 1, ptr %615, align 8
  call void @llvm.memcpy.p0.p0.i64(ptr align 16 %83, ptr align 16 @__const.main.pfh, i64 24, i1 false)
  call void @llvm.memcpy.p0.p0.i64(ptr align 16 %84, ptr align 16 @__const.main.pfm, i64 24, i1 false)
  %616 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %86, i32 0, i32 0
  %617 = getelementptr inbounds [6 x i64], ptr %82, i64 0, i64 0
  store ptr %617, ptr %616, align 8
  %618 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %86, i32 0, i32 1
  store i64 6, ptr %618, align 8
  %619 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %86, i32 0, i32 2
  store i64 8, ptr %619, align 8
  %620 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %86, i32 0, i32 3
  store i64 8, ptr %620, align 8
  %621 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %87, i32 0, i32 0
  %622 = getelementptr inbounds [3 x i64], ptr %83, i64 0, i64 0
  store ptr %622, ptr %621, align 8
  %623 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %87, i32 0, i32 1
  store i64 3, ptr %623, align 8
  %624 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %87, i32 0, i32 2
  store i64 8, ptr %624, align 8
  %625 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %87, i32 0, i32 3
  store i64 8, ptr %625, align 8
  %626 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %88, i32 0, i32 0
  %627 = getelementptr inbounds [3 x i64], ptr %84, i64 0, i64 0
  store ptr %627, ptr %626, align 8
  %628 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %88, i32 0, i32 1
  store i64 3, ptr %628, align 8
  %629 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %88, i32 0, i32 2
  store i64 8, ptr %629, align 8
  %630 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %88, i32 0, i32 3
  store i64 8, ptr %630, align 8
  %631 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %89, i32 0, i32 0
  %632 = getelementptr inbounds [6 x i64], ptr %85, i64 0, i64 0
  store ptr %632, ptr %631, align 8
  %633 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %89, i32 0, i32 1
  store i64 6, ptr %633, align 8
  %634 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %89, i32 0, i32 2
  store i64 8, ptr %634, align 8
  %635 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %89, i32 0, i32 3
  store i64 8, ptr %635, align 8
  %636 = call i64 @frontier_closure(ptr noundef %86, i64 noundef 6, ptr noundef %87, ptr noundef %88, i64 noundef 3, ptr noundef %89)
  store i64 %636, ptr %90, align 8
  %637 = load i64, ptr %90, align 8
  %638 = icmp eq i64 %637, 2
  br i1 %638, label %639, label %647

639:                                              ; preds = %604
  %640 = getelementptr inbounds [6 x i64], ptr %85, i64 0, i64 0
  %641 = load i64, ptr %640, align 16
  %642 = icmp eq i64 %641, 2
  br i1 %642, label %643, label %647

643:                                              ; preds = %639
  %644 = getelementptr inbounds [6 x i64], ptr %85, i64 0, i64 1
  %645 = load i64, ptr %644, align 8
  %646 = icmp eq i64 %645, 3
  br label %647

647:                                              ; preds = %643, %639, %604
  %648 = phi i1 [ false, %639 ], [ false, %604 ], [ %646, %643 ]
  %649 = zext i1 %648 to i32
  store i32 %649, ptr %91, align 4
  %650 = load i32, ptr %91, align 4
  %651 = icmp ne i32 %650, 0
  %652 = zext i1 %651 to i64
  %653 = select i1 %651, ptr @.str.1, ptr @.str.2
  %654 = load i64, ptr %90, align 8
  %655 = call i32 (ptr, ...) @printf(ptr noundef @.str.12, ptr noundef %653, i64 noundef %654)
  call void @llvm.memset.p0.i64(ptr align 16 %92, i8 0, i64 48, i1 false)
  %656 = getelementptr inbounds [6 x i64], ptr %92, i32 0, i32 0
  store i64 1, ptr %656, align 16
  %657 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %94, i32 0, i32 0
  %658 = getelementptr inbounds [6 x i64], ptr %92, i64 0, i64 0
  store ptr %658, ptr %657, align 8
  %659 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %94, i32 0, i32 1
  store i64 6, ptr %659, align 8
  %660 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %94, i32 0, i32 2
  store i64 8, ptr %660, align 8
  %661 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %94, i32 0, i32 3
  store i64 8, ptr %661, align 8
  %662 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %95, i32 0, i32 0
  %663 = getelementptr inbounds [6 x i64], ptr %93, i64 0, i64 0
  store ptr %663, ptr %662, align 8
  %664 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %95, i32 0, i32 1
  store i64 6, ptr %664, align 8
  %665 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %95, i32 0, i32 2
  store i64 8, ptr %665, align 8
  %666 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %95, i32 0, i32 3
  store i64 8, ptr %666, align 8
  %667 = call i64 @frontier_missing(ptr noundef %94, i64 noundef 6, ptr noundef %87, ptr noundef %88, i64 noundef 3, ptr noundef %95)
  store i64 %667, ptr %96, align 8
  %668 = load i64, ptr %96, align 8
  %669 = icmp eq i64 %668, 6
  br i1 %669, label %670, label %678

670:                                              ; preds = %647
  %671 = getelementptr inbounds [6 x i64], ptr %93, i64 0, i64 0
  %672 = load i64, ptr %671, align 16
  %673 = icmp eq i64 %672, 1
  br i1 %673, label %674, label %678

674:                                              ; preds = %670
  %675 = getelementptr inbounds [6 x i64], ptr %93, i64 0, i64 1
  %676 = load i64, ptr %675, align 8
  %677 = icmp eq i64 %676, 2
  br label %678

678:                                              ; preds = %674, %670, %647
  %679 = phi i1 [ false, %670 ], [ false, %647 ], [ %677, %674 ]
  %680 = zext i1 %679 to i64
  %681 = select i1 %679, ptr @.str.1, ptr @.str.2
  %682 = load i64, ptr %96, align 8
  %683 = call i32 (ptr, ...) @printf(ptr noundef @.str.13, ptr noundef %681, i64 noundef %682)
  call void @llvm.memcpy.p0.p0.i64(ptr align 16 %97, ptr align 16 @__const.main.ba, i64 32, i1 false)
  %684 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %99, i32 0, i32 0
  %685 = getelementptr inbounds [4 x i64], ptr %97, i64 0, i64 0
  store ptr %685, ptr %684, align 8
  %686 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %99, i32 0, i32 1
  store i64 4, ptr %686, align 8
  %687 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %99, i32 0, i32 2
  store i64 8, ptr %687, align 8
  %688 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %99, i32 0, i32 3
  store i64 8, ptr %688, align 8
  %689 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %100, i32 0, i32 0
  %690 = getelementptr inbounds [4 x i64], ptr %98, i64 0, i64 0
  store ptr %690, ptr %689, align 8
  %691 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %100, i32 0, i32 1
  store i64 4, ptr %691, align 8
  %692 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %100, i32 0, i32 2
  store i64 8, ptr %692, align 8
  %693 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %100, i32 0, i32 3
  store i64 8, ptr %693, align 8
  %694 = call i64 @bfs(ptr noundef %99, i64 noundef 4, i64 noundef 0, ptr noundef %100)
  store i64 %694, ptr %101, align 8
  %695 = load i64, ptr %101, align 8
  %696 = icmp eq i64 %695, 3
  br i1 %696, label %697, label %709

697:                                              ; preds = %678
  %698 = getelementptr inbounds [4 x i64], ptr %98, i64 0, i64 0
  %699 = load i64, ptr %698, align 16
  %700 = icmp eq i64 %699, 0
  br i1 %700, label %701, label %709

701:                                              ; preds = %697
  %702 = getelementptr inbounds [4 x i64], ptr %98, i64 0, i64 1
  %703 = load i64, ptr %702, align 8
  %704 = icmp eq i64 %703, 1
  br i1 %704, label %705, label %709

705:                                              ; preds = %701
  %706 = getelementptr inbounds [4 x i64], ptr %98, i64 0, i64 2
  %707 = load i64, ptr %706, align 16
  %708 = icmp eq i64 %707, 2
  br label %709

709:                                              ; preds = %705, %701, %697, %678
  %710 = phi i1 [ false, %701 ], [ false, %697 ], [ false, %678 ], [ %708, %705 ]
  %711 = zext i1 %710 to i32
  store i32 %711, ptr %102, align 4
  %712 = load i32, ptr %102, align 4
  %713 = icmp ne i32 %712, 0
  %714 = zext i1 %713 to i64
  %715 = select i1 %713, ptr @.str.1, ptr @.str.2
  %716 = load i64, ptr %101, align 8
  %717 = call i32 (ptr, ...) @printf(ptr noundef @.str.14, ptr noundef %715, i64 noundef %716)
  call void @llvm.memcpy.p0.p0.i64(ptr align 16 %103, ptr align 16 @__const.main.ptu, i64 24, i1 false)
  call void @llvm.memcpy.p0.p0.i64(ptr align 16 %104, ptr align 16 @__const.main.ptv, i64 24, i1 false)
  %718 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %106, i32 0, i32 0
  %719 = getelementptr inbounds [3 x i64], ptr %103, i64 0, i64 0
  store ptr %719, ptr %718, align 8
  %720 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %106, i32 0, i32 1
  store i64 3, ptr %720, align 8
  %721 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %106, i32 0, i32 2
  store i64 8, ptr %721, align 8
  %722 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %106, i32 0, i32 3
  store i64 8, ptr %722, align 8
  %723 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %107, i32 0, i32 0
  %724 = getelementptr inbounds [3 x i64], ptr %104, i64 0, i64 0
  store ptr %724, ptr %723, align 8
  %725 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %107, i32 0, i32 1
  store i64 3, ptr %725, align 8
  %726 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %107, i32 0, i32 2
  store i64 8, ptr %726, align 8
  %727 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %107, i32 0, i32 3
  store i64 8, ptr %727, align 8
  %728 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %108, i32 0, i32 0
  %729 = getelementptr inbounds [4 x i64], ptr %105, i64 0, i64 0
  store ptr %729, ptr %728, align 8
  %730 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %108, i32 0, i32 1
  store i64 4, ptr %730, align 8
  %731 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %108, i32 0, i32 2
  store i64 8, ptr %731, align 8
  %732 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %108, i32 0, i32 3
  store i64 8, ptr %732, align 8
  %733 = call i64 @topo(ptr noundef %106, ptr noundef %107, i64 noundef 3, i64 noundef 4, ptr noundef %108)
  store i64 %733, ptr %109, align 8
  %734 = load i64, ptr %109, align 8
  %735 = icmp eq i64 %734, 4
  br i1 %735, label %736, label %740

736:                                              ; preds = %709
  %737 = getelementptr inbounds [4 x i64], ptr %105, i64 0, i64 0
  %738 = load i64, ptr %737, align 16
  %739 = icmp eq i64 %738, 0
  br label %740

740:                                              ; preds = %736, %709
  %741 = phi i1 [ false, %709 ], [ %739, %736 ]
  %742 = zext i1 %741 to i32
  store i32 %742, ptr %110, align 4
  %743 = load i32, ptr %110, align 4
  %744 = icmp ne i32 %743, 0
  %745 = zext i1 %744 to i64
  %746 = select i1 %744, ptr @.str.1, ptr @.str.2
  %747 = load i64, ptr %109, align 8
  %748 = call i32 (ptr, ...) @printf(ptr noundef @.str.15, ptr noundef %746, i64 noundef %747)
  call void @llvm.memcpy.p0.p0.i64(ptr align 16 %111, ptr align 16 @__const.main.pp, i64 32, i1 false)
  %749 = getelementptr inbounds [4 x i64], ptr %111, i64 0, i64 0
  %750 = call i64 @uf_union(ptr noundef %749, i64 noundef 0, i64 noundef 1)
  store i64 %750, ptr %112, align 8
  %751 = getelementptr inbounds [4 x i64], ptr %111, i64 0, i64 0
  %752 = call i64 @uf_union(ptr noundef %751, i64 noundef 2, i64 noundef 3)
  store i64 %752, ptr %113, align 8
  %753 = getelementptr inbounds [4 x i64], ptr %111, i64 0, i64 0
  %754 = call i64 @uf_union(ptr noundef %753, i64 noundef 1, i64 noundef 2)
  store i64 %754, ptr %114, align 8
  %755 = load i64, ptr %112, align 8
  %756 = icmp eq i64 %755, 1
  br i1 %756, label %757, label %769

757:                                              ; preds = %740
  %758 = load i64, ptr %113, align 8
  %759 = icmp eq i64 %758, 1
  br i1 %759, label %760, label %769

760:                                              ; preds = %757
  %761 = load i64, ptr %114, align 8
  %762 = icmp eq i64 %761, 1
  br i1 %762, label %763, label %769

763:                                              ; preds = %760
  %764 = getelementptr inbounds [4 x i64], ptr %111, i64 0, i64 0
  %765 = call i64 @uf_find(ptr noundef %764, i64 noundef 0)
  %766 = getelementptr inbounds [4 x i64], ptr %111, i64 0, i64 0
  %767 = call i64 @uf_find(ptr noundef %766, i64 noundef 3)
  %768 = icmp eq i64 %765, %767
  br label %769

769:                                              ; preds = %763, %760, %757, %740
  %770 = phi i1 [ false, %760 ], [ false, %757 ], [ false, %740 ], [ %768, %763 ]
  %771 = zext i1 %770 to i32
  store i32 %771, ptr %115, align 4
  %772 = load i32, ptr %115, align 4
  %773 = icmp ne i32 %772, 0
  %774 = zext i1 %773 to i64
  %775 = select i1 %773, ptr @.str.1, ptr @.str.2
  %776 = call i32 (ptr, ...) @printf(ptr noundef @.str.16, ptr noundef %775)
  call void @llvm.memcpy.p0.p0.i64(ptr align 16 %116, ptr align 16 @__const.main.ca, i64 32, i1 false)
  %777 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %118, i32 0, i32 0
  %778 = getelementptr inbounds [4 x i64], ptr %116, i64 0, i64 0
  store ptr %778, ptr %777, align 8
  %779 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %118, i32 0, i32 1
  store i64 4, ptr %779, align 8
  %780 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %118, i32 0, i32 2
  store i64 8, ptr %780, align 8
  %781 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %118, i32 0, i32 3
  store i64 8, ptr %781, align 8
  %782 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %119, i32 0, i32 0
  %783 = getelementptr inbounds [4 x i64], ptr %117, i64 0, i64 0
  store ptr %783, ptr %782, align 8
  %784 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %119, i32 0, i32 1
  store i64 4, ptr %784, align 8
  %785 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %119, i32 0, i32 2
  store i64 8, ptr %785, align 8
  %786 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %119, i32 0, i32 3
  store i64 8, ptr %786, align 8
  call void @bitset_closure(ptr noundef %118, i64 noundef 4, ptr noundef %119)
  %787 = getelementptr inbounds [4 x i64], ptr %117, i64 0, i64 0
  %788 = load i64, ptr %787, align 16
  %789 = icmp eq i64 %788, 6
  br i1 %789, label %790, label %794

790:                                              ; preds = %769
  %791 = getelementptr inbounds [4 x i64], ptr %117, i64 0, i64 1
  %792 = load i64, ptr %791, align 8
  %793 = icmp eq i64 %792, 4
  br label %794

794:                                              ; preds = %790, %769
  %795 = phi i1 [ false, %769 ], [ %793, %790 ]
  %796 = zext i1 %795 to i32
  store i32 %796, ptr %120, align 4
  %797 = load i32, ptr %120, align 4
  %798 = icmp ne i32 %797, 0
  %799 = zext i1 %798 to i64
  %800 = select i1 %798, ptr @.str.1, ptr @.str.2
  %801 = call i32 (ptr, ...) @printf(ptr noundef @.str.17, ptr noundef %800)
  call void @llvm.memset.p0.i64(ptr align 16 %121, i8 0, i64 40, i1 false)
  %802 = getelementptr inbounds [5 x i64], ptr %121, i32 0, i32 0
  store i64 3, ptr %802, align 16
  %803 = getelementptr inbounds [5 x i64], ptr %121, i32 0, i32 1
  store i64 7, ptr %803, align 8
  %804 = getelementptr inbounds [5 x i64], ptr %121, i32 0, i32 2
  store i64 3, ptr %804, align 16
  %805 = getelementptr inbounds [5 x i64], ptr %121, i32 0, i32 3
  store i64 9, ptr %805, align 8
  %806 = getelementptr inbounds [5 x i64], ptr %121, i32 0, i32 4
  store i64 -1, ptr %806, align 16
  %807 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %125, i32 0, i32 0
  %808 = getelementptr inbounds [5 x i64], ptr %121, i64 0, i64 0
  store ptr %808, ptr %807, align 8
  %809 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %125, i32 0, i32 1
  store i64 5, ptr %809, align 8
  %810 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %125, i32 0, i32 2
  store i64 8, ptr %810, align 8
  %811 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %125, i32 0, i32 3
  store i64 8, ptr %811, align 8
  %812 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %126, i32 0, i32 0
  %813 = getelementptr inbounds [8 x i64], ptr %122, i64 0, i64 0
  store ptr %813, ptr %812, align 8
  %814 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %126, i32 0, i32 1
  store i64 8, ptr %814, align 8
  %815 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %126, i32 0, i32 2
  store i64 8, ptr %815, align 8
  %816 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %126, i32 0, i32 3
  store i64 8, ptr %816, align 8
  %817 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %127, i32 0, i32 0
  %818 = getelementptr inbounds [5 x i64], ptr %123, i64 0, i64 0
  store ptr %818, ptr %817, align 8
  %819 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %127, i32 0, i32 1
  store i64 5, ptr %819, align 8
  %820 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %127, i32 0, i32 2
  store i64 8, ptr %820, align 8
  %821 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %127, i32 0, i32 3
  store i64 8, ptr %821, align 8
  %822 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %128, i32 0, i32 0
  %823 = getelementptr inbounds [5 x i64], ptr %124, i64 0, i64 0
  store ptr %823, ptr %822, align 8
  %824 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %128, i32 0, i32 1
  store i64 5, ptr %824, align 8
  %825 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %128, i32 0, i32 2
  store i64 8, ptr %825, align 8
  %826 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %128, i32 0, i32 3
  store i64 8, ptr %826, align 8
  call void @build_index(ptr noundef %125, i64 noundef 4, i64 noundef 8, ptr noundef %126, ptr noundef %127)
  call void @index_add(ptr noundef %125, ptr noundef %126, i64 noundef 8, ptr noundef %127, i64 noundef 4, i64 noundef 3)
  %827 = call i64 @index_lookup(ptr noundef %125, i64 noundef 5, ptr noundef %126, i64 noundef 8, ptr noundef %127, i64 noundef 3, ptr noundef %128)
  store i64 %827, ptr %129, align 8
  %828 = call i64 @index_remove(ptr noundef %125, i64 noundef 0)
  store i64 %828, ptr %130, align 8
  %829 = call i64 @index_lookup(ptr noundef %125, i64 noundef 5, ptr noundef %126, i64 noundef 8, ptr noundef %127, i64 noundef 3, ptr noundef %128)
  store i64 %829, ptr %131, align 8
  %830 = load i64, ptr %129, align 8
  %831 = icmp eq i64 %830, 3
  br i1 %831, label %832, label %838

832:                                              ; preds = %794
  %833 = load i64, ptr %130, align 8
  %834 = icmp eq i64 %833, 3
  br i1 %834, label %835, label %838

835:                                              ; preds = %832
  %836 = load i64, ptr %131, align 8
  %837 = icmp eq i64 %836, 2
  br label %838

838:                                              ; preds = %835, %832, %794
  %839 = phi i1 [ false, %832 ], [ false, %794 ], [ %837, %835 ]
  %840 = zext i1 %839 to i32
  store i32 %840, ptr %132, align 4
  %841 = load i32, ptr %132, align 4
  %842 = icmp ne i32 %841, 0
  %843 = zext i1 %842 to i64
  %844 = select i1 %842, ptr @.str.1, ptr @.str.2
  %845 = load i64, ptr %129, align 8
  %846 = load i64, ptr %130, align 8
  %847 = load i64, ptr %131, align 8
  %848 = call i32 (ptr, ...) @printf(ptr noundef @.str.18, ptr noundef %844, i64 noundef %845, i64 noundef %846, i64 noundef %847)
  %849 = call i64 @bce_q16(i64 noundef 0, i64 noundef 65536)
  store i64 %849, ptr %133, align 8
  %850 = call i64 @bce_q16(i64 noundef 0, i64 noundef 0)
  store i64 %850, ptr %134, align 8
  %851 = load i64, ptr %133, align 8
  %852 = icmp sgt i64 %851, 45000
  br i1 %852, label %853, label %862

853:                                              ; preds = %838
  %854 = load i64, ptr %133, align 8
  %855 = icmp slt i64 %854, 46000
  br i1 %855, label %856, label %862

856:                                              ; preds = %853
  %857 = load i64, ptr %134, align 8
  %858 = icmp sgt i64 %857, 45000
  br i1 %858, label %859, label %862

859:                                              ; preds = %856
  %860 = load i64, ptr %134, align 8
  %861 = icmp slt i64 %860, 46000
  br label %862

862:                                              ; preds = %859, %856, %853, %838
  %863 = phi i1 [ false, %856 ], [ false, %853 ], [ false, %838 ], [ %861, %859 ]
  %864 = zext i1 %863 to i32
  store i32 %864, ptr %135, align 4
  %865 = load i32, ptr %135, align 4
  %866 = icmp ne i32 %865, 0
  %867 = zext i1 %866 to i64
  %868 = select i1 %866, ptr @.str.1, ptr @.str.2
  %869 = load i64, ptr %133, align 8
  %870 = load i64, ptr %134, align 8
  %871 = call i32 (ptr, ...) @printf(ptr noundef @.str.19, ptr noundef %868, i64 noundef %869, i64 noundef %870)
  call void @llvm.memcpy.p0.p0.i64(ptr align 16 %136, ptr align 16 @__const.main.bw, i64 32, i1 false)
  call void @llvm.memcpy.p0.p0.i64(ptr align 16 %137, ptr align 16 @__const.main.bdy, i64 16, i1 false)
  %872 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %139, i32 0, i32 0
  %873 = getelementptr inbounds [4 x i64], ptr %136, i64 0, i64 0
  store ptr %873, ptr %872, align 8
  %874 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %139, i32 0, i32 1
  store i64 4, ptr %874, align 8
  %875 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %139, i32 0, i32 2
  store i64 8, ptr %875, align 8
  %876 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %139, i32 0, i32 3
  store i64 8, ptr %876, align 8
  %877 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %140, i32 0, i32 0
  %878 = getelementptr inbounds [2 x i64], ptr %137, i64 0, i64 0
  store ptr %878, ptr %877, align 8
  %879 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %140, i32 0, i32 1
  store i64 2, ptr %879, align 8
  %880 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %140, i32 0, i32 2
  store i64 8, ptr %880, align 8
  %881 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %140, i32 0, i32 3
  store i64 8, ptr %881, align 8
  %882 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %141, i32 0, i32 0
  %883 = getelementptr inbounds [2 x i64], ptr %138, i64 0, i64 0
  store ptr %883, ptr %882, align 8
  %884 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %141, i32 0, i32 1
  store i64 2, ptr %884, align 8
  %885 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %141, i32 0, i32 2
  store i64 8, ptr %885, align 8
  %886 = getelementptr inbounds nuw %struct.MaruArrayView, ptr %141, i32 0, i32 3
  store i64 8, ptr %886, align 8
  call void @backward_matvec(ptr noundef %139, i64 noundef 2, i64 noundef 2, ptr noundef %140, ptr noundef %141)
  %887 = getelementptr inbounds [2 x i64], ptr %138, i64 0, i64 0
  %888 = load i64, ptr %887, align 16
  %889 = icmp eq i64 %888, 131072
  br i1 %889, label %890, label %894

890:                                              ; preds = %862
  %891 = getelementptr inbounds [2 x i64], ptr %138, i64 0, i64 1
  %892 = load i64, ptr %891, align 8
  %893 = icmp eq i64 %892, 196608
  br label %894

894:                                              ; preds = %890, %862
  %895 = phi i1 [ false, %862 ], [ %893, %890 ]
  %896 = zext i1 %895 to i32
  store i32 %896, ptr %142, align 4
  %897 = load i32, ptr %142, align 4
  %898 = icmp ne i32 %897, 0
  %899 = zext i1 %898 to i64
  %900 = select i1 %898, ptr @.str.1, ptr @.str.2
  %901 = call i32 (ptr, ...) @printf(ptr noundef @.str.20, ptr noundef %900)
  store i64 0, ptr %143, align 8
  store i64 0, ptr %144, align 8
  store i64 6553600, ptr %145, align 8
  store i64 1, ptr %146, align 8
  br label %902

902:                                              ; preds = %909, %894
  %903 = load i64, ptr %146, align 8
  %904 = icmp sle i64 %903, 3
  br i1 %904, label %905, label %912

905:                                              ; preds = %902
  %906 = load i64, ptr %145, align 8
  %907 = load i64, ptr %146, align 8
  %908 = call i64 @adam_step(i64 noundef %906, i64 noundef 655360, ptr noundef %143, ptr noundef %144, i64 noundef %907, i64 noundef 3277, i64 noundef 58982, i64 noundef 64225, i64 noundef 655)
  store i64 %908, ptr %145, align 8
  br label %909

909:                                              ; preds = %905
  %910 = load i64, ptr %146, align 8
  %911 = add nsw i64 %910, 1
  store i64 %911, ptr %146, align 8
  br label %902, !llvm.loop !14

912:                                              ; preds = %902
  %913 = load i64, ptr %145, align 8
  %914 = icmp slt i64 %913, 6553600
  br i1 %914, label %915, label %918

915:                                              ; preds = %912
  %916 = load i64, ptr %145, align 8
  %917 = icmp sgt i64 %916, 0
  br label %918

918:                                              ; preds = %915, %912
  %919 = phi i1 [ false, %912 ], [ %917, %915 ]
  %920 = zext i1 %919 to i32
  store i32 %920, ptr %147, align 4
  %921 = load i32, ptr %147, align 4
  %922 = icmp ne i32 %921, 0
  %923 = zext i1 %922 to i64
  %924 = select i1 %922, ptr @.str.1, ptr @.str.2
  %925 = load i64, ptr %145, align 8
  %926 = call i32 (ptr, ...) @printf(ptr noundef @.str.21, ptr noundef %924, i64 noundef %925)
  %927 = call i32 (ptr, ...) @printf(ptr noundef @.str.22)
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
  br label %21, !llvm.loop !15

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
  br label %16, !llvm.loop !16

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
  br label %17, !llvm.loop !17

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
  br label %18, !llvm.loop !18

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
  br label %38, !llvm.loop !19

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
  br label %62, !llvm.loop !20

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
  br label %19, !llvm.loop !21

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
  br label %36, !llvm.loop !22

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
  br label %62, !llvm.loop !23

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
  br label %117, !llvm.loop !24

151:                                              ; preds = %117
  br label %152

152:                                              ; preds = %151
  %153 = load i64, ptr %23, align 8
  %154 = add nsw i64 %153, 1
  store i64 %154, ptr %23, align 8
  br label %50, !llvm.loop !25

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
  br label %160, !llvm.loop !26

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
  br label %192, !llvm.loop !27

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
  br label %188, !llvm.loop !28

221:                                              ; preds = %188
  br label %222

222:                                              ; preds = %221
  %223 = load i64, ptr %34, align 8
  %224 = add nsw i64 %223, 1
  store i64 %224, ptr %34, align 8
  br label %156, !llvm.loop !29

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
  br label %249, !llvm.loop !30

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
  br label %292, !llvm.loop !31

311:                                              ; preds = %292
  br label %312

312:                                              ; preds = %311
  %313 = load i64, ptr %43, align 8
  %314 = add nsw i64 %313, 1
  store i64 %314, ptr %43, align 8
  br label %226, !llvm.loop !32

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
  br label %125, !llvm.loop !33

162:                                              ; preds = %125
  br label %163

163:                                              ; preds = %162
  %164 = load i32, ptr %29, align 4
  %165 = add nsw i32 %164, 1
  store i32 %165, ptr %29, align 4
  br label %85, !llvm.loop !34

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
  br label %171, !llvm.loop !35

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
  br label %206, !llvm.loop !36

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
  br label %202, !llvm.loop !37

238:                                              ; preds = %202
  br label %239

239:                                              ; preds = %238
  %240 = load i32, ptr %40, align 4
  %241 = add nsw i32 %240, 1
  store i32 %241, ptr %40, align 4
  br label %167, !llvm.loop !38

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
  br label %259, !llvm.loop !39

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
  br label %305, !llvm.loop !40

326:                                              ; preds = %305
  br label %327

327:                                              ; preds = %326
  %328 = load i32, ptr %49, align 4
  %329 = add nsw i32 %328, 1
  store i32 %329, ptr %49, align 4
  br label %243, !llvm.loop !41

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
  br label %22, !llvm.loop !42

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
  br label %44, !llvm.loop !43

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
  br label %67, !llvm.loop !44

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
  br label %35, !llvm.loop !45

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
  br label %108, !llvm.loop !46

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
  br label %11, !llvm.loop !47

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
  br label %13, !llvm.loop !48

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
  br label %14, !llvm.loop !49

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
  br label %25, !llvm.loop !50

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
  br label %24, !llvm.loop !51

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
  br label %22, !llvm.loop !52

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
  br label %60, !llvm.loop !53

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
  br label %43, !llvm.loop !54

95:                                               ; preds = %43
  br label %39, !llvm.loop !55

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
  br label %36, !llvm.loop !56

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
  br label %19, !llvm.loop !57

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
  br label %39, !llvm.loop !58

66:                                               ; preds = %39
  br label %23, !llvm.loop !59

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
  br label %21, !llvm.loop !60

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
  br label %36, !llvm.loop !61

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
  br label %68, !llvm.loop !62

97:                                               ; preds = %68
  br label %55, !llvm.loop !63

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
  br label %5, !llvm.loop !64

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
  br label %12, !llvm.loop !65

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
  br label %31, !llvm.loop !66

55:                                               ; preds = %31
  br label %56

56:                                               ; preds = %55
  %57 = load i64, ptr %9, align 8
  %58 = add nsw i64 %57, 1
  store i64 %58, ptr %9, align 8
  br label %26, !llvm.loop !67

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
  br label %60, !llvm.loop !68

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
  br label %19, !llvm.loop !69

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
  br label %14, !llvm.loop !70

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
  br label %17, !llvm.loop !71

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
  br label %18, !llvm.loop !72

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
  br label %9, !llvm.loop !73

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
  br label %9, !llvm.loop !74

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
