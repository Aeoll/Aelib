#ifndef __arrays3d_detail_
#define __arrays3d_detail_

// Macros for easier array3d method usage
#define set3d(arr,x,y,z,val)			arr.f[x + y*arr.cols + z*arr.rows*arr.cols] = val
#define get3d(arr,x,y,z)				arr.f[x + y*arr.cols + z*arr.rows*arr.cols]

#define a3d(var,r,c,s) \
array3d var;  \
var->init(r, c, s) \

#define zeros(var,r,c,s) \
array3d var; \
var->init(r, c, s, 0.0) \

// Want to support int, float, vector array3d but its not straightforward? keep them separate? array3di/array3df/array3dv?
// separate structs? this would mean reproducing a of functions..?
struct array3d {
	int rows;
	int cols;
	int slices;
	float f[];

	function void init() {
		resize(f, rows*cols*slices);
	}

	function void init(int r; int c; int s) {
		rows = r;
		cols = c;
		slices = s;
		resize(f, rows*cols*slices);
	}

	// initialise with value for all?
	function void init(int r; int c; int s; float val) {
		rows = r;
		cols = c;		
		slices = s;
		resize(f, rows*cols*slices);
		for(int i = 0; i < len(f); i++){
			f[i] = val;
		}
	}

	function void init(int r; int c; int s; float a[]) {
		rows = r;
		cols = c;		
		slices = s;
		resize(f, rows*cols*slices);
		f = a;
	}

	// =======================================
	// Utility
	// =======================================
	void resize(int r; int c; int s) {
		rows = r;
		cols = c;
		slices = s;
		resize(f, rows*cols*slices);
	}

	vector index(int i){
		// int x = int(i/cols);
		// int y = int(i%cols);
		// int z = int(i/(rows*cols));
		int z = int(i / (rows*cols));
		int i2 = i - (z * rows * cols);
		int y = int(i2 / cols); 
		int x = int(i2 % cols);
		return set(x, y, z);
	}
	
	int index(vector xyz){
		// return int(xy.x*cols) + int(xy.y); // old
		return int(xyz.x) + int(xyz.y*cols) + int(xyz.z * rows * cols);
	}

	int printlen() {
		printf("%d", len(f));
	}

	float getf(int x; int y; int z) {
		return f[x + cols*y + z*rows*cols];
	}

	void setf(int x; int y; int z; float v) {
		f[x + y*cols + z*rows*cols] = v;
	}

	// slice the current array3d along axes
	// TODO still not working?
	array3d subarray(int x_min; int x_max; int y_min; int y_max; int z_min; int z_max) {
		array3d sub;
		int r = x_max-x_min;
		int c = y_max-y_min;
		int s = z_max-z_min;
		sub->init(r, c, s);
		for(int i = 0; i < r; i++){
			for(int j = 0; j < c; j++){
				for(int k = 0; k < s; k++){
					float v = this->getf(x_min+i, y_min+j, z_min+k);
					sub->setf(i, j, k, v);
				}
			}	
		}
		sub->resize(r,c,s);
		return sub;
	}
	
	// sets all values of the array3d subarray to val
	// TODO not working atm...
	void setSubarray(int x_min; int x_max; int y_min; int y_max; int z_min; int z_max; float val){
		int r = x_max - x_min;
		int c = y_max - y_min;
		int s = z_max - z_min;
		for(int i = 0; i < r; i++){
			for(int j = 0; j < c; j++){
					for(int k = 0; l < s; k++){
					this->setf(x_min+i, y_min+j, z_min+k, val);
				}
			}	
		}
	}

	// count number of nonzero elements
	int count_nonzero() {
		int c = 0;
		foreach(float val; f){
			c += (val != 0)?1:0;
		}
		return c;
	}

	// get nonzero elements
	// any advantage to returning array of vec2 instead of array2d like python does?
	vector[] nonzero() {
		vector nonzero[];
		foreach(int ind; float val; f){
			if(val != 0){
				vector xyz = this->index(ind);
				append(nonzero, xyz);
			}
		}
		return nonzero;
	}	

	// print
	void print3d() {
		// printf("%dx%dx%d\n", rows, cols, slices);
		// for (int i = 0; i < rows; i++) {
		// 	for (int j = 0; j < cols; j++) {
		// 			int y = cols  * i;
		// 			int x = (i *cols) + cols;
		// 			printf("%g)\t%8d\n ", i + 1, slice(f, y, x));
		// 	}
		// }
		for (int k = 0; k < slices; k++) {
			for (int i = 0; i < rows; i++) {
			for (int j = 0; j < cols; j++) {
					float val = this->getf(i,j,k);
					printf("%d", val);
				}
				printf("_\n");
			}
			printf("____\n");
		}
		printf("\n");
	}

	void printsize() {
		printf("%d", set(rows,cols,slices));
		printf("\n%d", len(f));
		//printf("\n%d", f);
		printf("\n");
	}	
};

#endif