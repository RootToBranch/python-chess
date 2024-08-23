# server.py

import socket
import json
from _thread import *
from ast import literal_eval
from random import randint

client_sockets = []
statusManage = {}

def reset():
    print("Variable Reset Start")
    global statusManage, client_sockets
    client_sockets = []
    statusManage = {    
        "status": 0,
        "ready_array": [],
        "user_count": 0,
        "prev_selected_team": ""
    }

    print("Reset Completed")

reset()

# 서버 IP와 포트 설정
HOST = socket.gethostbyname(socket.gethostname())
PORT = 9999

def threaded(client_socket, addr):
    print('>> Connected by :', addr[0], ':', addr[1])
    print(client_socket)


    statusManage["ready_array"].append(client_socket)
    while True:
        try:

            data = client_socket.recv(1024)
            
            if not data:
                print('>> Disconnected by ' + addr[0], ':', addr[1])
                break


            data = literal_eval(data.decode())
            return_data = {"status": "wait"}

            
            



            if len(statusManage["ready_array"]) == 2 and statusManage["status"] < 1:
                return_data["status"] = "start"

                if statusManage["prev_selected_team"] == "":    
                    return_data["team"] = randomTeam()
                    statusManage["prev_selected_team"] = return_data["team"]
                elif statusManage["prev_selected_team"] == "black":
                    return_data["team"] = "white"
                else:
                    return_data["team"] = "black"

                return_data["turn"] = "white"
                statusManage["user_count"] += 1
                # 2명다 작업 완료 시에
                if statusManage["user_count"] == 2:
                    statusManage["status"] = 1
   
   


            if statusManage["status"] == 0:

                print("test")

                
            if statusManage["status"] == 1:
                if data['status'] == "in_progress":
                    return_data = {
                        "status": "in_progress",
                        "pieces": data["pieces"], 
                        "team": data["team"], 
                        "moveOrigin": [data['moveOrigin'][0], reverse_y(data['moveOrigin'][1])],
                        "moved": [data['moved'][0], reverse_y(data['moved'][1])],
                        "winner": None
                    }

                    if data["killedPiece"] == "king":
                        return_data["status"] = "finished"
                        return_data["winner"] = return_data['team']
                        return_data = str(return_data).encode()

                        for client in client_sockets:
                            client.send(return_data)
                        
                        print("게임 끝! 승자는 {}".format(return_data["winner"]))
                        exit()


                # if data['status'] == "not_received":
                #     continue


            return_data = str(return_data).encode()
            # 메시지를 다른 클라이언트에게 브로드캐스트
            for client in client_sockets:
                if client != client_socket:
                    client.send(return_data)

        except ConnectionResetError as e:
            print('>> Disconnected by ' + addr[0], ':', addr[1])
            break
    
    if client_socket in client_sockets:
        client_sockets.remove(client_socket)
        print('remove client list : ', len(client_sockets))

        if len(client_sockets) == 0:
            reset()

    client_socket.close()

def reverse_y(int):
    reverse = list(reversed([0, 1, 2, 3, 4, 5, 6, 7]))
    return reverse[int]

def randomTeam():

    teamArray = ["black", "white"]
    if(len(teamArray) <= 0):
        return
    integer = randint(0, 1)
    result = teamArray[integer]
    teamArray.remove(result)
    return result

# 소켓 생성 및 바인딩
# print('>> Server Start with IP :', HOST)
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((HOST, PORT))
server_socket.listen(2)

try:
    while True:
        print('>> Wait')
        client_socket, addr = server_socket.accept()
        client_sockets.append(client_socket)
        start_new_thread(threaded, (client_socket, addr))
        print("참가자 수 : ", len(client_sockets))
except Exception as e:
    print('에러 : ', e)
finally:
    server_socket.close()
