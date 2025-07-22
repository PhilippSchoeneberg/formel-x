import sqlite3

class Database:
    def __init__(self, db_path="formulaX.db"):
        self.connection = sqlite3.connect(db_path)
        self.cursor = self.connection.cursor()

    def get_all_categories(self):
        self.cursor.execute("SELECT id, name, date FROM categories")
        rows = self.cursor.fetchall()

        category_dict = {
            row[0]: {
                "name": row[1],
                "date": row[2],
            }
            for row in rows
        }

        return category_dict


    def get_all_compounds(self):
        self.cursor.execute("SELECT id, correct_name, wrong_name1, wrong_name2, correct_formula, wrong_formula1, wrong_formula2, category_id, date FROM compounds")
        rows = self.cursor.fetchall()

        compound_dict = {
            row[0]: {
                "correct_name": row[1],
                "wrong_name1": row[2],
                "wrong_name2": row[3],
                "correct_formula": row[4],
                "wrong_formula1": row[5],
                "wrong_formula2": row[6],
                "category": row[7],
                "date": row[8],
            }
            for row in rows
        }

        return compound_dict


    def get_all_questions(self):
        self.cursor.execute("SELECT id, question, correct_answer, wrong_answer1, wrong_answer2, wrong_answer3, wrong_answer4, date FROM questions")
        rows = self.cursor.fetchall()

        question_dict = {
            row[0]: {
                "question": row[1],
                "correct_answer": row[2],
                "wrong_answer1": row[3],
                "wrong_answer2": row[4],
                "wrong_answer3": row[5],
                "wrong_answer4": row[6],
                "date": row[7],
            }
            for row in rows
        }

        return question_dict


    def close(self):
        self.connection.close()