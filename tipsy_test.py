import tipsy
import numpy as np

def check(x, true, msg):
    tol = 1e-6
    if np.isscalar(x):
        if not abs(x - true) < tol:
            raise ValueError(msg + ' should be ' + str(true) + ', but found ' + str(x))
    else:
        if not np.all(np.abs(x - true) < tol):
            raise ValueError(msg + ' should be \n' + str(true) + '\n, but found \n' + str(x))

def generate_data(size, rank):
    data = [None] * rank
    data[0] = np.random.rand(size)
    data[1] = np.random.rand(size, 3)
    data[2] = np.random.rand(size, 3)
     
    for i in range(rank - 3):
        data[i + 3] = np.random.rand(size)
    
    return data

def run_test(filename, is_xdr, ngas, ndark, nstar):
    time = 10.0
 
    with tipsy.streaming_writer(filename, is_xdr) as f:
        f.header(time, ngas, ndark, nstar)
        if ngas > 0:
            gas = generate_data(ngas, 8)
            f.gas(*gas, ngas)
        if ndark > 0:
            dark = generate_data(ndark, 5)
            f.darkmatter(*dark, ndark)
        if nstar > 0:
            star = generate_data(nstar, 7)
            f.stars(*star, nstar)

    with tipsy.File(filename, is_xdr) as f:
        hdr = f.header
        check(hdr.time, time, 'hdr.time')
        check(hdr.nbodies, ngas + ndark + nstar, 'hdr.nbodies')
        check(hdr.ngas, ngas, 'hdr.ngas')
        check(hdr.ndark, ndark, 'hdr.ndark')
        check(hdr.nstar, nstar, 'hdr.nstar')
        
        data = f.gas
        if data.size > 0:
            attrs = ['mass', 'pos', 'vel', 'rho', 'temp', 'hsmooth', 'metals', 'phi']
            for a in attrs:
                check(getattr(data, a), gas[attrs.index(a)], 'gas({0:d},{1:d},{2:d}).{3:s}'.format(ngas, ndark, nstar, a))
        data = f.darkmatter
        if data.size > 0:
            attrs = ['mass', 'pos', 'vel', 'soft', 'phi']
            for a in attrs:
                check(getattr(data, a), dark[attrs.index(a)], 'dark({0:d},{1:d},{2:d}).{3:s}'.format(ngas, ndark, nstar, a))
  
        data = f.stars
        if data.size > 0:
            attrs = ['mass', 'pos', 'vel', 'metals', 'tform', 'soft', 'phi']
            for a in attrs:
                check(getattr(data, a), star[attrs.index(a)], 'star({0:d},{1:d},{2:d}).{3:s}'.format(ngas, ndark, nstar, a))

#----------------------------------------------------------------------------------------

filename = 'test.tipsy'
for i in range(0, 201):
    try:
        run_test(filename, True, 0, 0, 0)
        run_test(filename, True, 0, 0, 13)
        run_test(filename, True, 0, 13, 0)
        run_test(filename, True, 0, 13, 13)
        run_test(filename, True, 13, 0, 0)
        run_test(filename, True, 13, 0, 13)
        run_test(filename, True, 13, 13, 0)
        run_test(filename, True, 13, 13, 13)
        run_test(filename, False, 0, 0, 0)
        run_test(filename, False, 0, 0, 13)
        run_test(filename, False, 0, 13, 0)
        run_test(filename, False, 0, 13, 13)
        run_test(filename, False, 13, 0, 0)
        run_test(filename, False, 13, 0, 13)
        run_test(filename, False, 13, 13, 0)
        run_test(filename, False, 13, 13, 13)
    except ValueError as err:
        print('iteration {0:d} failed'.format(i))
        import traceback
        traceback.print_exc()
        break
    else:
        print('Passed')

from os import unlink
unlink(filename)

