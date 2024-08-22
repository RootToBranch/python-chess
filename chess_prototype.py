# 
# 체스 싱글 프로토타입
# - 턴 시스템 X
# - 검은색 기물 이동 불가
#
# 하얀색 기물 기준으로 모든 코드를 작성한 파일 


from tkinter import *
from randomId import randomUUID
import pygame




default_setting = {
    "x": 0,
    "y": 0,
    "width": 866,
    "height": 866
}


interface_status = 2 # 게임 레이아웃 관리
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


bg = PhotoImage(file="img/chess-board.png")
cursor = PhotoImage(file="img/cursor.png")

pygame.mixer.init()
sound_effect = pygame.mixer.Sound("./sounds/move-self.mp3")



frame3 = Frame(root, relief='solid')
frame_main = Frame(root, relief='solid')
frame_game = Canvas(root, width=860, height=860)


frame_game.create_image(430, 430, image=bg)
# Label(frame_game, image=bg).pack(fill='both')
frame_game.place(x=0, y=0, width=860, height=860)

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



class Server:
    def __init__(self):
        pass
    # 유저가 준 JSON 코드를 실제 서버에 반영
    def decode(self, ): 
        ...


class Game:
    history = []
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

    

    def setArea(self, x, y, obj):
        global frame_game 
        Game.gameArea[x][y] = obj
        frame_game.create_image(obj.x * 100 + 80, obj.y * 100 + 80, image=pieces_image[f"{obj.pieceType}-{obj.team}"], tag=f"{obj.id}")
    
    # def print_gameArea(self):
        
    def __init__(self):
        self.create()
    def create(self):
        self.setArea(0, 0, Rook('black', 0, 0))
        self.setArea(7, 0, Rook('black', 7, 0))

        self.setArea(1, 0, Knight('black', 1, 0))
        self.setArea(6, 0, Knight('black', 6, 0))

        self.setArea(2, 0, Bishop('black', 2, 0))
        self.setArea(5, 0, Bishop('black', 5, 0))

        self.setArea(3, 0, King('black', 3, 0))
        self.setArea(4, 0, Queen('black', 4, 0))



        self.setArea(0, 7, Rook('white', 0, 7))
        self.setArea(7, 7, Rook('white', 7, 7))

        self.setArea(1, 7, Knight('white', 1, 7))
        self.setArea(6, 7, Knight('white', 6, 7))

        self.setArea(2, 7, Bishop('white', 2, 7))
        self.setArea(5, 7, Bishop('white', 5, 7))

        self.setArea(3, 7, King('white', 3, 7))
        self.setArea(4, 7, Queen('white', 4, 7))

        for i in range(8):
            self.setArea(i, 1, Pawn('black', i, 1))
            self.setArea(i, 6, Pawn('white', i, 6))

        # for i in Game.gameArea:
        #     i = i.reverse()
    def event_bind(self):
        def mouse_move(e) :
            global mouse_x, mouse_y
            mouse_x = e.x
            mouse_y = e.y
        def mouse_press(e):
            global mouse_pieces_selected, current_selected_pieces

            frame_game.delete("RANGE_EFFECT")

            if 30 <= mouse_x and mouse_x < 30 + 100 * 8 and 30 <= mouse_y and mouse_y < 30 + 100 * 8:
                selected_pieces = Game.gameArea[cursor_x][cursor_y]
                
                
                # 만약 클릭한 기물과 예전에 클릭했던 기물이 있고, 같은 기물과 예전 기물의 팀이 같을 경우

                
                if selected_pieces != 0 and \
                    current_selected_pieces != 0 and \
                    selected_pieces.team == current_selected_pieces.team:
                    # 예전에 기록했던 기물의 기록을 지운다
                    current_selected_pieces = 0 
                    
                # 선택한 기물이 이동할 떄
                if current_selected_pieces != 0 and \
                    (selected_pieces == 0 or selected_pieces != 0 and selected_pieces.team != current_selected_pieces.team):
                        final_moveRangeArr = get_valid_moves(current_selected_pieces)
                else:
                    final_moveRangeArr = get_valid_moves(selected_pieces)
                    
                if [cursor_x, cursor_y] in final_moveRangeArr:
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
                





        def get_valid_moves( piece):

            # 배열 복사
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
                if pieceType == "pawn" and Game.gameArea[piece.x][piece.y - 1] != 0 and Game.gameArea[piece.x][piece.y - 1].team != piece.team:
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


        root.bind("<Motion>", mouse_move)           # 마우스 이동 시 실행할 함수 지정
        root.bind("<ButtonPress>", mouse_press)     # 마우스 포인터 클릭 시 실행할 함수 지정

    def getHistory(self):
        for historyItem in Game.history:
            print(f"{historyItem}")

    def processing(self):
        global index, timer, score, hisc, difficulty, tsugi
        global cursor_x, cursor_y, interface_status, mouse_x, mouse_y


        frame_game.create_image(cursor_x * 72 + 60, cursor_y * 72 + 60, image=cursor, tag="CURSOR")


        if interface_status >= 2:
            

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
            

        root.after(100, process.processing)


class Pieces:
    def __init__(self, team, x, y):


        self.id = randomUUID()
        self.team = team
        self.x = x
        self.y = y
        self.pieceType = ""
        self.diagonalMove = False
        self.moveRangeArr = None

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
            if pieceType == "pawn" and Game.gameArea[piece.x][piece.y - 1] != 0 and Game.gameArea[piece.x][piece.y - 1].team != piece.team:
                print(moveRangeArr)
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

    def move(self, x, y):
        if [x, y] in self.get_valid_moves(Game.gameArea[self.x][self.y]):

            # 만약 움직이지 않으면
            if self.pieceType == "pawn" and self.notMove == True:
                self.notMove = False
                self.moveRangeArr.remove([0, -2])

                
            frame_game.delete(self.id)
            
            # print("Game.gameArea[x][y] - 1")
            # print(Game.gameArea[x][y])
            # print("Game.gameArea[self.x][self.y] - 1")
            # print(Game.gameArea[self.x][self.y])


            if Game.gameArea[x][y] != 0:
                frame_game.delete(Game.gameArea[x][y].id)

            Game.gameArea[x][y] = Game.gameArea[self.x][self.y]
            Game.gameArea[self.x][self.y] = 0

            # print()
            # print("Game.gameArea[x][y] - 2")
            # print(Game.gameArea[x][y])
            # print("Game.gameArea[self.x][self.y] - 2")
            # print(Game.gameArea[self.x][self.y])


            self.x = x
            self.y = y
            sound_effect.play()
            frame_game.create_image(x * 100 + 80, y * 100 + 80, image=pieces_image[f"{self.pieceType}-{self.team}"], tag=f"{self.id}")



        # 현재 계획
        # 만약 moveRange 하나만 존재한다면 그게 이동 & 공격 가능 범위라고 인식하기
        # 만약 attackRange 가 따로 존재한다면 공격 범위랑 이동 범위가 따로 있다고 가정하고 if문 세분화

    # def moveable:
        


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
        self.id = randomUUID()
        self.team = team
        def moveRange(self):
            return
        self.x = x
        self.y = y
        self.pieceType = "king"

        
        self.moveRangeArr = [
            [1, 0], [1, -1], [1, 1],
            [0, -1], [0, 1],
            [-1, 0], [-1, -1], [-1, 1],
        ]

class Pawn(Pieces):
    def __init__(self, team, x, y):
        self.id = randomUUID()
        self.team = team
        self.x = x
        self.y = y
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
