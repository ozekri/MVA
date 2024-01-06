import os
import torch
import numpy as np

from base64 import b64encode
from cotracker.utils.visualizer import Visualizer, read_video_from_path
from cotracker.predictor import CoTrackerPredictor
from IPython.display import HTML

##Parameters
path_vid = os.path.abspath('../data/swing/anim.mp4') #path of a video
is_checkpoint = False #True if the cotracker chkpt is in the right folder, False otherwise (if False, put the path to the checkpoint in "checkpoint_path")
checkpoint_path = 'C:/Users/dofel/Desktop/cotracker2.pth'

display_blank_vid = False #True if you want to display the original video at the beginning of the code, False otherwise
display_vid = True #True if you want to display the video after the code executes, False otherwise
display_details = True #True if you want to display the number of positive points and their classification during the first sampling

n=150 #Number of points for the first sampling
eps_L,eps_l = 100., 100. #Sampling edges

n_2=3 #Number of POSITIVE points for the second sampling
first_frame_2 = 0 #first frame to apply SAM-PT for the second sampling

## Main code

video = read_video_from_path(path_vid)
video = torch.from_numpy(video).permute(0, 3, 1, 2)[None].float()

def show_video(video_path): #function that display a video
    os.startfile(video_path)
    
if display_blank_vid: show_video(path_vid)

#Importing CoTrackerPredictor and creating an instance of it
if is_checkpoint:
    model = CoTrackerPredictor(checkpoint=os.path.join('./checkpoints/cotracker2.pth'))
else:
    model = CoTrackerPredictor(checkpoint=os.path.join(checkpoint_path))

if torch.cuda.is_available():
    model = model.cuda()
    video = video.cuda()

#We will start by sampling points randomnly in the full domain (excepting edges).
#We define a queried point as: [first_frame, x coord, y coord]
#So, the code below defines points with different x and y coordinates sampled from frame 0.

x_rand = np.random.rand(n,1)*(float(video.shape[4])-2*eps_L) + eps_L
y_rand = np.random.rand(n,1)*(float(video.shape[3])-2*eps_l) + eps_l
frames_num = np.zeros((1,n),dtype=int).T

points = np.hstack((frames_num,x_rand,y_rand))

queries = torch.tensor(points.tolist())


if torch.cuda.is_available():
    queries = queries.cuda()
    

pred_tracks, pred_visibility = model(video, queries=queries[None])

def sum_speed(l):
    res = 0
    for i in range(len(l)-1):
        res += np.linalg.norm(l[i]-l[i+1])
    return res
#create a big list L with the couples [res,normk]

def normalized_speed(L): #return a list with all the normalized speed
    norm = np.amax(np.array(L))
    res = []
    for elem in L:
        res.append(elem/norm)
    return res

def is_positive(p,tresh):
    if p > tresh: return False
    else: return True

traj_list=[]
for i in range(n):
    traj_list.append(pred_tracks[0,:,i].cpu().numpy())

L=[]
for traj in traj_list:
    L.append(sum_speed(traj))

normalized_s = normalized_speed(L)
   
c=0 #counter of posiitve points
point_hash={} #hasmap with the points index in key and the label True if positive, False if negative in values
tresh = 0.3 #treshold : posiitve or negative.

for idx,p in enumerate(normalized_s):
    if is_positive(p,tresh):
        c+=1
        point_hash[idx] = True
    else: point_hash[idx] = False


"""
def sum_dist(liste):
    res = 0
    norml = [np.linalg.norm(liste[-1])]
    for i in range(len(liste)-1):
        res += np.linalg.norm(liste[i]-liste[i+1])
        norml.append(np.linalg.norm(liste[i]))
    norm = sum(norml)
    return res/norm

def is_Positive(pt,tresh):
    if sum_dist(pt) > tresh: return False
    else: return True
    
plist=[]
for i in range(n):
    plist.append(pred_tracks[0,:,i].cpu().numpy())

c=0 #counter of posiitve points
point_hash={} #hasmap with the points index in key and the label True if positive, False if negative in values
tresh = 0.015 #treshold : posiitve or negative.

for idx,p in enumerate(plist):
    if is_Positive(p,tresh):
        c+=1
        point_hash[idx] = True
    else: point_hash[idx] = False
"""
if display_details:
    print(c) #counter
    print(point_hash) #point list with labels


min_x,max_x,min_y,max_y = np.inf,0.0,np.inf,0.0 #defining the new region of samples
x_neg,y_neg=0.0,0.0

for i in range(len(points)):
    if point_hash[i]:
        if min_x >= points[i][1] : min_x = points[i][1]
        if max_x <= points[i][1] : max_x = points[i][1]
        if min_y >= points[i][2] : min_y = points[i][2]
        if max_y <= points[i][2] : max_y = points[i][2]
    else:
        x_neg,y_neg = points[i][1],points[i][2]
    

#We are now sampling onto the second region.

x_rand_2 = np.random.rand(n_2+1,1)*(max_x-min_x) + min_x
x_rand_2[-1] = x_neg
y_rand_2 = np.random.rand(n_2+1,1)*(max_y-min_y) + min_y
y_rand_2[-1] = y_neg


frames_num_2 = np.zeros((1,n_2+1),dtype=int).T + first_frame_2

points_2 = np.hstack((frames_num_2,x_rand_2,y_rand_2))
queries_2 = torch.tensor(points_2.tolist())

#Here, we are creating the queries text file

nom='queries_swing_new.txt'
fichier=open(nom,'w')
ecr_pos,ecr_neg='',''

for i in range(len(points_2)-1):
    ecr_pos+=str(points_2[i][1])+','+str(points_2[i][2])+' '
ecr_neg+=str(points_2[-1][1])+','+str(points_2[-1][2])+' '

final = str(int(points_2[0][0]))+';' + ecr_pos +ecr_neg

fichier.write(str(n_2)+'\n')
fichier.write(final)
fichier.close()
  
#Now, we are creating the final video

vis = Visualizer(
    save_dir='./videos',
    linewidth=6,
    mode='cool',
    tracks_leave_trace=-1
)
vis.visualize(
    video=video,
    tracks=pred_tracks,
    visibility=pred_visibility,
    filename='queries');

path_show = os.path.abspath("./videos/queries.mp4")
if display_vid: show_video(path_show)