# Pure Python Core Logic

**DEVELOPMENT INSTRUCTIONS:**
Code your bare AI logic, helper classes, and functional scripts in this `core/` directory **without using any ROS imports** (`rclpy`, `Node`, etc.). 

1. Write classes here that take standard Python types (`strings`, `numpy arrays`, `dicts`).
2. Test them by writing simple `if __name__ == '__main__':` execution blocks or Jupyter Notebooks.
3. Later, the ROS nodes in the directory above will import your classes from here and wrap them in the ROS pub/sub middleware.
