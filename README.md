# follow_wall
Package to make a differential robot follow a wall with a 2d lidar

## How it works

It uses an Euclidean distance based vector field, together with feedback linearization.

## Requirements

```bash
$ sudo apt-get install ros-$ROS_DISTRO-stage-ros ros-$ROS_DISTRO-map-server
```

## Instructions

Clone this repository into your `catkin_ws/src` folder:

```bash
$ git clone https://github.com/SillyEndless/follow_wall_py.git
```

Compile and source:

```bash
$ catkin_make
$ source ~/catkin_ws/devel/setup.bash
```

For a quick example, run:

```bash
$ roslaunch follow_wall follow_wall_stage.launch
```


## Parameters

The list of parameters are on the file inside the `config` folder. They are:

- `vr` (`float`): Robot's velocity

- `kf` (`float`): Convergence gain for the vector field

- `epsilon` (`float`): Distance from the wall

- `d` (`float`): Control distance for the feedback linearization

- `cmd_vel_topic` (`string`): Name of the cmd_vel topic

- `scan_topic` (`string`): Name of the laser scan topic

- `log_path_name` (`string`): Name of the laser frame

- `log_gt_flag` (`bool`): Enable the saving of gt data

- `gt_topic` (`string`): Name of the Odometry topic with ground truth (only if log_gt_flag = True)

- `log_path_name` (`string`): Path and name to save the ground truth log file (only if `log_gt_flag = True`)


## Contact

Adriano Rezende: ``adrianomcr18@gmail.com``

Universidade Federal de Minas Gerais
