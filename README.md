# AI Online Exam Proctoring System

An AI-based online examination monitoring system developed using Python and Computer Vision techniques.

## Overview

This system monitors user behavior during online examinations using webcam-based head movement tracking.  
The application detects suspicious activities such as continuous distraction from the screen and automatically terminates the examination session if abnormal behavior is identified.

At the end of the session, the system stores:
- Session video recordings
- User activity graphs
- Examination results

The admin module allows monitoring and managing registered users, recorded sessions, graphs, and results.

## Features

### User Module

- User Login
- Online Examination Interface
- Head Movement Detection
- Left/Right Face Tracking
- Screen Attention Monitoring
- Automatic Session Termination
- Session Video Recording
- Activity Graph Generation

### Admin Module

- View Registered Users
- Access Session Videos
- View Activity Graphs
- Monitor Examination Results
- Manage User Records

## Technologies Used

- Python
- OpenCV
- Tkinter / Flask
- NumPy
- Matplotlib
- SQLite / MySQL

## AI Concepts Used

- Face Detection
- Head Pose Tracking
- Real-Time Monitoring
- Computer Vision
