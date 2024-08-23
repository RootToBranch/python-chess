# client.py


from tkinter import *
from tkinter import messagebox, font
from randomId import randomUUID
import pygame
import threading

import socket
from _thread import *
from time import sleep
from ast import literal_eval

import pyglet

default_setting = {
    "x": 0,
    "y": 0,
    "width": 866,
    "height": 866
}

HOST = ""
PORT = ""


user = {
    "team": "",
}



current_turn_team = ""
interface_status = 0 # 게임 레이아웃 관리
cursor_x = 0  
cursor_y = 0
mouse_x = 0
mouse_y = 0

# mouse_click = 0 # 클릭 감지
mouse_pieces_selected = 0

current_selected_pieces = 0


root = Tk()
root.title("Chess") # 창 이름
root.resizable(False,False) # 창 크기 조절 막기


root.geometry("860x860")

pyglet.font.add_file('font/Pretendard-Medium.otf')


bg = PhotoImage(file="img/chess-board.png")
cursor = PhotoImage(file="img/cursor.png")

pygame.mixer.init()
sound_effect = pygame.mixer.Sound("./sounds/move-self.mp3")

# ==============================

#
# Frame_start section
#

frame_start = Frame(root, relief='solid')
frame_start.place(x=0, y=0, width=860, height=860)

# def change_status(int):
#     global interface_status
#     interface_status = int

client = None



Label(frame_start, text="서버 주소",font="Pretendard").pack(pady=10)
addressInput = Entry(frame_start)
addressInput.pack(pady=10)

Label(frame_start, text="포트", font="Pretendard").pack(pady=10)
portInput = Entry(frame_start)
portInput.pack(pady=10)

gameStartBtn = Button(frame_start, text="게임 시작", font="Pretendard", command= lambda: connect_server(addressInput.get(), portInput.get()))
gameStartBtn.pack(pady=15)


# Debug

addressInput.insert(0, "127.0.0.1")
portInput.insert(0, "9999")


statusText = Label(frame_start, text="")
statusText.pack(pady=10)
# frame_start.pack(fill='both', expand=True)

def connect_server(address, port):
    global client
    # address = str(address)
    # port = str(port)
    if address != "" and port != "":
        if int(port) >= 0 and int(port) <= 65535:  
            statusText.configure(text="")
            gameStartBtn.configure(state="disabled")
            sleep(1)
            client = Client(address, port)
        else:
            messagebox.showwarning("포트가 올바르지 않습니다", "포트가 올바르지 않습니다")
    else:
        messagebox.showwarning("주소나 포트가 올바르지 않습니다", "주소나 포트가 올바르지 않습니다")


# ==============================

#
# Frame_game section
#

# ==============================


frame_game = Canvas(root, width=860, height=860)
frame_game.create_image(430, 430, image=bg)
# Label(frame_game, image=bg).pack(fill='both')

pieces_image = {
    "bishop-black": PhotoImage(file=f"img/bishop-black.png"),
    "bishop-white": PhotoImage(file=f"img/bishop-white.png"),
    "king-black": PhotoImage(file=f"img/king-black.png"),
    "king-white": PhotoImage(file=f"img/king-white.png"),
    "knight-black": PhotoImage(file=f"img/knight-black.png"),
    "knight-white": PhotoImage(file=f"img/knight-white.png"),
    "pawn-black": PhotoImage(file=f"img/pawn-black.png"),
    "pawn-white": PhotoImage(file=f"img/pawn-white.png"),
    "queen-black": PhotoImage(file=f"img/queen-black.png"),
    "queen-white": PhotoImage(file=f"img/queen-white.png"),
    "rook-black": PhotoImage(file=f"img/rook-black.png"),
    "rook-white": PhotoImage(file=f"img/rook-white.png"),
    "range-effect": PhotoImage(file=f"img/range-effect.png"),
}




class Client:
    count = 0

    # 0은 default
    # 1은 게임 시작 신호


    status = 0
    def __init__(self, host, port):
        global client
        Client.count = 0
        
        # HOST = '127.0.0.1'  # 서버 IP를 입력하세요
        # PORT = 9999

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # 성공적으로 연결될 때까지 계속 시도
        
        while True:
            if Client.count > 4:
                statusText.configure(text="연결에 실패했습니다")
                gameStartBtn.configure(state="normal")
                del client
                return
            
            try:
                self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.client_socket.connect((host, int(port)))

                self.receive_thread = threading.Thread(target=self.recv_data, args=(self.client_socket,))
                self.receive_thread.daemon = True
                self.receive_thread.start()
                break
            except socket.error as e:
                # statusText.configure(text="연결 시도 횟수: , 2초 후 재시도... ")
                Client.count += 1
                sleep(2)
            
            sleep(0.3)


        

        # start_new_thread(self.recv_data, (self.client_socket,))
        print('>> 서버에 연결됨')
        self.send_data()

    def send_data(self, json = ""):

        global process
        try:
            if json == "":
                dict = {"status": "data_request"}
                if Client.status == 1:
                    process = Game()
                    dict["status"] = "ready"
                    Client.status = 2
                    # print("test", interface_status)

                
                elif Client.status == 2:
                    pass
            else:
                dict = json

            dict = str(dict).encode()
            self.client_socket.send(dict)
        except socket.error as e:
            print("메시지 전송 중 소켓 에러:", e)
            self.client_socket.close()
        
        sleep(0.3)
        # 메인 루프 탈출 시 소켓 닫기


                
    def recv_data(self, client_socket):

        global interface_status, current_turn_team, user
        while True:
            try:
                data = client_socket.recv(1024)

                # data["status"] 
                if not data:
                    break
                
                data = literal_eval(data.decode())

                # 사람이 2명 모여 게임이 시작했을 경우
                
                if data["status"] == "start" and Client.status < 1:
                    Client.status = 1 # 게임 시작 신호 전송
                    interface_status = 2 # 게임 시작 레이아웃으로 변경

                    frame_start.place_forget()
                    frame_game.place(x=0, y=0, width=860, height=860)

                    
                    user["team"] = data['team'] # 다룰 기물의 색을 랜덤으로 결정
                    current_turn_team = data['turn']
                    print(user)
                    self.send_data()

                print('data["status"]', data["status"])
                    
                if data["status"] == "in_progress":
                    x, y = data['moveOrigin']
                    x2, y2 = data['moved']
                    current_turn_team = user['team']
                    moved_piece = Game.gameArea[x][y]
                    if moved_piece != 0:
                        moved_piece.receive_move(x=x2, y=y2)
                
                if data["status"] == "finished":
                    
                    x, y = data['moveOrigin']
                    x2, y2 = data['moved']
                    current_turn_team = user['team']
                    moved_piece = Game.gameArea[x][y]

                    
                    if moved_piece != 0:
                        moved_piece.receive_move(x=x2, y=y2)
                   
                    

                    if user['team'] == data['winner']:
                        Label(root, text="승리", font=("Pretendard", 15)).pack(side="top", padx="15")
                    else:
                        Label(root, text="패배", font=("Pretendard", 15)).pack(side="top")
                    
                    break
                # print(repr(data.decode()))
            except socket.error as e:
                print("소켓 에러:", e)
                break
            
            sleep(0.3)

        client_socket.close()        
        print('연결 종료')
        exit()


    # 유저가 준 JSON 코드를 실제 서버에 반영
    def decode(self, ): 
        ...


class Game:
    turn_team = "white"
    history = []

    start = 0
    gameArea = [
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0]
    ]


    # def locationSet(self, team):
    #     if team == "white":
    #         return
    #     return

    

    def setArea(self, obj: "Pieces") -> None:
        global frame_game 
        Game.gameArea[obj.x][obj.y] = obj
        
        
        frame_game.create_image(obj.x * 100 + 80, obj.y * 100 + 80, image=pieces_image[f"{obj.pieceType}-{obj.team}"], tag=(f"{obj.id}", "pieces"))
   
    # def print_gameArea(self):
        
    def __init__(self):
        self.create()
    def create(self):
        frame_game.delete("pieces")
        
        self.setArea(Rook('black', 7, 0))
        self.setArea(Rook('black', 0, 0))

        self.setArea(Knight('black', 1, 0))
        self.setArea(Knight('black', 6, 0))

        self.setArea(Bishop('black', 2, 0))
        self.setArea(Bishop('black', 5, 0))

        self.setArea(King('black', 3, 0))
        self.setArea(Queen('black', 4, 0))



        self.setArea(Rook('white', 0, 7))
        self.setArea(Rook('white', 7, 7))

        self.setArea(Knight('white', 1, 7))
        self.setArea(Knight('white', 6, 7))

        self.setArea(Bishop('white', 2, 7))
        self.setArea(Bishop('white', 5, 7))

        self.setArea(King('white', 3, 7))
        self.setArea(Queen('white', 4, 7))

        for i in range(8):
            self.setArea(Pawn('black', i, 1))
            self.setArea(Pawn('white', i, 6))

        # for i in Game.gameArea:
        #     i = i.reverse()
    def event_bind(self):
        def mouse_move(e) :
            global mouse_x, mouse_y
            mouse_x = e.x
            mouse_y = e.y
        def mouse_press(e):
            global mouse_pieces_selected, current_selected_pieces, interface_status


            if interface_status >= 2:
                frame_game.delete("RANGE_EFFECT")

                if 30 <= mouse_x and mouse_x < 30 + 100 * 8 and 30 <= mouse_y and mouse_y < 30 + 100 * 8:
                    selected_pieces = Game.gameArea[cursor_x][cursor_y]

                    

                    # 이전에 선택된 기물이 없고 선택된 기물과 유저의 팀이 다를 경우
                    if current_selected_pieces == 0 and selected_pieces != 0 and selected_pieces.team != user["team"]:
                        return
                    
                    
                    # 만약 클릭한 기물과 예전에 클릭했던 기물이 있고, 같은 기물과 예전 기물의 팀이 같을 경우
                    if selected_pieces != 0 and \
                        current_selected_pieces != 0 and \
                        selected_pieces.team == current_selected_pieces.team:
                        # 예전에 기록했던 기물의 기록을 지운다
                        current_selected_pieces = 0 
                        
                    # 선택한 기물이 이동할 떄
                    if current_selected_pieces != 0 and \
                        (selected_pieces == 0 or selected_pieces != 0 and selected_pieces.team != current_selected_pieces.team):
                            final_moveRangeArr = Pieces.get_valid_moves(self, current_selected_pieces)
                    else:
                        final_moveRangeArr = Pieces.get_valid_moves(self, selected_pieces)
                        
                    if [cursor_x, cursor_y] in final_moveRangeArr:

                        # 유저의 팀이랑 현재 턴을 가진 팀이랑 다를 경우 동작을 거부한다
                        if current_turn_team != user["team"]:
                            return
                        # 특정 기물을 클릭한 후, 다른 팀의 기물을 클릭하거나 아무 것도 없는 곳을 클릭했을 경우
                        if current_selected_pieces != 0 and (selected_pieces == 0 or selected_pieces.team != current_selected_pieces.team):
                            current_selected_pieces.move(x=cursor_x, y=cursor_y)
                            current_selected_pieces = 0
                            return
                        
                    # 특정 기물을 클릭했을 경우
                    if selected_pieces != 0 and current_selected_pieces == 0:
                        for i in final_moveRangeArr:
                            # 범위 표시
                            frame_game.create_image(i[0] * 100 + 80, i[1] * 100 + 80, image=pieces_image["range-effect"], tag="RANGE_EFFECT")   
                    
                    current_selected_pieces = selected_pieces


        root.bind("<Motion>", mouse_move)           # 마우스 이동 시 실행할 함수 지정
        root.bind("<ButtonPress>", mouse_press)     # 마우스 포인터 클릭 시 실행할 함수 지정

    def getHistory(self):
        for historyItem in Game.history:
            print(f"{historyItem}")

    def processing(self):
        global index, timer, score, hisc, difficulty, tsugi
        global cursor_x, cursor_y, interface_status, mouse_x, mouse_y, interface_status

        # if interface_status == 2:

        #     frame_game.place(x=0, y=0, width=860, height=860)
        # print("interface_status", interface_status)

        frame_game.create_image(cursor_x * 72 + 60, cursor_y * 72 + 60, image=cursor, tag="CURSOR")


        if 30 <= mouse_x and mouse_x < 30 + 100 * 8 and 30 <= mouse_y and mouse_y < 30 + 100 * 8:
            cursor_x = int((mouse_x - 30) / 100) 
            cursor_y = int((mouse_y - 30) / 100) 
            # if mouse_click == 1:
            #     frame_game.create_image(cursor_x * 100 + 80, cursor_y * 100 + 80, image=PhotoImage(file=f"img/bishop-black.png"))
            #     print("test3")
            #     mouse_click = 0
            
                # mouse_c = 0
                # set_neko()
                # neko[cursor_y][cursor_x] = tsugi
                # tsugi = 0
                # index = 2
                
            frame_game.delete("CURSOR")
            frame_game.create_image(cursor_x * 100 + 80, cursor_y * 100 + 80, image=cursor, tag="CURSOR")
        else:
            frame_game.delete("CURSOR")
        
        root.after(10, self.processing)


class Pieces:
    def __init__(self, team, x, y):
        

        self.id = randomUUID()
        self.team = team
        self.x = x
        self.y = y
        self.pieceType = ""
        self.moveRangeArr = None

        if user['team'] == "black":
            reverse = list(reversed([0, 1, 2, 3, 4, 5, 6, 7]))
            self.y = reverse[self.y]
    # @property
    # def moveRange(self) -> list:
    #     array = []
    #     if str(type(self.moveRangeArr)) == "<class 'list'>":
    #         for moveRange in self.moveRangeArr:
    #             array.append([self.x + moveRange[0], self.y + moveRange[1]])
    #         return array 
    #     else:
    #         pass
        
        # if str(type(self.moveRangeArr)) == "<class 'int'>":
        #     for moveRange in self.moveRangeArr:
        #         array.append([self.x + moveRange[0], self.y + moveRange[1]])
        #     return array 

    def get_valid_moves(self, piece):
        moveRangeArr = piece.moveRangeArr.copy()
        valid_moves = []

        pieceType = piece.pieceType
        directions = []

        if pieceType == "rook":
            directions = [[0, 1], [1, 0], [0, -1], [-1, 0]]
        elif pieceType == "queen":
            directions = [[0, 1], [1, 0], [0, -1], [-1, 0], [1, 1], [-1, -1], [-1, 1], [1, -1]]
        elif pieceType == "bishop":
            directions = [[1, 1], [-1, -1], [-1, 1], [1, -1]]


        if pieceType in ["rook", "queen", "bishop"]:
            for direction in directions:
                for i in range(1, 8):
                    x = piece.x + direction[0] * i
                    y = piece.y + direction[1] * i
                    if x < 0 or x > 7 or y < 0 or y > 7:
                        break
                    moveRangeItem = Game.gameArea[x][y]
                    if moveRangeItem == 0:
                        valid_moves.append([x, y])
                    elif moveRangeItem.team != piece.team:
                        valid_moves.append([x, y])
                        break
                    else:
                        break
        else:
            if pieceType == "pawn":
                if Game.gameArea[piece.x][piece.y - 1] != 0:
                    moveRangeArr.remove([0, -1])
                    if piece.notMove == True:
                        moveRangeArr.remove([0, -2])

                for attackRange in piece.attackRangeArr:
                    
                    x2 = piece.x + attackRange[0]
                    y2 = piece.y + attackRange[1]

                    if x2 < 0 or x2 > 7 or y2 < 0 or y2 > 7:
                        continue
                    attackRangeItem = Game.gameArea[x2][y2]
                    
                    # 대각선 옆에 상대방 기물이 있을 경우 범위 추가
                    if attackRangeItem != 0 and attackRangeItem.team != piece.team:
                        valid_moves.append([x2, y2])


            for move in moveRangeArr:
                x = piece.x + move[0]
                y = piece.y + move[1]
                if x < 0 or x > 7 or y < 0 or y > 7:
                    continue
                moveRangeItem = Game.gameArea[x][y]
                
                        
                
                if moveRangeItem == 0 or moveRangeItem.team != piece.team:
                    valid_moves.append([x, y])

        return valid_moves



    def exists(self, team, x, y):
        classObj = Game.gameArea[x][y]
        if classObj.team == 0: # 아무도 없을떄
            return "empty"
        elif classObj.team != team: # 적일떄
            return "enemy"
        elif classObj.team == team: # 아군일떄
            return "ally"
# send_data
    def move(self, x, y):
        global current_turn_team
        if [x, y] in self.get_valid_moves(Game.gameArea[self.x][self.y]):
            moveOrigin = [self.x, self.y]
            moved = [x, y]
            killPieces = None
            
            if self.pieceType == "pawn":
                if self.notMove == True:
                    self.notMove = False
                    self.moveRangeArr.remove([0, -2])

                if y == -7:
                    self.promotion(x, y)

                
            frame_game.delete(self.id)

            

            if Game.gameArea[x][y] != 0:
                frame_game.delete(Game.gameArea[x][y].id)
                killPieces = Game.gameArea[x][y]

            Game.gameArea[x][y] = Game.gameArea[self.x][self.y]
            Game.gameArea[self.x][self.y] = 0

            
            self.x = x
            self.y = y
            sound_effect.play()
            frame_game.create_image(x * 100 + 80, y * 100 + 80, image=pieces_image[f"{self.pieceType}-{self.team}"], tag=f"{self.id}")

            json = {
                "status": "in_progress",
                "pieces": self.pieceType, 
                "killedPiece": killPieces.pieceType if killPieces != None else killPieces,
                "team": user['team'], 
                "moveOrigin": moveOrigin,
                "moved": moved
            }

            client.send_data(json)
            current_turn_team = toggle_color(user['team'])
            # if user["team"] != 

        # 현재 계획
        # 만약 moveRange 하나만 존재한다면 그게 이동 & 공격 가능 범위라고 인식하기
        # 만약 attackRange 가 따로 존재한다면 공격 범위랑 이동 범위가 따로 있다고 가정하고 if문 세분화

    def receive_move(self, x, y):
        frame_game.delete(self.id)

        if Game.gameArea[x][y] != 0:
            frame_game.delete(Game.gameArea[x][y].id)

        Game.gameArea[x][y] = Game.gameArea[self.x][self.y]
        Game.gameArea[self.x][self.y] = 0


        self.x = x
        self.y = y
        sound_effect.play()
        frame_game.create_image(x * 100 + 80, y * 100 + 80, image=pieces_image[f"{self.pieceType}-{self.team}"], tag=f"{self.id}")
    
    def promotion(self, x, y):
        
        def click_event(e):
            print(e)

        promotion_display = Frame(root, relief='solid')
        promotion_display.place(x=x, y=y, width=120*5, height=120)
        
        Queen = Label(root, width=100, height=100, overrelief="solid", image=pieces_image[f"queen-{user['team']}"])
        Rook = Label(root, width=100, height=100, overrelief="solid", image=pieces_image[f"rook-{user['team']}"])
        Bishop = Label(root, width=100, height=100, overrelief="solid", image=pieces_image[f"bishop-{user['team']}"])
        Knight = Label(root, width=100, height=100, overrelief="solid", image=pieces_image[f"knight-{user['team']}"])

        Queen.pack(side=LEFT, padx=10, pady=10)
        Rook.pack(side=LEFT, padx=10, pady=10)
        Bishop.pack(side=LEFT, padx=10, pady=10)
        Knight.pack(side=LEFT, padx=10, pady=10)

        Queen.bind("<ButtonPress>", click_event)
        Rook.bind("<ButtonPress>", click_event)
        Bishop.bind("<ButtonPress>", click_event)
        Knight.bind("<ButtonPress>", click_event)

        print('test')

# gameStartBtn = Button(frame_start, text="게임 시작", command= lambda: connect_server(addressInput.get(), portInput.get()))


def toggle_color(current_color):
    return "white" if current_color == "black" else "black"



class Rook(Pieces):
    def __init__(self, team, x, y):
        super().__init__(team, x, y)
        self.pieceType = "rook"
        self.moveRangeArr = [
            [0, 1], [0, 2], [0, 3], [0, 4], [0, 5], [0, 6], [0, 7],
            [1, 0], [2, 0], [3, 0], [4, 0], [5, 0], [6, 0], [7, 0],
            
            [0, -1], [0, -2], [0, -3], [0, -4], [0, -5], [0, -6], [0, -7],
            [-1, 0], [-2, 0], [-3, 0], [-4, 0], [-5, 0], [-6, 0], [-7, 0],
        ]
    
# class Knight():
#     def __init__(self, team):
#         randid = randomUUID()
#         piecelist.append({randid: {"team":team, "class":"knight"}})
#         self.gameArea[y][x] = randid


class Knight(Pieces):
    def __init__(self, team, x, y):
        super().__init__(team, x, y)
        self.pieceType = "knight"
        self.moveRangeArr = [
            [-2, -1], [-1, -2], [1, -2], [2, -1], 
            [-2, 1], [-1, 2], [1, 2], [2, 1]
        ]
        # return ({"id": randomUUID(), "team":team, "class":"knight"})
    
class Bishop(Pieces):
    def __init__(self, team, x, y):
        super().__init__(team, x, y)
        self.pieceType = "bishop"
        self.moveRangeArr = [
            [1, 1], [2, 2], [3, 3], [4, 4], [5, 5], [6, 6], [7, 7], 
            [-1, -1], [-2, -2], [-3, -3], [-4, -4], [-5, -5], [-6, -6], [-7, -7], 
            [1, -1], [2, -2], [3, -3], [4, -4], [5, -5], [6, -6], [7, -7], 
            [-1, 1], [-2, 2], [-3, 3], [-4, 4], [-5, 5], [-6, 6], [-7, 7], 
        ]

    # @property
    # def diagonalMove():
        
    #     pass


class Queen(Pieces):
    def __init__(self, team, x, y):
        super().__init__(team, x, y)
        self.pieceType = "queen"
        
        self.moveRangeArr = [
            [1, 1], [2, 2], [3, 3], [4, 4], [5, 5], [6, 6], [7, 7], 
            [-1, -1], [-2, -2], [-3, -3], [-4, -4], [-5, -5], [-6, -6], [-7, -7], 
            [1, -1], [2, -2], [3, -3], [4, -4], [5, -5], [6, -6], [7, -7], 
            [-1, 1], [-2, 2], [-3, 3], [-4, 4], [-5, 5], [-6, 6], [-7, 7], 
            [0, 1], [0, 2], [0, 3], [0, 4], [0, 5], [0, 6], [0, 7], 
            [0, -1], [0, -2], [0, -3], [0, -4], [0, -5], [0, -6], [0, -7], 
            [1, 0], [2, 0], [3, 0], [4, 0], [5, 0], [6, 0], [7, 0], 
            [-1, 0], [-2, 0], [-3, 0], [-4, 0], [-5, 0], [-6, 0], [-7, 0], 
        ]
    

class King(Pieces):
    def __init__(self, team, x, y):
        super().__init__(team, x, y)
        self.pieceType = "king"

        
        self.moveRangeArr = [
            [1, 0], [1, -1], [1, 1],
            [0, -1], [0, 1],
            [-1, 0], [-1, -1], [-1, 1],
        ]

class Pawn(Pieces):
    def __init__(self, team, x, y):
        super().__init__(team, x, y)
        self.pieceType = "pawn"

        self.notMove = True
        self.moveRangeArr = [[0, -1], self.firstmove]
        self.attackRangeArr = [[-1, -1], [1, -1]]
    @property
    def firstmove(self):
        if self.notMove:
            return [0, -2]
        


process = Game() # 게임 프로세스
process.event_bind()






# cvs.create_rectangle(660, 100, 840, 160, fill="white")
# cvs.create_text(750, 130, text="테스트", fill="red", \
# font=("Times New Roman", 30))


# cvs.create_image(433, 433, image = bg)

process.processing()
root.mainloop()