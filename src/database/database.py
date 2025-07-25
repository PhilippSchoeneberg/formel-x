import datetime
import sqlite3

class Database:
    def __init__(self, db_path="src/database/formulaX.db"):
        self.connection = sqlite3.connect(db_path)
        self.cursor = self.connection.cursor()


    def fill_elements_table(self):
        with open("src/database/insert_elements.sql", "r", encoding="utf-8") as f:
            sql_script = f.read()
            self.cursor.executescript(sql_script)
        self.connection.commit()


    def get_all_elements(self):
        self.cursor.execute("SELECT * FROM elements")
        rows = self.cursor.fetchall()

        element_dict = {
            row[0]: {
                "symbol": row[0],
                "name": row[1],
                "group": row[2],
                "period": row[3],
            }
            for row in rows
        }

        return element_dict


    def link_element_to_group(self, element, group):
        date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute(
            "INSERT INTO elements_to_groups (symbol, group_id, date) VALUES (?, ?, ?)",
            (element["symbol"], group["id"], date)
        )
        self.connection.commit()


    def unlink_element_to_group(self, element, group):
        self.cursor.execute(
            "DELETE FROM elements_to_groups WHERE symbol = ? AND group_id = ?",
            (element["symbol"], group["id"])
        )
        self.connection.commit()


    def get_all_elements_by_group(self, group):
        if group:
            self.cursor.execute("SELECT elements.symbol, elements.name, elements.\"group\", elements.period FROM elements_to_groups LEFT OUTER JOIN elements ON elements_to_groups.symbol = elements.symbol WHERE elements_to_groups.group_id = ?", (group["id"],))
            rows = self.cursor.fetchall()

            category_dict = {
                row[0]: {
                    "symbol": row[0],
                    "name": row[1],
                    "group": row[2],
                    "period": row[3],
                }
                for row in rows
            }

            return category_dict
        else:
            return {}


    def get_category_by_id(self, category_id):
        self.cursor.execute("SELECT * FROM categories WHERE id = ?", (category_id,))
        row = self.cursor.fetchone()

        category_dict = {
            "id": row[0],
            "name": row[1],
            "date": row[2],
        }
        return category_dict


    def get_all_categories_by_group(self, group):
        if group:
            self.cursor.execute("SELECT id, name, date FROM categories WHERE group_id = ?", (group["id"],))
            rows = self.cursor.fetchall()

            category_dict = {
                row[0]: {
                    "id": row[0],
                    "name": row[1],
                    "date": row[2],
                }
                for row in rows
            }

            return category_dict
        else:
            return {}


    def delete_category(self, category):
        self.cursor.execute("DELETE FROM categories WHERE id = ?", (category["id"],))
        self.connection.commit()


    def get_all_compounds_by_group(self, group):
        if group:
            self.cursor.execute("SELECT id, correct_name, wrong_name1, wrong_name2, correct_formula, wrong_formula1, wrong_formula2, category_id, group_id, date FROM compounds WHERE group_id = ?", (group["id"],))
            rows = self.cursor.fetchall()

            compound_dict = {
                row[0]: {
                    "id": row[0],
                    "correct_name": row[1],
                    "wrong_name1": row[2],
                    "wrong_name2": row[3],
                    "correct_formula": row[4],
                    "wrong_formula1": row[5],
                    "wrong_formula2": row[6],
                    "category": row[7],
                    "group_id": row[8],
                    "date": row[9],
                }
                for row in rows
            }

            return compound_dict
        else:
            return {}


    def delete_compound(self, compound):
        self.cursor.execute("DELETE FROM compounds WHERE id = ?", (compound["id"],))
        self.connection.commit()


    def get_all_questions_by_group(self, group):
        if group:
            self.cursor.execute("SELECT id, question, correct_answer, wrong_answer1, wrong_answer2, wrong_answer3, wrong_answer4, group_id, date FROM questions WHERE group_id = ?", (group["id"],))
            rows = self.cursor.fetchall()

            question_dict = {
                row[0]: {
                    "id": row[0],
                    "question": row[1],
                    "correct_answer": row[2],
                    "wrong_answer1": row[3],
                    "wrong_answer2": row[4],
                    "wrong_answer3": row[5],
                    "wrong_answer4": row[6],
                    "group_id": row[7],
                    "date": row[8],
                }
                for row in rows
            }

            return question_dict
        else:
            return {}


    def delete_question(self, question):
        self.cursor.execute("DELETE FROM questions WHERE id = ?", (question["id"],))
        self.connection.commit()


    def get_all_groups_by_owner_id(self, owner_id):
        self.cursor.execute("SELECT id, name, owner_id, date FROM groups WHERE owner_id = ?", (owner_id,))
        rows = self.cursor.fetchall()
        group_list = []

        for row in rows:
            group_list.append({
                "id": row[0],
                "name": row[1],
                "owner_id": row[2],
                "date": row[3],
            })

        return group_list


    def delete_group(self, group):
        self.cursor.execute("DELETE FROM elements_to_groups WHERE group_id = ?", (group["id"],))
        self.cursor.execute("DELETE FROM categories WHERE group_id = ?", (group["id"],))
        self.cursor.execute("DELETE FROM compounds WHERE group_id = ?", (group["id"],))
        self.cursor.execute("DELETE FROM questions WHERE group_id = ?", (group["id"],))
        self.cursor.execute("DELETE FROM groups WHERE id = ?", (group["id"],))
        self.connection.commit()


    def close(self):
        self.connection.close()