#!/usr/bin/env python
import rospy
from geometry_msgs.msg import Twist, Point
from nav_msgs.msg import Odometry
from sensor_msgs.msg import LaserScan
from visualization_msgs.msg import Marker, MarkerArray
from math import sqrt, atan2, exp, atan, cos, sin, acos, pi, asin, atan2
from tf.transformations import euler_from_quaternion, quaternion_from_euler
import numpy as np
from random import randrange
from time import sleep
import tf





# Callback to get the ground truth (if simulator stage is used)
def callback_gt(data):
    global FILE

    my_str = str(data.pose.pose.position.x) + "\t"
    my_str = my_str + str(data.pose.pose.position.y) + "\t"
    my_str = my_str + str(data.pose.pose.orientation.z) + "\n"

    #Write to file
    FILE.write(my_str)

    return
# ----------  ----------  ----------  ----------  ----------






# Callback to get the laser data
def callback_laser(data):
    global delta_m, phi_m, new_data

    laserVec = data.ranges

    #Compute the minimum distance and get the direction of the correspondent point
    delta_m = 1000000
    k_m = -1
    for k in range(len(laserVec)):
        if(laserVec[k] < delta_m and laserVec[k] > 0.10):
            delta_m = laserVec[k]
            k_m = k

    #Compute the associated direction in the body frame
    phi_m = data.angle_min + k_m*data.angle_increment

    new_data = True

    return
# ----------  ----------  ----------  ----------  ----------








# Function to compute the control law
def compute_command():

    G = (2/pi)*atan(kf*(delta_m-epsilon))
    H = sqrt(1-G*G)

    v = vr*(cos(phi_m)*G -sin(phi_m)*H)
    omega = vr*(sin(phi_m)*G/d + cos(phi_m)*H/d)

    return (v, omega)
# ----------  ----------  ----------  ----------  ----------







def follow_wall():
    global x_n, y_n, theta_n
    global pub_rviz, pub_targ, pub_pose
    global freq
    global new_data


    rospy.init_node("follow_wall")

    pub_stage = rospy.Publisher(cmd_vel_topic, Twist, queue_size=1)
    pub_close_point = rospy.Publisher("closest_laser_marker", Marker, queue_size=1)
    rospy.Subscriber(scan_topic, LaserScan, callback_laser)
    if(log_gt_flag):
        rospy.Subscriber(gt_topic, Odometry, callback_gt)
        global FILE
        FILE  = open(log_path_name, "w")

    vel = Twist()

    #Define a marker to indicate the closest point
    close_point_marker = Marker()
    close_point_marker.header.frame_id = laser_frame_id
    close_point_marker.header.stamp = rospy.Time.now()
    close_point_marker.id = 0
    close_point_marker.type = close_point_marker.SPHERE
    close_point_marker.action = close_point_marker.ADD
    close_point_marker.scale.x = 3*d
    close_point_marker.scale.y = 3*d
    close_point_marker.scale.z = 3*d
    close_point_marker.color.a = 1.0
    close_point_marker.color.r = 0.0
    close_point_marker.color.g = 0.0
    close_point_marker.color.b = 1.0
    close_point_marker.pose.orientation.w = 1.0
    close_point_marker.pose.position.x = 0.0
    close_point_marker.pose.position.y = 0.0
    close_point_marker.pose.position.z = d

    freq = 10.0  # Hz
    rate = rospy.Rate(freq)

    sleep(1)

    i = freq+1
    while not rospy.is_shutdown():

        i = i + 1

        if(new_data):
            (v, omega) = compute_command()
            i = 0
            #Update the marker that indicates the closest point
            close_point_marker.pose.position.x = delta_m*cos(phi_m)
            close_point_marker.pose.position.y = delta_m*sin(phi_m)
            close_point_marker.pose.position.z = d
            pub_close_point.publish(close_point_marker)
            new_data = False
        elif(i > freq):
            #Stop the robot if laser is out for one second
            v = 0.0
            omega = 0.0

        vel.linear.x = v
        vel.angular.z = omega

        #Publish velocity command
        pub_stage.publish(vel)

        rate.sleep()


    if(log_gt_flag):
        FILE.close()

# ---------- !! ---------- !! ---------- !! ---------- !! ----------










# Main function
if __name__ == '__main__':


    global vr #velocity for the robot
    vr = 1
    global kf #convergence gain for the vector field
    kf = 1
    global epsilon # distance from the wall
    epsilon = 1
    global d  #for feedback linearization
    d = 0.2
    global cmd_vel_topic #name of the cmd_vel topic
    cmd_vel_topic = "cmd_vel"
    global scan_topic #name of the laser scan topic
    scan_topic = "scan"
    global laser_frame_id #name of the laser frame
    laser_frame_id = "base_laser_link"

    #Falg for new laser data
    global new_data
    new_data = False

    #Measurements from the laser
    global delta_m, phi_m


    #Load parameters
    #try:
    vr = float(rospy.get_param("/follow_wall/vr"))
    kf = float(rospy.get_param("/follow_wall/kf"))
    epsilon = float(rospy.get_param("/follow_wall/epsilon"))
    d = float(rospy.get_param("/follow_wall/d"))
    cmd_vel_topic = rospy.get_param("/follow_wall/cmd_vel_topic")
    scan_topic = rospy.get_param("/follow_wall/scan_topic")
    laser_frame_id = rospy.get_param("/follow_wall/laser_frame_id")
    log_gt_flag = bool(rospy.get_param("/follow_wall/log_gt_flag"))
    if(log_gt_flag):
        gt_topic = rospy.get_param("/follow_wall/gt_topic")
        log_path_name = rospy.get_param("/follow_wall/log_path_name")
        #print "\n\33[92mParameters loaded\33[0m"
        #print "\33[94mvr: ", vr,"\33[0m"
        #print "\33[94mkf: ", kf,"\33[0m"
        #print "\33[94mepsilon: ", epsilon,"\33[0m"
        #print "\33[94md: ", d,"\33[0m"
        #print "\33[94mcmd_vel_topic: ", cmd_vel_topic,"\33[0m"
        #print "\33[94mscan_topic: ", scan_topic,"\33[0m"
        #print "\33[94mlaser_frame_id: ", laser_frame_id,"\33[0m"
        #print "\33[94mlog_gt_flag: ", log_gt_flag,"\33[0m"
        if(log_gt_flag):
            #print "\33[94mgt_topic: ", gt_topic,"\33[0m"
            #print "\33[94mlog_path_namec: ", log_path_name,"\33[0m"
    #except:
        #print "\33[41mProblem occurred when trying to read the parameters!\33[0m"
        #print "\33[41mNode follow_wall.py\33[0m"



    #try:
            follow_wall()
    #except rospy.ROSInterruptException:
    pass
