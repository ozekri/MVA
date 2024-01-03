import os
import torch
import numpy as np

from base64 import b64encode
from cotracker_main.cotracker.utils.visualizer import Visualizer, read_video_from_path
from cotracker_main.cotracker.predictor import CoTrackerPredictor
from IPython.display import HTML


path_vid=os.path.abspath(os.getcwd() + '/code/data/bus/anim.mp4') #path of a video

video = read_video_from_path(path_vid)
video = torch.from_numpy(video).permute(0, 3, 1, 2)[None].float()

def show_video(video_path): #function that display a video
    os.startfile(video_path)
    
show_video(path_vid)

#Importing CoTrackerPredictor and creating an instance of it
model = CoTrackerPredictor(
    checkpoint=os.path.join(
        './checkpoints/cotracker2.pth'
    )
)

if torch.cuda.is_available():
    model = model.cuda()
    video = video.cuda()

#We will start by tracking points queried manually. We define a queried point as: [time, x coord, y coord]
#So, the code below defines points with different x and y coordinates sampled on frames 0, 10, 20, and 30

queries = torch.tensor([
    [0., 400., 350.],  # point tracked from the first frame
    [10., 600., 500.], # frame number 10
    [20., 750., 600.], # ...
    [30., 900., 200.]
])
if torch.cuda.is_available():
    queries = queries.cuda()
    
pred_tracks, pred_visibility = model(video, queries=queries[None])

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
for i in range(4):
    plist.append(pred_tracks[0,:,i].cpu().numpy())
    
for p in plist:
  print(is_Positive(p,0.03))
  
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

show_video("./videos/queries.mp4")