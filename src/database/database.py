from supabase import create_client, Client


class Database:
    def __init__(self, url, key):
        self.supabase: Client = create_client(url, key)


    def create_account(self, email, password):
        self.supabase.table("accounts").insert({
            "email": email,
            "password": password,
        }).execute()


    def get_account_by_email(self, email):
        response = self.supabase.table("accounts").select("*").eq("email", email).limit(1).execute()
        if response.data:
            row = response.data[0]
            return {
                "id": row["id"],
                "email": row["email"],
                "password": row["password"],
                "date": row["date"],
            }
        return None


    def create_group(self, name, owner_id):
        self.supabase.table("groups").insert({
            "name": name,
            "owner_id": owner_id,
        }).execute()


    def update_group(self, id, name, owner_id):
        group = {
            "id": id,
            "name": name,
            "owner_id": owner_id,
        }
        response = self.supabase.table("groups").update(group).eq("id", group["id"]).execute()
        return bool(response.data)


    def group_exists_by_id(self, group_id):
        response = self.supabase.table("groups").select("id").eq("id", group_id).limit(1).execute()
        return len(response.data or []) > 0


    def get_group_by_name(self, name):
        response = self.supabase.table("groups").select("*").eq("name", name).limit(1).execute()
        if response.data:
            row = response.data[0]
            return {
                "id": row["id"],
                "name": row["name"],
                "owner_id": row["owner_id"],
                "date": row["date"],
            }
        return None


    def get_all_groups_by_owner_id(self, owner_id):
        response = self.supabase.table("groups").select("*").eq("owner_id", owner_id).execute()

        return [
            {
                "id": row["id"],
                "name": row["name"],
                "owner_id": row["owner_id"],
                "date": row["date"],
            }
            for row in response.data or []
        ]


    def delete_group(self, group):
        gid = group["id"]
        self.supabase.table("elements_to_groups").delete().eq("group_id", gid).execute()
        self.supabase.table("categories").delete().eq("group_id", gid).execute()
        self.supabase.table("compounds").delete().eq("group_id", gid).execute()
        self.supabase.table("questions").delete().eq("group_id", gid).execute()
        self.supabase.table("groups").delete().eq("id", gid).execute()


    def get_all_elements(self):
        response = self.supabase.table("elements").select("*").execute()
        rows = response.data or []

        return {
            row["symbol"]: {
                "symbol": row["symbol"],
                "name": row["name"],
                "system_group": row["system_group"],
                "system_period": row["system_period"],
            }
            for row in rows
        }


    def link_element_to_group(self, element, group):
        self.supabase.table("elements_to_groups").insert({
            "symbol": element["symbol"],
            "group_id": group["id"],
        }).execute()


    def unlink_element_to_group(self, element, group):
        self.supabase.table("elements_to_groups") \
            .delete() \
            .eq("symbol", element["symbol"]) \
            .eq("group_id", group["id"]) \
            .execute()


    def get_all_elements_by_group(self, group):
        if not group:
            return []

        response = self.supabase \
            .table("elements_to_groups") \
            .select("symbol, date, elements(symbol, name, system_group, system_period)") \
            .eq("group_id", group["id"]) \
            .execute()

        rows = response.data or []

        return [
            {
                "symbol": row["symbol"],
                "name": row["elements"]["name"],
                "system_group": row["elements"]["system_group"],
                "system_period": row["elements"]["system_period"],
            }
            for row in rows if row.get("elements")
        ]


    def create_category(self, name, category_type, group):
        self.supabase.table("categories").insert({
            "name": name,
            "type": category_type.value,
            "group_id": group["id"],
        }).execute()


    def update_category(self, id, name, category_type, group):
        category = {
            "id": id,
            "name": name,
            "type": category_type.value,
            "group_id": group["id"],
        }
        response = self.supabase.table("categories").update(category).eq("id", category["id"]).execute()
        return bool(response.data)


    def get_category_by_id(self, category_id):
        response = self.supabase.table("categories").select("*").eq("id", category_id).limit(1).execute()
        if response.data:
            row = response.data[0]
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

        response = self.supabase.table("categories").select("*") \
            .eq("type", type.value).eq("group_id", group["id"]).execute()

        return [
            {
                "id": row["id"],
                "name": row["name"],
                "type": row["type"],
                "group_id": row["group_id"],
                "date": row["date"],
            }
            for row in response.data or []
        ]


    def delete_category(self, category):
        self.supabase.table("categories").delete().eq("id", category["id"]).execute()


    def create_compound(self, correct_name, wrong_name1, wrong_name2, wrong_name3, wrong_name4, correct_formula, wrong_formula1, wrong_formula2, wrong_formula3, wrong_formula4, difficulty, category, group):
        self.supabase.table("compounds").insert({
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
        }).execute()


    def update_compound(self, id, correct_name, wrong_name1, wrong_name2, wrong_name3, wrong_name4, correct_formula, wrong_formula1, wrong_formula2, wrong_formula3, wrong_formula4, difficulty, category, group):
        compound = {
            "id": id,
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
        response = self.supabase.table("compounds").update(compound).eq("id", compound["id"]).execute()
        return bool(response.data)


    def get_all_compounds_by_group(self, group):
        if not group:
            return {}

        response = self.supabase.table("compounds").select("*").eq("group_id", group["id"]).execute()

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
            for row in response.data or []
        ]


    def delete_compound(self, compound):
        self.supabase.table("compounds").delete().eq("id", compound["id"]).execute()


    def create_question(self, question, correct_answer, wrong_answer1, wrong_answer2, wrong_answer3, wrong_answer4, difficulty, category, group):
        self.supabase.table("questions").insert({
            "question": question,
            "correct_answer": correct_answer,
            "wrong_answer1": wrong_answer1,
            "wrong_answer2": wrong_answer2,
            "wrong_answer3": wrong_answer3,
            "wrong_answer4": wrong_answer4,
            "difficulty": difficulty.value,
            "category_id": category["id"],
            "group_id": group["id"],
        }).execute()


    def update_question(self, id, question, correct_answer, wrong_answer1, wrong_answer2, wrong_answer3, wrong_answer4, difficulty, category, group):
        question = {
            "id": id,
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
        response = self.supabase.table("questions").update(question).eq("id", question["id"]).execute()
        return bool(response.data)


    def get_all_questions_by_group(self, group):
        if not group:
            return {}

        response = self.supabase.table("questions").select("*").eq("group_id", group["id"]).execute()

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
            for row in response.data or []
        ]


    def delete_question(self, question):
        self.supabase.table("questions").delete().eq("id", question["id"]).execute()
