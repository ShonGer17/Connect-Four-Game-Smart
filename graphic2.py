from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
import json
import numpy as np
import tensorflow as tf
import random
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.popup import Popup


class FirstScreen(FloatLayout):


    def __init__(self, **kwargs):
        super(FirstScreen, self).__init__(**kwargs)
        self.graphBoard = Board(self)
        self.addOn()
        self.addLabel()
        self.addButton()


    def addOn(self):
        self.graphBoard.size_hint = (.5, .5)
        self.graphBoard.pos_hint = {"center_x": .5, "center_y": .7}
        self.add_widget(self.graphBoard)


    def addLabel(self):
        self.turn = Label()
        self.turn.font_size = 30
        self.turn.color = '#00FF00'
        self.turn.text = "playing"
        self.turn.size_hint = (.2, .1)
        self.turn.pos_hint = {"center_x": .1, "center_y": .5}
        self.add_widget(self.turn)


    def addButton(self):
        self.buttonRestart = Button()
        self.buttonRestart.text = "refresh"
        self.buttonRestart.pos_hint = {"center_x": .1, "center_y": .2}
        self.buttonRestart.size_hint = (.2, .1)
        self.buttonRestart.bind(on_press=self.react)
        self.add_widget(self.buttonRestart)


    def react(self, touched):
        touched.text = "refresh"
        self.turn.text = "playing"
        self.graphBoard.start_game()
        self.parent.manager.current = 'title'


    def start_agent_turn(self, agent_type):
        self.graphBoard.start_agent_turn(agent_type)


class FirstScreenLayout(Screen):


    def __init__(self, **kwargs):
        super(FirstScreenLayout, self).__init__(**kwargs)
        self.layout = FirstScreen()
        self.add_widget(self.layout)


    def start_agent_turn(self, agent_type):
        self.layout.start_agent_turn(agent_type)


class Cell(Button):

    def __init__(self, row, col, parent_board):
        Button.__init__(self)
        self.text = "?"
        self.row = row
        self.col = col
        self.board = parent_board


    def on_press(self):
        if not self.board.check_win():
            answer = self.parent.check(self.row, self.col)
            if answer:
                self.text = "O"
                self.background_color = (1, 1, 0, 1)
                self.board.check_win()
                if not self.board.check_win():
                    self.parent.agentTurn()


class StartScreen(Screen):


    def __init__(self, **kwargs):
        super(StartScreen, self).__init__(**kwargs)
        self.add_title()
        self.add_buttons()


    def add_title(self):
        title_label = Label(text="Connect Four Game", font_size=50, color=(0, 1, 0, 1), bold=True, size_hint=(None, None), size=(600, 200), pos_hint={"center_x": 0.5, "center_y": 0.85}, halign="center", valign="middle")
        self.add_widget(title_label)


    def add_buttons(self):
        smart_agent_button = Button(text="Smart Agent", size_hint=(0.25, 0.25), pos_hint={"center_x": 0.2, "center_y": 0.5}, background_color=(0, 0, 0, 1), color=(0, 1, 0, 1))
        network_agent_button = Button(text="CNN Network", size_hint=(0.25, 0.25), pos_hint={"center_x": 0.5, "center_y": 0.5}, background_color=(0, 0, 0, 1), color=(0, 1, 0, 1))
        # random_agent_button = Button(text="Random", size_hint=(0.25, 0.25), pos_hint={"center_x": 0.5, "center_y": 0.8}, background_color=(0, 0, 0, 1), color=(0, 1, 0, 1))
        rules_button = Button(text="Rules", size_hint=(0.25, 0.25), pos_hint={"center_x": 0.8, "center_y": 0.5}, background_color=(0, 0, 0, 1), color=(0, 1, 0, 1))

        smart_agent_button.bind(on_release = lambda x : self.start_smart_agent())
        network_agent_button.bind(on_press = lambda x : self.start_network_agent())
        # random_agent_button.bind(on_press = lambda x : self.start_random_agent())
        rules_button.bind(on_release = lambda x : self.rules())

        self.add_widget(smart_agent_button)
        self.add_widget(network_agent_button)
        # self.add_widget(random_agent_button)
        self.add_widget(rules_button)


    def start_smart_agent(self):
        self.manager.current = 'game'
        self.manager.get_screen('game').start_agent_turn('smart')


    def start_network_agent(self):
        self.manager.current = 'game'
        self.manager.get_screen('game').start_agent_turn('network')


    # def start_random_agent(self):
    #     self.manager.current = 'game'
    #     self.manager.get_screen('game').start_agent_turn('random')


    def rules(self):
        self.rules_popup = BoxLayout(orientation='vertical', size_hint=(0.8, 0.8), pos_hint={"center_x": 0.5, "center_y": 0.5}, padding=[20, 20, 20, 20])
        rules_text = Label(text =""" 
Board Layout: 6 rows by 7 columns.
Objective: The first player to align 4 discs in a row (horizontal, vertical, or diagonal) wins.
Gameplay: 
• Players take turns dropping one disc per turn.
• Discs fall to the lowest available spot in the column.
• If a column is full, choose another.
• If all columns are full and no one wins, the game ends in a draw.
"""
                           , font_size = 20, color=(0, 0, 0, 1), halign='center', valign='middle', size_hint=(1,1))
        self.rules_popup.add_widget(rules_text)

        close_button = Button(text = "Back", size_hint_y=None, height=50, color=(0, 0, 0, 1))
        close_button.bind(on_release=self.hide_rules)
        self.rules_popup.add_widget(close_button)

        self.popup = Popup(title="Rules of the game", content=self.rules_popup, size_hint=(0.8, 0.8))
        self.popup.open()


    def hide_rules(self, instance):
        self.popup.dismiss()


class Board(GridLayout):

    def __init__(self, firstScreen):
        GridLayout.__init__(self)
        self.cols = 7
        self.listGraphBoard = []
        self.controller = Controller()
        self.addCellsToBoard()
        self.firstScreen = firstScreen


    def agentTurn(self):
        row, col = self.controller.agentTurn()
        self.listGraphBoard[row][col].text = "O"
        #תור הסוכן יהיה בצבע אדום
        self.listGraphBoard[row][col].background_color = (1, 0, 0, 1)
        self.check_win()


    def check_win(self):
        if self.controller.check_win() == 1:
            self.firstScreen.turn.text = "Agent Win!"
            return True
        elif self.controller.check_win() == -1:
            self.firstScreen.turn.text = "Player Win!"
            return True
        elif self.controller.tie():
            self.firstScreen.turn.text = "TIE!"
            return True
        return False


    def addCellsToBoard(self):
        for line in range(6):
            newLine = []
            for col in range(7):
                temp_cell = Cell(line, col, self)
                self.add_widget(temp_cell)
                newLine.append(temp_cell)
            self.listGraphBoard.append(newLine)


    def check(self, row, col):
        return self.controller.check(row, col)


    def start_game(self):
        self.controller.restart()
        for row in range(6):
            for col in range(7):
                self.listGraphBoard[row][col].text = "?"
                self.listGraphBoard[row][col].background_color = (1, 1, 1, 1)


    def start_agent_turn(self, agent_type):
        self.controller.start_agent_turn(agent_type)
        self.agentTurn()


class Controller():


    def __init__(self):
        self.logic = Logic()


    def check(self, row, col):
        return self.logic.check(row, col)


    def agentTurn(self):
        return self.logic.agentTurn()


    def check_win(self):
        return self.logic.check_win()


    def tie(self):
        return self.logic.tie()


    def restart(self):
        self.logic.restart()


    def start_game(self):
        self.logic.restart()
        return self.logic.agentTurn()


    def start_agent_turn(self, agent_type):
        self.logic.start_agent_turn(agent_type)


class Logic():


    def __init__(self):
        # 0 = empty, 1 = Red O = agent, -1 = Yellow O = player
        self.board = np.zeros((6,7))
        self.agent_type=''
        self.lowest_place = [0, 0, 0, 0, 0, 0, 0]
        self.data = {}
        file_path = 'results_game.json'
        with open(file_path, 'r') as file:
            self.data = json.load(file)
        self.model = tf.keras.models.load_model("modelCnn5.keras")


    def check(self, row, col):

        # בדיקה האם המהלך תקין
        if self.board[row][col] == 0 and self.lowest_place[col] == (5 - row):
            self.board[row][col] = -1
            self.lowest_place[col] += 1
            print(self.board)
            return True
        else:
            return False


    def agentTurn(self):
        if self.agent_type == "smart":
            return self.agentTurnDict()
        elif self.agent_type == "network":
            return self.agentTurnCnn()
        else:
            return self.agentTurnRandom()  # ברירת מחדל


    def start_agent_turn(self, agent_type):
        self.agent_type = agent_type


    def agentTurnRandom(self):
        #מגרילה תא מתוך התאים הפנויים שניתן להכניס לתוכם בלוח ומציבה את הערך 1 המסמן את הסוכן

        col = random.randint(0,6)
        while self.lowest_place[col] == 6:
            col = random.randint(0, 6)
        row = self.lowest_place[col]
        self.board[5-row, col] = 1
        self.lowest_place[col] += 1
        return 5-row, col


    def agentTurnDict(self):
        col = self.check_block(1)
        if col != -1:
            row = 5-self.lowest_place[col]
            self.board[row, col] = 1
            self.lowest_place[col] += 1
            return row, col

        col = self.check_block(-1)
        if col != -1:
            row = 5 - self.lowest_place[col]
            self.board[row, col] = 1
            self.lowest_place[col] += 1
            return row, col

        best_score = -float('inf')  # משתנה מניקוד מינמלי לניקוד המקסימלי
        best_move = None  # תא לשמור את המהלך הטוב ביותר


        # נבדוק כל מהלך אפשרי
        for col in range(7):
            row = self.lowest_place[col]

            if row == 6:
                continue

            # נציב את המהלך בלוח הקיים (שינויים במקום)
            self.board[5 - row, col] = 1

            # נהפוך את הלוח הנוכחי למחרוזת
            board_str = ''.join(map(str, (2 if cell == -1 else int(cell) for cell in self.board.flatten())))

            if board_str in self.data:

                # בדיקת ניקוד הלוח במילון
                score = self.data[board_str][0]  # ברירת מחדל לניקוד 0

                 # אם מצאנו ניקוד טוב יותר, נעדכן את המהלך הטוב ביותר
                if score > best_score:
                    best_score = score
                    best_move = (5 - row, col)

            # החזרת התא למצבו המקורי
            self.board[5 - row, col] = 0

        # אם מצאנו מהלך טוב, נבצע אותו
        if best_move:
            row, col = best_move
            self.board[row, col] = 1
            self.lowest_place[col] += 1
            print(self.board)
            return row, col
        else:
            print(self.board)
            return self.agentTurnRandom()


    def agentTurnCnn(self):

        best_score = -float('inf')  # משתנה מניקוד מינמלי לניקוד המקסימלי
        best_move = None  # תא לשמור את המהלך הטוב ביותר
        # נבדוק כל מהלך אפשרי
        for col in range(7):
            row = self.lowest_place[col]

            if row == 6:
                continue
        # נעתיק את הלוח הנוכחי כדי לא לפגוע בלוח המקורי
            temp_board = np.copy(self.board)  # יצירת עותק
            temp_board[5 - row][col] = 1  # עדכון הלוח עם המהלך החדש
            board_input = np.expand_dims(temp_board, axis=0)  # הוספת Batch Dimension בלבד
            print(board_input)
            print(board_input.shape)
            score = self.model.predict(board_input)
            print(f"({row},{col}), predict: {score}")
            # אם מצאנו ניקוד טוב יותר, נעדכן את המהלך הטוב ביותר
            if score > best_score:
                best_score = score
                best_move = (5 - row, col)
                print(best_move)
                print(best_score)
        print(best_move)
        # מבצעים את המהלך הטוב ביותר שמצאנו
        if best_move:
            row, col = best_move
            print(row)
            print(col)
            self.board[row][col] = 1
            self.lowest_place[col] += 1
            return row, col
        else:
            print("Warning: No valid move found for CNN agent. Board might be full or an unexpected state.")
            return self.agentTurnRandom()


    def check_win(self):
        # בודק מצב הלוח ומחזירה: 1 אם הסוכן ניצח, 1- אם השחקן ניצח ו0 אם המשחק לא הסתיים

        # בדיקת שורות
        for row in range(6):
            for col in range(4):
                segment = self.board[row, col:col + 4]
                if np.sum(segment) == 4:
                    return 1
                elif np.sum(segment) == -4:
                    return -1

        # בדיקת עמודות
        for row in range(3):
            for col in range(7):
                segment = self.board[row:row + 4, col]
                if np.sum(segment) == 4:
                    return 1
                elif np.sum(segment) == -4:
                    return -1

        # בדיקת אלכסונים יורדים
        for row in range(3):
            for col in range(4):
                diagonal = [self.board[row + i, col + i] for i in range(4)]
                if sum(diagonal) == 4:
                    return 1
                elif sum(diagonal) == -4:
                    return -1

        # בדיקת אלכסונים עולים
        for row in range(3, 6):
            for col in range(4):
                diagonal = [self.board[row - i, col + i] for i in range(4)]
                if sum(diagonal) == 4:
                    return 1
                elif sum(diagonal) == -4:
                    return -1

        # אם לא נמצא ניצחון
        return 0


    def tie(self):
        # מחזיר אמת אם יש תיקו, אחרת יחזיר שקר
        for l in self.lowest_place:
            if (l<6):
                return False
        return True


    def check_block(self, who_to_block):
        row, col = 0, 0

        for cell in range (7):
            board_copy = np.copy(self.board)
            col = cell
            row = self.lowest_place[col]
            if row == 6:
                continue
            self.board[5-row, col] = who_to_block
            if self.check_win() == who_to_block: # אם יהיה ניצחון אז נחזיר שהיה ניצחון
                self.board = np.copy(board_copy)
                return col
            self.board = np.copy(board_copy)

        return -1 # החזר שאין ניצחון


    def restart(self):
        self.board = np.zeros((6,7))
        self.lowest_place = [0, 0, 0, 0, 0, 0, 0]


class MyPaintApp(App):

    def build(self):
        sm = ScreenManager()
        sm.add_widget(StartScreen(name='title'))
        sm.add_widget(FirstScreenLayout(name='game'))
        return sm


MyPaintApp().run()
