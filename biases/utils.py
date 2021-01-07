from torch import Tensor
from scipy.spatial.transform import Rotation
import torch
import numpy as np
from oil.utils.utils import export
import random
import torch

@export
class FixedSeedAll(object):
    def __init__(self, seed):
        self.seed = seed
    def __enter__(self):
        self.np_rng_state = np.random.get_state()
        np.random.seed(self.seed)
        self.rand_rng_state = random.getstate()
        random.seed(self.seed)
        self.pt_rng_state = torch.random.get_rng_state()
        torch.manual_seed(self.seed)
    def __exit__(self, *args):
        np.random.set_state(self.np_rng_state)
        random.setstate(self.rand_rng_state)
        torch.random.set_rng_state(self.pt_rng_state)

def rel_err(x: Tensor, y: Tensor) -> Tensor:
    return (((x - y) ** 2).sum() / ((x + y) ** 2).sum()).sqrt()

def cross_matrix(k):
    """Application of hodge star on R3, mapping Λ^1 R3 -> Λ^2 R3.
        See e.g. (https://en.wikipedia.org/wiki/Angular_velocity)"""
    K = torch.zeros(*k.shape[:-1],3,3,device=k.device,dtype=k.dtype)
    K[...,0,1] = -k[...,2]
    K[...,0,2] = k[...,1]
    K[...,1,0] = k[...,2]
    K[...,1,2] = -k[...,0]
    K[...,2,0] = -k[...,1]
    K[...,2,1] = k[...,0]
    return K

def uncross_matrix(K):
    """Application of hodge star on R3, mapping Λ^2 R3 -> Λ^1 R3
        See e.g. (https://en.wikipedia.org/wiki/Angular_velocity)"""
    k = torch.zeros(*K.shape[:-1],device=K.device,dtype=K.dtype)
    k[...,0] = (K[...,2,1] - K[...,1,2])/2
    k[...,1] = (K[...,0,2] - K[...,2,0])/2
    k[...,2] = (K[...,1,0] - K[...,0,1])/2
    return k

def eulerdot2omega(euler): #(reference: https://arxiv.org/pdf/1407.8155.pdf)
    """ Given euler angles (phi,theta,psi) produces the matrix which converts
        from euler angle derivatives (phi_dot,theta_dot,psi_dot) to angular
        velocity (wx,wy,wz) expressed in the body frame. Supports batch dimension.
        input: [euler (bs,3)]
        output: [M (bs,3,3)]"""
    bs,_ = euler.shape
    M = torch.zeros(bs,3,3,device=euler.device,dtype=euler.dtype)
    phi,theta,psi = euler.T
    M[:,0,0] = theta.sin()*psi.sin()
    M[:,0,1] = psi.cos()
    M[:,1,0] = theta.sin()*psi.cos()
    M[:,1,1] = -psi.sin()
    M[:,2,0] = theta.cos()
    M[:,2,2] = 1
    return M

@export
def euler2frame(euler_and_dot):
    """ Given an array that contains euler angles and derivatives, return an array
        containing the frame (as expressed by the rotation matrix R) and its derivatives (R_dot).
        input: (bs,2,3)
        output: (bs,2,3,3)"""
    euler,eulerdot = euler_and_dot.permute(1,0,2)
    omega = (eulerdot2omega(euler)@eulerdot.unsqueeze(-1)).squeeze(-1)
    # omega = (angular velocity in the body frame)
    RT_Rdot = cross_matrix(omega) 
    R = torch.from_numpy(Rotation.from_euler('ZXZ',euler.data.cpu().numpy()).as_matrix()).to(euler.device,euler.dtype)
    Rdot = R@RT_Rdot
    return torch.stack([R,Rdot],dim=1).permute(0,1,3,2) # (bs,2,d,n->bs,2,n,d)

@export
def frame2euler(frame_pos_vel):
    """ Inverts euler2frame, converts from frame+derivatives-> euler+derivatives
        input: (bs,2,3,3)
        output: (bs,2,3)"""
    R,Rdot = frame_pos_vel.permute(1,0,3,2) #(bs,3,3)
    omega = uncross_matrix(R.permute(0,2,1)@Rdot) #angular velocity in body frame Omega = RTRdot
    angles = torch.from_numpy(np.ascontiguousarray(Rotation.from_matrix(R.data.cpu().numpy()).as_euler('ZXZ'))).to(R.device,R.dtype)
    eulerdot = torch.solve(omega.unsqueeze(-1),eulerdot2omega(angles))[0].squeeze(-1)
    return torch.stack([angles,eulerdot],dim=1)

@export
def bodyX2comEuler(X):
    """ Converts from they body matrix X (4,3) along with its derivatives X_dot (4,3) 
        stacked as (2,4,3) to the center of mass and derivative (2,3) and euler angles
        and derivatives (2,3) stacked together. Includes a batch axis
        input: (bs,2,4,3) output: (bs,2,6)"""
    xcom = X[:,:,0] #(bs,2,3)
    euler = frame2euler(X[:,:,1:]-xcom[:,:,None,:])
    return torch.cat([xcom,euler],dim=-1)


@export
def comEuler2bodyX(com_euler):
    """ Inverse of bodyX2comEuler
        output: (bs,2,6) input: (bs,2,4,3) """
    xcom = com_euler[:,:,:3] #(bs,2,3)
    frame = euler2frame(com_euler[:,:,3:]) #(bs,2,3,3)
    shifted_frame = frame+xcom[:,:,None,:] # (bs,2,3,3)
    return torch.cat([xcom[:,:,None,:],shifted_frame],dim=-2)

@export
def read_obj(filename):
    import pywavefront
    scene = pywavefront.Wavefront(filename,collect_faces=True)
    return np.roll(np.array(scene.vertices),1,axis=1), np.array(np.concatenate([mesh.faces for mesh in scene.mesh_list]))

def Vols(mesh_verts):
    """ computes the volume of an obj from vertices of the boundary mesh"""
    #(num verts, verts per triangle, xyz)
    return mesh_verts.det()/6
    
def Coms(mesh_verts):
    """ (bs,n,d) -> (bs,d)"""
    return mesh_verts.sum(1)/4

def ExxT(V,mu):
    """ (bs,n,d), (bs,d) -> (bs,d,d)"""
    return (V.permute(0,2,1)@V)/20+(4/5)*mu[:,None]*mu[:,:,None]

@export
def compute_moments(mesh_verts):
    with torch.no_grad():
        vols = Vols(mesh_verts)
        Vol = vols.sum()
        weights = vols/Vol
        coms = Coms(mesh_verts)
        Com = (coms*weights[:,None]).sum(0)
        xxT = (ExxT(mesh_verts,coms)*weights[:,None,None]).sum(0)
        covar = xxT-Com[None,:]*Com[:,None]
        return Vol,Com,covar
