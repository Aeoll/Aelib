#ifndef __arrays_detail_
#define __arrays_detail_

// Macros for easier array2d method usage
#define set2d(arr,x,y,val)			arr.f[x * arr.cols + y] = val
#define get2d(arr,x,y)				arr.f[x * arr.cols + y]

#define a2d(var,r,c) \
array2d var;  \
var->init(r, c) \

#define zeros(var,r,c) \
array2d var; \
var->init(r, c, 0.0) \

// Want to support int, float, vector array2d but its not straightforward? keep them separate? array2di/array2df/array2dv?
// separate structs? this would mean reproducing a of functions..?
struct array2d {
	int rows;
	int cols;
	float f[];

	function void init() {
		resize(f, rows*cols);
	}

	function void init(int r; int c) {
		rows = r;
		cols = c;
		resize(f, rows*cols);
	}

	// initialise with value for all?
	function void init(int r; int c; float val) {
		rows = r;
		cols = c;		
		resize(f, rows*cols);
		for(int i = 0; i < len(f); i++){
			f[i] = val;
		}
	}

	function void init(int r; int c; float a[]) {
		rows = r;
		cols = c;		
		resize(f, rows*cols);
		f = a;
	}

	// =======================================
	// Utility
	// =======================================
	void resize(int r; int c) {
		rows = r;
		cols = c;
		resize(f, rows*cols);
	}

	vector2 index(int i){
		int x = int(i/cols);
		int y = int(i%cols);
		return set(x, y);
	}
	
	int index(vector2 xy){
		return int(xy.x*cols) + int(xy.y);
	}

	float getf(int x; int y) {
		return f[x*cols + y];
	}

	void setf(int x; int y; float v) {
		f[x*cols + y] = v;
	}

	// slice the current array2d along both axes
	// TODO still not working?
	array2d subarray(int x_min; int x_max; int y_min; int y_max) {
		array2d sub;
		int r = x_max-x_min;
		int c = y_max-y_min;
		sub->init(r, c);
		for(int i = 0; i < r; i++){
			for(int j = 0; j < c; j++){
				float v = this->getf(x_min+i, y_min+j);
				sub->setf(i, j, v);
			}	
		}
		return sub;
	}
	
	// sets all values of the array2d subarray to val
	// TODO not working atm...
	void setSubarray(int x_min; int x_max; int y_min; int y_max; float val){
		int r = x_max - x_min;
		int c = y_max - y_min;
		for(int i = 0; i < r; i++){
			for(int j = 0; j < c; j++){
				this->setf(x_min+i, y_min+j, val);
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
	vector2[] nonzero() {
		vector2 nonzero[];
		foreach(int ind; float val; f){
			if(val != 0){
				vector2 xy = this->index(ind);
				append(nonzero, xy);
			}
		}
		return nonzero;
	}	

	// print
	void print2d() {
		printf("%dx%d\n", rows, cols);
		for (int i = 0; i < rows; i++) {
				int y = cols  * i;
				int x = (i *cols) + cols;
				printf("%g)\t%8d\n ", i + 1, slice(f, y, x));
		}
	}
};

#endif