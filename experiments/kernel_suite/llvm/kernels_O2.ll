; ModuleID = 'src/kernels.c'
source_filename = "src/kernels.c"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-linux-gnu"

%struct.MaruArrayView = type { ptr, i64, i64, i64 }

@__const.main.b = private unnamed_addr constant [2 x i64] [i64 100, i64 200], align 16
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
  %42 = alloca [6 x i64], align 16
  %43 = alloca [6 x i64], align 16
  %44 = alloca [4 x i64], align 16
  %45 = alloca [3 x i64], align 16
  %46 = alloca [3 x i64], align 16
  %47 = alloca %struct.MaruArrayView, align 8
  %48 = alloca %struct.MaruArrayView, align 8
  %49 = alloca [3 x i64], align 16
  %50 = alloca [3 x i64], align 16
  %51 = alloca [3 x i64], align 16
  %52 = alloca [3 x i64], align 16
  %53 = alloca %struct.MaruArrayView, align 8
  %54 = alloca %struct.MaruArrayView, align 8
  %55 = alloca %struct.MaruArrayView, align 8
  %56 = alloca %struct.MaruArrayView, align 8
  %57 = alloca [12 x i64], align 16
  %58 = alloca [48 x i64], align 16
  %59 = alloca [12 x i64], align 16
  %60 = alloca [16 x i64], align 16
  %61 = alloca [4 x i64], align 16
  %62 = alloca [4 x i64], align 16
  %63 = alloca [4 x i64], align 16
  %64 = alloca [12 x i64], align 16
  %65 = alloca [12 x i64], align 16
  %66 = alloca %struct.MaruArrayView, align 8
  %67 = alloca %struct.MaruArrayView, align 8
  %68 = alloca [5 x i64], align 16
  %69 = alloca [5 x i64], align 16
  %70 = alloca [3 x i64], align 16
  %71 = alloca [3 x i64], align 16
  %72 = alloca %struct.MaruArrayView, align 8
  %73 = alloca %struct.MaruArrayView, align 8
  %74 = alloca %struct.MaruArrayView, align 8
  %75 = alloca %struct.MaruArrayView, align 8
  %76 = alloca [4 x i64], align 16
  %77 = alloca [8 x i64], align 16
  %78 = alloca [4 x i64], align 16
  %79 = alloca [4 x i64], align 16
  %80 = alloca %struct.MaruArrayView, align 8
  %81 = alloca %struct.MaruArrayView, align 8
  %82 = alloca %struct.MaruArrayView, align 8
  %83 = alloca [4 x i64], align 16
  %84 = alloca [4 x i64], align 16
  %85 = alloca [4 x i64], align 16
  %86 = alloca [5 x i64], align 16
  %87 = alloca [8 x i64], align 16
  %88 = alloca [5 x i64], align 16
  %89 = alloca %struct.MaruArrayView, align 8
  %90 = alloca %struct.MaruArrayView, align 8
  %91 = alloca %struct.MaruArrayView, align 8
  %92 = alloca [9 x i64], align 16
  %93 = alloca [3 x i64], align 16
  %94 = alloca [3 x i64], align 16
  %95 = alloca [3 x i64], align 16
  %96 = alloca [3 x i64], align 16
  %97 = alloca %struct.MaruArrayView, align 8
  %98 = alloca %struct.MaruArrayView, align 8
  %99 = alloca %struct.MaruArrayView, align 8
  %100 = alloca [6 x i64], align 16
  call void @llvm.lifetime.start.p0(ptr nonnull %42) #9
  call void @llvm.memset.p0.i64(ptr noundef nonnull align 16 dereferenceable(48) %42, i8 0, i64 48, i1 false)
  store i64 65536, ptr %42, align 16
  %101 = getelementptr inbounds nuw i8, ptr %42, i64 32
  store i64 65536, ptr %101, align 16
  %102 = tail call i32 (ptr, ...) @printf(ptr noundef nonnull dereferenceable(1) @.str, ptr noundef nonnull @.str.1, i64 noundef 65636, i64 noundef 131272)
  call void @llvm.lifetime.start.p0(ptr nonnull %43) #9
  store i64 65536, ptr %43, align 16
  %103 = getelementptr inbounds nuw i8, ptr %43, i64 8
  store i64 131072, ptr %103, align 8
  %104 = getelementptr inbounds nuw i8, ptr %43, i64 16
  store i64 196608, ptr %104, align 16
  %105 = getelementptr inbounds nuw i8, ptr %43, i64 24
  store i64 131072, ptr %105, align 8
  %106 = getelementptr inbounds nuw i8, ptr %43, i64 32
  store i64 196608, ptr %106, align 16
  %107 = getelementptr inbounds nuw i8, ptr %43, i64 40
  store i64 262144, ptr %107, align 8
  call void @llvm.lifetime.start.p0(ptr nonnull %44) #9
  br label %108

108:                                              ; preds = %395, %0
  %109 = phi i1 [ true, %0 ], [ false, %395 ]
  %110 = phi i64 [ 0, %0 ], [ 1, %395 ]
  %111 = mul nuw nsw i64 %110, 24
  %112 = getelementptr inbounds nuw i8, ptr %43, i64 %111
  %113 = shl nuw nsw i64 %110, 4
  %114 = getelementptr inbounds nuw i8, ptr %44, i64 %113
  %115 = getelementptr inbounds nuw i8, ptr %112, i64 8
  %116 = getelementptr inbounds nuw i8, ptr %112, i64 16
  %117 = load i8, ptr %112, align 8, !tbaa !9
  %118 = getelementptr inbounds nuw i8, ptr %112, i64 1
  %119 = load i8, ptr %118, align 1, !tbaa !9
  %120 = getelementptr inbounds nuw i8, ptr %112, i64 2
  %121 = load i8, ptr %120, align 2, !tbaa !9
  %122 = getelementptr inbounds nuw i8, ptr %112, i64 3
  %123 = load i8, ptr %122, align 1, !tbaa !9
  %124 = getelementptr inbounds nuw i8, ptr %112, i64 4
  %125 = load i8, ptr %124, align 4, !tbaa !9
  %126 = getelementptr inbounds nuw i8, ptr %112, i64 5
  %127 = load i8, ptr %126, align 1, !tbaa !9
  %128 = getelementptr inbounds nuw i8, ptr %112, i64 6
  %129 = load i8, ptr %128, align 2, !tbaa !9
  %130 = getelementptr inbounds nuw i8, ptr %112, i64 7
  %131 = load i8, ptr %130, align 1, !tbaa !9
  %132 = load i8, ptr %115, align 8, !tbaa !9
  %133 = getelementptr inbounds nuw i8, ptr %112, i64 9
  %134 = load i8, ptr %133, align 1, !tbaa !9
  %135 = getelementptr inbounds nuw i8, ptr %112, i64 10
  %136 = load i8, ptr %135, align 2, !tbaa !9
  %137 = getelementptr inbounds nuw i8, ptr %112, i64 11
  %138 = load i8, ptr %137, align 1, !tbaa !9
  %139 = getelementptr inbounds nuw i8, ptr %112, i64 12
  %140 = load i8, ptr %139, align 4, !tbaa !9
  %141 = getelementptr inbounds nuw i8, ptr %112, i64 13
  %142 = load i8, ptr %141, align 1, !tbaa !9
  %143 = getelementptr inbounds nuw i8, ptr %112, i64 14
  %144 = load i8, ptr %143, align 2, !tbaa !9
  %145 = getelementptr inbounds nuw i8, ptr %112, i64 15
  %146 = load i8, ptr %145, align 1, !tbaa !9
  %147 = load i8, ptr %116, align 8, !tbaa !9
  %148 = getelementptr inbounds nuw i8, ptr %112, i64 17
  %149 = load i8, ptr %148, align 1, !tbaa !9
  %150 = getelementptr inbounds nuw i8, ptr %112, i64 18
  %151 = load i8, ptr %150, align 2, !tbaa !9
  %152 = getelementptr inbounds nuw i8, ptr %112, i64 19
  %153 = load i8, ptr %152, align 1, !tbaa !9
  %154 = getelementptr inbounds nuw i8, ptr %112, i64 20
  %155 = load i8, ptr %154, align 4, !tbaa !9
  %156 = getelementptr inbounds nuw i8, ptr %112, i64 21
  %157 = load i8, ptr %156, align 1, !tbaa !9
  %158 = getelementptr inbounds nuw i8, ptr %112, i64 22
  %159 = load i8, ptr %158, align 2, !tbaa !9
  %160 = getelementptr inbounds nuw i8, ptr %112, i64 23
  %161 = load i8, ptr %160, align 1, !tbaa !9
  %162 = zext i8 %147 to i64
  %163 = zext i8 %149 to i64
  %164 = shl nuw nsw i64 %163, 8
  %165 = or disjoint i64 %164, %162
  %166 = zext i8 %151 to i64
  %167 = shl nuw nsw i64 %166, 16
  %168 = or disjoint i64 %167, %165
  %169 = zext i8 %153 to i64
  %170 = shl nuw nsw i64 %169, 24
  %171 = or disjoint i64 %170, %168
  %172 = zext i8 %155 to i64
  %173 = shl nuw nsw i64 %172, 32
  %174 = or disjoint i64 %173, %171
  %175 = zext i8 %157 to i64
  %176 = shl nuw nsw i64 %175, 40
  %177 = or i64 %176, %174
  %178 = zext i8 %159 to i64
  %179 = shl nuw nsw i64 %178, 48
  %180 = or i64 %179, %177
  %181 = zext i8 %161 to i64
  %182 = shl nuw i64 %181, 56
  %183 = or i64 %182, %180
  %184 = zext i8 %132 to i64
  %185 = zext i8 %134 to i64
  %186 = shl nuw nsw i64 %185, 8
  %187 = or disjoint i64 %186, %184
  %188 = zext i8 %136 to i64
  %189 = shl nuw nsw i64 %188, 16
  %190 = or disjoint i64 %189, %187
  %191 = zext i8 %138 to i64
  %192 = shl nuw nsw i64 %191, 24
  %193 = or disjoint i64 %192, %190
  %194 = zext i8 %140 to i64
  %195 = shl nuw nsw i64 %194, 32
  %196 = or disjoint i64 %195, %193
  %197 = zext i8 %142 to i64
  %198 = shl nuw nsw i64 %197, 40
  %199 = or i64 %198, %196
  %200 = zext i8 %144 to i64
  %201 = shl nuw nsw i64 %200, 48
  %202 = or i64 %201, %199
  %203 = zext i8 %146 to i64
  %204 = shl nuw i64 %203, 56
  %205 = or i64 %204, %202
  %206 = zext i8 %117 to i64
  %207 = zext i8 %119 to i64
  %208 = shl nuw nsw i64 %207, 8
  %209 = or disjoint i64 %208, %206
  %210 = zext i8 %121 to i64
  %211 = shl nuw nsw i64 %210, 16
  %212 = or disjoint i64 %211, %209
  %213 = zext i8 %123 to i64
  %214 = shl nuw nsw i64 %213, 24
  %215 = or disjoint i64 %214, %212
  %216 = zext i8 %125 to i64
  %217 = shl nuw nsw i64 %216, 32
  %218 = or disjoint i64 %217, %215
  %219 = zext i8 %127 to i64
  %220 = shl nuw nsw i64 %219, 40
  %221 = or i64 %220, %218
  %222 = zext i8 %129 to i64
  %223 = shl nuw nsw i64 %222, 48
  %224 = or i64 %223, %221
  %225 = zext i8 %131 to i64
  %226 = shl nuw i64 %225, 56
  %227 = or i64 %226, %224
  br label %228

228:                                              ; preds = %228, %108
  %229 = phi i1 [ false, %108 ], [ true, %228 ]
  %230 = phi i64 [ 0, %108 ], [ 1, %228 ]
  %231 = mul nuw nsw i64 %230, 24
  %232 = getelementptr inbounds nuw i8, ptr %42, i64 %231
  %233 = load i8, ptr %232, align 8, !tbaa !9
  %234 = getelementptr inbounds nuw i8, ptr %232, i64 1
  %235 = load i8, ptr %234, align 1, !tbaa !9
  %236 = getelementptr inbounds nuw i8, ptr %232, i64 2
  %237 = load i8, ptr %236, align 2, !tbaa !9
  %238 = getelementptr inbounds nuw i8, ptr %232, i64 3
  %239 = load i8, ptr %238, align 1, !tbaa !9
  %240 = getelementptr inbounds nuw i8, ptr %232, i64 4
  %241 = load i8, ptr %240, align 4, !tbaa !9
  %242 = getelementptr inbounds nuw i8, ptr %232, i64 5
  %243 = load i8, ptr %242, align 1, !tbaa !9
  %244 = getelementptr inbounds nuw i8, ptr %232, i64 6
  %245 = load i8, ptr %244, align 2, !tbaa !9
  %246 = getelementptr inbounds nuw i8, ptr %232, i64 7
  %247 = load i8, ptr %246, align 1, !tbaa !9
  %248 = getelementptr inbounds nuw i8, ptr %232, i64 8
  %249 = load i8, ptr %248, align 8, !tbaa !9
  %250 = getelementptr inbounds nuw i8, ptr %232, i64 9
  %251 = load i8, ptr %250, align 1, !tbaa !9
  %252 = getelementptr inbounds nuw i8, ptr %232, i64 10
  %253 = load i8, ptr %252, align 2, !tbaa !9
  %254 = getelementptr inbounds nuw i8, ptr %232, i64 11
  %255 = load i8, ptr %254, align 1, !tbaa !9
  %256 = getelementptr inbounds nuw i8, ptr %232, i64 12
  %257 = load i8, ptr %256, align 4, !tbaa !9
  %258 = getelementptr inbounds nuw i8, ptr %232, i64 13
  %259 = load i8, ptr %258, align 1, !tbaa !9
  %260 = getelementptr inbounds nuw i8, ptr %232, i64 14
  %261 = load i8, ptr %260, align 2, !tbaa !9
  %262 = getelementptr inbounds nuw i8, ptr %232, i64 15
  %263 = load i8, ptr %262, align 1, !tbaa !9
  %264 = getelementptr inbounds nuw i8, ptr %232, i64 16
  %265 = load i8, ptr %264, align 8, !tbaa !9
  %266 = getelementptr inbounds nuw i8, ptr %232, i64 17
  %267 = load i8, ptr %266, align 1, !tbaa !9
  %268 = getelementptr inbounds nuw i8, ptr %232, i64 18
  %269 = load i8, ptr %268, align 2, !tbaa !9
  %270 = getelementptr inbounds nuw i8, ptr %232, i64 19
  %271 = load i8, ptr %270, align 1, !tbaa !9
  %272 = getelementptr inbounds nuw i8, ptr %232, i64 20
  %273 = load i8, ptr %272, align 4, !tbaa !9
  %274 = getelementptr inbounds nuw i8, ptr %232, i64 21
  %275 = load i8, ptr %274, align 1, !tbaa !9
  %276 = getelementptr inbounds nuw i8, ptr %232, i64 22
  %277 = load i8, ptr %276, align 2, !tbaa !9
  %278 = getelementptr inbounds nuw i8, ptr %232, i64 23
  %279 = load i8, ptr %278, align 1, !tbaa !9
  %280 = shl nuw nsw i64 %230, 3
  %281 = getelementptr inbounds nuw i8, ptr @__const.main.b, i64 %280
  %282 = load i8, ptr %281, align 8, !tbaa !9
  %283 = zext i8 %282 to i64
  %284 = getelementptr inbounds nuw i8, ptr %281, i64 1
  %285 = load i8, ptr %284, align 1, !tbaa !9
  %286 = zext i8 %285 to i64
  %287 = shl nuw nsw i64 %286, 8
  %288 = or disjoint i64 %287, %283
  %289 = getelementptr inbounds nuw i8, ptr %281, i64 2
  %290 = load i8, ptr %289, align 2, !tbaa !9
  %291 = zext i8 %290 to i64
  %292 = shl nuw nsw i64 %291, 16
  %293 = or disjoint i64 %292, %288
  %294 = getelementptr inbounds nuw i8, ptr %281, i64 3
  %295 = load i8, ptr %294, align 1, !tbaa !9
  %296 = zext i8 %295 to i64
  %297 = shl nuw nsw i64 %296, 24
  %298 = or disjoint i64 %297, %293
  %299 = getelementptr inbounds nuw i8, ptr %281, i64 4
  %300 = load i8, ptr %299, align 4, !tbaa !9
  %301 = zext i8 %300 to i64
  %302 = shl nuw nsw i64 %301, 32
  %303 = or disjoint i64 %302, %298
  %304 = getelementptr inbounds nuw i8, ptr %281, i64 5
  %305 = load i8, ptr %304, align 1, !tbaa !9
  %306 = zext i8 %305 to i64
  %307 = shl nuw nsw i64 %306, 40
  %308 = or i64 %307, %303
  %309 = getelementptr inbounds nuw i8, ptr %281, i64 6
  %310 = load i8, ptr %309, align 2, !tbaa !9
  %311 = zext i8 %310 to i64
  %312 = shl nuw nsw i64 %311, 48
  %313 = or i64 %312, %308
  %314 = getelementptr inbounds nuw i8, ptr %281, i64 7
  %315 = load i8, ptr %314, align 1, !tbaa !9
  %316 = zext i8 %315 to i64
  %317 = shl nuw i64 %316, 56
  %318 = or i64 %317, %313
  %319 = zext i8 %265 to i64
  %320 = zext i8 %267 to i64
  %321 = shl nuw nsw i64 %320, 8
  %322 = or disjoint i64 %321, %319
  %323 = zext i8 %269 to i64
  %324 = shl nuw nsw i64 %323, 16
  %325 = or disjoint i64 %324, %322
  %326 = zext i8 %271 to i64
  %327 = shl nuw nsw i64 %326, 24
  %328 = or disjoint i64 %327, %325
  %329 = zext i8 %273 to i64
  %330 = shl nuw nsw i64 %329, 32
  %331 = or disjoint i64 %330, %328
  %332 = zext i8 %275 to i64
  %333 = shl nuw nsw i64 %332, 40
  %334 = or i64 %333, %331
  %335 = zext i8 %277 to i64
  %336 = shl nuw nsw i64 %335, 48
  %337 = or i64 %336, %334
  %338 = zext i8 %279 to i64
  %339 = shl nuw i64 %338, 56
  %340 = or i64 %339, %337
  %341 = zext i8 %249 to i64
  %342 = zext i8 %251 to i64
  %343 = shl nuw nsw i64 %342, 8
  %344 = or disjoint i64 %343, %341
  %345 = zext i8 %253 to i64
  %346 = shl nuw nsw i64 %345, 16
  %347 = or disjoint i64 %346, %344
  %348 = zext i8 %255 to i64
  %349 = shl nuw nsw i64 %348, 24
  %350 = or disjoint i64 %349, %347
  %351 = zext i8 %257 to i64
  %352 = shl nuw nsw i64 %351, 32
  %353 = or disjoint i64 %352, %350
  %354 = zext i8 %259 to i64
  %355 = shl nuw nsw i64 %354, 40
  %356 = or i64 %355, %353
  %357 = zext i8 %261 to i64
  %358 = shl nuw nsw i64 %357, 48
  %359 = or i64 %358, %356
  %360 = zext i8 %263 to i64
  %361 = shl nuw i64 %360, 56
  %362 = or i64 %361, %359
  %363 = zext i8 %233 to i64
  %364 = zext i8 %235 to i64
  %365 = shl nuw nsw i64 %364, 8
  %366 = or disjoint i64 %365, %363
  %367 = zext i8 %237 to i64
  %368 = shl nuw nsw i64 %367, 16
  %369 = or disjoint i64 %368, %366
  %370 = zext i8 %239 to i64
  %371 = shl nuw nsw i64 %370, 24
  %372 = or disjoint i64 %371, %369
  %373 = zext i8 %241 to i64
  %374 = shl nuw nsw i64 %373, 32
  %375 = or disjoint i64 %374, %372
  %376 = zext i8 %243 to i64
  %377 = shl nuw nsw i64 %376, 40
  %378 = or i64 %377, %375
  %379 = zext i8 %245 to i64
  %380 = shl nuw nsw i64 %379, 48
  %381 = or i64 %380, %378
  %382 = zext i8 %247 to i64
  %383 = shl nuw i64 %382, 56
  %384 = or i64 %383, %381
  %385 = mul nsw i64 %227, %384
  %386 = ashr i64 %385, 16
  %387 = mul nsw i64 %205, %362
  %388 = ashr i64 %387, 16
  %389 = add nsw i64 %388, %386
  %390 = mul nsw i64 %183, %340
  %391 = ashr i64 %390, 16
  %392 = add nsw i64 %389, %391
  %393 = add nsw i64 %392, %318
  %394 = getelementptr inbounds nuw [8 x i8], ptr %114, i64 %230
  store i64 %393, ptr %394, align 8, !tbaa !10
  br i1 %229, label %395, label %228, !llvm.loop !12

395:                                              ; preds = %228
  br i1 %109, label %108, label %396, !llvm.loop !14

396:                                              ; preds = %395
  %397 = load i64, ptr %44, align 16, !tbaa !10
  %398 = icmp eq i64 %397, 65636
  %399 = getelementptr inbounds nuw i8, ptr %44, i64 8
  %400 = load i64, ptr %399, align 8
  %401 = icmp eq i64 %400, 131272
  %402 = select i1 %398, i1 %401, i1 false
  %403 = select i1 %402, ptr @.str.1, ptr @.str.2
  %404 = tail call i32 (ptr, ...) @printf(ptr noundef nonnull dereferenceable(1) @.str.3, ptr noundef nonnull %403)
  call void @llvm.lifetime.start.p0(ptr nonnull %45) #9
  call void @llvm.memcpy.p0.p0.i64(ptr noundef nonnull align 16 dereferenceable(24) %45, ptr noundef nonnull align 16 dereferenceable(24) @__const.main.sx, i64 24, i1 false)
  call void @llvm.lifetime.start.p0(ptr nonnull %46) #9
  call void @llvm.lifetime.start.p0(ptr nonnull %47) #9
  store ptr %45, ptr %47, align 8, !tbaa !15
  %405 = getelementptr inbounds nuw i8, ptr %47, i64 8
  store i64 3, ptr %405, align 8, !tbaa !19
  %406 = getelementptr inbounds nuw i8, ptr %47, i64 16
  store i64 8, ptr %406, align 8, !tbaa !20
  %407 = getelementptr inbounds nuw i8, ptr %47, i64 24
  store i64 8, ptr %407, align 8, !tbaa !21
  call void @llvm.lifetime.start.p0(ptr nonnull %48) #9
  store ptr %46, ptr %48, align 8, !tbaa !15
  %408 = getelementptr inbounds nuw i8, ptr %48, i64 8
  store i64 3, ptr %408, align 8, !tbaa !19
  %409 = getelementptr inbounds nuw i8, ptr %48, i64 16
  store i64 8, ptr %409, align 8, !tbaa !20
  %410 = getelementptr inbounds nuw i8, ptr %48, i64 24
  store i64 8, ptr %410, align 8, !tbaa !21
  call fastcc void @softmax(ptr noundef %47, ptr noundef %48)
  %411 = load i64, ptr %46, align 16, !tbaa !10
  %412 = getelementptr inbounds nuw i8, ptr %46, i64 8
  %413 = load i64, ptr %412, align 8, !tbaa !10
  %414 = add nsw i64 %413, %411
  %415 = getelementptr inbounds nuw i8, ptr %46, i64 16
  %416 = load i64, ptr %415, align 16, !tbaa !10
  %417 = add nsw i64 %416, %414
  %418 = add i64 %417, -65534
  %419 = icmp ult i64 %418, 5
  %420 = select i1 %419, ptr @.str.1, ptr @.str.2
  %421 = call i32 (ptr, ...) @printf(ptr noundef nonnull dereferenceable(1) @.str.4, ptr noundef nonnull %420, i64 noundef %417)
  call void @llvm.lifetime.start.p0(ptr nonnull %49) #9
  call void @llvm.memcpy.p0.p0.i64(ptr noundef nonnull align 16 dereferenceable(24) %49, ptr noundef nonnull align 16 dereferenceable(24) @__const.main.lx, i64 24, i1 false)
  call void @llvm.lifetime.start.p0(ptr nonnull %50) #9
  call void @llvm.memcpy.p0.p0.i64(ptr noundef nonnull align 16 dereferenceable(24) %50, ptr noundef nonnull align 16 dereferenceable(24) @__const.main.lg3, i64 24, i1 false)
  call void @llvm.lifetime.start.p0(ptr nonnull %51) #9
  call void @llvm.memset.p0.i64(ptr noundef nonnull align 16 dereferenceable(24) %51, i8 0, i64 24, i1 false)
  call void @llvm.lifetime.start.p0(ptr nonnull %52) #9
  call void @llvm.lifetime.start.p0(ptr nonnull %53) #9
  store ptr %49, ptr %53, align 8, !tbaa !15
  %422 = getelementptr inbounds nuw i8, ptr %53, i64 8
  store i64 3, ptr %422, align 8, !tbaa !19
  %423 = getelementptr inbounds nuw i8, ptr %53, i64 16
  store i64 8, ptr %423, align 8, !tbaa !20
  %424 = getelementptr inbounds nuw i8, ptr %53, i64 24
  store i64 8, ptr %424, align 8, !tbaa !21
  call void @llvm.lifetime.start.p0(ptr nonnull %54) #9
  store ptr %50, ptr %54, align 8, !tbaa !15
  %425 = getelementptr inbounds nuw i8, ptr %54, i64 8
  store i64 3, ptr %425, align 8, !tbaa !19
  %426 = getelementptr inbounds nuw i8, ptr %54, i64 16
  store i64 8, ptr %426, align 8, !tbaa !20
  %427 = getelementptr inbounds nuw i8, ptr %54, i64 24
  store i64 8, ptr %427, align 8, !tbaa !21
  call void @llvm.lifetime.start.p0(ptr nonnull %55) #9
  store ptr %51, ptr %55, align 8, !tbaa !15
  %428 = getelementptr inbounds nuw i8, ptr %55, i64 8
  store i64 3, ptr %428, align 8, !tbaa !19
  %429 = getelementptr inbounds nuw i8, ptr %55, i64 16
  store i64 8, ptr %429, align 8, !tbaa !20
  %430 = getelementptr inbounds nuw i8, ptr %55, i64 24
  store i64 8, ptr %430, align 8, !tbaa !21
  call void @llvm.lifetime.start.p0(ptr nonnull %56) #9
  store ptr %52, ptr %56, align 8, !tbaa !15
  %431 = getelementptr inbounds nuw i8, ptr %56, i64 8
  store i64 3, ptr %431, align 8, !tbaa !19
  %432 = getelementptr inbounds nuw i8, ptr %56, i64 16
  store i64 8, ptr %432, align 8, !tbaa !20
  %433 = getelementptr inbounds nuw i8, ptr %56, i64 24
  store i64 8, ptr %433, align 8, !tbaa !21
  call fastcc void @layernorm(ptr noundef %53, i64 noundef 3, ptr noundef %54, ptr noundef %55, ptr noundef %56)
  %434 = load i64, ptr %52, align 16, !tbaa !10
  %435 = getelementptr inbounds nuw i8, ptr %52, i64 8
  %436 = load i64, ptr %435, align 8, !tbaa !10
  %437 = add nsw i64 %436, %434
  %438 = getelementptr inbounds nuw i8, ptr %52, i64 16
  %439 = load i64, ptr %438, align 16, !tbaa !10
  %440 = add nsw i64 %439, %437
  %441 = add i64 %440, 9
  %442 = icmp ult i64 %441, 19
  %443 = select i1 %442, ptr @.str.1, ptr @.str.2
  %444 = call i32 (ptr, ...) @printf(ptr noundef nonnull dereferenceable(1) @.str.5, ptr noundef nonnull %443, i64 noundef %440)
  call void @llvm.lifetime.start.p0(ptr nonnull %57) #9
  call void @llvm.lifetime.start.p0(ptr nonnull %58) #9
  call void @llvm.lifetime.start.p0(ptr nonnull %59) #9
  call void @llvm.lifetime.start.p0(ptr nonnull %60) #9
  call void @llvm.lifetime.start.p0(ptr nonnull %61) #9
  call void @llvm.lifetime.start.p0(ptr nonnull %62) #9
  call void @llvm.lifetime.start.p0(ptr nonnull %63) #9
  call void @llvm.lifetime.start.p0(ptr nonnull %64) #9
  call void @llvm.lifetime.start.p0(ptr nonnull %65) #9
  store i64 -12800, ptr %57, align 16, !tbaa !10
  %445 = getelementptr inbounds nuw i8, ptr %57, i64 8
  store i64 -3328, ptr %445, align 8, !tbaa !10
  %446 = getelementptr inbounds nuw i8, ptr %57, i64 16
  store i64 6144, ptr %446, align 16, !tbaa !10
  %447 = getelementptr inbounds nuw i8, ptr %57, i64 24
  store i64 -9984, ptr %447, align 8, !tbaa !10
  %448 = getelementptr inbounds nuw i8, ptr %57, i64 32
  store i64 -512, ptr %448, align 16, !tbaa !10
  %449 = getelementptr inbounds nuw i8, ptr %57, i64 40
  store i64 8960, ptr %449, align 8, !tbaa !10
  %450 = getelementptr inbounds nuw i8, ptr %57, i64 48
  store i64 -7168, ptr %450, align 16, !tbaa !10
  %451 = getelementptr inbounds nuw i8, ptr %57, i64 56
  store i64 2304, ptr %451, align 8, !tbaa !10
  %452 = getelementptr inbounds nuw i8, ptr %57, i64 64
  store i64 11776, ptr %452, align 16, !tbaa !10
  %453 = getelementptr inbounds nuw i8, ptr %57, i64 72
  store i64 -4352, ptr %453, align 8, !tbaa !10
  %454 = getelementptr inbounds nuw i8, ptr %57, i64 80
  store i64 5120, ptr %454, align 16, !tbaa !10
  %455 = getelementptr inbounds nuw i8, ptr %57, i64 88
  store i64 -11008, ptr %455, align 8, !tbaa !10
  br label %456

456:                                              ; preds = %456, %396
  %457 = phi i64 [ 0, %396 ], [ %472, %456 ]
  %458 = phi <2 x i16> [ <i16 0, i16 1>, %396 ], [ %473, %456 ]
  %459 = mul nuw nsw <2 x i16> %458, splat (i16 13)
  %460 = mul <2 x i16> %458, splat (i16 13)
  %461 = add <2 x i16> %460, splat (i16 26)
  %462 = urem <2 x i16> %459, splat (i16 200)
  %463 = urem <2 x i16> %461, splat (i16 200)
  %464 = shl nuw nsw <2 x i16> %462, splat (i16 7)
  %465 = shl nuw nsw <2 x i16> %463, splat (i16 7)
  %466 = zext nneg <2 x i16> %464 to <2 x i64>
  %467 = zext nneg <2 x i16> %465 to <2 x i64>
  %468 = add nsw <2 x i64> %466, splat (i64 -12800)
  %469 = add nsw <2 x i64> %467, splat (i64 -12800)
  %470 = getelementptr inbounds nuw [8 x i8], ptr %58, i64 %457
  %471 = getelementptr inbounds nuw i8, ptr %470, i64 16
  store <2 x i64> %468, ptr %470, align 16, !tbaa !10
  store <2 x i64> %469, ptr %471, align 16, !tbaa !10
  %472 = add nuw i64 %457, 4
  %473 = add <2 x i16> %458, splat (i16 4)
  %474 = icmp eq i64 %472, 48
  br i1 %474, label %475, label %456, !llvm.loop !22

475:                                              ; preds = %456
  store i64 -1600, ptr %59, align 16, !tbaa !10
  %476 = getelementptr inbounds nuw i8, ptr %59, i64 8
  store i64 -1152, ptr %476, align 8, !tbaa !10
  %477 = getelementptr inbounds nuw i8, ptr %59, i64 16
  store i64 -704, ptr %477, align 16, !tbaa !10
  %478 = getelementptr inbounds nuw i8, ptr %59, i64 24
  store i64 -256, ptr %478, align 8, !tbaa !10
  %479 = getelementptr inbounds nuw i8, ptr %59, i64 32
  store i64 192, ptr %479, align 16, !tbaa !10
  %480 = getelementptr inbounds nuw i8, ptr %59, i64 40
  store i64 640, ptr %480, align 8, !tbaa !10
  %481 = getelementptr inbounds nuw i8, ptr %59, i64 48
  store i64 1088, ptr %481, align 16, !tbaa !10
  %482 = getelementptr inbounds nuw i8, ptr %59, i64 56
  store i64 1536, ptr %482, align 8, !tbaa !10
  %483 = getelementptr inbounds nuw i8, ptr %59, i64 64
  store i64 -1216, ptr %483, align 16, !tbaa !10
  %484 = getelementptr inbounds nuw i8, ptr %59, i64 72
  store i64 -768, ptr %484, align 8, !tbaa !10
  %485 = getelementptr inbounds nuw i8, ptr %59, i64 80
  store i64 -320, ptr %485, align 16, !tbaa !10
  %486 = getelementptr inbounds nuw i8, ptr %59, i64 88
  store i64 128, ptr %486, align 8, !tbaa !10
  store i64 -12800, ptr %60, align 16, !tbaa !10
  %487 = getelementptr inbounds nuw i8, ptr %60, i64 8
  store i64 -11392, ptr %487, align 8, !tbaa !10
  %488 = getelementptr inbounds nuw i8, ptr %60, i64 16
  store i64 -9984, ptr %488, align 16, !tbaa !10
  %489 = getelementptr inbounds nuw i8, ptr %60, i64 24
  store i64 -8576, ptr %489, align 8, !tbaa !10
  %490 = getelementptr inbounds nuw i8, ptr %60, i64 32
  store i64 -7168, ptr %490, align 16, !tbaa !10
  %491 = getelementptr inbounds nuw i8, ptr %60, i64 40
  store i64 -5760, ptr %491, align 8, !tbaa !10
  %492 = getelementptr inbounds nuw i8, ptr %60, i64 48
  store i64 -4352, ptr %492, align 16, !tbaa !10
  %493 = getelementptr inbounds nuw i8, ptr %60, i64 56
  store i64 -2944, ptr %493, align 8, !tbaa !10
  %494 = getelementptr inbounds nuw i8, ptr %60, i64 64
  store i64 -1536, ptr %494, align 16, !tbaa !10
  %495 = getelementptr inbounds nuw i8, ptr %60, i64 72
  store i64 -128, ptr %495, align 8, !tbaa !10
  %496 = getelementptr inbounds nuw i8, ptr %60, i64 80
  store i64 1280, ptr %496, align 16, !tbaa !10
  %497 = getelementptr inbounds nuw i8, ptr %60, i64 88
  store i64 2688, ptr %497, align 8, !tbaa !10
  %498 = getelementptr inbounds nuw i8, ptr %60, i64 96
  store i64 4096, ptr %498, align 16, !tbaa !10
  %499 = getelementptr inbounds nuw i8, ptr %60, i64 104
  store i64 5504, ptr %499, align 8, !tbaa !10
  %500 = getelementptr inbounds nuw i8, ptr %60, i64 112
  store i64 6912, ptr %500, align 16, !tbaa !10
  %501 = getelementptr inbounds nuw i8, ptr %60, i64 120
  store i64 8320, ptr %501, align 8, !tbaa !10
  call void @llvm.memset.p0.i64(ptr noundef nonnull align 16 dereferenceable(32) %63, i8 0, i64 32, i1 false), !tbaa !10
  store i64 0, ptr %61, align 16, !tbaa !10
  %502 = getelementptr inbounds nuw i8, ptr %61, i64 8
  store i64 10, ptr %502, align 8, !tbaa !10
  %503 = getelementptr inbounds nuw i8, ptr %61, i64 16
  store i64 20, ptr %503, align 16, !tbaa !10
  %504 = getelementptr inbounds nuw i8, ptr %61, i64 24
  store i64 30, ptr %504, align 8, !tbaa !10
  store <4 x i64> splat (i64 65536), ptr %62, align 16, !tbaa !10
  call void @llvm.lifetime.start.p0(ptr nonnull %66) #9
  store ptr %62, ptr %66, align 8, !tbaa !15
  %505 = getelementptr inbounds nuw i8, ptr %66, i64 8
  store i64 4, ptr %505, align 8, !tbaa !19
  %506 = getelementptr inbounds nuw i8, ptr %66, i64 16
  store i64 8, ptr %506, align 8, !tbaa !20
  %507 = getelementptr inbounds nuw i8, ptr %66, i64 24
  store i64 8, ptr %507, align 8, !tbaa !21
  call void @llvm.lifetime.start.p0(ptr nonnull %67) #9
  store ptr %63, ptr %67, align 8, !tbaa !15
  %508 = getelementptr inbounds nuw i8, ptr %67, i64 8
  store i64 4, ptr %508, align 8, !tbaa !19
  %509 = getelementptr inbounds nuw i8, ptr %67, i64 16
  store i64 8, ptr %509, align 8, !tbaa !20
  %510 = getelementptr inbounds nuw i8, ptr %67, i64 24
  store i64 8, ptr %510, align 8, !tbaa !21
  call void @llvm.lifetime.start.p0(ptr nonnull %27) #9
  call void @llvm.lifetime.start.p0(ptr nonnull %28) #9
  call void @llvm.lifetime.start.p0(ptr nonnull %29) #9
  call void @llvm.lifetime.start.p0(ptr nonnull %30) #9
  call void @llvm.lifetime.start.p0(ptr nonnull %31) #9
  call void @llvm.lifetime.start.p0(ptr nonnull %32) #9
  %511 = getelementptr inbounds nuw i8, ptr %58, i64 128
  %512 = getelementptr inbounds nuw i8, ptr %58, i64 256
  br label %570

513:                                              ; preds = %1622
  %514 = getelementptr inbounds nuw i8, ptr %38, i64 8
  %515 = getelementptr inbounds nuw i8, ptr %38, i64 16
  %516 = getelementptr inbounds nuw i8, ptr %38, i64 24
  %517 = getelementptr inbounds nuw i8, ptr %39, i64 8
  %518 = getelementptr inbounds nuw i8, ptr %39, i64 16
  %519 = getelementptr inbounds nuw i8, ptr %39, i64 24
  %520 = load i64, ptr %29, align 16, !tbaa !10
  %521 = getelementptr inbounds nuw i8, ptr %29, i64 32
  %522 = load i64, ptr %521, align 16, !tbaa !10
  %523 = getelementptr inbounds nuw i8, ptr %29, i64 64
  %524 = load i64, ptr %523, align 16, !tbaa !10
  %525 = load i64, ptr %28, align 16, !tbaa !10
  %526 = getelementptr inbounds nuw i8, ptr %28, i64 8
  %527 = load i64, ptr %526, align 8, !tbaa !10
  %528 = getelementptr inbounds nuw i8, ptr %28, i64 16
  %529 = load i64, ptr %528, align 16, !tbaa !10
  %530 = getelementptr inbounds nuw i8, ptr %28, i64 24
  %531 = load i64, ptr %530, align 8, !tbaa !10
  %532 = getelementptr inbounds nuw i8, ptr %28, i64 32
  %533 = load i64, ptr %532, align 16, !tbaa !10
  %534 = getelementptr inbounds nuw i8, ptr %28, i64 40
  %535 = load i64, ptr %534, align 8, !tbaa !10
  %536 = getelementptr inbounds nuw i8, ptr %28, i64 48
  %537 = load i64, ptr %536, align 16, !tbaa !10
  %538 = getelementptr inbounds nuw i8, ptr %28, i64 56
  %539 = load i64, ptr %538, align 8, !tbaa !10
  %540 = getelementptr inbounds nuw i8, ptr %36, i64 8
  %541 = getelementptr inbounds nuw i8, ptr %28, i64 64
  %542 = load i64, ptr %541, align 16, !tbaa !10
  %543 = getelementptr inbounds nuw i8, ptr %28, i64 72
  %544 = load i64, ptr %543, align 8, !tbaa !10
  %545 = getelementptr inbounds nuw i8, ptr %28, i64 80
  %546 = load i64, ptr %545, align 16, !tbaa !10
  %547 = getelementptr inbounds nuw i8, ptr %28, i64 88
  %548 = load i64, ptr %547, align 8, !tbaa !10
  %549 = getelementptr inbounds nuw i8, ptr %36, i64 16
  %550 = getelementptr inbounds nuw i8, ptr %37, i64 8
  %551 = getelementptr inbounds nuw i8, ptr %37, i64 16
  %552 = getelementptr inbounds nuw i8, ptr %29, i64 8
  %553 = load i64, ptr %552, align 8
  %554 = getelementptr inbounds nuw i8, ptr %29, i64 40
  %555 = load i64, ptr %554, align 8
  %556 = getelementptr inbounds nuw i8, ptr %29, i64 72
  %557 = load i64, ptr %556, align 8
  %558 = getelementptr inbounds nuw i8, ptr %29, i64 16
  %559 = load i64, ptr %558, align 16
  %560 = getelementptr inbounds nuw i8, ptr %29, i64 48
  %561 = load i64, ptr %560, align 16
  %562 = getelementptr inbounds nuw i8, ptr %29, i64 80
  %563 = load i64, ptr %562, align 16
  %564 = getelementptr inbounds nuw i8, ptr %29, i64 24
  %565 = load i64, ptr %564, align 8
  %566 = getelementptr inbounds nuw i8, ptr %29, i64 56
  %567 = load i64, ptr %566, align 8
  %568 = getelementptr inbounds nuw i8, ptr %29, i64 88
  %569 = load i64, ptr %568, align 8
  br label %1635

570:                                              ; preds = %1622, %475
  %571 = phi i64 [ 0, %475 ], [ %1626, %1622 ]
  %572 = shl nuw nsw i64 %571, 5
  %573 = getelementptr inbounds nuw i8, ptr %57, i64 %572
  call void @llvm.lifetime.start.p0(ptr nonnull %33) #9
  call void @llvm.lifetime.start.p0(ptr nonnull %34) #9
  call void @llvm.lifetime.start.p0(ptr nonnull %35) #9
  %574 = getelementptr inbounds nuw i8, ptr %573, i64 8
  %575 = getelementptr inbounds nuw i8, ptr %573, i64 16
  %576 = getelementptr inbounds nuw i8, ptr %573, i64 24
  %577 = load i8, ptr %573, align 16, !tbaa !9
  %578 = getelementptr inbounds nuw i8, ptr %573, i64 1
  %579 = load i8, ptr %578, align 1, !tbaa !9
  %580 = getelementptr inbounds nuw i8, ptr %573, i64 2
  %581 = load i8, ptr %580, align 2, !tbaa !9
  %582 = getelementptr inbounds nuw i8, ptr %573, i64 3
  %583 = load i8, ptr %582, align 1, !tbaa !9
  %584 = getelementptr inbounds nuw i8, ptr %573, i64 4
  %585 = load i8, ptr %584, align 4, !tbaa !9
  %586 = getelementptr inbounds nuw i8, ptr %573, i64 5
  %587 = load i8, ptr %586, align 1, !tbaa !9
  %588 = getelementptr inbounds nuw i8, ptr %573, i64 6
  %589 = load i8, ptr %588, align 2, !tbaa !9
  %590 = getelementptr inbounds nuw i8, ptr %573, i64 7
  %591 = load i8, ptr %590, align 1, !tbaa !9
  %592 = load i8, ptr %574, align 8, !tbaa !9
  %593 = getelementptr inbounds nuw i8, ptr %573, i64 9
  %594 = load i8, ptr %593, align 1, !tbaa !9
  %595 = getelementptr inbounds nuw i8, ptr %573, i64 10
  %596 = load i8, ptr %595, align 2, !tbaa !9
  %597 = getelementptr inbounds nuw i8, ptr %573, i64 11
  %598 = load i8, ptr %597, align 1, !tbaa !9
  %599 = getelementptr inbounds nuw i8, ptr %573, i64 12
  %600 = load i8, ptr %599, align 4, !tbaa !9
  %601 = getelementptr inbounds nuw i8, ptr %573, i64 13
  %602 = load i8, ptr %601, align 1, !tbaa !9
  %603 = getelementptr inbounds nuw i8, ptr %573, i64 14
  %604 = load i8, ptr %603, align 2, !tbaa !9
  %605 = getelementptr inbounds nuw i8, ptr %573, i64 15
  %606 = load i8, ptr %605, align 1, !tbaa !9
  %607 = load i8, ptr %575, align 16, !tbaa !9
  %608 = getelementptr inbounds nuw i8, ptr %573, i64 17
  %609 = load i8, ptr %608, align 1, !tbaa !9
  %610 = getelementptr inbounds nuw i8, ptr %573, i64 18
  %611 = load i8, ptr %610, align 2, !tbaa !9
  %612 = getelementptr inbounds nuw i8, ptr %573, i64 19
  %613 = load i8, ptr %612, align 1, !tbaa !9
  %614 = getelementptr inbounds nuw i8, ptr %573, i64 20
  %615 = load i8, ptr %614, align 4, !tbaa !9
  %616 = getelementptr inbounds nuw i8, ptr %573, i64 21
  %617 = load i8, ptr %616, align 1, !tbaa !9
  %618 = getelementptr inbounds nuw i8, ptr %573, i64 22
  %619 = load i8, ptr %618, align 2, !tbaa !9
  %620 = getelementptr inbounds nuw i8, ptr %573, i64 23
  %621 = load i8, ptr %620, align 1, !tbaa !9
  %622 = load i8, ptr %576, align 8, !tbaa !9
  %623 = getelementptr inbounds nuw i8, ptr %573, i64 25
  %624 = load i8, ptr %623, align 1, !tbaa !9
  %625 = getelementptr inbounds nuw i8, ptr %573, i64 26
  %626 = load i8, ptr %625, align 2, !tbaa !9
  %627 = getelementptr inbounds nuw i8, ptr %573, i64 27
  %628 = load i8, ptr %627, align 1, !tbaa !9
  %629 = getelementptr inbounds nuw i8, ptr %573, i64 28
  %630 = load i8, ptr %629, align 4, !tbaa !9
  %631 = getelementptr inbounds nuw i8, ptr %573, i64 29
  %632 = load i8, ptr %631, align 1, !tbaa !9
  %633 = getelementptr inbounds nuw i8, ptr %573, i64 30
  %634 = load i8, ptr %633, align 2, !tbaa !9
  %635 = getelementptr inbounds nuw i8, ptr %573, i64 31
  %636 = load i8, ptr %635, align 1, !tbaa !9
  %637 = zext i8 %622 to i64
  %638 = zext i8 %624 to i64
  %639 = shl nuw nsw i64 %638, 8
  %640 = or disjoint i64 %639, %637
  %641 = zext i8 %626 to i64
  %642 = shl nuw nsw i64 %641, 16
  %643 = or disjoint i64 %642, %640
  %644 = zext i8 %628 to i64
  %645 = shl nuw nsw i64 %644, 24
  %646 = or disjoint i64 %645, %643
  %647 = zext i8 %630 to i64
  %648 = shl nuw nsw i64 %647, 32
  %649 = or disjoint i64 %648, %646
  %650 = zext i8 %632 to i64
  %651 = shl nuw nsw i64 %650, 40
  %652 = or i64 %651, %649
  %653 = zext i8 %634 to i64
  %654 = shl nuw nsw i64 %653, 48
  %655 = or i64 %654, %652
  %656 = zext i8 %636 to i64
  %657 = shl nuw i64 %656, 56
  %658 = or i64 %657, %655
  %659 = zext i8 %607 to i64
  %660 = zext i8 %609 to i64
  %661 = shl nuw nsw i64 %660, 8
  %662 = or disjoint i64 %661, %659
  %663 = zext i8 %611 to i64
  %664 = shl nuw nsw i64 %663, 16
  %665 = or disjoint i64 %664, %662
  %666 = zext i8 %613 to i64
  %667 = shl nuw nsw i64 %666, 24
  %668 = or disjoint i64 %667, %665
  %669 = zext i8 %615 to i64
  %670 = shl nuw nsw i64 %669, 32
  %671 = or disjoint i64 %670, %668
  %672 = zext i8 %617 to i64
  %673 = shl nuw nsw i64 %672, 40
  %674 = or i64 %673, %671
  %675 = zext i8 %619 to i64
  %676 = shl nuw nsw i64 %675, 48
  %677 = or i64 %676, %674
  %678 = zext i8 %621 to i64
  %679 = shl nuw i64 %678, 56
  %680 = or i64 %679, %677
  %681 = zext i8 %592 to i64
  %682 = zext i8 %594 to i64
  %683 = shl nuw nsw i64 %682, 8
  %684 = or disjoint i64 %683, %681
  %685 = zext i8 %596 to i64
  %686 = shl nuw nsw i64 %685, 16
  %687 = or disjoint i64 %686, %684
  %688 = zext i8 %598 to i64
  %689 = shl nuw nsw i64 %688, 24
  %690 = or disjoint i64 %689, %687
  %691 = zext i8 %600 to i64
  %692 = shl nuw nsw i64 %691, 32
  %693 = or disjoint i64 %692, %690
  %694 = zext i8 %602 to i64
  %695 = shl nuw nsw i64 %694, 40
  %696 = or i64 %695, %693
  %697 = zext i8 %604 to i64
  %698 = shl nuw nsw i64 %697, 48
  %699 = or i64 %698, %696
  %700 = zext i8 %606 to i64
  %701 = shl nuw i64 %700, 56
  %702 = or i64 %701, %699
  %703 = zext i8 %577 to i64
  %704 = zext i8 %579 to i64
  %705 = shl nuw nsw i64 %704, 8
  %706 = or disjoint i64 %705, %703
  %707 = zext i8 %581 to i64
  %708 = shl nuw nsw i64 %707, 16
  %709 = or disjoint i64 %708, %706
  %710 = zext i8 %583 to i64
  %711 = shl nuw nsw i64 %710, 24
  %712 = or disjoint i64 %711, %709
  %713 = zext i8 %585 to i64
  %714 = shl nuw nsw i64 %713, 32
  %715 = or disjoint i64 %714, %712
  %716 = zext i8 %587 to i64
  %717 = shl nuw nsw i64 %716, 40
  %718 = or i64 %717, %715
  %719 = zext i8 %589 to i64
  %720 = shl nuw nsw i64 %719, 48
  %721 = or i64 %720, %718
  %722 = zext i8 %591 to i64
  %723 = shl nuw i64 %722, 56
  %724 = or i64 %723, %721
  br label %725

725:                                              ; preds = %725, %570
  %726 = phi i64 [ 0, %570 ], [ %932, %725 ]
  %727 = shl i64 %726, 5
  %728 = getelementptr i8, ptr %58, i64 %727
  %729 = load i8, ptr %728, align 16, !tbaa !9
  %730 = getelementptr inbounds nuw i8, ptr %728, i64 1
  %731 = load i8, ptr %730, align 1, !tbaa !9
  %732 = getelementptr inbounds nuw i8, ptr %728, i64 2
  %733 = load i8, ptr %732, align 2, !tbaa !9
  %734 = getelementptr inbounds nuw i8, ptr %728, i64 3
  %735 = load i8, ptr %734, align 1, !tbaa !9
  %736 = getelementptr inbounds nuw i8, ptr %728, i64 4
  %737 = load i8, ptr %736, align 4, !tbaa !9
  %738 = getelementptr inbounds nuw i8, ptr %728, i64 5
  %739 = load i8, ptr %738, align 1, !tbaa !9
  %740 = getelementptr inbounds nuw i8, ptr %728, i64 6
  %741 = load i8, ptr %740, align 2, !tbaa !9
  %742 = getelementptr inbounds nuw i8, ptr %728, i64 7
  %743 = load i8, ptr %742, align 1, !tbaa !9
  %744 = getelementptr i8, ptr %728, i64 8
  %745 = load i8, ptr %744, align 8, !tbaa !9
  %746 = getelementptr i8, ptr %728, i64 9
  %747 = load i8, ptr %746, align 1, !tbaa !9
  %748 = getelementptr i8, ptr %728, i64 10
  %749 = load i8, ptr %748, align 2, !tbaa !9
  %750 = getelementptr i8, ptr %728, i64 11
  %751 = load i8, ptr %750, align 1, !tbaa !9
  %752 = getelementptr i8, ptr %728, i64 12
  %753 = load i8, ptr %752, align 4, !tbaa !9
  %754 = getelementptr i8, ptr %728, i64 13
  %755 = load i8, ptr %754, align 1, !tbaa !9
  %756 = getelementptr i8, ptr %728, i64 14
  %757 = load i8, ptr %756, align 2, !tbaa !9
  %758 = getelementptr i8, ptr %728, i64 15
  %759 = load i8, ptr %758, align 1, !tbaa !9
  %760 = getelementptr i8, ptr %728, i64 16
  %761 = load i8, ptr %760, align 16, !tbaa !9
  %762 = getelementptr i8, ptr %728, i64 17
  %763 = load i8, ptr %762, align 1, !tbaa !9
  %764 = getelementptr i8, ptr %728, i64 18
  %765 = load i8, ptr %764, align 2, !tbaa !9
  %766 = getelementptr i8, ptr %728, i64 19
  %767 = load i8, ptr %766, align 1, !tbaa !9
  %768 = getelementptr i8, ptr %728, i64 20
  %769 = load i8, ptr %768, align 4, !tbaa !9
  %770 = getelementptr i8, ptr %728, i64 21
  %771 = load i8, ptr %770, align 1, !tbaa !9
  %772 = getelementptr i8, ptr %728, i64 22
  %773 = load i8, ptr %772, align 2, !tbaa !9
  %774 = getelementptr i8, ptr %728, i64 23
  %775 = load i8, ptr %774, align 1, !tbaa !9
  %776 = getelementptr i8, ptr %728, i64 24
  %777 = load i8, ptr %776, align 8, !tbaa !9
  %778 = getelementptr i8, ptr %728, i64 25
  %779 = load i8, ptr %778, align 1, !tbaa !9
  %780 = getelementptr i8, ptr %728, i64 26
  %781 = load i8, ptr %780, align 2, !tbaa !9
  %782 = getelementptr i8, ptr %728, i64 27
  %783 = load i8, ptr %782, align 1, !tbaa !9
  %784 = getelementptr i8, ptr %728, i64 28
  %785 = load i8, ptr %784, align 4, !tbaa !9
  %786 = getelementptr i8, ptr %728, i64 29
  %787 = load i8, ptr %786, align 1, !tbaa !9
  %788 = getelementptr i8, ptr %728, i64 30
  %789 = load i8, ptr %788, align 2, !tbaa !9
  %790 = getelementptr i8, ptr %728, i64 31
  %791 = load i8, ptr %790, align 1, !tbaa !9
  %792 = shl nsw i64 %726, 3
  %793 = getelementptr inbounds nuw i8, ptr %59, i64 %792
  %794 = load i8, ptr %793, align 8, !tbaa !9
  %795 = zext i8 %794 to i64
  %796 = getelementptr inbounds nuw i8, ptr %793, i64 1
  %797 = load i8, ptr %796, align 1, !tbaa !9
  %798 = zext i8 %797 to i64
  %799 = shl nuw nsw i64 %798, 8
  %800 = or disjoint i64 %799, %795
  %801 = getelementptr inbounds nuw i8, ptr %793, i64 2
  %802 = load i8, ptr %801, align 2, !tbaa !9
  %803 = zext i8 %802 to i64
  %804 = shl nuw nsw i64 %803, 16
  %805 = or disjoint i64 %804, %800
  %806 = getelementptr inbounds nuw i8, ptr %793, i64 3
  %807 = load i8, ptr %806, align 1, !tbaa !9
  %808 = zext i8 %807 to i64
  %809 = shl nuw nsw i64 %808, 24
  %810 = or disjoint i64 %809, %805
  %811 = getelementptr inbounds nuw i8, ptr %793, i64 4
  %812 = load i8, ptr %811, align 4, !tbaa !9
  %813 = zext i8 %812 to i64
  %814 = shl nuw nsw i64 %813, 32
  %815 = or disjoint i64 %814, %810
  %816 = getelementptr inbounds nuw i8, ptr %793, i64 5
  %817 = load i8, ptr %816, align 1, !tbaa !9
  %818 = zext i8 %817 to i64
  %819 = shl nuw nsw i64 %818, 40
  %820 = or i64 %819, %815
  %821 = getelementptr inbounds nuw i8, ptr %793, i64 6
  %822 = load i8, ptr %821, align 2, !tbaa !9
  %823 = zext i8 %822 to i64
  %824 = shl nuw nsw i64 %823, 48
  %825 = or i64 %824, %820
  %826 = getelementptr inbounds nuw i8, ptr %793, i64 7
  %827 = load i8, ptr %826, align 1, !tbaa !9
  %828 = zext i8 %827 to i64
  %829 = shl nuw i64 %828, 56
  %830 = or i64 %829, %825
  %831 = zext i8 %777 to i64
  %832 = zext i8 %779 to i64
  %833 = shl nuw nsw i64 %832, 8
  %834 = or disjoint i64 %833, %831
  %835 = zext i8 %781 to i64
  %836 = shl nuw nsw i64 %835, 16
  %837 = or disjoint i64 %836, %834
  %838 = zext i8 %783 to i64
  %839 = shl nuw nsw i64 %838, 24
  %840 = or disjoint i64 %839, %837
  %841 = zext i8 %785 to i64
  %842 = shl nuw nsw i64 %841, 32
  %843 = or disjoint i64 %842, %840
  %844 = zext i8 %787 to i64
  %845 = shl nuw nsw i64 %844, 40
  %846 = or i64 %845, %843
  %847 = zext i8 %789 to i64
  %848 = shl nuw nsw i64 %847, 48
  %849 = or i64 %848, %846
  %850 = zext i8 %791 to i64
  %851 = shl nuw i64 %850, 56
  %852 = or i64 %851, %849
  %853 = zext i8 %761 to i64
  %854 = zext i8 %763 to i64
  %855 = shl nuw nsw i64 %854, 8
  %856 = or disjoint i64 %855, %853
  %857 = zext i8 %765 to i64
  %858 = shl nuw nsw i64 %857, 16
  %859 = or disjoint i64 %858, %856
  %860 = zext i8 %767 to i64
  %861 = shl nuw nsw i64 %860, 24
  %862 = or disjoint i64 %861, %859
  %863 = zext i8 %769 to i64
  %864 = shl nuw nsw i64 %863, 32
  %865 = or disjoint i64 %864, %862
  %866 = zext i8 %771 to i64
  %867 = shl nuw nsw i64 %866, 40
  %868 = or i64 %867, %865
  %869 = zext i8 %773 to i64
  %870 = shl nuw nsw i64 %869, 48
  %871 = or i64 %870, %868
  %872 = zext i8 %775 to i64
  %873 = shl nuw i64 %872, 56
  %874 = or i64 %873, %871
  %875 = zext i8 %745 to i64
  %876 = zext i8 %747 to i64
  %877 = shl nuw nsw i64 %876, 8
  %878 = or disjoint i64 %877, %875
  %879 = zext i8 %749 to i64
  %880 = shl nuw nsw i64 %879, 16
  %881 = or disjoint i64 %880, %878
  %882 = zext i8 %751 to i64
  %883 = shl nuw nsw i64 %882, 24
  %884 = or disjoint i64 %883, %881
  %885 = zext i8 %753 to i64
  %886 = shl nuw nsw i64 %885, 32
  %887 = or disjoint i64 %886, %884
  %888 = zext i8 %755 to i64
  %889 = shl nuw nsw i64 %888, 40
  %890 = or i64 %889, %887
  %891 = zext i8 %757 to i64
  %892 = shl nuw nsw i64 %891, 48
  %893 = or i64 %892, %890
  %894 = zext i8 %759 to i64
  %895 = shl nuw i64 %894, 56
  %896 = or i64 %895, %893
  %897 = zext i8 %729 to i64
  %898 = zext i8 %731 to i64
  %899 = shl nuw nsw i64 %898, 8
  %900 = or disjoint i64 %899, %897
  %901 = zext i8 %733 to i64
  %902 = shl nuw nsw i64 %901, 16
  %903 = or disjoint i64 %902, %900
  %904 = zext i8 %735 to i64
  %905 = shl nuw nsw i64 %904, 24
  %906 = or disjoint i64 %905, %903
  %907 = zext i8 %737 to i64
  %908 = shl nuw nsw i64 %907, 32
  %909 = or disjoint i64 %908, %906
  %910 = zext i8 %739 to i64
  %911 = shl nuw nsw i64 %910, 40
  %912 = or i64 %911, %909
  %913 = zext i8 %741 to i64
  %914 = shl nuw nsw i64 %913, 48
  %915 = or i64 %914, %912
  %916 = zext i8 %743 to i64
  %917 = shl nuw i64 %916, 56
  %918 = or i64 %917, %915
  %919 = mul nsw i64 %724, %918
  %920 = ashr i64 %919, 16
  %921 = mul nsw i64 %702, %896
  %922 = ashr i64 %921, 16
  %923 = add nsw i64 %922, %920
  %924 = mul nsw i64 %680, %874
  %925 = ashr i64 %924, 16
  %926 = add nsw i64 %923, %925
  %927 = mul nsw i64 %658, %852
  %928 = ashr i64 %927, 16
  %929 = add nsw i64 %926, %928
  %930 = add nsw i64 %929, %830
  %931 = getelementptr inbounds nuw [8 x i8], ptr %33, i64 %726
  store i64 %930, ptr %931, align 8, !tbaa !10
  %932 = add nuw nsw i64 %726, 1
  %933 = icmp eq i64 %932, 4
  br i1 %933, label %934, label %725, !llvm.loop !12

934:                                              ; preds = %725
  %935 = getelementptr inbounds nuw i8, ptr %573, i64 1
  %936 = getelementptr inbounds nuw i8, ptr %573, i64 2
  %937 = getelementptr inbounds nuw i8, ptr %573, i64 3
  %938 = getelementptr inbounds nuw i8, ptr %573, i64 4
  %939 = getelementptr inbounds nuw i8, ptr %573, i64 5
  %940 = getelementptr inbounds nuw i8, ptr %573, i64 6
  %941 = getelementptr inbounds nuw i8, ptr %573, i64 7
  %942 = getelementptr inbounds nuw i8, ptr %573, i64 9
  %943 = getelementptr inbounds nuw i8, ptr %573, i64 10
  %944 = getelementptr inbounds nuw i8, ptr %573, i64 11
  %945 = getelementptr inbounds nuw i8, ptr %573, i64 12
  %946 = getelementptr inbounds nuw i8, ptr %573, i64 13
  %947 = getelementptr inbounds nuw i8, ptr %573, i64 14
  %948 = getelementptr inbounds nuw i8, ptr %573, i64 15
  %949 = getelementptr inbounds nuw i8, ptr %573, i64 17
  %950 = getelementptr inbounds nuw i8, ptr %573, i64 18
  %951 = getelementptr inbounds nuw i8, ptr %573, i64 19
  %952 = getelementptr inbounds nuw i8, ptr %573, i64 20
  %953 = getelementptr inbounds nuw i8, ptr %573, i64 21
  %954 = getelementptr inbounds nuw i8, ptr %573, i64 22
  %955 = getelementptr inbounds nuw i8, ptr %573, i64 23
  %956 = getelementptr inbounds nuw i8, ptr %573, i64 25
  %957 = getelementptr inbounds nuw i8, ptr %573, i64 26
  %958 = getelementptr inbounds nuw i8, ptr %573, i64 27
  %959 = getelementptr inbounds nuw i8, ptr %573, i64 28
  %960 = getelementptr inbounds nuw i8, ptr %573, i64 29
  %961 = getelementptr inbounds nuw i8, ptr %573, i64 30
  %962 = getelementptr inbounds nuw i8, ptr %573, i64 31
  %963 = load i8, ptr %573, align 16, !tbaa !9
  %964 = load i8, ptr %935, align 1, !tbaa !9
  %965 = load i8, ptr %936, align 2, !tbaa !9
  %966 = load i8, ptr %937, align 1, !tbaa !9
  %967 = load i8, ptr %938, align 4, !tbaa !9
  %968 = load i8, ptr %939, align 1, !tbaa !9
  %969 = load i8, ptr %940, align 2, !tbaa !9
  %970 = load i8, ptr %941, align 1, !tbaa !9
  %971 = load i8, ptr %574, align 8, !tbaa !9
  %972 = load i8, ptr %942, align 1, !tbaa !9
  %973 = load i8, ptr %943, align 2, !tbaa !9
  %974 = load i8, ptr %944, align 1, !tbaa !9
  %975 = load i8, ptr %945, align 4, !tbaa !9
  %976 = load i8, ptr %946, align 1, !tbaa !9
  %977 = load i8, ptr %947, align 2, !tbaa !9
  %978 = load i8, ptr %948, align 1, !tbaa !9
  %979 = load i8, ptr %575, align 16, !tbaa !9
  %980 = load i8, ptr %949, align 1, !tbaa !9
  %981 = load i8, ptr %950, align 2, !tbaa !9
  %982 = load i8, ptr %951, align 1, !tbaa !9
  %983 = load i8, ptr %952, align 4, !tbaa !9
  %984 = load i8, ptr %953, align 1, !tbaa !9
  %985 = load i8, ptr %954, align 2, !tbaa !9
  %986 = load i8, ptr %955, align 1, !tbaa !9
  %987 = load i8, ptr %576, align 8, !tbaa !9
  %988 = load i8, ptr %956, align 1, !tbaa !9
  %989 = load i8, ptr %957, align 2, !tbaa !9
  %990 = load i8, ptr %958, align 1, !tbaa !9
  %991 = load i8, ptr %959, align 4, !tbaa !9
  %992 = load i8, ptr %960, align 1, !tbaa !9
  %993 = load i8, ptr %961, align 2, !tbaa !9
  %994 = load i8, ptr %962, align 1, !tbaa !9
  %995 = zext i8 %987 to i64
  %996 = zext i8 %988 to i64
  %997 = shl nuw nsw i64 %996, 8
  %998 = or disjoint i64 %997, %995
  %999 = zext i8 %989 to i64
  %1000 = shl nuw nsw i64 %999, 16
  %1001 = or disjoint i64 %1000, %998
  %1002 = zext i8 %990 to i64
  %1003 = shl nuw nsw i64 %1002, 24
  %1004 = or disjoint i64 %1003, %1001
  %1005 = zext i8 %991 to i64
  %1006 = shl nuw nsw i64 %1005, 32
  %1007 = or disjoint i64 %1006, %1004
  %1008 = zext i8 %992 to i64
  %1009 = shl nuw nsw i64 %1008, 40
  %1010 = or i64 %1009, %1007
  %1011 = zext i8 %993 to i64
  %1012 = shl nuw nsw i64 %1011, 48
  %1013 = or i64 %1012, %1010
  %1014 = zext i8 %994 to i64
  %1015 = shl nuw i64 %1014, 56
  %1016 = or i64 %1015, %1013
  %1017 = zext i8 %979 to i64
  %1018 = zext i8 %980 to i64
  %1019 = shl nuw nsw i64 %1018, 8
  %1020 = or disjoint i64 %1019, %1017
  %1021 = zext i8 %981 to i64
  %1022 = shl nuw nsw i64 %1021, 16
  %1023 = or disjoint i64 %1022, %1020
  %1024 = zext i8 %982 to i64
  %1025 = shl nuw nsw i64 %1024, 24
  %1026 = or disjoint i64 %1025, %1023
  %1027 = zext i8 %983 to i64
  %1028 = shl nuw nsw i64 %1027, 32
  %1029 = or disjoint i64 %1028, %1026
  %1030 = zext i8 %984 to i64
  %1031 = shl nuw nsw i64 %1030, 40
  %1032 = or i64 %1031, %1029
  %1033 = zext i8 %985 to i64
  %1034 = shl nuw nsw i64 %1033, 48
  %1035 = or i64 %1034, %1032
  %1036 = zext i8 %986 to i64
  %1037 = shl nuw i64 %1036, 56
  %1038 = or i64 %1037, %1035
  %1039 = zext i8 %971 to i64
  %1040 = zext i8 %972 to i64
  %1041 = shl nuw nsw i64 %1040, 8
  %1042 = or disjoint i64 %1041, %1039
  %1043 = zext i8 %973 to i64
  %1044 = shl nuw nsw i64 %1043, 16
  %1045 = or disjoint i64 %1044, %1042
  %1046 = zext i8 %974 to i64
  %1047 = shl nuw nsw i64 %1046, 24
  %1048 = or disjoint i64 %1047, %1045
  %1049 = zext i8 %975 to i64
  %1050 = shl nuw nsw i64 %1049, 32
  %1051 = or disjoint i64 %1050, %1048
  %1052 = zext i8 %976 to i64
  %1053 = shl nuw nsw i64 %1052, 40
  %1054 = or i64 %1053, %1051
  %1055 = zext i8 %977 to i64
  %1056 = shl nuw nsw i64 %1055, 48
  %1057 = or i64 %1056, %1054
  %1058 = zext i8 %978 to i64
  %1059 = shl nuw i64 %1058, 56
  %1060 = or i64 %1059, %1057
  %1061 = zext i8 %963 to i64
  %1062 = zext i8 %964 to i64
  %1063 = shl nuw nsw i64 %1062, 8
  %1064 = or disjoint i64 %1063, %1061
  %1065 = zext i8 %965 to i64
  %1066 = shl nuw nsw i64 %1065, 16
  %1067 = or disjoint i64 %1066, %1064
  %1068 = zext i8 %966 to i64
  %1069 = shl nuw nsw i64 %1068, 24
  %1070 = or disjoint i64 %1069, %1067
  %1071 = zext i8 %967 to i64
  %1072 = shl nuw nsw i64 %1071, 32
  %1073 = or disjoint i64 %1072, %1070
  %1074 = zext i8 %968 to i64
  %1075 = shl nuw nsw i64 %1074, 40
  %1076 = or i64 %1075, %1073
  %1077 = zext i8 %969 to i64
  %1078 = shl nuw nsw i64 %1077, 48
  %1079 = or i64 %1078, %1076
  %1080 = zext i8 %970 to i64
  %1081 = shl nuw i64 %1080, 56
  %1082 = or i64 %1081, %1079
  br label %1083

1083:                                             ; preds = %934, %1083
  %1084 = phi i64 [ %1290, %1083 ], [ 0, %934 ]
  %1085 = shl i64 %1084, 5
  %1086 = getelementptr i8, ptr %511, i64 %1085
  %1087 = load i8, ptr %1086, align 16, !tbaa !9
  %1088 = getelementptr inbounds nuw i8, ptr %1086, i64 1
  %1089 = load i8, ptr %1088, align 1, !tbaa !9
  %1090 = getelementptr inbounds nuw i8, ptr %1086, i64 2
  %1091 = load i8, ptr %1090, align 2, !tbaa !9
  %1092 = getelementptr inbounds nuw i8, ptr %1086, i64 3
  %1093 = load i8, ptr %1092, align 1, !tbaa !9
  %1094 = getelementptr inbounds nuw i8, ptr %1086, i64 4
  %1095 = load i8, ptr %1094, align 4, !tbaa !9
  %1096 = getelementptr inbounds nuw i8, ptr %1086, i64 5
  %1097 = load i8, ptr %1096, align 1, !tbaa !9
  %1098 = getelementptr inbounds nuw i8, ptr %1086, i64 6
  %1099 = load i8, ptr %1098, align 2, !tbaa !9
  %1100 = getelementptr inbounds nuw i8, ptr %1086, i64 7
  %1101 = load i8, ptr %1100, align 1, !tbaa !9
  %1102 = getelementptr i8, ptr %1086, i64 8
  %1103 = load i8, ptr %1102, align 8, !tbaa !9
  %1104 = getelementptr i8, ptr %1086, i64 9
  %1105 = load i8, ptr %1104, align 1, !tbaa !9
  %1106 = getelementptr i8, ptr %1086, i64 10
  %1107 = load i8, ptr %1106, align 2, !tbaa !9
  %1108 = getelementptr i8, ptr %1086, i64 11
  %1109 = load i8, ptr %1108, align 1, !tbaa !9
  %1110 = getelementptr i8, ptr %1086, i64 12
  %1111 = load i8, ptr %1110, align 4, !tbaa !9
  %1112 = getelementptr i8, ptr %1086, i64 13
  %1113 = load i8, ptr %1112, align 1, !tbaa !9
  %1114 = getelementptr i8, ptr %1086, i64 14
  %1115 = load i8, ptr %1114, align 2, !tbaa !9
  %1116 = getelementptr i8, ptr %1086, i64 15
  %1117 = load i8, ptr %1116, align 1, !tbaa !9
  %1118 = getelementptr i8, ptr %1086, i64 16
  %1119 = load i8, ptr %1118, align 16, !tbaa !9
  %1120 = getelementptr i8, ptr %1086, i64 17
  %1121 = load i8, ptr %1120, align 1, !tbaa !9
  %1122 = getelementptr i8, ptr %1086, i64 18
  %1123 = load i8, ptr %1122, align 2, !tbaa !9
  %1124 = getelementptr i8, ptr %1086, i64 19
  %1125 = load i8, ptr %1124, align 1, !tbaa !9
  %1126 = getelementptr i8, ptr %1086, i64 20
  %1127 = load i8, ptr %1126, align 4, !tbaa !9
  %1128 = getelementptr i8, ptr %1086, i64 21
  %1129 = load i8, ptr %1128, align 1, !tbaa !9
  %1130 = getelementptr i8, ptr %1086, i64 22
  %1131 = load i8, ptr %1130, align 2, !tbaa !9
  %1132 = getelementptr i8, ptr %1086, i64 23
  %1133 = load i8, ptr %1132, align 1, !tbaa !9
  %1134 = getelementptr i8, ptr %1086, i64 24
  %1135 = load i8, ptr %1134, align 8, !tbaa !9
  %1136 = getelementptr i8, ptr %1086, i64 25
  %1137 = load i8, ptr %1136, align 1, !tbaa !9
  %1138 = getelementptr i8, ptr %1086, i64 26
  %1139 = load i8, ptr %1138, align 2, !tbaa !9
  %1140 = getelementptr i8, ptr %1086, i64 27
  %1141 = load i8, ptr %1140, align 1, !tbaa !9
  %1142 = getelementptr i8, ptr %1086, i64 28
  %1143 = load i8, ptr %1142, align 4, !tbaa !9
  %1144 = getelementptr i8, ptr %1086, i64 29
  %1145 = load i8, ptr %1144, align 1, !tbaa !9
  %1146 = getelementptr i8, ptr %1086, i64 30
  %1147 = load i8, ptr %1146, align 2, !tbaa !9
  %1148 = getelementptr i8, ptr %1086, i64 31
  %1149 = load i8, ptr %1148, align 1, !tbaa !9
  %1150 = shl nsw i64 %1084, 3
  %1151 = getelementptr inbounds nuw i8, ptr %479, i64 %1150
  %1152 = load i8, ptr %1151, align 8, !tbaa !9
  %1153 = zext i8 %1152 to i64
  %1154 = getelementptr inbounds nuw i8, ptr %1151, i64 1
  %1155 = load i8, ptr %1154, align 1, !tbaa !9
  %1156 = zext i8 %1155 to i64
  %1157 = shl nuw nsw i64 %1156, 8
  %1158 = or disjoint i64 %1157, %1153
  %1159 = getelementptr inbounds nuw i8, ptr %1151, i64 2
  %1160 = load i8, ptr %1159, align 2, !tbaa !9
  %1161 = zext i8 %1160 to i64
  %1162 = shl nuw nsw i64 %1161, 16
  %1163 = or disjoint i64 %1162, %1158
  %1164 = getelementptr inbounds nuw i8, ptr %1151, i64 3
  %1165 = load i8, ptr %1164, align 1, !tbaa !9
  %1166 = zext i8 %1165 to i64
  %1167 = shl nuw nsw i64 %1166, 24
  %1168 = or disjoint i64 %1167, %1163
  %1169 = getelementptr inbounds nuw i8, ptr %1151, i64 4
  %1170 = load i8, ptr %1169, align 4, !tbaa !9
  %1171 = zext i8 %1170 to i64
  %1172 = shl nuw nsw i64 %1171, 32
  %1173 = or disjoint i64 %1172, %1168
  %1174 = getelementptr inbounds nuw i8, ptr %1151, i64 5
  %1175 = load i8, ptr %1174, align 1, !tbaa !9
  %1176 = zext i8 %1175 to i64
  %1177 = shl nuw nsw i64 %1176, 40
  %1178 = or i64 %1177, %1173
  %1179 = getelementptr inbounds nuw i8, ptr %1151, i64 6
  %1180 = load i8, ptr %1179, align 2, !tbaa !9
  %1181 = zext i8 %1180 to i64
  %1182 = shl nuw nsw i64 %1181, 48
  %1183 = or i64 %1182, %1178
  %1184 = getelementptr inbounds nuw i8, ptr %1151, i64 7
  %1185 = load i8, ptr %1184, align 1, !tbaa !9
  %1186 = zext i8 %1185 to i64
  %1187 = shl nuw i64 %1186, 56
  %1188 = or i64 %1187, %1183
  %1189 = zext i8 %1135 to i64
  %1190 = zext i8 %1137 to i64
  %1191 = shl nuw nsw i64 %1190, 8
  %1192 = or disjoint i64 %1191, %1189
  %1193 = zext i8 %1139 to i64
  %1194 = shl nuw nsw i64 %1193, 16
  %1195 = or disjoint i64 %1194, %1192
  %1196 = zext i8 %1141 to i64
  %1197 = shl nuw nsw i64 %1196, 24
  %1198 = or disjoint i64 %1197, %1195
  %1199 = zext i8 %1143 to i64
  %1200 = shl nuw nsw i64 %1199, 32
  %1201 = or disjoint i64 %1200, %1198
  %1202 = zext i8 %1145 to i64
  %1203 = shl nuw nsw i64 %1202, 40
  %1204 = or i64 %1203, %1201
  %1205 = zext i8 %1147 to i64
  %1206 = shl nuw nsw i64 %1205, 48
  %1207 = or i64 %1206, %1204
  %1208 = zext i8 %1149 to i64
  %1209 = shl nuw i64 %1208, 56
  %1210 = or i64 %1209, %1207
  %1211 = zext i8 %1119 to i64
  %1212 = zext i8 %1121 to i64
  %1213 = shl nuw nsw i64 %1212, 8
  %1214 = or disjoint i64 %1213, %1211
  %1215 = zext i8 %1123 to i64
  %1216 = shl nuw nsw i64 %1215, 16
  %1217 = or disjoint i64 %1216, %1214
  %1218 = zext i8 %1125 to i64
  %1219 = shl nuw nsw i64 %1218, 24
  %1220 = or disjoint i64 %1219, %1217
  %1221 = zext i8 %1127 to i64
  %1222 = shl nuw nsw i64 %1221, 32
  %1223 = or disjoint i64 %1222, %1220
  %1224 = zext i8 %1129 to i64
  %1225 = shl nuw nsw i64 %1224, 40
  %1226 = or i64 %1225, %1223
  %1227 = zext i8 %1131 to i64
  %1228 = shl nuw nsw i64 %1227, 48
  %1229 = or i64 %1228, %1226
  %1230 = zext i8 %1133 to i64
  %1231 = shl nuw i64 %1230, 56
  %1232 = or i64 %1231, %1229
  %1233 = zext i8 %1103 to i64
  %1234 = zext i8 %1105 to i64
  %1235 = shl nuw nsw i64 %1234, 8
  %1236 = or disjoint i64 %1235, %1233
  %1237 = zext i8 %1107 to i64
  %1238 = shl nuw nsw i64 %1237, 16
  %1239 = or disjoint i64 %1238, %1236
  %1240 = zext i8 %1109 to i64
  %1241 = shl nuw nsw i64 %1240, 24
  %1242 = or disjoint i64 %1241, %1239
  %1243 = zext i8 %1111 to i64
  %1244 = shl nuw nsw i64 %1243, 32
  %1245 = or disjoint i64 %1244, %1242
  %1246 = zext i8 %1113 to i64
  %1247 = shl nuw nsw i64 %1246, 40
  %1248 = or i64 %1247, %1245
  %1249 = zext i8 %1115 to i64
  %1250 = shl nuw nsw i64 %1249, 48
  %1251 = or i64 %1250, %1248
  %1252 = zext i8 %1117 to i64
  %1253 = shl nuw i64 %1252, 56
  %1254 = or i64 %1253, %1251
  %1255 = zext i8 %1087 to i64
  %1256 = zext i8 %1089 to i64
  %1257 = shl nuw nsw i64 %1256, 8
  %1258 = or disjoint i64 %1257, %1255
  %1259 = zext i8 %1091 to i64
  %1260 = shl nuw nsw i64 %1259, 16
  %1261 = or disjoint i64 %1260, %1258
  %1262 = zext i8 %1093 to i64
  %1263 = shl nuw nsw i64 %1262, 24
  %1264 = or disjoint i64 %1263, %1261
  %1265 = zext i8 %1095 to i64
  %1266 = shl nuw nsw i64 %1265, 32
  %1267 = or disjoint i64 %1266, %1264
  %1268 = zext i8 %1097 to i64
  %1269 = shl nuw nsw i64 %1268, 40
  %1270 = or i64 %1269, %1267
  %1271 = zext i8 %1099 to i64
  %1272 = shl nuw nsw i64 %1271, 48
  %1273 = or i64 %1272, %1270
  %1274 = zext i8 %1101 to i64
  %1275 = shl nuw i64 %1274, 56
  %1276 = or i64 %1275, %1273
  %1277 = mul nsw i64 %1082, %1276
  %1278 = ashr i64 %1277, 16
  %1279 = mul nsw i64 %1060, %1254
  %1280 = ashr i64 %1279, 16
  %1281 = add nsw i64 %1280, %1278
  %1282 = mul nsw i64 %1038, %1232
  %1283 = ashr i64 %1282, 16
  %1284 = add nsw i64 %1281, %1283
  %1285 = mul nsw i64 %1016, %1210
  %1286 = ashr i64 %1285, 16
  %1287 = add nsw i64 %1284, %1286
  %1288 = add nsw i64 %1287, %1188
  %1289 = getelementptr inbounds nuw [8 x i8], ptr %34, i64 %1084
  store i64 %1288, ptr %1289, align 8, !tbaa !10
  %1290 = add nuw nsw i64 %1084, 1
  %1291 = icmp eq i64 %1290, 4
  br i1 %1291, label %1292, label %1083, !llvm.loop !12

1292:                                             ; preds = %1083
  %1293 = load i8, ptr %573, align 16, !tbaa !9
  %1294 = load i8, ptr %935, align 1, !tbaa !9
  %1295 = load i8, ptr %936, align 2, !tbaa !9
  %1296 = load i8, ptr %937, align 1, !tbaa !9
  %1297 = load i8, ptr %938, align 4, !tbaa !9
  %1298 = load i8, ptr %939, align 1, !tbaa !9
  %1299 = load i8, ptr %940, align 2, !tbaa !9
  %1300 = load i8, ptr %941, align 1, !tbaa !9
  %1301 = load i8, ptr %574, align 8, !tbaa !9
  %1302 = load i8, ptr %942, align 1, !tbaa !9
  %1303 = load i8, ptr %943, align 2, !tbaa !9
  %1304 = load i8, ptr %944, align 1, !tbaa !9
  %1305 = load i8, ptr %945, align 4, !tbaa !9
  %1306 = load i8, ptr %946, align 1, !tbaa !9
  %1307 = load i8, ptr %947, align 2, !tbaa !9
  %1308 = load i8, ptr %948, align 1, !tbaa !9
  %1309 = load i8, ptr %575, align 16, !tbaa !9
  %1310 = load i8, ptr %949, align 1, !tbaa !9
  %1311 = load i8, ptr %950, align 2, !tbaa !9
  %1312 = load i8, ptr %951, align 1, !tbaa !9
  %1313 = load i8, ptr %952, align 4, !tbaa !9
  %1314 = load i8, ptr %953, align 1, !tbaa !9
  %1315 = load i8, ptr %954, align 2, !tbaa !9
  %1316 = load i8, ptr %955, align 1, !tbaa !9
  %1317 = load i8, ptr %576, align 8, !tbaa !9
  %1318 = load i8, ptr %956, align 1, !tbaa !9
  %1319 = load i8, ptr %957, align 2, !tbaa !9
  %1320 = load i8, ptr %958, align 1, !tbaa !9
  %1321 = load i8, ptr %959, align 4, !tbaa !9
  %1322 = load i8, ptr %960, align 1, !tbaa !9
  %1323 = load i8, ptr %961, align 2, !tbaa !9
  %1324 = load i8, ptr %962, align 1, !tbaa !9
  %1325 = zext i8 %1317 to i64
  %1326 = zext i8 %1318 to i64
  %1327 = shl nuw nsw i64 %1326, 8
  %1328 = or disjoint i64 %1327, %1325
  %1329 = zext i8 %1319 to i64
  %1330 = shl nuw nsw i64 %1329, 16
  %1331 = or disjoint i64 %1330, %1328
  %1332 = zext i8 %1320 to i64
  %1333 = shl nuw nsw i64 %1332, 24
  %1334 = or disjoint i64 %1333, %1331
  %1335 = zext i8 %1321 to i64
  %1336 = shl nuw nsw i64 %1335, 32
  %1337 = or disjoint i64 %1336, %1334
  %1338 = zext i8 %1322 to i64
  %1339 = shl nuw nsw i64 %1338, 40
  %1340 = or i64 %1339, %1337
  %1341 = zext i8 %1323 to i64
  %1342 = shl nuw nsw i64 %1341, 48
  %1343 = or i64 %1342, %1340
  %1344 = zext i8 %1324 to i64
  %1345 = shl nuw i64 %1344, 56
  %1346 = or i64 %1345, %1343
  %1347 = zext i8 %1309 to i64
  %1348 = zext i8 %1310 to i64
  %1349 = shl nuw nsw i64 %1348, 8
  %1350 = or disjoint i64 %1349, %1347
  %1351 = zext i8 %1311 to i64
  %1352 = shl nuw nsw i64 %1351, 16
  %1353 = or disjoint i64 %1352, %1350
  %1354 = zext i8 %1312 to i64
  %1355 = shl nuw nsw i64 %1354, 24
  %1356 = or disjoint i64 %1355, %1353
  %1357 = zext i8 %1313 to i64
  %1358 = shl nuw nsw i64 %1357, 32
  %1359 = or disjoint i64 %1358, %1356
  %1360 = zext i8 %1314 to i64
  %1361 = shl nuw nsw i64 %1360, 40
  %1362 = or i64 %1361, %1359
  %1363 = zext i8 %1315 to i64
  %1364 = shl nuw nsw i64 %1363, 48
  %1365 = or i64 %1364, %1362
  %1366 = zext i8 %1316 to i64
  %1367 = shl nuw i64 %1366, 56
  %1368 = or i64 %1367, %1365
  %1369 = zext i8 %1301 to i64
  %1370 = zext i8 %1302 to i64
  %1371 = shl nuw nsw i64 %1370, 8
  %1372 = or disjoint i64 %1371, %1369
  %1373 = zext i8 %1303 to i64
  %1374 = shl nuw nsw i64 %1373, 16
  %1375 = or disjoint i64 %1374, %1372
  %1376 = zext i8 %1304 to i64
  %1377 = shl nuw nsw i64 %1376, 24
  %1378 = or disjoint i64 %1377, %1375
  %1379 = zext i8 %1305 to i64
  %1380 = shl nuw nsw i64 %1379, 32
  %1381 = or disjoint i64 %1380, %1378
  %1382 = zext i8 %1306 to i64
  %1383 = shl nuw nsw i64 %1382, 40
  %1384 = or i64 %1383, %1381
  %1385 = zext i8 %1307 to i64
  %1386 = shl nuw nsw i64 %1385, 48
  %1387 = or i64 %1386, %1384
  %1388 = zext i8 %1308 to i64
  %1389 = shl nuw i64 %1388, 56
  %1390 = or i64 %1389, %1387
  %1391 = zext i8 %1293 to i64
  %1392 = zext i8 %1294 to i64
  %1393 = shl nuw nsw i64 %1392, 8
  %1394 = or disjoint i64 %1393, %1391
  %1395 = zext i8 %1295 to i64
  %1396 = shl nuw nsw i64 %1395, 16
  %1397 = or disjoint i64 %1396, %1394
  %1398 = zext i8 %1296 to i64
  %1399 = shl nuw nsw i64 %1398, 24
  %1400 = or disjoint i64 %1399, %1397
  %1401 = zext i8 %1297 to i64
  %1402 = shl nuw nsw i64 %1401, 32
  %1403 = or disjoint i64 %1402, %1400
  %1404 = zext i8 %1298 to i64
  %1405 = shl nuw nsw i64 %1404, 40
  %1406 = or i64 %1405, %1403
  %1407 = zext i8 %1299 to i64
  %1408 = shl nuw nsw i64 %1407, 48
  %1409 = or i64 %1408, %1406
  %1410 = zext i8 %1300 to i64
  %1411 = shl nuw i64 %1410, 56
  %1412 = or i64 %1411, %1409
  br label %1413

1413:                                             ; preds = %1292, %1413
  %1414 = phi i64 [ %1620, %1413 ], [ 0, %1292 ]
  %1415 = shl i64 %1414, 5
  %1416 = getelementptr i8, ptr %512, i64 %1415
  %1417 = load i8, ptr %1416, align 16, !tbaa !9
  %1418 = getelementptr inbounds nuw i8, ptr %1416, i64 1
  %1419 = load i8, ptr %1418, align 1, !tbaa !9
  %1420 = getelementptr inbounds nuw i8, ptr %1416, i64 2
  %1421 = load i8, ptr %1420, align 2, !tbaa !9
  %1422 = getelementptr inbounds nuw i8, ptr %1416, i64 3
  %1423 = load i8, ptr %1422, align 1, !tbaa !9
  %1424 = getelementptr inbounds nuw i8, ptr %1416, i64 4
  %1425 = load i8, ptr %1424, align 4, !tbaa !9
  %1426 = getelementptr inbounds nuw i8, ptr %1416, i64 5
  %1427 = load i8, ptr %1426, align 1, !tbaa !9
  %1428 = getelementptr inbounds nuw i8, ptr %1416, i64 6
  %1429 = load i8, ptr %1428, align 2, !tbaa !9
  %1430 = getelementptr inbounds nuw i8, ptr %1416, i64 7
  %1431 = load i8, ptr %1430, align 1, !tbaa !9
  %1432 = getelementptr i8, ptr %1416, i64 8
  %1433 = load i8, ptr %1432, align 8, !tbaa !9
  %1434 = getelementptr i8, ptr %1416, i64 9
  %1435 = load i8, ptr %1434, align 1, !tbaa !9
  %1436 = getelementptr i8, ptr %1416, i64 10
  %1437 = load i8, ptr %1436, align 2, !tbaa !9
  %1438 = getelementptr i8, ptr %1416, i64 11
  %1439 = load i8, ptr %1438, align 1, !tbaa !9
  %1440 = getelementptr i8, ptr %1416, i64 12
  %1441 = load i8, ptr %1440, align 4, !tbaa !9
  %1442 = getelementptr i8, ptr %1416, i64 13
  %1443 = load i8, ptr %1442, align 1, !tbaa !9
  %1444 = getelementptr i8, ptr %1416, i64 14
  %1445 = load i8, ptr %1444, align 2, !tbaa !9
  %1446 = getelementptr i8, ptr %1416, i64 15
  %1447 = load i8, ptr %1446, align 1, !tbaa !9
  %1448 = getelementptr i8, ptr %1416, i64 16
  %1449 = load i8, ptr %1448, align 16, !tbaa !9
  %1450 = getelementptr i8, ptr %1416, i64 17
  %1451 = load i8, ptr %1450, align 1, !tbaa !9
  %1452 = getelementptr i8, ptr %1416, i64 18
  %1453 = load i8, ptr %1452, align 2, !tbaa !9
  %1454 = getelementptr i8, ptr %1416, i64 19
  %1455 = load i8, ptr %1454, align 1, !tbaa !9
  %1456 = getelementptr i8, ptr %1416, i64 20
  %1457 = load i8, ptr %1456, align 4, !tbaa !9
  %1458 = getelementptr i8, ptr %1416, i64 21
  %1459 = load i8, ptr %1458, align 1, !tbaa !9
  %1460 = getelementptr i8, ptr %1416, i64 22
  %1461 = load i8, ptr %1460, align 2, !tbaa !9
  %1462 = getelementptr i8, ptr %1416, i64 23
  %1463 = load i8, ptr %1462, align 1, !tbaa !9
  %1464 = getelementptr i8, ptr %1416, i64 24
  %1465 = load i8, ptr %1464, align 8, !tbaa !9
  %1466 = getelementptr i8, ptr %1416, i64 25
  %1467 = load i8, ptr %1466, align 1, !tbaa !9
  %1468 = getelementptr i8, ptr %1416, i64 26
  %1469 = load i8, ptr %1468, align 2, !tbaa !9
  %1470 = getelementptr i8, ptr %1416, i64 27
  %1471 = load i8, ptr %1470, align 1, !tbaa !9
  %1472 = getelementptr i8, ptr %1416, i64 28
  %1473 = load i8, ptr %1472, align 4, !tbaa !9
  %1474 = getelementptr i8, ptr %1416, i64 29
  %1475 = load i8, ptr %1474, align 1, !tbaa !9
  %1476 = getelementptr i8, ptr %1416, i64 30
  %1477 = load i8, ptr %1476, align 2, !tbaa !9
  %1478 = getelementptr i8, ptr %1416, i64 31
  %1479 = load i8, ptr %1478, align 1, !tbaa !9
  %1480 = shl nsw i64 %1414, 3
  %1481 = getelementptr inbounds nuw i8, ptr %483, i64 %1480
  %1482 = load i8, ptr %1481, align 8, !tbaa !9
  %1483 = zext i8 %1482 to i64
  %1484 = getelementptr inbounds nuw i8, ptr %1481, i64 1
  %1485 = load i8, ptr %1484, align 1, !tbaa !9
  %1486 = zext i8 %1485 to i64
  %1487 = shl nuw nsw i64 %1486, 8
  %1488 = or disjoint i64 %1487, %1483
  %1489 = getelementptr inbounds nuw i8, ptr %1481, i64 2
  %1490 = load i8, ptr %1489, align 2, !tbaa !9
  %1491 = zext i8 %1490 to i64
  %1492 = shl nuw nsw i64 %1491, 16
  %1493 = or disjoint i64 %1492, %1488
  %1494 = getelementptr inbounds nuw i8, ptr %1481, i64 3
  %1495 = load i8, ptr %1494, align 1, !tbaa !9
  %1496 = zext i8 %1495 to i64
  %1497 = shl nuw nsw i64 %1496, 24
  %1498 = or disjoint i64 %1497, %1493
  %1499 = getelementptr inbounds nuw i8, ptr %1481, i64 4
  %1500 = load i8, ptr %1499, align 4, !tbaa !9
  %1501 = zext i8 %1500 to i64
  %1502 = shl nuw nsw i64 %1501, 32
  %1503 = or disjoint i64 %1502, %1498
  %1504 = getelementptr inbounds nuw i8, ptr %1481, i64 5
  %1505 = load i8, ptr %1504, align 1, !tbaa !9
  %1506 = zext i8 %1505 to i64
  %1507 = shl nuw nsw i64 %1506, 40
  %1508 = or i64 %1507, %1503
  %1509 = getelementptr inbounds nuw i8, ptr %1481, i64 6
  %1510 = load i8, ptr %1509, align 2, !tbaa !9
  %1511 = zext i8 %1510 to i64
  %1512 = shl nuw nsw i64 %1511, 48
  %1513 = or i64 %1512, %1508
  %1514 = getelementptr inbounds nuw i8, ptr %1481, i64 7
  %1515 = load i8, ptr %1514, align 1, !tbaa !9
  %1516 = zext i8 %1515 to i64
  %1517 = shl nuw i64 %1516, 56
  %1518 = or i64 %1517, %1513
  %1519 = zext i8 %1465 to i64
  %1520 = zext i8 %1467 to i64
  %1521 = shl nuw nsw i64 %1520, 8
  %1522 = or disjoint i64 %1521, %1519
  %1523 = zext i8 %1469 to i64
  %1524 = shl nuw nsw i64 %1523, 16
  %1525 = or disjoint i64 %1524, %1522
  %1526 = zext i8 %1471 to i64
  %1527 = shl nuw nsw i64 %1526, 24
  %1528 = or disjoint i64 %1527, %1525
  %1529 = zext i8 %1473 to i64
  %1530 = shl nuw nsw i64 %1529, 32
  %1531 = or disjoint i64 %1530, %1528
  %1532 = zext i8 %1475 to i64
  %1533 = shl nuw nsw i64 %1532, 40
  %1534 = or i64 %1533, %1531
  %1535 = zext i8 %1477 to i64
  %1536 = shl nuw nsw i64 %1535, 48
  %1537 = or i64 %1536, %1534
  %1538 = zext i8 %1479 to i64
  %1539 = shl nuw i64 %1538, 56
  %1540 = or i64 %1539, %1537
  %1541 = zext i8 %1449 to i64
  %1542 = zext i8 %1451 to i64
  %1543 = shl nuw nsw i64 %1542, 8
  %1544 = or disjoint i64 %1543, %1541
  %1545 = zext i8 %1453 to i64
  %1546 = shl nuw nsw i64 %1545, 16
  %1547 = or disjoint i64 %1546, %1544
  %1548 = zext i8 %1455 to i64
  %1549 = shl nuw nsw i64 %1548, 24
  %1550 = or disjoint i64 %1549, %1547
  %1551 = zext i8 %1457 to i64
  %1552 = shl nuw nsw i64 %1551, 32
  %1553 = or disjoint i64 %1552, %1550
  %1554 = zext i8 %1459 to i64
  %1555 = shl nuw nsw i64 %1554, 40
  %1556 = or i64 %1555, %1553
  %1557 = zext i8 %1461 to i64
  %1558 = shl nuw nsw i64 %1557, 48
  %1559 = or i64 %1558, %1556
  %1560 = zext i8 %1463 to i64
  %1561 = shl nuw i64 %1560, 56
  %1562 = or i64 %1561, %1559
  %1563 = zext i8 %1433 to i64
  %1564 = zext i8 %1435 to i64
  %1565 = shl nuw nsw i64 %1564, 8
  %1566 = or disjoint i64 %1565, %1563
  %1567 = zext i8 %1437 to i64
  %1568 = shl nuw nsw i64 %1567, 16
  %1569 = or disjoint i64 %1568, %1566
  %1570 = zext i8 %1439 to i64
  %1571 = shl nuw nsw i64 %1570, 24
  %1572 = or disjoint i64 %1571, %1569
  %1573 = zext i8 %1441 to i64
  %1574 = shl nuw nsw i64 %1573, 32
  %1575 = or disjoint i64 %1574, %1572
  %1576 = zext i8 %1443 to i64
  %1577 = shl nuw nsw i64 %1576, 40
  %1578 = or i64 %1577, %1575
  %1579 = zext i8 %1445 to i64
  %1580 = shl nuw nsw i64 %1579, 48
  %1581 = or i64 %1580, %1578
  %1582 = zext i8 %1447 to i64
  %1583 = shl nuw i64 %1582, 56
  %1584 = or i64 %1583, %1581
  %1585 = zext i8 %1417 to i64
  %1586 = zext i8 %1419 to i64
  %1587 = shl nuw nsw i64 %1586, 8
  %1588 = or disjoint i64 %1587, %1585
  %1589 = zext i8 %1421 to i64
  %1590 = shl nuw nsw i64 %1589, 16
  %1591 = or disjoint i64 %1590, %1588
  %1592 = zext i8 %1423 to i64
  %1593 = shl nuw nsw i64 %1592, 24
  %1594 = or disjoint i64 %1593, %1591
  %1595 = zext i8 %1425 to i64
  %1596 = shl nuw nsw i64 %1595, 32
  %1597 = or disjoint i64 %1596, %1594
  %1598 = zext i8 %1427 to i64
  %1599 = shl nuw nsw i64 %1598, 40
  %1600 = or i64 %1599, %1597
  %1601 = zext i8 %1429 to i64
  %1602 = shl nuw nsw i64 %1601, 48
  %1603 = or i64 %1602, %1600
  %1604 = zext i8 %1431 to i64
  %1605 = shl nuw i64 %1604, 56
  %1606 = or i64 %1605, %1603
  %1607 = mul nsw i64 %1412, %1606
  %1608 = ashr i64 %1607, 16
  %1609 = mul nsw i64 %1390, %1584
  %1610 = ashr i64 %1609, 16
  %1611 = add nsw i64 %1610, %1608
  %1612 = mul nsw i64 %1368, %1562
  %1613 = ashr i64 %1612, 16
  %1614 = add nsw i64 %1611, %1613
  %1615 = mul nsw i64 %1346, %1540
  %1616 = ashr i64 %1615, 16
  %1617 = add nsw i64 %1614, %1616
  %1618 = add nsw i64 %1617, %1518
  %1619 = getelementptr inbounds nuw [8 x i8], ptr %35, i64 %1414
  store i64 %1618, ptr %1619, align 8, !tbaa !10
  %1620 = add nuw nsw i64 %1414, 1
  %1621 = icmp eq i64 %1620, 4
  br i1 %1621, label %1622, label %1413, !llvm.loop !12

1622:                                             ; preds = %1413
  %1623 = getelementptr i8, ptr %29, i64 %572
  %1624 = getelementptr i8, ptr %28, i64 %572
  %1625 = getelementptr i8, ptr %27, i64 %572
  call void @llvm.memcpy.p0.p0.i64(ptr noundef nonnull align 16 dereferenceable(32) %1625, ptr noundef nonnull align 16 dereferenceable(32) %33, i64 32, i1 false), !tbaa !10
  call void @llvm.memcpy.p0.p0.i64(ptr noundef nonnull align 16 dereferenceable(32) %1624, ptr noundef nonnull align 16 dereferenceable(32) %34, i64 32, i1 false), !tbaa !10
  call void @llvm.memcpy.p0.p0.i64(ptr noundef nonnull align 16 dereferenceable(32) %1623, ptr noundef nonnull align 16 dereferenceable(32) %35, i64 32, i1 false), !tbaa !10
  call void @llvm.lifetime.end.p0(ptr nonnull %35) #9
  call void @llvm.lifetime.end.p0(ptr nonnull %34) #9
  call void @llvm.lifetime.end.p0(ptr nonnull %33) #9
  %1626 = add nuw nsw i64 %571, 1
  %1627 = icmp eq i64 %1626, 3
  br i1 %1627, label %513, label %570, !llvm.loop !25

1628:                                             ; preds = %1635
  %1629 = getelementptr inbounds nuw i8, ptr %40, i64 8
  %1630 = getelementptr inbounds nuw i8, ptr %40, i64 16
  %1631 = getelementptr inbounds nuw i8, ptr %40, i64 24
  %1632 = getelementptr inbounds nuw i8, ptr %41, i64 8
  %1633 = getelementptr inbounds nuw i8, ptr %41, i64 16
  %1634 = getelementptr inbounds nuw i8, ptr %41, i64 24
  br label %1722

1635:                                             ; preds = %1635, %513
  %1636 = phi i64 [ 0, %513 ], [ %1720, %1635 ]
  call void @llvm.lifetime.start.p0(ptr nonnull %36) #9
  call void @llvm.lifetime.start.p0(ptr nonnull %37) #9
  %1637 = getelementptr inbounds nuw [32 x i8], ptr %27, i64 %1636
  %1638 = load i64, ptr %1637, align 16, !tbaa !10
  %1639 = getelementptr inbounds nuw i8, ptr %1637, i64 8
  %1640 = load i64, ptr %1639, align 8, !tbaa !10
  %1641 = getelementptr inbounds nuw i8, ptr %1637, i64 16
  %1642 = load i64, ptr %1641, align 16, !tbaa !10
  %1643 = getelementptr inbounds nuw i8, ptr %1637, i64 24
  %1644 = load i64, ptr %1643, align 8, !tbaa !10
  %1645 = mul nsw i64 %1638, %525
  %1646 = and i64 %1645, -65536
  %1647 = mul nsw i64 %1640, %527
  %1648 = and i64 %1647, -65536
  %1649 = add i64 %1648, %1646
  %1650 = mul nsw i64 %1642, %529
  %1651 = and i64 %1650, -65536
  %1652 = add i64 %1649, %1651
  %1653 = mul nsw i64 %1644, %531
  %1654 = add i64 %1652, %1653
  %1655 = and i64 %1654, -65536
  %1656 = sdiv i64 %1655, 131072
  store i64 %1656, ptr %36, align 16, !tbaa !10
  %1657 = mul nsw i64 %1638, %533
  %1658 = and i64 %1657, -65536
  %1659 = mul nsw i64 %1640, %535
  %1660 = and i64 %1659, -65536
  %1661 = add i64 %1660, %1658
  %1662 = mul nsw i64 %1642, %537
  %1663 = and i64 %1662, -65536
  %1664 = add i64 %1661, %1663
  %1665 = mul nsw i64 %1644, %539
  %1666 = add i64 %1664, %1665
  %1667 = and i64 %1666, -65536
  %1668 = sdiv i64 %1667, 131072
  store i64 %1668, ptr %540, align 8, !tbaa !10
  %1669 = mul nsw i64 %1638, %542
  %1670 = and i64 %1669, -65536
  %1671 = mul nsw i64 %1640, %544
  %1672 = and i64 %1671, -65536
  %1673 = add i64 %1672, %1670
  %1674 = mul nsw i64 %1642, %546
  %1675 = and i64 %1674, -65536
  %1676 = add i64 %1673, %1675
  %1677 = mul nsw i64 %1644, %548
  %1678 = add i64 %1676, %1677
  %1679 = and i64 %1678, -65536
  %1680 = sdiv i64 %1679, 131072
  store i64 %1680, ptr %549, align 16, !tbaa !10
  call void @llvm.lifetime.start.p0(ptr nonnull %38) #9
  store ptr %36, ptr %38, align 8, !tbaa !15
  store i64 3, ptr %514, align 8, !tbaa !19
  store i64 8, ptr %515, align 8, !tbaa !20
  store i64 8, ptr %516, align 8, !tbaa !21
  call void @llvm.lifetime.start.p0(ptr nonnull %39) #9
  store ptr %37, ptr %39, align 8, !tbaa !15
  store i64 3, ptr %517, align 8, !tbaa !19
  store i64 8, ptr %518, align 8, !tbaa !20
  store i64 8, ptr %519, align 8, !tbaa !21
  call fastcc void @softmax(ptr noundef %38, ptr noundef %39)
  %1681 = getelementptr inbounds nuw [32 x i8], ptr %30, i64 %1636
  %1682 = load i64, ptr %37, align 16, !tbaa !10
  %1683 = mul nsw i64 %1682, %520
  %1684 = ashr i64 %1683, 16
  %1685 = load i64, ptr %550, align 8, !tbaa !10
  %1686 = mul nsw i64 %1685, %522
  %1687 = ashr i64 %1686, 16
  %1688 = add nsw i64 %1687, %1684
  %1689 = load i64, ptr %551, align 16, !tbaa !10
  %1690 = mul nsw i64 %1689, %524
  %1691 = ashr i64 %1690, 16
  %1692 = add nsw i64 %1688, %1691
  store i64 %1692, ptr %1681, align 16, !tbaa !10
  %1693 = mul nsw i64 %1682, %553
  %1694 = ashr i64 %1693, 16
  %1695 = mul nsw i64 %1685, %555
  %1696 = ashr i64 %1695, 16
  %1697 = add nsw i64 %1696, %1694
  %1698 = mul nsw i64 %1689, %557
  %1699 = ashr i64 %1698, 16
  %1700 = add nsw i64 %1697, %1699
  %1701 = getelementptr inbounds nuw i8, ptr %1681, i64 8
  store i64 %1700, ptr %1701, align 8, !tbaa !10
  %1702 = mul nsw i64 %1682, %559
  %1703 = ashr i64 %1702, 16
  %1704 = mul nsw i64 %1685, %561
  %1705 = ashr i64 %1704, 16
  %1706 = add nsw i64 %1705, %1703
  %1707 = mul nsw i64 %1689, %563
  %1708 = ashr i64 %1707, 16
  %1709 = add nsw i64 %1706, %1708
  %1710 = getelementptr inbounds nuw i8, ptr %1681, i64 16
  store i64 %1709, ptr %1710, align 16, !tbaa !10
  %1711 = mul nsw i64 %1682, %565
  %1712 = ashr i64 %1711, 16
  %1713 = mul nsw i64 %1685, %567
  %1714 = ashr i64 %1713, 16
  %1715 = add nsw i64 %1714, %1712
  %1716 = mul nsw i64 %1689, %569
  %1717 = ashr i64 %1716, 16
  %1718 = add nsw i64 %1715, %1717
  %1719 = getelementptr inbounds nuw i8, ptr %1681, i64 24
  store i64 %1718, ptr %1719, align 8, !tbaa !10
  call void @llvm.lifetime.end.p0(ptr nonnull %39) #9
  call void @llvm.lifetime.end.p0(ptr nonnull %38) #9
  call void @llvm.lifetime.end.p0(ptr nonnull %37) #9
  call void @llvm.lifetime.end.p0(ptr nonnull %36) #9
  %1720 = add nuw nsw i64 %1636, 1
  %1721 = icmp eq i64 %1720, 3
  br i1 %1721, label %1628, label %1635, !llvm.loop !26

1722:                                             ; preds = %1942, %1628
  %1723 = phi i64 [ 0, %1628 ], [ %2216, %1942 ]
  %1724 = getelementptr inbounds nuw [32 x i8], ptr %30, i64 %1723
  %1725 = getelementptr inbounds nuw [32 x i8], ptr %32, i64 %1723
  %1726 = load i64, ptr %1724, align 16
  %1727 = getelementptr inbounds nuw i8, ptr %1724, i64 8
  %1728 = load i64, ptr %1727, align 8
  %1729 = getelementptr inbounds nuw i8, ptr %1724, i64 16
  %1730 = load i64, ptr %1729, align 16
  %1731 = getelementptr inbounds nuw i8, ptr %1724, i64 24
  %1732 = load i64, ptr %1731, align 8
  br label %1733

1733:                                             ; preds = %1733, %1722
  %1734 = phi i64 [ 0, %1722 ], [ %1940, %1733 ]
  %1735 = shl i64 %1734, 5
  %1736 = getelementptr i8, ptr %60, i64 %1735
  %1737 = load i8, ptr %1736, align 16, !tbaa !9
  %1738 = zext i8 %1737 to i64
  %1739 = getelementptr inbounds nuw i8, ptr %1736, i64 1
  %1740 = load i8, ptr %1739, align 1, !tbaa !9
  %1741 = zext i8 %1740 to i64
  %1742 = shl nuw nsw i64 %1741, 8
  %1743 = or disjoint i64 %1742, %1738
  %1744 = getelementptr inbounds nuw i8, ptr %1736, i64 2
  %1745 = load i8, ptr %1744, align 2, !tbaa !9
  %1746 = zext i8 %1745 to i64
  %1747 = shl nuw nsw i64 %1746, 16
  %1748 = or disjoint i64 %1747, %1743
  %1749 = getelementptr inbounds nuw i8, ptr %1736, i64 3
  %1750 = load i8, ptr %1749, align 1, !tbaa !9
  %1751 = zext i8 %1750 to i64
  %1752 = shl nuw nsw i64 %1751, 24
  %1753 = or disjoint i64 %1752, %1748
  %1754 = getelementptr inbounds nuw i8, ptr %1736, i64 4
  %1755 = load i8, ptr %1754, align 4, !tbaa !9
  %1756 = zext i8 %1755 to i64
  %1757 = shl nuw nsw i64 %1756, 32
  %1758 = or disjoint i64 %1757, %1753
  %1759 = getelementptr inbounds nuw i8, ptr %1736, i64 5
  %1760 = load i8, ptr %1759, align 1, !tbaa !9
  %1761 = zext i8 %1760 to i64
  %1762 = shl nuw nsw i64 %1761, 40
  %1763 = or i64 %1762, %1758
  %1764 = getelementptr inbounds nuw i8, ptr %1736, i64 6
  %1765 = load i8, ptr %1764, align 2, !tbaa !9
  %1766 = zext i8 %1765 to i64
  %1767 = shl nuw nsw i64 %1766, 48
  %1768 = or i64 %1767, %1763
  %1769 = getelementptr inbounds nuw i8, ptr %1736, i64 7
  %1770 = load i8, ptr %1769, align 1, !tbaa !9
  %1771 = zext i8 %1770 to i64
  %1772 = shl nuw i64 %1771, 56
  %1773 = or i64 %1772, %1768
  %1774 = mul nsw i64 %1726, %1773
  %1775 = ashr i64 %1774, 16
  %1776 = getelementptr i8, ptr %1736, i64 8
  %1777 = load i8, ptr %1776, align 8, !tbaa !9
  %1778 = zext i8 %1777 to i64
  %1779 = getelementptr i8, ptr %1736, i64 9
  %1780 = load i8, ptr %1779, align 1, !tbaa !9
  %1781 = zext i8 %1780 to i64
  %1782 = shl nuw nsw i64 %1781, 8
  %1783 = or disjoint i64 %1782, %1778
  %1784 = getelementptr i8, ptr %1736, i64 10
  %1785 = load i8, ptr %1784, align 2, !tbaa !9
  %1786 = zext i8 %1785 to i64
  %1787 = shl nuw nsw i64 %1786, 16
  %1788 = or disjoint i64 %1787, %1783
  %1789 = getelementptr i8, ptr %1736, i64 11
  %1790 = load i8, ptr %1789, align 1, !tbaa !9
  %1791 = zext i8 %1790 to i64
  %1792 = shl nuw nsw i64 %1791, 24
  %1793 = or disjoint i64 %1792, %1788
  %1794 = getelementptr i8, ptr %1736, i64 12
  %1795 = load i8, ptr %1794, align 4, !tbaa !9
  %1796 = zext i8 %1795 to i64
  %1797 = shl nuw nsw i64 %1796, 32
  %1798 = or disjoint i64 %1797, %1793
  %1799 = getelementptr i8, ptr %1736, i64 13
  %1800 = load i8, ptr %1799, align 1, !tbaa !9
  %1801 = zext i8 %1800 to i64
  %1802 = shl nuw nsw i64 %1801, 40
  %1803 = or i64 %1802, %1798
  %1804 = getelementptr i8, ptr %1736, i64 14
  %1805 = load i8, ptr %1804, align 2, !tbaa !9
  %1806 = zext i8 %1805 to i64
  %1807 = shl nuw nsw i64 %1806, 48
  %1808 = or i64 %1807, %1803
  %1809 = getelementptr i8, ptr %1736, i64 15
  %1810 = load i8, ptr %1809, align 1, !tbaa !9
  %1811 = zext i8 %1810 to i64
  %1812 = shl nuw i64 %1811, 56
  %1813 = or i64 %1812, %1808
  %1814 = mul nsw i64 %1728, %1813
  %1815 = ashr i64 %1814, 16
  %1816 = add nsw i64 %1815, %1775
  %1817 = getelementptr i8, ptr %1736, i64 16
  %1818 = load i8, ptr %1817, align 16, !tbaa !9
  %1819 = zext i8 %1818 to i64
  %1820 = getelementptr i8, ptr %1736, i64 17
  %1821 = load i8, ptr %1820, align 1, !tbaa !9
  %1822 = zext i8 %1821 to i64
  %1823 = shl nuw nsw i64 %1822, 8
  %1824 = or disjoint i64 %1823, %1819
  %1825 = getelementptr i8, ptr %1736, i64 18
  %1826 = load i8, ptr %1825, align 2, !tbaa !9
  %1827 = zext i8 %1826 to i64
  %1828 = shl nuw nsw i64 %1827, 16
  %1829 = or disjoint i64 %1828, %1824
  %1830 = getelementptr i8, ptr %1736, i64 19
  %1831 = load i8, ptr %1830, align 1, !tbaa !9
  %1832 = zext i8 %1831 to i64
  %1833 = shl nuw nsw i64 %1832, 24
  %1834 = or disjoint i64 %1833, %1829
  %1835 = getelementptr i8, ptr %1736, i64 20
  %1836 = load i8, ptr %1835, align 4, !tbaa !9
  %1837 = zext i8 %1836 to i64
  %1838 = shl nuw nsw i64 %1837, 32
  %1839 = or disjoint i64 %1838, %1834
  %1840 = getelementptr i8, ptr %1736, i64 21
  %1841 = load i8, ptr %1840, align 1, !tbaa !9
  %1842 = zext i8 %1841 to i64
  %1843 = shl nuw nsw i64 %1842, 40
  %1844 = or i64 %1843, %1839
  %1845 = getelementptr i8, ptr %1736, i64 22
  %1846 = load i8, ptr %1845, align 2, !tbaa !9
  %1847 = zext i8 %1846 to i64
  %1848 = shl nuw nsw i64 %1847, 48
  %1849 = or i64 %1848, %1844
  %1850 = getelementptr i8, ptr %1736, i64 23
  %1851 = load i8, ptr %1850, align 1, !tbaa !9
  %1852 = zext i8 %1851 to i64
  %1853 = shl nuw i64 %1852, 56
  %1854 = or i64 %1853, %1849
  %1855 = mul nsw i64 %1730, %1854
  %1856 = ashr i64 %1855, 16
  %1857 = add nsw i64 %1856, %1816
  %1858 = getelementptr i8, ptr %1736, i64 24
  %1859 = load i8, ptr %1858, align 8, !tbaa !9
  %1860 = getelementptr i8, ptr %1736, i64 25
  %1861 = load i8, ptr %1860, align 1, !tbaa !9
  %1862 = getelementptr i8, ptr %1736, i64 26
  %1863 = load i8, ptr %1862, align 2, !tbaa !9
  %1864 = getelementptr i8, ptr %1736, i64 27
  %1865 = load i8, ptr %1864, align 1, !tbaa !9
  %1866 = getelementptr i8, ptr %1736, i64 28
  %1867 = load i8, ptr %1866, align 4, !tbaa !9
  %1868 = getelementptr i8, ptr %1736, i64 29
  %1869 = load i8, ptr %1868, align 1, !tbaa !9
  %1870 = getelementptr i8, ptr %1736, i64 30
  %1871 = load i8, ptr %1870, align 2, !tbaa !9
  %1872 = getelementptr i8, ptr %1736, i64 31
  %1873 = load i8, ptr %1872, align 1, !tbaa !9
  %1874 = shl nsw i64 %1734, 3
  %1875 = getelementptr inbounds nuw i8, ptr %61, i64 %1874
  %1876 = load i8, ptr %1875, align 8, !tbaa !9
  %1877 = zext i8 %1876 to i64
  %1878 = getelementptr inbounds nuw i8, ptr %1875, i64 1
  %1879 = load i8, ptr %1878, align 1, !tbaa !9
  %1880 = zext i8 %1879 to i64
  %1881 = shl nuw nsw i64 %1880, 8
  %1882 = or disjoint i64 %1881, %1877
  %1883 = getelementptr inbounds nuw i8, ptr %1875, i64 2
  %1884 = load i8, ptr %1883, align 2, !tbaa !9
  %1885 = zext i8 %1884 to i64
  %1886 = shl nuw nsw i64 %1885, 16
  %1887 = or disjoint i64 %1886, %1882
  %1888 = getelementptr inbounds nuw i8, ptr %1875, i64 3
  %1889 = load i8, ptr %1888, align 1, !tbaa !9
  %1890 = zext i8 %1889 to i64
  %1891 = shl nuw nsw i64 %1890, 24
  %1892 = or disjoint i64 %1891, %1887
  %1893 = getelementptr inbounds nuw i8, ptr %1875, i64 4
  %1894 = load i8, ptr %1893, align 4, !tbaa !9
  %1895 = zext i8 %1894 to i64
  %1896 = shl nuw nsw i64 %1895, 32
  %1897 = or disjoint i64 %1896, %1892
  %1898 = getelementptr inbounds nuw i8, ptr %1875, i64 5
  %1899 = load i8, ptr %1898, align 1, !tbaa !9
  %1900 = zext i8 %1899 to i64
  %1901 = shl nuw nsw i64 %1900, 40
  %1902 = or i64 %1901, %1897
  %1903 = getelementptr inbounds nuw i8, ptr %1875, i64 6
  %1904 = load i8, ptr %1903, align 2, !tbaa !9
  %1905 = zext i8 %1904 to i64
  %1906 = shl nuw nsw i64 %1905, 48
  %1907 = or i64 %1906, %1902
  %1908 = getelementptr inbounds nuw i8, ptr %1875, i64 7
  %1909 = load i8, ptr %1908, align 1, !tbaa !9
  %1910 = zext i8 %1909 to i64
  %1911 = shl nuw i64 %1910, 56
  %1912 = or i64 %1911, %1907
  %1913 = zext i8 %1859 to i64
  %1914 = zext i8 %1861 to i64
  %1915 = shl nuw nsw i64 %1914, 8
  %1916 = or disjoint i64 %1915, %1913
  %1917 = zext i8 %1863 to i64
  %1918 = shl nuw nsw i64 %1917, 16
  %1919 = or disjoint i64 %1918, %1916
  %1920 = zext i8 %1865 to i64
  %1921 = shl nuw nsw i64 %1920, 24
  %1922 = or disjoint i64 %1921, %1919
  %1923 = zext i8 %1867 to i64
  %1924 = shl nuw nsw i64 %1923, 32
  %1925 = or disjoint i64 %1924, %1922
  %1926 = zext i8 %1869 to i64
  %1927 = shl nuw nsw i64 %1926, 40
  %1928 = or i64 %1927, %1925
  %1929 = zext i8 %1871 to i64
  %1930 = shl nuw nsw i64 %1929, 48
  %1931 = or i64 %1930, %1928
  %1932 = zext i8 %1873 to i64
  %1933 = shl nuw i64 %1932, 56
  %1934 = or i64 %1933, %1931
  %1935 = mul nsw i64 %1732, %1934
  %1936 = ashr i64 %1935, 16
  %1937 = add nsw i64 %1936, %1857
  %1938 = add nsw i64 %1912, %1937
  %1939 = getelementptr inbounds nuw [8 x i8], ptr %1725, i64 %1734
  store i64 %1938, ptr %1939, align 8, !tbaa !10
  %1940 = add nuw nsw i64 %1734, 1
  %1941 = icmp eq i64 %1940, 4
  br i1 %1941, label %1942, label %1733, !llvm.loop !12

1942:                                             ; preds = %1733
  %1943 = getelementptr inbounds nuw i8, ptr %1724, i64 8
  %1944 = getelementptr inbounds nuw i8, ptr %1724, i64 16
  %1945 = getelementptr inbounds nuw i8, ptr %1724, i64 24
  %1946 = shl nuw nsw i64 %1723, 5
  %1947 = getelementptr inbounds nuw i8, ptr %57, i64 %1946
  %1948 = load i8, ptr %1947, align 16, !tbaa !9
  %1949 = zext i8 %1948 to i64
  %1950 = getelementptr inbounds nuw i8, ptr %1947, i64 1
  %1951 = load i8, ptr %1950, align 1, !tbaa !9
  %1952 = zext i8 %1951 to i64
  %1953 = shl nuw nsw i64 %1952, 8
  %1954 = or disjoint i64 %1953, %1949
  %1955 = getelementptr inbounds nuw i8, ptr %1947, i64 2
  %1956 = load i8, ptr %1955, align 2, !tbaa !9
  %1957 = zext i8 %1956 to i64
  %1958 = shl nuw nsw i64 %1957, 16
  %1959 = or disjoint i64 %1958, %1954
  %1960 = getelementptr inbounds nuw i8, ptr %1947, i64 3
  %1961 = load i8, ptr %1960, align 1, !tbaa !9
  %1962 = zext i8 %1961 to i64
  %1963 = shl nuw nsw i64 %1962, 24
  %1964 = or disjoint i64 %1963, %1959
  %1965 = getelementptr inbounds nuw i8, ptr %1947, i64 4
  %1966 = load i8, ptr %1965, align 4, !tbaa !9
  %1967 = zext i8 %1966 to i64
  %1968 = shl nuw nsw i64 %1967, 32
  %1969 = or disjoint i64 %1968, %1964
  %1970 = getelementptr inbounds nuw i8, ptr %1947, i64 5
  %1971 = load i8, ptr %1970, align 1, !tbaa !9
  %1972 = zext i8 %1971 to i64
  %1973 = shl nuw nsw i64 %1972, 40
  %1974 = or i64 %1973, %1969
  %1975 = getelementptr inbounds nuw i8, ptr %1947, i64 6
  %1976 = load i8, ptr %1975, align 2, !tbaa !9
  %1977 = zext i8 %1976 to i64
  %1978 = shl nuw nsw i64 %1977, 48
  %1979 = or i64 %1978, %1974
  %1980 = getelementptr inbounds nuw i8, ptr %1947, i64 7
  %1981 = load i8, ptr %1980, align 1, !tbaa !9
  %1982 = zext i8 %1981 to i64
  %1983 = shl nuw i64 %1982, 56
  %1984 = or i64 %1983, %1979
  %1985 = shl i64 %1723, 5
  %1986 = getelementptr inbounds nuw [32 x i8], ptr %31, i64 %1723
  %1987 = load i64, ptr %1725, align 16, !tbaa !10
  %1988 = add nsw i64 %1987, %1984
  store i64 %1988, ptr %1986, align 16, !tbaa !10
  %1989 = shl i64 %1723, 5
  %1990 = or disjoint i64 %1989, 8
  %1991 = getelementptr inbounds nuw i8, ptr %57, i64 %1990
  %1992 = load i8, ptr %1991, align 8, !tbaa !9
  %1993 = zext i8 %1992 to i64
  %1994 = getelementptr inbounds nuw i8, ptr %1991, i64 1
  %1995 = load i8, ptr %1994, align 1, !tbaa !9
  %1996 = zext i8 %1995 to i64
  %1997 = shl nuw nsw i64 %1996, 8
  %1998 = or disjoint i64 %1997, %1993
  %1999 = getelementptr inbounds nuw i8, ptr %1991, i64 2
  %2000 = load i8, ptr %1999, align 2, !tbaa !9
  %2001 = zext i8 %2000 to i64
  %2002 = shl nuw nsw i64 %2001, 16
  %2003 = or disjoint i64 %2002, %1998
  %2004 = getelementptr inbounds nuw i8, ptr %1991, i64 3
  %2005 = load i8, ptr %2004, align 1, !tbaa !9
  %2006 = zext i8 %2005 to i64
  %2007 = shl nuw nsw i64 %2006, 24
  %2008 = or disjoint i64 %2007, %2003
  %2009 = getelementptr inbounds nuw i8, ptr %1991, i64 4
  %2010 = load i8, ptr %2009, align 4, !tbaa !9
  %2011 = zext i8 %2010 to i64
  %2012 = shl nuw nsw i64 %2011, 32
  %2013 = or disjoint i64 %2012, %2008
  %2014 = getelementptr inbounds nuw i8, ptr %1991, i64 5
  %2015 = load i8, ptr %2014, align 1, !tbaa !9
  %2016 = zext i8 %2015 to i64
  %2017 = shl nuw nsw i64 %2016, 40
  %2018 = or i64 %2017, %2013
  %2019 = getelementptr inbounds nuw i8, ptr %1991, i64 6
  %2020 = load i8, ptr %2019, align 2, !tbaa !9
  %2021 = zext i8 %2020 to i64
  %2022 = shl nuw nsw i64 %2021, 48
  %2023 = or i64 %2022, %2018
  %2024 = getelementptr inbounds nuw i8, ptr %1991, i64 7
  %2025 = load i8, ptr %2024, align 1, !tbaa !9
  %2026 = zext i8 %2025 to i64
  %2027 = shl nuw i64 %2026, 56
  %2028 = or i64 %2027, %2023
  %2029 = getelementptr inbounds nuw i8, ptr %1725, i64 8
  %2030 = load i64, ptr %2029, align 8, !tbaa !10
  %2031 = add nsw i64 %2030, %2028
  %2032 = getelementptr inbounds nuw i8, ptr %1986, i64 8
  store i64 %2031, ptr %2032, align 8, !tbaa !10
  %2033 = shl i64 %1723, 5
  %2034 = or disjoint i64 %2033, 16
  %2035 = getelementptr inbounds nuw i8, ptr %57, i64 %2034
  %2036 = load i8, ptr %2035, align 16, !tbaa !9
  %2037 = zext i8 %2036 to i64
  %2038 = getelementptr inbounds nuw i8, ptr %2035, i64 1
  %2039 = load i8, ptr %2038, align 1, !tbaa !9
  %2040 = zext i8 %2039 to i64
  %2041 = shl nuw nsw i64 %2040, 8
  %2042 = or disjoint i64 %2041, %2037
  %2043 = getelementptr inbounds nuw i8, ptr %2035, i64 2
  %2044 = load i8, ptr %2043, align 2, !tbaa !9
  %2045 = zext i8 %2044 to i64
  %2046 = shl nuw nsw i64 %2045, 16
  %2047 = or disjoint i64 %2046, %2042
  %2048 = getelementptr inbounds nuw i8, ptr %2035, i64 3
  %2049 = load i8, ptr %2048, align 1, !tbaa !9
  %2050 = zext i8 %2049 to i64
  %2051 = shl nuw nsw i64 %2050, 24
  %2052 = or disjoint i64 %2051, %2047
  %2053 = getelementptr inbounds nuw i8, ptr %2035, i64 4
  %2054 = load i8, ptr %2053, align 4, !tbaa !9
  %2055 = zext i8 %2054 to i64
  %2056 = shl nuw nsw i64 %2055, 32
  %2057 = or disjoint i64 %2056, %2052
  %2058 = getelementptr inbounds nuw i8, ptr %2035, i64 5
  %2059 = load i8, ptr %2058, align 1, !tbaa !9
  %2060 = zext i8 %2059 to i64
  %2061 = shl nuw nsw i64 %2060, 40
  %2062 = or i64 %2061, %2057
  %2063 = getelementptr inbounds nuw i8, ptr %2035, i64 6
  %2064 = load i8, ptr %2063, align 2, !tbaa !9
  %2065 = zext i8 %2064 to i64
  %2066 = shl nuw nsw i64 %2065, 48
  %2067 = or i64 %2066, %2062
  %2068 = getelementptr inbounds nuw i8, ptr %2035, i64 7
  %2069 = load i8, ptr %2068, align 1, !tbaa !9
  %2070 = zext i8 %2069 to i64
  %2071 = shl nuw i64 %2070, 56
  %2072 = or i64 %2071, %2067
  %2073 = getelementptr inbounds nuw i8, ptr %1725, i64 16
  %2074 = load i64, ptr %2073, align 16, !tbaa !10
  %2075 = add nsw i64 %2074, %2072
  %2076 = getelementptr inbounds nuw i8, ptr %1986, i64 16
  store i64 %2075, ptr %2076, align 16, !tbaa !10
  %2077 = or disjoint i64 %1985, 24
  %2078 = getelementptr inbounds nuw i8, ptr %57, i64 %2077
  %2079 = load i8, ptr %2078, align 8, !tbaa !9
  %2080 = zext i8 %2079 to i64
  %2081 = getelementptr inbounds nuw i8, ptr %2078, i64 1
  %2082 = load i8, ptr %2081, align 1, !tbaa !9
  %2083 = zext i8 %2082 to i64
  %2084 = shl nuw nsw i64 %2083, 8
  %2085 = or disjoint i64 %2084, %2080
  %2086 = getelementptr inbounds nuw i8, ptr %2078, i64 2
  %2087 = load i8, ptr %2086, align 2, !tbaa !9
  %2088 = zext i8 %2087 to i64
  %2089 = shl nuw nsw i64 %2088, 16
  %2090 = or disjoint i64 %2089, %2085
  %2091 = getelementptr inbounds nuw i8, ptr %2078, i64 3
  %2092 = load i8, ptr %2091, align 1, !tbaa !9
  %2093 = zext i8 %2092 to i64
  %2094 = shl nuw nsw i64 %2093, 24
  %2095 = or disjoint i64 %2094, %2090
  %2096 = getelementptr inbounds nuw i8, ptr %2078, i64 4
  %2097 = load i8, ptr %2096, align 4, !tbaa !9
  %2098 = zext i8 %2097 to i64
  %2099 = shl nuw nsw i64 %2098, 32
  %2100 = or disjoint i64 %2099, %2095
  %2101 = getelementptr inbounds nuw i8, ptr %2078, i64 5
  %2102 = load i8, ptr %2101, align 1, !tbaa !9
  %2103 = zext i8 %2102 to i64
  %2104 = shl nuw nsw i64 %2103, 40
  %2105 = or i64 %2104, %2100
  %2106 = getelementptr inbounds nuw i8, ptr %2078, i64 6
  %2107 = load i8, ptr %2106, align 2, !tbaa !9
  %2108 = zext i8 %2107 to i64
  %2109 = shl nuw nsw i64 %2108, 48
  %2110 = or i64 %2109, %2105
  %2111 = getelementptr inbounds nuw i8, ptr %2078, i64 7
  %2112 = load i8, ptr %2111, align 1, !tbaa !9
  %2113 = zext i8 %2112 to i64
  %2114 = shl nuw i64 %2113, 56
  %2115 = or i64 %2114, %2110
  %2116 = getelementptr inbounds nuw i8, ptr %1725, i64 24
  %2117 = load i64, ptr %2116, align 8, !tbaa !10
  %2118 = add nsw i64 %2117, %2115
  %2119 = getelementptr inbounds nuw i8, ptr %1986, i64 24
  store i64 %2118, ptr %2119, align 8, !tbaa !10
  call void @llvm.lifetime.start.p0(ptr nonnull %40) #9
  store ptr %1986, ptr %40, align 8, !tbaa !15
  store i64 4, ptr %1629, align 8, !tbaa !19
  store i64 8, ptr %1630, align 8, !tbaa !20
  store i64 8, ptr %1631, align 8, !tbaa !21
  call void @llvm.lifetime.start.p0(ptr nonnull %41) #9
  store ptr %1724, ptr %41, align 8, !tbaa !15
  store i64 4, ptr %1632, align 8, !tbaa !19
  store i64 8, ptr %1633, align 8, !tbaa !20
  store i64 8, ptr %1634, align 8, !tbaa !21
  call fastcc void @layernorm(ptr noundef %40, i64 noundef 4, ptr noundef nonnull readonly %66, ptr noundef nonnull readonly %67, ptr noundef %41)
  %2120 = load i64, ptr %1724, align 16, !tbaa !10
  %2121 = getelementptr inbounds nuw i8, ptr %64, i64 %1946
  %2122 = trunc i64 %2120 to i8
  store i8 %2122, ptr %2121, align 16, !tbaa !9
  %2123 = lshr i64 %2120, 8
  %2124 = trunc i64 %2123 to i8
  %2125 = getelementptr inbounds nuw i8, ptr %2121, i64 1
  store i8 %2124, ptr %2125, align 1, !tbaa !9
  %2126 = lshr i64 %2120, 16
  %2127 = trunc i64 %2126 to i8
  %2128 = getelementptr inbounds nuw i8, ptr %2121, i64 2
  store i8 %2127, ptr %2128, align 2, !tbaa !9
  %2129 = lshr i64 %2120, 24
  %2130 = trunc i64 %2129 to i8
  %2131 = getelementptr inbounds nuw i8, ptr %2121, i64 3
  store i8 %2130, ptr %2131, align 1, !tbaa !9
  %2132 = lshr i64 %2120, 32
  %2133 = trunc i64 %2132 to i8
  %2134 = getelementptr inbounds nuw i8, ptr %2121, i64 4
  store i8 %2133, ptr %2134, align 4, !tbaa !9
  %2135 = lshr i64 %2120, 40
  %2136 = trunc i64 %2135 to i8
  %2137 = getelementptr inbounds nuw i8, ptr %2121, i64 5
  store i8 %2136, ptr %2137, align 1, !tbaa !9
  %2138 = lshr i64 %2120, 48
  %2139 = trunc i64 %2138 to i8
  %2140 = getelementptr inbounds nuw i8, ptr %2121, i64 6
  store i8 %2139, ptr %2140, align 2, !tbaa !9
  %2141 = lshr i64 %2120, 56
  %2142 = trunc nuw i64 %2141 to i8
  %2143 = getelementptr inbounds nuw i8, ptr %2121, i64 7
  store i8 %2142, ptr %2143, align 1, !tbaa !9
  %2144 = load i64, ptr %1943, align 8, !tbaa !10
  %2145 = getelementptr inbounds nuw i8, ptr %64, i64 %1990
  %2146 = trunc i64 %2144 to i8
  store i8 %2146, ptr %2145, align 8, !tbaa !9
  %2147 = lshr i64 %2144, 8
  %2148 = trunc i64 %2147 to i8
  %2149 = getelementptr inbounds nuw i8, ptr %2145, i64 1
  store i8 %2148, ptr %2149, align 1, !tbaa !9
  %2150 = lshr i64 %2144, 16
  %2151 = trunc i64 %2150 to i8
  %2152 = getelementptr inbounds nuw i8, ptr %2145, i64 2
  store i8 %2151, ptr %2152, align 2, !tbaa !9
  %2153 = lshr i64 %2144, 24
  %2154 = trunc i64 %2153 to i8
  %2155 = getelementptr inbounds nuw i8, ptr %2145, i64 3
  store i8 %2154, ptr %2155, align 1, !tbaa !9
  %2156 = lshr i64 %2144, 32
  %2157 = trunc i64 %2156 to i8
  %2158 = getelementptr inbounds nuw i8, ptr %2145, i64 4
  store i8 %2157, ptr %2158, align 4, !tbaa !9
  %2159 = lshr i64 %2144, 40
  %2160 = trunc i64 %2159 to i8
  %2161 = getelementptr inbounds nuw i8, ptr %2145, i64 5
  store i8 %2160, ptr %2161, align 1, !tbaa !9
  %2162 = lshr i64 %2144, 48
  %2163 = trunc i64 %2162 to i8
  %2164 = getelementptr inbounds nuw i8, ptr %2145, i64 6
  store i8 %2163, ptr %2164, align 2, !tbaa !9
  %2165 = lshr i64 %2144, 56
  %2166 = trunc nuw i64 %2165 to i8
  %2167 = getelementptr inbounds nuw i8, ptr %2145, i64 7
  store i8 %2166, ptr %2167, align 1, !tbaa !9
  %2168 = load i64, ptr %1944, align 16, !tbaa !10
  %2169 = getelementptr inbounds nuw i8, ptr %64, i64 %2034
  %2170 = trunc i64 %2168 to i8
  store i8 %2170, ptr %2169, align 16, !tbaa !9
  %2171 = lshr i64 %2168, 8
  %2172 = trunc i64 %2171 to i8
  %2173 = getelementptr inbounds nuw i8, ptr %2169, i64 1
  store i8 %2172, ptr %2173, align 1, !tbaa !9
  %2174 = lshr i64 %2168, 16
  %2175 = trunc i64 %2174 to i8
  %2176 = getelementptr inbounds nuw i8, ptr %2169, i64 2
  store i8 %2175, ptr %2176, align 2, !tbaa !9
  %2177 = lshr i64 %2168, 24
  %2178 = trunc i64 %2177 to i8
  %2179 = getelementptr inbounds nuw i8, ptr %2169, i64 3
  store i8 %2178, ptr %2179, align 1, !tbaa !9
  %2180 = lshr i64 %2168, 32
  %2181 = trunc i64 %2180 to i8
  %2182 = getelementptr inbounds nuw i8, ptr %2169, i64 4
  store i8 %2181, ptr %2182, align 4, !tbaa !9
  %2183 = lshr i64 %2168, 40
  %2184 = trunc i64 %2183 to i8
  %2185 = getelementptr inbounds nuw i8, ptr %2169, i64 5
  store i8 %2184, ptr %2185, align 1, !tbaa !9
  %2186 = lshr i64 %2168, 48
  %2187 = trunc i64 %2186 to i8
  %2188 = getelementptr inbounds nuw i8, ptr %2169, i64 6
  store i8 %2187, ptr %2188, align 2, !tbaa !9
  %2189 = lshr i64 %2168, 56
  %2190 = trunc nuw i64 %2189 to i8
  %2191 = getelementptr inbounds nuw i8, ptr %2169, i64 7
  store i8 %2190, ptr %2191, align 1, !tbaa !9
  %2192 = load i64, ptr %1945, align 8, !tbaa !10
  %2193 = getelementptr inbounds nuw i8, ptr %64, i64 %2077
  %2194 = trunc i64 %2192 to i8
  store i8 %2194, ptr %2193, align 8, !tbaa !9
  %2195 = lshr i64 %2192, 8
  %2196 = trunc i64 %2195 to i8
  %2197 = getelementptr inbounds nuw i8, ptr %2193, i64 1
  store i8 %2196, ptr %2197, align 1, !tbaa !9
  %2198 = lshr i64 %2192, 16
  %2199 = trunc i64 %2198 to i8
  %2200 = getelementptr inbounds nuw i8, ptr %2193, i64 2
  store i8 %2199, ptr %2200, align 2, !tbaa !9
  %2201 = lshr i64 %2192, 24
  %2202 = trunc i64 %2201 to i8
  %2203 = getelementptr inbounds nuw i8, ptr %2193, i64 3
  store i8 %2202, ptr %2203, align 1, !tbaa !9
  %2204 = lshr i64 %2192, 32
  %2205 = trunc i64 %2204 to i8
  %2206 = getelementptr inbounds nuw i8, ptr %2193, i64 4
  store i8 %2205, ptr %2206, align 4, !tbaa !9
  %2207 = lshr i64 %2192, 40
  %2208 = trunc i64 %2207 to i8
  %2209 = getelementptr inbounds nuw i8, ptr %2193, i64 5
  store i8 %2208, ptr %2209, align 1, !tbaa !9
  %2210 = lshr i64 %2192, 48
  %2211 = trunc i64 %2210 to i8
  %2212 = getelementptr inbounds nuw i8, ptr %2193, i64 6
  store i8 %2211, ptr %2212, align 2, !tbaa !9
  %2213 = lshr i64 %2192, 56
  %2214 = trunc nuw i64 %2213 to i8
  %2215 = getelementptr inbounds nuw i8, ptr %2193, i64 7
  store i8 %2214, ptr %2215, align 1, !tbaa !9
  call void @llvm.lifetime.end.p0(ptr nonnull %41) #9
  call void @llvm.lifetime.end.p0(ptr nonnull %40) #9
  %2216 = add nuw nsw i64 %1723, 1
  %2217 = icmp eq i64 %2216, 3
  br i1 %2217, label %2218, label %1722, !llvm.loop !27

2218:                                             ; preds = %1942
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
  store ptr %62, ptr %19, align 8, !tbaa !15
  %2219 = getelementptr inbounds nuw i8, ptr %19, i64 8
  store i64 4, ptr %2219, align 8, !tbaa !19
  %2220 = getelementptr inbounds nuw i8, ptr %19, i64 16
  store i64 8, ptr %2220, align 8, !tbaa !20
  %2221 = getelementptr inbounds nuw i8, ptr %19, i64 24
  store i64 8, ptr %2221, align 8, !tbaa !21
  call void @llvm.lifetime.start.p0(ptr nonnull %20) #9
  store ptr %63, ptr %20, align 8, !tbaa !15
  %2222 = getelementptr inbounds nuw i8, ptr %20, i64 8
  store i64 4, ptr %2222, align 8, !tbaa !19
  %2223 = getelementptr inbounds nuw i8, ptr %20, i64 16
  store i64 8, ptr %2223, align 8, !tbaa !20
  %2224 = getelementptr inbounds nuw i8, ptr %20, i64 24
  store i64 8, ptr %2224, align 8, !tbaa !21
  %2225 = load i64, ptr %58, align 16
  %2226 = getelementptr inbounds nuw i8, ptr %58, i64 8
  %2227 = load i64, ptr %2226, align 8
  %2228 = getelementptr inbounds nuw i8, ptr %58, i64 16
  %2229 = load i64, ptr %2228, align 16
  %2230 = getelementptr inbounds nuw i8, ptr %58, i64 24
  %2231 = load i64, ptr %2230, align 8
  %2232 = getelementptr inbounds nuw i8, ptr %58, i64 32
  %2233 = load i64, ptr %2232, align 16
  %2234 = getelementptr inbounds nuw i8, ptr %58, i64 40
  %2235 = load i64, ptr %2234, align 8
  %2236 = getelementptr inbounds nuw i8, ptr %58, i64 48
  %2237 = load i64, ptr %2236, align 16
  %2238 = getelementptr inbounds nuw i8, ptr %58, i64 56
  %2239 = load i64, ptr %2238, align 8
  %2240 = getelementptr inbounds nuw i8, ptr %58, i64 64
  %2241 = load i64, ptr %2240, align 16
  %2242 = getelementptr inbounds nuw i8, ptr %58, i64 72
  %2243 = load i64, ptr %2242, align 8
  %2244 = getelementptr inbounds nuw i8, ptr %58, i64 80
  %2245 = load i64, ptr %2244, align 16
  %2246 = getelementptr inbounds nuw i8, ptr %58, i64 88
  %2247 = load i64, ptr %2246, align 8
  %2248 = getelementptr inbounds nuw i8, ptr %58, i64 96
  %2249 = load i64, ptr %2248, align 16
  %2250 = getelementptr inbounds nuw i8, ptr %58, i64 104
  %2251 = load i64, ptr %2250, align 8
  %2252 = getelementptr inbounds nuw i8, ptr %58, i64 112
  %2253 = load i64, ptr %2252, align 16
  %2254 = getelementptr inbounds nuw i8, ptr %58, i64 120
  %2255 = load i64, ptr %2254, align 8
  %2256 = load i64, ptr %511, align 16
  %2257 = getelementptr inbounds nuw i8, ptr %58, i64 136
  %2258 = load i64, ptr %2257, align 8
  %2259 = getelementptr inbounds nuw i8, ptr %58, i64 144
  %2260 = load i64, ptr %2259, align 16
  %2261 = getelementptr inbounds nuw i8, ptr %58, i64 152
  %2262 = load i64, ptr %2261, align 8
  %2263 = getelementptr inbounds nuw i8, ptr %58, i64 160
  %2264 = load i64, ptr %2263, align 16
  %2265 = getelementptr inbounds nuw i8, ptr %58, i64 168
  %2266 = load i64, ptr %2265, align 8
  %2267 = getelementptr inbounds nuw i8, ptr %58, i64 176
  %2268 = load i64, ptr %2267, align 16
  %2269 = getelementptr inbounds nuw i8, ptr %58, i64 184
  %2270 = load i64, ptr %2269, align 8
  %2271 = getelementptr inbounds nuw i8, ptr %58, i64 192
  %2272 = load i64, ptr %2271, align 16
  %2273 = getelementptr inbounds nuw i8, ptr %58, i64 200
  %2274 = load i64, ptr %2273, align 8
  %2275 = getelementptr inbounds nuw i8, ptr %58, i64 208
  %2276 = load i64, ptr %2275, align 16
  %2277 = getelementptr inbounds nuw i8, ptr %58, i64 216
  %2278 = load i64, ptr %2277, align 8
  %2279 = getelementptr inbounds nuw i8, ptr %58, i64 224
  %2280 = load i64, ptr %2279, align 16
  %2281 = getelementptr inbounds nuw i8, ptr %58, i64 232
  %2282 = load i64, ptr %2281, align 8
  %2283 = getelementptr inbounds nuw i8, ptr %58, i64 240
  %2284 = load i64, ptr %2283, align 16
  %2285 = getelementptr inbounds nuw i8, ptr %58, i64 248
  %2286 = load i64, ptr %2285, align 8
  %2287 = load i64, ptr %512, align 16
  %2288 = getelementptr inbounds nuw i8, ptr %58, i64 264
  %2289 = load i64, ptr %2288, align 8
  %2290 = getelementptr inbounds nuw i8, ptr %58, i64 272
  %2291 = load i64, ptr %2290, align 16
  %2292 = getelementptr inbounds nuw i8, ptr %58, i64 280
  %2293 = load i64, ptr %2292, align 8
  %2294 = getelementptr inbounds nuw i8, ptr %58, i64 288
  %2295 = load i64, ptr %2294, align 16
  %2296 = getelementptr inbounds nuw i8, ptr %58, i64 296
  %2297 = load i64, ptr %2296, align 8
  %2298 = getelementptr inbounds nuw i8, ptr %58, i64 304
  %2299 = load i64, ptr %2298, align 16
  %2300 = getelementptr inbounds nuw i8, ptr %58, i64 312
  %2301 = load i64, ptr %2300, align 8
  %2302 = getelementptr inbounds nuw i8, ptr %58, i64 320
  %2303 = load i64, ptr %2302, align 16
  %2304 = getelementptr inbounds nuw i8, ptr %58, i64 328
  %2305 = load i64, ptr %2304, align 8
  %2306 = getelementptr inbounds nuw i8, ptr %58, i64 336
  %2307 = load i64, ptr %2306, align 16
  %2308 = getelementptr inbounds nuw i8, ptr %58, i64 344
  %2309 = load i64, ptr %2308, align 8
  %2310 = getelementptr inbounds nuw i8, ptr %58, i64 352
  %2311 = load i64, ptr %2310, align 16
  %2312 = getelementptr inbounds nuw i8, ptr %58, i64 360
  %2313 = load i64, ptr %2312, align 8
  %2314 = getelementptr inbounds nuw i8, ptr %58, i64 368
  %2315 = load i64, ptr %2314, align 16
  %2316 = getelementptr inbounds nuw i8, ptr %58, i64 376
  %2317 = load i64, ptr %2316, align 8
  br label %2375

2318:                                             ; preds = %2375
  %2319 = getelementptr inbounds nuw i8, ptr %23, i64 8
  %2320 = getelementptr inbounds nuw i8, ptr %23, i64 16
  %2321 = getelementptr inbounds nuw i8, ptr %23, i64 24
  %2322 = getelementptr inbounds nuw i8, ptr %24, i64 8
  %2323 = getelementptr inbounds nuw i8, ptr %24, i64 16
  %2324 = getelementptr inbounds nuw i8, ptr %24, i64 24
  %2325 = load i64, ptr %16, align 16, !tbaa !10
  %2326 = getelementptr inbounds nuw i8, ptr %16, i64 32
  %2327 = load i64, ptr %2326, align 16, !tbaa !10
  %2328 = getelementptr inbounds nuw i8, ptr %16, i64 64
  %2329 = load i64, ptr %2328, align 16, !tbaa !10
  %2330 = load i64, ptr %15, align 16, !tbaa !10
  %2331 = getelementptr inbounds nuw i8, ptr %15, i64 8
  %2332 = load i64, ptr %2331, align 8, !tbaa !10
  %2333 = getelementptr inbounds nuw i8, ptr %15, i64 16
  %2334 = load i64, ptr %2333, align 16, !tbaa !10
  %2335 = getelementptr inbounds nuw i8, ptr %15, i64 24
  %2336 = load i64, ptr %2335, align 8, !tbaa !10
  %2337 = getelementptr inbounds nuw i8, ptr %15, i64 32
  %2338 = load i64, ptr %2337, align 16, !tbaa !10
  %2339 = getelementptr inbounds nuw i8, ptr %15, i64 40
  %2340 = load i64, ptr %2339, align 8, !tbaa !10
  %2341 = getelementptr inbounds nuw i8, ptr %15, i64 48
  %2342 = load i64, ptr %2341, align 16, !tbaa !10
  %2343 = getelementptr inbounds nuw i8, ptr %15, i64 56
  %2344 = load i64, ptr %2343, align 8, !tbaa !10
  %2345 = getelementptr inbounds nuw i8, ptr %21, i64 8
  %2346 = getelementptr inbounds nuw i8, ptr %15, i64 64
  %2347 = load i64, ptr %2346, align 16, !tbaa !10
  %2348 = getelementptr inbounds nuw i8, ptr %15, i64 72
  %2349 = load i64, ptr %2348, align 8, !tbaa !10
  %2350 = getelementptr inbounds nuw i8, ptr %15, i64 80
  %2351 = load i64, ptr %2350, align 16, !tbaa !10
  %2352 = getelementptr inbounds nuw i8, ptr %15, i64 88
  %2353 = load i64, ptr %2352, align 8, !tbaa !10
  %2354 = getelementptr inbounds nuw i8, ptr %21, i64 16
  %2355 = getelementptr inbounds nuw i8, ptr %22, i64 8
  %2356 = getelementptr inbounds nuw i8, ptr %22, i64 16
  %2357 = getelementptr inbounds nuw i8, ptr %16, i64 8
  %2358 = load i64, ptr %2357, align 8
  %2359 = getelementptr inbounds nuw i8, ptr %16, i64 40
  %2360 = load i64, ptr %2359, align 8
  %2361 = getelementptr inbounds nuw i8, ptr %16, i64 72
  %2362 = load i64, ptr %2361, align 8
  %2363 = getelementptr inbounds nuw i8, ptr %16, i64 16
  %2364 = load i64, ptr %2363, align 16
  %2365 = getelementptr inbounds nuw i8, ptr %16, i64 48
  %2366 = load i64, ptr %2365, align 16
  %2367 = getelementptr inbounds nuw i8, ptr %16, i64 80
  %2368 = load i64, ptr %2367, align 16
  %2369 = getelementptr inbounds nuw i8, ptr %16, i64 24
  %2370 = load i64, ptr %2369, align 8
  %2371 = getelementptr inbounds nuw i8, ptr %16, i64 56
  %2372 = load i64, ptr %2371, align 8
  %2373 = getelementptr inbounds nuw i8, ptr %16, i64 88
  %2374 = load i64, ptr %2373, align 8
  br label %2559

2375:                                             ; preds = %2375, %2218
  %2376 = phi i64 [ 0, %2218 ], [ %2550, %2375 ]
  %2377 = shl nuw nsw i64 %2376, 5
  %2378 = getelementptr inbounds nuw i8, ptr %57, i64 %2377
  %2379 = load i64, ptr %2378, align 16
  %2380 = mul nsw i64 %2379, %2225
  %2381 = ashr i64 %2380, 16
  %2382 = getelementptr inbounds nuw i8, ptr %2378, i64 8
  %2383 = load i64, ptr %2382, align 8
  %2384 = mul nsw i64 %2383, %2227
  %2385 = ashr i64 %2384, 16
  %2386 = add nsw i64 %2385, %2381
  %2387 = getelementptr inbounds nuw i8, ptr %2378, i64 16
  %2388 = load i64, ptr %2387, align 16
  %2389 = mul nsw i64 %2388, %2229
  %2390 = ashr i64 %2389, 16
  %2391 = add nsw i64 %2390, %2386
  %2392 = getelementptr inbounds nuw i8, ptr %2378, i64 24
  %2393 = load i64, ptr %2392, align 8
  %2394 = mul nsw i64 %2393, %2231
  %2395 = ashr i64 %2394, 16
  %2396 = add nsw i64 %2395, %2391
  %2397 = add nsw i64 %2396, -1600
  %2398 = mul nsw i64 %2379, %2233
  %2399 = ashr i64 %2398, 16
  %2400 = mul nsw i64 %2383, %2235
  %2401 = ashr i64 %2400, 16
  %2402 = add nsw i64 %2401, %2399
  %2403 = mul nsw i64 %2388, %2237
  %2404 = ashr i64 %2403, 16
  %2405 = add nsw i64 %2404, %2402
  %2406 = mul nsw i64 %2393, %2239
  %2407 = ashr i64 %2406, 16
  %2408 = add nsw i64 %2407, %2405
  %2409 = add nsw i64 %2408, -1152
  %2410 = mul nsw i64 %2379, %2241
  %2411 = ashr i64 %2410, 16
  %2412 = mul nsw i64 %2383, %2243
  %2413 = ashr i64 %2412, 16
  %2414 = add nsw i64 %2413, %2411
  %2415 = mul nsw i64 %2388, %2245
  %2416 = ashr i64 %2415, 16
  %2417 = add nsw i64 %2416, %2414
  %2418 = mul nsw i64 %2393, %2247
  %2419 = ashr i64 %2418, 16
  %2420 = add nsw i64 %2419, %2417
  %2421 = add nsw i64 %2420, -704
  %2422 = mul nsw i64 %2379, %2249
  %2423 = ashr i64 %2422, 16
  %2424 = mul nsw i64 %2383, %2251
  %2425 = ashr i64 %2424, 16
  %2426 = add nsw i64 %2425, %2423
  %2427 = mul nsw i64 %2388, %2253
  %2428 = ashr i64 %2427, 16
  %2429 = add nsw i64 %2428, %2426
  %2430 = mul nsw i64 %2393, %2255
  %2431 = ashr i64 %2430, 16
  %2432 = add nsw i64 %2431, %2429
  %2433 = add nsw i64 %2432, -256
  %2434 = mul nsw i64 %2379, %2256
  %2435 = ashr i64 %2434, 16
  %2436 = mul nsw i64 %2383, %2258
  %2437 = ashr i64 %2436, 16
  %2438 = add nsw i64 %2437, %2435
  %2439 = mul nsw i64 %2388, %2260
  %2440 = ashr i64 %2439, 16
  %2441 = add nsw i64 %2440, %2438
  %2442 = mul nsw i64 %2393, %2262
  %2443 = ashr i64 %2442, 16
  %2444 = add nsw i64 %2443, %2441
  %2445 = add nsw i64 %2444, 192
  %2446 = load i64, ptr %2378, align 16
  %2447 = mul nsw i64 %2446, %2264
  %2448 = ashr i64 %2447, 16
  %2449 = load i64, ptr %2382, align 8
  %2450 = mul nsw i64 %2449, %2266
  %2451 = ashr i64 %2450, 16
  %2452 = add nsw i64 %2451, %2448
  %2453 = load i64, ptr %2387, align 16
  %2454 = mul nsw i64 %2453, %2268
  %2455 = ashr i64 %2454, 16
  %2456 = add nsw i64 %2455, %2452
  %2457 = load i64, ptr %2392, align 8
  %2458 = mul nsw i64 %2457, %2270
  %2459 = ashr i64 %2458, 16
  %2460 = add nsw i64 %2459, %2456
  %2461 = add nsw i64 %2460, 640
  %2462 = mul nsw i64 %2446, %2272
  %2463 = ashr i64 %2462, 16
  %2464 = mul nsw i64 %2449, %2274
  %2465 = ashr i64 %2464, 16
  %2466 = add nsw i64 %2465, %2463
  %2467 = mul nsw i64 %2453, %2276
  %2468 = ashr i64 %2467, 16
  %2469 = add nsw i64 %2468, %2466
  %2470 = mul nsw i64 %2457, %2278
  %2471 = ashr i64 %2470, 16
  %2472 = add nsw i64 %2471, %2469
  %2473 = add nsw i64 %2472, 1088
  %2474 = mul nsw i64 %2446, %2280
  %2475 = ashr i64 %2474, 16
  %2476 = mul nsw i64 %2449, %2282
  %2477 = ashr i64 %2476, 16
  %2478 = add nsw i64 %2477, %2475
  %2479 = mul nsw i64 %2453, %2284
  %2480 = ashr i64 %2479, 16
  %2481 = add nsw i64 %2480, %2478
  %2482 = mul nsw i64 %2457, %2286
  %2483 = ashr i64 %2482, 16
  %2484 = add nsw i64 %2483, %2481
  %2485 = add nsw i64 %2484, 1536
  %2486 = mul nsw i64 %2446, %2287
  %2487 = ashr i64 %2486, 16
  %2488 = mul nsw i64 %2449, %2289
  %2489 = ashr i64 %2488, 16
  %2490 = add nsw i64 %2489, %2487
  %2491 = mul nsw i64 %2453, %2291
  %2492 = ashr i64 %2491, 16
  %2493 = add nsw i64 %2492, %2490
  %2494 = mul nsw i64 %2457, %2293
  %2495 = ashr i64 %2494, 16
  %2496 = add nsw i64 %2495, %2493
  %2497 = add nsw i64 %2496, -1216
  %2498 = mul nsw i64 %2446, %2295
  %2499 = ashr i64 %2498, 16
  %2500 = mul nsw i64 %2449, %2297
  %2501 = ashr i64 %2500, 16
  %2502 = add nsw i64 %2501, %2499
  %2503 = mul nsw i64 %2453, %2299
  %2504 = ashr i64 %2503, 16
  %2505 = add nsw i64 %2504, %2502
  %2506 = mul nsw i64 %2457, %2301
  %2507 = ashr i64 %2506, 16
  %2508 = add nsw i64 %2507, %2505
  %2509 = add nsw i64 %2508, -768
  %2510 = load i64, ptr %2378, align 16
  %2511 = mul nsw i64 %2510, %2303
  %2512 = ashr i64 %2511, 16
  %2513 = load i64, ptr %2382, align 8
  %2514 = mul nsw i64 %2513, %2305
  %2515 = ashr i64 %2514, 16
  %2516 = add nsw i64 %2515, %2512
  %2517 = load i64, ptr %2387, align 16
  %2518 = mul nsw i64 %2517, %2307
  %2519 = ashr i64 %2518, 16
  %2520 = add nsw i64 %2519, %2516
  %2521 = load i64, ptr %2392, align 8
  %2522 = mul nsw i64 %2521, %2309
  %2523 = ashr i64 %2522, 16
  %2524 = add nsw i64 %2523, %2520
  %2525 = add nsw i64 %2524, -320
  %2526 = mul nsw i64 %2510, %2311
  %2527 = ashr i64 %2526, 16
  %2528 = mul nsw i64 %2513, %2313
  %2529 = ashr i64 %2528, 16
  %2530 = add nsw i64 %2529, %2527
  %2531 = mul nsw i64 %2517, %2315
  %2532 = ashr i64 %2531, 16
  %2533 = add nsw i64 %2532, %2530
  %2534 = mul nsw i64 %2521, %2317
  %2535 = ashr i64 %2534, 16
  %2536 = add nsw i64 %2535, %2533
  %2537 = add nsw i64 %2536, 128
  %2538 = getelementptr i8, ptr %16, i64 %2377
  %2539 = getelementptr i8, ptr %15, i64 %2377
  %2540 = getelementptr i8, ptr %14, i64 %2377
  store i64 %2397, ptr %2540, align 16, !tbaa !10
  %2541 = getelementptr inbounds nuw i8, ptr %2540, i64 8
  store i64 %2409, ptr %2541, align 8, !tbaa !10
  %2542 = getelementptr inbounds nuw i8, ptr %2540, i64 16
  store i64 %2421, ptr %2542, align 16, !tbaa !10
  %2543 = getelementptr inbounds nuw i8, ptr %2540, i64 24
  store i64 %2433, ptr %2543, align 8, !tbaa !10
  store i64 %2445, ptr %2539, align 16, !tbaa !10
  %2544 = getelementptr inbounds nuw i8, ptr %2539, i64 8
  store i64 %2461, ptr %2544, align 8, !tbaa !10
  %2545 = getelementptr inbounds nuw i8, ptr %2539, i64 16
  store i64 %2473, ptr %2545, align 16, !tbaa !10
  %2546 = getelementptr inbounds nuw i8, ptr %2539, i64 24
  store i64 %2485, ptr %2546, align 8, !tbaa !10
  store i64 %2497, ptr %2538, align 16, !tbaa !10
  %2547 = getelementptr inbounds nuw i8, ptr %2538, i64 8
  store i64 %2509, ptr %2547, align 8, !tbaa !10
  %2548 = getelementptr inbounds nuw i8, ptr %2538, i64 16
  store i64 %2525, ptr %2548, align 16, !tbaa !10
  %2549 = getelementptr inbounds nuw i8, ptr %2538, i64 24
  store i64 %2537, ptr %2549, align 8, !tbaa !10
  %2550 = add nuw nsw i64 %2376, 1
  %2551 = icmp eq i64 %2550, 3
  br i1 %2551, label %2318, label %2375, !llvm.loop !28

2552:                                             ; preds = %2559
  %2553 = getelementptr inbounds nuw i8, ptr %25, i64 8
  %2554 = getelementptr inbounds nuw i8, ptr %25, i64 16
  %2555 = getelementptr inbounds nuw i8, ptr %25, i64 24
  %2556 = getelementptr inbounds nuw i8, ptr %26, i64 8
  %2557 = getelementptr inbounds nuw i8, ptr %26, i64 16
  %2558 = getelementptr inbounds nuw i8, ptr %26, i64 24
  br label %2646

2559:                                             ; preds = %2559, %2318
  %2560 = phi i64 [ 0, %2318 ], [ %2644, %2559 ]
  call void @llvm.lifetime.start.p0(ptr nonnull %21) #9
  call void @llvm.lifetime.start.p0(ptr nonnull %22) #9
  %2561 = getelementptr inbounds nuw [32 x i8], ptr %14, i64 %2560
  %2562 = load i64, ptr %2561, align 16, !tbaa !10
  %2563 = getelementptr inbounds nuw i8, ptr %2561, i64 8
  %2564 = load i64, ptr %2563, align 8, !tbaa !10
  %2565 = getelementptr inbounds nuw i8, ptr %2561, i64 16
  %2566 = load i64, ptr %2565, align 16, !tbaa !10
  %2567 = getelementptr inbounds nuw i8, ptr %2561, i64 24
  %2568 = load i64, ptr %2567, align 8, !tbaa !10
  %2569 = mul nsw i64 %2562, %2330
  %2570 = and i64 %2569, -65536
  %2571 = mul nsw i64 %2564, %2332
  %2572 = and i64 %2571, -65536
  %2573 = add i64 %2572, %2570
  %2574 = mul nsw i64 %2566, %2334
  %2575 = and i64 %2574, -65536
  %2576 = add i64 %2573, %2575
  %2577 = mul nsw i64 %2568, %2336
  %2578 = add i64 %2576, %2577
  %2579 = and i64 %2578, -65536
  %2580 = sdiv i64 %2579, 131072
  store i64 %2580, ptr %21, align 16, !tbaa !10
  %2581 = mul nsw i64 %2562, %2338
  %2582 = and i64 %2581, -65536
  %2583 = mul nsw i64 %2564, %2340
  %2584 = and i64 %2583, -65536
  %2585 = add i64 %2584, %2582
  %2586 = mul nsw i64 %2566, %2342
  %2587 = and i64 %2586, -65536
  %2588 = add i64 %2585, %2587
  %2589 = mul nsw i64 %2568, %2344
  %2590 = add i64 %2588, %2589
  %2591 = and i64 %2590, -65536
  %2592 = sdiv i64 %2591, 131072
  store i64 %2592, ptr %2345, align 8, !tbaa !10
  %2593 = mul nsw i64 %2562, %2347
  %2594 = and i64 %2593, -65536
  %2595 = mul nsw i64 %2564, %2349
  %2596 = and i64 %2595, -65536
  %2597 = add i64 %2596, %2594
  %2598 = mul nsw i64 %2566, %2351
  %2599 = and i64 %2598, -65536
  %2600 = add i64 %2597, %2599
  %2601 = mul nsw i64 %2568, %2353
  %2602 = add i64 %2600, %2601
  %2603 = and i64 %2602, -65536
  %2604 = sdiv i64 %2603, 131072
  store i64 %2604, ptr %2354, align 16, !tbaa !10
  call void @llvm.lifetime.start.p0(ptr nonnull %23) #9
  store ptr %21, ptr %23, align 8, !tbaa !15
  store i64 3, ptr %2319, align 8, !tbaa !19
  store i64 8, ptr %2320, align 8, !tbaa !20
  store i64 8, ptr %2321, align 8, !tbaa !21
  call void @llvm.lifetime.start.p0(ptr nonnull %24) #9
  store ptr %22, ptr %24, align 8, !tbaa !15
  store i64 3, ptr %2322, align 8, !tbaa !19
  store i64 8, ptr %2323, align 8, !tbaa !20
  store i64 8, ptr %2324, align 8, !tbaa !21
  call fastcc void @softmax(ptr noundef %23, ptr noundef %24)
  %2605 = getelementptr inbounds nuw [32 x i8], ptr %17, i64 %2560
  %2606 = load i64, ptr %22, align 16, !tbaa !10
  %2607 = mul nsw i64 %2606, %2325
  %2608 = ashr i64 %2607, 16
  %2609 = load i64, ptr %2355, align 8, !tbaa !10
  %2610 = mul nsw i64 %2609, %2327
  %2611 = ashr i64 %2610, 16
  %2612 = add nsw i64 %2611, %2608
  %2613 = load i64, ptr %2356, align 16, !tbaa !10
  %2614 = mul nsw i64 %2613, %2329
  %2615 = ashr i64 %2614, 16
  %2616 = add nsw i64 %2612, %2615
  store i64 %2616, ptr %2605, align 16, !tbaa !10
  %2617 = mul nsw i64 %2606, %2358
  %2618 = ashr i64 %2617, 16
  %2619 = mul nsw i64 %2609, %2360
  %2620 = ashr i64 %2619, 16
  %2621 = add nsw i64 %2620, %2618
  %2622 = mul nsw i64 %2613, %2362
  %2623 = ashr i64 %2622, 16
  %2624 = add nsw i64 %2621, %2623
  %2625 = getelementptr inbounds nuw i8, ptr %2605, i64 8
  store i64 %2624, ptr %2625, align 8, !tbaa !10
  %2626 = mul nsw i64 %2606, %2364
  %2627 = ashr i64 %2626, 16
  %2628 = mul nsw i64 %2609, %2366
  %2629 = ashr i64 %2628, 16
  %2630 = add nsw i64 %2629, %2627
  %2631 = mul nsw i64 %2613, %2368
  %2632 = ashr i64 %2631, 16
  %2633 = add nsw i64 %2630, %2632
  %2634 = getelementptr inbounds nuw i8, ptr %2605, i64 16
  store i64 %2633, ptr %2634, align 16, !tbaa !10
  %2635 = mul nsw i64 %2606, %2370
  %2636 = ashr i64 %2635, 16
  %2637 = mul nsw i64 %2609, %2372
  %2638 = ashr i64 %2637, 16
  %2639 = add nsw i64 %2638, %2636
  %2640 = mul nsw i64 %2613, %2374
  %2641 = ashr i64 %2640, 16
  %2642 = add nsw i64 %2639, %2641
  %2643 = getelementptr inbounds nuw i8, ptr %2605, i64 24
  store i64 %2642, ptr %2643, align 8, !tbaa !10
  call void @llvm.lifetime.end.p0(ptr nonnull %24) #9
  call void @llvm.lifetime.end.p0(ptr nonnull %23) #9
  call void @llvm.lifetime.end.p0(ptr nonnull %22) #9
  call void @llvm.lifetime.end.p0(ptr nonnull %21) #9
  %2644 = add nuw nsw i64 %2560, 1
  %2645 = icmp eq i64 %2644, 3
  br i1 %2645, label %2552, label %2559, !llvm.loop !29

2646:                                             ; preds = %2646, %2552
  %2647 = phi i64 [ 0, %2552 ], [ %2718, %2646 ]
  %2648 = getelementptr inbounds nuw [32 x i8], ptr %17, i64 %2647
  %2649 = load i64, ptr %2648, align 16
  %2650 = mul nsw i64 %2649, -12800
  %2651 = ashr i64 %2650, 16
  %2652 = getelementptr inbounds nuw i8, ptr %2648, i64 8
  %2653 = load i64, ptr %2652, align 8
  %2654 = mul nsw i64 %2653, -11392
  %2655 = ashr i64 %2654, 16
  %2656 = add nsw i64 %2655, %2651
  %2657 = getelementptr inbounds nuw i8, ptr %2648, i64 16
  %2658 = load i64, ptr %2657, align 16
  %2659 = mul nsw i64 %2658, -9984
  %2660 = ashr i64 %2659, 16
  %2661 = add nsw i64 %2660, %2656
  %2662 = getelementptr inbounds nuw i8, ptr %2648, i64 24
  %2663 = load i64, ptr %2662, align 8
  %2664 = mul nsw i64 %2663, -8576
  %2665 = ashr i64 %2664, 16
  %2666 = add nsw i64 %2665, %2661
  %2667 = ashr i64 %2649, 4
  %2668 = mul nsw i64 %2653, 5504
  %2669 = ashr i64 %2668, 16
  %2670 = add nsw i64 %2669, %2667
  %2671 = mul nsw i64 %2658, 6912
  %2672 = ashr i64 %2671, 16
  %2673 = add nsw i64 %2672, %2670
  %2674 = mul nsw i64 %2663, 8320
  %2675 = ashr i64 %2674, 16
  %2676 = add nsw i64 %2675, %2673
  %2677 = add nsw i64 %2676, 30
  %2678 = shl nuw nsw i64 %2647, 5
  %2679 = getelementptr i8, ptr %65, i64 %2678
  %2680 = getelementptr nuw i8, ptr %17, i64 %2678
  %2681 = getelementptr inbounds nuw [32 x i8], ptr %18, i64 %2647
  %2682 = getelementptr inbounds nuw i8, ptr %57, i64 %2678
  %2683 = load i64, ptr %2682, align 16, !tbaa !10
  %2684 = add nsw i64 %2666, %2683
  store i64 %2684, ptr %2681, align 16, !tbaa !10
  %2685 = getelementptr inbounds nuw i8, ptr %2682, i64 8
  %2686 = getelementptr inbounds nuw i8, ptr %2681, i64 8
  %2687 = mul nsw i64 %2649, -1536
  %2688 = mul nsw i64 %2649, -7168
  %2689 = ashr i64 %2687, 16
  %2690 = ashr i64 %2688, 16
  %2691 = mul nsw i64 %2653, -128
  %2692 = mul nsw i64 %2653, -5760
  %2693 = ashr i64 %2691, 16
  %2694 = ashr i64 %2692, 16
  %2695 = add nsw i64 %2693, %2689
  %2696 = add nsw i64 %2694, %2690
  %2697 = mul nsw i64 %2658, 1280
  %2698 = mul nsw i64 %2658, -4352
  %2699 = ashr i64 %2697, 16
  %2700 = ashr i64 %2698, 16
  %2701 = add nsw i64 %2699, %2695
  %2702 = add nsw i64 %2700, %2696
  %2703 = mul nsw i64 %2663, 2688
  %2704 = mul nsw i64 %2663, -2944
  %2705 = ashr i64 %2703, 16
  %2706 = ashr i64 %2704, 16
  %2707 = add nsw i64 %2705, %2701
  %2708 = add nsw i64 %2706, %2702
  %2709 = insertelement <2 x i64> poison, i64 %2708, i64 0
  %2710 = insertelement <2 x i64> %2709, i64 %2707, i64 1
  %2711 = add nsw <2 x i64> %2710, <i64 10, i64 20>
  %2712 = load <2 x i64>, ptr %2685, align 8, !tbaa !10
  %2713 = add nsw <2 x i64> %2711, %2712
  store <2 x i64> %2713, ptr %2686, align 8, !tbaa !10
  %2714 = getelementptr inbounds nuw i8, ptr %2682, i64 24
  %2715 = load i64, ptr %2714, align 8, !tbaa !10
  %2716 = add nsw i64 %2677, %2715
  %2717 = getelementptr inbounds nuw i8, ptr %2681, i64 24
  store i64 %2716, ptr %2717, align 8, !tbaa !10
  call void @llvm.lifetime.start.p0(ptr nonnull %25) #9
  store ptr %2681, ptr %25, align 8, !tbaa !15
  store i64 4, ptr %2553, align 8, !tbaa !19
  store i64 8, ptr %2554, align 8, !tbaa !20
  store i64 8, ptr %2555, align 8, !tbaa !21
  call void @llvm.lifetime.start.p0(ptr nonnull %26) #9
  store ptr %2648, ptr %26, align 8, !tbaa !15
  store i64 4, ptr %2556, align 8, !tbaa !19
  store i64 8, ptr %2557, align 8, !tbaa !20
  store i64 8, ptr %2558, align 8, !tbaa !21
  call fastcc void @layernorm(ptr noundef %25, i64 noundef 4, ptr noundef %19, ptr noundef %20, ptr noundef %26)
  call void @llvm.memcpy.p0.p0.i64(ptr noundef nonnull align 16 dereferenceable(32) %2679, ptr noundef nonnull align 16 dereferenceable(32) %2680, i64 32, i1 false), !tbaa !10
  call void @llvm.lifetime.end.p0(ptr nonnull %26) #9
  call void @llvm.lifetime.end.p0(ptr nonnull %25) #9
  %2718 = add nuw nsw i64 %2647, 1
  %2719 = icmp eq i64 %2718, 3
  br i1 %2719, label %2720, label %2646, !llvm.loop !30

2720:                                             ; preds = %2646
  call void @llvm.lifetime.end.p0(ptr nonnull %20) #9
  call void @llvm.lifetime.end.p0(ptr nonnull %19) #9
  call void @llvm.lifetime.end.p0(ptr nonnull %18) #9
  call void @llvm.lifetime.end.p0(ptr nonnull %17) #9
  call void @llvm.lifetime.end.p0(ptr nonnull %16) #9
  call void @llvm.lifetime.end.p0(ptr nonnull %15) #9
  call void @llvm.lifetime.end.p0(ptr nonnull %14) #9
  %2721 = load i64, ptr %64, align 16, !tbaa !10
  %2722 = load i64, ptr %65, align 16, !tbaa !10
  %2723 = icmp eq i64 %2721, %2722
  br i1 %2723, label %3174, label %3172

2724:                                             ; preds = %3277, %2793
  %2725 = phi i64 [ %2832, %2793 ], [ %3565, %3277 ]
  %2726 = phi i64 [ %2794, %2793 ], [ 0, %3277 ]
  %2727 = shl nsw i64 %2725, 3
  %2728 = getelementptr inbounds nuw i8, ptr %76, i64 %2727
  %2729 = load i8, ptr %2728, align 8, !tbaa !9
  %2730 = zext i8 %2729 to i64
  %2731 = getelementptr inbounds nuw i8, ptr %2728, i64 1
  %2732 = load i8, ptr %2731, align 1, !tbaa !9
  %2733 = zext i8 %2732 to i64
  %2734 = shl nuw nsw i64 %2733, 8
  %2735 = or disjoint i64 %2734, %2730
  %2736 = getelementptr inbounds nuw i8, ptr %2728, i64 2
  %2737 = load i8, ptr %2736, align 2, !tbaa !9
  %2738 = zext i8 %2737 to i64
  %2739 = shl nuw nsw i64 %2738, 16
  %2740 = or disjoint i64 %2739, %2735
  %2741 = getelementptr inbounds nuw i8, ptr %2728, i64 3
  %2742 = load i8, ptr %2741, align 1, !tbaa !9
  %2743 = zext i8 %2742 to i64
  %2744 = shl nuw nsw i64 %2743, 24
  %2745 = or disjoint i64 %2744, %2740
  %2746 = getelementptr inbounds nuw i8, ptr %2728, i64 4
  %2747 = load i8, ptr %2746, align 4, !tbaa !9
  %2748 = zext i8 %2747 to i64
  %2749 = shl nuw nsw i64 %2748, 32
  %2750 = or disjoint i64 %2749, %2745
  %2751 = getelementptr inbounds nuw i8, ptr %2728, i64 5
  %2752 = load i8, ptr %2751, align 1, !tbaa !9
  %2753 = zext i8 %2752 to i64
  %2754 = shl nuw nsw i64 %2753, 40
  %2755 = or i64 %2754, %2750
  %2756 = getelementptr inbounds nuw i8, ptr %2728, i64 6
  %2757 = load i8, ptr %2756, align 2, !tbaa !9
  %2758 = zext i8 %2757 to i64
  %2759 = shl nuw nsw i64 %2758, 48
  %2760 = or i64 %2759, %2755
  %2761 = getelementptr inbounds nuw i8, ptr %2728, i64 7
  %2762 = load i8, ptr %2761, align 1, !tbaa !9
  %2763 = zext i8 %2762 to i64
  %2764 = shl nuw i64 %2763, 56
  %2765 = or i64 %2764, %2760
  %2766 = icmp eq i64 %2765, 3
  br i1 %2766, label %2767, label %2793

2767:                                             ; preds = %2724
  %2768 = shl nsw i64 %2726, 3
  %2769 = getelementptr inbounds i8, ptr %79, i64 %2768
  %2770 = trunc i64 %2725 to i8
  store i8 %2770, ptr %2769, align 8, !tbaa !9
  %2771 = lshr i64 %2725, 8
  %2772 = trunc i64 %2771 to i8
  %2773 = getelementptr inbounds nuw i8, ptr %2769, i64 1
  store i8 %2772, ptr %2773, align 1, !tbaa !9
  %2774 = lshr i64 %2725, 16
  %2775 = trunc i64 %2774 to i8
  %2776 = getelementptr inbounds nuw i8, ptr %2769, i64 2
  store i8 %2775, ptr %2776, align 2, !tbaa !9
  %2777 = lshr i64 %2725, 24
  %2778 = trunc i64 %2777 to i8
  %2779 = getelementptr inbounds nuw i8, ptr %2769, i64 3
  store i8 %2778, ptr %2779, align 1, !tbaa !9
  %2780 = lshr i64 %2725, 32
  %2781 = trunc i64 %2780 to i8
  %2782 = getelementptr inbounds nuw i8, ptr %2769, i64 4
  store i8 %2781, ptr %2782, align 4, !tbaa !9
  %2783 = lshr i64 %2725, 40
  %2784 = trunc i64 %2783 to i8
  %2785 = getelementptr inbounds nuw i8, ptr %2769, i64 5
  store i8 %2784, ptr %2785, align 1, !tbaa !9
  %2786 = lshr i64 %2725, 48
  %2787 = trunc i64 %2786 to i8
  %2788 = getelementptr inbounds nuw i8, ptr %2769, i64 6
  store i8 %2787, ptr %2788, align 2, !tbaa !9
  %2789 = lshr i64 %2725, 56
  %2790 = trunc nuw nsw i64 %2789 to i8
  %2791 = getelementptr inbounds nuw i8, ptr %2769, i64 7
  store i8 %2790, ptr %2791, align 1, !tbaa !9
  %2792 = add nsw i64 %2726, 1
  br label %2793

2793:                                             ; preds = %2767, %2724
  %2794 = phi i64 [ %2726, %2724 ], [ %2792, %2767 ]
  %2795 = getelementptr inbounds nuw i8, ptr %78, i64 %2727
  %2796 = load i8, ptr %2795, align 8, !tbaa !9
  %2797 = zext i8 %2796 to i64
  %2798 = getelementptr inbounds nuw i8, ptr %2795, i64 1
  %2799 = load i8, ptr %2798, align 1, !tbaa !9
  %2800 = zext i8 %2799 to i64
  %2801 = shl nuw nsw i64 %2800, 8
  %2802 = or disjoint i64 %2801, %2797
  %2803 = getelementptr inbounds nuw i8, ptr %2795, i64 2
  %2804 = load i8, ptr %2803, align 2, !tbaa !9
  %2805 = zext i8 %2804 to i64
  %2806 = shl nuw nsw i64 %2805, 16
  %2807 = or disjoint i64 %2806, %2802
  %2808 = getelementptr inbounds nuw i8, ptr %2795, i64 3
  %2809 = load i8, ptr %2808, align 1, !tbaa !9
  %2810 = zext i8 %2809 to i64
  %2811 = shl nuw nsw i64 %2810, 24
  %2812 = or disjoint i64 %2811, %2807
  %2813 = getelementptr inbounds nuw i8, ptr %2795, i64 4
  %2814 = load i8, ptr %2813, align 4, !tbaa !9
  %2815 = zext i8 %2814 to i64
  %2816 = shl nuw nsw i64 %2815, 32
  %2817 = or disjoint i64 %2816, %2812
  %2818 = getelementptr inbounds nuw i8, ptr %2795, i64 5
  %2819 = load i8, ptr %2818, align 1, !tbaa !9
  %2820 = zext i8 %2819 to i64
  %2821 = shl nuw nsw i64 %2820, 40
  %2822 = or i64 %2821, %2817
  %2823 = getelementptr inbounds nuw i8, ptr %2795, i64 6
  %2824 = load i8, ptr %2823, align 2, !tbaa !9
  %2825 = zext i8 %2824 to i64
  %2826 = shl nuw nsw i64 %2825, 48
  %2827 = or i64 %2826, %2822
  %2828 = getelementptr inbounds nuw i8, ptr %2795, i64 7
  %2829 = load i8, ptr %2828, align 1, !tbaa !9
  %2830 = zext i8 %2829 to i64
  %2831 = shl nuw i64 %2830, 56
  %2832 = or i64 %2831, %2827
  %2833 = icmp sgt i64 %2832, -1
  br i1 %2833, label %2724, label %2834, !llvm.loop !31

2834:                                             ; preds = %2793, %3277
  %2835 = phi i64 [ 0, %3277 ], [ %2794, %2793 ]
  %2836 = getelementptr inbounds nuw i8, ptr %77, i64 8
  %2837 = load i8, ptr %2836, align 8, !tbaa !9
  %2838 = zext i8 %2837 to i64
  %2839 = getelementptr inbounds nuw i8, ptr %77, i64 9
  %2840 = load i8, ptr %2839, align 1, !tbaa !9
  %2841 = zext i8 %2840 to i64
  %2842 = shl nuw nsw i64 %2841, 8
  %2843 = or disjoint i64 %2842, %2838
  %2844 = getelementptr inbounds nuw i8, ptr %77, i64 10
  %2845 = load i8, ptr %2844, align 2, !tbaa !9
  %2846 = zext i8 %2845 to i64
  %2847 = shl nuw nsw i64 %2846, 16
  %2848 = or disjoint i64 %2847, %2843
  %2849 = getelementptr inbounds nuw i8, ptr %77, i64 11
  %2850 = load i8, ptr %2849, align 1, !tbaa !9
  %2851 = zext i8 %2850 to i64
  %2852 = shl nuw nsw i64 %2851, 24
  %2853 = or disjoint i64 %2852, %2848
  %2854 = getelementptr inbounds nuw i8, ptr %77, i64 12
  %2855 = load i8, ptr %2854, align 4, !tbaa !9
  %2856 = zext i8 %2855 to i64
  %2857 = shl nuw nsw i64 %2856, 32
  %2858 = or disjoint i64 %2857, %2853
  %2859 = getelementptr inbounds nuw i8, ptr %77, i64 13
  %2860 = load i8, ptr %2859, align 1, !tbaa !9
  %2861 = zext i8 %2860 to i64
  %2862 = shl nuw nsw i64 %2861, 40
  %2863 = or i64 %2862, %2858
  %2864 = getelementptr inbounds nuw i8, ptr %77, i64 14
  %2865 = load i8, ptr %2864, align 2, !tbaa !9
  %2866 = zext i8 %2865 to i64
  %2867 = shl nuw nsw i64 %2866, 48
  %2868 = or i64 %2867, %2863
  %2869 = getelementptr inbounds nuw i8, ptr %77, i64 15
  %2870 = load i8, ptr %2869, align 1, !tbaa !9
  %2871 = zext i8 %2870 to i64
  %2872 = shl nuw i64 %2871, 56
  %2873 = or i64 %2872, %2868
  %2874 = icmp sgt i64 %2873, -1
  br i1 %2874, label %2875, label %2985

2875:                                             ; preds = %2834, %2944
  %2876 = phi i64 [ %2983, %2944 ], [ %2873, %2834 ]
  %2877 = phi i64 [ %2945, %2944 ], [ 0, %2834 ]
  %2878 = shl nsw i64 %2876, 3
  %2879 = getelementptr inbounds nuw i8, ptr %76, i64 %2878
  %2880 = load i8, ptr %2879, align 8, !tbaa !9
  %2881 = zext i8 %2880 to i64
  %2882 = getelementptr inbounds nuw i8, ptr %2879, i64 1
  %2883 = load i8, ptr %2882, align 1, !tbaa !9
  %2884 = zext i8 %2883 to i64
  %2885 = shl nuw nsw i64 %2884, 8
  %2886 = or disjoint i64 %2885, %2881
  %2887 = getelementptr inbounds nuw i8, ptr %2879, i64 2
  %2888 = load i8, ptr %2887, align 2, !tbaa !9
  %2889 = zext i8 %2888 to i64
  %2890 = shl nuw nsw i64 %2889, 16
  %2891 = or disjoint i64 %2890, %2886
  %2892 = getelementptr inbounds nuw i8, ptr %2879, i64 3
  %2893 = load i8, ptr %2892, align 1, !tbaa !9
  %2894 = zext i8 %2893 to i64
  %2895 = shl nuw nsw i64 %2894, 24
  %2896 = or disjoint i64 %2895, %2891
  %2897 = getelementptr inbounds nuw i8, ptr %2879, i64 4
  %2898 = load i8, ptr %2897, align 4, !tbaa !9
  %2899 = zext i8 %2898 to i64
  %2900 = shl nuw nsw i64 %2899, 32
  %2901 = or disjoint i64 %2900, %2896
  %2902 = getelementptr inbounds nuw i8, ptr %2879, i64 5
  %2903 = load i8, ptr %2902, align 1, !tbaa !9
  %2904 = zext i8 %2903 to i64
  %2905 = shl nuw nsw i64 %2904, 40
  %2906 = or i64 %2905, %2901
  %2907 = getelementptr inbounds nuw i8, ptr %2879, i64 6
  %2908 = load i8, ptr %2907, align 2, !tbaa !9
  %2909 = zext i8 %2908 to i64
  %2910 = shl nuw nsw i64 %2909, 48
  %2911 = or i64 %2910, %2906
  %2912 = getelementptr inbounds nuw i8, ptr %2879, i64 7
  %2913 = load i8, ptr %2912, align 1, !tbaa !9
  %2914 = zext i8 %2913 to i64
  %2915 = shl nuw i64 %2914, 56
  %2916 = or i64 %2915, %2911
  %2917 = icmp eq i64 %2916, 9
  br i1 %2917, label %2918, label %2944

2918:                                             ; preds = %2875
  %2919 = shl nsw i64 %2877, 3
  %2920 = getelementptr inbounds i8, ptr %79, i64 %2919
  %2921 = trunc i64 %2876 to i8
  store i8 %2921, ptr %2920, align 8, !tbaa !9
  %2922 = lshr i64 %2876, 8
  %2923 = trunc i64 %2922 to i8
  %2924 = getelementptr inbounds nuw i8, ptr %2920, i64 1
  store i8 %2923, ptr %2924, align 1, !tbaa !9
  %2925 = lshr i64 %2876, 16
  %2926 = trunc i64 %2925 to i8
  %2927 = getelementptr inbounds nuw i8, ptr %2920, i64 2
  store i8 %2926, ptr %2927, align 2, !tbaa !9
  %2928 = lshr i64 %2876, 24
  %2929 = trunc i64 %2928 to i8
  %2930 = getelementptr inbounds nuw i8, ptr %2920, i64 3
  store i8 %2929, ptr %2930, align 1, !tbaa !9
  %2931 = lshr i64 %2876, 32
  %2932 = trunc i64 %2931 to i8
  %2933 = getelementptr inbounds nuw i8, ptr %2920, i64 4
  store i8 %2932, ptr %2933, align 4, !tbaa !9
  %2934 = lshr i64 %2876, 40
  %2935 = trunc i64 %2934 to i8
  %2936 = getelementptr inbounds nuw i8, ptr %2920, i64 5
  store i8 %2935, ptr %2936, align 1, !tbaa !9
  %2937 = lshr i64 %2876, 48
  %2938 = trunc i64 %2937 to i8
  %2939 = getelementptr inbounds nuw i8, ptr %2920, i64 6
  store i8 %2938, ptr %2939, align 2, !tbaa !9
  %2940 = lshr i64 %2876, 56
  %2941 = trunc nuw nsw i64 %2940 to i8
  %2942 = getelementptr inbounds nuw i8, ptr %2920, i64 7
  store i8 %2941, ptr %2942, align 1, !tbaa !9
  %2943 = add nsw i64 %2877, 1
  br label %2944

2944:                                             ; preds = %2918, %2875
  %2945 = phi i64 [ %2877, %2875 ], [ %2943, %2918 ]
  %2946 = getelementptr inbounds nuw i8, ptr %78, i64 %2878
  %2947 = load i8, ptr %2946, align 8, !tbaa !9
  %2948 = zext i8 %2947 to i64
  %2949 = getelementptr inbounds nuw i8, ptr %2946, i64 1
  %2950 = load i8, ptr %2949, align 1, !tbaa !9
  %2951 = zext i8 %2950 to i64
  %2952 = shl nuw nsw i64 %2951, 8
  %2953 = or disjoint i64 %2952, %2948
  %2954 = getelementptr inbounds nuw i8, ptr %2946, i64 2
  %2955 = load i8, ptr %2954, align 2, !tbaa !9
  %2956 = zext i8 %2955 to i64
  %2957 = shl nuw nsw i64 %2956, 16
  %2958 = or disjoint i64 %2957, %2953
  %2959 = getelementptr inbounds nuw i8, ptr %2946, i64 3
  %2960 = load i8, ptr %2959, align 1, !tbaa !9
  %2961 = zext i8 %2960 to i64
  %2962 = shl nuw nsw i64 %2961, 24
  %2963 = or disjoint i64 %2962, %2958
  %2964 = getelementptr inbounds nuw i8, ptr %2946, i64 4
  %2965 = load i8, ptr %2964, align 4, !tbaa !9
  %2966 = zext i8 %2965 to i64
  %2967 = shl nuw nsw i64 %2966, 32
  %2968 = or disjoint i64 %2967, %2963
  %2969 = getelementptr inbounds nuw i8, ptr %2946, i64 5
  %2970 = load i8, ptr %2969, align 1, !tbaa !9
  %2971 = zext i8 %2970 to i64
  %2972 = shl nuw nsw i64 %2971, 40
  %2973 = or i64 %2972, %2968
  %2974 = getelementptr inbounds nuw i8, ptr %2946, i64 6
  %2975 = load i8, ptr %2974, align 2, !tbaa !9
  %2976 = zext i8 %2975 to i64
  %2977 = shl nuw nsw i64 %2976, 48
  %2978 = or i64 %2977, %2973
  %2979 = getelementptr inbounds nuw i8, ptr %2946, i64 7
  %2980 = load i8, ptr %2979, align 1, !tbaa !9
  %2981 = zext i8 %2980 to i64
  %2982 = shl nuw i64 %2981, 56
  %2983 = or i64 %2982, %2978
  %2984 = icmp sgt i64 %2983, -1
  br i1 %2984, label %2875, label %2985, !llvm.loop !31

2985:                                             ; preds = %2944, %2834
  %2986 = phi i64 [ 0, %2834 ], [ %2945, %2944 ]
  %2987 = icmp eq i64 %2835, 2
  %2988 = icmp eq i64 %2986, 1
  %2989 = and i1 %2987, %2988
  %2990 = load i64, ptr %79, align 16
  %2991 = icmp eq i64 %2990, 3
  %2992 = select i1 %2989, i1 %2991, i1 false
  %2993 = select i1 %2992, ptr @.str.1, ptr @.str.2
  %2994 = call i32 (ptr, ...) @printf(ptr noundef nonnull dereferenceable(1) @.str.11, ptr noundef nonnull %2993, i64 noundef %2835, i64 noundef %2986)
  %2995 = call i32 (ptr, ...) @printf(ptr noundef nonnull dereferenceable(1) @.str.12, ptr noundef nonnull @.str.1, i64 noundef 2)
  %2996 = call i32 (ptr, ...) @printf(ptr noundef nonnull dereferenceable(1) @.str.13, ptr noundef nonnull @.str.1, i64 noundef 6)
  call void @llvm.lifetime.start.p0(ptr nonnull %83) #9
  call void @llvm.lifetime.start.p0(ptr nonnull %13) #9
  store i64 0, ptr %13, align 16, !tbaa !10
  br label %2997

2997:                                             ; preds = %3061, %2985
  %2998 = phi i64 [ 0, %2985 ], [ %3042, %3061 ]
  %2999 = phi i64 [ 0, %2985 ], [ %3052, %3061 ]
  %3000 = phi i64 [ 0, %2985 ], [ %3062, %3061 ]
  %3001 = phi i64 [ 0, %2985 ], [ %3033, %3061 ]
  %3002 = phi i64 [ 1, %2985 ], [ %3063, %3061 ]
  %3003 = getelementptr inbounds nuw [8 x i8], ptr %13, i64 %3001
  %3004 = load i64, ptr %3003, align 8, !tbaa !10
  %3005 = shl nsw i64 %3001, 3
  %3006 = getelementptr inbounds nuw i8, ptr %83, i64 %3005
  %3007 = trunc i64 %3004 to i8
  store i8 %3007, ptr %3006, align 8, !tbaa !9
  %3008 = lshr i64 %3004, 8
  %3009 = trunc i64 %3008 to i8
  %3010 = getelementptr inbounds nuw i8, ptr %3006, i64 1
  store i8 %3009, ptr %3010, align 1, !tbaa !9
  %3011 = lshr i64 %3004, 16
  %3012 = trunc i64 %3011 to i8
  %3013 = getelementptr inbounds nuw i8, ptr %3006, i64 2
  store i8 %3012, ptr %3013, align 2, !tbaa !9
  %3014 = lshr i64 %3004, 24
  %3015 = trunc i64 %3014 to i8
  %3016 = getelementptr inbounds nuw i8, ptr %3006, i64 3
  store i8 %3015, ptr %3016, align 1, !tbaa !9
  %3017 = lshr i64 %3004, 32
  %3018 = trunc i64 %3017 to i8
  %3019 = getelementptr inbounds nuw i8, ptr %3006, i64 4
  store i8 %3018, ptr %3019, align 4, !tbaa !9
  %3020 = lshr i64 %3004, 40
  %3021 = trunc i64 %3020 to i8
  %3022 = getelementptr inbounds nuw i8, ptr %3006, i64 5
  store i8 %3021, ptr %3022, align 1, !tbaa !9
  %3023 = lshr i64 %3004, 48
  %3024 = trunc i64 %3023 to i8
  %3025 = getelementptr inbounds nuw i8, ptr %3006, i64 6
  store i8 %3024, ptr %3025, align 2, !tbaa !9
  %3026 = lshr i64 %3004, 56
  %3027 = trunc nuw i64 %3026 to i8
  %3028 = getelementptr inbounds nuw i8, ptr %3006, i64 7
  store i8 %3027, ptr %3028, align 1, !tbaa !9
  %3029 = shl nsw i64 %3004, 3
  %3030 = getelementptr inbounds i8, ptr @__const.main.ba, i64 %3029
  %3031 = load i8, ptr %3030, align 8, !tbaa !9
  %3032 = zext i8 %3031 to i64
  %3033 = add nuw nsw i64 %3001, 1
  %3034 = and i64 %3032, 2
  %3035 = icmp eq i64 %3034, 0
  br i1 %3035, label %3041, label %3036

3036:                                             ; preds = %2997
  %3037 = icmp eq i64 %2998, 0
  br i1 %3037, label %3038, label %3041

3038:                                             ; preds = %3036
  %3039 = add nsw i64 %3002, 1
  %3040 = getelementptr inbounds [8 x i8], ptr %13, i64 %3002
  store i64 1, ptr %3040, align 8, !tbaa !10
  br label %3041

3041:                                             ; preds = %3038, %3036, %2997
  %3042 = phi i64 [ %2998, %2997 ], [ 1, %3038 ], [ 1, %3036 ]
  %3043 = phi i64 [ %3002, %2997 ], [ %3039, %3038 ], [ %3002, %3036 ]
  %3044 = and i64 %3032, 4
  %3045 = icmp eq i64 %3044, 0
  br i1 %3045, label %3051, label %3046

3046:                                             ; preds = %3041
  %3047 = icmp eq i64 %2999, 0
  br i1 %3047, label %3048, label %3051

3048:                                             ; preds = %3046
  %3049 = add nsw i64 %3043, 1
  %3050 = getelementptr inbounds [8 x i8], ptr %13, i64 %3043
  store i64 2, ptr %3050, align 8, !tbaa !10
  br label %3051

3051:                                             ; preds = %3048, %3046, %3041
  %3052 = phi i64 [ %2999, %3041 ], [ 1, %3048 ], [ 1, %3046 ]
  %3053 = phi i64 [ %3043, %3041 ], [ %3049, %3048 ], [ %3043, %3046 ]
  %3054 = and i64 %3032, 8
  %3055 = icmp eq i64 %3054, 0
  br i1 %3055, label %3061, label %3056

3056:                                             ; preds = %3051
  %3057 = icmp eq i64 %3000, 0
  br i1 %3057, label %3058, label %3061

3058:                                             ; preds = %3056
  %3059 = add nsw i64 %3053, 1
  %3060 = getelementptr inbounds [8 x i8], ptr %13, i64 %3053
  store i64 3, ptr %3060, align 8, !tbaa !10
  br label %3061

3061:                                             ; preds = %3058, %3056, %3051
  %3062 = phi i64 [ %3000, %3051 ], [ 1, %3058 ], [ 1, %3056 ]
  %3063 = phi i64 [ %3053, %3051 ], [ %3059, %3058 ], [ %3053, %3056 ]
  %3064 = icmp slt i64 %3033, %3063
  br i1 %3064, label %2997, label %3065, !llvm.loop !32

3065:                                             ; preds = %3061
  call void @llvm.lifetime.end.p0(ptr nonnull %13) #9
  %3066 = icmp eq i64 %3033, 3
  %3067 = load i64, ptr %83, align 16
  %3068 = icmp eq i64 %3067, 0
  %3069 = select i1 %3066, i1 %3068, i1 false
  %3070 = getelementptr inbounds nuw i8, ptr %83, i64 8
  %3071 = load i64, ptr %3070, align 8
  %3072 = icmp eq i64 %3071, 1
  %3073 = select i1 %3069, i1 %3072, i1 false
  %3074 = getelementptr inbounds nuw i8, ptr %83, i64 16
  %3075 = load i64, ptr %3074, align 16
  %3076 = icmp eq i64 %3075, 2
  %3077 = select i1 %3073, i1 %3076, i1 false
  %3078 = select i1 %3077, ptr @.str.1, ptr @.str.2
  %3079 = call i32 (ptr, ...) @printf(ptr noundef nonnull dereferenceable(1) @.str.14, ptr noundef nonnull %3078, i64 noundef %3033)
  call void @llvm.lifetime.start.p0(ptr nonnull %84) #9
  call void @llvm.lifetime.start.p0(ptr nonnull %12) #9
  store i64 0, ptr %12, align 16, !tbaa !10
  br label %3080

3080:                                             ; preds = %3134, %3065
  %3081 = phi i64 [ 1, %3065 ], [ %3137, %3134 ]
  %3082 = phi i64 [ 1, %3065 ], [ %3135, %3134 ]
  %3083 = phi i64 [ 1, %3065 ], [ %3136, %3134 ]
  %3084 = phi i64 [ 0, %3065 ], [ %3112, %3134 ]
  %3085 = phi i64 [ 1, %3065 ], [ %3138, %3134 ]
  %3086 = getelementptr inbounds nuw [8 x i8], ptr %12, i64 %3084
  %3087 = load i64, ptr %3086, align 8, !tbaa !10
  %3088 = shl nsw i64 %3084, 3
  %3089 = getelementptr inbounds nuw i8, ptr %84, i64 %3088
  %3090 = trunc i64 %3087 to i8
  store i8 %3090, ptr %3089, align 8, !tbaa !9
  %3091 = lshr i64 %3087, 8
  %3092 = trunc i64 %3091 to i8
  %3093 = getelementptr inbounds nuw i8, ptr %3089, i64 1
  store i8 %3092, ptr %3093, align 1, !tbaa !9
  %3094 = lshr i64 %3087, 16
  %3095 = trunc i64 %3094 to i8
  %3096 = getelementptr inbounds nuw i8, ptr %3089, i64 2
  store i8 %3095, ptr %3096, align 2, !tbaa !9
  %3097 = lshr i64 %3087, 24
  %3098 = trunc i64 %3097 to i8
  %3099 = getelementptr inbounds nuw i8, ptr %3089, i64 3
  store i8 %3098, ptr %3099, align 1, !tbaa !9
  %3100 = lshr i64 %3087, 32
  %3101 = trunc i64 %3100 to i8
  %3102 = getelementptr inbounds nuw i8, ptr %3089, i64 4
  store i8 %3101, ptr %3102, align 4, !tbaa !9
  %3103 = lshr i64 %3087, 40
  %3104 = trunc i64 %3103 to i8
  %3105 = getelementptr inbounds nuw i8, ptr %3089, i64 5
  store i8 %3104, ptr %3105, align 1, !tbaa !9
  %3106 = lshr i64 %3087, 48
  %3107 = trunc i64 %3106 to i8
  %3108 = getelementptr inbounds nuw i8, ptr %3089, i64 6
  store i8 %3107, ptr %3108, align 2, !tbaa !9
  %3109 = lshr i64 %3087, 56
  %3110 = trunc nuw i64 %3109 to i8
  %3111 = getelementptr inbounds nuw i8, ptr %3089, i64 7
  store i8 %3110, ptr %3111, align 1, !tbaa !9
  %3112 = add nuw nsw i64 %3084, 1
  switch i64 %3087, label %3134 [
    i64 0, label %3113
    i64 1, label %3119
  ]

3113:                                             ; preds = %3080
  %3114 = add nsw i64 %3083, -1
  %3115 = icmp eq i64 %3114, 0
  br i1 %3115, label %3116, label %3122

3116:                                             ; preds = %3113
  %3117 = add nsw i64 %3085, 1
  %3118 = getelementptr inbounds [8 x i8], ptr %12, i64 %3085
  store i64 1, ptr %3118, align 8, !tbaa !10
  br label %3122

3119:                                             ; preds = %3080
  %3120 = add nsw i64 %3082, -1
  %3121 = icmp eq i64 %3120, 0
  br i1 %3121, label %3126, label %3134

3122:                                             ; preds = %3113, %3116
  %3123 = phi i64 [ %3085, %3113 ], [ %3117, %3116 ]
  %3124 = add nsw i64 %3081, -1
  %3125 = icmp eq i64 %3124, 0
  br i1 %3125, label %3126, label %3134

3126:                                             ; preds = %3122, %3119
  %3127 = phi i64 [ %3085, %3119 ], [ %3123, %3122 ]
  %3128 = phi i64 [ 2, %3119 ], [ 3, %3122 ]
  %3129 = phi i64 [ 0, %3119 ], [ %3082, %3122 ]
  %3130 = phi i64 [ %3083, %3119 ], [ %3114, %3122 ]
  %3131 = phi i64 [ %3081, %3119 ], [ 0, %3122 ]
  %3132 = add nsw i64 %3127, 1
  %3133 = getelementptr inbounds [8 x i8], ptr %12, i64 %3127
  store i64 %3128, ptr %3133, align 8, !tbaa !10
  br label %3134

3134:                                             ; preds = %3126, %3080, %3119, %3122
  %3135 = phi i64 [ %3120, %3119 ], [ %3082, %3122 ], [ %3082, %3080 ], [ %3129, %3126 ]
  %3136 = phi i64 [ %3083, %3119 ], [ %3114, %3122 ], [ %3083, %3080 ], [ %3130, %3126 ]
  %3137 = phi i64 [ %3081, %3119 ], [ %3124, %3122 ], [ %3081, %3080 ], [ %3131, %3126 ]
  %3138 = phi i64 [ %3085, %3119 ], [ %3123, %3122 ], [ %3085, %3080 ], [ %3132, %3126 ]
  %3139 = icmp slt i64 %3112, %3138
  br i1 %3139, label %3080, label %3140, !llvm.loop !33

3140:                                             ; preds = %3134
  %3141 = load i64, ptr %84, align 16
  call void @llvm.lifetime.end.p0(ptr nonnull %12) #9
  %3142 = icmp eq i64 %3112, 4
  %3143 = icmp eq i64 %3141, 0
  %3144 = select i1 %3142, i1 %3143, i1 false
  %3145 = select i1 %3144, ptr @.str.1, ptr @.str.2
  %3146 = call i32 (ptr, ...) @printf(ptr noundef nonnull dereferenceable(1) @.str.15, ptr noundef nonnull %3145, i64 noundef %3112)
  call void @llvm.lifetime.start.p0(ptr nonnull %85) #9
  call void @llvm.memcpy.p0.p0.i64(ptr noundef nonnull align 16 dereferenceable(32) %85, ptr noundef nonnull align 16 dereferenceable(32) @__const.main.pp, i64 32, i1 false)
  %3147 = getelementptr inbounds nuw i8, ptr %85, i64 8
  store i64 0, ptr %3147, align 8, !tbaa !10
  %3148 = getelementptr inbounds nuw i8, ptr %85, i64 16
  %3149 = getelementptr inbounds nuw i8, ptr %85, i64 24
  store i64 2, ptr %3149, align 8, !tbaa !10
  br label %3150

3150:                                             ; preds = %3140, %3150
  %3151 = phi i64 [ %3156, %3150 ], [ 0, %3140 ]
  %3152 = phi ptr [ %3155, %3150 ], [ %3147, %3140 ]
  %3153 = getelementptr inbounds [8 x i8], ptr %85, i64 %3151
  %3154 = load i64, ptr %3153, align 8, !tbaa !10
  store i64 %3154, ptr %3152, align 8, !tbaa !10
  %3155 = getelementptr inbounds [8 x i8], ptr %85, i64 %3154
  %3156 = load i64, ptr %3155, align 8, !tbaa !10
  %3157 = icmp eq i64 %3156, %3154
  br i1 %3157, label %3158, label %3150, !llvm.loop !34

3158:                                             ; preds = %3150
  %3159 = load i64, ptr %3148, align 16, !tbaa !10
  %3160 = icmp eq i64 %3159, 2
  br i1 %3160, label %3169, label %3161

3161:                                             ; preds = %3158, %3161
  %3162 = phi i64 [ %3167, %3161 ], [ %3159, %3158 ]
  %3163 = phi ptr [ %3166, %3161 ], [ %3148, %3158 ]
  %3164 = getelementptr inbounds [8 x i8], ptr %85, i64 %3162
  %3165 = load i64, ptr %3164, align 8, !tbaa !10
  store i64 %3165, ptr %3163, align 8, !tbaa !10
  %3166 = getelementptr inbounds [8 x i8], ptr %85, i64 %3165
  %3167 = load i64, ptr %3166, align 8, !tbaa !10
  %3168 = icmp eq i64 %3167, %3165
  br i1 %3168, label %3169, label %3161, !llvm.loop !34

3169:                                             ; preds = %3161, %3158
  %3170 = phi i64 [ 2, %3158 ], [ %3165, %3161 ]
  %3171 = icmp eq i64 %3154, %3170
  br i1 %3171, label %3595, label %3567

3172:                                             ; preds = %2720
  %3173 = call i32 (ptr, ...) @printf(ptr noundef nonnull dereferenceable(1) @.str.6, i32 noundef 0, i64 noundef %2721, i64 noundef %2722)
  br label %3174

3174:                                             ; preds = %2720, %3172
  %3175 = phi i32 [ 0, %3172 ], [ 1, %2720 ]
  %3176 = getelementptr inbounds nuw i8, ptr %64, i64 8
  %3177 = load i64, ptr %3176, align 8, !tbaa !10
  %3178 = getelementptr inbounds nuw i8, ptr %65, i64 8
  %3179 = load i64, ptr %3178, align 8, !tbaa !10
  %3180 = icmp eq i64 %3177, %3179
  br i1 %3180, label %3183, label %3181

3181:                                             ; preds = %3174
  %3182 = call i32 (ptr, ...) @printf(ptr noundef nonnull dereferenceable(1) @.str.6, i32 noundef 1, i64 noundef %3177, i64 noundef %3179)
  br label %3183

3183:                                             ; preds = %3181, %3174
  %3184 = phi i32 [ 0, %3181 ], [ %3175, %3174 ]
  %3185 = getelementptr inbounds nuw i8, ptr %64, i64 16
  %3186 = load i64, ptr %3185, align 16, !tbaa !10
  %3187 = getelementptr inbounds nuw i8, ptr %65, i64 16
  %3188 = load i64, ptr %3187, align 16, !tbaa !10
  %3189 = icmp eq i64 %3186, %3188
  br i1 %3189, label %3192, label %3190

3190:                                             ; preds = %3183
  %3191 = call i32 (ptr, ...) @printf(ptr noundef nonnull dereferenceable(1) @.str.6, i32 noundef 2, i64 noundef %3186, i64 noundef %3188)
  br label %3192

3192:                                             ; preds = %3190, %3183
  %3193 = phi i32 [ 0, %3190 ], [ %3184, %3183 ]
  %3194 = getelementptr inbounds nuw i8, ptr %64, i64 24
  %3195 = load i64, ptr %3194, align 8, !tbaa !10
  %3196 = getelementptr inbounds nuw i8, ptr %65, i64 24
  %3197 = load i64, ptr %3196, align 8, !tbaa !10
  %3198 = icmp eq i64 %3195, %3197
  br i1 %3198, label %3201, label %3199

3199:                                             ; preds = %3192
  %3200 = call i32 (ptr, ...) @printf(ptr noundef nonnull dereferenceable(1) @.str.6, i32 noundef 3, i64 noundef %3195, i64 noundef %3197)
  br label %3201

3201:                                             ; preds = %3199, %3192
  %3202 = phi i32 [ 0, %3199 ], [ %3193, %3192 ]
  %3203 = getelementptr inbounds nuw i8, ptr %64, i64 32
  %3204 = load i64, ptr %3203, align 16, !tbaa !10
  %3205 = getelementptr inbounds nuw i8, ptr %65, i64 32
  %3206 = load i64, ptr %3205, align 16, !tbaa !10
  %3207 = icmp eq i64 %3204, %3206
  br i1 %3207, label %3210, label %3208

3208:                                             ; preds = %3201
  %3209 = call i32 (ptr, ...) @printf(ptr noundef nonnull dereferenceable(1) @.str.6, i32 noundef 4, i64 noundef %3204, i64 noundef %3206)
  br label %3210

3210:                                             ; preds = %3208, %3201
  %3211 = phi i32 [ 0, %3208 ], [ %3202, %3201 ]
  %3212 = getelementptr inbounds nuw i8, ptr %64, i64 40
  %3213 = load i64, ptr %3212, align 8, !tbaa !10
  %3214 = getelementptr inbounds nuw i8, ptr %65, i64 40
  %3215 = load i64, ptr %3214, align 8, !tbaa !10
  %3216 = icmp eq i64 %3213, %3215
  br i1 %3216, label %3219, label %3217

3217:                                             ; preds = %3210
  %3218 = call i32 (ptr, ...) @printf(ptr noundef nonnull dereferenceable(1) @.str.6, i32 noundef 5, i64 noundef %3213, i64 noundef %3215)
  br label %3219

3219:                                             ; preds = %3217, %3210
  %3220 = phi i32 [ 0, %3217 ], [ %3211, %3210 ]
  %3221 = getelementptr inbounds nuw i8, ptr %64, i64 48
  %3222 = load i64, ptr %3221, align 16, !tbaa !10
  %3223 = getelementptr inbounds nuw i8, ptr %65, i64 48
  %3224 = load i64, ptr %3223, align 16, !tbaa !10
  %3225 = icmp eq i64 %3222, %3224
  br i1 %3225, label %3228, label %3226

3226:                                             ; preds = %3219
  %3227 = call i32 (ptr, ...) @printf(ptr noundef nonnull dereferenceable(1) @.str.6, i32 noundef 6, i64 noundef %3222, i64 noundef %3224)
  br label %3228

3228:                                             ; preds = %3226, %3219
  %3229 = phi i32 [ 0, %3226 ], [ %3220, %3219 ]
  %3230 = getelementptr inbounds nuw i8, ptr %64, i64 56
  %3231 = load i64, ptr %3230, align 8, !tbaa !10
  %3232 = getelementptr inbounds nuw i8, ptr %65, i64 56
  %3233 = load i64, ptr %3232, align 8, !tbaa !10
  %3234 = icmp eq i64 %3231, %3233
  br i1 %3234, label %3237, label %3235

3235:                                             ; preds = %3228
  %3236 = call i32 (ptr, ...) @printf(ptr noundef nonnull dereferenceable(1) @.str.6, i32 noundef 7, i64 noundef %3231, i64 noundef %3233)
  br label %3237

3237:                                             ; preds = %3235, %3228
  %3238 = phi i32 [ 0, %3235 ], [ %3229, %3228 ]
  %3239 = getelementptr inbounds nuw i8, ptr %64, i64 64
  %3240 = load i64, ptr %3239, align 16, !tbaa !10
  %3241 = getelementptr inbounds nuw i8, ptr %65, i64 64
  %3242 = load i64, ptr %3241, align 16, !tbaa !10
  %3243 = icmp eq i64 %3240, %3242
  br i1 %3243, label %3246, label %3244

3244:                                             ; preds = %3237
  %3245 = call i32 (ptr, ...) @printf(ptr noundef nonnull dereferenceable(1) @.str.6, i32 noundef 8, i64 noundef %3240, i64 noundef %3242)
  br label %3246

3246:                                             ; preds = %3244, %3237
  %3247 = phi i32 [ 0, %3244 ], [ %3238, %3237 ]
  %3248 = getelementptr inbounds nuw i8, ptr %64, i64 72
  %3249 = load i64, ptr %3248, align 8, !tbaa !10
  %3250 = getelementptr inbounds nuw i8, ptr %65, i64 72
  %3251 = load i64, ptr %3250, align 8, !tbaa !10
  %3252 = icmp eq i64 %3249, %3251
  br i1 %3252, label %3255, label %3253

3253:                                             ; preds = %3246
  %3254 = call i32 (ptr, ...) @printf(ptr noundef nonnull dereferenceable(1) @.str.6, i32 noundef 9, i64 noundef %3249, i64 noundef %3251)
  br label %3255

3255:                                             ; preds = %3253, %3246
  %3256 = phi i32 [ 0, %3253 ], [ %3247, %3246 ]
  %3257 = getelementptr inbounds nuw i8, ptr %64, i64 80
  %3258 = load i64, ptr %3257, align 16, !tbaa !10
  %3259 = getelementptr inbounds nuw i8, ptr %65, i64 80
  %3260 = load i64, ptr %3259, align 16, !tbaa !10
  %3261 = icmp eq i64 %3258, %3260
  br i1 %3261, label %3264, label %3262

3262:                                             ; preds = %3255
  %3263 = call i32 (ptr, ...) @printf(ptr noundef nonnull dereferenceable(1) @.str.6, i32 noundef 10, i64 noundef %3258, i64 noundef %3260)
  br label %3264

3264:                                             ; preds = %3262, %3255
  %3265 = phi i32 [ 0, %3262 ], [ %3256, %3255 ]
  %3266 = getelementptr inbounds nuw i8, ptr %64, i64 88
  %3267 = load i64, ptr %3266, align 8, !tbaa !10
  %3268 = getelementptr inbounds nuw i8, ptr %65, i64 88
  %3269 = load i64, ptr %3268, align 8, !tbaa !10
  %3270 = icmp eq i64 %3267, %3269
  br i1 %3270, label %3273, label %3271

3271:                                             ; preds = %3264
  %3272 = call i32 (ptr, ...) @printf(ptr noundef nonnull dereferenceable(1) @.str.6, i32 noundef 11, i64 noundef %3267, i64 noundef %3269)
  br label %3276

3273:                                             ; preds = %3264
  %3274 = freeze i32 %3265
  %3275 = icmp eq i32 %3274, 0
  br i1 %3275, label %3276, label %3277

3276:                                             ; preds = %3271, %3273
  br label %3277

3277:                                             ; preds = %3273, %3276
  %3278 = phi ptr [ @.str.2, %3276 ], [ @.str.1, %3273 ]
  %3279 = call i32 (ptr, ...) @printf(ptr noundef nonnull dereferenceable(1) @.str.7, ptr noundef nonnull %3278)
  call void @llvm.lifetime.start.p0(ptr nonnull %68) #9
  store i64 5, ptr %68, align 16
  %3280 = getelementptr inbounds nuw i8, ptr %68, i64 8
  store i64 1, ptr %3280, align 8
  %3281 = getelementptr inbounds nuw i8, ptr %68, i64 16
  store i64 9, ptr %3281, align 16
  %3282 = getelementptr inbounds nuw i8, ptr %68, i64 24
  store i64 3, ptr %3282, align 8
  %3283 = getelementptr inbounds nuw i8, ptr %68, i64 32
  store i64 7, ptr %3283, align 16
  call void @llvm.lifetime.start.p0(ptr nonnull %69) #9
  store i64 10, ptr %69, align 16
  %3284 = getelementptr inbounds nuw i8, ptr %69, i64 8
  store i64 11, ptr %3284, align 8
  %3285 = getelementptr inbounds nuw i8, ptr %69, i64 16
  store i64 12, ptr %3285, align 16
  %3286 = getelementptr inbounds nuw i8, ptr %69, i64 24
  store i64 13, ptr %3286, align 8
  %3287 = getelementptr inbounds nuw i8, ptr %69, i64 32
  store i64 14, ptr %3287, align 16
  call void @llvm.lifetime.start.p0(ptr nonnull %70) #9
  call void @llvm.lifetime.start.p0(ptr nonnull %71) #9
  call void @llvm.lifetime.start.p0(ptr nonnull %72) #9
  store ptr %68, ptr %72, align 8, !tbaa !15
  %3288 = getelementptr inbounds nuw i8, ptr %72, i64 8
  store i64 5, ptr %3288, align 8, !tbaa !19
  %3289 = getelementptr inbounds nuw i8, ptr %72, i64 16
  store i64 8, ptr %3289, align 8, !tbaa !20
  %3290 = getelementptr inbounds nuw i8, ptr %72, i64 24
  store i64 8, ptr %3290, align 8, !tbaa !21
  call void @llvm.lifetime.start.p0(ptr nonnull %73) #9
  store ptr %69, ptr %73, align 8, !tbaa !15
  %3291 = getelementptr inbounds nuw i8, ptr %73, i64 8
  store i64 5, ptr %3291, align 8, !tbaa !19
  %3292 = getelementptr inbounds nuw i8, ptr %73, i64 16
  store i64 8, ptr %3292, align 8, !tbaa !20
  %3293 = getelementptr inbounds nuw i8, ptr %73, i64 24
  store i64 8, ptr %3293, align 8, !tbaa !21
  call void @llvm.lifetime.start.p0(ptr nonnull %74) #9
  store ptr %70, ptr %74, align 8, !tbaa !15
  %3294 = getelementptr inbounds nuw i8, ptr %74, i64 8
  store i64 3, ptr %3294, align 8, !tbaa !19
  %3295 = getelementptr inbounds nuw i8, ptr %74, i64 16
  store i64 8, ptr %3295, align 8, !tbaa !20
  %3296 = getelementptr inbounds nuw i8, ptr %74, i64 24
  store i64 8, ptr %3296, align 8, !tbaa !21
  call void @llvm.lifetime.start.p0(ptr nonnull %75) #9
  store ptr %71, ptr %75, align 8, !tbaa !15
  %3297 = getelementptr inbounds nuw i8, ptr %75, i64 8
  store i64 3, ptr %3297, align 8, !tbaa !19
  %3298 = getelementptr inbounds nuw i8, ptr %75, i64 16
  store i64 8, ptr %3298, align 8, !tbaa !20
  %3299 = getelementptr inbounds nuw i8, ptr %75, i64 24
  store i64 8, ptr %3299, align 8, !tbaa !21
  call fastcc void @topk(ptr noundef %72, i64 noundef 5, ptr noundef %73, ptr noundef %74, ptr noundef %75)
  %3300 = load i64, ptr %70, align 16, !tbaa !10
  %3301 = icmp eq i64 %3300, 12
  %3302 = getelementptr inbounds nuw i8, ptr %70, i64 8
  %3303 = load i64, ptr %3302, align 8
  %3304 = icmp eq i64 %3303, 14
  %3305 = select i1 %3301, i1 %3304, i1 false
  %3306 = getelementptr inbounds nuw i8, ptr %70, i64 16
  %3307 = load i64, ptr %3306, align 16
  %3308 = icmp eq i64 %3307, 10
  %3309 = select i1 %3305, i1 %3308, i1 false
  %3310 = load i64, ptr %71, align 16
  %3311 = icmp eq i64 %3310, 9
  %3312 = select i1 %3309, i1 %3311, i1 false
  %3313 = getelementptr inbounds nuw i8, ptr %71, i64 8
  %3314 = load i64, ptr %3313, align 8
  %3315 = icmp eq i64 %3314, 7
  %3316 = select i1 %3312, i1 %3315, i1 false
  %3317 = getelementptr inbounds nuw i8, ptr %71, i64 16
  %3318 = load i64, ptr %3317, align 16
  %3319 = icmp eq i64 %3318, 5
  %3320 = select i1 %3316, i1 %3319, i1 false
  %3321 = select i1 %3320, ptr @.str.1, ptr @.str.2
  %3322 = call i32 (ptr, ...) @printf(ptr noundef nonnull dereferenceable(1) @.str.8, ptr noundef nonnull %3321)
  %3323 = load i8, ptr %68, align 16, !tbaa !9
  %3324 = getelementptr inbounds nuw i8, ptr %68, i64 1
  %3325 = load i8, ptr %3324, align 1, !tbaa !9
  %3326 = getelementptr inbounds nuw i8, ptr %68, i64 2
  %3327 = load i8, ptr %3326, align 2, !tbaa !9
  %3328 = getelementptr inbounds nuw i8, ptr %68, i64 3
  %3329 = load i8, ptr %3328, align 1, !tbaa !9
  %3330 = getelementptr inbounds nuw i8, ptr %68, i64 4
  %3331 = load i8, ptr %3330, align 4, !tbaa !9
  %3332 = getelementptr inbounds nuw i8, ptr %68, i64 5
  %3333 = load i8, ptr %3332, align 1, !tbaa !9
  %3334 = getelementptr inbounds nuw i8, ptr %68, i64 6
  %3335 = load i8, ptr %3334, align 2, !tbaa !9
  %3336 = getelementptr inbounds nuw i8, ptr %68, i64 7
  %3337 = load i8, ptr %3336, align 1, !tbaa !9
  %3338 = load i8, ptr %3280, align 8, !tbaa !9
  %3339 = getelementptr inbounds nuw i8, ptr %68, i64 9
  %3340 = load i8, ptr %3339, align 1, !tbaa !9
  %3341 = getelementptr inbounds nuw i8, ptr %68, i64 10
  %3342 = load i8, ptr %3341, align 2, !tbaa !9
  %3343 = getelementptr inbounds nuw i8, ptr %68, i64 11
  %3344 = load i8, ptr %3343, align 1, !tbaa !9
  %3345 = getelementptr inbounds nuw i8, ptr %68, i64 12
  %3346 = load i8, ptr %3345, align 4, !tbaa !9
  %3347 = getelementptr inbounds nuw i8, ptr %68, i64 13
  %3348 = load i8, ptr %3347, align 1, !tbaa !9
  %3349 = getelementptr inbounds nuw i8, ptr %68, i64 14
  %3350 = load i8, ptr %3349, align 2, !tbaa !9
  %3351 = getelementptr inbounds nuw i8, ptr %68, i64 15
  %3352 = load i8, ptr %3351, align 1, !tbaa !9
  %3353 = load i8, ptr %3281, align 16, !tbaa !9
  %3354 = getelementptr inbounds nuw i8, ptr %68, i64 17
  %3355 = load i8, ptr %3354, align 1, !tbaa !9
  %3356 = getelementptr inbounds nuw i8, ptr %68, i64 18
  %3357 = load i8, ptr %3356, align 2, !tbaa !9
  %3358 = getelementptr inbounds nuw i8, ptr %68, i64 19
  %3359 = load i8, ptr %3358, align 1, !tbaa !9
  %3360 = getelementptr inbounds nuw i8, ptr %68, i64 20
  %3361 = load i8, ptr %3360, align 4, !tbaa !9
  %3362 = getelementptr inbounds nuw i8, ptr %68, i64 21
  %3363 = load i8, ptr %3362, align 1, !tbaa !9
  %3364 = getelementptr inbounds nuw i8, ptr %68, i64 22
  %3365 = load i8, ptr %3364, align 2, !tbaa !9
  %3366 = getelementptr inbounds nuw i8, ptr %68, i64 23
  %3367 = load i8, ptr %3366, align 1, !tbaa !9
  %3368 = load i8, ptr %3282, align 8, !tbaa !9
  %3369 = getelementptr inbounds nuw i8, ptr %68, i64 25
  %3370 = load i8, ptr %3369, align 1, !tbaa !9
  %3371 = getelementptr inbounds nuw i8, ptr %68, i64 26
  %3372 = load i8, ptr %3371, align 2, !tbaa !9
  %3373 = getelementptr inbounds nuw i8, ptr %68, i64 27
  %3374 = load i8, ptr %3373, align 1, !tbaa !9
  %3375 = getelementptr inbounds nuw i8, ptr %68, i64 28
  %3376 = load i8, ptr %3375, align 4, !tbaa !9
  %3377 = getelementptr inbounds nuw i8, ptr %68, i64 29
  %3378 = load i8, ptr %3377, align 1, !tbaa !9
  %3379 = getelementptr inbounds nuw i8, ptr %68, i64 30
  %3380 = load i8, ptr %3379, align 2, !tbaa !9
  %3381 = getelementptr inbounds nuw i8, ptr %68, i64 31
  %3382 = load i8, ptr %3381, align 1, !tbaa !9
  %3383 = load i8, ptr %3283, align 16, !tbaa !9
  %3384 = zext i8 %3383 to i64
  %3385 = getelementptr inbounds nuw i8, ptr %68, i64 33
  %3386 = load i8, ptr %3385, align 1, !tbaa !9
  %3387 = zext i8 %3386 to i64
  %3388 = shl nuw nsw i64 %3387, 8
  %3389 = or disjoint i64 %3388, %3384
  %3390 = getelementptr inbounds nuw i8, ptr %68, i64 34
  %3391 = load i8, ptr %3390, align 2, !tbaa !9
  %3392 = zext i8 %3391 to i64
  %3393 = shl nuw nsw i64 %3392, 16
  %3394 = or disjoint i64 %3393, %3389
  %3395 = getelementptr inbounds nuw i8, ptr %68, i64 35
  %3396 = load i8, ptr %3395, align 1, !tbaa !9
  %3397 = zext i8 %3396 to i64
  %3398 = shl nuw nsw i64 %3397, 24
  %3399 = or disjoint i64 %3398, %3394
  %3400 = getelementptr inbounds nuw i8, ptr %68, i64 36
  %3401 = load i8, ptr %3400, align 4, !tbaa !9
  %3402 = zext i8 %3401 to i64
  %3403 = shl nuw nsw i64 %3402, 32
  %3404 = or disjoint i64 %3403, %3399
  %3405 = getelementptr inbounds nuw i8, ptr %68, i64 37
  %3406 = load i8, ptr %3405, align 1, !tbaa !9
  %3407 = zext i8 %3406 to i64
  %3408 = shl nuw nsw i64 %3407, 40
  %3409 = or i64 %3408, %3404
  %3410 = getelementptr inbounds nuw i8, ptr %68, i64 38
  %3411 = load i8, ptr %3410, align 2, !tbaa !9
  %3412 = zext i8 %3411 to i64
  %3413 = shl nuw nsw i64 %3412, 48
  %3414 = or i64 %3413, %3409
  %3415 = getelementptr inbounds nuw i8, ptr %68, i64 39
  %3416 = load i8, ptr %3415, align 1, !tbaa !9
  %3417 = zext i8 %3416 to i64
  %3418 = shl nuw i64 %3417, 56
  %3419 = or i64 %3418, %3414
  %3420 = zext i8 %3368 to i64
  %3421 = zext i8 %3370 to i64
  %3422 = shl nuw nsw i64 %3421, 8
  %3423 = or disjoint i64 %3422, %3420
  %3424 = zext i8 %3372 to i64
  %3425 = shl nuw nsw i64 %3424, 16
  %3426 = or disjoint i64 %3425, %3423
  %3427 = zext i8 %3374 to i64
  %3428 = shl nuw nsw i64 %3427, 24
  %3429 = or disjoint i64 %3428, %3426
  %3430 = zext i8 %3376 to i64
  %3431 = shl nuw nsw i64 %3430, 32
  %3432 = or disjoint i64 %3431, %3429
  %3433 = zext i8 %3378 to i64
  %3434 = shl nuw nsw i64 %3433, 40
  %3435 = or i64 %3434, %3432
  %3436 = zext i8 %3380 to i64
  %3437 = shl nuw nsw i64 %3436, 48
  %3438 = or i64 %3437, %3435
  %3439 = zext i8 %3382 to i64
  %3440 = shl nuw i64 %3439, 56
  %3441 = or i64 %3440, %3438
  %3442 = zext i8 %3353 to i64
  %3443 = zext i8 %3355 to i64
  %3444 = shl nuw nsw i64 %3443, 8
  %3445 = or disjoint i64 %3444, %3442
  %3446 = zext i8 %3357 to i64
  %3447 = shl nuw nsw i64 %3446, 16
  %3448 = or disjoint i64 %3447, %3445
  %3449 = zext i8 %3359 to i64
  %3450 = shl nuw nsw i64 %3449, 24
  %3451 = or disjoint i64 %3450, %3448
  %3452 = zext i8 %3361 to i64
  %3453 = shl nuw nsw i64 %3452, 32
  %3454 = or disjoint i64 %3453, %3451
  %3455 = zext i8 %3363 to i64
  %3456 = shl nuw nsw i64 %3455, 40
  %3457 = or i64 %3456, %3454
  %3458 = zext i8 %3365 to i64
  %3459 = shl nuw nsw i64 %3458, 48
  %3460 = or i64 %3459, %3457
  %3461 = zext i8 %3367 to i64
  %3462 = shl nuw i64 %3461, 56
  %3463 = or i64 %3462, %3460
  %3464 = zext i8 %3338 to i64
  %3465 = zext i8 %3340 to i64
  %3466 = shl nuw nsw i64 %3465, 8
  %3467 = or disjoint i64 %3466, %3464
  %3468 = zext i8 %3342 to i64
  %3469 = shl nuw nsw i64 %3468, 16
  %3470 = or disjoint i64 %3469, %3467
  %3471 = zext i8 %3344 to i64
  %3472 = shl nuw nsw i64 %3471, 24
  %3473 = or disjoint i64 %3472, %3470
  %3474 = zext i8 %3346 to i64
  %3475 = shl nuw nsw i64 %3474, 32
  %3476 = or disjoint i64 %3475, %3473
  %3477 = zext i8 %3348 to i64
  %3478 = shl nuw nsw i64 %3477, 40
  %3479 = or i64 %3478, %3476
  %3480 = zext i8 %3350 to i64
  %3481 = shl nuw nsw i64 %3480, 48
  %3482 = or i64 %3481, %3479
  %3483 = zext i8 %3352 to i64
  %3484 = shl nuw i64 %3483, 56
  %3485 = or i64 %3484, %3482
  %3486 = zext i8 %3323 to i64
  %3487 = zext i8 %3325 to i64
  %3488 = shl nuw nsw i64 %3487, 8
  %3489 = or disjoint i64 %3488, %3486
  %3490 = zext i8 %3327 to i64
  %3491 = shl nuw nsw i64 %3490, 16
  %3492 = or disjoint i64 %3491, %3489
  %3493 = zext i8 %3329 to i64
  %3494 = shl nuw nsw i64 %3493, 24
  %3495 = or disjoint i64 %3494, %3492
  %3496 = zext i8 %3331 to i64
  %3497 = shl nuw nsw i64 %3496, 32
  %3498 = or disjoint i64 %3497, %3495
  %3499 = zext i8 %3333 to i64
  %3500 = shl nuw nsw i64 %3499, 40
  %3501 = or i64 %3500, %3498
  %3502 = zext i8 %3335 to i64
  %3503 = shl nuw nsw i64 %3502, 48
  %3504 = or i64 %3503, %3501
  %3505 = zext i8 %3337 to i64
  %3506 = shl nuw i64 %3505, 56
  %3507 = or i64 %3506, %3504
  %3508 = call i64 @llvm.smax.i64(i64 %3485, i64 %3507)
  %3509 = call i64 @llvm.smax.i64(i64 %3463, i64 %3508)
  %3510 = icmp sle i64 %3441, %3509
  %3511 = icmp sgt i64 %3463, %3508
  %3512 = call i64 @llvm.smax.i64(i64 %3441, i64 %3509)
  %3513 = icmp sle i64 %3419, %3512
  %3514 = and i1 %3511, %3510
  %3515 = select i1 %3513, i1 %3514, i1 false
  %3516 = select i1 %3515, ptr @.str.1, ptr @.str.2
  %3517 = call i32 (ptr, ...) @printf(ptr noundef nonnull dereferenceable(1) @.str.9, ptr noundef nonnull %3516)
  %3518 = call i32 (ptr, ...) @printf(ptr noundef nonnull dereferenceable(1) @.str.10, ptr noundef nonnull @.str.1, i64 noundef 3)
  call void @llvm.lifetime.start.p0(ptr nonnull %76) #9
  call void @llvm.memcpy.p0.p0.i64(ptr noundef nonnull align 16 dereferenceable(32) %76, ptr noundef nonnull align 16 dereferenceable(32) @__const.main.ik, i64 32, i1 false)
  call void @llvm.lifetime.start.p0(ptr nonnull %77) #9
  call void @llvm.lifetime.start.p0(ptr nonnull %78) #9
  call void @llvm.lifetime.start.p0(ptr nonnull %79) #9
  call void @llvm.lifetime.start.p0(ptr nonnull %80) #9
  store ptr %76, ptr %80, align 8, !tbaa !15
  %3519 = getelementptr inbounds nuw i8, ptr %80, i64 8
  store i64 4, ptr %3519, align 8, !tbaa !19
  %3520 = getelementptr inbounds nuw i8, ptr %80, i64 16
  store i64 8, ptr %3520, align 8, !tbaa !20
  %3521 = getelementptr inbounds nuw i8, ptr %80, i64 24
  store i64 8, ptr %3521, align 8, !tbaa !21
  call void @llvm.lifetime.start.p0(ptr nonnull %81) #9
  store ptr %77, ptr %81, align 8, !tbaa !15
  %3522 = getelementptr inbounds nuw i8, ptr %81, i64 8
  store i64 8, ptr %3522, align 8, !tbaa !19
  %3523 = getelementptr inbounds nuw i8, ptr %81, i64 16
  store i64 8, ptr %3523, align 8, !tbaa !20
  %3524 = getelementptr inbounds nuw i8, ptr %81, i64 24
  store i64 8, ptr %3524, align 8, !tbaa !21
  call void @llvm.lifetime.start.p0(ptr nonnull %82) #9
  store ptr %78, ptr %82, align 8, !tbaa !15
  %3525 = getelementptr inbounds nuw i8, ptr %82, i64 8
  store i64 4, ptr %3525, align 8, !tbaa !19
  %3526 = getelementptr inbounds nuw i8, ptr %82, i64 16
  store i64 8, ptr %3526, align 8, !tbaa !20
  %3527 = getelementptr inbounds nuw i8, ptr %82, i64 24
  store i64 8, ptr %3527, align 8, !tbaa !21
  call fastcc void @build_index(ptr noundef %80, ptr noundef %81, ptr noundef %82)
  %3528 = getelementptr inbounds nuw i8, ptr %77, i64 24
  %3529 = load i8, ptr %3528, align 8, !tbaa !9
  %3530 = zext i8 %3529 to i64
  %3531 = getelementptr inbounds nuw i8, ptr %77, i64 25
  %3532 = load i8, ptr %3531, align 1, !tbaa !9
  %3533 = zext i8 %3532 to i64
  %3534 = shl nuw nsw i64 %3533, 8
  %3535 = or disjoint i64 %3534, %3530
  %3536 = getelementptr inbounds nuw i8, ptr %77, i64 26
  %3537 = load i8, ptr %3536, align 2, !tbaa !9
  %3538 = zext i8 %3537 to i64
  %3539 = shl nuw nsw i64 %3538, 16
  %3540 = or disjoint i64 %3539, %3535
  %3541 = getelementptr inbounds nuw i8, ptr %77, i64 27
  %3542 = load i8, ptr %3541, align 1, !tbaa !9
  %3543 = zext i8 %3542 to i64
  %3544 = shl nuw nsw i64 %3543, 24
  %3545 = or disjoint i64 %3544, %3540
  %3546 = getelementptr inbounds nuw i8, ptr %77, i64 28
  %3547 = load i8, ptr %3546, align 4, !tbaa !9
  %3548 = zext i8 %3547 to i64
  %3549 = shl nuw nsw i64 %3548, 32
  %3550 = or disjoint i64 %3549, %3545
  %3551 = getelementptr inbounds nuw i8, ptr %77, i64 29
  %3552 = load i8, ptr %3551, align 1, !tbaa !9
  %3553 = zext i8 %3552 to i64
  %3554 = shl nuw nsw i64 %3553, 40
  %3555 = or i64 %3554, %3550
  %3556 = getelementptr inbounds nuw i8, ptr %77, i64 30
  %3557 = load i8, ptr %3556, align 2, !tbaa !9
  %3558 = zext i8 %3557 to i64
  %3559 = shl nuw nsw i64 %3558, 48
  %3560 = or i64 %3559, %3555
  %3561 = getelementptr inbounds nuw i8, ptr %77, i64 31
  %3562 = load i8, ptr %3561, align 1, !tbaa !9
  %3563 = zext i8 %3562 to i64
  %3564 = shl nuw i64 %3563, 56
  %3565 = or i64 %3564, %3560
  %3566 = icmp sgt i64 %3565, -1
  br i1 %3566, label %2724, label %2834

3567:                                             ; preds = %3169
  %3568 = getelementptr inbounds [8 x i8], ptr %85, i64 %3170
  store i64 %3154, ptr %3568, align 8, !tbaa !10
  %3569 = load i64, ptr %85, align 16, !tbaa !10
  %3570 = icmp eq i64 %3569, 0
  br i1 %3570, label %3579, label %3571

3571:                                             ; preds = %3567, %3571
  %3572 = phi i64 [ %3577, %3571 ], [ %3569, %3567 ]
  %3573 = phi ptr [ %3576, %3571 ], [ %85, %3567 ]
  %3574 = getelementptr inbounds [8 x i8], ptr %85, i64 %3572
  %3575 = load i64, ptr %3574, align 8, !tbaa !10
  store i64 %3575, ptr %3573, align 8, !tbaa !10
  %3576 = getelementptr inbounds [8 x i8], ptr %85, i64 %3575
  %3577 = load i64, ptr %3576, align 8, !tbaa !10
  %3578 = icmp eq i64 %3577, %3575
  br i1 %3578, label %3579, label %3571, !llvm.loop !34

3579:                                             ; preds = %3571, %3567
  %3580 = phi i64 [ 0, %3567 ], [ %3575, %3571 ]
  %3581 = load i64, ptr %3149, align 8, !tbaa !10
  %3582 = icmp eq i64 %3581, 3
  br i1 %3582, label %3591, label %3583

3583:                                             ; preds = %3579, %3583
  %3584 = phi i64 [ %3589, %3583 ], [ %3581, %3579 ]
  %3585 = phi ptr [ %3588, %3583 ], [ %3149, %3579 ]
  %3586 = getelementptr inbounds [8 x i8], ptr %85, i64 %3584
  %3587 = load i64, ptr %3586, align 8, !tbaa !10
  store i64 %3587, ptr %3585, align 8, !tbaa !10
  %3588 = getelementptr inbounds [8 x i8], ptr %85, i64 %3587
  %3589 = load i64, ptr %3588, align 8, !tbaa !10
  %3590 = icmp eq i64 %3589, %3587
  br i1 %3590, label %3591, label %3583, !llvm.loop !34

3591:                                             ; preds = %3583, %3579
  %3592 = phi i64 [ 3, %3579 ], [ %3587, %3583 ]
  %3593 = icmp eq i64 %3580, %3592
  %3594 = select i1 %3593, ptr @.str.1, ptr @.str.2
  br label %3595

3595:                                             ; preds = %3591, %3169
  %3596 = phi ptr [ @.str.2, %3169 ], [ %3594, %3591 ]
  %3597 = call i32 (ptr, ...) @printf(ptr noundef nonnull dereferenceable(1) @.str.16, ptr noundef nonnull %3596)
  %3598 = call i32 (ptr, ...) @printf(ptr noundef nonnull dereferenceable(1) @.str.17, ptr noundef nonnull @.str.1)
  call void @llvm.lifetime.start.p0(ptr nonnull %86) #9
  store i64 3, ptr %86, align 16
  %3599 = getelementptr inbounds nuw i8, ptr %86, i64 8
  store i64 7, ptr %3599, align 8
  %3600 = getelementptr inbounds nuw i8, ptr %86, i64 16
  store i64 3, ptr %3600, align 16
  %3601 = getelementptr inbounds nuw i8, ptr %86, i64 24
  store i64 9, ptr %3601, align 8
  %3602 = getelementptr inbounds nuw i8, ptr %86, i64 32
  store i64 -1, ptr %3602, align 16
  call void @llvm.lifetime.start.p0(ptr nonnull %87) #9
  call void @llvm.lifetime.start.p0(ptr nonnull %88) #9
  call void @llvm.lifetime.start.p0(ptr nonnull %89) #9
  store ptr %86, ptr %89, align 8, !tbaa !15
  %3603 = getelementptr inbounds nuw i8, ptr %89, i64 8
  store i64 5, ptr %3603, align 8, !tbaa !19
  %3604 = getelementptr inbounds nuw i8, ptr %89, i64 16
  store i64 8, ptr %3604, align 8, !tbaa !20
  %3605 = getelementptr inbounds nuw i8, ptr %89, i64 24
  store i64 8, ptr %3605, align 8, !tbaa !21
  call void @llvm.lifetime.start.p0(ptr nonnull %90) #9
  store ptr %87, ptr %90, align 8, !tbaa !15
  %3606 = getelementptr inbounds nuw i8, ptr %90, i64 8
  store i64 8, ptr %3606, align 8, !tbaa !19
  %3607 = getelementptr inbounds nuw i8, ptr %90, i64 16
  store i64 8, ptr %3607, align 8, !tbaa !20
  %3608 = getelementptr inbounds nuw i8, ptr %90, i64 24
  store i64 8, ptr %3608, align 8, !tbaa !21
  call void @llvm.lifetime.start.p0(ptr nonnull %91) #9
  store ptr %88, ptr %91, align 8, !tbaa !15
  %3609 = getelementptr inbounds nuw i8, ptr %91, i64 8
  store i64 5, ptr %3609, align 8, !tbaa !19
  %3610 = getelementptr inbounds nuw i8, ptr %91, i64 16
  store i64 8, ptr %3610, align 8, !tbaa !20
  %3611 = getelementptr inbounds nuw i8, ptr %91, i64 24
  store i64 8, ptr %3611, align 8, !tbaa !21
  call fastcc void @build_index(ptr noundef %89, ptr noundef %90, ptr noundef %91)
  store i8 3, ptr %3602, align 16, !tbaa !9
  %3612 = getelementptr inbounds nuw i8, ptr %86, i64 33
  %3613 = getelementptr inbounds nuw i8, ptr %87, i64 24
  call void @llvm.memset.p0.i64(ptr noundef nonnull align 1 dereferenceable(7) %3612, i8 0, i64 7, i1 false)
  %3614 = load i8, ptr %3613, align 8, !tbaa !9
  %3615 = zext i8 %3614 to i64
  %3616 = getelementptr inbounds nuw i8, ptr %87, i64 25
  %3617 = load i8, ptr %3616, align 1, !tbaa !9
  %3618 = zext i8 %3617 to i64
  %3619 = shl nuw nsw i64 %3618, 8
  %3620 = or disjoint i64 %3619, %3615
  %3621 = getelementptr inbounds nuw i8, ptr %87, i64 26
  %3622 = load i8, ptr %3621, align 2, !tbaa !9
  %3623 = zext i8 %3622 to i64
  %3624 = shl nuw nsw i64 %3623, 16
  %3625 = getelementptr inbounds nuw i8, ptr %87, i64 27
  %3626 = load i8, ptr %3625, align 1, !tbaa !9
  %3627 = zext i8 %3626 to i64
  %3628 = shl nuw nsw i64 %3627, 24
  %3629 = or disjoint i64 %3628, %3620
  %3630 = or disjoint i64 %3629, %3624
  %3631 = getelementptr inbounds nuw i8, ptr %87, i64 28
  %3632 = load i8, ptr %3631, align 4, !tbaa !9
  %3633 = zext i8 %3632 to i64
  %3634 = shl nuw nsw i64 %3633, 32
  %3635 = getelementptr inbounds nuw i8, ptr %87, i64 29
  %3636 = load i8, ptr %3635, align 1, !tbaa !9
  %3637 = zext i8 %3636 to i64
  %3638 = shl nuw nsw i64 %3637, 40
  %3639 = or disjoint i64 %3634, %3638
  %3640 = or disjoint i64 %3639, %3630
  %3641 = getelementptr inbounds nuw i8, ptr %87, i64 30
  %3642 = load i8, ptr %3641, align 2, !tbaa !9
  %3643 = zext i8 %3642 to i64
  %3644 = shl nuw nsw i64 %3643, 48
  %3645 = getelementptr inbounds nuw i8, ptr %87, i64 31
  %3646 = load i8, ptr %3645, align 1, !tbaa !9
  %3647 = zext i8 %3646 to i64
  %3648 = shl nuw i64 %3647, 56
  %3649 = or disjoint i64 %3644, %3648
  %3650 = or disjoint i64 %3649, %3640
  %3651 = getelementptr inbounds nuw i8, ptr %88, i64 32
  store i8 %3614, ptr %3651, align 16, !tbaa !9
  %3652 = getelementptr inbounds nuw i8, ptr %88, i64 33
  store i8 %3617, ptr %3652, align 1, !tbaa !9
  %3653 = getelementptr inbounds nuw i8, ptr %88, i64 34
  store i8 %3622, ptr %3653, align 2, !tbaa !9
  %3654 = getelementptr inbounds nuw i8, ptr %88, i64 35
  store i8 %3626, ptr %3654, align 1, !tbaa !9
  %3655 = lshr i64 %3640, 32
  %3656 = trunc i64 %3655 to i8
  %3657 = getelementptr inbounds nuw i8, ptr %88, i64 36
  store i8 %3656, ptr %3657, align 4, !tbaa !9
  %3658 = lshr i64 %3640, 40
  %3659 = trunc nuw i64 %3658 to i8
  %3660 = getelementptr inbounds nuw i8, ptr %88, i64 37
  store i8 %3659, ptr %3660, align 1, !tbaa !9
  %3661 = lshr i64 %3650, 48
  %3662 = trunc i64 %3661 to i8
  %3663 = getelementptr inbounds nuw i8, ptr %88, i64 38
  store i8 %3662, ptr %3663, align 2, !tbaa !9
  %3664 = lshr i64 %3650, 56
  %3665 = trunc nuw i64 %3664 to i8
  %3666 = getelementptr inbounds nuw i8, ptr %88, i64 39
  store i8 %3665, ptr %3666, align 1, !tbaa !9
  store i8 4, ptr %3613, align 8, !tbaa !9
  call void @llvm.memset.p0.i64(ptr noundef nonnull align 1 dereferenceable(7) %3616, i8 0, i64 7, i1 false)
  br label %3667

3667:                                             ; preds = %3595, %3667
  %3668 = phi i64 [ %3749, %3667 ], [ 4, %3595 ]
  %3669 = phi i64 [ %3711, %3667 ], [ 0, %3595 ]
  %3670 = shl nsw i64 %3668, 3
  %3671 = getelementptr inbounds nuw i8, ptr %86, i64 %3670
  %3672 = load i8, ptr %3671, align 8, !tbaa !9
  %3673 = zext i8 %3672 to i64
  %3674 = getelementptr inbounds nuw i8, ptr %3671, i64 1
  %3675 = load i8, ptr %3674, align 1, !tbaa !9
  %3676 = zext i8 %3675 to i64
  %3677 = shl nuw nsw i64 %3676, 8
  %3678 = or disjoint i64 %3677, %3673
  %3679 = getelementptr inbounds nuw i8, ptr %3671, i64 2
  %3680 = load i8, ptr %3679, align 2, !tbaa !9
  %3681 = zext i8 %3680 to i64
  %3682 = shl nuw nsw i64 %3681, 16
  %3683 = or disjoint i64 %3682, %3678
  %3684 = getelementptr inbounds nuw i8, ptr %3671, i64 3
  %3685 = load i8, ptr %3684, align 1, !tbaa !9
  %3686 = zext i8 %3685 to i64
  %3687 = shl nuw nsw i64 %3686, 24
  %3688 = or disjoint i64 %3687, %3683
  %3689 = getelementptr inbounds nuw i8, ptr %3671, i64 4
  %3690 = load i8, ptr %3689, align 4, !tbaa !9
  %3691 = zext i8 %3690 to i64
  %3692 = shl nuw nsw i64 %3691, 32
  %3693 = or disjoint i64 %3692, %3688
  %3694 = getelementptr inbounds nuw i8, ptr %3671, i64 5
  %3695 = load i8, ptr %3694, align 1, !tbaa !9
  %3696 = zext i8 %3695 to i64
  %3697 = shl nuw nsw i64 %3696, 40
  %3698 = or i64 %3697, %3693
  %3699 = getelementptr inbounds nuw i8, ptr %3671, i64 6
  %3700 = load i8, ptr %3699, align 2, !tbaa !9
  %3701 = zext i8 %3700 to i64
  %3702 = shl nuw nsw i64 %3701, 48
  %3703 = or i64 %3702, %3698
  %3704 = getelementptr inbounds nuw i8, ptr %3671, i64 7
  %3705 = load i8, ptr %3704, align 1, !tbaa !9
  %3706 = zext i8 %3705 to i64
  %3707 = shl nuw i64 %3706, 56
  %3708 = or i64 %3707, %3703
  %3709 = icmp eq i64 %3708, 3
  %3710 = zext i1 %3709 to i64
  %3711 = add nuw nsw i64 %3669, %3710
  %3712 = getelementptr inbounds nuw i8, ptr %88, i64 %3670
  %3713 = load i8, ptr %3712, align 8, !tbaa !9
  %3714 = zext i8 %3713 to i64
  %3715 = getelementptr inbounds nuw i8, ptr %3712, i64 1
  %3716 = load i8, ptr %3715, align 1, !tbaa !9
  %3717 = zext i8 %3716 to i64
  %3718 = shl nuw nsw i64 %3717, 8
  %3719 = or disjoint i64 %3718, %3714
  %3720 = getelementptr inbounds nuw i8, ptr %3712, i64 2
  %3721 = load i8, ptr %3720, align 2, !tbaa !9
  %3722 = zext i8 %3721 to i64
  %3723 = shl nuw nsw i64 %3722, 16
  %3724 = or disjoint i64 %3723, %3719
  %3725 = getelementptr inbounds nuw i8, ptr %3712, i64 3
  %3726 = load i8, ptr %3725, align 1, !tbaa !9
  %3727 = zext i8 %3726 to i64
  %3728 = shl nuw nsw i64 %3727, 24
  %3729 = or disjoint i64 %3728, %3724
  %3730 = getelementptr inbounds nuw i8, ptr %3712, i64 4
  %3731 = load i8, ptr %3730, align 4, !tbaa !9
  %3732 = zext i8 %3731 to i64
  %3733 = shl nuw nsw i64 %3732, 32
  %3734 = or disjoint i64 %3733, %3729
  %3735 = getelementptr inbounds nuw i8, ptr %3712, i64 5
  %3736 = load i8, ptr %3735, align 1, !tbaa !9
  %3737 = zext i8 %3736 to i64
  %3738 = shl nuw nsw i64 %3737, 40
  %3739 = or i64 %3738, %3734
  %3740 = getelementptr inbounds nuw i8, ptr %3712, i64 6
  %3741 = load i8, ptr %3740, align 2, !tbaa !9
  %3742 = zext i8 %3741 to i64
  %3743 = shl nuw nsw i64 %3742, 48
  %3744 = or i64 %3743, %3739
  %3745 = getelementptr inbounds nuw i8, ptr %3712, i64 7
  %3746 = load i8, ptr %3745, align 1, !tbaa !9
  %3747 = zext i8 %3746 to i64
  %3748 = shl nuw i64 %3747, 56
  %3749 = or i64 %3748, %3744
  %3750 = icmp sgt i64 %3749, -1
  br i1 %3750, label %3667, label %3751, !llvm.loop !31

3751:                                             ; preds = %3667
  %3752 = load i8, ptr %86, align 16, !tbaa !9
  %3753 = getelementptr inbounds nuw i8, ptr %86, i64 1
  %3754 = load i8, ptr %3753, align 1, !tbaa !9
  %3755 = getelementptr inbounds nuw i8, ptr %86, i64 2
  %3756 = load i8, ptr %3755, align 2, !tbaa !9
  %3757 = getelementptr inbounds nuw i8, ptr %86, i64 3
  %3758 = load i8, ptr %3757, align 1, !tbaa !9
  %3759 = getelementptr inbounds nuw i8, ptr %86, i64 4
  %3760 = load i8, ptr %3759, align 4, !tbaa !9
  %3761 = getelementptr inbounds nuw i8, ptr %86, i64 5
  %3762 = load i8, ptr %3761, align 1, !tbaa !9
  %3763 = getelementptr inbounds nuw i8, ptr %86, i64 6
  %3764 = load i8, ptr %3763, align 2, !tbaa !9
  %3765 = getelementptr inbounds nuw i8, ptr %86, i64 7
  %3766 = load i8, ptr %3765, align 1, !tbaa !9
  store i64 -1, ptr %86, align 16
  %3767 = zext i8 %3752 to i64
  %3768 = zext i8 %3754 to i64
  %3769 = shl nuw nsw i64 %3768, 8
  %3770 = or disjoint i64 %3769, %3767
  %3771 = zext i8 %3756 to i64
  %3772 = shl nuw nsw i64 %3771, 16
  %3773 = or disjoint i64 %3772, %3770
  %3774 = zext i8 %3758 to i64
  %3775 = shl nuw nsw i64 %3774, 24
  %3776 = or disjoint i64 %3775, %3773
  %3777 = zext i8 %3760 to i64
  %3778 = shl nuw nsw i64 %3777, 32
  %3779 = or disjoint i64 %3778, %3776
  %3780 = zext i8 %3762 to i64
  %3781 = shl nuw nsw i64 %3780, 40
  %3782 = or i64 %3781, %3779
  %3783 = zext i8 %3764 to i64
  %3784 = shl nuw nsw i64 %3783, 48
  %3785 = or i64 %3784, %3782
  %3786 = zext i8 %3766 to i64
  %3787 = shl nuw i64 %3786, 56
  %3788 = or i64 %3787, %3785
  br label %3789

3789:                                             ; preds = %3751, %3789
  %3790 = phi i64 [ %3871, %3789 ], [ 4, %3751 ]
  %3791 = phi i64 [ %3833, %3789 ], [ 0, %3751 ]
  %3792 = shl nsw i64 %3790, 3
  %3793 = getelementptr inbounds nuw i8, ptr %86, i64 %3792
  %3794 = load i8, ptr %3793, align 8, !tbaa !9
  %3795 = zext i8 %3794 to i64
  %3796 = getelementptr inbounds nuw i8, ptr %3793, i64 1
  %3797 = load i8, ptr %3796, align 1, !tbaa !9
  %3798 = zext i8 %3797 to i64
  %3799 = shl nuw nsw i64 %3798, 8
  %3800 = or disjoint i64 %3799, %3795
  %3801 = getelementptr inbounds nuw i8, ptr %3793, i64 2
  %3802 = load i8, ptr %3801, align 2, !tbaa !9
  %3803 = zext i8 %3802 to i64
  %3804 = shl nuw nsw i64 %3803, 16
  %3805 = or disjoint i64 %3804, %3800
  %3806 = getelementptr inbounds nuw i8, ptr %3793, i64 3
  %3807 = load i8, ptr %3806, align 1, !tbaa !9
  %3808 = zext i8 %3807 to i64
  %3809 = shl nuw nsw i64 %3808, 24
  %3810 = or disjoint i64 %3809, %3805
  %3811 = getelementptr inbounds nuw i8, ptr %3793, i64 4
  %3812 = load i8, ptr %3811, align 4, !tbaa !9
  %3813 = zext i8 %3812 to i64
  %3814 = shl nuw nsw i64 %3813, 32
  %3815 = or disjoint i64 %3814, %3810
  %3816 = getelementptr inbounds nuw i8, ptr %3793, i64 5
  %3817 = load i8, ptr %3816, align 1, !tbaa !9
  %3818 = zext i8 %3817 to i64
  %3819 = shl nuw nsw i64 %3818, 40
  %3820 = or i64 %3819, %3815
  %3821 = getelementptr inbounds nuw i8, ptr %3793, i64 6
  %3822 = load i8, ptr %3821, align 2, !tbaa !9
  %3823 = zext i8 %3822 to i64
  %3824 = shl nuw nsw i64 %3823, 48
  %3825 = or i64 %3824, %3820
  %3826 = getelementptr inbounds nuw i8, ptr %3793, i64 7
  %3827 = load i8, ptr %3826, align 1, !tbaa !9
  %3828 = zext i8 %3827 to i64
  %3829 = shl nuw i64 %3828, 56
  %3830 = or i64 %3829, %3825
  %3831 = icmp eq i64 %3830, 3
  %3832 = zext i1 %3831 to i64
  %3833 = add nuw nsw i64 %3791, %3832
  %3834 = getelementptr inbounds nuw i8, ptr %88, i64 %3792
  %3835 = load i8, ptr %3834, align 8, !tbaa !9
  %3836 = zext i8 %3835 to i64
  %3837 = getelementptr inbounds nuw i8, ptr %3834, i64 1
  %3838 = load i8, ptr %3837, align 1, !tbaa !9
  %3839 = zext i8 %3838 to i64
  %3840 = shl nuw nsw i64 %3839, 8
  %3841 = or disjoint i64 %3840, %3836
  %3842 = getelementptr inbounds nuw i8, ptr %3834, i64 2
  %3843 = load i8, ptr %3842, align 2, !tbaa !9
  %3844 = zext i8 %3843 to i64
  %3845 = shl nuw nsw i64 %3844, 16
  %3846 = or disjoint i64 %3845, %3841
  %3847 = getelementptr inbounds nuw i8, ptr %3834, i64 3
  %3848 = load i8, ptr %3847, align 1, !tbaa !9
  %3849 = zext i8 %3848 to i64
  %3850 = shl nuw nsw i64 %3849, 24
  %3851 = or disjoint i64 %3850, %3846
  %3852 = getelementptr inbounds nuw i8, ptr %3834, i64 4
  %3853 = load i8, ptr %3852, align 4, !tbaa !9
  %3854 = zext i8 %3853 to i64
  %3855 = shl nuw nsw i64 %3854, 32
  %3856 = or disjoint i64 %3855, %3851
  %3857 = getelementptr inbounds nuw i8, ptr %3834, i64 5
  %3858 = load i8, ptr %3857, align 1, !tbaa !9
  %3859 = zext i8 %3858 to i64
  %3860 = shl nuw nsw i64 %3859, 40
  %3861 = or i64 %3860, %3856
  %3862 = getelementptr inbounds nuw i8, ptr %3834, i64 6
  %3863 = load i8, ptr %3862, align 2, !tbaa !9
  %3864 = zext i8 %3863 to i64
  %3865 = shl nuw nsw i64 %3864, 48
  %3866 = or i64 %3865, %3861
  %3867 = getelementptr inbounds nuw i8, ptr %3834, i64 7
  %3868 = load i8, ptr %3867, align 1, !tbaa !9
  %3869 = zext i8 %3868 to i64
  %3870 = shl nuw i64 %3869, 56
  %3871 = or i64 %3870, %3866
  %3872 = icmp sgt i64 %3871, -1
  br i1 %3872, label %3789, label %3873, !llvm.loop !31

3873:                                             ; preds = %3789
  %3874 = icmp eq i64 %3711, 3
  %3875 = icmp eq i64 %3788, 3
  %3876 = select i1 %3874, i1 %3875, i1 false
  %3877 = icmp eq i64 %3833, 2
  %3878 = select i1 %3876, i1 %3877, i1 false
  %3879 = select i1 %3878, ptr @.str.1, ptr @.str.2
  %3880 = call i32 (ptr, ...) @printf(ptr noundef nonnull dereferenceable(1) @.str.18, ptr noundef nonnull %3879, i64 noundef %3711, i64 noundef %3788, i64 noundef %3833)
  %3881 = call i32 (ptr, ...) @printf(ptr noundef nonnull dereferenceable(1) @.str.19, ptr noundef nonnull @.str.1, i64 noundef 45426, i64 noundef 45426)
  %3882 = call i32 (ptr, ...) @printf(ptr noundef nonnull dereferenceable(1) @.str.20, ptr noundef nonnull @.str.1)
  %3883 = call i32 (ptr, ...) @printf(ptr noundef nonnull dereferenceable(1) @.str.21, ptr noundef nonnull @.str.1, i64 noundef 6543778)
  %3884 = call i32 (ptr, ...) @printf(ptr noundef nonnull dereferenceable(1) @.str.22, ptr noundef nonnull @.str.1, i64 noundef 65536, i64 noundef 0)
  call void @llvm.lifetime.start.p0(ptr nonnull %92) #9
  call void @llvm.memset.p0.i64(ptr noundef nonnull align 16 dereferenceable(72) %92, i8 0, i64 64, i1 false)
  store i64 65536, ptr %92, align 16
  %3885 = getelementptr inbounds nuw i8, ptr %92, i64 32
  store i64 65536, ptr %3885, align 16
  %3886 = getelementptr inbounds nuw i8, ptr %92, i64 64
  store i64 65536, ptr %3886, align 16
  call void @llvm.lifetime.start.p0(ptr nonnull %93) #9
  call void @llvm.memset.p0.i64(ptr noundef nonnull align 16 dereferenceable(24) %93, i8 0, i64 24, i1 false)
  call void @llvm.lifetime.start.p0(ptr nonnull %94) #9
  call void @llvm.memcpy.p0.p0.i64(ptr noundef nonnull align 16 dereferenceable(24) %94, ptr noundef nonnull align 16 dereferenceable(24) @__const.main.lg3, i64 24, i1 false)
  call void @llvm.lifetime.start.p0(ptr nonnull %95) #9
  call void @llvm.memset.p0.i64(ptr noundef nonnull align 16 dereferenceable(24) %95, i8 0, i64 24, i1 false)
  call void @llvm.lifetime.start.p0(ptr nonnull %96) #9
  call void @llvm.lifetime.start.p0(ptr nonnull %97) #9
  store ptr %94, ptr %97, align 8, !tbaa !15
  %3887 = getelementptr inbounds nuw i8, ptr %97, i64 8
  store i64 3, ptr %3887, align 8, !tbaa !19
  %3888 = getelementptr inbounds nuw i8, ptr %97, i64 16
  store i64 8, ptr %3888, align 8, !tbaa !20
  %3889 = getelementptr inbounds nuw i8, ptr %97, i64 24
  store i64 8, ptr %3889, align 8, !tbaa !21
  call void @llvm.lifetime.start.p0(ptr nonnull %98) #9
  store ptr %95, ptr %98, align 8, !tbaa !15
  %3890 = getelementptr inbounds nuw i8, ptr %98, i64 8
  store i64 3, ptr %3890, align 8, !tbaa !19
  %3891 = getelementptr inbounds nuw i8, ptr %98, i64 16
  store i64 8, ptr %3891, align 8, !tbaa !20
  %3892 = getelementptr inbounds nuw i8, ptr %98, i64 24
  store i64 8, ptr %3892, align 8, !tbaa !21
  call void @llvm.lifetime.start.p0(ptr nonnull %99) #9
  store ptr %96, ptr %99, align 8, !tbaa !15
  %3893 = getelementptr inbounds nuw i8, ptr %99, i64 8
  store i64 3, ptr %3893, align 8, !tbaa !19
  %3894 = getelementptr inbounds nuw i8, ptr %99, i64 16
  store i64 8, ptr %3894, align 8, !tbaa !20
  %3895 = getelementptr inbounds nuw i8, ptr %99, i64 24
  store i64 8, ptr %3895, align 8, !tbaa !21
  call void @llvm.lifetime.start.p0(ptr nonnull %10) #9
  br label %3896

3896:                                             ; preds = %3896, %3873
  %3897 = phi i64 [ 0, %3873 ], [ %4059, %3896 ]
  %3898 = mul nuw nsw i64 %3897, 24
  %3899 = getelementptr i8, ptr %92, i64 %3898
  %3900 = load i8, ptr %3899, align 8, !tbaa !9
  %3901 = getelementptr inbounds nuw i8, ptr %3899, i64 1
  %3902 = load i8, ptr %3901, align 1, !tbaa !9
  %3903 = getelementptr inbounds nuw i8, ptr %3899, i64 2
  %3904 = load i8, ptr %3903, align 2, !tbaa !9
  %3905 = getelementptr inbounds nuw i8, ptr %3899, i64 3
  %3906 = load i8, ptr %3905, align 1, !tbaa !9
  %3907 = getelementptr inbounds nuw i8, ptr %3899, i64 4
  %3908 = load i8, ptr %3907, align 4, !tbaa !9
  %3909 = getelementptr inbounds nuw i8, ptr %3899, i64 5
  %3910 = load i8, ptr %3909, align 1, !tbaa !9
  %3911 = getelementptr inbounds nuw i8, ptr %3899, i64 6
  %3912 = load i8, ptr %3911, align 2, !tbaa !9
  %3913 = getelementptr inbounds nuw i8, ptr %3899, i64 7
  %3914 = load i8, ptr %3913, align 1, !tbaa !9
  %3915 = getelementptr i8, ptr %3899, i64 8
  %3916 = load i8, ptr %3915, align 8, !tbaa !9
  %3917 = getelementptr i8, ptr %3899, i64 9
  %3918 = load i8, ptr %3917, align 1, !tbaa !9
  %3919 = getelementptr i8, ptr %3899, i64 10
  %3920 = load i8, ptr %3919, align 2, !tbaa !9
  %3921 = getelementptr i8, ptr %3899, i64 11
  %3922 = load i8, ptr %3921, align 1, !tbaa !9
  %3923 = getelementptr i8, ptr %3899, i64 12
  %3924 = load i8, ptr %3923, align 4, !tbaa !9
  %3925 = getelementptr i8, ptr %3899, i64 13
  %3926 = load i8, ptr %3925, align 1, !tbaa !9
  %3927 = getelementptr i8, ptr %3899, i64 14
  %3928 = load i8, ptr %3927, align 2, !tbaa !9
  %3929 = getelementptr i8, ptr %3899, i64 15
  %3930 = load i8, ptr %3929, align 1, !tbaa !9
  %3931 = getelementptr i8, ptr %3899, i64 16
  %3932 = load i8, ptr %3931, align 8, !tbaa !9
  %3933 = getelementptr i8, ptr %3899, i64 17
  %3934 = load i8, ptr %3933, align 1, !tbaa !9
  %3935 = getelementptr i8, ptr %3899, i64 18
  %3936 = load i8, ptr %3935, align 2, !tbaa !9
  %3937 = getelementptr i8, ptr %3899, i64 19
  %3938 = load i8, ptr %3937, align 1, !tbaa !9
  %3939 = getelementptr i8, ptr %3899, i64 20
  %3940 = load i8, ptr %3939, align 4, !tbaa !9
  %3941 = getelementptr i8, ptr %3899, i64 21
  %3942 = load i8, ptr %3941, align 1, !tbaa !9
  %3943 = getelementptr i8, ptr %3899, i64 22
  %3944 = load i8, ptr %3943, align 2, !tbaa !9
  %3945 = getelementptr i8, ptr %3899, i64 23
  %3946 = load i8, ptr %3945, align 1, !tbaa !9
  %3947 = shl nsw i64 %3897, 3
  %3948 = getelementptr inbounds nuw i8, ptr %93, i64 %3947
  %3949 = load i8, ptr %3948, align 8, !tbaa !9
  %3950 = zext i8 %3949 to i64
  %3951 = getelementptr inbounds nuw i8, ptr %3948, i64 1
  %3952 = load i8, ptr %3951, align 1, !tbaa !9
  %3953 = zext i8 %3952 to i64
  %3954 = shl nuw nsw i64 %3953, 8
  %3955 = or disjoint i64 %3954, %3950
  %3956 = getelementptr inbounds nuw i8, ptr %3948, i64 2
  %3957 = load i8, ptr %3956, align 2, !tbaa !9
  %3958 = zext i8 %3957 to i64
  %3959 = shl nuw nsw i64 %3958, 16
  %3960 = or disjoint i64 %3959, %3955
  %3961 = getelementptr inbounds nuw i8, ptr %3948, i64 3
  %3962 = load i8, ptr %3961, align 1, !tbaa !9
  %3963 = zext i8 %3962 to i64
  %3964 = shl nuw nsw i64 %3963, 24
  %3965 = or disjoint i64 %3964, %3960
  %3966 = getelementptr inbounds nuw i8, ptr %3948, i64 4
  %3967 = load i8, ptr %3966, align 4, !tbaa !9
  %3968 = zext i8 %3967 to i64
  %3969 = shl nuw nsw i64 %3968, 32
  %3970 = or disjoint i64 %3969, %3965
  %3971 = getelementptr inbounds nuw i8, ptr %3948, i64 5
  %3972 = load i8, ptr %3971, align 1, !tbaa !9
  %3973 = zext i8 %3972 to i64
  %3974 = shl nuw nsw i64 %3973, 40
  %3975 = or i64 %3974, %3970
  %3976 = getelementptr inbounds nuw i8, ptr %3948, i64 6
  %3977 = load i8, ptr %3976, align 2, !tbaa !9
  %3978 = zext i8 %3977 to i64
  %3979 = shl nuw nsw i64 %3978, 48
  %3980 = or i64 %3979, %3975
  %3981 = getelementptr inbounds nuw i8, ptr %3948, i64 7
  %3982 = load i8, ptr %3981, align 1, !tbaa !9
  %3983 = zext i8 %3982 to i64
  %3984 = shl nuw i64 %3983, 56
  %3985 = or i64 %3984, %3980
  %3986 = zext i8 %3932 to i64
  %3987 = zext i8 %3934 to i64
  %3988 = shl nuw nsw i64 %3987, 8
  %3989 = or disjoint i64 %3988, %3986
  %3990 = zext i8 %3936 to i64
  %3991 = shl nuw nsw i64 %3990, 16
  %3992 = or disjoint i64 %3991, %3989
  %3993 = zext i8 %3938 to i64
  %3994 = shl nuw nsw i64 %3993, 24
  %3995 = or disjoint i64 %3994, %3992
  %3996 = zext i8 %3940 to i64
  %3997 = shl nuw nsw i64 %3996, 32
  %3998 = or disjoint i64 %3997, %3995
  %3999 = zext i8 %3942 to i64
  %4000 = shl nuw nsw i64 %3999, 40
  %4001 = or i64 %4000, %3998
  %4002 = zext i8 %3944 to i64
  %4003 = shl nuw nsw i64 %4002, 48
  %4004 = or i64 %4003, %4001
  %4005 = zext i8 %3946 to i64
  %4006 = shl nuw i64 %4005, 56
  %4007 = or i64 %4006, %4004
  %4008 = zext i8 %3916 to i64
  %4009 = zext i8 %3918 to i64
  %4010 = zext i8 %3920 to i64
  %4011 = zext i8 %3922 to i64
  %4012 = zext i8 %3924 to i64
  %4013 = zext i8 %3926 to i64
  %4014 = zext i8 %3928 to i64
  %4015 = zext i8 %3930 to i64
  %4016 = zext i8 %3900 to i64
  %4017 = zext i8 %3902 to i64
  %4018 = shl nuw nsw i64 %4017, 8
  %4019 = or disjoint i64 %4018, %4016
  %4020 = zext i8 %3904 to i64
  %4021 = shl nuw nsw i64 %4020, 16
  %4022 = or disjoint i64 %4021, %4019
  %4023 = zext i8 %3906 to i64
  %4024 = shl nuw nsw i64 %4023, 24
  %4025 = or disjoint i64 %4024, %4022
  %4026 = zext i8 %3908 to i64
  %4027 = shl nuw nsw i64 %4026, 32
  %4028 = or disjoint i64 %4027, %4025
  %4029 = zext i8 %3910 to i64
  %4030 = shl nuw nsw i64 %4029, 40
  %4031 = or i64 %4030, %4028
  %4032 = zext i8 %3912 to i64
  %4033 = shl nuw nsw i64 %4032, 48
  %4034 = or i64 %4033, %4031
  %4035 = zext i8 %3914 to i64
  %4036 = shl nuw i64 %4035, 56
  %4037 = or i64 %4036, %4034
  %4038 = shl i64 %4015, 57
  %4039 = shl nuw nsw i64 %4014, 49
  %4040 = shl nuw nsw i64 %4013, 41
  %4041 = shl nuw nsw i64 %4012, 33
  %4042 = shl nuw nsw i64 %4011, 25
  %4043 = shl nuw nsw i64 %4010, 17
  %4044 = shl nuw nsw i64 %4009, 9
  %4045 = shl nuw nsw i64 %4008, 1
  %4046 = or disjoint i64 %4044, %4045
  %4047 = or disjoint i64 %4043, %4046
  %4048 = or disjoint i64 %4042, %4047
  %4049 = or disjoint i64 %4041, %4048
  %4050 = or i64 %4040, %4049
  %4051 = or i64 %4039, %4050
  %4052 = or i64 %4038, %4051
  %4053 = add nsw i64 %4052, %4037
  %4054 = mul nsw i64 %4007, 196608
  %4055 = ashr exact i64 %4054, 16
  %4056 = add nsw i64 %4053, %4055
  %4057 = add nsw i64 %4056, %3985
  %4058 = getelementptr inbounds nuw [8 x i8], ptr %10, i64 %3897
  store i64 %4057, ptr %4058, align 8, !tbaa !10
  %4059 = add nuw nsw i64 %3897, 1
  %4060 = icmp eq i64 %4059, 3
  br i1 %4060, label %4061, label %3896, !llvm.loop !12

4061:                                             ; preds = %3896
  call void @llvm.lifetime.start.p0(ptr nonnull %11) #9
  store ptr %10, ptr %11, align 8, !tbaa !15
  %4062 = getelementptr inbounds nuw i8, ptr %11, i64 8
  store i64 3, ptr %4062, align 8, !tbaa !19
  %4063 = getelementptr inbounds nuw i8, ptr %11, i64 16
  store i64 8, ptr %4063, align 8, !tbaa !20
  %4064 = getelementptr inbounds nuw i8, ptr %11, i64 24
  store i64 8, ptr %4064, align 8, !tbaa !21
  call fastcc void @layernorm(ptr noundef %11, i64 noundef 3, ptr noundef nonnull readonly %97, ptr noundef nonnull readonly %98, ptr noundef nonnull readonly %99)
  call void @llvm.lifetime.end.p0(ptr nonnull %11) #9
  call void @llvm.lifetime.end.p0(ptr nonnull %10) #9
  %4065 = load i64, ptr %96, align 16, !tbaa !10
  %4066 = getelementptr inbounds nuw i8, ptr %96, i64 8
  %4067 = load i64, ptr %4066, align 8, !tbaa !10
  %4068 = add nsw i64 %4067, %4065
  %4069 = getelementptr inbounds nuw i8, ptr %96, i64 16
  %4070 = load i64, ptr %4069, align 16, !tbaa !10
  %4071 = add nsw i64 %4070, %4068
  %4072 = add i64 %4071, 9
  %4073 = icmp ult i64 %4072, 19
  %4074 = select i1 %4073, ptr @.str.1, ptr @.str.2
  %4075 = call i32 (ptr, ...) @printf(ptr noundef nonnull dereferenceable(1) @.str.23, ptr noundef nonnull %4074, i64 noundef %4071)
  call void @llvm.lifetime.start.p0(ptr nonnull %100) #9
  call void @llvm.lifetime.start.p0(ptr nonnull %1) #9
  call void @llvm.memset.p0.i64(ptr noundef nonnull align 16 dereferenceable(64) %1, i8 0, i64 64, i1 false)
  store i8 1, ptr %1, align 16, !tbaa !9
  %4076 = getelementptr inbounds nuw i8, ptr %1, i64 1
  store i8 1, ptr %4076, align 1, !tbaa !9
  %4077 = getelementptr inbounds nuw i8, ptr %1, i64 2
  %4078 = getelementptr inbounds nuw i8, ptr %1, i64 3
  %4079 = getelementptr inbounds nuw i8, ptr %1, i64 4
  %4080 = getelementptr inbounds nuw i8, ptr %1, i64 5
  store i32 0, ptr %4077, align 2
  call void @llvm.lifetime.start.p0(ptr nonnull %2) #9
  call void @llvm.lifetime.start.p0(ptr nonnull %3) #9
  call void @llvm.lifetime.start.p0(ptr nonnull %4) #9
  call void @llvm.lifetime.start.p0(ptr nonnull %5) #9
  store i64 0, ptr %2, align 16, !tbaa !10
  %4081 = getelementptr inbounds nuw i8, ptr %2, i64 8
  store i64 1, ptr %4081, align 8, !tbaa !10
  %4082 = getelementptr inbounds nuw i8, ptr %2, i64 16
  store i64 2, ptr %4082, align 16, !tbaa !10
  %4083 = getelementptr inbounds nuw i8, ptr %6, i64 8
  %4084 = getelementptr inbounds nuw i8, ptr %6, i64 16
  %4085 = getelementptr inbounds nuw i8, ptr %6, i64 24
  %4086 = getelementptr inbounds nuw i8, ptr %7, i64 8
  %4087 = getelementptr inbounds nuw i8, ptr %7, i64 16
  %4088 = getelementptr inbounds nuw i8, ptr %7, i64 24
  %4089 = getelementptr inbounds nuw i8, ptr %8, i64 8
  %4090 = getelementptr inbounds nuw i8, ptr %8, i64 16
  %4091 = getelementptr inbounds nuw i8, ptr %8, i64 24
  %4092 = getelementptr inbounds nuw i8, ptr %9, i64 8
  %4093 = getelementptr inbounds nuw i8, ptr %9, i64 16
  %4094 = getelementptr inbounds nuw i8, ptr %9, i64 24
  %4095 = getelementptr inbounds nuw i8, ptr %5, i64 8
  %4096 = getelementptr inbounds nuw i8, ptr %4, i64 8
  %4097 = getelementptr inbounds nuw i8, ptr %5, i64 16
  %4098 = getelementptr inbounds nuw i8, ptr %4, i64 16
  %4099 = getelementptr inbounds nuw i8, ptr %3, i64 8
  %4100 = getelementptr inbounds nuw i8, ptr %3, i64 16
  br label %4101

4101:                                             ; preds = %4324, %4061
  %4102 = phi i64 [ 0, %4061 ], [ %4326, %4324 ]
  %4103 = load i8, ptr %1, align 16
  %4104 = icmp eq i8 %4103, 0
  %4105 = load i8, ptr %4076, align 1
  %4106 = icmp eq i8 %4105, 0
  %4107 = load i8, ptr %4079, align 4
  %4108 = icmp ne i8 %4107, 0
  %4109 = load i8, ptr %4077, align 2, !tbaa !9
  %4110 = icmp ne i8 %4109, 0
  %4111 = select i1 %4110, i1 true, i1 %4104
  %4112 = select i1 %4111, i1 true, i1 %4106
  %4113 = select i1 %4112, i64 -999999999, i64 100
  store i64 %4113, ptr %3, align 16, !tbaa !10
  %4114 = load i8, ptr %4078, align 1, !tbaa !9
  %4115 = icmp eq i8 %4114, 0
  %4116 = select i1 %4115, i1 %4108, i1 false
  %4117 = select i1 %4116, i64 300, i64 -999999999
  store i64 %4117, ptr %4099, align 8, !tbaa !10
  %4118 = load i8, ptr %4080, align 1, !tbaa !9
  %4119 = icmp ne i8 %4118, 0
  %4120 = select i1 %4119, i1 true, i1 %4104
  %4121 = select i1 %4120, i64 -999999999, i64 200
  store i64 %4121, ptr %4100, align 16, !tbaa !10
  call void @llvm.lifetime.start.p0(ptr nonnull %6) #9
  store ptr %2, ptr %6, align 8, !tbaa !15
  store i64 3, ptr %4083, align 8, !tbaa !19
  store i64 8, ptr %4084, align 8, !tbaa !20
  store i64 8, ptr %4085, align 8, !tbaa !21
  call void @llvm.lifetime.start.p0(ptr nonnull %7) #9
  store ptr %3, ptr %7, align 8, !tbaa !15
  store i64 3, ptr %4086, align 8, !tbaa !19
  store i64 8, ptr %4087, align 8, !tbaa !20
  store i64 8, ptr %4088, align 8, !tbaa !21
  call void @llvm.lifetime.start.p0(ptr nonnull %8) #9
  store ptr %4, ptr %8, align 8, !tbaa !15
  store i64 3, ptr %4089, align 8, !tbaa !19
  store i64 8, ptr %4090, align 8, !tbaa !20
  store i64 8, ptr %4091, align 8, !tbaa !21
  call void @llvm.lifetime.start.p0(ptr nonnull %9) #9
  store ptr %5, ptr %9, align 8, !tbaa !15
  store i64 3, ptr %4092, align 8, !tbaa !19
  store i64 8, ptr %4093, align 8, !tbaa !20
  store i64 8, ptr %4094, align 8, !tbaa !21
  call fastcc void @topk(ptr noundef %7, i64 noundef 3, ptr noundef %6, ptr noundef %8, ptr noundef %9)
  %4122 = load i64, ptr %5, align 16, !tbaa !10
  %4123 = icmp slt i64 %4122, -999999998
  br i1 %4123, label %4124, label %4125

4124:                                             ; preds = %4101
  call void @llvm.lifetime.end.p0(ptr nonnull %9) #9
  call void @llvm.lifetime.end.p0(ptr nonnull %8) #9
  call void @llvm.lifetime.end.p0(ptr nonnull %7) #9
  call void @llvm.lifetime.end.p0(ptr nonnull %6) #9
  br label %4328

4125:                                             ; preds = %4101
  %4126 = load i64, ptr %4, align 16, !tbaa !10
  %4127 = shl nsw i64 %4126, 3
  %4128 = getelementptr inbounds i8, ptr @__const.main.pih, i64 %4127
  %4129 = load i8, ptr %4128, align 8, !tbaa !9
  %4130 = zext i8 %4129 to i64
  %4131 = getelementptr inbounds nuw i8, ptr %4128, i64 1
  %4132 = load i8, ptr %4131, align 1, !tbaa !9
  %4133 = zext i8 %4132 to i64
  %4134 = shl nuw nsw i64 %4133, 8
  %4135 = or disjoint i64 %4134, %4130
  %4136 = getelementptr inbounds nuw i8, ptr %4128, i64 2
  %4137 = load i8, ptr %4136, align 2, !tbaa !9
  %4138 = zext i8 %4137 to i64
  %4139 = shl nuw nsw i64 %4138, 16
  %4140 = getelementptr inbounds nuw i8, ptr %4128, i64 3
  %4141 = load i8, ptr %4140, align 1, !tbaa !9
  %4142 = zext i8 %4141 to i64
  %4143 = shl nuw nsw i64 %4142, 24
  %4144 = or disjoint i64 %4143, %4135
  %4145 = or disjoint i64 %4144, %4139
  %4146 = getelementptr inbounds nuw i8, ptr %4128, i64 4
  %4147 = load i8, ptr %4146, align 4, !tbaa !9
  %4148 = zext i8 %4147 to i64
  %4149 = shl nuw nsw i64 %4148, 32
  %4150 = getelementptr inbounds nuw i8, ptr %4128, i64 5
  %4151 = load i8, ptr %4150, align 1, !tbaa !9
  %4152 = zext i8 %4151 to i64
  %4153 = shl nuw nsw i64 %4152, 40
  %4154 = or disjoint i64 %4149, %4153
  %4155 = or disjoint i64 %4154, %4145
  %4156 = getelementptr inbounds nuw i8, ptr %4128, i64 6
  %4157 = load i8, ptr %4156, align 2, !tbaa !9
  %4158 = zext i8 %4157 to i64
  %4159 = shl nuw nsw i64 %4158, 48
  %4160 = getelementptr inbounds nuw i8, ptr %4128, i64 7
  %4161 = load i8, ptr %4160, align 1, !tbaa !9
  %4162 = zext i8 %4161 to i64
  %4163 = shl nuw i64 %4162, 56
  %4164 = or disjoint i64 %4159, %4163
  %4165 = or disjoint i64 %4164, %4155
  %4166 = getelementptr inbounds i8, ptr %1, i64 %4165
  %4167 = load i8, ptr %4166, align 1, !tbaa !9
  %4168 = icmp eq i8 %4167, 0
  br i1 %4168, label %4169, label %4188

4169:                                             ; preds = %4125
  store i8 1, ptr %4166, align 1, !tbaa !9
  %4170 = shl nsw i64 %4102, 3
  %4171 = getelementptr inbounds i8, ptr %100, i64 %4170
  store i8 %4129, ptr %4171, align 8, !tbaa !9
  %4172 = getelementptr inbounds nuw i8, ptr %4171, i64 1
  store i8 %4132, ptr %4172, align 1, !tbaa !9
  %4173 = getelementptr inbounds nuw i8, ptr %4171, i64 2
  store i8 %4137, ptr %4173, align 2, !tbaa !9
  %4174 = getelementptr inbounds nuw i8, ptr %4171, i64 3
  store i8 %4141, ptr %4174, align 1, !tbaa !9
  %4175 = lshr i64 %4155, 32
  %4176 = trunc i64 %4175 to i8
  %4177 = getelementptr inbounds nuw i8, ptr %4171, i64 4
  store i8 %4176, ptr %4177, align 4, !tbaa !9
  %4178 = lshr i64 %4155, 40
  %4179 = trunc nuw i64 %4178 to i8
  %4180 = getelementptr inbounds nuw i8, ptr %4171, i64 5
  store i8 %4179, ptr %4180, align 1, !tbaa !9
  %4181 = lshr i64 %4165, 48
  %4182 = trunc i64 %4181 to i8
  %4183 = getelementptr inbounds nuw i8, ptr %4171, i64 6
  store i8 %4182, ptr %4183, align 2, !tbaa !9
  %4184 = lshr i64 %4165, 56
  %4185 = trunc nuw i64 %4184 to i8
  %4186 = getelementptr inbounds nuw i8, ptr %4171, i64 7
  store i8 %4185, ptr %4186, align 1, !tbaa !9
  %4187 = add nsw i64 %4102, 1
  br label %4188

4188:                                             ; preds = %4169, %4125
  %4189 = phi i32 [ 0, %4125 ], [ 1, %4169 ]
  %4190 = phi i64 [ %4102, %4125 ], [ %4187, %4169 ]
  %4191 = load i64, ptr %4095, align 8, !tbaa !10
  %4192 = icmp slt i64 %4191, -999999998
  br i1 %4192, label %4324, label %4193

4193:                                             ; preds = %4188
  %4194 = load i64, ptr %4096, align 8, !tbaa !10
  %4195 = shl nsw i64 %4194, 3
  %4196 = getelementptr inbounds i8, ptr @__const.main.pih, i64 %4195
  %4197 = load i8, ptr %4196, align 8, !tbaa !9
  %4198 = zext i8 %4197 to i64
  %4199 = getelementptr inbounds nuw i8, ptr %4196, i64 1
  %4200 = load i8, ptr %4199, align 1, !tbaa !9
  %4201 = zext i8 %4200 to i64
  %4202 = shl nuw nsw i64 %4201, 8
  %4203 = or disjoint i64 %4202, %4198
  %4204 = getelementptr inbounds nuw i8, ptr %4196, i64 2
  %4205 = load i8, ptr %4204, align 2, !tbaa !9
  %4206 = zext i8 %4205 to i64
  %4207 = shl nuw nsw i64 %4206, 16
  %4208 = getelementptr inbounds nuw i8, ptr %4196, i64 3
  %4209 = load i8, ptr %4208, align 1, !tbaa !9
  %4210 = zext i8 %4209 to i64
  %4211 = shl nuw nsw i64 %4210, 24
  %4212 = or disjoint i64 %4211, %4203
  %4213 = or disjoint i64 %4212, %4207
  %4214 = getelementptr inbounds nuw i8, ptr %4196, i64 4
  %4215 = load i8, ptr %4214, align 4, !tbaa !9
  %4216 = zext i8 %4215 to i64
  %4217 = shl nuw nsw i64 %4216, 32
  %4218 = getelementptr inbounds nuw i8, ptr %4196, i64 5
  %4219 = load i8, ptr %4218, align 1, !tbaa !9
  %4220 = zext i8 %4219 to i64
  %4221 = shl nuw nsw i64 %4220, 40
  %4222 = or disjoint i64 %4217, %4221
  %4223 = or disjoint i64 %4222, %4213
  %4224 = getelementptr inbounds nuw i8, ptr %4196, i64 6
  %4225 = load i8, ptr %4224, align 2, !tbaa !9
  %4226 = zext i8 %4225 to i64
  %4227 = shl nuw nsw i64 %4226, 48
  %4228 = getelementptr inbounds nuw i8, ptr %4196, i64 7
  %4229 = load i8, ptr %4228, align 1, !tbaa !9
  %4230 = zext i8 %4229 to i64
  %4231 = shl nuw i64 %4230, 56
  %4232 = or disjoint i64 %4227, %4231
  %4233 = or disjoint i64 %4232, %4223
  %4234 = getelementptr inbounds i8, ptr %1, i64 %4233
  %4235 = load i8, ptr %4234, align 1, !tbaa !9
  %4236 = icmp eq i8 %4235, 0
  br i1 %4236, label %4237, label %4256

4237:                                             ; preds = %4193
  store i8 1, ptr %4234, align 1, !tbaa !9
  %4238 = shl nsw i64 %4190, 3
  %4239 = getelementptr inbounds i8, ptr %100, i64 %4238
  store i8 %4197, ptr %4239, align 8, !tbaa !9
  %4240 = getelementptr inbounds nuw i8, ptr %4239, i64 1
  store i8 %4200, ptr %4240, align 1, !tbaa !9
  %4241 = getelementptr inbounds nuw i8, ptr %4239, i64 2
  store i8 %4205, ptr %4241, align 2, !tbaa !9
  %4242 = getelementptr inbounds nuw i8, ptr %4239, i64 3
  store i8 %4209, ptr %4242, align 1, !tbaa !9
  %4243 = lshr i64 %4223, 32
  %4244 = trunc i64 %4243 to i8
  %4245 = getelementptr inbounds nuw i8, ptr %4239, i64 4
  store i8 %4244, ptr %4245, align 4, !tbaa !9
  %4246 = lshr i64 %4223, 40
  %4247 = trunc nuw i64 %4246 to i8
  %4248 = getelementptr inbounds nuw i8, ptr %4239, i64 5
  store i8 %4247, ptr %4248, align 1, !tbaa !9
  %4249 = lshr i64 %4233, 48
  %4250 = trunc i64 %4249 to i8
  %4251 = getelementptr inbounds nuw i8, ptr %4239, i64 6
  store i8 %4250, ptr %4251, align 2, !tbaa !9
  %4252 = lshr i64 %4233, 56
  %4253 = trunc nuw i64 %4252 to i8
  %4254 = getelementptr inbounds nuw i8, ptr %4239, i64 7
  store i8 %4253, ptr %4254, align 1, !tbaa !9
  %4255 = add nsw i64 %4190, 1
  br label %4256

4256:                                             ; preds = %4237, %4193
  %4257 = phi i32 [ %4189, %4193 ], [ 1, %4237 ]
  %4258 = phi i64 [ %4190, %4193 ], [ %4255, %4237 ]
  %4259 = load i64, ptr %4097, align 16, !tbaa !10
  %4260 = icmp slt i64 %4259, -999999998
  br i1 %4260, label %4324, label %4261

4261:                                             ; preds = %4256
  %4262 = load i64, ptr %4098, align 16, !tbaa !10
  %4263 = shl nsw i64 %4262, 3
  %4264 = getelementptr inbounds i8, ptr @__const.main.pih, i64 %4263
  %4265 = load i8, ptr %4264, align 8, !tbaa !9
  %4266 = zext i8 %4265 to i64
  %4267 = getelementptr inbounds nuw i8, ptr %4264, i64 1
  %4268 = load i8, ptr %4267, align 1, !tbaa !9
  %4269 = zext i8 %4268 to i64
  %4270 = shl nuw nsw i64 %4269, 8
  %4271 = or disjoint i64 %4270, %4266
  %4272 = getelementptr inbounds nuw i8, ptr %4264, i64 2
  %4273 = load i8, ptr %4272, align 2, !tbaa !9
  %4274 = zext i8 %4273 to i64
  %4275 = shl nuw nsw i64 %4274, 16
  %4276 = getelementptr inbounds nuw i8, ptr %4264, i64 3
  %4277 = load i8, ptr %4276, align 1, !tbaa !9
  %4278 = zext i8 %4277 to i64
  %4279 = shl nuw nsw i64 %4278, 24
  %4280 = or disjoint i64 %4279, %4271
  %4281 = or disjoint i64 %4280, %4275
  %4282 = getelementptr inbounds nuw i8, ptr %4264, i64 4
  %4283 = load i8, ptr %4282, align 4, !tbaa !9
  %4284 = zext i8 %4283 to i64
  %4285 = shl nuw nsw i64 %4284, 32
  %4286 = getelementptr inbounds nuw i8, ptr %4264, i64 5
  %4287 = load i8, ptr %4286, align 1, !tbaa !9
  %4288 = zext i8 %4287 to i64
  %4289 = shl nuw nsw i64 %4288, 40
  %4290 = or disjoint i64 %4285, %4289
  %4291 = or disjoint i64 %4290, %4281
  %4292 = getelementptr inbounds nuw i8, ptr %4264, i64 6
  %4293 = load i8, ptr %4292, align 2, !tbaa !9
  %4294 = zext i8 %4293 to i64
  %4295 = shl nuw nsw i64 %4294, 48
  %4296 = getelementptr inbounds nuw i8, ptr %4264, i64 7
  %4297 = load i8, ptr %4296, align 1, !tbaa !9
  %4298 = zext i8 %4297 to i64
  %4299 = shl nuw i64 %4298, 56
  %4300 = or disjoint i64 %4295, %4299
  %4301 = or disjoint i64 %4300, %4291
  %4302 = getelementptr inbounds i8, ptr %1, i64 %4301
  %4303 = load i8, ptr %4302, align 1, !tbaa !9
  %4304 = icmp eq i8 %4303, 0
  br i1 %4304, label %4305, label %4324

4305:                                             ; preds = %4261
  store i8 1, ptr %4302, align 1, !tbaa !9
  %4306 = shl nsw i64 %4258, 3
  %4307 = getelementptr inbounds i8, ptr %100, i64 %4306
  store i8 %4265, ptr %4307, align 8, !tbaa !9
  %4308 = getelementptr inbounds nuw i8, ptr %4307, i64 1
  store i8 %4268, ptr %4308, align 1, !tbaa !9
  %4309 = getelementptr inbounds nuw i8, ptr %4307, i64 2
  store i8 %4273, ptr %4309, align 2, !tbaa !9
  %4310 = getelementptr inbounds nuw i8, ptr %4307, i64 3
  store i8 %4277, ptr %4310, align 1, !tbaa !9
  %4311 = lshr i64 %4291, 32
  %4312 = trunc i64 %4311 to i8
  %4313 = getelementptr inbounds nuw i8, ptr %4307, i64 4
  store i8 %4312, ptr %4313, align 4, !tbaa !9
  %4314 = lshr i64 %4291, 40
  %4315 = trunc nuw i64 %4314 to i8
  %4316 = getelementptr inbounds nuw i8, ptr %4307, i64 5
  store i8 %4315, ptr %4316, align 1, !tbaa !9
  %4317 = lshr i64 %4301, 48
  %4318 = trunc i64 %4317 to i8
  %4319 = getelementptr inbounds nuw i8, ptr %4307, i64 6
  store i8 %4318, ptr %4319, align 2, !tbaa !9
  %4320 = lshr i64 %4301, 56
  %4321 = trunc nuw i64 %4320 to i8
  %4322 = getelementptr inbounds nuw i8, ptr %4307, i64 7
  store i8 %4321, ptr %4322, align 1, !tbaa !9
  %4323 = add nsw i64 %4258, 1
  br label %4324

4324:                                             ; preds = %4305, %4261, %4256, %4188
  %4325 = phi i32 [ %4257, %4261 ], [ %4257, %4256 ], [ %4189, %4188 ], [ 1, %4305 ]
  %4326 = phi i64 [ %4258, %4261 ], [ %4258, %4256 ], [ %4190, %4188 ], [ %4323, %4305 ]
  call void @llvm.lifetime.end.p0(ptr nonnull %9) #9
  call void @llvm.lifetime.end.p0(ptr nonnull %8) #9
  call void @llvm.lifetime.end.p0(ptr nonnull %7) #9
  call void @llvm.lifetime.end.p0(ptr nonnull %6) #9
  %4327 = icmp eq i32 %4325, 0
  br i1 %4327, label %4328, label %4101, !llvm.loop !35

4328:                                             ; preds = %4324, %4124
  %4329 = phi i64 [ %4102, %4124 ], [ %4326, %4324 ]
  call void @llvm.lifetime.end.p0(ptr nonnull %5) #9
  call void @llvm.lifetime.end.p0(ptr nonnull %4) #9
  call void @llvm.lifetime.end.p0(ptr nonnull %3) #9
  call void @llvm.lifetime.end.p0(ptr nonnull %2) #9
  call void @llvm.lifetime.end.p0(ptr nonnull %1) #9
  %4330 = icmp sgt i64 %4329, 0
  br i1 %4330, label %4331, label %4366

4331:                                             ; preds = %4328
  %4332 = and i64 %4329, 1
  %4333 = icmp eq i64 %4329, 1
  br i1 %4333, label %4338, label %4334

4334:                                             ; preds = %4331
  %4335 = and i64 %4329, 9223372036854775806
  br label %4373

4336:                                             ; preds = %4373
  %4337 = icmp eq i64 %4332, 0
  br i1 %4337, label %4353, label %4338

4338:                                             ; preds = %4336, %4331
  %4339 = phi i64 [ 0, %4331 ], [ %4398, %4336 ]
  %4340 = phi i32 [ 0, %4331 ], [ %4397, %4336 ]
  %4341 = phi i32 [ 0, %4331 ], [ %4394, %4336 ]
  %4342 = phi i32 [ 0, %4331 ], [ %4391, %4336 ]
  %4343 = trunc i64 %4329 to i1
  call void @llvm.assume(i1 %4343)
  %4344 = getelementptr inbounds nuw [8 x i8], ptr %100, i64 %4339
  %4345 = load i64, ptr %4344, align 8, !tbaa !10
  %4346 = freeze i64 %4345
  %4347 = icmp eq i64 %4346, 2
  %4348 = select i1 %4347, i32 1, i32 %4342
  %4349 = icmp eq i64 %4346, 5
  %4350 = select i1 %4349, i32 1, i32 %4341
  %4351 = icmp eq i64 %4346, 3
  %4352 = select i1 %4351, i32 1, i32 %4340
  br label %4353

4353:                                             ; preds = %4336, %4338
  %4354 = phi i32 [ %4391, %4336 ], [ %4348, %4338 ]
  %4355 = phi i32 [ %4394, %4336 ], [ %4350, %4338 ]
  %4356 = phi i32 [ %4397, %4336 ], [ %4352, %4338 ]
  %4357 = icmp ne i32 %4354, 0
  %4358 = icmp ne i32 %4355, 0
  %4359 = icmp eq i64 %4329, 2
  %4360 = select i1 %4359, i1 %4357, i1 false
  %4361 = select i1 %4360, i1 %4358, i1 false
  %4362 = icmp eq i32 %4356, 0
  %4363 = freeze i1 %4361
  %4364 = select i1 %4362, ptr @.str.1, ptr @.str.2
  %4365 = select i1 %4363, ptr %4364, ptr @.str.2
  br label %4366

4366:                                             ; preds = %4353, %4328
  %4367 = phi ptr [ %4364, %4353 ], [ @.str.1, %4328 ]
  %4368 = phi i32 [ %4356, %4353 ], [ 0, %4328 ]
  %4369 = phi ptr [ %4365, %4353 ], [ @.str.2, %4328 ]
  %4370 = call i32 (ptr, ...) @printf(ptr noundef nonnull dereferenceable(1) @.str.24, ptr noundef nonnull %4369, i64 noundef %4329)
  %4371 = call i32 (ptr, ...) @printf(ptr noundef nonnull dereferenceable(1) @.str.25, ptr noundef nonnull %4367, i32 noundef %4368)
  %4372 = call i32 @puts(ptr nonnull dereferenceable(1) @str)
  call void @llvm.lifetime.end.p0(ptr nonnull %100) #9
  call void @llvm.lifetime.end.p0(ptr nonnull %99) #9
  call void @llvm.lifetime.end.p0(ptr nonnull %98) #9
  call void @llvm.lifetime.end.p0(ptr nonnull %97) #9
  call void @llvm.lifetime.end.p0(ptr nonnull %96) #9
  call void @llvm.lifetime.end.p0(ptr nonnull %95) #9
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

4373:                                             ; preds = %4373, %4334
  %4374 = phi i64 [ 0, %4334 ], [ %4398, %4373 ]
  %4375 = phi i32 [ 0, %4334 ], [ %4397, %4373 ]
  %4376 = phi i32 [ 0, %4334 ], [ %4394, %4373 ]
  %4377 = phi i32 [ 0, %4334 ], [ %4391, %4373 ]
  %4378 = phi i64 [ 0, %4334 ], [ %4399, %4373 ]
  %4379 = getelementptr inbounds nuw [8 x i8], ptr %100, i64 %4374
  %4380 = load i64, ptr %4379, align 16, !tbaa !10
  %4381 = freeze i64 %4380
  %4382 = icmp eq i64 %4381, 2
  %4383 = icmp eq i64 %4381, 5
  %4384 = icmp eq i64 %4381, 3
  %4385 = getelementptr inbounds nuw [8 x i8], ptr %100, i64 %4374
  %4386 = getelementptr inbounds nuw i8, ptr %4385, i64 8
  %4387 = load i64, ptr %4386, align 8, !tbaa !10
  %4388 = freeze i64 %4387
  %4389 = icmp eq i64 %4388, 2
  %4390 = or i1 %4389, %4382
  %4391 = select i1 %4390, i32 1, i32 %4377
  %4392 = icmp eq i64 %4388, 5
  %4393 = or i1 %4392, %4383
  %4394 = select i1 %4393, i32 1, i32 %4376
  %4395 = icmp eq i64 %4388, 3
  %4396 = or i1 %4395, %4384
  %4397 = select i1 %4396, i32 1, i32 %4375
  %4398 = add nuw nsw i64 %4374, 2
  %4399 = add i64 %4378, 2
  %4400 = icmp eq i64 %4399, %4335
  br i1 %4400, label %4336, label %4373, !llvm.loop !36
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
  %3 = load ptr, ptr %0, align 8, !tbaa !15
  %4 = getelementptr inbounds nuw i8, ptr %0, i64 16
  %5 = getelementptr inbounds nuw i8, ptr %0, i64 24
  %6 = load i64, ptr %5, align 8, !tbaa !21
  %7 = icmp sgt i64 %6, 0
  br i1 %7, label %8, label %390

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
  %18 = load i8, ptr %17, align 1, !tbaa !9
  %19 = zext i8 %18 to i64
  %20 = shl nsw i64 %14, 3
  %21 = shl i64 %19, %20
  %22 = or i64 %21, %15
  %23 = or disjoint i64 %14, 1
  %24 = getelementptr inbounds nuw i8, ptr %3, i64 %23
  %25 = load i8, ptr %24, align 1, !tbaa !9
  %26 = zext i8 %25 to i64
  %27 = shl nsw i64 %23, 3
  %28 = shl i64 %26, %27
  %29 = or i64 %28, %22
  %30 = or disjoint i64 %14, 2
  %31 = getelementptr inbounds nuw i8, ptr %3, i64 %30
  %32 = load i8, ptr %31, align 1, !tbaa !9
  %33 = zext i8 %32 to i64
  %34 = shl nsw i64 %30, 3
  %35 = shl i64 %33, %34
  %36 = or i64 %35, %29
  %37 = or disjoint i64 %14, 3
  %38 = getelementptr inbounds nuw i8, ptr %3, i64 %37
  %39 = load i8, ptr %38, align 1, !tbaa !9
  %40 = zext i8 %39 to i64
  %41 = shl nsw i64 %37, 3
  %42 = shl i64 %40, %41
  %43 = or i64 %42, %36
  %44 = add nuw nsw i64 %14, 4
  %45 = add i64 %16, 4
  %46 = icmp eq i64 %45, %12
  br i1 %46, label %47, label %13, !llvm.loop !37

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
  %58 = load i8, ptr %57, align 1, !tbaa !9
  %59 = zext i8 %58 to i64
  %60 = shl nsw i64 %54, 3
  %61 = shl i64 %59, %60
  %62 = or i64 %61, %55
  %63 = add nuw nsw i64 %54, 1
  %64 = add i64 %56, 1
  %65 = icmp eq i64 %64, %9
  br i1 %65, label %66, label %53, !llvm.loop !38

66:                                               ; preds = %53, %47
  %67 = phi i64 [ %43, %47 ], [ %62, %53 ]
  %68 = sitofp i64 %67 to double
  %69 = fmul nnan double %68, f0x3EF0000000000000
  %70 = load i64, ptr %4, align 8, !tbaa !20
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
  %81 = load i8, ptr %80, align 1, !tbaa !9
  %82 = zext i8 %81 to i64
  %83 = shl nsw i64 %77, 3
  %84 = shl i64 %82, %83
  %85 = or i64 %84, %78
  %86 = or disjoint i64 %77, 1
  %87 = getelementptr inbounds nuw i8, ptr %71, i64 %86
  %88 = load i8, ptr %87, align 1, !tbaa !9
  %89 = zext i8 %88 to i64
  %90 = shl nsw i64 %86, 3
  %91 = shl i64 %89, %90
  %92 = or i64 %91, %85
  %93 = or disjoint i64 %77, 2
  %94 = getelementptr inbounds nuw i8, ptr %71, i64 %93
  %95 = load i8, ptr %94, align 1, !tbaa !9
  %96 = zext i8 %95 to i64
  %97 = shl nsw i64 %93, 3
  %98 = shl i64 %96, %97
  %99 = or i64 %98, %92
  %100 = or disjoint i64 %77, 3
  %101 = getelementptr inbounds nuw i8, ptr %71, i64 %100
  %102 = load i8, ptr %101, align 1, !tbaa !9
  %103 = zext i8 %102 to i64
  %104 = shl nsw i64 %100, 3
  %105 = shl i64 %103, %104
  %106 = or i64 %105, %99
  %107 = add nuw nsw i64 %77, 4
  %108 = add i64 %79, 4
  %109 = icmp eq i64 %108, %75
  br i1 %109, label %110, label %76, !llvm.loop !37

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
  %121 = load i8, ptr %120, align 1, !tbaa !9
  %122 = zext i8 %121 to i64
  %123 = shl nsw i64 %117, 3
  %124 = shl i64 %122, %123
  %125 = or i64 %124, %118
  %126 = add nuw nsw i64 %117, 1
  %127 = add i64 %119, 1
  %128 = icmp eq i64 %127, %72
  br i1 %128, label %129, label %116, !llvm.loop !40

129:                                              ; preds = %116, %110
  %130 = phi i64 [ %106, %110 ], [ %125, %116 ]
  %131 = sitofp i64 %130 to double
  %132 = fmul nnan double %131, f0x3EF0000000000000
  %133 = fcmp ogt double %132, %69
  %134 = select i1 %133, double %132, double %69
  %135 = shl nsw i64 %70, 1
  %136 = getelementptr inbounds i8, ptr %3, i64 %135
  %137 = and i64 %6, 3
  %138 = icmp ult i64 %6, 4
  br i1 %138, label %177, label %139

139:                                              ; preds = %129
  %140 = and i64 %6, 9223372036854775804
  br label %141

141:                                              ; preds = %141, %139
  %142 = phi i64 [ 0, %139 ], [ %172, %141 ]
  %143 = phi i64 [ 0, %139 ], [ %171, %141 ]
  %144 = phi i64 [ 0, %139 ], [ %173, %141 ]
  %145 = getelementptr inbounds nuw i8, ptr %136, i64 %142
  %146 = load i8, ptr %145, align 1, !tbaa !9
  %147 = zext i8 %146 to i64
  %148 = shl nsw i64 %142, 3
  %149 = shl i64 %147, %148
  %150 = or i64 %149, %143
  %151 = or disjoint i64 %142, 1
  %152 = getelementptr inbounds nuw i8, ptr %136, i64 %151
  %153 = load i8, ptr %152, align 1, !tbaa !9
  %154 = zext i8 %153 to i64
  %155 = shl nsw i64 %151, 3
  %156 = shl i64 %154, %155
  %157 = or i64 %156, %150
  %158 = or disjoint i64 %142, 2
  %159 = getelementptr inbounds nuw i8, ptr %136, i64 %158
  %160 = load i8, ptr %159, align 1, !tbaa !9
  %161 = zext i8 %160 to i64
  %162 = shl nsw i64 %158, 3
  %163 = shl i64 %161, %162
  %164 = or i64 %163, %157
  %165 = or disjoint i64 %142, 3
  %166 = getelementptr inbounds nuw i8, ptr %136, i64 %165
  %167 = load i8, ptr %166, align 1, !tbaa !9
  %168 = zext i8 %167 to i64
  %169 = shl nsw i64 %165, 3
  %170 = shl i64 %168, %169
  %171 = or i64 %170, %164
  %172 = add nuw nsw i64 %142, 4
  %173 = add i64 %144, 4
  %174 = icmp eq i64 %173, %140
  br i1 %174, label %175, label %141, !llvm.loop !37

175:                                              ; preds = %141
  %176 = icmp eq i64 %137, 0
  br i1 %176, label %194, label %177

177:                                              ; preds = %175, %129
  %178 = phi i64 [ 0, %129 ], [ %172, %175 ]
  %179 = phi i64 [ 0, %129 ], [ %171, %175 ]
  %180 = icmp ne i64 %137, 0
  tail call void @llvm.assume(i1 %180)
  br label %181

181:                                              ; preds = %181, %177
  %182 = phi i64 [ %191, %181 ], [ %178, %177 ]
  %183 = phi i64 [ %190, %181 ], [ %179, %177 ]
  %184 = phi i64 [ %192, %181 ], [ 0, %177 ]
  %185 = getelementptr inbounds nuw i8, ptr %136, i64 %182
  %186 = load i8, ptr %185, align 1, !tbaa !9
  %187 = zext i8 %186 to i64
  %188 = shl nsw i64 %182, 3
  %189 = shl i64 %187, %188
  %190 = or i64 %189, %183
  %191 = add nuw nsw i64 %182, 1
  %192 = add i64 %184, 1
  %193 = icmp eq i64 %192, %137
  br i1 %193, label %194, label %181, !llvm.loop !41

194:                                              ; preds = %181, %175
  %195 = phi i64 [ %171, %175 ], [ %190, %181 ]
  %196 = sitofp i64 %195 to double
  %197 = fmul nnan double %196, f0x3EF0000000000000
  %198 = fcmp ogt double %197, %134
  %199 = select i1 %198, double %197, double %134
  %200 = and i64 %6, 3
  %201 = icmp ult i64 %6, 4
  br i1 %201, label %240, label %202

202:                                              ; preds = %194
  %203 = and i64 %6, 9223372036854775804
  br label %204

204:                                              ; preds = %204, %202
  %205 = phi i64 [ 0, %202 ], [ %235, %204 ]
  %206 = phi i64 [ 0, %202 ], [ %234, %204 ]
  %207 = phi i64 [ 0, %202 ], [ %236, %204 ]
  %208 = getelementptr inbounds nuw i8, ptr %3, i64 %205
  %209 = load i8, ptr %208, align 1, !tbaa !9
  %210 = zext i8 %209 to i64
  %211 = shl nsw i64 %205, 3
  %212 = shl i64 %210, %211
  %213 = or i64 %212, %206
  %214 = or disjoint i64 %205, 1
  %215 = getelementptr inbounds nuw i8, ptr %3, i64 %214
  %216 = load i8, ptr %215, align 1, !tbaa !9
  %217 = zext i8 %216 to i64
  %218 = shl nsw i64 %214, 3
  %219 = shl i64 %217, %218
  %220 = or i64 %219, %213
  %221 = or disjoint i64 %205, 2
  %222 = getelementptr inbounds nuw i8, ptr %3, i64 %221
  %223 = load i8, ptr %222, align 1, !tbaa !9
  %224 = zext i8 %223 to i64
  %225 = shl nsw i64 %221, 3
  %226 = shl i64 %224, %225
  %227 = or i64 %226, %220
  %228 = or disjoint i64 %205, 3
  %229 = getelementptr inbounds nuw i8, ptr %3, i64 %228
  %230 = load i8, ptr %229, align 1, !tbaa !9
  %231 = zext i8 %230 to i64
  %232 = shl nsw i64 %228, 3
  %233 = shl i64 %231, %232
  %234 = or i64 %233, %227
  %235 = add nuw nsw i64 %205, 4
  %236 = add i64 %207, 4
  %237 = icmp eq i64 %236, %203
  br i1 %237, label %238, label %204, !llvm.loop !37

238:                                              ; preds = %204
  %239 = icmp eq i64 %200, 0
  br i1 %239, label %257, label %240

240:                                              ; preds = %238, %194
  %241 = phi i64 [ 0, %194 ], [ %235, %238 ]
  %242 = phi i64 [ 0, %194 ], [ %234, %238 ]
  %243 = icmp ne i64 %200, 0
  tail call void @llvm.assume(i1 %243)
  br label %244

244:                                              ; preds = %244, %240
  %245 = phi i64 [ %254, %244 ], [ %241, %240 ]
  %246 = phi i64 [ %253, %244 ], [ %242, %240 ]
  %247 = phi i64 [ %255, %244 ], [ 0, %240 ]
  %248 = getelementptr inbounds nuw i8, ptr %3, i64 %245
  %249 = load i8, ptr %248, align 1, !tbaa !9
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
  %259 = sitofp i64 %258 to double
  %260 = fmul nnan double %259, f0x3EF0000000000000
  %261 = fsub double %260, %199
  %262 = tail call double @exp(double noundef %261) #9
  %263 = fadd double %262, 0.000000e+00
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
  %272 = getelementptr inbounds nuw i8, ptr %71, i64 %269
  %273 = load i8, ptr %272, align 1, !tbaa !9
  %274 = zext i8 %273 to i64
  %275 = shl nsw i64 %269, 3
  %276 = shl i64 %274, %275
  %277 = or i64 %276, %270
  %278 = or disjoint i64 %269, 1
  %279 = getelementptr inbounds nuw i8, ptr %71, i64 %278
  %280 = load i8, ptr %279, align 1, !tbaa !9
  %281 = zext i8 %280 to i64
  %282 = shl nsw i64 %278, 3
  %283 = shl i64 %281, %282
  %284 = or i64 %283, %277
  %285 = or disjoint i64 %269, 2
  %286 = getelementptr inbounds nuw i8, ptr %71, i64 %285
  %287 = load i8, ptr %286, align 1, !tbaa !9
  %288 = zext i8 %287 to i64
  %289 = shl nsw i64 %285, 3
  %290 = shl i64 %288, %289
  %291 = or i64 %290, %284
  %292 = or disjoint i64 %269, 3
  %293 = getelementptr inbounds nuw i8, ptr %71, i64 %292
  %294 = load i8, ptr %293, align 1, !tbaa !9
  %295 = zext i8 %294 to i64
  %296 = shl nsw i64 %292, 3
  %297 = shl i64 %295, %296
  %298 = or i64 %297, %291
  %299 = add nuw nsw i64 %269, 4
  %300 = add i64 %271, 4
  %301 = icmp eq i64 %300, %267
  br i1 %301, label %302, label %268, !llvm.loop !37

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
  %312 = getelementptr inbounds nuw i8, ptr %71, i64 %309
  %313 = load i8, ptr %312, align 1, !tbaa !9
  %314 = zext i8 %313 to i64
  %315 = shl nsw i64 %309, 3
  %316 = shl i64 %314, %315
  %317 = or i64 %316, %310
  %318 = add nuw nsw i64 %309, 1
  %319 = add i64 %311, 1
  %320 = icmp eq i64 %319, %264
  br i1 %320, label %321, label %308, !llvm.loop !43

321:                                              ; preds = %308, %302
  %322 = phi i64 [ %298, %302 ], [ %317, %308 ]
  %323 = sitofp i64 %322 to double
  %324 = fmul nnan double %323, f0x3EF0000000000000
  %325 = fsub double %324, %199
  %326 = tail call double @exp(double noundef %325) #9
  %327 = fadd double %263, %326
  %328 = and i64 %6, 3
  %329 = icmp ult i64 %6, 4
  br i1 %329, label %368, label %330

330:                                              ; preds = %321
  %331 = and i64 %6, 9223372036854775804
  br label %332

332:                                              ; preds = %332, %330
  %333 = phi i64 [ 0, %330 ], [ %363, %332 ]
  %334 = phi i64 [ 0, %330 ], [ %362, %332 ]
  %335 = phi i64 [ 0, %330 ], [ %364, %332 ]
  %336 = getelementptr inbounds nuw i8, ptr %136, i64 %333
  %337 = load i8, ptr %336, align 1, !tbaa !9
  %338 = zext i8 %337 to i64
  %339 = shl nsw i64 %333, 3
  %340 = shl i64 %338, %339
  %341 = or i64 %340, %334
  %342 = or disjoint i64 %333, 1
  %343 = getelementptr inbounds nuw i8, ptr %136, i64 %342
  %344 = load i8, ptr %343, align 1, !tbaa !9
  %345 = zext i8 %344 to i64
  %346 = shl nsw i64 %342, 3
  %347 = shl i64 %345, %346
  %348 = or i64 %347, %341
  %349 = or disjoint i64 %333, 2
  %350 = getelementptr inbounds nuw i8, ptr %136, i64 %349
  %351 = load i8, ptr %350, align 1, !tbaa !9
  %352 = zext i8 %351 to i64
  %353 = shl nsw i64 %349, 3
  %354 = shl i64 %352, %353
  %355 = or i64 %354, %348
  %356 = or disjoint i64 %333, 3
  %357 = getelementptr inbounds nuw i8, ptr %136, i64 %356
  %358 = load i8, ptr %357, align 1, !tbaa !9
  %359 = zext i8 %358 to i64
  %360 = shl nsw i64 %356, 3
  %361 = shl i64 %359, %360
  %362 = or i64 %361, %355
  %363 = add nuw nsw i64 %333, 4
  %364 = add i64 %335, 4
  %365 = icmp eq i64 %364, %331
  br i1 %365, label %366, label %332, !llvm.loop !37

366:                                              ; preds = %332
  %367 = icmp eq i64 %328, 0
  br i1 %367, label %385, label %368

368:                                              ; preds = %366, %321
  %369 = phi i64 [ 0, %321 ], [ %363, %366 ]
  %370 = phi i64 [ 0, %321 ], [ %362, %366 ]
  %371 = icmp ne i64 %328, 0
  tail call void @llvm.assume(i1 %371)
  br label %372

372:                                              ; preds = %372, %368
  %373 = phi i64 [ %382, %372 ], [ %369, %368 ]
  %374 = phi i64 [ %381, %372 ], [ %370, %368 ]
  %375 = phi i64 [ %383, %372 ], [ 0, %368 ]
  %376 = getelementptr inbounds nuw i8, ptr %136, i64 %373
  %377 = load i8, ptr %376, align 1, !tbaa !9
  %378 = zext i8 %377 to i64
  %379 = shl nsw i64 %373, 3
  %380 = shl i64 %378, %379
  %381 = or i64 %380, %374
  %382 = add nuw nsw i64 %373, 1
  %383 = add i64 %375, 1
  %384 = icmp eq i64 %383, %328
  br i1 %384, label %385, label %372, !llvm.loop !44

385:                                              ; preds = %372, %366
  %386 = phi i64 [ %362, %366 ], [ %381, %372 ]
  %387 = sitofp i64 %386 to double
  %388 = fmul nnan double %387, f0x3EF0000000000000
  %389 = fsub double %388, %199
  br label %390

390:                                              ; preds = %2, %385
  %391 = phi double [ %327, %385 ], [ 2.000000e+00, %2 ]
  %392 = phi double [ %326, %385 ], [ 1.000000e+00, %2 ]
  %393 = phi double [ %262, %385 ], [ 1.000000e+00, %2 ]
  %394 = phi double [ %389, %385 ], [ 0.000000e+00, %2 ]
  %395 = tail call double @exp(double noundef %394) #9
  %396 = fadd double %391, %395
  %397 = getelementptr inbounds nuw i8, ptr %1, i64 16
  %398 = getelementptr inbounds nuw i8, ptr %1, i64 24
  %399 = fdiv double %393, %396
  %400 = fmul double %399, 6.553600e+04
  %401 = fptosi double %400 to i64
  %402 = load ptr, ptr %1, align 8, !tbaa !15
  %403 = load i64, ptr %398, align 8, !tbaa !21
  %404 = icmp sgt i64 %403, 0
  br i1 %404, label %405, label %449

405:                                              ; preds = %390, %405
  %406 = phi i64 [ %411, %405 ], [ 0, %390 ]
  %407 = shl nsw i64 %406, 3
  %408 = ashr i64 %401, %407
  %409 = trunc i64 %408 to i8
  %410 = getelementptr inbounds nuw i8, ptr %402, i64 %406
  store i8 %409, ptr %410, align 1, !tbaa !9
  %411 = add nuw nsw i64 %406, 1
  %412 = load i64, ptr %398, align 8, !tbaa !21
  %413 = icmp slt i64 %411, %412
  br i1 %413, label %405, label %414, !llvm.loop !45

414:                                              ; preds = %405
  %415 = load ptr, ptr %1, align 8, !tbaa !15
  %416 = icmp sgt i64 %412, 0
  %417 = fdiv double %392, %396
  %418 = fmul double %417, 6.553600e+04
  %419 = fptosi double %418 to i64
  %420 = load i64, ptr %397, align 8, !tbaa !20
  %421 = getelementptr inbounds i8, ptr %415, i64 %420
  br i1 %416, label %422, label %449

422:                                              ; preds = %414, %422
  %423 = phi i64 [ %428, %422 ], [ 0, %414 ]
  %424 = shl nsw i64 %423, 3
  %425 = ashr i64 %419, %424
  %426 = trunc i64 %425 to i8
  %427 = getelementptr inbounds nuw i8, ptr %421, i64 %423
  store i8 %426, ptr %427, align 1, !tbaa !9
  %428 = add nuw nsw i64 %423, 1
  %429 = load i64, ptr %398, align 8, !tbaa !21
  %430 = icmp slt i64 %428, %429
  br i1 %430, label %422, label %431, !llvm.loop !45

431:                                              ; preds = %422
  %432 = load ptr, ptr %1, align 8, !tbaa !15
  %433 = load i64, ptr %397, align 8, !tbaa !20
  %434 = icmp sgt i64 %429, 0
  %435 = fdiv double %395, %396
  %436 = fmul double %435, 6.553600e+04
  %437 = fptosi double %436 to i64
  %438 = shl nsw i64 %433, 1
  %439 = getelementptr inbounds i8, ptr %432, i64 %438
  br i1 %434, label %440, label %449

440:                                              ; preds = %431, %440
  %441 = phi i64 [ %446, %440 ], [ 0, %431 ]
  %442 = shl nsw i64 %441, 3
  %443 = ashr i64 %437, %442
  %444 = trunc i64 %443 to i8
  %445 = getelementptr inbounds nuw i8, ptr %439, i64 %441
  store i8 %444, ptr %445, align 1, !tbaa !9
  %446 = add nuw nsw i64 %441, 1
  %447 = load i64, ptr %398, align 8, !tbaa !21
  %448 = icmp slt i64 %446, %447
  br i1 %448, label %440, label %449, !llvm.loop !45

449:                                              ; preds = %440, %390, %414, %431
  ret void
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind willreturn memory(argmem: readwrite)
declare void @llvm.lifetime.end.p0(ptr captures(none)) #1

; Function Attrs: nofree norecurse nosync nounwind sspstrong memory(readwrite, inaccessiblemem: none, target_mem: none) uwtable
define internal fastcc void @layernorm(ptr nofree noundef nonnull readonly captures(none) %0, i64 noundef range(i64 3, 5) %1, ptr nofree noundef nonnull readonly captures(none) %2, ptr nofree noundef nonnull readonly captures(none) %3, ptr nofree noundef nonnull readonly captures(none) %4) unnamed_addr #4 {
  %6 = load ptr, ptr %0, align 8, !tbaa !15
  %7 = getelementptr inbounds nuw i8, ptr %0, i64 16
  %8 = load i64, ptr %7, align 8, !tbaa !20
  %9 = getelementptr inbounds nuw i8, ptr %0, i64 24
  %10 = load i64, ptr %9, align 8, !tbaa !21
  %11 = icmp sgt i64 %10, 0
  %12 = and i64 %10, 3
  %13 = icmp ult i64 %10, 4
  %14 = and i64 %10, 9223372036854775804
  %15 = icmp eq i64 %12, 0
  %16 = icmp ne i64 %12, 0
  br label %24

17:                                               ; preds = %81
  %18 = sdiv i64 %83, %1
  %19 = and i64 %10, 3
  %20 = icmp ult i64 %10, 4
  %21 = and i64 %10, 9223372036854775804
  %22 = icmp eq i64 %19, 0
  %23 = icmp ne i64 %19, 0
  br label %106

24:                                               ; preds = %5, %81
  %25 = phi i64 [ 0, %5 ], [ %83, %81 ]
  %26 = phi i64 [ 0, %5 ], [ %84, %81 ]
  %27 = mul nsw i64 %8, %26
  %28 = getelementptr inbounds i8, ptr %6, i64 %27
  br i1 %11, label %29, label %81

29:                                               ; preds = %24
  br i1 %13, label %65, label %30

30:                                               ; preds = %29, %30
  %31 = phi i64 [ %61, %30 ], [ 0, %29 ]
  %32 = phi i64 [ %60, %30 ], [ 0, %29 ]
  %33 = phi i64 [ %62, %30 ], [ 0, %29 ]
  %34 = getelementptr inbounds nuw i8, ptr %28, i64 %31
  %35 = load i8, ptr %34, align 1, !tbaa !9
  %36 = zext i8 %35 to i64
  %37 = shl nsw i64 %31, 3
  %38 = shl i64 %36, %37
  %39 = or i64 %38, %32
  %40 = or disjoint i64 %31, 1
  %41 = getelementptr inbounds nuw i8, ptr %28, i64 %40
  %42 = load i8, ptr %41, align 1, !tbaa !9
  %43 = zext i8 %42 to i64
  %44 = shl nsw i64 %40, 3
  %45 = shl i64 %43, %44
  %46 = or i64 %45, %39
  %47 = or disjoint i64 %31, 2
  %48 = getelementptr inbounds nuw i8, ptr %28, i64 %47
  %49 = load i8, ptr %48, align 1, !tbaa !9
  %50 = zext i8 %49 to i64
  %51 = shl nsw i64 %47, 3
  %52 = shl i64 %50, %51
  %53 = or i64 %52, %46
  %54 = or disjoint i64 %31, 3
  %55 = getelementptr inbounds nuw i8, ptr %28, i64 %54
  %56 = load i8, ptr %55, align 1, !tbaa !9
  %57 = zext i8 %56 to i64
  %58 = shl nsw i64 %54, 3
  %59 = shl i64 %57, %58
  %60 = or i64 %59, %53
  %61 = add nuw nsw i64 %31, 4
  %62 = add i64 %33, 4
  %63 = icmp eq i64 %62, %14
  br i1 %63, label %64, label %30, !llvm.loop !37

64:                                               ; preds = %30
  br i1 %15, label %81, label %65

65:                                               ; preds = %64, %29
  %66 = phi i64 [ 0, %29 ], [ %61, %64 ]
  %67 = phi i64 [ 0, %29 ], [ %60, %64 ]
  tail call void @llvm.assume(i1 %16)
  br label %68

68:                                               ; preds = %68, %65
  %69 = phi i64 [ %78, %68 ], [ %66, %65 ]
  %70 = phi i64 [ %77, %68 ], [ %67, %65 ]
  %71 = phi i64 [ %79, %68 ], [ 0, %65 ]
  %72 = getelementptr inbounds nuw i8, ptr %28, i64 %69
  %73 = load i8, ptr %72, align 1, !tbaa !9
  %74 = zext i8 %73 to i64
  %75 = shl nsw i64 %69, 3
  %76 = shl i64 %74, %75
  %77 = or i64 %76, %70
  %78 = add nuw nsw i64 %69, 1
  %79 = add i64 %71, 1
  %80 = icmp eq i64 %79, %12
  br i1 %80, label %81, label %68, !llvm.loop !46

81:                                               ; preds = %64, %68, %24
  %82 = phi i64 [ 0, %24 ], [ %60, %64 ], [ %77, %68 ]
  %83 = add nsw i64 %82, %25
  %84 = add nuw nsw i64 %26, 1
  %85 = icmp eq i64 %84, %1
  br i1 %85, label %17, label %24, !llvm.loop !47

86:                                               ; preds = %163
  %87 = udiv i64 %168, %1
  %88 = add nuw nsw i64 %87, 1
  br label %89

89:                                               ; preds = %86, %89
  %90 = phi i64 [ %91, %89 ], [ 0, %86 ]
  %91 = add nuw nsw i64 %90, 1
  %92 = mul nuw nsw i64 %91, %91
  %93 = icmp samesign ugt i64 %92, %88
  br i1 %93, label %94, label %89, !llvm.loop !48

94:                                               ; preds = %89
  %95 = icmp eq i64 %90, 0
  br i1 %95, label %98, label %96

96:                                               ; preds = %94
  %97 = udiv i64 4294967296, %90
  br label %98

98:                                               ; preds = %94, %96
  %99 = phi i64 [ %97, %96 ], [ 0, %94 ]
  %100 = getelementptr inbounds nuw i8, ptr %2, i64 16
  %101 = getelementptr inbounds nuw i8, ptr %2, i64 24
  %102 = getelementptr inbounds nuw i8, ptr %3, i64 16
  %103 = getelementptr inbounds nuw i8, ptr %3, i64 24
  %104 = getelementptr inbounds nuw i8, ptr %4, i64 16
  %105 = getelementptr inbounds nuw i8, ptr %4, i64 24
  br label %172

106:                                              ; preds = %17, %163
  %107 = phi i64 [ 0, %17 ], [ %169, %163 ]
  %108 = phi i64 [ 0, %17 ], [ %168, %163 ]
  %109 = mul nsw i64 %8, %107
  %110 = getelementptr inbounds i8, ptr %6, i64 %109
  br i1 %11, label %111, label %163

111:                                              ; preds = %106
  br i1 %20, label %147, label %112

112:                                              ; preds = %111, %112
  %113 = phi i64 [ %143, %112 ], [ 0, %111 ]
  %114 = phi i64 [ %142, %112 ], [ 0, %111 ]
  %115 = phi i64 [ %144, %112 ], [ 0, %111 ]
  %116 = getelementptr inbounds nuw i8, ptr %110, i64 %113
  %117 = load i8, ptr %116, align 1, !tbaa !9
  %118 = zext i8 %117 to i64
  %119 = shl nsw i64 %113, 3
  %120 = shl i64 %118, %119
  %121 = or i64 %120, %114
  %122 = or disjoint i64 %113, 1
  %123 = getelementptr inbounds nuw i8, ptr %110, i64 %122
  %124 = load i8, ptr %123, align 1, !tbaa !9
  %125 = zext i8 %124 to i64
  %126 = shl nsw i64 %122, 3
  %127 = shl i64 %125, %126
  %128 = or i64 %127, %121
  %129 = or disjoint i64 %113, 2
  %130 = getelementptr inbounds nuw i8, ptr %110, i64 %129
  %131 = load i8, ptr %130, align 1, !tbaa !9
  %132 = zext i8 %131 to i64
  %133 = shl nsw i64 %129, 3
  %134 = shl i64 %132, %133
  %135 = or i64 %134, %128
  %136 = or disjoint i64 %113, 3
  %137 = getelementptr inbounds nuw i8, ptr %110, i64 %136
  %138 = load i8, ptr %137, align 1, !tbaa !9
  %139 = zext i8 %138 to i64
  %140 = shl nsw i64 %136, 3
  %141 = shl i64 %139, %140
  %142 = or i64 %141, %135
  %143 = add nuw nsw i64 %113, 4
  %144 = add i64 %115, 4
  %145 = icmp eq i64 %144, %21
  br i1 %145, label %146, label %112, !llvm.loop !37

146:                                              ; preds = %112
  br i1 %22, label %163, label %147

147:                                              ; preds = %146, %111
  %148 = phi i64 [ 0, %111 ], [ %143, %146 ]
  %149 = phi i64 [ 0, %111 ], [ %142, %146 ]
  tail call void @llvm.assume(i1 %23)
  br label %150

150:                                              ; preds = %150, %147
  %151 = phi i64 [ %160, %150 ], [ %148, %147 ]
  %152 = phi i64 [ %159, %150 ], [ %149, %147 ]
  %153 = phi i64 [ %161, %150 ], [ 0, %147 ]
  %154 = getelementptr inbounds nuw i8, ptr %110, i64 %151
  %155 = load i8, ptr %154, align 1, !tbaa !9
  %156 = zext i8 %155 to i64
  %157 = shl nsw i64 %151, 3
  %158 = shl i64 %156, %157
  %159 = or i64 %158, %152
  %160 = add nuw nsw i64 %151, 1
  %161 = add i64 %153, 1
  %162 = icmp eq i64 %161, %19
  br i1 %162, label %163, label %150, !llvm.loop !49

163:                                              ; preds = %146, %150, %106
  %164 = phi i64 [ 0, %106 ], [ %142, %146 ], [ %159, %150 ]
  %165 = sub nsw i64 %164, %18
  %166 = mul nsw i64 %165, %165
  %167 = lshr i64 %166, 16
  %168 = add nuw nsw i64 %167, %108
  %169 = add nuw nsw i64 %107, 1
  %170 = icmp eq i64 %169, %1
  br i1 %170, label %86, label %106, !llvm.loop !50

171:                                              ; preds = %395
  ret void

172:                                              ; preds = %98, %395
  %173 = phi i64 [ 0, %98 ], [ %396, %395 ]
  %174 = load ptr, ptr %0, align 8, !tbaa !15
  %175 = load i64, ptr %7, align 8, !tbaa !20
  %176 = mul nsw i64 %175, %173
  %177 = getelementptr inbounds i8, ptr %174, i64 %176
  %178 = load i64, ptr %9, align 8, !tbaa !21
  %179 = icmp sgt i64 %178, 0
  br i1 %179, label %180, label %238

180:                                              ; preds = %172
  %181 = and i64 %178, 3
  %182 = icmp ult i64 %178, 4
  br i1 %182, label %221, label %183

183:                                              ; preds = %180
  %184 = and i64 %178, 9223372036854775804
  br label %185

185:                                              ; preds = %185, %183
  %186 = phi i64 [ 0, %183 ], [ %216, %185 ]
  %187 = phi i64 [ 0, %183 ], [ %215, %185 ]
  %188 = phi i64 [ 0, %183 ], [ %217, %185 ]
  %189 = getelementptr inbounds nuw i8, ptr %177, i64 %186
  %190 = load i8, ptr %189, align 1, !tbaa !9
  %191 = zext i8 %190 to i64
  %192 = shl nsw i64 %186, 3
  %193 = shl i64 %191, %192
  %194 = or i64 %193, %187
  %195 = or disjoint i64 %186, 1
  %196 = getelementptr inbounds nuw i8, ptr %177, i64 %195
  %197 = load i8, ptr %196, align 1, !tbaa !9
  %198 = zext i8 %197 to i64
  %199 = shl nsw i64 %195, 3
  %200 = shl i64 %198, %199
  %201 = or i64 %200, %194
  %202 = or disjoint i64 %186, 2
  %203 = getelementptr inbounds nuw i8, ptr %177, i64 %202
  %204 = load i8, ptr %203, align 1, !tbaa !9
  %205 = zext i8 %204 to i64
  %206 = shl nsw i64 %202, 3
  %207 = shl i64 %205, %206
  %208 = or i64 %207, %201
  %209 = or disjoint i64 %186, 3
  %210 = getelementptr inbounds nuw i8, ptr %177, i64 %209
  %211 = load i8, ptr %210, align 1, !tbaa !9
  %212 = zext i8 %211 to i64
  %213 = shl nsw i64 %209, 3
  %214 = shl i64 %212, %213
  %215 = or i64 %214, %208
  %216 = add nuw nsw i64 %186, 4
  %217 = add i64 %188, 4
  %218 = icmp eq i64 %217, %184
  br i1 %218, label %219, label %185, !llvm.loop !37

219:                                              ; preds = %185
  %220 = icmp eq i64 %181, 0
  br i1 %220, label %238, label %221

221:                                              ; preds = %219, %180
  %222 = phi i64 [ 0, %180 ], [ %216, %219 ]
  %223 = phi i64 [ 0, %180 ], [ %215, %219 ]
  %224 = icmp ne i64 %181, 0
  tail call void @llvm.assume(i1 %224)
  br label %225

225:                                              ; preds = %225, %221
  %226 = phi i64 [ %235, %225 ], [ %222, %221 ]
  %227 = phi i64 [ %234, %225 ], [ %223, %221 ]
  %228 = phi i64 [ %236, %225 ], [ 0, %221 ]
  %229 = getelementptr inbounds nuw i8, ptr %177, i64 %226
  %230 = load i8, ptr %229, align 1, !tbaa !9
  %231 = zext i8 %230 to i64
  %232 = shl nsw i64 %226, 3
  %233 = shl i64 %231, %232
  %234 = or i64 %233, %227
  %235 = add nuw nsw i64 %226, 1
  %236 = add i64 %228, 1
  %237 = icmp eq i64 %236, %181
  br i1 %237, label %238, label %225, !llvm.loop !51

238:                                              ; preds = %219, %225, %172
  %239 = phi i64 [ 0, %172 ], [ %215, %219 ], [ %234, %225 ]
  %240 = sub nsw i64 %239, %18
  %241 = mul nsw i64 %240, %99
  %242 = ashr i64 %241, 16
  %243 = load ptr, ptr %2, align 8, !tbaa !15
  %244 = load i64, ptr %100, align 8, !tbaa !20
  %245 = mul nsw i64 %244, %173
  %246 = getelementptr inbounds i8, ptr %243, i64 %245
  %247 = load i64, ptr %101, align 8, !tbaa !21
  %248 = icmp sgt i64 %247, 0
  br i1 %248, label %249, label %311

249:                                              ; preds = %238
  %250 = and i64 %247, 3
  %251 = icmp ult i64 %247, 4
  br i1 %251, label %290, label %252

252:                                              ; preds = %249
  %253 = and i64 %247, 9223372036854775804
  br label %254

254:                                              ; preds = %254, %252
  %255 = phi i64 [ 0, %252 ], [ %285, %254 ]
  %256 = phi i64 [ 0, %252 ], [ %284, %254 ]
  %257 = phi i64 [ 0, %252 ], [ %286, %254 ]
  %258 = getelementptr inbounds nuw i8, ptr %246, i64 %255
  %259 = load i8, ptr %258, align 1, !tbaa !9
  %260 = zext i8 %259 to i64
  %261 = shl nsw i64 %255, 3
  %262 = shl i64 %260, %261
  %263 = or i64 %262, %256
  %264 = or disjoint i64 %255, 1
  %265 = getelementptr inbounds nuw i8, ptr %246, i64 %264
  %266 = load i8, ptr %265, align 1, !tbaa !9
  %267 = zext i8 %266 to i64
  %268 = shl nsw i64 %264, 3
  %269 = shl i64 %267, %268
  %270 = or i64 %269, %263
  %271 = or disjoint i64 %255, 2
  %272 = getelementptr inbounds nuw i8, ptr %246, i64 %271
  %273 = load i8, ptr %272, align 1, !tbaa !9
  %274 = zext i8 %273 to i64
  %275 = shl nsw i64 %271, 3
  %276 = shl i64 %274, %275
  %277 = or i64 %276, %270
  %278 = or disjoint i64 %255, 3
  %279 = getelementptr inbounds nuw i8, ptr %246, i64 %278
  %280 = load i8, ptr %279, align 1, !tbaa !9
  %281 = zext i8 %280 to i64
  %282 = shl nsw i64 %278, 3
  %283 = shl i64 %281, %282
  %284 = or i64 %283, %277
  %285 = add nuw nsw i64 %255, 4
  %286 = add i64 %257, 4
  %287 = icmp eq i64 %286, %253
  br i1 %287, label %288, label %254, !llvm.loop !37

288:                                              ; preds = %254
  %289 = icmp eq i64 %250, 0
  br i1 %289, label %307, label %290

290:                                              ; preds = %288, %249
  %291 = phi i64 [ 0, %249 ], [ %285, %288 ]
  %292 = phi i64 [ 0, %249 ], [ %284, %288 ]
  %293 = icmp ne i64 %250, 0
  tail call void @llvm.assume(i1 %293)
  br label %294

294:                                              ; preds = %294, %290
  %295 = phi i64 [ %304, %294 ], [ %291, %290 ]
  %296 = phi i64 [ %303, %294 ], [ %292, %290 ]
  %297 = phi i64 [ %305, %294 ], [ 0, %290 ]
  %298 = getelementptr inbounds nuw i8, ptr %246, i64 %295
  %299 = load i8, ptr %298, align 1, !tbaa !9
  %300 = zext i8 %299 to i64
  %301 = shl nsw i64 %295, 3
  %302 = shl i64 %300, %301
  %303 = or i64 %302, %296
  %304 = add nuw nsw i64 %295, 1
  %305 = add i64 %297, 1
  %306 = icmp eq i64 %305, %250
  br i1 %306, label %307, label %294, !llvm.loop !52

307:                                              ; preds = %294, %288
  %308 = phi i64 [ %284, %288 ], [ %303, %294 ]
  %309 = mul nsw i64 %308, %242
  %310 = ashr i64 %309, 16
  br label %311

311:                                              ; preds = %307, %238
  %312 = phi i64 [ 0, %238 ], [ %310, %307 ]
  %313 = load ptr, ptr %3, align 8, !tbaa !15
  %314 = load i64, ptr %102, align 8, !tbaa !20
  %315 = mul nsw i64 %314, %173
  %316 = getelementptr inbounds i8, ptr %313, i64 %315
  %317 = load i64, ptr %103, align 8, !tbaa !21
  %318 = icmp sgt i64 %317, 0
  br i1 %318, label %319, label %377

319:                                              ; preds = %311
  %320 = and i64 %317, 3
  %321 = icmp ult i64 %317, 4
  br i1 %321, label %360, label %322

322:                                              ; preds = %319
  %323 = and i64 %317, 9223372036854775804
  br label %324

324:                                              ; preds = %324, %322
  %325 = phi i64 [ 0, %322 ], [ %355, %324 ]
  %326 = phi i64 [ 0, %322 ], [ %354, %324 ]
  %327 = phi i64 [ 0, %322 ], [ %356, %324 ]
  %328 = getelementptr inbounds nuw i8, ptr %316, i64 %325
  %329 = load i8, ptr %328, align 1, !tbaa !9
  %330 = zext i8 %329 to i64
  %331 = shl nsw i64 %325, 3
  %332 = shl i64 %330, %331
  %333 = or i64 %332, %326
  %334 = or disjoint i64 %325, 1
  %335 = getelementptr inbounds nuw i8, ptr %316, i64 %334
  %336 = load i8, ptr %335, align 1, !tbaa !9
  %337 = zext i8 %336 to i64
  %338 = shl nsw i64 %334, 3
  %339 = shl i64 %337, %338
  %340 = or i64 %339, %333
  %341 = or disjoint i64 %325, 2
  %342 = getelementptr inbounds nuw i8, ptr %316, i64 %341
  %343 = load i8, ptr %342, align 1, !tbaa !9
  %344 = zext i8 %343 to i64
  %345 = shl nsw i64 %341, 3
  %346 = shl i64 %344, %345
  %347 = or i64 %346, %340
  %348 = or disjoint i64 %325, 3
  %349 = getelementptr inbounds nuw i8, ptr %316, i64 %348
  %350 = load i8, ptr %349, align 1, !tbaa !9
  %351 = zext i8 %350 to i64
  %352 = shl nsw i64 %348, 3
  %353 = shl i64 %351, %352
  %354 = or i64 %353, %347
  %355 = add nuw nsw i64 %325, 4
  %356 = add i64 %327, 4
  %357 = icmp eq i64 %356, %323
  br i1 %357, label %358, label %324, !llvm.loop !37

358:                                              ; preds = %324
  %359 = icmp eq i64 %320, 0
  br i1 %359, label %377, label %360

360:                                              ; preds = %358, %319
  %361 = phi i64 [ 0, %319 ], [ %355, %358 ]
  %362 = phi i64 [ 0, %319 ], [ %354, %358 ]
  %363 = icmp ne i64 %320, 0
  tail call void @llvm.assume(i1 %363)
  br label %364

364:                                              ; preds = %364, %360
  %365 = phi i64 [ %374, %364 ], [ %361, %360 ]
  %366 = phi i64 [ %373, %364 ], [ %362, %360 ]
  %367 = phi i64 [ %375, %364 ], [ 0, %360 ]
  %368 = getelementptr inbounds nuw i8, ptr %316, i64 %365
  %369 = load i8, ptr %368, align 1, !tbaa !9
  %370 = zext i8 %369 to i64
  %371 = shl nsw i64 %365, 3
  %372 = shl i64 %370, %371
  %373 = or i64 %372, %366
  %374 = add nuw nsw i64 %365, 1
  %375 = add i64 %367, 1
  %376 = icmp eq i64 %375, %320
  br i1 %376, label %377, label %364, !llvm.loop !53

377:                                              ; preds = %358, %364, %311
  %378 = phi i64 [ 0, %311 ], [ %354, %358 ], [ %373, %364 ]
  %379 = add nsw i64 %378, %312
  %380 = load ptr, ptr %4, align 8, !tbaa !15
  %381 = load i64, ptr %104, align 8, !tbaa !20
  %382 = mul nsw i64 %381, %173
  %383 = getelementptr inbounds i8, ptr %380, i64 %382
  %384 = load i64, ptr %105, align 8, !tbaa !21
  %385 = icmp sgt i64 %384, 0
  br i1 %385, label %386, label %395

386:                                              ; preds = %377, %386
  %387 = phi i64 [ %392, %386 ], [ 0, %377 ]
  %388 = shl nsw i64 %387, 3
  %389 = ashr i64 %379, %388
  %390 = trunc i64 %389 to i8
  %391 = getelementptr inbounds nuw i8, ptr %383, i64 %387
  store i8 %390, ptr %391, align 1, !tbaa !9
  %392 = add nuw nsw i64 %387, 1
  %393 = load i64, ptr %105, align 8, !tbaa !21
  %394 = icmp slt i64 %392, %393
  br i1 %394, label %386, label %395, !llvm.loop !45

395:                                              ; preds = %386, %377
  %396 = add nuw nsw i64 %173, 1
  %397 = icmp eq i64 %396, %1
  br i1 %397, label %171, label %172, !llvm.loop !54
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
  store i64 -1, ptr %6, align 16, !tbaa !10
  store i64 -1, ptr %7, align 8, !tbaa !10
  store i64 -1, ptr %8, align 16, !tbaa !10
  store i64 -999999999, ptr %9, align 16, !tbaa !10
  store i64 -999999999, ptr %10, align 8, !tbaa !10
  store i64 -999999999, ptr %11, align 16, !tbaa !10
  %12 = load ptr, ptr %0, align 8, !tbaa !15
  %13 = getelementptr inbounds nuw i8, ptr %0, i64 16
  %14 = load i64, ptr %13, align 8, !tbaa !20
  %15 = getelementptr inbounds nuw i8, ptr %0, i64 24
  %16 = load i64, ptr %15, align 8, !tbaa !21
  %17 = icmp sgt i64 %16, 0
  %18 = getelementptr inbounds nuw i8, ptr %2, i64 16
  %19 = getelementptr inbounds nuw i8, ptr %2, i64 24
  %20 = and i64 %16, 3
  %21 = icmp ult i64 %16, 4
  %22 = and i64 %16, 9223372036854775804
  %23 = icmp eq i64 %20, 0
  %24 = icmp ne i64 %20, 0
  br label %34

25:                                               ; preds = %177
  %26 = getelementptr inbounds nuw i8, ptr %3, i64 16
  %27 = getelementptr inbounds nuw i8, ptr %3, i64 24
  %28 = getelementptr inbounds nuw i8, ptr %4, i64 16
  %29 = getelementptr inbounds nuw i8, ptr %4, i64 24
  %30 = load i64, ptr %6, align 16, !tbaa !10
  %31 = load ptr, ptr %3, align 8, !tbaa !15
  %32 = load i64, ptr %27, align 8, !tbaa !21
  %33 = icmp sgt i64 %32, 0
  br i1 %33, label %180, label %189

34:                                               ; preds = %5, %177
  %35 = phi i64 [ 0, %5 ], [ %178, %177 ]
  %36 = mul nsw i64 %14, %35
  %37 = getelementptr inbounds i8, ptr %12, i64 %36
  br i1 %17, label %38, label %90

38:                                               ; preds = %34
  br i1 %21, label %74, label %39

39:                                               ; preds = %38, %39
  %40 = phi i64 [ %70, %39 ], [ 0, %38 ]
  %41 = phi i64 [ %69, %39 ], [ 0, %38 ]
  %42 = phi i64 [ %71, %39 ], [ 0, %38 ]
  %43 = getelementptr inbounds nuw i8, ptr %37, i64 %40
  %44 = load i8, ptr %43, align 1, !tbaa !9
  %45 = zext i8 %44 to i64
  %46 = shl nsw i64 %40, 3
  %47 = shl i64 %45, %46
  %48 = or i64 %47, %41
  %49 = or disjoint i64 %40, 1
  %50 = getelementptr inbounds nuw i8, ptr %37, i64 %49
  %51 = load i8, ptr %50, align 1, !tbaa !9
  %52 = zext i8 %51 to i64
  %53 = shl nsw i64 %49, 3
  %54 = shl i64 %52, %53
  %55 = or i64 %54, %48
  %56 = or disjoint i64 %40, 2
  %57 = getelementptr inbounds nuw i8, ptr %37, i64 %56
  %58 = load i8, ptr %57, align 1, !tbaa !9
  %59 = zext i8 %58 to i64
  %60 = shl nsw i64 %56, 3
  %61 = shl i64 %59, %60
  %62 = or i64 %61, %55
  %63 = or disjoint i64 %40, 3
  %64 = getelementptr inbounds nuw i8, ptr %37, i64 %63
  %65 = load i8, ptr %64, align 1, !tbaa !9
  %66 = zext i8 %65 to i64
  %67 = shl nsw i64 %63, 3
  %68 = shl i64 %66, %67
  %69 = or i64 %68, %62
  %70 = add nuw nsw i64 %40, 4
  %71 = add i64 %42, 4
  %72 = icmp eq i64 %71, %22
  br i1 %72, label %73, label %39, !llvm.loop !37

73:                                               ; preds = %39
  br i1 %23, label %90, label %74

74:                                               ; preds = %73, %38
  %75 = phi i64 [ 0, %38 ], [ %70, %73 ]
  %76 = phi i64 [ 0, %38 ], [ %69, %73 ]
  tail call void @llvm.assume(i1 %24)
  br label %77

77:                                               ; preds = %77, %74
  %78 = phi i64 [ %87, %77 ], [ %75, %74 ]
  %79 = phi i64 [ %86, %77 ], [ %76, %74 ]
  %80 = phi i64 [ %88, %77 ], [ 0, %74 ]
  %81 = getelementptr inbounds nuw i8, ptr %37, i64 %78
  %82 = load i8, ptr %81, align 1, !tbaa !9
  %83 = zext i8 %82 to i64
  %84 = shl nsw i64 %78, 3
  %85 = shl i64 %83, %84
  %86 = or i64 %85, %79
  %87 = add nuw nsw i64 %78, 1
  %88 = add i64 %80, 1
  %89 = icmp eq i64 %88, %20
  br i1 %89, label %90, label %77, !llvm.loop !55

90:                                               ; preds = %73, %77, %34
  %91 = phi i64 [ 0, %34 ], [ %69, %73 ], [ %86, %77 ]
  %92 = load i64, ptr %9, align 16, !tbaa !10
  %93 = icmp sgt i64 %91, %92
  br i1 %93, label %169, label %94

94:                                               ; preds = %90
  %95 = load i64, ptr %10, align 8, !tbaa !10
  %96 = icmp sgt i64 %91, %95
  br i1 %96, label %169, label %97

97:                                               ; preds = %94
  %98 = load i64, ptr %11, align 16, !tbaa !10
  %99 = icmp sgt i64 %91, %98
  br i1 %99, label %100, label %177

100:                                              ; preds = %169, %174, %97
  %101 = phi ptr [ %8, %97 ], [ %171, %174 ], [ %171, %169 ]
  %102 = phi ptr [ %11, %97 ], [ %170, %174 ], [ %170, %169 ]
  store i64 %91, ptr %102, align 8, !tbaa !10
  %103 = load ptr, ptr %2, align 8, !tbaa !15
  %104 = load i64, ptr %18, align 8, !tbaa !20
  %105 = mul nsw i64 %104, %35
  %106 = getelementptr inbounds i8, ptr %103, i64 %105
  %107 = load i64, ptr %19, align 8, !tbaa !21
  %108 = icmp sgt i64 %107, 0
  br i1 %108, label %109, label %167

109:                                              ; preds = %100
  %110 = and i64 %107, 3
  %111 = icmp ult i64 %107, 4
  br i1 %111, label %150, label %112

112:                                              ; preds = %109
  %113 = and i64 %107, 9223372036854775804
  br label %114

114:                                              ; preds = %114, %112
  %115 = phi i64 [ 0, %112 ], [ %145, %114 ]
  %116 = phi i64 [ 0, %112 ], [ %144, %114 ]
  %117 = phi i64 [ 0, %112 ], [ %146, %114 ]
  %118 = getelementptr inbounds nuw i8, ptr %106, i64 %115
  %119 = load i8, ptr %118, align 1, !tbaa !9
  %120 = zext i8 %119 to i64
  %121 = shl nsw i64 %115, 3
  %122 = shl i64 %120, %121
  %123 = or i64 %122, %116
  %124 = or disjoint i64 %115, 1
  %125 = getelementptr inbounds nuw i8, ptr %106, i64 %124
  %126 = load i8, ptr %125, align 1, !tbaa !9
  %127 = zext i8 %126 to i64
  %128 = shl nsw i64 %124, 3
  %129 = shl i64 %127, %128
  %130 = or i64 %129, %123
  %131 = or disjoint i64 %115, 2
  %132 = getelementptr inbounds nuw i8, ptr %106, i64 %131
  %133 = load i8, ptr %132, align 1, !tbaa !9
  %134 = zext i8 %133 to i64
  %135 = shl nsw i64 %131, 3
  %136 = shl i64 %134, %135
  %137 = or i64 %136, %130
  %138 = or disjoint i64 %115, 3
  %139 = getelementptr inbounds nuw i8, ptr %106, i64 %138
  %140 = load i8, ptr %139, align 1, !tbaa !9
  %141 = zext i8 %140 to i64
  %142 = shl nsw i64 %138, 3
  %143 = shl i64 %141, %142
  %144 = or i64 %143, %137
  %145 = add nuw nsw i64 %115, 4
  %146 = add i64 %117, 4
  %147 = icmp eq i64 %146, %113
  br i1 %147, label %148, label %114, !llvm.loop !37

148:                                              ; preds = %114
  %149 = icmp eq i64 %110, 0
  br i1 %149, label %167, label %150

150:                                              ; preds = %148, %109
  %151 = phi i64 [ 0, %109 ], [ %145, %148 ]
  %152 = phi i64 [ 0, %109 ], [ %144, %148 ]
  %153 = icmp ne i64 %110, 0
  tail call void @llvm.assume(i1 %153)
  br label %154

154:                                              ; preds = %154, %150
  %155 = phi i64 [ %164, %154 ], [ %151, %150 ]
  %156 = phi i64 [ %163, %154 ], [ %152, %150 ]
  %157 = phi i64 [ %165, %154 ], [ 0, %150 ]
  %158 = getelementptr inbounds nuw i8, ptr %106, i64 %155
  %159 = load i8, ptr %158, align 1, !tbaa !9
  %160 = zext i8 %159 to i64
  %161 = shl nsw i64 %155, 3
  %162 = shl i64 %160, %161
  %163 = or i64 %162, %156
  %164 = add nuw nsw i64 %155, 1
  %165 = add i64 %157, 1
  %166 = icmp eq i64 %165, %110
  br i1 %166, label %167, label %154, !llvm.loop !56

167:                                              ; preds = %148, %154, %100
  %168 = phi i64 [ 0, %100 ], [ %144, %148 ], [ %163, %154 ]
  store i64 %168, ptr %101, align 8, !tbaa !10
  br label %177

169:                                              ; preds = %94, %90
  %170 = phi ptr [ %10, %94 ], [ %9, %90 ]
  %171 = phi ptr [ %7, %94 ], [ %6, %90 ]
  %172 = load i64, ptr %10, align 8, !tbaa !10
  store i64 %172, ptr %11, align 16, !tbaa !10
  %173 = load i64, ptr %7, align 8, !tbaa !10
  store i64 %173, ptr %8, align 16, !tbaa !10
  br i1 %93, label %174, label %100

174:                                              ; preds = %169
  %175 = load i64, ptr %9, align 16, !tbaa !10
  store i64 %175, ptr %10, align 8, !tbaa !10
  %176 = load i64, ptr %6, align 16, !tbaa !10
  store i64 %176, ptr %7, align 8, !tbaa !10
  br label %100

177:                                              ; preds = %97, %167
  %178 = add nuw nsw i64 %35, 1
  %179 = icmp eq i64 %178, %1
  br i1 %179, label %25, label %34, !llvm.loop !57

180:                                              ; preds = %25, %180
  %181 = phi i64 [ %186, %180 ], [ 0, %25 ]
  %182 = shl nsw i64 %181, 3
  %183 = ashr i64 %30, %182
  %184 = trunc i64 %183 to i8
  %185 = getelementptr inbounds nuw i8, ptr %31, i64 %181
  store i8 %184, ptr %185, align 1, !tbaa !9
  %186 = add nuw nsw i64 %181, 1
  %187 = load i64, ptr %27, align 8, !tbaa !21
  %188 = icmp slt i64 %186, %187
  br i1 %188, label %180, label %189, !llvm.loop !45

189:                                              ; preds = %180, %25
  %190 = phi i64 [ %32, %25 ], [ %187, %180 ]
  %191 = load i64, ptr %9, align 16, !tbaa !10
  %192 = load ptr, ptr %4, align 8, !tbaa !15
  %193 = load i64, ptr %29, align 8, !tbaa !21
  %194 = icmp sgt i64 %193, 0
  br i1 %194, label %195, label %206

195:                                              ; preds = %189, %195
  %196 = phi i64 [ %201, %195 ], [ 0, %189 ]
  %197 = shl nsw i64 %196, 3
  %198 = ashr i64 %191, %197
  %199 = trunc i64 %198 to i8
  %200 = getelementptr inbounds nuw i8, ptr %192, i64 %196
  store i8 %199, ptr %200, align 1, !tbaa !9
  %201 = add nuw nsw i64 %196, 1
  %202 = load i64, ptr %29, align 8, !tbaa !21
  %203 = icmp slt i64 %201, %202
  br i1 %203, label %195, label %204, !llvm.loop !45

204:                                              ; preds = %195
  %205 = load i64, ptr %27, align 8, !tbaa !21
  br label %206

206:                                              ; preds = %204, %189
  %207 = phi i64 [ %202, %204 ], [ %193, %189 ]
  %208 = phi i64 [ %205, %204 ], [ %190, %189 ]
  %209 = load i64, ptr %7, align 8, !tbaa !10
  %210 = load ptr, ptr %3, align 8, !tbaa !15
  %211 = load i64, ptr %26, align 8, !tbaa !20
  %212 = getelementptr inbounds i8, ptr %210, i64 %211
  %213 = icmp sgt i64 %208, 0
  br i1 %213, label %214, label %225

214:                                              ; preds = %206, %214
  %215 = phi i64 [ %220, %214 ], [ 0, %206 ]
  %216 = shl nsw i64 %215, 3
  %217 = ashr i64 %209, %216
  %218 = trunc i64 %217 to i8
  %219 = getelementptr inbounds nuw i8, ptr %212, i64 %215
  store i8 %218, ptr %219, align 1, !tbaa !9
  %220 = add nuw nsw i64 %215, 1
  %221 = load i64, ptr %27, align 8, !tbaa !21
  %222 = icmp slt i64 %220, %221
  br i1 %222, label %214, label %223, !llvm.loop !45

223:                                              ; preds = %214
  %224 = load i64, ptr %29, align 8, !tbaa !21
  br label %225

225:                                              ; preds = %223, %206
  %226 = phi i64 [ %221, %223 ], [ %208, %206 ]
  %227 = phi i64 [ %224, %223 ], [ %207, %206 ]
  %228 = load i64, ptr %10, align 8, !tbaa !10
  %229 = load ptr, ptr %4, align 8, !tbaa !15
  %230 = load i64, ptr %28, align 8, !tbaa !20
  %231 = getelementptr inbounds i8, ptr %229, i64 %230
  %232 = icmp sgt i64 %227, 0
  br i1 %232, label %233, label %244

233:                                              ; preds = %225, %233
  %234 = phi i64 [ %239, %233 ], [ 0, %225 ]
  %235 = shl nsw i64 %234, 3
  %236 = ashr i64 %228, %235
  %237 = trunc i64 %236 to i8
  %238 = getelementptr inbounds nuw i8, ptr %231, i64 %234
  store i8 %237, ptr %238, align 1, !tbaa !9
  %239 = add nuw nsw i64 %234, 1
  %240 = load i64, ptr %29, align 8, !tbaa !21
  %241 = icmp slt i64 %239, %240
  br i1 %241, label %233, label %242, !llvm.loop !45

242:                                              ; preds = %233
  %243 = load i64, ptr %27, align 8, !tbaa !21
  br label %244

244:                                              ; preds = %242, %225
  %245 = phi i64 [ %240, %242 ], [ %227, %225 ]
  %246 = phi i64 [ %243, %242 ], [ %226, %225 ]
  %247 = load i64, ptr %8, align 16, !tbaa !10
  %248 = load ptr, ptr %3, align 8, !tbaa !15
  %249 = load i64, ptr %26, align 8, !tbaa !20
  %250 = shl nsw i64 %249, 1
  %251 = getelementptr inbounds i8, ptr %248, i64 %250
  %252 = icmp sgt i64 %246, 0
  br i1 %252, label %253, label %264

253:                                              ; preds = %244, %253
  %254 = phi i64 [ %259, %253 ], [ 0, %244 ]
  %255 = shl nsw i64 %254, 3
  %256 = ashr i64 %247, %255
  %257 = trunc i64 %256 to i8
  %258 = getelementptr inbounds nuw i8, ptr %251, i64 %254
  store i8 %257, ptr %258, align 1, !tbaa !9
  %259 = add nuw nsw i64 %254, 1
  %260 = load i64, ptr %27, align 8, !tbaa !21
  %261 = icmp slt i64 %259, %260
  br i1 %261, label %253, label %262, !llvm.loop !45

262:                                              ; preds = %253
  %263 = load i64, ptr %29, align 8, !tbaa !21
  br label %264

264:                                              ; preds = %262, %244
  %265 = phi i64 [ %263, %262 ], [ %245, %244 ]
  %266 = load i64, ptr %11, align 16, !tbaa !10
  %267 = load ptr, ptr %4, align 8, !tbaa !15
  %268 = load i64, ptr %28, align 8, !tbaa !20
  %269 = shl nsw i64 %268, 1
  %270 = getelementptr inbounds i8, ptr %267, i64 %269
  %271 = icmp sgt i64 %265, 0
  br i1 %271, label %272, label %281

272:                                              ; preds = %264, %272
  %273 = phi i64 [ %278, %272 ], [ 0, %264 ]
  %274 = shl nsw i64 %273, 3
  %275 = ashr i64 %266, %274
  %276 = trunc i64 %275 to i8
  %277 = getelementptr inbounds nuw i8, ptr %270, i64 %273
  store i8 %276, ptr %277, align 1, !tbaa !9
  %278 = add nuw nsw i64 %273, 1
  %279 = load i64, ptr %29, align 8, !tbaa !21
  %280 = icmp slt i64 %278, %279
  br i1 %280, label %272, label %281, !llvm.loop !45

281:                                              ; preds = %272, %264
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
  %6 = load ptr, ptr %1, align 8, !tbaa !15
  %7 = load i64, ptr %5, align 8, !tbaa !21
  %8 = icmp sgt i64 %7, 0
  br i1 %8, label %9, label %98

9:                                                ; preds = %3, %9
  %10 = phi i64 [ %12, %9 ], [ 0, %3 ]
  %11 = getelementptr inbounds nuw i8, ptr %6, i64 %10
  store i8 -1, ptr %11, align 1, !tbaa !9
  %12 = add nuw nsw i64 %10, 1
  %13 = load i64, ptr %5, align 8, !tbaa !21
  %14 = icmp slt i64 %12, %13
  br i1 %14, label %9, label %15, !llvm.loop !45

15:                                               ; preds = %9
  %16 = load ptr, ptr %1, align 8, !tbaa !15
  %17 = load i64, ptr %4, align 8, !tbaa !20
  %18 = getelementptr inbounds i8, ptr %16, i64 %17
  %19 = icmp sgt i64 %13, 0
  br i1 %19, label %20, label %98

20:                                               ; preds = %15, %20
  %21 = phi i64 [ %23, %20 ], [ 0, %15 ]
  %22 = getelementptr inbounds nuw i8, ptr %18, i64 %21
  store i8 -1, ptr %22, align 1, !tbaa !9
  %23 = add nuw nsw i64 %21, 1
  %24 = load i64, ptr %5, align 8, !tbaa !21
  %25 = icmp slt i64 %23, %24
  br i1 %25, label %20, label %26, !llvm.loop !45

26:                                               ; preds = %20
  %27 = load ptr, ptr %1, align 8, !tbaa !15
  %28 = load i64, ptr %4, align 8, !tbaa !20
  %29 = shl nsw i64 %28, 1
  %30 = getelementptr inbounds i8, ptr %27, i64 %29
  %31 = icmp sgt i64 %24, 0
  br i1 %31, label %32, label %98

32:                                               ; preds = %26, %32
  %33 = phi i64 [ %35, %32 ], [ 0, %26 ]
  %34 = getelementptr inbounds nuw i8, ptr %30, i64 %33
  store i8 -1, ptr %34, align 1, !tbaa !9
  %35 = add nuw nsw i64 %33, 1
  %36 = load i64, ptr %5, align 8, !tbaa !21
  %37 = icmp slt i64 %35, %36
  br i1 %37, label %32, label %38, !llvm.loop !45

38:                                               ; preds = %32
  %39 = load ptr, ptr %1, align 8, !tbaa !15
  %40 = load i64, ptr %4, align 8, !tbaa !20
  %41 = mul nsw i64 %40, 3
  %42 = getelementptr inbounds i8, ptr %39, i64 %41
  %43 = icmp sgt i64 %36, 0
  br i1 %43, label %44, label %98

44:                                               ; preds = %38, %44
  %45 = phi i64 [ %47, %44 ], [ 0, %38 ]
  %46 = getelementptr inbounds nuw i8, ptr %42, i64 %45
  store i8 -1, ptr %46, align 1, !tbaa !9
  %47 = add nuw nsw i64 %45, 1
  %48 = load i64, ptr %5, align 8, !tbaa !21
  %49 = icmp slt i64 %47, %48
  br i1 %49, label %44, label %50, !llvm.loop !45

50:                                               ; preds = %44
  %51 = load ptr, ptr %1, align 8, !tbaa !15
  %52 = load i64, ptr %4, align 8, !tbaa !20
  %53 = shl nsw i64 %52, 2
  %54 = getelementptr inbounds i8, ptr %51, i64 %53
  %55 = icmp sgt i64 %48, 0
  br i1 %55, label %56, label %98

56:                                               ; preds = %50, %56
  %57 = phi i64 [ %59, %56 ], [ 0, %50 ]
  %58 = getelementptr inbounds nuw i8, ptr %54, i64 %57
  store i8 -1, ptr %58, align 1, !tbaa !9
  %59 = add nuw nsw i64 %57, 1
  %60 = load i64, ptr %5, align 8, !tbaa !21
  %61 = icmp slt i64 %59, %60
  br i1 %61, label %56, label %62, !llvm.loop !45

62:                                               ; preds = %56
  %63 = load ptr, ptr %1, align 8, !tbaa !15
  %64 = load i64, ptr %4, align 8, !tbaa !20
  %65 = mul nsw i64 %64, 5
  %66 = getelementptr inbounds i8, ptr %63, i64 %65
  %67 = icmp sgt i64 %60, 0
  br i1 %67, label %68, label %98

68:                                               ; preds = %62, %68
  %69 = phi i64 [ %71, %68 ], [ 0, %62 ]
  %70 = getelementptr inbounds nuw i8, ptr %66, i64 %69
  store i8 -1, ptr %70, align 1, !tbaa !9
  %71 = add nuw nsw i64 %69, 1
  %72 = load i64, ptr %5, align 8, !tbaa !21
  %73 = icmp slt i64 %71, %72
  br i1 %73, label %68, label %74, !llvm.loop !45

74:                                               ; preds = %68
  %75 = load ptr, ptr %1, align 8, !tbaa !15
  %76 = load i64, ptr %4, align 8, !tbaa !20
  %77 = mul nsw i64 %76, 6
  %78 = getelementptr inbounds i8, ptr %75, i64 %77
  %79 = icmp sgt i64 %72, 0
  br i1 %79, label %80, label %98

80:                                               ; preds = %74, %80
  %81 = phi i64 [ %83, %80 ], [ 0, %74 ]
  %82 = getelementptr inbounds nuw i8, ptr %78, i64 %81
  store i8 -1, ptr %82, align 1, !tbaa !9
  %83 = add nuw nsw i64 %81, 1
  %84 = load i64, ptr %5, align 8, !tbaa !21
  %85 = icmp slt i64 %83, %84
  br i1 %85, label %80, label %86, !llvm.loop !45

86:                                               ; preds = %80
  %87 = load ptr, ptr %1, align 8, !tbaa !15
  %88 = load i64, ptr %4, align 8, !tbaa !20
  %89 = mul nsw i64 %88, 7
  %90 = getelementptr inbounds i8, ptr %87, i64 %89
  %91 = icmp sgt i64 %84, 0
  br i1 %91, label %92, label %98

92:                                               ; preds = %86, %92
  %93 = phi i64 [ %95, %92 ], [ 0, %86 ]
  %94 = getelementptr inbounds nuw i8, ptr %90, i64 %93
  store i8 -1, ptr %94, align 1, !tbaa !9
  %95 = add nuw nsw i64 %93, 1
  %96 = load i64, ptr %5, align 8, !tbaa !21
  %97 = icmp slt i64 %95, %96
  br i1 %97, label %92, label %98, !llvm.loop !45

98:                                               ; preds = %92, %3, %15, %26, %38, %50, %62, %74, %86
  %99 = phi i64 [ %7, %3 ], [ %84, %86 ], [ %72, %74 ], [ %60, %62 ], [ %48, %50 ], [ %36, %38 ], [ %24, %26 ], [ %13, %15 ], [ %96, %92 ]
  %100 = getelementptr inbounds nuw i8, ptr %0, i64 16
  %101 = getelementptr inbounds nuw i8, ptr %0, i64 24
  %102 = getelementptr inbounds nuw i8, ptr %2, i64 16
  %103 = getelementptr inbounds nuw i8, ptr %2, i64 24
  br label %105

104:                                              ; preds = %277
  ret void

105:                                              ; preds = %98, %277
  %106 = phi i64 [ %99, %98 ], [ %278, %277 ]
  %107 = phi i64 [ 0, %98 ], [ %279, %277 ]
  %108 = load ptr, ptr %0, align 8, !tbaa !15
  %109 = load i64, ptr %100, align 8, !tbaa !20
  %110 = mul nsw i64 %109, %107
  %111 = getelementptr inbounds i8, ptr %108, i64 %110
  %112 = load i64, ptr %101, align 8, !tbaa !21
  %113 = icmp sgt i64 %112, 0
  br i1 %113, label %114, label %175

114:                                              ; preds = %105
  %115 = and i64 %112, 3
  %116 = icmp ult i64 %112, 4
  br i1 %116, label %155, label %117

117:                                              ; preds = %114
  %118 = and i64 %112, 9223372036854775804
  br label %119

119:                                              ; preds = %119, %117
  %120 = phi i64 [ 0, %117 ], [ %150, %119 ]
  %121 = phi i64 [ 0, %117 ], [ %149, %119 ]
  %122 = phi i64 [ 0, %117 ], [ %151, %119 ]
  %123 = getelementptr inbounds nuw i8, ptr %111, i64 %120
  %124 = load i8, ptr %123, align 1, !tbaa !9
  %125 = zext i8 %124 to i64
  %126 = shl nsw i64 %120, 3
  %127 = shl i64 %125, %126
  %128 = or i64 %127, %121
  %129 = or disjoint i64 %120, 1
  %130 = getelementptr inbounds nuw i8, ptr %111, i64 %129
  %131 = load i8, ptr %130, align 1, !tbaa !9
  %132 = zext i8 %131 to i64
  %133 = shl nsw i64 %129, 3
  %134 = shl i64 %132, %133
  %135 = or i64 %134, %128
  %136 = or disjoint i64 %120, 2
  %137 = getelementptr inbounds nuw i8, ptr %111, i64 %136
  %138 = load i8, ptr %137, align 1, !tbaa !9
  %139 = zext i8 %138 to i64
  %140 = shl nsw i64 %136, 3
  %141 = shl i64 %139, %140
  %142 = or i64 %141, %135
  %143 = or disjoint i64 %120, 3
  %144 = getelementptr inbounds nuw i8, ptr %111, i64 %143
  %145 = load i8, ptr %144, align 1, !tbaa !9
  %146 = zext i8 %145 to i64
  %147 = shl nsw i64 %143, 3
  %148 = shl i64 %146, %147
  %149 = or i64 %148, %142
  %150 = add nuw nsw i64 %120, 4
  %151 = add i64 %122, 4
  %152 = icmp eq i64 %151, %118
  br i1 %152, label %153, label %119, !llvm.loop !37

153:                                              ; preds = %119
  %154 = icmp eq i64 %115, 0
  br i1 %154, label %172, label %155

155:                                              ; preds = %153, %114
  %156 = phi i64 [ 0, %114 ], [ %150, %153 ]
  %157 = phi i64 [ 0, %114 ], [ %149, %153 ]
  %158 = icmp ne i64 %115, 0
  tail call void @llvm.assume(i1 %158)
  br label %159

159:                                              ; preds = %159, %155
  %160 = phi i64 [ %169, %159 ], [ %156, %155 ]
  %161 = phi i64 [ %168, %159 ], [ %157, %155 ]
  %162 = phi i64 [ %170, %159 ], [ 0, %155 ]
  %163 = getelementptr inbounds nuw i8, ptr %111, i64 %160
  %164 = load i8, ptr %163, align 1, !tbaa !9
  %165 = zext i8 %164 to i64
  %166 = shl nsw i64 %160, 3
  %167 = shl i64 %165, %166
  %168 = or i64 %167, %161
  %169 = add nuw nsw i64 %160, 1
  %170 = add i64 %162, 1
  %171 = icmp eq i64 %170, %115
  br i1 %171, label %172, label %159, !llvm.loop !58

172:                                              ; preds = %159, %153
  %173 = phi i64 [ %149, %153 ], [ %168, %159 ]
  %174 = srem i64 %173, 8
  br label %175

175:                                              ; preds = %172, %105
  %176 = phi i64 [ 0, %105 ], [ %174, %172 ]
  %177 = load ptr, ptr %1, align 8, !tbaa !15
  %178 = load i64, ptr %4, align 8, !tbaa !20
  %179 = mul nsw i64 %178, %176
  %180 = getelementptr inbounds i8, ptr %177, i64 %179
  %181 = icmp sgt i64 %106, 0
  br i1 %181, label %182, label %240

182:                                              ; preds = %175
  %183 = and i64 %106, 3
  %184 = icmp ult i64 %106, 4
  br i1 %184, label %223, label %185

185:                                              ; preds = %182
  %186 = and i64 %106, 9223372036854775804
  br label %187

187:                                              ; preds = %187, %185
  %188 = phi i64 [ 0, %185 ], [ %218, %187 ]
  %189 = phi i64 [ 0, %185 ], [ %217, %187 ]
  %190 = phi i64 [ 0, %185 ], [ %219, %187 ]
  %191 = getelementptr inbounds nuw i8, ptr %180, i64 %188
  %192 = load i8, ptr %191, align 1, !tbaa !9
  %193 = zext i8 %192 to i64
  %194 = shl nsw i64 %188, 3
  %195 = shl i64 %193, %194
  %196 = or i64 %195, %189
  %197 = or disjoint i64 %188, 1
  %198 = getelementptr inbounds nuw i8, ptr %180, i64 %197
  %199 = load i8, ptr %198, align 1, !tbaa !9
  %200 = zext i8 %199 to i64
  %201 = shl nsw i64 %197, 3
  %202 = shl i64 %200, %201
  %203 = or i64 %202, %196
  %204 = or disjoint i64 %188, 2
  %205 = getelementptr inbounds nuw i8, ptr %180, i64 %204
  %206 = load i8, ptr %205, align 1, !tbaa !9
  %207 = zext i8 %206 to i64
  %208 = shl nsw i64 %204, 3
  %209 = shl i64 %207, %208
  %210 = or i64 %209, %203
  %211 = or disjoint i64 %188, 3
  %212 = getelementptr inbounds nuw i8, ptr %180, i64 %211
  %213 = load i8, ptr %212, align 1, !tbaa !9
  %214 = zext i8 %213 to i64
  %215 = shl nsw i64 %211, 3
  %216 = shl i64 %214, %215
  %217 = or i64 %216, %210
  %218 = add nuw nsw i64 %188, 4
  %219 = add i64 %190, 4
  %220 = icmp eq i64 %219, %186
  br i1 %220, label %221, label %187, !llvm.loop !37

221:                                              ; preds = %187
  %222 = icmp eq i64 %183, 0
  br i1 %222, label %240, label %223

223:                                              ; preds = %221, %182
  %224 = phi i64 [ 0, %182 ], [ %218, %221 ]
  %225 = phi i64 [ 0, %182 ], [ %217, %221 ]
  %226 = icmp ne i64 %183, 0
  tail call void @llvm.assume(i1 %226)
  br label %227

227:                                              ; preds = %227, %223
  %228 = phi i64 [ %237, %227 ], [ %224, %223 ]
  %229 = phi i64 [ %236, %227 ], [ %225, %223 ]
  %230 = phi i64 [ %238, %227 ], [ 0, %223 ]
  %231 = getelementptr inbounds nuw i8, ptr %180, i64 %228
  %232 = load i8, ptr %231, align 1, !tbaa !9
  %233 = zext i8 %232 to i64
  %234 = shl nsw i64 %228, 3
  %235 = shl i64 %233, %234
  %236 = or i64 %235, %229
  %237 = add nuw nsw i64 %228, 1
  %238 = add i64 %230, 1
  %239 = icmp eq i64 %238, %183
  br i1 %239, label %240, label %227, !llvm.loop !59

240:                                              ; preds = %221, %227, %175
  %241 = phi i64 [ 0, %175 ], [ %217, %221 ], [ %236, %227 ]
  %242 = load ptr, ptr %2, align 8, !tbaa !15
  %243 = load i64, ptr %102, align 8, !tbaa !20
  %244 = mul nsw i64 %243, %107
  %245 = getelementptr inbounds i8, ptr %242, i64 %244
  %246 = load i64, ptr %103, align 8, !tbaa !21
  %247 = icmp sgt i64 %246, 0
  br i1 %247, label %248, label %262

248:                                              ; preds = %240, %248
  %249 = phi i64 [ %254, %248 ], [ 0, %240 ]
  %250 = shl nsw i64 %249, 3
  %251 = ashr i64 %241, %250
  %252 = trunc i64 %251 to i8
  %253 = getelementptr inbounds nuw i8, ptr %245, i64 %249
  store i8 %252, ptr %253, align 1, !tbaa !9
  %254 = add nuw nsw i64 %249, 1
  %255 = load i64, ptr %103, align 8, !tbaa !21
  %256 = icmp slt i64 %254, %255
  br i1 %256, label %248, label %257, !llvm.loop !45

257:                                              ; preds = %248
  %258 = load ptr, ptr %1, align 8, !tbaa !15
  %259 = load i64, ptr %4, align 8, !tbaa !20
  %260 = load i64, ptr %5, align 8, !tbaa !21
  %261 = mul nsw i64 %259, %176
  br label %262

262:                                              ; preds = %257, %240
  %263 = phi i64 [ %261, %257 ], [ %179, %240 ]
  %264 = phi i64 [ %260, %257 ], [ %106, %240 ]
  %265 = phi ptr [ %258, %257 ], [ %177, %240 ]
  %266 = getelementptr inbounds i8, ptr %265, i64 %263
  %267 = icmp sgt i64 %264, 0
  br i1 %267, label %268, label %277

268:                                              ; preds = %262, %268
  %269 = phi i64 [ %274, %268 ], [ 0, %262 ]
  %270 = shl nsw i64 %269, 3
  %271 = lshr i64 %107, %270
  %272 = trunc nuw nsw i64 %271 to i8
  %273 = getelementptr inbounds nuw i8, ptr %266, i64 %269
  store i8 %272, ptr %273, align 1, !tbaa !9
  %274 = add nuw nsw i64 %269, 1
  %275 = load i64, ptr %5, align 8, !tbaa !21
  %276 = icmp slt i64 %274, %275
  br i1 %276, label %268, label %277, !llvm.loop !45

277:                                              ; preds = %268, %262
  %278 = phi i64 [ %264, %262 ], [ %275, %268 ]
  %279 = add nuw nsw i64 %107, 1
  %280 = icmp eq i64 %279, 4
  br i1 %280, label %104, label %105, !llvm.loop !60
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
!9 = !{!7, !7, i64 0}
!10 = !{!11, !11, i64 0}
!11 = !{!"long", !7, i64 0}
!12 = distinct !{!12, !13}
!13 = !{!"llvm.loop.mustprogress"}
!14 = distinct !{!14, !13}
!15 = !{!16, !17, i64 0}
!16 = !{!"", !17, i64 0, !11, i64 8, !11, i64 16, !11, i64 24}
!17 = !{!"p1 omnipotent char", !18, i64 0}
!18 = !{!"any pointer", !7, i64 0}
!19 = !{!16, !11, i64 8}
!20 = !{!16, !11, i64 16}
!21 = !{!16, !11, i64 24}
!22 = distinct !{!22, !13, !23, !24}
!23 = !{!"llvm.loop.isvectorized", i32 1}
!24 = !{!"llvm.loop.unroll.runtime.disable"}
!25 = distinct !{!25, !13}
!26 = distinct !{!26, !13}
!27 = distinct !{!27, !13}
!28 = distinct !{!28, !13}
!29 = distinct !{!29, !13}
!30 = distinct !{!30, !13}
!31 = distinct !{!31, !13}
!32 = distinct !{!32, !13}
!33 = distinct !{!33, !13}
!34 = distinct !{!34, !13}
!35 = distinct !{!35, !13}
!36 = distinct !{!36, !13}
!37 = distinct !{!37, !13}
!38 = distinct !{!38, !39}
!39 = !{!"llvm.loop.unroll.disable"}
!40 = distinct !{!40, !39}
!41 = distinct !{!41, !39}
!42 = distinct !{!42, !39}
!43 = distinct !{!43, !39}
!44 = distinct !{!44, !39}
!45 = distinct !{!45, !13}
!46 = distinct !{!46, !39}
!47 = distinct !{!47, !13}
!48 = distinct !{!48, !13}
!49 = distinct !{!49, !39}
!50 = distinct !{!50, !13}
!51 = distinct !{!51, !39}
!52 = distinct !{!52, !39}
!53 = distinct !{!53, !39}
!54 = distinct !{!54, !13}
!55 = distinct !{!55, !39}
!56 = distinct !{!56, !39}
!57 = distinct !{!57, !13}
!58 = distinct !{!58, !39}
!59 = distinct !{!59, !39}
!60 = distinct !{!60, !13}
