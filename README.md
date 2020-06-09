# chatapp

CS300 Term Project


This application consists of a chat server and many chat clients (users).
A client can send messages to other clients through the server, and at the same time, can receive messages from other clients through the server.
The server accepts connections from the clients and delivers messages from one client to the other over Internet in real time.

## Preview

## Installation

1. Clone the repository to your local machine:
`git clone https://github.com/pchung0/chatapp.git`

2. Navigate to the clone folder:
`cd chatapp`

3. install virtualenv:
`python3 -m pip install --user virtualenv`

4. Create a virtual environment:
`python3 -m venv venv`

5. activate the virtual environment:
`source venv/bin/activate`

6. install the required python packages:
`pip install -r requirement.txt`

7. start the user service:
`python run_user.py`

8. start the chatroom service:
`python run_chatroom.py`

9. open the app by entering `localhost:5000` in a broswer address bar
