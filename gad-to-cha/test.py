import tipsy_file as tf

with tf.streaming_reader('~/Projects/OortLimit/vertical_oscillations/200/snap_200_000.hdf5') as r:
	r.foo()
