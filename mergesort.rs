use rand::prelude::*;
use std::time::Instant;
use std::vec::Vec;

struct Foo {
	nums: Vec<i32>
}

fn randint(a: i32, b: i32) -> i32 {
	return thread_rng().gen_range(a, b);
}

impl Foo {

	fn new(sz: i32) -> Foo {
		let mut f = Foo{nums: Vec::new()};
		for _ in 0 .. sz {
			f.nums.push(randint(0, 100));
		}
		return f;
	}

	fn is_sorted(&self) -> bool {
		if self.nums.len() < 2 {
			return true;
		}
		let mut val = self.nums[0];
		for i in 1 .. self.nums.len() {
			if self.nums[i] < val {
				return false;
			}
			val = self.nums[i];
		}
		return true;
	}

	fn shuffle(&mut self) {
		let length = self.nums.len() as i32;
		for n in 0 .. length {
			let i = randint(n, length);
			self.nums.swap(n as usize, i as usize);
		}
	}

	fn mergesort(&mut self) {
		Foo::__mergesort(&mut self.nums[..]);
	}

	fn __mergesort(v: &mut[i32]) {

		let vlen = v.len();

		// Trivial cases...

		if vlen < 2 {
			return;
		}

		if vlen == 2 {
			if v[0] <= v[1] {
				return;
			}
			let tmp = v[0];
			v[0] = v[1];
			v[1] = tmp;
			return;
		}

		// Hard cases...

		let mid = vlen / 2;

		Foo::__mergesort(&mut v[..mid]);
		Foo::__mergesort(&mut v[mid..]);

		let mut sorted = Vec::with_capacity(vlen);

		let mut i = 0;
		let mut j = mid;

		loop {
			if i >= mid && j >= vlen {
				break;
			} else if i >= mid {
				sorted.push(v[j]);
				j += 1;
			} else if j >= vlen {
				sorted.push(v[i]);
				i += 1;
			} else {
				if v[i] < v[j] {
					sorted.push(v[i]);
					i += 1;
				} else {
					sorted.push(v[j]);
					j += 1;
				}
			}
		}

		for n in 0 .. vlen {
			v[n] = sorted[n];
		}
	}
}

fn main() {

	let mut f = Foo::new(10_000_000);
	f.shuffle();

	let now = Instant::now();

	f.mergesort();
	assert!(f.is_sorted());

	println!("Mergesort took {:?}", now.elapsed());
}
