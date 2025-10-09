import httpx

class Database:
    def __init__(self, url, key):
        self.url = url
        self.headers = {
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }
        self.client = httpx.Client(base_url=url+"/rest/v1", headers=self.headers)


    def create_account(self, email, password):
        data = {
            "email": email,
            "password": password,
        }
        response = self.client.post("/accounts", json=data)
        return response.json()[0]


    def get_account_by_email(self, email):
        response = self.client.get("/accounts", params={"email": f"eq.{email}", "limit": 1})
        data = response.json()
        if data:
            row = data[0]
            return {
                "id": row["id"],
                "email": row["email"],
                "password": row["password"],
                "date": row["date"],
            }
        return None


    def create_group(self, name, owner_id):
        data = {
            "name": name,
            "owner_id": owner_id,
        }
        response = self.client.post("/groups", json=data)
        return response.json()[0]


    def update_group(self, id, name, owner_id):
        data = {
            "name": name,
            "owner_id": owner_id,
        }
        response = self.client.patch(f"/groups?id=eq.{id}", json=data)
        return response.json()[0]


    def group_exists_by_id(self, group_id):
        response = self.client.get("/groups", params={"id": f"eq.{group_id}", "select": "id", "limit": 1})
        return bool(response.json())


    def get_group_by_name(self, name):
        response = self.client.get("/groups", params={"name": f"eq.{name}", "limit": 1})
        data = response.json()
        if data:
            row = data[0]
            return {
                "id": row["id"],
                "name": row["name"],
                "owner_id": row["owner_id"],
                "date": row["date"],
            }
        return None


    def get_all_groups_by_owner_id(self, owner_id):
        response = self.client.get("/groups", params={"owner_id": f"eq.{owner_id}"})
        data = response.json()
        return [
            {
                "id": row["id"],
                "name": row["name"],
                "owner_id": row["owner_id"],
                "date": row["date"],
            }
            for row in data or []
        ]


    def delete_group(self, group):
        group_id = group["id"]
        tables_to_delete = ["elements_to_groups", "categories", "compounds", "questions"]
        for table in tables_to_delete:
            self.client.delete(f"/{table}", params={f"group_id": f"eq.{group_id}"})
        self.client.delete(f"/groups", params={"id": f"eq.{group_id}"})


    def get_all_elements(self):
        response = self.client.get("/elements")
        data = response.json()
        return {
            row["symbol"]: {
                "symbol": row["symbol"],
                "name": row["name"],
                "system_group": row["system_group"],
                "system_period": row["system_period"],
            }
            for row in data
        }


    def link_element_to_group(self, element, group):
        data = {
            "symbol": element["symbol"],
            "group_id": group["id"],
        }
        self.client.post("/elements_to_groups", json=data)


    def unlink_element_to_group(self, element, group):
        symbol = element["symbol"]
        group_id = group["id"]
        self.client.delete("/elements_to_groups", params={"symbol": f"eq.{symbol}", "group_id": f"eq.{group_id}"})


    def get_all_elements_by_group(self, group):
        if not group:
            return []

        group_id = group["id"]
        response = self.client.get("/elements_to_groups", params={"group_id": f"eq.{group_id}", "select": "symbol, elements(*)"})
        data = response.json()
        return [
            {
                "symbol": row["symbol"],
                "name": row["elements"]["name"],
                "system_group": row["elements"]["system_group"],
                "system_period": row["elements"]["system_period"],
            }
            for row in data if row.get("elements")
        ]


    def create_category(self, name, category_type, group):
        data = {
            "name": name,
            "category_type": category_type,
            "group_id": group["id"],
        }
        response = self.client.post("/categories", json=data)
        return response.json()[0]


    def update_category(self, id, name, category_type, group):
        data = {
            "name": name,
            "type": category_type,
            "group_id": group["id"],
        }
        response = self.client.patch(f"/categories?id=eq.{id}", json=data)
        return response.json()[0]


    def get_category_by_id(self, category_id):
        response = self.client.get("/categories", params={"id": f"eq.{category_id}", "limit": 1})
        data = response.json()
        if data:
            row = data[0]
            return {
                "id": row["id"],
                "name": row["name"],
                "type": row["type"],
                "group_id": row["group_id"],
                "date": row["date"],
            }
        return None


    def get_all_categories_by_type_and_group(self, type, group):
        if not group:
            return {}

        group_id = group["id"]
        response = self.client.get("/categories", params={"group_id": f"eq.{group_id}"})
        data = response.json()
        return [
            {
                "id": row["id"],
                "name": row["name"],
                "type": row["type"],
                "group_id": row["group_id"],
                "date": row["date"],
            }
            for row in data
        ]


    def delete_category(self, category):
        category_id = category["id"]
        self.client.delete("/categories", params={"id": f"eq.{category_id}"})


    def create_compound(self, correct_name, wrong_name1, wrong_name2, wrong_name3, wrong_name4, correct_formula, wrong_formula1, wrong_formula2, wrong_formula3, wrong_formula4, difficulty, category, group):
        data = {
            "correct_name": correct_name,
            "wrong_name1": wrong_name1,
            "wrong_name2": wrong_name2,
            "wrong_name3": wrong_name3,
            "wrong_name4": wrong_name4,
            "correct_formula": correct_formula,
            "wrong_formula1": wrong_formula1,
            "wrong_formula2": wrong_formula2,
            "wrong_formula3": wrong_formula3,
            "wrong_formula4": wrong_formula4,
            "difficulty": difficulty.value,
            "category_id": category["id"],
            "group_id": group["id"],
        }
        response = self.client.post("/compounds", json=data)
        return response.json()[0]


    def update_compound(self, id, correct_name, wrong_name1, wrong_name2, wrong_name3, wrong_name4, correct_formula, wrong_formula1, wrong_formula2, wrong_formula3, wrong_formula4, difficulty, category, group):
        data = {
            "correct_name": correct_name,
            "wrong_name1": wrong_name1,
            "wrong_name2": wrong_name2,
            "wrong_name3": wrong_name3,
            "wrong_name4": wrong_name4,
            "correct_formula": correct_formula,
            "wrong_formula1": wrong_formula1,
            "wrong_formula2": wrong_formula2,
            "wrong_formula3": wrong_formula3,
            "wrong_formula4": wrong_formula4,
            "difficulty": difficulty.value,
            "category_id": category["id"],
            "group_id": group["id"],
        }
        response = self.client.patch(f"/compounds?id=eq.{id}", json=data)
        return response.json()[0]


    def get_all_compounds_by_group(self, group):
        if not group:
            return {}

        group_id = group["id"]
        response = self.client.get("/compounds", params={"group_id": f"eq.{group_id}"})
        data = response.json()
        return [
            {
                "id": row["id"],
                "correct_name": row["correct_name"],
                "wrong_name1": row["wrong_name1"],
                "wrong_name2": row["wrong_name2"],
                "wrong_name3": row["wrong_name3"],
                "wrong_name4": row["wrong_name4"],
                "correct_formula": row["correct_formula"],
                "wrong_formula1": row["wrong_formula1"],
                "wrong_formula2": row["wrong_formula2"],
                "wrong_formula3": row["wrong_formula3"],
                "wrong_formula4": row["wrong_formula4"],
                "difficulty": row["difficulty"],
                "category_id": row["category_id"],
                "group_id": row["group_id"],
                "date": row["date"],
            }
            for row in data
        ]


    def delete_compound(self, compound):
        compound_id = compound["id"]
        self.client.delete("/compounds", params={"id": f"eq.{compound_id}"})


    def create_question(self, question, correct_answer, wrong_answer1, wrong_answer2, wrong_answer3, wrong_answer4, difficulty, category, group):
        data = {
            "question": question,
            "correct_answer": correct_answer,
            "wrong_answer1": wrong_answer1,
            "wrong_answer2": wrong_answer2,
            "wrong_answer3": wrong_answer3,
            "wrong_answer4": wrong_answer4,
            "difficulty": difficulty.value,
            "category_id": category["id"],
            "group_id": group["id"],
        }
        response = self.client.post("/questions", json=data)
        return response.json()[0]


    def update_question(self, id, question, correct_answer, wrong_answer1, wrong_answer2, wrong_answer3, wrong_answer4, difficulty, category, group):
        data = {
            "question": question,
            "correct_answer": correct_answer,
            "wrong_answer1": wrong_answer1,
            "wrong_answer2": wrong_answer2,
            "wrong_answer3": wrong_answer3,
            "wrong_answer4": wrong_answer4,
            "difficulty": difficulty.value,
            "category_id": category["id"],
            "group_id": group["id"],
        }
        response = self.client.patch(f"/questions?id=eq.{id}", json=data)
        return response.json()[0]


    def get_all_questions_by_group(self, group):
        if not group:
            return {}

        group_id = group["id"]
        response = self.client.get("/questions", params={"group_id": f"eq.{group_id}"})
        data = response.json()
        return [
            {
                "id": row["id"],
                "question": row["question"],
                "correct_answer": row["correct_answer"],
                "wrong_answer1": row["wrong_answer1"],
                "wrong_answer2": row["wrong_answer2"],
                "wrong_answer3": row["wrong_answer3"],
                "wrong_answer4": row["wrong_answer4"],
                "difficulty": row["difficulty"],
                "category_id": row["category_id"],
                "group_id": row["group_id"],
                "date": row["date"],
            }
            for row in data
        ]


    def delete_question(self, question):
        question_id = question["id"]
        self.client.delete("/questions", params={"id": f"eq.{question_id}"})
