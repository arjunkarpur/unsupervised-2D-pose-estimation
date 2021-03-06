import numpy as np
import h5py

# Inputs vars
top_n = 5

dist_grid_fp = "/net/cvcfs/storage/skull-atlas/imgscrape/dist_grids/finetune/triplets_two/1_28mil/margin_0_2/test_set_dist_grids.hdf5"

out_fp = "./out/check.txt"

imlist_fp = "./test_error/test_set.txt"
#imlist_fp = "../inputs/real_images.txt"

# Open distance grid data file for reading
dist_grid_f = h5py.File(dist_grid_fp, 'r')

# Read list of files to perform pose estimation
im_list = []
imlist_f = open(imlist_fp, 'r')
lines = imlist_f.readlines()
imlist_f.close()
for l in lines:
  im_list.append(l.split("\n")[0])

# Open output file
out_f = open(out_fp, 'w')

global total_pose_distance
total_pose_distance = 0
global total_other_distance
total_other_distance = 0
global total_count
total_count = 0

####################
#  BEGIN FUNCTIONS  #
#####################

def pose_estimation(dist_grid):
  min_pose = -1
  min_sum = -1
  total_sum = 0
  for p in range(len(dist_grid)):
    # Calculate sum of L2 distances for top N renderings per pose
    curr_sum = 0
    for n in range(top_n):
      curr_sum += float(dist_grid[p][n][1])
    #print "%i:\t %f" % (p,float(curr_sum)/float(top_n))
    total_sum += curr_sum 

    # Set the best pose as one with min top_n sum
    if (min_pose == -1 and min_sum == -1) or \
       (curr_sum < min_sum):
      min_pose = p
      min_sum = curr_sum

  total_sum -= min_sum
  print "Pose avg distance: %f" % (min_sum/top_n)
  print "Other avg distance: %f" % (total_sum/(top_n*(len(dist_grid)-1)))
  global total_pose_distance 
  total_pose_distance += (min_sum/top_n)
  global total_other_distance
  total_other_distance += (total_sum/(top_n*(len(dist_grid)-1)))
  global total_count
  total_count += 1
  return min_pose

#####################
#   END FUNCTIONS   #
#####################

print "Performing pose estimation for %i images" % len(im_list)
count = 0
for im in im_list:
  count += 1
  print "Pose estimation: %i / %i" % (count, len(im_list))
  if im not in dist_grid_f:
    print "ERROR: No distance grid available for image %s" % im
    continue
  curr_pose = pose_estimation(dist_grid_f[im])
  out_f.write("%s %s\n" % (im, str(curr_pose)))

print "All avg pose distance: %f"  % (total_pose_distance/total_count)
print "All avg non-pose distance: %f" % (total_other_distance/total_count)

# Close files
dist_grid_f.close()
out_f.close()
