import numpy as np
import random
import json
import tensorflow as tf


class Game:


    def __init__(self):
        #בניית לוח
        self.board = np.zeros((6,7))
        #בניית רשימה של המקומות הכי נמוכים בלוח
        self.lowest_place = [0, 0, 0, 0, 0, 0, 0]
        #הגדרת ערכי השחקנים
        self.agent = 1
        self.player = -1
        # רשימה של כל הלוחות שהיו במשחק מסוים מתחילתו ועד סופו
        self.all_boards = []
        # תכונות הנקודות של מצבי הסוכן
        self.winPointsAgent = 1
        self.losePointsAgent = 0
        self.drawPointsAgent = 0.5
        # גאמא הוא פרמטר למידה אשר משקף את המרחק של הלוח מהלוח הסופי
        self.gamma = 0.9
        # רשימה שתורכב מטאפלים שיכילו את הסטרינג של הלוח ואת הניקוד, בעבור משחק בודד
        self.boards_points = list()
        #מילון התוצאות
        self.first_dict = {}
        #משתנה אלפא שתפקידו הוא לייצג את האחוז פעמים שמשחקים סוכן חכם
        self.alpha = 0.8
        #האם אנחנו מאמנים את המילון בפעם הראשונה או שלא
        self.firstTime = False
        if not self.firstTime:
            # שמירת המילון של הלוח הראשון
            with open('results_game.json', 'r') as f:
                self.first_dict = json.load(f)
        # with open('results_game.json', 'r') as f:
        #     self.first_dict = json.load(f)
        # self.model = tf.keras.models.load_model("modelCnn5.keras")


    def restart_game(self):
        #מאפס את המשחק
        self.board = np.zeros((6, 7))
        self.lowest_place = [0, 0, 0, 0, 0, 0, 0]

        self.all_boards.clear()
        self.boards_points.clear()


    def check_win(self):
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
        #פעולה המחזירה אמת אם יש תיקו ושקר אחרת

        for l in self.lowest_place:
            if (l < 6):
                return False

        return True


    def agentTurn(self):
        #מגרילה תא מתוך התאים הפנויים שניתן להכניס לתוכם בלוח ומציבה את הערך 1 המסמן את הסוכן

        num = random.randint(0,6)
        while self.lowest_place[num] == 6:
            num = random.randint(0, 6)
        col = num
        row = self.lowest_place[num]
        self.board[5-row, col] = 1
        self.lowest_place[num] += 1


    def printBoard(self):
        """
        מדפיסה את הלוח הנוכחי של המשחק בצורה קריאה.
        מספרת את העמודות ומציינת שחקנים (1: סוכן, -1: שחקן, 0: ריק).
        """
        print("\n  0 1 2 3 4 5 6")  # כותרות עמודות
        print("  -------------")  # קו הפרדה
        for r_idx, row in enumerate(self.board):
            row_str = []
            for cell in row:
                if cell == 1:
                    row_str.append('X')  # סוכן
                elif cell == -1:
                    row_str.append('O')  # שחקן
                else:
                    row_str.append('.')  # ריק
            print(f"{5 - r_idx}|{' '.join(row_str)}")  # שורות הלוח (הפוך כדי שהשורה התחתונה תהיה 0)
        print("  -------------")  # קו הפרדה תחתון


    def playerTurn(self):
        #מגרילה תא מתוך התאים הפנויים שניתן להכניס לתוכם בלוח ומציבה את הערך 1- המסמן את השחקן

        num = random.randint(0, 6)
        while self.lowest_place[num] == 6:
            num = random.randint(0, 6)
        col = num
        row = self.lowest_place[num]
        self.board[5-row, col] = -1
        self.lowest_place[num] += 1


    def smartAgentTurn(self):

        best_score = -float('inf')  # משתנה מניקוד מינמלי לניקוד המקסימלי
        best_move = None  # תא לשמור את המהלך הטוב ביותר

        all = 0 #מספר המהלכים שנספר עד כה
        in_dict = 0 #כמה קיימים במילון


        # נבדוק כל מהלך אפשרי
        for col in range(7):
            row = self.lowest_place[col]

            if row == 6:
                continue

            all += 1

            # נציב את המהלך בלוח הקיים
            self.board[5 - row, col] = self.agent

            # נהפוך את הלוח הנוכחי למחרוזת
            board_str = ''.join(map(str, (2 if cell == -1 else int(cell) for cell in self.board.flatten())))

            if board_str in self.first_dict:
                in_dict += 1

                # בדיקת ניקוד הלוח במילון
                score = self.first_dict[board_str][0]  # ברירת מחדל לניקוד 0


                 # אם מצאנו ניקוד טוב יותר, נעדכן את המהלך הטוב ביותר
                if score > best_score:
                    best_score = score
                    best_move = (5 - row, col)

            # החזרת התא למצבו המקורי
            self.board[5 - row, col] = 0

        # אם מצאנו מהלך טוב, נבצע אותו
        if best_move and in_dict >= all/2:
            row, col = best_move
            self.board[row, col] = self.agent
            self.lowest_place[col] += 1
        else:
            self.agentTurn()


    def smartAgentCnn(self):

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
            board_input = temp_board.reshape((1, 6, 7, 1)).astype(np.float32)
            print(board_input)
            print(board_input.shape)
            score = self.model.predict(board_input)[0][0]
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
            self.board[row][col] = self.agent
            self.lowest_place[col] += 1


    def board_string(self):
        # ממיר את הלוח למחרוזת בת 42 תווים ללא רווחים

        result = ''.join(str(int(2 if cell == -1 else cell)) for row in self.board for cell in row)
        return result


    def calculatingPoints(self):
        #חישוב נקודות ללוח במשחק

        pointsVal = 0

        # הגדרת ערך הנקודות בהתאם למצב המשחק
        if self.check_win() == 1:
            pointsVal = self.winPointsAgent
        elif self.check_win() == -1:
            pointsVal = self.losePointsAgent
        elif self.tie():
            pointsVal = self.drawPointsAgent
        num = pointsVal
        self.all_boards.reverse()

        # הוספת הנקודות לכל לוח
        for board_str in self.all_boards:
            self.boards_points.append((board_str, num))
            num *= self.gamma  # עדכון הניקוד בהתאם לגאמא

        self.boards_points.reverse()
        self.all_boards.clear()

        # הדפסת הניקוד
        ###################
        #for n in self.boards_points:
        #    print(n)
        ###############################


    def updateDictionary(self):
        # הפעולה מעדכנת את המילון על פי התוצאות במשחק האחרון

        for key, points in self.boards_points:
            if key in self.first_dict:
                old_score, count = self.first_dict[key]
                new_avg = (old_score * count + points) / (count + 1)
                self.first_dict[key] = (new_avg, count + 1)
            else:
                self.first_dict[key] = (points, 1)

            ###############################################
            # print(f"Updated board: {key}, Points: {points}")
            ###########################################

        #############################################################
        # print(f"Current dictionary size: {len(self.dict_of_games)}")
        ##########################################################

        self.boards_points.clear()
        self.all_boards.clear()


    def PlayOneGame(self):
        #מבצעת משחק שלם המורכב מתור הסוכן והשחקן לסירוגין, אחרי כל תור יודפס הלוח.לבסוף הפעולה תדפיס את הלוח ואת המנצח

        self.restart_game()

        ##################
        self.printBoard()
        ##################
        # לאורך כל הפעולה, צמד השורות הבא ממיר את הלוח כל פעם למחרוזת ולאחר מכן מוסיף את המחרוזת אל הרשימה
        board_str = self.board_string()
        self.all_boards.append(board_str)

        while (self.check_win() == 0 and self.tie() == False):
            # עושים תנאי שעושה 80 אחוז שייבחר סוכן חכם ולא סוכן רנדומלי
            if random.uniform(0, 1) <= self.alpha and not self.firstTime:
                self.smartAgentTurn()
            else:
                self.agentTurn()
            ####################
            self.printBoard()
            ####################
            board_str = self.board_string()
            #print(board_str)
            self.all_boards.append(board_str)
            if (self.check_win() == 0 and self.tie() == False):
                self.playerTurn()
                ###################
                self.printBoard()
                ###################
                board_str = self.board_string()
                self.all_boards.append(board_str)
            if self.check_win() == 1 :
                 print("The agent won !!!!!")
            else:
                    if self.check_win() == -1 :
                        print("The player won !!!!!")
                    else:
                        if self.tie() == True:
                            print("DRAW, no one won !")

            # מימוש פעולה שמחשבת את הנקודות לכל לוח במשחק
        self.calculatingPoints()


    def PlayOneGameRandomAgaintsCnn(self):
        #מבצעת משחק שלם המורכב מתור הסוכן והשחקן לסירוגין, אחרי כל תור יודפס הלוח.לבסוף הפעולה תדפיס את הלוח ואת המנצח

        self.restart_game()

        ##################
        #self.printBoard()
        ##################
        # לאורך כל הפעולה, צמד השורות הבא ממיר את הלוח כל פעם למחרוזת ולאחר מכן מוסיף את המחרוזת אל הרשימה
        board_str = self.board_string()
        self.all_boards.append(board_str)

        while (self.check_win() == 0 and self.tie() == False):
            self.smartAgentCnn()
            ####################
            #self.printBoard()
            ####################
            board_str = self.board_string()
            print(board_str)
            self.all_boards.append(board_str)
            if (self.check_win() == 0 and self.tie() == False):
                self.playerTurn()
                ###################
                #self.printBoard()
                ###################
                board_str = self.board_string()
                self.all_boards.append(board_str)
            # if self.check_win() == 1 :
            #      print("The agent won !!!!!")
            # else:
            #         if self.check_win() == -1 :
            #             print("The player won !!!!!")
            #         else:
            #             if self.tie() == True:
            #                 print("DRAW, no one won !")

            # מימוש פעולה שמחשבת את הנקודות לכל לוח במשחק
        self.calculatingPoints()


# shons_game = Game()
# shons_game.PlayOneGameRandomAgaintsCnn()


class Games:

    def __init__(self):
        self.num_games = 3200000
        self.num_games_smart = 100
        self.game = Game()


    def run_games(self):
        # הפעולה מריצה רצף משחקי איקס עיגול, מאכסנת את הלוחות עם ערך של ניקוד וכמות בתוך הקובץ

        countWinPlayer = 0
        countWinAgent = 0
        countGames = 0


        for i in range(self.num_games):
            if i % 100 == 0:
                print(f"game number: {i}")
            self.game.PlayOneGame()

            score = self.game.check_win()
            if (score == 1):
                countWinAgent = countWinAgent + 1
            if (score == -1):
                countWinPlayer = countWinPlayer + 1
            countGames = countGames + 1

            # עדכון המילון המרכזי עם המילון של המשחק
            self.game.updateDictionary()

        self.save_dict_to_json()

        ahuzWinPlayer = (float)((countWinPlayer / countGames) * 100)
        ahuzWinAgent = (float)((countWinAgent / countGames) * 100)

        print("The player won ", ahuzWinPlayer, " percent of the time, the agent won ", ahuzWinAgent,
              " percent of the time.")


    def run_games_smart(self):
        # הפעולה מריצה רצף משחקי איקס עיגול, מאכסנת את הלוחות עם ערך של ניקוד וכמות בתוך הקובץ

        countWinPlayer = 0
        countWinAgent = 0
        countGames = 0


        for i in range(self.num_games_smart):
            # if i % 100 == 0:
            #     print(f"game number: {i}")
            self.game.PlayOneGameRandomAgaintsCnn()

            score = self.game.check_win()
            if (score == 1):
                countWinAgent = countWinAgent + 1
            if (score == -1):
                countWinPlayer = countWinPlayer + 1
            countGames = countGames + 1

            # עדכון המילון המרכזי עם המילון של המשחק
            # self.game.updateDictionary()

        # self.save_dict_to_json()

        ahuzWinPlayer = (float)((countWinPlayer / countGames) * 100)
        ahuzWinAgent = (float)((countWinAgent / countGames) * 100)

        print("The player won ", ahuzWinPlayer, " percent of the time, the agent won ", ahuzWinAgent,
              " percent of the time.")


    def save_dict_to_json(self):
        # שמירת המילון game_dict לקובץ JSON
        with open('results_game.json', 'w') as json_file:
            json.dump(self.game.first_dict, json_file, indent=4)  # שמירה עם הזחה לקריאה נוחה
        print("Game dictionary saved to 'results_game.json'.")


# games = Games()
# games.run_games_smart()


def print_dictionary_size_from_file(file_path='results_game.json'):
    """
    Loads a JSON dictionary from a specified file path
    and prints the number of entries (unique boards) in it.
    """
    with open(file_path, 'r') as f:
        data = json.load(f)
        print(f"Number of unique boards in '{file_path}': {len(data)}")


# print_dictionary_size_from_file()