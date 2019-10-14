'''
@author: Darren Janeczek
'''

from numpy import sin, cos, arcsin
import numpy
import os

def interpolate(x_vector, y_vector, h, c=2.0, scale_factor=1.0, 
                target_divisions=10, save_images=None, show_steps=False, viewer_callback=None):
    ''' Accepted approach '''

    zero = numpy.zeros(3, dtype=float)
    x = numpy.zeros(3, dtype=float)
    y = numpy.zeros(3, dtype=float)

    x[:] = x_vector
    y[:] = y_vector
    z = numpy.cross(x_vector, y_vector)
    z_unit = z / numpy.linalg.norm(z)
    
    del x_vector
    del y_vector

    P = numpy.zeros((2, 2, 3), dtype=float)
    P[0,0] = zero
    P[1,0] = x
    P[0,1] = y
    P[1,1] = x + y

    scale = scale_factor * (numpy.linalg.norm(x) + numpy.linalg.norm(y)) / 2
    ratio = c ** (-h)

    def displace(pt_pairs, std):
        pts = []
        displacements = []
        
        for pt1, pt2 in pt_pairs:
            pts.append(pt1)
            pts.append(pt2)
        
            M, N, _ = pt1.shape
            
            delta = pt2 - pt1
            delta_mag = numpy.linalg.norm(delta, axis=2)[:,:,numpy.newaxis]
            delta_unit = delta / delta_mag

            gauss = numpy.random.randn(M, N, 1) * std
            
            displacement = numpy.zeros((M, N, 3), dtype=float)
            dp = numpy.tensordot(z_unit, delta_unit, axes=([0],[2]))
            theta = arcsin(dp)
            
            displacement[:,:] = (cos(theta)[:,:,numpy.newaxis] * z_unit + 
                                 delta_unit * sin(theta)[:,:,numpy.newaxis])
            displacement[:,:,:] *= gauss
            
            displacements.append(displacement)
        
        midpoint = numpy.mean(pts, axis=0)
        return midpoint + numpy.mean(displacements, axis=0)

    divisions = 0
    
    std = scale * ratio
    
    while target_divisions >= divisions:
        M, N, _ = P.shape
        if show_steps and viewer_callback:
            if save_images:
                screenshot = "../output/%s-%02d.png" % (save_images, divisions)
                print("Wrote file %s. " % os.path.abspath(screenshot))
                viewer_callback(P, screenshot_file=screenshot)
            else:
                viewer_callback(P)

        if target_divisions == divisions:
            if (not show_steps or save_images) and viewer_callback:
                #Because we would have already shown it
                viewer_callback(P)
            break

        divisions += 1

        QM = M * 2 - 1
        QN = N * 2 - 1

        Q = numpy.zeros((QM + 2, QN + 2, 3), dtype=float)
        # COPY ORIGINALS ##################################
        Q[:QM:2,:QN:2] = P[:,:] 
        
        # DIAMOND STEP ####################################
        
        # middle nodes
        UL = P[:M-1,:N-1]
        LL = P[:M-1,1:]
        UR = P[1:,:N-1]
        LR = P[1:,1:]
        Q[1:QM:2, 1:QN:2] = displace([(LR, UL), (LL, UR)], std)

        # SET UP BUFFER ###################################

        # Continue the slope to the left of Q (i=-1)
        U = P[0, :N-1]
        D = P[0, 1:]
        R = Q[1, 1:QN:2]
        mean_UD = numpy.mean((U, D), axis=0)
        Q[-1, 1:QN:2] = mean_UD + (mean_UD - R)

        # Continue the slope to the right of Q (i=QM)
        U = P[M-1, :N-1]
        D = P[M-1, 1:]
        L = Q[QM-2, 1:QN:2]
        mean_UD = numpy.mean((U, D), axis=0)
        Q[QM, 1:QN:2] = mean_UD + (mean_UD - L)

        # Continue the slope to the up of Q (j=-1)
        L = P[:M-1, 0]
        R = P[1:, 0]
        D = Q[1:QM:2, 1]
        mean_LR = numpy.mean((L, R), axis=0)
        Q[1:QM:2, -1] = mean_LR + (mean_LR - D)

        # Continue the slope to the down of Q (j=QN)
        L = P[:M-1, N-1]
        R = P[1:, N-1]
        U = Q[1:QM:2, QN-2]
        mean_LR = numpy.mean((L, R), axis=0)
        Q[1:QM:2, QN] = mean_LR + (mean_LR - U)

        # Square Step #########################################

        # Even rows
        L = P[0:M-1, :]
        R = P[1:M, :]
        U = Q[1:QM:2, range(-1,QN-1,2)]
        D = Q[1:QM:2, 1:QN+1:2]
        Q[1:QM:2, 0:QN:2] = displace([(U, D), (L, R)], std)

        # Odd rows
        L = Q[range(-1,QM-1,2), 1:QN:2]
        R = Q[range(1,QM+1,2), 1:QN:2]
        U = P[:, 0:N-1]
        D = P[:, 1:N]
        Q[0:QM:2, 1:QN:2] = displace([(U, D), (L, R)], std)

        # CORRECT ORIGINAL POINTS ##################################

        # Smooth original points to match
        Q[2:QM-1:2,2:QN-1:2] = numpy.mean(
            (
                Q[2-1:QM-1-1:2,2:QN-2:2],
                Q[2+1:QM-1+1:2,2:QN-2:2],
                Q[2:QM-1:2,2-1:QN-2-1:2],
                Q[2:QM-1:2,2+1:QN-2+1:2],
            ), axis=0
        )

        #LEFT edge originals
        Q[0,2:QN-1:2] = numpy.mean(
            (
                Q[0,2-1:QN-2-1:2],
                Q[0,2+1:QN-2+1:2],
            ), axis=0
        )
 
        #RIGHT edge originals                 
        Q[QM-1,2:QN-1:2] = numpy.mean(
            (
                Q[QM-1,2-1:QN-2-1:2],
                Q[QM-1,2+1:QN-2+1:2],
            ), axis=0
        )
 
        #UP edge originals
        Q[2:QM-1:2,0] = numpy.mean(
            (
                Q[2-1:QM-1-1:2,0],
                Q[2+1:QM-1+1:2,0],
            ), axis=0
        )
 
        #DOWN edge originals
        Q[2:QM-1:2,QN-1] = numpy.mean(
            (
                Q[2-1:QM-1-1:2,QN-1],
                Q[2+1:QM-1+1:2,QN-1],
            ), axis=0
        )

        std *= ratio
        P = Q[:QM,:QN]

    return P
