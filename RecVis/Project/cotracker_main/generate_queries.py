import os
import torch
import numpy as np

from base64 import b64encode
from cotracker.utils.visualizer import Visualizer, read_video_from_path
from cotracker.predictor import CoTrackerPredictor
from IPython.display import HTML

path_vid = os.path.abspath('../data/hockey/anim.mp4') #path of a video

video = read_video_from_path(path_vid)
video = torch.from_numpy(video).permute(0, 3, 1, 2)[None].float()

def show_video(video_path): #function that display a video
    os.startfile(video_path)
    
#show_video(path_vid)

#Importing CoTrackerPredictor and creating an instance of it
"""model = CoTrackerPredictor(
    checkpoint=os.path.join(
        './checkpoints/cotracker2.pth'
    )
)"""

model = CoTrackerPredictor(
    checkpoint=os.path.join(
        'C:/Users/dofel/Desktop/cotracker2.pth'
    )
)


if torch.cuda.is_available():
    model = model.cuda()
    video = video.cuda()

#We will start by tracking points queried manually. We define a queried point as: [time, x coord, y coord]
#So, the code below defines points with different x and y coordinates sampled on frames 0, 10, 20, and 30


eps_L,eps_l = 100., 100.
n=150

x_rand = np.random.rand(n,1)*(float(video.shape[4])-2*eps_L) + eps_L
y_rand = np.random.rand(n,1)*(float(video.shape[3])-2*eps_l) + eps_l
frames_num = np.zeros((1,n),dtype=int).T

points = np.hstack((frames_num,x_rand,y_rand))

queries = torch.tensor(points.tolist())
#print(points)

"""queries = torch.tensor([
    [0., eps_L, eps_l],  # point tracked from the first frame
    [0., float(video.shape[4])-eps_L, eps_l], # frame number 0
    [0., eps_l, float(video.shape[3])-eps_l], # ...
    [0., float(video.shape[4])-eps_L, float(video.shape[3])-eps_l]
])

queries = torch.tensor([
    [0., 400., 350.],  # point tracked from the first frame
    [0., 600., 500.], # frame number 10
    [0., 750., 600.], # ...
    [0., 900., 200.]
])"""
if torch.cuda.is_available():
    queries = queries.cuda()
    
"""
import matplotlib.pyplot as plt
# Create a list of frame numbers corresponding to each point
frame_numbers = queries[:,0].int().tolist()

fig, axs = plt.subplots(2, 2)
axs = axs.flatten()

for i, (query, frame_number) in enumerate(zip(queries, frame_numbers)):
    ax = axs[i]
    ax.plot(query[1].item(), query[2].item(), 'ro') 
    
    ax.set_title("Frame {}".format(frame_number))
    ax.set_xlim(0, video.shape[4])
    ax.set_ylim(0, video.shape[3])
    ax.invert_yaxis()
    
plt.tight_layout()
plt.show()

"""


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
for i in range(n):
    plist.append(pred_tracks[0,:,i].cpu().numpy())

c=0
point_hash={} #hasmap with the points index in key and the label True if positive, False if negative in values
tresh = 0.008
for idx,p in enumerate(plist):
    #print(sum_dist(p))
    #print(is_Positive(p,0.02))
    if is_Positive(p,tresh):
        c+=1
        point_hash[idx] = True
    else: point_hash[idx] = False
  
print(c) #counter
print(point_hash) #point list with labels

nom='queries_hockey.txt'      #on crée une variable de type string
fichier=open(nom,'w')#ouverture du fichier en écriture : 'w' pour write
ecr_pos,ecr_neg='',''
for i in range(len(points)):
    if point_hash[i]:
        ecr_pos+=str(points[i][1])+','+str(points[i][2])+' ' #si le fichier n'existe pas, il est créé, sinon son contenu est écrasé
    else:
        ecr_neg+=str(points[i][1])+','+str(points[i][2])+' '
final = str(int(points[0][0]))+';' + ecr_pos +ecr_neg
fichier.write(str(c)+'\n')
fichier.write(final)
fichier.close() #close the document

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
show_video(path_show)